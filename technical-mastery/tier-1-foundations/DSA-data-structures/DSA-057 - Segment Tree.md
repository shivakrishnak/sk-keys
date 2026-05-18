---
id: DSA-057
title: Segment Tree
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-016, DSA-026
used_by: DSA-058
related: DSA-058, DSA-028
tags:
  - data-structures
  - segment-tree
  - range-query
  - o-log-n
  - competitive-programming
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 57
permalink: /technical-mastery/dsa/segment-tree/
---

## TL;DR

A Segment Tree answers range aggregate queries (sum, min,
max) in O(log n) and supports point or range updates in
O(log n) - versus O(n) brute force for each query.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-057 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, segment-tree, range-query |
| **Prerequisites** | DSA-016, DSA-026 |

---

### The Problem This Solves

Given an array [1, 3, 5, 7, 9, 11], answer:
- "What is the sum from index 2 to 4?" repeatedly
- "Update index 3 to 6, then re-query."

Brute force: O(n) per query, O(n) per update.
Segment Tree: O(log n) per query, O(log n) per update.
Prefix sum array: O(1) query, O(n) update - can't handle
dynamic updates.

---

### Textbook Definition

A Segment Tree is a binary tree built over an array where
each node covers a range [l, r] of array indices and stores
an aggregate (sum, min, max) over that range. Leaves hold
individual elements. Internal nodes combine their children.
The tree has height O(log n) and uses O(n) space (4*n array
is a common backing store). Build: O(n). Query: O(log n).
Update: O(log n).

---

### Understand It in 30 Seconds

```
Array: [1, 3, 5, 7, 9, 11]  (sum over range)

Segment tree (sum):
         [36]          [0..5]
        /      \
     [9]       [27]    [0..2], [3..5]
    /   \      /   \
 [4]  [5]  [16] [11]  [0..1],[2],[3..4],[5]
  / \
[1] [3]                  [0],[1]

Query sum[2..4]: sum(arr[2..4])=5+7+9=21
Decompose [2..4] into O(log n) covered nodes.
```

---

### How It Works

**Array-backed implementation (popular approach):**

```java
class SegmentTree {
    private final int[] tree;
    private final int n;

    SegmentTree(int[] arr) {
        n = arr.length;
        tree = new int[4 * n]; // safe upper bound
        build(arr, 0, 0, n - 1);
    }

    // Build: O(n)
    void build(int[] arr, int node, int l, int r) {
        if (l == r) {
            tree[node] = arr[l];
            return;
        }
        int mid = (l + r) / 2;
        build(arr, 2 * node + 1, l, mid);
        build(arr, 2 * node + 2, mid + 1, r);
        tree[node] = tree[2*node+1] + tree[2*node+2]; // sum
    }

    // Query sum [ql..qr]: O(log n)
    int query(int node, int l, int r, int ql, int qr) {
        if (qr < l || r < ql) return 0;   // out of range
        if (ql <= l && r <= qr) return tree[node]; // fully covered
        int mid = (l + r) / 2;
        return query(2*node+1, l, mid, ql, qr) +
               query(2*node+2, mid+1, r, ql, qr);
    }

    // Point update: O(log n)
    void update(int node, int l, int r, int idx, int val) {
        if (l == r) {
            tree[node] = val;
            return;
        }
        int mid = (l + r) / 2;
        if (idx <= mid) update(2*node+1, l, mid, idx, val);
        else            update(2*node+2, mid+1, r, idx, val);
        tree[node] = tree[2*node+1] + tree[2*node+2];
    }

    // Public API
    int query(int l, int r) { return query(0, 0, n-1, l, r); }
    void update(int idx, int val) { update(0, 0, n-1, idx, val); }
}
```

---

### Comparison Table

| Structure | Build | Query | Update | Use case |
|-----------|-------|-------|--------|---------|
| Brute force | O(n) | O(n) | O(1) | Few queries |
| Prefix sum | O(n) | O(1) | O(n) | Static data |
| Segment Tree | O(n) | O(log n) | O(log n) | Dynamic range |
| BIT (Fenwick) | O(n) | O(log n) | O(log n) | Sum/freq only |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Segment tree is overkill for most problems" | For any problem with repeated range queries + updates, O(n) per query becomes infeasible; segment tree is the standard solution |
| "Segment tree always uses O(n) space" | The 4n array backing store guarantees it, but lazy-propagation segment trees (for range updates) also use O(n) - just a larger constant |

---

### Failure Modes & Diagnosis

**Failure: Segment tree gives wrong answers after updates**
- Cause: Forgot to propagate aggregate up the tree after
  leaf update; only leaf is updated but internal node
  remains stale
- Fix: Always re-merge internal nodes on the path from
  updated leaf back to root:
  `tree[node] = tree[left] + tree[right]` at each level

---

### Quick Reference Card

| Operation | Time | Space |
|-----------|------|-------|
| Build | O(n) | O(n) |
| Point query | O(log n) | - |
| Range query | O(log n) | - |
| Point update | O(log n) | - |
| Range update + lazy | O(log n) | O(n) |

---

### The Surprising Truth

Segment trees appear in production databases. Apache
Druid (real-time analytics) uses segment-based data
structures for range time queries. ClickHouse uses
merge-tree structures similar in spirit to segment trees
for time-range aggregations. The "segment" in Druid's
name literally refers to time-range segments. What looks
like a competitive programming tool is the architectural
backbone of modern OLAP systems.

---

### Mastery Checklist

- [ ] Can build segment tree for sum and min from scratch
- [ ] Implements correct out-of-range and fully-covered
      base cases in query
- [ ] Knows when to use Fenwick Tree vs Segment Tree

---

### Interview Deep-Dive

**Q1 (Hard):** Given a stream of stock prices, answer
queries: "what is the minimum price between index i
and j?" with O(log n) per update and O(log n) per query.

> This is a classic range-minimum query (RMQ) problem.
> Build a segment tree where each node stores the minimum
> of its range, not the sum. Build: O(n). Query: traverse
> the tree decomposing [i,j] into O(log n) covered nodes,
> return their minimum. Update: change leaf to new price,
> walk up recomputing min at each internal node: O(log n).
> Alternatives: Sparse Table gives O(1) query but O(n log n)
> build and O(n log n) space - only works for static data.
> For streaming updates, Segment Tree is the right choice.
