---
layout: default
title: "Rate Limiting (System)"
parent: "System Design"
nav_order: 703
permalink: /system-design/rate-limiting/
number: "703"
category: System Design
difficulty: ★★☆
depends_on: "Token Bucket, Leaky Bucket, Capacity Planning"
used_by: "API Gateway, Thundering Herd (System), Capacity Planning"
tags: #intermediate, #distributed, #architecture, #reliability, #performance
---

# 703 — Rate Limiting (System)

`#intermediate` `#distributed` `#architecture` `#reliability` `#performance`

⚡ TL;DR — **Rate Limiting** controls how many requests a client can make in a given time window, protecting systems from abuse, overload, and ensuring fair resource sharing across all clients.

| #703            | Category: System Design                                  | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Token Bucket, Leaky Bucket, Capacity Planning            |                 |
| **Used by:**    | API Gateway, Thundering Herd (System), Capacity Planning |                 |

---

### 📘 Textbook Definition

**Rate Limiting** is a technique that controls the frequency of operations a caller can perform against a system within a defined time window. It serves multiple purposes: protecting server resources from exhaustion (availability), preventing abuse and denial-of-service attacks (security), enforcing business quotas (monetisation), and ensuring equitable resource distribution across clients (fairness). Common algorithms: **Fixed Window** (N requests per window), **Sliding Window** (N requests per rolling window), **Token Bucket** (burst-friendly: accumulate tokens, spend on requests), **Leaky Bucket** (rate-smoothing: fixed output rate), and **Sliding Window Log** (exact, memory-intensive). Rate limiting can be applied at multiple layers: client-side (self-throttle), API gateway (per-key, per-IP), service mesh, and at individual service endpoints. Exceeded limits return HTTP 429 Too Many Requests with a `Retry-After` header.

---

### 🟢 Simple Definition (Easy)

Rate Limiting: you can only knock on the door 10 times per minute, not 10,000. The bouncer at the API door says "you've had your 10 requests this minute — come back in 30 seconds." It stops one angry user (or a bug) from flooding the system and causing downtime for everyone else.

---

### 🔵 Simple Definition (Elaborated)

GitHub's API: 5,000 requests/hour for authenticated users, 60/hour for unauthenticated. Twitter's API: tiers with different limits per endpoint. Stripe's API: 100 reads/second, 100 writes/second. These limits protect the service from single clients consuming all capacity. Without rate limiting: one misconfigured client in a retry loop makes 100,000 requests/minute → database overwhelmed → everyone gets 503. With rate limiting: that client gets 429 after its 100th request; the remaining 999 clients are unaffected.

---

### 🔩 First Principles Explanation

**Rate limiting algorithms compared:**

````
ALGORITHM 1: FIXED WINDOW COUNTER

  Implementation: counter per client per time window.
  Window: 1 minute. Limit: 100 requests.

  Client A in window [12:00:00 - 12:00:59]:
    Request 1-100: allowed (counter 1-100)
    Request 101+: rejected (429)

  At 12:01:00: counter resets to 0.

  PROBLEM — Boundary burst (the "double hit" attack):
    Client sends 100 requests at 12:00:50 (window 1, last 10 seconds)
    Client sends 100 requests at 12:01:00 (window 2, first 1 second)
    Result: 200 requests in 10 seconds (2× the intended 100/minute rate)
    The window reset allows a burst at every window boundary.

ALGORITHM 2: SLIDING WINDOW LOG

  Implementation: store timestamp of each request in sorted set.
  On each request: count timestamps in last 60 seconds.
  If count >= 100: reject.

  Timeline:
    12:00:00 - 12:00:59: 100 requests logged
    12:00:45: request 101 → count timestamps in [11:59:45 - 12:00:45] = 100 → reject ✓
    12:01:00: request 102 → count timestamps in [12:00:00 - 12:01:00] = 100 → reject ✓
    12:01:05: request 103 → timestamps in [12:00:05 - 12:01:05] = 99 (12:00:00 dropped) → allow ✓

  ADVANTAGE: Exact sliding window. No boundary burst.
  PROBLEM: Memory usage: O(max_requests_per_window) per client.
    100 requests/minute × 1 million clients = 100M timestamps in memory.
    Redis sorted set: ~70 bytes/entry → 7 GB for this example.

ALGORITHM 3: SLIDING WINDOW COUNTER (approximate sliding window)

  Hybrid: fixed window counters + weighted overlap.

  Formula:
    current_window_count + previous_window_count × (overlap_fraction)

  Example (100 req/min limit):
    Previous window [11:59:00-12:00:00]: 80 requests
    Current window [12:00:00-12:01:00]: 60 requests (so far)
    Current time: 12:00:45 (75% into current window)
    Overlap: previous window overlaps 25% (1 - 0.75)

    Estimated request rate = 60 + 80 × 0.25 = 60 + 20 = 80 requests
    Under limit (80 < 100) → allow

  ADVANTAGE: O(1) memory per client. Good accuracy (~0.003% error rate).
  COMMONLY USED in production (Cloudflare, Nginx rate limiting).

ALGORITHM 4: TOKEN BUCKET
  See keyword #704 — Token Bucket for full detail.
  Key property: allows controlled bursts (accumulate tokens during quiet periods).

ALGORITHM 5: LEAKY BUCKET
  See keyword #705 — Leaky Bucket for full detail.
  Key property: smooths output to constant rate regardless of input bursts.

DISTRIBUTED RATE LIMITING (multi-server):

  Problem: 10 API gateway instances. Rate limit: 100 req/min per user.

  Option A: Local counter (per instance).
    Each instance: 100 req/min limit.
    User can hit: 10 × 100 = 1,000 requests/min total.
    NOT a rate limit — just 10 independent limits.

  Option B: Centralized counter (Redis).
    All instances: share counter in Redis.
    Redis: single source of truth.
    Implementation: INCR + EXPIRE in Lua script (atomic).

    Lua script (atomic check-and-increment):
    ```lua
    local key = KEYS[1]
    local limit = tonumber(ARGV[1])
    local expiry = tonumber(ARGV[2])

    local count = redis.call("INCR", key)
    if count == 1 then
      redis.call("EXPIRE", key, expiry)
    end
    if count > limit then
      return 0  -- reject
    end
    return 1    -- allow
    ```

    Trade-off: network roundtrip to Redis on every request (~1ms latency added).

  Option C: Approximate distributed (local + sync).
    Each instance: local counter.
    Every 100ms: sync with Redis (add local count to Redis, get updated total).
    Allow if local estimate < limit.
    Trade-off: allows slight over-limit (up to: instances × 100ms traffic).
    Acceptable for most rate limiting (not for exact quota enforcement).

RATE LIMIT RESPONSE FORMAT (HTTP 429):

  HTTP/1.1 429 Too Many Requests
  Content-Type: application/json
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1672531260       ← Unix timestamp when window resets
  Retry-After: 30                     ← Seconds until retry allowed

  Body:
  {
    "error": "rate_limit_exceeded",
    "message": "Too many requests. Limit: 100/min.",
    "retry_after": 30
  }
````

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Rate Limiting:

- One misbehaving client → database overload → all clients degraded
- DDoS trivial: attacker sends unlimited requests
- Runaway retry logic (bugs) → infinite request loops → self-inflicted DDoS

WITH Rate Limiting:
→ Noisy neighbours isolated: one client's traffic cannot affect others
→ DDoS mitigation: attacker's requests throttled at the gateway
→ Fair resource allocation: each client gets their contracted share

---

### 🧠 Mental Model / Analogy

> A highway toll booth has a limit: each lane processes one car every 3 seconds. If 100 cars arrive simultaneously, 99 must queue. The booth doesn't stop working — it just processes at a fixed rate. Cars that arrive faster than the rate are queued (leaky bucket) or rejected after the queue fills (rate limit). The highway can serve everyone — just not all at once.

"Highway toll booth" = API endpoint with a rate limit
"3 seconds per car" = rate limit (X requests per second)
"100 cars arriving simultaneously" = burst traffic / DDoS
"Queue 99 cars" = request queuing / backpressure
"Queue fills up → turn away cars" = 429 Too Many Requests response

---

### ⚙️ How It Works (Mechanism)

**Spring Boot: rate limiter with Redis (Bucket4j + Redis):**

```java
@RestController
public class ApiController {

    @Autowired
    private ProxyManager<String> proxyManager;

    // Rate limit config: 100 requests per minute per API key
    private BucketConfiguration createBucketConfiguration() {
        return BucketConfiguration.builder()
            .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
            .build();
    }

    @GetMapping("/api/data")
    public ResponseEntity<String> getData(
            @RequestHeader("X-API-Key") String apiKey) {

        // Get or create bucket for this API key (stored in Redis):
        BucketProxy bucket = proxyManager.builder()
            .build(apiKey, this::createBucketConfiguration);

        ConsumptionProbe probe = bucket.tryConsumeAndReturnRemaining(1);

        if (probe.isConsumed()) {
            // Request allowed:
            return ResponseEntity.ok()
                .header("X-RateLimit-Remaining",
                    String.valueOf(probe.getRemainingTokens()))
                .body(fetchData());
        } else {
            // Rate limit exceeded:
            long retryAfterSeconds = probe.getNanosToWaitForRefill() / 1_000_000_000;
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
                .header("Retry-After", String.valueOf(retryAfterSeconds))
                .header("X-RateLimit-Remaining", "0")
                .body("{\"error\": \"rate_limit_exceeded\"}");
        }
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Client (API caller)
        │ (request)
        ▼
API Gateway ──► Rate Limiting ◄──── (you are here)
                (check: allowed?)
                │               │
                │ (rejected)     │ (allowed)
                ▼               ▼
         429 Response    Token Bucket / Leaky Bucket
                              │
                              ▼
                         Backend Service
                              │
                              ▼
                      Capacity Planning
                      (rate limit ceiling)
```

---

### 💻 Code Example

**Node.js: sliding window counter in Redis:**

```javascript
const redis = require("redis");
const client = redis.createClient();

async function isRateLimited(userId, limitPerMinute = 100) {
  const now = Date.now();
  const windowMs = 60_000; // 1 minute

  const prevWindowKey = `rl:${userId}:${Math.floor((now - windowMs) / windowMs)}`;
  const currWindowKey = `rl:${userId}:${Math.floor(now / windowMs)}`;

  // Atomic sliding window calculation via Lua:
  const luaScript = `
    local prev_count = tonumber(redis.call('GET', KEYS[1]) or 0)
    local curr_count = tonumber(redis.call('INCR', KEYS[2]))
    if curr_count == 1 then
      redis.call('EXPIRE', KEYS[2], 120)
    end
    local overlap = tonumber(ARGV[1]) / 1000   -- fraction of prev window overlap
    local estimated = curr_count + prev_count * overlap
    return {estimated, curr_count}
  `;

  const windowPosition = now % windowMs;
  const prevOverlapFraction = windowMs - windowPosition; // ms remaining in prev window

  const [estimated] = await client.eval(
    luaScript,
    2,
    prevWindowKey,
    currWindowKey,
    String(prevOverlapFraction),
  );

  return estimated > limitPerMinute;
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rate limiting always uses a fixed "per second" window | Rate limits can be per second, per minute, per hour, per day, or tiered (e.g., 100/min AND 1000/hour AND 10000/day). Multiple window sizes allow burst tolerance at the short scale while enforcing fairness at the longer scale                                            |
| 429 response means the server is down                 | 429 Too Many Requests means only that this specific client has hit its rate limit. The server is healthy and serving other clients normally. Clients should read the Retry-After header and back off, not retry immediately (which would be recursive rate limit violation) |
| Rate limiting and circuit breakers do the same thing  | Rate limiting: controls how fast a CLIENT can send requests. Circuit breaker: prevents a CLIENT from sending requests to a FAILING SERVICE. Rate limiting is inbound request governance; circuit breaker is outbound call protection. Both are needed                       |
| Rate limiting at the application layer is sufficient  | Application-layer rate limiting can be bypassed if an attacker controls many IPs or API keys. DDoS protection requires network-layer rate limiting (AWS Shield, Cloudflare) which operates before traffic reaches your application. Layer the defences                      |

---

### 🔥 Pitfalls in Production

**Retry storms from synchronised Retry-After:**

```
PROBLEM: All clients retry at exactly the same time

  Scenario: 10,000 API clients, rate limit = 100 req/min per client.
  At 12:00:00: all 10,000 clients start a batch job.
  Requests: 10,000 × 100 = 1M requests in the first minute.
  Server capacity: 500,000 req/min.
  Response: 500,000 get 429 with "Retry-After: 60" (window resets in 60 seconds).

  At 12:01:00:
    500,000 clients receive "Retry-After: 60" set at 12:00:00.
    ALL 500,000 clients retry simultaneously at 12:01:00.
    + 500,000 new requests from continued first batch.
    = 1M simultaneous requests again → thundering herd → cascade.

SOLUTION: Add jitter to Retry-After response:

  BAD:
    Retry-After: 60  // all clients retry at T+60s

  GOOD:
    // Server-side: add random jitter to Retry-After:
    int jitter = ThreadLocalRandom.current().nextInt(0, 30);
    response.setHeader("Retry-After", String.valueOf(60 + jitter));
    // Clients spread retries over 60-90s window → no thundering herd

BETTER: Exponential backoff with jitter on the client side:

  retry_delay = min(cap, base * 2^attempt) + random(0, base)
  // Each client independently randomises → natural desynchronization
```

---

### 🔗 Related Keywords

- `Token Bucket` — burst-friendly rate limiting algorithm (accumulate capacity during quiet periods)
- `Leaky Bucket` — rate-smoothing algorithm (constant output regardless of burst input)
- `Capacity Planning` — rate limit ceiling is determined by capacity planning
- `Thundering Herd (System)` — Retry-After synchronisation causes thundering herd
- `Circuit Breaker` — protects downstream services from being overwhelmed (complementary)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Control request frequency per client to   │
│              │ prevent overload and ensure fairness      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Public APIs; protecting downstream        │
│              │ services; multi-tenant systems            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Fixed window without jitter; Retry-After  │
│              │ without randomisation (causes stampede)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One driver can't use every lane of the   │
│              │  highway simultaneously."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Token Bucket → Leaky Bucket               │
│              │ → Distributed Rate Limiting               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing rate limiting for a REST API used by 100,000 developers. Each developer gets 1,000 requests/hour. An API gateway has 5 instances. Describe the full architecture: where does the rate limit state live? What happens if Redis goes down? Should you fail open (allow all requests) or fail closed (reject all requests) when the rate limiter itself fails? What are the trade-offs of each failure mode?

**Q2.** Compare Fixed Window and Sliding Window Counter rate limiting for an e-commerce checkout endpoint. The limit is 10 checkout attempts per minute per user (anti-fraud measure). Construct a specific scenario where Fixed Window allows a user to make 20 checkout attempts in 10 seconds (the boundary burst attack). Show numerically exactly how many requests pass through in the fixed window example. Then explain why Sliding Window Counter prevents this specific attack.
