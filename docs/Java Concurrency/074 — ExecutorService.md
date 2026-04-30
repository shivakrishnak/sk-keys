---
layout: default
title: "ExecutorService"
parent: "Java Concurrency"
nav_order: 74
permalink: /java-concurrency/executorservice/
---
# 074 — ExecutorService

`#java` `#concurrency` `#threading` `#thread-pool` `#executor`

⚡ TL;DR — ExecutorService is a managed thread pool that decouples task submission from thread management — submit Runnable/Callable tasks; the pool handles thread lifecycle, queuing, and shutdown, returning Future for async results.

| #074 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, Runnable vs Callable, Future, Thread Pool | |
| **Used by:** | Future, CompletableFuture, Spring Async, Scheduled Tasks | |

---

### 📘 Textbook Definition

`ExecutorService` is a `java.util.concurrent` interface extending `Executor` that provides a managed pool of threads for executing tasks asynchronously. It supports submitting `Runnable` (via `execute` or `submit`) and `Callable<T>` (via `submit`) tasks, returning `Future<T>` for result retrieval. Lifecycle methods `shutdown()` (graceful) and `shutdownNow()` (forceful) control pool termination. `Executors` factory class provides pre-configured implementations: `newFixedThreadPool`, `newCachedThreadPool`, `newSingleThreadExecutor`, `newScheduledThreadPool`.

---

### 🟢 Simple Definition (Easy)

Instead of manually creating threads for every task, ExecutorService gives you a pool of worker threads. You hand it a task, it assigns an available worker. When the task finishes, that worker picks up the next task from the queue. You manage tasks, not threads — the pool handles thread creation, reuse, and cleanup.

---

### 🔵 Simple Definition (Elaborated)

Creating a new `Thread` for every task is expensive (~1MB stack, OS overhead, JVM bookkeeping). ExecutorService reuses threads — when a task finishes, the thread waits for the next task rather than dying. You choose the pool type: fixed size (predictable resource use), cached (elastic, good for I/O), single-threaded (sequential execution), or scheduled (periodic tasks). The submit/execute separation matters: `submit` returns a `Future` you can check for result/errors; `execute` is fire-and-forget with no result and silent exception swallowing.

---

### 🔩 First Principles Explanation

**The problem with raw thread creation:**

```
Task arrives every 10ms, each takes 100ms:

Without pool:
  new Thread(task1).start()  → 1MB stack
  new Thread(task2).start()  → 1MB stack
  ...
  new Thread(task100).start() → 100 MB after 1 second
  → OutOfMemoryError or OS thread limit hit

With fixed thread pool (size=10):
  Worker 1  handles task1, then task11, then task21...
  Worker 2  handles task2, then task12, then task22...
  ...
  Worker 10 handles task10, then task20...
  → 10 threads × 1MB = 10MB constant memory regardless of load
  → Extra tasks queue up and wait — no crash, backpressure applied
```

**Task lifecycle in the pool:**

```
submit(task)
    ↓
WorkQueue (LinkedBlockingQueue for fixed pool)
    ↓ worker picks up
Thread executes task
    ↓ task finishes
Thread returns to pool, picks up next queued task
    ↓ No more tasks
Thread waits (WAITING state) until new task arrives or timeout
```

---

### ❓ Why Does This Exist — Why Before What

```
Without ExecutorService (Java 1.4 and before):
  → Developers manually managed thread pools with hand-rolled linked lists
  → Thread creation/destruction overhead on every request
  → No standardized lifecycle (start/stop/drain)
  → No standard way to retrieve results or exceptions from async tasks

With ExecutorService (Java 5+):
  ✅ Thread reuse → predictable resource consumption
  ✅ Task queue → backpressure, no unbounded thread creation
  ✅ Future<T> → get results and exceptions from async tasks
  ✅ Lifecycle methods → graceful shutdown, await termination
  ✅ Pluggable implementations → virtual thread executor (Java 21)
```

---

### 🧠 Mental Model / Analogy

> ExecutorService is a **restaurant kitchen**. You (the application) are a waiter taking orders (tasks) and putting them on the order rail (queue). The cooks (thread pool) pick orders from the rail and prepare them. There are always exactly N cooks (fixed pool) — orders beyond that wait on the rail. When closing (shutdown), waiters stop taking new orders, and cooks finish everything on the rail before going home.

---

### ⚙️ How It Works — Pool Types

```
Executors.newFixedThreadPool(n)
  → n threads, unbounded queue
  → Best for: CPU-bound tasks where n ≈ CPU cores
  → Risk: queue grows unbounded under sustained load

Executors.newCachedThreadPool()
  → 0 to Integer.MAX_VALUE threads (elastic)
  → Idle threads die after 60s
  → Best for: short-lived I/O tasks with variable load
  → Risk: can create too many threads under sudden spike

Executors.newSingleThreadExecutor()
  → 1 thread, tasks execute in submission order
  → Best for: background sequential processing, event loop
  → Thread replaced if it dies unexpectedly

Executors.newScheduledThreadPool(n)
  → Supports delayed and periodic tasks
  → scheduleAtFixedRate (starts at regular intervals)
  → scheduleWithFixedDelay (waits between completions)

Executors.newVirtualThreadPerTaskExecutor() [Java 21]
  → Creates one virtual thread per task
  → Millions of tasks with near-zero overhead
  → Best for: I/O-heavy workloads (DB, HTTP, file)
```

---

### 🔄 How It Connects

```
ExecutorService
  │
  ├─ execute(Runnable)  → fire-and-forget
  ├─ submit(Runnable)   → Future<?> (null value, but tracks completion)
  ├─ submit(Callable)   → Future<T> with result
  ├─ invokeAll(...)     → submit list, wait for ALL to complete
  ├─ invokeAny(...)     → submit list, return FIRST successful result
  │
  ├─ shutdown()         → no new tasks; finishes queued + running
  ├─ shutdownNow()      → interrupts running; returns unstarted tasks
  └─ awaitTermination() → blocks caller until pool is fully terminated
```

---

### 💻 Code Example

```java
// Fixed thread pool — CPU-bound tasks
ExecutorService pool = Executors.newFixedThreadPool(
    Runtime.getRuntime().availableProcessors()
);

// submit Callable → get Future
List<Future<Integer>> futures = new ArrayList<>();
for (int i = 0; i < 10; i++) {
    final int num = i;
    futures.add(pool.submit(() -> computeSquare(num)));
}

// Collect results
for (Future<Integer> f : futures) {
    System.out.println(f.get()); // blocks per Future until result ready
}

// Always shut down — otherwise pool threads keep JVM alive
pool.shutdown();
pool.awaitTermination(30, TimeUnit.SECONDS);
```

```java
// Proper shutdown pattern
ExecutorService pool = Executors.newFixedThreadPool(4);
try {
    // submit tasks...
    pool.submit(task1);
    pool.submit(task2);
} finally {
    pool.shutdown();   // stop accepting new tasks
    try {
        if (!pool.awaitTermination(60, TimeUnit.SECONDS)) {
            pool.shutdownNow();  // force-cancel if still running after 60s
            if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
                System.err.println("Pool did not terminate");
            }
        }
    } catch (InterruptedException e) {
        pool.shutdownNow();
        Thread.currentThread().interrupt();
    }
}
```

```java
// invokeAll — submit batch, wait for all results
ExecutorService pool = Executors.newFixedThreadPool(4);
List<Callable<String>> tasks = List.of(
    () -> fetchFromServiceA(),
    () -> fetchFromServiceB(),
    () -> fetchFromServiceC()
);
List<Future<String>> futures = pool.invokeAll(tasks);  // blocks until ALL done
for (Future<String> f : futures) {
    System.out.println(f.get());  // each is already done — get() won't block
}
```

```java
// invokeAny — return first successful result (cancel rest)
ExecutorService pool = Executors.newFixedThreadPool(3);
String result = pool.invokeAny(List.of(
    () -> callPrimaryServer(),
    () -> callFallbackServer(),
    () -> callDRServer()
));
// Returns whichever server responds first — cancels the others
System.out.println("Got result from fastest server: " + result);
```

```java
// Java 21: virtual thread executor for I/O-bound tasks
ExecutorService vPool = Executors.newVirtualThreadPerTaskExecutor();
// Each task runs on a separate virtual thread — millions possible
for (int i = 0; i < 100_000; i++) {
    vPool.submit(() -> httpClient.get("https://api.example.com/data/" + id));
}
vPool.shutdown();
vPool.awaitTermination(60, TimeUnit.SECONDS);
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `execute()` and `submit()` are interchangeable | `execute()` is fire-and-forget; `submit()` returns Future — errors only visible via Future.get() |
| `shutdown()` kills all running tasks | `shutdown()` is graceful — it drains the queue; `shutdownNow()` interrupts active tasks |
| Pool threads die after tasks complete | Fixed pool threads wait for new tasks (WAITING) — they stay alive until shutdown |
| `newCachedThreadPool()` is always better | Cached pool can create unbounded threads under load — risky in production |
| Not calling shutdown() is safe | Pool threads are user threads — they prevent JVM exit; always shut down |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using default unbounded queue with fixed pool — queue overflow**

```java
// Fixed pool with unbounded queue — under sustained overload:
ExecutorService pool = Executors.newFixedThreadPool(10);
// LinkedBlockingQueue is unbounded → tasks pile up → OutOfMemoryError

// Fix: use ThreadPoolExecutor with bounded queue + rejection policy
ExecutorService pool = new ThreadPoolExecutor(
    10, 20,                              // core, max threads
    60L, TimeUnit.SECONDS,              // idle thread timeout
    new ArrayBlockingQueue<>(1000),     // bounded queue
    new ThreadPoolExecutor.CallerRunsPolicy() // backpressure: caller runs task
);
```

**Pitfall 2: Forgetting to call shutdown — JVM won't exit**

```java
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(task);
// Program logic finishes but JVM doesn't exit — pool threads still alive
// Fix: always call pool.shutdown() or use try-with-resources (Java 19+)
try (ExecutorService pool = Executors.newFixedThreadPool(4)) {  // Java 19+
    pool.submit(task);
} // auto-shutdown on exit
```

**Pitfall 3: Silently swallowing exceptions with execute()**

```java
pool.execute(() -> {
    throw new RuntimeException("Something failed!");
});
// Exception is swallowed — no log, task appears to complete normally

// Fix: use submit + check Future.get(), or set a UncaughtExceptionHandler
pool.submit(() -> {
    throw new RuntimeException("Something failed!");
}).get(); // throws ExecutionException — exception is visible
```

---

### 🔗 Related Keywords

- **[Thread](./066 — Thread.md)** — ExecutorService manages a pool of these
- **[Runnable vs Callable](./067 — Runnable vs Callable.md)** — the two task types ExecutorService accepts
- **[Future & CompletableFuture](./075 — Future and CompletableFuture.md)** — how results and errors are retrieved
- **[ThreadLocal](./073 — ThreadLocal.md)** — ThreadLocal cleanup needed in pooled threads
- **[Deadlock](./071 — Deadlock.md)** — can occur when pool tasks wait for each other

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Managed thread pool: decouple task submission │
│              │ from thread lifecycle; reuse threads safely   │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Any async/parallel work — always use instead  │
│              │ of raw new Thread() in production code        │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid Executors.newCachedThreadPool for steady│
│              │ high-load; use bounded ThreadPoolExecutor     │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Don't create threads — submit tasks;         │
│              │  the pool handles the rest"                   │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Future → CompletableFuture → ThreadPoolExecutor│
│              │ → Virtual Threads (Java 21) → ForkJoinPool    │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a `FixedThreadPool(5)` and submit 5 tasks that each call `pool.submit(subTask).get()` inside them — waiting for a nested task in the same pool. What happens? How many threads are now at capacity and waiting? What is this called and how do you fix it?

**Q2.** `shutdown()` vs `shutdownNow()` — what do they guarantee? If you call `shutdownNow()`, are all running tasks stopped immediately? What must tasks do to support responsive cancellation?

**Q3.** `Executors.newVirtualThreadPerTaskExecutor()` creates a new virtual thread per task — no reuse. Why is this not wasteful like creating new platform threads for each task? What makes virtual threads cheap enough to create-and-discard?

