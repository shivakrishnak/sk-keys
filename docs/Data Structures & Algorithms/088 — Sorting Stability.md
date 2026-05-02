---
layout: default
title: "Sorting Stability"
parent: "Data Structures & Algorithms"
nav_order: 88
permalink: /dsa/sorting-stability/
number: "0088"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Sorting Algorithms, Array, Time Complexity / Big-O
used_by: Multi-Key Sorting, Database ORDER BY, Radix Sort
related: Merge Sort, Quick Sort, Comparison Sort
tags:
  - algorithm
  - intermediate
  - datastructure
  - pattern
  - foundational
---

# 088 — Sorting Stability

⚡ TL;DR — A stable sort preserves the original relative order of equal elements — essential for multi-key sorting and predictable database ordering.

| #0088 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Sorting Algorithms, Array, Time Complexity / Big-O | |
| **Used by:** | Multi-Key Sorting, Database ORDER BY, Radix Sort | |
| **Related:** | Merge Sort, Quick Sort, Comparison Sort | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Sort employees first by department, then by salary. You sort by salary first to get salary-ordered list. Then you sort by department. Without stability, the second sort scrambles the salary order within departments — employees in "Engineering" come out sorted by department but no longer in salary order within the department. Every secondary sort breaks the primary sort's ordering.

THE BREAKING POINT:
Multi-key sorting requires sorting multiple times, each sort refining the previous. This only works correctly if each sort preserves the relative ordering established by previous sorts. An unstable sort makes "sort by salary, then department" produce incorrect multi-key ordering.

THE INVENTION MOMENT:
A sort that preserves the relative order of equal elements — a **stable sort** — makes multi-key sorting compositional: sort by least-significant key first, then by most significant key. Equal-key elements retain their previously established order (from prior sorts). MergeSort and TimSort are canonical stable sorts. This is exactly why **Sorting Stability** matters.

---

### 📘 Textbook Definition

A sorting algorithm is **stable** if, for any two elements a and b where the key of a equals the key of b, and a appears before b in the input array, a still appears before b in the sorted output array. Formally: if key(a[i]) = key(a[j]) and i < j, then in the output a[i] still precedes a[j]. Stable sorting algorithms include: MergeSort, InsertionSort, BubbleSort, TimSort, and CountingSort. Unstable algorithms include HeapSort, QuickSort (standard), and SelectionSort. Any unstable algorithm can be made stable by augmenting elements with their original index as a tiebreaker.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Equal elements keep their original order — what was first stays first.

**One analogy:**
> A stack of index cards sorted alphabetically by last name. Two "Smith" cards exist — one for "John Smith" (page 7) and "Jane Smith" (page 3). A stable sort leaves John before Jane (since John was first in the original stack). An unstable sort might swap them, losing the original ordering information.

**One insight:**
Stability only matters when elements are considered "equal" by the sort key but differ in other ways. For primitive types sorted by value (integers sorted numerically), stability is irrelevant — equal integers are identical. For objects sorted by one field (sorting users by last name while preserving registration order among same-name users), stability is critical.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Equal elements are not identical: two elements with the same sort key may differ in other fields.
2. Stability preserves the information in those other fields' ordering — it's information-conserving for the unsorted dimensions.
3. Making any sort stable: augment each element with its original index `(key, original_index)`. Use `original_index` as tiebreaker. This increases key size by 1 field but guarantees stability.

DERIVED DESIGN:
**Why MergeSort is naturally stable:**
When merging two sorted halves, if `left[i]` and `right[j]` have equal keys, MergeSort takes from `left` first (left index is earlier in original array). This preserves relative order.

**Why QuickSort is naturally unstable:**
During partitioning, equal elements can be swapped past each other relative to the pivot. There's no natural mechanism to preserve original order of equal elements without additional tracking.

**Multi-key sorting via stable sort:**
Sort by field K1 first (stable), then by K2 (stable). Elements with equal K2 retain their K1 order from the first sort. Generalizes: sort by K1, K2, ..., Kn from least significant to most significant, each sort stable. Final order: lexicographic by (Kn, ..., K2, K1).

THE TRADE-OFFS:
Gain: Compositional multi-key sorting; predictable ordering; preserves original order for equal elements.
Cost: Stable sorts typically require O(N) extra space (MergeSort). Augmentation approach (+original_index) increases comparison key size.

---

### 🧪 Thought Experiment

SETUP:
Sort student records by grade (A, B, C, D) who are already ordered by name (alphabetical) within each grade.

WHAT HAPPENS WITH UNSTABLE SORT (HeapSort):
Input: [Alice-A, Bob-A, Carol-B, Dave-B]. Sort by grade. HeapSort may swap Alice and Bob (both grade A) while building the heap. Output: [Bob-A, Alice-A, Dave-B, Carol-B]. The alphabetical ordering within grades is destroyed.

WHAT HAPPENS WITH STABLE SORT (MergeSort):
Input: [Alice-A, Bob-A, Carol-B, Dave-B]. Sort by grade. MergeSort preserves equal elements' relative order. Output: [Alice-A, Bob-A, Carol-B, Dave-B]. Alphabetical order within grades maintained — you get a "free" secondary sort.

THE INSIGHT:
A stable sort on grade gives you "sorted by grade, then alphabetically by name" — for free — because the input was already alphabetically sorted. This is the foundation of multi-key radix sort: by sorting on each key from least significant to most significant using a stable sort, you build a multi-key sorted order without a multi-key comparator.

---

### 🧠 Mental Model / Analogy

> Stable sorting is like sorting a deck of playing cards: if two cards have the same value (say, both are 7s), you keep them in their original left-to-right order. An unstable sort might swap the 7♠ and 7♥ without reason. A stable sort guarantees: "I only moved cards when necessary — I never disturbed the original order otherwise."

"Two 7s" → two elements with equal sort key
"Original left-to-right order" → original array order
"Stable: keep 7♠ before 7♥" → stable sort preserves relative order
"Unstable: might swap 7s" → unstable sort has no guarantee for equal keys

Where this analogy breaks down: In practice, playing cards with the same rank are interchangeable (suit is visible but secondary). The analogy works when the cards have hidden information beyond their face value that determines their "true" position.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Stable sorting means ties are broken by keeping the original order. If two items are "equal" by the sort rule, whichever came first in the input comes first in the output. No one gets bumped without reason.

**Level 2 — How to use it (junior developer):**
Check stability before choosing sort: Java `Arrays.sort(Object[])` is stable (TimSort). Java `Arrays.sort(int[])` is not guaranteed stable (dual-pivot QuickSort on primitives). Python `sorted()` and `.sort()` are stable. When sorting by multiple keys: sort by secondary key first (stable), then primary key (stable). Or use custom `Comparator` with explicit tiebreaking by secondary field.

**Level 3 — How it works (mid-level engineer):**
Java's `Arrays.sort(int[])` uses dual-pivot QuickSort — unstable but fast (O(N log N)). `Arrays.sort(Object[])` uses TimSort — stable and O(N log N). The difference exists because for primitives, "equal" integers are truly identical (no other fields to preserve); for objects, equal compareTo values may differ in hidden fields. TimSort is a hybrid MergeSort+InsertionSort that is stable because MergeSort's merge step takes from the left half on ties.

**Level 4 — Why it was designed this way (senior/staff):**
Stability was a formal requirement in database sorting (SQL `ORDER BY` with multiple columns), which drove the adoption of TimSort in JDK 1.7 (replacing MergeSort for objects) and Python. TimSort achieves stability by exploiting "runs" (already-sorted subsequences) common in real-world data; it merges runs using stable merge. The cost: O(N) extra space for the merge buffer. For in-place stable sorting, algorithms like WikiSort and BlockSort achieve O(1) extra space with a more complex implementation. Radix sort requires stability to be correct: without a stable counting sort as the inner primitive, the radix sort invariant breaks down entirely.

---

### ⚙️ How It Works (Mechanism)

**MergeSort stability (key step):**

```
┌────────────────────────────────────────────────┐
│ Merge: left=[Bob-A, Carol-A], right=[Alice-A]  │
│                                                │
│ Compare left[0]="Bob-A" with right[0]="Alice-A"│
│   Keys equal (both grade A)                    │
│   STABLE: take from LEFT first → Bob written  │
│   (Bob was earlier in original array than Alice)│
│                                                │
│ Compare left[1]="Carol-A" with right[0]="Alice-A"│
│   Keys equal                                   │
│   STABLE: take from LEFT → Carol written       │
│                                                │
│ Remaining: right[0]="Alice" → Alice written    │
│                                                │
│ Result: [Bob-A, Carol-A, Alice-A]              │
│   Original relative order of equal elements ✓  │
└────────────────────────────────────────────────┘
```

**Multi-key sort (Least Significant Digit first):**

```
┌────────────────────────────────────────────────┐
│ Sort (grade, salary) by LSB-first method       │
│ Input: [(A,50k,Alice),(B,80k,Bob),(A,80k,Carol)]│
│                                                │
│ Step 1: stable sort by salary                  │
│ [(A,50k,Alice),(A,80k,Carol),(B,80k,Bob)]       │
│                                                │
│ Step 2: stable sort by grade                   │
│ Grade-A: [(A,50k,Alice),(A,80k,Carol)]  ← order│
│            preserved from step 1              │
│ Grade-B: [(B,80k,Bob)]                         │
│                                                │
│ Result: [(A,50k,Alice),(A,80k,Carol),(B,80k,Bob)]│
│ Sorted by (grade ASC, salary ASC) ✓            │
└────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Multi-field sort requirement
→ Identify sort keys K1 (primary), K2 (secondary)
→ Choose STABLE sort algorithm
→ [STABLE SORT ← YOU ARE HERE]
  → Sort by K2 (secondary) first
  → Sort by K1 (primary) second (stable → K2 preserved within K1-equal groups)
→ Result: sorted by K1, equal K1 → sorted by K2
```

FAILURE PATH:
```
Unstable sort used for multi-key sort
→ Equal-K1 elements have wrong K2 order
→ Database query results inconsistent (non-deterministic order)
→ Radix sort produces wrong sorted order (inner sort not stable)
→ Diagnostic: check with test where equal keys have different secondary fields
→ Fix: replace sort with stable variant (TimSort, MergeSort)
```

WHAT CHANGES AT SCALE:
For 10-billion-row database sorts (external sort), stability requires merge-based external sort (not in-memory QuickSort). TimSort adapted for external merge is used in most database systems and Hadoop. The O(N) extra space for stability becomes significant: 10B rows × 100 bytes = 1TB extra space. PostgreSQL, MySQL use merge sort for large sorts to guarantee stability and ordering.

---

### 💻 Code Example

**Example 1 — Java: stable vs unstable sort:**
```java
// Stable: Arrays.sort(Object[]) uses TimSort
Employee[] employees = ...;
// Sort by salary (stable: preserves department order within same salary)
Arrays.sort(employees,
    Comparator.comparingInt(Employee::getSalary));

// Unstable: Arrays.sort(int[]) uses DualPivotQuickSort
int[] arr = {3, 1, 4, 1, 5, 9, 2, 6};
Arrays.sort(arr); // unstable, but int values are identical if equal
```

**Example 2 — Multi-key sort via stable sort composition:**
```java
// Goal: sort by (department, salary) — stable composition
Employee[] employees = ...;

// Step 1: sort by salary (secondary key, less significant)
Arrays.sort(employees,
    Comparator.comparingInt(Employee::getSalary));

// Step 2: sort by department (primary key, more significant)
// Stability preserves salary order within same department
Arrays.sort(employees,
    Comparator.comparing(Employee::getDepartment));

// Result: sorted by department; within same dept: sorted by salary
```

**Example 3 — Multi-key via single comparator (cleaner):**
```java
// Direct approach: define full comparator
Arrays.sort(employees,
    Comparator.comparing(Employee::getDepartment)
              .thenComparingInt(Employee::getSalary));
// This is equivalent to the two-step stable sort above
```

**Example 4 — Making QuickSort stable (augmentation):**
```java
// Add original index as tiebreaker
class IndexedEmployee {
    Employee emp;
    int originalIndex;
}
// Sort with tiebreaker:
Arrays.sort(indexed,
    Comparator.comparing((IndexedEmployee ie) ->
        ie.emp.getDepartment())
    .thenComparingInt(ie -> ie.originalIndex)); // stable!
// Cost: O(N) extra space for index tracking
```

---

### ⚖️ Comparison Table

| Algorithm | Stable | Time | Space | Notes |
|---|---|---|---|---|
| **MergeSort** | Yes | O(N log N) | O(N) | Natural stable sort |
| **TimSort** | Yes | O(N log N) | O(N) | Java/Python default for objects |
| **InsertionSort** | Yes | O(N²) | O(1) | Stable, in-place; good for small N |
| **BubbleSort** | Yes | O(N²) | O(1) | Stable but impractical |
| **CountingSort** | Yes | O(N+K) | O(K) | Stable when implemented correctly |
| **HeapSort** | No | O(N log N) | O(1) | In-place, no stability |
| **QuickSort** | No | O(N log N) avg | O(log N) | Unstable; fastest in practice |
| **SelectionSort** | No | O(N²) | O(1) | Unstable, impractical |

How to choose: Use TimSort (Java default for objects) for most multi-key or order-preserving sorts. Use counting/radix sort for small integer key ranges. Use QuickSort for single-key primitive sorts where stability is irrelevant.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All Java sorts are stable | `Arrays.sort(int[])` and other primitive arrays use DualPivotQuickSort — UNSTABLE. `Arrays.sort(Object[])` and `Collections.sort` use TimSort — STABLE. Primitives are equal only if identical, so instability is unobservable; for objects it matters. |
| Stability matters only when duplicates exist | Stability matters whenever sort keys might be equal while elements differ in other properties. Even with unique records, if records have multiple fields, sorting by one field may give equal "keys" for different records. |
| Radix sort is inherently stable | Radix sort DEPENDS on stability of its inner counting sort. If the inner sort is unstable, radix sort produces wrong results. Stability is the foundational requirement. |
| Making a sort stable requires O(N log N) extra work | The augmentation approach (add original index as tiebreaker) adds O(N) extra space but no extra comparisons. TimSort is stable without explicit tiebreaking via its merge step design. |

---

### 🚨 Failure Modes & Diagnosis

**1. Using unstable sort for multi-key sort by composition**

Symptom: Employees sorted by department but salary order within department is random, not correct.

Root Cause: Each `Arrays.sort(int[])` call disrupts the previous sort's equal-element ordering. Results are non-deterministic.

Diagnostic:
```java
// Test: sort by salary then department
// Expected: within each dept, employees sorted by salary
// If salaries within dept are scrambled: unstable sort used
```

Fix: Replace with `Arrays.sort(Object[], Comparator)` (TimSort, stable). Or compose with `thenComparingInt` in a single `Comparator`.

Prevention: Never use primitive array sort for multi-key object sorting. Use `Comparator.comparing().thenComparing()`.

---

**2. Radix sort using unstable inner sort**

Symptom: Radix sort on integer sequences produces incorrect sorted order even for small N.

Root Cause: Inner counting sort lacks stability (updates count array without preserving order).

Diagnostic:
```java
// Test input: [321, 123, 231] (digit sort by units)
// Expected intermediate: [321, 231, 123] (sort by units: 1,1,3)
// If 321 and 231 are swapped: inner sort is unstable
```

Fix: Implement counting sort with right-to-left element placement:
```java
// WRONG (unstable): fill left-to-right
for (int x : input) output[count[digit(x, d)]++] = x;
// CORRECT (stable): compute prefix sums, fill from end
for (int i = n-1; i >= 0; i--)
    output[--prefixSum[digit(input[i], d)]] = input[i];
```

Prevention: Always implement radix sort's inner counting sort with right-to-left placement for stability.

---

**3. Non-deterministic sort results in production database queries**

Symptom: `ORDER BY` in MySQL returns different row orders for equal-key rows between identical queries; pagination breaks (page 2 shows records from page 1).

Root Cause: Without a stable sort or a unique tiebreaker, equal-key rows have non-deterministic order that changes between queries.

Diagnostic:
```sql
-- Check if ORDER BY has a unique tiebreaker:
SELECT * FROM users ORDER BY department;
-- If department is non-unique, no stable order guaranteed
-- Fix: add a unique tiebreaker
SELECT * FROM users ORDER BY department, id;
```

Fix: Always include a unique column (e.g., `id`) as the final tiebreaker in SQL `ORDER BY` clauses.

Prevention: Lint SQL queries to require unique tiebreaker in `ORDER BY`; document this requirement in query guidelines.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Sorting Algorithms` — Stability is a property of sorting algorithms; understanding how different algorithms sort is prerequisite.
- `Array` — Sorting operates on arrays; understanding in-place vs out-of-place affects stability trade-offs.
- `Time Complexity / Big-O` — Understanding that stable sorts (MergeSort O(N log N)) and unstable sorts (QuickSort O(N log N)) have same asymptotic complexity helps explain the practical choice.

**Builds On This (learn these next):**
- `Radix Sort` — Entirely depends on stable counting sort as its inner primitive; stability is not optional.
- `Database ORDER BY` — SQL stability semantics: without stable sort, pagination and multi-column ordering break.

**Alternatives / Comparisons:**
- `MergeSort` — The canonical stable sort; O(N log N) with O(N) space.
- `QuickSort` — Canonical unstable sort; O(N log N) average with O(log N) space; faster in practice for single-key sorts.
- `TimSort` — Hybrid MergeSort+InsertionSort; stable, adaptive (fast for partially sorted data); default in Java and Python.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Property: equal elements keep their       │
│              │ original relative order after sorting     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-key sorting breaks without stability;│
│ SOLVES       │ equal elements' secondary order scrambled │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Stable sort makes multi-key sort composable:│
│              │ sort LSB first, MSB last → correct LSD    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sorting objects with multiple fields;     │
│              │ preserving insertion order among equal keys│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sorting primitives for raw speed (unstable │
│              │ QuickSort is faster); stability irrelevant│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Stability guarantees vs O(N) extra space  │
│              │ for MergeSort; TimSort minimises overhead  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ties stay in original order"             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TimSort → Radix Sort → DB ORDER BY        │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Radix Sort is O(N×K) where K is the number of digits (or bit groups). It sorts N k-digit numbers in linear time for fixed K — beating O(N log N) comparison sort. Yet it requires stability of the inner counting sort. Trace a specific failure: given [312,132,213], perform radix sort by units digit. What incorrect output results if the inner sort is unstable (swaps equal-digit elements)? Then show the correct stable output. Explain why this failure generalises: any instability in the inner sort propagates to global incorrectness regardless of how many digits remain to process.

**Q2.** TimSort is the production sort in Java (`Arrays.sort(Object[])`) and Python. It detects "runs" (already-sorted subsequences) in the input and merges them. For nearly-sorted input of N=10,000 elements with 100 already-sorted runs of length ~100, TimSort runs in O(N log R) ≈ O(N × 7) comparisons (R=100 runs) instead of O(N log N) = O(N × 13). Compare this to MergeSort on the same input (O(N log N) always). What real-world data characteristic makes TimSort win over pure MergeSort in practice, and why is Python's `list.sort()` benchmarked faster than pure Python MergeSort implementations on typical data?

