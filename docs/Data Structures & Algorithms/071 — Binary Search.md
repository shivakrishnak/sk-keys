---
layout: default
title: "Binary Search"
parent: "Data Structures & Algorithms"
nav_order: 71
permalink: /dsa/binary-search/
number: "0071"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, Sorting Algorithms, Time Complexity / Big-O
used_by: Two Pointer, Sliding Window, Divide and Conquer
related: Two Pointer, Linear Search, Interpolation Search
tags:
  - algorithm
  - intermediate
  - datastructure
  - performance
  - pattern
---

# 071 — Binary Search

⚡ TL;DR — Binary Search halves the search space at every step, finding a target in a sorted array in O(log N) instead of O(N).

| #0071 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, Sorting Algorithms, Time Complexity / Big-O | |
| **Used by:** | Two Pointer, Sliding Window, Divide and Conquer | |
| **Related:** | Two Pointer, Linear Search, Interpolation Search | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have a dictionary with 500,000 words sorted alphabetically and need to find "pragmatic." A linear scan starts at "aardvark," checks every word one by one — on average 250,000 comparisons. At 1 million lookups per second, that's 0.25 seconds per query. In a production autocomplete system with 10,000 simultaneous users, the server is saturated.

**THE BREAKING POINT:**
O(N) linear search is unusable for large sorted datasets. The sorted order is completely ignored — every comparison provides only one bit of information ("found" or "not found"). The sorted arrangement hints at a far more powerful approach that's being wasted.

**THE INVENTION MOMENT:**
Sorting not only organises data — it creates a map. At any midpoint, you instantly know: target is in the left half or the right half. Each comparison eliminates half the remaining candidates. 500,000 elements → 19 comparisons. This is exactly why **Binary Search** was created.

---

### 📘 Textbook Definition

**Binary Search** is a divide-and-conquer search algorithm that operates on a sorted array by repeatedly halving the search space. It maintains `low` and `high` pointers defining the current candidate range; at each step it computes `mid = (low + high) / 2`, compares `arr[mid]` against the target, and eliminates the half that cannot contain the target. It finds an exact match in O(log N) time and O(1) auxiliary space (iterative), or O(log N) stack space (recursive). A pre-condition of sorted order is required.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Look at the middle, then eliminate the impossible half and repeat until found.

**One analogy:**
> Finding a name in a phone book: open to the middle. If your name comes before it alphabetically, tear out and discard the right half. Repeat with the left half. Each step removes half the book. A 1,000-page book needs at most 10 tears.

**One insight:**
Binary Search's power comes from eliminating possibilities, not from finding the answer directly. Each comparison doesn't just check one candidate — it rules out an entire half of all remaining candidates. This compounding elimination is why O(log N) grows so slowly: log₂(1,000,000,000) = 30 comparisons.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The target, if it exists, is always within `[low..high]` — the invariant is never violated.
2. Each iteration strictly reduces the search space: `high - low` decreases by at least 1 per step.
3. The array is sorted — moving left or right provides deterministic information about where the target must be.

**DERIVED DESIGN:**
Given invariant 3, at any midpoint `m`, exactly one of three things is true:
- `arr[m] == target`: found.
- `arr[m] < target`: target must be in `[m+1..high]` (sorted order guarantees nothing in `[low..m]` can equal target).
- `arr[m] > target`: target must be in `[low..m-1]`.

Each case either finds the answer or reduces the space by roughly half. Because the space decreases geometrically (÷2 each step), the process terminates in ⌈log₂(N)⌉ steps.

**Boundary subtlety — `mid = low + (high - low) / 2`:**
Using `(low + high) / 2` overflows for large indices when `low + high > Integer.MAX_VALUE`. The form `low + (high - low) / 2` is overflow-safe and identically correct.

**THE TRADE-OFFS:**
**Gain:** O(log N) search — 30 comparisons finds any element in a billion-element sorted array.
**Cost:** Requires sorted input (O(N log N) sort if unsorted). Cannot handle insertions/deletions without re-sorting (use a BST for dynamic sorted data).

---

### 🧪 Thought Experiment

**SETUP:**
Sorted array `[1, 3, 5, 7, 9, 11, 13, 15]`. Find target = 7.

**WHAT HAPPENS WITHOUT BINARY SEARCH (linear):**
- Check 1, 3, 5, 7 — found at index 3. 4 comparisons.
- For target = 15: check all 8 elements. In worst case: N comparisons.

**WHAT HAPPENS WITH BINARY SEARCH:**
- low=0, high=7. mid=3. arr[3]=7 == target. Found in 1 comparison!
- For target = 15: low=0, high=7, mid=3, arr[3]=7 < 15 → low=4.
  low=4, high=7, mid=5, arr[5]=11 < 15 → low=6.
  low=6, high=7, mid=6, arr[6]=13 < 15 → low=7.
  low=7, high=7, mid=7, arr[7]=15 == 15. Found in 4 comparisons (vs 8 linear).

**THE INSIGHT:**
Even in the worst case, Binary Search never needs more than ⌈log₂(N)⌉ steps. For N=10⁹, that's 30 comparisons regardless of where the target is. The sorted array is not just organised data — it's an implicit decision tree of depth log₂(N).

---

### 🧠 Mental Model / Analogy

> Binary Search is like the "higher or lower" guessing game for numbers 1–100. Each time the other person says "higher" or "lower," you jump to the exact middle of the remaining range — never wasting a guess. You always guess 50, then 75 or 25, then the midpoint of the survivor — found in at most 7 guesses.

- "Remaining range" → `[low..high]`
- "Midpoint guess" → `arr[mid]`
- "Higher" → `low = mid + 1`
- "Lower" → `high = mid - 1`
- "Exact match" → return `mid`
- "Number not in range" → `low > high`, return -1

Where this analogy breaks down: In the guessing game, the answer is a single integer; in Binary Search the target is compared to array values at positions. Also, the analogy doesn't capture the off-by-one subtlety of `≤ vs <` when searching for a range boundary (lower_bound / upper_bound variations).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Binary Search is the strategy of always checking the middle of what remains. If your target is smaller, look left. If larger, look right. Each check cuts the remaining search in half. It's far faster than checking every item one by one.

**Level 2 — How to use it (junior developer):**
Pre-condition: array must be sorted. Use `low = 0, high = n-1`. Loop `while (low <= high)`. Compute `mid = low + (high - low) / 2`. If `arr[mid] == target` return `mid`. If `arr[mid] < target` set `low = mid + 1`. Otherwise set `high = mid - 1`. Return -1 if loop ends. Java provides `Arrays.binarySearch(arr, target)` — returns index if found, or `-(insertionPoint + 1)` if not.

**Level 3 — How it works (mid-level engineer):**
Beyond exact-match search, Binary Search generalises to **lower_bound** (first index where `arr[i] >= target`) and **upper_bound** (first index where `arr[i] > target`). These are used for range queries, counting occurrences, and finding insertion points. The key insight: maintain the invariant "answer is in [low..high]" and keep the loop condition `while (low < high)` with careful `mid` and pointer updates. Also applicable to answer-space searches: "find the minimum capacity K such that condition(K) is true" — binary search over K instead of an array.

**Level 4 — Why it was designed this way (senior/staff):**
Binary Search embodies the divide-and-conquer principle at its simplest: a sorted array is an implicit balanced BST (arr[mid] is the root, left and right halves are subtrees). The design is optimal: information-theoretically, any comparison-based search on N items requires Ω(log N) comparisons — Binary Search achieves exactly this bound. Its limitation appears in cache performance: for extremely large arrays, linear scan of a small range may outperform binary search due to CPU cache prefetching (sequential access patterns are predicted by hardware). B-trees and database index structures solve this by grouping related nodes into pages matching cache-line size.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────┐
│ Binary Search: arr=[1,3,5,7,9,11,13,15]      │
│ target=11                                    │
│                                              │
│ Iteration 1:                                 │
│   low=0, high=7                              │
│   mid = 0 + (7-0)/2 = 3                     │
│   arr[3]=7 < 11 → low = mid+1 = 4           │
│                                              │
│ Iteration 2:                                 │
│   low=4, high=7                              │
│   mid = 4 + (7-4)/2 = 5                     │
│   arr[5]=11 == 11 → FOUND at index 5         │
│                                              │
│ Total comparisons: 2 (vs 6 linear)          │
└──────────────────────────────────────────────┘
```

**Lower Bound (first position ≥ target):**

```
┌──────────────────────────────────────────────┐
│ lower_bound: first index where arr[i] >= T   │
│                                              │
│  low=0, high=N (exclusive upper bound)       │
│  while (low < high):                         │
│    mid = low + (high-low)/2                  │
│    if arr[mid] < target:                     │
│      low = mid + 1   ← mid definitely wrong │
│    else:                                     │
│      high = mid      ← mid might be answer  │
│  return low          ← low == high == answer │
└──────────────────────────────────────────────┘
```

**Answer-Space Binary Search:**
Used when the search space is a range of integer values rather than an array. Example: "What is the minimum ship weight W such that all packages can be shipped in D days?" Binary search over W ∈ [max(packages), sum(packages)], checking feasibility for each W in O(N). Total: O(N log(sum)).

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Unsorted data arrives
→ Sort data O(N log N)    [or use pre-sorted source]
→ Store in array
→ [BINARY SEARCH ← YOU ARE HERE]
  → Query: target value
  → low=0, high=N-1
  → Halve search space each step
  → Return index or -1
→ Use index to access value or report not found
```

**FAILURE PATH:**
```
Array not sorted (or mutated after sort)
→ Binary Search returns wrong index or -1
→ Observable: correct value exists but search returns -1
→ Diagnostic: print arr[mid] at each step; verify monotone
→ Fix: sort before search; don't modify array between sort and search
```

**WHAT CHANGES AT SCALE:**
Binary Search on a 1-billion-element sorted array takes 30 comparisons, but each comparison may cause a cache miss if the array spans multiple cache lines. Modern CPUs pre-fetch sequential memory; random access patterns at log N positions across a huge array bypass prefetch. Database B-trees group ~100 keys per node, limiting to log₁₀₀(N) ≈ 5 page reads for 10⁹ records — far fewer I/O operations than 30 random cache misses.

---

### 💻 Code Example

**Example 1 — Standard binary search (exact match):**
```java
int binarySearch(int[] arr, int target) {
    int low = 0, high = arr.length - 1;
    while (low <= high) {
        // Avoid overflow: don't use (low+high)/2
        int mid = low + (high - low) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1; // not found
}
```

**Example 2 — Lower bound (first index ≥ target):**
```java
int lowerBound(int[] arr, int target) {
    int low = 0, high = arr.length;
    while (low < high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] < target) low = mid + 1;
        else high = mid; // mid is a candidate
    }
    return low; // first position where arr[i] >= target
}
```

**Example 3 — Answer-space search (minimum valid K):**
```java
// Minimum days to ship all packages within capacity W
boolean canShip(int[] weights, int D, int capacity) {
    int days = 1, load = 0;
    for (int w : weights) {
        if (load + w > capacity) { days++; load = 0; }
        load += w;
    }
    return days <= D;
}

int shipWithinDays(int[] weights, int D) {
    int low = Arrays.stream(weights).max().getAsInt();
    int high = Arrays.stream(weights).sum();
    while (low < high) {
        int mid = low + (high - low) / 2;
        if (canShip(weights, D, mid)) high = mid;
        else low = mid + 1;
    }
    return low;
}
```

**Example 4 — Rotated sorted array search:**
```java
// Array like [4,5,6,7,0,1,2] (rotated once)
int searchRotated(int[] nums, int target) {
    int low = 0, high = nums.length - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (nums[mid] == target) return mid;
        // Left half is sorted
        if (nums[low] <= nums[mid]) {
            if (target >= nums[low] && target < nums[mid])
                high = mid - 1;
            else low = mid + 1;
        } else { // Right half is sorted
            if (target > nums[mid] && target <= nums[high])
                low = mid + 1;
            else high = mid - 1;
        }
    }
    return -1;
}
```

---

### ⚖️ Comparison Table

| Approach | Time | Space | Requires Sorted | Best For |
|---|---|---|---|---|
| **Binary Search** | O(log N) | O(1) | Yes | Static sorted arrays, repeated queries |
| Linear Search | O(N) | O(1) | No | Tiny arrays, unsorted data, single queries |
| Hash Map | O(1) avg | O(N) | No | Exact-match with preloaded data |
| B-Tree Index | O(log N) disk | O(N) | Yes (DB) | Database range queries, disk-based data |
| Interpolation Search | O(log log N) avg | O(1) | Yes + uniform | Uniformly distributed data |

How to choose: Use Binary Search for sorted in-memory arrays with repeated queries. Use HashMap when O(1) lookup justifies O(N) extra space. Use B-Tree for disk-based or database scenarios where page locality matters.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `mid = (low + high) / 2` is always correct | This overflows when `low + high > Integer.MAX_VALUE`. Always use `low + (high - low) / 2`. |
| Binary Search requires `while (low <= high)` | For lower_bound/upper_bound variants, `while (low < high)` with `high = mid` (not `mid-1`) is correct and cleaner. Using `<=` with the wrong pointer update causes infinite loops. |
| Binary Search only finds exact matches | It generalises to lower_bound, upper_bound, and answer-space searches over any monotone function — not just array element equality. |
| Binary Search fails on duplicates | It works correctly even with duplicates for exact match (returns one valid index). For all occurrences, use lower_bound and upper_bound to get the range. |
| You must sort before every search | If the array is already sorted (database index, sorted log, etc.), binary search applies directly. The sort cost is O(N log N) amortized across all future queries. |

---

### 🚨 Failure Modes & Diagnosis

**1. Integer overflow in mid calculation**

**Symptom:** `mid` becomes negative for large arrays; wrong elements accessed.

**Root Cause:** `(low + high)` overflows `int` when both are close to `Integer.MAX_VALUE`.

**Diagnostic:**
```java
// Add assertion:
assert low >= 0 && high < arr.length
    : "Out of bounds: low=" + low + " high=" + high;
// Or print mid: if negative, overflow has occurred
System.out.println("mid=" + ((low + high) / 2));
```

**Fix:** Replace `(low + high) / 2` with `low + (high - low) / 2`.

**Prevention:** Always use the overflow-safe form from the start.

---

**2. Infinite loop with `while (low < high)` and wrong pointer update**

**Symptom:** Loop runs forever; `low == high` never reached.

**Root Cause:** When `low == high - 1` and `arr[mid] >= target`, setting `high = mid - 1` is wrong for lower_bound semantics. The invariant "answer is in [low..high]" is violated.

**Diagnostic:**
```bash
# Add iteration counter with assertion:
int iter = 0;
while (low < high) {
    assert ++iter < 100 : "Infinite loop detected";
    ...
}
```

**Fix:** For lower_bound, use `high = mid` (not `mid - 1`). Ensure loop makes progress: `low` must increase or `high` must decrease each iteration.

**Prevention:** Dry-run the boundary case: `low = 4, high = 5`, `mid = 4`, then trace the pointer update.

---

**3. Off-by-one in insertion index**

**Symptom:** `Arrays.binarySearch` returns a negative value; code crashes treating it as an index.

**Root Cause:** `Arrays.binarySearch` returns `-(insertionPoint + 1)` when not found. Many developers forget to check for negative return values.

**Diagnostic:**
```java
int idx = Arrays.binarySearch(arr, target);
System.out.println("result=" + idx +
    (idx < 0 ? " (not found, insert at " +
     (-idx - 1) + ")" : " (found)"));
```

**Fix:**
```java
// BAD: assumes element is always found
arr[Arrays.binarySearch(arr, 5)] = 99;

// GOOD: check before using
int idx = Arrays.binarySearch(arr, 5);
if (idx >= 0) arr[idx] = 99;
```

**Prevention:** Always check the sign of the return value from `Arrays.binarySearch`.

---

**4. Searching unsorted or partially sorted array**

**Symptom:** Correct elements exist but Binary Search returns -1 or the wrong index.

**Root Cause:** The decision rule `arr[mid] < target → low = mid + 1` is only valid if arr is sorted. On unsorted data, the target may be in the discarded half.

**Diagnostic:**
```java
// Validate sorted precondition
for (int i = 1; i < arr.length; i++)
    assert arr[i] >= arr[i-1] :
        "Not sorted at index " + i;
```

**Fix:** Sort the array before searching, or use linear search for unsorted data.

**Prevention:** Document the sorted precondition: `// PRECONDITION: arr must be sorted ascending`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — Binary Search operates on arrays; random access (O(1)) is essential to the algorithm's O(log N) claim.
- `Sorting Algorithms` — Binary Search requires sorted input; understanding why and how to sort determines when Binary Search is viable.
- `Time Complexity / Big-O` — Understanding logarithmic complexity is essential to appreciate why 30 comparisons finds anything in a billion-element array.

**Builds On This (learn these next):**
- `Divide and Conquer` — Binary Search is the simplest divide-and-conquer algorithm; understanding it paves the way for Mergesort and more complex D&C problems.
- `Two Pointer` — Often combined with Binary Search: Binary Search on sorted answers, Two Pointer to verify feasibility.
- `B-Tree` — The database generalisation of Binary Search: instead of splitting an array in half, a B-tree node holds ~100 keys per page, reducing disk I/O.

**Alternatives / Comparisons:**
- `Linear Search` — O(N) but works on unsorted data; only preferred for very small arrays or single queries on unsorted data.
- `Hash Map` — O(1) average lookup; trades O(N) space for O(1) time; no sorted order available for range queries.
- `Interpolation Search` — O(log log N) average for uniformly distributed data; uses value-proportional probing rather than midpoint.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Halve-and-eliminate search on sorted data │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ O(N) linear scan ignores sorted order;    │
│ SOLVES       │ O(log N) exploits it via midpoint probing │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Each comparison eliminates half of all    │
│              │ remaining candidates — log₂(10⁹) = 30    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Data is sorted; repeated queries needed;  │
│              │ or answer-space is monotone               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data is unsorted and sort cost isn't      │
│              │ amortized; or need O(1) point lookup      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(log N) search vs sorted precondition    │
│              │ requirement and O(N log N) sort overhead  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Always check the middle; trust the order"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lower Bound → Answer Space → B-Tree Index │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Binary Search on a sorted array runs in O(log N). Now consider a rotated sorted array (e.g., `[4,5,6,7,0,1,2]`). At each `mid`, how do you determine which half is guaranteed sorted, and how does that determination let you still eliminate half the candidates? What property of the rotated array makes this work, and what breaks if the array is rotated more than once or contains duplicates?

**Q2.** You are designing an API rate limiter that must answer "has user X exceeded N requests in the last 60 seconds?" in under 100 microseconds. You maintain a sorted timestamp log for each user. Sketch how Binary Search solves this: what is your search target, what is the monotone condition, and what is the time complexity per query when the log contains 10 million timestamps?

