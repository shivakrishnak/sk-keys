---
layout: default
title: "Semaphore"
parent: "Operating Systems"
nav_order: 115
permalink: /operating-systems/semaphore/
number: "0115"
category: Operating Systems
difficulty: ★★☆
depends_on: Mutex, Thread, Concurrency vs Parallelism
used_by: Thread Pool, Resource Pool, Rate Limiting, Producer-Consumer
related: Mutex, Condition Variable, CountDownLatch, Semaphore (Java)
tags:
  - os
  - concurrency
  - synchronization
  - fundamentals
---

# 115 — Semaphore

⚡ TL;DR — A semaphore is a counter-based synchronisation primitive that allows at most N threads to access a resource simultaneously; acquire decrements the counter, release increments it; zero = block.

| #0115           | Category: Operating Systems                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Mutex, Thread, Concurrency vs Parallelism                    |                 |
| **Used by:**    | Thread Pool, Resource Pool, Rate Limiting, Producer-Consumer |                 |
| **Related:**    | Mutex, Condition Variable, CountDownLatch, Semaphore (Java)  |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You have a connection pool with 10 database connections. 100 threads all need a connection simultaneously. Without a controlling mechanism, all 100 threads might try to acquire connections, exhausting the pool and causing failures or unbounded resource consumption.

THE BREAKING POINT:
A mutex solves 1-at-a-time access, but many resources can handle N concurrent users. A connection pool, a rate limiter (5 requests/second), a thread-bounded download queue — all need to allow exactly N concurrent accesses, not 1. A mutex is too restrictive (N=1 only).

THE INVENTION MOMENT:
Dijkstra introduced the semaphore in 1965 alongside the critical section problem. The "wait" (P, from Dutch "proberen" = to test) and "signal" (V, from "verhogen" = to increment) operations on an integer counter were the original and remain the definitive solution to N-resource bounded access.

---

### 📘 Textbook Definition

A **semaphore** is a synchronisation primitive consisting of an integer counter and two atomic operations:

- **acquire** (also called `wait`, `P`, `down`): if counter > 0, decrement it and continue; if counter == 0, block until counter > 0.
- **release** (also called `signal`, `V`, `up`): increment the counter; if any threads are blocked, wake one.

A **binary semaphore** (counter initialised to 1) behaves like a mutex but with a critical difference: release can be called by any thread (unlike a mutex, which must be released by the acquiring thread). A **counting semaphore** (counter initialised to N) allows up to N threads to hold the semaphore concurrently, making it suitable for resource pools.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A semaphore is a counter that starts at N; each user decrements it before entering and increments it when done; when it hits zero, new users block.

**One analogy:**

> A parking garage with 10 spaces and an electronic counter at the entrance. When you enter, the counter decrements (9 free). When you leave, it increments (10 free). When counter = 0, the gate stays down. You wait until someone leaves and the counter goes to 1, then the gate opens.

**One insight:**
A mutex is a special semaphore (N=1) with an ownership rule. A semaphore is more general — but lacks ownership, which means any thread can release it. This makes semaphores powerful for signalling (thread A acquires, thread B releases to signal A to proceed) but dangerous if release/acquire are mismatched.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Counter ≥ 0 always.
2. `acquire()` is atomic: check + decrement + (possibly block) is one indivisible operation.
3. `release()` is atomic: increment + (possibly wake a waiter) is one indivisible operation.
4. The value at any time = initial_value + total_releases - total_acquires (but never < 0).

DERIVED DESIGN:
A semaphore implementation needs:

1. An integer counter (protected by an internal lock).
2. A wait queue for blocked threads.
3. `acquire()`: lock, if counter > 0: decrement + unlock + return; else: add to wait queue + unlock + sleep.
4. `release()`: lock, increment counter, if wait queue non-empty: wake one thread + decrement counter (giving it the slot) + unlock.

The OS-level implementation uses a futex (like mutex) for the wait/wake step, so uncontended paths require no syscall.

THE TRADE-OFFS:
Gain: Limits concurrent access to exactly N; enables producer-consumer patterns; supports cross-thread signalling.
Cost: No ownership → any thread can release, making bugs hard to diagnose; easy to misconfigure initial count; susceptible to deadlock if acquire/release pairs are unbalanced; fairness depends on implementation.

---

### 🧪 Thought Experiment

SETUP:
Connection pool: 3 connections, 5 threads each needing a connection.

```
Semaphore sem = new Semaphore(3);  // 3 permits

Thread 1: sem.acquire() → counter: 3→2 → proceeds
Thread 2: sem.acquire() → counter: 2→1 → proceeds
Thread 3: sem.acquire() → counter: 1→0 → proceeds
Thread 4: sem.acquire() → counter = 0 → BLOCKS
Thread 5: sem.acquire() → counter = 0 → BLOCKS

Thread 1: sem.release() → counter: 0→1 → wake Thread 4
Thread 4: counter: 1→0 → proceeds (gets connection)

Thread 2: sem.release() → counter: 0→1 → wake Thread 5
Thread 5: counter: 1→0 → proceeds
```

THE INSIGHT:
At no point were more than 3 threads in the critical section. The semaphore acted as a bounded gate. Thread 4 and 5 waited efficiently (blocked, not spinning) and were woken exactly when a permit became available.

---

### 🧠 Mental Model / Analogy

> A semaphore is a bouncer with a clicker at a club. The club capacity is N. The bouncer decrements their clicker when someone enters and increments it when someone leaves. When the count = 0 (full), new arrivals join a queue and wait. When someone leaves, the bouncer checks the queue and lets the first person in.

> Binary semaphore (N=1): the bouncer only allows 1 person at a time — acts like a mutex, except the person who enters doesn't have to be the same one who notifies the bouncer they've left. Anyone can say "I'm leaving" (any thread can release). This makes binary semaphores useful for signalling but dangerous for mutual exclusion.

Where the analogy breaks down: unlike a real club, semaphore wait queues typically don't guarantee FIFO. The "first in" may not be "first served" unless a fair semaphore implementation is used.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A semaphore is a counter. Programs ask "may I proceed?" (acquire). If the counter is above zero, yes — counter decrements. When done, they say "I'm done" (release) — counter increments. If the counter is zero, they wait. This allows exactly N concurrent users.

**Level 2 — How to use it (junior developer):**
Java: `Semaphore sem = new Semaphore(permits, fair)`. `sem.acquire()` blocks until a permit is available. `sem.release()` returns one permit. Always release in `finally`. For fair scheduling (FIFO), use `new Semaphore(N, true)` — slightly slower but prevents starvation. Use for: DB connection pools, rate limiting (try `tryAcquire(timeout)`), bounded blocking queues.

**Level 3 — How it works (mid-level engineer):**
Java `Semaphore` uses `AbstractQueuedSynchronizer` (AQS) internally. AQS state = permit count. `acquire()`: `tryAcquireShared(1)` via `getAndDecrement` CAS — if result ≥ 0, done; if < 0, add to CLH (Craig-Landin-Hagersten) queue and park with `LockSupport.park()`. `release()`: `releaseShared(1)` via `getAndAdd(1)` CAS + unpark head of queue. Fair version: always check if queue is non-empty before CAS attempt (enqueue if queue non-empty, even if permits available).

**Level 4 — Why it was designed this way (senior/staff):**
Dijkstra's original P/V semaphore was the foundation for all higher-level synchronisation. The key insight was that both mutual exclusion (P: lock, V: unlock) AND synchronisation (thread A does P, blocks; thread B does V when ready — signals A) could be unified in one primitive. Java's `Semaphore(1)` is a binary semaphore that can be used for signalling: thread A acquires it, thread B releases it when an event occurs — thread A proceeds. This is fundamentally different from a mutex (where A must release what it acquires). The AQS backbone in Java ensures Semaphore, ReentrantLock, and CountDownLatch all use the same efficient CLH queue and LockSupport mechanism, reducing maintenance burden and ensuring consistent performance characteristics.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            COUNTING SEMAPHORE FLOW (N=3)               │
├────────────────────────────────────────────────────────┤
│  sem = Semaphore(3)  // permits = 3                    │
│                                                        │
│  T1: acquire() → CAS(3,2) → permits=2 → proceed       │
│  T2: acquire() → CAS(2,1) → permits=1 → proceed       │
│  T3: acquire() → CAS(1,0) → permits=0 → proceed       │
│  T4: acquire() → CAS(0,-1) → fail → enqueue+park      │
│  T5: acquire() → CAS(0,-2) → fail → enqueue+park      │
│                                                        │
│  T1: release() → CAS(-2,-1) → unpark T4               │
│  T4: resumes → permits=-1 → proceed                   │
│  T2: release() → CAS(-1,0) → unpark T5                │
│  T5: resumes → permits=0 → proceed                    │
│  T3: release() → permits=1 → no waiters               │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

PRODUCER-CONSUMER WITH BOUNDED BUFFER:

```
Semaphore empty = new Semaphore(BUFFER_SIZE);  // tracks empty slots
Semaphore full  = new Semaphore(0);             // tracks filled slots
Mutex mutex = new Mutex();                      // protects buffer access

Producer:
  empty.acquire();  // wait for empty slot
  mutex.lock();
  buffer.add(item);
  mutex.unlock();
  full.release();   // signal item added

Consumer:
  full.acquire();   // wait for item
  mutex.lock();
  item = buffer.take();
  mutex.unlock();
  empty.release();  // signal slot freed
```

This is the classic three-semaphore solution: no busy-waiting, no lost signals, bounded buffer correctly enforced.

FAILURE PATH (release without acquire → "over-release"):

```java
Semaphore sem = new Semaphore(1);
// Accidental extra release:
sem.release();  // permits: 1→2 (should be max 1!)
Thread A: sem.acquire() → permits: 2→1 → proceeds
Thread B: sem.acquire() → permits: 1→0 → proceeds
// TWO threads now hold what should be exclusive!
```

---

### 💻 Code Example

Example 1 — Java Semaphore for connection pool:

```java
public class ConnectionPool {
    private final Semaphore semaphore;
    private final BlockingQueue<Connection> pool;

    public ConnectionPool(int size) {
        semaphore = new Semaphore(size, true);  // fair
        pool = new ArrayBlockingQueue<>(size);
        for (int i = 0; i < size; i++) {
            pool.add(createConnection());
        }
    }

    public Connection acquire(long timeoutMs)
            throws InterruptedException {
        if (!semaphore.tryAcquire(timeoutMs, TimeUnit.MILLISECONDS)) {
            throw new RuntimeException("Connection pool timeout");
        }
        return pool.poll();  // always available after semaphore acquired
    }

    public void release(Connection conn) {
        pool.offer(conn);
        semaphore.release();
    }
}
```

Example 2 — POSIX semaphore in C:

```c
#include <semaphore.h>
#define POOL_SIZE 5

sem_t pool_sem;
sem_init(&pool_sem, 0, POOL_SIZE);  // 5 permits, process-local

// Thread: acquire
sem_wait(&pool_sem);       // blocks if 0
use_resource();
sem_post(&pool_sem);       // release

// With timeout
struct timespec ts;
clock_gettime(CLOCK_REALTIME, &ts);
ts.tv_sec += 5;  // 5 second timeout
int result = sem_timedwait(&pool_sem, &ts);
if (result == -1 && errno == ETIMEDOUT) {
    // timeout — handle gracefully
}
```

Example 3 — Semaphore for signalling (binary semaphore):

```java
// Thread A waits for thread B to complete initialisation
Semaphore ready = new Semaphore(0);  // starts at 0 — A will block

// Thread B: setup
Thread b = new Thread(() -> {
    performSetup();
    ready.release();  // signals A that setup is done
});
b.start();

// Thread A: waits
ready.acquire();  // blocks until B calls release
useSetupResults();
```

Example 4 — Rate limiter using Semaphore + ScheduledExecutor:

```java
// Allow at most 10 requests per second
public class RateLimiter {
    private final Semaphore semaphore = new Semaphore(10);
    private final ScheduledExecutorService scheduler =
        Executors.newScheduledThreadPool(1);

    public RateLimiter() {
        // Refill permits every second
        scheduler.scheduleAtFixedRate(() -> {
            int used = 10 - semaphore.availablePermits();
            if (used > 0) semaphore.release(used);
        }, 1, 1, TimeUnit.SECONDS);
    }

    public boolean tryAcquire() {
        return semaphore.tryAcquire();
    }
}
```

---

### ⚖️ Comparison Table

| Primitive          | Count          | Ownership                  | Signalling | Use For                              |
| ------------------ | -------------- | -------------------------- | ---------- | ------------------------------------ |
| **Semaphore(1)**   | Binary         | None (any thread releases) | Yes        | Cross-thread signal, binary resource |
| Mutex              | Binary         | Owner must release         | No         | Exclusive critical section           |
| **Semaphore(N)**   | Counting       | None                       | No         | Resource pool, concurrency limiter   |
| CountDownLatch     | N→0            | N/A (one-shot)             | Yes        | Wait for N events                    |
| Condition Variable | — (with mutex) | Mutex owner                | Yes        | Wait for condition                   |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                 |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Semaphore(1) == Mutex"                               | Semaphore(1) has no ownership — any thread can release it; this makes it suitable for signalling but not for mutual exclusion where the same thread must always release |
| "acquire/release must be in same thread"              | Explicitly NOT required — this cross-thread signalling is a key semaphore feature (unlike mutex)                                                                        |
| "Semaphore is outdated — use higher-level tools"      | Semaphore is often the right tool for resource counting; `BlockingQueue`, `ThreadPoolExecutor`, and `RateLimiter` are built on semaphore-like internals                 |
| "fair=true is always better"                          | Fair semaphore guarantees FIFO but requires queue management overhead; unfair can be 2–5× faster for high-throughput scenarios                                          |
| "sem.availablePermits() is reliable for flow control" | Non-atomic; by the time you check, another thread may have acquired/released                                                                                            |

---

### 🚨 Failure Modes & Diagnosis

**1. Semaphore Leak (acquire without release)**

Symptom: System gradually slows down; threads increasingly blocked on `acquire()`; `sem.availablePermits()` returns 0.

Root Cause: Release not called in exception path; missing `finally` block.

Diagnostic:

```java
// Java: JStack shows all blocked threads
jstack <PID> | grep -A 10 "acquire\|WAITING"
// Count threads waiting on semaphore vs total threads

// Check current permit count
System.out.println("Permits: " + semaphore.availablePermits());
System.out.println("Queued: " + semaphore.getQueueLength());
```

Fix: Always use try-finally:

```java
semaphore.acquire();
try {
    doWork();
} finally {
    semaphore.release();
}
```

---

**2. Over-Release (release without acquire)**

Symptom: More concurrent users than the semaphore's intended limit; resource pool sees more concurrent holders than capacity.

Root Cause: Release called unconditionally (e.g., in an error handler that runs even when acquire wasn't called); or release called multiple times for one acquire.

Diagnostic:

```java
// Check if permits > initial value
if (semaphore.availablePermits() > INITIAL_PERMITS) {
    log.error("Semaphore over-released: " + semaphore.availablePermits());
}
```

Fix: Track whether acquire was called before release (use a boolean flag per operation).

---

**3. Starvation with Unfair Semaphore Under High Load**

Symptom: Some threads wait indefinitely for permits while others continuously acquire and release; occasional timeout exceptions even when throughput seems fine.

Root Cause: Unfair (non-FIFO) semaphore; high-throughput threads keep being selected for wakeup over low-priority waiters.

Diagnostic:

```java
// Log wait time per thread
long start = System.nanoTime();
semaphore.acquire();
long wait = System.nanoTime() - start;
if (wait > TimeUnit.MILLISECONDS.toNanos(100)) {
    log.warn("Long semaphore wait: {}ms on thread {}",
             wait / 1_000_000, Thread.currentThread().getName());
}
```

Fix: Use `new Semaphore(N, true)` (fair mode) to guarantee FIFO ordering.

Prevention: Profile wait time distribution under load; alert on p99 > expected threshold.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Mutex` — understand 1-holder locking before generalising to N-holder semaphore
- `Thread` — semaphores coordinate threads; need threading fundamentals
- `Concurrency vs Parallelism` — semaphore is a concurrency control tool

**Builds On This (learn these next):**

- `Condition Variable` — combines semaphore-like waiting with mutex-based condition checking
- `Producer-Consumer Pattern` — the classic use case requiring two semaphores
- `Thread Pool` — thread pool implementations use semaphore-like counting for active threads

**Alternatives / Comparisons:**

- `CountDownLatch` — one-shot semaphore; can't be reset; use for "wait for N events once"
- `BlockingQueue` — higher-level bounded queue with implicit semaphore semantics; preferred over raw semaphore for producer-consumer
- `Phaser` — flexible generalization of CountDownLatch and CyclicBarrier; reusable

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Counter-based lock: N threads allowed;   │
│              │ acquire decrements, release increments   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Need to limit concurrent access to       │
│ SOLVES       │ exactly N resources (pool, rate limit)    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ No ownership — any thread can release;   │
│              │ enables cross-thread signalling          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Resource pool sizing; rate limiting;     │
│              │ signalling between threads               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Mutual exclusion (use mutex); one-time   │
│              │ event (use CountDownLatch/CompletableFuture)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Concurrency control vs risk of over-     │
│              │ release if acquire/release mismatched    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "N parking spaces: take a ticket,        │
│              │  return it when done, wait if full"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Condition Variable → BlockingQueue → AQS  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The classic "Dining Philosophers" problem is typically solved with semaphores. Five philosophers sit at a table; each needs two forks (both left and right) to eat; there are five forks. A naive semaphore solution (philosopher i acquires fork i, then fork (i+1)%5) leads to deadlock — all philosophers hold one fork and wait for the other. Describe two semaphore-based solutions that avoid deadlock, and for each, identify whether it prevents starvation or only deadlock.

**Q2.** Java's `Semaphore` uses `AbstractQueuedSynchronizer` which internally uses a CLH (Craig-Landin-Hagersten) spin queue. Each waiting thread spins on a local variable in a predecessor node (not the shared lock variable). This avoids the "thundering herd" problem when many threads are released simultaneously. However, `Semaphore.release(n)` (release N permits at once) calls `releaseShared(n)` which then calls `tryReleaseShared` and `doReleaseShared` in a loop. Under very high contention with N=100 threads waiting and one release(100) call: does AQS wake all 100 threads simultaneously, or sequentially? What is the time complexity of the wake-up process, and at what thread count does the overhead of the CLH queue traversal become noticeable?
