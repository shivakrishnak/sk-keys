---
version: 1
layout: default
title: "EXPLAIN"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /databases/explain/
id: DBF-035
category: Database Fundamentals
difficulty: ★★☆
depends_on: Query Planner / Execution Plan, Index Types, B+ Tree
used_by: Query Optimization, Index Design
related: Query Planner / Execution Plan, Index Types, Statistics
tags:
  - database
  - query-optimization
  - debugging
  - intermediate
---

# DBF-035 - EXPLAIN

⚡ TL;DR - `EXPLAIN` shows you what the database _plans_ to do; `EXPLAIN (ANALYZE, BUFFERS)` shows what it _actually_ did - the gap between those two is where performance problems live.

| #430            | Category: Database Fundamentals                         | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Query Planner / Execution Plan, Index Types, B+ Tree    |                 |
| **Used by:**    | Query Optimization, Index Design                        |                 |
| **Related:**    | Query Planner / Execution Plan, Index Types, Statistics |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A query is slow. The developer checks: the table has an index. The query should be fast. It isn't. Without visibility into the execution plan, the developer has no way to know whether the index is being used, whether a table scan is happening, why a join is slow, or whether the query is sorting 10 million rows unnecessarily. The only available tools are timing and guesswork.

**THE BREAKING POINT:**
Modern queries involve multiple tables, multiple indexes, multiple join algorithms, sort operations, and aggregations. Any one node in the execution plan can be the bottleneck. Without seeing the plan, you cannot know which node is slow - or why.

**THE INVENTION MOMENT:**
"Show the developer the entire execution plan with cost estimates and actual timings."

---

### 📘 Textbook Definition

`EXPLAIN` is a SQL command that displays the **execution plan** chosen by the query planner for a given query. `EXPLAIN` alone shows the estimated plan (no query execution). `EXPLAIN ANALYZE` actually executes the query and shows actual row counts, actual timing, and actual vs. estimated rows - the critical comparison for diagnosing performance issues. `EXPLAIN (ANALYZE, BUFFERS)` additionally shows cache hits vs. disk reads per plan node. The output is a tree of plan nodes - each node is an operation (Seq Scan, Index Scan, Hash Join, Sort, etc.) with cost estimates and, after ANALYZE, actual measurements.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`EXPLAIN ANALYZE` shows the full execution plan with estimated vs. actual rows and timings - the difference reveals where the planner went wrong and why the query is slow.

**One analogy:**

> A GPS trip summary. `EXPLAIN` alone = the route the GPS planned before the trip (with estimated distances and times). `EXPLAIN ANALYZE` = the GPS log after the trip (what roads were actually taken, how long each segment actually took, where traffic jams occurred). The "traffic jam" in your query is the slow plan node - EXPLAIN ANALYZE shows exactly which one.

**One insight:**
The single most important number in `EXPLAIN ANALYZE` output is the ratio of "actual rows" to "rows" (estimated). A 100× discrepancy means the planner's statistics are wrong - it's choosing a plan based on incorrect assumptions about how many rows each step will return. Finding and fixing that discrepancy is the core skill of query optimization.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `EXPLAIN` never executes the query - it shows the _planned_ operations.
2. `EXPLAIN ANALYZE` executes the query - the results are real; do not use on write queries without a transaction and rollback.
3. Cost units are arbitrary - they're relative, not seconds/ms. `cost=0.00..1234.56` means startup_cost `0.00`, total_cost `1234.56`.
4. Rows = estimated rows at that node. Actual rows = rows that were produced. Large discrepancy = statistics problem.
5. The plan tree is read inside-out, bottom-up: the innermost node executes first.

**KEY OPTIONS:**

```sql
EXPLAIN query                    -- Plan only, no execution
EXPLAIN ANALYZE query            -- Execute + plan + timings + actual rows
EXPLAIN (ANALYZE, BUFFERS) query -- + cache hits/misses per node
EXPLAIN (ANALYZE, FORMAT JSON)   -- Machine-readable; use with explain.depesz.com
EXPLAIN (VERBOSE) query          -- Includes output columns per node
```

**READING THE PLAN - KEY FIELDS:**

- `cost=startup..total` - relative cost units; compare across nodes.
- `rows=NNN` - estimated rows output by this node.
- `actual time=Xms..Yms` - time from when node was first called to last row returned.
- `actual rows=NNN` - actual rows produced.
- `loops=N` - how many times this node was executed (e.g., in a Nested Loop).
- `Buffers: shared hit=N read=N` - cache hits vs. disk reads.
- `Rows Removed by Filter: N` - rows that were read but discarded by a filter condition.

**THE TRADE-OFFS:**
`EXPLAIN` vs. `EXPLAIN ANALYZE`: EXPLAIN is safe (no execution); ANALYZE executes the query - for SELECT queries this is fine. For INSERT/UPDATE/DELETE with ANALYZE: wrap in a transaction:

```sql
BEGIN;
EXPLAIN ANALYZE UPDATE ...;
ROLLBACK;
```

---

### 🧪 Thought Experiment

**SETUP:**
Table: `orders(id, customer_id, status, amount)`, 10M rows. Index: `idx_customer` on `customer_id`.

**SCENARIO:**

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 42;
```

**EXPECTED OUTPUT (index used, statistics correct):**

```
Index Scan using idx_customer on orders  (cost=0.43..12.45 rows=5 width=64)
                                          (actual time=0.089..0.234 rows=7 loops=1)
  Index Cond: (customer_id = 42)
  Buffers: shared hit=4
Planning Time: 0.3 ms
Execution Time: 0.3 ms
```

- `rows=5 actual rows=7`: close estimate - minor discrepancy (7 vs 5), statistics are good.
- `shared hit=4`: 4 buffer pool reads, 0 disk reads - fully cached.
- Index Scan used: planner correctly chose the index.

**PROBLEMATIC OUTPUT (stale statistics):**

```
Seq Scan on orders  (cost=0.00..225000.00 rows=50 width=64)
                    (actual time=1205.234..4567.891 rows=500000 loops=1)
  Filter: (customer_id = 42)
  Rows Removed by Filter: 9500000
Planning Time: 0.5 ms
Execution Time: 4578 ms
```

- `rows=50 actual rows=500000`: 10,000× estimate error - statistics are wildly wrong.
- `Rows Removed by Filter: 9500000` - scanned 10M rows to find 500K.
- Seq Scan instead of Index Scan - planner thought only 50 rows match, not worth index.
- Fix: `ANALYZE orders` to update statistics.

**THE INSIGHT:**
The `rows` vs. `actual rows` discrepancy in the Seq Scan node immediately reveals the diagnosis: planner estimated 50, actually 500,000. This is a statistics problem. The fix is `ANALYZE`, not a new index.

---

### 🧠 Mental Model / Analogy

> `EXPLAIN ANALYZE` is like a flight data recorder + pre-flight plan. Before the flight, the captain files a flight plan (EXPLAIN: route, altitude, estimated time). After the flight, the black box shows what actually happened (EXPLAIN ANALYZE: actual path, actual time per segment, any deviations). When the flight took 3× longer than planned, you compare the plan to the actual - you find one segment where turbulence (a slow join) added 2 hours. Fix that segment (add an index, fix statistics), re-file the plan, re-fly.

- "Pre-flight plan" → EXPLAIN output (estimates only)
- "Black box data" → EXPLAIN ANALYZE output (actual timings, actual rows)
- "Segment that added 2 hours" → the slow plan node (highest actual time)
- "Turbulence" → stale statistics, missing index, data skew
- "Fix that segment" → run ANALYZE, add index, rewrite query

Where this analogy breaks down: EXPLAIN ANALYZE must actually execute the query (the "flight" happens). For destructive queries, use a transaction wrapper.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
`EXPLAIN` is a command you run before a slow query to see how the database is planning to run it. `EXPLAIN ANALYZE` actually runs the query and shows you what happened vs. what was planned. It tells you: did it use an index? How many rows did it scan? Where did the time go?

**Level 2 - How to use it (junior developer):**
Run `EXPLAIN (ANALYZE, BUFFERS)` on any slow query. Look for:

1. "Seq Scan" on a large table → missing index or stale statistics.
2. "Rows Removed by Filter: large number" → filter not using an index.
3. `rows=N actual rows=M` where M >> N → stale statistics; run `ANALYZE`.
4. `Buffers: shared read=N` where N is large → many disk reads; data not cached.
5. "Sort" node with large cost → consider adding index for ORDER BY column.

**Level 3 - How it works (mid-level engineer):**
Plan reading in depth: the plan tree is indented - inner nodes execute before outer nodes. Cost is cumulative: a node's `cost` includes all child costs. `actual time` is the time for THIS node's work, not including children (to get wall-clock time for a subtree, compare to parent). For `loops=N`: multiply `actual rows` and `actual time` by N to get totals. Buffers: `shared hit` = pages found in buffer pool; `shared read` = pages read from disk; high `shared read` = cold cache or data too large for cache. Tool: paste EXPLAIN output at [explain.depesz.com](https://explain.depesz.com) or [explain.dalibo.com](https://explain.dalibo.com) - these visualize the plan with highlighting of the most expensive nodes.

**Level 4 - Why it was designed this way (senior/staff):**
The `EXPLAIN` output format exposes the internal plan tree structure - this is by design, not just a debugging aid. PostgreSQL's modular executor is a pull-based iterator model (Volcano/iterator model): each node has a `GetNext()` function that pulls a row from its children. The plan tree reflects this exactly. `EXPLAIN ANALYZE` instruments each node's `GetNext()` call - the instrumentation adds ~5% overhead (negligible for optimization). The separation of `EXPLAIN` (no execution) and `EXPLAIN ANALYZE` (executes) is important: for production queries, `EXPLAIN` alone is safe; `EXPLAIN ANALYZE` on a write query must be wrapped in a transaction. Modern `EXPLAIN (ANALYZE, SETTINGS, WAL)` format (PostgreSQL 13+) also shows configuration settings that affect the plan and WAL usage - useful for debugging non-obvious plan choices. The canonical tool for production plan analysis: `pg_stat_statements` tracks all queries' plan hashes, execution counts, mean/stddev of timings, and rows - essential for finding which queries most need optimization.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│ EXPLAIN ANALYZE OUTPUT: ANNOTATED                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Hash Join  (cost=150.00..4200.00 rows=1000 width=128)   │
│            (actual time=12.5..890.3 rows=987 loops=1)   │
│   Hash Cond: (o.customer_id = c.id)                     │
│   Buffers: shared hit=45 read=120                       │
│   ->  Seq Scan on orders o                              │
│       (cost=0..3000 rows=100000 width=64)               │
│       (actual time=0.05..234.5 rows=100000 loops=1)     │
│       Buffers: shared hit=30 read=100                   │
│   ->  Hash  (cost=50.00..50.00 rows=1000 width=64)     │
│       (actual time=10.2..10.2 rows=987 loops=1)         │
│       Buckets: 1024  Batches: 1  Memory: 128kB          │
│       ->  Index Scan on customers c using idx_region    │
│           (cost=0.43..50.00 rows=1000 width=64)         │
│           (actual time=0.09..8.3 rows=987 loops=1)      │
│           Index Cond: (region = 'EU')                   │
│           Buffers: shared hit=15 read=20                │
│                                                          │
│ KEY NUMBERS:                                            │
│ • rows=1000 vs actual rows=987: good estimate (close)   │
│ • Buffers: shared read=120: 120 disk reads for join     │
│   (120 × 8KB = 960KB from disk - acceptable)           │
│ • Seq Scan on orders: 100K rows scanned - is this the  │
│   right approach? Check if amount filter could help.   │
│                                                          │
│ Planning Time: 0.8 ms                                   │
│ Execution Time: 891 ms                                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Query is slow
→ Developer runs EXPLAIN (ANALYZE, BUFFERS) query
→ [EXPLAIN ← YOU ARE HERE: read the output]
→ Find node with largest actual time
→ Check rows estimate vs actual
→ Large discrepancy → run ANALYZE table
→ Seq Scan on large table → check selectivity → add index if <5%
→ Buffers: shared read high → cold data; check buffer pool size
→ Loops=N with high cost → inner loop is bottleneck; check inner table index
→ Re-run EXPLAIN ANALYZE after fix → verify improvement
```

**FAILURE PATH:**

```
Developer sees: rows=1 actual rows=1000000
→ Runs ANALYZE → rows estimate corrects to 1000000
→ Planner now chooses Seq Scan instead of Index Scan
→ Query is faster (seq scan better for 10% selectivity)
→ But developer sees "Seq Scan" and thinks it's still broken
→ Misconception: "Seq Scan = bad"
→ Reality: Seq Scan is correct for this selectivity
```

**WHAT CHANGES AT SCALE:**
At scale, `EXPLAIN ANALYZE` on production is dangerous for write queries and for slow queries that take minutes. Use `EXPLAIN` first to see the plan without executing. For production analysis without query execution: use `pg_stat_statements` to find slow queries by tracking mean execution time, `pg_stat_user_indexes` to find unused indexes, and `pg_stat_user_tables` to find tables with high sequential scan counts.

---

### ⚖️ Comparison Table

| Command                      | Executes? | Shows Actual Rows? | Shows Timings?   | Safe for Writes?    |
| ---------------------------- | --------- | ------------------ | ---------------- | ------------------- |
| `EXPLAIN`                    | No        | No                 | No               | Yes                 |
| `EXPLAIN ANALYZE`            | Yes       | Yes                | Yes              | Wrap in transaction |
| `EXPLAIN (ANALYZE, BUFFERS)` | Yes       | Yes                | Yes + cache hits | Wrap in transaction |
| `EXPLAIN (FORMAT JSON)`      | Yes       | Yes                | Yes              | Wrap in transaction |
| `pg_stat_statements`         | Ongoing   | Aggregated         | Mean/stddev      | Always safe         |

How to choose: Always start with `EXPLAIN (ANALYZE, BUFFERS)` on SELECT queries. For writes: `BEGIN; EXPLAIN ANALYZE ...; ROLLBACK`. For production monitoring: `pg_stat_statements`.

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                           |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Seq Scan = bad, Index Scan = good"                      | Seq Scan is correct when selectivity is low (>5–20% rows match) - sequential I/O is faster than many random heap fetches; don't force index use without understanding selectivity |
| `EXPLAIN` shows what will happen                         | `EXPLAIN` shows the planned operation - `EXPLAIN ANALYZE` shows what actually happened; the two can differ significantly with stale statistics                                    |
| High `cost` number in EXPLAIN = slow query               | Cost numbers are relative units, not milliseconds - cost=500,000 on one system may be faster than cost=100 on another; use `actual time` from EXPLAIN ANALYZE for real timing     |
| Once EXPLAIN shows an index scan, the query is optimized | An index scan returning 5M rows via 5M random heap fetches may be slower than a seq scan; "index scan used" does not mean "query is fast" - check actual timing                   |

---

### 🚨 Failure Modes & Diagnosis

**1. Large estimates vs. actuals discrepancy (Stale Statistics)**

**Symptom:** `EXPLAIN ANALYZE` shows `rows=50 actual rows=500000` on a key filter node; query is slow.

**Root Cause:** Statistics in `pg_statistic` are stale - autovacuum's ANALYZE hasn't run since the data distribution changed.

**Diagnostic:**

```sql
-- Run EXPLAIN ANALYZE and look for nodes where
-- "rows=" (estimate) << "actual rows=" by > 10×
EXPLAIN (ANALYZE, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 42;

-- Check when ANALYZE last ran
SELECT relname, last_analyze, last_autoanalyze, n_mod_since_analyze
FROM pg_stat_user_tables
WHERE relname = 'orders';
-- n_mod_since_analyze > reltuples * 0.1 → ANALYZE needed

-- Check statistics themselves
SELECT attname, n_distinct, correlation, null_frac
FROM pg_stats
WHERE tablename = 'orders' AND attname = 'customer_id';
```

**Fix:** `ANALYZE orders` - immediate fix. For long-term: ensure autovacuum is configured with `autovacuum_analyze_scale_factor = 0.01` for high-write tables.

**Prevention:** Monitor `n_mod_since_analyze` / `reltuples`. Alert when ratio > 10%. Run manual ANALYZE after bulk data loads.

---

**2. High `Rows Removed by Filter` (Missing or Unused Index)**

**Symptom:** EXPLAIN ANALYZE shows `Rows Removed by Filter: 9,500,000` for a Seq Scan; query scans entire table to find 500K matching rows.

**Root Cause:** The filter condition is not using an index - either no index exists, the index doesn't match the predicate type, or the planner deemed the index non-selective enough.

**Diagnostic:**

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM events WHERE event_type = 'purchase' AND amount > 100;

-- Check what indexes exist
\d events  -- in psql
-- or:
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'events';

-- Check if an index exists but isn't being used
-- Try forcing index use temporarily:
SET enable_seqscan = off;
EXPLAIN SELECT * FROM events WHERE event_type = 'purchase';
-- If it now uses index and is faster → selectivity was miscalculated
-- Fix: ANALYZE events
SET enable_seqscan = on;  -- always reset after diagnosis
```

**Fix:** If no index: `CREATE INDEX idx ON events(event_type, amount)`. If index exists but unused: run `ANALYZE`. If planner still prefers seq scan: check `random_page_cost` (set to 1.1 for SSD).

**Prevention:** Use `pg_stat_user_tables.seq_scan` to identify tables with high sequential scan rates that should have indexed reads. High seq_scan on large tables = missing or wrong indexes.

---

**3. Nested Loop Join with High `loops=` Count (N+1 Query Pattern in Database)**

**Symptom:** EXPLAIN ANALYZE shows a Nested Loop node with `loops=50000` and inner node has high `actual time`; total join time is huge.

**Root Cause:** The outer table produces many rows, and for each one, the planner probes the inner table. If the inner table probe is slow (no index on join key), this multiplies the cost. Equivalent to the "N+1 query problem" - N rows in outer × 1 inner lookup each.

**Diagnostic:**

```sql
-- In EXPLAIN ANALYZE output, find:
-- Nested Loop  (... loops=1)
--   -> Seq Scan outer_table  (actual rows=50000 loops=1)
--   -> Index Scan inner_table  (actual time=0.5..0.5 rows=1 loops=50000)
-- Total inner time: 0.5ms × 50000 = 25 seconds

-- The inner Index Scan "loops=50000" means it ran 50000 times
-- Each run = 0.5ms → 25 total seconds for the join
```

**Fix:** If inner table has no index on join key: `CREATE INDEX ON inner_table(join_key_column)`. If the outer table is producing too many rows: check if there's a filter that should reduce outer rows first (push filter before join). Consider switching to Hash Join by enabling `enable_hashjoin = on`.

**Prevention:** Review multi-table queries with EXPLAIN before deployment. Nested Loops with high loop counts on unindexed columns are a common performance trap in ORM-generated queries.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Query Planner / Execution Plan` - EXPLAIN shows the plan the planner chose
- `Index Types (B-Tree, Hash, Composite, Covering)` - EXPLAIN shows which index types are used
- `B+ Tree` - underlying structure for Index Scan nodes in EXPLAIN output

**Builds On This (learn these next):**

- `Normalization` - normalized schemas create more EXPLAIN-readable query plans
- `Index Types` - after diagnosing with EXPLAIN, create the right index type
- `Query Planner / Execution Plan` - deep dive into plan node types and cost model

**Alternatives / Comparisons:**

- `pg_stat_statements` - production monitoring for query performance over time
- `EXPLAIN (FORMAT JSON)` + external tools (explain.depesz.com) - richer visualization

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ EXPLAIN       │ Plan only. Safe. No execution.           │
│ EXPLAIN ANALYZE│ Execute + actual rows + actual time     │
│ + BUFFERS     │ + cache hits vs. disk reads per node     │
├──────────────┼───────────────────────────────────────────┤
│ LOOK FOR      │ rows= vs actual rows= discrepancy        │
│               │ → stale stats → run ANALYZE              │
├──────────────┼───────────────────────────────────────────┤
│ LOOK FOR      │ Seq Scan + Rows Removed by Filter: high  │
│               │ → missing index or wrong predicate       │
├──────────────┼───────────────────────────────────────────┤
│ LOOK FOR      │ loops=N on inner join node               │
│               │ → N+1 pattern → add index on join key    │
├──────────────┼───────────────────────────────────────────┤
│ LOOK FOR      │ shared read=high → cold data → memory    │
│               │ → increase shared_buffers                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER     │ "EXPLAIN shows the plan; ANALYZE shows   │
│               │  the proof; the gap is your problem"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE  │ pg_stat_statements → Index Types → Stats  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - Pattern Identification) Given this EXPLAIN ANALYZE output:

```
Hash Join (cost=2000..150000 rows=50000) (actual time=450..8900 rows=12 loops=1)
  Hash Cond: (a.id = b.a_id)
  Buffers: shared hit=200 read=15000
  -> Seq Scan on table_a (cost=0..8000 rows=400000) (actual rows=400000)
  -> Hash (cost=1500..1500 rows=40000) (actual rows=12)
     -> Index Scan on table_b (actual rows=12)
```

Identify all three performance problems visible in this output. For each, explain the root cause and the fix. What single change would most improve this query?

**Q2.** (TYPE C - Design Trade-off) A team proposes running `EXPLAIN ANALYZE` on every slow query that exceeds 1 second in production, automatically logging the output to a monitoring table. What are the three risks of this approach in production, and how would you redesign it using `pg_stat_statements` and `auto_explain` to get the same diagnostics without those risks?
