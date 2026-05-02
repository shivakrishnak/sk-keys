---
layout: default
title: "Thread Pool Pattern"
parent: "Design Patterns"
nav_order: 792
permalink: /design-patterns/thread-pool-pattern/
number: "792"
category: Design Patterns
difficulty: ★★★
depends_on: "Producer-Consumer Pattern, Object Pool Pattern, Thread Safety, ExecutorService"
used_by: "Web servers, task queues, parallel processing, Spring async, async I/O"
tags: #advanced, #design-patterns, #concurrency, #threading, #performance, #java-concurrency
---

# 792 — Thread Pool Pattern

`#advanced` `#design-patterns` `#concurrency` `#threading` `#performance` `#java-concurrency`

⚡ TL;DR — **Thread Pool** pre-creates a fixed set of reusable worker threads that process tasks from a shared queue — avoiding thread creation overhead per task, bounding concurrent threads, and enabling back-pressure and graceful shutdown.

| #792            | Category: Design Patterns                                                      | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Producer-Consumer Pattern, Object Pool Pattern, Thread Safety, ExecutorService |                 |
| **Used by:**    | Web servers, task queues, parallel processing, Spring async, async I/O         |                 |

---

### 📘 Textbook Definition

**Thread Pool**: a concurrency design pattern that maintains a pool of pre-initialized worker threads that are available to execute submitted tasks. Instead of creating a new thread per task (expensive: ~100μs, ~512KB–1MB stack), tasks are submitted to a queue and picked up by available threads from the pool. Components: **task queue** (bounded `BlockingQueue`); **worker threads** (pre-created, loop consuming from queue); **pool management** (min/max threads, idle timeout, rejection policies). Java: `java.util.concurrent.ThreadPoolExecutor` is the standard implementation. `ExecutorService` factory methods: `newFixedThreadPool(n)`, `newCachedThreadPool()`, `newScheduledThreadPool(n)`, `ForkJoinPool`. Spring: `@Async` with `TaskExecutor`. Virtual threads (Java 21): lightweight threads that change the calculus — a thread per task becomes feasible again.

---

### 🟢 Simple Definition (Easy)

A team of 5 customer service agents. When a customer call comes in (task), it's routed to an available agent (worker thread). If all 5 agents are busy, the call waits on hold (queue). When an agent finishes, they take the next call from the queue. The company doesn't hire and fire agents for every call — 5 agents handle many calls throughout the day. Thread Pool: 5 agents = 5 pre-created threads. Call queue = task queue.

---

### 🔵 Simple Definition (Elaborated)

`Executors.newFixedThreadPool(10)`: 10 threads pre-created. Submit 1000 tasks: all 1000 go on queue; 10 threads process them concurrently in batches. Creating 1000 threads: ~100ms + ~512MB RAM. Thread Pool: 10 threads created once; 1000 tasks processed in waves. Spring `@Async`: methods annotated `@Async` execute on a thread from Spring's `TaskExecutor` (thread pool) — calling thread returns immediately; method runs on pool thread. `ThreadPoolTaskExecutor` configures core size, max size, queue capacity, and rejection policy.

---

### 🔩 First Principles Explanation

**ThreadPoolExecutor parameters and their interactions:**

```
ThreadPoolExecutor INTERNALS:

  new ThreadPoolExecutor(
      corePoolSize,       // threads always alive (even idle)
      maximumPoolSize,    // max threads when queue is full
      keepAliveTime,      // idle time before non-core threads are terminated
      timeUnit,
      workQueue,          // where tasks wait
      threadFactory,      // creates threads (name them, set daemon flag, etc.)
      rejectionHandler    // policy when queue full AND at maxPoolSize
  );

TASK SUBMISSION FLOW (surprising precedence — confusing!):

  Submit task:
  1. If running threads < corePoolSize: CREATE new thread immediately (even if idle threads exist!)
  2. If at corePoolSize: try to queue in workQueue
  3. If workQueue full AND running < maximumPoolSize: CREATE new non-core thread
  4. If workQueue full AND at maximumPoolSize: apply rejectionHandler

  IMPORTANT: Queue is tried BEFORE maximumPoolSize expansion.
  maxPoolSize only matters when queue is full.

  Example:
  core=10, max=20, queue=LinkedBlockingQueue(100):
  1-10 tasks: create 10 core threads
  11-110 tasks: queue tasks (queue capacity 100)
  111-120 tasks: create 10 extra threads (up to max=20)
  121+ tasks: rejection!

  With SynchronousQueue (zero capacity):
  core=0, max=∞ (newCachedThreadPool):
  Every task creates a new thread immediately.
  Idle threads survive keepAliveTime then terminate.

EXECUTORSERVICE FACTORY METHODS:

  newFixedThreadPool(n):
  ThreadPoolExecutor(n, n, 0, ms, LinkedBlockingQueue.unbounded)
  Always exactly n threads. Unbounded queue: no rejection, no back-pressure.
  ✓ CPU-bound tasks: n = Runtime.getRuntime().availableProcessors()
  ⚠ Unbounded queue: slow tasks can cause queue to grow unboundedly (OOM)

  newCachedThreadPool():
  ThreadPoolExecutor(0, MAX_VALUE, 60s, SynchronousQueue)
  Creates threads as needed; recycles idle threads.
  ✓ Many short-lived tasks; bursty I/O workloads
  ⚠ Unbounded threads: spike in tasks → spike in threads → OOM or OS thread limit

  newScheduledThreadPool(n):
  ScheduledThreadPoolExecutor(n)
  ✓ Periodic tasks (cron-like); delayed execution

  ForkJoinPool.commonPool():
  Work-stealing pool for divide-and-conquer parallel tasks.
  parallelStream() uses it. default size = CPU cores - 1.
  ⚠ NEVER run blocking I/O on commonPool — starves parallel streams.

SPRING ThreadPoolTaskExecutor:

  @Configuration
  @EnableAsync
  class AsyncConfig implements AsyncConfigurer {

      @Override
      @Bean
      public Executor getAsyncExecutor() {
          ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
          executor.setCorePoolSize(10);          // always alive
          executor.setMaxPoolSize(50);           // max on queue full
          executor.setQueueCapacity(200);        // queue depth
          executor.setKeepAliveSeconds(60);      // idle non-core thread survival
          executor.setThreadNamePrefix("async-"); // thread naming for diagnostics
          executor.setRejectionPolicy(
              new ThreadPoolExecutor.CallerRunsPolicy()  // back-pressure: caller runs task
          );
          executor.initialize();
          return executor;
      }
  }

  @Service
  class EmailService {
      @Async
      CompletableFuture<Void> sendEmail(String to, String body) {
          // runs on async- thread pool, not caller thread
          emailClient.send(to, body);
          return CompletableFuture.completedFuture(null);
      }
  }

REJECTION POLICIES:

  AbortPolicy (default):    throw RejectedExecutionException
  CallerRunsPolicy:         caller thread executes the task (back-pressure!)
  DiscardPolicy:            silently drop new tasks
  DiscardOldestPolicy:      drop oldest queued task; retry submitting new one

  CallerRunsPolicy is BEST for most services:
  → When pool is saturated, caller thread does work.
  → Caller blocks → request rate slows naturally → back-pressure.
  → No tasks lost. System self-regulates.

JAVA 21 VIRTUAL THREADS (PROJECT LOOM):

  // Virtual threads are JVM-managed, lightweight (few KB, not 512KB+).
  // Thread-per-task model becomes viable again:

  ExecutorService virtualPool = Executors.newVirtualThreadPerTaskExecutor();
  // Creates a new virtual thread per task — millions of virtual threads OK.

  // For I/O-bound tasks: virtual threads make thread pools less critical.
  // A blocking virtual thread is "unmounted" from the carrier thread — no OS thread wasted.
  // Still useful to limit concurrency (semaphore) to avoid overwhelming downstream resources.

SIZING THREAD POOLS:

  CPU-bound tasks:
  pool size ≈ N_CPUS (avoid context-switching overhead)

  I/O-bound tasks (blocking I/O, DB calls):
  pool size ≈ N_CPUS × (1 + wait_time / compute_time)
  If I/O takes 100ms and CPU takes 10ms: pool size ≈ N_CPUS × 11

  Rule of thumb for Java web services (pre-Loom):
  Tomcat default: 200 threads (handles 200 concurrent HTTP requests)
  DB pool: 10-20 connections (DB can't handle 200 concurrent)
  → Design: most requests complete in <100ms; 200 threads handle much higher throughput.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Thread Pool:

- `new Thread(() -> handleRequest(r)).start()` per request: thread creation overhead + unlimited thread count → OOM under load

WITH Thread Pool:
→ Fixed thread count. Tasks queue when all busy. Back-pressure via bounded queue. Graceful degradation.

---

### 🧠 Mental Model / Analogy

> Post office with 5 counters (worker threads). Customers arrive (tasks submitted). Available counter serves the next customer. If all 5 counters busy: customers wait in the queue. Queue full and no counters: reject (or handle via policy). Closing time (shutdown): finish all customers currently being served; no new customers accepted. Thread pool is the post office — counters are threads, customers are tasks.

"Post office" = ThreadPoolExecutor
"Counters (5)" = worker threads (corePoolSize)
"Customers wait in line" = task queue (BlockingQueue)
- "Line too long → no new customers accepted" = rejection policy (queue full + maxPoolSize reached)
"Closing time" = shutdown() + awaitTermination()

---

### ⚙️ How It Works (Mechanism)

```
THREAD POOL TASK EXECUTION:

  submit(task):
  1. If workers < corePoolSize: start new worker thread → run task
  2. Else: offer to queue
  3. If queue full AND workers < maxPoolSize: start new worker → run task
  4. If queue full AND workers == maxPoolSize: apply RejectedExecutionHandler

  Worker thread loop:
  while (running) {
      task = queue.take();    // block if empty
      task.run();             // execute
  }

  Shutdown:
  shutdown(): reject new submissions; let queued tasks finish; workers exit when idle
  shutdownNow(): interrupt workers; return remaining queued tasks unexecuted
  awaitTermination(timeout): wait for all tasks to finish or timeout
```

---

### 🔄 How It Connects (Mini-Map)

```
Reusable worker threads + task queue; bounded concurrency; back-pressure
        │
        ▼
Thread Pool Pattern ◄──── (you are here)
(ThreadPoolExecutor; core/max threads; queue; rejection policy)
        │
        ├── Producer-Consumer: thread pool IS P-C: submit=produce, worker threads=consume
        ├── Object Pool: thread pool = Object Pool for Thread objects
        ├── Future/CompletableFuture: async result handle for submitted tasks
        └── Virtual Threads (Java 21): alternative to thread pools for I/O-bound workloads
```

---

### 💻 Code Example

```java
// Custom thread pool with monitoring:
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    5,                          // corePoolSize
    20,                         // maximumPoolSize
    60L, TimeUnit.SECONDS,      // keepAliveTime for non-core threads
    new LinkedBlockingQueue<>(500),  // bounded queue (back-pressure)
    new ThreadFactory() {
        private final AtomicInteger count = new AtomicInteger(0);
        @Override
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r, "worker-" + count.incrementAndGet());
            t.setDaemon(false);      // non-daemon: JVM waits for workers to finish
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy()  // back-pressure: caller runs when saturated
);

// Monitor pool health:
ScheduledExecutorService monitor = Executors.newSingleThreadScheduledExecutor();
monitor.scheduleAtFixedRate(() -> {
    System.out.printf("Pool: active=%d, queued=%d, completed=%d, poolSize=%d%n",
        executor.getActiveCount(),
        executor.getQueue().size(),
        executor.getCompletedTaskCount(),
        executor.getPoolSize());
}, 10, 10, TimeUnit.SECONDS);

// Submit tasks:
List<Future<Result>> futures = tasks.stream()
    .map(task -> executor.submit(() -> processTask(task)))
    .collect(Collectors.toList());

// Collect results:
for (Future<Result> f : futures) {
    Result result = f.get(30, TimeUnit.SECONDS);  // wait max 30s per task
    handleResult(result);
}

// Graceful shutdown:
executor.shutdown();
if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
    executor.shutdownNow();  // force if graceful shutdown takes too long
}
```

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More threads = faster                       | False for CPU-bound work. Beyond N_CPUs threads, context-switching overhead reduces throughput. For I/O-bound work: more threads CAN help (threads wait on I/O, not CPU). But too many threads: contention on shared resources (DB connections), OOM from stack allocations, scheduler thrashing. Profile to find optimal pool size.  |
| newCachedThreadPool() is safe for high-load | DANGEROUS for burst traffic. `newCachedThreadPool()` = unbounded threads. 10,000 simultaneous tasks = 10,000 threads = OS thread limit hit or OOM. Use `newFixedThreadPool(n)` or `ThreadPoolExecutor` with bounded queue and rejection policy for production services.                                                               |
| shutdown() immediately stops all tasks      | `shutdown()` ONLY stops accepting new tasks. Already-submitted tasks (in queue + running) complete normally. `shutdownNow()` interrupts running tasks and returns unexecuted queued tasks — but tasks must check `Thread.interrupted()` to respond. A task that ignores interrupts will run to completion even after `shutdownNow()`. |

---

### 🔥 Pitfalls in Production

**Thread pool deadlock — all threads waiting on tasks that need free threads:**

```java
// DEADLOCK: parent tasks submit child tasks; all threads occupied by parent tasks;
// child tasks can never execute; parent tasks wait forever for child results:
ExecutorService pool = Executors.newFixedThreadPool(5);

// 5 parent tasks submitted — fills the 5 threads:
for (int i = 0; i < 5; i++) {
    pool.submit(() -> {
        // Parent task: submits child task and WAITS for its result:
        Future<String> child = pool.submit(() -> doChildWork());  // submitted to queue
        String result = child.get();  // BLOCKS — waits for child task
        // But pool has 0 free threads (all 5 blocked here!)
        // child task is queued but NEVER executes — no free threads
        // DEADLOCK: all 5 threads blocked waiting for child tasks that can never run.
    });
}

// FIX 1: Use a separate pool for child tasks:
ExecutorService parentPool = Executors.newFixedThreadPool(5);
ExecutorService childPool  = Executors.newFixedThreadPool(10);
// parent task submits to childPool — no pool self-deadlock.

// FIX 2: Use CompletableFuture (async continuation — no blocking):
pool.submit(() -> {
    CompletableFuture.supplyAsync(() -> doChildWork(), pool)
                     .thenAccept(result -> processResult(result));
    // Non-blocking: when child completes, thenAccept runs without holding a thread
});

// FIX 3: Restructure to eliminate parent-child task dependency within same pool.
```

---

### 🔗 Related Keywords

- `Producer-Consumer Pattern` — thread pool IS Producer-Consumer: submitters produce, workers consume
- `Object Pool Pattern` — thread pool = Object Pool for Thread objects (pre-allocated, reused)
- `CompletableFuture` — async result composition; tasks submitted to thread pool return CompletableFutures
- `Virtual Threads (Java 21)` — lightweight threads that reduce the need for pool sizing for I/O-bound work
- `Spring @Async` — Spring's thread pool abstraction for non-blocking method execution

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Pre-created worker threads consume from  │
│              │ task queue. Bounded concurrency. Back-   │
│              │ pressure via bounded queue + rejection.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many short-lived tasks; bounding         │
│              │ concurrency; avoiding thread creation    │
│              │ overhead; async task execution           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Java 21 virtual threads cover I/O-bound  │
│              │ case; tasks must execute in strict order;│
│              │ tasks submit child tasks to same pool    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Post office: 5 counters serve customers │
│              │  from a queue — counters don't retire    │
│              │  after each customer."                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CompletableFuture → Virtual Threads →    │
│              │ ForkJoinPool → Spring @Async             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java 21's virtual threads (`Thread.ofVirtual()`) are mounted onto a small pool of OS (carrier) threads from the `ForkJoinPool`. When a virtual thread performs blocking I/O, it is unmounted from the carrier thread (which is freed to run other virtual threads) and remounted when the I/O completes. This means you can have millions of virtual threads with only N_CPU carrier threads. Does this make traditional `ThreadPoolExecutor` obsolete for I/O-bound workloads? What use cases remain where a traditional thread pool is still better than virtual threads?

**Q2.** `ForkJoinPool` and `ThreadPoolExecutor` are both thread pools, but with fundamentally different task execution models. `ThreadPoolExecutor`: global shared queue; one thread picks from head; no work stealing. `ForkJoinPool`: each worker has its own deque (double-ended queue); when idle, a worker steals from the tail of another worker's deque. Why is work stealing better for recursive, divide-and-conquer tasks (`parallelStream()`, `RecursiveTask`)? In what scenario would work stealing perform WORSE than a shared queue?
