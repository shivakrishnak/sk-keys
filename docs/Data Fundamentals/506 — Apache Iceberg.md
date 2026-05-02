---
layout: default
title: "Apache Iceberg"
parent: "Data Fundamentals"
nav_order: 506
permalink: /data-fundamentals/apache-iceberg/
number: "506"
category: Data Fundamentals
difficulty: ★★★
depends_on: Parquet, Delta Lake, Data Lake, Data Lakehouse, Columnar vs Row Storage
used_by: Data Lakehouse, Data Catalog, Data Lineage, Apache Spark, Apache Flink
tags:
  - data
  - lakehouse
  - storage
  - deep-dive
---

# 506 — Apache Iceberg

`#data` `#lakehouse` `#storage` `#deep-dive`

⚡ TL;DR — An open table format for large analytic datasets that adds ACID transactions, schema evolution, time travel, and hidden partitioning on top of object storage (S3/ADLS/GCS).

| #506 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Parquet, Delta Lake, Data Lake, Data Lakehouse, Columnar vs Row Storage | |
| **Used by:** | Data Lakehouse, Data Catalog, Data Lineage, Apache Spark, Apache Flink | |

---

### 📘 Textbook Definition

**Apache Iceberg** is an open-source table format specification designed for huge analytic tables stored in object storage. It defines a metadata layer above Parquet/ORC/Avro files that provides: ACID transaction guarantees, full schema evolution without rewrites, hidden partitioning (separating physical layout from query logic), snapshot-based time travel, partition and column stats-based query pruning, and row-level deletes/updates. Iceberg is engine-agnostic — Spark, Flink, Trino, Presto, Hive, and Dremio all read/write Iceberg tables via the same open specification.

### 🟢 Simple Definition (Easy)

Iceberg is a smart table format for a data lake — it adds a metadata "brain" on top of raw Parquet files that enables SQL updates/deletes, time travel queries, safe concurrent writes, and schema changes without moving any data.

### 🔵 Simple Definition (Elaborated)

Traditional data lakes store raw Parquet files in S3. This gives you cheap storage but no transactions, no way to UPDATE or DELETE rows, and painful partition management. Apache Iceberg adds an open metadata layer — a set of JSON manifest files — that tracks exactly which files belong to which snapshot of the table. This enables: reading the table as it looked 7 days ago (time travel), multiple writers without corruption (optimistic concurrency), deleting specific rows without rewriting everything (position-based row deletes), and changing column types or adding columns without any data migration.

### 🔩 First Principles Explanation

**The problem with raw data lakes:**

```
Traditional data lake:
  S3: s3://bucket/events/year=2026/month=05/day=02/file1.parquet
                                                  /file2.parquet
  Issues:
  1. No transactions: two writers → corrupted partial writes
  2. No deletes: GDPR delete requires full partition rewrite
  3. Schema changes: rename a column → all downstream queries break
  4. No stats: query engine reads every file to check partition
  5. Partition discovery: MSCK REPAIR TABLE is slow and unreliable
```

**Iceberg metadata architecture:**

```
Table State:
  Catalog (Hive Metastore / Glue / REST / Nessie)
    ↓ points to
  Metadata File (metadata/v42.json)
    ↓ contains
  Snapshot List → Snapshot #42 (current), #41, #40...
    ↓ snapshot contains
  Manifest List (snap-42-manifest-list.avro)
    ↓ lists
  Manifest Files (manifest-xyz.avro)
    ↓ each manifest lists
  Data Files (s3://bucket/data/file1.parquet, file2.parquet...)
    ↓ with per-file stats
  Column-level min/max, null counts, row counts
```

**Key features:**

**1. Hidden Partitioning:**
```sql
-- Query engine uses transform functions, not raw column values
CREATE TABLE events (event_time TIMESTAMP, event_type STRING)
PARTITIONED BY (bucket(10, event_type), days(event_time));
-- Physical files partitioned by bucket + day,
-- but queries don't need to know partition layout:
SELECT * FROM events WHERE event_time = TIMESTAMP '2026-05-02';
-- Iceberg automatically prunes to relevant partitions via metadata
```

**2. Time Travel:**
```sql
-- Read table as of a specific snapshot
SELECT * FROM events TIMESTAMP AS OF '2026-04-01';
-- or by snapshot ID
SELECT * FROM events VERSION AS OF 42;
```

**3. Schema Evolution (safe):**
```sql
ALTER TABLE events ADD COLUMN user_id BIGINT; -- O(1), metadata only
ALTER TABLE events RENAME COLUMN event_type TO type; -- no rewrite
-- Old files without the column → new column returns NULL
-- New files with column → reads correctly
-- Engine merges transparently
```

**4. Row-Level Deletes:**
```
GDPR delete user_id = 12345:
  Option 1: Copy-on-Write (COW) — rewrite all affected files
  Option 2: Merge-on-Read (MOR) — write delete file listing row positions
  → Read path merges data files + delete files transparently
```

**5. ACID Optimistic Concurrency:**
```
Writer A: reads snapshot 42, decides to write new data files
Writer B: reads snapshot 42, also decides to write data files
Both attempt to commit new metadata pointing to snapshot 43:
  → First writer succeeds
  → Second writer detects conflict, retries against snapshot 43
  → Serializability via snapshot CAS (Compare-And-Swap) on metadata
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Iceberg (raw data lakes):
- GDPR delete of one user: rewrite all partitions containing that user → hours.
- Two Spark jobs writing simultaneously → corrupt empty files.
- Partition column renamed → all 50 downstream jobs break.

WITH Iceberg:
→ Concurrent writes without corruption via snapshot isolation.
→ Row deletes via delete files, not full rewrites.
→ Schema evolution without breaking downstream consumers.

### 🧠 Mental Model / Analogy

> Iceberg is like a database's transaction log and catalog system, but for files in S3. The raw Parquet files are the data pages of a database. The Iceberg metadata files are the B-tree index, the transaction log, and the system catalog combined. Just as a database tracks which pages belong to which table version (via WAL), Iceberg tracks which files belong to which snapshot. The database can roll back — so can Iceberg (via snapshot rollback). The database enforces ACID — so does Iceberg (for file-level operations).

### ⚙️ How It Works (Mechanism)

**Compaction (maintenance):**

```sql
-- Small files accumulate from streaming writes → compaction needed
CALL catalog.system.rewrite_data_files(
  table => 'db.events',
  strategy => 'binpack',
  options => MAP('target-file-size-bytes', '536870912') -- 512 MB
);

-- Expire old snapshots (free up storage)
CALL catalog.system.expire_snapshots(
  table => 'db.events',
  older_than => TIMESTAMP '2026-04-01 00:00:00',
  retain_last => 3
);
```

**Iceberg vs Delta Lake vs Hudi:**

| Feature | Iceberg | Delta Lake | Hudi |
|---|---|---|---|
| Open spec | ✅ Yes | Mostly (open sourced) | ✅ Yes |
| Spark integration | ✅ Native | ✅ Native | ✅ Native |
| Time travel | ✅ Snapshots | ✅ Version history | ✅ Timeline |
| Row deletes | ✅ COW+MOR | ✅ COW | ✅ COW+MOR |
| Incremental reads | ✅ Snapshot diff | ✅ CDF | ✅ Incremental queries |
| Hidden partitioning | ✅ Yes | ❌ No | ❌ No |
| Catalog agnostic | ✅ Yes | Partial | Partial |

### 🔄 How It Connects (Mini-Map)

```
Parquet / ORC / Avro (physical data files)
        ↓ managed by
Apache Iceberg ← you are here
  (table format: metadata + snapshots + stats)
        ↓ queried by
Apache Spark | Flink | Trino | Presto | Hive
        ↓ stored in
S3 / ADLS / GCS (object storage)
        ↓ registered in
Hive Metastore | AWS Glue | Nessie | REST Catalog
        ↓ competes with
Delta Lake | Apache Hudi
```

### 💻 Code Example

Example 1 — Create and query an Iceberg table in Spark:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.local",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.local.type", "hadoop") \
    .config("spark.sql.catalog.local.warehouse", "s3://my-bucket/warehouse") \
    .getOrCreate()

# Create Iceberg table
spark.sql("""
  CREATE TABLE local.db.events (
    event_id BIGINT,
    event_time TIMESTAMP,
    user_id BIGINT,
    event_type STRING
  ) USING ICEBERG
  PARTITIONED BY (days(event_time), bucket(16, user_id))
""")

# Append data
df = spark.createDataFrame([...])
df.writeTo("local.db.events").append()

# Time travel
spark.sql("""
  SELECT * FROM local.db.events
  TIMESTAMP AS OF '2026-04-01 00:00:00'
""")
```

Example 2 — Row-level delete (GDPR):

```python
# Delete all events for a specific user (without full partition rewrite)
spark.sql("""
  DELETE FROM local.db.events WHERE user_id = 12345
""")
# With MergeOnRead: writes a delete file (fast)
# With CopyOnWrite: rewrites affected files (safe, slower)
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Iceberg stores data in a special format | Iceberg is a metadata layer; data is still in standard Parquet/ORC/Avro files. Any engine that reads Parquet can read raw Iceberg data files. |
| Iceberg requires Spark | Iceberg is engine-agnostic. Trino, Flink, Presto, Dremio, and many others natively support it. |
| Iceberg replaces a data warehouse | Iceberg is a table format for a data lakehouse. It brings warehouse-like features to a data lake but doesn't replace operational databases. |
| Time travel queries are expensive | Time travel reads the same data files; only the metadata pointer changes. It's as fast as reading the current table (no extra computation). |

### 🔥 Pitfalls in Production

**1. Not Running Table Maintenance → Storage Explosion**
```python
# BAD: MergeOnRead deletes accumulate thousands of delete files
# → read amplification (each read merges data + delete files)
# → eventually slower than rewriting

# GOOD: Schedule regular compaction + snapshot expiry
spark.sql("""
  CALL local.system.rewrite_data_files('db.events')
""")
spark.sql("""
  CALL local.system.expire_snapshots(
    'db.events', TIMESTAMP '2026-04-01', 5)
""")
```

**2. Wrong Partition Strategy → Small Files**
```python
# BAD: Partition by raw timestamp → one file per minute of data
PARTITIONED BY (timestamp)  # ← too granular, millions of files

# GOOD: Use implicit transform
PARTITIONED BY (hours(event_time))  # aggregate to hourly partitions
```

### 🔗 Related Keywords

- `Delta Lake` — competing open table format, primarily in Azure/Databricks ecosystem.
- `Hudi` — third major open table format; originated at Uber for streaming upserts.
- `Parquet` — the default columnar file format for Iceberg data files.
- `Data Lakehouse` — the architecture combining lake storage + warehouse features via Iceberg/Delta/Hudi.
- `Schema Registry` — manages schemas for Avro/Protobuf; Iceberg has built-in schema evolution.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Open table format: ACID + time travel +   │
│              │ schema evolution on top of object storage.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Data lakehouse needing deletes, upserts,  │
│              │ GDPR compliance, safe concurrent writes.  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Iceberg: turns S3 files into a proper    │
│              │ database table — with transactions."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hudi → Delta Lake → Data Lakehouse →      │
│              │ Schema Evolution                          │
└──────────────────────────────────────────────────────────┘
```

