---
id: DSA-031
title: Quick Sort
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-004, DSA-026
used_by: DSA-049
related: DSA-021, DSA-030, DSA-032, DSA-049, DSA-091
tags:
  - algorithms
  - sorting
  - quicksort
  - divide-and-conquer
  - pivot
  - in-place
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/dsa/quick-sort/
---

## TL;DR

Quicksort partitions around a pivot, recursively sorts each
partition - O(n log n) average with O(log n) space; the
fastest practical sort for primitives, powering Java's
`Arrays.sort(int[])`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-031 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, sorting, quicksort, pivot |
| **Prerequisites** | DSA-004, DSA-026 |

---

### The Problem This Solves

Merge sort has guaranteed O(n log n) but uses O(n) extra
space. Heapsort uses O(1) space but poor cache behavior.
Quicksort's partition step is cache-friendly (sequential
access), uses O(1) extra memory (excluding stack), and
is consistently the fastest comparison sort for random data
in practice - despite the O(n²) worst case.

---

### Textbook Definition

Quicksort is a divide-and-conquer algorithm. Choose a pivot
element. Partition: rearrange so all elements less than the
pivot come before it, and all greater elements come after.
Recursively quicksort the sub-arrays before and after the
pivot. The pivot is now in its final sorted position.
Average: O(n log n). Worst (sorted input with bad pivot):
O(n²). Space: O(log n) call stack.

---

### Understand It in 30 Seconds

```
Array: [3, 6, 8, 10, 1, 2, 1]  pivot = last element (1)

After partition:
[1, 1, 8, 10, 3, 2, 6]  (pivot 1 placed correctly)
Wait, that's wrong...

Lomuto scheme, pivot = last:
[3, 6, 8, 10, 1, 2, 1]
Partition: [1, 1, 2, 3, 6, 8, 10]  (1 at index 1 = final)
Recurse on [1] and [2, 3, 6, 8, 10]
```

The partition step places the pivot in its FINAL position
in O(n) - this is the key insight.

---

### How It Works

**Lomuto partition (simple to understand):**

```java
void quickSort(int[] arr, int low, int high) {
    if (low >= high) return;
    int pivotIdx = partition(arr, low, high);
    quickSort(arr, low, pivotIdx - 1);   // before pivot
    quickSort(arr, pivotIdx + 1, high);  // after pivot
}

int partition(int[] arr, int low, int high) {
    int pivot = arr[high];  // last element as pivot
    int i = low - 1;        // boundary of smaller elements
    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(arr, i, j);
        }
    }
    swap(arr, i + 1, high); // place pivot in correct position
    return i + 1;
}
```

**Worst case: sorted input with last-element pivot:**

```
[1, 2, 3, 4, 5] with pivot = last element:
Partition: [1,2,3,4] | 5   → pivot at index 4 (unbalanced)
Partition: [1,2,3] | 4     → pivot at index 3
...
n + (n-1) + ... + 1 = O(n²)
```

**Fix: randomized pivot selection:**

```java
// Randomized quicksort: O(n log n) expected, O(n²) rare
int randomPartition(int[] arr, int low, int high) {
    int r = low + (int)(Math.random() * (high - low + 1));
    swap(arr, r, high);           // swap random to last
    return partition(arr, low, high);
}
```

**Java uses Dual-Pivot Quicksort for primitives:**

```java
// Vladimir Yaroslavskiy's dual-pivot algorithm (Java 7+)
// Two pivots: elements < pivot1, between pivots, > pivot2
// Better cache performance than classic quicksort
// O(n log n) average, O(n²) worst (rare)
Arrays.sort(new int[]{5, 2, 8, 1}); // uses dual-pivot QS
```

---

### Comparison Table

| Algorithm | Time avg | Time worst | Space | Stable | Cache |
|-----------|---------|-----------|-------|--------|-------|
| Quicksort | O(n log n) | O(n²) | O(log n) | No | Excellent |
| Merge sort | O(n log n) | O(n log n) | O(n) | Yes | Good |
| Heap sort | O(n log n) | O(n log n) | O(1) | No | Poor |
| TimSort | O(n log n) | O(n log n) | O(n) | Yes | Good |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Quicksort is O(n log n) guaranteed" | Average case; worst case O(n²) with sorted input and bad pivot choice |
| "Quicksort is not used in practice" | Java uses Dual-Pivot Quicksort for all primitive sorts |
| "Quicksort is unstable so it should be avoided" | Instability matters only for objects with meaningful equality; primitives don't have "relative order" meaning |

---

### Failure Modes & Diagnosis

**Failure: O(n²) performance on nearly sorted data**
- Cause: Always choosing first or last element as pivot on
  sorted input creates maximally unbalanced partitions
- Diagnosis: Sort performance much worse than O(n log n)
  for large sorted inputs
- Fix: Randomize pivot selection or use median-of-three;
  Java's dual-pivot QS has built-in mitigations
- Security note: Attackers can craft input to force O(n²)
  in systems that use deterministic quicksort (algorithmic
  complexity attacks / ReDoS analogy)

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Time (average) | O(n log n) |
| Time (worst) | O(n²) sorted + bad pivot |
| Space | O(log n) stack |
| Stable | No |
| Java use | `Arrays.sort(int[])` (Dual-Pivot) |
| Best fix for worst case | Randomize pivot |

---

### The Surprising Truth

Quicksort's worst case is O(n²), yet it consistently beats
merge sort (O(n log n) guaranteed) in practice. Why?
Cache lines: quicksort's partition step accesses memory
sequentially (excellent locality), while merge sort writes
to an auxiliary array (extra cache pressure). The constant
hidden inside O(n log n) is ~3x smaller for quicksort.
Tony Hoare invented quicksort in 1959 and described it
as "my greatest mistake" before winning the Turing Award.

---

### Mastery Checklist

- [ ] Can implement quicksort with Lomuto partition from
      memory
- [ ] Can explain the worst case and the randomized fix
- [ ] Knows Java uses Dual-Pivot Quicksort for primitives
      and TimSort for objects, and why

---

### Interview Deep-Dive

**Q1 (Medium):** What is the worst case for quicksort and
how do you prevent it?

> Worst case O(n²) occurs when every partition is maximally
> unbalanced - one subarray empty, the other with n-1
> elements. This happens with sorted (or reverse-sorted)
> input when using a fixed pivot (first or last element).
> Prevention: (1) Randomized pivot - pick a random element
> as pivot; probability of O(n²) becomes astronomically
> small. (2) Median-of-three - pick median of first, middle,
> last; avoids sorted-input worst case. (3) Dual-pivot
> (Java's approach) - two pivots create three partitions,
> better balancing on most inputs.

**Q2 (Hard):** Why does Java use Dual-Pivot Quicksort for
primitives but TimSort for objects?

> Two reasons: (1) Stability. TimSort is stable (equal
> elements keep relative order). For objects, stability
> matters (sort Employees by name - equal-name employees
> should keep their original order). Primitives have no
> identity, so stability is irrelevant. (2) Performance.
> Dual-Pivot Quicksort is faster for primitives due to
> cache efficiency and no boxing overhead. TimSort has
> O(n) auxiliary space allocation which is cheaper for
> objects (already heap-allocated) than for primitives.
> Java guarantees `Arrays.sort(Object[])` is stable;
> no such guarantee for `Arrays.sort(int[])`.
