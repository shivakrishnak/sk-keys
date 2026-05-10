---
layout: default
title: "Rate Limiting (Microservices)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /microservices/rate-limiting-microservices/
id: MSV-042
category: Microservices
difficulty: ★★☆
depends_on: API Gateway (Microservices), Service Mesh (Microservices), HTTP & APIs
used_by: Circuit Breaker (Microservices), Bulkhead Pattern, Chaos Engineering
related: Timeout Strategy, Retry Strategy, Fallback Strategy
tags:
  - microservices
  - api
  - reliability
  - performance
  - intermediate
status: complete
version: 2
---

# MSV-032 - Rate Limiting (Microservices)

⚡ TL;DR - Rate limiting caps how many requests a service accepts per time window, protecting it from being overwhelmed by any single caller.

| #649            | Category: Microservices                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | API Gateway (Microservices), Service Mesh (Microservices), HTTP & APIs |                 |
| **Used by:**    | Circuit Breaker (Microservices), Bulkhead Pattern, Chaos Engineering   |                 |
| **Related:**    | Timeout Strategy, Retry Strategy, Fallback Strategy                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a payment service running at 1,000 requests/second normally. One busy morning a marketing email goes out and suddenly 50,000 customers hit "buy" simultaneously. Without any rate limiting, every microservice in the chain - payments, inventory, notifications - receives a tsunami of requests it was never sized to handle.

**THE BREAKING POINT:**
Threads exhaust, database connection pools drain, memory fills with pending work. The payment service slows, timeouts cascade upstream, and now even the 1,000 normal-rate requests that would have succeeded are failing. A single traffic spike has caused a total outage for all users.

**THE INVENTION MOMENT:**
This is exactly why rate limiting was created - to give each service a hard ceiling so no single caller, campaign, or bug can push it past its designed capacity.


**EVOLUTION:**
Rate limiting evolved from connection throttling (network layer, 1990s) to application-level HTTP API throttling. Token Bucket and Leaky Bucket algorithms (network engineering, 1980s) were adapted for HTTP APIs. GitHub popularised per-client rate limits with standard headers (X-RateLimit-Remaining, Retry-After) in 2011. AWS API Gateway's built-in rate limiting (2015) made it a managed service pattern. The discipline evolved from 'protect your servers from abuse' to 'implement fair multi-tenant resource sharing': per-client-tier limits, per-endpoint limits, and distributed rate limiting across instances.
---

### 📘 Textbook Definition

**Rate limiting** is a mechanism that restricts the number of requests a service processes within a defined time window (e.g., 500 req/sec per client). Requests exceeding the limit are rejected immediately, queued, or delayed rather than forwarded to downstream services. In microservices, rate limiting is applied at the API Gateway, service mesh sidecar, or within the service itself to enforce fair use, protect downstream capacity, and prevent denial-of-service conditions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Set a maximum speed at which any one caller can use your service.

**One analogy:**

> Think of a highway on-ramp with a traffic light. During rush hour, the light only lets one car onto the highway every 3 seconds - not because the road is blocked, but to prevent the merging wave from causing gridlock further down. Rate limiting is that on-ramp signal for your API.

**One insight:**
The key insight is that rate limiting protects the _provider_, not just the _consumer_. Returning a fast `429 Too Many Requests` to an overloading caller is far cheaper than letting that caller consume all your threads and slow down everyone else.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A service has finite processing capacity - threads, connections, CPU.
2. Any caller can accidentally or intentionally exceed that capacity.
3. Failing fast for the excess is cheaper than slow-failing for everyone.

**DERIVED DESIGN:**
Given these invariants, rate limiting must: track request counts per caller per window, enforce a limit, and respond immediately when exceeded - without blocking legitimate traffic.

Two primary algorithms exist:

**Token Bucket**: A bucket holds N tokens. Each request consumes one token. Tokens refill at a steady rate (e.g., 100/sec). Bursts are allowed up to bucket capacity; sustained overdrive is rejected. This is flexible - allows short bursts.

**Fixed Window Counter**: Count requests in a fixed time window (e.g., every second). Reset at the window boundary. Simple but has a "thundering herd" edge case at boundaries - a caller can do 2× the limit by clustering at the end of one window and start of the next.

**Sliding Window Log**: Track timestamps of each request. Count only those within the last N seconds. Accurate but memory-intensive at scale.

**THE TRADE-OFFS:**
**Gain:** Service stability under load; fair resource sharing; protection against misbehaving clients.
**Cost:** Legitimate traffic is dropped or delayed at peaks; client retry logic becomes mandatory; distributed rate limiting requires coordination across instances.

---

### 🧪 Thought Experiment

**SETUP:**
Your order service handles 200 req/sec and is rate-limited to exactly that. A consumer app has a bug that issues 10 parallel requests per user action instead of 1.

**WHAT HAPPENS WITHOUT RATE LIMITING:**
Each user action generates 10 requests. With 100 concurrent users, that's 1,000 req/sec - 5× capacity. Thread pool fills in seconds, new requests queue, queue fills, service starts refusing connections at the OS level. All 100 users see hanging pages or hard errors.

**WHAT HAPPENS WITH RATE LIMITING:**
The gateway sees that this client already used 200 tokens this second. Requests 201–1,000 receive immediate `429` responses. The order service itself never sees more than 200 req/sec. The 100 users whose requests made it through get normal responses; others see a clear "slow down" signal that the client app can handle gracefully.

**THE INSIGHT:**
Rate limiting converts an unpredictable capacity failure into a predictable protocol response. The system stays healthy; the burden shifts to callers to behave correctly.

---

### 🧠 Mental Model / Analogy

> A nightclub has a maximum occupancy of 200 people. A bouncer counts people going in and stops the queue when capacity is reached. People in the queue wait, or leave and try later.

- "Maximum occupancy" → rate limit (requests per second)
- "Bouncer" → rate limiting middleware (gateway or sidecar)
- "People in queue" → buffered or rejected requests
- "Nightclub fire code" → service capacity (threads, connections)
- "Count of people inside" → current request counter

Where this analogy breaks down: in software, a "person inside" (in-flight request) may finish in milliseconds, so capacity recovers much faster - making token-bucket burst behaviour critical to model correctly.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Rate limiting is like a speed governor on a car engine - it lets the engine run at full speed but prevents it from going past the safe maximum, no matter how hard you press the accelerator.

**Level 2 - How to use it (junior developer):**
Apply rate limiting at the API Gateway for all inbound traffic. Configure limits per client (by API key or IP), per endpoint, and per time window. Return `HTTP 429 Too Many Requests` with a `Retry-After` header when limits are exceeded. Log all rate-limited responses with client identity for abuse detection.

**Level 3 - How it works (mid-level engineer):**
Token bucket is the most common algorithm: each client has a bucket holding up to `burst_size` tokens; tokens refill at `rate` tokens/second. Redis (or a distributed counter) stores the token state. On each request: atomically check bucket, consume a token if available, reject otherwise. The atomic check+decrement is critical - a race condition allows two threads to both "see" a token and both consume it, exceeding the limit.

**Level 4 - Why it was designed this way (senior/staff):**
Distributed rate limiting is hard because each service instance sees only its own traffic. A naive per-instance limit of 100/sec with 5 instances gives 500/sec total - but one instance could handle 100 while others are idle, letting a single client hammer one instance. Centralized counters (Redis) solve coordination but add latency; approximate local counters (each node tracks N/instances) sacrifice precision for speed. The tradeoff between exact enforcement and low overhead defines the algorithm choice.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│            Rate Limiting - Token Bucket Flow            │
└─────────────────────────────────────────────────────────┘

Client Request
     │
     ▼
┌──────────────┐    Lookup client bucket state
│ API Gateway  │──────────────────────────────► Redis
│  (sidecar)   │◄──────────────── { tokens: 47, last: T }
└──────────────┘
     │
     │  tokens > 0?
     ├──YES──► Decrement tokens, forward request
     │              │
     │              ▼
     │         Upstream Service → Response → Client
     │
     └──NO───► Return HTTP 429
               Header: Retry-After: 1
               Body: { error: "rate_limit_exceeded" }
```

**Token refill calculation:**

```
elapsed = now - last_refill_time
new_tokens = min(bucket_max, current_tokens + elapsed × rate)
```

This calculation runs atomically in Redis using a Lua script to prevent race conditions.

**Sliding window log alternative:**
Stores a sorted set of request timestamps per client in Redis. Each request:

1. Remove timestamps older than `window_size`
2. Count remaining entries
3. If count < limit: add current timestamp, allow
4. If count ≥ limit: reject with TTL of oldest entry

**Distributed considerations:**

- Use Redis `INCR` with `EXPIRE` for simple fixed-window counting
- Use Lua scripts for atomic token bucket operations
- Gossip-based approximate counting (Twitter Finagle approach) avoids Redis as a single point of failure

**Happy path:** Client gets `200 OK` within normal rate.
**Error path:** Client gets `429` with `X-RateLimit-Limit: 100`, `X-RateLimit-Remaining: 0`, `Retry-After: 1` headers, enabling smart client backoff.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Client] → [DNS / Load Balancer] → [API Gateway]
  → [Rate Limit Check ← YOU ARE HERE]
  → [Auth / Routing] → [Upstream Service]
  → [Response] → [Client]
```

**FAILURE PATH:**

```
[Rate Limiter fails open] → [No limit enforced]
  → [Service overload] → [Cascading failure]

[Rate Limiter fails closed] → [All requests rejected]
  → [Total outage for this client]
```

**WHAT CHANGES AT SCALE:**
At 10,000 req/sec, every Redis call adds ~1ms latency; a 1ms check per request at 10k RPS means the rate limiter itself becomes a bottleneck. At 100k RPS, teams switch to in-process approximate counters with periodic Redis sync, accepting 1–5% overcounting for 10× throughput gain. At 1M RPS, token-bucket state is sharded across Redis clusters by client ID hash.

---

### 💻 Code Example

**Example 1 - Wrong: no rate limiting at service level:**

```java
@RestController
public class OrderController {
    @PostMapping("/orders")
    public Order createOrder(@RequestBody OrderRequest req) {
        // No rate check - any caller can hammer this
        return orderService.create(req);
    }
}
```

**Example 2 - Right: Resilience4j rate limiter:**

```java
@Bean
public RateLimiter orderRateLimiter(
    RateLimiterRegistry registry) {
  return registry.rateLimiter("orders",
    RateLimiterConfig.custom()
      .limitRefreshPeriod(Duration.ofSeconds(1))
      .limitForPeriod(500)       // 500 req/sec
      .timeoutDuration(Duration.ZERO) // fail-fast
      .build());
}

@PostMapping("/orders")
public ResponseEntity<Order> createOrder(
    @RequestBody OrderRequest req) {
  return Try.of(RateLimiter.decorateSupplier(
        limiter, () -> orderService.create(req)))
    .map(o -> ResponseEntity.ok(o))
    .recover(RequestNotPermitted.class,
        e -> ResponseEntity.status(429)
          .header("Retry-After", "1").build())
    .get();
}
```

**Example 3 - Production: Redis token bucket (Lua):**

```lua
-- redis_rate_limit.lua
-- KEYS[1] = bucket key, ARGV = rate, burst, now
local tokens_key = KEYS[1]
local last_key = KEYS[1] .. ":last"
local rate = tonumber(ARGV[1])
local burst = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local last = tonumber(redis.call("get", last_key)) or now
local tokens = tonumber(redis.call("get", tokens_key))
                or burst

local elapsed = now - last
local new_tokens = math.min(burst,
                    tokens + elapsed * rate)
if new_tokens >= 1 then
  redis.call("set", tokens_key, new_tokens - 1)
  redis.call("set", last_key, now)
  return 1  -- allowed
else
  return 0  -- rejected
end
```

---

### ⚖️ Comparison Table

| Algorithm             | Burst Support | Memory                | Accuracy | Best For                             |
| --------------------- | ------------- | --------------------- | -------- | ------------------------------------ |
| **Token Bucket**      | Yes           | Low (2 values/client) | High     | Most APIs - allows legitimate bursts |
| Fixed Window          | No            | Very Low (1 counter)  | Medium   | Simple use cases, high traffic       |
| Sliding Window Log    | No            | High (N timestamps)   | Exact    | Billing / strict SLA enforcement     |
| Sliding Window Approx | Partial       | Low                   | ~99%     | High-throughput with tolerable error |
| Leaky Bucket          | No (smoothed) | Low                   | High     | Smoothing output rate to downstream  |

**How to choose:** Use **token bucket** for most API rate limiting (allows bursts within capacity). Use **sliding window log** only when exact enforcement has billing or legal consequences.

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                       |
| -------------------------------------------------- | ----------------------------------------------------------------------------- |
| Rate limiting prevents all abuse                   | It limits request volume - not malicious payload content or auth bypass       |
| One global limit per service is sufficient         | Limits must be per-client (API key/IP) or a single bot consumes all capacity  |
| Rate limiting guarantees service stability         | Overlong-running requests still exhaust threads even below rate limit         |
| The limit should equal measured peak capacity      | Limit should be 70–80% of capacity to leave headroom for overhead and retries |
| 429 is a client error - the client broke something | 429 means "slow down" - it is a normal flow control signal, not an error      |

---

### 🚨 Failure Modes & Diagnosis

**Rate Limiter Bypass via Clock Skew**

**Symptom:** Service receives bursts above configured limit; some clients consistently bypass throttling.

**Root Cause:** Distributed instances use local clocks for token refill. A 50ms skew across 5 instances means each refills at slightly different times, allowing a client to hit all instances at refill boundaries.

**Diagnostic Command:**

```bash
redis-cli --stat | grep "keys"
# Check if rate limit keys are expiring correctly
redis-cli TTL "ratelimit:client123"
```

**Fix:** Use Redis-based centralized token state with server-side timestamps only. Never use client-reported timestamps.

**Prevention:** Always compute elapsed time server-side using Redis clock (`TIME` command).

---

**Rate Limiter as Single Point of Failure**

**Symptom:** When Redis is down, all requests are rejected (fail-closed) or all limits are ignored (fail-open).

**Root Cause:** Rate limiter has no fallback behaviour defined.

**Diagnostic Command:**

```bash
redis-cli ping  # Check Redis availability
# Check application logs for connection errors
```

**Fix:** Configure fail-open with circuit breaker around the rate limit check - if Redis is unreachable, allow traffic but alert.

**Prevention:** Use Redis Sentinel or Cluster for HA; define explicit fail-open/closed policy at service start.

---

**Noisy Neighbour (Shared Limit)**

**Symptom:** Service A's traffic spike causes throttling for Service B sharing the same rate limit key.

**Root Cause:** Rate limit key is too coarse - multiple distinct callers share a single counter.

**Diagnostic Command:**

```bash
# Inspect rate limit key naming
redis-cli KEYS "ratelimit:*" | head -20
```

**Fix:** Include caller identity in key: `ratelimit:{service}:{api_key}:{endpoint}`.

**Prevention:** Design rate limit key schema at inception to include client ID, endpoint, and time window.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `API Gateway (Microservices)` - the usual enforcement point for rate limits
- `HTTP & APIs` - 429 status code and `Retry-After` header semantics
- `Service Mesh (Microservices)` - sidecar-level rate limiting without code changes

**Builds On This (learn these next):**

- `Circuit Breaker (Microservices)` - stops calling a downstream that's already failing
- `Bulkhead Pattern` - isolates thread pools so one caller can't exhaust shared resources
- `Chaos Engineering` - tests whether rate limits hold under simulated failure

**Alternatives / Comparisons:**

- `Timeout Strategy` - limits how long a request runs, not how many run
- `Retry Strategy` - what clients do after receiving 429
- `Token Bucket` (System Design) - the specific algorithm used in most implementations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Cap on requests per client per time window│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single caller can exhaust shared service  │
│ SOLVES       │ capacity for all other callers            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Returning 429 fast is cheaper than slow-  │
│              │ failing for everyone under overload       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Public APIs, multi-tenant services, or    │
│              │ any service with finite thread capacity   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Internal services with trusted, known-    │
│              │ rate callers (overhead may not be worth it│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Service stability vs legitimate burst     │
│              │ traffic being dropped                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The bouncer that keeps the nightclub from│
│              │  burning down"                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Token Bucket → Circuit Breaker → Bulkhead │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Rate limiting is fair resource allocation, not just abuse prevention. A rate limit tells each client: 'This is your guaranteed share of capacity.' Without rate limits, a single large client can consume all available capacity, starving other clients. The same principle governs CPU scheduling (time slicing ensures no process monopolises the CPU), database connection pools (max connections per user), and network QoS (traffic shaping for bandwidth fairness).

**Where else this pattern appears:**
- **Database query throttling:** Limiting concurrent queries per session is rate limiting at the database level - protecting shared resources from individual query storms.
- **Email sending:** Email providers (SendGrid, Mailgun) rate limit per API key to protect deliverability reputation - rate limiting applied to communication channels.
- **CI/CD build systems:** GitHub Actions minutes and Jenkins concurrent build limits are rate limiting applied to compute resource allocation per account.

---

### 💡 The Surprising Truth

The most counterintuitive property of rate limiting is that it can make systems less reliable when misconfigured. A rate limit set below legitimate peak demand rejects valid requests during high-traffic events (product launches, viral posts). The most common failure is setting limits based on average traffic rather than peak demand: a system handling 100 req/s average but 500 req/s peak needs a rate limit of 500, not 100. Teams that set limits based on average traffic reject 80% of legitimate peak requests and provide no protection value to their users - the worst of both worlds.
---

### 🧠 Think About This Before We Continue

**Q1.** Your rate limiter uses a fixed-window counter at 100 req/sec. A client knows your window resets at each second boundary. They send 100 requests at T=0.99s and another 100 at T=1.01s. Both windows show 100 requests - within limit - yet you just processed 200 requests in 20ms. Trace exactly why this happens, which algorithm eliminates it, and what cost that algorithm pays.

*Hint:* Think about what fixed-window means: the counter resets at each second boundary. A client who knows the exact reset time sends N requests just before the reset and N more just after, achieving 2N requests in a very short window while both windows show N (within limit). Explore how a sliding window (count requests in the last N seconds continuously, not since the last reset) eliminates this boundary exploit, and what the implementation cost difference is between a Redis atomic counter (fixed window) and a Redis sorted set with timestamps (sliding window).

**Q2.** You have 10 service instances each enforcing a local token bucket at 100 req/sec. A bot distributes exactly 10 req/sec to each instance - hitting the per-instance limit at exactly 10% utilisation. The service's actual capacity is 100 req/sec total but the bot is sending 100 req/sec and none are being rate limited. What architectural change fixes this, and what does it cost in latency?

*Hint:* Think about what per-instance rate limiting means: each instance has its own independent counter, with no coordination. A client distributing 10 req/s to each of 10 instances sends 100 req/s total but never exceeds any single instance's 100 req/s limit. Explore whether a centralised rate limiter (Redis INCR shared across all instances, checked on each request) solves this, and what the latency cost of a Redis round-trip is on every rate limit check (typically 1-2ms, multiplied by all requests).

**Q3 (Design Trade-off):** A DDoS attack uses 10,000 unique bot IPs, each sending exactly 99 req/s (1 below your per-IP limit of 100). Collectively they generate 990,000 req/s. No individual IP hits the rate limit. Your service is overwhelmed. Design additional protection layers that handle this scenario.

*Hint:* Think about what per-IP rate limiting cannot defend against: a distributed attack where each attacker stays below the per-IP limit. Explore whether aggregate rate limiting (total requests across all clients caps total service throughput), IP reputation filtering (blocking known bad IPs via threat intelligence), bot detection (browser fingerprinting, CAPTCHA on suspicious traffic), and geographic rate limiting (block entire ASNs under active attack) provide defense-in-depth. Note these are WAF/CDN layer controls, not just application-level rate limiting.
