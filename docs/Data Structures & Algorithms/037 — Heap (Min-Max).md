---
layout: default
title: "Heap (Min/Max)"
parent: "Data Structures & Algorithms"
nav_order: 37
permalink: /dsa/heap-min-max/
number: "037"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, Binary Tree Concepts
used_by: Priority Queue, HeapSort, Dijkstra's Algorithm, K Largest Elements, Median of a Stream
tags:
  - datastructure
  - algorithm
  - intermediate
---

# 037 — Heap (Min/Max)

`#datastructure` `#algorithm` `#intermediate`

⚡ TL;DR — A complete binary tree stored as an array where the parent is always smaller (min-heap) or larger (max-heap) than its children, enabling O(log n) insert and O(1) peek of the min/max.

| #037 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, Binary Tree Concepts | |
| **Used by:** | Priority Queue, HeapSort, Dijkstra's Algorithm, K Largest Elements, Median of a Stream | |

---

### 📘 Textbook Definition

A **heap** is a specialised array-based binary tree satisfying the *heap property*: in a **min-heap**, every node's value is ≤ its children's values (root holds the minimum); in a **max-heap**, every node's value is ≥ its children's values (root holds the maximum). The tree is *complete* — all levels fully filled except possibly the last, which is filled left-to-right. This allows compact array storage: for node at index `i`, left child is at `2i+1`, right child at `2i+2`, parent at `(i-1)/2`. Primary operations: `insert` in O(log n), `extractMin/Max` in O(log n), `peek` in O(1). Java's `PriorityQueue` is a min-heap implementation.

### 🟢 Simple Definition (Easy)

A min-heap is like a tournament bracket — the smallest player always rises to the top position. Inserting a new player or removing the champion takes O(log n) time.

### 🔵 Simple Definition (Elaborated)

A heap is a partially sorted structure: you only guarantee that the minimum (or maximum) element is at the top, not that everything is fully sorted. This partial ordering is far cheaper to maintain than full sorting — O(log n) insert vs O(n log n) full sort — yet it gives you instant access to the most important element. The clever trick: store the entire binary tree in a flat array using index arithmetic for parent-child relationships, avoiding pointer overhead. This makes heaps extremely cache-friendly. Java's `PriorityQueue` wraps a min-heap; for a max-heap, pass `Comparator.reverseOrder()`.

### 🔩 First Principles Explanation

**Why a heap instead of a sorted array for priority queues?**

- Sorted array: insert O(n) (shift), extract-min O(1) (first element).
- Sorted linked list: insert O(n) (find position), extract-min O(1).
- Heap: insert O(log n), extract-min O(log n). **Best trade-off** for dynamic workloads.

**Array-to-tree mapping (1-indexed for clarity):**

```
Heap array: [1, 3, 5, 7, 9, 11] (min-heap)

Binary tree view:
          1         (index 1)
        /   \
       3     5      (index 2, 3)
      / \   /
     7   9 11       (index 4, 5, 6)

0-indexed: parent(i) = (i-1)/2
           left(i)   = 2i+1
           right(i)  = 2i+2
```

**Insert (heapify-up / sift-up):**

```
Insert 2 into min-heap [1, 3, 5, 7, 9, 11]:
1. Append at end: [1, 3, 5, 7, 9, 11, 2]
2. Compare with parent: 2 < parent(11)? Wait — index 6, parent = (6-1)/2 = 2
   parent = arr[2] = 5. 2 < 5 → swap
   [1, 3, 2, 7, 9, 11, 5]
3. Compare with parent: index 2, parent = (2-1)/2 = 0
   parent = arr[0] = 1. 2 > 1 → stop
Result: [1, 3, 2, 7, 9, 11, 5]
```

**Extract min (heapify-down / sift-down):**

```
Extract from min-heap [1, 3, 2, 7, 9, 11, 5]:
1. Save root (1 = min); move last element to root
   [5, 3, 2, 7, 9, 11]
2. Sift-down: compare 5 with children 3, 2. Min child = 2. 5 > 2 → swap
   [2, 3, 5, 7, 9, 11]
3. Compare 5 with children (indices 5, 6 — none exist). Stop.
Result: [2, 3, 5, 7, 9, 11], returned 1
```

**Build heap from array (heapify): O(n)** — surprising but provable: sifting down from last non-leaf to root. Despite each sift taking O(log n), the majority of nodes are near the bottom (shallow sifts), yielding O(n) total.

### ❓ Why Does This Exist (Why Before What)

WITHOUT a heap (using sorted array for priority queue):

- Dynamic priority queue with frequent inserts: O(n) per insert for sorted array.
- Dijkstra's algorithm would be O(V²) without heap, O(E log V) with heap.
- K-largest problems: O(n log n) sort vs O(n log k) with heap.

What breaks without it:
1. Real-time systems processing tasks by priority: O(n) per task insertion is unacceptable.
2. Stream median maintenance impossible efficiently without two heaps.

WITH Heap:
→ Priority queue in O(log n) — enables efficient scheduling, shortest path, top-K.
→ HeapSort algorithm: O(n log n) guaranteed, O(1) space (in-place).
→ Streaming algorithms: maintain running min/max/median on infinite data.

### 🧠 Mental Model / Analogy

> A min-heap is like a company org chart where the CEO (smallest value) is always at the top, and every manager is less important (larger value) than their subordinates… wait, reversed: every manager's salary is *less* than each direct report. Hiring (insert): a new person starts at the bottom, then gets "promoted" as long as they outperform their manager. Firing the CEO (extract-min): the last hired takes the top spot temporarily, then gets "demoted" to where they belong.

"CEO" = minimum root, "promotion" = sift-up after insert, "demotion" = sift-down after extract, "org chart" = heap tree.

### ⚙️ How It Works (Mechanism)

**Complexity summary:**

```
Operation        Min-Heap       Max-Heap
──────────────────────────────────────────
peek (min/max)   O(1)           O(1)
insert           O(log n)       O(log n)
extract min/max  O(log n)       O(log n)
build from array O(n)           O(n)
decrease key     O(log n)       O(log n)
delete arbitrary O(log n)       O(log n)
```

**Heapify-down code:**

```java
void siftDown(int[] arr, int n, int i) {
    int smallest = i;
    int left  = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < n && arr[left] < arr[smallest])
        smallest = left;
    if (right < n && arr[right] < arr[smallest])
        smallest = right;

    if (smallest != i) {
        swap(arr, i, smallest);
        siftDown(arr, n, smallest); // recurse down
    }
}
```

### 🔄 How It Connects (Mini-Map)

```
Array (compact storage)
        ↓ structured as complete binary tree
Heap (Min or Max) ← you are here
        ↓ implements
PriorityQueue (Java standard library)
        ↓ used in
HeapSort | Dijkstra | Prim's MST
Top-K / K Largest Elements
Median of a Stream (two heaps)
```

### 💻 Code Example

Example 1 — Java PriorityQueue (min-heap by default):

```java
// Min-Heap: PriorityQueue defaults to natural ordering
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(5); minHeap.offer(1); minHeap.offer(3);

System.out.println(minHeap.peek());  // 1 — min, O(1)
System.out.println(minHeap.poll());  // 1 — extract min, O(log n)
System.out.println(minHeap.poll());  // 3

// Max-Heap: reverse comparator
PriorityQueue<Integer> maxHeap =
    new PriorityQueue<>(Comparator.reverseOrder());
maxHeap.offer(5); maxHeap.offer(1); maxHeap.offer(3);
System.out.println(maxHeap.poll()); // 5 — extract max
```

Example 2 — K Largest Elements:

```java
// Find K largest elements in stream/array — O(n log k)
public int[] kLargest(int[] nums, int k) {
    // Min-heap of size k: root is smallest of the k largest
    PriorityQueue<Integer> minHeap = new PriorityQueue<>();

    for (int num : nums) {
        minHeap.offer(num);
        if (minHeap.size() > k) {
            minHeap.poll(); // remove the smallest (not in top-k)
        }
    }
    // Remaining k elements are the k largest
    return minHeap.stream().mapToInt(i -> i).toArray();
}
// Input: [3,1,4,1,5,9,2,6], k=3 → [5,6,9] (or similar order)
```

Example 3 — Median of a Data Stream (two heaps):

```java
class MedianFinder {
    // maxHeap: lower half; minHeap: upper half
    PriorityQueue<Integer> lo =
        new PriorityQueue<>(Comparator.reverseOrder());
    PriorityQueue<Integer> hi = new PriorityQueue<>();

    void addNum(int num) {
        lo.offer(num);                    // add to lower half
        hi.offer(lo.poll());              // balance: move max-of-lo to hi
        if (lo.size() < hi.size()) {
            lo.offer(hi.poll());          // keep |lo| >= |hi|
        }
    }

    double findMedian() {
        if (lo.size() > hi.size()) return lo.peek();
        return (lo.peek() + hi.peek()) / 2.0;
    }
}
// addNum: O(log n), findMedian: O(1)
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A heap is a fully sorted structure | A heap only guarantees the root is min/max. Internal ordering is partial — you cannot iterate a heap to get sorted order without repeatedly extracting. |
| Java PriorityQueue iterates in sorted order | PriorityQueue.iterator() does NOT return elements in sorted order. Only repeated poll() extracts in priority order. |
| HeapSort is the fastest sort | HeapSort is O(n log n) worst case (better than QuickSort's O(n²) worst), but QuickSort with good pivot selection outperforms HeapSort in practice due to cache locality. |
| Building a heap with repeated inserts is O(n log n) | Repeated inserts are O(n log n). The O(n) build-heap algorithm uses sift-down from the last non-leaf — not repeated inserts. |
| Heap and TreeMap have the same use case | Heap gives O(1) min/max access but no range queries. TreeMap gives O(log n) sorted access and range queries. Heap is better for pure priority queue; TreeMap for sorted map operations. |

### 🔥 Pitfalls in Production

**1. Mutating Objects in PriorityQueue After Insertion**

```java
// BAD: Mutating an object whose compareTo uses mutable state
PriorityQueue<Task> pq = new PriorityQueue<>(
    Comparator.comparing(t -> t.priority));
Task task = new Task("A", 5);
pq.offer(task);
task.priority = 1; // mutate!
// PriorityQueue doesn't detect this; ordering is now wrong
Task head = pq.poll(); // may NOT be the minimum priority task!

// GOOD: Remove, update, re-insert (expensive but correct)
pq.remove(task); task.priority = 1; pq.offer(task);
// Or: use immutable value objects as queue elements
```

**2. PriorityQueue Not Thread-Safe**

```java
// BAD: Shared PriorityQueue in multi-threaded context
PriorityQueue<Task> queue = new PriorityQueue<>();
// multiple threads offering/polling → corruption

// GOOD: Use PriorityBlockingQueue for thread safety
BlockingQueue<Task> queue = new PriorityBlockingQueue<>();
```

**3. Using Sorted Collection (TreeSet) Instead of Heap for Priority Queue**

```java
// BAD: TreeSet for priority queue — O(log n) but more overhead
// TreeSet requires unique elements; duplicates are dropped!
TreeSet<Integer> pq = new TreeSet<>();
pq.add(5); pq.add(5); // only one 5 stored!

// GOOD: PriorityQueue allows duplicates
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(5); pq.offer(5); // both stored
```

### 🔗 Related Keywords

- `Priority Queue` — the abstract data type a heap implements.
- `HeapSort` — O(n log n) in-place sorting algorithm using heap operations.
- `Dijkstra's Algorithm` — uses a min-heap to efficiently find shortest paths.
- `Array` — the backing storage for heap's compact representation.
- `TreeMap` — sorted alternative; use when non-priority sorted access needed.
- `Median of a Stream` — two-heap technique for O(log n) add + O(1) median.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Complete binary tree in array: O(1) peek  │
│              │ min/max; O(log n) insert/extract.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Priority queue, top-K, stream median,     │
│              │ Dijkstra / Prim shortest path / MST.      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need sorted iteration → TreeMap/TreeSet;  │
│              │ range queries → TreeMap.                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Heap: the minimum/maximum is always at   │
│              │ the top — O(1) to see, O(log n) to use."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Priority Queue → HeapSort → Dijkstra's    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The O(n) build-heap algorithm is counterintuitive — inserting n elements one by one is O(n log n), but building from an unsorted array in a single pass is O(n). Prove this mathematically by summing the work done by sift-down operations across all levels of a complete binary tree with n nodes, explaining why the sum converges to O(n) and at which tree level the majority of work is concentrated.

**Q2.** The "median of a stream" algorithm uses two heaps: a max-heap for the lower half and a min-heap for the upper half. The invariant is that the max-heap's root ≤ min-heap's root, and their sizes differ by at most 1. Trace the algorithm through the stream `[5, 15, 1, 3, 2, 8]`, show the heap states after each insertion, and identify the one scenario where `lo.peek() > hi.peek()` could temporarily violate the invariant during insertion — and which specific step in the algorithm restores it.

