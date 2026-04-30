---
layout: default
title: "wait / notify / notifyAll"
parent: "Java Concurrency"
nav_order: 103
permalink: /java-concurrency/wait-notify-notifyall/
number: "103"
category: Java Concurrency
difficulty: ★★★
depends_on: synchronized, Thread, Object Monitor, Java Memory Model
used_by: Producer-Consumer Pattern, Condition Variables, BlockingQueue (internal)
tags: #java, #concurrency, #synchronization, #wait, #notify, #monitor
---

# 103 — wait / notify / notifyAll

`#java` `#concurrency` `#synchronization` `#wait` `#notify` `#monitor`

⚡ TL;DR — `wait()` releases a monitor lock and suspends the calling thread until another thread calls `notify()` or `notifyAll()` on the same object; the thread re-acquires the lock before returning — Java's built-in condition variable mechanism.

| #103 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | synchronized, Thread, Object Monitor, Java Memory Model | |
| **Used by:** | Producer-Consumer Pattern, Condition Variables, BlockingQueue (internal) | |

---

### 📘 Textbook Definition

`Object.wait()`, `Object.notify()`, and `Object.notifyAll()` are the low-level inter-thread communication methods built into every Java object's monitor. A thread must **hold the object's monitor** (be inside a `synchronized` block on that object) to call these methods. `wait()` atomically releases the monitor and suspends the thread in a `WAITING` or `TIMED_WAITING` state. A subsequent `notify()` (wakes one waiting thread) or `notifyAll()` (wakes all) causes the waiting thread(s) to compete to re-acquire the monitor, then resume after `wait()` returns.

---

### 🟢 Simple Definition (Easy)

`wait` and `notify` let two threads talk to each other: one thread does `wait()` to pause and say "I'm waiting for something to happen." Another thread does `notify()` to say "Something happened — wake up." Both must use the same shared object as the communication channel, and both must be inside a `synchronized` block on that object.

---

### 🔵 Simple Definition (Elaborated)

Think of the object monitor as a meeting room (lock) with a waiting lounge. When a thread calls `wait()`, it exits the meeting room, sits in the waiting lounge, and releases the lock so others can enter. When another thread calls `notify()`, one waiting thread is moved from the lounge back to the queue to re-enter the meeting room. The woken thread doesn't run immediately — it re-competes for the lock. `notifyAll()` moves all waiting threads back to the queue, preventing issues where the wrong thread is woken.

---

### 🔩 First Principles Explanation

**The core problem:**

```
Thread A (Consumer): checks if queue has data → empty → should pause
Thread B (Producer): adds data to queue → should wake Consumer

Without wait/notify:
  Consumer: while (queue.isEmpty()) { }  ← busy-wait, burns CPU
  
With wait/notify:
  Consumer: synchronized(lock) {
    while (queue.isEmpty()) { lock.wait(); }  ← releases lock, sleeps
    process(queue.poll());
  }
  Producer: synchronized(lock) {
    queue.add(item);
    lock.notify();  ← wakes sleeping Consumer
  }
```

**Why `wait()` must be in a `synchronized` block:**

```
Without synchronization — broken:
  Thread A: checks queue.isEmpty() → true (about to call wait)
  Thread B: adds item, calls notify() → no one is waiting yet!
  Thread A: calls wait() → waits forever (missed notification)

With synchronized — safe:
  The check + wait is atomic; notify() cannot sneak in between
```

---

### ❓ Why Does This Exist — Why Before What

Before Java had `java.util.concurrent` (pre-Java 5), `wait/notify` were the only way to implement condition-based synchronization. `BlockingQueue`, `CountDownLatch`, and `ReentrantLock.Condition` are all built on top of these primitives — or equivalent park/unpark mechanisms. Understanding `wait/notify` reveals what higher-level abstractions do internally.

---

### 🧠 Mental Model / Analogy

> Think of a restaurant (shared object). The cook (producer) and waiter (consumer) share one bell. The waiter rings the bell and sits down (`wait()`) when there are no dishes ready. When the cook finishes a dish, they ring the bell back (`notify()`). The waiter wakes up, checks if a dish is ready, and picks it up. The synchronized block is the kitchen — only one person inside at a time.

---

### ⚙️ How It Works — The Monitor Protocol

```
State transitions:

                   ┌─── synchronized(lock) ───────────────┐
Thread enters ────>│                                       │
                   │  Holds monitor                        │
                   │       │                               │
                   │  calls lock.wait()                    │
                   │       │                               │
                   │       ▼                               │
                   │  ┌─────────────────┐                  │
                   │  │ WAITING set     │ ← releases lock  │
                   │  │ (lounge)        │                  │
                   │  └─────────────────┘                  │
                   │       │ notify()/notifyAll()           │
                   │       ▼                               │
                   │  ┌─────────────────┐                  │
                   │  │ ENTRY set       │ ← re-compete     │
                   │  │ (queue)         │   for lock       │
                   │  └─────────────────┘                  │
                   │       │ wins lock                     │
                   │       ▼                               │
                   │  Returns from wait()                  │
                   └───────────────────────────────────────┘

Key facts:
- wait() releases the lock atomically with entering WAITING state
- notify() does NOT release the lock; notifier continues until it exits synchronized block
- notified thread must re-acquire the lock before wait() returns
- spurious wakeups are possible → always use while loop, never if
```

---

### 💻 Code Example

```java
// Classic Producer-Consumer with wait/notify
public class BoundedBuffer<T> {
    private final Queue<T> queue = new LinkedList<>();
    private final int capacity;
    private final Object lock = new Object();

    public BoundedBuffer(int capacity) { this.capacity = capacity; }

    public void put(T item) throws InterruptedException {
        synchronized (lock) {
            while (queue.size() == capacity) {  // ← WHILE, not if (spurious wakeup)
                lock.wait();                    // releases lock, suspends
            }
            queue.add(item);
            lock.notifyAll();                   // wake consumers AND other producers
        }
    }

    public T take() throws InterruptedException {
        synchronized (lock) {
            while (queue.isEmpty()) {           // ← WHILE, not if
                lock.wait();
            }
            T item = queue.poll();
            lock.notifyAll();                   // wake producers AND other consumers
            return item;
        }
    }
}
```

```java
// notify() vs notifyAll() risk demonstrated
// Scenario: 2 producers waiting (full), 2 consumers waiting (empty)

// With notify(): only ONE thread is woken
//   If a producer wakes a producer (same condition) → both go back to sleep
//   → Deadlock / starvation

// With notifyAll(): ALL threads wake, re-check their while condition
//   The ones whose condition is met proceed; others wait again
//   → Always safe (with while loop), slightly less efficient

// Rule: use notifyAll() unless you are certain only one type of waiter exists
```

```java
// Timed wait — wait with timeout
synchronized (lock) {
    long deadline = System.currentTimeMillis() + 5000;
    while (!conditionMet()) {
        long remaining = deadline - System.currentTimeMillis();
        if (remaining <= 0) throw new TimeoutException();
        lock.wait(remaining);  // wakes after timeout OR notify
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `notify()` immediately runs the waiting thread | Notified thread must re-acquire the lock first — notifier continues |
| Using `if` instead of `while` around `wait()` is fine | Spurious wakeups exist; always use `while` loop |
| `wait()` holds the lock while sleeping | `wait()` **releases** the lock atomically |
| `notify()` is always better than `notifyAll()` | `notify()` can cause missed wakeups if multiple wait conditions exist |
| Can call `wait()` without synchronized | Throws `IllegalMonitorStateException` at runtime |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using `if` instead of `while` (spurious wakeup)**

```java
// BUG: spurious wakeup or wrong-thread wakeup causes incorrect behavior
synchronized (lock) {
    if (queue.isEmpty()) {  // ❌
        lock.wait();
    }
    process(queue.poll()); // might fail if queue still empty
}

// Fix:
synchronized (lock) {
    while (queue.isEmpty()) {  // ✅
        lock.wait();
    }
    process(queue.poll());
}
```

**Pitfall 2: Forgetting to call `notifyAll()` after state change**

```java
// BUG: state changes but no one is woken
synchronized (lock) {
    queue.add(item);
    // forgot lock.notifyAll() ← consumers wait forever
}
```

**Pitfall 3: Calling `wait()` outside synchronized**

```java
// Throws IllegalMonitorStateException at runtime
lock.wait(); // ❌ — must own the monitor

synchronized (lock) {
    lock.wait(); // ✅
}
```

**Modern Alternative:** Prefer `java.util.concurrent.locks.Condition` from `ReentrantLock`, or use `BlockingQueue` — they provide cleaner APIs and avoid these pitfalls.

---

### 🔗 Related Keywords

- **[synchronized](./338 — synchronized.md)** — must hold monitor to call wait/notify
- **[ReentrantLock](./341 — ReentrantLock.md)** — modern lock with explicit `Condition` objects (replacement)
- **[BlockingQueue](./360 — BlockingQueue.md)** — uses wait/notify internally; preferred for producer-consumer
- **[Thread Lifecycle](./336 — Thread Lifecycle.md)** — WAITING / TIMED_WAITING states
- **[Race Condition](./346 — Race Condition.md)** — what wait/notify prevents

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ wait()       │ Release lock + sleep until notify/timeout     │
├──────────────┼───────────────────────────────────────────────┤
│ notify()     │ Wake ONE waiting thread (non-deterministic)   │
├──────────────┼───────────────────────────────────────────────┤
│ notifyAll()  │ Wake ALL waiting threads (safer)              │
├──────────────┼───────────────────────────────────────────────┤
│ RULE #1      │ Always call inside synchronized block         │
├──────────────┼───────────────────────────────────────────────┤
│ RULE #2      │ Always check condition in while loop          │
├──────────────┼───────────────────────────────────────────────┤
│ PREFER       │ BlockingQueue / Condition over raw wait/notify│
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Why must `wait()` always be called inside a `while` loop rather than an `if`? Name two distinct reasons.

**Q2.** `notify()` wakes one thread — but which one? Is it the one that has been waiting longest? What does the JVM guarantee?

**Q3.** You have a buffer with producers and consumers both waiting. You use `notify()`. Under what exact scenario does this cause a deadlock?

