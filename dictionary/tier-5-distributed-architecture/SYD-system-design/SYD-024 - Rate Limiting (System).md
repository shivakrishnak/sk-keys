---
id: SYD-052
title: "Rate Limiting (System)"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-018
used_by: SYD-054, SYD-055, SYD-064
related: SYD-054, SYD-055
tags:
  - performance
  - intermediate
  - architecture
  - reliability
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 24
permalink: /syd/rate-limiting-system/
---

# SYD-041 - Rate Limiting (System)

⚡ TL;DR - Limiting request rate from clients to prevent overload, DDoS attacks, and resource exhaustion. Implemented at API gateway, per-user, per-endpoint levels.

| #703            | Category: System Design                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Throttling, Infrastructure           |                 |
| **Used by:**    | API Management, DDoS Protection, Resource Protection |                 |
| **Related:**    | Token Bucket, Leaky Bucket, Throttling               |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Single user sends 10,000 requests/sec. Other users starved. System overloaded. DDoS possible.

**THE BREAKING POINT:**
Need to prevent single client from monopolizing resources.

**THE INVENTION MOMENT:**
"Limit requests per user per time window. User exceeds limit? Reject or queue."

**EVOLUTION:**
Rate limiting began as a network-level concept in the 1970s - telephone switches rate-limited incoming calls to prevent network congestion. Web applications adopted rate limiting in the early 2000s as DDoS attacks became common. AWS API Gateway (2015) made managed rate limiting a service rather than a custom implementation. OAuth 2.0 and API management platforms standardised rate limit headers (X-RateLimit-Remaining, Retry-After). The discipline evolved from low-level network protection to a business policy tool: rate limits are now used for tiered pricing (free tier vs paid tier API limits) as much as for technical protection.

---

### 📘 Textbook Definition

**Rate Limiting:** Technique to control the rate at which clients can make requests to a service. Requests exceeding configured limits are rejected (HTTP 429) or queued, preventing overload and DDoS attacks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Allow max 100 requests per user per minute. Exceed? Get 429 (Too Many Requests).

**One analogy:**

> Movie theater: "Max 1000 tickets sold per day. Today's limit reached? Reject new sales."

**One insight:**
Simple, effective defense against abuse and accidental overload.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Resource finite (server capacity, bandwidth)
2. Single user can monopolize if unchecked
3. Limit must be enforced per user/endpoint
4. Honest users unaffected
5. Abusive users rejected/throttled

**RATE LIMITING STRATEGIES:**

1. **Per-User**: User gets limit (e.g., 100 req/min)
2. **Per-Endpoint**: Endpoint gets total limit (e.g., /api/users max 10K req/min)
3. **Per-IP**: All requests from IP limited (coarse, but effective for DDoS)
4. **Tiered**: Different limits by user tier (free: 100, premium: 10K)

**THE TRADE-OFFS:**
**Gain:** Prevent overload. Protect honest users. Simple to implement.

**Cost:** False positives (legitimate spike rejected). Complexity (track per-user state). Storage (need to track quotas).

---

### 🧪 Thought Experiment

**SCENARIO:**
Payment API. 1000 users. Each should get max 100 req/min.

**Without Rate Limiting:**

- Malicious user sends 50,000 req/sec
- Legitimate users' requests queued, timeout
- Service appears down
- Payment processing halts

**With Rate Limiting:**

- Malicious user: first 100 requests accepted, 101st → 429 (Too Many Requests)
- Malicious user: backoff required (exponential)
- Legitimate users: unaffected (still get 100 req/min)
- Service healthy

---

### 🧠 Mental Model / Analogy

> Bank teller: "Max 10 customers per hour. 11th customer: come back later." Simple, fair, prevents mob situations.

- "Teller" → API
- "10 customers/hour" → rate limit
- "Come back later" → HTTP 429 or queue

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
API limits how fast you can make requests. Too many? Rejected. Prevents abuse.

**Level 2 - How to use it (junior developer):**
Implement rate limiting at API gateway. Track requests per user (Redis counter). If count > limit, return 429.

**Level 3 - How it works (mid-level engineer):**
Rate limiting strategies: sliding window (precise), token bucket (smooth), leaky bucket (FIFO). Implement in gateway or service. Persist state in Redis/cache. Return 429 or queue for backoff.

**Level 4 - Why it was designed this way (senior/staff):**
Rate limiting emerged from: (1) protection against DDoS, (2) resource fair-sharing, (3) cost control (metering). Different strategies trade precision vs. memory: sliding window precise but memory-heavy; token bucket smooth and memory-light. Used by all major APIs (Stripe, AWS, Twitter).

---

### ⚙️ How It Works (Mechanism)

Rate limiting mechanisms:

```
MECHANISM 1: FIXED WINDOW COUNTER (Simple but flawed)
──────────────────────────────────────────────────────
Count requests in 1-minute window:

Minute 1 (00:00-00:59): User makes 100 requests
  Counter = 100 (limit reached)
  Request 101 in minute 1: REJECTED (429)

Minute 2 (01:00-01:59): Counter resets to 0
  Request 1 in minute 2: ACCEPTED (edge burst possible)

Flaw: At window boundary (00:59 and 01:00)
  User can make 200 requests in 2 seconds:
    - 0 at 00:59 (window 1 nearly full)
    - 100 at 01:00 (window 2 starts)
  Bypasses rate limit!

MECHANISM 2: SLIDING WINDOW (Accurate)
──────────────────────────────────────
Track exact request timestamps:

User requests at:
  00:01, 00:05, 00:10, 00:20, 00:55, 00:59
  (6 requests in 1 minute window)

At 01:01 (1 minute later):
  Window slides: 00:01-01:01
  Old request at 00:01 exits window
  5 requests remain
  New request at 01:01: ACCEPTED

Accurate but memory-intensive (store timestamps)

MECHANISM 3: TOKEN BUCKET (Smooth, efficient)
──────────────────────────────────────────────
Bucket contains tokens. Each request consumes 1 token.
Tokens replenished at rate.

Bucket capacity: 100 tokens
Refill rate: 100 tokens per minute (1.67/sec)

Time 00:00: Bucket = 100 tokens (full)
  Request 1: 100-1 = 99 tokens (ACCEPTED)
  Request 2: 99-1 = 98 tokens (ACCEPTED)
  ... (100 requests in first 2 seconds)
  Request 101: 0 tokens (REJECTED, 429)

At 00:02: 100 + (2 sec * 1.67 tokens/sec) = 103 tokens (cap at 100)
  New request: 100-1 = 99 tokens (ACCEPTED)

Smooth, doesn't penalize bursts (first 100 requests instant)

MECHANISM 4: LEAKY BUCKET (FIFO queue)
──────────────────────────────────────
Requests queue in bucket. Leak at constant rate.

Bucket size: 100 requests max
Leak rate: 100 requests per minute (1.67/sec)

Time 00:00:
  Request 1-100: queued
  Bucket size: 100 (full, no room for more)
  Request 101: REJECTED (bucket full)

Requests leak out at 1.67/sec (processing rate controlled)
All queued requests eventually served (FIFO)

Advantage: Smooth, predictable processing
Disadvantage: Requests queued (higher latency)
```

**Rate Limiting Levels:**

```
LEVEL 1: API Gateway (Global)
  All requests through gateway
  Global rate limit: 100K req/sec
  Per-IP rate limit: 10K req/sec
  Per-endpoint limit: 5K req/sec

LEVEL 2: Per-User (Authenticated)
  User ID 123: 1000 req/min
  User ID 456: 10K req/min (premium)

LEVEL 3: Per-Endpoint (Resource-specific)
  /api/search: 100 req/sec (expensive, slow)
  /api/health: unlimited (cheap)

LEVEL 4: Per-Customer/Tenant (Multi-tenant)
  Customer A: 10 million req/month quota
  Customer B: 1 billion req/month quota
```

---

### 💻 Code Example

**Example 1 - Token Bucket Rate Limiter (Python):**

```python
from time import time
from collections import defaultdict

class TokenBucketRateLimiter:
    def __init__(self, capacity, refill_rate):
        """
        capacity: max tokens in bucket
        refill_rate: tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = defaultdict(lambda: {'tokens': capacity, 'last_refill': time()})

    def refill_tokens(self, user_id):
        """Add tokens based on time elapsed"""
        bucket = self.buckets[user_id]
        now = time()
        time_elapsed = now - bucket['last_refill']

        # Add tokens: time_elapsed * refill_rate
        new_tokens = time_elapsed * self.refill_rate
        bucket['tokens'] = min(bucket['tokens'] + new_tokens, self.capacity)
        bucket['last_refill'] = now

    def is_allowed(self, user_id):
        """Check if request allowed (consume token if yes)"""
        self.refill_tokens(user_id)
        bucket = self.buckets[user_id]

        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        return False

    def get_remaining_tokens(self, user_id):
        """Get remaining tokens for user"""
        self.refill_tokens(user_id)
        return self.buckets[user_id]['tokens']

# Usage
limiter = TokenBucketRateLimiter(capacity=100, refill_rate=10)  # 100 tokens, 10/sec

# User makes requests
for i in range(105):
    if limiter.is_allowed('user123'):
        print(f"Request {i+1}: ALLOWED")
    else:
        print(f"Request {i+1}: REJECTED (rate limited)")

    if i == 10:
        print(f"  → Waiting 1 second for refill...")
        time.sleep(1)
```

**Example 2 - Sliding Window Rate Limiter (Redis):**

```python
import redis
import time
from datetime import datetime, timedelta

class SlidingWindowRateLimiter:
    def __init__(self, redis_client, window_size_sec=60, max_requests=100):
        self.redis = redis_client
        self.window_size = window_size_sec
        self.max_requests = max_requests

    def is_allowed(self, user_id):
        """Check if request allowed using sliding window"""
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - self.window_size

        # Remove old requests outside window
        self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        count = self.redis.zcard(key)

        if count < self.max_requests:
            # Add current request timestamp
            self.redis.zadd(key, {str(now): now})
            self.redis.expire(key, self.window_size)
            return True

        return False

    def get_remaining(self, user_id):
        """Get remaining quota"""
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - self.window_size

        self.redis.zremrangebyscore(key, 0, window_start)
        count = self.redis.zcard(key)
        return max(0, self.max_requests - count)

# Usage with Redis
redis_client = redis.Redis(host='localhost')
limiter = SlidingWindowRateLimiter(redis_client, window_size_sec=60, max_requests=100)

# Check rate limit for user
if limiter.is_allowed('user@example.com'):
    print("Request allowed")
else:
    print("Rate limit exceeded")
    remaining = limiter.get_remaining('user@example.com')
    print(f"Try again in a bit. Remaining: {remaining}/100")
```

**Example 3 - Tiered Rate Limiting:**

```python
class TieredRateLimiter:
    TIERS = {
        'free': {'requests_per_minute': 100, 'requests_per_hour': 1000},
        'pro': {'requests_per_minute': 10000, 'requests_per_hour': 100000},
        'enterprise': {'requests_per_minute': float('inf'), 'requests_per_hour': float('inf')},
    }

    def __init__(self):
        self.user_buckets = {}

    def get_tier(self, user_id):
        """Get user tier (from database)"""
        # In reality, query user DB
        if user_id in ['alice', 'bob']:
            return 'pro'
        return 'free'

    def check_rate_limit(self, user_id, endpoint):
        """Check if request allowed"""
        tier = self.get_tier(user_id)
        limits = self.TIERS[tier]

        # Simplified: check minute limit
        if limits['requests_per_minute'] == float('inf'):
            return True  # Enterprise: no limit

        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = 0

        if self.user_buckets[user_id] < limits['requests_per_minute']:
            self.user_buckets[user_id] += 1
            return True

        return False

# Usage
limiter = TieredRateLimiter()
if limiter.check_rate_limit('alice', '/api/search'):
    print("Request allowed (pro tier)")
else:
    print("Rate limit exceeded")
```

---

### ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                            |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| "Rate limiting stops all DDoS"  | Incomplete. Protects against volume DDoS. Sophisticated DDoS needs other measures. |
| "Rate limit same for all users" | No. Typically tiered (free, pro, enterprise). Or per-user quota.                   |
| "Always reject if over limit"   | Options: reject (429), queue, or respond with backpressure header.                 |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Rate Limit Too Strict**

**Symptom:**
Legitimate user legitimate spike rejected. User upset.

**Prevention:**
Tiered limits. Allow burst (token bucket). Communicate limits clearly.

---

**Failure Mode 2: Rate Limit Bypassed**

**Symptom:**
Attacker uses multiple IPs to bypass per-IP limit.

**Prevention:**
Enforce per-user ID (not IP). Or combine multiple signals.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-018 - Load Balancing]] - the layer where rate limiting is typically enforced

**Builds On This (learn these next):**
- [[SYD-054 - Token Bucket]] - one algorithm for implementing rate limits
- [[SYD-055 - Leaky Bucket]] - alternative algorithm with different burst characteristics
- [[SYD-064 - Rate Limiter Design]] - end-to-end system design using rate limiting

**Alternatives / Comparisons:**
- [[SYD-054 - Token Bucket]] - implementation algorithm that allows bursts
- [[SYD-055 - Leaky Bucket]] - implementation algorithm that smooths output

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Limit request rate from clients       │
│              │ to prevent overload                    │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Single user can monopolize resources;│
│ SOLVES       │ DDoS attacks                          │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Reject or queue excess requests; use  │
│              │ token/leaky bucket for smoothing      │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Max 100 req/min per user. Exceed?    │
│              │ Get 429. Simple, effective."          │
└──────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Control the rate of work entering a system to protect its capacity. This principle appears everywhere: circuit breakers limit the rate of failure propagation, TCP congestion control limits the rate of packet sending, database connection pools limit the rate of concurrent queries. Every shared resource needs a rate controller, or the fastest client takes all resources.

**Where else this pattern appears:**
- **TCP congestion control:** TCP's AIMD algorithm rate-limits packet sending based on network feedback - a rate limiter for network bandwidth.
- **Database connection pools:** Maximum pool size limits concurrent query rate - preventing one application from exhausting all database connections.
- **Kubernetes resource requests:** CPU requests limit the rate at which pods consume cluster CPU - pod-level rate limiting enforced by the kernel cgroups.

---

### 💡 The Surprising Truth

Rate limiting has a business model dimension that is rarely discussed technically. Stripe, Twilio, and GitHub all use rate limits not primarily as protection mechanisms but as product packaging: the free tier gets 100 requests per minute, the paid tier gets 10,000 requests per minute. The rate limiter is the technical enforcement of the pricing policy. This means rate limiting code is revenue-critical infrastructure - a bug that grants free-tier users paid-tier access directly costs money. Rate limiting systems are tested more carefully than most engineers realise, because a single misconfiguration is a potential revenue loss of significant magnitude.

---

### 🧠 Think About This Before We Continue

**Q1.** Attacker has 100 IPs, each sends 100 req/min. Per-IP limit: 100 req/min (seems safe). How does attacker bypass?

*Hint:* Think about the attacker's perspective: 100 IPs x 100 req/min = 10,000 req/min globally. Does per-IP rate limiting prevent this? Explore what a global rate limit (total requests per minute regardless of source) or account-level rate limit (tied to authenticated identity) would catch that per-IP limits miss.

**Q2.** Legitimate user has traffic spike (3x normal). Rate limit rejects it. How do you handle?

*Hint:* Think about what 3x normal looks like vs the configured limit - is the spike anticipated (a scheduled job, an email campaign going live) or random? Explore whether burst allowance (token bucket capacity), separate limit tiers for trusted clients, or proactive notification (rate limit approaching alert) handles legitimate spikes better than hard rejection.

**Q3 (Design Trade-off):** You implement per-user rate limiting in a distributed API gateway with 5 nodes. Each node independently tracks a user's request count. A user sends 120 req/min across 5 nodes (24 per node). Per-node limit is 100 req/min. The user is never rate limited. Design a fix.

*Hint:* Think about where the per-user state lives: each node has its own counter with no coordination. Explore whether centralising the counter in Redis solves the problem and what the latency and availability implications of that Redis dependency are.
