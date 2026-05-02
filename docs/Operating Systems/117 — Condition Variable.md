---
layout: default
title: "Condition Variable"
parent: "Operating Systems"
nav_order: 117
permalink: /operating-systems/condition-variable/
number: "0117"
category: Operating Systems
difficulty: ★★☆
depends_on: Mutex, Thread, Synchronous vs Asynchronous
used_by: Producer-Consumer, Monitor, BlockingQueue, Object.wait/notify
related: Mutex, Semaphore, Monitor, spurious wakeup
tags:
  - os
  - concurrency
  - synchronization
  - fundamentals
---

# 117 — Condition Variable

⚡ TL;DR — A condition variable lets a thread atomically release a mutex and wait until another thread signals that a condition is true — the mechanism behind every blocking queue.

| #0117           | Category: Operating Systems                                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Mutex, Thread, Synchronous vs Asynchronous                    |                 |
| **Used by:**    | Producer-Consumer, Monitor, BlockingQueue, Object.wait/notify |                 |
| **Related:**    | Mutex, Semaphore, Monitor, spurious wakeup                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A consumer thread needs to wait for an item to appear in an empty queue. Without condition variables, the consumer either: (1) polls the queue in a spin loop — burns 100% CPU checking an empty queue, (2) sleeps for a fixed interval — wastes time or misses items.

**THE BREAKING POINT:**
Neither approach is correct: polling wastes CPU, sleep-and-check misses events or adds latency. You need an efficient "sleep until the queue is non-empty" primitive. But sleeping can't be done while holding the mutex (that would block the producer from adding items). You need to atomically release the mutex and sleep.

**THE INVENTION MOMENT:**
Condition variables were introduced in the CAR Hoare monitor abstraction (1974). The key insight: `wait(cv, mutex)` atomically releases the mutex and puts the thread to sleep — in one indivisible operation. The producer acquires the mutex, adds an item, calls `signal(cv)` to wake the consumer, and releases the mutex. The consumer is woken, re-acquires the mutex, and finds the item.

---

### 📘 Textbook Definition

A **condition variable** is a synchronisation primitive that enables threads to wait (block) until a particular condition is satisfied, with the associated mutex atomically released during the wait. Core operations:

- **wait(cv, mutex)**: atomically releases `mutex` and blocks the calling thread until `cv` is signalled; upon waking, re-acquires `mutex` before returning.
- **signal(cv)** (also `notify_one`): wakes one waiting thread; if no thread is waiting, the signal is lost.
- **broadcast(cv)** (also `notify_all`): wakes all waiting threads.

A condition variable is always used with a mutex. The typical pattern is: `lock mutex → check condition → if false: wait(cv, mutex) → re-check condition (spurious wakeup!) → proceed`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Condition variable: release the mutex and sleep atomically; the signaller wakes you and you re-check.

**One analogy:**

> You're waiting for a package (condition) in a secured mailroom (mutex). You hold the key (mutex) but the package isn't there. You leave the key in the door (release mutex) and put up a "knock when delivery arrives" sign (wait on cv). The delivery person arrives, knocks (signal), and you return to check. You find the package and take it.

**One insight:**
The atomicity of "release mutex + sleep" is crucial. Without it, there's a race: release mutex → producer adds item → producer signals → you go to sleep (never woken). The condition variable prevents this lost signal by making the check-and-sleep atomic with respect to the mutex.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `wait()` atomically releases the mutex and blocks. No window for signal loss.
2. Upon waking, `wait()` re-acquires the mutex before returning to caller.
3. Spurious wakeups are possible (POSIX explicitly allows them) — always re-check the condition in a loop.
4. Signals are not queued — `signal()` with no waiting threads loses the signal.

**DERIVED DESIGN:**
The condition variable maintains a wait queue. `wait(cv, mutex)`:

1. Add self to cv's wait queue.
2. Release mutex (atomically with step 1 via internal lock).
3. Block (sleep).

`signal(cv)`:

1. If wait queue non-empty: remove one thread, move to run queue.
2. (The woken thread will try to re-acquire the mutex in `wait()` step 2.)

THE SPURIOUS WAKEUP:
POSIX allows implementations to wake `wait()` for reasons other than a `signal()` call (e.g., signal delivery to the process). Any correct implementation must loop: `while (!condition) wait(cv, mutex);`. The `while` absorbs spurious wakeups.

**THE TRADE-OFFS:**
**Gain:** Efficient blocking without polling; zero CPU usage while waiting; correct signal-wait ordering.
**Cost:** Always used with a mutex (adds locking overhead); spurious wakeups require while-loop; signal is "fire and forget" — if no one is waiting, the signal is lost (use semaphore if you need to remember signals).

---

### 🧪 Thought Experiment

PRODUCER-CONSUMER with bounded buffer:

```
Mutex mtx; CondVar not_empty; CondVar not_full;
Queue<T> buf; int MAX = 10;

Producer:
  mtx.lock();
  while (buf.size() == MAX) not_full.wait(mtx);  ← BLOCKS if full
  buf.push(item);
  not_empty.signal();
  mtx.unlock();

Consumer:
  mtx.lock();
  while (buf.empty()) not_empty.wait(mtx);  ← BLOCKS if empty
  item = buf.pop();
  not_full.signal();
  mtx.unlock();
```

SCENARIO: Buffer empty, Consumer runs first:

1. Consumer: lock, check empty → true, `not_empty.wait(mtx)`: releases lock + sleeps.
2. Producer: lock, push item, `not_empty.signal()`: wakes Consumer, unlock.
3. Consumer: wakes, re-acquires lock, re-checks (while): not empty → exits loop, pops item.

**THE INSIGHT:** No busy-wait, no lost signal, no data race. The `while` loop handles spurious wakeups and the case where multiple consumers race to dequeue the same item.

---

### 🧠 Mental Model / Analogy

> A condition variable is like a phone notification system for a shared kitchen. You hold the key (mutex), open the fridge (shared resource), find it empty. You put the key on the hook (release mutex) and register for "food added" notifications (add to wait queue). When someone adds food (signal), your phone buzzes. You take the key back (re-acquire mutex) and check the fridge (re-check condition — another person may have taken the food first). If empty: register again. If food: take it.

Where the analogy breaks down: in real condition variables, `signal()` with no registered receivers loses the notification. Unlike phone apps that show unread count, condition variable signals do not accumulate. This is why semaphores (which count signals) are used for producer-consumer variants where the consumer might not be waiting when the producer fires.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A condition variable lets a thread wait efficiently for something to happen. You release your lock, go to sleep, and wake up only when another thread says "the thing happened." You then re-check and proceed if the condition is really true.

**Level 2 — How to use it (junior developer):**
Java: `Object.wait()` / `Object.notify()` / `Object.notifyAll()` (inside `synchronized`). Or `Condition condition = lock.newCondition(); condition.await(); condition.signal();` (with ReentrantLock). POSIX C: `pthread_cond_wait(&cv, &mutex)`. ALWAYS use `while` not `if` around `wait()`. Call `notifyAll()` instead of `notify()` unless you are sure exactly one thread should handle the event.

**Level 3 — How it works (mid-level engineer):**
Java `Object.wait()` / `notify()` are tied to the monitor (implicit mutex of synchronized block). `wait()` atomically: (1) adds thread to object's wait set; (2) releases monitor; (3) blocks via `LockSupport.park()`. `notify()` moves one thread from wait set to entry set (threads competing for monitor). The thread in entry set must still compete to acquire the monitor. `notifyAll()` moves all threads from wait set to entry set. POSIX `pthread_cond_wait` is similar: adds to condvar's wait queue, releases mutex, blocks on futex. Signal: futex wake → thread competes for mutex.

**Level 4 — Why it was designed this way (senior/staff):**
The condition variable design directly implements the monitor abstraction from Hoare (1974). The critical requirement is atomicity of "release mutex + block" — without it, there is a window where: (1) thread A releases mutex, (2) thread B acquires mutex, adds item, signals (no one waiting yet), (3) thread A goes to sleep (never woken). The condvar's internal lock prevents this race by making the "add to wait queue" step visible to the signaller before the mutex is released. Java's `Object.wait()` and `notifyAll()` are a simplified version of Hoare monitors that avoid condition variable stacks (threads go back to waiting for the monitor, not back to the condition) — this is why `while (!condition) wait()` is required rather than `if`.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         CONDITION VARIABLE: wait() FLOW                │
├────────────────────────────────────────────────────────┤
│  Consumer thread:                                      │
│  1. mutex.lock()                                       │
│  2. while (queue.empty())                              │
│  3.   cv.wait(mutex):                                  │
│       a. Internal: acquire cv's internal lock          │
│       b. Add self to cv's wait queue                  │
│       c. Release mutex (atomically with b)             │
│       d. futex(WAIT) → sleep                          │
│       e. [woken by signal()]                          │
│       f. Compete to re-acquire mutex                   │
│       g. Return to while loop                         │
│  4. item = queue.dequeue()                             │
│  5. mutex.unlock()                                     │
│                                                        │
│  Producer thread:                                      │
│  1. mutex.lock()                                       │
│  2. queue.enqueue(item)                                │
│  3. cv.signal()                                        │
│       a. If wait queue non-empty: futex(WAKE) one      │
│       b. (woken thread: re-acquire mutex, return from wait)│
│  4. mutex.unlock()                                     │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

JAVA BlockingQueue (ArrayBlockingQueue internals):

```java
// ArrayBlockingQueue uses one ReentrantLock + two Conditions
final ReentrantLock lock = new ReentrantLock();
final Condition notEmpty = lock.newCondition();  // consumer waits
final Condition notFull  = lock.newCondition();  // producer waits

// put() — blocks if full
public void put(E e) throws InterruptedException {
    lock.lock();
    try {
        while (count == items.length)  // WHILE — not if
            notFull.await();           // release lock + sleep
        enqueue(e);
        notEmpty.signal();             // wake one consumer
    } finally {
        lock.unlock();
    }
}

// take() — blocks if empty
public E take() throws InterruptedException {
    lock.lock();
    try {
        while (count == 0)             // WHILE — not if
            notEmpty.await();          // release lock + sleep
        E item = dequeue();
        notFull.signal();              // wake one producer
        return item;
    } finally {
        lock.unlock();
    }
}
```

---

### 💻 Code Example

Example 1 — Java with ReentrantLock and Condition (recommended):

```java
import java.util.concurrent.locks.*;

public class BoundedBuffer<T> {
    private final Object[] buf;
    private int head, tail, count;
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();

    public BoundedBuffer(int capacity) {
        buf = new Object[capacity];
    }

    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (count == buf.length)  // ALWAYS while, never if
                notFull.await();
            buf[tail++ % buf.length] = item;
            count++;
            notEmpty.signal();
        } finally { lock.unlock(); }
    }

    @SuppressWarnings("unchecked")
    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0)           // ALWAYS while
                notEmpty.await();
            T item = (T) buf[head++ % buf.length];
            count--;
            notFull.signal();
            return item;
        } finally { lock.unlock(); }
    }
}
```

Example 2 — Java synchronized (Object.wait / notifyAll):

```java
public class SimpleBlockingQueue<T> {
    private final Queue<T> queue = new LinkedList<>();
    private final int maxSize;

    public SimpleBlockingQueue(int maxSize) {
        this.maxSize = maxSize;
    }

    public synchronized void put(T item) throws InterruptedException {
        while (queue.size() == maxSize)  // while, not if
            wait();  // releases 'this' monitor, sleeps
        queue.add(item);
        notifyAll();  // wake all waiting threads
    }

    public synchronized T take() throws InterruptedException {
        while (queue.isEmpty())
            wait();
        T item = queue.remove();
        notifyAll();
        return item;
    }
}
// Note: notifyAll() is safer than notify() when multiple
// different conditions are waited on (avoids lost signal)
```

---

### ⚖️ Comparison Table

| Primitive                | Signal Queued?       | Ownership       | Best For                                             |
| ------------------------ | -------------------- | --------------- | ---------------------------------------------------- |
| **Condition Variable**   | No (fire-and-forget) | Used with mutex | Wait for arbitrary condition                         |
| Semaphore                | Yes (counted)        | None            | Rate limiting, resource counting, bounded signalling |
| CountDownLatch           | N/A (decremented)    | None            | One-time "wait for N events"                         |
| Future/CompletableFuture | N/A                  | None            | Wait for one async result                            |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                          |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Use if instead of while for condition check" | Spurious wakeups are explicitly allowed by POSIX; also, multiple threads may be woken by notifyAll() — only first gets the item; others must re-check                                                                            |
| "notifyAll is always correct over notify"     | notifyAll wakes all waiting threads; they all compete; with a single condition, one proceeds, others re-wait. It's safe but may have thundering herd overhead. Use notify only if ALL waiting threads would handle the condition |
| "signal() is remembered if no one is waiting" | No — signals on a condition variable are lost if no thread is waiting. This is why Semaphore (which counts) is different from Condition (which doesn't)                                                                          |
| "Condition variable without mutex is fine"    | Always wrong — the atomicity of "check condition + wait" requires the mutex; without it, there's a lost-signal race condition                                                                                                    |

---

### 🚨 Failure Modes & Diagnosis

**1. Lost Signal (notify before wait)**

**Symptom:** Consumer thread blocks indefinitely even though items were produced; no deadlock detected.

**Root Cause:** Signal fired before consumer entered wait; signal lost; consumer never woken.

**Diagnostic:** Can occur if `notify()` is called outside the mutex, or if the condition is pre-satisfied before the first consumer starts. Thread dump will show consumer in WAITING state on the condition.

**Fix:** Check condition in a while loop before waiting (if condition already met, skip wait). Always hold the mutex before calling `signal()`/`wait()`.

---

**2. If Instead of While (Spurious/Wrong-Thread Wakeup)**

**Symptom:** Consumer dequeues from empty queue; ArrayIndexOutOfBoundsException or NullPointerException.

**Root Cause:** Used `if (!condition) wait()` instead of `while (!condition) wait()`; woken by a spurious wakeup or notifyAll(); condition was re-taken by another thread.

**Fix:** ALWAYS `while (condition not met) wait()`.

---

**3. notify() Instead of notifyAll() with Multiple Conditions**

**Symptom:** Application deadlock; some threads stuck in WAITING state though data is available.

**Root Cause:** Two different conditions (notFull and notEmpty) using the same `wait()`/`notify()`. A producer calls `notify()` when adding an item — it wakes a producer (waiting on notFull) instead of a consumer (waiting on notEmpty).

**Fix:** Use `notifyAll()` to wake all waiters; or use two separate Condition objects (`notFull` and `notEmpty`) with `ReentrantLock` and call the correct `signal()`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Mutex` — condition variable always paired with a mutex; cannot use without
- `Thread` — condition variables coordinate blocking threads
- `Synchronous vs Asynchronous` — condition variable provides synchronous waiting for an event

**Builds On This (learn these next):**

- `Deadlock` — incorrect use of condition variables (wrong lock order, missing notify) causes deadlock
- `Producer-Consumer Pattern` — the canonical use case: two condition variables with one bounded buffer
- `BlockingQueue` — Java's high-level abstraction over the exact condition variable pattern shown above

**Alternatives / Comparisons:**

- `Semaphore` — stores signal count; correct when producer may signal before consumer starts waiting
- `CompletableFuture` — async equivalent; no blocking thread; signal = complete()
- `SynchronousQueue` — rendez-vous: one producer and one consumer meet; no buffer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Atomic "release mutex + sleep" + signal  │
│              │ mechanism for efficient condition waiting  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Polling wastes CPU; sleep misses signals; │
│ SOLVES       │ cv gives efficient, correct waiting       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ALWAYS use while loop — spurious wakeups  │
│              │ + notifyAll() mean condition may be false  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ One thread waits for another to change    │
│              │ state (queue, flag, resource available)   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Producer may signal before consumer       │
│              │ starts (use Semaphore); one-shot event    │
│              │ (use CountDownLatch)                      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero CPU while waiting vs need for        │
│              │ while-loop re-check + mutex pairing       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Release lock + sleep atomically;        │
│              │  ALWAYS re-check condition after waking"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BlockingQueue → Producer-Consumer → Phaser│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Mesa semantics vs Hoare semantics for condition variables: In Hoare monitors (original 1974 design), when thread A signals thread B, B runs immediately and A is suspended. When B finishes its critical section, A resumes. In Mesa semantics (used by all modern systems: POSIX, Java), when A signals B, B is moved to the ready queue but A continues running. B runs "sometime later." This is why Mesa requires `while` instead of `if`. Why did all practical implementations choose Mesa over Hoare semantics despite Mesa requiring `while` loops? Consider the implementation complexity and OS scheduling requirements of each.

**Q2.** Java's `Object.wait()` has a one-argument form: `wait(long timeoutMs)`. This is a timed wait: the thread will wake if signalled OR if the timeout expires. This creates an ambiguity: upon waking, how does the caller know whether it was signalled (condition may be true) or timed out (condition may still be false)? Java's `wait(timeout)` returns `void` — there's no indication of why it woke up. Compare this to `pthread_cond_timedwait()` which returns ETIMEDOUT vs 0. Now compare to `Condition.await(long, TimeUnit)` in `java.util.concurrent.locks.Condition` which returns `boolean`. Design the complete pattern for handling timed waits correctly in both POSIX C and Java, including handling spurious wakeups and timeouts without polling.
