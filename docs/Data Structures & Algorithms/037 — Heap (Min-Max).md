---
layout: default
title: "Heap (Min/Max)"
parent: "Data Structures & Algorithms"
nav_order: 37
permalink: /dsa/heap-min-max/
number: "0037"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, Binary Search
used_by: Priority Queue, Heapsort, Dijkstra, A* Search
related: Priority Queue, Segment Tree, Sorted Array
tags:
  - datastructure
  - intermediate
  - algorithm
  - performance
---

# 037 — Heap (Min/Max)

⚡ TL;DR — A Heap is an array-based binary tree guaranteeing O(1) access to the minimum (or maximum) element with O(log N) insert and remove.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #037         │ Category: Data Structures & Algorithms │ Difficulty: ★★☆        │
├──────────────┼────────────────────────────────────────┼────────────────────────┤
│ Depends on:  │ Array, Binary Search                   │                        │
│ Used by:     │ Priority Queue, Heapsort, Dijkstra     │                        │
│ Related:     │ Priority Queue, Segment Tree           │                        │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You are building an emergency room triage system. Patients arrive continuously with varying severity scores. At any moment, the doctor needs to see the most critical patient. If you store patients in an unsorted array, finding the most critical is O(N) every time. If you use a sorted array, finding the most critical is O(1) — but each new patient requires O(N) insertion to maintain sort order. With 1,000 arrivals per hour, 500 removals per hour, that is 750,000 element shifts per hour just for triage ordering.

THE BREAKING POINT:
You need O(1) find-minimum but O(log N) insert/remove. A sorted array gives O(1) find but O(N) insert. An unsorted array gives O(1) insert but O(N) find. No simple array achieves both.

THE INVENTION MOMENT:
You don't need the entire array sorted — you only need the minimum always at the front. A partially-ordered tree where every parent is smaller than its children guarantees the minimum is always the root, and both insert and remove-min are O(log N). Storing this tree in an array (by level order) eliminates pointer overhead. This is exactly why the Heap was created.

### 📘 Textbook Definition

A **Heap** is a complete binary tree stored in an array satisfying the **heap property**: in a min-heap, every node's value is ≤ its children's values; in a max-heap, every node's value is ≥ its children's values. The minimum (or maximum) element is always at index 0 — accessible in O(1). Insertion and extraction of the root are O(log N) via the `sift-up` and `sift-down` operations. Building a heap from N elements is O(N) using the Floyd algorithm (not O(N log N)).

### ⏱️ Understand It in 30 Seconds

**One line:**
An array disguised as a tree where the smallest element is always first.

**One analogy:**
> Think of a tournament bracket. The winner (smallest value) sits at the top. Every match guarantees the winner beats both competitors. When the winner is removed, the runner-up takes the spot — one "re-match" per level, not a full re-sort.

**One insight:**
A Heap deliberately maintains only *partial* order — not full sorting. This is why it achieves O(log N) for both insert and extract-min, while a fully sorted structure pays O(N) or O(log N) respectively; no structure can do both in O(1).

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The tree is *complete* — all levels filled left-to-right; this enables array storage.
2. Every parent ≤ children (min-heap). No constraint between siblings.
3. The root is always the global minimum.

DERIVED DESIGN:
**Array index arithmetic** (0-indexed):
- Parent of node i: `(i - 1) / 2`
- Left child of i: `2 * i + 1`
- Right child of i: `2 * i + 2`

This eliminates all pointer storage. The "shape" (complete binary tree) is implicit from array position.

**Insert (sift-up):**
Append new element at end; compare with parent; swap if smaller; repeat up to root. Height of complete binary tree = log₂(N), so at most log₂(N) swaps.

**Extract-min (sift-down):**
Remove root; move last element to root; compare with smaller child; swap if larger; repeat down. At most log₂(N) swaps.

**Heap build from array (Floyd algorithm):**
Instead of N individual inserts (O(N log N)), start from the last non-leaf (`N/2 - 1`) and sift down each element toward the root. Total work is O(N) because most nodes are near the leaves where sift-down is shortest.

THE TRADE-OFFS:
Gain: O(1) find-min, O(log N) insert and extract-min, O(N) build.
Cost: No O(log N) search for arbitrary elements, no sorted iteration (only partial order).

### 🧪 Thought Experiment

SETUP:
A printer queue with jobs of priority 1–10 (1=highest). Jobs arrive and depart constantly. At any moment, you must serve the highest-priority job.

WHAT HAPPENS WITH SORTED ARRAY:
Every new job insertion binary-searches its position (O(log N)) then shifts all lower-priority jobs right (O(N)). With 1,000 active jobs, each arrival costs ~500 shifts.

WHAT HAPPENS WITH HEAP:
New job appended at end: O(1). Sifted up to its correct position: O(log N) comparisons, zero shifts. Get next job: `array[0]` — O(1). Remove it: swap with last, sift down: O(log N). No shifting ever.

THE INSIGHT:
The heap achieves O(log N) insert without shifting because it uses tree hierarchy instead of array contiguity to encode order. The "shape" of the tree — not the index — carries the ordering information.

### 🧠 Mental Model / Analogy

> A Heap is like a corporate hierarchy where the CEO (minimum value) is always at the top and every manager earns less than both their direct reports (employees). When the CEO leaves, the most junior employee temporarily takes the chair, then everyone shuffles up one level until proper order is restored.

"CEO at top" → minimum at index 0
"Each manager < both reports" → heap property
"Employee temporarily takes CEO chair" → last element moves to root
"Reshuffle up one level" → sift-down O(log N)

Where this analogy breaks down: A corporate hierarchy has unique reporting chains; a heap has no ordering between siblings (left child may be larger or smaller than right child), so the analogy breaks for "lateral comparisons."

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A special list where the smallest item is always first, and adding or removing items from the front is fast.

**Level 2 — How to use it (junior developer):**
Java provides `PriorityQueue<E>` (min-heap by default). `offer(val)` adds; `poll()` removes the minimum; `peek()` reads minimum without removal. For max-heap: `new PriorityQueue<>(Collections.reverseOrder())`. For custom ordering: `new PriorityQueue<>(Comparator.comparing(Task::getPriority))`.

**Level 3 — How it works (mid-level engineer):**
Java's `PriorityQueue` stores elements in `Object[] queue`. `offer(e)` places at index `size`, increments `size`, calls `siftUp(size-1, e)`: compares with parent at `(i-1)>>>1`, swaps if parent > child. `poll()`: stores root, places last element at root, calls `siftDown(0, element)`: compares with smaller of two children, swaps if needed, repeats.

**Level 4 — Why it was designed this way (senior/staff):**
The choice of array over pointer-based tree is deliberate: array access has perfect cache locality because parent-child relationships are adjacent in memory. Floyd's O(N) build (starting from the bottom) rather than N insertions (O(N log N)) works because the total work of sifting all interior nodes is bounded by the sum of tree heights = O(N) — a non-obvious mathematical result. The heap's partial order (not full sort) is why Heapsort is O(N log N) worst-case unlike Quicksort's O(N²) worst-case — the heap never degrades.

### ⚙️ How It Works (Mechanism)

**Array representation of min-heap:**
```
Heap array: [1, 3, 5, 7, 4, 8, 9]
Index:        0  1  2  3  4  5  6

Tree structure:
        1       (index 0)
       / \
      3   5     (index 1, 2)
     / \ / \
    7  4 8  9   (index 3, 4, 5, 6)

Parent of i: (i-1)/2
Left child:  2i+1
Right child: 2i+2
```

**Insert 2 (sift-up):**
```
Append: [1, 3, 5, 7, 4, 8, 9, 2] — index 7
Parent: (7-1)/2 = 3 → array[3]=7 > 2 → swap
        [1, 3, 5, 2, 4, 8, 9, 7]
Parent: (3-1)/2 = 1 → array[1]=3 > 2 → swap
        [1, 2, 5, 3, 4, 8, 9, 7]
Parent: (1-1)/2 = 0 → array[0]=1 < 2 → stop
Result: [1, 2, 5, 3, 4, 8, 9, 7]
```

**Extract-min (sift-down):**
```
Remove root (1). Move last (7) to root:
[7, 2, 5, 3, 4, 8, 9]
Children of 0: array[1]=2, array[2]=5 → smaller=2
7 > 2 → swap: [2, 7, 5, 3, 4, 8, 9]
Children of 1: array[3]=3, array[4]=4 → smaller=3
7 > 3 → swap: [2, 3, 5, 7, 4, 8, 9]
Children of 3: out of bounds → stop
```

┌──────────────────────────────────────────────┐
│  Min-Heap: sift-down after extract           │
│                                              │
│  Before:  7 at root                         │
│  Step 1:  7 vs 2,5 → swap with 2            │
│  Step 2:  7 vs 3,4 → swap with 3            │
│  Step 3:  7 at leaf → stop                  │
│  Result:  2 at root (new minimum)           │
└──────────────────────────────────────────────┘

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
New element arrives
→ Append to end of array
→ sift-up: compare with parent, swap if needed
→ [HEAP ← YOU ARE HERE]
→ O(1) read of minimum at index 0
→ Extract minimum: move last to root, sift-down
```

FAILURE PATH:
```
Mutable element changes comparison value after insertion
→ Heap property violated
→ poll() returns wrong element
→ Fix: never mutate elements in a PriorityQueue
```

WHAT CHANGES AT SCALE:
At 10 million elements, Java's `PriorityQueue` performs well (arrays up to ~40MB for objects). However, `siftDown` causes cache misses as it chases far-apart indices. At extreme scale, a **d-ary heap** (d=4 or d=8 children per node) reduces tree height and improves cache efficiency — used in production schedulers. For concurrent priority queues, `PriorityBlockingQueue` exists but serialises all operations; Fibonacci heaps offer O(1) decrease-key but are rarely practical in Java due to pointer overhead.

### 💻 Code Example

**Example 1 — K smallest elements from a stream:**
```java
// Using max-heap of size K to track K smallest
int[] kSmallest(int[] nums, int k) {
    // Max-heap: keeps K smallest by ejecting largest
    PriorityQueue<Integer> maxHeap =
        new PriorityQueue<>(Collections.reverseOrder());
    for (int num : nums) {
        maxHeap.offer(num);
        if (maxHeap.size() > k) maxHeap.poll();
    }
    return maxHeap.stream()
                  .mapToInt(Integer::intValue).toArray();
}
```

**Example 2 — Merge K sorted lists:**
```java
ListNode mergeKLists(ListNode[] lists) {
    // Min-heap ordered by node value
    PriorityQueue<ListNode> heap =
        new PriorityQueue<>(
            Comparator.comparingInt(n -> n.val));
    for (ListNode head : lists)
        if (head != null) heap.offer(head);

    ListNode dummy = new ListNode(0), cur = dummy;
    while (!heap.isEmpty()) {
        ListNode min = heap.poll();
        cur.next = min;
        cur = cur.next;
        if (min.next != null) heap.offer(min.next);
    }
    return dummy.next;
}
```

**Example 3 — Dijkstra's shortest path (heap-optimised):**
```java
int[] dijkstra(int[][] graph, int src) {
    int n = graph.length;
    int[] dist = new int[n];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[src] = 0;
    // Min-heap: [distance, node]
    PriorityQueue<int[]> pq =
        new PriorityQueue<>(Comparator.comparingInt(a->a[0]));
    pq.offer(new int[]{0, src});
    while (!pq.isEmpty()) {
        int[] curr = pq.poll();
        int d = curr[0], u = curr[1];
        if (d > dist[u]) continue; // stale entry
        for (int v = 0; v < n; v++) {
            if (graph[u][v] > 0) {
                int nd = dist[u] + graph[u][v];
                if (nd < dist[v]) {
                    dist[v] = nd;
                    pq.offer(new int[]{nd, v});
                }
            }
        }
    }
    return dist;
}
```

### ⚖️ Comparison Table

| Structure | find-min | insert | extract-min | Build | Best For |
|---|---|---|---|---|---|
| **Min-Heap** | O(1) | O(log N) | O(log N) | O(N) | Priority queues, top-K |
| Sorted Array | O(1) | O(N) | O(1) | O(N log N) | Read-heavy priority |
| BST (TreeMap) | O(log N) | O(log N) | O(log N) | O(N log N) | Both min + range queries |
| Unsorted Array | O(N) | O(1) | O(N) | O(1) | Write-heavy, no priority |
| Fibonacci Heap | O(1) | O(1) | O(log N) | O(N) | Decrease-key heavy graphs |

How to choose: Use `PriorityQueue` (min-heap) for all priority-queue needs in Java. Use Fibonacci heap only in graph algorithms requiring frequent `decreaseKey` and you can afford complexity. Use sorted array only when reads vastly outnumber writes.

### 🔁 Flow / Lifecycle

```
Build phase (Floyd): start at index N/2-1
  → siftDown each interior node toward leaves
  → O(N) total (fewer swaps near bottom)
     ↓
Operating phase:
  offer(e) → append + siftUp     O(log N)
  peek()   → return array[0]     O(1)
  poll()   → remove root,
             move last to root,
             siftDown             O(log N)
     ↓
Heap property maintained after every operation
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Heap is a fully sorted structure | Heap is only partially ordered: parent < children; siblings have no ordering guarantee |
| PriorityQueue.poll() returns elements in insertion order | It returns them in priority order (smallest first by default), not insertion order |
| Building a heap from N elements is O(N log N) | Floyd's algorithm builds a heap in O(N) — significantly better than N insertions |
| Heap supports O(log N) search for an arbitrary element | Heaps do not support efficient arbitrary-element search; only the root is O(1) accessible |
| A max-heap and min-heap store elements in opposite order in memory | The array layout depends on insertion order and sift operations; the same values can produce different arrays |

### 🚨 Failure Modes & Diagnosis

**1. Heap returned wrong minimum after element mutation**

Symptom: `pq.poll()` returns an element that is not the smallest; ordering appears corrupted.

Root Cause: An element inside the PriorityQueue was mutated after insertion. Heap property depends on immutable comparison values; mutation violates it.

Diagnostic:
```bash
# Add assertion before poll():
assert pq.stream().allMatch(e -> e.compareTo(pq.peek()) >= 0);
# Will fail when heap property is violated
```

Fix:
```java
// BAD: mutate inside heap
task.setPriority(1);  // still in pq — heap now invalid

// GOOD: remove, update, re-insert
pq.remove(task);
task.setPriority(1);
pq.offer(task);
```

Prevention: Elements in PriorityQueue must be effectively immutable regarding their comparison field.

---

**2. O(N) linear scan instead of O(log N) extract**

Symptom: "Priority queue" implementation is slow; profiler shows O(N) per extraction.

Root Cause: Using a sorted `List` (scanning for min on every poll) instead of a proper `PriorityQueue`.

Diagnostic:
```bash
./profiler.sh -e cpu -d 10 <pid>
# Time in Collections.min() or List.sort() called repeatedly
```

Fix: Replace `List` + `Collections.min()` with `PriorityQueue`.

Prevention: Identify "I need the smallest/largest element" use cases and always reach for `PriorityQueue`.

---

**3. PriorityQueue with wrong comparator direction**

Symptom: Algorithm returns K largest elements when K smallest were needed (or vice versa).

Root Cause: Used natural order (min-heap) when max-heap was needed, or reversed comparator incorrectly.

Diagnostic:
```bash
# Unit test with known input: [5,1,3,2,4], K=2
# K smallest should be [1,2]; if you get [4,5] → wrong heap
```

Fix:
```java
// For K smallest: use MAX heap to track K smallest
PriorityQueue<Integer> maxH =
    new PriorityQueue<>(Collections.reverseOrder());

// For K largest: use MIN heap to track K largest
PriorityQueue<Integer> minH = new PriorityQueue<>();
```

Prevention: Write the invariant in a comment: `// max-heap: top = largest of K smallest so far`.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — the heap is array-encoded; index arithmetic is the key mechanism.
- `Binary Search` — same logarithmic-height traversal logic underlies both BST search and heap sift operations.

**Builds On This (learn these next):**
- `Priority Queue` — the abstract data type that a Heap implements.
- `Heapsort` — in-place O(N log N) sort using the heap structure.
- `Dijkstra` — uses a min-heap to efficiently extract the next-closest unvisited node.

**Alternatives / Comparisons:**
- `TreeMap` — provides O(log N) min/max with range queries, but higher constant factor and no O(N) build.
- `Sorted Array` — O(1) find-min but O(N) insert; use when data is static.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Array-backed complete binary tree where   │
│              │ parent ≤ children; min at index 0         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Need O(1) find-min with O(log N) insert   │
│ SOLVES       │ — sorted array and BST both fail one      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Partial order (not full sort) is why      │
│              │ O(log N) insert AND extract are possible  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Priority queues, top-K streaming,         │
│              │ Dijkstra, event simulation, scheduling    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Arbitrary search needed; or range queries │
│              │ needed (use TreeMap/TreeSet instead)      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(1) min + O(log N) ops vs no search      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A tournament bracket that guarantees     │
│              │  the winner is always at the top"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Priority Queue → Heapsort → Dijkstra      │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** You are implementing a real-time leaderboard that must emit the top-10 players at every second from a stream of 1 million score updates per second. A max-heap of size 10 is proposed. At 1 million updates per second, what is the exact time complexity of each update, and what is the total throughput in operations per second? At what point would this approach fail to keep up in real time, and what architectural change would be needed?

**Q2.** Floyd's algorithm builds a heap in O(N) rather than O(N log N) from N insertions. The mathematical proof relies on the fact that most nodes are near the leaves where sift-down distance is short. Intuitively, why does the sum of all sift-down distances converge to O(N) rather than O(N log N)? What is the height-weight argument, and how does it differ from the analysis of N individual insertions?

