---
id: SYD-044
title: Rate Limiter Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-028, SYD-029, SYD-030
used_by: ""
related: SYD-028, SYD-029, SYD-030, SYD-039
tags:
  - architecture
  - rate-limiting
  - distributed
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/syd/rate-limiter-design/
---

⚡ TL;DR - A rate limiter controls the number of
requests a client can make in a time window. The design
challenge is implementing this at API scale (millions
of clients) with sub-millisecond overhead, distributed
correctness (across multiple API servers), and multiple
limit types (per-user, per-IP, per-endpoint). The
production pattern: sliding window counter in Redis
with Lua scripting for atomic check-and-increment,
limit decisions returned in HTTP headers
(X-RateLimit-*), and a centralized Redis cluster.

| #044 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Rate Limiting (System), Token Bucket, Leaky Bucket | |
| **Related:** | Rate Limiting, Token Bucket, Leaky Bucket, Distributed Locks | |

---

### 🔥 The Problem This Solves

An API endpoint costs $0.001/call to serve
(compute + DB + cache). A poorly-written client script
accidentally issues 50,000 requests in one minute to
the same user's account. Without rate limiting:
- Cost: $50 in 60 seconds for one user's bug
- System: legitimate users get 503 as capacity exhausted
- Abuse: bad actors can use APIs without paying
- DoS: unintentional denial-of-service via scripting bugs

Rate limiting provides: cost control, fairness between
clients, abuse prevention, and graceful degradation.

---

### 📘 Textbook Definition

**Rate limiter:** A component that enforces an upper
bound on the number of requests a client can make
within a defined time window. Requests that exceed
the limit are rejected (HTTP 429 Too Many Requests)
or queued (delayed until capacity is available).

**Key parameters:**
- `rate`: requests allowed per window
- `window`: time duration (seconds)
- `client_key`: identity (user_id, API key, IP address)
- `algorithm`: token bucket, leaky bucket, fixed window
  counter, sliding window counter, sliding window log

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Reject requests from a client that exceed N requests
per time window. Track request counts in a shared
store (Redis).

**One analogy:**
> A nightclub bouncer with a clicker: each person gets
> a maximum of 10 entries per hour. The bouncer clicks
> each entry, checks the count, and says "come back in
> 20 minutes" if the count is exceeded.
>
> Distributed problem: if there are 10 bouncers at 10
> doors (10 API servers), they must share the same
> clicker (Redis) or they can each let 10 people in
> (total 100, not 10).

**One insight:**
The single-server rate limiter is trivial. The hard
problem is: how do you make it distributed without
adding 50ms of Redis latency to every request? And
how do you handle Redis failures gracefully (fail-open
vs fail-closed)?

---

### 🔩 First Principles Explanation

**ALGORITHM COMPARISON:**
```
Fixed Window Counter:
  Increment counter for current time window.
  Reset at window boundary.
  
  Problem: boundary burst. Client sends 100 requests
  at 11:59:59 and 100 more at 12:00:01. Both windows
  allow 100 each. Client effectively got 200 requests
  in 2 seconds vs the intended 100/minute.

Sliding Window Log:
  Store timestamp of each request.
  On new request: delete all timestamps > 1 minute ago.
  Count remaining timestamps. If < limit: allow.
  
  Accurate: no boundary burst.
  Problem: memory = O(requests in window). At 1,000
  requests/minute per user, store 1,000 timestamps.

Sliding Window Counter (hybrid):
  Blend of fixed window counter and the previous window.
  current_count + previous_count * (1 - elapsed/window)
  
  Uses two integer counters per user (not timestamps).
  Accurate enough for most use cases.
  Memory: O(1) per user (two integers).
  Production default.

Token Bucket:
  Bucket filled at rate R. Drained on each request.
  Allows bursts up to bucket capacity.
  Good for allowing controlled short bursts.

Leaky Bucket:
  FIFO queue. Process at constant rate.
  Good for smoothing traffic.
```

**SLIDING WINDOW COUNTER - REDIS + LUA:**
```
Why Lua script?
  A rate limiter requires:
    1. Read current count
    2. Compare against limit
    3. Increment if under limit
  
  If done as 3 separate Redis commands:
    GET → compare in application → INCR
  Race condition: two concurrent requests both GET
  and see count=99 (limit=100). Both pass the check.
  Both INCR. Final count=101. Limit violated.
  
  Solution: Lua script runs atomically in Redis.
  GET + compare + INCR = 1 atomic operation.
  No race condition possible.
```

---

### 🧪 Thought Experiment

**DESIGN: Rate limiter for a public API**

**Requirements:**
- 1M active API users
- Limit: 1,000 requests/hour per API key
- Multiple API servers (10 servers)
- Latency budget for rate limit check: < 5ms

**Design:**

1. **Client key:** API key (from Authorization header).
   Fallback: IP address if no API key.

2. **Algorithm:** Sliding window counter in Redis.
   Two counters per API key: current window and
   previous window. O(1) memory per user.

3. **Storage:** Redis Cluster (3 nodes + 3 replicas).
   1M users × 2 counters × 50 bytes = 100MB - tiny.
   Redis can store this in memory with headroom to spare.

4. **Implementation:** Lua script for atomicity.
   Single Redis call from each API server.
   Redis RTT: ~1-2ms (same datacenter). Under budget.

5. **Middleware placement:** Rate limiter middleware
   before the API handler. Check → allow or 429.
   Return X-RateLimit-* headers with every response.

6. **Redis failure:** Fail-open (allow requests if
   Redis is unavailable). Alternative: maintain local
   per-server counter as fallback (may allow N × limit
   if all servers fail open, but better than 100% 503).

7. **Multiple limit types:**
   - Global (API key): key=`rl:apikey:{api_key}`
   - Per-endpoint: key=`rl:endpoint:{api_key}:{path}`
   - Per-IP: key=`rl:ip:{ip_address}`
   Apply all applicable limits; reject on first exceeded.

---

### 🧠 Mental Model / Analogy

> A rate limiter is like a prepaid phone plan: you have
> 1,000 minutes per month. A shared minute counter tracks
> usage. When you hit 1,000: calls are blocked until
> the next month (window reset).
>
> Distributed challenge: imagine 10 billing agents, each
> with a local notepad. They'd each count separately
> and all allow 1,000 minutes each (total 10,000).
> The solution: one central counter (Redis), shared
> by all billing agents (API servers). Each agent
> asks the central counter before allowing a call.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Rate limiting prevents any single user from making too
many requests in a short time period. If you send 1,001
requests when the limit is 1,000/hour, your 1,001st
request gets rejected with "try again in an hour."

**Level 2 - How to use it (junior developer):**
Middleware that checks a counter in Redis. For each
request: increment a counter keyed to the user's API
key. If counter > limit: reject with HTTP 429. Set
counter TTL to the window size (1 hour) so it resets
automatically.

**Level 3 - How it works (mid-level engineer):**
Use a Lua script in Redis for atomic check-and-increment
(prevents race conditions). Implement sliding window
counter (blend of current + previous window counts)
to avoid the "boundary burst" problem of fixed windows.
Return X-RateLimit-Remaining and X-RateLimit-Reset
headers so clients know their quota status.

**Level 4 - Why it was designed this way (senior/staff):**
Sliding window counter is a memory-efficient compromise:
it approximates sliding window log accuracy (no boundary
burst) using only two counters per user (not all
timestamps). Lua atomicity is essential: without it,
concurrent requests create race conditions that violate
the limit guarantee. Fail-open policy for Redis downtime
is deliberate: better to allow excess requests during
a brief outage than to fail all requests globally.

**Level 5 - Mastery (distinguished engineer):**
At massive scale (100M+ users), per-request Redis calls
(even at 1-2ms) become the rate limiter's own bottleneck.
Optimization: local in-process counter (counts recent
requests for a client without Redis), synced to Redis
every N requests or every T seconds (lazy sync).
Trade-off: soft limit enforcement (may exceed limit
briefly during sync interval) but removes per-request
Redis overhead. Design decision: hard limit enforcement
(Redis per request) vs soft limit with lower latency
(local + sync). Most production systems choose soft
limits with periodic sync. Second challenge: geographic
distribution. Separate Redis clusters per region allow
each region to enforce limits independently, but a user
in two regions simultaneously can exceed the global limit.
Solution: accept soft global limit OR use global
distributed counters (much higher coordination cost).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ SLIDING WINDOW COUNTER ALGORITHM                    │
│                                                      │
│ Window size: 60s. Limit: 100 reqs/window.           │
│                                                      │
│ Time: 12:00:45 (45s into current minute)            │
│                                                      │
│ current_window = "12:00:00 - 12:01:00"             │
│ previous_window = "11:59:00 - 12:00:00"            │
│                                                      │
│ Redis counters:                                     │
│   rl:user123:1200 = 80  (current, last 45s)        │
│   rl:user123:1159 = 40  (previous, full 60s)       │
│                                                      │
│ Weight of previous window:                          │
│   elapsed = 45s into current 60s window            │
│   weight = 1 - (45/60) = 0.25                      │
│   weighted_prev = 40 × 0.25 = 10                   │
│                                                      │
│ Effective count = 80 + 10 = 90                     │
│ Limit = 100. 90 < 100: ALLOW request.              │
│ Increment current window counter: 81               │
│                                                      │
│ If effective count >= 100: REJECT (429)            │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Sliding window counter in Redis + Lua**
```python
import redis
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

app = FastAPI()
r = redis.Redis(host="localhost", port=6379)

# Lua script: atomic sliding window counter
# Returns: [allowed (1/0), current_count]
RATE_LIMIT_LUA = """
local key_curr = KEYS[1]
local key_prev = KEYS[2]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local elapsed = tonumber(ARGV[4])

local prev_count = tonumber(redis.call('GET', key_prev) or 0)
local curr_count = tonumber(redis.call('GET', key_curr) or 0)

-- Weighted previous window count
local weight = 1 - (elapsed / window)
local effective = curr_count + (prev_count * weight)

if effective >= limit then
    return {0, math.ceil(effective)}
end

-- Allow: increment current window counter
redis.call('INCR', key_curr)
redis.call('EXPIRE', key_curr, window * 2)
return {1, math.ceil(effective + 1)}
"""

rate_limit_script = r.register_script(RATE_LIMIT_LUA)

def check_rate_limit(
    client_key: str,
    limit: int = 100,
    window: int = 60
) -> tuple[bool, int]:
    """
    Returns (allowed, current_count).
    Uses sliding window counter: two Redis keys.
    Lua script ensures atomicity.
    """
    now = time.time()
    window_start = int(now // window) * window
    elapsed = now - window_start

    # Two keys: current window and previous window
    key_curr = f"rl:{client_key}:{window_start}"
    key_prev = f"rl:{client_key}:{window_start - window}"

    result = rate_limit_script(
        keys=[key_curr, key_prev],
        args=[limit, window, now, elapsed]
    )
    allowed = bool(result[0])
    count = int(result[1])
    return allowed, count

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Extract client identifier
    api_key = request.headers.get("X-API-Key")
    client_key = api_key if api_key else (
        request.client.host)

    allowed, count = check_rate_limit(
        client_key, limit=100, window=60)

    if not allowed:
        return Response(
            content='{"error": "rate limit exceeded"}',
            status_code=429,
            headers={
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "Retry-After": "60",
                "Content-Type": "application/json",
            }
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(
        max(0, 100 - count))
    return response
```

**Example 2 - Fixed window race condition (BAD)**
```python
# BAD: Non-atomic check-and-increment (race condition)
def check_rate_limit_bad(client_key: str,
                          limit: int) -> bool:
    count = r.get(f"rl:{client_key}")
    count = int(count) if count else 0

    # RACE: Two concurrent requests both see count=99
    # Both pass this check. Both increment.
    # Final count: 101. Limit violated.
    if count >= limit:
        return False

    r.incr(f"rl:{client_key}")
    r.expire(f"rl:{client_key}", 60)
    return True

# GOOD: Use Lua script (shown above) or
# Redis SET with NX+atomic operations for atomicity.
# Two separate Redis commands are never atomic.
```

---

### ⚖️ Comparison Table

| Algorithm | Accuracy | Memory | Burst Behavior | Complexity |
|---|---|---|---|---|
| **Fixed Window** | Low (boundary burst) | O(1) | Allows double at boundary | Simple |
| **Sliding Window Log** | High | O(n per user) | None | Medium |
| **Sliding Window Counter** | High (approximate) | O(1) | Minimal | Medium |
| **Token Bucket** | Medium | O(1) | Allows controlled bursts | Medium |
| **Leaky Bucket** | High | O(queue) | Smoothed (no burst) | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Rate limiting can be done per-server without Redis | Without a shared store, each server tracks its own count. A client can hit 10 servers and get 10× the allowed rate. Always use a shared distributed store (Redis) for correctness across multiple API servers. |
| HTTP 429 is the only response option | 429 is for "too many requests" (rate limit). Some systems prefer silently dropping, throttling (adding delay), or queueing (buffer and process at capacity). The choice depends on the use case: public API (429), internal traffic (queue), streaming data (drop). |
| Rate limiting prevents DDoS | Rate limiting stops abuse from authenticated or rate-keyed clients. A DDoS from millions of IPs can bypass per-IP rate limits by distributing requests. DDoS protection requires additional: IP reputation, geo-blocking, challenge-response (CAPTCHA), WAF layer. |

---

### 🚨 Failure Modes & Diagnosis

**Redis Rate Limiter Becomes a Bottleneck**

**Symptom:**
At high throughput (100K+ requests/second), the API
latency P99 increases from 20ms to 200ms. Profiling
shows 90% of time is spent in the rate limiter's Redis
call. Redis CPU is at 80%.

**Root Cause:** At 100K req/sec, 100K Lua script
executions per second in a single Redis. Redis is
single-threaded for command execution. The rate limiter
Redis call has become the bottleneck.

**Fix - Local sliding window with lazy Redis sync:**
```python
import threading
from collections import defaultdict

# Local in-memory counter (per process)
_local_counts = defaultdict(int)
_local_lock = threading.Lock()
_sync_threshold = 10  # Sync to Redis every 10 requests

def check_rate_limit_local(client_key: str,
                             limit: int) -> bool:
    """
    Local counter with lazy sync to Redis.
    Trade-off: client can exceed limit by
    (sync_threshold × num_api_servers) in burst.
    """
    with _local_lock:
        _local_counts[client_key] += 1
        local_count = _local_counts[client_key]

    # Sync to Redis periodically (not every request)
    if local_count % _sync_threshold == 0:
        total = r.incrby(
            f"rl:{client_key}", _sync_threshold)
        _local_counts[client_key] = 0
        return total <= limit

    # Local check: approximate, not perfectly accurate
    return True  # Defer hard check to sync points
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Rate Limiting (System)` - conceptual overview
  of rate limiting patterns
- `Token Bucket` - burst-tolerant rate limiting algorithm
- `Leaky Bucket` - smoothing algorithm for rate limiting

**Builds On This (learn these next):**
- `Distributed Locks` - Redis-based locking pattern
  used in rate limiter Lua scripts

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ALGORITHM   │ Sliding window counter (best default):    │
│             │ 2 Redis counters, approximate accuracy   │
├─────────────┼──────────────────────────────────────────┤
  │
│ ATOMICITY   │ Lua script: GET + compare + INCR         │
│             │ Without Lua: race condition allows over- │
│             │ limit requests at concurrent load        │
├─────────────┼──────────────────────────────────────────┤
  │
│ KEYS        │ rl:{client_key}:{window_ts}              │
│             │ TTL = window * 2 (auto-cleanup)          │
├─────────────┼──────────────────────────────────────────┤
  │
│ RESPONSE    │ 429 Too Many Requests + Retry-After      │
│             │ X-RateLimit-{Limit,Remaining,Reset}      │
├─────────────┼──────────────────────────────────────────┤
  │
│ REDIS FAIL  │ Fail-open (allow) preferred over         │
│             │ fail-closed (block all) during outage    │
├─────────────┼──────────────────────────────────────────┤
  │
│ SCALE       │ 100K+ req/sec: local counter + lazy      │
│             │ Redis sync (reduces Redis calls 10-100x) │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Lua-atomic sliding window in Redis;     │
│             │ fail-open; X-RateLimit-* headers"       │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ News Feed Design → Search Autocomplete   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use a shared store (Redis) across all API servers.
   Per-server counters allow N× the intended rate limit
   (N = number of servers). Centralized Redis enforces
   the limit globally.
2. Use a Lua script for atomic check-and-increment.
   Two separate Redis commands (GET, then INCR) have a
   race condition: concurrent requests both see the
   pre-limit count and both proceed.
3. Sliding window counter (two counters, blended) is the
   production default. It approximates sliding window
   log accuracy with O(1) memory per user. Return
   X-RateLimit-Remaining in every response so clients
   can self-throttle.

**Interview one-liner:**
"Rate limiter design: sliding window counter in Redis (two counters:
current and previous window, blended by elapsed fraction). Lua script
for atomic GET+compare+INCR - without atomicity, concurrent requests
race past the limit. Single Redis cluster shared by all API servers -
per-server counters allow N× the rate. Return X-RateLimit-Remaining
and Retry-After headers. Fail-open if Redis is down (better than
blocking all users). At 100K+ req/sec, switch to local counter with
lazy Redis sync (sync every 10 requests) to reduce Redis load by 10x,
accepting soft limit enforcement."
