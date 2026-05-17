---
id: SYD-047
title: Notification System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-036, SYD-037
used_by: ""
related: SYD-036, SYD-037, SYD-035, SYD-028
tags:
  - architecture
  - notifications
  - messaging
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /syd/notification-system-design/
---

# SYD-047 - Notification System Design

⚡ TL;DR - A notification system delivers real-time
and scheduled alerts to users via multiple channels
(push notifications, email, SMS, in-app). The core
design: producers publish notification events to a
queue (Kafka/SQS); channel-specific workers consume
and deliver to third-party providers (APNs, FCM, SendGrid,
Twilio). Key challenges: delivery reliability (at-least-once
with deduplication), per-user preference management
(opt-out per channel/type), rate limiting (prevent
notification spam), and fan-out at scale (one event
→ millions of recipients).

| #047 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Push vs Pull Architecture, Polling vs Webhooks | |
| **Related:** | Push vs Pull, Polling vs Webhooks, Fan-Out, Rate Limiting | |

---

### 🔥 The Problem This Solves

When a user receives a reply on Twitter, a LinkedIn
connection request, or an Amazon order shipped alert,
a notification must be delivered to potentially millions
of users simultaneously. A company announcing a product
launch may need to send push notifications to 50M app
users in under 5 minutes. Without thoughtful design:
- Single-threaded email sender crashes at 1M recipients
- No retry means transient failures permanently lose notifications
- No preference management = user gets 100 emails/day and unsubscribes
- Fan-out bottleneck = all 50M notifications go through one service

---

### 📘 Textbook Definition

**Notification system:** A platform that receives
notification trigger events from producers (application
services) and delivers them to end users through one
or more delivery channels. Manages delivery routing,
preference filtering, rate limiting, retry logic, and
delivery status tracking.

**Channels:**
- **Mobile push:** APNs (iOS), FCM (Android). Delivered
  to device via Apple/Google infrastructure.
- **Email:** SMTP relay / transactional email providers
  (SendGrid, SES, Mailgun).
- **SMS:** SMS gateway providers (Twilio, Vonage).
- **In-app:** WebSocket or polling; stored in DB for
  display in notification center.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Event happens → enqueue notification → workers
deliver through the right channel to users who want it.

**One analogy:**
> A postal sorting facility:
> Incoming mail (events) arrives at the sorting dock.
> Sorters (workers) read the address (user + channel),
> check do-not-mail lists (preferences), then pass
> to the right courier: UPS for packages (push), USPS
> for letters (email), FedEx for priority (SMS).
> Each courier handles their own delivery and retry.

**One insight:**
The hardest problem is not sending a notification -
it is sending it reliably, exactly the right number of
times (not 0, not 5), only to users who want it, at the
right time, without overwhelming the third-party providers.

---

### 🔩 First Principles Explanation

**SYSTEM COMPONENTS:**
```
Producers: Any service that triggers a notification.
  - Order service: "Order #123 shipped"
  - Social service: "User X replied to your post"
  - Batch jobs: "Weekly digest is ready"

Notification Service API:
  Accepts trigger events from producers.
  POST /notify {user_id, type, payload}
  Validates, enriches (fetch user channel preferences),
  then publishes to the appropriate queues.

Queues (per channel):
  push-notification-queue
  email-queue
  sms-queue
  inapp-queue

Workers (per channel):
  Pull from queue, apply rate limiting,
  check preferences, call third-party providers.
  On provider error: retry with exponential backoff.
  On permanent failure (invalid token): deactivate device.

Third-party Providers:
  APNs, FCM (push)
  SendGrid, AWS SES (email)
  Twilio, Vonage (SMS)
  WebSocket server (in-app)
```

**PREFERENCE MANAGEMENT:**
```
Users have per-type, per-channel preferences.
Example schema:

user_preferences table:
  user_id INT
  notification_type VARCHAR (ORDER_SHIPPED, SOCIAL_REPLY)
  channel VARCHAR (push, email, sms, inapp)
  enabled BOOLEAN
  frequency_limit INT (max per day, 0 = unlimited)

On every notification:
  1. Look up user preferences for {type, channel}
  2. If not enabled: skip this channel
  3. Check frequency_limit: has user exceeded daily
     limit for this type?
  4. Check DND hours (Do Not Disturb: no push 11pm-7am)
  5. Proceed with delivery

Preferences stored in Redis (cache) + DB (source of truth).
Redis TTL: 5 minutes (balance freshness vs load).
```

**DEDUPLICATION:**
```
At-least-once delivery (Kafka consumer) means a
notification can be delivered twice on retry.

Deduplication key: {notification_id} or
  {user_id + type + entity_id + window}
  Example: "user 123 liked post 456" deduplicated
  within a 30-minute window (1 notification per post
  per 30 mins regardless of multiple likes).

Strategy:
  Before calling provider, check Redis:
    dedup_key = f"notif:{user_id}:{type}:{entity_id}"
    SET dedup_key 1 NX EX 1800  (NX=only if not exists)
    If key exists: skip (duplicate)
    If key set: proceed with delivery
```

---

### 🧪 Thought Experiment

**SIZING: Notification system at 100M users**

Events/day: 500M notifications (5 per user avg)
Push: 60% = 300M push/day = 3,472 push/sec
Email: 30% = 150M email/day = 1,736 email/sec
SMS: 10% = 50M SMS/day = 578 SMS/sec
Peak (10x): 35K push/sec, 17K email/sec

**Push notification throughput:**
APNs/FCM support ~250K messages/second (per provider
account). 35K peak is easily handled. But single queue
consumer = bottleneck. Need: 10-50 parallel workers
consuming from push queue.

**Queue sizing:**
Kafka topic: push-notifications, 50 partitions
(each consumed by 1 worker). 50 parallel pushes/sec.
At 35K/sec: 50 × 700 = 35K. Feasible.

**Fan-out event (1 event → 50M users):**
Example: Product launch announcement to all users.
50M push notifications.
At 35K/sec throughput: 50M / 35K = ~24 minutes.
This is acceptable for mass announcements.
For truly urgent mass notifications (< 5 min):
need 200K/sec throughput = 500+ workers.

**Storage:**
In-app notifications: stored in DB for notification center.
Retention: 30 days. 500M/day × 30 days = 15B rows.
Sharded by user_id. Each row ~200 bytes = 3TB.
Partition by user_id (hash). Read by user (fast).

---

### 🧠 Mental Model / Analogy

> A notification system is like a government mailing system:
>
> - The post office (notification service) receives
>   letters (events) from senders (services).
> - It checks the recipient's mail preferences
>   (do-not-disturb, opt-outs).
> - It sorts letters by delivery method (email, phone,
>   physical mail) into separate bins (queues).
> - Couriers (workers) take letters from each bin
>   and deliver them.
> - If delivery fails (recipient moved), the courier
>   retries and eventually marks the address invalid.
>
> The challenge is ensuring every letter is delivered
> exactly once, even if the courier trips (worker crash).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A notification system sends alerts to users when
something happens - like when your food is delivered,
someone likes your post, or a payment is due. It handles
sending to millions of users across email, push
notifications, and SMS.

**Level 2 - How to use it (junior developer):**
Services publish notification events to a queue. Workers
consume the queue and send through the right channel
(APNs for iOS, FCM for Android, SendGrid for email).
Store user preferences in a database (opt-in/opt-out).
Check preferences before sending. Retry on failure.

**Level 3 - How it works (mid-level engineer):**
Channel-specific queues (Kafka topics) with parallel
workers per channel. Before delivery: check Redis-cached
user preferences, apply rate limits, run deduplication
(Redis NX set to prevent duplicate sends within a window).
Call third-party provider. On provider error: Kafka
consumer does not commit offset → Kafka redelivers
(at-least-once). Track device token validity (invalid
tokens deactivated after first failure to avoid wasted
calls).

**Level 4 - Why it was designed this way (senior/staff):**
Separate queues per channel because each channel has
different throughput characteristics, SLAs, and error
handling (APNs has different error codes than Twilio).
Channel isolation prevents a Twilio outage from blocking
email delivery. Worker count per channel tunable
independently. The deduplication window (30 minutes for
social notifications) is a product decision: users should
see "5 people liked your post" batched rather than 5
individual notifications. This batching logic sits in
the notification aggregation layer before the queue.

**Level 5 - Mastery (distinguished engineer):**
The notification system at Meta/LinkedIn scale has
additional layers: notification aggregation service
(batches "10 people liked your post" into 1 notification),
notification ranking (not all notifications sent
immediately - rank by predicted engagement, send
high-priority first), personalized timing (ML model
predicts optimal delivery time per user - when they
are most likely to open), A/B testing for notification
content, and notification fatigue scoring (reduce
frequency for users who never engage). The system
generates terabytes of delivery event logs per day
used by the ranking models. Delivery rate (delivered /
attempted) and open rate (opened / delivered) are
the two key business metrics.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ NOTIFICATION SYSTEM FLOW                            │
│                                                      │
│ Trigger:                                            │
│  Service A ──POST /notify──► Notification API      │
│  Validate + check user preferences                  │
│  Publish to channel queues:                         │
│    push-queue (Kafka partition by user_id)          │
│    email-queue                                      │
│    sms-queue                                        │
│                                                      │
│ Delivery (per channel):                             │
│  Push Workers (50 instances):                       │
│    consume push-queue                               │
│    check dedup (Redis NX) → skip if duplicate      │
│    check DND hours                                  │
│    call APNs/FCM                                    │
│    success → commit Kafka offset                   │
│    failure → retry (3x exp backoff) → DLQ          │
│                                                      │
│  Email Workers (20 instances):                      │
│    consume email-queue → call SendGrid              │
│                                                      │
│  In-App Workers (30 instances):                     │
│    consume inapp-queue → write to DB               │
│    push via WebSocket if user is online             │
│                                                      │
│ DLQ (Dead Letter Queue):                           │
│  Failed notifications after all retries            │
│  Alert: PagerDuty if DLQ depth > threshold         │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Notification service with deduplication**
```python
import redis
import json
from kafka import KafkaProducer, KafkaConsumer
from dataclasses import dataclass
from enum import Enum

r = redis.Redis()
producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda v: json.dumps(v).encode()
)

class Channel(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    INAPP = "inapp"

@dataclass
class NotificationEvent:
    notification_id: str
    user_id: int
    notification_type: str
    channel: Channel
    payload: dict
    dedup_window_secs: int = 1800  # 30 minutes

def send_notification(event: NotificationEvent):
    """Publish notification event to the right queue."""
    # Check user preferences (Redis cache → DB fallback)
    prefs = get_user_preferences(
        event.user_id, event.notification_type,
        event.channel)
    if not prefs.get("enabled", True):
        return  # User opted out of this type+channel

    # Rate limit: max N notifications per type per day
    rate_key = (
        f"notif:rate:{event.user_id}:"
        f"{event.notification_type}:{event.channel}"
    )
    daily_count = r.incr(rate_key)
    if daily_count == 1:
        r.expire(rate_key, 86400)  # Reset after 24h
    max_per_day = prefs.get("daily_limit", 10)
    if daily_count > max_per_day:
        return  # Rate limit exceeded

    # Publish to channel-specific Kafka topic
    topic = f"notifications-{event.channel.value}"
    producer.send(topic, event.__dict__)

def process_push_notification(event: dict):
    """Worker: consume from push queue, deliver."""
    user_id = event["user_id"]
    notif_type = event["notification_type"]
    entity_id = event["payload"].get("entity_id", "")

    # Deduplication check
    dedup_key = (
        f"notif:dedup:{user_id}:{notif_type}:{entity_id}"
    )
    window = event.get("dedup_window_secs", 1800)
    already_sent = not r.set(
        dedup_key, "1", nx=True, ex=window)
    if already_sent:
        return  # Duplicate: skip

    # Fetch device tokens for user
    device_tokens = get_device_tokens(user_id)
    for token in device_tokens:
        try:
            send_apns_or_fcm(token, event["payload"])
        except InvalidTokenError:
            deactivate_device_token(token)
        except ProviderError as e:
            # Re-raise to trigger Kafka retry
            raise e
```

**Example 2 - Missing preference check (BAD pattern)**
```python
# BAD: No preference check - user gets notified
# even if they opted out
def notify_bad(user_id: int, message: str):
    device_token = get_device_token(user_id)
    send_push_notification(device_token, message)
    # Sends even if user disabled push notifications
    # Sends even at 3am (no DND check)
    # No rate limit: user can receive 1000/day

# GOOD: Always check preferences, DND, rate limits
# before calling provider (see process_push_notification)
```

---

### ⚖️ Comparison Table

| Component | Simple Approach | Production Approach |
|---|---|---|
| Delivery | Direct API call from service | Queue (Kafka) → workers → provider |
| Reliability | Fire-and-forget (may drop) | At-least-once + deduplication |
| Preferences | None | Per-user, per-type, per-channel in Redis+DB |
| Rate limiting | None | Per-type daily limit per user |
| Fan-out | Loop in-process | Parallel Kafka consumers, sharded by user_id |
| Failure handling | None | Retry + DLQ + alert on DLQ depth |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Push notifications are delivered instantly | Push notifications go through APNs/FCM → carrier → device. End-to-end latency is typically 1-5 seconds but can be minutes during network issues. APNs and FCM do not guarantee delivery - if the device is offline, APNs stores the latest notification for 30 days (configurable) but may discard older ones. |
| At-least-once delivery prevents notification loss | At-least-once means each notification is delivered at least once - but also possibly more than once (duplicates on retry). You must implement deduplication to prevent users from receiving the same notification twice. Use Redis NX with an appropriate deduplication window. |
| Email delivery is reliable | Email delivery has significant variability. ISPs apply spam filters, rate limits, and domain reputation checks. A new sending domain may see 70%+ of emails in spam. Production systems use reputable transactional email providers (SES, SendGrid), warm up sending domains gradually, maintain suppression lists (bounces, unsubscribes), and track delivery/open rates. |

---

### 🚨 Failure Modes & Diagnosis

**Notification Flood After System Outage**

**Symptom:**
The notification service is down for 2 hours. When it
recovers, 10 million queued notifications are delivered
to users in 10 minutes - users receive 100s of stale
notifications. Users report "spam" and unsubscribe.

**Root Cause:** Kafka retained all notifications
during the outage. On recovery, workers consume at
full speed, sending all accumulated notifications
without staleness checks.

**Fix - Staleness TTL in notification events:**
```python
import time

@dataclass
class NotificationEvent:
    notification_id: str
    user_id: int
    notification_type: str
    channel: Channel
    payload: dict
    created_at: float = None    # Unix timestamp
    # Max age: discard if not delivered within this time
    ttl_seconds: int = 3600     # 1 hour

def process_notification_with_staleness_check(
    event: dict
):
    """Skip stale notifications after outage recovery."""
    created_at = event.get("created_at", 0)
    ttl = event.get("ttl_seconds", 3600)

    if time.time() - created_at > ttl:
        # Event is stale - discard silently
        # Log for observability but don't deliver
        log_metric("notification.discarded.stale",
                   type=event["notification_type"])
        return

    # Proceed with normal delivery
    process_push_notification(event)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Push vs Pull Architecture` - notification delivery
  is a push model (push to user devices)
- `Polling vs Webhooks` - in-app notifications can
  use polling or WebSocket push

**Builds On This (learn these next):**
- `Fan-Out on Write vs Read` - mass notification
  fan-out is the same problem as feed fan-out
- `Rate Limiting (System)` - protect users from
  notification spam with per-type rate limits

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CHANNELS    │ Push (APNs/FCM), Email (SES/SendGrid),    │
│             │ SMS (Twilio), In-App (WebSocket/DB)      │
├─────────────┼──────────────────────────────────────────  │
│ QUEUE       │ Kafka topics per channel. Partition by   │
│             │ user_id for ordering + parallel consume. │
├─────────────┼──────────────────────────────────────────  │
│ DEDUP       │ Redis SET NX per notification+entity+    │
│             │ user within dedup window (30 min).       │
├─────────────┼──────────────────────────────────────────  │
│ PREFERENCES │ Per-user, per-type, per-channel.         │
│             │ Redis cache (5 min TTL) + DB.            │
├─────────────┼──────────────────────────────────────────  │
│ RATE LIMIT  │ Daily per-type per-user. Redis INCR.     │
│             │ DND hours: no push 11pm-7am.             │
├─────────────┼──────────────────────────────────────────  │
│ RELIABILITY │ At-least-once (Kafka offset on success). │
│             │ DLQ for permanent failures. Alert.       │
├─────────────┼──────────────────────────────────────────  │
│ FAILURE     │ Outage → flood on recovery: add TTL to  │
│             │ events; discard stale on consumption.    │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Event → channel queue → worker →       │
│             │  prefer check + dedup → provider"       │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Chat System Design → Video Streaming     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Separate queues per channel (push, email, SMS, in-app).
   Channel isolation means a Twilio outage does not block
   email delivery. Workers per channel can be scaled and
   configured independently.
2. Always check user preferences before delivery (per-type,
   per-channel, DND hours, daily rate limit). Store
   preferences in Redis (5-min TTL cache) backed by a DB.
   Sending to opted-out users damages trust and deliverability.
3. Deduplication is required with at-least-once delivery.
   Use Redis SET NX with a window matching the notification
   type (30 minutes for social, 1 day for weekly digest).
   Add a TTL to notification events to discard stale
   notifications after an outage-recovery flood.

**Interview one-liner:**
"Notification system: producers POST events to the notification service,
which checks user preferences (Redis cache + DB) and publishes to
per-channel Kafka topics (push, email, SMS, in-app). Channel workers
consume in parallel, check Redis dedup (SET NX per user+type+entity
within a 30-min window), call third-party providers (APNs/FCM, SES,
Twilio). At-least-once via Kafka offset commit only on success. Failed
messages go to DLQ with alerting. Outage recovery flood prevention: add
TTL to every notification event, discard stale events on consumption."
