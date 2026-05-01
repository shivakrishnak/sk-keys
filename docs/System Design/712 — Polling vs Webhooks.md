---
layout: default
title: "Polling vs Webhooks"
parent: "System Design"
nav_order: 712
permalink: /system-design/polling-vs-webhooks/
number: "712"
category: System Design
difficulty: ★★☆
depends_on: "Push vs Pull Architecture, HTTP and APIs"
used_by: "Push vs Pull Architecture, Notification System Design"
tags: #intermediate, #architecture, #http, #integration, #async
---

# 712 — Polling vs Webhooks

`#intermediate` `#architecture` `#http` `#integration` `#async`

⚡ TL;DR — **Polling** repeatedly asks a server "anything new?" at intervals; **Webhooks** let the server call back to a URL when something happens — webhooks are lower-latency and more efficient, but require a publicly accessible endpoint.

| #712            | Category: System Design                               | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Push vs Pull Architecture, HTTP and APIs              |                 |
| **Used by:**    | Push vs Pull Architecture, Notification System Design |                 |

---

### 📘 Textbook Definition

**Polling** is a client-initiated integration pattern where a client periodically sends HTTP requests to a server to check for new data or state changes. The polling interval determines the trade-off between latency (shorter intervals = lower lag) and server load (shorter intervals = more wasted requests). **Webhooks** are a server-initiated integration pattern where a service sends an HTTP POST callback to a pre-registered URL on the client's server whenever a specified event occurs. Webhooks provide event-driven, near-real-time notification without client-side request overhead. Webhooks require the consumer to expose a publicly reachable HTTPS endpoint; polling works in any network topology including restricted/private networks. Both patterns implement push vs. pull at the HTTP API integration layer.

---

### 🟢 Simple Definition (Easy)

Polling: you keep calling your friend every 5 minutes asking "have you left yet?" Webhook: you ask your friend to text you WHEN they leave, and you do other things until the text arrives. Polling wastes your time (and your friend's). Webhooks are efficient — you're notified only when something actually happens.

---

### 🔵 Simple Definition (Elaborated)

GitHub CI integration: Option A (polling): your CI server calls GitHub API every 60 seconds — "any new commits?" 99% of the time: "nope." 1% of the time: "yes." Wasted requests: 1,440 per day to detect ~5 commits. Option B (webhook): you configure GitHub to POST to your CI server's `/webhook/github` URL on every push. GitHub calls you instantly on commit. CI starts build in < 1 second. 0 wasted requests. Polling: simpler setup; webhook: more efficient and faster. Stripe, GitHub, Shopify, Twilio all offer webhooks as the primary integration method.

---

### 🔩 First Principles Explanation

**Polling vs webhooks: mechanics and comparison:**

```
POLLING VARIANTS:

  1. SHORT POLLING (most common):
     Client: GET /orders?status=pending&since={last_check_time}
     Every 30 seconds.

     Load: 1 request/30s × 10,000 clients = 333 requests/second to server.
     If 99% return empty: 330 wasted requests/sec.

  2. LONG POLLING:
     Client: GET /events?since={last_id}
     Server: holds request until event occurs (up to 30 seconds).
     Client: immediately re-requests after response.

     Benefit: near-real-time without wasted "empty" responses.
     Cost: server holds many open connections (N concurrent clients).
          Memory: ~1-5 KB per held connection × 10,000 clients = 10-50 MB.

  3. SHORT POLLING WITH EXPONENTIAL BACKOFF:
     On empty response: double the interval (2s → 4s → 8s → ... → max 60s).
     On event received: reset to base interval.

     Benefit: adapts to event frequency. Low load during quiet periods.
     Best for: low-frequency events with occasional burst.

WEBHOOKS:

  Registration:
    Client registers callback URL with provider:
    POST https://api.stripe.com/v1/webhook_endpoints
    { "url": "https://yourdomain.com/stripe/webhook", "enabled_events": ["payment_intent.succeeded"] }

  Delivery flow:
    1. Event occurs (payment succeeds)
    2. Provider prepares HTTP POST to callback URL
    3. Provider sends: POST https://yourdomain.com/stripe/webhook
       Headers:
         Stripe-Signature: t=timestamp,v1=hmac_sha256_signature
         Content-Type: application/json
       Body:
         { "type": "payment_intent.succeeded", "data": { "object": {...} } }
    4. Client endpoint: validate signature, process event, return 200 OK
    5. Provider: marks webhook as delivered

  SIGNATURE VALIDATION (security critical):

    // Java: Stripe webhook signature validation
    @PostMapping("/stripe/webhook")
    public ResponseEntity<String> handleStripeWebhook(
            @RequestBody String payload,
            @RequestHeader("Stripe-Signature") String sigHeader) {

        try {
            // Validate HMAC-SHA256 signature:
            Event event = Webhook.constructEvent(
                payload,
                sigHeader,
                stripeWebhookSecret  // from Stripe dashboard
            );
            // Process event...
            return ResponseEntity.ok("Received");
        } catch (SignatureVerificationException e) {
            // Invalid signature: reject immediately (possible replay/forgery attack)
            return ResponseEntity.status(400).body("Invalid signature");
        }
    }

  WEBHOOK SECURITY REQUIREMENTS:
    1. VERIFY SIGNATURE: always. Never process webhooks without signature check.
    2. IDEMPOTENCY: provider may retry on 5xx → your handler must be idempotent.
    3. RESPOND QUICKLY: return 200 within 5-10 seconds (async processing).
    4. HTTPS ONLY: never accept webhooks over HTTP (MITM risk).
    5. IP ALLOWLIST: optionally restrict to provider's known IP ranges.

  RETRY BEHAVIOUR (Stripe example):
    On non-2xx response: retry with exponential backoff:
    Attempt 1: immediate
    Attempt 2: 5 minutes later
    Attempt 3: 30 minutes later
    Attempt 4: 2 hours later
    ...up to 72 hours, ~87 attempts total

    IMPLICATION: Your webhook handler MUST be idempotent.
    If Stripe retries "payment_succeeded" 3 times (due to your 500 error):
    Non-idempotent: 3 fulfilled orders for 1 payment → critical bug.
    Idempotent: uses payment_intent.id as idempotency key → second/third delivery is no-op.

COMPARISON MATRIX:

  ┌──────────────────────────────────────────────────────┐
  │ Aspect           │ Polling      │ Webhook            │
  ├──────────────────┼──────────────┼────────────────────┤
  │ Latency          │ 0-interval   │ ~1-5 seconds       │
  │ Wasted requests  │ High (99%+)  │ None               │
  │ Server load      │ Constant     │ Only on events     │
  │ Setup complexity │ Low          │ Medium             │
  │ Client needs     │ Network out  │ Public HTTPS URL   │
  │ Works in NAT/VPN │ Yes          │ No (needs pub URL) │
  │ Reliability      │ High         │ Needs retry logic  │
  │ Debugging        │ Simple       │ Need event log/UI  │
  └──────────────────────────────────────────────────────┘

WHEN TO USE EACH:

  USE POLLING WHEN:
    - Client is behind NAT/firewall (no public URL possible)
    - Simple integration with low event frequency
    - Client is a mobile app (no persistent server)
    - Provider doesn't offer webhooks

  USE WEBHOOKS WHEN:
    - Real-time or near-real-time events needed
    - High event volume (polling would waste resources)
    - Integration with payment processors, version control, IoT
    - Client has a stable public HTTPS endpoint
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Webhooks (polling only):

- 10,000 integrations polling GitHub API every 60 seconds = 167 API req/sec wasted
- Latency: up to 60 seconds between commit and build trigger
- API rate limits exhausted on wasted polling

WITH Webhooks:
→ Instant event delivery: commit → build trigger in < 5 seconds
→ Zero wasted requests: server only sends HTTP requests when events occur
→ API rate limits preserved for actual data fetching

---

### 🧠 Mental Model / Analogy

> Polling: checking your email every 5 minutes to see if a package delivery notification arrived. Webhook: giving the delivery service your phone number to text you when the package arrives. Polling: you do the work (constant checking). Webhook: the service does the work (calls you once). For high-frequency events or many subscribers, webhooks are dramatically more efficient.

"Checking email every 5 minutes" = polling (client initiates, constant overhead)
"Delivery service texts you" = webhook (server initiates on event)
"Most email checks: no new notification" = wasted polling requests (empty responses)
"One text when package arrives" = webhook: zero overhead between events
"Need a phone number to receive texts" = webhook: requires public endpoint

---

### ⚙️ How It Works (Mechanism)

**Webhook endpoint with idempotent processing:**

```java
@RestController
@RequestMapping("/webhooks")
public class WebhookController {

    @Autowired private OrderService orderService;
    @Autowired private WebhookEventRepository webhookEventRepository;

    @PostMapping("/payment")
    public ResponseEntity<String> handlePaymentWebhook(
            @RequestBody String rawPayload,
            @RequestHeader("X-Webhook-Signature") String signature) {

        // 1. Validate signature FIRST (security):
        if (!isValidSignature(rawPayload, signature)) {
            return ResponseEntity.status(401).body("Invalid signature");
        }

        PaymentEvent event = parseEvent(rawPayload);

        // 2. IDEMPOTENCY CHECK: have we processed this event before?
        if (webhookEventRepository.existsByEventId(event.getId())) {
            // Already processed (retry delivery) — return 200 without reprocessing:
            return ResponseEntity.ok("Already processed");
        }

        // 3. STORE EVENT RECEIPT FIRST (before processing):
        webhookEventRepository.save(new WebhookEvent(event.getId(), "PROCESSING", rawPayload));

        // 4. PROCESS ASYNCHRONOUSLY (respond within 5s to avoid provider timeout):
        CompletableFuture.runAsync(() -> {
            try {
                if ("payment.succeeded".equals(event.getType())) {
                    orderService.fulfillOrder(event.getOrderId());
                }
                webhookEventRepository.updateStatus(event.getId(), "PROCESSED");
            } catch (Exception e) {
                webhookEventRepository.updateStatus(event.getId(), "FAILED");
                // Will be retried by provider on next delivery attempt
            }
        });

        // 5. Return 200 immediately (don't wait for async processing):
        return ResponseEntity.ok("Received");
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Event occurs on third-party service
        │
        ▼
Polling vs Webhooks ◄──── (you are here)
        │
        ├── POLLING → regular GET requests, pull model
        └── WEBHOOKS → HTTP POST callback, push model
                │
                ▼
        Push vs Pull Architecture (broader concept)
        Notification System Design (internal notifications)
```

---

### 💻 Code Example

**GitHub webhook vs polling comparison (Node.js):**

```javascript
// POLLING approach (inefficient):
async function pollGitHub(repo, lastChecked) {
  setInterval(async () => {
    const commits = await fetch(
      `https://api.github.com/repos/${repo}/commits?since=${lastChecked}`,
      { headers: { Authorization: `Bearer ${TOKEN}` } },
    ).then((r) => r.json());

    if (commits.length > 0) {
      triggerBuild(commits[0]);
      lastChecked = new Date().toISOString();
    }
    // 99% of the time: commits.length = 0 — wasted request
  }, 60_000); // poll every 60 seconds
}

// WEBHOOK approach (efficient):
const express = require("express");
const crypto = require("crypto");
const app = express();

app.post(
  "/webhook/github",
  express.json({
    verify: (req, res, buf) => {
      req.rawBody = buf; // needed for signature verification
    },
  }),
  (req, res) => {
    // Verify signature:
    const sig = req.headers["x-hub-signature-256"];
    const expected =
      "sha256=" +
      crypto
        .createHmac("sha256", GITHUB_WEBHOOK_SECRET)
        .update(req.rawBody)
        .digest("hex");

    if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) {
      return res.status(401).send("Invalid signature");
    }

    // Process event:
    const event = req.headers["x-github-event"];
    if (event === "push") {
      triggerBuild(req.body.commits[0]);
    }

    res.sendStatus(200);
  },
);
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Webhooks are always more reliable than polling              | Webhooks can fail: your endpoint is down, network issues, provider bugs. Polling is inherently self-healing — if it misses a window, the next poll catches up. For mission-critical integrations, use webhooks for speed + background reconciliation polling to catch missed events               |
| A single 200 response means the webhook was processed       | Returning 200 quickly means "received" — not "processed." If you process asynchronously (recommended), the 200 just acknowledges receipt. You must track processing status separately. The provider doesn't know if your async processing succeeded                                               |
| Polling at short intervals (1 second) is fine for low-scale | Short-interval polling on a public API typically violates rate limits. 1-second polling × 10,000 clients = 10,000 req/sec on the provider's API — usually immediately rate limited (429). Check the API's rate limit before choosing polling interval                                             |
| Webhooks don't need replay/catchup logic                    | Your webhook endpoint will be down occasionally (deploys, outages). Even with provider retry logic, you can miss events if the outage exceeds the retry window. Always implement a reconciliation job: periodically poll for recent events and re-process any that don't appear in your event log |

---

### 🔥 Pitfalls in Production

**Non-idempotent webhook handler causes duplicate orders:**

```
PROBLEM: Stripe retries webhook → duplicate order fulfilment

  Scenario:
    Stripe sends: POST /webhook (payment_intent.succeeded, id=pi_123)
    Your handler: starts processing (creates order, emails customer)
    Your handler: times out after 10 seconds (slow DB query)
    Response: 504 Gateway Timeout (not 200)

  Stripe sees: no 200 response → retry after 5 minutes
    Retry: POST /webhook (same event, id=pi_123)
    Your handler: creates ANOTHER order (duplicate!)

  Bug: customer charged once, receives two shipments. Or charged twice.

FIX: IDEMPOTENCY KEY CHECK

  @PostMapping("/stripe/webhook")
  @Transactional
  public ResponseEntity<String> handleStripe(@RequestBody String payload, ...) {
    StripeEvent event = parseAndValidate(payload, sigHeader);

    // Idempotency: use event.id as unique key
    boolean alreadyProcessed = processedEvents.existsById(event.getId());
    if (alreadyProcessed) {
      return ResponseEntity.ok("Duplicate - ignored");
    }

    // Mark as being processed (before actual processing):
    processedEvents.save(event.getId(), "PROCESSING");

    // Process (idempotent operations only):
    processPaymentIntent(event);  // creates order only if not exists by payment_id

    processedEvents.updateStatus(event.getId(), "DONE");
    return ResponseEntity.ok("OK");
  }

  // Idempotent order creation:
  @Transactional
  public void processPaymentIntent(StripeEvent event) {
    String paymentIntentId = event.getDataObject().getString("id");

    // Skip if order already exists for this payment:
    if (orderRepository.existsByPaymentIntentId(paymentIntentId)) {
      return;  // idempotent: no-op on duplicate
    }

    orderRepository.save(new Order(paymentIntentId, ...));
    emailService.sendConfirmation(...);
  }
```

---

### 🔗 Related Keywords

- `Push vs Pull Architecture` — polling = pull; webhooks = push (at HTTP integration layer)
- `Idempotency Key` — required for safe webhook processing (provider retries)
- `Rate Limiting (System)` — polling must respect API rate limits
- `Notification System Design` — internal system notifications use similar push/pull trade-offs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Polling: client asks repeatedly;          │
│              │ Webhook: server calls client on event     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Polling: private networks, no public URL; │
│              │ Webhook: real-time events, public server  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Non-idempotent webhook handlers;          │
│              │ polling without exponential backoff       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Check email every 5 min vs let delivery  │
│              │  service text you when parcel arrives."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Idempotency Key → Push vs Pull            │
│              │ → Notification System Design              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're integrating with Stripe for payment processing. Stripe offers both webhooks and a polling API (`/v1/events?created[gte]=timestamp`). Design a robust integration that uses webhooks as the primary delivery mechanism but adds polling-based reconciliation to catch any missed webhook events. Specifically: (a) what triggers the reconciliation job, (b) how often does it run, (c) how does it determine which events were missed (i.e., in your webhook log but not in Stripe's event list, or vice versa)?

**Q2.** Your company is building a developer platform where third-party developers can register webhooks to receive events. Design the webhook delivery system: (a) how do you store webhook registrations? (b) what happens when an event occurs — synchronous or asynchronous delivery? (c) what retry policy do you implement and why? (d) how do you prevent a slow or malicious subscriber from blocking your delivery pipeline?
