---
layout: default
title: "Semaphore"
parent: "Java Concurrency"
nav_order: 356
permalink: /java-concurrency/semaphore/
number: "356"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, synchronized, Thread Lifecycle
used_by: Connection Pools, Rate Limiting, Resource Throttling
tags: #java, #concurrency, #synchronizer, #resource-control
---

# 356 — Semaphore

`#java` `#concurrency` `#synchronizer` `#resource-control`

⚡ TL;DR — A Semaphore maintains N permits; threads must acquire a permit before accessing a resource and release it after — limiting concurrent access to at most N threads at once; unlike synchronized, it is not tied to a specific object.

| #356 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, synchronized, Thread Lifecycle | |
| **Used by:** | Connection Pools, Rate Limiting, Resource Throttling | |

---

### 📘 Textbook Definition

`java.util.concurrent.Semaphore` maintains a count of available **permits**. `acquire()` blocks until a permit is available, then decrements the count. `release()` increments the count and potentially unblocks waiting threads. A **binary semaphore** (N=1) provides mutual exclusion like `synchronized` but without lock ownership — any thread can release it. A **counting semaphore** (N>1) limits concurrent access to N threads simultaneously.

---

### 🟢 Simple Definition (Easy)

A parking lot with N spaces. Cars (threads) can only enter if a space is available (`acquire()`). When they leave, they free the space (`release()`). If the lot is full, newcomers wait. Never more than N cars inside at once.

---

### 🔵 Simple Definition (Elaborated)

Semaphore is the right tool when you need to limit how many threads can do something simultaneously — not "one at a time" (that's a mutex/lock), but "N at a time." Classic examples: limit to 10 concurrent HTTP connections to an external API; limit to 5 database connections; throttle a rate-limited endpoint. Unlike `ReentrantLock`, the thread that acquires the permit doesn't have to be the same thread that releases it.

---

### 🔩 First Principles Explanation

```
Problem: an external API supports max 10 concurrent requests.
Without Semaphore:
  100 threads all fire simultaneously → API throttled, errors returned

With Semaphore(10):
  semaphore = new Semaphore(10)
  Each thread: semaphore.acquire() → do request → semaphore.release()
  → At most 10 requests concurrent, rest queue up → no API overload

Binary semaphore (N=1) vs synchronized:
  synchronized: only the owning thread can release (reentrant)
  Semaphore(1):  ANY thread can release — enables producer/consumer handoff patterns
                 where one thread acquires and a different thread releases
```

---

### 🧠 Mental Model / Analogy

> A library checkout system for N physical copies of a book. If all copies are checked out, you wait. When someone returns one (`release()`), the next waiting person gets it (`acquire()` unblocked). The librarian doesn't care who returns the book — it doesn't have to be the same person who borrowed it.

---

### ⚙️ How It Works

```
new Semaphore(int permits)
new Semaphore(int permits, boolean fair)  // fair = FIFO ordering

void acquire()                     → block until permit available
void acquire(int n)                → acquire n permits atomically
boolean tryAcquire()               → immediately return false if unavailable
boolean tryAcquire(long, TimeUnit) → timed attempt
void release()                     → return 1 permit
void release(int n)                → return n permits

int availablePermits()             → current count (diagnostic)
int getQueueLength()               → waiting thread count (diagnostic)

Note: release() can be called MORE times than acquire()
→ permits can grow beyond initial count (unlike synchronized)
→ This is a feature (dynamic throttle adjustment) and a risk (bug)
```

---

### 🔄 How It Connects

```
Semaphore
  ├─ N=1 (binary) → non-reentrant mutex; any-thread release
  ├─ N>1 (counting) → resource pool throttle
  ├─ vs synchronized → synchronized is per-object, reentrant, same-thread unlock
  ├─ vs ReentrantLock → lock is per-object, reentrant; semaphore is per-permit
  ├─ fair=true → FIFO reduces starvation at throughput cost
  └─ Use in resource pools: DB connections, thread pools, HTTP clients
```

---

### 💻 Code Example

```java
// Rate limiter: at most 5 concurrent DB operations
public class ConnectionThrottle {
    private final Semaphore permits = new Semaphore(5, true); // fair

    public <T> T executeWithDB(Callable<T> query) throws Exception {
        permits.acquire();
        try {
            return query.call();
        } finally {
            permits.release(); // always release in finally
        }
    }
}
```

```java
// Bounded pool using Semaphore
public class BoundedPool<T> {
    private final Queue<T> pool = new ConcurrentLinkedQueue<>();
    private final Semaphore available;

    public BoundedPool(List<T> resources) {
        pool.addAll(resources);
        available = new Semaphore(resources.size(), true);
    }

    public T acquire() throws InterruptedException {
        available.acquire();
        return pool.poll();  // guaranteed non-null due to semaphore
    }

    public void release(T resource) {
        pool.offer(resource);
        available.release();
    }
}
```

```java
// tryAcquire — non-blocking attempt with fallback
if (semaphore.tryAcquire(500, TimeUnit.MILLISECONDS)) {
    try {
        callExternalService();
    } finally {
        semaphore.release();
    }
} else {
    returnCachedResult(); // graceful degradation
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Semaphore(1) is the same as synchronized | Semaphore(1) is non-reentrant; `synchronized` on same object IS reentrant |
| The thread that acquired must release | ANY thread can call release() on a Semaphore — by design |
| release() without prior acquire() throws | It increases permits beyond initial count — a logic bug, not an exception |
| Semaphore is always fair | Default constructor is NON-fair; pass `true` explicitly for FIFO |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Forgetting release() in finally — permits leak → deadlock**

```java
semaphore.acquire();
doWork();          // if this throws, permit is never released
semaphore.release();

// Fix:
semaphore.acquire();
try { doWork(); } finally { semaphore.release(); } // ✅
```

**Pitfall 2: Calling release() without acquire() — permit count bloats**

```java
// Bug: conditional release in error handler called even without prior acquire
if (error) semaphore.release(); // ❌ — bloats permit count silently

// Fix: track whether acquire() succeeded
boolean acquired = semaphore.tryAcquire();
try { if (acquired) doWork(); }
finally { if (acquired) semaphore.release(); }
```

---

### 🔗 Related Keywords

- **[ReentrantLock](./076 — ReentrantLock.md)** — single-permit reentrant alternative
- **[CountDownLatch](./078 — CountDownLatch.md)** — coordination, not resource control
- **[BlockingQueue](./081 — BlockingQueue.md)** — higher-level producer/consumer
- **[ExecutorService](./074 — ExecutorService.md)** — thread pool is an alternative to manual semaphore throttle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ N permit pool — acquire blocks if 0 permits; │
│              │ release returns one; limit N concurrent users │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Throttle concurrent access: N DB connections, │
│              │ N API calls, N file handles                   │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Need reentrant mutual exclusion → synchronized│
│              │ or ReentrantLock; coordination → CountDownLatch│
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "A parking lot: N spaces, arrive and leave    │
│              │  in any order — no assigned spots"            │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ BlockingQueue → ReentrantLock → Rate Limiting │
│              │ → Connection Pool patterns                    │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You use a `Semaphore(5)` to throttle 5 concurrent API calls. A thread calls `acquire()` but then a `RuntimeException` is thrown before `release()` in the finally. How does the permit count change? What happens over time if this bug occurs repeatedly?

**Q2.** Can you implement a `CountDownLatch` using a `Semaphore`? What about the reverse? What are the differences in semantics?

**Q3.** What is the practical difference between `new Semaphore(1)` and `synchronized(lock) {}`? Give a scenario where you MUST use a Semaphore instead of synchronized.

