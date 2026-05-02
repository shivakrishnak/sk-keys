---
layout: default
title: "API Throttling"
parent: "HTTP & APIs"
nav_order: 254
permalink: /http-apis/api-throttling/
number: "0254"
category: HTTP & APIs
difficulty: ★★☆
depends_on: API Rate Limiting, REST, HTTP
used_by: REST APIs, API Gateways, Microservices Protection
related: API Rate Limiting, API Gateway, Circuit Breaker, Bulkhead
tags:
  - throttling
  - rate-limiting
  - backpressure
  - api-protection
  - intermediate
---

# 254 — API Throttling

⚡ TL;DR — API throttling deliberately slows down or blocks requests that exceed a defined rate to protect the backend from overload; while **rate limiting** is binary (allow/deny per time window), **throttling** is a broader term that includes queuing, gradual slow-down, and request shaping — ensuring the API degrades gracefully under high load rather than crashing.

| #254 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | API Rate Limiting, REST, HTTP | |
| **Used by:** | REST APIs, API Gateways, Microservices Protection | |
| **Related:** | API Rate Limiting, API Gateway, Circuit Breaker, Bulkhead | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A partner company integrates with your notification API. A bug in their code creates
an infinite retry loop — 50,000 requests per second hit your notification service.
Without throttling: the notification service's database connection pool is exhausted.
Other customers' notification requests queue up and time out. The service crushes under
load and becomes unavailable for all customers. The misbehaving partner effectively
performs an accidental DoS attack on your multi-tenant platform.

**THE INVENTION MOMENT:**
Throttling predates the modern API era — network routers use traffic shaping and
policing (leaky bucket / token bucket) to ensure fair bandwidth usage. Applied to APIs:
cloud platforms (AWS, Azure, GCP) expose throttling at the API Gateway layer to protect
backends from both malicious and accidental overuse. The key insight: it is better to
make some requests slower (throttle) than to make all requests fail (crash).

---

### 📘 Textbook Definition

**API Throttling** is the process of controlling the rate at which requests are
processed by an API, to ensure fair resource distribution, protect backend systems
from overload, and enable graceful degradation under peak traffic. Throttling includes:
(1) **Hard rate limiting** — reject excess requests immediately with `429 Too Many Requests`.
(2) **Soft throttling / queueing** — accept requests but delay processing (queue) when
throughput exceeds capacity. (3) **Traffic shaping** — smooth burst traffic into a
steady rate (leaky bucket). (4) **Adaptive throttling** — dynamically adjust limits
based on current system load (CPU, memory, queue depth). HTTP responses signal throttling
via: `429 Too Many Requests`, `Retry-After` header (when client can retry), and rate
limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Throttling is the speed governor for your API — it doesn't let requests go too fast
for the backend to handle, protecting shared resources under burst traffic.

**One analogy:**
> Throttling is like a smart highway on-ramp metering light.
> Individual drivers (API consumers) want to merge onto the highway (backend)
> as fast as possible. Without metering: nobody can merge — gridlock.
> The metering light (throttle) governs entry rate to match what the highway
> can absorb — some drivers wait 30 seconds (queued) or are redirected (429).
> The highway keeps flowing safely for everyone already on it.

**One insight:**
The most important difference between rate limiting and throttling: rate limiting is binary
(allowed/denied); throttling is continuous (allowed/slower/queued/denied). A well-designed
throttling strategy prefers queuing over immediate rejection for bursty but not abusive
clients — making the API feel more reliable without overloading the backend.

---

### 🔩 First Principles Explanation

**THROTTLING vs RATE LIMITING:**

```
RATE LIMITING (binary, count-based):
  "You get 1000 requests per hour. After that: 429."
  Enforcement: per time window, count-based
  Response on excess: immediate 429
  Use case: API monetization, preventing quota abuse

THROTTLING (continuous, rate-based):
  "Requests flow through at max N/second. Excess: queued or delayed."
  Enforcement: per second / per millisecond, flow rate
  Response on excess: queue (delay) or reject
  Use case: backend protection, fair resource sharing, burst handling

TECHNIQUES:
  Token Bucket:     Refill N tokens/second. Each request costs 1 token.
                    Burst allowed (up to bucket size).
                    ✅ Handles bursts
                    Use: API gateways (AWS API Gateway, Kong)

  Leaky Bucket:     Requests fill a queue (bucket). Queue drains at fixed rate.
                    Smooths bursts → steady output rate.
                    ✅ No bursts in output (smooth traffic shaping)
                    Use: network QoS, audio/video streaming

  Sliding Window:   Count requests in rolling window.
                    More precise than fixed window (no boundary burst exploit).
                    Use: API rate limiting with fairness requirements

  Concurrency Limit (Bulkhead):
                    "Max N requests active simultaneously."
                    Excess: immediately rejected or queued.
                    Use: downstream service protection, DB connection pools
```

**HTTP THROTTLING RESPONSE HEADERS:**

```
429 Too Many Requests response:
  HTTP/1.1 429 Too Many Requests
  Content-Type: application/json
  X-RateLimit-Limit: 1000          ← total allowed per window
  X-RateLimit-Remaining: 0         ← 0 = exhausted
  X-RateLimit-Reset: 1705004460    ← Unix timestamp when window resets
  Retry-After: 30                  ← seconds until client can retry
  
  Body: {
    "error": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Retry after 30 seconds.",
    "retryAfter": 30
  }

INFORMATIONAL HEADERS (on 200 responses too):
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 847
  X-RateLimit-Reset: 1705004460
  → Clients can see themselves approaching the limit and back off proactively
```

---

### 🧪 Thought Experiment

**SCENARIO:** Notification API used by 100 tenants in multi-tenant SaaS.

```
WITHOUT THROTTLING:
  Tenant A (bug): 10,000 requests/sec (infinite retry loop)
  Tenants B-Z: 1 request/sec each
  
  DB connection pool: 100 connections
  Tenant A: consumes all 100 connections
  Tenants B-Z: timeout, 0 connections available
  → All customers affected by one tenant's bug

WITH PER-TENANT THROTTLING:
  Policy: each tenant gets max 50 requests/second rate limit
  Tenant A (bug): hits 50/s limit instantly
  → Requests 51+ get 429 (or queued at gateway)
  → Tenant A's bug self-limits at 50/s, then they auto-retry, still limited
  → DB connections: 50/tenant × active tenants = at most 5000 queued
  → Other tenants: unaffected, still getting their 50/s allowed

GLOBAL CONCURRENCY LIMIT (backup protection):
  Max 200 concurrent requests globally
  Tenant A at 50/s → contributing ~10 concurrent (avg 200ms response)
  50 active tenants at 1/s → contributing ~10 concurrent total
  Total ~20 concurrent — well within 200 limit
  → Even without per-tenant limits: global concurrency prevents DB exhaustion
```

---

### 🧠 Mental Model / Analogy

> Throttling is like a coffee shop with a fixed number of baristas.
> 100 customers arrive at once (traffic burst). The shop can serve 10 customers per minute.
> Option A (no throttling): all 100 try to order simultaneously — chaos, nothing done.
> Option B (hard rate limit): 10 served, 90 turned away at the door.
> Option C (throttling + queue): first 10 served immediately, next 90 queued — served in order.
> Throttling is Option C: nobody gets turned away if they're willing to wait a reasonable time.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is:**
Throttling is a speed limit for API requests. If a client sends requests too fast,
some are slowed down or told "wait 30 seconds and try again." This stops one client
from overwhelming the server and breaking things for everyone else.

**Level 2 — How to use it:**
Spring Boot: Resilience4j `@RateLimiter` annotation limits invocations per time period.
At API Gateway level: configure rate limit policies per API key, per IP, or per tenant.
Always return `429 Too Many Requests` with `Retry-After` header when limiting.
Expose `X-RateLimit-*` headers on every response so clients know their remaining budget.

**Level 3 — How it works:**
Resilience4j RateLimiter uses a time-division algorithm: `limitForPeriod` events allowed
per `limitRefreshPeriod`. Excess calls either block (up to `timeoutDuration`) or throw
`RequestNotPermitted` immediately. For distributed systems: no per-instance limits
(clients load-balanced across instances would see inconsistent limits) — use Redis-based
distributed rate limiting. Redis + Lua script atomically checks + decrements a counter.
Sliding window via Redis sorted sets: add current request timestamp; remove timestamps
outside window; count remaining. Atomic Lua script ensures consistent count across
concurrent requests.

**Level 4 — Why it was designed this way:**
Throttling is a mechanism for enforcing backpressure at the network boundary. The
fundamental design challenge: where to throttle determines the protection surface.
Per-IP throttling: catches individual clients but misses distributed attack sources.
Per-API-key: better for multi-tenant fairness but requires API key auth. Per-tenant:
optimal for SaaS platforms. The distributed rate limiting challenge (consistency across
instances) is a fundamental trade-off: Redis-based centralized counting is accurate but
adds latency; local counting is fast but allows some burst overage during counter sync.
AWS and Google recommend a small (5-10%) over-allowance tolerance for globally distributed
rate limiting given replication lag. The `Retry-After` header is critical: without it,
clients implement exponential backoff with arbitrary delays, causing thundering herd
when the limit resets — synchronized `Retry-After` staggers retries.

---

### ⚙️ How It Works (Mechanism)

```
REDIS-BASED DISTRIBUTED RATE LIMITING:

-- Lua script for atomic sliding window rate limiting:
local key = KEYS[1]           -- "rate_limit:tenant_A:notifications"
local limit = tonumber(ARGV[1]) -- 50 (max per window)
local window = tonumber(ARGV[2]) -- 1000 (window size in ms)
local now = tonumber(ARGV[3])   -- current time in ms

-- Remove expired entries
redis.call("ZREMRANGEBYSCORE", key, 0, now - window)
-- Count current window size
local count = redis.call("ZCARD", key)

if count < limit then
    -- Add current request
    redis.call("ZADD", key, now, now .. math.random())
    redis.call("PEXPIRE", key, window)
    return 1  -- allowed
else
    return 0  -- rate limited
end

JAVA INTEGRATION:
  boolean allowed = redisRateLimiter.isAllowed(tenantId, 50, 1000);
  if (!allowed) {
      throw new RateLimitExceededException("Rate limit exceeded");
      // → 429 response with Retry-After header
  }
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
MULTI-LAYER THROTTLING ARCHITECTURE:

  [Client] → [CDN/WAF] → [API Gateway] → [BFF/Service] → [DB]
               │               │               │
           IP-level         API key level   Service level
           DDoS throttle     per-tenant      Resilience4j
           (coarse)          rate limit      concurrency limit
           (blocks floods)   (per second)    (protects DB pool)

  Each layer catches a different threat:
  CDN: volumetric DDoS, bot traffic
  API Gateway: per-key/per-tenant fairness quotas
  Service: concurrency limit protects DB connections
```

---

### 💻 Code Example

```java
// Resilience4j rate limiter on Spring Boot service method
@Service
public class NotificationService {

    @RateLimiter(name = "notificationRateLimiter",
                 fallbackMethod = "sendNotificationFallback")
    public NotificationResult sendNotification(String tenantId, Notification notification) {
        return notificationRepository.save(notification);
    }

    public NotificationResult sendNotificationFallback(String tenantId,
            Notification notification, RequestNotPermitted ex) {
        log.warn("Rate limit exceeded for tenant: {}", tenantId);
        throw new RateLimitExceededException(
            "Too many requests for tenant: " + tenantId, 30);
    }
}

// application.yml Resilience4j config
// resilience4j:
//   ratelimiter:
//     instances:
//       notificationRateLimiter:
//         limitForPeriod: 50        # 50 requests allowed
//         limitRefreshPeriod: 1s    # per 1 second
//         timeoutDuration: 0        # don't wait — fail fast

// Controller: return 429 with Retry-After header
@ExceptionHandler(RateLimitExceededException.class)
public ResponseEntity<ErrorResponse> handleRateLimit(RateLimitExceededException ex) {
    return ResponseEntity
        .status(HttpStatus.TOO_MANY_REQUESTS)
        .header("Retry-After", String.valueOf(ex.getRetryAfterSeconds()))
        .header("X-RateLimit-Reset",
            String.valueOf(Instant.now().plusSeconds(ex.getRetryAfterSeconds()).getEpochSecond()))
        .body(new ErrorResponse("RATE_LIMIT_EXCEEDED", ex.getMessage()));
}
```

---

### ⚖️ Comparison Table

| Mechanism | Behavior on Excess | Best For | Latency Added |
|---|---|---|---|
| **Hard rate limit (429)** | Immediate rejection | API quotas, billing tiers | None |
| **Soft throttle (queue)** | Delay + eventually serve | Bursty but valid traffic | Up to queue timeout |
| **Token bucket** | Allows bursts, rejects when empty | General API protection | None |
| **Leaky bucket** | Smooths bursts to steady rate | Traffic shaping, smooth output | Burst delay |
| **Concurrency limit** | Rejects when max concurrent reached | DB pool protection | None |
| **Adaptive throttle** | Dynamic limit based on system load | Auto-scaling APIs | Variable |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Throttling and rate limiting are synonyms | Rate limiting: binary allow/deny per quota. Throttling: broader — includes queueing, shaping, adaptive control. Rate limiting IS one form of throttling |
| Throttling is only for public APIs | Internal microservices throttle each other to prevent cascade failure under load. A downstream DB being slow should trigger upstream throttling |
| Retry-After header is optional | Optional per spec, but CRITICAL for preventing thundering herd where all 429 clients retry at the same moment (same window reset time) |

---

### 🚨 Failure Modes & Diagnosis

**Thundering Herd After Rate Limit Window Reset**

**Symptom:**
Thousands of 429 clients all retry at exactly the same second when the rate limit
window resets → creates another spike → another round of 429s → oscillating overload.

**Root Cause:**
All clients received the same `X-RateLimit-Reset` timestamp → all retry simultaneously.

**Fix:**
```java
// Add jitter to Retry-After header:
int baseDelay = 30;  // seconds
int jitter = ThreadLocalRandom.current().nextInt(0, 15); // 0-15s random jitter
response.setHeader("Retry-After", String.valueOf(baseDelay + jitter));
// Spreads retries over a 15-second window → no thundering herd
```

---

### 🔗 Related Keywords

- `API Rate Limiting` — specific form of throttling: per-window request quotas
- `Circuit Breaker` — related pattern: stops calls entirely when downstream is unhealthy
- `Bulkhead` — concurrency-based isolation; limits concurrent requests per service
- `Backpressure` — upstream signaling that downstream cannot accept more requests

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Speed governor for API requests;          │
│              │ prevents backend overload                 │
├──────────────┼───────────────────────────────────────────┤
│ HTTP STATUS  │ 429 Too Many Requests                     │
│ HEADERS      │ Retry-After: 30                           │
│              │ X-RateLimit-Remaining: 0                  │
├──────────────┼───────────────────────────────────────────┤
│ RESILIENCE4J │ @RateLimiter: N requests per period       │
│              │ fallbackMethod for graceful handling      │
├──────────────┼───────────────────────────────────────────┤
│ DISTRIBUTED  │ Redis Lua script: atomic sliding window   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Speed limit; some wait, none crash"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Rate Limiting → Circuit Breaker       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You're designing a multi-tenant SaaS API. Tenant A is on a "Professional" plan (10,000 req/min),
Tenant B is on "Enterprise" (100,000 req/min), and Tenant C is on "Free" (100 req/min).
Your notification service has a hard physical limit of 50,000 req/min total from the DB pool.
On a typical day, peak combined demand from all tenants is 80,000 req/min. Design a throttling
architecture that honors plan limits, prevents overload, and prioritizes paid tiers when
total demand exceeds capacity. What mechanisms (burst credit, priority queues, adaptive limits)
address the "Enterprise at 100K but physical max is 50K" scenario?
