---
version: 2
layout: default
title: "Dirty Read"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /databases/dirty-read/
id: DBF-034
category: Database Fundamentals
difficulty: ★★☆
depends_on: Isolation Levels, Transaction, ACID
used_by: MVCC, Read Committed, Database Testing
related: Non-Repeatable Read, Phantom Read, Isolation
tags:
  - database
  - transactions
  - concurrency
  - intermediate
---

# DBF-007 - Dirty Read

⚡ TL;DR - A dirty read is when a transaction reads data that another transaction has written but not yet committed - data that may be rolled back and thus never officially exist.

| #419            | Category: Database Fundamentals              | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------- | :-------------- |
| **Depends on:** | Isolation Levels, Transaction, ACID          |                 |
| **Used by:**    | MVCC, Read Committed, Database Testing       |                 |
| **Related:**    | Non-Repeatable Read, Phantom Read, Isolation |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT DIRTY READ PREVENTION:**
A payment processing system: Transaction A writes `payment_status = 'APPROVED'` but hasn't committed yet (still processing). Transaction B reads the payment status, sees 'APPROVED', and ships the goods. Transaction A then encounters an error and rolls back - `payment_status` was never actually committed as 'APPROVED'. The goods have shipped for a payment that doesn't legally exist. The company takes the loss.

**THE BREAKING POINT:**
Dirty reads don't just cause data inconsistency - they cause business decisions based on phantom data. In financial systems, inventory systems, or any system where state drives irreversible actions (shipping, notifications, authorisations), acting on uncommitted data is equivalent to acting on lies.

**THE INVENTION MOMENT:**
"This is exactly why preventing dirty reads is the baseline requirement for safe database concurrency."

---

### 📘 Textbook Definition

A **dirty read** (also called an "uncommitted dependency") is a concurrency anomaly in which a transaction reads data that has been modified by another transaction but not yet committed. If the modifying transaction subsequently rolls back, the reading transaction has based its work on data that never officially existed. A dirty read is possible only at the **READ UNCOMMITTED** isolation level. All higher isolation levels (READ COMMITTED, REPEATABLE READ, SERIALIZABLE) prevent dirty reads. Most production databases default to READ COMMITTED, making dirty reads a prevented anomaly by default.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A dirty read is seeing another transaction's work-in-progress data - data that may be erased before it's official.

**One analogy:**

> Reading a journalist's draft article before it's been fact-checked and published. The article might say the stock price is $200, but the journalist found an error and deleted the article before publishing. You made investment decisions based on content that was never officially true. That's a dirty read.

**One insight:**
Dirty reads are the most dangerous isolation anomaly because they expose business logic to phantom data - data that the database will officially treat as having never existed. The 50ms performance gain from READ UNCOMMITTED is never worth the risk in any production system that drives real-world actions from database state.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Committed data is authoritative - it reflects the database's official, permanent state.
2. Uncommitted data is provisional - it may be rolled back and treated as having never existed.
3. A reading transaction should only see committed data to make decisions on real state.

**DERIVED DESIGN:**
At READ UNCOMMITTED, the database reads directly from data pages (or memory buffers) without checking transaction status - the fastest possible read, but with no visibility guarantees.

At READ COMMITTED (the fix), the database uses MVCC (Multi-Version Concurrency Control): each row maintains multiple versions tagged with the transaction ID that created them. A read query only sees versions created by committed transactions - in-progress versions from uncommitted transactions are invisible.

This is implemented via PostgreSQL's `xmin`/`xmax` row headers: a reader checks whether the `xmin` (creating transaction ID) is in the "committed transactions" list (`pg_clog`/`pg_xact`). If not committed yet, that version is invisible.

**THE TRADE-OFFS:**
**READ UNCOMMITTED (dirty reads allowed):**

- Gain: maximum read throughput - no version checking needed.
- Cost: reads may reflect in-flight writes that never commit.

**READ COMMITTED (dirty reads prevented):**

- Gain: reads are always based on committed, official state.
- Cost: marginal MVCC overhead per read (version visibility check).

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce system. Transaction A begins updating an order's status to 'SHIPPED'. Transaction B simultaneously checks the order status.

**DIRTY READ SCENARIO (READ UNCOMMITTED):**

- T=0: Transaction A begins. Updates order #100: status = 'SHIPPED'.
- T=1: Transaction B reads order #100: sees status = 'SHIPPED'. B sends the customer a shipping notification email.
- T=2: Transaction A's update triggers a constraint violation (warehouse ID invalid). A rolls back. Order #100 status reverts to 'PENDING'.
- Result: Customer received a shipping notification. Order is still PENDING. Customer calls support. Support sees 'PENDING'. Chaos ensues.

**CLEAN READ SCENARIO (READ COMMITTED):**

- T=0: Transaction A begins. Updates order #100: status = 'SHIPPED' (uncommitted).
- T=1: Transaction B reads order #100: MVCC shows the uncommitted version is invisible. B sees status = 'PENDING'.
- T=2: Transaction A rolls back. Order #100 = 'PENDING'.
- Result: Transaction B saw the correct, committed state. No phantom notification. Business logic intact.

**THE INSIGHT:**
READ UNCOMMITTED gives you the read performance of "ignore other transactions" at the cost of acting on data that may never officially exist. READ COMMITTED adds almost no overhead while guaranteeing that every read is based on real, committed state.

---

### 🧠 Mental Model / Analogy

> A dirty read is like peeking at a chef's recipe modifications before they finalise the dish. You memorise the new recipe, go home and cook it - but the chef scrapped those changes and went back to the original. You cooked the wrong dish based on draft notes that were never approved. The "official" recipe (committed data) never had those modifications.

- "Chef's draft notes" → uncommitted transaction writes
- "Finalising the dish" → COMMIT
- "Scrapping changes" → ROLLBACK
- "Official recipe" → committed data in the database
- "You copying the draft" → dirty read

Where this analogy breaks down: unlike a recipe, database ROLLBACK is instantaneous and guaranteed - there's never a "partial rollback" state.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A dirty read is when you see someone else's unfinished database changes - changes they might cancel (rollback) later. It's like reading an email draft that was deleted before it was sent.

**Level 2 - How to use it (junior developer):**
Dirty reads only happen at READ UNCOMMITTED isolation level. Since most databases default to READ COMMITTED, dirty reads are prevented by default - you don't need to do anything special. Never set `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED` in production code unless you have a specific, documented reason (approximate counts, max throughput analytics where some staleness is acceptable).

**Level 3 - How it works (mid-level engineer):**
Under READ COMMITTED with MVCC (PostgreSQL): when a row is updated, a new row version is created with the current transaction ID as `xmin`. The old version remains. A reader checks the `xmin` of each candidate row version: if `xmin` is a committed transaction (in `pg_xact`), the version is visible. If `xmin` is an active (uncommitted) transaction, the version is invisible - the reader falls back to the previous committed version. This version visibility check is the mechanism that prevents dirty reads.

**Level 4 - Why it was designed this way (senior/staff):**
READ UNCOMMITTED exists because there are legitimate use cases for approximate reads: approximate row counts, sampling analytics, or reads in systems where slight inconsistency is structurally acceptable (e.g., read-only analytics replicas where the worst case is a slightly wrong number). The cost of READ COMMITTED MVCC version checking is minimal on modern hardware - a few nanoseconds per row. However, in very high throughput scenarios (100M+ reads/second), even this minimal overhead matters. High-performance analytics databases (ClickHouse, DuckDB) use their own multi-version schemes that optimise for read-heavy workloads while still preventing dirty reads.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ DIRTY READ: READ UNCOMMITTED vs COMMITTED    │
├──────────────────────────────────────────────┤
│                                              │
│  READ UNCOMMITTED:                           │
│    Reader → reads current data page         │
│    Sees whatever value is in buffer pool     │
│    (may be from uncommitted transaction)     │
│                                              │
│  READ COMMITTED (MVCC):                      │
│    Row versions in heap:                     │
│    ┌─────────────────────────────────────┐   │
│    │ xmin=100(committed) | val='PENDING' │   │
│    │ xmin=101(active)    | val='SHIPPED' │   │
│    └─────────────────────────────────────┘   │
│                                              │
│    Reader checks xmin=101: active tx?       │
│      → Yes → invisible (dirty, skip it)     │
│    Falls back to xmin=100: committed?       │
│      → Yes → visible → returns 'PENDING'    │
│                                              │
│    After txn 101 commits:                   │
│    Reader sees xmin=101: committed?         │
│      → Yes → returns 'SHIPPED' (clean read) │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Transaction A writes uncommitted data
→ [DIRTY READ prevention ← YOU ARE HERE]
→ MVCC hides uncommitted row version
→ Transaction B reads only committed version
→ Transaction A commits → version becomes visible
```

**FAILURE PATH:**

```
Transaction A writes + ROLLS BACK
→ MVCC: uncommitted version was never visible to B
→ B only saw committed state throughout
→ No business decision based on phantom data
```

**WHAT CHANGES AT SCALE:**
At high read throughput (millions of reads/second), MVCC version visibility checking adds nanosecond-level overhead per row. For analytics workloads on billions of rows, this overhead is non-trivial. Systems like Snowflake and BigQuery use isolated read replicas with point-in-time snapshots rather than MVCC to eliminate dirty read risk while maintaining high read throughput.

---

### ⚖️ Comparison Table

| Anomaly             | Isolation Level Required to Prevent | Risk Level  | Frequency in Practice            |
| ------------------- | ----------------------------------- | ----------- | -------------------------------- |
| **Dirty Read**      | READ COMMITTED                      | Critical    | Rare (default level prevents it) |
| Non-Repeatable Read | REPEATABLE READ                     | Medium      | Common without explicit handling |
| Phantom Read        | SERIALIZABLE                        | Medium-High | Common in range queries          |
| Write Skew          | SERIALIZABLE                        | High        | Often overlooked                 |

How to choose: Dirty reads are the floor - always use at least READ COMMITTED. Identify which additional anomalies your business logic is vulnerable to and raise the isolation level only for those specific transactions.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                  |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dirty reads are common in production         | Most databases default to READ COMMITTED, which prevents dirty reads - they only occur if READ UNCOMMITTED is explicitly set                                                             |
| READ UNCOMMITTED is significantly faster     | The performance difference between READ UNCOMMITTED and READ COMMITTED is minimal in MVCC databases - the MVCC version check is nanoseconds; not worth the data integrity risk           |
| A dirty read always causes wrong results     | It causes wrong results IF the writing transaction rolls back - if the write commits, the read happens to be correct despite the anomaly                                                 |
| All databases prevent dirty reads by default | MySQL InnoDB defaults to REPEATABLE READ (stronger than READ COMMITTED); PostgreSQL defaults to READ COMMITTED; SQL Server defaults to READ COMMITTED; Oracle defaults to READ COMMITTED |

---

### 🚨 Failure Modes & Diagnosis

**1. READ UNCOMMITTED Set Globally in Configuration**

**Symptom:** Occasional phantom data in application; records reported by users that don't exist when support investigates; intermittent data inconsistencies that "fix themselves."

**Root Cause:** Database or connection pool configured with READ UNCOMMITTED globally; application sees uncommitted writes from concurrent transactions that subsequently roll back.

**Diagnostic:**

```sql
-- PostgreSQL: check current isolation level
SHOW default_transaction_isolation;
-- Should be 'read committed' or higher

-- MySQL: check global and session isolation
SELECT @@GLOBAL.transaction_isolation;
SELECT @@SESSION.transaction_isolation;

-- Per-connection check in application
SELECT current_setting('transaction_isolation');
```

**Fix:**

```sql
-- PostgreSQL: set globally in postgresql.conf
default_transaction_isolation = 'read committed'

-- MySQL: set in my.cnf
transaction-isolation = READ-COMMITTED
```

**Prevention:** Never set READ UNCOMMITTED in production configuration. Include isolation level checks in database provisioning scripts and startup health checks.

---

**2. Phantom Business Actions from Dirty Reads**

**Symptom:** External actions (emails, notifications, API calls to payment processors) triggered based on database state that was subsequently rolled back; duplicate notifications; charge attempts for cancelled orders.

**Root Cause:** Business logic reads database state and triggers irreversible external actions without ensuring the triggering state is committed.

**Diagnostic:**

```bash
# Check for notification events without corresponding committed DB records
# This requires application-level audit logging
grep "NOTIFICATION_SENT" app.log | while read event; do
  order_id=$(echo $event | grep -o 'order=[0-9]*' | cut -d= -f2)
  echo "Checking order $order_id"
done
```

**Fix:** Never trigger irreversible external actions (send email, charge card, call API) inside a database transaction or based on data read within a transaction that may roll back. Use the transactional outbox pattern: write the "intent to notify" as a committed database record, then process it asynchronously after commit.

**Prevention:** Design external action triggers to read from committed state only, ideally using event-driven architecture with transactional outbox pattern.

---

**3. Analytics Query Using READ UNCOMMITTED for "Speed" - Wrong Aggregates**

**Symptom:** Analytics dashboard shows totals that are impossible given known business transactions; negative inventory counts; more orders than order IDs would allow.

**Root Cause:** Analytics queries explicitly set READ UNCOMMITTED to avoid locking, and are reading in-progress batch operations that are partially written but not yet committed.

**Diagnostic:**

```sql
-- Check if analytics sessions use READ UNCOMMITTED
SELECT pid, query, client_addr,
       current_setting('transaction_isolation') AS isolation
FROM pg_stat_activity
WHERE state = 'active';
```

**Fix:** Use a read replica for analytics. The replica applies changes only from committed WAL records - it inherently provides READ COMMITTED semantics without any performance penalty, since replicas don't need to lock primary tables.

**Prevention:** Route analytics queries to a read replica. Never use READ UNCOMMITTED as a performance optimisation for analytics - the data quality cost is never justified.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Isolation Levels` - dirty read is the anomaly that READ UNCOMMITTED allows and READ COMMITTED prevents
- `Transaction` - dirty reads occur when reading another transaction's in-progress writes
- `ACID` - dirty reads violate the Isolation property of ACID

**Builds On This (learn these next):**

- `MVCC` - the mechanism that prevents dirty reads in most modern databases
- `Non-Repeatable Read` - the next level of isolation anomaly, prevented at REPEATABLE READ
- `Phantom Read` - the anomaly requiring SERIALIZABLE to prevent

**Alternatives / Comparisons:**

- `Non-Repeatable Read` - dirty read = seeing uncommitted data; non-repeatable read = seeing committed changes from concurrent transactions mid-query
- `Write Skew` - more subtle anomaly not prevented by REPEATABLE READ

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Reading another transaction's uncommitted │
│              │ data - data that may be rolled back       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Business decisions based on phantom data  │
│ SOLVES       │ that is subsequently erased by rollback   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Only occurs at READ UNCOMMITTED; all      │
│              │ higher levels prevent it via MVCC         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Never in production for data-driven logic │
│              │ Only for truly approximate analytics      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Any system where incorrect reads drive    │
│              │ real-world actions (payment, shipping)    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Marginal read speed vs data correctness   │
│              │ (correctness always wins in production)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reading a cheque before it clears -      │
│              │  it might bounce and your goods are gone" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Non-Repeatable Read → Phantom Read → MVCC │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D - Root Cause Trace) A system uses READ UNCOMMITTED for a "real-time" inventory count displayed on a product page. A batch restock operation begins a transaction that increments stock count from 0 to 100 for 10,000 products (takes 30 seconds). During those 30 seconds, what do product page viewers see, what can they do with that information, and what happens if the batch operation fails and rolls back? Trace the complete sequence of events including customer actions.

**Q2.** (TYPE F - Comparison Depth) Both dirty reads and non-repeatable reads are "seeing the wrong data" - but they are different anomalies requiring different isolation levels to prevent. Explain precisely what is different about the state of the writing transaction in each case (committed vs uncommitted), and design a single SQL test that demonstrates the difference between the two anomalies in the same transaction.
