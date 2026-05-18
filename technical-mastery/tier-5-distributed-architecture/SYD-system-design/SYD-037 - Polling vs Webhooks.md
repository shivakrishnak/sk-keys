---
id: SYD-037
title: Polling vs Webhooks
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-036
used_by: ""
related: SYD-028, SYD-036, SYD-047
tags:
  - architecture
  - integration-pattern
  - api-design
  - intermediate
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/syd/polling-vs-webhooks/
---

⚡ TL;DR - Polling: client repeatedly asks a server
"any updates?" at intervals. Webhooks: server sends
an HTTP POST to a pre-registered URL when an event
occurs. Polling is simple but wastes resources on
empty responses. Webhooks are event-driven and
efficient but require the client to expose an HTTPS
endpoint and handle delivery failures. Webhooks are
the standard for event-driven B2B integrations
(Stripe, GitHub, Twilio); polling is still used where
webhooks are impractical (behind firewalls, simple
integrations, or where eventual consistency is acceptable).

| #037 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Push vs Pull Architecture | |
| **Used by:** | (Notification System Design) | |
| **Related:** | Rate Limiting (System), Push vs Pull Architecture, Notification System Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT WEBHOOKS:**
A payment processor (Stripe) processes a card payment.
The merchant's server needs to know if the payment
succeeded. With polling:
```
t=0: payment submitted
t=1: GET /payments/pay_123 → status: pending
t=2: GET /payments/pay_123 → status: pending
t=3: GET /payments/pay_123 → status: succeeded
```
3 API calls for 1 event. At 1M payments/day, that's
3M polling requests, 2M of which return "pending."
At Stripe scale (millions of merchants × millions of
payments): billions of wasted polling requests per day.

**WITH WEBHOOKS:**
Stripe sends POST to `merchant.com/webhook` when
payment succeeds. 1 HTTP request per event. No
waste. Merchant server reacts instantly.

---

### 📘 Textbook Definition

**Polling:** A client periodically sends requests to
a server at fixed intervals to check for new data or
status changes. Simple to implement; works through
firewalls; stateless server. Costs: wasted empty
requests; higher latency (up to one polling interval).

**Webhooks:** An event-driven callback mechanism where
a server sends an HTTP POST to a client's registered
URL when a specific event occurs. Also called "reverse
API" or "HTTP callback." Efficient (one request per
event); low latency; but requires the client to:
(1) expose a public HTTPS endpoint, (2) handle
authentication/signature verification, (3) respond
quickly (within timeout), (4) implement idempotency
(webhooks may be retried on failure).

**Long polling:** A hybrid - client sends a request
and the server holds it open until new data is available
or a timeout occurs, then responds. Reduces empty polls;
lower latency than fixed-interval polling. More complex
than simple polling but does not require a public
client endpoint (unlike webhooks).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Polling: "Are we there yet?" every N seconds.
Webhook: "We've arrived!" sent once when it happens.

**One analogy:**
> Waiting for a package:
>
> Polling: call UPS every 30 minutes asking "has my
> package arrived?" 10 calls, 9 of which say "not yet."
>
> Webhook: give UPS your phone number; they text you
> when the package arrives. 1 notification, zero wasted
> calls. But: your phone must be on (public endpoint).
>
> Long polling: stay on hold with UPS until they have
> news. One call, immediate answer when ready.

**One insight:**
Webhooks invert the request direction. Instead of "client
asks server," it becomes "server tells client." This is
more efficient for event-driven integrations but shifts
responsibility to the client: it must be accessible,
available, and idempotent.

---

### 🔩 First Principles Explanation

**POLLING CHARACTERISTICS:**

```
Simple polling:
  loop:
    response = GET /api/resource/status
    if response.status == "done":
      process(response)
      break
    sleep(poll_interval)

Pros:
  Simple to implement
  Works through firewalls (client initiates)
  Server is stateless (no subscriber list)
  No need for public client endpoint
  Natural retry (just poll again)
  
Cons:
  Latency = up to poll_interval
  Empty requests: (total_time / poll_interval) - 1
  Server load proportional to (clients × poll_rate)
  Must tune poll_interval:
    Too short: wasted requests
    Too long: high latency

Exponential backoff polling (better):
  interval = 1 second
  loop:
    response = GET /api/status
    if done: break
    sleep(min(interval, 60))  # cap at 60s
    interval = interval * 2
  
  Reduces wasted requests while still checking
```

**WEBHOOK CHARACTERISTICS:**

```
Webhook flow:
  1. Client registers endpoint: POST /webhooks
     {"url": "https://merchant.com/stripe-hook",
      "events": ["payment.succeeded", "charge.failed"]}
  2. Stripe stores {url, events, secret}
  3. Event occurs → Stripe POSTs to registered URL

Pros:
  1 HTTP call per event (no empty polls)
  Low latency (near-real-time delivery)
  Server does not need to maintain client state
    between events (just deliver when event occurs)

Cons:
  Client must expose HTTPS endpoint (no firewall)
  Client must handle retries (webhook may be re-sent
    if client returns non-2xx)
  Idempotency required (same event may arrive 2x)
  Signature verification required (security)
  Client must respond < 30 seconds (timeout)
  Debugging harder (no request log at client side)

SECURITY: Webhook Signature Verification (non-optional):
  // Stripe: X-Stripe-Signature header
  // GitHub: X-Hub-Signature-256 header
  // Verify: HMAC-SHA256(payload, secret) == signature
  // Prevents spoofed webhooks from arbitrary senders
```

**IDEMPOTENCY IN WEBHOOKS:**

```
Webhook retry scenario:
  Stripe sends POST → merchant ACKs (200 OK)
  Network drops the ACK → Stripe doesn't see 200
  Stripe retries: sends same webhook again
  Merchant processes payment twice: DOUBLE CHARGE

Idempotent webhook handler:
  Extract event_id from payload
  Check: have we seen this event_id before?
  If yes: return 200 (already processed; no-op)
  If no:  process, store event_id, return 200

Event ID is the idempotency key.
```

---

### 🧪 Thought Experiment

**SCENARIO: GitHub Actions notifying a CI/CD system**

A CI/CD system needs to trigger a build when a new
commit is pushed to GitHub. Options:

**Option A: Polling**
Poll GitHub API: `GET /repos/org/repo/commits`
every 60 seconds. At 1,000 repos × 60/sec = 1,000
API calls/min. GitHub's API rate limit: 5,000 calls/hour.
60K polls/hour exceeds limits. Polling GitHub is
impractical at scale. Also: 60-second build trigger
latency is unacceptable for fast CI.

**Option B: Webhooks (GitHub's actual design)**
Register webhook on repo. GitHub POSTs `push` event
to `ci-server.com/github-hook` within seconds of push.
Build triggers in < 2 seconds. Zero wasted API calls.
Scales to 1M repos without increasing CI server polling load.

**Consideration: Firewall**
If the CI system is behind a corporate firewall
(no public URL), webhooks won't work. Solution:
GitHub Action webhook → public relay service →
internal CI system (proxied ingress). Or: GitHub
Actions hosted runners that GitHub initiates (hybrid:
GitHub manages the endpoint, not the customer).

**THE LESSON:**
Webhooks are the correct pattern for event-driven
integrations between systems where both have public
endpoints. Polling is the fallback when the consumer
cannot expose a public endpoint or when simple
eventual consistency (a few minutes) is acceptable.

---

### 🧠 Mental Model / Analogy

> Polling vs Webhooks is like two ways a teacher
> returns exam results:
>
> Polling: Students check the school portal every day.
> "Is the result posted?" Most checks: no. One day:
> yes. Low tech, simple for the teacher, but students
> do repeated unnecessary work.
>
> Webhook (email notification): Teacher posts results
> and emails every student. Students receive instant
> notification. Students do zero wasted checking.
> But: teacher must have all students' email addresses
> (registered endpoints) and must handle bounced emails
> (webhook failure + retry).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Polling: keep asking for updates. Webhooks: get
notified automatically when something happens.
Webhooks are more efficient but more complex to set up.

**Level 2 - How to use it (junior developer):**
Register a webhook URL with the external service
(Stripe, GitHub, Twilio). Implement an endpoint at
that URL that accepts POST requests. Verify the
signature. Respond within 10-30 seconds with 200 OK.
Store the event_id to implement idempotency.

**Level 3 - How it works (mid-level engineer):**
Webhook reliability: external service retries on
non-2xx or timeout. Implement the endpoint to return
200 immediately and process asynchronously (queue the
event, return 200, process in background). If you
process synchronously and your handler is slow, the
retries will pile up.

**Level 4 - Why it was designed this way (senior/staff):**
Webhooks with HMAC signature verification create a
trust model without shared credentials: the client
pre-registers a secret with the server. The server
HMAC-signs each webhook payload. The client verifies
the signature using the same secret. Neither party
needs to authenticate themselves with OAuth tokens
on each request. This is a simpler and more efficient
trust model for event delivery than mutual TLS or
API key per request.

**Level 5 - Mastery (distinguished engineer):**
The webhook delivery guarantee is "at-least-once"
in most implementations (Stripe, GitHub, Twilio):
they retry until they receive a 200. The consumer
must be idempotent. Some systems offer "exactly-once"
by using event_id deduplication on both ends, but
this requires a persistent deduplication store. For
high-volume webhook consumers (millions of events/day),
the idempotency check (lookup event_id in a Redis set
or DB) can itself become a bottleneck. The production
solution: batch accept events into a Kafka topic
(O(1) per event), run deduplication and processing
from Kafka downstream (separate concern from acceptance).

---

### ⚙️ How It Works (Mechanism)

**Webhook delivery with retry:**

```
┌──────────────────────────────────────────────────────┐
│ WEBHOOK DELIVERY FLOW (Stripe pattern)              │
│                                                      │
│  Event:    payment.succeeded for pay_123            │
│                                                      │
│  Attempt 1: POST merchant.com/webhook               │
│    Timeout: 30 seconds                              │
│    Response: 200 OK → Success, done                 │
│                                                      │
│  If 500 or timeout:                                 │
│  Attempt 2: POST (after 5 minutes)                  │
│  Attempt 3: POST (after 30 minutes)                 │
│  Attempt 4: POST (after 2 hours)                    │
│  ...                                                 │
│  Attempt N: POST (after 3 days) → give up           │
│                                                      │
│  CRITICAL: Each attempt has same webhook payload.   │
│  Consumer MUST be idempotent (event_id check).      │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Secure webhook receiver (Python/Flask)**
```python
import hmac
import hashlib
import json
from flask import Flask, request, jsonify
import redis

app = Flask(__name__)
STRIPE_SECRET = "whsec_your_secret_here"
r = redis.Redis(host="redis", port=6379)

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    """Stripe webhook receiver with all safety checks."""
    
    # 1. Signature verification (security - non-optional)
    sig_header = request.headers.get("Stripe-Signature")
    payload = request.data  # raw bytes

    if not verify_stripe_signature(payload, sig_header):
        return jsonify({"error": "Invalid signature"}), 400

    event = json.loads(payload)
    event_id = event["id"]  # e.g. "evt_abc123"

    # 2. Idempotency check (prevent double-processing)
    if r.sismember("processed_webhook_ids", event_id):
        return jsonify({"status": "already processed"}), 200

    # 3. Return 200 FAST; process asynchronously
    # Do NOT process inline (risk: timeout → retry loop)
    queue_for_processing(event)
    r.sadd("processed_webhook_ids", event_id)
    r.expire("processed_webhook_ids", 86400 * 7)  # 7-day TTL

    return jsonify({"received": True}), 200

def verify_stripe_signature(payload: bytes,
                              sig_header: str) -> bool:
    """HMAC-SHA256 verification of Stripe signature."""
    try:
        timestamp, signatures = parse_stripe_sig(sig_header)
        expected = hmac.new(
            STRIPE_SECRET.encode(),
            f"{timestamp}.{payload.decode()}".encode(),
            hashlib.sha256
        ).hexdigest()
        return any(s == expected for s in signatures)
    except Exception:
        return False
```

**Example 2 - BAD: Polling vs GOOD: Webhook**
```python
# BAD: Polling for payment status
# Wastes API calls; adds latency; hits rate limits

def wait_for_payment_BAD(payment_id: str) -> str:
    """Poll until payment completes. Anti-pattern."""
    max_attempts = 30
    for attempt in range(max_attempts):
        resp = stripe.PaymentIntent.retrieve(payment_id)
        if resp.status in ["succeeded", "canceled"]:
            return resp.status
        time.sleep(10)  # Poll every 10 seconds
    # 30 attempts × 10s = 5 minutes; 30 API calls wasted
    raise TimeoutError("Payment did not complete in time")

# GOOD: Webhook-driven (event-based)
# 1. Submit payment intent; return to client immediately
# 2. Stripe POSTs webhook when status changes
# 3. Process webhook; fulfill order

@app.route("/create-payment", methods=["POST"])
def create_payment():
    """Create payment intent and return client secret."""
    intent = stripe.PaymentIntent.create(
        amount=2000,
        currency="usd"
    )
    # Return client_secret to frontend for payment UI
    # Stripe will POST webhook when payment completes
    return jsonify({"client_secret": intent.client_secret})

# Webhook handler (see Example 1) fulfills order
# Zero polling; instant event delivery
```

**Example 3 - Long polling as alternative**
```python
# Long polling: client waits up to N seconds for update
# Server holds request open until data is available
# No public endpoint required (works through firewalls)

@app.route("/events/poll", methods=["GET"])
def long_poll():
    """
    Long polling endpoint.
    Waits up to 30 seconds for an event.
    Client calls this in a loop.
    """
    last_event_id = request.args.get("last_event_id")
    timeout = 30  # seconds

    start = time.time()
    while time.time() - start < timeout:
        # Check if new event available since last_event_id
        event = get_next_event(after=last_event_id)
        if event:
            return jsonify(event)
        time.sleep(0.5)  # check every 500ms

    # Timeout: return empty response; client retries
    return jsonify({"events": []}), 200

# Client:
def poll_events(last_event_id):
    while True:
        response = requests.get(
            "/events/poll",
            params={"last_event_id": last_event_id},
            timeout=35  # > server timeout
        )
        events = response.json()
        if events:
            process(events)
            last_event_id = events[-1]["id"]
        # If empty response: timeout reached; retry immediately
```

---

### ⚖️ Comparison Table

| Property | Polling | Webhooks | Long Polling |
|---|---|---|---|
| **Latency** | Up to poll_interval | Near-real-time | Near-real-time |
| **Empty requests** | Many | None | Fewer (1 per event or timeout) |
| **Public endpoint needed** | No | Yes | No |
| **Works through firewall** | Yes | No | Yes |
| **Implementation** | Simple | Medium (signature, idempotency) | Medium |
| **Reliability** | Client retries | Server retries + idempotency | Client retries |
| **Best for** | Simple status checks, slow-changing data | Event-driven B2B integrations | Real-time without public endpoint |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Webhooks are guaranteed delivery | Webhooks are "at-least-once": the sender retries on failure. Consumers must implement idempotency (event_id deduplication) to handle duplicate delivery. |
| Polling is always inefficient | For low-frequency events (once/hour), polling at 5-minute intervals produces only 12 empty polls per event - perfectly acceptable. Webhooks are overkill for slow-changing data. |
| Webhooks eliminate the need for any polling | Webhooks can fail permanently (endpoint down for days). A "reconciliation job" that polls the source of truth periodically (daily or hourly) is standard practice alongside webhooks to catch missed events. |

---

### 🚨 Failure Modes & Diagnosis

**Webhook Retry Storm**

**Symptom:**
The merchant's webhook endpoint was down for 2 hours
(deployment issue). When it came back up, Stripe
delivered all 20,000 queued webhooks simultaneously.
The endpoint was overwhelmed with 2,000 req/sec
for 10 seconds.

**Root Cause:**
Delayed retries all arrived together. No rate limiting
on the webhook receiver.

**Fix:**
```python
# Rate limit the webhook endpoint itself
# Stripe sends at a natural rate, but add protection

@app.route("/webhook", methods=["POST"])
@rate_limit(max_per_second=100)  # accept max 100/sec
def webhook():
    # Queue for async processing
    # Return 200 immediately (prevents retry cascade)
    event = request.json
    task_queue.enqueue(process_webhook, event)
    return jsonify({"received": True}), 200

# Do NOT block on processing in the webhook handler
# The 30s timeout + slow processing = retry storm
# Queue + return 200 immediately = safe

# Reconciliation job (safety net for missed webhooks):
def daily_reconciliation():
    """Catch any webhooks missed during downtime."""
    last_24h_payments = stripe.PaymentIntent.list(
        created={"gte": int(time.time()) - 86400}
    )
    for payment in last_24h_payments.auto_paging_iter():
        if payment.status == "succeeded":
            if not is_fulfilled(payment.id):
                fulfill_order(payment.id)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Push vs Pull Architecture` - webhooks are push;
  polling is pull; this entry is the concrete API-level
  instantiation of that broader concept

**Builds On This (learn these next):**
- `Notification System Design` - applies webhooks
  and polling decisions in a full system design

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ POLLING       │ Client asks periodically. Simple,       │
│               │ firewall-friendly. Empty polls = waste. │
├───────────────┼─────────────────────────────────────────┤
│ WEBHOOKS      │ Server POST to client on event.         │
│               │ Efficient, event-driven. Needs HTTPS    │
│               │ endpoint + idempotency + signature verif│
├───────────────┼─────────────────────────────────────────┤
│ LONG POLLING  │ Hold request open. Less empty polls.    │
│               │ No public endpoint needed.              │
├───────────────┼─────────────────────────────────────────┤
│ WEBHOOK RULES │ 1. Verify signature (HMAC-SHA256)       │
│               │ 2. Return 200 fast; process async       │
│               │ 3. Deduplicate by event_id              │
│               │ 4. Add reconciliation job as fallback   │
├───────────────┼─────────────────────────────────────────┤
│ CHOOSE POLL   │ Behind firewall, simple status check,   │
│               │ low-frequency events, no public endpoint│
├───────────────┼─────────────────────────────────────────┤
│ CHOOSE WEBHOOK│ Real-time event delivery, B2B integratio│
│               │ high-volume events, Stripe/GitHub/Twilio│
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Poll = ask repeatedly.                 │
│               │  Webhook = be told immediately.         │
│               │  Both need idempotency."                │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Idempotency Key → Distributed Locks     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Webhooks: server POSTs to client on event. 1 request
   per event (no waste). Need public HTTPS endpoint,
   signature verification, and idempotency.
2. Polling: client asks at intervals. Works behind
   firewalls; no setup on server side. Wasteful for
   high-frequency events.
3. Production webhook pattern: verify signature →
   return 200 immediately → process async → deduplicate
   by event_id. Plus: daily reconciliation job as safety
   net for missed events.

**Interview one-liner:**
"Polling has the client repeatedly ask 'any updates?' at intervals -
simple, firewall-friendly, but generates empty requests proportional
to (clients × poll_rate). Webhooks invert this: the server POSTs
to a registered endpoint when an event occurs - efficient (one
request per event), but requires the client to expose a public HTTPS
endpoint and implement three things: signature verification (HMAC-SHA256
to prevent spoofed webhooks), idempotency (event_id deduplication since
webhooks can be retried), and return 200 immediately then process async
(to avoid timeout-triggered retry storms). Long polling is a middle ground:
client sends a request and server holds it until data is available,
reducing empty polls without requiring a public endpoint."
