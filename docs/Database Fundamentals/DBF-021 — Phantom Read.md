---
layout: default
title: "Phantom Read"
parent: "Database Fundamentals"
nav_order: 21
permalink: /databases/phantom-read/
number: "DBF-021"
category: Database Fundamentals
difficulty: ★★☆
depends_on: Non-Repeatable Read, Isolation Levels, MVCC
used_by: SERIALIZABLE, Gap Lock, Predicate Locking
related: Non-Repeatable Read, Write Skew, Dirty Read
tags:
  - database
  - transactions
  - concurrency
  - intermediate
---

# DBF-021 — Phantom Read

⚡ TL;DR — A phantom read is when a transaction runs the same range query twice and gets different rows, because another transaction inserted or deleted rows matching that range between the two queries.

| #421            | Category: Database Fundamentals             | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Non-Repeatable Read, Isolation Levels, MVCC |                 |
| **Used by:**    | SERIALIZABLE, Gap Lock, Predicate Locking   |                 |
| **Related:**    | Non-Repeatable Read, Write Skew, Dirty Read |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A capacity management system checks "how many active sessions do we have?" to enforce a maximum of 100 concurrent users. Transaction A queries: `SELECT COUNT(*) FROM sessions WHERE status = 'ACTIVE'` — result: 99. Just before A inserts a new session, Transactions B and C each insert a new active session and commit. Transaction A inserts its session: now 102 active sessions exist, despite the guard that was supposed to prevent exceeding 100. The check saw 99; it inserted; but the reality changed between the check and the insert.

**THE BREAKING POINT:**
Any "count then insert" or "find rows matching condition then make decisions" logic is vulnerable. Reservation systems, capacity limits, business rule enforcement (at most N per user/day/hour) — all are silent targets for phantom reads under REPEATABLE READ.

**THE INVENTION MOMENT:**
"This is exactly why SERIALIZABLE isolation was created."

---

### 📘 Textbook Definition

A **phantom read** is a concurrency anomaly where a transaction executes the same query with the same predicate (range or condition) twice within the same transaction and receives a different set of rows, because another transaction committed an INSERT or DELETE matching that predicate between the two executions. Unlike a non-repeatable read (where existing row values change), a phantom read involves the appearance or disappearance of entire rows. Phantom reads are prevented by the **SERIALIZABLE** isolation level. MySQL InnoDB's **REPEATABLE READ** also prevents phantoms via gap locks; PostgreSQL's REPEATABLE READ does not prevent all phantoms.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A phantom read is when the set of rows matching your query changes between two runs of the same query in one transaction.

**One analogy:**

> You count the people in a room: 10. You turn around to write it down. Three people sneak in the back. You count again: 13. The room is the same, the people who were there are the same, but the set changed. Phantom reads are those three people appearing between your two counts.

**One insight:**
Phantom reads are subtle because REPEATABLE READ prevents value changes to existing rows — but says nothing about new rows arriving or old rows departing. A "SELECT WHERE condition" at REPEATABLE READ can still return different sets in PostgreSQL if rows matching the condition were inserted or deleted by concurrent commits.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A phantom read is about the set of rows matching a predicate, not the values within existing rows.
2. REPEATABLE READ guarantees the same value for a row you've previously read — it doesn't guarantee no new rows will appear.
3. Preventing phantoms requires locking or tracking the predicate space (range), not just individual row versions.

**DERIVED DESIGN:**
Two approaches prevent phantom reads:

**Predicate locking (conceptual):** Lock the entire range of the predicate — any INSERT into that range by a concurrent transaction must wait. True predicate locking is expensive and rarely fully implemented.

**Gap locks (MySQL InnoDB):** Instead of locking just the row, lock the gap between indexed values. A `SELECT ... WHERE id BETWEEN 10 AND 20 FOR UPDATE` at REPEATABLE READ locks not just rows 10–20 but the gaps between them — no new row with id 11–19 can be inserted until the lock is released.

**SSI (Serializable Snapshot Isolation, PostgreSQL):** Tracks read-write dependencies between transactions. If Transaction A's range query would have returned different results had Transaction B's INSERT been visible, and A and B's operations form a cycle, one is aborted.

**THE TRADE-OFFS:**
**SERIALIZABLE:**

- Gain: no phantom reads; correct results for any range-based business logic.
- Cost: higher abort/retry rate; PostgreSQL SSI overhead; MySQL gap lock deadlock risk.

---

### 🧪 Thought Experiment

**SETUP:**
An application enforces "max 3 active reservations per user." It checks the count, then inserts if under the limit.

**PHANTOM READ SCENARIO (REPEATABLE READ in PostgreSQL):**

- Transaction A: `SELECT COUNT(*) FROM reservations WHERE user_id=42 AND status='ACTIVE'` → 2.
- Transaction B: Inserts a new active reservation for user 42. Commits.
- Transaction A: Verifies (re-counts or relies on initial count) → still 2 (REPEATABLE READ).
- Transaction A: Inserts reservation (count was 2 < 3 = OK).
- Result: Database has 4 active reservations for user 42. Limit violated.

Note: In PostgreSQL REPEATABLE READ, the re-read also returns 2 (snapshot frozen). But the INSERT by A still creates a new row — the snapshot protects reads, not the validity of the count-based insert decision.

**SERIALIZABLE SCENARIO:**

- Transaction A reads count = 2. Snapshot + SSI dependency recorded.
- Transaction B inserts for same user. Commits.
- Transaction A tries to commit: SSI detects A's read predicate conflicts with B's insert.
- Transaction A aborted: "ERROR: could not serialize access."
- Transaction A retries: now reads count = 3 → does not insert.
- Result: Limit enforced correctly.

**THE INSIGHT:**
The phantom read problem is about the gap between the observation ("2 reservations") and the action ("insert because count < 3"). SERIALIZABLE closes this gap by making the observation and action atomic with respect to the predicate.

---

### 🧠 Mental Model / Analogy

> A phantom read is like counting chairs in a meeting room to see if there's space for one more person, stepping out to get the person, and returning to find someone moved 3 more chairs in while you were gone — now the room is full. You checked the predicate (number of chairs < capacity), made a decision (go get someone), and the predicate's result changed between check and action. SERIALIZABLE ensures nobody can change the chair count in the range you checked while your decision is in flight.

- "Counting chairs" → SELECT COUNT(\*) WHERE condition
- "Stepping out" → the gap between read and write in your transaction
- "Chairs moved in" → concurrent INSERT matching your predicate
- "Room full on return" → phantom — new rows appeared
- "SERIALIZABLE" → locking or aborting to prevent the change while your transaction is in flight

Where this analogy breaks down: SERIALIZABLE doesn't literally lock the room — it detects the conflict and aborts one transaction, which then retries with fresh data.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A phantom read is when the same "find all X matching Y" query returns different results at two points in the same database operation, because new matching records were added in between. The word "phantom" captures it — new rows appear like ghosts.

**Level 2 — How to use it (junior developer):**
Use `@Transactional(isolation = Isolation.SERIALIZABLE)` for any count-then-insert, check-then-insert pattern that enforces a capacity limit. Handle `CannotSerializeTransactionException` with retry logic. Alternatively, use a database-level UNIQUE constraint or `INSERT ... WHERE NOT EXISTS` to enforce limits atomically.

**Level 3 — How it works (mid-level engineer):**
PostgreSQL REPEATABLE READ uses MVCC snapshot — frozen at transaction start. New rows inserted by T2 with `xmin > snapshot_id` are invisible to T1's reads. But this only affects reads — T1 can still INSERT a row that "conflicts" conceptually with the business rule. PostgreSQL SERIALIZABLE SSI tracks anti-dependencies: if T1 read a predicate range and T2 inserted into that range, SSI records this. If T1 then writes based on what it read, a read-write dependency cycle is detected → one transaction aborts. MySQL InnoDB gap locks at REPEATABLE READ: lock the indexed gap so no INSERT can occur in the range between T1's read and its commit.

**Level 4 — Why it was designed this way (senior/staff):**
Phantom reads expose a fundamental limitation of row-level MVCC: MVCC versioning protects individual rows, but not the predicate space (the set of rows matching a condition). Truly preventing phantoms requires either predicate locking (expensive, rarely fully implemented) or detecting conflicts at commit time (SSI) or locking gaps (MySQL gap locks). PostgreSQL chose SSI over gap locks because gap locks cause notorious deadlocks in InnoDB — two transactions acquiring gap locks in different orders can deadlock. SSI avoids this by being optimistic (no locks taken) and aborting only on detected cycles. The practical implication: SERIALIZABLE is the only reliable choice for phantom-free operation in PostgreSQL; REPEATABLE READ in PostgreSQL is not phantom-safe.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ PHANTOM READ: MECHANISMS                     │
├──────────────────────────────────────────────┤
│                                              │
│  REPEATABLE READ (PostgreSQL) — NOT safe:    │
│                                              │
│  T1 snapshot: reads 2 rows matching WHERE   │
│  T2 inserts 1 row matching WHERE → commits  │
│  T1 re-reads: still sees 2 (snapshot)       │
│  T1 inserts based on count=2 → commits      │
│  Result: 4 rows exist (business rule broken)│
│                                              │
│  SERIALIZABLE (PostgreSQL SSI) — safe:       │
│                                              │
│  T1 reads predicate P: 2 rows              │
│  T2 inserts row matching P → commits        │
│  ┌────────────────────────────────────────┐  │
│  │ SSI detects:                           │  │
│  │   T1 read predicate P                 │  │
│  │   T2 wrote row matching P             │  │
│  │   T1 would produce different result   │  │
│  │   if T2 was visible → cycle detected  │  │
│  └────────────────────────────────────────┘  │
│  T1 commit → ABORT: serialization failure   │
│  T1 retries → reads 3 rows → does not insert│
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
T1 BEGIN SERIALIZABLE → read predicate range
→ [PHANTOM READ prevention ← YOU ARE HERE]
→ SSI tracks T1's read predicate
→ T2 inserts matching row → SSI records dependency
→ T1 COMMIT → conflict detected → T1 aborted
→ T1 retries with fresh data
```

**FAILURE PATH:**

```
Application doesn't implement retry logic
→ Serialization error not handled
→ Business operation silently fails
→ Data not written, user sees error or silent failure
```

**WHAT CHANGES AT SCALE:**
At high write concurrency with SERIALIZABLE, SSI abort rates increase significantly for hot predicates (ranges or conditions that many transactions read and write). Each abort requires a full transaction retry, increasing latency and load. Design: narrow predicates (smaller ranges) reduce conflict rates. Alternatively, move predicate-based business rules to atomic SQL patterns (`INSERT ... WHERE NOT EXISTS`, `UPDATE ... WHERE count < limit`) that don't require multi-statement predicate safety.

---

### ⚖️ Comparison Table

| Anomaly             | Row Change       | New Rows                | Prevention Level | Typical Scenario                      |
| ------------------- | ---------------- | ----------------------- | ---------------- | ------------------------------------- |
| Dirty Read          | Uncommitted      | No                      | READ COMMITTED   | Reading in-progress writes            |
| Non-Repeatable Read | Committed change | No                      | REPEATABLE READ  | Re-reading changed existing row       |
| **Phantom Read**    | **No change**    | **Yes (new/deleted)**   | **SERIALIZABLE** | **Count-then-insert capacity checks** |
| Write Skew          | Committed        | No (but combined wrong) | SERIALIZABLE     | Disjoint read, concurrent writes      |

How to choose: Phantom reads affect any logic that counts or scans a range and makes decisions based on that count/set. If your transaction does count-based guards or range-based capacity enforcement, use SERIALIZABLE or atomic SQL patterns.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                 |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| REPEATABLE READ prevents phantom reads      | Only MySQL InnoDB REPEATABLE READ prevents phantoms (via gap locks); PostgreSQL REPEATABLE READ does NOT prevent all phantom reads                                      |
| Phantom reads only affect COUNT queries     | Any range predicate query (WHERE status='ACTIVE', WHERE date BETWEEN, WHERE category='X') is vulnerable — the phantom is any new row matching the predicate             |
| SERIALIZABLE makes phantom reads impossible | SERIALIZABLE prevents phantoms by aborting conflicting transactions — application code must implement retry logic; without retry, phantom read prevention is incomplete |
| Gap locks in MySQL are always safe          | MySQL gap locks can cause deadlocks when two transactions acquire gap locks in different orders on the same range — a known InnoDB limitation                           |

---

### 🚨 Failure Modes & Diagnosis

**1. Capacity Limit Exceeded Due to Phantom Read**

**Symptom:** System allows more than the configured maximum (users, sessions, reservations) — count-based limit is violated despite the check.

**Root Cause:** Count-then-insert pattern at REPEATABLE READ or READ COMMITTED — multiple transactions simultaneously see count < limit and all insert.

**Diagnostic:**

```sql
-- Find capacity violations
SELECT user_id, COUNT(*) as reservation_count
FROM reservations
WHERE status = 'ACTIVE'
GROUP BY user_id
HAVING COUNT(*) > 3;  -- 3 = configured max
```

**Fix:**

```sql
-- Atomic enforcement: insert only if count < limit
INSERT INTO reservations (user_id, event_id, status)
SELECT 42, 100, 'ACTIVE'
WHERE (
  SELECT COUNT(*) FROM reservations
  WHERE user_id = 42 AND status = 'ACTIVE'
) < 3;

-- Check rows inserted = 1; if 0, limit was reached
-- This entire statement is atomic at the SQL engine level
-- at SERIALIZABLE isolation
```

**Prevention:** Use SERIALIZABLE + retry for count-based capacity enforcement, or use database-level constraints (partial unique index, trigger) to enforce limits atomically.

---

**2. Gap Lock Deadlock in MySQL InnoDB**

**Symptom:** In MySQL, transactions time out with `ERROR 1213: Deadlock found when trying to get lock` on range queries even when rows involved are different.

**Root Cause:** Two transactions acquire gap locks on overlapping ranges in different orders — classic deadlock scenario specific to InnoDB's gap locking mechanism for phantom prevention.

**Diagnostic:**

```sql
-- MySQL: show last deadlock details
SHOW ENGINE INNODB STATUS\G
-- Look for "LATEST DETECTED DEADLOCK" section
-- Shows which gap locks were involved and in what order
```

**Fix:** Use consistent lock ordering (always lock ranges in ascending order). Alternatively, switch to SERIALIZABLE with PostgreSQL's SSI which avoids gap lock deadlocks.

**Prevention:** Identify high-contention range queries. Use advisory locks or redesign to avoid overlapping range predicates in concurrent transactions.

---

**3. Missing Retry Logic for SERIALIZABLE Failures**

**Symptom:** `CannotSerializeTransactionException` logged but not handled; affected operations fail silently; business invariants enforced but data not written.

**Root Cause:** Application uses SERIALIZABLE isolation but doesn't implement retry on serialization failure — this error is expected and normal; it means "retry this transaction."

**Diagnostic:**

```bash
# Count serialization failures per hour
grep "could not serialize" /var/log/postgresql/postgresql*.log | \
  sed 's/.*\(20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]\).*/\1/' | \
  sort | uniq -c
```

**Fix:**

```java
@Retryable(
    value = CannotSerializeTransactionException.class,
    maxAttempts = 3,
    backoff = @Backoff(delay = 50, multiplier = 2))
@Transactional(isolation = Isolation.SERIALIZABLE)
public void createReservation(Long userId, Long eventId) {
    long count = reservationRepo
        .countByUserIdAndStatus(userId, "ACTIVE");
    if (count >= maxReservations) {
        throw new CapacityExceededException();
    }
    reservationRepo.save(new Reservation(userId, eventId));
}
```

**Prevention:** Every SERIALIZABLE transaction must have retry logic. Use Spring's `@Retryable` or a manual retry loop. Make transactions idempotent to handle retries safely.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Non-Repeatable Read` — phantom read is the next level: not changed values, but appeared/disappeared rows
- `Isolation Levels` — phantom read defines why SERIALIZABLE exists
- `MVCC` — snapshot isolation handles non-repeatable reads but not phantoms

**Builds On This (learn these next):**

- `MVCC` — understanding why snapshot isolation doesn't prevent phantoms
- `Locking (Row, Table, Gap, Next-Key)` — MySQL InnoDB's mechanism for phantom prevention via gap locks
- `Write Skew` — related anomaly at the same SERIALIZABLE boundary

**Alternatives / Comparisons:**

- `Non-Repeatable Read` — existing row value changed vs. new rows appeared
- `Write Skew` — two transactions each reading and writing disjoint sets, together violating a constraint

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Same range query returns different rows   │
│              │ at two points in the same transaction     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Count-based guards can be bypassed by     │
│ SOLVES       │ concurrent inserts between check+insert   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ PostgreSQL REPEATABLE READ does NOT        │
│              │ prevent phantoms — need SERIALIZABLE      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ SERIALIZABLE for count-based limits or    │
│              │ range-based business rule enforcement     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use SERIALIZABLE for read-only      │
│              │ queries — READ COMMITTED is sufficient    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Correct range queries vs abort/retry      │
│              │ overhead under high concurrent inserts    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "You counted 10, turned around, and       │
│              │  3 more appeared — that's a phantom"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Write Skew → MVCC → Locking               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Trade-off) A high-throughput ticketing platform must enforce "max 2 tickets per user per event." The system processes 500 ticket purchase requests per second during peak. Option A: SERIALIZABLE isolation with retry. Option B: `INSERT ... WHERE COUNT < 2` atomic SQL. Option C: Database-level partial unique index. Compare all three on: prevention correctness, throughput impact, implementation complexity, and retry complexity. Which is correct for this scale?

**Q2.** (TYPE F — Comparison Depth) Both phantom reads and write skew require SERIALIZABLE isolation to prevent — yet they are different anomalies. Describe a real business scenario that is a write skew but not a phantom read, and a scenario that is a phantom read but not a write skew. What is the precise structural difference between the two anomalies?
