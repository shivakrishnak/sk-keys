---
layout: default
title: "Thread (OS)"
parent: "Operating Systems"
nav_order: 92
permalink: /operating-systems/thread-os/
number: "092"
category: Operating Systems
difficulty: ★☆☆
depends_on: Process, CPU Scheduling
used_by: Process vs Thread, Context Switch, Thread (Java), Fiber / Coroutine, Concurrency vs Parallelism
tags:
  - os
  - foundational
  - process
  - concurrency
---

# 092 — Thread (OS)

`#os` `#foundational` `#process` `#concurrency`

⚡ TL;DR — A lightweight execution unit within a process that shares the process's memory and resources but has its own CPU registers, program counter, and call stack.

| #092 | Category: Operating Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Process, CPU Scheduling | |
| **Used by:** | Process vs Thread, Context Switch, Thread (Java), Fiber / Coroutine, Concurrency vs Parallelism | |

---

### 📘 Textbook Definition

An OS **thread** (kernel thread) is a schedulable unit of execution within a process. All threads in a process share the same virtual address space, code segment, data segment, heap, and file descriptor table. Each thread maintains its own: **program counter** (PC), **CPU register set**, and **call stack** (a dedicated region of the process's address space). The OS kernel is aware of threads, schedules them independently on available CPU cores, and can preempt them. Thread creation, scheduling, and context switching are lighter-weight than process operations — no new address space needed — but shared memory introduces data races requiring synchronisation.

### 🟢 Simple Definition (Easy)

A thread is a mini-process inside a process — it runs its own sequence of instructions but shares all the memory and files of the process it lives in.

### 🔵 Simple Definition (Elaborated)

A process has all its resources (memory, files, network connections). Threads live inside a process and share all those resources, but each has its own "execution context" — which instruction it's currently executing, what's on its call stack, and the values of its CPU registers. Multiple threads in one process = true parallel execution on multi-core CPUs. They can communicate by reading/writing shared memory — blazing fast compared to inter-process communication. The trade-off: without careful synchronisation, threads reading and writing shared data simultaneously cause bugs called data races.

### 🔩 First Principles Explanation

**Why threads vs. processes?**

Creating a new process is expensive: allocate new virtual address space, copy page tables, set up file descriptor table, kernel bookkeeping. A new thread in an existing process requires only: allocate a new stack (typically 512KB–8MB), save new PC and registers in the kernel's thread descriptor. A thread context switch only saves/restores registers — no address space switch, no TLB flush. This makes threads ~5-10× cheaper to create and switch between than processes.

**Thread anatomy:**

```
Process Address Space:
┌────────────────────────────────────────┐
│                   Stack for Thread 1   │ ← SP1 (each thread's stack)
│                                        │
│                   Stack for Thread 2   │ ← SP2
│                                        │
│                   Stack for Thread 3   │ ← SP3
│                   ...                  │
│ Heap (shared by all threads)           │ ← objects, class data
│ BSS / Data (shared)                    │ ← static fields
│ Code (shared)                          │ ← bytecode / machine code
└────────────────────────────────────────┘

Each thread has its own:
- Program Counter (PC): where in code it's executing
- Register file: rsp, rbp, rax, rbx... (saved/restored on switch)
- Stack pointer: points to its dedicated stack region
```

**Thread types:**

1. **Kernel threads:** Created and managed by the OS. Scheduled by the kernel. Can run truly in parallel on different CPUs. Java's `Thread` maps 1:1 to kernel threads.

2. **User-space threads (green threads):** Managed by a user-space library, not the kernel. Old Java before 1.2, Go's goroutines (partially), Kotlin coroutines. Cannot use multiple CPUs simultaneously without M:N mapping.

3. **M:N hybrid (virtual threads):** Java 21 Virtual Threads — M user-space virtual threads mapped to N kernel carrier threads. Best of both: cheap creation + true parallelism.

**Thread lifecycle:**

```
New (allocated, not yet scheduled)
       ↓ start()
Runnable (ready; waiting for CPU)
       ↓ scheduled
Running (on CPU)
       ↓ I/O | sleep() | wait() | blocked on lock
Blocked/Waiting
       ↓ I/O done | notify() | lock available
Runnable (again)
       ↓ run() returns / exception
Terminated
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Threads (single-threaded process only):

- Web server handling one request at a time: while serving user A, user B waits completely.
- GUI freezes during computation: single-threaded UI blocks on any long operation.
- CPU cores idle while waiting for I/O: sequential program can't exploit multi-core parallelism.

What breaks without it:
1. 1-server-per-request model requires separate process per request — 10× more overhead.
2. No way to utilise multiple CPU cores within a single program's address space.

WITH Threads:
→ Web server handles thousands of simultaneous requests (1 thread per request model).
→ GUI remains responsive because UI runs on one thread, computation on another.
→ Parallel algorithms exploit multiple CPU cores within a single program.

### 🧠 Mental Model / Analogy

> A process is a restaurant kitchen. Threads are the chefs working in that kitchen. All chefs (threads) share the same kitchen space, equipment, and ingredients (shared memory, files, heap). Each chef is working on their own dish (separate call stack, PC, registers) — independently. If two chefs try to use the same cutting board simultaneously without coordination (shared data without synchronisation), they collide (race condition). The head chef (OS scheduler) decides when each chef gets to work at specific stations (CPU time).

"Kitchen" = process memory space, "chefs" = threads, "cutting board" = shared data, "OS scheduler" = head chef assigning stations.

### ⚙️ How It Works (Mechanism)

**Thread vs Process overhead comparison:**

```
                        Process     Thread (in same process)
Creation time          ~100-1000µs  ~10-100µs
Memory overhead        MB+          ~1MB (stack) + kernel TCB
Context switch time    ~1000ns      ~100ns (no address space switch)
Communication          IPC (slow)   Shared memory (fast)
Fault isolation        Strong       Weak (crash one = crash all)
```

**Stack sizes:**

```
Platform thread default stack sizes:
  Linux:   8 MB (ulimit -s)
  macOS:   8 MB
  Windows: 1 MB

Java virtual threads: ~few KB growing on-demand (on heap)
Java -Xss flag: can reduce platform thread stack size
  java -Xss512k -jar app.jar
  (reduces 8 MB → 512 KB for each thread; saves memory with many threads)
```

**Thread-local storage (TLS):**

```
Each thread has exclusive access to its thread-local storage:
Java: ThreadLocal<T> — per-thread value
OS:   __thread keyword (C) / pthread_getspecific()
Use case: Request context, DB connection per thread,
          SimpleDateFormat (not thread-safe, use ThreadLocal)
```

### 🔄 How It Connects (Mini-Map)

```
Process (address space, resources)
        ↓ contains
Thread (OS) ← you are here
  (kernel-scheduled execution unit; shared heap)
        ↓ Java implementation
Thread (Java) → Virtual Threads (Java 21)
        ↓ managed by
OS Scheduler (time-slicing, preemption)
        ↓ challenges
Race Condition | Deadlock | Thread Safety
        ↓ vs lighter alternative
Fiber / Coroutine (cooperative, user-space)
```

### 💻 Code Example

Example 1 — Creating and managing Java threads (OS threads):

```java
// Java Thread maps 1:1 to OS kernel thread
Thread t = Thread.ofPlatform()
    .name("worker-1")
    .stackSize(512 * 1024) // 512 KB stack
    .start(() -> {
        System.out.println("Running in: " +
            Thread.currentThread().getName());
        System.out.println("Thread ID: " +
            Thread.currentThread().threadId());
    });

t.join(); // wait for thread to finish

// Thread count: JVM threads (daemon + non-daemon)
ThreadMXBean tmx = ManagementFactory.getThreadMXBean();
System.out.println("Live threads: " + tmx.getThreadCount());
System.out.println("Peak threads: " + tmx.getPeakThreadCount());
```

Example 2 — Race condition with shared data (illustrating the problem):

```java
// BAD: Unsynchronised access to shared counter
int counter = 0; // shared between threads

Runnable increment = () -> {
    for (int i = 0; i < 100_000; i++) {
        counter++; // NOT atomic: read-modify-write is 3 ops!
    }
};

Thread t1 = new Thread(increment);
Thread t2 = new Thread(increment);
t1.start(); t2.start();
t1.join(); t2.join();

System.out.println(counter); // NOT 200,000! e.g., 147583
// Two threads read counter=X, both write X+1 → one increment lost

// GOOD: Use AtomicInteger
AtomicInteger safeCounter = new AtomicInteger(0);
Runnable safeIncrement = () -> {
    for (int i = 0; i < 100_000; i++)
        safeCounter.incrementAndGet(); // atomic CAS operation
};
```

Example 3 — Thread pool sizing guidance:

```bash
# Optimal thread pool size depends on workload type:

# CPU-bound (image processing, crypto, compression):
# threads = available_processors (or available_processors + 1)
int threads = Runtime.getRuntime().availableProcessors();

# I/O-bound (HTTP calls, DB queries, file I/O):
# Most threads block on I/O; more threads = better utilisation
# threads = processors * (1 + wait_time / cpu_time)
# Example: 8 cores, each request 10ms CPU + 90ms DB wait:
# threads = 8 * (1 + 90/10) = 8 * 10 = 80 threads
# Or: use Java 21 Virtual Threads — let JVM handle it automatically

# Java 21 recommendation for I/O-bound:
ExecutorService exec =
    Executors.newVirtualThreadPerTaskExecutor();
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Threads run truly simultaneously on all machines | On a single-core CPU, threads time-slice — one runs at a time. True parallelism requires multi-core hardware. |
| More threads always means better performance | More threads than CPU cores for CPU-bound work causes contention. For I/O-bound work, virtual threads are preferable to large platform thread pools. |
| Thread creation is free | Platform thread creation allocates a stack (default 8 MB), creates a kernel TCB, and makes OS system calls. For high-concurrency, use thread pools or virtual threads. |
| Killing a thread is safe | Thread.stop() is deprecated for good reason — it can leave shared objects in inconsistent state. Use interrupt() and cooperative cancellation. |
| All threads in a process die when the process exits | Only non-daemon threads keep the JVM alive. Daemon threads are killed when all non-daemon threads finish. |

### 🔥 Pitfalls in Production

**1. Thread Pool Exhaustion — All Threads Blocked on I/O**

```java
// BAD: Fixed thread pool of 10; all blocking on slow DB
ExecutorService pool = Executors.newFixedThreadPool(10);
// 10 simultaneous slow DB queries → pool full
// 11th request waits indefinitely → effectively sequential!

// GOOD for Java 21: Virtual threads for I/O-bound tasks
ExecutorService pool =
    Executors.newVirtualThreadPerTaskExecutor();
// 10,000 simultaneous DB queries possible — VTs unmount during blocking
```

**2. Thread Stack Memory for High Concurrency**

```bash
# BAD: 10,000 threads × 8 MB default stack = 80 GB virtual memory
# Modern OS overcommits, but RSS grows to actual stack usage
# → OOM if many threads actually use their stack deeply

# GOOD: For high concurrency → Java 21 Virtual Threads
# Virtual thread stacks are heap-allocated (~few KB each)
# 10,000 virtual threads ≈ 50 MB heap vs 80 GB virtual memory

# Or: reduce platform thread stack size
java -Xss512k -jar app.jar  # 10,000 threads × 512 KB = 5 GB virtual
```

**3. Not Joining Threads — Lost Exceptions**

```java
// BAD: Threads started but never joined
// Exceptions in run() are silently lost!
Thread t = new Thread(() -> {
    throw new RuntimeException("thread failed"); // lost!
});
t.start();
// main() continues; exception never seen

// GOOD: Set uncaught exception handler
t.setUncaughtExceptionHandler(
    (thread, e) -> log.error("Thread {} failed", thread, e));
t.start();
t.join(); // wait and observe completion
```

### 🔗 Related Keywords

- `Process` — the parent container holding all threads and shared resources.
- `Context Switch` — the OS operation saving/restoring thread state when switching.
- `Thread (Java)` — Java's platform thread, a 1:1 mapping to OS kernel threads.
- `Fiber / Coroutine` — the lightweight alternative to OS threads.
- `Race Condition` — the concurrency bug caused by unsynchronised shared thread access.
- `Concurrency vs Parallelism` — threads enable both (time-sliced concurrency; multi-core parallelism).

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Execution unit in a process: own PC/stack │
│              │ + registers; shared heap with siblings.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Parallelism within a process; server      │
│              │ handling concurrent requests; background  │
│              │ work alongside UI/main thread.            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High concurrency I/O → use Virtual Threads│
│              │ or async; true isolation → use processes. │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Thread: a chef in the kitchen —          │
│              │ own work, shared fridge."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Process vs Thread → Context Switch →      │
│              │ Virtual Memory → Concurrency vs Parallelism│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Java web server uses a fixed thread pool of 200 platform threads. Each request calls a downstream microservice that takes 100ms average. Under load, the average request rate is 400 requests/second. Using Little's Law (L = λW), calculate the expected number of concurrently active requests and determine whether the pool is adequately sized. Then explain how replacing the fixed thread pool with `Executors.newVirtualThreadPerTaskExecutor()` changes the equation — specifically, why the 200-thread constraint becomes irrelevant with virtual threads for I/O-bound workloads.

**Q2.** OS thread context switching preserves the thread's register state in the kernel's Thread Control Block (TCB). On a modern 64-bit x86 Linux kernel, the register save/restore includes: general-purpose registers (16), floating-point state (xsave area, ~512-4096 bytes), segment registers, and CR3 (page table base — only changed on process switch, not thread switch within same process). Calculate the minimum state size saved per thread context switch, and explain why thread context switch within a process is significantly faster than a process context switch — specifically what hardware operation is avoided.

