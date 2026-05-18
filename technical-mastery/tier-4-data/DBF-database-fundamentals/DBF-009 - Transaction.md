---
version: 2
layout: default
title: "Transaction"
parent: "Database Fundamentals"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/databases/transaction/
id: DBF-023
category: Database Fundamentals
difficulty: ★☆☆
depends_on: SQL, Database Fundamentals
used_by: ACID, Isolation Levels, Connection Pooling
related: Commit, Rollback, Savepoint
tags:
  - database
  - transactions
  - reliability
  - foundational
---

⚡ TL;DR - A database transaction is a group of SQL operations treated as a single unit of work - the group either fully succeeds or fully fails, with no partial results ever persisting.

| #416            | Category: Database Fundamentals            | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | SQL, Database Fundamentals                 |                 |
| **Used by:**    | ACID, Isolation Levels, Connection Pooling |                 |
| **Related:**    | Commit, Rollback, Savepoint                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Transferring money between two bank accounts requires two separate SQL statements: `UPDATE accounts SET balance = balance - 500 WHERE id = 1` and `UPDATE accounts SET balance = balance + 500 WHERE id = 2`. Without transactions, each statement is independent. A server crash, network failure, or application exception between statements leaves Account 1 debited and Account 2 unchanged. $500 has vanished from the system. There is no built-in way to "undo" the first UPDATE now that the second never ran.

**THE BREAKING POINT:**
Any operation that must change multiple rows or tables simultaneously is vulnerable. Order placement (create order + update inventory + record payment) has three critical writes. Any failure between them creates inconsistent state. Without transactions, every multi-step database operation is a potential data corruption event waiting for the next server hiccup.

**THE INVENTION MOMENT:**
"This is exactly why database Transactions were created."

---

### 📘 Textbook Definition

A **database transaction** is a sequence of one or more SQL operations that are executed as a single logical unit of work, governed by the ACID properties (Atomicity, Consistency, Isolation, Durability). A transaction begins explicitly with `BEGIN` (or implicitly with the first DML statement in auto-commit-disabled mode), proceeds through a sequence of SQL statements, and ends with either `COMMIT` (permanently applying all changes) or `ROLLBACK` (reverting all changes to the state at the `BEGIN`). Savepoints allow partial rollback within a transaction without rolling back the entire unit of work.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A transaction wraps multiple database operations into one - all succeed together or all fail together.

**One analogy:**

> A transaction is like loading a dishwasher and running it. You load all the dishes (multiple operations), then press Start (COMMIT). Either all dishes get washed - or you cancel (ROLLBACK) and all dishes go back to being dirty. The machine never finishes washing half the dishes and leaves the rest dirty. It's all or nothing.

**One insight:**
Most databases run in "auto-commit" mode by default - every single SQL statement is its own transaction, auto-committed immediately. This is convenient for single-row operations but silently wrong for any multi-step operation that must be atomic. Developers who don't understand transactions write multi-statement code in auto-commit mode and discover partial-state corruption in production.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A transaction defines an atomic boundary - all changes within it are provisional until COMMIT.
2. The database tracks every change since `BEGIN` so it can reverse them on `ROLLBACK`.
3. Concurrent transactions are isolated from each other's in-progress work.
4. Once committed, changes are durable and cannot be uncommitted by a subsequent crash.

**DERIVED DESIGN:**
The transaction manager maintains a transaction ID (`xid`) for each active transaction. Every row modification records which transaction made the change. The undo log tracks the "before" values of every modified row. On COMMIT, the transaction's undo log is discarded (changes are permanent). On ROLLBACK, the undo log is replayed in reverse to restore original values.

The WAL (Write-Ahead Log) records all changes and commits. On crash, the database replays the WAL: transactions with a COMMIT record are re-applied; those without are rolled back using undo data.

**THE TRADE-OFFS:**

**Gain:** Multi-step mutations are safe. Code can assume that either all changes took effect or none did - no defensive coding for partial state.

**Cost:** Transactions hold resources (locks, undo log space) for their duration. Long-running transactions block other transactions, accumulate undo log, and delay MVCC cleanup. Transactions across distributed systems (2PC) add coordination latency and failure risk.

---

### 🧪 Thought Experiment

**SETUP:**
An airline booking system: check seat availability, create a booking record, update seat count - three operations.

**WITHOUT TRANSACTIONS:**

- Check: 1 seat available.
- Insert booking: success.
- Update seat count: server crashes.
- Result: a booking record exists, but seat count still shows 1 (it was never decremented). Next customer also books the same seat. Two bookings, one seat.

**WITH TRANSACTIONS:**

- BEGIN
- Check: 1 seat available.
- Insert booking: staged (not committed).
- Update seat count: staged.
- Server crashes.
- On restart: transaction has no COMMIT record in WAL.
- Rollback applied: booking record removed, seat count unchanged.
- Result: database looks exactly as before. Next customer sees 1 seat available - accurate, bookable, correct.

**THE INSIGHT:**
The transaction doesn't prevent the crash - it makes the crash irrelevant. Either all three operations take effect (when committed) or none of them do (when crashed/rolled back). The application never has to reason about partial states.

---

### 🧠 Mental Model / Analogy

> A transaction is like a shopping cart. You add items to your cart (BEGIN + SQL writes) - but nothing is final until you click "Place Order" (COMMIT). If your browser crashes while shopping, nothing was ordered - the cart is simply empty when you return (ROLLBACK). The store's inventory is untouched. Your credit card wasn't charged. Everything is exactly as it was before you started shopping.

- "Adding items to cart" → SQL writes within a transaction (provisional changes)
- "Clicking Place Order" → COMMIT (all changes made permanent)
- "Browser crash mid-checkout" → crash/exception → ROLLBACK
- "Empty cart on return" → database state unchanged after rollback
- "Inventory update + charge + order creation" → multi-statement atomicity

Where this analogy breaks down: unlike a shopping cart, a database transaction has strict time limits - long-running transactions block others (locks) or accumulate bloat (MVCC).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A transaction lets you say "these database changes go together." Either they all happen or none of them do. If anything goes wrong in the middle, the database automatically undoes everything back to where it started.

**Level 2 - How to use it (junior developer):**
Use `BEGIN` / `COMMIT` / `ROLLBACK` in SQL. In Java with Spring, add `@Transactional` to your service method - Spring automatically wraps it in a transaction, committing on success and rolling back on `RuntimeException`. Remember: `@Transactional` doesn't roll back on checked exceptions by default.

**Level 3 - How it works (mid-level engineer):**
The database assigns a transaction ID on `BEGIN`. All writes are recorded in the undo log with the old values. The WAL receives a COMMIT record on commit. On crash: WAL is scanned from the last checkpoint; committed transactions are replayed; uncommitted ones are rolled back via undo log. MVCC uses the transaction ID to determine which row versions are visible to which transactions - `xmin` (transaction that created the row version) and `xmax` (transaction that deleted it) control visibility.

**Level 4 - Why it was designed this way (senior/staff):**
The boundary between "implicit transaction per statement" (auto-commit) and "explicit multi-statement transaction" is a design tension. PostgreSQL wraps every statement in an implicit transaction even in auto-commit mode - a single-statement transaction is still ACID-compliant. MySQL's InnoDB does the same. The cost of auto-commit is one fsync per statement - high for write-heavy workloads. Explicit transaction batching amortises this: 1,000 inserts in one transaction = 1 fsync vs. 1,000 fsyncs in auto-commit mode. This is why bulk import operations wrap thousands of rows per transaction rather than committing after every row.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ TRANSACTION LIFECYCLE                        │
├──────────────────────────────────────────────┤
│                                              │
│  BEGIN (or first DML in non-autocommit)      │
│    → Assign Transaction ID (xid)             │
│    → Start tracking changes                  │
│                                              │
│  SQL Statement 1: UPDATE accounts ...        │
│    → Old value written to UNDO LOG           │
│    → New value written to BUFFER POOL        │
│    → WAL entry written for statement         │
│                                              │
│  SQL Statement 2: INSERT INTO orders ...     │
│    → Same: undo log + buffer + WAL           │
│                                              │
│  COMMIT:                                     │
│    → COMMIT record written to WAL            │
│    → fsync WAL to disk                       │
│    → Release locks                           │
│    → Changes now visible to other txns       │
│    → Undo log cleaned up (eventually)        │
│                                              │
│  ROLLBACK (or crash without COMMIT):         │
│    → Read UNDO LOG in reverse                │
│    → Restore each row's original value       │
│    → Release locks                           │
│    → Transaction ID recycled                 │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
App code → BEGIN → SQL writes (undo log + WAL)
→ [TRANSACTION ← YOU ARE HERE: atomic boundary]
→ COMMIT → fsync WAL → changes visible
→ Locks released → undo log eventually purged
```

**FAILURE PATH:**

```
Exception thrown mid-transaction → ROLLBACK
→ Undo log reversed → Original state restored
→ App handles exception → Can safely retry
```

**WHAT CHANGES AT SCALE:**
At high volume, transaction throughput is limited by fsync latency × transactions/second. Group commit (PostgreSQL, MySQL) batches multiple transactions' WAL writes into one fsync, achieving 10,000+ commits per second on NVMe storage. Long-running transactions at scale create MVCC bloat (PostgreSQL) or lock contention (MySQL), degrading throughput for all concurrent transactions. The scaling rule: keep transactions short - open late, close early.

---

### ⚖️ Comparison Table

| Transaction Scope                  | Consistency               | Complexity | Best For                                      |
| ---------------------------------- | ------------------------- | ---------- | --------------------------------------------- |
| **Single-statement (auto-commit)** | Per-statement             | None       | Simple single-row CRUD                        |
| **Multi-statement explicit**       | Across all statements     | Low        | Business operations (order, transfer)         |
| **Savepoints**                     | Partial rollback possible | Medium     | Nested operations needing partial undo        |
| **Distributed (2PC)**              | Cross-service             | High       | Cross-database operations (avoid if possible) |
| **SAGA**                           | Eventual                  | High       | Distributed microservice workflows            |

How to choose: Use explicit multi-statement transactions for any operation requiring atomicity across multiple tables. Use distributed transactions (2PC/SAGA) only when data truly cannot be co-located - prefer designing data locality to avoid distributed transactions.

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                         |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Auto-commit means transactions are disabled   | Auto-commit wraps every statement in its own implicit transaction - each single statement is still fully ACID-compliant                                                         |
| @Transactional always wraps the entire method | @Transactional uses a proxy - the transaction only starts when the method is called through the proxy; self-invocation (`this.method()`) bypasses the proxy and the transaction |
| Transactions prevent all concurrency issues   | Transactions + default READ COMMITTED isolation still allow dirty reads and lost updates; the isolation level determines which anomalies are prevented                          |
| Longer transactions = more durability         | Transaction duration has no relationship to durability; a 10ms transaction and a 10-hour transaction are equally durable once committed                                         |

---

### 🚨 Failure Modes & Diagnosis

**1. Open Transaction Leaking - Connection Pool Exhaustion**

**Symptom:** Application hangs; connection pool shows 0 available connections; some connections have been "in use" for hours; new requests time out waiting for a connection.

**Root Cause:** A transaction was begun but never committed or rolled back (exception swallowed, code path with missing COMMIT, long-running report running in a transaction). The database connection is occupied until the transaction closes.

**Diagnostic:**

```sql
-- PostgreSQL: find long-running transactions
SELECT pid,
       now() - xact_start AS tx_duration,
       state, query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND state != 'idle'
ORDER BY tx_duration DESC;

-- Kill blocking transaction
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE now() - xact_start > interval '10 minutes';
```

**Fix:** Set `idle_in_transaction_session_timeout = '5min'` in PostgreSQL. Use try-finally (or try-with-resources in Java) to guarantee transaction close even on exceptions.

**Prevention:** Never perform long-running external operations (HTTP calls, file I/O) inside an open database transaction. Use `@Transactional` with short-running database operations only.

---

**2. Transaction Too Large - Rollback Taking Longer Than Forward**

**Symptom:** A failed batch operation takes 30 minutes to roll back after a 30-minute run; database connections blocked during rollback; undo tablespace exhausted (MySQL).

**Root Cause:** A single transaction modified millions of rows. Rollback must reverse every change via the undo log - same I/O cost as the forward transaction.

**Diagnostic:**

```sql
-- MySQL: check undo log size and rollback progress
SHOW ENGINE INNODB STATUS\G
-- Look for "TRANSACTION" section with "ROLLING BACK" status
-- "History list length" shows accumulated undo log size
```

**Fix:** Split large batch operations into smaller transactions of 1,000–10,000 rows each. Accept that partial failure requires resumable batch logic rather than a single atomic rollback.

**Prevention:** Never process more than ~10,000 rows per transaction in batch jobs. Design batches to be idempotent (safe to re-run) rather than relying on a single large transaction for atomicity.

---

**3. Nested @Transactional with Propagation.REQUIRES_NEW Not Rolling Back Parent**

**Symptom:** Outer method's transaction committed; inner method with `REQUIRES_NEW` rolled back; but partially committed outer transaction has inconsistent data.

**Root Cause:** `Propagation.REQUIRES_NEW` suspends the outer transaction and starts a completely independent inner transaction. If the inner transaction commits and the outer subsequently fails, the inner's changes are already committed - they won't roll back with the outer.

**Diagnostic:**

```java
// This is the problematic pattern
@Transactional
public void outerOp() {
    repo.saveOrder(order);   // outer tx
    auditService.log(order); // REQUIRES_NEW - separate tx
    // If exception here: order rolled back, audit LOG stays
    throw new RuntimeException("Payment failed");
}

@Transactional(propagation = REQUIRES_NEW)
public void log(Order order) {
    auditRepo.save(new AuditEntry(order)); // independent commit
}
```

**Fix:** Use `REQUIRES_NEW` only for operations that must always commit regardless of outer outcome (audit logs, retry counters). If the inner operation must be part of the outer's atomicity, use the default `REQUIRED` propagation.

**Prevention:** Document propagation decisions explicitly. `REQUIRES_NEW` is a deliberate break in atomicity - treat it as such.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SQL` - transactions wrap SQL DML statements; understand SELECT, INSERT, UPDATE, DELETE
- `Database Fundamentals` - understand what a relational database is before understanding transactions

**Builds On This (learn these next):**

- `ACID` - the four properties that define what transactions guarantee
- `Isolation Levels` - the trade-off settings that control how transactions interact concurrently
- `Connection Pooling (DB)` - transactions occupy connections; connection pool management is critical

**Alternatives / Comparisons:**

- `Commit / Rollback / Savepoint` - the SQL commands that control transaction lifecycle
- `SAGA Pattern` - the distributed systems alternative to spanning a transaction across services
- `Optimistic Locking` - an application-level pattern that achieves partial transaction isolation without DB-level locks

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A group of SQL operations treated as     │
│              │ one indivisible unit of work             │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-step mutations leave partial state │
│ SOLVES       │ on crash/error without atomicity         │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Auto-commit mode = every statement is its│
│              │ own transaction; wrap multi-step ops     │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Any multi-table or multi-row mutation    │
│              │ that must be atomic (transfer, order)    │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Read-only operations - unnecessary       │
│              │ overhead without benefit                 │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Safety vs resource hold time             │
│              │ (keep transactions short)                │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "All or nothing - never half done"       │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ ACID → Isolation Levels → MVCC           │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - System Interaction) A Spring `@Transactional` service method performs 3 operations: save an Order, call an external payment API, save a Payment record. The payment API call succeeds but takes 8 seconds. During those 8 seconds, the database connection is held in an open transaction. At 100 concurrent users doing this, what happens to the connection pool, the database lock table, and the MVCC bloat - and how would you redesign this flow to eliminate the problem?

**Q2.** (TYPE C - Design Trade-off) A batch job must migrate 50 million rows from one table to another. Option A: one giant transaction for all 50 million rows. Option B: one transaction per row (auto-commit). Option C: one transaction per 10,000 rows. Compare all three on rollback safety, undo log size, fsync count, failure recoverability, and runtime. Which is correct and why?
