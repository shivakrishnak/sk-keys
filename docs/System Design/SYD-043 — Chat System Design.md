---
layout: default
title: "Chat System Design"
parent: "System Design"
nav_order: 43
permalink: /system-design/chat-system-design/
number: "SYD-043"
category: System Design
difficulty: ★★★
depends_on: WebSockets, Message Queues, Notification System Design
used_by: Messaging Apps, Collaboration Tools, Support Platforms
related: Notification System Design, Push vs Pull Architecture, Fan-Out on Write vs Read
tags:
  - system-design
  - chat
  - realtime
  - advanced
  - messaging
---

# SYD-043 — Chat System Design

⚡ TL;DR — A chat system handles real-time message delivery, ordering, unread state, presence, and offline sync. The hard parts are connection scale, message fan-out, mobile intermittency, and maintaining a useful ordering model without over-promising global consistency.

| #723            | Category: System Design                                                         | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | WebSockets, Message Queues, Notification System Design                          |                 |
| **Used by:**    | Messaging Apps, Collaboration Tools, Support Platforms                          |                 |
| **Related:**    | Notification System Design, Push vs Pull Architecture, Fan-Out on Write vs Read |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Users expect messages to arrive instantly, show in order, and survive disconnects.

**SOLUTION:**
Persist canonical messages, stream real-time delivery when possible, and sync missed events later.

---

### 📘 Textbook Definition

**Chat System Design:** System design problem centered on real-time and offline-capable messaging infrastructure for one-to-one or group conversations, including storage, delivery, synchronization, and presence.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store every message once, deliver quickly to connected users, and backfill anyone who was offline.

**One analogy:**

> A post office plus live courier service: if the recipient is home, hand them the letter now; otherwise keep it safely and deliver later.

**One insight:**
Persistence is the source of truth. Sockets are only the fast path.

---

### 🧠 Mental Model

```
sender -> chat gateway -> message store -> fanout/delivery service -> recipient socket or offline queue
```

---

### 📶 Gradual Depth

**Level 1:** Send and receive messages.

**Level 2:** Use WebSockets for online users and push notifications for offline users.

**Level 3:** Maintain per-conversation sequence numbers, ack states, unread counters, and device sync.

**Level 4:** Large chat systems optimize connection management separately from message storage and usually scope ordering guarantees to a conversation, not globally.

---

### ⚙️ How It Works

```
1. Client sends message to gateway
2. Server assigns conversation sequence/id
3. Message stored durably
4. Online recipients receive over socket
5. Offline recipients get push notification
6. On reconnect, client syncs from last seen cursor
```

---

### 💻 Code Example

```python
class Conversation:
    def __init__(self):
        self.sequence = 0
        self.messages = []

    def add_message(self, sender, text):
        self.sequence += 1
        message = {"seq": self.sequence, "sender": sender, "text": text}
        self.messages.append(message)
        return message
```

---

### ⚖️ Comparison Table

| Concern             | Common answer             |
| ------------------- | ------------------------- |
| Realtime delivery   | WebSockets                |
| Offline reliability | durable message store     |
| Ordering            | per conversation sequence |
| Presence            | ephemeral state store     |

---

### ⚠️ Common Misconceptions

| Misconception                     | Reality                                                    |
| --------------------------------- | ---------------------------------------------------------- |
| "WebSocket means no message loss" | Sockets drop. Storage and replay still matter.             |
| "Global ordering is required"     | Conversation-local ordering is usually enough and cheaper. |

---

### 🚨 Failure Modes

**Failure Mode 1: Duplicate delivery across reconnects**

**Symptom:**
User reconnects and sees the same message rendered twice.

**Prevention:**
Stable message IDs and client-side dedupe by sequence.

---

**Failure Mode 2: Presence overload**

**Symptom:**
Every online/offline toggle floods subscribers and backend stores.

**Prevention:**
Coarse presence, TTL-based ephemeral state, batching.

---

### 📌 Quick Reference

```
Chat design:
  durable message store first
  sockets for fast path
  per-conversation ordering
  offline sync via cursor replay
```

---

### 🧠 Questions

**Q1.** Should message ordering be guaranteed across all devices or only within one conversation timeline?

**Q2.** How much presence precision does your product really need?
