---
id: SYD-037
title: Polling vs Webhooks
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-036, SYD-008
used_by: SYD-047, SYD-048
related: SYD-038, SYD-036, SYD-044
tags:
  - architecture
  - api
  - async
  - pattern
  - intermediate
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 37
permalink: /syd/polling-vs-webhooks/
---

# SYD-037 - Polling vs Webhooks

⚡ TL;DR - Polling repeatedly asks "anything new?"; webhooks let the server push events to you the moment they happen - trading simplicity for efficiency.

| SYD-037         | Category: System Design      | Difficulty: ★★☆ |
| :-------------- | :--------------------------- | :-------------- |
| **Depends on:** | SYD-036, SYD-008             |                 |
| **Used by:**    | SYD-047, SYD-048             |                 |
| **Related:**    | SYD-038, SYD-036, SYD-044   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a notification mechanism, consumers must continuously ask the server "do you have anything new for me?" This means thousands of identical GET requests every minute - most returning nothing.

**THE BREAKING POINT:**
At scale, polling becomes a denial-of-service attack in slow motion. A system with 100K clients polling every 30 seconds generates 3,300 requests/sec on the server, the vast majority returning empty responses.

**THE INVENTION MOMENT:**
Webhooks inverted the model: instead of the consumer asking the server, the server tells the consumer exactly when something happens. Polling is the consumer calling the bakery every hour asking if the bread is ready; webhooks are the bakery calling you when the bread comes out of the oven.

**EVOLUTION:**
Polling evolved into long polling (hold the connection open until data arrives), then Server-Sent Events and WebSockets for real-time streaming. Webhooks evolved with retry logic, delivery guarantees, and HMAC signature verification to handle failures and abuse.

---

### 📘 Textbook Definition

**Polling** is a pattern where a client periodically requests updates from a server on a fixed or adaptive schedule. **Webhooks** are HTTP callbacks: the server makes an outbound HTTP POST to a consumer-registered endpoint whenever a relevant event occurs. Both solve event notification; they differ in who initiates the communication and who bears the operational complexity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Polling asks on a schedule; webhooks deliver on event.

**One analogy:**

> Polling is refreshing your email inbox every 5 minutes. Webhooks are having new emails ring your phone instantly.

**One insight:**
The choice is not just technical - it is operational. Polling requires the consumer to handle nothing special on its end. Webhooks require the consumer to run a public HTTPS endpoint, handle retries, and process events idempotently.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. In distributed systems, parties need to know when state changes occur.
2. Communication always requires one party to initiate it.
3. Bandwidth and compute are finite - idle requests waste both.
4. Reliability requires handling delivery failures.

**DERIVED DESIGN:**
If the consumer initiates: polling. Simple for the consumer, wasteful at scale.
If the producer initiates: webhook/push. Efficient, but requires the consumer to be reachable and resilient.

**THE TRADE-OFFS:**
**Gain (Webhooks):** Real-time delivery, no wasted requests, server-driven fanout.
**Cost (Webhooks):** Consumer must expose a public endpoint; delivery is not guaranteed without retry logic; event ordering is not guaranteed.

**Gain (Polling):** Consumer controls timing, works behind firewalls, simple to implement.
**Cost (Polling):** High latency (up to poll interval), wasteful at scale, misses events between polls if retention is limited.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** You must detect and react to change. That communication has direction and timing.
**Accidental:** The retry, signature, and queue mechanisms needed to make webhooks reliable at scale.

---

### 🧪 Thought Experiment

**SETUP:** A payment provider wants to notify 50K merchants when a payment clears. Payments complete within 200ms-30s.

**WHAT HAPPENS WITHOUT WEBHOOKS (pure polling):**
Each merchant polls `GET /payments?status=pending` every 5 seconds. That is 50K × 12 req/min = 600K req/min = 10K req/sec, most returning nothing. A merchant processing 100 payments/day waits up to 5 seconds after completion before their server knows. The payment provider's API is dominated by empty polls.

**WHAT HAPPENS WITH WEBHOOKS:**
The payment provider POSTs `payment.completed` to each merchant's registered URL the moment payment clears. Zero wasted requests. Average notification latency under 1 second. The provider queue absorbs burst and retries on failure.

**THE INSIGHT:**
Webhooks shift the cost from the consumer's polling loop to the producer's delivery infrastructure. This is almost always the right trade-off when the producer can support it - but it requires the consumer to run reliable HTTPS endpoints and implement idempotent event processing.

---

### 🧠 Mental Model / Analogy

> Think of polling as a postal worker checking an empty mailbox twelve times a day, and webhooks as a delivery driver who only shows up when there is an actual package to drop off.

- **Mailbox** = consumer endpoint
- **Postal worker checking** = polling request
- **Package** = event payload
- **Delivery driver call** = webhook POST
- **Delivery confirmation** = HTTP 200 response
- **Redelivery attempt** = webhook retry

Where this analogy breaks down: delivery drivers do not send packages simultaneously to 50K doors - at scale, webhooks need fan-out queues that this analogy does not capture.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Polling means you keep asking "is it ready yet?" Webhooks mean you get a call when it is ready. One wastes time asking; the other lets you focus on something else.

**Level 2 - How to use it (junior developer):**
Use polling when you control both sides and data changes slowly (e.g., checking job status). Use webhooks when subscribing to third-party events (payment complete, GitHub push). Always return HTTP 200 quickly from a webhook receiver and process the event async to avoid timeout-triggered retries.

**Level 3 - How it works (mid-level engineer):**
Polling = `GET /resource` on a timer, compare to previous state. Long polling = server holds connection open until data available or timeout. Webhooks = provider registers your URL, fires HTTP POST on event, expects 200-299 response. Failures trigger retries with exponential backoff. Consumers must implement idempotency.

**Level 4 - Why it was designed this way (senior/staff):**
Webhook delivery reliability requires a durable event queue at the producer side. Slow consumer endpoints backlog the delivery queue. At very high event rates, webhooks invert the scaling problem: the producer manages thousands of outbound connections. Hybrid approaches (webhook primary, polling fallback) handle consumer unavailability. Kafka-style pull combines ordering guarantees with event retention.

**Expert Thinking Cues:**
- Ask: "What is the p99 latency from event occurrence to consumer processing?"
- Ask: "What happens when the consumer endpoint is down for 30 minutes?"
- Red flag: consumers polling faster than the event rate
- Red flag: webhooks without idempotency keys causing duplicate processing

---

### ⚙️ How It Works (Mechanism)

**Polling mechanism:**
```
Client timer fires
  -> GET /api/events?since=last_timestamp
  -> Server queries DB for events > timestamp
  -> Returns [] if none, or events if any
  -> Client updates last_timestamp
  -> Wait for next timer tick
```

**Webhook mechanism:**
```
Producer detects state change
  -> Serializes event to JSON payload
  -> Looks up registered webhook URLs
  -> Enqueues delivery tasks (durable)
  -> Worker POSTs payload to each URL
  -> On HTTP 200-299: mark delivered
  -> On 4xx/5xx or timeout: retry with backoff
  -> After N retries: dead-letter / alert
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Event occurs at Producer]
         |
         v
[Outbound queue (durable)] <- YOU ARE HERE
         |
         v
[Delivery worker]
         |
    HTTP POST /webhook
         |
         v
[Consumer endpoint -> ACK 200]
         |
         v
[Async job queued: process event]
         |
         v
[Business logic executed]
```

**FAILURE PATH:**
```
Delivery worker -> POST -> 500 or timeout
  -> Retry at T+30s
  -> Retry at T+5m
  -> Retry at T+30m
  -> Dead-letter queue -> alert team
Consumer must use idempotency_key to skip
duplicates when retries succeed after partial
processing.
```

**WHAT CHANGES AT SCALE:**
At 1M webhooks/min, queue depth becomes the key metric. Slow consumers block delivery workers. Solution: per-consumer queues with rate limiting. Slow consumers are isolated so they don't delay fast ones.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Webhooks arrive in parallel from retries and original delivery. Consumers must be idempotent. Use the event ID as idempotency key. In clustered consumer environments, implement distributed locking or DB unique constraints on event ID.

---

### 💻 Code Example

**BAD - polling every second regardless of results:**
```python
# BAD: tight polling, no backoff
while True:
    resp = requests.get("/api/orders?status=pending")
    for order in resp.json():
        process(order)
    time.sleep(1)  # hammers server even when no data
```

**GOOD - adaptive polling with backoff:**
```python
import time, requests

POLL_MIN, POLL_MAX = 2, 60
interval = POLL_MIN

def poll_orders(last_id=0):
    global interval
    resp = requests.get(
        "/api/orders",
        params={"after_id": last_id, "limit": 100}
    )
    orders = resp.json()
    if orders:
        for o in orders:
            process(o)
        last_id = orders[-1]["id"]
        interval = POLL_MIN        # reset on activity
    else:
        interval = min(interval * 2, POLL_MAX)  # backoff
    return last_id

last_id = 0
while True:
    last_id = poll_orders(last_id)
    time.sleep(interval)
```

**GOOD - webhook receiver with idempotency:**
```python
from flask import Flask, request, jsonify
import hashlib, hmac, os

app = Flask(__name__)
SECRET = os.environ["WEBHOOK_SECRET"]
seen = set()  # use Redis in production

@app.route("/webhook/payment", methods=["POST"])
def payment_webhook():
    sig = request.headers.get("X-Signature-256", "")
    body = request.get_data()
    expected = "sha256=" + hmac.new(
        SECRET.encode(), body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return jsonify({"error": "bad sig"}), 401

    event = request.get_json()
    eid = event["id"]
    if eid in seen:
        return jsonify({"status": "duplicate"}), 200

    seen.add(eid)
    enqueue_for_processing(event)  # durable async queue
    return jsonify({"status": "accepted"}), 200
```

**How to test / verify correctness:**
- Send duplicate `event_id` twice - assert second call returns 200 but does not re-process.
- Tamper with body before HMAC check - assert 401 response.
- Simulate consumer returning 500 - assert retry logic fires.

---

### ⚖️ Comparison Table

| Dimension          | Polling           | Long Polling     | Webhooks          |
| ------------------ | ----------------- | ---------------- | ----------------- |
| Latency            | Up to interval    | Near real-time   | Near real-time    |
| Wasted requests    | High              | Low              | None              |
| Consumer simplicity | High             | Medium           | Low (needs URL)   |
| Works behind NAT   | Yes               | Yes              | No                |
| Ordering guarantee | Client controls   | Client controls  | Not guaranteed    |
| Delivery guarantee | Client controls   | Client controls  | Retry-based       |
| Best for           | Infrequent events | Chat, queues     | Payment, CI/CD    |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Webhooks guarantee delivery" | Webhooks deliver best-effort with retries. Consumers must implement reconciliation polling as a fallback for missed events. |
| "Polling is always bad" | Polling is correct when consumers are behind firewalls, event rate is low, or consumer uptime cannot be guaranteed. |
| "Return 200 then process" | Correct - but the queue you enqueue to must be durable. A crash between 200 ACK and enqueue loses the event. |
| "Webhook retries handle all failures" | Retries stop after N attempts. If your endpoint is down longer than the retry window, events are permanently lost. |
| "Long polling is just slow polling" | Long polling holds the server connection open, allowing near real-time delivery - it has fundamentally different server resource implications. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Polling stampede**

**Symptom:** Server CPU spikes every N seconds as all clients poll simultaneously.

**Root Cause:** All clients initialized with the same interval and no jitter.

**Diagnostic:**
```bash
tail -f /var/log/nginx/access.log \
  | awk '{print $4}' | cut -d: -f2,3 \
  | sort | uniq -c | sort -rn | head -20
```

**Fix:**
```python
# BAD: all clients sleep same interval
time.sleep(30)

# GOOD: add jitter
import random
time.sleep(30 + random.uniform(0, 10))
```

**Prevention:** Add randomized jitter to all polling intervals at initialization.

---

**Failure Mode 2: Webhook delivery backlog**

**Symptom:** Notification latency grows from seconds to minutes during traffic spikes.

**Root Cause:** Shared delivery queue; slow consumers block fast consumers (head-of-line blocking).

**Diagnostic:**
```bash
# Check queue depth per consumer
redis-cli llen webhook_queue:consumer_123
```

**Fix:** Implement per-consumer queues. Isolate slow consumers.

**Prevention:** Monitor per-consumer queue depth; alert on depth > threshold.

---

**Failure Mode 3: Event ordering assumption**

**Symptom:** Order shows "refunded" before "charged" due to out-of-order webhook delivery.

**Root Cause:** Retry for event 2 arrived before original delivery of event 1 succeeded.

**Diagnostic:**
```sql
SELECT event_id, event_timestamp, processed_at
FROM webhook_events
WHERE event_type LIKE 'payment.%'
ORDER BY processed_at;
```

**Fix:** Apply state machine transitions only in valid sequences. Reject invalid transitions.

**Prevention:** Design consumers that reject invalid state transitions rather than assume order.

---

**Failure Mode 4 (Security): Webhook spoofing**

**Symptom:** Fake `payment.completed` events trigger order fulfillment without real payment.

**Root Cause:** Missing HMAC signature verification at the consumer.

**Diagnostic:** Check whether receiver validates `X-Signature-256` before processing any payload.

**Fix:**
```python
# BAD: no verification
@app.route("/webhook")
def webhook():
    process(request.get_json())
    return "ok"

# GOOD: verify HMAC before processing
def verify(body, sig, secret):
    exp = hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={exp}", sig)
```

**Prevention:** Always verify HMAC signatures. Reject unauthenticated requests with 401.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-036 - Push vs Pull Architecture]] - the strategic choice underlying this pattern
- [[SYD-008 - Load Balancing]] - distributing incoming webhook traffic

**Builds On This (learn these next):**
- [[SYD-038 - Idempotency Key]] - essential for safe webhook retry handling
- [[SYD-047 - Notification System Design]] - system design using both patterns
- [[SYD-048 - Chat System Design]] - real-time design where push/poll choice matters

**Alternatives / Comparisons:**
- [[SYD-035 - Fan-Out on Write vs Read]] - event distribution architectural pattern
- [[SYD-036 - Push vs Pull Architecture]] - broader pattern of which this is an instance

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two event notification patterns: │
│              │ consumer-pull vs producer-push   │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Detecting state changes across   │
│ IT SOLVES    │ service boundaries efficiently   │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Polling is simple but wasteful;  │
│              │ webhooks are efficient but       │
│              │ require operational discipline   │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Webhooks: real-time, third-party │
│              │ Polling: firewalls, low rate     │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Webhooks: consumer behind NAT;   │
│              │ Polling: high event rate         │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Efficiency vs operational        │
│              │ simplicity                       │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Polling asks; webhooks tell."   │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-038 Idempotency Key          │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Webhooks are efficient but require idempotent consumers and HMAC verification.
2. Always ACK webhook delivery immediately and process async.
3. Implement reconciliation polling as a fallback for missed events.

**Interview one-liner:** "Polling wastes bandwidth asking; webhooks invert control so the producer pushes on event - the trade-off is consumer operational complexity vs server efficiency."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The party with the most information about *when* something happens should initiate communication. Having uninformed parties poll is systemic waste - invert control to the informed party.

**Where else this pattern appears:**
- **Database CDC:** DB writes emit events (webhook-like) rather than application polling the binlog.
- **CI/CD pipelines:** GitHub webhooks trigger builds on push rather than CI server polling repos every minute.
- **IoT telemetry:** Devices publish sensor changes on event rather than cloud polling millions of devices.

---

### 💡 The Surprising Truth

Webhooks were popularized not because of efficiency but because of a permission constraint: developers integrating with payment providers could not modify the provider's server, so the only way for the provider to notify them was to call their server. The efficiency gains were a second-order benefit. The pattern that scales better (webhooks) was invented to solve an access problem, not a performance problem.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A user signs up on your platform and you fire a `user.created` webhook to five third-party integrations. Two integrations respond in 50ms, two in 3 seconds, and one is completely down. How does the slow or failed integration affect delivery to the fast integrations if you share a single delivery queue?

*Hint:* Look into per-consumer queue isolation strategies and how head-of-line blocking manifests in shared queues at services like Stripe or GitHub webhooks.

**Q2 (Scale):** You serve 10K merchants, each with a webhook endpoint. During a peak event, payment volume spikes 50x for 4 hours. If your webhook queue normally drains in 2 seconds, what depth does it reach during the spike, and what is the notification latency at peak?

*Hint:* Apply Little's Law (L = lambda * W): if delivery rate stays constant but event rate spikes 50x, calculate queue growth per second and resulting notification delay. Then consider how you would scale the worker pool.

**Q3 (Design Trade-off):** GitHub offers both webhooks and a REST API for polling. A security scanner needs to analyze every commit to every repo in a 500-repo organization within 60 seconds of push. What are the failure modes of each approach, and which would you choose?

*Hint:* Explore webhook missed-delivery risk vs polling overhead (500 repos x poll interval), then look at GitHub's webhook reliability SLA and their recommendations for security-critical integrations.
