---
layout: default
title: "Rate Limiter Design"
parent: "System Design"
nav_order: 39
permalink: /system-design/rate-limiter-design/
number: "SYD-039"
category: System Design
difficulty: ★★★
depends_on: Rate Limiting (System), Token Bucket, Leaky Bucket
used_by: API Gateways, Abuse Prevention, Multi-Tenant Platforms
related: Token Bucket, Leaky Bucket, Capacity Planning
tags:
  - system-design
  - rate-limiting
  - advanced
  - gateway
  - reliability
---

# SYD-039 — Rate Limiter Design

⚡ TL;DR — Rate limiter design turns a concept into a production system: where to enforce limits, which algorithm to use, how to store counters, and how to keep the system fast and correct under distributed traffic.

| #719            | Category: System Design                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Rate Limiting (System), Token Bucket, Leaky Bucket     |                 |
| **Used by:**    | API Gateways, Abuse Prevention, Multi-Tenant Platforms |                 |
| **Related:**    | Token Bucket, Leaky Bucket, Capacity Planning          |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Conceptually knowing rate limiting is not enough. You need a distributed design that is accurate, fast, and resilient.

**SOLUTION:**
Centralize or shard counters, choose an algorithm, and put enforcement close to ingress.

---

### 📘 Textbook Definition

**Rate Limiter Design:** End-to-end system design for enforcing request quotas or throughput limits across distributed clients and services with acceptable latency and correctness guarantees.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store request usage somewhere fast, check it on every request, and reject or delay when over quota.

**One analogy:**

> A stadium turnstile counts entries in real time and stops admitting fans after capacity is reached.

**One insight:**
The limiter itself must not become the bottleneck or single point of failure.

---

### 🧠 Mental Model

```
client -> gateway -> limiter check -> service
                   |
                   -> counter store / local cache
```

---

### 📶 Gradual Depth

**Level 1:** Count requests and block excess.

**Level 2:** Enforce at gateway so bad traffic is stopped early.

**Level 3:** Use local caches for speed, centralized stores for coordination, and eventual or strict consistency depending on business need.

**Level 4:** Good design balances precision, latency, and availability. Perfect global accuracy can cost more than the abuse it prevents.

---

### ⚙️ How It Works

```
Core steps:
1. Extract limiter key (user, API key, IP, tenant)
2. Check token/counter in fast store
3. Allow, reject, or delay request
4. Emit metrics and response headers

Placement options:
- client SDK: advisory only
- service: too late for expensive traffic
- API gateway / edge: usually best

Storage options:
- in-memory local: very fast, not globally accurate
- Redis: common balance
- database: often too slow for hot path
```

---

### 💻 Code Example

```python
def allow_request(redis, key, limit, window_seconds):
    current = redis.incr(key)
    if current == 1:
        redis.expire(key, window_seconds)
    return current <= limit
```

---

### ⚖️ Comparison Table

| Design choice       | Benefit           | Cost                  |
| ------------------- | ----------------- | --------------------- |
| Gateway enforcement | stop abuse early  | extra edge dependency |
| Local counters      | low latency       | inconsistent globally |
| Central counters    | stronger accuracy | network hop           |
| Token bucket        | burst-friendly    | more state math       |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                               |
| -------------------------------------- | --------------------------------------------------------------------- |
| "Just use Redis and you are done"      | You still need key design, eviction policy, HA, and failure behavior. |
| "Limiter must be perfectly consistent" | Often approximate enforcement is acceptable and cheaper.              |

---

### 🚨 Failure Modes

**Failure Mode 1: Limiter outage blocks all traffic**

**Symptom:**
Counter store fails and the whole API becomes unavailable.

**Prevention:**
Decide fail-open vs fail-closed, add fallback budgets, replicate store.

---

**Failure Mode 2: Cardinality explosion**

**Symptom:**
Limiter tracks millions of ephemeral keys and memory usage spikes.

**Prevention:**
TTL, key compaction, per-tier strategy, approximate structures where acceptable.

---

### 📌 Quick Reference

```
Rate limiter design:
  place at edge
  choose key carefully
  pick algorithm for workload
  decide fail-open or fail-closed
  monitor rejects, latency, and store health
```

---

### 🧠 Questions

**Q1.** Should a payment API fail open or fail closed when the limiter backend is down?

**Q2.** What is your limiter key if many users share one NAT IP?
