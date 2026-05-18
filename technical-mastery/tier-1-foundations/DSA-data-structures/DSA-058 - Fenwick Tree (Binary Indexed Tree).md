---
id: DSA-058
title: Fenwick Tree (Binary Indexed Tree)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-057
used_by: DSA-077
related: DSA-057, DSA-028
tags:
  - data-structures
  - fenwick-tree
  - binary-indexed-tree
  - bit
  - range-sum
  - o-log-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/dsa/fenwick-tree/
---

## TL;DR

A Fenwick Tree (BIT) computes prefix sums and point updates
in O(log n) time with O(n) space and minimal code - a
simpler, faster-in-practice alternative to Segment Trees
for sum/frequency queries.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-058 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, BIT, prefix-sum, O(log n) |
| **Prerequisites** | DSA-057 |

---

### The Problem This Solves

Prefix sum arrays answer "sum of arr[0..i]?" in O(1) but
require O(n) to update any element. Fenwick Trees answer
the same query in O(log n) and update in O(log n), using
a clever bitwise trick to navigate a conceptual tree stored
in a flat array - no tree allocation, no recursion.

---

### Textbook Definition

A Fenwick Tree (Binary Indexed Tree, BIT) is a flat array
of size n+1 where each index i stores the sum of a specific
range of the original array, determined by the lowest set
bit of i in binary. Index i covers the range of length
`lowbit(i) = i & (-i)`. Prefix sum and update both walk
indices by adding or subtracting the lowest set bit,
achieving O(log n) with simple bit arithmetic.

---

### Understand It in 30 Seconds

```
The magic of i & (-i): the lowest set bit

i=6  = 110  →  6 & (-6) = 110 & 010 = 010 = 2
BIT[6] covers arr[5] and arr[6] (2 elements)

i=4  = 100  →  4 & (-4) = 100 & 100 = 100 = 4
BIT[4] covers arr[1..4] (4 elements)

Update index i: go UP by adding lowbit:
  6 → 6+2=8 → 8+8=16 → done when >n

Prefix sum to index i: go DOWN by subtracting lowbit:
  6 → 6-2=4 → 4-4=0 → stop
```

---

### How It Works

**Complete Fenwick Tree implementation:**

```java
class FenwickTree {
    private final int[] bit;
    private final int n;

    FenwickTree(int n) {
        this.n = n;
        this.bit = new int[n + 1]; // 1-indexed
    }

    // Build from array: O(n) using O(n log n) approach:
    FenwickTree(int[] arr) {
        n = arr.length;
        bit = new int[n + 1];
        for (int i = 0; i < n; i++) {
            update(i + 1, arr[i]); // 1-indexed
        }
    }

    // Add val to index i (1-indexed): O(log n)
    void update(int i, int val) {
        for (; i <= n; i += i & (-i)) {
            bit[i] += val;
        }
    }

    // Prefix sum [1..i] (1-indexed): O(log n)
    int prefixSum(int i) {
        int sum = 0;
        for (; i > 0; i -= i & (-i)) {
            sum += bit[i];
        }
        return sum;
    }

    // Range sum [l..r] (1-indexed): O(log n)
    int rangeSum(int l, int r) {
        return prefixSum(r) - prefixSum(l - 1);
    }
}

// Usage:
int[] arr = {1, 3, 5, 7, 9, 11};
FenwickTree ft = new FenwickTree(arr);
// sum[0..3] = 1+3+5+7 = 16
System.out.println(ft.rangeSum(1, 4)); // 16
ft.update(3, 2); // arr[2] += 2, so arr[2] = 7 now
System.out.println(ft.rangeSum(1, 4)); // 18
```

---

### Comparison Table

| Property | Prefix Sum | Fenwick Tree | Segment Tree |
|---------|-----------|-------------|-------------|
| Build | O(n) | O(n log n) | O(n) |
| Update | O(n) | O(log n) | O(log n) |
| Prefix sum | O(1) | O(log n) | O(log n) |
| Range sum | O(1) | O(log n) | O(log n) |
| Code complexity | Trivial | Simple | Moderate |
| Space | O(n) | O(n) | O(4n) |
| Supports min/max | No | No | Yes |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Fenwick Tree is just a prefix sum array" | It supports O(log n) updates, which a plain prefix sum array cannot |
| "Segment Tree is always better" | For sum/frequency queries, Fenwick Tree is simpler code, smaller constant factor, and sufficient; Segment Tree is needed for min/max or range updates |

---

### Failure Modes & Diagnosis

**Failure: Wrong answers from off-by-one errors**
- Cause: Fenwick Trees are 1-indexed; accessing bit[0]
  is undefined behavior (i & (-i) = 0 causes infinite loop)
- Fix: Always shift array input by +1 when building from
  0-indexed array; document the indexing convention

---

### Quick Reference Card

| Property | Fenwick Tree |
|---------|-------------|
| Update (point) | O(log n) |
| Prefix sum | O(log n) |
| Range sum | O(log n) |
| Space | O(n) |
| Indexing | 1-based |
| Range update + range query | Requires 2 BITs |
| Can do min/max | No (sum/freq only) |

---

### The Surprising Truth

Fenwick Trees are used in competitive programming order-
statistics problems: "how many elements less than x?"
Build a BIT indexed by value (frequency array), where
update(x, 1) means "x was inserted" and prefixSum(x)
answers "how many elements ≤ x?". This is the basis of
BIT-based merge sort (counting inversions in O(n log n))
and several LeetCode hard problems. The data structure
was invented by Peter Fenwick in 1994 to compute word
frequency statistics in documents.

---

### Mastery Checklist

- [ ] Can implement Fenwick Tree from memory (15 lines)
- [ ] Understands the `i & (-i)` trick and why it works
- [ ] Knows when to use BIT vs Segment Tree

---

### Interview Deep-Dive

**Q1 (Hard):** Count the number of inversions in an
array: pairs (i, j) where i < j but arr[i] > arr[j].

> An inversion is a pair where the left element is larger
> than the right. Brute force O(n^2).
> Optimal using Fenwick Tree: O(n log n).
> 
> Approach: Process elements left to right. For each
> element arr[i], count how many already-processed
> elements are GREATER than arr[i]. That count =
> number of inversions with arr[i] as the right element.
> 
> Coordinate compress values to range [1..n].
> Build BIT of size n (all zeros).
> For each element x (left to right):
>   inversions += i - prefixSum(x)  // elements so far
>                                    // minus those ≤ x
>   update(x, 1)                    // mark x as seen
> 
> Total: O(n log n) time. O(n) space.
> Example: [3,1,2]: inversions = (3,1), (3,2) = 2.
