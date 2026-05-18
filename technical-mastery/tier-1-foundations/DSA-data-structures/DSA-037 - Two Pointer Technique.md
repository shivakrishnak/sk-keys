---
id: DSA-037
title: Two Pointer Technique
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-008, DSA-020
used_by: DSA-038
related: DSA-038, DSA-020
tags:
  - algorithms
  - two-pointer
  - array
  - string
  - in-place
  - o-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/dsa/two-pointer-technique/
---

## TL;DR

Two pointers (left+right or slow+fast) eliminate nested
loops by processing arrays linearly - converting many O(n²)
problems into O(n) without extra space.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-037 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | algorithms, two-pointer, array, O(n) |
| **Prerequisites** | DSA-008, DSA-020 |

---

### The Problem This Solves

Two Sum on sorted array: naive = check all pairs = O(n²).
With two pointers, converge from both ends: O(n).
Detecting a cycle in linked list: naive = track all visited
nodes = O(n) space. Slow/fast pointer: O(1) space.

---

### Textbook Definition

The two pointer technique uses two indices (or references)
into a data structure, typically moving toward each other
or at different speeds (slow/fast pointers). It converts
problems that seemingly require O(n²) brute force into
O(n) by exploiting sorted order or cyclic structure.

---

### Understand It in 30 Seconds

**Two Sum (sorted array):**
```
[1, 3, 6, 8, 10, 14]  target = 14
 ^                ^
left=1          right=14
sum=15 > 14 → move right left
 ^             ^
left=1       right=10
sum=11 < 14 → move left right
    ^          ^
left=3       right=10
sum=13 < 14 → move left right
       ^       ^
left=6       right=10 → sum=16 > 14 → move right
       ^    ^
left=6    right=8 → sum=14 ✓ FOUND
```

Two comparisons eliminated all pairs in O(n).

---

### How It Works

**Pattern 1: Left-right convergence (sorted array):**

```java
// Two sum on sorted array: O(n) time, O(1) space
int[] twoSumSorted(int[] arr, int target) {
    int left = 0, right = arr.length - 1;
    while (left < right) {
        int sum = arr[left] + arr[right];
        if (sum == target) return new int[]{left, right};
        if (sum < target) left++;   // need larger sum
        else right--;                // need smaller sum
    }
    return new int[]{};
}
```

**Pattern 2: Same direction (slow/fast pointers):**

```java
// Remove duplicates from sorted array: O(n) time, O(1) space
int removeDuplicates(int[] arr) {
    if (arr.length == 0) return 0;
    int slow = 0;  // last unique position
    for (int fast = 1; fast < arr.length; fast++) {
        if (arr[fast] != arr[slow]) {
            slow++;
            arr[slow] = arr[fast];
        }
    }
    return slow + 1;  // length of deduplicated array
}

// Detect cycle in linked list (Floyd's algorithm)
boolean hasCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;           // 1 step
        fast = fast.next.next;      // 2 steps
        if (slow == fast) return true;  // cycle!
    }
    return false;
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Two pointers only works on sorted arrays" | Slow/fast pointer works on linked lists (cycle detection) and unsorted arrays (remove duplicates by value) |
| "Two pointers always needs two different starting positions" | Slow and fast pointers start at the same position in cycle detection |

---

### Quick Reference Card

| Pattern | Starting positions | Movement | Classic use |
|---------|------------------|----------|------------|
| Converge | Opposite ends | Both inward | Two sum, palindrome |
| Same direction | Both at start | Different speeds | Remove dupes, cycle |
| Sliding window | Both at start | Both right | Substring problems |

---

### Mastery Checklist

- [ ] Can implement two-sum on sorted array with two pointers
- [ ] Can detect linked list cycle with Floyd's algorithm
- [ ] Recognizes when two pointers converts O(n²) to O(n)

---

### Interview Deep-Dive

**Q1 (Easy):** Is a string a palindrome using two pointers?

> ```java
> boolean isPalindrome(String s) {
>     int left = 0, right = s.length() - 1;
>     while (left < right) {
>         if (s.charAt(left) != s.charAt(right)) return false;
>         left++;
>         right--;
>     }
>     return true;
> }
> ```
> O(n) time, O(1) space. Compare from both ends inward.

**Q2 (Medium):** Three Sum: find all unique triplets in an
array that sum to zero.

> Sort the array O(n log n). For each element nums[i] as
> the "fixed" element, use two pointers left=i+1, right=n-1
> to find pairs summing to -nums[i]. Skip duplicates by
> advancing past equal values. Total: O(n²) - outer loop
> O(n) × inner two-pointer scan O(n). Space: O(1) excluding
> output. Without two pointers, brute force would be O(n³).
