---
layout: default
title: "Rate Limiting (Microservices)"
parent: "Microservices"
nav_order: 649
permalink: /microservices/rate-limiting-microservices/
number: "649"
category: Microservices
difficulty: ★★☆
depends_on: "API Gateway (Microservices), Resilience4j"
used_by: "Bulkhead Pattern, Timeout Strategy"
tags: #intermediate, #microservices, #reliability, #security, #distributed
---

# 649 — Rate Limiting (Microservices)

`#intermediate` `#microservices` `#reliability` `#security` `#distributed`

⚡ TL;DR — **Rate Limiting** controls how many requests a client or service can make in a given time window. Protects services from overload and abuse. Implementations: **Token Bucket**, **Leaky Bucket**, **Fixed Window**, **Sliding Window**. Applied at API Gateway (global), per-service (Resilience4j RateLimiter), or in a Service Mesh.

| #649            | Category: Microservices                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | API Gateway (Microservices), Resilience4j |                 |
| **Used by:**    | Bulkhead Pattern, Timeout Strategy        |                 |

---

### 📘 Textbook Definition

**Rate Limiting** is a mechanism that constrains the number of requests a client, user, or service can make within a defined time period. In microservices, rate limiting serves two purposes: **protection** — preventing individual clients or faulty services from overwhelming a downstream service with excessive requests; and **fairness** — ensuring equitable resource allocation among multiple concurrent clients. Rate limiting can be implemented at several layers: the **API Gateway** (global rate limiting per API key, IP, or user), individual **microservices** (Resilience4j RateLimiter, protecting a service from a specific caller), and the **Service Mesh** (Envoy global rate limit service). Common algorithms: **Token Bucket** — tokens refill at a fixed rate; each request consumes one token; allows bursting; **Leaky Bucket** — requests processed at a constant rate regardless of arrival rate; smooths traffic; **Fixed Window Counter** — count requests per fixed window (per minute); simple but has burst problem at window boundaries; **Sliding Window** — smooth rolling window; no boundary burst. When a rate limit is exceeded, the standard response is HTTP 429 Too Many Requests with a `Retry-After` header.

---

### 🟢 Simple Definition (Easy)

Rate Limiting is a "you can only call this service X times per second" rule. If a client or service exceeds the limit, requests are rejected with 429 (Too Many Requests). This protects services from being overwhelmed — whether by a misbehaving client, a retry storm, or a DDoS attack.

---

### 🔵 Simple Definition (Elaborated)

An API Gateway rate limits the `GET /api/products` endpoint to 1,000 requests per second per user. Under normal load, a user makes 10 requests/second — well within limit. During a misconfigured client retry loop: the client sends 5,000 requests/second. The first 1,000 pass through; the remaining 4,000 receive 429 Too Many Requests immediately. `ProductService` sees at most 1,000 req/s regardless of how broken the client is. Without rate limiting: 5,000 req/s overwhelms `ProductService`, slowing it for all other users.

---

### 🔩 First Principles Explanation

**Rate limiting algorithms — compared:**

```
1. TOKEN BUCKET:
   Bucket holds max N tokens.
   Tokens refill at rate R per second.
   Each request consumes 1 token.
   If no tokens: reject request.

   Example: capacity=100, refillRate=10/sec
   Steady state: 10 req/s always allowed
   Burst: up to 100 req in 1 second (if bucket was full)
   → Good for: APIs that need to allow short bursts (legitimate usage)
   → AWS API Gateway, Kong, Resilience4j use Token Bucket

   timeline:
   T=0:  100 tokens. Client sends 100 req. 100 pass. Bucket empty.
   T=0.1 0 tokens. Client sends 10 req. 10 REJECTED (429).
   T=1:  10 tokens refilled. Next 10 requests pass.

2. LEAKY BUCKET:
   Requests enter queue at any rate.
   Queue processed at fixed rate R (constant outflow).
   If queue full: new requests dropped.
   → Traffic is smoothed to constant R req/s
   → Good for: smoothing burst traffic before sending to backend

3. FIXED WINDOW:
   Count requests in fixed time window (e.g., 12:00:00 – 12:00:59).
   If count > limit: reject.
   Reset count at 12:01:00.
   PROBLEM: burst at window boundary
   → 100 req limit: client sends 100 at 12:00:59 + 100 at 12:01:00 = 200 in 2 seconds
   → Simple to implement but vulnerable to window boundary exploitation

4. SLIDING WINDOW LOG:
   Track timestamps of recent requests.
   For each new request: count requests within last N seconds.
   If count > limit: reject.
   → Most accurate but memory-intensive (store N timestamps per client)

5. SLIDING WINDOW COUNTER (approximate):
   Blend previous window count + current window count weighted by elapsed time.
   → Memory-efficient approximation of sliding window log
   → Redis-based rate limiters typically use this
   → Formula: approxCount = prevCount × (1 - elapsed/windowSize) + currentCount
```

**WHERE to apply rate limiting in the stack:**

```
LAYER 1: API Gateway (client → gateway)
  Rate limit by: IP, API Key, User ID, OAuth client_id
  Protects: all downstream microservices from external abuse
  Tools: Spring Cloud Gateway (Redis-backed), Kong, AWS API Gateway
  Response: 429 Too Many Requests + Retry-After header

LAYER 2: Microservice-to-Microservice (Resilience4j)
  Rate limit by: which upstream service is calling
  Protects: payment-service from being called too fast by order-service
  Tools: Resilience4j RateLimiter
  Response: RequestNotPermitted exception → fallback logic

LAYER 3: Service Mesh (Envoy global rate limit service)
  Centralised rate limiting across all service mesh nodes
  Consistent limits even when multiple instances of caller exist
  Tools: Envoy + Lyft's rate limit service, Redis backend
  Response: 429 via Envoy → caller service

CHOOSE BY SCOPE:
  External client abuse → API Gateway
  Internal service quota → Resilience4j per-service
  Cross-service policy → Service Mesh global rate limit
```

**Distributed rate limiting — Redis-backed shared counters:**

```
PROBLEM: Single microservice may have 10 instances.
  Each instance has its own Resilience4j RateLimiter (100 req/s).
  10 instances × 100 = 1,000 req/s allowed total — but you wanted 100 total.

SOLUTION: Redis atomic counter:
  Each request: INCR counter:service:window → get count
  If count > limit: reject
  Expire counter at end of window: EXPIRE key windowDuration

  # Lua script (atomic increment + compare + expire):
  local count = redis.call('INCR', KEYS[1])
  if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
  end
  if count > tonumber(ARGV[2]) then
    return 0  -- rate limited
  end
  return 1    -- allowed

  Spring Cloud Gateway uses Redis for distributed rate limiting:
    spring.cloud.gateway.routes[0].filters:
      - name: RequestRateLimiter
        args:
          redis-rate-limiter.replenishRate: 100   # tokens per second
          redis-rate-limiter.burstCapacity: 200   # max burst
          key-resolver: "#{@userKeyResolver}"     # rate limit per user
```

---

### ❓ Why Does This Exist (Why Before What)

Any publicly reachable API endpoint is a potential abuse target. Microservices within a system can also generate unintended overload (misconfigured retry loops, buggy clients). Without rate limiting: a single runaway process or malicious client can consume all resources of a downstream service, degrading performance for all other clients. Rate limiting is the circuit breaker at the input — it caps demand before it reaches the processing layer.

---

### 🧠 Mental Model / Analogy

> Rate Limiting is like a highway on-ramp meter. During rush hour, a traffic light on the on-ramp allows only one car every 3 seconds (rate = 20 cars/minute). Regardless of how many cars are waiting, they enter the highway at a controlled rate — protecting the highway from gridlock (service overload). Cars that can't get on quickly enough wait or take another route (429 with Retry-After). Without the meter: all cars enter at once → gridlock → everyone stuck → highway (service) completely unresponsive.

---

### ⚙️ How It Works (Mechanism)

**Resilience4j RateLimiter with Spring:**

```java
@Service
class ExternalPaymentClient {

    @RateLimiter(name = "payment-gateway", fallbackMethod = "rateLimitFallback")
    public PaymentResponse processPayment(PaymentRequest request) {
        return externalGatewayClient.post(request);
    }

    public PaymentResponse rateLimitFallback(PaymentRequest request,
                                              RequestNotPermitted ex) {
        // Queue the payment for retry in 1 second:
        retryQueue.schedule(() -> processPayment(request), 1, TimeUnit.SECONDS);
        return PaymentResponse.queued(request.getOrderId());
    }
}

// application.yml:
// resilience4j.ratelimiter.instances.payment-gateway:
//   limitForPeriod: 50         # 50 calls per period
//   limitRefreshPeriod: 1s     # period duration
//   timeoutDuration: 500ms     # wait up to 500ms for a permit (0 = reject immediately)
```

---

### 🔄 How It Connects (Mini-Map)

```
External Clients / Internal Services
        │
        ▼
Rate Limiting (Microservices)  ◄──── (you are here)
        │
        ├── API Gateway → primary enforcement point for external rate limits
        ├── Resilience4j → per-service rate limiting in Java services
        ├── Service Mesh (Envoy) → global distributed rate limiting
        └── Token Bucket / Leaky Bucket → algorithms implementing rate limiting
```

---

### 💻 Code Example

**Spring Cloud Gateway — per-user rate limiting with Redis:**

```java
@Configuration
class RateLimiterConfig {

    // Rate limit key: extract user ID from JWT header (set by JWT filter):
    @Bean
    KeyResolver userKeyResolver() {
        return exchange -> Mono.justOrEmpty(
            exchange.getRequest().getHeaders().getFirst("X-User-Id")
        ).defaultIfEmpty("anonymous");
    }
}

// application.yml:
// spring.cloud.gateway.routes:
//   - id: products
//     uri: lb://product-service
//     predicates:
//       - Path=/api/products/**
//     filters:
//       - name: RequestRateLimiter
//         args:
//           redis-rate-limiter.replenishRate: 100    # 100 tokens/sec refill
//           redis-rate-limiter.burstCapacity: 200    # max burst
//           redis-rate-limiter.requestedTokens: 1   # cost per request
//           key-resolver: "#{@userKeyResolver}"     # per-user limits
//
// Response when rate limited:
//   HTTP 429 Too Many Requests
//   X-RateLimit-Remaining: 0
//   X-RateLimit-Replenish-Rate: 100
//   X-RateLimit-Burst-Capacity: 200
```

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rate limiting only protects against DDoS attacks | Rate limiting also protects against unintentional overload: misconfigured retry loops, bulky batch jobs, clients with exponential retry without backoff. Most rate limit violations in production are unintentional         |
| HTTP 429 means the service is down               | HTTP 429 means the client is sending too many requests. The service itself is healthy. Clients should implement exponential backoff with jitter on 429 responses — not alarm-level failures                                 |
| Rate limiting at the API Gateway is sufficient   | If services are accessible within the cluster (service-to-service), API Gateway rate limits only protect from external callers. Internal service-to-service limits require Resilience4j or a Service Mesh rate limit policy |

---

### 🔥 Pitfalls in Production

**Retry storm after rate limiting — making it worse**

```
SCENARIO:
  10 clients each make 200 req/s to ProductService (total: 2,000 req/s).
  Rate limit: 1,000 req/s total. Every second: 1,000 requests rejected (429).
  Clients have retry logic: on 429, retry in 1 second (no jitter).

  Next second: same 10 clients retry ALL rejected requests simultaneously.
  → 2,000 req/s again → 1,000 more rejections → retry again → ...

  RETRY STORM: rate limiting triggers synchronised retries → sustained overload

FIX: Exponential backoff with JITTER on 429:
  // Bad (synchronised retries):
  if (response.code == 429) {
    Thread.sleep(1000);  // all clients sleep same duration → retry together
    retry();
  }

  // Good (jittered backoff):
  if (response.code == 429) {
    String retryAfter = response.headers["Retry-After"];  // use server hint
    long waitMs = retryAfter != null
        ? Long.parseLong(retryAfter) * 1000
        : (long)(Math.random() * 2000) + 500;  // random 500–2500ms
    Thread.sleep(waitMs);
    retry();
  }
  // Random jitter desynchronises retries → load spreads across time
```

---

### 🔗 Related Keywords

- `API Gateway (Microservices)` — primary enforcement point for external-facing rate limits
- `Token Bucket` — common algorithm for rate limiting (allows controlled bursting)
- `Leaky Bucket` — smooths traffic to constant rate
- `Resilience4j` — provides `@RateLimiter` for Java microservice rate limiting

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PROTECTS     │ Service from overload and abuse           │
│ RESPONSE     │ HTTP 429 + Retry-After header             │
├──────────────┼───────────────────────────────────────────┤
│ TOKEN BUCKET │ Burst-friendly, refill at fixed rate      │
│ LEAKY BUCKET │ Smooth constant output rate               │
│ SLIDING WIN  │ Accurate, memory-intensive                │
├──────────────┼───────────────────────────────────────────┤
│ WHERE        │ API Gateway (external), Resilience4j      │
│              │ (internal), Service Mesh (global)         │
├──────────────┼───────────────────────────────────────────┤
│ DISTRIBUTED  │ Redis-backed counters (shared across      │
│ RATE LIMIT   │ multiple service instances)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A rate limiter at the API Gateway limits each user to 100 requests/minute. A user has a mobile app and a desktop browser open simultaneously — each generating 60 requests/minute. Total: 120 requests/minute → rate limited. Is this the correct behaviour? How would you design the rate limit key to handle multiple devices per user without unfairly blocking legitimate usage? What are the challenges of rate limiting by user identity when the user is anonymous (not logged in)?

**Q2.** A Token Bucket rate limiter allows a burst of 1,000 requests (full bucket) followed by a steady rate of 100 requests/second. A web scraper discovers this and sends 1,000 requests immediately on each new minute (full bucket reset). They are never rate limited during their bursting window. How would you detect and prevent this burst abuse pattern while still allowing legitimate users who need occasional short bursts (e.g., a mobile app doing initial data sync)? Consider sliding window counter vs token bucket trade-offs.
