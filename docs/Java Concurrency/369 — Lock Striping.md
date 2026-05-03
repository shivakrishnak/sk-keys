---
layout: default
title: "Lock Striping"
parent: "Java Concurrency"
nav_order: 369
permalink: /java-concurrency/lock-striping/
number: "0369"
category: Java Concurrency
difficulty: ★★★
depends_on: ReentrantLock, synchronized, ConcurrentHashMap, Hash Table
used_by: ConcurrentHashMap, High-Throughput Caches, Parallel Data Structures
related: ConcurrentHashMap, ReentrantLock, Deadlock Detection, ReadWriteLock
tags:
  - concurrency
  - java
  - lock-striping
  - performance
  - advanced
  - data-structures
---

# 369 — Lock Striping

⚡ TL;DR — Lock striping divides a single global lock into N independent "stripe" locks, each protecting a subset of data, reducing contention proportionally to N by allowing threads accessing different stripes to proceed in parallel.

| #0369           | Category: Java Concurrency                                          | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | ReentrantLock, synchronized, ConcurrentHashMap, Hash Table          |                 |
| **Used by:**    | ConcurrentHashMap, High-Throughput Caches, Parallel Data Structures |                 |
| **Related:**    | ConcurrentHashMap, ReentrantLock, Deadlock Detection, ReadWriteLock |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have a `HashMap<String, Object>` accessed by 100 concurrent threads. You wrap it with `Collections.synchronizedMap()` — which adds a single `synchronized` lock around all operations. Every `get`, `put`, `remove` acquires the same lock. Only one thread can operate at a time. Your throughput is limited to a single thread's speed regardless of how many cores you have. CPU utilisation: 1 of 16 cores. Throughput: terrible.

**THE BREAKING POINT:**
A single global lock serialises all threads, even those accessing completely independent data. Two threads writing to key "alice" and "bob" respectively have no logical conflict — they operate on different buckets. But a global lock forces them to take turns. This is false sharing at the lock level.

**THE INVENTION MOMENT:**
Lock striping asks: "Do all threads REALLY need the same lock?" If the data can be partitioned into N independent segments, each with its own lock, then N threads can work in parallel with zero contention. `ConcurrentHashMap` before Java 8 used exactly 16 stripes (configurable as `concurrencyLevel`). Modern `ConcurrentHashMap` (Java 8+) goes further — lock per bucket — but the conceptual foundation is lock striping.

---

### 📘 Textbook Definition

**Lock Striping** is a concurrency pattern that replaces a single global lock with an array of N locks (stripes), where each lock protects a fixed partition of the data set. An operation on data item K acquires `locks[hash(K) % N]` — a deterministic lock based on K's hash, not a single global lock. Lock granularity: coarser than per-entry locks (lower memory overhead), finer than a single lock (lower contention). Classic example: `ConcurrentHashMap` (Java 5–7) used 16 stripes by default — up to 16 concurrent writes possible. Trade-offs: N stripes allow N-way parallel write throughput; N > number-of-CPUs provides no additional benefit; compound operations spanning multiple stripes require multi-lock acquisition (care needed to avoid deadlock via lock ordering).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Lock striping replaces one global lock with N locks, one per partition of the data, so threads touching different partitions never block each other.

**One analogy:**

> Lock striping is like replacing a single-cashier checkout lane (one global lock) with 16 self-checkout kiosks (16 stripe locks). Each customer (thread) goes to the kiosk for their item (hash to a stripe). Customers at different kiosks work simultaneously with no waiting. If two customers happen to both need kiosk #3 (same stripe), they wait — but that's rare and brief. Overall throughput is up to 16× better than the single cashier.

**One insight:**
The core insight is that lock scope and lock granularity should match data access patterns. When data can be partitioned (hash map buckets, account IDs modulo N, etc.), locks can be partitioned too. Contention drops from "one thread at a time" to "one thread per stripe at a time."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. N stripe locks replace 1 global lock.
2. Data item K is always assigned to stripe `hash(K) % N` — deterministic.
3. Threads accessing different stripes run in parallel.
4. Threads accessing the same stripe wait for each other (same as global lock for that stripe).
5. N = number of stripes; optimal N ≈ number of CPU cores × 2–4.

**DERIVED DESIGN:**

```java
// LOCK STRIPING IMPLEMENTATION — Core Pattern
public class StripedMap<K, V> {
    private static final int STRIPES = 16;

    // The data: hash buckets
    @SuppressWarnings("unchecked")
    private final LinkedList<Map.Entry<K, V>>[] buckets =
        new LinkedList[STRIPES];

    // The stripe locks — one per partition
    private final Object[] locks = new Object[STRIPES];

    public StripedMap() {
        for (int i = 0; i < STRIPES; i++) {
            buckets[i] = new LinkedList<>();
            locks[i] = new Object();       // each stripe: own lock
        }
    }

    // Map key to stripe index — consistent hashing
    private int stripeFor(K key) {
        return Math.abs(key.hashCode() % STRIPES);
    }

    public V get(K key) {
        int stripe = stripeFor(key);
        synchronized (locks[stripe]) {     // only this stripe locked
            for (Map.Entry<K, V> e : buckets[stripe])
                if (e.getKey().equals(key)) return e.getValue();
            return null;
        }
    }

    public void put(K key, V value) {
        int stripe = stripeFor(key);
        synchronized (locks[stripe]) {
            // Remove existing, then add
            buckets[stripe].removeIf(e -> e.getKey().equals(key));
            buckets[stripe].add(Map.entry(key, value));
        }
    }

    // COMPOUND OPERATION spanning multiple stripes:
    // Requires acquiring BOTH stripe locks — use consistent ordering!
    public void move(K fromKey, K toKey) {
        int s1 = stripeFor(fromKey);
        int s2 = stripeFor(toKey);
        // Always acquire lower-index stripe first (prevent deadlock)
        Object firstLock  = s1 <= s2 ? locks[s1] : locks[s2];
        Object secondLock = s1 <= s2 ? locks[s2] : locks[s1];
        synchronized (firstLock) {
            synchronized (secondLock) {
                V val = remove(fromKey);   // internal, already locked
                put(toKey, val);
            }
        }
    }
}
```

```
THROUGHPUT COMPARISON:
Single global lock (synchronized map):
  Thread 1 ──get("a")──► LOCK ──get──► UNLOCK
  Thread 2 ──get("b")──► WAIT ──────────────────► LOCK ──get──► UNLOCK
  Thread 3 ──put("c")──► WAIT ─────────────────────────────────► ...
  Parallelism: 1

16-stripe lock:
  Thread 1 ──get("a")──► LOCK[stripe 3] ──get──► UNLOCK[3]
  Thread 2 ──get("b")──► LOCK[stripe 11]──get──► UNLOCK[11]   (parallel!)
  Thread 3 ──put("c")──► LOCK[stripe 7] ──put──► UNLOCK[7]    (parallel!)
  Parallelism: up to 16
```

---

### 🧪 Thought Experiment

**SETUP:**
You're building a high-throughput user session cache: `Map<String, Session>` with 100 concurrent threads doing 80% reads and 20% writes. Session IDs are random UUIDs.

**WITH single lock:**
All 100 threads contend on a single lock. Even reads (which should be parallelisable) serialise. Throughput: ~1 operation per lock acquisition cycle.

**WITH 64 stripes:**
Each stripe covers ~1/64 of the session ID hash space. With random UUIDs, thread distribution across stripes is near-uniform. Expected concurrent threads per stripe: 100/64 ≈ 1.5. In practice: most stripes have 0–2 threads simultaneously. Contention is rare. Throughput: approaches linear scaling with cores.

**WHAT CHANGES WITH N:**

- N=1: equivalent to single global lock
- N=16: 16× theoretical parallelism (often enough for most workloads)
- N=128: diminishing returns — overhead of 128 lock objects, most idle
- N=number of entries: per-entry locking (maximum parallelism, maximum memory)

**THE INSIGHT:**
Optimal N is the concurrency level — the expected number of threads simultaneously accessing the map. ConcurrentHashMap's Java 5–7 default of 16 was chosen as a reasonable estimate for server thread counts.

---

### 🧠 Mental Model / Analogy

> Lock striping is like a library with 16 reading rooms instead of one. Each reading room has its own librarian (stripe lock). Books are assigned to rooms by their first letter (hash). Readers for A–B go to room 1, C–D to room 2, etc. Sixteen simultaneous readers across different rooms = sixteen parallel reading sessions with no waiting. Two readers who both want a C–D book must wait for each other at room 2's desk — but only them, not everyone else.

- "One librarian" → global lock (synchronized map)
- "16 librarians" → 16 stripe locks
- "Book-to-room assignment" → `hash(key) % stripes`
- "Two readers at same desk" → threads in same stripe waiting for each other
- "Readers in different rooms" → threads in different stripes proceed in parallel

Where this analogy breaks down: unlike rooms, stripes don't have a fixed number of books — the number of keys in each stripe varies with the actual key distribution. With pathological hash functions, all keys could end up in one stripe, defeating striping entirely.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Lock striping is like going from one checkout lane to 16 checkout lanes at a supermarket. Instead of all customers waiting for one cashier, they spread across 16. Most of the time, customers don't interfere with each other. Throughput goes up dramatically.

**Level 2 — How to use it (junior developer):**
Use `ConcurrentHashMap` (Java's built-in striped map). For custom striping: create `Lock[] stripes = new ReentrantLock[N]`. For key K: `int s = Math.abs(k.hashCode() % N)`. Always acquire `stripes[s]` before accessing data for K. For multi-key operations: acquire stripes in ascending index order to prevent deadlock.

**Level 3 — How it works (mid-level engineer):**
`ConcurrentHashMap` in Java 5–7 used an inner `Segment` class extending `ReentrantLock`. Each `Segment` was a mini-hash table with its own lock. The number of segments = `concurrencyLevel` (default 16). `put(key, value)` hashes the key to a segment, acquires that segment's lock, writes into the segment's bucket. Java 8+ replaced segments with CAS-based per-bucket locks (using `synchronized` on individual node objects), eliminating the fixed segment count and lock overhead when a bucket is uncontended.

**Level 4 — Why it was designed this way (senior/staff):**
Java 5–7 `ConcurrentHashMap`'s segment design was a carefully engineered trade-off: 16 segments as the default balanced memory overhead (16 `Segment` objects with their locks), concurrency (16-way parallelism), and implementation simplicity. The `concurrencyLevel` parameter was an admission that the optimal stripe count depends on the application's thread pool size — the library couldn't know this at compile time. Java 8's move to per-bucket CAS eliminated the contention ceiling entirely (no fixed stripe count) and removed the Segment overhead. The Segment design is now a historical example of lock striping in the JDK, superseded by a finer-grained lock-free approach.

---

### ⚙️ How It Works (Mechanism)

```
JAVA 7 ConcurrentHashMap (Segment-based striping):
  16 Segment objects, each extending ReentrantLock
  Each Segment: its own internal hash table

  put("alice", value):
  1. hash("alice") = 0x3A42F...
  2. segment index = top bits of hash % 16 = 7
  3. Segment[7].lock()                   ← only segment 7 locked
  4. Segment[7].put("alice", value)      ← write into segment 7
  5. Segment[7].unlock()

  put("bob", value):                     ← concurrent, hash → segment 3
  1. Segment[3].lock()                   ← different segment
  2. Segment[3].put("bob", value)        ← parallel with step 4 above!
  3. Segment[3].unlock()

JAVA 8 ConcurrentHashMap (per-bucket CAS + synchronized):
  No Segment class — array of Node objects

  put("alice", value):
  1. Compute bucket = hash % tableSize
  2. If bucket empty: CAS to insert first node (no lock needed)
  3. If bucket non-empty: synchronized(bucket.headNode) { insert }

  Parallelism: only threads writing to SAME bucket contend.
  Threads writing to different buckets = zero contention.
  Theoretical max parallelism: tableSize (can be millions)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (ConcurrentHashMap.put):
Thread 1: put("alice", v1) → hash to stripe/bucket 3
Thread 2: put("bob", v2)   → hash to stripe/bucket 11
Thread 3: get("alice")     → hash to stripe/bucket 3

Thread 1 acquires lock on bucket 3
Thread 2 acquires lock on bucket 11 — PARALLEL (no conflict)
Thread 3 waits for lock on bucket 3 — Thread 1 holds it
[Lock Striping ← YOU ARE HERE]
Thread 1 completes put, releases bucket 3 lock
Thread 3 acquires bucket 3, completes get
Threads 1, 2, 3 all finish — two ran in parallel

FAILURE PATH (same stripe collision):
All keys hash to stripe 0 (bad hash function / hash bias)
→ All threads contend on stripe[0] only
→ Striping provides no benefit
→ Observe: high contention on one stripe in profiler
→ Fix: better hash function, increase stripe count, or
       rekey data differently

WHAT CHANGES AT SCALE:
Lock striping scales to N stripes = N CPU cores worth of
parallelism. Beyond that, per-entry locking (Java 8 CHM style)
or lock-free CAS is needed. At extreme scale (millions of
concurrent operations), striping overhead — 16 lock objects —
is negligible; the benefit (reduced contention) dominates.
```

---

### 💻 Code Example

```java
// Guava's Striped<Lock> — production-ready striping utility

import com.google.common.util.concurrent.Striped;

// Create 64-stripe lock bank
Striped<Lock> striped = Striped.lock(64);

// Operation on key "alice":
Lock lock = striped.get("alice");   // hash("alice") → stripe N
lock.lock();
try {
    // Work on alice's data — only alice's stripe locked
    cache.put("alice", computeValue("alice"));
} finally {
    lock.unlock();
}

// Multi-key operation (e.g., transfer between two accounts):
Iterable<Lock> locks = striped.bulkGet(
    Arrays.asList("alice", "bob") // returns locks in consistent order
);
Streams.stream(locks).forEach(Lock::lock);
try {
    transfer("alice", "bob", amount);
} finally {
    Streams.stream(locks).forEach(Lock::unlock);
}
// Note: Striped.bulkGet() always returns locks in consistent
// (sorted) order — prevents deadlock automatically

// Manual implementation for custom data:
int STRIPES = 32;
ReentrantLock[] stripes = new ReentrantLock[STRIPES];
for (int i = 0; i < STRIPES; i++)
    stripes[i] = new ReentrantLock();

int stripeFor(Object key) {
    return Math.abs(key.hashCode() % STRIPES);
}

void update(String key, Object value) {
    int s = stripeFor(key);
    stripes[s].lock();
    try { dataMap.put(key, value); }
    finally { stripes[s].unlock(); }
}
```

---

### ⚖️ Comparison Table

| Strategy                    | Concurrency           | Memory | Complexity | Best For                              |
| --------------------------- | --------------------- | ------ | ---------- | ------------------------------------- |
| Global lock (synchronized)  | 1 thread              | O(1)   | Trivial    | Low-contention, correctness priority  |
| ReadWriteLock               | Readers in parallel   | O(1)   | Low        | Read-heavy, rare writes               |
| **Lock Striping (N locks)** | N threads             | O(N)   | Medium     | Balanced read/write, keyed data       |
| Per-entry locking           | M threads (M=entries) | O(M)   | High       | Very high concurrency, many keys      |
| Lock-free (CAS)             | Unlimited (CAS)       | O(M)   | Very High  | Maximum throughput, simple operations |

**How to choose:** Use `ConcurrentHashMap` (built-in striping) instead of rolling your own. For custom keyed data structures: use Guava's `Striped<Lock>`. Set stripe count ≈ 4× expected concurrent thread count.

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                               |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More stripes always means more throughput     | Diminishing returns apply: more stripes than CPUs provides no additional real parallelism. Excessive stripes waste memory. Optimal is ~2–4× CPU count                                 |
| Lock striping is only useful for hash maps    | Any data structure with independent partitions can be striped: arrays (stripe by index range), files (stripe by byte range), account ledgers (stripe by account ID % N)               |
| ConcurrentHashMap uses lock striping today    | Java 8+ `ConcurrentHashMap` does NOT use traditional lock striping. It uses CAS for empty buckets and `synchronized` on the head node of each bucket — effectively per-bucket locking |
| Striped locks prevent deadlocks automatically | Striped locks can deadlock if multi-stripe operations acquire locks in inconsistent order. Always use `bulkGet()` (Guava) or sort stripe indices before acquiring multiple stripes    |

---

### 🚨 Failure Modes & Diagnosis

**Hash Skew — All Keys Hit One Stripe**

**Symptom:** High contention on one stripe lock; threads mostly blocked even with 16 stripes; similar throughput to global lock.

**Root Cause:** Poor `hashCode()` implementation — many keys produce same hash modulo N. E.g., all integer keys divisible by 16 hash to stripe 0.

**Diagnostic Command:**

```java
// Diagnose hash distribution:
Map<Integer, Long> stripeHistogram = keys.stream()
    .collect(Collectors.groupingBy(
        k -> Math.abs(k.hashCode() % STRIPES),
        Collectors.counting()
    ));
// If any stripe has >> (totalKeys / STRIPES), hash skew present

// In production: use async-profiler to identify hot lock objects:
// async-profiler -e lock -d 30 -f profile.html <pid>
```

**Fix:** Override `hashCode()` to distribute uniformly. Use power-of-two stripe counts with hash spreading (ConcurrentHashMap applies a secondary hash spread).

**Prevention:** When designing stripe count: use power-of-two N. Use `Integer.reverse(key.hashCode())` for better spread. Benchmark distribution before deploying.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `synchronized` — the intrinsic lock mechanism that stripes replace
- `ReentrantLock` — the explicit lock type commonly used in stripe arrays
- `Hash Table` — lock striping assumes hash-based partitioning of data

**Builds On This (learn these next):**

- `ConcurrentHashMap` — Java's most-used striped (Java 5–7) then per-bucket-locked (Java 8+) map
- `Deadlock Detection (Java)` — multi-stripe operations require careful lock ordering to avoid deadlock

**Alternatives / Comparisons:**

- `ReadWriteLock` — parallelises reads but not writes; better when reads >> writes
- `Lock-free (CAS/Atomic)` — eliminates locks entirely at cost of CAS loop complexity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Array of N locks replacing 1 global lock; │
│              │ key K → lock[hash(K) % N]                 │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single global lock serialises all threads │
│ SOLVES       │ even for logically independent operations  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Threads touching different stripes run     │
│              │ in parallel with zero contention          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Keyed data with high concurrent access;   │
│              │ need more than ReadWriteLock can offer    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data has no natural partition key;        │
│              │ single-threaded or low-concurrency code   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ N× parallelism vs O(N) lock memory and    │
│              │ multi-stripe deadlock risk                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "16 checkout lanes instead of 1 —         │
│              │  customers spread out, rarely collide"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ConcurrentHashMap → Deadlock Detection →  │
│              │ Lock-Free (CAS)                           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Lock striping improves parallelism by a factor of N (number of stripes). But there's a compound operation problem: if you need to atomically move an entry from key `A` (stripe 3) to key `B` (stripe 7), you must hold both stripe 3 and stripe 7 locks simultaneously. Describe the deadlock risk, the standard prevention technique, and why Guava's `Striped.bulkGet()` solves this — specifically what sorting guarantee `bulkGet()` provides and why that breaks the deadlock cycle.

**Q2.** Java 8's `ConcurrentHashMap` uses CAS for empty buckets and `synchronized(head_node)` for non-empty buckets — not a fixed stripe array. Compare this design to classic 16-stripe lock striping in terms of: (a) maximum concurrent writers supported, (b) memory overhead per entry, (c) fairness under high contention, and (d) behavior when the table is rehashed (resized). Which scenario makes classic striping preferable over Java 8's approach?
