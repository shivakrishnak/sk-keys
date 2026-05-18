---
id: DSA-045
title: Deque (Double-Ended Queue)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-012, DSA-013, DSA-041
used_by: DSA-038
related: DSA-012, DSA-013, DSA-038, DSA-041
tags:
  - data-structures
  - deque
  - double-ended-queue
  - arraydeque
  - stack
  - queue
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/dsa/deque/
---

## TL;DR

A Deque supports O(1) insert and remove at both ends -
the universal replacement for Stack and Queue in Java,
also the engine behind sliding window maximum algorithms.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-045 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, deque, ArrayDeque, O(1) |
| **Prerequisites** | DSA-012, DSA-013, DSA-041 |

---

### The Problem This Solves

Java's `Stack` is synchronized (legacy, slow). `LinkedList`
has poor cache performance. `ArrayDeque` is a circular
buffer-backed deque that gives O(1) at both ends with
good cache performance - the correct default for stack
and queue in modern Java.

---

### Textbook Definition

A Deque (Double-Ended Queue, pronounced "deck") is an
abstract data type supporting O(1) insertion and removal
at both front and back. Java's `ArrayDeque` implements
Deque with a resizable circular array. Also implements
the `Queue` and `Deque` interfaces. Not thread-safe.

---

### How It Works

**Java ArrayDeque API:**

```java
Deque<Integer> deque = new ArrayDeque<>();

// Add to front or back
deque.addFirst(1);   // / offerFirst()
deque.addLast(2);    // / offerLast()
deque.push(3);       // addFirst() alias (stack)
deque.offer(4);      // addLast() alias (queue)

// Remove from front or back
deque.removeFirst(); // / pollFirst()
deque.removeLast();  // / pollLast()
deque.pop();         // removeFirst() alias
deque.poll();        // pollFirst() alias

// Peek front or back
deque.peekFirst();
deque.peekLast();
```

**Using ArrayDeque as stack:**
```java
Deque<String> stack = new ArrayDeque<>();
stack.push("a");
stack.push("b");
stack.push("c");
stack.pop();  // "c" (LIFO)
```

**Using ArrayDeque as queue:**
```java
Queue<String> queue = new ArrayDeque<>();
queue.offer("a");
queue.offer("b");
queue.offer("c");
queue.poll(); // "a" (FIFO)
```

**Sliding window maximum (classic Deque algorithm):**

```java
// Maximum of every window of size k: O(n) with deque
int[] maxSlidingWindow(int[] nums, int k) {
    int n = nums.length;
    int[] result = new int[n - k + 1];
    // Deque stores INDICES; front = index of max in window
    Deque<Integer> deque = new ArrayDeque<>();

    for (int i = 0; i < n; i++) {
        // Remove indices no longer in window
        if (!deque.isEmpty() && deque.peekFirst() <= i - k)
            deque.pollFirst();
        // Remove smaller elements from back (they'll never
        // be the max while nums[i] is in the window)
        while (!deque.isEmpty()
               && nums[deque.peekLast()] <= nums[i])
            deque.pollLast();
        deque.offerLast(i);
        // Window is full
        if (i >= k - 1) result[i - k + 1] = nums[deque.peekFirst()];
    }
    return result;
}
```

---

### Comparison Table

| Class | Stack | Queue | Thread-safe | Notes |
|-------|-------|-------|-------------|-------|
| `ArrayDeque` | Yes | Yes | No | Recommended default |
| `java.util.Stack` | Yes | No | Yes | Legacy, avoid |
| `LinkedList` | Yes | Yes | No | Worse cache than ArrayDeque |
| `LinkedBlockingDeque` | Yes | Yes | Yes | For concurrent use |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Stack class is the right Java stack" | `java.util.Stack` extends `Vector` (synchronized ArrayList), making every push/pop synchronized unnecessarily. Use `ArrayDeque` |
| "ArrayDeque can't be used as a queue" | It implements `Queue` interface; `offer()`/`poll()`/`peek()` work as expected for FIFO |

---

### Quick Reference Card

| Use case | ArrayDeque method |
|---------|------------------|
| Stack push | `push(e)` or `addFirst(e)` |
| Stack pop | `pop()` or `removeFirst()` |
| Queue enqueue | `offer(e)` or `addLast(e)` |
| Queue dequeue | `poll()` or `removeFirst()` |
| Window max/min | Monotonic deque pattern |

---

### Mastery Checklist

- [ ] Uses `ArrayDeque` instead of `Stack` or `LinkedList`
      for stack/queue operations in new code
- [ ] Can implement the sliding window maximum in O(n)
      using a monotonic deque

---

### Interview Deep-Dive

**Q1 (Medium):** Implement sliding window maximum:
given an array and window size k, find the max of each
window in O(n).

> Use a monotonic deque storing indices in decreasing
> order of their values. For each new element: (1) Remove
> front if it's out of the window (index <= i-k). (2) Remove
> all back elements smaller than current (they can never be
> the max while current is in the window). (3) Add current
> index to back. (4) Front is the max of current window.
> Each index added and removed at most once = O(n) total.
> Without the deque: O(n*k) brute force.
