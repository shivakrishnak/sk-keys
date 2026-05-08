---
layout: default
title: "B-Tree"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /databases/b-tree/
id: DBF-030
category: Database Fundamentals
difficulty: ★★☆
depends_on: Index Types, Query Planner / Execution Plan
used_by: B+ Tree, Index Types
related: B+ Tree, LSM Tree, Hash Index
tags:
  - database
  - data-structures
  - indexing
  - intermediate
---

# DBF-030 - B-Tree

⚡ TL;DR - A B-Tree is a self-balancing tree where every node can hold multiple keys, keeping the tree height small (typically 3–4 levels) for billions of rows - making point lookups and range scans efficient in O(log n) disk reads.

| #425            | Category: Database Fundamentals             | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Index Types, Query Planner / Execution Plan |                 |
| **Used by:**    | B+ Tree, Index Types                        |                 |
| **Related:**    | B+ Tree, LSM Tree, Hash Index               |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without an index, finding a row requires scanning every row in the table (full table scan). For a 100M-row orders table, a `WHERE customer_id = 42` query reads 100M rows, most of which are irrelevant. At 100 rows per 8KB page, that's 1 million page reads. At 100 MB/s sequential I/O, that's 10 seconds - for every single point lookup.

**THE BREAKING POINT:**
Binary search trees are O(log n) but require one disk I/O per node visit - for 100M rows, that's 27 disk I/Os at 10ms each = 270ms per lookup. Binary trees are too tall for disk-based systems. The bottleneck is not CPU - it's disk I/Os per lookup.

**THE INVENTION MOMENT:**
"Store many keys per node, matching the disk block size - minimize the number of disk reads per lookup."

---

### 📘 Textbook Definition

A **B-Tree** (Balanced Tree) is a self-balancing, multi-way search tree designed for block-oriented storage. Each internal node holds between ⌈m/2⌉ and m keys (where m is the order), with m+1 child pointers between them. Keys within each node are sorted. The tree maintains balance by splitting overfull nodes and merging/redistributing underfull ones on insert/delete. All leaf nodes are at the same depth. The height is O(log_m n), which for m=200 (typical database page of 8KB holding 200 keys) and n=100M rows is just 4 levels - meaning 4 disk I/Os for any lookup. Standard B-Trees store data records in all nodes; the variant used by most databases is the **B+ Tree** (data only in leaf nodes).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A B-Tree is a fat, short tree where each node holds hundreds of keys - keeping the tree so shallow that any value can be found in 3–4 disk reads, regardless of table size.

**One analogy:**

> A phone book is organized by alphabet: flip to the A section, then within A find "Ac", then find "Adams." Three physical jumps to find any entry in a 1,000-page book - because each "jump" narrows the search by a large factor. A B-Tree works the same way: each node covers a range and points to the child that narrows the search further. With hundreds of keys per node, the tree stays shallow even for billions of entries.

**One insight:**
The key insight is matching the tree's "fan-out" (keys per node) to the storage block size. An 8KB page holding 200 × 40-byte keys has fan-out 200. Three levels of fan-out-200 tree = 200³ = 8 million leaves. Four levels = 1.6 billion - covering any realistic table with just 4 disk reads.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every internal node has between ⌈m/2⌉ and m children (except root).
2. All leaf nodes are at the same depth (perfectly balanced).
3. Keys in each node are sorted; child pointer between key[i] and key[i+1] leads to all keys in (key[i], key[i+1]).
4. Root has at least 2 children (if not a leaf) or 1 key (if a leaf).

**DERIVED DESIGN:**
**Node structure (order m):**

```
[ptr₀ | key₁ | ptr₁ | key₂ | ptr₂ | ... | keyₙ | ptrₙ]
```

Where ptr[i] points to the subtree containing keys < key[i+1] and > key[i].

**Search (O(log_m n)):**

1. Load root node; binary search within it for the target key or range.
2. Follow child pointer to appropriate child node.
3. Repeat until key found (in leaf) or not found.

**Insert:**

1. Search for insertion position (leaf).
2. Insert key+value into leaf.
3. If leaf overfull (> m keys): split → push median key up to parent.
4. If parent overfull: repeat recursively → may propagate to root → root split increases tree height by 1.

**Delete:**

1. Find and remove key.
2. If node underfull (< ⌈m/2⌉ keys): borrow from sibling OR merge with sibling (pulling down parent key).
3. Merge propagates up → may reduce tree height by 1.

**THE TRADE-OFFS:**
**Gain:** O(log_m n) point lookup - typically 3–4 disk I/Os for any table size. Efficient range scans (within a subtree). Self-balancing - no manual rebalancing.
**Cost:** Write amplification: every write to a full leaf causes splits that may propagate up the tree; each split writes a full page. Not optimal for write-heavy workloads (LSM Tree is better). Random I/O pattern for page-at-a-time reads.

---

### 🧪 Thought Experiment

**SETUP:**
A table has 1 billion rows (10⁹). Build a B-Tree index with order m=200 (each node holds up to 200 keys, fits in an 8KB page).

**HEIGHT CALCULATION:**

- Level 0 (root): 1 node, covers all 10⁹ rows
- Level 1: 200 nodes, each covers 5M rows
- Level 2: 40,000 nodes, each covers 25,000 rows
- Level 3: 8M nodes, each covers ~125 rows
- Level 4 (leaf): 1.6B leaf entries

Tree height = 4. Any lookup: 4 disk I/Os (reading one 8KB page per level).

**COMPARISON:**

- Full table scan: 10⁹ / 100 rows per page = 10M page reads = 100 seconds (HDD at 100 MB/s)
- Binary tree: log₂(10⁹) = 30 levels = 30 disk I/Os × 10ms = 300ms
- B-Tree (m=200): 4 levels = 4 disk I/Os × 10ms = 40ms (HDD) or 0.4ms (NVMe)

**THE INSIGHT:**
The fan-out (keys per node) is the critical parameter. Doubling the node size from 8KB to 16KB reduces tree height by one level at 200B keys - from 4 to 3 levels for 1B rows. This is why PostgreSQL's default `fillfactor=90` for B-Tree indexes leaves 10% space in each page: reduces page splits on sequential inserts.

---

### 🧠 Mental Model / Analogy

> A B-Tree is like a library's card catalog system with multiple levels of organization: the master index tells you which section (A–Z), the section index tells you which shelf, the shelf label tells you which row. Each "card" at each level gives you hundreds of options, so you narrow from "all books" to "your book" in 3–4 jumps. Unlike a binary search (narrow by half each time), each B-Tree level narrows by a factor of 200 - much more efficient on physical storage where each "jump" costs a disk read.

- "Section index" → B-Tree root node
- "Shelf label" → internal B-Tree node
- "Row within shelf" → leaf node
- "3–4 jumps to any book" → O(log_m n) = 3–4 disk I/Os
- "Adding a book without reorganizing everything" → B-Tree split/merge maintaining balance

Where this analogy breaks down: B-Trees are symmetric - searching, inserting, and deleting all use the same structure. Physical card catalogs require human reorganization when sections get too full; B-Trees self-balance.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A B-Tree is a special kind of sorted tree used to organize database indexes. It keeps itself perfectly balanced (all paths from root to any leaf are the same length) and stores many values per node. This lets databases find any row in just 3–4 steps, regardless of how many millions of rows the table has.

**Level 2 - How to use it (junior developer):**
`CREATE INDEX idx_name ON table(column)` creates a B-Tree index by default in PostgreSQL and MySQL. B-Tree indexes support: equality (`=`), range (`<`, `>`, `BETWEEN`), `ORDER BY`, and `LIKE 'prefix%'` queries. They do NOT help with `LIKE '%suffix'`, full-text search, or very low cardinality columns (e.g., boolean). `EXPLAIN (ANALYZE)` shows whether index scans are used.

**Level 3 - How it works (mid-level engineer):**
PostgreSQL B-Tree implementation: each page is 8KB; default fill factor 90% (leaves 10% free for inserts without immediate splits). Index pages contain: item pointers, actual keys and value/TID (heap tuple identifier). For multi-column indexes, keys are ordered by first column, then second (leftmost prefix rule). The page-level structure includes a `PageHeaderData` with high key (maximum key in subtree), left and right sibling pointers (enabling range scans without traversing up the tree). B-Tree scans can be ascending or descending without separate index structures (bidirectional scans via sibling pointers).

**Level 4 - Why it was designed this way (senior/staff):**
The B-Tree was designed in the 1970s specifically for disk-based storage where I/O latency dominates. The optimal node size is the storage block size (4KB–16KB) - larger nodes reduce height but increase I/O per cache miss. The choice of m=200 (typical for 8KB pages with 40-byte keys) produces 4-level trees for up to ~1.6 billion entries - effectively constant-depth for any realistic table. The fundamental limitation of B-Trees for write-heavy workloads is write amplification: an insert into a full leaf triggers a page split, writing two full pages. Worst case: a root split rewrites O(log n) pages. LSM Trees (RocksDB, Cassandra storage engine) address this by converting random writes to sequential writes at the cost of read amplification - a deliberate trade-off for write-heavy workloads.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ B-TREE STRUCTURE (order m=3, simplified)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Level 0 (Root):          [30 | 60]                    │
│                          /    |    \                    │
│  Level 1 (Internal): [10|20] [40|50] [70|80]           │
│                      / | \  / | \  / | \               │
│  Level 2 (Leaf):   [.][.][.][.][.][.][.][.][.]        │
│                    (data records / TID pointers)        │
│                                                         │
│  ← Sibling pointers link leaves for range scans →       │
│                                                         │
│  Search for key=45:                                     │
│  Root: 45 > 30, 45 < 60 → middle child [40|50]        │
│  Internal: 45 > 40, 45 < 50 → middle child             │
│  Leaf: scan leaf for 45                                 │
│  Total: 3 disk I/Os (for height-3 tree)                 │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Query: SELECT * FROM orders WHERE customer_id = 42
→ Planner: index available on customer_id?
→ [B-TREE ← YOU ARE HERE: traverse index]
→ Root page load: 42 → child pointer
→ Internal page load: 42 → child pointer
→ Internal page load: 42 → leaf pointer
→ Leaf page load: find TID for customer_id=42
→ Heap page load: fetch actual row data
→ Return row
Total I/Os: 4 (tree height) + 1 (heap fetch)
```

**FAILURE PATH:**

```
Table grows to 10B rows; index height increases to 5
→ All point lookups now require 5 I/Os
→ Most pages cached in buffer pool → 5 cache lookups
→ No real degradation (cached lookups are fast)
→ But: INSERT into full leaf → split → 2 page writes
→ High insert rate → frequent splits → write amplification
→ Use FILLFACTOR=70 to pre-allocate space in leaves
```

**WHAT CHANGES AT SCALE:**
With buffer pool (shared_buffers in PostgreSQL), upper levels of B-Tree are almost always cached - only the leaf pages require disk I/O for cold reads. Hot indexes (accessed frequently) are almost entirely in memory, making the 3–4 I/O cost theoretical. The real scale concern is index bloat from dead entries (deleted rows leave behind index entries until VACUUM cleans them) and page splits from high insert rates on sequential keys (monotonically increasing IDs cause rightmost-leaf splits, requiring periodic `REINDEX`).

---

### ⚖️ Comparison Table

| Index Type        | Point Lookup    | Range Scan        | Write Cost      | Best For                             |
| ----------------- | --------------- | ----------------- | --------------- | ------------------------------------ |
| **B-Tree**        | O(log n)        | O(log n + k)      | Medium (splits) | General purpose - equality + range   |
| B+ Tree           | O(log n)        | O(log n + k) fast | Medium          | Same; all databases use this variant |
| Hash              | O(1)            | N/A               | Low             | Equality only; no range support      |
| LSM Tree          | O(log n)-slower | Slower (merges)   | Very low        | Write-heavy; RocksDB, Cassandra      |
| GiST (PostgreSQL) | Depends         | Depends           | Higher          | Geometric, full-text, custom types   |

How to choose: B-Tree (B+ Tree) is the correct default for 95% of indexed columns. Use hash indexes only for equality-only, no-range-scan columns (PostgreSQL only). Consider LSM-backed storage engines for write-heavy time-series or event data.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                 |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "B-Tree" and "B+ Tree" are the same               | B-Trees store data in all nodes; B+ Trees store data only in leaf nodes (internal nodes store only keys). All databases use B+ Tree, though they often call it "B-Tree" |
| B-Tree indexes help with `LIKE '%suffix'` queries | B-Tree indexes only help with prefix-anchored LIKE (`'prefix%'`) - they cannot accelerate suffix or infix matches without full-text or reverse indexes                  |
| More indexes = faster queries                     | More indexes = slower writes (each INSERT/UPDATE/DELETE must update every index). Index-per-column maximizes read speed at the cost of significant write overhead       |
| B-Tree height grows rapidly with table size       | B-Tree height grows logarithmically - a table growing 10× only increases height by 1 level. Height rarely exceeds 4–5 for any realistic table size                      |

---

### 🚨 Failure Modes & Diagnosis

**1. Index Bloat from Dead Entries**

**Symptom:** Index size is disproportionately large vs. table size; `EXPLAIN` shows index scans reading many pages; query performance degrades despite index existing.

**Root Cause:** Deleted/updated rows leave behind dead index entries. B-Tree pages with many dead entries are not automatically compacted until VACUUM processes them.

**Diagnostic:**

```sql
-- Check index size vs table size
SELECT
  schemaname,
  relname AS table,
  indexrelname AS index,
  pg_size_pretty(pg_relation_size(indexrelid)) AS idx_size,
  pg_size_pretty(pg_relation_size(relid)) AS tbl_size,
  idx_scan,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname = 'orders'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Check dead tuples (using pgstattuple extension)
SELECT * FROM pgstatindex('idx_orders_customer_id');
-- avg_leaf_density < 50% indicates significant bloat
```

**Fix:** `REINDEX INDEX CONCURRENTLY idx_orders_customer_id` - rebuilds index without locking table. `VACUUM ANALYZE orders` - reclaims dead entries and updates statistics.

**Prevention:** Set `autovacuum_vacuum_scale_factor = 0.01` for high-churn tables. Set `fillfactor = 70–80` for hot-insert tables to delay splits.

---

**2. Write Amplification from Sequential Key Inserts**

**Symptom:** Rightmost B-Tree leaf pages are always full; every INSERT causes a page split; `pg_stat_bgwriter.buffers_checkpoint` growing rapidly; insert rate plateauing despite adequate CPU.

**Root Cause:** Monotonically increasing keys (auto-increment IDs, timestamps) always insert into the rightmost leaf - it fills up and splits immediately. With `fillfactor=100` (default for non-index tables), every insert into a full leaf causes a split.

**Diagnostic:**

```sql
-- Check pages, tuples, and dead ratio
SELECT relname,
       relpages,
       reltuples,
       relpages / NULLIF(reltuples,0) * 8 AS avg_row_kb
FROM pg_class
WHERE relname = 'idx_events_created_at';

-- High split rate in pg_stat_user_indexes
SELECT indexrelname, idx_blks_hit, idx_blks_read
FROM pg_statio_user_indexes
WHERE indexrelname = 'idx_events_created_at';
```

**Fix:** Use `fillfactor = 70` for B-Tree indexes on monotonically increasing columns: `CREATE INDEX idx_events_created_at ON events(created_at) WITH (fillfactor=70)`. This leaves 30% of each leaf page free for future inserts before a split is needed.

**Prevention:** Set `fillfactor = 70–80` for any index on an auto-increment or timestamp column. For append-only tables with sequential keys, consider partitioning by time range to limit active index size.

---

**3. Wrong Index Not Used by Query Planner**

**Symptom:** `EXPLAIN` shows `Seq Scan` instead of `Index Scan` despite an index existing on the queried column; query is slow.

**Root Cause:** Planner estimates full table scan is cheaper than index scan - this can happen when: (a) column statistics are stale (run ANALYZE); (b) predicate matches too many rows (low selectivity); (c) `random_page_cost` is too high relative to `seq_page_cost` (tune for SSD); (d) TOAST or type cast prevents index use.

**Diagnostic:**

```sql
-- Check if statistics are current
SELECT relname,
       last_analyze,
       last_autoanalyze,
       n_distinct
FROM pg_stat_user_tables
WHERE relname = 'orders';

-- Check planner cost estimates
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 42;

-- For SSD storage: reduce random_page_cost
SHOW random_page_cost;  -- default 4.0; set to 1.1 for NVMe
```

**Fix:** `ANALYZE orders` to update statistics. Set `random_page_cost = 1.1` for SSD storage in `postgresql.conf`. If index is valid but not used, check for implicit type casts in the WHERE clause (e.g., `WHERE customer_id = '42'` when `customer_id` is integer).

**Prevention:** Enable autovacuum with ANALYZE. Set `random_page_cost` appropriately for storage type. Check column statistics with `\d+ table_name` and `pg_stats`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Index Types (B-Tree, Hash, Composite, Covering)` - B-Tree is the most common index type; understand the taxonomy
- `Query Planner / Execution Plan` - the planner decides when to use B-Tree indexes

**Builds On This (learn these next):**

- `B+ Tree` - the actual variant all databases use (data in leaf nodes only)
- `LSM Tree` - the write-optimized alternative to B-Trees for high-write workloads
- `EXPLAIN` - the tool for verifying B-Tree indexes are being used

**Alternatives / Comparisons:**

- `LSM Tree` - write-optimized; accepts higher read cost for dramatically lower write cost
- `Hash Index` - O(1) equality; no range support; rarely used in practice
- `GiST / GIN / SP-GiST` (PostgreSQL) - specialized index structures for geometric, full-text, array data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Self-balancing multi-way search tree      │
│              │ with hundreds of keys per node            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Full table scans are O(n) - too slow      │
│ SOLVES       │ for any selective query on large tables   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ fan-out=200 → height=4 for 1B rows        │
│              │ = only 4 disk I/Os for any lookup         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Point lookups, range queries, ORDER BY,   │
│              │ JOIN conditions - default choice          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Write-heavy append-only (use LSM);        │
│              │ equality-only (hash); full-text (GIN)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fast reads (O(log n)) at cost of          │
│              │ write amplification (page splits)         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Phone book in tree form - find anything  │
│              │  in 3–4 hops no matter how large"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ B+ Tree → LSM Tree → Index Types          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE B - Scale Thought Experiment) A social media platform has an `events` table with 500 billion rows growing at 1 million inserts/second. The primary key is a monotonically increasing `event_id`. The B-Tree index on `event_id` has height 6. What specific write amplification pattern occurs, why does the rightmost-leaf problem get worse over time, and what two architectural changes would you make to prevent B-Tree write amplification at this scale?

**Q2.** (TYPE C - Design Trade-off) A product search system needs to support three query types: (a) exact product_id lookup, (b) price range queries (price BETWEEN X AND Y), (c) full-text description search. A DBA suggests creating three separate indexes. Compare: B-Tree for (a) and (b), full-text GIN index for (c), vs. a single covering B-Tree index on (product_id, price, description). What are the trade-offs in read performance, write overhead, and storage cost for each approach?
