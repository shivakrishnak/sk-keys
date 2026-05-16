---
id: SYD-006
title: What is a Cache (System Design Context)
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: SYD-005
used_by: SYD-073
related: SYD-030
tags:
  - caching
  - foundational
  - mental-model
  - performance
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /system-design/what-is-a-cache-system-design-context/
---

# SYD-006 - What is a Cache (System Design Context)

⚡ TL;DR - A cache stores expensive computation results
near the reader so the same work is never done twice,
trading memory for speed.

| #006            | Category: System Design       | Difficulty: ★☆☆ |
| :-------------- | :---------------------------- | :-------------- |
| **Depends on:** | What is Scalability           |                 |
| **Used by:**    | Cache Invalidation Strategies |                 |
| **Related:**    | CDN Architecture Pattern      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your database stores 50 million user profiles. Every
page load fetches the current user's profile from the
database: a disk seek, a SQL parse, an index scan, a
row read - 20ms of latency per request. At 10,000
requests per second, your database processes 10,000
identical profile fetches every second. The same 100
"hot" users account for 70% of that load. You are
executing the same query, reading the same rows, and
paying the full database round-trip cost - every single
time.

**THE BREAKING POINT:**
Database connections are limited. Connection pools
exhaust. Query queues build. CPU spikes. Latency climbs.
Under heavy read load, a database that could handle
complex writes and analytical queries is now burning
resources on trivially repetitive reads.

**THE INVENTION MOMENT:**
"This is exactly why caching was created." - pre-compute
once, store the result in fast memory, serve thousands
of reads from that single stored result.

**EVOLUTION:**
Early caches were OS page caches (1960s) - the kernel
kept recently used disk blocks in RAM. Application-level
caches became widespread with memcached (2003, designed
for LiveJournal). Redis (2009) added data structures and
persistence, becoming the dominant distributed cache.
Today, multi-tier caches span L1 (in-process), L2
(Redis cluster), and L3 (CDN) for globally distributed
access.

---

### 📘 Textbook Definition

A **cache** is a component that stores the results of
expensive operations in a faster storage tier so future
requests for the same result are served faster. In
system design, caches reduce latency, increase
throughput, and shield downstream systems from read
amplification. The cache operates on the principle of
temporal locality: recently accessed data is likely to
be accessed again soon.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A cache remembers the answer to a question so the next
person asking gets an instant reply.

**One analogy:**

> A librarian who notices everyone asks for the same
> five books keeps those books on their desk instead of
> re-fetching them from the back stacks for every visitor.
> The desk is the cache. The stacks are the database.

**One insight:**
A cache does not make your data faster to compute -
it makes it free to read the second time. The value
compounds: if 95% of reads hit the cache, your database
only sees 5% of the traffic, multiplying its effective
capacity 20x.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Some data is read far more often than it changes.
2. Fast storage (RAM) is more expensive than slow
   storage (disk, network).
3. Repeated identical computation is waste.

**DERIVED DESIGN:**
Given that reads vastly outnumber writes for hot data,
and RAM access is ~1000x faster than a database round
trip, a cache layer intercepts reads, stores results
in RAM, and returns them without touching the origin.

The key design decision: **cache invalidation** - when
must the cached copy be discarded because the source
changed? This is famously one of computer science's
two hard problems.

**THE TRADE-OFFS:**
**Gain:** Orders-of-magnitude reduction in read latency
and database load.

**Cost:** Stale data risk - the cache may serve outdated
results if invalidation is delayed. Additional
operational complexity (cache warming, eviction,
serialization).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Cache invalidation is inherently hard
because distributed systems have no instant global
consistency. When data changes, every cache holding
a copy must learn about it.

**Accidental:** Cache serialization formats
(JSON vs MessagePack vs Protobuf) and cache key
naming conventions are accidental - tooling choices
that could be simpler.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce site renders a product page. Rendering
requires 12 database queries: product details,
inventory, reviews, recommendations, pricing. Total
DB time: 150ms. The product page is viewed 10,000
times per hour.

**WHAT HAPPENS WITHOUT A CACHE:**
12 queries x 10,000 views = 120,000 DB queries per
hour for one product page. The DB handles it, but
barely. Add 1,000 products and it buckles.

**WHAT HAPPENS WITH A CACHE:**
The first render executes all 12 queries and stores
the rendered HTML (or the aggregated data) in Redis
with a 5-minute TTL. The next 9,999 views in that
window fetch from Redis in 1ms instead of the DB
in 150ms. DB queries drop from 120,000/hour to
12/5-minutes = 144/hour per product.

**THE INSIGHT:**
A cache turns O(N) database queries into O(1) - or
more precisely, O(unique-keys) queries regardless of
read volume. The value scales with read amplification.

---

### 🧠 Mental Model / Analogy

> Think of a cash register with a small tray of common
> change (nickels, dimes, quarters). The cashier does
> not go to the vault for every transaction - they
> reach into the tray. Only when the tray runs out does
> the vault get touched. The tray is the cache.
> The vault is the database.

Mapping:

- "Tray of common change" → cache store (Redis)
- "Vault" → database / origin server
- "Frequently used coins" → hot/popular cache keys
- "Tray runs out" → cache miss
- "Restocking from vault" → cache population on miss
- "Old coins replaced with current bills" → eviction

**Where this analogy breaks down:** The tray has no
concept of "staleness" - coins don't expire. Cache
entries do, and stale data can cause correctness
problems, unlike stale coins.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A cache saves the answer to a slow question in a
fast place so the same question never costs full
price again.

**Level 2 - How to use it (junior developer):**
Store the result of a database query in Redis with
a key derived from the query parameters and a TTL
that matches how often the data changes. Check the
cache before every query. If the key exists, return
it. If not, query the DB and store the result.

**Level 3 - How it works (mid-level engineer):**
Caches operate on eviction policies (LRU, LFU, TTL).
LRU (Least Recently Used) evicts the oldest untouched
entry when memory is full. A cache hit ratio below
80% usually signals the cache is too small or the
keyspace is too large. Consistent hashing distributes
keys across a Redis cluster so adding nodes does not
invalidate the entire cache.

**Level 4 - Why it was designed this way (senior/staff):**
The read-through vs cache-aside distinction matters
at scale: cache-aside (application checks cache, then
DB) puts invalidation logic in application code,
creating N invalidation points as services multiply.
Read-through (cache fetches from DB on miss
transparently) centralizes it but requires a cache
that understands your data model. Write-through vs
write-behind affects durability vs throughput trade-off
for write paths.

**Level 5 - Mastery (distinguished engineer):**
Cache effectiveness is measured by hit ratio and
cache efficiency (bytes of useful data per byte of
cache memory). A high hit ratio on large objects is
worth more than the same ratio on tiny objects.
The hardest cache design problem is stampede
prevention: when a popular key expires, thousands
of simultaneous misses hammer the origin. Solutions:
mutex locks, probabilistic early expiry, or
background refresh. At scale, cache topology (L1
in-process + L2 distributed) reduces network
overhead for the hottest keys.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│       CACHE-ASIDE READ PATTERN          │
│                                         │
│  Request                                │
│    │                                    │
│    ▼                                    │
│  Cache lookup (key)                     │
│    │         │                          │
│  HIT         MISS                       │
│    │           │                        │
│    ▼           ▼                        │
│  Return    Query DB                     │
│  cached    │                            │
│  value     ▼                            │
│          Store in cache                 │
│          (key, value, TTL)              │
│            │                            │
│            ▼                            │
│          Return value                   │
└─────────────────────────────────────────┘
```

**Step 1 - Key Generation:**
A deterministic key is derived from the request
parameters: `product:v2:{product_id}`. The version
prefix allows instant full invalidation by bumping
the version.

**Step 2 - Cache Lookup:**
Redis GET by key. If found, deserialize and return.
Time: ~0.2ms.

**Step 3 - Cache Miss:**
Query the database. Serialize the result. Store in
Redis with SET key value EX {ttl}. Return the value.

**Step 4 - Expiry and Eviction:**
Redis TTL expires the key after the configured time.
If memory pressure hits `maxmemory`, the configured
eviction policy (LRU, LFU, allkeys-lru) removes
the least valuable entries.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Client → App Server
  → Redis GET "product:v2:42"
      ← YOU ARE HERE (cache layer)
  → HIT: deserialize → return in 1ms
  → MISS: SQL query → 20ms → store in
    Redis → return
```

**FAILURE PATH:**

```
Redis cluster unavailable
  → All reads fall through to DB
  → DB load spikes 10-100x
  → DB connection pool exhausts
  → App returns 503
  → Fix: circuit breaker to DB on
    Redis failure
```

**WHAT CHANGES AT SCALE:**
At 10x load, cache hit ratio becomes critical -
a drop from 95% to 85% doubles DB load. At 100x,
a single Redis node becomes the bottleneck; cluster
mode with consistent hashing is required. At 1000x,
an in-process L1 cache reduces Redis round trips
for the hottest keys.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Caching pattern**

```python
# BAD - no caching, DB hit on every request
def get_user_profile(user_id):
    return db.query(
        "SELECT * FROM users WHERE id = %s",
        user_id
    )
```

```python
# GOOD - cache-aside pattern with TTL
import json, redis

cache = redis.Redis(host='redis', port=6379)

def get_user_profile(user_id):
    key = f"user:v1:{user_id}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)  # cache HIT
    # cache MISS - fetch from DB
    profile = db.query(
        "SELECT * FROM users WHERE id = %s",
        user_id
    )
    cache.setex(
        key,
        300,  # 5-minute TTL
        json.dumps(profile)
    )
    return profile
```

**Example 2 - Failure: Cache stampede fix**

```python
# BAD - all threads query DB on cache expiry
def get_popular_product(product_id):
    key = f"product:{product_id}"
    data = cache.get(key)
    if not data:
        # 1000 threads all reach here simultaneously
        data = db.get_product(product_id)
        cache.setex(key, 60, json.dumps(data))
    return json.loads(data)
```

```python
# GOOD - mutex lock prevents stampede
import threading
_locks = {}

def get_popular_product(product_id):
    key = f"product:{product_id}"
    data = cache.get(key)
    if data:
        return json.loads(data)
    # Only one thread refreshes the cache
    lock = _locks.setdefault(
        product_id, threading.Lock()
    )
    with lock:
        data = cache.get(key)  # re-check
        if data:
            return json.loads(data)
        result = db.get_product(product_id)
        cache.setex(key, 60, json.dumps(result))
        return result
```

**How to test / verify correctness:**
Mock the DB call and assert it is called exactly once
even with 100 concurrent threads. Verify cache.get
returns the stored value on subsequent calls without
hitting the DB mock.

---

### ⚖️ Comparison Table

| Cache Strategy  | Consistency | Complexity | Best For             |
| --------------- | ----------- | ---------- | -------------------- |
| **Cache-Aside** | Eventual    | Low        | General reads        |
| Read-Through    | Eventual    | Medium     | ORM integration      |
| Write-Through   | Strong      | High       | Write+read parity    |
| Write-Behind    | Eventual    | High       | Write-heavy, durable |

**How to choose:** Cache-aside is the default for most
read-heavy applications - it is simple and puts the
developer in control. Use write-through only when read
consistency immediately after writes is required.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                 |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Caching always improves performance          | A cache with a 20% hit ratio adds latency overhead without reducing DB load meaningfully.                               |
| Bigger cache is always better                | Beyond the working set size, adding cache memory yields zero improvement. Profile your hit ratio first.                 |
| Cache invalidation is easy                   | It is famously one of the two hard problems in CS. Complex data relationships make safe invalidation non-trivial.       |
| Redis is just a cache                        | Redis is a data structure server. Using it only as a cache misses persistence, pub/sub, streams, and distributed locks. |
| TTL-based caches are safe for financial data | Stale pricing or balance data can cause real-money errors. Never use TTL-only invalidation for money-related data.      |

---

### 🚨 Failure Modes & Diagnosis

**Cache Stampede (Thundering Herd)**

**Symptom:**
Periodic database CPU spikes at exact intervals
matching cache TTLs. App latency spikes coincide.

**Root Cause:**
Popular cache key expires. Many concurrent requests
miss the cache and simultaneously query the DB.

**Diagnostic Command / Tool:**

```bash
# Redis: monitor expired events
redis-cli monitor | grep "expired"
# Confirm DB spike correlation in Grafana
```

**Fix:**
Add per-key mutex (see Example 2). Or add TTL jitter:
`TTL = base + random.randint(0, base // 10)`

**Prevention:**
Use probabilistic early expiry: refresh the key with
a small probability when TTL drops below 20% of base.

---

**Cache Poisoning (Security Failure)**

**Symptom:**
Users see other users' data. Sensitive data is leaked
across accounts. Audit logs show impossible access
patterns.

**Root Cause:**
Cache key includes user-controlled input without
sanitization. Attacker crafts a key that collides
with another user's cache entry.

**Diagnostic Command / Tool:**

```bash
# Redis: scan for unexpected key patterns
redis-cli --scan --pattern "user:*" \
  | head -20
# Look for keys with injected separators
```

**Fix:**
Never include raw user input in cache keys.
Hash or encode all user-provided parameters.

**Prevention:**
Treat cache keys as internal identifiers.
Use SHA256 of the canonical query string as the key.

---

**Cache Inconsistency After Write**

**Symptom:**
User updates their profile, refreshes the page, and
sees the old data for up to N seconds (N = TTL).

**Root Cause:**
Write path updated the database but did not invalidate
the cache. Stale cached entry is still served.

**Diagnostic Command / Tool:**

```bash
# Redis: check key TTL and value after write
redis-cli TTL "user:v1:42"
redis-cli GET "user:v1:42"
```

**Fix:**
On every write, call `cache.delete(key)` or
`cache.setex(key, ttl, new_value)` atomically.

**Prevention:**
Use the write-through pattern or event-driven
invalidation via database change streams.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What is Scalability` - caching is the primary tool
  for scaling read throughput without adding DB nodes
- `Redis` - the dominant distributed cache technology;
  understanding its data types and eviction policies
  is essential for production caching

**Builds On This (learn these next):**

- `Cache Invalidation Strategies` - the hard problem:
  when and how to evict stale data correctly
- `CDN Architecture Pattern` - caches at the network
  edge, applying the same principle geographically
- `Connection Pooling (System Design)` - the related
  pattern of reusing expensive resources

**Alternatives / Comparisons:**

- `Materialized Views` - database-level pre-computation
  that avoids network overhead of a separate cache tier

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fast storage tier that serves repeated    │
│              │ reads without hitting the origin          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Identical DB reads are wasteful;          │
│ SOLVES       │ hot data deserves a fast path             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ 95% hit ratio means DB sees 5% of reads;  │
│              │ the cache multiplies DB capacity 20x      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Data is read far more often than it       │
│              │ changes; DB reads are the bottleneck      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Data changes very frequently OR strict    │
│              │ consistency is required (financial data)  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Caching user-controlled keys without      │
│              │ sanitization (cache poisoning)            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lower latency + DB load vs stale data     │
│              │ risk and invalidation complexity          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The fastest query is the one you         │
│              │  never execute."                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cache Invalidation → Redis → CDN          │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Hit ratio is the metric. Below 80% the cache adds
   overhead without meaningful benefit.
2. Cache invalidation is hard. Stale data is a
   correctness problem, not just a performance one.
3. The stampede problem: popular key expiry causes
   thundering herd. Always protect with jitter or mutex.

**Interview one-liner:**
"A cache stores expensive results near the reader.
The value is in read amplification reduction: a 95%
hit ratio means the database handles 5% of read
traffic. The hard problem is invalidation - you need
a strategy for how caches learn about writes, whether
TTL, explicit delete, or event-driven."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Pre-compute once, serve many." Caching is the
application of memoization at the infrastructure
level. Any time the same expensive operation is
repeated with the same inputs, caching is applicable.

**Where else this pattern appears:**

- CPU L1/L2/L3 caches - hardware-level memoization
  of memory accesses
- DNS caching - cached IP resolutions avoid resolver
  round trips on every connection
- Browser caches - HTTP ETag and Cache-Control headers
  prevent re-downloading unchanged assets

**Industry applications:**

- Social media platforms - cached timelines and
  friend counts for billions of users; strong
  consistency is sacrificed for throughput
- E-commerce - product catalog pages cached at CDN
  edge; inventory accuracy requires shorter TTL

---

### 💡 The Surprising Truth

A cache with a 95% hit ratio does not speed up the
average request by 95%. It speeds up 95% of requests
from 20ms to 0.2ms and leaves 5% unchanged. But at
system level, removing 95% of DB queries is the
difference between the database surviving and melting.
The cache's value is not the user experience
improvement - it is the capacity amplification on the
downstream system.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. [EXPLAIN] Explain cache hit ratio and why a 95% hit
   ratio effectively multiplies DB capacity 20x.
2. [DEBUG] Given periodic DB CPU spikes at exact
   intervals, identify cache stampede as the cause and
   describe the fix.
3. [DECIDE] Given write-heavy data that users must see
   updated immediately, choose write-through over
   cache-aside and explain the trade-off.
4. [BUILD] Implement a cache-aside pattern with TTL
   jitter and mutex stampede protection in Python or
   Java from memory.
5. [EXTEND] Design a multi-tier cache (L1 in-process +
   L2 Redis) for an application with 1 million RPS, and
   explain how cache invalidation propagates through
   both tiers consistently.

---

### 🧠 Think About This Before We Continue

**Q1.** Your cache hit ratio drops from 95% to 60%
after a new feature deploys. The feature adds 5 new
cache keys per user session. What are the top causes
of this drop and how do you diagnose each?
_Hint: Think about cache size (eviction), key
cardinality (too many unique keys), and TTL
misconfiguration._

**Q2.** At 1 million requests per second, your Redis
cluster handles reads fine but you need to reduce
network round trips for the 500 hottest keys. How
would you architect a two-tier caching solution
without introducing consistency problems?
_Hint: Consider in-process LRU caches and how they
learn about invalidation events._

**Q3.** [HANDS-ON] You need to cache product search
results that depend on user location, category, and
sort order. Design the cache key schema, TTL strategy,
and invalidation approach. What happens when a
product's price changes and it is in 10,000 cached
search result sets?
_Hint: Explore coarse-grained vs fine-grained
invalidation and whether you can afford eventual
consistency for search results._

---

### 🎯 Interview Deep-Dive

**Q1: What is cache invalidation and why is it hard?**
_Why they ask:_ Tests whether the candidate understands
caching beyond "add Redis." Invalidation is where
systems break.
_Strong answer includes:_

- Invalidation is removing stale entries when source
  data changes.
- Hard because distributed systems have no instant
  global consistency - caches may serve stale data
  between the write and the invalidation propagating.
- Common strategies: TTL expiry, explicit delete on
  write, event-driven invalidation via pub/sub.

**Q2: Your cache hit ratio is 45%. The product manager
wants to add more cache memory. Is that the right fix?**
_Why they ask:_ Tests whether candidate measures
before optimizing.
_Strong answer includes:_

- 45% may mean the working set exceeds cache size
  (add memory), or may mean the keyspace is too large
  (optimize key design).
- First step: measure key frequency distribution.
  If top 1% of keys account for 80% of reads, the
  cache is fine but the eviction policy is wrong.
- Profile with `redis-cli --hotkeys` or `OBJECT FREQ`.

**Q3: How would you cache data that multiple users
can write to, ensuring no user ever sees another
user's stale data?**
_Why they ask:_ Tests cache correctness in multi-writer
scenarios.
_Strong answer includes:_

- Use user-scoped cache keys: `resource:{id}:user:{uid}`
- On any write to the resource, invalidate all user
  scopes (expensive) or use a version counter
  (resource version in key, bump on write).
- For financial data: never cache with TTL-only;
  always invalidate on write explicitly.
