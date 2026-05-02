---
layout: default
title: "TreeMap"
parent: "Data Structures & Algorithms"
nav_order: 36
permalink: /dsa/treemap/
number: "0036"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: HashMap, Binary Search
used_by: Segment Tree, Consistent Hash Ring
related: HashMap, LinkedHashMap, TreeSet
tags:
  - datastructure
  - intermediate
  - algorithm
  - performance
---

# 036 — TreeMap

⚡ TL;DR — A TreeMap stores key-value pairs in sorted key order using a balanced BST, giving O(log N) access but enabling range queries that HashMap cannot support.

| #036 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HashMap, Binary Search | |
| **Used by:** | Segment Tree, Consistent Hash Ring | |
| **Related:** | HashMap, LinkedHashMap, TreeSet | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You are building a leaderboard where you need to find all players with scores between 1,000 and 5,000. You store scores in a `HashMap`. To answer the range query, you iterate every entry and check if the score falls in range — O(N) for every single query. With 10 million players and 10,000 range queries per second, that is 100 billion operations per second — impossible.

THE BREAKING POINT:
HashMap sacrifices key ordering for O(1) speed. Once ordering is gone, range queries require full scans. Any system that needs "all keys between X and Y", "the nearest key to X", or "sorted iteration" is broken by HashMap's unordered design.

THE INVENTION MOMENT:
Store keys in a balanced binary search tree. Every node's left subtree has smaller keys, right subtree has larger. Finding all keys in range [lo, hi] is a single guided traversal — O(log N + K) where K is the number of results. This is exactly why the TreeMap was created.

### 📘 Textbook Definition

A **TreeMap** is a `NavigableMap` implementation backed by a red-black tree. Keys are stored in sorted order according to their natural ordering or a `Comparator` provided at construction. `get`, `put`, and `remove` operations are O(log N). Additionally, it provides O(log N) range operations: `subMap(lo, hi)`, `headMap(hi)`, `tailMap(lo)`, `floorKey(k)`, `ceilingKey(k)`, `lowerKey(k)`, and `higherKey(k)`.

### ⏱️ Understand It in 30 Seconds

**One line:**
A key-value map that keeps its keys sorted, enabling range queries that a HashMap cannot do.

**One analogy:**
> A dictionary organises words alphabetically on the page. You can instantly flip to the 'M' section and find all words between "mango" and "mute" — because the sorted order makes range navigation trivial.

**One insight:**
TreeMap makes you pay O(log N) per operation instead of O(1) — but in return, it gives you something HashMap fundamentally cannot provide: the ability to ask "what is the next key after X?" or "give me all keys from A to B?" without scanning everything.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. All keys in the left subtree of any node are less than the node's key.
2. All keys in the right subtree are greater.
3. The tree is *balanced* — height is O(log N) — so no single branch grows to O(N).

DERIVED DESIGN:
Java's `TreeMap` uses a **red-black tree** — a self-balancing BST. Every insertion and deletion may trigger rotations to maintain balance. A red-black tree guarantees height ≤ 2 × log₂(N), bounding all operations at O(log N).

Range query `subMap(lo, hi)` works by:
1. Finding `lo` via BST traversal: O(log N).
2. Iterating in-order from `lo` until `hi` is exceeded: O(K) for K results.
3. Total: O(log N + K) — far better than O(N) for sparse ranges.

Can we use a sorted array instead? Lookup would be O(log N) via binary search, but insertion would be O(N) due to shifting. Red-black trees achieve O(log N) for both.

THE TRADE-OFFS:
Gain: Sorted order, O(log N) range queries, nearest-key operations.
Cost: O(log N) vs O(1) for basic get/put, higher constant factor, more memory per node.

### 🧪 Thought Experiment

SETUP:
A stock trading system must find the best available ask price ≥ the buyer's limit price. 10,000 active orders, 1,000 queries per second.

WHAT HAPPENS WITH HASHMAP:
Each query scans all 10,000 orders to find the minimum ask ≥ limit. 1,000 queries × 10,000 orders = 10 million comparisons per second.

WHAT HAPPENS WITH TREEMAP:
Orders stored by price as keys. Each query calls `ceilingKey(limitPrice)` — finds the lowest key ≥ limit in O(log 10000) = O(13) operations. 1,000 queries × 13 = 13,000 operations per second. An improvement of ~770×.

THE INSIGHT:
The "sorted order" that TreeMap maintains is not just cosmetic — it is a structural property that enables sub-linear range queries. HashMap cannot do this at any cost because it has structurally thrown away ordering information.

### 🧠 Mental Model / Analogy

> A TreeMap is like a sorted filing cabinet where files are alphabetically ordered. Finding files between "Mango" and "Mute" means opening the 'M' drawer and pulling all consecutive files — no searching other drawers.

"Alphabetical drawer order" → BST key ordering
"Pull consecutive files" → in-order traversal
"Finding the right drawer section" → BST navigation `floorKey/ceilingKey`
"Adding a new file in order" → rebalanced tree insertion

Where this analogy breaks down: Filing cabinets don't self-balance. TreeMap automatically restructures itself on each insert to maintain O(log N) height — you never do this in a physical filing cabinet.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A map where keys are always kept in sorted order. You can find not just a specific key, but also the nearest key, or all keys within a range.

**Level 2 — How to use it (junior developer):**
`NavigableMap<Integer, String> map = new TreeMap<>()`. Use `put/get/remove` as with HashMap. Use `floorKey(k)` (≤k), `ceilingKey(k)` (≥k), `subMap(lo, hi)` (range). Provide a `Comparator` at construction to sort in custom order. Never use with keys that don't implement `Comparable` without a `Comparator` — will throw `ClassCastException`.

**Level 3 — How it works (mid-level engineer):**
Backed by a `TreeMap.Entry` red-black tree. Each entry: key, value, left, right, parent, color (boolean). `put(k,v)`: BST insert by comparing key; after insertion, call `fixAfterInsertion()` which rebalances via left/right rotations and color changes. `floorKey(k)`: navigate BST to find the largest key ≤ k. `subMap(lo, hi)` returns a view (not a copy) backed by the original tree, lazily checking bounds during iteration.

**Level 4 — Why it was designed this way (senior/staff):**
Red-black trees were chosen over AVL trees because they require fewer rotations on insertion/deletion (at most 3 rotations vs up to O(log N) for AVL). The cost is slightly taller trees (≤ 2 log N vs log N for AVL), but the constant factor on mutations is better. `TreeMap.subMap()` returns a view rather than a copy — O(1) view creation, lazy traversal. This is an important API design decision: if it copied, a range query on 1 element of a 10M map would allocate 10M entries. The view approach makes chained range queries efficient.

### ⚙️ How It Works (Mechanism)

**Red-black tree properties:**
```
1. Every node is red or black
2. Root is black
3. Red nodes have only black children
4. Every path from root to null has same black-node count
```
These invariants bound height to 2 × log₂(N).

**put(5, "five") in tree with {3, 7, 10}:**
```
Step 1: BST insert at correct position
  3(B)
    \
     7(B) ← 5 goes here as left child (5 < 7)
    / \
   5(R)  10(B)

Step 2: fixAfterInsertion() — check parent is black
  Parent 7 is black → no violation → done
```

┌──────────────────────────────────────────────┐
│  TreeMap floorKey(6) traversal               │
│                                              │
│    7(B)     ← 6 < 7, go left; 7 is candidate│
│   /   \                                      │
│  3(B)  10(B)← 6 > 3, go right; 3 candidate  │
│   \                                          │
│    5(R)  ← 6 > 5, go right; 5 is candidate  │
│       (null) ← return 5 as floor            │
└──────────────────────────────────────────────┘

**subMap(3, 7) — returns a view:**
```java
// Returns a live view — not a copy
SortedMap<K,V> sub = map.subMap(3, true, 7, false);
// Iterating sub traverses in-order from key=3 to key<7
// Any put(8, x) on sub throws IllegalArgumentException
// Any put(4, x) on sub reflects immediately in original map
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Key provided for put/get
→ hashCode not used; compareTo() traverses tree
→ BST navigation O(log N) [TREEMAP ← YOU ARE HERE]
→ Rebalance if needed (insert/delete)
→ Range query returns live view
```

FAILURE PATH:
```
Custom key class without Comparable and no Comparator
→ ClassCastException at first put()
→ Missing: implement Comparable or pass Comparator
```

WHAT CHANGES AT SCALE:
At 10M+ entries, TreeMap works correctly but has higher memory footprint (~64 bytes per entry with object headers and 5 pointers). Cache miss rate increases for random key lookups because red-black tree nodes are scattered in memory. At extreme scale, a B-tree (like those in databases) provides better cache efficiency because child nodes fill entire cache lines together. Java's TreeMap has no concurrency support; use `ConcurrentSkipListMap` for thread-safe sorted access at scale.

### 💻 Code Example

**Example 1 — Range query (stock order book):**
```java
TreeMap<Integer, List<Order>> asks = new TreeMap<>();
// Add orders: key=price, value=list of orders at price
asks.put(100, List.of(order1));
asks.put(105, List.of(order2));
asks.put(110, List.of(order3));

// Find best ask >= buyer's limit of 103
Integer bestAsk = asks.ceilingKey(103); // returns 105
```

**Example 2 — Consistent hashing ring basics:**
```java
// Servers on a hash ring; find which server owns a key
TreeMap<Integer, String> ring = new TreeMap<>();
ring.put(hash("server-A"), "server-A");
ring.put(hash("server-B"), "server-B");
ring.put(hash("server-C"), "server-C");

int keyHash = hash("user-123");
// Find first server clockwise from keyHash
Map.Entry<Integer, String> entry =
    ring.ceilingEntry(keyHash);
if (entry == null)
    entry = ring.firstEntry(); // wrap around
System.out.println("Routes to: " + entry.getValue());
```

**Example 3 — subMap for date range queries:**
```java
TreeMap<LocalDate, List<Event>> calendar = new TreeMap<>();
// ... populate calendar

// All events in March 2025
LocalDate start = LocalDate.of(2025, 3, 1);
LocalDate end   = LocalDate.of(2025, 4, 1);
SortedMap<LocalDate, List<Event>> march =
    calendar.subMap(start, true, end, false);
// march is a live view — O(log N) creation, O(K) iteration
```

### ⚖️ Comparison Table

| Map | Ordering | get/put | Range Query | Thread-safe | Best For |
|---|---|---|---|---|---|
| **TreeMap** | Sorted | O(log N) | O(log N+K) | ✗ | Range queries, sorted keys |
| HashMap | None | O(1) avg | O(N) | ✗ | General lookup |
| LinkedHashMap | Insertion/LRU | O(1) avg | O(N) | ✗ | Ordered iteration |
| ConcurrentSkipListMap | Sorted | O(log N) | O(log N+K) | ✓ | Concurrent sorted access |
| EnumMap | Enum order | O(1) | O(K) | ✗ | Enum keys |

How to choose: Use TreeMap when you need sorted keys or range queries. Use HashMap for maximum throughput with no ordering requirement. Use `ConcurrentSkipListMap` when you need thread-safe sorted access.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| TreeMap is just a slower HashMap | TreeMap provides capabilities (range queries, floor/ceiling) that HashMap fundamentally cannot provide |
| subMap() copies the entries | `subMap()` returns a live view backed by the original tree; no copying occurs |
| TreeMap works with any object as key | Keys must implement `Comparable` or a `Comparator` must be provided; otherwise `ClassCastException` |
| TreeMap is thread-safe like ConcurrentHashMap | `TreeMap` has no synchronization; use `Collections.synchronizedSortedMap()` or `ConcurrentSkipListMap` |
| Iteration order of TreeMap equals insertion order | TreeMap iterates in key-sorted order, not insertion order |

### 🚨 Failure Modes & Diagnosis

**1. ClassCastException with non-Comparable key**

Symptom: `java.lang.ClassCastException: MyClass cannot be cast to java.lang.Comparable` on first `put()`.

Root Cause: TreeMap requires keys to be comparable. Custom class without `Comparable` and no `Comparator` at construction.

Diagnostic:
```bash
# Stack trace will point to TreeMap.compare() method
# Check your key class definition
```

Fix:
```java
// BAD: No ordering defined
TreeMap<MyClass, String> map = new TreeMap<>();

// GOOD: Provide Comparator
TreeMap<MyClass, String> map =
    new TreeMap<>(Comparator.comparing(MyClass::getId));
```

Prevention: Always define ordering explicitly for custom key types.

---

**2. Mutation of keys after insertion breaks tree invariant**

Symptom: `get(key)` returns null even though the key was previously put; iteration skips entries.

Root Cause: Key's `compareTo()` result changed after insertion (e.g., mutable field used in comparison). Tree was built on the original value; now traversal takes wrong path.

Diagnostic:
```bash
# Print all entries via tree traversal vs direct iterate:
map.forEach((k, v) -> System.out.println(k + "=" + v));
```

Fix: Use only immutable objects as TreeMap keys.

Prevention: Make key classes immutable; document the invariant.

---

**3. Performance regression vs HashMap**

Symptom: Service using TreeMap is 5–10× slower than expected; profiler shows time in tree rotations.

Root Cause: Using TreeMap where no range queries are needed — paying O(log N) for every operation unnecessarily.

Diagnostic:
```bash
./profiler.sh -e cpu -d 30 <pid>
# Time concentrated in TreeMap.put() and TreeMap.fixAfterInsertion()
```

Fix: Replace TreeMap with HashMap if sorted iteration is not required.

Prevention: Choose TreeMap only when range queries or sorted iteration are a stated requirement.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HashMap` — understanding O(1) hash-based access highlights why TreeMap trades speed for ordering.
- `Binary Search` — BST navigation is binary search applied to a tree structure.

**Builds On This (learn these next):**
- `Segment Tree` — builds range operations on top of a sorted structure.
- `Consistent Hash Ring` — typically implemented with `TreeMap.ceilingKey()` to find the next node on the ring.

**Alternatives / Comparisons:**
- `HashMap` — O(1) access but no ordering; prefer when range queries are not needed.
- `ConcurrentSkipListMap` — thread-safe sorted map; O(log N) reads with better concurrent throughput than synchronised TreeMap.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Sorted key-value map backed by red-black  │
│              │ tree; O(log N) access + range queries     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ HashMap cannot answer "all keys between   │
│ SOLVES       │ X and Y" without scanning everything      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Sorted structure enables O(log N) range   │
│              │ queries; HashMap structurally cannot      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Range queries, floor/ceiling lookups,     │
│              │ sorted iteration, consistent hashing ring │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple key lookup with no ordering need   │
│              │ (use HashMap, 5-10× faster)               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(log N) range power vs O(1) HashMap speed│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A sorted dictionary vs a heap of files   │
│              │  — one finds ranges, one finds keys"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HashMap → Consistent Hash Ring → Skip List│
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** A ride-sharing service needs to find the nearest available driver to a customer, where "nearest" is determined by a 1D distance metric on a mapped road segment. You have 50,000 drivers updated 5 times per second each. Design a solution using `TreeMap` and evaluate its time complexity for both driver-position updates and nearest-driver queries. What happens when two drivers have identical position keys, and how does that affect your design?

**Q2.** Java's `TreeMap.subMap(lo, hi)` returns a live view, not a copy. This means iterating the sub-map while another thread modifies the backing TreeMap is not safe. If you need a thread-safe sorted map with range queries, you have `ConcurrentSkipListMap` as an option. What is the fundamental structural reason that a skip list is more amenable to concurrent access than a red-black tree, even though both provide O(log N) operations?

