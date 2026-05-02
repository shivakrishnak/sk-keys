---
layout: default
title: "Webhook"
parent: "HTTP & APIs"
nav_order: 230
permalink: /http-apis/webhook/
number: "0230"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, REST, HTTPS
used_by: Payment Processing, CI/CD, SaaS Integrations, Event Notifications
related: API Polling, Event-Driven Architecture, API Gateway, HMAC
tags:
  - api
  - webhook
  - event-driven
  - integration
  - intermediate
---

# 230 — Webhook

⚡ TL;DR — A webhook is a user-defined HTTP callback that a service calls to notify your application when an event occurs; instead of your app polling "did anything happen?", the sender POSTs event data to your URL the moment it does — reversing the traditional request/response direction.

┌──────────────────────────────────────────────────────────────────────────┐
│ #230 │ Category: HTTP & APIs │ Difficulty: ★★☆ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ HTTP, REST, HTTPS │ │
│ Used by: │ Payments, CI/CD, SaaS, Notifs │ │
│ Related: │ API Polling, EDA, API Gateway, HMAC│ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your e-commerce app needs to know the moment Stripe processes a payment. You could
poll `GET /charges/{id}` every second — but you won't know the payment ID until after
checkout, and Stripe would block your API key after thousands of polling requests.
Alternatively, the user could sit looking at a spinner while your backend waits for
the payment to clear synchronously. For async operations (payment processing, repo
events, order fulfillment, document conversion), there's no clean way for external
services to tell you "it's done" using regular HTTP.

**THE INVENTION MOMENT:**
The solution: reverse the arrow. You don't call them; they call you. Register a
URL with the external service. When the event you care about happens, the service
sends a POST request to your URL with the event data. You get notified within
milliseconds of the event occurring — no polling, no waiting. This is called a
webhook: "hook into" the external system's event stream using HTTP ("web"). Stripe,
GitHub, Shopify, Twilio, and virtually every SaaS platform with an API uses webhooks
as the primary mechanism for event delivery.

---

### 📘 Textbook Definition

A **webhook** is a pattern where an application registers a publicly accessible HTTP
endpoint with an external service; the service makes an HTTP POST request to that
endpoint when a specified event occurs, delivering event data as the request body
(typically JSON). Webhooks are also called "reverse APIs" or "push APIs" — rather
than a consumer polling a provider for state changes (pull), the provider pushes an
event to the consumer at the moment it occurs. Webhook implementations typically
include: a registration mechanism (storing the consumer's URL), an event selection
mechanism (which events to deliver), a delivery guarantee mechanism (retries on
failure), and a verification mechanism (HMAC signature to prove authenticity).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Webhooks flip REST: instead of you calling them repeatedly to ask "did anything
change?", they call you once the moment something changes.

**One analogy:**

> Traditional API polling: you drive to the post office every hour asking "is
> there a package for me?" Webhook: you give the delivery person your home address.
> They show up at your door when the package arrives. Same outcome, radically
> different resource usage.

**One insight:**
The key insight is about who initiates communication. REST APIs are always
consumer-initiated. Webhooks are provider-initiated. This makes webhooks ideal
for events the provider detects (payment cleared, repo pushed, order shipped)
where the consumer can't efficiently poll for them.

---

### 🔩 First Principles Explanation

**THE THREE ACTORS:**

```
1. PROVIDER — the service that generates events (Stripe, GitHub, Shopify)
   - Stores registered webhook URLs
   - Detects events internally
   - POSTs event data to registered URLs when events fire

2. CONSUMER — your application
   - Registers a webhook URL with the provider
   - Exposes an HTTPS endpoint to receive webhook payloads
   - Verifies signature, processes event, returns 2xx quickly

3. WEBHOOK ENDPOINT — the specific URL in your application
   - Must return 2xx within a short timeout (Stripe: 30s, GitHub: 10s)
   - Must be idempotent (retried on failure)
   - Should do minimal work synchronously; defer to a queue
```

**DELIVERY SEMANTICS:**

```
Most providers guarantee at-least-once delivery:
  - If your endpoint returns non-2xx or times out → retry
  - Stripes retries up to 24+ hours with exponential backoff
  - Same event may be delivered multiple times → you must deduplicate

Providers do NOT guarantee exactly-once delivery:
  - Duplicate webhook events are normal
  - Use idempotency keys (event IDs) to handle duplicates
  - Store processed event IDs in your database with a unique constraint
```

**VERIFICATION:**

```
Anyone on the internet can POST to your webhook URL.
How do you know it's really from Stripe?

HMAC-SHA256 signature:
  1. Stripe generates: HMAC_SHA256(timestamp + "." + body, webhook_secret)
  2. Stripe sends: Stripe-Signature: t=1630000000,v1=<signature>
  3. You verify: compute HMAC yourself, compare → reject if mismatch
  4. Also check: |now - t| < 5 minutes → prevent replay attacks
```

---

### 🧪 Thought Experiment

**SCENARIO:** Payment webhook delivery failures.
Stripe POST to your webhook URL returns 500 (your DB was down for 2 minutes).
Stripe retries on a schedule. Your DB comes back up at retry #3.

```
t=0:00   Payment completes at Stripe
t=0:00   Stripe POSTs to your /webhook → 500 (DB down)
t=0:05   Stripe retry #1 → 500 (DB still down)
t=1:00   Stripe retry #2 → 500 (DB still down)
t=2:00   Stripe retry #3 → 200 ✓ (DB back up) — event processed, order fulfilled
t=2:01   Stripe retry #4 → but already queued? Stripe doesn't wait for outcome of #3
t=2:02   Stripe POSTs AGAIN (retry #4) → 200 ✓ — but event already processed!

If your handler is NOT idempotent:
  Order fulfilled TWICE, charge applied twice → disaster

If your handler IS idempotent:
  SELECT... WHERE stripe_event_id = 'evt_xyz' → already processed → skip → 200
  → Correct behavior regardless of delivery duplicates
```

**LESSON:** At-least-once delivery makes idempotency non-optional.

---

### 🧠 Mental Model / Analogy

> Webhooks are like a fire alarm notification service.
> You subscribe (register your webhook URL).
> You specify which events you care about ("payment.succeeded", not "payment.failed").
> When the event fires, you're immediately notified (POST to your URL).
> You don't have to keep checking if there's been a fire.
>
> The subtlety: the alarm system may call you twice for the same fire (at-least-once
> delivery). You need to handle that gracefully — check if you've already sent the
> fire trucks before dispatching them again.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of your app constantly asking "has anything changed?", you tell the service "call THIS URL when something happens." The service does the asking — to your URL, the moment the event occurs.

**Level 2 — How to use it (junior developer):**
Register a HTTPS URL with the provider. Build an endpoint to accept POST requests.
Parse the JSON body. Return 200 quickly. Verify the signature header. Store event in
a queue or DB. Process asynchronously. Use the webhook's event ID as an idempotency key.

**Level 3 — How it works (mid-level engineer):**
The provider stores your webhook URL. On event occurrence, the provider serializes the
event to JSON, signs it (HMAC-SHA256), and makes an HTTP POST to each registered URL
for that event type. If your server doesn't return 2xx within the timeout period, the
provider retries with exponential backoff. Your endpoint receives the event, verifies
the signature, optionally saves the raw payload, and queues the work for background
processing. This two-phase approach (quick ACK → async process) prevents timeout
failures under load spikes and makes your handler resilient.

**Level 4 — Why it was designed this way (senior/staff):**
Webhooks solve a fundamental problem in distributed systems: how do you get event
notifications across organizational and network boundaries using only HTTP? The webhook
pattern makes the receiver responsible for hosting a publicly accessible endpoint —
this shifts complexity to the consumer but keeps the provider simple (just HTTP POST).
The HMAC signature is a clever use of shared secrets at the application layer: both
parties hold the same secret, neither party needs TLS client certificates or OAuth
tokens for webhook-to-webhook auth. The payload-timestamp inclusion in the HMAC
signature prevents replay attacks (old signed payloads can't be re-submitted). When
building a webhook system as a provider, you must design for: fan-out (one event to N
webhooks), retry semantics, dead-letter handling, delivery ordering (usually not
guaranteed), and back-pressure (what to do if a consumer's endpoint is slow).

---

### ⚙️ How It Works (Mechanism)

```
WEBHOOK DELIVERY LIFECYCLE:

1. REGISTRATION
   Developer registers URL at provider's dashboard:
   POST https://api.stripe.com/v1/webhook_endpoints
   { url: "https://your-app.com/webhooks/stripe",
     enabled_events: ["payment_intent.succeeded"] }

2. EVENT OCCURS AT PROVIDER
   Stripe payment clears → internal event bus fires
   Webhook dispatcher: look up registered URLs for "payment_intent.succeeded"
   For each registered URL: enqueue delivery job

3. DELIVERY
   POST https://your-app.com/webhooks/stripe
   Headers:
     Content-Type: application/json
     Stripe-Signature: t=1630000000,v1=abc123def...
   Body: { "id": "evt_xyz", "type": "payment_intent.succeeded",
           "created": 1630000000,
           "data": { "object": { "id": "pi_abc", "amount": 2000 }}}

4. YOUR HANDLER
   Verify signature → parse event → deduplicate → queue work → return 200

5. RETRY ON FAILURE
   Non-2xx or timeout → retry with exponential backoff → up to provider's limit
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Customer pays on Stripe checkout:

Stripe → internal event "payment_intent.succeeded" fires
     ↓
Stripe webhook dispatcher: find registered endpoints for event
     ↓
HTTP POST to your /webhooks/stripe (with HMAC signature)
     ↓
Your endpoint:
  [1] Verify Stripe-Signature → reject if invalid
  [2] Check DB: WHERE stripe_event_id = 'evt_xyz' → exists? Skip.
  [3] INSERT into webhook_events (idempotent insert)
  [4] Publish "order.fulfill" to internal queue → return 200 immediately
     ↓
Background worker processes order fulfillment asynchronously
     ↓
Customer sees order confirmed; warehouse receives pick request
```

---

### 💻 Code Example

```java
// Spring Boot webhook endpoint with HMAC verification
@RestController
public class StripeWebhookController {

    private final String webhookSecret = System.getenv("STRIPE_WEBHOOK_SECRET");

    @PostMapping("/webhooks/stripe")
    public ResponseEntity<Void> receive(
            HttpServletRequest request,
            @RequestHeader("Stripe-Signature") String sigHeader,
            @RequestBody String payload) {

        // Step 1: Verify HMAC signature (prevents spoofed webhooks)
        if (!isValidSignature(payload, sigHeader, webhookSecret)) {
            return ResponseEntity.status(401).build();
        }

        // Step 2: Parse event
        StripeEvent event = parseEvent(payload);

        // Step 3: Deduplicate (idempotency)
        if (eventRepository.existsByStripeEventId(event.getId())) {
            return ResponseEntity.ok().build(); // Already processed
        }

        // Step 4: Store event atomically + enqueue (transactional outbox)
        try {
            eventRepository.insertAndPublish(event); // TX: INSERT + queue message
        } catch (DataIntegrityViolationException e) {
            // Race condition — another instance already inserted
            return ResponseEntity.ok().build();
        }

        // Step 5: Return 200 FAST — do not do heavy work here
        return ResponseEntity.ok().build();
    }

    private boolean isValidSignature(String payload, String sigHeader, String secret) {
        // Parse: "t=1630000000,v1=abc123..."
        long timestamp = extractTimestamp(sigHeader);
        String expectedSig = extractSig(sigHeader);

        // Reject stale webhooks (prevents replay attacks)
        if (Math.abs(Instant.now().getEpochSecond() - timestamp) > 300) {
            return false;
        }

        // Compute HMAC: HMAC-SHA256(timestamp + "." + payload, secret)
        String computed = computeHmac(timestamp + "." + payload, secret);
        return MessageDigest.isEqual(
            computed.getBytes(StandardCharsets.UTF_8),
            expectedSig.getBytes(StandardCharsets.UTF_8)
        );
    }
}
```

---

### ⚖️ Comparison Table

| Pattern       | Direction           | Latency             | Complexity | Best For                            |
| ------------- | ------------------- | ------------------- | ---------- | ----------------------------------- |
| **Polling**   | Consumer → Provider | Up to interval      | Low        | Simple, low-rate changes            |
| **Webhook**   | Provider → Consumer | ~0ms (event-driven) | Medium     | Event notifications across services |
| **SSE**       | Provider → Consumer | ~0ms                | Low        | Same-origin streaming               |
| **WebSocket** | Bidirectional       | ~0ms                | High       | Interactive bidirectional real-time |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                       |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Webhooks guarantee exactly-once delivery                   | Most providers guarantee at-least-once — design for duplicates with idempotency keys                                          |
| Webhook URL must be publicly accessible on the internet    | Yes, always — or you need a tunnel (ngrok/localtunnel) for local development                                                  |
| Webhooks are secure by default because they use HTTPS      | HTTPS encrypts the channel but doesn't prove identity — HMAC signature verification is required                               |
| You can do heavy work synchronously in the webhook handler | No — return 200 quickly, defer heavy work. Slow handlers time out; the provider retries; load spikes cause cascading failures |

---

### 🚨 Failure Modes & Diagnosis

**Silent Event Loss from Unhandled Retries**

Symptom:
Some orders never get fulfilled. No errors in your logs. Stripe dashboard shows
"webhook failed" after 72 hours for some events.

Root Cause:
Your webhook endpoint was timing out (taking 31+ seconds) under load. Stripe
retried but your server was still overloaded. After max retries, events were
abandoned. No alerting on Stripe's failed webhook dashboard.

Diagnostic Command:

```
# Stripe dashboard: Developers → Webhooks → Failed webhooks
# Your app: query for events that are in "queued" state older than 5min
SELECT * FROM webhook_events
WHERE state = 'queued' AND created_at < NOW() - INTERVAL '5 minutes';

# Fix: reduce handler sync time to <500ms
# Fix: alert on Stripe webhook failure email
# Fix: implement manual retry API for failed events
```

Prevention:
Load test the webhook endpoint. Return 200 within 100ms. Process async.
Set up alerting on provider's webhook failure dashboard.

---

### 🔗 Related Keywords

- `HMAC` — the signature scheme used to verify webhook authenticity
- `API Gateway` — can sit in front of webhook endpoints for rate limiting and routing
- `Idempotency` — the property required to handle webhook duplicate delivery safely
- `Event-Driven Architecture` — webhooks are a simple form of event notification across service boundaries

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Provider POSTs event to your URL when    │
│              │ event occurs — "reverse REST"             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Real-time notification without polling:   │
│ SOLVES       │ payment cleared, repo pushed, order done  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Flip who initiates the HTTP call —        │
│              │ provider calls consumer, not vice versa   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ External service needs to notify your app │
│              │ of async events (payments, CI, SaaS)      │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS DO    │ Verify HMAC signature; deduplicate by     │
│              │ event ID; return 200 quickly              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "They call you when something happens"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HMAC → Idempotency → Event-Driven Arch   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You're building a webhook delivery system as a provider (like Stripe): 10M registered webhooks, events fire at 100K/second at peak, consumer endpoints have p99 response latency of 5 seconds. Design the webhook dispatch infrastructure: fan-out at event time, retry scheduling, dead-lettering strategy, and how you prevent slow consumer endpoints from affecting your delivery pipeline.
