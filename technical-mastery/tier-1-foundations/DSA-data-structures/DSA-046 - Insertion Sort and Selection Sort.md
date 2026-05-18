---
id: DSA-046
title: Insertion Sort and Selection Sort
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-004, DSA-021
used_by: DSA-043
related: DSA-021, DSA-030, DSA-031, DSA-043
tags:
  - algorithms
  - sorting
  - insertion-sort
  - selection-sort
  - o-n-squared
  - small-arrays
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 46
permalink: /technical-mastery/dsa/insertion-sort-selection-sort/
---

## TL;DR

Insertion sort builds a sorted prefix by inserting each
element in its correct position - O(n) for nearly sorted
input, the real-world winner for small arrays (n<50),
used inside Java's TimSort.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-046 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, sorting, insertion-sort, O(n²) |
| **Prerequisites** | DSA-004, DSA-021 |

---

### The Problem This Solves

Quicksort and merge sort have overhead for small arrays.
For n < ~50 elements, insertion sort beats them due to
smaller constants and better cache behavior. TimSort uses
insertion sort for small runs (< 32 elements) before
merging with merge sort.

---

### How It Works

**Insertion sort:**

```java
// Like sorting cards in hand: take each card, slide it
// into the correct position in the sorted left portion
void insertionSort(int[] arr) {
    for (int i = 1; i < arr.length; i++) {
        int key = arr[i];
        int j = i - 1;
        // Shift right to make room for key
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;  // insert at correct position
    }
}
// O(n²) worst/avg,  O(n) best (already sorted),  O(1) space
```

**Selection sort:**

```java
// Find the minimum of unsorted portion, swap to front
void selectionSort(int[] arr) {
    for (int i = 0; i < arr.length - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < arr.length; j++) {
            if (arr[j] < arr[minIdx]) minIdx = j;
        }
        swap(arr, i, minIdx);
    }
}
// O(n²) all cases,  exactly n*(n-1)/2 comparisons
// Only n swaps (minimum possible) - useful if swaps are expensive
```

---

### Comparison Table

| Algorithm | Best | Avg | Worst | Stable | Swaps |
|-----------|------|-----|-------|--------|-------|
| Insertion Sort | O(n) | O(n²) | O(n²) | Yes | O(n²) |
| Selection Sort | O(n²) | O(n²) | O(n²) | No* | O(n) |
| Bubble Sort | O(n) | O(n²) | O(n²) | Yes | O(n²) |

*Selection sort can be made stable with care; standard impl is not.

---

### Quick Reference Card

| Use insertion sort when | Use selection sort when |
|------------------------|------------------------|
| Nearly sorted data | Minimizing writes/swaps is critical |
| Small arrays (n<50) | Simple implementation needed |
| Online: sort as items arrive | Memory writes are expensive |
| TimSort internal small run sort | (rarely in production) |

---

### The Surprising Truth

TimSort, Java's default sort for objects, uses insertion
sort internally for subarrays smaller than 32 elements.
The overhead of divide-and-conquer recursion exceeds the
O(n²) cost of insertion sort for such small n. Insertion
sort's O(n) best case on already-sorted runs is also why
TimSort is O(n) for sorted arrays overall.

---

### Mastery Checklist

- [ ] Can implement insertion sort from memory
- [ ] Knows insertion sort is O(n) for sorted input and
      where it's used in Java (TimSort)
- [ ] Can explain why selection sort minimizes swaps

---

### Interview Deep-Dive

**Q1 (Easy):** When does insertion sort outperform
quicksort in practice?

> (1) Small arrays (n < ~50): insertion sort's small
> constant dominates quicksort's log factor. (2) Nearly
> sorted data: insertion sort is O(n) for already-sorted
> input; quicksort is still O(n log n). (3) Online sorting:
> elements arrive one at a time; insertion sort can insert
> each new element in O(n) into the already-sorted prefix.
> This is why TimSort uses insertion sort for small runs
> and achieves O(n) on already-sorted object arrays.
