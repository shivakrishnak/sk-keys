---
id: SYD-041
title: "Write-Ahead Logging (System)"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-040, SYD-039
used_by: SYD-042, SYD-023
related: SYD-040, SYD-038, SYD-042
tags:
  - distributed
  - database
  - reliability
  - deep-dive
  - internals
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 41
permalink: /syd/write-ahead-logging-system/
---

# SYD-041 - Write-Ahead Logging (System)

⚡ TL;DR - WAL writes every change to a sequential log before applying it to the actual data structure, enabling crash recovery and replication with minimal performance cost.

| SYD-041         | Category: System Design         | Difficulty: ★★★ |
| :-------------- | :------------------------------ | :-------------- |
| **Depends on:** | SYD-040, SYD-039                |                 |
| **Used by:**    | SYD-042, SYD-023                |                 |
| **Related:**    | SYD-040, SYD-038, SYD-042      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A database modifies pages in memory and writes them to disk. Midway through updating a B-tree index, the server crashes. The disk now contains a partially-written, corrupted data structure. Recovery requires scanning every page to find inconsistencies - taking minutes or hours for large databases.

**THE BREAKING POINT:**
In-place writes to complex data structures are not atomic at the disk level. A multi-page update (B-tree rebalancing, row insert spanning pages) can be interrupted at any point. Without a recovery mechanism, every crash risks permanent data corruption.

**THE INVENTION MOMENT:**
Before modifying anything on disk, write a log entry describing the intended change. The log is append-only (sequential writes - fast). After the log entry is durable, apply the change. If the system crashes, replay the log from the last checkpoint to reconstruct state. The log is the truth; the data files are a cached projection of the log.

**EVOLUTION:**
WAL originated in ARIES (Algorithm for Recovery and Isolation Exploiting Semantics, IBM 1992). PostgreSQL, MySQL/InnoDB, SQLite all use WAL internally. Kafka's durability model is WAL at the message level. The pattern spread to application-level systems: event sourcing, distributed state machines, and blockchain (each block is a WAL entry).

---

### 📘 Textbook Definition

**Write-Ahead Logging (WAL)** is a durability technique where all changes to a data structure are first recorded in a sequential, append-only log before being applied to the primary storage. The log entry must be durably written (fsync to disk) before the data modification is considered committed. WAL enables crash recovery (replay the log) and replication (ship the log to replicas).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Record the plan before executing it - so if execution is interrupted, you can finish from the plan.

**One analogy:**

> WAL is like a chef writing down every recipe step in a notebook before cooking. If the kitchen burns down mid-meal, you can restart from the notebook and know exactly what was done and what is left.

**One insight:**
Sequential appends to a log are orders of magnitude faster than random writes to data pages. WAL converts random writes (heap/index updates) into sequential log appends + deferred random writes - a substantial performance win on spinning disks and a predictable pattern on SSDs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Log entries must be written to durable storage before the corresponding data page is modified.
2. The log must be complete enough to reconstruct any committed state.
3. The log is append-only and sequential - individual log entries are never modified.
4. Checkpoints periodically flush dirty pages so log replay can start from a recent point.

**DERIVED DESIGN:**
On every write: append log entry (LSN=Log Sequence Number, operation, before/after values). Fsync the log entry. Then modify the buffer pool page. On crash: read from last checkpoint LSN, replay log entries in order, roll back any incomplete transactions.

**THE TRADE-OFFS:**
**Gain:** Crash safety without full fsync on every data page write; fast sequential log I/O; enables streaming replication by shipping the log.
**Cost:** Each write = log append + data write (2 writes instead of 1); log must be managed (rotation, archival); recovery time proportional to log replay distance from checkpoint.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** You need a record of intent separate from the data itself to recover from partial execution.
**Accidental:** LSN management, log segment rotation, WAL compression, parallel recovery workers.

---

### 🧪 Thought Experiment

**SETUP:** A user updates their profile. The DB modifies 3 pages: the row data page, the email index, and the username index. Power fails after page 1 is written but before pages 2 and 3.

**WHAT HAPPENS WITHOUT WAL:**
Data page 1 (row) is updated. Index pages 2 and 3 are not. The row says `email = new@example.com` but the email index still points to the old row. Queries by email find nothing. Queries by username return the wrong row. Data corruption. Recovery: full table scan to rebuild indexes - possibly hours.

**WHAT HAPPENS WITH WAL:**
Before modifying any page, WAL entry is written: `UPDATE row 42: email=new@, idx_email: old->new, idx_user: old->new`. WAL is fsynced. Power fails. On restart: WAL shows the incomplete transaction. Since WAL entry was written but data pages were not fully updated, the DB replays from the last checkpoint. All 3 pages are correctly updated from the log. No corruption.

**THE INSIGHT:**
WAL separates the record of intent from the execution. Execution can fail; intent (the log) is durable. Recovery is deterministic: replay the log. This is the core insight behind both crash recovery and replication.

---

### 🧠 Mental Model / Analogy

> WAL is like a court reporter at a trial. Before anything officially happens (is committed to the record), the reporter writes it down verbatim. If the judge's gavel (power) fails mid-session, you replay the transcript from the last break point to reconstruct exactly where you were.

- **Transcript** = WAL log file
- **Verbatim entry** = log record with LSN, operation, old/new values
- **Gavel fail** = system crash
- **Break point** = checkpoint
- **Replaying transcript** = WAL replay on recovery
- **Official court record** = data pages on disk

Where this analogy breaks down: a court reporter writes after events happen; WAL writes before the data page is modified - the order is critical.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before changing data, write down what you're about to change. If something breaks, use the written record to redo it correctly. Like saving your work before each edit.

**Level 2 - How to use it (junior developer):**
WAL is built into every ACID database - you don't implement it. You configure it: `wal_level`, `synchronous_commit`, checkpoint frequency. Understanding WAL explains why `fsync=off` is dangerous (disables WAL durability) and why streaming replication works (ship WAL files to replica).

**Level 3 - How it works (mid-level engineer):**
Each transaction writes log records to the WAL buffer. On commit, WAL buffer is flushed to disk (fsync). Background writer flushes dirty data pages periodically. Checkpoint: all dirty data pages flushed + checkpoint record written. Recovery: start from last checkpoint LSN, apply all subsequent WAL records (redo phase), then undo any uncommitted transactions (undo phase).

**Level 4 - Why it was designed this way (senior/staff):**
ARIES formalized the WAL protocol with three rules: (1) All log records for a transaction must be written before the transaction commits. (2) Log record for a page update must be written before the dirty page is flushed. (3) Log must be written to stable storage before the transaction is reported committed. These rules ensure atomicity and durability. The redo/undo separation allows partial-transaction recovery. Physical logging (actual before/after page bytes) vs logical logging (SQL statement) vs logical-physical (operation + tuple ID) each have different recovery performance characteristics.

**Expert Thinking Cues:**
- Ask: "What is your WAL retention window? Is it long enough for slow replicas to catch up?"
- Ask: "What is the impact of `synchronous_commit = off` on durability?"
- Red flag: low `checkpoint_completion_target` causing I/O spikes during checkpoints
- Red flag: WAL disk filling up due to slow replicas or long-running transactions

---

### ⚙️ How It Works (Mechanism)

**Write path:**
```
Transaction modifies row
  1. Write WAL record to WAL buffer (memory)
     {LSN, txn_id, op: UPDATE, tbl, row_id,
      old_values, new_values}
  2. Mark data page as dirty in buffer pool
  3. On COMMIT:
     a. Flush WAL buffer to WAL file (fsync)
     b. Return success to client
  4. Background: bgwriter flushes dirty data pages
     (not on critical path)
  5. Periodic checkpoint: flush all dirty pages
     + write checkpoint record to WAL
```

**Recovery on crash:**
```
1. Find last checkpoint LSN in pg_control
2. Open WAL from checkpoint LSN
3. REDO phase: replay all log records forward
   - Apply committed changes to data pages
   - Reconstruct in-doubt transactions
4. UNDO phase: rollback uncommitted transactions
   using before-images in log records
5. Database is consistent - open for connections
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Client: BEGIN / UPDATE row]
         |
         v
[WAL record appended to WAL buffer]  <- YOU ARE HERE
         |
         v
[Data page marked dirty in buffer pool]
         |
         v
[Client: COMMIT]
         |
         v
[WAL buffer flushed to disk (fsync)]
         |
         v
[Success returned to client]
         |
    (background)
         v
[Dirty pages written to data files]
         |
         v
[Checkpoint: all dirty pages flushed]
```

**FAILURE PATH:**
```
[Server crashes mid-transaction]
         |
[Restart: find last checkpoint]
         |
[Replay WAL forward from checkpoint]
         |
[Undo incomplete transactions]
         |
[Database consistent at last commit]
```

**WHAT CHANGES AT SCALE:**
High write volume generates large WAL. WAL must be replicated to followers before it is recycled. Slow followers cause WAL accumulation - risk of disk fill. Set `wal_keep_size` appropriately. WAL archival to object storage (S3) enables point-in-time recovery.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
WAL streaming is the foundation of leader-follower replication. The leader ships WAL segments or uses streaming replication (continuous WAL shipping). Followers have a WAL receiver process that applies records. Replication lag = WAL position on leader - WAL position applied by follower. WAL provides a globally ordered sequence that makes replication deterministic.

---

### 💻 Code Example

**BAD - disabling fsync (data loss risk):**
```sql
-- BAD: disabling fsync = WAL not durable
-- OS crash can lose committed transactions
ALTER SYSTEM SET fsync = off;
-- BAD: also removes crash safety
ALTER SYSTEM SET synchronous_commit = off;
```

**GOOD - understand and tune WAL safely:**
```sql
-- GOOD: check current WAL settings
SHOW wal_level;       -- minimal/replica/logical
SHOW synchronous_commit; -- on/off/remote_write

-- GOOD: enable WAL archiving for PITR
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command =
  'cp %p /mnt/wal_archive/%f';

-- GOOD: monitor WAL lag to replicas
SELECT client_addr,
       state,
       pg_wal_lsn_diff(
         pg_current_wal_lsn(),
         sent_lsn
       ) AS behind_bytes
FROM pg_stat_replication;

-- GOOD: measure WAL generation rate
SELECT pg_wal_lsn_diff(
  pg_current_wal_lsn(),
  '0/0'
) AS total_wal_bytes;
```

**GOOD - application-level WAL equivalent (event sourcing):**
```python
# Application-level WAL: write intent before state
import json, time

class EventLog:
    """Append-only event log - application-level WAL"""
    def __init__(self, path):
        self.path = path

    def append(self, event_type, payload):
        entry = {
            "lsn": time.time_ns(),
            "type": event_type,
            "payload": payload,
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            # fsync equivalent: ensure durable
            import os; os.fsync(f.fileno())
        return entry["lsn"]

# Write intent BEFORE mutating state
log = EventLog("/var/log/app/wal.log")
lsn = log.append("TRANSFER", {
    "from": 1, "to": 2, "amount": 100
})
# Only mutate state after log is durable
apply_transfer(from_id=1, to_id=2, amount=100)
```

**How to test / verify correctness:**
- Write 1000 rows, kill DB process mid-write (kill -9), restart - assert no corruption and all committed data present.
- Enable WAL archiving; restore from archive to a new instance; verify data matches.
- Measure recovery time from a 1GB WAL segment gap.

---

### ⚖️ Comparison Table

| Durability approach      | Write cost  | Recovery speed | Replication | Use case              |
| ------------------------ | ----------- | -------------- | ----------- | --------------------- |
| WAL (full fsync)         | 2x seq I/O  | Fast           | Yes         | Default ACID DB       |
| WAL (sync_commit=off)    | 1x seq I/O  | Fast           | Yes         | Non-critical writes   |
| Shadow paging            | High        | Slow           | Difficult   | Old style (Berkeley)  |
| No WAL (dangerous)       | 1x random   | May not recover | No         | Never in production   |
| Logical logging (SQL)    | Smaller log | Medium         | Cross-version | Logical replication |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "WAL doubles write cost" | WAL writes are sequential (fast); data page writes are deferred and batched. Net I/O is often less than naive random writes. |
| "Disabling fsync makes WAL unsafe" | Disabling fsync loses crash safety for committed data. You can lose confirmed transactions. This is not a valid performance optimization in production. |
| "WAL is only for crash recovery" | WAL is also the mechanism for streaming replication, point-in-time recovery (PITR), logical replication, and change data capture (CDC). |
| "Short WAL retention is safe" | If replicas lag more than your WAL retention, they can no longer replicate and must be rebuilt from scratch. Retain WAL at least as long as your slowest replica's maximum lag. |
| "Checkpoints have no performance impact" | Checkpoints flush all dirty pages - a burst of I/O that can cause latency spikes. Tune `checkpoint_completion_target` to spread I/O over time. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: WAL disk fill causes DB crash**

**Symptom:** PostgreSQL reports "no space left on device" for WAL directory; DB stops accepting writes.

**Root Cause:** Slow replica holding a replication slot causes WAL segments to accumulate.

**Diagnostic:**
```sql
-- Check replication slots and WAL retained
SELECT slot_name, active, pg_wal_lsn_diff(
    pg_current_wal_lsn(), confirmed_flush_lsn
) AS retained_bytes
FROM pg_replication_slots;

-- Check WAL directory size
SELECT pg_size_pretty(
  sum(size)
) FROM pg_ls_waldir();
```

**Fix:** Drop stale replication slots; increase WAL disk; reduce `max_slot_wal_keep_size`.

**Prevention:** Alert when WAL retained > 50% of WAL disk capacity.

---

**Failure Mode 2: Long recovery time after crash**

**Symptom:** Database takes 30+ minutes to recover after crash.

**Root Cause:** Last checkpoint was very old (small `checkpoint_timeout` or infrequent checkpointing); large WAL replay window.

**Diagnostic:**
```bash
# Check recovery progress in PostgreSQL log
grep "redo in progress" /var/log/postgresql/postgresql.log
grep "consistent recovery state reached" /var/log/...
```

**Fix:** Reduce `checkpoint_timeout` to force more frequent checkpoints, reducing WAL replay distance.

**Prevention:** Test recovery time after forced crash in staging. Alert if WAL size since last checkpoint > 1GB.

---

**Failure Mode 3: Data loss from synchronous_commit = off**

**Symptom:** Committed transactions missing after server crash.

**Root Cause:** `synchronous_commit = off` delays WAL flush - committed data not yet on disk.

**Diagnostic:**
```sql
SHOW synchronous_commit;
-- Check for recently missing records after crash
SELECT count(*) FROM orders
WHERE created_at > '<crash_time>' - INTERVAL '1s';
```

**Fix:** Set `synchronous_commit = on` for any business-critical data. Accept write latency increase.

**Prevention:** Never use `synchronous_commit = off` for financial or user account data.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-040 - Leader-Follower Pattern]] - WAL is the replication mechanism in leader-follower
- [[SYD-039 - Distributed Locks]] - WAL operations require ordering guarantees locks provide

**Builds On This (learn these next):**
- [[SYD-042 - Data Partitioning Strategies]] - WAL per shard enables distributed WAL
- [[SYD-023 - Geo-Replication]] - WAL shipping across regions is the foundation

**Alternatives / Comparisons:**
- [[SYD-038 - Idempotency Key]] - application-level durability alternative for event processing

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Append-only intent log written   │
│              │ before any data page is changed  │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Partial writes causing data      │
│ IT SOLVES    │ corruption on crash              │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Sequential log writes are fast;  │
│              │ replay gives crash safety        │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Always - built into every ACID   │
│              │ database by default              │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Never disable WAL safety for     │
│              │ production financial data        │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Extra I/O per write vs full      │
│              │ crash recovery + replication     │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Log the intent first; then act. │
│              │ Replay the log to recover."      │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-042 Data Partitioning        │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. WAL must be fsynced before the transaction is confirmed - never disable fsync in production.
2. WAL enables both crash recovery and streaming replication from the same mechanism.
3. Monitor WAL retention: if replicas lag more than your WAL window, they fall behind irreparably.

**Interview one-liner:** "WAL writes every change to a sequential log before touching data pages - on crash, replay the log from the last checkpoint to reconstruct any committed state."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Separate the record of intent from the execution of intent. Intent (the log) can be made durable cheaply with sequential writes. Execution (data page updates) can be deferred. Recovery is simply re-executing all durable intents.

**Where else this pattern appears:**
- **Event sourcing:** Application stores events (the log) as the source of truth; current state is projected from the event log - identical to WAL.
- **Kafka:** Each topic partition is an append-only log. Consumer offset = LSN. Replay from any offset = crash recovery.
- **Blockchain:** Each block is a WAL entry describing state transitions. The full chain replays from genesis = complete history.

---

### 💡 The Surprising Truth

PostgreSQL's WAL makes reads slower, not faster. Every read must check the visibility map and potentially follow the WAL chain to determine which version of a row is visible (MVCC). The performance benefit of WAL is entirely on the write side - sequential log writes instead of synchronous random page writes. The tradeoff is a richer implementation that handles concurrent readers and writers without locking.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** PostgreSQL's `checkpoint_completion_target = 0.05` means each checkpoint completes all I/O within 5% of `checkpoint_timeout`. At `checkpoint_timeout = 5min`, that means 15 seconds of I/O burst every 5 minutes. What happens to write latency during checkpoint, and what value of `checkpoint_completion_target` would you set instead?

*Hint:* Investigate how checkpoint I/O competes with normal write I/O in the OS I/O scheduler. Then look at what PostgreSQL documentation recommends for `checkpoint_completion_target` on write-heavy workloads (hint: 0.9 is common).

**Q2 (Scale):** A write-heavy service generates 1GB of WAL per minute. You have 3 read replicas: one in the same datacenter (5ms lag), one in a remote DC (50ms lag), and one intentionally slow batch analytics replica (5-minute lag). What WAL retention do you need, and how do you prevent the analytics replica from starving disk space?

*Hint:* Retention must cover the slowest replica's lag window. Explore `max_slot_wal_keep_size` in PostgreSQL 13+ and the trade-off between WAL disk cost and replica rebuild cost.

**Q3 (First Principles):** Kafka uses a WAL to store messages. Cassandra uses a commit log (WAL equivalent) but does not support replication via the commit log. Why does Kafka's WAL enable log-based replication while Cassandra's commit log does not?

*Hint:* Compare the WAL contents of each: Kafka's log contains the canonical data (the message IS the log entry); Cassandra's commit log is ephemeral (it exists to survive crashes of a single node, then compacted away once memtable is flushed). The canonical vs ephemeral distinction determines replication suitability.
