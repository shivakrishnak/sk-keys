---
layout: default
title: "WAL (Write-Ahead Log)"
parent: "Database Fundamentals"
nav_order: 28
permalink: /databases/wal/
id: DBF-028
category: Database Fundamentals
difficulty: ★★★
depends_on: Durability, Transaction, ACID
used_by: Replication, Point-in-Time Recovery, MVCC
related: Redo Log / Undo Log, Commit / Rollback, Durability
tags:
  - database
  - internals
  - durability
  - replication
  - deep-dive
---

# DBF-028 — WAL (Write-Ahead Log)

⚡ TL;DR — WAL (Write-Ahead Log) is the durability backbone of most databases: every change is written to a sequential append-only log before the data page is modified, guaranteeing crash recovery without losing committed transactions.

| #423            | Category: Database Fundamentals                    | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Durability, Transaction, ACID                      |                 |
| **Used by:**    | Replication, Point-in-Time Recovery, MVCC          |                 |
| **Related:**    | Redo Log / Undo Log, Commit / Rollback, Durability |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A database writes data directly to its main storage pages. At 3:47 AM the server loses power mid-write — a data page is partially written (torn page). On restart, the database cannot tell which data was written correctly and which was corrupted. Even if you can detect corruption, you have no record of what the committed transaction was trying to change. All changes since the last full backup are lost. The ACID Durability guarantee is broken.

**THE BREAKING POINT:**
Random disk I/O for data pages is slow (each write seeks to the page's physical location). Writing to multiple data pages in a transaction means multiple random seeks — dramatically limiting transaction throughput. Without a mechanism to defer data page writes (and make them safe to defer), databases are limited to synchronous random writes for every transaction.

**THE INVENTION MOMENT:**
"Write to a sequential log first, update the actual pages lazily — the log is the truth."

---

### 📘 Textbook Definition

**WAL (Write-Ahead Log)**, also called a **redo log**, is a mechanism in which every change to the database is first appended to a sequential log file before the corresponding data pages are modified. The rule "write-ahead" means: a log record must be durably written to stable storage before the data page write is allowed. On crash recovery, the database replays WAL records forward from the last checkpoint to reconstruct the state of all committed transactions, and rolls back any uncommitted transactions. WAL enables: (1) crash durability without synchronous data page writes; (2) physical streaming replication (send WAL to replicas); (3) Point-in-Time Recovery (replay WAL to any point in time).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
WAL is a sequential append-only log that records every change before applying it — the log is the source of truth for crash recovery.

**One analogy:**

> A construction crew logs every action in a journal before doing it: "Going to lay brick #4743 at position (10,5)." If the building collapses mid-construction, the crew reads the journal and reconstructs exactly what was done and what wasn't. WAL is that journal for databases — every write is logged before it's applied to the actual structure (data pages).

**One insight:**
Sequential writes to a log file are orders of magnitude faster than random writes to scattered data pages. WAL trades the cost of writing twice (log then page) for the benefit of making one of those writes sequential and fast, dramatically increasing write throughput.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Write-Ahead Rule:** A WAL record must be flushed (fsync'd) to stable storage before the corresponding data page change can be committed.
2. **Log Sequence Number (LSN):** Every WAL record has a monotonically increasing LSN. Data pages store the LSN of the last WAL record that modified them.
3. **Checkpoint:** Periodically, a checkpoint flushes all dirty data pages to disk and records the checkpoint LSN. On recovery, replay begins from the last checkpoint.
4. **ARIES recovery:** Most databases follow Algorithm for Recovery and Isolation Exploiting Semantics (ARIES): redo all changes from checkpoint, then undo incomplete transactions.

**DERIVED DESIGN:**
On a transaction commit:

1. WAL record (redo log entry) is written to the WAL buffer.
2. WAL buffer is fsync'd to the WAL segment file (durable write).
3. Transaction is acknowledged as committed.
4. (Asynchronously) dirty data pages are written to their storage locations.

On crash recovery:

1. Find the last checkpoint (recorded in `pg_control`).
2. Replay all WAL records from that checkpoint's LSN forward.
3. Pages whose on-disk LSN < WAL record's LSN are out of date — apply the WAL change.
4. Roll back any transactions that started but had no COMMIT record in the WAL.

**THE TRADE-OFFS:**
**Gain:** Durability with fast sequential writes. Enables asynchronous data page writes (checkpointing). Foundation for replication and PITR.
**Cost:** WAL files consume disk space. WAL segment cleanup must be managed. `fsync()` call per commit is a latency bottleneck (solved by group commit). WAL size during heavy writes can be large.

---

### 🧪 Thought Experiment

**SETUP:**
A database receives 10,000 INSERTs per second into a 500 GB table spread across 50,000 8KB pages.

**WITHOUT WAL:**
Each INSERT writes directly to a data page (random I/O). A 7200 RPM HDD does ~150 random IOPS. Maximum throughput: ~150 transactions per second. An SSD does ~100,000 IOPS → ~100,000 TPS. But: on crash, all uncommitted (and some committed) data is potentially lost.

**WITH WAL:**
Each INSERT appends to the WAL — sequential writes. A HDD sequential write: ~100 MB/s. Each WAL record: ~100 bytes. Throughput: ~1,000,000 WAL records/second (before fsync overhead). With `synchronous_commit = on`, one fsync per commit. Group commit: batch 1,000 commits in one fsync → 100,000+ TPS on SSD. Data pages are written lazily by the bgwriter/checkpointer — random writes happen asynchronously, not in the commit path. Crash recovery: replay WAL from last checkpoint — deterministic and complete.

**THE INSIGHT:**
WAL decouples the commit acknowledgment (sequential log write + fsync) from the data page write (random I/O). The commit path is fast because sequential writes are fast. Data pages can be written whenever convenient (checkpoints, bgwriter). The log is always the authoritative record of committed state.

---

### 🧠 Mental Model / Analogy

> WAL is like double-entry bookkeeping in accounting. Every financial change is first recorded in the ledger (WAL) with a sequential entry: "Moved $500 from account A to account B." Then the actual account balances are updated. If the office burns down between the ledger entry and updating the account balances, the auditor reads the ledger and reconstructs exactly what happened. The ledger is always written before the accounts are updated — that's "write-ahead."

- "Ledger entry" → WAL record with LSN
- "Account balances" → data pages
- "Write the ledger first" → Write-Ahead Rule (fsync WAL before page write)
- "Auditor reads ledger after fire" → crash recovery, WAL replay
- "Last ledger entry processed before fire" → last checkpoint LSN
- "Old ledger pages" → archived WAL segments (for PITR)

Where this analogy breaks down: WAL also enables replication — like faxing every ledger entry to a branch office in real-time so they have an identical set of books.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
WAL is a safety net that databases use: before changing any data, write down exactly what's about to be changed. If the power goes out mid-change, read the log and finish (or undo) the change. It's the database's "save your work" mechanism — everything logged is safe.

**Level 2 — How to use it (junior developer):**
WAL behavior surfaces in these settings: `synchronous_commit` (default `on` = fsync WAL before commit ack; `off` = faster but last ~500ms of commits may be lost on crash); `wal_level` (`replica` = enables streaming replication; `logical` = enables logical decoding/CDC); `archive_mode` = enable WAL archiving for PITR. `synchronous_commit = off` is a valid performance trade-off for non-critical data (logs, analytics events) where losing last 500ms on crash is acceptable.

**Level 3 — How it works (mid-level engineer):**
PostgreSQL WAL records contain: record type (HEAP_INSERT, HEAP_UPDATE, BTREE_INSERT, etc.), target relation OID, block number, offset, old and new tuple data, LSN. WAL records are written to the in-memory WAL buffer (`wal_buffers`) and flushed on commit (fsync to WAL segment files in `$PGDATA/pg_wal/`). Each WAL segment is 16MB (configurable via `wal_segment_size`). The checkpointer flushes dirty buffers and records a checkpoint in WAL, advancing `pg_control`'s `checkpoint_lsn`. Recovery reads `pg_control` to find last checkpoint, then replays WAL records forward until end of WAL. Group commit: multiple backends can fsync the WAL buffer simultaneously, amortizing the fsync overhead across many commits.

**Level 4 — Why it was designed this way (senior/staff):**
The Write-Ahead Rule is a provably correct mechanism for crash consistency — it is the database equivalent of the "log-structured" insight in file systems (LFS, ZFS). Sequential append to a log is the fastest possible durable write pattern on any storage medium (HDD or SSD). The fundamental challenge is managing WAL size and replication lag. WAL files accumulate until cleanup is safe (no active replication slot or PITR window requires them). Replication slot leak — a replica or logical replication consumer that stops consuming WAL but holds its slot — causes unbounded WAL accumulation, potentially filling the disk and crashing the primary. This is a critical production failure mode. Modern databases add WAL segment recycling (PostgreSQL recycles WAL files after checkpoint), WAL compression, and replication slot monitoring to manage this operationally.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WAL: COMMIT PATH                                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. Transaction generates changes in buffer pool     │
│  2. Each change appended to WAL buffer (in-memory)   │
│  3. COMMIT received:                                 │
│     a. WAL buffer → fsync → WAL segment file         │
│        (pg_wal/000000010000000000000001 etc.)        │
│     b. "Transaction committed" returned to client    │
│  4. bgwriter/checkpointer (async):                  │
│     → dirty data pages → fsync → data files          │
│                                                      │
├──────────────────────────────────────────────────────┤
│ WAL: CRASH RECOVERY                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. Read pg_control → last_checkpoint_LSN            │
│  2. Open WAL at last_checkpoint_LSN                  │
│  3. For each WAL record:                             │
│     - If page on disk LSN < WAL record LSN:          │
│       → Apply WAL record to page (REDO)              │
│     - If no COMMIT record for xid:                   │
│       → Rollback via undo log (UNDO)                 │
│  4. Database ready                                   │
│                                                      │
│  Replay time = time since last checkpoint            │
│  (checkpoint_completion_target controls frequency)   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Client sends INSERT
→ Row written to buffer pool (dirty page)
→ WAL record appended to WAL buffer
→ COMMIT: WAL buffer fsync'd to pg_wal/
→ [WAL ← YOU ARE HERE: sequential durable write]
→ Client receives commit acknowledgment
→ bgwriter asynchronously writes dirty pages to disk
→ Checkpointer records checkpoint LSN
→ Old WAL segments recycled/archived
```

**FAILURE PATH:**

```
Replication slot created for CDC consumer
→ Consumer goes offline / stops consuming
→ Slot holds back WAL cleanup (slot LSN frozen)
→ WAL segments accumulate in pg_wal/
→ Disk fills → PostgreSQL PANIC → DB crashes
```

**WHAT CHANGES AT SCALE:**
At high write throughput, WAL generation rate can be significant — a heavy write workload can generate 1–5 GB/hour of WAL. Archive storage must accommodate the configured retention window. Replication: WAL is streamed to replicas in real-time — network bandwidth must match WAL generation rate to avoid replication lag. WAL archiving for PITR requires additional storage and a WAL archiver process that doesn't block the primary.

---

### ⚖️ Comparison Table

| Property                  | WAL (PostgreSQL)          | Redo Log (MySQL InnoDB)           | No Log (flat file) |
| ------------------------- | ------------------------- | --------------------------------- | ------------------ |
| **Durability**            | Full crash recovery       | Full crash recovery               | Lost on crash      |
| **Write pattern**         | Sequential append         | Sequential append                 | Random             |
| **Replication**           | Streaming via WAL sender  | Binary log (binlog) + redo        | None               |
| **PITR**                  | Yes, via WAL archiving    | Yes, via binlog                   | No                 |
| **Space management**      | Recycled after checkpoint | Redo log ring buffer (fixed size) | N/A                |
| **Replication slot risk** | Slot leak fills disk      | Less critical                     | N/A                |

How to choose: WAL and redo log serve the same purpose; the implementation difference (PostgreSQL WAL = files, InnoDB redo = fixed ring buffer) affects operational concerns. InnoDB's fixed-size redo log avoids the disk-fill risk of WAL accumulation; PostgreSQL's WAL files enable flexible PITR and archiving.

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                            |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `synchronous_commit = off` risks data loss on transaction | `synchronous_commit = off` only risks losing the last ~500ms of commits on crash — not arbitrary data loss; it's a valid trade-off for non-critical data                           |
| WAL archiving is just for PITR                            | WAL archiving is also the backup mechanism for streaming replication to standby servers that may fall behind and need to replay archived WAL                                       |
| Checkpointing makes WAL unnecessary after checkpoint      | WAL after the last checkpoint is still needed for crash recovery — the checkpoint records which pages were clean, but subsequent changes are only in WAL until the next checkpoint |
| Replication slots are safe to leave unmonitored           | Unused replication slots (no consumer) hold back WAL cleanup and can fill disk — replication slots must be monitored and dropped when consumers are permanently offline            |

---

### 🚨 Failure Modes & Diagnosis

**1. Replication Slot WAL Accumulation Fills Disk**

**Symptom:** `pg_wal/` directory size growing without bound; `df -h` shows disk filling; eventually `PANIC: could not write to file "pg_wal/..."` and database stops.

**Root Cause:** A replication slot's `restart_lsn` is not advancing — the consumer (replica or logical subscriber) is offline, paused, or dead. PostgreSQL cannot recycle WAL segments before the slot's LSN.

**Diagnostic:**

```sql
-- Find replication slots with oldest restart_lsn
SELECT slot_name,
       slot_type,
       active,
       restart_lsn,
       pg_current_wal_lsn() - restart_lsn AS lag_bytes,
       pg_size_pretty(pg_current_wal_lsn() - restart_lsn) AS lag_pretty
FROM pg_replication_slots
ORDER BY restart_lsn ASC NULLS FIRST;

-- If lag_bytes > 5GB for an inactive slot, consider dropping:
-- SELECT pg_drop_replication_slot('slot_name');
```

**Fix:** Drop the abandoned slot: `SELECT pg_drop_replication_slot('abandoned_slot')`. If the replica must resume, provision more disk space first, then reconnect the replica before dropping.

**Prevention:** Monitor `pg_replication_slots` with alerting when any slot's lag exceeds 1 GB. Set `max_slot_wal_keep_size` (PostgreSQL 13+) to limit WAL kept for slots.

---

**2. Long Checkpoint Duration Causing I/O Spikes**

**Symptom:** Periodic I/O spikes every few minutes; `pg_stat_bgwriter.checkpoint_write_time` high; application latency spikes during checkpoints.

**Root Cause:** The checkpointer flushes all dirty pages to disk at checkpoint time. If `checkpoint_completion_target` is too low (default 0.5), it flushes all dirty pages in 50% of the checkpoint interval — causing I/O spike.

**Diagnostic:**

```sql
-- Check checkpoint frequency and duration
SELECT checkpoints_timed,
       checkpoints_req,
       checkpoint_write_time / 1000 AS write_secs,
       checkpoint_sync_time / 1000 AS sync_secs,
       buffers_checkpoint,
       buffers_clean,
       maxwritten_clean
FROM pg_stat_bgwriter;
```

**Fix:** Set `checkpoint_completion_target = 0.9` to spread checkpoint writes over 90% of the interval. Increase `checkpoint_timeout` (e.g., 15min) to reduce checkpoint frequency. These settings spread the I/O load over time rather than batching it.

**Prevention:** Set `checkpoint_completion_target = 0.9` in production. Monitor checkpoint frequency — more than 1–2 checkpoints per minute indicates checkpoint configuration needs tuning.

---

**3. WAL Generation Exceeding I/O Throughput**

**Symptom:** `synchronous_commit = on` commits taking >10ms; replica lag growing despite good network.

**Root Cause:** WAL fsync rate (commits/second × WAL size per commit) exceeds the storage subsystem's sequential write throughput.

**Diagnostic:**

```sql
-- WAL generation rate per second
SELECT pg_size_pretty(
  sum(size)
) AS total_wal_size
FROM pg_ls_waldir();

-- Monitor pg_stat_wal for WAL write/sync times (PG14+)
SELECT wal_bytes / 1024 / 1024 AS wal_mb,
       wal_write_time,
       wal_sync_time,
       wal_sync
FROM pg_stat_wal;
```

**Fix:** Enable `synchronous_commit = off` for non-critical workloads. Use a WAL-dedicated SSD (separate from data files) for high-throughput systems. Tune `wal_compression = on` to reduce WAL size.

**Prevention:** Benchmark WAL throughput separately from data file throughput. WAL needs low-latency sequential I/O; data files need high-throughput random I/O — place them on different volumes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Durability` — WAL is the mechanism that implements ACID Durability
- `Transaction` — WAL records are grouped and identified by transaction ID
- `ACID` — WAL provides the D in ACID

**Builds On This (learn these next):**

- `Redo Log / Undo Log` — WAL is a redo log; undo log is its complement for rollback
- `Database Replication` — WAL is the data source for physical streaming replication
- `MVCC` — WAL and MVCC work together: WAL for durability, MVCC for isolation

**Alternatives / Comparisons:**

- `Redo Log / Undo Log` — InnoDB uses separate redo and undo logs vs. PostgreSQL's unified WAL
- `Commit / Rollback / Savepoint` — WAL records COMMIT/ROLLBACK operations that drive recovery

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Append-only sequential log of all changes │
│              │ written before data pages are modified    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Random data page writes are slow and      │
│ SOLVES       │ non-atomic — crash means data loss        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Sequential WAL write + lazy page write    │
│              │ = fast commits + crash recovery           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (automatic) — WAL is always on     │
│              │ in production PostgreSQL/MySQL            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ `synchronous_commit=off` is OK for        │
│              │ non-critical writes (≤500ms data loss)    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Double write (log + page) for             │
│              │ fast sequential commits + crash safety    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Write the log first, update the pages    │
│              │  later — the log is the truth"            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Redo/Undo Log → Replication → Checkpoint  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D — Failure Scenario) A PostgreSQL production server crashes at 3:47 AM. The last checkpoint was at 3:45 AM. The server had `synchronous_commit = off` and `checkpoint_timeout = 5min`. Walk through exactly what happens during recovery: which transactions are guaranteed recovered, which may be lost, how does the recovery algorithm determine where to start replay, and how long does recovery take given 100MB of WAL generated per minute?

**Q2.** (TYPE F — Comparison Depth) InnoDB uses a fixed-size circular redo log (traditional default: 48 MB, now auto-sized in MySQL 8.0.30+). PostgreSQL uses append-only WAL segment files that are recycled after checkpoints. What are the three operational advantages of each approach, and what failure mode is unique to each design (InnoDB redo log: redo log flooding; PostgreSQL WAL: replication slot leak)? In which scenarios would you prefer one database over the other based solely on WAL/redo log design?
