---
id: DSA-041
title: Circular Buffer (Ring Buffer)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-008, DSA-013
used_by: DSA-045
related: DSA-013, DSA-045
tags:
  - data-structures
  - circular-buffer
  - ring-buffer
  - fixed-capacity
  - o-1
  - streaming
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/dsa/circular-buffer/
---

## TL;DR

A circular buffer is a fixed-size array treated as a ring -
head and tail pointers wrap around, giving O(1) enqueue and
dequeue with zero allocation. The data structure behind
most I/O and networking buffers.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-041 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, ring-buffer, streaming, O(1) |
| **Prerequisites** | DSA-008, DSA-013 |

---

### The Problem This Solves

A regular queue backed by a linked list allocates a node
on every enqueue (GC pressure). A regular array queue
must shift elements on dequeue (O(n)). A circular buffer
reuses fixed memory with O(1) operations and zero allocation
after initialization - essential for real-time and
low-latency systems.

---

### Textbook Definition

A circular buffer (ring buffer) is a fixed-capacity data
structure using a single array where the tail pointer wraps
back to index 0 after reaching the end. Two pointers:
head (next read) and tail (next write). Full when
(tail + 1) % capacity == head. Empty when head == tail.
All operations: O(1) with zero allocation.

---

### How It Works

```java
class CircularBuffer<T> {
    private Object[] data;
    private int head = 0, tail = 0, size = 0;
    private int capacity;

    CircularBuffer(int capacity) {
        this.capacity = capacity;
        this.data = new Object[capacity];
    }

    // Add to tail: O(1)
    boolean offer(T item) {
        if (size == capacity) return false;  // full
        data[tail] = item;
        tail = (tail + 1) % capacity;        // wrap around
        size++;
        return true;
    }

    // Remove from head: O(1)
    @SuppressWarnings("unchecked")
    T poll() {
        if (size == 0) return null;         // empty
        T item = (T) data[head];
        data[head] = null;                  // help GC
        head = (head + 1) % capacity;       // wrap around
        size--;
        return item;
    }

    boolean isEmpty() { return size == 0; }
    boolean isFull()  { return size == capacity; }
    int size()        { return size; }
}
```

**Ring buffer visualization (capacity=5):**

```
Initial:  [_, _, _, _, _]  head=0, tail=0
After 3 enqueues:
          [A, B, C, _, _]  head=0, tail=3
After 2 dequeues:
          [_, _, C, _, _]  head=2, tail=3
After 3 more enqueues:
          [E, F, C, D, _]  head=2, tail=1 (wrapped!)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Circular buffer is just a queue" | It's a bounded queue with O(1) ops and zero allocation - different performance profile |
| "Full detection is head == tail" | Empty = head==tail; full = (tail+1)%cap == head (one slot wasted) or use a size counter |

---

### Quick Reference Card

| Property | Value |
|---------|-------|
| Space | O(capacity) fixed, pre-allocated |
| enqueue/dequeue | O(1) |
| Allocation after init | Zero (key advantage) |
| Java equivalent | `ArrayDeque` (unbounded, grows) |
| Use case | Streaming, I/O buffers, LMAX Disruptor |

---

### Mastery Checklist

- [ ] Can implement circular buffer with head/tail pointers
      and modular wrap-around
- [ ] Understands the full vs empty detection distinction
- [ ] Knows the zero-allocation advantage over linked queues

---

### Interview Deep-Dive

**Q1 (Medium):** Implement a circular buffer that returns
the last N elements of a stream.

> Fixed-size circular buffer of capacity N. Enqueue
> overwrites oldest element when full (instead of returning
> false). Use head and tail with modular arithmetic. When
> full: overwrite data[tail], advance both tail and head
> (oldest element is gone).
> This "sliding window over a stream" is used in metrics
> collection (last N requests), moving averages, and
> video encoding frame buffers.
