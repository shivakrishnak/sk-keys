---
layout: default
title: "Starvation"
parent: "Java Concurrency"
nav_order: 120
permalink: /java-concurrency/starvation/
number: "120"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, synchronized, ReentrantLock, Thread Priority
used_by: Fair Locks, Thread Scheduling, Executor Fairness
tags: #java, #concurrency, #starvation, #fairness, #scheduling
---

# 120 — Starvation

`#java` `#concurrency` `#starvation` `#fairness` #scheduling`

⚡ TL;DR — Starvation occurs when a thread is perpetually denied access to a shared resource because other threads always take priority — the thread is RUNNABLE but never progresses, not blocked, not livelocked.

| #120 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, synchronized, ReentrantLock, Thread Priority | |
| **Used by:** | Fair Locks, Thread Scheduling, Executor Fairness | |

---

### 📘 Textbook Definition

**Thread starvation** is a liveness failure in which a thread is unable to make progress because other threads continuously acquire a shared resource ahead of it. The starving thread remains in the RUNNABLE state (or keeps retrying) but never gets scheduled. Common causes: unfair lock acquisition (high-priority or greedy threads always win), non-fair `synchronized` or `ReentrantLock(false)`, unbounded heavy writers in a `ReadWriteLock`, or a thread pool with a work queue that is always saturated by high-priority tasks.

---

### 🟢 Simple Definition (Easy)

A customer at a deli counter who keeps getting skipped because new customers keep arriving and the server always serves the most recent (or loudest) customer first. The starving customer is present, willing, and waiting — but never served.

---

### 🔵 Simple Definition (Elaborated)

Starvation is subtler than deadlock — threads aren't frozen, they're just consistently unlucky. In a non-fair `synchronized` block, when the lock is released and 10 threads compete, the JVM picks any one of them. A low-priority or unlucky thread could theoretically never be chosen if high-priority threads keep arriving faster. Thread priority misuse (`Thread.MAX_PRIORITY`) is a classic cause — a CPU-intensive high-priority thread starves all low-priority threads.

---

### 🔩 First Principles Explanation

```
Normal scheduling (fair):
  Thread A, B, C, D all want the lock
  Release order: A→B→C→D→A→B...  (FIFO)
  All threads eventually get the lock ✓

Starvation (unfair scheduling):
  Thread A (high priority) and Thread B (low priority) compete
  Lock released → A always picked first (priority scheduling)
  A does long work, releases → A allowed in again before B
  B waits... waits... waits → effectively frozen

Starvation patterns:
  1. Thread priority: high-priority threads starve low-priority
  2. Non-fair lock: synchronized/ReentrantLock(false) — no queuing
     → same thread can reacquire immediately after release
  3. ReadWriteLock: continuous readers starve a writer
  4. Thread pool saturation: low-priority tasks never dequeued
  5. Greedy thread: holds lock for very long operations
```

---

### 🧠 Mental Model / Analogy

> A single express lane at a grocery store checkout. Customers with fewer than 10 items (high-priority threads) always get served first. A customer with 15 items (low-priority thread) keeps being passed over every time a new express customer arrives. They're present, waiting — but never helped. Fix: after waiting 5 minutes, any customer gets escalated to the express lane regardless (aging / priority boost).

---

### ⚙️ How It Works — Causes and Fixes

```
Cause 1: Non-fair ReentrantLock
  new ReentrantLock(false) → barge-in allowed → no FIFO
  Fix: new ReentrantLock(true) → FIFO ordering → no starvation
  Trade-off: fair locks ~10× slower throughput

Cause 2: Thread priority abuse
  Thread t = new Thread(...); t.setPriority(Thread.MAX_PRIORITY);
  → High-priority thread gets more CPU → low-priority starved
  Fix: avoid thread priorities; rely on JVM/OS scheduler

Cause 3: ReadWriteLock writer starvation
  Continuous incoming readers → writer never gets the lock
  Fix: fair RWLock; or use StampedLock (optimistic reads don't block writers)

Cause 4: Thread pool saturation
  Long-running tasks fill the pool queue
  Short tasks wait indefinitely
  Fix: separate pools for tasks of different duration/priority
       (e.g. fast-lane pool for priority tasks)

Cause 5: Holding locks for long operations
  Thread holds lock during expensive I/O → others starve
  Fix: minimise lock scope; use async patterns
```

---

### 🔄 How It Connects

```
Starvation
  ├─ vs Deadlock   → starvation: some threads progress; deadlock: none do
  ├─ vs Livelock   → livelock: all active but no progress; starvation: victim never runs
  ├─ Caused by     → unfair scheduling, priority misuse, lock holder hogging
  ├─ Fixed by      → fair locks, priority aging, bounded lock scope
  └─ Detected via  → throughput metrics per thread; jstack RUNNABLE long wait times
```

---

### 💻 Code Example

```java
// Demonstrating starvation: high-priority thread starves low-priority
Runnable highPriTask = () -> {
    while (true) { synchronized (lock) { doExpensiveWork(); } }
};
Runnable lowPriTask = () -> {
    while (true) { synchronized (lock) { doWork(); } }
};

Thread high = new Thread(highPriTask);
Thread low  = new Thread(lowPriTask);
high.setPriority(Thread.MAX_PRIORITY); // ← starvation risk
low.setPriority(Thread.MIN_PRIORITY);
high.start(); low.start();
// low priority thread gets very little (or no) CPU time
```

```java
// Fix 1: fair ReentrantLock — guarantees FIFO acquisition
ReentrantLock fairLock = new ReentrantLock(true); // fair = FIFO queue

fairLock.lock();
try { doWork(); } finally { fairLock.unlock(); }
// Guarantees all waiting threads eventually acquire in arrival order
```

```java
// Fix 2: priority inversion protection — avoid setting priorities
// Just don't use Thread.setPriority() unless you have a specific profiled need
// JVM and OS scheduler handle fairness better without explicit priorities

// Fix 3: reader-writer starvation — StampedLock optimistic reads
// don't block writers, eliminating the continuous-readers problem
StampedLock lock = new StampedLock();
long stamp = lock.tryOptimisticRead(); // doesn't register as a reader
// writer can always acquire write lock even while optimistic reads are "happening"
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Thread starvation causes an exception | Starving threads remain RUNNABLE or at a lock — no exception is thrown |
| Fair locks eliminate starvation with zero cost | Fair locks cost ~10× throughput; use only when starvation is a proven problem |
| `synchronized` is always fair | `synchronized` is non-fair — any waiting thread can be awakened in any order |
| Setting thread priority fixes performance | Priority misuse causes starvation; avoid priorities unless deeply necessary |

---

### 🔥 Pitfalls in Production

**Pitfall: Connection pool starvation — long queries monopolise connections**

```java
// Long-running analytics queries hold connections for 30 seconds
// Short transactional queries wait → user-facing requests time out

// Fix: separate connection pools by query type
DataSource oltp = HikariPool(maxPoolSize=20);   // fast transactions
DataSource olap = HikariPool(maxPoolSize=5);    // slow analytics
// Each pool is isolated; OLAP queries never starve OLTP
```

---

### 🔗 Related Keywords

- **[Deadlock](./071 — Deadlock.md)** — total halt vs starvation (one thread never runs)
- **[Livelock](./088 — Livelock.md)** — all busy but no progress vs one thread dormant
- **[ReentrantLock](./076 — ReentrantLock.md)** — fair=true prevents starvation
- **[ReadWriteLock](./083 — ReadWriteLock.md)** — writer starvation classic case
- **[StampedLock](./087 — StampedLock.md)** — solves reader-caused writer starvation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Thread perpetually denied access — others     │
│              │ always win; RUNNABLE but never progresses     │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing: some threads consistently slow or │
│              │ never completing despite being runnable       │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Prevent: fair locks; avoid setPriority;       │
│              │ separate pools for different task durations   │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Everyone moves, but one thread always        │
│              │  gets cut in line and never gets there"       │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Fair ReentrantLock → StampedLock →            │
│              │ Thread Priority → Priority Inversion          │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A fair `ReentrantLock(true)` guarantees FIFO ordering and eliminates starvation. How does it achieve this mechanically? What data structure does it use internally to maintain order?

**Q2.** "Priority inversion" is related to but different from starvation. A low-priority thread holds a lock needed by a high-priority thread; a medium-priority thread runs in between, blocking the high-priority thread indefinitely. How does this differ from starvation, and what OS mechanism (used in RTOS) prevents it?

**Q3.** In Java, thread priorities (`Thread.MIN_PRIORITY` to `Thread.MAX_PRIORITY`) are hints to the OS scheduler. Why is it generally a bad idea to rely on thread priorities for correctness in Java programs?

