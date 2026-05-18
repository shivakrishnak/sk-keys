---
id: OSY-018
title: Semaphore
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-017
used_by: OSY-030
related: OSY-017, OSY-030, OSY-040
tags:
  - foundational
  - semaphore
  - synchronization
  - counting
  - concurrency
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/osy/semaphore/
---

## TL;DR

A semaphore is a generalized mutex that controls access
to a resource pool. A binary semaphore (value 0 or 1)
works like a mutex. A counting semaphore limits N
concurrent accesses - used for connection pools, rate
limiting, and thread pool coordination.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-018 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | semaphore, counting, synchronization |
| **Prerequisites** | OSY-017 |

---

### Semaphore Operations

```
Semaphore has integer value: S

P (wait / acquire / down):
  if (S > 0): S-- (atomic), proceed
  else: block until S > 0

V (signal / release / up):
  S++ (atomic)
  if any threads waiting: wake one

Binary semaphore (S = 0 or 1):
  Works like mutex but with important difference:
  Mutex: ONLY the thread that locked can unlock
  Semaphore: ANY thread can signal (release)
  Use case: signaling between threads (one thread waits
            for event from another thread)

Counting semaphore (S = N):
  Allows up to N concurrent accesses
  Classic use: connection pool of N connections
  Thread needs connection: P() -> blocks if 0 available
  Thread releases connection: V() -> wakes waiting thread
```

---

### Java Semaphore

```java
import java.util.concurrent.Semaphore;

// Connection pool implementation using Semaphore:
class ConnectionPool {
    private final Semaphore semaphore;
    private final Queue<Connection> connections;
    
    ConnectionPool(int poolSize) {
        this.semaphore = new Semaphore(poolSize);
        this.connections = new ArrayDeque<>();
        for (int i = 0; i < poolSize; i++) {
            connections.offer(new Connection());
        }
    }
    
    Connection acquire() throws InterruptedException {
        semaphore.acquire(); // blocks if 0 available
        synchronized (connections) {
            return connections.poll();
        }
    }
    
    void release(Connection conn) {
        synchronized (connections) {
            connections.offer(conn);
        }
        semaphore.release(); // wake a waiting thread
    }
}

// Semaphore for signaling (binary semaphore pattern):
Semaphore ready = new Semaphore(0); // starts at 0

// Worker thread: initialize then signal
Thread worker = new Thread(() -> {
    doInitialization();
    ready.release(); // V() - signal completion
});

// Main thread: wait for worker to be ready
ready.acquire(); // P() - blocks until signal
startServer();
```

---

### Semaphore vs Mutex

| Aspect | Mutex | Semaphore |
|--------|-------|-----------|
| Value | Binary (0/1) | Integer (0 to N) |
| Ownership | Locked by one thread, unlocked by same | Any thread can V() |
| Use case | Mutual exclusion | Resource counting, signaling |
| Java equivalent | synchronized, ReentrantLock | java.util.concurrent.Semaphore |
| Deadlock risk | Yes (if lock order wrong) | Yes (but different patterns) |

---

### Textbook Definition

A semaphore is a synchronization primitive consisting
of an integer counter and two atomic operations: P
(wait/acquire, decrement) and V (signal/release,
increment). A binary semaphore has value 0 or 1 (used
for signaling). A counting semaphore has value N
(used to limit concurrent access to N units of a resource).

---

### Understand It in 30 Seconds

A semaphore is a parking lot gate with a counter. The
counter shows free parking spaces. Each car entering
decrements the counter. Each car leaving increments.
If counter = 0, cars wait at the gate (blocked). Mutex
is a parking lot with exactly 1 space.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Semaphore is just a mutex" | A mutex has ownership (only the locking thread can unlock). A semaphore has no ownership - any thread can V(). This makes semaphores suitable for signaling but dangerous for mutual exclusion (releasing without acquiring is a bug) |
| "Use semaphore for everything" | Semaphores are low-level. Java's higher-level constructs (BlockingQueue, CountDownLatch, CyclicBarrier) are typically better for producer-consumer, coordination, and barrier patterns |

---

### Mastery Checklist

- [ ] Knows P() decrements (blocks if 0) and V() increments (wakes waiter)
- [ ] Can implement a connection pool using counting semaphore
- [ ] Understands semaphore vs mutex ownership difference
- [ ] Knows Java Semaphore class and its acquire/release methods
