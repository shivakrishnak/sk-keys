---
layout: default
title: "Leaky Bucket"
parent: "System Design"
nav_order: 705
permalink: /system-design/leaky-bucket/
number: "705"
category: System Design
difficulty: ★★★
depends_on: "Rate Limiting (System), Token Bucket"
used_by: "Rate Limiting (System), API Gateway"
tags: #advanced, #distributed, #architecture, #performance, #networking
---

# 705 — Leaky Bucket

`#advanced` `#distributed` `#architecture` `#performance` `#networking`

⚡ TL;DR — **Leaky Bucket** is a rate limiting algorithm where requests queue in a "bucket" that drains at a constant rate — bursts are absorbed in the queue, and output is always a smooth, constant stream regardless of input variation.

| #705            | Category: System Design              | Difficulty: ★★★ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Rate Limiting (System), Token Bucket |                 |
| **Used by:**    | Rate Limiting (System), API Gateway  |                 |

---

### 📘 Textbook Definition

**Leaky Bucket** is a rate limiting and traffic shaping algorithm that models requests as water flowing into a bucket with a hole at the bottom. Requests enter the bucket (queue) at any rate; the bucket leaks (processes requests) at a constant rate R. If the bucket is full (queue at capacity B), incoming requests overflow (are dropped). Unlike Token Bucket (which allows bursts to pass through), Leaky Bucket enforces a strictly constant output rate — all bursts are smoothed out. There are two interpretations: (1) **Leaky Bucket as a meter**: measures conformance of a traffic stream; (2) **Leaky Bucket as a queue**: shapes traffic by queuing and releasing at constant rate. The algorithm is foundational in network traffic policing (ATM networks, QoS), and is used in APIs where a strictly constant downstream rate is required.

---

### 🟢 Simple Definition (Easy)

Leaky Bucket: water (requests) pours in at any rate, drips out at a fixed rate (1 drop per second). If too much water pours in, the bucket overflows (requests rejected). What comes out is always a steady drip — never a flood. Contrast with Token Bucket: Token Bucket stores saved-up water for a burst; Leaky Bucket just drains at a constant rate no matter what.

---

### 🔵 Simple Definition (Elaborated)

You have an API that can handle exactly 100 requests/second to a downstream database. With Leaky Bucket: even if 1,000 requests arrive in 1 second, only 100/second flow through to the database (the rest queue up). The database always sees exactly 100 req/second — never 1,000. Token Bucket: the database might see 500 req/second (burst) then 50 req/second (refill). Leaky Bucket: always exactly 100. This is critical for network equipment, streaming systems, and any backend that cannot handle any bursts.

---

### 🔩 First Principles Explanation

**Leaky Bucket vs Token Bucket — detailed comparison:**

````
LEAKY BUCKET MECHANICS:

  State:
  - queue: FIFO queue of pending requests
  - capacity: maximum queue size (B)
  - leak_rate: requests processed per second (R)
  - last_leak: timestamp of last processing

  On request arrival:
    if queue.size() < capacity:
      queue.add(request)     // buffered
    else:
      DROP request           // overflow

  Background worker (or lazy evaluation):
    At constant interval (1/R seconds):
      if queue is not empty:
        process queue.poll()  // one request per interval

  Key guarantee: output rate = EXACTLY R (when backlogged)
                 Input rate can be anything up to capacity/second.

TOKEN BUCKET vs LEAKY BUCKET (fundamental difference):

  TOKEN BUCKET:
    ┌────────────────────────────────────────────────┐
    │ Input: burst of 500 requests at T=0            │
    │ Bucket: 500 tokens available                   │
    │ Output: 500 requests processed instantly (T=0) │
    │ Then: refill at 100/sec                        │
    │ Result: backend sees 500 QPS spike at T=0      │
    └────────────────────────────────────────────────┘
    Burst passes through to backend.

  LEAKY BUCKET:
    ┌────────────────────────────────────────────────┐
    │ Input: burst of 500 requests at T=0            │
    │ Queue: 500 requests queued (if capacity ≥ 500) │
    │ Output: 100 requests per second (constant)     │
    │ T=0:  100 processed                            │
    │ T=1:  100 processed                            │
    │ T=4:  last 100 processed, queue empty          │
    │ Result: backend always sees exactly 100 QPS    │
    └────────────────────────────────────────────────┘
    Burst absorbed by queue, smoothed to constant rate.

OVERFLOW BEHAVIOUR:

  Case A: Queue = 1000, rate = 100/sec, burst = 2000 requests
    - 1000 requests: queued (fills queue)
    - 1000 requests: DROPPED (queue full — overflow)
    - Processing: 100/sec drain for 10 seconds

  Case B: Low queue, high burst
    Queue = 100, rate = 100/sec, burst = 500
    - 100 requests: queued
    - 400 requests: DROPPED immediately
    - Users see: 400 immediate rejections + 100 processed over 1 second
    - This is problematic: legitimate requests dropped with no retry

  IMPORTANT: Leaky Bucket does NOT guarantee fairness between clients.
  First-come-first-served. A burst of low-priority requests can fill the queue
  before high-priority requests arrive → high-priority requests dropped.
  Solution: Multiple leaky buckets (one per priority class) or fair queuing.

LAZY EVALUATION (no background timer for implementation):

  Instead of a background timer draining the queue, implement as rate check:

  On each incoming request:
    1. Calculate: how many requests should have leaked since last_leak?
       leaked = floor((now - last_leak) × leak_rate)
    2. "Remove" leaked requests from queue (just update count):
       queue_size = max(0, queue_size - leaked)
    3. Update last_leak = last_leak + (leaked / leak_rate)
    4. If queue_size < capacity:
       queue_size += 1; allow request
    Else:
       drop request
    5. Schedule actual processing at constant rate (or use approximation for metrics)

  This is stateless and works well for Redis-based distributed implementations.
  (Similar to Token Bucket lazy refill pattern)

PRACTICAL IMPLEMENTATIONS:

  1. NGINX rate limiting uses Leaky Bucket:
     ```nginx
     limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
     location /api/ {
       limit_req zone=api burst=20 nodelay;
       # rate=10r/s → leak rate = 10/sec
       # burst=20 → queue capacity = 20
       # nodelay: burst requests processed immediately (not queued)
       #   (NGINX burst=nodelay is actually Token Bucket behaviour!)
     }
     ```
     NOTE: NGINX without 'nodelay' = true Leaky Bucket (queued, delayed output).
           NGINX with 'nodelay' = effectively Token Bucket (burst allowed instantly).

  2. AWS API Gateway uses Token Bucket (not Leaky):
     rateLimit = sustained rate, burstLimit = burst capacity.

  3. Network routers (QoS): true Leaky Bucket for traffic shaping.
````

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Leaky Bucket (using Token Bucket for network QoS):

- Network traffic shaped with Token Bucket: downstream link sees bursty traffic
- Bursty traffic: causes jitter in latency (bad for voice/video)
- Downstream QoS requirements violated by burst passthrough

WITH Leaky Bucket:
→ Perfectly constant output rate: no bursts downstream
→ Jitter eliminated: latency is predictable (critical for streaming/VoIP)
→ Downstream system protected from any burst, regardless of input pattern

---

### 🧠 Mental Model / Analogy

> Water pours into a bucket that has a small hole at the bottom. No matter how fast water is poured in (a brief flood, a steady stream, or intermittent drops), the water drips out through the hole at exactly the same constant rate. If the bucket overflows (too much water, too fast), the excess spills over the sides and is lost. The output is always the same drip — a metronome of water.

"Water pouring into bucket" = incoming requests (any rate, bursty or steady)
"Bucket capacity" = maximum queue size (excess beyond this is dropped)
"Hole at bottom" = leak rate R (constant request processing rate)
"Water dripping from hole" = processed requests (constant output regardless of input)
"Bucket overflows" = requests dropped (429 or discard) when queue at capacity

---

### ⚙️ How It Works (Mechanism)

**NGINX: Leaky Bucket rate limiting in practice:**

```nginx
# /etc/nginx/nginx.conf

http {
    # Define rate limit zone:
    # - $binary_remote_addr: key per client IP (4 bytes compressed)
    # - zone=api_limit:10m: store state in 10MB shared memory zone
    # - rate=100r/s: leak rate = 100 requests/second per IP
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;

    server {
        location /api/ {
            # Apply Leaky Bucket rate limiting:
            # - zone=api_limit: use defined zone
            # - burst=200: queue capacity = 200 requests
            # - (no nodelay): requests queue and are delayed to match rate
            limit_req zone=api_limit burst=200;

            # Return 429 (not default 503) on overflow:
            limit_req_status 429;

            proxy_pass http://backend;
        }

        location /api/search {
            # Stricter limit for expensive search:
            limit_req_zone $binary_remote_addr zone=search_limit:10m rate=10r/s;
            limit_req zone=search_limit burst=5;
            limit_req_status 429;

            proxy_pass http://backend;
        }
    }
}
```

**Java: Leaky Bucket implementation with lazy evaluation:**

```java
public class LeakyBucket {
    private final double leakRatePerSec;  // requests per second output
    private final int capacity;            // max queue size
    private double queueSize;             // current pending request count
    private long lastLeakNanos;           // last leak timestamp

    public LeakyBucket(double leakRatePerSec, int capacity) {
        this.leakRatePerSec = leakRatePerSec;
        this.capacity = capacity;
        this.queueSize = 0;
        this.lastLeakNanos = System.nanoTime();
    }

    public synchronized boolean tryAdd() {
        leak(); // drain queue based on elapsed time

        if (queueSize < capacity) {
            queueSize++;
            return true;  // request accepted (will be processed at constant rate)
        }
        return false;     // queue full: request dropped
    }

    private void leak() {
        long now = System.nanoTime();
        double elapsedSeconds = (now - lastLeakNanos) / 1_000_000_000.0;
        double leaked = elapsedSeconds * leakRatePerSec;
        queueSize = Math.max(0, queueSize - leaked);
        lastLeakNanos = now;
    }

    public double getQueueSize() {
        leak();
        return queueSize;
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Incoming Requests (any rate, bursty)
        │
        ▼
Leaky Bucket Queue ◄──── (you are here)
(absorbs burst in queue, drops overflow)
        │
        ▼ (constant rate R)
Rate Limiting (System)
        │
        ├── Token Bucket (contrast: allows bursts through vs smooths them)
        └── API Gateway (NGINX, HAProxy implement Leaky Bucket natively)
```

---

### 💻 Code Example

**Comparison demo: Token Bucket vs Leaky Bucket behaviour under burst:**

```python
import time

class TokenBucket:
    def __init__(self, capacity, fill_rate):
        self.tokens = capacity
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.last_time = time.time()

    def allow(self):
        now = time.time()
        self.tokens = min(self.capacity,
                         self.tokens + (now - self.last_time) * self.fill_rate)
        self.last_time = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

class LeakyBucket:
    def __init__(self, capacity, leak_rate):
        self.queue_size = 0
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.last_time = time.time()

    def allow(self):
        now = time.time()
        elapsed = now - self.last_time
        self.queue_size = max(0, self.queue_size - elapsed * self.leak_rate)
        self.last_time = now
        if self.queue_size < self.capacity:
            self.queue_size += 1
            return True
        return False

# Both: rate=100/sec, capacity=500
tb = TokenBucket(500, 100)
lb = LeakyBucket(500, 100)

# Simulate: idle for 5 seconds, then 600 burst requests
time.sleep(5)  # tokens accumulate to 500

tb_allowed = sum(1 for _ in range(600) if tb.allow())
lb_allowed = sum(1 for _ in range(600) if lb.allow())

print(f"Token Bucket: {tb_allowed}/600 allowed instantly")  # 500 (burst passes through)
print(f"Leaky Bucket: {lb_allowed}/600 allowed")            # 500 (queued, 100 dropped)
# Key difference: Token Bucket allows 500 instantly;
#                 Leaky Bucket queues 500, drains at 100/sec over 5 seconds
```

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Leaky Bucket and Token Bucket have identical throughput | They have identical average throughput (both cap at R req/sec sustained). The key difference is burst handling: Token Bucket passes bursts through instantly (up to bucket capacity); Leaky Bucket queues bursts and always outputs at constant rate R. Use Leaky Bucket when downstream must never see a burst                   |
| NGINX `limit_req burst=N` is Leaky Bucket               | Without `nodelay`: NGINX uses true Leaky Bucket — burst requests are queued and delayed to maintain constant rate. WITH `nodelay`: burst requests are processed immediately (no delay) — this is effectively Token Bucket behaviour. The `nodelay` keyword fundamentally changes the algorithm                                    |
| Leaky Bucket is better than Token Bucket                | Neither is universally better. Token Bucket is better for user-facing APIs (humans burst, should get fast responses). Leaky Bucket is better for downstream service protection (database, 3rd party APIs where constant rate is critical). Choose based on whether the goal is protecting upstream clients or downstream services |
| Larger queue capacity means better performance          | Larger queue = more requests absorbed before dropping, but: (1) increased latency for queued requests (a full queue of 10,000 at 100/sec = 100-second wait), (2) more memory used, (3) stale requests may be processed long after the user has timed out. Queue capacity should be sized so max wait time ≤ client timeout        |

---

### 🔥 Pitfalls in Production

**Leaky Bucket queue causes request timeout before processing:**

```
PROBLEM: Queue too large → requests processed after client timeout

  Configuration:
    Leak rate: 100 req/sec
    Queue capacity: 10,000 requests
    Client timeout: 5 seconds

  Scenario: burst of 10,000 requests at T=0
    10,000 requests: all queued (queue fills completely)
    Processing: 100/sec → last request processed at T=100s

  Client timeout = 5 seconds:
    Requests queued after position 500: processed at T > 5 seconds.
    9,500 requests: processed AFTER client already timed out.

  Result:
    - Client: received timeout (gave up)
    - Server: still processing 9,500 stale requests (wasting resources)
    - Backend database: 9,500 unnecessary queries for no-longer-waiting clients

CORRECT APPROACH: Queue capacity = leak_rate × acceptable_wait_seconds

  Acceptable wait: 2 seconds (before client timeout of 5s — with safety margin)
  Max queue: 100 × 2 = 200 requests

  With burst of 10,000:
    200 requests: queued and processed within 2 seconds ✓
    9,800 requests: immediately dropped (429) ← clients retry quickly

  Better for clients: immediate 429 → client can retry or fail fast
  vs. stale processing: client times out AND server wastes work

  Configure:
    # NGINX with short burst limit:
    limit_req zone=api_limit burst=200;  # not 10000
    # burst = leak_rate × max_acceptable_delay_seconds
```

---

### 🔗 Related Keywords

- `Token Bucket` — complementary algorithm: burst-friendly (bursts pass through) vs Leaky Bucket (bursts queued/smoothed)
- `Rate Limiting (System)` — Leaky Bucket is one of the core rate limiting algorithms
- `Backpressure` — Leaky Bucket implements upstream backpressure by queuing excess requests
- `API Gateway` — NGINX, HAProxy implement Leaky Bucket in `limit_req` module
- `Thundering Herd (System)` — Leaky Bucket prevents thundering herds from reaching backends

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Queue absorbs bursts; constant output     │
│              │ rate regardless of input variation        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Downstream service needs constant rate;   │
│              │ NGINX rate limiting; network QoS          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Queue too large vs client timeout;        │
│              │ user-facing APIs where burst should pass  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bucket with a hole: pour fast, drip      │
│              │  slow — the drip rate never changes."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Token Bucket → Sliding Window Counter     │
│              │ → NGINX limit_req module                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** NGINX is configured with `limit_req zone=api burst=100 nodelay`. A client sends 150 requests in 0.5 seconds. The zone has rate=10r/s. Explain: with `nodelay`, how many requests are immediately allowed? How many are rejected with 429? Now remove `nodelay` — how many requests are allowed and what happens to the allowed requests' processing times? Which configuration would you choose for an API used by mobile app users expecting < 500ms response time?

**Q2.** You're designing the rate limiting layer for a payment processing API. The downstream payment processor can handle exactly 50 transactions/second with zero tolerance for bursts (contract SLA: exceed 50 TPS even momentarily and you're billed 10× the overage). Should you use Token Bucket or Leaky Bucket? Design the exact configuration parameters. What happens to rejected payments — immediate 429 or queue with delay? How does your answer change if the downstream payment processor allows 10-second bursts up to 200 TPS?
