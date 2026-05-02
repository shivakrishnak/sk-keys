---
layout: default
title: "ForkJoinPool"
parent: "Java Concurrency"
nav_order: 352
permalink: /java-concurrency/fork-join-pool/
number: "0352"
category: Java Concurrency
difficulty: ★★★
depends_on: ExecutorService, ThreadPoolExecutor, Callable
used_by: Stream API, CompletableFuture, Virtual Threads (Project Loom)
related: ThreadPoolExecutor, ExecutorService, RecursiveTask
tags:
  - java
  - concurrency
  - fork-join
  - deep-dive
  - parallel
---

# 0352 — ForkJoinPool

⚡ TL;DR — `ForkJoinPool` uses **work-stealing**: each worker thread has its own deque of tasks; idle threads steal tasks from busy threads' deques — enabling efficient divide-and-conquer parallelism where tasks split into subtasks without the coordinator blocking.

| #0352 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ExecutorService, ThreadPoolExecutor, Callable | |
| **Used by:** | Stream API, CompletableFuture, Virtual Threads (Project Loom) | |
| **Related:** | ThreadPoolExecutor, ExecutorService, RecursiveTask | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Divide-and-conquer algorithms split a problem into independent subtasks and combine results. With `ThreadPoolExecutor`, a coordinator thread submits subtasks and calls `future.get()` — blocking itself while waiting. A divide-into-8 problem: coordinator blocked waiting for each level, pool threads working. The blocked coordinator wastes a thread and reduces effective concurrency.

**THE BREAKING POINT:**
A merge sort of 10M elements with 8 CPU cores. With `ThreadPoolExecutor(8)`: the coordinator thread splits, submits, and blocks (waiting) — effectively using threads as waiting threads, not working threads. Actual parallelism < 8 because blocked threads don't work. Only the leaf-level tasks use all 8 cores simultaneously.

**THE INVENTION MOMENT:**
**`ForkJoinPool`** was created for exactly this pattern — it allows blocked threads (waiting for subtasks) to pick up other available work instead of truly blocking — maximising CPU utilisation for divide-and-conquer workloads.

---

### 📘 Textbook Definition

**`ForkJoinPool`** is a `ExecutorService` implementation specialised for divide-and-conquer (fork-join) parallel algorithms. It uses **work-stealing**: each worker thread has its own `ArrayDeque` of tasks; when idle, threads steal tasks from the tail of other workers' deques. Tasks are defined as `RecursiveTask<V>` (returns a value) or `RecursiveAction` (no return) and use `fork()` (submit subtask) + `join()` (wait for subtask) in an efficient non-blocking manner. `ForkJoinPool.commonPool()` is a JVM-wide shared pool used by parallel streams and `CompletableFuture.supplyAsync()` (no executor arg).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`ForkJoinPool` is a pool where idle threads steal work from busy ones — keeping CPUs busy during divide-and-conquer without blocking the coordinator.

**One analogy:**
> A restaurant where idle waiters help busy ones. Each waiter has their own order queue. When a waiter has no orders (idle), they take from the END of the busiest waiter's queue (steal). No waiter sits idle — there's always work to steal. Coordinators who "wait" for prep rooms to finish don't truly wait — they pick up other orders in the meantime.

**One insight:**
Work-stealing reduces contention vs. a single shared queue: each thread works from its own deque nose (LIFO), while stealers take from the tail (FIFO). This keeps cache-warm tasks with the thread that created them, while stealers get older tasks with less contention.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each worker has a private `ArrayDeque` — NO contention between workers doing their own work.
2. Stealing is from the TAIL (oldest task) — the thief's access pattern differs from the owner's, minimising lock contention on the deque.
3. `fork()` + `join()` in a task triggers the worker to pick up other available work instead of blocking during `join()`.

**DERIVED DESIGN:**
The work-stealing mechanism:
```
Worker T1's deque (LIFO for owner, FIFO for stealers):
  [New task] → Owner T1 pushes/pops here (head)
  [Old task] → Stealers take from here (tail)

When T1 calls join(subtask) and subtask is not done:
  → T1's thread tries to execute pending tasks from its deque
  → If deque empty, T1 scans other workers' deques to steal
  → T1 stays active (CPU used) while "waiting"
  → T1 resumes join() when subtask completes
```

This is different from a regular ThreadPoolExecutor where `future.get()` truly parks the thread doing nothing.

**THE TRADE-OFFS:**
**Gain:** High CPU utilisation for recursive divide-and-conquer; no blocked waiting threads; efficient for parallel streams.
**Cost:** Overhead of deque management and stealing; JVM-wide common pool shared by all parallel streams + CompletableFuture; blocking I/O in common pool tasks is catastrophic; not ideal for simple task queues (use ThreadPoolExecutor instead).

---

### 🧪 Thought Experiment

**SETUP:**
Sum an array of 1M integers in parallel.

WITH ThreadPoolExecutor (inefficient):
```java
// Coordinator submits two halves, then blocks waiting
Future<Long> f1 = pool.submit(() -> sum(arr, 0, 500_000));
Future<Long> f2 = pool.submit(() -> sum(arr, 500_000, 1_000_000));
long result = f1.get() + f2.get(); // coordinator blocks
// If coordinator is a pool thread: wasted thread
```

WITH ForkJoinPool (efficient):
```java
class SumTask extends RecursiveTask<Long> {
    static final int THRESHOLD = 10_000;
    final long[] arr; final int lo, hi;

    protected Long compute() {
        if (hi - lo <= THRESHOLD) {
            return sumSequential(arr, lo, hi); // base case
        }
        int mid = (lo + hi) / 2;
        SumTask left  = new SumTask(arr, lo, mid);
        SumTask right = new SumTask(arr, mid, hi);
        left.fork();                // async — submits to deque
        Long rightResult = right.compute(); // run right inline
        Long leftResult  = left.join();     // wait; steal work in meantime
        return leftResult + rightResult;
    }
}
long result = ForkJoinPool.commonPool()
    .invoke(new SumTask(arr, 0, arr.length));
```

**THE INSIGHT:**
`right.compute()` runs inline (no fork overhead for last subtask). `left.fork()` + `left.join()` allows the worker to pick up other tasks during join — no wasted blocking.

---

### 🧠 Mental Model / Analogy

> ForkJoinPool is like a construction crew with a critical-path work policy. Foreman (coordinator) divides blueprint into tasks (fork), each worker takes a task. When someone finishes early (idle), they look around — the slowest team has leftover tasks — they pick one up (steal) without coordination overhead. No worker ever stands idle as long as work exists.

- "Foreman divides blueprint" → `RecursiveTask.fork()`.
- "Picking up another team's leftover tasks" → work-stealing.
- "All workers contributing" → work-stealing prevents idle CPU cores.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** ForkJoinPool keeps all CPU cores busy during divide-and-conquer by having idle threads steal work from busy ones.

**Level 2:** Use `RecursiveTask<V>` (returns value) or `RecursiveAction` (void) with a threshold for the sequential base case. Submit with `pool.invoke(task)`. Use `commonPool()` for parallel streams. Use a dedicated `ForkJoinPool` for CPU-bound work that shouldn't compete with streams.

**Level 3:** `ForkJoinPool` uses `WorkQueue[]` array — even indices are submission queues, odd indices are worker queues. Each worker has its own index. Stealing: random victim selection with SpinWait; deque access via `Unsafe.compareAndExchangeObject`. `join()` uses `doJoin()` which calls `pollAndExecCC()` — either runs a stolen continuation or `wait()` on the FJ task.

**Level 4:** Java 21's virtual threads use `ForkJoinPool` as the carrier thread pool. Virtual thread `park()` unmounts from the carrier (FJ worker) and the worker picks up another virtual thread — the same work-stealing principle applied to coroutine scheduling. This is why blocking I/O in virtual threads is efficient: the FJ carrier doesn't block, just unmounts the virtual thread and runs another.

---

### ⚙️ How It Works (Mechanism)

**RecursiveTask for divide-and-conquer:**
```java
class ParallelMergeSort extends RecursiveAction {
    private final int[] arr;
    private final int lo, hi;
    private static final int THRESHOLD = 1000;

    protected void compute() {
        if (hi - lo <= THRESHOLD) {
            Arrays.sort(arr, lo, hi); // sequential base case
            return;
        }
        int mid = (lo + hi) / 2;
        ParallelMergeSort left  = new ParallelMergeSort(arr, lo, mid);
        ParallelMergeSort right = new ParallelMergeSort(arr, mid, hi);
        invokeAll(left, right); // fork both, join both
        merge(arr, lo, mid, hi);
    }
}

ForkJoinPool pool = new ForkJoinPool(
    Runtime.getRuntime().availableProcessors()
);
pool.invoke(new ParallelMergeSort(arr, 0, arr.length));
```

**commonPool vs. dedicated pool:**
```java
// commonPool: shared by parallel streams, CompletableFuture
ForkJoinPool.commonPool().invoke(task);

// Dedicated pool: isolated from stream interference
ForkJoinPool customPool = new ForkJoinPool(
    4, // parallelism
    ForkJoinPool.defaultForkJoinWorkerThreadFactory,
    null, // uncaught exception handler
    true  // asyncMode = FIFO (for event-driven tasks)
);
customPool.invoke(task);
// OR: force parallel stream to use custom pool:
customPool.submit(
    () -> largeList.parallelStream().map(fn).collect(toList())
).join();
```

**Pitfall: blocking I/O in commonPool:**
```java
// BAD: HTTP call in parallel stream uses commonPool
largeList.parallelStream()
    .map(item -> httpClient.get(item.url)) // blocks commonPool thread!
    .collect(toList());
// Blocks all FJ workers → parallel streams JVM-wide degrade

// GOOD: dedicated pool or virtual threads
customPool.submit(
    () -> largeList.parallelStream()
                   .map(item -> httpClient.get(item.url))
                   .collect(toList())
).join();
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
[pool.invoke(SumTask(0, 1M))]
    → [Worker T1: compute() — range > threshold, fork]  ← YOU ARE HERE
    → [T1 pushes left half to own deque, runs right half]
    → [T2 (idle): steals left half from T1's deque]
    → [T1: right.compute() returns, join() left]
    → [join(): T1 checks if left done — not yet]
    → [T1: works on own deque or steals other tasks]
    → [T2: left half completes]
    → [T1: join() returns left result]
    → [T1: combines left + right → result to parent]
```

**WHAT CHANGES AT SCALE:**
ForkJoinPool parallelism should equal available CPU cores for CPU-bound work. For tasks below `THRESHOLD`, sequential is faster (spawn overhead > parallelism gain). Tune threshold: too small = too many fork() calls, too large = too little parallelism.

---

### 💻 Code Example

```java
// When to use parallelStream vs explicit ForkJoinPool:

// OK: CPU-bound, stateless — use commonPool via parallelStream
long sum = largeNumbers.parallelStream()
    .mapToLong(n -> n * n) // pure CPU
    .sum();

// NECESSARY: CPU-bound but isolated from app-wide commonPool
ForkJoinPool isolated = new ForkJoinPool(4);
long result = isolated.submit(
    () -> largeNumbers.parallelStream()
                      .mapToLong(n -> expensiveCompute(n))
                      .sum()
).join();
isolated.shutdown();

// AVOID: I/O in parallel streams (blocks FJ workers)
// Use CompletableFuture with dedicated executor instead
```

---

### ⚖️ Comparison Table

| Pool Type | Best For | Blocking I/O | Overhead | Stealing |
|---|---|---|---|---|
| `ThreadPoolExecutor` | General tasks, I/O | Fine | Low | No |
| **`ForkJoinPool`** | Divide-and-conquer, CPU | Avoid in commonPool | Medium | Yes |
| `VirtualThreadExecutor` | High-concurrency I/O | Fine | Very low | No (FJ-backed) |

How to choose: ForkJoinPool for CPU-bound recursive algorithms and parallel streams. ThreadPoolExecutor for I/O-bound task queues with bounded concurrency. VirtualThreadExecutor for high-concurrency I/O.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ForkJoinPool is always better than ThreadPoolExecutor | For non-recursive, non-CPU-bound work, ThreadPoolExecutor is simpler and appropriate. ForkJoinPool's overhead only pays off for divide-and-conquer with fine-grained tasks |
| commonPool is isolated per application | The JVM shares ONE commonPool across ALL parallel streams and default CompletableFuture calls in the JVM. One blocking operation starves all parallel streams |
| More parallelism = faster in ForkJoinPool | Parallelism > CPU cores causes thread context switching, hurting performance. Set parallelism = CPU cores for CPU-bound work |

---

### 🚨 Failure Modes & Diagnosis

**commonPool starvation from blocking tasks:**
```bash
# Thread dump: all ForkJoinPool workers BLOCKED on I/O
jstack <pid> | grep "ForkJoinPool.commonPool" -A5
```
**Fix:** Use dedicated `ForkJoinPool` for workloads with any blocking I/O.

**Task granularity too fine (threshold too small):**
**Symptom:** Overhead exceeds benefit; poor performance despite parallelism.
**Fix:** Increase threshold. Benchmark with JMH varying threshold sizes.

---

### 🔗 Related Keywords

**Prerequisites:** `ExecutorService`, `RecursiveTask`, `ThreadPoolExecutor`
**Builds on:** Stream API (parallelStream uses commonPool), Virtual Threads
**Related:** `CompletableFuture`, `RecursiveTask`, `RecursiveAction`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Work-stealing thread pool: idle workers   │
│              │ steal tasks from busy workers' queues     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ commonPool is JVM-SHARED — blocking in   │
│              │ parallel streams hurts ALL parallel code. │
│              │ Set parallelism = CPU count for CPU work  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Idle workers steal from busy ones —      │
│              │  maximum CPU use for divide-and-conquer"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Virtual Threads → RecursiveTask           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Using `parallelStream()` inside a Spring `@Transactional` method risks a subtle bug. The parallel stream runs tasks in `ForkJoinPool.commonPool()` threads. Explain why these FJ worker threads do NOT inherit the `@Transactional` context from the calling thread (trace the Spring transaction propagation mechanism using `ThreadLocal`), what happens when FJ worker threads attempt database operations, and describe the exact exception type thrown when the EntityManager is used without an active transaction in the FJ worker context.

**Q2.** `ForkJoinPool.commonPool().getParallelism()` returns `Runtime.getRuntime().availableProcessors() - 1`. Explain: why it's reserved -1 CPU for the submitting thread (the thread that calls `invoke()`), what happens to throughput for a purely recursive computation if the submitter's thread is counted as parallelism (trace a binary tree fork where all leaves are done by pool workers but the root waits — who submits the root?), and what `-Djava.util.concurrent.ForkJoinPool.common.parallelism=N` JVM property allows and why it can be set to a value larger than CPU count for I/O-tolerant workloads.

