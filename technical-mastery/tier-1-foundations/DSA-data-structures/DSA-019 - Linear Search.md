---
id: DSA-019
title: Linear Search
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-008
used_by: DSA-020
related: DSA-020, DSA-023
tags:
  - algorithms
  - search
  - linear
  - fundamentals
  - o-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/dsa/linear-search/
---

## TL;DR

Linear search scans every element until finding the target -
O(n) worst case, works on any collection, and is correct
when no better structure exists.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-019 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, search, linear, O(n) |
| **Prerequisites** | DSA-008 |

---

### The Problem This Solves

Given a collection and a target value, determine if the
target is present (and where). Linear search is the
baseline: it works on any collection with no preconditions.

---

### Textbook Definition

Linear search (sequential search) examines each element in
a collection sequentially from start to end until the target
is found or all elements are examined. Time complexity: O(n)
worst and average case, O(1) best case (target at index 0).

---

### Understand It in 30 Seconds

Search for "Dave" in: [Alice, Bob, Carol, Dave, Eve].
Check Alice: no. Check Bob: no. Check Carol: no. Check Dave:
yes! Return index 3. Worst case: check all 5 elements.

---

### How It Works

```java
// Basic linear search
int linearSearch(int[] arr, int target) {
    for (int i = 0; i < arr.length; i++) {
        if (arr[i] == target) return i;
    }
    return -1;  // not found
}
// O(n) worst case, O(1) best case
```

**When linear search wins over binary search:**

| Condition | Linear | Binary |
|-----------|--------|--------|
| Unsorted array | Yes | No |
| Small array (n < 50) | Yes (simpler) | Marginal gain |
| Single search on data | Yes (no sort cost) | No (sort O(n log n) first) |
| Sorted array, frequent search | No | Yes, O(log n) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Linear search is never correct in production" | For small collections or one-off searches, linear scan is faster than building a hash map |
| "Binary search is always better" | Binary search requires sorted data; linear search has no preconditions |

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Time (worst/avg) | O(n) |
| Time (best) | O(1) |
| Space | O(1) |
| Requirement | None (any collection) |
| Break-even with binary | ~n=50 for single search |

---

### Mastery Checklist

- [ ] Can implement linear search and name its complexity
- [ ] Knows when linear search is preferable to binary search
- [ ] Understands the "sort then binary search" trade-off
      based on query frequency

---

### Interview Deep-Dive

**Q1 (Easy):** When is linear search appropriate despite
its O(n) complexity?

> (1) Unsorted data where sorting is not worth the O(n log n)
> cost for infrequent search. (2) Very small arrays (< ~50)
> where binary search overhead exceeds linear scan time due
> to simpler code and better branch prediction. (3) Finding
> elements in streams or iterators where random access is
> not possible. (4) First-time search when data will not
> be searched again.
