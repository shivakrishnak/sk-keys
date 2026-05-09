---
version: 1
layout: default
title: "Redo Log  Undo Log"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /databases/redo-log-undo-log/
id: DBF-029
category: Database Fundamentals
difficulty: ★★★
depends_on: WAL (Write-Ahead Log), Transaction, ACID, MVCC
used_by: Crash Recovery, Rollback, MVCC
related: WAL, Commit / Rollback, Durability, Atomicity
tags:
  - database
  - internals
  - durability
  - recovery
  - deep-dive
---

# DBF-029 - Redo Log  Undo Log

⚡ TL;DR - The redo log replays committed changes after a crash; the undo log reverses uncommitted changes during rollback. Together they guarantee both D (Durability) and A (Atomicity) in ACID.

| #424            | Category: Database Fundamentals                | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | WAL (Write-Ahead Log), Transaction, ACID, MVCC |                 |
| **Used by:**    | Crash Recovery, Rollback, MVCC                 |                 |
| **Related:**    | WAL, Commit / Rollback, Durability, Atomicity  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A database handles a multi-step transfer: debit account A, credit account B. The debit happens (A's balance reduced on disk). Before the credit completes, the server crashes. Restart: account A has been debited but B has not been credited. $1,000 has vanished. There is no log of what was attempted, no mechanism to either complete the credit or reverse the debit. The database has violated Atomicity - partial updates are persisted.

**THE BREAKING POINT:**
Two failure modes require two distinct log types:

1. **Committed data lost on crash** → need a redo log (re-apply committed changes).
2. **Uncommitted partial changes survive crash** → need an undo log (reverse incomplete changes on recovery, or allow explicit rollback).

A single mechanism cannot solve both - they are opposites.

**THE INVENTION MOMENT:**
"Use two logs: one to redo what was committed, one to undo what wasn't."

---

### 📘 Textbook Definition

The **redo log** is a write-ahead log recording the "after image" of every data change (the new value) - used to re-apply committed changes after a crash, ensuring Durability. The **undo log** records the "before image" of every data change (the old value) - used to reverse uncommitted changes during rollback (ensuring Atomicity) and to provide old versions of rows to concurrent readers (enabling MVCC). In PostgreSQL, WAL serves as the redo log; old row versions in the heap serve as the undo mechanism. In MySQL InnoDB, there are explicit separate structures: the redo log (ring buffer in `ib_logfile`) and the undo tablespace (separate files).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Redo log = "play forward" for commits after crash; undo log = "play backward" for rollbacks and old read versions.

**One analogy:**

> A home video camera records the "before" and "after" of every room renovation. The undo tape (before) lets you undo any changes if a project goes wrong - restoring the original state. The redo tape (after) lets you replay what was done if you need to reconstruct the work. A database uses both: undo for "this transaction failed, revert it"; redo for "the server crashed, but this was committed - reapply it."

**One insight:**
In PostgreSQL, the "undo mechanism" isn't a separate log - old row versions in the heap serve as the undo log, which is why PostgreSQL needs VACUUM. InnoDB's explicit undo tablespace allows it to discard old versions immediately when no reader needs them (via the purge thread), without requiring the full heap scan that PostgreSQL's VACUUM performs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Redo invariant:** A committed transaction's changes must survive a crash. On recovery, redo log is replayed forward from last checkpoint to restore committed state.
2. **Undo invariant:** An uncommitted transaction's changes must not be visible after recovery (Atomicity). On recovery, in-progress transactions are reversed using the undo log.
3. **Order:** Redo first (apply all changes, including committed ones), then undo (reverse uncommitted ones). This is the ARIES algorithm.
4. **MVCC undo:** The undo log also provides old row versions to concurrent readers under snapshot isolation.

**DERIVED DESIGN:**
**ARIES recovery algorithm (3 phases):**

1. **Analysis phase:** Scan WAL forward from the last checkpoint to determine which pages are dirty (modified but not flushed) and which transactions were active at crash time.
2. **Redo phase:** Replay ALL WAL records from the oldest dirty page's LSN - both committed and uncommitted transactions. Goal: restore the exact in-memory state at crash time.
3. **Undo phase:** For each transaction that was active at crash time (no COMMIT record), apply undo log entries in reverse order to reverse their changes.

**InnoDB specifics:**

- **Redo log:** Circular ring buffer (`ib_logfile0`, `ib_logfile1` historically; auto-sized single file in MySQL 8.0.30+). Records physical changes to InnoDB pages. Flushed synchronously on commit.
- **Undo log:** Stored in undo tablespace files. Records the before-image of every modified row. Kept until no active transaction needs the old version; purge thread deletes obsolete undo records.

**PostgreSQL specifics:**

- **Redo log = WAL:** All page changes written to WAL. No separate redo log.
- **Undo = heap old versions:** Old row tuples remain in the heap with `xmax` set. VACUUM eventually removes them.
- No explicit undo log; rollback is achieved by marking xid as aborted in `pg_xact` - no data is physically reversed.

**THE TRADE-OFFS:**
**InnoDB explicit undo log:**

- Gain: Compact clustered index (only current version); purge thread cleans up without needing full table scan.
- Cost: Undo log I/O; long-running transactions hold undo history; undo log reads required for long version chains.

**PostgreSQL heap-as-undo:**

- Gain: Simple model; reads don't traverse undo chains (old versions in same heap, same I/O access pattern).
- Cost: VACUUM required; heap and index bloat; VACUUM can't always keep up with write rate.

---

### 🧪 Thought Experiment

**SETUP:**
MySQL InnoDB database. Transaction T1 starts: `UPDATE accounts SET balance = balance - 1000 WHERE id = 42` (balance was 5000; new value: 4000). Server crashes after the undo log and redo log are written but before the transaction commits.

**CRASH RECOVERY - WHAT HAPPENS:**

1. **Redo phase:** InnoDB reads redo log. Finds redo record: "page X, offset Y: balance changed to 4000 for row id=42." Data file page is stale (may still have 5000). InnoDB replays redo → page now shows 4000. T1 still has no COMMIT record.

2. **Undo phase:** InnoDB finds T1 in the transaction state table (no COMMIT). Reads T1's undo log: "Before UPDATE account_id=42: balance was 5000." InnoDB applies undo: sets balance back to 5000 for row id=42.

3. **Result:** Database is consistent - balance is 5000 as if T1 never happened. Atomicity preserved.

**CONTRAST - COMMITTED TRANSACTION:**
If T1 had committed (COMMIT record in redo log), the redo phase restores balance=4000, the undo phase skips T1 (it has a COMMIT record), and the committed change is preserved. Durability preserved.

**THE INSIGHT:**
The same physical data page ends up in different states depending only on whether a COMMIT record exists in the redo log - the redo and undo logs are the authoritative source of truth, not the data pages.

---

### 🧠 Mental Model / Analogy

> Think of redo/undo as a pair of video tapes for a bank vault. The "redo tape" records the final state of every completed transaction: "vault now contains $X." The "undo tape" records the starting state of every in-progress transaction: "vault started with $Y." After a break-in (crash):
>
> 1. The redo tape is played forward: restore all completed vault states.
> 2. The undo tape is played backward: reverse all incomplete transactions.
>
> The vault ends up exactly as if nothing bad happened - every completed transaction preserved, every incomplete transaction reversed.

- "Redo tape → vault state" = redo log: after-image of committed changes
- "Undo tape → starting state" = undo log: before-image of in-progress changes
- "Break-in" = server crash
- "Playing tapes" = ARIES recovery (redo then undo phase)
- "Vault contents" = data pages

Where this analogy breaks down: the undo tape is also used during normal operation (for MVCC) - concurrent readers "watch" the undo tape to see old versions without needing to wait for the vault to be reset.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Two types of log help databases survive crashes and mistakes: the redo log ("replay what was done") and the undo log ("reverse what wasn't finished"). Together they make sure databases always land in a consistent state - whether recovery from a crash or rolling back a failed transaction.

**Level 2 - How to use it (junior developer):**
As a developer, these logs are invisible - they work automatically. You benefit from them when: (a) a crash doesn't lose committed data (redo log); (b) `ROLLBACK` works instantly even for large transactions (undo log applied). Be aware: `synchronous_commit = on` ensures redo log is flushed before commit acknowledgment; setting `innodb_flush_log_at_trx_commit = 1` in MySQL does the same. Changing these to non-durable values trades crash safety for performance.

**Level 3 - How it works (mid-level engineer):**
InnoDB undo log: stored in separate undo tablespace files. Each modified row gets an undo log record pointing back to the previous version. Undo records form a linked list (undo chain) - the current row version points to its undo log record, which points to the one before it. MVCC readers follow this chain to find the version visible to their snapshot. The purge thread monitors the oldest active read view - undo records older than the oldest read view are deleted. This is why a long-running transaction prevents purge, causing undo log growth.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental tension: redo and undo logs serve opposite purposes and have opposite performance characteristics. Redo logs must be written synchronously at commit (durability requires it). Undo logs must be written before data page changes (Atomicity requires they be available before any change is visible). This means EVERY data modification requires writing to BOTH logs before the data page can be modified. InnoDB's redo log is a fixed-size ring buffer - when it fills up, InnoDB must flush dirty pages and advance the checkpoint, causing a "redo log flush storm." MySQL 8.0.30 changed this to auto-sizing. PostgreSQL's combined WAL (redo only) with heap-based undo sidesteps the ring buffer limitation but introduces VACUUM complexity. The ARIES algorithm's insight - redo everything first (even uncommitted), then undo selectively - is counter-intuitive but correct: it minimizes the state that needs to be tracked during recovery and handles the case where undo itself needs to be recoverable (undo changes are also WAL-logged).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ INNODB: REDO + UNDO LOG FLOW                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  UPDATE accounts SET balance=4000 WHERE id=42       │
│  (old value: 5000)                                   │
│                                                      │
│  1. UNDO LOG:                                        │
│     → Write before-image to undo tablespace:         │
│       "row id=42: balance was 5000"                 │
│     → Row's undo pointer updated to this record     │
│                                                      │
│  2. DATA PAGE: balance updated to 4000 (in buffer)  │
│                                                      │
│  3. REDO LOG:                                        │
│     → Append after-image: "page X, balance=4000"   │
│                                                      │
│  4. COMMIT: redo log flushed → client ACK            │
│                                                      │
│  5. PURGE (async): once no snapshot needs 5000,     │
│     undo record for id=42 deleted                   │
│                                                      │
├──────────────────────────────────────────────────────┤
│ RECOVERY (crash after step 3, no COMMIT):           │
│                                                      │
│  REDO phase: replay redo log → page shows 4000      │
│  UNDO phase: T1 has no COMMIT → apply undo:         │
│     → balance restored to 5000                      │
│  Result: as if T1 never ran                         │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Transaction modifies row
→ Undo log written (before-image)
→ Data page modified in buffer pool
→ Redo log written (after-image)
→ [REDO/UNDO LOG ← YOU ARE HERE]
→ COMMIT: redo log flushed → durable
→ Purge thread: remove undo records no reader needs
```

**FAILURE PATH:**

```
Long-running OLAP query on OLTP database
→ Open read view holds back purge thread
→ Undo log grows as writes accumulate
→ Undo tablespace fills disk
→ InnoDB: ERROR "undo tablespace is full"
→ Write operations begin failing
```

**WHAT CHANGES AT SCALE:**
At high write rates with long-running reads on InnoDB, undo log accumulation is a critical operational concern. On PostgreSQL, the equivalent is heap bloat from unvacuumed dead tuples. Both are caused by the same root cause: long-running transactions holding old snapshots. Solutions: route OLAP queries to a read replica; set `innodb_undo_log_truncate = ON` (MySQL 5.7.24+); set `idle_in_transaction_session_timeout` to limit idle transaction lifetimes.

---

### ⚖️ Comparison Table

| Log Type           | What It Records           | When Used                      | Enables                           | PostgreSQL Equivalent    |
| ------------------ | ------------------------- | ------------------------------ | --------------------------------- | ------------------------ |
| **Redo log**       | After-image (new values)  | Every write; flushed at commit | Crash recovery (re-apply commits) | WAL records              |
| **Undo log**       | Before-image (old values) | Every write; kept until purged | Rollback + MVCC old versions      | Heap old tuples + xmax   |
| **Binlog (MySQL)** | Logical row changes       | After commit                   | External replication, CDC         | Logical replication slot |

How to choose: Both redo and undo are automatic. Tune `innodb_flush_log_at_trx_commit` (MySQL) or `synchronous_commit` (PostgreSQL) to balance durability vs. performance. Monitor undo log size (MySQL) or dead tuple count (PostgreSQL) for long-running transaction impact.

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                   |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL has no undo log                                  | PostgreSQL uses old heap tuples as its undo mechanism - it's implicit rather than a separate structure; VACUUM is the equivalent of InnoDB's purge thread |
| Rollback is instant because undo log just "deletes" changes | Undo log physically reverses changes by writing them as new changes - a large transaction's rollback can take as long as the transaction itself           |
| Redo log and WAL are the same thing                         | PostgreSQL's WAL IS its redo log; InnoDB has separate redo log (ib_logfile) AND WAL equivalent (binlog) for different purposes                            |
| Undo log is only used for rollback                          | InnoDB's undo log is also the MVCC version chain - concurrent readers follow undo pointers to find old row versions matching their snapshot               |

---

### 🚨 Failure Modes & Diagnosis

**1. InnoDB Undo Log Tablespace Growth (Long-Running Transactions)**

**Symptom:** `ibdata1` or undo tablespace files growing; disk usage increasing; `SHOW ENGINE INNODB STATUS` shows large history list length.

**Root Cause:** Long-running read transaction holds an old read view, preventing the purge thread from deleting undo records. Undo records accumulate for every write since the read view was opened.

**Diagnostic:**

```sql
-- MySQL: history list length = unpurged undo records
SHOW ENGINE INNODB STATUS\G
-- Look for: History list length NNN
-- > 10,000 = potential issue; > 1,000,000 = serious

-- Find long-running transactions
SELECT trx_id,
       trx_started,
       NOW() - trx_started AS duration,
       trx_query,
       trx_rows_modified,
       trx_rows_locked
FROM information_schema.INNODB_TRX
ORDER BY trx_started ASC;
```

**Fix:** Terminate the long-running transaction. Enable `innodb_undo_log_truncate = ON` with `innodb_purge_rseg_truncate_frequency` tuned. Route long-running analytical queries to a read replica.

**Prevention:** Set `wait_timeout` / `interactive_timeout` for idle connections. Monitor history list length; alert at > 50,000. Use read replicas for OLAP to isolate long read views from OLTP writes.

---

**2. Redo Log Filling During High Write Bursts**

**Symptom (MySQL pre-8.0.30):** Write stalls; InnoDB slows significantly during write bursts; `SHOW ENGINE INNODB STATUS` shows checkpoint lag approaching redo log size.

**Root Cause:** Fixed-size redo log ring buffer fills up. InnoDB cannot accept new writes until dirty pages are flushed to advance the checkpoint, creating a "redo log flush storm."

**Diagnostic:**

```sql
-- MySQL: check redo log utilization
SELECT variable_name, variable_value
FROM performance_schema.global_status
WHERE variable_name IN (
  'Innodb_os_log_written',
  'Innodb_log_write_requests',
  'Innodb_log_writes'
);

-- Check redo log file size
SHOW VARIABLES LIKE 'innodb_log_file_size';
-- If redo log fills in < 1 hour at peak load → too small
```

**Fix (MySQL < 8.0.30):** Stop MySQL cleanly; increase `innodb_log_file_size` in `my.cnf` (e.g., 1–4 GB); restart. MySQL will regenerate redo log files. In MySQL 8.0.30+, redo log is auto-sized.

**Prevention:** Size redo log to hold at least 1 hour of write workload. Rule of thumb: set `innodb_log_file_size` to 25–50% of `innodb_buffer_pool_size`. Monitor redo log write rate.

---

**3. PostgreSQL Rollback of Large Transaction Takes Too Long**

**Symptom:** `ROLLBACK` on a large transaction (e.g., bulk INSERT of 10M rows that was aborted) takes minutes; application appears hung.

**Root Cause:** PostgreSQL's rollback marks the transaction's xid as aborted in `pg_xact` - this part is instant. But the heap tuples from the aborted transaction remain as dead tuples. VACUUM must eventually clean them. However, if the application is waiting for rollback to "free up space" - the space is not immediately reclaimed. Additionally, if rollback involves reversing many changes (PostgreSQL does physically rollback some scenarios), it can take time proportional to the work done.

**Diagnostic:**

```sql
-- Check for long-running idle-in-transaction sessions
SELECT pid, now() - xact_start AS duration, state, query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - xact_start > interval '5 min';

-- After rollback, check dead tuple accumulation
SELECT relname, n_dead_tup, n_live_tup
FROM pg_stat_user_tables
WHERE relname = 'my_bulk_insert_table';
```

**Fix:** After large aborted transactions, run `VACUUM my_table` immediately to reclaim space. Set `idle_in_transaction_session_timeout = '5min'` to auto-terminate idle transactions before they grow large.

**Prevention:** For bulk inserts that may need to be rolled back, consider staging tables (insert into a temporary or staging table, validate, then move to production). This limits the rollback scope.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `WAL (Write-Ahead Log)` - PostgreSQL WAL IS the redo log; understand WAL first
- `Transaction` - redo/undo logs are transaction-scoped
- `ACID` - redo log enables D (Durability); undo log enables A (Atomicity)

**Builds On This (learn these next):**

- `MVCC` - InnoDB uses undo log as its MVCC version chain
- `Crash Recovery` - the ARIES algorithm orchestrates redo then undo phases
- `Locking (Row, Table, Gap, Next-Key)` - row locks protect data pages while undo/redo logs protect consistency

**Alternatives / Comparisons:**

- `Commit / Rollback / Savepoint` - high-level operations that redo/undo logs make possible
- `Durability` - the ACID property that redo log implements
- `Atomicity` - the ACID property that undo log implements

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REDO LOG     │ After-image; replay forward on crash      │
│              │ → ensures Durability (committed = safe)   │
├──────────────┼───────────────────────────────────────────┤
│ UNDO LOG     │ Before-image; replay backward on rollback │
│              │ → ensures Atomicity + MVCC old versions   │
├──────────────┼───────────────────────────────────────────┤
│ ARIES ORDER  │ 1. Analysis → 2. Redo all → 3. Undo uncommitted │
├──────────────┼───────────────────────────────────────────┤
│ PostgreSQL   │ WAL = redo log; heap old tuples = undo    │
│ InnoDB       │ ib_logfile = redo; undo tablespace = undo │
├──────────────┼───────────────────────────────────────────┤
│ KEY FAILURE  │ Long-running transactions cause undo      │
│              │ accumulation → disk fill → write failures │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Redo = re-do what committed;             │
│              │  Undo = un-do what didn't"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ MVCC → Crash Recovery → Locking           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Trade-off) An analytics platform runs 2-hour OLAP queries against a MySQL InnoDB database that also handles high OLTP write rates. After 6 months, operations finds the undo tablespace has grown to 200 GB and history list length consistently exceeds 5 million. Design a complete architecture change that (a) preserves OLTP performance, (b) eliminates undo log accumulation from OLAP queries, and (c) maintains data freshness within 30 seconds for OLAP queries.

**Q2.** (TYPE E - First Principles Challenge) PostgreSQL's "undo mechanism" stores old row versions in the heap alongside current versions. MySQL InnoDB's undo mechanism stores old versions in a separate undo tablespace linked via row pointers. Design a synthetic benchmark that would produce dramatically different performance between the two approaches. What is the fundamental I/O access pattern difference, and at what point (what kind of query/workload) does each approach win?
