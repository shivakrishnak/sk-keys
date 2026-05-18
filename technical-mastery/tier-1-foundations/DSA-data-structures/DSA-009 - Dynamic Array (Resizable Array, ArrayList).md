---
id: DSA-009
title: Dynamic Array (Resizable Array, ArrayList)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-008
used_by: DSA-028, DSA-030, DSA-031, DSA-046
related: DSA-008, DSA-010, DSA-070
tags:
  - data-structures
  - array
  - dynamic
  - arraylist
  - amortized
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/dsa/dynamic-array/
---

## TL;DR

A dynamic array solves the static array's fixed-size problem
by doubling capacity on overflow - achieving O(1) amortized
append while retaining O(1) random access.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-009 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, array, amortized, ArrayList |
| **Prerequisites** | DSA-008 |

---

### The Problem This Solves

Static arrays require knowing the size upfront. In practice,
collection sizes are rarely known ahead of time. Dynamic
arrays add a managed resize mechanism that keeps the O(1)
access benefit of arrays while removing the size constraint.

**EVOLUTION:**
Dynamic arrays are implemented in every major language:
Java's `ArrayList`, Python's `list`, C++'s `std::vector`,
Go's `slice`. The doubling strategy for amortized O(1) append
was formalized in the 1980s; it is now a fundamental pattern
in data structure design.

---

### Textbook Definition

A dynamic array (resizable array) wraps a static array.
When the array is full and a new element is appended, it
allocates a new array (typically 2x the current size),
copies all elements, and frees the old array. All existing
elements retain O(1) access by index. Append is O(1)
amortized because the O(n) resize happens rarely enough that
its cost, spread over n appends, is O(1) per append.

---

### Understand It in 30 Seconds

Start with a box holding 4 items. When it fills:
1. Get a box holding 8 items
2. Move all 4 existing items into the new box
3. Discard the old box

The next 4 additions are free (there is space). The cost of
moving 4 items is paid over the 4 previous adds.
Average cost per add: (4 moves + 4 free adds) / 8 total adds
= 0.5 moves per add → O(1) amortized.

---

### First Principles

**Why doubling (not +1 or +10)?**

If you grow by 1 each time: n adds → n resizes → n copies
total. Total copies = 1+2+...+n = O(n^2). Each add is O(n)
amortized. Bad.

If you grow by 2x each time: n adds → log(n) resizes.
Total copies = 1+2+4+...+n = O(n). Each add is O(1)
amortized. Good.

The doubling factor is the minimal constant that achieves
O(1) amortized. Java uses 1.5x (capacity + capacity>>1)
as a space-time compromise.

---

### Thought Experiment

1,000 appends to a dynamic array that doubles (starts at 1):
- Resizes at: 1, 2, 4, 8, 16, ... 512 (10 resizes)
- Elements copied: 1+2+4+...+512 = 1023 copies
- 1,000 appends + 1,023 copies = 2,023 total operations
- Amortized: 2.023 operations per append ≈ O(1)

---

### Mental Model / Analogy

**The hotel booking model:**
A hotel starts with 1 room. When fully booked and a new guest
arrives, they build a hotel with 2x the rooms and move
everyone. Expensive per move, but moves happen logarithmically
often as the guest count grows.

---

### Gradual Depth - Five Levels

**Level 1 - Five-year-old:**
A magic growing bag. When full, it silently swaps itself for
a bag that is twice as big.

**Level 2 - Junior developer:**
`ArrayList` in Java grows automatically. When you `add()` and
it's full, it allocates a new internal array, copies all
elements, then adds the new one. You don't manage size.

**Level 3 - Mid engineer:**
Understand the resize cost: O(n) per resize, amortized O(1)
per add. Capacity vs size distinction: `size()` is the
number of elements; capacity is the backing array length.
`ensureCapacity(n)` pre-allocates to avoid resizes when
the final size is known.

**Level 4 - Senior/staff engineer:**
In high-throughput systems, ArrayList resize triggers GC
pressure: the old backing array becomes garbage. Pre-size
ArrayLists when the expected size is known. In Java, the
`ArrayList(initialCapacity)` constructor avoids all resizes
if initialCapacity >= final size.

**Level 5 - Expert/architect:**
Off-heap memory (DirectByteBuffer, sun.misc.Unsafe) uses
array-like contiguous memory without GC overhead. High-
performance messaging systems (Aeron, LMAX Disruptor) use
ring buffers (fixed-size circular arrays) with atomic
indexes to avoid allocation entirely. The "dynamic array"
becomes a pre-allocated circular buffer.

---

### How It Works

**Java ArrayList internals:**

```java
// BAD: no initial capacity hint, forces multiple resizes
List<User> users = new ArrayList<>();
for (User u : fetchAllUsers()) {  // 100k users
    users.add(u);
    // resizes at 10, 15, 22, 33... ~17 times for 100k
}

// GOOD: pre-size when count is known
int count = userDao.count();  // one count query
List<User> users = new ArrayList<>(count);
for (User u : fetchAllUsers()) {
    users.add(u);  // zero resizes
}
```

**Resize sequence (Java, initial capacity 10, growth 1.5x):**

```
Capacity:  10 → 15 → 22 → 33 → 49 → 73 → 109 → ...
Resize at: 11th, 16th, 23rd, 34th, 50th element...
```

**Memory layout before/after resize:**

```
BEFORE (capacity=4, size=4):
[A][B][C][D] <- backing array (full)

append(E) triggers resize:
1. Allocate [_][_][_][_][_][_][_][_] (capacity=8)
2. Copy:   [A][B][C][D][_][_][_][_]
3. Add E:  [A][B][C][D][E][_][_][_]
4. Old array becomes GC garbage
```

---

### Comparison Table

| | Static Array | Dynamic Array | Linked List |
|--|-------------|---------------|-------------|
| Access | O(1) | O(1) | O(n) |
| Append | O(1) | O(1) amortized | O(1) at tail |
| Insert (mid) | O(n) | O(n) | O(1) at known node |
| Delete (mid) | O(n) | O(n) | O(1) at known node |
| Memory | Compact | Compact+waste | Scattered+overhead |
| Cache | Excellent | Excellent | Poor |
| Size | Fixed | Dynamic | Dynamic |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "ArrayList.add() is always O(1)" | O(1) amortized; occasional O(n) resize; matters for latency-sensitive code |
| "ArrayList and LinkedList are equivalent" | ArrayList: O(1) random access, O(n) mid-insert. LinkedList: O(n) access, O(1) insert at known node. Very different |
| "You should always use LinkedList for frequent adds" | Frequent adds at END → ArrayList. Random position adds → LinkedList (if position known). Cache behavior usually favors ArrayList |
| "Capacity and size are the same" | Size = number of elements; Capacity = backing array length; always capacity >= size |

---

### Failure Modes & Diagnosis

**Failure 1: Repeated resize in performance-critical path**
- Symptom: GC spikes correlating with ArrayList growth
- Cause: No initial capacity; backing array resizes 10-15
  times for large collections
- Diagnosis: GC logs showing frequent tenured object
  allocation; heap profiler showing old ArrayList[] arrays
- Fix: `new ArrayList<>(expectedSize)`

**Failure 2: Off-heap copy for "immutable" snapshot**
- Symptom: Unexpected mutation of a "copy" of a list
- Cause: `List<T> copy = new ArrayList<>(original)` copies
  references, not objects
- Fix: Deep copy if objects are mutable; document clearly

**Failure 3: ConcurrentModificationException**
- Symptom: Exception on list iteration under concurrent writes
- Cause: ArrayList is not thread-safe; iterator detects
  structural modification via `modCount`
- Fix: Use `CopyOnWriteArrayList` for read-heavy concurrent
  access; synchronize externally for write-heavy

---

### Related Keywords

**Prerequisites:**
- [[DSA-008 - Array (Static Array)]]

**Builds toward:**
- [[DSA-028 - Heap (Min-Heap and Max-Heap)]]
- [[DSA-030 - Merge Sort]]
- [[DSA-070 - Amortized Analysis]]

**See also:**
- [[DSA-010 - Linked List (Singly Linked)]]

---

### Quick Reference Card

| Operation | Complexity |
|-----------|-----------|
| Access arr[i] | O(1) |
| Append at end | O(1) amortized |
| Insert at middle | O(n) |
| Delete at middle | O(n) |
| Search | O(n) unsorted, O(log n) sorted |
| Size/isEmpty | O(1) |

**When to use:** The default list implementation for most
use cases. Pre-size when final count is known.

**When NOT to use:** Frequent insert/delete at arbitrary
positions (use `LinkedList` or redesign); thread-safe
access without external sync (use `CopyOnWriteArrayList`).

---

### The Surprising Truth

Java's `ArrayList` uses a growth factor of 1.5 rather than
2.0 (the theoretical optimum for amortized analysis) to
reduce memory waste. Python's list uses a more complex
growth formula (roughly 1.125x + 6) tuned for small lists
that are common in Python programs. The "correct" growth
factor is workload-dependent.

---

### Mastery Checklist

- [ ] Can explain amortized O(1) append using the accounting
      method (each append pre-pays for future resize cost)
- [ ] Knows the initial capacity and growth factor of
      ArrayList in the primary working language
- [ ] Uses `ensureCapacity` or sized constructor when
      final size is predictable
- [ ] Can explain why ConcurrentModificationException
      occurs and how to fix it
- [ ] Has measured the GC impact of unsized vs pre-sized
      ArrayList in a benchmark

---

### Think About This

1. Java's `ArrayList.remove(index)` shifts all elements
   after the index left by one. What is the complexity?
   Is `remove(object)` more or less expensive? Why?

2. You need to process 1 million records and collect the
   results. You don't know the final count. Should you
   use `LinkedList` or `ArrayList`? What if you're
   inserting at the beginning each time?

3. **TYPE G:** A microservice builds a response list from
   a database query. The query returns between 10 and
   100,000 rows depending on the filter. You notice GC
   pauses during peak load. How do you diagnose whether
   ArrayList resizing is the cause, and what is the fix?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between `size()` and
`capacity()` in an ArrayList?

> `size()`: the number of elements currently stored.
> `capacity`: the length of the internal backing array
> (not directly exposed in Java's ArrayList - only via
> `ensureCapacity` and internal field inspection).
> Always: capacity >= size. When size == capacity, the
> next add triggers a resize.

**Q2 (Medium):** Explain why ArrayList.add(index, element)
is O(n) in the worst case but O(1) amortized does not apply.

> Adding at arbitrary index always requires shifting all
> elements from index to the end: index 0 means shifting
> all n elements. No amortization applies because the O(n)
> shift cost occurs on EVERY such insertion, not just on
> capacity overflow. Amortized O(1) applies only to
> `add(element)` at the end, where resizes are infrequent.

**Q3 (Hard):** How would you implement a thread-safe variant
of ArrayList that supports high-read, low-write workloads?

> `CopyOnWriteArrayList`: on every write, create a complete
> copy of the backing array, mutate the copy, then atomically
> replace the reference. Reads use the current array without
> locking (read-heavy workloads get O(1) access, no
> contention). Writes are O(n) (full copy). Iterators
> operate on a snapshot and never throw
> ConcurrentModificationException. Trade-off: write cost
> is O(n), suitable only when reads >> writes.
