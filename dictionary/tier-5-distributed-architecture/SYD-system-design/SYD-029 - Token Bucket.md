---
id: SYD-029
title: Token Bucket
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-028
used_by: SYD-044
related: SYD-028, SYD-030, SYD-044
tags:
  - rate-limiting
  - algorithm
  - advanced
  - performance
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /syd/token-bucket/
---

# SYD-029 - Token Bucket

⚡ TL;DR - Rate limiting algorithm where tokens accumulate at a fixed rate up to a capacity; each request consumes one token, allowing controlled bursts while enforcing an average rate.

| SYD-029         | Category: System Design   | Difficulty: ★★★ |
| :-------------- | :------------------------ | :-------------- |
| **Depends on:** | SYD-028                   |                 |
| **Used by:**    | SYD-044                   |                 |
| **Related:**    | SYD-028, SYD-030, SYD-044 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to rate limit an API to 10 requests/second per user. The naive approach: a fixed window counter that resets every second. Problem: a user can fire 10 requests at 00:00.999 and another 10 at 00:01.001 - delivering 20 requests in 2 milliseconds, perfectly within the rules but completely violating the spirit of the limit. The fixed window has a predictable exploit at every boundary.

**THE BREAKING POINT:**
Fixed windows allow boundary bursts. Sliding windows fix the boundary problem but are memory-intensive (must store timestamps for every request). What is needed is an algorithm that allows natural, legitimate bursts (a user sends 5 requests quickly then pauses) while preventing sustained overload - without storing per-request timestamps.

**THE INVENTION MOMENT:**
The token bucket algorithm was originally designed for network packet scheduling in the 1980s. Engineers observed that the right abstraction for bursty traffic is a bucket that accumulates "permission tokens" over time. Each token permits one action. The bucket fills at a steady rate and may hold a maximum number of tokens. Bursts are allowed (drain the bucket quickly) but sustained rates are bounded (limited by refill rate).

**EVOLUTION:**
Token bucket was standardised in networking as part of ATM and IP QoS specifications. Amazon, Stripe, and Google Application APIs popularised it for HTTP rate limiting in the 2010s. Today it is the dominant algorithm for API rate limiting, implemented in API gateways, service meshes, and distributed systems.

---

### 📘 Textbook Definition

The **token bucket** is a rate limiting algorithm where a bucket holds a maximum of `capacity` tokens. Tokens are added at a fixed `rate` (tokens/second). Each incoming request consumes one token. If tokens are available, the request is allowed and one token is removed. If no tokens are available, the request is rejected or queued. The bucket enforces an *average rate* equal to the refill rate and a *burst size* equal to the capacity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A bucket fills with permission tokens at a fixed rate; each request spends one token; empty bucket means rejected request.

**One analogy:**
> A prepaid calling card. It starts with 100 minutes. You can use all 100 minutes in one call (burst), but the card only recharges at 10 minutes per hour. You can make long calls, but sustained calling is limited by the recharge rate.

**One insight:**
Token bucket does not smooth traffic - it permits legitimate bursts while enforcing a long-term average rate. This is the right trade-off for most interactive API use cases.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Sustained throughput cannot exceed the refill rate - over any window long enough to deplete the bucket, the average rate is bounded by the refill rate.
2. Short bursts up to the bucket capacity are always allowed - the burst headroom is the accumulated token surplus.
3. State required is constant: just the current token count and last refill timestamp - O(1) per user.
4. Refill and consume are the only two operations - the algorithm is trivially stateless per-user.

**DERIVED DESIGN:**
Two parameters determine all behaviour: `capacity` (maximum burst size) and `rate` (sustained request rate). Setting capacity = rate makes it behave like a strict per-second window. Setting capacity >> rate allows extended bursts.

**THE TRADE-OFFS:**
**Gain:** Allows legitimate bursts, memory-efficient (O(1) per user), fast (O(1) per request), prevents sustained overload.
**Cost:** Does not smooth downstream traffic - two buckets draining simultaneously create spikes. Burst capacity can be abused if capacity is set too high.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Rate limiting inherently requires tracking time-relative state per client.
**Accidental:** Distributed implementations (Redis-based) add lock contention; this is not inherent to the algorithm but to its distribution.

---

### 🧪 Thought Experiment

**SETUP:**
An API has a token bucket rate limiter: capacity = 10, refill = 2 tokens/second. User A is interactive (sends bursts while actively working). User B is a bot (sends at a perfectly steady 3 req/sec).

**WHAT HAPPENS WITHOUT TOKEN BUCKET (fixed window):**
User A fires 10 requests at 00:00.1 (burst of legitimate work) → all allowed. Then pauses. User B fires 3 requests at 00:00.0, 3 at 00:01.0, 3 at 00:02.0 → all allowed. But at window boundary, User B can also spike to 10+10=20 in 2ms. Both users look identical to the fied window rule. Boundary exploitation is undetectable.

**WHAT HAPPENS WITH TOKEN BUCKET:**
User A: bucket starts at 10, fires 10 requests → bucket empties, all allowed, then refills at 2/sec. User A's subsequent requests are throttled to 2/sec, naturally matching human typing speed. User B: starts at 10, fires 3/sec → bucket depletes in ~0.5 sec, then sustainable at 2/sec. User B gets throttled because 3/sec > 2/sec refill. The sustained bot is correctly limited; the interactive burst is correctly allowed.

**THE INSIGHT:**
Token bucket correctly penalises sustained over-rate users while rewarding users who save up tokens through normal usage patterns. This is the correct fairness model for interactive APIs.

---

### 🧠 Mental Model / Analogy

> Token bucket is like a punch card at a bakery. The card has 10 punches. Buying any pastry uses a punch. The bakery adds one new punch to your card every 6 minutes. You can buy 10 pastries at once if you have saved up punches. But you cannot buy at a rate faster than one every 6 minutes indefinitely.

**Mapping:**
- Punch card → token bucket
- Punches remaining → current token count
- Card capacity → bucket capacity
- New punch every 6 min → token refill rate
- Buying a pastry → making an API request
- Card full (no new punches) → bucket at capacity, tokens not wasted

Where this analogy breaks down: punch cards are physical and discrete; token bucket implementations often use fractional tokens and floating-point arithmetic for sub-second granularity.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Imagine a jar that can hold 10 marbles. Every second someone adds 1 marble. When you make a request, you take a marble. If the jar is empty, your request is rejected. If you were patient and the jar filled up, you can take 10 marbles at once (burst). But you cannot keep taking more than 1 per second on average.

**Level 2 - How to use it (junior developer):**
Configure two parameters: `capacity` (max burst) and `rate` (per-second refill). Store `(token_count, last_refill_timestamp)` per user in Redis. On each request: calculate tokens added since last refill (`elapsed_seconds * rate`), cap at capacity, check if remaining >= 1, decrement if so. Redis atomic operations (MULTI/EXEC or Lua scripts) ensure thread safety.

**Level 3 - How it works (mid-level engineer):**
Token state updates are lazy (computed on demand rather than maintained in a background process): tokens = min(capacity, stored_tokens + (now - last_refill) * rate). This avoids any background job or timer - the bucket is computed from timestamps on each request. The key insight is that token count is a continuous function of time, discretised only when consumed. Race conditions in distributed systems are handled via atomic compare-and-swap or Lua scripts in Redis.

**Level 4 - Why it was designed this way (senior/staff):**
Token bucket was designed for network packet scheduling where the scheduling decision is time-critical and the implementation is in hardware. The lazy evaluation property (recompute tokens on demand from elapsed time) was critical - it avoids background jobs and makes the algorithm stateless beyond two numbers per client. The algorithm is also composable: you can have both a per-user bucket and a global bucket, requiring tokens from both. Stripe uses this for API rate limiting: global burst + per-user sustained rate.

**Expert Thinking Cues:**
- "What is the maximum burst my downstream systems can absorb? That sets capacity."
- "What is my target sustained per-user rate? That sets the refill rate."
- "Is my rate limiter in-process (fast, not distributed) or Redis-based (distributed, atomic)?"
- "What happens to the bucket state when a user is idle for 24 hours? (Token hoarding problem)"

---

### ⚙️ How It Works (Mechanism)

```
TOKEN BUCKET ALGORITHM
══════════════════════

State per client:
  tokens: float     (current token count)
  last_refill: time (timestamp of last update)

On request arrival:
  1. elapsed = now - last_refill
  2. tokens = min(capacity,
                  tokens + elapsed * rate)
  3. last_refill = now
  4. if tokens >= 1:
       tokens -= 1
       return ALLOW
     else:
       return DENY

Timeline (capacity=10, rate=2/sec):
  t=0:   bucket=10 (full)
  t=0:   10 requests arrive → all allowed
         bucket=0
  t=0.5: elapsed=0.5s → +1 token → bucket=1
         1 request arrives → allowed, bucket=0
  t=1.0: elapsed=0.5s → +1 token → bucket=1
  t=5.0: elapsed=4.0s → +8 tokens → bucket=8
         (capped at 10 even at t=10)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Incoming API Request
        │
        ▼
Rate Limiter (Gateway)    ← YOU ARE HERE
        │
        ▼
Load token state from Redis
(user_id → {tokens, last_refill})
        │
        ▼
Recalculate: add elapsed tokens
cap at capacity
        │
   tokens >= 1?
   ┌──────┴──────┐
  YES            NO
   │              │
   ▼              ▼
Decrement,    Return 429
forward req   Too Many Requests
```

**FAILURE PATH:**
Redis unavailable → rate limiter cannot load state → choose: allow all (availability-first) or deny all (safety-first). Stripe allows all during Redis outage; critical financial APIs deny all. This decision must be made explicitly at design time.

**WHAT CHANGES AT SCALE:**
At scale, a single Redis node becomes a bottleneck. Options: Redis Cluster (consistent hashing of users to nodes), local rate limiter with eventual synchronisation (slight over-admission), or approximate counting (HyperLogLog-based approximate token counts).

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Concurrent requests from the same user must not both read a non-empty bucket, decrement simultaneously, and both be allowed. The atomic check-and-decrement pattern - either Redis MULTI/EXEC or a Lua script - is required. Without atomicity, race conditions allow 2x or more the configured rate.

---

### 💻 Code Example

```python
import time
import redis

# BAD: Non-atomic read-modify-write allows race conditions
class BrokenTokenBucket:
    def allow_request(self, user_id):
        tokens = int(r.get(f"tokens:{user_id}") or 0)
        if tokens > 0:
            # RACE: another thread may read same value
            r.set(f"tokens:{user_id}", tokens - 1)
            return True
        return False

# GOOD: Atomic Lua script ensures correctness
ALLOW_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local data = redis.call('HMGET', key,
                         'tokens', 'last_refill')
local tokens = tonumber(data[1]) or capacity
local last = tonumber(data[2]) or now

local elapsed = now - last
local refilled = math.min(capacity,
                  tokens + elapsed * rate)

if refilled >= 1 then
    redis.call('HMSET', key,
      'tokens', refilled - 1, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return 1
else
    redis.call('HMSET', key,
      'tokens', refilled, 'last_refill', now)
    return 0
end
"""

class TokenBucket:
    def __init__(self, redis_client,
                 capacity=10, rate=2.0):
        self.r = redis_client
        self.capacity = capacity
        self.rate = rate    # tokens per second
        self._script = self.r.register_script(
            ALLOW_SCRIPT)

    def is_allowed(self, user_id: str) -> bool:
        key = f"rate:{user_id}"
        result = self._script(
            keys=[key],
            args=[self.capacity, self.rate,
                  time.time()])
        return bool(result)
```

**How to test / verify correctness:**
- Burst test: fire `capacity` requests simultaneously; all should be allowed; the next should be rejected.
- Steady-state test: fire at exactly `rate` req/sec; all should be allowed indefinitely.
- Over-rate test: fire at 2x `rate` for 10 seconds; ~50% should be rejected.
- Concurrency test: 10 parallel threads firing simultaneously; verify total allowed equals exactly `capacity`.

---

### ⚖️ Comparison Table

| Algorithm | Burst Allowed | Memory | Smoothing | Best For |
|---|---|---|---|---|
| **Token Bucket** | Yes (up to capacity) | O(1) per user | No (bursts pass through) | API rate limiting |
| **Leaky Bucket** | No (queued) | O(N) queue | Yes (constant output rate) | Network traffic shaping |
| **Fixed Window** | Yes (boundary burst) | O(1) | No | Simple counters |
| **Sliding Window** | Partial | O(requests) | Partial | Accurate rate limiting |
| **Sliding Window Log** | No | O(requests) | Yes | Strict per-user auditing |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Token bucket = leaky bucket" | Different algorithms. Token bucket allows bursts freely; leaky bucket queues all requests and outputs at a constant rate. |
| "Capacity = requests per second" | Capacity controls burst size; rate controls sustained throughput. They are independent parameters. |
| "Token bucket guarantees fairness" | Without per-user buckets, a single high-traffic user depletes a shared bucket. Always implement per-user buckets. |
| "Local token bucket is good enough" | In distributed systems, each node has its own bucket - total admission is `capacity × nodes`. Need distributed state. |
| "Idle users accumulate infinite tokens" | Tokens cap at capacity - idle periods do not grant super-burst privileges beyond the capacity ceiling. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Token Hoarding Attack**
**Symptom:** A user makes no requests for 1 hour, then fires 10,000 requests in 1 second.
**Root Cause:** Capacity is too high relative to the system's burst tolerance.
**Diagnostic:**
```bash
# Check maximum bucket capacity in config
grep "bucket.capacity" /etc/api-gateway/rate-limit.yml
# Monitor request bursts per user in Prometheus
max_over_time(api_requests_total[1m])
```
**Fix:** Reduce capacity to the burst size the downstream system can absorb. Consider also capping burst to `rate * 60` (one minute's worth of tokens maximum).
**Prevention:** Set capacity = expected_legitimate_burst, not theoretical maximum.

**Mode 2: Race Condition in Distributed Token Bucket**
**Symptom:** Rate-limited endpoint admits 2x the configured rate under concurrent load.
**Root Cause:** Non-atomic read-modify-write: two threads both read `tokens=1`, both decrement to 0, both admit requests.
**Diagnostic:**
```bash
# Load test with concurrent requests
hey -n 1000 -c 100 http://api/endpoint
# Count admitted vs expected
```
**Fix:** Use a Redis Lua script (atomic) or Redis MULTI/EXEC for the check-and-decrement operation.
**Prevention:** Always use atomic operations for distributed token state. Test under concurrency, not just serial load.

**Mode 3: Redis Unavailability - Wrong Default**
**Symptom:** Redis goes down; rate limiter fails open, admitting all traffic; downstream service is overwhelmed.
**Root Cause:** Default behavior on Redis failure is "allow" with no circuit breaker on downstream.
**Diagnostic:**
```bash
# Check Redis connection health
redis-cli ping  # Should return PONG
# Check fallback policy in gateway config
grep "fallback" /etc/gateway/rate-limit.conf
```
**Fix:** Implement a local in-process fallback token bucket with more conservative limits during Redis outages.
**Prevention:** Define and document the fail-open vs fail-closed policy explicitly at design time.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-028 - Rate Limiting (System)]] - The broader problem that token bucket solves
- [[SYD-004 - Estimation and Back-of-Envelope Thinking]] - Estimating the right capacity and rate values

**Builds On This (learn these next):**
- [[SYD-030 - Leaky Bucket]] - The alternative algorithm with different burst characteristics
- [[SYD-044 - Rate Limiter Design]] - End-to-end system design using token bucket

**Alternatives / Comparisons:**
- [[SYD-030 - Leaky Bucket]] - Queued output vs allowed bursts
- [[SYD-028 - Rate Limiting (System)]] - The problem class this solves

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Rate limiting algorithm     ║
║               with burst allowance        ║
╠══════════════════════════════════════════╣
║ PROBLEM       Fixed windows allow         ║
║ IT SOLVES     boundary bursts             ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   capacity = burst tolerance; ║
║               rate = sustained limit      ║
╠══════════════════════════════════════════╣
║ USE WHEN      API rate limiting; allow    ║
║               interactive bursts          ║
╠══════════════════════════════════════════╣
║ AVOID WHEN    Need perfectly smooth       ║
║               downstream traffic          ║
╠══════════════════════════════════════════╣
║ TRADE-OFF     Burstability vs smoothing;  ║
║               simplicity vs fairness      ║
╠══════════════════════════════════════════╣
║ ONE-LINER     tokens = min(cap,           ║
║               tokens + elapsed*rate)      ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-030: Leaky Bucket       ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Capacity controls burst size; rate controls sustained throughput - they are independent.
2. Always use atomic operations (Redis Lua) for distributed token buckets or you get 2x admission under concurrency.
3. Token bucket is the right default for API rate limiting; leaky bucket is the right choice for smooth network traffic output.

**Interview one-liner:**
"Token bucket maintains a counter of tokens that refill at a fixed rate up to a capacity; each request consumes a token; capacity controls burst and rate controls sustained throughput."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate burst tolerance from sustained rate. Every resource limit has two dimensions: the burst the system can absorb over a short window, and the sustained rate it can handle over a long window. Systems that conflate the two either block legitimate bursts (too strict) or allow sustained overload (too lenient). Token bucket separates these concerns explicitly.

**Where else this pattern appears:**
- **Retry budgets:** Exponential backoff with jitter is a token bucket analogy - you accumulate "retry permission" over time and spend it on retries.
- **Cloud API quotas:** AWS IAM, Google Cloud APIs, and Azure all use token-bucket-style burst+sustained quotas.
- **CPU scheduling (CFS):** Linux CFS scheduler uses a token-like "virtual runtime" concept to balance burst and sustained CPU fairness.

---

### 💡 The Surprising Truth

The token bucket and leaky bucket algorithms were originally designed for ATM (Asynchronous Transfer Mode) network cells in the 1980s - not for HTTP APIs. The ATM standard used token bucket for policing (admission control) and leaky bucket for shaping (smoothing output). HTTP API rate limiting co-opted the same mathematics decades later, but with a key difference: HTTP requests have wildly variable sizes, while ATM cells are fixed 53 bytes. This mismatch means that weighting token bucket requests by their actual cost (tokens_required proportional to response size) is correct but rarely implemented.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** You have a token bucket with capacity=100, rate=10/sec per user. Your downstream database can handle 1,000 req/sec total. You have 200 active users. What is the maximum load your database can receive, and is the token bucket sufficient to protect it?
*Hint:* Calculate the maximum simultaneous burst across all 200 users, then the maximum sustained rate - explore whether per-user limits provide system-level protection or whether you need a global token bucket as well.

**Q2 (Scale):** You deploy your Redis-backed token bucket across 50 API gateway nodes. Each node has its own Redis connection. What happens when a user sends requests to 10 different nodes simultaneously?
*Hint:* Think about where the per-user state lives and whether all nodes are reading from the same source of truth - explore the difference between centralised state (Redis) and the network round-trip cost per request.

**Q3 (Design Trade-off):** You are designing an API for a payment processor. Should you use a token bucket (which allows bursts) or a leaky bucket (which queues requests)? What specific properties of payment processing drive this choice?
*Hint:* Think about the latency implications of queuing in a payment flow, the blast radius of a burst hitting your payment provider, and whether burst-then-wait is acceptable in a real-time financial context.

