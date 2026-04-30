---
layout: default
title: "ScheduledExecutorService"
parent: "Java Concurrency"
nav_order: 93
permalink: /java-concurrency/scheduledexecutorservice/
number: "093"
category: Java Concurrency
difficulty: ★★☆
depends_on: ExecutorService, Thread, Runnable vs Callable
used_by: Health Checks, Polling, Cache Refresh, Cleanup Tasks
tags: #java, #concurrency, #scheduled, #timer, #periodic
---

# 093 — ScheduledExecutorService

`#java` `#concurrency` `#scheduled` `#timer` `#periodic`

⚡ TL;DR — ScheduledExecutorService extends ExecutorService to run tasks after a delay or at fixed intervals — replacing error-prone `Timer`/`TimerTask` with a thread-safe, recoverable scheduler backed by a thread pool.

| #093 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ExecutorService, Thread, Runnable vs Callable | |
| **Used by:** | Health Checks, Polling, Cache Refresh, Cleanup Tasks | |

---

### 📘 Textbook Definition

`java.util.concurrent.ScheduledExecutorService` extends `ExecutorService` with three scheduling methods: `schedule(Callable, delay, unit)` — run once after a delay; `scheduleAtFixedRate(Runnable, initialDelay, period, unit)` — run at regular intervals regardless of execution time; `scheduleWithFixedDelay(Runnable, initialDelay, delay, unit)` — run with a fixed gap between the END of one execution and the START of the next. Returns `ScheduledFuture<?>` for cancellation. Unlike `Timer`, exceptions in tasks don't silently kill the scheduler.

---

### 🟢 Simple Definition (Easy)

`ScheduledExecutorService` is a scheduled task runner: "Run this task in 5 seconds" (`schedule`), "Run this every 10 seconds" (`scheduleAtFixedRate`), or "Wait 10 seconds after the last run finishes, then run again" (`scheduleWithFixedDelay`). Far better than `Timer` — thread-safe, exception-safe, cancellable.

---

### 🔵 Simple Definition (Elaborated)

`java.util.Timer` was the Java 1.3 way to schedule tasks — it uses a single background thread, so an exception in one task kills ALL scheduled tasks silently. `ScheduledExecutorService` fixes both: it uses a thread pool (configurable size), and if a task throws an unchecked exception, only that task's future scheduling is cancelled — other tasks continue. The `ScheduledFuture` return value lets you cancel a task programmatically.

---

### 🔩 First Principles Explanation

```
Timer problems (Java 1.3):
  Single thread: if task A takes 60s, task B is delayed too
  Exception: task throws RuntimeException → Timer thread dies
    → ALL future tasks silently stop running
    → No error logged (unless you add Thread.UncaughtExceptionHandler)
  Not thread-safe: TimerTask methods aren't synchronized

ScheduledExecutorService solutions:
  Pool: multiple threads → tasks don't block each other
  Exception: task throws → task's ScheduledFuture is cancelled
    → Other tasks continue normally
    → Future.get() propagates the exception
  Thread-safe: inherits ExecutorService guarantees

scheduleAtFixedRate vs scheduleWithFixedDelay:
  Rate:  period measured from START of execution
    |--task(2s)--|     |--task(2s)--|
    0     2      5     5     7     10    (period=5s)
    Task always starts at 0, 5, 10... regardless of duration

  Delay: period measured from END of execution
    |--task(2s)--|     |--task(2s)--|
    0     2      7     7     9     14    (delay=5s)
    Next start = previous end + 5s → gaps grow if task is slow
```

---

### 🧠 Mental Model / Analogy

> `scheduleAtFixedRate` is a meeting that starts every Monday at 9am regardless of how long the previous meeting ran. `scheduleWithFixedDelay` is a meeting that starts 5 days after the last one ended — if the last meeting ran long, the next is further away. `Timer` is a meeting organiser who quits if anyone sneezes.

---

### ⚙️ How It Works

```
ScheduledExecutorService exec =
    Executors.newScheduledThreadPool(int corePoolSize);

Methods:
  ScheduledFuture<?> schedule(Runnable task, long delay, TimeUnit unit)
     → run ONCE after 'delay'

  ScheduledFuture<?> schedule(Callable<V> task, long delay, TimeUnit unit)
     → run ONCE after 'delay', returns result via Future<V>

  ScheduledFuture<?> scheduleAtFixedRate(
     Runnable task, long initialDelay, long period, TimeUnit unit)
     → first execution after initialDelay
     → subsequent: every 'period' from START of previous
     → if task takes LONGER than period: next execution starts immediately after

  ScheduledFuture<?> scheduleWithFixedDelay(
     Runnable task, long initialDelay, long delay, TimeUnit unit)
     → first execution after initialDelay
     → subsequent: 'delay' after END of previous execution

  ScheduledFuture.cancel(boolean mayInterruptIfRunning)
     → cancel scheduled task; returns false if already completed
```

---

### 🔄 How It Connects

```
ScheduledExecutorService
  ├─ extends ExecutorService → also has submit(), execute(), shutdown()
  ├─ vs Timer → thread-safe, exception-safe, multi-threaded, cancellable
  ├─ scheduleAtFixedRate → rate limited (e.g. poll every 5s exact)
  ├─ scheduleWithFixedDelay → gap-based (e.g. 5s after last completion)
  └─ Spring: @Scheduled → Spring wrapper over ScheduledExecutorService
```

---

### 💻 Code Example

```java
// One-time delayed task
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
scheduler.schedule(
    () -> System.out.println("Delayed task executed"),
    5, TimeUnit.SECONDS
);
```

```java
// Health check: run every 30 seconds (fixed rate)
ScheduledFuture<?> healthCheck = scheduler.scheduleAtFixedRate(
    () -> {
        try { pingDatabase(); }
        catch (Exception e) { log.warn("DB health check failed", e); }
        // Exception caught → task continues scheduling
    },
    0, 30, TimeUnit.SECONDS  // starts immediately (0 delay), then every 30s
);

// Cancel health check on shutdown
healthCheck.cancel(false); // don't interrupt if currently running
```

```java
// Cache refresh: fixed delay (wait 60s after last refresh finishes)
scheduler.scheduleWithFixedDelay(
    () -> cache.refresh(),  // may take variable time
    0, 60, TimeUnit.SECONDS
    // If refresh takes 10s, next refresh starts at second 70
    // Never overlaps itself
);
```

```java
// Propagate exceptions — future.get() reveals them
ScheduledFuture<?> future = scheduler.schedule(
    () -> { throw new RuntimeException("task failed"); },
    1, TimeUnit.SECONDS
);

try {
    future.get();  // blocks until completion
} catch (ExecutionException e) {
    System.err.println("Task threw: " + e.getCause());
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Exception in scheduled task stops all tasks | Only that task's future scheduling stops; other tasks continue |
| `scheduleAtFixedRate` always starts exactly on time | If thread pool is full or task takes longer than period, execution is delayed |
| `cancel()` stops a currently-running task | `cancel(false)` won't interrupt; `cancel(true)` interrupts — and task must respond |
| Shutdown is automatic | Must call `scheduler.shutdown()` or JVM won't exit (scheduler thread keeps it alive) |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Exception silently cancels periodic task**

```java
scheduler.scheduleAtFixedRate(() -> {
    processData(); // throws RuntimeException
}, 0, 5, TimeUnit.SECONDS);
// After first exception: task silently stops scheduling — no log!
// System appears to work (no crash) but periodic task stopped

// Fix: wrap in try/catch
scheduler.scheduleAtFixedRate(() -> {
    try { processData(); }
    catch (Exception e) { log.error("Scheduled task failed", e); }
}, 0, 5, TimeUnit.SECONDS);
```

**Pitfall 2: Not calling shutdown() — pool threads keep JVM alive**

```java
ScheduledExecutorService s = Executors.newScheduledThreadPool(1);
// program logic ends, but JVM stays alive — scheduler thread running
// Fix: always shutdown in shutdown hook or service stop method
Runtime.getRuntime().addShutdownHook(new Thread(s::shutdown));
```

---

### 🔗 Related Keywords

- **[ExecutorService](./074 — ExecutorService.md)** — parent interface
- **[Thread Interruption](./090 — Thread Interruption.md)** — `cancel(true)` uses interruption
- **[Future & CompletableFuture](./075 — Future and CompletableFuture.md)** — `ScheduledFuture` extends Future
- **Spring @Scheduled** — declarative scheduling backed by ScheduledExecutorService

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Thread-safe, exception-safe task scheduler;  │
│              │ once, at fixed rate, or with fixed delay     │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Periodic tasks: health checks, cache refresh, │
│              │ polling, cleanup, metrics flush               │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Never use Timer/TimerTask — use this instead; │
│              │ long-running tasks → use larger pool size     │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Timer that doesn't die on exception;         │
│              │  schedule once, at rate, or after delay"      │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ @Scheduled (Spring) → Quartz Scheduler →      │
│              │ ScheduledFuture.cancel() → ForkJoinPool       │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `scheduleAtFixedRate` with period=5s: a task takes 8 seconds. What happens? Does the next execution start at second 5 or second 8? What if the pool has multiple threads?

**Q2.** You need a scheduled task that should NEVER overlap itself (next execution must wait for current to finish). Which method — `scheduleAtFixedRate` or `scheduleWithFixedDelay` — guarantees this, and why?

**Q3.** Spring's `@Scheduled(fixedRate = 5000)` and `@Scheduled(fixedDelay = 5000)` map directly to the two scheduling modes. What thread pool does Spring use by default? How would you configure a custom executor?

