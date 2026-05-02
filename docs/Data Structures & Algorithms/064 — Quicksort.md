---
layout: default
title: "Quicksort"
parent: "Data Structures & Algorithms"
nav_order: 64
permalink: /dsa/quicksort/
number: "0064"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Recursion, Divide and Conquer, Arrays
used_by: Dual-Pivot Quicksort (Java Arrays.sort), Quickselect, Introsort
related: Mergesort, Heapsort, Timsort
tags:
  - algorithm
  - intermediate
  - pattern
  - performance
  - datastructure
---

# 064 — Quicksort

⚡ TL;DR — Quicksort is a divide-and-conquer sorting algorithm that partitions around a pivot and recursively sorts partitions — O(N log N) average, O(N²) worst case, but fastest in practice due to cache efficiency.

| #064 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Recursion, Divide and Conquer, Arrays | |
| **Used by:** | Dual-Pivot Quicksort (Java Arrays.sort), Quickselect, Introsort | |
| **Related:** | Mergesort, Heapsort, Timsort | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You have 1 million integers to sort. Bubble sort and insertion sort are O(N²) — 10¹² comparisons — taking hours. You need an algorithm that sorts in O(N log N), like mergesort. But mergesort requires O(N) extra memory for the merge step — for large arrays, this means allocating hundreds of megabytes of auxiliary space that may not be available, or fragmenting memory badly.

THE BREAKING POINT:
O(N²) algorithms are too slow for large datasets. O(N log N) mergesort solves the speed problem but introduces a memory problem: O(N) auxiliary space and poor cache behavior (accessing two separate in/out buffers). For cache-heavy workloads, memory access patterns dominate runtime.

THE INVENTION MOMENT:
Instead of merging two sorted halves (which requires auxiliary space), partition the array in-place around a "pivot" value: move all elements smaller than the pivot to its left, all larger to its right. This partition step is O(N) and in-place. Then recursively sort each half. Average case: O(N log N). In practice, in-place partition means all operations touch a single array — maximising cache reuse. This is exactly why **Quicksort** was created.

---

### 📘 Textbook Definition

**Quicksort** is a divide-and-conquer sorting algorithm that selects a pivot element, partitions the array around the pivot (all smaller elements left, all larger right), and recursively sorts the sub-arrays. Average time complexity: O(N log N). Worst case: O(N²) when the pivot repeatedly divides the array into 1 vs N-1 elements (e.g., sorted input with last-element pivot). Space complexity: O(log N) average (recursion stack). Quicksort is **not stable** — equal elements may be reordered.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pick a pivot, put smaller elements to its left and larger to its right, then recursively sort each side.

**One analogy:**
> Imagine sorting a shuffled deck of cards. Pick one card (the pivot). Quickly deal cards into two piles: "lower value than pivot" and "higher value than pivot." Now independently sort each pile the same way. After enough rounds of splitting, every pile has one card — already sorted. The entire deck is sorted by reassembling.

**One insight:**
Quicksort's average O(N log N) performance with O(log N) space relies on a fortunate property: a randomly chosen pivot splits the array roughly in half on average, producing a balanced recursion tree of depth O(log N). The danger is a "bad pivot" that creates a lopsided split (one partition of size 1, one of N-1), which degrades to O(N²). Randomised pivot selection makes this extremely improbable — and this is why production Quicksort implementations randomise the pivot or use median-of-three.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. After partitioning, the pivot is in its **final sorted position** — it never moves again.
2. All elements in the left partition are ≤ pivot; all in the right partition are ≥ pivot.
3. The two partitions are sorted **independently** — no merging step is needed.

DERIVED DESIGN:
Invariants 1 and 3 together mean Quicksort never needs auxiliary memory for combining results (unlike mergesort's merge step). The partition step achieves invariants 1 and 2 in O(N) in-place via Lomuto or Hoare partition:

**Lomuto partition** (simpler):
Use `i` as the boundary of "small" elements. Walk `j` from left to right. When `arr[j] <= pivot`, swap `arr[j]` with `arr[++i]`. At end, swap pivot into position `i+1`.

**Hoare partition** (faster in practice, ~3x fewer swaps):
Use two pointers starting at opposite ends. Walk them inward until they cross. Swap elements that are on the wrong sides. The pivot ends up somewhere in the middle (not necessarily its final position), requiring two recursive calls to cover the full range.

**Pivot selection strategies:**
- Last element: simple but O(N²) on sorted input
- Random element: O(N²) probability < 1/N! for any fixed input
- Median-of-three: take median of first, middle, last elements
- Ninther (Java's default): median of three medians for large arrays

**Why Quicksort is faster than Mergesort in practice despite same big-O:**
Quicksort's partition step accesses the array sequentially, maximising CPU cache line usage. Mergesort accesses two separate arrays alternately with pointer chasing (cache unfriendly). For modern CPUs with large L1/L2 caches, the constant factor difference is 2-4x. This is why Java's `Arrays.sort` uses Dual-Pivot Quicksort for primitive arrays (cache friendly) but Timsort for object arrays (stable + cache friendly).

THE TRADE-OFFS:
Gain: O(N log N) average, O(log N) space, best cache performance of all comparison sorts.
Cost: O(N²) worst case on adversarial input (mitigated by randomisation); not stable (equal elements can swap order).

---

### 🧪 Thought Experiment

SETUP:
Already-sorted array [1, 2, 3, 4, 5]. Quicksort with last-element pivot.

WHAT HAPPENS WITH LAST-ELEMENT PIVOT ON SORTED INPUT:
Pivot = 5 (last). Partition: all elements [1,2,3,4] are left of 5. Pivot goes to position 4 (last). Left partition = [1,2,3,4], right partition = [].
Recurse: pivot = 4. All [1,2,3] go left. Pivot at position 3.
Recurse: pivot = 3. All [1,2] go left. Pivot at position 2.
...
Total partitions: N. Each partition is O(N), O(N-1), O(N-2), ... Total work = O(N²). For N=10,000: 50 million operations. Slow!

WHAT HAPPENS WITH RANDOM PIVOT:
Pick random pivot from [1,2,3,4,5]. Say pivot = 3.
Left = [1,2], right = [4,5]. Two ~equal sub-problems of size 2 each.
Recursion depth ≈ log₂(5) ≈ 3. Total work ≈ N log N = 12. Fast!

THE INSIGHT:
Sorted input is the adversarial case for fixed-position pivots. A pivot that always picks the median would guarantee O(N log N), but finding the median is itself O(N). Random pivot selection achieves expected O(N log N) because on average, a random pivot splits the array roughly in half.

---

### 🧠 Mental Model / Analogy

> Quicksort is like playing the "higher/lower" number guessing game as a group activity. Everyone picks a random number. One person (pivot) stands up. Everyone with a lower number stands to the left, everyone with a higher number to the right. Repeat within each group. The groups get smaller and smaller until everyone is standing in order — no merging needed.

"Pivot person" → pivot element
"Stand left/right" → in-place partition step
"Repeat within each group" → recursive calls on sub-arrays
"Groups get smaller" → O(log N) recursion depth (on average)

Where this analogy breaks down: If the pivot person is always the tallest (worst case), one group has everyone and the other is empty — O(N) groups of decreasing size each = O(N²). The game only works efficiently when the pivot is roughly in the middle.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Quicksort picks a "splitter" value, arranges everything smaller on one side and larger on the other, then sorts each side independently. It keeps splitting until each piece has one element — already sorted.

**Level 2 — How to use it (junior developer):**
Implement with Lomuto partition: choose pivot (arr[high]), use variable `i` to track "last small element" boundary. Swap elements ≤ pivot into the left zone as you scan. After scan, place pivot at boundary. Recurse on left (lo to pivot-1) and right (pivot+1 to hi). Add randomisation: `swap(arr[lo + rand.nextInt(hi-lo+1)], arr[hi])` before partitioning to avoid O(N²) on sorted inputs.

**Level 3 — How it works (mid-level engineer):**
Java's `Arrays.sort` for primitives uses Dual-Pivot Quicksort (Vladimir Yaroslavskiy, 2009): choose two pivots (p1, p2 with p1 ≤ p2), partition into three zones: [< p1], [p1 to p2], [> p2]. This reduces unnecessary comparisons and achieves better cache performance by keeping pivots in registers. Introsort (introspective sort) is the production default in C++ (`std::sort`): Quicksort with a depth counter that falls back to Heapsort when recursion depth exceeds 2*log₂(N) — guarantees O(N log N) worst case while keeping Quicksort's average-case speed.

**Level 4 — Why it was designed this way (senior/staff):**
Quicksort (Tony Hoare, 1959, ALGOL) was designed primarily for in-place performance on sequential memory. Its cache efficiency advantage over mergesort grew as CPUs added larger L1/L2 caches — a property Hoare could not have anticipated in 1959. The worst-case O(N²) behaviour drove 20+ years of research into pivot selection mechanisms. The randomised version's O(N log N) expected time with near-certainty made it practical. Median-of-medians guarantees O(N log N) deterministic pivot selection in O(N), but with a constant factor so large (10x) that it is never used in practice — a classic example of theoretically optimal but practically inferior.

---

### ⚙️ How It Works (Mechanism)

**Lomuto Partition:**
```
┌────────────────────────────────────────────┐
│ Lomuto Partition [lo..hi]                  │
│                                            │
│  pivot = arr[hi]                           │
│  i = lo - 1  ← boundary of small zone     │
│                                            │
│  for j = lo to hi-1:                       │
│    if arr[j] <= pivot:                     │
│      i++                                   │
│      swap(arr[i], arr[j])                  │
│      ← arr[lo..i] all <= pivot now        │
│                                            │
│  swap(arr[i+1], arr[hi])  ← place pivot   │
│  return i+1               ← pivot index   │
└────────────────────────────────────────────┘
```

**Hoare Partition:**
```
┌────────────────────────────────────────────┐
│ Hoare Partition [lo..hi]                   │
│                                            │
│  pivot = arr[lo + (hi-lo)/2]               │
│  i = lo - 1                               │
│  j = hi + 1                               │
│                                            │
│  LOOP forever:                             │
│    do i++ while arr[i] < pivot            │
│    do j-- while arr[j] > pivot            │
│    if i >= j: return j (split point)       │
│    swap(arr[i], arr[j])                    │
└────────────────────────────────────────────┘
```

**Complexity analysis:**
- Best/average: O(N log N) comparisons, O(log N) stack depth
- Worst (sorted, fixed pivot): O(N²) comparisons, O(N) stack depth → StackOverflowError for N=100,000

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Unsorted array of N elements
→ randomise pivot selection
→ [QUICKSORT ← YOU ARE HERE]
  → Partition: place pivot in final position
  → Recurse on left sub-array (< pivot)
  → Recurse on right sub-array (> pivot)
  → Base case: size ≤ 1, return
→ Array is sorted in-place
→ O(N log N) average, O(log N) stack space
```

FAILURE PATH:
```
Sorted input + last-element pivot
→ Every partition: left=[N-1 elements], right=[]
→ Recursion depth = N
→ Stack frames = N
→ StackOverflowError for large N (N > 10,000)
→ Fix: randomise pivot or switch to Introsort
```

WHAT CHANGES AT SCALE:
For N=10⁸ elements (1 billion), random Quicksort's cache efficiency is crucial: mergesort accesses ~120 cache misses per element (L3 cache overflow); Quicksort accesses ~30 (better sequential access). At this scale, the factor-of-4 cache advantage translates to ~2 minutes vs ~8 minutes on real hardware. Parallel Quicksort partitions independently recursive sub-problems across cores — good parallel speedup until partition size < L1 cache, at which point sequential is faster.

---

### 💻 Code Example

**Example 1 — Standard Quicksort with randomised pivot:**
```java
void quicksort(int[] arr, int lo, int hi) {
    if (lo >= hi) return; // base case

    // Randomise pivot to avoid O(N²) worst case
    int pivotIdx = lo + rand.nextInt(hi-lo+1);
    swap(arr, pivotIdx, hi);

    int p = partition(arr, lo, hi);
    quicksort(arr, lo, p-1);
    quicksort(arr, p+1, hi);
}

// Lomuto partition
int partition(int[] arr, int lo, int hi) {
    int pivot = arr[hi];
    int i = lo - 1;
    for (int j = lo; j < hi; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(arr, i, j);
        }
    }
    swap(arr, i+1, hi);
    return i+1;
}

void swap(int[] arr, int i, int j) {
    int tmp = arr[i]; arr[i]=arr[j]; arr[j]=tmp;
}
```

**Example 2 — Introsort (practical production pattern):**
```java
void introsort(int[] arr, int lo, int hi,
               int depthLimit) {
    int size = hi - lo + 1;
    if (size < 16) {
        // Small arrays: insertion sort is faster
        insertionSort(arr, lo, hi);
        return;
    }
    if (depthLimit == 0) {
        // Fallback to heapsort: O(N log N) worst
        heapsort(arr, lo, hi);
        return;
    }
    // Normal quicksort
    int p = partition(arr, lo, hi);
    introsort(arr, lo, p-1, depthLimit-1);
    introsort(arr, p+1, hi, depthLimit-1);
}

void sort(int[] arr) {
    int n = arr.length;
    int depthLimit = 2 * (int)(Math.log(n)
        / Math.log(2));
    introsort(arr, 0, n-1, depthLimit);
}
```

**Example 3 — Quickselect (kth smallest element):**
```java
// Quickselect: O(N) average, O(N²) worst
// Select kth smallest element (0-indexed)
int quickselect(int[] arr, int lo, int hi,
                int k) {
    if (lo == hi) return arr[lo];

    int pivotIdx = lo + rand.nextInt(hi-lo+1);
    swap(arr, pivotIdx, hi);
    int p = partition(arr, lo, hi);

    if (k == p) return arr[p];
    else if (k < p)
        return quickselect(arr, lo, p-1, k);
    else
        return quickselect(arr, p+1, hi, k);
}
// Use: find median in O(N) average time
// int median = quickselect(arr, 0, n-1, n/2);
```

---

### ⚖️ Comparison Table

| Algorithm | Time (avg) | Time (worst) | Space | Stable | Cache Friendly | Best For |
|---|---|---|---|---|---|---|
| **Quicksort** | O(N log N) | O(N²) | O(log N) | No | Yes | Primitives, general in-memory |
| Mergesort | O(N log N) | O(N log N) | O(N) | Yes | Moderate | Objects (stable), external sort |
| Heapsort | O(N log N) | O(N log N) | O(1) | No | No | Memory-constrained, guaranteed worst |
| Timsort | O(N log N) | O(N log N) | O(N) | Yes | Yes | Mixed/partially-sorted data |
| Insertion Sort | O(N²) | O(N²) | O(1) | Yes | Yes | Small arrays (N < 20), nearly sorted |

How to choose: Use Quicksort (or native sort) for primitives. Use Mergesort/Timsort when stability is required. Use Heapsort when O(1) extra space is required and worst case must be O(N log N).

---

### 🔁 Flow / Lifecycle

```
┌──────────────────────────────────────────────┐
│ Quicksort Recursion Tree (balanced pivot)    │
│                                              │
│  [8 elements]                                │
│  partition → pivot at position 4             │
│  ├──[4 left]    ──[3 right]                  │
│  │  partition       partition                │
│  ├──[2][1]        ──[1][2]                   │
│  │  base case      base case                 │
│  Total levels: O(log N)                      │
│  Work per level: O(N)                        │
│  Total: O(N log N)                           │
│                                              │
│  Worst case (sorted, fixed pivot):           │
│  [8]→[0][7]→[0][6]→...→[0][1]              │
│  N levels, O(N) work each = O(N²)            │
└──────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Quicksort is always faster than Mergesort | Quicksort has better cache performance for random data; Mergesort is faster for nearly-sorted data (Timsort exploits existing runs) and provides guaranteed O(N log N) |
| Quicksort's worst case is extremely rare | Fixed-position pivots (first, last) produce O(N²) on sorted or reverse-sorted input — a common real-world scenario in databases that pre-sorts data |
| Quicksort is in-place and uses O(1) extra space | Quicksort is in-place for data but uses O(log N) stack space (recursion) — O(N) in worst case (unbalanced partitions). Not truly O(1) space |
| Randomised Quicksort guarantees O(N log N) | Randomised Quicksort has expected O(N log N) — it is possible (though astronomically unlikely) to get O(N²) with unlucky random choices. Introsort provides a hard O(N log N) guarantee |
| Java's Arrays.sort uses standard Quicksort | Java uses Dual-Pivot Quicksort (for primitives) and Timsort (for objects). Standard one-pivot Quicksort has not been used in Java since Java 7 |

---

### 🚨 Failure Modes & Diagnosis

**1. O(N²) performance on sorted/reverse-sorted input**

Symptom: Sort of 100,000 elements that should complete in <100ms takes 10+ seconds; profiler shows `quicksort` is the hotspot with O(N²) call count.

Root Cause: Pivot is always first or last element. Sorted input causes maximally unbalanced partitions.

Diagnostic:
```bash
# Time sort on sorted vs random input:
time java Sort sorted  # should be similar
time java Sort random  # to this
# If sorted >> random: pivot selection bug
```

Fix:
```java
// BAD: always picks last element
int pivot = arr[hi]; // O(N²) on sorted

// GOOD: randomised pivot
int pivotIdx = lo + rand.nextInt(hi-lo+1);
swap(arr, pivotIdx, hi);
```

Prevention: Always randomise pivot selection or use median-of-three.

---

**2. StackOverflowError on large sorted input**

Symptom: `java.lang.StackOverflowError` for arrays larger than ~10,000 with non-randomised pivot.

Root Cause: O(N²) case also causes O(N) recursion depth. JVM default stack holds ~1000 frames for typical Quicksort frames — overflows at N=1000.

Diagnostic:
```bash
java -Xss10m Sort # Increase stack temporarily
# Still slow? Root cause is pivot selection.
```

Fix: Switch to iterative Quicksort using an explicit stack, or add recursion depth check (Introsort pattern).

Prevention: Introsort prevents both O(N²) time AND O(N) stack depth — use it for production sorts.

---

**3. Quicksort used when stable sort needed**

Symptom: Records sorted by secondary key, then sorted by primary key — secondary order is not preserved within same primary key groups.

Root Cause: Quicksort is not stable — equal elements can swap positions during partition. Stability requires a stable algorithm (Mergesort, Timsort).

Diagnostic:
```java
// Check stability violation:
// Sort [{3,A},{1,B},{1,C}] by first field
// Stable result: {1,B},{1,C},{3,A} (B before C)
// Unstable result: {1,C},{1,B},{3,A} possible
```

Fix: Use `Arrays.sort(objectArray)` in Java (Timsort, stable) instead of custom Quicksort. For primitives, stability does not apply (no identity separate from value).

Prevention: Document stability requirements upfront. Default to stable sort unless performance profiling proves unstable sort is needed.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Recursion` — Quicksort's recursive structure is central to understanding its performance; understand recursion depth and stack frames.
- `Divide and Conquer` — Quicksort divides (partition) then conquers (recursively sort); the paradigm explains its O(N log N) average behaviour.
- `Arrays` — Quicksort operates in-place on arrays; understand random access and swap operations.

**Builds On This (learn these next):**
- `Dual-Pivot Quicksort` — Java's `Arrays.sort` optimisation using two pivots for better performance on random data.
- `Quickselect` — Quicksort's partitioning applied to find the kth smallest element in O(N) average time.
- `Introsort` — production Quicksort with Heapsort fallback; used in C++ `std::sort`.

**Alternatives / Comparisons:**
- `Mergesort` — stable, O(N log N) worst case, O(N) space; better for objects and external sorting.
- `Heapsort` — O(N log N) worst case, O(1) space, not stable; Quicksort beats it in cache performance.
- `Timsort` — stable, O(N log N) worst case, exploits existing sorted runs; Java's choice for objects.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Divide-and-conquer in-place sort using    │
│              │ pivot-based partitioning                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ In-memory sorting with best cache         │
│ SOLVES       │ performance among O(N log N) algorithms   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ After partition, pivot is in its FINAL    │
│              │ position — never moved again              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ In-place sort of primitives, cache-        │
│              │ performance critical, stability not needed │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Stability required (use Timsort);          │
│              │ guaranteed worst case needed (Heapsort)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N log N) avg / O(N²) worst vs Mergesort │
│              │ O(N log N) always / O(N) space            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pick a pivot, sort left and right —      │
│              │  pivot never moves after partition"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Mergesort → Timsort → Dual-Pivot Quicksort│
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Quicksort's average case O(N log N) performance relies on the pivot splitting the array roughly in half on average. Using random pivot selection, the probability that a random choice is in the "good" range (splits into at least 25% on each side) is exactly 50%. Using a recurrence relation T(N) = T(αN) + T((1-α)N) + O(N) for a split of α:(1-α), prove that any constant-fraction split (α ≥ 0.1) still gives O(N log N) time. What does this tell you about how imprecise the "in half" requirement actually is?

**Q2.** Dual-Pivot Quicksort (used by Java for primitive arrays) uses two pivots p1 ≤ p2, dividing the array into three partitions: [< p1], [p1 to p2], [> p2]. In the best case (p1 and p2 split the array into thirds), what is the recurrence and resulting time complexity? In the worst case (p1 = p2 = minimum element), what does the partition look like, and how does the dual-pivot version handle this degenerate case compared to single-pivot Quicksort?

