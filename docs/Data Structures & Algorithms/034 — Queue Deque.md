---
layout: default
title: "Queue / Deque"
parent: "Data Structures & Algorithms"
nav_order: 34
permalink: /dsa/queue-deque/
number: "034"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, LinkedList, Stack
used_by: BFS, Thread Pool Task Queue, Rate Limiting, Sliding Window, Priority Queue
tags:
  - datastructure
  - algorithm
  - foundational
---

# 034 — Queue / Deque

`#datastructure` `#algorithm` `#foundational`

⚡ TL;DR — Queue is FIFO (first-in, first-out); Deque is a double-ended queue supporting O(1) insert and remove from both ends.

| #034 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Array, LinkedList, Stack | |
| **Used by:** | BFS, Thread Pool Task Queue, Rate Limiting, Sliding Window, Priority Queue | |

---

### 📘 Textbook Definition

A **Queue** is an abstract data type implementing First-In, First-Out (FIFO) ordering: elements are enqueued at the tail and dequeued from the head. A **Deque** (double-ended queue) generalises this to allow O(1) insertion and removal at both ends — functioning as both a stack and a queue. In Java, `java.util.Deque<E>` provides the interface, implemented by `ArrayDeque<E>` (backed by a circular resizable array — preferred) and `LinkedList<E>`. `PriorityQueue<E>` provides a heap-based queue variant where dequeue returns the minimum (or maximum with comparator) element.

### 🟢 Simple Definition (Easy)

A queue is like a checkout line: first person in line is first to be served. A deque is a line where you can join or leave from either end.

### 🔵 Simple Definition (Elaborated)

Queues model "wait your turn" logic — essential for scheduling, breadth-first search, and producer-consumer patterns. The FIFO property ensures fairness: whoever arrives first is processed first. A deque extends this to a double-ended queue where you can add or remove from either the front or the back — combining Stack (LIFO from one end) and Queue (FIFO across both ends) into a single structure. Java's `ArrayDeque` implements `Deque` and is the standard choice for both stack and queue needs, offering better cache performance than `LinkedList`.

### 🔩 First Principles Explanation

**Queue operations:**
- `enqueue(x)` / `offer(x)`: add `x` to tail. O(1).
- `dequeue()` / `poll()`: remove and return head. O(1).
- `peek()` / `element()`: return head without removing. O(1).

**Array-based queue (circular buffer implementation):**

```
Circular Array Queue (capacity = 5):
arr:   [ 3 | 7 | 5 | _ | _ ]
head = 0, tail = 3, size = 3

enqueue(9): arr[3] = 9, tail = 4
            [ 3 | 7 | 5 | 9 | _ ]

dequeue(): return arr[0] = 3, head = 1
            [ _ | 7 | 5 | 9 | _ ]

enqueue(2): arr[4] = 2, tail = 0 (wrap!)
            [ _ | 7 | 5 | 9 | 2 ]

dequeue(): return arr[1] = 7, head = 2
            [ _ | _ | 5 | 9 | 2 ]
```

The circular buffer avoids shifting elements on dequeue — O(1) for all operations without linked-list overhead.

**Deque operations:**
- `addFirst()` / `addLast()` — O(1) insert at either end.
- `removeFirst()` / `removeLast()` — O(1) remove from either end.
- `peekFirst()` / `peekLast()` — O(1) peek at either end.

**BlockingQueue for concurrent use:**

```
java.util.concurrent.BlockingQueue<T>:
  - put(x): enqueue; BLOCKS if queue full
  - take():  dequeue; BLOCKS if queue empty

Implementations: ArrayBlockingQueue (bounded),
  LinkedBlockingQueue (optionally bounded),
  SynchronousQueue (no buffer — direct handoff)
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Queue:

- BFS requires processing nodes in the order they were discovered — strictly FIFO.
- Thread pool task scheduling: use a LIFO stack and new requests always wait behind newer ones — unbounded latency for old tasks.
- Producer-consumer: without a buffer queue, producer and consumer must synchronise on every item.

What breaks without it:
1. BFS with a stack becomes DFS — completely different traversal, wrong algorithm.
2. Thread pool with stack task queue causes starvation: early tasks never run.

WITH Queue:
→ BFS explores nodes level by level — correct shortest-path algorithm.
→ Fair FIFO scheduling ensures no task starvation in thread pools.
→ BlockingQueue enables decoupled producer-consumer with back-pressure.

### 🧠 Mental Model / Analogy

> Queue: the checkout line at a grocery store. Customers join at the back, are served at the front. First in, first served. Deque: a bus with doors at both front and back — passengers can board or exit from either end. Priority Queue: VIP airport security — highest priority fliers go through regardless of arrival order.

"Queue" = FIFO line, "Deque" = front-and-back boarding, "Priority Queue" = priority lane.

### ⚙️ How It Works (Mechanism)

**Complexity:**

```
Operation          Queue(ArrayDeque) Queue(LinkedList) PriorityQueue
─────────────────────────────────────────────────────────────────────
offer(enqueue)     O(1) amortised   O(1)              O(log n)
poll(dequeue)      O(1)             O(1)              O(log n)
peek               O(1)             O(1)              O(1)
contains           O(n)             O(n)              O(n)
```

**Sliding window maximum using Deque (monotonic deque):**

```
Array: [1, 3, -1, -3, 5, 3, 6, 7], k=3 (window size 3)
Use deque to track index of max in current window:

Process index 0 (val=1): deque = [0]
Process index 1 (val=3): 3>1 → remove 0, deque = [1]
Process index 2 (val=-1): -1<3, deque = [1, 2] → window full
  max = arr[deque.front()] = arr[1] = 3

Window [0..2]=3, [1..3]=-1, [2..4]=5, [3..5]=5...
```

### 🔄 How It Connects (Mini-Map)

```
Array | LinkedList (implementations)
        ↓
Queue (FIFO) ← you are here
  addLast() / pollFirst()
        ↓ extends to
Deque (both ends)
  push/pop ←stack | queue→ offer/poll
        ↓ variants
PriorityQueue (min-heap based)
BlockingQueue (thread-safe with blocking)
        ↓ used in
BFS | Thread Pool | Rate Limiting | Sliding Window
```

### 💻 Code Example

Example 1 — Queue for BFS:

```java
// BFS using Queue — explores level by level (shortest path)
public List<List<Integer>> levelOrder(TreeNode root) {
    List<List<Integer>> result = new ArrayList<>();
    if (root == null) return result;

    Queue<TreeNode> queue = new ArrayDeque<>();
    queue.offer(root); // enqueue root

    while (!queue.isEmpty()) {
        int levelSize = queue.size();
        List<Integer> level = new ArrayList<>();

        for (int i = 0; i < levelSize; i++) {
            TreeNode node = queue.poll(); // dequeue
            level.add(node.val);
            if (node.left  != null) queue.offer(node.left);
            if (node.right != null) queue.offer(node.right);
        }
        result.add(level);
    }
    return result;
}
```

Example 2 — Producer-Consumer with BlockingQueue:

```java
BlockingQueue<Task> taskQueue =
    new ArrayBlockingQueue<>(100); // bounded: max 100 tasks

// Producer thread
Thread producer = new Thread(() -> {
    while (true) {
        Task task = generateTask();
        taskQueue.put(task); // blocks if queue full (back-pressure)
    }
});

// Consumer thread
Thread consumer = new Thread(() -> {
    while (true) {
        Task task = taskQueue.take(); // blocks if queue empty
        process(task);
    }
});
```

Example 3 — Sliding window maximum with monotonic deque:

```java
public int[] maxSlidingWindow(int[] nums, int k) {
    Deque<Integer> deque = new ArrayDeque<>(); // stores indices
    int[] result = new int[nums.length - k + 1];

    for (int i = 0; i < nums.length; i++) {
        // Remove indices outside current window
        while (!deque.isEmpty() && deque.peekFirst() < i - k + 1)
            deque.pollFirst();

        // Remove smaller elements from back (maintain max at front)
        while (!deque.isEmpty() &&
               nums[deque.peekLast()] < nums[i])
            deque.pollLast();

        deque.offerLast(i);

        if (i >= k - 1) {
            result[i - k + 1] = nums[deque.peekFirst()];
        }
    }
    return result;
}
// Time: O(n), Space: O(k)
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LinkedList is better than ArrayDeque for Queue | ArrayDeque has better cache performance and lower memory overhead. LinkedList is only better if you need explicit node reference access. |
| Queue and Stack can be used interchangeably | FIFO (Queue) and LIFO (Stack) produce fundamentally different results: BFS vs DFS. They are not interchangeable for traversal algorithms. |
| PriorityQueue is a type of Queue | PriorityQueue does not guarantee FIFO ordering; it always removes the minimum (or custom-ordered) element regardless of insertion order. |
| Deque is always better than Queue | Deque has the same complexity but allows both-end operations. If you only need FIFO, using Queue semantics communicates intent better. |
| ArrayDeque has O(n) operations due to resizing | Resizing is amortised — individual operations are O(1) amortised, exactly like ArrayList. |

### 🔥 Pitfalls in Production

**1. Unbounded Queue Causing OOM Under Load**

```java
// BAD: Unbounded queue grows without limit under load
Queue<Task> tasks = new LinkedList<>();
// Producer adds 1M tasks, consumer is slow → OOM!

// GOOD: Use bounded BlockingQueue with back-pressure
BlockingQueue<Task> tasks = new ArrayBlockingQueue<>(10_000);
// put() blocks producer when full → natural back-pressure
```

**2. Using poll() Without Checking for Null**

```java
// BAD: poll() returns null when empty, not exception
Queue<Integer> q = new ArrayDeque<>();
int val = q.poll(); // returns null → NullPointerException on unboxing!

// GOOD: Check before use or use peek() + isEmpty()
Integer val = q.poll(); // use Integer, not int — avoids unboxing NPE
if (val != null) { process(val); }
// Or:
if (!q.isEmpty()) { process(q.poll()); }
```

**3. Iterating and Modifying a Queue Simultaneously**

```java
// BAD: Modifying queue while iterating → ConcurrentModificationException
for (Integer item : queue) {
    if (shouldRemove(item)) queue.remove(item); // CME!
}

// GOOD: Use iterator's remove() or process via poll()
Iterator<Integer> it = queue.iterator();
while (it.hasNext()) {
    if (shouldRemove(it.next())) it.remove(); // safe
}
```

### 🔗 Related Keywords

- `Stack` — LIFO partner; Deque implements both.
- `BFS` — the graph traversal algorithm requiring a FIFO queue.
- `Priority Queue` — heap-based variant; returns minimum/maximum regardless of FIFO order.
- `BlockingQueue` — thread-safe variant with blocking put/take for producer-consumer.
- `Sliding Window` — monotonic deque enables O(n) sliding window maximum/minimum.
- `Thread Pool Task Queue` — task submission order preserved by queue's FIFO property.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ Queue │ FIFO: offer at tail, poll from head. O(1) all.  │
│ Deque │ Both ends O(1): addFirst/Last, removeFirst/Last. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ BFS, task scheduling, producer-consumer,  │
│              │ sliding window, rate limiting.            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ LIFO needed → use Stack/Deque.push/pop;  │
│              │ priority ordering → PriorityQueue.        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Queue: the fairest data structure —      │
│              │ first in, first served."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HashMap → Priority Queue → BFS → Deque    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A task queue in a thread pool uses an unbounded `LinkedList` queue. Under a load spike, the producer thread submits tasks 10× faster than the consumer processes them. After the spike, the consumer eventually finishes all queued tasks but the application's response time never returns to baseline — it remains 30% higher permanently. What data structure-level explanation could account for this permanent degradation (not an application bug), and how would switching to a bounded `ArrayBlockingQueue` potentially prevent it?

**Q2.** Java's `PriorityQueue` is often described incorrectly as "a sorted queue." It is actually a min-heap that only guarantees the minimum element is at the top at O(1). Explain why iterating a `PriorityQueue` in Java does NOT return elements in sorted order, trace what the iterator actually returns for `PriorityQueue<Integer>` containing {5, 1, 3, 2, 4}, and describe the correct efficient approach to extract all elements in sorted order — with its time complexity.

