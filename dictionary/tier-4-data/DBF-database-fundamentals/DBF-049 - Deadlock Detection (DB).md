---
version: 2
layout: default
title: "Deadlock Detection (DB)"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /databases/deadlock-detection/
id: DBF-056
category: Database Fundamentals
difficulty: ★★★
depends_on: Locking, Transaction, Isolation Levels
used_by: Optimistic vs Pessimistic Locking, Connection Pooling
related: Locking, MVCC, Isolation Levels
tags:
  - database
  - concurrency
  - transactions
  - deep-dive
---

# DBF-053 - Deadlock Detection (DB)

⚡ TL;DR - A deadlock is a circular lock wait between two or more transactions; databases detect it via a wait-for graph cycle, pick a "victim" transaction to abort, and require the application to retry.

| #435            | Category: Database Fundamentals                       | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Locking, Transaction, Isolation Levels                |                 |
| **Used by:**    | Optimistic vs Pessimistic Locking, Connection Pooling |                 |
| **Related:**    | Locking, MVCC, Isolation Levels                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Transaction 1 holds a lock on Row A, waiting for Row B. Transaction 2 holds a lock on Row B, waiting for Row A. Neither can proceed. Both wait forever. The database connection pool fills with stuck connections. The application hangs.

**THE BREAKING POINT:**
Without deadlock detection, deadlocked transactions would wait forever (or until a lock wait timeout fires - possibly 50 seconds later). During that window, every new request for those rows also queues up. Eventually: application-level timeout cascade, all connections consumed, service outage.

**THE INVENTION MOMENT:**
"Periodically scan the lock wait graph. If there's a cycle, break it by aborting the cheapest transaction to abort."

---

### 📘 Textbook Definition

A **deadlock** occurs when two or more transactions are each waiting for a lock held by the other, forming a circular wait. Database **deadlock detection** builds a **wait-for graph** (directed graph where an edge from T1 → T2 means T1 is waiting for a lock held by T2). A deadlock exists if and only if this graph contains a **cycle**. Detection runs periodically (or continuously) - when a cycle is detected, the database selects a **victim transaction** (typically the one with the least work done, fewest locks held, or a configurable weight), aborts it (rolling back its changes), and returns an error to that transaction's caller. The application is responsible for detecting the deadlock error and retrying the aborted transaction.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A deadlock is two transactions each waiting for the other's lock - the database detects the cycle by analyzing the wait graph and kills the cheaper transaction to resolve it.

**One analogy:**

> Two cars at a single-lane bridge from opposite ends. Car A is on the bridge, waiting for Car B to back off. Car B is on the bridge, waiting for Car A to back off. Neither backs off - forever. A traffic officer (the database) arrives, detects the standstill, and tells one car (the victim) to reverse (transaction abort + retry). The road is clear. The other car (the winner) proceeds. The reversed car (retry) re-enters the queue.

**One insight:**
Deadlocks are a normal, expected occurrence in concurrent database systems - not a sign of a broken database or catastrophically broken application code. The correct application response is retry. The problem is writing code that detects `CannotAcquireLockException` (Spring) or MySQL error 1213 and transparently retries, with exponential backoff.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS - Coffman Conditions (all 4 required for deadlock):**

1. **Mutual exclusion:** Locks are exclusive - only one holder at a time.
2. **Hold and wait:** A transaction holds locks AND waits for more.
3. **No preemption:** The database won't forcibly take a lock away from a transaction (except deadlock victim selection).
4. **Circular wait:** A cycle exists in the wait-for graph.

Breaking any condition prevents deadlocks:

- Break mutual exclusion → MVCC (readers don't lock) - handles read-write but not write-write.
- Break hold and wait → Acquire all locks at once at transaction start - impractical for most workloads.
- Break no preemption → Deadlock detection (the database preempts the victim).
- Break circular wait → Always acquire locks in the same global order - the most practical prevention strategy.

**WAIT-FOR GRAPH:**

```
T1 → T2 (T1 waits for a lock held by T2)
T2 → T3 (T2 waits for a lock held by T3)
T3 → T1 (T3 waits for a lock held by T1)
→ Cycle: T1 → T2 → T3 → T1 → DEADLOCK
```

**VICTIM SELECTION:**
PostgreSQL: always aborts the transaction that was detected to have caused the cycle (the last transaction to create the wait). InnoDB: selects the transaction with the lowest "weight" - typically the one that has modified the fewest rows (least rollback cost). Some databases allow configuring victim priority with `innodb_deadlock_detect`.

**DEADLOCK vs. LIVELOCK vs. STARVATION:**

- **Deadlock:** Circular wait - no progress possible without intervention.
- **Livelock:** Transactions retry but keep colliding - progress attempted but blocked (e.g., two transactions keep stepping back and trying again at the same time).
- **Starvation:** A transaction repeatedly loses the deadlock victim election - never makes progress despite no cycle.

---

### 🧪 Thought Experiment

**SETUP:**
Transfer $100 from Account A to Account B (T1) simultaneously with transfer $50 from Account B to Account A (T2).

**DEADLOCK SCENARIO:**

```
T1: BEGIN
T1: UPDATE accounts SET balance = balance - 100 WHERE id = A  → locks row A
T2: BEGIN
T2: UPDATE accounts SET balance = balance - 50 WHERE id = B   → locks row B
T1: UPDATE accounts SET balance = balance + 100 WHERE id = B  → waits for T2's lock on B
T2: UPDATE accounts SET balance = balance + 50 WHERE id = A   → waits for T1's lock on A
→ DEADLOCK: T1 waiting for B (held by T2); T2 waiting for A (held by T1)
```

**DATABASE DETECTS CYCLE:**

- Wait-for graph: T1 → T2 → T1 (cycle of length 2)
- Victim: T2 (fewer locks held or randomly selected)
- T2 aborted: `ERROR 1213: Deadlock found; try restarting transaction`
- T1 proceeds: locks B, completes, commits
- T2 application catches deadlock error, retries T2 from the beginning
- T2 retry: B is now unlocked → locks B → locks A → completes

**PREVENTION SOLUTION:**
Always lock accounts in order of account ID:

```
T1 and T2 both: lock lower account ID first
→ Both try to lock Account A first (id=1 < id=2)
→ T1 gets A, T2 waits for A
→ T1 gets B (no conflict), commits
→ T2 gets A, gets B, commits
→ No deadlock possible
```

---

### 🧠 Mental Model / Analogy

> A deadlock is a gridlock intersection. Car A needs to cross to the north and is blocking the east lanes. Car B needs to cross to the east and is blocking the north lanes. A traffic officer (deadlock detector) periodically surveys the intersection. If gridlocked, the officer picks one car (victim), directs it to back up (transaction abort + rollback), and the intersection clears. The backed-up car rejoins at the end of the queue (application retry).

- "Car blocking intersection lane" → transaction holding a lock
- "Car waiting for a lane" → transaction waiting for a lock
- "Circular blocking" → wait-for graph cycle
- "Traffic officer surveys" → deadlock detection algorithm runs
- "Picks one car to back up" → victim selection
- "Car backs up" → transaction aborted and rolled back
- "Car rejoins queue" → application retries the transaction

Where this analogy breaks down: The traffic officer runs continuously (or very frequently - every few milliseconds in InnoDB). In contrast, traffic officers don't constantly survey every intersection.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A deadlock is when two database operations are stuck waiting for each other - Transaction A is waiting for something Transaction B has, and Transaction B is waiting for something Transaction A has. Neither can move forward. The database detects this standoff and forces one to give up (retry), so the other can finish.

**Level 2 - How to use it (junior developer):**
You don't "use" deadlock detection - the database handles it automatically. What you must do: catch the deadlock error in your application and retry the transaction. In Spring/JPA: catch `CannotAcquireLockException`. In raw JDBC: catch `SQLException` with error code 1213 (MySQL) or SQL state 40P01 (PostgreSQL). Implement retry with exponential backoff: wait 50ms, retry; wait 100ms, retry; wait 200ms, retry - up to 3 retries before failing to the user.

**Level 3 - How it works (mid-level engineer):**
InnoDB deadlock detection algorithm: runs whenever a lock wait is requested. Builds a wait-for graph on the fly. Traverses the graph using DFS to detect cycles. If a cycle is found, selects the victim (minimum weight transaction) and immediately rolls it back. Cycle detection is O(N²) in the number of waiting transactions - typically very fast (< 1ms) because production deadlocks are almost always 2-3 transactions. `innodb_deadlock_detect = ON` (default). Can be disabled (`OFF`) for extreme-throughput workloads that use `lock_wait_timeout` instead - but this is dangerous and rarely appropriate. PostgreSQL detects deadlocks using a similar wait-for graph scan but also with a configurable `deadlock_timeout` (default 1 second) - it waits `deadlock_timeout` before running the detection algorithm to avoid overhead for lock contention that resolves quickly.

**Level 4 - Why it was designed this way (senior/staff):**
The choice between deadlock detection vs. deadlock prevention (timeout-based lock waiting) involves a fundamental trade-off. Timeout-based: simpler implementation, but causes long waits (up to timeout duration) for legitimate deadlocks, wasting resources. Detection-based: faster resolution (< 1ms for detection) but incurs graph-traversal overhead on every lock wait. InnoDB chose detection. PostgreSQL does both: wait `deadlock_timeout` (1s default) to handle temporary contention, then run detection. The victim selection heuristic matters for system throughput: aborting the transaction that has done the least work minimizes rollback cost. But if one transaction type is always lightweight (e.g., reads with SELECT FOR UPDATE), it becomes the perpetual victim - starvation risk. Production systems with chronic deadlock issues should redesign lock acquisition order rather than tuning victim selection. The global lock ordering principle (always acquire locks in a consistent order across all code paths) eliminates deadlocks structurally.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WAIT-FOR GRAPH: DEADLOCK DETECTION                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ T1 holds lock(A) ──waits for──→ T2                   │
│ T2 holds lock(B) ──waits for──→ T1                   │
│                                                      │
│ Wait-for graph:                                      │
│     T1 ──→ T2 ──→ T1  (CYCLE DETECTED)              │
│                                                      │
│ Detection: DFS from each node, look for back-edge    │
│ Victim: T2 (fewer rows modified = cheaper rollback)  │
│ Action: ROLLBACK T2, release lock(B)                 │
│ Result: T1 acquires lock(B), commits                 │
│         T2 receives ERROR 1213 / SQL state 40P01     │
│         Application retries T2                       │
│                                                      │
│ TIMING (InnoDB):                                     │
│ Detection: < 1ms after lock wait registered          │
│ PostgreSQL: waits deadlock_timeout (1s) first        │
│             then runs detection algorithm            │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
T1 and T2 acquire locks in consistent order (A before B)
→ T1 gets A → T1 gets B → T1 commits → both released
→ T2 gets A (after T1 releases) → T2 gets B → T2 commits
→ No deadlock: consistent lock ordering prevents cycle
```

**FAILURE PATH:**

```
T1 acquires lock A; T2 acquires lock B (opposite order)
→ T1 requests lock B → waits for T2
→ T2 requests lock A → waits for T1
→ Deadlock detector scans: T1→T2→T1 cycle
→ Victim selected: T2 aborted
→ T2 application: catches CannotAcquireLockException
→ T2 application: no retry implemented → returns 500 to user
→ User sees internal server error; data not corrupted
→ But user experience broken; retry was needed
```

**WHAT CHANGES AT SCALE:**
High-concurrency write workloads produce frequent deadlocks. If each deadlock takes 1 second to detect (PostgreSQL's default `deadlock_timeout`) and there are 10 deadlocks/second, 10 connections are always stuck for 1 second - at 100 connections, this consumes 10% capacity. Reduce `deadlock_timeout` to 50–100ms for OLTP workloads with hot contention. Or redesign to eliminate deadlocks through consistent lock ordering - zero detection overhead.

---

### ⚖️ Comparison Table

| Approach               | Deadlock Resolution        | Overhead               | Recovery Time   | Best For                   |
| ---------------------- | -------------------------- | ---------------------- | --------------- | -------------------------- |
| **Detection (InnoDB)** | Immediate cycle detection  | DFS on lock wait graph | < 1ms detection | Default OLTP               |
| **Timeout-based**      | Abort after N seconds      | None until timeout     | Up to N seconds | Simple, rare deadlocks     |
| **Lock ordering**      | Prevention (no deadlocks)  | Developer discipline   | N/A             | High-concurrency writes    |
| **Optimistic locking** | Prevention (no locks held) | Retry overhead         | Immediate       | Read-heavy, low contention |

How to choose: InnoDB detection is the right default. Use lock ordering as a design principle to minimize deadlock frequency. Use optimistic locking for write-rarely, read-often patterns.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A deadlock means the database is broken           | Deadlocks are expected in concurrent systems; the database handles them correctly via victim selection; the only requirement is application-level retry |
| Deadlocks are rare and can be ignored             | At high concurrency, deadlocks can occur dozens/second; without retry logic, this causes user-visible errors on every deadlock                          |
| Disabling deadlock detection improves performance | Only safe if using lock_wait_timeout as the fallback; disabling detection + no timeout = stuck transactions forever                                     |
| Increasing lock_wait_timeout prevents deadlocks   | It doesn't prevent them - just increases the time a deadlocked transaction waits before aborting; use lock ordering to prevent deadlocks                |

---

### 🚨 Failure Modes & Diagnosis

**1. Application Not Retrying Deadlock Errors**

**Symptom:** User sees 500 Internal Server Error intermittently; logs show `CannotAcquireLockException` or `Deadlock found`; no retry attempted.

**Root Cause:** Application code catches the exception and returns an error instead of retrying.

**Diagnostic:**

```
Log analysis: grep "deadlock\|CannotAcquireLock\|1213\|40P01" app.log
→ If frequency > 0 and no "retrying" log message → retry logic missing
```

**Fix (Java/Spring):**

```java
@Retryable(
    value = CannotAcquireLockException.class,
    maxAttempts = 3,
    backoff = @Backoff(delay = 50, multiplier = 2)
)
@Transactional
public void transferFunds(long fromId, long toId, BigDecimal amount) {
    // transfer logic
}
```

**Prevention:** All write transactions that involve multiple rows must have retry logic for deadlock errors. Add deadlock error monitoring - deadlock rate > 1/second suggests a lock ordering problem that should be fixed structurally.

---

**2. Chronic Deadlocks from Inconsistent Lock Ordering**

**Symptom:** High deadlock rate (dozens/second) in `SHOW ENGINE INNODB STATUS`; same pair of tables always involved; performance degrading.

**Root Cause:** Two code paths that update the same two tables (or rows) do so in opposite orders - guaranteeing deadlock under any concurrent execution.

**Diagnostic:**

```sql
-- MySQL: examine last deadlock
SHOW ENGINE INNODB STATUS\G
-- Look for LATEST DETECTED DEADLOCK
-- Pattern: T1 holds lock on table A row X, waiting for table B row Y
--           T2 holds lock on table B row Y, waiting for table A row X
-- → Both code paths need to acquire locks A→B (not A→B and B→A)
```

**Fix:** Audit all code paths that touch both tables. Standardize lock acquisition order: always process table A rows before table B rows, or always process lower entity ID before higher ID.

**Example fix:**

```java
// Before (deadlock-prone): order depends on input order
void transfer(Account from, Account to, BigDecimal amount) {
    lock(from); lock(to); // T1 might lock A then B
    // T2 might lock B then A → deadlock
}

// After (deadlock-free): always lock lower ID first
void transfer(Account from, Account to, BigDecimal amount) {
    Account first = from.id < to.id ? from : to;
    Account second = from.id < to.id ? to : from;
    lock(first); lock(second); // always consistent order
}
```

**Prevention:** Document lock acquisition order as an architectural rule. Code review should check that any code touching multiple entities acquires locks in a globally consistent order.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Locking (Row, Table, Gap, Next-Key)` - deadlocks are caused by lock conflicts
- `Transaction` - deadlocks only occur within transactions
- `Isolation Levels` - isolation level determines what locks are acquired; SERIALIZABLE acquires most locks

**Builds On This (learn these next):**

- `Optimistic vs. Pessimistic Locking` - optimistic locking avoids deadlocks by not holding locks
- `Connection Pooling (DB)` - deadlocks consume connections; pool sizing must account for deadlock retry

**Alternatives / Comparisons:**

- `Optimistic vs. Pessimistic Locking` - optimistic avoids deadlocks entirely; pessimistic must handle them
- `MVCC` - reduces deadlock frequency by eliminating read-write lock contention

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Circular lock wait → wait-for graph cycle │
│              │ → DB detects → victim aborted → retry     │
├──────────────┼───────────────────────────────────────────┤
│ DETECTION    │ InnoDB: immediate DFS on lock wait        │
│              │ PostgreSQL: wait deadlock_timeout then DFS│
├──────────────┼───────────────────────────────────────────┤
│ VICTIM       │ Transaction with least work done          │
│              │ (fewest rows modified)                    │
├──────────────┼───────────────────────────────────────────┤
│ APP RESPONSE │ Catch error, retry with backoff           │
│              │ Spring: @Retryable(CannotAcquireLockEx)   │
├──────────────┼───────────────────────────────────────────┤
│ PREVENTION   │ Always acquire locks in consistent order  │
│              │ (e.g., lower entity ID first)             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Circular lock wait → DB picks a victim   │
│              │  to abort → app must retry"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Locking → Optimistic vs Pessimistic Lock  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) You're building a financial ledger service. Every transaction involves debiting one account and crediting another. Account IDs are UUIDs (unordered). Without a global lock ordering strategy, any two concurrent transfers touching the same pair of accounts in reverse order will deadlock. Design a lock ordering strategy that: (a) works with UUID account IDs, (b) is enforced at the service layer regardless of which endpoints are called, (c) handles 3-party transfers (A → B → C in one transaction).

**Q2.** (TYPE E - Optimization) A high-throughput order processing service experiences 50 deadlocks/minute. The deadlocks always involve the same pattern: `inventory` table row updated in one code path before `order_items` table, and in reverse order in another code path. Propose three solutions at different levels: (a) fix the immediate deadlock (code change), (b) reduce deadlock frequency without code restructuring (configuration change), (c) eliminate the root cause (architectural change). Analyze trade-offs of each.
