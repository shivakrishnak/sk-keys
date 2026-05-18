---
id: SYD-029
title: Token Bucket
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-028
used_by: ""
related: SYD-025, SYD-028, SYD-030, SYD-044
tags:
  - architecture
  - algorithm
  - rate-limiting
  - traffic-shaping
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/syd/token-bucket/
---

⚡ TL;DR - The token bucket algorithm rate-limits
requests by modeling a bucket that fills with tokens
at a constant rate and empties when requests consume
tokens. Each request consumes one token; if the bucket
is empty, the request is rejected or queued. The bucket
capacity (burst size) allows short traffic bursts above
the sustained rate. It is the most widely used rate
limiting algorithm because it naturally handles burst
traffic that is normal in web applications.

| #029 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Rate Limiting (System) | |
| **Used by:** | (Rate Limiter Design) | |
| **Related:** | Thundering Herd, Rate Limiting (System), Leaky Bucket, Rate Limiter Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (fixed window rate limiter):**
A fixed window allows 100 requests per minute.
At second 58, a user sends 100 requests (all allowed).
At second 61 (new window), the user sends another
100 requests (all allowed). In a 3-second window,
200 requests went through - twice the intended rate.
The server must handle a 200 req/3sec burst that was
not anticipated.

**THE BURST PROBLEM:**
Real web applications have bursty traffic patterns.
A user opens a dashboard that fires 20 API calls in
parallel. A mobile app synchronizes on login with
50 requests in 2 seconds. These are legitimate bursts,
not abuse. A strict "1 request per 600ms" rate limiter
would reject half of these. The token bucket allows
a burst up to the bucket capacity, then enforces the
average rate - accurately modeling legitimate burst
patterns while still preventing abuse.

---

### 📘 Textbook Definition

**Token bucket:** A rate limiting algorithm that
maintains a virtual bucket with a maximum capacity
of N tokens. Tokens are added to the bucket at a
constant rate (R tokens per second). Each incoming
request consumes one (or more) tokens from the bucket.
If the bucket has enough tokens, the request is allowed
and tokens are consumed. If the bucket is empty (or
has insufficient tokens), the request is rejected
(or queued). The bucket capacity determines the maximum
burst size: a full bucket means N requests can be
processed immediately, regardless of rate. The refill
rate R determines the sustained throughput.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A bucket fills with tokens at a steady rate. Requests
spend tokens. Empty bucket = reject request. Burst is
allowed up to bucket capacity.

**One analogy:**
> A coin-operated laundromat dryer:
> - The bucket = the dryer's "credit" (max 10 quarters)
> - Refill rate = 1 quarter added per 10 minutes
>   (time accumulates credit)
> - Request cost = 1 quarter per dryer cycle
>
> If you arrive with a full "credit" (10 quarters),
> you can start 10 loads back-to-back (burst).
> If you use them up, you must wait 10 minutes per
> additional load (sustained rate enforcement).
>
> A new user arriving with no credit must wait 10
> minutes for the first token (no burst credit accumulated).

**One insight:**
Token bucket smooths bursty traffic while enforcing
average rates. The burst capacity is a legitimate
allowance, not a loophole. Most API clients are bursty
by design (parallel requests on page load), and token
bucket models this correctly.

---

### 🔩 First Principles Explanation

**THE ALGORITHM:**

```
State:
  tokens: float    # current token count (0 to capacity)
  last_refill: float  # timestamp of last refill

Parameters:
  capacity: int    # max burst size (e.g., 100 tokens)
  refill_rate: float  # tokens added per second (e.g.,
    10/sec)

Request processing:
  1. Calculate tokens to add since last_refill:
     elapsed = now - last_refill
     new_tokens = elapsed × refill_rate
     tokens = min(capacity, tokens + new_tokens)
     last_refill = now

  2. Check if request can proceed:
     if tokens >= cost:
         tokens -= cost
         return ALLOW
     else:
         return DENY (429)
```

**EXAMPLE:**

```
Config: capacity=10, refill=2 tokens/sec

t=0.0: tokens=10 (full bucket)
  Request 1-10: all allowed (tokens = 0)
  
t=0.5: tokens = 0 + 0.5s × 2/s = 1 token
  Request 11: allowed (token = 0)
  
t=0.5: tokens=0
  Request 12: DENIED (empty)
  
t=1.0: tokens = 0 + 0.5s × 2/s = 1 token
  Request 13: allowed
  
Sustained rate: 2 req/sec (= refill rate)
Burst: up to 10 req immediately (= capacity)
```

**PARAMETERS AND THEIR MEANING:**

```
capacity = max burst size
  Small capacity: fast response to abuse,
    limited legitimate burst tolerance
  Large capacity: tolerates large legitimate bursts,
    slower to respond to sustained abuse
  Typical: 10-100x the per-second refill rate

refill_rate = sustained throughput
  = the actual rate limit enforcement
  If client sends exactly at refill_rate: never runs out
  If client sends above refill_rate: bucket drains over
    time
  Example: refill_rate=10/sec, capacity=100
    → Can burst 100 in 1 second
    → Then limited to 10/sec
    → After 10 seconds of silence: full bucket again
      (burst ready)
```

**THE TRADE-OFFS:**

**Token bucket vs Leaky bucket:**
Token bucket allows bursting (up to capacity). Leaky
bucket enforces a strict constant output rate (no
burst). For API rate limiting: token bucket. For
traffic shaping (e.g., network QoS): leaky bucket.

**Token bucket vs Fixed window:**
Fixed window has the boundary burst problem (200 req
in 2 seconds across a window boundary). Token bucket
naturally handles this because token accumulation
spans windows continuously.

**Memory per user:** Token bucket requires only 2
values per user (current tokens + last refill time).
O(1) per user.

---

### 🧪 Thought Experiment

**SCENARIO: API client behavior vs rate limiter response**

API limit: 100 tokens/min capacity, 1.67 tokens/sec refill

**Well-behaved API client:**
Makes ~100 requests over a minute, distributed evenly.
~1.67 req/sec. Bucket never empties. No 429s.

**Bursty-but-legitimate client:**
Dashboard loads, fires 50 parallel API calls (burst).
50 tokens consumed instantly. Then makes 2 calls/sec
for next 25 seconds.
- 50 tokens consumed in 1 second
- 50 tokens regenerate over next 30 seconds
- After 25 seconds: 50 tokens regenerated; 50 consumed
- Balance at end: 50 tokens remaining
No 429s; the burst was within capacity.

**Abusive client:**
Sends 200 requests in 1 second.
- First 100 allowed (full bucket)
- Remaining 100 rejected (429)
- Bucket starts refilling: 1.67 tokens/sec
- Next minute: client can burst another 100

**THE INSIGHT:**
The burst-then-rate-limited behavior means abuse gets
100 "free" requests before hitting the limit. This is
often acceptable (100 requests is not a serious attack).
For truly rate-sensitive APIs (payment submission),
set the capacity much smaller (5-10) to limit burst.
For read APIs: larger capacity (100-1000) to allow
legitimate app burst patterns.

---

### 🧠 Mental Model / Analogy

> Token bucket is like a car's fuel tank:
> - Tank capacity = burst capacity (max 50L)
> - Fuel station fills at 1L/minute (refill rate)
> - Each trip consumes 1L (request cost)
>
> If the tank is full, you can take 50 trips
> in a row immediately (burst). Then you must
> wait for the station to refill the tank.
>
> You cannot take 51 trips without waiting.
> And the tank never overflows (capacity cap).
>
> A fixed window is like: "50 trips per hour, starting
> at 00:00." You can take 50 at 00:59, then 50 more
> at 01:00. 100 trips in 2 minutes = burst problem.
> Token bucket does not have this issue.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A bucket fills with tokens at a steady rate. Every
request uses one token. When the bucket is empty,
requests are rejected. The bucket size allows short
bursts.

**Level 2 - How to use it (junior developer):**
Most rate limiting libraries implement token bucket
(or similar). Use a Redis-backed implementation for
distributed systems. Configure: capacity (max burst),
refill_rate (sustained limit). Return 429 when tokens
are unavailable.

**Level 3 - How it works (mid-level engineer):**
Implement token bucket in Redis using an atomic Lua
script (read-modify-write must be atomic to avoid
race conditions). The script: compute elapsed time,
calculate tokens to add (min with capacity), check
if enough tokens exist, decrement if yes, return
result. O(1) per request.

**Level 4 - Why it was designed this way (senior/staff):**
The token bucket's burst tolerance is not a design
accident - it is by design. Cloud provider APIs
(AWS, GCP, Stripe) all use token bucket variants
precisely because burst tolerance matches legitimate
client behavior (batch processes, retry storms after
an outage, dashboard page loads). The refill rate
sets the sustained limit; the capacity sets the burst
tolerance. Tuning these two parameters independently
is the key design flexibility that fixed-window counters
lack.

**Level 5 - Mastery (distinguished engineer):**
Generic token bucket limitation: it only enforces an
average rate over the refill window. A malicious client
can systematically empty the bucket exactly at capacity,
wait for it to fill, empty again - achieving exactly
the configured limit but in a bursty pattern that may
still overload the service. The mitigation: adaptive
rate limiting (detect systematic bucket-emptying
patterns and apply stricter limits) or hierarchical
rate limits (per-second AND per-minute limits, both
enforced). AWS uses "burst credits" per-second +
"baseline" per-second: both must be satisfied. This
requires two token buckets per client.

---

### ⚙️ How It Works (Mechanism)

**Distributed token bucket in Redis:**

```
┌──────────────────────────────────────────────────────┐
│ REDIS ATOMIC TOKEN BUCKET                           │
│                                                      │
│ Per-user state stored in Redis:                     │
│   Key: "tb:user:{user_id}"                          │
│   Value (hash):                                     │
│     tokens: 85.5    (current token count)           │
│     last_refill: 1705315200.345  (UNIX timestamp)   │
│                                                      │
│ On each request:                                     │
│   1. HGETALL → get current tokens + last_refill      │
│   2. elapsed = now - last_refill                     │
│   3. tokens = min(capacity, tokens + elapsed × rate) │
│   4. if tokens >= 1: tokens -= 1; return ALLOW       │
│   5. else: return DENY                               │
│   6. HSET → update tokens + last_refill             │
│   7. EXPIRE → reset TTL (auto-cleanup inactive users)│
│                                                      │
│ Steps 1-6 wrapped in Lua script for atomicity       │
│ (prevents race condition between read and write)     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Token bucket implementation (Python + Redis)**
```python
# Token bucket rate limiter using Redis Lua script
# Atomic: no race conditions even under high concurrency

import redis
import time
from typing import Optional

r = redis.Redis(host="redis", port=6379, db=0)

TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local cost = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

-- Refill tokens based on elapsed time
local elapsed = now - last_refill
local new_tokens = elapsed * refill_rate
tokens = math.min(capacity, tokens + new_tokens)

local allowed = 0
if tokens >= cost then
    tokens = tokens - cost
    allowed = 1
end

-- Update state with TTL (cleanup after 2x window)
redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)

return allowed
"""
_script = r.register_script(TOKEN_BUCKET_SCRIPT)

def check_token_bucket(
        user_id: str,
        capacity: int = 100,
        refill_rate: float = 10.0,  # tokens/second
        cost: int = 1
) -> bool:
    """Returns True if allowed, False if rate limited."""
    key = f"tb:user:{user_id}"
    now = time.time()

    result = _script(
        keys=[key],
        args=[capacity, refill_rate, cost, now]
    )
    return bool(result)

# Usage:
# capacity=100: burst up to 100 requests instantly
# refill_rate=10: 10 requests/second sustained rate
# After 10s of silence: full burst available again

# Endpoint cost examples:
# Regular API: cost=1
# Search (expensive): cost=5
# Video upload: cost=20
```

**Example 2 - Spring Boot: token bucket via Resilience4j**
```java
// Spring Boot rate limiting with Resilience4j
// Resilience4j implements a semaphore-based limiter;
// combine with token bucket for burst handling.

@Configuration
public class RateLimiterConfig {

    @Bean
    public RateLimiterRegistry rateLimiterRegistry() {
        // 10 calls per second, burst of 20
        io.github.resilience4j.ratelimiter.RateLimiterConfig config =
            io.github.resilience4j.ratelimiter.RateLimiterConfig
                .custom()
                .limitForPeriod(10)     // 10 per period
                .limitRefreshPeriod(Duration.ofSeconds(1))
                .timeoutDuration(Duration.ofMillis(100))
                .build();

        return RateLimiterRegistry.of(config);
    }
}

@RestController
public class SearchController {

    @Autowired
    private RateLimiterRegistry rateLimiterRegistry;

    @GetMapping("/search")
    @RateLimiter(name = "search-rate-limiter",
                  fallbackMethod = "rateLimitedFallback")
    public ResponseEntity<SearchResult> search(
            @RequestParam String q,
            @RequestHeader("X-User-Id") String userId) {

        SearchResult result = searchService.search(q);
        return ResponseEntity.ok(result);
    }

    // Called when rate limit exceeded
    public ResponseEntity<String> rateLimitedFallback(
            String q, String userId,
            RequestNotPermitted ex) {
        return ResponseEntity
            .status(HttpStatus.TOO_MANY_REQUESTS)
            .header("Retry-After", "1")
            .header("X-RateLimit-Limit", "10")
            .body("Rate limit exceeded. Retry in 1 second.");
    }
}
```

**Example 3 - Tiered token buckets (per-plan)**
```python
# Different rate limits per subscription plan
from dataclasses import dataclass

@dataclass
class Plan:
    name: str
    capacity: int       # burst tokens
    refill_rate: float  # tokens/second

PLANS = {
    "free":       Plan("free",       20,    1.0),   # 1 req/sec
    "starter":    Plan("starter",   100,   10.0),   # 10 req/sec
    "pro":        Plan("pro",       500,   50.0),   # 50 req/sec
    "enterprise": Plan("enterprise", 2000, 200.0),  # 200 req/sec
}

def check_rate_limit_for_user(
        user_id: str, plan_name: str) -> bool:
    """Check rate limit based on user's subscription plan."""
    plan = PLANS.get(plan_name, PLANS["free"])
    return check_token_bucket(
        user_id=user_id,
        capacity=plan.capacity,
        refill_rate=plan.refill_rate
    )

# Response headers indicate plan limits:
# X-RateLimit-Plan: pro
# X-RateLimit-Limit: 50 (per second)
# X-RateLimit-Burst: 500 (max burst)
# X-RateLimit-Remaining: 423
```

---

### ⚖️ Comparison Table

| Property | Token Bucket | Leaky Bucket | Fixed Window | Sliding Window |
|---|---|---|---|---|
| **Burst allowed** | Yes (up to capacity) | No (strict constant rate) | At boundaries | Never |
| **Memory** | O(1) | O(queue depth) | O(1) | O(requests in window) |
| **Consistency** | Smooth average + bursts | Perfectly smooth | Choppy (window reset) | Smooth |
| **Implementation** | Medium (need float time) | Medium (queue) | Simple (INCR/EXPIRE) | Medium (sorted set) |
| **Best for** | API rate limiting | Traffic shaping (network) | Simple counters | Accurate no-burst limiting |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Token bucket and leaky bucket are the same | Token bucket allows bursting up to capacity. Leaky bucket enforces a strict constant output rate (acts as a queue with constant drain rate). They have opposite burst behaviors. |
| Full bucket on startup gives a free attack window | This is a real design consideration. A new client starting with a full bucket (capacity=100) can immediately send 100 requests. Solution: initialize new users at a fraction of capacity (e.g., 50% of capacity) or use a smaller initial bucket that grows with usage. |
| Token bucket is only for APIs | It is used in network QoS (TCP congestion control uses variants), CPU scheduling, cloud service limits (AWS API quotas), and application-level rate limiting. The algorithm is general-purpose. |

---

### 🚨 Failure Modes & Diagnosis

**Race Condition in Non-Atomic Implementation**

**Symptom:**
Rate limiter allows 2x the configured limit under high
concurrency. A limit of 100 req/min is effectively
200 req/min with 10 concurrent API workers.

**Root Cause:**
Two API workers read the token count simultaneously:
both read "5 tokens remaining." Both check "5 >= 1
→ allow." Both decrement by 1. Result: 5 - 1 = 4
(not 3). Two requests were allowed with one token
effectively "double-spent."

**Fix:**
All read-modify-write operations on the token count
MUST be atomic. Use Redis Lua script (entire script
runs atomically) or Redis WATCH/MULTI/EXEC
(optimistic locking). Never use GET + SET as two
separate Redis commands for rate limiting.

```python
# BAD: Non-atomic (race condition possible):
tokens = r.hget(key, "tokens")  # Read
# → another thread reads same value here
if tokens >= 1:
    r.hset(key, "tokens", tokens - 1)  # Write (race)

# GOOD: Atomic Lua script (as in Example 1 above)
# Entire Lua script runs atomically in Redis
# No other command executes between read and write
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Rate Limiting (System)` - the context in which
  token bucket is used; the "why" before the algorithm

**Builds On This (learn these next):**
- `Leaky Bucket` - the contrasting algorithm: strict
  constant-rate enforcement, no burst
- `Rate Limiter Design` - applying token bucket in
  a full system design interview answer

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ALGORITHM     │ Bucket fills at R tokens/sec to max N.  │
│               │ Each request costs 1+ tokens.           │
│               │ Empty bucket → 429 or queue.            │
├───────────────┼─────────────────────────────────────────┤
│ PARAMS        │ capacity: max burst (tokens)            │
│               │ refill_rate: sustained limit (tokens/s) │
├───────────────┼─────────────────────────────────────────┤
│ STATE         │ O(1): just tokens + last_refill per user│
├───────────────┼─────────────────────────────────────────┤
│ BURST         │ Client can burst up to capacity tokens  │
│               │ instantly, then limited to refill_rate  │
├───────────────┼─────────────────────────────────────────┤
│ KEY RULE      │ Implementation MUST be atomic           │
│               │ (Redis Lua script or equivalent)        │
├───────────────┼─────────────────────────────────────────┤
│ VS LEAKY      │ Token bucket = burst OK                 │
│               │ Leaky bucket = strict constant rate     │
│               │ API rate limiting → token bucket        │
│               │ Network QoS → leaky bucket              │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Bucket fills with tokens at rate R.    │
│               │  Burst up to capacity N then capped at R│
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Leaky Bucket → Rate Limiter Design      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Token bucket: refills at R tokens/sec, max capacity
   N. Burst up to N allowed immediately; then capped
   at R/sec. Two parameters, independent tuning.
2. Token bucket is preferred for APIs because it
   tolerates legitimate burst traffic (parallel requests,
   batch jobs). Leaky bucket enforces strict constant rate.
3. Must be atomic (Redis Lua script). Non-atomic
   read-modify-write creates a race condition that lets
   clients exceed the limit under concurrency.

**Interview one-liner:**
"Token bucket has two parameters: capacity (max burst tokens)
and refill_rate (tokens added per second). Each request costs
tokens. A full bucket allows bursting up to capacity; then
the client is limited to the refill rate. State is O(1) per
user: just current token count and last refill timestamp.
Token bucket is preferred over fixed window for API rate
limiting because it correctly models bursty but legitimate
traffic (parallel API calls on dashboard load) while still
enforcing average rates. Critical implementation detail: the
read-modify-write must be atomic (use Redis Lua script) to
prevent race conditions that let clients exceed the limit
under concurrency."
