---
layout: default
title: "Sliding Window"
parent: "Data Structures & Algorithms"
nav_order: 70
permalink: /dsa/sliding-window/
number: "0070"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, Two Pointer, Time Complexity / Big-O
used_by: Maximum Subarray, Longest Substring Without Repeating Characters, Minimum Window Substring
related: Two Pointer, Prefix Sum, Dynamic Programming
tags:
  - algorithm
  - intermediate
  - pattern
  - datastructure
  - performance
---

# 070 — Sliding Window

⚡ TL;DR — Sliding Window maintains a moving subarray of variable or fixed size, solving contiguous-range problems in O(N) instead of O(N²).

| #0070 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, Two Pointer, Time Complexity / Big-O | |
| **Used by:** | Maximum Subarray, Longest Substring Without Repeating Characters, Minimum Window Substring | |
| **Related:** | Two Pointer, Prefix Sum, Dynamic Programming | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Find the maximum sum of any subarray of length 3 in `[2, 1, 5, 1, 3, 2]`. The naive approach recalculates the sum for every starting position: (2+1+5), (1+5+1), (5+1+3), (1+3+2) — recomputing overlapping elements each time. For N=10,000 with window size K=1,000 that's 10,000 × 1,000 = 10 million additions per query.

THE BREAKING POINT:
O(N×K) brute-force recalculation is wasteful because 99% of each new window overlaps with the previous one. Every shift discards one element and adds one element — yet the naive approach throws away all previous work and restarts from scratch. At N=10⁶, K=1,000, that's one billion operations per pass.

THE INVENTION MOMENT:
The key observation: when the window slides right by one, the new sum = old sum - left element + new right element. This single O(1) update replaces K additions. One pass, O(N) total. This is exactly why **Sliding Window** was created.

### 📘 Textbook Definition

The **Sliding Window** technique maintains a contiguous subarray (the "window") defined by two pointers `left` and `right` that always satisfy `left ≤ right`. In the fixed-size variant, both pointers advance together at a fixed distance. In the variable-size variant, `right` expands the window to include new elements and `left` contracts it when a constraint is violated. Both variants process each element at most twice (once added, once removed), yielding O(N) time with O(1) to O(K) auxiliary space depending on the tracked state.

### ⏱️ Understand It in 30 Seconds

**One line:**
Move a frame across an array, updating the result by adding one element and removing another instead of recalculating everything.

**One analogy:**
> Imagine tracking the average temperature for the last 7 days. Each new day you add today's temperature and drop the eight-days-ago reading — you never re-add the 6 days in between. The "window" of 7 days slides forward one day at a time.

**One insight:**
Sliding Window only works for **contiguous** subarrays or substrings. If the problem asks about non-contiguous subsets, the window's O(1) update rule breaks down. The power comes from the fact that consecutive windows share N-1 elements: the update is incremental, not from scratch.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The window is always a contiguous range `[left..right]` of the input.
2. Every element enters the window exactly once (via `right++`) and leaves exactly once (via `left++`): O(N) total moves.
3. An **aggregation state** (sum, character count, hashmap) is maintained incrementally: updated in O(1) per pointer move.

DERIVED DESIGN:
Because the window is contiguous, the "add right element / remove left element" rule always applies. This forces two variants:
- **Fixed window (K):** `right` and `left` both advance; window size is constant. Use when the problem specifies a fixed length (`K consecutive elements`).
- **Variable window:** `right` always advances; `left` advances only when the window violates a constraint (e.g., sum exceeds target, duplicate character appears). Use when the problem asks for the longest/shortest window satisfying a condition.

THE TRADE-OFFS:
Gain: O(N) time, O(1) extra space for numeric aggregation, O(K) for character/element tracking.
Cost: Restricted to **contiguous** subarrays. Requires defining a clear "validity constraint" for variable windows. If the aggregation cannot be updated in O(1) (e.g., median of window), the classic technique requires augmentation with a sorted data structure → O(N log K).

### 🧪 Thought Experiment

SETUP:
Find the maximum sum of any contiguous subarray of exactly length 3 in `[2, 1, 5, 1, 3, 2]`.

WHAT HAPPENS WITHOUT SLIDING WINDOW:
- Window starting at index 0: 2+1+5 = 8. 3 additions.
- Window starting at index 1: 1+5+1 = 7. 3 more additions (re-adds 1 and 5).
- Window starting at index 2: 5+1+3 = 9. 3 more additions (re-adds 5 and 1).
- Window starting at index 3: 1+3+2 = 6. 3 additions.
- Total: 12 additions for 4 windows. Wasteful — elements 1 and 5 were added three times each.

WHAT HAPPENS WITH SLIDING WINDOW:
- Init: windowSum = 2+1+5 = 8. maxSum = 8.
- Slide: windowSum = 8 - 2 + 1 = 7. maxSum = 8.
- Slide: windowSum = 7 - 1 + 3 = 9. maxSum = 9.
- Slide: windowSum = 9 - 5 + 2 = 6. maxSum = 9.
- Total: 5 additions + 3 subtractions = 8 operations (vs 12). Result: 9 — correct.

THE INSIGHT:
Each slide is O(1) regardless of window size K. This transforms O(N×K) into O(N+K) ≈ O(N). The larger K is, the greater the savings — Sliding Window pays off most when windows are large.

### 🧠 Mental Model / Analogy

> Sliding Window is like a train moving along a track where each car is one element. As the train moves forward by one car length, you drop the last car from the rear and add a new car at the front. You always know the total "weight" of the train by adjusting — you never re-weigh all cars from scratch.

"Train cars" → elements in the window
"Train weight" → aggregated value (sum, count, etc.)
"Drop rear car" → remove `arr[left]`, `left++`
"Add front car" → `right++`, add `arr[right]`
"Track constraint" → validity rule (max sum, no duplicates, etc.)
"Train length" → window size (fixed or variable)

Where this analogy breaks down: A real train has a fixed length; the variable-window variant dynamically changes window size. Also, some aggregations (like median) cannot be updated in O(1) even with the analogy intact.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Sliding Window is a technique where you look at a moving section of a list — like reading a newspaper through a small frame that shifts one column at a time. Instead of re-reading the whole frame every time you move it, you just note what left your view and what entered.

**Level 2 — How to use it (junior developer):**
For fixed-size windows: compute the initial window, then loop from index K to N-1, subtracting `arr[i-K]` and adding `arr[i]`, updating your answer each step. For variable-size windows: use two pointers `left=0, right=0`; always advance `right` to expand; shrink from `left` when the window violates your constraint. Track the answer after each valid state.

**Level 3 — How it works (mid-level engineer):**
The variable-size variant relies on a "monotone" constraint: when the window becomes invalid, shrinking from `left` always moves toward validity. This works because adding an element can only make the window "more invalid" (e.g., longer, higher sum, more duplicates), and removing the leftmost element reduces the violation. The auxiliary data structure (HashMap for character counts, deque for max/min) determines whether left-pointer logic is O(1) amortized. For the sliding window maximum problem, a monotone deque (elements stored in decreasing order) is required to maintain O(N) overall.

**Level 4 — Why it was designed this way (senior/staff):**
Sliding Window is an application of the "amortized O(1) update" principle: any aggregate that can be updated by a single add/remove is a candidate. The technique dates to early text-search algorithms where substring patterns required scanning linearly without repetition. In stream processing, sliding windows are fundamental: tumbling, sliding, and session windows in Kafka Streams/Flink directly implement this pattern for real-time aggregations. The challenge at scale is state management: for a 1-hour tumbling window over 10M events/second, the state store must evict 36 billion entries per hour — the "add right, remove left" invariant translates directly to a time-ordered eviction policy.

### ⚙️ How It Works (Mechanism)

**Fixed-Size Sliding Window (sum of K consecutive elements):**

```
┌──────────────────────────────────────────────┐
│ Fixed Window: size K=3                       │
│                                              │
│ arr = [2, 1, 5, 1, 3, 2]                    │
│                                              │
│ Step 1: Init window [0..K-1]                 │
│   sum = arr[0]+arr[1]+arr[2] = 8             │
│   maxSum = 8                                 │
│                                              │
│ Step 2: Slide i from K to N-1                │
│   i=3: sum = 8 - arr[0] + arr[3]            │
│        sum = 8 - 2 + 1 = 7                  │
│   i=4: sum = 7 - arr[1] + arr[4]            │
│        sum = 7 - 1 + 3 = 9   ← new max      │
│   i=5: sum = 9 - arr[2] + arr[5]            │
│        sum = 9 - 5 + 2 = 6                  │
│                                              │
│ Result: maxSum = 9                           │
└──────────────────────────────────────────────┘
```

**Variable-Size Sliding Window (longest substring without repeating chars):**

```
┌──────────────────────────────────────────────┐
│ Variable Window: no duplicate chars          │
│                                              │
│ s = "abcabcbb"                               │
│ charCount = {}                               │
│ left = 0, maxLen = 0                         │
│                                              │
│ right=0 'a': count={a:1}. len=1             │
│ right=1 'b': count={a:1,b:1}. len=2         │
│ right=2 'c': count={a:1,b:1,c:1}. len=3     │
│ right=3 'a': a already in window!           │
│   → shrink: remove s[left=0]='a'            │
│     count={a:0,b:1,c:1}. left=1             │
│   add 'a': count={a:1,b:1,c:1}. len=3       │
│ right=4 'b': b in window!                   │
│   → shrink until b removed: left→2          │
│   ... continues                              │
│                                              │
│ Result: maxLen = 3                           │
└──────────────────────────────────────────────┘
```

**Why the shrink step works in O(N) amortized:**
`left` only ever moves right. From left=0 to left=N, that is at most N increments total across the entire algorithm — not per step. Combined with N increments of `right`, total pointer moves = 2N = O(N).

**Monotone Deque for Sliding Window Maximum:**
For finding the maximum within each window of size K, maintain a deque of indices in decreasing order of `arr[i]`. When adding `arr[right]`, pop all indices from the back where `arr[deque.back()] ≤ arr[right]`. Pop from the front if that index is outside the current window. The front always holds the maximum. Each index enters/leaves the deque once: O(N) total.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Input array (contiguous data)
→ Identify window type (fixed K or variable constraint)
→ Initialize window [0..K-1] or left=right=0
→ [SLIDING WINDOW ← YOU ARE HERE]
  → Expand right: add arr[right] to state
  → Check validity constraint
  → If violated: shrink left until valid
  → Record candidate answer
  → Advance right
→ Return best answer across all windows
```

FAILURE PATH:
```
Non-contiguous problem mistakenly uses Sliding Window
→ Shrink logic skips valid configurations
→ Wrong answer returned
→ Debug: verify problem requires contiguous subarray
→ Fix: use DP or backtracking for non-contiguous
```

WHAT CHANGES AT SCALE:
For streaming data (Kafka Streams, Flink), the sliding window maps directly to a time-based window operator where `arr[right]` is the incoming event and `arr[left]` is the event aged out of the window. At 1M events/second with a 1-minute tumbling window, state stores hold ~60M entries — LSM-tree–backed state stores (RocksDB in Flink) make eviction O(1) amortized. The algorithm is identical; the storage layer changes.

### 💻 Code Example

**Example 1 — Fixed window (max sum of K elements):**
```java
int maxSumFixedWindow(int[] arr, int k) {
    int sum = 0;
    // Build initial window
    for (int i = 0; i < k; i++) sum += arr[i];
    int maxSum = sum;
    // Slide the window
    for (int i = k; i < arr.length; i++) {
        sum += arr[i] - arr[i - k]; // add new, remove old
        maxSum = Math.max(maxSum, sum);
    }
    return maxSum;
}
```

**Example 2 — Variable window (longest substring, no repeats):**
```java
int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> count = new HashMap<>();
    int left = 0, maxLen = 0;
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        count.merge(c, 1, Integer::sum);
        // Shrink until no duplicate
        while (count.get(c) > 1) {
            char lc = s.charAt(left++);
            count.merge(lc, -1, Integer::sum);
        }
        maxLen = Math.max(maxLen, right - left + 1);
    }
    return maxLen;
}
```

**Example 3 — Minimum window substring (variable, complex constraint):**
```java
String minWindowSubstring(String s, String t) {
    Map<Character, Integer> need = new HashMap<>();
    for (char c : t.toCharArray())
        need.merge(c, 1, Integer::sum);
    int left = 0, formed = 0, required = need.size();
    Map<Character, Integer> window = new HashMap<>();
    int[] ans = {-1, 0, 0}; // length, left, right
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        window.merge(c, 1, Integer::sum);
        if (need.containsKey(c) &&
            window.get(c).equals(need.get(c))) formed++;
        while (formed == required) {
            if (ans[0] == -1 || right - left + 1 < ans[0]) {
                ans[0] = right - left + 1;
                ans[1] = left; ans[2] = right;
            }
            char lc = s.charAt(left++);
            window.merge(lc, -1, Integer::sum);
            if (need.containsKey(lc) &&
                window.get(lc) < need.get(lc)) formed--;
        }
    }
    return ans[0] == -1 ? "" :
        s.substring(ans[1], ans[2] + 1);
}
```

**Example 4 — Sliding window maximum (deque):**
```java
int[] maxSlidingWindow(int[] nums, int k) {
    Deque<Integer> dq = new ArrayDeque<>(); // stores indices
    int[] result = new int[nums.length - k + 1];
    for (int i = 0; i < nums.length; i++) {
        // Remove indices outside window
        while (!dq.isEmpty() && dq.peekFirst() < i - k + 1)
            dq.pollFirst();
        // Maintain decreasing order
        while (!dq.isEmpty() &&
               nums[dq.peekLast()] <= nums[i])
            dq.pollLast();
        dq.offerLast(i);
        if (i >= k - 1)
            result[i - k + 1] = nums[dq.peekFirst()];
    }
    return result;
}
```

### ⚖️ Comparison Table

| Approach | Time | Space | Best For |
|---|---|---|---|
| **Sliding Window** | O(N) | O(1)–O(K) | Contiguous subarray/string problems with monotone constraint |
| Brute Force (nested loops) | O(N×K) | O(1) | Verification only — never production |
| Prefix Sum | O(N) precompute, O(1) query | O(N) | Range sum queries (non-sliding, arbitrary ranges) |
| Dynamic Programming | O(N²) or O(N) | O(N) | Non-contiguous subsequences, overlapping sub-problems |
| Monotone Deque | O(N) | O(K) | Sliding window min/max efficiently |

How to choose: Use Sliding Window when the problem involves contiguous subarrays with a constraint that becomes "more violated" as the window grows and "less violated" as it shrinks. Use Prefix Sum for arbitrary range queries without a sliding constraint.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Sliding Window and Two Pointer are the same | Two Pointer solves pair problems (converging from ends); Sliding Window solves contiguous subarray problems (both pointers moving in same direction). Both use two indices but with different semantics. |
| Sliding Window only works for fixed-size windows | The variable-size variant is equally valid and more widely used — it handles "longest/shortest window satisfying condition X." |
| You can always shrink from left when constraint is violated | This only holds if adding an element makes the window strictly "more invalid" — a monotone constraint. If validity is non-monotone (e.g., exactly K distinct elements), you need a different tracking approach. |
| The time complexity is O(N²) because of the inner while loop | The inner shrink loop is O(N) amortized across the full pass — `left` moves right at most N times total, not per outer iteration. Overall: O(N). |
| Sliding Window requires sorted input | Unlike Two Pointer (converging variant), Sliding Window works on unsorted arrays. The constraint is contiguity, not ordering. |

### 🚨 Failure Modes & Diagnosis

**1. Applying sliding window to non-contiguous problems**

Symptom: Wrong answer on test cases where optimal solution skips elements.

Root Cause: Sliding Window only considers contiguous ranges. Problems like "longest increasing subsequence" require DP because the optimal subsequence may skip elements.

Diagnostic:
```bash
# Verify on small test: does brute force pick non-adjacent elements?
# arr=[3,1,4,1,5,9], does "longest increasing" skip index 1 (value 1)?
# Yes → DP needed, not Sliding Window
```

Fix: Switch to DP (`dp[i]` = best result ending at index i).

Prevention: Check problem statement — "subarray" means contiguous; "subsequence" means non-contiguous.

---

**2. Off-by-one in fixed window initialization**

Symptom: `ArrayIndexOutOfBoundsException` or first window excludes last element.

Root Cause: Loop `for (int i = 0; i < k; i++)` initializes [0..k-1]; slide starts at `i=k`. Using `i ≤ k` accidentally includes index k in init and misses a window.

Diagnostic:
```java
// Print window boundaries per iteration
System.out.println("Init window: [0.." + (k-1) + "]");
System.out.println("Slide start: i=" + k);
```

Fix: Ensure init loop is `i < k` and slide loop starts at `i = k`.

Prevention: Dry-run on a 3-element array with k=2 before submitting.

---

**3. HashMap not cleaned up in variable window**

Symptom: Produces wrong (too-long) window for strings with many duplicate characters.

Root Cause: After removing `arr[left]` from the window, the count goes to 0 but the key remains in the HashMap. Subsequent `containsKey` returns `true` for absent characters.

Diagnostic:
```java
// After left++, check: is charCount.get(lc) == 0?
// If yes, remove the key: charCount.remove(lc)
```

Fix:
```java
// BAD: leaves zero-count entries
count.put(lc, count.get(lc) - 1);

// GOOD: remove when count reaches 0
count.merge(lc, -1, Integer::sum);
if (count.get(lc) == 0) count.remove(lc);
```

Prevention: Use `count.getOrDefault(c, 0)` for lookups and remove zero-count entries.

---

**4. Monotone deque not evicting stale indices**

Symptom: Sliding window maximum returns incorrect results for later windows.

Root Cause: The deque contains an index from outside the current window `[i-k+1..i]`. The front of the deque holds a maximum from a previous window that has already slid past.

Diagnostic:
```java
// Add assertion: index at front must be >= i - k + 1
assert dq.peekFirst() >= i - k + 1 :
    "Stale index in deque: " + dq.peekFirst();
```

Fix: Add `while (!dq.isEmpty() && dq.peekFirst() < i - k + 1) dq.pollFirst();` before using the front.

Prevention: Always evict stale front-of-deque indices before reading the window maximum.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — Sliding Window operates on arrays; index arithmetic is fundamental.
- `Two Pointer` — Sliding Window is the same-direction generalization of Two Pointer; understanding two-pointer first clarifies the left/right mechanics.
- `Time Complexity / Big-O` — Understanding amortized O(N) is essential to see why the inner shrink loop doesn't make this O(N²).

**Builds On This (learn these next):**
- `Minimum Window Substring` — A classic variable-window problem requiring HashMap tracking; directly applies this technique.
- `Longest Substring Without Repeating Characters` — The canonical variable-window problem; teaches constraint management.
- `Sliding Window Maximum` — Extends Sliding Window with a monotone deque for O(N) max/min queries.

**Alternatives / Comparisons:**
- `Prefix Sum` — Also O(N) for range queries, but handles arbitrary non-overlapping ranges; doesn't require a validity constraint.
- `Dynamic Programming` — More general; handles non-contiguous problems Sliding Window cannot.
- `Segment Tree` — O(log N) per range query including updates; use when range queries are not strictly sliding.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Moving subarray with O(1) add/remove      │
│              │ updates on aggregated state               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ O(N×K) brute-force subarray scan →        │
│ SOLVES       │ reduce to O(N) via incremental updates    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Consecutive windows share N-1 elements;   │
│              │ only 1 element changes per slide          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Problem involves contiguous subarrays      │
│              │ with a monotone validity constraint        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Non-contiguous subsequences; non-monotone  │
│              │ constraints (use DP or backtracking)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N) time, O(K) space vs O(N×K) brute     │
│              │ force; requires contiguous data           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Slide the frame; don't repaint it"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Two Pointer → Prefix Sum → Monotone Deque │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** The variable Sliding Window guarantees O(N) because `left` moves right at most N times total. Now consider a Sliding Window problem where the validity constraint is "at most K distinct characters." If the input is "aabbccddee...zz" (26 pairs, K=1), trace how many total `left` moves occur. Does O(N) still hold? What changes when K approaches N/2?

**Q2.** In stream processing (Apache Kafka Streams), a 5-minute tumbling window receives 10,000 events per second. At minute 5, the window closes and a new one opens. Design the state eviction strategy: what data structure holds the window state, how do you implement the "remove left" operation for time-ordered events, and what happens to out-of-order late-arriving events that belong to the closed window?

