---
id: DSA-090
title: Quickselect (k-th Largest Element)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-031, DSA-028
used_by: DSA-077
related: DSA-031, DSA-028
tags:
  - algorithms
  - quickselect
  - k-th-element
  - median
  - o-n-average
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 90
permalink: /technical-mastery/dsa/quickselect/
---

## TL;DR

Quickselect finds the k-th smallest element in O(n) average
time using QuickSort's partition step without fully sorting
the array - the algorithm behind finding medians and
percentiles efficiently.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-090 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, quickselect, k-th element, O(n) |
| **Prerequisites** | DSA-031, DSA-028 |

---

### The Problem This Solves

"Find the median of n elements." Sort and return middle:
O(n log n). We don't need full sorting - just find the
one element at position n/2. Quickselect: O(n) average
by only recursing on the partition that contains k.

---

### Textbook Definition

Quickselect selects the k-th smallest element using
QuickSort's partition. After partitioning around a pivot:
- If pivot is at position k → found
- If k < pivot position → recurse on left subarray only
- If k > pivot position → recurse on right subarray only

Average time: O(n) (expected). Worst case: O(n^2) for
adversarial pivot selection (use randomized pivot to avoid).
Space: O(1) in-place (or O(log n) with recursive stack).

---

### How It Works

**Implementation:**

```java
// Find k-th smallest (0-indexed) in arr[lo..hi]
int quickselect(int[] arr, int lo, int hi, int k) {
    if (lo == hi) return arr[lo]; // base case

    int pivot = partition(arr, lo, hi); // in-place partition

    if (pivot == k) {
        return arr[pivot]; // found exact position
    } else if (k < pivot) {
        return quickselect(arr, lo, pivot - 1, k); // left half only
    } else {
        return quickselect(arr, pivot + 1, hi, k); // right half only
    }
}

// Lomuto partition (simple, O(n))
int partition(int[] arr, int lo, int hi) {
    // Randomize pivot to avoid O(n^2) worst case
    int randIdx = lo + (int)(Math.random() * (hi - lo + 1));
    swap(arr, randIdx, hi);
    int pivot = arr[hi];

    int i = lo - 1;
    for (int j = lo; j < hi; j++) {
        if (arr[j] <= pivot) swap(arr, ++i, j);
    }
    swap(arr, i + 1, hi);
    return i + 1; // pivot's final position
}

// Find k-th LARGEST (0-indexed): use k = n - 1 - k
int kthLargest(int[] arr, int k) {
    return quickselect(arr, 0, arr.length - 1, arr.length - 1 - k);
}
```

**Why O(n) average:**

```
After first partition at position p:
  Case k < p: recurse on left  (size p-lo ≤ n/2 on avg)
  Case k > p: recurse on right (size hi-p ≤ n/2 on avg)

T(n) = T(n/2) + O(n) → O(n) by Master Theorem (Case 3)

Worst case: pivot always min/max element
  T(n) = T(n-1) + O(n) → O(n^2)
  Randomized pivot makes this O(n^2) probability negligible.
```

---

### Comparison Table

| Method | Time | Space | Notes |
|--------|------|-------|-------|
| Sort and index | O(n log n) | O(1) | Simple but overworks |
| Min-heap size k | O(n log k) | O(k) | Good for streaming |
| Quickselect | O(n) avg | O(1) | In-place, modifies array |
| Median-of-medians | O(n) worst | O(n) | Deterministic but slow const |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Quickselect sorts the array" | It partially partitions; elements are not in sorted order except the k-th element is at its correct final position |
| "Median-of-medians is always better" | Median-of-medians guarantees O(n) worst case but has a large constant factor; randomized quickselect is faster in practice |

---

### Failure Modes & Diagnosis

**Failure: Quickselect O(n^2) in production**
- Cause: Non-randomized pivot on adversarially sorted input
- Fix: Always use randomized pivot; test with sorted and
  reverse-sorted arrays

---

### Quick Reference Card

| Property | Quickselect |
|---------|------------|
| Time (average) | O(n) |
| Time (worst case) | O(n^2) without randomization |
| Space | O(1) in-place |
| Modifies array | Yes (in-place partitioning) |
| Java built-in | Not directly; use sort or PriorityQueue |

---

### The Surprising Truth

NumPy's `numpy.partition(arr, k)` uses introselect - a
hybrid of quickselect (fast in practice) and median-of-
medians (O(n) worst case guarantee). The partition step
runs quickselect and switches to median-of-medians if
progress is too slow (similar to introsort for sorting).
This gives O(n) expected AND O(n) worst case with good
practical constants. Pandas' `DataFrame.nlargest()` uses
this under the hood.

---

### Mastery Checklist

- [ ] Implements quickselect from memory
- [ ] Uses randomized pivot to avoid O(n^2) worst case
- [ ] Knows when to use min-heap vs quickselect

---

### Interview Deep-Dive

**Q1 (Medium - LeetCode 215):** Find the k-th largest
element in an unsorted array.

> Three approaches by trade-off:
> 1. Sort: O(n log n), O(1). Simple, slow.
> 2. Min-heap size k: O(n log k), O(k). Good for streaming.
> 3. Quickselect: O(n) avg, O(1). Modifies input array.
> 
> Interview answer: use quickselect with randomized pivot.
> Convert to k-th smallest: idx = n - 1 - (k-1) = n-k.
> After quickselect, arr[n-k] = k-th largest.
> 
> Discuss trade-offs: if input cannot be modified, copy
> first (O(n) space) or use min-heap (O(k) space).
> If k << n, min-heap O(n log k) may be preferred.
> If k ≈ n/2 (median), quickselect O(n) is best.
