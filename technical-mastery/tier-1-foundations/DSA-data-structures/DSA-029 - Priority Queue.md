---
id: DSA-029
title: Priority Queue
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-028
used_by: DSA-063, DSA-064
related: DSA-028, DSA-063, DSA-064
tags:
  - data-structures
  - priority-queue
  - heap
  - scheduling
  - o-log-n
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/dsa/priority-queue/
---

## TL;DR

A Priority Queue serves elements in priority order, not
arrival order - backed by a heap for O(log n) insert and
O(log n) extract, O(1) peek. Java's PriorityQueue is the
standard implementation.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-029 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, priority-queue, scheduling |
| **Prerequisites** | DSA-028 |

---

### The Problem This Solves

A regular queue serves requests in arrival order. An ER
treats the most critical patient first, regardless of when
they arrived. Dijkstra's algorithm processes the closest
unvisited node next. Task schedulers prioritize urgent jobs.
All of these need a queue that serves by priority, not time.

---

### Textbook Definition

A priority queue is an abstract data type where each element
has an associated priority. Elements are dequeued in priority
order: the element with the highest (or lowest) priority is
served first. Implemented with a heap: O(1) peek, O(log n)
insert and extract. Java's `PriorityQueue<E>` is a min-heap
by default (lowest value = highest priority).

---

### Understand It in 30 Seconds

Tasks with priorities: [Task(priority=5), Task(priority=1),
Task(priority=3)].

Add all three. Poll order: priority=1, then 3, then 5.
Not insertion order - priority order.

---

### How It Works

**Java PriorityQueue:**

```java
// Min-priority queue: lowest value polled first
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(5);
pq.offer(1);
pq.offer(3);
pq.peek();   // 1 (min) - O(1), does not remove
pq.poll();   // 1 - removes and returns min - O(log n)
pq.poll();   // 3
pq.poll();   // 5
```

**Custom priority with Comparator:**

```java
// Task with priority - custom ordering
record Task(String name, int priority) {}

// Lower priority number = more urgent
PriorityQueue<Task> scheduler = new PriorityQueue<>(
    Comparator.comparingInt(Task::priority)
);
scheduler.offer(new Task("email", 5));
scheduler.offer(new Task("deploy", 1));   // urgent
scheduler.offer(new Task("cleanup", 3));

Task next = scheduler.poll();  // deploy (priority=1)
```

**Dijkstra's algorithm core loop (priority queue usage):**

```java
// Process nodes in order of current shortest distance
PriorityQueue<int[]> pq = new PriorityQueue<>(
    Comparator.comparingInt(a -> a[1])  // sort by distance
);
pq.offer(new int[]{source, 0});

while (!pq.isEmpty()) {
    int[] curr = pq.poll();         // closest unvisited
    int node = curr[0], dist = curr[1];
    // expand neighbors...
}
```

---

### Comparison Table

| Queue Type | Order | Use case |
|-----------|-------|---------|
| ArrayDeque (FIFO) | Arrival | BFS, request queues |
| ArrayDeque (LIFO) | Reverse arrival | DFS, undo stacks |
| PriorityQueue | Priority | Dijkstra, scheduling, top-k |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "PriorityQueue is sorted" | Internal array is heap-ordered (parent <= children), not fully sorted; `toArray()` is NOT in sorted order |
| "PriorityQueue preserves equal-priority order" | No FIFO guarantee for equal priorities; use a tie-breaker (e.g., sequence number) if needed |

---

### Failure Modes & Diagnosis

**Failure: Iterating PriorityQueue in wrong order**
- Cause: `for (T item : pq)` iterates the underlying heap
  array, not in priority order
- Fix: Use `while (!pq.isEmpty()) { T item = pq.poll(); }`
  to drain in priority order

---

### Quick Reference Card

| Operation | Time | Java method |
|-----------|------|------------|
| Peek min | O(1) | `pq.peek()` |
| Insert | O(log n) | `pq.offer(e)` |
| Extract min | O(log n) | `pq.poll()` |
| Size | O(1) | `pq.size()` |
| Remove specific | O(n) | `pq.remove(e)` |

---

### Mastery Checklist

- [ ] Can use Java PriorityQueue with custom comparators
- [ ] Knows that iteration order != poll order
- [ ] Recognizes the top-k, merge-k-sorted, and Dijkstra
      patterns as priority queue problems

---

### Interview Deep-Dive

**Q1 (Medium):** How do you merge k sorted lists using a
priority queue?

> Create a min-heap initialized with the head node of each
> of the k lists. Poll the minimum, append to result,
> then push the next node from that same list (if exists).
> Repeat until heap is empty.
> Time: O(n log k) where n = total nodes, k = list count.
> Space: O(k) for the heap. This is the classic
> "merge k sorted files" streaming pattern.
