---
id: DSA-038
title: Sliding Window Technique
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-008, DSA-037
used_by: DSA-051
related: DSA-037, DSA-041
tags:
  - algorithms
  - sliding-window
  - array
  - string
  - subarray
  - o-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/dsa/sliding-window-technique/
---

## TL;DR

The sliding window expands and contracts a subarray window
rather than recomputing from scratch - converting O(n²)
subarray/substring problems into O(n).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-038 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, sliding-window, subarray, O(n) |
| **Prerequisites** | DSA-008, DSA-037 |

---

### The Problem This Solves

"Find the maximum sum subarray of length k" - naive: compute
sum of each k-length window = O(n*k). Sliding window:
move window one step at a time, subtract the leaving element
and add the arriving element = O(n) total. One pass.

---

### Textbook Definition

The sliding window technique maintains a "window" (range
[left, right]) over a sequence. The window expands rightward
and shrinks leftward based on a condition. Fixed window:
size k stays constant. Variable window: size adjusts based
on a constraint (e.g., no duplicates, sum ≤ limit).
All subarray/substring problems with a contiguous constraint
are candidates.

---

### Understand It in 30 Seconds

Max sum subarray of length 3 in [2, 1, 5, 1, 3, 2]:

```
Window [2,1,5] = 8
       slide →
Window [1,5,1] = 7  (subtract 2, add 1)
       slide →
Window [5,1,3] = 9  ← max
       slide →
Window [1,3,2] = 6

O(n) - each element added and removed once
```

---

### How It Works

**Fixed window (sum of k consecutive):**

```java
int maxSumSubarray(int[] arr, int k) {
    int windowSum = 0, maxSum = 0;
    // Build first window
    for (int i = 0; i < k; i++) windowSum += arr[i];
    maxSum = windowSum;

    // Slide window: add right, remove left
    for (int right = k; right < arr.length; right++) {
        windowSum += arr[right] - arr[right - k];
        maxSum = Math.max(maxSum, windowSum);
    }
    return maxSum;
}
// O(n) time, O(1) space
```

**Variable window (longest substring without repeating chars):**

```java
int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> lastSeen = new HashMap<>();
    int maxLen = 0, left = 0;

    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        // If c seen and it's inside current window, shrink
        if (lastSeen.containsKey(c) && lastSeen.get(c) >= left) {
            left = lastSeen.get(c) + 1;  // shrink window
        }
        lastSeen.put(c, right);
        maxLen = Math.max(maxLen, right - left + 1);
    }
    return maxLen;
}
// O(n) time, O(k) space where k = charset size
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Sliding window only works on sorted arrays" | Works on any array; sorting is not required for most window problems |
| "Sliding window requires both left and right pointers" | Fixed window only needs one pointer (right); left = right - k + 1 |

---

### Quick Reference Card

| Window type | Condition | Adjustment |
|------------|-----------|-----------|
| Fixed size k | Always maintain exactly k elements | right++, left = right - k |
| Variable (expand) | While constraint satisfied | right++ |
| Variable (shrink) | While constraint violated | left++ |

**Sliding window pattern:** "All subarrays of length k" or
"longest/shortest subarray satisfying condition" = sliding window.

---

### Mastery Checklist

- [ ] Can solve fixed-window problems (max sum of k elements)
- [ ] Can solve variable-window problems (longest substring
      without duplicates)
- [ ] Recognizes "subarray/substring with constraint" as
      sliding window candidates

---

### Interview Deep-Dive

**Q1 (Medium):** Minimum size subarray with sum >= target.

> Variable window. Expand right as long as sum < target.
> When sum >= target, record length and shrink from left.
> ```java
> int minSubArrayLen(int target, int[] nums) {
>     int left = 0, sum = 0, min = Integer.MAX_VALUE;
>     for (int right = 0; right < nums.length; right++) {
>         sum += nums[right];
>         while (sum >= target) {
>             min = Math.min(min, right - left + 1);
>             sum -= nums[left++];
>         }
>     }
>     return min == Integer.MAX_VALUE ? 0 : min;
> }
> ```
> O(n) - each element added and removed at most once.
