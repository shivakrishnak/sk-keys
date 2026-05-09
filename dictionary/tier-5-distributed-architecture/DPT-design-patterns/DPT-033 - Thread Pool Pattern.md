---
layout: default
title: "Thread Pool Pattern"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 33
permalink: /design-patterns/thread-pool-pattern/
id: DPT-033
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - deep-dive
  - concurrency
  - java
  - performance
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-033 - Thread Pool Pattern

⚡ TL;DR - Thread Pool pre-allocates a fixed set of reusable threads and routes tasks through a queue, eliminating the cost of repeated thread creation and preventing resource exhaustion.

| DPT-033 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Thread, ExecutorService, BlockingQueue, Producer-Consumer, Java Concurrency | |
| **Used by:** | Web Servers, Database Connection Pools, Reactive Frameworks, Async Task Execution | |
| **Related:** | Producer-Consumer, Scheduler Pattern, Bulkhead, Object Pool, ThreadPoolExecutor | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Each incoming HTTP request spawns a new thread: `new Thread(() -> handleRequest(req)).start()`. Each thread creation takes 0.5–1 ms and allocates ~1 MB of stack. At 1,000 requests/second, you create and destroy 1,000 threads/second. At 10,000 concurrent connections, 10,000 threads consume 10 GB of stack space. Thread creation overhead becomes a significant fraction of request latency. The JVM crashes with `OutOfMemoryError: unable to create new native thread`.

**THE BREAKING POINT:**
Thread creation is not free. OS scheduling, stack allocation, JVM thread registration - these costs accumulate. A spike of 5,000 concurrent requests creates 5,000 threads simultaneously. The OS struggles to schedule them efficiently, context-switching overhead dominates, and actual I/O work slows down.

**THE INVENTION MOMENT:**
This is exactly why the Thread Pool pattern was created. Create N threads once. Route all tasks through a queue. Workers pick up tasks and process them. Thread creation cost is paid once at startup; the steady-state overhead is just task dispatch.

**EVOLUTION:**
Thread Pool Pattern became mainstream with Java 5's Executor
framework (2004), which standardised `ExecutorService`,
`ThreadPoolExecutor`, and `ScheduledExecutorService`. Before this,
developers hand-rolled thread pools with varying reliability.
The pattern's relevance is being transformed by Java 21 Virtual
Threads (Project Loom): virtual threads are so lightweight (less
than 1KB overhead vs. ~1MB per platform thread) that one-thread-
per-task becomes viable, potentially making thread pools for I/O-
bound tasks unnecessary. CPU-bound tasks still benefit from pools
sized to the physical core count.

---

### 📘 Textbook Definition

The **Thread Pool** pattern maintains a pool of pre-created worker threads that process tasks submitted to an internal queue. When a task is submitted, it enters the queue rather than spawning a new thread. Idle worker threads dequeue and execute tasks; when done, they return to waiting for the next task. The pool has a configured minimum and maximum thread count, a queue strategy, and a rejection policy for when the pool is saturated. Java's `ThreadPoolExecutor` implements this pattern with configurable `corePoolSize`, `maximumPoolSize`, `keepAliveTime`, `BlockingQueue`, and `RejectedExecutionHandler`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A fixed set of reusable workers take tasks from a queue - no thread creation per task.

**One analogy:**
> A fast food restaurant has a permanent kitchen crew (thread pool). When orders arrive (tasks), they go to the order queue. Available kitchen staff (idle threads) grab orders and cook. The restaurant never creates new permanent staff for a lunch rush - it queues orders. The staff size is set based on kitchen capacity, not current demand.

**One insight:**
Thread Pool's hidden power is bounded concurrency. The maximum pool size acts as a ceiling on simultaneous resource consumption. Without it, a burst of requests creates an unbounded number of threads, each consuming memory and competing for CPU - the pool's ceiling converts resource exhaustion into predictable queuing.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Thread creation is expensive; threads must be reused.
2. The number of concurrent threads must be bounded to prevent resource exhaustion.
3. Tasks arrive asynchronously and must not be lost during bursts.
4. Idle threads must not waste CPU (they must block, not spin).

**DERIVED DESIGN:**
Given invariant 1: worker threads loop forever: `while (running) { task = queue.take(); task.execute(); }`. Thread creation happens once at pool initialisation.

Given invariant 2: `maximumPoolSize` hard-caps threads. Given invariant 3: a `BlockingQueue` buffers tasks. Given invariant 4: `queue.take()` parks idle threads (no CPU spin).

`ThreadPoolExecutor` tuning: `corePoolSize` threads always alive; additional threads created up to `maximumPoolSize` when queue is full; excess threads die after `keepAliveTime`. Queue choice determines overflow behaviour: `ArrayBlockingQueue(N)` → bounded, rejects after N + maxPoolSize tasks; `LinkedBlockingQueue` → unbounded but risks OOM.

**THE TRADE-OFFS:**
**Gain:** Thread creation amortised over many tasks; bounded concurrency prevents resource exhaustion; backpressure via rejection policies; simple uniform interface (`submit(Runnable)`).
**Cost:** Fixed pool size requires upfront tuning; CPU-bound and I/O-bound workloads need different pool sizes; a slow task blocks a thread, reducing effective pool capacity; context-switching cost is non-zero even with pooling.

---

### 🧪 Thought Experiment

**SETUP:**
API server handles 500 requests/second. Each request does 50 ms of I/O. No thread pool.

**WHAT HAPPENS WITHOUT THREAD POOL:**
500 req/s × 50 ms each = 25 concurrent threads needed at steady state. But each request creates a new thread (500/second), each thread runs 50 ms then is destroyed. Thread creation/destruction cost: 500 × ~1 ms = 500 ms/second overhead - 1% CPU just for thread lifecycle. A 5× traffic spike: 2,500 threads created simultaneously, JVM hits OS thread limit, crash.

**WHAT HAPPENS WITH THREAD POOL:**
25 threads pre-created (`corePoolSize=25`). 500 tasks/second submitted to the pool. Each worker handles 20 tasks/second (1/50ms). 25 workers × 20 tasks = 500/second - perfect match. Zero thread creation overhead. A 5× spike: 2,500 tasks/second arrive. 475 tasks/second queue up. Queue drains as traffic normalises. No crash.

**THE INSIGHT:**
The pool converts "thread count proportional to load" into "thread count proportional to capacity." Queue depth signals when more consumers are needed - not as a crash, but as a metric.

---

### 🧠 Mental Model / Analogy

> Thread Pool is like a delivery company's driver fleet. The company has 20 permanent drivers (threads). Packages arrive at dispatch (task queue). Available drivers pick up packages and deliver them. The company doesn't hire new drivers for each package - drivers are reused. During peak season, the queue backs up; the company hires seasonal drivers (threads up to max pool size). Off-peak, seasonal drivers are let go (threads above corePoolSize time out and die).

- "Permanent drivers" → core pool threads
- "Seasonal drivers" → threads above coreSize, up to maxPoolSize
- "Delivery queue" → BlockingQueue of tasks
- "Package arrives" → `executor.submit(task)`
- "Driver picks up package" → worker calls `queue.take()`
- "Driver works independently" → task executed on worker thread

Where this analogy breaks down: delivery has per-driver physical limits (fuel, time). Thread pool workers are fungible - any task can go to any worker. There's no affinity between tasks and specific threads (unless using `ThreadLocal` data, which can create unexpected state).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Thread Pool is a group of permanent workers waiting for assignments. Instead of hiring a new worker for every task, you pass tasks to the existing team. When all workers are busy, tasks wait in a line.

**Level 2 - How to use it (junior developer):**
Use `Executors.newFixedThreadPool(n)` for simple cases. For production, use `new ThreadPoolExecutor(core, max, keepAlive, unit, queue, rejectionPolicy)` for explicit control. Submit tasks with `executor.submit(Runnable)` or `executor.submit(Callable)`. Shut down with `executor.shutdown()` followed by `executor.awaitTermination(timeout, unit)`. Never use `Executors.newCachedThreadPool()` in production - it creates unlimited threads under load.

**Level 3 - How it works (mid-level engineer):**
`ThreadPoolExecutor` task routing logic:
1. If active threads < `corePoolSize`: create new thread to run task
2. If core threads busy and queue not full: enqueue task
3. If queue full and threads < `maxPoolSize`: create new thread
4. If queue full and at max threads: apply rejection policy

This means threads beyond `corePoolSize` are only created when the queue is full - counter-intuitive. With an unbounded `LinkedBlockingQueue`, step 3 never occurs; `maxPoolSize` is effectively irrelevant with this queue type. Virtual threads (Java 21, Project Loom) change the model: a virtual thread is a lightweight JVM-managed thread, not an OS thread - `Executors.newVirtualThreadPerTaskExecutor()` creates one virtual thread per task at ~100 ns, eliminating the thread pool's primary motivation for I/O-bound workloads.

**Level 4 - Why it was designed this way (senior/staff):**
Thread Pool's optimal size is workload-dependent. CPU-bound work: pool size ≈ number of CPU cores (N_CPU). I/O-bound work: pool size >> N_CPU (threads are mostly waiting on I/O). The correct formula: `pool_size = N_CPU × (1 + wait_time / cpu_time)`. A web service with 90% I/O wait ratio on 8-core server needs ~80 threads. Getting this wrong is a common production failure: undersized pools cause request queuing and latency spikes; oversized pools cause context-switching overhead and memory pressure. Modern solution: Virtual Threads (Java 21) eliminate this tuning exercise for I/O-bound code - each request gets a virtual thread that parks during I/O without consuming an OS thread. Platform thread pools remain optimal for CPU-bound work.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────┐
│  THREAD POOL - THREADPOOLEXECUTOR INTERNALS        │
│                                                    │
│  submit(task)                                      │
│       ↓                                            │
│  ┌────────────────────────────────────────────┐    │
│  │ Active < coreSize?                         │    │
│  │   YES → create new thread                 │    │
│  │   NO  ↓                                   │    │
│  │ Queue not full?                            │    │
│  │   YES → enqueue                           │    │
│  │   NO  ↓                                   │    │
│  │ Threads < maxSize?                        │    │
│  │   YES → create new thread                 │    │
│  │   NO  → apply rejection policy           │    │
│  └────────────────────────────────────────────┘    │
│                                                    │
│  Worker Thread Loop:                               │
│  while (pool running):                             │
│    task = workQueue.take() ← blocks if empty       │
│    task.run()                                      │
│    thread returns to pool                          │
└────────────────────────────────────────────────────┘
```

**Rejection policies:**
- `AbortPolicy` (default): throw `RejectedExecutionException`
- `CallerRunsPolicy`: the calling thread executes the task (natural backpressure)
- `DiscardPolicy`: silently drop the task
- `DiscardOldestPolicy`: drop the oldest queued task, attempt resubmit

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
HTTP request arrives → DispatcherServlet
  → request wrapped as Runnable task
  → executor.submit(task)
             ← YOU ARE HERE (thread pool)
  → task queued in BlockingQueue
  → idle worker thread: task = queue.take()
  → worker executes: handleRequest(req)
  → worker returns HTTP response via callback
  → worker loops back to queue.take()
```

**FAILURE PATH:**
```
Queue full + pool at max capacity:
  → RejectedExecutionException thrown
  → caller receives 503 Service Unavailable
OR:
Worker thread throws uncaught exception:
  → task is removed from pool's active count
  → pool creates replacement thread (if below coreSize)
  → exception propagated to Future.get() caller
```

**WHAT CHANGES AT SCALE:**
At 100,000 req/s with 200 worker threads, task submission overhead (queue lock contention) becomes the bottleneck. `ForkJoinPool` uses work-stealing - each worker has its own deque, reducing shared queue contention. Project Loom (Java 21) virtual threads eliminate the OS thread cost entirely for I/O-bound work but still use carrier thread pools internally.

---

### 💻 Code Example

**Example 1 - Production ThreadPoolExecutor configuration:**
```java
// BAD: Executors.newCachedThreadPool() - unlimited threads
ExecutorService bad = Executors.newCachedThreadPool();
// Under load spike: creates 10,000+ threads → OOM

// GOOD: Explicit bounded pool
int coreThreads = Runtime.getRuntime().availableProcessors();
int maxThreads = coreThreads * 4; // I/O-bound estimate
int queueCapacity = 1000;

ThreadPoolExecutor executor = new ThreadPoolExecutor(
    coreThreads,                        // corePoolSize
    maxThreads,                         // maximumPoolSize
    60L, TimeUnit.SECONDS,              // keepAliveTime
    new ArrayBlockingQueue<>(queueCapacity), // bounded queue
    new ThreadFactory() {               // named threads
        private final AtomicInteger n =
            new AtomicInteger();
        @Override
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r,
                "worker-" + n.getAndIncrement());
            t.setDaemon(false);
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy() // backpressure
);

// Shutdown hook
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    executor.shutdown();
    try {
        if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
            executor.shutdownNow();
        }
    } catch (InterruptedException e) {
        executor.shutdownNow();
    }
}));
```

**Example 2 - Monitoring thread pool health:**
```java
// Expose metrics for thread pool health
@Scheduled(fixedRate = 5000)
void reportThreadPoolMetrics() {
    ThreadPoolExecutor pool = (ThreadPoolExecutor) executor;

    metrics.gauge("pool.active.threads",
        pool.getActiveCount());
    metrics.gauge("pool.queue.size",
        pool.getQueue().size());
    metrics.gauge("pool.pool.size",
        pool.getPoolSize());
    metrics.counter("pool.completed.tasks",
        pool.getCompletedTaskCount());

    // Alert on queue saturation
    double queueFill = (double) pool.getQueue().size()
        / (pool.getQueue().size()
           + pool.getQueue().remainingCapacity());
    if (queueFill > 0.8) {
        alertManager.fire("ThreadPool queue at "
            + (int)(queueFill*100) + "%");
    }
}
```

**Example 3 - Virtual Threads (Java 21) for I/O-bound:**
```java
// Java 21+: one virtual thread per task for I/O-bound work
// No pool size tuning needed - JVM manages scheduling
ExecutorService virtualExecutor =
    Executors.newVirtualThreadPerTaskExecutor();

// Each submitted task runs on a lightweight virtual thread
// Blocking I/O parks the virtual thread, not its carrier
for (Request req : requests) {
    virtualExecutor.submit(() -> {
        // This I/O blocks the virtual thread (not OS thread)
        Response r = httpClient.get(req.url());
        processResponse(r);
    });
}
// No OOM risk: virtual threads use heap, not OS thread stacks
```

---

### ⚖️ Comparison Table

| Strategy | Thread Creation | Concurrency Bound | Best For |
|---|---|---|---|
| **Thread Pool (fixed)** | Once at startup | Hard limit | Stable, known workloads |
| CachedThreadPool | Per task (cached) | Unbounded (risk OOM) | Bursty, short tasks only |
| ForkJoinPool | Fixed + work-steal | Bounded | CPU-bound recursive tasks |
| Virtual Threads (Java 21) | Lightweight per task | JVM-managed | I/O-bound, high concurrency |
| Single Thread Executor | Once | 1 | Sequential background tasks |

How to choose: use fixed ThreadPoolExecutor for server-side HTTP/DB work. Use ForkJoinPool for parallel computation. Use Virtual Threads for I/O-heavy concurrent tasks on Java 21+.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More threads always means more throughput | Context-switching overhead increases with thread count. CPU-bound work tops out at N_CPU threads; adding more hurts |
| `Executors.newFixedThreadPool(n)` is production-ready | It uses an unbounded `LinkedBlockingQueue` - tasks queue indefinitely, hiding backpressure. Use explicit `ThreadPoolExecutor` with bounded queue |
| ThreadPool eliminates all thread creation cost | Core threads are pre-created; threads above corePoolSize are still created on demand when the queue is full |
| CallerRunsPolicy is always safe | When the calling thread is an HTTP handler, CallerRunsPolicy blocks the handler thread - reducing HTTP throughput. Intentional backpressure, but with that cost |
| Shutting down the executor stops it immediately | `shutdown()` stops accepting new tasks but lets running tasks finish. `shutdownNow()` interrupts running tasks - tasks must check `Thread.interrupted()` to honour this |

---

### 🚨 Failure Modes & Diagnosis

**1. Thread Pool Starvation - All Threads Blocked**

**Symptom:** Application appears hung. No tasks complete. `queue.size()` grows. Thread dump shows all worker threads blocked on the same resource (DB, external service, another async operation).

**Root Cause:** All N threads are simultaneously blocking on I/O. No threads available for new tasks. Pool size < concurrent blocking requests.

**Diagnostic:**
```bash
jstack <PID> | grep -A 10 "worker-"
# If all worker threads show "WAITING" on I/O:
# Pool size too small for I/O wait ratio
```

**Fix:**
Increase pool size OR reduce blocking duration OR use async I/O with callbacks:
```java
// Calculate: size = cores × (1 + wait_time / cpu_time)
// 8 cores, 90% wait: 8 × (1 + 9) = 80 threads
int optimalSize = coreCount * (1 + waitCpuRatio);
```

**Prevention:** Monitor `activeCount / poolSize` ratio. If consistently > 90%, pool is undersized.

---

**2. Unbounded Queue - Silent OOM Accumulation**

**Symptom:** Memory usage grows steadily over hours. OOM crash occurs. Heap dump shows millions of `Runnable` task objects in the executor's queue.

**Root Cause:** `Executors.newFixedThreadPool()` or `new LinkedBlockingQueue()` without capacity. Tasks arrive faster than consumed - queue grows unbounded.

**Diagnostic:**
```bash
# Heap dump analysis
jmap -dump:live,format=b,file=heap.bin <PID>
# In jvisualvm or Eclipse MAT:
# Look for Runnable/Callable instances in millions
```

**Fix:**
```java
// Replace unbounded queue
new LinkedBlockingQueue<>() // BAD: unbounded

// with bounded queue + rejection policy
new ArrayBlockingQueue<>(capacity) // GOOD: bounded
```

**Prevention:** Never use `LinkedBlockingQueue` without capacity in production. Set queue size = max tasks you can hold in memory.

---

**3. ThreadLocal Leak - Data Bleeds Between Tasks**

**Symptom:** Security context from Request A appears in Request B. User session data bleeds between requests. Intermittent, hard to reproduce.

**Root Cause:** A task sets a `ThreadLocal` value and does not clear it in a `finally` block. The thread returns to the pool with the value still set. The next task on that thread sees stale data.

**Diagnostic:**
```java
// Add instrumentation to thread pool
executor.submit(() -> {
    System.out.println("Before: " +
        SecurityContext.getCurrent()); // should be null
    if (SecurityContext.getCurrent() != null) {
        System.err.println("LEAK DETECTED");
    }
});
```

**Fix:**
```java
// Always clear ThreadLocal in finally:
try {
    SecurityContext.set(user);
    doWork();
} finally {
    SecurityContext.clear(); // MUST clear before returning
}
```

**Prevention:** Code review rule: every `ThreadLocal.set()` must have a corresponding `remove()` in a `finally` block. Use wrapper tasks that enforce cleanup.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Thread` - Thread Pool manages threads; understanding OS thread cost, stack size, and context switching explains why pooling is needed
- `BlockingQueue` - the queue inside ThreadPoolExecutor; `put()`/`take()` semantics drive pool behaviour
- `Producer-Consumer` - Thread Pool is a specialisation of Producer-Consumer: submitters are producers, worker threads are consumers

**Builds On This (learn these next):**
- `ForkJoinPool` - specialised pool with work-stealing for recursive parallel tasks; `parallelStream()` and `CompletableFuture` use it internally
- `Virtual Threads (Project Loom)` - Java 21 alternative for I/O-bound workloads; eliminates thread pool size tuning
- `Bulkhead Pattern` - uses separate thread pools per resource to isolate failure domains (e.g., separate pool for DB calls and HTTP calls)

**Alternatives / Comparisons:**
- `Object Pool` - same reuse principle applied to objects instead of threads; JDBC connection pools are Object Pools
- `Scheduler Pattern` - extends Thread Pool with time-based task dispatch; `ScheduledThreadPoolExecutor` is the Java implementation
- `Reactive Programming (Reactor/RxJava)` - replaces thread pools for I/O-bound work with non-blocking event loops and schedulers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Pre-allocated reusable worker threads      │
│              │ executing tasks from a shared queue       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Per-task thread creation wastes ~1ms;     │
│ SOLVES       │ unbounded threads cause OOM crashes       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pool size must match workload type:       │
│              │ CPU-bound ≈ cores; I/O-bound >> cores     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Short or medium tasks arrive frequently;  │
│              │ thread creation overhead is measurable    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Java 21+, I/O-bound: use virtual threads; │
│              │ tasks are very long-running (one task per │
│              │ thread then is more readable)             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Thread reuse efficiency vs upfront tuning │
│              │ complexity and fixed capacity ceiling     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hire once, work forever; queue the       │
│              │  overflow."                               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ForkJoinPool → Virtual Threads →          │
│              │ Bulkhead Pattern                          │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Pre-allocate a fixed set of reusable workers. Distribute work
items to idle workers. When bounded, the pool becomes a natural
rate limiter -- work cannot exceed the pool's capacity of workers.

**Where else this pattern appears:**
- **HTTP server connection handlers (Nginx worker processes):**
  Each `worker_process` in Nginx is a fixed pool member;
  connection requests are distributed across the pool.
- **Database server connection handler threads:** PostgreSQL
  pre-forks a fixed number of backend processes; connection
  requests block when all processes are busy.
- **Operating system interrupt handlers:** Kernel bottom-half
  handlers are pre-allocated kernel threads that process
  deferred interrupt work -- a kernel-level thread pool.

---

### 💡 The Surprising Truth

Java 21's Virtual Threads do not eliminate the Thread Pool
Pattern for CPU-bound work -- they eliminate it only for I/O-
bound work. A CPU-bound task on a virtual thread still requires
a platform thread to execute; scheduling 10,000 virtual threads
on 8 CPU cores still throttles to 8 simultaneously running tasks.
The confusion arises because "thread" means two different things:
a lightweight concurrency unit (virtual thread) and a CPU execution
slot (platform thread/carrier thread). Thread pools for CPU-bound
work will remain -- they just become pools of carrier threads
rather than application threads.
---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application uses a `ThreadPoolExecutor` with `corePoolSize=10`, `maxPoolSize=50`, `queue=ArrayBlockingQueue(100)`, and `CallerRunsPolicy`. Under normal load (50 req/s), everything is fine. During a traffic spike (500 req/s), the following sequence occurs: 10 threads busy → queue fills to 100 → 40 more threads created → queue still filling → CallerRunsPolicy activates. Trace exactly what happens to the HTTP server's Tomcat threads that call `submit()` when CallerRunsPolicy runs, and explain why this configuration under extreme load could cause Tomcat's own connection acceptance to stop working.

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A high-throughput service (Java 21) processes 50,000 tasks/second. Each task does 10 ms of database I/O. An architect proposes two options: (A) `ThreadPoolExecutor` with 500 threads, or (B) `newVirtualThreadPerTaskExecutor()`. Calculate the memory usage for option A (500 OS threads × 1 MB stack). Then explain how option B handles the same 50,000 concurrent tasks in terms of memory and OS thread usage, and identify one class of workload where option A would still outperform option B.



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A Spring Boot application uses a
`ThreadPoolTaskExecutor` with `corePoolSize=10`,
`maxPoolSize=50`, `queueCapacity=100`. Under a traffic spike:
300 concurrent requests arrive. Trace the exact sequence of
how the task executor handles them, identify when the 301st
request arrives and what happens to it, and explain how
to tune the pool for a service where tasks are 90% I/O wait.

*Hint: The How It Works diagram and the Failure Modes section
on RejectedExecutionException cover this scenario. The 90% I/O
wait ratio means Little's Law applies: optimal pool size is
much larger than CPU count.*
