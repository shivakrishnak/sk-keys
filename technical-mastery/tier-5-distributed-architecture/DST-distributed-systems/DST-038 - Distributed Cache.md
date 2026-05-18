---
id: DST-038
title: Distributed Cache
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-026, DST-030
used_by: DST-042, DST-054
related: DST-014, DST-026, DST-028, DST-030
tags:
  - distributed
  - caching
  - performance
  - scalability
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/distributed-systems/distributed-cache/
---

⚡ TL;DR - A distributed cache stores frequently
accessed data in fast memory across multiple nodes,
reducing database load and improving latency; it
introduces cache invalidation complexity (stale data),
cache stampede risk (all clients miss simultaneously),
and consistency challenges that must be explicitly
designed for, because the cache is always potentially
stale.

---

### 📋 Entry Metadata

| #038 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Replication Lag, Consistent Hashing | |
| **Used by:** | Content Delivery, Session Management | |
| **Related:** | Consistency, Replication Lag, Eventual Consistency, Consistent Hashing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A product detail page reads 10 database queries per
request: product details, pricing, inventory, reviews,
recommendations, related products, user preferences,
shipping options, discount rules, and seller info.
At 10,000 requests per second, this is 100,000 database
queries per second. The database can handle 5,000
queries per second. The service is 20x over database
capacity. The database crashes. The application crashes.

**THE INSIGHT:**
Product details change infrequently (minutes to hours).
Reading the same data from a database millions of times
per day is wasteful. A cache stores the result in memory,
serving subsequent reads in microseconds without hitting
the database. At 95% cache hit rate, the 100,000 queries
per second become 5,000 database queries - within capacity.

The flip side: caches introduce a new class of bugs:
what happens when the data changes but the cache still
serves the old version? Cache invalidation is one of
the two hard problems in computer science (the other
being naming things and off-by-one errors).

---

### 📘 Textbook Definition

A **distributed cache** is an in-memory data store
spread across multiple nodes, accessible by application
instances over a network. It serves as a temporary
high-speed storage layer in front of slower primary
storage (databases, filesystems).

**Key properties:**
- **Cache hit:** data found in cache; served from memory
  (typically microseconds)
- **Cache miss:** data not in cache; fetched from source
  (typically milliseconds)
- **TTL (Time To Live):** how long a cache entry is
  valid before automatic expiry
- **Eviction policy:** what to remove when cache is full
  (LRU = Least Recently Used, LFU = Least Frequently Used)

**Cache write strategies:**
- **Cache-aside:** application manages cache explicitly
- **Write-through:** write to cache and database together
- **Write-behind (write-back):** write to cache first,
  async to database

---

### ⏱️ Understand It in 30 Seconds

**The cache hit ratio determines the value:**
```
Without cache:  10,000 req/s × 10ms DB latency
  = 100,000 DB queries/s (impossible at this scale)

With 95% hit rate:
  5% miss × 10,000 req/s = 500 DB queries/s
  95% hit: served from cache in <1ms

Cache hit rate improvement impact:
  90% hit rate: 1000 DB queries/s
  95% hit rate: 500 DB queries/s
  99% hit rate: 100 DB queries/s (10x reduction vs 95%)
```

**The three main failure modes:**
```
1. Cache stampede:   Key expires → all clients query DB
                     simultaneously → DB overwhelmed

2. Stale data:       Cache serves old data after update
                     (invalidation not propagated)

3. Cache avalanche:  Many keys expire simultaneously
                     → massive DB spike
```

---

### 🔩 First Principles Explanation

**CACHE-ASIDE (LAZY LOADING) PATTERN:**

```
READ PATH:
  1. Check cache for key
  2. If HIT: return cached value (fast path)
  3. If MISS:
     a. Read from database
     b. Store result in cache with TTL
     c. Return value to caller

WRITE PATH:
  1. Write to database
  2. Invalidate (delete) cache key
     (OR: update cache with new value)

WHY INVALIDATE (NOT UPDATE):
  Deleting is safer: ensures next read gets fresh DB data.
  Updating is faster: no miss on next read.
  Race condition with update:
    Thread A: reads DB (old value)
    Thread B: writes DB + updates cache (new value)
    Thread A: overwrites cache with old value
  → Stale cache despite recent write
  → Invalidation avoids this by forcing a re-read.
```

**THE CACHE STAMPEDE PROBLEM:**

```
Cache entry for product:123 expires at t=1000

t=1001: 500 concurrent requests check cache
         → all see MISS (key expired)
         → all query database
         → database receives 500 simultaneous queries
         → database overloads

FIX OPTIONS:
  1. MUTEX LOCK: first miss acquires lock, computes,
     stores result; others wait. Prevents stampede
     but adds latency to waiters.

  2. PROBABILISTIC EARLY REFRESH: before TTL expires,
     probabilistically recompute:
     P(refresh) = 1 / (TTL_remaining × rate_of_access)
     High traffic = high probability of early refresh.

  3. STALE-WHILE-REVALIDATE: serve stale data to most
     callers, refresh in background.
     Accept brief staleness in exchange for no stampede.
```

**DISTRIBUTED CACHE TOPOLOGY:**

```
CENTRALIZED (single Redis/Memcached node):
  Simple; single point of failure; limited capacity.

REPLICATED (Redis Sentinel or Cluster read replicas):
  Reads from replicas; writes to primary.
  Same replication lag concerns as databases.

SHARDED (Redis Cluster, Memcached consistent hashing):
  Keys distributed across shards.
  Hot key = single shard overloaded.
  Consistent hashing minimizes rebalancing cost.

LOCAL CACHE (in-process, per node):
  No network hop; fastest possible.
  Difficult to invalidate across nodes.
  Cache entries may differ per application instance.
```

---

### 🧠 Mental Model / Analogy

> A distributed cache is like a library system with
> a photocopier. The original books are in the main
> library (database). The photocopier creates copies
> for the branch libraries (cache). Most people can
> find what they need at the branch (cache hit). When
> the original is updated (new edition), the branch
> copies become stale. Someone must either immediately
> update all branches (write-through) or discard the
> old copies and wait for the next person to request
> a fresh copy (cache-aside with invalidation). If you
> never notify branches of updates, they serve
> outdated information indefinitely (missing TTL or
> invalidation).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A fast in-memory store that saves results from slow
database queries. Read from cache first; if not there,
read from database and store in cache. Subsequent reads
are fast. Trade-off: the cache may be slightly out of date.

**Level 2 - Cache-aside vs write-through:**
Cache-aside (lazy): you manage when to populate and
invalidate the cache. Simple but cache starts empty
(cold start problem). Write-through: on every database
write, also update the cache. Always consistent but
higher write latency. Choose based on read-to-write ratio
and consistency requirements.

**Level 3 - TTL strategy:**
TTL is the primary mechanism for ensuring eventual
freshness. Choosing TTL:
- Too short: high cache miss rate, high database load
- Too long: stale data served to users

Pattern: differentiate by data change frequency.
User profile: TTL=5 minutes (changes infrequently).
Stock price: TTL=1 second (changes frequently).
Static content: TTL=24 hours or until deployment.

**Level 4 - The distributed nature:**
Redis Cluster distributes keys across 16,384 hash slots
using CRC16 mod 16384. Consistent hashing for key routing.
Adding/removing shards triggers slot migration (keys
move incrementally). During migration: cache is
temporarily unavailable for migrating keys. Applications
must handle cache miss gracefully (fall through to DB).

**Level 5 - Read-through and write-around:**
Read-through: the cache itself fetches from the database
on miss (cache acts as a proxy). Application code has
no knowledge of the database. Used by some CDN and
database caching layers. Write-around: all writes go
directly to the database, bypassing the cache. Cache
is populated only on reads. Good for write-heavy workloads
where cached data may never be read. The right pattern
depends on the access pattern: predominant reads favor
cache-aside or read-through; write-heavy workloads with
occasional reads favor write-around.

---

### ⚙️ Cache Invalidation Strategies

```
STRATEGY 1: TTL-ONLY (simplest)
  Set TTL based on acceptable staleness.
  No explicit invalidation on write.
  Risk: stale data for up to TTL duration.
  Use when: staleness is acceptable (product listings)

STRATEGY 2: WRITE-INVALIDATE (cache-aside)
  On every database write: delete cache key.
  Next read: cache miss → fresh DB fetch → populate cache.
  Use when: strong consistency needed after writes.
  Risk: cache stampede after popular key invalidation.

STRATEGY 3: WRITE-UPDATE (update-on-write)
  On every database write: also write to cache.
  Next read: always a hit (no cold start after write).
  Risk: race condition (write order matters).
  Fix: use conditional updates (version check).

STRATEGY 4: EVENT-DRIVEN INVALIDATION
  Database change captured as CDC event.
  Cache listener receives event, invalidates key.
  More complex but decoupled.
  Use when: many services cache the same data.
```

---

### 💻 Code Example

**Cache-Aside: Wrong vs Right**

```python
# BAD: Caching without TTL or error handling
import redis

r = redis.Redis()

def get_product(product_id: str) -> dict:
    cached = r.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)
    # BUG 1: No TTL - stale data cached forever
    # BUG 2: No exception handling - cache failure kills service
    # BUG 3: No stampede protection
    product = db.query(
        "SELECT * FROM products WHERE id=%s",
        product_id
    )
    r.set(f"product:{product_id}", json.dumps(product))
    return product
```

```python
# GOOD: Cache-aside with TTL, stampede protection,
# and graceful degradation on cache failure

import redis
import json
import time
import threading
from typing import Optional

redis_client = redis.Redis(
    host="redis-host",
    port=6379,
    socket_timeout=0.1,    # Fast timeout on cache errors
    socket_connect_timeout=0.1
)

_stampede_locks: dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()

def get_stampede_lock(key: str) -> threading.Lock:
    with _locks_lock:
        if key not in _stampede_locks:
            _stampede_locks[key] = threading.Lock()
        return _stampede_locks[key]

def get_product(
    product_id: str,
    ttl_seconds: int = 300
) -> Optional[dict]:
    cache_key = f"product:{product_id}"

    # 1. Try cache first (fast path)
    try:
        cached = redis_client.get(cache_key)
        if cached is not None:
            return json.loads(cached)
    except redis.RedisError:
        # Cache unavailable: fall through to database
        pass  # Never let cache failure kill the service

    # 2. Cache miss: use lock to prevent stampede
    lock = get_stampede_lock(cache_key)
    with lock:
        # Double-check after acquiring lock
        try:
            cached = redis_client.get(cache_key)
            if cached is not None:
                return json.loads(cached)
                # Another thread populated it
        except redis.RedisError:
            pass

        # 3. Fetch from database
        product = db.fetch_product(product_id)
        if product is None:
            # Cache the "not found" result too (prevents DB hammering)
            try:
                redis_client.setex(
                    cache_key,
                    60,         # Shorter TTL for "not found"
                    json.dumps(None)
                )
            except redis.RedisError:
                pass
            return None

        # 4. Populate cache with TTL
        try:
            redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(product)
            )
        except redis.RedisError:
            pass  # Cache write failure: not fatal

        return product

def invalidate_product(product_id: str) -> None:
    """Call after product update in database."""
    try:
        redis_client.delete(f"product:{product_id}")
    except redis.RedisError:
        pass  # Best-effort invalidation; TTL will catch it
```

---

### ⚖️ Comparison Table

| Pattern | Consistency | Write Latency | Read Latency | Complexity |
|---|---|---|---|---|
| **Cache-aside** | Eventual (TTL) | DB write only | Miss: DB; Hit: Cache | Low |
| **Write-through** | Strong | DB + Cache | Always Cache | Medium |
| **Write-behind** | Eventual | Cache only | Always Cache | High |
| **Read-through** | Eventual (TTL) | DB write only | Cache transparent | Medium |

| Eviction Policy | Best For |
|---|---|
| **LRU** (Least Recently Used) | General-purpose access patterns |
| **LFU** (Least Frequently Used) | Viral/popular content |
| **TTL-based** | Time-sensitive data |
| **FIFO** | Streaming/pipeline data |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The cache is always consistent with the database" | Caches are inherently eventually consistent. Even write-through has a window where the database write could fail while the cache was updated (or vice versa). Design for occasional staleness. |
| "Caching is just about performance" | Caches reduce load (availability), reduce latency (performance), and can serve stale data during database outages (resilience). The resilience use case is underappreciated. |
| "Cache invalidation is straightforward" | "There are only two hard things in Computer Science: cache invalidation and naming things." - Phil Karlton. Race conditions between writes and invalidation are subtle and frequent. |
| "Higher cache hit rate is always better" | 100% hit rate means the cache never reflects updates (infinite TTL). The correct hit rate balances freshness requirements with load reduction needs. 95-99% is typical; 100% is wrong. |

---

### 🚨 Failure Modes & Diagnosis

**Cache Stampede**

**Symptom:** Database CPU spikes to 100% every 5
minutes exactly. Application latency spikes at the
same interval.

**Root Cause:** Popular cache key with TTL = 5 minutes.
Every 5 minutes, the key expires. Hundreds of concurrent
requests see a miss and simultaneously query the database.

**Diagnosis:**
```bash
# Redis: check TTL of popular keys:
redis-cli TTL product:bestseller:123
# If TTL is consistent and matches spike interval: stampede

# Redis: monitor cache hit/miss rate:
redis-cli info stats | grep -E "keyspace_hits|keyspace_misses"
# Calculate hit rate: hits / (hits + misses)
# Spike in misses at regular intervals: stampede pattern

# Application: add metrics on cache misses:
# If miss_count spikes 100x normal every N minutes: stampede
```

**Fix:**
```python
# Add jitter to TTL to prevent synchronized expiry:
import random

def set_with_jitter(
    key: str,
    value: str,
    base_ttl: int
) -> None:
    # Add ±10% random jitter to TTL
    jitter = random.randint(
        -base_ttl // 10,
        base_ttl // 10
    )
    redis_client.setex(key, base_ttl + jitter, value)

# Or: use probabilistic early refresh (prevent expiry):
def should_early_refresh(
    ttl_remaining: int,
    ttl_original: int,
    access_rate: float,
    beta: float = 1.0
) -> bool:
    """Return True if we should refresh before expiry."""
    return random.random() < (
        1 / (ttl_remaining * access_rate ** beta)
    )
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Replication Lag` (DST-026)
- `Consistent Hashing` (DST-030)

**Builds On This:**
- Content Delivery Networks (CDN), Session Management

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PATTERNS   │ Cache-aside: app manages (most common)     │
│            │ Write-through: always consistent           │
│            │ Write-behind: async DB writes              │
├────────────┼────────────────────────────────────────────┤
│ RISKS      │ Stampede: many miss on same key expiry     │
│            │ Avalanche: many keys expire together       │
│            │ Stale data: TTL too long                   │
├────────────┼────────────────────────────────────────────┤
│ FIXES      │ Lock on miss (stampede), TTL jitter (avalan│
│            │ Invalidate-on-write (staleness)            │
├────────────┼────────────────────────────────────────────┤
│ GOLDEN TTL │ Short for volatile data, long for static;  │
│            │ always add jitter                          │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Cache reads work; cache invalidation      │
│            │  is the hard part - design it first."     │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The distributed cache pattern introduces the most
important principle in caching: every caching layer
creates a consistency contract. That contract must
be explicit: how stale can the data be? Who is
responsible for invalidation? What happens on cache
failure? A cache without explicit answers to these
questions is a correctness bug waiting for a high-traffic
moment to reveal itself. The same questions apply to
browser caches, CDN edge caches, HTTP caches, and DNS
caches. The domain changes; the contract questions
do not.

---

### 💡 The Surprising Truth

Facebook's "Memcache at Scale" paper (2013) revealed
a counter-intuitive finding: at extreme scale, the
biggest cache reliability problem was not hardware
failure or network partitions - it was "thundering
herd from cold start." When a Facebook cache cluster
was restarted (routine maintenance), millions of
requests immediately hit the backend databases with
cache misses. The resulting load exceeded database
capacity. Facebook's solution: "lease mechanism" -
when a key is being fetched (miss in progress), the
cache issues a "lease token" to the first requester
and holds subsequent requesters in a short wait.
This prevents multiple simultaneous fetches of the
same key. The insight: cache stampede is often more
dangerous than total cache unavailability, because
the stampede actively degrades the system while the
cache is up and apparently functioning.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Write cache-aside for a product catalog
   with TTL, stampede protection via mutex, and graceful
   degradation when Redis is unavailable.
2. [CHOOSE] For each: user authentication tokens, product
   prices, static homepage HTML, user shopping cart -
   specify the cache pattern (cache-aside/write-through),
   TTL, and invalidation strategy.
3. [DEBUG] Database CPU spikes every 10 minutes exactly.
   Diagnose whether it is cache stampede, and implement
   TTL jitter to fix it.
4. [DESIGN] For a read-heavy API serving 100,000 req/s
   with a database that handles 5,000 queries/s, calculate
   the minimum cache hit rate required and design the
   caching layer to achieve it.
5. [EXPLAIN] The race condition in "write-then-update-cache"
   vs "write-then-invalidate-cache" with a concrete
   example of the failure scenario each produces.
