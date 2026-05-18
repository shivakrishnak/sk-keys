---
version: 2
layout: default
title: "ACID"
parent: "Database Fundamentals"
grand_parent: "Technical Mastery"
nav_order: 6
permalink: /technical-mastery/databases/acid/
id: DBF-039
category: Database Fundamentals
difficulty: ★☆☆
depends_on: Transaction, Relational Database
used_by: Isolation Levels, MVCC, WAL
related: BASE, CAP Theorem, Eventual Consistency
tags:
  - database
  - transactions
  - reliability
  - foundational
---

⚡ TL;DR - ACID is the four-property guarantee that makes database transactions reliable: every operation either fully succeeds or fully disappears, leaving the database consistent.

| #411            | Category: Database Fundamentals         | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | Transaction, Relational Database        |                 |
| **Used by:**    | Isolation Levels, MVCC, WAL             |                 |
| **Related:**    | BASE, CAP Theorem, Eventual Consistency |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A bank runs a transfer: debit $500 from Account A, credit $500 to Account B. Halfway through the server crashes. Account A has been debited. Account B has not been credited. $500 has vanished from the system. The bank has no way to know whether to retry (risk doubling the debit) or abandon (leave the money gone). Every operation that touches multiple records is a potential money-losing race condition.

**THE BREAKING POINT:**
At scale, without transactional guarantees, two users simultaneously booking the last seat on a flight both see "1 seat available," both confirm, both get charged - and both show up at the gate. Without atomicity and isolation working together, every concurrent write becomes a data integrity lottery.

**THE INVENTION MOMENT:**
"This is exactly why ACID was created."

---

### 📘 Textbook Definition

**ACID** is an acronym describing four properties that database transactions must guarantee to ensure data validity: **Atomicity** (all operations in a transaction succeed or none do), **Consistency** (the database moves from one valid state to another), **Isolation** (concurrent transactions don't interfere with each other), and **Durability** (committed transactions survive failures). These four properties together make database transactions a reliable unit of work that can be reasoned about in a concurrent, failure-prone environment.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ACID means your database changes are all-or-nothing, valid, invisible until done, and permanent.

**One analogy:**

> Imagine writing a cheque. Either the entire transaction - you sign it, the bank processes it, and money moves - happens completely, or if anything fails (no funds, wrong signature) nothing happens at all. The bank's ledger is never left in a half-written state. ACID is that guarantee for databases.

**One insight:**
ACID is not a single feature - it's four separate, complementary guarantees that together make concurrent multi-step database operations safe. You can't have one without the others being meaningful. Atomicity without Isolation means concurrent transactions can still corrupt data even if each individual transaction completes fully.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A transaction is the unit of work - it either completes entirely or has no effect.
2. The database must enforce its own integrity rules (constraints, foreign keys) at transaction boundaries.
3. Concurrent transactions must not produce results that would be impossible with serial execution.
4. Committed data must survive crashes, power failures, and restarts.

**DERIVED DESIGN:**
Given these invariants, a database must maintain:

- A **transaction log** (WAL) to reconstruct committed state after crashes (Durability + Atomicity)
- A **locking or MVCC mechanism** to prevent concurrent transactions from seeing each other's in-progress writes (Isolation)
- **Constraint checking** at commit time to reject transactions that would violate referential integrity, uniqueness, or domain rules (Consistency)

The database can't just "try and see" - it must track every change, buffer it in memory, write it to a durable log before confirming success, and be able to roll back if anything fails.

**THE TRADE-OFFS:**

**Gain:** Predictable, correct behaviour under concurrent access and system failures. Applications can reason about database state without defensive coding for partial writes.

**Cost:** Overhead of logging, locking, and MVCC versioning reduces raw write throughput. Highly contentious workloads suffer lock contention. This is why NoSQL systems offering BASE (Basically Available, Soft state, Eventually consistent) exist - they trade ACID guarantees for throughput and availability.

---

### 🧪 Thought Experiment

**SETUP:**
Two users simultaneously book the last ticket to a concert. The system has 1 ticket available. Both requests arrive at the same millisecond.

**WHAT HAPPENS WITHOUT ACID:**

- User A reads: tickets_available = 1. ✅
- User B reads: tickets_available = 1. ✅ (same row, same value)
- User A writes: tickets_available = 0, creates booking.
- User B writes: tickets_available = 0, creates booking.
- Result: 2 bookings created for 1 ticket. $200 taken, 1 angry customer.

**WHAT HAPPENS WITH ACID:**

- User A begins transaction, reads and locks tickets_available = 1.
- User B begins transaction, attempts to read - must wait (Isolation).
- User A decrements to 0, creates booking, commits. Lock released.
- User B resumes, reads tickets_available = 0.
- User B's transaction rolls back: no ticket, no charge (Atomicity).
- Result: 1 booking, 1 happy customer.

**THE INSIGHT:**
ACID doesn't just make individual writes reliable - it makes concurrent writes safe. Without Isolation working alongside Atomicity, you still get data corruption even if each individual transaction "succeeds."

---

### 🧠 Mental Model / Analogy

> A database transaction is like a surgery procedure. The surgeon either performs the complete operation successfully, or if something goes wrong mid-surgery, the patient is stabilised back to pre-surgery state. The operating room is sealed during the procedure (no visitors mid-surgery). And the completed surgery is permanent - it doesn't "un-happen" after the patient wakes up.

- "Complete operation or stabilise" → Atomicity - all or nothing
- "Patient's health must improve or stay same" → Consistency - valid state to valid state
- "Sealed operating room, no outside interference" → Isolation - concurrent transactions don't interfere
- "Completed surgery is permanent" → Durability - committed writes survive restarts

Where this analogy breaks down: unlike surgery, database rollback is instantaneous and complete - there's no "partial recovery" state.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
ACID is a promise your database makes about every change: either all of it happens, or none of it does; it never breaks its own rules; two people changing data at the same time can't corrupt each other's work; and once saved, it stays saved even if the server crashes.

**Level 2 - How to use it (junior developer):**
Wrap related database operations in a transaction (`BEGIN` / `COMMIT` / `ROLLBACK`). If any step fails, call `ROLLBACK` and the database undoes everything since `BEGIN`. The database engine enforces Consistency via constraints (NOT NULL, UNIQUE, FOREIGN KEY). Isolation is automatic - you choose the level via `SET TRANSACTION ISOLATION LEVEL`.

**Level 3 - How it works (mid-level engineer):**
Atomicity and Durability are implemented via WAL (Write-Ahead Log) - changes are written to a durable log before being applied to the actual data pages. On crash, the database replays the log to recover committed transactions and rolls back incomplete ones. Isolation is implemented via MVCC (in PostgreSQL, MySQL InnoDB) or locking (traditional engines) - readers see a consistent snapshot without blocking writers. Consistency is enforced by the engine at commit time via constraint validation.

**Level 4 - Why it was designed this way (senior/staff):**
ACID's cost is the reason BASE and eventual-consistency systems exist. The "I" in ACID - Isolation - is the most expensive guarantee. Full serializability (the strongest isolation level) requires either global locking or expensive conflict detection. Most databases default to READ COMMITTED (not SERIALIZABLE) because serializable throughput is 50–90% lower under write-heavy workloads. Distributed ACID (spanning multiple nodes) requires 2-Phase Commit (2PC), which introduces coordinator failure risk and latency. Google Spanner achieves distributed ACID using TrueTime - GPS and atomic clocks to bound clock uncertainty. This is why distributed transactions are avoided unless absolutely necessary.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ ACID TRANSACTION LIFECYCLE                   │
├──────────────────────────────────────────────┤
│                                              │
│  BEGIN TRANSACTION                           │
│    │                                         │
│    ├── Read data (MVCC snapshot or locks)    │
│    ├── Modify data in memory buffer          │
│    ├── Validate constraints                  │
│    │     └── If violated → ROLLBACK          │
│    │                                         │
│  COMMIT                                      │
│    │                                         │
│    ├── 1. Write to WAL (durable log)         │
│    │       └── fsync to disk ← Durability   │
│    ├── 2. Apply changes to data pages        │
│    │       └── In memory / background flush  │
│    └── 3. Release locks / MVCC cleanup       │
│                                              │
│  ON CRASH (before commit):                   │
│    WAL shows transaction incomplete          │
│    → Engine rolls back on restart (Atomicity)│
│                                              │
│  ON CRASH (after WAL written, before pages): │
│    WAL shows transaction committed           │
│    → Engine replays WAL on restart           │
│    → Durability guaranteed                   │
└──────────────────────────────────────────────┘
```

The WAL is the backbone of both Atomicity and Durability. Because the log is written before data pages are modified, the database can always determine the correct state after a crash: if the log shows "COMMIT," replay the changes; if not, undo them.

Isolation is layered on top - MVCC lets readers see a consistent snapshot of the database as of their transaction start time, without blocking writers or being blocked by them.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Client → BEGIN → Read/Write operations
→ [ACID ← YOU ARE HERE] → Constraint check
→ WAL write → COMMIT → Changes visible
```

**FAILURE PATH:**

```
Crash during write → WAL incomplete
→ Restart reads WAL → Transaction not committed
→ Rollback applied → Database at pre-transaction state
→ Client receives error / connection drop
```

**WHAT CHANGES AT SCALE:**
At high write volumes, WAL fsyncs become the bottleneck - group commit batches multiple transactions' WAL entries into one fsync to amortise the disk write cost. Under extremely high concurrency, lock contention or MVCC bloat (long-running transactions holding old row versions) degrades performance. Distributed ACID across shards requires 2PC, which is avoided in most web-scale systems by designing transactions to stay within a single partition.

---

### ⚖️ Comparison Table

| Model    | Consistency             | Availability | Partition Tolerance | Best For                                                   |
| -------- | ----------------------- | ------------ | ------------------- | ---------------------------------------------------------- |
| **ACID** | Strong                  | Lower        | Lower               | Financial systems, bookings, any correctness-critical data |
| BASE     | Eventual                | High         | High                | Social feeds, analytics, high-throughput writes            |
| SAGA     | Eventual (compensating) | High         | High                | Distributed long-running business transactions             |
| 2PC      | Strong                  | Low          | Low                 | Cross-node distributed ACID (rarely used at scale)         |

How to choose: Use ACID when data correctness is non-negotiable (money, inventory, reservations). Use BASE/eventual when availability and throughput outweigh strict consistency (user activity feeds, read-heavy analytics).

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                           |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ACID means the database is always consistent | Consistency in ACID means the database enforces its own defined constraints - it doesn't guarantee application-level logical correctness; your application can still corrupt data while respecting DB constraints |
| ACID transactions are slow                   | The overhead is real but manageable; most OLTP workloads run thousands of ACID transactions per second on commodity hardware                                                                                      |
| Rollback undoes the physical disk writes     | Rollback uses the undo log to logically reverse changes; data pages may already be written to disk - undo reconstructs the old values                                                                             |
| NoSQL databases don't support ACID           | Many modern NoSQL databases (MongoDB 4.0+, DynamoDB with transactions) support ACID transactions; it's a spectrum, not a binary choice                                                                            |

---

### 🚨 Failure Modes & Diagnosis

**1. Long-Running Transaction Holding Locks**

**Symptom:** Application threads stuck waiting; `SHOW PROCESSLIST` shows queries waiting `Lock wait timeout exceeded`; connection pool exhausted.

**Root Cause:** A transaction was opened, performed some writes, and then stalled (application bug, slow external call mid-transaction) - holding row locks that block other transactions.

**Diagnostic:**

```sql
-- PostgreSQL: find long-running transactions
SELECT pid, now() - xact_start AS duration,
       query, state
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND state != 'idle'
ORDER BY duration DESC;
```

**Fix:** Set `statement_timeout` and `idle_in_transaction_session_timeout` in PostgreSQL, or `innodb_lock_wait_timeout` in MySQL. Never make external calls (HTTP, messaging) inside a database transaction.

**Prevention:** Keep transactions short - open late, commit early. Separate business logic from transactional data access.

---

**2. Violated Durability - `fsync` Disabled**

**Symptom:** Data loss after crash; recent commits not present after restart.

**Root Cause:** `fsync=off` or `synchronous_commit=off` in PostgreSQL - WAL entries are not flushed to disk before `COMMIT` returns success. The OS may buffer WAL in memory, losing it on crash.

**Diagnostic:**

```bash
# Check PostgreSQL sync settings
psql -c "SHOW fsync;"
psql -c "SHOW synchronous_commit;"
# Both should be 'on' for full durability guarantees
```

**Fix:** Never disable `fsync` on production databases. `synchronous_commit=off` is acceptable only for non-critical data (logging, analytics) where some data loss is tolerable.

**Prevention:** Review PostgreSQL/MySQL configuration in infrastructure-as-code. Include a durability settings check in database provisioning runbooks.

---

**3. Phantom Reads Breaking Business Logic**

**Symptom:** A query run twice in the same transaction returns different rows - new rows appear mid-transaction.

**Root Cause:** Using READ COMMITTED or REPEATABLE READ isolation level, which doesn't prevent phantom reads (new rows inserted by concurrent transactions becoming visible).

**Diagnostic:**

```sql
-- Session 1: Begin transaction, read rows
BEGIN;
SELECT COUNT(*) FROM orders
WHERE status = 'PENDING'; -- returns 5

-- Session 2 (concurrent): inserts new pending order
INSERT INTO orders (status) VALUES ('PENDING'); COMMIT;

-- Session 1: same query, different result (phantom)
SELECT COUNT(*) FROM orders
WHERE status = 'PENDING'; -- returns 6 at READ COMMITTED
```

**Fix:**

```sql
-- Use SERIALIZABLE isolation to prevent phantoms
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN;
-- Both reads now return same result
```

**Prevention:** Understand which isolation level your business logic requires. Use SERIALIZABLE for read-modify-write cycles that must be consistent.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Transaction` - ACID describes the guarantees of a transaction; understand what a transaction is first
- `Relational Database` - ACID originated in relational systems; understand the relational model

**Builds On This (learn these next):**

- `Isolation Levels` - the four isolation levels (READ UNCOMMITTED through SERIALIZABLE) define trade-offs within ACID's "I"
- `MVCC` - the mechanism most modern databases use to implement Isolation without full locking
- `WAL (Write-Ahead Log)` - the mechanism that implements Atomicity and Durability

**Alternatives / Comparisons:**

- `BASE` - Basically Available, Soft state, Eventually consistent; trades ACID for availability and throughput
- `CAP Theorem` - explains why distributed systems can't have all three: Consistency, Availability, Partition Tolerance
- `SAGA Pattern` - achieves eventual consistency across distributed services without distributed ACID transactions

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 4 guarantees: Atomic, Consistent,        │
│              │ Isolated, Durable                        │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Concurrent writes + crashes corrupt data │
│ SOLVES       │ without all-or-nothing, isolated ops     │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Isolation is the most expensive of the   │
│              │ four - it's why NoSQL/BASE exist         │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Data correctness is non-negotiable:      │
│              │ finance, inventory, reservations         │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Throughput > correctness: analytics,     │
│              │ activity feeds, write-heavy logging      │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Correctness vs throughput / availability │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "All four or it's not a transaction"     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Isolation Levels → MVCC → WAL            │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE F - Comparison Depth) Both ACID and the SAGA pattern claim to handle transaction failures safely across multiple operations. What is the precise condition that makes ACID the correct choice and SAGA the wrong choice - and vice versa? Consider a scenario where a single order creation involves a payment service, an inventory service, and a notification service, each with its own database.

**Q2.** (TYPE B - Scale Thought Experiment) A PostgreSQL database processing 50,000 write transactions per second has `fsync=on` and `synchronous_commit=on`. At what point does WAL flushing become the throughput bottleneck, and what three mechanisms does PostgreSQL use to mitigate this at scale without sacrificing Durability?
