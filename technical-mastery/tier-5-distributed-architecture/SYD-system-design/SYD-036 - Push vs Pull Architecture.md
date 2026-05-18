---
id: SYD-036
title: Push vs Pull Architecture
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-005
used_by: SYD-037
related: SYD-005, SYD-035, SYD-037, SYD-047
tags:
  - architecture
  - integration-pattern
  - scalability
  - design-tradeoff
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/syd/push-vs-pull-architecture/
---

⚡ TL;DR - Push architecture: a producer sends data
to consumers when it is ready ("server pushes"). Pull
architecture: consumers request data from the producer
when they need it ("client polls"). Push minimizes
latency (instant delivery) but requires the producer
to know all consumers and handle backpressure. Pull
gives consumers control over consumption rate (natural
backpressure) but introduces polling latency and
empty-poll overhead. Most production systems use a
hybrid: push for real-time delivery, pull for high-
throughput batch consumption (e.g., Kafka consumer
groups).

| #036 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAP Theorem and Consistency Models | |
| **Used by:** | Polling vs Webhooks | |
| **Related:** | CAP Theorem, Fan-Out on Write vs Read, Polling vs Webhooks, Notification System Design | |

---

### 🔥 The Problem This Solves

**THE REAL-TIME DATA DELIVERY PROBLEM:**
A stock trading platform needs to deliver price updates
to clients. Updates arrive at 10,000/sec per stock.

**Pure pull (client polls):**
10,000 clients each poll every 100ms → 100K HTTP
requests/sec to the data server. 99% of polls return
"no update" (empty poll). 100K requests/sec wasted.
When a price updates: client sees it at the next poll
interval (up to 100ms stale).

**Pure push (server pushes):**
Server has 10,000 subscribers. On each price update,
push to all 10,000 clients via WebSocket. 10,000/sec ×
10,000 clients = 100M push operations/sec. At 100 bytes
per update: 10 GB/sec. Server must track all 10,000
active client connections. If a client is slow, the
server must buffer or drop updates.

**The right model:** Consumers subscribe (express
interest). Server pushes relevant updates only.
Consumer implements backpressure (tells server to
slow down if overwhelmed). This is the hybrid model.

---

### 📘 Textbook Definition

**Push architecture:** The data producer initiates
data transfer to consumers. When new data is available,
the producer notifies or sends data to consumers without
waiting to be asked. Low latency; requires producer to
know and track consumers; producer controls rate.

**Pull architecture:** Consumers initiate data requests.
Consumers ask the producer for data on a schedule or
when they need it. Consumer controls rate (natural
backpressure); producer does not need to track consumers;
introduces polling latency and potential for empty polls.

**Hybrid / event-driven:** Consumers subscribe (register
interest). System notifies consumers when relevant events
occur (push for notification) but consumers fetch full
data on demand (pull for payload). Common in modern APIs:
webhooks (push notification) + REST (pull for full data).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Push: producer sends when ready (low latency, hard for
producers to scale). Pull: consumer requests when ready
(natural flow control, polling overhead).

**One analogy:**
> Two ways to get your mail:
>
> Push (mail carrier delivers): Letter arrives instantly
> when sent. You don't know when to expect it; it arrives
> when the carrier decides. No effort from you (no polling).
> Carrier must visit every address, even if some people
> moved away.
>
> Pull (post office box): You check your PO box when you
> want mail. You control when you check. Post office just
> stores mail; doesn't track where you live. Empty trip
> if no mail (empty poll). Delay: proportional to how
> often you check.
>
> Most modern systems: push notification ("you have mail")
> + pull to retrieve it.

**One insight:**
Push trades producer complexity (track consumers, handle
slow ones) for consumer simplicity (just receive). Pull
trades consumer complexity (implement polling, handle
empty results) for producer simplicity (just serve). The
right choice depends on which side is more constrained.

---

### 🔩 First Principles Explanation

**COMPARISON ACROSS DIMENSIONS:**

```
DIMENSION          PUSH               PULL
─────────────────────────────────────────────
Latency            Very low (instant) Polling interval
  delay
Backpressure       Hard (producer     Easy (consumer
  controls
                   must slow down     request rate)
                   for slow consumers)
Producer complexity High: track        Low: stateless;
                   consumers, handle  respond to requests
                   connection state
Consumer complexity Low: just receive  Medium: implement
                                      polling loop,
                                      deduplicate
Empty poll waste   None               O(poll_rate) wasted
                                      requests when idle
Scalability        Hard: producer      Easy: add consumers
                   becomes bottleneck  without telling
                     producer
Reliability        Producer must       Consumer retries on
                   retry on consumer  failure; simpler
                   failure             
Consumer offline   Buffer or drop;    Consumer catches up
                   producer must know  when it comes back
                   about offline state (just poll later)
```

**BACKPRESSURE - THE KEY DISTINCTION:**

Pull naturally implements backpressure:
```
Kafka consumer pull:
  Consumer reads 100 messages
  Processes them (takes 1 second)
  Reads next 100 messages
  
If consumer is slow: it reads at its own pace.
Kafka broker holds unread messages (durable).
Consumer lag grows but consumer is not overwhelmed.
Producer keeps writing without knowing consumers are slow.
```

Push must implement backpressure explicitly:
```
Server-Sent Events / WebSocket push:
  Server sends updates as fast as they arrive
  If client is slow: TCP buffer fills up
  OS drops messages or blocks the server
  
Explicit backpressure strategies:
  1. Rate limit push: send at max N messages/sec per client
  2. Batch: buffer and send in batches, not per-event
  3. Acknowledge-based: only push next event after
     consumer ACKs the previous one (slow but safe)
  4. Drop: if client buffer full, drop oldest updates
     (acceptable for live stock tickers, not for orders)
```

**WHEN TO USE EACH:**

```
Use PUSH when:
  - Latency is critical (< 100ms)
  - Real-time delivery required (chat, live scores)
  - Consumer list is bounded and stable
  - Consumer reliability is high
  - Examples: WebSocket for chat, SSE for live feeds,
    mobile push notifications

Use PULL when:
  - Consumers are unreliable or offline-capable
  - Throughput matters more than latency
  - Consumer processing rate is variable
  - Producers should not know consumer state
  - Examples: Kafka consumers, message queue workers,
    REST API polling, email (IMAP)

Use HYBRID (push notify + pull fetch) when:
  - High-volume payloads that cannot be pushed cheaply
  - Webhooks: POST small notification + consumer
    fetches full payload from REST API
  - RSS/Atom: "new posts available" signal (push) +
    feed content fetch (pull)
```

---

### 🧪 Thought Experiment

**SCENARIO: Real-time order book for a crypto exchange**

The order book updates 10,000 times/second.
50,000 trading clients need the latest order book.

**Pure push (WebSocket broadcast):**
10,000 updates/sec × 50,000 clients = 500M push
operations/sec. Each order book snapshot is 10KB.
= 5 TB/sec outbound. Physically impossible.

**Optimization: push diffs only (not full state)**
Push only the change (bid/ask delta) per update.
Avg delta: 100 bytes. 10,000/sec × 50,000 clients
× 100 bytes = 50 GB/sec. Still too expensive.

**Push to interested parties only:**
Clients subscribe to specific trading pairs.
BTC/USD: 10,000 interested clients.
ETH/USD: 5,000 interested clients.
10,000 updates/sec × avg 2,000 subscribers × 100 bytes
= 2 GB/sec. Manageable with horizontal scaling.

**Final design:**
1. WebSocket push: client subscribes to specific pairs
2. Server pushes diffs only (not full snapshot)
3. Client reconstructs full order book from diffs
4. If client misses updates (connection drop): pull
   full snapshot from REST API, then resubscribe to
   diffs

**This is the hybrid pattern:**
- Push for real-time diffs (low latency)
- Pull for full state recovery (snapshot on reconnect)
- Subscription model limits push fanout
- Consumer controls which data it receives

---

### 🧠 Mental Model / Analogy

> TV broadcast vs On-Demand streaming:
>
> Push (broadcast TV): Station pushes the show at
> a scheduled time. Viewers who are available receive
> it. Late viewer misses it. Producer (station) does
> not know individual viewer status.
>
> Pull (Netflix): Viewer requests the show when ready.
> Netflix stores content; serves on demand. Any viewer
> can start at any time. No wasted broadcast to
> unattended TVs.
>
> Push notification + Pull content (hybrid):
> Netflix sends a notification "New season available"
> (push). Viewer decides when to watch (pull the content).
> Both benefits: instant awareness + consumer control.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Push: server sends data to clients automatically.
Pull: clients ask the server for data when they need it.
Most modern systems use both.

**Level 2 - How to use it (junior developer):**
Long polling, WebSockets, SSE = push patterns.
REST GET requests on a schedule = pull (polling).
Webhooks = push with HTTP callback.
Kafka = pull-based message queue (consumers pull from
Kafka broker).

**Level 3 - How it works (mid-level engineer):**
Kafka's pull model is deliberate: consumers poll the
broker at their own rate. This provides natural backpressure
(slow consumer just polls less frequently; broker stores
messages). Push message queues (old RabbitMQ default)
can overwhelm slow consumers. Kafka's pull model is
one of its key operational advantages.

**Level 4 - Why it was designed this way (senior/staff):**
The CAP theorem's consistency-availability tradeoff
manifests in push vs pull differently. A push model
requires the producer to maintain consumer state
(connection, last-sent position, backpressure signals).
If the producer fails, consumer state is lost. A pull
model keeps consumer state at the consumer (or in a
shared log like Kafka). Producer failure is transparent:
consumers start pulling from a different broker replica.
The pull model is inherently more resilient to producer
failures, which is why Kafka, S3, and most durable
data stores use pull semantics.

**Level 5 - Mastery (distinguished engineer):**
The fundamental insight from distributed systems theory:
push requires unbounded buffer at the producer (to handle
slow consumers), while pull requires unbounded buffer
at the consumer (to handle fast producers). In practice,
both push and pull systems bound buffers and must define
what happens when a buffer is full: drop (loss), backpressure
(slowdown), or error. The choice of where to place the
buffer (producer-side vs consumer-side) is the architectural
decision. Modern stream processing (Kafka, Kinesis, Flink)
uses a durable distributed log as the buffer, allowing both
high-throughput producers (push to log) and variable-rate
consumers (pull from log) without coordinating directly.

---

### ⚙️ How It Works (Mechanism)

**Hybrid push-pull pattern:**

```
┌────────────────────────────────────────────────────────┐
│ HYBRID PUSH-PULL (Webhook pattern)                    │
│                                                        │
│ Producer                Consumer                       │
│                                                        │
│ Event occurs:          (subscriber registered)        │
│  → POST /webhook ─────────────────────►              │
│    {"event": "payment.success",                       │
│     "payment_id": "pay_123"}                          │
│                                                        │
│                        Receives notification          │
│                         → GET /payments/pay_123 ─►    │
│                         (pulls full payload)          │
│                                                        │
│ Benefits:                                             │
│  - Push notification: low latency, event-driven       │
│  - Pull for payload: consumer gets only what it needs  │
│  - Producer does not need to send large payloads       │
│    in push (expensive at scale)                       │
│  - Consumer can skip fetch if event is not relevant   │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Pull-based worker (Kafka consumer)**
```python
from kafka import KafkaConsumer
import json

# PULL MODEL: consumer controls its own consumption rate
# Natural backpressure: slow consumer just polls less often
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers=["kafka:9092"],
    group_id="order-processor",
    auto_offset_reset="earliest",
    # Consumer pulls in configurable batches
    max_poll_records=100,         # pull up to 100 at a time
    fetch_min_bytes=1,            # poll as soon as 1 byte ready
    fetch_max_wait_ms=500         # or after 500ms
)

for messages in consumer:
    # Consumer processes at its own pace
    # If processing is slow, Kafka holds messages
    # No overwhelm; no push backpressure needed
    process_order(json.loads(messages.value))
    # Implicit commit: Kafka tracks offset (position)
```

**Example 2 - Push-based delivery (WebSocket)**
```python
# PUSH MODEL: server sends updates as they arrive
# Server must handle backpressure explicitly

import asyncio
import websockets
import json

connected_clients = set()

async def broadcast(message: dict):
    """Push message to all connected clients."""
    if not connected_clients:
        return

    payload = json.dumps(message)
    dead_clients = set()

    for websocket in connected_clients:
        try:
            # push to each connected client
            await asyncio.wait_for(
                websocket.send(payload),
                timeout=5.0  # backpressure: 5s timeout
            )
        except (websockets.ConnectionClosed,
                asyncio.TimeoutError):
            dead_clients.add(websocket)  # slow/dead client

    connected_clients -= dead_clients  # cleanup

async def handle_client(websocket, path):
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.discard(websocket)

# Trade-off: push latency < 1ms per client
# But: server must track ALL connected clients
# At 100K clients: 100K socket state in memory
```

**Example 3 - Hybrid (webhook + REST pull)**
```python
# HYBRID: push notification + pull full payload
# Stripe-style webhook pattern

import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_..."  # from Stripe/GitHub/etc.

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Receive push notification from Stripe."""
    # Verify webhook signature (security check)
    sig = request.headers.get("Stripe-Signature")
    payload = request.data
    
    try:
        # Signature verification prevents spoofing
        event = verify_stripe_signature(
            payload, sig, WEBHOOK_SECRET)
    except ValueError:
        return jsonify({"error": "Invalid signature"}), 400

    # Step 1: Received PUSH notification
    event_type = event["type"]  # "payment_intent.succeeded"
    payment_intent_id = event["data"]["object"]["id"]

    # Step 2: PULL full payment details from Stripe API
    # (Don't trust webhook payload; fetch authoritative copy)
    payment = stripe_client.payment_intents.retrieve(
        payment_intent_id)

    # Process authoritative data from pull
    if event_type == "payment_intent.succeeded":
        fulfill_order(payment)

    return jsonify({"received": True}), 200

# Pattern:
# Push: instant notification with minimal payload
# Pull: fetch authoritative full payload on demand
# Security: verify push; trust pull (from secure API)
```

---

### ⚖️ Comparison Table

| Property | Push | Pull | Hybrid |
|---|---|---|---|
| **Latency** | Minimal (real-time) | Polling interval delay | Notification: low; payload: on-demand |
| **Backpressure** | Complex (producer manages) | Natural (consumer controls rate) | Consumer-controlled |
| **Producer complexity** | High (track consumers, state) | Low (stateless) | Medium |
| **Scalability** | Limited by producer state | Linear (add consumers freely) | Good |
| **Offline consumers** | Buffer or drop | Consumer catches up naturally | Consumer catches up |
| **Implementation** | WebSocket, SSE, webhooks, mobile push | REST polling, Kafka consumer | Webhooks + REST, Kafka + alerts |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Push is always faster than pull | At very short polling intervals (100ms), pull latency approaches push latency. HTTP/2 and long-polling eliminate most of the polling overhead. For many systems, poll-every-100ms is fast enough. |
| Kafka is a push system | Kafka is pull-based. Consumers poll the Kafka broker for new messages. Kafka does not push messages to consumers. This is intentional: consumer-controlled pull provides natural backpressure. |
| WebSockets are always the right choice for real-time | WebSockets require persistent TCP connections, which consume server memory and increase operational complexity. For infrequent updates (< 1/sec), Server-Sent Events (SSE) or long-polling are simpler and more scalable. |

---

### 🚨 Failure Modes & Diagnosis

**Slow Consumer in Push System (Consumer Overwhelm)**

**Symptom:**
A push-based notification service has 10K subscribers.
During a high-traffic event (product launch), the
server pushes 5,000 events/sec. 200 subscribers have
slow mobile connections. Their TCP buffers fill up.
The push server's goroutines (or threads) are blocked
waiting for slow clients. After 10 minutes, the
server is out of goroutines. Healthy subscribers stop
receiving updates (goroutine starvation).

**Root Cause:**
No timeout on individual push operations. Slow consumers
blocked the server's event loop.

**Fix:**
```go
// Go WebSocket push with per-client timeout
func pushToClient(conn *websocket.Conn, msg []byte) error {
    // Set write deadline: drop client if too slow
    deadline := time.Now().Add(5 * time.Second)
    conn.SetWriteDeadline(deadline)
    
    err := conn.WriteMessage(websocket.TextMessage, msg)
    if err != nil {
        // Slow/dead client: remove from subscriber list
        return err
    }
    return nil
}

// Per-client send channel with bounded buffer
// If buffer full: client is too slow; drop or disconnect
type Client struct {
    send chan []byte  // bounded buffer
}

// In broadcast:
select {
case client.send <- message:
    // Queued for client
default:
    // Buffer full: client is overwhelmed
    // Close connection; client will reconnect and catch up
    close(client.send)
    delete(subscribers, client)
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `CAP Theorem and Consistency Models` - consistency
  guarantees differ between push and pull models

**Builds On This (learn these next):**
- `Polling vs Webhooks` - concrete implementation of
  the pull vs push tradeoff for API integrations
- `Notification System Design` - applies push/pull
  to a system design interview scenario

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PUSH           │ Server sends when ready. Low latency.  │
│                │ Producer tracks consumers.             │
│                │ Backpressure: complex.                 │
├────────────────┼────────────────────────────────────────┤
│ PULL           │ Consumer requests when ready.          │
│                │ Natural backpressure. Polling latency. │
│                │ Producer is stateless.                 │
├────────────────┼────────────────────────────────────────┤
│ HYBRID         │ Push notification + pull payload.      │
│                │ Webhooks: POST (push) + GET (pull).    │
├────────────────┼────────────────────────────────────────┤
│ KAFKA          │ Pull model (consumer polls broker).    │
│                │ Backpressure natural.                  │
├────────────────┼────────────────────────────────────────┤
│ WEBSOCKET      │ Push model (server sends to client).   │
│                │ Must handle slow consumers with timeout│
├────────────────┼────────────────────────────────────────┤
│ CHOOSE PUSH    │ Real-time required, bounded consumers, │
│                │ low-throughput steady stream           │
├────────────────┼────────────────────────────────────────┤
│ CHOOSE PULL    │ Variable consumer rate, high throughput│
│                │ unreliable consumers, durable delivery │
├────────────────┼────────────────────────────────────────┤
│ ONE-LINER      │ "Push = instant but complex.           │
│                │  Pull = controlled but latency.        │
│                │  Hybrid = notification + on-demand."   │
├────────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE   │ Polling vs Webhooks                    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Push gives low latency; pull gives flow control.
   Push requires producer to track consumers (stateful).
   Pull allows consumers to be added without producer
   knowing (stateless producer).
2. Kafka is pull. Consumer polls at its own rate. This
   is the source of Kafka's natural backpressure.
3. Hybrid (push notification + pull payload) is the
   most pragmatic: push for instant awareness, pull for
   the full payload on demand. Used by Stripe, GitHub,
   and most modern webhook APIs.

**Interview one-liner:**
"Push architecture: producer sends data immediately when available -
low latency but requires tracking all consumers and handling
backpressure explicitly. Pull architecture: consumers request data
on demand - natural backpressure (consumer controls rate), stateless
producer, but introduces polling latency and empty-poll waste.
Kafka is pull-based by design: consumers poll the broker at their
own rate, providing natural backpressure. WebSockets are push-based:
server sends in real-time, but requires handling slow consumers
with timeouts. The hybrid pattern (push notification + pull payload)
combines both: a push notification tells the consumer something is
ready, and the consumer pulls the full payload - used by Stripe
webhooks and GitHub events."
