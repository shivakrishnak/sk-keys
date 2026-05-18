---
id: DSA-055
title: B-Tree
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-017, DSA-053
used_by: DSA-081
related: DSA-053, DSA-054, DSA-081
tags:
  - data-structures
  - b-tree
  - database
  - disk
  - index
  - o-log-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/dsa/b-tree/
---

## TL;DR

A B-tree is a self-balancing multi-way search tree optimized
for disk I/O - each node holds many keys, minimizing tree
height and therefore disk reads; the data structure behind
every database index.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-055 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, B-tree, database, disk-index |
| **Prerequisites** | DSA-017, DSA-053 |

---

### The Problem This Solves

A binary tree with 1 billion nodes needs height ~30 (log2 n).
Every node access = one disk I/O (4KB typical page).
30 disk I/Os × 5ms each = 150ms per lookup - unacceptably
slow. A B-tree with branching factor 1000 needs height ~3
for the same 1 billion records (log1000 n ≈ 3). 3 disk
I/Os = 15ms. This is why every RDBMS uses B-trees.

---

### Textbook Definition

A B-tree of order m is a rooted tree where: every node
has at most m children; every non-root node has at least
⌈m/2⌉ children; all leaves are at the same depth (perfectly
balanced); a node with k children contains k-1 sorted keys.
Insertion and deletion maintain balance via splits and merges.
Time: O(log n) for all operations.

---

### Understand It in 30 Seconds

```
B-tree of order 5 (max 4 keys per node, max 5 children):

         [30, 70]
        /    |    \
[10,20]  [40,50,60]  [80,90]

All leaves at depth 1. 3 nodes instead of 9 nodes
for a binary tree with same data.
With order 1000: 1 node holds 999 keys, 1000 children.
10^9 records: height ≈ 3.
```

---

### How It Works

**Node splits on insert:**

```
Insert 45 into B-tree of order 3 (max 2 keys):

Before: [10, 30]
         / |  \
       [5] [20] [35,40,45] ← OVERFLOW! (3 keys, max=2)

Split [35,40,45]:
  Promote middle key (40) to parent
  Left: [35], Right: [45]

After:
        [10,30,40]
        / |   |  \
      [5][20][35][45]
```

**B+ tree (variant used by databases):**

```
All data in leaf nodes, internal nodes hold only keys.
Leaves form a linked list → supports range scans.

        [30, 70]
       /    |    \
[10,20] [30,50,60] [70,80,90]
   ↕          ↕           ↕
[data]     [data]      [data]
```

**Why RDBMS uses B+ tree, not binary BST:**

| Property | Binary BST | B+ Tree |
|---------|-----------|---------|
| Disk I/Os per lookup | O(log2 n) = ~30 for 10^9 | O(log1000 n) ≈ 3 |
| Keys per node | 1 | 100-1000 |
| Range scan | O(n) | O(log n + k) via leaf list |
| Cache line fit | No | Yes (node = disk page = 4KB) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Database indexes use binary trees" | RDBMSs use B+ trees (variant of B-tree with all data in leaves); binary trees would be too tall for disk I/O |
| "B-tree and B+ tree are the same" | B-tree: data can be in any node. B+ tree: data only in leaves; internal nodes are "router" keys only. Databases use B+ tree |

---

### Failure Modes & Diagnosis

**Failure: Poor index performance despite B-tree index**
- Cause: Low cardinality column (e.g., boolean is_active)
  causes every lookup to return 50% of rows; B-tree index
  not useful
- Fix: Index selective columns; partial index or composite
  index for low-cardinality + high-cardinality combination

---

### Quick Reference Card

| Property | B-tree (order m) |
|---------|-----------------|
| Keys per node | 1 to m-1 |
| Children per node | 2 to m |
| Height | O(log_m n) |
| All ops | O(log n) |
| Disk I/Os | O(log n), typically 2-4 |
| Database variant | B+ tree (data in leaves) |

---

### The Surprising Truth

PostgreSQL's default index type is B-tree. MySQL InnoDB
uses B+ tree. Oracle, SQL Server - all B+ tree. Despite
decades of research into competing structures (LSM trees,
fractal trees, skip lists), B+ trees remain dominant
for traditional RDBMS indexes because they optimize for
the read-heavy, range-scan workload of typical OLTP queries.
NoSQL databases (RocksDB, Cassandra) use LSM trees for
write-heavy workloads.

---

### Mastery Checklist

- [ ] Can explain why B-trees have O(1) to O(3) disk I/Os
      vs O(30) for a binary tree on 1 billion records
- [ ] Understands the difference between B-tree and B+ tree
- [ ] Knows why databases use B+ tree (range scans via
      linked leaf list)

---

### Interview Deep-Dive

**Q1 (Hard):** Why does PostgreSQL use a B-tree index
instead of a hash index for range queries?

> Hash indexes compute hash(key) → bucket. O(1) lookup
> for exact match. But they cannot support range queries
> (BETWEEN, >, <) because hash values have no ordering
> relationship - all keys in [10, 100] may hash to random
> buckets with no way to scan them in order.
> B-tree nodes store keys in sorted order. Range query
> [10, 100]: find 10 in O(log n), then scan sequentially
> to 100 in O(k) where k = matching records. B+ tree's
> linked leaf list makes this scan especially efficient
> (sequential disk reads). PostgreSQL maintains both index
> types: B-tree for range queries, hash for exact equality
> when explicitly chosen.
