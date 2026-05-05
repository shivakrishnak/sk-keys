---
layout: default
title: "B+ Tree"
parent: "Database Fundamentals"
nav_order: 426
permalink: /databases/b-plus-tree/
number: "0426"
category: Database Fundamentals
difficulty: ★★★
depends_on: B-Tree, Index Types
used_by: Query Planner / Execution Plan, EXPLAIN
related: B-Tree, LSM Tree, Index Types
tags:
  - database
  - data-structures
  - indexing
  - deep-dive
---

# 426 — B+ Tree

⚡ TL;DR — A B+ Tree stores data only in leaf nodes (internal nodes hold only keys as guides) and links all leaf nodes in a doubly-linked list — enabling both fast point lookups and extremely efficient range scans without re-traversing the tree.

| #426            | Category: Database Fundamentals         | Difficulty: ★★★ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | B-Tree, Index Types                     |                 |
| **Used by:**    | Query Planner / Execution Plan, EXPLAIN |                 |
| **Related:**    | B-Tree, LSM Tree, Index Types           |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A plain B-Tree stores data records in every node — internal and leaf. A range scan (`WHERE price BETWEEN 10 AND 50`) must traverse multiple subtrees, and after finding the first matching key in an internal node, it must descend into multiple branches to find all remaining matching records. Each branch descent is one or more disk I/Os. For a range returning 10,000 rows, this is many non-sequential disk I/Os — slow.

**THE BREAKING POINT:**
Database workloads are dominated by range scans, not just point lookups — `ORDER BY`, `BETWEEN`, `>=`, pagination. Optimizing for point lookups alone (as a pure B-Tree does) leaves range scan performance on the table.

**THE INVENTION MOMENT:**
"If all data is in leaf nodes and leaf nodes are linked, any range scan is a single tree traversal to the start, then a linear scan through a linked list of leaf pages — maximally sequential."

---

### 📘 Textbook Definition

A **B+ Tree** is a variant of the B-Tree where: (1) all data records (or row pointers) are stored only in leaf nodes — internal nodes store only keys as routing guides; (2) all leaf nodes are linked in a doubly-linked list ordered by key. Internal nodes are denser (more keys per node, since they store no data records), reducing tree height. Leaf nodes form a sorted linked list enabling sequential range scans. This structure is universally used as the default B-Tree index in all major relational databases (PostgreSQL, MySQL InnoDB, Oracle, SQL Server) — when databases say "B-Tree index," they mean B+ Tree.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
B+ Tree = B-Tree where internal nodes are navigation-only and leaf nodes form a sorted linked list, making range scans sequential.

**One analogy:**

> An encyclopedia index. The index pages (internal nodes) tell you which volume and page range to go to — they don't contain the actual content. All actual content is in the encyclopedia pages (leaf nodes), arranged in alphabetical order, with "continued on next page" links connecting them. To find "Astronomy": look up the index (3 steps) → go to the A-volume → scan forward through the sorted pages to find all Astronomy entries. The index is pure navigation; the actual content is only in the pages; the pages are linked for sequential scanning.

**One insight:**
Because internal nodes store only keys (not data), an internal node fits more keys in the same 8KB page — higher fan-out (more children per node) → shorter tree height. And because leaf nodes are linked, any range scan is: traverse to start key (O(log n)) + linear linked-list scan for matching entries (O(k) where k = number of matches). No further tree traversal needed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Internal nodes: contain only keys (routing values) and child pointers. No data records.
2. Leaf nodes: contain key-value pairs (key + row pointer or entire row for clustered index).
3. Leaf nodes: linked in a doubly-linked list sorted by key.
4. Every key in an internal node also appears in a leaf node (leaf nodes contain all keys).
5. Balance: all leaf nodes at same depth.

**DERIVED DESIGN:**
**Internal node (order m, key size 8B, pointer 6B):**

```
8KB page = 8192 bytes
Each slot: 8B key + 6B pointer = 14 bytes
Slots per page: ~8192 / 14 ≈ 585 keys
Fan-out = 586 children per internal node
```

Higher fan-out → shorter tree. A B+ Tree with fan-out 500 holds:

- Height 1: 500 leaves = ~37,500 rows
- Height 2: 250,000 leaves = ~18.75M rows
- Height 3: 125M leaves = ~9.4B rows

3 levels cover ~9.4 billion rows with 3 disk I/Os (plus 1 for heap fetch).

**Clustered vs. Secondary:**

- **Clustered index (InnoDB):** Leaf nodes contain the actual row data. Primary key = clustered index. Rows physically sorted by primary key on disk. Only one per table.
- **Secondary index (InnoDB):** Leaf nodes contain primary key values (not row data). Lookup requires: secondary index traversal → primary key → clustered index lookup (two B+ Tree traversals). PostgreSQL heap-based indexes: leaf nodes always contain TID (heap pointer); all indexes are "secondary."

**THE TRADE-OFFS:**
**Gain (vs. B-Tree):** Higher internal node fan-out (no data in internal nodes → more keys per node → shorter tree). Sequential range scans (leaf linked list). More predictable I/O for range queries.
**Cost (vs. B-Tree):** Write amplification from page splits (same as B-Tree). Not optimal for write-heavy workloads (see LSM Tree). Every update must update both the old leaf entry and the new one.

---

### 🧪 Thought Experiment

**SETUP:**
A table has `orders(order_id, customer_id, amount, created_at)`. Two query patterns:

1. Point: `WHERE order_id = 12345678`
2. Range: `WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31'` — returns 500,000 rows

**PLAIN B-TREE behavior (hypothetical, data in all nodes):**
Range scan: traverse to first matching key in any node level. Some matches are in internal nodes, some in leaves. To traverse all matches, must revisit multiple subtrees. Each subtree re-entry requires 2–3 disk I/Os. For 500,000 results spread across many subtrees: potentially thousands of non-sequential disk I/Os.

**B+ TREE behavior (actual behavior):**
Range scan:

1. Traverse from root to first leaf node with `created_at >= '2024-01-01'`: 3 disk I/Os.
2. Scan leaf linked list forward until `created_at > '2024-01-31'`.
3. For 500,000 results at ~100 entries per leaf page: ~5,000 leaf page reads.
4. Leaf pages in this range are physically adjacent (if table is clustered by created_at) or physically adjacent on the index (sequential linked-list scan).
5. At 128 leaf pages per I/O prefetch: ~40 prefetch operations.

**THE INSIGHT:**
For range queries returning many rows, B+ Tree's leaf linked list transforms potentially thousands of random disk I/Os (B-Tree) into a sequential scan of a sorted linked list. The difference is significant for storage performance: sequential reads are 10–100× faster than random reads on HDDs; 3–5× faster on SSDs.

---

### 🧠 Mental Model / Analogy

> A B+ Tree is like a sorted filing cabinet with a master index at the front. The master index (internal nodes) tells you exactly which drawer and which section holds what you need — but the index itself contains no documents, only labels and pointers. All documents are in the actual drawer files (leaf nodes). Every drawer connects to the next with a "next section" pointer (linked list). To find all invoices from January: look up the index (3 steps) → go to the January drawer → read through drawer-by-drawer until you hit February.

- "Master index pages" → internal B+ Tree nodes (routing-only, no data)
- "Drawer files" → leaf B+ Tree nodes (all data here)
- "Next section pointer between drawers" → doubly-linked list of leaf nodes
- "Reading drawer-by-drawer" → sequential leaf list scan for range queries

Where this analogy breaks down: physical drawers hold real documents; B+ Tree leaf nodes for secondary indexes hold only pointers (TIDs or primary keys) — to get the actual row data, a second lookup (heap fetch) is needed.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A B+ Tree is the tree structure behind every database index. It organizes data so that finding any single value takes 3–4 steps (from root to leaf), and finding a range of values — like "all orders from last month" — is efficient because all the leaves are connected in a sorted chain, so you scan forward through the chain without jumping back to the top of the tree.

**Level 2 — How to use it (junior developer):**
When you create an index in PostgreSQL (`CREATE INDEX`) or MySQL InnoDB (`CREATE INDEX`), you're creating a B+ Tree. Use `EXPLAIN` to confirm index scans. For range queries, ensure the leftmost column in the index matches your range predicate. Understand index-only scans: if your SELECT columns are all in the index, no heap fetch needed — PostgreSQL uses a "visibility map" to enable index-only scans without checking the heap for every tuple.

**Level 3 — How it works (mid-level engineer):**
PostgreSQL B+ Tree page types: meta page (tracks root page number), internal pages (item pointers + keys + child page numbers), leaf pages (item pointers + keys + heap TIDs). Leaf pages have `PageHeaderData.pd_special` pointing to the next leaf page (one-directional linked list in PostgreSQL). Range scan: start at root → traverse to first leaf matching the range predicate → follow leaf's `pd_special` pointer to next leaf → continue until range exhausted. InnoDB clustered index: leaf pages contain full row data (no heap fetch needed for clustered index scans). InnoDB secondary index: leaf pages contain primary key → must do clustered index lookup ("double-dip") for non-covered queries.

**Level 4 — Why it was designed this way (senior/staff):**
The split between internal (routing) nodes and leaf (data) nodes is a deliberate engineering decision that emerged from the observation that internal nodes are accessed on every traversal (cached in buffer pool with high probability) while leaf nodes are accessed only for their data. Storing data only in leaves maximizes internal node fan-out (smaller keys → more per page → shallower tree) and makes the internal nodes small enough to stay permanently cached. The leaf linked list exploits the observation that range scans are sequential by definition — connecting leaves eliminates the need to re-traverse upper tree levels for each new leaf in the range. InnoDB's clustered index design (rows in leaves of the primary key B+ Tree) is the database equivalent of a "clustered file" — physically ordering data by primary key on disk to make range scans on the primary key sequential disk reads. This is why choosing a random UUID as a primary key in InnoDB is catastrophic for write performance: every new UUID inserts into a random location in the clustered index, causing maximum random I/O and page splits — sequential IDs (auto-increment, ULIDs, Twitter Snowflake) insert at the rightmost leaf, making writes sequential.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ B+ TREE: STRUCTURE vs PLAIN B-TREE                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Plain B-Tree:            B+ Tree:                   │
│  Internal nodes have      Internal nodes:            │
│  data + keys:             routing-only (keys only):  │
│  [10|data] [20|data]      [30] [60]                  │
│  [30|data] ...            /      \                   │
│                          [10|20]  [40|50]            │
│                          ↓  ↓  ↓  ↓  ↓  ↓           │
│  Leaf level:             L0→L1→L2→L3→L4→L5          │
│                          (doubly-linked list)        │
│                          All data only in leaves     │
│                                                      │
│  Range scan WHERE key BETWEEN 15 AND 45:             │
│  1. Traverse to leaf containing key=15: 3 I/Os       │
│  2. Scan linked list forward: L1→L2→L3→L4           │
│     (4 sequential leaf pages = 4 I/Os)              │
│  3. Stop when key > 45                               │
│  Total: ~7 I/Os for range of 4 leaves               │
│                                                      │
│  vs. Full table scan for same range: 1000+ I/Os      │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Query: SELECT * FROM orders WHERE order_date >= '2024-01-01'
→ Query planner: B+ Tree index on order_date available
→ [B+ TREE ← YOU ARE HERE: traversal + leaf scan]
→ Root page read: find child containing '2024-01-01'
→ Internal page read: narrow to leaf range
→ Leaf page read: first matching leaf
→ Leaf-to-leaf scan via linked list: read sequential leaves
→ For each leaf entry: TID → heap fetch (unless covering index)
→ Return rows
```

**FAILURE PATH:**

```
InnoDB clustered index with random UUID primary key
→ Every INSERT finds a random leaf position
→ Page split probability: ~50% (random inserts into full pages)
→ Write amplification: 2× page writes per insert (split)
→ Insert rate degrades at scale → use sequential IDs
```

**WHAT CHANGES AT SCALE:**
At large table sizes, the upper B+ Tree levels (root and first 1–2 internal levels) are almost permanently cached in the buffer pool. The real I/O cost is only for leaf pages on cache misses. For range scans on hot indexes (e.g., recent orders by created_at), the leaf pages are also frequently cached — making range scans essentially in-memory linked-list traversals. The operational concern at scale is leaf page fragmentation: frequent updates/deletes fragment the leaf linked list, causing non-sequential page reads. `REINDEX CONCURRENTLY` rebuilds the B+ Tree with packed leaf pages, restoring sequential access patterns.

---

### ⚖️ Comparison Table

| Property          | B-Tree                      | B+ Tree                               | LSM Tree                            |
| ----------------- | --------------------------- | ------------------------------------- | ----------------------------------- |
| Data location     | All nodes                   | Leaf nodes only                       | SSTable files (disk)                |
| Internal fan-out  | Lower (data in nodes)       | Higher (routing only)                 | N/A                                 |
| Range scan        | Multiple subtree traversals | Leaf linked list — sequential         | Merge read from multiple levels     |
| Point lookup      | O(log n)                    | O(log n)                              | O(log n) — slower (multiple levels) |
| Write performance | Medium (splits)             | Medium (splits)                       | Excellent (append-only memtable)    |
| Used by           | Theoretical only            | PostgreSQL, MySQL, Oracle, SQL Server | RocksDB, Cassandra, LevelDB         |

How to choose: B+ Tree for all relational database use cases. LSM Tree when write throughput is the primary concern and slightly higher read latency is acceptable (time-series, event stores, Cassandra).

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                  |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL uses B-Tree; it's not a B+ Tree              | PostgreSQL's B-Tree indexes ARE B+ Trees — internal nodes contain only keys; leaf nodes contain TIDs; leaf nodes are linked                              |
| InnoDB's clustered index is just an index               | InnoDB's clustered index IS the table — the rows live in the leaf nodes of the primary key B+ Tree; there is no separate heap storage                    |
| UUID primary keys are fine performance-wise             | Random UUID primary keys destroy InnoDB clustered index performance at scale — random inserts cause 50%+ page split rates; use sequential IDs            |
| B+ Tree range scans read all leaf pages between L and R | B+ Tree range scans read only the leaf pages that contain rows matching the range predicate — if many rows match, that's many pages; but it's sequential |

---

### 🚨 Failure Modes & Diagnosis

**1. InnoDB UUID Primary Key Write Amplification**

**Symptom:** INSERT throughput degrades as InnoDB table grows beyond a few million rows; `SHOW ENGINE INNODB STATUS` shows very high number of page splits; disk I/O spikes on inserts.

**Root Cause:** Random UUID (v4) primary keys insert into random positions in the B+ Tree clustered index. As the index fills, every insert hits a full leaf page, causing a split: two half-full pages written, plus the parent updated. Page split rate approaches 1 split per insert as the tree fills.

**Diagnostic:**

```sql
-- MySQL: Check page split frequency
SHOW ENGINE INNODB STATUS\G
-- Look for: BUFFER POOL AND MEMORY
-- Pages written vs pages read ratio

-- Check average fill factor
SELECT
  INDEX_NAME,
  STAT_VALUE as pages_count
FROM mysql.innodb_index_stats
WHERE table_name = 'orders'
  AND stat_name = 'n_leaf_pages';
```

**Fix:** For new tables, switch to `BIGINT AUTO_INCREMENT` or a time-ordered UUID variant (UUID v7, ULID). For existing tables with UUID PKs: add an integer surrogate key as the clustered index PK; keep UUID as a unique secondary index.

**Prevention:** Never use random UUID (v4) as InnoDB primary key for high-insert-rate tables. Use `AUTO_INCREMENT`, ULID, or UUID v7 (time-ordered) instead.

---

**2. Index-Only Scan Regression After High Delete Rate**

**Symptom:** Queries using index-only scans (visible in `EXPLAIN` as `Index Only Scan`) start performing heap fetches unexpectedly; performance regression on previously fast queries.

**Root Cause (PostgreSQL):** Index-only scans rely on the visibility map — pages marked "all visible" don't require a heap fetch to check tuple visibility. High delete rates create "not all visible" pages (dead tuples present), forcing the planner to fetch the heap anyway. The index-only scan degrades to a standard index scan.

**Diagnostic:**

```sql
-- Check visibility map coverage
SELECT relname,
       n_live_tup,
       n_dead_tup,
       last_autovacuum,
       last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 'products';

-- Check if VACUUM restores index-only scan performance
VACUUM ANALYZE products;
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, price FROM products WHERE price < 100;
```

**Fix:** Run `VACUUM ANALYZE` to update visibility map and remove dead tuples. Ensure autovacuum is configured aggressively for high-churn tables.

**Prevention:** Set `autovacuum_vacuum_cost_delay = 2ms` and `autovacuum_vacuum_scale_factor = 0.01` for tables with high delete rates. Monitor `n_dead_tup / n_live_tup` ratio.

---

**3. B+ Tree Height Increases Without Bound (Rare)**

**Symptom:** Point lookup performance degrades over years; `EXPLAIN` shows more buffer hits than expected for index scans; index size disproportionately large.

**Root Cause:** Rare, but possible in pathological cases: index never rebalanced after many deletes left pages with very few entries (underfull); tree grows taller than necessary.

**Diagnostic:**

```sql
-- PostgreSQL: check B-Tree height
-- Requires pageinspect extension
CREATE EXTENSION IF NOT EXISTS pageinspect;

-- Get root page
SELECT * FROM bt_metap('idx_orders_customer_id');
-- level field = tree height (should be 3–5 for large tables)
```

**Fix:** `REINDEX INDEX CONCURRENTLY idx_orders_customer_id` — rebuilds with optimal packing, restoring correct height.

**Prevention:** Periodic `REINDEX CONCURRENTLY` for high-churn indexes (tables with heavy DELETE rates). Include index bloat monitoring in database health checks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `B-Tree` — understand the base structure before the B+ Tree variant
- `Index Types (B-Tree, Hash, Composite, Covering)` — B+ Tree is the implementation behind most index types

**Builds On This (learn these next):**

- `LSM Tree` — the alternative for write-heavy workloads
- `Query Planner / Execution Plan` — the planner decides when to use B+ Tree indexes
- `EXPLAIN` — verify B+ Tree index usage and scan types

**Alternatives / Comparisons:**

- `LSM Tree` — write-optimized; accepts read amplification
- `Hash Index` — O(1) equality; no range; limited use cases
- `B-Tree` — the theoretical predecessor; B+ Tree is universally preferred in practice

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ B-Tree variant: data only in leaves;      │
│              │ leaves linked for sequential range scans  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ B-Trees need to re-traverse tree for      │
│ SOLVES       │ range scans — B+ Tree uses leaf list      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Internal nodes = routing only → higher    │
│              │ fan-out → shorter tree + faster range     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All relational DB indexes — it's the      │
│              │ default everywhere                        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ InnoDB: avoid random UUID PKs;            │
│              │ use sequential IDs for clustered index    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Sequential range scans vs write           │
│              │ amplification from page splits            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Data only in leaves, leaves in a chain — │
│              │  reach the start, then scan forward"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LSM Tree → Index Types → EXPLAIN          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D — Failure Scenario) An e-commerce platform migrates from PostgreSQL to MySQL InnoDB and uses UUID v4 as the primary key for all tables. Six months later, they report that INSERT performance degrades by 80% after each table exceeds 10M rows. Trace the exact mechanism — from random UUID generation to B+ Tree page splits — that causes this degradation. What is the fix, and how do you migrate existing data without downtime?

**Q2.** (TYPE F — Comparison Depth) PostgreSQL uses a heap-and-secondary-index model: all B+ Tree indexes point to heap TIDs. InnoDB uses a clustered index model: the primary key B+ Tree contains the actual rows; secondary indexes contain primary key values. Compare the performance characteristics of a query `SELECT name, email FROM users WHERE email = 'user@example.com'` in both systems when: (a) there is only a B+ Tree index on `email`; (b) there is a covering index `(email, name)`. What is the "double-dip" problem in InnoDB and when does it matter?
