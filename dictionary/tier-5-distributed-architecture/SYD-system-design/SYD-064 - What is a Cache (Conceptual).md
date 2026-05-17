---
id: SYD-064
title: What is a Cache (Conceptual)
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: ""
used_by: SYD-031, SYD-052, SYD-069
related: SYD-031, SYD-052, SYD-069, SYD-063
tags:
  - fundamentals
  - caching
  - conceptual
  - design
  - beginner
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 64
permalink: /syd/what-is-a-cache/
---

# SYD-064 - What is a Cache (Conceptual)

⚡ TL;DR - A cache is a fast, temporary storage layer
that saves copies of frequently-accessed data so future
requests can be served faster without going back to
the original (slower) source. The key trade-off: speed
vs. freshness. Cached data may be stale (outdated).
The central questions: what to cache, for how long (TTL),
and what to do when the cache is full (eviction policy).
Three hit rate targets: anything below 80% hit rate is
usually a caching problem worth investigating; 95%+ is
typical for well-designed caches.

| #064 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | (none - foundational concept) | |
| **Related:** | Caching (System Design), Distributed Cache Design, Cache Invalidation Strategies, What is Scalability | |

---

### 🔥 The Problem This Solves

An e-commerce site queries a product's details
(name, price, description, images) on every page view.
That product has 100,000 page views per day. Each query
hits the database: ~10ms. 100,000 × 10ms = 1,000 seconds
of database CPU time per day on a static query.
The product data changes once per week. Without caching:
the database re-computes the same answer 100,000 times.
With caching: compute once, store in Redis, serve 100K
requests from cache in < 1ms each.

---

### 📘 Textbook Definition

**Cache:** A high-speed storage layer that stores
copies of frequently-accessed data in a location
that is faster to access than the original source.
The "original source" is typically a database, an
API, or a computed result.

**Cache hit:** The requested data is found in the cache.
Served from cache (fast, no trip to the original source).

**Cache miss:** The requested data is NOT in the cache.
Must fetch from the original source (slow), then
optionally store in the cache for future requests.

**TTL (Time To Live):** The duration for which a cached
entry is considered valid. After TTL expires, the next
request results in a cache miss and the data is re-fetched.

**Eviction policy:** The rule for which cache entry to
remove when the cache is full and a new entry must be
stored. Common policies: LRU (Least Recently Used),
LFU (Least Frequently Used), FIFO, Random.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store expensive-to-compute results close to where they
are needed. Serve from cache when available; compute
only on miss.

**One analogy:**
> A cheat sheet in an exam:
> Without cheat sheet: look up every formula in your
> textbook (slow, expensive).
> With cheat sheet: the 5 most-used formulas are right
> in front of you (fast, free to access).
> Trade-off: the cheat sheet might not have the formula
> you need (cache miss). And if you memorized the wrong
> formula (stale cache), you get the wrong answer.

**One insight:**
The benefit of caching comes from locality of reference:
real workloads follow the Pareto principle (80/20 rule).
20% of data items account for 80% of requests. Caching
that 20% of "hot" items can reduce database load by 80%.
This is why a small cache (10% of total data) can produce
a 90%+ hit rate for typical workloads.

---

### 🔩 First Principles Explanation

**WHERE CACHES LIVE (CACHE LAYERS):**
```
Every system has multiple cache layers:

1. CPU L1/L2/L3 cache:
   Nanoseconds. Tiny (MB). CPU automatically managed.
   
2. Application memory (in-process cache):
   Microseconds. MB to GB.
   data stored in application memory (HashMap).
   
3. Distributed cache (Redis, Memcached):
   Sub-millisecond. GB to TB.
   Shared across all application instances.
   
4. Database cache (query cache, page cache):
   OS page cache automatically caches hot DB pages.
   
5. CDN (Content Delivery Network):
   10s of milliseconds globally.
   Caches static assets and API responses near users.
   
Each layer: faster than the one below it.
The goal: serve as many requests as possible from
the highest (fastest) layer.
```

**CACHE-ASIDE (LAZY LOADING - most common):**
```
Application code manages the cache explicitly.

def get_product(product_id):
    # 1. Check cache
    cached = redis.get(f"product:{product_id}")
    if cached:
        return deserialize(cached)  # Cache HIT
    
    # 2. Cache MISS: fetch from database
    product = db.query(
        "SELECT * FROM products WHERE id = ?",
        [product_id])
    
    # 3. Store in cache for future requests
    redis.setex(
        f"product:{product_id}",
        3600,  # TTL: 1 hour
        serialize(product))
    
    return product

Pros: simple, flexible, only caches what is actually needed.
Cons: first request for each item = cache miss (slow).
      On cache restart: all requests miss until cache warms.
      ("cold start problem")
```

**WRITE-THROUGH (EAGER LOADING):**
```
Every write to the DB also writes to the cache.

def update_product(product_id, new_price):
    # 1. Write to database
    db.execute(
        "UPDATE products SET price = ? WHERE id = ?",
        [new_price, product_id])
    
    # 2. Update cache immediately
    product = {"id": product_id, "price": new_price}
    redis.setex(f"product:{product_id}",
                 3600, serialize(product))

Pros: cache is always fresh. No cold start on reads.
Cons: write latency increased (two operations).
      Cache may contain data never read (wasted memory).
```

**EVICTION POLICIES:**
```
LRU (Least Recently Used): evict item not accessed
  for the longest time. Good for temporal locality.
  Example: 1GB cache, 2GB of hot data accessed.
  LRU evicts items not seen recently; keeps recent
  items. Works well for most access patterns.

LFU (Least Frequently Used): evict item accessed
  fewest times. Better for stable "popularity" patterns.
  Example: product catalog - popular items always accessed
  more than obscure items. LFU keeps popular items.

FIFO: evict oldest-added item.
  Simple but ignores access patterns.
  Often suboptimal.

Random: evict random item.
  Surprisingly competitive with LRU in some workloads.
  Very simple to implement.

Default recommendation: LRU (Redis default with maxmemory-policy=allkeys-lru).
```

---

### 🧪 Thought Experiment

**CACHE HIT RATE AND ITS IMPACT**

User profile read: 20ms from database, 1ms from cache.
Traffic: 1,000 reads/second.

At 0% hit rate (no caching):
  All 1,000 reads hit database.
  DB load: 1,000 queries/sec.
  Average latency: 20ms.

At 80% hit rate:
  200 reads miss (hit DB). 800 reads hit cache.
  DB load: 200 queries/sec (80% reduction).
  Average latency: 0.8 × 1ms + 0.2 × 20ms = 4.8ms.

At 95% hit rate:
  50 reads miss. 950 reads hit cache.
  DB load: 50 queries/sec.
  Average latency: 0.95 × 1ms + 0.05 × 20ms = 1.95ms.

At 99% hit rate:
  10 reads miss. 990 reads hit cache.
  DB load: 10 queries/sec.
  Average latency: 0.99 × 1ms + 0.01 × 20ms = 1.19ms.

The "cache hit rate cliff": below 90% hit rate, the
database still sees significant load and latency stays
relatively high. Above 95%, database load becomes
negligible. This is why 95%+ hit rate is the target
for effective caching.

---

### 🧠 Mental Model / Analogy

> A cache is like a browser's bookmarks:
>
> Without bookmarks: type the full URL every time (slow,
> must look it up in your memory or history).
> With bookmarks: click on a bookmark (fast, direct).
>
> The bookmark might be wrong if the URL changed
> (stale cache). If you have 1,000 bookmarks but
> only 10 browser tabs (limited cache size), you need
> to manage which ones to keep (eviction).
>
> TTL = "check if this bookmark is still valid
>         every N days"

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A cache stores answers to common questions so you do not
have to look them up every time. Like remembering your
friend's phone number instead of looking it up each call.
The risk: if the number changes, your memory is wrong.

**Level 2 - How to use it (junior developer):**
Use Redis as a cache. Store key-value pairs with a TTL.
Check cache before database. On miss: fetch from DB,
store in cache, return result. Use appropriate TTL
(short for data that changes often, long for static data).

**Level 3 - How it works (mid-level engineer):**
Measure cache hit rate (aim for 95%+). Choose eviction
policy (LRU for most cases). Design cache keys carefully
(product:123, not just 123 - namespacing). Handle cache
stampede (thundering herd on cache miss for popular keys).
Handle cold start (cache is empty after a restart). Plan
cache invalidation strategy (when data changes: update
or invalidate the cache).

**Level 4 - Why it was designed this way (senior/staff):**
Redis is most commonly used as a distributed cache because
its architecture (single-threaded event loop, in-memory data
structures, rich data types) makes it ideal for sub-millisecond
read/write. The single-threaded model avoids lock contention
while the in-memory design provides consistent low latency.
The cache is not just for performance; it is also a resilience
tool: if the database goes down briefly, the cache can
continue serving requests from memory. Designing cache
invalidation correctly is harder than it appears (Phil
Karlton: "There are only two hard things in Computer
Science: cache invalidation and naming things"). Stale
data in production can cause subtle, hard-to-debug bugs.

**Level 5 - Mastery (distinguished engineer):**
Facebook's Memcache paper (2013) describes caching at
true hyperscale: 10+ trillion cache operations per day,
5B+ keys, across thousands of servers. Key insights:
(1) "Lease" mechanism to prevent thundering herd: when a
key is evicted, only one client gets a "lease" to fetch
the value from the database and populate the cache; others
wait. (2) Regional pools: different cache pools for
different consistency requirements (some data can be very
stale; some must be fresh). (3) Cache as a coordination
mechanism: the cache is not just for performance; it is
also used to implement distributed locking and notification
between services. At Facebook's scale, a 1% decrease in
hit rate means millions more DB queries per second - more
than any database farm can handle.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CACHE-ASIDE FLOW                                    │
│                                                      │
│ Client → GET /products/123                         │
│                 │                                   │
│                 ▼                                   │
│          Check Redis                               │
│         key: product:123                           │
│                 │                                   │
│         HIT ───┤─── MISS                           │
│          │         │                               │
│          │         ▼                               │
│          │    Query Database:                      │
│          │    SELECT * FROM products               │
│          │    WHERE id = 123                       │
│          │         │                               │
│          │         ▼                               │
│          │    SET product:123 EX 3600              │
│          │    (store in cache, TTL 1 hour)         │
│          │         │                               │
│          └─────────┘                               │
│                 │                                   │
│                 ▼                                   │
│          Return to Client                          │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Cache-aside with stampede protection**
```python
import redis
import json
import time

r = redis.Redis()
LOCK_TTL = 10  # seconds

def get_product(product_id: int) -> dict:
    """
    Cache-aside with stampede protection.
    Only one request populates the cache on miss.
    """
    cache_key = f"product:{product_id}"
    lock_key = f"lock:product:{product_id}"

    # Try cache first
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss: acquire lock to prevent stampede
    # SET NX (only set if not exists): atomic acquisition
    acquired = r.set(lock_key, "1",
                      ex=LOCK_TTL, nx=True)

    if acquired:
        try:
            # Re-check cache (another request may have
            # populated it while we were acquiring lock)
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)

            # Fetch from database
            product = db_get_product(product_id)

            # Store in cache
            r.setex(cache_key, 3600,
                     json.dumps(product))
            return product
        finally:
            r.delete(lock_key)
    else:
        # Another request holds the lock.
        # Wait briefly and retry from cache.
        time.sleep(0.05)  # 50ms wait
        cached = r.get(cache_key)
        if cached:
            return json.loads(cached)
        # Fallback: go to DB directly
        return db_get_product(product_id)


def invalidate_product(product_id: int):
    """Call this when product data changes."""
    r.delete(f"product:{product_id}")
```

**Example 2 - No caching (BAD for read-heavy data)**
```python
# BAD: reads from DB on every request
# 100K daily reads × 10ms = wasteful for static data
def get_product_bad(product_id: int) -> dict:
    # Every call hits the database
    # No caching - product data changes once per week
    # 100K requests per day × 10ms each = 1,000 CPU-sec
    return db.query(
        "SELECT * FROM products WHERE id = ?",
        [product_id])

# GOOD: 95%+ of reads served from cache
# Database only queried on miss or TTL expiry
# Cache TTL = 3600s (1 hour) - acceptable freshness
# for data that changes weekly
```

---

### ⚖️ Comparison Table

| Aspect | No Cache | In-Process Cache | Redis Cache | CDN Cache |
|---|---|---|---|---|
| **Speed** | DB latency (10ms) | Nanoseconds-microseconds | Sub-millisecond | Tens of ms (edge) |
| **Consistency** | Strong (always fresh) | Eventual | Eventual | Eventual |
| **Shared across servers** | N/A | No (per-instance) | Yes | Yes (globally) |
| **Max size** | DB size | Instance memory | TB | Unlimited |
| **Best for** | Low traffic, critical data | Hot data, single instance | Shared hot data | Static assets, public APIs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A longer TTL means better performance | Longer TTL means more cache hits (better performance) BUT higher chance of serving stale data. The right TTL is determined by how frequently the data changes and how much staleness is acceptable. A product's price that changes hourly should have a TTL shorter than 1 hour. A static page that changes monthly can have a TTL of 1 day. |
| Cache and database should always agree | A cache is designed to be a temporary, potentially stale copy. Strict consistency between cache and database requires either a very short TTL (frequent misses) or cache invalidation on every write (complex and potentially slow). For most data, eventual consistency (within the TTL window) is acceptable. Design explicitly: which data requires strong consistency (don't cache it, or use write-through), and which can be stale. |
| High hit rate means the cache is working well | A 99% hit rate for data that never changes is not impressive - it could just be a very long TTL. The meaningful metric is: how much database load has been reduced? A 70% hit rate on data that accounts for 99% of DB reads is more impactful than a 99% hit rate on data accounting for 1% of reads. Measure DB query rate reduction, not just hit rate in isolation. |

---

### 🚨 Failure Modes & Diagnosis

**Cache Stampede (Thundering Herd)**

**Symptom:**
At a regular interval (e.g., every hour on the dot),
database CPU spikes to 100%. Latency spikes. Users
experience slow responses briefly, then it recovers.
Pattern repeats exactly every hour.

**Root Cause:**
All instances of a popular cached value have the same
TTL (set to exactly 3600 seconds). They all expire
simultaneously. Hundreds of requests simultaneously
miss the cache and hit the database (a "thundering herd").

**Fix - Jitter on TTL:**
```python
import random

def cache_set_with_jitter(key: str, value: str,
                            base_ttl: int):
    """
    Add random jitter to TTL to prevent
    synchronized expiration (cache stampede).
    """
    # Instead of all keys expiring at exactly 3600s:
    # Some expire at 3400s, some at 3600s, some at 3800s.
    # Requests are spread over a 400-second window.
    jitter = random.randint(
        -int(base_ttl * 0.1),
        int(base_ttl * 0.1)
    )
    actual_ttl = base_ttl + jitter
    r.setex(key, actual_ttl, value)

# Also: use probabilistic early expiration
# If remaining TTL is < 10% of original, and you are
# the lucky request (1% probability): pre-refresh the cache
# before the TTL expires. Prevents the spike entirely.
def get_with_early_refresh(key: str, original_ttl: int,
                             fetch_fn):
    cached = r.get(key)
    ttl = r.ttl(key)  # Remaining TTL
    
    if cached and ttl > original_ttl * 0.1:
        return json.loads(cached)
    
    if not cached or (random.random() < 0.01):
        # Fetch fresh value and refresh cache
        fresh = fetch_fn()
        cache_set_with_jitter(key, json.dumps(fresh),
                               original_ttl)
        return fresh
    
    return json.loads(cached)  # Return stale while refreshing
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- (none - this is a foundational concept entry)

**Builds On This (learn these next):**
- `Caching (System Design)` - detailed patterns:
  cache-aside, write-through, write-behind, read-through
- `Distributed Cache Design` - designing Redis/Memcached
  clusters for high availability
- `Cache Invalidation Strategies` - strategies for
  keeping cache consistent with the database

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Store expensive results near the reader.  │
│             │ Serve from cache. Update DB on miss.      │
├─────────────┼──────────────────────────────────────────  │
│ HIT RATE    │ Target: 95%+. Below 80% = investigate.   │
│             │ Measure DB load reduction, not just rate. │
├─────────────┼──────────────────────────────────────────  │
│ TTL         │ Match to data freshness requirement.      │
│             │ Add ±10% jitter to prevent stampedes.    │
├─────────────┼──────────────────────────────────────────  │
│ EVICTION    │ LRU (default). LFU for stable popularity. │
│             │ Size cache to fit hot data (20% of total).│
├─────────────┼──────────────────────────────────────────  │
│ CACHE-ASIDE │ App checks cache. Miss → DB → store.     │
│             │ Most common pattern.                     │
├─────────────┼──────────────────────────────────────────  │
│ STAMPEDE    │ Jitter TTL. Stampede lock. Early refresh. │
│             │ Prevent synchronized expiration.         │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Check cache. Hit: return fast.          │
│             │  Miss: fetch DB, store, return."        │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ What is a Message Queue (Conceptual)      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Cache hit rate target: 95%+. The "cliff" is around
   90% - below 90%, the database still handles significant
   load. Measure actual database query reduction, not
   just cache hit rate in isolation.
2. TTL = the trade-off between freshness and performance.
   Match TTL to how often data actually changes. Add
   ±10% jitter to prevent cache stampedes (synchronized
   expiration of many keys at the same moment).
3. The hardest problem in caching is invalidation: when
   data changes in the database, how do you make sure
   the cache serves the new value? Options: delete the
   cache key (invalidate), update the cache key immediately
   (write-through), or accept stale data until TTL expires.

**Interview one-liner:**
"Cache: fast, temporary storage for expensive-to-compute results. Cache-aside
(most common): check cache first, on miss: fetch DB, store with TTL, return.
Target 95%+ hit rate. TTL: match to data change frequency, add ±10% jitter to
prevent stampedes. Eviction: LRU (allkeys-lru in Redis). Cold start: cache is
empty on restart, first requests are all misses. Invalidation options: delete key
on write (lazy), update key on write (write-through), or accept stale until TTL.
Hardest problem: invalidation."
