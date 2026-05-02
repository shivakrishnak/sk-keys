---
layout: default
title: "ExecutorService"
parent: "Java Concurrency"
nav_order: 350
permalink: /java-concurrency/executor-service/
number: "0350"
category: Java Concurrency
difficulty: ★★☆
depends_on: Executor, Callable, Future, Thread (Java)
used_by: ThreadPoolExecutor, ForkJoinPool, CompletableFuture
related: ThreadPoolExecutor, ForkJoinPool, CompletableFuture
tags:
  - java
  - concurrency
  - thread-pool
  - intermediate
  - executor
---

# 0350 — ExecutorService

⚡ TL;DR — `ExecutorService` extends `Executor` with `submit(Callable)` for typed results, `invokeAll/Any` for batches, and lifecycle management (`shutdown`, `awaitTermination`) — the standard Java interface for managed thread pool usage.

| #0350 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Executor, Callable, Future, Thread (Java) | |
| **Used by:** | ThreadPoolExecutor, ForkJoinPool, CompletableFuture | |
| **Related:** | ThreadPoolExecutor, ForkJoinPool, CompletableFuture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`Executor.execute(Runnable)` has no lifecycle management — you can't shut it down gracefully, wait for in-flight tasks to finish, or retrieve results. Production services need to stop their thread pools on shutdown, wait for pending work to complete, and retrieve typed results from background tasks.

**THE INVENTION MOMENT:**
**`ExecutorService`** adds lifecycle control and result-returning task support to the base `Executor` abstraction — the production-grade thread pool interface.

---

### 📘 Textbook Definition

**`ExecutorService`** extends `Executor` with: `submit(Callable<T>)` — returns `Future<T>`; `submit(Runnable)` — returns `Future<?>`; `invokeAll(List<Callable<T>>)` — submits all, returns all Futures; `invokeAny(List<Callable<T>>)` — returns first completed result; `shutdown()` — orderly shutdown (accepts no new tasks, runs pending); `shutdownNow()` — immediate stop attempt (interrupts running); `awaitTermination(timeout, unit)` — waits for completion after shutdown; `isShutdown()` / `isTerminated()` — state checks. Factory: `Executors` utility class creates standard implementations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`ExecutorService` = thread pool with submit/result/shutdown lifecycle.

**One analogy:**
> A managed staffing agency: you submit jobs (submit), get ticket numbers for results (Future), and when closing for the day, tell the agency to finish current assignments (shutdown + awaitTermination).

**One insight:**
Proper shutdown is critical. An `ExecutorService` without shutdown prevents JVM exit — daemon threads aside. Always call `shutdown()` + `awaitTermination()` on application lifecycle hooks (Spring `@PreDestroy`, try-with-resources with `ExecutorService.close()` in Java 19+).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. After `shutdown()`, no new tasks are accepted; pending tasks complete.
2. `shutdownNow()` tries to interrupt running tasks; returns pending (not-started) task list.
3. `awaitTermination()` blocks until all tasks complete or timeout expires.

**DERIVED DESIGN:**
```java
// Lifecycle management pattern:
ExecutorService service = Executors.newFixedThreadPool(4);
try {
    // submit tasks
    service.submit(task1);
    service.submit(task2);
} finally {
    service.shutdown();                          // accept no more
    service.awaitTermination(30, TimeUnit.SECONDS); // wait for drain
}

// Java 19+: AutoCloseable
try (ExecutorService svc =
        Executors.newVirtualThreadPerTaskExecutor()) {
    svc.submit(task);
} // auto-calls close() = shutdown + awaitTermination
```

Standard factory methods:
```java
Executors.newFixedThreadPool(n)      // n threads, unbounded queue
Executors.newCachedThreadPool()      // grows/shrinks thread count
Executors.newSingleThreadExecutor()  // 1 thread, tasks serialised
Executors.newScheduledThreadPool(n)  // delayed/periodic tasks
Executors.newVirtualThreadPerTaskExecutor() // Java 21 virtual threads
```

**THE TRADE-OFFS:**
**Gain:** Lifecycle management; Future results; batch submit.
**Cost:** Must call shutdown; `FixedThreadPool` with unbounded queue can OOM; `CachedThreadPool` can create unlimited threads.

---

### 🧪 Thought Experiment

**SETUP:** Parallel report generation with results.

```java
ExecutorService pool = Executors.newFixedThreadPool(4);

List<Future<Report>> futures = reportIds.stream()
    .map(id -> pool.submit(() -> generateReport(id)))
    .collect(toList());

// All submitted and running concurrently
List<Report> reports = futures.stream()
    .map(f -> {
        try { return f.get(30, SECONDS); }
        catch (Exception e) { throw new RuntimeException(e); }
    })
    .collect(toList());

pool.shutdown();
pool.awaitTermination(60, SECONDS);
```

**THE INSIGHT:** All submissions happen before any `.get()` call — this ensures concurrent execution. Then results are collected sequentially without reducing throughput.

---

### 🧠 Mental Model / Analogy

> ExecutorService is a staffing agency that accepts job orders (submit), provides order tracking (Future), and has a close-of-business procedure (shutdown + awaitTermination).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A thread pool with a "submit job and get a result ticket" interface, plus "stop accepting jobs" and "wait for finish" lifecycle.

**Level 2:** Use `newFixedThreadPool(n)` for CPU-bound, `newVirtualThreadPerTaskExecutor()` for I/O-bound (Java 21). Always `shutdown()` + `awaitTermination()`. Use `submit(Callable)` for results, `execute(Runnable)` for fire-and-forget.

**Level 3:** `AbstractExecutorService` provides default `submit()` implementations by wrapping Runnables/Callables in `FutureTask`. The concrete `ThreadPoolExecutor` manages a worker queue, core/max thread counts, keep-alive time, and rejection handler.

**Level 4:** `ExecutorService.close()` (Java 19+) follows the `AutoCloseable` pattern — `close() = shutdown() + awaitTermination(Long.MAX_VALUE, NANOSECONDS)`. This enables try-with-resources usage, preventing the common "forgot shutdown" bug and enabling the "scoped structured concurrency" pattern.

---

### ⚙️ How It Works (Mechanism)

```java
// Standard usage:
ExecutorService pool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors()
);

try {
    // Submit callable for result:
    Future<String> future = pool.submit(() -> fetchUser(id));

    // Submit runnable for side effect:
    pool.execute(() -> sendEmail(user));

    // Batch - submit all, get all:
    List<Future<Data>> allFutures = pool.invokeAll(
        List.of(() -> fetchA(), () -> fetchB(), () -> fetchC())
    );

    // Get first result:
    Data fastest = pool.invokeAny(
        List.of(() -> cacheGet(key), () -> dbGet(key))
    );

    String user = future.get(5, SECONDS);
} finally {
    pool.shutdown();
    pool.awaitTermination(30, SECONDS);
}
```

**Java 21 virtual thread executor:**
```java
// Best for I/O-bound workloads: unlimited virtual threads
try (ExecutorService vThreads =
        Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<Response>> futures = requests.stream()
        .map(req -> vThreads.submit(() -> callExternalApi(req)))
        .toList();
    // Each callExternalApi() blocks virtually — no thread starvation
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
[App shutdown: @PreDestroy called]
    → [pool.shutdown()]             ← YOU ARE HERE
    → [New submissions: rejected]
    → [Pending tasks: continue running]
    → [pool.awaitTermination(30s)]
    → [Last task completes: pool terminates]
    → [JVM exit proceeds normally]
```

FAILURE PATH (forgot shutdown):
```
[App: "started" signal to orchestrator]
    → [JVM: non-daemon pool threads prevent exit]
    → [Container: SIGTERM sent, timeout]
    → [SIGKILL: data loss for in-flight tasks]
    → [Fix: always shutdown executors in @PreDestroy]
```

---

### 💻 Code Example

```java
// Spring bean with proper lifecycle:
@Bean(destroyMethod = "shutdown")
public ExecutorService reportExecutor() {
    return Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors()
    );
}

// Service using injected executor:
@Service
class ReportService {
    private final ExecutorService executor;

    ReportService(ExecutorService reportExecutor) {
        this.executor = reportExecutor;
    }

    List<Report> generateAll(List<Long> ids) {
        List<Future<Report>> futures = ids.stream()
            .map(id -> executor.submit(
                () -> generateSingle(id)
            ))
            .toList();
        return futures.stream()
            .map(f -> {
                try { return f.get(60, SECONDS); }
                catch (Exception e) {
                    throw new ReportException(e);
                }
            })
            .toList();
    }
}
```

---

### ⚖️ Comparison Table

| Factory | Thread Count | Queue | Best For |
|---|---|---|---|
| `newFixedThreadPool(n)` | Fixed n | Unbounded LinkedList | CPU-bound bounded parallelism |
| `newCachedThreadPool()` | 0 to ∞ | SynchronousQueue | Short-lived I/O tasks, low-concurrency |
| `newSingleThreadExecutor()` | 1 | Unbounded | Sequential guaranteed ordering |
| `newVirtualThreadPerTaskExecutor()` | Virtual (millions) | None | I/O-heavy, Java 21+ |

How to choose: Fixed thread pool for CPU tasks (n = core count). Virtual thread executor for I/O. Single thread for sequential ordering guarantee.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `shutdown()` stops running tasks | `shutdown()` stops NEW submissions; running tasks finish normally. `shutdownNow()` interrupts running tasks (but they may ignore interrupts) |
| CachedThreadPool is always appropriate | CachedThreadPool creates a new thread for each task if pool is full. Under load spikes: OOM from unlimited thread creation |
| Fixed thread pool can't OOM | Fixed pool has bounded threads but unbounded queue — millions of queued tasks = OOM |

---

### 🚨 Failure Modes & Diagnosis

**Forgot shutdown — JVM won't exit:**
```bash
jstack <pid> | grep "pool-" | head -20
# Shows non-daemon threads keeping JVM alive
```
**Fix:** `@Bean(destroyMethod = "shutdown")` or try-with-resources.

**Unbounded queue growth (FixedThreadPool):**
```bash
# JMX: check JVM thread pool queue depth
jcmd <pid> GC.heap_info
```
**Fix:** Use `ThreadPoolExecutor` with bounded `ArrayBlockingQueue` + rejection handler.

---

### 🔗 Related Keywords

**Prerequisites:** `Executor`, `Callable`, `Future`
**Builds on:** `ThreadPoolExecutor`, `ForkJoinPool`
**Alternatives:** `CompletableFuture.supplyAsync()` for non-blocking chains

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Executor + submit/Future + shutdown       │
│              │ lifecycle — the standard thread pool API  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Always shutdown() + awaitTermination().   │
│              │ Submit ALL before get()-ing any — parallel│
│              │ FixedThreadPool queue is unbounded — cap  │
│              │ it with ThreadPoolExecutor if needed      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Thread pool with results, batches,       │
│              │  and graceful shutdown"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ThreadPoolExecutor → ForkJoinPool         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer uses `Executors.newFixedThreadPool(10)` for a service that calls an external API. The API sometimes takes 30 seconds to respond. At 100 RPS, 10 threads × 30s = 10 threads occupied for 30 seconds → backpressure after 10 concurrent, queue grows unbounded. Trace: what happens to `submit()` calls after pool is saturated, why the queue grows to OOM without bounded queue configuration, and what the exact `ThreadPoolExecutor` constructor arguments are for: 10 core threads, max 10, bounded queue of 100, reject policy that blocks caller until space is available (the `CallerRunsPolicy` variant that blocks rather than runs-in-caller).

