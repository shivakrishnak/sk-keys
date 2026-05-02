---
layout: default
title: "Lock Striping"
parent: "Java Concurrency"
nav_order: 369
permalink: /java-concurrency/lock-striping/
number: "369"
category: Java Concurrency
difficulty: ★★★
depends_on: ReentrantLock, synchronized, ConcurrentHashMap, Race Condition, Java Memory Model (JMM)
used_by: ConcurrentHashMap, Actor Model
tags:
  - java
  - concurrency
  - advanced
  - pattern
  - deep-dive
---

# 369 — Lock Striping

`#java` `#concurrency` `#advanced` `#pattern` `#deep-dive`

⚡ TL;DR — A concurrency technique that replaces a single lock protecting a large collection with an array of independent locks, each covering a subset of the data, reducing contention proportionally.

| #369 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ReentrantLock, synchronized, ConcurrentHashMap, Race Condition, Java Memory Model (JMM) | |
| **Used by:** | ConcurrentHashMap, Actor Model | |

---

### 📘 Textbook Definition

**Lock Striping** is a lock granularity technique in which a single coarse-grained lock protecting a shared data structure is replaced by an array of locks (stripes), where each lock protects a disjoint partition of the data. A thread accesses data by first computing a lock index from the data item's key (commonly `key.hashCode() % stripeCount`), then acquiring only the lock for the relevant stripe. Contention is reduced by a factor proportional to the number of stripes, as concurrent operations on different stripes proceed in parallel. `java.util.concurrent.ConcurrentHashMap` in Java 8+ uses a form of lock striping via segment locks (Java 7) or intrinsic per-bucket locking (Java 8+).

### 🟢 Simple Definition (Easy)

Instead of one lock for an entire data structure (one queue for a bank), use many smaller locks, one per section — so different threads can work on different sections simultaneously.

### 🔵 Simple Definition (Elaborated)

Imagine a library with one librarian who handles all requests — everyone must wait for the single librarian. Lock striping is like having 16 librarians, one per section (A–B, C–D, ...). You only need to wait if someone else needs the SAME section. Requests for different sections proceed independently. In code: instead of `synchronized(this)` on an entire `HashMap`, you maintain an array of 16 `ReentrantLock`s and map each key to a lock index via `key.hashCode() & 15`. Two writes to different buckets use different locks and never block each other.

### 🔩 First Principles Explanation

**The problem with a single lock:**

```
Thread 1: put("alice", 100)  → acquires THE lock         → writes → releases
Thread 2: put("bob",   200)  → waits for THE lock ...      → writes
Thread 3: get("carol")       → waits for THE lock ...             → reads
```

All three operations are independent (different keys) but serialised by the single lock. Throughput is O(1/threads) — more threads = worse performance.

**Lock striping solution:**

```java
// Stripe count: power of 2 for efficient modulo via bitmasking
static final int STRIPE_COUNT = 16;
final Lock[] locks = new ReentrantLock[STRIPE_COUNT];
// initialise locks...
final Map<String, Integer>[] segments =
    new HashMap[STRIPE_COUNT];
// initialise segments...

int stripe(Object key) {
    return (key.hashCode() & 0x7fff_ffff) % STRIPE_COUNT;
    // or: key.hashCode() & (STRIPE_COUNT - 1) for power-of-2
}

void put(String key, Integer value) {
    int s = stripe(key);
    locks[s].lock();
    try {
        segments[s].put(key, value);
    } finally {
        locks[s].unlock();
    }
}
```

Now threads accessing different stripes proceed in parallel. Contention reduced by 16× vs. single lock.

**Optimal stripe count:**

- Too few stripes (1): same as single lock.
- Too many stripes: high memory overhead; operations needing data from all stripes (e.g., `size()`) must acquire all locks.
- Rule of thumb: start with 16–64 stripes; measure contention and scale up.

**ConcurrentHashMap evolution:**
- Java 5–7: 16 explicit `Segment` locks (heavyweight `ReentrantLock`).
- Java 8+: abandons Segment, uses intrinsic `synchronized` per-bucket head node — fine-grained striping where each bucket is its own stripe.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Lock Striping:

- High-concurrency workloads on a shared collection serialise all writes through one lock.
- 32-thread server on 32-core machine with single HashMap lock: effectively single-threaded.
- Adding CPUs doesn't improve throughput — more threads just queue on the lock.

What breaks without it:
1. Lock contention becomes the scalability ceiling, wasting available parallelism.
2. Response times under load grow linearly with concurrent thread count.

WITH Lock Striping:
→ Throughput scales nearly linearly with stripe count for independent key workloads.
→ `ConcurrentHashMap` achieves this automatically — used everywhere concurrent maps are needed.

### 🧠 Mental Model / Analogy

> Lock striping is like converting a single-lane toll booth into 16 parallel lanes. Everyone heading in the same lane still waits behind each other, but traffic to different lanes flows independently. The total capacity is 16× higher. The only bottleneck remains: counting the total number of vehicles on all lanes simultaneously (lock-all-stripes operation like `size()`).

"Single lane" = single lock, "16 lanes" = 16 lock stripes, "counting all vehicles" = acquiring all locks for count/clear, "lane assignment" = hash to stripe.

### ⚙️ How It Works (Mechanism)

**Stripe selection:**

```
key → hashCode → & (stripeCount - 1) → stripe index → lock

"alice".hashCode() = 92599395
92599395 & 15 (0xF) = 3  → locks[3]

"bob".hashCode() = 97299
97299 & 15 = 3            → locks[3]  ← same stripe, contention!

"carol".hashCode() = 94933690
94933690 & 15 = 10        → locks[10] ← different stripe, parallel!
```

**Operations requiring all stripes (global operations):**

```java
// size() — must sum all segments safely
int size() {
    // Acquire all locks to get consistent count
    for (int i = 0; i < STRIPE_COUNT; i++) locks[i].lock();
    try {
        int total = 0;
        for (Map<?,?> seg : segments) total += seg.size();
        return total;
    } finally {
        for (int i = 0; i < STRIPE_COUNT; i++) locks[i].unlock();
    }
}
// Note: ConcurrentHashMap uses a smarter lock-free approach for size()
```

**ConcurrentHashMap Java 8 per-bucket striping:**

```
Bucket 0: [lock on head node 0] → node chain
Bucket 1: [lock on head node 1] → node chain
...
Bucket N: [lock on head node N] → node chain

put() on key with hash=K:
  1. Compute bucket = K & (table.length - 1)
  2. CAS on empty bucket (lock-free for empty insert)
  3. Or synchronized(head_node) for existing bucket
→ Only the specific bucket is locked
→ All other buckets proceed concurrently
```

### 🔄 How It Connects (Mini-Map)

```
Single lock (coarse-grained, high contention)
           ↓ evolution
Lock Striping ← you are here
(N locks, N partitions, N× throughput)
           ↓ realised by
ConcurrentHashMap (per-bucket Java 8+)
           ↓ further evolved
Lock-Free Data Structures (CAS-based, no locks)
```

### 💻 Code Example

Example 1 — Custom striped map implementation:

```java
import java.util.concurrent.locks.ReentrantLock;
import java.util.*;

public class StripedMap<K, V> {
    private static final int STRIPE_COUNT = 16;
    private final Object[] locks;
    private final HashMap<K, V>[] buckets;

    @SuppressWarnings("unchecked")
    public StripedMap() {
        locks = new Object[STRIPE_COUNT];
        buckets = new HashMap[STRIPE_COUNT];
        for (int i = 0; i < STRIPE_COUNT; i++) {
            locks[i] = new Object(); // use as monitor
            buckets[i] = new HashMap<>();
        }
    }

    private int stripeFor(Object key) {
        // Spread bits for better distribution
        int h = key.hashCode();
        h = h ^ (h >>> 16); // spread
        return h & (STRIPE_COUNT - 1);
    }

    public V put(K key, V value) {
        int stripe = stripeFor(key);
        synchronized (locks[stripe]) {
            return buckets[stripe].put(key, value);
        }
    }

    public V get(Object key) {
        int stripe = stripeFor(key);
        synchronized (locks[stripe]) {
            return buckets[stripe].get(key);
        }
    }

    public int size() {
        // Lock all stripes for consistent global count
        for (Object lock : locks) {
            synchronized (lock) { /* acquire */ }
        }
        // Note: this demonstration omits deadlock-safe acquisition
        // In practice: acquire all in consistent order, release all
        int total = 0;
        for (HashMap<?, ?> b : buckets) total += b.size();
        return total;
    }
}
```

Example 2 — Using Guava's Striped for production:

```java
import com.google.common.util.concurrent.Striped;

// Guava Striped: ready-made lock striping abstraction
Striped<Lock> striped = Striped.lock(64); // 64 stripes

void updateUserBalance(long userId, int delta) {
    Lock lock = striped.get(userId); // hash-based stripe
    lock.lock();
    try {
        balanceMap.merge(userId, delta, Integer::sum);
    } finally {
        lock.unlock();
    }
}
```

Example 3 — Benchmarking single lock vs. striped:

```java
// At 32 threads, 1M ops each:
// Single lock:   ~800ms  (threads queue)
// 16-stripe:     ~60ms   (13× faster)
// 64-stripe:     ~20ms   (40× faster)
// ConcurrentHashMap: ~15ms (per-bucket)
// LockFree CMap:  ~12ms  (no locks at all)
// Best tool depends on write:read ratio and key distribution
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More stripes always means better performance | Beyond CPU count stripes, adding more stripes increases memory overhead and global operation cost without improving throughput. |
| Lock striping eliminates all contention | It reduces contention proportionally; keys that hash to the same stripe still contend. Poor hash distribution can make striping ineffective. |
| ConcurrentHashMap uses exactly 16 locks | Java 7 ConcurrentHashMap had 16 Segments. Java 8+ uses per-bucket synchronized blocks — effectively table.length stripes. |
| Lock striping is only for maps | Any partitionable data structure benefits: caches, user session stores, rate limiters, connection pools, etc. |
| Striped locks are hard to implement correctly | Libraries like Guava's Striped handle implementation details; use library abstractions rather than rolling your own in most cases. |

### 🔥 Pitfalls in Production

**1. Skewed Key Distribution — All Keys Land on Same Stripe**

```java
// BAD: Key is always the same entity type
// All user requests for user ID 1 hash to stripe 5
// → stripe 5 is hot, others are cold
// Lock striping provides zero benefit for hot-key workloads

// GOOD: Detect hot keys and apply separate strategy
// (local caching, request deduplication, or partitioning)
// Striping helps with uniformly distributed keys
```

**2. Deadlock When Acquiring Multiple Stripes**

```java
// BAD: Acquiring stripes in undefined order during transfer
void transfer(K from, K to, V value) {
    int s1 = stripeFor(from);
    int s2 = stripeFor(to);
    synchronized (locks[s1]) {
        synchronized (locks[s2]) {  // → deadlock risk!
            // Thread A: s1=3, s2=7
            // Thread B: s1=7, s2=3 → cycle
        }
    }
}

// GOOD: Always acquire in consistent order (by stripe index)
void transfer(K from, K to, V value) {
    int s1 = stripeFor(from);
    int s2 = stripeFor(to);
    int lo = Math.min(s1, s2);
    int hi = Math.max(s1, s2);
    synchronized (locks[lo]) {
        synchronized (locks[hi]) {
            // Safe: always lo before hi
        }
    }
}
```

**3. Stripe Count Not a Power of 2 — Slow Modulo**

```java
// BAD: Arbitrary stripe count requires expensive %
int stripe = Math.abs(key.hashCode()) % 17; // % 17 is slow

// GOOD: Power-of-2 allows cheap bitmasking
int stripe = key.hashCode() & (16 - 1); // & 15 = fast
```

### 🔗 Related Keywords

- `ConcurrentHashMap` — the canonical Java implementation of lock striping at per-bucket granularity.
- `ReentrantLock` — the lock type commonly used in striped implementations.
- `Deadlock Detection (Java)` — multi-lock acquisition during operations like `size()` creates deadlock risk if ordering isn't enforced.
- `Race Condition` — the problem lock striping solves by protecting per-stripe data.
- `Lock-Free Data Structures` — the next evolution beyond lock striping.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ N locks → N independent partitions →      │
│              │ N× throughput for independent key ops.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High-concurrency shared collections with  │
│              │ uniformly distributed keys; cache maps;   │
│              │ rate limiters per entity.                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Highly skewed key distribution (hot keys);│
│              │ frequent global ops (size, clear);        │
│              │ better to use ConcurrentHashMap directly. │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Lock striping: divide the crowd into     │
│              │ lanes so each lane flows freely."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ConcurrentHashMap → Lock-Free DS → VarHandle│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A session store backed by a `StripedMap` with 64 stripes handles 10,000 concurrent requests per second. Monitoring shows 3 of the 64 stripes handle 70% of all traffic because session IDs are assigned sequentially rather than randomly. Calculate the effective parallelism multiplier this striping provides compared to a single lock, and propose two architectural changes — one at the application level and one at the striping level — to restore balanced stripe utilisation.

**Q2.** `ConcurrentHashMap.size()` in Java 8+ does NOT acquire all bucket locks; instead it returns an approximate count maintained via atomic `LongAdder`-like cells. Explain why an exact lock-all-stripes `size()` would be problematic for concurrent performance, what correctness trade-off the approximate approach makes, and describe a scenario where the approximate `size()` returning a stale value could cause a correctness bug in application code.

