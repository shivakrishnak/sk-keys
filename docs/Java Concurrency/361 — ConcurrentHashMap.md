---
layout: default
title: "ConcurrentHashMap"
parent: "Java Concurrency"
nav_order: 361
permalink: /java-concurrency/concurrenthashmap/
number: "361"
category: Java Concurrency
difficulty: ★★★
depends_on: HashMap, Race Condition, volatile, CAS
used_by: Caching, Shared Registries, Counters, Concurrent State
tags: #java, #concurrency, #collections, #lock-free, #hashmap
---

# 361 — ConcurrentHashMap

`#java` `#concurrency` `#collections` `#lock-free` `#hashmap`

⚡ TL;DR — ConcurrentHashMap is a fully thread-safe HashMap that uses lock-striping (Java 7) or CAS + synchronized-on-bucket (Java 8+) to allow concurrent reads with zero locking and concurrent writes with minimal contention.

| #361 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | HashMap, Race Condition, volatile, CAS | |
| **Used by:** | Caching, Shared Registries, Counters, Concurrent State | |

---

### 📘 Textbook Definition

`java.util.concurrent.ConcurrentHashMap<K,V>` is a hash table supporting full concurrency for reads and high concurrency for writes. In Java 8+, it uses `volatile` array entries for lock-free reads, CAS operations for initial bucket insertions, and synchronized blocks on individual bucket heads for collision chains. It provides additional atomic operations: `putIfAbsent`, `computeIfAbsent`, `computeIfPresent`, `compute`, and `merge` — which are atomically safe for compound read-modify-write patterns.

---

### 🟢 Simple Definition (Easy)

`HashMap` is NOT thread-safe — using it from multiple threads causes data corruption and infinite loops. `ConcurrentHashMap` is the thread-safe drop-in replacement. Multiple threads can read simultaneously with no locking. Writes only lock the specific bucket being modified — not the whole map.

---

### 🔵 Simple Definition (Elaborated)

`Collections.synchronizedMap(new HashMap<>())` puts a single lock around the entire map — every read and write goes through the same mutex. ConcurrentHashMap is far smarter: reads are lock-free (volatile reads), and writes only lock the specific bucket (array slot) being modified. A map with 16 buckets can have 16 writes happening concurrently in different buckets simultaneously. Java 8+ uses CAS for the common case (empty bucket), making most insertions completely lock-free.

---

### 🔩 First Principles Explanation

```
HashMap under concurrent access (Java 8+):
  ✗ Two threads resize simultaneously → infinite loop in linked list
  ✗ Two threads insert with same key → data loss
  ✗ One reads, one writes → partially-visible state

Collections.synchronizedMap:
  lock(map) → read/write → unlock(map)
  → Only ONE thread in the entire map at a time
  → 16 threads, 1 lock → 15 threads blocked 94% of the time

ConcurrentHashMap (Java 8):
  Reads: volatile read of bucket array → no lock → all threads read simultaneously
  Write to empty bucket: CAS(null → node) → no lock → concurrent safe insert
  Write to non-empty bucket: synchronized(bucket_head) → only locks ONE bucket
  → 16 threads writing to 16 different buckets → all proceed simultaneously
```

**Atomic compound operations (critical):**

```
map.get(key) + check + map.put(key, val)  ← NOT atomic (race between get and put)

map.putIfAbsent(key, val)                 ← ATOMIC single operation
map.computeIfAbsent(key, k -> compute(k)) ← ATOMIC: compute and put only if absent
map.compute(key, (k,v) -> v == null ? 1 : v+1)  ← ATOMIC increment
map.merge(key, 1, Integer::sum)           ← ATOMIC accumulate
```

---

### 🧠 Mental Model / Analogy

> A library with 1000 shelves. The old synchronized library: one librarian holds the master key — only one person can access anything at once. ConcurrentHashMap: each shelf has its own small lock. Reading? Anyone can browse freely (no lock). Adding to a shelf? You only lock THAT shelf, not the whole library. Thousands of readers and hundreds of writers simultaneously — only conflict when two people reach for the SAME shelf.

---

### ⚙️ How It Works

```
Java 8+ internals:
  Node<K,V>[] table — volatile array of bucket heads

  READ (get):
    volatile read of table[hash & (n-1)]
    traverse linked list / tree nodes (no lock needed — volatile visibility)

  WRITE to empty bucket:
    CAS(table[i], null, newNode) — lock-free insert

  WRITE to non-empty bucket (collision):
    synchronized(bucket_head) { insert/update chain or tree }

  RESIZE:
    Multiple threads cooperate on resize (transfer tasks)
    Uses forwarding nodes to signal "bucket moved"

Key additional operations:
  putIfAbsent(key, value)                → absent-only insert (atomic)
  computeIfAbsent(key, Function<K,V>)    → compute and put only if absent (atomic)
  computeIfPresent(key, BiFunction)      → update only if present (atomic)
  compute(key, BiFunction<K,V,V>)        → atomic read-modify-write
  merge(key, value, BiFunction<V,V,V>)   → combine with existing (atomic)
  getOrDefault(key, defaultVal)          → null-safe read
  forEach(long parallelismThreshold, BiConsumer) → parallel scan
```

---

### 🔄 How It Connects

```
ConcurrentHashMap
  ├─ vs HashMap                  → CHM is thread-safe; HashMap is not
  ├─ vs synchronizedMap          → CHM has much higher concurrency
  ├─ vs Hashtable                → CHM is modern, more concurrent, no full-map lock
  ├─ compute/merge/computeIfAbsent → atomic compound ops replace get+check+put
  └─ size() is approximate       → LongAdder-like counter cells; not exact under concurrency
```

---

### 💻 Code Example

```java
// Basic thread-safe operations
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
map.put("a", 1);
map.get("a");           // lock-free read
map.remove("a");        // locked write on bucket

// Thread-safe counter — WRONG way vs RIGHT way
// ❌ Not atomic: get + check + put are 3 separate operations
Integer count = map.get(key);
map.put(key, count == null ? 1 : count + 1);  // race between get and put

// ✅ Atomic: compute is a single atomic operation
map.compute(key, (k, v) -> v == null ? 1 : v + 1);
map.merge(key, 1, Integer::sum);  // even cleaner
```

```java
// computeIfAbsent — thread-safe lazy initialisation
ConcurrentHashMap<String, List<String>> groups = new ConcurrentHashMap<>();
groups.computeIfAbsent(userId, k -> new CopyOnWriteArrayList<>()).add(item);
// Only ONE list is created per key even if 100 threads call this simultaneously
```

```java
// putIfAbsent — singleton pattern
ConcurrentHashMap<String, Connection> connections = new ConcurrentHashMap<>();
Connection newConn = createConnection(host);
Connection existing = connections.putIfAbsent(host, newConn);
if (existing != null) {
    newConn.close();   // another thread beat us — use theirs, close ours
    return existing;
}
return newConn;
```

```java
// Parallel aggregation — forEach with parallelism threshold
ConcurrentHashMap<String, Long> wordCount = new ConcurrentHashMap<>();
// Parallelism threshold: 1 = use all cores; Long.MAX_VALUE = always sequential
long totalWords = wordCount.reduceValues(1L, Long::sum);

wordCount.forEach(1L, (word, count) ->
    System.out.println(word + ": " + count)); // parallel scan
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| CHM.size() is always accurate | `size()` is approximate under concurrent modification; individual ops are atomic |
| get() + put() as a compound op is safe | These are two separate atomic ops — a race exists between them; use `compute()/merge()` |
| CHM prevents all race conditions | CHM makes individual ops atomic; multi-step logic still needs `compute()`/`merge()` |
| ConcurrentHashMap null keys/values allowed | `null` keys and values throw `NullPointerException` (unlike HashMap which allows one null key) |

---

### 🔥 Pitfalls in Production

**Pitfall 1: check-then-put race condition**

```java
// ❌ Race: two threads both see absent, both put
if (!map.containsKey(key)) {
    map.put(key, expensiveComputation());
}
// ✅ Use computeIfAbsent
map.computeIfAbsent(key, k -> expensiveComputation());
```

**Pitfall 2: Blocking inside computeIfAbsent — deadlock risk**

```java
// ❌ Calling computeIfAbsent recursively on same map with same key → deadlock
map.computeIfAbsent("key", k -> {
    return map.computeIfAbsent("key", k2 -> "value"); // same key → deadlock
});
// Fix: avoid re-entry into the map with the same key during compute
```

---

### 🔗 Related Keywords

- **[Race Condition](./072 — Race Condition.md)** — what CHM prevents for individual ops
- **[volatile](./070 — volatile.md)** — used internally for lock-free reads
- **[Atomic Variables](./077 — Atomic Variables.md)** — CAS used internally for empty-bucket inserts
- **HashMap** — non-thread-safe predecessor; never use for shared mutable state
- **[CopyOnWriteArrayList](./091 — CopyOnWriteArrayList.md)** — complementary for concurrent lists

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Lock-free reads; per-bucket CAS/sync writes;  │
│              │ atomic compound ops via compute/merge         │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Shared mutable map; caches; counters; any map │
│              │ accessed by multiple threads                  │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Multi-step logic — always use compute/merge;  │
│              │ never null keys or values                     │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "HashMap for one thread; ConcurrentHashMap    │
│              │  for many — and always use compute()"        │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ computeIfAbsent → merge → CopyOnWriteList →   │
│              │ ConcurrentLinkedQueue → LongAdder             │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You need a thread-safe `Set` backed by `ConcurrentHashMap`. How would you create one? (Hint: Java provides a factory method.)

**Q2.** `computeIfAbsent` guarantees the function runs at most once per key even if 100 threads call it simultaneously. What internal mechanism ensures this? Can the function ever be called more than once?

**Q3.** `size()` on a ConcurrentHashMap is not guaranteed to be accurate under concurrent modification. Why doesn't this violate thread safety? When would you use `mappingCount()` instead of `size()`?

