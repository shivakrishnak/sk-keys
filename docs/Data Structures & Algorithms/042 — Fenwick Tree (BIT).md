---
layout: default
title: "Fenwick Tree (BIT)"
parent: "Data Structures & Algorithms"
nav_order: 42
permalink: /dsa/fenwick-tree-bit/
number: "0042"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Array, Bit Manipulation
used_by: Inversion Count, Competitive Programming
related: Segment Tree, Prefix Sum Array
tags:
  - datastructure
  - advanced
  - algorithm
  - deep-dive
---

# 042 — Fenwick Tree (BIT)

⚡ TL;DR — A Fenwick Tree (Binary Indexed Tree) answers prefix-sum queries and point updates in O(log N) using a single array and bit manipulation, with a fraction of the code of a segment tree.

| #042 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Array, Bit Manipulation | |
| **Used by:** | Inversion Count, Competitive Programming | |
| **Related:** | Segment Tree, Prefix Sum Array | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You count cumulative votes in an election as they come in. After each batch, you need: (1) the total votes for candidate A from district 1 to district K (a prefix sum), and (2) to add a new batch to district J (a point update). A prefix-sum array answers queries in O(1) but requires O(N) to update (recompute all sums at positions ≥ J). A plain array updates in O(1) but queries in O(N). With 1 million districts and 1 million updates, both approaches are too slow.

**THE BREAKING POINT:**
There is a fundamental tension: O(1) prefix query requires precomputed sums, but updates invalidate all downstream sums (O(N) to fix). Any structure that wants O(log N) for both must find a way to partially precompute sums at multiple granularities.

**THE INVENTION MOMENT:**
Store each position's contribution at multiple granularities determined by its lowest-set bit. Position 6 (binary 110) is responsible for 2 elements; position 8 (binary 1000) for 8 elements. A clever bit trick (`i += i & (-i)` and `i -= i & (-i)`) navigates exactly the right nodes in O(log N). This is exactly why the Fenwick Tree was created.

---

### 📘 Textbook Definition

A **Fenwick Tree** (also called a **Binary Indexed Tree**, BIT) is an array-based data structure that supports two operations on an array in O(log N): `update(i, delta)` — add delta to element i, and `prefixSum(i)` — return the sum of elements 1 through i. The key insight is that each index `i` stores the sum of `(i & -i)` elements ending at position i; the bit manipulation `i += i & (-i)` and `i -= i & (-i)` navigate parent/child relationships without an explicit tree structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An array that answers "sum from 1 to i" in O(log N) using a bit trick to skip just the right precomputed sums.

**One analogy:**
> Imagine counting money by combining bills of different denominations: a $100, a $20, and a $5 make $125. The Fenwick tree does this for array sums: each cell stores the total for a precise "denomination" of consecutive elements, and you collect just the right denominations to answer any prefix query.

**One insight:**
The number of steps in a Fenwick tree query is exactly the number of set bits in i's binary representation, never more than log₂(N). The bit operations `i & (-i)` (isolates the lowest set bit) and their inverse drive all navigation — there is no explicit tree structure, only array indices.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. `tree[i]` stores the sum of elements from `i - (i & -i) + 1` to `i`.
2. `i & -i` extracts the lowest set bit of i: for i=6 (110), `6 & -6 = 2` → stores 2 elements.
3. Navigation uses only bit manipulation — no pointers or explicit parent/child arrays.

**DERIVED DESIGN:**
**prefixSum(i)**: sum `tree[i]`, then jump to `i -= i & (-i)`, repeat until i=0.
```
prefixSum(7) = tree[7] + tree[6] + tree[4]
  7 = 111: tree[7] stores 1 element (index 7)
  6 = 110: tree[6] stores 2 elements (5,6)
  4 = 100: tree[4] stores 4 elements (1,2,3,4)
  Total: elements 1..7 in 3 steps
```

**update(i, delta)**: add delta to `tree[i]`, jump to `i += i & (-i)`, repeat until i > N.
```
update(5, +1):
  5 = 101: update tree[5]
  6 = 110: update tree[6]
  8 = 1000: update tree[8]
  ...
```

**Query [L, R]**: `prefixSum(R) - prefixSum(L-1)` — two prefix queries.

**THE TRADE-OFFS:**
**Gain:** O(log N) query and update, O(N) space, smallest possible code for this complexity.
**Cost:** Only works for operations with an inverse (subtraction for sum; doesn't generalise to min/max unlike segment tree). Conceptually harder to understand than segment tree.

---

### 🧪 Thought Experiment

**SETUP:**
Array [1, 2, 3, 4, 5]. Query prefix sum to index 5. Update index 3 by +10.

**WHAT HAPPENS WITHOUT FENWICK (prefix array):**
Prefix: [1, 3, 6, 10, 15]. Query prefix[5] = 15. O(1).
Update index 3: must recompute prefix[3..5]: O(N) = 3 operations.

**WHAT HAPPENS WITH FENWICK:**
Array maps to tree[1..5] with responsibility ranges by lowest set bit.
Query prefix[5]: `tree[5] + tree[4]` = (5) + (1+2+3+4) = 5 + 10 = 15. O(log 5) = 2 steps.
Update index 3 by +10: update tree[3], tree[4] — 2 nodes. O(log 5) = 2 steps.

**THE INSIGHT:**
The Fenwick tree achieves something that seems impossible: O(log N) for both prefix queries and point updates, without a segment tree's implementation complexity. The trick is that each position "owns" a number of elements equal to its lowest set bit — a property that lets bit arithmetic replace pointer traversal.

---

### 🧠 Mental Model / Analogy

> A Fenwick tree is like a nested Russian doll of partial sums. The outermost doll contains sums of 8 elements, inside it a doll for 4 elements, inside one for 2, inside one for 1. To answer a prefix query, you open exactly the right dolls and add their contents.

- "Outermost doll (size 8)" → tree[8] stores elements 1–8
- "4-element doll" → tree[4] stores elements 1–4
- "Specific nesting determined by bit" → i & (-i) picks the right doll

Where this analogy breaks down: Dolls nest strictly inside each other; Fenwick tree ranges can overlap depending on the query position. The bit arithmetic correctly selects non-overlapping partial sums automatically.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A clever array where each slot stores the sum of some group of nearby elements, and two bit tricks let you answer "sum from 1 to K" or update any element in about 20 steps regardless of array size.

**Level 2 — How to use it (junior developer):**
1-indexed. `update(i, delta)`: add delta to position i, then propagate up using `i += i&(-i)` until `i > N`. `prefixQuery(i)`: sum `tree[i]` values, drop lowest set bit `i -= i&(-i)`, repeat until `i==0`. Range query `[L,R]`: `prefixQuery(R) - prefixQuery(L-1)`.

**Level 3 — How it works (mid-level engineer):**
`i & (-i)` exploits two's complement: `-i` flips all bits and adds 1, so `i & (-i)` isolates the rightmost 1 bit. For i=12 (1100): `12 & -12 = 4`. tree[12] stores sum of 4 elements: 9..12. tree[8] stores 1..8. tree[4] stores 1..4. Each node covers a power-of-2 range determined by its index's trailing zeros.

**Level 4 — Why it was designed this way (senior/staff):**
Peter Fenwick's 1994 paper introduced this to solve inverse probability calculations in data compression. The cleverness is that the bit manipulation implicitly encodes the tree structure — no pointers, no recursion, just two arithmetic operations per step. Range updates are possible via a "difference BIT": store the difference array, and query a prefix-sum of differences to recover the original value. This gives O(log N) for range updates + point queries — the complement of the standard BIT. Combining two BITs enables O(log N) range updates + range queries (but this equals a segment tree in complexity and is usually not worth it over a segment tree).

---

### ⚙️ How It Works (Mechanism)

**Common BIT responsibility map (N=8):**
```
Index:    1  2  3  4  5  6  7  8
Lowest SB:1  2  1  4  1  2  1  8
Covers: [1][12][3][14][5][56][7][18]
```

**prefixSum(7):**
```
i=7 (111): sum tree[7], i -= 1 → i=6
i=6 (110): sum tree[6], i -= 2 → i=4
i=4 (100): sum tree[4], i -= 4 → i=0
Done: tree[7] + tree[6] + tree[4]
```

**update(3, +5):**
```
i=3 (011): tree[3] += 5, i += 1 → i=4
i=4 (100): tree[4] += 5, i += 4 → i=8
i=8 (1000):tree[8] += 5, i += 8 → i=16 > N
Done
```

**Full implementation:**
```java
class BIT {
    int[] tree;
    int n;

    BIT(int n) { this.n = n; tree = new int[n + 1]; }

    void update(int i, int delta) {
        for (; i <= n; i += i & (-i))
            tree[i] += delta;
    }

    int prefixSum(int i) {
        int sum = 0;
        for (; i > 0; i -= i & (-i))
            sum += tree[i];
        return sum;
    }

    // Range sum [l, r]
    int rangeSum(int l, int r) {
        return prefixSum(r) - prefixSum(l - 1);
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Array element updated
→ update(i, delta): propagate upward via i += i&(-i)
→ [FENWICK TREE ← YOU ARE HERE]
→ prefixSum(k): accumulate via i -= i&(-i)
→ Range query: two prefix queries, subtract
```

**FAILURE PATH:**
```
Use 0-based indexing with a 1-indexed BIT
→ update(0, delta): Loop i=0 → 0 forever (i&-i=0)
→ Infinite loop or silent no-op
→ Fix: always use 1-based indexing with BIT
```

**WHAT CHANGES AT SCALE:**
At N=10^8, the BIT uses 400 MB for int array — feasible but pushed. For 64-bit sums (long), 800 MB. At larger scales, BITs are distributed across shards, each handling a range, with a meta-BIT tracking shard sums. Modern competitive programming uses BITs up to N=10^7 comfortably; beyond that, offline algorithms (sorting queries) often outperform.

---

### 💻 Code Example

**Example 1 — Count inversions in array:**
```java
// Inversion: pair (i,j) where i<j but arr[i]>arr[j]
// BIT approach: count smaller elements to the right
int countInversions(int[] arr) {
    int n = arr.length;
    int max = Arrays.stream(arr).max().getAsInt();
    BIT bit = new BIT(max);
    int inv = 0;
    // Process right to left; count elements < current
    for (int i = n - 1; i >= 0; i--) {
        inv += bit.prefixSum(arr[i] - 1);
        bit.update(arr[i], 1);
    }
    return inv;
}
```

**Example 2 — 2D BIT (range sum in matrix):**
```java
// BIT can extend to 2D: for (i, j) update:
void update2D(int[][] tree, int x, int y, int v, int N) {
    for (int i = x; i <= N; i += i & (-i))
        for (int j = y; j <= N; j += j & (-j))
            tree[i][j] += v;
}
int query2D(int[][] tree, int x, int y) {
    int sum = 0;
    for (int i = x; i > 0; i -= i & (-i))
        for (int j = y; j > 0; j -= j & (-j))
            sum += tree[i][j];
    return sum;
}
```

---

### ⚖️ Comparison Table

| Structure | Prefix Query | Point Update | Range Update | Space | Best For |
|---|---|---|---|---|---|
| **Fenwick Tree** | O(log N) | O(log N) | O(log N)* | O(N) | Prefix sums — simplest code |
| Segment Tree | O(log N) | O(log N) | O(log N) | O(N) | General queries (min/max/etc.) |
| Prefix Sum Array | O(1) | O(N) | O(N) | O(N) | Static arrays |

*Requires two BITs or a difference-BIT trick for range updates.

How to choose: Use Fenwick tree when your operation is sum (or has an inverse); it's simpler to code. Use segment tree for min/max or non-invertible operations, or when range updates are needed with lazy propagation.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| BIT can answer range min/max queries | BIT only works for operations with an inverse (subtraction); min/max have no inverse — use segment tree |
| BIT is faster than segment tree in practice | Both are O(log N); BIT has a smaller constant factor and better cache behaviour due to smaller code size |
| BIT must be 1-indexed | It must; index 0 creates an infinite loop because `0 & -0 = 0` |
| BIT with range updates = lazy segment tree | Range-update BIT uses two BITs (difference method) and only works for the specific patterns it supports |

---

### 🚨 Failure Modes & Diagnosis

**1. Infinite loop from zero-index usage**

**Symptom:** Program hangs indefinitely on `update(0, delta)` or `prefixSum(0)`.

**Root Cause:** BIT is 1-based. At i=0, `i & (-i) = 0` → loop never terminates.

**Diagnostic:**
```bash
jstack <pid> | grep "BIT\|update\|prefixSum"
# Thread stuck in BIT loop
```

**Fix:** Always add 1 to 0-based indices before calling BIT. If your array is 0-indexed, wrap the BIT calls: `bit.update(i + 1, delta)`.

**Prevention:** Document clearly: "BIT is 1-indexed; all inputs must be ≥ 1."

---

**2. Wrong range query from off-by-one in L boundary**

**Symptom:** Range query `[L, R]` returns sum including index L-1.

**Root Cause:** `rangeSum(L, R)` uses `prefixSum(L)` instead of `prefixSum(L-1)`.

**Diagnostic:**
```java
// Test: array [1,2,3,4,5], query [2,4] should be 2+3+4=9
assert bit.rangeSum(2, 4) == 9; // fails if using prefixSum(L) instead of prefixSum(L-1)
```

**Fix:** `rangeSum(l, r) = prefixSum(r) - prefixSum(l-1)` — always subtract `l-1`, not `l`.

**Prevention:** Write a unit test for `rangeSum` that includes the boundary elements.

---

**3. Overflow for large sum values**

**Symptom:** prefixSum returns negative number or incorrect large value.

**Root Cause:** `tree[]` is `int` but cumulative sum exceeds `Integer.MAX_VALUE` (≈ 2 billion).

**Diagnostic:**
```java
// Check if max possible sum exceeds Integer.MAX_VALUE
long maxPossibleSum = (long)N * maxElementValue;
if (maxPossibleSum > Integer.MAX_VALUE)
    System.out.println("Overflow risk!");
```

**Fix:** Use `long[] tree` instead of `int[] tree`.

**Prevention:** Default to `long` for BIT arrays in production; the memory difference is minimal.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — BIT is a flat array; understanding index arithmetic is required.
- `Bit Manipulation` — `i & (-i)` (isolate lowest set bit) is the core operation.

**Builds On This (learn these next):**
- `Inversion Count` — classic BIT application; count pairs (i,j) where i<j and arr[i]>arr[j] in O(N log N).

**Alternatives / Comparisons:**
- `Segment Tree` — more complex code but handles min/max and lazy range updates.
- `Prefix Sum Array` — O(1) query but O(N) update; use when array is static.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Array where each index stores partial sum │
│              │ of (i & -i) elements; O(log N) ops       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Prefix sums need O(N) rebuild after any   │
│ SOLVES       │ point update                              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ i & (-i) isolates the lowest set bit —    │
│              │ this one operation encodes the whole tree │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Prefix sum queries + point updates on a   │
│              │ mutable array (simplest O(log N) code)    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Non-invertible operations (min, max, GCD) │
│              │ needed — use Segment Tree instead         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplest O(log N) code vs limited to      │
│              │ invertible operations only               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two bit tricks to sum anything in        │
│              │  log N steps — no tree needed"            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Segment Tree → Inversion Count → 2D BIT   │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A Fenwick tree answers "sum of elements from index 1 to k" in O(log N). A segment tree also answers this in O(log N). Both have the same asymptotic complexity. In a timed programming contest with N=10^6 and 10^6 queries and updates, empirically the Fenwick tree solutions often run 2–3× faster. Without implementing both, explain what hardware-level factors cause this speed difference despite identical big-O complexity.

**Q2.** The standard Fenwick tree handles point updates and prefix queries. To handle range updates and point queries, you use a "difference BIT" (BIT on difference array). To handle range updates AND range queries, you need two BITs simultaneously. Explain the mathematical identity that makes the two-BIT approach work for range update + range query, and describe a scenario where it would be simpler to use a segment tree with lazy propagation instead, and at what point the BIT's code simplicity advantage vanishes.

