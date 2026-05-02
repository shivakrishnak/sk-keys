---
layout: default
title: "Parquet"
parent: "Data Fundamentals"
nav_order: 503
permalink: /data-fundamentals/parquet/
number: "0503"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Columnar vs Row Storage, Binary Formats, Data Types, Apache Spark
used_by: Delta Lake, Apache Iceberg, Hudi, Data Lake, Apache Spark
related: ORC, Avro, Columnar vs Row Storage, Delta Lake, Data Compression
tags:
  - dataengineering
  - intermediate
  - bigdata
  - performance
  - spark
---

# 503 — Parquet

⚡ TL;DR — Parquet is the standard columnar file format for data lakes — it stores data by column with built-in compression and statistics, making analytics queries 10–50× faster than row formats.

| #503 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Columnar vs Row Storage, Binary Formats, Data Types, Apache Spark | |
| **Used by:** | Delta Lake, Apache Iceberg, Hudi, Data Lake, Apache Spark | |
| **Related:** | ORC, Avro, Columnar vs Row Storage, Delta Lake, Data Compression | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The Hadoop era stored data as text files (CSV, JSON) on HDFS.
A MapReduce job computing weekly revenue needed to read and
parse every byte of every record — even fields it never used.
A 500 GB log file with 50 columns, where the job used 3 columns,
meant reading 500 GB to get 30 GB of relevant data. HDFS
replication tripled storage. Compute nodes spent 60% of their
CPU parsing text instead of running business logic.

**THE BREAKING POINT:**
As data volumes grew to petabytes, the cost of reading
unnecessary columns became the dominant expense — both in time
and cloud storage bills. A 1-hour Spark job became acceptable.
A 10-hour job blocked the business. Text formats at petabyte
scale were simply not viable.

**THE INVENTION MOMENT:**
This is exactly why Parquet was created (co-designed by Twitter
and Cloudera in 2013). By storing each column's values
contiguously, Spark can fetch only the 3 columns a query needs,
skipping 94% of the bytes. With column-specific compression turning
30 GB into 3 GB, the same query now reads 3 GB of data. A 10-hour
job becomes 20 minutes. Same hardware, same data, different file
format.

---

### 📘 Textbook Definition

**Apache Parquet** is an open-source columnar binary file format
optimised for analytical workloads. Parquet stores data in
**row groups** (horizontal partitions of ~128 MB) within which
each column is stored as a separate **column chunk**. Each column
chunk is further divided into **data pages** (~1 MB). Parquet
applies column-type-specific encodings (dictionary encoding,
run-length encoding, delta encoding, bit packing) and then
optionally compresses each column chunk (Snappy, Zstandard,
GZIP). Row group footers contain column-level statistics (min,
max, null count, distinct count) that enable predicate pushdown:
query engines skip entire row groups without reading their data.
Parquet uses Apache Thrift for metadata serialisation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Parquet stores each column as its own block of bytes so queries
only read the columns they actually need.

**One analogy:**

> A traditional filing system stores complete employee folders —
> all documents for each person together. Parquet is a different
> system: one drawer holds every employee's salary, another holds
> every employee's name, another holds every department. To
> compute the average salary, you open only the salary drawer —
> not every folder.

**One insight:**
Parquet's magic comes from two compounding optimisations: column
pruning (read fewer columns) AND predicate pushdown (skip row
groups outside the query's range). Each eliminates 80–99% of
data independently. Combined, a single Spark query can read
0.1% of a table's bytes while returning correct results.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Analytics queries read few columns across many rows.
2. Column values are often highly compressible (repeated values,
   monotonic sequences, low cardinality).
3. Query engines can skip entire data segments if they know the
   min/max range of values in each segment.

**DERIVED DESIGN:**
Given invariant 1: store column values contiguously (columnar
layout). Column pruning eliminates reading entire column chunks
for columns not in the query.

Given invariant 2: apply column-type-specific encoding before
compression. The right encoding reduces size before the
compressor even runs:
- Low-cardinality strings (region, status) → dictionary encoding:
  replace "NORTH_EAST" with 1 byte integer → 90% size reduction
- Monotonic integers (IDs, timestamps) → delta encoding:
  store differences [1, 1, 1, 2, 1] instead of [1000, 1001,
  1002, 1004, 1005] → smaller numbers → more compressible
- Booleans or low-bit-depth values → bit packing:
  pack 8 booleans in 1 byte

After encoding: apply Snappy or Zstd for final compression.
Typical combined ratio: 5–10× for real-world data.

Given invariant 3: compute and store min/max/null statistics per
column chunk in the row group footer. Query engines read the footer
(free metadata, KB not GB), compare query predicates against
statistics, and skip entire 128 MB row groups that cannot contain
matching rows. This is **predicate pushdown**.

**THE TRADE-OFFS:**
**Gain:** 10–50× faster analytics; 5–10× compression; column
pruning; predicate pushdown; language-neutral open standard.
**Cost:** Immutable files (no in-place updates); poor random
access by row; requires a separate write phase for bulk loads;
complex metadata management for large tables (addressed by Delta
Lake, Iceberg).

---

### 🧪 Thought Experiment

**SETUP:**
1 billion rows × 40 columns. Mean row size 200 bytes.
Table total: 200 GB. Query: `SELECT AVG(price) WHERE region='NE'`
The `price` and `region` columns are 8 bytes and 10 bytes each.

**WITHOUT PARQUET (CSV / JSON):**
Engine reads 200 GB. Parses every character. Extracts `price`
and `region` from each row. Discards 38 columns of data per row.
Effective work: (8+10) bytes / 200 bytes = 9% work,
91% wasted I/O. At 500 MB/s disk throughput: **400 seconds**.

**WITH PARQUET (columnar, compressed):**
Column pruning: only read `price` (8×1B=8 GB raw) and `region`
(10×1B=10 GB raw) columns. With dictionary encoding, `region`
stores 4 distinct values as 1-byte IDs — 1 GB. `price` with
Snappy: 4 GB. Total I/O: **5 GB** (2.5% of original).
At 500 MB/s: 10 seconds. Plus predicate pushdown skips row
groups where region statistics exclude 'NE': maybe 70% more
rows skipped → **3 seconds**.

**THE INSIGHT:**
Column pruning and predicate pushdown each provide an order-of-
magnitude reduction independently. Combined, complex analytical
queries on petabyte datasets become feasible on small clusters.
Format is the primary performance lever — not more CPU.

---

### 🧠 Mental Model / Analogy

> Parquet is like a highly organised library with two innovations.
> First, instead of one section per book, there's one section
> per type of information — all "publication years" together,
> all "authors" together. Second, each section has a sign at
> the entrance: "this section contains years 1950–2020."
> If you need books from 2021+, you skip the entire section
> without entering.

- "Section per type" → column chunk (all values of one column)
- "Sign at entrance" → row group statistics (min/max in footer)
- "Skipping the section" → predicate pushdown
- "Taking only the year section" → column pruning
- "Section organised into sorted sub-shelves" → dictionary encoding

**Where this analogy breaks down:** Parquet's row group structure
means all the "year sections" are split into 128 MB blocks
(row groups). Within each block, all column sections are present.
Accessing a single row still requires reading data from each
column chunk within its row group.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Parquet is a file format for storing large amounts of data.
Unlike a spreadsheet where all fields for one row are together,
Parquet stores all values from one column together. This makes
it much faster to compute things like "average salary" because
you only need to read the salary column — not every row.

**Level 2 — How to use it (junior developer):**
In PySpark: `df.write.parquet("s3://bucket/data/")` and
`df = spark.read.parquet("s3://bucket/data/")`. Always add
`.select("col1","col2")` before reading to enable column pruning.
Use `.filter("date = '2024-01-01'")` before reading to enable
predicate pushdown. Partition tables by date/region on write:
`df.write.partitionBy("event_date").parquet(...)`. Avoid many
small files (target 128–512 MB each).

**Level 3 — How it works (mid-level engineer):**
File layout: `PAR1` magic (4 bytes) → row groups → file footer
→ footer length (4 bytes) → `PAR1` magic. Reader starts from
the END of the file: reads the last 8 bytes to get footer offset,
reads footer (Thrift-encoded), gets row group locations and
column statistics, decides which row groups and columns to fetch,
reads those byte ranges (using S3 range requests). This means
reading a Parquet file starts at the end, not the beginning — a
common gotcha when debugging. Encodings are specified per page in
page headers. `SNAPPY` compression is applied per column chunk;
`GZIP` per column chunk (slower but smaller).

**Level 4 — Why it was designed this way (senior/staff):**
Parquet's row group / column chunk hierarchy is a deliberate
compromise between the two extreme storage models: pure NSM
(row-at-a-time, good for OLTP) and pure DSM (column-at-a-time,
good for OLAP). A 128 MB row group means a streaming Kafka
consumer writing row-by-row will produce a new file every 128 MB
~ every few minutes at 1 MB/s — tolerable write frequency.
Within the 128 MB block, columnar layout means a Spark job
reading 5 of 50 columns reads 10% of each block — still a 10×
speedup. The file format designers explicitly chose 128 MB as the
HDFS block size — so one row group fits in one HDFS block,
enabling one-mapper-per-row-group parallelism. In the S3 era,
128 MB row groups align with S3 multi-part upload chunk sizes.
Every number in the layout was a hardware/network optimisation.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              PARQUET FILE LAYOUT                       │
├────────────────────────────────────────────────────────┤
│ Magic: "PAR1"                                          │
├────────────────────────────────────────────────────────┤
│ Row Group 0  (128 MB)                                  │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Column Chunk: region  [DICT+RLE | SNAPPY]          │ │
│ │   Data page 0 (1 MB): [0][0][1][0][2][1]...        │ │
│ │   Dict: {0:"NE", 1:"SE", 2:"SW"}                   │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ Column Chunk: price   [PLAIN | SNAPPY]             │ │
│ │   Data page 0 (1 MB): [85.0][92.5][78.3]...        │ │
│ └────────────────────────────────────────────────────┘ │
│ Row Group 1 ... Row Group N                            │
├────────────────────────────────────────────────────────┤
│ File Footer (Thrift)                                   │
│   Schema: {region: STRING, price: FLOAT, ...}         │
│   Row groups: [{offset, rows, columns: [min,max]}...] │
│   Footer length: 4 bytes                              │
│ Magic: "PAR1"                                          │
└────────────────────────────────────────────────────────┘
```

**Read path with predicate pushdown:**
```
Query: SELECT AVG(price) WHERE region = 'NE'

1. Read last 8 bytes → get footer offset
2. Read footer → column statistics per row group
   RG0: region min='NE', max='SW' → MAY contain NE → READ
   RG1: region min='SE', max='SW' → NO  NE → SKIP
   RG2: region min='NE', max='NE' → ALL NE → READ
3. For RG0 and RG2: read ONLY region + price column chunks
4. Filter region = 'NE', compute AVG(price)
```

---

### 💻 Code Example

**Example 1 — Write partitioned Parquet:**
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

df = spark.read.json("s3://raw/events/")

# Write Parquet partitioned by date for predicate pushdown
df.write \
  .mode("overwrite") \
  .partitionBy("event_date") \
  .option("compression", "snappy") \
  .parquet("s3://warehouse/events/")
```

**Example 2 — Read with column pruning and filter pushdown:**
```python
# Spark automatically applies column pruning and predicate pushdown
result = spark.read \
  .parquet("s3://warehouse/events/") \
  .select("device_id", "temperature") \  # column pruning
  .filter("event_date = '2024-01-15'") \ # partition pruning
  .filter("temperature > 90")            # predicate pushdown
  .groupBy("device_id") \
  .agg({"temperature": "avg"})

# Verify with explain
result.explain(True)
# Look for: PartitionFilters, PushedFilters, ReadSchema
```

**Example 3 — Inspect Parquet metadata:**
```python
import pyarrow.parquet as pq

# Read metadata WITHOUT reading data
meta = pq.read_metadata("s3://warehouse/events/part-0.parquet")
print(f"Rows: {meta.num_rows}")
print(f"Row groups: {meta.num_row_groups}")
print(f"Columns: {meta.schema.names}")

for i in range(meta.num_row_groups):
    rg = meta.row_group(i)
    for j in range(rg.num_columns):
        col = rg.column(j)
        stats = col.statistics
        if stats:
            print(f"  RG{i} {col.path_in_schema}:"
                  f" min={stats.min}, max={stats.max}")
```

**Example 4 — Compaction (fix small files):**
```python
# BAD: many small files (streaming writes)
# Produces 10,000 files × 1 MB = 10,000 Spark tasks on read

# GOOD: compact to fewer large files
df = spark.read.parquet("s3://bucket/raw/")
df.coalesce(100) \  # 100 files × 100 MB each
  .write.mode("overwrite") \
  .parquet("s3://bucket/compacted/")
```

---

### ⚖️ Comparison Table

| Format | Layout | Native Indexes | Ecosystem | Best For |
|---|---|---|---|---|
| **Parquet** | Columnar | Row group stats | Spark, Hive, Presto | General data lake analytics |
| ORC | Columnar | Stripe+Bloom filter | Hive, Hive ACID | Hive-heavy workloads, updates |
| Avro | Row | None | Kafka, Hadoop | Streaming, full-row serialisation |
| Delta Lake | Columnar (Parquet) | Transaction log + stats | Spark, Databricks | ACID on Parquet, upserts |
| Iceberg | Columnar (Parquet) | Manifests + stats | Spark, Flink, Trino | Multi-engine open table format |

**How to choose:** Parquet for any Spark/Presto/Trino/BigQuery data
lake workload. ORC for Hive-primary workloads (better Hive ACID
integration). Layer Delta Lake or Iceberg on top of Parquet when
you need ACID transactions, upserts, and time travel.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Parquet is a database | Parquet is a file format with no query engine, no transactions, and no indexes. All query engines are external (Spark, Trino, DuckDB) |
| All Parquet files are well-optimised | Poorly written Parquet (unsorted, small row groups, wrong partitioning) can be slower than well-written CSV for some queries |
| Predicate pushdown always works | Pushdown only works on columns with non-null statistics in the footer. If statistics were disabled at write time (rare but possible), all row groups are read |
| Parquet supports updates | Parquet files are immutable. "Updates" require rewriting affected row groups or entire files — use Delta Lake/Iceberg for ACID updates on Parquet |
| Snappy is always the right compression | Snappy is fast (good for Spark) but not smallest. Zstd achieves 30% better compression with similar decompression speed. GZIP achieves best compression but slowest. |

---

### 🚨 Failure Modes & Diagnosis

**Too Many Small Parquet Files**

**Symptom:**
Spark job reading a Parquet table creates 100,000 tasks.
Job planning takes longer than execution. S3 LIST calls time out.

**Root Cause:**
Many small files created by streaming writes or over-partitioned
batch writes. One Spark task per Parquet file → 100,000 tasks
for a table with 100,000 × 1 MB files = 100 GB total, but task
overhead dominates.

**Diagnostic Command / Tool:**
```bash
aws s3 ls s3://bucket/table/ --recursive | \
  awk '{print $3}' | \
  python3 -c "
import sys, statistics
sizes = [int(l) for l in sys.stdin]
print(f'Count: {len(sizes)}')
print(f'Avg: {statistics.mean(sizes)/1024/1024:.1f} MB')
print(f'Max: {max(sizes)/1024/1024:.1f} MB')"
```

**Fix:**
Run compaction (Spark `coalesce`/`repartition`, Delta `OPTIMIZE`).
Target 128–512 MB per file.

**Prevention:**
Set `spark.sql.files.maxPartitionBytes = 134217728` (128 MB) to
auto-coalesce small files on read. Use Delta Lake `OPTIMIZE`
scheduled daily.

---

**Column Statistics Inaccurate (Predicate Pushdown Fails)**

**Symptom:**
Spark reads far more data than expected for a simple date filter.
`EXPLAIN` shows `DataFilters` but not `PushedFilters`.

**Root Cause:**
Statistics were not written (disabled at write time), or data is
not sorted so every row group spans the full value range.

**Diagnostic Command / Tool:**
```python
import pyarrow.parquet as pq
meta = pq.read_metadata("file.parquet")
# If statistics is None for any column:
col = meta.row_group(0).column(3)
print(col.statistics)  # None = no pushdown possible
```

**Fix:**
Re-write data sorted by the filter column. Ensure
`parquet.write.statistics=true` (Spark default).

**Prevention:**
Always write Parquet sorted by the most common filter column.
Validate row group statistics using `pyarrow` post-write.

---

**Schema Evolution Breaks Existing Readers**

**Symptom:**
After adding a new column to the Parquet schema, old Spark jobs
fail with `AnalysisException: cannot resolve column`.

**Root Cause:**
Old Spark jobs hard-code column position (index) rather than
column name for read. Parquet schema evolution shifts positions.

**Diagnostic Command / Tool:**
```python
import pyarrow.parquet as pq
schema = pq.read_schema("new_file.parquet")
print(schema)  # Inspect field names and types
```

**Fix:**
```python
# BAD: positional column access
row[4]  # breaks if new column inserted before position 4

# GOOD: named column access
row["region"]  # works regardless of schema changes
```

**Prevention:**
Always access Parquet columns by name. Use Parquet schema
merging (`spark.read.option("mergeSchema","true")`) when
reading tables with mixed schema versions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Columnar vs Row Storage` — Parquet is a specific
  implementation of columnar storage; understanding the
  concept before the implementation
- `Binary Formats` — Parquet is a binary format; context
  for why binary was chosen over text
- `Apache Spark` — the primary query engine for Parquet
  in data lake architectures

**Builds On This (learn these next):**
- `Delta Lake` — adds ACID transactions, CDC log, and
  efficient upserts on top of Parquet files
- `Apache Iceberg` — alternative open table format using
  Parquet underneath with multi-engine support
- `Data Compression (gzip, snappy, zstd, lz4)` — the
  compression codecs applied within Parquet column chunks

**Alternatives / Comparisons:**
- `ORC` — Hive's alternative columnar format with
  built-in Bloom filters and stripe-level indexes
- `Avro` — row-oriented counterpart for streaming;
  Avro and Parquet are complementary not competing
- `Delta Lake` — not an alternative but a layer on top
  that solves Parquet's immutability limitation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Open-source columnar binary file format   │
│              │ with per-column compression and stats     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Text formats force reading all columns    │
│ SOLVES       │ even when queries use 2 of 50             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Column pruning + predicate pushdown are   │
│              │ multiplicative — combine for 100× speedup │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Data lake OLAP analytics with Spark,      │
│              │ Trino, BigQuery, or Athena                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Streaming one row at a time; single-key   │
│              │ row lookups; data needing in-place updates│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Analytic read speed vs write complexity   │
│              │ and immutability                          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Parquet is the difference between a 10-  │
│              │  hour Spark job and a 20-minute one."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ORC → Delta Lake → Apache Iceberg         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spark job processes a 10 TB Parquet table daily.
The table has 50 columns and is partitioned by `event_date`.
The daily job runs `SELECT SUM(revenue) WHERE event_date = today
AND product_category = 'electronics'`. Today the job takes
45 minutes reading 2.1 TB of data. The table has 8 years of
history. Describe exactly what data is being read vs what
could be skipped, why 2.1 TB is still far more than theoretically
necessary, and what two architectural changes would bring it
under 5 minutes.

**Q2.** Delta Lake stores its transaction log alongside Parquet
files. When you run an `UPDATE` statement in Delta Lake, no
Parquet file bytes are modified. Explain the exact sequence of
operations Delta Lake performs for an update, why it doesn't
modify Parquet in place, and under what access pattern does this
design create a "data amplification" problem that makes Delta
Lake unsuitable.

