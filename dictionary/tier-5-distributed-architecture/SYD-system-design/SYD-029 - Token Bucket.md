---
layout: default
title: "Token Bucket"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /system-design/token-bucket/
id: SYD-029
category: System Design
difficulty: ★★★
depends_on: Rate Limiting, Algorithm Design
used_by: API Rate Limiting, Traffic Shaping
related: Leaky Bucket, Rate Limiting
tags:
  - rate-limiting
  - algorithm
  - advanced
  - performance
  - smoothing
---

# SYD-029 - Token Bucket

⚡ TL;DR - Algorithm allowing smooth, bursty traffic by maintaining a bucket of tokens. Requests consume tokens; tokens replenish at a fixed rate. Allows controlled bursts without sustained overload.

| #704            | Category: System Design            | Difficulty: ★★★ |
| :-------------- | :--------------------------------- | :-------------- |
| **Depends on:** | Rate Limiting, Algorithm Design    |                 |
| **Used by:**    | API Rate Limiting, Traffic Shaping |                 |
| **Related:**    | Leaky Bucket, Rate Limiting        |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Fixed window: burst at boundaries. Need smooth rate limiting that allows bursts but prevents sustained overload.

**SOLUTION:**
Token bucket: burst-friendly, predictable, memory-efficient.

---

### 📘 Textbook Definition

**Token Bucket:** Rate limiting algorithm where a bucket accumulates tokens at fixed rate. Each request consumes one token. Bucket has capacity limit. Allows controlled bursts while enforcing average rate.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bucket starts full (100 tokens). Each request = 1 token. Tokens refill at 10/sec. Burst = drain bucket fast; sustained traffic = limited by refill rate.

**One analogy:**

> Movie theater: "Pre-print 100 tickets/day. Customer buys tickets (removes from stack). Reprint 10 tickets/hour." Bursts OK (if tickets available), but sustained tickets limited by reprinting rate.

**One insight:**
Allows short bursts while enforcing long-term rate.

---

### 🧠 Mental Model

Token bucket as physical metaphor:

```
[Bucket with 100 tokens]
  |
  ├─ Request comes: remove 1 token
  ├─ Every 100ms: add 1 token (10/sec)
  ├─ If tokens > 100: drop excess (capacity limit)
  └─ No tokens? Request queued/rejected
```

---

### 📶 Gradual Depth

**Level 1:** Each request needs token. Tokens refill slowly. Burst = fast drain, then wait for refill.

**Level 2:** Capacity (bucket size) determines burst duration. Refill rate determines sustained rate.

**Level 3:** Equation: tokens = min(tokens + refill_rate\*time_elapsed, capacity). Request allowed if tokens >= 1.

**Level 4:** Token bucket emerged from networking (traffic shaping, QoS). Used by AWS, Stripe, Google APIs. Solves burstiness problem: sliding window too strict (rejects legitimate bursts); fixed window allows cheating at boundaries; token bucket balances both.

---

### ⚙️ How It Works

```
Algorithm:
──────────
1. Bucket capacity = 100 tokens
2. Refill rate = 10 tokens/second
3. Last refill time = now

On each request:
  1. Calculate time elapsed since last refill
  2. Add (time_elapsed × refill_rate) tokens to bucket
  3. Cap bucket at capacity
  4. If bucket >= 1 token:
       - Remove 1 token
       - Request ALLOWED
     Else:
       - Request REJECTED or QUEUED

Example timeline:
  00:00 - Bucket = 100 (full)
  00:00.1 - Request 1: 100-1 = 99, ALLOWED
  00:00.2 - Request 2-100: drain bucket (101-199 us into request)
  00:00.2 - Request 101: bucket = 0, REJECTED
  00:01 - 1 second elapsed, refill 10 tokens: bucket = 10
  00:01 - New request: 10-1 = 9, ALLOWED
```

---

### 💻 Code Example

```python
class TokenBucket:
    def __init__(self, capacity, refill_rate_per_sec):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = capacity
        self.last_refill_time = time.time()

    def refill(self):
        now = time.time()
        time_passed = now - self.last_refill_time
        self.tokens = min(self.capacity, self.tokens + self.refill_rate * time_passed)
        self.last_refill_time = now

    def allow_request(self, tokens_needed=1):
        self.refill()
        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False

# Usage: 100 capacity, 10 tokens/sec (avg 10 req/sec, burst 100 req)
bucket = TokenBucket(capacity=100, refill_rate_per_sec=10)

# First 100 requests instant (burst)
for i in range(100):
    assert bucket.allow_request()  # OK

# Request 101: rejected (no tokens)
assert not bucket.allow_request()  # REJECTED

# Wait 10 seconds (100 tokens refilled)
time.sleep(10)

# Another 100 requests OK
for i in range(100):
    assert bucket.allow_request()  # OK
```

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                 |
| ---------------------------------------- | --------------------------------------- |
| "Token bucket allows unlimited burst"    | No. Limited by bucket capacity.         |
| "Token bucket = guaranteed fair sharing" | Incomplete. Still need per-user limits. |

---

### 🚨 Failure Modes

**Failure Mode: Token Accumulation Overload**

**Symptom:**
Inactive user's bucket fills to max. When active, they burst with queued tokens (unfair).

**Prevention:**
Reset bucket on user reactivation, or limit burst fraction of capacity.

---

### 📌 Quick Reference

```
Token Bucket Summary:
  Capacity: max burst size
  Refill rate: sustained rate
  Allows: smooth traffic, controlled bursts
  Trade-off: simple, but allows one large burst per period
```

---

### 🧠 Questions

**Q1.** Capacity=100, refill=10/sec. User bursts 50 requests/sec for 2 sec. What happens?

**Q2.** How would you prevent token hoarding (saving up tokens for huge burst later)?
