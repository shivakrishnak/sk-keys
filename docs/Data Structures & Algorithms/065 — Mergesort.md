---
layout: default
title: "Mergesort"
parent: "Data Structures & Algorithms"
nav_order: 65
permalink: /dsa/mergesort/
number: "0065"
category: Data Structures & Algorithms
difficulty: â˜…â˜…â˜†
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

# 065 â€” Mergesort

âš¡ TL;DR â€” Mergesort divides an array in half, recursively sorts each half, then merges them â€” guaranteeing O(N log N) in all cases and stable ordering, at the cost of O(N) extra space.

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #065         â”‚ Category: Data Structures & Algorithms â”‚ Difficulty: â˜…â˜…â˜†        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Depends on:  â”‚ Recursion, Divide and Conquer, Arrays  â”‚                        â”‚
â”‚ Used by:     â”‚ Timsort, External Sort, Parallel Sort  â”‚                        â”‚
â”‚ Related:     â”‚ Quicksort, Timsort, Heapsort           â”‚                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

### ðŸ”¥ The Problem This Solves

WORLD WITHOUT IT:
You need to sort 1 million Employee objects by salary. Quicksort achieves O(N log N) on average but is **not stable** â€” two employees with equal salaries might swap positions. If you previously sorted by last name, a Quicksort on salary will scramble employees with identical salaries into arbitrary order. Also, Quicksort can degrade to O(NÂ²) on adversarial input.

THE BREAKING POINT:
For sorting objects (not just primitives), two requirements often conflict: stability (preserve relative order of equal elements) and guaranteed O(N log N) performance. Quicksort provides neither guarantee. You need a sort that is both stable and worst-case O(N log N).

THE INVENTION MOMENT:
Divide the array in half. Sort each half independently. Merge the two sorted halves by comparing front-to-front and always choosing the smaller element â€” if equal, choose the left half's element (preserving order = stability). This merge step is O(N) â€” two sorted arrays can be merged without any backtracking. The recursion produces O(log N) levels, each doing O(N) work in total. This is exactly why **Mergesort** was created.

### ðŸ“˜ Textbook Definition

**Mergesort** is a divide-and-conquer sorting algorithm that recursively divides arrays into halves until trivially sorted (size â‰¤ 1), then merges them back using a two-pointer merge operation. Time complexity: O(N log N) in all cases (best, average, worst). Space complexity: O(N) auxiliary. Mergesort is **stable** â€” equal elements retain their original relative order. It is optimal for fully general comparison-based sorting: no comparison sort can beat O(N log N) in worst case.

### â±ï¸ Understand It in 30 Seconds

**One line:**
Split into halves, sort each half, then merge them â€” works perfectly every time because merging two sorted arrays is trivial.

**One analogy:**
> Imagine sorting a shuffled stack of numbered cards. Split the deck in half. Hand each half to a friend to sort. When both friends return sorted piles, merge them: always take the smaller top card from either pile. Two sorted piles merge into one sorted pile in O(N) steps.

**One insight:**
Mergesort's strength is its predictability â€” O(N log N) regardless of input, no adversarial cases, stable. Its weakness is the O(N) extra space for the merge buffer. This space cost is why production systems use Timsort (mergesort variant) for objects, which reuses existing sorted runs to reduce auxiliary memory usage.

### ðŸ”© First Principles Explanation

CORE INVARIANTS:
1. Mergesort's correctness relies on one fact: **two sorted arrays can be merged into one sorted array in O(N) time** using two pointers.
2. The recursion terminates because sub-arrays strictly shrink. An array of size 1 is trivially sorted.
3. The merge step is **stable** if left-half elements are chosen before right-half when equal.

DERIVED DESIGN:
The merge operation is the core insight. Given two sorted arrays L and R, maintain pointers `i` (into L) and `j` (into R). Compare L[i] and R[j]; write the smaller. For stability: if equal, write L[i] (left has priority). Advance the pointer of the written element. When one array is exhausted, copy the remaining elements of the other.

**Why O(N log N) is a lower bound for comparison sort:**
Any comparison sort must distinguish N! possible input orderings. Information-theoretically, this requires at least logâ‚‚(N!) comparisons = Î˜(N log N) by Stirling's approximation. Mergesort achieves exactly this lower bound â€” it is asymptotically optimal.

**Why Quicksort beats Mergesort in practice despite same big-O:**
Mergesort writes to an auxiliary buffer then back â€” two passes per merge. Quicksort's in-place partition does one pass. For random data, Quicksort's cache-sequential access pattern gives 2-4x speedup despite the same asymptotic complexity. Mergesort wins when: stability required, adversarial inputs possible, or sorting linked lists (mergesort is O(1) space for linked lists â€” no random access needed; Quicksort on linked lists is O(N) space).

THE TRADE-OFFS:
Gain: O(N log N) guaranteed (no adversarial cases); stable; parallelisable; ideal for linked lists and external sort.
Cost: O(N) auxiliary space; worse cache performance than Quicksort for in-memory random data.

### ðŸ§ª Thought Experiment

SETUP:
Array: [5, 2, 4, 6, 1, 3]. Walk through mergesort.

SPLIT PHASE:
Level 0: [5,2,4,6,1,3]
Level 1: [5,2,4] | [6,1,3]
Level 2: [5,2] [4] | [6,1] [3]
Level 3: [5] [2] [4] | [6] [1] [3]  â† all size-1

MERGE PHASE (bottom-up):
Merge [5]+[2]=[2,5]. Merge [4]==[4].
Merge [2,5]+[4]=[2,4,5] â† stable merge.
Merge [6]+[1]=[1,6]. Merge [3]=[3].
Merge [1,6]+[3]=[1,3,6].
Merge [2,4,5]+[1,3,6]=[1,2,3,4,5,6]. Done.

THE INSIGHT:
Each merge level does O(N) total work across all merge operations at that level (all sub-arrays together span the full array). With O(log N) levels, total work is O(N log N) â€” and this is the same regardless of the initial order of elements. Mergesort's tree is always perfectly balanced â€” unlike Quicksort where adversarial inputs can create a degenerate tree.

### ðŸ§  Mental Model / Analogy

> Mergesort is like a library reorganisation project. You sort all books by category, then by author within each category, then by title within each author â€” each step works with already-organised smaller groups and just merges them. The merge operation is clean: always take whichever book comes next alphabetically from either pile. You never have to re-examine a book you've already filed.

"Sort smaller groups first" â†’ recursive sort of halves
"Always take alphabetically-next book" â†’ two-pointer merge comparison
"Already-filed books never re-examined" â†’ O(N) merge (no backtracking)
"Final merge = fully sorted" â†’ merging two sorted halves produces sorted whole

Where this analogy breaks down: A real library reorganisation would reorder books in-place (no extra shelf space). Mergesort requires an auxiliary array for the merge buffer â€” the equivalent of a temporary staging shelf, which real libraries often don't have.

### ðŸ“¶ Gradual Depth â€” Four Levels

**Level 1 â€” What it is (anyone can understand):**
Mergesort sorts by splitting into two halves, sorting each half (recursively), then merging the sorted halves. Merging two sorted lists is easy: compare the fronts and always take the smaller one. Repeat this "split â†’ sort â†’ merge" process until the whole array is sorted.

**Level 2 â€” How to use it (junior developer):**
`mergesort(arr, 0, n-1)`. Base case: if `lo == hi`, return. Split at `mid = (lo+hi)/2`. Recursively sort `[lo..mid]` and `[mid+1..hi]`. Then call `merge(arr, lo, mid, hi)` which uses an auxiliary array `temp[]` to merge the two sorted halves back into `arr[lo..hi]`. Stability: in the merge step, when `arr[i] == arr[j]`, always write `arr[i]` first (left sub-array priority).

**Level 3 â€” How it works (mid-level engineer):**
Bottom-up mergesort avoids recursion entirely: start with sub-arrays of size 1 (all trivially sorted), merge them into size-2, then size-4, then size-8, until the whole array is sorted. This is cache-friendlier than top-down and avoids function call overhead. Timsort uses bottom-up mergesort with size-doubling and exploits existing sorted runs (natural mergesort). For linked lists, mergesort is O(1) extra space: merge is done by relinking nodes, not by copying to an auxiliary array â€” making mergesort the optimal linked-list sort.

**Level 4 â€” Why it was designed this way (senior/staff):**
John von Neumann invented mergesort in 1945 â€” predating computers. It was the foundational algorithm for early computing because it maps perfectly to sequential tape storage: two tapes can be merged into a sorted output tape without random access. This "external sort" application remains relevant today for big-data sorting (Hadoop's map phase produces sorted partitions that are then merge-sorted in the reduce phase). The information-theoretic lower bound proof (O(N log N) is optimal for comparison sort) was developed partly in response to trying to prove mergesort could be improved â€” leading to the fundamental negative result.

### âš™ï¸ How It Works (Mechanism)

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Mergesort Top-Down Recursion               â”‚
â”‚                                            â”‚
â”‚  mergesort(arr, lo, hi):                   â”‚
â”‚    if lo >= hi: return (base case)         â”‚
â”‚    mid = lo + (hi - lo) / 2               â”‚
â”‚    mergesort(arr, lo, mid)   â† left half   â”‚
â”‚    mergesort(arr, mid+1, hi) â† right half  â”‚
â”‚    merge(arr, lo, mid, hi)   â† combine     â”‚
â”‚                                            â”‚
â”‚  merge(arr, lo, mid, hi):                  â”‚
â”‚    copy arr[lo..hi] to temp[]             â”‚
â”‚    i = lo, j = mid+1, k = lo              â”‚
â”‚    while i<=mid AND j<=hi:                 â”‚
â”‚      if temp[i] <= temp[j]:               â”‚
â”‚        arr[k++] = temp[i++] â† left first â”‚
â”‚      else:                                â”‚
â”‚        arr[k++] = temp[j++]              â”‚
â”‚    copy remaining elements               â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
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

### ðŸ”„ The Complete Picture â€” End-to-End Flow

NORMAL FLOW:
```
Unsorted array of N elements
â†’ [MERGESORT â† YOU ARE HERE]
  â†’ Recursively split to size-1 arrays
  â†’ Merge bottom-up: 1â†’2â†’4â†’8â†’...â†’N
  â†’ Each merge: two sorted halves â†’ one
â†’ Fully sorted array
â†’ O(N log N) time, O(N) space, stable
```

FAILURE PATH:
```
Very large N with constrained memory
â†’ Auxiliary array of N elements = NÃ—4 bytes
â†’ For N=10â¸: 400 MB auxiliary memory
â†’ System OOM or swap thrashing
â†’ Fix: use in-place mergesort (complex,
  degrades to O(N logÂ²N)) or external sort
  with streaming merge from disk
```

WHAT CHANGES AT SCALE:
Mergesort is the basis for **external sorting** â€” data too large for RAM. Write sorted chunks to disk (run generation phase), then K-way merge the sorted chunks. Apache Spark's sort shuffle uses distributed mergesort: each task sorts its partition, and the shuffle merge combines sorted partitions across machines. For N=1 TB of data on 100 machines, each machine processes 10 GB, sorts it (mergesort), and the sorted outputs are merged using a priority queue.

### ðŸ’» Code Example

**Example 1 â€” Standard top-down mergesort:**
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

**Example 2 â€” Mergesort for counting inversions:**
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

**Example 3 â€” External K-way merge (streaming):**
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

### âš–ï¸ Comparison Table

| Algorithm | Time (all cases) | Stable | Space | Cache | Best For |
|---|---|---|---|---|---|
| **Mergesort** | O(N log N) | Yes | O(N) | Moderate | Objects, external sort, linked list |
| Quicksort | O(N log N) avg, O(NÂ²) worst | No | O(log N) | Excellent | Primitives, in-memory random data |
| Timsort | O(N log N) | Yes | O(N) | Excellent | Mixed/partially-sorted data (production) |
| Heapsort | O(N log N) | No | O(1) | Poor | In-place, worst-case guarantee |
| Insertion Sort | O(NÂ²) | Yes | O(1) | Excellent | Small arrays N < 20 |

How to choose: Use Mergesort for objects requiring stable sort, linked list sorting, or external sorting. Use Quicksort for primitives when stability is not required. Use Timsort (Java's default) for the best overall practical performance.

### âš ï¸ Common Misconceptions

| Misconception | Reality |
|---|---|
| Mergesort is always slower than Quicksort | Mergesort is faster than Quicksort for: objects (pointer chasing dominates, stable needed), linked lists (O(1) space merge via re-linking), and nearly-sorted data (Timsort exploits runs) |
| Mergesort is O(N) space â€” same as input | The auxiliary array is O(N) additional space beyond the input. Total space usage is O(N) for the array + O(N) for temp = O(N), but double the input size at peak |
| Stable sort is just a "nice to have" | Stability is required for multi-key sorts: sort by salary, then by name. Only a stable re-sort preserves name order within same-salary groups. Python's `sorted()` and Java's `Arrays.sort(objects)` are stable for exactly this reason |
| Bottom-up mergesort is harder to understand | Bottom-up avoids recursion and can be simpler to reason about for non-recursive programmers. It also avoids recursion stack depth concerns |
| Mergesort is O(N log N) on linked lists | On linked lists, merge is O(N log N) time AND O(1) space (nodes are re-linked, not copied). This makes mergesort the optimal sort for linked lists â€” unlike arrays where O(N) auxiliary space is needed |

### ðŸš¨ Failure Modes & Diagnosis

**1. Off-by-one in merge boundaries**

Symptom: Sorted output has duplicate values, missing values, or values out of order.

Root Cause: `mid` calculation or loop bounds are wrong. `mid = (lo+hi)/2` overflows for large indices; loop conditions `i <= mid` vs `i < mid` are critical.

Diagnostic:
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

Fix: Use `mid = lo + (hi - lo) / 2` (overflow-safe). Loop conditions: `i <= mid`, `j <= hi` (not `<`). Always verify element count before/after.

Prevention: Unit test edge cases: single element, two elements, all-equal elements, reversed input.

---

**2. Auxiliary array allocated inside recursive calls (memory thrashing)**

Symptom: Extremely slow sorting; heap allocation spikes visible in profiler; GC pressure high.

Root Cause: `int[] temp = new int[hi-lo+1]` inside the `merge()` method allocates a new array on every recursive call. For `mergesort(arr, 0, N-1)`, this allocates O(N log N) total memory â€” for N=10â¶, roughly 80 MB of garbage.

Diagnostic:
```bash
# Java: enable GC logging
java -Xlog:gc* -jar Sort.jar
# Look for repeated minor GC during sort
```

Fix: Allocate `temp` once in the outer `sort()` method and pass it to every recursive call.

Prevention: Never allocate auxiliary memory inside the recursive step. Pre-allocate before recursion begins.

---

**3. Instability due to wrong comparison operator**

Symptom: Elements with equal keys are reordered unexpectedly after sort.

Root Cause: Using `<` instead of `<=` when comparing left vs right sub-array elements. `if (temp[i] < temp[j])` (strict less than) will choose right-half elements on equal â€” making sort unstable.

Diagnostic:
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

Fix: Change to `if (temp[i] <= temp[j])` â€” when equal, left wins (preserves order).

Prevention: Comment stability requirement explicitly. Document: `<=` for stable, `<` for unstable.

### ðŸ”— Related Keywords

**Prerequisites (understand these first):**
- `Recursion` â€” mergesort is recursive; understand base cases and stack depth.
- `Divide and Conquer` â€” mergesort is the canonical D&C example; understand split-and-combine paradigm.
- `Arrays` â€” mergesort operates on arrays with auxiliary buffer; understand copying and indexing.

**Builds On This (learn these next):**
- `Timsort` â€” mergesort optimised for real-world data; exploits existing sorted runs; Java's `Arrays.sort` for objects.
- `External Sort` â€” K-way merge of sorted disk chunks; widely used in databases and Hadoop.
- `Parallel Mergesort` â€” independent sub-arrays are sorted on separate threads, then merged.

**Alternatives / Comparisons:**
- `Quicksort` â€” faster in practice for primitives (cache efficiency); not stable; O(NÂ²) worst case.
- `Heapsort` â€” O(N log N) worst case, O(1) space; not stable; poor cache performance.
- `Timsort` â€” adaptive mergesort; significantly faster on real-world partially-sorted data.

### ðŸ“Œ Quick Reference Card

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ WHAT IT IS   â”‚ Divide-and-conquer sort: split, sort,     â”‚
â”‚              â”‚ merge; O(N log N) guaranteed, stable      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ PROBLEM IT   â”‚ Stable guaranteed-O(N log N) sort;        â”‚
â”‚ SOLVES       â”‚ Quicksort's instability and O(NÂ²) worst   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ KEY INSIGHT  â”‚ Two sorted arrays can be merged in O(N)   â”‚
â”‚              â”‚ â€” this is the primitive that enables D&C  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Stable sort needed; linked lists; externalâ”‚
â”‚              â”‚ sort; objects; adversarial input possible  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Memory is constrained (O(N) aux space);   â”‚
â”‚              â”‚ primitives where Quicksort is faster      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ TRADE-OFF    â”‚ O(N log N) guaranteed, stable vs O(N)     â”‚
â”‚              â”‚ extra space, cache-unfriendly vs Quicksortâ”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Split to atoms, merge back precisely â€”   â”‚
â”‚              â”‚  every merge is a guaranteed O(N)"        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Timsort â†’ External Sort â†’ Parallel Sort   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

---
### ðŸ§  Think About This Before We Continue

**Q1.** The merge step of mergesort writes to an auxiliary array and then copies back. This means each element is written twice per merge level (once to temp, once back to arr). Total writes = 2N per level Ã— O(log N) levels = O(N log N) writes. Design an optimisation â€” used in some production implementations â€” that alternates the role of `arr` and `temp` between recursion levels, eliminating the copy-back step. What invariant must the recursion maintain, and how does the bottom-up version simplify this alternation?

**Q2.** Mergesort is efficient for external sorting because it processes data in sequential passes â€” ideal for magnetic tape or disk. Consider sorting 1 TB of integers on a machine with 1 GB RAM and 2 TB of disk space. Design the complete external mergesort: (1) how many sorted runs are generated in the first pass, (2) how many merge passes are needed, (3) what is the total number of disk reads and writes, and (4) where does a K-way heap-based merge reduce the number of passes compared to 2-way merge?

