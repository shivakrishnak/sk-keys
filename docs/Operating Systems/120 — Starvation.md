---
layout: default
title: "Starvation"
parent: "Operating Systems"
nav_order: 120
permalink: /operating-systems/starvation/
number: "0120"
category: Operating Systems
difficulty: ★★☆
depends_on: Deadlock, Livelock, Scheduler — Preemption, Mutex
used_by: Thread Priority, Fair Scheduling, ReadWriteLock
related: Deadlock, Livelock, Priority Inversion, Aging
tags:
  - os
  - concurrency
  - scheduling
  - fundamentals
---

# 120 — Starvation

⚡ TL;DR — Starvation is when a thread is perpetually denied CPU or resources because higher-priority threads or unfair algorithms always take precedence — the thread is alive but never runs.

| #0120           | Category: Operating Systems                       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Deadlock, Livelock, Scheduler — Preemption, Mutex |                 |
| **Used by:**    | Thread Priority, Fair Scheduling, ReadWriteLock   |                 |
| **Related:**    | Deadlock, Livelock, Priority Inversion, Aging     |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A read-heavy system uses a ReadWriteLock. Readers are frequent; a writer arrives. The lock implementation allows new readers to acquire the read lock even while a writer is waiting. Readers arrive in a continuous stream — there's always a reader holding the read lock. The writer waits forever, even though it's not blocked in a deadlock cycle. This is writer starvation.

THE BREAKING POINT:
Any unfair scheduling policy can cause starvation in the presence of high-priority or high-frequency work. The starved thread is WAITING (not running), but the reason isn't a cycle (deadlock) or mutual interference (livelock) — it's simply never being selected. In production: a low-priority housekeeping task never runs because high-priority request threads always preempt it; cache eviction never runs; logs never flush; indexes never rebuild.

THE INVENTION MOMENT:
OS scheduling research in the 1960s–70s introduced **aging**: gradually increase a waiting thread's priority the longer it waits, until it eventually overtakes the high-priority threads. This prevents indefinite postponement without changing the basic priority-based scheduling model.

---

### 📘 Textbook Definition

**Starvation** (also called **indefinite postponement**) is a scheduling failure mode in which a thread is perpetually denied the CPU or a resource it needs, even though it is not involved in a deadlock or livelock. Starvation occurs when a scheduling or resource allocation policy systematically favours some threads over others, causing certain threads to wait indefinitely. Unlike deadlock (circular wait) and livelock (active but unproductive), starvation involves a thread that is simply never selected. Solutions include: **fair scheduling** (FIFO queuing, time-sliced algorithms), **priority aging** (increase priority of waiting threads over time), and **read-write lock fairness** policies.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Starvation = a thread waits forever not because of a cycle or bug, but because the scheduler always picks someone else.

**One analogy:**

> A busy restaurant: VIP customers always get seated first. If VIPs keep arriving, regular customers in the queue wait indefinitely — the queue grows, but the regulars never get a table. No deadlock (no circular waiting), no livelock (everyone is moving) — just perpetual unfairness.

**One insight:**
Starvation is the expected result of priority-based scheduling without aging or fairness bounds. It's a design choice: a system that prioritises high-priority work will starve low-priority work if high-priority work is continuous. The fix (aging) says: if you've waited long enough, you become high priority.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. A starved thread is runnable but never scheduled (or waiting for a resource that's never granted).
2. No cycle exists (distinguishes from deadlock).
3. The thread is not looping productively (distinguishes from livelock).
4. Other threads continuously prevent the starved thread from being selected.

CAUSES:

- **Priority-based preemption**: High-priority threads always run; low-priority never scheduled.
- **Unfair mutex**: Non-FIFO lock acquisition; a thread repeatedly loses to faster competitors.
- **Reader-writer lock writer starvation**: New readers allowed in while a writer waits.
- **Resource exhaustion with unfair allocation**: Threads with more concurrent requests get more resources.

SOLUTIONS:

- **Aging**: Gradually increase priority of waiting threads. OS schedulers (Linux CFS, Windows scheduler) use this implicitly.
- **Fair mutex**: FIFO queue for lock acquisition (`new ReentrantLock(true)` in Java).
- **Writer preference**: ReadWriteLock blocks new readers if a writer is waiting.
- **Time slicing**: Even low-priority threads get scheduled occasionally.
- **Rate limiting**: Prevent high-priority threads from monopolising resources indefinitely.

THE TRADE-OFFS:
Gain: Fairness guarantees — every runnable thread eventually runs.
Cost: Throughput: a fair FIFO lock has higher overhead than unfair; aging complicates scheduler implementation; writer preference increases write latency for reads-dominated workloads.

---

### 🧪 Thought Experiment

READER-WRITER LOCK WRITER STARVATION:

```
Situation: 100 reader threads arrive continuously at 10ms intervals
ReadWriteLock (unfair, allows new readers):
  t=0:   Readers 1–10 acquire read lock
  t=5:   Writer 1 arrives, waits (read lock held)
  t=10:  Readers 11–20 arrive, acquire read lock (WRITER STILL WAITING)
  t=15:  Readers 1–10 release
         Readers 21–30 arrive, acquire read lock (WRITER STILL WAITING)
  t=∞:   Writer 1 never acquires write lock → STARVATION

ReadWriteLock (writer preference, blocks new readers if writer waiting):
  t=0:   Readers 1–10 acquire read lock
  t=5:   Writer 1 arrives, sets "writer waiting" flag
  t=10:  Readers 11–20 arrive → BLOCKED (writer waiting)
  t=15:  Readers 1–10 release → read lock count = 0
         Writer 1 acquires write lock → proceeds
  t=16:  Writer 1 releases → Readers 11–20 proceed
```

THE INSIGHT:
A subtle policy change (block new readers when a writer waits) converts writer starvation to bounded wait. The write latency increases slightly (must drain in-flight readers) but unbounded starvation is eliminated.

---

### 🧠 Mental Model / Analogy

> A highway on-ramp with a zipper merge. If the existing highway traffic (high-priority threads) never leaves a gap (never yields), on-ramp cars (low-priority threads) wait forever. Aging is a traffic law: after waiting 5 minutes, on-ramp cars have priority and highway traffic must stop. Forced fairness via time.

> In ReadWriteLock terms: the "writer waiting" flag is a physical barrier placed on the on-ramp: new readers see it and stop. Once all in-flight readers pass, the writer goes.

Where this breaks down: aging in software is explicit and configurable; natural fairness mechanisms (like humans yielding out of social pressure) don't exist for threads.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Starvation is when a thread always gets pushed back in line. Other threads keep getting resources first, and the starved thread never gets its turn — not because of a bug, but because the scheduling policy always picks others.

**Level 2 — How to use it (junior developer):**
In Java, `new ReentrantLock(true)` creates a fair lock (FIFO acquisition order) — prevents thread starvation. `ReentrantReadWriteLock` writer starvation: prevent with careful design or use `StampedLock` (Java 8+) for optimistic reads. For thread priority, avoid using `Thread.setPriority()` in application code — JVM priority mapping is OS-dependent. For background tasks that must not starve, dedicate a thread pool with bounded capacity.

**Level 3 — How it works (mid-level engineer):**
Linux CFS (Completely Fair Scheduler) prevents starvation via virtual runtime: each task has a `vruntime` counter (nanoseconds of CPU time received, weighted by priority). The scheduler always picks the task with lowest `vruntime`. Low-priority tasks have slower-growing `vruntime` but they still grow — eventually they reach the head of the red-black tree and get scheduled. This is aging by design: the longer you wait, the lower your relative `vruntime`. The minimum granularity (1ms) ensures even low-priority tasks run eventually.

**Level 4 — Why it was designed this way (senior/staff):**
The tension between "highest priority runs" and "all threads eventually run" is fundamental to scheduling theory. Early batch systems used pure priority (easy to implement, maximum throughput for high-priority work). Time-sharing systems (1960s) introduced fairness as a requirement (users pay for time and expect proportional service). CFS (2007, Ingo Molnár) resolved the tension with weighted-fair queuing: each task's `vruntime` grows at a rate inversely proportional to its weight (priority). Low-priority tasks accumulate `vruntime` slowly — they get less CPU — but they always make some progress. This is mathematically equivalent to weighted fair queuing in networking (WFQ), applied to CPU scheduling.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│           CFS: VIRTUAL RUNTIME AND FAIRNESS            │
├────────────────────────────────────────────────────────┤
│  Priority: High(H) = 2 weight, Low(L) = 1 weight      │
│  At every 1ms tick, update vruntime:                   │
│    H: vruntime += 1ms / 2  = 0.5ms virtual             │
│    L: vruntime += 1ms / 1  = 1.0ms virtual             │
│                                                        │
│  Scheduler always picks lowest vruntime:               │
│  t=0: H.vrt=0, L.vrt=0 → pick H (tie, H first)        │
│  t=1: H.vrt=0.5, L.vrt=0 → pick L                     │
│  t=2: H.vrt=0.5, L.vrt=1.0 → pick H                   │
│  t=3: H.vrt=1.0, L.vrt=1.0 → pick H (tie)             │
│  t=4: H.vrt=1.5, L.vrt=1.0 → pick L                   │
│  ...                                                   │
│  H gets 2 runs per 3 slots (67%), L gets 1 (33%)       │
│  Low always makes progress — no starvation             │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

FAIR REENTRANTLOCK (FIFO acquisition):

```
Thread A (req 1): lock.lock() → acquires (queue empty)
Thread B (req 2): lock.lock() → enqueues (position 1)
Thread C (req 3): lock.lock() → enqueues (position 2)
Thread D (req 4): lock.lock() → enqueues (position 3)

Thread A: unlock() → dequeues Thread B (FIFO) → B acquires
Thread B: unlock() → dequeues Thread C (FIFO) → C acquires
Thread C: unlock() → dequeues Thread D (FIFO) → D acquires

All threads served in arrival order → no starvation
```

UNFAIR LOCK (default ReentrantLock):

```
Thread A holds lock; B, C, D queued
Thread A: unlock()
  → B is queued head, but D just called lock.lock()
  → Unfair: D gets immediate CAS opportunity (it's running)
  → D wins, B re-queues
  → With continuous new arrivals: B never gets the lock
  → STARVATION
```

---

### 💻 Code Example

Example 1 — Fair vs unfair lock:

```java
// UNFAIR (default) — faster throughput but starvation possible
ReentrantLock unfairLock = new ReentrantLock();

// FAIR — FIFO ordering, prevents starvation
ReentrantLock fairLock = new ReentrantLock(true);

// Measure: fair lock has ~20% higher overhead but no starvation
// For most workloads: use unfair; for bounded latency guarantees: use fair
```

Example 2 — ReadWriteLock writer starvation fix:

```java
// WRITER STARVATION PRONE: default ReadWriteLock
ReadWriteLock rwLock = new ReentrantReadWriteLock();
// Default: fair = false → readers can sneak in past waiting writers

// WRITER STARVATION PREVENTION: fair ReadWriteLock
ReadWriteLock fairRwLock = new ReentrantReadWriteLock(true);
// When writer waiting: new readers queue behind writer
Lock readLock  = fairRwLock.readLock();
Lock writeLock = fairRwLock.writeLock();

// ALTERNATIVE: StampedLock with optimistic reads (Java 8+)
StampedLock sl = new StampedLock();
// Optimistic read (no lock acquired):
long stamp = sl.tryOptimisticRead();
int value = sharedValue;           // READ without lock
if (!sl.validate(stamp)) {         // Check if still valid
    stamp = sl.readLock();         // Fall back to lock
    try { value = sharedValue; } finally { sl.unlockRead(stamp); }
}
// StampedLock: writers not starved, readers have optimistic path
```

Example 3 — Detect starvation via thread wait time monitoring:

```java
// Monitor lock wait time to detect starvation
public class MonitoredLock {
    private final ReentrantLock lock = new ReentrantLock(true);  // fair
    private static final long STARVATION_THRESHOLD_MS = 1000;

    public void lock() throws InterruptedException {
        long waitStart = System.currentTimeMillis();
        if (!lock.tryLock(STARVATION_THRESHOLD_MS, TimeUnit.MILLISECONDS)) {
            log.error("Potential starvation: waited {}ms for lock in thread {}",
                System.currentTimeMillis() - waitStart,
                Thread.currentThread().getName());
            lock.lock();  // block indefinitely (or throw)
        }
    }

    public void unlock() { lock.unlock(); }
}
```

---

### ⚖️ Comparison Table

| Progress Failure   | Threads Active?   | CPU?            | Detectable?          | Fix                  |
| ------------------ | ----------------- | --------------- | -------------------- | -------------------- |
| **Deadlock**       | No (BLOCKED)      | No              | Yes (jstack)         | Lock ordering        |
| Livelock           | Yes               | 100%            | Hard (RUNNABLE)      | Jitter/backoff       |
| **Starvation**     | Starved = WAITING | Low for starved | Possible (wait time) | Fair lock, aging     |
| Priority Inversion | Mixed             | Normal          | Possible             | Priority inheritance |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Starvation = deadlock"                       | Different: deadlock is a cycle; starvation is perpetual unfairness without a cycle                                                                                                         |
| "Thread.setPriority() prevents starvation"    | High priority can CAUSE starvation in low-priority threads; it doesn't prevent starvation in the prioritised thread                                                                        |
| "Fair=true in ReentrantLock is always better" | Fair lock has higher overhead (CLH queue maintenance); only use when starvation is actually a concern                                                                                      |
| "Low-priority JVM threads never starve"       | On JVM with OS-mapped threads and a preemptive OS (Linux/macOS), low-priority threads still run (CFS prevents true starvation), but on Windows with priority 1 threads, starvation is real |

---

### 🚨 Failure Modes & Diagnosis

**1. Background Task Never Runs**

Symptom: Housekeeping tasks (cache eviction, log rotation, index rebuild) never execute despite appearing in scheduled executor logs; system resources accumulate indefinitely.

Root Cause: High-priority request threads monopolise executor thread pool or CPU; low-priority housekeeping tasks scheduled but never selected.

Diagnostic:

```java
// Check scheduled task execution lag
scheduledExecutor.schedule(
    () -> log.info("Housekeeping ran at {}", Instant.now()),
    0, TimeUnit.MILLISECONDS
);
// If log message appears > 10s after schedule → starvation

// ThreadPoolExecutor queue size
ThreadPoolExecutor tpe = (ThreadPoolExecutor) executor;
log.info("Queue size: {}", tpe.getQueue().size());
// Growing queue with tasks never completing = starvation
```

Fix: Dedicate a separate thread pool for background tasks; use `Executors.newSingleThreadScheduledExecutor()` for housekeeping.

---

**2. ReadWriteLock Writer Starvation in Cache**

Symptom: Cache hit rate is high but cache updates lag minutes behind the source; invalidation rarely occurs; stale data returned.

Root Cause: High reader throughput holds readLock continuously; cache writer (invalidation) acquires writeLock but waits indefinitely.

Diagnostic:

```java
ReentrantReadWriteLock rwl = (ReentrantReadWriteLock) cacheLock;
log.info("Write queue length: {}", rwl.getQueueLength());
log.info("Read hold count: {}", rwl.getReadHoldCount());
// High write queue with always-nonzero read hold = writer starved
```

Fix: Use `new ReentrantReadWriteLock(true)` (fair) or `StampedLock` for optimistic reads.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Deadlock` — distinguish from starvation; both are progress failures, different cause
- `Livelock` — active non-progress; contrast with starvation (passive non-progress)
- `Scheduler — Preemption` — starvation arises from scheduling policy; need scheduler understanding

**Builds On This (learn these next):**

- `Priority Inversion` — related failure: high-priority thread blocked by low-priority one holding a mutex
- `Fair Scheduling` — the solution concept that prevents starvation
- `ReadWriteLock` — the concrete data structure where writer starvation is a real production issue

**Alternatives / Comparisons:**

- `Priority Inversion` — high-priority thread starved specifically because it's waiting for a mutex held by a low-priority thread (Mars Pathfinder bug)
- `Thundering Herd` — many threads stall, then all rush; related to starvation recovery

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Thread perpetually denied resources;     │
│              │ not blocked in a cycle — just never picked│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Unfair scheduling causes low-priority    │
│ SOLVES       │ work to never execute                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Aging (Linux CFS vruntime) ensures every │
│              │ thread eventually runs                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing background tasks not running; │
│              │ ReadWriteLock writer never acquiring      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ "Avoid" = use fair locks, dedicated      │
│              │ thread pools, and bounded wait times      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fairness (all run eventually) vs         │
│              │ throughput (prioritised work runs more)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Always last in line — not blocked,      │
│              │  just never picked"                      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Priority Inversion → CFS → StampedLock   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Mars Pathfinder priority inversion bug (1997): a high-priority meteorology task was being reset by the watchdog timer because it couldn't run. The reason: a low-priority task held a mutex needed by a medium-priority task, which held a mutex needed by the high-priority meteorology task. The medium-priority task's continuous preemption of the low-priority task prevented the low-priority task from releasing the mutex. This is priority inversion — the high-priority task's effective priority was inverted to match the low-priority mutex holder's priority. Describe the exact priority inheritance fix that solved this on Mars Pathfinder, and why priority inheritance on POSIX systems (`PTHREAD_PRIO_INHERIT`) is not enabled by default despite the obvious benefit.

**Q2.** Java 21 introduces virtual threads (JEP 425), which are extremely lightweight threads mapped to carrier (OS) threads by the JVM. A single OS thread can multiplex millions of virtual threads. Virtual threads have no OS-level priority (they're not OS threads). If your application has 1 million virtual threads and one carrier thread pool of 4 threads, describe: (1) how starvation of virtual threads is prevented (what scheduling policy does the JVM use?), (2) whether blocking operations like `synchronized` cause carrier thread starvation (hint: yes, pre-JDK 24 — a virtual thread pinned to its carrier blocks the carrier), and (3) how JDK 21's virtual thread scheduler differs from CFS in its fairness guarantees.
