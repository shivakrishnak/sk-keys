---
layout: default
title: "ThreadPoolExecutor"
parent: "Java Concurrency"
nav_order: 351
permalink: /java-concurrency/threadpoolexecutor/
number: "351"
category: Java Concurrency
difficulty: ★★★
depends_on: ExecutorService, BlockingQueue, Thread, Semaphore
used_by: Custom Thread Pools, Backpressure, Rejection Policies
tags: #java, #concurrency, #thread-pool, #executor, #advanced
---

# 351 — ThreadPoolExecutor

`#java` `#concurrency` `#thread-pool` `#executor` `#advanced`

⚡ TL;DR — ThreadPoolExecutor is the full-control implementation behind `Executors` factory pools — exposing corePoolSize, maximumPoolSize, keepAlive, work queue, thread factory, and rejection policy for precise production tuning.

| #351 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | ExecutorService, BlockingQueue, Thread, Semaphore | |
| **Used by:** | Custom Thread Pools, Backpressure, Rejection Policies | |

---

### 📘 Textbook Definition

`java.util.concurrent.ThreadPoolExecutor` is the concrete class implementing `ExecutorService` that all `Executors` factory methods delegate to. Parameters: **corePoolSize** (threads always kept alive), **maximumPoolSize** (upper bound), **keepAliveTime** (how long surplus threads stay idle), **workQueue** (task buffer between core and max), **threadFactory** (for naming/daemon/priority), **rejectedExecutionHandler** (action when work queue is full and max threads reached). Five built-in rejection policies: AbortPolicy (default), CallerRunsPolicy, DiscardPolicy, DiscardOldestPolicy.

---

### 🟢 Simple Definition (Easy)

`Executors.newFixedThreadPool(10)` creates a hidden `ThreadPoolExecutor(10, 10, ...)`. `ThreadPoolExecutor` is the explicit version: you set EVERY dial — minimum threads, maximum threads, idle timeout, queue size, what to do when overwhelmed. It's the full control knob that `Executors` hides from you.

---

### 🔵 Simple Definition (Elaborated)

The `Executors` factory methods are convenience wrappers — but they use dangerous defaults for production: both `newFixedThreadPool` and `newCachedThreadPool` use unbounded queues or unbounded thread counts, which can silently cause OOM under load. `ThreadPoolExecutor` forces you to choose a bounded queue, a maximum thread count, and a rejection policy — this is exactly what a production service needs for predictable behaviour under pressure.

---

### 🔩 First Principles Explanation

```
Thread creation decision tree (ThreadPoolExecutor logic):

  Task submitted →
    Current threads < corePoolSize?
      YES → create new thread (even if idle threads exist)
    Current threads >= corePoolSize?
      Queue not full?
        YES → add to queue
      Queue full AND current threads < maximumPoolSize?
        YES → create new thread
      Queue full AND at maximum threads?
        → invoke RejectedExecutionHandler

Thread lifecycle:
  Core threads: stay alive (idle) indefinitely (keepAliveTime irrelevant unless allowCoreThreadTimeOut=true)
  Surplus threads (> core): killed after keepAliveTime of idle

Queue effects:
  SynchronousQueue (CachedPool):   no buffering → forces new thread per task
  LinkedBlockingQueue (FixedPool): unbounded buffer → core never grows past core size
  ArrayBlockingQueue(N):           bounded buffer → triggers max threads when full → triggers rejection when at max
```

**Why size matters:**

```
Under 1000 req/s burst with FixedThreadPool(10, unbounded queue):
  First 10 tasks run → thousands queue up → OOM after minutes
  No backpressure: callers never see "system busy"

With ThreadPoolExecutor(10, 50, 60s, ArrayBlockingQueue(200), CallerRunsPolicy):
  10 core threads running
  Queue fills to 200
  Up to 50 threads created
  When 50 threads + 200 queue all busy → CallerRunsPolicy runs task in caller thread
  → Caller blocked → natural backpressure
```

---

### 🧠 Mental Model / Analogy

> A restaurant with kitchen staff. `corePoolSize` = permanent chefs always on duty. `workQueue` = order tickets backing up. `maximumPoolSize` = temporary chefs called in during rush. `keepAliveTime` = how long temps stay after the rush. `RejectedExecutionHandler` = "sorry, kitchen closed for new orders" (or "customer makes their own food" with `CallerRunsPolicy`).

---

### ⚙️ How It Works — Key Parameters

```java
new ThreadPoolExecutor(
    int  corePoolSize,       // min threads always alive
    int  maximumPoolSize,    // max threads total
    long keepAliveTime,      // idle time before surplus thread dies
    TimeUnit unit,
    BlockingQueue<Runnable> workQueue,   // task buffer
    ThreadFactory threadFactory,         // name/priority/daemon control
    RejectedExecutionHandler handler     // action after queue + max threads full
);

Rejection policies:
  AbortPolicy (default)    → throws RejectedExecutionException
  CallerRunsPolicy         → runs task in the SUBMITTING thread (natural backpressure)
  DiscardPolicy            → silently drops the task (data loss!)
  DiscardOldestPolicy      → drops oldest queued task, retries new one (LIFO pressure)
  Custom handler           → log + metric + graceful degradation
```

---

### 🔄 How It Connects

```
ThreadPoolExecutor
  ├─ Created by → Executors.newFixedThreadPool / newCachedThreadPool (hidden)
  ├─ Exposes    → coreSize, maxSize, keepAlive, queue, threadFactory, handler
  ├─ Monitors   → getActiveCount(), getQueue().size(), getCompletedTaskCount()
  ├─ Extends    → AbstractExecutorService → ExecutorService
  └─ Used by    → Spring's ThreadPoolTaskExecutor (wrapper around TPE)
```

---

### 💻 Code Example

```java
// Production-grade pool: bounded, named, rejection policy
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    10,                                   // core: 10 always alive
    50,                                   // max: 50 under burst
    60L, TimeUnit.SECONDS,               // surplus threads die after 60s idle
    new ArrayBlockingQueue<>(500),        // buffer 500 tasks
    new ThreadFactory() {
        private final AtomicInteger count = new AtomicInteger(0);
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r, "worker-" + count.incrementAndGet());
            t.setDaemon(true);           // don't prevent JVM exit
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy()  // caller thread runs task on overflow
);
```

```java
// Monitoring the pool — expose via metrics
ScheduledExecutorService monitor = Executors.newSingleThreadScheduledExecutor();
monitor.scheduleAtFixedRate(() -> {
    System.out.printf(
        "Pool: active=%d, queued=%d, completed=%d, poolSize=%d%n",
        executor.getActiveCount(),
        executor.getQueue().size(),
        executor.getCompletedTaskCount(),
        executor.getPoolSize()
    );
}, 0, 5, TimeUnit.SECONDS);
```

```java
// Graceful shutdown
executor.shutdown();
try {
    if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
        List<Runnable> pending = executor.shutdownNow();
        log.warn("Forced shutdown; {} tasks not started", pending.size());
        if (!executor.awaitTermination(10, TimeUnit.SECONDS))
            log.error("Pool did not terminate");
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
    Thread.currentThread().interrupt();
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Extra threads are created before the queue fills | Extra threads only created when QUEUE IS FULL (and below max) |
| `Executors.newFixedThreadPool` is safe for production | Uses unbounded `LinkedBlockingQueue` → OOM under sustained overload |
| CallerRunsPolicy is always the right choice | Correct for backpressure; wrong if the caller thread must remain responsive |
| `getActiveCount()` equals running task count | Approximate — may include threads starting/finishing |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Unbounded queue causes silent OOM (Executors default)**

```java
// ❌ From Executors.newFixedThreadPool:
new ThreadPoolExecutor(10, 10, 0L, MILLISECONDS, new LinkedBlockingQueue<>()); // unbounded!
// Under load: tasks pile up silently → heap exhausted → OOM

// ✅ Always use bounded queue in production
new ThreadPoolExecutor(10, 50, 60L, SECONDS, new ArrayBlockingQueue<>(1000),
    new ThreadPoolExecutor.CallerRunsPolicy());
```

**Pitfall 2: maximumPoolSize never reached because queue fills slowly**

```java
// With unbounded queue: corePoolSize threads run; extras NEVER created
// max threads only kick in AFTER queue is full
// With ArrayBlockingQueue(10000) + corePoolSize=4, maxPoolSize=50:
// → 4 threads run; up to 10000 tasks queue; only AFTER 10000 queued do extra threads spawn
// If traffic spike fills queue → extra threads too late → latency spike
// Tune: smaller queue + bigger max; or use SynchronousQueue for instant burst scaling
```

---

### 🔗 Related Keywords

- **[ExecutorService](./074 — ExecutorService.md)** — the interface TPE implements
- **[BlockingQueue](./081 — BlockingQueue.md)** — the work queue inside TPE
- **[Thread Interruption](./090 — Thread Interruption.md)** — `shutdownNow()` interrupts running tasks
- **Spring ThreadPoolTaskExecutor** — Spring wrapper with bean lifecycle integration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Full-control pool: core/max/keepAlive/queue/ │
│              │ factory/handler — never use Executors in prod │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Production services: need bounded queue +     │
│              │ named threads + explicit rejection policy     │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Never use Executors.newFixed/CachedThreadPool │
│              │ in production — both use dangerous defaults   │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Executors hides the dials —                  │
│              │  ThreadPoolExecutor exposes them all"         │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ BlockingQueue sizing → CallerRunsPolicy →     │
│              │ Virtual Threads → Spring TaskExecutor         │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** With `ThreadPoolExecutor(4, 20, 60s, ArrayBlockingQueue(100))`: at what point are threads 5–20 created? What must happen to trigger their creation? Why don't they get created immediately when the pool is busy?

**Q2.** `CallerRunsPolicy` runs the rejected task in the submitting thread. If the submitter is an HTTP request handler thread (Tomcat NIO thread), what is the effect on the server's ability to accept new connections while the task runs? Is this desirable?

**Q3.** How would you implement a custom `RejectedExecutionHandler` that publishes a metric, logs a warning, and then falls back to `CallerRunsPolicy` behaviour?

