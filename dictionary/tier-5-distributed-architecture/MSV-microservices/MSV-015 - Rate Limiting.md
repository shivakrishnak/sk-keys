---
id: MSV-015
title: Rate Limiting
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-012, MSV-002, MSV-008
used_by: MSV-044
related: MSV-012, MSV-017, MSV-044, MSV-045, MSV-043
tags:
  - microservices
  - reliability
  - intermediate
  - resilience
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /microservices/rate-limiting/
---

# MSV-015 - Rate Limiting

⚡ TL;DR - Rate Limiting is the mechanism for capping
how many requests a client can make to a service within
a time window. It protects services from overload due to
misbehaving clients, traffic spikes, and runaway callers -
returning HTTP 429 to excess requests instead of crashing.

| #015 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | API Gateway, Microservices Architecture, Health Check Patterns | |
| **Used by:** | Circuit Breaker | |
| **Related:** | API Gateway, Retry Strategy, Circuit Breaker, Bulkhead Pattern, Resilience4j | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your Public API is accessed by 500 customers. One customer
has a bug: their background job sends 50,000 requests per
minute instead of 50. This one customer consumes all 100
threads on your API service. The other 499 customers get
timeouts. Your service crashes. Post-mortem reveals:
one bad actor (even a well-intentioned one) could take
down the service for everyone.

**THE SECONDARY PROBLEM:**
A legitimate customer with a flash sale drives 10x traffic
in 30 seconds. Your service cannot auto-scale in time
(new pods take 90s to become ready). Service crashes,
wasting the customers' sale opportunity.

**THE BREAKING POINT:**
Without rate limiting, every client is trusted to behave
reasonably. The first misbehaving client (bug, attack,
flash sale) exhausts shared capacity and triggers a
platform-wide outage.

**THE INVENTION MOMENT:**
Rate limiting is the first line of defence: before doing
any work, check if the client has exceeded their quota.
Excess requests get HTTP 429 (Too Many Requests) immediately
- no thread pool consumed, no database query, no CPU cost.

---

### 📘 Textbook Definition

**Rate Limiting** is a control mechanism that enforces
a maximum request rate for a client, service, or endpoint
within a defined time window. When a client exceeds its
allowed rate, excess requests are rejected with HTTP 429
(Too Many Requests) and a `Retry-After` header indicating
when the client can try again. Rate limiting protects
services from overload, ensures equitable access across
clients, and provides a cost control mechanism for APIs
with per-request billing. The main algorithms are: Token
Bucket, Sliding Window, Fixed Window, and Leaky Bucket,
each with different burst-handling characteristics.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Rate limiting is a quota system: each client gets N
requests per second/minute. Exceed the quota and requests
are rejected immediately - no resources consumed.

**One analogy:**
> A coffee shop gives each loyalty customer one free
> refill per hour. Attempting a second refill gets a
> friendly "try again in 45 minutes". The policy prevents
> one very thirsty customer from emptying the coffee
> machine for everyone else. The "refill counter" is
> the token bucket; the "45 minutes" is the Retry-After
> header.

**One insight:**
Rate limiting rejects work BEFORE it starts. This is
fundamentally different from a circuit breaker (which
fails fast after downstream failure) or a bulkhead
(which limits concurrent work). Rate limiting's cost
is near-zero: a counter check and an early 429 return.

---

### 🔩 First Principles Explanation

**THE FOUR ALGORITHMS:**

```
FIXED WINDOW:
──────────────────
[00:00 - 00:59]: 100 allowed, counter=0
  Request 1..100: ALLOWED, counter 1..100
  Request 101: REJECTED (429)
[01:00 - 01:59]: counter reset to 0

Problem: boundary burst - 100 requests at 00:59,
  100 more at 01:00 = 200 requests in 2 seconds.
  Server sees 2x capacity despite "100/minute" limit.

SLIDING WINDOW LOG:
─────────────────────
  Store timestamp of each request
  Count requests in last 60 seconds
  Reject if count >= 100
  Accurate but O(N) memory per client

SLIDING WINDOW COUNTER (hybrid):
─────────────────────────
  Two counters: current minute + previous minute
  Weighted: prev_count * (1 - elapsed) + curr_count
  O(1) per client, good burst control

TOKEN BUCKET:
──────────────
  Bucket holds max N tokens (burst capacity)
  Tokens added at rate R per second
  Each request consumes 1 token
  Reject if bucket empty
  Allows bursts up to bucket size, then enforces rate

LEAKY BUCKET:
──────────────
  Queue requests at burst rate
  Process at constant output rate
  Smooths bursty traffic to steady stream
  Best for: traffic shaping (not just rate limiting)
```

**WHERE RATE LIMITING LIVES:**

```
API Gateway (external-facing):
  Protects from external clients, bots, DDoS
  Keyed by: API key, user ID, IP address
  Example: 100 req/min per API key

Service-to-Service (internal):
  Protects services from misbehaving callers
  Keyed by: calling service name, user context
  Example: payment-service allows max 20 req/s
  from order-service (prevents data pipeline bugs)

Per-endpoint:
  Different limits for different endpoints
  POST /payments: 10/min (expensive operation)
  GET /status:    1000/min (cheap read)
```

---

### 🧪 Thought Experiment

**TOKEN BUCKET SIMULATION:**

```
Config: bucket=10 tokens, refill=1 token/second

Time 0s:   bucket=10
  Burst of 15 requests arrives
  Request 1-10: ALLOWED (consumes all tokens)
  Request 11-15: REJECTED (429)

Time 1s:   bucket=1 (1 token refilled)
  1 request ALLOWED

Time 10s:  bucket=10 (max capacity restored)
  Next burst of 10 can proceed

USE CASE: SMS verification API
  Allow burst: user can retry 3 times quickly
    after a phone typo (bucket=3)
  Enforce rate: no more than 1/min overall
    to prevent SMS bombing (refill=1/60s)
  Result: bucket=3, refill=1/60s
    allows 3 quick retries, then slows to
    1 per minute for extended abuse prevention
```

---

### 🧠 Mental Model / Analogy

> Rate limiting is like a highway on-ramp metering light.
> The light turns green every N seconds (token refill
> rate), allowing one car per green (token consumption).
> Cars that arrive when the light is red must wait
> (queued) or are turned away (rejected with 429).
> The number of green flashes per hour (rate) and the
> initial green count at light startup (burst bucket size)
> are the two knobs to configure.

Where this breaks down: rate limiting at the API Gateway
is per-request (single ramp), but at the service level
you may need distributed rate limiting where multiple
instances share a counter (Redis) to enforce the global
limit - one ramp per lane, but all lanes share the same
total allowance.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Rate limiting says "you can make up to N requests per
minute". If you send more, you get a 429 error and a
message saying when to try again. It prevents one customer
from monopolising the service.

**Level 2 - How to use it (junior developer):**
In Spring Cloud Gateway: add `RequestRateLimiter` filter
with a `RedisRateLimiter` bean. Configure replenishRate
(tokens per second) and burstCapacity (max burst tokens).
Redis stores the per-client counter; all gateway instances
share a global counter.

**Level 3 - How it works (mid-level engineer):**
Spring Cloud Gateway's `RedisRateLimiter` uses a Lua
script in Redis implementing the token bucket algorithm.
The Lua script is atomic - no race conditions between
multiple gateway instances. Key: `request_rate_limiter
.{client-id}.tokens` and `.timestamp`. On each request:
compute elapsed time, refill tokens (min(elapsed * rate,
burst)), check if tokens > 0, decrement and allow or reject.

**Level 4 - Why it was designed this way (senior/staff):**
Distributed rate limiting requires atomic counter management.
Naive approach: increment a Redis counter and check limit.
Race condition: two gateway instances both check (counter=99
< 100), both increment, counter becomes 101. Fix: Lua
script in Redis (single-threaded, atomic execution) or
Redis INCR + EXPIRE. Token bucket via Lua is the production
choice because it handles the refill calculation atomically.
Note: Redis adds ~1ms latency per request for the counter
check - this is the cost of distributed rate limiting.

**Level 5 - Mastery (distinguished engineer):**
At large scale, Redis becomes the bottleneck for rate
limiting (all gateway instances serialize on Redis for
each request). Solutions: (1) Local token bucket in each
gateway instance (no Redis latency), with 20% overshoot
accepted as trade-off; (2) Redis Cluster sharding by
client ID; (3) Sliding window with approximate counting
via Redis HyperLogLog for very high cardinality client
sets. For multi-region, you must choose: global limit
(higher latency, cross-region Redis replication) or
regional limit (lower latency, each region gets N/regions
quota). Cloudflare uses a local token bucket per PoP
for performance, accepting ~5% overshoot at boundary.

---

### ⚙️ How It Works (Mechanism)

**SPRING CLOUD GATEWAY RATE LIMITER CONFIGURATION:**

```yaml
# application.yml
spring:
  cloud:
    gateway:
      routes:
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - name: RequestRateLimiter
              args:
                # Tokens added per second
                redis-rate-limiter.replenishRate: 10
                # Max burst size
                redis-rate-limiter.burstCapacity: 20
                # Key resolver bean name
                redis-rate-limiter.requestedTokens: 1
                key-resolver: "#{@apiKeyResolver}"
```

```java
@Bean
KeyResolver apiKeyResolver() {
    // Extract client identifier from request header
    return exchange -> Mono.justOrEmpty(
        exchange.getRequest()
            .getHeaders()
            .getFirst("X-API-Key"));
    // Each API key gets its own token bucket
    // Key stored in Redis: request_rate_limiter.{key}.*
}
```

**RESILIENCE4J RATE LIMITER (service-to-service):**

```java
@Bean
public RateLimiterConfig rateLimiterConfig() {
    return RateLimiterConfig.custom()
        // Max concurrent calls in time window
        .limitForPeriod(50)
        // Time window length
        .limitRefreshPeriod(Duration.ofSeconds(1))
        // Max wait time before rejecting
        .timeoutDuration(Duration.ofMillis(100))
        .build();
}

@RateLimiter(name = "payment-service",
    fallbackMethod = "rateLimitFallback")
public OrderResponse createOrder(OrderRequest request) {
    return paymentClient.charge(request);
}

public OrderResponse rateLimitFallback(
    OrderRequest req, RequestNotPermitted ex) {
    // Return 429 with Retry-After header
    throw new TooManyRequestsException(
        "Rate limit exceeded. Retry in 1 second");
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**RATE LIMITING DECISION FLOW:**

```
Incoming Request: POST /api/payments
  (API Key: key-abc123)
  │
  ▼
API Gateway filter chain
  ├─ RequestRateLimiter filter:
  │     1. Extract API key: "key-abc123"
  │     2. Execute Redis Lua script:
  │          key = "rrl.key-abc123"
  │          tokens = GET(key.tokens) or burstCapacity
  │          now = current time
  │          elapsed = now - GET(key.timestamp)
  │          refill = elapsed * replenishRate
  │          tokens = min(tokens + refill, burst)
  │          if tokens >= 1:
  │            tokens -= 1
  │            SET(key.tokens, tokens)
  │            SET(key.timestamp, now)
  │            ALLOWED
  │          else:
  │            REJECTED
  │
  ├─ ALLOWED: pass to downstream service
  └─ REJECTED:
        HTTP 429 Too Many Requests
        Retry-After: 1 (seconds)
        X-RateLimit-Limit: 10
        X-RateLimit-Remaining: 0
        X-RateLimit-Reset: 1701234567
```

**TIERED RATE LIMITING (production pattern):**

```
Free tier:     10 req/min per API key
Basic tier:   100 req/min per API key
Premium tier: 1000 req/min per API key
Enterprise:   custom (negotiate)

Implementation:
  Key resolver returns: "{tier}:{api-key}"
  Route-level limits match tier:
    free config:    replenishRate=0.166 (10/60s)
    basic config:   replenishRate=1.666 (100/60s)
    premium config: replenishRate=16.66 (1000/60s)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: returning 500 on overload**

```java
// BAD: no rate limiting - overload causes 500/timeouts
@PostMapping("/payments")
public ResponseEntity<Payment> createPayment(
    @RequestBody PaymentRequest req) {
    // No rate limiting - any client can send unlimited
    // Buggy client sends 50,000 req/min
    // Thread pool exhausted -> 500 errors for everyone
    return ResponseEntity.ok(paymentService.process(req));
}
```

```java
// GOOD: rate limiting with proper 429 response
@PostMapping("/payments")
@RateLimiter(name = "payments",
    fallbackMethod = "paymentRateLimitFallback")
public ResponseEntity<Payment> createPayment(
    @RequestBody PaymentRequest req) {
    return ResponseEntity.ok(paymentService.process(req));
}

public ResponseEntity<Payment> paymentRateLimitFallback(
    PaymentRequest req, RequestNotPermitted ex) {
    return ResponseEntity
        .status(HttpStatus.TOO_MANY_REQUESTS)
        .header("Retry-After", "1")
        .header("X-RateLimit-Limit", "50")
        .body(null);
    // Client knows: wait 1s and retry
    // vs silently getting a 500 and not knowing why
}
```

**Example 2 - Failure: no Retry-After header causes
retry storms**

```
BAD RESPONSE:
  HTTP 429 Too Many Requests
  Body: {"error": "rate limit exceeded"}
  // No Retry-After header
  // Client retries immediately (100ms)
  // Creates exponential retry storm:
  //   T=0: 100 requests -> 80 rejected (429)
  //   T=100ms: 80 retries + 100 new = 180 req
  //   T=200ms: 180 rejected... spirals

GOOD RESPONSE:
  HTTP 429 Too Many Requests
  Retry-After: 1
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1701234568 (Unix epoch)
  Body: {
    "error": "rate_limit_exceeded",
    "message": "Retry after 1 second",
    "retryAfter": 1
  }
  // Client respects Retry-After and backs off
  // No retry storm
```

---

### ⚖️ Comparison Table

| Algorithm | Burst Handling | Memory | Accuracy | Best For |
|---|---|---|---|---|
| **Fixed Window** | Poor (boundary burst) | O(1) | Low | Simple internal limits |
| **Sliding Window Log** | Good | O(N) per client | High | Low-volume, high-accuracy |
| **Sliding Window Counter** | Good | O(1) | Medium | Production API rate limiting |
| **Token Bucket** | Excellent (configurable burst) | O(1) | High | Public APIs with burst allowance |
| **Leaky Bucket** | None (queue-based) | O(queue) | High | Traffic shaping, smooth output |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Rate limiting prevents DDoS attacks | Rate limiting prevents overload from legitimate clients and limits damage from application-layer floods. A volumetric DDoS (millions of packets/sec at L3/L4) requires CDN/WAF protection before the gateway. Rate limiting is an application-layer control. |
| Rate limiting by IP is sufficient | IP-based limiting is easily bypassed via IP rotation. Production APIs rate-limit by API key, user ID, or client certificate - authenticated identity, not IP. |
| Local rate limiter works for distributed services | If 3 gateway instances each allow 100 req/s, the effective limit is 300 req/s. Distributed rate limiting (shared Redis counter) is required for a true global limit. |

---

### 🚨 Failure Modes & Diagnosis

**Redis failure disables rate limiting**

**Symptom:**
Redis cluster goes down at 2pm. All rate limiting stops
(open) or all requests are rejected (closed), depending
on fail-open vs fail-closed configuration.

**Root Cause:**
Spring Cloud Gateway's `RedisRateLimiter` with no fallback
configuration defaults to... fail-open in some versions
(allows all traffic when Redis is unavailable). This means
a Redis outage = unlimited traffic = service overload.

**Diagnostic Command:**
```bash
# Check Redis connectivity from gateway pod
kubectl exec -it gateway-pod -- redis-cli -h redis ping

# Check rate limiter metrics
curl http://gateway:8080/actuator/metrics/ \
  http.server.requests | jq \
  '.measurements[] | select(.statistic=="COUNT")'

# Spring Boot rate limiter decision log
logging.level.org.springframework.cloud.gateway
  .filter.ratelimit=DEBUG
```

**Fix:**
Configure explicit fail-closed or local-fallback strategy:
```java
@Bean
public RateLimiter rateLimiter(
    RedisRateLimiter redisRL, LocalRateLimiter localRL) {
    return new FallbackRateLimiter(redisRL, localRL);
    // If Redis unavailable, fall back to local
    // Local limiter allows 50% of normal rate (conservative)
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `API Gateway` - the primary deployment point for
  external-facing rate limiting
- `Microservices Architecture` - the context requiring
  rate limiting as a protection mechanism

**Builds On This (learn these next):**
- `Retry Strategy` - clients need backoff strategy when
  receiving 429; without it, retries create storms
- `Circuit Breaker` - complements rate limiting:
  rate limiting = cap per client;
  circuit breaker = fail fast when downstream is sick

**Alternatives / Comparisons:**
- `Bulkhead Pattern` - limits concurrent requests (threads
  or connections) rather than rate over time
- `Resilience4j` - library implementing rate limiter,
  circuit breaker, bulkhead, and retry in one

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STATUS CODE  │ HTTP 429 Too Many Requests               │
│              │ Include Retry-After header (always)      │
├──────────────┼───────────────────────────────────────────┤
│ ALGORITHM    │ Token bucket for public APIs              │
│ CHOICE       │ (configurable burst + steady rate)       │
├──────────────┼───────────────────────────────────────────┤
│ KEY BY       │ API key or user ID (not IP alone)        │
├──────────────┼───────────────────────────────────────────┤
│ DISTRIBUTED  │ Redis Lua script for atomic counter       │
│              │ Spring Cloud Gateway: RedisRateLimiter   │
├──────────────┼───────────────────────────────────────────┤
│ FAILURE TRAP │ No Retry-After = retry storm             │
│              │ Redis down = fail-open (unlimited traffic)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reject excess requests BEFORE doing      │
│              │  any work - quota per client identity"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Retry Strategy → Circuit Breaker         │
│              │ → Bulkhead Pattern                        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always include `Retry-After` header in 429 responses.
   Without it, clients retry immediately and create
   a retry storm that amplifies the overload.
2. Token bucket is the preferred algorithm for public APIs:
   it allows legitimate burst (bucket) while enforcing
   a steady state rate (refill rate).
3. Distributed rate limiting requires an atomic counter
   (Redis Lua script). Multiple gateway instances
   with local counters produce N times the configured limit.

**Interview one-liner:**
"Rate limiting caps requests per client within a time
window, returning HTTP 429 with a Retry-After header for
excess requests. The token bucket algorithm is standard
for public APIs - allows burst up to bucket size, then
enforces the replenish rate. In distributed deployments,
the counter lives in Redis with a Lua script for atomic
read-modify-write. Without Retry-After, rejected clients
retry immediately and amplify the overload (retry storm)."

---

### 💡 The Surprising Truth

Fixed window rate limiting has a boundary burst vulnerability
that makes it unsuitable for protecting services at scale.
With a 100 req/minute fixed window limit: a client sends
100 requests at 00:59:50 (just before window end) and
100 more at 01:00:01 (just after window reset). The service
sees 200 requests in 11 seconds - 2x the stated limit -
because both windows reset independently. Sliding window
or token bucket algorithms eliminate this boundary burst
because the rate is computed over a rolling window, not
a discrete one. Fixed window is simple but the boundary
burst means the effective limit can be up to 2x the
configured value in a worst case.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** The boundary burst problem in fixed-window
   rate limiting and why token bucket or sliding window
   is preferred for public APIs.
2. **IMPLEMENT** Spring Cloud Gateway + Redis rate limiter
   with per-API-key limits, proper 429 response headers,
   and fail-closed behaviour when Redis is unavailable.
3. **DESIGN** Tiered rate limiting (free/basic/premium)
   where limits increase with subscription tier.
4. **DEBUG** A retry storm caused by missing Retry-After
   headers: identify from logs, add the header, verify
   storm dissipation.
5. **DECIDE** Choose between distributed rate limiting
   (Redis, exact) vs local rate limiting (no Redis dep,
   ~N-instance overshoot) based on the cost of overshoot
   vs operational complexity.

---

### 🧠 Think About This Before We Continue

**Q1.** Your SMS OTP API allows 5 OTPs per phone number
per hour. A token bucket with burst=5, refill=5/hour.
A user legitimately loses their OTPs due to network issues
and needs 6 within 2 minutes. How do you handle this
without making the rate limiting ineffective against abuse?
(Hint: consider separate admin endpoint, support bypass
tokens, audit log, or per-event retry window.)

**Q2.** You have 10 gateway instances. Each instance
has a local token bucket: 100 req/s. A single client
sends exactly 200 req/s distributed evenly across all
instances (20 req/s per instance). Is the client rate
limited? What is the actual effective limit with local
buckets? What are the exact trade-offs between local
buckets and distributed Redis counter for this scenario?

**Q3.** Design the rate limiting strategy for a fintech
open banking API that must comply with: (a) PSD2 regulation
- banks must not block legitimate calls, (b) partners
with SLA guarantees, (c) public developers on free tier,
(d) internal services that need unlimited access. What
are the keys, limits, algorithms, and bypass mechanisms
for each category?