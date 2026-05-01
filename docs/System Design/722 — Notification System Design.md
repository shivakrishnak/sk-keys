---
layout: default
title: "Notification System Design"
parent: "System Design"
nav_order: 722
permalink: /system-design/notification-system-design/
number: "722"
category: System Design
difficulty: ★★★
depends_on: "Message Queues, Push vs Pull Architecture, Rate Limiting (System)"
used_by: "System Design Interview"
tags: #advanced, #system-design, #interview, #notifications, #mobile
---

# 722 — Notification System Design

`#advanced` `#system-design` `#interview` `#notifications` `#mobile`

⚡ TL;DR — **Notification System Design** delivers billions of targeted notifications across channels (push, email, SMS) using provider-specific adapters, Kafka fan-out, per-user preference filtering, and idempotency to prevent duplicates.

| #722            | Category: System Design                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Message Queues, Push vs Pull Architecture, Rate Limiting (System) |                 |
| **Used by:**    | System Design Interview                                           |                 |

---

### 📘 Textbook Definition

A **Notification System** is infrastructure that routes, queues, and delivers personalised messages to users across multiple delivery channels: mobile push (APNs for iOS, FCM for Android), email (SendGrid, SES), SMS (Twilio), and in-app notifications. Key design considerations include: (1) **fan-out** from a single trigger event to notifications across multiple channels simultaneously; (2) **provider integration** with third-party delivery services and handling their failure modes (delivery receipts, bounced tokens); (3) **user preference management** (opt-in/out per channel per notification type); (4) **rate limiting and digest** (prevent notification fatigue — batch or suppress excessive notifications); (5) **idempotency** (events re-processed on failure must not send duplicate notifications); (6) **delivery tracking** (sent, delivered, opened). At scale: billions of notifications per day, each with different delivery guarantees and latency requirements (push: < 1 second; email: < 10 seconds; SMS: < 30 seconds).

---

### 🟢 Simple Definition (Easy)

Notification System: when something happens (new message, sale, order shipped), the system decides WHO to notify, HOW (push, email, SMS), WHEN (immediately, or batched at 9 AM), and ensures the notification arrives EXACTLY ONCE (not twice). Think of it as an intelligent, scalable postal service: it routes packages (notifications) to different carriers (APNs, FCM, Twilio), retries failed deliveries, respects do-not-disturb settings, and tracks every delivery.

---

### 🔵 Simple Definition (Elaborated)

Amazon ships an order: triggers event → Notification Service receives event → checks user preferences ("Sarah wants: push + email; no SMS") → creates two notifications → queues them → Email Worker sends via SendGrid → Push Worker sends via APNs (iPhone) or FCM (Android). If APNs returns "device token expired" → update token in DB, retry with new token. If email bounces → mark email as undeliverable. Track all delivery statuses in DynamoDB. Aggregate: "85% of daily deal emails opened today." This pipeline handles 1 billion notifications per day across 500M users.

---

### 🔩 First Principles Explanation

**Notification system: components, flow, and failure handling:**

```
SYSTEM COMPONENTS:

  1. EVENT PRODUCERS (triggers):
     - Application services: "order shipped", "new message", "payment received"
     - Marketing platform: "send promotion to segment X"
     - Alerting systems: "CPU > 90% on prod server"

  2. NOTIFICATION SERVICE (orchestrator):
     - Receives trigger events
     - Resolves target users (user ID → device tokens, email, phone)
     - Checks user notification preferences
     - Applies rate limiting and digest rules
     - Publishes to channel-specific Kafka topics

  3. CHANNEL WORKERS (delivery agents):
     - Push Worker: APNs (iOS) + FCM (Android)
     - Email Worker: SendGrid / AWS SES
     - SMS Worker: Twilio / AWS SNS
     - In-App Worker: WebSocket or SSE to connected clients

  4. PROVIDER ADAPTERS (external services):
     - Apple APNs: device_token + payload → HTTP/2 API
     - Google FCM: registration_token + payload → HTTP API
     - SendGrid: email address + template → HTTP API
     - Twilio: phone_number + message → HTTP API

  5. DELIVERY TRACKING (audit + analytics):
     - DynamoDB: notification_id → status (QUEUED/SENT/DELIVERED/OPENED/FAILED)
     - Delivery callbacks (FCM/APNs push receipts, email open tracking pixels)

DATA MODEL:

  users table:
    user_id, name, email, phone_number

  device_tokens table:
    token_id, user_id, device_type (IOS/ANDROID), token, is_active, updated_at
    -- Multiple devices per user (phone, tablet)

  notification_preferences table:
    user_id, notification_type, channel, is_enabled
    -- e.g., user 123, "marketing", "push", enabled=false
    --       user 123, "order_updates", "email", enabled=true

  notifications table (tracking):
    notification_id, user_id, type, channel, payload, status, created_at, sent_at
    -- Idempotency: notification_id = idempotency key (prevent duplicates)

NOTIFICATION FLOW:

  1. Trigger: Order shipped (order_id=456, user_id=123)

  2. Notification Service:
     a. Resolve user: user_id=123 → {email: "alice@example.com", devices: [token1, token2]}
     b. Check preferences: user 123 + "order_updates" + "push" → enabled
                           user 123 + "order_updates" + "email" → enabled
     c. Check rate limits: user 123 had 0 notifications last hour → ok
     d. Create notification records (with idempotency check):
        INSERT INTO notifications (notification_id, ...)
        ON CONFLICT (notification_id) DO NOTHING  ← idempotency
     e. Publish to Kafka:
        Topic "notifications.push": {notification_id, user_id, token1, payload}
        Topic "notifications.push": {notification_id, user_id, token2, payload}
        Topic "notifications.email": {notification_id, user_id, "alice@...", payload}

  3. Push Worker (consumes "notifications.push"):
     a. Send to APNs/FCM
     b. APNs response: 200 OK → update status = SENT
     c. APNs response: 410 Unregistered → device_token deactivated, skip notification
     d. APNs response: 503 Service Unavailable → retry with exponential backoff

  4. Email Worker (consumes "notifications.email"):
     a. Render email template with personalised content
     b. Send to SendGrid API
     c. SendGrid async webhook: "delivered" → status = DELIVERED
     d. SendGrid webhook: "bounced" → mark email as undeliverable, remove from future sends

IDEMPOTENCY (prevent duplicate notifications):

  Scenario: Kafka consumer processes order_shipped event, sends push notification,
            but crashes before committing Kafka offset.
  On restart: re-processes same event → sends push notification AGAIN.

  Prevention:
    notification_id = deterministic hash(event_id + user_id + channel + type)
    Before sending: INSERT INTO notifications (notification_id, ...) ON CONFLICT DO NOTHING
    After conflict: notification already sent → skip

    Redis set for recent notifications (TTL 24 hours):
      SADD sent:{today} notification_id → already in set → skip
      Fast O(1) check before DB write

RATE LIMITING AND DIGEST:

  Per-user rate limit: max 10 push notifications per hour
    If exceeded: queue for digest notification ("You have 5 new updates")

  Quiet hours: respect user timezone
    User in Tokyo (JST): no push between 11 PM and 8 AM JST
    Queue notifications → deliver at 8 AM JST

  Digest rules:
    "3 separate 'liked your post' notifications in 1 hour" → merge into
    "Alice, Bob, and 1 other liked your photo"

  Implementation:
    Digest Worker: runs every 5 minutes per user
    Checks: pending notifications in digest queue
    If >1 of same type: merge into single digest notification

DEVICE TOKEN MANAGEMENT:

  Push notifications require a fresh device token per device.

  iOS (APNs):
    App registers → APNs issues device token (changes on app reinstall).
    App sends token to backend on launch.
    APNs: 410 response → token expired/invalid → deactivate token in DB.

  Android (FCM):
    Similar: registration token refreshed periodically.
    FCM: "NotRegistered" error → deactivate token.

  Multi-device handling:
    User on 3 devices → 3 tokens → send to all 3.
    Only ONE device receives the notification (user taps it → acknowledge).
    Acknowledged on device 1: dismiss pending on devices 2 and 3 (in-app state sync).
    For push: send to all devices (APNs/FCM deduplicate on their end if collapse_key set).

ARCHITECTURE DIAGRAM:

  [Event Producers] → [Notification Service] → [Kafka Topics]
                                                    │
                           ┌────────────────────────┤
                           │          │              │
                     [Push Worker] [Email Worker] [SMS Worker]
                           │          │              │
                        [APNs/FCM] [SendGrid]    [Twilio]
                           │
                     [Delivery Tracking DB]
                     (DynamoDB / Cassandra)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT dedicated notification system:

- Services send notifications directly (tight coupling, no retry, no preference management)
- No deduplication: event re-processing sends duplicate notifications
- No rate limiting: one bug sends 10,000 notifications to same user in 1 second

WITH notification system:
→ Decoupled delivery: services fire events; notification system handles routing, retry, preferences
→ Idempotency: same event processed multiple times → single notification delivered
→ Rate limiting + digest: notification fatigue prevented programmatically

---

### 🧠 Mental Model / Analogy

> A postal sorting office. Packages (notifications) arrive from various senders (application services). The sorting office (Notification Service): checks the recipient's delivery preferences (does Mrs. Johnson accept SMS?), routes each package to the correct carrier (UPS for parcels = FCM, Royal Mail for letters = email, DHL for urgent = SMS). Each carrier has a tracking system. If a package is undeliverable (APNs token expired = "address not found"), the sorting office is notified and updates its records. Rate limiting = "no more than 10 packages per day to the same recipient or they refuse delivery."

"Packages arriving from senders" = trigger events from application services
"Sorting office routing to carriers" = Notification Service → Kafka → channel workers
"Recipient delivery preferences" = user notification preference table
"Carrier tracking" = delivery status in DynamoDB (SENT → DELIVERED → OPENED)
"Address not found → update records" = APNs 410 → deactivate device token

---

### ⚙️ How It Works (Mechanism)

**Push notification with APNs (Java):**

```java
@Service
public class ApplePushNotificationService {

    private final ApnsClient apnsClient;
    private static final String BUNDLE_ID = "com.example.myapp";

    public void sendPushNotification(String deviceToken, NotificationPayload payload) {
        // Build APNs payload:
        ApnsPayloadBuilder payloadBuilder = new SimpleApnsPayloadBuilder()
            .setAlertTitle(payload.getTitle())
            .setAlertBody(payload.getBody())
            .setBadgeNumber(payload.getBadgeCount())
            .setSound("default")
            .addCustomProperty("notification_id", payload.getNotificationId())
            .addCustomProperty("type", payload.getType());

        SimpleApnsPushNotification notification = new SimpleApnsPushNotification(
            deviceToken,
            BUNDLE_ID,
            payloadBuilder.build(),
            Instant.now().plus(24, ChronoUnit.HOURS),  // expiry (24h)
            DeliveryPriority.IMMEDIATE,                  // send immediately
            PushType.ALERT
        );

        // Send asynchronously:
        apnsClient.sendNotification(notification).whenComplete((response, cause) -> {
            if (cause != null) {
                log.error("APNs network error: {}", cause.getMessage());
                // Schedule retry with backoff
                scheduleRetry(deviceToken, payload);
                return;
            }

            if (response.isAccepted()) {
                // APNs accepted for delivery (not yet delivered to device)
                updateNotificationStatus(payload.getNotificationId(), "SENT");
            } else {
                String reason = response.getRejectionReason().orElse("unknown");
                log.warn("APNs rejected notification: {} for token {}", reason, deviceToken);

                if ("Unregistered".equals(reason) || "BadDeviceToken".equals(reason)) {
                    // Device token no longer valid → deactivate:
                    deactivateDeviceToken(deviceToken);
                } else if ("TooManyRequests".equals(reason)) {
                    // Rate limited by APNs → back off:
                    scheduleRetry(deviceToken, payload, Duration.ofSeconds(60));
                }
                updateNotificationStatus(payload.getNotificationId(), "FAILED_" + reason);
            }
        });
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Application event (order shipped, new message)
        │
        ▼
Notification System Design ◄──── (you are here)
(fan-out, preference filtering, delivery)
        │
        ├── Message Queues (Kafka fan-out to channel workers)
        ├── Idempotency Key (prevent duplicate notifications on retry)
        └── Rate Limiting (notification fatigue prevention)
```

---

### 💻 Code Example

**Notification preference check and fan-out:**

```java
@Service
public class NotificationOrchestrator {

    @Autowired private UserPreferenceRepository preferenceRepo;
    @Autowired private DeviceTokenRepository tokenRepo;
    @Autowired private KafkaTemplate<String, NotificationMessage> kafka;
    @Autowired private NotificationRepository notificationRepo;

    public void processEvent(NotificationEvent event) {
        String notificationId = generateIdempotencyKey(event);

        // Idempotency check:
        if (notificationRepo.existsByIdempotencyKey(notificationId)) {
            log.info("Notification {} already sent — skipping", notificationId);
            return;
        }

        List<Long> userIds = resolveTargetUsers(event);

        for (long userId : userIds) {
            List<NotificationChannel> enabledChannels =
                preferenceRepo.getEnabledChannels(userId, event.getType());

            for (NotificationChannel channel : enabledChannels) {
                switch (channel) {
                    case PUSH -> {
                        List<String> tokens = tokenRepo.getActiveTokens(userId);
                        for (String token : tokens) {
                            kafka.send("notifications.push", new PushMessage(
                                notificationId, userId, token, event.buildPushPayload()));
                        }
                    }
                    case EMAIL -> {
                        String email = userRepo.getEmail(userId);
                        kafka.send("notifications.email", new EmailMessage(
                            notificationId, userId, email, event.buildEmailPayload()));
                    }
                    case SMS -> {
                        String phone = userRepo.getPhone(userId);
                        kafka.send("notifications.sms", new SmsMessage(
                            notificationId, userId, phone, event.buildSmsPayload()));
                    }
                }
            }
        }
    }

    private String generateIdempotencyKey(NotificationEvent event) {
        // Deterministic: same event always generates same key
        return DigestUtils.md5Hex(event.getEventId() + ":" + event.getType());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Push notifications are delivered in real-time       | APNs and FCM deliver notifications on a best-effort basis. If the device is offline, the notification is queued by APNs/FCM for up to 28 days (APNs) or indefinitely (FCM with TTL). If a newer notification arrives for the same collapse key, the older one is replaced. "Real-time" delivery only happens if the device is online and connected                                                                                       |
| A single notification table can handle all channels | Push, email, and SMS have fundamentally different schemas, delivery flows, and status models. Email has: bounce, spam, open, click events. Push has: device token management, silent notifications, badge counts. SMS has: delivery receipts, carrier errors. A shared notifications table with nullable columns for each channel becomes unmanageable. Separate tables or separate services per channel are cleaner                     |
| Notification delivery receipts are reliable         | APNs and FCM provide delivery receipts, but they are not 100% reliable. A device may receive a notification without a receipt reaching the server (network issue). Email open tracking uses 1×1 pixel images — blocked by email clients. "Delivered" in most notification systems means "accepted by the provider" (APNs, FCM), not "shown on the user's screen." True delivery verification requires app-side confirmation (in-app ACK) |
| User preference checks are simple                   | User preference management is complex at scale: per-notification-type × per-channel × per-user × quiet hours × frequency caps × segmentation. A user may have 50+ notification types and 4 channels = 200 preference rows. Query for "what channels does user 123 want for type X" must be fast (in hot path). Solution: cache preferences in Redis per user, invalidate on preference change                                            |

---

### 🔥 Pitfalls in Production

**Notification storm from marketing campaign bug:**

```
PROBLEM: Marketing sends campaign to 10M users, but due to a bug,
         each user receives the notification 50 times

  Campaign: "Holiday sale — 50% off!"
  Bug: event published to Kafka 50 times (retry loop didn't check for success)

  Result:
    10M users × 50 push notifications = 500M notifications in 2 minutes
    APNs/FCM rate limit exceeded → provider throttles → cascade retry → more duplicates
    Users: 50 "Holiday sale" notifications → uninstall the app

PREVENTION:

  1. IDEMPOTENCY KEY PER CAMPAIGN:
     campaign_id = "holiday_sale_2024_12"
     notification_id = hash(campaign_id + user_id)

     Before sending: INSERT INTO notifications (notification_id, ...) ON CONFLICT DO NOTHING
     → 50 duplicate events → only 1 notification actually sent (other 49: conflict, skip)

  2. RATE LIMITING PER USER:
     Max 3 marketing notifications per day per user.
     Campaign: check rate limit before enqueuing → user already received 3 today → skip.

  3. CAMPAIGN SAFEGUARDS:
     Pre-send checklist: require human approval for campaigns > 1M users.
     Canary: send to 0.1% of users first → wait 30 minutes → check unsubscribe/uninstall rate → proceed.

  4. DUPLICATE DETECTION AT PROVIDER LEVEL:
     FCM collapse_key: "campaign:holiday_sale_2024_12"
     → If 50 notifications with same collapse_key reach FCM for same device:
       FCM delivers only the LATEST one (deduplicates at device level).
     APNs apns-collapse-id header: same behavior.
     This is the last line of defense (not a substitute for application-level idempotency).
```

---

### 🔗 Related Keywords

- `Message Queues` — Kafka fan-out from notification service to channel-specific workers
- `Idempotency Key` — prevents duplicate notifications when events are re-processed
- `Rate Limiting (System)` — notification frequency caps per user per channel
- `Push vs Pull Architecture` — push notifications (server-initiated) vs in-app polling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Kafka fan-out → channel workers → APNs/   │
│              │ FCM/SendGrid; idempotency key per notif   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-channel notifications at scale;     │
│              │ decoupled delivery from application logic │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ No idempotency on retry; no user prefs;   │
│              │ direct provider calls without queuing     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Postal sorting office — routes packages  │
│              │  to correct carriers, respects prefs,     │
│              │  tracks every delivery."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Message Queues → Idempotency Key          │
│              │ → APNs/FCM Deep Dive                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design the "quiet hours" feature for the notification system: users in different timezones should not receive marketing push notifications between 11 PM and 8 AM local time. The system processes 10,000 notification events per second. How do you store timezone per user? How do you implement the quiet hours check efficiently without blocking the hot path? What happens to notifications that arrive during quiet hours — are they queued for 8 AM delivery or discarded? How do you handle users who travel between timezones?

**Q2.** A user's iOS device token has become invalid (app deleted and reinstalled). The backend still has the old token. You send a push notification using the old token → APNs returns `410 Unregistered`. Your system deactivates the old token. Two hours later, the user reinstalls the app and registers a new token with your backend. Describe the full lifecycle: how does the app get a new APNs token? How does it send this token to your backend? How does your backend update the device_tokens table (replace old with new, or add new alongside old)? What prevents the user from receiving duplicate notifications during the token transition period?
