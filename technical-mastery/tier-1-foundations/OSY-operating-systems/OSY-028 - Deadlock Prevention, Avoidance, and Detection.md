---
id: OSY-028
title: "Deadlock Prevention, Avoidance, and Detection"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-027
used_by: OSY-042
related: OSY-027, OSY-029, OSY-030
tags:
  - deadlock
  - prevention
  - avoidance
  - detection
  - bankers-algorithm
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/osy/deadlock-prevention-avoidance/
---

## TL;DR

Deadlock strategies are: Prevention (eliminate a Coffman
condition at design time), Avoidance (Banker's Algorithm
- never enter unsafe state), Detection and Recovery (let
it happen, then fix). In production Java, Prevention via
lock ordering is the standard; Avoidance is too expensive;
Detection via jstack or timeout-based lock acquisition.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-028 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | deadlock prevention, avoidance, Banker's Algorithm |
| **Prerequisites** | OSY-027 |

---

### Three Strategies Compared

```
Prevention: Eliminate >= 1 Coffman condition at DESIGN TIME
  - Design code so deadlock is structurally impossible
  - No runtime overhead
  - May reduce concurrency

Avoidance: Check EVERY resource request at RUNTIME
  - Banker's Algorithm: only grant requests that keep
    the system in a "safe state"
  - Runtime overhead per request
  - Requires knowing maximum resource needs upfront

Detection and Recovery: Let deadlock happen, then fix
  - Periodically check for cycles in resource graph
  - Recovery: preempt a resource, roll back, or kill a thread
  - Lowest design-time cost, highest incident cost
```

---

### Strategy 1: Prevention in Java

```java
// PREVENTION TECHNIQUE 1: Lock Ordering
// Assign a global order to all locks.
// Always acquire in ascending order.

// BAD: inconsistent order -> potential deadlock
class AccountBad {
    synchronized void transfer(Account other, int amount) {
        synchronized (other) {  // order: this, then other
            this.balance -= amount;
            other.balance += amount;
        }
    }
}
// T1: A.transfer(B) -> locks A, then tries B
// T2: B.transfer(A) -> locks B, then tries A -> DEADLOCK

// GOOD: consistent order via System.identityHashCode()
class AccountGood {
    void transfer(Account other, int amount) {
        // Determine lock order by object identity
        Object first = (System.identityHashCode(this) <
            System.identityHashCode(other)) ? this : other;
        Object second = (first == this) ? other : this;
        
        synchronized (first) {
            synchronized (second) {
                this.balance -= amount;
                other.balance += amount;
            }
        }
    }
}
// Both T1 and T2 always acquire same (lower hash) lock first
// Circular wait condition eliminated
```

```java
// PREVENTION TECHNIQUE 2: tryLock with timeout
// Allows preemption (removes "no preemption" condition)
class TransferService {
    private final Lock lock1 = new ReentrantLock();
    private final Lock lock2 = new ReentrantLock();
    
    boolean transfer(int amount) throws InterruptedException {
        while (true) {
            boolean got1 = false, got2 = false;
            try {
                got1 = lock1.tryLock(100, TimeUnit.MILLISECONDS);
                got2 = lock2.tryLock(100, TimeUnit.MILLISECONDS);
                if (got1 && got2) {
                    performTransfer(amount);
                    return true;
                }
            } finally {
                // Release everything if we couldn't get both
                if (got1) lock1.unlock();
                if (got2) lock2.unlock();
            }
            // Back off and retry (prevent live-lock with random delay)
            Thread.sleep(10 + ThreadLocalRandom.current().nextInt(50));
        }
    }
}
// "No preemption" condition removed: timeouts allow backing off
```

---

### Strategy 2: Avoidance (Banker's Algorithm)

```
Banker's Algorithm (Dijkstra 1965):
  Track: max resource claim, current allocation, remaining need
  On each request: check if granting request leaves a "safe state"
  Safe state: there exists an order to complete all threads
  
Example with 1 resource type (12 instances total):
  
  Thread | Max | Allocated | Need | Available
  -------|-----|-----------|------|----------
  T0     |  10 |         5 |    5 | 
  T1     |   4 |         2 |    2 |
  T2     |   9 |         3 |    6 |
  Total allocated = 10, Available = 12 - 10 = 2
  
  Safe sequence check: T1 (needs 2, available=2) -> runs,
  releases 2+2=4 -> T0 (needs 5, available=4) BLOCKED!
  Recalculate: after T1, available=4; T0 needs 5 -> not safe yet
  Wait for T2? T2 needs 6 > available 4... unsafe!
  
  Actually: T1 completes (need=2, available=2) -> 
  available=4; T0 needs 5 > 4 -> can't run;
  T2 needs 6 > 4 -> can't run.
  State IS unsafe: if T0 or T2 request their remaining need,
  deadlock would occur.
  
  If T0 had requested 1 more (need 5->4 remaining):
  T1 completes -> available=4; T0 completes -> available=9;
  T2 completes -> safe!

Why not used in practice:
  1. Requires knowing maximum resource claim in advance
  2. O(n^2) check per request (n = thread count)
  3. Resources can vary at runtime (network connections, etc.)
  4. May refuse valid requests to stay "safe"
```

---

### Strategy 3: Detection and Recovery

```bash
# Detection: scan for cycles in resource allocation graph

# In Java (JVM detection):
ThreadMXBean bean = ManagementFactory.getThreadMXBean();

# findDeadlockedThreads(): Java object monitor deadlocks
# findMonitorDeadlockedThreads(): java.util.concurrent locks
long[] deadlockedThreads = bean.findDeadlockedThreads();
if (deadlockedThreads != null) {
    // Deadlock detected!
    // Recovery options:
    // 1. Log the thread dump and alert ops team
    // 2. Interrupt one of the deadlocked threads
    for (long tid : deadlockedThreads) {
        // Find thread handle and interrupt
        // (interruption may not help if threads use
        //  non-interruptible synchronized blocks)
    }
}

# Database deadlock detection example:
# PostgreSQL: automatic deadlock detection, kills one transaction
# MySQL InnoDB: deadlock detection enabled by default
# Resolution: one transaction automatically rolled back
# Application must catch SQLException(code=1213 MySQL,
#   or "deadlock detected" for PostgreSQL) and retry
```

```java
// Recovery pattern: retry with exponential backoff
public <T> T executeWithDeadlockRetry(
        Callable<T> dbOperation) throws Exception {
    int maxRetries = 3;
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return dbOperation.call();
        } catch (DeadlockLoserException e) {
            if (attempt == maxRetries) throw e;
            // Exponential backoff: 100ms, 200ms, 400ms
            Thread.sleep(100L * (1L << (attempt - 1)));
        }
    }
    throw new RuntimeException("Unreachable");
}
```

---

### Choosing the Right Strategy

```
Decision guide:

1. Custom locking code (synchronized, ReentrantLock)?
   -> USE PREVENTION: lock ordering or tryLock with timeout
   
2. Database transactions?
   -> USE DETECTION: DB handles it; application catches
      deadlock errors and retries transaction
   
3. Complex resource allocation (connection pools, etc.)?
   -> USE PREVENTION: pool sizing limits and acquisition
      ordering to prevent cross-resource cycles
      
4. System with formal resource bounds (OS, embedded)?
   -> CONSIDER AVOIDANCE: Banker's Algorithm if maximum
      claims are statically known
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Banker's Algorithm is used in modern operating systems" | Modern OSes do not implement Banker's Algorithm. It requires knowing thread maximum resource needs upfront (impossible for general-purpose OSes) and has O(n^2) overhead. OSes use prevention (resource ordering in kernel code) and detection (timeouts) instead |
| "Detection-based systems always have worse deadlock rates than prevention-based" | Databases use detection because prevention would over-restrict concurrency. Detection + automatic rollback of one transaction is cheaper than the overhead of prevention at the transaction level |

---

### Related Keywords

**Builds on:** OSY-027 (Deadlock Definition and Coffman Conditions)

**Related:** OSY-029 (Race Condition), OSY-030 (Mutex vs
Semaphore vs Monitor)

**Used by:** OSY-042 (OS Interview Essentials - Working Level)

---

### Quick Reference Card

| Strategy | When to Use | Java Mechanism | Cost |
|----------|------------|----------------|------|
| Prevention (ordering) | Custom sync code | Lock ordering by identity hash | Design time only |
| Prevention (timeout) | Multi-lock acquisition | ReentrantLock.tryLock(timeout) | Small runtime overhead |
| Avoidance | Known max resources | N/A (not used in Java) | O(n^2) per request |
| Detection | Database transactions | Catch DeadlockException, retry | Incident response cost |

---

### Interview Deep-Dive

**Q1 (Easy): What is the difference between deadlock
prevention and avoidance?**
Prevention eliminates a Coffman condition at design time
(e.g., lock ordering eliminates circular wait). Avoidance
checks every resource request at runtime to stay in a safe
state (Banker's Algorithm). Prevention is a design
constraint; avoidance is a runtime mechanism.

**Q2 (Medium): A Java service occasionally hangs with no
error messages. How do you confirm it is a deadlock and
not something else (like an infinite loop)?**
Deadlock vs infinite loop: `jstack -l PID` - deadlock
shows BLOCKED threads with "Found Java-level deadlock";
infinite loop shows RUNNABLE thread consuming CPU (visible
in `top`). For deadlock: no CPU consumption (threads are
blocked waiting, not spinning). vmstat will show low CPU
usage and high blocked thread count.

**Q3 (Hard): Your microservices system has Service A
calling Service B, and Service B calling Service C, and
Service C calling Service A for some business flows.
A distributed deadlock occurs. How do you diagnose and fix?**
Distributed deadlock: no single jstack can show it.
Diagnosis: distributed tracing (OpenTelemetry) to trace
request spans - look for circular wait chains in traces.
The trace will show A->B->C->A with A waiting. Fix:
break the cycle by making one call asynchronous (return
event, process async) or by timeout + circuit breaker.
Set service call timeouts short enough that a deadlock
cycle unwinds in < 30 seconds (each service times out
and returns error). Monitor with circuit breaker to
prevent cascade retry storms after timeout.
