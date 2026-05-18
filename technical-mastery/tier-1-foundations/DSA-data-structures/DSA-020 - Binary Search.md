---
id: DSA-020
title: Binary Search
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-004, DSA-019
used_by: DSA-052, DSA-081
related: DSA-017, DSA-019
tags:
  - algorithms
  - search
  - binary
  - sorted
  - divide-and-conquer
  - o-log-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 20
permalink: /technical-mastery/dsa/binary-search/
---

## TL;DR

Binary search halves the search space at each step by
comparing the target to the midpoint of a sorted collection
- O(log n) where linear search would be O(n).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-020 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, search, binary, O(log n) |
| **Prerequisites** | DSA-004, DSA-019 |

---

### The Problem This Solves

Searching a million-element sorted array with linear search
requires up to 1,000,000 comparisons. Binary search requires
at most 20 (log2(1,000,000) ≈ 20). Sorted data should never
be searched linearly in production.

**EVOLUTION:**
The binary search concept dates to 1946 (John Mauchly).
Despite its simplicity, a correct implementation proved
elusive: Jon Bentley reported in 1986 that 90% of
programmers could not implement it correctly within an hour,
mainly due to off-by-one errors. Java's `Arrays.binarySearch`
implementation itself had an integer overflow bug from 1946
to 2006 (`mid = (low + high) / 2` overflows; fix is
`mid = low + (high - low) / 2`).

---

### Textbook Definition

Binary search finds a target in a sorted array by repeatedly
halving the search interval. At each step: compare target to
the midpoint; if equal return it; if target is less, search
the left half; if target is greater, search the right half.
Continue until found or interval is empty.

Precondition: collection must be sorted.
Time complexity: O(log n). Space: O(1) iterative, O(log n)
recursive due to call stack.

---

### Understand It in 30 Seconds

Find 23 in [1, 5, 9, 12, 18, 23, 31, 45]:

```
Step 1: low=0, high=7, mid=3 → arr[3]=12
        12 < 23 → search right half

Step 2: low=4, high=7, mid=5 → arr[5]=23
        23 == 23 → FOUND at index 5
```

8 elements → 2 comparisons. 1 billion elements → 30.

---

### First Principles

Binary search is divide and conquer applied to search.
Each comparison eliminates exactly half the remaining
candidates. After k comparisons, at most n/2^k candidates
remain. When n/2^k = 1, we have our answer: k = log2(n).

This is why "binary" - we make a binary decision (left or
right) that halves the space each time.

---

### How It Works

**BAD - common off-by-one error:**

```java
// BUG: incorrect bounds can skip or repeat elements
int binarySearchBad(int[] arr, int target) {
    int low = 0, high = arr.length;   // BUG: should be length-1
    while (low < high) {              // BUG: should be <=
        int mid = (low + high) / 2;   // BUG: overflow for large arrays
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) low = mid;  // BUG: infinite loop
        else high = mid;
    }
    return -1;
}
```

**GOOD - correct implementation:**

```java
int binarySearch(int[] arr, int target) {
    int low = 0, high = arr.length - 1;  // inclusive bounds
    while (low <= high) {                 // = handles single element
        // Prevents (low + high) overflow for large indices
        int mid = low + (high - low) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) low = mid + 1;  // exclude mid
        else high = mid - 1;                    // exclude mid
    }
    return -1;  // not found
}
// Matches Arrays.binarySearch contract
```

**Generalized binary search on a condition (very powerful):**

```java
// Find smallest index where condition is true in sorted space
// Works for: first occurrence, lower_bound, "at least k"
int lowerBound(int[] arr, int target) {
    int low = 0, high = arr.length;  // half-open: [low, high)
    while (low < high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] < target) low = mid + 1;
        else high = mid;
    }
    return low;  // first index where arr[i] >= target
}
```

**Binary search on answer (not on an array):**

```java
// How many days needed? Binary search on the answer.
// isFeasible(days) = true means days is enough
int minDays = Integer.MAX_VALUE;
int lo = 1, hi = maxPossibleDays;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (isFeasible(mid)) { minDays = mid; hi = mid - 1; }
    else lo = mid + 1;
}
```

---

### Comparison Table

| Search | Time (avg) | Time (worst) | Precondition |
|--------|-----------|--------------|--------------|
| Linear Search | O(n) | O(n) | None |
| Binary Search | O(log n) | O(log n) | Sorted |
| Hash Map lookup | O(1) | O(n) worst case | Hash function |
| BST search | O(log n) avg | O(n) unbalanced | BST invariant |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Binary search is simple to implement" | Jon Bentley 1986: 90% of programmers failed; overflow, off-by-one, and termination bugs are common |
| "`(low + high) / 2` is always fine" | Overflows when low + high > Integer.MAX_VALUE (2.1B); use `low + (high - low) / 2` |
| "Binary search only works on arrays" | Works on any monotonic condition: binary search on the answer is a powerful generalization |
| "Always use binary search on sorted data" | For very small collections (<~20), linear search can be faster due to cache effects |

---

### Failure Modes & Diagnosis

**Failure 1: Infinite loop**
- Cause: `low = mid` instead of `low = mid + 1` (or `high = mid`
  instead of `high = mid - 1`) means the search space never
  shrinks
- Diagnosis: Watch low/high values; if they stop changing,
  the loop will run forever
- Fix: Always use `low = mid + 1` and `high = mid - 1` (or
  use the half-open interval [low, high) consistently)

**Failure 2: Integer overflow in mid calculation**
- Cause: `(low + high)` overflows when both are near
  Integer.MAX_VALUE
- Fix: Always use `low + (high - low) / 2`

**Failure 3: Off-by-one on boundary conditions**
- Cause: `high = arr.length` (out of bounds) instead of
  `arr.length - 1`, or `while (low < high)` misses the last
  element
- Fix: Use inclusive bounds with `while (low <= high)` OR
  half-open bounds with `while (low < high)` consistently;
  never mix

---

### Related Keywords

**Prerequisites:**
- [[DSA-004 - Big O Notation - The Language of Efficiency]]

**Builds toward:**
- [[DSA-017 - Binary Search Tree (BST)]]
- [[DSA-091 - Quickselect (k-th Largest Element)]]

**See also:**
- [[DSA-019 - Linear Search]]

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Time | O(log n) |
| Space | O(1) iterative |
| Precondition | Sorted (or monotonic condition) |
| Overflow-safe mid | `low + (high - low) / 2` |
| Java built-in | `Arrays.binarySearch()`, `Collections.binarySearch()` |
| Returns (Java) | Index if found; `-(insertion point) - 1` if not |

**3 things to always check:** correct bounds (inclusive vs
half-open), overflow-safe mid, both branches move progress.

**One-liner for interviews:** "Binary search eliminates half
the search space per step, giving O(log n), but requires
sorted data and careful off-by-one handling."

---

### Transferable Wisdom

Binary search generalizes beyond arrays: any time you have
a monotonic function f(x) and need to find the smallest x
where f(x) becomes true, binary search the answer space.
Used in: network congestion control, database query
optimization, game theory, numerical methods (bisection
method for root finding).

---

### The Surprising Truth

The first correct published binary search appeared in 1946.
The first correct implementation in a textbook appeared in
1962 - 16 years later. And a commonly used Java standard
library implementation had an integer overflow bug from 1946
until 2006, when it was reported by Joshua Bloch (author of
Effective Java). A 60-year-old bug in one of the most-taught
algorithms in computer science.

---

### Mastery Checklist

- [ ] Can implement binary search from memory with correct
      bounds and overflow-safe mid
- [ ] Understands inclusive vs half-open interval strategies
- [ ] Can apply binary search to a monotonic condition
      ("binary search on the answer")
- [ ] Knows when NOT to use binary search (unsorted data,
      very small collections)

---

### Think About This

1. You have a sorted array of 1 billion integers. Binary
   search takes ~30 comparisons. But each array access
   might be a cache miss. At what point does this become
   a bottleneck, and how would you address it?

2. Write a binary search to find the first bad version in
   a software release history where all versions after a
   bad one are also bad. This is "binary search on a
   condition" - the monotonic function is
   `isBadVersion(v)`.

3. **TYPE G:** A team is using `ArrayList.contains()` to
   check membership in a sorted list of 100K IDs. It's
   called 50,000 times per request. What would you change?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the time complexity of binary search
and what is its precondition?

> O(log n) time, O(1) space (iterative). Precondition:
> the collection must be sorted (or more generally, the
> search condition must be monotonic - transitions from
> false to true exactly once). Without the sorted
> precondition, binary search produces incorrect results.

**Q2 (Medium):** How do you find the first and last
occurrence of a target in a sorted array with duplicates?

> Two binary searches: one to find the leftmost occurrence
> (lower bound) and one to find the rightmost (upper bound).
> For leftmost: when `arr[mid] == target`, set `high = mid`
> and continue (don't return immediately).
> For rightmost: when `arr[mid] == target`, set `low = mid`
> and continue. This ensures all occurrences are scanned.
> O(2 log n) = O(log n).

**Q3 (Hard):** You have a rotated sorted array
[4,5,6,7,0,1,2]. How do you binary search in O(log n)?

> At each step, one half is always sorted. Check which half
> is sorted by comparing arr[low] to arr[mid]. If
> arr[low] <= arr[mid], left half is sorted - check if
> target is in [arr[low], arr[mid]]; if yes, search left,
> else search right. If right half is sorted, similar logic.
> This handles the rotation with no extra passes: O(log n).
