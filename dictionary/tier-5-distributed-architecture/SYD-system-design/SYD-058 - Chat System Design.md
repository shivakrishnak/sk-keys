---
id: SYD-031
title: Chat System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-067
used_by:
related: SYD-067, SYD-023, SYD-059
tags:
  - architecture
  - advanced
  - distributed
  - async
status: complete
version: 2
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /syd/chat-system-design/
---

# SYD-068 - Chat System Design

⚡ TL;DR - A chat system delivers messages in real time to online
users, durably stores every message, and syncs offline users when
they reconnect.

| Field           | Detail                            |
| :-------------- | :-------------------------------- |
| **Depends on:** | SYD-067 - Notification System Design |
| **Used by:**    | -                                 |
| **Related:**    | SYD-067, SYD-023, SYD-059        |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Early internet communication required both parties to be
simultaneously online. If the recipient was offline, the message
was lost. ICQ and early messaging apps stored messages locally on
the sender's device only - switching devices meant losing history.

**THE BREAKING POINT:**
Mobile changed everything. Users are intermittently connected,
switch between phone, tablet, and laptop, and expect the same
conversation history everywhere. A system that loses messages on
disconnect is unusable for modern communication.

**THE INVENTION MOMENT:**
The core insight: separate the delivery path from the storage path.
Persist every message to a canonical store first. Use sockets for
the fast delivery path when the recipient is online. Replay from
the store when they reconnect. Presence becomes a hint, not a
requirement for delivery.

**EVOLUTION:**
Real-time chat evolved from centralised IRC servers (1988) through
peer-to-peer ICQ (1996) to today's WebSocket-based distributed
architectures. WhatsApp (2009) demonstrated that a lean engineering
team could scale to billions of users with Erlang's actor model.
Slack (2013) popularised rich presence and integrations for
workplace collaboration. The architectural challenge evolved from
simple message delivery to multi-device synchronisation, end-to-end
encryption, rich media handling, and regulatory compliance. Modern
chat systems are the proving ground for distributed systems
patterns: consistent messaging requires solving ordering, delivery
guarantees, and presence at internet scale.

---

### 📘 Textbook Definition

**Chat System Design** is a system design problem centred on
real-time and offline-capable messaging infrastructure for one-to-one
or group conversations, including message storage, reliable delivery,
multi-device synchronisation, and presence state management.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store every message once, deliver instantly to online users, and
replay to anyone who was offline.

**One analogy:**

> A postal service with an express courier option: if the recipient
> is home, hand the letter over immediately; if not, keep it safely
> in the sorting office and deliver it when they next open the door.

**One insight:**
Persistence is the source of truth. WebSockets are only the fast
path. If the socket drops, the message store is what keeps the
conversation intact.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every message must be stored durably before acknowledgement.
2. Delivery order within a conversation must be consistent across
   all devices of the same user.
3. A recipient offline today must receive all messages when they
   reconnect - regardless of how long they were away.
4. The system must tolerate partial failures: one unavailable chat
   server cannot block other conversations.

**DERIVED DESIGN:**
These four invariants derive the core architecture: a durable
message store (not the socket server) is the source of truth.
Fan-out delivers to online clients; a sync cursor enables offline
clients to catch up. Chat servers are stateless workers, not
authoritative stores.

**THE TRADE-OFFS:**
**Gain:** Reliability (messages survive disconnects), multi-device
consistency, audit trail.
**Cost:** Storage at scale (billions of messages per day), fan-out
amplification for large groups, latency added by write-before-send.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Message ordering within a conversation; offline
delivery guarantee; fan-out for group chats; presence state.
**Accidental:** Maintaining per-conversation sequence numbers
globally; routing all messages through a single ordering service;
synchronising presence at millisecond precision.

---

### 🧪 Thought Experiment

**SETUP:** You are building a chat app for 10 million users. You
decide to skip the message store and rely entirely on WebSocket
delivery - messages are forwarded directly from sender to recipient
socket with no persistence.

**WHAT HAPPENS WITHOUT IT:**
A user sends a message at 9:00 AM. The recipient's phone loses
signal at 9:01 AM and reconnects at 10:00 AM. The message is gone.
The sender has no way to know if it was received. Group chats
deliver to whoever happens to be connected at the instant of send.
Switching from phone to laptop shows a blank conversation.

**WHAT HAPPENS WITH IT:**
The message is persisted first. The socket delivers it instantly if
the recipient is online. If not, a push notification wakes their
app, which fetches the message from the store. All devices share
the same sequence of messages from the store. History is available
regardless of connection state.

**THE INSIGHT:**
Chat is not a real-time problem - it is a storage-with-real-time-
delivery problem. The storage layer defines the contract. The socket
layer is an optimisation.

---

### 🧠 Mental Model / Analogy

> A postal service that also offers live hand-delivery: every letter
> goes into the secure sorting office first, then the courier
> attempts immediate delivery. If the recipient is out, the letter
> stays in the office until they come to collect it or it is
> re-delivered automatically.

Element mapping:
- Sorting office = durable message store (Cassandra / PostgreSQL)
- Courier = WebSocket connection / push notification
- Recipient home = user online
- Re-delivery = reconnect sync from cursor
- Letter tracking number = message sequence ID

Where this analogy breaks down: a real postal service delivers
once; chat systems fan out to every device simultaneously.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A chat app lets you send text messages to other people in real
time, and lets them read those messages even if they were offline
when you sent them.

**Level 2 - How to use it (junior developer):**
Use WebSockets to maintain a persistent connection for online
users. Persist every message to a database. When a user reconnects,
send them all messages they missed using a "last seen" cursor.

**Level 3 - How it works (mid-level engineer):**
Messages are written to a durable store (Cassandra for scale, keyed
by conversation ID + sequence). A fan-out service delivers to all
online devices via WebSocket connection servers. Offline delivery
uses push notifications. Sequence numbers are per-conversation
(monotonic counter) not global. Presence is stored in an ephemeral
key-value store (Redis) with TTL.

**Level 4 - Why it was designed this way (senior/staff):**
Separating the delivery path from the storage path is the key
architectural decision. Connection servers are stateless (no
message storage) - they can be scaled horizontally and fail without
data loss. The durable store is the only authoritative state. This
design also enables multi-device sync: every device reads from the
same store and maintains its own read cursor. Global message
ordering would require a distributed sequence service (bottleneck);
per-conversation ordering is sufficient for user experience and
orders of magnitude cheaper.

**Expert Thinking Cues:**
- "Where is the message at-rest state?" - only in the store.
- "What happens if a connection server crashes?" - nothing is lost;
  client reconnects and syncs from cursor.
- "How do I fan out to 1M users in a group?" - fan-out on read
  (each device syncs independently) not fan-out on write.

---

### ⚙️ How It Works (Mechanism)

```
1. Client connects to chat gateway (WebSocket)
2. Gateway authenticates, registers presence in Redis
3. Client sends message -> gateway receives
4. Gateway writes message to message store (assigned seq ID)
5. Gateway acknowledges send to sender (with seq ID)
6. Fan-out service picks up message from store
7. For each recipient device:
   a. If online: push over WebSocket
   b. If offline: enqueue push notification
8. Recipient client ACKs receipt; unread counter decrements
9. On reconnect: client sends last_seq -> server streams delta
```

**Presence:**
Maintained as TTL keys in Redis. Every heartbeat (30s) refreshes
the key. Expired key = offline. Coarse presence reduces noise.

**Ordering:**
Per-conversation sequence counter (atomic increment in Redis or
SEQUENCE in Postgres). No global ordering service needed.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
+----------+  WS   +----------+  write  +----------+
|  Sender  |------>| Gateway  |-------->| Msg Store|
|  Client  |       |  Server  |         | (Cass.)  |
+----------+       +----+-----+         +----+-----+
                        |                    |
                   fan-out svc          seq assigned
                        |                    |
               +--------+--------+           |
               |                 |           |
        +------+---+      +------+---+  <----+
        | Recip.   |      | Recip.   |
        | Online   |      | Offline  |
        | (WS push)|      |(push notif)|
        +----------+      +----------+
                                 | reconnect
                          +------+---+
                          | Sync from|
                          | last_seq |
                          +----------+
                                    <- YOU ARE HERE (offline sync)
```

**FAILURE PATH:**
- Gateway crash: client reconnects to another gateway; no messages
  lost (store is authoritative).
- Message store unavailable: gateway rejects send, client retries.
- Fan-out delay: recipient sees push notification; opens app; syncs
  from store.

**WHAT CHANGES AT SCALE:**
- Millions of concurrent WebSocket connections: dedicated connection
  layer (no business logic), connection multiplexing.
- Group chats with 10K+ members: fan-out on read, not on write.
- Media messages: presigned upload URLs to object storage (S3);
  message store holds only URL + metadata.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
- Multiple gateway instances must route messages correctly: use a
  routing table (Redis) to map user -> gateway instance.
- Exactly-once delivery requires client-side dedup by message ID.
- Sequence counter per conversation must be atomic; use Redis INCR
  or database SEQUENCE, not application-level counters.

---

### 💻 Code Example

**BAD - Delivery without persistence:**

```python
# Messages exist only in memory; lost on disconnect
connected_clients = {}

def send_message(sender, recipient, text):
    if recipient in connected_clients:
        connected_clients[recipient].send(text)
    # If offline: message silently dropped
```

**GOOD - Persist first, deliver second:**

```python
class ChatService:
    def __init__(self, store, fanout, push):
        self.store = store      # durable message store
        self.fanout = fanout    # WebSocket delivery
        self.push = push        # push notifications

    def send_message(self, conv_id, sender, text):
        msg = self.store.save(conv_id, sender, text)
        # msg.seq assigned atomically per conversation
        self._deliver(conv_id, msg)
        return msg.seq          # ack with sequence ID

    def _deliver(self, conv_id, msg):
        for device in self.store.get_members(conv_id):
            if self.fanout.is_online(device.user_id):
                self.fanout.push(device, msg)
            else:
                self.push.notify(device, msg)

    def sync(self, user_id, conv_id, last_seq):
        # Called on reconnect
        return self.store.get_since(conv_id, last_seq)
```

**How to test / verify correctness:**
- Unit: test that `send_message` calls `store.save` before any
  delivery attempt.
- Integration: simulate offline recipient, disconnect, reconnect;
  verify all messages are returned by `sync`.
- Load: send 10K messages/sec; verify no sequence gaps.

---

### ⚖️ Comparison Table

| Concern             | Common Answer             | Trade-off              |
| ------------------- | ------------------------- | ---------------------- |
| Realtime delivery   | WebSockets                | Per-device connection  |
| Offline reliability | Durable message store     | Storage cost at scale  |
| Ordering            | Per-conversation sequence | No global order        |
| Presence            | Ephemeral Redis + TTL     | Coarse precision       |
| Group fan-out       | Fan-out on read           | Higher read latency    |
| Media files         | Object storage + URL      | CDN needed for speed   |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "WebSocket guarantees delivery" | Sockets drop. Storage and replay are what guarantee delivery, not the socket. |
| "Global ordering is required" | Per-conversation ordering is sufficient. Global ordering requires a distributed sequence service and is a write bottleneck. |
| "Presence must be real time" | Coarse presence (online/offline within 30 seconds) satisfies almost all use cases and is 100x cheaper than second-precision presence. |
| "Fan-out on write is always better" | Fan-out on write works for small groups. At 10K+ members, write amplification exceeds storage and network budgets. Fan-out on read is the correct model. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Duplicate messages on reconnect**

**Symptom:** User reconnects and sees the same message rendered
twice or more in the conversation.

**Root Cause:** Fan-out delivers the message once over the socket.
On reconnect, the sync-from-cursor also delivers it again because
the client's `last_seq` was not advanced before disconnect.

**Diagnostic:**
```bash
# Check if client last_seq matches server-side ack log
SELECT seq, delivered_at FROM message_acks
WHERE user_id = ? AND conv_id = ?
ORDER BY seq DESC LIMIT 20;
```

**Fix:**

BAD: Sync all messages from last N minutes on reconnect.
GOOD: Sync only messages with `seq > client_last_seq`, where
`last_seq` is advanced only after client ACK.

**Prevention:** Assign stable message IDs; require explicit client
ACK before advancing cursor; deduplicate by message ID on client.

---

**Failure Mode 2: Presence storm on high churn**

**Symptom:** Presence service CPU and memory spike when many users
connect and disconnect rapidly (mobile network switching).

**Root Cause:** Each connect/disconnect triggers a presence update
broadcast to all subscribers of that user. At scale with millions
of subscribers, this creates a fanout storm.

**Diagnostic:**
```bash
redis-cli monitor | grep "PUBLISH presence"
# Count presence publish events per second
```

**Fix:**

BAD: Broadcast every connect/disconnect immediately.
GOOD: Debounce presence updates (coalesce rapid changes within
5-10 seconds before publishing). Use TTL-based presence (key
expires = offline) to eliminate explicit disconnect broadcasts.

**Prevention:** Coarse presence granularity; separate presence
service from chat service; rate-limit presence subscriptions.

---

**Failure Mode 3: Group chat fan-out OOM**

**Symptom:** Chat servers run out of memory or timeout when sending
a message to a group with thousands of members.

**Root Cause:** Fan-out on write to 10K members creates 10K
simultaneous write operations, overwhelming the fan-out service.

**Diagnostic:**
```bash
# Check fan-out queue depth
redis-cli llen fanout_queue
# Check message delivery latency by group size
SELECT group_size, avg(delivery_latency_ms)
FROM message_metrics GROUP BY group_size;
```

**Fix:**

BAD: Fan-out on write to all members at send time.
GOOD: For groups above threshold (e.g., 500 members), switch to
fan-out on read: store message once, let each client pull on sync.

**Prevention:** Set group size limits per tier; use fan-out on read
for large groups; shard large groups across multiple fan-out workers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-067 - Notification System Design]] - real-time delivery
  infrastructure that chat's push path builds on

**Builds On This (learn these next):**
- [[SYD-023 - Push vs Pull Architecture]] - fundamental design
  decision for message delivery
- [[SYD-059 - Fan-Out on Write vs Read]] - fan-out strategy for
  group chat delivery at scale

**Alternatives / Comparisons:**
- [[SYD-067 - Notification System Design]] - simpler one-way
  delivery vs chat's bidirectional, multi-device model
- [[SYD-023 - Push vs Pull Architecture]] - architectural choice
  that applies to both chat and notification systems

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------------+
| WHAT IT IS  | Real-time + offline-capable messaging       |
|             | infrastructure                              |
+-----------------------------------------------------------+
| PROBLEM     | Messages lost on disconnect; no history     |
|             | across devices                              |
+-----------------------------------------------------------+
| KEY INSIGHT | Persist first; socket is just the fast path|
+-----------------------------------------------------------+
| USE WHEN    | Building 1:1 or group chat with multi-      |
|             | device and offline requirements             |
+-----------------------------------------------------------+
| AVOID WHEN  | Simple notification-only (use SYD-067)     |
+-----------------------------------------------------------+
| TRADE-OFF   | Storage cost + fan-out complexity vs        |
|             | reliability and multi-device consistency    |
+-----------------------------------------------------------+
| ONE-LINER   | Store durably; deliver fast; sync on        |
|             | reconnect                                   |
+-----------------------------------------------------------+
| NEXT EXPLORE| Fan-out on Write vs Read (SYD-059)         |
+-----------------------------------------------------------+
```

**If you remember only 3 things:**
1. The message store is the source of truth, not the socket.
2. Use per-conversation sequence numbers, not global ordering.
3. Fan-out on write fails at large group sizes - switch to read.

**Interview one-liner:** "Chat systems separate the delivery path
from the storage path: persist first, deliver via socket when
online, sync from cursor on reconnect."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Delivery guarantees define user trust. Chat users expect messages
to arrive exactly once, in order, and to be retrievable forever.
These three requirements - exactly-once delivery, ordering, and
durability - form the core of any messaging system design, and they
recur across payment systems, event sourcing, and distributed logs.

**Where else this pattern appears:**
- **Payment processing:** A payment must be idempotent (exactly-
  once), ordered (no debit before credit), and durable (permanent
  record) - the same three properties as chat messages.
- **Event sourcing:** An event log must be append-only (ordered),
  persistent (durable), and deduplicated (exactly-once) - a chat
  message store under a different name.
- **Email delivery:** SMTP with deduplication IDs implements
  at-least-once delivery; the receiver deduplicates - the same
  exactly-once pattern with the dedup step at the consumer.

---

### 💡 The Surprising Truth

WhatsApp served 2 billion users with fewer than 50 engineers as of
2014 - an extraordinary efficiency achieved by Erlang's actor model
where each user connection is a lightweight process. Traditional
Java or Python web frameworks would have required 10-100x more
engineers for the same scale, because Erlang was designed for
telecom switch software (fault-tolerant, massively concurrent,
continuously running) long before it was applied to chat. The right
language choice - motivated by a completely different domain's
constraints - made billion-user scale achievable with a small team.
WhatsApp is the strongest argument in software engineering that
domain constraints produce better language design than
general-purpose optimisation.

---

### 🧠 Think About This Before We Continue

**Q1.** Should message ordering be guaranteed across all devices or
only within one conversation timeline?

*Hint:* Think about what global ordering across all conversations
requires - a single distributed sequence counter for every message
system-wide. Explore what per-conversation ordering (sequence per
conversation) actually guarantees and whether that is sufficient
for user experience.

**Q2.** How much presence precision does your product really need?

*Hint:* Think about what "online" means at second granularity (is
the app in focus?) vs minute granularity (did they open the app in
the last 15 minutes?). Explore whether second-precision presence
requires persistent connections and what the server load difference
is between TTL-based and heartbeat-based presence.

**Q3 (Design Trade-off):** A user sends messages in a chat system
with end-to-end encryption (E2EE). The server cannot read message
content. The user gets a new device and wants their message history.
Design a scheme that enables multi-device message history with E2EE.

*Hint:* Think about where the decryption key lives - if only the
sender's original device has it, multi-device sync is impossible
without key sharing. Explore how Signal's key exchange protocol or
iMessage's per-device encryption approach solve the multi-device
E2EE history problem and what the security trade-offs are.
