---
layout: default
title: "Priority Queue"
parent: "Data Structures & Algorithms"
nav_order: 38
permalink: /dsa/priority-queue/
number: "038"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Heap (Min/Max), Queue / Deque, Comparator
used_by: Dijkstra's Algorithm, A* Search, K Largest Elements, Task Scheduling, Huffman Coding
tags:
  - datastructure
  - algorithm
  - intermediate
---

# 038 — Priority Queue

`#datastructure` `#algorithm` `#intermediate`

⚡ TL;DR — A queue variant where each element has a priority, and dequeue always removes the highest-priority (min or max) element regardless of insertion order.

| #038 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Heap (Min/Max), Queue / Deque, Comparator | |
| **Used by:** | Dijkstra's Algorithm, A* Search, K Largest Elements, Task Scheduling, Huffman Coding | |

---

### 📘 Textbook Definition

A **priority queue** is an abstract data type representing a collection of elements, each associated with a priority, supporting two fundamental operations: `insert(element, priority)` in O(log n) and `extractMin()` / `extractMax()` — removing and returning the highest-priority element — in O(log n). Unlike a FIFO queue where dequeue order reflects insertion order, a priority queue dequeues elements by priority. In Java, `java.util.PriorityQueue<E>` implements a min-priority queue via a binary min-heap; for a max-priority queue, pass `Comparator.reverseOrder()` or a custom comparator.

### 🟢 Simple Definition (Easy)

A priority queue is like a hospital emergency room — patients aren't seen in arrival order but in urgency order. The most critical case is always handled first, regardless of when they arrived.

### 🔵 Simple Definition (Elaborated)

A regular queue is strictly FIFO — first in, first out. A priority queue replaces "first in" with "highest priority" — the element with the highest urgency (lowest number in min-heap, or highest in max-heap) is always extracted next, regardless of insertion order. This is implemented via a heap, which maintains the highest-priority element at the root. The power of a priority queue lies in O(log n) operations — Dijkstra's algorithm, A* search, Huffman coding, event-driven simulation, and task scheduling all rely on this property.

### 🔩 First Principles Explanation

**Priority queue contract:**
```
insert(element)   → O(log n); element has an implicit or explicit priority
peek()            → O(1);     return highest-priority element without removing
poll() / extract  → O(log n); remove and return highest-priority element
isEmpty()         → O(1)
size()            → O(1)
```

**Priority source options in Java PriorityQueue:**
1. Natural ordering: elements implement `Comparable<E>` (Integer, String, etc.).
2. Comparator: explicit comparator passed at construction.
3. Custom class: implement `Comparable`, defining `compareTo()`.

**Min-heap vs max-heap as priority queues:**

```java
// Min priority queue (default): smallest value = highest priority
PriorityQueue<Integer> minPQ = new PriorityQueue<>();

// Max priority queue: largest value = highest priority
PriorityQueue<Integer> maxPQ =
    new PriorityQueue<>(Comparator.reverseOrder());

// Priority by field (e.g., task priority number — lower = more urgent)
PriorityQueue<Task> taskPQ =
    new PriorityQueue<>(Comparator.comparing(Task::getPriority));
```

**Priority queue with change-priority (decrease-key):**

Java's standard PriorityQueue doesn't support O(log n) decrease-key. Workarounds:
1. **Lazy deletion:** Add updated item with new priority; mark old entry as deleted. Check on extraction.
2. **HashMap tracking:** Store {element: heap_position} to find element in O(1) then sift.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Priority Queue:

- Task scheduling: iterate all tasks to find highest priority each time = O(n) per extraction = O(n²) total.
- Dijkstra's algorithm: without priority queue, must scan all unvisited nodes to find minimum = O(V²).
- Huffman coding: merge two lowest-frequency nodes in each step — O(n) if linear scan.

What breaks without it:
1. Dijkstra on a graph with 1M nodes: O(V²) = 10^12 operations vs O(E log V) = ~20M.
2. Any algorithm requiring "next best element" in a dynamic set degrades to O(n).

WITH Priority Queue:
→ Dijkstra O(E log V), Prim O(E log V) — practical on real-world graphs.
→ Event-driven simulation: process events in time order efficiently.
→ Top-K extraction: O(n log k) instead of O(n log n) full sort.

### 🧠 Mental Model / Analogy

> A priority queue is the hospital ER triage system. Patients (elements) arrive throughout the day (inserts, O(log n) to maintain triage order). The nurse always calls the most critical patient next (extractMin — the patient with the lowest "urgency score," O(log n)). A stable patient who arrived 6 hours ago waits behind a critical case who just arrived. The triage board is maintained as a heap — the most critical patient is always at the top.

"Triage board" = heap, "most critical first" = extractMin, "urgency score" = priority value.

### ⚙️ How It Works (Mechanism)

**Dijkstra's algorithm with PriorityQueue:**

```
Graph: A→B:1, A→C:4, B→C:2, B→D:5, C→D:1

PQ: {(A,0)}
Extract (A,0): dist[A]=0. Add (B,1), (C,4) → PQ: {(B,1),(C,4)}
Extract (B,1): dist[B]=1. Add (C,3),(D,6) → PQ: {(C,3),(C,4),(D,6)}
Extract (C,3): dist[C]=3. Add (D,4)        → PQ: {(C,4),(D,4),(D,6)}
Extract (C,4): skip (C already visited/relaxed)
Extract (D,4): dist[D]=4. Done!

Shortest paths: A→B=1, A→C=3, A→D=4
```

**Event simulation pattern:**

```java
// Time-ordered event processing
PriorityQueue<Event> events =
    new PriorityQueue<>(Comparator.comparing(Event::getTime));

events.offer(new Event(100, "timeout"));
events.offer(new Event(50,  "user_click"));
events.offer(new Event(75,  "api_response"));

while (!events.isEmpty()) {
    Event e = events.poll(); // always processes earliest event
    process(e);
    // May generate new future events
}
```

### 🔄 How It Connects (Mini-Map)

```
Heap (Min/Max) [implementation]
        ↓ abstracted as
Priority Queue ← you are here
  (abstract data type: insert + extractMin/Max)
        ↓ used by
Dijkstra | A* | Prim's MST
K-Largest | Merge K Sorted Lists
Huffman Coding | Event Simulation
Task Scheduling
```

### 💻 Code Example

Example 1 — Merge K Sorted Lists using PriorityQueue:

```java
// Merge K sorted arrays into one sorted array
// PriorityQueue holds one element per array, ordered by value
public int[] mergeKSortedArrays(int[][] arrays) {
    // Entry: (value, array_index, element_index)
    record Entry(int val, int arr, int idx)
        implements Comparable<Entry> {
        public int compareTo(Entry o) {
            return Integer.compare(val, o.val);
        }
    }

    PriorityQueue<Entry> pq = new PriorityQueue<>();
    for (int i = 0; i < arrays.length; i++) {
        if (arrays[i].length > 0)
            pq.offer(new Entry(arrays[i][0], i, 0));
    }

    List<Integer> result = new ArrayList<>();
    while (!pq.isEmpty()) {
        Entry e = pq.poll();           // O(log k)
        result.add(e.val());
        if (e.idx() + 1 < arrays[e.arr()].length) {
            pq.offer(new Entry(
                arrays[e.arr()][e.idx() + 1],
                e.arr(), e.idx() + 1)); // O(log k)
        }
    }
    return result.stream().mapToInt(i -> i).toArray();
}
// Total time: O(n log k) where n = total elements, k = arrays
```

Example 2 — Task scheduler with custom priority:

```java
PriorityQueue<Task> scheduler = new PriorityQueue<>(
    Comparator.comparing(Task::getPriority) // low num = high priority
              .thenComparing(Task::getSubmitTime) // FIFO for same priority
);

scheduler.offer(new Task("Email", 3, now()));
scheduler.offer(new Task("Deploy", 1, now())); // highest priority
scheduler.offer(new Task("Meeting", 2, now()));

// Processes: Deploy (1) → Meeting (2) → Email (3)
while (!scheduler.isEmpty()) {
    Task t = scheduler.poll();
    System.out.println("Processing: " + t.getName());
}
```

Example 3 — Heap without standard PQ (when decrease-key needed via lazy deletion):

```java
// Dijkstra with lazy deletion workaround
PriorityQueue<long[]> pq = new PriorityQueue<>(
    Comparator.comparingLong(arr -> arr[0]));  // [dist, node]
long[] dist = new long[n];
Arrays.fill(dist, Long.MAX_VALUE);
dist[src] = 0;
pq.offer(new long[]{0, src});

while (!pq.isEmpty()) {
    long[] curr = pq.poll();
    long d = curr[0]; int u = (int) curr[1];

    if (d > dist[u]) continue; // lazy deletion: stale entry

    for (int[] edge : graph.get(u)) {
        int v = edge[0]; long w = edge[1];
        if (dist[u] + w < dist[v]) {
            dist[v] = dist[u] + w;
            pq.offer(new long[]{dist[v], v}); // new entry
            // old entry for v stays; will be skipped above
        }
    }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| PriorityQueue is a sorted queue | PriorityQueue is a heap, not a sorted structure. poll() extracts in priority order, but iterating the PriorityQueue does NOT yield sorted output. |
| PriorityQueue handles duplicate priorities in insertion order | PriorityQueue (Java) does not guarantee FIFO within the same priority. Use a secondary comparator (e.g., insertion timestamp) for stable ordering within priority. |
| PriorityQueue supports O(log n) decrease-key | Java's PriorityQueue does NOT expose decrease-key in O(log n). See lazy deletion pattern above. |
| PriorityQueue.remove(element) is O(1) | remove(element) is O(n) — it scans the underlying array to find the element then sifts. Only poll() is O(log n). |
| A priority queue can only be a heap | Priority queues can also be implemented as sorted arrays or Fibonacci heaps. Fibonacci heaps theoretically offer O(1) amortised decrease-key. |

### 🔥 Pitfalls in Production

**1. PriorityQueue Not Thread-Safe**

```java
// BAD: Shared PriorityQueue in concurrent code
PriorityQueue<Task> pq = new PriorityQueue<>();
// Multiple threads offer/poll → internal state corruption

// GOOD: PriorityBlockingQueue for thread safety
BlockingQueue<Task> pq = new PriorityBlockingQueue<>();
// put/take are blocking; offer/poll are non-blocking
```

**2. Comparing Objects Without Consistent Total Order**

```java
// BAD: Comparator violates transitivity
PriorityQueue<Task> pq = new PriorityQueue<>(
    (a, b) -> a.isUrgent() ? -1 : 1
    // Not a valid total order! compareTo(a,b) and compareTo(b,a)
    // can both return -1 → undefined heap behaviour
);

// GOOD: Ensure comparator defines a valid total order
PriorityQueue<Task> pq = new PriorityQueue<>(
    Comparator.comparing(Task::getPriority)
              .thenComparing(Task::getId) // tie-break for stability
);
```

**3. Memory Leak — Never-Polled Expired Entries**

```java
// BAD: Lazy deletion heap grows unboundedly
// Each decrease-key adds a new entry; old ones never removed
// If graph has 1M edges: PQ grows to 1M even when logically empty

// GOOD: Bound PQ growth by tracking visited nodes
Set<Integer> visited = new HashSet<>();
while (!pq.isEmpty()) {
    long[] curr = pq.poll();
    int node = (int) curr[1];
    if (visited.contains(node)) continue; // skip stale
    visited.add(node);
    // process...
}
// visited set bounds PQ effective size to O(V)
```

### 🔗 Related Keywords

- `Heap (Min/Max)` — the data structure implementing priority queue.
- `Queue / Deque` — the FIFO queue contrast; priority queue sacrifices FIFO for priority.
- `Dijkstra's Algorithm` — the canonical shortest-path algorithm built on priority queue.
- `HeapSort` — sorting algorithm using heap's extract-max repeatedly.
- `K Largest Elements` — classic interview problem solved with min-heap of size k.
- `Comparator` — the Java interface for defining custom priority ordering.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Dequeue always returns highest-priority   │
│              │ element; insert and extract both O(log n).│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Dijkstra, A*, task scheduling, top-K,     │
│              │ merge K sorted, event simulation.         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ FIFO needed → Queue; sorted iteration →   │
│              │ TreeSet/TreeMap; thread-safe → PBQ.       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "PQ: the doctor who sees the sickest      │
│              │ patient next, not the earliest."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dijkstra → Huffman → Merge K Sorted Lists │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Dijkstra's algorithm with a binary min-heap has complexity O((V+E) log V). With a Fibonacci heap supporting O(1) amortised decrease-key, it improves to O(E + V log V). For a dense graph with E = V², calculate when the Fibonacci heap version provides meaningful speedup vs. the binary heap version, and explain why despite its theoretical advantage, Fibonacci heaps are rarely used in production implementations of Dijkstra — citing practical factors.

**Q2.** You are designing a real-time auction system where bids arrive continuously and you must always serve the current highest bid within 1 millisecond. The constraint is that bids can be retracted (removed) and modified (price updated) in real-time. Java's `PriorityQueue` lacks O(log n) arbitrary removal and decrease-key. Design a data structure combining a `PriorityQueue` (or heap) with additional structures to support O(log n) insert, O(log n) remove-by-id, O(log n) update-bid, and O(1) get-max operations — and analyse the space complexity of your solution.

