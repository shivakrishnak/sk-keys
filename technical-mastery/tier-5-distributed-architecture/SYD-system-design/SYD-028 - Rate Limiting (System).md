---
id: SYD-028
title: Rate Limiting (System)
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008, SYD-027
used_by: SYD-029, SYD-030, SYD-044
related: SYD-008, SYD-025, SYD-027, SYD-029, SYD-030, SYD-044
tags:
  - architecture
  - security
  - reliability
  - api
  - design-pattern
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/syd/rate-limiting-system/
---

⚡ TL;DR - Rate limiting controls the number of requests
a client can make to a service within a time window.
It protects servers from abuse (DoS), enforces fair
usage in multi-tenant systems, and prevents cascading
failures when downstream services are degraded. The
key design decisions are: where to enforce it (API
gateway, application, service), which algorithm to
use (token bucket, leaky bucket, fixed window, sliding
window), and what to do when the limit is exceeded
(reject with 429, queue, or degrade gracefully).

| #028 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Capacity Planning | |
| **Used by:** | Token Bucket, Leaky Bucket, Rate Limiter Design | |
| **Related:** | Load Balancing, Thundering Herd, Capacity Planning, Token Bucket, Leaky Bucket | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A public API has no rate limiting. A buggy client
in production accidentally sends 10,000 requests/second
(instead of 10). The database is overwhelmed. All
other clients experience degraded performance. The
service goes down. All other customers are impacted
by one buggy client.

**THREE PROBLEMS RATE LIMITING SOLVES:**
1. **DoS protection:** Prevents any single client from
   monopolizing resources.
2. **Fair usage:** In multi-tenant systems, one tenant's
   traffic cannot degrade service for others.
3. **Cascading failure prevention:** When a downstream
   service is slow, rate limiting prevents the caller
   from hammering it with retries, giving it time to recover.

---

### 📘 Textbook Definition

**Rate limiting:** A control mechanism that restricts
the number of requests an entity (user, IP, API key,
service) can make to a system within a defined time
window. When the limit is exceeded, requests are
rejected (typically with HTTP 429 Too Many Requests),
queued, or throttled (slowed down). Rate limiting can
be applied at multiple levels: network (firewall),
API gateway, application code, and database query layer.
It is distinct from load shedding (which drops all
traffic above a threshold) and throttling (which slows
requests rather than rejecting them).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Limit how many requests a client can make in a given
time window to protect the service and ensure fair
usage.

**One analogy:**
> A bank limits ATM withdrawals to $500/day per card.
> This protects the bank from a compromised card
> emptying an account instantly. It also ensures
> ATM cash is available for all customers (fair usage).
> When you hit the limit, you are rejected - not
> because the bank is out of money, but because your
> specific allowance is exhausted.
>
> A 429 response is the API equivalent of the ATM
> saying "daily withdrawal limit reached."

**One insight:**
Rate limiting is asymmetric: it protects the server
at the cost of some legitimate requests being rejected.
The limit must be set high enough to not affect normal
usage but low enough to protect against abuse. Getting
this calibration right requires understanding typical
client usage patterns.

---

### 🔩 First Principles Explanation

**RATE LIMITING DIMENSIONS:**

```
1. BY ENTITY (what is rate-limited?):
   - IP address: protects against anonymous abuse
     but breaks with NAT (1 IP = 1000 users)
   - API key: per-application; accurate for programmatic
   - User ID: per-user; accurate for authenticated flows
   - Endpoint: per-URL; protect expensive endpoints

2. BY TIME WINDOW:
   - Fixed window: count resets every N seconds
     Burst problem: 100 req/min limit → 100 at 00:59
     + 100 at 01:00 = 200 in 2 seconds
   - Sliding window: rolling count over last N seconds
     More accurate; eliminates burst at window boundary
   - Token bucket: allows bursting up to bucket capacity;
     refills at constant rate (most popular)
   - Leaky bucket: queues and processes at constant rate;
     eliminates bursting entirely

3. BY ACTION ON LIMIT:
   - Reject (429): simplest; clear signal to client
   - Queue: hold request; serve when capacity available
     Risk: queue depth grows; memory pressure
   - Throttle: artificially slow responses
     (rarely used in REST APIs)
   - Degrade: return simplified/cached response instead
```

**THE IMPLEMENTATION LAYERS:**

```
┌─────────────────────────────────────────────────────┐
│ WHERE TO ENFORCE RATE LIMITING                      │
│                                                     │
│ L1: Edge / CDN (e.g., Cloudflare, Fastly)          │
│   Pros: stops traffic before it hits your servers  │
│   Cons: limited per-user context; expensive to     │
│   configure for complex rules                      │
│                                                     │
│ L2: API Gateway (e.g., Kong, AWS API GW, Nginx)    │
│   Pros: centralized; works for all services;       │
│   configurable per route                           │
│   Cons: adds latency; gateway is a bottleneck      │
│                                                     │
│ L3: Application layer (code in service)            │
│   Pros: full context (user, tenant, plan tier);    │
│   complex rules possible                           │
│   Cons: each service implements its own; no        │
│   centralization in microservices                  │
│                                                     │
│ L4: Distributed rate limiter service               │
│   Pros: shared state across multiple instances     │
│   (needed for horizontal scaling)                  │
│   Cons: adds network hop; rate limiter service     │
│   itself is a dependency that can fail             │
└─────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

**Local rate limiting (per-instance counter):**
Gain: no network hop, very fast.
Cost: each instance has its own counter. With 10
instances: client can make 10x the limit (one
instance per request, each at limit/10).

**Centralized rate limiting (Redis):**
Gain: accurate across all instances.
Cost: Redis call on every request (+1ms RTT); Redis
itself is a single point of failure for all requests.

**Distributed rate limiting (token bucket in Redis):**
Most common in production. Redis provides atomicity
(INCR/EXPIRE or Lua scripts); all instances share
the same counter.

---

### 🧪 Thought Experiment

**SCENARIO: Rate limiting in a multi-tier system**

A search API has 3 rate limits:
- Per IP: 100 req/min (prevents DoS from single IP)
- Per API key: 1,000 req/min (per-application limit)
- Per user: 10,000 req/day (per-user daily quota)

A request comes in. Which check runs first?

**Answer: evaluate in order of cheapest to enforce:**
1. IP rate limit (no auth needed, just IP header)
   → Fastest to check (no DB lookup)
2. API key rate limit (check after key validation)
   → Medium: need to look up the key's counter
3. User daily quota (check after authentication)
   → Slowest: need to decode JWT + check user counter

**Why this order matters:**
A DoS attack using random IPs will be blocked at L1
before touching the auth system. A bot using many
API keys will be blocked at L2 before the user quota
system is involved. A legitimate user exceeding their
daily quota is blocked at L3.

Each check is a gate that protects the more expensive
gates behind it.

**RATE LIMIT HEADERS (client communication):**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705315200
```
The client knows exactly when to retry. This allows
well-behaved clients to back off automatically and
retry at the right time, rather than hammering with
retries.

---

### 🧠 Mental Model / Analogy

> Rate limiting is a highway on-ramp metering light:
> - Normal traffic: green light every 3 seconds
>   (allow 20 cars per minute)
> - Rush hour (high system load): green every 5 seconds
>   (allow 12 cars per minute)
> - Emergency: light stays red (service unavailable)
>
> The metering light does not care if the waiting cars
> are important - it enforces a rate uniformly (or by
> priority with HOV lanes = premium tier).
>
> The cars that cannot get in are not lost (queued at
> the ramp) or turned away (429 rejection). The highway
> is never overwhelmed. Traffic entering is always at
> a predictable rate.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A limit on how many requests you can make to a service
in a given time. Like a "maximum 10 requests per minute"
rule. If you exceed it, you get an error and must wait.

**Level 2 - How to use it (junior developer):**
Add rate limiting at the API gateway for public APIs.
Configure per-IP and per-API-key limits. Return 429
with Retry-After header. Log rate limit violations
for monitoring. Start with conservative limits and
increase based on observed legitimate usage.

**Level 3 - How it works (mid-level engineer):**
For horizontal scale: use Redis with INCR + EXPIRE
for per-window counters, or implement token bucket
algorithm in Redis using a Lua script (atomic).
Per-user rate limiting requires user ID extraction
(from JWT, session, or API key lookup).

**Level 4 - Why it was designed this way (senior/staff):**
Rate limiting is a form of queue management. When
requests arrive faster than they can be processed,
the system must decide: queue them (adds latency,
memory pressure, potentially unbounded delay) or
reject them (clear signal, no resource waste). For
interactive APIs: rejection (429) is almost always
the right choice - queuing adds latency that is
worse than retrying. For batch processing APIs:
queuing may be appropriate if the client can handle
asynchronous processing.

**Level 5 - Mastery (distinguished engineer):**
Advanced rate limiting at scale uses a sliding window
log (log each request timestamp, count the last N
seconds) or a sliding window counter (two fixed
windows blended by timestamp position). The sliding
window eliminates the burst-at-boundary problem of
fixed windows but requires more memory per user.
Redis sorted sets (ZADD with timestamp score, ZRANGEBYSCORE
to count recent requests, ZREMRANGEBYSCORE to evict old)
implement the sliding window log efficiently. At very
high scale (Twitter-scale API rate limiting): consider
approximate counting using probabilistic data structures
(Count-Min Sketch) to reduce memory by 10-100x at the
cost of slight over-counting (never under-counting).

---

### 💻 Code Example

**Example 1 - BAD: Local in-memory rate limiter**
```python
# BAD: Local rate limiter - each instance has its
# own counter. With 10 instances, user can 10x the limit.

from collections import defaultdict
import time

# This counter is per-process, not per-cluster
_counters = defaultdict(list)

def is_rate_limited(user_id: str,
                    limit: int = 100,
                    window_seconds: int = 60) -> bool:
    now = time.time()
    window_start = now - window_seconds

    # Remove old requests
    _counters[user_id] = [
        t for t in _counters[user_id]
        if t > window_start
    ]

    if len(_counters[user_id]) >= limit:
        return True  # Rate limited

    _counters[user_id].append(now)
    return False
# Problem: with 10 API servers, each allows 100 req/min
# Total: 1000 req/min per user (10x intended limit)
```

**Example 2 - GOOD: Redis-backed sliding window counter**
```python
# GOOD: Centralized rate limiting via Redis
# Atomic Lua script: check and increment in one operation

import redis

r = redis.Redis(host="redis-cluster", port=6379)

RATE_LIMIT_SCRIPT = """
local key = KEYS[1]
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Remove entries older than window
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)

-- Count entries in window
local count = redis.call('ZCARD', key)

if count < limit then
    -- Add this request
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, window + 1)
    return 0  -- Not limited
else
    return 1  -- Rate limited
end
"""
_script = r.register_script(RATE_LIMIT_SCRIPT)

def check_rate_limit(
        user_id: str,
        limit: int = 100,
        window_seconds: int = 60) -> bool:
    """Returns True if rate limited."""
    import time
    key = f"rl:user:{user_id}"
    now = int(time.time() * 1000)  # millisecond precision

    result = _script(
        keys=[key],
        args=[window_seconds * 1000, limit, now]
    )
    return bool(result)

# FastAPI middleware:
from fastapi import Request, HTTPException

async def rate_limit_middleware(request: Request, call_next):
    user_id = request.headers.get("X-User-ID", "anonymous")
    if check_rate_limit(user_id, limit=100, window_seconds=60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"}
        )
    return await call_next(request)
```

**Example 3 - Rate limit headers for client transparency**
```python
def get_rate_limit_headers(
        user_id: str,
        limit: int,
        window_seconds: int) -> dict:
    """Return standard rate limit headers."""
    import time

    key = f"rl:user:{user_id}"
    now = int(time.time() * 1000)
    window_start = now - (window_seconds * 1000)

    # Count current usage
    r.zremrangebyscore(key, '-inf', window_start)
    current_count = r.zcard(key)
    remaining = max(0, limit - current_count)

    # Next window reset time
    window_reset = int(time.time()) + window_seconds

    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(window_reset),
        "X-RateLimit-Window": f"{window_seconds}s"
    }
# Client can use these to implement adaptive throttling:
# reduce request rate as X-RateLimit-Remaining approaches 0
```

---

### ⚖️ Comparison Table

| Algorithm | Burst Handling | Implementation | Memory | Use Case |
|---|---|---|---|---|
| Fixed window | Allows burst at boundary | Simple (INCR/EXPIRE) | O(1) | Simple APIs |
| Sliding window log | No boundary burst | Medium (ZADD/ZRANGEBYSCORE) | O(requests in window) | Accurate limiting |
| Token bucket | Allows configured burst | Medium (custom Redis Lua) | O(1) | Flexible burst allowance |
| Leaky bucket | No burst (constant rate) | Medium | O(queue depth) | Strict rate enforcement |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Rate limiting is the same as throttling | Rate limiting rejects excess requests (429). Throttling slows requests (artificially delays responses). Rate limiting is more common for APIs; throttling is used in some streaming or processing systems. |
| Per-IP rate limiting is sufficient | IP-based rate limiting breaks for NAT (one IP = thousands of users from a corporate office) and is too granular for some abuse patterns. Per-API-key or per-user-ID limits are more accurate for authenticated APIs. |
| Rate limiting should be set tightly to save resources | Too-tight rate limiting rejects legitimate traffic, degrading user experience. Set limits based on observed legitimate usage patterns, not on what the server "can handle." The server should handle the legitimate peak; rate limiting protects against abuse above that. |

---

### 🚨 Failure Modes & Diagnosis

**Rate Limiter Redis Failure Takes Down All Requests**

**Symptom:**
Redis cluster used for rate limiting becomes unavailable.
All API requests start failing with 500 (not 429).
The rate limiter is blocking all requests rather than
failing open.

**Root Cause:**
The rate limiter is implemented as a hard dependency:
if the Redis call fails, the request is rejected (fail-
closed). This means rate limiter availability = API
availability.

**Fix:**
```python
# GOOD: Fail-open rate limiting
# If rate limiter is down, allow traffic (accept risk)
# rather than blocking everything (guaranteed outage)

def check_rate_limit_safe(user_id: str) -> bool:
    try:
        return check_rate_limit(user_id)
    except redis.RedisError as e:
        # Rate limiter unavailable: fail open
        # Log for monitoring; accept temporary risk
        # of unthrottled traffic
        logger.warning(
            f"Rate limiter unavailable: {e}. "
            f"Failing open for user {user_id}."
        )
        return False  # False = not rate limited → allow request

# Decision: fail-open (allow) vs fail-closed (block):
# For APIs serving users: fail-open. Outage > risk of abuse.
# For security-critical systems: fail-closed may be correct.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - rate limiting often sits in the
  load balancer or API gateway layer
- `Capacity Planning` - rate limits are set based on
  capacity; they protect what has been provisioned

**Builds On This (learn these next):**
- `Token Bucket` - the most common rate limiting
  algorithm; allows burst while enforcing average rate
- `Leaky Bucket` - alternative algorithm for strict
  constant-rate enforcement

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PURPOSE       │ Protect service from abuse; ensure fair │
│               │ usage; prevent cascading failures       │
├───────────────┼─────────────────────────────────────────┤
│ ENTITY        │ IP (simple), API key (accurate),        │
│               │ User ID (per-user), endpoint (per-op)   │
├───────────────┼─────────────────────────────────────────┤
│ ALGORITHMS    │ Fixed window, Sliding window,           │
│               │ Token bucket (most common), Leaky bucket│
├───────────────┼─────────────────────────────────────────┤
│ RESPONSE      │ 429 Too Many Requests                   │
│               │ Headers: Retry-After, X-RateLimit-*     │
├───────────────┼─────────────────────────────────────────┤
│ DISTRIBUTED   │ Use Redis: shared counter across all    │
│               │ instances; fail-open on Redis failure   │
├───────────────┼─────────────────────────────────────────┤
│ LAYERS        │ Edge/CDN → API Gateway → Application    │
│               │ → Database; defend in depth             │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Limit requests per entity per window.  │
│               │  Reject excess with 429. Use Redis for  │
│               │  accurate distributed enforcement."     │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Token Bucket → Leaky Bucket             │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Rate limiting protects servers from abuse and ensures
   fair multi-tenant usage. Response code: 429 with
   Retry-After header.
2. In-process counters are wrong at scale: each instance
   has its own counter → user can 10x the limit. Use
   Redis for centralized counting across all instances.
3. Fail-open when rate limiter is down (Redis failure
   → allow traffic) unless security requires fail-closed.
   Rate limiter downtime should not cause API downtime.

**Interview one-liner:**
"Rate limiting controls requests per entity per time window
to protect servers from abuse and ensure fair usage in
multi-tenant systems. Algorithms: fixed window (simple but
allows burst at boundary), sliding window (accurate, more
memory), and token bucket (allows controlled bursting, most
common). For horizontal scale, use Redis as a shared counter
- in-process counters are inaccurate because each instance
maintains its own. Return 429 with Retry-After header on
limit exceeded. Critical: fail-open when Redis is unavailable
- the rate limiter should never be a harder dependency than
the service it protects."
