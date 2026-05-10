---
id: JCC-004
title: Concurrency vs Parallelism in Java
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★☆☆
depends_on: JCC-001
used_by: JCC-005, JCC-048, JCC-049, JCC-066
related: JCC-001, JCC-003, JCC-005
tags:
  - java
  - concurrency
  - foundational
  - mental-model
  - performance
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /jcc/concurrency-vs-parallelism-in-java/
---

# JCC-004 - Concurrency vs Parallelism in Java

⚡ TL;DR - Concurrency is about managing multiple tasks that can overlap in time; parallelism is about executing multiple tasks simultaneously on multiple CPU cores - they are different problems requiring different Java tools.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | JCC-001                            |     |
| **Used by:**    | JCC-005, JCC-048, JCC-049, JCC-066 |     |
| **Related:**    | JCC-001, JCC-003, JCC-005          |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer says "I need better performance, so I'll add more threads." They add 50 threads to a CPU-bound computation. The machine has 8 cores. Performance degrades - more context switching, more memory pressure, no improvement in CPU utilization. They added concurrency (multiple threads) but did not add parallelism (actual simultaneous CPU execution). The wrong tool for the wrong problem.

**THE BREAKING POINT:**
Another developer hears "use reactive programming for performance" and rewrites a database service using `CompletableFuture` chains, targeting I/O performance. The database queries are actually CPU-intensive transformations. The reactive rewrite adds complexity with no benefit because the bottleneck is CPU, not thread blocking. They confused the concurrency problem (thread utilization) with the parallelism problem (CPU saturation).

**THE INVENTION MOMENT:**
Rob Pike's definition (from Go's design documentation) is now standard: _"Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once."_ Java provides different tools for each: `ExecutorService` and Virtual Threads for concurrency (managing overlapping I/O-bound tasks), `ForkJoinPool` and parallel streams for parallelism (splitting CPU-bound computation across cores).

**EVOLUTION:**
Java 7 introduced `ForkJoinPool` specifically for parallel computation (work-stealing for CPU-bound divide-and-conquer). Java 8 added parallel streams built on `ForkJoinPool`. Java 21 Virtual Threads are a concurrency tool (for I/O-bound tasks), not a parallelism tool (they do not add CPU cores).

---

### 📘 Textbook Definition

**Concurrency** is a program structure property: a program is concurrent if it has multiple tasks that can be in progress at the same time, regardless of whether they physically execute simultaneously. Concurrent tasks may interleave on a single core via time-slicing.

**Parallelism** is an execution property: a computation is parallel if it physically executes multiple sub-computations simultaneously on multiple CPU cores at the same time.

The key distinction: concurrency is a design choice (how you structure the program); parallelism is a hardware capability (how many cores you have). Concurrency enables parallelism, but concurrency does not require parallelism.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Concurrency = multiple tasks overlapping in time; parallelism = multiple tasks running at the same instant.

**One analogy:**

> A restaurant kitchen: One chef can cook multiple dishes concurrently by switching between them (concurrency without parallelism - one CPU core). Two chefs can each cook their own dish simultaneously (parallelism - two CPU cores). A restaurant with 2 chefs each cooking 3 dishes is both concurrent and parallel.

**One insight:**
Concurrency is about **structure and coordination** - it deals with I/O waits, async events, and task interleaving. Parallelism is about **throughput** - it splits CPU work across cores. Wrong tool for wrong problem: threads for I/O waste memory; parallel streams for I/O add overhead without benefit.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Concurrency requires at least two tasks that can be in an incomplete state simultaneously** - there is no requirement for a second CPU core.
2. **Parallelism requires at least two CPU cores (or hardware execution units) that are simultaneously active**.
3. **I/O-bound work benefits from concurrency** - while a thread waits for I/O, another thread can use the CPU. More threads than cores is fine because threads spend most time waiting.
4. **CPU-bound work benefits from parallelism** - splitting computation across N cores gives up to N× speedup (limited by Amdahl's Law).
5. **Amdahl's Law:** Speedup from parallelism is limited by the fraction of work that cannot be parallelized. If 10% of work is serial, max speedup is 10× regardless of core count.

**DERIVED DESIGN:**
Given invariant 3: for a web service making 100 concurrent database calls, use a thread pool (or Virtual Threads) sized to the I/O concurrency needed, not to the CPU core count. 200 Virtual Threads waiting on DB is fine; 200 CPU-bound threads on an 8-core machine is harmful.

Given invariant 4 and 5: for a sorting algorithm on a 16-core machine, use `ForkJoinPool` to divide the array into 16 sub-arrays and sort in parallel. Adding 200 threads does not help because the work is CPU-bound and adding threads beyond core count only adds switching overhead.

**THE TRADE-OFFS:**
**Gain:** Choosing the right model (concurrency vs. parallelism) gives maximum performance with minimum resource cost.
**Cost:** Mixing the two models (e.g., parallel streams for I/O-bound work) introduces hidden thread pool contention and degraded performance.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Both I/O-bound and CPU-bound workloads exist. They fundamentally require different execution strategies.
**Accidental:** The Java ecosystem often conflates the two, leading to "add threads for performance" cargo-culting that hurts rather than helps.

---

### 🧪 Thought Experiment

**SETUP:**
You have two services: Service A fetches user profiles from 100 different microservices. Service B sorts a list of 10 million integers.

**WHAT HAPPENS IF YOU APPLY THE WRONG TOOL TO EACH:**
Service A with parallel streams (`stream().parallel().map(this::fetchProfile)`): parallel streams use the common `ForkJoinPool` (default size = CPU cores, e.g., 8). All 100 fetches are I/O-bound and block. You have 8 threads blocking on network I/O instead of 100 threads blocking (92 fetches run sequentially). Slower than a simple loop with Virtual Threads.

Service B with 200 Virtual Threads: each Virtual Thread gets a tiny slice of sorting work. Sorting is CPU-bound and never blocks. Virtual Threads schedule cooperatively (on blocking I/O); for CPU-bound work, they behave like regular threads. 200 Virtual Threads on 8 cores = 192 threads context-switching uselessly. Worse than a `ForkJoinPool` with 8 threads.

**WHAT HAPPENS WITH THE RIGHT TOOL:**
Service A with Virtual Threads (`Executors.newVirtualThreadPerTaskExecutor()`): 100 Virtual Threads, each blocking on a different network call. Carrier threads (8 total) are reused whenever a Virtual Thread blocks. All 100 fetches run concurrently. Maximum I/O utilization.

Service B with `ForkJoinPool` parallel sort (`Arrays.parallelSort()`): 8 threads (one per core), each sorting a partition. CPU is 100% utilized. No wasted context switching. Near-optimal throughput.

**THE INSIGHT:**
"More threads" is not the same as "more performance." The right question is: "Is my bottleneck I/O wait (use concurrency) or CPU capacity (use parallelism)?"

---

### 🧠 Mental Model / Analogy

> A chef multitasking (concurrency) vs. a kitchen brigade of specialized chefs working in parallel (parallelism). One chef can start boiling pasta, then chop vegetables while the pasta boils, then plate while the vegetables cook. This is concurrency - one CPU, multiple tasks in progress. A kitchen brigade has a saucier, a pastry chef, and a garde-manger all working simultaneously on different dishes. This is parallelism - multiple CPUs, simultaneous work.

Element mapping:

- **One chef** = single CPU core
- **Multiple dishes in progress** = concurrent tasks
- **Switching between dishes** = context switching
- **Kitchen brigade** = multiple CPU cores
- **Each chef on their own dish simultaneously** = parallel execution
- **Head chef coordinating** = the Java scheduler / `ForkJoinPool` work-stealing

Where this analogy breaks down: in a kitchen, switching between dishes takes time but is voluntary. In a CPU, context switching happens involuntarily (OS preemption) and has a fixed overhead.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Concurrency is like a person juggling - they handle multiple balls, but only touch one at a time. Parallelism is like two people each juggling their own balls - both are working simultaneously. Juggling more balls does not make you faster; having a second person does.

**Level 2 - How to use it (junior developer):**
For I/O-bound work (database, HTTP, file): use concurrency tools - thread pools, Virtual Threads, `CompletableFuture`. For CPU-bound work (computation, sorting, transforms): use parallelism tools - `ForkJoinPool`, `Arrays.parallelSort()`, parallel streams. Do not mix: avoid parallel streams for database calls; avoid Virtual Threads for pure computation.

**Level 3 - How it works (mid-level engineer):**
I/O-bound concurrency: a thread blocks on I/O, releasing the CPU. Other threads fill that CPU time. N threads > N cores is fine because most threads are blocked, not running. Virtual Threads make this cheap at scale.
CPU-bound parallelism: a thread uses the CPU 100% of its time slice. N threads > N cores causes context switching overhead. Optimal thread count = core count (or core count × 1-2 for hyperthreading). `ForkJoinPool` auto-sizes to core count.

**Level 4 - Why it was designed this way (senior/staff):**
`ForkJoinPool` uses **work-stealing** - idle threads steal tasks from busy threads' queues. This is optimal for divide-and-conquer parallelism: the task graph is irregular (some subtasks are larger), and work-stealing automatically balances load without central coordination. An `ExecutorService` with a fixed pool and `BlockingQueue` is better for concurrency: task ordering, fairness, and bounded queuing matter more than work-stealing for I/O-bound tasks.

**Expert Thinking Cues:**

- "What is the bottleneck: CPU or I/O?"
- "How much of the work can be parallelized? What does Amdahl's Law say about the expected speedup?"
- "Am I putting I/O-bound tasks into a CPU-sized thread pool (bad) or a concurrency-sized pool (good)?"

---

### ⚙️ How It Works (Mechanism)

**CONCURRENCY MECHANISM (I/O-bound):**

```
Thread 1: ──[CPU work]──[blocking I/O wait]──[CPU work]──►
Thread 2: ──────────────[CPU work]──[I/O wait]──[CPU]──►
Thread 3: ──────────────────────────[CPU work]──────────►

CPU core: [T1 CPU][T2 CPU][T3 CPU][T1 CPU][T2 CPU][T3 CPU]
```

Multiple threads share the CPU. While T1 waits on I/O, T2 and T3 use the CPU. The CPU is never idle. More threads than cores is acceptable because most threads wait.

**PARALLELISM MECHANISM (CPU-bound):**

```
Core 1: [Task A partition 1]──────────────────────►
Core 2: [Task A partition 2]──────────────────────►
Core 3: [Task A partition 3]──────────────────────►
Core 4: [Task A partition 4]──────────────────────►
```

Multiple cores execute different partitions of the same computation simultaneously. Each core is 100% utilized. Adding more threads than cores adds overhead without adding throughput.

**JAVA TOOL MAPPING:**

| Workload              | Java Tool                        | Why                                      |
| --------------------- | -------------------------------- | ---------------------------------------- |
| I/O-bound concurrency | Virtual Threads, ExecutorService | Cheap blocking, many tasks               |
| CPU-bound parallelism | ForkJoinPool, parallel streams   | Work-stealing, core-count threads        |
| Mixed (I/O + CPU)     | Separate pools                   | Don't share; each needs different sizing |
| Async composition     | CompletableFuture                | Non-blocking chaining of I/O results     |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (picking the right tool):**

```
Task analysis
    │
    ▼
Is task I/O-bound (network, DB, file)?
  ──YES──► Concurrency tools:
  │         - Java 21+: Virtual Threads
  │         - Java 8-20: CompletableFuture / bounded pool
  │
  ▼
Is task CPU-bound (computation)?       ← YOU ARE HERE
  ──YES──► Parallelism tools:
            - ForkJoinPool
            - Arrays.parallelSort()
            - parallel streams
            (thread count = CPU cores)
```

**FAILURE PATH:**
Using parallel streams for I/O: the common `ForkJoinPool` (default = CPU core count) starves legitimate CPU-parallel work because its threads are blocked waiting on I/O. This is a hidden cross-task performance dependency.

**WHAT CHANGES AT SCALE:**
At scale (cloud deployments), CPU core count per container may be 2-4. Parallelism gains from `ForkJoinPool` are limited by core count. Over-threading (dozens of parallel threads on a 2-core container) hurts performance. Profiling and right-sizing are essential.

---

### ⚖️ Comparison Table

| Dimension            | Concurrency                      | Parallelism                    |
| -------------------- | -------------------------------- | ------------------------------ |
| Goal                 | Task interleaving, I/O overlap   | Simultaneous CPU execution     |
| Bottleneck           | I/O wait time                    | CPU capacity                   |
| Optimal thread count | >> CPU cores (mostly waiting)    | = CPU cores (all running)      |
| Java tools           | Virtual Threads, ExecutorService | ForkJoinPool, parallel streams |
| Speedup model        | More tasks per unit time         | Faster per-task completion     |
| Coordination         | Synchronization of shared state  | Data partitioning + merge      |
| Failure mode         | Thread starvation, deadlock      | Amdahl's Law plateau           |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "More threads always means more performance"              | CPU-bound work: adding threads beyond core count adds context-switching overhead. I/O-bound work: adding threads is fine until memory or I/O saturation.                                                                                                               |
| "Parallel streams are always faster than sequential"      | Parallel streams have overhead (task splitting, merging, coordination). For small collections or simple operations, sequential is faster. Parallel shines for large, CPU-bound, embarrassingly parallel work.                                                          |
| "Virtual Threads are a parallelism tool"                  | Virtual Threads are a concurrency tool. They make I/O-bound blocking cheap. They do not add CPU cores. For CPU-bound work, use `ForkJoinPool`.                                                                                                                         |
| "Concurrency and parallelism mean the same thing"         | Concurrency = overlapping tasks (possible on 1 core). Parallelism = simultaneous tasks (requires multiple cores). They are related but distinct properties.                                                                                                            |
| "Reactive/async frameworks are faster than blocking code" | Async frameworks provide concurrency (non-blocking I/O). On a single core, they are not faster - just more memory-efficient. On multi-core systems, they enable better I/O concurrency. Java 21 Virtual Threads provide equivalent I/O concurrency with blocking code. |
| "ForkJoinPool is the best thread pool for all workloads"  | ForkJoinPool is optimized for CPU-bound recursive tasks (work-stealing, locality). For I/O-bound tasks, a standard `ThreadPoolExecutor` with bounded queue is more appropriate.                                                                                        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Parallel Streams for I/O**
**Symptom:** Parallel stream over a collection of URLs or DB queries runs slower than sequential stream. CPU utilization is low. Threads are blocked.
**Root Cause:** Parallel streams use the common `ForkJoinPool` sized to CPU core count. I/O-bound tasks block threads, reducing parallelism to near-zero.
**Diagnostic:**

```bash
# Profile thread states during parallel stream execution
jstack <pid> | grep -A5 "ForkJoinPool.commonPool"
# Most threads should be BLOCKED (wrong for this use case)
```

**Fix:**

```java
// BAD: parallel stream for I/O-bound tasks
urls.parallelStream()
    .map(url -> httpClient.fetch(url)) // blocks FJP threads
    .collect(toList());

// GOOD: Virtual Threads for I/O-bound concurrency
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    var futures = urls.stream()
        .map(url -> exec.submit(() -> httpClient.fetch(url)))
        .toList();
    return futures.stream().map(Future::get).toList();
}
```

**Prevention:** Never use parallel streams for I/O operations. Use Virtual Threads or `CompletableFuture` with a dedicated I/O executor.

---

**Failure Mode 2: CPU-Bound Work in Virtual Thread Pool**
**Symptom:** CPU-bound computation is not faster with Virtual Threads than with a single thread.
**Root Cause:** Virtual Threads do not add CPU execution capacity. CPU-bound work consumes the carrier thread without ever unmounting. You have M virtual threads competing for N carrier threads - no improvement over N threads.
**Diagnostic:**

```bash
# Check carrier thread count (should equal CPU cores for CPU-bound work)
jstack <pid> | grep "ForkJoinPool\|carrier"
# If virtual thread count >> carrier thread count for CPU work, it's over-threaded
```

**Fix:**

```java
// BAD: Virtual Threads for CPU-bound parallel sort
var tasks = partitions.stream()
    .map(p -> Thread.ofVirtual().start(() -> sort(p)))
    .toList();
// Virtual Threads don't help; carrier threads = CPU cores already

// GOOD: ForkJoinPool for CPU-bound parallel sort
ForkJoinPool.commonPool().submit(
    () -> partitions.parallelStream().forEach(p -> sort(p))
).join();
```

**Prevention:** Profile first. If CPU is the bottleneck, use `ForkJoinPool` or parallel streams. If I/O is the bottleneck, use Virtual Threads.

---

**Failure Mode 3: Shared ForkJoinPool Starvation**
**Symptom:** Application-wide slowdown when a feature using parallel streams is added. Other async operations slow down mysteriously.
**Root Cause:** Parallel streams and `CompletableFuture.supplyAsync()` (without custom executor) both use the common `ForkJoinPool`. Blocking or slow tasks in one feature starve the other.
**Diagnostic:**

```bash
# Thread dump shows common pool threads blocked
jstack <pid> | grep -B2 -A10 "ForkJoinPool.commonPool-worker"
```

**Fix:**

```java
// BAD: uses common ForkJoinPool - affects all parallel operations
List<Result> results = items.parallelStream()
    .map(this::expensiveOp)
    .toList();

// GOOD: dedicated ForkJoinPool isolates work
ForkJoinPool customPool = new ForkJoinPool(4);
List<Result> results = customPool.submit(
    () -> items.parallelStream().map(this::expensiveOp).toList()
).get();
```

**Prevention:** Use custom `ForkJoinPool` instances for parallel work to isolate from the common pool used by `CompletableFuture`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-001 - Why Concurrency Is Hard]] - the root problems
- [[JCC-003 - Java Concurrency Approach -- History and Philosophy]] - why different tools were created

**Builds On This (learn these next):**

- [[JCC-048 - ForkJoinPool]] - the primary Java parallelism tool
- [[JCC-049 - Virtual Threads (Project Loom)]] - the primary Java concurrency tool (Java 21+)
- [[JCC-005 - The Java Concurrency Ecosystem Map]] - all tools mapped to their use cases

**Alternatives / Comparisons:**

- [[JCC-066 - Concurrent System Design at Scale]] - applying this distinction at system design level
- [[JCC-017 - ExecutorService]] - the I/O concurrency workhorse

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Two distinct performance problems   │
│ PROBLEM       │ Wrong tool = worse performance      │
│ KEY INSIGHT   │ I/O-bound→concurrency; CPU→parallel │
│ USE WHEN      │ Choosing any concurrency approach   │
│ AVOID WHEN    │ N/A - a mental model, not a tool    │
│ TRADE-OFF     │ Thread count vs. CPU utilization    │
│ ONE-LINER     │ Concurrent = overlapping; parallel  │
│               │ = simultaneous                      │
│ NEXT EXPLORE  │ JCC-048 ForkJoinPool, JCC-049 VT    │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Concurrency = overlapping tasks in time (good for I/O-bound work).
2. Parallelism = simultaneous execution on multiple cores (good for CPU-bound work).
3. Virtual Threads = concurrency tool; `ForkJoinPool` = parallelism tool. Do not swap them.

**Interview one-liner:**
"Concurrency is about managing overlapping I/O-bound tasks (use Virtual Threads, thread pools); parallelism is about splitting CPU-bound computation across cores (use ForkJoinPool, parallel streams). Using the wrong model degrades performance."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Always profile before optimizing. A performance problem is either bottlenecked on I/O wait (add concurrency) or on CPU capacity (add parallelism). Adding threads to the wrong bottleneck makes things worse, not better.

**Where else this pattern appears:**

- **Node.js event loop:** Node.js is highly concurrent (single-threaded event loop handles thousands of I/O-bound connections) but not parallel (single-threaded CPU execution). Worker threads add parallelism for CPU-bound work. Same distinction as Java.
- **Database query optimization:** A query can be parallelized across CPU cores (parallel query execution plans) or made concurrent with other queries (connection pool management). DBAs tune each independently.
- **OS scheduler:** The OS runs processes concurrently (time-slicing on single core) and in parallel (multiple cores). Knowing which mode a process uses helps with tuning CPU affinity and scheduler priority.

---

### 💡 The Surprising Truth

Amdahl's Law reveals a counterintuitive limit on parallelism: if only 5% of your program is inherently sequential (cannot be parallelized), the maximum possible speedup from any number of cores is 20× - no matter how many cores you add. A program that is 50% serial has a maximum speedup of 2× regardless of having 1,000 cores. This means that for most real-world Java applications (which have serialized I/O, locking, and startup), the practical gains from parallelism are far smaller than expected - and the I/O concurrency problem (Virtual Threads, async) has a much larger performance impact than CPU parallelism.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** A program is 90% parallelizable. You add 10 CPU cores. By Amdahl's Law, what is the maximum speedup? What happens when you add 100 cores? What does this tell you about where to focus performance investment?
_Hint:_ Apply the Amdahl formula: Speedup = 1 / (S + (1-S)/N) where S = serial fraction, N = cores.

**Q2 (A - System Interaction):** A Spring Boot application has a `@Scheduled` task running on the `ForkJoinPool.commonPool()`. A developer adds `parallelStream()` processing that uses the same common pool. What is the failure mode? How would you isolate the two workloads?
_Hint:_ Consider what happens when the common pool is saturated by the parallel stream while the scheduled task is waiting for a worker.

**Q3 (C - Design Trade-off):** You are designing a data pipeline that reads 10,000 files, processes each (CPU-heavy transformation), and writes results. What is the optimal thread model? Should you use one pool or two? What happens if reads are slow (network filesystem) vs. fast (local SSD)?
_Hint:_ Consider separating the I/O-bound read phase (concurrency) from the CPU-bound transform phase (parallelism) into a producer-consumer pattern with a `BlockingQueue`.
