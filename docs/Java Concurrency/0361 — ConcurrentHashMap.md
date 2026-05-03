---
layout: default
title: "ConcurrentHashMap"
parent: "Java Concurrency"
nav_order: 361
permalink: /java-concurrency/concurrenthashmap/
number: "0361"
category: Java Concurrency
difficulty: ★★★
depends_on: HashMap, Thread Safety, Lock Striping, CAS (Compare-And-Swap)
used_by: Cache Implementations, Concurrent Applications
related: HashMap, CopyOnWriteArrayList, HashTable
tags:
  - java
  - concurrency
  - deep-dive
  - data-structures
  - lock-free
---

# 0361 — ConcurrentHashMap

⚡ TL;DR — `ConcurrentHashMap` is a thread-safe `HashMap` that achieves high concurrency by using CAS + per-bucket synchronisation (Java 8+) instead of locking the entire map — allowing reads to proceed with no locks and writes to only lock the specific bucket being modified.

| #0361           | Category: Java Concurrency                                    | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | HashMap, Thread Safety, Lock Striping, CAS (Compare-And-Swap) |                 |
| **Used by:**    | Cache Implementations, Concurrent Applications                |                 |
| **Related:**    | HashMap, CopyOnWriteArrayList, HashTable                      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A shared counter map tracks request counts by endpoint. Without thread safety, two threads reading the same key and updating it lose updates (read-modify-write race). Using `HashMap` + `synchronized(map)` (or `Collections.synchronizedMap()`) puts a single lock on the entire map. Every read, every write, every compute — all serialised through one lock. With 16 threads, 15 are always waiting. Throughput collapses.

**THE BREAKING POINT:**
`HashTable` (the original Java thread-safe map) uses `synchronized` on every method. On a modern 16-core server, the lock contention makes `HashTable` barely faster than single-threaded code. `Collections.synchronizedMap` wraps every operation in `synchronized(this)` — same problem. The fundamental issue: locking the entire map for a single key operation means all map access is serialised, regardless of how many independent keys exist.

**THE INVENTION MOMENT:**
`ConcurrentHashMap` was designed around the insight that map operations on different keys are truly independent. Key A and Key B in different buckets have zero data sharing — they need no mutual exclusion. Lock only the bucket being modified, not the entire map. Reads don't need locks at all if data is accessed via volatile reads.

---

### 📘 Textbook Definition

**ConcurrentHashMap:** A thread-safe `HashMap` implementation (`java.util.concurrent.ConcurrentHashMap`) that supports full concurrency of retrievals and high expected concurrency for updates. In Java 8+, it uses a combination of CAS (Compare-And-Swap) for insertions into empty buckets and `synchronized` on individual bucket heads for non-empty buckets. It never locks the entire map. Reads are always lock-free. Null keys and null values are NOT permitted.

**Striped locking:** The pattern where instead of one lock protecting an entire data structure, N locks each protect 1/N of the structure. ConcurrentHashMap in Java 7 used 16 explicit `Segment` locks (each protecting 1/16 of the buckets). Java 8 eliminated the Segment abstraction — each bucket head node IS the lock.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ConcurrentHashMap lets 16 threads write to 16 different buckets simultaneously — no thread blocks another unless they hash to the exact same bucket.

**One analogy:**

> A regular locked map is a single-counter at a bank — one teller, everyone waits. ConcurrentHashMap is a bank with 1,000 teller stations. Customers (threads) go to their specific station (bucket). As long as no two customers need the same station simultaneously, there's zero waiting. The 1,000 stations share no locks — only customers needing the exact same station must coordinate.

**One insight:**
The key insight is structural: a hash map is already divided into independent buckets by design. `ConcurrentHashMap` leverages this existing structure to provide structural independence of locks. Two operations on different buckets are already logically independent — CHM just makes this physical reality explicit by locking at the bucket level rather than the map level.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Reads are always non-blocking (volatile node traversal).
2. Writes to an empty bucket use CAS (no lock).
3. Writes to a non-empty bucket synchronise on the bucket head node (`synchronized(node)`).
4. `size()` is approximate (uses a distributed counter across `CounterCell` objects).
5. Null keys and null values are explicitly forbidden (unlike `HashMap`).

**JAVA 8+ INTERNAL STRUCTURE:**

```
ConcurrentHashMap INTERNAL (Java 8+):

table: volatile Node[] (array of bucket heads)

Each bucket = linked list of Node → or TreeNode (red-black tree if > 8 entries)

Node:
  final int hash
  final K key
  volatile V val    ← volatile for lock-free reads
  volatile Node next ← volatile for lock-free traversal

Write to EMPTY bucket:
  CAS(table[i], null, newNode)  ← no lock needed

Write to NON-EMPTY bucket:
  synchronized(table[i]) {      ← lock only this bucket's head
    // insert/update within bucket
  }

Read (get):
  Node n = table[i]  ← volatile read
  while (n != null) {
    if (n.hash == hash && n.key.equals(key)) return n.val; ← volatile read
    n = n.next;       ← volatile read
  }
  return null;
  // Zero locks. Zero CAS. Pure volatile reads.
```

**JAVA 7 SEGMENT-BASED DESIGN (for comparison):**

```
16 Segment objects, each = mini-HashMap with its own ReentrantLock
Segment 0: buckets 0–N/16
Segment 1: buckets N/16 – 2N/16
...
Operations on same segment: synchronised
Operations on different segments: fully concurrent
size(): acquires ALL 16 locks briefly (expensive)
```

**NULL PROHIBITION:**
`HashMap` allows `null` key and value. `ConcurrentHashMap` does NOT. Reason: in a concurrent context, `map.get(key) == null` is ambiguous — does the key not exist, or does it map to null? With nullable values, you'd need `map.containsKey(key)` + `map.get(key)` as two operations, which is not atomic. Prohibiting null eliminates this ambiguity.

---

### 🧪 Thought Experiment

**SETUP:**
16 threads increment counters in a `Map<String, Long>`. Keys are URL paths. There are 1,000 distinct keys. Compare three implementations: `HashMap + synchronized`, `ConcurrentHashMap`, `ConcurrentHashMap.compute()`.

**HashMap + synchronized:**

```
All 16 threads contend on the same lock (the map object).
15 threads always waiting. 1 thread running.
Throughput: essentially single-threaded.
Lock contention: extreme (15/16 threads blocked at any moment).
```

**ConcurrentHashMap with manual read-modify-write:**

```java
// WRONG: two separate non-atomic operations:
Long current = map.get(key);       // read
map.put(key, current == null ? 1L : current + 1); // write
// Race: two threads read same value, both increment, one update is lost.
```

**ConcurrentHashMap.compute() (correct):**

```java
// CORRECT: atomic compute
map.compute(key, (k, v) -> v == null ? 1L : v + 1);
// compute() holds the bucket lock for the duration
// → exactly one thread updates each key at a time
// → 1000 keys → 1000 independent bucket locks
// → up to 16 threads can compute() simultaneously (if different buckets)
```

---

### 🧠 Mental Model / Analogy

> ConcurrentHashMap is a library with 1,000 separate catalogue drawers. A `HashMap + synchronized` is one master catalogue with a single lock — one librarian at a time. CHM lets up to 1,000 librarians work simultaneously, each updating their own drawer. Two librarians working on different drawers never interfere. Only two librarians trying to update the SAME drawer must take turns. Most of the time, they're in completely different drawers.

Explicit mapping:

- "catalogue drawers" → hash table buckets (array slots)
- "librarians" → threads
- "updating a drawer" → `put()`/`compute()`/`remove()`
- "single master lock" → `HashMap + synchronized`
- "1 librarian at a time" → `Collections.synchronizedMap`
- "drawer-level lock" → `synchronized(bucketHead)`

Where this analogy breaks down: in CHM, inserting a NEW entry into an empty drawer uses CAS (no lock at all — optimistic concurrent write). Only if two librarians simultaneously try to write to the same empty drawer does one retry. This is even faster than the "one librarian per drawer" model for the common case.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
ConcurrentHashMap is a thread-safe version of HashMap. You can use it from multiple threads simultaneously without any external synchronisation. It's much faster than using `synchronized(map)` because threads can work on different parts of the map at the same time.

**Level 2 — How to use it (junior developer):**
Drop-in replacement for `HashMap` in concurrent code. Use `computeIfAbsent()` for initialise-once patterns, `compute()` for atomic read-modify-write, `putIfAbsent()` for first-write-wins semantics. Do NOT use `null` keys or values. Use `getOrDefault()` instead of null-check-after-get. Remember `size()` is approximate in high-concurrency scenarios — use it for monitoring, not exact logic.

**Level 3 — How it works (mid-level engineer):**
Java 8+ CHM uses a flat `Node[]` table. Reads traverse the linked list / red-black tree using volatile reads (no lock). Writes to an empty bucket use a CAS on the table slot. Writes to occupied buckets use `synchronized(firstNode)` — only threads hashing to the same bucket contend. When a bucket has > 8 entries (same as `HashMap`), it converts the linked list to a red-black `TreeNode` structure for O(log n) lookup. `computeIfAbsent()`, `compute()`, and `merge()` are all atomic at the bucket level.

**Level 4 — Why it was designed this way (senior/staff):**
The Java 8 redesign eliminated the `Segment` abstraction (Java 7's approach). Segments required lock acquisition even for operations on the same segment but different buckets, and `size()` required acquiring all segment locks. The Java 8 design locks only the specific bucket head node — the minimum possible granularity. The use of `synchronized` (rather than `ReentrantLock`) on the bucket head was deliberate: since Java 6, biased locking and monomorphic call site optimisations make `synchronized` on a specific object nearly as fast as an uncontended `ReentrantLock`, but `synchronized` requires no separate lock object (the Node itself IS the monitor), saving memory. The volatile fields on Node (`val`, `next`) are the key to lock-free reads — as long as the JVM's memory model guarantees that volatile writes are visible to subsequent volatile reads, no read lock is needed.

---

### ⚙️ How It Works (Mechanism)

```
get(key):
  hash = spread(key.hashCode())
  i = (n-1) & hash           // bucket index
  Node e = tabAt(table, i)   // volatile read of table[i]
  while (e != null):
    if e.hash == hash && e.key.equals(key):
      return e.val            // volatile read — LOCK FREE
    e = e.next                // volatile read

put(key, value):
  hash = spread(key.hashCode())
  for (;;):                   // retry loop (CAS may fail)
    Node f = tabAt(table, i)  // volatile read
    if f == null:
      if casTabAt(table, i, null, new Node(hash, key, value)):
        break                 // CAS SUCCESS — no lock needed
      // else: CAS failed (concurrent insert) → retry loop
    else:
      synchronized(f):        // lock only THIS bucket's head
        // search bucket: update existing or append new node
        ...

compute(key, remappingFunction):
  // Similar to put, but always uses synchronized(f) for the
  // read-modify-write atomicity (function must run under lock)

size():
  // Does NOT lock anything
  // Uses sumCount() over distributed CounterCell[] cells
  // Result is approximate (due to concurrent modifications)
  // Use mappingCount() for long precision
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
ConcurrentHashMap<String, Long> counts = new ConcurrentHashMap<>();

Thread 1: counts.compute("GET /api/users", (k,v) -> v==null ? 1 : v+1)
Thread 2: counts.compute("POST /api/orders", (k,v) -> v==null ? 1 : v+1)
Thread 3: counts.compute("GET /api/users", (k,v) -> v==null ? 1 : v+1)

"GET /api/users" → hash → bucket 42
"POST /api/orders" → hash → bucket 87

Thread 1 and Thread 3 → both want bucket 42:
  One wins synchronized(bucket42Head), other waits.
  → Serialised at bucket level.

Thread 2 → bucket 87:
  No contention. Runs concurrently with Thread 1 AND Thread 3.
  → 2 of 3 operations run simultaneously.

Result: correct counters, no data loss, high concurrency.
```

---

### 💻 Code Example

**Example 1 — Atomic compute patterns:**

```java
ConcurrentHashMap<String, Long> requestCounts = new ConcurrentHashMap<>();

// WRONG: non-atomic read-modify-write
Long v = requestCounts.get(key);
requestCounts.put(key, v == null ? 1L : v + 1); // RACE CONDITION

// CORRECT: atomic compute
requestCounts.compute(key, (k, v) -> v == null ? 1L : v + 1);

// CORRECT: merge (clean for increment pattern)
requestCounts.merge(key, 1L, Long::sum);

// CORRECT: computeIfAbsent (lazy initialisation)
ConcurrentHashMap<String, List<String>> groups = new ConcurrentHashMap<>();
groups.computeIfAbsent("groupA", k -> new CopyOnWriteArrayList<>()).add("item");
// WARNING: the List itself is not thread-safe here — use CopyOnWriteArrayList
//          or ensure single-writer access to the List

// CORRECT: putIfAbsent (first-writer wins)
String existing = map.putIfAbsent("key", "value");
// returns null if inserted; returns existing value if key already present
```

**Example 2 — High-performance counter (prefer LongAdder for counters):**

```java
// For pure increment/decrement with no per-key reads needed:
// ConcurrentHashMap<String, LongAdder> is more efficient
ConcurrentHashMap<String, LongAdder> counters = new ConcurrentHashMap<>();

// Add count without checking first:
counters.computeIfAbsent(key, k -> new LongAdder()).increment();

// Read count:
LongAdder counter = counters.get(key);
long count = counter != null ? counter.sum() : 0L;
```

**Example 3 — Parallel bulk operations (Java 8+):**

```java
ConcurrentHashMap<String, Integer> scores = new ConcurrentHashMap<>();

// forEach parallel (threshold=1: always parallel)
scores.forEach(1, (key, value) -> {
    System.out.println(key + " → " + value);
});

// reduce parallel
int totalScore = scores.reduce(1, (k, v) -> v, Integer::sum);

// search parallel (returns first non-null result)
String highScorer = scores.search(1, (k, v) -> v > 100 ? k : null);
```

---

### ⚖️ Comparison Table

| Map                         | Thread-safe | Null keys/values | Concurrency level            | Notes                              |
| --------------------------- | ----------- | ---------------- | ---------------------------- | ---------------------------------- |
| **ConcurrentHashMap**       | Yes         | No / No          | High (per-bucket)            | Default choice for concurrent maps |
| HashMap                     | No          | Yes / Yes        | None (not thread-safe)       | Single-threaded only               |
| Collections.synchronizedMap | Yes         | Yes / Yes        | Low (whole-map lock)         | Avoid — high contention            |
| HashTable                   | Yes         | No / No          | Very Low (method-level lock) | Legacy; deprecated in practice     |
| ConcurrentSkipListMap       | Yes         | No / No          | High (lock-free)             | Sorted order; higher overhead      |

How to choose: `ConcurrentHashMap` for almost all concurrent map use cases. Use `ConcurrentSkipListMap` only when you need sorted key iteration. Never use `HashTable` or `Collections.synchronizedMap` in new code.

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                   |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "ConcurrentHashMap guarantees atomic compound operations"      | Only single operations (get, put, compute) are atomic. A logical compound operation like "if not present, compute and put" must use computeIfAbsent() — NOT separate get()+putIfAbsent(). |
| "size() is accurate"                                           | size() is approximate. Concurrent modifications may not be reflected. Use for monitoring only. Use `isEmpty()` for empty check (fast path).                                               |
| "I can store null to signal absence"                           | Null values are forbidden. Use Optional<V> or a sentinel value if you need to distinguish "not present" from "present with a specific marker".                                            |
| "ConcurrentHashMap is always faster than synchronized HashMap" | At very low concurrency (1–2 threads), the overhead of CAS and volatile fences makes CHM slightly slower than a simple synchronized map. CHM wins at 4+ concurrent threads.               |
| "computeIfAbsent is totally non-blocking"                      | computeIfAbsent CAN acquire the bucket lock if the bucket is non-empty. It uses CAS only for empty bucket insertion.                                                                      |

---

### 🚨 Failure Modes & Diagnosis

**1. Stale Reads in Multi-Step Logic**

**Symptom:** Application logic behaves incorrectly under concurrency — "check then act" logic produces wrong results. Example: code checks `map.containsKey(k)` then `map.get(k)`, but between the two calls another thread removes the key.

**Root Cause:** Using multiple separate CHM operations where atomicity is required.

**Diagnostic:**

```java
// WRONG (race between containsKey and get):
if (map.containsKey(key)) {
    Value v = map.get(key);  // key might be removed between these lines!
    process(v);
}

// CORRECT: single atomic operation:
Value v = map.get(key);
if (v != null) process(v);

// CORRECT: if you need getOrCreate:
Value v = map.computeIfAbsent(key, k -> createValue(k));
```

**Prevention:** Always use the atomic CHM methods (`compute`, `computeIfAbsent`, `merge`, `putIfAbsent`) rather than combining separate operations.

---

**2. DeadLock via computeIfAbsent Recursive Call**

**Symptom:** Application freezes. Thread dump shows thread in `ConcurrentHashMap.computeIfAbsent()` holding bucket lock, waiting for... the same lock.

**Root Cause (Java 8, fixed in Java 9):** In Java 8, calling `computeIfAbsent()` from WITHIN the mapping function of another `computeIfAbsent()` on the same CHM could deadlock if both map to the same bucket.

**Diagnostic:**

```bash
jstack <pid> | grep -B 5 "ConcurrentHashMap"
# Look for threads with the same CHM instance blocked
```

**Fix (Java 8):** Restructure code to avoid recursive CHM operations. Use a separate temporary map for the inner computation. Java 9+ fixed this specific deadlock.

**Prevention:** Avoid calling CHM methods within mapping functions that could hash to the same bucket.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HashMap` — the non-thread-safe foundation; understand its structure first
- `Thread Safety` — the problem CHM solves
- `CAS (Compare-And-Swap)` — the hardware instruction CHM uses for lock-free empty-bucket inserts
- `Lock Striping` — the general concurrency pattern CHM implements

**Builds On This (learn these next):**

- `Cache Implementations` — CHM is the typical backing store for in-process caches
- `LongAdder` — preferred alternative to `ConcurrentHashMap<K, AtomicLong>` for counters

**Alternatives / Comparisons:**

- `HashMap` — single-threaded only; never share without synchronisation
- `Collections.synchronizedMap` — whole-map lock; high contention; avoid
- `CopyOnWriteArrayList` — similar philosophy for lists (read-optimised)
- `ConcurrentSkipListMap` — sorted concurrent map; higher overhead

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Thread-safe HashMap: reads lock-free,     │
│              │ writes lock only the affected bucket      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Whole-map locking (HashTable/synced map)  │
│ SOLVES       │ serialises all access; destroys throughput│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Different keys → different buckets →      │
│              │ zero contention between independent ops   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Concurrent map access; shared caches;     │
│              │ multi-threaded counters/accumulators      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-threaded (HashMap is faster);      │
│              │ need null values (use wrapper/sentinel)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ High concurrency vs. slightly more CPU    │
│              │ than HashMap due to volatile + CAS        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "1000 tellers, not 1: different keys      │
│              │  never wait for each other."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LongAdder → CopyOnWriteArrayList          │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two threads simultaneously call `map.computeIfAbsent("X", k -> expensiveInit())`. Both find key "X" absent. Walk through exactly what happens at the CAS and synchronized-block level. Does `expensiveInit()` run once or twice? Is the outcome correct either way? What performance implication does this have for very expensive initialisation functions?

**Q2.** You need a concurrent map where the VALUE is also a mutable object that multiple threads update. For example: `ConcurrentHashMap<String, List<String>>` where multiple threads concurrently add to the list for the same key. Identify all the race conditions in a naïve implementation, and describe the correct pattern using only `ConcurrentHashMap` API and one other standard Java concurrent collection.
