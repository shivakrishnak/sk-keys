---
layout: default
title: "Polling vs Webhooks"
parent: "System Design"
nav_order: 32
permalink: /system-design/polling-vs-webhooks/
number: "SYD-032"
category: System Design
difficulty: ★★☆
depends_on: Push vs Pull Architecture, HTTP APIs, Event Delivery
used_by: SaaS Integrations, Notifications, Sync Systems
related: Push vs Pull Architecture, Idempotency Key, Retries
tags:
  - integration
  - webhooks
  - polling
  - system-design
  - apis
---

# SYD-032 — Polling vs Webhooks

⚡ TL;DR — Polling repeatedly asks a server whether something changed. Webhooks let the server call you when it changes. Polling is simpler and safer for consumers. Webhooks are more efficient and lower latency, but need retries, signatures, and idempotency.

| #712            | Category: System Design                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Push vs Pull Architecture, HTTP APIs, Event Delivery |                 |
| **Used by:**    | SaaS Integrations, Notifications, Sync Systems       |                 |
| **Related:**    | Push vs Pull Architecture, Idempotency Key, Retries  |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Your system needs to know when a remote system changes state. Do you keep asking, or wait for a callback?

**TRADE-OFF:**
Polling is easy to control. Webhooks reduce wasted requests and improve freshness.

---

### 📘 Textbook Definition

**Polling vs Webhooks:** Two common integration patterns for change notification. Polling is consumer-driven repeated fetching. Webhooks are producer-driven HTTP callbacks triggered on events.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Polling asks "anything new yet?" Webhooks say "something new happened."

**One analogy:**

> Polling is calling a restaurant every 10 minutes to ask whether your order is ready. Webhooks are the restaurant texting you when it is.

**One insight:**
Polling wastes work during quiet periods. Webhooks shift complexity into delivery guarantees.

---

### 🧠 Mental Model

```
POLLING:
  Consumer timer → GET /updates?since=t
  Pros: simple, consumer-controlled
  Cons: stale + many empty requests

WEBHOOKS:
  Producer event → POST consumer callback URL
  Pros: fast, efficient
  Cons: retries, signatures, downtime handling
```

---

### 📶 Gradual Depth

**Level 1:** Polling repeatedly checks. Webhooks notify automatically.

**Level 2:** Polling fits low-frequency changes. Webhooks fit event-driven workflows.

**Level 3:** Webhooks require authentication, replay protection, idempotency keys, and retry strategy. Polling benefits from incremental cursors and backoff.

**Level 4:** Mature integrations often support both: webhook for low-latency hint, polling as repair path when deliveries fail.

---

### ⚙️ How It Works

```
POLLING
1. Consumer stores last_seen timestamp or cursor
2. Every N seconds: GET /events?after=cursor
3. Producer returns new changes
4. Consumer advances cursor

WEBHOOKS
1. Consumer registers callback URL
2. Producer sends POST on event
3. Consumer validates signature
4. Consumer processes idempotently
5. On failure: producer retries

HYBRID
1. Webhook received
2. Consumer immediately polls details endpoint
3. Polling also runs periodically for missed events
```

---

### 💻 Code Example

```python
import hmac
import hashlib


def verify_webhook(secret, payload, signature):
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


class PollingClient:
    def __init__(self, api):
        self.api = api
        self.cursor = None

    def sync(self):
        response = self.api.get_events(after=self.cursor)
        for event in response["items"]:
            handle(event)
        self.cursor = response["next_cursor"]
```

---

### ⚖️ Comparison Table

| Aspect              | Polling         | Webhooks                         |
| ------------------- | --------------- | -------------------------------- |
| Latency             | Interval-bound  | Near real-time                   |
| Empty work          | High            | Low                              |
| Consumer control    | High            | Lower                            |
| Delivery complexity | Lower           | Higher                           |
| Recovery            | Easy to re-poll | Needs retry/dead-letter strategy |

---

### ⚠️ Common Misconceptions

| Misconception                | Reality                                    |
| ---------------------------- | ------------------------------------------ |
| "Webhooks are always better" | No. They are harder to secure and operate. |
| "Polling is primitive"       | It is often the most robust fallback.      |

---

### 🚨 Failure Modes

**Failure Mode 1: Duplicate webhook delivery**

**Symptom:**
Consumer processes the same event multiple times.

**Prevention:**
Idempotency keys, event IDs, dedupe store.

---

**Failure Mode 2: Polling stampede**

**Symptom:**
All clients poll on the minute, causing synchronized load spikes.

**Prevention:**
Jitter, staggered schedules, caching, long polling.

---

### 📌 Quick Reference

```
Polling: simpler, wasteful, controllable
Webhooks: efficient, faster, more operationally complex
Best practical answer: support both when integration matters
```

---

### 🧠 Questions

**Q1.** If your consumers cannot expose public endpoints, can they still use webhooks?

**Q2.** If webhook delivery is not guaranteed, what repair loop do you add?
