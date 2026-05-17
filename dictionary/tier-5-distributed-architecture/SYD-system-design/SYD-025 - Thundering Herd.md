---
id: SYD-025
title: Thundering Herd
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-014
used_by: ""
related: SYD-008, SYD-014, SYD-027, SYD-028, SYD-029
tags:
  - architecture
  - reliability
  - performance
  - cache
  - distributed-systems
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /syd/thundering-herd/
---

# SYD-025 - Thundering Herd

⚡ TL;DR - The thundering herd problem occurs when a
large number of processes or requests are simultaneously
awakened or triggered by a single event, all competing
for the same resource at the same time. Classic examples:
cache expiry (all requests hit the database simultaneously
when a popular cache key expires) and server restart
(all clients reconnect at once). The solutions are
probabilistic cache expiration, cache locking/stampede
protection, and jitter in retry/reconnect logic.

| #025 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Auto Scaling | |
| **Used by:** | (defensive design pattern) | |
| **Related:** | Load Balancing, Auto Scaling, Capacity Planning, Rate Limiting, Token Bucket | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Redis cache stores the result of an expensive DB
query for a popular product page. TTL = 60 seconds.
The key expires. At that exact moment, 10,000
concurrent requests are all serving that product page.
All 10,000 requests simultaneously call the database
to regenerate the cache. The database (configured
for 500 concurrent connections) is hammered with
10,000 queries, times out, and goes down. The system
that was supposed to be protected by the cache just
took down the database.

**THE BREAKDOWN:**
The cache was protecting the database. The moment
the cache key expired, the protection collapsed
simultaneously for all concurrent users. The event
(key expiry) produced a correlated spike, not a
gradual ramp. Correlated spikes are worse than
gradual load increases because there is no ramp-up
time for auto-scaling to respond.

---

### 📘 Textbook Definition

**Thundering herd:** A failure mode in distributed
systems where a large number of processes (or requests)
are simultaneously triggered by the same event and
compete for the same shared resource. The sudden
correlated demand overloads the resource, often
causing it to fail, which can cascade. Named after
stampeding animals that collectively destroy what
they rush toward.

**Classic triggering events:**
- Cache key expiry (all requests miss simultaneously)
- Server restart (all clients reconnect simultaneously)
- Scheduled job completion (N workers awaken simultaneously)
- New item in queue (all idle consumers poll simultaneously)
- Auto-scaled fleet comes online (all nodes check
  in with the configuration server simultaneously)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When many requests hit a shared resource at the exact
same time (triggered by the same event), the resource
collapses under the simultaneous load.

**One analogy:**
> A store opens at 9am. 500 people have been waiting
> outside since 8am. At exactly 9:00:00, all 500
> rush through the doors simultaneously. The checkout
> system crashes under the sudden load.
>
> Compare to: people arriving randomly throughout
> the day (uniform load) - the checkout handles it
> fine. The problem is the correlated arrival at a
> single event (store opens).

**One insight:**
Thundering herd is fundamentally a correlation
problem. Individual requests are fine; correlated
requests at the same instant overwhelm shared
resources. Solutions add randomness or coordination
to break the correlation.

---

### 🔩 First Principles Explanation

**WHY CACHE STAMPEDE IS THE CANONICAL CASE:**

```
Cache TTL = 60s. Key: "product:123:details"
Concurrent users at cache hit time: 10,000/second.

Normal (key present in cache):
  10,000 req/s → cache → no DB calls

At second 61 (key expired):
  10,000 req/s → cache MISS → 10,000 DB queries

DB capacity: 100 queries/second
DB instantly receives: 10,000 queries
DB connection pool exhausted → queries timeout
Cache cannot be populated (DB failing) → more misses
Cascade: new requests also miss → more DB load
System death spiral
```

**THE SOLUTIONS:**

```
Solution 1: Cache Lock (Mutex/Thundering Herd Lock)
  - First request on cache miss acquires a lock
  - All other concurrent requests wait for lock
  - Lock holder regenerates cache, releases lock
  - Others read the newly populated cache
  - DB impact: 1 query, not 10,000
  - Tradeoff: lock holder must succeed (no timeout
    protection if lock holder also fails)

Solution 2: Probabilistic Early Expiry (PER)
  - Before TTL expires, some requests "pre-expire"
    the key probabilistically
  - Formula: should_recompute = -ttl_remaining
    > β * delta * ln(random.uniform(0,1))
    where β is tuning parameter, delta is compute time
  - Some requests regenerate the cache early, before
    the key actually expires
  - Others read the (still valid) key
  - No coordination needed; stateless

Solution 3: Background Refresh
  - A background job regenerates cache keys before
    they expire (proactive)
  - TTL is long; background job refreshes every 50s
  - Actual expiry (TTL) never reached under normal ops
  - Problem: background job is a new component to fail

Solution 4: Stale-While-Revalidate
  - Expired key is served stale while one request
    regenerates it in background
  - Client gets response (stale), backend regenerates
  - No wait, no stampede, slight staleness

Solution 5: Jitter on TTL
  - Instead of TTL = 60s for all keys
  - TTL = 60s + random(0, 10s)
  - Keys expire at different times → no synchronized mass
    expiry → DB load spreads over time
```

**RECONNECT THUNDERING HERD (clients):**

```
Problem: Server restarts. 50,000 clients all have
TCP timeout = 30s. At exactly t=30, all 50,000
reconnect simultaneously.

Solution: Exponential backoff with jitter
  BAD: reconnect at fixed t=30 (all reconnect together)
  GOOD: reconnect at t = base_delay
    × 2^(attempt) + random(0, base_delay)
  Result: reconnects spread over minutes,
  not concentrated at one instant.
```

**THE TRADE-OFFS:**
**Cache lock:** Eliminates DB hammering. Adds lock
latency for all waiting requests. Lock holder failure
can leave others waiting indefinitely (need timeout).
**Probabilistic early expiry:** No coordination,
no lock. Some DB load before expiry. Tuning parameter
(β) needs calibration.
**Jitter on TTL:** Simplest. Requires no code changes
to cache logic. Slightly reduces cache hit rate
(keys expire sooner on average).

---

### 🧪 Thought Experiment

**SCENARIO: Redis cluster restart → all nodes re-register**

A Redis cluster has 200 clients (microservices).
The cluster is restarted for maintenance. All 200
clients receive a connection error simultaneously.
All 200 implement a simple retry: wait 5 seconds,
reconnect.

At t=5 seconds: all 200 clients reconnect simultaneously.
Redis startup is still completing initialization.
200 simultaneous connection attempts overload the
new Redis startup. Redis crashes again.

At t=10: all 200 retry again (still synchronized).
Redis crashes again. Repeat indefinitely.
This is a thundering herd that prevents the system
from ever recovering.

**SOLUTION: Jitter + exponential backoff**
Each client:
```
attempt = 1
delay = min(base_delay × 2^attempt + random(0, base_delay),
            max_delay)
```
Client reconnect times spread from 5s to 60s, not
all at exactly 5s. Redis gets gradual reconnect load,
has time to initialize, and recovers successfully.

**THE INSIGHT:**
Synchronized retries are as dangerous as synchronized
requests. Any situation where many components respond
to the same failure event with the same timing needs
jitter. This is a universal pattern for distributed
systems: whenever adding retry logic, always add
jitter. Exponential backoff without jitter still
has thundering herd if all retriers started at the
same time.

---

### 🧠 Mental Model / Analogy

> Cache stampede is like a traffic light at a
> highway on-ramp:
> - Normal (green light): cars trickle onto the
>   highway gradually (metered by the light timing)
> - Green light failure: ramp metering off, all
>   queued cars enter simultaneously → gridlock
>
> The cache is the metering light. When it fails
> (cache miss), all cars hit the highway at once.
> The solutions:
> - Jitter: random green-light times, not synchronized
> - Lock: only one car gets the green; others wait
> - Early expiry: re-meter before the scheduled expiry

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When a cached item expires, ALL requests that were
relying on it hit the database at the same moment.
The database gets overwhelmed. The solution: prevent
them from all hitting at the same moment.

**Level 2 - How to use it (junior developer):**
Always add jitter (random delay) to cache TTLs and
retry delays. `TTL = base_ttl + random(0, jitter_range)`.
Never use fixed TTL for all keys of the same type.

**Level 3 - How it works (mid-level engineer):**
For high-concurrency cache misses: implement stampede
protection. In Python: use a distributed lock (Redis
SETNX) so only one request regenerates the cache.
Others wait briefly or serve stale data. In Go/Java:
singleflight package (Go) or Guava LoadingCache
with refresh semantics (Java).

**Level 4 - Why it was designed this way (senior/staff):**
The probabilistic early expiry (PER) algorithm is
the theoretically clean solution: it requires no
coordination between clients, is tunable by a single
parameter (β), and provides a natural trade-off
between load distribution and staleness. The insight:
model cache regeneration as a stochastic process
where each request independently decides whether to
refresh based on remaining TTL and historical
regeneration cost.

**Level 5 - Mastery (distinguished engineer):**
The thundering herd problem is a special case of
the synchronization problem in distributed systems:
correlated timing is more dangerous than equal total
load. The same total number of requests distributed
randomly over time is handled easily by a system;
the same requests arriving at the same millisecond
overwhelms it. The design principle: break
correlations. This applies to cache TTL (jitter),
retries (jitter), reconnect (backoff + jitter),
scheduled jobs (randomize start times), and even
batch processing (randomize batch sizes). Any
mechanism that can cause coordinated simultaneous
actions must be explicitly decoupled.

---

### ⚙️ How It Works (Mechanism)

**Go singleflight: serialize concurrent calls**

```
┌──────────────────────────────────────────────────────┐
│ singleflight.Group: deduplicate concurrent calls    │
│                                                      │
│  10,000 concurrent requests for "product:123"        │
│                                                      │
│  Request 1 → cache MISS → singleflight.Do("p:123")  │
│  Request 2 → cache MISS → singleflight.Do("p:123")  │
│    ↓ (request 1 already in flight)                  │
│    ↓ request 2 WAITS for request 1's result         │
│  ...                                                 │
│  Request N → same: wait for request 1               │
│                                                      │
│  Request 1 completes: 1 DB query executed           │
│  All N requests get the same result from 1 query    │
│  DB impact: 1 query, not 10,000                     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - BAD: Cache miss with no stampede protection**
```python
# BAD: All concurrent requests hit DB on cache miss
import redis

r = redis.Redis()

def get_product(product_id):
    key = f"product:{product_id}"
    data = r.get(key)

    if data is None:
        # PROBLEM: All 10,000 concurrent requests
        # for this product reach here simultaneously
        # when the key expires.
        data = expensive_db_query(product_id)
        r.setex(key, 60, data)  # Fixed TTL: all expire at once
    return data
```

**Example 2 - GOOD: Stampede protection + TTL jitter**
```python
# GOOD: Cache lock (stampede protection) + jitter on TTL
import redis
import random
import time

r = redis.Redis()

def get_product(product_id):
    key = f"product:{product_id}"
    lock_key = f"lock:product:{product_id}"

    # Try to get from cache
    data = r.get(key)
    if data:
        return data

    # Cache miss: acquire lock to regenerate
    # Only one worker regenerates; others wait briefly
    # NX = only set if not exists, PX = expire in ms
    acquired = r.set(
        lock_key, "1", nx=True, px=5000  # 5s lock TTL
    )

    if acquired:
        try:
            # Double-check: another worker may have
            # populated while we were acquiring the lock
            data = r.get(key)
            if data:
                return data

            # Regenerate cache
            data = expensive_db_query(product_id)

            # Jitter: spread expiry over 50-70s window
            # Different keys expire at different times
            ttl = 60 + random.randint(-10, 10)
            r.setex(key, ttl, data)
            return data
        finally:
            r.delete(lock_key)
    else:
        # Lock not acquired: another request is regenerating
        # Wait briefly and retry from cache
        # (serve stale or wait a short time)
        time.sleep(0.1)
        data = r.get(key)
        if data:
            return data
        # Fallback: serve directly from DB if still missing
        return expensive_db_query(product_id)
```

**Example 3 - Retry with exponential backoff + jitter**
```java
// GOOD: Reconnect with jitter to prevent thundering herd
// Use when implementing client reconnect logic

public class RetryWithJitter {
    private static final int BASE_DELAY_MS = 1000;
    private static final int MAX_DELAY_MS = 30_000;
    private final Random rng = new Random();

    /**
     * Calculate delay with full jitter.
     * "Full jitter" (AWS recommendation) is better than
     * "equal jitter" for preventing thundering herd.
     */
    public long getDelayMs(int attempt) {
        // Exponential backoff cap
        long cap = Math.min(
            MAX_DELAY_MS,
            (long) BASE_DELAY_MS * (1L << attempt)
        );
        // Full jitter: random between 0 and cap
        // Not: cap/2 + random(0, cap/2) (equal jitter)
        // Full jitter spreads load more uniformly
        return (long) (rng.nextDouble() * cap);
    }

    public void connectWithRetry(Runnable connectFn,
                                  int maxAttempts) {
        for (int attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                connectFn.run();
                return;  // Success
            } catch (ConnectionException e) {
                if (attempt == maxAttempts - 1) throw e;

                long delay = getDelayMs(attempt);
                log.warn("Connection failed (attempt {}). "
                    + "Retrying in {}ms", attempt + 1, delay);
                Thread.sleep(delay);
            }
        }
    }
}
// 50,000 clients all disconnected at t=0:
// attempt=0: delay = random(0, 1000ms)
// attempt=1: delay = random(0, 2000ms)
// attempt=2: delay = random(0, 4000ms)
// → reconnects spread over 0-7s window, not at one moment
```

---

### ⚖️ Comparison Table

| Solution | DB Protection | Code Complexity | Staleness Risk | Coordination |
|---|---|---|---|---|
| No protection (BAD) | None | None | None | None |
| TTL jitter | Partial (spreads expiry) | Very low | Minimal | None |
| Cache lock (mutex) | Full (1 query) | Medium | Wait latency | Distributed lock |
| Singleflight | Full (1 query) | Low (library) | Wait latency | In-process |
| Stale-while-revalidate | Full | Medium | Slight staleness | None |
| Probabilistic early expiry | Full | Medium | Pre-expiry load | None |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Thundering herd only affects caches | It affects any shared resource that responds to a simultaneous trigger: database connection pools on server restart, message queue consumers all polling after a pause, auto-scaled nodes all registering with a config service at once. |
| Exponential backoff prevents thundering herd | Only if jitter is added. Pure exponential backoff (1s, 2s, 4s, 8s) still concentrates retries if all clients started at the same time (they all retry at 1s, then 2s, then 4s simultaneously). Jitter is essential. |
| A bigger cache prevents the problem | A bigger cache reduces cache miss frequency. But when any popular key expires (regardless of cache size), the concurrent miss problem occurs. Cache size does not solve the thundering herd - stampede protection does. |

---

### 🚨 Failure Modes & Diagnosis

**Cache Stampede Taking Down Database**

**Symptom:**
Every 5 minutes, the database experiences a spike
to 10x normal query load for exactly 2-3 seconds,
then returns to baseline. The pattern is clockwork-
regular. Each spike causes 5-8% of queries to fail
(timeouts).

**Root Cause:**
A critical cache key (homepage data) has TTL = 5
minutes. 50 API servers all have this key expire
simultaneously (all set it at the same time during
a previous restart). Every 5 minutes, all 50 servers
miss simultaneously and hit the DB.

**Diagnosis:**
```bash
# Check for synchronized cache key expiry
# Monitor cache miss rate over time - look for spikes
redis-cli MONITOR | grep MISS  # Or check metrics

# Check if keys were all set at the same time:
# (Keys with same TTL set simultaneously expire together)
redis-cli DEBUG SLEEP 0
redis-cli TTL homepage:data
# If multiple servers: all show same TTL remaining

# Add jitter now: update all servers to use
# TTL = 300 + random(0,60) on next write
```

**Fix (immediate):**
```python
# Force jitter on the next write to spread expiry
import random
# Old: r.setex("homepage:data", 300, value)
# New:
r.setex("homepage:data",
        300 + random.randint(0, 60),
        value)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - the component that often bears
  the thundering herd impact first
- `Auto Scaling` - the mechanism that should (but
  often cannot) respond fast enough to thundering herd

**Builds On This (learn these next):**
- `Rate Limiting (System)` - complements stampede
  protection by capping how many requests can hit
  a backend simultaneously
- `Token Bucket` - a rate-limiting algorithm that
  smooths bursty traffic

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Simultaneous correlated requests to a    │
│               │ resource overwhelm it                    │
├───────────────┼──────────────────────────────────────────┤
│ CAUSES        │ Cache key expiry, server restart,        │
│               │ job completion, reconnect storms          │
├───────────────┼──────────────────────────────────────────┤
│ CACHE FIX     │ TTL jitter + cache lock (mutex) +        │
│               │ stale-while-revalidate                   │
├───────────────┼──────────────────────────────────────────┤
│ RETRY FIX     │ Exponential backoff + FULL JITTER        │
│               │ (not equal jitter)                       │
├───────────────┼──────────────────────────────────────────┤
│ KEY RULE      │ Every retry, reconnect, and TTL in a     │
│               │ distributed system MUST have jitter      │
├───────────────┼──────────────────────────────────────────┤
│ LIBRARY       │ Go: golang.org/x/sync/singleflight       │
│               │ Java: Guava LoadingCache (async refresh) │
│               │ Spring: @Cacheable with custom resolver  │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "Cache expires → everyone hits DB.       │
│               │  Fix: jitter TTLs + serialize misses     │
│               │  (one DB query, not 10,000)."            │
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Rate Limiting → Token Bucket             │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Thundering herd = correlated simultaneous requests
   overwhelm a shared resource. Cache expiry is the
   canonical case.
2. Fix cache stampede: TTL jitter (simplest) + mutex/
   lock on cache miss (strongest). Singleflight
   library handles this in Go.
3. Fix retry stampede: exponential backoff + full
   jitter (random between 0 and cap, not cap/2 + random).
   Never retry without jitter in a distributed system.

**Interview one-liner:**
"Thundering herd occurs when many requests simultaneously
hit a shared resource due to a common trigger - the classic
case is a cache key expiry where all concurrent users miss
the cache and hammer the database at the same instant. Fix
with three layers: TTL jitter (randomize expiry times so
keys don't expire simultaneously), cache lock or singleflight
(serialize regeneration so only one request queries the DB
while others wait), and stale-while-revalidate (serve stale
data while one request refreshes in background). Same principle
applies to retry storms: exponential backoff must include full
jitter, otherwise synchronized retries create the same pattern."
