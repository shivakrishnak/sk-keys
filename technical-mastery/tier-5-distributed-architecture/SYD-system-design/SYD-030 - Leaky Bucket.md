---
id: SYD-030
title: Leaky Bucket
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-028
used_by: ""
related: SYD-025, SYD-028, SYD-029, SYD-044
tags:
  - architecture
  - algorithm
  - rate-limiting
  - traffic-shaping
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/syd/leaky-bucket/
---

⚡ TL;DR - The leaky bucket algorithm rate-limits by
modeling a bucket that "leaks" at a constant rate.
Incoming requests are added to the bucket (queue).
The bucket drains at a fixed rate, processing one
request at a time. If the bucket is full, incoming
requests overflow (are dropped). The output is a
perfectly smooth, constant stream - regardless of
how bursty the input is. This is the correct algorithm
for strict traffic shaping (smoothing output), not
just rejection-based rate limiting.

| #030 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Rate Limiting (System) | |
| **Used by:** | (Rate Limiter Design) | |
| **Related:** | Thundering Herd, Rate Limiting (System), Token Bucket, Rate Limiter Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (context):**
A payment processor downstream accepts 100 payments/sec.
The upstream checkout service receives a burst of 500
payment requests in 1 second (a flash sale). Token
bucket would allow 100 of those through immediately
(burst = bucket capacity) and reject the rest.
The downstream payment processor handles 100/sec
as a sudden burst, which may cause internal queueing
and latency spikes.

**THE SMOOTH TRAFFIC NEED:**
Some systems cannot tolerate even a short burst above
their processing rate. Network devices (switches),
streaming pipelines, and any system that processes
work at a hardware-limited constant rate need input
shaped to exactly their processing rate. Burst traffic
must be absorbed as queue depth, not forwarded as
a burst.

---

### 📘 Textbook Definition

**Leaky bucket:** A rate limiting and traffic shaping
algorithm where incoming requests are placed in a
bounded queue (the "bucket"). A processor drains the
queue at a constant rate (the "leak rate"), forwarding
one item per time slot. If the queue is full when
a new request arrives, the request is dropped (bucket
overflow). The output is always at exactly the leak
rate - never faster, never slower (until the queue
empties). This guarantees smooth, constant output
regardless of bursty input.

Two variants exist:
- **Leaky bucket as a queue** (traffic shaping): queue
  requests, drain at constant rate, drop on overflow.
  Output is smooth.
- **Leaky bucket as a meter** (rate limiting): count
  requests, allow if rate is within limit, reject if
  exceeded. Similar to fixed window but with smoother
  behavior.

Most implementations use the queue variant for traffic
shaping.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A bucket collects bursty incoming traffic and releases
it at a constant rate. Full bucket → incoming requests
overflow (dropped). Output is always smooth.

**One analogy:**
> A water bucket with a small hole at the bottom:
> - You pour water in at varying rates (bursty traffic)
> - The hole lets water out at a constant rate (leak rate)
> - When the bucket is full, extra water overflows (dropped)
>
> The output stream from the hole is constant: same rate
> whether you pour slowly or in a sudden rush.
> A garden hose on mist mode, not pulse mode.

**One insight:**
Leaky bucket and token bucket solve different problems.
Token bucket: "allow bursty traffic but enforce an
average rate" (rate limiting). Leaky bucket: "smooth
bursty traffic into a constant output stream" (traffic
shaping). Token bucket is right for API rate limiting;
leaky bucket is right for QoS and output smoothing.

---

### 🔩 First Principles Explanation

**THE ALGORITHM:**

```
State:
  queue: Queue     # holds pending requests (FIFO)
  queue_capacity: int  # max = bucket size

Parameters:
  leak_rate: int   # requests processed per second
  capacity: int    # max queue depth (bucket size)

Request arrival:
  if len(queue) < capacity:
      queue.enqueue(request)  # add to bucket
  else:
      drop(request)  # bucket overflow

Processing (runs at constant rate):
  while True:
      if not queue.empty():
          request = queue.dequeue()
          process(request)
      sleep(1 / leak_rate)  # process every 1/leak_rate
        seconds
```

**TOKEN BUCKET VS LEAKY BUCKET COMPARISON:**

```
TOKEN BUCKET:
  Input:  → 500 req/s burst
  Output: → 100 req/s burst (capacity) then 10 req/s
  Characteristic: Output MIRRORS burst (up to capacity)
  
LEAKY BUCKET:
  Input:  → 500 req/s burst
  Output: → 10 req/s constant
  The 90 excess requests wait in queue
  (or overflow if queue full)
  Characteristic: Output is ALWAYS constant rate

EXAMPLE TIMELINE (leak_rate=10/s, capacity=100):

t=0:  100 requests arrive (burst)
      Queue depth: 100
      Outputs: 10 requests processed
      
t=1:  No new arrivals
      Queue depth: 90 (was 100, processed 10)
      Outputs: 10 more processed
      
t=9:  Queue empties; all 100 processed in 10 seconds
      Even though they all arrived at t=0
      Output: constant 10/sec throughout
```

**WHEN THE QUEUE FILLS (overflow behavior):**

```
Scenario: leak_rate=10/s, capacity=100

t=0: 200 requests arrive (burst)
  - 100 queued (bucket fills)
  - 100 dropped (overflow)
  
t=0-10: 10/sec processed from queue
t=10: Queue empty

Behavior: 100 processed, 100 dropped, output always 10/s
Compared to token bucket (capacity=100, rate=10/s):
  - 100 allowed immediately (burst)
  - 100 rejected (429)
  - All 100 allowed requests processed IMMEDIATELY
  - No queueing; all 100 served at once

Key difference: leaky bucket QUEUES the allowed requests;
token bucket PROCESSES allowed requests immediately.
```

**THE TRADE-OFFS:**

**Leaky bucket as traffic shaper:**
Gain: perfectly smooth output; downstream system
never receives a burst.
Cost: queuing adds latency for burst traffic. First
request in a burst is delayed by 0; last request
in a burst of 100 waits 10 seconds (100 ahead of
it in queue). Latency variance is high.

**Token bucket:**
Gain: burst traffic processed immediately (no queue latency).
Cost: downstream receives burst up to capacity;
must handle it.

**For API rate limiting (client-facing):**
Token bucket is typically better: clients prefer
immediate rejection (429) over hanging for 10 seconds
in a queue only to eventually get a response.

**For internal traffic shaping (protecting backends):**
Leaky bucket is better: absorbs bursts as queued
work rather than flooding the downstream.

---

### 🧪 Thought Experiment

**SCENARIO: Email delivery system**

An email marketing platform sends 100,000 emails
per campaign. The SMTP relay accepts 1,000 emails/min.
Sending all 100,000 instantly would overwhelm the
relay. The platform must shape outgoing traffic to
exactly 1,000/min.

**Token bucket approach:**
capacity=1,000, rate=1,000/min. First 1,000 sent
instantly (burst). Then 1,000/min. After 100 seconds
(at 1,000/min), all 100,000 sent. But the first 1,000
were sent as an instant burst, which the SMTP relay
may throttle.

**Leaky bucket approach:**
capacity=1,000 queue, leak_rate=1,000/min (~17/sec).
Each email is queued. Outputs at exactly 17/sec = 1,000/min.
No burst. SMTP relay receives perfectly smooth traffic.
All 100,000 sent in exactly 100 minutes.

**THE WINNER:** Leaky bucket. The requirement is
"never exceed 1,000/min even momentarily." This
requires constant-rate output, not average-rate output.
Email delivery, batch job submission to rate-limited
APIs, data ingestion pipelines - all benefit from
leaky bucket's constant output.

---

### 🧠 Mental Model / Analogy

> Leaky bucket is like an assembly line on a factory floor:
> - Raw materials (requests) arrive in batches (bursty)
> - A conveyor belt moves items through at a fixed speed
>   (leak rate)
> - Overflow bin at the input (queue): holds items
>   waiting for the belt
> - When overflow bin is full: reject new raw materials
>   (bucket overflow)
>
> The production line always runs at the same pace,
> regardless of how raw materials arrived.
>
> Token bucket is like: "accept orders up to batch size
> immediately, then one at a time." Good for order
> acceptance (API). Leaky bucket is for the production
> line itself (processing rate control).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Incoming requests go into a queue. The queue drains
at a fixed rate. When the queue is full, new requests
are dropped. The output is always the same rate, no
matter how many requests arrive at once.

**Level 2 - How to use it (junior developer):**
Use a message queue (Redis list, SQS, RabbitMQ) as
the "bucket." A fixed-rate consumer reads from the
queue at the configured rate. This naturally implements
leaky bucket: queue is the bucket; consumer is the
leak; queue max depth is the capacity.

**Level 3 - How it works (mid-level engineer):**
The key latency property: requests at the head of
the queue experience minimal latency; requests at
the tail wait. For a queue of depth D at rate R,
the tail request waits D/R seconds. For real-time
systems: limit queue depth aggressively to bound
latency. For throughput-optimal systems: larger queue
is acceptable if latency is not critical.

**Level 4 - Why it was designed this way (senior/staff):**
The leaky bucket algorithm (and its implementation
as a constant-rate queue drain) is the foundation
of QoS (Quality of Service) in networking. Cisco,
Juniper, and other network equipment implement
traffic shaping using leaky bucket to enforce SLAs
for premium traffic classes. TCP's congestion window
is related: it controls the rate at which data is
injected into the network, leaking at the maximum
acknowledged rate to prevent congestion.

**Level 5 - Mastery (distinguished engineer):**
The dual of leaky bucket (shaper) is the leaky
bucket (meter/policer). In network QoS:
- Shaper: queues traffic, delays to enforce rate.
  Output is smooth. Adds latency.
- Policer: drops non-conforming traffic immediately.
  No queue. No added latency. Similar to token bucket
  in behavior but without burst tolerance.

In software systems, the distinction maps to:
- Shaper = queue-based leaky bucket (latency tradeoff)
- Policer = token bucket with capacity=1 (strict rate,
  minimal burst, immediate rejection)

Choosing between these is a latency-vs-accuracy
tradeoff: shaping is kinder to clients (queued, not
dropped) but adds latency; policing is harsher
(immediate rejection) but adds no latency.

---

### ⚙️ How It Works (Mechanism)

**Leaky bucket as a queue (traffic shaper):**

```
┌──────────────────────────────────────────────────────┐
│ LEAKY BUCKET IMPLEMENTATION                         │
│                                                      │
│  Incoming requests:                                  │
│  ─────────────────────►                             │
│  Burst: 500 req/s      │                            │
│                        ▼                            │
│               ┌────────────────┐                    │
│               │  Queue (Bucket)│ ← capacity = 100   │
│               │  [req1 req2   ]│                    │
│               │  [req3 req4   ]│                    │
│               │  [req5 ... 100]│                    │
│               └───────┬────────┘                    │
│                       │ drain at constant rate       │
│                       │ 10 req/sec                  │
│                       ▼                             │
│  Outgoing requests: exactly 10/sec                  │
│  ─────────────────────────────►                     │
│  (smooth output regardless of bursty input)         │
│                                                      │
│ If queue full → incoming requests dropped           │
│   (client receives 429 or connection refused)       │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Leaky bucket traffic shaper (Python)**
```python
# Leaky bucket as a traffic shaper
# Used for outbound rate-limited API calls
import asyncio
import time
from collections import deque

class LeakyBucket:
    """
    Traffic shaper: drains at constant rate.
    Suitable for outbound API call rate limiting.
    """

    def __init__(self, rate: float, capacity: int):
        """
        rate: requests per second to drain
        capacity: max queue depth (bucket size)
        """
        self.rate = rate
        self.capacity = capacity
        self.queue: deque = deque()
        self._last_drain = time.monotonic()

    def add(self, item) -> bool:
        """Add item to bucket. Returns False if overflow."""
        if len(self.queue) >= self.capacity:
            return False  # Overflow: drop
        self.queue.append(item)
        return True

    async def start_draining(self, processor):
        """Drain the bucket at constant rate."""
        interval = 1.0 / self.rate  # seconds per request
        while True:
            if self.queue:
                item = self.queue.popleft()
                await processor(item)
            await asyncio.sleep(interval)

# Usage: outbound email sending at 100/min
class EmailSender:
    def __init__(self):
        # 100 emails/min = 1.67/sec, buffer up to 1000
        self.bucket = LeakyBucket(
            rate=100/60, capacity=1000)

    async def send_campaign(self, emails: list[str]):
        # Add all emails to the bucket
        dropped = 0
        for email in emails:
            if not self.bucket.add(email):
                dropped += 1  # Overflow
        if dropped:
            print(f"WARNING: {dropped} emails dropped")

        # The bucket drains at exactly 100/min
        # No burst; SMTP server receives smooth traffic
```

**Example 2 - BAD: Token bucket when smooth output needed**
```python
# BAD: Using token bucket when leaky bucket is required
# Token bucket allows burst → overwhelms rate-limited API

import time

def send_to_rate_limited_api(requests: list):
    """BAD: Token bucket approach for outbound calls"""
    tokens = 100  # burst capacity
    last_refill = time.time()
    refill_rate = 10  # tokens/sec

    for req in requests:
        now = time.time()
        tokens = min(100, tokens + (now - last_refill) * refill_rate)
        last_refill = now

        if tokens >= 1:
            tokens -= 1
            call_api(req)  # PROBLEM: First 100 calls made
                           # instantly - API throttles us
        else:
            print("Rate limited locally - skipping")
    
# GOOD: Use leaky bucket (see Example 1)
# All 100k requests queued and drained at 10/sec
# API receives perfectly smooth traffic, no throttling
```

**Example 3 - Rate limiting inbound requests (leaky bucket as meter)**
```java
// Leaky bucket as a rate limiter (meter/policer variant)
// No queue; non-conforming requests rejected immediately

public class LeakyBucketRateLimiter {
    private final double leakRate;  // requests per millisecond
    private double water;           // current bucket level
    private long lastLeakTime;      // last leak timestamp

    public LeakyBucketRateLimiter(
            double requestsPerSecond,
            double capacity) {
        this.leakRate = requestsPerSecond / 1000.0;
        this.water = 0;
        this.capacity = capacity;
        this.lastLeakTime = System.currentTimeMillis();
    }

    public synchronized boolean allowRequest(double cost) {
        long now = System.currentTimeMillis();
        long elapsed = now - lastLeakTime;

        // Leak: reduce water level based on elapsed time
        water = Math.max(0, water - (elapsed * leakRate));
        lastLeakTime = now;

        // Check if request fits
        if (water + cost <= capacity) {
            water += cost;
            return true;  // Allow
        }
        return false;  // Rate limited
    }
}
// Behavior: no queue, no burst.
// Each request either passes or is immediately rejected.
// Effective rate = leakRate (constant drain).
// Compared to token bucket: same API but no burst tolerance.
```

---

### ⚖️ Comparison Table

| Property | Leaky Bucket (Shaper) | Token Bucket | Fixed Window |
|---|---|---|---|
| **Burst handling** | Queues burst, outputs at constant rate | Allows burst up to capacity | Allows burst at window boundary |
| **Output rate** | Exactly constant (always = leak rate) | Variable (burst then sustained) | Variable (choppy) |
| **Client latency** | Higher for burst traffic (queued) | Low (immediate allow or reject) | Low (immediate) |
| **Memory** | O(queue depth) | O(1) | O(1) |
| **Best for** | Outbound traffic shaping, QoS | API rate limiting (inbound) | Simple counters |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Leaky bucket is the same as token bucket | They solve opposite problems. Token bucket controls average rate while allowing burst. Leaky bucket enforces constant rate with no burst. Choosing wrong leads to either rejected legitimate traffic (too strict) or overwhelmed downstream (too permissive). |
| Leaky bucket is better because it never rejects | The queue-based leaky bucket still drops requests when the queue is full. It is not "kinder" - it is just that the drop decision happens at queue capacity rather than at rate limit. Overflow behavior is the same: requests are still dropped. |
| Use leaky bucket for API rate limiting | For inbound API rate limiting, token bucket (with burst tolerance) is almost always better. Leaky bucket's queue creates variable latency for bursty but legitimate traffic. Clients prefer immediate 429 over waiting 10 seconds in a queue. |

---

### 🚨 Failure Modes & Diagnosis

**Queue Depth Grows Unbounded Under Sustained Overload**

**Symptom:**
A leaky bucket implementation with a large queue
capacity (10,000 items) is configured to drain at
100/sec. A sustained 200 req/sec load arrives.
The queue grows by 100 items/sec. After 100 seconds,
the queue holds 10,000 items. Requests at the tail
of the queue wait 10,000/100 = 100 seconds. Users
experience 100-second latency instead of rejection.

**Root Cause:**
Queue capacity was too large relative to acceptable
latency. 10,000 items at 100/sec = 100 seconds wait
for tail items.

**Fix:**
```python
# Size the queue based on acceptable max latency:
# max_queue_depth = max_acceptable_latency_sec × leak_rate

# Example: max latency = 5 seconds, rate = 100/sec
MAX_LATENCY = 5   # seconds
LEAK_RATE = 100   # requests/second
capacity = MAX_LATENCY * LEAK_RATE  # = 500

# This ensures the last item in a full queue
# waits at most 5 seconds before being processed
# or being dropped if the queue remains full.

bucket = LeakyBucket(rate=LEAK_RATE, capacity=500)
```

**Rule:** `max_queue_wait = capacity / leak_rate`.
Set capacity to meet latency SLO, not to maximize
acceptance rate.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Rate Limiting (System)` - the context for both
  leaky bucket and token bucket

**Builds On This (learn these next):**
- `Token Bucket` - the contrasting algorithm; helps
  clarify when to use leaky vs token bucket
- `Rate Limiter Design` - applying these algorithms
  in a full system design answer

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ALGORITHM     │ Queue (bucket) fills with requests.     │
│               │ Drains at constant rate. Overflow = drop│
├───────────────┼─────────────────────────────────────────┤
│ PARAMS        │ leak_rate: constant output rate         │
│               │ capacity: max queue depth (bucket size) │
├───────────────┼─────────────────────────────────────────┤
│ OUTPUT        │ ALWAYS constant (= leak_rate)           │
│               │ Regardless of bursty input              │
├───────────────┼─────────────────────────────────────────┤
│ USE CASE      │ Outbound traffic shaping                │
│               │ Network QoS, email delivery,            │
│               │ batch API call rate limiting            │
├───────────────┼─────────────────────────────────────────┤
│ LATENCY       │ max_wait = capacity / leak_rate         │
│               │ Size capacity to bound max wait time    │
├───────────────┼─────────────────────────────────────────┤
│ VS TOKEN      │ Leaky: constant output, queue latency   │
│               │ Token: burst allowed, immediate reject  │
│               │ API inbound → token bucket              │
│               │ Outbound shaping → leaky bucket         │
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Input: bursty. Output: always constant.│
│               │  Queue absorbs burst. Full queue = drop.│
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Sharding → Hot Shard                    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Leaky bucket = constant output rate, always. Burst
   absorbed as queue depth; full queue = dropped.
   Token bucket allows burst; leaky bucket smooths it.
2. Use leaky bucket for outbound traffic shaping (sending
   to a rate-limited third-party API). Use token bucket
   for inbound API rate limiting.
3. Size queue capacity to bound latency: capacity =
   max_acceptable_wait_sec × leak_rate. Large queue
   = long tail latency, not kindness to clients.

**Interview one-liner:**
"Leaky bucket enforces a strictly constant output rate: incoming
requests are added to a bounded queue (the bucket), which drains
at a fixed rate (the leak). Burst traffic fills the queue rather
than being forwarded as a burst. When the queue overflows, requests
are dropped. The key distinction from token bucket: token bucket
allows bursting up to capacity and immediately processes allowed
requests; leaky bucket queues all traffic and processes at constant
rate, eliminating any burst on the output. Leaky bucket is correct
for outbound traffic shaping (email delivery, sending to third-party
APIs with strict rate limits). Token bucket is correct for inbound
API rate limiting where clients prefer immediate rejection (429)
over queued latency."
