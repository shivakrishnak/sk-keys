---
layout: default
title: "Hudi"
parent: "Data Fundamentals"
nav_order: 507
permalink: /data-fundamentals/hudi/
number: "507"
category: Data Fundamentals
difficulty: ★★★
depends_on: Parquet, Delta Lake, Apache Iceberg, Data Lake, Data Lakehouse
used_by: Data Lakehouse, Change Data Capture (CDC), Apache Spark, Apache Flink
tags:
  - data
  - lakehouse
  - storage
  - streaming
  - deep-dive
---

# 507 — Hudi

`#data` `#lakehouse` `#storage` `#streaming` `#deep-dive`

⚡ TL;DR — Apache Hudi (Hadoop Upserts Deletes and Incrementals) is an open table format optimised for streaming upserts and incremental data processing on data lakes, with copy-on-write and merge-on-read storage types.

| #507 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Parquet, Delta Lake, Apache Iceberg, Data Lake, Data Lakehouse | |
| **Used by:** | Data Lakehouse, Change Data Capture (CDC), Apache Spark, Apache Flink | |

---

### 📘 Textbook Definition

**Apache Hudi** (Hadoop Upserts, Deletes and Incrementals) is an open-source data lakehouse storage layer originally developed at Uber. It provides upsert/delete capabilities on data lake files in object storage (S3, ADLS, GCS) via two storage table types: **Copy-on-Write (CoW)** — rewrites Parquet files on every update ensuring clean reads, and **Merge-on-Read (MoR)** — appends delta log files for fast writes, merging with base files at read time. Hudi's core differentiator is its **timeline** — an ordered log of all table operations — enabling incremental pulls, CDC integration, and near-real-time data ingestion pipelines.

---

### 🟢 Simple Definition (Easy)

Hudi is like a transaction log for a data lake — it tracks every insert, update, and delete as events on a timeline, enabling fast streaming ingestion, efficient GDPR deletes, and incremental data pulls.

---

### 🔵 Simple Definition (Elaborated)

Traditional data lakes are append-only: you can add files but updating or deleting specific rows is painfully expensive (full rewrite). Hudi was built at Uber to solve the high-volume streaming upsert problem — millions of records per hour where each ride event needed to update the ride's status. Hudi's MOR approach: write tiny delta files immediately (fast), merge with base Parquet files lazily during compaction (clean reads). Its timeline makes incremental reads trivial: "give me all changes since checkpoint X" instead of reading the entire table — critical for CDC pipelines feeding downstream consumers.

---

### 🔩 First Principles Explanation

**Two table types:**

```
Copy-on-Write (CoW):
  Write: rewrite all affected Parquet files for every commit
  Read:  fast — always reading clean Parquet files
  Use:   read-heavy workloads, BI dashboards, latency-sensitive reads
  Trade-off: slow writes (full file rewrites)

Merge-on-Read (MoR):
  Write: append AVRO delta log files instantly (no rewrite)
  Read:  merge base Parquet + delta logs
          → reads need to merge on-the-fly (slightly slower)
          → Compaction moves deltas into base files periodically
  Use:   write-heavy streaming ingestion, near-real-time pipelines
  Trade-off: read latency until compaction runs
```

**Hudi's Timeline:**

```
Timeline (stored in .hoodie/ directory):
  20260502T100000.commit  ← successful batch commit
  20260502T100500.deltacommit ← MoR streaming write
  20260502T101000.compaction  ← MoR compaction
  20260502T101500.rollback    ← failed commit rolled back
  20260502T102000.clean       ← old file versions cleaned up

Every action recorded as REQUESTED → INFLIGHT → COMPLETED
Atomic: only fully successful commits reflected in reads
```

**Incremental query (the key differentiator):**

```python
# Pull only records that changed since a specific timestamp
# No full table scan needed — uses timeline to find changed files
hudi_incremental_opts = {
    "hoodie.datasource.query.type": "incremental",
    "hoodie.datasource.read.begin.instanttime": "20260501000000",
    "hoodie.datasource.read.end.instanttime":   "20260502000000",
}
df = spark.read.format("hudi") \
    .options(**hudi_incremental_opts) \
    .load("s3://bucket/rides_table")
# Returns ONLY records committed in the specified time range
# Perfect for feeding Kafka, downstream tables, ML features
```

**CDC from databases to Hudi:**

```
MySQL / PostgreSQL (Debezium CDC)
    ↓ Kafka topic (change events)
    ↓ Spark Streaming / Flink
    ↓ Hudi MoR upsert (key = primary key)
    ↓ Object storage (S3)
    → Hudi deduplicates, handles out-of-order events
    → Near-real-time database replica in data lake
```

**Record Key + Partition:**

```python
# Hudi requires:
# 1. Record key: uniquely identifies a row for upserts
# 2. Partition path: physical partitioning

hudi_write_opts = {
    "hoodie.table.name": "rides",
    "hoodie.datasource.write.recordkey.field": "ride_id",
    "hoodie.datasource.write.partitionpath.field": "city,date",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.table.type": "MERGE_ON_READ",
}
df.write.format("hudi").options(**hudi_write_opts) \
    .mode("append").save("s3://bucket/rides")
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Hudi (append-only data lake):
- Uber processes millions of ride events/hour. Each event updates the ride status multiple times. Storing all raw events means massive duplication.
- GDPR delete (erase user data) requires rewriting all partitions containing that user: days of compute.

WITH Hudi:
→ Upsert with ride_id as key: latest state automatically merged, deduplication free.
→ Delete: mark records deleted via delete logs, compaction removes physical data.
→ Incremental reads: downstream pipelines receive only changed records since last checkpoint.

---

### 🧠 Mental Model / Analogy

> Hudi is like a database WAL (Write-Ahead Log) wrapped around a data lake. Traditional data lakes are like an append-only ledger: you can add pages but not erase or correct entries. Hudi adds a timeline (like a bank's transaction journal) plus two strategies: either correct the notebook immediately (CoW — clean but slow) or note corrections on a sticky note (MoR — fast, clean up later during compaction). The timeline lets any reader jump to "state at time T" or ask "what changed between T1 and T2?"

---

### ⚙️ How It Works (Mechanism)

**Hudi vs Iceberg vs Delta comparison:**

| Feature | Hudi | Iceberg | Delta Lake |
|---|---|---|---|
| Streaming upserts | ★★★ Best | ★★☆ Good | ★★☆ Good |
| CDC / incremental reads | ★★★ Native | ★★☆ Snapshot diff | ★★☆ CDF |
| Hidden partitioning | ❌ No | ✅ Yes | ❌ No |
| Engine agnostic | ★★☆ Mostly | ★★★ Best | ★★☆ Mostly |
| Concurrency control | ★★☆ OCC | ★★★ OCC | ★★☆ OCC |
| File format | Parquet+Avro | Parquet/ORC/Avro | Parquet |

**Compaction strategy:**

```python
# MoR tables need periodic compaction (delta + base → fresh base)
# Synchronous compaction: inline during commit (adds write latency)
# Asynchronous compaction: separate compaction job (better throughput)
hudi_opts = {
    "hoodie.compact.inline": "false",  # async compaction
    "hoodie.compact.inline.max.delta.commits": "5",  # trigger after 5 deltas
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Streaming data (Kafka, CDC events)
        ↓ upserted via
Apache Hudi ← you are here
  (timeline + CoW/MoR + incremental reads)
        ↓ stored on
Object Storage (S3 / ADLS / GCS) as Parquet + Avro deltas
        ↓ queried by
Spark | Presto | Trino | Hive
        ↓ competes with
Delta Lake | Apache Iceberg
```

---

### 💻 Code Example

```python
# Full upsert pipeline: CDC → Hudi
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.serializer",
            "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()

# Read CDC change stream
cdc_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "mysql.rides.changes") \
    .load()

# Parse and upsert to Hudi
query = cdc_df.writeStream.format("hudi") \
    .option("hoodie.table.name", "rides") \
    .option("hoodie.datasource.write.recordkey.field", "ride_id") \
    .option("hoodie.datasource.write.operation", "upsert") \
    .option("hoodie.datasource.write.table.type", "MERGE_ON_READ") \
    .option("checkpointLocation", "s3://bucket/checkpoints/rides") \
    .start("s3://bucket/rides")
```

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Streaming upserts + incremental reads     │
│              │ on data lake files via CoW/MoR + timeline.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ CDC ingestion, high-volume upsert,        │
│              │ near-real-time data lake, GDPR deletes.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hudi: the streaming-native table format  │
│              │ — born for upserts, built for CDC."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Apache Iceberg → Delta Lake → CDC → ETL   │
└──────────────────────────────────────────────────────────┘
```

