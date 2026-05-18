---
id: DSA-028
title: "Heap (Min-Heap and Max-Heap)"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-016, DSA-022
used_by: DSA-029, DSA-063, DSA-083, DSA-086
related: DSA-016, DSA-029, DSA-086
tags:
  - data-structures
  - heap
  - min-heap
  - max-heap
  - priority
  - complete-binary-tree
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/dsa/heap/
---

## TL;DR

A heap is a complete binary tree with the heap property:
parent is always smaller (min-heap) or larger (max-heap)
than children - giving O(1) peek at the extreme and O(log n)
insert/delete.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-028 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, heap, priority, O(log n) |
| **Prerequisites** | DSA-016, DSA-022 |

---

### The Problem This Solves

You need to repeatedly extract the minimum (or maximum)
value from a collection that is changing. Sorted array:
O(n) insert. BST: O(log n) but complex balancing. Heap:
O(log n) insert and delete, O(1) peek - the optimal
structure for priority-based access.

**EVOLUTION:**
Heaps were introduced by J.W.J. Williams in 1964 for
heapsort. The key insight is the array-based implicit
representation: a complete binary tree stored as a flat
array where children of index i are at 2i+1 and 2i+2.
No pointers needed.

---

### Textbook Definition

A binary heap is a complete binary tree satisfying the heap
property. Min-heap: each parent <= its children; the minimum
element is at the root. Max-heap: each parent >= its children;
the maximum is at root. "Complete binary tree" means all
levels filled except possibly the last, filled left-to-right.
Operations: insert O(log n) via sift-up; extract-min/max
O(log n) via sift-down; peek-min/max O(1).

---

### Understand It in 30 Seconds

Min-heap with values [3, 5, 8, 10, 7]:

```
        3         ← minimum always at root
       / \
      5   8
     / \
    10   7
```

Peek min: O(1) - always root (3).
Insert 2: add at bottom, "bubble up" until heap property
  restored: 2 swaps with 7, then 5, then 3 → 2 at root.
Extract min: remove root (3), put last element (7) at root,
  "sift down" until heap property restored.

---

### How It Works

**Array representation (no pointers needed):**

```
Index: 0  1  2   3   4   5
Array: 3  5  8  10   7  (...)

For index i:
  parent     = (i-1) / 2
  left child = 2*i + 1
  right child= 2*i + 2
```

**Min-heap implementation:**

```java
class MinHeap {
    private int[] heap;
    private int size;

    MinHeap(int capacity) {
        heap = new int[capacity];
        size = 0;
    }

    int peek() { return heap[0]; }  // O(1)

    void insert(int val) {          // O(log n)
        heap[size] = val;
        siftUp(size++);
    }

    int extractMin() {              // O(log n)
        int min = heap[0];
        heap[0] = heap[--size];
        siftDown(0);
        return min;
    }

    private void siftUp(int i) {
        while (i > 0) {
            int parent = (i - 1) / 2;
            if (heap[parent] <= heap[i]) break;
            swap(i, parent);
            i = parent;
        }
    }

    private void siftDown(int i) {
        while (true) {
            int smallest = i;
            int left = 2*i + 1, right = 2*i + 2;
            if (left < size && heap[left] < heap[smallest])
                smallest = left;
            if (right < size && heap[right] < heap[smallest])
                smallest = right;
            if (smallest == i) break;
            swap(i, smallest);
            i = smallest;
        }
    }

    private void swap(int i, int j) {
        int tmp = heap[i]; heap[i] = heap[j]; heap[j] = tmp;
    }
}
```

**Java PriorityQueue (built-in min-heap):**

```java
// Min-heap (default)
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(5);
minHeap.offer(2);
minHeap.offer(8);
minHeap.peek();    // 2 - minimum, O(1)
minHeap.poll();    // 2 - removes minimum, O(log n)

// Max-heap
PriorityQueue<Integer> maxHeap =
    new PriorityQueue<>(Comparator.reverseOrder());
maxHeap.offer(5);
maxHeap.peek();    // max element
```

**Classic heap use case - k largest elements:**

```java
// Find k largest in O(n log k) instead of O(n log n) sort
List<Integer> kLargest(int[] nums, int k) {
    // Min-heap of size k: maintains k largest seen so far
    PriorityQueue<Integer> minHeap = new PriorityQueue<>();
    for (int n : nums) {
        minHeap.offer(n);
        if (minHeap.size() > k) minHeap.poll(); // remove min
    }
    return new ArrayList<>(minHeap);
    // Contains k largest elements
}
```

---

### Comparison Table

| Structure | Peek min | Insert | Extract min | Ordered iteration |
|-----------|---------|--------|-------------|------------------|
| Array (unsorted) | O(n) | O(1) | O(n) | O(n log n) sort |
| Array (sorted) | O(1) | O(n) | O(1) | O(1) |
| Min-Heap | O(1) | O(log n) | O(log n) | O(n log n) |
| BST (balanced) | O(log n) | O(log n) | O(log n) | O(n) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Heap is a sorted data structure" | Heap only guarantees parent < children; siblings have no ordering relative to each other |
| "Java PriorityQueue is a max-heap" | It is a min-heap by default; use `Comparator.reverseOrder()` for max-heap |
| "Heap search is O(1)" | Heap search is O(n); heap only optimizes minimum/maximum access, not arbitrary search |

---

### Failure Modes & Diagnosis

**Failure: Modifying elements in PriorityQueue breaks heap order**
- Cause: PriorityQueue does not update priority when an
  element is mutated externally - the heap property is
  violated
- Fix: Remove the element, modify it, re-insert. Or use
  a TreeMap for indexed priority tracking

**Failure: Using PriorityQueue.contains() in hot paths**
- Cause: `contains()` is O(n) on PriorityQueue (linear scan)
- Diagnosis: Performance profiler shows time in `contains()`
- Fix: Maintain a separate HashSet for O(1) membership test

---

### Related Keywords

**Prerequisites:**
- [[DSA-016 - Binary Tree]]

**Builds toward:**
- [[DSA-029 - Priority Queue]]
- [[DSA-091 - Quickselect (k-th Largest Element)]]

**See also:**
- [[DSA-063 - Dijkstra's Algorithm]]

---

### Quick Reference Card

| Operation | Time | Java API |
|-----------|------|---------|
| peek min | O(1) | `pq.peek()` |
| insert | O(log n) | `pq.offer(val)` |
| extract min | O(log n) | `pq.poll()` |
| contains | O(n) | `pq.contains(val)` |
| build heap | O(n) | new PriorityQueue<>(list) |

**3 things:** O(1) peek, O(log n) insert/extract, O(n)
search.

**One-liner for interviews:** "A heap is an array-backed
complete binary tree; parent always beats children; gives
O(1) min/max access and O(log n) insert/delete."

---

### Transferable Wisdom

The heap pattern - "maintain only the k most relevant items,
discard the rest" - appears everywhere:
- Top K queries in analytics
- Priority scheduling in OS kernels
- Dijkstra's shortest path (priority queue over distances)
- Merge K sorted streams (heap over heads of each stream)
- Event simulation (process events in chronological order)

Any time you say "give me the most/least of these continuously
changing items", reach for a heap.

---

### The Surprising Truth

Building a heap from n elements takes O(n), not O(n log n)
as you might expect from inserting n items one by one.
Starting from the last internal node and sifting down each
node, lower levels have more nodes but shorter sift paths.
The total work sums to O(n) via geometric series. This O(n)
buildHeap is what makes Heapsort's worst case O(n log n)
with O(1) additional space - better than quicksort's
average O(n log n) but O(n²) worst.

---

### Mastery Checklist

- [ ] Can explain heap property, array representation, and
      sift-up/sift-down
- [ ] Uses Java `PriorityQueue` correctly (min-heap default,
      reverseOrder for max-heap)
- [ ] Recognizes the "k largest/smallest" pattern and
      solves it with a heap in O(n log k)
- [ ] Knows that `PriorityQueue.contains()` is O(n)

---

### Think About This

1. You receive a continuous stream of integers and at any
   point must return the median. Can you maintain the
   median using two heaps? How?

2. Merge 1000 sorted files of 1MB each into one sorted
   output. RAM is limited to 50MB. How does a min-heap
   over file heads solve this?

3. **TYPE G:** A background job scheduler receives tasks
   with integer priorities (lower = higher priority).
   Tasks can be submitted and started concurrently.
   What data structure and Java type serves this?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between a min-heap
and a max-heap, and what does Java PriorityQueue use?

> Min-heap: parent <= children; root holds the minimum.
> Max-heap: parent >= children; root holds the maximum.
> Java PriorityQueue is a min-heap by default (peek/poll
> returns the smallest element per the natural ordering or
> comparator). For a max-heap, use
> `new PriorityQueue<>(Comparator.reverseOrder())`.

**Q2 (Medium):** How do you find the k-th largest element
in an array using a heap, and what is the time complexity?

> Maintain a min-heap of size k. Iterate through the array:
> push each element; if heap size exceeds k, pop the min.
> After processing all n elements, the heap contains the
> k largest elements, and the root is the k-th largest.
> Time: O(n log k) - n iterations, each heap op is O(log k).
> Space: O(k). This beats O(n log n) sort when k << n.

**Q3 (Hard):** Find the median of a data stream. Design
a data structure supporting `addNum(int)` in O(log n)
and `findMedian()` in O(1).

> Maintain two heaps: a max-heap of the lower half and a
> min-heap of the upper half. After each `addNum`:
> balance the heaps so their sizes differ by at most 1.
> For even count: median = (max-heap.peek() + min-heap.peek()) / 2.
> For odd count: median = peek of the larger heap.
> Rebalancing: if sizes differ by 2, move the root of the
> larger to the smaller. Each add = O(log n). findMedian = O(1).
