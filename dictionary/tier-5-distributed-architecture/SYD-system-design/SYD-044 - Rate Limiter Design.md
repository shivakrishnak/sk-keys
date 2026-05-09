---
id: SYD-044
title: Rate Limiter Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-028, SYD-029, SYD-030
used_by: SYD-047, SYD-048
related: SYD-028, SYD-029, SYD-039
tags:
  - architecture
  - security
  - reliability
  - distributed
  - advanced
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /syd/rate-limiter-design/
---

# SYD-044 - Rate Limiter Design

⚡ TL;DR - A rate limiter controls how many requests a client can make in a time window - protecting services from abuse, overload, and DDoS while providing fair resource allocation.

| SYD-044         | Category: System Design        | Difficulty: ★★★ |
| :-------------- | :----------------------------- | :-------------- |
| **Depends on:** | SYD-028, SYD-029, SYD-030     |                 |
| **Used by:**    | SYD-047, SYD-048               |                 |
| **Related:**    | SYD-028, SYD-029, SYD-039     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A single malicious actor sends 1M requests/second to your API. Your service spends all CPU responding to attackers. Legitimate users receive errors or timeouts. The service effectively goes offline - not from a technical failure but from deliberate or accidental overload.

**THE BREAKING POINT:**
APIs are public surfaces. Any authenticated or unauthenticated endpoint can be hammered by a bot, a misbehaving client, or a DDoS attack. Without rate limiting, one bad actor can degrade the entire service for everyone else.

**THE INVENTION MOMENT:**
Track request counts per client per time window in a fast counter store (Redis). On each request, check whether the counter exceeds the limit. If yes, reject with `429 Too Many Requests`. If no, increment and allow.

**EVOLUTION:**
Early rate limiters used fixed-window counters (simple but boundary spikes). Token bucket (Stripe's API) added smoothing. Sliding window algorithms eliminated boundary spikes. Modern rate limiters add: per-endpoint limits, per-tier limits (free vs paid), global cluster-level limits via Redis, and circuit breakers that upgrade to rate limiting under load.

---

### 📘 Textbook Definition

A **rate limiter** is a system component that enforces an upper bound on the number of requests or operations a client can make within a defined time window. Implementations vary by algorithm (fixed window, sliding window, token bucket, leaky bucket) and scope (per-user, per-IP, per-API-key, global). Rate limiters protect backend services from overload and ensure fair resource allocation among clients.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A bouncer who counts how many times you've entered tonight and turns you away if you've exceeded your limit.

**One analogy:**

> A rate limiter is like a turnstile at a subway station with a daily limit. You get N passes per day. Each trip deducts one pass. When you're out, the turnstile blocks you until tomorrow.

**One insight:**
The algorithm choice matters enormously. Fixed window allows 2x the limit in a burst around the window boundary. Sliding window and token bucket avoid this but cost more to implement in a distributed system.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each client must be identifiable (by IP, API key, user ID, or combination).
2. Counters must be atomic - concurrent requests must not both read the same zero counter.
3. The rate limit check must be on the critical path but fast enough not to add significant latency.
4. The rate limiter must be consistent across all service instances (centralized state).

**DERIVED DESIGN:**
Use Redis atomic operations (INCR + EXPIRE for fixed window; ZADD + ZRANGEBYSCORE for sliding window; DECRBY for token bucket). Check counter before allowing request. On limit breach: return 429 with `Retry-After` header. Log limit-hit events for abuse detection.

**THE TRADE-OFFS:**
**Gain:** Protection from overload and abuse; fair resource allocation; billing enforcement.
**Cost:** Extra Redis round trip per request (adds ~1-5ms); rate limit state must be replicated for HA; distributed systems can transiently allow 2x limit if sharded.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Count requests per client per window; reject when over limit.
**Accidental:** Algorithm choice nuances (sliding vs fixed), cluster-wide consensus for limit enforcement, per-route vs global limits.

---

### 🧪 Thought Experiment

**SETUP:** A payment API allows 100 requests/minute per API key. A buggy client sends 10,000 requests in 10 seconds.

**WHAT HAPPENS WITHOUT RATE LIMITING:**
The backend receives 10,000 requests. Each queries the payment DB. DB connection pool exhausts. Legitimate payment requests time out waiting for connections. Even if the buggy client is well-intentioned, the entire payment system goes down.

**WHAT HAPPENS WITH RATE LIMITING:**
Requests 1-100: allowed (within limit for current minute window). Requests 101-10,000: rejected with 429 at the rate limiter layer, before hitting the backend. The backend receives only 100 requests. Legitimate clients continue to function normally. The buggy client receives 429 responses and (if well-written) slows down.

**THE INSIGHT:**
Rate limiting is about protecting shared resources from one actor consuming them all. The rate limiter is a guard at the front door: cheap to check, saves the expensive backend from unnecessary work.

---

### 🧠 Mental Model / Analogy

> A rate limiter is like a sluice gate on a canal. The gate limits flow to prevent downstream flooding regardless of how fast water upstream arrives. The rate (volume per unit time) is controlled, not the total volume.

- **Canal upstream** = incoming requests (any rate)
- **Sluice gate** = rate limiter
- **Controlled flow downstream** = allowed requests (at most N/window)
- **Overflow spill** = 429 rejections
- **Gate setting** = rate limit configuration
- **Multiple gates** = per-user, per-IP, per-endpoint limits

Where this analogy breaks down: a sluice gate queues and delays water; a rate limiter typically rejects (not queues) excess requests immediately to prevent buildup.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
You can only knock on the door 10 times per minute. If you knock more, the door stays closed until the next minute. This prevents someone from knocking 10,000 times and annoying everyone.

**Level 2 - How to use it (junior developer):**
Return 429 with `Retry-After: 60` header when over limit. Always identify the client (API key > user ID > IP address). Implement at the API gateway rather than each service - avoids duplication.

**Level 3 - How it works (mid-level engineer):**
Fixed window: `INCR key; EXPIRE key window_seconds` in Redis (atomic). Sliding window: `ZADD key timestamp; ZREMRANGEBYSCORE key 0 (now-window); ZCARD key` - count of events in last window. Token bucket: store (tokens, last_refill_ts) in Redis; on each request refill tokens based on elapsed time, then deduct 1.

**Level 4 - Why it was designed this way (senior/staff):**
Distributed rate limiting requires all instances to share state. Redis is the standard. But a Redis round trip on every request adds latency. Optimization: local in-process counter with periodic Redis sync (loses precision but saves latency). For highest accuracy with lowest latency: Redis Lua scripts for atomic multi-step operations. For global rate limits across datacenters: Gossip-based distributed counters (trade accuracy for availability). The choice is always accuracy vs latency vs availability.

**Expert Thinking Cues:**
- Ask: "What is your acceptable false positive rate? Some clients blocked who are under limit?"
- Ask: "Should limit breaches result in immediate 429s or graceful degradation (slower service)?"
- Red flag: rate limiter adds > 5ms to p99 latency - move out of critical path
- Red flag: in-memory counters per instance - each instance has 1/N of the true limit

---

### ⚙️ How It Works (Mechanism)

**Fixed window (Redis):**
```
key = f"rl:{user_id}:{window_start_ts}"
count = INCR key
EXPIRE key window_size_seconds
if count > limit: REJECT (429)
else: ALLOW
```

**Sliding window (Redis sorted set):**
```
key = f"rl:{user_id}"
now = current_timestamp_ms
ZADD key now now
ZREMRANGEBYSCORE key 0 (now - window_ms)
count = ZCARD key
if count > limit: REJECT (429)
else: ALLOW
```

**Token bucket (Redis):**
```
key = f"tb:{user_id}"
{tokens, last_ts} = HMGET key tokens last_ts
elapsed = now - last_ts
new_tokens = min(capacity, tokens + elapsed * rate)
if new_tokens < 1: REJECT (429)
SET tokens = new_tokens - 1, last_ts = now
ALLOW
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Request arrives at API gateway]
         |
         v
[Extract client identifier (API key)]  <- YOU ARE HERE
         |
         v
[Redis counter check (Lua atomic script)]
    UNDER LIMIT    |    OVER LIMIT
         |                |
         v                v
[Forward to backend]  [Return 429 + Retry-After]
         |
         v
[Backend processes request]
```

**FAILURE PATH:**
```
[Redis unavailable]
         |
[Rate limiter: fail open or fail closed?]
    Open (allow all)  |  Closed (block all)
         |
[Decision: fail open with logging]
[Alert: rate limiter down, protection off]
```

**WHAT CHANGES AT SCALE:**
At 1M RPS, the Redis rate limit counter becomes a bottleneck. Shard counters by user ID across Redis cluster. Use local token bucket per instance synced to Redis every 100ms. Accept slight over-limit of (instances * local_bucket_size) to save Redis calls.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multiple API gateway instances must share a Redis counter for accurate global limit. Without shared state, each instance allows N requests and the true limit becomes N * instances. Lua scripts ensure atomic read-increment-check. Redis pipeline reduces round trips when checking multiple limits simultaneously.

---

### 💻 Code Example

**BAD - in-memory counter per instance:**
```python
# BAD: each of 10 instances allows 100 req/min
# Total allowed: 1000 req/min = 10x the limit
from collections import defaultdict
import time

counters = defaultdict(int)
windows = {}

def allow_request(user_id: str, limit=100) -> bool:
    now = int(time.time() // 60)  # per-minute window
    key = f"{user_id}:{now}"
    counters[key] += 1           # NOT shared across instances!
    return counters[key] <= limit
```

**GOOD - Redis sliding window with Lua script:**
```python
import redis, time

r = redis.Redis()

SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)

if count < limit then
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, math.ceil(window / 1000))
    return 1  -- allowed
else
    return 0  -- rejected
end
"""

script = r.register_script(SLIDING_WINDOW_SCRIPT)

def allow_request(user_id: str, limit=100,
                  window_ms=60000) -> bool:
    now_ms = int(time.time() * 1000)
    key = f"rl:sliding:{user_id}"
    result = script(
        keys=[key],
        args=[now_ms, window_ms, limit]
    )
    return bool(result)

# In your API handler:
def api_handler(request):
    if not allow_request(request.api_key, limit=100):
        return Response(
            "Too Many Requests",
            status=429,
            headers={"Retry-After": "60"}
        )
    return handle(request)
```

**How to test / verify correctness:**
- Send exactly 100 requests in 1 minute, assert all allowed. Send 101st, assert 429.
- Send 50 requests, wait 60 seconds, send 50 more - assert all 100 allowed (window resets).
- Run 10 concurrent instances, send 200 requests total - assert no more than 100 are allowed.

---

### ⚖️ Comparison Table

| Algorithm      | Implementation | Burst handling | Boundary spike | Memory cost |
| -------------- | -------------- | -------------- | -------------- | ----------- |
| Fixed window   | Simple         | Allows burst   | Yes (2x spike) | O(1)        |
| Sliding window | Moderate       | Smooth         | No             | O(requests) |
| Token bucket   | Moderate       | Controlled burst | No           | O(1)        |
| Leaky bucket   | Moderate       | No burst       | No             | O(1)        |
| Sliding window log | Complex   | Smoothest      | No             | O(requests) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "In-memory rate limiting is fine for single-instance apps" | It works until you scale to 2+ instances. Any horizontal scaling breaks in-memory rate limits without shared state. Use Redis from day one. |
| "Rate limiting only applies to external APIs" | Internal service-to-service calls also need rate limits. A fanout service calling 100 downstream services in a loop can accidentally DDoS your own infrastructure. |
| "429 Too Many Requests means the client is malicious" | A misconfigured or buggy legitimate client is the most common source of rate limit hits. Always include `Retry-After` to guide well-behaved clients to back off. |
| "Rate limiting at the application layer is sufficient" | DDoS attacks can exhaust network bandwidth or connection slots before reaching application-layer rate limiting. Layer 3/4 rate limiting (firewall, CDN) must precede application-layer limits. |
| "All endpoints should have the same limit" | Different endpoints have different costs. A search endpoint may take 100ms; a report export takes 30 seconds. Limits should reflect the cost of the operation, not just the count. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Boundary burst with fixed window**

**Symptom:** Clients send 100 requests at 11:59:55 and 100 more at 12:00:05 - 200 requests in 10 seconds despite a 100/minute limit.

**Root Cause:** Fixed window resets at :00 boundary; a client can use the full limit twice near the boundary.

**Diagnostic:**
```python
# Simulate: 100 req at 59s + 100 req at 61s
# Check if total allowed = 200 (bug) or 100 (correct)
```

**Fix:** Switch to sliding window algorithm. Or use token bucket with burst cap.

**Prevention:** Always use sliding window or token bucket for security-sensitive limits.

---

**Failure Mode 2: Rate limiter overhead on hot path**

**Symptom:** P99 API latency increases by 10ms after adding rate limiter.

**Root Cause:** Synchronous Redis call on every request adds network round trip latency.

**Diagnostic:**
```bash
# Measure Redis latency from application host
redis-cli --latency-history -i 1
# Average should be < 1ms; p99 should be < 3ms
```

**Fix:** Use Redis pipeline (batch multiple commands). Use local token bucket updated periodically from Redis. Move rate limiter to API gateway (off-path from main service).

**Prevention:** Benchmark rate limiter in load testing before production rollout.

---

**Failure Mode 3 (Security): Rate limit bypass via IP rotation**

**Symptom:** Attacker sends 10K requests/minute by rotating through 100 IP addresses, staying under 100/minute per IP.

**Root Cause:** Rate limit keyed on IP only; attacker has a botnet or cloud IP pool.

**Diagnostic:**
```bash
# Check request volume by user agent or payload
# Look for correlated requests despite different IPs
grep "POST /api/login" access.log | awk '{print $1}' \
  | sort | uniq -c | sort -rn | head -20
```

**Fix:** Rate limit by API key, account ID, or behavioral fingerprint in addition to IP. Require authentication for sensitive endpoints (rate limit is then per-account, not per-IP).

**Prevention:** Layer multiple rate limit keys: IP + User-Agent + account fingerprint.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-028 - Rate Limiting (System)]] - the concept; this entry covers the full system design
- [[SYD-029 - Token Bucket]] - the primary algorithm for smooth rate limiting
- [[SYD-030 - Leaky Bucket]] - alternative algorithm for strict rate enforcement

**Builds On This (learn these next):**
- [[SYD-039 - Distributed Locks]] - used in rate limiter critical sections
- [[SYD-047 - Notification System Design]] - applies rate limiting to notification sends

**Alternatives / Comparisons:**
- [[SYD-039 - Distributed Locks]] - heavier alternative for per-user serialization

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Per-client request counter with  │
│              │ reject-on-exceed enforcement     │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Abuse, overload, unfair resource │
│ IT SOLVES    │ consumption by one client        │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Must use shared Redis state;     │
│              │ sliding window avoids boundary   │
│              │ spike of fixed window            │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Any public-facing API; internal  │
│              │ fanout services; billing tiers   │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Limit adds more latency than the │
│              │ call it's protecting             │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Accuracy (sliding) vs simplicity │
│              │ (fixed) vs smoothness (token     │
│              │ bucket)                          │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Redis counter per client per    │
│              │ window; reject when over limit." │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-045 News Feed Design         │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always use shared Redis state - in-memory counters multiply by instance count.
2. Use sliding window or token bucket to avoid fixed-window boundary bursts.
3. Include `Retry-After` header - it guides good clients to back off correctly.

**Interview one-liner:** "A rate limiter counts requests per client in a shared Redis counter with atomic operations - use sliding window or token bucket to avoid boundary bursts, and always return Retry-After on 429."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The guard at the gate is cheaper than the work inside. Rate limiting protects expensive downstream resources by doing minimal work (a counter check) to prevent expensive work (full request processing). Always gate cheap before expensive.

**Where else this pattern appears:**
- **DB connection pools:** Max connections is a rate limit on concurrency, not throughput - protects DB from connection exhaustion.
- **Email sending:** Providers limit outbound emails/second to protect mail delivery reputation.
- **AWS API throttling:** AWS services return 429/ThrottlingException when SDKs call too quickly - the SDK implements exponential backoff as a client-side response.

---

### 💡 The Surprising Truth

A correctly implemented rate limiter can make your service less available to some legitimate clients even with no attack happening. If your limit is 100 requests/minute per user and a legitimate power user legitimately needs 200, they see 429s. The rate limit is a policy decision, not a technical constraint. The real design question is not "how do I implement a rate limiter" but "what is the right limit for each client tier, and how do I communicate and enforce it fairly."

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Your rate limiter uses Redis with a 1ms average latency. Your API p50 response time is 10ms. You add rate limiting to 100K QPS traffic. Suddenly p99 jumps from 20ms to 45ms. What is happening and how do you diagnose it?

*Hint:* At 100K QPS, you're making 100K Redis calls/second. Explore Redis CPU saturation at this rate, then look at pipelining and connection pool sizing to reduce round-trip overhead.

**Q2 (Scale):** You need global rate limiting across 5 geographic regions (us-east, eu-west, ap-south, etc.). A user can have 1000 req/min globally. Putting all counters in one Redis requires cross-region calls (50-150ms). What architecture achieves global limits without cross-region latency on every request?

*Hint:* Explore distributed counter strategies (gossip, periodic sync) that accept some over-limit tolerance in exchange for local latency. Then look at how Cloudflare implements distributed rate limiting across 200+ PoPs.

**Q3 (Design Trade-off):** You rate-limit the login endpoint to 5 attempts/minute per IP to prevent brute force. A corporate office with 5,000 employees behind one NAT IP address legitimately has workers failing login regularly. How do you design a rate limiter that protects against brute force without blocking a corporate NAT?

*Hint:* Consider multi-dimensional rate limiting: low limit per IP (anti-bot), higher limit per account (anti-brute-force from many sources), and CAPTCHA challenges at IP-level thresholds instead of hard blocks.
