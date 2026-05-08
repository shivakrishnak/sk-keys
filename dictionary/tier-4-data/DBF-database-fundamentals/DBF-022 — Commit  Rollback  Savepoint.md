---
layout: default
title: "Commit  Rollback  Savepoint"
parent: "Database Fundamentals"
nav_order: 22
permalink: /databases/commit-rollback-savepoint/
id: DBF-022
category: Database Fundamentals
difficulty: ★☆☆
depends_on: Transaction, ACID, WAL
used_by: ACID, Atomicity, Stored Procedure
related: Isolation Levels, Durability, Undo Log
tags:
  - database
  - transactions
  - reliability
  - foundational
---

# DBF-022 — Commit  Rollback  Savepoint

⚡ TL;DR — COMMIT makes a transaction's changes permanent, ROLLBACK undoes them entirely, and SAVEPOINT creates a partial rollback point within a transaction — these three commands control the lifecycle of every database transaction.

| #417            | Category: Database Fundamentals        | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------- | :-------------- |
| **Depends on:** | Transaction, ACID, WAL                 |                 |
| **Used by:**    | ACID, Atomicity, Stored Procedure      |                 |
| **Related:**    | Isolation Levels, Durability, Undo Log |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every database write is immediately permanent. There is no way to "try" a set of operations and undo them if they don't work out. A multi-step business operation — create order, charge card, update inventory — has no safe execution model. If step 2 fails, step 1 is already permanent. The only recourse is compensating writes (delete the order manually), which can themselves fail.

**THE BREAKING POINT:**
Without a way to say "I'm done and everything is correct" (COMMIT) or "something went wrong, undo everything" (ROLLBACK), every multi-step operation is either unsafe (immediate writes) or requires complex compensating logic. Savepoints add a third dimension: the ability to undo part of a complex transaction without abandoning the whole thing.

**THE INVENTION MOMENT:**
"This is exactly why COMMIT, ROLLBACK, and SAVEPOINT were created."

---

### 📘 Textbook Definition

**COMMIT** is the SQL command that permanently applies all changes made since the transaction's `BEGIN`, making them durable and visible to other transactions. **ROLLBACK** is the SQL command that reverses all changes made since `BEGIN` (or since a named savepoint), restoring the database to its pre-transaction state using the undo log. **SAVEPOINT** creates a named intermediate point within a transaction; `ROLLBACK TO savepoint_name` undoes all changes since that savepoint without affecting changes made before it, and the transaction can continue. Together, these three commands implement the transactional control language (TCL) of SQL.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
COMMIT saves your work permanently, ROLLBACK erases it completely, SAVEPOINT lets you undo just part of it.

**One analogy:**

> Video game save states. SAVEPOINT is creating a save state mid-game. ROLLBACK TO saves you back to that state if you fail. COMMIT is finishing the level and saving permanently. ROLLBACK (no savepoint) takes you all the way back to the beginning of the session. Saves let you experiment without losing all your progress.

**One insight:**
Auto-commit mode (the default in most database drivers) issues an implicit COMMIT after every single SQL statement. This means every INSERT, UPDATE, and DELETE is immediately permanent. Developers who don't know this write multi-statement "transactions" in auto-commit mode and discover they have no rollback capability when something fails mid-operation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Before COMMIT: all changes are provisional — visible to the current transaction but not to others.
2. After COMMIT: all changes are permanent — visible to all transactions, cannot be undone by ROLLBACK.
3. ROLLBACK reverses all changes to either the BEGIN point or to a named SAVEPOINT.
4. SAVEPOINTs partition a transaction into checkpointable sub-units without committing.

**DERIVED DESIGN:**
The undo log is the enabling mechanism for ROLLBACK. Every row modification writes the original value to the undo log. On ROLLBACK, the database reads the undo log in reverse and restores original values. SAVEPOINTs work by recording the "undo log position" at the savepoint — ROLLBACK TO a savepoint replays the undo log from the current position back to the savepoint's position.

COMMIT writes a COMMIT record to the WAL and fsyncs it — this is the moment durability is achieved. Before the COMMIT record is fsynced, the transaction's changes are not durable.

**THE TRADE-OFFS:**
**COMMIT:** Gain: durability + visibility. Cost: fsync I/O; changes cannot be undone.
**ROLLBACK:** Gain: clean reversal, no partial state. Cost: undo I/O proportional to transaction size.
**SAVEPOINT:** Gain: fine-grained partial rollback within a transaction. Cost: maintains additional undo log state per savepoint; complex to reason about in concurrent code.

---

### 🧪 Thought Experiment

**SETUP:**
A bank processes a batch payment: credit 100 accounts in one transaction. Accounts 1–90 succeed. Account 91 has a rule violation. Without SAVEPOINTs, the entire 100-account batch would need to roll back. With SAVEPOINTs around each account update, only account 91 is rolled back; 1–90 remain in the transaction and can be committed.

**WITHOUT SAVEPOINTS:**

- Update accounts 1–90: queued.
- Update account 91: constraint violation.
- ROLLBACK: all 90 updates reversed.
- Re-process 90 accounts manually: wasteful, slow.

**WITH SAVEPOINTS:**

```sql
BEGIN;
  SAVEPOINT batch_start;
  -- Update accounts 1..90 successfully
  SAVEPOINT before_91;
  UPDATE accounts SET balance = ... WHERE id = 91;
  -- Constraint violation caught
  ROLLBACK TO before_91;  -- Only account 91 reversed
  -- Log account 91 as failed, continue
  COMMIT;  -- Commits accounts 1–90
```

**THE INSIGHT:**
SAVEPOINTs let complex batch operations skip individual failures without losing all prior work — essential for high-throughput batch processing where individual row failures are expected and must be handled gracefully.

---

### 🧠 Mental Model / Analogy

> COMMIT / ROLLBACK / SAVEPOINT are like a chef cooking a complex dish. The chef can taste and adjust (SAVEPOINT — checkpoint mid-recipe). If one component goes wrong (ROLLBACK TO savepoint — redo just that component). When the full dish is ready, the chef serves it (COMMIT — permanent, can't be unserted). If the whole meal is wrong, the chef throws it out and starts over (ROLLBACK — full reversal).

- "Tasting mid-recipe" → SAVEPOINT (intermediate checkpoint)
- "Redoing just one component" → ROLLBACK TO savepoint
- "Serving the dish" → COMMIT (permanent, visible to diners)
- "Throwing out the meal" → ROLLBACK (full reversal to BEGIN)
- "The kitchen state before cooking" → database state at BEGIN

Where this analogy breaks down: unlike cooking, ROLLBACK is instantaneous for the database — there's no "cooking time" for reversal.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
COMMIT means "save all my database changes permanently." ROLLBACK means "undo all my changes." SAVEPOINT means "mark a point I can go back to later if part of my work goes wrong." These three commands are the on/off switches of database safety.

**Level 2 — How to use it (junior developer):**

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- Both updates permanent

-- Or on error:
ROLLBACK;  -- Both updates reversed
```

In Java/Spring: `@Transactional` handles BEGIN/COMMIT/ROLLBACK automatically — commit on method return, rollback on `RuntimeException`.

**Level 3 — How it works (mid-level engineer):**
COMMIT: flushes WAL entry with COMMIT record → fsync → releases locks → transaction ID marked complete in `pg_clog` (PostgreSQL's commit log). ROLLBACK: reads undo log in reverse order → applies before-images to rows → releases locks → marks transaction as aborted. SAVEPOINT: records current undo log tail position with a name → `ROLLBACK TO` replays undo log from current position to savepoint position only.

**Level 4 — Why it was designed this way (senior/staff):**
The SQL TCL (Transaction Control Language) commands were standardised in SQL-92 but existed in various forms since the earliest relational databases. SAVEPOINTs were a pragmatic solution to the "all-or-nothing is sometimes too coarse" problem in stored procedures and batch processing. In distributed systems, the "commit" concept extends to two-phase commit (2PC): phase 1 is "prepare" (every participant acknowledges it can commit) and phase 2 is the actual "commit" (a coordinator tells all participants to finalise). The fundamental problem with 2PC is coordinator failure between phases 1 and 2 — participants are "in doubt," holding locks indefinitely.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ COMMIT / ROLLBACK / SAVEPOINT MECHANICS      │
├──────────────────────────────────────────────┤
│                                              │
│  BEGIN ─────────────────────────────────┐   │
│    ↓                                    │   │
│  Statement 1 ── undo log position: 100  │   │
│    ↓                                    │   │
│  SAVEPOINT sp1 ── records undo pos: 100 │   │
│    ↓                                    │   │
│  Statement 2 ── undo log position: 150  │   │
│    ↓                                    │   │
│  Statement 3 ── undo log position: 200  │   │
│    ↓                                    │   │
│  ROLLBACK TO sp1:                       │   │
│    Replay undo log from pos 200 → 100   │   │
│    Stmt 2 + Stmt 3 reversed             │   │
│    Stmt 1 still in transaction          │   │
│    ↓                                    │   │
│  Statement 4 ── undo log position: 110  │   │
│    ↓                                    │   │
│  COMMIT:                                │   │
│    Write COMMIT to WAL + fsync          │   │
│    Stmt 1 + Stmt 4 permanent            │   │
│    Stmts 2+3 never committed            │   │
└─────────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
BEGIN → SQL writes (undo log tracks changes)
→ [COMMIT ← YOU ARE HERE] → WAL fsynced
→ Changes visible to all → Locks released
```

**FAILURE PATH:**

```
Exception thrown → [ROLLBACK] → Undo log reversed
→ All changes since BEGIN erased
→ Database at pre-transaction state
→ Locks released → App receives error
```

**WHAT CHANGES AT SCALE:**
At high transaction rates, each explicit COMMIT incurs a WAL fsync. Group commit amortises this: PostgreSQL delays WAL flush by up to `wal_writer_delay` (default 200ms) to batch multiple COMMITs into one fsync. SAVEPOINTs in high-frequency loops (e.g., savepoint per row in a 10-million-row batch) accumulate undo log state and can exhaust memory — batching 1,000 rows per savepoint interval is more scalable.

---

### ⚖️ Comparison Table

| Command            | Effect                                | Reversible           | Best For                                            |
| ------------------ | ------------------------------------- | -------------------- | --------------------------------------------------- |
| **COMMIT**         | Makes all changes permanent + durable | No                   | Finalising completed business operations            |
| **ROLLBACK**       | Reverses all changes to BEGIN         | N/A                  | Error recovery, abandoning failed operations        |
| **ROLLBACK TO sp** | Reverses changes since savepoint      | Can continue txn     | Partial error recovery in complex transactions      |
| **SAVEPOINT**      | Creates a named rollback point        | Release with RELEASE | Batch processing with individual-row error handling |

How to choose: Use COMMIT/ROLLBACK for standard transactions. Add SAVEPOINTs only in complex batch operations or stored procedures where partial failure handling is explicitly designed.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                      |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ROLLBACK is instant                              | Rollback replays the undo log in reverse — for large transactions (millions of rows), rollback takes as long as the forward transaction                      |
| After COMMIT, data is immediately on disk        | COMMIT writes the WAL and fsyncs it; the actual data pages may still be in the buffer pool and only written to disk asynchronously during checkpoint         |
| SAVEPOINT creates a new transaction              | SAVEPOINT creates a nested checkpoint within the same transaction — the outer transaction's isolation and atomicity still apply                              |
| auto-commit=true means transactions are disabled | Auto-commit wraps every statement in its own transaction automatically — transactions are always active; auto-commit just sets the boundary to per-statement |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing ROLLBACK on Exception — Partial State Committed**

**Symptom:** Database contains partially-completed operations after application error; orders without payments; inventory decremented without order creation.

**Root Cause:** Application caught an exception but didn't roll back the transaction; remaining statements were skipped but the partial writes were committed.

**Diagnostic:**

```sql
-- Find orders without corresponding payments (orphaned orders)
SELECT o.id, o.created_at
FROM orders o
LEFT JOIN payments p ON p.order_id = o.id
WHERE p.id IS NULL
  AND o.status = 'CONFIRMED';
```

**Fix:**

```java
// BAD: exception swallowed, no rollback
try {
    orderRepo.save(order);
    paymentService.charge(order);
} catch (Exception e) {
    log.error("Failed", e); // no rollback!
}

// GOOD: @Transactional handles rollback automatically
@Transactional
public void processOrder(Order order) {
    orderRepo.save(order);
    paymentService.charge(order); // exception → auto-rollback
}
```

**Prevention:** Use `@Transactional` or explicit try-finally with ROLLBACK. Never swallow exceptions inside a transaction scope.

---

**2. SAVEPOINT Accumulation Causing Memory Pressure**

**Symptom:** Batch job memory usage climbs throughout execution; eventually crashes with OOM or undo tablespace exhaustion.

**Root Cause:** Creating a SAVEPOINT per row in a multi-million-row batch — each savepoint holds an undo log position reference; row-level savepoints accumulate unbounded undo state.

**Diagnostic:**

```sql
-- MySQL: check undo log length
SHOW ENGINE INNODB STATUS\G
-- "History list length" growing continuously = undo log accumulation

-- PostgreSQL: monitor transaction memory usage
SELECT pid, query, state,
       pg_size_pretty(work_mem) AS work_mem
FROM pg_stat_activity
WHERE state = 'active';
```

**Fix:** Use SAVEPOINTs at batch level (every 1,000 rows), not per-row. Release SAVEPOINTs after successful sections (`RELEASE SAVEPOINT sp1` to reclaim undo log space).

**Prevention:** Design batch jobs with SAVEPOINTs at coarse granularity. Profile undo log growth during batch job development.

---

**3. DDL Statement Implicitly Committing Transaction (MySQL)**

**Symptom:** In MySQL, a `ROLLBACK` after a `CREATE TABLE` or `ALTER TABLE` statement has no effect — schema changes are permanent; data changes before the DDL are also committed unexpectedly.

**Root Cause:** MySQL auto-commits the current transaction before executing DDL statements (implicit commit). PostgreSQL does NOT do this — DDL is transactional in PostgreSQL.

**Diagnostic:**

```sql
-- MySQL: test whether DDL forces implicit commit
BEGIN;
INSERT INTO test_table VALUES (1);
CREATE TABLE temp_check (id INT); -- implicit COMMIT here in MySQL
ROLLBACK; -- too late: INSERT and CREATE already committed

-- PostgreSQL: DDL is transactional
BEGIN;
INSERT INTO test_table VALUES (1);
CREATE TABLE temp_check (id INT);
ROLLBACK; -- both INSERT and CREATE are rolled back
```

**Fix:** In MySQL, never mix DDL and DML in the same transaction expecting rollback to work. Structure migrations to keep DDL and DML separate, or migrate to PostgreSQL for transactional DDL.

**Prevention:** Know your database's DDL transaction behaviour. In MySQL, use explicit transactions only for DML, not DDL.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Transaction` — COMMIT/ROLLBACK/SAVEPOINT are the lifecycle commands of a transaction
- `ACID` — these commands implement the Atomicity and Durability properties
- `WAL (Write-Ahead Log)` — COMMIT triggers the WAL fsync; ROLLBACK reads the undo log

**Builds On This (learn these next):**

- `Isolation Levels` — the isolation context in which COMMIT/ROLLBACK operate
- `Stored Procedure / Trigger` — stored procedures use SAVEPOINTs for internal error handling
- `Durability` — COMMIT's guarantee: once committed, permanent

**Alternatives / Comparisons:**

- `Undo Log` — the mechanism ROLLBACK uses to reverse changes
- `SAGA Pattern` — distributed systems' alternative to ROLLBACK: compensating transactions
- `Optimistic Locking` — application-level alternative to ROLLBACK for conflict detection

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ SQL commands controlling transaction fate:│
│              │ COMMIT=save, ROLLBACK=undo, SAVEPOINT=mark│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No way to safely attempt multi-step       │
│ SOLVES       │ operations and undo on failure            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Rollback = re-running the transaction in  │
│              │ reverse — large txns = slow rollback      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always wrap multi-step mutations in txns  │
│              │ Use SAVEPOINT for batch partial recovery  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't SAVEPOINT per-row in million-row    │
│              │ batches — use coarser granularity         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Safety vs rollback time / undo log size   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "COMMIT is a promise; ROLLBACK is         │
│              │  time travel back to before you promised" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Isolation Levels → MVCC → WAL             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D — Root Cause Trace) A MySQL stored procedure processes 10,000 records. For each record, it creates a SAVEPOINT, processes the record, and either releases the savepoint (success) or rolls back to it (failure). After processing 500 records, the application server runs out of memory. Trace the exact mechanism causing the memory growth and describe the correct SAVEPOINT strategy for this scenario.

**Q2.** (TYPE F — Comparison Depth) PostgreSQL treats DDL statements (CREATE TABLE, ALTER TABLE) as transactional — they can be rolled back. MySQL issues an implicit COMMIT before DDL statements. Describe a database migration scenario where PostgreSQL's transactional DDL provides a critical safety guarantee that MySQL's approach cannot provide — and explain what MySQL developers must do instead to achieve equivalent safety.
