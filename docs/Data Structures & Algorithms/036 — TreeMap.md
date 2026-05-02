---
layout: default
title: "TreeMap"
parent: "Data Structures & Algorithms"
nav_order: 36
permalink: /dsa/treemap/
number: "036"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: HashMap, Binary Search Tree, Red-Black Tree
used_by: Priority Queue, Range Queries, NavigableMap
tags:
  - datastructure
  - algorithm
  - intermediate
---

# 036 — TreeMap

`#datastructure` `#algorithm` `#intermediate`

⚡ TL;DR — A sorted key-value Map backed by a red-black tree providing O(log n) put/get/remove and O(log n) range operations like floorKey, ceilingKey, and subMap.

| #036 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HashMap, Binary Search Tree, Red-Black Tree | |
| **Used by:** | Priority Queue, Range Queries, NavigableMap | |

---

### 📘 Textbook Definition

`java.util.TreeMap<K, V>` is a `NavigableMap` implementation backed by a red-black tree that maintains keys in sorted order according to their natural ordering or a provided `Comparator`. All fundamental Map operations (`put`, `get`, `remove`, `containsKey`) execute in O(log n) time. `TreeMap` also supports navigational methods: `floorKey(k)` (largest key ≤ k), `ceilingKey(k)` (smallest key ≥ k), `headMap(toKey)` (sub-map up to toKey), `tailMap(fromKey)` (sub-map from fromKey), and `subMap(fromKey, toKey)` — all O(log n). Iteration over entries is in key-sorted order.

### 🟢 Simple Definition (Easy)

A TreeMap is like a HashMap but always keeps its keys sorted — so you can not only look up values by key, but also find the nearest key above or below a given value.

### 🔵 Simple Definition (Elaborated)

HashMap gives you O(1) key lookup but in random order. TreeMap gives you O(log n) key lookup — slower — but with a crucial extra capability: the keys are always sorted. This enables range queries: "give me all entries with keys between 100 and 200," "find the closest key to 150," or "give me the 10 keys just above 500." These queries are impossible or O(n) on a HashMap but O(log n) on a TreeMap. The classic use case: event scheduling (keys are timestamps), rate limiting by time ranges, and any problem needing "neighbours" of a given key.

### 🔩 First Principles Explanation

**Why a balanced BST (red-black tree)?**

A sorted array would give O(log n) search but O(n) insert/delete. A linked list gives O(n) all operations. A Binary Search Tree (BST) gives O(log n) average but O(n) worst case (degenerates to a list with sorted input). A *balanced* BST (red-black tree) guarantees O(log n) worst case for all operations by rebalancing after each insert/delete.

**Red-Black Tree properties:**
1. Every node is Red or Black.
2. Root is Black.
3. No two consecutive Red nodes (from root to leaf).
4. All paths from any node to null leaves have the same number of Black nodes.
These constraints guarantee a tree height of at most 2 × log₂(n+1) — O(log n).

**NavigableMap methods enabled by sorted order:**

```
TreeMap<Integer, String> map with keys: {1, 5, 10, 15, 20}

floorKey(12)   → 10  (largest key ≤ 12)
ceilingKey(12) → 15  (smallest key ≥ 12)
lowerKey(10)   → 5   (largest key < 10, strictly)
higherKey(10)  → 15  (smallest key > 10, strictly)
firstKey()     → 1
lastKey()       → 20
subMap(5, 15)  → {5, 10}   (5 inclusive, 15 exclusive)
headMap(10)    → {1, 5}    (keys < 10)
tailMap(10)    → {10, 15, 20} (keys ≥ 10)
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT TreeMap (using HashMap + sorting):

- Range queries require dumping all keys, sorting them, then filtering: O(n log n).
- Finding "nearest key" requires O(n) scan of all keys.
- Iterating keys in sorted order requires O(n log n) sort on every iteration.

What breaks without it:
1. Event scheduler needing "next event after time T" is O(n) with HashMap.
2. Sliding window problems needing sorted window contents are O(n log n) per step.

WITH TreeMap:
→ floorKey/ceilingKey in O(log n) on sorted tree.
→ Sorted iteration in O(n) without extra sort step.
→ subMap range views computed in O(log n) — backed by the same tree.

### 🧠 Mental Model / Analogy

> TreeMap is like a phone book (sorted alphabetically) vs. a card index box (HashMap, unsorted). In the phone book, finding the person with the name alphabetically closest to "Smith" is easy — just open to "Sm" and look at neighbours. In the card box, you'd have to search every card. The phone book's sorted order is O(log n) binary search for any name AND gives you "nearest neighbours" for free.

"Phone book" = TreeMap (sorted), "card index box" = HashMap (unsorted), "alphabetically closest" = floorKey/ceilingKey.

### ⚙️ How It Works (Mechanism)

**Tree structure:**

```
TreeMap with keys: {5, 10, 15, 20, 25, 30}
                  20 (Black)
                /         \
           10 (Red)       25 (Black)
           /     \           \
        5 (Black) 15 (Black) 30 (Red)

Red-Black invariants maintained after each insert via rotation + recoloring
Height ≤ 2 × log₂(7) ≈ 5.6 → all operations O(log n)
```

**Choosing TreeMap vs HashMap:**

```
Need                          Use
──────────────────────────────────────────────
O(1) key lookup               HashMap
Sorted key iteration          TreeMap
Range query (between A and B) TreeMap
Nearest key (floor/ceiling)   TreeMap
Insertion-order iteration     LinkedHashMap
```

### 🔄 How It Connects (Mini-Map)

```
HashMap (O(1) lookup, unordered)
        ↕ sorted-key alternative
TreeMap ← you are here (O(log n), sorted keys)
        ↓ backed by
Red-Black Tree (self-balancing BST)
        ↓ enables
NavigableMap interface (floor, ceiling, subMap)
        ↓ used in
Event scheduling | Range queries | SortedSets
```

### 💻 Code Example

Example 1 — Event scheduler with TreeMap:

```java
// Schedule events by timestamp; find next event
TreeMap<Long, String> events = new TreeMap<>();
events.put(1000L, "Login");
events.put(2000L, "Purchase");
events.put(3500L, "Logout");
events.put(5000L, "Session Expire");

long now = 2500L;

// O(log n): find next event after now
Map.Entry<Long, String> next = events.higherEntry(now);
System.out.println(next); // 3500=Logout

// O(log n): find last event at or before now
Map.Entry<Long, String> last = events.floorEntry(now);
System.out.println(last); // 2000=Purchase

// O(log n): all events in a time range
NavigableMap<Long, String> window =
    events.subMap(1000L, true, 4000L, true);
System.out.println(window); // {1000=Login, 2000=Purchase, 3500=Logout}
```

Example 2 — Count smaller numbers (LeetCode-style problem):

```java
// For each num, count how many previous numbers are smaller
// TreeMap<value, count> — ordered for floor queries
public int[] countSmaller(int[] nums) {
    TreeMap<Integer, Integer> freq = new TreeMap<>();
    int[] result = new int[nums.length];

    for (int i = nums.length - 1; i >= 0; i--) {
        // O(log n): sum of all values with key < nums[i]
        // headMap gives all keys < nums[i]
        result[i] = freq.headMap(nums[i]).values()
                        .stream().mapToInt(v -> v).sum();
        freq.merge(nums[i], 1, Integer::sum);
    }
    return result;
}
```

Example 3 — Rate limiter using TreeMap (sliding window):

```java
// Sliding window rate limiter: max N requests per windowMs
class RateLimiter {
    private final TreeMap<Long, Integer> requests
        = new TreeMap<>();
    private final int maxRequests;
    private final long windowMs;

    RateLimiter(int maxRequests, long windowMs) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
    }

    synchronized boolean allow(long timestamp) {
        // Remove requests outside the window
        long cutoff = timestamp - windowMs;
        requests.headMap(cutoff).clear(); // O(log n)

        int total = requests.values().stream()
                            .mapToInt(v -> v).sum();
        if (total >= maxRequests) return false;

        requests.merge(timestamp, 1, Integer::sum);
        return true;
    }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| TreeMap is always slower than HashMap | For operations that need ordering (range queries, floor/ceiling), TreeMap is the correct choice and is faster than applying sorting to a HashMap result. |
| TreeMap preserves insertion order | TreeMap sorts by key, not insertion order. LinkedHashMap preserves insertion order. These are different ordering strategies. |
| TreeMap works with any key type | TreeMap requires keys to implement Comparable or provide a Comparator. Using a non-comparable key without a Comparator throws ClassCastException at runtime. |
| floorKey() throws if no floor exists | floorKey() returns null if no key ≤ k exists. Always null-check the result. |
| TreeMap iterates faster than HashMap | TreeMap iterates in O(n) sorted order; HashMap iterates in O(n) random order. Speed is similar, but TreeMap guarantees sorted output. |

### 🔥 Pitfalls in Production

**1. Key Not Implementing Comparable**

```java
// BAD: Custom class as key without Comparable
class Event { String name; }
TreeMap<Event, Integer> map = new TreeMap<>();
map.put(new Event("A"), 1); // ClassCastException at runtime!

// GOOD: Implement Comparable or provide Comparator
TreeMap<Event, Integer> map = new TreeMap<>(
    Comparator.comparing(e -> e.name));
```

**2. Mutable Keys Corrupting Sort Order**

```java
// BAD: Key object mutated after insertion
TreeMap<StringBuilder, Integer> map = new TreeMap<>(
    Comparator.comparing(Object::toString));
StringBuilder key = new StringBuilder("abc");
map.put(key, 1);
key.append("xyz"); // sort order changes → map corrupted!
map.get(key); // null — can't find it!

// GOOD: Use immutable keys
TreeMap<String, Integer> map = new TreeMap<>();
```

**3. Ignoring null Returns from Floor/Ceiling**

```java
TreeMap<Integer, String> map = new TreeMap<>();
map.put(10, "A"); map.put(20, "B");

Integer floor = map.floorKey(5); // null — no key ≤ 5!
System.out.println(floor.toString()); // NullPointerException!

// GOOD: null-check first
Integer floor = map.floorKey(5);
if (floor != null) { System.out.println(map.get(floor)); }
```

### 🔗 Related Keywords

- `HashMap` — O(1) unordered alternative; use when ordering not needed.
- `LinkedHashMap` — insertion-order-preserving HashMap variant.
- `Red-Black Tree` — the self-balancing BST backing TreeMap.
- `NavigableMap` — the interface exposing TreeMap's floor/ceiling/subMap operations.
- `Priority Queue` — also maintains ordering but only exposes min/max, not full sorted access.
- `Binary Search Tree` — the unbalanced predecessor that TreeMap improves upon.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Sorted Map backed by red-black tree:      │
│              │ O(log n) all ops + floor/ceiling/subMap.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sorted key iteration; range queries;      │
│              │ nearest-key lookups; event scheduling.    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only need key-value lookup → HashMap      │
│              │ (5-10× faster for pure get/put).          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "TreeMap: HashMap + sorted order + range  │
│              │ queries, at O(log n) cost."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Heap → Priority Queue → Red-Black Tree    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A stock trading system stores last-trade prices for 10,000 securities in a `TreeMap<String, Double>` keyed by security symbol. A query asks: "for all securities with symbols between 'AAAA' and 'MZZZ', find the one with the highest price." Describe the time complexity of solving this with `subMap("AAAA", "MZZZ")` followed by a max scan, compared with doing the same on a `HashMap<String, Double>`. Then identify a data structure combination that would answer this query in O(log n) rather than O(k) where k is the number of matching securities.

**Q2.** `TreeMap.entrySet().iterator()` returns entries in sorted key order in O(n) total. Internally, a red-black tree's in-order traversal visits all nodes in sorted order. Describe the iterative in-order traversal algorithm for a BST using an explicit stack, explain why this achieves O(1) amortised time per `next()` call, and contrast with the naive approach of collecting all nodes then iterating the list.

