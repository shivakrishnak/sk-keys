---
layout: default
title: "Timsort"
parent: "Data Structures & Algorithms"
nav_order: 66
permalink: /dsa/timsort/
number: "0066"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Mergesort, Insertion Sort, Divide and Conquer
used_by: Java Arrays.sort (objects), Python sorted(), Android Arrays.sort
related: Mergesort, Quicksort, Adaptive Sorting
tags:
  - algorithm
  - advanced
  - deep-dive
  - pattern
  - performance
---

# 066 — Timsort

⚡ TL;DR — Timsort is a hybrid mergesort that exploits naturally occurring sorted "runs" in real data, achieving O(N) on nearly-sorted input while guaranteeing O(N log N) worst case and full stability.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #066         │ Category: Data Structures & Algorithms │ Difficulty: ★★★        │
├──────────────┼────────────────────────────────────────┼────────────────────────┤
│ Depends on:  │ Mergesort, Insertion Sort,             │                        │
│              │ Divide and Conquer                     │                        │
│ Used by:     │ Java Arrays.sort (objects), Python     │                        │
│              │ sorted(), Android Arrays.sort          │                        │
│ Related:     │ Mergesort, Quicksort, Adaptive Sorting │                        │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
vanilla mergesort treats every array as completely random — it always splits into exactly two halves, ignoring the order already present in real-world data. A database result set sorted by timestamp then queried with new records inserted in order might be 95% already sorted. Standard mergesort still performs the full O(N log N) work, ignoring this existing order.

THE BREAKING POINT:
Real-world data is rarely random. Arrays arrive partially sorted (database query results, log files already partially ordered, records with several fields already in order). Algorithms designed for worst-case random inputs waste operations on already-ordered sequences. A "smart" sort could be O(N) for already-sorted data and O(N log N) for random — but no classic algorithm achieves this without sacrifice.

THE INVENTION MOMENT:
Tim Peters designed Timsort in 2002 for Python. The key insight: scan the array for **natural runs** (already-sorted sequences, ascending or descending). Extend each run to a minimum length using insertion sort (insertion sort is O(N²) overall but O(N) on nearly-sorted data for small N). Then merge runs together using a carefully designed merge order that balances run sizes using a stack — the "galloping" merge accelerates through long ordered sequences. This is exactly why **Timsort** was created.

### 📘 Textbook Definition

**Timsort** is a hybrid stable sorting algorithm derived from mergesort and insertion sort. It identifies and extends natural sorted **runs** of minimum length `minrun` (typically 32–64), then merges them using a merge stack that maintains size-balance invariants to ensure O(N log N) worst-case performance. Best case (already sorted): O(N). Average and worst case: O(N log N). Space: O(N). Timsort is the default sort in Python (`sorted()`, `list.sort()`), Java (`Arrays.sort` for objects), Android, V8, and many other platforms.

### ⏱️ Understand It in 30 Seconds

**One line:**
Find existing sorted chunks, extend them to minimum size, then merge them strategically to minimise total work.

**One analogy:**
> Imagine sorting a stack of papers that are 70% already in alphabetical order (put there by a previous half-finished sort). A naive sorter throws them all back and re-sorts. Timsort notices the alphabetical stretches and only re-sorts the gaps — slotting unsorted papers into the already-sorted streaks using the cheapest possible method (insertion sort), then merging the large ordered blocks together.

**One insight:**
Timsort is an **adaptive** algorithm — its work is proportional to the disorder in the input, not the input size. For fully sorted data, it detects one run and stops in O(N). For random data, it creates N/minrun runs and merges them in O(N log N). The genius is that it detects and exploits the existing structure without degrading worst-case performance.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The input is decomposed into **runs** — maximal ascending (or descending-then-reversed) sequences.
2. Every run is extended to at least `minrun` length using **insertion sort** — insertion sort is O(N) on nearly-sorted small arrays.
3. A merge stack maintains the **balance invariant**: for runs A, B, C on the stack (top = C): `|A| > |B| + |C|` and `|B| > |C|`. This ensures total merge cost is O(N log N).

DERIVED DESIGN:
**Why minrun = 32 to 64?**
For N elements with runs of minrun each, there are approximately N/minrun runs. These runs are then merged in a balanced manner. minrun is chosen so that N/minrun is a power of 2 (or close), making merges perfectly balanced. Empirically, 32–64 is optimal on modern hardware (cache line size × small).

**Why the balance invariant prevents O(N²) merges?**
Without the invariant, always merging adjacent runs could degenerate: if run sizes are [1, 1, 1, ..., 1, N], merging from left produces 1+1=2, 2+1=3, 3+1=4, ... N-1+1=N — total work O(N²). The balance invariant forces larger runs to be merged first, creating a balanced merge tree — total work O(N log N).

**Galloping mode:**
During merge, if one run consistently wins comparisons (e.g., 7+ consecutive elements from left beat all from right), enter "galloping mode" — use exponential search to find where the current run's contribution ends, then copy the whole block at once. This is O(1) per element for long monotone streaks. Disabled when elements alternate between left/right (random order).

THE TRADE-OFFS:
Gain: O(N) on nearly-sorted data; O(N log N) worst case; stable; excellent real-world performance.
Cost: Complex implementation (~500 lines in CPython vs ~30 lines for naive mergesort); O(N) auxiliary space.

### 🧪 Thought Experiment

SETUP:
Array of 100 elements: [sorted 80 elements] + [random 20 elements].

WITHOUT TIMSORT (standard mergesort):
Split at mid=50 (ignoring the natural 80-element run). Mergesort recursively splits into 25, 12, 6, 3, 2, 1-element sub-arrays. ~650 comparisons total (Nlog₂N ≈ 100×6.6).

WITH TIMSORT:
Scan: finds run 1 = first 80 elements (already sorted). Run 2 = last 20 elements. Merge run 1 (size 80) with run 2 (size 20): O(80+20) = 100 comparisons. Wait — run 2 is not sorted. Insertion sort run 2 (20 elements, random): O(20²)/2 ≈ 200 comparisons worst case, but likely much fewer. Then merge: ~100 comparisons. Total: ~300 comparisons vs ~650. Timsort is roughly 2x faster on this input.

THE INSIGHT:
Timsort's adaptive behaviour means it performs work proportional to the **entropy** of the input, not just its size. The fewer sorted runs that need merging, the less work is done. For random data, the work is similar to plain mergesort; for real-world data (which has significant existing order), Timsort is substantially faster.

### 🧠 Mental Model / Analogy

> Timsort is like a professional archivist sorting documents. Instead of blindly shuffling everything into a single pile and sorting from scratch, the archivist first identifies which files are already in order (runs). They slightly re-organise small clusters (insertion sort small runs to minrun size), then systematically merge the ordered clusters in the most balanced possible order. The already-ordered work is never redone.

"Already-ordered files" → natural runs in input
"Organise small clusters" → insertion sort to extend runs to minrun
"Merge ordered clusters in balanced order" → merge stack with balance invariant
"Never redo ordered work" → O(N) for already-sorted input

Where this analogy breaks down: Real archivists can see the whole document set at once. Timsort makes one sequential pass to identify runs, then merges blindly — it cannot skip ahead to see future optimal run boundaries.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Timsort notices that most real data has stretches already in order. It takes advantage of this — reusing the order that's already there instead of throwing it away and sorting from scratch. The result is a sort that starts fast when data is already mostly sorted, and falls back to reliable N log N speed for random data.

**Level 2 — How to use it (junior developer):**
In Java: `Arrays.sort(objectArray)` and `Collections.sort(list)` use Timsort automatically. In Python: `sorted()` and `list.sort()` use Timsort. For custom implementations, the key parameters are `minrun` (typically 32) and the merge stack balance invariant checks. You rarely implement Timsort yourself — use the language-provided stable sort.

**Level 3 — How it works (mid-level engineer):**
Timsort scans the array once identifying runs (O(N)). For each run shorter than `minrun`, insertion sort extends it by absorbing subsequent elements. The merge stack maintains two invariants: `A > B + C` and `B > C`. When a new run C is pushed, check if invariants hold; if not, merge B with the smaller of A or C, then recheck. This cascades until invariants hold. Galloping mode activates when one-sided consecutive wins exceed 7 — exponential search then binary search to find the boundary, then bulk copy. Galloping is disabled when the advantage disappears.

**Level 4 — Why it was designed this way (senior/staff):**
The merge invariants were designed to ensure that the total number of merges is O(N log N) regardless of run distribution. The proof uses a potential function argument: each element participates in O(log N) merges because each merge doubles the size of at least one participant. The galloping mode is Timsort's most clever innovation: it transitions from comparison-based to rank-based (binary search) as patterns are detected. Tim Peters described Timsort in a 2002 email as running faster than any general comparison sort at the time on a wide variety of real-world data. It has since been found to have a bug (the invariant was slightly wrong, triggering an ArrayIndexOutOfBoundsException discovered by formal verification in 2015 via model checking with OpenJDK). The fix changed the stack size from `2×ceil(log₂(n)) + 1` to `ceil(log₂(n)) + 4`.

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ Timsort: Phase 1 — Run Detection           │
│                                            │
│  Scan array left to right:                 │
│  If arr[i] <= arr[i+1]: ascending run      │
│  If arr[i] >  arr[i+1]: descending run     │
│    → reverse in-place (stable reversal)    │
│  Extend short runs to minrun via           │
│    insertion sort                          │
└────────────────────────────────────────────┘
┌────────────────────────────────────────────┐
│ Timsort: Phase 2 — Run Merging             │
│                                            │
│  Stack: top 3 runs = C, B, A (C = newest) │
│  After each new run pushed:                │
│    while NOT (|A| > |B|+|C| AND |B| > |C|)│
│      merge B with min(A, C)               │
│      check again                           │
│  At end: merge all remaining on stack      │
└────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Real-world object array (partially sorted)
→ Compute minrun for this N
→ Scan for natural runs
→ [TIMSORT ← YOU ARE HERE]
  → Extend short runs via insertion sort
  → Push runs onto merge stack
  → Maintain balance invariant (merge when violated)
  → Merge all remaining stack entries
→ Fully sorted, stable output
→ O(N) if pre-sorted, O(N log N) general
```

FAILURE PATH:
```
Pathological input crafts run sizes that
violate balance invariant implementation assumptions
→ Stack overflow in merge stack (pre-2015 bug)
→ Fixed in Java 8u40, Python 2.7.x/3.x patches
→ Modern: invariant proof ensures O(N log N)
```

WHAT CHANGES AT SCALE:
For N=10⁸ elements, Timsort's run detection phase (O(N)) avoids the O(N log N) overhead of naive mergesort for partially-sorted inputs. In practice (database results, log files), 30-70% of real data has significant existing order, making Timsort 2-4x faster than theoretical random-data analysis would suggest.

### 💻 Code Example

**Example 1 — Using Timsort in Java (always default):**
```java
// Java Arrays.sort for objects uses Timsort
// No action needed — it's the default
Employee[] employees = loadEmployees();

// Sort by salary (Timsort runs, stable)
Arrays.sort(employees,
    Comparator.comparingInt(Employee::getSalary));

// Sort by name, then salary (multi-key)
// First sort by salary, then stable sort by name
// Name sort preserves order within same names
Arrays.sort(employees,
    Comparator.comparing(Employee::getName)
              .thenComparingInt(
                  Employee::getSalary));
```

**Example 2 — Simplified Timsort skeleton:**
```java
static final int MIN_RUN = 32;

void timsort(int[] arr) {
    int n = arr.length;
    // Phase 1: Create runs of at least MIN_RUN
    for (int i = 0; i < n; i += MIN_RUN) {
        int end = Math.min(i + MIN_RUN - 1, n-1);
        // Extend run using insertion sort
        insertionSort(arr, i, end);
    }
    // Phase 2: Merge runs
    for (int size = MIN_RUN; size < n; size *= 2) {
        for (int lo = 0; lo < n; lo += 2*size) {
            int mid = lo + size - 1;
            int hi = Math.min(lo+2*size-1, n-1);
            if (mid < hi)
                merge(arr, lo, mid, hi);
        }
    }
}

void insertionSort(int[] arr, int lo, int hi) {
    for (int i = lo+1; i <= hi; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= lo && arr[j] > key) {
            arr[j+1] = arr[j--];
        }
        arr[j+1] = key;
    }
}
```

**Example 3 — Benchmarking Timsort vs Mergesort:**
```java
// Create nearly-sorted array (90% sorted)
int[] arr = new int[100_000];
for (int i = 0; i < arr.length; i++)
    arr[i] = i; // fully sorted
// Scramble 10%:
Random r = new Random(42);
for (int i = 0; i < 10_000; i++) {
    int a = r.nextInt(arr.length);
    int b = r.nextInt(arr.length);
    int tmp = arr[a]; arr[a]=arr[b]; arr[b]=tmp;
}

int[] arrCopy = arr.clone();
long t1 = System.nanoTime();
Arrays.sort(arr); // Timsort (if Integer[])
long timsortTime = System.nanoTime() - t1;

// Manual mergesort on copy:
long t2 = System.nanoTime();
mergesortNaive(arrCopy);
long mergesortTime = System.nanoTime() - t2;

// Expected: timsortTime << mergesortTime
// for nearly-sorted input
System.out.printf("Timsort: %dms%n",
    timsortTime/1_000_000);
System.out.printf("Mergesort: %dms%n",
    mergesortTime/1_000_000);
```

### ⚖️ Comparison Table

| Algorithm | Best | Average | Worst | Stable | Adaptive | Space |
|---|---|---|---|---|---|---|
| **Timsort** | O(N) | O(N log N) | O(N log N) | Yes | Yes | O(N) |
| Mergesort | O(N log N) | O(N log N) | O(N log N) | Yes | No | O(N) |
| Quicksort | O(N log N) | O(N log N) | O(N²) | No | No | O(log N) |
| Heapsort | O(N log N) | O(N log N) | O(N log N) | No | No | O(1) |
| Insertion Sort | O(N) | O(N²) | O(N²) | Yes | Yes | O(1) |

How to choose: Use language-provided sort (Timsort) by default for objects. Use Quicksort for primitives (Java's default for primitives). Use Heapsort only when O(1) extra space is required.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Timsort is just "mergesort with insertion sort" | Timsort's original contribution is the merge balance invariant (run stack management), not just the hybrid. The invariant ensures O(N log N) worst case while exploiting existing runs |
| Timsort always uses O(N) space | Timsort uses O(N/2) auxiliary space for the merge buffer (only the smaller run is copied) — but it's still O(N) asymptotically. For very small merges, it uses O(minrun) space |
| Python's sorted() is slower than C qsort | Timsort in CPython's `sorted()` is implemented in C and is consistently faster than C's `qsort` on real-world data due to adaptive behaviour. On purely random data, they are comparable |
| Timsort's formal verification bug was serious | The bug (2015, formal verification by Brandeis team) caused ArrayIndexOutOfBoundsException only for arrays with > 2^49 ≈ 500 trillion elements — never triggered in practice. Fixed in Java 8u40 anyway |
| Galloping mode is always faster | Galloping mode is a net win only when long monotone sequences are present. For random data, the overhead of galloping threshold tracking makes it slightly slower. Timsort disables galloping when it's not helping |

### 🚨 Failure Modes & Diagnosis

**1. Using unstable sort where stable sort is required**

Symptom: After multi-key sort (sort by B, then sort by A), elements with equal A values are not in B-order.

Root Cause: Using `Arrays.sort(int[])` (Dual-Pivot Quicksort, unstable) or Quicksort instead of `Arrays.sort(Integer[])` / `Arrays.sort(objects, comparator)` (Timsort, stable).

Diagnostic:
```java
// Stability test:
Integer[][] rows = {{1,3},{1,2},{1,1}};
// Sort by second column: [{1,1},{1,2},{1,3}]
Arrays.sort(rows, (a,b)->a[1]-b[1]);
// Now sort by first column (stable: preserves 2nd)
Arrays.sort(rows, (a,b)->a[0]-b[0]);
assert rows[0][1]==1 && rows[1][1]==2 : "Unstable!";
```

Fix: Use `Arrays.sort` with a Comparator (uses Timsort for object arrays). Never use `int[]` sort when stability matters — box to `Integer[]` first or use a comparator.

Prevention: Document stability requirements at sort call sites. Java: Object sort = stable (Timsort). Primitive sort = unstable (Dual-Pivot Quicksort).

---

**2. Timsort run detection creating too many tiny runs (all-random data)**

Symptom: Timsort is not faster than plain mergesort on random data; profiling shows many small runs.

Root Cause: On truly random data, Timsort finds only runs of length 1-2 (no existing order). All runs are extended to minrun via insertion sort. This is effectively a bottom-up mergesort with extra overhead from run detection.

Diagnostic:
```bash
# Measure Timsort on random vs sorted data:
# If random is not significantly slower,
# Timsort is working correctly
# Timsort is NOT designed to beat Quicksort
# on random data — it's designed for real-world
```

Prevention: Not a failure — it is expected behaviour. Timsort on random data performs similarly to mergesort, which is the correct fallback.

---

**3. Using Timsort's assumed stability for external comparators with side effects**

Symptom: Comparator is called with the same pair in both orders (a,b) and (b,a); side effects trigger twice per pair.

Root Cause: Any comparison-based sort may call the comparator on any pair in any order. Timsort's stability only guarantees output order — not the order of comparator invocations.

Diagnostic:
```java
// Anti-pattern: logging in comparator
Arrays.sort(arr, (a,b) -> {
    log.info("Comparing {} and {}", a, b);
    return Integer.compare(a, b);
}); // log volume is not predictable
```

Fix: Move side effects out of the comparator. Log before/after sort, not inside.

Prevention: Comparators must be pure functions (no side effects). Java's documentation explicitly requires this.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Mergesort` — Timsort's primary merge mechanism is derived from mergesort; understand merge invariants.
- `Insertion Sort` — Timsort uses insertion sort to extend short runs; understand its O(N) behaviour on nearly-sorted small arrays.

**Builds On This (learn these next):**
- `Adaptive Sorting` — the broader category of algorithms that exploit existing order in input data.
- `External Sort` — Timsort's run generation phase is analogous to external sort's initial sorted-chunk generation.

**Alternatives / Comparisons:**
- `Mergesort` — simpler implementation, same asymptotic bounds; less adaptive (no O(N) best case).
- `Quicksort` — faster for primitives on random data; not stable; O(N²) worst case.
- `Introsort` — Quicksort hybrid with O(N log N) guarantee; not stable; used in C++ `std::sort`.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Hybrid mergesort exploiting natural runs  │
│              │ for adaptive performance                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Mergesort ignores existing order; real    │
│ SOLVES       │ data is partially sorted — waste avoided  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Detecting natural runs + merge balance    │
│              │ invariant = O(N) best + O(N log N) worst  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sorting objects (Java/Python default);    │
│              │ data has existing partial order           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sorting primitives (Dual-Pivot Quicksort  │
│              │ is faster); O(1) space required (Heapsort)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N) to O(N log N) adaptive vs complex    │
│              │ implementation (~500 lines in CPython)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't sort what's already sorted —       │
│              │  detect it and merge smart"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ External Sort → Parallel Sort → Introsort │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Timsort's merge stack invariant requires `|A| > |B| + |C|` and `|B| > |C|` for consecutive stack entries A, B, C. The 2015 formal verification found that the stack size was miscalculated: the implementation allocated `2*ceil(log_phi(n)) + 1` stack slots (where phi ≈ 1.618, Fibonacci growth), but rare inputs could create stack entries not bounded by this Fibonacci-related formula. Construct a sequence of run sizes that would minimally violate the original (buggy) stack size calculation. What property of the merge invariant enforcement allows a run sequence to grow the stack beyond the Fibonacci bound?

**Q2.** Timsort's galloping mode uses exponential search (doubling the range: 1, 2, 4, 8...) then binary search to find where to insert elements from one run into the other. The threshold for entering galloping mode is 7 consecutive one-sided victories. Why 7 specifically, and not 2 or 15? Describe the mathematical tradeoff: for an array with alternating blocks of size K from left and right runs, what value of K minimises the total comparison count when choosing the optimal galloping threshold?

