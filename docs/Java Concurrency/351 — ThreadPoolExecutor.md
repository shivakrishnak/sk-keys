---
layout: default
title: "ThreadPoolExecutor"
parent: "Java Concurrency"
nav_order: 351
permalink: /java-concurrency/thread-pool-executor/
number: "0351"
category: Java Concurrency
difficulty: ★★★
depends_on: ExecutorService, Runnable, Callable, BlockingQueue
used_by: ForkJoinPool, ExecutorService
related: ExecutorService, ForkJoinPool, BlockingQueue
tags:
  - java
  - concurrency
  - thread-pool
  - deep-dive
  - internals
---

# 0351 — ThreadPoolExecutor

⚡ TL;DR — `ThreadPoolExecutor` is the concrete thread pool implementation underlying `Executors.newFixedThreadPool()` — exposing all tunable parameters: core/max thread counts, keep-alive time, work queue type, and rejection handler — enabling precise control over pool behaviour.

| #0351 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ExecutorService, Runnable, Callable, BlockingQueue | |
| **Used by:** | ForkJoinPool, ExecutorService | |
| **Related:** | ExecutorService, ForkJoinPool, BlockingQueue | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
`Executors.newFixedThreadPool(10)` uses an unbounded `LinkedBlockingQueue`. At 100 tasks/second with 10 threads processing at 30 seconds each, the queue grows at 90 tasks/second — eventually OOM. There's no way to customise rejection behaviour, queue depth, or keep-alive time without understanding and using `ThreadPoolExecutor` directly.

THE INVENTION MOMENT:
`ThreadPoolExecutor` is the fully-configurable thread pool — all factory methods in `Executors` delegate to it with preset parameters. Direct usage enables production-tuned configurations.

### 📘 Textbook Definition

**`ThreadPoolExecutor`** is the primary implementation of `ExecutorService` providing a configurable thread pool. Constructor parameters: `corePoolSize` — threads maintained even when idle; `maximumPoolSize` — max threads when queue is full; `keepAliveTime` — how long excess threads wait before termination; `unit` — time unit for keepAliveTime; `workQueue` — `BlockingQueue` for pending tasks; `threadFactory` — creates new threads (optional); `handler` — `RejectedExecutionHandler` when queue is full and max threads reached. Thread lifecycle: threads created on demand up to `corePoolSize`; if all busy, tasks queue; if queue full, threads up to `maximumPoolSize`; if max reached, apply rejection handler.

### ⏱️ Understand It in 30 Seconds

**One line:**
`ThreadPoolExecutor` = a configurable thread pool — set thread counts, queue size, and what happens when full.

**One analogy:**
> A restaurant kitchen with configurable staff. Core cook count (corePoolSize): 5 always present. If queued orders exceed capacity, hire seasonal staff up to 10 (maximumPoolSize). If 10 cooks and queue still full: turn new orders away or call the chef to notify (rejection handler). Seasonal staff go home after 60 seconds of no orders (keepAliveTime).

**One insight:**
The counterintuitive ThreadPoolExecutor growth: new threads are only created when the queue is FULL and thread count is below max. So for `new ThreadPoolExecutor(2, 10, 60s, SECONDS, new LinkedBlockingQueue<>(100))`, the pool has 2 threads by default, queues up to 100, THEN scales to 10. Think "queue first, then scale."

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Threads are created on-demand up to `corePoolSize` first, then tasks queue, then threads scale to `maximumPoolSize` if queue full.
2. Threads above `corePoolSize` are removed after `keepAliveTime` idle; core threads are permanent (unless `allowCoreThreadTimeOut(true)`).
3. The queue type determines pool behaviour under load: unbounded → no limit on queued tasks; bounded → enables scaling beyond corePoolSize.

**Thread lifecycle decision tree:**
```
Task submitted:
  threadCount < corePoolSize?
    YES → create new thread to run task immediately
    NO  → queue.offer(task)?
           YES → task queued (thread picks up when free)
           NO (queue full) → threadCount < maxPoolSize?
                              YES → create new thread
                              NO  → RejectedExecutionHandler
```

**Queue type selection:**
```java
// Unbounded queue (DEFAULT for Executors.newFixedThreadPool):
new LinkedBlockingQueue<>() // tasks queue forever → OOM risk

// Bounded queue (production recommendation):
new ArrayBlockingQueue<>(100) // blocks scale-out + rejection

// SynchronousQueue (DEFAULT for newCachedThreadPool):
new SynchronousQueue<>() // no queuing — immediate thread or bail
```

THE TRADE-OFFS:
Gain: Full control over all pool parameters; configurable rejection; custom thread factories; performance tuning.
Cost: Complex to configure correctly; wrong parameters cause OOM, starvation, or excessive thread creation; developers must understand growth model.

### 🧪 Thought Experiment

SETUP: Service needing backpressure for external API calls.

MISCONFIGURED (Executors.newFixedThreadPool):
```java
// Hidden: LinkedBlockingQueue() with no capacity bound
ExecutorService pool = Executors.newFixedThreadPool(10);
// queue.offer() ALWAYS returns true → tasks queue indefinitely
// 10,000 slow requests → 10,000 queued tasks → OOM
```

CORRECTLY CONFIGURED:
```java
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    10,               // corePoolSize: 10 always
    10,               // maxPoolSize: 10 (fixed)
    0, TimeUnit.SECONDS, // keepAlive: irrelevant (core = max)
    new ArrayBlockingQueue<>(100), // queue: max 100 waiting
    new ThreadPoolExecutor.CallerRunsPolicy() // on full: caller executes
);
// Backpressure: when queue(100) + threads(10) full,
// CallerRunsPolicy runs task in the caller's thread
// → caller slows down → natural flow control
```

THE INSIGHT:
`CallerRunsPolicy` as rejection handler provides natural backpressure — when the pool is full, the submitting thread runs the task itself, slowing submission rate to match processing rate.

### 🧠 Mental Model / Analogy

> `ThreadPoolExecutor` is a factory floor configuration panel. Dial 1: minimum staff (corePoolSize). Dial 2: maximum staff during peak (maximumPoolSize). Buffer: the work order queue (workQueue). Overflow protocol: what happens when everything is full (rejectionHandler). Go-home timer: how long idle extra staff wait (keepAliveTime).

### 📶 Gradual Depth — Four Levels

**Level 1:** A configurable, tuneable thread pool where you set how many threads, how big the queue, and what to do when both are full.

**Level 2:** Direct construction gives production control. Always use bounded queue (`ArrayBlockingQueue`) in production. `CallerRunsPolicy` provides natural backpressure. `AbortPolicy` (default) throws `RejectedExecutionException`. `DiscardPolicy` silently discards. Custom `ThreadFactory` enables naming threads for debugging.

**Level 3:** `ThreadPoolExecutor` uses an internal `AtomicInteger ctl` combining thread count (low 29 bits) and pool state (high 3 bits). Workers are `HashSet<Worker>` (each `Worker` wraps a thread + `Runnable`). `getTask()` from queue blocks workers when idle. `processWorkerExit()` handles thread termination and potential replacement. Pool state: RUNNING → SHUTDOWN → TIDYING → TERMINATED.

**Level 4:** The design of thread creation order (core first, queue second, scale-out third) was deliberate. For CPU-bound workloads: core should equal CPU count, queue acts as buffer absorbing burst. For I/O-bound: virtual threads (`Executors.newVirtualThreadPerTaskExecutor()`) are the modern replacement — no queue depth needed because virtual threads don't consume OS threads during blocking I/O.

### ⚙️ How It Works (Mechanism)

**Full constructor (production-ready pattern):**
```java
int cpuCount = Runtime.getRuntime().availableProcessors();

ThreadPoolExecutor executor = new ThreadPoolExecutor(
    cpuCount,           // corePoolSize
    cpuCount * 2,       // maximumPoolSize (allow burst)
    60L,                // keepAliveTime
    TimeUnit.SECONDS,   // unit
    new ArrayBlockingQueue<>(500), // bounded queue
    new ThreadFactory() {          // named threads
        AtomicInteger count = new AtomicInteger();
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r);
            t.setName("order-worker-" + count.getAndIncrement());
            t.setUncaughtExceptionHandler((thread, ex) ->
                log.error("Uncaught in {}: ", thread.getName(), ex)
            );
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy() // backpressure
);
```

**Rejection handlers:**
```java
// AbortPolicy (default): throw RejectedExecutionException
// DiscardPolicy: silently drop task
// DiscardOldestPolicy: drop oldest queued task, retry submit
// CallerRunsPolicy: run in calling thread (backpressure)

// Custom: log + metric + discard
executor.setRejectedExecutionHandler((r, pool) -> {
    metrics.increment("executor.rejected");
    log.warn("Task rejected — pool full, max={}", pool.getMaximumPoolSize());
});
```

**Monitoring a live pool:**
```java
log.info("Pool stats: active={}, queue={}, completed={}, pool={}",
    executor.getActiveCount(),
    executor.getQueue().size(),
    executor.getCompletedTaskCount(),
    executor.getPoolSize()
);
```

### 🔄 The Complete Picture — End-to-End Flow

```
[submit(task) when corePoolSize reached and queue empty]
    → [queue.offer(task) → queued]             ← YOU ARE HERE
    → [Worker thread: queue.poll() picks up]
    → [task.run() executes]
    → [Worker: queue.poll() again — idle loop]
    → [No tasks for keepAliveTime: thread exits if > core]
```

REJECTION FLOW:
```
[All 10 threads busy, queue(ArrayBlockingQueue 100) full]
    → [max threads reached (10 = max): reject!]
    → [CallerRunsPolicy: calling thread runs task]
    → [Caller is slowed — natural backpressure]
    → [Pool drains: caller resumes submitting]
```

### 💻 Code Example

```java
// Production-recommended pattern:
private ExecutorService buildExecutor(int coreSize,
                                      int maxSize,
                                      int queueCapacity,
                                      String prefix) {
    return new ThreadPoolExecutor(
        coreSize, maxSize,
        60, SECONDS,
        new ArrayBlockingQueue<>(queueCapacity),
        r -> {
            Thread t = new Thread(r, prefix + "-" +
                threadNum.getAndIncrement());
            t.setDaemon(false);
            return t;
        },
        new ThreadPoolExecutor.CallerRunsPolicy()
    );
}

// CPU-bound compute:
ExecutorService compute = buildExecutor(
    cpuCount, cpuCount, 200, "compute");

// I/O-bound (Java 21):
ExecutorService io = Executors
    .newVirtualThreadPerTaskExecutor();
```

### ⚖️ Comparison Table

| Factory Method | coreSize | maxSize | Queue | Rejection |
|---|---|---|---|---|
| newFixedThreadPool(n) | n | n | Unbounded LinkedList | AbortPolicy |
| newCachedThreadPool() | 0 | MAX_INT | SynchronousQueue | AbortPolicy |
| newSingleThreadExecutor() | 1 | 1 | Unbounded LinkedList | AbortPolicy |
| **Direct ThreadPoolExecutor** | Configurable | Configurable | Configurable | Configurable |

How to choose: Direct `ThreadPoolExecutor` for production when you need bounded queues, custom rejection, or named threads. Factory methods for quick/demo code only.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ThreadPoolExecutor scales up first, queues second | WRONG — it queues up to `queueCapacity` FIRST, then scales beyond `corePoolSize`. With unbounded queue, it NEVER scales beyond corePoolSize! |
| Setting high maxPoolSize solves scaling | With unbounded queue, maxPoolSize is irrelevant — the queue absorbs all tasks before scaling. Need bounded queue for maxPoolSize to matter |
| shutdown() calls are immediate | `shutdown()` is non-blocking: it initiates shutdown but returns immediately. `awaitTermination()` is the blocking wait for drain. |

### 🚨 Failure Modes & Diagnosis

**OOM from unbounded queue:**
```bash
jcmd <pid> VM.info | grep "OutOfMemory"
jstack <pid> | grep "pool-" -c  # count pool threads
```
Fix: Use `new ArrayBlockingQueue<>(maxCapacity)` + appropriate rejection handler.

**Threads not scaling (stuck at corePoolSize):**
Fix: Use `SynchronousQueue` instead of bounded queue to force direct thread creation, or pre-start core threads: `executor.prestartAllCoreThreads()`.

### 🔗 Related Keywords

**Prerequisites:** `ExecutorService`, `BlockingQueue`, `Runnable`
**Builds on:** `ForkJoinPool` — work-stealing alternative; virtual threads — replacement for I/O pools
**Related:** `BlockingQueue`, `RejectedExecutionHandler`

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fully configurable thread pool: core,    │
│              │ max, queue, keepAlive, rejection handler  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Queues BEFORE scaling beyond corePoolSize!│
│              │ Unbounded queue → never scales, OOM risk  │
│              │ CallerRunsPolicy = free backpressure      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The configurable factory behind every    │
│              │  Executors.newX() call"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ForkJoinPool → Virtual Threads            │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** Explain with exact thread counts and queue sizes what happens in a `ThreadPoolExecutor(5, 20, 60s, SECONDS, new ArrayBlockingQueue<>(50))` under these sequential events: (a) 5 tasks submitted; (b) all 5 run for 60s, then 10 more tasks submitted; (c) all 15 run for 60s, then 60 tasks submitted simultaneously. At each point, how many threads are active, how many tasks are queued, and what happens to the 61st task submitted?

**Q2.** `ThreadPoolExecutor.CallerRunsPolicy` runs rejected tasks in the caller's thread. A Spring `@RestController` handler calls `executor.submit(task)` and the pool is full — `CallerRunsPolicy` runs the task in the HTTP request thread. Explain the specific production risk: why running a 5-second task in the HTTP request thread causes a cascade failure, what Tomcat/Jetty's connector thread limit means for this scenario, and why this "free backpressure" can become a full application freeze under certain load patterns.

