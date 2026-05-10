---
id: SYD-030
title: Leaky Bucket
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-028, SYD-029
used_by: SYD-044
related: SYD-028, SYD-029, SYD-044
tags:
  - rate-limiting
  - algorithm
  - advanced
  - performance
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /syd/leaky-bucket/
---

# SYD-030 - Leaky Bucket

⚡ TL;DR - Rate limiting algorithm where requests queue in a FIFO bucket and drain at a fixed rate, producing perfectly smooth output traffic regardless of bursty input.

| SYD-030         | Category: System Design   | Difficulty: ★★★ |
| :-------------- | :------------------------ | :-------------- |
| **Depends on:** | SYD-028, SYD-029          |                 |
| **Used by:**    | SYD-044                   |                 |
| **Related:**    | SYD-028, SYD-029, SYD-044 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A downstream service (database, payment provider, third-party API) can handle exactly 100 requests/second. Your upstream application has bursty traffic - sometimes 0 req/sec, sometimes 1,000 req/sec. Even though the average is 80 req/sec (within the downstream limit), the bursts cause downstream overload, timeouts, and cascading failures. Averaging is not enough - you need output to be smooth.

**THE BREAKING POINT:**
The token bucket algorithm allows bursts to pass through to downstream systems. A user with a full token bucket (100 tokens) can fire 100 requests in 1 millisecond, overwhelming any downstream service that assumes smooth traffic. Token bucket is right for admission control but wrong for traffic shaping.

**THE INVENTION MOMENT:**
Network engineers designing ATM networks in the 1980s needed to guarantee that traffic entering a network segment would not exceed its bandwidth. They designed the leaky bucket: bursts are absorbed by a queue, and traffic exits the queue at a fixed, predictable rate. Downstream equipment never sees a burst, regardless of upstream traffic patterns.

**EVOLUTION:**
Leaky bucket became a standard in network QoS protocols and was documented in RFC 2697. In software systems, it is used in message queue consumers (Kafka consumer rate limiting), API gateways needing smooth forwarding, and job queues protecting downstream workers from bursts.

---

### 📘 Textbook Definition

The **leaky bucket** is a traffic shaping algorithm that places incoming requests into a FIFO queue (the bucket). A separate process drains the queue at a fixed rate (the leak rate), forwarding one request per time interval. If the queue is full, new arrivals are rejected. The algorithm guarantees that output rate is always constant regardless of input burst pattern.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Queue all requests in a fixed-size FIFO; drain at a constant rate; reject arrivals when the queue is full.

**One analogy:**
> A traffic light on a busy road. Cars arrive in bursts, but only one car passes per green cycle (fixed rate). The queue behind the light absorbs the burst. If the queue overflows onto the highway, no more cars can join.

**One insight:**
Leaky bucket smooths output at the cost of added queuing latency. Token bucket smooths input at the cost of allowing bursts downstream. They solve different halves of the same problem.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Output rate is strictly constant - the drain rate is a hard ceiling on downstream request frequency.
2. Burst absorption capacity is finite - bounded by queue size measured in requests, not time.
3. Queuing delays are predictable - request N waits approximately N/drain_rate seconds in a full queue.
4. Fairness is FIFO - no request jumps the queue regardless of priority.

**DERIVED DESIGN:**
Two parameters fully determine behaviour: queue capacity (burst absorption headroom) and drain rate (downstream load guarantee). Setting drain rate = downstream service limit guarantees the downstream service is never overloaded regardless of upstream pattern.

**THE TRADE-OFFS:**
**Gain:** Perfectly smooth downstream traffic, predictable latency for queued requests, guaranteed downstream protection.
**Cost:** Added queuing latency for every request (worst case: queue_capacity / drain_rate seconds), memory proportional to queue size, no burst pass-through.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Smoothing traffic requires buffering it - the queue is intrinsic to the algorithm.
**Accidental:** In distributed systems, the queue must be persistent to survive crashes (Kafka, Redis streams) - this adds coordination overhead not present in single-node implementations.

---

### 🧪 Thought Experiment

**SETUP:**
A payment API can process 10 requests/second. You receive a burst of 50 payment requests in 1 second.

**WHAT HAPPENS WITHOUT LEAKY BUCKET:**
All 50 requests hit the payment API simultaneously. The API handles 10, then rejects the other 40. 80% of payments fail. Even though the average load was manageable, the instantaneous burst was 5x the limit.

**WHAT HAPPENS WITH LEAKY BUCKET:**
50 requests enter the queue (capacity 100). The queue drains at 10 req/sec. Request 1 is processed in 0-100ms. Request 50 is processed in approximately 5 seconds. All 50 payments succeed with increased latency for later requests but zero failures.

**THE INSIGHT:**
Leaky bucket trades latency for reliability. In payment processing, a 5-second delay is acceptable; a failed payment is not. The choice between token bucket and leaky bucket comes down to: which is worse - latency or failure?

---

### 🧠 Mental Model / Analogy

> Leaky bucket is a physical bucket with a small hole at the base. Water (requests) pours in from the top at variable rates. It drips out the hole at a constant rate. If you pour faster than the hole drains, the bucket fills. When it overflows, excess water is lost.

**Mapping:**
- Water pouring in → incoming requests (variable rate)
- Hole at base → drain rate (constant)
- Bucket → FIFO queue
- Bucket capacity → maximum queue depth
- Water level → current queue depth
- Overflow water → rejected requests (queue full)
- Drips out → processed requests at constant rate

Where this analogy breaks down: real water flows continuously; leaky bucket implementations are discrete (one request per time slot), and the queue is ordered (FIFO), unlike water which mixes uniformly.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Imagine a ticket queue outside a concert. The venue lets in exactly 10 people per minute regardless of how many arrive. Early arrivals queue. If the queue gets too long (100 people), latecomers are turned away. The venue always gets exactly 10 people per minute - never more.

**Level 2 - How to use it (junior developer):**
Create a FIFO queue with a maximum size. Accept incoming requests into the queue if not full; reject if full. Run a background thread that dequeues one request per (1/rate) seconds and processes it. Tune queue capacity: max_wait_seconds * drain_rate = max queue depth.

**Level 3 - How it works (mid-level engineer):**
Two concurrent processes: (1) accept process - enqueue incoming requests if queue < capacity, else reject with 429; (2) drain process - dequeue one request every (1/rate) seconds and forward to downstream. The drain process acts as a governor, making downstream throughput independent of upstream pattern. Multi-threaded implementations must synchronise queue access between both processes.

**Level 4 - Why it was designed this way (senior/staff):**
Leaky bucket enforces a traffic contract. In distributed systems, a message queue (Kafka, SQS) IS the leaky bucket: the queue absorbs bursts (producers), and the consumer group is the drain (at whatever processing rate the consumers can sustain). The queue capacity is the leaky bucket size; the consumer throughput is the leak rate. This pattern is already deployed in every Kafka-backed system.

**Expert Thinking Cues:**
- "What is the maximum queuing delay I can tolerate? That sets queue capacity."
- "What is my downstream service's safe ingestion rate? That sets drain rate."
- "Should I use a persistent queue (Kafka) or in-memory queue (on crash tolerance)?"
- "What happens to queued requests during a downstream outage?"

---

### ⚙️ How It Works (Mechanism)

```
LEAKY BUCKET ALGORITHM
══════════════════════

State:
  queue: FIFO deque (max_size = capacity)
  drain_rate: requests per second

Accept process (on request arrival):
  if len(queue) < capacity:
    queue.append(request) → QUEUED
  else:
    return REJECTED (429)

Drain process (background, runs forever):
  sleep(1.0 / drain_rate)
  if queue not empty:
    request = queue.popleft()
    forward_to_downstream(request)

Example (capacity=100, rate=10/sec):
  t=0:   50 requests arrive, all queued
  t=0.1: request[0] forwarded downstream
  t=5.0: request[49] forwarded downstream
  t=5.0: queue empty, drain idles
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Incoming Requests (bursty)
    │
    ▼
Accept Process        ← YOU ARE HERE
    │
    ├── Queue not full → enqueue
    └── Queue full    → 429 rejected
              │
              ▼
         FIFO Queue
         [r1|r2|r3|...|rN]
              │
              ▼ (drain at fixed rate)
    Drain Process
    (1 request per 1/rate seconds)
              │
              ▼
    Downstream Service
    (always receives smooth traffic)
```

**FAILURE PATH:**
Drain process crashes → queue fills → all new requests rejected. For production, use a persistent queue (Kafka, SQS) and a supervised consumer group so drain survives restarts without losing queued requests.

**WHAT CHANGES AT SCALE:**
With N application nodes each running a local leaky bucket, the downstream receives N * drain_rate requests/sec total. Solution: centralised queue (shared Kafka topic) that all nodes enqueue to, with a single consumer group draining at the intended rate.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multi-threaded accept and drain processes require synchronised queue access: Python `collections.deque` with `threading.Lock`; Java `LinkedBlockingQueue` provides built-in thread safety. In distributed systems, the queue (Kafka, SQS) provides concurrency guarantees natively.

---

### 💻 Code Example

```python
from collections import deque
import threading, time

# BAD: No synchronisation - race condition between
# accept and drain threads
class UnsafeLeakyBucket:
    def __init__(self, capacity, rate):
        self.queue = []   # not thread-safe
    def add(self, req):
        if len(self.queue) < self.capacity:
            self.queue.append(req)  # RACE

# GOOD: Thread-safe with locking
class LeakyBucket:
    def __init__(self, capacity: int,
                 drain_rate: float):
        self.capacity = capacity
        self.drain_rate = drain_rate
        self.queue: deque = deque()
        self.lock = threading.Lock()
        threading.Thread(
            target=self._drain, daemon=True
        ).start()

    def _drain(self):
        interval = 1.0 / self.drain_rate
        while True:
            time.sleep(interval)
            with self.lock:
                if self.queue:
                    req = self.queue.popleft()
                    self._process(req)

    def _process(self, req):
        pass  # forward to downstream

    def submit(self, request) -> bool:
        with self.lock:
            if len(self.queue) < self.capacity:
                self.queue.append(request)
                return True   # QUEUED
            return False      # REJECTED
```

**How to test / verify correctness:**
- Burst test: submit 50 requests instantly; verify all queued if capacity >= 50.
- Drain rate test: submit 100 requests; measure time until last is processed (= 100/drain_rate sec).
- Overflow test: submit capacity+1 requests; verify exactly 1 is rejected.
- Latency test: request N waits approximately N/drain_rate seconds.

---

### ⚖️ Comparison Table

| Property | Leaky Bucket | Token Bucket |
|---|---|---|
| **Output traffic** | Always constant | Can burst |
| **Input burst handling** | Queued (absorbed) | Passed through |
| **Latency** | Added queuing delay | Near-zero if allowed |
| **Memory** | O(queue capacity) | O(1) per user |
| **Downstream protection** | Guaranteed | Not guaranteed |
| **Best for** | Traffic shaping, protecting downstream | API admission control |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Leaky bucket = token bucket with queuing" | Fundamentally different: token bucket controls admission; leaky bucket controls output rate. |
| "Leaky bucket is fairer" | FIFO is not fair when one user's burst fills the entire queue, blocking all others. |
| "Queue depth does not affect latency" | Worst-case latency = queue_capacity / drain_rate. Queue of 1000 at 10/sec = 100 second wait. |
| "Leaky bucket prevents all overload" | Only for the specific downstream it directly protects. Upstream still sees 429 rejections. |
| "Token bucket is always better" | For protecting a downstream with a strict rate limit, leaky bucket provides provably better guarantees. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Queue Fills Permanently**
**Symptom:** All requests rejected; queue never drains because sustained input > drain rate.
**Root Cause:** Drain rate set too low for sustained input rate - queue absorbs bursts but cannot clear backlog.
**Diagnostic:**
```bash
# Monitor Kafka consumer lag (if Kafka-backed)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group rate-limiter-consumer
# LAG growing = drain rate insufficient
```
**Fix:** Increase drain rate or scale consumer group. Queue is for burst absorption, not sustained backlog.
**Prevention:** Set drain_rate >= sustained average input rate during design.

**Mode 2: Drain Process Single Point of Failure**
**Symptom:** Queue depth grows indefinitely; downstream receives nothing.
**Root Cause:** Single drain thread or process crashed; no monitoring or restart.
**Diagnostic:**
```bash
# Check if drain process is running
ps aux | grep drain-worker
# Check queue depth trend
redis-cli llen leaky_bucket_queue
```
**Fix:** Use process supervisor (systemd, Supervisor). Prefer persistent queue (Kafka) with consumer group auto-rebalance.
**Prevention:** Monitor queue depth growth rate; alert when depth increases for > 30 seconds.

**Mode 3: Latency SLO Breach Under Burst**
**Symptom:** P99 latency spikes to minutes on burst; clients timeout before requests are served.
**Root Cause:** Queue capacity set too high; P99 wait = queue_capacity / drain_rate >> SLO.
**Diagnostic:**
```bash
# Measure wait time at queue depth
# max_wait = capacity / drain_rate
echo "Max wait: $((capacity / drain_rate)) seconds vs SLO: ${slo}s"
```
**Fix:** Reduce capacity = drain_rate * max_acceptable_latency_sec. Add deadline-aware dequeue: discard requests older than timeout.
**Prevention:** Always compute max_wait at design time and compare to your SLO timeout.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-028 - Rate Limiting (System)]] - The problem class leaky bucket addresses
- [[SYD-029 - Token Bucket]] - The complementary admission control algorithm

**Builds On This (learn these next):**
- [[SYD-044 - Rate Limiter Design]] - Full system design incorporating both algorithms
- [[SYD-036 - Push vs Pull Architecture]] - Related pattern for producer-consumer flow control

**Alternatives / Comparisons:**
- [[SYD-029 - Token Bucket]] - Allows burst pass-through; lower latency; weaker downstream guarantee
- [[SYD-028 - Rate Limiting (System)]] - Overview of all rate limiting strategies

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Traffic shaping via         ║
║               fixed-rate FIFO drain       ║
╠══════════════════════════════════════════╣
║ PROBLEM       Bursts overload downstream  ║
║ IT SOLVES     services with strict limits ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   Output rate is always       ║
║               constant; input burst       ║
║               is absorbed by queue        ║
╠══════════════════════════════════════════╣
║ USE WHEN      Protecting downstream;      ║
║               smoothing async job load    ║
╠══════════════════════════════════════════╣
║ AVOID WHEN    Low-latency interactive     ║
║               APIs; queuing is unacceptable║
╠══════════════════════════════════════════╣
║ TRADE-OFF     Downstream protection vs    ║
║               added queuing latency       ║
╠══════════════════════════════════════════╣
║ ONE-LINER     Enqueue burst; drain at     ║
║               fixed rate; reject overflow ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-031: Sharding           ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Leaky bucket guarantees constant output rate; token bucket does not - use leaky for downstream protection.
2. Max queuing latency = queue_capacity / drain_rate - always compute this and compare to your SLO timeout.
3. In distributed systems, Kafka consumer group IS the leaky bucket - the consumer is the drain.

**Interview one-liner:**
"Leaky bucket queues bursts in a FIFO and drains at a constant rate, guaranteeing downstream traffic is always smooth regardless of upstream burst pattern."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Control output rate, not just input admission. Systems that focus only on admission control (do I accept this?) but ignore output shaping (at what rate do I forward this?) move the overload problem one layer downstream. Complete traffic management requires both: admit at user-facing capacity, shape output to match downstream limits.

**Where else this pattern appears:**
- **Kafka consumer groups:** Consumer lag is the leaky bucket queue - produce at any rate, consume at sustainable processing rate.
- **Print queues:** Documents queue at arbitrary arrival frequency; the printer processes at its fixed mechanical rate.
- **CPU run queue:** Runnable processes queue; CPU executes one thread at a time at its fixed clock rate.

---

### 💡 The Surprising Truth

The leaky bucket algorithm from RFC 2697 is called the "single rate three-colour marker" in networking and does NOT use binary accept/reject - it marks packets green (conforming), yellow (slightly over), or red (far over) to signal different drop priorities to routers. This graduated response means slightly-over-limit traffic might survive network congestion instead of being completely rejected. Software API rate limiters almost never implement this three-colour model, opting for binary 200/429 responses instead - even though returning a "Retry-After" header with a short delay (yellow) would produce far better user experience than a hard rejection.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A leaky bucket has capacity=1000, drain_rate=100/sec. A bug sends 10,000 requests in 1 second. What fraction of requests are rejected, how long does the queue take to clear, and what retry strategy should the upstream implement?
*Hint:* Calculate rejection count (10000-1000), then compute drain time (1000/100 = 10 sec), then look into exponential backoff with jitter to avoid retry storms.

**Q2 (Scale):** You have 20 API gateway nodes each with a local leaky bucket (capacity=100, drain_rate=10/sec). Your downstream can handle 50 req/sec total. What is the maximum downstream load possible, and what architecture change is required?
*Hint:* Multiply per-node drain rate by node count for worst-case calculation, then explore the shared queue pattern (centralised Kafka topic with single consumer group) and its latency implications.

**Q3 (Design Trade-off):** For a chat API where messages must be delivered within 2 seconds, is leaky bucket the right choice for rate limiting incoming messages? What is the maximum queue capacity you can set, and what alternative approach might be better?
*Hint:* Compute max_capacity = drain_rate * max_wait_sec, evaluate whether this capacity is sufficient for real burst patterns, then compare with token bucket's immediate-response model and the trade-offs around message loss vs delay.
