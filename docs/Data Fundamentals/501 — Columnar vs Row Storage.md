---
layout: default
title: "Columnar vs Row Storage"
parent: "Data Fundamentals"
nav_order: 501
permalink: /data-fundamentals/columnar-vs-row-storage/
number: "0501"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Binary Formats, Data Types, Database Fundamentals, Data Structures
used_by: Parquet, ORC, Data Warehouse, Apache Spark, OLTP vs OLAP
related: Parquet, ORC, OLTP vs OLAP, Data Compression, Avro
tags:
  - dataengineering
  - intermediate
  - database
  - performance
  - bigdata
---

# 501 — Columnar vs Row Storage

⚡ TL;DR — Row storage groups all fields of one record together; columnar storage groups all values of one field together, making analytics queries dramatically faster.

| #501 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Binary Formats, Data Types, Database Fundamentals, Data Structures | |
| **Used by:** | Parquet, ORC, Data Warehouse, Apache Spark, OLTP vs OLAP | |
| **Related:** | Parquet, ORC, OLTP vs OLAP, Data Compression, Avro | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A data warehouse stores 1 billion retail transactions with 40
columns: order_id, customer_id, product_id, price, discount,
tax, timestamp, store_id, region, … Every month, an analyst runs:
`SELECT AVG(price), region FROM orders GROUP BY region`
With row storage, the engine reads every row — all 40 columns —
even though the query needs only `price` and `region`. That's
40× more disk I/O than necessary.

**THE BREAKING POINT:**
OLAP queries (aggregations over millions of rows, few columns)
fundamentally mismatch with row storage. Row storage scans the
entire table — caches fill with irrelevant column data, I/O
dominates runtime, and adding more CPU doesn't help because the
bottleneck is disk bandwidth. A 45-minute query could run in
90 seconds if only the relevant columns were read.

**THE INVENTION MOMENT:**
This is exactly why columnar storage was invented. By storing all
values of `price` together and all values of `region` together,
a columnar engine reads only 2 of 40 columns — 5% of the data.
Combined with column-specific compression (repeated region names
compress 90%), the result is both 20× less I/O and 10× better
compression ratios.

---

### 📘 Textbook Definition

**Row storage** (row-oriented or NSM — N-ary Storage Model)
stores each record as a contiguous sequence of field values on
disk. Accessing any field in a record requires reading the full
record. **Columnar storage** (column-oriented or DSM — Decomposed
Storage Model) stores all values of each column as a contiguous
sequence. Accessing one column requires reading only that column's
byte range. Columnar storage applies per-column type-specific
compression (run-length encoding, dictionary encoding, delta
encoding) and enables predicate pushdown — skipping column
segments whose min/max statistics exclude the query predicate.
Row storage excels for OLTP (frequent full-record reads/writes);
columnar storage excels for OLAP (infrequent, wide-scan analytics).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Row storage files records together; columnar storage files
each field's values across all records together.

**One analogy:**

> Imagine a spreadsheet stored two ways. Row storage photocopies
> each entire row onto a separate card. To find everyone's salary,
> you flip through every card and fish out the salary field.
> Columnar storage cuts out the salary column from every row and
> stacks those slips together. To find everyone's salary, you
> read one stack.

**One insight:**
The same data — same bits, same values — causes a 20–50× speed
difference in analytics purely because of layout. Data layout
is not an implementation detail; it is the dominant factor in
query performance for analytical workloads.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Disk I/O is the dominant cost of analytical queries at scale.
2. Analytical queries read a few columns across many rows.
3. Contiguous same-typed values compress better than interleaved
   mixed-typed rows.

**DERIVED DESIGN:**
Given invariant 2: store each column's values contiguously so a
column read is one sequential I/O.

Given invariant 3: same-typed contiguous values enable:
- *Dictionary encoding*: replace repeated strings (region names)
  with integer IDs. "NORTH_EAST" → 1, "SOUTH_WEST" → 2.
  Reduces 11-byte string to 1-byte integer per row.
- *Run-length encoding (RLE)*: `1,1,1,1,2,2,2` → `4×1, 3×2`.
  Sorted columns compress to almost nothing.
- *Delta encoding*: timestamps `[1000, 1001, 1003, 1006]` → deltas
  `[1000, 1, 2, 3]` — smaller numbers, better compression.
- *Bit packing*: boolean columns → 1 bit per value.

Given invariant 1: column pruning (reading only needed columns)
and predicate pushdown (skipping column chunks outside predicate
range) reduce I/O multiplicatively.

**THE TRADE-OFFS:**
**Gain (Columnar):** Analytic query speed; compression ratios
(3–10×); column-level statistics enable skipping data segments.
**Cost (Columnar):** Single-record inserts require writing all
column files — poor for transactional workloads. Random row
lookups reconstruct a record by joining N column segments —
higher latency than row stores for key lookups.

**Gain (Row):** Single-record write = one sequential write.
Full-record retrieval = one sequential read. Excellent for OLTP.
**Cost (Row):** Reads unneeded columns on analytic queries;
homogeneous compression cannot be applied across mixed-type rows.

---

### 🧪 Thought Experiment

**SETUP:**
A table with 4 columns: `id`, `name`, `salary`, `department`.
1 million rows. You need: `SELECT AVG(salary) FROM employees`.

**WHAT HAPPENS WITH ROW STORAGE:**
```
Row 1: [1][Alice][85000][ENG]
Row 2: [2][Bob][92000][HR]
... 1,000,000 rows ...
```
The engine reads every byte of every row: 4 fields × avg 20 bytes
= 80 bytes/row × 1M rows = **80 MB** of I/O.
IDs and names are read then immediately discarded. 75% of I/O
was wasted on irrelevant data.

**WHAT HAPPENS WITH COLUMNAR STORAGE:**
```
id column:         [1][2][3]...[1000000]         → 4 MB
name column:       [Alice][Bob][Carol]...          → 14 MB
salary column:     [85000][92000][78000]...        → 4 MB
department column: [ENG][HR][ENG]...               → 2 MB (dict-encod.)
```
Engine reads ONLY the `salary` column: **4 MB** of I/O.
20× less I/O than row storage. `AVG()` computed on the tightly
packed integer array in a tight CPU loop.

**THE INSIGHT:**
The speedup is not from a smarter algorithm — the same AVG
operation runs on the same data. The speedup is entirely from
reading 5% of the data. Layout IS the algorithm at scale.

---

### 🧠 Mental Model / Analogy

> Think of a database as a shelf of binders. **Row storage** gives
> each customer one binder containing ALL their documents — every
> transaction, every attribute. To calculate total sales, you pull
> every customer's binder and flip to the "amount" page in each.
> **Columnar storage** creates one binder per attribute — the
> "amount" binder has everyone's amounts in order. To calculate
> total sales, you grab just the amounts binder.

- "Customer binder" → database row
- "Amount page" → a single column value within a row
- "Amount binder" → entire column stored together
- "Grabbing just the amounts binder" → column pruning
- "Skipping binders whose index says wrong range" → predicate pushdown

**Where this analogy breaks down:** Real columnar stores use
**row groups** (Parquet) or **stripes** (ORC) — blocks of rows
stored in columnar format. This hybrid enables efficient streaming
writes (one row group per batch) while preserving columnar read
performance within each group.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Two ways to organise data on disk. Row storage keeps all info
about person 1 together, then all info about person 2, etc. —
good for looking up one person. Columnar storage keeps everyone's
salary together, everyone's name together, etc. — good for
computing statistics across all people.

**Level 2 — How to use it (junior developer):**
Use row storage (PostgreSQL, MySQL) for web application
transactions: user login, order creation, inventory update.
Use columnar storage (Parquet files, Amazon Redshift, BigQuery,
Snowflake) for analytics: dashboards, reports, aggregations.
Never run analytical workloads on OLTP row databases at scale —
they will degrade production transactional performance.

**Level 3 — How it works (mid-level engineer):**
In Parquet: data is split into **row groups** (~128 MB). Within
each row group, each column has its own **column chunk**. Within
each column chunk, data is split into **data pages** (~1 MB).
Each data page uses one encoding: `PLAIN`, `DICTIONARY_ENCODING`,
or `RLE_DICTIONARY`. Column chunks have statistics (min, max,
distinct count, null count) written to the row group footer.
The read path: read footer → check statistics per row group
→ skip row groups outside predicate → read column chunk bytes
→ decompress → decode → filter → aggregate. The entire
pipeline operates on column vectors, enabling SIMD CPU
optimisations.

**Level 4 — Why it was designed this way (senior/staff):**
The row-vs-column debate mirrors the CPU cache line optimisation
principle: spatial locality trumps everything at scale. Row
stores achieve spatial locality for full-record operations —
all fields of one entity are within the same cache line sequence.
Column stores achieve spatial locality for aggregation operations —
10,000 consecutive salary values fit in CPU L1/L2 cache for
vectorised SIMD processing. The academic insight (Stonebraker
et al., C-Store 2005) was that OLAP workloads achieve 5–50× better
performance on columnar than row stores — a gap that grows with
table width. Modern systems like DuckDB push this further with
SIMD-vectorised column-at-a-time query execution that processes
1024 values per CPU instruction.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              ROW STORAGE LAYOUT                        │
│                                                        │
│  Page 1: [id=1,name=Alice,sal=85K,dept=ENG]            │
│           [id=2,name=Bob,  sal=92K,dept=HR ]            │
│           [id=3,name=Carol,sal=78K,dept=ENG]            │
│  Page 2: ...                                           │
│                                                        │
│  Query: SELECT AVG(sal)                                │
│  Must read: ALL columns in ALL pages → 100% I/O        │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│           COLUMNAR STORAGE LAYOUT (PARQUET)            │
│                                                        │
│  Row Group 0:                                          │
│    id chunk:   [1][2][3][4]...[1000000]                │
│    name chunk: [Alice][Bob][Carol]...                  │
│    sal chunk:  [85000][92000][78000]...                │
│    dept chunk: [0][1][0]...  (dict: 0=ENG,1=HR)        │
│                                                        │
│  Query: SELECT AVG(sal)                                │
│  Reads: ONLY sal chunk → 2.5% of I/O                  │
└────────────────────────────────────────────────────────┘
```

**Column encoding example (salary):**
```
Raw values:    85000, 85000, 85000, 92000, 92000, 78000
After RLE:     3×85000, 2×92000, 1×78000
Bytes used:    6 pairs × 8 bytes = 48 bytes vs 6 × 4 = 24 raw
               → RLE wins only when runs are long; dict better here

Dictionary encoding:
  Dict: {0: 78000, 1: 85000, 2: 92000}
  Values: [1, 1, 1, 2, 2, 0]
  → 6 bytes (1 byte each) + 3 × 4 byte dict = 18 bytes (vs 24)
```

---

### 💻 Code Example

**Example 1 — Write columnar Parquet and verify column pruning:**
```python
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder.getOrCreate()

# Write as Parquet (columnar)
employees_df.write.parquet("s3://bucket/employees/")

# Query with column pruning — Spark reads ONLY salary column
result = spark.read.parquet("s3://bucket/employees/") \
  .select("salary") \
  .agg(F.avg("salary").alias("avg_salary"))

# Confirm with explain — look for "PushedFilters" and
# "ReadSchema: struct<salary:double>"
result.explain(True)
```

**Example 2 — Compare PostgreSQL (row) vs DuckDB (column):**
```sql
-- PostgreSQL (row storage) — reads all columns
SELECT AVG(salary) FROM employees;
-- Execution: Seq Scan on employees — reads every row
-- 1M rows × 80 bytes = 80 MB I/O

-- DuckDB (columnar) — same query
SELECT AVG(salary) FROM 'employees.parquet';
-- Reads only salary column chunk
-- 1M × 4 bytes (int32) = 4 MB I/O → 20× faster
```

**Example 3 — Redshift column compression:**
```sql
-- In Amazon Redshift (columnar), define compression
-- per column at table creation time
CREATE TABLE orders (
  order_id     BIGINT       ENCODE DELTA,      -- sequential IDs
  customer_id  BIGINT       ENCODE LZO,
  amount       DECIMAL(10,2) ENCODE AZ64,      -- numeric
  region       VARCHAR(20)  ENCODE BYTEDICT,   -- low cardinality
  created_at   TIMESTAMP    ENCODE DELTA32K    -- time series
)
SORTKEY (created_at);  -- enables zone map (predicate pushdown)
```

---

### ⚖️ Comparison Table

| Aspect | Row Storage (OLTP) | Columnar Storage (OLAP) |
|---|---|---|
| **Single-record read** | Fast (one seek, full record) | Slow (re-assemble N columns) |
| **Full-column scan** | Slow (reads all columns) | Fast (reads one column) |
| **Single-row insert** | Fast (append one row) | Slow (update N column files) |
| **Bulk insert** | Medium | Fast (columnar batch write) |
| **Compression ratio** | 1.5–2× | 3–10× |
| **Best for** | Web apps, transactions | Analytics, reports |

**How to choose:** Web application with frequent reads/writes of
individual records → row storage (PostgreSQL, MySQL). Analytics
dashboard computing aggregations over millions of rows → columnar
storage (Parquet/Redshift/BigQuery/Snowflake).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Columnar is always faster | For single-row lookups (by primary key), row storage is faster — columnar must re-assemble the record from N column chunks |
| You have to choose one or the other | HTAP systems (TiDB, SingleStore, Oracle) support both layouts simultaneously; data warehouses use columnar for historical, row for hot data |
| Columnar compression explains all the speedup | Compression reduces I/O; column pruning reduces it further; predicate pushdown on row group statistics can eliminate 90%+ of reads entirely |
| Parquet is a database | Parquet is a file format, not a database. It has no query engine, no transactions, no indexes. The engine is provided by Spark, Hive, Trino, DuckDB, etc. |
| Row groups negate columnar benefits | Row groups are a practical write-performance compromise; analytics still benefits from column pruning and predicate pushdown within each row group |

---

### 🚨 Failure Modes & Diagnosis

**Low Compression Due to Unsorted Data**

**Symptom:**
Parquet files are nearly as large as JSON equivalents.
Compression ratio is only 1.5× for string columns.

**Root Cause:**
Data is not sorted before writing. Run-length encoding and
dictionary encoding achieve maximum compression on sorted,
similar values. Random ordering prevents long runs.

**Diagnostic Command / Tool:**
```python
import pyarrow.parquet as pq
meta = pq.read_metadata("data.parquet")
# Inspect per-column statistics
for rg in range(meta.num_row_groups):
    col = meta.row_group(rg).column(0)
    print(col.statistics)
# Low distinct_count vs num_values → good dict opportunity
```

**Fix:**
Sort data on the most-filtered column before writing:
```python
df.orderBy("region", "created_at") \
  .write.parquet("s3://bucket/sorted_data/")
```

**Prevention:**
Sort on write for high-cardinality analytics tables.
Use Delta Lake `OPTIMIZE ZORDER BY (col)` for after-the-fact
sorting without rewriting all data.

---

**Columnar Store Used for OLTP-Like Queries**

**Symptom:**
Redshift/BigQuery query `SELECT * FROM orders WHERE order_id = 123`
takes 3–5 seconds on a 100M row table.

**Root Cause:**
Direct key lookup on a columnar store must read all column chunks
for the matching row group and re-assemble the record.
No row-level B-tree index exists.

**Diagnostic Command / Tool:**
```sql
-- Redshift: check if query is scanning too many blocks
SELECT query, rows, blocks_read, exec_time
FROM stl_scan WHERE query = [your query id]
ORDER BY exec_time DESC;
```

**Fix:**
For random key lookups, use a row-oriented cache (Redis/Cassandra)
as a lookup layer. Use columnar store only for analytics.

**Prevention:**
Do not use data warehouse/data lake for application-level
single-record lookups. Use a separate OLTP or key-value store.

---

**Row Group Statistics Not Helping (Wrong Sort Order)**

**Symptom:**
Spark query with `WHERE order_date = '2024-01-15'` reads
100% of Parquet files instead of ~0.3% (one day of data).

**Root Cause:**
Data was written unsorted. Every row group contains all dates
— row group min/max statistics span full date range. No row
groups can be skipped.

**Diagnostic Command / Tool:**
```python
import pyarrow.parquet as pq
meta = pq.read_metadata("events.parquet")
for i in range(meta.num_row_groups):
    stats = meta.row_group(i).column(
      meta.row_group(i).num_columns - 1  # date column
    ).statistics
    print(f"RG {i}: min={stats.min}, max={stats.max}")
# If every row group shows same min/max → no pruning possible
```

**Fix:**
Re-partition and sort by date on write, or use Delta Lake
`OPTIMIZE ZORDER BY (order_date)`.

**Prevention:**
Write Parquet data sorted by the primary partition key.
Verify row group statistics after writing using `pyarrow.parquet`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Binary Formats` — Parquet and ORC are binary columnar
  formats; understanding binary vs text is a prerequisite
- `Database Fundamentals` — the B-tree, heap, and index
  storage models that row databases use
- `Data Types` — columnar encoding choices depend on
  knowing the type (integer, string, timestamp)

**Builds On This (learn these next):**
- `Parquet` — the dominant columnar file format; drill into
  encoding, compression, and predicate pushdown in detail
- `ORC` — Hive's alternative columnar format with different
  stripe-level index structure
- `OLTP vs OLAP` — the workload types that drive the
  choice between row and columnar storage

**Alternatives / Comparisons:**
- `Delta Lake` — adds ACID transactions and update/delete
  capability on top of Parquet columnar files
- `Data Compression` — compression is applied within columnar
  formats but is a separable concern
- `Avro` — the row-oriented binary format; counterpart to
  Parquet for streaming/row-access workloads

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two strategies for laying bytes on disk:  │
│              │ group by record vs group by field         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Analytics reads 3 of 50 columns; row      │
│ SOLVES       │ storage forces reading all 50             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Layout IS performance. The same query on  │
│              │ the same data differs 20–50× by layout    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Row: OLTP (insert/update/key lookup)      │
│              │ Column: OLAP (aggregations, scans)        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use columnar for single-row lookups; │
│              │ don't use row storage for analytics at TB+ │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Write performance vs analytic scan speed  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Row storage files people; columnar       │
│              │  storage files their salaries together."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Parquet → ORC → OLTP vs OLAP              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce platform uses PostgreSQL (row storage) for
orders. The table has grown to 500 million rows and 35 columns.
Monthly revenue reports (`SELECT SUM(amount), region, month FROM
orders GROUP BY region, month`) take 25 minutes. An engineer
proposes adding a Parquet-based data warehouse. Describe exactly
why the same SQL query would run ×30 faster in a columnar system,
what specific physical I/O operations differ, and identify three
operational risks in the migration that could negate the
performance gain.

**Q2.** HTAP databases (like TiDB, SingleStore) claim to support
both row and columnar layouts in the same system. Using your
understanding of the fundamental I/O trade-offs, explain at what
point the "both" claim starts to break down — what specific
workload mix would cause such a system to perform worse than
a dedicated row or columnar store, and why.

