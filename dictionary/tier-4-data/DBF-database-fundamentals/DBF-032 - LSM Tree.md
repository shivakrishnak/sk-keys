---
version: 1
layout: default
title: "LSM Tree"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /databases/lsm-tree/
id: DBF-032
category: Database Fundamentals
difficulty: ★★★
depends_on: B+ Tree, B-Tree, WAL (Write-Ahead Log)
used_by: RocksDB, Cassandra, LevelDB, HBase
related: B+ Tree, Write Amplification, Compaction
tags:
  - database
  - data-structures
  - indexing
  - nosql
  - deep-dive
---

# DBF-032 - LSM Tree

⚡ TL;DR - An LSM Tree (Log-Structured Merge Tree) converts all writes into sequential append operations - never modifying data in place - then periodically merges sorted files, trading read amplification for dramatically lower write amplification than B+ Trees.

| #427            | Category: Database Fundamentals          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | B+ Tree, B-Tree, WAL (Write-Ahead Log)   |                 |
| **Used by:**    | RocksDB, Cassandra, LevelDB, HBase       |                 |
| **Related:**    | B+ Tree, Write Amplification, Compaction |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A B+ Tree index handles 50,000 writes/second on a high-write event-tracking system. Each write randomly modifies a leaf page (random I/O). A 1TB SSD does ~500,000 random 4KB writes/second - but the B+ Tree adds overhead: page splits, parent updates, write-ahead logging. Effective throughput: ~30,000 writes/second. At 100,000 events/second: queue builds up, latency spikes, data is dropped. The system can't keep up with the write rate.

**THE BREAKING POINT:**
HDDs had ~150 random IOPS but ~100 MB/s sequential writes - ~600× faster sequential vs. random. SSDs close this gap but random writes still degrade SSD cells faster (write endurance) and have higher latency than sequential writes. Any storage medium benefits from sequential access patterns.

**THE INVENTION MOMENT:**
"Never modify data in place. Always append. Compact periodically. Reads do more work, writes do almost none."

---

### 📘 Textbook Definition

An **LSM Tree (Log-Structured Merge Tree)** is a data structure designed for write-optimized storage. It buffers writes in memory (memtable), periodically flushes the sorted memtable to disk as immutable sorted string table files (SSTables), and periodically merges SSTables across levels (compaction). All writes are sequential appends - never in-place modifications. Reads must search the memtable and potentially multiple SSTable levels to find the latest version of a key. Used by: RocksDB (Meta, Uber, MySQL MyRocks), Apache Cassandra (SSTables), LevelDB, HBase, ClickHouse (MergeTree engine), Apache Kafka (log segments), Elasticsearch (Lucene segments). The trade-off: write amplification is reduced (no page splits, sequential writes); read amplification is increased (must search multiple levels/files).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
LSM Tree = in-memory sorted buffer + sequential disk files + periodic merge - optimizes writes by eliminating random I/O entirely.

**One analogy:**

> An inbox/outbox system. Instead of immediately filing every new document in its exact alphabetical folder (random access - find the right folder, insert it), you pile all new documents in an inbox (memtable). Periodically, you sort the inbox and file the sorted batch into a new shelf (SSTable flush). Periodically, you merge multiple sorted shelves into a single sorted shelf (compaction). Reading requires checking the inbox and all shelves - more work for the reader, but the writer never searches for a folder.

**One insight:**
LSM Trees trade "read amplification" (reading must check multiple levels) for "write amplification" (writes are sequential appends). The bet: writes are more frequent than reads in certain workloads (time-series, logs, events) - making the trade worthwhile. Also: sequential writes are much kinder to SSD endurance than random writes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Memtable:** In-memory sorted write buffer (typically a red-black tree or skip list). All writes go here first - O(log n) in-memory insert.
2. **WAL:** Every memtable write is also appended to a WAL (crash recovery). Write path: WAL append → memtable insert → client ACK.
3. **SSTable (Sorted String Table):** When memtable reaches threshold (e.g., 64MB), it is sorted and flushed to a new SSTable file (immutable, sequential write). Each SSTable has a bloom filter to speed point lookups.
4. **Levels:** SSTables are organized into levels (L0, L1, L2, ...). L0: freshly flushed SSTables (may have overlapping key ranges). L1+: compacted SSTables with non-overlapping key ranges within a level.
5. **Compaction:** Background process merges SSTables within/between levels. L0→L1 compaction: merge L0 files with overlapping L1 files → new sorted L1 files. L1→L2: similar. Compaction sorts, deduplicates, and applies deletes (tombstones).

**DERIVED DESIGN:**
**Write path (RocksDB):**

1. Append to WAL (sequential, durable).
2. Insert into memtable (in-memory sorted tree).
3. Client receives ACK.
4. When memtable full → immutable memtable → flushed to L0 SSTable (sequential disk write).

**Read path:**

1. Check memtable (most recent writes).
2. Check immutable memtable (if present).
3. Check L0 SSTables (may have overlapping ranges → check ALL L0 files) - use bloom filter to skip files that don't contain the key.
4. Check L1 SSTables (non-overlapping → binary search to find the single relevant file).
5. Check L2, L3, ... until key found or all levels exhausted (key not found).

**Bloom filter:** Probabilistic data structure per SSTable. For a given key: "definitely not in this SSTable" (skip it) or "possibly in this SSTable" (read it). False positive rate ~1%. Without bloom filters, every point read would require reading every SSTable file.

**THE TRADE-OFFS:**
**Gain:** Write throughput: 5–10× better than B+ Tree for write-heavy workloads. Sequential I/O → better SSD endurance. Crash recovery via WAL is simple. Compaction naturally deduplicates and applies deletes.
**Cost:** Read amplification: checking multiple levels for any key (partially mitigated by bloom filters). Space amplification: during compaction, old data coexists with new data (compaction can temporarily require 2× disk space). Compaction I/O competes with user reads/writes (compaction stalls). Deleted keys require tombstone propagation until compaction.

---

### 🧪 Thought Experiment

**SETUP:**
An IoT platform receives 500,000 sensor readings per second, each ~200 bytes. Keys are sensor_id + timestamp (monotonically increasing). Reads are: 90% range scans ("get last 1 hour of readings for sensor 42"), 10% point lookups.

**WITH B+ TREE:**

- 500K writes/second to B+ Tree on SSD: theoretical 500K IOPS, but B+ Tree page splits and random I/O reduce effective throughput to ~150K writes/second.
- WAL + data page write per insert: write amplification ~2×.
- Range scans for recent data: mostly cached in buffer pool - fast.
- Bottleneck: write throughput at peak.

**WITH LSM TREE (RocksDB):**

- 500K writes/second: all go to memtable (in-memory) + WAL (sequential). Effective write throughput: 500K/second with minimal latency (sub-millisecond).
- Compaction runs in background, consuming ~200 MB/s write I/O.
- Range scans for recent data: mostly in memtable or L0/L1 (recent data) - fast for recent queries. Older data: L2/L3 SSTables, requires 2–3 level reads.
- Point lookups: bloom filter on each SSTable eliminates 99% of unnecessary file reads.
- Bottleneck: compaction I/O can interfere with reads during heavy write bursts.

**THE INSIGHT:**
For monotonically increasing keys (timestamps, IDs), LSM Trees have near-zero write amplification - new keys always go to the most recent memtable/L0 files, compaction flows efficiently downward. B+ Tree random-key insertion causes 50%+ page split rate. LSM Tree is the natural fit for time-series and event workloads.

---

### 🧠 Mental Model / Analogy

> LSM Tree is like a library where new books are never shelved immediately - they pile up in the reading room (memtable). When the reading room is full, librarians sort the pile and place it as a new stack in the archive room (SSTable flush). Periodically, they merge stacks into larger, better-organized stacks (compaction). A reader looking for a specific book must check: the reading room, then each archive stack. A reader looking for all books on a topic (range scan) finds them by scanning the sorted stacks.

- "Reading room" → memtable (in-memory sorted buffer)
- "Sorted pile placed in archive" → SSTable flush (sequential disk write)
- "Merging stacks" → compaction (background sorted merge)
- "Checking reading room + each stack" → read amplification
- "New books always go to reading room, never shelved mid-stack" → no in-place modification

Where this analogy breaks down: Unlike a library where readers find the same book each time, databases update and delete keys - LSM Trees handle this via "newest version wins" on read and tombstone records for deletes, resolved during compaction.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An LSM Tree is a storage structure used by high-write databases. Instead of modifying data in place (like a sorted file), every write goes into a memory buffer. When the buffer fills, it's saved as a sorted file on disk. Periodically, these files are merged. This makes writes very fast (just add to the buffer) at the cost of reads being slightly slower (may need to check multiple files).

**Level 2 - How to use it (junior developer):**
LSM Trees are the storage engine behind RocksDB, Cassandra, and LevelDB. As a developer: use Cassandra's CQL or RocksDB's Java/C++ API. Key operational awareness: (a) `compaction` is the background process - tune its concurrency for performance; (b) deleted data leaves "tombstones" - large deletes require compaction to clean up; (c) bloom filter false positive rate affects read performance (tune `bloom_filter_bits_per_key`).

**Level 3 - How it works (mid-level engineer):**
RocksDB levels: L0 (fresh SSTables, may have overlapping keys), L1 (max 256MB, non-overlapping), L2 (max 2.56GB), ... (10× per level). L0→L1 compaction: pick all L0 files + overlapping L1 files → merge-sort → write new L1 files → delete old files. This is "leveled compaction" (LevelDB/RocksDB default). Alternative: "size-tiered compaction" (Cassandra default for write-heavy) - merge multiple SSTables of similar size. Bloom filter: per SSTable, 10 bits per key → 1% false positive rate. On point read: check memtable → check each level's SSTable bloom filters → read only SSTables where bloom filter says "possibly present." Without bloom filters, every level requires a file read even for non-existent keys.

**Level 4 - Why it was designed this way (senior/staff):**
LSM Trees were invented by Patrick O'Neil et al. (1996) as a response to the insight that sequential I/O is dramatically faster than random I/O on any storage medium. The core bet: if you can afford to do more I/O on reads (amplification), you can eliminate almost all random I/O on writes. Compaction introduces a secondary concern: write amplification from compaction itself. Leveled compaction has write amplification of O(levels × level_multiplier) - for 7 levels with 10× multiplier, write amplification can reach 10–30×. Size-tiered compaction has lower write amplification but higher space amplification and worse read performance. The tension between write amplification, read amplification, and space amplification is called the "RUM conjecture" - you can optimize for any two, but not all three simultaneously. This is why different compaction strategies exist: different workloads accept different trade-offs.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ LSM TREE: WRITE + READ PATH                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  WRITE PATH:                                         │
│  1. Write → WAL (seq append) → memtable (sorted)    │
│  2. Memtable full → flush → L0 SSTable (seq write)  │
│  3. L0 has 4 files → compact → L1 (merge-sort)      │
│  4. L1 exceeds 256MB → compact L1→L2 ...            │
│                                                      │
│  READ PATH (point lookup, key=X):                   │
│  1. Check memtable → found? Return.                 │
│  2. Check L0 SSTables (ALL of them - may overlap)   │
│     → bloom filter: "X not here" → skip            │
│  3. Check L1: binary search for relevant file       │
│     → bloom filter: "X maybe here" → read file     │
│  4. Check L2, L3 ... until found or exhausted       │
│                                                      │
│  AMPLIFICATION:                                     │
│  Write amp: 1 (seq WAL) + compaction overhead      │
│  Read amp: 1 + #levels checked (mitigated by bloom) │
│  Space amp: old + new versions coexist pre-compact  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Application writes key=K, value=V
→ WAL: sequential append (durable)
→ Memtable: insert into sorted in-memory tree
→ ACK to client
→ [LSM TREE ← YOU ARE HERE: memtable buffering]
→ Memtable full → immutable → flush to L0 SSTable
→ Compaction: L0→L1→L2 (background merge-sort)
→ Old SSTables deleted after compaction
```

**FAILURE PATH:**

```
Compaction falls behind write rate
→ L0 files accumulate (many overlapping key ranges)
→ Read amplification: every point read scans ALL L0 files
→ "Compaction stall": RocksDB slows writes when L0 > threshold
→ "Compaction stop": hard stop when L0 > stop_threshold
→ Writes blocked until compaction catches up
```

**WHAT CHANGES AT SCALE:**
At high write rates, compaction must be tuned to not fall behind. RocksDB: `max_background_jobs` controls compaction threads. Cassandra: `compaction_throughput_mb_per_sec`. If compaction can't keep up: L0 files accumulate → read amplification spikes → latency degrades for reads. Production rule: compaction throughput should be ≥ 10× write throughput (to handle periodic compaction spikes). SSD capacity must accommodate 1.1–2× actual data size (space amplification during compaction).

---

### ⚖️ Comparison Table

| Property                | B+ Tree                      | LSM Tree                                              |
| ----------------------- | ---------------------------- | ----------------------------------------------------- |
| **Write pattern**       | Random I/O (page splits)     | Sequential (append-only)                              |
| **Write amplification** | Low-medium (splits)          | Variable (1 write + compaction overhead)              |
| **Read performance**    | Excellent (single path)      | Good with bloom filters; worse for cold reads         |
| **Range scan**          | Efficient (leaf linked list) | Good (SSTables sorted; merge on read for multi-level) |
| **Space amplification** | Low (in-place)               | Medium (multiple versions during compaction)          |
| **Delete**              | Immediate in-place           | Tombstone → compaction needed                         |
| **Best for**            | Mixed read/write OLTP        | Write-heavy; time-series; events; logs                |
| **Used by**             | PostgreSQL, MySQL, Oracle    | RocksDB, Cassandra, LevelDB, HBase                    |

How to choose: B+ Tree for general OLTP with balanced reads/writes. LSM Tree for write-heavy workloads (IoT, events, time-series, message storage) where write throughput is the primary constraint.

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                              |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LSM Trees eliminate all write amplification           | Compaction itself causes write amplification - each byte written once to memtable may be rewritten 10–30× through compaction levels; LSM eliminates B+ Tree page-split write amp but introduces compaction write amp |
| Deletes in LSM Trees are instant                      | Deletes write a "tombstone" record - the actual data persists until compaction removes it; this can cause space to appear "unreclaimable" and deleted data to appear in range scans until compaction runs            |
| Bloom filters make LSM reads as fast as B+ Tree       | Bloom filters reduce but don't eliminate read amplification - false positives still cause unnecessary SSTable reads; cold reads on data in lower levels still require multiple I/Os                                  |
| LSM Trees are always better for append-only workloads | True for random-key workloads; for monotonically increasing keys (timestamps), B+ Tree's rightmost-leaf insertion is also nearly sequential - B+ Tree can be competitive for pure append-only time-series            |

---

### 🚨 Failure Modes & Diagnosis

**1. Compaction Stall / Write Stop**

**Symptom:** RocksDB/Cassandra write latency spikes suddenly to 1–10 seconds; `WriteStall` in RocksDB metrics; Cassandra write timeouts; reads also degrade.

**Root Cause:** L0 files accumulated faster than compaction can process them (write burst exceeds compaction throughput). RocksDB's `level0_slowdown_writes_trigger` (default 20) throttles writes; `level0_stop_writes_trigger` (default 36) halts writes.

**Diagnostic:**

```bash
# RocksDB: check compaction statistics
# In RocksDB logs or via GetProperty:
# rocksdb.stats - look for:
# Level 0: files = N (high = compaction backlog)
# Compaction stats: write_amp = (compaction writes / flush writes)

# Cassandra: check compaction metrics
nodetool compactionstats
# Look for "pending tasks" count
# > 50 = compaction backlog

nodetool tpstats
# Look for dropped messages / timeouts
```

**Fix:** Temporarily increase compaction threads: `rocksdb.Options.max_background_jobs = 8`. For Cassandra: `nodetool setcompactionthroughput 256` (MB/s). Reduce write rate if compaction cannot keep up. After recovery: tune `write_buffer_size` (larger memtables → fewer L0 flushes → less L0 accumulation).

**Prevention:** Provision compaction I/O at 3–5× write rate. Monitor L0 file count. Alert when L0 files > 10. Reserve 30–40% of disk I/O for compaction.

---

**2. Tombstone Accumulation / Read Amplification from Deletes**

**Symptom (Cassandra):** Range scans are slow even for queries returning few rows; Cassandra logs `GC pauses too frequent`; heap pressure from reading tombstones.

**Root Cause:** Heavy delete workloads write many tombstones. Until compaction removes them, tombstones accumulate across multiple SSTable levels. A range scan must read all tombstones to determine which keys are deleted - O(tombstones) work even for small result sets. At 10M tombstones, even a query returning 10 rows might scan millions of tombstones.

**Diagnostic:**

```bash
# Cassandra: check tombstone count per query
cqlsh> TRACING ON;
cqlsh> SELECT * FROM events WHERE sensor_id=42 LIMIT 10;
# Look for: "tombstone warnings" in trace output
# Default threshold: 100,000 tombstones → warning; 1M → timeout

# Check SSTable statistics
nodetool cfstats keyspace.table
# Look for "SSTable count" and "Max tombstones per read"
```

**Fix:** Run `nodetool compact keyspace.table` to force compaction and clean tombstones. For large delete workloads, use TTL-based expiration (`CREATE TABLE ... WITH default_time_to_live = 86400`) instead of explicit deletes - Cassandra handles TTL expiration more efficiently.

**Prevention:** Avoid patterns that generate many tombstones: deleting individual rows at high rate, time-series with per-row deletes. Use partition-level deletes (delete entire partition at once) or TTL for bulk expiration. Monitor tombstone per read metrics.

---

**3. Space Amplification During Compaction**

**Symptom:** Disk usage spikes to 2× normal size during compaction; alerts fire for disk space; compaction may fail if disk fills completely.

**Root Cause:** During L1→L2 compaction, both the old L1/L2 files AND the new compacted files exist simultaneously. For a 100 GB table, peak disk usage during full compaction can reach 150–200 GB.

**Diagnostic:**

```bash
# Check current disk usage by level (RocksDB)
# Via GetProperty("rocksdb.levelstats"):
# Level 0: X files, Y MB
# Level 1: X files, Y MB
# ...
# Total size = sum of all levels

# Before planning compaction, check free space
df -h /data/rocksdb
# Must have >= 2x current data size free for safe compaction
```

**Fix:** Provision disk at 2–2.5× expected data size. If compaction fails mid-run (disk full): free space manually (remove old WAL files, old SSTables from other columns/tables). Resume compaction. Consider tiered storage: hot data on SSD (L0/L1), warm data on HDD (L2+).

**Prevention:** Always provision 2× data size for LSM-backed storage. Alert when disk > 70% full (leaves buffer for compaction spikes). Use compression in SSTables (RocksDB: `snappy`, `zstd` compression → 40–60% space reduction).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `B+ Tree` - understand the structure LSM Trees replace for write-heavy workloads
- `WAL (Write-Ahead Log)` - LSM Trees use a WAL for the memtable; same mechanism
- `B-Tree` - understand why B+ Tree page splits create write amplification

**Builds On This (learn these next):**

- `Write Amplification` - the core trade-off LSM Trees navigate
- `NoSQL & Distributed Databases` - Cassandra, HBase, and others use LSM Trees
- `Observability & SRE` - monitoring compaction health is critical for LSM-backed systems

**Alternatives / Comparisons:**

- `B+ Tree` - read-optimized; lower read amplification; worse write amplification
- `Index Types (B-Tree, Hash, Composite, Covering)` - all built on B+ Trees in relational databases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Write-optimized structure: memtable +     │
│              │ immutable SSTables + background compaction│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ B+ Tree random writes too slow for        │
│ SOLVES       │ high write-throughput workloads           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Sequential writes always; reads search    │
│              │ multiple levels (mitigated by bloom filter│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Write-heavy: IoT, events, time-series,    │
│              │ log storage, message brokers              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Read-heavy OLTP with balanced reads/      │
│              │ writes - use B+ Tree there                │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Write amplification (low) ↔               │
│              │ Read amplification (higher) + compaction  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Append everything, merge later -         │
│              │  writes are fast, compaction cleans up"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Write Amplification → RocksDB → Compaction│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Trade-off) A messaging platform needs to store 10 billion messages per day (each ~500 bytes) with the following query pattern: 95% writes (new messages), 5% reads (most recent 100 messages per user, accessed within 1 hour of writing). Messages older than 30 days are deleted. Compare B+ Tree vs. LSM Tree for this workload on: write throughput, read latency for recent messages, delete cost, and disk space utilization. Which would you choose and why?

**Q2.** (TYPE E - First Principles Challenge) The RUM conjecture states: a storage structure cannot simultaneously minimize read amplification (R), update amplification (U = write amplification), and memory amplification (M = space amplification). Given this constraint, describe where B+ Trees and LSM Trees sit in the RUM triangle, and design a hybrid storage engine that optimizes for: low write amplification for recent data (last 24 hours) AND low read amplification for historical data (older than 24 hours). What architectural components would you need, and what trade-offs remain?
