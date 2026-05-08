---
layout: default
title: "Durability"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /databases/durability/
id: DBF-020
category: Database Fundamentals
difficulty: ★★☆
depends_on: ACID, WAL, Transaction
used_by: WAL, Redo Log, Database Replication
related: Atomicity, fsync, Write Amplification
tags:
  - database
  - transactions
  - reliability
  - intermediate
---

# DBF-020 — Durability

⚡ TL;DR — Durability guarantees that once a transaction commits, its changes survive forever — even if the server crashes, loses power, or the OS panics the instant after `COMMIT` returns.

| #415            | Category: Database Fundamentals       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | ACID, WAL, Transaction                |                 |
| **Used by:**    | WAL, Redo Log, Database Replication   |                 |
| **Related:**    | Atomicity, fsync, Write Amplification |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A customer completes an online purchase. The database commits the order. The server crashes 10 milliseconds later before the data pages have been flushed from the OS buffer cache to disk. The server restarts. The order is gone — the committed transaction existed only in memory. The customer received an order confirmation email. The warehouse has no record of the order. The customer gets charged but receives nothing.

**THE BREAKING POINT:**
Without durability, the word "committed" is meaningless. Any confirmed transaction could silently vanish on the next crash. Applications can't be built on databases that forget what they've confirmed. Financial ledgers, order systems, medical records — all become unreliable if the storage guarantee is "probably persisted."

**THE INVENTION MOMENT:**
"This is exactly why Durability was created."

---

### 📘 Textbook Definition

**Durability** is the fourth property of ACID, guaranteeing that once a transaction is committed, it remains committed permanently. The committed data must survive system failures — crashes, power outages, OS panics, hardware failures — and be recoverable on restart. Durability is implemented via the **WAL (Write-Ahead Log)**: before a `COMMIT` returns success to the client, the transaction's changes are written to a durable log on persistent storage (via `fsync` to ensure the OS flushes its buffers to disk). On recovery, the database replays the WAL to restore all committed transactions that hadn't yet been flushed to data pages.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Once the database says "committed," that data is permanent — no crash can erase it.

**One analogy:**

> Signing a contract and filing it in a fireproof safe. Once you've signed (committed) and locked it in the safe (fsync to durable storage), the contract is permanent. Even if your office burns down, the contract survives in the safe. Without the safe, the signed contract on your desk could be destroyed before it was ever official.

**One insight:**
Durability is implemented entirely in the storage layer — specifically by the `fsync` system call, which forces the OS to flush its write buffers to physical disk. Disabling `fsync` (for "performance") breaks durability completely — `COMMIT` can return success while data exists only in volatile OS memory. This is the #1 cause of silent data loss in improperly configured databases.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The database's word ("committed") must be trustworthy — it cannot be revoked by a crash.
2. Durable storage means data survives even if every byte of RAM is lost simultaneously.
3. To guarantee this, changes must be on physical, persistent storage before `COMMIT` signals success.

**DERIVED DESIGN:**
The problem: writing to disk is 100–1000x slower than writing to memory. If the database waited for every data page write to disk before confirming commit, throughput would be catastrophically low.

The solution: **Write-Ahead Log (WAL)**. Instead of immediately flushing modified data pages to their final locations on disk, the database writes a compact sequential log entry describing the change. Log entries are small, sequential writes — much faster than random data page writes. The WAL is fsynced to disk before COMMIT returns. Data pages can be flushed lazily in the background.

On crash:

- WAL has COMMIT record → transaction was durable. Replay WAL to get data pages up to date.
- WAL no COMMIT record → transaction was in-progress. Roll back using undo log.

The WAL is the durability backbone. Everything else (data pages, indexes, MVCC versions) can be reconstructed from the WAL.

**THE TRADE-OFFS:**
**Gain:** Committed transactions are permanent. Applications can trust the database's confirmation.
**Cost:** Every commit requires at least one `fsync` to the WAL — a disk I/O operation. At high transaction rates, this becomes the throughput bottleneck. Group commit and async commit are optimisations that reduce this cost at the price of reduced durability guarantee window.

---

### 🧪 Thought Experiment

**SETUP:**
A database processes 1,000 transactions per second. Each transaction modifies a row in memory. The server crashes 2 seconds after a batch of 1,000 commits were confirmed.

**WITHOUT DURABILITY (`fsync=off`):**

- 1,000 commits "succeeded" — confirmation sent to clients.
- Data exists only in OS write buffer cache (volatile memory).
- Server crashes. OS write buffer flushed to /dev/null (lost).
- Server restarts. WAL has no fsync'd COMMIT records.
- Database starts fresh: 0 of those 1,000 transactions exist.
- 1,000 clients received success; 1,000 operations are gone.
- Result: ghost confirmations — the database lied.

**WITH DURABILITY (`fsync=on`):**

- Each commit waits for WAL entry to be fsync'd to disk.
- Server crashes.
- Server restarts. WAL is scanned.
- All 1,000 COMMIT records are in the WAL.
- Database replays WAL → all 1,000 transactions restored.
- Result: all 1,000 operations permanent. Database kept its word.

**THE INSIGHT:**
`fsync=off` doesn't make the database faster — it makes the database lying about durability. The throughput gain comes entirely from not doing the work that durability requires. It's not an optimisation; it's a silent correctness trade-off that only matters when the server crashes.

---

### 🧠 Mental Model / Analogy

> Durability is like writing a cheque vs. handing someone cash. Handing cash is instant (fast), but once you hand it over it's permanent. A cheque (without durability) might bounce — you handed it over, but until the bank processes it, the transfer isn't real. Durability is the "bank processed it" confirmation — once you get it, the transaction is real and permanent regardless of what happens next.

- "Handing cash" → `COMMIT` with `fsync=on` (instant durable confirmation)
- "Cheque that might bounce" → `COMMIT` with `fsync=off` (fast but not permanent)
- "Bank processing confirmation" → WAL fsynced to disk
- "Bank's records" → durable storage (disk/SSD)

Where this analogy breaks down: unlike banking, database durability guarantees byte-level recovery — even partial disk writes are recovered from the WAL, whereas a bounced cheque has no automatic recovery.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Durability means when the database says "saved," it really is saved — forever, even if the power goes out five seconds later. Your data doesn't disappear when the server crashes.

**Level 2 — How to use it (junior developer):**
Durability is automatic when using a properly configured relational database. Don't disable it: never set `fsync=off` or `synchronous_commit=off` in PostgreSQL, never set `innodb_flush_log_at_trx_commit=0` in MySQL. These settings trade durability for speed — appropriate only for test databases, never production.

**Level 3 — How it works (mid-level engineer):**
The WAL (Write-Ahead Log) is written before data pages. PostgreSQL's WAL is stored in `pg_wal/`; MySQL InnoDB uses `ib_logfile0` and `ib_logfile1` (redo log). Every `COMMIT` calls `fsync()` on the WAL file, which forces the OS to flush write buffers to the underlying storage device. Group commit batches multiple transactions' WAL writes into a single fsync to amortise the disk I/O cost. Async commit (`synchronous_commit=off` in PostgreSQL) returns success before fsync — commits up to ~60ms old may be lost on crash, but the database never produces inconsistent data.

**Level 4 — Why it was designed this way (senior/staff):**
The fundamental durability bottleneck is the `fsync` latency — typically 1–10ms on spinning disk, 0.05–0.5ms on NVMe SSD. At these latencies, a single-threaded commit stream is capped at 100–1,000 commits/second. Group commit breaks this ceiling: instead of fsyncing after each commit, the database collects commits for a short window (1–10ms), writes all their WAL entries, and issues one fsync — achieving thousands of commits per fsync. This is the primary throughput lever for write-heavy PostgreSQL/MySQL deployments. Cloud databases (Aurora, AlloyDB) go further: they stream WAL to replicas over the network and confirm durability once a majority of storage nodes acknowledge receipt — decoupling fsync from local disk entirely.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ DURABILITY: WAL + fsync                      │
├──────────────────────────────────────────────┤
│                                              │
│  Transaction commits:                        │
│    1. Write WAL entry to WAL buffer          │
│          (in memory — fast)                  │
│    2. fsync WAL buffer to disk               │
│          (blocks until OS confirms write)    │
│    3. Return COMMIT success to client        │
│                                              │
│  Data pages written lazily in background:    │
│    - Checkpoint process flushes dirty pages  │
│    - Runs every N seconds or N WAL bytes     │
│                                              │
│  CRASH RECOVERY:                             │
│  ┌──────────────────────────────────────┐    │
│  │ Read WAL from last checkpoint        │    │
│  │ For each record:                     │    │
│  │   COMMIT seen → redo data page write │    │
│  │   No COMMIT  → skip (undo on start)  │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  fsync=off: step 2 skipped                   │
│    → COMMIT returns before durable          │
│    → On crash: WAL in OS buffer = lost      │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
App COMMIT → WAL buffer written → fsync to disk
→ [DURABILITY ← YOU ARE HERE: WAL durable]
→ COMMIT returns to app → background checkpoint
→ Data pages eventually flushed to disk
```

**FAILURE PATH:**

```
Crash before WAL fsync → COMMIT not returned → Atomicity handles rollback
Crash after WAL fsync, before page flush → Durability holds:
  WAL replayed on restart → Data pages reconstructed
  No data loss for committed transactions
```

**WHAT CHANGES AT SCALE:**
At 10,000+ transactions/second, every commit waiting for an individual `fsync` caps throughput at ~500–2,000 TPS per disk. Group commit (default in modern PostgreSQL/MySQL) batches fsync calls to sustain 10,000+ TPS. At 100x scale, cloud storage architectures (AWS Aurora) route WAL to a distributed storage fleet — durability is confirmed by a quorum of storage nodes, removing the single-server fsync bottleneck entirely.

---

### ⚖️ Comparison Table

| Durability Mode            | Data Loss Risk                 | Write Throughput | Best For                                                    |
| -------------------------- | ------------------------------ | ---------------- | ----------------------------------------------------------- |
| `fsync=on, sync_commit=on` | Zero (within hardware limits)  | Lower            | Financial, medical, any production data                     |
| `synchronous_commit=off`   | Up to ~60ms of commits         | Higher           | Non-critical high-frequency events (analytics events, logs) |
| `fsync=off`                | Entire WAL buffer on crash     | Highest          | Throw-away test/dev databases only                          |
| Replication (sync)         | Zero (if replica acknowledges) | Lower            | High-availability clusters needing cross-server durability  |

How to choose: Always use `fsync=on` for production. Consider `synchronous_commit=off` only for data where losing a few seconds of writes on crash is acceptable (e.g., session events, non-financial metrics).

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                 |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `fsync=off` just reduces disk writes            | It disables the durability guarantee entirely — committed transactions exist only in volatile OS cache and vanish on crash                                                                              |
| Replication replaces durability                 | Replication copies data to another node, but if the primary crashes before WAL is fsynced AND replication is async, the replica also loses the uncommitted-but-confirmed data                           |
| SSDs make fsync fast enough to not matter       | NVMe SSDs reduce fsync latency to ~50μs, but at high TPS the cumulative fsync calls still bottleneck throughput; group commit is still needed                                                           |
| Durability guarantees hardware failure survival | Durability is a logical guarantee against software crashes and power failures. Physical disk failure (hardware RAID failure, disk corruption) requires backups and replication, not just WAL durability |

---

### 🚨 Failure Modes & Diagnosis

**1. Silent Data Loss from `fsync=off` in Production**

**Symptom:** After server restart, recent commits are missing; customer confirmation emails sent but orders don't exist; audit log has gaps.

**Root Cause:** `fsync=off` or `synchronous_commit=off` set in PostgreSQL configuration, or `innodb_flush_log_at_trx_commit=0` in MySQL. Changes committed to OS write buffer but not flushed to disk before crash.

**Diagnostic:**

```bash
# PostgreSQL: check durability settings
psql -c "SHOW fsync;"                    # must be 'on'
psql -c "SHOW synchronous_commit;"       # 'on' for full durability
psql -c "SHOW data_sync_retry;"

# MySQL: check InnoDB flush setting
mysql -e "SHOW VARIABLES
  LIKE 'innodb_flush_log_at_trx_commit';"
# Must be 1 for full durability (not 0 or 2)
```

**Fix:** Set `fsync=on` and `synchronous_commit=on` in `postgresql.conf`. Restart required. For MySQL: `innodb_flush_log_at_trx_commit=1` in `my.cnf`.

**Prevention:** Include durability settings in infrastructure-as-code database provisioning. Add a startup check that verifies these settings before the application connects.

---

**2. WAL Disk Full Stopping All Writes**

**Symptom:** All writes to the database fail with `ERROR: could not write to file "pg_wal/..."` or `ENOSPC`; application completely blocked.

**Root Cause:** WAL volume full — can't write new WAL entries, so no commits can proceed. Causes: WAL replication slot held by offline replica (accumulates WAL indefinitely); WAL volume undersized for write load.

**Diagnostic:**

```sql
-- Check replication slots holding WAL
SELECT slot_name, active,
       pg_size_pretty(
         pg_wal_lsn_diff(pg_current_wal_lsn(),
                         restart_lsn)) AS retained_wal
FROM pg_replication_slots
ORDER BY retained_wal DESC;

-- Check WAL directory size
SELECT pg_size_pretty(sum(size))
FROM pg_ls_waldir();
```

**Fix:** Drop inactive replication slots (`SELECT pg_drop_replication_slot('slot_name')`). Extend WAL volume. Set `max_slot_wal_keep_size` to cap WAL retention per slot.

**Prevention:** Monitor WAL directory size and replication slot lag. Alert when WAL exceeds 80% of volume capacity.

---

**3. Checkpoint Too Infrequent Causing Slow Recovery**

**Symptom:** Database restart after crash takes 10+ minutes replaying WAL; application startup blocked.

**Root Cause:** `checkpoint_completion_target` set too high or `max_wal_size` too large — checkpoints run infrequently. On crash, the database must replay all WAL back to the last checkpoint, which may be gigabytes.

**Diagnostic:**

```sql
-- Check checkpoint frequency
SELECT * FROM pg_stat_bgwriter;

-- Check time since last checkpoint
SELECT now() - pg_last_xact_replay_timestamp() AS recovery_lag;

-- Check WAL size between checkpoints
SHOW max_wal_size;     -- should be tuned to recovery time target
SHOW checkpoint_timeout;
```

**Fix:** Reduce `max_wal_size` and `checkpoint_timeout` to run checkpoints more frequently. More frequent checkpoints mean less WAL to replay on recovery.

**Prevention:** Define a Recovery Time Objective (RTO) and tune `max_wal_size` to match: `max_wal_size = WAL_write_rate * target_recovery_seconds`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ACID` — durability is the "D"; understand the full model
- `WAL (Write-Ahead Log)` — the mechanism that implements durability
- `Transaction` — durability is a property of committed transactions

**Builds On This (learn these next):**

- `Redo Log / Undo Log` — the specific log structures that implement durability and atomicity
- `Database Replication` — extends durability across multiple servers for high availability
- `Write Amplification` — the cost side of WAL-based durability at scale

**Alternatives / Comparisons:**

- `Atomicity` — the twin of durability: atomicity handles pre-commit rollback; durability handles post-commit survival
- `fsync` — the OS mechanism that implements the physical durability guarantee

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Committed transactions survive crashes    │
│              │ and power failures permanently            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Commits in memory vanish on crash —       │
│ SOLVES       │ confirmed transactions silently lost      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ fsync=off breaks durability entirely;     │
│              │ "fast but durable" needs group commit     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always in production — durability is      │
│              │ the foundation of database trustworthiness│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Test/dev databases where data is          │
│              │ disposable — fsync=off speeds CI runs     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Data safety vs write throughput           │
│              │ (group commit reduces this cost)          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "'Committed' means forever, or it         │
│              │  means nothing"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WAL → Redo Log → Database Replication     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Trade-off) AWS Aurora PostgreSQL confirms durability by writing WAL to a quorum of 6 storage nodes across 3 Availability Zones before returning COMMIT success — without a local fsync. Traditional PostgreSQL fsyncs WAL to local disk. In what two specific failure scenarios does Aurora provide stronger durability than single-server PostgreSQL with fsync=on? In what one scenario does Aurora provide weaker durability guarantees?

**Q2.** (TYPE E — First Principles Challenge) You are designing a database for an embedded IoT sensor with 512KB of flash storage, no OS, and a 3.3V system that can lose power at any moment. The sensor must record temperature readings with durability. You cannot use a WAL (too much write amplification on flash). What alternative mechanism would you design to provide durability guarantees on power loss, and what are the trade-offs compared to WAL-based durability?
