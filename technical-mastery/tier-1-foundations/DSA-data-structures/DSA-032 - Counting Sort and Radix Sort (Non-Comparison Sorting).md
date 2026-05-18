---
id: DSA-032
title: Counting Sort and Radix Sort (Non-Comparison Sorting)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-004, DSA-030
used_by: DSA-049
related: DSA-030, DSA-031, DSA-049
tags:
  - algorithms
  - sorting
  - counting-sort
  - radix-sort
  - linear-time
  - non-comparison
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/dsa/counting-sort-radix-sort/
---

## TL;DR

Counting sort and radix sort break the O(n log n) barrier
for comparison-based sorting - achieving O(n) for integers
in a bounded range by counting rather than comparing.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-032 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, sorting, linear-time, non-comparison |
| **Prerequisites** | DSA-004, DSA-030 |

---

### The Problem This Solves

The O(n log n) comparison sort lower bound assumes you can
only learn about element ordering via comparisons. If you
know the value range (e.g., age 0-120, grades 0-100), you
can sort without comparisons in O(n + k) where k is the
range. Sorting 1M ages? O(n), not O(n log n).

---

### Textbook Definition

**Counting sort:** For integers in range [0, k], count
occurrences of each value, compute prefix sums (to get
output positions), then place each element at its correct
index. Time: O(n + k). Space: O(k) counter array.
Stable with prefix-sum technique.

**Radix sort:** Sort integers by digit, from least
significant to most significant (LSD radix sort).
Use a stable sort (counting sort) for each digit.
Time: O(d * (n + k)) where d = digits, k = radix (10).
For n-bit integers: O(n) with base 2^(log n).

---

### Understand It in 30 Seconds

Count sort [3, 1, 4, 1, 5, 9, 2, 6]:
Range 0-9, so count array of size 10.

```
count[0]=0, count[1]=2, count[2]=1, count[3]=1,
count[4]=1, count[5]=1, count[6]=1, count[7]=0,
count[8]=0, count[9]=1

Output: [1,1,2,3,4,5,6,9]  ← O(n) with O(k) space
```

---

### How It Works

**Counting sort (stable version):**

```java
// Sort arr[] with values in [0, maxVal]
int[] countingSort(int[] arr, int maxVal) {
    int[] count = new int[maxVal + 1];

    // Phase 1: count occurrences
    for (int val : arr) count[val]++;

    // Phase 2: prefix sum (cumulative)
    // count[i] = number of elements <= i
    for (int i = 1; i <= maxVal; i++)
        count[i] += count[i - 1];

    // Phase 3: place elements in output (reverse for stability)
    int[] output = new int[arr.length];
    for (int i = arr.length - 1; i >= 0; i--) {
        output[--count[arr[i]]] = arr[i];
    }
    return output;
}
// Time: O(n + k),  Space: O(n + k)
```

**Radix sort (LSD - Least Significant Digit first):**

```java
// Sort non-negative integers
void radixSort(int[] arr) {
    int max = Arrays.stream(arr).max().getAsInt();
    // Sort by each digit position
    for (int exp = 1; max / exp > 0; exp *= 10) {
        countingSortByDigit(arr, exp);
    }
}

void countingSortByDigit(int[] arr, int exp) {
    int[] output = new int[arr.length];
    int[] count = new int[10]; // digits 0-9

    for (int val : arr)
        count[(val / exp) % 10]++;
    for (int i = 1; i < 10; i++)
        count[i] += count[i - 1];
    for (int i = arr.length - 1; i >= 0; i--) {
        int digit = (arr[i] / exp) % 10;
        output[--count[digit]] = arr[i];
    }
    System.arraycopy(output, 0, arr, 0, arr.length);
}
// Time: O(d * n) where d = number of digits
```

---

### Comparison Table

| Algorithm | Time | Space | Stable | Requirement |
|-----------|------|-------|--------|-------------|
| Counting Sort | O(n + k) | O(k) | Yes | Integer range k |
| Radix Sort | O(d * n) | O(n + k) | Yes | Integer, fixed digits |
| Merge Sort | O(n log n) | O(n) | Yes | Comparable |
| Quick Sort | O(n log n) avg | O(log n) | No | Comparable |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "O(n) sorts are always better than O(n log n)" | Only when k (range) is small; if k = n², counting sort is O(n²) - worse than merge sort |
| "These sorts break the O(n log n) lower bound" | The lower bound is for comparison sorts; these avoid comparisons by exploiting integer structure |

---

### Quick Reference Card

| Sort | When to use |
|------|------------|
| Counting sort | Small integer range, e.g., grades 0-100, age 0-120 |
| Radix sort | Large integers, fixed number of digits |
| General sort | Arbitrary objects, large or unknown range |

---

### Mastery Checklist

- [ ] Understands why O(n) is possible for integers
      (no comparison → not bound by comparison lower bound)
- [ ] Can identify when counting sort is appropriate
      (bounded integer range)
- [ ] Knows the practical Java alternative:
      `Arrays.sort()` handles most cases; use counting
      sort only when profiling shows sorting is a bottleneck

---

### Interview Deep-Dive

**Q1 (Medium):** You have 1 million ages (integers 0-120).
What sorting algorithm would you use and why?

> Counting sort: O(n + k) with k=120. Create a count array
> of size 121, count occurrences of each age, then reconstruct
> the sorted array from the counts. Time: O(n + 120) = O(n).
> Space: O(120) = O(1). This is dramatically faster than
> O(n log n) for this specific case because we exploit that
> all values fall in a known small range.
