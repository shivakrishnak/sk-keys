---
layout: default
title: "Non-Repeatable Read"
parent: "Database Fundamentals"
nav_order: 25
permalink: /databases/non-repeatable-read/
id: DBF-025
category: Database Fundamentals
difficulty: ★★☆
depends_on: Isolation Levels, Dirty Read, MVCC
used_by: REPEATABLE READ, Serializable, MVCC
related: Dirty Read, Phantom Read, Write Skew
tags:
  - database
  - transactions
  - concurrency
  - intermediate
---

# DBF-025 — Non-Repeatable Read

⚡ TL;DR — A non-repeatable read occurs when a transaction reads the same row twice and gets different values because another transaction committed an update between the two reads.

| #420            | Category: Database Fundamentals      | Difficulty: ★★☆ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Isolation Levels, Dirty Read, MVCC   |                 |
| **Used by:**    | REPEATABLE READ, Serializable, MVCC  |                 |
| **Related:**    | Dirty Read, Phantom Read, Write Skew |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT NON-REPEATABLE READ PREVENTION:**
A bank transaction calculates a transfer: read Account A ($1,000), verify sufficient funds, compute new balance ($700 after $300 transfer), write new balance. Between the first read and the write, a concurrent transaction withdraws $800 from Account A and commits. The first transaction reads $1,000, computes $700 as the new balance, and writes $700 — but the actual starting point was $200. The account now shows $700, but $800 was already withdrawn — the account should show -$100 (overdraft), but instead shows a positive balance. Fraud is now possible.

**THE BREAKING POINT:**
Any business logic that reads a value, performs calculations, and writes a derived value is vulnerable. If the value changes between the read and the write, the derived write is wrong. Financial systems, inventory systems, and any read-then-compute-then-write pattern are all affected.

**THE INVENTION MOMENT:**
"This is exactly why REPEATABLE READ isolation was created."

---

### 📘 Textbook Definition

A **non-repeatable read** is a concurrency anomaly where a transaction reads the same row twice within a single transaction and receives different data values, because another transaction committed a modification to that row between the two reads. Unlike a dirty read (which reads uncommitted data), a non-repeatable read reads only committed data — but committed data that changed during the reading transaction. Non-repeatable reads are prevented by the **REPEATABLE READ** isolation level, which creates a consistent snapshot of the database at transaction start — all reads within the transaction see data as of that snapshot, regardless of concurrent commits.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A non-repeatable read is when the same question asked twice in the same transaction returns different answers because someone else's answer got committed between your questions.

**One analogy:**

> Checking a flight price online, going to enter your credit card, and finding the price changed in the 30 seconds it took you to find your wallet. Both prices were real (committed) — but the price changed between your first look and your second action. A non-repeatable read is the same thing: real, committed data that changed mid-operation.

**One insight:**
Unlike dirty reads (where you see data that may be erased), non-repeatable reads involve data that is 100% real and committed — it just changed. This makes them more insidious: the data looks correct at every point in time, but the values seen within one transaction are inconsistent with each other.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A non-repeatable read involves a committed write (not a dirty/uncommitted write).
2. The anomaly occurs when a transaction reads the same row at two different points and sees two different committed values.
3. REPEATABLE READ prevents this by freezing the visible snapshot at transaction start.

**DERIVED DESIGN:**
MVCC (Multi-Version Concurrency Control) solves non-repeatable reads elegantly:

- At `BEGIN` (REPEATABLE READ or higher), the database records the current transaction ID as the snapshot point.
- All reads within the transaction only see row versions created by transactions committed before this snapshot point.
- When Transaction B commits a new value for row X: the new version has a higher transaction ID. The reading transaction (snapshot at earlier ID) sees the version before B's commit.
- Result: re-reading the same row always returns the same value within the transaction.

Under READ COMMITTED, the snapshot refreshes per statement (not per transaction) — this is what allows non-repeatable reads at READ COMMITTED.

**THE TRADE-OFFS:**
**REPEATABLE READ:**

- Gain: consistent snapshot throughout the transaction; read-then-compute-then-write is safe from concurrent modifications to read rows.
- Cost: the transaction holds a snapshot that prevents MVCC cleanup of row versions visible at that snapshot; long-running REPEATABLE READ transactions accumulate "bloat."

---

### 🧪 Thought Experiment

**SETUP:**
An application reads a product price, applies a 10% discount calculation, and records the discounted price in a quote table. The read and write are in the same transaction.

**NON-REPEATABLE READ SCENARIO (READ COMMITTED):**

- T=0: Transaction A reads product #5: price = $100.
- T=1: Transaction B updates product #5: price = $200. Commits.
- T=2: Transaction A verifies price before writing quote: reads product #5 again — price = $200 (READ COMMITTED refreshed snapshot).
- T=3: Transaction A records quote: "10% off $100" = $90.
- Result: Quote says 10% off $100 = $90, but current price is $200. Quote is wrong. Customer gets a $90 quote for a $200 product.

**REPEATABLE READ SCENARIO:**

- T=0: Transaction A begins REPEATABLE READ. Snapshot taken.
- T=1: Transaction A reads product #5: price = $100 (snapshot value).
- T=2: Transaction B updates product #5: price = $200. Commits.
- T=3: Transaction A reads product #5 again: price = $100 (snapshot unchanged — B's commit is after the snapshot point).
- T=4: Transaction A records quote: 10% off $100 = $90. Consistent with what was read.
- Result: Quote is internally consistent. A may want to refresh before committing, but the data it used is self-consistent.

**THE INSIGHT:**
Non-repeatable reads make read-then-compute-then-write patterns unsafe. REPEATABLE READ guarantees that the "read" phase of this pattern sees a consistent snapshot, so the "compute" phase works on stable data.

---

### 🧠 Mental Model / Analogy

> A non-repeatable read is like checking your bank balance on your phone ($1,000), walking to the ATM to withdraw $800, and the ATM showing $200 (your partner withdrew $800 on the same account between your phone check and the ATM). Both figures are 100% correct at their respective moments. But within your single transaction (deciding how much to withdraw), you saw two different values for the same account.

- "Phone balance check" → first read in the transaction
- "Partner's withdrawal" → concurrent committed transaction
- "ATM balance" → second read in the same transaction (different value)
- "REPEATABLE READ" → ATM showing the same balance your phone showed, locked for your session

Where this analogy breaks down: unlike banking, a database REPEATABLE READ snapshot doesn't prevent you from making a write that conflicts with concurrent changes — you might commit an inconsistent value.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A non-repeatable read is when you look up the same data twice in one operation and get different answers, because someone changed and saved that data between your two lookups. It's like a spreadsheet recalculating between the time you read cell A1 and the time you used that value.

**Level 2 — How to use it (junior developer):**
Use `@Transactional(isolation = Isolation.REPEATABLE_READ)` in Spring for any operation that reads the same data multiple times and uses it in calculations. If you only read data once per transaction and don't compute from multiple reads, READ COMMITTED is sufficient.

**Level 3 — How it works (mid-level engineer):**
Under PostgreSQL REPEATABLE READ: the database records the transaction's snapshot ID at `BEGIN`. Each row has an `xmin` (transaction that created this version). A read returns the newest version whose `xmin` is committed AND whose transaction ID is ≤ the snapshot ID. Concurrent commits with higher transaction IDs produce row versions with higher `xmin` values — invisible to the snapshot. Result: re-reading the same row within the transaction always finds the same version.

**Level 4 — Why it was designed this way (senior/staff):**
Non-repeatable reads are often confused with phantom reads, but they're distinct. A non-repeatable read involves a changed value in an existing row. A phantom read involves new rows appearing (or disappearing). REPEATABLE READ prevents value changes to existing rows; it doesn't prevent new rows from appearing (phantoms). The distinction matters: REPEATABLE READ is sufficient for "re-read same row must return same value" patterns, but SERIALIZABLE is needed when "scan of a row range must return same set of rows" patterns are required. In practice, most application-level bugs from non-repeatable reads are eliminated by using `SELECT FOR UPDATE` at READ COMMITTED — locking the specific rows being read-modify-written — rather than upgrading the whole transaction to REPEATABLE READ.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ NON-REPEATABLE READ PREVENTION (MVCC)        │
├──────────────────────────────────────────────┤
│                                              │
│  READ COMMITTED (anomaly allowed):           │
│    T1 reads row A: snapshot = latest commit  │
│    T2 commits update to row A               │
│    T1 reads row A again: snapshot refreshed  │
│    → T1 sees T2's committed update           │
│    → Non-repeatable read occurred            │
│                                              │
│  REPEATABLE READ (anomaly prevented):        │
│    T1 BEGIN → snapshot_id = 500              │
│                                              │
│  Row A versions:                             │
│  ┌───────────────────────────────────────┐   │
│  │ xmin=490(committed) | val='old_value' │   │
│  │ xmin=505(committed) | val='new_value' │   │
│  └───────────────────────────────────────┘   │
│                                              │
│    T1 reads row A: sees xmin=490 ✅          │
│    (xmin=505 > snapshot_id=500 → invisible) │
│    T1 reads row A again: still sees 490 ✅   │
│    → Same value → non-repeatable read        │
│       prevented                              │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
T1 BEGIN (REPEATABLE READ) → snapshot_id recorded
→ T1 reads row A: snapshot value
→ T2 commits update to row A (new xmin > snapshot_id)
→ [NON-REPEATABLE READ prevention ← YOU ARE HERE]
→ T1 reads row A again: same snapshot value
→ T1 computes and writes consistently → COMMIT
```

**FAILURE PATH:**

```
T1 uses REPEATABLE READ but ignores serialization errors
→ T1 writes based on stale snapshot
→ Logical inconsistency: write assumes old value, DB has new value
→ Lost update / incorrect derived value committed
```

**WHAT CHANGES AT SCALE:**
Under high read-modify-write concurrency with REPEATABLE READ, multiple transactions may each see consistent snapshots but produce conflicting writes. REPEATABLE READ prevents non-repeatable reads but does not prevent write skew or lost updates — these require SERIALIZABLE or explicit locking. At scale, the choice between REPEATABLE READ + SELECT FOR UPDATE vs SERIALIZABLE determines the abort/retry rate and lock contention profile.

---

### ⚖️ Comparison Table

| Anomaly                 | Data State of Writer | Prevention Level    | Risk to Application                              |
| ----------------------- | -------------------- | ------------------- | ------------------------------------------------ |
| Dirty Read              | Uncommitted          | READ COMMITTED      | Critical — reading phantom data                  |
| **Non-Repeatable Read** | **Committed**        | **REPEATABLE READ** | **High — computed values based on changed data** |
| Phantom Read            | Committed (new rows) | SERIALIZABLE        | Medium-High — missing/extra rows in range query  |
| Write Skew              | Committed            | SERIALIZABLE        | High — business invariants violated silently     |

How to choose: If your transaction reads the same row multiple times and derives values, use REPEATABLE READ or SELECT FOR UPDATE. If you need row stability for range queries or business invariants across multiple rows, use SERIALIZABLE.

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Non-repeatable reads involve dirty (uncommitted) data     | Non-repeatable reads involve only committed data — both values seen are legitimate; it's the change between reads that's the problem                                   |
| REPEATABLE READ prevents all concurrency anomalies        | REPEATABLE READ prevents dirty reads and non-repeatable reads, but NOT phantom reads (in PostgreSQL) and NOT write skew — SERIALIZABLE is needed for those             |
| Non-repeatable reads and phantom reads are the same       | Different: non-repeatable read = existing row value changed; phantom read = new rows appeared or disappeared in a range query                                          |
| READ COMMITTED is always sufficient if you read only once | If your "read once" value is used to compute and write a new value, a concurrent write can invalidate your assumption — SELECT FOR UPDATE or REPEATABLE READ is needed |

---

### 🚨 Failure Modes & Diagnosis

**1. Lost Update from Read-Compute-Write at READ COMMITTED**

**Symptom:** Account balance wrong after concurrent transfers; inventory count drifts negative; counter values don't match expected totals.

**Root Cause:** Two transactions each read the same value, compute a new value, and write — the second write overwrites the first without knowing about it.

**Diagnostic:**

```sql
-- Find accounts with balance that doesn't match transaction history
SELECT a.id, a.balance,
       SUM(t.amount) as computed_balance
FROM accounts a
JOIN transactions t ON t.account_id = a.id
GROUP BY a.id, a.balance
HAVING a.balance != SUM(t.amount);
```

**Fix:**

```sql
-- Option A: SELECT FOR UPDATE (pessimistic lock)
BEGIN;
SELECT balance FROM accounts WHERE id = 42 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 42;
COMMIT;

-- Option B: Atomic update (preferred)
UPDATE accounts SET balance = balance - 100
WHERE id = 42 AND balance >= 100;
-- check rows affected
```

**Prevention:** For any read-then-write on shared mutable state, use `SELECT FOR UPDATE` or atomic `UPDATE ... WHERE` rather than separate read and write statements.

---

**2. Stale Snapshot in Long-Running REPEATABLE READ Transaction**

**Symptom:** Application reads data that appears hours old; decisions made on stale inventory, stale prices, or stale user state.

**Root Cause:** A long-running REPEATABLE READ transaction started its snapshot hours ago; all reads within it see data as of that old snapshot, missing all intervening commits.

**Diagnostic:**

```sql
-- PostgreSQL: find long-running transactions with old snapshots
SELECT pid,
       now() - xact_start AS age,
       state, query,
       backend_xid
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start;
```

**Fix:** Keep REPEATABLE READ transactions short. For long-running processes that need to read fresh data, use READ COMMITTED and accept that individual reads may see different snapshots — or break the work into short transactions.

**Prevention:** Set `statement_timeout` and `idle_in_transaction_session_timeout` to automatically terminate stale long-running transactions.

---

**3. Failing to Handle Serialization Failure Retry**

**Symptom:** Under SERIALIZABLE isolation, random transaction failures with `ERROR: could not serialize access`; no retry logic means these silently fail; data is never written.

**Root Cause:** Application uses SERIALIZABLE isolation without implementing retry logic for serialization failures — these errors are expected and normal under high concurrency.

**Diagnostic:**

```bash
# Count serialization failures in PostgreSQL logs
grep "could not serialize" /var/log/postgresql/*.log | \
  awk '{print $1,$2}' | sort | uniq -c | sort -rn | head -20
```

**Fix:**

```java
// Retry on serialization failure
@Retryable(
    value = {CannotSerializeTransactionException.class},
    maxAttempts = 5,
    backoff = @Backoff(delay = 100, multiplier = 2))
@Transactional(isolation = Isolation.SERIALIZABLE)
public void processOrder(Order order) {
    // business logic
}
```

**Prevention:** Any code using SERIALIZABLE isolation must implement retry logic. Design retried transactions to be idempotent. Set a reasonable max retry count with exponential backoff.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Isolation Levels` — non-repeatable read is the anomaly that REPEATABLE READ prevents; understand the isolation level spectrum
- `Dirty Read` — the weaker anomaly (uncommitted data); non-repeatable read is the next level (committed data changed)
- `MVCC` — the mechanism that implements snapshot isolation to prevent non-repeatable reads

**Builds On This (learn these next):**

- `Phantom Read` — the next anomaly up; new rows appear in range queries; requires SERIALIZABLE to prevent
- `Write Skew` — a related anomaly where two transactions make locally valid writes that together violate a constraint
- `Locking (Row, Table, Gap, Next-Key)` — SELECT FOR UPDATE as an alternative to REPEATABLE READ for specific row protection

**Alternatives / Comparisons:**

- `Dirty Read` — involves uncommitted writes; non-repeatable read involves committed writes
- `Phantom Read` — row value changed vs. rows appeared/disappeared in a set

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Same row read twice returns different     │
│              │ values within one transaction             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Read-compute-write uses stale data;       │
│ SOLVES       │ financial calculations become incorrect   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Unlike dirty reads, both values are real  │
│              │ committed data — the change is the problem│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ REPEATABLE READ for read-compute-write;   │
│              │ or SELECT FOR UPDATE at READ COMMITTED    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use REPEATABLE READ for long-running│
│              │ transactions — stale snapshots accumulate │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Consistent reads vs MVCC bloat from       │
│              │ long-lived transaction snapshots          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The price changed while you were getting  │
│              │  your wallet — REPEATABLE READ freezes it"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Phantom Read → Write Skew → MVCC          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A — System Interaction) A ticket booking system uses REPEATABLE READ. Transaction A reads "5 tickets available" and is about to INSERT a booking. Transaction B commits a booking reducing available tickets to 4. Transaction A still sees 5 (snapshot). Transaction A inserts its booking — now 4 seats are sold but the system thinks 5 exist (its snapshot value was 5, so it didn't check the actual remaining count). How does this differ from a non-repeatable read causing a problem, and which isolation level + SQL pattern correctly prevents overbooking here?

**Q2.** (TYPE E — First Principles Challenge) REPEATABLE READ prevents non-repeatable reads by freezing the snapshot at transaction start. But a long-running reporting transaction using REPEATABLE READ for 2 hours holds back PostgreSQL's MVCC cleanup, causing table bloat. Design an alternative mechanism to provide repeatable-read semantics for a single specific row (not the whole database snapshot) that allows MVCC cleanup to proceed normally — what are the trade-offs of this targeted approach?
