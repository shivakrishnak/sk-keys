---
layout: default
title: "Fiber / Coroutine"
parent: "Operating Systems"
nav_order: 93
permalink: /operating-systems/fiber-coroutine/
number: "093"
category: Operating Systems
difficulty: ★★☆
depends_on: Thread (OS), Process vs Thread, Concurrency vs Parallelism
used_by: Virtual Threads (Project Loom), Kotlin Coroutines, Go Goroutine Scheduler, Continuation, Reactive Programming
tags:
  - os
  - concurrency
  - intermediate
---

# 093 — Fiber / Coroutine

`#os` `#concurrency` `#intermediate`

⚡ TL;DR — Cooperative, lightweight execution units that yield control voluntarily at suspension points, enabling massive concurrency on a small thread pool without OS-level context switch overhead.

| #093 | Category: Operating Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread (OS), Process vs Thread, Concurrency vs Parallelism | |
| **Used by:** | Virtual Threads (Project Loom), Kotlin Coroutines, Go Goroutine Scheduler, Continuation, Reactive Programming | |

---

### 📘 Textbook Definition

A **fiber** (also called a green thread, cooperative thread, or user-mode thread) is a unit of execution managed entirely in user space, without kernel involvement in scheduling. **Coroutines** are a language-level abstraction of the same concept: functions that can suspend (`yield` / `await` / `suspend`) and resume at defined points. Both are multiplexed onto a small pool of OS threads by a user-space scheduler. Context switches between fibers are cooperative: a fiber yields explicitly (or at designated suspension points) rather than being preempted by the OS. This enables millions of concurrent fibers with microsecond context switch costs vs. OS thread's ~1-10 microsecond kernel context switch.

### 🟢 Simple Definition (Easy)

A fiber is a super-lightweight "mini thread" that voluntarily pauses when it has to wait, freeing the thread to run another fiber — like dozens of tasks sharing one worker who switches between them at natural wait points.

### 🔵 Simple Definition (Elaborated)

OS threads are managed by the kernel — it preempts them involuntarily (taking the CPU away at any time). Fibers/coroutines voluntarily yield control at suspension points they define (usually I/O waits, sleeps, or explicit yield calls). This cooperativeness has a huge benefit: no kernel involvement means no expensive system call for context switch — just a few instructions to save registers and switch stacks, entirely in user space. The result: you can have 1 million concurrent fibers on a machine with 8 CPU cores consuming only ~8 OS threads, while 1 million OS threads would require ~8 TB of virtual memory for stacks alone.

### 🔩 First Principles Explanation

**Problem: OS threads are expensive at scale**

- Default stack: 8 MB per OS thread.
- 10,000 connections × 8 MB = 80 GB virtual memory.
- OS scheduler must context-switch between 10,000 threads — kernel overhead.
- Real-world web servers can't use 1 OS thread per connection at scale.

**Fiber/Coroutine solution:**

```
Fiber runtime:
  - Small stack (4 KB to 64 KB, or heap-allocated and growing)
  - User-space scheduler (not OS)
  - Cooperative yield at I/O / sleep / explicit yield

10,000 fibers × 4 KB = 40 MB (vs 80 GB for OS threads)
Context switch: ~100 instructions (register save/restore in user space)
vs OS context switch: ~1000 instructions + kernel trap + TLB ops
```

**Cooperative vs Preemptive:**

```
Preemptive (OS threads):
  Any instruction can be interrupted → thread cannot control WHEN it yields
  OS timer interrupt → saves all registers → switches to next thread
  Pro: fair scheduling, no starvation from CPU-hog
  Con: expensive; need synchronisation on every shared data access

Cooperative (Fibers/Coroutines):
  Fiber yields only at defined suspension points
  Pro: no synchronisation needed for non-yielded state; very fast switch
  Con: one CPU-bound fiber blocks all fibers on that OS thread
       (unless work-stealing scheduler detects long-running task)
```

**Coroutine model (Kotlin/Python/JS async):**

```kotlin
// Kotlin Coroutine — suspends at 'await' points
suspend fun fetchData(): String {
    delay(1000)          // suspend: release thread
    return httpClient.get("...") // suspend: release thread
}

launch {               // start coroutine (not a thread)
    val result = fetchData() // suspend here, thread continues elsewhere
    println(result)          // resumed when fetchData() returns
}
```

**Go goroutines:**

```go
// Go: goroutines are M:N user-space threads on goroutine scheduler
// 100,000 goroutines possible; mapped to GOMAXPROCS OS threads
go func() {
    // this runs as a goroutine
    time.Sleep(1 * time.Second) // cooperative yield at sleep
    fmt.Println("Done")
}()
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Fibers (OS threads only):

- 1 million simultaneous API clients: 1 million OS threads = 8 TB stack memory.
- High context-switch rate for I/O-bound workloads wastes kernel time.
- Reactive/async programming needed as workaround (callback hell, CompletableFuture chains).

What breaks without it:
1. Node.js style single-threaded async is necessary to handle 10k+ connections — not needed with fibers.
2. Kotlin/Python async coroutines enable sequential-looking code for async operations.

WITH Fibers/Coroutines:
→ Sequential code style preserved (no callback inversion).
→ Massive concurrency without massive thread count.
→ Near-zero overhead for million-concurrent-connection servers.

### 🧠 Mental Model / Analogy

> Fibers are like cooperative carpoolers. OS threads are self-driving taxis — the city (OS) controls when each taxi moves and can stop any taxi at any time (preemption). Fibers are carpoolers who all agree to drive together: each drives until they hit a red light (I/O wait), then the next car takes over. The city only needs to manage 8 roads (OS threads), not 1 million cars. Carpoolers can communicate freely in the car (no synchronisation overhead) — the risk: if one driver ignores red lights (CPU-bound loop), they block the whole group.

"Taxis" = OS threads, "carpoolers" = fibers, "red light" = I/O wait / yield point, "8 roads" = OS thread pool, "ignoring red lights" = CPU-bound fiber.

### ⚙️ How It Works (Mechanism)

**Fiber runtime internals:**

```
User-space scheduler maintains:
  - Run queue: ready fibers
  - Blocked queue: fibers waiting for I/O/sleep

Fiber 1 runs → calls read() → I/O interrupted (non-blocking syscall):
  epoll/kqueue registers interest for fd
  Fiber 1 moved to blocked queue
  Scheduler picks next ready fiber (Fiber 2)
  Fiber 2 runs on same OS thread
  ...
I/O ready for Fiber 1's fd:
  epoll_wait returns → Fiber 1 moved to run queue
  Next scheduling opportunity → Fiber 1 resumes
```

**Java Virtual Threads (JEP 444, Java 21):**

```
Virtual Thread = JVM-managed fiber
  - Heap-allocated continuation (stack snapshot)
  - Carrier thread pool = N OS threads (default: N = CPU cores)
  - Blocking operation → unmount from carrier (save continuation to heap)
  - Carrier free to run another VT
  - I/O done → remount VT on available carrier
```

**Kotlin coroutines dispatchers:**

```kotlin
// Different dispatchers = different thread pools
withContext(Dispatchers.IO) {
    // I/O-bound: dedicated IO thread pool (elastic)
    readFile()
}
withContext(Dispatchers.Default) {
    // CPU-bound: fixed to CPU count
    heavyComputation()
}
withContext(Dispatchers.Main) {
    // UI thread only (Android)
    updateUI()
}
```

### 🔄 How It Connects (Mini-Map)

```
OS Thread (kernel-managed, preemptive, expensive)
        ↓ user-space alternative
Fiber / Coroutine ← you are here
  (user-managed, cooperative, cheap)
        ↓ Java implementation
Virtual Threads (Project Loom — JVM-managed fibers)
Continuation (saved stack state enabling suspend/resume)
        ↓ language-level implementations
Kotlin Coroutines | Python asyncio | Go goroutines
JavaScript async/await | C# async/await
```

### 💻 Code Example

Example 1 — Java Virtual Threads (JVM fibers):

```java
// 1 million virtual threads — impossible with platform threads
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 1_000_000; i++) {
        int taskId = i;
        exec.submit(() -> {
            // I/O wait — VT unmounts from carrier
            Thread.sleep(Duration.ofMillis(100));
            // Carrier free during sleep; remounts here
            return "Task " + taskId + " done";
        });
    }
} // ~100ms total elapsed; not 100M ms sequentially
```

Example 2 — Kotlin Coroutines (structured concurrency):

```kotlin
import kotlinx.coroutines.*

// coroutineScope ensures all children complete before return
suspend fun fetchAllUsers(ids: List<Long>): List<User> =
    coroutineScope {
        ids.map { id ->
            async {              // each async = one coroutine (fiber)
                fetchUser(id)   // suspends on I/O, releases thread
            }
        }.awaitAll()            // wait for all coroutines
    }
// 1000 IDs → 1000 coroutines → concurrent I/O → not 1000 OS threads
```

Example 3 — Go goroutines:

```go
// 100,000 goroutines — each much lighter than OS thread
package main
import (
    "fmt"
    "sync"
)

func main() {
    var wg sync.WaitGroup
    for i := 0; i < 100_000; i++ {
        wg.Add(1)
        go func(id int) {  // goroutine: ~4 KB initial stack
            defer wg.Done()
            // simulate I/O: time.Sleep(100 * time.Millisecond)
            fmt.Printf("goroutine %d\n", id)
        }(i)
    }
    wg.Wait()
}
// Go scheduler multiplexes on GOMAXPROCS OS threads
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Fibers run in parallel like OS threads | Fibers multiplexed on one OS thread run concurrently (interleaved) but not in parallel. True parallelism requires fibers multiplexed on multiple OS threads (M:N model). |
| Cooperative scheduling means fibers are safer than threads | Cooperative scheduling reduces the NEED for synchronisation between fibers that yield at well-defined points. But fibers sharing state that's not protected by yield points still have race conditions. |
| Java Virtual Threads are Kotlin Coroutines | They solve the same problem differently. VTs are JVM-managed fibers that work with existing blocking Java code. Kotlin Coroutines require explicit `suspend` annotations and structured concurrency. |
| Fibers are always faster than OS threads | For CPU-bound workloads with no blocking, OS threads with preemptive scheduling are at least as fast and prevent one thread from starving others. |
| Go goroutines are OS threads | Goroutines are user-space coroutines scheduled by the Go runtime's M:N scheduler, not directly by the OS. A machine may run 100k goroutines on 8 OS threads. |

### 🔥 Pitfalls in Production

**1. CPU-Bound Work Monopolising a Carrier Thread (VT Pinning)**

```java
// BAD: CPU-heavy task on virtual thread blocks carrier
Thread.ofVirtual().start(() -> {
    // Tight CPU loop — never yields voluntarily
    while (true) computePi(10_000_000); // monopolises carrier!
});

// GOOD: CPU work belongs on platform threads
ExecutorService cpuPool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors());
cpuPool.submit(() -> computePi(10_000_000));
```

**2. Mixing Blocking and Async in Coroutines**

```kotlin
// BAD: Calling blocking IO from a coroutine on Dispatchers.Default
launch(Dispatchers.Default) {  // CPU-bound dispatcher
    Thread.sleep(1000)  // BLOCKS the thread! monopolises it
}

// GOOD: Use Dispatchers.IO for blocking calls
launch(Dispatchers.IO) {
    Thread.sleep(1000)  // delegates to IO pool; OK
}
// Or: use suspending version
launch {
    delay(1000)  // suspending: releases thread
}
```

**3. Shared Mutable State Between Coroutines**

```kotlin
// BAD: unsynchronised shared state between coroutines
var counter = 0
val jobs = (1..1000).map {
    launch { counter++ } // NOT atomic; data race!
}
jobs.forEach { it.join() }
println(counter) // Not 1000!

// GOOD: Use atomic or channel-based communication
val counter = AtomicInteger(0)
val jobs = (1..1000).map { launch { counter.incrementAndGet() } }
```

### 🔗 Related Keywords

- `Thread (OS)` — the kernel-managed preemptive alternative fibers aim to replace.
- `Virtual Threads (Project Loom)` — Java 21's implementation of JVM-managed fibers.
- `Continuation` — the mechanism that saves/restores fiber execution state.
- `Concurrency vs Parallelism` — fibers enable massive concurrency; parallelism requires multiple carriers.
- `Reactive Programming` — the async callback-based alternative that fibers make unnecessary.
- `Context Switch` — fibers have user-space context switches; far cheaper than OS thread switches.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ User-space mini-threads: cooperatively    │
│              │ yield, ~KB stack, millions possible.      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Massive I/O concurrency (thousands of     │
│              │ simultaneous connections/requests/streams)│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ CPU-bound work → use OS thread pool;      │
│              │ need preemptive fairness guarantees.      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fiber: the cooperative driver who pulls  │
│              │ over voluntarily — not the one being      │
│              │ stopped by traffic police."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Virtual Threads → Continuation → Context  │
│              │ Switch → Concurrency vs Parallelism       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Go's goroutine scheduler (runtime) uses a work-stealing algorithm where each OS thread (M) has a local run queue, and idle OS threads "steal" goroutines from busy threads' queues. Explain how work-stealing improves CPU utilisation compared to a single global FIFO run queue — specifically, how it reduces contention at the scheduler level. Then describe what happens when all goroutines are blocked on channel operations (none in any run queue) and how the scheduler detects this deadlock condition.

**Q2.** Python's asyncio uses a single-threaded event loop with cooperative coroutines. A developer calls a CPU-intensive function (e.g., bcrypt password hashing taking 200ms) directly inside an `async def` coroutine without `await`. Trace the effect of this on all other coroutines in the event loop during those 200ms, explain why this does NOT occur with Java Virtual Threads running the same CPU operation (without any `await`-equivalent), and describe what Python developers must do to prevent this blocking — and why the Java VT model is architecturally superior for this case.

