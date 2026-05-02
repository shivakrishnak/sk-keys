---
layout: default
title: "Two Pointer"
parent: "Data Structures & Algorithms"
nav_order: 69
permalink: /dsa/two-pointer/
number: "0069"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, Sorting Algorithms, Time Complexity / Big-O
used_by: Sliding Window, Three Sum, Container With Most Water
related: Sliding Window, Binary Search, Hash Map
tags:
  - algorithm
  - intermediate
  - pattern
  - datastructure
  - performance
---

# 069 — Two Pointer

⚡ TL;DR — Two Pointer uses two indices that move toward (or away from) each other through a sorted array, solving pair/partition problems in O(N) instead of O(N²).

| #069 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, Sorting Algorithms, Time Complexity / Big-O | |
| **Used by:** | Sliding Window, Three Sum, Container With Most Water | |
| **Related:** | Sliding Window, Binary Search, Hash Map | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Find all pairs in a sorted array `[1, 2, 3, 4, 6]` that sum to target 6. The naive approach checks every pair: (1,2), (1,3), (1,4), (1,6), (2,3), (2,4), (2,6), (3,4), (3,6), (4,6) — 10 pairs for 5 elements, O(N²). For N=10,000 elements, that's 50 million pair checks.

**THE BREAKING POINT:**
O(N²) brute-force pair enumeration is too slow for large arrays. Each new element adds N more checks. At N=10⁶, it's one trillion comparisons — seconds become hours.

**THE INVENTION MOMENT:**
If the array is sorted, two observations unlock O(N): (1) if `arr[left] + arr[right] > target`, the sum is too large — move `right` left to reduce it. (2) if sum < target, move `left` right to increase it. These two moves cover all useful pairs in a single left-to-right + right-to-left sweep. Each element is visited at most once by each pointer: O(N) total. This is exactly why **Two Pointer** was created.

---

### 📘 Textbook Definition

The **Two Pointer** technique uses two index variables (`left` and `right`) to traverse a data structure (typically a sorted array or string) in a coordinated manner — either converging from opposite ends, moving in the same direction at different speeds, or partitioning. It reduces O(N²) pair-enumeration problems to O(N) by exploiting a monotonicity property: moving a pointer in one direction either increases or decreases the value of interest, enabling deterministic pruning of impossible cases.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Start from both ends and move inward based on whether the current combination is too large or too small.

**One analogy:**
> Imagine two people starting at opposite ends of a seesaw. If the seesaw tips left (sum too small), the left person moves right. If it tips right (sum too large), the right person moves left. They converge to the balance point (target) without checking every possible combination.

**One insight:**
Two Pointer only works reliably when there is a clear **monotonicity property**: moving a pointer in one direction guarantees a predictable change in the result (larger or smaller). Sorted arrays provide this. Unsorted arrays do not — moving `left` right in an unsorted array might increase or decrease the sum unpredictably, breaking the pruning logic.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Pointers `left` and `right` define the current candidate pair/window.
2. A **decision rule** determines which pointer to move: move the pointer that can improve the current value toward the target.
3. Each pointer moves at most N times total → O(N) time.

**DERIVED DESIGN:**
The key insight is that sorted arrays provide a total order: `arr[i] ≤ arr[i+1]`. This means:
- Moving `left` right **increases** the minimum element of any pair containing `left`.
- Moving `right` left **decreases** the maximum element of any pair containing `right`.

These two operations cover all "interesting" pairs. No pair is missed because: if `arr[left] + arr[right] > target`, any pair involving `right` with a smaller `left` value would still exceed target (since array is sorted). The current `right` can be safely excluded.

**Variants:**
- **Converging (opposite direction):** Left starts at 0, right at N-1. Used for pair-sum, palindrome check, container with most water.
- **Same direction (fast/slow):** Both start at 0, one advances faster. Used for Floyd's cycle detection, removing duplicates, finding middle of linked list.
- **Partition (Lomuto/Hoare):** Used in Quicksort partitioning.

**THE TRADE-OFFS:**
**Gain:** O(N) instead of O(N²) for problems with monotonicity.
**Cost:** Requires sorted array for converging variant — O(N log N) sort overhead; doesn't directly find ALL pairs (needs modification for that).

---

### 🧪 Thought Experiment

**SETUP:**
Sorted array `[1, 2, 3, 4, 6]`, target = 6. Find pair summing to 6.

WITHOUT TWO POINTER:
Check (1+2=3<6), (1+3=4<6), (1+4=5<6), (1+6=7>6), (2+3=5<6), (2+4=6✓). Found but checked 6 pairs. For all pairs: 10 total.

WITH TWO POINTER:
left=0 (val=1), right=4 (val=6). Sum=7 > 6 → move right left. right=3 (val=4). Sum=5 < 6 → move left right. left=1 (val=2). Sum=6 = target ✓ Found! Only 3 steps.

**THE INSIGHT:**
When sum > target, the current `right` value is too large for any remaining `left` position — it can be discarded. This prunes entire columns of the pair matrix. When sum < target, current `left` is too small for any remaining `right` — prune entire rows. This transforms an O(N²) grid search into an O(N) diagonal walk.

---

### 🧠 Mental Model / Analogy

> Two Pointer is like finding the right temperature for a shower. Start with cold on the left tap (minimum), hot on the right (maximum). Water too cold? Turn up heat (move left→). Too hot? Turn down heat (move right←). You converge to the perfect temperature without testing every hot/cold combination.

- "Cold tap position" → left pointer
- "Hot tap position" → right pointer
- "Water temperature" → current pair sum / value
- "Too cold → turn up heat" → sum < target → left++
- "Too hot → turn down" → sum > target → right--
- "Perfect temperature" → found target pair

Where this analogy breaks down: Tap positions are continuous; array indices are discrete. Also, a tap analogy implies one pair of values; Two Pointer can find multiple pairs by continuing after a match (with appropriate increments).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Two Pointer puts one finger at the start and one at the end of a sorted list. Based on whether the combination is too big or too small, move one finger inward. They meet in the middle having checked every useful combination — much faster than checking every possible pair.

**Level 2 — How to use it (junior developer):**
Template: `left=0, right=n-1`. Loop `while left < right`. Compute value from `arr[left]` and `arr[right]`. If value == target: record result, move both. If value < target: `left++`. If value > target: `right--`. Prerequisite: array must be sorted. When to use: pair/triplet sum problems, checking palindromes, two-pointer partition.

**Level 3 — How it works (mid-level engineer):**
For Three Sum (find all triplets summing to 0): fix the first element `i`, then apply two-pointer on `[i+1..n-1]` for pairs summing to `-arr[i]`. Total: O(N²). For Container With Most Water: two pointers converge, always moving the shorter height side (since moving the taller side can only decrease or maintain area). For linked list cycle detection (Floyd's): slow pointer advances 1, fast pointer advances 2; if they meet, a cycle exists.

**Level 4 — Why it was designed this way (senior/staff):**
Two Pointer is essentially an application of the **monotone function** observation: in a sorted array, all linear functions of sub-arrays are monotone. This connects to the broader theory of "pruning by dominance" in search algorithms. The same principle underlies binary search (half the search space per step), and Two Pointer can be seen as binary search extended to pairs. In computational geometry, Two Pointer is the foundation of algorithms on convex hulls and rotating calipers — finding antipodal pairs in O(N) by exploiting the circular monotonicity of a convex polygon's vertices.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────┐
│ Converging Two Pointer: Pair Sum           │
│                                            │
│  left = 0, right = n - 1                  │
│                                            │
│  while left < right:                       │
│    sum = arr[left] + arr[right]            │
│    if sum == target:                       │
│      → record (left, right)               │
│      left++; right--                       │
│    else if sum < target:                   │
│      left++   ← need bigger sum           │
│    else: (sum > target)                    │
│      right--  ← need smaller sum          │
└────────────────────────────────────────────┘
```

**Why each pointer moves at most N times:**
`left` only moves right (increases). `right` only moves left (decreases). Both start within [0, N-1] and can each move at most N-1 times. Total moves ≤ 2N = O(N).

**Handling duplicates:**
After finding a valid pair `(left, right)`, skip all duplicates:
```java
while (left < right && arr[left] == arr[left+1]) left++;
while (left < right && arr[right] == arr[right-1]) right--;
left++; right--;
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Unsorted input array
→ Sort array O(N log N)
→ [TWO POINTER ← YOU ARE HERE]
  → Initialize left=0, right=N-1
  → Compare arr[left]+arr[right] vs target
  → Move pointer per decision rule
  → Collect results
→ Return all valid pairs/result
```

**FAILURE PATH:**
```
Applied to unsorted array
→ Decision rule (left++ or right--) based on
  sum comparison is no longer valid
→ Wrong pairs returned or pairs missed
→ Debug: sort first, verify for small N
```

**WHAT CHANGES AT SCALE:**
For N=10⁸, Two Pointer's O(N) is 10⁸ operations — feasible in ~0.1 seconds. The sort step (O(N log N)) dominates if input is unsorted: ~2.7 billion comparisons. If input arrives pre-sorted (e.g., streaming ordered data), Two Pointer runs in pure O(N) — optimal.

---

### 💻 Code Example

**Example 1 — Two Sum (sorted array):**
```java
int[] twoSum(int[] arr, int target) {
    int left = 0, right = arr.length - 1;
    while (left < right) {
        int sum = arr[left] + arr[right];
        if (sum == target) {
            return new int[]{left, right};
        } else if (sum < target) {
            left++;
        } else {
            right--;
        }
    }
    return new int[]{-1, -1}; // not found
}
```

**Example 2 — Three Sum (all unique triplets summing to 0):**
```java
List<List<Integer>> threeSum(int[] nums) {
    Arrays.sort(nums);
    List<List<Integer>> result = new ArrayList<>();
    for (int i = 0; i < nums.length - 2; i++) {
        // Skip duplicate first elements
        if (i > 0 && nums[i] == nums[i-1])
            continue;
        int left = i + 1, right = nums.length - 1;
        while (left < right) {
            int sum = nums[i]+nums[left]+nums[right];
            if (sum == 0) {
                result.add(Arrays.asList(
                    nums[i], nums[left], nums[right]));
                // Skip duplicates
                while (left<right &&
                   nums[left]==nums[left+1]) left++;
                while (left<right &&
                   nums[right]==nums[right-1]) right--;
                left++; right--;
            } else if (sum < 0) {
                left++;
            } else {
                right--;
            }
        }
    }
    return result;
}
```

**Example 3 — Container With Most Water:**
```java
int maxWater(int[] height) {
    int left = 0, right = height.length - 1;
    int maxArea = 0;
    while (left < right) {
        int area = Math.min(height[left],
                            height[right])
                   * (right - left);
        maxArea = Math.max(maxArea, area);
        // Move the shorter side — moving the
        // taller side can only decrease width
        // without guaranteed height gain
        if (height[left] < height[right]) {
            left++;
        } else {
            right--;
        }
    }
    return maxArea;
}
```

**Example 4 — Linked list cycle detection (Floyd):**
```java
boolean hasCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;        // +1 step
        fast = fast.next.next;   // +2 steps
        if (slow == fast) return true;
    }
    return false;
}
```

---

### ⚖️ Comparison Table

| Approach | Time | Space | Requires Sorted | Best For |
|---|---|---|---|---|
| **Two Pointer** | O(N) | O(1) | Yes (converging) | Sorted pair/partition problems |
| HashMap | O(N) | O(N) | No | Unsorted pair sum, complement lookup |
| Brute Force | O(N²) | O(1) | No | Reference/verification only |
| Binary Search | O(N log N) | O(1) | Yes | Single-target search, not pairs |

How to choose: Use Two Pointer for sorted arrays when you need O(N) with O(1) space. Use HashMap when the array is unsorted and O(N) space is acceptable. Brute force only for correctness testing.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Two Pointer always requires a sorted array | The converging variant requires sorted input. The fast/slow (same direction) variant works on unsorted arrays/linked lists for cycle detection, middle finding, etc. |
| Two Pointer finds ALL pairs in O(N) | It finds pairs AND all pairs can be found in O(N), but duplicate handling requires careful increment logic — careless code may report duplicates |
| Two Pointer and Sliding Window are the same | Both use two pointers but have different semantics: converging two-pointer closes inward for pair problems; sliding window maintains a variable-size subarray for contiguous-range problems |
| Moving either pointer works | The decision of WHICH pointer to move is determined by the problem's monotonicity. For pair sum: move left if sum too small; move right if too large. Getting this wrong produces incorrect results |

---

### 🚨 Failure Modes & Diagnosis

**1. Applied to unsorted array — wrong results**

**Symptom:** Some valid pairs are missed or invalid pairs are reported.

**Root Cause:** The decision rule `sum < target → left++` assumes moving `left` right increases the sum. This only holds for sorted arrays.

**Diagnostic:**
```java
// Compare with brute force on small test:
// arr = [4, 1, 3, 2], target = 5
// Expected pairs: (1,4), (2,3)
// Test both approaches on same input
assert twoPointer(arr,5).equals(bruteForce(arr,5));
```

**Fix:** Sort the array first: `Arrays.sort(arr)`. Or use HashMap-based approach for unsorted arrays.

**Prevention:** Document at the function entry: "// PRECONDITION: array must be sorted."

---

**2. Duplicate pairs reported for arrays with repeated values**

**Symptom:** `threeSum([0,0,0,0])` returns `[[0,0,0],[0,0,0],[0,0,0]]` instead of `[[0,0,0]]`.

**Root Cause:** After finding a valid pair, the outer/inner loops don't skip duplicate values, so the same pair is reported multiple times.

**Diagnostic:**
```java
assert threeSum(new int[]{0,0,0,0}).size() == 1
    : "Duplicate triplets returned";
```

**Fix:** After recording a match, skip duplicate left and right values before moving pointers.

**Prevention:** Always add duplicate-skip logic when dealing with arrays that may contain repeated values.

---

**3. Off-by-one: using `left <= right` instead of `left < right`**

**Symptom:** Same element used twice (e.g., pair `(3, 3)` using `arr[2]` twice when `arr = [3, ...]`).

**Root Cause:** With `left <= right`, when left == right both pointers point to the same element — effectively using it twice.

**Fix:** Use `while (left < right)` (strict).

**Prevention:** The loop invariant for converging Two Pointer requires two **distinct** elements: left < right strictly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — Two Pointer operates on arrays; understand random access and indexing.
- `Sorting Algorithms` — the converging variant requires sorted input; know when to sort.

**Builds On This (learn these next):**
- `Sliding Window` — a generalisation of Two Pointer to variable-size subarrays; both pointers move in the same direction.
- `Three Sum / K-Sum` — combines outer loop with inner Two Pointer; reduces K-sum to O(N^(K-1)).

**Alternatives / Comparisons:**
- `HashMap` — O(N) time for unsorted arrays; trades O(1) space for O(N); no sort required.
- `Binary Search` — O(log N) per query on sorted arrays; use when the complement of each element is searched independently.

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two indices moving coordinately through   │
│              │ sorted data to find pairs/partitions      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ O(N²) brute-force pair search on sorted   │
│ SOLVES       │ arrays — reduce to O(N) via monotonicity  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ In sorted arrays, sum-too-large means     │
│              │ right pointer's value is exhausted        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Pair/triplet sum on sorted array,         │
│              │ palindrome check, partition problems      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Unsorted data (use HashMap); need to find │
│              │ index (not value) in original array       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(N) time, O(1) space vs sorting overhead │
│              │ required (O(N log N) if not pre-sorted)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Start from both ends, move the one that  │
│              │  needs to change"                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sliding Window → Three Sum → K-Sum        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Two Pointer technique is guaranteed to find all valid pairs in a sorted array in O(N). Prove this more rigorously: show that no valid pair `(i, j)` with `i < j` is ever skipped by the algorithm. Specifically, consider the state when `left = i'` and `right = j`; if `arr[i'] + arr[j] > target`, the algorithm moves `right--`. Under what condition could a valid pair `(i'', j)` with `i'' > i'` still exist? What does this tell you about the completeness guarantee?

**Q2.** Container With Most Water uses Two Pointer with the rule "move the shorter side." Prove this greedy rule is correct: show that for any pair `(left, right)`, if `height[left] < height[right]`, no pair `(left, right')` with `right' < right` can have greater area than the best pair containing a `left' > left`. How does this proof use the monotonicity of area as a function of the pointer positions, and where does it break down if heights are modified mid-algorithm?

