---
layout: default
title: "Notification System Design"
parent: "System Design"
nav_order: 47
permalink: /system-design/notification-system-design/
id: SYD-047
category: System Design
difficulty: ★★★
depends_on: Queues, Push vs Pull Architecture, Rate Limiting
used_by: Product Messaging, Alerts, Engagement Systems
related: Fan-Out on Write vs Read, Polling vs Webhooks, Chat System Design
tags:
  - system-design
  - notifications
  - queues
  - advanced
  - messaging
---

# SYD-047 — Notification System Design

⚡ TL;DR — A notification system accepts events, applies user preferences and channel rules, then delivers messages through email, SMS, push, or in-app channels. The hard parts are fan-out, deduplication, rate control, and delivery observability.

| #722            | Category: System Design                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Queues, Push vs Pull Architecture, Rate Limiting                  |                 |
| **Used by:**    | Product Messaging, Alerts, Engagement Systems                     |                 |
| **Related:**    | Fan-Out on Write vs Read, Polling vs Webhooks, Chat System Design |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Apps need to notify millions of users quickly without spamming, duplicating, or violating preferences.

**SOLUTION:**
Separate event ingestion, preference evaluation, channel dispatch, and delivery tracking.

---

### 📘 Textbook Definition

**Notification System Design:** System design problem involving event-driven generation, routing, scheduling, and delivery of user notifications across multiple channels with reliability and preference enforcement.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Take events like `order_shipped` and turn them into the right message on the right channel for the right user.

**One analogy:**

> A mailroom sorting incoming letters into email, text, and paper delivery while checking each recipient’s do-not-contact rules.

**One insight:**
The system is usually more about suppression and routing than about message rendering.

---

### 🧠 Mental Model

```
event -> queue -> preference/filtering -> channel-specific workers -> provider -> delivery status
```

---

### 📶 Gradual Depth

**Level 1:** Send a message when an event happens.

**Level 2:** Respect preferences and per-channel quotas.

**Level 3:** Use queues, retries, dedupe, template rendering, and dead-letter handling.

**Level 4:** Large systems treat notifications as a policy engine plus a delivery pipeline, not just a message sender.

---

### ⚙️ How It Works

```
1. Producer emits business event
2. Notification service consumes event
3. Resolve recipients and preferences
4. Generate channel jobs
5. Dispatch via push/email/SMS providers
6. Track sent, delivered, opened, failed states
```

---

### 💻 Code Example

```python
def build_notifications(event, user_prefs):
    channels = []
    if user_prefs.get("push"):
        channels.append("push")
    if user_prefs.get("email"):
        channels.append("email")
    return [{"channel": ch, "event": event} for ch in channels]
```

---

### ⚖️ Comparison Table

| Concern                     | Common answer                   |
| --------------------------- | ------------------------------- |
| Burst handling              | queues                          |
| User preference enforcement | policy layer                    |
| Duplicate suppression       | idempotency key / dedupe window |
| Provider failure            | retry + fallback channel        |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                     |
| -------------------------------------- | ----------------------------------------------------------- |
| "Just send every event"                | Unfiltered notification volume destroys product trust.      |
| "Delivery success equals user seen it" | Providers report accepted/delivered; attention is separate. |

---

### 🚨 Failure Modes

**Failure Mode 1: Notification storm**

**Symptom:**
One backend incident triggers thousands of near-identical messages per user.

**Prevention:**
Grouping, cooldowns, dedupe windows, alert aggregation.

---

**Failure Mode 2: Provider outage**

**Symptom:**
SMS or push provider fails and jobs pile up.

**Prevention:**
Retries with backoff, DLQ, alternate provider, status visibility.

---

### 📌 Quick Reference

```
Notification design:
  ingest events
  apply preferences
  dedupe and throttle
  dispatch by channel
  track delivery outcomes
```

---

### 🧠 Questions

**Q1.** Which matters more in your product: guaranteed delivery or avoiding over-notification?

**Q2.** When should a notification be aggregated instead of sent immediately?
