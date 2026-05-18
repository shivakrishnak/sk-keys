---
id: OSY-017
title: Mutex (Mutual Exclusion Lock)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-007, OSY-029
used_by: OSY-030, OSY-038, OSY-062, OSY-063
related: OSY-018, OSY-030, OSY-062
tags:
  - foundational
  - mutex
  - lock
  - synchronization
  - critical-section
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/osy/mutex/
---

## TL;DR

A mutex (mutual exclusion lock) ensures only one thread
executes a critical section at a time. A thread acquires
the mutex (blocking if held), executes the protected
code, then releases. In Java: `synchronized` keyword
and `ReentrantLock` class.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-017 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | mutex, lock, synchronization, critical section |
| **Prerequisites** | OSY-007, OSY-029 |

---

### The Problem This Solves

A bank balance is 100. Two threads simultaneously:
Thread A reads 100, subtracts 50, intends to write 50.
Thread B reads 100, subtracts 30, intends to write 70.
Both write: balance becomes 70 (or 50, depending on
order). Net result: a $30 transaction vanished.

A mutex prevents this by ensuring only one thread
reads-and-writes at a time.

---

### Mutex Semantics

```
State: UNLOCKED (0) or LOCKED (1)

Thread acquires lock:
  if (mutex == UNLOCKED) {
    mutex = LOCKED; // must be atomic!
    return SUCCESS;
  } else {
    // BLOCKED: thread sleeps until mutex is released
    wait(mutex);
    // when woken: retry acquisition
  }
  
Thread releases lock:
  mutex = UNLOCKED;
  wake_one_waiter(mutex);  // if any threads waiting

ATOMIC requirement: the check-and-set must be one
indivisible operation. CPUs provide: CMPXCHG instruction.
OS provides: futex (fast user space mutex) for contended case.
```

---

### Java Mutex Implementations

```java
// 1. synchronized (intrinsic lock / monitor lock)
class BankAccount {
    private int balance = 100;
    
    // BAD: unsynchronized - race condition!
    public void withdraw_bad(int amount) {
        balance -= amount; // read-modify-write: NOT atomic
    }
    
    // GOOD: mutex protects the critical section
    public synchronized void withdraw(int amount) {
        if (balance >= amount) {
            balance -= amount;
        }
    }
    
    // GOOD: explicit ReentrantLock (more flexible)
    private final ReentrantLock lock = new ReentrantLock();
    
    public void withdrawWithLock(int amount) {
        lock.lock();
        try {
            if (balance >= amount) {
                balance -= amount;
            }
        } finally {
            lock.unlock(); // MUST be in finally!
        }
    }
    
    // GOOD: tryLock with timeout (avoids indefinite block)
    public boolean tryWithdraw(int amount, long timeout,
                                TimeUnit unit)
            throws InterruptedException {
        if (lock.tryLock(timeout, unit)) {
            try {
                if (balance >= amount) {
                    balance -= amount;
                    return true;
                }
            } finally {
                lock.unlock();
            }
        }
        return false; // lock not acquired in time
    }
}
```

---

### Mutex vs OS Thread State

```
When Thread B tries to acquire a HELD mutex:
  
  futex (fast path): check if mutex locked
    If locked: thread calls futex_wait() system call
    Thread state changes: RUNNING -> BLOCKED
    Thread removed from scheduler run queue
    
  When Thread A releases mutex:
    futex_wake() signals waiting threads
    Thread B state: BLOCKED -> READY
    Thread B re-added to run queue
    Thread B eventually gets CPU, acquires mutex
    
Cost of lock contention:
  Uncontended lock: ~20ns (atomic CAS in user space)
  Contended lock: ~1-10us (context switch to kernel)
  High-contention scenario: 50-100x overhead per lock
```

---

### Textbook Definition

A mutex (mutual exclusion lock) is a synchronization
primitive that grants exclusive access to a shared
resource. A thread that finds the mutex locked blocks
(enters BLOCKED state) until the holding thread releases
it. The acquire and release operations are atomic to
prevent races between multiple threads checking the mutex.

---

### Understand It in 30 Seconds

A mutex is a single key to a single door. Only the
thread holding the key can enter (critical section).
Other threads wait outside until the key is returned.
One at a time, no exceptions.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "synchronized in Java is always slow" | Uncontended synchronized is ~20ns (JVM uses biased locking). Contended synchronized causes thread blocking (~1-10us). For low-contention shared state, synchronized is fine; for high-contention, use concurrent collections |
| "All critical sections should be as small as possible" | Yes to minimizing critical section size, but sometimes grouping multiple operations into one critical section is necessary for atomicity. A "get then set" must be one atomic operation even if it's two lines |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Deadlock | Application hangs, threads blocked forever | Thread A holds lock 1, wants lock 2; Thread B holds lock 2, wants lock 1 | Always acquire locks in consistent order; use tryLock with timeout |
| Lock not in finally | Lock never released after exception | `lock.unlock()` missing in finally block | Always use try-finally for explicit locks |
| Security | Mutex bypass via reflection | Synchronized doesn't prevent reflection-based access | Use immutable objects or access control checks inside synchronized |

---

### Mastery Checklist

- [ ] Understands mutex as single-thread exclusion for critical sections
- [ ] Knows Java synchronized and ReentrantLock
- [ ] Knows to always put unlock() in finally block
- [ ] Understands uncontended vs contended lock cost difference
