---
layout: default
title: "Thread"
parent: "Operating Systems"
nav_order: 92
permalink: /operating-systems/thread/
number: "0092"
category: Operating Systems
difficulty: ★☆☆
depends_on: Process, CPU, Stack
used_by: Context Switch, Java Concurrency, Thread Pool, Deadlock
related: Fiber / Coroutine, Process vs Thread, Green Thread
tags:
  - os
  - concurrency
  - internals
  - foundational
---

# 092 — Thread

⚡ TL;DR — A thread is a lightweight unit of execution within a process, sharing its memory but with its own stack and program counter.

| #092 | Category: Operating Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Process, CPU, Stack | |
| **Used by:** | Context Switch, Java Concurrency, Thread Pool, Deadlock | |
| **Related:** | Fiber / Coroutine, Process vs Thread, Green Thread | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
In the early Unix process model, every unit of concurrent work required
a separate process. A web server serving 100 simultaneous clients needed
100 full processes — each with its own address space, PCB, and copy of
the program code. Passing data between these processes required pipes,
sockets, or shared memory with explicit synchronization. Spawning a new
process cost hundreds of microseconds and megabytes of memory.

When a single program needed to do two things in parallel — like handle
a network connection while computing a result — the only option was to
fork() and then use IPC to communicate results. This was slow, complex,
and memory-intensive. For a database server handling thousands of
simultaneous queries, one process per query was simply untenable.

THE BREAKING POINT:
Programs that need parallelism within a single address space — sharing
data structures, caches, and file handles — pay an enormous overhead
penalty if forced to use separate processes with IPC.

THE INVENTION MOMENT:
This is exactly why the **Thread** was created — a second execution
pointer running inside the same process, sharing its memory, so parallel
work can happen cheaply without IPC.

### 📘 Textbook Definition

A **thread** (or thread of execution) is the smallest schedulable unit
of work within a process. All threads in a process share the process's
virtual address space, heap, static data, and file descriptors. Each
thread has its own: program counter, register set, stack pointer, and
stack (for local variables and call frames). The OS schedules threads
independently — multiple threads from the same process can run
simultaneously on different CPU cores. Thread creation, context switch,
and communication are significantly cheaper than the process equivalents.

### ⏱️ Understand It in 30 Seconds

**One line:**
A thread is a second worker inside the same office, sharing all the desks.

**One analogy:**

> A process is a restaurant kitchen. A thread is a cook. The kitchen has
> one set of pots, pans, and ingredients (shared memory). Each cook has
> their own hands and their own recipe card they're currently following
> (private stack and program counter). Two cooks can work simultaneously,
> but they must not both grab the same pan at the same time.

**One insight:**
Threads make sharing data cheap (it's already in the same memory), but
they make coordination hard (any thread can corrupt shared data at any
time). This tradeoff — easy sharing, hard safety — is the root cause of
most concurrency bugs.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. **Shared address space**: all threads in a process see the same virtual
   memory. A write by Thread A is immediately visible to Thread B.
2. **Private execution state**: each thread has its own stack, program
   counter, and register set — what it's doing right now.
3. **Independent scheduling**: the OS can schedule Thread A on Core 1 and
   Thread B on Core 2 simultaneously, or preempt either independently.

DERIVED DESIGN:
Since threads share memory, thread creation only requires allocating a
new stack and thread control block — not copying the entire address space.
The OS thread scheduler treats each thread as a schedulable entity,
placing them in ready/blocked queues independently of other threads in
the same process.

THE TRADE-OFFS:
Gain: cheap creation (~1 µs vs ~100 µs for fork), zero-copy data sharing,
exploits multiple CPU cores within one program.
Cost: shared memory means any thread can corrupt shared state; requires
explicit synchronization (mutexes, locks) to be correct; one crashed
thread (unhandled exception, stack overflow) can kill the entire
process.

### 🧪 Thought Experiment

SETUP:
A web server receives two simultaneous HTTP requests. Both need to
increment a shared `requestCount` variable.

WHAT HAPPENS WITHOUT THREAD (one process per request):
Both processes have their own `requestCount`. After both handle one
request, Process A has requestCount=1, Process B has requestCount=1.
Neither reflects the true total. To share state, they must use IPC —
a pipe or socket — adding ~10 µs per update and complex code.

WHAT HAPPENS WITH THREAD:
Thread A reads requestCount=0, Thread B reads requestCount=0 simultaneously.
Thread A writes 1. Thread B writes 1. Final value: 1 — not 2.
This is a race condition. The data is shared, but without a mutex,
the increment is not atomic. With a mutex: Thread A locks, increments
to 1, unlocks. Thread B locks, increments to 2, unlocks. Correct.

THE INSIGHT:
Threads make sharing trivially easy and safety non-trivially hard.
The mutex is the price of sharing without IPC overhead.

### 🧠 Mental Model / Analogy

> Think of a process as a single-screen cinema. Threads are the
> projectors. A multi-threaded cinema has two projectors showing
> films on the same screen simultaneously — they share the screen
> (memory) but each runs its own film reel (stack/PC).

**Analogy mapping:**

- "Screen (shared)" → process virtual address space / heap
- "Projector 1's film reel" → Thread 1's stack and program counter
- "Projector 2's film reel" → Thread 2's stack and program counter
- "Projectionist coordinating" → mutex / synchronized block
- "Film reel collision" → race condition / data corruption

Where this analogy breaks down: in a cinema two projectors would show
overlapping images (visible corruption); in code the corruption is silent
and intermittent — much harder to detect.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A thread is a second execution path inside the same program. You can
have Thread A download a file while Thread B updates the UI — both
happening in the same application at the same time.

**Level 2 — How to use it (junior developer):**
In Java: `new Thread(() -> doWork()).start()`. In Python: `threading.Thread`.
Each thread needs its own stack (typically 512 KB–8 MB). Be careful with
shared variables — read-modify-write sequences need synchronization.
In Java, `synchronized` blocks or `java.util.concurrent` classes handle this.

**Level 3 — How it works (mid-level engineer):**
The OS maintains a Thread Control Block (TCB) per thread: saved registers,
stack pointer, thread state, scheduling priority. On Linux, threads are
implemented as "light-weight processes" via `clone()` with `CLONE_VM` flag
— they share the same mm_struct (virtual memory descriptor). The JVM maps
Java threads 1:1 to OS threads (since Java 1.2); Java 21 Virtual Threads
are multiplexed onto OS threads by the JVM scheduler.

**Level 4 — Why it was designed this way (senior/staff):**
The 1:1 thread-to-OS-thread model makes the OS responsible for scheduling,
enabling true parallelism on multi-core CPUs. The alternative — N:M green
threads (many user threads on few OS threads) — was used in early Java but
abandoned because it couldn't exploit multiple cores and kernel blocking
calls blocked all user threads. Java 21 Project Loom revisits this with
virtual threads, but using structured concurrency and cooperative
preemption at blocking points only.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│        THREAD MEMORY LAYOUT (per process)        │
├──────────────────────────────────────────────────┤
│  Process Virtual Address Space                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Shared: Heap, BSS, Data, Text (code)        │ │
│  ├──────────────────┬──────────────────────────┤ │
│  │ Thread 1 Stack   │ Thread 2 Stack           │ │
│  │ (private)        │ (private)                │ │
│  └──────────────────┴──────────────────────────┘ │
├──────────────────────────────────────────────────┤
│  Kernel maintains per-thread:                    │
│  • Program Counter (where executing)             │
│  • Register set (CPU state when not running)     │
│  • Thread ID (TID)                               │
│  • Scheduling state (ready/running/blocked)      │
│  • Stack pointer                                 │
└──────────────────────────────────────────────────┘
```

**Thread creation in Linux:**

```
pthread_create()  →  clone(CLONE_VM | CLONE_FILES ...)
                  →  new task_struct with shared mm_struct
                  →  allocated stack (mmap or pthread_attr)
                  →  placed in scheduler READY queue
```

**Execution on multi-core:**

```
Core 0                    Core 1
──────                    ──────
Thread A runs             Thread B runs
reads counter=0           reads counter=0   ← RACE
writes counter=1          writes counter=1  ← LOST UPDATE
```

**With mutex:**

```
Thread A                  Thread B
lock(mutex)               try lock(mutex) → BLOCKED
reads counter=0           (waiting)
writes counter=1
unlock(mutex)             lock(mutex) acquired
                          reads counter=1
                          writes counter=2
                          unlock(mutex)
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
main() starts
  → JVM/OS creates initial thread (main thread)
  → new Thread(task).start() called
  → OS clone() syscall → new TCB allocated
  → [NEW THREAD ← YOU ARE HERE] enters READY queue
  → Scheduler picks thread → runs on CPU core
  → Thread completes → OS frees TCB + stack
  → main thread calls join() → collects result
```

FAILURE PATH:

```
Thread throws uncaught exception
  → JVM calls Thread.UncaughtExceptionHandler
  → Default: print stack trace to stderr
  → Thread terminates
  → Other threads in process continue running
  → If it was the last non-daemon thread: JVM exits
```

WHAT CHANGES AT SCALE:
At 10,000 threads, each consuming 1–8 MB of stack, you exhaust virtual
address space before physical RAM. The OS scheduler overhead for 10,000
ready threads becomes measurable. This is why thread pools cap at
100–500 threads per JVM instance, and why virtual threads (Java 21)
use 1 KB carrier stacks with grow-on-demand heap stacks.

### 💻 Code Example

Example 1 — Basic thread creation and race condition:

```java
// BAD: unsynchronized shared counter
public class RaceDemo {
    static int counter = 0;

    public static void main(String[] args)
        throws InterruptedException {
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) counter++;
        });
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) counter++;
        });
        t1.start(); t2.start();
        t1.join(); t2.join();
        // Final value: NOT reliably 20000 — race condition
        System.out.println(counter);
    }
}

// GOOD: use AtomicInteger for lock-free thread safety
import java.util.concurrent.atomic.AtomicInteger;
public class SafeDemo {
    static AtomicInteger counter = new AtomicInteger(0);

    public static void main(String[] args)
        throws InterruptedException {
        Thread t1 = new Thread(
            () -> { for (int i=0;i<10000;i++) counter.incrementAndGet(); }
        );
        Thread t2 = new Thread(
            () -> { for (int i=0;i<10000;i++) counter.incrementAndGet(); }
        );
        t1.start(); t2.start();
        t1.join(); t2.join();
        System.out.println(counter.get()); // Always 20000
    }
}
```

Example 2 — Production pattern: thread pool over raw threads:

```java
// BAD: creating new threads per task
void handleRequest(Request req) {
    new Thread(() -> process(req)).start(); // unbounded!
}

// GOOD: bounded thread pool limits resource consumption
import java.util.concurrent.*;
ExecutorService pool = Executors.newFixedThreadPool(50);

void handleRequest(Request req) {
    pool.submit(() -> process(req));
    // Pool reuses threads; bounded at 50 concurrent
}
```

### ⚖️ Comparison Table

| Concurrency Unit | Memory Share | Creation Cost | OS Visible | Best For             |
| ---------------- | ------------ | ------------- | ---------- | -------------------- |
| Process          | None         | High (~100µs) | Yes        | Strong isolation     |
| **Thread**       | Yes          | Medium (~1µs) | Yes        | Shared-state tasks   |
| Virtual Thread   | Yes          | Very low      | No (JVM)   | High-concurrency IO  |
| Fiber/Coroutine  | Yes          | Near zero     | No         | Cooperative async IO |

How to choose: use threads when you need true parallelism on multi-core
hardware with shared mutable state; use virtual threads (Java 21+) or
async/await when concurrency is IO-bound with thousands of concurrent tasks.

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| "More threads = faster program"                         | More threads than CPU cores causes context switch overhead; CPU-bound code slows with excess threads                                   |
| "Threads are safe if variables are not shared"          | Local variables on the stack are safe; any static or heap object accessible to multiple threads is shared                              |
| "synchronized makes code thread-safe"                   | synchronized prevents concurrent access to one block, but compound operations across multiple synchronized blocks are still not atomic |
| "Thread.sleep() releases locks"                         | sleep() does NOT release held monitors; only wait() (on a monitor) releases the lock                                                   |
| "Daemon threads are garbage-collected after main exits" | Daemon threads are forcibly terminated when all non-daemon threads finish — they don't run to completion                               |

### 🚨 Failure Modes & Diagnosis

**1. Deadlock**

Symptom:
Application hangs. Thread dump shows two threads each waiting for the
other's lock: "waiting to lock <0x...> (held by Thread-B)".

Root Cause:
Thread A holds Lock 1 and waits for Lock 2. Thread B holds Lock 2 and
waits for Lock 1. Circular dependency — neither can proceed.

Diagnostic:

```bash
# Java: get thread dump
kill -3 <java_pid>      # prints to stdout
jstack <java_pid>       # dedicated tool
# Look for "deadlock" or "waiting to lock"
```

Fix: always acquire locks in the same global order across all threads.
Prevention: use `tryLock(timeout)` instead of blocking `lock()`; use
higher-level concurrent collections instead of manual locking.

**2. Thread Leak**

Symptom:
Thread count in JVM grows without bound over hours. Eventually: OOM
or "unable to create new native thread".

Root Cause:
Threads created but never terminated — blocked waiting for input that
never comes, or blocked forever on a broken connection.

Diagnostic:

```bash
# JVM thread count
jstack <pid> | grep -c "java.lang.Thread.State"
# Or via JMX:
# ManagementFactory.getThreadMXBean().getThreadCount()
```

Fix: always use thread pools with bounded queues; set socket timeouts
so threads don't block forever on IO.

Prevention: monitor thread count as a production metric; alert on
sustained thread count growth.

**3. Race Condition / Data Corruption**

Symptom:
Intermittent wrong results, NullPointerExceptions in code that looks
correct, or data structure corruption (e.g., HashMap infinite loop in
Java 7 under concurrent access).

Root Cause:
Multiple threads read-modify-write shared mutable state without
synchronization. The JVM memory model allows threads to cache values in
CPU registers — a write on Core 0 may not be visible on Core 1 without
a memory barrier.

Diagnostic:

```bash
# Java: use thread sanitizer or data race detectors
# Run tests with: -XX:+EnableThreadLocalAllocationBuffers
# Production: look for heap corruption in GC logs
# Tool: Google ThreadSanitizer (C/C++), Helgrind (Valgrind)
```

Fix: use `synchronized`, `volatile`, or `java.util.concurrent` classes
for all shared mutable state access.

Prevention: prefer immutable objects; use `ConcurrentHashMap`,
`AtomicInteger`, `CopyOnWriteArrayList`; minimize shared mutable state.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process` — a thread lives inside a process; understand the container first
- `CPU` — threads compete for CPU time on cores
- `Stack` — each thread has its own call stack for local variables

**Builds On This (learn these next):**

- `Context Switch` — how the OS switches the CPU between threads
- `Mutex` — the fundamental tool for thread-safe access to shared data
- `Deadlock` — what goes wrong when two threads wait for each other's locks
- `Thread Pool` — the production pattern for managing threads at scale

**Alternatives / Comparisons:**

- `Fiber / Coroutine` — user-space cooperative concurrency; no OS involvement
- `Process` — stronger isolation; no shared memory; higher overhead
- `Virtual Thread` — JVM-managed lightweight threads (Java 21+)

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ Lightweight execution unit inside a process│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ Parallelism within one program was too │
│ SOLVES │ expensive with separate processes │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ Sharing memory makes data exchange free │
│ │ but makes correctness hard │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ CPU-bound parallel work or shared-state │
│ │ concurrent operations within one process │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ You need 10,000+ concurrent IO tasks — │
│ │ use virtual threads or async instead │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ Easy sharing vs hard correctness │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "Second worker, same kitchen — watch out │
│ │ for the same knife" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Mutex → Deadlock → Thread Pool │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `HashMap` is documented as "not thread-safe." Under Java 7,
concurrent puts from two threads can cause an infinite loop in `get()`.
Trace the exact mechanism: which data structure operation causes the cycle,
what CPU instruction interleaving enables it, and why does Java 8's
`HashMap` avoid the infinite loop but still corrupt data under concurrent
access?

**Q2.** The JVM uses 1:1 thread mapping to OS threads. Node.js uses a
single-threaded event loop. Both handle tens of thousands of simultaneous
HTTP connections in production. What is the precise workload characteristic
that makes Node.js's model superior for typical web APIs, and what workload
would make the JVM multi-thread model definitively win?
