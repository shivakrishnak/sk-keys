---
layout: default
title: "Deadlock"
parent: "Operating Systems"
nav_order: 118
permalink: /operating-systems/deadlock/
number: "0118"
category: Operating Systems
difficulty: ★★☆
depends_on: Mutex, Thread, Condition Variable
used_by: Database Transaction Management, OS Resource Scheduling, Distributed Systems
related: Livelock, Starvation, Resource Allocation Graph, Banker's Algorithm
tags:
  - os
  - concurrency
  - synchronization
  - fundamentals
---

# 118 — Deadlock

⚡ TL;DR — Deadlock is when two or more threads each hold a resource the other needs, forming a cycle of waiting — none can proceed.

| #0118 | Category: Operating Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Mutex, Thread, Condition Variable | |
| **Used by:** | Database Transaction Management, OS Resource Scheduling, Distributed Systems | |
| **Related:** | Livelock, Starvation, Resource Allocation Graph, Banker's Algorithm | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Thread A holds Lock 1, Thread B holds Lock 2. Thread A requests Lock 2 (blocked). Thread B requests Lock 1 (blocked). Neither can proceed. The program hangs silently — no exception, no error, no output. In production, this causes a service to stop responding completely, typically requiring a restart.

THE BREAKING POINT:
Deadlock is particularly dangerous because: (1) it's non-deterministic (depends on thread scheduling timing), (2) it may happen only under load (higher concurrency increases probability), (3) it produces no diagnostic output by default, (4) in distributed systems, it can involve processes across machines, making it even harder to detect.

THE INVENTION MOMENT:
Dijkstra identified and formalised deadlock conditions in the 1960s. The four Coffman conditions (1971) provide the definitive model. Detection, prevention, and avoidance algorithms (Banker's algorithm, lock ordering, timeout-based breaking) are all responses to these conditions.

### 📘 Textbook Definition

**Deadlock** is a situation in which two or more threads (or processes) are permanently blocked, each waiting for a resource held by another thread in the cycle. Deadlock requires all four **Coffman conditions** simultaneously:
1. **Mutual Exclusion**: at least one resource is held in a non-shareable mode.
2. **Hold and Wait**: a thread holds at least one resource while waiting to acquire another.
3. **No Preemption**: resources cannot be forcibly taken from a thread; only voluntary release.
4. **Circular Wait**: a circular chain of threads exists, each waiting for a resource held by the next.

Breaking any single Coffman condition prevents deadlock.

### ⏱️ Understand It in 30 Seconds

**One line:**
Deadlock = circular wait where everyone holds what others need and no one will release first.

**One analogy:**
> Two cars on a one-lane bridge from opposite ends, each refusing to back up. Neither can proceed. Neither reverses. They wait forever. Removing any condition breaks the deadlock: allow one car to reverse (no "no preemption"), build a two-lane bridge ("mutual exclusion" broken), or enforce a rule that cars enter only from the north end (lock ordering — "circular wait" broken).

**One insight:**
The simplest and most practical prevention strategy is **consistent lock ordering**: always acquire Lock A before Lock B, across all threads. If no thread ever holds B while waiting for A (and vice versa), circular wait is impossible.

### 🔩 First Principles Explanation

CORE INVARIANTS (Coffman Conditions):
1. Mutual exclusion: at least one resource must be held exclusively — cannot be shared.
2. Hold and Wait: thread holds resources while waiting for more — releases nothing.
3. No preemption: resources cannot be taken away — only voluntarily released.
4. Circular wait: T1 waits for T2, T2 waits for T3, ..., Tn waits for T1.

PREVENTION STRATEGIES (break one condition):
- Break mutual exclusion: use lock-free data structures (not always possible).
- Break hold-and-wait: acquire all needed resources atomically or release all and retry.
- Break no preemption: use `tryLock(timeout)` — if timeout expires, release all held locks.
- Break circular wait: **lock ordering** — define a global order; always acquire locks in that order.

DETECTION STRATEGIES (allow, then detect):
- Build a Resource Allocation Graph (RAG): nodes are threads and resources; edges are "holds" and "waits-for". A cycle in the RAG = deadlock.
- Database engines detect transaction deadlocks by maintaining a wait-for graph and periodically checking for cycles.

THE TRADE-OFFS:
Prevention (lock ordering): simple and effective but requires discipline across the entire codebase. Detection + recovery: allows higher concurrency but requires victim selection and transaction rollback. Avoidance (Banker's algorithm): guarantees no deadlock but requires knowing maximum resource needs in advance — not practical for most software.

### 🧪 Thought Experiment

CLASSIC DEADLOCK:
```java
ReentrantLock lockA = new ReentrantLock();
ReentrantLock lockB = new ReentrantLock();

// Thread 1: acquires A then B
lockA.lock();
// [scheduler switches to Thread 2]
lockB.lock();  // Thread 1 blocks here (B held by Thread 2)

// Thread 2: acquires B then A
lockB.lock();
lockA.lock();  // Thread 2 blocks here (A held by Thread 1)

// Result: Thread 1 holds A, waits for B
//         Thread 2 holds B, waits for A
//         Neither proceeds → DEADLOCK
```

FIX (consistent lock ordering):
```java
// BOTH threads always acquire lockA before lockB
Thread 1: lockA.lock() → lockB.lock() → ... → unlock both
Thread 2: lockA.lock() → lockB.lock() → ... → unlock both
// Thread 2 will block on lockA until Thread 1 releases it
// Thread 1 can always proceed without waiting for B
// No circular wait possible
```

THE INSIGHT:
The deadlock arose solely from inconsistent acquisition order. The fix requires no algorithm, no timeouts — just a convention enforced by code review and static analysis.

### 🧠 Mental Model / Analogy

> Four cars at a 4-way intersection (Coffman conditions mapped):
> 1. Mutual exclusion: each lane can only be used by one car at a time.
> 2. Hold and Wait: each car occupies one lane and wants another.
> 3. No preemption: no car backs up (no preemption allowed).
> 4. Circular wait: each car is blocked by the car to its right.
>
> Fix 4 (circular wait): traffic rule — always yield to your left. One direction of yielding breaks the cycle. Same as lock ordering.

Where the analogy breaks down: in a real 4-way intersection, deadlock is rare because humans will eventually back up (preemption). In software, threads don't give up unless coded to do so (`tryLock()` with timeout).

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Deadlock is when two (or more) threads are stuck waiting for each other forever. Thread 1 needs what Thread 2 has. Thread 2 needs what Thread 1 has. Neither releases what it holds. Everyone waits. Nothing moves.

**Level 2 — How to use it (junior developer):**
Prevention rules: (1) always acquire multiple locks in the same order in all threads. (2) Use `tryLock(timeout)` instead of `lock()` when acquiring multiple locks; if tryLock fails, release all held locks and retry. (3) Minimise lock scope — hold locks for the shortest possible time. (4) Use higher-level abstractions (BlockingQueue, concurrent collections) that manage locking internally. Tools: `jstack <PID>` detects Java deadlocks automatically.

**Level 3 — How it works (mid-level engineer):**
JVM deadlock detection: `jstack` uses JVM's built-in deadlock detector that tracks the lock acquisition graph for `synchronized` and `ReentrantLock`. It reports: "Found one Java-level deadlock" with full thread stacks and lock information. For distributed deadlock (two services each holding a database row locked by the other's transaction), detection requires a distributed wait-for graph or timeouts. Databases (MySQL InnoDB, PostgreSQL) detect deadlocks via wait-for graph cycle detection on a background thread (runs every ~0.1s). On detection: choose a victim (rollback smaller transaction), unblock the other.

**Level 4 — Why it was designed this way (senior/staff):**
Database deadlock detection was chosen over prevention because database transactions don't know in advance which rows they'll access — prevention via lock ordering would require acquiring all locks before starting a transaction, which would drastically reduce concurrency. Detection + rollback trades some overhead (cycle detection every 0.1s, occasional rollback) for maximum concurrency. OS-level deadlock prevention (Banker's algorithm) is theoretically sound but practically unusable in general OS contexts because: (a) processes don't declare maximum resource needs, (b) resource types are diverse (files, sockets, memory, semaphores). Most OS deadlock "prevention" is actually "ignore it" — the assumption that deadlock is rare and can be resolved by killing a process or rebooting.

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              RESOURCE ALLOCATION GRAPH                 │
├────────────────────────────────────────────────────────┤
│  Threads: T1, T2     Resources: R1(lockA), R2(lockB)   │
│                                                        │
│  T1 holds R1:   T1 → R1  (assignment edge)             │
│  T2 holds R2:   T2 → R2  (assignment edge)             │
│  T1 waits R2:   R2 → T1  (request edge)                │
│  T2 waits R1:   R1 → T2  (request edge)                │
│                                                        │
│  Cycle: T1 → R2 → T2 → R1 → T1  ← DEADLOCK            │
│                                                        │
│  If no cycle in RAG: no deadlock                       │
│  If cycle in RAG: deadlock (single-instance resources) │
└────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

MYSQL INNODB DEADLOCK DETECTION:
```
T1: BEGIN; UPDATE accounts SET balance=... WHERE id=1; (holds row 1 lock)
T2: BEGIN; UPDATE accounts SET balance=... WHERE id=2; (holds row 2 lock)
T1: UPDATE accounts SET balance=... WHERE id=2; → WAITS for row 2
T2: UPDATE accounts SET balance=... WHERE id=1; → WAITS for row 1

InnoDB background thread (every 0.1s):
  Build wait-for graph: T1 → T2 → T1 (cycle detected)
  Select victim (smaller transaction = T2)
  Rollback T2: release row 2 lock
  T1: unblocked → acquires row 2 → completes

T2 application receives: "ERROR 1213: Deadlock found when trying to get lock"
Application: retry T2 transaction → succeeds
```

FAILURE PATH (distributed deadlock — no detection):
```
Service A: acquires lock for User 1's account (database)
Service B: acquires lock for User 2's account (database)
Service A: requests User 2's lock → blocked
Service B: requests User 1's lock → blocked
Result: both services hang; no database-level detection
         (two separate database connections, no shared wait graph)
Fix: timeout + retry; or distributed lock manager; or order requests
```

### 💻 Code Example

Example 1 — Classic deadlock + prevention:
```java
// DEADLOCK PRONE — inconsistent lock order
class TransferService {
    void transfer(Account from, Account to, double amount) {
        synchronized (from) {      // acquires 'from' first
            synchronized (to) {    // acquires 'to' second
                // ... transfer
            }
        }
    }
}
// Thread 1: transfer(A→B) → acquires A, wants B
// Thread 2: transfer(B→A) → acquires B, wants A → DEADLOCK

// DEADLOCK SAFE — consistent lock ordering by identity
class SafeTransferService {
    void transfer(Account from, Account to, double amount) {
        // Lock in consistent order (lower id first)
        Account first  = from.id < to.id ? from : to;
        Account second = from.id < to.id ? to : from;
        synchronized (first) {
            synchronized (second) {
                // ... transfer
            }
        }
    }
}
```

Example 2 — tryLock with timeout (breaks "hold and wait"):
```java
// Acquire both locks or release and retry
ReentrantLock lockA = new ReentrantLock();
ReentrantLock lockB = new ReentrantLock();

boolean acquireBothLocks(long timeoutMs) throws InterruptedException {
    long deadline = System.nanoTime() + timeoutMs * 1_000_000;
    while (System.nanoTime() < deadline) {
        if (lockA.tryLock(10, TimeUnit.MILLISECONDS)) {
            try {
                if (lockB.tryLock(10, TimeUnit.MILLISECONDS)) {
                    return true;  // both acquired
                }
                // Failed to get B — release A and retry
            } finally {
                if (!lockB.isHeldByCurrentThread()) lockA.unlock();
            }
        }
        Thread.sleep(1 + (long)(Math.random() * 5));  // random backoff
    }
    return false;
}
```

Example 3 — jstack deadlock diagnosis:
```bash
# Java: detect deadlock in running JVM
jstack <PID>
# Output example:
# Found one Java-level deadlock:
# =============================
# "Thread-1":
#   waiting to lock monitor 0x... (lockA, held by "Thread-0")
# "Thread-0":
#   waiting to lock monitor 0x... (lockB, held by "Thread-1")
# 
# Java stack information for the threads listed above:
# Thread-0:
#   at TransferService.transfer(TransferService.java:7)
#   - waiting to lock <0x...> (lockB)
#   - locked <0x...> (lockA)
# Thread-1:
#   at TransferService.transfer(TransferService.java:7)
#   - waiting to lock <0x...> (lockA)
#   - locked <0x...> (lockB)

# Detect with deadlock detection thread:
ThreadMXBean tmx = ManagementFactory.getThreadMXBean();
long[] deadlockedIds = tmx.findDeadlockedThreads();  // null if none
```

### ⚖️ Comparison Table

| Condition | Prevention | Detection | Cost |
|---|---|---|---|
| **Mutual exclusion** | Lock-free data structures | Hard to detect | High (refactoring) |
| **Hold and wait** | tryLock + release all | N/A | Medium (retry logic) |
| **No preemption** | tryLock timeout | N/A | Low (add timeout) |
| **Circular wait** | Lock ordering | RAG cycle detection | Low (convention) |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Deadlock throws an exception" | No — threads silently block forever; no exception, no error |
| "Lock-free code can't deadlock" | Lock-free code cannot deadlock by definition (no locks to cycle on); but it can livelock |
| "ReentrantLock deadlock is detected by JVM" | jstack detects both synchronized and ReentrantLock deadlocks |
| "Deadlock only involves two threads" | Any cycle works: T1→T2→T3→T1 is a three-thread deadlock |
| "Increasing thread count fixes deadlock" | More threads increases deadlock probability by increasing concurrent lock acquisition |

### 🚨 Failure Modes & Diagnosis

**1. Production Service Hangs (No Response)**

Symptom: Service stops responding; health checks fail; all threads BLOCKED; CPU usage drops to zero.

Root Cause: Deadlock in request-handling threads; all handlers blocked waiting for locks in a cycle.

Diagnostic:
```bash
# Java: generate thread dump
kill -3 <PID>  # sends SIGQUIT → JVM dumps threads to stderr
# Or: jstack <PID> | grep -A 20 "deadlock"

# Linux: show all thread states
cat /proc/<PID>/task/*/status | grep State
```

Fix: Identify the deadlocking threads from jstack output; fix lock ordering in source code.

Prevention: Add a deadlock monitoring thread in production that calls `tmx.findDeadlockedThreads()` every 30 seconds and alerts.

---

**2. Database Deadlock Spike Under Load**

Symptom: "Deadlock found" errors spike during peak traffic; transaction retry rate increases; P99 latency spikes.

Root Cause: Hot rows accessed in different order by concurrent transactions.

Diagnostic:
```sql
-- MySQL: last deadlock info
SHOW ENGINE INNODB STATUS\G
-- Section "LATEST DETECTED DEADLOCK" shows the transactions and locks

-- PostgreSQL: lock waits
SELECT * FROM pg_locks WHERE NOT granted;
```

Fix: Ensure all transactions accessing the same rows do so in consistent order; use `SELECT ... FOR UPDATE` in the same order across transactions.

Prevention: Test with concurrent load using `pgbench` (PostgreSQL) or `sysbench` (MySQL) before production.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Mutex` — deadlock requires mutually exclusive locks; understand mutex first
- `Thread` — deadlock is a multi-thread phenomenon
- `Condition Variable` — incorrect condition variable usage (missing notify) can cause deadlock

**Builds On This (learn these next):**
- `Livelock` — threads are active but stuck in a retrying loop; not truly blocked like deadlock
- `Starvation` — a thread never acquires resources despite not being in a deadlock cycle
- `Distributed Systems consensus` — distributed deadlock (across services) requires distributed detection

**Alternatives / Comparisons:**
- `Livelock` — threads active but stuck looping (e.g., two people walking toward each other, both step aside to the same side, repeat)
- `Starvation` — one thread never runs; not a mutual cycle but unfair scheduling

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Circular wait where each thread holds    │
│              │ what others need; nothing can proceed    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Silent program hang; no exception;       │
│ SOLVES       │ requires restart to recover              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Break any Coffman condition to prevent;  │
│              │ lock ordering (break #4) is simplest     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing hangs; designing concurrent   │
│              │ code with multiple locks                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ "Avoid" = prevent: use lock ordering,    │
│              │ tryLock timeout, or lock-free design     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Prevention (ordering) vs detection +     │
│              │ rollback (database style)                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Everyone waits for everyone else —      │
│              │  break the cycle with lock ordering"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Livelock → Starvation → Distributed Locks │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** Dijkstra's Banker's Algorithm is a deadlock avoidance algorithm: before granting a resource request, the OS simulates a hypothetical future where all running processes request their maximum resources and checks whether a "safe state" (all can complete) exists. If not, the request is delayed. This algorithm is used in virtually zero production operating systems. Explain why: what are the three practical requirements of Banker's Algorithm that make it unworkable in a general-purpose OS, and what simpler mechanism do real OSes use to handle resource exhaustion?

**Q2.** Consider a microservices architecture where Service A holds a distributed lock on "user-123" (via Redis SETNX) and calls Service B, which needs to acquire a lock on "user-456". Simultaneously, Service B holds "user-456" and calls Service A, which needs "user-123". This is a distributed deadlock — neither service is blocked in the traditional sense (they're making network calls), but neither can proceed. Redis's SETNX with TTL would eventually break the cycle (via TTL expiry). Design a deterministic deadlock prevention strategy for this microservices case that: (a) doesn't rely on timeout/TTL, (b) scales to 100K distinct resource IDs, and (c) handles the case where lock acquisition order is determined by runtime data (user ID pairs that arrive in any order).
