---
layout: default
title: "OLTP vs OLAP"
parent: "Data Fundamentals"
nav_order: 529
permalink: /data-fundamentals/oltp-vs-olap/
number: "0529"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Data Warehouse, Database Fundamentals, Columnar vs Row Storage, Star Schema, Data Types (Primitive, Complex, Semi-Structured)
used_by: Data Warehouse, ETL vs ELT, Data Lakehouse, Data Modeling
related: Data Warehouse, Data Lake, ETL vs ELT, Columnar vs Row Storage, Data Modeling
tags:
  - dataengineering
  - database
  - architecture
  - intermediate
  - tradeoff
---

# 529 — OLTP vs OLAP

⚡ TL;DR — OLTP handles fast single-row transactions; OLAP handles slow multi-row analytical queries — two fundamentally different workloads that require different database architectures.

| #529 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Data Warehouse, Database Fundamentals, Columnar vs Row Storage, Star Schema | |
| **Used by:** | Data Warehouse, ETL vs ELT, Data Lakehouse, Data Modeling | |
| **Related:** | Data Warehouse, Data Lake, ETL vs ELT, Columnar vs Row Storage, Data Modeling | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce company runs all workloads — customer checkout, inventory updates, and year-over-year sales reports — on the same PostgreSQL database. During Black Friday, the sales analytics team runs a `SELECT SUM(revenue) GROUP BY product_category WHERE order_date > '2020-01-01'` query. It scans 500 million rows. While scanning, it holds shared locks on the orders table. Checkout transactions that need to update `orders` wait. Checkout latency spikes from 40 ms to 8 seconds. 12% of customers abandon carts. The database cannot serve two fundamentally different access patterns simultaneously.

**THE BREAKING POINT:**
Transactional databases are optimised for row-at-a-time inserts and lookups; analytical databases excel at scanning millions of rows to aggregate columns. The access patterns are orthogonal — the same physical storage layout that makes one fast makes the other slow.

**THE INVENTION MOMENT:**
This is exactly why the distinction between OLTP and OLAP was formalised — acknowledging that transaction processing and analytical processing require fundamentally different architectures and should not share the same system.

---

### 📘 Textbook Definition

**OLTP (Online Transaction Processing)** is a class of database workload characterised by high-frequency, short-duration, single or small-set row operations (INSERT, UPDATE, DELETE, point-SELECT) that modify the operational state of a business in real time. OLTP systems use normalised schemas, row-oriented storage, and are ACID-compliant. **OLAP (Online Analytical Processing)** is a class of database workload characterised by low-frequency, long-duration queries that scan large numbers of rows across multiple dimensions to aggregate and compute analytical results. OLAP systems use denormalised star/snowflake schemas, columnar storage, and massively parallel query execution. The two workload types are so different in access pattern that they require physically separate database architectures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OLTP writes and reads individual rows fast; OLAP reads millions of rows slowly to compute aggregations — never mix them on the same system.

**One analogy:**
> OLTP is like a cash register at a supermarket — it processes one transaction at a time, extremely fast, needs to know exactly what's in the basket right now. OLAP is like the store's monthly inventory and sales report — it reads through millions of transactions to find patterns and totals. You would never run the monthly report on the cash register while customers are checking out.

**One insight:**
The physical root of the difference is storage layout. Row-oriented storage (PostgreSQL, MySQL) stores all columns of one row together — ideal for reading or updating the whole row. Columnar storage (Snowflake, BigQuery, Parquet) stores all values of one column together — ideal for `SUM(revenue)` which only needs one column from 500 million rows, not all columns.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. OLTP reads/writes one row at a time; I/O is per-row.
2. OLAP reads N columns across M rows; I/O is per-column.
3. These two I/O patterns require mutually incompatible physical storage layouts.

**DERIVED DESIGN:**

| Feature | OLTP | OLAP |
|---|---|---|
| Physical storage | Row-oriented | Columnar |
| Schema | Normalised (3NF) | Denormalised (star/snowflake) |
| Indexing | B-tree indexes on PKs/FKs | Zone maps / min-max metadata |
| Transactions | ACID, short-lived | Read-heavy, long-running |
| Concurrency | High (thousands/second) | Low (dozens/day) |
| Data age | Current operational state | Historical snapshots |
| Scale | GB–TB | TB–PB |

**DERIVED DESIGN reasoning:**
For OLTP: You need to find a single customer's record fast → B-tree index on `customer_id` → O(log n) lookup. You need to update the `status` column for one row → row-oriented means the whole row is on one page → one disk seek updates all columns.

For OLAP: You need `SUM(revenue)` across 500 million rows → only need the `revenue` column → columnar storage means reading only 1/N of the data (where N is number of columns) → 100× less I/O → query in seconds instead of hours.

**THE TRADE-OFFS:**
OLTP **Gains:** Sub-millisecond row operations; strong ACID; current-state accuracy.
OLTP **Costs:** Cannot scan billions of rows efficiently; normalised schema requires many JOINs for analytics.

OLAP **Gains:** Sub-second aggregations on billions of rows; columnar compression.
OLAP **Costs:** Write operations are expensive; data is never fully current (ETL lag); complex ad hoc updates impractical.

---

### 🧪 Thought Experiment

**SETUP:**
A single database serves both checkout (OLTP) and monthly revenue report (OLAP). The revenue query: `SELECT SUM(price * quantity) FROM orders WHERE order_date > '2023-01-01'` across 800 million rows.

**WHAT HAPPENS IF YOU MIX THEM:**
Row-oriented database reads every column of every row to find `price` and `quantity` → 800 million × 128 bytes/row = 102 GB of disk reads. Execution time: 45 minutes. During those 45 minutes, table-level statistics locking and buffer pool saturation degrade checkout performance. Checkout p99 latency: 12 seconds. Revenue:  at least 2 cart abandonments per second = 5,400 lost carts.

**WHAT HAPPENS WITH SEPARATION:**
Checkout runs on OLTP (PostgreSQL, row-oriented). The revenue query runs on OLAP (Snowflake, columnar). Snowflake reads only the `price`, `quantity`, and `order_date` columns from 800 million rows → 800 million × 16 bytes/row (3 columns) = 12.8 GB. With columnar compression, effective I/O ≈ 2 GB. Query: 8 seconds. Checkout unaffected.

**THE INSIGHT:**
The 45-minute OLTP query vs 8-second OLAP query — on identical datasets — is entirely explained by physical storage layout. The SQL is identical. The hardware is similar. The storage format made a 300× difference.

---

### 🧠 Mental Model / Analogy

> Think of row-oriented storage as a filing cabinet of folders — each folder is one customer's complete record. Finding one customer's file is fast (one folder). Adding a new field means updating every folder. Columnar storage is a spreadsheet — every cell in the "Revenue" column is adjacent. Summing the entire revenue column reads one contiguous strip. Adding a new customer means a new entry at the end of every column, which is non-trivial.

**Mapping:**
- "Filing cabinet folder" → row-oriented page (all columns per row together)
- "Spreadsheet column" → columnar storage block (all values per column together)
- "Find one customer's folder" → OLTP point lookup (fast in row storage)
- "Sum all revenue cells" → OLAP aggregation (fast in columnar storage)

**Where this analogy breaks down:** Modern databases blur the line — some OLTP databases (PostgreSQL BRIN indexes, InnoDB buffer pool) cache frequently-scanned columns; HTAP databases (TiDB, CockroachDB) offer both modes simultaneously. The distinction is architectural preference, not an absolute wall.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
OLTP is the fast system that handles everyday transactions — placing an order, updating inventory. OLAP is the reporting system that analyses millions of transactions to find patterns — "how did sales perform last quarter?" They need different types of databases because a cash register and an accounting system are used in completely different ways.

**Level 2 — How to use it (junior developer):**
When building an application, you put transactional logic (inserts/updates/deletes for user actions) on an OLTP database (PostgreSQL, MySQL, Aurora). You set up a separate analytical pipeline that periodically syncs data to an OLAP warehouse (Snowflake, BigQuery) for reporting queries. Never run heavy analytical queries directly on your production OLTP database.

**Level 3 — How it works (mid-level engineer):**
The index design differs fundamentally. OLTP uses B-tree indexes on high-cardinality keys (customer_id, order_id) for O(log n) point lookups — an index on a 100M-row table adds only 3–4 disk seeks per query. OLAP uses zone maps (min/max per data block stored in metadata) to skip entire blocks — a query for `revenue_usd > 1000` can skip any block whose max < 1000 without reading it. OLAP also uses dictionary encoding (map "New York" → integer 42, then store integers) which compresses repetitive dimension values by 10–100×.

**Level 4 — Why it was designed this way (senior/staff):**
The distinction was first formalised by Edgar Codd in 1993 when he described OLAP as a separate category. Before this, all databases used row-oriented storage because the dominant workload was operational (OLTP). The explosion of business intelligence demand in the 1990s (Teradata, Sybase IQ) created the recognition that analytical workloads needed columnar, parallel architectures. Cloud computing enabled this separation to become economical for any organisation via on-demand compute (BigQuery, Athena → no idle compute cost). The ongoing tension: HTAP (Hybrid Transactional/Analytical Processing) databases (DuckDB, TiDB, SingleStore) attempt to serve both in one engine, accepting a compromise on each rather than optimising for either.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│ OLTP (ROW-ORIENTED STORAGE)                            │
│                                                        │
│ Table row layout in page:                              │
│  [cust_id|name|email|addr|revenue|status|created_at]  │
│  [cust_id|name|email|addr|revenue|status|created_at]  │
│  [cust_id|name|email|addr|revenue|status|created_at]  │
│                                                        │
│  Point lookup:  read one row → minimal I/O ✓          │
│  SUM(revenue):  must read ALL columns of ALL rows ✗   │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ OLAP (COLUMNAR STORAGE)                                │
│                                                        │
│ Column files on disk:                                  │
│  revenue_usd: [120.00][45.50][890.00][12.00]...       │
│  order_date:  [2024-01][2024-01][2024-02]...          │
│  product_id:  [P001][P002][P001][P003]...             │
│                                                        │
│  SUM(revenue WHERE date > 2024-01):                   │
│   → read only revenue_usd + order_date columns ✓      │
│   → all other columns never touched ✓                 │
│   → compressed: dict encode product_id (4B → 2 bits) ✓│
│  Point lookup (WHERE id = X):                         │
│   → must read column-by-column to reconstruct row ✗   │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
User action → OLTP (PostgreSQL) → operational row stored
           → ETL/ELT pipeline → [OLAP warehouse ← YOU ARE HERE]
           → analytical columnar tables → BI query returns in seconds
```

**FAILURE PATH:**
```
ETL pipeline fails → OLAP warehouse not updated
→ BI report shows yesterday's data
→ observable: row count / last_loaded_at check fails
→ no impact on OLTP operations (fully decoupled)
```

**WHAT CHANGES AT SCALE:**
At 10B+ rows in OLAP, partition pruning strategy becomes critical — a missed partition filter causes full-table scans. Snowflake's micro-partition metadata (16 MB blocks × millions of partitions) enables pruning to < 1% of data for well-filtered queries. At OLTP scale (100K TPS), row-lock contention in hot pages becomes the bottleneck — sharding by customer/region routes transactions to different partitions and eliminates hotspots.

---

### 💻 Code Example

Example 1 — OLTP: optimised for point operations (PostgreSQL):
```sql
-- OLTP: single-row insert (fast)
INSERT INTO orders (order_id, customer_id, product_id,
                    quantity, price_usd, status)
VALUES (gen_random_uuid(), 'C-1234', 'P-5678', 2, 49.99, 'PENDING');

-- OLTP: point lookup (B-tree index on order_id → O(log n))
SELECT * FROM orders WHERE order_id = 'abc-123';

-- Index for fast point reads
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status)
  WHERE status != 'COMPLETE';  -- partial index for active orders
```

Example 2 — OLAP: optimised for aggregation (Snowflake):
```sql
-- OLAP: aggregate across 800M rows (columnar — only reads 3 columns)
SELECT
    dp.category,
    dt.year,
    dt.month,
    SUM(fo.revenue_usd) AS total_revenue,
    COUNT(DISTINCT fo.customer_key) AS unique_customers
FROM fact_orders fo
JOIN dim_product dp ON fo.product_key = dp.product_key
JOIN dim_time    dt ON fo.time_key    = dt.time_key
WHERE dt.year = 2024
GROUP BY dp.category, dt.year, dt.month
ORDER BY total_revenue DESC;
-- Only revenue_usd, product_key, time_key, and dimension join columns
-- are read. All other columns in fact_orders are skipped.
```

---

### ⚖️ Comparison Table

| Dimension | OLTP | OLAP | HTAP |
|---|---|---|---|
| Workload | Transactions | Analytics | Both |
| Storage | Row-oriented | Columnar | Hybrid |
| Schema | Normalised (3NF) | Star/Snowflake | Mixed |
| Query latency | Milliseconds | Seconds–minutes | Seconds |
| Write speed | Very high | Low | Medium |
| Data freshness | Real-time | Minutes–hours lag | Near real-time |
| Examples | PostgreSQL, MySQL | Snowflake, BigQuery | TiDB, DuckDB |

**How to choose:** Always separate OLTP and OLAP workloads unless using a purpose-built HTAP engine. Running analytical queries on your OLTP production database is one of the most common and costly mistakes in data engineering. Use HTAP only when analytical latency of seconds is genuinely required alongside real-time transactional consistency — most BI use cases tolerate minutes of lag.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Adding more RAM fixes analytical query slowness in OLTP | The root cause is storage layout — columnar data is simply not in memory in the right format; RAM cannot fix a structural mismatch |
| Indexes make OLAP queries fast enough in OLTP | Indexes help for selective point queries; they do not help for `SUM(revenue)` across 80% of the table |
| OLAP warehouses can replace OLTP for operational queries | OLAP warehouses have write latency of seconds and lack row-level ACID for concurrent updates — they cannot handle 10K TPS of operational writes |
| HTAP eliminates the need for separation | HTAP engines make trade-offs on both sides — they are slower at OLTP and slower at OLAP than dedicated systems; justified only when both in one system is operationally essential |
| A read replica solves the OLTP/OLAP problem | Read replicas reduce write contention but do not change the storage format — analytical queries on a PostgreSQL read replica are still limited by row-oriented storage |

---

### 🚨 Failure Modes & Diagnosis

**Analytical Query on Production OLTP**

**Symptom:** Checkout latency spikes; database CPU at 100%; on-call alert fires; root cause: a BI dashboard scheduled query is scanning the production database.

**Diagnostic Command / Tool:**
```sql
-- PostgreSQL: find long-running queries
SELECT pid, now() - query_start AS duration,
       state, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > INTERVAL '30 seconds'
ORDER BY duration DESC;
-- Large duration + SELECT with no WHERE or GROUP BY → OLAP query
```

**Fix:** Kill the offending query (`SELECT pg_cancel_backend(pid)`). Move all analytical queries to a separate read replica or OLAP warehouse.

**Prevention:** Block queries with execution plan cost above threshold on production OLTP. Most BI tools can be configured to point at a read replica or warehouse instead of production.

---

**OLAP Warehouse Not Partitioned Correctly**

**Symptom:** Simple date-filtered query takes minutes; cost report shows 100 TB scanned for what should be 1 day of data.

**Diagnostic Command / Tool:**
```sql
-- Snowflake: check micro-partition pruning efficiency
SELECT query_id,
       partitions_total,
       partitions_scanned,
       bytes_scanned
FROM snowflake.account_usage.query_history
WHERE start_time > DATEADD(hour, -1, CURRENT_TIMESTAMP)
ORDER BY bytes_scanned DESC LIMIT 5;
-- partitions_scanned / partitions_total close to 1.0 = bad pruning
```

**Fix:** Ensure the WHERE clause uses the clustering key column. Re-cluster the table if access patterns changed.

**Prevention:** Define clustering keys aligned to the most frequent filter predicates at table creation time.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Columnar vs Row Storage` — the physical storage difference that defines OLTP vs OLAP performance
- `Database Fundamentals` — OLTP is the traditional operational database use case

**Builds On This (learn these next):**
- `Data Warehouse` — the standard OLAP architecture for business analytics
- `ETL vs ELT` — the pipeline that moves data from OLTP to OLAP systems

**Alternatives / Comparisons:**
- `HTAP (Hybrid Transactional/Analytical Processing)` — attempts both in one system
- `Data Lakehouse` — combines OLAP performance with lake-style raw storage

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two fundamentally different workloads:   │
│              │ row-level transactions vs bulk analytics  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Running analytics on OLTP systems        │
│ SOLVES       │ destroys transactional performance       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Storage layout (row vs columnar) is the  │
│              │ physical reason they cannot share a DB   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always: separate your transactional and  │
│              │ analytical workloads architecturally     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never mix them on one DB under load      │
│              │ (read replica is only a partial fix)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ OLTP: fast writes, slow scans           │
│              │ OLAP: fast scans, slow writes, data lag  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A cash register and an accountant's     │
│              │  ledger — same data, different tools"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Warehouse → ETL vs ELT →            │
│              │ Columnar vs Row Storage                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A startup is building a SaaS product. Their PostgreSQL database handles all user-facing transactional operations. The founders also want real-time analytics dashboards that show "total revenue today" and "active users last 30 minutes." They argue that adding a read replica of PostgreSQL is sufficient — no separate OLAP warehouse needed. Under what specific conditions is this argument correct, and at what exact threshold (row count, query frequency, latency requirement) does it become incorrect?

**Q2.** An HTAP database (TiDB) is proposed to replace both your PostgreSQL OLTP system and your Snowflake OLAP warehouse — "one database to rule them all." Construct the strongest possible argument against this proposal by identifying the specific workload characteristics of your system that would be degraded relative to purpose-built systems, and describe the production failure mode that would manifest first at 1M TPS OLTP + 50 concurrent heavy OLAP queries.

