---
id: SYD-069
title: Cache Invalidation Strategies
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-031, SYD-064
used_by: ""
related: SYD-031, SYD-064, SYD-052, SYD-067, SYD-049
tags:
  - architecture
  - caching
  - cache-invalidation
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /syd/cache-invalidation-strategies/
---

# SYD-069 - Cache Invalidation Strategies

⚡ TL;DR - Cache invalidation is one of the two hard
problems in computer science (the other: naming things).
A cached value is wrong when the underlying data changes
and the cache is not updated. The four core strategies:
(1) TTL (time-to-live) - expire after N seconds,
accept staleness; (2) write-through - update cache and
database together; (3) write-behind - update cache first,
database asynchronously; (4) invalidate-on-write - delete
(not update) the cache key on writes, let it be
repopulated on next read. The dangerous anti-pattern:
cache poisoning - a stale or wrong value gets cached
and serves incorrect data to all users until it expires.

| #069 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching (System Design), What is a Cache (Conceptual) | |
| **Related:** | Caching, What is a Cache, Distributed Cache Design, CDN Architecture Pattern, Video Streaming Design | |

---

### 🔥 The Problem This Solves

User updates their profile name. The user's data
is cached in Redis (TTL: 24 hours). The profile page
reads from cache. For the next 24 hours: every user
who views the profile sees the OLD name. The cache
is serving stale data. The database has the correct
value; the cache does not. This is the cache coherence
problem. Every caching system must decide: when the
underlying data changes, how quickly must the cached
copy be updated (or removed)?

---

### 📘 Textbook Definition

**Cache invalidation:** The process of removing or
updating a cached entry when the underlying data
changes, to prevent stale data from being served.

**Cache coherence:** The property that the cached value
matches the actual value in the source of truth (database).

**Staleness:** The degree to which a cached value
differs from the current database value. Acceptable
staleness depends on the use case: product description
(minutes OK), bank balance (zero staleness acceptable).

**TTL (time-to-live):** A cached entry automatically
expires after N seconds. The system accepts that data
may be stale for up to N seconds. After expiry: next
read fetches fresh from source and caches the result.

**Write-through cache:** On write, update both the cache
and the database atomically (or in sequence). Cache
is always fresh, but writes are slower (wait for both).

**Write-behind (write-back) cache:** On write, update
only the cache immediately; flush to database
asynchronously. Fastest writes; risk of data loss if
cache fails before flush.

**Cache-aside (lazy loading):** Application manages
cache. On read: check cache (hit: return). On miss:
fetch from DB, populate cache, return. On write:
write to DB, then DELETE the cache key (not update).
The key is deleted, not updated, to avoid race conditions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When data changes, make the cache reflect reality.
Choose between: accept staleness (TTL), keep in sync
on writes (write-through), or evict and reload (cache-aside).

**One analogy:**
> A reference book on a shelf:
>
> Book = cache. Library database = source of truth.
> Book may have old information (published 2019).
> Strategies:
>
> TTL: throw out the book every year and print a fresh
> one. Always < 1 year stale.
>
> Write-through: whenever any fact changes, reprinting
> the relevant page immediately. Always current.
> Slow and expensive if updates are frequent.
>
> Cache-aside: remove the book when it becomes wrong.
> Next person who needs it prints a fresh copy.
> The shelf may be empty briefly (cache miss penalty).
>
> Write-behind: update the book immediately (fast read),
> but submit database corrections overnight (async).
> Risk: if the library burns down overnight, your
> corrections are lost.

**One insight:**
The most important rule of cache invalidation:
**delete the cache key on writes, don't update it.**
Updating the cache on write creates a race condition:
two concurrent writes can interleave, leaving the
cache with an older version than the database. Deleting
the cache entry forces the next read to re-populate
from the database (fresh data). The brief cache miss
after deletion is a small price for correctness.

---

### 🔩 First Principles Explanation

**THE FOUR CORE STRATEGIES:**

**1. TTL (Passive Invalidation)**
```
Cache entry lives for N seconds, then expires.
On expiry: next read → DB miss → repopulate cache.

Pro: Simplest. No coupling between write and cache.
     Works even if writer does not know about cache.
Con: Stale for up to TTL seconds after write.
     "Last writer" problem: if TTL is 5 minutes,
     a product price update takes 5 minutes to
     appear in the cache.

Choose when: staleness of a few minutes/hours is
acceptable. Product catalog, trending lists, weather.
```

**2. Cache-Aside with Delete (Invalidate-On-Write)**
```
Read path: if cache miss → DB → store in cache.
Write path: write to DB → DELETE cache key.
           (NOT: update cache with new value)

Why delete, not update?

Race condition with update:
  T1: User A updates profile. Writes new data to DB.
  T2: User B reads profile. DB miss. Reads DB: gets
      NEW value. About to SET cache.
  T3: User A's write thread: SET cache = new value.
  T4: User B: SET cache = (old DB value read at T2).
  Result: Cache has STALE value. DB is correct.
  
  Problem: T2 and T3 interleaved. T4 overwrote T3.

With delete:
  T1: User A writes to DB. DELETE cache key.
  T2: User B reads. Cache miss. DB fetch: gets NEW value.
  T4: User B: SET cache = new (correct) value.
  Result: Cache is correct. No race condition.

Pro: Correct under concurrent writes.
     Simple to implement.
Con: Brief cache miss period after delete.
     Two-trip cost: DB write + cache delete.
     Stampede: many readers hit DB simultaneously
     on popular key after delete.
     (Fix: request coalescing or mutex on cache miss)
```

**3. Write-Through**
```
Every write: update DB AND update cache atomically.
Read: always hits cache (no misses except cold start).

Pro: Cache always consistent. Reads never miss.
Con: Write latency: must update both cache + DB.
     Cache contains ALL data, even rarely read.
     Wasted memory for write-only data.
     Atomic update problem: if DB write succeeds
     but cache update fails → DB and cache diverge.
     (Fix: 2PC or eventual consistency with TTL
     as fallback cleanup)

Use when: read-heavy workloads; every record is
          frequently read; low tolerance for cache misses.
          Example: session data (written once on login,
          read on every request).
```

**4. Write-Behind (Write-Back)**
```
Write: update cache only (instant ACK to client).
       Queue DB write for async flush (batch).
Read: hits cache (fast).

Pro: Fastest write performance.
     Batching reduces DB write pressure.
     Useful for counters (increment in cache,
     flush to DB every 60 seconds).
Con: Data loss if cache crashes before DB flush.
     Not suitable for financial transactions.
     Cache becomes single source of truth during
     flush window.

Use when: write-heavy, eventual consistency OK.
          Like/view counters, analytics events,
          game scores.
```

**CACHE STAMPEDE / THUNDERING HERD:**
```
Popular cache key (product: 10M views/day) expires.
Thousands of simultaneous reads: all miss.
All 1,000 go to DB simultaneously.
DB: overwhelmed. Timeouts. Cascading failure.

Solutions:
  1. Probabilistic early expiration (XFetch algorithm):
     Slightly before TTL expiry, probabilistically
     recompute the cache. Prevents simultaneous expiry.
  
  2. Mutex/lock on cache miss:
     First thread to miss acquires a lock.
     Other threads wait for the lock or return stale.
     Lock holder: fetches DB, updates cache, releases.
     Others: get fresh value from cache.
  
  3. Serve stale while revalidating:
     Return expired (stale) value immediately.
     Background: one thread recomputes and updates.
     Users see slightly stale data (acceptable for most).
     HTTP: Cache-Control: stale-while-revalidate=60.
  
  4. Extended TTL (jitter):
     Instead of: TTL = 3600 seconds.
     Use: TTL = 3600 + random(0, 300) seconds.
     Different entries expire at different times.
     Stagger recomputations. Reduces spike.
```

---

### 🧪 Thought Experiment

**Bank Account Balance**

"What is the balance?" is read 100x per day.
"Transfer money" happens 1-2 times per day.

Cache strategy comparison:

TTL = 1 hour:
  After a transfer, balance is wrong for up to 1 hour.
  Customer sees wrong balance. Unacceptable for banking.
  Cannot use TTL for financial data.

Cache-aside with delete:
  Transfer: DB write + DELETE cache key.
  Next balance read: DB miss → correct fresh balance.
  Correct. Very brief cache miss period (< 1ms).
  Acceptable.

Write-through:
  Transfer: DB write + cache update atomically.
  If DB write succeeds, cache update fails:
  DB: $900. Cache: $1000 (old). User sees $1000.
  Requires careful atomic semantics or fallback TTL.
  Harder to get right.

Correct choice: cache-aside with delete + short
or no TTL fallback. After DELETE, DB is ground truth.
Next read always gets fresh DB value. No staleness.
For critical financial data: consider very short TTL
(30 seconds) as a safety net, not primary strategy.

---

### 🧠 Mental Model / Analogy

> Cache invalidation strategies are like keeping a
> whiteboard up to date with real-world prices:
>
> TTL: Erase and rewrite the whole board every 15 min.
>   Slightly old between erasures. Simple.
>
> Cache-aside (delete): Erase just the entry that
>   changed. Next customer who asks gets the updated
>   price from the source. Brief moment with no price
>   on board (cache miss).
>
> Write-through: Whenever price changes: update source
>   AND board simultaneously. Board always current.
>   Updating takes two steps every time.
>
> Write-behind: Update board instantly. Update source
>   at end of day (batch). Board is always fresh;
>   source may be hours behind. If board is wiped
>   before EOD sync: source never gets the updates.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you save something in a fast temporary location
(cache), and the original data changes, the temporary
copy may be wrong. Cache invalidation is the process
of making sure the temporary copy gets updated or
removed when the original changes.

**Level 2 - How to use it (junior developer):**
Use TTL for data where slight staleness is acceptable
(5-60 minutes). For data that must be current after
writes: delete the cache key after writing to the
database. Don't try to update the cache on writes
(race condition). Use Redis `DEL` or `EXPIRE` to
invalidate. Monitor cache hit rate.

**Level 3 - How it works (mid-level engineer):**
Cache-aside with delete: the safest pattern for general
use. Write to DB, then DEL the cache key. Avoids the
write race condition. Thundering herd: prevent with
jitter TTL, stale-while-revalidate, or distributed
mutex (Redlock or simple Redis SETNX). Write-through:
update cache and DB atomically; watch for partial failures.
Write-behind: fast writes to cache, async flush to DB;
data loss risk if cache fails.

**Level 4 - Why it was designed this way (senior/staff):**
The "delete not update" rule for cache-aside exists
because writes frequently come with read-modify-write
semantics (e.g., "increment user's post count"). If
two writes happen concurrently, setting the cache
after each write can leave the cache with a value that
is neither the pre-write nor post-write state - it
reflects the order of cache-set operations, which
may differ from the order of DB commits. Deletion
removes the corrupted intermediate state entirely,
forcing a fresh read on next access. Facebook described
this at scale in their Memcached paper (2013): "lease"
tokens granted to the first cache-miss reader prevent
stampedes and stale sets from concurrent writers.

**Level 5 - Mastery (distinguished engineer):**
Twitter's timeline caching (2012-2015) illustrates the
complexity at scale: user timeline was pre-computed and
cached per user. When a user posted a tweet, the system
needed to invalidate or update the timeline cache of
all their followers (fan-out-on-write). For celebrities
with 50M followers, this was prohibitively expensive:
50M cache invalidations per tweet. Their solution:
fan-out-on-write for normal users, but fan-out-on-read
(lazy loading) for celebrity tweets. This hybrid approach
means most timelines are cache-consistent immediately;
celebrity tweet propagation is deferred. The insight:
cache invalidation strategy is not one-size-fits-all
even within the same system - model the write amplification
for your access patterns and choose per data type.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CACHE-ASIDE (MOST COMMON)                           │
│                                                      │
│ READ path:                                          │
│   App → Redis GET user:123                         │
│   Hit: return cached user                          │
│   Miss: App → DB SELECT user WHERE id=123         │
│          → Redis SET user:123 {data} EX 3600      │
│          → return fresh data                       │
│                                                      │
│ WRITE path:                                         │
│   App → DB UPDATE users SET name=... WHERE id=123  │
│       → Redis DEL user:123  (NOT SET!)             │
│   Next read: cache miss → fresh DB fetch           │
│                                                      │
│ THUNDERING HERD PREVENTION:                        │
│   Redis SET user:123:lock 1 EX 5 NX  (SETNX)     │
│   If lock acquired (NX=new only):                 │
│     Fetch DB, SET cache, DEL lock                 │
│   Else (lock exists = someone is fetching):       │
│     Wait 10ms, retry GET → should hit now        │
│     Or return stale value if TTL recently expired │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Cache-aside with delete (Python/Redis)**
```python
import redis
import json
from typing import Optional

r = redis.Redis(host="redis.internal", port=6379,
                decode_responses=True)

CACHE_TTL = 3600  # 1 hour

def get_user(user_id: int) -> Optional[dict]:
    """Read: cache-aside pattern"""
    cache_key = f"user:{user_id}"
    
    # 1. Try cache first
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 2. Cache miss: fetch from DB
    user = db.query("SELECT * FROM users WHERE id = %s",
                    [user_id])
    if not user:
        return None
    
    # 3. Populate cache with TTL
    r.setex(cache_key, CACHE_TTL, json.dumps(user))
    return user

def update_user(user_id: int, name: str, email: str):
    """Write: update DB, DELETE cache key (not SET!)"""
    # 1. Update source of truth
    db.execute(
        "UPDATE users SET name=%s, email=%s WHERE id=%s",
        [name, email, user_id]
    )
    
    # 2. DELETE cache key - NOT: r.set(cache_key, new_data)
    # Deleting avoids race condition where two concurrent
    # writes leave cache with an older version.
    cache_key = f"user:{user_id}"
    r.delete(cache_key)
    
    # Next read will get fresh data from DB and re-cache.

# BAD: updating cache on write (race condition risk)
def update_user_bad(user_id: int, name: str):
    db.execute("UPDATE users SET name=%s WHERE id=%s",
               [name, user_id])
    # BAD: if two updates happen concurrently,
    # the second SET may store an older value:
    # T1 update: DB=name2, about to SET cache
    # T2 update: DB=name3, SET cache=name3 ← later write
    # T1: SET cache=name2 ← overwrites newer value!
    # Cache: name2. DB: name3. Stale!
    user = {"id": user_id, "name": name}
    r.setex(f"user:{user_id}", CACHE_TTL,
            json.dumps(user))  # RACE CONDITION!
```

**Example 2 - Thundering herd prevention with mutex**
```python
import time

def get_user_safe(user_id: int) -> Optional[dict]:
    """Cache-aside with thundering herd protection"""
    cache_key = f"user:{user_id}"
    lock_key = f"user:{user_id}:lock"
    
    # Try cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Try to acquire "fetch lock" (NX = only set if not exists)
    # Lock TTL = 5s (prevents stuck locks)
    acquired = r.set(lock_key, "1", ex=5, nx=True)
    
    if acquired:
        try:
            # This thread fetches from DB
            user = db.query(
                "SELECT * FROM users WHERE id = %s",
                [user_id])
            if user:
                r.setex(cache_key, CACHE_TTL,
                        json.dumps(user))
            return user
        finally:
            r.delete(lock_key)
    else:
        # Another thread is fetching.
        # Wait briefly and retry cache.
        for _ in range(10):
            time.sleep(0.05)  # 50ms
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)
        # Fallback: fetch from DB directly if still no cache
        return db.query(
            "SELECT * FROM users WHERE id = %s", [user_id])

# TTL jitter: different entries expire at different times
import random

def set_with_jitter(key: str, value: str,
                    base_ttl: int = 3600,
                    jitter: int = 300):
    """Add random jitter to TTL to prevent stampede"""
    ttl = base_ttl + random.randint(0, jitter)
    r.setex(key, ttl, value)
```

**Example 3 - Write-through pattern**
```python
from contextlib import contextmanager

@contextmanager
def write_through_user(user_id: int):
    """
    Context manager: write to DB and cache together.
    If cache update fails: log but continue
    (TTL will clean up; DB is source of truth).
    """
    yield  # Execute the write block
    # Post-write hook: re-populate cache with fresh DB data
    user = db.query(
        "SELECT * FROM users WHERE id = %s", [user_id])
    if user:
        cache_key = f"user:{user_id}"
        try:
            r.setex(cache_key, CACHE_TTL, json.dumps(user))
        except redis.RedisError as e:
            # Cache update failed: log, but don't fail
            # the write. TTL will expire old value.
            logger.warning(
                f"Cache update failed for user {user_id}: {e}")

def update_user_write_through(user_id: int, name: str):
    """Write-through: DB and cache both updated after write"""
    with write_through_user(user_id):
        db.execute(
            "UPDATE users SET name=%s WHERE id=%s",
            [name, user_id])
    # After context manager: cache has fresh value from DB
```

---

### ⚖️ Comparison Table

| Strategy | Staleness | Write Performance | Complexity | Data Loss Risk | Best For |
|---|---|---|---|---|---|
| **TTL only** | Up to TTL duration | Fast (no cache update needed) | Low | None | Rarely-updated data, public API responses |
| **Cache-aside + delete** | Brief (cache miss period) | Slight overhead (DEL after write) | Low-Medium | None | General purpose, user data |
| **Write-through** | Zero | Slower (update cache + DB) | Medium | None | Session data, read-heavy records |
| **Write-behind** | Zero | Fastest (cache only) | High | Yes (crash before flush) | Counters, analytics, view counts |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Cache invalidation is just setting an expiry time | TTL alone does not ensure freshness - it only guarantees that the cache will eventually be updated. If the TTL is 1 hour and data changes every minute, users see stale data for most of that hour. True cache invalidation means actively invalidating the cache entry on writes. TTL should be a safety net, not the primary mechanism. |
| Update cache on write (instead of delete) is safe | A concurrent read-modify-write race can leave the cache with a value older than the database. Two writes interleaving: write-A sets cache to value-A; write-B sets cache to value-B before A. Then A sets cache to value-A (stale). DB has value-B; cache has value-A. Use DELETE-not-SET to avoid this. |
| Cache consistency is an application concern only | At scale, CDN layers, browser caches, and intermediate proxies all cache responses. Getting a correct value into your Redis cache but continuing to serve a stale value from a CDN edge (which cached the old HTTP response) is a real failure. End-to-end cache invalidation must account for every caching layer, from application cache to CDN to browser. |

---

### 🚨 Failure Modes & Diagnosis

**Cache Poisoning via Stale Set**

**Symptom:**
After a product price update, some users see the old
price. Clearing Redis manually fixes it temporarily.
The problem recurs. Price is consistently wrong for
5-10 seconds after every update.

**Root Cause:**
Write path: write to DB, then SET cache = new value.
Two concurrent update requests race:
  T1: Slow update (long-running txn). DB not committed.
  T2: Faster update. DB committed. DEL + SET cache=new.
  T1: DB commits (old data). SET cache=old. Overwrites T2!
Cache has old price. DB has new price.

**Fix:**
```python
# Change write path from SET to DEL
def update_price_bad(product_id, price):
    db.execute("UPDATE products SET price=%s...", [price])
    cache.set(f"product:{product_id}",
              json.dumps({"price": price}),
              ex=3600)  # RACE: may set stale value

def update_price_good(product_id, price):
    db.execute("UPDATE products SET price=%s...", [price])
    cache.delete(f"product:{product_id}")  # DEL not SET
    # Next read: DB miss → fresh DB fetch → correct price

# Additional safeguard: add version to cache key
def get_product(product_id):
    # Use "product:v2:{id}" if you suspect stale caches
    # from a bad deploy; bump version to invalidate all
    version = "v2"
    cache_key = f"product:{version}:{product_id}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    product = db.query(
        "SELECT * FROM products WHERE id = %s",
        [product_id])
    cache.setex(cache_key, 3600, json.dumps(product))
    return product
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching (System Design)` - cache patterns: read-through,
  write-through, eviction policies
- `What is a Cache (Conceptual)` - foundational cache
  concepts (hit/miss, TTL, eviction)

**Builds On This (learn these next):**
- `Distributed Cache Design` - applying invalidation
  strategies in a distributed Redis/Memcached cluster
- `CDN Architecture Pattern` - CDN-level cache
  invalidation (purge APIs, content-hash versioning)
- `Video Streaming Design` - invalidation for media
  segment caches and manifest files

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE RULE   │ On write: DELETE cache key. Never SET.   │
│             │ Avoids concurrent write race condition.  │
├─────────────┼──────────────────────────────────────────  │
│ TTL         │ Safety net, not primary strategy.        │
│             │ Use short TTL for dynamic; 1yr static.  │
├─────────────┼──────────────────────────────────────────  │
│ STAMPEDE    │ On popular key expiry: thousands miss.  │
│             │ Fix: mutex lock, jitter TTL, stale-while│
├─────────────┼──────────────────────────────────────────  │
│ WRITE-THRU  │ Write cache + DB. No misses. Slower     │
│             │ writes. Atomicity: hard to guarantee.   │
├─────────────┼──────────────────────────────────────────  │
│ WRITE-BEHIND│ Write cache only; async flush to DB.   │
│             │ Fastest. Risk: data loss on crash.     │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "DEL not SET. TTL as backup. Jitter    │
│             │  to prevent stampede."                 │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Blob Storage Design                      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. On writes: DELETE the cache key, never SET a new value.
   Deleting prevents the concurrent-write race condition
   where a slower writer overwrites a newer cached value.
   The brief cache miss after deletion is correct behavior.
2. Thundering herd: when a popular cache key expires,
   many readers stampede the database simultaneously.
   Prevent with TTL jitter (random ±5 minutes on expiry)
   or a distributed mutex (Redis SETNX) so only one
   request fetches from DB while others wait.
3. End-to-end invalidation: your Redis may be fresh but
   CDN or browser may still serve stale data. Set correct
   Cache-Control headers + CDN purge API calls for complete
   invalidation across all caching layers.

**Interview one-liner:**
"Cache invalidation: on writes, DELETE cache key (not SET) to avoid the
concurrent-write race condition where a slower thread overwrites a newer cached value.
TTL is a safety net, not the primary strategy. Strategies: cache-aside with delete
(general purpose), write-through (read-heavy, zero staleness), write-behind (fastest
writes, data loss risk). Thundering herd: jitter TTL + distributed mutex (Redis SETNX).
CDN invalidation: content-hash versioning for static assets; purge API for dynamic.
End-to-end: Redis cache + CDN + browser cache headers must all be coherent."
