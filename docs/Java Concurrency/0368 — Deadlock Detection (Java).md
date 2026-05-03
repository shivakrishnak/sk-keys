---
layout: default
title: "Deadlock Detection (Java)"
parent: "Java Concurrency"
nav_order: 368
permalink: /java-concurrency/deadlock-detection-java/
number: "0368"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread (Java), synchronized, ReentrantLock, Thread Dump Analysis
used_by: Observability & SRE, Production Debugging
related: Thread Dump Analysis, Lock Striping, Livelock
tags:
  - java
  - concurrency
  - deep-dive
  - debugging
  - deadlock
---

# 0368 — Deadlock Detection (Java)

⚡ TL;DR — A deadlock occurs when two or more threads each hold a lock the other needs, forming a circular wait from which no thread can proceed — Java's `ThreadMXBean` can detect them programmatically, and the four Coffman conditions (mutual exclusion, hold-and-wait, no preemption, circular wait) tell you which one to eliminate to prevent them.

| #0368           | Category: Java Concurrency                                       | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread (Java), synchronized, ReentrantLock, Thread Dump Analysis |                 |
| **Used by:**    | Observability & SRE, Production Debugging                        |                 |
| **Related:**    | Thread Dump Analysis, Lock Striping, Livelock                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two payment processing threads, Thread A and Thread B, each need to lock two accounts to transfer money between them. Thread A locks Account 1, Thread B locks Account 2. Thread A tries to lock Account 2 — blocked. Thread B tries to lock Account 1 — blocked. Neither thread can proceed. The payment service silently hangs. No exception. No timeout. Thread pool threads fill up. Service goes unresponsive. The bug is in production and there's no way to diagnose it from logs.

**THE BREAKING POINT:**
Deadlocks are silent by default. No exception is thrown. No error is logged. The affected threads simply stop making progress. If the deadlocked threads hold resources (like thread pool threads), the entire service can become unresponsive. Without deadlock detection, you're left with thread dumps, prayer, and a restarted service — without fixing the root cause.

**THE INVENTION MOMENT:**
Java's `ThreadMXBean` was designed to expose deadlock detection as a first-class JVM capability. `findDeadlockedThreads()` uses the JVM's internal wait-for graph to detect circular dependencies in both `synchronized` monitors and `ReentrantLock`/`AbstractQueuedSynchronizer` locking — returning the thread IDs involved so you can programmatically alert on deadlocks, not just discover them during post-incident analysis.

---

### 📘 Textbook Definition

**Deadlock:** A state where two or more threads are permanently blocked, each waiting for a resource held by another thread in the cycle. Named after Dijkstra (1965). Requires all four Coffman conditions simultaneously: (1) mutual exclusion, (2) hold-and-wait, (3) no preemption, (4) circular wait.

**Coffman conditions:** Four necessary and sufficient conditions for deadlock. Eliminating any one condition prevents deadlock. In Java: (1) mutual exclusion = locks/monitors; (2) hold-and-wait = holding lock A while requesting lock B; (3) no preemption = JVM doesn't forcibly release locks; (4) circular wait = Thread A waits for B, B waits for A.

**Livelock:** A variant where threads are not blocked but continuously change state in response to each other without making progress — like two people trying to pass in a hallway who keep stepping the same way. CPU stays high (unlike deadlock where CPU drops to 0).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Deadlock is two threads each holding the lock the other needs — they wait forever, neither makes progress, and the service silently hangs.

**One analogy:**

> Two diners at a fondue restaurant, one fork and one knife on the table. Diner A grabs the fork, Diner B grabs the knife. Diner A needs the knife to eat, Diner B needs the fork. Neither lets go of what they have. They both wait. Indefinitely. The restaurant service stops.

**One insight:**
The simplest deadlock prevention strategy is lock ordering: always acquire locks in the same global order. If ALL threads agree to always lock Account 1 before Account 2 (never the other way), circular wait becomes impossible — you've eliminated Coffman condition #4. This is the lock ordering principle.

---

### 🔩 First Principles Explanation

**THE FOUR COFFMAN CONDITIONS (must ALL be true for deadlock):**

```
1. MUTUAL EXCLUSION
   A resource can only be held by one thread at a time.
   In Java: a synchronized block or ReentrantLock.
   Elimination: use non-exclusive resources (read locks, copy-on-write).
   Usually not eliminable for correctness reasons.

2. HOLD-AND-WAIT
   A thread holds at least one resource while waiting for another.
   Elimination: acquire all locks atomically at once (all-or-nothing).
   In Java: tryLock() with backoff — acquire A, try B, if fail release A and retry.

3. NO PREEMPTION
   Locks cannot be forcibly taken from a thread.
   Elimination: use timed locks (tryLock(timeout)) — thread voluntarily
   releases locks if it can't acquire all needed ones within timeout.

4. CIRCULAR WAIT
   Thread A waits for something Thread B holds; Thread B waits for
   something Thread A holds (or through a longer chain).
   Elimination: enforce a global lock ordering — all threads acquire
   locks in the same predefined order (by ID, hash, etc.).
   MOST PRACTICAL prevention in Java.
```

**DEADLOCK EXAMPLE — THE CLASSIC LOCK INVERSION:**

```java
// BAD: locks acquired in different orders (lock inversion)
// Thread A:
synchronized (account1) {           // holds account1
    synchronized (account2) {       // waits for account2
        transfer(account1, account2);
    }
}

// Thread B (simultaneously):
synchronized (account2) {           // holds account2
    synchronized (account1) {       // waits for account1 — DEADLOCK
        transfer(account2, account1);
    }
}

// GOOD: always lock in the same order (by account ID)
Account first  = account1.id < account2.id ? account1 : account2;
Account second = account1.id < account2.id ? account2 : account1;
synchronized (first) {
    synchronized (second) {
        transfer(account1, account2);
    }
}
// Both threads acquire locks in the same order → no circular wait → no deadlock
```

---

### 🧪 Thought Experiment

**SETUP:**
A microservice has an in-memory `ConcurrentHashMap` cache. Cache access is protected by `cachelock`. Database access is protected by `dbLock`. Two operations are performed concurrently:

- Operation X: `cachelock.lock()` → check cache → if miss: `dbLock.lock()` → fetch DB → populate cache → `dbLock.unlock()` → `cachelock.unlock()`
- Operation Y: `dbLock.lock()` → refresh DB connection → check if cache needs invalidation → `cachelock.lock()` → clear cache → `cachelock.unlock()` → `dbLock.unlock()`

**WHAT HAPPENS:**
Thread 1 (Op X): acquires cachelock → waiting for dbLock
Thread 2 (Op Y): acquires dbLock → waiting for cachelock
DEADLOCK. Service hangs on every concurrent cache-miss + cache-invalidation.

**THE FIX:**
Enforce lock ordering: always acquire `cachelock` before `dbLock`, OR always acquire `dbLock` before `cachelock` — consistently across both operations. Operation Y must be redesigned to either: not hold cachelock while holding dbLock, or use the same lock acquisition order as Operation X.

**THE INSIGHT:**
Deadlocks are rarely obvious in code review. They emerge at runtime when two concurrent operations happen to interleave in exactly the wrong order. Lock ordering review — ensuring all code paths acquire the same locks in the same order — is the only static prevention technique.

---

### 🧠 Mental Model / Analogy

> Deadlock is the "Mexican standoff" of lock acquisition: Thread A points its gun at Thread B (waiting for B's lock), Thread B points its gun at Thread A (waiting for A's lock). Neither can move forward without the other dropping their weapon first. Since neither will drop their weapon first, the standoff is permanent.

Explicit mapping:

- "gun pointed at someone" → holding a lock another thread needs
- "waiting for them to drop their weapon" → blocked, waiting for the other's lock
- "permanent standoff" → deadlock (neither thread can proceed)
- "both drop simultaneously" → tryLock() with timeout (voluntary release)
- "agreed firing order" → lock ordering (eliminate circular wait)

Where this analogy breaks down: in a real standoff, a third party could intervene. JVM does NOT preempt locks — there's no "third party" that can force a thread to release a lock. The only interventions are: the thread voluntarily releases via `tryLock(timeout)`, the thread is interrupted (`lockInterruptibly()`), or the JVM is restarted.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Deadlock is when two threads each need something the other has and neither will let go first. They wait forever. Nothing moves. The solution is to always grab resources in the same order so this circular waiting can never happen.

**Level 2 — How to prevent it (junior developer):**
(a) Lock ordering: always acquire locks in the same order across all code paths. (b) Use `tryLock(timeout)` instead of `lock()` — if you can't acquire within the timeout, release what you hold and retry. (c) Avoid nested locking when possible. (d) Use `ThreadMXBean.findDeadlockedThreads()` in your health check endpoint to detect deadlocks automatically.

**Level 3 — How to detect and fix (mid-level engineer):**
At runtime: `jstack -l <pid>` reports "Found one Java-level deadlock" and prints the involved thread stacks and lock addresses. Programmatically: `mxBean.findDeadlockedThreads()` returns thread IDs involved in a deadlock cycle. For prevention: implement a total ordering on all lock objects (by `System.identityHashCode()` for arbitrary objects, or by a domain ID for business objects). For recovery: `ReentrantLock.lockInterruptibly()` allows deadlocked threads to be broken out by interruption — JVM cannot interrupt `synchronized` deadlocks, but can interrupt `lockInterruptibly()` waiters.

**Level 4 — Why it's architecturally important (senior/staff):**
Deadlock prevention is a locking discipline problem, not an implementation problem. The real solution is to minimize lock scope: if a method only needs to read from a map while holding a lock, it should release the lock before making any external call. The canonical architecture principle: never hold a lock while calling code you don't control (callbacks, external services, user-supplied functions). This is because user-supplied code might itself try to acquire locks that create a cycle. This principle explains why Java GUI frameworks (Swing, JavaFX) require all UI updates to happen on a single thread — it eliminates the class of GUI deadlocks that would arise from multi-threaded UI access.

---

### ⚙️ How It Works (Mechanism)

```
JVM DEADLOCK DETECTION:

The JVM maintains a "wait-for graph" internally:
  - Each thread has a "waiting_for" pointer (what lock it wants)
  - Each lock has an "owner" pointer (what thread holds it)

To detect deadlock, JVM follows the chain:
  Thread A → waiting for Lock X
  Lock X owned by → Thread B
  Thread B → waiting for Lock Y
  Lock Y owned by → Thread A ← CYCLE! → DEADLOCK

ThreadMXBean.findDeadlockedThreads():
  Walks the wait-for graph looking for cycles.
  Returns array of thread IDs in the deadlock cycle.
  Returns null if no deadlock detected.
  Detects: synchronized monitors + ReentrantLock (ownable synchronizers)

ThreadMXBean.findMonitorDeadlockedThreads():
  Like above but ONLY synchronized monitors, not ReentrantLock.

Thread.State.BLOCKED:
  Waiting for a synchronized monitor.
  JVM's deadlock detection covers these.

Thread.State.WAITING (parking):
  Waiting in LockSupport.park() (ReentrantLock.lock() internally).
  Also covered by findDeadlockedThreads() via ownable synchronizers.
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Two threads, two locks:
  Thread A acquires Lock 1 → tries to acquire Lock 2 → BLOCKS
  Thread B acquires Lock 2 → tries to acquire Lock 1 → BLOCKS
    ↓
JVM wait-for graph:
  A → waits for Lock2 (owned by B)
  B → waits for Lock1 (owned by A)
  Cycle detected: A → B → A
    ↓
ThreadMXBean.findDeadlockedThreads() → [threadA.id, threadB.id]
    ↓
Health check endpoint detects deadlock
    ↓
Alert fires: "DEADLOCK DETECTED in thread IDs [42, 43]"
    ↓
Dump stack traces of deadlocked threads for RCA
    ↓
Root cause: lock inversion in OrderService.transfer()
    ↓
Fix: enforce lock ordering by account ID
```

---

### 💻 Code Example

**Example 1 — Lock ordering prevention:**

```java
// Classic deadlock prevention via consistent lock ordering
public class BankTransfer {
    public void transfer(Account from, Account to, BigDecimal amount) {
        // ALWAYS lock in the same order (lower ID first)
        Account first  = from.getId() < to.getId() ? from : to;
        Account second = from.getId() < to.getId() ? to : from;

        synchronized (first) {
            synchronized (second) {
                from.debit(amount);
                to.credit(amount);
            }
        }
    }
}
```

**Example 2 — tryLock with timeout (eliminates hold-and-wait):**

```java
public class SafeTransfer {
    public boolean transfer(Account from, Account to, BigDecimal amount)
            throws InterruptedException {
        long timeout = 100;
        TimeUnit unit = TimeUnit.MILLISECONDS;

        while (true) {
            if (from.getLock().tryLock(timeout, unit)) {
                try {
                    if (to.getLock().tryLock(timeout, unit)) {
                        try {
                            from.debit(amount);
                            to.credit(amount);
                            return true;
                        } finally {
                            to.getLock().unlock();
                        }
                    }
                    // Failed to acquire second lock — release first and retry
                } finally {
                    from.getLock().unlock();
                }
            }
            // Both locks not acquired — back off and retry
            Thread.sleep(ThreadLocalRandom.current().nextLong(1, 10));
        }
    }
}
```

**Example 3 — Programmatic deadlock detection (health check):**

```java
import java.lang.management.*;

@Component
public class DeadlockHealthCheck {
    private final ThreadMXBean threadMX = ManagementFactory.getThreadMXBean();

    @Scheduled(fixedRate = 30_000) // check every 30 seconds
    public void checkForDeadlocks() {
        long[] deadlockedIds = threadMX.findDeadlockedThreads();
        if (deadlockedIds != null && deadlockedIds.length > 0) {
            ThreadInfo[] info = threadMX.getThreadInfo(deadlockedIds, true, true);
            StringBuilder sb = new StringBuilder("DEADLOCK DETECTED:\n");
            for (ThreadInfo ti : info) {
                sb.append("Thread: ").append(ti.getThreadName())
                  .append(", State: ").append(ti.getThreadState())
                  .append(", Waiting for: ").append(ti.getLockName()).append("\n");
                for (StackTraceElement ste : ti.getStackTrace()) {
                    sb.append("    ").append(ste).append("\n");
                }
            }
            log.error(sb.toString());
            // Alert: page on-call, trigger diagnostic dump, etc.
            alertService.critical("JVM_DEADLOCK", sb.toString());
        }
    }
}
```

---

### ⚖️ Comparison Table

| Problem                | CPU                     | Progress               | Detection                               | Resolution                          |
| ---------------------- | ----------------------- | ---------------------- | --------------------------------------- | ----------------------------------- |
| **Deadlock**           | Low (threads blocked)   | None (permanent)       | ThreadMXBean, jstack                    | Fix code: lock ordering / tryLock   |
| Livelock               | High (threads spinning) | None (busy spinning)   | Profiler (CPU hot spot)                 | Add backoff, randomise retry        |
| Starvation             | Variable                | Some (others progress) | Thread dump (one thread always blocked) | Ensure fair scheduling / fair locks |
| Thread pool exhaustion | Low (threads waiting)   | None for new requests  | Thread dump (all pool threads WAITING)  | Fix timeout on blocking calls       |

How to distinguish: CPU low + threads BLOCKED = deadlock. CPU high + threads RUNNABLE but no real work = livelock. CPU low + threads WAITING in I/O = pool exhaustion.

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                    |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Deadlocks always crash the application"                 | Deadlocks do NOT throw exceptions. Affected threads silently stop. The JVM continues running. Service appears "live" but does no work.                     |
| "Using ConcurrentHashMap prevents deadlocks"             | Thread-safe data structures prevent data races, not deadlocks. You can still deadlock if you hold a ConcurrentHashMap lock while waiting for another lock. |
| "synchronized is more deadlock-prone than ReentrantLock" | Both can deadlock. ReentrantLock has tryLock() and lockInterruptibly() for recovery options not available with synchronized.                               |
| "Adding more threads fixes deadlock"                     | No. More threads means more chances for deadlock if the root cause (lock inversion) is not fixed. Adding threads may make deadlocks more frequent.         |

---

### 🚨 Failure Modes & Diagnosis

**1. Silent Service Hang (Deadlock in Production)**

**Symptom:** Service stops responding. CPU near 0%. No errors in logs. jstack shows "Found one Java-level deadlock."

**Root Cause:** Two or more threads holding locks in opposite order.

**Diagnostic:**

```bash
# Step 1: Confirm deadlock
jstack -l <pid> | grep -A 50 "Found one Java-level deadlock"

# Step 2: Identify the threads and lock addresses
# Output example:
# "Thread A":
#   waiting to lock monitor 0x00000006c3a0f1a8 (Account@abc123)
#   Locked 0x00000006c3b0c1a0 (Account@def456)
# "Thread B":
#   waiting to lock 0x00000006c3b0c1a0 (Account@def456)
#   Locked 0x00000006c3a0f1a8 (Account@abc123)

# Step 3: Find the class/method from the stack trace
# Identify the offending code
```

**Fix:** Implement lock ordering (sort by `System.identityHashCode()` or domain ID). For immediate recovery: restart the service (deadlock is permanent without external intervention).

**Prevention:** Add `@Scheduled` deadlock detection health check. Code review: any nested locking must enforce global ordering.

---

**2. Intermittent Deadlock (Hard to Reproduce)**

**Symptom:** Service occasionally hangs for 30–60 seconds then recovers (because a thread times out), or service hangs permanently but only under specific load patterns.

**Root Cause:** Deadlock only occurs when two specific operations happen to run concurrently. At low load, they rarely overlap.

**Diagnostic:**

```bash
# Enable detailed lock logging in production:
-Xlog:jdk.jfr.ThreadPark:file=park.log  # Java Flight Recorder
jcmd <pid> JFR.start duration=120s filename=recording.jfr
# Analyze with JMC: look for lock park events exceeding threshold
```

**Fix:** Static analysis: review all code paths that acquire multiple locks, list acquisition order, verify consistency. Any inconsistency = potential deadlock. Use tools like IntelliJ's lock-order analysis or custom static analysis.

**Prevention:** Enforce a documented global lock ordering policy. Any code that acquires multiple locks must document the order and include a comment referencing the policy.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `synchronized` — the Java mechanism that creates BLOCKED state and monitors
- `ReentrantLock` — the alternative that supports tryLock/lockInterruptibly
- `Thread (Java)` — deadlocks affect threads
- `Thread Dump Analysis` — primary diagnostic tool for deadlock investigation

**Builds On This (learn these next):**

- `Lock Striping` — a design pattern that reduces lock contention without risking deadlock
- `Observability & SRE` — deadlock detection as part of production monitoring

**Alternatives / Comparisons:**

- `Lock Striping` — reduces contention; orthogonal to deadlock (can still deadlock with striped locks)
- `STM (Software Transactional Memory)` — eliminates deadlocks entirely but rare in Java production

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Circular wait: each thread holds what the │
│              │ other needs; both wait forever            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Silent service hang — no exception, no    │
│ SOLVES       │ log, no recovery without restart          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Eliminate ONE Coffman condition: enforce  │
│              │ global lock ordering (kill circular wait) │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any code that acquires 2+ locks needs     │
│              │ deadlock prevention analysis              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Can't avoid — but can prevent: lock       │
│              │ ordering + tryLock timeout + health check │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Strict ordering (safe) vs. natural lock   │
│              │ order in business logic (readable)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Each has what the other needs; neither   │
│              │  lets go; service hangs forever."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lock Striping → Actor Model               │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a distributed system with two services, Service A and Service B. Service A uses `synchronized` to hold an in-memory lock while calling Service B via REST. Service B uses `synchronized` to hold its own lock while calling Service A via REST. Can this deadlock? Is it detectable by `ThreadMXBean.findDeadlockedThreads()`? What is the correct architectural solution?

**Q2.** Implement a deadlock-free version of a graph-traversal algorithm that requires acquiring node locks during traversal. The graph is a directed graph where traversal visits neighbours and reads/writes to each node. Nodes have integer IDs. Your solution must: (a) be deadlock-free under concurrent traversal by multiple threads, (b) not acquire more locks than necessary at any time, (c) handle cycles in the graph. Write the lock acquisition strategy (not the full implementation).
