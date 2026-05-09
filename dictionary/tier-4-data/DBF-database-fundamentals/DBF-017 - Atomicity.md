---
version: 1
layout: default
title: "Atomicity"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /databases/atomicity/
id: DBF-017
category: Database Fundamentals
difficulty: ★☆☆
depends_on: Transaction, ACID
used_by: WAL, Redo Log, Undo Log
related: Durability, Rollback, Savepoint
tags:
  - database
  - transactions
  - reliability
  - foundational
---

# DBF-017 - Atomicity

⚡ TL;DR - Atomicity is the database guarantee that a transaction's operations are indivisible: either every change commits or none of them do, with no partial results ever persisted.

| #412            | Category: Database Fundamentals | Difficulty: ★☆☆ |
| :-------------- | :------------------------------ | :-------------- |
| **Depends on:** | Transaction, ACID               |                 |
| **Used by:**    | WAL, Redo Log, Undo Log         |                 |
| **Related:**    | Durability, Rollback, Savepoint |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A fund transfer: debit $500 from Account A, credit $500 to Account B - two SQL UPDATE statements. The first succeeds. Then the database server crashes, the network drops, or an application exception fires. Account A is now $500 lighter. Account B has received nothing. The money has been destroyed. There's no way to know at the application level whether to retry (double-debit) or give up (accept the loss). Every multi-step data change becomes a potential data loss event.

**THE BREAKING POINT:**
Even a simple operation like "update inventory count and create an order record" involves two writes. Without atomicity, any failure between write 1 and write 2 creates ghost inventory or ghost orders. At thousands of transactions per second, the probability of a failure between writes is not zero - it's a certainty over time.

**THE INVENTION MOMENT:**
"This is exactly why Atomicity was created."

---

### 📘 Textbook Definition

**Atomicity** is the first property of the ACID model, guaranteeing that a database transaction is treated as a single indivisible unit. Either all operations within the transaction are applied to the database (on `COMMIT`) or none of them are (on `ROLLBACK` or failure). The database engine ensures this by maintaining an undo log - a record of the original values of every row modified during the transaction - enabling complete reversal if the transaction cannot complete. Atomicity is enforced by the transaction manager using the WAL (Write-Ahead Log) and undo log mechanisms.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Atomicity means all database changes in a transaction happen together or not at all.

**One analogy:**

> Think of a vending machine. Either the machine dispenses the snack AND takes your money - or if it jams, it refunds your money and gives you nothing. The machine never takes your money without dispensing the snack, and never dispenses without charging. That all-or-nothing behaviour is Atomicity.

**One insight:**
Atomicity is not about speed - it's about failure handling. In the happy path (no crashes, no errors), atomicity is invisible. Its value only appears when something goes wrong mid-transaction. It's an insurance policy that costs a small write overhead but prevents catastrophic partial-state corruption.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A transaction is an all-or-nothing unit - no intermediate state is ever observable or permanent.
2. The database must be able to undo every write a transaction made, at any point before commit.
3. After a crash, the database must be able to determine which transactions committed and which did not.

**DERIVED DESIGN:**
To guarantee "undo at any point," the database maintains an **undo log**: before overwriting any row's value, the database writes the original value to the undo log. If a rollback is needed, the engine reads the undo log and restores all original values.

To guarantee "survive crash," the database uses a **WAL (Write-Ahead Log)**: the commit record must be written to the durable log before `COMMIT` returns success to the client. On restart, the engine scans the log: transactions with a COMMIT record are re-applied (redo); transactions without one are rolled back using the undo log.

This dual-log design (redo log + undo log) is what makes atomicity work even across crashes.

**THE TRADE-OFFS:**
**Gain:** No partial state ever persists. Applications can write multi-step mutations and handle only two outcomes: success or rollback.
**Cost:** Every write requires writing to the undo log before modifying data pages, adding I/O overhead. Long transactions accumulate large undo logs, consuming memory and disk space.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce system processes an order: deduct 1 unit from `inventory`, insert a row into `orders`. These are two separate writes.

**WHAT HAPPENS WITHOUT ATOMICITY:**

- Write 1: inventory decremented from 5 to 4. ✅
- Application exception fires (credit card API timeout).
- Write 2: order row never inserted. ❌
- Result: inventory shows 4 units but no order exists. A "ghost deduction" - inventory is wrong forever until manual correction.

**WHAT HAPPENS WITH ATOMICITY:**

- BEGIN TRANSACTION
- Write 1: inventory decremented (undo log records: inventory was 5).
- Exception fires.
- ROLLBACK triggered.
- Undo log applied: inventory restored to 5.
- Result: database looks exactly as it did before the transaction. Application can safely retry.

**THE INSIGHT:**
Atomicity turns a "may have partially happened" problem into a clean "either it happened or it didn't" outcome. This eliminates the class of bugs that come from partial state - the hardest bugs to find because they look like valid data.

---

### 🧠 Mental Model / Analogy

> Atomicity is like a revision history in a document editor. When you start making edits, every change is tracked. If you hit "Undo All," every change is reversed instantly - the document is exactly as it was when you started. Nothing is "mostly undone." Either all your edits are there or none are.

- "Starting to edit" → BEGIN TRANSACTION
- "Making edits" → SQL writes (buffered with undo log)
- "Save" → COMMIT (all edits permanent)
- "Undo All" → ROLLBACK (all edits reversed via undo log)
- "Tracked change history" → undo log

Where this analogy breaks down: in a database, rollback happens automatically on failure - there's no "Undo All" button for the application to forget to press.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Atomicity means all the steps in a database operation happen together or not at all. Like flipping a switch - the light is either on or off, never "half on."

**Level 2 - How to use it (junior developer):**
Wrap multiple SQL statements in `BEGIN` / `COMMIT`. If anything fails, call `ROLLBACK`. In Spring/Java, annotate your service method with `@Transactional` - Spring automatically begins a transaction, commits on success, and rolls back on unchecked exceptions.

**Level 3 - How it works (mid-level engineer):**
The undo log stores before-images of every modified row. When a transaction rolls back, the engine reads the undo log in reverse and restores original values. The WAL ensures the commit decision survives crashes: if the COMMIT log entry is present on restart, the transaction is considered committed; otherwise the undo log is used to reverse it. In InnoDB (MySQL), the undo log is stored in the system tablespace; in PostgreSQL, MVCC uses tuple visibility flags to achieve similar atomicity without a separate undo log.

**Level 4 - Why it was designed this way (senior/staff):**
PostgreSQL's MVCC-based atomicity is elegant: instead of maintaining a separate undo log, PostgreSQL keeps old row versions in the heap. A transaction writes a new row version; if it rolls back, the old version is simply marked as "the current one." No undo I/O is needed. The cost is "table bloat" - old versions accumulate and must be cleaned by VACUUM. MySQL InnoDB uses a traditional undo log approach - rollback is an explicit I/O operation writing old values back. Neither approach is strictly superior: PostgreSQL's approach is faster for rollbacks but requires background maintenance; MySQL's approach has more predictable write amplification.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ ATOMICITY: UNDO LOG + WAL                    │
├──────────────────────────────────────────────┤
│                                              │
│  BEGIN                                       │
│    │                                         │
│    ▼                                         │
│  UPDATE row A                                │
│    ├── Write old value to UNDO LOG           │
│    └── Write new value to buffer pool        │
│                                              │
│  UPDATE row B                                │
│    ├── Write old value to UNDO LOG           │
│    └── Write new value to buffer pool        │
│                                              │
│  ┌────────────────────────────────────┐      │
│  │ COMMIT PATH        │ ROLLBACK PATH │      │
│  ├────────────────────┼───────────────┤      │
│  │ Write COMMIT to WAL│ Read UNDO LOG │      │
│  │ fsync WAL to disk  │ in reverse    │      │
│  │ Return success     │ Restore rows  │      │
│  │ (changes visible)  │ Return error  │      │
│  └────────────────────┴───────────────┘      │
│                                              │
│  CRASH RECOVERY:                             │
│    WAL has COMMIT? → Redo (replay changes)   │
│    WAL no COMMIT?  → Undo (restore originals)│
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
App calls service → @Transactional begins → SQL writes
→ [ATOMICITY ← YOU ARE HERE: undo log tracks each write]
→ All writes succeed → COMMIT → WAL fsynced
→ Changes visible to other transactions
```

**FAILURE PATH:**

```
Exception mid-transaction → ROLLBACK triggered
→ Undo log read in reverse → All writes reversed
→ Database at pre-transaction state
→ App receives exception / transaction marked rolled back
```

**WHAT CHANGES AT SCALE:**
At high transaction volume, the undo log grows large if transactions are long-running, causing contention on the undo tablespace. In PostgreSQL, rapid write workloads generate "table bloat" from dead tuples (old MVCC versions), requiring aggressive VACUUM scheduling. In both systems, keeping transactions short is the primary scaling lever - short transactions mean small undo logs and fast rollbacks.

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                       |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rollback instantly undoes writes                   | Rollback applies the undo log entry by entry - for large transactions with millions of modified rows, rollback can take as long as the transaction itself took to run                         |
| Atomicity means the transaction is fast            | Atomicity adds overhead (undo logging) for every write; the guarantee is about correctness, not speed                                                                                         |
| @Transactional in Spring always provides atomicity | Only if the transaction is actually committed/rolled back correctly - checked exceptions don't trigger rollback by default; `@Transactional(rollbackFor = Exception.class)` must be specified |
| Atomicity prevents concurrent access issues        | Atomicity is only about all-or-nothing completion; preventing concurrent access interference is Isolation's responsibility                                                                    |

---

### 🚨 Failure Modes & Diagnosis

**1. @Transactional Not Rolling Back on Checked Exception**

**Symptom:** Service throws a checked exception; the database changes from earlier in the method are committed anyway; partial state exists.

**Root Cause:** Spring's `@Transactional` only rolls back on unchecked exceptions (`RuntimeException` and `Error`) by default. A checked exception (e.g., `IOException`) does not trigger rollback.

**Diagnostic:**

```bash
# Check if partial data exists after an expected rollback
# Look for orphaned records in the database after a failed operation
SELECT * FROM orders WHERE payment_id IS NULL;
# orders without payment = atomicity failure
```

**Fix:**

```java
// BAD: checked exception does NOT rollback
@Transactional
public void processOrder() throws IOException {
    orderRepo.save(order);
    throw new IOException("Payment failed");
    // Order is COMMITTED despite the exception!
}

// GOOD: specify rollbackFor
@Transactional(rollbackFor = Exception.class)
public void processOrder() throws IOException {
    orderRepo.save(order);
    throw new IOException("Payment failed");
    // Order is rolled back correctly
}
```

**Prevention:** Always specify `rollbackFor = Exception.class` unless you have a specific reason to commit on checked exceptions.

---

**2. Large Transaction Causing Undo Log Explosion**

**Symptom:** MySQL `ERROR 1206: The total number of locks exceeds the lock table size`; or PostgreSQL query performance degrading during a long-running transaction; disk space spike.

**Root Cause:** A transaction modifying millions of rows generates an enormous undo log. MySQL's undo tablespace fills; PostgreSQL accumulates millions of dead tuples blocking VACUUM.

**Diagnostic:**

```sql
-- MySQL: check undo log size
SHOW ENGINE INNODB STATUS\G
-- Look for "History list length" - above 1000 is a warning signal

-- PostgreSQL: check bloat from long transactions
SELECT pid, now() - xact_start AS duration
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY duration DESC;
```

**Fix:** Break large batch operations into smaller transactions - process 1,000 rows per transaction rather than 1,000,000 rows in one transaction.

**Prevention:** Never run bulk data migrations in a single transaction. Use batched commits with explicit checkpoint intervals.

---

**3. Self-Invocation Breaking @Transactional (Spring)**

**Symptom:** A `@Transactional` method called from within the same class doesn't start a new transaction; nested calls don't roll back independently.

**Root Cause:** Spring's `@Transactional` uses a proxy - the proxy intercepts external calls but not `this.method()` calls within the same class instance.

**Diagnostic:**

```java
// This does NOT create a new transaction - self-invocation bypasses proxy
@Service
public class OrderService {
    public void outer() {
        this.inner(); // proxy NOT invoked - @Transactional ignored
    }

    @Transactional
    public void inner() { /* ... */ }
}
```

**Fix:** Inject the service as a self-reference (`@Autowired OrderService self`) or extract the transactional method to a separate Spring bean.

**Prevention:** Structure transactional code so it's called from other beans, not via `this`. Use `@Transactional` at the service boundary, not deep within a class's internal methods.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Transaction` - atomicity is a property of transactions; understand what a transaction is first
- `ACID` - atomicity is the "A" of ACID; understand the full model

**Builds On This (learn these next):**

- `WAL (Write-Ahead Log)` - the mechanism that makes atomicity survive crashes
- `Redo Log / Undo Log` - the specific log structures that implement commit and rollback
- `Savepoint` - allows partial rollbacks within a transaction, extending atomicity's granularity

**Alternatives / Comparisons:**

- `Durability` - the "D" of ACID; where atomicity handles rollback, durability handles crashes post-commit
- `Compensating Transaction` - the SAGA pattern alternative to rollback for distributed systems without ACID

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ All-or-nothing: every write in a          │
│              │ transaction commits or none do            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Crashes mid-transaction leave partial     │
│ SOLVES       │ state - ghost data, lost money            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Rollback can be as slow as the original   │
│              │ transaction - keep transactions short     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any multi-step mutation must succeed or   │
│              │ fail together (transfers, orders, etc.)   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-row writes - atomicity is free     │
│              │ but adds overhead to large batch ops      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Correctness vs undo log overhead/bloat    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "All or nothing - never half-done"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WAL → Undo Log → Isolation Levels         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D - Root Cause Trace) A Spring service method annotated with `@Transactional` calls two repository methods. The first saves an Order record. The second throws a `java.io.IOException` (a checked exception). Trace step by step what Spring does with the transaction, what ends up in the database, and exactly what you would need to change in the code to get the expected rollback behaviour.

**Q2.** (TYPE E - First Principles Challenge) If you had to implement atomicity for a file system (not a database) - specifically, you need a "write two files atomically" operation that either updates both files or neither - what mechanism would you design? What data structures would you need? Where would PostgreSQL's approach (MVCC) help, and where would it be insufficient?
