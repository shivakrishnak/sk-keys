---
layout: default
title: "Partitioning (DB)"
parent: "Database Fundamentals"
nav_order: 440
permalink: /databases/partitioning/
number: "0440"
category: Database Fundamentals
difficulty: ★★★
depends_on: B+ Tree, Index Types, Query Planner
used_by: Database Sharding, Materialized View, Schema Evolution
related: Database Sharding, Index Types, Query Planner
tags:
  - database
  - scalability
  - performance
  - deep-dive
---

# 440 — Partitioning (DB)

⚡ TL;DR — Database partitioning splits a large table into smaller physical segments (partitions) based on a key — enabling partition pruning (query only relevant partitions), faster maintenance, and eventual horizontal scaling — while keeping a single logical table view.

| #440            | Category: Database Fundamentals                        | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | B+ Tree, Index Types, Query Planner                    |                 |
| **Used by:**    | Database Sharding, Materialized View, Schema Evolution |                 |
| **Related:**    | Database Sharding, Index Types, Query Planner          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A single `orders` table with 10 billion rows. Deleting last year's data: `DELETE FROM orders WHERE created_at < '2023-01-01'` — scans 10 billion rows, generates 10 billion WAL records, holds a massive lock, runs for hours. Meanwhile: VACUUM must process the entire 10-billion-row table. Indexes are huge (hundreds of GB), degrading query performance.

**THE BREAKING POINT:**
Tables grow unbounded. Maintenance operations (VACUUM, ANALYZE, index REBUILD) take increasingly long on large tables. A "hot" date range (recent orders) is queried constantly but is buried in 10 years of cold data sharing the same table files and indexes.

**THE INVENTION MOMENT:**
"Divide the table into physical segments by some key (date, region, type). Queries that filter on that key only touch relevant segments. Maintenance operates on one segment at a time. Old segments can be detached and archived instantly."

---

### 📘 Textbook Definition

**Database partitioning** is the division of a single logical table into multiple physical **partitions** (child tables/segments) based on a **partition key**. Partitioning types: **Range** (partitions by value range, e.g., by year or by ID range); **List** (partitions by discrete values, e.g., by country or status); **Hash** (partitions by hash of the key, distributing rows evenly). The query planner uses **partition pruning** to skip irrelevant partitions when a query's WHERE clause includes the partition key — turning a full table scan into a targeted scan of one or a few partitions. Partitioning exists within a single database server (vs. **sharding**, which distributes across multiple servers). It enables: partition-level maintenance (VACUUM/ANALYZE/REINDEX a partition independently), data lifecycle management (DROP old partitions in O(1) instead of DELETE), and parallelism (multiple partitions scanned in parallel).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Partitioning splits a big table into smaller physical slices — the database only reads the slices your query needs, and you can drop old slices instantly.

**One analogy:**

> A filing cabinet with millions of files, organized by year. Filing cabinet without partitions: everything in one pile — finding 2024 files means sifting through everything. Filing cabinet with partitions: each drawer is one year. When you need 2024 records, you open just that drawer. When you need to archive 2019, you remove that drawer entirely in seconds. The files are still "in the same filing system" — it just has physical sections.

- "Filing cabinet" → the logical table (single name, single schema)
- "Individual drawers" → physical partitions
- "Opening just one drawer" → partition pruning
- "Removing a drawer" → DROP PARTITION (instant, no row-by-row delete)
- "One pile" → unpartitioned table (full scan for any query)

**One insight:**
`DROP TABLE orders_2019` (a partition) is O(1) — it drops a file on disk. `DELETE FROM orders WHERE year=2019` is O(rows) — scans and deletes 365M rows one by one, generating billions of WAL records. Partitioning makes data lifecycle management the dominant practical reason for adoption, even when query performance is already acceptable.

---

### 🔩 First Principles Explanation

**POSTGRESQL DECLARATIVE PARTITIONING:**

```sql
-- Range partitioning by date (most common)
CREATE TABLE orders (
    id          BIGINT,
    customer_id BIGINT,
    amount      DECIMAL,
    created_at  TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Default partition (catches rows that don't fit others)
CREATE TABLE orders_other PARTITION OF orders DEFAULT;

-- Partition-level index (each partition has its own index)
CREATE INDEX ON orders_2024 (customer_id);
-- OR: index on parent propagates to all partitions:
CREATE INDEX ON orders (customer_id);  -- creates index on all partitions
```

**PARTITION PRUNING (the key performance mechanism):**

```sql
-- Query with partition key in WHERE: partition pruning occurs
EXPLAIN SELECT * FROM orders WHERE created_at >= '2024-01-01';
-- → Seq Scan on orders_2024 (only this partition scanned)
-- → orders_2023, orders_other: excluded by pruning

-- Query WITHOUT partition key: full scan ALL partitions
EXPLAIN SELECT * FROM orders WHERE customer_id = 42;
-- → Seq Scan on orders_2023 (scanned)
-- → Seq Scan on orders_2024 (scanned)
-- → orders_other (scanned)
-- No pruning! Must use index on customer_id across all partitions
```

**HASH PARTITIONING (even distribution):**

```sql
-- Hash by customer_id: distributes evenly
CREATE TABLE customers (
    id   BIGINT,
    name TEXT
) PARTITION BY HASH (id);

CREATE TABLE customers_p0 PARTITION OF customers
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE customers_p1 PARTITION OF customers
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- ... etc.
```

**LIST PARTITIONING:**

```sql
CREATE TABLE events (
    id     BIGINT,
    region TEXT,
    data   JSONB
) PARTITION BY LIST (region);

CREATE TABLE events_us   PARTITION OF events FOR VALUES IN ('US');
CREATE TABLE events_eu   PARTITION OF events FOR VALUES IN ('EU', 'UK');
CREATE TABLE events_apac PARTITION OF events FOR VALUES IN ('AU', 'JP', 'SG');
```

**THE TRADE-OFFS:**
**Gain:** Partition pruning (massive query speedup for partition-key queries), O(1) partition DROP for data lifecycle, per-partition maintenance, parallel scan of multiple partitions.
**Cost:** Partition key must appear in most queries (otherwise no pruning benefit — actually slower due to cross-partition overhead). Joins across partition keys fan out to all partitions. Indexes must be managed per partition (or globally with overhead). Cross-partition queries are more complex for the planner.

---

### 🧪 Thought Experiment

**SETUP:**
`events` table: 5 billion rows, partitioned by month (60 partitions × ~83M rows each). Query: `SELECT * FROM events WHERE event_time >= '2024-11-01' AND event_time < '2024-12-01'`.

**WITHOUT PARTITIONING:**

- 5 billion rows × 8KB page average → ~40 TB table
- Even with index on `event_time`: B+ Tree traversal + 83M qualifying rows → multiple GB of I/O
- VACUUM: must process all 5B rows periodically
- DELETE for old data: billions of row-by-row deletes

**WITH MONTHLY RANGE PARTITIONING:**

- Query: planner detects `event_time >= '2024-11-01' AND < '2024-12-01'` → exactly partition `events_2024_11`
- Partition pruning: 59 of 60 partitions excluded
- Query: scans only `events_2024_11` (~83M rows, ~666GB)
- Still a lot — add index on `event_id` WITHIN the partition: much faster
- VACUUM: only vacuums `events_2024_11` when needed
- Archive 2023: `ALTER TABLE events DETACH PARTITION events_2023_01` (instant) → `DROP TABLE events_2023_01` (instant)
- No row-by-row delete needed ever

**WRONG PARTITION KEY SCENARIO:**
Query: `SELECT * FROM events WHERE user_id = 42` (no partition key in WHERE)
→ Must scan ALL 60 partitions
→ 60 table scans in parallel (if `enable_parallel_append = on`)
→ More work than unpartitioned table with index on `user_id`
→ Lesson: partition key must match query patterns

---

### 🧠 Mental Model / Analogy

> Database partitioning is like organizing a warehouse by shipping zone. Before: every shipment in one giant pile — finding "shipments to Seattle" means inspecting the entire warehouse. After: shipping zones divide the warehouse into sections (partition by region). Finding Seattle shipments: go to the Northwest section only (partition pruning). Removing old shipments from 2020: empty and remove the "2020" section entirely (DROP PARTITION). The warehouse address is the same (logical table name), the sections are managed separately (physical partitions).

- "Warehouse address" → logical table name (application code unchanged)
- "Shipping zone sections" → partitions (physical storage segments)
- "Go to Northwest section only" → partition pruning
- "Remove 2020 section" → DROP PARTITION (instant file deletion)
- "Inspecting entire warehouse" → full scan when no partition key in WHERE

Where this analogy breaks down: Warehouse sections can be different sizes; in hash partitioning, the database ensures sections are equal size. In range partitioning, "hot" recent partitions may be larger than archived ones — plan partition sizes accordingly.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When a database table becomes too large (billions of rows), it gets slow and hard to maintain. Partitioning is like putting dividers in a binder — instead of flipping through the whole binder, you go to the right section. The database can skip irrelevant sections, and you can remove old sections instantly without affecting the rest.

**Level 2 — How to use it (junior developer):**
Choose a partition key that matches your most common query filter (usually `created_at` for time-series data, or `region`/`tenant_id` for multi-tenant). Range partition by month or year for time-series. Always include the partition key in your WHERE clauses — otherwise every partition gets scanned. Use `pg_partman` (PostgreSQL) for automated monthly partition creation and maintenance. Use `ALTER TABLE DETACH PARTITION` to archive old data, then `DROP TABLE` the detached partition.

**Level 3 — How it works (mid-level engineer):**
PostgreSQL declarative partitioning (v10+): the parent table is a logical container (no data stored directly). Child tables (partitions) store actual data. INSERT: routed to the correct partition via constraint check. SELECT: query planner examines partition constraints; if WHERE clause can exclude a partition (constraint exclusion), it's omitted from the plan. Partition pruning happens at plan time (static pruning) and at execution time (dynamic pruning, v11+) for parameterized queries. `enable_partition_pruning = on` (default). Check pruning in EXPLAIN: look for `Partitions: 1 out of 60` — means 59 pruned. `pg_partman` automates: creating future partitions, dropping/detaching old partitions based on retention policy, maintenance scheduling. Sub-partitioning: partition by year, then sub-partition by region — can be 2-3 levels deep.

**Level 4 — Why it was designed this way (senior/staff):**
Partitioning is a single-server scaling technique — it improves operational characteristics but doesn't distribute load across servers. The design principle: keep a logical table view for application simplicity while gaining physical segmentation benefits. The key distinction from sharding: sharding distributes across multiple servers (true horizontal scale for writes); partitioning segments within one server (operational and read-path benefits only). Modern partitioning in PostgreSQL evolved from constraint exclusion (unreliable, table-inheritance-based) to declarative partitioning (v10, clean semantics) to native partition pruning (v11-12, including runtime pruning). The Citus extension (now part of Azure Cosmos DB for PostgreSQL) extends PostgreSQL's partitioning model to distribute partitions across multiple nodes — essentially making PostgreSQL's partitioning the foundation for distributed sharding. This architectural continuity means: a partitioned PostgreSQL schema can be migrated to distributed Citus without application schema changes — only the distribution key configuration changes. This is the correct path: partition first (for operational benefits), then shard (for write scale) only when partitioning is insufficient.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PARTITIONING: QUERY EXECUTION WITH PRUNING           │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Logical table: orders (partitioned by created_at)    │
│                                                      │
│ Physical partitions:                                 │
│  orders_2022 [Jan 2022 → Jan 2023]                   │
│  orders_2023 [Jan 2023 → Jan 2024]                   │
│  orders_2024 [Jan 2024 → Jan 2025]  ← current       │
│  orders_2025 [Jan 2025 → Jan 2026]  ← future (empty)│
│                                                      │
│ Query: WHERE created_at >= '2024-06-01'              │
│        AND created_at < '2024-07-01'                 │
│                                                      │
│ Planner: checks partition constraints                │
│  orders_2022: constraint [Jan22,Jan23) → doesn't     │
│              overlap [Jun24,Jul24) → PRUNED          │
│  orders_2023: PRUNED (same reason)                   │
│  orders_2024: overlaps [Jun24,Jul24) → SCANNED       │
│  orders_2025: constraint [Jan25,...) → PRUNED        │
│                                                      │
│ Result: Seq Scan on orders_2024 only                 │
│ Plan output: "Partitions: 1 out of 4"                │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Application inserts record: INSERT INTO orders (created_at='2024-06-15')
→ PostgreSQL: check which partition's constraint matches 2024-06-15
→ Route INSERT to orders_2024 (Jan 2024 → Jan 2025 range)
→ Row stored in orders_2024's physical file

Application queries: SELECT WHERE created_at BETWEEN '2024-06-01' AND '2024-07-01'
→ Planner: evaluates partition constraints
→ [PARTITIONING ← YOU ARE HERE: partition pruning]
→ Only orders_2024 satisfies the range → scan orders_2024 only
→ 59× less data to scan vs. unpartitioned
```

**FAILURE PATH — No Partition Key in Query:**

```
Application queries: SELECT * FROM orders WHERE customer_id = 42
→ customer_id is NOT the partition key
→ No partition pruning possible
→ Planner: must scan ALL partitions
→ For 60 monthly partitions: 60 parallel table scans
→ More complex plan + more overhead than unpartitioned table with index
→ Fix: add index on customer_id on the partitioned table
       OR ensure customer_id queries also filter on created_at (partition key)
```

**WHAT CHANGES AT SCALE:**
At 100B rows: partitioning enables monthly partitions of ~833M rows each — manageable. Archive partitions by month: `DETACH + DROP` — instant. Monthly `VACUUM ANALYZE` on new partition only: fast. With Citus: distribute partitions across nodes for write scaling. AWS Aurora: partitioned PostgreSQL tables benefit from Aurora's parallel query across partitions.

---

### ⚖️ Comparison Table

| Partitioning Type | Key Characteristic              | Pruning Condition           | Best For                                |
| ----------------- | ------------------------------- | --------------------------- | --------------------------------------- |
| **Range**         | Partitions by value range       | `WHERE key BETWEEN a AND b` | Time-series, sequential IDs             |
| **List**          | Partitions by enumerated values | `WHERE key IN ('A','B')`    | Region, tenant, category                |
| **Hash**          | Even distribution by hash       | Rarely pruned               | Evenly distributed key, no range needed |
| **Composite**     | Range + List (sub-partition)    | Both keys                   | Large multi-dimensional data            |

Partitioning vs. Sharding:
| | Partitioning | Sharding |
|---|---|---|
| Location | Single database server | Multiple database servers |
| Write scaling | No | Yes |
| Query routing | In-DB (transparent) | Application/proxy layer |
| Operational complexity | Low | High |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                  |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Partitioning automatically speeds up all queries | Only queries that include the partition key in WHERE benefit from pruning; queries without the partition key scan ALL partitions — potentially slower than unpartitioned |
| Partitioning replaces indexes                    | Partitioning and indexes are complementary; partition pruning eliminates irrelevant partitions; indexes speed up lookups within a partition                              |
| Partitioning and sharding are the same           | Partitioning = physical segmentation on ONE server; sharding = distribution across MULTIPLE servers. Partitioning doesn't scale writes                                   |
| DROP PARTITION is dangerous                      | Dropping a partition is instantaneous (file deletion) and doesn't affect other partitions; it's safer and faster than DELETE for data lifecycle management               |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing Partitions Causing INSERT Failure**

**Symptom:** `ERROR: no partition of relation "orders" found for row` — inserts fail for future dates when the partition doesn't exist yet.

**Root Cause:** Range-partitioned table has no partition covering the value being inserted (e.g., inserting January 2026 data when the latest partition only covers through December 2025).

**Diagnostic:**

```sql
-- Check existing partition ranges
SELECT child.relname, pg_get_expr(child.relpartbound, child.oid)
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'orders'
ORDER BY child.relname;

-- If future partition missing: create it
CREATE TABLE orders_2026 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

**Fix (immediate):** Create the missing partition. **Fix (long-term):** Use `pg_partman` to automatically create future partitions in advance. Set `premake = 3` — creates 3 future partitions ahead of current period.

**Prevention:** Always have a DEFAULT partition as a safety net: `CREATE TABLE orders_other PARTITION OF orders DEFAULT`. This catches any row that doesn't fit a specific partition and prevents insert failures (though it may indicate a misconfiguration).

---

**2. No Partition Pruning — Full Table Scan Across All Partitions**

**Symptom:** EXPLAIN shows all partitions being scanned even when you expect pruning; query is not faster than before partitioning.

**Root Cause:** Query doesn't include the partition key in WHERE, or partition key is inside a function call/cast that prevents constraint exclusion.

**Diagnostic:**

```sql
-- Check EXPLAIN for partition pruning
EXPLAIN SELECT * FROM orders WHERE DATE_TRUNC('month', created_at) = '2024-06-01';
-- Problem: DATE_TRUNC wraps the partition key → pruning impossible
-- Result: all partitions scanned

-- Fix: rewrite without function on partition key
EXPLAIN SELECT * FROM orders
WHERE created_at >= '2024-06-01' AND created_at < '2024-07-01';
-- Pruning works: scans only the June partition
```

**Fix:** Rewrite queries to use the partition key directly in range conditions. Avoid functions wrapping the partition key (same rule as indexes: no function on the indexed/partitioned column in WHERE).

**Prevention:** Test new queries with EXPLAIN ANALYZE, verifying "Partitions: N out of M" shows effective pruning. Document: partition key must appear bare (no function wrapping) in WHERE for pruning to work.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `B+ Tree` — partitions have their own B+ Tree indexes
- `Index Types` — partition pruning and index usage work together; understand both
- `Query Planner / Execution Plan` — the planner drives partition pruning; EXPLAIN reveals pruning

**Builds On This (learn these next):**

- `Database Sharding` — partitioning is a prerequisite concept; sharding extends it to multiple servers
- `Materialized View` — materialized views can be built on specific partitions
- `Schema Evolution` — adding partitions or changing partition key requires careful schema evolution

**Alternatives / Comparisons:**

- `Database Sharding` — for write-scale horizontal distribution; partitioning stays on one server
- `Index Types` — covering index for small-to-medium tables vs. partitioning for large tables

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TYPES        │ Range (by date/ID) — most common          │
│              │ List (by enum: region, type)              │
│              │ Hash (even distribution)                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFIT  │ Partition pruning (scan only relevant)    │
│              │ DROP PARTITION = instant data lifecycle   │
│              │ Per-partition VACUUM / ANALYZE            │
├──────────────┼───────────────────────────────────────────┤
│ PRUNING RULE │ WHERE clause must contain partition key   │
│              │ bare (no function wrapping)               │
├──────────────┼───────────────────────────────────────────┤
│ AUTOMATION   │ pg_partman: auto-create future partitions │
│              │ premake=3: keep 3 ahead                   │
├──────────────┼───────────────────────────────────────────┤
│ ≠ SHARDING   │ Partitioning = 1 server, physical split   │
│              │ Sharding = many servers, network split    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Divide the table by key; query only the  │
│              │  slices you need; drop old slices in O(1)"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Database Sharding → Materialized View     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design the partitioning strategy for a multi-tenant SaaS application: `events` table with columns `tenant_id`, `event_time`, `user_id`, `event_type`, `payload`. The application has 1,000 tenants; most queries filter by both `tenant_id` AND `event_time`; data retention is 90 days per tenant; each tenant generates ~10,000 events/day. Compare: (a) partition by `event_time` (monthly), (b) partition by `tenant_id` (hash or list), (c) sub-partition by `tenant_id` within monthly partitions. Analyze query performance, data lifecycle management, and operational complexity for each.

**Q2.** (TYPE E — Optimization) A partitioned `orders` table (monthly range, 36 partitions) is experiencing slow queries for: `SELECT SUM(amount) FROM orders WHERE customer_id = 42`. EXPLAIN shows all 36 partitions being scanned. The `customer_id` index exists on the parent table. Propose three optimizations: one at the query level, one at the schema level, and one at the partitioning strategy level. Analyze their relative impact and trade-offs.
