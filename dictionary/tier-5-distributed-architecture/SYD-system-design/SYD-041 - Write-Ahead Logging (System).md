---
id: SYD-041
title: Write-Ahead Logging (System)
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-040
used_by: SYD-042
related: SYD-039, SYD-040, SYD-042, SYD-059
tags:
  - architecture
  - database
  - durability
  - recovery
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 41
permalink: /syd/write-ahead-logging/
---

# SYD-041 - Write-Ahead Logging (System)

⚡ TL;DR - Write-Ahead Logging (WAL) is the durability
mechanism used by every serious database: before any
data page is modified on disk, a log record describing
the change is appended to a sequential log file. On
crash, the database replays the log to recover to a
consistent state. WAL enables: ACID durability (crash
recovery), replication (ship the log to replicas),
and point-in-time recovery (replay log from any
checkpoint). It is the foundation of PostgreSQL,
MySQL, Kafka, RocksDB, and virtually every durable
storage system.

| #041 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Leader-Follower Pattern | |
| **Used by:** | Data Partitioning Strategies | |
| **Related:** | Distributed Locks, Leader-Follower Pattern, Data Partitioning Strategies, Event Sourcing | |

---

### 🔥 The Problem This Solves

**WITHOUT WAL:**
A database updates a data page in memory and writes
it to disk. Midway through the write, power fails.
The page is partially written. On restart: the data
page is corrupted. The database cannot tell if the
write succeeded, partially succeeded, or failed.
Recovery requires a full consistency scan (slow,
unreliable). Data loss is likely.

**WITH WAL:**
Before updating the data page, append a log record
to the WAL: "change column X in page P from old_val
to new_val." The log record is written to disk
(sequential append, fast). Then update the data page.
If power fails during the data page write: on restart,
the database reads the WAL and re-applies any log
records whose data page changes were not fully written.
The database is restored to a consistent state.
No data loss; recovery in seconds.

---

### 📘 Textbook Definition

**Write-Ahead Log (WAL):** An append-only sequential
log file where every database change is recorded as
a log entry before the corresponding data page is
modified. The "write-ahead" contract is: the log
record MUST be durable (on disk) before the data
page is modified. This guarantees crash recovery:
if a crash occurs, replaying the WAL from the last
checkpoint restores the database to a consistent state.

**Key properties:**
- **Durability:** Log entries are fsynced before data
  page changes (D in ACID)
- **Sequential writes:** WAL is append-only → fast
  (sequential I/O >> random I/O on magnetic disks;
  also better for SSDs)
- **Replication stream:** WAL records can be streamed
  to replicas (logical or physical replication)
- **Point-in-time recovery (PITR):** Replay WAL from
  any checkpoint to recover to any past timestamp

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Log the change before making the change. If the system
crashes, replay the log to recover.

**One analogy:**
> A surgeon's pre-op checklist:
> - Before cutting, the surgeon logs the plan:
>   "Patient: Alice. Operation: appendectomy.
>    Instruments prepared: [list]."
> - If the surgeon is interrupted mid-operation (crash),
>   another surgeon reads the checklist and knows
>   exactly what was planned and what was done.
> - Without the checklist: the second surgeon doesn't
>   know the safe starting state. The patient is at risk.
>
> The WAL is the surgery log. The checkpoint is the
> point at which all prior steps are confirmed complete.

**One insight:**
WAL converts random writes (data page updates scattered
across disk) into sequential writes (appends to a
single file). Sequential I/O is orders of magnitude
faster than random I/O on spinning disks. This is
why WAL is a performance optimization as much as
a durability mechanism. Kafka's durability model is
essentially WAL: every message is a sequential append
to a log file.

---

### 🔩 First Principles Explanation

**WAL RECORD STRUCTURE:**

```
WAL record (simplified PostgreSQL format):
  [LSN]       [XID]    [Resource]  [Type] [Data]
  0x12345678  txn_99   page_42     UPDATE old=[...] new=[...]
  
LSN = Log Sequence Number (monotonically increasing)
XID = Transaction ID
Resource = which page/table is being modified
Type = INSERT / UPDATE / DELETE / COMMIT / ABORT
Data = old and new values (for undo and redo)
```

**CHECKPOINT:**
```
A checkpoint is a point where:
  1. All dirty pages in memory are flushed to disk
  2. The LSN of the checkpoint is recorded in WAL

On recovery:
  Start from the last checkpoint LSN
  Replay WAL records from that point forward
  (do not need to replay records before checkpoint:
   data is already on disk)

Without checkpoints: must replay entire WAL from
  the beginning on every restart (hours for large DBs)
With checkpoints every 5 minutes: replay at most
  5 minutes of WAL on restart
```

**THE WAL CONTRACT (The "Write-Ahead" Rule):**
```
MUST happen in this order:
  1. Write log record to WAL file
  2. fsync() WAL file (ensure it's on disk)
  3. THEN modify data page
  
If crash between step 1 and step 3:
  WAL has the log record
  Replay: re-apply the change → data page updated
  
If crash before step 1:
  WAL has no record of this change
  The change never happened → consistent state
  
If crash during step 3 (partial data page write):
  WAL has log record
  Recovery: replay WAL → re-apply correctly
```

**WAL AND REPLICATION:**
```
PostgreSQL streaming replication:
  Primary writes WAL record
  WAL sender process streams records to standby
  Standby applies WAL records to its data files
  Standby = exact copy of primary's data
  
  Sync replication: primary waits for standby ACK
    before returning to client (RPO = 0: no data loss)
  Async replication: primary returns immediately
    (lower latency, possible data loss on failover)

Logical replication (PostgreSQL):
  Decodes WAL records into logical operations
  (INSERT/UPDATE/DELETE with column values)
  Can replicate to different DB versions or schemas
  Used by: Debezium, pglogical, AWS DMS
```

---

### 🧪 Thought Experiment

**SCENARIO: PostgreSQL crash during high write load**

A PostgreSQL server receives 10,000 INSERTs/sec.
The OS crashes (kernel panic) at t=30 seconds.
At t=30, 300,000 rows have been inserted.

**What happens on restart:**
1. PostgreSQL starts recovery mode
2. Reads the most recent checkpoint location from
   `pg_control` file
3. The checkpoint was at t=28 (2 seconds of WAL to replay)
4. Replays WAL from checkpoint LSN: 20,000 operations
   (2s × 10,000 ops/s)
5. Data pages are restored to the t=30 state
6. Any transactions not yet COMMITTED in WAL: rolled back
7. PostgreSQL opens for connections

**Recovery time:** seconds (not minutes or hours)
because the checkpoint was recent (2 seconds ago).
Without WAL: full table scan to find corruption; hours.

**What about the 50 transactions in-flight at crash time?**
WAL contains their BEGIN records but not COMMIT records.
Recovery applies UNDO for these (rolls them back).
No partial data: either fully committed or fully rolled back.
This is the ACID atomicity guarantee enabled by WAL.

---

### 🧠 Mental Model / Analogy

> WAL is like a double-entry bookkeeping ledger in accounting:
>
> Single-entry (no WAL): You update the balance directly.
> If you drop the ledger mid-update: the balance is wrong.
> No way to know what the intended transaction was.
>
> Double-entry (WAL): Before updating the balance,
> you write the journal entry: "Debit accounts payable
> $500, Credit cash $500." If the ledger is dropped,
> re-read the journal and re-apply the entries.
> The journal is always written first (write-ahead).
>
> The journal is the WAL.
> The ledger balance is the data page.
> Balancing the ledger from the journal = crash recovery.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Before making any change to stored data, write a note
about what the change will be. If the system crashes
mid-change, use the note to finish or undo the change
correctly.

**Level 2 - How to use it (junior developer):**
WAL is automatic in any ACID database. You don't
implement it; you configure it. Key settings in
PostgreSQL: `wal_level` (replica/logical), `fsync`
(NEVER set to off in production), `checkpoint_timeout`,
`synchronous_commit`.

**Level 3 - How it works (mid-level engineer):**
WAL records are sequential appends. Sequential I/O
is 10-100x faster than random I/O. This is why
high-throughput writes to a WAL (Kafka, PostgreSQL,
MySQL binlog) can sustain millions of writes/sec
even on spinning disks. The trade-off: WAL requires
an fsync per COMMIT (or batch of COMMITs) to ensure
durability. Disabling fsync enables higher throughput
but risks data loss on crash.

**Level 4 - Why it was designed this way (senior/staff):**
WAL is the implementation of the "D" in ACID. The
key insight is that sequential log writes are durable
and fast, while random data page writes are slow.
Decouple the two: write WAL sequentially (fast,
durable), update data pages lazily (asynchronous,
in background). The WAL is the source of truth.
Data pages are a "cache" derived from the WAL.
This is exactly the same insight as event sourcing:
the event log is the source of truth; current state
is derived by replaying events.

**Level 5 - Mastery (distinguished engineer):**
Kafka's architecture is an explicit application of
WAL at the message broker layer. Kafka partitions
are append-only log files. Each message is a WAL
record. Consumer offsets are the "checkpoint."
Compacted topics are analogous to checkpoints in
databases (merge all updates for a key into latest
state). The connection between WAL, Kafka, and
event sourcing is not coincidental: they are all
implementations of the same fundamental insight -
an append-only, ordered log of changes is the most
durable and efficient way to record state transitions
in a system.

---

### ⚙️ How It Works (Mechanism)

**WAL flow in PostgreSQL:**

```
┌───────────────────────────────────────────────────────┐
│ WRITE PATH WITH WAL                                  │
│                                                       │
│  Client: INSERT INTO orders VALUES (...)             │
│                                                       │
│  1. Generate WAL record:                             │
│     LSN=0x9A2B, XID=567, Page=42                    │
│     Type=INSERT, data=[new row bytes]               │
│                                                       │
│  2. Append WAL record to WAL buffer (in memory)     │
│                                                       │
│  3. At COMMIT:                                       │
│     Write COMMIT record to WAL buffer               │
│     fsync() WAL buffer → WAL file on disk           │
│     (This is the durability guarantee)              │
│                                                       │
│  4. Return SUCCESS to client                         │
│                                                       │
│  5. Background: update data pages (async)            │
│     (Data pages may lag behind WAL by seconds/mins)  │
│                                                       │
│  ON CRASH:                                           │
│  1. Find last checkpoint in pg_control              │
│  2. Read WAL from checkpoint forward                │
│  3. Re-apply changes to data pages (REDO)           │
│  4. Roll back uncommitted transactions (UNDO)       │
│  5. Open for business                               │
└───────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - PostgreSQL WAL configuration**
```sql
-- Check WAL configuration (critical settings)
SHOW wal_level;
-- replica = enables streaming replication
-- logical = enables logical decoding (Debezium, etc.)

SHOW synchronous_commit;
-- on = fsync before returning to client (safest)
-- off = return before fsync (faster, small loss window)
-- remote_apply = wait for standby to apply (strongest)

-- Monitor WAL generation rate
SELECT pg_wal_lsn_diff(
  pg_current_wal_lsn(),
  '0/0'::pg_lsn
) / 1024 / 1024 AS wal_written_mb;

-- Check WAL lag on replicas
SELECT client_addr,
       state,
       pg_wal_lsn_diff(
         pg_current_wal_lsn(),
         sent_lsn
       ) AS send_lag_bytes,
       pg_wal_lsn_diff(
         sent_lsn,
         replay_lsn
       ) AS replay_lag_bytes
FROM pg_stat_replication;
-- If replay_lag_bytes is large → replica is behind
-- Risk of data loss on failover proportional to lag
```

**Example 2 - Kafka as a distributed WAL**
```java
// Kafka is a distributed WAL for event streams
// Each topic partition is an append-only log file

Properties props = new Properties();
props.put("bootstrap.servers", "kafka:9092");
props.put("key.serializer",
    "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer",
    "org.apache.kafka.common.serialization.StringSerializer");

// WAL durability settings:
// acks=all: write durably to all ISR replicas
// (equivalent to synchronous replication in PostgreSQL)
props.put("acks", "all");

// idempotence: exactly-once WAL semantics
props.put("enable.idempotence", "true");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// Each message is a WAL record: ordered, durable, append-only
// Consumer offset = checkpoint in WAL recovery terms
// Consumer restart = replay from offset (replay WAL from checkpoint)
producer.send(new ProducerRecord<>(
    "order-events",
    orderId,           // key = shard key (partition routing)
    orderJson          // value = WAL record payload
));

// Consumer is idempotent: same offset processed only once
// If consumer crashes: resume from last committed offset
// = crash recovery via WAL replay
```

**Example 3 - WAL-based Change Data Capture (CDC)**
```python
# Use PostgreSQL WAL for CDC via logical decoding
# Without CDC: polling table for changes (expensive)
# With WAL CDC: stream changes as they happen (efficient)

import psycopg2

# Connect to PostgreSQL with replication role
conn = psycopg2.connect(
    host="postgres",
    dbname="mydb",
    user="replication_user",
    password="secret",
    connection_factory=psycopg2.extras.LogicalReplicationConnection
)
cursor = conn.cursor()

# Create replication slot using pgoutput (logical decoding)
# pgoutput decodes WAL records into INSERT/UPDATE/DELETE
cursor.create_replication_slot(
    "cdc_slot",
    output_plugin="pgoutput"
)

# Start streaming WAL changes
cursor.start_replication(
    slot_name="cdc_slot",
    decode=True,
    options={"proto_version": "1",
              "publication_names": "my_publication"}
)

def process_change(msg):
    """Process each WAL record as a CDC event."""
    change = parse_wal_message(msg.payload)
    # change = {"op": "INSERT", "table": "orders",
    #            "new": {"id": 1, "status": "pending"}}
    # Publish to Kafka, update search index, etc.
    publish_to_kafka("db-changes", change)
    msg.cursor.send_feedback(flush_lsn=msg.data_start)

cursor.consume_stream(process_change)

# WAL-based CDC: no polling, no table locks, minimal overhead
# Latency: < 100ms from DB write to downstream event
```

---

### ⚖️ Comparison Table

| Property | WAL (PostgreSQL) | Binlog (MySQL) | Kafka Log | RocksDB WAL |
|---|---|---|---|---|
| **Purpose** | ACID durability + replication | Replication + PITR | Distributed durable log | Write-optimized durability |
| **Format** | Physical or logical | Row-based or statement | Append-only messages | Memtable + SSTable |
| **Replication** | Streaming (physical/logical) | Binlog replication | Consumer groups | Remote compaction |
| **CDC support** | Yes (logical decoding) | Yes (Debezium) | Native | Via RocksDB listener |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| WAL slows down writes (extra disk write) | WAL uses sequential I/O (appends). Sequential writes are faster than the random I/O of data page updates. WAL often IMPROVES write throughput by batching random updates behind sequential log writes. |
| You can disable fsync for performance in production | `fsync=off` in PostgreSQL means WAL records are not guaranteed on disk before returning to client. A kernel crash can cause data corruption. Never disable fsync in production. Use `synchronous_commit=off` instead (small loss window, no corruption). |
| WAL and event sourcing are different concepts | They are the same pattern at different layers. WAL is event sourcing for databases: changes are recorded as an ordered log of events; current state is derived by replaying the log. Kafka is event sourcing for application-level data streams. |

---

### 🚨 Failure Modes & Diagnosis

**WAL Volume Fills Disk → Database Stops**

**Symptom:**
PostgreSQL stops accepting writes. Error: "no space left
on device." WAL directory (`pg_wal/`) is consuming
100% of the disk. All database connections are blocked.

**Root Cause:**
A long-running replication slot is holding the WAL
back. PostgreSQL cannot delete WAL files that have
not been consumed by all replication slots.

**Diagnosis and Fix:**
```sql
-- Find which slot is blocking WAL cleanup
SELECT slot_name,
       pg_wal_lsn_diff(
         pg_current_wal_lsn(),
         restart_lsn
       ) AS retained_bytes,
       active
FROM pg_replication_slots;

-- If a slot is inactive (active=false) and has large
-- retained_bytes: it is blocking WAL cleanup
-- (e.g., a CDC consumer that has been down for days)

-- Emergency: drop the inactive slot
-- WARNING: the consumer will need to re-sync from scratch
SELECT pg_drop_replication_slot('stuck_cdc_slot');

-- Prevention: set max_slot_wal_keep_size in postgresql.conf
-- max_slot_wal_keep_size = 10GB
-- PostgreSQL will invalidate slots that would require
-- retaining more than 10GB of WAL
-- (consumer must resync; better than outage)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Leader-Follower Pattern` - WAL streaming is how
  leader replicates state to followers

**Builds On This (learn these next):**
- `Data Partitioning Strategies` - WAL is partitioned
  per shard in distributed databases
- `Event Sourcing` - the application-level equivalent
  of WAL: ordered log as source of truth

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RULE          │ Write log record BEFORE data page change  │
│               │ fsync() log before returning to client   │
├───────────────┼──────────────────────────────────────────┤
│ RECOVERY      │ Replay WAL from last checkpoint          │
│               │ REDO committed; UNDO uncommitted txns    │
├───────────────┼──────────────────────────────────────────┤
│ PERFORMANCE   │ Sequential appends (fast)               │
│               │ Data pages updated async (background)    │
├───────────────┼──────────────────────────────────────────┤
│ REPLICATION   │ Stream WAL records to replicas           │
│               │ Sync = no data loss; Async = low latency │
├───────────────┼──────────────────────────────────────────┤
│ CDC           │ Logical decoding decodes WAL to         │
│               │ INSERT/UPDATE/DELETE events              │
├───────────────┼──────────────────────────────────────────┤
│ KAFKA         │ Kafka partitions ARE a WAL               │
│               │ Consumer offset = checkpoint             │
├───────────────┼──────────────────────────────────────────┤
│ DANGER        │ fsync=off → corruption on crash         │
│               │ Inactive replication slots → disk full  │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "Log first, then write. Replay log on   │
│               │  crash. Stream log to replicas."        │
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Data Partitioning Strategies             │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. WAL = append log record before changing data page.
   Sequential appends are fast. fsync log to disk
   before returning to client (ACID durability).
2. Crash recovery: replay WAL from last checkpoint.
   REDO committed transactions. UNDO uncommitted ones.
   Recovery time = checkpoint interval (usually seconds).
3. WAL enables replication (stream log to replicas)
   and CDC (decode log to INSERT/UPDATE/DELETE events).
   Inactive replication slots hold WAL on disk - monitor
   and drop them if they fall behind.

**Interview one-liner:**
"Write-Ahead Logging guarantees durability by appending a log record
before any data page modification. The 'write-ahead' contract: the
log record must be on disk (fsynced) before the data page is changed.
On crash, recovery replays the WAL from the last checkpoint, re-applying
committed transactions and rolling back uncommitted ones. WAL uses
sequential I/O (appends) which is far faster than the random I/O of
data page updates. Two key applications beyond crash recovery: (1)
streaming replication - ship WAL records to replicas; (2) CDC via
logical decoding - decode WAL into INSERT/UPDATE/DELETE events for
downstream systems. Kafka's architecture is WAL applied to distributed
message streaming: each partition is an append-only log file, consumer
offsets are checkpoints, and consumer restart is crash recovery via log replay."
