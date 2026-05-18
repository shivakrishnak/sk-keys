---
id: OSY-030
title: Mutex vs Semaphore vs Monitor
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-017, OSY-018, OSY-029
used_by: OSY-038, OSY-042
related: OSY-017, OSY-018, OSY-029, OSY-038
tags:
  - mutex
  - semaphore
  - monitor
  - synchronization
  - comparison
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/osy/mutex-semaphore-monitor/
---

## TL;DR

Mutex: binary lock with strict ownership (only the
locking thread can unlock). Semaphore: counting permit
with no ownership (any thread can release). Monitor:
mutex plus condition variable bundled together. Java
`synchronized` implements monitor semantics. Use mutex
for mutual exclusion, semaphore for signaling/limiting,
monitor for complex wait-notify patterns.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-030 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | mutex, semaphore, monitor, concurrency primitives |
| **Prerequisites** | OSY-017, OSY-018, OSY-029 |

---

### The Three Primitives Defined

```
Mutex (Mutual Exclusion Lock):
  - Binary: locked or unlocked
  - Ownership: only the thread that locked can unlock
  - Purpose: mutual exclusion (one thread in CS at a time)
  - Operations: lock() / unlock()
  - Java equivalent: synchronized block, ReentrantLock

Semaphore:
  - Integer count: 0 to N
  - No ownership: any thread can signal (V/release)
  - Purpose: signaling and resource counting
  - Operations: P() = wait/down (decrement), V() = signal/up (increment)
  - Java equivalent: java.util.concurrent.Semaphore
  - Binary semaphore (count=1): NOT a mutex (no ownership!)

Monitor:
  - Mutex + condition variable combined
  - Ownership same as mutex
  - Condition: queue of threads waiting for a state condition
  - Operations: lock, unlock, wait (releases lock and sleeps),
    notify (wakes one waiter), notifyAll (wakes all waiters)
  - Java equivalent: every Object (wait/notify/notifyAll)
  - Higher-level than mutex or semaphore
```

---

### Code Examples

```java
// MUTEX via synchronized block
public class MutexExample {
    private int counter = 0;
    private final Object lock = new Object();
    
    public void increment() {
        synchronized (lock) {       // lock() - one thread enters
            counter++;               // critical section
        }                           // unlock() - released automatically
        // Thread that locked MUST be the one to reach closing brace
    }
}

// MUTEX via ReentrantLock (more control)
public class ReentrantLockExample {
    private int counter = 0;
    private final ReentrantLock lock = new ReentrantLock();
    
    public void increment() {
        lock.lock();                // explicit lock
        try {
            counter++;
        } finally {
            lock.unlock();          // MUST be in finally!
            // Same thread that called lock() must call unlock()
        }
    }
    
    public void tryIncrement() {
        if (lock.tryLock()) {      // non-blocking attempt
            try {
                counter++;
            } finally {
                lock.unlock();
            }
        }
    }
}
```

```java
// SEMAPHORE for connection pool limiting
// Limits concurrent database connections to MAX_CONN
public class ConnectionPool {
    private final Semaphore semaphore;
    private final Queue<Connection> connections;
    private static final int MAX_CONN = 10;
    
    public ConnectionPool() {
        semaphore = new Semaphore(MAX_CONN);  // 10 permits
        // initialize connections...
    }
    
    public Connection acquire() throws InterruptedException {
        semaphore.acquire();        // P(): decrement, blocks if 0
        return connections.poll();  // get a connection
    }
    
    public void release(Connection conn) {
        connections.offer(conn);    // return connection
        semaphore.release();        // V(): increment
        // Note: ANY thread can call release(), not just acquirer
        // This is different from mutex!
    }
}
```

```java
// MONITOR: wait/notify pattern for producer-consumer
public class BoundedBuffer {
    private final Queue<Integer> buffer = new LinkedList<>();
    private final int MAX_SIZE = 10;
    
    // synchronized on 'this' = monitor on this object
    public synchronized void produce(int value)
            throws InterruptedException {
        while (buffer.size() == MAX_SIZE) {
            wait();  // releases lock, sleeps on condition
            // wait() is ALWAYS inside while loop (not if!)
            // because of spurious wakeups
        }
        buffer.add(value);
        notifyAll();  // wake waiting consumers
    }
    
    public synchronized int consume()
            throws InterruptedException {
        while (buffer.isEmpty()) {
            wait();  // releases lock, sleeps on condition
        }
        int value = buffer.poll();
        notifyAll();  // wake waiting producers
        return value;
    }
}
// 'this' object's monitor: lock + wait set + condition
```

---

### Comparison Table

| Property | Mutex | Semaphore | Monitor |
|----------|-------|-----------|---------|
| State | Locked/Unlocked | Integer 0..N | Locked/Unlocked + condition queue |
| Ownership | YES (only locker can unlock) | NO (any thread can signal) | YES |
| Purpose | Mutual exclusion | Signaling, counting | Mutual exclusion + condition |
| Wait on condition | No (use separately) | No (use separately) | YES (built in) |
| Java equivalent | synchronized, ReentrantLock | java.util.concurrent.Semaphore | synchronized + wait/notify |
| Risk | Deadlock if not released | Permit leak / over-release | Spurious wakeup (use while loop) |
| Recursive entry | YES (ReentrantLock) | NO (Semaphore(1) != mutex) | YES (synchronized is reentrant) |

---

### Critical Difference: Ownership

```
Mutex with Ownership:
  Thread A: lock.lock()  <-- A owns it
  Thread B: lock.unlock() <-- ERROR or ignored
  Thread A: lock.unlock() <-- OK, A releases what A owns
  
  Why ownership matters: prevents a helper thread from
  accidentally releasing a mutex it doesn't own.
  Also enables reentrancy: owning thread can lock again
  without deadlocking (ReentrantLock, Java synchronized).

Semaphore without Ownership:
  Thread A: semaphore.acquire()  <-- permits decremented
  Thread B: semaphore.release()  <-- valid! B can release A's permit
  
  Why no-ownership is useful: Producer/Consumer - producer
  signals that work is available; consumer waits. Different
  threads acquire vs release permits.
  
  Danger: semaphore.release() called without prior acquire()
  -> permits > maximum -> over-admission bug.
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Binary semaphore (count=1) is the same as a mutex" | Binary semaphore has no ownership. Any thread can release it. Mutex ownership prevents a helper/other thread from accidentally releasing the lock. Also: binary semaphore doesn't support reentrancy (calling acquire() twice from same thread deadlocks) |
| "wait() should be in an if statement, not while" | wait() can return spuriously (wake up for no reason). ALWAYS wrap wait() in a while loop that re-checks the condition. This is a classic Java concurrency bug |
| "ReentrantLock is always better than synchronized" | synchronized is simpler, JIT-optimized (biased locking, lock elision), and perfectly adequate for most cases. ReentrantLock advantages: tryLock with timeout, fair locking, multiple condition variables |

---

### Failure Modes and Diagnosis

```
Mutex Failure: Deadlock
  Cause: Thread holds lock, never releases (exception path
    skips unlock without try/finally)
  Diagnosis: jstack shows BLOCKED threads
  Fix: always unlock in finally block

Semaphore Failure: Permit Leak
  Cause: acquire() without matching release() in error path
  Symptom: semaphore permits drain to 0, all acquire() block
  Diagnosis: semaphore.availablePermits() returns 0
  Fix: release() in finally block

Monitor Failure: Lost Signal
  Cause: notify() called when no thread is waiting,
    then another thread calls wait() and waits forever
  Symptom: thread permanently blocked in wait()
  Fix: check condition before waiting (while loop);
    use notifyAll() instead of notify() when in doubt

Monitor Failure: Spurious Wakeup Loop Bug
  BAD:
    if (buffer.isEmpty()) wait();  // if, not while
  Symptom: NullPointerException or incorrect behavior
    after wait() returns spuriously
  Fix:
    while (buffer.isEmpty()) wait();  // re-check condition
```

---

### Related Keywords

**Builds on:** OSY-017 (Mutex), OSY-018 (Semaphore),
OSY-029 (Race Condition and Critical Section)

**Related:** OSY-038 (Thread-Safe Programming), OSY-027 (Deadlock)

---

### Quick Reference Card

| Use Case | Best Choice | Java API |
|---------|------------|---------|
| Single shared variable | AtomicInteger | java.util.concurrent.atomic |
| Mutual exclusion | synchronized or ReentrantLock | synchronized, Lock |
| Resource pool limiting | Semaphore | Semaphore(N) |
| Producer-consumer | Monitor | synchronized + wait/notifyAll |
| Timed lock acquisition | ReentrantLock | tryLock(timeout) |
| Read-heavy, write-rare | ReadWriteLock | ReentrantReadWriteLock |

---

### Interview Deep-Dive

**Q1 (Easy): What is the difference between a mutex and
a semaphore?**
Mutex has ownership: only the thread that locked it
can unlock it. Semaphore has no ownership: any thread
can release a permit. Mutex is for mutual exclusion;
semaphore is for signaling and resource counting.

**Q2 (Medium): Why should wait() always be in a while
loop and not an if statement?**
Spurious wakeups: the JVM specification permits wait()
to return without a corresponding notify() call. If
the loop condition is checked only once (if), the
thread proceeds even though the condition isn't met.
Always use `while (condition not met) { wait(); }` to
re-evaluate the condition after every wakeup.

**Q3 (Hard): Explain how Java synchronized implements
monitor semantics and how it differs from ReentrantLock.**
Java synchronized is monitor semantics: every Java
Object has a monitor header (mark word in object header)
with: mutex state (locked/unlocked), owning thread ID,
lock count (for reentrancy), and entry/wait queues.
`wait()`, `notify()`, and `notifyAll()` operate on one
implicit condition queue. ReentrantLock uses AQS
(AbstractQueuedSynchronizer) with a CLH spin-then-park
queue. Key differences: ReentrantLock allows multiple
Condition objects (multiple wait/notify queues),
`tryLock(timeout)`, `lockInterruptibly()`, and fair
ordering. synchronized is JIT-optimized (biased locking
eliminates CAS for single-thread scenarios) and simpler.
