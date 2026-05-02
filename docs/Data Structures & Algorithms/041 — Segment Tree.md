---
layout: default
title: "Segment Tree"
parent: "Data Structures & Algorithms"
nav_order: 41
permalink: /dsa/segment-tree/
number: "0041"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Array, Heap (Min/Max), Divide and Conquer
used_by: Range Queries, Competitive Programming
related: Fenwick Tree (BIT), Sparse Table, Sqrt Decomposition
tags:
  - datastructure
  - advanced
  - algorithm
  - deep-dive
---

# 041 — Segment Tree

⚡ TL;DR — A Segment Tree answers range queries (sum, min, max) and range updates on an array in O(log N) per operation, replacing O(N) brute force.

| #041 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Array, Heap (Min/Max), Divide and Conquer | |
| **Used by:** | Range Queries, Competitive Programming | |
| **Related:** | Fenwick Tree (BIT), Sparse Table, Sqrt Decomposition | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You manage a stock exchange. For any time window [L, R], traders ask the minimum price during that period. With 1 million price points, a naive scan of the window is O(R-L+1) per query — up to O(N). With 10,000 queries per second each spanning 500,000 points, that is 5 billion operations per second. Meanwhile prices update in real time. No array-based approach handles both dynamic updates and fast range queries.

THE BREAKING POINT:
Brute-force range queries are O(N). Precomputing all answers is O(N²) space. Neither scales. The fundamental tension: queries demand pre-aggregated summaries, but updates invalidate those summaries.

THE INVENTION MOMENT:
Divide the array recursively in half. Each tree node stores the answer for its range. A query combines at most 2 log N nodes. An update recomputes at most log N nodes. This divide-and-conquer decomposition reduces both query and update to O(log N). This is exactly why the Segment Tree was created.

---

### 📘 Textbook Definition

A **Segment Tree** is a binary tree where each node stores a precomputed aggregate (sum, min, max, GCD, etc.) for a contiguous subarray of an input array. The root covers the full array; each internal node covers the union of its children's ranges; leaves cover single elements. Construction is O(N). Point updates and arbitrary range queries are O(log N). Range updates with **lazy propagation** are also O(log N) per operation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A binary tree where each node summarises half the array, so any range query needs at most 2 log N nodes.

**One analogy:**
> Think of a sports tournament bracket. Rather than watching every match to find the overall champion, each match records the winner. To find the best player in rounds 3–7, you combine a few bracket results — not re-watch every match.

**One insight:**
The key insight is that every range [L, R] can be decomposed into at most 2 log N pre-computed tree nodes. This decomposition is what makes O(log N) range queries possible without precomputing answers for every possible range (which would be O(N²)).

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Each node stores the aggregate of exactly the elements in its range — this must always be correct.
2. A leaf node covers range [i, i] with the raw element value.
3. An internal node covering [l, r] stores `f(left_child_value, right_child_value)` where `f` is the query function (sum, min, max).

DERIVED DESIGN:
**Array storage** (similar to heaps): store in a 1-indexed array of size 4N.
- Node 1: root covering [0, N-1].
- Node i: left child = 2i, right child = 2i+1.
- Node i covers [l, r]: left child covers [l, mid], right child covers [mid+1, r].

**Query [L, R]**: if node's range is fully inside [L, R], return its stored value — don't recurse. If fully outside, return identity (0 for sum, ∞ for min). If partially overlapping, recurse both children and combine. At most 4 nodes per level are partially overlapping → O(4 log N) = O(log N).

**Update index i**: update leaf, then recompute all ancestors. Path from leaf to root has log N nodes → O(log N).

**Lazy propagation**: defers range updates. Instead of updating all N leaves, place a "pending update" marker on high-level nodes. When a node is visited by a future query or update, push the lazy value down to children first.

THE TRADE-OFFS:
Gain: O(log N) both query and update; handles sum, min, max, GCD — any associative operation.
Cost: O(4N) memory, complex implementation, constant factor larger than Fenwick tree for the sum-only case.

---

### 🧪 Thought Experiment

SETUP:
Range sum query on array `[2, 1, 5, 3, 4]`. Query sum of [1, 3] (indices 1 to 3). Update index 2 to value 7.

WHAT HAPPENS WITHOUT SEGMENT TREE:
Query [1,3]: scan indices 1,2,3 → sum = 1+5+3 = 9. O(N) scan.
Update: just assign `arr[2] = 7`. O(1).
For 10,000 queries × 10,000 queries on N=1M: 10 billion ops.

WHAT HAPPENS WITH SEGMENT TREE:
Query [1,3]: tree decomposes into at most 3 nodes at depth 2-3. Returns 9 in O(log 5) = O(3) ops.
Update index 2: update leaf, recompute 3 ancestors. O(log 5) = O(3) ops.
10,000 queries × 20 ops each = 200,000 ops — 50,000× faster.

THE INSIGHT:
The "decompose query into O(log N) precomputed nodes" trick is the central idea of segment trees, Fenwick trees, and sparse tables. All three trade storage for query speed using the divide-and-conquer principle applied to ranges.

---

### 🧠 Mental Model / Analogy

> A Segment Tree is like a company org chart where every manager summarises their entire team's performance. Asking "best performer in division A to B" means consulting a few managers, not every employee.

"Employee" → leaf node (single array element)
"Manager summary" → internal node aggregate
"Division query" → combine a few manager summaries
"Employee performance change" → update leaf + all managers above

Where this analogy breaks down: In a real org chart, managers are domain-specific; in a segment tree, every internal node is generic — it stores only the computed aggregate, not the actual subordinate data.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A tree where every node summarises a slice of your array. You can ask "what's the sum/min/max in range [L,R]?" and get the answer fast by combining a few tree nodes.

**Level 2 — How to use it (junior developer):**
For range-sum queries with point updates: build segment tree of size 4N. Query and update both traverse from root to leaves guided by range overlap. Always compute mid as `l + (r - l) / 2` to avoid overflow. Identify your aggregate function — must be associative: `f(a, b) = f(b, a)` isn't required; `f(f(a,b), c) = f(a, f(b,c))` is.

**Level 3 — How it works (mid-level engineer):**
`build(node, l, r)`: if leaf, `tree[node] = arr[l]`; else recurse children, `tree[node] = tree[2*node] + tree[2*node+1]`. `query(node, l, r, L, R)`: three cases — outside: return 0; inside: return `tree[node]`; partial: combine `query(left, l, mid, L, R)` and `query(right, mid+1, r, L, R)`. Lazy propagation adds `lazy[node]` array: when a range update hits a fully-covered node, store update in `lazy[node]` and return; when recursing later, push `lazy[node]` to children first.

**Level 4 — Why it was designed this way (senior/staff):**
The 4N array size (instead of the tight 2N) is a safety buffer because the tree is not always a perfect binary tree — leaves at different depths may require different node indices, and 4N bounds the maximum index. Persistent segment trees (keeping old versions on update by sharing unchanged subtrees) enable O(log N) historical queries — used in online judge problems and database MVCC implementations. Merge sort trees (Segment Tree where each node stores a sorted array of its range) enable O(log² N) "count of elements in range [L,R] with value in [X,Y]" queries.

---

### ⚙️ How It Works (Mechanism)

**Segment tree for array [2, 1, 5, 3, 4] — range sum:**
```
            [0,4]=15
           /         \
      [0,2]=8        [3,4]=7
      /     \        /     \
  [0,1]=3  [2,2]=5 [3,3]=3 [4,4]=4
  /    \
[0,0]=2 [1,1]=1
```

**Build implementation:**
```java
int[] tree = new int[4 * N];

void build(int[] arr, int node, int l, int r) {
    if (l == r) { tree[node] = arr[l]; return; }
    int mid = l + (r - l) / 2;
    build(arr, 2*node, l, mid);
    build(arr, 2*node+1, mid+1, r);
    tree[node] = tree[2*node] + tree[2*node+1];
}

int query(int node, int l, int r, int L, int R) {
    if (R < l || r < L) return 0;      // outside
    if (L <= l && r <= R) return tree[node]; // fully inside
    int mid = l + (r - l) / 2;
    return query(2*node, l, mid, L, R)
         + query(2*node+1, mid+1, r, L, R);
}

void update(int node, int l, int r, int idx, int val) {
    if (l == r) { tree[node] = val; return; }
    int mid = l + (r - l) / 2;
    if (idx <= mid) update(2*node, l, mid, idx, val);
    else            update(2*node+1, mid+1, r, idx, val);
    tree[node] = tree[2*node] + tree[2*node+1];
}
```

┌──────────────────────────────────────────────┐
│  query([1,3]) traversal in tree              │
│                                              │
│  node [0,4]: partial → recurse              │
│   node [0,2]: partial → recurse             │
│    node [0,1]: partial → recurse            │
│     node [0,0]: outside [1,3] → return 0   │
│     node [1,1]: inside → return 1          │
│    node [2,2]: inside [1,3] → return 5     │
│   node [3,4]: partial → recurse             │
│    node [3,3]: inside → return 3           │
│    node [4,4]: outside → return 0          │
│  Result: 0+1+5+3+0 = 9                      │
└──────────────────────────────────────────────┘

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Input array arrives
→ build() constructs tree in O(N)
→ query(L, R): O(log N) range aggregate
→ [SEGMENT TREE ← YOU ARE HERE]
→ update(idx, val): O(log N) point update
→ Answers returned in real time
```

FAILURE PATH:
```
Incorrect aggregate function (non-associative)
→ query() combines partial results incorrectly
→ Produces wrong answers with no runtime error
→ Fix: verify f(f(a,b),c) == f(a,f(b,c)) before use
```

WHAT CHANGES AT SCALE:
At N=10^8, a segment tree uses 4×10^8 integers ≈ 1.6 GB. Memory becomes the bottleneck. Use a dynamic segment tree (allocate nodes on-demand, only for visited ranges) reducing memory to O(Q log N) where Q is the number of queries/updates. For truly large-scale (distributed), segment trees are not used directly; range aggregation is computed via columnar databases or pre-aggregated summaries.

---

### 💻 Code Example

**Example 1 — Range minimum query (stock prices):**
```java
class SegTree {
    int[] tree;
    int n;
    SegTree(int[] arr) {
        n = arr.length;
        tree = new int[4 * n];
        build(arr, 1, 0, n - 1);
    }
    void build(int[] a, int nd, int l, int r) {
        if (l == r) { tree[nd] = a[l]; return; }
        int m = l + (r - l) / 2;
        build(a, 2*nd, l, m);
        build(a, 2*nd+1, m+1, r);
        tree[nd] = Math.min(tree[2*nd], tree[2*nd+1]);
    }
    int query(int nd, int l, int r, int L, int R) {
        if (R < l || r < L) return Integer.MAX_VALUE;
        if (L <= l && r <= R) return tree[nd];
        int m = l + (r - l) / 2;
        return Math.min(query(2*nd, l, m, L, R),
                        query(2*nd+1, m+1, r, L, R));
    }
    int rangeMin(int L, int R) {
        return query(1, 0, n-1, L, R);
    }
}
```

---

### ⚖️ Comparison Table

| Structure | Build | Query | Update | Space | Best For |
|---|---|---|---|---|---|
| **Segment Tree** | O(N) | O(log N) | O(log N) | O(N) | General range ops + updates |
| Fenwick Tree | O(N) | O(log N) | O(log N) | O(N) | Prefix sums (simpler code) |
| Sparse Table | O(N log N) | O(1) | O(N) | O(N log N) | Static arrays, range min/max |
| Sqrt Decomposition | O(N) | O(√N) | O(1) | O(N) | Simple to implement, moderate N |
| Brute Force | O(1) | O(N) | O(1) | O(N) | N < 100 or query count < 10 |

How to choose: Use Segment Tree when you need both efficient queries AND updates. Use Fenwick Tree for prefix sums (simpler). Use Sparse Table for static data with range min/max (O(1) queries). Use brute force when N < 1,000 or query count is tiny.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Segment tree requires N to be a power of 2 | N can be any size; use 4N as tree size; the recursive build handles arbitrary N |
| Segment tree is only for sum queries | Any associative operation works: min, max, GCD, XOR, matrix multiplication, etc. |
| Lazy propagation makes all range updates O(1) | Lazy propagation makes range updates O(log N), not O(1); it avoids O(N) leaf updates but still visits O(log N) nodes |
| A segment tree and a Fenwick tree are equivalent | Segment trees are more general (any associative f, range updates, custom merge); Fenwick trees are simpler but limited to prefix queries with inverses |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong answers from incorrect identity element**

Symptom: Range queries return wrong results, especially on edge ranges including index 0 or the last element.

Root Cause: The "outside range" case returns the wrong identity value. For sum: 0. For min: Integer.MAX_VALUE. For max: Integer.MIN_VALUE. Using 0 as identity for min queries returns 0 for non-overlapping ranges, contaminating the min.

Diagnostic:
```java
// Test with known arrays:
// [5, 3, 7] : rangeMin(0, 2) should be 3, not 0
assert tree.rangeMin(0, 2) == 3;
```

Fix: Use the correct identity for your operation. Always document which operation and identity your tree uses.

Prevention: Unit test range queries including boundary cases: [0,0], [N-1,N-1], [0,N-1].

---

**2. ArrayIndexOutOfBoundsException from undersized tree array**

Symptom: AIOOBE when building or querying large trees.

Root Cause: Allocated `tree = new int[2*N]` instead of `4*N`. The segment tree's node indices can exceed 2N for non-power-of-2 array sizes.

Diagnostic:
```bash
# Stack trace will point to line where tree[node] is accessed
# Verify: System.out.println(tree.length); should be >= 4*N
```

Fix: Always use `4*N` as the segment tree array size.

Prevention: Comment the allocation line: `// 4*N is safe upper bound for any N`.

---

**3. TLE from forgetting to push lazy values down before querying**

Symptom: Range queries return stale values after range updates; results appear to be pre-update values.

Root Cause: Lazy propagation stores pending updates in `lazy[node]`. If a query hits a node without pushing lazy values to children first, children have stale data.

Diagnostic:
```java
// Apply range update, then query same range:
// If answers don't match, lazy push is missing
tree.rangeUpdate(2, 5, +1);
assert tree.rangeQuery(2, 5) == expectedAfterUpdate;
```

Fix: At the start of every query and update function: if `lazy[node] != 0`, push lazy to children before recursing.

Prevention: Add `pushDown(node)` as the first operation in both `query()` and `update()` methods.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — segment tree is array-encoded binary tree.
- `Divide and Conquer` — the recursive halving of the range is the core design principle.
- `Heap (Min/Max)` — same array-index arithmetic for tree navigation.

**Builds On This (learn these next):**
- `Fenwick Tree (BIT)` — simpler structure for the specific case of prefix sums.

**Alternatives / Comparisons:**
- `Fenwick Tree` — simpler, O(log N) prefix queries, but limited to operations with inverses.
- `Sparse Table` — O(1) queries but O(N) updates; for static arrays only.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Binary tree where each node stores a range│
│              │ aggregate; O(log N) query and update      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Range queries on mutable arrays are O(N)  │
│ SOLVES       │ brute force; prefix sums break on updates │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every range decomposes into O(log N)      │
│              │ pre-computed tree nodes — not O(N) leaves │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Range sum/min/max with point or range     │
│              │ updates on a mutable array                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Array is static and only min/max needed   │
│              │ (use Sparse Table for O(1) queries)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(log N) query+update vs O(4N) memory     │
│              │ and complex implementation                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A tournament bracket that answers        │
│              │  range questions without re-playing       │
│              │  every match"                             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Fenwick Tree → Sparse Table → Lazy Prop   │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A segment tree with lazy propagation supports range updates in O(log N). An alternative is to use a Fenwick tree of differences (BIT on a difference array) which also handles range updates + prefix queries in O(log N). What class of queries can a lazy segment tree answer that a Fenwick tree fundamentally cannot, and what property of the query function determines this limitation?

**Q2.** A persistent segment tree creates a new "version" on each update by creating O(log N) new nodes and sharing the rest with the previous version. This enables O(log N) queries "at any historical version" with O(N + Q log N) total space. Explain why sharing unchanged subtrees is correct (what invariant of segment trees makes immutable sharing safe), and give one real-world use case where querying historical versions is necessary for correctness, not just convenience.

