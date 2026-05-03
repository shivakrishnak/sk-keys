---
layout: default
title: "ConcurrentHashMap"
parent: "Java Concurrency"
nav_order: 361
permalink: /java-concurrency/concurrenthashmap/
number: "0361"
category: Java Concurrency
difficulty: ★★★
depends_on: HashMap, Thread Safety, Synchronization, Hash Table, Segment Locking
used_by: Caching, Shared State, Count Aggregation, Registry Pattern
related: HashMap, Hashtable, CopyOnWriteArrayList, AtomicReference, Segment Locking
tags:
  - concurrency
  - map
  - thread-safe
  - java
  - advanced
  - lock-striping
---

# 361 — ConcurrentHashMap

⚡ TL;DR — ConcurrentHashMap provides a thread-safe HashMap with lock-free reads, stripe-level (per-bucket) writes, and atomic bulk operations, achieving far higher concurrency than `Collections.synchronizedMap` or `Hashtable`.

| #0361           | Category: Java Concurrency                                                 | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | HashMap, Thread Safety, Synchronization, Hash Table, Segment Locking       |                 |
| **Used by:**    | Caching, Shared State, Count Aggregation, Registry Pattern                 |                 |
| **Related:**    | HashMap, Hashtable, CopyOnWriteArrayList, AtomicReference, Segment Locking |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A web server has a request counter map (path → count). Multiple threads update it simultaneously. Using `HashMap`: data corruption, lost updates, infinite loops in resize. Using `Collections.synchronizedMap(new HashMap<>())` or `Hashtable`: every read and write acquires the same global lock. At 10,000 RPS with 100 threads, 99 threads are always waiting for the 1 thread holding the lock. You've added thread safety but destroyed throughput.

**THE BREAKING POINT:**
Most concurrent map use cases have many reads for every write, and writes to different keys are independent. A single global lock treats a write to key "A" as blocking reads of key "Z" — a false dependency that destroys parallelism.

**THE INVENTION MOMENT:**
`ConcurrentHashMap` (Java 5+, redesigned in Java 8) decomposes the locking: reads are lock-free using `volatile` reads and CAS operations. Writes lock only the specific bucket being modified (a single array slot in Java 8+), not the whole table. 100 threads writing to 100 different keys can proceed simultaneously. Result: orders-of-magnitude better throughput under concurrent access.

---

### 📘 Textbook Definition

**ConcurrentHashMap** is a thread-safe hash table implementation in `java.util.concurrent` designed for high concurrency. In Java 8+, the internal structure is an array of `Node` objects where each bucket (array slot) is independently locked during write operations via `synchronized` on the bucket head node, while reads use `volatile` and CAS (Compare-And-Swap) operations without locking. Key guarantees: (1) reads are always non-blocking and return a consistent view of the data at some point during the call; (2) writes to different buckets are fully parallel; (3) bulk operations like `putIfAbsent`, `computeIfAbsent`, `merge`, and `forEach` are atomic at the key level; (4) `size()` is an approximation under concurrent modification. Does not allow `null` keys or values.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ConcurrentHashMap is a HashMap where reads never block and writes only lock one bucket at a time, so 100 threads can work on 100 different keys simultaneously.

**One analogy:**

> ConcurrentHashMap is a filing cabinet with 1024 individual drawers, each with its own lock. Reading a file: no lock needed (files are self-consistent). Writing to drawer 47: lock drawer 47 only. All other 1023 drawers are completely unaffected. Compare to a single locked cabinet door (Hashtable) where nobody can access any drawer while one person updates any single file.

**One insight:**
The most powerful aspect of ConcurrentHashMap is not its concurrent get/put — it's atomic compound operations like `computeIfAbsent(key, supplier)`. These guarantee that the supplier is called at most once per key even under concurrent access, eliminating the classic check-then-act race condition.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The backing array is `volatile Node<K,V>[]` — reads without locking always see the latest array reference.
2. Writes to an empty bucket: use CAS to atomically insert the first node.
3. Writes to a non-empty bucket: `synchronized(bucketHeadNode)` — only that bucket is locked.
4. Table resize: uses a cooperative multi-threaded transfer protocol; threads helping with resize are safe.
5. `null` keys and values are forbidden (unlike HashMap).

**DERIVED DESIGN:**

```
JAVA 8+ INTERNAL STRUCTURE:
┌────────────────────────────────────────────────────────┐
│  volatile Node<K,V>[] table  (power-of-2 length)       │
│                                                        │
│  table[0]: null (empty bucket)                         │
│  table[1]: Node{key="A", val=1} → Node{key="C", val=3} │
│  table[2]: TreeNode{...}  (bin converted to red-black  │
│            tree when chain length > 8)                 │
│  table[3]: ForwardingNode{...} (bucket being resized)  │
│  ...                                                   │
└────────────────────────────────────────────────────────┘

READ (get):
  1. Compute hash
  2. Volatile read: node = table[hash & (len-1)]
  3. Walk chain/tree: compare key using == and equals()
  4. No lock acquired. Returns value or null.

WRITE (put) - empty bucket:
  1. Compute hash, check table[bucket] == null
  2. CAS(table[bucket], null, newNode)
  3. If CAS fails (concurrent insert): retry

WRITE (put) - non-empty bucket:
  1. synchronized(table[bucket]) {
  2.   walk chain, insert or update node
  3. }  // only this bucket locked
```

```java
// Demonstrating the lock granularity:
// Thread A: put("keyA", val) → locks bucket #42
// Thread B: put("keyB", val) → locks bucket #17  ← CONCURRENT
// Thread C: get("keyC")      → no lock           ← CONCURRENT
// All three proceed simultaneously!
```

**THE TRADE-OFFS:**

- **Gain:** Near-linear throughput scaling with thread count for independent-key operations.
- **Cost:** `size()` is approximate; iteration is weakly consistent (sees state during iteration, not a snapshot); no null keys/values; compound operations require `compute*` methods, not manual check-then-act.

---

### 🧪 Thought Experiment

**SETUP:**
A cache for translated strings: `Map<String, String> translations`. 50 threads simultaneously call `getOrCompute(key, () -> translate(key))` where `translate()` takes 100ms.

**WITHOUT computeIfAbsent:**

```java
// WRONG: classic race condition
String cached = map.get(key);
if (cached == null) {
    cached = translate(key); // 50 threads all reach here!
    map.put(key, cached);    // 50 translations happen!
}
return cached;
```

All 50 threads see `null`, all call `translate()` → 50 × 100ms = 5 seconds of redundant work.

**WITH ConcurrentHashMap.computeIfAbsent:**

```java
return translations.computeIfAbsent(key, k -> translate(k));
```

First thread entering `computeIfAbsent` for a key acquires the bucket lock. Other threads calling `computeIfAbsent` for the SAME key will wait. Other threads calling for DIFFERENT keys proceed immediately. Result: exactly 1 `translate()` call per key.

**THE INSIGHT:**
`computeIfAbsent` is not just convenience — it's the correct atomic primitive for cache population. The check-then-act pattern on `get/put` is inherently racy even with ConcurrentHashMap, because `get` and `put` are each individually atomic but not composed.

---

### 🧠 Mental Model / Analogy

> ConcurrentHashMap is a post office with 1024 numbered PO boxes arranged in a single large room. Collecting your mail (reading): just walk to your box and take it — no need to ask anyone. Putting mail in a box (writing): you briefly lock that specific box while you insert the letter. Other people can use any of the other 1023 boxes simultaneously. The whole post office doesn't shut down when someone locks box #42.

- "1024 PO boxes" → array of buckets
- "Collecting mail without asking" → lock-free volatile read
- "Briefly locking your specific box" → `synchronized(bucketHead)` on write
- "Other boxes unaffected" → lock striping = independent bucket locks
- "Post office expansion" → table resize with cooperative transfer

Where this analogy breaks down: in a real post office, resizing (adding more boxes) requires closing temporarily. ConcurrentHashMap resizes cooperatively — helping threads assist with the transfer while other operations continue on already-transferred buckets.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
ConcurrentHashMap is a thread-safe version of HashMap that multiple threads can use simultaneously without data corruption or needing to write synchronization code. Unlike a lock that blocks everyone, it lets different threads work on different entries at the same time.

**Level 2 — How to use it (junior developer):**
Use it exactly like a HashMap but in multi-threaded code. Prefer atomic methods: `putIfAbsent(key, value)` instead of `if (!map.containsKey(k)) map.put(k, v)`. Use `computeIfAbsent(key, k -> newValue(k))` for lazy initialization. Use `merge(key, 1, Integer::sum)` to increment counters atomically. Avoid iterating while modifying (weakly consistent iteration may or may not reflect concurrent modifications).

**Level 3 — How it works (mid-level engineer):**
Java 8 replaced the Java 5 `Segment` array design with a single array and per-bucket locking. Each bucket is either null (empty), a linked list (for short chains), or a red-black TreeNode (for chains > 8 elements — `TREEIFY_THRESHOLD`). Reads use `volatile` reads through the node chain — `Node.val` is `volatile`. Writes to non-empty buckets use `synchronized` on the first node (effectively per-bucket lock). The `LongAdder`-based `sumCount()` approximates size across stripe counters without global locking. Resize uses `ForwardingNode` markers: when a bucket is transferred to the new table, the slot is replaced with a `ForwardingNode` that redirects reads to the new table.

**Level 4 — Why it was designed this way (senior/staff):**
Java 8's redesign removed segments in favour of direct per-bucket locking, because segments added indirection without proportional benefit — CPU caches prefer contiguous array access over two-level indirection. The shift from `ReentrantLock` per segment to `synchronized` per bucket leverages JVM biased locking and lock coarsening optimisations in HotSpot. `computeIfAbsent` blocks the bucket during computation to prevent the thundering-herd problem, but this means a slow supplier can block all writers for that bucket — a design trade-off between correctness and potential contention. For high-contention single-key scenarios, prefer a custom `AtomicReference` with CAS retry loops.

---

### ⚙️ How It Works (Mechanism)

```
CONCURRENT PUT FLOW (Java 8):
┌─────────────────────────────────────────────────────────┐
│ put(key, value)                                         │
│                                                         │
│ 1. hash = spread(key.hashCode())                        │
│ 2. index = hash & (table.length - 1)                    │
│ 3. f = tabAt(table, index)  // volatile read            │
│                                                         │
│ Case A: f == null (empty bucket)                        │
│   → casTabAt(table, index, null, newNode)               │
│   → If CAS wins: done. If lost: loop to retry.          │
│                                                         │
│ Case B: f.hash == MOVED (-1) (resize in progress)       │
│   → helpTransfer(table, f)  // assist resize            │
│                                                         │
│ Case C: f is a real node (non-empty bucket)             │
│   → synchronized(f) {                                   │
│       walk chain/tree, insert/update                    │
│       if chain > 8: treeifyBin()                        │
│     }                                                   │
│   → addCount(1, binCount)  // update size estimate      │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (frequency counter):
Multiple threads call: map.merge(word, 1L, Long::sum)
→ Each call: compute bucket index from word's hash
→ [ConcurrentHashMap bucket lock ← YOU ARE HERE]
→ lock only bucket containing this word
→ atomic merge: read current count, add 1, write back
→ unlock bucket
→ All other buckets unaffected — full concurrency

FAILURE PATH:
computeIfAbsent with slow supplier blocks bucket:
→ Thread A calls computeIfAbsent("key", k -> slowDB.load(k))
→ Bucket locked during 500ms DB call
→ Thread B calls computeIfAbsent("key") → waits 500ms
→ Thread C calls put("key", x) → waits 500ms
→ Observable: threads blocked in computeIfAbsent
→ Fix: compute value BEFORE calling computeIfAbsent,
       use putIfAbsent with pre-computed value

WHAT CHANGES AT SCALE:
At extreme concurrency (1M+ ops/sec on same key), even
per-bucket locking becomes a bottleneck. Switch to
LongAdder/LongAccumulator for counters, or shard the
map with multiple CHMs and a consistent hash for key
routing.
```

---

### 💻 Code Example

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// Example 1 — WRONG: check-then-act race condition
// BAD (even with CHM, these two ops are not atomic)
if (!map.containsKey("user1")) {
    map.put("user1", 0);
}

// Example 1 — GOOD: atomic putIfAbsent
map.putIfAbsent("user1", 0); // atomic, no race

// Example 2 — WRONG: non-atomic counter increment
// BAD: get + compute + put is three operations = race
int count = map.getOrDefault("hits", 0);
map.put("hits", count + 1); // lost updates under concurrency

// Example 2 — GOOD: atomic merge for counter
map.merge("hits", 1, Integer::sum); // atomic increment

// Example 3 — WRONG: slow supplier inside computeIfAbsent
// BAD: blocks entire bucket for duration of DB call
Object val = map.computeIfAbsent(key, k -> slowDatabaseLoad(k));

// Example 3 — GOOD: precompute then putIfAbsent
Object computed = slowDatabaseLoad(key); // compute OUTSIDE lock
map.putIfAbsent(key, computed);          // fast atomic insert
// Note: may compute even if key already exists — trade off
// duplicate computation vs bucket hold time

// Example 4 — Word frequency counter (thread-safe)
ConcurrentHashMap<String, Long> freq = new ConcurrentHashMap<>();
// All threads can call concurrently:
words.parallelStream()
     .forEach(w -> freq.merge(w, 1L, Long::sum));

// Example 5 — ConcurrentHashMap as concurrent set
Set<String> set = ConcurrentHashMap.newKeySet();
// or: map.keySet(defaultValue) for a Set view
```

---

### ⚖️ Comparison Table

| Map                         | Thread Safe | Read Lock       | Write Lock | Null Keys   | Best For                        |
| --------------------------- | ----------- | --------------- | ---------- | ----------- | ------------------------------- |
| HashMap                     | No          | None            | None       | Yes         | Single-threaded use             |
| **ConcurrentHashMap**       | Yes         | None (volatile) | Per-bucket | No          | High-concurrency reads/writes   |
| Hashtable                   | Yes         | Global          | Global     | No          | Legacy code only                |
| Collections.synchronizedMap | Yes         | Global          | Global     | Via wrapper | Simple wrapping of existing map |
| CopyOnWriteArrayList        | Yes (list)  | None            | Full copy  | N/A         | Read-heavy, rare writes         |

**How to choose:** Use ConcurrentHashMap for any multi-threaded map in modern Java. Avoid Hashtable (legacy). Use `synchronizedMap` only when wrapping a pre-existing HashMap for simple code where performance doesn't matter. Use `CopyOnWriteArrayList` for lists (not maps) with very infrequent writes.

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                                                                                        |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ConcurrentHashMap is fully consistent for compound operations           | Individual operations (get, put) are atomic. Compound operations (get-then-put) are NOT atomic unless you use the provided atomic methods (computeIfAbsent, merge, etc.). Always use the atomic variants       |
| size() is accurate in concurrent code                                   | `size()` / `mappingCount()` returns an estimate under concurrent modification. For precise counting, maintain a separate `LongAdder` counter alongside the map                                                 |
| ConcurrentHashMap allows null values because HashMap does               | ConcurrentHashMap explicitly forbids null keys and values. The reason: null return from `get()` would be ambiguous — does it mean the key is absent, or the key maps to null? CHM uses null as "absent" signal |
| ConcurrentHashMap is safe to use without synchronized blocks everywhere | You still need atomic compound methods. `if (!map.containsKey(k)) map.put(k, v)` is a race condition with CHM. Use `putIfAbsent()` or `computeIfAbsent()` for correctness                                      |

---

### 🚨 Failure Modes & Diagnosis

**Lost Updates from Non-Atomic Compound Operations**

**Symptom:** Counter values are incorrect under load; concurrent tests pass intermittently; production shows lower-than-expected counts.

**Root Cause:** Using `map.put(k, map.get(k) + 1)` — a non-atomic read-modify-write sequence. Two threads read the same value, both increment, last writer wins.

**Diagnostic Command:**

```bash
# Add assertions in tests with concurrent access:
# Run with many threads and verify count == expected
# Use stress testing: jcstress (JVM Concurrency Stress Tests)
mvn dependency:get -Dartifact=org.openjdk.jcstress:jcstress-core:0.16
```

**Fix:**

```java
// BAD: non-atomic
map.put(key, map.getOrDefault(key, 0) + 1);

// GOOD: atomic merge
map.merge(key, 1, Integer::sum);
```

**Prevention:** Code review rule: no manual get+put in concurrent code with CHM. Always use atomic methods.

---

**computeIfAbsent Deadlock via Recursive Call**

**Symptom:** Application hangs; thread dump shows thread blocked in `ConcurrentHashMap.computeIfAbsent`, holding bucket lock.

**Root Cause:** The `computeIfAbsent` supplier recursively calls `computeIfAbsent` on the same map with the same key. The bucket lock is re-entrant via `synchronized`, but in Java 8, the same-key recursive call causes an infinite loop in some JVM versions.

**Diagnostic Command:**

```bash
jstack <pid> | grep -A 15 "computeIfAbsent"
```

**Fix:** Never call `computeIfAbsent` (on the same map) from within the supplier lambda. Use a pre-populated helper map or restructure the computation.

**Prevention:** Keep suppliers in `computeIfAbsent` simple and free of recursive map access.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HashMap` — understand hash table internals before concurrent variant
- `Thread Safety` — why shared mutable state needs coordination
- `Synchronized` — the primitive mechanism CHM uses internally per bucket

**Builds On This (learn these next):**

- `LongAdder` — high-performance concurrent counter; often pairs with CHM
- `CacheBuilder (Guava/Caffeine)` — higher-level caching built on CHM primitives
- `Lock Striping` — the general pattern CHM implements

**Alternatives / Comparisons:**

- `Hashtable` — same interface, global lock; deprecated by CHM
- `Collections.synchronizedMap` — same global-lock problem; use CHM instead
- `CopyOnWriteArrayList` — analogous for lists: read-heavy, write copies entire structure

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Thread-safe HashMap with lock-free reads  │
│              │ and per-bucket write locking              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shared maps need concurrent access        │
│ SOLVES       │ without global locking bottleneck         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Compound ops (check+put) still need       │
│              │ atomic methods: computeIfAbsent, merge    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple threads read/write shared map;   │
│              │ frequency counting; shared caches         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-threaded code (use HashMap);       │
│              │ need exact size() atomically              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Concurrent throughput vs weakly           │
│              │ consistent size() and iteration           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "1024 independently-locked drawers:       │
│              │  one person per drawer, unlimited readers"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LongAdder → Caffeine Cache → Lock Striping│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** ConcurrentHashMap's Java 8 redesign removed the Segment array from Java 5/6 and replaced it with per-bucket `synchronized` locks. The Segment design required a two-level indirection (array of segments → array of buckets), while the Java 8 design uses a single array with the first node as the lock object. Explain the exact CPU cache performance difference between these two designs, and why L1/L2 cache line effects make the Java 8 design faster for sequential-access patterns.

**Q2.** `computeIfAbsent` guarantees that the supplier is called at most once per key under concurrent access. However, there is a documented case in the JDK where calling `computeIfAbsent` on a `ConcurrentHashMap` with a supplier that recursively inserts into the same map can cause an infinite loop or deadlock. Identify the exact internal condition that causes this — is it a lock re-entrance issue, a structural modification issue, or something else — and describe the minimal code pattern that triggers it.
