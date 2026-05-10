---
version: 2
layout: default
title: "Query Optimization"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /databases/query-optimization/
id: DBF-008
category: Database Fundamentals
difficulty: ★★★
depends_on: SQL, Indexing, Complex SQL Queries
used_by: Database Fundamentals, NoSQL & Distributed Databases
related: Execution Plan, Index Design, Partitioning
tags:
  - database
  - performance
  - advanced
  - production
---

# DBF-008 - Query Optimization

⚡ TL;DR - Query optimization transforms a SQL statement into the fastest physical execution plan by choosing join order, access paths, and algorithms based on table statistics.

| Field        | Value |
|--------------|-------|
| Depends on   | SQL, Indexing, Complex SQL Queries |
| Used by      | Database Fundamentals, NoSQL & Distributed Databases |
| Related      | Execution Plan, Index Design, Partitioning |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** In the earliest database systems, the programmer specified the access path explicitly - "scan this file, then that one, merge on this field." The query language described HOW to retrieve data, not WHAT data to retrieve. A change in table size or index structure required rewriting the application.

**THE BREAKING POINT:** A query joining four tables has 24 possible join orderings, three join algorithm choices per join, and two access path choices per table - over 1,000 candidate plans. A human cannot evaluate these at runtime. A 10-table join has over 3.6 million orderings.

**THE INVENTION MOMENT:** IBM's System R (1976) introduced the cost-based optimizer (CBO): a component that uses statistics about table sizes, column distributions, and available indexes to assign a cost estimate to each candidate plan and select the cheapest one automatically.

---

### 📘 Textbook Definition

**Query optimization** is the process by which a database management system transforms a declarative SQL statement into an efficient physical execution plan. The optimizer performs logical rewrites (predicate pushdown, subquery unnesting, join reordering) and then selects physical operators (index scan vs full table scan, hash join vs nested loop) using a cost model fed by table statistics (row counts, column histograms, NDV - number of distinct values).

---

### ⏱️ Understand It in 30 Seconds

**One line:** The optimizer is a compiler for SQL - it translates "what you want" into "the fastest way to get it" using statistics and cost models.

> Imagine planning a road trip across five cities. You can visit them in any order. A GPS navigator (optimizer) considers traffic data (statistics), road types (indexes), and fuel cost (I/O cost) to automatically find the shortest total route - without you specifying each turn.

**One insight:** The optimizer can only be as good as the statistics it has. Stale or missing statistics are the single most common cause of catastrophically bad query plans in production.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. SQL is declarative - the optimizer is free to choose any plan that produces the correct result set.
2. Cost = estimated I/O + CPU; the optimizer minimizes cost, not response time directly.
3. Cardinality estimates (row counts at each plan node) drive everything - wrong estimates propagate and amplify errors downstream.
4. Join ordering is NP-hard for N > ~8 tables; optimizers use heuristics (dynamic programming, genetic algorithms) for large queries.

**DERIVED DESIGN:**
- **Statistics:** Table row counts, column histograms, and index statistics - gathered by `ANALYZE` (PostgreSQL), `DBMS_STATS` (Oracle), or `UPDATE STATISTICS` (SQL Server).
- **Predicate pushdown:** Move WHERE filters as close to the data source as possible to reduce row counts early.
- **Subquery unnesting:** Convert correlated subqueries to joins - allowing join reordering and algorithm selection.
- **Cost model:** I/O cost (page reads) + CPU cost (comparisons, hash computations) weighted by `seq_page_cost`, `random_page_cost`, etc.

**THE TRADE-OFFS:**

**Gain:** Automatically adapts to changing data distributions; human engineers don't need to encode access paths; minor schema changes don't require application rewrites.

**Cost:** Optimizer can make wrong choices with stale statistics, complex expressions, or skewed data; execution plans can change without code changes ("plan flip"); debugging requires reading EXPLAIN output, which is a skill in itself.

---

### 🧪 Thought Experiment

**SETUP:** Table `orders` has 100 million rows. Table `customers` has 10,000 rows. Query joins them on `customer_id` with a filter `WHERE c.region = 'EU'` (which matches 500 customers).

**WITHOUT QUERY OPTIMIZATION:** The database reads all 100 million `orders` rows, reads all 10,000 `customers` rows, and does a Cartesian merge - 1 trillion row comparisons.

**WITH QUERY OPTIMIZATION:**
1. Optimizer sees: `customers` filtered to ~500 rows (small).
2. Builds hash table on 500 customer IDs (tiny).
3. Scans `orders` once, probing the hash table for each row.
4. Total: 100M comparisons (not 1 trillion) - 10,000× faster.

**THE INSIGHT:** Join ordering matters enormously. Always apply the most selective filter first to minimize the number of rows flowing through subsequent operators.

---

### 🧠 Mental Model / Analogy

> The optimizer is like a logistics manager who receives an order: "deliver packages to 5 warehouses, pick up returns, and stop at the supplier." They consult traffic reports (statistics), evaluate possible routes (candidate plans), estimate total driving time (cost), and dispatch the driver on the cheapest route - all before the truck leaves the depot.

- **Order from customer** = SQL query
- **Traffic reports** = table statistics / histograms
- **Route options** = candidate execution plans
- **Estimated driving time** = cost estimate
- **Chosen route** = physical execution plan
- **Driver** = query executor

Where this analogy breaks down: A logistics manager can reroute mid-trip; the optimizer commits to a plan before execution begins (though some databases support adaptive query execution that revises mid-run).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The database automatically figures out the fastest way to run your query. You don't tell it which files to read first - it decides based on how much data exists in each table.

**Level 2 - How to use it (junior developer):**
Run `EXPLAIN` before your query to see the plan. Look for "Seq Scan" on large tables (bad if an index exists). Look for row estimates that are wildly wrong. Run `ANALYZE tablename;` to refresh statistics if they look stale.

**Level 3 - How it works (mid-level engineer):**
The optimizer has three phases: (1) parsing to logical plan, (2) logical plan rewrites (predicate pushdown, subquery unnesting, join elimination), (3) physical plan selection (access path + join algorithm + sort strategy). Statistics include: `n_distinct` (cardinality), histograms (value distribution), correlation (physical ordering). PostgreSQL's planner uses dynamic programming for ≤8 tables; above that, it switches to a genetic algorithm (GEQO). Cost parameters (`seq_page_cost`, `random_page_cost`, `cpu_tuple_cost`) are configurable to match actual hardware.

**Level 4 - Why it was designed this way (senior/staff):**
The cost model deliberately simplifies: it assumes column value independence (no correlation between columns), uniform distribution within histogram buckets, and no data skew. These assumptions fail for correlated predicates (`WHERE city = 'London' AND country = 'UK'`) and skewed data. Modern databases address this with multi-column statistics (PostgreSQL: `CREATE STATISTICS`), extended statistics, and adaptive query execution (SQL Server 2017+, Oracle's Adaptive Plans). Cardinality estimation errors compound at each join - a 2× overestimate at three joins becomes an 8× error. This is why hints (`/*+ HASH_JOIN(orders) */`) exist as escape hatches when the optimizer fails.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│         Query Optimizer Pipeline             │
│                                              │
│  SQL Text                                    │
│    │                                         │
│    ▼                                         │
│  Parser → Logical Plan Tree                  │
│    │                                         │
│    ▼                                         │
│  Rewriter:                                   │
│    • Predicate pushdown                      │
│    • Subquery → semi-join                    │
│    • View expansion                          │
│    │                                         │
│    ▼                                         │
│  Planner:                                    │
│    • Generate candidate plans                │
│    • Cost each with statistics               │
│    • Select minimum cost plan                │
│    │                                         │
│    ▼                                         │
│  Physical Plan → Executor                    │
└──────────────────────────────────────────────┘
```

**Index type selection heuristics:**
```
B-tree:  equality + range; default for most queries
Hash:    equality only; no range; PostgreSQL, MySQL
BRIN:    naturally ordered large tables (time series)
GIN:     full-text, JSONB, array containment
GiST:    geometric, range type, full-text (alt)
Partial: WHERE clause on index; skips NULLs
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Developer writes SQL
  │
  ▼
Parser: syntax check, resolve names
  │
  ▼
Statistics consulted: pg_statistic, dba_tab_col_stats
  │
  ▼
Logical rewrites applied
       ← YOU ARE HERE
  │
  ▼
Candidate physical plans generated
  │
  ▼
Cost estimates computed per plan
  │
  ▼
Cheapest plan selected → Executor runs it
  │
  ▼
Result rows returned to client
```

**FAILURE PATH:**
- **Plan flip:** Statistics update causes optimizer to switch from index scan to seq scan. Queries that ran in 10ms now take 30s. Solution: `pg_hint_plan` (PostgreSQL) or optimizer hints to stabilize.
- **Stale statistics:** No `ANALYZE` after a large bulk load. Optimizer thinks table has 1,000 rows; it actually has 10 million. Seq scan selected; nested loop chosen for huge table.
- **Parameter sniffing (SQL Server):** Stored procedure compiled with atypical parameter values; cached plan is catastrophic for typical values.

**WHAT CHANGES AT SCALE:**
- Distributed query optimizers (Redshift, BigQuery, Presto) must account for network shuffle cost. Broadcast-small-table vs redistribute-large-table is the dominant trade-off.
- Partition pruning: the optimizer eliminates entire partitions from the scan based on predicates. A query with `WHERE order_date = '2024-01-01'` on a date-partitioned table reads one partition instead of all.

---

### 💻 Code Example

**Reading EXPLAIN ANALYZE output (PostgreSQL):**
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT c.name, SUM(o.amount)
FROM   customers c
JOIN   orders o ON o.customer_id = c.id
WHERE  c.region = 'EU'
GROUP  BY c.name;

-- Sample output:
-- HashAggregate (cost=12450.00..12460.00 rows=500)
--   -> Hash Join (cost=150.00..12000.00 rows=18000)
--        Hash Cond: (o.customer_id = c.id)
--        -> Seq Scan on orders (rows=1000000)
--        -> Hash (rows=500)
--             -> Index Scan on customers
--                  Index Cond: (region='EU')
--                  Rows Removed by Filter: 9500
```

**BAD - query without index; full scan:**
```sql
-- BAD: no index on region; scans all customers
SELECT * FROM customers WHERE region = 'EU';
-- EXPLAIN shows: Seq Scan on customers
--   Filter: (region = 'EU')
--   Rows Removed by Filter: 9500
```

**GOOD - create index, refresh stats:**
```sql
-- GOOD: add index for selective filter
CREATE INDEX idx_customers_region
ON customers (region);

-- Refresh statistics after bulk load
ANALYZE customers;

-- Now EXPLAIN shows:
-- Index Scan using idx_customers_region on customers
--   Index Cond: (region = 'EU')
```

**Multi-column statistics for correlated columns:**
```sql
-- PostgreSQL: correlated predicates underestimate rows
-- without extended statistics
CREATE STATISTICS stat_city_country
  ON city, country
  FROM customers;

ANALYZE customers;
-- Optimizer now accounts for city/country correlation
```

**Force join order with hint (Oracle):**
```sql
-- When optimizer chooses wrong join order
SELECT /*+ LEADING(c o) USE_HASH(o) */
  c.name, SUM(o.amount)
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE c.region = 'EU'
GROUP BY c.name;
```

---

### ⚖️ Comparison Table

| Optimizer Feature | PostgreSQL | Oracle | MySQL (8+) | SQL Server |
|---|---|---|---|---|
| Statistics refresh | ANALYZE | DBMS_STATS | ANALYZE TABLE | UPDATE STATISTICS |
| Histogram type | MCV + equi-depth | Endpoint + frequency | Equi-height | Equi-height + frequency |
| Multi-column stats | CREATE STATISTICS | Column groups (11g+) | No | No (single-col) |
| Adaptive execution | Memoize (15+) | Adaptive Plans (12c) | No | Adaptive Joins (2017+) |
| Hint syntax | pg_hint_plan (ext) | /*+ HINT */ | STRAIGHT_JOIN | WITH (INDEX=...) |
| Parallel query | Parallel Seq Scan | Parallel Query | Limited | Parallel Scan |
| Partition pruning | Yes | Yes | Yes | Yes |
| Plan caching | Prepared statements | Shared pool | Query cache (removed 8.0) | Plan cache |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Adding more indexes always speeds up queries" | Index maintenance slows INSERT/UPDATE/DELETE. The optimizer may still prefer a sequential scan if selectivity is low. Index bloat wastes buffer cache. |
| "EXPLAIN shows the actual query plan" | `EXPLAIN` without `ANALYZE` shows the *estimated* plan - what the optimizer *thinks* it will do, before execution. `EXPLAIN ANALYZE` runs the query and shows actual rows and timing. |
| "The optimizer always picks the best plan" | The optimizer minimizes *estimated* cost based on statistics. Wrong statistics = wrong plan. The "best" plan is only as good as the data model the optimizer uses. |
| "SELECT * is fine for debugging" | Even for debugging, SELECT * forces the engine to fetch all columns - bypassing index-only scans and increasing I/O. At scale it trains bad habits. |
| "Query hints are the solution to slow queries" | Hints are escape hatches for optimizer failures, not a first resort. They are fragile (break on schema changes) and mask the root cause. Fix statistics or indexes first. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Stale Statistics Causing Full Table Scan**

**Symptom:** A query that uses an index in staging runs 100× slower in production (full scan). Estimated row count in EXPLAIN is wildly wrong.

**Root Cause:** A large bulk load was done without running ANALYZE. Statistics still reflect the old row count.

**Diagnostic:**
```sql
-- PostgreSQL: check stats freshness
SELECT schemaname, tablename,
       n_live_tup, last_analyze, last_autoanalyze
FROM   pg_stat_user_tables
WHERE  tablename = 'orders';

-- Oracle: check stale statistics
SELECT table_name, num_rows, last_analyzed
FROM   dba_tab_statistics
WHERE  stale_stats = 'YES';
```

**Fix:**
```sql
-- PostgreSQL
ANALYZE orders;

-- Oracle
EXEC DBMS_STATS.GATHER_TABLE_STATS('schema', 'orders',
  cascade => TRUE);
```

**Prevention:** Run ANALYZE as part of any bulk load pipeline. Enable autovacuum/auto-stats in development and staging environments.

---

**Mode 2: Nested Loop Join on Large Tables**

**Symptom:** Join between two large tables takes minutes; EXPLAIN shows nested loop with millions of iterations.

**Root Cause:** Optimizer estimated one table as small (wrong cardinality); chose nested loop. Actual row count is large; nested loop degrades to O(n×m).

**Diagnostic:**
```sql
-- PostgreSQL: compare estimated vs actual
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM orders o JOIN shipments s
ON s.order_id = o.id;
-- Look for: "Plan Rows" vs "Actual Rows" discrepancy
-- on the inner side of a Nested Loop node
```

**Fix:**
```sql
-- Force hash join (PostgreSQL)
SET enable_nestloop = off;  -- session-level, temporary

-- Or use hint (pg_hint_plan extension)
/*+ HashJoin(o s) */ SELECT ...
```

**Prevention:** Run `ANALYZE` after large loads. Create multi-column statistics for correlated columns that affect cardinality estimates.

---

**Mode 3: Missing Index on Foreign Key (MySQL/PostgreSQL)**

**Symptom:** `DELETE FROM customers WHERE id = 5` takes 30 seconds. `EXPLAIN` shows full scan on `orders`.

**Root Cause:** On DELETE of a parent row, the database must check child rows for FK constraint. Without an index on `orders.customer_id`, it does a full table scan of `orders` for every deleted customer row.

**Diagnostic:**
```sql
-- PostgreSQL: find FK columns without indexes
SELECT c.conname, c.conrelid::regclass AS table,
       a.attname AS fk_column
FROM   pg_constraint c
JOIN   pg_attribute a ON a.attrelid = c.conrelid
  AND  a.attnum = ANY(c.conkey)
WHERE  c.contype = 'f'
AND    NOT EXISTS (
  SELECT 1 FROM pg_index i
  WHERE i.indrelid = c.conrelid
  AND   a.attnum = ANY(i.indkey)
);
```

**Fix:**
```sql
CREATE INDEX idx_orders_customer_id
ON orders (customer_id);
```

**Prevention:** Automatically create indexes on all FK columns as a schema design rule.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- SQL - the language the optimizer operates on
- Indexing - the primary performance lever the optimizer exploits
- Complex SQL Queries - the join/subquery patterns the optimizer rewrites

**Builds On This (learn these next):**
- Execution Plan - reading EXPLAIN output; identifying bottlenecks
- Index Design - choosing the right index type and column order
- Partitioning - partition pruning as an optimizer shortcut

**Alternatives / Comparisons:**
- Materialized Views - pre-compute expensive query results to avoid optimization at query time
- Query Hints - override optimizer decisions when they fail
- Columnar Stores - fundamentally different data layout; different optimizer assumptions

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════╗
║ WHAT IT IS     Automatic SQL plan selection ║
║ PROBLEM SOLVED 10-table join has 3.6M plans;║
║                humans can't choose manually ║
║ KEY INSIGHT    Statistics quality = plan    ║
║                quality; stale stats = fire  ║
║ USE WHEN       Always on (it's automatic);  ║
║                tune via ANALYZE + indexes   ║
║ AVOID WHEN     Never avoid; tune instead;  ║
║                hints are last resort        ║
║ TRADE-OFF      Automatic vs predictable;   ║
║                plan flips are real risk     ║
║ ONE-LINER      EXPLAIN ANALYZE first;      ║
║                then fix stats or indexes    ║
║ NEXT EXPLORE   Execution Plan, BRIN, GIN   ║
╚══════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(D - Root Cause)** A query runs in 50ms for most parameter values but takes 45 seconds for one specific value. The table has an index on the filtered column. EXPLAIN shows the index is used for the fast case but a seq scan for the slow case. What does this tell you about the data distribution, and what database mechanism (short of hints) could make the optimizer choose consistently?

2. **(B - Scale)** You have a distributed SQL database (e.g., CockroachDB) joining a 100GB table and a 1MB lookup table across 10 nodes. Compare the cost model considerations between (a) broadcasting the 1MB table to all 10 nodes and (b) shuffling the 100GB table by join key. When does each strategy win?

3. **(C - Design Trade-off)** PostgreSQL's GEQO (genetic algorithm) kicks in for queries with more than 8 tables in a join. The resulting plan may not be globally optimal. What are the practical consequences of this trade-off in a data warehouse with 15-table star schema queries, and what schema design pattern reduces the join count?
