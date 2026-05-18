---
id: DSA-030
title: Merge Sort
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-004, DSA-026
used_by: DSA-068
related: DSA-021, DSA-031, DSA-032, DSA-049, DSA-068
tags:
  - algorithms
  - sorting
  - merge-sort
  - divide-and-conquer
  - stable-sort
  - o-n-log-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/dsa/merge-sort/
---

## TL;DR

Merge sort divides an array in half, recursively sorts each
half, then merges them - O(n log n) guaranteed, stable,
the basis of Java's TimSort for objects.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-030 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, sorting, merge-sort, O(n log n) |
| **Prerequisites** | DSA-004, DSA-026 |

---

### The Problem This Solves

Bubble sort and insertion sort are O(n²) - catastrophic for
large inputs. Merge sort achieves O(n log n) worst case
(unlike quicksort's O(n²) worst case) and is stable
(equal elements preserve relative order), making it ideal
for sorting objects and external sorting.

---

### Textbook Definition

Merge sort is a divide-and-conquer sorting algorithm.
Divide: split the array into two halves. Conquer: recursively
sort each half. Combine: merge two sorted halves into one
sorted array. Base case: an array of 0 or 1 elements is
already sorted. Time: O(n log n) in all cases. Space: O(n)
auxiliary for the merge step.

---

### Understand It in 30 Seconds

```
Sort [38, 27, 43, 3, 9, 82, 10]:

Divide:     [38,27,43,3]   [9,82,10]
Divide:   [38,27] [43,3] [9,82] [10]
Divide:  [38][27] [43][3] [9][82] [10]

Merge:    [27,38] [3,43] [9,82] [10]
Merge:      [3,27,38,43]  [9,10,82]
Merge:        [3,9,10,27,38,43,82]
```

log n levels, n work per level = O(n log n).

---

### First Principles

Why does merging two sorted arrays take O(n)?
Compare the fronts: take the smaller one.
This requires O(1) per element → O(n) total for n elements.
The log n levels come from splitting in half each time.
Together: O(n log n).

**Why O(n log n) is optimal for comparison-based sorting:**
Any comparison-based sort must make at least log2(n!)
comparisons to distinguish all n! orderings. By Stirling's
approximation, log2(n!) = O(n log n). Merge sort matches
this bound.

---

### How It Works

**Merge sort implementation:**

```java
void mergeSort(int[] arr, int left, int right) {
    if (left >= right) return;          // base case: 0 or 1

    int mid = left + (right - left) / 2;
    mergeSort(arr, left, mid);          // sort left half
    mergeSort(arr, mid + 1, right);     // sort right half
    merge(arr, left, mid, right);       // merge both halves
}

void merge(int[] arr, int left, int mid, int right) {
    // Auxiliary space: O(n) per merge call
    int[] tmp = new int[right - left + 1];
    int i = left, j = mid + 1, k = 0;

    while (i <= mid && j <= right) {
        // Stable: <= preserves relative order of equals
        if (arr[i] <= arr[j]) tmp[k++] = arr[i++];
        else                   tmp[k++] = arr[j++];
    }
    while (i <= mid)    tmp[k++] = arr[i++]; // copy remainder
    while (j <= right)  tmp[k++] = arr[j++];

    // Copy back
    System.arraycopy(tmp, 0, arr, left, tmp.length);
}
```

**Visualizing recursion tree:**

```
               [left, right]
              /             \
       [left, mid]      [mid+1, right]
       /       \           /       \
   ...          ...      ...        ...
  [i,i]       [j,j]    [k,k]     [l,l]   ← base cases
```

**Merge sort in practice - Java objects use TimSort:**

```java
// Arrays.sort(Object[]) uses TimSort - merge sort hybrid
// TimSort detects already-sorted runs, O(n) for sorted input
String[] names = {"Charlie", "Alice", "Bob"};
Arrays.sort(names);  // ["Alice", "Bob", "Charlie"]
// Stable: equal elements keep original positions
```

---

### Comparison Table

| Algorithm | Time (avg) | Time (worst) | Space | Stable |
|-----------|-----------|--------------|-------|--------|
| Merge Sort | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Sort | O(n log n) | O(n²) | O(log n) | No |
| Heap Sort | O(n log n) | O(n log n) | O(1) | No |
| TimSort | O(n log n) | O(n log n) | O(n) | Yes |
| Insertion Sort | O(n²) | O(n²) | O(1) | Yes |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Merge sort is the fastest O(n log n) sort" | Quicksort is typically faster in practice due to cache efficiency; merge sort's O(n) auxiliary allocation is a hidden cost |
| "Java Arrays.sort() uses merge sort" | For primitives: Dual-Pivot Quicksort. For objects: TimSort (merge sort + insertion sort hybrid) |
| "Merge sort requires O(n log n) space" | O(n) auxiliary space - n for the temporary array, not n log n |

---

### Failure Modes & Diagnosis

**Failure: Excessive GC pressure from merge sort**
- Cause: Each `merge()` call allocates a new temporary array;
  for n=10^6, many short-lived arrays created
- Diagnosis: GC logs show frequent minor GC during sort
- Fix: Pre-allocate a single temporary array of size n,
  pass it to all merge calls; reduce allocation to O(1) per
  merge instead of O(n) per call

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Time (all cases) | O(n log n) |
| Space | O(n) auxiliary |
| Stable | Yes |
| When to use | Object sorting, external sort, stable required |
| Java use | TimSort under `Arrays.sort(Object[])` |
| Recursive depth | O(log n) stack frames |

---

### The Surprising Truth

Merge sort's most powerful application is not in-memory
sorting at all - it is external sorting. When you have 1TB
of data that does not fit in RAM, you chunk it into 1GB
pieces, sort each in RAM, then merge the sorted chunks with
a priority queue. This is how databases sort large result
sets and how Hadoop's sort phase works. The merge insight
generalizes to any divide-and-merge problem, not just sorting.

---

### Mastery Checklist

- [ ] Can implement merge sort from memory including the
      merge step
- [ ] Can explain why merge sort is O(n log n) by drawing
      the recursion tree
- [ ] Understands that Java uses TimSort (not merge sort)
      for object arrays
- [ ] Knows when to choose merge sort vs quicksort

---

### Interview Deep-Dive

**Q1 (Easy):** What is the time and space complexity of
merge sort and why is it O(n) space (not O(n log n))?

> Time: O(n log n) - log n levels of recursion, O(n) work
> per level for the merge step. Space: O(n) - only one level
> of auxiliary arrays is alive at any time. When merging
> at depth d, we have 2^d subarrays each of size n/2^d, but
> the temp arrays for one level total n elements. Recursion
> stack is O(log n). Total: O(n) auxiliary + O(log n) stack
> = O(n).

**Q2 (Hard):** How would you implement an external merge
sort for a 1TB file with only 1GB of RAM?

> Phase 1 (sort chunks): Read 1GB chunks, sort each in RAM
> using in-memory sort, write sorted chunk to disk.
> Result: 1000 sorted 1GB files.
> Phase 2 (merge): Use a min-heap of size 1000 initialized
> with the first record from each chunk. Repeatedly poll
> the min, write to output, then push the next record from
> that chunk's file. Each record is read and written once:
> O(n log k) where k=1000. This is the standard database
> external sort approach.
