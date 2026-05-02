---
layout: default
title: "API Rate Limiting"
parent: "HTTP & APIs"
nav_order: 233
permalink: /http-apis/api-rate-limiting/
number: "0233"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, Redis, API Gateway
used_by: Public APIs, API Gateways, Microservices, SaaS Platforms
related: API Throttling, API Gateway, HMAC, API Authentication, Circuit Breaker
tags:
  - api
  - rate-limiting
  - throttling
  - redis
  - intermediate
---

# 233 — API Rate Limiting

⚡ TL;DR — API rate limiting controls how many requests a client can make in a time window; the server returns HTTP 429 (Too Many Requests) when the limit is exceeded; strategies include Fixed Window, Sliding Window, Token Bucket, and Leaky Bucket — each with different fairness and burst tolerance tradeoffs.

| #233 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, Redis, API Gateway | |
| **Used by:** | Public APIs, API Gateways, Microservices, SaaS Platforms | |
| **Related:** | API Throttling, API Gateway, HMAC, API Authentication, Circuit Breaker | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You launch a public API. A buggy integration sends 50,000 requests per second
to `/search`. Your Elasticsearch cluster buckles under load. All users — even
legitimate ones — experience timeouts. Alternatively: a competitor scrapes all
your product data using 100 API keys simultaneously. Your competitor has a complete
copy of your database within hours, and your costs balloon from their egress traffic.
Or: a free-tier user writing a for-loop in production accidentally hammers your API
and causes a DDoS on themselves and others.

**THE INVENTION MOMENT:**
Rate limiting emerged from telecom and network engineering. HTTP rate limiting
was popularized by Twitter's API (2009) after the "fail whale" era. The insight:
protect server resources AND guarantee fair access to shared infrastructure by
enforcing per-client request quotas. When a client exceeds their quota, return
HTTP 429 (Too Many Requests) with `Retry-After` header — tell them to back off
rather than silently slowing down responses.

---

### 📘 Textbook Definition

**API Rate Limiting** is a mechanism that controls the number of requests a client
(identified by API key, user ID, IP address, or account) can make to an API within
a specified time window. When the threshold is exceeded, the server returns an
HTTP 429 (Too Many Requests) response, optionally with a `Retry-After` or
`X-RateLimit-Reset` header indicating when the limit resets. Rate limiting serves
multiple purposes: protecting backend services from overload, preventing abuse and
scraping, ensuring fair resource distribution among clients, enforcing commercial
service tiers (free vs paid quotas), and meeting DDoS mitigation requirements.
Common algorithms: Fixed Window Counter, Sliding Window Log, Sliding Window Counter,
Token Bucket, and Leaky Bucket.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Rate limiting enforces "you can only make N requests per time window" — exceeding
it returns 429, protecting the server and ensuring fair access for all clients.

**One analogy:**

> Rate limiting is like a coffee shop with a loyalty punch card.
> "10 coffees per day max per customer." If you try for the 11th, you're told
> to come back tomorrow. This isn't because coffee is unavailable — it's so
> one customer can't consume the entire day's supply, leaving nothing for others.
> The `Retry-After` header is the barista saying "come back in 47 minutes."

**One insight:**
The choice of algorithm matters more than the limit value:

- Fixed Window can be "beaten" by 2x the limit at window boundaries
- Token Bucket allows controlled bursting (good for real user behavior)
- Leaky Bucket enforces a smooth rate regardless of burst (good for downstream protection)

---

### 🔩 First Principles Explanation

**ALGORITHM COMPARISON:**

```
ALGORITHM 1 — FIXED WINDOW COUNTER (simplest)
  Window: [0:00–0:59], [1:00–1:59], etc.
  Limit: 100 requests per minute
  Counter: reset at window boundary

  Problem (boundary attack):
  t=0:59: send 100 requests → all accepted (window 1)
  t=1:00: send 100 requests → all accepted (window 2 starts fresh)
  Result: 200 requests in 2 seconds — 2x the intended limit!

ALGORITHM 2 — SLIDING WINDOW LOG
  Store timestamp of every request (in Redis sorted set)
  Count requests in window [now - 1min, now]
  Reject if count ≥ 100

  Pro: Precise, no boundary attack
  Con: Memory O(requests in window) — 100 per client → fine
       But 1M clients × 100 requests = 100M Redis entries

ALGORITHM 3 — SLIDING WINDOW COUNTER (hybrid)
  Keep current and previous window counters
  Estimate: count = prev_count × (1 - elapsed_fraction) + current_count
  Example: prev_window: 80, current_window: 30, elapsed: 25% of window
  Estimated: 80 × 0.75 + 30 = 60 + 30 = 90 → under limit ✓

  Pro: Memory O(1) per client, approximates sliding window behavior
  Con: Approximate — ±few requests at boundary

ALGORITHM 4 — TOKEN BUCKET
  Client has a bucket with capacity C tokens
  Tokens refill at rate R per second
  Each request consumes 1 token
  If bucket empty: 429

  Pro: Allows bursting (accumulate tokens, spend quickly)
  Example: capacity=100, refill=10/sec
  Client idle for 10 seconds → accumulates 100 tokens
  → can burst 100 requests immediately, then back to 10/sec sustained
  Great for: user-facing APIs where users click occasionally, then rapidly explore

ALGORITHM 5 — LEAKY BUCKET
  Requests enter a queue (the "bucket")
  Queue drains at a fixed rate (the "leak")
  If queue full: 429

  Pro: Smooth output rate — protects downstream at constant rate
  Con: Latency introduced by queue; no burst benefit
  Great for: downstream service protection (DB, external API)
```

---

### 🧪 Thought Experiment

**SCENARIO:** Token Bucket vs Fixed Window for a search API.

```
Search API: limit 60 requests per minute (1/second average)

USER BEHAVIOR: A developer opens your dashboard, navigates through 10 pages
loading data widgets. Over 3 seconds: 40 requests. Then idle for 2 minutes.

FIXED WINDOW:
  Window [0:00-0:59]: 40 out of 60 → fine
  Window [1:00-1:59]: idle → 0 requests
  Real usage: bursty but reasonable

TOKEN BUCKET (capacity=60, refill=1/sec):
  User starts with 60 tokens
  10 widget loads × ~4 requests = 40 requests → 20 tokens left
  Idle 2 minutes → refills to 60 tokens
  → Same developer NEVER hits rate limit despite "burst"

SLIDING LOG:
  If 40 requests come in at t=0-3secs:
  At t=1: within last 60s: 15 requests
  At t=3: within last 60s: 40 requests → still fine
  → Fine, but memory-expensive at scale

CONCLUSION:
For user-facing APIs, Token Bucket is most intuitive and fair.
For background batch jobs, Leaky Bucket keeps downstream safe.
```

---

### 🧠 Mental Model / Analogy

> Rate limiting algorithms as water containers:
>
> Fixed Window: A cup that resets (empties) every minute.
> You can pour 100ml at any time in the minute. Risk: pour 100ml at 0:59
> and another 100ml at 1:00 (new cup). 200ml in 2 seconds.
>
> Token Bucket: A cup that slowly fills from a tap.
> You can drink accumulated water quickly (burst), but the tap refills slowly (sustained rate).
> Empty cup → no more drinking despite wanting to.
>
> Leaky Bucket: A cup with a hole at the bottom.
> Water drips out at a steady rate. You can pour in quickly (queue),
> but the output is always smooth. Overflow (full bucket) = reject.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Rate limiting means: "you've made too many requests, slow down." After a set number
of requests in a time window, you get a 429 response telling you to wait before
trying again. It keeps one client from overwhelming the service.

**Level 2 — How to use it (junior developer):**
Identify the client (API key, authenticated user, or IP). Count requests in a window
(store in Redis with TTL). If count ≥ limit: return 429 with `Retry-After` header.
Set headers on all responses: `X-RateLimit-Limit: 100`, `X-RateLimit-Remaining: 47`,
`X-RateLimit-Reset: 1630000060` so clients can self-adjust.

**Level 3 — How it works (mid-level engineer):**
At high scale, rate limiting must be distributed (multiple gateway nodes all counting
the same client). Redis is the standard backend: atomic INCR + EXPIRE or Lua scripts
for token bucket logic. For Sliding Window Counter: two keys per client per window
(`rate:userId:window1`, `rate:userId:window2`), compute weighted estimate. Best practice:
always use LUA scripts in Redis to make the check-and-increment atomic — non-atomic
implementations have race conditions that allow limit bypasses. Kong rate-limiting
plugin, AWS API Gateway quotas, and Spring Gateway rate limiter all use this approach.

**Level 4 — Why it was designed this way (senior/staff):**
Rate limiting at scale has fundamental tradeoffs. Using Redis INCR requires a network
round trip per request — adds ~1ms. At 200K req/s this is a lot. Local in-process
rate limiting (no Redis) is faster but loses coordination across instances —
N gateway nodes each allowing N×limit requests. The compromise: approximate distributed
rate limiting with Redis pipelines, gossip-based counters, or "local + global" two-tier
approaches. Advanced rate limiting distinguishes between rate limiting (request count)
and throttling (response rate/bandwidth shaping). Adaptive rate limiting adjusts limits
based on upstream health — if upstream latency rises, tighten limits earlier
(API Gateway acting as circuit breaker triggering).

---

### ⚙️ How It Works (Mechanism)

```
REQUEST FLOW WITH TOKEN BUCKET RATE LIMITING:

Client → API Gateway

Gateway (Lua/plugin):
  1. Extract client ID (API key from header)
  2. Redis EVAL lua-script:
       local tokens = redis.call("HGET", key, "tokens")
       local last_refill = redis.call("HGET", key, "last_refill")
       local now = tonumber(ARGV[1])
       local rate = tonumber(ARGV[2])
       local capacity = tonumber(ARGV[3])
       -- refill tokens based on elapsed time
       local elapsed = now - last_refill
       local new_tokens = math.min(capacity, tokens + elapsed * rate)
       if new_tokens >= 1 then
           redis.call("HSET", key, "tokens", new_tokens - 1, "last_refill", now)
           return 1  -- allowed
       else
           return 0  -- rejected
       end
  3. If rejected: return HTTP 429, set Retry-After header
  4. If allowed: forward to backend

RESPONSE HEADERS (added by gateway):
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 23
  X-RateLimit-Reset: 1630000060
  Retry-After: 37     (only on 429)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Client sends 101st request in window:

1. API Gateway extracts: API key "key_abc123"
2. Redis: token bucket for "key_abc123": tokens = 0, last_refill was 2s ago
   Refill: 2s × 10 tokens/s = 20 tokens added, but capacity=100 → 20 tokens
   Request consumes 1 token: 19 remaining
   Wait — this was the 101st? Let's say limit is 10/min (Fixed Window):
   Redis: INCR "rl:key_abc123:2024-hour-minute" → 11 > 10 → REJECT

3. Gateway: HTTP 429 Too Many Requests
   Headers:
     X-RateLimit-Limit: 10
     X-RateLimit-Remaining: 0
     X-RateLimit-Reset: 1630000060  ← Unix timestamp of window reset
     Retry-After: 47               ← seconds until reset

4. Client should: parse Retry-After, wait, then retry
   Client should NOT: immediately retry (exponential backoff is safest)
```

---

### 💻 Code Example

```java
// Spring Boot — custom Token Bucket rate limiter using Redis

@Component
public class TokenBucketRateLimiter {

    private final RedisTemplate<String, String> redis;
    private final int capacity = 100;      // max burst
    private final double refillRate = 10;  // tokens per second

    public boolean isAllowed(String clientId) {
        String key = "rl:tb:" + clientId;
        long now = System.currentTimeMillis();

        // Atomic Lua script: check and consume one token
        String luaScript = """
            local tokens = tonumber(redis.call("HGET", KEYS[1], "tokens") or ARGV[1])
            local last   = tonumber(redis.call("HGET", KEYS[1], "last") or ARGV[2])
            local now    = tonumber(ARGV[2])
            local rate   = tonumber(ARGV[3])
            local cap    = tonumber(ARGV[1])
            local elapsed = (now - last) / 1000.0
            tokens = math.min(cap, tokens + elapsed * rate)
            if tokens >= 1.0 then
                tokens = tokens - 1
                redis.call("HSET", KEYS[1], "tokens", tokens, "last", now)
                redis.call("EXPIRE", KEYS[1], 3600)
                return 1
            else
                redis.call("HSET", KEYS[1], "tokens", tokens, "last", now)
                return 0
            end
            """;

        Long result = redis.execute(
            RedisScript.of(luaScript, Long.class),
            List.of(key),
            String.valueOf(capacity),
            String.valueOf(now),
            String.valueOf(refillRate)
        );
        return result != null && result == 1L;
    }
}

// Filter that applies rate limiting
@Component
public class RateLimitFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse res,
                                    FilterChain chain) throws IOException, ServletException {
        String apiKey = req.getHeader("X-API-Key");
        if (apiKey == null || !rateLimiter.isAllowed(apiKey)) {
            res.setStatus(429);
            res.setHeader("Retry-After", "10");
            res.setHeader("X-RateLimit-Limit", "100");
            res.getWriter().write("{\"error\": \"Rate limit exceeded\"}");
            return;
        }
        chain.doFilter(req, res);
    }
}
```

---

### ⚖️ Comparison Table

| Algorithm           | Boundary Attack | Burst Support | Memory      | Precision | Best For              |
| ------------------- | --------------- | ------------- | ----------- | --------- | --------------------- |
| **Fixed Window**    | ❌ Vulnerable   | ✅            | O(1)        | Low       | Simple limits         |
| **Sliding Log**     | ✅ Immune       | Partial       | O(requests) | High      | Low-volume accuracy   |
| **Sliding Counter** | ✅ Near-immune  | Partial       | O(1)        | Med-High  | Scalable accuracy     |
| **Token Bucket**    | ✅ Immune       | ✅ Controlled | O(1)        | High      | User-facing APIs      |
| **Leaky Bucket**    | ✅ Immune       | ❌            | O(queue)    | High      | Downstream protection |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                    |
| ------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Rate limiting = throttling                  | Rate limiting rejects (429). Throttling delays (slows down). Different responses           |
| Count requests per IP for security          | IP-based limits are easily bypassed by rotating IPs; use API keys + IP as secondary signal |
| Rate limits must be per-second              | Limits can be per minute, per hour, per day, or hierarchical (10/sec AND 1000/day)         |
| Redis INCR is always safe for rate limiting | INCR + check is NOT atomic; use INCR+EXPIRE in Lua script or SET with NX to avoid races    |

---

### 🚨 Failure Modes & Diagnosis

**Rate Limit Bypass at Distributed Gateway**

Symptom:
Client making 5x the declared limit without getting 429. Rate limit metrics look
correct on each individual node but total throughput is N×limit.

Root Cause:
Rate limit counter is in-process (memory) per gateway instance, not shared via Redis.
5 gateway nodes × 100 req/min limit = 500 effective req/min per client.

Diagnostic:

```
# Test: hit API 120 req/min (expect 429 at 101):
for i in {1..120}; do
  curl -w "%{http_code}" -H "X-API-Key: test123" https://api/endpoint
done
# If no 429s at 101+: rate limiter is NOT distributed

# Kong: check rate-limiting plugin config: "policy: redis"
# AWS API Gateway: check usage plan quota settings (gateway-level, not per instance)
```

Fix:
Use Redis as the shared rate limit counter backend. All gateway instances share state.
Use Lua scripts for atomic check-and-increment.

---

### 🔗 Related Keywords

- `API Throttling` — the related concept of slowing down (not blocking) excess requests
- `API Gateway` — the primary location where rate limiting is enforced at scale
- `Redis` — the standard distributed counter backend for rate limiting
- `Circuit Breaker` — a related pattern that stops sending to a failing backend

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ N requests per time window per client;   │
│              │ exceed → 429 Too Many Requests            │
├──────────────┼───────────────────────────────────────────┤
│ ALGORITHMS   │ Token Bucket (bursting, user APIs)        │
│              │ Leaky Bucket (smooth rate, downstream)    │
│              │ Sliding Counter (accurate, scalable)      │
├──────────────┼───────────────────────────────────────────┤
│ KEY HEADERS  │ X-RateLimit-Limit: N                      │
│              │ X-RateLimit-Remaining: M                  │
│              │ Retry-After: seconds-until-reset          │
├──────────────┼───────────────────────────────────────────┤
│ DISTRIBUTED  │ All nodes share Redis counter             │
│ IMPL         │ Lua script for atomic check+increment     │
├──────────────┼───────────────────────────────────────────┤
│ IDENTIFY BY  │ API key (preferred), user ID, IP (weak)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Quota enforcement with a bucket"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Throttling → Redis → Circuit Breaker  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A global API is deployed across 5 regions. Rate limit: 1000 req/min per API key. A client's requests are distributed across regions by latency routing: ~200 req/min per region. A centralized Redis in us-east-1 has 50ms latency from eu-west-1. At 200K req/s total, the per-request Redis overhead is prohibitive. Design a multi-region rate limiting architecture that is accurate within ±5%, handles regional Redis failure gracefully, and adds no more than 1ms to P99 latency.
