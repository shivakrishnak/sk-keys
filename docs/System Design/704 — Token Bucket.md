---
layout: default
title: "Token Bucket"
parent: "System Design"
nav_order: 704
permalink: /system-design/token-bucket/
number: "704"
category: System Design
difficulty: ★★★
depends_on: "Rate Limiting (System)"
used_by: "Rate Limiting (System), Leaky Bucket, API Gateway"
tags: #advanced, #distributed, #architecture, #performance, #reliability
---

# 704 — Token Bucket

`#advanced` `#distributed` `#architecture` `#performance` `#reliability`

⚡ TL;DR — **Token Bucket** is a rate limiting algorithm where tokens accumulate in a bucket at a fixed rate; each request consumes one token — burst traffic is allowed up to the bucket capacity while long-term rate is enforced by the fill rate.

| #704            | Category: System Design                           | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Rate Limiting (System)                            |                 |
| **Used by:**    | Rate Limiting (System), Leaky Bucket, API Gateway |                 |

---

### 📘 Textbook Definition

**Token Bucket** is a rate limiting and traffic shaping algorithm that maintains a virtual "bucket" holding up to B tokens (the burst capacity). Tokens are added to the bucket at a constant rate R (tokens per second). Each incoming request must consume one token. If the bucket has tokens available, the request is processed and a token is consumed. If the bucket is empty, the request is either queued or rejected. The bucket never exceeds its capacity B; excess tokens (when demand is below the fill rate) are discarded. The algorithm enforces: (1) a sustained average rate of at most R requests/second (governed by fill rate); (2) a burst limit of B simultaneous requests (governed by bucket size). Token Bucket is used widely in network QoS (traffic policing), API rate limiting (AWS API Gateway, Stripe), and OS scheduling (Linux kernel's `tc` traffic shaper).

---

### 🟢 Simple Definition (Easy)

Token Bucket: a jar fills with tokens at 1 per second (max 10 tokens in the jar). Send a request → take 1 token. No tokens → request rejected. Quiet for 10 seconds → jar fills to 10 tokens → you can burst 10 requests instantly. The jar prevents continuous flooding but allows short bursts.

---

### 🔵 Simple Definition (Elaborated)

Token Bucket is burst-friendly rate limiting. Fill rate = 100 tokens/second. Bucket size = 1,000 tokens. If a client sends 0 requests for 10 seconds, the bucket fills to 1,000 tokens. Then the client can send 1,000 requests in one second (a burst). But after that burst, the bucket is empty — the client must wait for tokens to refill at 100/second. Average rate over any sustained period: ≤ 100 requests/second. Maximum instantaneous burst: 1,000. This makes Token Bucket ideal for real user traffic (intermittent, bursty) while protecting against sustained high-rate attacks.

---

### 🔩 First Principles Explanation

**Token Bucket mechanics and implementation:**

````
TOKEN BUCKET STATE:
  - tokens:     current token count  (float, range: 0.0 to capacity)
  - capacity:   maximum tokens        (integer, e.g., 1000)
  - fill_rate:  tokens added/second  (float, e.g., 100.0)
  - last_refill: timestamp of last refill (Unix nanoseconds)

REFILL CALCULATION (lazy evaluation — no background timer needed):

  On each request:
  1. Calculate elapsed time since last refill:
     elapsed = now - last_refill

  2. Add tokens proportional to elapsed time:
     new_tokens = elapsed × fill_rate
     tokens = min(capacity, tokens + new_tokens)

  3. Update last_refill = now

  4. Check if request can proceed:
     if tokens >= 1:
       tokens -= 1
       return ALLOW
     else:
       return DENY  (or QUEUE)

COMPLETE EXAMPLE:

  Config: fill_rate = 10 tokens/sec, capacity = 20 tokens

  T=0s:   Initial state: tokens = 20 (full bucket)
  T=0s:   10 requests arrive: tokens = 20 - 10 = 10. All ALLOWED.
  T=0s:   15 more requests arrive: 10 allowed (tokens exhausted), 5 DENIED.
  T=5s:   5 requests arrive.
          Elapsed = 5s. New tokens = 5 × 10 = 50, capped at 20.
          tokens = 20. 5 requests allowed, tokens = 15.
  T=6s:   Request arrives.
          Elapsed = 1s. New tokens = 1 × 10 = 10.
          tokens = min(20, 15 + 10) = 20. (would be 25 but capped)
          1 request allowed. tokens = 19.

COMPARISON: TOKEN BUCKET vs LEAKY BUCKET

  Token Bucket:
    - Allows BURSTS up to bucket capacity
    - Long-term rate capped at fill_rate
    - Request timing: variable (bursty OK)
    - Use case: APIs with bursty but bounded clients (normal user behaviour)

    Timeline: |████████    |██   |█████████████|
              burst  empty  refill  normal use

  Leaky Bucket:
    - SMOOTHS bursts to constant output rate
    - Input: any rate (bursts OK); Output: fixed rate
    - Excess requests: queued (up to queue limit) or dropped
    - Use case: network traffic shaping, audio/video streaming (constant bitrate)

    Timeline: |████|████|████|████|████|████|████|
              smooth constant rate regardless of input bursts

DISTRIBUTED TOKEN BUCKET (Redis implementation):

  Problem: multiple server instances must share token state.
  Solution: store bucket state in Redis; use Lua for atomic operations.

  Lua script (atomic token check-and-consume):
  ```lua
  local key = KEYS[1]           -- bucket key: "tb:user123"
  local capacity = tonumber(ARGV[1])    -- e.g., 1000
  local fill_rate = tonumber(ARGV[2])   -- e.g., 100 (tokens/sec)
  local now = tonumber(ARGV[3])         -- current Unix timestamp (seconds float)
  local requested = tonumber(ARGV[4])   -- tokens requested (usually 1)

  -- Get current bucket state:
  local bucket = redis.call("HMGET", key, "tokens", "last_refill")

  local tokens = tonumber(bucket[1]) or capacity  -- default: full bucket on first use
  local last_refill = tonumber(bucket[2]) or now

  -- Refill:
  local elapsed = now - last_refill
  local new_tokens = elapsed * fill_rate
  tokens = math.min(capacity, tokens + new_tokens)
  last_refill = now

  -- Check and consume:
  local allowed = 0
  if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
  end

  -- Save updated state (TTL = 2× refill window to expire idle buckets):
  redis.call("HMSET", key, "tokens", tokens, "last_refill", last_refill)
  redis.call("EXPIRE", key, math.ceil(capacity / fill_rate) * 2)

  return {allowed, tokens}  -- returns: 1=allow/0=deny, remaining tokens
````

WEIGHTED REQUESTS (cost > 1 per operation):

Not all operations cost equally:

- Simple GET: 1 token
- Complex search: 5 tokens
- Bulk export: 50 tokens

Implementation: pass requested = N (not 1) to token check.
Example: Search API costs 5 tokens.
Bucket: 100 tokens/min = 100 simple GETs/min OR 20 searches/min OR 2 bulk exports/min.
This aligns rate limit cost with actual server resource consumption.

````

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Token Bucket (Fixed Window limit):
- Short bursts from real users rejected unfairly (user pressed submit twice → second request blocked)
- Window reset exploitable: 2× the limit in one window boundary

WITH Token Bucket:
→ Bursts allowed: idle time accumulates capacity for legitimate burst usage
→ Sustained rate enforced: no long-term abuse possible
→ Natural user behaviour accommodated: humans request in bursts, not perfectly evenly

---

### 🧠 Mental Model / Analogy

> A parking meter refills at 1 coin per minute, maximum 10 coins stored. When you arrive, you find 8 coins already accumulated. You can park for 8 hours immediately. But if you park for 12 hours, you'll run out of coins after 8 + (however many accumulate during your visit). The meter never gives you more than 10 coins at once (capacity cap), and generates 1 per minute regardless (fill rate). You can accumulate capacity during absence, but cannot use more than you've saved.

"Parking meter coin reservoir" = token bucket (stores tokens during quiet periods)
"1 coin per minute fill rate" = token fill rate (R tokens/second)
"10 coin maximum" = bucket capacity (B, maximum burst size)
"Parking 8 hours without topping up" = burst consumption (uses stored tokens)
- "Meter runs dry after capacity exhausted" = rate limit enforced (no tokens → deny)

---

### ⚙️ How It Works (Mechanism)

**Java: thread-safe Token Bucket with lazy refill:**

```java
public class TokenBucket {
    private final double capacity;      // max tokens
    private final double fillRatePerSec; // tokens added per second
    private double tokens;              // current tokens
    private long lastRefillNanos;       // last refill timestamp

    public TokenBucket(double capacity, double fillRatePerSec) {
        this.capacity = capacity;
        this.fillRatePerSec = fillRatePerSec;
        this.tokens = capacity;          // start full
        this.lastRefillNanos = System.nanoTime();
    }

    public synchronized boolean tryConsume(double requested) {
        refill();
        if (tokens >= requested) {
            tokens -= requested;
            return true;   // allowed
        }
        return false;      // denied
    }

    private void refill() {
        long now = System.nanoTime();
        double elapsedSeconds = (now - lastRefillNanos) / 1_000_000_000.0;
        double newTokens = elapsedSeconds * fillRatePerSec;
        tokens = Math.min(capacity, tokens + newTokens);
        lastRefillNanos = now;
    }

    public double getAvailableTokens() {
        refill();
        return tokens;
    }

    // Factory: 100 req/sec average, burst up to 500:
    public static TokenBucket create100RpsWithBurst500() {
        return new TokenBucket(500, 100);
    }
}

// Usage in API handler:
@Component
public class ApiRateLimiter {

    private final Map<String, TokenBucket> buckets = new ConcurrentHashMap<>();

    public boolean isAllowed(String clientId) {
        TokenBucket bucket = buckets.computeIfAbsent(
            clientId,
            k -> new TokenBucket(1000, 100)  // 100 req/sec, burst 1000
        );
        return bucket.tryConsume(1);
    }

    // Weighted: search costs 5 tokens:
    public boolean isSearchAllowed(String clientId) {
        TokenBucket bucket = buckets.computeIfAbsent(
            clientId,
            k -> new TokenBucket(1000, 100)
        );
        return bucket.tryConsume(5);  // search = 5× cost
    }
}
````

---

### 🔄 How It Connects (Mini-Map)

```
Rate Limiting (System) — conceptual framework
        │
        ▼
Token Bucket ◄──── (you are here)
(burst-friendly algorithm)
        │
        ├── Leaky Bucket (contrast: constant rate vs burst-friendly)
        ├── API Gateway (where token bucket is typically enforced)
        └── Capacity Planning (fill rate derived from capacity limits)
```

---

### 💻 Code Example

**AWS API Gateway Token Bucket (usage plan configuration):**

```yaml
# AWS CDK: Create API Gateway Usage Plan with Token Bucket rate limiting
const api = new apigateway.RestApi(this, 'MyApi');

const usagePlan = api.addUsagePlan('StandardPlan', {
  name: 'standard',
  throttle: {
    rateLimit: 100,    // fill rate: 100 requests/second (sustained)
    burstLimit: 1000,  // bucket size: burst of 1000 requests allowed
  },
  quota: {
    limit: 1000000,    // daily quota: 1M requests per day
    period: apigateway.Period.DAY,
  },
});

// API Gateway uses Token Bucket internally:
// - rateLimit = fill rate (R)
// - burstLimit = bucket capacity (B)
// When client sends burst of 1000 requests: all allowed (tokens available)
// After burst: allowed at 100/sec (fill rate only)
// If client sends 200/sec sustained: 100 req/sec allowed, 100/sec denied (429)
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                   |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Token Bucket guarantees exactly fill_rate requests/second   | Token Bucket guarantees AT MOST fill_rate × time_period requests over any given period. A client can use tokens slower (bucket accumulates) and then burst faster. The guarantee is a maximum, not a constant rate. For constant rate, use Leaky Bucket                                                                   |
| Large bucket capacity increases the sustained rate          | Bucket capacity only increases burst size, not the sustained rate. A bucket of 10,000 tokens with 100/sec fill rate still averages ≤100 req/sec over any minute-long window. A client that consumes 10,000 tokens in 1 second must then wait 100 seconds (10,000 / 100 = 100s) to refill                                  |
| Token Bucket requires a background timer to add tokens      | Production implementations use lazy evaluation: tokens are calculated on each request based on elapsed time since last refill. No background timer, no thread, no periodic task needed. This makes it stateless between requests and efficient to implement in Redis Lua scripts                                          |
| Token Bucket and Sliding Window Counter are interchangeable | They have different burst behaviours. Token Bucket: allows bursts equal to bucket capacity. Sliding Window Counter: smoothly limits rate across the window, regardless of when within the window requests arrive. Token Bucket is better for bursty API clients; Sliding Window is better for strict fairness enforcement |

---

### 🔥 Pitfalls in Production

**Token Bucket fill rate set too high relative to backend capacity:**

```
PROBLEM: Token Bucket allows bursts that exceed database capacity

  API rate limit: 1,000 tokens/sec fill rate, 10,000 token burst capacity.
  Scenario: client is idle for 10 seconds → bucket fills to 10,000 tokens.
  Client then sends 10,000 requests in 1 second (burst).

  Rate limiter: ALLOWS (10,000 tokens available — all consumed).
  Database: 10,000 queries in 1 second vs. capacity of 2,000 QPS.
  Result: database overwhelmed. Despite rate limiting being "in place."

  ROOT CAUSE: Bucket capacity (10,000) >> database capacity (2,000/sec).
  Rate limiter allowed a burst 5× larger than backend can handle.

FIX: Size burst capacity relative to backend capacity

  Rule: burst_capacity ≤ backend_capacity × acceptable_burst_seconds

  Backend: handles 2,000 QPS.
  Acceptable burst: 2 seconds worth (to allow short legitimate bursts).
  Max burst: 2,000 × 2 = 4,000 tokens max.
  Fill rate: 2,000 tokens/sec (matching backend sustained capacity).

  But: 1,000 clients × 2,000 fill rate = 2,000,000 tokens/sec total → still overwhelming.

  PER-CLIENT limit: 2 req/sec fill rate, 4 burst capacity.
  1,000 clients × 2 = 2,000 total RPS (matches backend).
  Burst: 1,000 × 4 = 4,000 → still 2× backend... consider queue instead of burst.

  LESSON: Rate limit parameters must be derived from capacity planning,
          not set arbitrarily. Always model: what happens if ALL clients
          burst simultaneously?
```

---

### 🔗 Related Keywords

- `Rate Limiting (System)` — Token Bucket is one algorithm for implementing rate limiting
- `Leaky Bucket` — complementary algorithm: smooths to constant rate (vs Token Bucket's burst allowance)
- `Capacity Planning` — fill rate and burst capacity must be sized from capacity analysis
- `Thundering Herd (System)` — large burst capacity can cause thundering herd on backends
- `API Gateway` — AWS API Gateway, Kong, etc. implement Token Bucket natively

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Tokens fill at rate R, bucket holds max B │
│              │ — allows bursts up to B, sustained ≤ R    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ API rate limiting for bursty clients;     │
│              │ network QoS; user-facing APIs             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Constant output rate needed (use Leaky);  │
│              │ burst cap exceeds backend capacity        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Parking meter: accumulate coins while    │
│              │  parked elsewhere, spend in one burst."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Leaky Bucket → Sliding Window Counter     │
│              │ → Distributed Rate Limiting               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An API has a Token Bucket with fill_rate = 50 tokens/second and capacity = 200 tokens. A client is idle for 5 seconds, then sends 300 requests as fast as possible. Trace the exact state of the bucket: (a) after 5 seconds of idle, (b) after processing the first 200 requests, (c) 2 seconds after the burst begins, (d) 10 seconds after the burst begins. How many total requests are allowed in the first 10 seconds after the burst starts?

**Q2.** You're implementing distributed Token Bucket rate limiting across 10 API gateway instances using Redis. You've implemented it with a Lua script that atomically reads, updates, and writes the bucket state to Redis on every single request. Under a sustained load of 100,000 RPS, your Redis instance starts showing signs of saturation. What optimisations can you apply to reduce Redis load without abandoning distributed rate limiting? Describe at least 2 techniques, with the trade-offs of each.
