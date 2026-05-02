---
layout: default
title: "Hashing Techniques"
parent: "Data Structures & Algorithms"
nav_order: 75
permalink: /dsa/hashing-techniques/
number: "0075"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, HashMap, Time Complexity / Big-O
used_by: String Matching (KMP, Rabin-Karp), Bloom Filter, Consistent Hash Ring
related: HashMap, Bloom Filter, Consistent Hash Ring
tags:
  - algorithm
  - intermediate
  - datastructure
  - performance
  - pattern
---

# 075 — Hashing Techniques

⚡ TL;DR — Hashing maps arbitrary-size keys to fixed-size integers, enabling O(1) average lookup, insertion, and deletion regardless of data size.

| #0075 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, HashMap, Time Complexity / Big-O | |
| **Used by:** | String Matching (KMP, Rabin-Karp), Bloom Filter, Consistent Hash Ring | |
| **Related:** | HashMap, Bloom Filter, Consistent Hash Ring | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Store 1 million user records and look up any user by ID in under 1 millisecond. A sorted array + binary search gives O(log N) = 20 comparisons — 20 microseconds at 1µs/comparison: fast. But INSERT requires O(N) shifts for a sorted array. A linked list: O(N) lookup. A BST: O(log N) average but O(N) worst case. At 1 million lookups/second from a hot database, even O(log N) latency adds up.

THE BREAKING POINT:
O(log N) is not O(1). For a 64-key table vs 64 million keys, binary search takes 6 vs 26 comparisons — a 4× slowdown. For a 10 billion-key table driven by global traffic, latency grows with every doubling of users. A cache lookup 50 million times per second cannot afford even 30 comparisons per call.

THE INVENTION MOMENT:
What if you could compute the exact storage location of a key in O(1), regardless of how many other keys exist? A **hash function** converts any key to an integer index. Given a fixed-size array, `index = hash(key) % arraySize` directly locates the bucket with no comparisons. O(1) insert, O(1) lookup, O(1) delete — independent of N. This is why **Hashing Techniques** were created.

---

### 📘 Textbook Definition

A **hash function** maps a key of arbitrary size to a fixed-size integer (the **hash code**) deterministically and efficiently. A **hash table** uses this hash code, reduced modulo table capacity, to determine an array bucket for each key. **Collision resolution** handles cases where two distinct keys hash to the same bucket; strategies include chaining (linked list per bucket) and open addressing (linear/quadratic probing, double hashing). A well-designed hash function distributes keys uniformly, minimises collisions, and executes in O(1). Under uniform distribution with load factor α = N/capacity, expected operations are O(1) average, O(N) worst case.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Convert any key to a number, use that number as an array index — find anything in one step.

**One analogy:**
> A classroom assigns every student a unique locker number based on their birthday (e.g., day-of-year mod 100). To find Sarah's locker, you calculate her birthday → number → walk straight to that locker. You never search every locker. Two students with the same locker number (collision) share a larger locker with multiple compartments.

**One insight:**
A hash function's quality is measured by two properties: **uniformity** (evenly distributes keys across all buckets, minimising collisions) and **avalanche effect** (changing even one bit of the key completely scrambles the hash, preventing patterns). A bad hash function — like using just the last digit of a number — clusters keys in a few buckets and degrades O(1) to O(N).

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. The hash function must be **deterministic**: the same key always produces the same hash code.
2. The hash function must be **O(1)** (or at most O(key length)) per computation.
3. The table must define a **collision resolution** strategy: no hash function is perfect, so collisions must be handled gracefully.

DERIVED DESIGN:
The ideal hash function is a **uniform random oracle**: each key maps uniformly and independently to a random bucket. In practice, good approximations use polynomial rolling hashes for strings, multiply-shift for integers, and cryptographic hash functions (SHA, MD5) when security or content-addressing is required.

**Chaining vs open addressing:**
- **Chaining:** Each bucket holds a linked list. Load factor can exceed 1. Easy to implement. Cache-unfriendly (pointer chasing).
- **Open addressing:** All entries in one contiguous array. Probing finds next empty slot on collision. Cache-friendly. Table cannot exceed load factor ~0.7 before performance degrades.

**Fundamental trade-off:** load factor `α = N/M` (N keys, M buckets).
- Expected chain length = α.
- Expected probes in open addressing ≈ 1/(1-α) (goes to ∞ as α→1).
- Java HashMap resizes at α=0.75 (default); load factor > 0.7 causes excessive collisions.

THE TRADE-OFFS:
Gain: O(1) average operations; no dependency on data size N.
Cost: O(N) worst case (all keys collide); non-deterministic ordering (unsorted); requires a good hash function; memory overhead (unused buckets; load factor < 1 wastes space).

---

### 🧪 Thought Experiment

SETUP:
Hash table with capacity 5. Keys: 10, 15, 20, 25, 30. Hash function: `key % 5`.

WHAT HAPPENS WITH BAD HASH FUNCTION:
All keys are multiples of 5: 10%5=0, 15%5=0, 20%5=0, 25%5=0, 30%5=0. Every key maps to bucket 0! The hash table degrades to a linked list of length 5 in bucket 0. Lookup time: O(N). This is a hash collision catastrophe.

WHAT HAPPENS WITH GOOD HASH FUNCTION (keys: 11, 13, 17, 19, 23):
11%5=1, 13%5=3, 17%5=2, 19%5=4, 23%5=3. One collision at bucket 3. All others in separate buckets. Lookup: O(1) for 4 keys, O(2) for bucket 3. Average: O(1).

THE INSIGHT:
The choice of table capacity matters: use a prime number as table size to reduce patterns in key distributions. Using a power-of-2 capacity with `key & (cap-1)` is fast but exposes clustering for keys that are multiples of the capacity. Java HashMap uses power-of-2 capacity with additional hash mixing (upper bits folded in) to compensate.

---

### 🧠 Mental Model / Analogy

> Hashing is like a filing system where the folder label is derived from the document's content. You scan the first paragraph of a document, run a formula, and that formula tells you: "This document belongs in drawer 42." To find it later, run the same formula on the title — immediately go to drawer 42. No need to scan all drawers. If two documents hash to drawer 42 (collision), the drawer holds both — you scan only that drawer's contents.

"Document content" → key
"Formula (hash function)" → hash computation
"Drawer number" → hash code mod capacity
"Drawer with multiple items" → collision: chaining or probing
"Filing once, finding instantly" → O(1) average

Where this analogy breaks down: Unlike a filing cabinet, hash tables can resize (rehash all entries when capacity is exceeded) — no physical filing cabinet doubles in size. Also, the analogy doesn't capture why uniformity of the formula matters for performance.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Hashing is a way to instantly find where something is stored. Instead of looking through everything, you run a quick calculation on the key and it tells you exactly where to look. It's like knowing the exact shelf number where a library book lives, rather than searching shelf by shelf.

**Level 2 — How to use it (junior developer):**
Use `HashMap<K,V>` in Java for most cases. Ensure keys override `hashCode()` and `equals()` correctly (they always go together in Java). Never use mutable objects as keys — if the key changes after insertion, the hash code changes and you can never find the entry again. Set initial capacity if you know N to avoid expensive resize operations: `new HashMap<>(N / 0.75 + 1)`.

**Level 3 — How it works (mid-level engineer):**
Java's `HashMap` uses chaining with a twist: above 8 entries per bucket, the chain converts to a red-black tree (O(log N) worst case vs O(N)). Hash codes are mixed: `h = key.hashCode(); h ^= (h >>> 16)` — this spreads high bits into low bits to improve distribution in small tables (low-index buckets tend to use only the lowest bits of hash code). Resize doubles capacity and rehashes all entries: O(N) total but O(1) amortized. ConcurrentHashMap uses 16-segment locking (Java 7) or per-bucket CAS (Java 8+) for concurrency.

**Level 4 — Why it was designed this way (senior/staff):**
The choice of prime vs power-of-2 table size reflects a fundamental trade-off: power-of-2 enables `hash & (cap-1)` (1 cycle) vs prime modulo `hash % prime` (multiple cycles). Java chose power-of-2 with supplemental hash mixing to get both speed and uniformity. Universal hashing — choosing a random hash function from a family at table creation time — provides expected O(1) regardless of input distribution, even adversarial. This is the basis of Cuckoo hashing (O(1) worst-case lookup), HopScotch hashing (cache-friendly, O(1) worst lookup), and Robin Hood hashing (reduces variance, not average). At 10B keys, consistent hashing distributes across machines while maintaining O(1) node membership changes.

---

### ⚙️ How It Works (Mechanism)

**Chaining hash table:**

```
┌────────────────────────────────────────────────┐
│ HashMap: capacity=8, keys: "cat","dog","ant"   │
│                                                │
│  hash("cat") % 8 = 3                          │
│  hash("dog") % 8 = 7                          │
│  hash("ant") % 8 = 3  ← collision with "cat"  │
│                                                │
│  Bucket 0: []                                  │
│  Bucket 1: []                                  │
│  Bucket 2: []                                  │
│  Bucket 3: ["cat"→value1] → ["ant"→value2]    │
│  Bucket 4: []                                  │
│  Bucket 5: []                                  │
│  Bucket 6: []                                  │
│  Bucket 7: ["dog"→value3]                      │
│                                                │
│  Lookup "ant": hash→3 → scan chain → found    │
└────────────────────────────────────────────────┘
```

**Open Addressing (linear probing):**

```
┌────────────────────────────────────────────────┐
│ Linear Probing: insert key=15 into capacity=7  │
│                                                │
│  hash(15) % 7 = 1                              │
│  Slot 1: OCCUPIED by key=8                     │
│  Probe slot 2: EMPTY → insert 15 at slot 2     │
│                                                │
│  Lookup 15: hash=1, slot 1≠15, probe 2=15 ✓   │
│                                                │
│  DELETE: mark slot as TOMBSTONE (not empty)    │
│  → future probes skip tombstones but don't    │
│    stop early                                 │
└────────────────────────────────────────────────┘
```

**Polynomial rolling hash for strings:**
```
h("abc") = ('a' * 31^2 + 'b' * 31^1 + 'c' * 31^0) % large_prime
         = (97*961 + 98*31 + 99) % MOD
         = (93217 + 3038 + 99) % MOD
         = 96354 % MOD
```
Used in Java `String.hashCode()` with base=31. Prime base 31 provides good distribution; 31 = 2^5 - 1, enabling fast computation: `31*n == (n<<5) - n`.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Key (string, integer, object)
→ Hash function: key → 32/64-bit integer
→ Reduce: hash % capacity → bucket index
→ [HASH TABLE ← YOU ARE HERE]
  → Check bucket for key equality
  → On collision: chain or probe
  → On load factor exceeded: resize → rehash all
→ Return value or null
```

FAILURE PATH:
```
All keys hash to same bucket
→ O(N) lookup after N insertions
→ Symptom: single-threaded HashMap slows to O(N)
→ Diagnostic: HashMap.getOrDefault + timing; or
  monitor bucket distribution in custom table
→ Fix: better hash function; use prime table size;
  supplement hash (Java HashMap does this)
```

WHAT CHANGES AT SCALE:
At 1 billion keys distributed across 1,000 servers, consistent hashing assigns each key to a server in O(1) + O(K) (K virtual nodes per server) without remapping all keys when servers join/leave. This is a distributed extension of the same hash-to-bucket concept, but the "bucket" is now a server node on a ring, and resizing (adding a server) only remaps N/S keys (N total, S servers) instead of all N. CockroachDB, Cassandra, and Redis Cluster use consistent hashing or virtual-node variants of it.

---

### 💻 Code Example

**Example 1 — HashMap with correct equals/hashCode:**
```java
class Point {
    int x, y;
    Point(int x, int y) { this.x=x; this.y=y; }
    // REQUIRED: both hashCode and equals
    @Override public int hashCode() {
        return Objects.hash(x, y);
    }
    @Override public boolean equals(Object o) {
        if (!(o instanceof Point)) return false;
        Point p = (Point) o;
        return x == p.x && y == p.y;
    }
}
// Usage: O(1) average lookup
Map<Point, String> map = new HashMap<>();
map.put(new Point(1, 2), "A");
map.get(new Point(1, 2)); // → "A" ✓
```

**Example 2 — Frequency counting (classic hashing use):**
```java
// Count word frequencies in O(N)
Map<String, Integer> freq = new HashMap<>();
for (String word : words)
    freq.merge(word, 1, Integer::sum);
// Top K frequent: O(N log K) using a heap
```

**Example 3 — Rolling hash for substring deduplication:**
```java
// Find duplicate substrings of length L in O(N·L)
// Using hashing: O(N) average
Set<Long> seen = new HashSet<>();
long hash = 0, base = 31, mod = 1_000_000_007L;
long pow = 1;
for (int i = 0; i < L - 1; i++) pow = pow * base % mod;
for (int i = 0; i < L; i++)
    hash = (hash * base + s.charAt(i)) % mod;
seen.add(hash);
for (int i = L; i < s.length(); i++) {
    hash = (hash - s.charAt(i-L) * pow % mod + mod) % mod;
    hash = (hash * base + s.charAt(i)) % mod;
    if (!seen.add(hash)) // collision possible; add equals check
        System.out.println("Duplicate at " + (i-L+1));
}
```

**Example 4 — Two-sum using HashMap (O(N)):**
```java
// BAD: nested loop O(N²)
for (int i = 0; i < n; i++)
    for (int j = i+1; j < n; j++)
        if (nums[i] + nums[j] == target) ...

// GOOD: HashMap complement lookup O(N)
Map<Integer, Integer> seen = new HashMap<>();
for (int i = 0; i < nums.length; i++) {
    int complement = target - nums[i];
    if (seen.containsKey(complement))
        return new int[]{seen.get(complement), i};
    seen.put(nums[i], i);
}
```

---

### ⚖️ Comparison Table

| Structure | Lookup | Insert | Delete | Space | Ordered |
|---|---|---|---|---|---|
| **Hash Table** | O(1) avg | O(1) avg | O(1) avg | O(N) | No |
| TreeMap (BST) | O(log N) | O(log N) | O(log N) | O(N) | Yes |
| Sorted Array | O(log N) | O(N) | O(N) | O(N) | Yes |
| LinkedList | O(N) | O(1) | O(1) | O(N) | Insertion order |
| Trie | O(M) | O(M) | O(M) | O(N·M) | Lexicographic |

How to choose: Use HashMap for O(1) operations on unordered data. Use TreeMap when you need sorted iteration or range queries. Use a sorted array when data is mostly static and binary search suffices.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| HashMap is always O(1) | Worst case is O(N) when all keys collide to the same bucket. Java 8 converts chains > 8 entries to red-black trees for O(log N) worst case within a bucket. |
| You can use mutable objects as HashMap keys safely | If a key's hash code changes after insertion, the key is permanently lost in the table — you'll never find it again. Always use immutable keys. |
| Two objects that are equal don't need the same hashCode | WRONG. The Java contract: if `a.equals(b)` then `a.hashCode() == b.hashCode()`. Violation causes `get` to always return null even for equal keys. |
| A larger table always means better performance | A 10× oversized table wastes memory and may increase CPU cache misses (table doesn't fit in L2 cache), hurting performance for small N. |
| HashCode must be unique across all objects | Only `equals()`-equal objects must share the same hashCode. Different objects can and do share hashCodes (collisions); the table handles this via chaining or probing. |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing or broken `hashCode()`/`equals()` override**

Symptom: `map.get(key)` returns null even though `key` was inserted; `map.containsKey(key)` returns false.

Root Cause: Default `Object.hashCode()` uses memory address; two logically equal objects (same field values) have different hash codes → mapped to different buckets → key not found.

Diagnostic:
```java
Point p1 = new Point(1, 2);
Point p2 = new Point(1, 2);
System.out.println(p1.hashCode() == p2.hashCode()); // false if broken
System.out.println(p1.equals(p2)); // false if broken
```

Fix: Override both `hashCode()` and `equals()`. Use `Objects.hash(field1, field2, ...)`.

Prevention: Use IDE-generated `hashCode`/`equals` or Lombok `@EqualsAndHashCode`.

---

**2. ConcurrentModificationException during iteration**

Symptom: `ConcurrentModificationException` when modifying HashMap while iterating.

Root Cause: HashMap maintains a `modCount` counter; the iterator captures this value and throws if the count changed.

Diagnostic:
```bash
# Stack trace: java.util.ConcurrentModificationException
#   at java.util.HashMap$HashIterator.nextNode(HashMap.java:1445)
```

Fix: Collect keys to remove first, then remove after iteration. Or use `ConcurrentHashMap` for concurrent access.

Prevention: Never add/remove from a HashMap while iterating it without using the Iterator's `remove()` method.

---

**3. Hash function clustering (poor distribution)**

Symptom: HashMap operations suddenly slow to milliseconds instead of microseconds for certain inputs.

Root Cause: Input keys have patterns that cause many collisions (e.g., all keys divisible by table capacity). Attack vectors: HashDoS attack uses crafted strings that all hash to the same bucket.

Diagnostic:
```bash
# Profile with async-profiler:
java -agentpath:libasyncProfiler.so=start,event=cpu,file=out.html MyApp
# Look for hot path in ConcurrentHashMap$Node.find or HashMap.getNode
```

Fix: Java HashMap uses randomised hash key per JVM start (JEPS 180, Java 8) to prevent HashDoS. For custom hash tables, use universal hashing or randomised seeds.

Prevention: Set `-Djdk.map.althashing.threshold=0` in older JVMs; use `ConcurrentHashMap` for concurrent access.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Array` — Hash tables are backed by an array; bucket indexing is an array access.
- `HashMap` — The canonical data structure built on hashing; understand its API before diving into internal mechanics.
- `Time Complexity / Big-O` — Understanding why O(1) average differs from O(N) worst case is essential for hash table analysis.

**Builds On This (learn these next):**
- `Bloom Filter` — Uses multiple hash functions applied to a bit array; a space-efficient probabilistic set using hashing.
- `Consistent Hash Ring` — Distributes keys across nodes using hashing; when a node is added/removed only N/M keys are remapped.
- `String Matching (Rabin-Karp)` — Uses rolling polynomial hashing to match patterns in O(N+M) average.

**Alternatives / Comparisons:**
- `TreeMap` — O(log N) operations but maintains sorted order; use for range queries or ordered iteration.
- `Trie` — O(M) per operation (M = key length): preferable for string prefix matching; uses more memory.
- `Skip List` — O(log N) probabilistic; sorted; used in Redis sorted sets as an alternative to balanced BST.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Key → integer index mapping for O(1)      │
│              │ average insert/lookup/delete in arrays    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ O(log N) or O(N) search in sorted/unsorted│
│ SOLVES       │ structures; grows with N; hashing is O(1) │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Uniform distribution of keys across       │
│              │ buckets is everything — a bad hash degrades│
│              │ O(1) to O(N)                              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Lookups/inserts by key; frequency         │
│              │ counting; deduplication; caching keys      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need ordered iteration or range queries   │
│              │ (use TreeMap); adversarial inputs possible │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(1) ops vs no ordering, O(N) worst case  │
│              │ collision, memory overhead at low load    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Know the address before you arrive"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bloom Filter → Consistent Hashing → LRU   │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `String.hashCode()` is pure (same string always returns same code), deterministic, and uses a 31-based polynomial. A HashDoS attack constructs thousands of strings that all hash to the same value, forcing O(N²) performance. Java 8 introduced randomised seeds for HashMap hash keys. But `String.hashCode()` itself is still deterministic — how does Java prevent HashDoS if `hashCode()` hasn't changed? What is the exact mechanism (JEPS 180), and does this fully protect against specially crafted key inputs?

**Q2.** You need to find all pairs (i, j) in an array where `arr[i] + arr[j] == target` in O(N) time and O(N) space. Write the algorithm and then extend it: what if you need all triplets summing to 0? The two-sum HashMap approach doesn't directly generalise to three-sum with O(N) time — why not, and what is the optimal approach for three-sum? How does this relate to the fundamental difference between O(1) point lookup and O(N) set enumeration?

