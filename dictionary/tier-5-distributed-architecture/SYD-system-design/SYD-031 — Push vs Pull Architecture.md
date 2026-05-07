---
layout: default
title: "Push vs Pull Architecture"
parent: "System Design"
nav_order: 31
permalink: /system-design/push-vs-pull-architecture/
number: "SYD-031"
category: System Design
difficulty: ★★★
depends_on: Distributed Systems, Messaging, Fan-Out on Write vs Read
used_by: Feed Systems, Event Delivery, Integration Design
related: Polling vs Webhooks, Fan-Out on Write vs Read, Event-Driven Architecture
tags:
  - architecture
  - messaging
  - advanced
  - integration
  - scalability
---

# SYD-031 — Push vs Pull Architecture

⚡ TL;DR — Push sends data proactively to consumers when events happen. Pull makes consumers ask for data when they need it. Push reduces latency but adds delivery complexity. Pull is simpler and more controllable but wastes requests and adds staleness.

| #711            | Category: System Design                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Systems, Messaging, Fan-Out on Write vs Read                 |                 |
| **Used by:**    | Feed Systems, Event Delivery, Integration Design                         |                 |
| **Related:**    | Polling vs Webhooks, Fan-Out on Write vs Read, Event-Driven Architecture |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Two systems need to exchange changing data. Should the producer send updates immediately, or should the consumer keep asking for them?

**TRADE-OFF:**
Push optimizes freshness. Pull optimizes simplicity and consumer control.

---

### 📘 Textbook Definition

**Push vs Pull Architecture:** Architectural choice for data movement between producer and consumer systems. In push architecture, producers send updates when state changes. In pull architecture, consumers request updates on their own schedule.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Push = "I’ll send you updates." Pull = "Ask me when you want updates."

**One analogy:**

> Newspaper delivery vs newsstand. Push is the newspaper arriving at your door every morning. Pull is you going to the newsstand when you decide you want one.

**One insight:**
The core question is who controls timing: producer or consumer.

---

### 🧠 Mental Model

```
PUSH:
  Producer notices change
    → immediately sends to consumers
  Pros: low latency, fresh data
  Cons: retries, backpressure, fanout complexity

PULL:
  Consumer wakes up on its own schedule
    → asks producer for current state
  Pros: simple, consumer controls load
  Cons: stale data, wasted requests
```

---

### 📶 Gradual Depth

**Level 1:** Push sends automatically. Pull asks manually.

**Level 2:** Use push when freshness matters. Use pull when occasional delay is acceptable.

**Level 3:** Push needs delivery guarantees, retries, idempotency, and backpressure. Pull needs scheduling, caching, and efficient query APIs.

**Level 4:** Push/pull shows up everywhere: replication, notification systems, feeds, integrations. Many real systems are hybrid: push for invalidation, pull for full data fetch.

---

### ⚙️ How It Works

```
PUSH FLOW
─────────
1. State changes in producer
2. Producer emits event or sends request
3. Consumer receives update
4. If consumer unavailable:
     retry / queue / dead-letter

PULL FLOW
─────────
1. Consumer wakes every N seconds
2. Consumer requests latest state
3. Producer responds with current data
4. Consumer stores/uses response

HYBRID FLOW
───────────
1. Producer sends lightweight push notification
2. Consumer pulls full payload only if needed
3. Cuts wasted traffic while keeping low latency
```

---

### 💻 Code Example

```python
class Producer:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def push_update(self, event):
        for callback in self.subscribers:
            callback(event)


class PullConsumer:
    def __init__(self, client):
        self.client = client

    def sync(self):
        latest = self.client.get("/events/latest")
        return latest


def on_event(event):
    print(f"push received: {event}")


producer = Producer()
producer.subscribe(on_event)
producer.push_update({"type": "order_created", "id": 123})
```

---

### ⚖️ Comparison Table

| Aspect                | Push     | Pull                        |
| --------------------- | -------- | --------------------------- |
| Freshness             | High     | Depends on polling interval |
| Producer complexity   | Higher   | Lower                       |
| Consumer control      | Lower    | Higher                      |
| Wasted traffic        | Lower    | Higher                      |
| Backpressure handling | Required | Easier                      |

---

### ⚠️ Common Misconceptions

| Misconception           | Reality                                                        |
| ----------------------- | -------------------------------------------------------------- |
| "Push is always better" | No. Push is harder to operate and debug.                       |
| "Pull is always stale"  | Not necessarily. Fast polling plus caching can be good enough. |
| "You must choose one"   | Many systems use push notification plus pull fetch.            |

---

### 🚨 Failure Modes

**Failure Mode 1: Push overwhelms slow consumers**

**Symptom:**
Producer emits faster than consumers can process. Queues grow, retries pile up.

**Prevention:**
Backpressure, rate limits, buffering, dead-letter queues.

---

**Failure Mode 2: Pull causes request storms**

**Symptom:**
10,000 consumers poll every second even when nothing changes.

**Prevention:**
Long polling, caching headers, exponential backoff, event hints.

---

### 📌 Quick Reference

```
Push vs Pull:
  Push: low latency, higher delivery complexity
  Pull: simpler, more stale, consumer-controlled
  Hybrid: push signal + pull payload
```

---

### 🧠 Questions

**Q1.** If 99% of data checks return "no change," should you still use pull?

**Q2.** If consumers are mobile devices with intermittent connectivity, which model is safer?
