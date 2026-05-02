---
layout: default
title: "Priority Queue"
parent: "Data Structures & Algorithms"
nav_order: 38
permalink: /dsa/priority-queue/
number: "0038"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Heap (Min/Max), Queue / Deque
used_by: Dijkstra, A* Search, Huffman Coding, Event Simulation
related: Heap (Min/Max), Queue / Deque, TreeMap
tags:
  - datastructure
  - intermediate
  - algorithm
  - performance
---

# 038 — Priority Queue

⚡ TL;DR — A Priority Queue always serves the highest-priority element next, regardless of insertion order, in O(log N) time.

| #038 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Heap (Min/Max), Queue / Deque | |
| **Used by:** | Dijkstra, A* Search, Huffman Coding, Event Simulation | |
| **Related:** | Heap (Min/Max), Queue / Deque, TreeMap | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A hospital manages 200 patients in the waiting room. Each patient has a triage score. Nurses want to serve the most critical patient next. Using a FIFO Queue, patient #1 is served before patient #200 even if patient #200 is critical. Using a sorted list, every new patient requires locating the correct sorted position and shifting — O(N) per arrival. With 200 arrivals per hour, the sorting overhead consumes 20,000 operations per hour and grows as the list grows.

THE BREAKING POINT:
A regular Queue ignores priority entirely — it serves whoever arrived first, not whoever needs help most. Keeping a sorted list gives priority access but makes insertion expensive. Neither structure serves the core need: "always serve the most critical next, cheaply."

THE INVENTION MOMENT:
An abstract interface that guarantees "remove the highest-priority element" without specifying how the ordering is maintained internally. The Heap is the natural implementation: O(1) peek at highest priority, O(log N) insert and remove. This is exactly why the Priority Queue was created.

---

### 📘 Textbook Definition

A **Priority Queue** is an abstract data type that operates like a queue but where each element has an associated priority. Elements are dequeued in priority order (highest priority first), not insertion order. The priority queue interface specifies: `insert(element, priority)`, `extractMax/Min()`, and `peekMax/Min()`. The standard implementation is a binary heap, which provides O(log N) insert and extract, and O(1) peek at the extremum.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A queue that always gives you the most important item next, not the oldest.

**One analogy:**
> An airline check-in desk has a normal queue, but a gate agent occasionally calls forward passengers with connections departing in 20 minutes. No matter when they arrived, urgency determines next service. The priority queue is that gate agent's mental model formalised.

**One insight:**
Priority Queue is an *interface contract*, not an implementation. You can back it with a heap (standard), a sorted array (if writes are rare), or a Fibonacci heap (if decrease-key operations dominate). Choosing the right implementation depends on your operation mix — the interface stays the same.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The element with the highest priority is always served next.
2. Priority is determined by comparison, not by insertion order.
3. Equal-priority elements have no guaranteed relative order (unless the comparator breaks ties).

DERIVED DESIGN:
The heap is the canonical implementation because it satisfies all three invariants while minimising the cost of the most common operations:
- `peek()`: O(1) — root of heap is always the extremum.
- `offer()`: O(log N) — sift-up through tree height.
- `poll()`: O(log N) — sift-down after moving last element to root.

Could a sorted array work? Peek is O(1) and poll is O(1), but offer is O(N) for insertion. If offers > polls (common in streaming), the heap is faster overall.

Could a Fibonacci heap work? O(1) amortised insert and O(log N) extract-min — but also O(1) decrease-key, which matters for Dijkstra. In Java there is no standard `FibonacciHeap`; it's complex to implement correctly.

THE TRADE-OFFS:
Gain: Always O(1) access to extremum, O(log N) insert and remove.
Cost: O(N) arbitrary search, no ordering among equal-priority elements, O(N log N) full sorted extraction.

---

### 🧪 Thought Experiment

SETUP:
A network router receives packets with Quality-of-Service (QoS) labels: 1 (video call, high priority) and 3 (background download, low priority). 100 packets arrive per second; the router can forward 80 per second.

WHAT HAPPENS WITH FIFO QUEUE:
Packets are sent in arrival order. A background download packet that arrived at t=0 blocks a video call packet that arrived at t=1. The video call stutters. QoS is meaningless.

WHAT HAPPENS WITH PRIORITY QUEUE:
All 100 packets are inserted with their QoS priority. Each send cycle polls the minimum-priority (= highest QoS) packet. Video call packets are always forwarded before background packets, regardless of arrival order. QoS is enforced automatically.

THE INSIGHT:
A priority queue is not just about performance — it is about *policy enforcement*. The data structure itself embodies the ordering rule: you define priority once (in the comparator), and the structure guarantees every extraction respects it.

---

### 🧠 Mental Model / Analogy

> A Priority Queue is like a hospital emergency triage system. Patients enter in any order (insertion), but the next patient seen is always the most critical (highest priority extraction). A FIFO queue is first-come-first-served; the priority queue is most-critical-first — always.

"Patient enters" → `offer(patient)`
"Most critical patient" → element with minimum priority number
"Doctor sees next patient" → `poll()`
"Check who's most critical" → `peek()`

Where this analogy breaks down: In a real hospital, the triage nurse re-assesses severity continuously (effectively "decreasing the key"). Java's `PriorityQueue` does not support efficient decrease-key; for that, use a Fibonacci heap or re-insert.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A special queue where the most important item always comes out first, no matter when it was added.

**Level 2 — How to use it (junior developer):**
Java's `PriorityQueue<E>` is a min-heap by default — `poll()` returns the smallest element. For max-heap: `new PriorityQueue<>(Collections.reverseOrder())`. For custom priority: `new PriorityQueue<>(Comparator.comparing(Job::getPriority))`. Use `offer()` to add, `poll()` to remove-and-return the min, `peek()` to see without removing. Check `isEmpty()` before `poll()`.

**Level 3 — How it works (mid-level engineer):**
Java `PriorityQueue` is backed by a binary min-heap in an `Object[]` array. `offer(e)` places `e` at the last position and calls `siftUp()`. `poll()` removes the root, places the last element at root, and calls `siftDown()`. Both are O(log N). The `remove(Object o)` method requires a linear scan (O(N)) to find the element before removing it — there is no O(log N) arbitrary removal.

**Level 4 — Why it was designed this way (senior/staff):**
The lack of O(log N) decrease-key in Java's `PriorityQueue` is a deliberate simplification. Decrease-key requires the queue to find the element in O(1) (via a position hashtable). Java's implementation avoids this overhead for the common case. In Dijkstra implementations, this is worked around by inserting duplicate entries with updated distances and using a "visited" check to skip stale ones — an accepted trade-off. For true decrease-key support, third-party Fibonacci or d-ary heap libraries are needed.

---

### ⚙️ How It Works (Mechanism)

**Standard Dijkstra pattern (no decrease-key needed):**
```java
PriorityQueue<int[]> pq =
    new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
// a[0] = distance, a[1] = node

pq.offer(new int[]{0, src}); // distance 0 to source
while (!pq.isEmpty()) {
    int[] curr = pq.poll(); // always minimum distance
    int dist = curr[0], node = curr[1];
    // Instead of decrease-key: just insert duplicate
    // and skip stale entries
    if (dist > bestDist[node]) continue;
    // process...
}
```

**Bounded priority queue (top-K):**
```
Keep a max-heap of size K.
For each new element e:
  If heap.size() < K: offer(e)
  Else if e < heap.peek(): poll(); offer(e)
  Else: skip
Heap always contains K smallest elements seen so far.
```

┌──────────────────────────────────────────────┐
│  Priority Queue operations                   │
│                                              │
│  offer(5): sift-up → O(log N)               │
│  offer(2): sift-up → becomes new root        │
│  peek():   return root (2) → O(1)           │
│  poll():   remove root (2), sift-down        │
│            → next min becomes root → O(log N)│
└──────────────────────────────────────────────┘

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
New element with priority arrives
→ offer(): inserted, sifted to correct position
→ [PRIORITY QUEUE ← YOU ARE HERE]
→ poll(): highest-priority element removed
→ Caller processes most-urgent element
→ Heap re-heapified for next extraction
```

FAILURE PATH:
```
Element's priority field mutated after insertion
→ Heap property violated silently
→ poll() returns wrong (non-minimum) element
→ Algorithm produces incorrect results
→ Fix: remove, update, re-insert
```

WHAT CHANGES AT SCALE:
At 10M elements, Java's `PriorityQueue` performs well but `siftDown` on extraction involves cache-inefficient pointer chasing through a large array. A **4-ary heap** (`d=4`) reduces tree height and improves cache occupancy per node. For ultra-high-throughput scenarios (financial tick processing), consider lock-free priority queues from libraries like Chronicle Queue or Agrona. For concurrent access, `PriorityBlockingQueue` exists but serialises all operations through a single lock.

---

### 💻 Code Example

**Example 1 — Task scheduler by priority:**
```java
record Task(String name, int priority)
    implements Comparable<Task> {
    @Override
    public int compareTo(Task o) {
        // Lower number = higher priority
        return Integer.compare(this.priority, o.priority);
    }
}

PriorityQueue<Task> scheduler = new PriorityQueue<>();
scheduler.offer(new Task("backup",    3));
scheduler.offer(new Task("video-call",1));
scheduler.offer(new Task("email",     2));

while (!scheduler.isEmpty()) {
    System.out.println(scheduler.poll().name());
}
// Output: video-call → email → backup
```

**Example 2 — Merge K sorted arrays:**
```java
int[] mergeKSortedArrays(int[][] arrays) {
    // min-heap: [value, arrIdx, elemIdx]
    PriorityQueue<int[]> pq =
        new PriorityQueue<>(Comparator.comparingInt(a -> a[0]));
    int totalLen = 0;
    for (int i = 0; i < arrays.length; i++) {
        if (arrays[i].length > 0) {
            pq.offer(new int[]{arrays[i][0], i, 0});
            totalLen += arrays[i].length;
        }
    }
    int[] result = new int[totalLen];
    int idx = 0;
    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        result[idx++] = curr[0];
        int ai = curr[1], ei = curr[2];
        if (ei + 1 < arrays[ai].length)
            pq.offer(new int[]{arrays[ai][ei+1], ai, ei+1});
    }
    return result;
}
```

---

### ⚖️ Comparison Table

| Implementation | insert | extract | decrease-key | Best For |
|---|---|---|---|---|
| **Binary Heap** | O(log N) | O(log N) | O(N) | General purpose |
| Fibonacci Heap | O(1) amort. | O(log N) | O(1) amort. | Decrease-key heavy (Dijkstra) |
| d-ary Heap (d=4) | O(log_d N) | O(d log_d N) | O(log_d N) | Cache-efficient bulk workloads |
| Sorted Array | O(N) | O(1) | O(N) | Read-dominant, small N |
| Sorted TreeMap | O(log N) | O(log N) | O(log N) | Range queries also needed |

How to choose: Use Java `PriorityQueue` (binary heap) for all standard cases. Use Fibonacci heap (3rd party) only when decrease-key is called more than extract-min. For cache performance at scale, use a 4-ary heap.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| PriorityQueue iterates in priority order | `for (E e : pq)` does NOT iterate in heap order; use repeated `poll()` for sorted output |
| PriorityQueue handles ties in insertion order | Equal priorities have no insertion-order guarantee; add a tie-breaker to your comparator |
| remove(Object) is O(log N) | `PriorityQueue.remove(Object)` is O(N) — requires linear scan |
| PriorityQueue is thread-safe | Not thread-safe; use `PriorityBlockingQueue` for concurrent access |
| Priority Queue equals Heap | Priority Queue is the abstract interface; Heap is the implementation — a PQ can be backed by any ordered structure |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong priority direction (max instead of min)**

Symptom: Algorithm processes lowest-priority items first instead of highest.

Root Cause: Used natural ordering (min-heap) when the application logic required max-first.

Diagnostic:
```java
// Unit test: offer 3 items, poll should return highest priority
pq.offer(new Task("low", 3));
pq.offer(new Task("high", 1));
assert pq.poll().name().equals("high"); // fails if wrong direction
```

Fix:
```java
// BAD: natural order = min heap (smallest number first)
PriorityQueue<Task> pq = new PriorityQueue<>();

// GOOD: reverse for max-first by number
PriorityQueue<Task> pq =
    new PriorityQueue<>(
        Comparator.comparingInt(Task::getPriority).reversed());
```

Prevention: Write the direction explicitly in a comment; always unit-test with two items of different priority.

---

**2. Stale entries in Dijkstra causing incorrect distances**

Symptom: Dijkstra returns wrong shortest paths; some nodes reported unreachable.

Root Cause: Using the "lazy deletion" pattern (re-insert instead of decrease-key) but forgetting to skip stale entries where `dist > bestDist[node]`.

Diagnostic:
```bash
# Add assertion: every polled distance should be ≤ best known
assert dist <= bestDist[node] || isStale(node, dist);
```

Fix:
```java
while (!pq.isEmpty()) {
    int[] curr = pq.poll();
    int d = curr[0], u = curr[1];
    if (d > dist[u]) continue; // skip stale — REQUIRED
    // process u...
}
```

Prevention: Always include the stale-entry guard when using lazy deletion.

---

**3. Memory leak from unbounded priority queue**

Symptom: Memory grows continuously; heap dump shows PriorityQueue with millions of entries.

Root Cause: Items are added faster than consumed; no eviction or size bound.

Diagnostic:
```bash
jmap -histo:live <pid> | grep PriorityQueue
# Shows internal Object[] array size
```

Fix: Bound the queue by checking size before insertion and evicting lowest-priority entries:
```java
if (pq.size() >= MAX_SIZE && pq.peek() < newElement)
    pq.poll(); // evict lowest
pq.offer(newElement);
```

Prevention: Always bound priority queues in streaming scenarios; monitor queue depth as a metric.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Heap (Min/Max)` — the binary heap is the standard implementation backing `PriorityQueue`.
- `Queue / Deque` — contrasts FIFO ordering with priority ordering.

**Builds On This (learn these next):**
- `Dijkstra` — uses a min-heap priority queue to extract the nearest unvisited node efficiently.
- `A* Search` — extends Dijkstra with a heuristic; uses priority queue ordered by `f(n) = g(n) + h(n)`.

**Alternatives / Comparisons:**
- `TreeMap` — also provides min/max access but additionally supports range queries; higher constant factor.
- `Heap (Min/Max)` — the implementation detail; Priority Queue is the abstract contract.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Queue that always serves the highest-     │
│              │ priority element next (O(1) peek,         │
│              │ O(log N) insert/extract)                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ FIFO ignores urgency; sorted list is      │
│ SOLVES       │ too slow for dynamic inserts              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ It's an interface, not just a heap —      │
│              │ the implementation is swappable           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Scheduling, Dijkstra, top-K streaming,    │
│              │ event simulation, network QoS             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need arbitrary search/update (O(N))       │
│              │ or guaranteed FIFO tie-breaking           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(log N) priority access vs no ordering   │
│              │ between equal-priority elements           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "An ER triage desk: always treats the     │
│              │  most critical patient next"              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Heap → Dijkstra → A* Search               │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Dijkstra's algorithm uses a priority queue to process the nearest unvisited node first. Java's `PriorityQueue` has no O(log N) decrease-key operation. The workaround is to re-insert a node with its updated distance and skip stale entries when polled. For a dense graph with V=10,000 vertices and E=50,000,000 edges, how many total queue entries can accumulate with this approach, and at what point does the memory overhead of stale entries make this approach impractical compared to a true decrease-key heap?

**Q2.** A real-time trading engine receives 500,000 order events per second and must always process the highest-value order first. The team debates between a binary heap `PriorityQueue` and a `TreeMap`. Both offer O(log N) insert and extract. Given that orders are rarely cancelled (decrease-key not needed), what are the concrete performance differences between the two under this workload, and in what scenario would `TreeMap`'s O(log N) range query capability justify its higher constant factor?

