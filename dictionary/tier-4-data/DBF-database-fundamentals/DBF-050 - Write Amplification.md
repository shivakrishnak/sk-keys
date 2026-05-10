---
version: 2
layout: default
title: "Write Amplification"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /databases/write-amplification/
id: DBF-032
category: Database Fundamentals
difficulty: ★★★
depends_on: B+ Tree, LSM Tree, WAL
used_by: LSM Tree, SSD Storage, Index Design
related: LSM Tree, B+ Tree, WAL, Compaction
tags:
  - database
  - storage
  - performance
  - deep-dive
---

# DBF-054 - Write Amplification

⚡ TL;DR - Write amplification is the ratio of actual bytes written to storage vs. logical bytes a user wrote - a single 1KB user write can cause 10–50KB of physical storage writes due to WAL, copy-on-write, index updates, and compaction.

| #439            | Category: Database Fundamentals     | Difficulty: ★★★ |
| :-------------- | :---------------------------------- | :-------------- |
| **Depends on:** | B+ Tree, LSM Tree, WAL              |                 |
| **Used by:**    | LSM Tree, SSD Storage, Index Design |                 |
| **Related:**    | LSM Tree, B+ Tree, WAL, Compaction  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (the problem that write amplification CAUSES):**
An SSD is rated for 500TB total bytes written before wear-out. An application writes 1GB/day of user data - should last 1,370 years. But write amplification factor (WAF) is 30× - actual bytes written to SSD = 30GB/day. The SSD wears out in 46 years... except consumer SSDs have much lower TBW ratings. Enterprise NVMe at 3TB/day WAF: SSD rated for 500TB → 167 days to wear-out. Understanding write amplification is existential for storage system design.

**THE SECOND PROBLEM:**
B+ Tree page splits cause cascading writes: update one row → split a leaf page → rewrite two leaf pages + parent page → split propagates up → entire path from root to leaf rewritten. Every index on the table: same amplification per index.

**THE INVENTION MOMENT:**
"Count the actual bytes written vs. the logical bytes - the ratio exposes hidden I/O costs that determine throughput limits and storage device lifespan."

---

### 📘 Textbook Definition

**Write amplification** (WA or WAF - Write Amplification Factor) is the ratio of actual physical storage writes to logical application writes:

$$\text{WAF} = \frac{\text{Bytes written to storage device}}{\text{Bytes written by application}}$$

Sources of amplification: (1) **WAL (Write-Ahead Log)** - every data change is first written to the WAL, then again to the data file (2×); (2) **B+ Tree page splits** - updating a full page splits it into two, requiring rewriting both pages plus propagating the split up the tree; (3) **Full-page writes** - PostgreSQL writes entire 8KB pages (not just the changed bytes) after a checkpoint to handle partial write protection; (4) **Index updates** - N indexes per table → N×amplification on every row write; (5) **LSM Tree compaction** - data written to SSTables is rewritten repeatedly during compaction (WA factor 10–30× for level-based compaction); (6) **SSD-level WA** - the SSD's own garbage collection rewrites flash pages (WA factor 2–10× internal to the SSD). Total WAF = (database WA) × (SSD WA).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write amplification is how many bytes actually hit the disk for every byte you "wrote" - every index, WAL record, page split, and compaction multiplies the real I/O cost.

**One analogy:**

> You write one word on a Post-It note. But to guarantee durability, the office policy is: (1) write it in the draft notebook (WAL), (2) write it on the Post-It (data page), (3) because the Post-It might be torn partially, write the entire Post-It sheet to a safety archive too (full-page write), (4) your word appears in three different indexes - update all three (index updates), (5) once a week, all Post-Its are reorganized - yours gets rewritten 10 more times (compaction). You wrote one word; the office wrote it ~15 times.

**One insight:**
Write amplification is not always bad - it's a trade-off with read performance and durability guarantees. WAL provides crash safety. Full-page writes prevent partial-write corruption. Index updates enable fast reads. The question is not "how do I eliminate write amplification?" but "which amplification sources give me acceptable durability and read performance for my workload, and which can I reduce?"

---

### 🔩 First Principles Explanation

**SOURCE 1: WAL (2× amplification minimum):**

```
Application writes 4KB row change
→ WAL record written: ~4KB (before data page change)
→ Data page written: 8KB page containing the row
→ Minimum 2× amplification for any durable write
→ WAL is sequential (fast); data page is random (slower)
```

**SOURCE 2: PostgreSQL Full-Page Writes (FPW):**

```
After checkpoint: first modification to a page →
full 8KB page written to WAL (not just the change delta)
→ Protects against partial page writes during crash
→ On write-heavy workloads: WAL volume 2-4× higher than without FPW
→ PostgreSQL setting: full_page_writes = on (default, recommended)
```

**SOURCE 3: B+ Tree Page Splits:**

```
Page with 100 entries at 100% fill capacity + 1 new entry:
1. Split: original page split into two 50% full pages
2. Both leaf pages rewritten
3. Parent page updated with new key (potentially split too)
4. Split propagates up tree in worst case
→ 3-5× amplification for a path-length-3 tree on a full-fill insert
→ FILLFACTOR=70% prevents splits: pages have 30% space buffer
→ Reduces split frequency at cost of 30% more storage
```

**SOURCE 4: Multiple Indexes:**

```
Table has 5 indexes. Insert one row:
→ Write row to heap: 1 write
→ Update 5 B+ Tree indexes: 5 writes (each with own amplification)
→ Base amplification: 6× before WAL, full-page writes, splits
→ More indexes → more read speed, more write cost
```

**SOURCE 5: LSM Tree Compaction (major amplification source):**

```
Level-based compaction (RocksDB default):
L0 → L1: compaction reads L0 + L1, merges, rewrites L1
L1 → L2: L1 size × 10 = L2 max size; every L1 write compacts through L2
→ WA factor: 10× per level, 2 levels typical = 10-30× amplification
→ A 1KB write in memtable becomes 10-30KB written during compaction
→ Tiered compaction: lower WA (~10×) but more space amplification
```

**SSD-LEVEL WRITE AMPLIFICATION:**

```
SSD flash pages: ~4KB each (architecture varies)
SSD erase unit: ~128 pages (1 block)
Cannot overwrite in place: must erase entire block first
SSD garbage collection: copies live pages from partially-empty blocks,
  erases block, writes elsewhere
→ Internal SSD WA: 2-10× depending on fill level and GC pressure
→ Total WA = Database WA × SSD WA = potentially 30× × 5× = 150×
```

---

### 🧪 Thought Experiment

**SETUP:**
Database: 5 indexes on a heavily written table. PostgreSQL with WAL and full-page writes. SSD storage.

**SINGLE ROW INSERT (1KB user data):**

```
1. WAL record: ~1KB delta
2. Full-page write (post-checkpoint): 8KB page
3. Data heap page write: 8KB page
4. Index 1 update: 8KB leaf page (potentially + parent pages)
5. Index 2 update: 8KB
6. Index 3 update: 8KB
7. Index 4 update: 8KB
8. Index 5 update: 8KB

Subtotal: ~57KB database-level writes for 1KB user data
Database WAF: 57×

SSD-internal WAF: ~3× (assume moderate GC pressure)
Total WAF: 57 × 3 ≈ 171×

Application writes 1KB → storage device writes 171KB
```

**IMPACT:**

- SSD rated 500TB TBW
- Application writes 1GB/day → storage writes 171GB/day
- SSD life: 500,000GB / 171GB/day ≈ 2,924 days ≈ 8 years

**WITH OPTIMIZATION (fillfactor=70%, drop 3 unnecessary indexes):**

- 2 indexes instead of 5: 5 writes not 8
- FILLFACTOR=70%: splits less frequent
- Optimized WAF: ~20×
- Storage writes: 20GB/day
- SSD life: ~68 years

---

### 🧠 Mental Model / Analogy

> Write amplification is like carbon footprint of a shipment. You ship a 1kg package. But the actual carbon footprint is: 1kg item in 3kg of packaging materials + 100km local van delivery + 1000km by air + 200km by regional truck + 50km by local van + returns logistics overhead. You shipped 1kg; the total "footprint" was 30kg equivalent. Reducing carbon footprint (write amplification) means: smaller packaging (fewer indexes), direct routes (fewer compaction levels), avoiding air shipping (reduce full-page write frequency), consolidating shipments (batch writes).

- "1kg package" → user's logical write
- "Packaging materials" → WAL overhead
- "Multiple legs of transport" → WAL + data page + index updates + compaction
- "Carbon footprint total" → physical bytes written to storage
- "Direct route" → append-only writes (LSM tree memtable path)
- "Consolidating shipments" → batch writes, larger transactions

Where this analogy breaks down: Carbon footprint is cumulative and external; write amplification is immediate and internal - each write causes amplification in real time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you save data to a database, the database actually writes much more to the disk than just your data. It writes a backup copy first (WAL), updates multiple indexes, and occasionally reorganizes the data. The ratio of "how much was really written vs. how much you told it to write" is called write amplification. High write amplification wears out SSDs faster and limits how fast a database can accept writes.

**Level 2 - How to use it (junior developer):**
Reduce write amplification by: (1) only creating indexes that are actually used - each index amplifies every insert/update; (2) using `FILLFACTOR=70%` on frequently updated tables to leave buffer space and avoid page splits; (3) batching writes (one INSERT of 1000 rows amplifies less than 1000 individual INSERTs because WAL overhead is amortized); (4) choosing the right data structure - LSM tree-based stores (Cassandra, RocksDB) have higher WA from compaction but lower WA per individual write (sequential memtable appends).

**Level 3 - How it works (mid-level engineer):**
PostgreSQL `pg_stat_bgwriter` reveals write amplification signals: `buffers_checkpoint` (pages written during checkpoints), `buffers_clean` (pages written by background writer), `buffers_backend` (pages written by backends directly). High `buffers_backend` indicates I/O stalls during writes. WAL volume can be measured: `pg_current_wal_lsn()` or `pg_wal_lsn_diff()`. If WAL volume >> data change volume, high write amplification is occurring (likely from full-page writes or large transactions). To reduce WAL full-page write amplification: increase `checkpoint_completion_target` (spread checkpoints further apart, reducing FPW frequency per page) or increase `checkpoint_segments`/`max_wal_size` (fewer checkpoints → fewer FPW events). LSM tree WA measurement: `rocksdb.write-amplification-factor` statistic - should be tuned to 10–30× for typical workloads.

**Level 4 - Why it was designed this way (senior/staff):**
The RUM conjecture (Read-Update-Memory) formalizes the write amplification trade-off: in any index structure, you cannot simultaneously minimize read overhead (R), update overhead (U, = write amplification), and memory overhead (M). Optimizing for two forces sacrifice of the third. B+ Tree: optimizes read performance (O(log n)), pays in update overhead (page splits, cascading updates) and memory overhead (index fragmentation after splits). LSM tree: optimizes update overhead (sequential writes only), pays in read overhead (bloom filters + compaction needed for reads) and memory overhead (compaction temporary space). The practical implication: write-heavy workloads (time series, logging, IoT) should use LSM-based stores (Cassandra, InfluxDB, TimescaleDB) because their sequential write path has low per-write amplification - compaction happens asynchronously and can be tuned. Read-heavy workloads with occasional writes should use B+ Tree-based databases (PostgreSQL, MySQL) where read performance is critical and write amplification is manageable. The write amplification issue has become more critical as NVMe SSDs replaced spinning disks - SSDs have finite P/E (program/erase) cycles and explicit TBW (terabytes written) ratings, making write amplification a direct hardware lifecycle concern, not just a performance metric.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WRITE AMPLIFICATION: SOURCES PER USER WRITE          │
├──────────────────────────────────────────────────────┤
│                                                      │
│ User: UPDATE products SET price=9.99 WHERE id=100    │
│ Logical write: ~50 bytes (one column change)         │
│                                                      │
│ Database-level writes:                               │
│  [1] WAL delta record:           ~100 bytes          │
│  [2] Full-page write (post-CKP): 8,192 bytes         │
│  [3] Heap page (data file):      8,192 bytes         │
│  [4] price_idx leaf page:        8,192 bytes         │
│  [5] category_price_idx page:    8,192 bytes         │
│  ─────────────────────────────────────────           │
│  Total database writes:         ~32,868 bytes        │
│  WAF (database level):           657×                │
│                                                      │
│ SSD-internal writes (WA 3×):    ~98,604 bytes        │
│ TOTAL WAF:                       ~1,972×             │
│                                                      │
│ (extreme case: post-checkpoint + 2 indexes)         │
│ More typical WAF: 20-50× for balanced workloads     │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Application writes record
→ WAL record appended (sequential, fast)
→ Data page modified in buffer pool
→ [WRITE AMPLIFICATION ← YOU ARE HERE: multiple pages dirtied]
→ Index pages updated (one per index)
→ Background: dirty pages flushed at checkpoint
→ Each flushed page: physical I/O to SSD
→ SSD: block-level write with internal GC amplification
→ Total physical bytes >> logical bytes written
```

**FAILURE PATH (high WA causing write stalls):**

```
Workload: 100,000 row inserts/second
5 indexes on the table
WAF: 50× → physical writes = 5,000,000 pages/sec × 8KB = 40GB/s
SSD rated for 2GB/s write throughput
→ Buffer pool fills faster than flushed
→ Backends block on dirty page flush ("IOPS-bound insert")
→ Application: insert latency spikes from 1ms to 500ms
→ Root cause: too many indexes + high WAF exceeds SSD throughput

Diagnosis: pg_stat_bgwriter.buffers_backend > 0 sustained
Fix: DROP unused indexes, increase checkpoint_completion_target
     or switch to LSM-based store for write-heavy workload
```

**WHAT CHANGES AT SCALE:**
At cloud scale: write amplification drives storage IOPS costs directly. AWS gp3 EBS: 3,000 IOPS base (free), $0.005/provisioned IOPS above that. 50× WAF on a write-heavy workload means IOPS bill is 50× what logical throughput would suggest. WAF profiling and reduction directly translates to cloud infrastructure cost reduction.

---

### ⚖️ Comparison Table

| Storage Structure                | Write per User Write     | Read Overhead          | Space Overhead           | Best For              |
| -------------------------------- | ------------------------ | ---------------------- | ------------------------ | --------------------- |
| **B+ Tree (PostgreSQL)**         | 2-30× (WAL + splits)     | Low (O(log n))         | Moderate                 | Read-heavy OLTP       |
| **LSM Tree (Cassandra/RocksDB)** | 10-30× (compaction)      | Higher (bloom + merge) | Higher (compaction temp) | Write-heavy workloads |
| **Heap + WAL only**              | 2×                       | Sequential scan only   | Low                      | Append-only logs      |
| **Copy-on-Write B-Tree**         | 2× per split (new pages) | O(log n)               | Higher                   | Immutable snapshots   |

How to choose: B+ Tree for OLTP read workloads. LSM tree for high write throughput (IoT, logging, time series). Minimize indexes on write-heavy tables.

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                      |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| WAF only matters for SSDs                     | WAF matters for HDDs too (I/O bandwidth limits) but is critical for SSDs because of TBW limits and write latency amplification               |
| Dropping indexes reduces durability           | Indexes are not part of durability; WAL and checkpoints provide durability; dropping indexes only affects read performance, not crash safety |
| WAL is the main source of write amplification | WAL is one source; full-page writes, index updates, and LSM compaction often dominate total WAF                                              |
| Faster SSDs eliminate the WA problem          | Faster SSDs improve throughput but not TBW limits - write amplification still degrades SSD lifespan, just more slowly on a faster device     |

---

### 🚨 Failure Modes & Diagnosis

**1. SSD Lifespan Exhaustion from Unexpected Write Amplification**

**Symptom:** Production NVMe drives reaching end-of-life unexpectedly early; cloud provider alerts on disk write metrics; write latency increasing as SSD nears TBW limit.

**Root Cause:** Actual write amplification much higher than estimated - insufficient accounting for indexes, full-page writes, or LSM compaction.

**Diagnostic:**

```sql
-- PostgreSQL: measure WAL generation rate vs. data change rate
SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS wal_bytes_since_start;

-- Run for 1 minute, compare WAL bytes to expected data change bytes:
-- If WAL is 10× expected data change → high WA

-- Check bgwriter stats for physical I/O volume:
SELECT buffers_checkpoint, buffers_clean, buffers_backend,
       checkpoint_write_time, checkpoint_sync_time
FROM pg_stat_bgwriter;
```

**Fix:** Profile which tables have the highest write volume and most indexes. Drop unused indexes (`pg_stat_user_indexes.idx_scan = 0`). Enable `track_io_timing = on` for detailed I/O measurement. Tune `full_page_writes = off` only if using a filesystem with atomic writes (DANGEROUS - only on certain ZFS/CoW filesystems).

**Prevention:** Include SSD TBW in capacity planning: estimate WAF × logical write rate × SSD TBW. Review index count per table as part of schema review.

---

**2. Write Throughput Ceiling from Index Write Amplification**

**Symptom:** Insert throughput caps at N rows/second regardless of hardware scaling; IOPS metric at 100% on the storage device.

**Root Cause:** Too many indexes on a high-insert-rate table. Each index multiplies the write I/O.

**Diagnostic:**

```sql
-- Find tables with many indexes
SELECT t.relname AS table, COUNT(i.indexrelid) AS index_count
FROM pg_class t
JOIN pg_index i ON i.indrelid = t.oid
GROUP BY t.relname
ORDER BY index_count DESC;

-- Find unused indexes (candidates for removal)
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan < 100  -- rarely or never used
  AND indexname NOT LIKE 'pk_%'  -- keep primary keys
ORDER BY idx_scan;
```

**Fix:** Drop unused indexes. Consolidate multi-column indexes (one composite covers multiple queries). Use partial indexes (`WHERE status='ACTIVE'`) to reduce indexed rows. Batch inserts to amortize per-write overhead.

**Prevention:** For high-insert-rate tables (events, logs, time series): minimize indexes to only what's required for critical read paths. Use PostgreSQL `pg_partman` with partition pruning + single partition index instead of full-table indexes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `B+ Tree` - B+ Tree page splits are a primary source of write amplification
- `LSM Tree` - LSM compaction is the dominant WA source in LSM-based stores
- `WAL (Write-Ahead Log)` - WAL itself contributes 2× minimum write amplification

**Builds On This (learn these next):**

- `LSM Tree` - how compaction strategies (level vs. tiered) trade write vs. read amplification
- `Index Types` - understanding which indexes to create/drop to manage WA
- `SSD / NVMe storage` - TBW ratings make WA a direct hardware lifecycle concern

**Alternatives / Comparisons:**

- `Read Amplification` - the complementary problem: too many reads for a single logical read
- `Space Amplification` - LSM tree's third problem: temporary storage during compaction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMULA      │ WAF = Physical bytes written /            │
│              │       Logical bytes written               │
├──────────────┼───────────────────────────────────────────┤
│ SOURCES      │ WAL (2×), Full-page writes (up to 8KB/Δ) │
│              │ Index updates (N× per N indexes)          │
│              │ LSM compaction (10-30×)                   │
│              │ SSD GC (2-10× internal)                   │
├──────────────┼───────────────────────────────────────────┤
│ REDUCE IT    │ Drop unused indexes                       │
│              │ FILLFACTOR=70% on hot tables              │
│              │ Batch writes (amortize WAL overhead)      │
│              │ LSM for write-heavy; B+ for read-heavy    │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSE     │ pg_stat_bgwriter (buffers_backend)        │
│              │ WAL generation rate vs. data change rate  │
│              │ Unused index check: idx_scan = 0          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every index you add amplifies every      │
│              │  write - fewer indexes, longer SSD life"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LSM Tree → Index Design → B+ Tree         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Trade-off) An IoT platform ingests 1,000,000 sensor readings per minute (each ~500 bytes). They need to query: latest value per sensor (1M sensors), range queries over time for a specific sensor, and aggregate statistics per hour. Design a storage schema with exactly the indexes needed - no more, no less - to satisfy the three query patterns while minimizing write amplification. Justify each index.

**Q2.** (TYPE F - Comparison Depth) Compare PostgreSQL (B+ Tree) vs. Apache Cassandra (LSM tree) on write amplification for the same write workload. For a write of 1KB user data: trace all physical writes for each system (WAL/commit log, data file, index, compaction). Which has higher per-write amplification? Which is better for a write-heavy workload at scale, and why? What is the asymptotic write amplification behavior as the dataset grows for each?
