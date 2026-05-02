---
layout: default
title: "Parquet"
parent: "Data Fundamentals"
nav_order: 503
permalink: /data-fundamentals/parquet/
number: "503"
category: Data Fundamentals
difficulty: ★★☆
depends_on: "Columnar vs Row Storage, Binary Formats (Avro, Parquet, ORC, Protobuf)"
used_by: "Delta Lake, Spark analytics, Athena, Trino, BigQuery external tables, Iceberg"
tags: #data, #parquet, #columnar, #compression, #analytics, #data-lake, #spark
---

# 503 — Parquet

`#data` `#parquet` `#columnar` `#compression` `#analytics` `#data-lake` `#spark`

⚡ TL;DR — **Apache Parquet** is the dominant open-source columnar file format for data lake analytics. Stores data column-by-column with per-column compression (snappy/zstd/gzip). Column statistics and predicate pushdown enable skipping irrelevant data. The de facto standard for S3-based data lakes (Spark/Athena/Trino/BigQuery external).

| #503 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Columnar vs Row Storage, Binary Formats (Avro, Parquet, ORC, Protobuf) | |
| **Used by:** | Delta Lake, Spark analytics, Athena, Trino, BigQuery external tables, Iceberg | |

---

### 📘 Textbook Definition

**Apache Parquet**: an open-source, binary, columnar storage format designed for the Apache Hadoop ecosystem. Developed jointly by Twitter and Cloudera (2013). Key structural concepts: **Row Group** (horizontal partition of rows, typically 128MB–1GB), **Column Chunk** (all values of one column within one row group), **Page** (smallest unit within a column chunk, typically 1MB). Each row group stores column statistics (min, max, null count, distinct count) in the **file footer** (metadata). Supports nested schemas via Dremel-encoding (required/optional/repeated fields → handles arrays, maps, nested records). Supported compression codecs: UNCOMPRESSED, SNAPPY, GZIP, LZO, BROTLI, LZ4, ZSTD. Supported encoding schemes: PLAIN, RLE (run-length), BIT_PACKED, DELTA_BINARY_PACKED, DELTA_LENGTH_BYTE_ARRAY, DELTA_BYTE_ARRAY, RLE_DICTIONARY. Ecosystem: natively read/written by Spark, Flink, Pandas (via PyArrow), Athena, Trino/Presto, BigQuery, Snowflake (external tables), DuckDB, Delta Lake, Apache Iceberg.

---

### 🟢 Simple Definition (Easy)

Parquet is a file format for storing large datasets efficiently. Unlike CSV (stores all columns of each row together), Parquet stores each column separately — all IDs together, all amounts together, all cities together. When you query "sum of amounts for Seattle orders," Parquet reads only the "amount" and "city" columns — skipping everything else. Plus, Parquet compresses each column individually (repeated cities like "Seattle" compress to almost nothing). Result: 10x smaller than CSV, 50x faster to query.

---

### 🔵 Simple Definition (Elaborated)

Parquet is the lingua franca of data lake storage for three reasons:

1. **Column pruning**: `SELECT amount, city` only reads those 2 columns from disk — skips all others. In a 50-column table, you skip 48 columns.

2. **Predicate pushdown**: `WHERE date = '2024-01-15'` can skip entire row groups where `max(date) < '2024-01-15'` — without reading any data in those row groups (just footer metadata).

3. **Compression**: per-column compression is far more effective than per-row compression because all values in a column have the same type and often similar values (e.g., city names → dictionary of 100 values encoding 100M records).

The only downside: Parquet is immutable (append-only, no in-place updates). Delta Lake and Apache Iceberg add a transaction layer on top to support updates, deletes, and ACID operations.

---

### 🔩 First Principles Explanation

```
PARQUET FILE STRUCTURE:

  ┌────────────────────────────────────────────────────────────────┐
  │ Magic: PAR1 (4 bytes)                                          │
  │                                                                │
  │ ROW GROUP 1 (rows 0 - 131,071, ~128MB uncompressed):          │
  │ ┌─────────────────────────────────────────────────────────┐   │
  │ │ Column Chunk: "order_id" (INT64)                        │   │
  │ │   Page 1 (1MB): [delta-encoded int64 values]            │   │
  │ │   Page 2 (1MB): [delta-encoded int64 values]            │   │
  │ │   Statistics: min=1001, max=132072, null_count=0        │   │
  │ ├─────────────────────────────────────────────────────────┤   │
  │ │ Column Chunk: "city" (BYTE_ARRAY / RLE_DICTIONARY)      │   │
  │ │   Dictionary page: ["Seattle","NYC","Austin","Chicago"] │   │
  │ │   Data pages: [0,1,0,2,3,0,1,...] (dict indices, 1 byte)│   │
  │ │   Statistics: min="Austin", max="Seattle", null_count=0 │   │
  │ ├─────────────────────────────────────────────────────────┤   │
  │ │ Column Chunk: "amount" (DOUBLE)                         │   │
  │ │   Pages: [byte-stream of doubles, snappy-compressed]    │   │
  │ │   Statistics: min=9.99, max=2499.99, null_count=145     │   │
  │ └─────────────────────────────────────────────────────────┘   │
  │                                                                │
  │ ROW GROUP 2 (rows 131,072 - 262,143):                         │
  │   ... (same structure)                                         │
  │                                                                │
  │ FILE FOOTER (metadata):                                        │
  │   Schema: {order_id:INT64, city:BYTE_ARRAY, amount:DOUBLE,...} │
  │   Row group 1: byte_offset=4, row_count=131072                 │
  │     Column "order_id": byte_offset=4, min=1001, max=132072    │
  │     Column "city": byte_offset=2456123, min="Austin",...      │
  │     Column "amount": byte_offset=3891234, min=9.99, max=2499  │
  │   Row group 2: byte_offset=18234567, row_count=131072          │
  │     ...                                                        │
  │ Footer length (4 bytes)                                        │
  │ Magic: PAR1 (4 bytes)                                          │
  └────────────────────────────────────────────────────────────────┘

HOW PREDICATE PUSHDOWN WORKS:

  Query: SELECT SUM(amount) FROM orders WHERE city='Seattle' AND date='2024-01-15'
  
  Step 1: Open Parquet file → read last 4 bytes (magic) → read footer length
  Step 2: Read footer metadata (tiny! maybe 100KB for a 10GB file)
  Step 3: For each row group, check column statistics:
  
  Row Group 1: city column stats: min="Austin", max="Seattle"
    → "Seattle" is in range [Austin, Seattle] → might match → READ
  Row Group 2: city column stats: min="NYC", max="Portland"  
    → "Seattle" not in [NYC, Portland] → SKIP ENTIRE ROW GROUP
  Row Group 3: date column stats: min="2024-01-01", max="2024-01-14"
    → "2024-01-15" not in range → SKIP ENTIRE ROW GROUP
  Row Group 4: city and date stats match → READ
  
  Result: read maybe 2 out of 10 row groups → 80% less I/O

BLOOM FILTERS (Parquet 2.0+):

  High-cardinality columns (UUIDs, user IDs): min/max statistics are nearly useless
  (every row group has min="00000..." max="ffffffff..." → no filtering)
  
  Bloom filter per column chunk: compact probabilistic structure
  → "does value X exist in this column chunk?"
  → False positives possible (says "maybe"); no false negatives (says "no" = certain)
  → 99% of non-matching row groups eliminated with a few KB of bloom filter data

PARTITIONING (Hive-style on S3):

  Partition by date and country:
  s3://bucket/orders/
    date=2024-01-14/country=US/part-001.parquet
    date=2024-01-14/country=EU/part-002.parquet
    date=2024-01-15/country=US/part-003.parquet
    date=2024-01-15/country=EU/part-004.parquet
  
  Query: WHERE date='2024-01-15' AND country='US'
  → Only read: s3://bucket/orders/date=2024-01-15/country=US/
  → Skip: 3 other partitions entirely (never even open those files)
  
  Partition pruning happens at the file listing level, before any file is opened
  Predicate pushdown happens inside files (row group level)
  Column pruning happens inside row groups (column chunk level)
  
  3 levels of pruning: partition → row group → column

COMPRESSION PERFORMANCE (real-world):

  100M order records (5 columns: id, customer, amount, city, status):
  
  Format           │ Size     │ Query time (SUM amount WHERE city='Seattle')
  ─────────────────┼──────────┼─────────────────────────────────────────────
  CSV (no compress)│ 8.0 GB   │ 120s (read all 8GB, parse all rows)
  CSV (gzip)       │ 1.2 GB   │ 45s (decompress then parse all rows)
  Parquet (snappy) │ 0.9 GB   │ 3s (2 cols, predicate pushdown, vectorized)
  Parquet (zstd)   │ 0.6 GB   │ 3.5s (better compression, slightly slower decompress)
  Parquet+partition│ 0.9 GB   │ 0.3s (if partitioned by city: read 1/5 of files)
```

---

### ❓ Why Does This Exist (Why Before What)

Google published the Dremel paper (2010) describing how they stored and queried web-scale structured data with a columnar format. Twitter and Cloudera implemented Apache Parquet as an open-source version of the Dremel file format. The problem: text formats (CSV, JSON) at petabyte scale were becoming the I/O and compute bottleneck for analytics. Parquet solved: (1) 10x storage reduction → lower S3 costs; (2) 50x query speedup → lower Athena/Spark costs; (3) nested schemas → complex event data in one file without joins.

---

### 🧠 Mental Model / Analogy

> **A phone book vs a set of specialized indexes**: a phone book (row storage / CSV) stores each person's name, address, and number together on one page — great for looking up one person, terrible for finding "everyone in Seattle" (must read all pages). Parquet is like having three separate binders: one for all names, one for all cities, one for all phone numbers — with an index card (file footer) at the front saying "Seattle appears in pages 3-7 and 22-31." To find everyone in Seattle: check the index card → read only pages 3-7 and 22-31 from the city binder → get their row positions → read only those rows from the name and phone binders.

---

### ⚙️ How It Works (Mechanism)

```
SPARK + PARQUET OPTIMIZATIONS:

  spark.read.parquet("s3://bucket/orders/")
      │
      ├── Partition discovery: LIST S3 prefix → partition directories
      ├── Partition pruning: WHERE date='2024-01-15' → filter directories
      ├── Read footer metadata from matching files
      ├── Row group pruning: statistics-based skip
      ├── Column pruning: SELECT → read only needed column chunks
      ├── Page-level filtering: dictionary pages for enum-like columns
      └── Vectorized scan: SIMD operations on column batches

SCHEMA EVOLUTION IN PARQUET:

  File v1 schema: {id: INT64, amount: DOUBLE}
  File v2 schema: {id: INT64, amount: DOUBLE, currency: STRING}
  
  Spark reads both files together (schema merging):
  spark.read.option("mergeSchema","true").parquet("s3://bucket/orders/")
  → Merged schema: {id: INT64, amount: DOUBLE, currency: STRING}
  → v1 files: currency column = null (not present in old files)
  → v2 files: all three columns present
  
  Delta Lake: handles schema evolution explicitly (ALTER TABLE ADD COLUMN)
  without needing mergeSchema (more controlled, explicit)
```

---

### 🔄 How It Connects (Mini-Map)

```
Data lake needs efficient columnar storage for analytics
        │
        ▼
Parquet ◄── (you are here)
(columnar; row groups; statistics; predicate pushdown; snappy/zstd)
        │
        ├── Columnar vs Row Storage: foundational principle
        ├── ORC: alternative columnar format (Hive ecosystem)
        ├── Delta Lake: ACID transaction layer built on Parquet
        ├── Apache Iceberg: alternative to Delta Lake on Parquet
        ├── Spark / Athena / Trino: query engines that read Parquet natively
        └── Apache Arrow: in-memory columnar format; Parquet ↔ Arrow conversion
```

---

### 💻 Code Example

```python
# PySpark: optimized Parquet reads with partition pruning + column pruning

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum

spark = SparkSession.builder \
    .appName("ParquetDemo") \
    .config("spark.sql.parquet.filterPushdown", "true") \    # enable predicate pushdown
    .config("spark.sql.parquet.mergeSchema", "false") \      # disable for performance
    .getOrCreate()

# Read partitioned Parquet dataset
# s3://bucket/orders/date=*/country=*/part-*.parquet
df = spark.read.parquet("s3://bucket/orders/")

# 1. PARTITION PRUNING: only reads date=2024-01-15 + country=US directories
# 2. COLUMN PRUNING: only reads amount + status column chunks (not order_id, customer_id)
# 3. PREDICATE PUSHDOWN: skips row groups where status statistics exclude 'COMPLETED'
result = df.filter(
    (col("date") == "2024-01-15") &      # partition pruning
    (col("country") == "US") &           # partition pruning
    (col("status") == "COMPLETED")       # predicate pushdown (row group statistics)
).select(
    "customer_id",                       # column pruning
    "amount"                             # column pruning (skip other columns)
).groupBy("customer_id") \
 .agg(spark_sum("amount").alias("total_revenue"))

result.write.mode("overwrite").parquet("s3://bucket/analytics/daily_revenue/date=2024-01-15/")

# Check Parquet file schema and metadata
import pyarrow.parquet as pq
pf = pq.ParquetFile("local_sample.parquet")
print(pf.schema_arrow)        # print schema
print(pf.metadata)            # row groups, columns, statistics
print(pf.metadata.row_group(0).column(2).statistics)  # min/max for column 2
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Parquet is write-once, cannot be updated | Parquet files themselves are immutable. But Delta Lake / Iceberg / Hudi add an ACID layer: updates write new Parquet files + a transaction log; old files are marked as deleted. The abstraction is a mutable table; the physical layer is immutable Parquet files. |
| Larger row groups are always better | Larger row groups (256MB+) give better statistics and compression. But they increase memory requirements during write (must buffer 256MB per column in memory). They also mean coarser granularity for row group skipping. The sweet spot is 128MB–512MB depending on memory and query patterns. |
| Parquet files are directly readable with a text editor | Parquet is binary. The first 4 bytes are the ASCII magic `PAR1`. After that, it's binary-encoded data. Use `parquet-tools show --head 100 file.parquet` or `pq.read_table("file.parquet").to_pandas().head()` to read Parquet data. |

---

### 🔥 Pitfalls in Production

```
PITFALL: small files problem (too many small Parquet files)

  # Streaming Spark job: writes one file per micro-batch per partition
  # 5-minute micro-batch × 100 Hive partitions × 6 months = 525,600 files
  # Athena: scans metadata for ALL 525K files before reading any data
  # S3 LIST requests: expensive and slow at this scale
  
  # FIX: use Delta Lake OPTIMIZE command (merges small files):
  # delta_table.optimize().executeCompaction()
  # or schedule periodic Spark compaction job:
  df = spark.read.parquet("s3://bucket/orders/date=2024-01-15/")
  df.coalesce(10).write.mode("overwrite").parquet("s3://bucket/orders/date=2024-01-15/")
  
  # RULE: target 128MB–1GB per Parquet file
  # RULE: if streaming, batch writes or use Delta Lake

PITFALL: wrong compression codec for your workload

  # Snappy: fast compression + decompression; moderate ratio (2-4x)
  # → Best for: interactive queries where decompression speed matters
  # → Default in Spark, Parquet-cpp
  
  # GZIP: slow compression; high ratio (4-8x)
  # → Best for: archival storage, cold data, S3 costs matter most
  # → Bad for: interactive queries (decompression is slow)
  
  # ZSTD: good compression ratio (3-5x) + fast decompression
  # → Best for: most production workloads (Parquet default since version 2.0)
  # → Recommended default
  
  spark.conf.set("spark.sql.parquet.compression.codec", "zstd")
```

---

### 🔗 Related Keywords

- `Columnar vs Row Storage` — the architectural principle behind Parquet
- `ORC` — alternative columnar format; better integrated with Hive/ACID
- `Binary Formats (Avro, Parquet, ORC, Protobuf)` — Parquet in context
- `Delta Lake` — ACID + schema evolution + time travel on top of Parquet
- `Apache Arrow` — in-memory columnar format; Parquet files are often read into Arrow for in-memory processing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PARQUET KEY FACTS:                                       │
│ • Columnar; row groups (128MB) → column chunks → pages  │
│ • Footer: schema + row group statistics (min/max/null)  │
│ • 3-level pruning: partition → row group → column       │
│ • Compression: snappy (fast), zstd (balanced), gzip     │
│ • Encoding: dict, RLE, delta → 10-50x vs CSV            │
│ • Schema evolution: mergeSchema=true or Delta/Iceberg   │
├──────────────────────────────────────────────────────────┤
│ Rule: target 128MB-1GB files; use zstd; partition by    │
│       high-cardinality query filters (date, region)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Parquet predicate pushdown works at the row group level using min/max statistics. For a column with high cardinality and random distribution (e.g., `user_id` is a UUID — min/max are "000..." and "fff..."), min/max statistics are useless for skipping. Bloom filters solve this for equality predicates. Explain exactly how a Parquet bloom filter works: what is it stored, when is it written, how does the reader use it, and what is the false positive rate trade-off?

**Q2.** Z-ordering (data skipping with multi-dimensional clustering) is a technique used in Delta Lake's OPTIMIZE ZORDER BY command. It clusters Parquet files by multiple columns simultaneously so that queries filtering on any of those columns can skip more files. How does this differ from Hive-style partitioning? In what scenarios is ZORDER better than partitioning? What are the costs of ZORDER (write amplification, rewrite time)?
