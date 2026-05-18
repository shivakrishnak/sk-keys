---
id: OSY-063
title: Condition Variables Deep Dive
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-023, OSY-062
used_by: OSY-064
related: OSY-062, OSY-064, OSY-079
tags:
  - condition-variable
  - monitor
  - wait-notify
  - spurious-wakeup
  - producer-consumer
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 63
permalink: /technical-mastery/osy/condition-variables/
---

## TL;DR

Condition variables enable threads to wait for a specific
condition to become true, releasing the mutex while sleeping.
Critical rule: ALWAYS check the condition in a `while` loop,
never `if` - spurious wakeups (wakeups with no signal) can
occur. Java's `wait()/notify()` and `Condition.await()/signal()`
are condition variables wrapped in the monitor pattern.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-063 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | condition variable, spurious wakeup, monitor, wait/notify |
| **Prerequisites** | OSY-023, OSY-062 |

---

### Condition Variable Mechanics

```
Problem: thread wants to wait until buffer has data
  
  WRONG approach (busy-wait):
    while (buffer.isEmpty()) {
        Thread.sleep(1);  // waste CPU and add latency
    }
  
  WRONG approach (check-then-act without condition variable):
    synchronized (lock) {
        if (buffer.isEmpty()) return null;  // race condition!
        return buffer.take();
    }
  
  CORRECT: condition variable
    synchronized (lock) {
        while (buffer.isEmpty()) {
            lock.wait();  // atomically: release lock AND sleep
            // when awakened: re-acquire lock, re-check condition
        }
        return buffer.take();
    }
    
Key property: wait() atomically releases mutex and sleeps
  This is essential to avoid lost-signal race:
  Without atomic: release lock (another thread signals), then sleep
    -> miss the signal, sleep forever
  With atomic: signal cannot arrive between release and sleep
```

---

### Producer-Consumer with Condition Variables

```java
// Classic producer-consumer (correct implementation)
public class BoundedBuffer<T> {
    private final Queue<T> queue = new ArrayDeque<>();
    private final int capacity;
    private final Object lock = new Object();
    
    public BoundedBuffer(int capacity) {
        this.capacity = capacity;
    }
    
    public void put(T item) throws InterruptedException {
        synchronized (lock) {
            // ALWAYS while, never if: spurious wakeup protection
            while (queue.size() == capacity) {
                lock.wait();  // buffer full: wait for consumer
            }
            queue.add(item);
            lock.notifyAll();  // wake waiting consumers
        }
    }
    
    public T take() throws InterruptedException {
        synchronized (lock) {
            // ALWAYS while, never if: spurious wakeup protection
            while (queue.isEmpty()) {
                lock.wait();  // buffer empty: wait for producer
            }
            T item = queue.poll();
            lock.notifyAll();  // wake waiting producers
            return item;
        }
    }
}

// BAD: using if instead of while (WRONG):
public T takeBad() throws InterruptedException {
    synchronized (lock) {
        if (queue.isEmpty()) {  // BUG: if woken spuriously,
            lock.wait();        // or by wrong signal,
        }                       // queue might still be empty!
        return queue.poll();    // NPE or stale data!
    }
}
// Spurious wakeup: JVM/OS can wake a waiting thread
// without anyone calling notify(). This is by design (allowed by spec).
// Protection: re-check condition in while loop after wakeup.
```

---

### Java Condition (ReentrantLock version)

```java
// Condition: more explicit, allows multiple conditions per lock
public class BoundedBufferCondition<T> {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull  = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    private final Queue<T> queue = new ArrayDeque<>();
    private final int capacity;
    
    public BoundedBufferCondition(int capacity) {
        this.capacity = capacity;
    }
    
    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() == capacity) {
                notFull.await();     // wait on "not full" condition
            }
            queue.add(item);
            notEmpty.signal();       // signal ONE waiting consumer
            // vs notifyAll(): signal() is more efficient
            // (only wakes one thread, not all)
        } finally {
            lock.unlock();
        }
    }
    
    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();   // wait on "not empty" condition
            }
            T item = queue.poll();
            notFull.signal();       // signal ONE waiting producer
            return item;
        } finally {
            lock.unlock();
        }
    }
}

// Advantage: two separate conditions allow targeted signaling
// notEmpty.signal(): ONLY wakes a consumer (not producers)
// notFull.signal(): ONLY wakes a producer (not consumers)
// With Object.notifyAll(): wakes ALL waiters (some may go back to sleep)
// -> Condition.signal() is more efficient under high contention
```

---

### Spurious Wakeups Explained

```
POSIX specification explicitly allows spurious wakeups:
  pthread_cond_wait() "may" wake up even without a signal
  Reason: implementation simplicity on some OS
    (especially when signal is delivered during kernel operations)
    
  Linux: rare but possible under:
    Signal delivery (SIGINT etc.) interrupts the wait
    fork() during conditional wait (implementation artifact)
    
JVM specification:
  "A thread can wake up without being notified, interrupted,
   or timing out - a so-called 'spurious wakeup'"
   (java.lang.Object.wait() Javadoc)
   
Protection rule (MANDATORY):
  while (condition not met) {
      lock.wait();   // or condition.await()
  }
  // NEVER:
  if (condition not met) {
      lock.wait();
  }
```

---

### notify() vs notifyAll()

```
notify():
  Wakes ONE waiting thread (arbitrary choice by JVM/OS)
  Efficient: only one context switch
  DANGEROUS when: multiple distinct condition states used with one lock
    Thread waiting for "not full" may be woken
    by a "not empty" notify -> condition not met -> back to wait
    -> Other threads waiting for "not empty" never woken!
    -> Starvation or deadlock

notifyAll():
  Wakes ALL waiting threads
  They all compete for the lock, check condition (while loop)
  Most go back to sleep, one proceeds
  Inefficient: O(N) context switches per notification
  SAFE: guarantees no missed signal

Decision rule:
  Use notify() ONLY when:
    All waiting threads are waiting for EXACTLY the same condition
    Only one thread should proceed per notification
    
  Use notifyAll() otherwise (safer default)
  
  Use Condition.signal() + separate conditions:
    Most efficient + safe (targeted wakeup of correct condition)
```

---

### Failure Modes and Diagnosis

```
1. Lost Wakeup (missed notification)
Symptom: Thread waits forever despite condition being true
Cause: check-then-sleep without holding lock
  if (buffer.isEmpty())     // <- release lock here
    lock.wait()             // <- another thread signals here = LOST
Fix: always check condition AND wait while holding the SAME lock

2. Spurious wakeup bug (using if instead of while)
Symptom: NullPointerException, stale data, corrupted state
Cause: if (condition) wait(); -> processes after spurious wake
Fix: while (condition) wait(); -- non-negotiable rule

3. notifyAll() performance storm
Symptom: High CPU, many lock contentions under load
  All consumer threads wake up, one proceeds, rest re-sleep
  Repeated for every produced item: O(N^2) wakeup overhead
Fix: Use separate Condition variables (notFull, notEmpty)
  Or: Use BlockingQueue (ArrayBlockingQueue uses this pattern)
  ArrayBlockingQueue: uses separate Condition instances internally
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Spurious wakeups are theoretical and don't happen in practice" | Spurious wakeups do occur, especially in JVM on Linux when the waiting thread receives a signal (like SIGQUIT for thread dumps). Applications that use `if` instead of `while` for condition checks have real bugs that appear under production load |
| "notifyAll() is always safer than notify()" | notifyAll() prevents missed wakeups (safer) but causes a thundering herd: N threads wake up, N-1 go back to sleep. Under high concurrency, this creates significant lock contention and context-switch overhead. The correct fix is separate Condition objects with targeted signal() |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| wait() atomicity | Releases lock AND sleeps in one atomic operation |
| Spurious wakeup | Wakeup with no signal; always use `while`, never `if` |
| Java API | `Object.wait()/notify()` or `Condition.await()/signal()` |
| notifyAll vs signal | notifyAll: O(N) wakeups; Condition.signal(): targeted wakeup |
| Lost wakeup | Signal before wait() = lost; always check under same lock |
| BlockingQueue | ArrayBlockingQueue: production-grade condition variable use |
