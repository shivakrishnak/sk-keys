---
layout: default
title: "HashMap"
parent: "Data Structures & Algorithms"
nav_order: 35
permalink: /dsa/hashmap/
number: "035"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, LinkedList, Hash Function
used_by: HashSet, LinkedHashMap, ConcurrentHashMap, Memoisation, Frequency Counting
tags:
  - datastructure
  - algorithm
  - foundational
---

# 035 — HashMap

`#datastructure` `#algorithm` `#foundational`

⚡ TL;DR — A key-value store using a hash function to map keys to array buckets, providing O(1) average put/get/remove — the most used data structure after arrays.

| #035 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Array, LinkedList, Hash Function | |
| **Used by:** | HashSet, LinkedHashMap, ConcurrentHashMap, Memoisation, Frequency Counting | |

---

### 📘 Textbook Definition

A **HashMap** is a data structure implementing the Map abstract data type, providing O(1) average-case time complexity for `put(key, value)`, `get(key)`, `remove(key)`, and `containsKey(key)` operations via hash-based key distribution. Internally, a HashMap maintains an array of *buckets*; each bucket stores key-value pairs that hash to that index. Java 8+ `HashMap` uses *separate chaining* (linked list per bucket, converting to a red-black tree at 8+ entries per bucket) for collision resolution. Java's `HashMap` is not thread-safe; `ConcurrentHashMap` is the concurrent alternative.

### 🟢 Simple Definition (Easy)

A HashMap is like a filing cabinet where you label each folder with a key — you can instantly retrieve any value by its key without searching through everything.

### 🔵 Simple Definition (Elaborated)

A HashMap works by converting a key (like a String or Integer) into a number (its hash code), then using that number to pick an array slot (bucket) where the value is stored. When you ask for a key, the same conversion happens instantly and you jump directly to the right slot. This is why lookup is O(1) regardless of how many entries exist — you never iterate; you compute the location. The challenge is handling two keys that hash to the same slot (collision) — Java uses a linked list (or tree for many collisions) per bucket to store multiple entries at the same index.

### 🔩 First Principles Explanation

**Problem:** Given a large collection of key-value pairs, find the value for a given key in O(1) — not O(n) (linear search) or O(log n) (binary search on sorted array).

**Key insight:** If you could convert any key to an integer in range [0, N), and use that integer as a direct array index, you get O(1) lookup — because array `arr[index]` is O(1).

**Hash function:** `h(key)` → integer in [0, N). Property: equal keys must produce equal hash codes; unequal keys SHOULD produce different codes (collisions still possible due to pigeonhole principle).

**Java HashMap internals:**

```
HashMap internal layout (Java 8):
table: [ null ] [ → Entry ] [ null ] [ → Entry → Entry ] ...
          0          1          2          3

Entry { key, value, hash, next }

bucket index = (n - 1) & hash(key)  // n = power-of-2 table size
                                     // efficient modulo via bit-AND
```

**Resizing (rehashing):** When `size / capacity > loadFactor` (default 0.75), the table doubles. All entries are rehashed and moved to new buckets. O(n) operation, amortised O(1) across many puts.

**Java 8 → TreeNode conversion:** When a single bucket has ≥ 8 entries, the linked list is converted to a red-black tree, reducing worst-case per-bucket lookup from O(n) to O(log n). Converts back to list when below 6 entries.

**Collision resolution strategies:**

```
Separate Chaining (Java HashMap):
  Each bucket is a linked list (or tree)
  Multiple entries at same index → traversal within bucket
  Load factor controls avg chain length

Linear Probing (open addressing):
  On collision, try index+1, index+2, ...
  Better cache locality; problematic clustering
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT HashMap:

- Finding an element in an unsorted list: O(n) linear scan.
- Frequency counting: O(n) scan per element = O(n²) total.
- Caching computed results (memoisation): requires sorted array or O(n) scan.

What breaks without it:
1. Two-sum problem: O(n²) brute force vs O(n) with HashMap.
2. Word frequency count: O(n log n) with sorted array vs O(n) with HashMap.

WITH HashMap:
→ O(1) average insert and lookup enables O(n) solutions for problems previously O(n²).
→ Memoisation, caching, indexes — all foundational patterns require O(1) lookup.

### 🧠 Mental Model / Analogy

> A HashMap is like a library with open shelves where every book has a fixed shelf determined by the first letter of its title and its publication year (the hash function). You don't search every shelf — you compute the shelf directly and look there first. If two books map to the same shelf (collision), they sit side by side and you check the spine to find yours. The library has more shelves than books so most shelves have 0–1 books (low load factor = few collisions).

"Shelf number" = bucket index, "first letter + year" = hash function, "multiple books on same shelf" = collision, "more shelves than books" = low load factor.

### ⚙️ How It Works (Mechanism)

**put(key, value) algorithm:**

```
1. hash = Objects.hashCode(key)  // compute hash
2. hash = (h ^ (h >>> 16))       // spread bits (HashMap.hash())
3. bucket = hash & (n-1)         // n = table length (power of 2)
4. If bucket empty: create new Entry
5. If bucket has entries: traverse chain
   a. If key found: update value
   b. If key not found: append new Entry
6. If size > threshold: resize(2n)
```

**Iteration order:** HashMap does NOT preserve insertion order. Use `LinkedHashMap` for insertion-order iteration, `TreeMap` for sorted key order.

**hashCode + equals contract:** Objects used as HashMap keys MUST implement both:

```java
// If a.equals(b) then a.hashCode() == b.hashCode() (required)
// If a.hashCode() == b.hashCode() then a might equal b (not required)
```

### 🔄 How It Connects (Mini-Map)

```
Array (bucket array) + LinkedList/TreeNode (per bucket)
           ↓ implements
HashMap (key-value O(1) average) ← you are here
           ↓ variants
LinkedHashMap (insertion-ordered)
TreeMap (sorted by key)
ConcurrentHashMap (thread-safe)
HashSet (HashMap wrapper, keys only)
           ↓ used in
Memoisation | LRU Cache | Frequency Counting | Graph (adjacency)
```

### 💻 Code Example

Example 1 — Frequency counting (most common use case):

```java
String[] words = {"apple","banana","apple","cherry","banana","apple"};
Map<String, Integer> freq = new HashMap<>();

for (String word : words) {
    freq.merge(word, 1, Integer::sum);
    // equivalent: freq.put(word, freq.getOrDefault(word, 0) + 1);
}
System.out.println(freq);
// {apple=3, banana=2, cherry=1}

// Find word with max frequency
String maxWord = Collections.max(
    freq.entrySet(),
    Map.Entry.comparingByValue()
).getKey(); // "apple"
```

Example 2 — Two-Sum problem (HashMap for O(n) solution):

```java
// Find indices of two numbers that sum to target
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int complement = target - nums[i];
        if (seen.containsKey(complement)) {
            return new int[]{seen.get(complement), i};
        }
        seen.put(nums[i], i);
    }
    throw new IllegalArgumentException("No solution");
}
// Input: [2, 7, 11, 15], target=9 → [0, 1]
// O(n) time, O(n) space vs O(n²) brute force
```

Example 3 — Custom key with proper hashCode/equals:

```java
// BAD: Using mutable or non-equals/hashCode-correct key
Map<Point, String> map = new HashMap<>();
Point p = new Point(1, 2); // mutable; no override
map.put(p, "A");
p.x = 3; // mutate key → map is now corrupted!

// GOOD: Use immutable record as key (Java 16+)
record Point(int x, int y) {} // auto-generated hashCode/equals

Map<Point, String> map = new HashMap<>();
map.put(new Point(1, 2), "A");
System.out.println(map.get(new Point(1, 2))); // "A" ✓
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| HashMap always provides O(1) lookup | HashMap provides O(1) average case. With poor hash functions or adversarial input, all keys can collide to one bucket → O(n) worst case (or O(log n) with Java 8's tree conversion). |
| HashMap maintains insertion order | HashMap makes no ordering guarantee. LinkedHashMap preserves insertion order; TreeMap maintains sorted order. |
| null keys are forbidden in HashMap | HashMap allows exactly one null key (maps to bucket 0). ConcurrentHashMap forbids null keys entirely. |
| HashMap is thread-safe | HashMap is not thread-safe. Concurrent access without synchronisation can corrupt the internal structure. Use ConcurrentHashMap for concurrent scenarios. |
| hashCode being equal means keys are equal | Two unequal keys can have equal hash codes (hash collision). Equality is determined by equals() after hash codes match. |

### 🔥 Pitfalls in Production

**1. Using Mutable Objects as HashMap Keys**

```java
// BAD: key is mutated after insertion → entry lost
List<Integer> key = new ArrayList<>(Arrays.asList(1, 2, 3));
Map<List<Integer>, String> map = new HashMap<>();
map.put(key, "value");
key.add(4); // mutates key!

String val = map.get(key); // null! hash(key) changed
// Original entry unreachable — memory leak

// GOOD: Use immutable keys (String, Integer, records)
Map<List<Integer>, String> map = new HashMap<>();
map.put(List.of(1, 2, 3), "value"); // immutable List.of
```

**2. HashMap in Concurrent Environment**

```java
// BAD: HashMap shared across threads without synchronisation
Map<String, User> cache = new HashMap<>();
// Thread A writes; Thread B reads → data race → corrupted state
// Java 8 HashMap's resize bug can cause infinite loop in concurrent use!

// GOOD: ConcurrentHashMap for concurrent access
Map<String, User> cache = new ConcurrentHashMap<>();
// Or: Collections.synchronizedMap(new HashMap<>()) for full lock
```

**3. Default Initial Capacity Too Small for Known Large Maps**

```java
// BAD: HashMap starts at capacity 16
// Adding 10,000 entries triggers log₂(10000/0.75) ≈ 14 resizes
Map<String, Data> map = new HashMap<>(); // capacity 16

// GOOD: Pre-size to avoid resizing
int expectedSize = 10_000;
Map<String, Data> map = new HashMap<>(
    (int)(expectedSize / 0.75f) + 1
); // pre-size with load factor
```

### 🔗 Related Keywords

- `Hash Function` — the foundation of HashMap's O(1) lookup mechanism.
- `HashSet` — a HashMap with only keys (values are a dummy object).
- `LinkedHashMap` — HashMap with insertion-order iteration.
- `ConcurrentHashMap` — thread-safe HashMap with lock-striped implementation.
- `TreeMap` — sorted key Map using red-black tree; O(log n) operations.
- `Memoisation` — HashMap as a cache of computed function results.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ hash(key) → bucket index → O(1) avg put/ │
│              │ get/remove. Resizes at 75% load.          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Key-value lookup, frequency counting,     │
│              │ caching, two-sum pattern, grouping.       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sorted iteration → TreeMap;               │
│              │ concurrent access → ConcurrentHashMap;    │
│              │ immutable keys required (always use).     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HashMap: compute the address, don't      │
│              │ search for it."                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TreeMap → ConcurrentHashMap → LRU Cache   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `HashMap` uses `(capacity - 1) & hash(key)` to compute the bucket index, requiring capacity to always be a power of 2. A developer argues it would be more natural to use `hash(key) % capacity` with any capacity. Explain the mathematical equivalence between these two operations specifically for power-of-2 capacities, why the bitwise AND version is faster at the hardware level, and what value of N would the formula `(N-1) & hash` produce an incorrect uniformly distributed bucket index.

**Q2.** Consider a HashMap with 1 million entries and a custom key class whose `hashCode()` always returns the constant `42`. Describe the exact internal state of this HashMap (bucket distribution, tree vs list structure, time complexity of each get() call), and explain why Java 8's treeification at 8+ entries per bucket only partially mitigates this problem rather than fully restoring O(1) performance.

