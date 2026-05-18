---
id: DSA-044
title: Data Structures Selection Framework
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-008, DSA-010, DSA-012, DSA-013, DSA-014, DSA-016, DSA-027, DSA-028
used_by: DSA-050
related: DSA-014, DSA-027, DSA-043, DSA-050
tags:
  - data-structures
  - decision-framework
  - selection
  - trade-offs
  - java-collections
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/dsa/data-structures-selection-framework/
---

## TL;DR

Choosing the right data structure is the single most
impactful performance decision in a codebase - a decision
tree based on access pattern, ordering, uniqueness, and
throughput requirements.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-044 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, decision-framework, selection |
| **Prerequisites** | DSA-008, DSA-010, DSA-012, DSA-013, DSA-014, DSA-016, DSA-027, DSA-028 |

---

### The Problem This Solves

Using `ArrayList` for everything, or `HashMap` for everything,
are common mistakes. The wrong data structure turns O(log n)
into O(n) or O(1) into O(n) without any visible bug - just
invisible slowness that emerges at scale.

---

### The Decision Framework

**1. Do you need key-value lookup (map)?**
→ Unordered, fastest: `HashMap` (O(1))
→ Sorted keys needed: `TreeMap` (O(log n))
→ Insertion order needed: `LinkedHashMap` (O(1))

**2. Do you need unique elements (set)?**
→ Unordered, fastest: `HashSet` (O(1))
→ Sorted: `TreeSet` (O(log n))
→ Insertion order: `LinkedHashSet` (O(1))

**3. Do you need a sequence (list/queue)?**
→ Random access by index: `ArrayList` (O(1))
→ Frequent insert/delete at ends: `ArrayDeque` (O(1))
→ Stack (LIFO): `ArrayDeque` (not `Stack`)
→ Queue (FIFO): `ArrayDeque` or `LinkedList`
→ Priority access: `PriorityQueue` (O(log n))

**4. Do you need range queries on sorted data?**
→ `TreeMap.subMap(from, to)`, `TreeSet.subSet()`: O(log n)

**5. Do you need thread-safe access?**
→ `ConcurrentHashMap`, `CopyOnWriteArrayList`,
  `BlockingQueue` implementations

---

### Java Collections Cheat Sheet

| Need | Java Class | Time |
|------|-----------|------|
| Fast lookup by key | `HashMap` | O(1) avg |
| Sorted map | `TreeMap` | O(log n) |
| Insertion-order map | `LinkedHashMap` | O(1) avg |
| Fast membership test | `HashSet` | O(1) avg |
| Sorted unique set | `TreeSet` | O(log n) |
| Indexed list | `ArrayList` | O(1) read |
| Queue / Stack | `ArrayDeque` | O(1) |
| Priority queue | `PriorityQueue` | O(log n) |
| Thread-safe map | `ConcurrentHashMap` | O(1) avg |

---

### Common Anti-Patterns

```java
// BAD: ArrayList for membership test - O(n)
List<String> ids = new ArrayList<>(loadIds());
if (ids.contains(userId)) { ... }   // O(n) per check!

// GOOD: HashSet - O(1)
Set<String> idSet = new HashSet<>(loadIds());
if (idSet.contains(userId)) { ... }  // O(1)

// BAD: LinkedList for indexed access - O(n)
List<Item> items = new LinkedList<>();
items.get(5000);  // walks 5000 nodes

// GOOD: ArrayList - O(1)
List<Item> items = new ArrayList<>();
items.get(5000);  // direct array index

// BAD: HashMap iteration in sorted order
for (Map.Entry<K, V> e : map.entrySet()) {
    // HashMap iteration order is undefined!
}

// GOOD: TreeMap for sorted iteration
for (Map.Entry<K, V> e : new TreeMap<>(map).entrySet()) {
    // always ascending key order
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "LinkedList is always a good alternative to ArrayList" | LinkedList is rarely better; ArrayDeque beats it for queue/stack, ArrayList beats it for list |
| "HashMap is always O(1)" | Average O(1); worst case O(log n) per bucket (Java 8+); degrades with poor hashCode |

---

### Quick Reference Card

| Access Pattern | Best Choice |
|---------------|------------|
| Key → value (fast) | HashMap |
| Key → value (sorted) | TreeMap |
| Unique elements | HashSet |
| Unique + sorted | TreeSet |
| Index access | ArrayList |
| Stack or queue | ArrayDeque |
| Min/max repeatedly | PriorityQueue |

---

### Mastery Checklist

- [ ] Can choose the correct Java collection for any
      access pattern
- [ ] Knows why `ArrayDeque` beats `LinkedList` for
      queue/stack operations
- [ ] Can identify `List.contains()` in hot paths as an
      O(n) anti-pattern and replace with `HashSet`

---

### Interview Deep-Dive

**Q1 (Medium):** A cache needs O(1) get, O(1) put, and
must evict the Least Recently Used item when full.
What data structure?

> `LinkedHashMap` with access-order mode:
> `new LinkedHashMap<>(capacity, 0.75f, true)`. Override
> `removeEldestEntry()` to evict when size exceeds capacity.
> LinkedHashMap maintains a doubly-linked list in access
> order (most recently accessed is tail), giving O(1) for
> all operations. This is the canonical LRU cache in Java -
> used explicitly as such in Android's `LruCache` and
> many production caching implementations.
