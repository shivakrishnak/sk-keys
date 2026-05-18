---
id: DSA-013
title: Queue (FIFO)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-008, DSA-010
used_by: DSA-024, DSA-036, DSA-041, DSA-045
related: DSA-012, DSA-029, DSA-045
tags:
  - data-structures
  - queue
  - fifo
  - bfs
  - task-queue
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/dsa/queue/
---

## TL;DR

A queue is a FIFO (First-In, First-Out) collection with O(1)
enqueue and dequeue - the structure behind BFS, task queues,
and every producer-consumer system.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-013 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, queue, FIFO, BFS, task-queue |
| **Prerequisites** | DSA-008, DSA-010 |

---

### The Problem This Solves

Many real systems process work in the order it arrives:
print jobs, network packets, task scheduling. The queue
formalizes "first arrived, first served" with O(1) operations
at both ends.

---

### Textbook Definition

A queue is an abstract data type enforcing First-In, First-Out
(FIFO) access. Elements are added at the back (enqueue) and
removed from the front (dequeue). Both operations are O(1).

---

### Understand It in 30 Seconds

A line at a coffee shop. New customers join the end (enqueue).
Customers at the front get served first (dequeue). No
cutting in line. No taking from the middle. Perfect fairness.

---

### First Principles

**Why FIFO models real systems:**
Most processing pipelines must preserve arrival order:
- HTTP request handling: requests served in arrival order
- Message brokers: events must be delivered in order
- BFS: level-by-level exploration requires FIFO ordering

A stack (LIFO) would process the NEWEST task first -
inverting work order. Queues are fairness incarnate.

---

### How It Works

**Java ArrayDeque as queue:**

```java
// BAD: using LinkedList as queue (cache-unfriendly)
Queue<String> queue = new LinkedList<>();
queue.offer("task1");
queue.offer("task2");
String next = queue.poll(); // "task1"

// GOOD: ArrayDeque (faster, cache-friendly backing array)
Deque<String> queue = new ArrayDeque<>();
queue.offerLast("task1");  // enqueue at back
queue.offerLast("task2");
String next = queue.pollFirst(); // dequeue from front → "task1"

// Null-safe check pattern
String next = queue.isEmpty() ? null : queue.pollFirst();
```

**BFS uses a queue:**

```java
void bfs(Node root) {
    Queue<Node> q = new ArrayDeque<>();
    q.offer(root);
    while (!q.isEmpty()) {
        Node node = q.poll();  // FIFO: process level by level
        process(node);
        for (Node child : node.children) q.offer(child);
    }
}
```

---

### Comparison Table

| Queue Type | Java Class | Use Case |
|-----------|-----------|---------|
| Basic FIFO | ArrayDeque | BFS, task processing |
| Blocking | ArrayBlockingQueue | Producer-consumer |
| Priority | PriorityQueue | Dijkstra, scheduling |
| Concurrent | ConcurrentLinkedQueue | Lock-free multi-thread |
| Delay | DelayQueue | Scheduled tasks |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "LinkedList is the standard queue implementation" | `ArrayDeque` is faster due to array backing; LinkedList has per-element object overhead |
| "Queue.poll() throws on empty" | `poll()` returns null; `remove()` throws NoSuchElementException |
| "Queues are only for message passing" | BFS, CPU scheduling, print spooling, rate limiting all use queues |

---

### Failure Modes & Diagnosis

**Failure: Unbounded queue memory growth**
- Symptom: OOM error; memory grows without bound
- Cause: Producers faster than consumers; queue grows forever
- Fix: Use `ArrayBlockingQueue(capacity)` - blocks producers
  when full, creating natural backpressure

**Failure: Polling wrong end**
- Symptom: Elements processed in wrong order (LIFO instead
  of FIFO)
- Cause: Using `stack.pop()` (removeFirst) but enqueueing
  with `addLast`; or vice versa
- Fix: Use named methods: `offerLast` / `pollFirst` for FIFO

---

### Quick Reference Card

| Operation | Method (ArrayDeque) | Complexity |
|-----------|---------------------|-----------|
| Enqueue | `offerLast(x)` | O(1) amortized |
| Dequeue | `pollFirst()` | O(1) |
| Peek front | `peekFirst()` | O(1) |
| isEmpty | `isEmpty()` | O(1) |

---

### Mastery Checklist

- [ ] Can implement BFS using a queue
- [ ] Knows the difference between Queue methods: offer vs
      add, poll vs remove, peek vs element
- [ ] Can choose between ArrayDeque, LinkedList, and
      BlockingQueue for different queue use cases
- [ ] Understands backpressure via bounded queues

---

### Think About This

1. Implement a queue using two stacks. What is the amortized
   complexity of enqueue and dequeue?

2. How does BFS guarantee that it visits nodes level by level?
   Why does a stack (DFS) not have this property?

---

### Interview Deep-Dive

**Q1 (Medium):** Implement a queue using two stacks.

> Use two stacks: `inStack` and `outStack`.
> Enqueue: push to inStack (O(1)).
> Dequeue: if outStack empty, pop ALL from inStack and push
>   to outStack (O(n) amortized O(1)); then pop outStack.
> This achieves amortized O(1) per operation because each
> element moves from inStack to outStack exactly once.

**Q2 (Hard):** Why does BFS use a queue while DFS uses a
stack? What goes wrong if you use the wrong structure?

> BFS needs to process all nodes at distance k before
> distance k+1. A queue's FIFO order naturally ensures this:
> when node A is processed, its children (distance k+1) are
> enqueued after all existing distance-k nodes.
> If you use a stack instead, children are processed
> immediately (LIFO → depth-first behavior), destroying the
> level-by-level guarantee. The algorithm still terminates
> but no longer computes shortest paths in unweighted graphs.
