---
layout: default
title: "wait / notify / notifyAll"
parent: "Java Concurrency"
nav_order: 340
permalink: /java-concurrency/wait-notify-notifyall/
number: "0340"
category: Java Concurrency
difficulty: ★★★
depends_on: synchronized, Thread Lifecycle, Thread States, Memory Barrier
used_by: ReentrantLock, BlockingQueue, Semaphore
related: synchronized, ReentrantLock, Condition
tags:
  - java
  - concurrency
  - synchronization
  - deep-dive
  - thread-coordination
---

# 0340 — wait / notify / notifyAll

⚡ TL;DR — `wait()` releases a monitor lock and pauses a thread until another thread calls `notify()` or `notifyAll()` on the same object — the fundamental Java mechanism for condition-based thread coordination, but prone to spurious wakeups and difficult to use correctly.

| #0340 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | synchronized, Thread Lifecycle, Thread States, Memory Barrier | |
| **Used by:** | ReentrantLock, BlockingQueue, Semaphore | |
| **Related:** | synchronized, ReentrantLock, Condition | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Thread T1 produces items, Thread T2 consumes them. T2 needs to wait when the buffer is empty. Without wait/notify, T2 must busy-wait (spin):
```java
while (buffer.isEmpty()) { /* spin */ } // consumes 100% CPU doing nothing
```
Spinning is wasteful — T2 uses an entire CPU core just checking a condition that doesn't change until T1 produces. It also prevents T1 from running on single-core systems (or under heavy multi-core load).

THE BREAKING POINT:
A producer-consumer system with 100 consumer threads. Without wait/notify, all 100 threads spin when the queue is empty. 100% CPU consumed by busy-waiting. Producers can't get CPU time to produce items. System deadlocks under its own spinning.

THE INVENTION MOMENT:
This is exactly why **`wait/notify`** was created — to allow a thread to release its lock, park itself efficiently (no CPU consumption), and be awakened precisely when the condition it's waiting for might be true.

### 📘 Textbook Definition

**`Object.wait()`** suspends the calling thread: it releases the object's monitor lock and enters WAITING state, parking without consuming CPU. **`Object.notify()`** wakes one arbitrary thread waiting on the object's monitor. **`Object.notifyAll()`** wakes ALL waiting threads. The awakened thread must re-acquire the monitor lock before continuing. All three methods must be called from within a `synchronized` block on the same object, or `IllegalMonitorStateException` is thrown. Spurious wakeups — a thread waking without being notified — are possible and must be handled with a `while` loop guard.

### ⏱️ Understand It in 30 Seconds

**One line:**
`wait()` releases the lock and sleeps; `notify()` wakes one sleeper; any wake-up must be checked in a loop.

**One analogy:**
> A doctor's waiting room with a number system. When the doctor is not ready, a patient (thread) takes a number, sits down, and waits (wait() — releases the counter, stops consuming). When the doctor is ready, the receptionist calls a number (notify()) or "everyone with a cold" (notifyAll()). The patient checks if their condition is met (loop check) and either sees the doctor or sits back down.

**One insight:**
The wait-check pattern MUST be a `while` loop, not `if`. Spurious wakeups are real — the JVM or OS can wake a thread without `notify()` for implementation-specific reasons. The loop re-checks the condition:
```java
synchronized (lock) {
    while (!conditionMet()) { // NOT if()!
        lock.wait();
    }
    // condition is now guaranteed true
}
```

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. `wait()` RELEASES the monitor lock — this is what allows the notifying thread to acquire the lock to call `notify()`.
2. After `notify()`, the awakened thread must RE-ACQUIRE the lock before it can proceed past `wait()`.
3. Spurious wakeups are possible — always use `while` loop, never `if`.

DERIVED DESIGN:
Given invariant 1 + 2: the standard pattern is:
```java
// Waiter:
synchronized (lock) {
    while (!condition) {
        lock.wait();         // releases lock, parks
    }                        // woken: condition may be true
    consumeResource();       // condition is true here
}

// Notifier:
synchronized (lock) {
    makeConditionTrue();
    lock.notify();           // picks one waiting thread to wake
}                            // lock released → waiter re-acquires
```

**Why is spurious wakeup possible?**
POSIX `pthread_cond_wait` (which `Object.wait()` may use internally on Linux) can spuriously return without a signal — implementation details of the OS condition variable. Treating wakes as informational ("something may have changed — recheck") rather than definitive ("the condition is definitely true") is the correct model.

THE TRADE-OFFS:
Gain: Efficient cooperative waiting (no CPU spin); lock-integrated (condition check and state change in same critical section).
Cost: Must always be in `synchronized`; must use `while` loop; `notify()` picks arbitrary waiter (may pick wrong one); multiple conditions need multiple objects or `Condition` (ReentrantLock); missed notifications if `notify()` fires before `wait()`.

### 🧪 Thought Experiment

SETUP:
Classic bounded producer-consumer with one buffer slot.

WITHOUT wait/notify (busy spin):
```java
while (buffer.isEmpty()) {} // spin — CPU waste
Item item = buffer.take();
```

WITH wait/notify (correct):
```java
synchronized (lock) {
    while (buffer.isEmpty()) {
        lock.wait(); // release lock, park efficiently
    }
    Item item = buffer.take();
    lock.notify(); // wake a producer if waiting
}
```

SPURIOUS WAKEUP TRAP:
```java
// WRONG: using if instead of while
synchronized (lock) {
    if (buffer.isEmpty()) {
        lock.wait(); // spurious wake: buffer still empty!
    }
    Item item = buffer.take(); // NullPointerException or wrong item!
}
```

THE INSIGHT:
`if(condition) wait()` is always wrong because: (1) spurious wakeups exist; (2) multiple waiters may be woken by `notifyAll()` but only one can consume the item — the rest find the condition false.

### 🧠 Mental Model / Analogy

> `wait()` is like a chef going on break when there's nothing to cook: they hand back the kitchen key (release lock), go to the break room, and wait. When the maître d' has ingredients ready (notify), they wake one chef, who returns to the kitchen, picks up the key (re-acquire lock), checks if there's actually food to cook (while loop — could have been false alarm), and either cooks or waits again.

"Hand back kitchen key" → `wait()` releases monitor.
"Wake one chef" → `notify()` picks arbitrary waiter.
"Check if food is actually there" → `while` loop recheck.
"False alarm" → spurious wakeup.

Where this analogy breaks down: `notifyAll()` wakes all chefs — only one needs to cook. The others check and go back to break (re-wait). This is correct but "thundering herd" — all woken, most immediately wait again.

### 📶 Gradual Depth — Four Levels

**Level 1:** `wait()` pauses a thread efficiently (no CPU waste) until another thread says "go check again" (`notify()`).

**Level 2:** Always use `while` loop with `wait()`. Always call `notify()`/`notifyAll()` after state changes that waiting threads need. ALWAYS call from within `synchronized` on the same object. Use `notifyAll()` when multiple different conditions are being waited on (simpler), or `notify()` when all waiters check the same condition and only one benefits.

**Level 3:** `Object.wait()` uses the monitor's wait queue (separate from the entry queue). JVM calls `LockSupport.park()` internally. On `notify()`, one thread moves from wait queue to entry queue (still blocked until notifier releases lock). The re-check loop handles "condition was met when notified but another thread consumed it before I acquired the lock."

**Level 4:** `wait/notify` is a low-level primitive — correct use is error-prone. `java.util.concurrent.locks.Condition` (from `ReentrantLock`) provides the same semantics with named conditions (multiple per lock), interruptible waits, and timed waits without the API complexity of `Object`. `BlockingQueue` (LinkedBlockingQueue, ArrayBlockingQueue) encapsulates the producer-consumer pattern correctly — use these instead of hand-coded wait/notify.

### ⚙️ How It Works (Mechanism)

**Standard producer-consumer template:**
```java
class BoundedBuffer<T> {
    private final Queue<T> buf = new LinkedList<>();
    private final int maxSize;
    private final Object lock = new Object();

    BoundedBuffer(int maxSize) { this.maxSize = maxSize; }

    void put(T item) throws InterruptedException {
        synchronized (lock) {
            while (buf.size() == maxSize) { // WHILE, not if
                lock.wait();  // buffer full: wait
            }
            buf.add(item);
            lock.notifyAll(); // wake consumers
        }
    }

    T take() throws InterruptedException {
        synchronized (lock) {
            while (buf.isEmpty()) { // WHILE, not if
                lock.wait();  // buffer empty: wait
            }
            T item = buf.poll();
            lock.notifyAll(); // wake producers
            return item;
        }
    }
}
```

**notify() vs notifyAll() choice:**
```java
// Use notify() ONLY when:
// - All waiters check the SAME condition
// - Waking one waiter is sufficient to process the state change

// Use notifyAll() when:
// - Multiple different conditions are waited on
// - Multiple consumers can run concurrently
// (safer default, slightly more overhead)

// Thundering herd example (notifyAll):
// 10 consumers wait for buffer. 1 item added. notifyAll().
// All 10 wake up. 9 find buffer empty, wait again.
// Solution: use notify() when one item added, one consumer needed.
```

**wait() with timeout:**
```java
synchronized (lock) {
    long deadline = System.currentTimeMillis() + 5000;
    while (!condition && System.currentTimeMillis() < deadline) {
        long remaining = deadline - System.currentTimeMillis();
        if (remaining <= 0) break;
        lock.wait(remaining); // wait at most 'remaining' ms
    }
    if (!condition) handleTimeout();
}
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (producer-consumer):
```
[Consumer: synchronized(lock)]
    → [Buffer empty: lock.wait()] ← YOU ARE HERE
    → [Monitor released, thread parks in WAITING]
    → [Producer: synchronized(lock)]
    → [Producer: buf.add(item)]
    → [Producer: lock.notify()]
    → [Consumer moved to entry queue]
    → [Producer releases lock: monitorexit]
    → [Consumer: re-acquires lock]
    → [Consumer: while(!isEmpty()) — NOT met]
    → [Consumer: buf.poll() → returns item]
```

FAILURE PATH (missed notification):
```
[Consumer: checks isEmpty() → true outside synchronized!]
    → [Producer: adds item, calls notify() — NO ONE WAITING]
    → [Consumer: lock.wait() — waits forever]
    → [Missed notification: state check before entering monitor]
    → [Fix: ALWAYS check condition inside synchronized]
```

WHAT CHANGES AT SCALE:
At scale, hand-written `wait/notify` is replaced by `java.util.concurrent` classes:
- `BlockingQueue` — producer-consumer
- `CountDownLatch` — one-time coordination
- `CyclicBarrier` — repeated phase synchronization
- `Semaphore` — resource pool management

These are safer, better-tested implementations of wait/notify patterns. Only use raw `wait/notify` when no standard primitive fits.

### 💻 Code Example

Example 1 — One-shot coordination (prefer CountDownLatch):
```java
// Simple: let T2 wait for T1 to finish setup
Object ready = new Object();
boolean isReady = false;

// T1 (setup thread):
synchronized (ready) {
    doSetup();
    isReady = true;
    ready.notifyAll();
}

// T2 (worker thread):
synchronized (ready) {
    while (!isReady) {
        ready.wait();
    }
    // setup is complete
}

// Modern equivalent (simpler, safer):
CountDownLatch latch = new CountDownLatch(1);
// T1: latch.countDown();
// T2: latch.await();
```

Example 2 — Modern BlockingQueue replaces hand-coded:
```java
// Instead of hand-coded BoundedBuffer above, use:
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);

// Producer thread:
queue.put(task);    // blocks if full — no wait/notify needed

// Consumer thread:
Task task = queue.take(); // blocks if empty — no wait/notify needed
```

### ⚖️ Comparison Table

| Mechanism | Efficiency | Spurious Wakeup | Multiple Conditions | Best For |
|---|---|---|---|---|
| **wait/notify** | Good | Must handle | One per lock (use notifyAll) | Custom conditions |
| ReentrantLock+Condition | Good | Must handle | Yes (multiple conditions) | Complex coordination |
| BlockingQueue | Best | Handled internally | N/A | Producer-consumer |
| CountDownLatch | Best | N/A | N/A | One-shot startup sync |
| Semaphore | Best | N/A | N/A | Resource pool |

How to choose: Use `BlockingQueue` for producer-consumer. Use `CountDownLatch` for one-time coordination. Use `ReentrantLock.Condition` when you need multiple conditions on one lock. Only use raw `wait/notify` for custom protocols not covered by the above.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `notify()` wakes the longest-waiting thread | `notify()` wakes an ARBITRARY thread from the wait queue. There's no FIFO guarantee. Use `notifyAll()` when fairness matters, or use `ReentrantLock(fair=true)` |
| `wait()` releases all locks held by the thread | `wait()` releases ONLY the lock on which `wait()` is called. All other locks held by the thread are NOT released |
| Spurious wakeups are rare and can be ignored | The JMM explicitly allows spurious wakeups. `if (condition) wait()` is ALWAYS WRONG — `while (condition) wait()` is required |
| `notifyAll()` guarantees deadlock freedom | `notifyAll()` prevents some notify-related deadlocks but not lock-ordering deadlocks. Calling `notifyAll()` when everything is locked in wrong order still deadlocks |
| `wait()` and `sleep()` are interchangeable | `sleep()` does NOT release any lock. `wait()` RELEASES the monitor lock. They have completely different semantics |

### 🚨 Failure Modes & Diagnosis

**Missed Notification (notify before wait)**

Symptom: Thread waits forever even though the condition was satisfied.

Root Cause: Condition was checked BEFORE entering `synchronized`, then `notify()` fired, then thread entered `wait()` — too late.

Fix: Always check condition inside `synchronized`, change condition inside `synchronized`, call `notify()` inside `synchronized`.

---

**Using `if` instead of `while` — Spurious Wakeup Bug**

Symptom: Intermittent NullPointerException or IllegalStateException after `wait()` returns.

Root Cause: Condition was false when thread woke up (spurious or beaten by another thread).

Fix:
```java
// WRONG:
if (buffer.isEmpty()) lock.wait();
buffer.take(); // may throw — buffer could be empty!

// CORRECT:
while (buffer.isEmpty()) lock.wait();
buffer.take(); // safe — while loop guarantees true
```

---

**Deadlock: notifying thread can't acquire lock**

Symptom: Notifier calls `notify()` but no waiting thread unblocks.

Root Cause: Waiter called `wait()` with wrong object. Notifier called `notify()` on a different object.

Fix: Ensure both `wait()` and `notify()` are called on the SAME object.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `synchronized` — `wait/notify` requires a synchronized context; all three methods throw `IllegalMonitorStateException` without it
- `Thread Lifecycle` — understanding WAITING state explains what `wait()` does to a thread

**Builds On This (learn these next):**
- `ReentrantLock` — provides `Condition` objects as a more powerful replacement for `wait/notify`; supports multiple conditions per lock
- `BlockingQueue` — encapsulates the producer-consumer pattern using `wait/notify` internally; the standard replacement for most custom uses

**Alternatives / Comparisons:**
- `ReentrantLock + Condition` — more powerful than `wait/notify`; supports named conditions, interruptible waits
- `BlockingQueue` — encapsulates producer-consumer correctly; prefer over custom wait/notify

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ wait() releases lock + parks thread;      │
│              │ notify() wakes one arbitrary waiter       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Busy-waiting wastes CPU; need a way to    │
│ SOLVES       │ wait for a condition without spinning     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ALWAYS use while loop — never if.         │
│              │ wait() releases ONLY its own lock.        │
│              │ Prefer BlockingQueue, CountDownLatch,     │
│              │ Semaphore over raw wait/notify            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Custom condition-based coordination when  │
│              │ no java.util.concurrent class fits        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Producer-consumer (use BlockingQueue);    │
│              │ simple coordination (use CountDownLatch)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Efficient waiting vs error-prone API;     │
│              │ flexibility vs using proven higher-level  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Release lock, sleep, recheck on wake"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ReentrantLock → Condition → BlockingQueue │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** A hand-coded `BoundedBuffer` using `wait()/notifyAll()` has a subtle performance issue when all 100 producers are waiting (buffer full) and a consumer takes one item and calls `notifyAll()`. Trace exactly what happens: how many producer threads wake up, how many will find the buffer still full (and return to wait immediately), what this costs in terms of monitor re-acquisition, and what change (using `notify()` vs `notifyAll()`) would be correct HERE — and why switching to `notify()` in a buffer used by both producers AND consumers simultaneously creates a correctness bug.

**Q2.** The Java Language Specification says concurrent implementations are permitted to perform "spurious wakeups" from `Object.wait()`. This is not a Java-specific design choice but a consequence of POSIX `pthread_cond_wait` semantics on Linux. Explain the kernel-level scenario: what specific Linux system call interaction (signal delivery, `futex` wake, or CPU migration) can cause `pthread_cond_wait` to return spuriously without a `pthread_cond_signal`, and why it would be prohibitively expensive for the JVM to suppress spurious wakeups by wrapping `wait()` with an additional kernel-side check.

