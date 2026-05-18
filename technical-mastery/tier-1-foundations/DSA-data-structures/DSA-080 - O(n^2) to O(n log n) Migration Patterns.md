---
id: DSA-080
title: O(n^2) to O(n log n) Migration Patterns
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-023, DSA-028, DSA-014
used_by: DSA-077
related: DSA-023, DSA-030, DSA-072
tags:
  - algorithms
  - optimization
  - migration
  - performance
  - n-squared
  - n-log-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 80
permalink: /technical-mastery/dsa/n-squared-to-n-log-n/
---

## TL;DR

Most O(n^2) algorithms can be reduced to O(n log n) by
replacing nested loops with sorting, binary search, hash
sets, or heaps - the single most impactful optimization
pattern in production systems.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-080 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, O(n^2) migration, optimization |
| **Prerequisites** | DSA-023, DSA-028, DSA-014 |

---

### The Problem This Solves

n=10,000 with O(n^2) = 100 million operations = ~100ms.
n=100,000 with O(n^2) = 10 billion = ~10 seconds. The
same 10x more data makes the feature unusable. Recognizing
O(n^2) patterns and applying proven reduction techniques
is a critical production skill.

---

### Patterns for Reducing O(n^2) to O(n log n)

**Pattern 1: Replace nested linear scan with sort + binary search**

```java
// BAD: O(n^2) - for each element, scan all others for complement
boolean hasPairSum(int[] arr, int target) {
    for (int i = 0; i < arr.length; i++)
        for (int j = i+1; j < arr.length; j++)
            if (arr[i] + arr[j] == target) return true;
    return false;
}

// GOOD: O(n log n) - sort, then binary search for complement
boolean hasPairSumFast(int[] arr, int target) {
    Arrays.sort(arr); // O(n log n)
    for (int x : arr) {
        int complement = target - x;
        int idx = Arrays.binarySearch(arr, complement);
        if (idx >= 0 && arr[idx] != x) return true;
        // O(log n) per element → O(n log n) total
    }
    return false;
}
```

**Pattern 2: Replace nested scan with HashSet for O(1) lookup**

```java
// BAD: O(n^2) - check each pair
// GOOD: O(n) - build set, then O(1) lookup per element
boolean hasPairSumO1(int[] arr, int target) {
    Set<Integer> seen = new HashSet<>();
    for (int x : arr) {
        if (seen.contains(target - x)) return true;
        seen.add(x);
    }
    return false; // O(n) time, O(n) space
}
```

**Pattern 3: Replace nested sort with single sort + sweep**

```java
// BAD: O(n^2) - find all overlapping intervals by checking pairs
// GOOD: O(n log n) - sort by start, then linear sweep
List<int[]> mergeIntervals(int[][] intervals) {
    Arrays.sort(intervals, (a,b) -> a[0] - b[0]); // O(n log n)
    List<int[]> result = new ArrayList<>();
    int[] curr = intervals[0];
    for (int[] next : intervals) {           // O(n)
        if (next[0] <= curr[1])
            curr[1] = Math.max(curr[1], next[1]);
        else {
            result.add(curr);
            curr = next;
        }
    }
    result.add(curr);
    return result; // Total: O(n log n)
}
```

**Pattern 4: Replace nested tracking with heap**

```java
// BAD: O(n^2) - find k-th largest by repeatedly scanning
// GOOD: O(n log k) - min-heap of size k
int findKthLargest(int[] nums, int k) {
    PriorityQueue<Integer> heap = new PriorityQueue<>(k);
    for (int x : nums) {          // O(n log k)
        heap.offer(x);
        if (heap.size() > k) heap.poll(); // keep k largest
    }
    return heap.peek(); // kth largest
}
```

---

### O(n^2) Pattern Recognition

| Pattern | Signal | Reduction |
|---------|--------|-----------|
| Nested loops on same array | `for i for j` | Sort + binary search |
| Check all pairs for condition | `if arr[i] + arr[j] == target` | HashSet O(n) |
| All vs all comparison | `O(n^2) comparisons` | Sort + sweep O(n log n) |
| Repeated max/min finding | `O(n) per find, n finds` | Heap O(n log k) |
| Find all overlaps | `O(n^2) pair checks` | Sort by start + sweep |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Sort adds overhead - O(n^2) is faster for small n" | For n < 100, yes. For n > 1000, O(n log n) wins decisively |
| "Every O(n^2) can become O(n log n)" | Some are O(n^2) by theoretical lower bound (e.g., matrix multiplication without Strassen); not all reductions apply |

---

### Failure Modes & Diagnosis

**Failure: O(n^2) discovered in production at scale**
- Detection: Request time grows quadratically as data
  grows; flame graph shows 2 levels of the same method
- Root cause: List.contains() inside a loop
  (O(n) per call, called n times)
- Fix: Replace inner List with HashSet

---

### Quick Reference Card

| Complexity | Strategy |
|-----------|----------|
| O(n^2) pair search | HashSet → O(n) |
| O(n^2) sort-related | Sort once → O(n log n) |
| O(n^2) k-max/min | Heap of size k → O(n log k) |
| O(n^2) overlaps | Sort + sweep → O(n log n) |
| O(n * k) search | Binary search → O(n log k) |

---

### The Surprising Truth

Java's List.contains() inside a for-each loop is the single
most common O(n^2) bug in enterprise Java codebases. It's
invisible in code review because it looks like two innocent
lines: a loop and a contains() call. At 100 elements no
one notices. At 100,000 elements it causes production
incidents. The fix: replace `List` with `Set` for the
inner lookup. This single change has saved multiple
production systems from O(n^2) latency degradation.

---

### Mastery Checklist

- [ ] Recognizes the List.contains() in a loop anti-pattern
- [ ] Can apply all 4 reduction patterns from memory
- [ ] Can calculate when the O(n log n) breakeven is worth it

---

### Interview Deep-Dive

**Q1 (Medium):** You have two arrays. Find all elements
that appear in both arrays. What's the optimal solution?

> O(n*m) brute force: nested loops.
> O((n+m) log(n+m)) with sort: sort both, merge-scan.
> O(n+m) with HashSet: put smaller array in set, scan
> larger array checking containment.
> O(n+m) with sorting: sort arr1 O(n log n), for each
> element in arr2 binary search arr1 O(m log n).
> Optimal: O(n+m) with HashSet if n and m are similar.
> O((n+m) log(min(n,m))) with sort if memory is limited.
> Real production consideration: if arr1 is static and
> arr2 changes per request, build HashSet from arr1 once
> and reuse - O(n) build, O(1) amortized per query.
