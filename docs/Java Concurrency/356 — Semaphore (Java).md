---
layout: default
title: "Semaphore (Java)"
parent: "Java Concurrency"
nav_order: 356
permalink: /java-concurrency/semaphore/
number: "0356"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread (Java), ReentrantLock, synchronized
used_by: BlockingQueue, Connection Pools, Rate Limiting
related: ReentrantLock, CountDownLatch, BlockingQueue
tags:
  - java
  - concurrency
  - synchronization
  - intermediate
  - resource-pool
---

# 0356 — Semaphore (Java)

⚡ TL;DR — A `Semaphore` maintains a count of available permits; threads acquire permits before accessing a resource and release them afterward — limiting how many threads access a resource concurrently, not just one (like a mutex), but N at a time.

| #0356 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), ReentrantLock, synchronized | |
| **Used by:** | BlockingQueue, Connection Pools, Rate Limiting | |
| **Related:** | ReentrantLock, CountDownLatch, BlockingQueue | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A database connection pool should allow at most 10 concurrent users. `synchronized` allows exactly 1. `ReentrantLock` allows exactly 1. There's no built-in mechanism to say "allow up to 10 threads, block the 11th until one finishes."

THE INVENTION MOMENT:
**`Semaphore`** generalises mutual exclusion to N-way access control — a mutex is a semaphore with 1 permit.

---

### 📘 Textbook Definition

**`Semaphore`** is a `java.util.concurrent` synchroniser that maintains a count of permits. `acquire()` decrements the count, blocking if count is 0. `release()` increments the count, unblocking one waiting thread. Supports fair (FIFO) and non-fair modes. Key methods: `acquire()`, `acquire(n)`, `tryAcquire()`, `tryAcquire(timeout)`, `release()`, `availablePermits()`. `Semaphore(1)` = binary semaphore (mutex equivalent, but NOT reentrant).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Semaphore = N-slot mutex: N threads can hold it simultaneously; the (N+1)th blocks until a slot opens.

**One analogy:**
> A parking garage with 10 spaces. Cars can enter when spaces are available (acquire permit). When a car leaves (release permit), another car can enter. 11th car waits at the gate. The gate count (permits) goes from 10 to 0 as cars fill up.

**One insight:**
`Semaphore(1)` is NOT the same as `synchronized` or `ReentrantLock` — it's NOT reentrant. The same thread calling `acquire()` twice without `release()` between them will deadlock itself. Use `ReentrantLock` for mutual exclusion; use `Semaphore` only for resource counting.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Permits are not thread-owned — any thread can call `release()`, even a thread that didn't call `acquire()`. This enables producer-consumer signalling.
2. `Semaphore(0).acquire()` blocks until at least one `release()` — like a gate that starts closed.
3. Permits can be negative conceptually during construction, but `availablePermits()` returns max(0, count).

```
Semaphore state machine:
  permits = 10 (initial)
  T1.acquire() → permits = 9
  T2.acquire() → permits = 8
  ...
  T10.acquire() → permits = 0
  T11.acquire() → BLOCKS (permits == 0)
  T1.release()  → permits = 1, T11 unblocked → permits = 0
```

THE TRADE-OFFS:
Gain: N-way access control; producer-consumer gate (start at 0); non-reentrant by design (intentional for resource pools).
Cost: Not reentrant; different thread can release (can be a feature OR a bug); permits don't belong to threads — no deadlock detection available.

---

### 🧪 Thought Experiment

SETUP: Connection pool with 10 connections.

```java
Semaphore pool = new Semaphore(10);

Connection getConnection() throws InterruptedException {
    pool.acquire(); // blocks if 10 already in use
    return connections.poll();
}

void returnConnection(Connection conn) {
    connections.offer(conn);
    pool.release(); // allow one more thread in
}
```

THE INSIGHT: Semaphore enforces the constraint "at most 10 concurrent users" without managing identity — it just counts. Any thread can call `release()` as long as the count doesn't exceed the intended maximum.

---

### 🧠 Mental Model / Analogy

> A semaphore is a nightclub with a capacity limit. The bouncer counts: 10 people inside → entry blocked. Someone exits → bouncer allows the next person. No one "owns" a slot — you hold a permit while inside, release it when you leave.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Semaphore = "only N threads at a time, everyone else waits."

**Level 2:** `acquire()` blocks until a permit is available. `tryAcquire()` returns false immediately if no permits. Use `tryAcquire(timeout, unit)` for time-limited waiting. Always `release()` in `finally`.

**Level 3:** Built on AQS (`AbstractQueuedSynchronizer`). State = permit count. `acquire()` decrements via CAS; if result < 0, thread enqueues and parks. `release()` increments, unparks head of queue.

**Level 4:** Semaphores are dual-purpose: **counting** (resource pools) and **signalling** (one thread releases to wake another that is blocked on 0 permits). The signalling use case is like a "one-shot gate" — `Semaphore(0)`: producer does work then `release()`; consumer blocks on `acquire()` until signal arrives.

---

### ⚙️ How It Works (Mechanism)

```java
// Resource pool:
Semaphore pool = new Semaphore(10, true); // fair=true

void useResource() throws InterruptedException {
    pool.acquire();   // blocks if 10 threads already in
    try {
        doWork();
    } finally {
        pool.release(); // always release
    }
}

// Rate limiting (permits per second approximation):
Semaphore rateLimiter = new Semaphore(100); // 100 concurrent
ScheduledExecutorService refiller = Executors.newSingleThreadScheduledExecutor();
refiller.scheduleAtFixedRate(
    () -> rateLimiter.release(100),
    0, 1, TimeUnit.SECONDS
);

// Non-blocking tryAcquire:
if (pool.tryAcquire(100, TimeUnit.MILLISECONDS)) {
    try { doWork(); }
    finally { pool.release(); }
} else {
    throw new ServiceOverloadedException();
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
[T11: acquire() — permits=0]
    → [AQS: decrementPermits → permits=-1 < 0]      ← YOU ARE HERE
    → [T11 enqueued in AQS wait queue, parked]
    → [T1: release() → permits=0: head unparked]
    → [T11: woken, acquires permit → permits=0]
    → [T11: executes work]
    → [T11: release() → permits=1]
```

---

### 💻 Code Example

```java
// FixedSizePool using Semaphore:
public class ResourcePool<T> {
    private final Semaphore semaphore;
    private final Queue<T> resources;

    ResourcePool(List<T> resources) {
        this.resources  = new ConcurrentLinkedQueue<>(resources);
        this.semaphore  = new Semaphore(resources.size(), true);
    }

    public T acquire() throws InterruptedException {
        semaphore.acquire();
        return resources.poll();
    }

    public void release(T resource) {
        resources.offer(resource);
        semaphore.release();
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism | Concurrency | Reentrant | Ownership | Best For |
|---|---|---|---|---|
| `synchronized` | 1 | Yes | Thread-owned | Critical sections |
| `ReentrantLock` | 1 | Yes | Thread-owned | Advanced locking |
| **`Semaphore(N)`** | N | No | Unowned | Resource pools, rate limiting |
| `CountDownLatch` | N→0 (one-shot) | No | N/A | Startup sync |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Semaphore(1) = synchronized | `Semaphore(1)` is NOT reentrant — same thread acquiring twice deadlocks! Use ReentrantLock for mutex semantics |
| Only the acquiring thread can release | Any thread can `release()` — including one that never called `acquire()`. This enables signalling patterns |

---

### 🚨 Failure Modes & Diagnosis

**Permit leak (release not called):**
```java
// Always use try/finally:
pool.acquire();
try { doWork(); }
finally { pool.release(); } // ALWAYS
```

**Duplicate release inflating permits:**
```java
// BAD: double release grows permits beyond initial
pool.release();
pool.release(); // permits now > initial capacity
// Use try/finally pattern — one acquire, one release
```

---

### 🔗 Related Keywords

**Prerequisites:** `ReentrantLock`, `Thread (Java)`
**Builds on:** `BlockingQueue` (uses semaphore internally for capacity), Connection Pools
**Related:** `ReentrantLock`, `CountDownLatch`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ N-slot access control: N threads at once, │
│              │ (N+1)th blocks until a slot frees         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ NOT reentrant. Semaphore(1) ≠ synchronized.│
│              │ Any thread can release (feature for gates) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "N-slot parking garage — enter if space,  │
│              │  exit gives space back"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CountDownLatch → CyclicBarrier → Phaser   │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** A producer-consumer system uses `Semaphore notEmpty = new Semaphore(0)` and `Semaphore notFull = new Semaphore(capacity)`. The producer calls `notFull.acquire()` before adding and `notEmpty.release()` after; the consumer calls `notEmpty.acquire()` before taking and `notFull.release()` after. Compare this to using `BlockingQueue` — explain what `BlockingQueue` adds beyond the raw semaphore coordination, specifically regarding exception handling, thread interruption, and collection iteration safety.

