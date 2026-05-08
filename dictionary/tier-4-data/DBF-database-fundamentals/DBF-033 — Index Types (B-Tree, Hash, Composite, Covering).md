---
layout: default
title: "Index Types (B-Tree, Hash, Composite, Covering)"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 33
permalink: /databases/index-types/
id: DBF-033
category: Database Fundamentals
difficulty: ★★☆
depends_on: B+ Tree, B-Tree, Query Planner / Execution Plan
used_by: EXPLAIN, Normalization, Query Optimization
related: B+ Tree, B-Tree, LSM Tree, EXPLAIN
tags:
  - database
  - indexing
  - query-optimization
  - intermediate
---

# DBF-033 — Index Types (B-Tree, Hash, Composite, Covering)

⚡ TL;DR — Choosing the right index type (B-Tree, Hash, Composite, Covering, Partial) determines whether your queries run in milliseconds or minutes — each type solves a specific query shape, and over-indexing destroys write performance.

| #428            | Category: Database Fundamentals                 | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | B+ Tree, B-Tree, Query Planner / Execution Plan |                 |
| **Used by:**    | EXPLAIN, Normalization, Query Optimization      |                 |
| **Related:**    | B+ Tree, B-Tree, LSM Tree, EXPLAIN              |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An application has 5 indexes on the `orders` table: `customer_id`, `status`, `(customer_id, status)`, `(status, customer_id)`, and `created_at`. A DBA adds two more after a slow query report. Each of the 7 indexes must be updated on every INSERT, UPDATE, DELETE — 7× write amplification. Insert performance drops 60%. A long-running deployment adds 3 more indexes. The table now has 10 indexes; INSERT throughput is 10% of baseline. The root cause: wrong index types were used, indexes overlap, and no covering indexes exist for the hot queries.

**THE BREAKING POINT:**
Without understanding index types, developers create indexes reactively (after slow queries) with no strategy — resulting in duplicate indexes, wrong types, and write-amplification debt that's hard to reverse.

**THE INVENTION MOMENT:**
"Match the index type to the query shape. No more, no less."

---

### 📘 Textbook Definition

A **database index** is a data structure that enables the database engine to locate rows matching a predicate without scanning the entire table. The major index types are: **B-Tree index** (default; supports equality, range, ORDER BY, LIKE prefix); **Hash index** (equality only, O(1) lookup); **Composite index** (index on multiple columns; enables multi-column filtering with leftmost-prefix rules); **Covering index** (an index containing all columns needed by a query — eliminates heap fetch); **Partial index** (an index on a subset of rows matching a condition — smaller, faster, specific); **Full-text index** (inverted index for text search); **Spatial index** (GiST/GeoHash for geometric queries). Each type has a specific query shape it optimizes and a write overhead it imposes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Different index types are built for different query shapes — B-Tree for ranges, hash for equality, composite for multi-column filters, covering for projection, partial for filtered subsets.

**One analogy:**

> Index types are like tool specializations: a screwdriver (B-Tree — general purpose, handles most fasteners), a socket wrench (composite index — handles multiple fasteners in sequence), a power drill (covering index — does the whole job without changing tools), and a specialty hex key (partial index — perfect for one specific screw type). Using the wrong tool isn't impossible — it's just slow.

**One insight:**
A covering index — one that contains all columns needed by a query — can eliminate the heap fetch entirely (PostgreSQL: "index-only scan"; MySQL: "using index"). A single covering index can often replace 2–3 separate indexes at lower total write overhead.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every index trades write overhead for read acceleration.
2. Unused indexes cost write performance with no benefit — identify and drop them.
3. The query planner chooses the index; it does not always choose the "best" one — use EXPLAIN to verify.
4. Composite index column order matters: the leftmost prefix rule — an index on `(a, b, c)` can be used for queries on `(a)`, `(a, b)`, `(a, b, c)` but NOT for `(b)` or `(c)` alone (without `a`).

**B-TREE INDEX:**

- Default type in all databases.
- Supports: `=`, `<`, `>`, `<=`, `>=`, `BETWEEN`, `LIKE 'prefix%'`, `ORDER BY`, `IS NULL`.
- Does NOT help: `LIKE '%suffix'`, full-text search, very low cardinality columns (boolean — often better to not index).
- `CREATE INDEX idx ON table(col)` — always creates B-Tree.

**HASH INDEX:**

- Exact equality only (`=`). O(1) average lookup.
- Does NOT support: range queries, ORDER BY, partial matches.
- PostgreSQL: `CREATE INDEX idx ON table USING HASH (col)`.
- Use cases: UUID lookups, token lookups, session ID lookups.
- Rarely used — B-Tree handles equality nearly as fast with the added range ability.

**COMPOSITE INDEX:**

- Index on multiple columns: `CREATE INDEX idx ON table(col1, col2, col3)`.
- Leftmost prefix: usable for queries on `(col1)`, `(col1, col2)`, `(col1, col2, col3)`.
- Column order: put most selective / most frequently filtered first. Put range predicate column last (range predicate stops the leftmost prefix optimization).
- Index on `(status, created_at)` helps: `WHERE status='active' AND created_at > '2024-01-01'`.
- Same index does NOT help: `WHERE created_at > '2024-01-01'` alone (no `status` prefix).

**COVERING INDEX:**

- An index that includes all columns needed by a query (in the index key or as INCLUDE columns).
- `CREATE INDEX idx ON orders(customer_id) INCLUDE (amount, status)`.
- Query: `SELECT amount, status FROM orders WHERE customer_id = 42` — uses index-only scan (no heap fetch).
- Write overhead: slightly higher (more data per index entry). Read benefit: eliminates 1 random I/O per row (heap fetch).

**PARTIAL INDEX:**

- Indexes only rows matching a condition.
- `CREATE INDEX idx ON orders(customer_id) WHERE status = 'PENDING'`.
- Smaller index (only PENDING orders). Faster for queries filtering by `status = 'PENDING'`.
- Planner uses it only when query includes the partial index predicate.
- Use case: indexes on "hot" subsets (active users, pending orders, unprocessed events).

**THE TRADE-OFFS:**
| Index Type | Write Cost | Read Gain | Best For |
|---|---|---|---|
| B-Tree | Medium | Range + equality | General purpose |
| Hash | Low | Equality only O(1) | UUID/token lookups |
| Composite | Medium-High | Multi-column filters | Multi-predicate queries |
| Covering | Higher | Eliminates heap fetch | Projection-heavy hot queries |
| Partial | Low | Smaller, faster | Hot subset access patterns |

---

### 🧪 Thought Experiment

**SETUP:**
Table: `orders(id BIGINT, customer_id BIGINT, status TEXT, amount DECIMAL, created_at TIMESTAMP)`. 100M rows. Key query patterns:

1. `SELECT * FROM orders WHERE customer_id = 42` — customer order history
2. `SELECT amount, status FROM orders WHERE customer_id = 42 AND status = 'PENDING'`
3. `SELECT COUNT(*) FROM orders WHERE status = 'PENDING'`

**NAIVE APPROACH:**
Three separate indexes: `idx_customer`, `idx_status`, `idx_customer_status`. Total: 3 indexes, 3× write amplification.

**OPTIMIZED APPROACH:**

1. Query 1: `idx_customer ON (customer_id)` — B-Tree covers equality.
2. Query 2: `idx_customer_status ON (customer_id, status) INCLUDE (amount)` — composite covering index. Eliminates heap fetch.
3. Query 3: `idx_pending ON (status) WHERE status = 'PENDING'` — partial index. Small, fast.

Result: 3 indexes as before, but:

- Query 2 uses covering composite index (no heap fetch) → 2–3× faster.
- Query 3 uses small partial index (only PENDING rows) → 5–10× smaller, faster.
- Composite index also covers Query 1 via leftmost prefix.
- Can drop `idx_customer` since `idx_customer_status` covers it.
- Result: 2 indexes instead of 3, with better query performance.

**THE INSIGHT:**
Strategic index design — using composite and covering indexes — often reduces index count while improving query performance AND write throughput.

---

### 🧠 Mental Model / Analogy

> Index types are like search systems in different kinds of reference books:
>
> - **B-Tree** = encyclopedia index (find "A" to "G", find range "Ada–Adams")
> - **Hash index** = phone book exact name lookup (O(1) direct lookup, but can't find "all names starting with Ad")
> - **Composite index** = card catalog organized by (last name, first name) — find "Smith, John" efficiently; find "Smith, _" efficiently; cannot find "_, John" efficiently
> - **Covering index** = an index that contains the answer itself (like a summary in the margin — no need to turn to the actual page)
> - **Partial index** = a specialized mini-directory of only active members (much smaller, faster than indexing everyone)

- "Turning to the actual page" → heap fetch (following TID from index to table)
- "Answer in the margin" → covering index (index-only scan)
- "Cannot find \*, John in name-first-name catalog" → leftmost prefix rule
- "Mini-directory of active members" → partial index on WHERE status='ACTIVE'

Where this analogy breaks down: database indexes are dynamic — they update automatically with every INSERT/UPDATE/DELETE, unlike printed reference books.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Database indexes are like book indexes — they let you find specific data quickly without reading everything. Different types of indexes are built for different types of searches. The most common type (B-Tree) handles most situations. Special types handle specific patterns more efficiently.

**Level 2 — How to use it (junior developer):**

- B-Tree: default — always the starting point.
- Composite: create `(col1, col2)` when you always filter by both; put most selective column first.
- Covering: add `INCLUDE (col3, col4)` for SELECT columns you always retrieve.
- Partial: add `WHERE condition` to index only the rows you actually query.
- Check index usage with `pg_stat_user_indexes.idx_scan` — zero-scan indexes are waste.

**Level 3 — How it works (mid-level engineer):**
**Leftmost prefix in depth:** A composite index `(a, b, c)` is stored as a B+ Tree sorted by `a` first, then `b`, then `c`. The planner can use it for predicates on `a` alone (binary search on first key), or `a AND b`, or `a AND b AND c`. It cannot use it starting from `b` because the B+ Tree isn't sorted by `b` at the top level. Exception: the planner can sometimes use an index backward (for `ORDER BY a DESC`) via a reverse scan.

**Range predicate column order:** In a composite index `(status, created_at)`, the predicate `WHERE status='ACTIVE' AND created_at > '2024-01-01'` uses both columns: B+ Tree finds rows where `status='ACTIVE'` (equality on first key), then scans forward within that partition where `created_at > '2024-01-01'` (range on second key). After the range column, no further keys in the composite index are used (the range stops the multi-column optimization). So `(status, created_at, amount)` doesn't help if the predicate is `WHERE status='ACTIVE' AND created_at > '...' AND amount > 100` — `amount` is useless in this index unless `created_at` is an equality predicate.

**Level 4 — Why it was designed this way (senior/staff):**
The leftmost prefix rule is not a limitation — it's a mathematical consequence of how B+ Trees sort keys. A composite index is a sorted list of (a, b, c) tuples — to binary-search by `b` alone you'd need the tree sorted by `b` first, which is a different index. The INCLUDE clause (PostgreSQL 11+, SQL Server) was added to create covering indexes without affecting the sort order of the index key — INCLUDE columns are stored in leaf nodes only (not internal nodes), so they're available for index-only scans but don't affect the leftmost prefix or sort order. This is elegant: you get covering-scan benefits without polluting the sort key structure. Hash indexes are fast for equality but were historically not crash-safe in PostgreSQL (pre-10); they're now WAL-logged but still rarely used because B-Tree equality is nearly as fast and has range ability. The practical decision: every covering index adds write overhead proportional to the size of included columns; covering indexes for infrequently queried columns add write overhead with negligible read benefit.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ INDEX TYPES: QUERY SUPPORT MATRIX                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Query Type          B-Tree  Hash  Composite  Partial │
│ ─────────────────────────────────────────────────── │
│ col = value           ✅     ✅      ✅*       ✅*    │
│ col > value           ✅     ❌      ✅*       ✅*    │
│ col BETWEEN x AND y   ✅     ❌      ✅*       ✅*    │
│ LIKE 'prefix%'        ✅     ❌      ✅*       ✅*    │
│ LIKE '%suffix'        ❌     ❌      ❌         ❌    │
│ ORDER BY col          ✅     ❌      ✅*        ✅    │
│ Multi-col filter      ❌     ❌      ✅         ❌    │
│ Col = value (O(1))    ❌     ✅      ❌         ❌    │
│                                                      │
│ *Composite: only for leftmost prefix columns         │
│ *Partial: only when WHERE condition is satisfied     │
│                                                      │
│ COVERING INDEX — additional benefit:                 │
│ Returns all needed columns from index leaf nodes     │
│ (no heap fetch) → "Index Only Scan" in EXPLAIN       │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Query: SELECT amount, status FROM orders
       WHERE customer_id=42 AND status='PENDING'
→ Query planner: available indexes?
→ [INDEX TYPES ← YOU ARE HERE: planner chooses type]
→ Composite covering index (customer_id, status) INCLUDE (amount)
→ Index-only scan: no heap fetch needed
→ Return amount, status from leaf nodes directly
```

**FAILURE PATH:**

```
Index on (status, customer_id) exists
Query: WHERE customer_id=42 AND status='PENDING'
→ Planner cannot efficiently use status-first index for customer_id=42
→ Falls back to sequential scan or inefficient bitmap scan
→ Fix: create index on (customer_id, status) — most selective first
```

**WHAT CHANGES AT SCALE:**
At high write rates, each additional index linearly increases write overhead. At 100K writes/second, the difference between 3 and 6 indexes is visible in latency. Index maintenance (splitting, WAL writes) competes with user transactions. Partial indexes on high-write tables can dramatically reduce index overhead: if 95% of orders are in status='COMPLETED' and only 5% are 'PENDING', a partial index on `WHERE status='PENDING'` is 20× smaller than a full index on `status`.

---

### ⚖️ Comparison Table

| Index Type       | Create Syntax (PostgreSQL)                                     | Best Query Shape          | Write Overhead    |
| ---------------- | -------------------------------------------------------------- | ------------------------- | ----------------- |
| B-Tree (default) | `CREATE INDEX idx ON t(col)`                                   | Equality, range, ORDER BY | Medium            |
| Hash             | `CREATE INDEX idx ON t USING HASH(col)`                        | Equality only             | Low               |
| Composite        | `CREATE INDEX idx ON t(col1, col2)`                            | Multi-column filters      | Medium-High       |
| Covering         | `CREATE INDEX idx ON t(col1) INCLUDE (col2, col3)`             | Projection + filter       | Higher            |
| Partial          | `CREATE INDEX idx ON t(col) WHERE condition`                   | Filtered subset           | Low (small index) |
| Full-text        | `CREATE INDEX idx ON t USING GIN(to_tsvector('english', col))` | Text search               | High              |

How to choose: Start with B-Tree. Add composite for multi-predicate queries. Add INCLUDE for hot SELECT columns. Use partial for high-cardinality subsets. Only use hash when equality-only is certain.

---

### ⚠️ Common Misconceptions

| Misconception                                                                 | Reality                                                                                                                                                                                          |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| More indexes always help performance                                          | Indexes accelerate reads at the cost of write performance; every insert/update/delete updates every index — each index beyond what's needed is pure overhead                                     |
| Composite index on (a,b) is equivalent to two separate indexes on (a) and (b) | A composite index (a,b) is used for queries filtering by a (with or without b) — it cannot be used as a standalone index on b; separate indexes on (a) and (b) cover different query shapes      |
| Partial indexes are an optimization trick, not production-worthy              | Partial indexes are standard production SQL; `CREATE INDEX ... WHERE condition` is ANSI SQL; they dramatically reduce index size and maintenance overhead for filtered access patterns           |
| INCLUDE columns in covering indexes affect sort order                         | INCLUDE columns are stored only in leaf nodes — they do not affect the sort key of the index and do not benefit range queries or ORDER BY; they only eliminate heap fetches for included columns |

---

### 🚨 Failure Modes & Diagnosis

**1. Unused Indexes Consuming Write Overhead**

**Symptom:** Write performance degrading as table grows; `EXPLAIN` shows many indexes exist; DBA can't identify which are needed.

**Root Cause:** Indexes were created reactively over time; some are now redundant (covered by composite indexes), some are never used (low-cardinality columns), some overlap.

**Diagnostic:**

```sql
-- Find unused indexes (never scanned)
SELECT schemaname,
       relname AS table,
       indexrelname AS index,
       idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE 'pg_%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Find redundant indexes (subset of another index)
-- e.g., idx on (customer_id) is redundant if (customer_id, status) exists
-- and all queries using customer_id also benefit from the composite
```

**Fix:** Drop zero-scan indexes (verify in staging first — some are used only for constraints like UNIQUE). Merge single-column indexes into composites where appropriate.

**Prevention:** Review indexes quarterly with `pg_stat_user_indexes`. Flag zero-scan indexes for removal. Never add an index without checking if an existing composite covers the same query.

---

**2. Composite Index Column Order Wrong — Query Not Using Index**

**Symptom:** `EXPLAIN` shows sequential scan despite composite index existing; query is slow.

**Root Cause:** Composite index column order doesn't match query predicate — the leftmost column in the index is not in the query's WHERE clause.

**Diagnostic:**

```sql
-- Example: index is (status, customer_id)
-- Query is WHERE customer_id = 42 (no status filter)
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 42;
-- Shows Seq Scan, not Index Scan

-- Verify index column order
SELECT
  indexname,
  array_agg(attname ORDER BY attnum) AS columns
FROM pg_index
JOIN pg_class ON pg_class.oid = pg_index.indexrelid
JOIN pg_attribute ON pg_attribute.attrelid = pg_index.indrelid
  AND pg_attribute.attnum = ANY(pg_index.indkey)
WHERE pg_class.relname = 'idx_orders_status_customer'
GROUP BY indexname;
```

**Fix:** Create a new index with correct column order: `CREATE INDEX idx ON orders(customer_id, status)`. Drop the old wrong-order index if it's not needed for other queries.

**Prevention:** Follow the rule: put the most frequently filtered, highest-cardinality column first. Put range predicate columns last. Verify with `EXPLAIN` before deploying.

---

**3. Index Not Used Due to Type Mismatch / Function on Column**

**Symptom:** `EXPLAIN` shows sequential scan; index clearly exists on queried column; query is slow.

**Root Cause:** Query uses a function or implicit type cast on the indexed column, preventing the planner from using the index. Examples: `WHERE LOWER(email) = 'user@example.com'` when index is on `email`; `WHERE customer_id = '42'` when `customer_id` is `INTEGER` (implicit cast from text).

**Diagnostic:**

```sql
-- Check for function usage on indexed column
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'user@example.com';
-- Shows: Seq Scan (function on indexed column disables index)

-- Fix: create a functional index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Or fix the query to not use function:
-- Store email already lowercased, use = directly
```

**Fix:** For `LOWER(col)` patterns: create `CREATE INDEX ON table(LOWER(col))` and store email lowercased on insert. For type mismatches: fix the query to use the correct type (`WHERE customer_id = 42` not `= '42'`).

**Prevention:** Code review: any function call on a column in WHERE clause is a red flag. Use database linting tools. Test all WHERE predicates with `EXPLAIN` before deployment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `B+ Tree` — the underlying structure for B-Tree, Composite, and Covering indexes
- `Query Planner / Execution Plan` — the planner selects which index to use
- `B-Tree` — the base structure for understanding B+ Tree implementation

**Builds On This (learn these next):**

- `EXPLAIN` — the tool to verify index selection and diagnose slow queries
- `Normalization` — normalized schemas create better index opportunities
- `Query Planner / Execution Plan` — understand how the planner chooses between indexes

**Alternatives / Comparisons:**

- `LSM Tree` — the storage structure underlying NoSQL indexes (Cassandra, RocksDB)
- `Full-text search` — GIN/GiST indexes for text search (different problem space)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ B-TREE       │ Default. Equality + range + ORDER BY      │
│ HASH         │ Equality-only. O(1). Rarely needed.       │
│ COMPOSITE    │ Multi-column. Leftmost prefix rule.       │
│ COVERING     │ INCLUDE cols. Eliminates heap fetch.      │
│ PARTIAL      │ WHERE clause. Small. Hot subsets.         │
├──────────────┼───────────────────────────────────────────┤
│ LEFTMOST     │ (a,b,c) helps: a, (a,b), (a,b,c)         │
│ PREFIX RULE  │ Does NOT help: b alone, c alone, (b,c)    │
├──────────────┼───────────────────────────────────────────┤
│ KEY PITFALL  │ Every index = write overhead. Drop        │
│              │ zero-scan indexes. Composite > many single│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Match the index to the query shape;      │
│              │  every index is a write tax"              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ EXPLAIN → Query Planner → B+ Tree         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A — Pattern Identification) Given this table: `events(id, user_id, event_type, payload, created_at)` with 1 billion rows and these query patterns:

- Q1: `WHERE user_id=42 ORDER BY created_at DESC LIMIT 100`
- Q2: `WHERE event_type='purchase' AND created_at > NOW()-INTERVAL '24h'`
- Q3: `SELECT user_id, COUNT(*) FROM events WHERE event_type='view' GROUP BY user_id`
  Design the minimum set of indexes (no more than 3) using appropriate types (B-Tree, Composite, Partial, Covering) that optimally covers all three queries. Justify each index choice with reference to query shape and leftmost prefix rule.

**Q2.** (TYPE C — Design Trade-off) A table processes 200,000 writes/second. It currently has 8 separate B-Tree single-column indexes. Analysis shows 3 indexes are never used and 4 queries account for 90% of read traffic. Design the optimal index strategy: which indexes to drop, which to merge into composites, which to convert to covering or partial. Quantify the expected write throughput improvement from reducing index count.
