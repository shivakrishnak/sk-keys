---
version: 2
layout: default
title: "Isolation"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /databases/isolation/
id: DBF-049
category: Database Fundamentals
difficulty: ★★☆
depends_on: ACID, Transaction, Concurrency
used_by: Isolation Levels, MVCC, Locking
related: Dirty Read, Phantom Read, Non-Repeatable Read
tags:
  - database
  - transactions
  - concurrency
  - intermediate
---

# DBF-040 - Isolation

⚡ TL;DR - Isolation is the ACID guarantee that concurrent transactions don't interfere with each other - each transaction behaves as if it's the only one running, even when thousands execute simultaneously.

| #414            | Category: Database Fundamentals               | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------- | :-------------- |
| **Depends on:** | ACID, Transaction, Concurrency                |                 |
| **Used by:**    | Isolation Levels, MVCC, Locking               |                 |
| **Related:**    | Dirty Read, Phantom Read, Non-Repeatable Read |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A flight booking system: User A reads "2 seats available," starts filling out passenger details. In the 30 seconds it takes, User B books both remaining seats and commits. User A submits their booking - they're reading stale data but the system doesn't know it. Both bookings go through. The flight is now overbooked. Alternatively, User A's in-progress transaction writes a "PENDING" booking that User B's transaction reads - and B charges the customer for a seat that A's transaction hasn't committed yet (and may roll back).

**THE BREAKING POINT:**
Any system where two transactions can read each other's in-progress writes, or where a transaction reads data that changes under it mid-execution, produces results that are logically impossible with sequential execution. Financial systems double-count money. Inventory systems oversell. Analytics produce numbers that could never exist in a consistent snapshot.

**THE INVENTION MOMENT:**
"This is exactly why Isolation was created."

---

### 📘 Textbook Definition

**Isolation** is the third property of ACID, guaranteeing that the concurrent execution of transactions produces the same result as if the transactions were executed serially (one after another). The degree of isolation is configurable via **isolation levels** (READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE), each offering different trade-offs between correctness and performance. Isolation is implemented via **locking** (pessimistic) or **MVCC** - Multi-Version Concurrency Control (optimistic), where readers see a snapshot of the database as of a specific point in time without blocking writers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Isolation ensures transactions don't see each other's in-progress, uncommitted work.

**One analogy:**

> Two accountants working on the same company's books. Isolation gives each accountant their own private photocopy of the ledger to work from. Changes one accountant makes to their copy are invisible to the other until they formally submit their changes. Neither accountant sees the other's scratch work - only the final, committed results.

**One insight:**
Isolation is the most expensive of the four ACID properties to guarantee. Full Serializability (complete isolation) can cut write throughput by 50–90% under contention. This is why databases offer isolation levels - weaker levels (READ COMMITTED) are the default in most databases because they're faster, even though they allow anomalies. Understanding which anomalies your business logic can tolerate is the core isolation design decision.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A transaction's uncommitted writes must be invisible to other transactions (at minimum).
2. The result of concurrent transaction execution must be equivalent to some serial order of execution.
3. The stronger the isolation, the fewer anomalies - and the lower the throughput.

**DERIVED DESIGN:**
Two approaches to implementing isolation:

**Locking (pessimistic):** Transactions acquire read or write locks on data they access. Other transactions wait. Guarantees isolation by preventing concurrent access - but causes lock contention and deadlocks.

**MVCC (optimistic):** The database maintains multiple versions of rows. Writers create new versions; readers access the version that was current at their transaction's start time. Readers never block writers; writers never block readers. Only write-write conflicts require serialization. PostgreSQL, MySQL InnoDB, Oracle all use MVCC.

The trade-off between isolation levels is which anomalies are allowed:

- Dirty Read: reading another transaction's uncommitted write
- Non-Repeatable Read: same row read twice returns different values
- Phantom Read: same query run twice returns different rows

**THE TRADE-OFFS:**
**Gain:** Transactions produce consistent, logical results even under heavy concurrency.
**Cost:** Locks reduce concurrency; MVCC creates row version bloat requiring cleanup (PostgreSQL VACUUM). Higher isolation levels reduce throughput significantly.

---

### 🧪 Thought Experiment

**SETUP:**
User A reads an account balance, computes a withdrawal amount, and writes the new balance. User B simultaneously reads and writes the same account balance. Both transactions run concurrently.

**WHAT HAPPENS WITHOUT ISOLATION:**

- A reads balance: $1000.
- B reads balance: $1000.
- A withdraws $300: writes balance $700.
- B withdraws $500: writes balance $500 (B read the original $1000, not A's $700).
- Final balance: $500. But two withdrawals of $300 + $500 = $800 were made.
- $300 effectively vanished - B's write overwrote A's write. This is the "lost update" anomaly.

**WHAT HAPPENS WITH ISOLATION:**

- A begins transaction, reads balance: $1000. Acquires lock (or snapshot).
- B begins transaction, tries to read balance - waits for A's lock (or reads snapshot at $1000, but write-write conflict detected at commit).
- A withdraws $300, writes $700, commits. Lock released.
- B resumes. Under REPEATABLE READ: B sees $700, computes correct balance.
- B withdraws $500: $700 - $500 = $200. Commits.
- Final balance: $200. Correct. ($1000 - $300 - $500 = $200.)

**THE INSIGHT:**
The "lost update" anomaly is silent - no error is thrown, data looks valid, but one transaction's write has been overwritten. Isolation prevents this by serialising conflicting write operations.

---

### 🧠 Mental Model / Analogy

> Isolation is like a whiteboard in a meeting room. Each team gets their own private whiteboard for their meeting. What one team writes on their whiteboard is invisible to other teams until they post the final result on the shared bulletin board. Nobody sees another team's draft work. The shared bulletin board (the committed database) only gets updated with complete, finished results.

- "Private whiteboard per team" → each transaction's private write buffer (MVCC version / undo log)
- "Meeting room" → transaction scope
- "Posting to bulletin board" → COMMIT (writes become visible)
- "Throwing whiteboard away" → ROLLBACK (private writes discarded)
- "Waiting for the room" → lock wait (under pessimistic locking)

Where this analogy breaks down: in MVCC, multiple "bulletin boards" (row versions) coexist simultaneously - the bulletin board metaphor implies one version, but MVCC maintains many.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Isolation means that when you're in the middle of making database changes, nobody else can see your half-finished work, and you can't see theirs. You each work in your own private space until you're done.

**Level 2 - How to use it (junior developer):**
Set your transaction isolation level based on what your operation requires: `SET TRANSACTION ISOLATION LEVEL READ COMMITTED` (default in PostgreSQL, MySQL), or `REPEATABLE READ`, or `SERIALIZABLE`. In Spring, use `@Transactional(isolation = Isolation.REPEATABLE_READ)`. Choose SERIALIZABLE for financial read-modify-write cycles; READ COMMITTED for most web application reads.

**Level 3 - How it works (mid-level engineer):**
Under MVCC (PostgreSQL): each row has `xmin` (transaction that created it) and `xmax` (transaction that deleted/updated it). A query sees rows whose `xmin` is a committed transaction that started before the reader's snapshot, and whose `xmax` is not yet committed. This snapshot is consistent - the reader sees the database as of a fixed point in time. Under InnoDB (MySQL): MVCC snapshot + gap locks prevent phantom reads at REPEATABLE READ level.

**Level 4 - Why it was designed this way (senior/staff):**
True serializability (SSI - Serializable Snapshot Isolation) was impractical for decades, requiring full lock escalation or 2PL. PostgreSQL 9.1 (2011) introduced SSI using Serializable Snapshot Isolation - an optimistic technique that detects serializability violations at commit time and aborts the conflicting transaction, without locking. This makes SERIALIZABLE in PostgreSQL practical for production use with ~10–30% throughput cost (vs. 50–90% for 2PL). MySQL still uses locking-based SERIALIZABLE, which is why READ COMMITTED is the recommended default in InnoDB for most workloads.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ MVCC SNAPSHOT ISOLATION                      │
├──────────────────────────────────────────────┤
│                                              │
│  Time → T1 begins       T2 begins           │
│          │              │                   │
│          │ Read row A=5 │                   │
│          │              │ Update A=10       │
│          │              │ COMMIT            │
│          │                                  │
│  Under READ COMMITTED:                       │
│    T1 re-reads A → sees 10 (T2's commit)    │
│    (non-repeatable read allowed)             │
│                                              │
│  Under REPEATABLE READ / SERIALIZABLE:       │
│    T1 re-reads A → sees 5 (snapshot)        │
│    T2's commit is invisible to T1            │
│    (non-repeatable read prevented)           │
│                                              │
│  MVCC Row Versions (PostgreSQL):             │
│  ┌─────────────────────────────────────────┐ │
│  │ row | xmin | xmax | value              │ │
│  │  A  |  100 | null |  5   ← T1 sees    │ │
│  │  A  |  101 | null |  10  ← T2 created │ │
│  └─────────────────────────────────────────┘ │
│  T1 (started at xid 100) ignores xmin=101   │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
T1 BEGIN → T1 reads snapshot (MVCC)
→ [ISOLATION ← YOU ARE HERE: snapshot filters row versions]
→ T1 writes (new row version created)
→ T1 COMMIT → new version visible to future transactions
→ Old versions cleaned by VACUUM
```

**FAILURE PATH:**

```
Serialization conflict detected at commit
→ T1 aborted: "ERROR: could not serialize access"
→ App must retry the entire transaction
→ On retry, T1 reads fresh snapshot with T2's committed data
```

**WHAT CHANGES AT SCALE:**
At high concurrency with SERIALIZABLE isolation, abort/retry rates increase - applications must implement retry logic for serialization failures. Under REPEATABLE READ with long-running transactions, MVCC bloat accumulates (PostgreSQL), requiring aggressive VACUUM to prevent table bloat and transaction ID wraparound. At 1000x load, the MVCC cleanup cost can exceed the transaction processing cost itself.

---

### ⚖️ Comparison Table

| Isolation Level    | Dirty Read    | Non-Repeatable Read | Phantom Read | Throughput |
| ------------------ | ------------- | ------------------- | ------------ | ---------- |
| READ UNCOMMITTED   | Possible      | Possible            | Possible     | Highest    |
| **READ COMMITTED** | **Prevented** | **Possible**        | **Possible** | **High**   |
| REPEATABLE READ    | Prevented     | Prevented           | Possible\*   | Medium     |
| SERIALIZABLE       | Prevented     | Prevented           | Prevented    | Lower      |

\*MySQL InnoDB REPEATABLE READ prevents phantoms via gap locks; PostgreSQL does not prevent all phantoms at REPEATABLE READ.

How to choose: Use READ COMMITTED for most web application reads (default in PostgreSQL). Use REPEATABLE READ or SERIALIZABLE for financial read-modify-write cycles, reservation systems, or any logic where reading the same data twice must return the same result.

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                     |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SERIALIZABLE isolation means transactions run one at a time | Modern SSI (PostgreSQL) runs transactions concurrently and only aborts on detected serializability violations - throughput is much higher than "one at a time"              |
| READ COMMITTED is unsafe for production                     | READ COMMITTED is the production default for most applications and is safe for most read-only queries; only read-modify-write cycles require higher isolation               |
| MVCC means no locking                                       | MVCC eliminates reader-writer lock contention but write-write conflicts still require row-level locks; SELECT FOR UPDATE still acquires locks under MVCC                    |
| Higher isolation level always means correct results         | Higher isolation prevents anomalies but doesn't fix application logic bugs; a SERIALIZABLE transaction can still compute the wrong result if the application logic is wrong |

---

### 🚨 Failure Modes & Diagnosis

**1. Lost Update Under READ COMMITTED**

**Symptom:** Account balance lower than expected; inventory count wrong; concurrent updates "disappear"; no errors logged.

**Root Cause:** Two transactions read the same row, both compute a new value based on the old value, both write - the second write overwrites the first. Known as the "lost update" anomaly; permitted at READ COMMITTED.

**Diagnostic:**

```sql
-- Detect suspicious balance discrepancies
SELECT account_id,
       SUM(amount) as expected_balance,
       (SELECT balance FROM accounts
        WHERE id = t.account_id) as actual_balance
FROM transactions t
GROUP BY account_id
HAVING expected_balance != actual_balance;
```

**Fix:**

```sql
-- Option 1: Use SELECT FOR UPDATE (pessimistic lock)
BEGIN;
SELECT balance FROM accounts
WHERE id = 42 FOR UPDATE; -- acquires row lock
UPDATE accounts SET balance = balance - 100 WHERE id = 42;
COMMIT;

-- Option 2: Use atomic UPDATE (no read needed)
UPDATE accounts
SET balance = balance - 100
WHERE id = 42 AND balance >= 100;
-- Check rows affected = 1; if 0, balance was insufficient
```

**Prevention:** For read-modify-write cycles, always use `SELECT FOR UPDATE` or atomic `UPDATE ... WHERE condition` patterns. Never read then write without locking.

---

**2. Phantom Read Breaking a Constraint Check**

**Symptom:** Business rule violated despite being checked in application code - e.g., maximum 3 concurrent reservations per user, but 4 exist.

**Root Cause:** Application read the count (saw 2), decided to insert (count < 3), committed - but between the count and the insert, another transaction inserted a 3rd reservation. Now 4 exist.

**Diagnostic:**

```sql
-- Find users violating the max-reservation rule
SELECT user_id, COUNT(*) as reservation_count
FROM reservations
WHERE status = 'ACTIVE'
GROUP BY user_id
HAVING COUNT(*) > 3;
```

**Fix:**

```sql
-- Use SERIALIZABLE to prevent phantom reads
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
SELECT COUNT(*) FROM reservations
WHERE user_id = 42 AND status = 'ACTIVE';
-- If count < 3, insert
INSERT INTO reservations (...) VALUES (...);
COMMIT;
-- Concurrent transaction doing the same will get serialization error
-- and must retry
```

**Prevention:** For any "count then insert" business logic, use SERIALIZABLE isolation or advisory locks.

---

**3. PostgreSQL MVCC Table Bloat**

**Symptom:** Table size grows unboundedly; query performance degrades; `pg_relation_size()` returns unexpectedly large values; VACUUM runs but table doesn't shrink.

**Root Cause:** Long-running transactions hold back MVCC cleanup - PostgreSQL can't vacuum dead tuples that are still visible to the oldest active transaction. `xmin` horizon is stuck; dead versions accumulate.

**Diagnostic:**

```sql
-- Find oldest blocking transaction
SELECT pid, now() - xact_start AS age,
       query, state
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start;

-- Check table dead tuple count
SELECT relname, n_dead_tup, n_live_tup,
       last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

**Fix:** Kill or complete long-running transactions. Run `VACUUM ANALYZE table_name`. Configure `autovacuum_vacuum_scale_factor` lower (e.g., 0.01) for high-write tables.

**Prevention:** Set `idle_in_transaction_session_timeout` to terminate abandoned transactions. Monitor `pg_stat_activity` for long-lived transactions in CI and production.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ACID` - isolation is the "I"; understand the full model
- `Transaction` - isolation is a property of transactions; understand transaction scope

**Builds On This (learn these next):**

- `Isolation Levels` - the configurable trade-offs within isolation: READ COMMITTED through SERIALIZABLE
- `MVCC` - the primary mechanism modern databases use to implement isolation
- `Locking (Row, Table, Gap, Next-Key)` - the pessimistic alternative to MVCC for isolation

**Alternatives / Comparisons:**

- `Dirty Read` - the anomaly that lowest isolation level (READ UNCOMMITTED) allows
- `Phantom Read` - the anomaly that only SERIALIZABLE prevents
- `Optimistic Locking` - application-level isolation using version numbers instead of DB locks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Concurrent transactions don't see each    │
│              │ other's uncommitted work                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without it: lost updates, dirty reads,    │
│ SOLVES       │ phantom data - silent data corruption     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Isolation is a spectrum - choose the      │
│              │ level that matches your anomaly tolerance │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any read-modify-write cycle: REPEATABLE   │
│              │ READ or SERIALIZABLE                      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ SERIALIZABLE for read-only analytics -    │
│              │ READ COMMITTED is sufficient and faster   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Correctness vs concurrency / throughput   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your own private view of the world       │
│              │  until you're ready to publish"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Isolation Levels → MVCC → Locking         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - System Interaction) A PostgreSQL database uses the default READ COMMITTED isolation level. Two microservices simultaneously execute a "transfer funds" operation between the same two accounts. Service A transfers $100 from Account 1 to Account 2. Service B transfers $200 from Account 1 to Account 3. Both services use the pattern: read balance, subtract, write new balance. Trace exactly what can go wrong, name the specific isolation anomaly, and explain precisely what isolation level and SQL pattern would fix it.

**Q2.** (TYPE B - Scale Thought Experiment) A high-traffic e-commerce platform processes 50,000 concurrent transactions per second using PostgreSQL with SERIALIZABLE isolation. The marketing team requests a daily report that runs a 10-minute analytical query on the orders table. What happens to the MVCC bloat, VACUUM, and serialization abort rate while this query runs - and what is the correct architecture to serve both the OLTP transactions and the analytical report without degrading either?
