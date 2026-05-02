---
layout: default
title: "HashMap"
parent: "Data Structures & Algorithms"
nav_order: 35
permalink: /dsa/hashmap/
number: "0035"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Array, Hashing Techniques
used_by: LRU Cache, Consistent Hash Ring, Graph, Memoization
related: TreeMap, HashSet, LinkedHashMap
tags:
  - datastructure
  - foundational
  - algorithm
  - performance
---

# 035 — HashMap

⚡ TL;DR — A HashMap maps keys to values in O(1) average time by using a hash function to find the storage bucket directly.

| #035 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Array, Hashing Techniques | |
| **Used by:** | LRU Cache, Consistent Hash Ring, Graph, Memoization | |
| **Related:** | TreeMap, HashSet, LinkedHashMap | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You are building a word-frequency counter for a 10GB log file. Each time you see a word, you need to increment its count. Using an array, you must search through all existing words to find the matching entry — O(N) per word. With 1 million unique words and 10 billion total occurrences, that is 10 trillion operations. The program would run for days.

THE BREAKING POINT:
Sequential search is O(N). Every key lookup in an unsorted list walks all entries until a match. As the collection grows, every operation slows proportionally. This is unusable for any real-world dictionary, cache, or index.

THE INVENTION MOMENT:
If we could convert a key directly into an index — without searching at all — lookup becomes O(1). A hash function converts any key to an integer; `integer % array_size` becomes the bucket index. This is exactly why the HashMap was created.

### 📘 Textbook Definition

A **HashMap** is a data structure that implements an associative array (a map from keys to values). It uses a hash function to compute an integer bucket index from each key, enabling average O(1) `get`, `put`, and `remove` operations. Collisions (two keys mapping to the same bucket) are resolved by chaining (linked list or tree per bucket) or open addressing. Worst-case performance degrades to O(N) if all keys collide into one bucket.

### ⏱️ Understand It in 30 Seconds

**One line:**
A table that converts any key into a direct address so lookup never requires searching.

**One analogy:**
> Think of a post office with 100 numbered mailboxes. When a letter arrives for "Alice", a clerk calculates which mailbox is hers (by some formula from her name). To retrieve Alice's mail, you go directly to that box — no searching every box in order.

**One insight:**
A HashMap's O(1) average access is not magic — it is O(1) array access in disguise. The hash function converts the key into an array index, and everything else follows from the O(1) property of arrays.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A hash function must be deterministic: the same key always produces the same hash.
2. The array (buckets) is the backing store; all speed derives from O(1) array access.
3. Collision handling is required: two distinct keys can produce the same bucket index.

DERIVED DESIGN:
The full pipeline: `key → hashCode() → spread/compress → bucket index → chain/probe`.

Java's `HashMap` computes `(key.hashCode() ^ (key.hashCode() >>> 16))` first — this "spreads" high bits into low bits to prevent clustering when the capacity is a power of 2. Bucket index = `hash & (capacity - 1)`.

Each bucket is a linked list. After Java 8, once a bucket chain exceeds 8 entries and total capacity ≥ 64, the chain is converted to a red-black tree — O(log N) worst-case instead of O(N). This prevents hash-flooding attacks from degrading performance to O(N).

**Load factor** determines when the map resizes. Default is 0.75: when 75% of buckets are occupied, capacity doubles and all entries are rehashed. Keeping load factor low reduces collisions; raising it saves memory but increases collision rate.

THE TRADE-OFFS:
Gain: O(1) average get/put/remove, flexible key types.
Cost: No ordering, O(N) worst-case on hash collisions, rehashing pauses, extra memory per entry.

### 🧪 Thought Experiment

SETUP:
Count word frequencies in a document with 100,000 words.

WHAT HAPPENS WITHOUT HASHMAP (using a sorted array):
Each word lookup binary-searches the sorted array: O(log N). Each insertion into the sorted position: O(N) shift. For 100,000 words: ~100,000 × O(N) insertions = ~5 billion operations.

WHAT HAPPENS WITH HASHMAP:
Each word is hashed directly to a bucket. `put("hello", count+1)` is two array accesses (hash → bucket index → entry). 100,000 operations: each O(1) → total O(N).

THE INSIGHT:
HashMap transforms an O(N) search problem into an O(1) address problem. The hash function is not about finding the needle in the haystack — it converts the needle into a GPS coordinate that takes you directly to the exact position.

### 🧠 Mental Model / Analogy

> A HashMap is like a filing cabinet where each drawer is labelled by the first letter of the surname. To file Alice's record, you go straight to drawer 'A'. To retrieve it, you go straight to 'A' and look only in that drawer. The filing rule (first letter) is the hash function.

"Filing rule (first letter)" → hash function
"Drawer" → bucket (array slot)
"Files in one drawer" → entries in one bucket chain
"Two people with same first letter" → hash collision

Where this analogy breaks down: Real filing cabinets use alphabetical order within a drawer (still O(N) scan). A HashMap's bucket chain is unordered; only Java 8's tree-ification gives O(log N) within an over-full bucket.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A key-value storage where each key maps to exactly one value, and you can get or set any value in an instant.

**Level 2 — How to use it (junior developer):**
`Map<String, Integer> map = new HashMap<>()`. Use `put(key, val)`, `get(key)`, `getOrDefault(key, 0)`, `containsKey(key)`, `remove(key)`. Override `equals()` and `hashCode()` in custom key classes — if two equal objects have different `hashCode`, the map will lose entries. Iterate with `for (Map.Entry<K,V> e : map.entrySet())`.

**Level 3 — How it works (mid-level engineer):**
Java `HashMap<K,V>`: backing array `Node<K,V>[] table`. Default initial capacity: 16. Bucket index: `(n-1) & hash` where n = table.length (power of 2). Each bucket is a singly linked list of `Node` objects; after 8 nodes in one bucket and table size ≥ 64, converts to `TreeNode` (red-black tree). `resize()` doubles the table and rehashes all entries — O(N) but amortized O(1) per put.

**Level 4 — Why it was designed this way (senior/staff):**
The capacity must be a power of 2 to avoid modulo division (use bitwise AND instead). The secondary hash `h ^ (h >>> 16)` prevents poor distributions from hash functions that cluster in low bits — common in hash codes from `Object.hashCode()` (typically derived from memory address). The tree-ification threshold of 8 balances memory (TreeNode is 2× the size of Node) against worst-case attack resistance. Pre-Java 8, hash-flooding attacks (adversarially chosen keys all colliding) could degrade a HashMap to O(N) per operation, effectively DoSing any service that stored attacker-controlled keys.

### ⚙️ How It Works (Mechanism)

**put("hello", 1) walkthrough:**
```
1. hashCode("hello") = 99162322
2. spread: 99162322 ^ (99162322 >>> 16)
         = 99162322 ^ 1513      = 99163835
3. bucket = 99163835 & (16-1) = 99163835 & 15 = 11
4. table[11] is null → create Node("hello", 1, null)
5. table[11] = new node; size++
```

**get("hello") walkthrough:**
```
1. Same hash → same bucket index 11
2. table[11] != null → check: node.key.equals("hello") → true
3. Return node.value = 1
```

**Collision handling:**
```
If table[11] already has a node with different key:
  → Append new node to chain (linked list)
  → get() scans chain with equals() check
```

┌──────────────────────────────────────────────┐
│  HashMap Internal Layout (capacity=8)        │
│                                              │
│  table[0]: null                              │
│  table[1]: ["cat",3] → null                 │
│  table[2]: null                              │
│  table[3]: ["dog",5] → ["log",2] → null     │
│            (collision: same bucket)          │
│  ...                                         │
│  table[7]: ["hi",1] → null                  │
└──────────────────────────────────────────────┘

**Resize trigger:**
When `size > capacity * loadFactor` (default: 16 × 0.75 = 12 entries):
```
newCapacity = capacity * 2 = 32
Rehash all entries: bucket = hash & 31
All entries redistributed — O(N) operation
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Key provided
→ hashCode() computed
→ Spread/mixing applied
→ Bucket index calculated [HASHMAP ← YOU ARE HERE]
→ Bucket chain/tree searched with equals()
→ Value returned or stored
```

FAILURE PATH:
```
All keys hash to same bucket (collision attack)
→ Chain grows to N entries
→ get() scans entire chain: O(N)
→ Pre-Java8: service DoS; Java8+: degrades to O(log N)
```

WHAT CHANGES AT SCALE:
At millions of entries, rehash events (capacity doublings) cause GC pressure and latency spikes. Pre-size the map: `new HashMap<>(expectedSize * 2)`. At 10M+ entries in a single HashMap, consider `ConcurrentHashMap` for read-heavy concurrent access, or segment the map across multiple partitions to reduce lock contention.

### 💻 Code Example

**Example 1 — Word frequency count:**
```java
Map<String, Integer> freq = new HashMap<>();
String[] words = text.split("\\s+");
for (String w : words) {
    freq.merge(w, 1, Integer::sum); // O(1) per word
}
```

**Example 2 — Critical: custom key must override hashCode + equals:**
```java
// BAD: uses Object.hashCode() — different instances
//      with same value map to different buckets
class Point { int x, y; }
Map<Point, String> map = new HashMap<>();
map.put(new Point(1, 2), "origin");
map.get(new Point(1, 2)); // returns null!

// GOOD: override equals and hashCode
class Point {
    int x, y;
    @Override public boolean equals(Object o) {
        if (!(o instanceof Point)) return false;
        Point p = (Point) o;
        return x == p.x && y == p.y;
    }
    @Override public int hashCode() {
        return Objects.hash(x, y);
    }
}
map.get(new Point(1, 2)); // returns "origin"
```

**Example 3 — Pre-size to avoid rehash pauses:**
```java
// BAD: triggers multiple rehash events for large input
Map<String, Long> cache = new HashMap<>();
for (int i = 0; i < 1_000_000; i++)
    cache.put("key" + i, (long) i);

// GOOD: pre-size to avoid rehashing
// Formula: (expected / loadFactor) + 1
int initialCapacity = (int)(1_000_000 / 0.75) + 1;
Map<String, Long> cache = new HashMap<>(initialCapacity);
```

### ⚖️ Comparison Table

| Map | Ordering | Get/Put | Memory | Best For |
|---|---|---|---|---|
| **HashMap** | None | O(1) avg | Medium | General key-value lookup |
| LinkedHashMap | Insertion/Access | O(1) avg | Higher | LRU cache, ordered iteration |
| TreeMap | Sorted by key | O(log N) | Higher | Range queries, sorted keys |
| ConcurrentHashMap | None | O(1) avg | Higher | Thread-safe concurrent access |
| EnumMap | Enum order | O(1) | Low | Enum keys only |

How to choose: Use `HashMap` for general-purpose key-value. Use `LinkedHashMap` for LRU or insertion-ordered iteration. Use `TreeMap` when you need keys in sorted order or range queries like `subMap()`.

### 🔁 Flow / Lifecycle

```
Creation → table = new Node[16]; loadFactor=0.75
  ↓
put() → hash → bucket → store node; size++
  ↓
size > threshold (capacity*0.75)?
  → resize: newTable = 2x; rehash all → O(N)
  ↓
get() → hash → bucket → equals scan → return value
  ↓
remove() → hash → bucket → unlink node; size--
  ↓
GC reclaims Node objects after removal
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| HashMap.get() is always O(1) | Worst-case is O(N) (all keys in one bucket); Java 8 caps it at O(log N) via tree-ification |
| HashMap is thread-safe | `HashMap` has no synchronization; use `ConcurrentHashMap` for concurrent access |
| HashMap iterates in insertion order | Iteration order is undefined; use `LinkedHashMap` for insertion order |
| Overriding `equals()` is enough for custom keys | Must override both `equals()` AND `hashCode()`; equal objects must have equal hash codes |
| HashMap wastes memory | Each entry is one Node object (~32 bytes); for primitive keys, use specialized maps (Trove, Eclipse Collections) |

### 🚨 Failure Modes & Diagnosis

**1. Silent data loss from missing hashCode override**

Symptom: `map.get(key)` returns null even though you just `put` an equal key object.

Root Cause: Custom class overrides `equals()` but not `hashCode()`. Two equal objects get different bucket indices → `get` never finds the entry.

Diagnostic:
```bash
# Add temporary logging:
System.out.println(key.hashCode()); // before put and get
# If different for equal keys: hashCode not overridden
```

Fix: Always override `hashCode()` when overriding `equals()`. Use `Objects.hash(fields...)`.

Prevention: Use IDE "generate equals and hashCode" together; use static analysis (SpotBugs, SonarQube `HE_EQUALS_NO_HASHCODE` rule).

---

**2. ConcurrentModificationException during iteration**

Symptom: `java.util.ConcurrentModificationException` during `for (Map.Entry e : map.entrySet())`.

Root Cause: Map modified (put/remove) during iteration increments `modCount`; iterator detects mismatch.

Diagnostic:
```bash
grep -n "put\|remove" MyClass.java
# Find modification inside the loop
```

Fix:
```java
// BAD
for (Map.Entry<K,V> e : map.entrySet())
    if (predicate(e)) map.remove(e.getKey());

// GOOD
map.entrySet().removeIf(e -> predicate(e));
// or use iterator
Iterator<Map.Entry<K,V>> it = map.entrySet().iterator();
while (it.hasNext()) {
    if (predicate(it.next())) it.remove();
}
```

Prevention: Never modify a `HashMap` while iterating it with an enhanced for loop.

---

**3. HashMap performance degradation under hash flooding**

Symptom: HashMap operations slow from O(1) to O(N); service response times spike under adversarial input.

Root Cause: Attacker sends keys that all hash to the same bucket. Pre-Java 8: O(N) chain scan. Java 8+: O(log N) tree but still degraded.

Diagnostic:
```bash
# Profile with async-profiler; look for time in HashMap.get:
./profiler.sh -e cpu -d 30 -f out.html <pid>
```

Fix: Use `String.hashCode()` (Java randomises it from Java 9 via Compact Strings, mitigating flooding); or switch keys to types with well-distributed hashes.

Prevention: Never use attacker-controlled strings as HashMap keys without input validation; consider using `--enable-preview` randomised hash seeds.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — HashMap is built on an array of buckets; O(1) array access is the foundation.
- `Hashing Techniques` — understanding hash functions, collisions, and distribution is required.

**Builds On This (learn these next):**
- `LRU Cache` — extends HashMap with a doubly linked list for O(1) eviction order.
- `Memoization` — uses a HashMap to cache recursive results and avoid recomputation.
- `Graph` — adjacency lists commonly stored as `Map<Node, List<Node>>`.

**Alternatives / Comparisons:**
- `TreeMap` — sorted key access at O(log N) cost; use when iteration order matters.
- `LinkedHashMap` — preserves insertion order or access order (LRU pattern).
- `ConcurrentHashMap` — thread-safe variant without full-map locking.

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Key-value store using hash function for   │
│              │ O(1) average get/put/remove               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Sequential search is O(N); any keyed      │
│ SOLVES       │ lookup needs O(1) direct access           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ O(1) is O(1) array access in disguise;    │
│              │ hash function = key → array index         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fast lookup, caching, frequency counting, │
│              │ deduplication, or memoization             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sorted iteration needed (use TreeMap)     │
│              │ or concurrent access (ConcurrentHashMap)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(1) access vs no ordering + rehash cost  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A post office where the key IS the       │
│              │  mailbox number"                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TreeMap → LRU Cache → Memoization         │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** Two Java developers argue: one says `new HashMap<>(1000)` is wasteful because the map will never hold more than 50 entries in practice. The other says `new HashMap<>()` is dangerous for a map that will hold exactly 900 entries at peak. Who is correct about what, and what is the exact calculation that determines when the default-constructed map will resize, and how many times?

**Q2.** A microservice caches user sessions in a `HashMap<String, Session>` on a single thread. Performance is acceptable at 10,000 users but degrades severely at 100,000 users even though theoretical O(1) should scale. A heap dump shows one bucket has 2,000 entries. What caused this, what data property would you examine in the session keys to confirm your hypothesis, and what would you change in the key design to fix it?

