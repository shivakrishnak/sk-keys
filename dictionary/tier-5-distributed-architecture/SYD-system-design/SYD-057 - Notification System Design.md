---
id: SYD-030
title: Notification System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-043, SYD-064, SYD-024
used_by: SYD-071
related: SYD-043, SYD-068, SYD-059
tags:
  - architecture
  - design
  - advanced
  - async
  - distributed
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 57
permalink: /syd/notification-system-design/
---

# SYD-067 - Notification System Design

⚡ TL;DR - A notification system delivers events to users across channels (push, SMS, email) reliably and at scale - the hard parts are channel fan-out, delivery guarantees, rate limiting, and preference management.

| SYD-067         | Category: System Design         | Difficulty: ★★★ |
| :-------------- | :------------------------------ | :-------------- |
| **Depends on:** | SYD-043, SYD-064, SYD-024      |                 |
| **Used by:**    | SYD-071                         |                 |
| **Related:**    | SYD-043, SYD-068, SYD-059      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce platform wants to notify users about order status updates, promotions, and shipping events. Without a notification system, every service (orders, shipping, payments) sends notifications directly via email/SMS providers. Preferences are scattered. Deduplication does not exist. Users receive 3 emails about the same order update from different services.

**THE BREAKING POINT:**
At scale, notification delivery requires: channel fan-out (push, email, SMS simultaneously), user preference enforcement (user opted out of marketing emails), deduplication (don't send the same notification twice), rate limiting (no more than 3 notifications/hour), and delivery tracking (did the notification reach the user?).

**THE INVENTION MOMENT:**
Centralize notification sending behind a single service. All producers publish events; the notification service handles channel selection, user preferences, rate limiting, deduplication, and delivery tracking.

**EVOLUTION:**
Early notification systems were per-channel (email daemon, SMS script). Unified messaging layers emerged to handle multiple channels. Firebase Cloud Messaging (FCM) and Apple Push Notification Service (APNs) standardized push. Modern notification systems add: user preference management portals, delivery time optimization (send at time user is most likely to engage), A/B testing of notification content, and analytics dashboards tracking open rates.

---

### 📘 Textbook Definition

A **notification system** is an infrastructure layer that receives event triggers from upstream services and delivers personalized messages to users via one or more channels (in-app push, mobile push, email, SMS, webhook). It manages user preferences, deduplicates events, rate-limits delivery to avoid notification fatigue, and tracks delivery status and engagement.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A central dispatcher that receives "tell this user about X" and handles channel selection, preferences, rate limits, and tracking.

**One analogy:**

> A notification system is like a concierge at a hotel. Guests (users) pre-register preferences (call the room? Send a text? Email?). When a package arrives (event), the concierge checks the guest's preferred contact method and reaches out exactly once through the right channel.

**One insight:**
Notification systems are much harder than they look. The actual send is 5% of the work. The other 95% is: idempotency (send exactly once), preference management, rate limiting, channel failover, and delivery tracking.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A notification must be delivered at most once per channel per event (idempotency).
2. User preferences must be respected before any send.
3. Rate limits protect users from notification fatigue and protect channel provider quotas.
4. Delivery must be asynchronous - the originating service must not wait for delivery.

**DERIVED DESIGN:**
Event arrives -> look up user preferences -> check rate limits -> deduplicate by event_id -> fan out to enabled channels (Kafka per channel) -> channel workers call providers (FCM, SendGrid, Twilio) -> track delivery status -> update analytics.

**THE TRADE-OFFS:**
**Gain:** Centralized preference enforcement; single source of truth for delivery tracking; channel abstraction for producers.
**Cost:** Additional latency hop; single notification service becomes a critical dependency; complex state management for preference + deduplication + rate limiting.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Fan-out to multiple channels respecting user preferences; idempotent delivery.
**Accidental:** Delivery time optimization, A/B testing of content, engagement analytics, delivery window management.

---

### 🧪 Thought Experiment

**SETUP:** A user places an order. The order service, payment service, and logistics service all want to notify the user. Without coordination, the user receives 3 "Order Confirmed" notifications.

**WHAT HAPPENS WITHOUT CENTRALIZED NOTIFICATION:**
Order service sends email directly to SendGrid. Payment service sends SMS directly to Twilio. Logistics service sends push via FCM. User gets 3 nearly identical notifications. User preferences (email only, no SMS) are not checked. No rate limiting. No deduplication. No delivery tracking.

**WHAT HAPPENS WITH CENTRALIZED NOTIFICATION:**
All three services publish to the notification event bus: `notify(user_id, event_type="order_confirmed", order_id="123")`. The notification service deduplicates by (user_id + event_type + order_id). Sends exactly one notification. Checks user preference (email only). Sends email. Records delivery. Respects user's rate limit (not more than 5 notifications/day).

**THE INSIGHT:**
The notification service is a coordinator that enforces contracts (at most once, respect preferences) that no individual producer can enforce on its own. Centralization enables enforcement.

---

### 🧠 Mental Model / Analogy

> A notification system is like a traffic management center for messages. It knows all the roads (channels), current traffic (rate limits), customer preferences (routes), and it deduplicates identical packages before dispatch.

- **Traffic management center** = notification service
- **Package** = notification event
- **Road preferences** = user channel preferences
- **Speed limits** = rate limits per user per channel
- **Duplicate package filter** = idempotency check
- **Delivery tracking** = notification status store

Where this analogy breaks down: traffic management doesn't need to track every car's delivery status or retry failed deliveries - notification systems must.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When something happens, your app tells you via phone notification, email, or text. A notification system decides which to use, whether you've asked not to be bothered, and whether it already told you.

**Level 2 - How to use it (junior developer):**
Publish events to the notification service rather than calling SendGrid/Twilio directly. Include user_id, event_type, and a deduplication key. The service handles the rest. Always make event publishing async (fire-and-forget from the producer).

**Level 3 - How it works (mid-level engineer):**
Event arrives as Kafka message. Notification service: (1) lookup user preferences + device tokens; (2) check rate limit per user per channel (Redis counter); (3) deduplicate by (user_id + event_id); (4) fan out to per-channel Kafka topics; (5) channel workers call FCM/APNs/SendGrid/Twilio; (6) receive delivery callback or poll for status; (7) store delivery event in analytics DB.

**Level 4 - Why it was designed this way (senior/staff):**
Separate Kafka topics per channel because push notification delivery takes 50ms while email delivery takes 2-10 seconds. Mixing channels in one queue causes push delivery to be delayed behind slow email sends. Channel workers scale independently based on channel volume and provider rate limits. Preference storage in a NoSQL store (Redis or DynamoDB) for sub-millisecond preference lookup on every notification - the preference check is on the hot path.

**Expert Thinking Cues:**
- Ask: "What is the acceptable end-to-end latency for a push notification? (target: < 5 seconds)"
- Ask: "What happens to queued notifications when a user unsubscribes between queue time and delivery time?"
- Red flag: synchronous notification delivery in the HTTP request cycle
- Red flag: no idempotency key - duplicate events cause duplicate notifications

---

### ⚙️ How It Works (Mechanism)

```
Producer publishes:
  {user_id, event_type, content, idempotency_key}

Notification Service:
  1. Dedup check: idempotency_key in Redis SET?
     YES -> drop (already sent)
     NO -> mark as processing
  2. Preference lookup: user:{user_id}:prefs
     -> {push: true, email: true, sms: false}
  3. Rate limit check: rl:{user_id}:{channel}
     -> under limit: proceed
     -> over limit: queue for later or drop
  4. Fan-out to enabled channels:
     -> Publish to push_topic (FCM/APNs worker)
     -> Publish to email_topic (SendGrid worker)
  5. Each worker delivers to provider
  6. Provider callback -> update delivery_status
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Order service: order_confirmed event]
         |
         v
[Notification service: deduplicate]  <- YOU ARE HERE
         |
         v
[Preference lookup: push + email enabled]
         |
         v
[Rate limit check: under limit]
         |
      Fan out
     /        \
[Push worker]  [Email worker]
     |              |
[FCM/APNs]    [SendGrid]
     |              |
[Delivery callback -> DB]
```

**FAILURE PATH:**
```
[FCM returns 503: service unavailable]
         |
[Push worker: exponential backoff retry]
         |
[After 3 retries: mark failed, no alert]
         |
[User-facing: no push notification received]
         |
[Email was delivered successfully as fallback]
```

**WHAT CHANGES AT SCALE:**
At 100M notifications/day (1,150/sec), queue depth becomes the key metric. Separate queues per priority (transactional vs marketing). Transactional notifications (order confirmed) get dedicated workers with guaranteed SLA. Marketing notifications are lower priority and subject to batch sending windows.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multiple notification service instances may receive the same event. Idempotency key must use atomic Redis SET NX before processing. Channel workers must implement idempotent delivery - if FCM returns "message already sent" for a duplicate - treat as success.

---

### 💻 Code Example

**BAD - synchronous multi-channel send without dedup:**
```python
# BAD: synchronous, no dedup, no preferences
def order_confirmed(order_id, user_id):
    email = get_user_email(user_id)
    phone = get_user_phone(user_id)
    send_email(email, f"Order {order_id} confirmed!")
    send_sms(phone, f"Order {order_id} confirmed!")
    # Blocks HTTP response; sends even if opt-out
```

**GOOD - async publish with idempotency:**
```python
import uuid, json
import kafka, redis

r = redis.Redis()
producer = kafka.KafkaProducer()
IDEM_TTL = 86400  # 24 hours

def publish_notification(
    user_id: str,
    event_type: str,
    content: dict,
    idem_key: str = None
):
    """Fire-and-forget notification event."""
    key = idem_key or f"{event_type}:{user_id}:{uuid.uuid4()}"
    # Caller can supply idem_key for cross-service dedup
    event = {
        "user_id": user_id,
        "event_type": event_type,
        "content": content,
        "idempotency_key": key,
    }
    producer.send(
        "notification.events",
        key=user_id.encode(),
        value=json.dumps(event).encode()
    )

# In notification service consumer:
def process_notification(event: dict):
    idem_key = event["idempotency_key"]
    # Atomic dedup check
    if not r.set(f"notif:idem:{idem_key}", 1,
                  nx=True, ex=IDEM_TTL):
        return  # Already processed

    prefs = get_user_prefs(event["user_id"])
    if prefs.get("push_enabled"):
        publish_to_channel("push", event)
    if prefs.get("email_enabled"):
        publish_to_channel("email", event)
```

**How to test / verify correctness:**
- Publish same event twice with same idempotency_key - assert user receives exactly one notification.
- User with push=false, email=true - assert no push sent, email sent.
- Rate limit: send 10 notifications in 1 minute with limit=5 - assert first 5 delivered, 6-10 dropped/queued.

---

### ⚖️ Comparison Table

| Channel     | Latency  | Cost     | Open rate | Opt-out friction |
| ----------- | -------- | -------- | --------- | ---------------- |
| Push (mobile) | < 5s  | Near-free | 10-20%  | Easy (system settings) |
| Email       | 1-30min  | Low      | 20-40%    | Moderate (unsubscribe link) |
| SMS         | < 60s    | High     | 90%+      | Low (STOP reply) |
| In-app      | Instant  | None     | N/A (must open app) | None  |
| Webhook     | < 1s     | None     | N/A (B2B) | Business contract |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Just call the email provider directly from my service" | Direct provider calls scatter preference enforcement, create duplicate sends, and make it impossible to add deduplication or rate limiting consistently. |
| "Fire-and-forget means I don't need delivery tracking" | Users who don't receive notifications call support. Without delivery tracking you cannot investigate. Always persist delivery attempts and status. |
| "Push notifications are always received instantly" | Push requires user device to be online and app to be registered with FCM/APNs. Offline devices get the notification when they reconnect but may have a TTL on the message. |
| "Rate limiting annoys users" | The opposite: unlimited notifications cause users to disable all notifications for your app. Rate limits protect long-term engagement. |
| "Notification content can be generated at send time" | Content should be generated at event time, stored in the event, and sent as-is. Content generated at send time may be stale (user's name changed, order status changed). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Duplicate notifications after retry**

**Symptom:** Users receive the same notification 3 times.

**Root Cause:** Notification worker retried due to timeout; provider already delivered but the ACK was lost.

**Diagnostic:**
```bash
# Check notification delivery log for duplicates
SELECT user_id, event_id, COUNT(*)
FROM notification_deliveries
WHERE ts > NOW() - INTERVAL '1h'
GROUP BY user_id, event_id HAVING COUNT(*) > 1;
```

**Fix:** Use idempotency_key in provider API calls where supported (SendGrid, Twilio support this). Check provider's "message already sent" error and treat as success.

**Prevention:** Store idempotency_key in delivery DB with unique constraint. Retry only if status is not "delivered".

---

**Failure Mode 2: Channel queue backup causing delayed notifications**

**Symptom:** Order confirmation emails arrive 30 minutes late because the email queue is backed up.

**Root Cause:** Email channel shares queue with marketing bulk sends; marketing volume overwhelms the queue.

**Diagnostic:**
```bash
kafka-consumer-groups.sh --describe \
  --group notification-email-workers \
  --bootstrap-server kafka:9092 | grep LAG
```

**Fix:** Separate queues for transactional vs marketing notifications. Transactional gets dedicated workers and higher priority.

**Prevention:** Never mix transactional and marketing in the same queue. Design queue isolation from day one.

---

**Failure Mode 3 (Security): Notification enumeration attack**

**Symptom:** Attacker triggers "forgot password" notifications to enumerate valid email addresses (account exists = gets email, no account = no email).

**Root Cause:** Notification system's existence/non-delivery reveals account existence.

**Diagnostic:** Check for mass "forgot password" events from single IP or device.

**Fix:** Always return success to the user regardless of whether the account exists. Send a "no account found" email to the address if account does not exist.

**Prevention:** Design notification flows to not leak account existence through timing or delivery confirmation signals.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-043 - Polling vs Webhooks]] - delivery mechanism context
- [[SYD-024 - Idempotency Key]] - critical for preventing duplicate notifications
- [[SYD-064 - Rate Limiter Design]] - rate limiting notification sends

**Builds On This (learn these next):**
- [[SYD-068 - Chat System Design]] - real-time messaging vs async notifications
- [[SYD-071 - System Design at Hyperscale]] - notification at billion-user scale

**Alternatives / Comparisons:**
- [[SYD-059 - Fan-Out on Write vs Read]] - fan-out strategy applies to notifications too

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Central dispatcher converting   │
│              │ events into multi-channel sends  │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Duplicate sends, missed prefs,   │
│ IT SOLVES    │ notification fatigue at scale    │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Deduplicate + check prefs +      │
│              │ rate limit BEFORE every send     │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Any multi-channel user comms     │
│              │ across multiple producer services│
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ One service, one channel, low    │
│              │ volume - direct call is fine     │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Centralization overhead vs       │
│              │ consistency of enforcement       │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Dedup + prefs + rate limit +    │
│              │ fan-out + track per channel."    │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-068 Chat System Design       │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always deduplicate with an idempotency key before sending to any channel.
2. Check user preferences before every send - never assume opt-in.
3. Use separate queues for transactional vs marketing notifications.

**Interview one-liner:** "A notification system centralizes event-to-channel delivery: dedup by idempotency key, check preferences, apply rate limits, then fan out to per-channel queues processed by independent workers."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Enforcement of correctness contracts (idempotency, preferences, rate limits) should be centralized at the service boundary, not duplicated across every producer. N producers each implementing these checks = N opportunities for bugs and inconsistency.

**Where else this pattern appears:**
- **Payment processing:** A payment gateway centralizes fraud checks, limits, and compliance - no individual merchant service re-implements these.
- **API gateway:** Rate limiting, auth, and logging centralized at the gateway, not in each microservice.
- **Event sourcing outbox:** A centralized outbox service publishes events reliably on behalf of all services.

---

### 💡 The Surprising Truth

Mobile push notifications are delivered by two private monopolies - Apple (APNs) and Google (FCM) - and your notification system must comply with their policies or risk being blocked. If your app sends too many irrelevant notifications ("notification spam"), Apple can withdraw your push delivery privileges entirely, silencing all notifications for your app for all iOS users globally. The notification system must include engagement tracking and automatic suppression of low-engagement users to protect push delivery reputation.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A user unsubscribes from email notifications at 2:00 PM. At 1:59 PM, 10 marketing emails were queued but not yet sent. Should those 10 emails be sent after the unsubscribe? How does your notification system enforce the preference change for already-queued messages?

*Hint:* Explore the "preference check at queue time" vs "preference check at delivery time" trade-off. Checking at delivery time is more correct (respects recent changes) but requires a preference lookup for every queued message before delivery.

**Q2 (Scale):** A flash sale event triggers 50M notifications in 60 seconds. Your SendGrid account allows 100 email/second. At that rate, the final email would be delivered 6 days later. What queuing strategy ensures transactional notifications (receipts) still arrive quickly while marketing notifications wait?

*Hint:* Design separate notification tiers with different SendGrid accounts/subusers and dedicated delivery quotas. Explore how SendGrid IP warm-up affects burst sending capacity and how dedicated IPs separate marketing from transactional reputation.

**Q3 (Design Trade-off):** You want to optimize notification delivery time to when users are most likely to engage (send at their local 9am instead of whenever the event triggers). How do you build this "delivery time optimization" feature without making users wait days for urgent transactional notifications?

*Hint:* Distinguish notification urgency: transactional (order confirmed, password reset) = send immediately; informational (weekly digest, promo) = send at optimal time. Let producers annotate urgency level and route to appropriate delivery queue.
