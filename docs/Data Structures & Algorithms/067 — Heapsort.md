---
layout: default
title: "Heapsort"
parent: "Data Structures & Algorithms"
nav_order: 67
permalink: /dsa/heapsort/
number: "0067"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Heap (Min/Max), Divide and Conquer, Arrays
used_by: Introsort (fallback), Priority Queues, k-largest element problems
related: Quicksort, Mergesort, Heap (Min/Max)
tags:
  - algorithm
  - advanced
  - deep-dive
  - datastructure
  - performance
---

# 067 — Heapsort

⚡ TL;DR — Heapsort sorts in-place using a max-heap — guaranteed O(N log N) in all cases and O(1) extra space, but poor cache performance makes it slower than Quicksort in practice.

| #067 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Heap (Min/Max), Divide and Conquer, Arrays | |
| **Used by:** | Introsort (fallback), Priority Queues, k-largest element problems | |
| **Related:** | Quicksort, Mergesort, Heap (Min/Max) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need a sorting algorithm with a hard O(N log N) worst-case guarantee AND O(1) extra space. Quicksort can degrade to O(N²) on adversarial inputs. Mergesort requires O(N) auxiliary space. For embedded systems or real-time software where both time budget and memory are constrained, neither is acceptable.

**THE BREAKING POINT:**
The combination of O(N log N) worst-case time with O(1) space appears impossible — the information-theoretic gap between simple O(N) space algorithms (mergesort) and fast O(1) space algorithms (quicksort, O(N²) worst) seems unbridgeable.

**THE INVENTION MOMENT:**
A heap is a partially-sorted array that supports extracting the maximum in O(log N). Build a max-heap in O(N) (Floyd's algorithm). Then repeatedly extract the maximum: swap it to the end (O(1)) and heapify down (O(log N)). After N extractions, the array is sorted — entirely in-place. Build O(N) + N × heapify O(log N) = O(N log N), O(1) extra space. This is exactly why **Heapsort** was created.

---

### 📘 Textbook Definition

**Heapsort** is a comparison-based sorting algorithm that first builds a max-heap from the input array, then repeatedly extracts the maximum element by swapping it to the end of the unsorted portion and restoring the heap property via `heapify` (sift-down). Time complexity: O(N log N) in all cases. Space complexity: O(1) (in-place). Heapsort is **not stable** — equal elements may be reordered. Phase 1 (build): O(N). Phase 2 (sort): O(N log N).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Build a max-heap, then repeatedly pull the max out and put it at the end — in-place, O(1) space, O(N log N) guaranteed.

**One analogy:**
> Imagine sorting a pile of numbered tiles. First, arrange them into a tournament bracket where each match winner beats its children (the heap). Then repeatedly pull out the overall winner, put them in the "sorted" pile at the back, and run a new tournament to find the next winner. The bracket (heap) is maintained in the same space as the "sorted" pile — no extra room needed.

**One insight:**
Heapsort's uniqueness is proven: it is the only classic comparison sort to achieve O(N log N) worst case AND O(1) extra space. However, this comes at a cache cost — heap operations (sift-down) jump to index `2i+1` and `2i+2` from parent `i`, causing scattered memory accesses that miss CPU cache frequently. This makes heap operations 2-5x slower than sequential array scans, despite same asymptotic complexity.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A **max-heap** satisfies: `arr[parent] >= arr[child]` for all parent-child pairs. The largest element is always at index 0.
2. **Heapify (sift-down)**: given a node that may violate the heap property, swap it with its largest child and recurse. O(log N) per call.
3. **Build-heap** (Floyd's algorithm): call heapify on all internal nodes from bottom-up. Counter-intuitively, this is O(N) — not O(N log N).

**DERIVED DESIGN:**
**Why build-heap is O(N) not O(N log N):**
Internal nodes at height h have O(N/2^h) count and O(h) heapify cost each. Total cost = Σ (N/2^h × h) for h=1 to log N = O(N) × Σ (h/2^h) = O(N) × 2 = O(N). The sum converges because deep nodes (high cost) are few and shallow nodes (many) have low cost.

**Phase 1 — Build max-heap in O(N):**
Start from the last internal node (index N/2-1) and call heapify on each, going toward index 0. This "bubbles down" any violations bottom-up.

**Phase 2 — Extract sort in O(N log N):**
For i from N-1 to 1:
1. Swap `arr[0]` (max) with `arr[i]` (end of heap).
2. Reduce heap size by 1 (the swapped element is now sorted).
3. Call `heapify(arr, 0, i)` to restore heap property on the remaining i elements.

**THE TRADE-OFFS:**
**Gain:** O(N log N) worst case guaranteed; O(1) extra space.
**Cost:** Not stable; worse cache performance than Quicksort (non-sequential memory access pattern during sift-down); rarely used as stand-alone sort in practice.

---

### 🧪 Thought Experiment

**SETUP:**
Array [4, 10, 3, 5, 1]. Sort using heapsort.

PHASE 1 — BUILD MAX-HEAP:
Start at index N/2-1 = 1 (node 10).
Heapify at 1: children are 5 (idx 3) and 1 (idx 4). 10 > both. No swap.
Heapify at 0: children are 10 (idx 1) and 3 (idx 2). 10 > 4. Swap arr[0]=10, arr[1]=4.
→ Heap: [10, 4, 3, 5, 1]. Wait, heapify down after swap: arr[1]=4, children are arr[3]=5, arr[4]=1. 5 > 4. Swap.
→ Heap: [10, 5, 3, 4, 1]. Max-heap property: 10≥{5,3}, 5≥{4,1}, 3≥{}\. Confirmed.

PHASE 2 — EXTRACT SORT:
i=4: swap arr[0]=10, arr[4]=1. Heap: [1,5,3,4], sorted: [...,10]
Heapify(0,4): 1 vs 5,3 → swap 1,5. [5,1,3,4]. 1 vs 4 → swap 1,4. [5,4,3,1].
i=3: swap arr[0]=5, arr[3]=1. Heap: [1,4,3], sorted: [...,5,10]
Heapify(0,3): 1 vs 4,3 → swap 1,4. [4,1,3].
i=2: swap arr[0]=4, arr[2]=3. Heap: [3,1], sorted: [...,4,5,10]
Heapify(0,2): 3 vs 1 → no swap.
i=1: swap arr[0]=3, arr[1]=1. Heap: [1], sorted: [1,3,4,5,10].
Done. Array = [1,3,4,5,10]. ✓

**THE INSIGHT:**
Each extraction of the maximum places it in its final position (from right to left). The heap structure ensures the next maximum is always at index 0. This is a perfect marriage of the heap's "fast maximum extraction" property with in-place sorting.

---

### 🧠 Mental Model / Analogy

> Heapsort is like a single-elimination tournament where you find the winner and permanently retire them. Build a bracket ensuring each player beats their children. Find the champion (top of heap). Retire them to the "hall of fame" (sorted end). Find the next champion from the remaining players by running a targeted mini-tournament (heapify). Repeat until everyone is in the hall of fame — all in the same trophy room (in-place).

- "Tournament bracket ensuring parent beats children" → max-heap property
- "Champion at top" → max element at arr[0]
- "Retire champion to hall of fame" → swap to sorted end
- "Mini-tournament to find next champion" → sift-down heapify (O(log N))

Where this analogy breaks down: Real tournaments have fixed brackets; changing participants after each round is unusual. Heapify's "sift-down" restructures the heap after each extraction — more like recalculating the bracket from the top for each new tournament.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Heapsort builds a special structure where the largest element is always on top. It repeatedly removes the top element (the largest), placing it at the end. It fixes the top by finding the next largest. Repeat until everything is in order — using no extra space.

**Level 2 — How to use it (junior developer):**
Implement `heapify(arr, n, i)`: given heap of size n, fix the sub-tree rooted at i (sift-down). Call `buildHeap(arr, n)` by calling heapify on `n/2-1` down to 0. Then the sort phase: for i from n-1 to 1, swap arr[0] and arr[i], call heapify(arr, i, 0). This extracts n-1 elements in sorted order.

**Level 3 — How it works (mid-level engineer):**
Floyd's build-heap algorithm is provably O(N) via amortised analysis: the sum of sift-down costs across all nodes ≤ 2N. During sort phase, each of N extractions costs O(log N) heapify. The non-sequential memory access pattern during sift-down (jumping to 2i+1 and 2i+2 positions) causes cache misses when heap size exceeds L1/L2 cache. For large arrays (N > 10,000), each sift-down operation may trigger multiple L3 cache misses compared to Quicksort's sequential scan — making Heapsort 2-5x slower in wall-clock time.

**Level 4 — Why it was designed this way (senior/staff):**
Heapsort (J. W. J. Williams, 1964) was the first sorting algorithm achieving both O(N log N) worst-case and O(1) space. Robert Floyd (1964) contributed the build-heap O(N) insight. Heapsort is theoretically near-optimal: the N log N lower bound applies to worst case, and Heapsort matches it. In practice, Heapsort is used as the fallback in Introsort (C++ `std::sort`): when Quicksort recursion depth exceeds 2×log₂(N), Introsort switches to Heapsort to guarantee O(N log N) worst case. This combines Quicksort's cache-friendly average performance with Heapsort's worst-case guarantee — using Heapsort as insurance, not the primary sort.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ Heapify (Sift-Down)                        │
│                                            │
│  heapify(arr, n, i):                       │
│    largest = i                             │
│    left = 2*i + 1                          │
│    right = 2*i + 2                         │
│    if left < n AND arr[left] > arr[largest]│
│      largest = left                        │
│    if right< n AND arr[right]>arr[largest] │
│      largest = right                       │
│    if largest != i:                        │
│      swap(arr[i], arr[largest])            │
│      heapify(arr, n, largest) ← recurse   │
└────────────────────────────────────────────┘
┌────────────────────────────────────────────┐
│ Heapsort Main                              │
│                                            │
│  Phase 1 - Build max-heap O(N):            │
│  for i = n/2-1 downto 0:                   │
│    heapify(arr, n, i)                      │
│                                            │
│  Phase 2 - Extract sort O(N log N):        │
│  for i = n-1 downto 1:                     │
│    swap(arr[0], arr[i])  ← extract max    │
│    heapify(arr, i, 0)    ← restore heap   │
└────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Unsorted array of N elements
→ Build max-heap O(N) [Floyd's algorithm]
→ [HEAPSORT EXTRACT PHASE ← YOU ARE HERE]
  → Swap max (arr[0]) to arr[N-1]
  → Heapify(0, N-1) → restore heap
  → Repeat with heap of size N-2, N-3, ...
→ Sorted array, in-place, O(N log N) guaranteed
```

**FAILURE PATH:**
```
Heapsort used for stable sort
→ Equal elements may swap during sift-down
→ Relative order not preserved
→ Multi-key sort corrupted
→ Use Timsort/Mergesort for stable sort
```

**WHAT CHANGES AT SCALE:**
For N=10⁷ elements, Heapsort's O(N log N) ≈ 230 million operations, but each sift-down on a heap larger than L2 cache (512KB, ~130K integers) causes cache misses. Each L3 miss costs ~100 cycles. At N=10⁷, each of the ~23 sift-down levels accesses a "random" position — 23 × cache misses × cycles/miss creates significant overhead. Quicksort's sequential scan hits cache much better. This is why Heapsort, despite theoretical equivalence, is measurably slower.

---

### 💻 Code Example

**Example 1 — Complete Heapsort:**
```java
void heapsort(int[] arr) {
    int n = arr.length;

    // Phase 1: Build max-heap (bottom-up)
    // Start from last internal node n/2-1
    for (int i = n/2 - 1; i >= 0; i--)
        heapify(arr, n, i);

    // Phase 2: Extract elements from heap one by one
    for (int i = n-1; i > 0; i--) {
        // Move current max to end
        int tmp = arr[0];
        arr[0] = arr[i];
        arr[i] = tmp;
        // Heapify the reduced heap
        heapify(arr, i, 0);
    }
}

void heapify(int[] arr, int n, int i) {
    int largest = i;
    int left = 2*i + 1;
    int right = 2*i + 2;

    if (left < n && arr[left] > arr[largest])
        largest = left;
    if (right < n && arr[right] > arr[largest])
        largest = right;

    if (largest != i) {
        int tmp = arr[i]; arr[i]=arr[largest];
        arr[largest]=tmp;
        heapify(arr, n, largest); // recurse
    }
}
```

**Example 2 — Find k largest elements in O(N + k log N):**
```java
int[] kLargest(int[] arr, int k) {
    int n = arr.length;
    int[] heap = arr.clone();

    // Build max-heap O(N)
    for (int i = n/2-1; i>=0; i--)
        heapify(heap, n, i);

    // Extract k maxima O(k log N)
    int[] result = new int[k];
    for (int i = 0; i < k; i++) {
        result[i] = heap[0]; // current max
        heap[0] = heap[n-1-i]; // last element up
        heapify(heap, n-1-i, 0); // re-heapify
    }
    return result;
}
```

**Example 3 — Introsort pattern (Quicksort + Heapsort fallback):**
```java
void introsort(int[] arr, int lo, int hi,
               int depthLimit) {
    if (hi - lo < 16) {
        insertionSort(arr, lo, hi);
        return;
    }
    if (depthLimit == 0) {
        // Quicksort is misbehaving: fallback
        heapsortRange(arr, lo, hi);
        return;
    }
    int pivot = partition(arr, lo, hi);
    introsort(arr, lo, pivot-1, depthLimit-1);
    introsort(arr, pivot+1, hi, depthLimit-1);
}

void sort(int[] arr) {
    // Max depth = 2 * log2(n)
    int maxDepth = 2 * (int)(
        Math.log(arr.length)/Math.log(2));
    introsort(arr, 0, arr.length-1, maxDepth);
}
```

---

### ⚖️ Comparison Table

| Algorithm | Time | Worst | Stable | Space | Cache | Best For |
|---|---|---|---|---|---|---|
| **Heapsort** | O(N log N) | O(N log N) | No | O(1) | Poor | Memory-constrained worst-case guarantee |
| Quicksort | O(N log N) | O(N²) | No | O(log N) | Excellent | In-memory, primitives, average case |
| Mergesort | O(N log N) | O(N log N) | Yes | O(N) | Good | Stable, objects, external sort |
| Timsort | O(N log N) | O(N log N) | Yes | O(N) | Good | Real-world, partially sorted |
| Introsort | O(N log N) | O(N log N) | No | O(log N) | Good | C++ `std::sort`, production |

How to choose: Use Heapsort only when O(1) space is required AND O(N log N) worst case is required (rare combination). Otherwise use Introsort (Quicksort + Heapsort fallback) for primitives or Timsort for objects.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Heapsort uses O(1) space including the heap | The heap IS the input array, rearranged in-place. No additional heap structure is allocated separately. Heapsort uses O(1) extra space beyond the input array |
| Heapsort is the fastest O(N log N) in-place sort | Quicksort is faster in practice despite same asymptotic complexity, due to better cache performance. Heapsort's scattered memory access pattern causes frequent cache misses |
| Build-heap is O(N log N) | Build-heap (Floyd's algorithm) is O(N), not O(N log N). This is a non-obvious result: most nodes are near the bottom and have small sift-down costs |
| Heapsort is widely used in practice | Heapsort is rarely used as the primary sort. It appears as the fallback in Introsort (C++ `std::sort`) and for k-largest element problems. Language libraries prefer Quicksort or Timsort |
| A min-heap is needed for ascending sort | Heapsort uses a MAX-heap for ascending sort. The max is placed at the end repeatedly, building the sorted array from right to left. Using a min-heap would sort in descending order |

---

### 🚨 Failure Modes & Diagnosis

**1. Off-by-one in build-heap starting index**

**Symptom:** Build-heap completes but array is not a valid max-heap; sort phase produces wrong results.

**Root Cause:** Starting heapify from the wrong index. Common errors: `n/2` (should be `n/2 - 1`), or `n-1` (starts too deep, includes leaf nodes).

**Diagnostic:**
```java
// Verify heap property after build:
boolean isMaxHeap(int[] arr, int n) {
    for (int i = 0; i <= n/2-1; i++) {
        int left = 2*i+1, right = 2*i+2;
        if (left < n && arr[i] < arr[left])
            return false;
        if (right < n && arr[i] < arr[right])
            return false;
    }
    return true;
}
assert isMaxHeap(arr, arr.length)
    : "Build-heap failed!";
```

**Fix:** Start build-heap from `n/2 - 1` (last non-leaf node in a 0-indexed array). Leaf nodes (indices n/2 to n-1) are already trivially valid heaps.

**Prevention:** Unit test build-heap with `isMaxHeap()` verification.

---

**2. Using heapsort when stable sort is required**

**Symptom:** Multi-key sort produces incorrect ordering for equal-valued elements.

**Root Cause:** Heapsort's sift-down may swap equal elements, violating stability.

**Diagnostic:** Same as Quicksort stability test — check that elements with equal keys maintain original relative order.

**Fix:** Use Timsort (`Arrays.sort(T[], comparator)`) for stable sorting.

**Prevention:** Explicitly choose algorithm based on stability requirements.

---

**3. Heapify called without reducing heap size correctly**

**Symptom:** Already-sorted elements at the end of the array are included in subsequent heapify operations, corrupting the sort.

**Root Cause:** In the sort phase, `heapify(arr, n, 0)` is called with `n` still equal to original array size, instead of reduced size `i`.

**Diagnostic:**
```java
// Check: after sort phase, is array sorted?
for (int i = 0; i < arr.length-1; i++) {
    assert arr[i] <= arr[i+1]
        : "Sort failed at index " + i;
}
```

**Fix:** Ensure heapify is called with the **current heap size** (`heapify(arr, i, 0)` in the loop where i decrements from n-1 to 1), not the original array length.

**Prevention:** The heap size must be the second argument to heapify, and it must decrease with each extraction.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Heap (Min/Max)` — Heapsort is built on the heap data structure; understand the heap property, sift-down, and parent-child index relationships.
- `Arrays` — Heapsort operates in-place on arrays using index arithmetic; understand 0-indexed arrays and in-place swaps.

**Builds On This (learn these next):**
- `Priority Queue` — priority queues are implemented using heaps; heapsort's logic is exactly what powers priority queue operations.
- `Introsort` — the production sort combining Quicksort and Heapsort; understand how Heapsort serves as the worst-case safety net.

**Alternatives / Comparisons:**
- `Quicksort` — faster in practice due to cache efficiency; O(N²) worst case; not stable.
- `Mergesort` — guaranteed O(N log N), stable, O(N) space; better cache than Heapsort.
- `Smooth Sort` — a variant of Heapsort using Leonardo heaps; better best-case performance (O(N) on nearly-sorted data); complex implementation.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ In-place sort using max-heap: build heap, │
│              │ repeatedly extract maximum                │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Need O(N log N) worst case AND O(1) space │
│ SOLVES       │ — both Quicksort and Mergesort fail one   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Build-heap is O(N) not O(N log N);        │
│              │ sift-down is the only operation needed    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Memory-constrained, O(N log N) hard       │
│              │ requirement, Introsort fallback           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Stable sort needed; or cache efficiency   │
│              │ critical (use Quicksort/Timsort instead)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N log N) always, O(1) space vs poor     │
│              │ cache performance, no stability           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Keep the max on top, extract to end,     │
│              │  no extra space ever"                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Priority Queue → Introsort → Smooth Sort  │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Floyd's build-heap algorithm builds a max-heap bottom-up in O(N) by calling heapify on internal nodes from index N/2-1 down to 0. The naive approach of heapifying N elements top-down (inserting one by one) runs in O(N log N). The key to Floyd's O(N) bound is that most nodes are near the leaves and have small sift-down distances. Prove formally that the total cost of Floyd's build-heap is O(N) by computing the exact sum Σ (N / 2^h) × h over all heights h from 1 to log N. Why does this sum converge to O(N) while top-down insertion does not?

**Q2.** Heapsort is not adaptive — it performs the same number of operations regardless of how sorted the input already is. Smooth Sort (Dijkstra, 1981) is an adaptive variant of Heapsort using Leonardo heaps that achieves O(N) on already-sorted input while maintaining O(N log N) worst case. Compare the structural difference between a standard binary max-heap and a Leonardo heap. What property of Leonardo numbers (`L(k) = L(k-1) + L(k-2) + 1`) makes them suitable for building an adaptive heap-based sort?

