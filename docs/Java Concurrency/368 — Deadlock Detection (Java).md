---
layout: default
title: "Deadlock Detection (Java)"
parent: "Java Concurrency"
nav_order: 368
permalink: /java-concurrency/deadlock-detection-java/
number: "0368"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread, synchronized, ReentrantLock, Lock Ordering, Thread Dump Analysis
used_by: JVM Monitoring, Deadlock Prevention, Production Diagnosis
related: Lock Striping, Thread Dump Analysis, ThreadMXBean, jstack, Livelock
tags:
  - concurrency
  - java
  - deadlock
  - diagnosis
  - advanced
  - debugging
---

# 368 — Deadlock Detection (Java)

⚡ TL;DR — A deadlock occurs when two or more threads each hold a lock the other needs; Java detects them via `ThreadMXBean.findDeadlockedThreads()` and `jstack`, and prevents them through consistent lock ordering, lock timeouts, and try-lock strategies.

| #0368           | Category: Java Concurrency                                               | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread, synchronized, ReentrantLock, Lock Ordering, Thread Dump Analysis |                 |
| **Used by:**    | JVM Monitoring, Deadlock Prevention, Production Diagnosis                |                 |
| **Related:**    | Lock Striping, Thread Dump Analysis, ThreadMXBean, jstack, Livelock      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Thread A acquires lock X, then tries to acquire lock Y. Simultaneously, thread B acquires lock Y, then tries to acquire lock X. Both threads block forever. No exception is thrown. No log line appears. The application silently stops processing affected requests. Without detection mechanisms, the deadlock is invisible until an operator notices zero RPS or a timeout.

**THE BREAKING POINT:**
Deadlocks are the silent killers of concurrent systems. They are deterministic (same code always deadlocks under the same threading order) but timing-dependent (require a specific interleaving to occur). They may happen once a month in production under load, never in dev. Once they occur, the threads never recover — they block indefinitely until the JVM is restarted.

**THE INVENTION MOMENT:**
The JVM exposes thread ownership and dependency information via `ThreadMXBean`. `findDeadlockedThreads()` runs a cycle detection algorithm on the waits-for graph of all locks in the JVM. `jstack` reports found deadlocks at the end of its output with "Found one Java-level deadlock." This allows dead-lock detection at runtime without stopping the JVM — enabling automated monitoring that triggers alerts before manual observation would notice.

---

### 📘 Textbook Definition

A **deadlock** in Java occurs when two or more threads form a cycle in the lock dependency graph: each thread holds one or more locks and waits indefinitely for a lock held by another thread in the cycle. The four Coffman conditions for deadlock: (1) **Mutual Exclusion** — locks can't be shared; (2) **Hold and Wait** — thread holds locks while waiting for more; (3) **No Preemption** — locks aren't forcibly taken; (4) **Circular Wait** — cycle in waits-for graph. Java detection: `ThreadMXBean.findDeadlockedThreads()` (covers `synchronized` + `java.util.concurrent` locks); `ThreadMXBean.findMonitorDeadlockedThreads()` (only `synchronized`). Prevention: lock ordering (always acquire locks in same global order); `tryLock()` with timeout (ReentrantLock); lock-free data structures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A deadlock is two threads each waiting for the other's lock — neither can proceed, both wait forever.

**One analogy:**

> Two polite drivers arrive at a one-lane bridge from opposite sides simultaneously. Driver A says, "You go first." Driver B says, "No, after you." Both are waiting for the other to move. Neither will ever cross. They each hold their half of the bridge (lock) and wait for the other's half — forever. A deadlock.

**One insight:**
Deadlocks in Java always involve a **lock cycle**. You can never deadlock with a single lock. You need at least two locks and at least two threads, each holding one lock and requesting the other. The fix is always the same: break the cycle by ensuring all threads acquire locks in the same global order.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A deadlock requires all 4 Coffman conditions simultaneously.
2. Deadlock involves ≥2 threads and ≥2 locks.
3. A deadlock cycle in the waits-for graph has no resolution — threads block indefinitely.
4. JVM cannot automatically break deadlocks (unlike database locks which have timeout/rollback).
5. `ThreadMXBean.findDeadlockedThreads()` returns all thread IDs in deadlock cycles.

**DERIVED DESIGN — THE CLASSIC PATTERN:**

```java
// DEADLOCK: acquire locks in opposite order
Object lockA = new Object();
Object lockB = new Object();

// Thread 1:
synchronized (lockA) {          // ← acquires lockA
    Thread.sleep(50);
    synchronized (lockB) {      // ← waits for lockB
        // never reaches here if Thread 2 runs concurrently
    }
}

// Thread 2 (concurrent):
synchronized (lockB) {          // ← acquires lockB
    Thread.sleep(50);
    synchronized (lockA) {      // ← waits for lockA
        // never reaches here   ← DEADLOCK!
    }
}
```

```
WAITS-FOR GRAPH (deadlock cycle):
Thread 1 ──holds──► lockA
Thread 1 ──wants──► lockB ──held by──► Thread 2
Thread 2 ──holds──► lockB
Thread 2 ──wants──► lockA ──held by──► Thread 1
              ↑_______cycle________↑
```

**PREVENTION STRATEGIES:**

```
Strategy 1: LOCK ORDERING (most reliable)
  Assign a global numeric order to all locks.
  Always acquire in ascending order.
  Thread 1: acquire lockA (order 1) → acquire lockB (order 2)
  Thread 2: acquire lockA (order 1) → acquire lockB (order 2)
  → Both threads request in same order → no cycle → no deadlock

Strategy 2: TRY-LOCK WITH TIMEOUT (ReentrantLock only)
  if (lockA.tryLock(100, MILLISECONDS)) {
    try {
      if (lockB.tryLock(100, MILLISECONDS)) {
        try { doWork(); } finally { lockB.unlock(); }
      } else {
        // Failed to get lockB — release lockA & retry
      }
    } finally { lockA.unlock(); }
  }
  → Never blocks indefinitely → deadlock impossible

Strategy 3: LOCK-FREE DATA STRUCTURES
  Use ConcurrentHashMap, AtomicReference, etc.
  → No explicit locks → no deadlock possible
```

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce app has `AccountService` and `OrderService`. Both have `synchronized` methods. A transfer operation: `AccountService.debit()` calls `OrderService.confirm()` (acquires OrderService lock after AccountService lock). Simultaneously, `OrderService.cancel()` calls `AccountService.credit()` (acquires AccountService lock after OrderService lock).

**WITHOUT deadlock prevention:**
Under load, exactly the wrong interleaving occurs: thread A acquires AccountService lock, thread B acquires OrderService lock. Thread A waits for OrderService lock, thread B waits for AccountService lock. Both wait forever. Payment processing stops. No logs, no errors.

**WITH lock ordering:**
Assign numeric IDs: AccountService=1, OrderService=2. Policy: always acquire in ascending ID order.

- `debit+confirm`: acquire AccountService (1) first, then OrderService (2).
- `cancel+credit`: must ALSO acquire AccountService (1) first, then OrderService (2).
- `cancel()` refactored: before calling `credit()`, acquire AccountService lock first.
- Now both operations acquire locks in same order → cycle is impossible.

**THE INSIGHT:**
Deadlock prevention is always architectural. No amount of retry logic prevents deadlocks — only consistent lock ordering or lock-free design does.

---

### 🧠 Mental Model / Analogy

> Deadlock detection is like a traffic air-traffic controller watching planes hold and wait for each other's runway. The controller runs a cycle check: if plane A is holding runway 1 waiting for runway 2, and plane B is holding runway 2 waiting for runway 1 — that's a cycle — reported immediately. Prevention is like the ATC rule "always request runways in alphabetical order" — so both planes always request runway 1 before runway 2 and no cycle can form.

- "Runway" → lock
- "Plane holding runway" → thread holding lock
- "Waiting for runway" → thread blocking on lock
- "ATC cycle check" → `ThreadMXBean.findDeadlockedThreads()`
- "Request in alphabetical order" → global lock ordering policy

Where this analogy breaks down: unlike real aircraft, Java threads don't have an ATC forcing them to follow ordering — the developer must enforce the ordering discipline in code.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A deadlock is when two threads each hold a key the other needs, and both are waiting forever. Java can detect this automatically and tell you exactly which threads and locks are involved.

**Level 2 — How to use it (junior developer):**
Detect with: `jstack <pid>` (look for "Found one Java-level deadlock" at the bottom), or `ThreadMXBean.findDeadlockedThreads()` programmatically. Prevent with: rule "always acquire locks in the same order" across your codebase. For `ReentrantLock`, use `tryLock(timeout)` to avoid blocking forever.

**Level 3 — How it works (mid-level engineer):**
The JVM maintains a per-thread "waiting for lock" reference. `findDeadlockedThreads()` builds the waits-for graph from all threads' lock ownership and wait relationships, then runs cycle detection (DFS). It checks both `synchronized` monitors (stored in object mark words) and `AbstractQueuedSynchronizer`-based locks (ReentrantLock, Semaphore etc.) — the AQS maintains a queue of waiting threads that the MXBean can inspect. Detection is O(threads × locks) — fast for normal applications.

**Level 4 — Why it was designed this way (senior/staff):**
Java (unlike databases) has no deadlock recovery mechanism because JVM thread state is not transactional. A database can roll back a transaction to break a deadlock — the state is recoverable. A Java thread holds arbitrary mutable state that may be partially updated; rolling back a thread's side effects is impossible in general. The JVM's design decision: detect deadlocks, report them, but leave resolution to the developer (via restart or kill). The practical implication: prevention is far more important than detection. Detection is useful for diagnosis but not for runtime recovery.

---

### ⚙️ How It Works (Mechanism)

```java
// PROGRAMMATIC DEADLOCK DETECTION + MONITORING

import java.lang.management.*;
import java.util.concurrent.*;

// Automated deadlock monitor (run periodically in production)
public class DeadlockMonitor {

    private final ThreadMXBean mxBean =
        ManagementFactory.getThreadMXBean();

    // Call every 30 seconds via ScheduledExecutorService
    public void checkForDeadlocks() {
        // findDeadlockedThreads: covers synchronized AND j.u.c. locks
        // findMonitorDeadlockedThreads: synchronized only
        long[] deadlockedThreadIds = mxBean.findDeadlockedThreads();

        if (deadlockedThreadIds != null) {
            // Get full thread info including stack traces and monitors
            ThreadInfo[] threadInfos = mxBean.getThreadInfo(
                deadlockedThreadIds,
                true,  // include locked monitors
                true   // include locked synchronizers
            );

            StringBuilder report = new StringBuilder(
                "DEADLOCK DETECTED — threads involved:\n");

            for (ThreadInfo ti : threadInfos) {
                report.append(String.format(
                    "  Thread: %s [id=%d] state=%s\n",
                    ti.getThreadName(), ti.getThreadId(),
                    ti.getThreadState()));
                report.append(String.format(
                    "  Waiting for lock: %s\n",
                    ti.getLockInfo()));
                report.append(String.format(
                    "  Lock held by: %s\n",
                    ti.getLockOwnerName()));
                for (StackTraceElement ste : ti.getStackTrace()) {
                    report.append("    at ").append(ste).append("\n");
                }
            }

            log.error(report.toString());
            // Alert via PagerDuty/Slack here
        }
    }
}

// PREVENTION: Lock ordering with System.identityHashCode
void transferWithOrdering(Account from, Account to, int amount) {
    // Order locks by identity hash code — consistent global order
    Object first  = System.identityHashCode(from) <
                    System.identityHashCode(to) ? from : to;
    Object second = first == from ? to : from;

    synchronized (first) {
        synchronized (second) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}

// PREVENTION: tryLock with timeout (ReentrantLock)
boolean transfer(Account from, Account to, int amount)
        throws InterruptedException {
    while (true) {
        if (from.lock.tryLock(50, MILLISECONDS)) {
            try {
                if (to.lock.tryLock(50, MILLISECONDS)) {
                    try {
                        from.debit(amount);
                        to.credit(amount);
                        return true;
                    } finally { to.lock.unlock(); }
                }
            } finally { from.lock.unlock(); }
        }
        // Both tries failed: back off and retry
        Thread.sleep(ThreadLocalRandom.current().nextInt(10));
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
DETECTION FLOW:
JVM maintains waits-for graph:
  thread.waitingForLock → lock.heldByThread

findDeadlockedThreads() runs cycle detection:
  For each thread T:
    Follow T → lock → holder → lock → holder → ...
    If we return to T: CYCLE FOUND
  [Deadlock Detection ← YOU ARE HERE]

JVM returns array of deadlocked thread IDs
  → Application logs thread info with stack traces
  → Monitoring system alerts on-call engineer
  → Engineer captures thread dump for full analysis
  → Root cause: lock ordering violation in ServiceA.method()
  → Fix: enforce global lock order (ServiceA=1, ServiceB=2)
  → Deploy → no more deadlocks

FAILURE PATH (detection missed):
ReentrantLock deadlock NOT caught by
findMonitorDeadlockedThreads() (only synchronized)
→ Must use findDeadlockedThreads() (covers j.u.c. too)
→ Or observe: threads permanently in WAITING state,
  "parking to wait for" same lock addresses

WHAT CHANGES AT SCALE:
More services = more shared locks = higher deadlock probability.
At microservice scale: distributed deadlocks (service A waits for
service B which waits for service A) are not detectable by JVM
MXBean — require distributed tracing and timeout-based detection.
```

---

### 💻 Code Example

```java
// THE CLASSIC DEADLOCK — DON'T DO THIS
class BankAccount {
    private final ReentrantLock lock = new ReentrantLock();
    private int balance;

    // BAD: locks in caller-determined order = potential deadlock
    public static void transferBad(BankAccount from,
                                   BankAccount to, int amount) {
        synchronized (from) {           // acquire 'from' lock first
            synchronized (to) {         // then 'to' lock
                from.balance -= amount;
                to.balance   += amount;
            }
        }
        // If two threads call transferBad(A,B) and transferBad(B,A)
        // concurrently → DEADLOCK
    }

    // GOOD: consistent lock ordering via identity hash code
    public static void transferSafe(BankAccount a,
                                    BankAccount b, int amount) {
        BankAccount first  = System.identityHashCode(a) <=
                             System.identityHashCode(b) ? a : b;
        BankAccount second = first == a ? b : a;
        synchronized (first) {
            synchronized (second) {
                a.balance -= amount;    // always a→b regardless
                b.balance += amount;   // of which is first/second
            }
        }
        // Same lock order guaranteed for any (a,b) pair → no cycle
    }

    // GOOD: ReentrantLock tryLock — never blocks indefinitely
    public static boolean tryTransfer(BankAccount from,
                                      BankAccount to, int amount)
            throws InterruptedException {
        if (from.lock.tryLock(100, TimeUnit.MILLISECONDS)) {
            try {
                if (to.lock.tryLock(100, TimeUnit.MILLISECONDS)) {
                    try {
                        from.balance -= amount;
                        to.balance   += amount;
                        return true;
                    } finally { to.lock.unlock(); }
                }
            } finally { from.lock.unlock(); }
        }
        return false; // caller can retry or report failure
    }
}
```

---

### ⚖️ Comparison Table

| Strategy                   | Deadlock Risk | Complexity | Failure Mode                               |
| -------------------------- | ------------- | ---------- | ------------------------------------------ |
| Lock ordering (consistent) | Zero          | Low        | Requires discipline across all code        |
| tryLock with timeout       | Zero          | Medium     | Must handle "failed to acquire" case       |
| Lock-free (Atomic/CAS)     | Zero          | High       | Livelock possible under extreme contention |
| Detection only (MXBean)    | Present       | Low        | Can detect but not prevent/recover         |

**How to choose:** Prefer lock ordering for any code with multiple acquired locks. Use tryLock for external/untrusted lock chains. Use lock-free structures where performance is critical and mutation patterns are simple.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `findMonitorDeadlockedThreads()` catches all deadlocks | It only detects deadlocks involving `synchronized` monitors. For `ReentrantLock`, `ReadWriteLock`, etc., use `findDeadlockedThreads()` which covers both                               |
| Increasing timeouts prevents deadlocks                 | Timeouts on individual operations (HTTP calls, DB queries) do NOT prevent lock deadlocks. Timeouts on `tryLock()` DO prevent lock deadlocks. These are different things                |
| A livelock is the same as a deadlock                   | A livelock: threads keep retrying but make no progress (not blocked — they're RUNNABLE). A deadlock: threads are BLOCKED forever. Livelocks are harder to detect because CPU is active |
| Deadlocks only happen with synchronized blocks         | Deadlocks happen with any mutual-exclusion mechanism: `synchronized`, `ReentrantLock`, database row locks, file locks, semaphores                                                      |

---

### 🚨 Failure Modes & Diagnosis

**Deadlock Between Service-Layer Objects (synchronized methods)**

**Symptom:** Subset of requests hang indefinitely; no exceptions thrown; thread count stable; CPU ~0%.

**Root Cause:** Two `synchronized` methods in different service classes call each other under contention, acquiring locks in opposite order.

**Diagnostic Command:**

```bash
# Immediate detection:
jstack <pid> | grep -A 30 "Found.*deadlock"

# Or programmatic:
long[] ids = ManagementFactory.getThreadMXBean()
    .findDeadlockedThreads();
System.out.println("Deadlocked threads: " + Arrays.toString(ids));
```

**Fix:** Apply global lock ordering. Alternatively, refactor to eliminate cross-service synchronized calls — introduce a single coordinating lock or use message-passing.

**Prevention:** Code review rule: no `synchronized` call across two different service/component boundaries without explicit lock ordering documentation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `synchronized` — Java's intrinsic lock mechanism; most deadlocks involve synchronized blocks
- `ReentrantLock` — explicit lock with `tryLock()` for deadlock prevention
- `Thread States` — BLOCKED state is the observable symptom of deadlock

**Builds On This (learn these next):**

- `Lock Striping` — reduces lock scope, reducing probability of deadlock
- `Thread Dump Analysis` — the primary tool for diagnosing deadlocks in production

**Alternatives / Comparisons:**

- `Livelock` — threads not blocked but making no progress; similar symptom, different mechanism
- `Starvation` — thread never gets lock due to unfair scheduler, not a cycle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Deadlock: cycle in waits-for lock graph;  │
│              │ all threads in cycle blocked forever      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Silent application hangs with no errors   │
│ SOLVES       │ or logs; only diagnosis reveals the cause │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Break cycle: acquire ALL locks in the     │
│              │ same global order in ALL code paths       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ App hangs, CPU~0%, threads BLOCKED —      │
│              │ run jstack / findDeadlockedThreads()      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Not about preventing: always prevent.     │
│              │ Detection is for diagnosis only           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lock ordering is free; tryLock adds retry │
│              │ complexity; lock-free adds CAS complexity │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two threads, each holding the key the    │
│              │  other needs — waiting forever"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lock Striping → Thread Dump Analysis →    │
│              │ Livelock                                  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `ThreadMXBean.findDeadlockedThreads()` detects deadlocks involving `java.util.concurrent` locks like `ReentrantLock`. Explain how this is technically possible: `ReentrantLock` is implemented in pure Java using `AbstractQueuedSynchronizer`. What information does the AQS maintain that the MXBean can query to build the waits-for graph — and why does this work for `ReentrantLock` but not for custom user-coded blocking mechanisms like a `boolean locked = true; while(locked) Thread.yield()` spin-wait?

**Q2.** The `System.identityHashCode()`-based lock ordering strategy prevents deadlocks for locks on two objects. But there's a rare corner case: two objects can have the same `identityHashCode()` (hash collision). What happens to the locking strategy in that case, and how does it need to handle this collision to remain deadlock-free while still being thread-safe?
