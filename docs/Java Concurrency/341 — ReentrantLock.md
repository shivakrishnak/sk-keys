---
layout: default
title: "ReentrantLock"
parent: "Java Concurrency"
nav_order: 341
permalink: /java-concurrency/reentrant-lock/
number: "0341"
category: Java Concurrency
difficulty: ★★★
depends_on: synchronized, wait / notify / notifyAll, Thread Lifecycle
used_by: ReadWriteLock, Condition, StampedLock
related: synchronized, ReadWriteLock, StampedLock
tags:
  - java
  - concurrency
  - locking
  - deep-dive
  - advanced
---

# 0341 — ReentrantLock

⚡ TL;DR — `ReentrantLock` is a flexible, explicit lock providing everything `synchronized` does, plus: attempt without blocking (`tryLock`), timed acquisition, interruptible waiting, multiple `Condition` objects per lock, and optional fairness — at the cost of manual `try/finally` release.

| #0341 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | synchronized, wait / notify / notifyAll, Thread Lifecycle | |
| **Used by:** | ReadWriteLock, Condition, StampedLock | |
| **Related:** | synchronized, ReadWriteLock, StampedLock | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
`synchronized` blocks the calling thread until the lock is available — no timeout, no "try and fail quickly," no way to interrupt a thread waiting for a lock. In a banking system, a transaction waiting for 10 seconds to acquire a lock is a poor user experience. Without tryLock, the thread waits forever (or until deadlock detection, which is too late).

THE BREAKING POINT:
A timeout-sensitive trading system tries to acquire a lock to update a position. The lock is held by a GC thread doing cleanup. The trading thread blocks for 500ms — way past the SLA. With `synchronized`, there's no way to abort the lock attempt after a timeout. The thread can't be interrupted while waiting for a `synchronized` lock.

THE INVENTION MOMENT:
This is exactly why **`ReentrantLock`** was created — to give developers full control over lock acquisition: try without blocking, try with timeout, interrupt while waiting, and support multiple independent conditions per lock.

---

### 📘 Textbook Definition

**`ReentrantLock`** is a lock implementation in `java.util.concurrent.locks` (Java 5+) that implements `Lock` interface and provides the same mutual exclusion and memory visibility as `synchronized`, plus extended capabilities: `lock()` — unconditional acquisition; `tryLock()` — immediate non-blocking attempt; `tryLock(timeout, unit)` — timed attempt; `lockInterruptibly()` — acquisition that can be interrupted; `newCondition()` — creates a `Condition` for selective thread coordination; constructor flag `fair=true` — FIFO ordering of waiting threads. Is reentrant: the holding thread can re-acquire without deadlock.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`ReentrantLock` = `synchronized` + timeout + interruptibility + multiple conditions + fairness option.

**One analogy:**
> A hotel check-in desk with a "I'll wait 5 minutes" option. With `synchronized` (basic), you stand in line until served — no leaving. With `ReentrantLock`: you can say "I'll wait exactly 5 minutes" (`tryLock(5, MINUTES)`), "I'll wait unless someone cancels my request" (`lockInterruptibly()`), or "just check if the desk is free and leave if not" (`tryLock()`). The desk itself still serves one person at a time.

**One insight:**
The MUST-USE pattern for `ReentrantLock` is `try/finally` — unlike `synchronized`, exceptions don't auto-release the lock. Forgetting `finally { lock.unlock(); }` means the lock is never released, causing permanent deadlock.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. `ReentrantLock` provides mutual exclusion and memory visibility identical to `synchronized`.
2. Lock must be manually released in a `finally` block — the JVM NEVER auto-releases a `ReentrantLock`.
3. A thread holding the lock can re-acquire it (reentrancy) — must release exactly as many times as acquired.

DERIVED DESIGN:
`ReentrantLock` is built on `AbstractQueuedSynchronizer` (AQS) — Doug Lea's framework that manages a queue of waiting threads using CAS operations and `LockSupport.park/unpark`. AQS provides both fair and non-fair modes. Non-fair (default) allows "barge-in" — a thread trying to acquire may succeed immediately even if others are waiting (lower latency). Fair mode processes threads strictly in FIFO order (avoids starvation, but slower).

```
AQS Internal Structure:
  State: int (0 = unlocked, N = N reentrant acquisitions)
  Owner: thread reference (reentrant check)
  Wait queue: CLH doubly-linked queue of parked waiters
  
  tryLock(): CAS state 0→1 (no queue)
  lock():    CAS state 0→1, or enqueue + park
  unlock():  decrement state, unpark head of queue
```

THE TRADE-OFFS:
Gain: tryLock, timeout, interruption, multiple conditions, fairness option; same mutual exclusion and visibility as synchronized.
Cost: MUST use try/finally; more verbose; slightly higher overhead than uncontended `synchronized`; forgetting unlock = permanent deadlock.

---

### 🧪 Thought Experiment

SETUP:
A distributed lock manager needs to acquire a lock or fail fast (SLA: max 50ms wait).

WITHOUT ReentrantLock:
```java
synchronized (resource) {
    // If resource is locked, waits indefinitely
    // Cannot time out — SLA impossible to enforce
    performUpdate(resource);
}
```

WITH ReentrantLock:
```java
ReentrantLock lock = getLockFor(resource);
if (lock.tryLock(50, TimeUnit.MILLISECONDS)) {
    try {
        performUpdate(resource);
    } finally {
        lock.unlock(); // NEVER FORGET THIS
    }
} else {
    throw new TimeoutException(
        "Could not acquire lock within 50ms"
    );
}
```

THE INSIGHT:
`tryLock(timeout)` enables SLA-enforced locking — the system fails gracefully rather than blocking indefinitely. This pattern is essential for latency-sensitive systems.

---

### 🧠 Mental Model / Analogy

> `ReentrantLock` is a turnstile with a VIP card reader and a timer. `lock()` — go through the regular turnstile (wait indefinitely). `tryLock()` — tap the VIP reader; if busy, come back later. `tryLock(5, SECONDS)` — tap and wait 5 seconds; leave if not through. `lockInterruptibly()` — go through unless security cancels your ticket. The turnstile still only lets one person through at a time.

"Regular turnstile" → `lock()` — indefinite wait.
"5-second VIP reader timeout" → `tryLock(5, SECONDS)`.
"Security cancels ticket" → `lockInterruptibly()` + `Thread.interrupt()`.

Where this analogy breaks down: A real turnstile releases automatically when you walk away. `ReentrantLock` does NOT release automatically — you must call `unlock()` explicitly in `finally`.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `ReentrantLock` is a better version of `synchronized` that lets you ask "please give me the lock, but I'll only wait 5 seconds."

**Level 2:** Use `tryLock()` for non-blocking acquisition, `tryLock(timeout)` for timed acquisition. Always `unlock()` in `finally`. Use `lockInterruptibly()` when the waiting thread should respond to interrupts. Use `newCondition()` for multiple conditions per lock. Use `fair=true` for FIFO ordering.

**Level 3:** Internally uses AQS with a CLH queue. `lock()` first attempts a non-fair CAS `state: 0→1`. On failure, enqueues in the CLH queue and calls `LockSupport.park()`. The thread head of the queue is unparked by `unlock()`. Fair mode skips the initial CAS barge-in and directly enqueues.

**Level 4:** AQS is the backbone of nearly all `java.util.concurrent` locks and synchronizers: `ReentrantLock`, `Semaphore`, `CountDownLatch`, `CyclicBarrier`, `LinkedBlockingQueue`. Understanding AQS state machine, CLH queue, and park/unpark is the foundation for implementing custom concurrent data structures. The design choice of CAS + park/unpark (vs OS mutexes) allows the JVM to optimise lock contention without OS kernel involvement for uncontended cases.

---

### ⚙️ How It Works (Mechanism)

**Standard usage (always try/finally):**
```java
ReentrantLock lock = new ReentrantLock();

lock.lock(); // block until acquired
try {
    // critical section
    updateSharedState();
} finally {
    lock.unlock(); // ALWAYS release — even on exception
}
```

**tryLock (non-blocking):**
```java
if (lock.tryLock()) {
    try {
        updateSharedState();
    } finally {
        lock.unlock();
    }
} else {
    // couldn't acquire — do fallback
    returnStaleData();
}
```

**tryLock with timeout:**
```java
try {
    if (lock.tryLock(100, TimeUnit.MILLISECONDS)) {
        try { updateSharedState(); }
        finally { lock.unlock(); }
    } else {
        throw new TimeoutException("Lock timeout");
    }
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
    throw new RuntimeException("Interrupted acquiring lock", e);
}
```

**Multiple conditions per lock:**
```java
ReentrantLock lock = new ReentrantLock();
Condition notFull  = lock.newCondition(); // signal producers
Condition notEmpty = lock.newCondition(); // signal consumers

// Producer:
lock.lock();
try {
    while (full()) notFull.await();  // wait for space
    add(item);
    notEmpty.signal();               // signal one consumer
} finally { lock.unlock(); }

// Consumer:
lock.lock();
try {
    while (empty()) notEmpty.await(); // wait for item
    T item = remove();
    notFull.signal();                 // signal one producer
} finally { lock.unlock(); }
// Better than notifyAll: signals the right condition
```

**Fair lock for FIFO ordering:**
```java
ReentrantLock fairLock = new ReentrantLock(true); // fair=true
// Threads acquire IN ORDER of waiting
// Prevents starvation but reduces throughput (no barge-in)
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Thread T1: lock.lock()]
    → [AQS CAS state 0→1: success]    ← YOU ARE HERE
    → [owner = T1]
    → [T2: lock.lock() → CAS fails]
    → [T2: enqueued in CLH, park()]
    → [T1: completes critical section]
    → [T1: lock.unlock()]
    → [AQS state 1→0, unpark(head=T2)]
    → [T2: CAS 0→1: success]
    → [T2: executes critical section]
```

FAILURE PATH (forgetting unlock):
```
[lock.lock() — acquired]
    → [Exception thrown in critical section]
    → [No finally block → lock.unlock() NOT called]
    → [Lock permanently held by T1 (even after T1 ends)]
    → [All subsequent lock.lock() calls: WAITING forever]
    → [Deadlock: invisible in thread dump (state=WAITING)]
```

WHAT CHANGES AT SCALE:
At scale, fair `ReentrantLock` prevents starvation but reduces throughput by preventing barge-in. Non-fair (default) has higher throughput but can starve low-priority threads. `StampedLock` (Java 8) adds optimistic reads for read-heavy workloads — faster than `ReadWriteLock` when contention is low. Choose the right lock type for the contention pattern.

---

### 💻 Code Example

Example 1 — Thread-safe cache with ReentrantLock:
```java
public class Cache<K, V> {
    private final Map<K, V> map = new HashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public V get(K key) {
        lock.lock();
        try { return map.get(key); }
        finally { lock.unlock(); }
    }

    public void put(K key, V value) {
        lock.lock();
        try { map.put(key, value); }
        finally { lock.unlock(); }
    }

    public V getOrCompute(K key, Function<K, V> computeFn) {
        lock.lock();
        try {
            V cached = map.get(key);
            if (cached == null) {
                cached = computeFn.apply(key);
                map.put(key, cached);
            }
            return cached;
        } finally { lock.unlock(); }
    }
}
```

Example 2 — Deadlock avoidance with tryLock:
```java
// Transfer between two accounts — acquire both locks,
// fail if can't get both (avoids deadlock):
boolean transfer(Account from, Account to, BigDecimal amount) {
    Lock lock1 = getLockFor(from);
    Lock lock2 = getLockFor(to);
    while (true) {
        if (lock1.tryLock()) {
            try {
                if (lock2.tryLock()) {
                    try {
                        from.debit(amount);
                        to.credit(amount);
                        return true;
                    } finally { lock2.unlock(); }
                }
            } finally { lock1.unlock(); }
        }
        Thread.yield(); // back off before retry
    }
}
```

---

### ⚖️ Comparison Table

| Feature | synchronized | ReentrantLock |
|---|---|---|
| Mutual exclusion | Yes | Yes |
| Memory visibility | Yes | Yes |
| Reentrancy | Yes | Yes |
| tryLock | No | Yes |
| Timeout | No | Yes (tryLock) |
| Interruptible wait | No | Yes (lockInterruptibly) |
| Multiple conditions | No (only 1 via Object.wait) | Yes (newCondition()) |
| Fair ordering | No | Optional (constructor) |
| Auto-release on exception | Yes | **No — must use finally** |
| Syntax | Keyword (simpler) | Explicit try/finally |

How to choose: Use `synchronized` when its simplicity is sufficient. Use `ReentrantLock` when you need timeout, interruption, multiple conditions, or fairness. Always use `try/finally` with `ReentrantLock`.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ReentrantLock is always faster than synchronized | For uncontended cases, JVM-optimized `synchronized` (biased locking) is often faster than `ReentrantLock`. Under contention, performance is comparable. Correctness, not speed, is the primary reason to choose ReentrantLock |
| lock() can be placed outside try/finally | Only safe if lock acquisition itself can throw. In practice, always place `lock.unlock()` in `finally` — even if the acquire can fail, the unlock is harmless (throws `IllegalMonitorStateException` if not locked, which is caught or propagates) |
| tryLock() is non-reentrant | `tryLock()` IS reentrant — a thread already holding the lock can successfully `tryLock()` |
| Fair ReentrantLock prevents starvation absolutely | Fair fairness ordering prevents starvation for the queue, but threads outside the queue that haven't called `lock()` yet are not protected. New arrivals always enqueue behind existing waiters in fair mode |

---

### 🚨 Failure Modes & Diagnosis

**Lock Not Released (Missing Finally)**

Symptom: All threads WAITING on lock.lock(). Application deadlocked.

Root Cause: `lock.unlock()` not in `finally` block. Exception prevented unlock.

Diagnostic:
```bash
jstack <pid> | grep "WAITING" | head -20
# Shows all threads waiting on LockSupport.park
# (ReentrantLock contention shows as WAITING, not BLOCKED)
# Look for lock owner: jstack shows which thread "owns" the lock
```

Fix:
```java
lock.lock();
try {
    riskyOperation(); // might throw
} finally {
    lock.unlock(); // ALWAYS released
}
```

---

**Deadlock with tryLock (Livelock variant)**

Symptom: System makes no progress but no thread is permanently blocked. CPU high.

Root Cause: Two threads each call `tryLock()` on two locks, always fail simultaneously, release, and retry — indefinitely.

Fix: Add random or exponential backoff between retries. Or use a lock ordering protocol.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `synchronized` — ReentrantLock is an alternative to synchronized; understanding synchronized is prerequisite
- `wait / notify / notifyAll` — Condition (from ReentrantLock) replaces wait/notify; understanding wait/notify contextualises Condition

**Builds On This (learn these next):**
- `ReadWriteLock` — extension of ReentrantLock for read-heavy workloads
- `StampedLock` — optimistic lock for maximum read performance

**Alternatives / Comparisons:**
- `synchronized` — simpler, auto-releasing, no features; best for simple critical sections
- `ReadWriteLock` — extends the concept for reader-writer separation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Explicit lock with tryLock, timeout,      │
│              │ interruptibility, Conditions, fairness    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ synchronized blocks indefinitely with no  │
│ SOLVES       │ timeout, no interruptibility, one condition│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ALWAYS unlock in finally. Missing finally  │
│              │ = permanent deadlock (no auto-release)    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need timeout, interruption, or multiple   │
│              │ conditions on one lock                    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple critical sections — use synchronized│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Power (timeout, conditions) vs verbosity  │
│              │ (try/finally requirement)                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "synchronized + timeout + conditions —    │
│              │  but you MUST unlock manually"            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ReadWriteLock → StampedLock →             │
│              │ AbstractQueuedSynchronizer                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A connection pool implementation uses a `ReentrantLock` with a `Condition notEmpty` to implement `borrowConnection()`: waits on `notEmpty` when pool is empty, signalled by `returnConnection()`. Under high load, all 50 borrowers are waiting on `notEmpty`. One connection is returned. `notEmpty.signal()` wakes ONE waiter. That waiter borrows, returns quickly, and signals again. Explain why this implementation can still cause starvation for some borrowers indefinitely — what ordering guarantee `signal()` provides vs `signalAll()`, and trace a specific scenario where borrower #47 never executes despite 1,000 borrow/return cycles.

**Q2.** `AbstractQueuedSynchronizer` (AQS) is the foundation for `ReentrantLock`, `Semaphore`, and `CountDownLatch`. AQS uses a single `volatile int state` variable and a CLH queue. Explain precisely: how does `ReentrantLock` use `state` to implement reentrancy (what value means "not held", "held once", "held twice"), how does `Semaphore` use the same `state` field differently, and why can't AQS's CLH queue be a simple `java.util.LinkedList` with `Collections.synchronizedList()` — what property of AQS's queue design is essential for correctness under concurrent insertions without a separate lock?

