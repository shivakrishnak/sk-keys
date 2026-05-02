---
layout: default
title: "Columnar vs Row Storage"
parent: "Data Fundamentals"
nav_order: 501
permalink: /data-fundamentals/columnar-vs-row-storage/
number: "501"
category: Data Fundamentals
difficulty: ★★☆
depends_on: "Binary Formats (Avro, Parquet, ORC, Protobuf), Data Types"
used_by: "Parquet, ORC, Delta Lake, Snowflake, BigQuery, analytical query engines"
tags: #data, #columnar, #row-storage, #parquet, #olap, #oltp, #storage-formats
---

# 501 — Columnar vs Row Storage

`#data` `#columnar` `#row-storage` `#parquet` `#olap` `#oltp` `#storage-formats`

⚡ TL;DR — **Row storage** (PostgreSQL, MySQL) stores complete rows together — optimal for OLTP (fetch all fields for one record). **Columnar storage** (Parquet, ORC, Snowflake, BigQuery) stores each column together — optimal for OLAP (aggregate one column across millions of rows). Most data warehouses and data lakes use columnar storage.

| #501            | Category: Data Fundamentals                                             | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Binary Formats (Avro, Parquet, ORC), Data Types                         |                 |
| **Used by:**    | Parquet, ORC, Delta Lake, Snowflake, BigQuery, analytical query engines |                 |

---

### 📘 Textbook Definition

**Row storage (row-oriented / NSM — N-ary Storage Model)**: data is physically stored row by row. All columns of row 1 are stored contiguously, followed by all columns of row 2, etc. Reading row 1 requires one sequential I/O (or one page access). Writing/updating row 1 is efficient (single seek to write all column values). Optimal for OLTP workloads: INSERT/UPDATE/DELETE individual records; point queries (fetch by primary key); full-row reads. Examples: PostgreSQL heap files, MySQL InnoDB pages, Oracle segments.

**Columnar storage (column-oriented / DSM — Decomposition Storage Model)**: data is physically stored column by column. All values of column 1 for all rows are stored contiguously, followed by all values of column 2, etc. Reading column 1 for all rows requires one sequential read. Writing all columns of one new row requires N writes (one to each column's storage). Optimal for OLAP workloads: aggregations (SUM, AVG, COUNT) over one column; queries that touch few columns from many rows; compression (identical data type per column → better compression). Examples: Parquet, ORC, Apache Arrow in-memory, Snowflake internal format, BigQuery storage.

---

### 🟢 Simple Definition (Easy)

Imagine a table with 1 million customers and 20 columns.

**Row storage**: each customer's 20 columns stored together. To find one customer → find their row → read all 20 columns. Great for: "show me everything about customer 12345."

**Columnar storage**: all customer IDs together, all names together, all amounts together. To sum all amounts → read only the amounts column, skip 19 other columns. Great for: "what's the total revenue from all customers?"

OLTP (web app) → row storage. OLAP (analytics) → columnar storage.

---

### 🔵 Simple Definition (Elaborated)

The access pattern difference is fundamental:

**OLTP** (Online Transaction Processing): "Read row X, update row X, insert row Y." Each operation touches one or few rows but all their columns. Row storage is optimal — one disk seek, read all columns in one pass.

**OLAP** (Online Analytical Processing): "Sum column `revenue` for all rows where `country='US'` and `date > '2024-01-01'`." This touches 2 columns across potentially 100M rows. Columnar storage skips 18 unused columns. Plus, all values in a column are the same data type → better compression (dict encoding, RLE).

Modern data architectures run OLTP on row-stores (PostgreSQL, MySQL) and OLAP on column-stores (Snowflake, BigQuery, Parquet + Spark/Athena). They are not competing technologies — they serve different workloads.

---

### 🔩 First Principles Explanation

```
PHYSICAL LAYOUT:

Table: orders
┌─────┬──────────────┬──────────┬──────────┬──────────┐
│ id  │ customer_id  │ amount   │ city     │ status   │
├─────┼──────────────┼──────────┼──────────┼──────────┤
│ 101 │ C001         │ 149.99   │ Seattle  │ DONE     │
│ 102 │ C002         │  89.50   │ NYC      │ DONE     │
│ 103 │ C001         │ 299.00   │ Seattle  │ PENDING  │
│ 104 │ C003         │  49.99   │ Austin   │ DONE     │
└─────┴──────────────┴──────────┴──────────┴──────────┘

ROW STORAGE physical layout (PostgreSQL heap page):
[101|C001|149.99|Seattle|DONE][102|C002|89.50|NYC|DONE][103|C001|299.00|Seattle|PENDING][104|C003|49.99|Austin|DONE]

Query: SELECT * FROM orders WHERE id = 102
→ Seek to row 102 → read all 5 columns at once → single I/O unit
✅ Perfect for full-row retrieval

Query: SELECT SUM(amount) FROM orders WHERE status = 'DONE'
→ Must read EVERY row to access both amount and status
→ Reads: id, customer_id (unnecessary), amount, city (unnecessary), status
→ For 1M rows: read ~100MB just to access 2 columns

COLUMNAR STORAGE physical layout (Parquet):
Column "id":          [101][102][103][104]
Column "customer_id": [C001][C002][C001][C003]
Column "amount":      [149.99][89.50][299.00][49.99]
Column "city":        [Seattle][NYC][Seattle][Austin]
Column "status":      [DONE][DONE][PENDING][DONE]

Query: SELECT SUM(amount) FROM orders WHERE status = 'DONE'
→ Step 1: Read "status" column → identify row positions {0,1,3} (status='DONE')
→ Step 2: Read "amount" column, positions {0,1,3} → [149.99, 89.50, 49.99]
→ SUM = 289.48
→ "id", "customer_id", "city" columns: never read

For 1M rows: read 2 columns × fraction of rows = 2-4MB vs 100MB
→ 25-50x less I/O → 25-50x faster query

COMPRESSION ADVANTAGE:

Row storage column data: mixed types in one disk block
[101|"C001"|149.99|"Seattle"|"DONE" | 102|"C002"|89.50|"NYC"|"DONE" | ...]
→ Mixed types, mixed values → poor compression ratio

Columnar "city" column: all same type, low cardinality
["Seattle","NYC","Seattle","Austin","Seattle","NYC","Seattle","NYC", ...]
→ Dictionary: {0:Seattle, 1:NYC, 2:Austin}
→ Encoded: [0,1,0,2,0,1,0,1, ...]  (ints instead of strings)
→ Compression ratio: 8-20x for low-cardinality string columns

Columnar "amount" column: all float64, similar values
[149.99, 89.50, 299.00, 49.99, 149.99, 89.50, ...]
→ Delta encoding or ZSTD: 2-5x compression

COMBINED EFFECT: 100MB CSV → 2-5MB Parquet (with compression)

WRITE PERFORMANCE COMPARISON:

Row storage (INSERT):
  INSERT INTO orders VALUES (105, 'C004', 199.00, 'Boston', 'PENDING')
  → Find correct heap page → write all 5 values to one location
  → 1 write operation (single page write)
  ✅ Fast single-row write

Columnar storage (INSERT to Parquet):
  Write new record: need to append to 5 column chunks
  → CANNOT do this efficiently in-place on immutable files
  → Solution 1: buffer writes → batch flush as new row group
  → Solution 2: Delta Lake / Iceberg — write to delta log, merge later (OPTIMIZE)
  ❌ Poor performance for single-row inserts
  ✅ Excellent performance for bulk inserts (10K+ rows at once)

OLTP vs OLAP SUMMARY:

              OLTP (PostgreSQL)      OLAP (Parquet/Snowflake)
  Workload   │ Individual rows      │ Aggregate columns
  Operation  │ R/W balance          │ Read-heavy
  Query      │ Simple + joins       │ Complex + aggregations
  Latency    │ Milliseconds         │ Seconds to minutes
  Throughput │ 1000s txn/sec        │ Terabytes/hour
  Schema     │ Normalized           │ Denormalized (star schema)
  Storage    │ Row-based            │ Columnar
  Example    │ PostgreSQL, MySQL    │ Parquet, BigQuery, Snowflake
```

---

### ❓ Why Does This Exist (Why Before What)

The OLTP/OLAP split emerged because the same storage layout cannot optimally serve both workloads. Before columnar databases (Sybase IQ, Vertica, then BigQuery, Snowflake), teams tried to run analytics directly on OLTP databases — with poor results (long-running analytics queries locked tables, blocked transactions). The separation of OLTP (row stores) and OLAP (column stores) into dedicated systems is the foundation of the modern data platform architecture.

---

### 🧠 Mental Model / Analogy

> **A bookshelf vs a card catalog**: **Row storage** is a bookshelf where each shelf holds one book (row) — all chapters (columns) of that book together. Finding one book: pull the book. Reading chapter 3 from every book: visit every shelf, open every book, flip to chapter 3. **Columnar storage** is a card catalog where one drawer holds all "chapter 3" pages from every book. Reading chapter 3 from every book: open one drawer. Finding one complete book: visit every drawer and pull that book's card. "Chapter 3 of every book" = one column across all rows.

---

### ⚙️ How It Works (Mechanism)

```
VECTORIZED EXECUTION (column-store advantage):

  SIMD (Single Instruction, Multiple Data) operations:

  Row-based SUM loop:
  for row in rows:
      sum += row.amount  # one float at a time

  Columnar vectorized:
  amounts = [149.99, 89.50, 299.00, 49.99, ...]  # contiguous float64 array
  sum = SIMD_ADD(amounts)  # 8 floats added per CPU cycle (AVX2: 256-bit register)

  Columnar: 8x more arithmetic throughput + better cache utilization
  (entire column fits in L1/L2 cache; mixed-type row data does not)

LATE MATERIALIZATION:

  Query: SELECT id, amount FROM orders WHERE city='Seattle' AND status='DONE'

  EARLY materialization (reconstruct rows):
  1. Read city column → filter → {row 0, row 2} match
  2. Read status column → filter → {row 0, row 2} still match
  3. Read id, amount for rows {0, 2}
  4. Return tuples [(101, 149.99), (103, 299.00)]

  With predicates: read only needed columns, apply filters on raw columns
  = late materialization → minimum bytes read, maximum cache efficiency
```

---

### 🔄 How It Connects (Mini-Map)

```
Analytics workloads need to aggregate columns across millions of rows
        │
        ▼
Columnar vs Row Storage ◄── (you are here)
        │
        ├── Parquet: columnar file format for data lakes
        ├── ORC: columnar format for Hive ecosystems
        ├── Snowflake / BigQuery: columnar databases in the cloud
        ├── Apache Arrow: in-memory columnar format (zero-copy)
        └── OLAP vs OLTP: the architectural pattern this enables
```

---

### 💻 Code Example

```python
# Demonstrating columnar efficiency with PyArrow

import pyarrow as pa
import pyarrow.parquet as pq
import time, random

# Generate 1M order records
n = 1_000_000
data = {
    "order_id": list(range(1, n+1)),
    "customer_id": [f"C{random.randint(1,10000):05d}" for _ in range(n)],
    "amount": [round(random.uniform(10, 500), 2) for _ in range(n)],
    "city": [random.choice(["Seattle","NYC","Austin","Chicago","LA"]) for _ in range(n)],
    "status": [random.choice(["COMPLETED","PENDING","CANCELLED"]) for _ in range(n)],
}
table = pa.table(data)

# Write as Parquet
pq.write_table(table, "orders.parquet", compression="snappy")

# COLUMNAR READ: only read 'amount' and 'status' columns
t0 = time.time()
result = pq.read_table(
    "orders.parquet",
    columns=["amount", "status"],  # column pruning: skip order_id, customer_id, city
    filters=[("status", "=", "COMPLETED")]  # predicate pushdown
)
total = result.column("amount").to_pylist()
print(f"Column pruning read: {time.time()-t0:.3f}s, {len(total)} completed orders")

# Compare: reading ALL columns (simulating row-based)
t0 = time.time()
result_all = pq.read_table("orders.parquet")  # no column pruning
print(f"Full table read: {time.time()-t0:.3f}s")
# Column-pruned read is significantly faster
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                                                       |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Columnar databases can't do transactional workloads | Modern columnar stores (Snowflake, BigQuery, Delta Lake) support ACID transactions via metadata layers (transaction logs, versioning). However, single-row INSERT/UPDATE latency is still higher than OLTP row stores. Use the right tool: PostgreSQL for OLTP, Snowflake/Parquet for OLAP.                                   |
| Parquet is slow to write (compared to CSV)          | Parquet write is slower than CSV write (encoding, schema, compression overhead). But a 10% slower write buys you 50x faster reads and 10x smaller storage. At analytics scale, reads vastly outnumber writes — optimize for reads.                                                                                            |
| Apache Arrow is the same as Parquet                 | Arrow is an **in-memory** columnar format (zero-copy IPC between processes/languages). Parquet is an **on-disk** columnar format (storage). Arrow is used to pass data between Pandas/Spark/DuckDB in memory. Parquet is used to persist data to S3/HDFS. They share the same columnar philosophy but serve different layers. |

---

### 🔥 Pitfalls in Production

```
PITFALL: joining fact table with dimension table — wrong partition order

  -- Fact table: 500M rows of orders (Parquet, partitioned by date)
  -- Dimension table: 10M rows of customers (Parquet, not partitioned)

  -- ❌ SLOW: small table as probe side, large table as build side
  SELECT o.amount, c.name
  FROM customers c    -- 10M rows: Spark builds hash table from this
  JOIN orders o       -- 500M rows: Spark probes → hash table too large for memory → spill
  ON c.id = o.customer_id
  WHERE o.date = '2024-01-15'

  -- ✅ FAST: let Spark broadcast the small table
  SELECT /*+ BROADCAST(c) */ o.amount, c.name
  FROM orders o       -- 500M rows: not shuffled
  JOIN customers c    -- 10M rows: broadcast to all executors
  ON o.customer_id = c.id
  WHERE o.date = '2024-01-15'

  -- Also: partition pruning on orders WHERE date='2024-01-15'
  -- → reads 1 partition (1/365th of data) instead of full table
```

---

### 🔗 Related Keywords

- `Parquet` — the primary columnar file format for data lake analytics
- `ORC` — columnar format for Hive/EMR ecosystems; built-in ACID
- `Binary Formats (Avro, Parquet, ORC, Protobuf)` — overview of all binary formats
- `Delta Lake` — ACID transactions + schema evolution on top of Parquet
- `Apache Arrow` — in-memory columnar format; bridges Pandas, Spark, DuckDB

---

### 📌 Quick Reference Card

```
┌─────────────────┬─────────────────────┬────────────────────────┐
│                 │ Row Storage         │ Columnar Storage       │
├─────────────────┼─────────────────────┼────────────────────────┤
│ Layout          │ Row by row          │ Column by column       │
│ Optimal for     │ OLTP: full row R/W  │ OLAP: aggregate cols   │
│ Examples        │ PostgreSQL, MySQL   │ Parquet, ORC, BigQuery │
│ Query speed     │ Fast for row fetch  │ Fast for aggregations  │
│ Compression     │ Moderate            │ Excellent (per-type)   │
│ Write speed     │ Fast single-row     │ Fast bulk, slow single │
│ Use when        │ Web app, CRUD       │ Analytics, reporting   │
└─────────────────┴─────────────────────┴────────────────────────┘
Rule: Never run heavy analytics on OLTP row stores at scale.
      Use columnar storage for data warehouse / data lake queries.
```

---

### 🧠 Think About This Before We Continue

**Q1.** Amazon Redshift uses a columnar storage format but stores data on SSD-backed nodes distributed across a cluster. BigQuery separates compute from storage (data stored in Google's Colossus, compute on Dremel). Snowflake also separates storage (S3) from compute (virtual warehouses). What does this "compute-storage separation" architecture imply about columnar vs row storage design? How does it affect the choice between running a large query on Snowflake vs running it on a PostgreSQL read replica?

**Q2.** Apache Arrow is an in-memory columnar format that has become the lingua franca for data interchange between data tools (Pandas, Spark, DuckDB, R). When Spark reads a Parquet file, it converts the data to Arrow format in memory. When you call `df.toPandas()`, Spark sends Arrow data to the Python driver. What would have happened before Arrow existed (prior to 2016)? What inefficiencies did Arrow eliminate?
