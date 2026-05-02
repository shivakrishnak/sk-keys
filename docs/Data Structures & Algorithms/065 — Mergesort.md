---
layout: default
title: "Mergesort"
parent: "Data Structures & Algorithms"
nav_order: 65
permalink: /dsa/mergesort/
number: "0065"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Recursion, Divide and Conquer, Arrays
used_by: Timsort, External Sort, Parallel Sort
related: Quicksort, Timsort, Heapsort
tags:
  - algorithm
  - intermediate
  - pattern
  - performance
  - datastructure
---

# 065 — Mergesort

⚡ TL;DR — Mergesort divides an array in half, recursively sorts each half, then merges them — guaranteeing O(N log N) in all cases and stable ordering, at the cost of O(N) extra space.

| #065 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Recursion, Divide and Conquer, Arrays | |
| **Used by:** | Timsort, External Sort, Parallel Sort | |
| **Related:** | Quicksort, Timsort, Heapsort | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to sort 1 million Employee objects by salary. Quicksort achieves O(N log N) on average but is **not stable** — two employees with equal salaries might swap positions. If you previously sorted by last name, a Quicksort on salary will scramble employees with identical salaries into arbitrary order. Also, Quicksort can degrade to O(N²) on adversarial input.

**THE BREAKING POINT:**
For sorting objects (not just primitives), two requirements often conflict: stability (preserve relative order of equal elements) and guaranteed O(N log N) performance. Quicksort provides neither guarantee. You need a sort that is both stable and worst-case O(N log N).

**THE INVENTION MOMENT:**
Divide the array in half. Sort each half independently. Merge the two sorted halves by comparing front-to-front and always choosing the smaller element — if equal, choose the left half's element (preserving order = stability). This merge step is O(N) — two sorted arrays can be merged without any backtracking. The recursion produces O(log N) levels, each doing O(N) work in total. This is exactly why **Mergesort** was created.

---

### 📘 Textbook Definition

**Mergesort** is a divide-and-conquer sorting algorithm that recursively divides arrays into halves until trivially sorted (size ≤ 1), then merges them back using a two-pointer merge operation. Time complexity: O(N log N) in all cases (best, average, worst). Space complexity: O(N) auxiliary. Mergesort is **stable** — equal elements retain their original relative order. It is optimal for fully general comparison-based sorting: no comparison sort can beat O(N log N) in worst case.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Split into halves, sort each half, then merge them — works perfectly every time because merging two sorted arrays is trivial.

**One analogy:**
> Imagine sorting a shuffled stack of numbered cards. Split the deck in half. Hand each half to a friend to sort. When both friends return sorted piles, merge them: always take the smaller top card from either pile. Two sorted piles merge into one sorted pile in O(N) steps.

**One insight:**
Mergesort's strength is its predictability — O(N log N) regardless of input, no adversarial cases, stable. Its weakness is the O(N) extra space for the merge buffer. This space cost is why production systems use Timsort (mergesort variant) for objects, which reuses existing sorted runs to reduce auxiliary memory usage.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Mergesort's correctness relies on one fact: **two sorted arrays can be merged into one sorted array in O(N) time** using two pointers.
2. The recursion terminates because sub-arrays strictly shrink. An array of size 1 is trivially sorted.
3. The merge step is **stable** if left-half elements are chosen before right-half when equal.

**DERIVED DESIGN:**
The merge operation is the core insight. Given two sorted arrays L and R, maintain pointers `i` (into L) and `j` (into R). Compare L[i] and R[j]; write the smaller. For stability: if equal, write L[i] (left has priority). Advance the pointer of the written element. When one array is exhausted, copy the remaining elements of the other.

**Why O(N log N) is a lower bound for comparison sort:**
Any comparison sort must distinguish N! possible input orderings. Information-theoretically, this requires at least log₂(N!) comparisons = Θ(N log N) by Stirling's approximation. Mergesort achieves exactly this lower bound — it is asymptotically optimal.

**Why Quicksort beats Mergesort in practice despite same big-O:**
Mergesort writes to an auxiliary buffer then back — two passes per merge. Quicksort's in-place partition does one pass. For random data, Quicksort's cache-sequential access pattern gives 2-4x speedup despite the same asymptotic complexity. Mergesort wins when: stability required, adversarial inputs possible, or sorting linked lists (mergesort is O(1) space for linked lists — no random access needed; Quicksort on linked lists is O(N) space).

**THE TRADE-OFFS:**
**Gain:** O(N log N) guaranteed (no adversarial cases); stable; parallelisable; ideal for linked lists and external sort.
**Cost:** O(N) auxiliary space; worse cache performance than Quicksort for in-memory random data.

---

### 🧪 Thought Experiment

**SETUP:**
Array: [5, 2, 4, 6, 1, 3]. Walk through mergesort.

SPLIT PHASE:
Level 0: [5,2,4,6,1,3]
Level 1: [5,2,4] | [6,1,3]
Level 2: [5,2] [4] | [6,1] [3]
Level 3: [5] [2] [4] | [6] [1] [3]  ← all size-1

MERGE PHASE (bottom-up):
Merge [5]+[2]=[2,5]. Merge [4]==[4].
Merge [2,5]+[4]=[2,4,5] ← stable merge.
Merge [6]+[1]=[1,6]. Merge [3]=[3].
Merge [1,6]+[3]=[1,3,6].
Merge [2,4,5]+[1,3,6]=[1,2,3,4,5,6]. Done.

**THE INSIGHT:**
Each merge level does O(N) total work across all merge operations at that level (all sub-arrays together span the full array). With O(log N) levels, total work is O(N log N) — and this is the same regardless of the initial order of elements. Mergesort's tree is always perfectly balanced — unlike Quicksort where adversarial inputs can create a degenerate tree.

---

### 🧠 Mental Model / Analogy

> Mergesort is like a library reorganisation project. You sort all books by category, then by author within each category, then by title within each author — each step works with already-organised smaller groups and just merges them. The merge operation is clean: always take whichever book comes next alphabetically from either pile. You never have to re-examine a book you've already filed.

- "Sort smaller groups first" → recursive sort of halves
- "Always take alphabetically-next book" → two-pointer merge comparison
- "Already-filed books never re-examined" → O(N) merge (no backtracking)
- "Final merge = fully sorted" → merging two sorted halves produces sorted whole

Where this analogy breaks down: A real library reorganisation would reorder books in-place (no extra shelf space). Mergesort requires an auxiliary array for the merge buffer — the equivalent of a temporary staging shelf, which real libraries often don't have.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Mergesort sorts by splitting into two halves, sorting each half (recursively), then merging the sorted halves. Merging two sorted lists is easy: compare the fronts and always take the smaller one. Repeat this "split → sort → merge" process until the whole array is sorted.

**Level 2 — How to use it (junior developer):**
`mergesort(arr, 0, n-1)`. Base case: if `lo == hi`, return. Split at `mid = (lo+hi)/2`. Recursively sort `[lo..mid]` and `[mid+1..hi]`. Then call `merge(arr, lo, mid, hi)` which uses an auxiliary array `temp[]` to merge the two sorted halves back into `arr[lo..hi]`. Stability: in the merge step, when `arr[i] == arr[j]`, always write `arr[i]` first (left sub-array priority).

**Level 3 — How it works (mid-level engineer):**
Bottom-up mergesort avoids recursion entirely: start with sub-arrays of size 1 (all trivially sorted), merge them into size-2, then size-4, then size-8, until the whole array is sorted. This is cache-friendlier than top-down and avoids function call overhead. Timsort uses bottom-up mergesort with size-doubling and exploits existing sorted runs (natural mergesort). For linked lists, mergesort is O(1) extra space: merge is done by relinking nodes, not by copying to an auxiliary array — making mergesort the optimal linked-list sort.

**Level 4 — Why it was designed this way (senior/staff):**
John von Neumann invented mergesort in 1945 — predating computers. It was the foundational algorithm for early computing because it maps perfectly to sequential tape storage: two tapes can be merged into a sorted output tape without random access. This "external sort" application remains relevant today for big-data sorting (Hadoop's map phase produces sorted partitions that are then merge-sorted in the reduce phase). The information-theoretic lower bound proof (O(N log N) is optimal for comparison sort) was developed partly in response to trying to prove mergesort could be improved — leading to the fundamental negative result.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ Mergesort Top-Down Recursion               │
│                                            │
│  mergesort(arr, lo, hi):                   │
│    if lo >= hi: return (base case)         │
│    mid = lo + (hi - lo) / 2               │
│    mergesort(arr, lo, mid)   ← left half   │
│    mergesort(arr, mid+1, hi) ← right half  │
│    merge(arr, lo, mid, hi)   ← combine     │
│                                            │
│  merge(arr, lo, mid, hi):                  │
│    copy arr[lo..hi] to temp[]             │
│    i = lo, j = mid+1, k = lo              │
│    while i<=mid AND j<=hi:                 │
│      if temp[i] <= temp[j]:               │
│        arr[k++] = temp[i++] ← left first │
│      else:                                │
│        arr[k++] = temp[j++]              │
│    copy remaining elements               │
└────────────────────────────────────────────┘
```

**Bottom-up mergesort (no recursion):**
```java
void mergesortBottomUp(int[] arr) {
    int n = arr.length;
    int[] temp = new int[n];
    for (int size = 1; size < n; size *= 2) {
        for (int lo = 0; lo < n-size; lo+=2*size){
            int mid = lo + size - 1;
            int hi = Math.min(lo+2*size-1, n-1);
            merge(arr, temp, lo, mid, hi);
        }
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Unsorted array of N elements
→ [MERGESORT ← YOU ARE HERE]
  → Recursively split to size-1 arrays
  → Merge bottom-up: 1→2→4→8→...→N
  → Each merge: two sorted halves → one
→ Fully sorted array
→ O(N log N) time, O(N) space, stable
```

**FAILURE PATH:**
```
Very large N with constrained memory
→ Auxiliary array of N elements = N×4 bytes
→ For N=10⁸: 400 MB auxiliary memory
→ System OOM or swap thrashing
→ Fix: use in-place mergesort (complex,
  degrades to O(N log²N)) or external sort
  with streaming merge from disk
```

**WHAT CHANGES AT SCALE:**
Mergesort is the basis for **external sorting** — data too large for RAM. Write sorted chunks to disk (run generation phase), then K-way merge the sorted chunks. Apache Spark's sort shuffle uses distributed mergesort: each task sorts its partition, and the shuffle merge combines sorted partitions across machines. For N=1 TB of data on 100 machines, each machine processes 10 GB, sorts it (mergesort), and the sorted outputs are merged using a priority queue.

---

### 💻 Code Example

**Example 1 — Standard top-down mergesort:**
```java
int[] temp; // allocate once outside recursion

void mergesort(int[] arr, int lo, int hi) {
    if (lo >= hi) return;
    int mid = lo + (hi - lo) / 2;
    mergesort(arr, lo, mid);
    mergesort(arr, mid+1, hi);
    merge(arr, lo, mid, hi);
}

void merge(int[] arr, int lo, int mid, int hi) {
    // Copy to temp (pre-allocated to arr.length)
    for (int k = lo; k <= hi; k++)
        temp[k] = arr[k];

    int i = lo, j = mid+1;
    for (int k = lo; k <= hi; k++) {
        if (i > mid)
            arr[k] = temp[j++];   // left exhausted
        else if (j > hi)
            arr[k] = temp[i++];   // right exhausted
        else if (temp[i] <= temp[j])
            arr[k] = temp[i++];   // left first: STABLE
        else
            arr[k] = temp[j++];
    }
}

void sort(int[] arr) {
    temp = new int[arr.length]; // one allocation
    mergesort(arr, 0, arr.length-1);
}
```

**Example 2 — Mergesort for counting inversions:**
```java
// Inversion: (i,j) where i<j but arr[i]>arr[j]
// Mergesort can count inversions in O(N log N)
long inversions = 0;

void mergeCounting(int[] arr,
    int lo, int mid, int hi) {
    // ...copy to temp...
    int i = lo, j = mid+1;
    for (int k = lo; k <= hi; k++) {
        if (i > mid)
            arr[k] = temp[j++];
        else if (j > hi)
            arr[k] = temp[i++];
        else if (temp[i] <= temp[j])
            arr[k] = temp[i++];
        else {
            // temp[j] < temp[i]: all elements
            // temp[i..mid] are > temp[j]
            inversions += (mid - i + 1);
            arr[k] = temp[j++];
        }
    }
}
```

**Example 3 — External K-way merge (streaming):**
```java
// Merge K sorted input streams into one output
// Uses min-heap of size K: O(N log K) total
int[] externalKWayMerge(
    List<Iterator<Integer>> sortedStreams) {
    // PQ entry: [value, stream_index]
    PriorityQueue<int[]> pq =
        new PriorityQueue<>(
            Comparator.comparingInt(a -> a[0]));

    // Initialize: one element per stream
    for (int i=0; i<sortedStreams.size(); i++) {
        Iterator<Integer> it = sortedStreams.get(i);
        if (it.hasNext())
            pq.offer(new int[]{it.next(), i});
    }

    List<Integer> result = new ArrayList<>();
    while (!pq.isEmpty()) {
        int[] min = pq.poll();
        result.add(min[0]);
        Iterator<Integer> it =
            sortedStreams.get(min[1]);
        if (it.hasNext())
            pq.offer(new int[]{it.next(), min[1]});
    }
    return result.stream()
                 .mapToInt(i->i).toArray();
}
```

---

### ⚖️ Comparison Table

| Algorithm | Time (all cases) | Stable | Space | Cache | Best For |
|---|---|---|---|---|---|
| **Mergesort** | O(N log N) | Yes | O(N) | Moderate | Objects, external sort, linked list |
| Quicksort | O(N log N) avg, O(N²) worst | No | O(log N) | Excellent | Primitives, in-memory random data |
| Timsort | O(N log N) | Yes | O(N) | Excellent | Mixed/partially-sorted data (production) |
| Heapsort | O(N log N) | No | O(1) | Poor | In-place, worst-case guarantee |
| Insertion Sort | O(N²) | Yes | O(1) | Excellent | Small arrays N < 20 |

How to choose: Use Mergesort for objects requiring stable sort, linked list sorting, or external sorting. Use Quicksort for primitives when stability is not required. Use Timsort (Java's default) for the best overall practical performance.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Mergesort is always slower than Quicksort | Mergesort is faster than Quicksort for: objects (pointer chasing dominates, stable needed), linked lists (O(1) space merge via re-linking), and nearly-sorted data (Timsort exploits runs) |
| Mergesort is O(N) space — same as input | The auxiliary array is O(N) additional space beyond the input. Total space usage is O(N) for the array + O(N) for temp = O(N), but double the input size at peak |
| Stable sort is just a "nice to have" | Stability is required for multi-key sorts: sort by salary, then by name. Only a stable re-sort preserves name order within same-salary groups. Python's `sorted()` and Java's `Arrays.sort(objects)` are stable for exactly this reason |
| Bottom-up mergesort is harder to understand | Bottom-up avoids recursion and can be simpler to reason about for non-recursive programmers. It also avoids recursion stack depth concerns |
| Mergesort is O(N log N) on linked lists | On linked lists, merge is O(N log N) time AND O(1) space (nodes are re-linked, not copied). This makes mergesort the optimal sort for linked lists — unlike arrays where O(N) auxiliary space is needed |

---

### 🚨 Failure Modes & Diagnosis

**1. Off-by-one in merge boundaries**

**Symptom:** Sorted output has duplicate values, missing values, or values out of order.

**Root Cause:** `mid` calculation or loop bounds are wrong. `mid = (lo+hi)/2` overflows for large indices; loop conditions `i <= mid` vs `i < mid` are critical.

**Diagnostic:**
```java
// Test on tiny arrays: [2,1], [3,1,2]
// Verify all elements present after sort
Set<Integer> before = new HashSet<>(
    Arrays.asList(ArrayUtils.toObject(arr)));
mergesort(arr, 0, arr.length-1);
Set<Integer> after = new HashSet<>(
    Arrays.asList(ArrayUtils.toObject(arr)));
assert before.equals(after)
    : "Elements lost or duplicated!";
```

**Fix:** Use `mid = lo + (hi - lo) / 2` (overflow-safe). Loop conditions: `i <= mid`, `j <= hi` (not `<`). Always verify element count before/after.

**Prevention:** Unit test edge cases: single element, two elements, all-equal elements, reversed input.

---

**2. Auxiliary array allocated inside recursive calls (memory thrashing)**

**Symptom:** Extremely slow sorting; heap allocation spikes visible in profiler; GC pressure high.

**Root Cause:** `int[] temp = new int[hi-lo+1]` inside the `merge()` method allocates a new array on every recursive call. For `mergesort(arr, 0, N-1)`, this allocates O(N log N) total memory — for N=10⁶, roughly 80 MB of garbage.

**Diagnostic:**
```bash
# Java: enable GC logging
java -Xlog:gc* -jar Sort.jar
# Look for repeated minor GC during sort
```

**Fix:** Allocate `temp` once in the outer `sort()` method and pass it to every recursive call.

**Prevention:** Never allocate auxiliary memory inside the recursive step. Pre-allocate before recursion begins.

---

**3. Instability due to wrong comparison operator**

**Symptom:** Elements with equal keys are reordered unexpectedly after sort.

**Root Cause:** Using `<` instead of `<=` when comparing left vs right sub-array elements. `if (temp[i] < temp[j])` (strict less than) will choose right-half elements on equal — making sort unstable.

**Diagnostic:**
{% raw %}
```java
// Test stability with equal-key objects:
int[][] data = {{3,"A"},{1,"B"},{1,"C"}};
// Sort by first field; expect B before C
mergesort(data);
assert data[0][1]=="B" && data[1][1]=="C"
    : "Stability violated!";
```
{% endraw %}

**Fix:** Change to `if (temp[i] <= temp[j])` — when equal, left wins (preserves order).

**Prevention:** Comment stability requirement explicitly. Document: `<=` for stable, `<` for unstable.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Recursion` — mergesort is recursive; understand base cases and stack depth.
- `Divide and Conquer` — mergesort is the canonical D&C example; understand split-and-combine paradigm.
- `Arrays` — mergesort operates on arrays with auxiliary buffer; understand copying and indexing.

**Builds On This (learn these next):**
- `Timsort` — mergesort optimised for real-world data; exploits existing sorted runs; Java's `Arrays.sort` for objects.
- `External Sort` — K-way merge of sorted disk chunks; widely used in databases and Hadoop.
- `Parallel Mergesort` — independent sub-arrays are sorted on separate threads, then merged.

**Alternatives / Comparisons:**
- `Quicksort` — faster in practice for primitives (cache efficiency); not stable; O(N²) worst case.
- `Heapsort` — O(N log N) worst case, O(1) space; not stable; poor cache performance.
- `Timsort` — adaptive mergesort; significantly faster on real-world partially-sorted data.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Divide-and-conquer sort: split, sort,     │
│              │ merge; O(N log N) guaranteed, stable      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Stable guaranteed-O(N log N) sort;        │
│ SOLVES       │ Quicksort's instability and O(N²) worst   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Two sorted arrays can be merged in O(N)   │
│              │ — this is the primitive that enables D&C  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Stable sort needed; linked lists; external│
│              │ sort; objects; adversarial input possible  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Memory is constrained (O(N) aux space);   │
│              │ primitives where Quicksort is faster      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N log N) guaranteed, stable vs O(N)     │
│              │ extra space, cache-unfriendly vs Quicksort│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Split to atoms, merge back precisely —   │
│              │  every merge is a guaranteed O(N)"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Timsort → External Sort → Parallel Sort   │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** The merge step of mergesort writes to an auxiliary array and then copies back. This means each element is written twice per merge level (once to temp, once back to arr). Total writes = 2N per level × O(log N) levels = O(N log N) writes. Design an optimisation — used in some production implementations — that alternates the role of `arr` and `temp` between recursion levels, eliminating the copy-back step. What invariant must the recursion maintain, and how does the bottom-up version simplify this alternation?

**Q2.** Mergesort is efficient for external sorting because it processes data in sequential passes — ideal for magnetic tape or disk. Consider sorting 1 TB of integers on a machine with 1 GB RAM and 2 TB of disk space. Design the complete external mergesort: (1) how many sorted runs are generated in the first pass, (2) how many merge passes are needed, (3) what is the total number of disk reads and writes, and (4) where does a K-way heap-based merge reduce the number of passes compared to 2-way merge?

