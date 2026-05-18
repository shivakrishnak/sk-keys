---
id: DSA-025
title: "Top 10 DSA Interview Questions - Basics"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-001, DSA-008, DSA-010, DSA-012, DSA-014, DSA-016
used_by: DSA-051
related: DSA-004, DSA-023, DSA-051
tags:
  - interview
  - review
  - fundamentals
  - basics
  - top-10
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 25
permalink: /technical-mastery/dsa/top-10-dsa-interview-questions-basics/
---

## TL;DR

The ten most commonly asked basic DSA interview questions,
with crisp answers that demonstrate understanding beyond
definitions - covering arrays, strings, hash maps, stacks,
and Big O.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-025 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | interview, review, fundamentals, top-10 |
| **Prerequisites** | DSA-001, DSA-008, DSA-010, DSA-012, DSA-014, DSA-016 |

---

### The 10 Questions

---

**Q1: What is the time complexity of HashMap.get() in Java?**

O(1) average case. HashMap uses a hash function to map keys
to buckets. If the hash function distributes keys uniformly,
each bucket has O(1) entries. Worst case O(n) if all keys
hash to the same bucket (hash collision), but Java 8+
converts long chains (>8) to balanced trees, making worst
case O(log n) per bucket.

---

**Q2: When would you use a LinkedList instead of an ArrayList?**

Almost never in modern Java code. LinkedList offers O(1)
insert/delete at head/tail but O(n) for random access.
ArrayList has O(n) insert at arbitrary position but O(1)
random access and better cache performance. The use case
for LinkedList is when you need O(1) insert/delete at
the middle of the list AND you already have a reference
to the node - rare in practice. For queue behavior,
use ArrayDeque (backed by a circular array, better cache).

---

**Q3: What is the difference between Stack and Queue?**

Stack: LIFO (Last In, First Out). Add and remove from the
same end (top). Operations: push, pop, peek.
Use cases: function call stack, undo/redo, DFS traversal.

Queue: FIFO (First In, First Out). Add to back (enqueue),
remove from front (dequeue).
Use cases: BFS traversal, task queues, print queues.

Java: use `Deque<T> stack = new ArrayDeque<>()` for stacks;
`Queue<T> q = new ArrayDeque<>()` or `LinkedList` for queues.
Never use `java.util.Stack` (legacy, synchronized).

---

**Q4: How do you find duplicates in an array?**

Use a HashSet. Scan the array; for each element, check if
it is already in the set. If yes: duplicate found. If no:
add to set. O(n) time, O(n) space.

```java
List<Integer> findDuplicates(int[] arr) {
    Set<Integer> seen = new HashSet<>();
    List<Integer> dupes = new ArrayList<>();
    for (int n : arr) {
        if (!seen.add(n)) dupes.add(n);
    }
    return dupes;
}
```

---

**Q5: What is Big O of sorting an array in Java?**

`Arrays.sort(int[])` uses Dual-Pivot Quicksort: O(n log n)
average, O(n²) worst case (rare). `Arrays.sort(Integer[])` /
`Collections.sort()` uses TimSort: O(n log n) worst case,
O(n) for already-sorted input.

---

**Q6: How do you reverse a linked list?**

Iterative (O(n) time, O(1) space):

```java
ListNode reverse(ListNode head) {
    ListNode prev = null, curr = head;
    while (curr != null) {
        ListNode next = curr.next;
        curr.next = prev;
        prev = curr;
        curr = next;
    }
    return prev;  // new head
}
```

---

**Q7: What is a balanced binary tree?**

A tree where the height difference between left and right
subtrees is at most 1 for every node. Height of a balanced
binary tree: O(log n). AVL trees and Red-Black Trees are
self-balancing BSTs that enforce this property automatically.
Java's TreeMap is a Red-Black Tree.

---

**Q8: How do you check if two strings are anagrams?**

Sort both and compare: O(n log n). Better: count character
frequencies with a frequency array/map: O(n) time, O(k)
space where k is the character set size.

```java
boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    int[] count = new int[26];
    for (char c : s.toCharArray()) count[c - 'a']++;
    for (char c : t.toCharArray()) count[c - 'a']--;
    for (int v : count) if (v != 0) return false;
    return true;
}
// O(n) time, O(1) space (fixed 26-char alphabet)
```

---

**Q9: What is recursion, and when should you avoid it?**

Recursion is a function calling itself with a smaller
subproblem until a base case. Avoid when: (1) stack depth
is large (risk of StackOverflowError in Java, default
stack ~512KB); (2) the same subproblems are recomputed
repeatedly (use memoization or iterative DP instead);
(3) an iterative solution is equally clear.

---

**Q10: What is the two-sum problem and how do you solve
it in O(n)?**

Given an array and a target, find two indices where the
values sum to target.
O(n²) brute force: check all pairs.
O(n) with HashMap: for each element, check if
`target - element` is already in the map.

```java
int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (map.containsKey(complement))
            return new int[]{map.get(complement), i};
        map.put(nums[i], i);
    }
    return new int[]{};
}
```

---

### Mastery Checklist

- [ ] Can answer all 10 questions without reference in
      under 30 seconds per question
- [ ] Can code solutions for Q4, Q6, Q8, Q10 from memory
- [ ] Knows the Java-specific implementation choices
      (ArrayDeque over Stack/LinkedList, TreeMap internals)

---

### Quick Reference Card

| Topic | Key Fact |
|-------|---------|
| HashMap.get() | O(1) avg, O(log n) worst (Java 8+) |
| LinkedList vs ArrayList | ArrayList almost always better; use ArrayDeque for queue |
| Reverse linked list | 3-pointer iterative: O(n) time, O(1) space |
| Anagram check | Frequency count: O(n) time, O(1) space |
| Two-sum | HashMap complement: O(n) time, O(n) space |
