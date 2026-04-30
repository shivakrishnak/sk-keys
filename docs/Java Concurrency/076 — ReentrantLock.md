---
layout: default
title: "ReentrantLock"
parent: "Java Concurrency"
nav_order: 76
permalink: /java-concurrency/reentrantlock/
---
# 076 — ReentrantLock

`#java` `#concurrency` `#locks` `#threading` `#advanced`

⚡ TL;DR — ReentrantLock is an explicit java.util.concurrent lock offering the same mutual exclusion as `synchronized` plus `tryLock` (non-blocking acquisition), timed waits, interruptible lock acquisition, fairness, and `Condition` variables for fine-grained wait/notify.

| #076 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | synchronized, Thread Lifecycle, Deadlock, Condition | |
| **Used by:** | Deadlock Prevention, tryLock, ReadWriteLock, Condition | |

---

### 📘 Textbook Definition

`java.util.concurrent.locks.ReentrantLock` implements the `Lock` interface and provides the same reentrant mutual exclusion semantics as `synchronized`, with additional capabilities: `tryLock()` (non-blocking attempt), `tryLock(time, unit)` (timed attempt), `lockInterruptibly()` (interruptible blocking), and constructor argument `fair = true` (FIFO ordering). `Condition` objects (created via `lock.newCondition()`) replace `Object.wait/notify`, supporting multiple wait queues per lock.

---

### 🟢 Simple Definition (Easy)

`ReentrantLock` is a more powerful padlock than `synchronized`. Same idea: one thread at a time. But the extra features: "Try the door for 5 seconds — if still locked, give up and do something else." Or: "Put me in line fairly — don't let anyone cut ahead." `synchronized` has neither.

---

### 🔵 Simple Definition (Elaborated)

`synchronized` is convenient but inflexible: you either wait for the lock indefinitely, you can't be interrupted while waiting, and `wait/notify` only supports one condition per monitor. `ReentrantLock` solves all three: `tryLock(timeout)` prevents deadlocks; `lockInterruptibly()` lets the thread be cancelled while waiting; multiple `Condition` objects support producer/consumer queues where "buffer not empty" and "buffer not full" are separate conditions you can wait on and signal independently.

---

### 🔩 First Principles Explanation

**What synchronized can't do:**

```
Problem 1: Deadlock due to indefinite waiting
   synchronized (lockA) {
       synchronized (lockB) { ... }  // blocks forever if B held
   }
   No way to "give up after 2 seconds"

Problem 2: Can't be interrupted while waiting for lock
   Thread blocked on synchronized cannot be interrupted
   → Can't implement cancellable operations cleanly

Problem 3: Only ONE wait queue per object
   Object.wait() / notify()
   In a bounded buffer:
     producer waits when FULL
     consumer waits when EMPTY
   Both share ONE condition → notifyAll() wakes BOTH
   → producers woken when there's space meant for consumers → noise

ReentrantLock solves all three:
  lock.tryLock(2, SECONDS)  → give up if not acquired
  lock.lockInterruptibly()  → interrupted waiting thread throws InterruptedException
  lock.newCondition()       → separate condition per scenario (notFull, notEmpty)
```

**How tryLock prevents deadlock:**

```
Standard synchronized: Thread blocks indefinitely
  Deadlock: A holds X, waits for Y
            B holds Y, waits for X → stuck forever

With tryLock:
  Thread A:
    lockX.lock();
    if (lockY.tryLock(100, MILLISECONDS)) {
        try { doWork(); }
        finally { lockY.unlock(); lockX.unlock(); }
    } else {
        lockX.unlock();  // release X, back off, retry later
    }
  → No deadlock: one thread gives up → other proceeds
```

---

### ❓ Why Does This Exist — Why Before What

```
synchronized (Java 1.0) limitations:
  ✗ No way to abort waiting for a lock (tryLock)
  ✗ No way to be interrupted while blocked
  ✗ No fairness guarantee (threads may starve)
  ✗ One condition per lock (wait/notify)
  ✗ Cannot test if lock is held diagnostically

ReentrantLock (Java 5, java.util.concurrent):
  ✅ tryLock() — non-blocking or timed lock attempt
  ✅ lockInterruptibly() — responds to Thread.interrupt() while waiting
  ✅ Fair mode — threads served in FIFO order (prevents starvation)
  ✅ Multiple Conditions — separate wait queues per lock
  ✅ isHeldByCurrentThread(), getQueueLength() — for diagnostics

When to prefer synchronized:
  → Simpler code, no need for advanced features
  → JIT optimises synchronized well (biased locking, lock elision)
  → No extra try/finally needed
```

---

### 🧠 Mental Model / Analogy

> `synchronized` is a simple **velvet rope** — you wait in line until it drops. `ReentrantLock` is a **numbered ticket system with options**: you can take a ticket and check back (tryLock), you can leave if you get a phone call while waiting (lockInterruptibly), there are separate queues for different services (Conditions), and you can request "fair queue" so nobody cuts in. Much more control — but you must remember to return your ticket (unlock in finally).

---

### ⚙️ How It Works

```
Lock interface key methods:
  lock()                           → block until acquired (like synchronized)
  lockInterruptibly()              → block, but respond to interrupt
  tryLock()                        → acquire immediately or return false
  tryLock(long time, TimeUnit unit)→ try for specified time
  unlock()                         → MUST be in finally block
  newCondition()                   → create a Condition for this lock

Condition interface:
  condition.await()                → like Object.wait() — releases lock, waits
  condition.await(time, unit)      → timed await
  condition.signal()               → like Object.notify() — wake one waiter
  condition.signalAll()            → like Object.notifyAll() — wake all waiters

Fairness:
  new ReentrantLock(true)          → fair: threads served in FIFO arrival order
  new ReentrantLock(false)         → non-fair (default): better throughput, possible starvation
  Fairness cost: ~10× lower throughput due to OS scheduling overhead
```

---

### 🔄 How It Connects

```
ReentrantLock
  │
  ├─ vs synchronized ──→ same mutual exclusion + advanced features
  ├─ tryLock         ──→ deadlock prevention, timeout acquisition
  ├─ Condition       ──→ fine-grained wait/notify (multiple queues)
  │
  ├─ extends to:
  │   ReadWriteLock  ──→ multiple readers OR one writer (ReentrantReadWriteLock)
  │   StampedLock    ──→ optimistic read mode (Java 8, highest performance)
  │
  └─ Always: lock.unlock() in finally block
```

---

### 💻 Code Example

```java
// Basic usage — always unlock in finally
private final ReentrantLock lock = new ReentrantLock();
private int count = 0;

public void increment() {
    lock.lock();
    try {
        count++;
    } finally {
        lock.unlock(); // MUST be in finally — releases even if exception thrown
    }
}
```

```java
// tryLock — non-blocking, deadlock-avoiding
public boolean transferMoney(Account from, Account to, double amount)
    throws InterruptedException {

    while (true) {
        if (from.lock.tryLock(100, TimeUnit.MILLISECONDS)) {
            try {
                if (to.lock.tryLock(100, TimeUnit.MILLISECONDS)) {
                    try {
                        from.balance -= amount;
                        to.balance   += amount;
                        return true;
                    } finally {
                        to.lock.unlock();
                    }
                }
            } finally {
                from.lock.unlock();
            }
        }
        // Failed to acquire both — back off before retrying
        Thread.sleep(ThreadLocalRandom.current().nextInt(1, 10));
    }
}
```

```java
// Multiple Conditions — bounded buffer (producer-consumer)
public class BoundedBuffer<T> {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();

    private final Object[] items;
    private int head, tail, count;

    public BoundedBuffer(int capacity) { items = new Object[capacity]; }

    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (count == items.length) notFull.await();  // wait for space
            items[tail] = item;
            tail = (tail + 1) % items.length;
            count++;
            notEmpty.signal();  // only wakes a WAITING CONSUMER — not producers
        } finally { lock.unlock(); }
    }

    @SuppressWarnings("unchecked")
    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0) notEmpty.await();  // wait for an item
            T item = (T) items[head];
            head = (head + 1) % items.length;
            count--;
            notFull.signal();  // only wakes a WAITING PRODUCER — not consumers
            return item;
        } finally { lock.unlock(); }
    }
}
// With synchronized: notifyAll() wakes BOTH producers AND consumers on every signal
// With ReentrantLock: notFull.signal() wakes ONLY producers → far less contention
```

```java
// lockInterruptibly — cancellable lock acquisition
public void doWorkWithCancellation() throws InterruptedException {
    lock.lockInterruptibly(); // throws InterruptedException if thread interrupted while waiting
    try {
        performWork();
    } finally {
        lock.unlock();
    }
}
// Useful in task cancellation scenarios:
// thread.interrupt() will break out of lockInterruptibly
// synchronized block would ignore the interrupt (thread stays blocked)
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Fair lock is always better | Fair mode costs ~10× throughput; use only when starvation is a proven problem |
| `unlock()` can be anywhere in the method | Must ALWAYS be in `finally` — exception before try block reaches unlock = lock leak |
| `tryLock()` with no args is always good | Non-timed `tryLock()` is non-blocking — returns immediately if not available; rarely what you want |
| ReentrantLock is faster than synchronized | Synchronized has JIT biased-locking optimizations; ReentrantLock wins only in high-contention + tryLock scenarios |
| ReentrantLock prevents all deadlocks | It enables AVOIDANCE via tryLock; it doesn't magically prevent deadlock if you always call `lock()` |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Forgetting unlock() — lock leak**

```java
// ❌ If someMethod() throws, lock is NEVER released → all other threads block forever
lock.lock();
someMethod();         // throws RuntimeException
lock.unlock();        // never reached!

// ✅ Always unlock in finally
lock.lock();
try {
    someMethod();
} finally {
    lock.unlock();
}
```

**Pitfall 2: Calling lock.unlock() when not holding the lock**

```java
// If lock.lock() is never called (e.g. code path skipped):
finally { lock.unlock(); }  // ❌ throws IllegalMonitorStateException

// Fix: gate unlock on whether lock was actually acquired
boolean acquired = lock.tryLock();
try {
    if (acquired) { doWork(); }
} finally {
    if (acquired) lock.unlock();
}
```

**Pitfall 3: Using Condition.await() outside lock**

```java
// ❌ Must own the lock before calling await()
condition.await(); // throws IllegalMonitorStateException

// ✅ Correct pattern
lock.lock();
try {
    while (!conditionMet) condition.await();
    doWork();
} finally { lock.unlock(); }
```

---

### 🔗 Related Keywords

- **[synchronized](./069 — synchronized.md)** — built-in simpler alternative
- **[Deadlock](./071 — Deadlock.md)** — `tryLock` is the primary tool to prevent it
- **[Thread Lifecycle](./068 — Thread Lifecycle.md)** — `lockInterruptibly` affects BLOCKED→WAITING transitions
- **[Race Condition](./072 — Race Condition.md)** — what ReentrantLock prevents
- **ReadWriteLock** — allow multiple concurrent readers; extends ReentrantLock concept
- **StampedLock** — Java 8 successor with optimistic reads (highest throughput)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Explicit lock with tryLock, timed waits,      │
│              │ interruptibility, fairness, and Conditions    │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Need tryLock (deadlock avoidance), multiple   │
│              │ Conditions, interruptible lock, or fairness   │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Simple mutex is enough — synchronized is      │
│              │ shorter, JIT-optimised, no finally needed     │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "synchronized with superpowers —              │
│              │  but always unlock() in finally"              │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ReadWriteLock → StampedLock → Condition →     │
│              │ Semaphore → CountDownLatch                    │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `ReentrantLock` is reentrant — a thread holding the lock can call `lock.lock()` again without deadlocking. What does the lock count track? What must happen for the lock to actually be released?

**Q2.** You have a `new ReentrantLock(true)` (fair). Under sustained contention, throughput drops significantly. Why does fairness have such a large performance cost? What mechanism causes this?

**Q3.** How does `Condition.await()` differ from `Object.wait()` in terms of which lock is released, and what happens after the thread is signalled? Draw the state diagram for the calling thread.

