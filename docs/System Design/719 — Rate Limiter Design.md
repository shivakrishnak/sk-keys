---
layout: default
title: "Rate Limiter Design"
parent: "System Design"
nav_order: 719
permalink: /system-design/rate-limiter-design/
number: "719"
category: System Design
difficulty: ★★★
depends_on: "Rate Limiting (System), Token Bucket, Leaky Bucket, Distributed Locks"
used_by: "API Gateway, System Design Interview"
tags: #advanced, #system-design, #interview, #api, #rate-limiting
---

# 719 — Rate Limiter Design

`#advanced` `#system-design` `#interview` `#api` `#rate-limiting`

⚡ TL;DR — **Rate Limiter Design** enforces request quotas (e.g., 100 req/s per user) using algorithms (Token Bucket, Sliding Window Log, Fixed Window) backed by Redis, with API gateway integration for pre-application enforcement.

| #719 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Rate Limiting (System), Token Bucket, Leaky Bucket, Distributed Locks | |
| **Used by:** | API Gateway, System Design Interview | |

---

### 📘 Textbook Definition

A **Rate Limiter** is a traffic control mechanism that restricts the number of requests a client (identified by IP, user ID, API key, or other identifier) can make to a service within a defined time window. It protects downstream services from overload, prevents abuse, enforces commercial API quotas, and ensures fair resource allocation. Key design considerations: (1) algorithm choice (Fixed Window Counter, Sliding Window Log, Sliding Window Counter, Token Bucket, Leaky Bucket); (2) distributed coordination (shared state across API gateway instances via Redis); (3) enforcement placement (API gateway layer, application middleware, or SDK); (4) rate limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After); (5) soft vs hard limits (log-and-alert vs HTTP 429 reject). At scale, the rate limiter itself must be highly available — a Redis cluster outage should fail open (allow all traffic) rather than deny all traffic.

---

### 🟢 Simple Definition (Easy)

Rate Limiter: a bouncer at a club who says "You can enter 10 times per minute maximum." Eleventh request in the same minute? Bouncer says "no, come back in X seconds" (HTTP 429). The bouncer keeps a counter in their notebook (Redis). Multiple bouncers at different doors (multiple API gateway instances) — they share the same notebook (shared Redis) so the count is consistent. Counter resets every minute.

---

### 🔵 Simple Definition (Elaborated)

GitHub API rate limiting: 5,000 requests per hour per authenticated user. Each API call: check Redis counter for user. Counter < 5,000: allow request, increment counter. Counter = 5,000: return HTTP 429 with `Retry-After: 3600` header. Counter resets at the start of each hour. Without rate limiting: a buggy client script could send 100,000 requests and bring down GitHub's API for everyone. Rate limiting ensures fair allocation and protects infrastructure.

---

### 🔩 First Principles Explanation

**Rate limiting algorithms and their trade-offs:**

```
ALGORITHM 1: FIXED WINDOW COUNTER (simplest)

  Window: current 1-minute period (00:00 to 01:00, 01:00 to 02:00, ...)
  Counter: requests made this window.
  
  Implementation:
    key = "rate:" + userId + ":" + floor(now / 60_000)  // current minute bucket
    count = INCR key
    EXPIRE key 60   // auto-cleanup
    
    if count > limit:
      return 429 Too Many Requests
  
  Problem: BOUNDARY BURST
    Limit: 100 req/min.
    00:59: user sends 100 requests (counter = 100, limit hit)
    01:00: counter resets to 0
    01:01: user sends 100 more requests
    
    In 2 seconds (00:59-01:01): 200 requests allowed!
    Effective rate: 200 req / 2 seconds = 6,000 req/min (60× the limit!)

ALGORITHM 2: SLIDING WINDOW LOG (most accurate, highest memory)

  Store timestamp of every request in a sorted set.
  Count requests in [now - 60s, now].
  
  Implementation (Redis Sorted Set):
    key = "rate:log:" + userId
    now = current_timestamp_ms
    window_start = now - 60_000
    
    // Add current request timestamp:
    ZADD key now now
    
    // Remove timestamps older than window:
    ZREMRANGEBYSCORE key 0 window_start
    
    // Count requests in current window:
    count = ZCARD key
    EXPIRE key 60
    
    if count > limit:
      return 429
  
  Accurate: no boundary burst. Sliding window is exact.
  Memory: each request stored individually. 1M users × 100 requests = 100M entries.

ALGORITHM 3: SLIDING WINDOW COUNTER (balance of fixed and log)

  Combine previous window and current window with a weight.
  
  rate = prev_window_count × (1 - elapsed_in_current_window/window_size) + current_window_count
  
  Example:
    Window: 60 seconds. Limit: 100.
    Previous window (00:00-01:00): 80 requests
    Current window (01:00-02:00): 30 seconds in, 50 requests so far
    
    Estimated rate = 80 × (1 - 30/60) + 50 = 80 × 0.5 + 50 = 40 + 50 = 90
    90 < 100: allow request.
    
    If previous window had 90 requests:
    rate = 90 × 0.5 + 50 = 45 + 50 = 95 → still allow.
    
    If previous window had 100:
    rate = 100 × 0.5 + 50 = 50 + 50 = 100 → at limit: allow (101 = reject).
    
  Memory: only 2 counters per user per window. Very efficient.
  Accuracy: approximation (not exact) but sufficient for production.

ALGORITHM 4: TOKEN BUCKET (most flexible for burst handling)

  Bucket capacity = max_burst. Tokens refill at constant rate.
  Each request consumes 1 token.
  No tokens: reject request.
  
  Redis implementation (last_refill + token_count):
    tokens, last_refill = GET bucket:userId
    now = current_timestamp_ms
    elapsed = now - last_refill
    
    // Refill tokens (rate = 10 tokens/second):
    new_tokens = min(capacity, tokens + elapsed × (10 / 1000))
    
    if new_tokens >= 1:
      SET bucket:userId (new_tokens - 1, now)
      allow request
    else:
      reject 429
  
  Advantage: allows bursts (user can use stored tokens for spike).
  Disadvantage: complex atomic update (must use Lua script for atomicity).
  
  USE WHEN: API that allows occasional bursts (client can burst 10 calls, then waits)

ALGORITHM 5: LEAKY BUCKET (smoothest output, queue-based)

  Requests enter a fixed-size queue (the bucket). 
  Queue drains at constant rate (the leak).
  Overflow: reject.
  
  USE WHEN: You need constant output rate (payment processors, SMS sending)
            Burst smoothing: spiky input → steady output
  
  AVOID WHEN: Low-latency APIs (queue adds latency to every request)

DISTRIBUTED RATE LIMITER ARCHITECTURE:

  Problem: 10 API gateway instances sharing rate limit state.
  
  Single Redis cluster:
  ┌─────────────────────────────────────────────┐
  │           API Gateway Cluster               │
  │  [Instance 1]  [Instance 2]  [Instance 3]   │
  └─────────────┬───────────┬────────────┬──────┘
                └───────────┴────────────┘
                            │
                   [Redis Cluster]
                  (shared rate limit state)
  
  Every gateway instance:
    1. Check Redis counter for user_id
    2. If under limit: increment counter, allow request
    3. If over limit: return 429
    
  Atomic check-and-increment (Lua script to prevent race condition):
  
  local key = KEYS[1]
  local limit = tonumber(ARGV[1])
  local ttl = tonumber(ARGV[2])
  
  local count = redis.call("INCR", key)
  if count == 1 then
      redis.call("EXPIRE", key, ttl)
  end
  
  if count > limit then
      return {0, count}  -- rejected, current count
  else
      return {1, count}  -- allowed, current count
  end
  
  FAILURE MODE (Redis is down):
    Option 1: FAIL OPEN — allow all requests (service degraded but available)
    Option 2: FAIL CLOSED — reject all requests (safe but unavailable)
    
    RECOMMENDATION: Fail open (Redis outage is temporary; better to allow some traffic
                    than deny all legitimate users). Add circuit breaker around Redis calls.
    
    Implementation:
    try {
      boolean allowed = redisRateLimiter.check(userId, limit);
      if (!allowed) return 429;
    } catch (RedisException e) {
      log.warn("Rate limiter Redis error — failing open");
      // Allow request (fail open)
    }

RATE LIMIT HEADERS (RFC 7231 + GitHub/Twitter conventions):

  HTTP Response Headers:
  X-RateLimit-Limit: 100          // max requests per window
  X-RateLimit-Remaining: 74       // remaining requests this window
  X-RateLimit-Reset: 1698765432   // Unix timestamp when window resets
  Retry-After: 26                 // seconds until next allowed request (on 429)
  
  These headers allow clients to implement back-off correctly.
  Stripe, GitHub, Twitter all use this pattern.

MULTI-TIER RATE LIMITING:

  Different limits for different dimensions simultaneously:
    User level:  100 req/minute per user_id
    IP level:    1000 req/minute per IP (unauthenticated protection)
    API key:     10,000 req/minute per API key (B2B tier)
    Endpoint:    POST /payments: 10 req/minute per user (extra strict)
    Global:      1,000,000 req/minute total (protect downstream services)
  
  Check all dimensions: if ANY limit is exceeded → 429.
  
  Implementation: Redis key per dimension:
    rate:user:{user_id}:{window}
    rate:ip:{ip_address}:{window}
    rate:key:{api_key}:{window}
    rate:endpoint:{endpoint}:{user_id}:{window}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Rate Limiter:
- One misbehaving client can saturate all CPU/DB connections for everyone
- DDoS amplification: single IP sends 1M requests → service down for all users
- Resource starvation: one heavy user monopolises shared infrastructure

WITH Rate Limiter:
→ Fair allocation: every user gets equal access to shared resources
→ DDoS mitigation: attackers' requests rejected at gateway, before reaching app servers
→ Cost control: API providers can enforce paid tiers via rate limits

---

### 🧠 Mental Model / Analogy

> A turnstile at a subway station that only allows 10 people through per minute. Person 11: turnstile locks, displays "wait 30 seconds" (Retry-After header). Each subway line has its own turnstile (endpoint-level limits). There's also a turnstile for the entire station (global rate limit). A regular commuter (API key) gets a faster turnstile than a tourist (anonymous IP). The turnstile count is displayed on a board visible to everyone (X-RateLimit-Remaining header).

"Turnstile allowing 10/minute" = rate limit rule (100 req/min per user)
"Person 11 is blocked" = HTTP 429 Too Many Requests
"Wait 30 seconds" = Retry-After header (time until reset)
"Count board" = X-RateLimit-Remaining header (transparency for clients)
"Regular commuter faster turnstile" = API tier (higher limit for premium users)

---

### ⚙️ How It Works (Mechanism)

**Sliding Window Counter implementation with Redis:**

```java
@Component
public class SlidingWindowRateLimiter {
    
    @Autowired private RedisTemplate<String, String> redis;
    
    private static final String LUA_SCRIPT = """
        local key = KEYS[1]
        local prev_key = KEYS[2]
        local limit = tonumber(ARGV[1])
        local window_size = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        local ttl = tonumber(ARGV[4])
        
        -- Get previous window count and current window count:
        local prev_count = tonumber(redis.call("GET", prev_key) or "0")
        local curr_count = tonumber(redis.call("GET", key) or "0")
        
        -- Calculate elapsed fraction into current window:
        local elapsed = (current_time % window_size) / window_size
        
        -- Estimated rate (sliding window approximation):
        local rate = prev_count * (1 - elapsed) + curr_count
        
        if rate >= limit then
            return {0, math.ceil(rate)}  -- rejected
        end
        
        -- Increment current window counter:
        local new_count = redis.call("INCR", key)
        if new_count == 1 then
            redis.call("EXPIRE", key, ttl)
        end
        
        return {1, math.ceil(rate + 1)}  -- allowed, approximate count
        """;
    
    public RateLimitResult check(String userId, int limitPerMinute) {
        long now = System.currentTimeMillis();
        long windowSize = 60_000L;  // 60 seconds in ms
        long currentWindow = now / windowSize;
        long prevWindow = currentWindow - 1;
        
        String currentKey = "rate:" + userId + ":" + currentWindow;
        String prevKey = "rate:" + userId + ":" + prevWindow;
        
        List<Object> result = redis.execute(
            RedisScript.of(LUA_SCRIPT, List.class),
            List.of(currentKey, prevKey),
            String.valueOf(limitPerMinute),
            String.valueOf(windowSize),
            String.valueOf(now),
            "120"  // TTL: 2 windows
        );
        
        boolean allowed = ((Number) result.get(0)).intValue() == 1;
        int count = ((Number) result.get(1)).intValue();
        long resetAt = (currentWindow + 1) * windowSize / 1000;  // Unix seconds
        
        return new RateLimitResult(allowed, limitPerMinute, limitPerMinute - count, resetAt);
    }
}

// Spring filter: applies rate limiting to all API requests
@Component
@Order(1)
public class RateLimitFilter implements Filter {
    
    @Autowired private SlidingWindowRateLimiter rateLimiter;
    
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        
        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) res;
        
        String userId = extractUserId(request);  // from JWT, API key, or IP
        int limit = getLimitForUser(userId);       // 100 for free, 10K for premium
        
        RateLimitResult result = rateLimiter.check(userId, limit);
        
        // Always set rate limit headers:
        response.setHeader("X-RateLimit-Limit", String.valueOf(result.getLimit()));
        response.setHeader("X-RateLimit-Remaining", String.valueOf(result.getRemaining()));
        response.setHeader("X-RateLimit-Reset", String.valueOf(result.getResetAt()));
        
        if (!result.isAllowed()) {
            response.setStatus(429);
            response.setHeader("Retry-After", String.valueOf(
                result.getResetAt() - System.currentTimeMillis() / 1000));
            response.getWriter().write("{\"error\": \"Too Many Requests\"}");
            return;
        }
        
        chain.doFilter(req, res);
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
API abuse / resource exhaustion risk
        │
        ▼
Rate Limiter Design ◄──── (you are here)
(Token Bucket / Sliding Window / Fixed Window)
        │
        ├── Redis (shared counter state across gateway instances)
        ├── API Gateway (integration point for pre-application enforcement)
        └── Token Bucket / Leaky Bucket (underlying algorithms)
```

---

### 💻 Code Example

**Token Bucket rate limiter using Redis Lua for atomicity:**

```python
import redis
import time

BUCKET_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])  -- tokens per second
local now = tonumber(ARGV[3])

local bucket = redis.call("HMGET", key, "tokens", "last_refill")
local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

-- Calculate tokens added since last refill:
local elapsed = now - last_refill
local new_tokens = math.min(capacity, tokens + elapsed * refill_rate)

if new_tokens >= 1 then
    -- Consume one token:
    redis.call("HMSET", key, "tokens", new_tokens - 1, "last_refill", now)
    redis.call("EXPIRE", key, math.ceil(capacity / refill_rate) + 1)
    return {1, math.floor(new_tokens - 1)}  -- allowed, remaining tokens
else
    redis.call("HMSET", key, "tokens", new_tokens, "last_refill", now)
    redis.call("EXPIRE", key, math.ceil(capacity / refill_rate) + 1)
    return {0, 0}  -- rejected
end
"""

r = redis.Redis()
script = r.register_script(BUCKET_SCRIPT)

def check_rate_limit(user_id: str, capacity: int = 10, refill_rate: float = 2.0):
    """Token Bucket: capacity=10 (max burst), refill=2 tokens/second."""
    key = f"bucket:{user_id}"
    now = time.time()
    result = script(keys=[key], args=[capacity, refill_rate, now])
    allowed = result[0] == 1
    remaining = result[1]
    return allowed, remaining

# Usage:
for i in range(15):
    allowed, remaining = check_rate_limit("user:123")
    print(f"Request {i+1}: {'✓' if allowed else '✗ 429'} (tokens remaining: {remaining})")

# Output:
# Request 1-10: ✓ (immediate burst up to capacity)
# Request 11: ✗ 429 (bucket empty)
# Request 12: ✗ 429 (bucket still refilling)
# [after 0.5s] next check: ✓ (1 token refilled: 2 tokens/sec × 0.5s = 1 token)
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Rate limiting is only for DDoS protection | Rate limiting serves multiple purposes: (1) DDoS/abuse prevention, (2) fair resource allocation among users, (3) commercial API tier enforcement (free vs paid plans), (4) protecting downstream services from cascading overload, (5) cost control (preventing unexpectedly expensive clients). Each use case may have different limits and algorithms |
| Redis INCR is sufficient for race-condition-free rate limiting | `INCR` alone is atomic, but `GET → check → INCR` across multiple commands is NOT atomic. Between GET and INCR, another request may increment the counter — causing two requests to both see count=99, both check < 100, both INCR to 100 and 101 — both allowed. Solution: use Lua scripts for atomic multi-command operations, or Redis 7+ GETSET patterns |
| A rate limiter should always reject over-limit requests | Soft rate limiting is often better: log the violation, let the request through, send an alert. Hard limits (429 rejection) should be reserved for abuse scenarios. Many systems use a tiered approach: >100% limit = throttle (slow down); >200% limit = reject. This reduces false positives where legitimate requests are blocked during traffic spikes |
| Rate limiting at the application layer is sufficient | Application-layer rate limiting is bypassed if the request load is enough to saturate the application servers before rate limit logic even runs. Rate limiting should be at the API gateway / load balancer layer — before requests reach application servers. Application-layer rate limiting is only appropriate for business logic rate limits (e.g., max 3 password reset attempts per hour) |

---

### 🔥 Pitfalls in Production

**Rate limit bypass via multiple IP addresses:**

```
PROBLEM: Rate limiting by IP is trivially bypassed by distributed attackers

  Rate limit: 100 requests/minute per IP address
  Attacker: controls botnet of 10,000 IP addresses
  Each IP: sends 99 requests/minute (just under limit)
  
  Total: 10,000 × 99 = 990,000 requests/minute to your service
  All requests: "allowed" by IP-based rate limiter
  Your service: overwhelmed

IP-BASED RATE LIMITING IS INSUFFICIENT ALONE:
  Multiple users behind NAT (corporate proxy): all share one IP → legitimate users blocked
  IPv6: attackers have effectively unlimited IP addresses
  VPNs/proxies: easy to rotate IP addresses

LAYERED RATE LIMITING STRATEGY:

  Layer 1: IP rate limit (broad, high threshold — stop obvious floods):
    100 req/second per IP (allows shared NAT, blocks flood attacks)
    
  Layer 2: User/API key rate limit (primary protection):
    100 req/minute per authenticated user_id
    Unauthenticated requests: rate limited more aggressively by IP
    
  Layer 3: Endpoint-specific rate limit:
    POST /auth/login: 5 attempts/minute (brute force protection)
    POST /payments: 10/minute per user (financial safety)
    POST /password-reset: 3/hour per user
    
  Layer 4: Global rate limit:
    Total requests/second: alert if > 1M (anomaly detection, not hard block)
    
  Layer 5: Behavioral detection (beyond simple rate limiting):
    Same IP cycling through user accounts → temporary block
    High error rate (all 401s) → suspect credential stuffing → captcha challenge

REDIS RATE LIMIT CLUSTER FAILURE:
  
  If Redis is down → all rate limit checks fail → fail-open or fail-closed?
  
  FIX: Circuit breaker around Redis rate limiter:
    - Redis healthy: enforce rate limits normally
    - Redis unavailable (circuit open): allow all traffic + alert
    - Never fail-closed: rate limiter outage should NOT cause service outage
    
  Secondary protection: even without Redis rate limits, downstream services have
  their own protection (DB connection pools, CPU limits). The service degrades
  gracefully rather than hard-failing.
```

---

### 🔗 Related Keywords

- `Token Bucket` — algorithm allowing burst requests up to bucket capacity
- `Leaky Bucket` — algorithm smoothing traffic to constant output rate
- `API Gateway` — integration point for centralized rate limiting enforcement
- `Redis` — shared state for distributed rate limit counters across gateway instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Shared Redis counter per user/window;     │
│              │ Lua for atomic check+increment            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ API quota enforcement; DDoS mitigation;   │
│              │ fair resource sharing; commercial tiers   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ IP-only rate limiting for auth endpoints; │
│              │ fail-closed on Redis outage               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Subway turnstile — 10 people/min;        │
│              │  shared counter board everyone can see."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Token Bucket → API Gateway Design         │
│              │ → Circuit Breaker                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing rate limits for a public REST API with three tiers: Free (100 req/hour), Pro (10,000 req/hour), Enterprise (unlimited). The rate limit state must be shared across 20 API gateway instances. Design the Redis data model: what is the key structure? What algorithm do you choose (Fixed Window, Sliding Window Counter, Token Bucket)? How do you handle a user upgrading from Free to Pro mid-hour (they've already used 80 of their 100 free requests)? What happens to their counter when they upgrade?

**Q2.** A mobile gaming company uses rate limiting to prevent cheating: "each player can claim a daily bonus only once per 24 hours." The 24-hour window resets at midnight UTC. A player claims their bonus at 11:59 PM — successfully. At 12:00 AM (next day), they try again — correctly expecting to claim the next day's bonus. Using a Fixed Window counter (midnight-to-midnight), does this work correctly? Using a Sliding Window (last 24 hours from claim time), does this work correctly? Which approach is more appropriate for this specific use case, and why?
