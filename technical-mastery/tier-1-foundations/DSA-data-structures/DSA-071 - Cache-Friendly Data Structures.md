---
id: DSA-071
title: Cache-Friendly Data Structures
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-023, DSA-011, DSA-004
used_by: DSA-072
related: DSA-004, DSA-011, DSA-070
tags:
  - data-structures
  - cache
  - memory-hierarchy
  - spatial-locality
  - temporal-locality
  - performance
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 71
permalink: /technical-mastery/dsa/cache-friendly-data-structures/
---

## TL;DR

Cache-friendly data structures access memory sequentially
(arrays), while cache-unfriendly ones scatter pointer
chases (linked lists, trees) - the difference between
10ns and 100ns per access even for the same Big-O.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-071 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, cache, memory-hierarchy |
| **Prerequisites** | DSA-023, DSA-011, DSA-004 |

---

### The Problem This Solves

Two algorithms with identical O(n) complexity can differ
by 10x in runtime due to cache behavior. A linked list
traversal with random pointer chase can be 100x slower
than an array scan of the same size, despite identical
Big-O. Understanding memory hierarchy is the difference
between theoretical and practical performance.

---

### Textbook Definition

Cache-friendly data structures exploit spatial and temporal
locality:
- Spatial locality: accessing nearby memory addresses;
  CPU loads cache lines (typically 64 bytes), so accessing
  one element prefetches adjacent elements
- Temporal locality: accessing recently used data again;
  hot data stays in L1/L2 cache

Memory hierarchy (typical latency):
- L1 cache: ~1ns, 32KB
- L2 cache: ~4ns, 256KB
- L3 cache: ~10ns, 8-32MB
- RAM: ~100ns, GB

---

### How It Works

**Array vs Linked List traversal:**

```java
// Cache-FRIENDLY: Array traversal (sequential access)
// CPU prefetches next elements automatically
int[] arr = new int[1_000_000];
int sum = 0;
for (int x : arr) sum += x; // ~1ms for 1M elements

// Cache-UNFRIENDLY: Linked list traversal
// Each next pointer chase = potential cache miss → 100ns
Node head = buildLinkedList(1_000_000);
Node curr = head;
int sum2 = 0;
while (curr != null) {
    sum2 += curr.val;
    curr = curr.next; // random pointer → cache miss
}
// ~100ms for 1M elements (same Big-O but 100x slower!)
```

**Why B-trees beat binary trees in databases:**

```
Binary tree: each node has 1 key, 2 pointers
- Node = 24 bytes (key + 2 pointers on 64-bit)
- Cache line = 64 bytes → fits ~2.7 nodes
- For 1M records: ~20 random pointer chases

B-tree (order 100): each node has 99 keys, 100 pointers
- Node = 64 * page_size bytes → fills entire cache page
- All keys in a node loaded in ONE cache operation
- For 1M records: ~3 I/Os, all sequential within node
```

**Struct-of-Arrays vs Array-of-Structs:**

```java
// BAD: Array-of-Structs (AoS) - processes one field per object
// but loads entire struct per cache line (wastes bandwidth)
class Point { int x, y, z; } // 12 bytes each
Point[] points = new Point[1000];
// Computing sum of x only loads y,z too - wasted
int sumX = 0;
for (Point p : points) sumX += p.x; // each p.x may be cache miss

// GOOD: Struct-of-Arrays (SoA) - for SIMD/vectorized loops
// All x values are contiguous in memory
int[] xs = new int[1000]; // only x, packed tightly
int[] ys = new int[1000];
int sumX2 = 0;
for (int x : xs) sumX2 += x; // sequential, cache-perfect
// 10-100x faster for large arrays with SIMD CPU ops
```

---

### Comparison Table

| Structure | Cache Behavior | Use Case |
|-----------|---------------|---------|
| Array | Excellent (sequential) | Iteration, SIMD |
| ArrayList | Excellent | Dynamic arrays |
| LinkedList | Poor (pointer chase) | Only for O(1) insert/delete at known node |
| TreeMap (Red-Black) | Moderate (semi-random) | Sorted order needed |
| HashMap | Good for hot keys | Lookup-heavy |
| ArrayDeque | Excellent | Queue/stack (prefer over LinkedList) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Big-O complexity fully describes performance" | Cache effects make O(n) array traversal 100x faster than O(n) linked list traversal in practice |
| "LinkedList is better than ArrayList for frequent insertions" | Only true for O(1) insertion at a KNOWN node reference; finding the insertion point requires traversal which has terrible cache behavior |

---

### Failure Modes & Diagnosis

**Failure: Unexpectedly slow processing despite O(n) code**
- Symptoms: CPU perf counters show high cache miss rate
  (llc-misses in perf stat)
- Diagnosis: `perf stat -e cache-misses ./app`
- Common cause: Processing tree/graph nodes in DFS order
  (random memory order); or using Java objects with
  scattered heap allocation
- Fix: Use array-backed structures; consider object pooling;
  process data in memory order

---

### Quick Reference Card

| Rule | Cache impact |
|------|-------------|
| Arrays > Linked Lists | 10-100x for large traversals |
| SoA > AoS for field-specific iteration | 5-10x with SIMD |
| Preallocate collections | Avoids scattered allocation |
| Process in index order | Prefetcher works correctly |
| Avoid pointer-chasing loops | Each miss = 100ns penalty |

---

### The Surprising Truth

Java's LinkedList is almost never the right choice over
ArrayDeque for queue operations. LinkedList creates a new
Node object per element, scattering them across heap.
ArrayDeque uses a circular array - O(1) amortized for both
ends with excellent cache performance. Java's official
Deque documentation even says: "This class is likely to
be faster than Stack when used as a stack, and faster
than LinkedList when used as a queue." LinkedList exists
primarily for historical reasons and O(1) insertion at
a specific iterator position.

---

### Mastery Checklist

- [ ] Can explain why linked list traversal is slower than
      array traversal despite same O(n)
- [ ] Knows when SoA is preferable to AoS
- [ ] Prefers ArrayDeque over LinkedList for Java queues

---

### Interview Deep-Dive

**Q1 (Hard):** Why does Java's HashMap performance degrade
in latency-sensitive systems even at low load factor?

> HashMap stores entries as Node objects on the heap.
> Each get/put involves: compute hash (O(1), fast) then
> follow pointer to Node (potential cache miss if Node
> evicted from cache). Under high throughput with large
> key space, most Node accesses are cache misses (100ns
> each). At 1M ops/sec, even 10% cache miss rate =
> 100K * 100ns = 10ms wasted in cache misses per second.
> Solutions: (1) preallocate to reduce GC-induced
> re-layout; (2) use primitive maps (Eclipse Collections
> IntIntHashMap avoids boxing/pointer chase entirely);
> (3) partition the map to keep hot keys in L2 cache.
> Low-latency trading systems use custom hash maps
> with off-heap memory for this reason.
