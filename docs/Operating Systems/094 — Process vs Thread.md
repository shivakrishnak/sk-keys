---
layout: default
title: "Process vs Thread"
parent: "Operating Systems"
nav_order: 94
permalink: /operating-systems/process-vs-thread/
number: "094"
category: Operating Systems
difficulty: ★☆☆
depends_on: Process, Thread (OS), Fiber / Coroutine
used_by: Concurrency vs Parallelism, Thread Safety, Context Switch
tags:
  - os
  - foundational
  - concurrency
---

# 094 — Process vs Thread

`#os` `#foundational` `#concurrency`

⚡ TL;DR — Processes have isolated address spaces (high fault isolation, high IPC cost); threads share a process's address space (fast communication, shared bugs, lower overhead).

| #094 | Category: Operating Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Process, Thread (OS), Fiber / Coroutine | |
| **Used by:** | Concurrency vs Parallelism, Thread Safety, Context Switch | |

---

### 📘 Textbook Definition

A **process** is an OS-level unit of resource allocation with its own virtual address space, file descriptors, and kernel data structures — isolated from all other processes. A **thread** is a unit of execution within a process, sharing the process's address space and resources with other threads in the same process. The fundamental distinction: processes share nothing by default (isolation), threads share everything in their containing process (communication). Process context switch involves address space switch (TLB flush). Thread context switch stays within the same address space (faster). Thread failure can corrupt the entire process; process failure is isolated from other processes.

### 🟢 Simple Definition (Easy)

A process is its own house with its own locks. Threads are people in the same house — they live together, share the furniture, and can bump into each other.

### 🔵 Simple Definition (Elaborated)

The fundamental trade-off between processes and threads: isolation vs. speed of communication. Processes are isolated — they cannot access each other's memory, a crash in one doesn't affect others, but sharing data requires explicit IPC (sockets, pipes). Threads within a process share all memory — accessing a shared object is just a pointer dereference (fast), but a thread crashing with an uncaught exception can kill the entire process, and all shared data requires synchronisation. Most applications use threads for concurrent work within one service and processes for isolation between services.

### 🔩 First Principles Explanation

**What processes share vs. isolate:**

```
Process A                    Process B
┌──────────────────┐        ┌──────────────────┐
│ Virtual address  │        │ Virtual address   │
│ space (private)  │        │ space (private)   │
│ Code, heap,      │        │ Code, heap,       │
│ stack, data      │        │ stack, data       │
│ File descriptors │        │ File descriptors  │
│ (unique table)   │        │ (unique table)    │
└──────────────────┘        └──────────────────┘
     Cannot directly read each other's memory
     Communicate via: IPC (pipes, sockets, shared memory, signals)
```

**What threads share vs. own:**

```
Process (one address space)
├── Thread 1: [own PC] [own registers] [own stack]
├── Thread 2: [own PC] [own registers] [own stack]
└── Thread 3: [own PC] [own registers] [own stack]
     All share: Heap, Static/Global Data, Code, File Descriptors
     Thread 1 can directly read Thread 2's heap objects
     → requires synchronisation for correctness
```

**Quantitative comparison:**

```
                        Process         Thread
Creation time           ~1-10 ms        ~0.1-1 ms
Memory overhead         MB+             ~1 MB stack + minimal TCB
Context switch          ~10-100 µs      ~1-10 µs
Communication speed     IPC (µs–ms)     Shared memory (ns)
Fault isolation         Complete        None (one crash = all crash)
Security isolation      Strong (MMU)    None
Scalability (concurrency) Hundreds       Thousands (VTs: millions)
```

**When to use processes:**

1. **Different trust levels:** Browser runs each tab in a separate process — one malicious tab can't read another's cookies.
2. **Different failure domains:** Nginx master process monitors worker processes — a worker crash doesn't bring down others.
3. **Different runtimes/languages:** Microservices in different languages communicating over HTTP.
4. **OS resource accounting:** Container = cgroup + namespace = process-level isolation.

**When to use threads:**

1. **Low-latency communication:** Two parts of an application sharing a cache — heap access is nanoseconds vs IPC microseconds.
2. **Shared large data:** Image processing — load 1 GB image once into heap, process regions in parallel with threads.
3. **HTTP servers:** Concurrent request handling — shared connection pool, caches.
4. **Background work:** JVM GC threads, JIT compilation threads — share the heap directly.

### ❓ Why Does This Exist (Why Before What)

This is a design choice, not a mechanism from scratch. The key question is always: "How much do these units need to SHARE, and how much do they need to be ISOLATED?"

Without this concept:
1. Single-process servers with one thread: sequential, blocks on I/O.
2. Multi-process servers (Apache pre-fork): scale but expensive memory use.
3. Multi-thread servers (Tomcat): efficient but single crash kills server.

### 🧠 Mental Model / Analogy

> Processes are separate apartments in a building — each has its own kitchen, living room, and locks. Tenants (code) can't walk into each other's apartments without an invitation (IPC). Threads are roommates in one apartment — they share all the same spaces. Cooking together (concurrent access to shared data) requires coordination (mutexes, synchronized). If a roommate burns down the kitchen (crash), all roommates lose their home (process dies). Different apartments burning down doesn't affect other tenants.

"Apartments" = processes, "roommates" = threads, "shared kitchen" = shared heap, "burning kitchen" = thread crashing entire process, "invitation" = IPC.

### ⚙️ How It Works (Mechanism)

**Context switch difference:**

```
Thread switch (within same process):
  1. Save current thread's registers to TCB (user-space or kernel)
  2. Load next thread's registers from TCB
  3. Stack pointer changes to next thread's stack
  NO address space change → NO TLB flush
  Cost: ~1-10 µs typical

Process switch:
  1. Save current process's registers + full state
  2. Switch CR3 (page table base register) → new address space
  3. TLB flush (all cached virtual→physical translations invalidated)
  4. Load next process's state
  Cost: ~10-100 µs typical
  High cost: TLB warm-up takes many memory accesses after switch
```

**IPC vs shared memory bandwidth:**

```
Communication method        Latency    Throughput
──────────────────────────────────────────────────
Shared memory (threads)     ~10 ns     ~50 GB/s
Shared memory segment (IPC) ~500 ns    ~20 GB/s
Unix domain socket (same host) ~2 µs   ~5 GB/s
TCP loopback (same host)     ~20 µs    ~2 GB/s
```

**Production architecture patterns using both:**

```
Nginx: Master Process (root, manages workers)
       ├── Worker Process 1: handles connections with epoll + threads
       ├── Worker Process 2: handles connections with epoll + threads
       └── Worker Process N: (N = CPU count)
       → Process isolation: worker crash doesn't affect master
       → Thread concurrency: each worker handles thousands of connections

JVM: Single OS Process
       ├── Main thread
       ├── HTTP handler threads (100–200)
       ├── GC threads (4-8)
       ├── JIT compiler thread
       └── Background daemon threads
```

### 🔄 How It Connects (Mini-Map)

```
Process (isolated, expensive IPC)
    ↕ vs
Thread (OS) (shared, fast communication, shared failure)
    ↕ vs
Fiber (user-space thread, cheapest)
    ↓
Concurrency vs Parallelism
Thread Safety (needed for shared-memory threads)
Context Switch (cost difference: process > thread > fiber)
```

### 💻 Code Example

Example 1 — Demonstrating isolation (process) vs sharing (thread):

```java
// Threads share heap — direct object reference sharing
AtomicInteger sharedCounter = new AtomicInteger(0);
var t1 = Thread.ofPlatform().start(() ->
    sharedCounter.addAndGet(1000)); // direct heap access
var t2 = Thread.ofPlatform().start(() ->
    sharedCounter.addAndGet(1000)); // same object!
t1.join(); t2.join();
System.out.println(sharedCounter.get()); // 2000 ✓

// Processes cannot share — must use IPC
// ProcessA creates shared memory segment; ProcessB maps it
// Or: communicate via socket, pipe, file
```

Example 2 — Nginx-style multi-process model:

```java
// In Java: pre-fork server model (process per CPU)
for (int i = 0; i < Runtime.getRuntime().availableProcessors(); i++) {
    new ProcessBuilder("java", "-jar", "worker.jar")
        .inheritIO()
        .start();
    // Each worker is a separate process
    // OS routes connections to workers
    // Worker crash doesn't affect siblings
}
```

Example 3 — Checking if a thread crash kills the process:

```java
// Thread crash terminates the process (by default)
Thread t = Thread.ofPlatform().start(() -> {
    throw new OutOfMemoryError("simulated OOM");
    // Default uncaught handler: prints stack trace, terminates JVM
});
t.join();
// If no UncaughtExceptionHandler: JVM exits!

// Protect with UncaughtExceptionHandler
t.setUncaughtExceptionHandler((thread, ex) -> {
    log.error("Thread {} died: {}", thread.getName(), ex.getMessage());
    // Process survives; thread is terminated
});
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Threads are always better than processes for performance | For CPU-bound parallel work, thread vs process is mostly similar. For I/O-bound concurrency, threads (and fibers) win. For fault isolation, processes win regardless of performance. |
| Processes can never share memory | Processes can share memory via mmap, POSIX shared memory, or System V shared memory. This is explicit, controlled sharing — vs threads' implicit total sharing. |
| Microservices must be separate processes | Microservices CAN run in separate OS processes on the same machine, but in containers, each microservice is typically a separate OS process in its own container. |
| Thread exit is always clean | A thread that calls System.exit() or Runtime.halt() terminates the ENTIRE JVM process — all other threads immediately die. |
| Using threads in Java is the same as using threads in C | Java threads are OS kernel threads with JVM-level safety. C pthreads are OS kernel threads with no language-level safety (manual memory management, segfaults possible). |

### 🔥 Pitfalls in Production

**1. Thread Leak Crashing the Process**

```java
// BAD: Creating threads in a loop without bounds
while (requestsArriving) {
    new Thread(handler).start(); // unbounded thread creation
}
// 10,000 threads × 8 MB = 80 GB virtual memory → OOM
// All threads share the JVM process → OOM kills everything

// GOOD: Use a bounded thread pool
ExecutorService pool = Executors.newFixedThreadPool(200);
pool.submit(handler);
```

**2. One Uncaught Exception Killing the Entire Service**

```java
// BAD: No global exception handler
// Any thread throwing Error → JVM exits

// GOOD: Set default uncaught exception handler
Thread.setDefaultUncaughtExceptionHandler((thread, ex) -> {
    log.error("Uncaught exception in thread {}", thread, ex);
    // Optionally: alert, restart just this service component
    // But do NOT call System.exit() here — let other threads continue
});

// For Spring Boot: ThreadPoolTaskExecutor and @Async methods
// configure rejection policy + exception handlers explicitly
```

**3. Process IPC Bottleneck — Choosing Wrong Communication**

```bash
# BAD: Two microservices on same machine communicate via HTTP
# ~20 µs per round trip + serialisation overhead

# GOOD: If on same machine and performance-critical:
# Unix Domain Socket: ~2 µs
# Shared memory (mmap): ~500 ns
# But: evaluate correctness and maintainability first
```

### 🔗 Related Keywords

- `Process` — the isolation unit; full address space separation.
- `Thread (OS)` — the sharing unit; concurrent execution within one address space.
- `Fiber / Coroutine` — lighter than threads; cooperative scheduling.
- `Context Switch` — faster within a process (threads) than between processes.
- `Thread Safety` — required because threads share heap data.
- `Concurrency vs Parallelism` — threads enable both; processes enable parallelism.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│             PROCESS              │     THREAD            │
│ Own address space                │ Shared address space  │
│ Isolated failure                 │ Shared failure        │
│ Expensive IPC                    │ Fast shared memory    │
│ Expensive create/switch          │ Cheap create/switch   │
│ Strong security isolation        │ No isolation          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Process: own house. Thread: roommate.   │
│              │ Pick based on isolation need."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Context Switch → Thread Safety → IPC      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A senior engineer argues that modern containerised microservices (each service in its own Docker container = own OS process) are the "process isolation model" writ large across a distributed system. Compare this claim: what exactly does Docker container isolation provide that bare processes on the same machine don't, what OS isolation techniques does it additionally use (namespaces, cgroups), and what security vectors remain possible between containers on the same host that would be blocked between containers on different physical machines?

**Q2.** Chrome browser uses multi-process architecture where each tab runs in a separate renderer process (not just a thread). Given that JavaScript in each tab is single-threaded anyway, and all tabs could theoretically run in the same process with threads, analyse why Google made this architectural decision — citing specific security properties, fault isolation scenarios, and memory management advantages of separate renderer processes — and identify the performance cost Chrome pays for this isolation that a single-process browser would not.

