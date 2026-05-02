---
layout: default
title: "Throttling Pattern"
parent: "Design Patterns"
nav_order: 813
permalink: /design-patterns/throttling-pattern/
number: "813"
category: Design Patterns
difficulty: ★★★
depends_on: "Retry Pattern, Bulkhead Pattern, API Gateway, Rate Limiting"
used_by: "API gateway, rate limiting, resource protection, SLA enforcement"
tags: #advanced, #design-patterns, #rate-limiting, #api-gateway, #resilience, #microservices
---

# 813 — Throttling Pattern

`#advanced` `#design-patterns` `#rate-limiting` `#api-gateway` `#resilience` `#microservices`

⚡ TL;DR — **Throttling Pattern** limits the rate or concurrency of requests a service accepts, protecting resources from overload and enforcing SLAs — returning 429 (Too Many Requests) when the limit is exceeded, enabling graceful degradation under load.

| #813 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Retry Pattern, Bulkhead Pattern, API Gateway, Rate Limiting | |
| **Used by:** | API gateway, rate limiting, resource protection, SLA enforcement | |

---

### 📘 Textbook Definition

**Throttling Pattern** (Microsoft Cloud Design Patterns; also "Rate Limiting" in API design): a resilience and resource management pattern that controls the rate or concurrency of requests accepted by a service, by rejecting or delaying requests that exceed a defined threshold. Returns HTTP 429 (Too Many Requests) with `Retry-After` header when the threshold is exceeded. Three primary algorithms: Token Bucket (allows bursting up to a limit), Leaky Bucket (enforces strict rate), Sliding Window (counts requests in a rolling time window). Used for: per-user/per-API-key rate limiting; protecting expensive operations (ML inference, report generation); enforcing SLA tiers; preventing abuse/DDoS amplification.

---

### 🟢 Simple Definition (Easy)

A popular API without rate limiting: one bad actor sends 100,000 requests/minute. Your database collapses. All users see 500 errors. With throttling: that actor gets 429 (Too Many Requests) after 1,000 requests/minute. Their 100,000 requests are rejected at the rate limiter. Your database: handles the normal 1,000 legitimate requests/minute. Throttling: the bouncer that says "you've had enough — wait outside."

---

### 🔵 Simple Definition (Elaborated)

A financial data API with two customer tiers: Basic (100 req/min) and Premium (1,000 req/min). Without throttling: a Basic customer's script runs amok, makes 50,000 req/min, consumes all database connections, Premium customers get 503 errors. With throttling: Basic customer is limited to 100/min (429 after that). Premium customers: unaffected at 1,000/min. A single report endpoint that takes 30 seconds: limited to 5 concurrent requests (concurrency throttling) regardless of user tier. Throttling = rate enforcement + resource protection + tier differentiation.

---

### 🔩 First Principles Explanation

**Throttling algorithms and Spring Boot implementation:**

```
THROTTLING ALGORITHMS:

  1. TOKEN BUCKET (most common for API rate limiting):
  
  Concept: A bucket that fills with tokens at a fixed rate (e.g., 100 tokens/minute).
  Each request: consumes 1 token. If no token available: reject (429).
  Allows bursting: if bucket isn't fully consumed, unused tokens accumulate up to bucket size.
  
  Example: 100 tokens/min, bucket size 200.
  Typical traffic: 80 req/min → tokens accumulate.
  Burst: 150 requests in 10 seconds → consumed from bucket (burst allowed).
  Sustained 150 req/min: tokens drain → 429 after bucket empty.
  
  Implementation: Redis INCR + EXPIRE (simple); Resilience4j RateLimiter; Bucket4j (Java).
  
  2. LEAKY BUCKET (strict rate, no bursting):
  
  Concept: Requests enter a queue (bucket). The bucket "leaks" at a fixed rate.
  If bucket full: request dropped (429).
  Guarantees: steady outflow regardless of input rate (smoothing).
  
  Use case: Payment processing — strict 100 payments/sec regardless of burst.
  Not suitable when bursting is acceptable or desirable.
  
  3. SLIDING WINDOW LOG (precise but memory-intensive):
  
  Concept: Log timestamp of each request. Count requests in last N seconds.
  If count > limit: reject.
  
  Precision: exact rate limiting. No burst within window.
  Cost: stores every request timestamp (memory: O(requests-per-window)).
  
  4. SLIDING WINDOW COUNTER (approximation, memory-efficient):
  
  Concept: Two fixed windows (current + previous). Weight current and previous window.
  Approximation: smooth out the fixed window edge problem.
  Used by: Cloudflare, many API gateways.
  Cost: O(1) memory per user.

THROTTLING DIMENSIONS:

  By user/API key:       100 req/min per API key (most common)
  By IP address:         1000 req/min per IP (abuse prevention)
  By endpoint:           /reports: 5 concurrent; /search: 100 req/min
  By tier/plan:          Basic: 100 req/min; Premium: 1000 req/min
  By resource:           CPU-intensive: 10 concurrent; lightweight: 100 req/min
  By time-of-day:        Off-peak: higher limits; peak hours: stricter limits

RESILIENCE4J RATE LIMITER (application-level throttling):

  resilience4j:
    ratelimiter:
      instances:
        reportGeneration:
          limitForPeriod: 5           # 5 requests per period
          limitRefreshPeriod: 1s      # period = 1 second
          timeoutDuration: 0ms        # fail immediately if rate limit exceeded

SPRING BOOT WITH BUCKET4J + REDIS (per-user API rate limiting):

  @Component @RequiredArgsConstructor
  class RateLimitingFilter extends OncePerRequestFilter {
  
      private final RateLimiterService rateLimiter;
      
      @Override
      protected void doFilterInternal(HttpServletRequest req,
              HttpServletResponse resp, FilterChain chain)
              throws ServletException, IOException {
              
          String apiKey = req.getHeader("X-API-Key");
          RateLimitResult result = rateLimiter.checkLimit(apiKey, "default");
          
          resp.setHeader("X-RateLimit-Limit", String.valueOf(result.getLimit()));
          resp.setHeader("X-RateLimit-Remaining", String.valueOf(result.getRemaining()));
          resp.setHeader("X-RateLimit-Reset", String.valueOf(result.getResetAt().getEpochSecond()));
          
          if (!result.isAllowed()) {
              resp.setStatus(429);
              resp.setHeader("Retry-After", String.valueOf(result.getRetryAfterSeconds()));
              resp.setContentType(MediaType.APPLICATION_JSON_VALUE);
              resp.getWriter().write("{\"error\":\"Too Many Requests\",\"retryAfter\":" 
                                    + result.getRetryAfterSeconds() + "}");
              return;
          }
          
          chain.doFilter(req, resp);
      }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Throttling:
- No upper bound on request rate: malicious or buggy clients can exhaust all resources
- Shared resource exhaustion: one heavy client degrades all others

WITH Throttling:
→ Resource consumption bounded per client. SLA tiers enforced. System stable under overload. Clients get clear 429 + Retry-After to handle gracefully.

---

### 🧠 Mental Model / Analogy

> A highway with an on-ramp metering light: during peak traffic, the light controls one car per green signal onto the highway. Cars arrive faster than the light allows: they queue on the ramp. If the queue fills: cars are turned away (to alternate routes). The highway never gets more traffic than it can handle. Off-peak: the ramp light is green continuously — no restriction. Throttling = ramp metering: control the input rate to match the system's processing capacity.

"Ramp metering light" = rate limiter (token bucket, leaky bucket)
"One car per green signal" = N requests per time window
"Cars queue on the ramp" = request queue (when using queuing throttle, not reject)
"Cars turned away" = 429 Too Many Requests
"Highway never overloaded" = downstream service never overloaded
"Off-peak: continuous green" = low-traffic periods: limits not hit, no restriction

---

### ⚙️ How It Works (Mechanism)

```
TOKEN BUCKET IN REDIS (atomic implementation):

  KEYS[1] = "rate_limit:{apiKey}"
  ARGV[1] = max_tokens (e.g., 100)
  ARGV[2] = refill_rate (tokens per second, e.g., 1.67 = 100/min)
  ARGV[3] = current_time (Unix timestamp)
  
  Lua script (atomic GET + conditional DECR):
  
  local key = KEYS[1]
  local max_tokens = tonumber(ARGV[1])
  local refill_rate = tonumber(ARGV[2])
  local now = tonumber(ARGV[3])
  
  local data = redis.call("HMGET", key, "tokens", "last_refill")
  local tokens = tonumber(data[1]) or max_tokens
  local last_refill = tonumber(data[2]) or now
  
  -- Refill based on elapsed time:
  local elapsed = now - last_refill
  tokens = math.min(max_tokens, tokens + elapsed * refill_rate)
  
  if tokens >= 1 then
      tokens = tokens - 1
      redis.call("HMSET", key, "tokens", tokens, "last_refill", now)
      redis.call("EXPIRE", key, 3600)
      return {1, math.floor(tokens)}    -- allowed, remaining tokens
  else
      return {0, 0}                     -- rejected
  end
  
  Lua script is atomic in Redis: no race conditions between check and decrement.
```

---

### 🔄 How It Connects (Mini-Map)

```
Unbounded request rates → resource exhaustion → cascading failure / SLA breach
        │
        ▼
Throttling Pattern ◄──── (you are here)
(rate/concurrency limits per client; 429 + Retry-After; algorithm: token/leaky/window)
        │
        ├── Retry Pattern: consumer retries on 429 (with Retry-After header)
        ├── Bulkhead Pattern: Bulkhead = concurrency throttle per downstream
        ├── Backpressure Pattern: Throttling is one mechanism for backpressure
        └── API Gateway: throttling implemented at gateway layer (Kong, AWS API GW)
```

---

### 💻 Code Example

```java
// Bucket4j + Redis distributed rate limiter (per-API-key):

@Service @RequiredArgsConstructor
public class RateLimiterService {
    
    private final RedisTemplate<String, String> redis;
    private final ObjectMapper mapper;
    
    // Token bucket: 1000 tokens, refills 1000/hour
    private static final long   CAPACITY       = 1_000;
    private static final double REFILL_PER_SEC = 1_000.0 / 3600.0;  // ~0.278/sec
    
    private static final DefaultRedisScript<List> TOKEN_BUCKET_SCRIPT =
        new DefaultRedisScript<>(REDIS_LUA_SCRIPT, List.class);
    
    public RateLimitResult checkLimit(String apiKey, String endpoint) {
        String key = "rate:" + apiKey + ":" + endpoint;
        long now = Instant.now().getEpochSecond();
        
        List<Long> result = (List<Long>) redis.execute(
            TOKEN_BUCKET_SCRIPT,
            List.of(key),
            String.valueOf(CAPACITY),
            String.valueOf(REFILL_PER_SEC),
            String.valueOf(now)
        );
        
        boolean allowed = result.get(0) == 1L;
        long remaining = result.get(1);
        long resetAt = now + (long)((CAPACITY - remaining) / REFILL_PER_SEC);
        
        return new RateLimitResult(allowed, CAPACITY, remaining, 
                                    Instant.ofEpochSecond(resetAt),
                                    allowed ? 0 : (long)(1.0 / REFILL_PER_SEC));
    }
}

// Rate limit response headers (standard RFC 6585 / IETF draft):
// X-RateLimit-Limit:     1000      (max requests per window)
// X-RateLimit-Remaining: 847       (remaining in current window)
// X-RateLimit-Reset:     1704067200 (Unix timestamp when window resets)
// Retry-After:           3600      (seconds until retry is allowed, on 429)
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Throttling at the application level is sufficient | Application-level throttling requires every request to reach the application (and be processed up to the throttle check). At high enough request rates, even the throttle check itself can overwhelm the application. Throttling should be implemented as close to the entry point as possible: API Gateway (AWS API GW, Kong, Nginx rate limiting) or load balancer. Application-level throttling (Resilience4j, Bucket4j) is for per-operation protection within the application, not for protecting against volumetric attacks. |
| All throttling algorithms are equivalent | Token Bucket allows bursting (unused capacity accumulates). Leaky Bucket enforces strict rate (no burst). Sliding Window provides precise counting but uses more memory. Token Bucket is right for APIs where burst is acceptable (user queries). Leaky Bucket is right for payment processing where strict rate is required. Choose based on whether bursting is acceptable for the specific resource being protected. |
| Throttling prevents DDoS | Throttling limits request rate per source (API key, IP). A distributed DDoS from millions of unique IPs: each IP under the per-IP limit → throttling ineffective. Throttling prevents abuse from individual sources and protects against accidental overload (buggy retry loops, traffic spikes). DDoS mitigation requires: upstream scrubbing services (Cloudflare, AWS Shield), BGP-level filtering, and capacity provisioning beyond what throttling can address. |

---

### 🔥 Pitfalls in Production

**Shared rate limit counter across distributed instances causing inconsistent limiting:**

```java
// ANTI-PATTERN — in-memory rate limiter (doesn't work across multiple instances):
@Component
class InMemoryRateLimiter {
    // ONE counter PER APPLICATION INSTANCE:
    private final ConcurrentHashMap<String, AtomicInteger> counters = new ConcurrentHashMap<>();
    
    public boolean isAllowed(String apiKey) {
        counters.putIfAbsent(apiKey, new AtomicInteger(0));
        // This is per-instance, not per-cluster!
        return counters.get(apiKey).incrementAndGet() <= 100;
    }
}

// Problem: 4 application instances behind a load balancer.
// Each instance: allows 100 req/min per API key.
// Total allowed: 400 req/min per API key (4 × 100).
// Advertised limit: 100 req/min. Actual limit: 400 req/min.
// Rate limit is meaningless — 4x the intended limit.
// Also: counters never reset — after first 100 requests: ALL future requests rejected.

// FIX — distributed rate limiter using Redis:
// Redis is shared across ALL instances → single consistent counter.
// Lua script ensures atomic check + decrement → no race conditions.
// TTL on Redis keys → counters reset automatically.

// CORRECT ARCHITECTURE:
// Load Balancer → Instance 1 ──┐
// Load Balancer → Instance 2 ──┤──► Redis Rate Limit Counter (shared)
// Load Balancer → Instance 3 ──┘
// All instances check the SAME Redis counter for each API key.
// Effective limit: 100 req/min regardless of how many instances serve the traffic.
```

---

### 🔗 Related Keywords

- `Retry Pattern` — consumer retries on 429 (respecting `Retry-After` header)
- `Backpressure Pattern` — Throttling is a form of backpressure: producer is slowed to match consumer capacity
- `Bulkhead Pattern` — Bulkhead = concurrency throttle per downstream dependency
- `API Gateway` — throttling implemented at the gateway layer (Kong rate limiting, AWS API Gateway)
- `Token Bucket` — the most common throttling algorithm (allows bursting, memory-efficient)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Limit request rate per client. Return 429 │
│              │ + Retry-After when exceeded. Protect     │
│              │ resources. Enforce SLA tiers.            │
├──────────────┼───────────────────────────────────────────┤
│ ALGORITHMS   │ Token Bucket (bursting OK);              │
│              │ Leaky Bucket (strict rate);              │
│              │ Sliding Window Counter (balanced)        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ API exposed to external clients;         │
│              │ expensive operations to protect;         │
│              │ SLA tiers to enforce                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Highway on-ramp metering light: one car │
│              │  per green. More arrive than allowed:   │
│              │  wait on the ramp or take another route."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Retry Pattern → Backpressure → Bulkhead  │
│              │ → Token Bucket → API Gateway Rate Limits  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Token Bucket algorithm allows bursting: if a client hasn't used their full allocation, they accumulate tokens that can be used for a burst. This is useful for human-driven APIs (browser-based: traffic is bursty by nature). But for some operations (payment processing, ML inference), bursting may be undesirable — even a burst of 50 simultaneous heavy requests can overwhelm the resource. How do you choose between Token Bucket (allows burst) vs. Leaky Bucket (strict rate) for a given API endpoint? What operational characteristics of the protected resource determine the appropriate algorithm?

**Q2.** Rate limiting in a distributed system requires a shared counter — Redis is the standard choice. But Redis itself can become a bottleneck or single point of failure for rate limiting at very high throughput (>1M req/sec). At that scale, options include: (a) approximate rate limiting with local counters synchronized periodically, (b) consistent hashing to shard rate limit keys across Redis cluster, (c) hardware rate limiting at the network layer. How does Redis Cluster shard rate limit keys, and what happens to rate limit accuracy when the cluster is under partition (network split) — what consistency model does Redis use for rate limit operations?
