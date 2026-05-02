---
layout: default
title: "Apache Iceberg"
parent: "Data Fundamentals"
nav_order: 506
permalink: /data-fundamentals/apache-iceberg/
number: "0506"
category: Data Fundamentals
difficulty: ★★★
depends_on: Parquet, Delta Lake, Data Lake, Apache Spark, ACID Transactions
used_by: Data Lakehouse, Data Mesh, Data Catalog
related: Delta Lake, Hudi, Data Lakehouse, Parquet, ORC
tags:
  - dataengineering
  - advanced
  - bigdata
  - database
  - distributed
---

# 506 — Apache Iceberg

⚡ TL;DR — Apache Iceberg is an open table format that adds ACID transactions, schema evolution, and time travel to data lakes with a design optimised for multi-engine access without a central coordinator.

| #506 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Parquet, Delta Lake, Data Lake, Apache Spark, ACID Transactions | |
| **Used by:** | Data Lakehouse, Data Mesh, Data Catalog | |
| **Related:** | Delta Lake, Hudi, Data Lakehouse, Parquet, ORC | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Netflix stores 500 petabytes of data across 100,000+ tables read
by Spark, Presto, Flink, and Trino concurrently. Delta Lake works
well for Spark but requires Databricks runtime for full ACID
support on non-Spark engines. Hive's metastore becomes a central
bottleneck — 100,000 partition renames during a schema change
require 100,000 metastore RPC calls, each taking 1–10 ms.
A table rename that should be atomic takes 17 minutes and
requires several Hive metastore boxes to prevent SPOF.

**THE BREAKING POINT:**
As data platforms scaled to petabytes spanning multiple query
engines (not all Spark), three problems collided: (1) no open
format offered truly atomic commits without a proprietary runtime,
(2) table metadata at petabyte scale required thousands of
metastore calls making planning O(partitions) instead of O(1),
and (3) concurrent writers across different engines created
race conditions with no conflict detection.

**THE INVENTION MOMENT:**
This is exactly why Apache Iceberg was created at Netflix in 2017.
Iceberg uses a snapshot-based metadata tree (not a linear log)
stored in the object store itself — no external metastore required.
Any engine that can read Iceberg's metadata format gets full ACID
semantics. Adding 100,000 partitions is one atomic metadata pointer
swap, not 100,000 metastore calls. Multi-engine concurrency is
handled via object store conditional `PUT`.

---

### 📘 Textbook Definition

**Apache Iceberg** is an open table format for analytic datasets
at petabyte scale, designed as an engine-agnostic layer on top of
file formats (Parquet, ORC, Avro) stored in any object store.
Iceberg provides: snapshot-based ACID transactions (each write
creates a new immutable snapshot); schema evolution (safely add,
rename, drop, reorder columns without rewriting data); partition
evolution (change partitioning scheme without rewriting data);
hidden partitioning (partition logic is in table metadata, not
embedded in file path); and time travel (read any past snapshot).
Iceberg metadata consists of a tree: table metadata JSON → manifest
list (one per snapshot) → manifest files (lists of data files
with per-file statistics) → Parquet/ORC/Avro data files. This
tree is stored entirely in the object store with no external
metadata service required.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Iceberg is a table format that makes any set of files on S3 behave
like a fully transactional database table, accessible by any engine.

**One analogy:**

> Imagine a library where instead of one card catalogue managed
> by one librarian, each book section has its own self-contained
> index card that describes all books in that section. To find
> any book, you just navigate the index cards. If the head
> librarian goes down, you can still read every book. Delta Lake
> has one central card catalogue (the transaction log). Iceberg
> has a tree of self-contained index cards stored with the books.

**One insight:**
Iceberg's design insight: the metadata format IS the transaction
system. There is no central coordinator; the metadata tree stored
in S3 is the source of truth. Concurrency control is achieved via
object store's atomic conditional PUT (CAS-like). Any engine that
implements Iceberg's metadata reader gets full ACID for free.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A table is a sequence of immutable snapshots; each snapshot
   lists the exact set of data files that constitute the table
   at that point.
2. Metadata is a tree (not a flat log) stored in the object store —
   no external service required to read or write a snapshot.
3. Schema and partitioning are decoupled from file paths —
   evolution doesn't require rewriting data files.

**DERIVED DESIGN:**
Given invariant 1: writes create a new snapshot. Atomic commit =
write new metadata JSON pointing to the new snapshot, then
atomically update the current metadata pointer. If the pointer
update fails, the new snapshot is invisible (orphaned files cleaned
by expiration).

Given invariant 2: the metadata tree:
- **Table metadata file** (JSON): schema, partition spec,
  current snapshot ID, list of all snapshot IDs + their manifest
  list paths, properties.
- **Manifest list** (Avro): one entry per manifest file,
  with partition-level statistics (min/max per partition field).
- **Manifest file** (Avro): one entry per data file with
  per-file statistics (min/max/null counts per column),
  file path, format, partition values.
- **Data files**: Parquet/ORC/Avro.

Query planning: read manifest list → prune manifests by
partition statistics → read only relevant manifests → get data
file list → prune by data file statistics → read data files.
Planning touches orders-of-magnitude fewer bytes than Hive
partition listing.

Given invariant 3: hidden partitioning means the partition
scheme is stored in metadata, not in the file path. Changing
from `partitioned by days(event_ts)` to
`partitioned by hours(event_ts)` is a metadata-only change.
Old files remain under their original day-based paths; new files
go to hour-based paths. Both are readable simultaneously.

**THE TRADE-OFFS:**
**Gain:** Engine-agnostic; self-contained metadata in object store;
O(log n) query planning instead of O(partitions); partition and
schema evolution without rewriting data; true ACID via object
store atomic PUT.
**Cost:** Metadata tree is more complex than a flat log (harder
to debug manually); Iceberg's multi-engine support requires each
engine to implement its Iceberg reader/writer (runtime-level
dependency); compaction and snapshot expiry must be managed
explicitly.

---

### 🧪 Thought Experiment

**SETUP:**
A data platform has a 1 PB table with 10 million Hive partitions.
Two teams want to use it: Team A uses Spark, Team B uses Trino.
The table's partition scheme (daily) needs to change to hourly
for a new use case without rebuilding the table.

**WITHOUT APACHE ICEBERG (Hive metastore):**
Listing 10 million partitions via Hive metastore takes 2 minutes
per query plan. Adding hourly partitions requires an `ALTER TABLE`
that touches the metastore 1 million times per day of data
(replacing 1 daily partition with 24 hourly ones). For 3 years
of history = 1,095 days × 24 = 26,280 new partitions × RPC calls.
Trino and Spark cannot both write without custom lock management.
The process takes 4 hours in a maintenance window with the table
offline.

**WITH APACHE ICEBERG:**
Partition evolution is a metadata-only operation:
`ALTER TABLE orders SET PARTITION SPEC (hours(event_ts))`
New data files land in hour-based paths. Old data stays in
day-based paths. Both are transparently readable by both Spark
and Trino from the same table. Planning uses manifest list
partition statistics — skipping 99% of manifests for a
single-hour query. Zero downtime. Zero data rewrite.

**THE INSIGHT:**
Decoupling partitioning logic from the physical file path
is a superpower at petabyte scale. It turns a multi-hour
maintenance operation into a metadata-only change that completes
in seconds. Most data systems conflate "how data is stored"
with "how data is indexed" — Iceberg separates them.

---

### 🧠 Mental Model / Analogy

> Think of Iceberg as a table of contents system for a petabyte
> library that has multiple simultaneously valid "editions."
> Each edition (snapshot) has its own table of contents (manifest
> list) pointing to chapter lists (manifest files) pointing to
> the actual pages (data files). A new edition doesn't reprint
> any pages — it just creates a new table of contents pointing
> to the same pages plus any new ones added. Any reader who
> knows the edition number can navigate to exactly those pages
> and no others.

- "Edition number" → snapshot ID
- "Table of contents" → manifest list
- "Chapter list" → manifest file (per partition/batch of files)
- "Pages" → Parquet/ORC data files
- "Publishing a new edition" → creating a new snapshot
- "Current edition pointer" → current snapshot pointer in metadata

**Where this analogy breaks down:** In Iceberg, "pages" (data
files) are never modified or deleted during normal operations —
only the edition pointer changes. "Old editions" accumulate until
snapshot expiration runs. And unlike a physical book,
different "readers" (engines) can hold different "editions"
simultaneously without conflict, as long as the edition they
reference hasn't been expired.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Apache Iceberg is a way to organise files in a data lake so that
multiple different tools (Spark, SQL tools, streaming engines)
can all read and write the same data safely. It adds the ability
to query data as it was at any past point in time, change the
table structure without breaking anything, and ensures that
concurrent operations don't corrupt each other.

**Level 2 — How to use it (junior developer):**
With Spark: configure Iceberg catalog, then use standard SQL or
DataFrame API. `CREATE TABLE catalog.db.orders USING iceberg`.
Read: `spark.table("catalog.db.orders")`. Time travel:
`spark.table("catalog.db.orders.snapshots")` to list snapshots;
`spark.read.option("snapshot-id", "12345").table(...)` to read
a specific snapshot. Schema changes: standard `ALTER TABLE ADD
COLUMN` — safe to run while readers are active. Maintenance:
run `CALL catalog.system.expire_snapshots(...)` and
`CALL catalog.system.rewrite_data_files(...)` periodically.

**Level 3 — How it works (mid-level engineer):**
Iceberg's atomic commit: the writer finishes writing all new
data files, creates a new manifest file listing them, creates a
new manifest list referencing the new manifest + existing manifests,
creates a new metadata JSON file pointing to the new snapshot,
then does an atomic metadata file swap: writes the new metadata
to a unique path and atomically updates the `metadata/version-hint.text`
(or the catalog's pointer). If a concurrent writer has also
updated the pointer between when the first writer read it and
when it tries to update → conflict → one writer retries.
File statistics in manifest files: `lower_bounds`, `upper_bounds`,
`null_value_counts`, `nan_value_counts` per column. Planning
engine reads manifest list → filters by partition bounds →
reads only relevant manifests → filters by column bounds →
builds task list. Planning touches KB/MB of metadata to plan
a read of TB of data.

**Level 4 — Why it was designed this way (senior/staff):**
Iceberg's manifest tree was designed to solve the specific
pathology of Hive at petabyte scale: Hive's metastore was a
relational database (MySQL/PostgreSQL) storing one row per
partition. At 1 billion partitions, metadata ops were O(N) SQL
queries. Iceberg's manifest tree is O(log N) — manifests themselves
are Avro files with per-file statistics, so a query planning pass
filters manifests using their statistics without reading the full
manifest content. This is the same B-tree principle applied to
file-level metadata rather than row-level data. The multi-engine
design stems from Netflix's specific requirement: Hive, Spark,
and Presto all accessing the same tables simultaneously. Delta
Lake's initial design tied atomicity to Spark's checkpoint
mechanism; Iceberg's metadata-in-object-store design was
explicitly engine-agnostic from day one. The Apache Software
Foundation decision to make Iceberg engine-neutral (no
Databricks runtime requirement) was political as much as
technical — data platform vendors wanted a standard not
controlled by a single vendor.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│          ICEBERG METADATA TREE                       │
│                                                      │
│  catalog:                                            │
│    orders → metadata/v5.metadata.json                │
│                    ↓                                 │
│  v5.metadata.json (table metadata)                   │
│    schema: {id, amount, region, event_ts}            │
│    partition-spec: hours(event_ts)                   │
│    current-snapshot-id: 8541                         │
│    snapshots: [7230, 8100, 8541]                     │
│                    ↓                                 │
│  snap-8541.avro (manifest list)                      │
│    │── manifest-a.avro [region min=EU max=US]        │
│    └── manifest-b.avro [region min=EU max=EU]        │
│                    ↓                                 │
│  manifest-a.avro  (manifest file)                    │
│    │── part-0001.parquet                             │
│    │     stats: {region: min=EU, max=US, rows: 50K}  │
│    └── part-0002.parquet                             │
│          stats: {region: min=US, max=US, rows: 45K}  │
└──────────────────────────────────────────────────────┘
```

**Query planning (predicate: `region = 'EU'`):**
```
1. Read v5.metadata.json → current snapshot = 8541
2. Read snap-8541 manifest list:
   manifest-a: region [EU, US] → may contain EU → include
   manifest-b: region [EU, EU] → all EU → include
3. Read manifest-a:
   part-0001 region [EU,US] → may match → include
   part-0002 region [US,US] → no EU → SKIP
4. Read manifest-b (all EU by definition → all included)
5. Read part-0001 + manifest-b's files only
   (skipped part-0002 entirely)
```

---

### 💻 Code Example

**Example 1 — Configure and use Iceberg with Spark:**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
  .config("spark.sql.extensions",
    "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
  .config("spark.sql.catalog.my_catalog",
    "org.apache.iceberg.spark.SparkCatalog") \
  .config("spark.sql.catalog.my_catalog.type", "hadoop") \
  .config("spark.sql.catalog.my_catalog.warehouse",
    "s3://my-bucket/warehouse/") \
  .getOrCreate()

# Create table
spark.sql("""
  CREATE TABLE my_catalog.db.orders (
    order_id BIGINT,
    amount DOUBLE,
    region STRING,
    event_ts TIMESTAMP
  ) USING iceberg
  PARTITIONED BY (days(event_ts))
""")

# Insert data
spark.sql("""
  INSERT INTO my_catalog.db.orders VALUES
  (1001, 99.99, 'EU', TIMESTAMP '2024-01-15 10:00:00')
""")
```

**Example 2 — Time travel:**
```python
# List all snapshots
spark.sql("""
  SELECT snapshot_id, committed_at, operation, summary
  FROM my_catalog.db.orders.snapshots
""").show()

# Read as of specific snapshot
df = spark.read \
  .option("snapshot-id", "8541362975585996088") \
  .table("my_catalog.db.orders")

# Read as of timestamp
df2 = spark.read \
  .option("as-of-timestamp",
    str(int(datetime(2024,1,15).timestamp() * 1000))) \
  .table("my_catalog.db.orders")
```

**Example 3 — Schema evolution (safe, no rewrite):**
```python
# Add column — safe even with active readers
spark.sql("""
  ALTER TABLE my_catalog.db.orders
  ADD COLUMN discount DOUBLE AFTER amount
""")
# Old files don't have 'discount' — returns NULL for old records
# New files include 'discount' column
# Both readable simultaneously without any data rewrite
```

**Example 4 — Partition evolution:**
```python
# Change partitioning from days to hours — metadata only
spark.sql("""
  ALTER TABLE my_catalog.db.orders
  REPLACE PARTITION FIELD days(event_ts)
  WITH hours(event_ts)
""")
# Old files stay in day-based paths
# New files go to hour-based paths
# Reads transparently combine both
```

**Example 5 — Maintenance:**
```python
# Expire old snapshots (free up storage after retention period)
spark.sql("""
  CALL my_catalog.system.expire_snapshots(
    table => 'db.orders',
    older_than => TIMESTAMP '2024-01-01 00:00:00'
  )
""")

# Compact small files
spark.sql("""
  CALL my_catalog.system.rewrite_data_files('db.orders')
""")
```

---

### ⚖️ Comparison Table

| Feature | Apache Iceberg | Delta Lake | Apache Hudi |
|---|---|---|---|
| **Metadata storage** | Object store (self-contained) | Object store (`_delta_log`) | Object store (timeline) |
| **Multi-engine** | Spark, Flink, Trino, Presto, Athena | Spark primary; others limited | Spark, Flink |
| **Partition evolution** | Yes (no data rewrite) | No (external tooling needed) | No |
| **Schema evolution** | Full (add/rename/drop/reorder) | Add/rename | Add/rename |
| **Compaction** | `rewrite_data_files` | `OPTIMIZE` | Rolling compaction |
| **Upsert model** | Copy-on-Write / Merge-on-Read | Copy-on-Write | CoW or MoR |
| **Governance** | Apache (neutral) | Delta.io / Databricks | Apache |
| **Best for** | Multi-engine open platform | Databricks workloads | Streaming upserts |

**How to choose:** Iceberg for multi-engine open platforms where
engine neutrality is a hard requirement (Trino + Spark + Flink
on same tables). Delta Lake for Databricks-primary workloads
where the Databricks runtime feature set (DeltaEngine, Unity
Catalog) is available. Hudi for high-frequency streaming upserts.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Iceberg replaces Parquet | Parquet is Iceberg's default data file format; Iceberg is the table format layer above Parquet — they are complementary |
| Iceberg and Delta Lake are identical | Both solve similar problems but differ in metadata structure (tree vs log), concurrency model, and multi-engine support |
| Iceberg is faster than Parquet | Iceberg uses Parquet for storage; query speed is the same. Iceberg's benefit is planning speed and ACID semantics, not data scan performance |
| Iceberg needs a central metastore | Iceberg's metadata tree is self-contained in the object store. A Hive Metastore or Glue is one optional catalog implementation — not required |
| Partition evolution is free | Partition evolution is a metadata-only operation but requires ALL new writes to use the new scheme. Mixed-scheme tables can be confusing to query planners not implementing spec correctly |

---

### 🚨 Failure Modes & Diagnosis

**Snapshot Accumulation (Metadata Bloat)**

**Symptom:**
Query planning time grows from 5s to 45s over 3 months.
Reading the manifest list for the latest snapshot takes 30s.

**Root Cause:**
Every write creates a new snapshot. After 90 days of hourly
writes = 2,160 snapshots, each with its own manifest list.
The current snapshot's manifest list references 1,000+ manifest
files; listing them takes many S3 API calls.

**Diagnostic Command / Tool:**
```python
spark.sql("""
  SELECT COUNT(*), MIN(committed_at), MAX(committed_at)
  FROM my_catalog.db.orders.snapshots
""").show()
```

**Fix:**
```python
spark.sql("""
  CALL my_catalog.system.expire_snapshots(
    table => 'db.orders',
    older_than => TIMESTAMP '2024-03-01 00:00:00',
    retain_last => 10
  )
""")
```

**Prevention:**
Schedule `expire_snapshots` daily. Keep only 7 days of history.

---

**Concurrent Write Conflict (CommitFailedException)**

**Symptom:**
Multiple Flink jobs writing to the same Iceberg table fail
with `org.apache.iceberg.exceptions.CommitFailedException:
Cannot commit: metadata.json update conflict`.

**Root Cause:**
Two writers both read snapshot v100, write data files, and try
to commit v101 simultaneously. One succeeds; the other's CAS
on the metadata pointer fails.

**Diagnostic Command / Tool:**
```bash
# Check table snapshots for signs of concurrent retries
aws s3 ls s3://bucket/warehouse/db/orders/metadata/ \
  | grep ".metadata.json" | sort | tail -20
# Gaps in version numbers indicate failed commits
```

**Fix:**
Iceberg clients auto-retry on commit conflict. Increase retry
limit:
```python
spark.conf.set(
  "spark.sql.iceberg.handle-timestamp-without-timezone", "true")
# In catalog config:
# "commit.retry.num-retries": "10"
# "commit.retry.min-wait-ms": "100"
```

**Prevention:**
Shard writers by partition range to minimise overlap.
Tune retry settings based on expected concurrency.

---

**Orphaned Data Files (Missing Expiry)**

**Symptom:**
S3 bucket storage grows steadily even though the logical table
size is stable. Running `expire_snapshots` doesn't reduce storage.

**Root Cause:**
Failed writes created data files that were never committed to
any snapshot (orphans). These are not cleaned by
`expire_snapshots` — which only removes unreferenced snapshots.

**Diagnostic Command / Tool:**
```python
# Find all files older than snapshot retention, not in any manifest
spark.sql("""
  CALL my_catalog.system.remove_orphan_files(
    table => 'db.orders',
    older_than => TIMESTAMP '2024-01-01 00:00:00'
  )
""")
# Returns paths of files that would be deleted
```

**Fix:**
Run `remove_orphan_files` monthly in dry-run mode first to
verify before actual deletion.

**Prevention:**
Add `remove_orphan_files` to scheduled maintenance jobs.
Monitor S3 vs logical table size divergence.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Parquet` — Iceberg's default data file format; Parquet
  knowledge is essential to interpret Iceberg's file statistics
- `Delta Lake` — Iceberg's primary competitor; understanding
  both reveals the design trade-offs clearly
- `ACID Transactions` — the database concept Iceberg
  implements for object store data

**Builds On This (learn these next):**
- `Data Lakehouse` — Iceberg is one of three table formats
  (with Delta and Hudi) that enable the lakehouse architecture
- `Data Mesh` — Iceberg tables with Glue Catalog support
  federated data mesh architectures
- `Data Catalog` — Glue Catalog, Polaris, Nessie are Iceberg
  catalog implementations for metadata governance

**Alternatives / Comparisons:**
- `Apache Hudi` — streaming-optimised table format with
  Merge-on-Read; different concurrency model and use case
- `Delta Lake` — Databricks-backed table format; similar
  capabilities, less multi-engine support out of the box
- `ORC` — data file format (not table format) that Iceberg
  can use as an alternative to Parquet underneath

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Engine-agnostic open table format with    │
│              │ snapshot-based ACID and partition evolution│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Hive metastore bottleneck + no engine-    │
│ SOLVES       │ neutral ACID for multi-engine data lakes  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Metadata IS the transaction system —      │
│              │ no external coordinator needed            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-engine platforms (Spark + Trino +   │
│              │ Flink); partition/schema evolution needed │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Databricks-only platforms where Delta Lake│
│              │ runtime features outweigh openness        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Engine neutrality + partition evolution   │
│              │ vs Delta's richer Databricks integration  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Iceberg is a table format that speaks    │
│              │  every engine's language fluently."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hudi → Data Lakehouse → Data Mesh         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A company is migrating a petabyte-scale Hive table with
5 million partitions to Iceberg. The current Hive metastore
holds 5 million partition entries. After migration, their Trino
query planner must decide which files to read for a query with
a 7-day date range filter. Compare exactly how Hive's metastore
and Iceberg's manifest tree handle this planning step, compute
the approximate number of metadata bytes read in each case, and
explain why Iceberg's approach scales O(log N) while Hive's is
O(N)-ish.

**Q2.** Two teams concurrently attempt to update the same
Iceberg table — Team A runs a Spark `DELETE WHERE region='EU'`
and Team B runs a Trino `INSERT INTO ... SELECT`. Both start
at the same snapshot. Trace the exact sequence of S3 API calls
each team makes, which one succeeds, what error the other
receives, how the retry mechanism works, and whether any data
can be lost or duplicated in the retry scenario.

