---
id: SYD-052
title: Distributed Cache Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-031
used_by: ""
related: SYD-008, SYD-031, SYD-032, SYD-069
tags:
  - architecture
  - cache
  - redis
  - distributed
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /syd/distributed-cache-design/
---

# SYD-052 - Distributed Cache Design

⚡ TL;DR - A distributed cache stores frequently-read
data in fast in-memory nodes shared across multiple
application servers, reducing database load and
improving response latency. Core design decisions:
cache-aside vs write-through vs write-behind (update
strategy), consistent hashing for node assignment (avoid
rehashing all keys when nodes are added/removed), TTL
management (how long data stays valid), eviction policy
(LRU, LFU, LRU-K), and hot key handling (a single
popular key overwhelming one cache node). Redis Cluster
is the standard production distributed cache.

| #052 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, Sharding | |
| **Related:** | Caching, Sharding, Hot Shard, Cache Invalidation Strategies | |

---

### 🔥 The Problem This Solves

A social media platform has 1M DAU. The user profile
API serves 50 million profile reads/day (50 reads per
user on average). Each profile read queries a PostgreSQL
database (100ms). Without a cache: 50M × 100ms latency,
and the database handles 578 queries/second. At 10x peak:
5,780 queries/second - exceeds PostgreSQL's write-optimized
connection limit. With a Redis cache: 90% cache hit rate
means 5% of queries reach the database (289 q/sec).
Profile reads drop to 5ms (cache hit). Database is free
for writes.

---

### 📘 Textbook Definition

**Distributed cache:** An in-memory data store that is
shared across multiple application servers. Reduces
database read load by serving frequently-accessed data
from memory. Faster than any database (< 1ms vs 10-100ms).
Horizontally scalable via consistent hashing.

**Cache-aside (lazy loading):** The most common caching
strategy. Application checks the cache first; on miss,
reads from the database and populates the cache.

**Write-through:** On write, update both the cache and
the database synchronously. Ensures cache is always
fresh; adds write latency.

**Write-behind (write-back):** Write to cache immediately;
flush to database asynchronously. Fastest writes; risk
of data loss if cache node fails before flush.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store frequently-read data in a fast in-memory cluster;
serve reads from memory instead of the database.

**One analogy:**
> A personal assistant:
> Instead of calling the archive room (database) every
> time your boss needs a document, your assistant keeps
> the most-used documents on their desk (cache).
> If it is on the desk: instant retrieval (cache hit).
> If not: go to the archive, get it, put a copy on
> the desk for next time (cache miss + population).
> When the desk is full: put away the least recently
> used document (LRU eviction).

**One insight:**
Cache hit rate is the primary metric. At 90% hit rate:
10% of requests reach the database. At 99% hit rate:
1% reach the database (10x better than 90%). Moving
from 90% to 99% hit rate has a larger impact than any
database optimization. The effort is in understanding
what to cache (hot data) and how long to cache it (TTL).

---

### 🔩 First Principles Explanation

**CONSISTENT HASHING:**
```
Problem with modulo hashing:
  key → server = hash(key) % N_servers
  Add 1 server (N=5 → N=6):
    hash(key) % 5 → hash(key) % 6
    ~83% of all keys map to a different server
    → massive cache miss storm when scaling

Consistent hashing:
  Arrange servers on a ring (0 to 2^32-1).
  Each server occupies a position on the ring.
  A key maps to the first server clockwise from hash(key).
  
  Add server:
    Only keys between the new server and its predecessor
    need to move. ~N/new_N = 1/N fraction of keys.
    5 → 6 servers: ~17% of keys move (not 83%).

Virtual nodes (vnodes):
  Each physical server has 150 virtual positions on ring.
  Reduces hot spots when servers have different loads.
  If one server goes down, its load spreads evenly
  across all remaining servers.
```

**UPDATE STRATEGIES:**
```
Cache-Aside (Lazy Loading):
  Read: app checks cache → miss → read DB → write cache
  Write: app writes DB only (cache entry becomes stale)
  
  Problem: cache is stale after writes
  Solution: invalidate (delete) cache key on write,
    or use TTL to expire stale data
  
  Pro: simple, only cache what is actually read
  Con: cache miss on first read (cold start)
  
  Best for: read-heavy data, acceptable staleness

Write-Through:
  Write: app writes cache AND DB synchronously
  Read: always hits cache (cache is always fresh)
  
  Pro: cache always up-to-date
  Con: write latency doubles (must wait for both)
  Con: caches data that may never be read (write-heavy)
  
  Best for: data that is written AND read frequently

Write-Behind (Write-Back):
  Write: app writes cache only (returns immediately)
  Async: background job flushes cache → DB
  
  Pro: fastest writes; DB write is non-blocking
  Con: data loss risk if cache fails before flush
  Con: complex: must handle flush failures
  
  Best for: high write throughput, acceptable risk
    (session data, analytics counts, non-critical)

Read-Through:
  Like cache-aside but cache handles DB read on miss
  (cache is a proxy, not just a store).
  Used when the cache library supports DB integration.
```

---

### 🧪 Thought Experiment

**SIZING: Twitter profile cache**

50M profiles. 90% of reads target top 10M profiles
(power law: celebrities and active users are hot).

**Cache what?**
Cache only the 10M hot profiles (not all 50M).
Average profile serialized: 1KB.
10M × 1KB = 10GB. Fits on a single Redis node with headroom.
With cluster (3 nodes × 100GB): plenty of space.

**TTL decision:**
Profile rarely changes. But when it does (name, avatar),
users expect near-real-time updates.
TTL: 5 minutes. On explicit profile update: invalidate key.
Cache hit: returns data up to 5 minutes old (acceptable).

**Hit rate:**
With 10M profiles cached and 90% of reads going to them:
expected cache hit rate = 90%.
10% miss rate → 578 × 10% = 57.8 queries/sec to DB.
Database handles easily. Latency: 5ms (cache hit) vs 100ms.

**Cluster topology:**
3 Redis primaries (consistent hashing, ~3.3M keys each).
3 replica nodes (one per primary, for failover).
Write quorum: write to primary only (async replication).
On primary failure: replica promoted in < 30 seconds.
During failover: ~30 seconds of potential inconsistency
(acceptable for profile cache).

---

### 🧠 Mental Model / Analogy

> Think of the distributed cache as a network of
> convenience stores in a city:
>
> - The warehouse (database) has everything but is
>   far away (100ms).
> - Convenience stores (cache nodes) stock the most
>   popular items near customers (< 1ms).
> - Different items go to different stores based on
>   a consistent algorithm (consistent hashing).
> - When a store runs out of space, the least recently
>   bought item is removed to make room (LRU eviction).
>
> Adding a new store: only move items near the new
> store's location (consistent hashing).
> Removing a store: its items go to the next nearest
> store (consistent hashing, graceful redistribution).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A distributed cache stores copies of database data in
fast memory that many servers share. Instead of asking
the database every time, servers ask the cache. If the
data is there: instant response. If not: ask the database
and save a copy for next time.

**Level 2 - How to use it (junior developer):**
Use Redis Cluster. On read: check Redis first (GET key).
On miss: query database, then SET the key with a TTL.
On write: update the database, then DELETE the cache key
(invalidate, so next read gets fresh data). Monitor
cache hit rate (target: > 80%). Monitor memory usage
(evict with LRU policy when memory is full).

**Level 3 - How it works (mid-level engineer):**
Redis Cluster uses consistent hashing (16,384 hash slots
divided among nodes). Each key maps to a slot. Nodes
own ranges of slots. Adding/removing nodes: migrate
only affected slots (not all keys). Use connection
pooling to Redis (avoid creating a connection per request).
Pipeline commands when doing multiple reads in one request.
Monitor: cache hit rate, eviction rate, memory usage,
key count per node (balanced?).

**Level 4 - Why it was designed this way (senior/staff):**
Redis Cluster uses hash slots (not pure consistent
hashing) because it simplifies cluster management: hash
slots can be migrated between nodes atomically, enabling
zero-downtime scaling. The 16,384 slot ceiling is a
design choice: large enough for fine-grained key
distribution, small enough for the gossip protocol
(each node broadcasts its slot assignments to all
other nodes). The eviction policy (LRU vs LFU) is
workload-dependent: LRU is good for temporal locality
(recently accessed data is likely to be accessed again);
LFU is better for long-lived hot data (frequently
accessed over time, not just recently).

**Level 5 - Mastery (distinguished engineer):**
At Facebook Memcache scale (trillions of cache operations
per day), the distributed cache is itself a distributed
system with its own failure modes. Key operational
challenges: (1) "thundering herd" on cache warmup after
a cold start (all servers simultaneously get cache
misses and flood the database) - mitigated with jittered
TTLs and rate-limited cache warming; (2) "hot key"
problem - a single viral post is read by 100M users
simultaneously, all hitting the same cache node (it
becomes a bottleneck) - mitigated with local L1 caches
on each app server (small, < 1000 keys) with very short
TTL (1-2 seconds) to absorb hot key traffic; (3) cache
eviction cascades - if cache is 95% full and a burst
of new data arrives, mass eviction of existing keys
triggers a database read spike. Prevention: size the
cache so steady-state utilization is < 70%.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REDIS CLUSTER: CONSISTENT HASHING                   │
│                                                      │
│ 16384 hash slots distributed across 3 nodes:        │
│   Node A: slots 0-5460                              │
│   Node B: slots 5461-10922                          │
│   Node C: slots 10923-16383                         │
│                                                      │
│ Key routing:                                        │
│   slot = CRC16(key) % 16384                         │
│   slot 7000 → Node B                               │
│                                                      │
│ Add Node D:                                         │
│   Migrate slots from A, B, C to D (rebalance)      │
│   Only migrated slots have cache misses             │
│   Other slots unaffected                           │
│                                                      │
│ Read flow:                                          │
│  App → Redis Client → compute slot → Node B        │
│  HIT: return value                                  │
│  MISS: return nil → App reads DB → SET in Redis    │
│                                                      │
│ Write flow (cache-aside):                           │
│  App → update DB → DEL key in Redis                 │
│  Next read: cache miss → DB read → re-cache        │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Cache-aside with stampede protection**
```python
import redis
import json
import time
import threading

r = redis.Redis()
_local_cache = {}  # L1: in-process cache for hot keys
_local_lock = threading.Lock()

def get_profile(user_id: int) -> dict:
    """
    Cache-aside read with L1 (process-local) and
    L2 (Redis) caches. Stampede protection via lock.
    """
    key = f"profile:{user_id}"

    # L1: process-local cache (ultra-hot keys only)
    # TTL: 2 seconds (reduces Redis calls for hot keys)
    with _local_lock:
        if key in _local_cache:
            cached, expiry = _local_cache[key]
            if time.time() < expiry:
                return cached
            del _local_cache[key]

    # L2: Redis cache
    cached_bytes = r.get(key)
    if cached_bytes:
        profile = json.loads(cached_bytes)
        # Populate L1 for next 2 seconds
        with _local_lock:
            _local_cache[key] = (profile, time.time() + 2)
        return profile

    # Cache miss: use distributed lock to prevent stampede
    # Only one process fills the cache; others wait
    lock_key = f"lock:profile:{user_id}"
    lock_acquired = r.set(lock_key, "1", nx=True, ex=5)

    if lock_acquired:
        try:
            # Read from database
            profile = db_get_profile(user_id)
            if profile:
                # Cache for 5 minutes with jitter
                # Jitter avoids synchronized expiry for
                # profiles fetched at the same time
                import random
                ttl = 300 + random.randint(-30, 30)
                r.setex(key, ttl,
                        json.dumps(profile))
            return profile
        finally:
            r.delete(lock_key)
    else:
        # Another process is filling the cache
        # Brief wait, then retry
        time.sleep(0.05)
        cached_bytes = r.get(key)
        if cached_bytes:
            return json.loads(cached_bytes)
        return db_get_profile(user_id)

def update_profile(user_id: int, updates: dict):
    """Cache-aside write: update DB, invalidate cache."""
    db_update_profile(user_id, updates)
    # Invalidate: next read will fetch fresh from DB
    r.delete(f"profile:{user_id}")
    # Also clear L1
    with _local_lock:
        _local_cache.pop(f"profile:{user_id}", None)
```

**Example 2 - Naive cache-aside without stampede protection (BAD)**
```python
# BAD: No stampede protection - thundering herd on miss
def get_profile_bad(user_id: int) -> dict:
    key = f"profile:{user_id}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    # PROBLEM: If 10,000 requests arrive for the same
    # user_id simultaneously, ALL miss the cache,
    # ALL query the database concurrently.
    # Database receives 10,000 concurrent reads for
    # one row. Potential overload.
    profile = db_get_profile(user_id)
    r.setex(key, 300, json.dumps(profile))
    return profile

# GOOD: Use distributed lock (shown above) to ensure
# only ONE process reads from DB on concurrent miss.
# All other waiters read from cache after lock releases.
```

---

### ⚖️ Comparison Table

| Strategy | Consistency | Write Latency | Complexity | Best For |
|---|---|---|---|---|
| **Cache-aside** | Eventual (TTL lag) | DB only | Simple | Read-heavy, tolerate stale |
| **Write-through** | Strong | DB + cache | Medium | Read+write-heavy, fresh data |
| **Write-behind** | Eventual (async flush) | Cache only | Complex | Write-heavy, low loss tolerance OK |
| **Read-through** | Eventual | DB only | Medium (library) | Transparent to app code |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Cache invalidation is simple (just delete on write) | Cache invalidation is one of the "two hard problems in computer science." Delete-on-write works for simple key-value. But cached objects often contain aggregated data (e.g., a "post with comment count" - updating a comment requires invalidating multiple keys). Design cache objects to minimize the number of events that require invalidation. |
| Redis is always faster than the database | Redis is faster for exact key lookups. But for complex queries (range scans, aggregations, joins), the database may be more appropriate. Do not cache data at a granularity that requires reassembly. Cache pre-aggregated objects: "user profile with follower count" (one Redis key) rather than separate keys that require joining in the application. |
| Setting a longer TTL is safer | Longer TTL means more stale reads. Short TTL (or invalidation on write) is safer for data consistency. Use long TTLs (hours) only for data that rarely changes (static content, user settings). Use short TTLs (seconds to minutes) for data that changes frequently. |

---

### 🚨 Failure Modes & Diagnosis

**Hot Key Overload (Single Cache Node Bottleneck)**

**Symptom:**
One of the 3 Redis cluster nodes has CPU at 99%.
Other nodes are at 10%. Application latency spikes
specifically for requests related to a viral post
(post_id = 999). All 1M simultaneous users are reading
the same cached object (the viral post data), which
hashes to node A.

**Root Cause:** Consistent hashing maps all keys for
the viral post to the same Redis node. That node
becomes a single-server bottleneck regardless of
cluster size.

**Fix - Local L1 cache (process-level):**
```python
# The viral post is read by 1M users simultaneously.
# Even if each request takes 0.5ms in Redis, 1M
# concurrent requests to one node = overload.
# Solution: L1 in-process cache (already shown above)
# Each app server instance caches the hot post locally
# for 2 seconds. Reduces Redis calls by ~99% for hot keys.

# For extreme cases: replicate hot keys across nodes
def get_with_replica_spread(post_id: int) -> dict:
    """
    Read hot keys from multiple replica shards
    to spread load. Use random replica selection.
    """
    import random
    # Instead of one key, store N copies with different
    # key names (different hash slots = different nodes)
    replica_count = 10
    suffix = random.randint(0, replica_count - 1)
    key = f"post:{post_id}:r{suffix}"  # Spreads across nodes
    
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    # On miss: populate all replicas
    post = db_get_post(post_id)
    for i in range(replica_count):
        r.setex(f"post:{post_id}:r{i}", 30,
                json.dumps(post))
    return post
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - cache-aside, write-through, eviction policies
- `Sharding` - consistent hashing is the same concept
  applied to cache nodes

**Builds On This (learn these next):**
- `Hot Shard` - hot key problem in cache is the same
  as the hot shard problem in databases
- `Cache Invalidation Strategies` - detailed strategies
  for keeping cache consistent with the database

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGY    │ Cache-aside default. Write-through for    │
│             │ fresh reads. Write-behind for fast writes.│
├─────────────┼──────────────────────────────────────────  │
│ HASHING     │ Redis Cluster: 16,384 hash slots.         │
│             │ Adding nodes: only affected slots move.   │
├─────────────┼──────────────────────────────────────────  │
│ EVICTION    │ LRU: temporal locality. LFU: frequency.  │
│             │ Keep utilization < 70% to avoid cascades.│
├─────────────┼──────────────────────────────────────────  │
│ TTL         │ Jitter TTL to prevent synchronized expiry.│
│             │ profile: 5 min. static: 1 hour.          │
├─────────────┼──────────────────────────────────────────  │
│ STAMPEDE    │ Redis SET NX lock on cache miss.          │
│             │ One process fills; others wait and retry. │
├─────────────┼──────────────────────────────────────────  │
│ HOT KEY     │ L1 in-process cache (2s TTL).            │
│             │ Or spread: N replica keys across nodes.   │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Consistent hashing + LRU + cache-aside  │
│             │  + stampede protection = production cache"│
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Social Network Design → E-Commerce Design │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Cache-aside is the default pattern. Read: check cache →
   miss → read DB → write cache. Write: update DB → delete
   cache key (invalidate). TTL as a safety net. Simple and
   effective for read-heavy workloads.
2. Consistent hashing (Redis Cluster: 16,384 slots) means
   adding/removing a cache node migrates only a fraction
   of keys. Modulo hashing invalidates 80%+ of keys when
   adding one node.
3. Stampede protection: use Redis SET NX on cache miss so
   only one process fills the cache from the database.
   All other concurrent requests wait briefly and read
   from the freshly populated cache. Prevents database
   overload when a popular key expires.

**Interview one-liner:**
"Distributed cache: Redis Cluster with consistent hashing (16,384 slots).
Cache-aside: read → Redis GET; on miss → DB query → Redis SETEX. Write →
DB update → Redis DEL (invalidate). Stampede protection: Redis SET NX lock
on miss (one process fills; others wait). TTL with jitter (avoid synchronized
expiry). Hot key mitigation: L1 in-process cache per app server (2s TTL,
handles viral content without Redis overload). Eviction: LRU for temporal
locality, LFU for frequency-based hotness. Keep cluster utilization < 70%
to prevent eviction cascades."
