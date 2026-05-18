---
id: DSA-081
title: "B+ Tree (Database Indexing Internals)"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-055
used_by: DSA-077, DSA-104
related: DSA-055, DSA-083, DSA-104
tags:
  - data-structures
  - b-plus-tree
  - database-index
  - range-scan
  - postgresql
  - mysql
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 81
permalink: /technical-mastery/dsa/b-plus-tree/
---

## TL;DR

A B+ Tree stores all data in leaf nodes (linked in a sorted
list) and keeps internal nodes as pure routing keys - this
enables both O(log n) point lookups AND efficient O(k)
range scans, making it the default index structure in
PostgreSQL, MySQL, and Oracle.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-081 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, B+-Tree, database-index |
| **Prerequisites** | DSA-055 |

---

### The Problem This Solves

B-trees store data in any node. For range queries
("WHERE salary BETWEEN 50000 AND 80000"), you must
traverse multiple branches - slow. B+ trees fix this:
all data lives in leaf nodes, linked sequentially.
Range scan = find start leaf, follow the linked list
to end. O(log n + k) where k = result count.

---

### Textbook Definition

A B+ Tree is a variant of the B-tree where:
1. All actual data records (or row pointers) are stored
   exclusively in leaf nodes
2. Internal nodes contain only key-value pairs used for
   routing (no actual data)
3. Leaf nodes are linked in a doubly-linked sorted list
4. Every key in the tree appears in a leaf node; some
   also appear in internal routing nodes

This structure enables: point lookup O(log n), range
scan O(log n + k), sequential scan O(n) via leaf list.

---

### How It Works

**Structure visualization:**

```
B+ Tree on salary column:

Internal nodes (routing only):
         [50000, 75000]
        /       |        \
  [25000,40000] [60000,70000] [80000,90000]
 
Leaf nodes (actual data, linked):
[10K→r1][25K→r5][40K→r2] ↔ [50K→r7][60K→r3][70K→r9] ↔ [75K→r4][80K→r8][90K→r6]
         ↑_________________________________________leaf linked list_______________↑

Range query: WHERE salary BETWEEN 40000 AND 75000
1. Navigate tree to find leaf with 40000: O(log n)
2. Follow linked list: 40K, 50K, 60K, 70K, 75K → done
3. Total: O(log n + k) where k=5 results
```

**PostgreSQL index internals:**

```sql
-- This creates a B+ tree index internally
CREATE INDEX idx_salary ON employees(salary);

-- Point lookup: O(log n) - navigates internal nodes to leaf
SELECT * FROM employees WHERE salary = 75000;

-- Range scan: O(log n + k) - finds start, follows leaf list
SELECT * FROM employees WHERE salary BETWEEN 40000 AND 80000;

-- Sequential scan: O(n) - follows all leaf links
SELECT * FROM employees ORDER BY salary;
-- B+ tree enables this WITHOUT a sort! Leaves are already sorted.

-- EXPLAIN ANALYZE to see B+ tree in action:
EXPLAIN ANALYZE SELECT * FROM employees WHERE salary BETWEEN 40000 AND 80000;
-- Shows: Index Scan using idx_salary, Pages Read: 3 (log n)
```

---

### Comparison Table

| Property | B-Tree | B+ Tree |
|---------|--------|---------|
| Data location | Any node | Leaf nodes only |
| Internal nodes | Data + routing | Routing only |
| Range scan | Slower (traverse branches) | Faster (linked leaf list) |
| Point lookup | O(log n) | O(log n) |
| Sequential scan | O(n) with branch traversal | O(n) via linked list |
| DB usage | Rare | PostgreSQL, MySQL, Oracle |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "B-tree and B+ tree are interchangeable terms in DB context" | When databases say "B-tree index," they almost always mean B+ tree; pure B-trees are rarely used in databases |
| "More indexes = faster queries" | Each index = one B+ tree; write operations must update ALL indexes; too many indexes slows INSERT/UPDATE significantly |

---

### Failure Modes & Diagnosis

**Failure: Index not used for range query**
- Cause: Leading column of composite index not in WHERE
  clause; or column with low cardinality (boolean field)
- Diagnosis: EXPLAIN ANALYZE shows "Seq Scan" instead
  of "Index Scan"
- Fix: Ensure leading column is in filter; add partial
  index for low-cardinality columns

---

### Quick Reference Card

| Operation | B+ Tree Time |
|-----------|-------------|
| Point lookup | O(log n) |
| Range scan | O(log n + k) |
| Insert | O(log n) + possible page split |
| Delete | O(log n) + possible merge |
| Sequential scan | O(n) |

---

### The Surprising Truth

B+ tree nodes are sized to match disk pages (typically
8KB in PostgreSQL, 16KB in MySQL). When PostgreSQL reads
an index node, it reads exactly one disk page - loading
all keys in that node into cache in one I/O. This is
intentional: the B+ tree order is tuned so one disk page
holds exactly one node. For a 100M-row table with 8-byte
integer keys, a B+ tree has height 4 - meaning 4 disk
reads for any lookup. This number hasn't changed in 40
years of database evolution.

---

### Mastery Checklist

- [ ] Explains why B+ tree is better than B-tree for
      range scans (linked leaf list)
- [ ] Knows node size = disk page size is intentional
- [ ] Can read EXPLAIN ANALYZE output for index scans

---

### Interview Deep-Dive

**Q1 (Hard):** Why does a composite index (a, b, c) help
for WHERE a=1 AND b=2 but NOT for WHERE b=2 AND c=3?

> B+ tree keys are sorted by (a, b, c) in that order.
> A node at depth k represents a specific prefix of
> (a, ...). Navigating the tree requires matching the
> leftmost columns first.
> WHERE a=1 AND b=2: navigate using a=1 first (O(log n)),
> then filter b=2 within that subtree. Index useful.
> WHERE b=2 AND c=3: no constraint on a. The B+ tree
> is sorted by a first - all values of a may contain
> b=2, requiring a full index scan. Effectively no
> better than a sequential scan.
> Fix: create separate index on (b, c) OR include
> a in WHERE clause. This is the "leftmost prefix rule."
