---
layout: default
title: "Context Switch"
parent: "Operating Systems"
nav_order: 95
permalink: /operating-systems/context-switch/
number: "0095"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, Thread, CPU Registers, Scheduler / Preemption
used_by: Scheduler / Preemption, Thread Pool, Performance Tuning
related: Fiber / Coroutine, Scheduler / Preemption, TLB
tags:
  - os
  - internals
  - performance
  - intermediate
---

# 095 — Context Switch

⚡ TL;DR — A context switch is the OS saving one process/thread's CPU state and loading another's, enabling the illusion of simultaneous execution on a single core.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #095 │ Category: Operating Systems │ Difficulty: ★★☆ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ Process, Thread, CPU Registers │ │
│ Used by: │ Scheduler, Thread Pool, Perf Tuning │ │
│ Related: │ Fiber / Coroutine, TLB │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Imagine a single-core CPU in the 1960s: Program A runs to completion,
then Program B starts. If Program A takes 10 minutes, the user waits
10 minutes before Program B begins. There is no "multitasking."

As operating systems became time-sharing systems — where multiple users
submitted programs that should all make progress — this sequential model
became unworkable. Program A might be waiting for user input for seconds.
During that wait, the CPU is idle. Meanwhile, Program B, Program C, and
Program D are ready to run but sitting in a queue.

THE BREAKING POINT:
A CPU doing nothing while a program waits for I/O wastes the most
valuable resource in the system. Without a way to switch between programs
mid-execution, a slow or blocking program monopolizes the CPU.

THE INVENTION MOMENT:
This is exactly why **Context Switch** was invented — the OS can save
every detail of Program A's execution state, give the CPU to Program B,
and later restore Program A exactly where it left off, creating the
illusion that all programs run simultaneously.

### 📘 Textbook Definition

A **context switch** is the procedure by which the operating system saves
the complete CPU execution state (context) of the currently executing
process or thread into its Process/Thread Control Block, and loads the
saved context of the next scheduled process or thread. The saved context
includes: all CPU registers (general-purpose, floating-point, SIMD),
the program counter, stack pointer, CPU flags, and (for process switches)
the memory management unit page table base register. Context switches are
triggered by timer interrupts (preemptive), I/O completion, system calls,
or explicit yield operations.

### ⏱️ Understand It in 30 Seconds

**One line:**
A context switch pauses one running task and resumes another, perfectly.

**One analogy:**

> Imagine a chef who cooks three dishes simultaneously. They stir pasta,
> then set a mental note ("pasta needs 2 more stirs, pot on medium heat"),
> walk to the grill, flip the steak, note "steak is medium rare, 1 minute
> left", then return to the pasta. The mental notes — the saved state —
> are the context. The walking between stations is the context switch.

**One insight:**
The context switch is not free. Every switch costs 1–10 microseconds of
real time where the CPU does no useful work — it's pure overhead. High
context switch rates (thousands per second per core) visibly reduce
throughput. This is the hidden cost of "just add more threads."

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. **Complete state capture**: when a process is suspended, _every_ aspect
   of its CPU state must be saved so resumption is indistinguishable from
   never stopping.
2. **Atomic save/restore**: the save and restore operations must not be
   interrupted — if the CPU state is partially saved/restored, the program
   is corrupted.
3. **Triggered by privileged code**: only the kernel can perform context
   switches — user-space code cannot modify another process's registers.

DERIVED DESIGN:
The save/restore must happen at the exact moment the CPU transitions to
kernel mode (via interrupt or syscall). The kernel then decides which
process/thread to schedule next (scheduler), loads its saved state, and
returns to user mode in the new process's context.

THE TRADE-OFFS:
Gain: CPU time-sharing; I/O latency hidden by switching to ready tasks;
responsive interactive systems.
Cost: each switch costs ~1–10 µs of pure overhead; CPU caches and TLB
contain the previous process's data and become "cold" after switching;
high switch rate reduces throughput measurably.

### 🧪 Thought Experiment

SETUP:
Thread A is computing a matrix multiplication (CPU-bound, no IO).
Thread B is waiting for a database response (IO-bound).

WHAT HAPPENS WITHOUT CONTEXT SWITCH:
Thread A runs for 100 ms. Thread B's DB response arrived at t=5ms
but cannot be processed. By the time Thread A finishes, the DB
connection has timed out (30s timeout). Thread B fails its request.
The CPU was "busy" but Thread B's work was lost.

WHAT HAPPENS WITH CONTEXT SWITCH:
Thread A runs for 5ms (its time slice). Timer interrupt fires →
context switch to Thread B. Thread B's context is restored. Thread B
reads the DB response, processes it in 2ms, completes. Context switch
back to Thread A. Thread A resumes exactly where it was (program
counter and all registers restored). Both threads make progress.

THE INSIGHT:
Context switching converts "wasted wait time" into productive CPU time
for other threads. The CPU never idles while there's runnable work.

### 🧠 Mental Model / Analogy

> A context switch is like a video game save-and-load. The OS hits
> "Save" (captures all CPU registers to memory), loads a different
> save file (different process/thread), and the CPU continues from
> exactly where the new save left off.

**Analogy mapping:**

- "Save game state" → write CPU registers to PCB/TCB in RAM
- "Load different save file" → load another process/thread's PCB/TCB
- "Resume from checkpoint" → set CPU program counter to saved value
- "Game world you were in" → virtual address space (process switch only)
- "Save slot in memory" → Process Control Block / Thread Control Block

Where this analogy breaks down: video game saves are user-initiated and
slow; OS context switches are automatic, sub-millisecond, and transparent
to the running code.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you have many programs running and only one CPU, the OS switches
the CPU between them so fast that everything appears to run at once.
Each switch saves the current program's "place" and loads another's.

**Level 2 — How to use it (junior developer):**
Context switches are transparent — your code doesn't control them.
But you can observe them: `vmstat 1` shows context switches per second.
High rates (>100,000/sec per core) indicate too many threads or too
small time slices. Reduce by using fewer threads or async IO.

**Level 3 — How it works (mid-level engineer):**
A timer interrupt fires every ~4ms (configurable HZ value, e.g. HZ=250).
The CPU switches to kernel mode, saves all registers to the current
`task_struct`. The scheduler picks the next thread (CFS in Linux). The
kernel loads the new thread's registers, switches the page table base
register (CR3 on x86) if it's a different process (causing TLB flush),
and returns to user mode. Total overhead: ~1–10 µs including cache warm-up.

**Level 4 — Why it was designed this way (senior/staff):**
The x86 CPU has a Task State Segment (TSS) specifically designed for
hardware-assisted context switches. However, modern OSes use _software_
context switches — saving only the registers actually used (caller-saved
vs callee-saved registers) and deferring FPU/SIMD state save until
actually needed (lazy FPU switching). This optimization was critical
because full SIMD register sets (512 bytes for AVX-512) make context
saves expensive. The kernel tracks whether a process has used FPU and
only saves/restores those registers if needed.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│          CONTEXT SWITCH SEQUENCE (Linux)         │
├──────────────────────────────────────────────────┤
│  1. TRIGGER:                                     │
│     • Timer interrupt (preemption)               │
│     • Syscall (voluntary or blocking IO)         │
│     • Explicit yield() or sleep()                │
│                                                  │
│  2. ENTER KERNEL MODE:                           │
│     • CPU auto-saves user RSP → kernel stack     │
│     • CPU switches to kernel stack               │
│     • CPU saves: RIP, RFLAGS, CS, SS             │
│                                                  │
│  3. SAVE CURRENT CONTEXT:                        │
│     • kernel saves: RAX–R15 (all GPRs)          │
│     • kernel saves: FS/GS segment registers      │
│     • context stored in task_struct              │
│                                                  │
│  4. SCHEDULER RUNS:                              │
│     • CFS picks next thread                      │
│     • next task_struct selected                  │
│                                                  │
│  5. LOAD NEW CONTEXT:                            │
│     • if different process: load new CR3         │
│       → TLB flush (expensive!)                   │
│     • restore GPRs from new task_struct          │
│     • restore FS/GS                              │
│                                                  │
│  6. RETURN TO USER MODE:                         │
│     • iretq → restore RIP, RFLAGS, RSP          │
│     • CPU now executing new thread               │
└──────────────────────────────────────────────────┘
```

**Thread vs Process context switch cost:**

```
┌──────────────────────────────────────────────────┐
│  Thread switch (same process):   ~1–3 µs         │
│  • Save/restore ~16 registers                    │
│  • Update scheduling data                        │
│  • No TLB flush (same address space)             │
│  • Cache still warm (same heap)                  │
│                                                  │
│  Process switch (different process): ~5–10 µs   │
│  • Same register save/restore                    │
│  • Load new page table (CR3 write)               │
│  • TLB flush: ~500ns–2µs                         │
│  • Cache miss: next 100µs slower (cold cache)    │
└──────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
Thread A running (user mode)
  → Timer interrupt fires (every ~4ms)
  → CPU enters kernel mode automatically
  → Kernel saves Thread A's registers to TCB
  → Scheduler picks Thread B (highest priority)
  → [CONTEXT SWITCH ← YOU ARE HERE]
  → Kernel loads Thread B's registers from TCB
  → CPU returns to user mode in Thread B's context
  → Thread B runs from exactly where it last stopped
```

FAILURE PATH:

```
Context switch during signal delivery
  → Signal received while in kernel mode
  → Kernel must save kernel-mode context too
  → Nested interrupts possible (interrupt in interrupt)
  → Interrupt stack grows → potential stack overflow in kernel
  → Kernel crash (oops) or panic
```

WHAT CHANGES AT SCALE:
At 100,000 context switches/second per core, the overhead is
100,000 × 5µs = 500ms per second — half the CPU time is wasted on
bookkeeping. Profiling shows high `%sy` (system time) in `top`.
Solutions: reduce thread count (async IO), pin CPU-bound threads to
cores (reduce cache churn), increase scheduler time slice (HZ tuning).

### 💻 Code Example

Example 1 — Observing context switch rate:

```bash
# Show context switches per second (cs column)
vmstat 1 5

# Output example:
# procs  memory    swap io   system    cpu
# r  b   swpd free  si  so  bi   bo  in   cs  us sy id wa
# 2  0   0 8G   0   0   0    0  500 1200  15  3 80  0

# cs=1200 switches/second — normal for a busy server
# cs=50000 — investigate thread count and IO patterns
```

Example 2 — Reducing context switches with thread pools:

```java
// BAD: one thread per task — thousands of threads, huge cs rate
void handleRequests(List<Request> reqs) {
    reqs.forEach(req ->
        new Thread(() -> process(req)).start()
    );
    // 10,000 requests = 10,000 threads = massive context switching
}

// GOOD: bounded thread pool caps concurrency
ExecutorService pool =
    Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors() * 2
    );
void handleRequests(List<Request> reqs) {
    reqs.forEach(req -> pool.submit(() -> process(req)));
    // Thread count bounded to ~16, context switches minimal
}
```

Example 3 — Pinning threads to CPU cores (reduce cache churn):

```java
// Affinity: keep thread on same CPU core
// Requires JNA or JVM-level support:
// taskset -c 0,1 java -jar myapp.jar
// Sets JVM process to only run on cores 0 and 1
// Prevents TLB flushes from inter-core migration

// In production (Aeron/Chronicle style):
// Use thread affinity library:
// AffinityLock al = AffinityLock.acquireCore();
// try { // thread pinned to dedicated core
// } finally { al.release(); }
```

### ⚖️ Comparison Table

| Switch Type        | Cost       | TLB Flush | Cache Impact | Trigger         |
| ------------------ | ---------- | --------- | ------------ | --------------- |
| Thread (same proc) | ~1 µs      | No        | Warm         | Timer, yield    |
| Process switch     | ~5–10 µs   | Yes       | Cold         | Timer, syscall  |
| Fiber switch       | ~10–100 ns | No        | Warm         | Explicit yield  |
| Interrupt          | ~100 ns    | No        | Minimal      | Hardware signal |

How to choose: minimize process switches for cache-sensitive workloads;
use fibers/coroutines to eliminate OS context switches for IO-heavy code.

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                        |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| "Context switches are free"                                | Each costs 1–10 µs plus cache cold-start; at high rates this is measurable throughput loss                     |
| "More CPUs eliminate context switch cost"                  | More CPUs reduce per-core switch rate, but a process still pays TLB and cache cost when migrated between cores |
| "Voluntary yielding avoids context switch overhead"        | Voluntary yield still enters kernel mode and executes the scheduler — the register save/restore still happens  |
| "Context switches only happen between different processes" | Thread switches within the same process are also context switches — just without the address space switch      |
| "High context switch rate always means a problem"          | A busy IO-bound server naturally has high cs rates — the issue is when cs rate exceeds useful work             |

### 🚨 Failure Modes & Diagnosis

**1. Thrashing from excessive context switches**

Symptom:
`top` shows high `sy` (system) CPU%. `vmstat 1` shows cs > 50,000/sec.
Throughput lower than expected despite low CPU `us` usage. Latency high.

Root Cause:
Too many threads relative to CPU cores. Scheduler runs constantly
switching between runnable threads, spending more time on bookkeeping
than actual computation.

Diagnostic:

```bash
# Context switches per second
vmstat 1 | awk '{print $12}' | tail -n +3
# Per-process context switch count
cat /proc/<pid>/status | grep ctxt
# voluntary_ctxt_switches + nonvoluntary_ctxt_switches
```

Fix: reduce thread pool size to `2 × CPU_count` for CPU-bound work;
use async IO for IO-bound work to eliminate blocked-thread overhead.

Prevention: set thread pool size based on workload type, not request count.

**2. Cache thrashing from CPU migration**

Symptom:
Benchmark shows inconsistent latency. `perf stat` shows high cache-miss
rate. Performance varies run-to-run despite identical workload.

Root Cause:
Threads migrate between CPU cores. Each migration invalidates L1/L2 cache
for that thread's working set. Rebuilding cache takes hundreds of µs.

Diagnostic:

```bash
perf stat -e cache-misses,cache-references,\
context-switches,cpu-migrations -p <pid> sleep 5
# High cpu-migrations with high cache-misses = thread migration issue
```

Fix: pin latency-sensitive threads to specific cores:

```bash
taskset -cp 0,1 <pid>  # restrict process to cores 0 and 1
```

Prevention: use CPU affinity for latency-sensitive services; use NUMA-
aware memory allocation to keep threads near their memory.

**3. Priority Inversion via Context Switch**

Symptom:
High-priority thread runs slower than low-priority thread. System appears
responsive to low-priority work but unresponsive to high-priority tasks.

Root Cause:
Low-priority thread holds a lock; high-priority thread waits for lock but
cannot preempt the low-priority holder. Medium-priority threads preempt
the low-priority holder, delaying lock release indefinitely.

Diagnostic:

```bash
# Linux: check priority and scheduling class
chrt -p <pid>     # scheduling policy and priority
ps -eo pid,pri,cmd | sort -k2 -n | head
# Java: thread dump shows waiting threads and lock holders
jstack <java_pid> | grep -A5 "waiting to lock"
```

Fix: use priority inheritance mutexes (`PTHREAD_PRIO_INHERIT`); in Java,
use `PriorityBlockingQueue` with correct priority assignment.

Prevention: avoid holding mutexes across preemption points; design lock
hierarchies to prevent priority inversion scenarios.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process` — context switch saves process state; understand the PCB
- `Thread` — thread switches are the most common form of context switch
- `CPU Registers` — the hardware state that must be saved/restored

**Builds On This (learn these next):**

- `Scheduler / Preemption` — the scheduler decides WHEN to context switch
- `TLB` — the hardware cache that gets flushed on process switches
- `Cache Line` — why cache "coldness" after a switch costs extra time

**Alternatives / Comparisons:**

- `Fiber / Coroutine` — user-space switching; avoids OS context switch overhead
- `Async I/O` — eliminates blocked-thread context switches for IO waits

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ OS saving one task's CPU state, loading │
│ │ another's to enable time-sharing │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ One CPU must appear to run many tasks │
│ SOLVES │ simultaneously │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ Context switch has a real cost: 1–10 µs │
│ │ plus cache cold-start; high rates hurt │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ Unavoidable — the OS does this; tune by │
│ │ reducing thread count and using async IO │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ Avoid excessive switching by designing │
│ │ for fewer, busier threads │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ Apparent parallelism vs throughput loss │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "The price of multitasking is paid in │
│ │ microseconds, thousands of times/second" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Scheduler → TLB → Cache Line │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A Java application uses 200 threads to handle incoming requests.
You observe that CPU utilization is 80% but `vmstat` shows 40,000 context
switches per second and throughput is only 60% of what you expected from
a single-threaded benchmark. Trace step-by-step what is consuming the
remaining 20% CPU and causing the throughput gap — is it the context
switch cost itself, cache cold-start, or scheduler overhead? How would
you verify your hypothesis with `perf stat`?

**Q2.** Locking a `synchronized` block in Java and performing a blocking
`socket.read()` both cause a context switch. Describe the precise kernel
path for each case — what triggers the switch, what kernel data structure
is updated, and how does the thread get rescheduled when the lock is
released vs when data arrives on the socket? What is different about the
two paths that makes IO-bound waits more expensive than lock-based waits?
