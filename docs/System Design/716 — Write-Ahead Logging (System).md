---
layout: default
title: "Write-Ahead Logging (System)"
parent: "System Design"
nav_order: 716
permalink: /system-design/write-ahead-logging/
number: "716"
category: System Design
difficulty: ★★★
depends_on: "Leader-Follower Pattern"
used_by: "Database Replication, Distributed Systems"
tags: #advanced, #distributed, #databases, #durability, #consistency
---

# 716 — Write-Ahead Logging (System)

`#advanced` `#distributed` `#databases` `#durability` `#consistency`

⚡ TL;DR — **Write-Ahead Logging** records every change to a sequential log BEFORE applying it to the actual data files, guaranteeing durability (crash recovery) and enabling replication (followers replay the log to stay in sync with the leader).

| #716            | Category: System Design                   | Difficulty: ★★★ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | Leader-Follower Pattern                   |                 |
| **Used by:**    | Database Replication, Distributed Systems |                 |

---

### 📘 Textbook Definition

**Write-Ahead Logging (WAL)** is a durability and replication mechanism in which all modifications to a database or storage system are first written to a sequential, append-only log before being applied to the primary data structure (heap files, B-trees, etc.). The invariant is: a change must be in the log before it is reflected in the actual data pages. This enables two critical capabilities: (1) **Crash recovery**: on restart after crash, the system replays the WAL from the last checkpoint to reconstruct any changes that were not yet flushed to data files; (2) **Replication**: follower nodes subscribe to the leader's WAL stream and replay each record to maintain an identical copy of the leader's state. WAL is the foundation of PostgreSQL's replication (streaming WAL), MySQL InnoDB's redo log, Kafka's internal log structure, and many other production storage systems.

---

### 🟢 Simple Definition (Easy)

WAL: write it down BEFORE you do it. Before changing any data file, always write "I am about to change X from A to B" into a journal. If the computer crashes mid-change, reboot reads the journal: "oh, I was changing X — let me finish that." The journal is also streamed to replicas: they read it and make the same changes. Same journal, two purposes: crash recovery and replication.

---

### 🔵 Simple Definition (Elaborated)

Imagine a bank teller's end-of-day reconciliation. Before modifying any account balance on the main ledger, the teller first writes every transaction in a transaction log (WAL). If the teller faints mid-way through updating the ledger: supervisor reads the log from where the last verified checkpoint was, and completes all logged transactions. Nothing is lost. Additionally, the branch office (replica) receives a copy of the transaction log and makes the same changes to their copy of the ledger. Same transaction log serves both fault tolerance and branch synchronisation.

---

### 🔩 First Principles Explanation

**WAL structure and crash recovery mechanics:**

```
WAL RECORD STRUCTURE:
  Each WAL record captures a before-image and after-image:

  [LSN][TransactionID][Type][TableOID][BlockNum][Offset][Before][After][CRC]
   |       |            |      |          |         |       |      |     |
   |    tx=42        INSERT  orders     page_5    slot_3  NULL  {data}  checksum
   |
  LSN = Log Sequence Number (monotonically increasing position in WAL stream)
        e.g., 0/1A2B3C4D (PostgreSQL format)

  LSN is the "address" in the WAL. Everything references LSN:
    - Checkpoints record "all data pages flushed up to LSN X"
    - Replicas tell leader: "I have received up to LSN X"
    - Recovery starts from: last checkpoint LSN

WAL WRITE PATH:

  Application: INSERT INTO orders (id, amount) VALUES (1, 100)

  Step 1: Allocate transaction ID (txid = 42)
  Step 2: Find/allocate data page in buffer pool (RAM)
  Step 3: WRITE WAL RECORD FIRST (to WAL buffer, then fsync to disk)
           WAL record: LSN=1000, txid=42, type=INSERT, table=orders,
                       block=5, slot=3, after={id:1, amount:100}
  Step 4: Apply change to page in buffer pool (in-memory only)
  Step 5: On COMMIT: fsync WAL to disk (mandatory before returning to client)
           → At this point: data is durable (on disk in WAL)
           → Data page may still be in RAM (not yet on disk)
  Step 6: At next checkpoint: flush dirty data pages to disk
           → At this point: both WAL and data page are on disk

  KEY INVARIANT: WAL is fsynced before COMMIT returns to client.
                 Data pages can be lazy-written (checkpointing).
                 WHY: WAL is sequential I/O (fast). Data pages: random I/O (slow).
                 WAL write: ~0.1ms. Full data page flush: 10-100ms.

CRASH RECOVERY (using WAL):

  CRASH SCENARIO:
    T=100: INSERT committed → WAL record at LSN 1000 written to disk
    T=101: Server power failure
    Data page: NOT yet flushed (was in buffer pool RAM → lost)

    RESTART PROCESS:
    1. Read pg_control: find last checkpoint LSN = 800
    2. Read WAL from LSN 800 onward
    3. For each WAL record from LSN 800 to 1000:
         Check: is this change already in the data file? (page_lsn vs record_lsn)
         If record_lsn > page_lsn: re-apply the change (REDO)
    4. Check: any uncommitted transactions in WAL? → UNDO (rollback)
    5. Database is now consistent as of LSN 1000 → ready to accept connections

    REDO: re-apply committed changes not yet in data files
    UNDO: roll back uncommitted transactions (were in-flight at crash)

REPLICATION VIA WAL STREAMING:

  Primary (leader):
    WAL records generated → WAL file written to disk
    WAL sender process: streams WAL records to standby

  Standby (follower):
    WAL receiver: accepts WAL stream from primary
    Replay process: applies WAL records to standby data files

  Protocol:
    Primary → Standby: "Here's WAL from LSN 1000 to 1100"
    Standby → Primary: "I have applied up to LSN 1050 (apply_lsn)"
                        "I have received up to LSN 1100 (flush_lsn)"
    Primary: tracks each standby's flush_lsn and apply_lsn

    For synchronous standbys:
      COMMIT on primary: waits until flush_lsn(standby) >= commit_lsn
      → guarantees standby has WAL on disk before client gets success

LOGICAL vs PHYSICAL WAL REPLICATION:

  Physical replication (default):
    WAL records: raw byte-level changes to data pages.
    Replica: must be identical PostgreSQL version, same page layout.
    Use: high-availability standby (hot standby reads, failover target).

  Logical replication (PostgreSQL 10+):
    WAL decoded: into logical row-level changes (INSERT/UPDATE/DELETE + data).
    Subscriber: can be different PostgreSQL version, different schema subset.
    Use: live migrations, selective table replication, multi-master scenarios.

    Logical decoding output:
      COMMIT 42
        table public.orders: INSERT: id[int4]:1 amount[numeric]:100
        table public.orders: UPDATE: id[int4]:1 amount[numeric]:150

    Subscriber replays these SQL-level changes (not raw byte changes).

CHECKPOINT MECHANISM:

  Without checkpoints: on restart, must replay ALL WAL from the beginning (hours!).

  Checkpoint process (runs every checkpoint_timeout = 5 minutes by default):
    1. Flush all dirty pages from buffer pool to disk.
    2. Write a checkpoint record to WAL: "All pages flushed as of LSN X"
    3. On next crash recovery: only need to replay WAL from checkpoint LSN X.

  checkpoint_completion_target = 0.9 (spread checkpoint writes over 90% of interval)
  → avoids I/O spike at checkpoint time
  → gradual flushing throughout the 5-minute interval
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Write-Ahead Logging:

- Crash mid-write: data page half-written → inconsistent state → database corrupted
- Replication: no cheap, reliable mechanism to send changes to replicas
- Recovery: must scan entire database to find corruption (hours of downtime)

WITH Write-Ahead Logging:
→ Crash recovery: replay WAL from last checkpoint → no data loss for committed transactions
→ Replication: stream WAL to followers → identical copy maintained
→ Fast writes: sequential WAL I/O instead of random data-page I/O

---

### 🧠 Mental Model / Analogy

> A surgeon performing an operation narrates every step into a voice recorder: "making incision at 14:32, applying clamp at 14:33..." If the surgeon loses consciousness mid-surgery, a colleague reads the recording from the last confirmed step and completes the operation exactly as described. The same recording is transmitted live to a teaching hospital across town, where a resident replays each step on a training mannequin — keeping perfect synchronisation with the original operation.

"Voice recorder narration" = WAL (sequential record of all changes before making them)
"Colleague reads recording and resumes" = crash recovery (replay WAL from checkpoint)
"Must narrate BEFORE making incision" = WAL written BEFORE data page modification
"Teaching hospital resident replays steps" = follower replica replaying WAL stream
"Live transmission of recording" = WAL streaming replication

---

### ⚙️ How It Works (Mechanism)

**WAL-based replication monitoring in PostgreSQL:**

```sql
-- Check replication lag (on primary):
SELECT
    client_addr,
    state,
    sent_lsn,             -- LSN primary has sent
    write_lsn,            -- LSN standby has written to its WAL file
    flush_lsn,            -- LSN standby has fsynced to disk
    replay_lsn,           -- LSN standby has applied to data files
    (sent_lsn - replay_lsn) AS replication_lag_bytes,
    write_lag,            -- time lag for write_lsn
    flush_lag,            -- time lag for flush_lsn
    replay_lag            -- time lag for replay_lsn (most important: data availability lag)
FROM pg_stat_replication;

-- Example output:
-- client_addr | state     | replication_lag_bytes | replay_lag
-- 10.0.0.2   | streaming | 0                     | 00:00:00.003
-- 10.0.0.3   | streaming | 2097152               | 00:00:01.2

-- Check checkpoint stats (WAL write efficiency):
SELECT
    checkpoints_timed,      -- scheduled checkpoints (good)
    checkpoints_req,        -- forced checkpoints from WAL filling up (bad — increase max_wal_size)
    buffers_checkpoint,     -- pages written at checkpoint
    buffers_clean,          -- pages written by background writer
    buffers_backend         -- pages written by backend directly (bad — means too much I/O pressure)
FROM pg_stat_bgwriter;
```

```
WAL write path performance:

  synchronous_commit options:
  ┌─────────────────┬─────────────────────────────────────────────────────┐
  │ Setting         │ Guarantee                                           │
  ├─────────────────┼─────────────────────────────────────────────────────┤
  │ on (default)    │ WAL fsynced to local disk before COMMIT returns      │
  ├─────────────────┼─────────────────────────────────────────────────────┤
  │ remote_write    │ WAL sent to standby + written (not fsynced) on      │
  │                 │ standby — faster than remote_apply                  │
  ├─────────────────┼─────────────────────────────────────────────────────┤
  │ remote_apply    │ WAL applied on standby — client waits for both      │
  │                 │ primary fsync AND standby apply                     │
  ├─────────────────┼─────────────────────────────────────────────────────┤
  │ local           │ WAL fsynced to local disk only (ignore standbys)    │
  ├─────────────────┼─────────────────────────────────────────────────────┤
  │ off             │ WAL not fsynced — return immediately                │
  │                 │ Risk: up to wal_writer_delay (200ms) of data loss   │
  │                 │ Safe if: can tolerate 200ms data loss on crash      │
  └─────────────────┴─────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
Leader-Follower Pattern (produces WAL on leader)
        │
        ▼
Write-Ahead Logging ◄──── (you are here)
(sequential log of all changes)
        │
        ├── Crash Recovery (replay WAL from checkpoint on restart)
        ├── Database Replication (stream WAL to followers)
        └── Point-in-Time Recovery (replay WAL to any past LSN)
```

---

### 💻 Code Example

**Implementing a simple WAL in Java (for educational understanding):**

```java
// Simplified WAL implementation demonstrating the key invariant:
// "write to log BEFORE applying to data structure"

public class SimpleWAL {

    private final Path walFile;
    private final Map<String, String> dataStore = new ConcurrentHashMap<>();

    public SimpleWAL(Path walFile) throws IOException {
        this.walFile = walFile;
        recoverFromWAL();  // Replay WAL on startup (crash recovery)
    }

    public void put(String key, String value) throws IOException {
        // STEP 1: Write to WAL FIRST (append-only, sequential I/O):
        String walRecord = String.format("PUT|%s|%s\n", key, value);
        Files.writeString(walFile, walRecord, StandardOpenOption.APPEND, StandardOpenOption.SYNC);
        // SYNC = fdatasync after write = guarantee on disk before continuing

        // STEP 2: Only AFTER WAL is on disk: apply to in-memory data structure:
        dataStore.put(key, value);
        // If JVM crashes here: on restart, recoverFromWAL() will replay PUT and restore key→value
    }

    public String get(String key) {
        return dataStore.get(key);  // Reads always from in-memory map (no WAL read)
    }

    private void recoverFromWAL() throws IOException {
        if (!Files.exists(walFile)) return;

        // Replay all WAL records to reconstruct in-memory state:
        Files.lines(walFile).forEach(line -> {
            String[] parts = line.split("\\|");
            if ("PUT".equals(parts[0])) {
                dataStore.put(parts[1], parts[2]);  // Re-apply committed changes
            }
        });

        System.out.println("Recovered " + dataStore.size() + " entries from WAL");
    }

    // Checkpoint: truncate WAL after confirmed flush to "permanent" storage
    public void checkpoint() throws IOException {
        // In production: flush data to durable storage, then truncate WAL
        // Here: WAL can be truncated (all entries applied to dataStore)
        Files.writeString(walFile, "", StandardOpenOption.TRUNCATE_EXISTING);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| WAL and transaction logs are the same thing | WAL is the physical-level log (byte-level page changes) used for crash recovery and streaming replication. A transaction log (or audit log) records business-level events (what was inserted/updated at the SQL level). PostgreSQL's logical decoding converts WAL into a transaction log format. They are related but distinct: WAL is an internal implementation detail; transaction logs are often used for auditing and external replication |
| WAL guarantees zero data loss on crash      | WAL guarantees zero data loss for COMMITTED transactions — those where the COMMIT WAL record was fsynced to disk before returning to the client. Uncommitted transactions at crash time are rolled back (UNDO). With `synchronous_commit = off`, even committed transactions can lose up to `wal_writer_delay` (200ms) of data. Always use `synchronous_commit = on` for financial or critical data                                              |
| WAL is only used for crash recovery         | WAL enables: (1) crash recovery, (2) streaming replication, (3) logical replication, (4) point-in-time recovery (PITR — restore DB to any past LSN by replaying WAL archive), (5) change data capture (CDC — external systems like Debezium read WAL for event streaming)                                                                                                                                                                        |
| More WAL = slower database                  | WAL writes are sequential I/O (fast: ~50,000 records/second on NVMe). The bottleneck is rarely WAL writing itself. Performance issues come from: `fsync` latency (solution: fast NVMe for WAL directory), checkpoint I/O pressure (solution: increase `max_wal_size`, tune `checkpoint_completion_target`), or WAL shipping latency in synchronous replication (solution: use async replication for non-critical replicas)                       |

---

### 🔥 Pitfalls in Production

**WAL archival filling disk during high write load:**

```
PROBLEM: WAL segments accumulate faster than archiving can process them

  PostgreSQL WAL configuration:
    wal_segment_size = 16MB     (each WAL file = 16MB)
    max_wal_size = 1GB          (before forcing checkpoint to reclaim space)

  Write-heavy application:
    10,000 INSERT/second → WAL generation: ~500MB/minute
    WAL archiver: uploads to S3 at 100MB/minute (slow network)

  Result:
    pg_wal/ directory grows 400MB/minute (500MB generated - 100MB archived)
    After 10 minutes: 4GB WAL backlog
    Disk full: PostgreSQL CRASHES (cannot write WAL = cannot proceed)

BAD: min_wal_size too low, no monitoring:
  min_wal_size = 80MB  ← immediately reuses WAL files
  # no alerting on pg_wal/ disk usage
  # archival bottleneck not detected until disk full

FIX:
  1. Separate disk partition for pg_wal/
     (WAL disk full never crashes the entire database volume)

  2. Monitor WAL archival lag:
     SELECT now() - pg_last_xact_replay_timestamp() AS replication_delay;
     Alert if: archive_lag > 60 seconds

  3. Increase archival throughput:
     archive_command = 'aws s3 cp %p s3://my-wal-archive/%f --storage-class STANDARD_IA'
     max_wal_senders = 10   -- allow more parallel archival processes

  4. Alert on pg_wal/ disk usage > 70%:
     # Prometheus rule:
     node_filesystem_avail_bytes{mountpoint="/var/lib/postgresql/pg_wal"} /
     node_filesystem_size_bytes{mountpoint="/var/lib/postgresql/pg_wal"} < 0.3
```

---

### 🔗 Related Keywords

- `Leader-Follower Pattern` — leader generates WAL; followers consume WAL stream to replicate state
- `Database Replication` — WAL streaming is the mechanism for PostgreSQL physical replication
- `Crash Recovery` — WAL enables REDO and UNDO recovery from last checkpoint after crash
- `Change Data Capture` — tools like Debezium read WAL logical decoding output for event streaming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Write to sequential log BEFORE data file  │
│              │ → crash recovery + streaming replication  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any durable storage (it's the default in  │
│              │ PostgreSQL, MySQL InnoDB, SQLite)          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ synchronous_commit=off for financial data;│
│              │ WAL disk on same volume as data disk      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Surgeon narrates before each cut —       │
│              │  colleague can always complete the        │
│              │  operation from the recording."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Database Replication → Raft               │
│              │ → Change Data Capture (CDC)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A PostgreSQL server has `synchronous_commit = off` set for maximum write performance. A developer argues: "We fsync the WAL on a timer every 200ms — there's at most 200ms of data loss in a crash, and our product manager says that's acceptable for our analytics workload." Is this configuration safe for ALL tables in the database, or only specific ones? How would you configure PostgreSQL to use async commit for analytics tables but synchronous commit for financial transaction tables in the same database instance?

**Q2.** You're building a custom key-value store in Java that must survive server restarts. Describe exactly how you would implement WAL-based crash recovery: what information must each WAL record contain? When exactly do you fsync the WAL? What is a checkpoint in your implementation? What is the recovery algorithm on startup? What is the maximum amount of data you could lose if the JVM crashes at the worst possible moment?
