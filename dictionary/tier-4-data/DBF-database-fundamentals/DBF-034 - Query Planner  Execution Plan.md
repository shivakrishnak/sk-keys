---
version: 1
layout: default
title: "Query Planner  Execution Plan"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 34
permalink: /databases/query-planner/
id: DBF-034
category: Database Fundamentals
difficulty: ★★★
depends_on: Index Types, B+ Tree, EXPLAIN
used_by: EXPLAIN, Query Optimization, Index Design
related: EXPLAIN, Index Types, Statistics
tags:
  - database
  - query-optimization
  - internals
  - deep-dive
---

# DBF-034 - Query Planner  Execution Plan

⚡ TL;DR - The query planner is the database's optimizer: it takes your SQL, enumerates possible execution strategies (scan types, join algorithms, index choices), estimates costs using statistics, and picks the lowest-cost plan - which may not be what you expected.

| #429            | Category: Database Fundamentals           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | Index Types, B+ Tree, EXPLAIN             |                 |
| **Used by:**    | EXPLAIN, Query Optimization, Index Design |                 |
| **Related:**    | EXPLAIN, Index Types, Statistics          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In early databases, the developer was responsible for writing queries that explicitly specified which index to use, in what order to join tables, and how to scan data. A query joining 4 tables has 24 possible join orderings × multiple algorithms per join × multiple scan types = hundreds of possible plans. Picking the wrong one could be 1000× slower than the optimal. Developers spent enormous time on manual query tuning.

**THE BREAKING POINT:**
The combinatorial space of query plans grows factorially with the number of joined tables. Even expert developers cannot manually evaluate all options for complex queries. And the optimal plan changes as data distribution changes - a plan that was optimal at table size 1M may be suboptimal at 100M.

**THE INVENTION MOMENT:**
"The database should automatically choose the optimal execution plan based on data statistics."

---

### 📘 Textbook Definition

The **query planner** (also called the query optimizer) is the component of a database engine that transforms a parsed SQL query into an **execution plan** - a tree of physical operations (scan, join, sort, aggregate) that implements the query's semantics. The planner uses: (1) **statistics** (`pg_statistic`, `innodb_stats`) - row counts, column value distributions, histogram of values; (2) **cost models** - formulas estimating disk I/O, CPU cost, and memory for each operation; (3) **enumeration** - trying possible plan combinations (join order, join algorithm, scan method). It selects the plan with the lowest estimated total cost. The **execution engine** then executes the chosen plan. A wrong plan (due to stale statistics or poor cardinality estimation) is a leading cause of unexpectedly slow queries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The query planner is the database's travel optimizer - given your destination (SQL result), it finds the fastest route (execution plan) using maps (statistics) and cost estimates.

**One analogy:**

> Google Maps for a query. You say "get me from A to B" (SQL query). Google Maps (query planner) considers: driving (sequential scan), taking the highway (index scan), taking the subway (index-only scan). It picks based on traffic data (statistics), distance (row count), and estimated time (cost). Sometimes it picks wrong if the traffic data is outdated (stale statistics). You can override it manually (hints) but usually it's right.

**One insight:**
The planner's cost estimates are only as good as its statistics. If `ANALYZE` was never run, or if data distribution has skewed (e.g., 90% of orders have status='COMPLETED'), the planner may choose the wrong plan. Stale statistics → wrong cardinality estimates → wrong plan → slow queries.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The planner selects the _estimated_ cheapest plan, not necessarily the _actual_ cheapest - estimates can be wrong.
2. Plan quality degrades with table correlation (related columns that statistics don't capture), data skew, and stale statistics.
3. The planner enumerates plans up to `join_collapse_limit` (PostgreSQL default: 8 joins) - above this, it uses genetic algorithms to avoid combinatorial explosion.
4. A plan is a tree of nodes; each node has an "estimated cost" (startup cost, total cost) and "estimated rows."

**PLAN NODE TYPES (PostgreSQL):**

- **Seq Scan:** Read all rows of a table sequentially. Cost: O(n pages).
- **Index Scan:** Traverse B+ Tree to find matching TIDs, then fetch from heap. Cost: O(log n + k heap fetches).
- **Index Only Scan:** Traverse B+ Tree, return results directly from index leaf (no heap fetch). Requires covering index + visible visibility map.
- **Bitmap Index Scan + Bitmap Heap Scan:** When multiple indexes are available, collect TIDs into a bitmap (eliminating duplicates), then fetch heap pages in order (minimizing random I/O).
- **Nested Loop Join:** For each row of outer table, probe inner table. Cost: O(outer_rows × inner_lookup_cost). Best for small outer tables with indexed inner.
- **Hash Join:** Build hash table of smaller relation, probe with larger. Cost: O(n+m). Best for large tables with no useful index on join key.
- **Merge Join:** Sort both relations on join key, then merge. Cost: O(n log n + m log m). Best when both relations are pre-sorted.
- **Sort:** Order rows by key. Cost: O(n log n).
- **Aggregate / HashAggregate / GroupAggregate:** Compute aggregates (COUNT, SUM, GROUP BY).

**COST MODEL:**
Each operation's cost is estimated as:

```
cost = disk_pages × seq_page_cost + heap_fetches × random_page_cost + rows × cpu_tuple_cost
```

- `seq_page_cost` = 1.0 (baseline)
- `random_page_cost` = 4.0 (default; should be 1.1 for NVMe SSD)
- `cpu_tuple_cost` = 0.01

**THE TRADE-OFFS:**
Planning time vs. execution time: complex queries with many joins require more planning time (exhaustive enumeration). Above ~8 joins, PostgreSQL switches to genetic query optimization (GEQO) - faster planning but may miss the optimal plan. Very complex OLAP queries sometimes benefit from `join_collapse_limit = 1` (preserve the join order as written) when the developer knows the optimal order.

---

### 🧪 Thought Experiment

**SETUP:**
Table: `orders(id, customer_id, status, amount, created_at)`, 100M rows. Status distribution: 95% 'COMPLETED', 5% 'PENDING'. Index: `idx_orders_status ON (status)`.

**SCENARIO A - Planner with correct statistics:**
Query: `SELECT * FROM orders WHERE status = 'PENDING'`

- Statistics say: 5% of rows = 5M rows match.
- Planner choice: **Index Scan** - 5M out of 100M rows is selective enough.
- Estimated cost: log(100M) + 5M heap fetches.
- Actual performance: fast.

**SCENARIO B - Planner with stale statistics:**
After bulk import doubles the PENDING orders to 20%:

- Statistics still say: 5% match.
- Planner choice: **Index Scan** (estimates 5M rows).
- Actual rows: 20M - 20% of table.
- Actual performance: slower than optimal (full table scan would have been better at 20% selectivity).
- Fix: `ANALYZE orders` → planner now sees 20% → chooses Seq Scan or Bitmap Scan → faster.

**SCENARIO C - Join plan choice:**
Query: `SELECT o.* FROM orders o JOIN customers c ON o.customer_id = c.id WHERE c.region = 'EU'`

- EU customers: 10% of 1M customers = 100K customers.
- Each EU customer has ~10 orders = 1M orders to return.
- Planner options:
  1. Nested Loop: for each of 100K EU customers, index-probe orders table → 100K × log(100M) = expensive.
  2. Hash Join: build hash table of 100K EU customers → scan 1M orders → hash probe → fast.
- Correct choice: Hash Join. Planner will choose this if statistics are current.

**THE INSIGHT:**
The planner's choice is data-dependent - same query on different data distributions requires different plans. This is why `ANALYZE` is critical, and why query performance can change as data changes.

---

### 🧠 Mental Model / Analogy

> The query planner is a chess engine evaluating positions. It doesn't calculate every possible game to the end (that's impossible) - instead it evaluates a few moves deep, scores each position using a heuristic (cost model), and picks the best-scoring move (lowest-cost plan). The "board position" is the query + table statistics. The "heuristic" is the cost formula. The "game outcome" is the actual query execution time. Just like a chess engine can be fooled by unusual positions, the planner can be fooled by skewed data distributions or correlated columns.

- "Chess engine" → query planner
- "Available moves" → plan alternatives (scan type, join algorithm, join order)
- "Position evaluation" → cost estimate (formula using statistics)
- "Best move" → chosen execution plan
- "Unusual positions that fool the engine" → skewed data, correlated columns, stale statistics

Where this analogy breaks down: a chess engine's evaluation is based on exact game rules; the planner's cost model is an approximation - its estimates have error margins, and the "optimal plan" chosen may not be globally optimal.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The query planner is the database's brain for deciding how to run your SQL query. It has multiple ways to get the same data (scan the whole table, use an index, join in different orders) and estimates which will be fastest. It then chooses that plan and runs it. Sometimes it guesses wrong, which is why slow queries happen.

**Level 2 - How to use it (junior developer):**
Use `EXPLAIN` to see the chosen plan and `EXPLAIN (ANALYZE, BUFFERS)` to see what actually happened vs. the estimate. If "Rows Removed by Filter" is very high → the planner overestimated selectivity → run `ANALYZE`. If the planner chooses a sequential scan when an index exists → check selectivity (if >5–20% of rows match, sequential scan is often faster) or `random_page_cost` setting. For NVMe SSD, set `random_page_cost = 1.1` to reflect actual I/O cost.

**Level 3 - How it works (mid-level engineer):**
PostgreSQL planner phases:

1. **Parse:** SQL → abstract syntax tree (AST).
2. **Analyze/Rewrite:** Semantic analysis; view expansion; rule rewrites.
3. **Plan:** Enumerate possible plans → estimate cost for each → pick minimum.
   - For each table: consider all scan methods (seq, index, bitmap).
   - For each join pair: consider all algorithms (nested loop, hash, merge) and both join orders.
   - Build plan tree bottom-up using dynamic programming.
4. **Execute:** The executor walks the plan tree, calling each node's `ExecScan`, `ExecJoin`, `ExecAgg` functions.

**Level 4 - Why it was designed this way (senior/staff):**
The cost-based optimizer (CBO) replaced rule-based optimizers in the 1980s–1990s because rule-based systems couldn't adapt to data distribution changes. The CBO's fundamental weakness is multi-column correlation: statistics are per-column (`pg_statistic`), but correlated column combinations (e.g., `city` and `zip_code` are highly correlated) have joint distributions that single-column statistics can't capture. PostgreSQL 10+ added "extended statistics" (`CREATE STATISTICS`) for multi-column correlations. Cardinality estimation is the core challenge - getting the number-of-rows estimate right determines join order, join algorithm, and memory grant. Modern databases augment traditional statistics with machine learning (Oracle's Adaptive Query Optimization, SQL Server's Adaptive Joins): if execution significantly diverges from the estimated plan, the plan is replaced mid-execution with a better one. PostgreSQL 14 added incremental sort and memoization to the plan space. The ongoing frontier: learned cardinality estimation using query feedback to correct future estimates.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ QUERY PLANNER: PHASES                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  SQL: "SELECT * FROM orders o                        │
│         JOIN customers c ON o.customer_id = c.id     │
│         WHERE c.region = 'EU' AND o.amount > 100"   │
│                                                      │
│  1. Parse → AST                                     │
│  2. Analyze: validate tables, columns, types         │
│  3. Plan enumeration (simplified):                   │
│                                                      │
│  Plan A: Seq Scan customers → filter region='EU'    │
│           → Nested Loop → Index Scan orders         │
│  Plan B: Index Scan customers(region) → Hash Build  │
│           → Seq Scan orders → Hash Join             │
│  Plan C: Seq Scan orders(amount>100) → Hash Build   │
│           → Index Scan customers(region) → Hash Join│
│                                                      │
│  Cost estimates (using pg_statistic):               │
│  - n_customers = 1M; EU fraction = 10% = 100K rows  │
│  - n_orders = 100M; amount>100 fraction = 70% = 70M │
│  Plan A cost: 100K × log(100M) = high               │
│  Plan B cost: 100K hash build + 70M probe = medium  │
│  Plan C cost: 70M scan + 100K hash probe = best →   │
│               Planner chooses Plan C                │
│                                                      │
│  4. Execute plan C                                  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
SQL query received
→ Parse → Analyze → Rewrite
→ [QUERY PLANNER ← YOU ARE HERE: enumerate + estimate + choose]
→ Execution plan tree generated
→ Executor walks plan tree (Seq Scan / Index Scan / Hash Join / ...)
→ Results returned to client
```

**FAILURE PATH:**

```
Bulk load: 10M new rows inserted, all with status='HOT_NEW'
→ Statistics not updated (no ANALYZE)
→ Planner estimates 0.01% have status='HOT_NEW' (old stats)
→ Query WHERE status='HOT_NEW' → Planner chooses Index Scan
→ Actual rows: 10M (10% of table)
→ 10M random heap fetches → 10× slower than Seq Scan
→ Fix: ANALYZE orders; (autovacuum does this automatically)
```

**WHAT CHANGES AT SCALE:**
At very large table counts (thousands of tables) or very complex queries (50+ joins in OLAP), planning time itself becomes a bottleneck - preparing a complex query plan can take hundreds of milliseconds. Solutions: prepared statements (plan once, execute many times), `plan_cache_mode = force_generic_plan` for parameterized queries with high skew, or OLAP-specific optimizers (columnar stores like DuckDB/ClickHouse bypass the traditional row-store planner entirely).

---

### ⚖️ Comparison Table

| Join Algorithm  | Best For                      | Cost Complexity      | Memory                            |
| --------------- | ----------------------------- | -------------------- | --------------------------------- |
| **Nested Loop** | Small outer, indexed inner    | O(outer × log inner) | Low                               |
| **Hash Join**   | Large tables, no useful index | O(n + m)             | Build hash table in memory        |
| **Merge Join**  | Both sides pre-sorted         | O(n + m) after sort  | Low (if sorted); sort cost if not |

| Scan Type            | Best For                      | Cost           | Notes                              |
| -------------------- | ----------------------------- | -------------- | ---------------------------------- |
| **Seq Scan**         | > 5–20% rows match            | O(n pages)     | Sequential I/O; fast for large %   |
| **Index Scan**       | < 5% rows match               | O(log n + k)   | Random I/O per row; fast for low % |
| **Index Only Scan**  | All needed cols in index      | O(log n + k)   | No heap fetch; fastest             |
| **Bitmap Heap Scan** | Multiple conditions, medium % | O(n log n + k) | Combines multiple indexes          |

How to choose: The planner chooses automatically. Tune `random_page_cost`, `effective_cache_size`, and keep statistics fresh. Override with hints only as last resort.

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                     |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The planner always uses the best index      | The planner uses the best _estimated_ plan - if statistics are stale, it may choose a suboptimal plan; ANALYZE updates statistics                                           |
| Sequential scan means no index exists       | The planner may choose a sequential scan even with an existing index if selectivity is low (>10–20% of rows match) - sequential I/O is faster than many random heap fetches |
| Adding an index always makes queries faster | The planner may ignore an index if it estimates the index scan is more expensive than a seq scan; adding an unused index only adds write overhead                           |
| EXPLAIN output shows what will happen       | `EXPLAIN` shows what the planner _estimates_; `EXPLAIN ANALYZE` shows what _actually_ happened - these can differ significantly with stale statistics                       |

---

### 🚨 Failure Modes & Diagnosis

**1. Planner Chooses Sequential Scan Instead of Index Scan**

**Symptom:** `EXPLAIN` shows `Seq Scan` on a large table with an existing relevant index; query is slow.

**Root Cause:** Either (a) statistics are stale - planner underestimates selectivity; (b) `random_page_cost` is too high for the storage type (SSD); (c) the query genuinely returns >10% of rows (seq scan IS faster in this case).

**Diagnostic:**

```sql
-- Check if ANALYZE was run recently
SELECT relname, last_analyze, last_autoanalyze, n_mod_since_analyze
FROM pg_stat_user_tables
WHERE relname = 'orders';

-- Run EXPLAIN to see estimates vs. actuals
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 42;

-- Compare: "rows=NNN" (estimate) vs "actual rows=NNN"
-- Large discrepancy → stale statistics

-- Check random_page_cost setting
SHOW random_page_cost;
-- Set to 1.1 for SSD: SET random_page_cost = 1.1;
```

**Fix:** `ANALYZE orders` - updates statistics. For SSD: `ALTER SYSTEM SET random_page_cost = 1.1; SELECT pg_reload_conf()`.

**Prevention:** Ensure autovacuum runs with ANALYZE. Set `autovacuum_analyze_scale_factor = 0.01` for high-write tables. Set `random_page_cost` appropriately for storage type.

---

**2. Wrong Join Order Causing Cartesian Product or Large Intermediate Result**

**Symptom:** A multi-table join query runs for minutes instead of seconds; `EXPLAIN ANALYZE` shows a join node with "actual rows" in the hundreds of millions; memory usage spikes.

**Root Cause:** Planner chose a join order that produces a large intermediate result early in the plan - a small intermediate result early in the plan is usually better. Often caused by stale statistics leading to wrong cardinality estimates.

**Diagnostic:**

```sql
-- Look for the join node with large actual rows vs estimate
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM a JOIN b ON ... JOIN c ON ... WHERE ...;

-- Find nodes where actual rows >> estimated rows
-- Those are the cardinality estimation failures

-- Check join order with enable_ flags (for diagnosis only)
SET enable_hashjoin = off;  -- force planner to avoid hash joins
SET join_collapse_limit = 1;  -- use query-as-written join order
EXPLAIN SELECT ...;  -- compare cost
```

**Fix:** Run `ANALYZE table1, table2, table3`. If data has multi-column correlations: `CREATE STATISTICS stats_name ON (col1, col2) FROM table`. As temporary workaround: rewrite query to force join order using subqueries or CTEs.

**Prevention:** After bulk loads, run `ANALYZE` on affected tables. For complex OLAP queries, review EXPLAIN ANALYZE output before deploying. Create extended statistics for known correlated column pairs.

---

**3. Planning Time Too High for Complex Queries**

**Symptom:** First execution of a complex query with many joins takes 5–10 seconds; subsequent executions (from plan cache) are fast; latency spikes every time the plan cache is cleared.

**Root Cause:** PostgreSQL's exhaustive join enumeration is O(n!) for n tables. Above `join_collapse_limit` (default 8), GEQO is used - faster but sometimes suboptimal. For complex queries with many joins, planning itself is slow.

**Diagnostic:**

```sql
-- Check planning vs execution time
EXPLAIN (ANALYZE, TIMING)
SELECT ... FROM many_tables ...;
-- Look for "Planning Time: NNN ms" vs "Execution Time: NNN ms"
-- If Planning Time >> Execution Time → optimization needed

-- Check join_collapse_limit
SHOW join_collapse_limit;  -- default 8
SHOW geqo_threshold;  -- default 12 (GEQO kicks in above this)
```

**Fix:** Use prepared statements (`PREPARE name AS SELECT ...`) to amortize planning cost across many executions. For OLAP workloads with static query shapes: increase `geqo_threshold` or manually specify join order. Consider columnar databases (DuckDB, ClickHouse) for complex analytical queries.

**Prevention:** For high-frequency queries, always use prepared statements. Benchmark planning time separately from execution time for complex queries.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Index Types (B-Tree, Hash, Composite, Covering)` - the planner chooses which index to use
- `B+ Tree` - the data structure behind index scans
- `EXPLAIN` - the tool to inspect query plans

**Builds On This (learn these next):**

- `EXPLAIN` - deep dive into reading and interpreting execution plans
- `Normalization` - normalized schemas give the planner more optimization opportunities
- `Index Types` - adding the right indexes gives the planner better plan options

**Alternatives / Comparisons:**

- `EXPLAIN` - the debugging interface to the planner
- `Statistics` - the data that drives the planner's cost estimates

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Database optimizer: enumerates, estimates,│
│              │ and selects the cheapest execution plan   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ SQL is declarative - someone must decide  │
│ SOLVES       │ HOW to execute it (join order, scan type) │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Plan quality = statistics quality -       │
│              │ stale stats → wrong plan → slow query     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Debugging slow queries - always check     │
│              │ EXPLAIN ANALYZE first                     │
├──────────────┼───────────────────────────────────────────┤
│ TUNE FOR     │ Set random_page_cost=1.1 for SSD;         │
│              │ run ANALYZE after bulk loads              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Planning time vs. execution time;         │
│              │ complexity vs. optimality                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The planner is only as smart as          │
│              │  its statistics are current"              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ EXPLAIN → Statistics → Index Design       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D - Failure Scenario) A production PostgreSQL database has autovacuum enabled. After a data migration that replaced 80% of the rows in the `orders` table (DELETE + INSERT, not UPDATE), query performance degrades significantly. `EXPLAIN ANALYZE` shows estimates wildly different from actuals. Walk through exactly what happened: why did autovacuum's ANALYZE not prevent this? What specific statistics are now wrong, how do they cause the wrong plan, and what is the correct remediation sequence?

**Q2.** (TYPE F - Comparison Depth) PostgreSQL's planner uses a cost-based model with fixed cost parameters (`seq_page_cost`, `random_page_cost`, `cpu_tuple_cost`). Modern databases like SQL Server and Oracle have added adaptive query processing - mid-execution plan correction when estimates are wrong. What are the three categories of estimation errors the traditional cost-based model makes poorly, and how does each adaptive mechanism address them? What would be the engineering cost of adding similar adaptive processing to PostgreSQL?
