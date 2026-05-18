---
id: DPT-034
title: Scheduler Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-033
used_by: DPT-064
related: DPT-033, DPT-035, DPT-036, DPT-034
tags:
  - pattern
  - concurrency
  - advanced
  - scheduling
  - timer
  - cron
  - delayed-execution
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/design-patterns/scheduler/
---

⚡ TL;DR - Scheduler Pattern executes tasks at specified
future times or recurring intervals, decoupling task
definition from execution timing and providing a single
control point for all time-triggered work in the system.

| #34 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-033 | |
| **Used by:** | DPT-064 | |
| **Related:** | DPT-033, DPT-035, DPT-036 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Three different background tasks in a Spring service:
(1) purge old sessions every 30 minutes,
(2) send digest emails every day at 8 AM,
(3) refresh a config cache every 5 minutes.

**NAIVE SOLUTIONS:**
- `Thread.sleep(1_800_000)` loops - drift, no error handling,
  cannot be monitored, hard to shut down.
- `java.util.Timer` - single background thread, one slow
  task blocks all others, no thread pool, poor exception
  handling.
- Manually creating `ScheduledExecutorService` instances
  per task - no central visibility, no cluster coordination.

**THE DEEPER PROBLEM:**
Three scheduling implementations scattered in three
service classes. When the session purge task throws an
exception: the `Timer` thread dies, silently stopping
ALL scheduled tasks in the JVM. No one notices until
sessions accumulate.

**THE INVENTION MOMENT:**
Scheduler Pattern: a central scheduler holds a priority
queue of future tasks sorted by next execution time.
A scheduling thread dequeues the earliest task, waits
until its time arrives, executes it (on a worker thread
pool), and re-enqueues it with the next run time.
Exceptions in one task do not affect others. Central
visibility. Configurable thread pool. Back-pressure.

**EVOLUTION:**
Java's `ScheduledExecutorService` (and its implementation
`ScheduledThreadPoolExecutor`). Spring's `@Scheduled`
annotation powered by `TaskScheduler`. Quartz Scheduler
(distributed, persistent jobs). Apache Airflow and
Apache Flink for workflow scheduling.

---

### 📘 Textbook Definition

The **Scheduler Pattern** is a concurrency design pattern
that defers and controls the timing of task execution.
A Scheduler maintains an ordered collection (typically
a priority queue or delay queue) of tasks with their
scheduled execution times. A scheduling thread monitors
the queue and dispatches tasks to worker threads when
their time arrives. The pattern decouples the decision
of WHEN a task executes from the task's own logic.
Recurring tasks are re-enqueued after each execution
with the next scheduled time. The Scheduler provides
a single control point for all time-triggered work.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Scheduler Pattern is a priority queue of "run this task
at this time" entries, with a dispatch thread that
fires tasks at the right moment.

**One analogy:**
> An airport flight schedule board. Each flight (task)
> has a departure time. The board (scheduler priority queue)
> is sorted by next departure. The gate agent (scheduling
> thread) checks the board, when the departure time arrives
> calls the boarding crew (worker thread). After boarding
> (task execution): the next day's same-flight time is
> added back (recurring schedule). One agent, many flights,
> no manual "check every minute" needed.

**One insight:**
The critical implementation detail: the scheduling thread
does NOT poll every millisecond. It sleeps until the
next task's scheduled time, wakes up, fires the task,
then recalculates the next sleep duration. This is
`DelayQueue.take()` in Java: the thread blocks until
the earliest item's delay expires.

---

### 🔩 First Principles Explanation

**CORE MECHANISM:**
```
Priority queue: [(task, time)] sorted by time
Scheduling thread:
  while (running) {
      (task, time) = queue.peek()    // nearest future task
      sleepUntil(time)               // efficient blocking
        wait
      queue.poll()
      workerPool.submit(task)        // execute on worker
        thread
      if (recurring) {
          queue.add(task, nextTime)  // re-enqueue
      }
  }
```

**JAVA IMPLEMENTATION:**
`ScheduledThreadPoolExecutor` uses a `DelayQueue<ScheduledFutureTask>`.
`DelayQueue.take()` blocks until the earliest element's
delay reaches zero. Worker threads execute the task.
For `scheduleAtFixedRate`: next run = lastScheduled + period.
For `scheduleWithFixedDelay`: next run = lastFinish + delay.

**FIXED RATE VS FIXED DELAY:**
- `scheduleAtFixedRate(task, initial, period)`:
  Next run = previous scheduled start + period.
  If task takes longer than period: tasks pile up.
  Use for: strict interval requirements (every 5 min,
  not "5 min after last run").
- `scheduleWithFixedDelay(task, initial, delay)`:
  Next run = previous completion + delay.
  Gap between tasks is always `delay` regardless of
  task duration. Use for: "wait N time between runs."

**TRADE-OFFS:**

**Gain:** Decouples timing from task logic. Reliable
recurring execution. Exception isolation (one task failing
does not stop others - unlike `Timer`). Central visibility
and control.

**Cost:** In-JVM scheduler (not persistent): tasks lost
on restart. Not cluster-aware: in multiple instances,
all run the same scheduled tasks (duplication). For
distributed scheduling: use Quartz (DB-backed), Spring
Batch, or a dedicated scheduler service.

---

### 🧪 Thought Experiment

**SETUP:**
Microservice that purges expired tokens, sends weekly
reports, and refreshes a circuit-breaker status cache.
Three tasks, different intervals, all need to survive
individual failures.

**`Timer` (old API):**
Single thread. Task 1 throws uncaught exception:
`TimerThread` thread dies. Tasks 2 and 3 never run again.
No one notices for days.

**`ScheduledExecutorService`:**
Thread pool. Task 1 throws exception: the exception is
captured in the `ScheduledFuture`; the task's re-scheduling
STOPS (this is a common gotcha). Tasks 2 and 3 continue.
Fix: wrap task body in try/catch.

---

### 🧠 Mental Model / Analogy

> Scheduler is an ALARM CLOCK RACK. Each alarm (task)
> is set for its next ring time. The alarm controller
> (scheduling thread) scans the rack, detects the nearest
> alarm time, waits until then (efficient sleep, not
> constant checking), fires that alarm (submits to thread
> pool), then resets it for the next ring (recurring task).
> Multiple alarms can ring simultaneously (different worker
> threads handle them). One broken alarm (task exception)
> does not prevent others from ringing.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Scheduler Pattern is a way to run code at specific times
or on a schedule (every 5 minutes, every day at midnight).
Instead of each piece of code managing its own timing,
a central scheduler handles when things run.

**Level 2 - How to use it (junior developer):**
Java: use `ScheduledExecutorService` (never `Timer`).
Spring: `@Scheduled(cron = "0 0 8 * * MON-FRI")` or
`@Scheduled(fixedRate = 300_000)`. Always wrap task
bodies in try/catch to prevent re-scheduling suppression.

**Level 3 - How it works (mid-level engineer):**
`ScheduledThreadPoolExecutor` (backing Spring's `TaskScheduler`)
uses `DelayQueue<ScheduledFutureTask>`. When a task is
scheduled, a `ScheduledFutureTask` is created with the
execution time as the delay. Worker threads call
`queue.take()` which blocks until the delay expires.
When the delay reaches zero: `take()` returns the task,
the worker runs it. For `fixedRate`: after execution,
the task's delay is reset to `nextExecution = lastScheduled
+ period` and re-added to the queue. For `fixedDelay`:
reset to `nextExecution = now + delay`.
CRITICAL GOTCHA: If a `@Scheduled` task throws an unchecked
exception, Spring re-throws it, and `ScheduledExecutorService`
does NOT re-schedule the task. The task silently stops
running. Always: `try { /* task */ } catch (Exception e)
{ log.error("...", e); }`.

**Level 4 - Why it was designed this way (senior/staff):**
Spring's `@Scheduled` + `ScheduledTaskRegistrar` is the
standard for single-instance scheduling. For clustered
environments (multiple service instances): a single
`@Scheduled` method runs on ALL instances simultaneously.
This causes: duplicate emails sent, duplicate DB operations,
race conditions in purge jobs. Solutions:
- **ShedLock**: distributed lock before task body.
  Only the instance that acquires the lock runs the task.
- **Quartz**: cluster-aware scheduler with DB-backed
  job store. One node in the cluster runs each job.
- **Spring Batch + Partitioning**: divide work across
  instances, each processes a partition.
The Scheduler Pattern in distributed systems becomes
a Leader Election problem (DPT-088): only the leader
runs the scheduled task; followers skip it.

**Level 5 - Mastery (distinguished engineer):**
Scheduling is fundamentally a consensus problem in distributed
systems: who runs what, when. Single-instance: trivial
(one scheduler, no coordination). Multi-instance: requires
distributed consensus. The implementation spectrum:
- **Quartz with JDBC store**: optimistic locking on a
  jobs table. The node that wins the DB lock runs the job.
  Failure: if the lock-holder node dies mid-job, the job
  is missed until the next trigger (configurable misfire
  policy).
- **Kubernetes CronJob**: Kubernetes scheduler ensures
  exactly-once per interval. The pod lifecycle provides
  isolation. Failure: Kubernetes retries the job.
- **Event-driven scheduling**: send a "trigger" event at
  schedule time (Kafka, EventBridge); consumer handles it.
  Back-pressure naturally: if consumers are slow, events
  queue; no lost work. Dead-letter queues capture failures.
The right solution depends on delivery semantics:
exactly-once (hard, requires coordination), at-least-once
(simpler, requires idempotency), or best-effort.

---

### ⚙️ How It Works (Mechanism)

```
ScheduledThreadPoolExecutor Internals
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ schedule(task, 5, MINUTES):                             │
│   ScheduledFutureTask sft = new ScheduledFutureTask(    │
│       task, now() + 5 * 60 * 1_000_000_000);            │
│   delayQueue.add(sft)                                   │
│                                                         │
│ Worker thread loop:                                     │
│   ScheduledFutureTask next = delayQueue.take();         │
│   // blocks until delay expires (now >= triggerTime)    │
│   next.run()  // executes the task                      │
│   if (next.isPeriodic()) {                              │
│       next.resetNext()  // update next trigger time     │
│       delayQueue.add(next)  // re-enqueue               │
│   }                                                     │
│                                                         │
│ DelayQueue: priority queue ordered by trigger time      │
│ take(): sleep until head item's delay <= 0              │
│ (efficient: thread sleeps, no polling)                  │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Spring @Scheduled application:

@Scheduled(cron = "0 0/5 * * * *")  // every 5 minutes
void refreshCache() {
    try {
        configCache.refresh();  // task logic
    } catch (Exception e) {
        log.error("Cache refresh failed", e);
        // DO NOT rethrow: would stop re-scheduling
    }
}

@Scheduled(fixedDelay = 30_000)  // 30s after last
  completion
void purgeExpiredSessions() {
    try {
        int purged =
          sessionRepo.deleteExpired(Instant.now());
        log.info("Purged {} sessions", purged);
    } catch (Exception e) {
        log.error("Session purge failed", e);
    }
}

Cluster deployment + ShedLock:
@Scheduled(cron = "0 0 8 * * MON-FRI")
@SchedulerLock(name = "dailyReportTask", lockAtMostFor =
  "10m")
void sendDailyReports() {
    // Only one node acquires the lock and runs this
    // Other nodes: lock() returns false, skip
    reportService.sendAll();
}
```

---

### 💻 Code Example

**Example 1 - Broken: java.util.Timer (avoid):**

```java
// BAD: Timer - single thread, kills all tasks on exception
Timer timer = new Timer("my-timer");

timer.scheduleAtFixedRate(new TimerTask() {
    @Override
    public void run() {
        // If this throws: Timer thread dies → ALL tasks stop
        purgeExpiredSessions();
    }
}, 0, 30_000);

timer.scheduleAtFixedRate(new TimerTask() {
    @Override
    public void run() {
        // Will NEVER run if purgeExpiredSessions threw
        sendDigestEmails();
    }
}, 0, 86_400_000);
// Timer: NEVER use in production code
```

**Example 2 - Correct: ScheduledExecutorService:**

```java
// GOOD: ScheduledExecutorService - exception-isolated tasks

ScheduledExecutorService scheduler =
    new ScheduledThreadPoolExecutor(
        4, // poolSize: 4 threads for concurrent tasks
        r -> {
            Thread t = new Thread(r, "scheduler-" + r.hashCode());
            t.setUncaughtExceptionHandler((thread, ex) ->
                log.error("Uncaught in {}: ", thread.getName(), ex));
            return t;
        }
    );

// CRITICAL: wrap task in try/catch to preserve re-scheduling
scheduler.scheduleWithFixedDelay(() -> {
    try {
        purgeExpiredSessions();
    } catch (Exception e) {
        log.error("Session purge failed - will retry next run", e);
        // Do NOT rethrow: ScheduledExecutorService stops
        // re-scheduling
    }
}, 0, 30, TimeUnit.SECONDS);

scheduler.scheduleAtFixedRate(() -> {
    try {
        sendDigestEmails();
    } catch (Exception e) {
        log.error("Email send failed", e);
    }
}, initialDelaySeconds(8, 0), 24, TimeUnit.HOURS);

// Graceful shutdown: let running tasks complete
scheduler.shutdown();
scheduler.awaitTermination(60, TimeUnit.SECONDS);
```

**Example 3 - Spring @Scheduled (most common in enterprise):**

```java
// GOOD: Spring @Scheduled with proper exception handling

@Service
@EnableScheduling
class MaintenanceService {

    @Scheduled(cron = "0 0/5 * * * *") // every 5 min
    public void refreshConfigCache() {
        try {
            configService.reload();
            log.info("Config cache refreshed");
        } catch (Exception e) {
            // Must catch: uncaught exception stops @Scheduled
            log.error("Config refresh failed", e);
        }
    }

    @Scheduled(fixedDelay = 60_000, initialDelay = 10_000)
    public void healthCheck() {
        try {
            healthCheckService.runAll();
        } catch (Exception e) {
            log.error("Health check failed", e);
        }
    }
}

// Spring boot: @EnableScheduling in a @Configuration class
// or @SpringBootApplication has it via @EnableAutoConfiguration
```

**Example 4 - Distributed scheduling with ShedLock:**

```java
// Cluster-safe: only one node runs the task

@Bean
public LockProvider lockProvider(DataSource dataSource) {
    return new JdbcTemplateLockProvider(
        JdbcTemplateLockProvider.Configuration.builder()
            .withJdbcTemplate(new JdbcTemplate(dataSource))
            .usingDbTime() // use DB clock for consistency
            .build()
    );
}

@Service
class ReportScheduler {
    @Scheduled(cron = "0 0 8 * * MON-FRI")  // 8 AM weekdays
    @SchedulerLock(
        name = "sendWeeklyReport",
        lockAtLeastFor = "5m",
        // hold lock even if task finishes fast
        lockAtMostFor  = "10m"
        // release lock after 10m (failure safety)
    )
    void sendWeeklyReport() {
        // ShedLock: only one node acquires the lock and runs
        // Other nodes: quietly skip (lock held by winner)
        reportService.generateAndSend();
    }
}
```

---

### ⚖️ Comparison Table

| Feature | `Timer` | `ScheduledExecutorService` | Spring `@Scheduled` | Quartz |
|---|---|---|---|---|
| Threads | Single | Pool | Configurable | Pool |
| Task isolation | No | Yes | Yes | Yes |
| Persistent jobs | No | No | No | Yes (DB-backed) |
| Cluster-aware | No | No | No (needs ShedLock) | Yes |
| Cron expressions | No | No | Yes | Yes |
| Monitoring | None | Metrics via TPE | Actuator | Job history |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `@Scheduled` tasks are thread-safe across runs | By default, `@Scheduled` runs on a single-threaded scheduler. If a task takes longer than its interval, the next run WAITS. Use `@Async` + a thread pool to allow concurrent runs, but then you must handle concurrent execution of the same task |
| Uncaught exceptions in `@Scheduled` are logged and retried | They are NOT retried by default. The `ScheduledExecutorService` suppresses future runs of a task that throws an uncaught exception. ALWAYS wrap task bodies in try/catch |
| `fixedRate` and `fixedDelay` are interchangeable | `fixedRate`: next run = lastStarted + period (can overlap under slow execution). `fixedDelay`: next run = lastFinished + delay (always waits the full delay after completion). Most jobs should use `fixedDelay` to prevent concurrent runs |
| ScheduledExecutorService alone is sufficient for production | For single-instance: yes. For clustered services: ScheduledExecutorService causes duplicate execution. Use ShedLock for distributed lock or Quartz for DB-backed scheduling |

---

### 🚨 Failure Modes & Diagnosis

**Scheduled Task Silently Stops Running**

**Symptom:**
A maintenance job (session purge, report generation) has
not run for days. No error in logs. The application is
healthy. `@Scheduled` method was never removed.

**Root Cause:**
An uncaught exception in the `@Scheduled` method caused
`ScheduledExecutorService` to stop re-scheduling the task.
No log entry because the exception is captured inside
the executor's future, not propagated to any error handler.

**Diagnosis:**
```java
// Add an explicit uncaught exception handler to the scheduler bean
@Configuration
class SchedulingConfig implements SchedulingConfigurer {
    @Override
    public void configureTasks(ScheduledTaskRegistrar reg) {
        ScheduledExecutorService executor =
            Executors.newScheduledThreadPool(4);
        reg.setScheduler(executor);
    }
}
// Or: add try/catch in every @Scheduled method body
// Monitor: @Scheduled invocation metrics via Micrometer
```

**Prevention:**
```java
@Scheduled(fixedDelay = 30_000)
public void runTask() {
    try {
        doWork();
    } catch (Exception e) {
        log.error("Task failed, will retry next run", e);
        // NEVER rethrow from @Scheduled
    }
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Thread Pool Pattern` - DPT-033; Scheduler uses a thread
  pool to execute tasks when their time arrives

**Builds On This (learn these next):**
- `Leader Election Pattern` - DPT-088; cluster scheduling
  requires leader election to ensure only one node runs
  the scheduled task
- `Active Object Pattern` - DPT-036; Active Object
  coordinates with scheduling for time-based behavior

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ JAVA API     │ ScheduledExecutorService (never Timer)   │
│              │ Spring: @Scheduled + @EnableScheduling   │
├──────────────┼──────────────────────────────────────────┤
│ GOTCHA       │ Uncaught exception → task stops silently │
│              │ Always wrap body in try/catch            │
├──────────────┼──────────────────────────────────────────┤
│ FIXED RATE   │ Period from last START time (can overlap)│
│ FIXED DELAY  │ Period from last END time (safer)        │
├──────────────┼──────────────────────────────────────────┤
│ CLUSTERED    │ ShedLock (distributed lock) or Quartz    │
│              │ (DB-backed); plain @Scheduled = duplicate│
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Timer: one exception kills all tasks     │
│              │ SES: one exception stops that task only  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Read-Write Lock → Active Object          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. NEVER use `java.util.Timer` - a single uncaught exception
   kills its single thread and stops ALL scheduled tasks silently.
   Use `ScheduledExecutorService` (Java) or `@Scheduled` (Spring).
2. In `@Scheduled` tasks: ALWAYS wrap the body in try/catch.
   Uncaught exceptions silently stop the task's re-scheduling
   in `ScheduledExecutorService`. This is a silent failure
   that is hard to detect.
3. In clustered deployments: `@Scheduled` runs on ALL
   instances simultaneously. Use ShedLock (distributed lock)
   or Quartz (DB-backed job store) to prevent duplicate
   execution across nodes.

