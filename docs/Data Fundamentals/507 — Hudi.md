hhnmmnmmjjjjjjj  ws---
layout: default
title: "Hudi"
parent: "Data Fundamentals"
nav_order: 507
permalink: /data-fundamentals/hudi/
number: "0507"
category: Data Fundamentals
difficulty: ★★★
depends_on: Parquet, ORC, Delta Lake, Apache Kafka, Apache Spark
used_by: Data Lakehouse, Data Mesh, Streaming Analytics
related: Delta Lake, Apache Iceberg, Parquet, Data Lake, Columnar vs Row Storage
tags:
  - dataengineering
  - advanced
  - streaming
  - bigdata
  - database
---

# 507 — Hudi

⚡ TL;DR — Apache Hudi enables high-frequency upserts and deletes on a data lake by using a Merge-on-Read model that appends changes and merges during reads, avoiding full file rewrites.

| #507 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Parquet, ORC, Delta Lake, Apache Kafka, Apache Spark | |
| **Used by:** | Data Lakehouse, Data Mesh, Streaming Analytics | |
| **Related:** | Delta Lake, Apache Iceberg, Parquet, Data Lake, Columnar vs Row Storage | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Uber's rider location data arrives as a stream of updates —
millions of position records changing every second. The data
lake must reflect the latest position for every active rider.
With plain Parquet + Delta Lake's Copy-on-Write model, every
update rewrites the entire Parquet file containing that rider's
record. At 100,000 updates per second, each touching different
records in different files, the write amplification is catastrophic:
you are rewriting gigabytes of Parquet files per second for
kilobytes of actual data changes.

**THE BREAKING POINT:**
Copy-on-Write table formats (Delta, Iceberg CoW) are optimal for
batch analytics where writes are infrequent and reads are frequent.
They are severely inefficient for streaming change data capture
(CDC) workloads where millions of individual records update each
minute. The write I/O grows proportionally to the number of "cold"
records that happen to share a Parquet file with "hot" records
being updated.

**THE INVENTION MOMENT:**
This is exactly why Hudi (Hadoop Upserts Deletes and Incrementals)
was created at Uber in 2016. Hudi's Merge-on-Read (MoR) model
appends changes to small delta log files alongside base Parquet/ORC
files. Reads merge the base + delta. Writes are fast (append-only
to delta log). Full rewrites happen asynchronously during compaction.

---

### 📘 Textbook Definition

**Apache Hudi** is an open-source data lake table format designed
for incremental data processing — specifically high-frequency
record-level upserts (insert + update) and deletes. Hudi supports
two storage types: **Copy-on-Write (CoW)** rewrites Parquet files
on every write (low read latency, high write cost — similar to
Delta Lake) and **Merge-on-Read (MoR)** appends changes to
Avro/Parquet delta log files alongside base ORC/Parquet files
(low write latency, higher read cost — reads merge base + deltas).
Hudi maintains a **timeline** of all table operations
(commit, compaction, clean, rollback) in a `.hoodie` directory.
Hudi provides built-in **incremental queries** — read only records
that changed since a given commit time — enabling efficient CDC
downstream pipelines.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Hudi keeps a small side-file of recent changes and merges them
into the main data only when you ask — making writes fast.

**One analogy:**

> Imagine updating a massive printed book. Copy-on-Write is like
> reprinting all pages that contain any edit every time you make
> a change. Merge-on-Read is like keeping a sticky note pad next
> to the book — write changes on sticky notes, attach them to
> the relevant pages, and consolidate them into the printed text
> only when you run a full reprint (compaction).

**One insight:**
The fundamental insight: separate the "record that a change
exists" (fast append to delta log) from "materialising the
latest view" (expensive merge or rewrite). By deferring the
materialisation, Hudi makes streaming updates orders of magnitude
cheaper at write time — at the cost of read-time merge overhead
if reads happen before compaction.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Random record updates to immutable Parquet files require
   rewriting every Parquet file touched by the update.
2. Appending to a log file is O(1) regardless of base file size.
3. Merging a small log with a large base on read is O(log records)
   if the log is kept small relative to the base.

**DERIVED DESIGN — MoR model:**
Given invariant 2: on upsert, write the changed records to an
Avro-format delta log file alongside the base Parquet file.
The base file is untouched. Write I/O ≈ changed record count.

On read: merge base file + all delta logs for that fileGroup.
Apply: inserts from logs not in base → insert; updates that
match a base record → override; deletes that match → exclude.

Compaction (async background job): periodically merge base +
all delta logs → new base file + empty log. After compaction,
reads are pure Parquet (fast). Frequency of compaction determines
trade-off between read overhead and write efficiency.

**DERIVED DESIGN — CoW model:**
Upsert triggers: find which base file contains the record
(using Hudi's index — Bloom filter by default), rewrite that base
file with the updated records. Higher write I/O but reads are
pure Parquet without merge overhead. Similar to Delta Lake CoW.

**Index types:**
- **Bloom filter** (default): per-file Bloom filters answer
  "is record key X in this file?" — enables targeted CoW file
  selection without reading all files.
- **HBase index**: external HBase table mapping record key →
  file ID — O(1) lookup, requires HBase dependency.
- **Bucket index**: consistent hash of record key → bucket →
  file — no index store required, constant-time lookup.

**THE TRADE-OFFS:**
**MoR Gain:** Write latency ~1/10 of CoW at high update rates.
**MoR Cost:** Read latency higher (merge overhead) until compaction.
**CoW Gain:** Read latency identical to plain Parquet after write.
**CoW Cost:** Write amplification — rewrites entire file per update.

---

### 🧪 Thought Experiment

**SETUP:**
A ride-sharing platform updates driver location every 3 seconds.
10,000 active drivers. 1 Parquet file per partition, 50,000
records per file, average file size 20 MB.

**WITH COPY-ON-WRITE (Delta Lake / Hudi CoW):**
Each location update = one record. To update driver #5,280 in
partition `city=NYC`, Hudi must:
1. Read the entire 20 MB NYC Parquet file.
2. Modify record #5,280.
3. Write a new 20 MB file.
That's 40 MB of I/O for 1 KB of real change.
At 10,000 updates/3s across partitions: ~133 updates/s.
In NYC partition alone: continuous 40 MB read + 20 MB write cycle.
Write amplification: 20,000×.

**WITH MERGE-ON-READ (Hudi MoR):**
Each location update = append 1 KB record to delta log for NYC
partition. No read. No file rewrite. I/O: 1 KB.
After 10 minutes: delta log has 3,000 entries. A read merges
the 20 MB base with 3 MB delta log → apply 3,000 updates.
Read cost: slightly higher. Write cost: 1 KB per update.
Write amplification: 1×.
Compaction runs every 30 minutes: clean merge, new 20 MB base.

**THE INSIGHT:**
MoR decouples write cost from base file size. CoW ties write cost
to base file size. For high-frequency updates on large files, this
difference is not linear — it's the difference between a viable
system and an unworkable one.

---

### 🧠 Mental Model / Analogy

> Think of Hudi's MoR as the way banks handle transaction ledgers.
> Instead of rewriting the "running balance" entry every second
> as thousands of transactions arrive, a bank records each
> transaction as a new row (append to delta log). The running
> balance (latest state) is computed by scanning from the last
> known balance + applying all new transactions. Periodically
> (end of day), the balance is updated and the ledger consolidated
> (compaction).

- "Running balance" → base Parquet file (latest compacted state)
- "New transaction entries" → Avro delta log file
- "Computing current balance" → read-time merge (base + logs)
- "End-of-day reconciliation" → Hudi compaction
- "Bank auditor reading full history" → Hudi incremental query

**Where this analogy breaks down:** Unlike a bank ledger where
all transactions are chronological, Hudi's delta logs reference
specific record keys. The merge is a key-based join, not just
a sequential sum — deletes are tombstones, updates must match
exactly by record key.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Hudi is a way to efficiently update individual records in a huge
data file without rewriting the whole file. When you change a
record, Hudi writes just the change to a small side-file.
When you read, it combines the big file and the small side-file
to show you the latest version.

**Level 2 — How to use it (junior developer):**
Set up Hudi with Spark: specify `hoodie.table.type = MERGE_ON_READ`
for streaming upserts or `COPY_ON_WRITE` for batch. Use
`HoodieSparkSqlWriter` or the DataFrame API with Hudi options.
Key config: `hoodie.datasource.write.recordkey.field` (the
primary key), `hoodie.datasource.write.partitionpath.field`
(partition field), `hoodie.upsert.shuffle.parallelism`.
Three query types: snapshot (latest state), incremental (only
changed records since time T), read-optimised (base files only,
no merge, fastest but potentially stale).

**Level 3 — How it works (mid-level engineer):**
Hudi table layout: `.hoodie/` (timeline: instant files),
`partition/` (base files + delta logs per file group).
Each "file group" = one base file ID + zero or more delta logs.
File group slice = {base file at time T} + {all delta logs after T}.
On upsert to MoR table:
1. Lookup which file group each incoming record belongs to
   (using index: Bloom filter checks each incoming record key
   against base file Bloom filters).
2. Records not in any base → INSERT: write new base file slice.
3. Records in a base file → UPDATE: append to that file group's
   delta log (Avro format, HoodieLogBlock structure).
Compaction: read all file group slices → merge → write new base
file → remove old delta logs.
Timeline: each operation creates an instant file in `.hoodie/`:
`20240115T100000.commit` (CoW), `20240115T100000.deltacommit`
(MoR), `20240115T100000.compaction.requested/inflight/completed`.

**Level 4 — Why it was designed this way (senior/staff):**
Hudi's origin at Uber was specifically for the "incremental ETL"
use case: replicate change data from production MySQL to the data
lake, enabling the data lake to reflect production state with
<30 minute latency. The CDC pipeline needed record-level MERGE
(not batch replace) and the ability to query "what changed since
timestamp T" without scanning the entire table. Delta Lake's
transaction log provides the latter but the former (CDC MERGE)
with CoW write amplification was prohibitive at Uber's scale.
Hudi's MoR model was the specific answer to the physics of the
problem: Parquet is immutable; you cannot update in place;
therefore defer the materialisation to background compaction.
The incremental query capability (batch jobs reading only
`delta_commit` files since last run timestamp) is Hudi's
signature feature that neither Delta nor Iceberg matched until their
recent incremental read additions — making Hudi the preferred
table format for CDC-to-analytics pipelines at companies with
sub-hour latency requirements on petabyte tables.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│          HUDI MoR TABLE LAYOUT                       │
│                                                      │
│  .hoodie/                                            │
│    20240115T100000.deltacommit                       │
│    20240115T103000.deltacommit                       │
│    20240115T110000.compaction.completed              │
│                                                      │
│  partition=2024-01-15/                               │
│    filegroup-001/                                    │
│      base-20240115T090000.parquet  ← last compaction │
│      delta-20240115T100000.log     ← 1st delta batch │
│      delta-20240115T103000.log     ← 2nd delta batch │
│    filegroup-002/                                    │
│      base-20240115T090000.parquet                    │
│      (no delta yet — no updates to these records)    │
└──────────────────────────────────────────────────────┘
```

**Read-time merge (snapshot query):**
```
For filegroup-001:
  1. Read base-20240115T090000.parquet → 50,000 records
  2. Read delta-20240115T100000.log → 200 updates + 5 deletes
  3. Read delta-20240115T103000.log → 150 updates
  4. Merge: apply updates (override base record by key)
             apply deletes (mark as tombstone, exclude)
  5. Return: 50,000 - 5 + (new inserts from log) records
```

**Incremental query (only changed records since T1):**
```
Select all delta_commit instants after T1:
→ 20240115T100000.deltacommit, 20240115T103000.deltacommit
Read only the delta log files for those commits
→ Returns ONLY the 350 changed records
→ Does NOT scan base files at all
```

---

### 💻 Code Example

**Example 1 — Hudi MoR upsert with PySpark:**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
  .config("spark.serializer",
    "org.apache.spark.serializer.KryoSerializer") \
  .config("spark.sql.extensions",
    "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
  .getOrCreate()

hudi_options = {
    "hoodie.table.name": "driver_locations",
    "hoodie.datasource.write.table.type": "MERGE_ON_READ",
    "hoodie.datasource.write.recordkey.field": "driver_id",
    "hoodie.datasource.write.partitionpath.field": "city",
    "hoodie.datasource.write.precombine.field": "ts",
    "hoodie.upsert.shuffle.parallelism": 200,
}

# Stream of CDC records (driver location updates)
cdc_df.write.format("hudi") \
  .options(**hudi_options) \
  .mode("append") \
  .save("s3://bucket/driver_locations/")
```

**Example 2 — Incremental query (CDC downstream):**
```python
# Read only records changed since a specific commit time
incremental_df = spark.read.format("hudi") \
  .option("hoodie.datasource.query.type", "incremental") \
  .option("hoodie.datasource.read.begin.instanttime",
          "20240115100000") \
  .load("s3://bucket/driver_locations/")

# Only 350 changed records returned — not 50M base records
incremental_df.write \
  .format("jdbc") \
  .option("url", "jdbc:postgresql://warehouse/db") \
  .mode("append") \
  .save()
```

**Example 3 — Trigger compaction:**
```python
from hudi import HoodieSparkUtils

# Run async compaction (MoR tables only)
spark.sql("""
  CALL run_compaction(
    op => 'schedule',
    table => 'driver_locations'
  )
""")
spark.sql("""
  CALL run_compaction(
    op => 'run',
    table => 'driver_locations'
  )
""")
```

---

### ⚖️ Comparison Table

| Use Case | Hudi MoR | Hudi CoW | Delta Lake | Iceberg CoW |
|---|---|---|---|---|
| High-freq CDC upserts | ★★★ Best | ★☆☆ Slow writes | ★★☆ Slow writes | ★★☆ Slow writes |
| Batch analytics reads | ★★☆ Merge overhead | ★★★ Pure Parquet | ★★★ Pure Parquet | ★★★ Pure Parquet |
| Incremental CDC query | ★★★ Native | ★★☆ Available | ★★☆ With CDF | ★★☆ With CDC |
| Multi-engine support | ★★☆ Spark+Flink | ★★☆ Spark+Flink | ★★☆ Spark-primary | ★★★ All engines |
| Write amplification | 1× (MoR) | 20-100× | 20-100× | 20-100× |

**How to choose:** Hudi MoR for streaming CDC pipelines with
>10,000 record updates/second. Hudi CoW for moderate-frequency
batch upserts. Delta/Iceberg for primarily analytical workloads
with infrequent updates. Iceberg for multi-engine requirements.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Hudi is just Delta Lake with a different name | Hudi's MoR model is architecturally distinct — Delta Lake only supports Copy-on-Write; Hudi's delta log append is fundamentally different |
| MoR reads are slow | MoR reads are fast if compaction runs regularly. The merge overhead is minimal when delta logs are small (< 20% of base file size) |
| Compaction must be synchronous | Hudi supports async background compaction — writes and reads continue while compaction runs in a separate job |
| Incremental queries are unique to Hudi | Delta Lake (Change Data Feed) and Iceberg both now support incremental reads, though with different APIs and performance characteristics |
| Hudi requires HBase | HBase index is optional; the default Bloom filter index requires no external service |

---

### 🚨 Failure Modes & Diagnosis

**Delta Log Accumulation (Compaction Lag)**

**Symptom:**
Snapshot query latency grows from 2s to 45s over 2 weeks.
MoR base files have 500+ delta log files each.

**Root Cause:**
Compaction job not running or failing silently. Delta logs
accumulate without being merged into base files. Merge overhead
at read time grows linearly with log count.

**Diagnostic Command / Tool:**
```bash
# Check Hudi timeline for compaction instants
aws s3 ls s3://bucket/driver_locations/.hoodie/ \
  | grep compaction | tail -20
# Should see recent .compaction.completed instants
# If none in past 30min: compaction is stalled
```

**Fix:**
Run manual compaction:
```python
spark.sql("CALL run_compaction(op => 'run', table => 'locations')")
```
Then schedule hourly compaction job.

**Prevention:**
Set `hoodie.compact.inline=true` for auto-compaction every N
delta commits. Monitor `.hoodie/` for accumulating log files.

---

**Record Key Mismatch (Duplicate Upserts)**

**Symptom:**
After upserts, the table contains duplicate records for
the same logical entity. `COUNT(DISTINCT driver_id)` < `COUNT(*)`.

**Root Cause:**
`hoodie.datasource.write.recordkey.field` is set to a non-unique
or composite field that doesn't match the actual uniqueness
constraint. New records are inserted instead of updating existing.

**Diagnostic Command / Tool:**
```python
df = spark.read.format("hudi").load("s3://bucket/locations/")
df.groupBy("driver_id") \
  .count() \
  .filter("count > 1") \
  .show()
# Any result here means duplicates
```

**Fix:**
Re-derive the correct record key configuration. If a composite
key is needed: `hoodie.datasource.write.recordkey.field = "col1,col2"`.
Deduplicate table: upsert with correct key to force coalescing.

**Prevention:**
Test upsert idempotency in staging: upsert same batch twice,
verify no duplicates via `COUNT(DISTINCT key)`.

---

**Bloom Index FPP Causing Full File Scans**

**Symptom:**
Hudi upsert job takes 3× longer than expected. Spark tasks
read many more files than hold the updated records.

**Root Cause:**
Bloom filter false positive rate too high. Index answers "maybe
in this file" for files that don't actually contain the record,
causing unnecessary file reads.

**Diagnostic Command / Tool:**
```python
spark.conf.set("hoodie.bloom.index.filter.type", "DYNAMIC_V0")
# Enable metrics to see false positive rate
spark.conf.set("hoodie.metrics.on", "true")
```

**Fix:**
Increase Bloom filter precision or switch to a bucket index:
```python
hudi_options["hoodie.index.type"] = "BUCKET"
hudi_options["hoodie.bucket.index.num.buckets"] = "256"
# Consistent hash → exact file, no false positives
```

**Prevention:**
For tables with > 10M records and high-frequency upserts,
benchmark Bloom vs Bucket index. Bucket index has no false
positives at the cost of fixed bucket count.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Parquet` — Hudi uses Parquet as the base file format
  for both CoW and MoR tables
- `Apache Kafka` — Hudi's primary use case is ingesting
  CDC streams from Kafka into a queryable data lake
- `Delta Lake` — understanding Delta Lake's CoW model
  highlights why Hudi's MoR model was created

**Builds On This (learn these next):**
- `Data Lakehouse` — Hudi is one of three table formats
  enabling the lakehouse architecture alongside Delta and Iceberg
- `Streaming Analytics` — Hudi's incremental query enables
  data lake → analytics pipelines with <1h latency

**Alternatives / Comparisons:**
- `Delta Lake` — CoW-only; simpler but higher write
  amplification for streaming upserts
- `Apache Iceberg` — multi-engine; CoW primary but MoR
  available via append + compaction patterns
- `ORC` — Hudi's default base file format for MoR tables
  (Hudi uses ORC for MoR base files, Parquet for CoW)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Data lake table format with Merge-on-Read │
│              │ for high-frequency streaming upserts      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Copy-on-Write has 10,000× write amplifi-  │
│ SOLVES       │ cation for high-frequency CDC workloads   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Write the change (fast), merge on read    │
│              │ (deferred) — decouples write from rewrite  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Streaming CDC ingest; >10K upserts/sec;   │
│              │ sub-hour data lake freshness required     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Primarily batch analytics with infrequent │
│              │ updates — plain Parquet + Delta is simpler│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Write speed vs read overhead              │
│              │ (until compaction runs)                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hudi writes the sticky note; compaction  │
│              │  rewrites the textbook."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Compression → Schema Registry →      │
│              │ Data Lakehouse                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment platform uses Hudi MoR to store transaction
records. The compaction job runs every 30 minutes. At 2 AM,
a fraud analyst runs: `SELECT * FROM transactions WHERE
status = 'PENDING' AND amount > 10000`. The query must return
an accurate, up-to-the-second view. The last compaction finished
22 minutes ago. Trace precisely what Hudi must read to answer
this query, how long the merge step takes relative to a pure-Parquet
read, and what the analyst can do to get faster reads without
waiting for compaction.

**Q2.** A company runs both Hudi (for streaming CDC ingest) and
a business intelligence tool that only supports reading plain
Parquet files (no Hudi runtime). The BI tool must read the latest
state of the Hudi table. Using your knowledge of Hudi's read-
optimised query type, explain what data it returns vs a snapshot
query, the staleness window, and design a nightly compaction
schedule that bounds the staleness to < 1 hour for the BI tool
without adding runtime dependencies to the BI tool.

