---
layout: default
title: "In-Place vs Out-of-Place"
parent: "Data Structures & Algorithms"
nav_order: 89
permalink: /dsa/in-place-vs-out-of-place/
number: "0089"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Space Complexity, Array, Sorting Algorithms
used_by: Sorting Stability, Memory Management, Cache Performance
related: Space-Time Trade-off, Memory Management Models, Sorting Stability
tags:
  - algorithm
  - intermediate
  - datastructure
  - performance
  - pattern
---

# 089 — In-Place vs Out-of-Place

⚡ TL;DR — In-place algorithms transform data using O(1) extra memory by modifying the input directly; out-of-place algorithms allocate additional space to produce a clean output without touching the original.

| #0089 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Space Complexity, Array, Sorting Algorithms | |
| **Used by:** | Sorting Stability, Memory Management, Cache Performance | |
| **Related:** | Space-Time Trade-off, Memory Management Models, Sorting Stability | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to sort a 16 GB array on a machine with 16 GB RAM. An out-of-place MergeSort allocates another 16 GB for its merge buffer — total 32 GB needed; the system runs out of memory. Alternatively, on an embedded device with 256 KB RAM, any algorithm that allocates proportional extra memory simply cannot run.

**THE BREAKING POINT:**
Memory is finite. Proportional-space algorithms fail when input size approaches available memory. For large datasets in production (in-memory databases, batch sort jobs), the difference between O(1) and O(N) extra space determines whether the algorithm fits in RAM at all.

**THE INVENTION MOMENT:**
QuickSort and HeapSort are in-place sorters: they rearrange elements within the input array using only O(log N) or O(1) extra space (recursion stack / swap variables). This makes them runnable on arrays that fill memory to capacity. The trade-off: in-place often means unstable or more complex implementation. This is exactly why **In-Place vs Out-of-Place** is a fundamental algorithm design choice.

---

### 📘 Textbook Definition

An **in-place algorithm** transforms its input using at most O(1) auxiliary space (not counting the input itself) — or more loosely, O(log N) for algorithms requiring a recursion stack. Examples: QuickSort (O(log N) stack), HeapSort (O(1)), InsertionSort (O(1)), selection sort (O(1)), in-place reversal. An **out-of-place algorithm** allocates auxiliary memory proportional to input size O(N) to produce its output. Examples: MergeSort (O(N) merge buffer), counting sort (O(N) output array), BFS (O(V) visited array). The distinction matters for memory-constrained environments, cache efficiency, and whether the original data must be preserved.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
In-place modifies data where it lives; out-of-place makes a copy to work with.

**One analogy:**
> Rearranging furniture in a small studio apartment: in-place means shuffling items within the apartment by rotating them through temporary positions using only the hallway as temporary buffer. Out-of-place means renting a storage unit, moving everything out, setting up perfectly, then moving back. The storage unit (extra memory) allows more freedom but costs more.

**One insight:**
In-place doesn't mean "no extra space ever" — it means O(1) or O(log N) extra. QuickSort's recursion stack is O(log N) extra space but is considered "in-place" algorithmically. The key question is whether extra space scales with input size (O(N) → out-of-place) or is bounded by a constant or logarithm (in-place).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An in-place algorithm achieves its transformation via reordering elements within the original array, using constant or logarithmic auxiliary space.
2. Every swap is a three-operation sequence: `tmp=a; a=b; b=tmp` — three register operations, O(1) extra.
3. Recursion counts: O(d) stack frames where d = recursion depth. For QuickSort: O(log N) expected stack depth → considered in-place. For MergeSort: O(log N) stack + O(N) merge buffer → out-of-place due to merge buffer.

**DERIVED DESIGN:**
**HeapSort in-place proof:** Heapify builds a max-heap in the original array (O(N)). Extract max: swap root with last element, shrink heap by 1, sift down. Each extraction is in-place — only swaps within the original array. Total extra memory: `tmp` variable for swap = O(1).

**In-place MergeSort complexity:** Exists but extremely complex. Algorithms like Kronrod's in-place merge achieve O(1) extra space but at O(N log² N) time due to internal data movements. Not used in practice.

**THE TRADE-OFFS:**
In-place gain: minimises memory footprint; better cache performance (data stays in same memory location).
In-place cost: often cannot be stable (QuickSort unstable); more complex implementation; may have higher constant factors.
Out-of-place gain: simpler implementation; stability preservation (MergeSort); original data preserved.
Out-of-place cost: O(N) extra memory; potential cache miss increase (two arrays instead of one).

---

### 🧪 Thought Experiment

**SETUP:**
Sort a 4 GB array on a machine with exactly 4 GB RAM available for the array (plus OS, JVM overhead).

**WHAT HAPPENS WITH OUT-OF-PLACE MERGESORT:**
MergeSort allocates a 4 GB merge buffer: total memory = 8 GB. `OutOfMemoryError`. Sort fails entirely. The machine cannot even start the sort.

**WHAT HAPPENS WITH IN-PLACE QUICKSORT:**
QuickSort uses only the `tmp` variable in swap + O(log N) stack frames ≈ O(log N × frame_size). For N=4GB / 8 bytes = 500M elements, stack depth ~30 frames × 64 bytes/frame = ~2 KB. Total extra: ~2 KB. Sort succeeds. Input array fits exactly in available RAM.

**THE INSIGHT:**
The in-place algorithm scales to any array that fits in memory; the out-of-place algorithm can only sort arrays that fit in half the available memory. For large data, in-place is not a convenience — it's a prerequisite.

---

### 🧠 Mental Model / Analogy

> In-place is like solving a sliding puzzle (15-puzzle): you rearrange tiles using only the empty square as a buffer. Out-of-place is like picking up all tiles, sorting them, then placing them back. The sliding puzzle approach uses only the empty square (O(1) extra) but requires specific sequences of moves. Picking all tiles up requires space to hold them all (O(N) extra) but allows arbitrary placement.

- "Sliding puzzle (empty square)" → in-place algorithm (O(1) buffer)
- "Picking up all tiles" → out-of-place (O(N) extra space)
- "Specific swap sequences" → in-place algorithms' algorithmic constraints
- "Arbitrary placement" → out-of-place's flexibility (e.g., can be stable)

Where this analogy breaks down: Not all puzzles have O(1) solutions in the sliding puzzle sense — in-place stable MergeSort is extremely complex. The analogy makes in-place look simpler when it's often more complex to implement correctly.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
In-place means the algorithm works within the original data without needing a separate copy. Like rearranging books on a shelf: you move books around the shelf itself rather than taking them all to a table and rearranging there. Less space, but you must always keep the shelf usable.

**Level 2 — How to use it (junior developer):**
Choose in-place when: memory is tight, input array size approaches available RAM, or cache efficiency is critical. Choose out-of-place when: stability is required (use stable MergeSort), original data must be preserved, or simplicity of implementation is priority. Java: `Arrays.sort(int[])` = in-place QuickSort; `Arrays.sort(Object[])` = out-of-place TimSort. Python: `list.sort()` = in-place TimSort (though TimSort uses O(N) internally, Python modifies in-place from caller's perspective).

**Level 3 — How it works (mid-level engineer):**
**Cache implications:** In-place algorithms access the same memory locations; data stays in CPU cache (high spatial locality). Out-of-place algorithms write to a separate buffer at different addresses; this may cause cache misses on the write side. For arrays that fit in L2 cache (< 256KB): the cache effect is minimal. For arrays that don't fit in cache: in-place has better cache utilisation because it doesn't need to load the buffer addresses. QuickSort practically outperforms MergeSort on modern hardware partly because it avoids the cache pollution from the merge buffer.

**Level 4 — Why it was designed this way (senior/staff):**
The in-place/out-of-place distinction intersects with the external sort problem: when the dataset doesn't fit in RAM at all, external sort uses out-of-place merging with disk-based buffers. External MergeSort reads chunks into RAM, sorts in-place in RAM, writes sorted runs to disk, then merges runs from disk — a hybrid. The merge step is inherently out-of-place (must write to a different file/disk block). Database external sort explicitly schedules I/O to minimise disk seeks — the algorithm is designed around the memory hierarchy, not just main memory. In-memory databases (Redis, VoltDB) must keep all data in RAM: they must use in-place algorithms or carefully manage O(N) buffers to avoid OOM.

---

### ⚙️ How It Works (Mechanism)

**HeapSort in-place (O(1) extra space):**

```
┌────────────────────────────────────────────────┐
│ HeapSort: in-place on array [4,10,3,5,1]       │
│                                                │
│ Step 1: Heapify → [10,5,3,4,1]                 │
│   All operations: swap elements within array   │
│   Extra space: O(1) (swap tmp variable)        │
│                                                │
│ Step 2: Extract max 10 → swap with last        │
│   [10,5,3,4,1] → Swap arr[0] with arr[4]       │
│   Array: [1,5,3,4|10]  ← heap|sorted           │
│   Sift down 1: [5,4,3,1|10]                    │
│                                                │
│ Continue until sorted [1,3,4,5,10]             │
│ Total extra space: 1 integer (tmp) = O(1)      │
└────────────────────────────────────────────────┘
```

**MergeSort out-of-place (O(N) extra space):**

```
┌────────────────────────────────────────────────┐
│ MergeSort: out-of-place merge step             │
│                                                │
│ Merge left=[1,4,5] and right=[2,3,6]           │
│                                                │
│ Allocate result buffer: [_,_,_,_,_,_] (O(N))  │
│                                                │
│ Compare: 1<2 → copy 1 to result[0]             │
│ Compare: 4>2 → copy 2 to result[1]             │
│ Compare: 4>3 → copy 3 to result[2]             │
│ ...                                            │
│ Result: [1,2,3,4,5,6]                          │
│ Copy back to original array.                   │
│                                                │
│ Extra: result buffer size = O(N)               │
└────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Array of N elements, M bytes available RAM
→ Compute required memory:
  In-place sort: ~O(N × element_size) + O(log N) stack
  Out-of-place sort: ~O(2N × element_size) + O(log N)
→ [IN-PLACE vs OUT-OF-PLACE ← YOU ARE HERE]
  → M > 2N×size: either algorithm fits; choose by stability/speed
  → N×size < M < 2N×size: must use in-place (OOM for out-of-place)
  → M < N×size: external sort required (disk-based)
→ Algorithm selection → sort
```

**FAILURE PATH:**
```
Out-of-place algorithm on memory-constrained system
→ OOM during merge buffer allocation
→ Application crash or GC pressure / STW pause
→ Diagnostic: java.lang.OutOfMemoryError: Java heap space
  → heap dump: check for large temporary arrays
→ Fix: switch to in-place algorithm or offload to disk
```

**WHAT CHANGES AT SCALE:**
For 1 billion records (8 bytes each = 8 GB), MergeSort needs 16 GB — impractical on an 8 GB machine. External sort: read 100M-record chunks (800 MB), sort each in-place with QuickSort (fits in RAM), write 10 sorted runs to disk, merge 10 runs with minimal in-memory buffers. Each merge step reads/writes disk once: O(N log₁₀(N/100M)) = O(N) disk I/O. The in-place step enables the external sort to work.

---

### 💻 Code Example

**Example 1 — In-place array reversal (O(1) space):**
```java
// In-place: modifies input, O(1) extra space
void reverseInPlace(int[] arr) {
    int left = 0, right = arr.length - 1;
    while (left < right) {
        int tmp = arr[left]; // O(1) tmp variable
        arr[left] = arr[right];
        arr[right] = tmp;
        left++; right--;
    }
}
// HeapSort: in-place O(N log N) sort
Arrays.sort(arr); // Java uses DualPivotQuickSort for int[] — in-place
```

**Example 2 — Out-of-place copy for preservation:**
```java
// Out-of-place: original preserved, O(N) space
int[] sortedCopy(int[] original) {
    int[] copy = original.clone(); // O(N) allocation
    Arrays.sort(copy);             // sort the copy
    return copy;                   // original untouched ✓
}
// Use when original must be preserved for later use
```

**Example 3 — In-place partition (QuickSort step):**
```java
int partition(int[] arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            // In-place swap: O(1) extra
            int tmp = arr[++i]; arr[i] = arr[j]; arr[j] = tmp;
        }
    }
    int tmp = arr[i+1]; arr[i+1] = arr[high]; arr[high] = tmp;
    return i + 1;
    // No auxiliary array allocated: in-place ✓
}
```

**Example 4 — Memory calculation for algorithm selection:**
```java
long chooseSortAlgorithm(long elementCount,
                          long elementBytes,
                          long availableRamBytes) {
    long inPlaceRam = elementCount * elementBytes
        + 64 * 30; // ~64 bytes/frame × 30 recursion depth
    long outOfPlaceRam = 2 * elementCount * elementBytes
        + 64 * 30;

    if (availableRamBytes >= outOfPlaceRam) {
        System.out.println("TimSort (stable, out-of-place)");
    } else if (availableRamBytes >= inPlaceRam) {
        System.out.println("QuickSort (in-place, unstable)");
    } else {
        System.out.println("External sort required");
    }
    return outOfPlaceRam;
}
```

---

### ⚖️ Comparison Table

| Algorithm | In-Place | Extra Space | Stable | Time | Best For |
|---|---|---|---|---|---|
| **QuickSort** | Yes | O(log N) stack | No | O(N log N) avg | Large arrays, memory-tight |
| **HeapSort** | Yes | O(1) | No | O(N log N) | Guaranteed O(N log N), O(1) space |
| **InsertionSort** | Yes | O(1) | Yes | O(N²) | Small arrays, nearly sorted |
| **MergeSort** | No | O(N) | Yes | O(N log N) | Stability required |
| **TimSort** | No* | O(N)* | Yes | O(N log N) | Default: objects in Java/Python |
| **CountingSort** | No | O(K) | Yes | O(N+K) | Integer keys, small range |

*TimSort modifies input in-place from caller's perspective but uses O(N) internal temporary storage.

How to choose: Use QuickSort/HeapSort for memory-constrained single-key sorts. Use MergeSort/TimSort when stability required. Use counting/radix sort for integer-key problems with bounded range.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| In-place means no extra memory at all | In-place allows O(1) or O(log N) extra. QuickSort's O(log N) recursion stack is considered in-place. HeapSort's O(1) swap variable is in-place. |
| Python list.sort() is out-of-place | Python's `list.sort()` modifies the list in-place from the user's perspective. Internally, TimSort uses O(N) temp array — this is the algorithm's auxiliary space, but the user's list is modified directly. |
| Out-of-place algorithms are always slower | For large arrays that don't fit in CPU cache, MergeSort's sequential access pattern can be faster than QuickSort's random access pattern despite the extra allocation overhead. Cache effects dominate at large N. |
| HeapSort should replace QuickSort (it's in-place AND O(N log N)!) | HeapSort has much worse cache performance: heap operations access distant array locations (parent-child relationships in heap), causing cache misses. QuickSort accesses sequential cache-friendly memory. In practice, HeapSort is 2-5× slower than QuickSort. |

---

### 🚨 Failure Modes & Diagnosis

**1. Out-of-place algorithm causes OOM on large input**

**Symptom:** `java.lang.OutOfMemoryError: Java heap space` during sort of large dataset.

**Root Cause:** Sort algorithm allocates O(N) extra array. For N=10^8 longs (800 MB input), sort allocates another 800 MB: total 1.6 GB, exceeds JVM heap.

**Diagnostic:**
```bash
# Check heap usage at sort start:
jstat -gc <pid> 1000
# If HeapUsed spikes by ~InputSize during sort: out-of-place algorithm
# Fix: run with larger heap or switch to in-place
java -Xmx4g MyApp  # temporary fix
# Permanent: replace MergeSort with Arrays.sort(int[]) (QuickSort)
```

**Fix:** For primitive arrays, use `Arrays.sort(int[])` (in-place). For objects requiring stability, increase heap or use external sort.

**Prevention:** Estimate memory per algorithm type before choosing; add a memory check before large operations.

---

**2. In-place algorithm corrupts original data needed later**

**Symptom:** Algorithm produces correct output, but original array is needed for later operation and is now sorted/modified.

**Root Cause:** In-place algorithm modified the input array. The caller expected it to be unchanged.

**Diagnostic:**
```java
// Before sort: arr = [3,1,4,1,5]
sort(arr); // in-place!
// After sort: arr = [1,1,3,4,5] — original order lost!
processOriginalOrder(arr); // BUG: order modified
```

**Fix:** Clone array before passing to in-place algorithm: `int[] toSort = arr.clone();`.

**Prevention:** API contract: document whether method modifies input. Immutable inputs: pass a copy. Java's `Arrays.sort` contract: sorts the array in-place.

---

**3. QuickSort recursion stack overflow for large sorted input**

**Symptom:** `StackOverflowError` when sorting already-sorted array of 100,000 elements with naive QuickSort.

**Root Cause:** Pivot always chosen as first element on sorted array; partition is O(N) deep. Stack depth = N = 100,000 frames × 64 bytes = ~6 MB usually exceeds default JVM stack (~512 KB).

**Diagnostic:**
```bash
# Check stack depth:
jstack <pid> | grep "quickSort" | wc -l
# If count ≈ N: degenerate recursion
```

**Fix:** Use randomised pivot (`ThreadLocalRandom`); or tail recursion optimisation (always recurse on smaller partition first, iterate on larger). Or use `Arrays.sort()` which uses dual-pivot QuickSort with insertion sort fallback.

**Prevention:** Never use first-element pivot without randomisation; `Arrays.sort(int[])` handles this correctly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Space Complexity` — In-place/out-of-place is a space complexity distinction; O(1) vs O(N) extra space.
- `Array` — Both algorithm types operate on arrays; understanding memory layout explains cache effects.
- `Sorting Algorithms` — In-place vs out-of-place is a fundamental property of sorting algorithms; QuickSort vs MergeSort exemplify the trade-off.

**Builds On This (learn these next):**
- `Sorting Stability` — In-place sorts (QuickSort, HeapSort) tend to be unstable; out-of-place sorts (MergeSort) tend to be stable — the two properties are interconnected.
- `Cache Performance` — In-place algorithms have better cache performance for small arrays; understanding cache lines explains why.
- `Memory Management Models` — In-place algorithms minimise GC pressure in garbage-collected languages by avoiding extra allocations.

**Alternatives / Comparisons:**
- `Space-Time Trade-off` — Out-of-place trading space for implementation simplicity/stability; in-place trading space savings for complexity.
- `External Sort` — When neither in-place nor out-of-place fits fully in RAM; extends out-of-place merging to disk.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ In-place: O(1/log N) extra space transforms│
│              │ input directly; out-of-place: O(N) buffer  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Large arrays fill RAM; out-of-place needs  │
│ SOLVES       │ 2× RAM; in-place fits in available memory  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ In-place allows sorting arrays that fill   │
│              │ available RAM; out-of-place needs 2× RAM  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ In-place: memory-constrained; large arrays;│
│              │ Out-of-place: stability required; preserve │
│              │ original; implementation simplicity        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ In-place HeapSort: cache-unfriendly for   │
│              │ large arrays; Out-of-place: near-RAM-limit │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ In-place: O(1) extra vs often unstable;   │
│              │ Out-of-place: O(N) extra + stability      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Sort in the room or rent a garage"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sorting Stability → External Sort → Cache  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In-place MergeSort (Kronrod 1969) achieves O(N log² N) time and O(1) extra space — but at the cost of a significantly more complex implementation. The standard out-of-place MergeSort is O(N log N) with O(N) space. For sorting 1 billion integers on a 4 GB machine (array = 4 GB), what is the practical trade-off: use in-place MergeSort (stable, O(1) space, O(N log² N) = 30-billion ops) vs external MergeSort (reads/writes 4 GB to disk multiple times, O(N log N) comparisons but with disk I/O cost)? Which is faster in wall-clock time on modern hardware and why?

**Q2.** Python's `list.sort()` uses TimSort which is documented as "in-place" but internally uses O(N) temporary storage. Java's `Arrays.sort(Object[])` is the same. From the API user's perspective, both are "in-place" — the input list/array is sorted. From the memory allocator's perspective, both allocate O(N). Explain: why do language designers claim TimSort is "in-place" despite its O(N) internal buffers? What would a TRUE in-place TimSort require algorithmically, and why would it have worse worst-case performance than the current O(N) buffer variant despite using less memory?

