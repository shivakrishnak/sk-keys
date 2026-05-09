#!/usr/bin/env python3
"""Write complete v3.0 entries for SYD-048, SYD-049, SYD-050."""
import os, pathlib

BASE = pathlib.Path(r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SYD-system-design")

def write(filename, content):
    fp = BASE / filename
    fp.write_text(content, encoding="utf-8")
    print(f"OK: {filename}")

# ────────────────────────────────────────────────────────────────────
# SYD-048 - Chat System Design
# ────────────────────────────────────────────────────────────────────
syd048 = """\
---
id: SYD-048
title: Chat System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: \u2605\u2605\u2605
depends_on: SYD-047
used_by:
related: SYD-047, SYD-036, SYD-035
tags:
  - architecture
  - advanced
  - distributed
  - async
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /syd/chat-system-design/
---

# SYD-048 - Chat System Design

\u26a1 TL;DR - A chat system delivers messages in real time to online
users, durably stores every message, and syncs offline users when
they reconnect.

| Field           | Detail                            |
| :-------------- | :-------------------------------- |
| **Depends on:** | SYD-047 - Notification System Design |
| **Used by:**    | -                                 |
| **Related:**    | SYD-047, SYD-036, SYD-035        |

---

### \U0001f525 The Problem This Solves

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

### \U0001f4d8 Textbook Definition

**Chat System Design** is a system design problem centred on
real-time and offline-capable messaging infrastructure for one-to-one
or group conversations, including message storage, reliable delivery,
multi-device synchronisation, and presence state management.

---

### \u23f1\ufe0f Understand It in 30 Seconds

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

### \U0001f529 First Principles Explanation

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

### \U0001f9ea Thought Experiment

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

### \U0001f9e0 Mental Model / Analogy

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

### \U0001f4f6 Gradual Depth - Four Levels

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

### \u2699\ufe0f How It Works (Mechanism)

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

### \U0001f504 The Complete Picture - End-to-End Flow

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

### \U0001f4bb Code Example

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

### \u2696\ufe0f Comparison Table

| Concern             | Common Answer             | Trade-off              |
| ------------------- | ------------------------- | ---------------------- |
| Realtime delivery   | WebSockets                | Per-device connection  |
| Offline reliability | Durable message store     | Storage cost at scale  |
| Ordering            | Per-conversation sequence | No global order        |
| Presence            | Ephemeral Redis + TTL     | Coarse precision       |
| Group fan-out       | Fan-out on read           | Higher read latency    |
| Media files         | Object storage + URL      | CDN needed for speed   |

---

### \u26a0\ufe0f Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "WebSocket guarantees delivery" | Sockets drop. Storage and replay are what guarantee delivery, not the socket. |
| "Global ordering is required" | Per-conversation ordering is sufficient. Global ordering requires a distributed sequence service and is a write bottleneck. |
| "Presence must be real time" | Coarse presence (online/offline within 30 seconds) satisfies almost all use cases and is 100x cheaper than second-precision presence. |
| "Fan-out on write is always better" | Fan-out on write works for small groups. At 10K+ members, write amplification exceeds storage and network budgets. Fan-out on read is the correct model. |

---

### \U0001f6a8 Failure Modes & Diagnosis

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

### \U0001f517 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-047 - Notification System Design]] - real-time delivery
  infrastructure that chat's push path builds on

**Builds On This (learn these next):**
- [[SYD-036 - Push vs Pull Architecture]] - fundamental design
  decision for message delivery
- [[SYD-035 - Fan-Out on Write vs Read]] - fan-out strategy for
  group chat delivery at scale

**Alternatives / Comparisons:**
- [[SYD-047 - Notification System Design]] - simpler one-way
  delivery vs chat's bidirectional, multi-device model
- [[SYD-036 - Push vs Pull Architecture]] - architectural choice
  that applies to both chat and notification systems

---

### \U0001f4cc Quick Reference Card

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
| AVOID WHEN  | Simple notification-only (use SYD-047)     |
+-----------------------------------------------------------+
| TRADE-OFF   | Storage cost + fan-out complexity vs        |
|             | reliability and multi-device consistency    |
+-----------------------------------------------------------+
| ONE-LINER   | Store durably; deliver fast; sync on        |
|             | reconnect                                   |
+-----------------------------------------------------------+
| NEXT EXPLORE| Fan-out on Write vs Read (SYD-035)         |
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

### \U0001f48e Transferable Wisdom

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

### \U0001f4a1 The Surprising Truth

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

### \U0001f9e0 Think About This Before We Continue

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
"""

# ────────────────────────────────────────────────────────────────────
# SYD-049 - Video Streaming Design
# ────────────────────────────────────────────────────────────────────
syd049 = """\
---
id: SYD-049
title: Video Streaming Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: \u2605\u2605\u2605
depends_on: SYD-023
used_by:
related: SYD-024, SYD-027
tags:
  - architecture
  - advanced
  - distributed
  - performance
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /syd/video-streaming-design/
---

# SYD-049 - Video Streaming Design

\u26a1 TL;DR - Video streaming encodes files into multiple quality
renditions, segments them into small chunks, distributes chunks
via CDN, and adapts quality dynamically to available bandwidth.

| Field           | Detail                            |
| :-------------- | :-------------------------------- |
| **Depends on:** | SYD-023 - Geo-Replication        |
| **Used by:**    | -                                 |
| **Related:**    | SYD-024, SYD-027                 |

---

### \U0001f525 The Problem This Solves

**WORLD WITHOUT IT:**
Before adaptive streaming, video was delivered as a single file.
The player had to buffer enough of the file before starting
playback. On slow connections, users waited minutes before the
first frame appeared. On congested networks, playback paused to
rebuffer mid-stream.

**THE BREAKING POINT:**
Global audiences on heterogeneous networks (3G, WiFi, fiber) with
varying device capabilities (4K TV, mobile phone) cannot all
receive the same fixed-bitrate file and have a good experience.
A file sized for 4K streaming causes constant rebuffering on 3G.

**THE INVENTION MOMENT:**
The core insight: pre-encode the same content at multiple bitrates
(renditions), split each rendition into small time-based segments
(2-10 seconds), and let the player dynamically switch between
renditions based on real-time bandwidth measurement. A manifest
file tells the player what renditions exist and where to fetch
each segment.

**EVOLUTION:**
Video streaming evolved from downloading entire files (RealPlayer,
1995) through progressive download to adaptive bitrate streaming
(ABR). YouTube (2005) demonstrated internet-scale video delivery
was possible with commodity hardware and CDN caching. Netflix
(2007-2012) pioneered ABR streaming with DASH and HLS formats,
then built Open Connect - their own CDN embedded in ISP networks.
The engineering challenge evolved from bandwidth efficiency to
per-viewer adaptation, then to latency reduction for live
streaming, and now to per-viewer ML-driven quality optimisation.
Video streaming accounts for approximately 70% of all internet
downstream bandwidth.

---

### \U0001f4d8 Textbook Definition

**Video Streaming Design** is a system design problem centred on
delivering large video files to global audiences at varying
network conditions, using transcoding pipelines, adaptive bitrate
(ABR) algorithms, content delivery networks (CDN), and segment-
based playback protocols such as HLS and MPEG-DASH.

---

### \u23f1\ufe0f Understand It in 30 Seconds

**One line:**
Encode video at multiple qualities, cut it into small segments,
cache segments near the viewer, and switch quality in real time.

**One analogy:**

> A highway with multiple speed lanes: slow drivers stay in the
> slow lane; fast drivers move to the fast lane. Traffic (ABR
> algorithm) continuously picks the best lane for current
> conditions without stopping.

**One insight:**
Segments are the unit of everything in streaming: CDN caches
segments, ABR switches between renditions at segment boundaries,
and players buffer segments ahead to absorb network jitter.

---

### \U0001f529 First Principles Explanation

**CORE INVARIANTS:**

1. Video playback requires continuous, uninterrupted frame
   delivery at a fixed frame rate (24/30/60 fps).
2. Network bandwidth is variable and unpredictable.
3. Video quality (resolution, bitrate) can be varied between
   segments without interrupting playback.
4. Segments cached near the viewer reduce both latency and
   origin server load.

**DERIVED DESIGN:**
Invariants 2 and 3 together derive ABR: vary quality dynamically.
Invariant 4 derives CDN distribution. Invariant 1 derives the
need to buffer ahead (2-5 segments) to absorb bandwidth drops.
The segment size (2-10 seconds) is a trade-off: shorter segments
enable faster quality adaptation; longer segments reduce manifest
overhead but slow adaptation.

**THE TRADE-OFFS:**
**Gain:** Smooth playback on variable networks; global scalability
via CDN; lower origin server load.
**Cost:** Storage multiplication (N renditions x total content);
transcoding pipeline complexity; encoding cost at ingest.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Multi-rendition encoding; CDN distribution;
bandwidth estimation in the player; segment-boundary switching.
**Accidental:** Segment format fragmentation (HLS vs DASH vs
Smooth Streaming); per-codec transcoding duplication; DRM key
management complexity.

---

### \U0001f9ea Thought Experiment

**SETUP:** You are building a video streaming service for 10
million users worldwide. You decide to skip multi-rendition
encoding and serve a single 1080p video file to all users.

**WHAT HAPPENS WITHOUT IT:**
A user on a 500 kbps 3G connection starts loading your 8 Mbps
1080p file. They must buffer 16x real-time. The player either
stalls immediately or shows a loading spinner for 30+ seconds.
70% of users abandon before the first frame. Users on fiber
receive excellent quality, but only 10% of your global audience
has fiber. Serving one rendition optimises for 10% of users.

**WHAT HAPPENS WITH IT:**
The same 3G user receives a 240p rendition at 300 kbps - just
within their bandwidth. Playback starts in 3 seconds. If signal
improves (they walk indoors to WiFi), the player switches to 720p
seamlessly at the next segment boundary. The fiber user gets 4K.
Each user receives the best quality their network can sustain.

**THE INSIGHT:**
The goal is not "best quality" but "best quality for this
connection right now". ABR converts a fixed constraint (file
quality) into a dynamic variable that the system continuously
optimises.

---

### \U0001f9e0 Mental Model / Analogy

> An airline booking system that dynamically upgrades or downgrades
> your seat based on real-time availability: your seat class
> changes at each layover (segment boundary) without your journey
> being interrupted.

Element mapping:
- Seat class = video rendition (240p / 720p / 1080p / 4K)
- Layover = segment boundary (every 4 seconds)
- Flight availability = available network bandwidth
- Upgrade/downgrade decision = ABR algorithm
- Airport lounges worldwide = CDN edge nodes

Where this analogy breaks down: airlines change your seat once;
ABR changes quality at every segment boundary, potentially
hundreds of times per viewing session.

---

### \U0001f4f6 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Video streaming adjusts video quality automatically based on your
internet speed, so you get smooth playback even on a slow
connection - just at lower resolution.

**Level 2 - How to use it (junior developer):**
Use FFmpeg to transcode a video to multiple bitrates. Use HLS
or DASH to generate a manifest file and segments. Upload segments
to S3. Serve via CloudFront CDN. The client player handles ABR
automatically using a library like hls.js or dash.js.

**Level 3 - How it works (mid-level engineer):**
The transcoding pipeline converts the original into renditions
(e.g., 240p/500kbps, 480p/1Mbps, 720p/3Mbps, 1080p/8Mbps).
Each rendition is split into 4-second segments. A master manifest
(`.m3u8` for HLS) lists all renditions with their bandwidth.
A per-rendition manifest lists all segments. The player measures
throughput of the last segment download, computes a buffer health
metric, and selects the next rendition using an ABR algorithm.
Segments are cached at CDN edge nodes closest to the viewer.

**Level 4 - Why it was designed this way (senior/staff):**
Segment-based delivery decouples CDN caching from video duration:
a CDN can cache individual 4-second segments, not entire multi-GB
files. This makes CDN cache hit rates extremely high (popular
content has thousands of viewers sharing the same cached segments).
ABR runs entirely client-side in most implementations, eliminating
the need for the server to know each viewer's bandwidth. Netflix's
BOLA (Buffer Occupancy Based Lyapunov Algorithm) optimises for
buffer health rather than raw throughput, preventing rebuffering
events even on throughput-variable connections.

**Expert Thinking Cues:**
- "What is the cache hit rate for popular content?" - extremely
  high if segments are uniform across renditions.
- "Who runs the ABR algorithm?" - the player, not the server.
- "What is the failure mode of aggressive ABR?" - quality
  oscillation (rapid switching up and down).

---

### \u2699\ufe0f How It Works (Mechanism)

```
Ingest pipeline:
  Original file
    -> Transcoder (FFmpeg/AWS MediaConvert)
       -> 240p, 480p, 720p, 1080p, 4K renditions
          -> Segmenter (4-sec chunks + manifests)
             -> S3 (origin)
                -> CDN (CloudFront/Akamai/Open Connect)

Playback:
  Player fetches master manifest
  -> Selects initial rendition
  -> Downloads first segment
  -> Measures download throughput
  -> ABR algorithm selects next rendition
  -> Downloads next segment from CDN edge
  -> Repeat every 4 seconds
```

**ABR Algorithm Decision (simplified BOLA):**
Buffer occupancy < 10s: downgrade rendition.
Buffer occupancy 10-30s: maintain rendition.
Buffer occupancy > 30s: upgrade rendition if bandwidth supports.

---

### \U0001f504 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
+----------+   upload   +----------+   +----------+
| Creator  |----------->|Transcode |-->|  S3      |
+----------+            | Pipeline |   | (origin) |
                        +----------+   +----+-----+
                                            |
                                       CDN push/pull
                                            |
                                   +--------+--------+
                                   |    CDN Edge     |
                                   | (near viewer)   |
                                   +--------+--------+
                                            |
                                       segment fetch
                                            |
+----------+  manifest  +----------+        |
|  Player  |<-----------|CDN Edge  |<-------+
|  (ABR)   |  segments  +----------+
+----------+                    <- YOU ARE HERE (playback)
```

**FAILURE PATH:**
- CDN edge miss: request falls through to origin (slower but
  works). High miss rate = origin overload.
- Transcoding failure: video unavailable; retry pipeline.
- ABR over-optimistic: player requests higher rendition than
  network supports; buffer drains; rebuffer event.

**WHAT CHANGES AT SCALE:**
- Popular content: CDN cache hit rates >99%; origin rarely hit.
- Long-tail content: low cache hit rate; origin serves most
  requests; CDN less effective.
- Concurrent launches: thundering herd at CDN edge for new
  popular content; mitigate with pre-warming.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
- Each viewer independently fetches segments; no server-side
  state per viewer for on-demand streaming.
- Live streaming adds real-time ingest latency: segments must be
  available at CDN within seconds of being recorded.
- DRM adds key server round-trip per viewer per content item.

---

### \U0001f4bb Code Example

**BAD - Single rendition, no CDN:**

```python
# Server directly streams the single 1080p file
# No adaptation, no CDN, no segments
@app.route('/video/<video_id>')
def stream_video(video_id):
    path = f"/storage/{video_id}/1080p.mp4"
    return send_file(path, mimetype='video/mp4')
    # Problems: no adaptation, origin overload at scale,
    # all bandwidth from your servers
```

**GOOD - Manifest + CDN + ABR:**

```python
@app.route('/video/<video_id>/manifest.m3u8')
def video_manifest(video_id):
    # Return pre-generated HLS master manifest from S3
    # Player handles ABR client-side
    cdn_base = f"https://cdn.example.com/{video_id}"
    manifest = generate_master_manifest(
        video_id,
        renditions=[
            (240, 400_000),
            (480, 1_000_000),
            (720, 3_000_000),
            (1080, 8_000_000),
        ],
        cdn_base=cdn_base
    )
    return manifest, 200, {'Content-Type': 'application/vnd.m3u8'}

# Player fetches: /video/abc/manifest.m3u8
# Player picks rendition based on bandwidth
# Player fetches segments from CDN directly
# No further origin involvement for segments (CDN serves)
```

**How to test / verify correctness:**
- Unit: test manifest generation for correct rendition URLs.
- Integration: throttle network to 500 kbps; verify player
  switches to 240p rendition within 2 segment cycles.
- Load: simulate 10K concurrent viewers; verify CDN handles
  without origin overload (check origin request rate).

---

### \u2696\ufe0f Comparison Table

| Concern           | HLS (Apple)         | MPEG-DASH           |
| ----------------- | ------------------- | ------------------- |
| Segment format    | MPEG-TS / fMP4      | fMP4                |
| Platform support  | Native iOS/Safari   | Chrome/Firefox/Edge |
| Latency (live)    | 10-30s (std)        | 2-8s (low-latency)  |
| ABR flexibility   | Limited by spec     | Fully customisable  |
| CDN compatibility | Universal           | Universal           |

| Approach       | Use when                         |
| -------------- | -------------------------------- |
| HLS            | Apple device support required    |
| DASH           | Cross-platform, adaptive quality |
| Progressive DL | Short clips, no adaptation needed|
| WebRTC         | Live, sub-1s latency required    |

---

### \u26a0\ufe0f Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "ABR maximises resolution" | ABR maximises playback continuity. It will downgrade quality to prevent rebuffering, even if bandwidth could technically support higher quality. |
| "CDN solves all scaling problems" | CDN excels for popular content (high cache hit rates). Long-tail content has low hit rates and still stresses the origin. |
| "Longer segments are better" | Longer segments (10+ seconds) slow ABR adaptation. A network change takes longer to detect and adapt to. 4-6 seconds is the common sweet spot. |
| "Live streaming is just on-demand with no pre-encoding" | Live streaming has fundamentally different pipeline constraints: real-time encoding, segment availability within seconds, and no pre-warming is possible. |

---

### \U0001f6a8 Failure Modes & Diagnosis

**Failure Mode 1: Thundering herd at CDN on launch**

**Symptom:** Major title launches at midnight. First 2 minutes of
content get massive cache misses; origin servers become
overwhelmed; initial viewers experience long start times.

**Root Cause:** CDN cache is cold for the new content. Millions of
simultaneous requests for the first segments miss the cache and
hit origin simultaneously.

**Diagnostic:**
```bash
# Check CDN origin request rate at launch vs steady state
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=$DIST_ID \
  --start-time $LAUNCH_TIME --end-time $PLUS_5MIN \
  --period 60 --statistics Sum
```

**Fix:**

BAD: Launch content cold; let CDN warm organically.
GOOD: Pre-warm CDN by proactively fetching popular segments
to all edge nodes 30 minutes before launch using CDN warming
API or a synthetic request generator.

**Prevention:** Pre-warm CDN before launch; use soft-launch with
small cohort to warm cache before full release.

---

**Failure Mode 2: ABR quality oscillation**

**Symptom:** Video quality constantly switches between 480p and
1080p every few seconds, causing visible quality flickering for
the viewer.

**Root Cause:** ABR algorithm is too aggressive in upgrading
quality (switches to 1080p on brief bandwidth spike) then must
immediately downgrade when the spike subsides.

**Diagnostic:**
```bash
# In browser console (hls.js)
hls.on(Hls.Events.LEVEL_SWITCHING, (event, data) => {
  console.log('Switch to level:', data.level,
    'at time:', video.currentTime);
});
# Frequent LEVEL_SWITCHING events = oscillation
```

**Fix:**

BAD: Use throughput-only ABR (switch up on any bandwidth spike).
GOOD: Use buffer-occupancy ABR (BOLA): upgrade only when buffer
is comfortably full; weight downgrade more aggressively than
upgrade to prevent oscillation.

**Prevention:** Set upgrade hysteresis (require N consecutive
segments at high bandwidth before upgrading); tune ABR for
content type (sports: smooth > quality; film: quality > smooth).

---

**Failure Mode 3: Live streaming lag spike**

**Symptom:** Live streaming latency spikes from 5 seconds to 60+
seconds for all viewers simultaneously.

**Root Cause:** Transcoder pipeline falls behind real-time: slow
encoding causes segments to become available late; CDN serves
stale manifest pointing to non-existent future segments; players
stall waiting.

**Diagnostic:**
```bash
# Check transcoder queue depth
aws mediaconvert list-jobs --status PROGRESSING \
  --query 'Jobs[*].{Id:Id,Progress:JobPercentComplete}'
# If progress < 95% for a LIVE job = falling behind
```

**Fix:**

BAD: Single transcoder instance; no monitoring on segment
availability lag.
GOOD: Monitor segment availability delay (time from capture to
CDN availability); auto-scale transcoder fleet when lag > 2s;
use GPU-accelerated encoding for real-time throughput headroom.

**Prevention:** Provision transcoder capacity at 2x expected
peak; set alerting on segment lag > 3 seconds; test with
simulated bitrate spikes in staging.

---

### \U0001f517 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-023 - Geo-Replication]] - CDN caching is geo-replication
  applied to video segments at edge nodes worldwide

**Builds On This (learn these next):**
- [[SYD-024 - Multi-Region Architecture]] - deployment pattern
  for global video CDN infrastructure
- [[SYD-027 - Capacity Planning]] - video is the highest-bandwidth
  workload to capacity plan in any consumer system

**Alternatives / Comparisons:**
- [[SYD-024 - Multi-Region Architecture]] - broader deployment
  pattern that video CDN is an implementation of
- [[SYD-048 - Chat System Design]] - contrasting real-time design
  (low latency + small payloads vs high throughput + large files)

---

### \U0001f4cc Quick Reference Card

```
+-----------------------------------------------------------+
| WHAT IT IS  | Multi-rendition segment-based adaptive      |
|             | video delivery via CDN                      |
+-----------------------------------------------------------+
| PROBLEM     | Variable bandwidth + huge files = constant  |
|             | rebuffering for some users                  |
+-----------------------------------------------------------+
| KEY INSIGHT | Segments are the unit: encode, cache, and   |
|             | switch quality at segment boundaries        |
+-----------------------------------------------------------+
| USE WHEN    | Delivering video to global audiences at     |
|             | varying network conditions                  |
+-----------------------------------------------------------+
| AVOID WHEN  | Short clips where progressive download is   |
|             | simpler (< 30 seconds of content)           |
+-----------------------------------------------------------+
| TRADE-OFF   | Storage x N renditions vs smooth playback   |
|             | on all network conditions                   |
+-----------------------------------------------------------+
| ONE-LINER   | Transcode to multiple quality levels,       |
|             | segment, cache at CDN, let player adapt     |
+-----------------------------------------------------------+
| NEXT EXPLORE| Multi-Region Architecture (SYD-024)        |
+-----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Encode at multiple bitrates; split into 4-second segments.
2. CDN caches segments close to viewers - not the full file.
3. ABR runs in the player; the server does not control quality.

**Interview one-liner:** "Video streaming encodes multiple bitrate
renditions, segments them into small chunks cached at CDN edge
nodes, and uses adaptive bitrate algorithms in the player to
switch quality dynamically based on available bandwidth."

---

### \U0001f48e Transferable Wisdom

**Reusable Engineering Principle:**
Segment, cache, and adapt. When content is large and networks are
variable, the solution is to segment content into uniform chunks,
cache chunks close to the consumer, and adapt delivery rate to
available capacity. This three-part strategy is not unique to
video.

**Where else this pattern appears:**
- **Software update delivery:** macOS and Windows updates are
  chunked into segments and delivered via CDN with delta-only
  downloads after the initial version - the same segment-and-cache
  pattern.
- **Podcast streaming:** RSS audio files are served via CDN with
  HTTP range request support, enabling the player to fetch and
  buffer ahead without downloading the full file.
- **Kafka streaming:** Producers write to partitioned log
  segments; consumers read at their own pace from the nearest
  replica - adaptive throughput via partition assignment mirrors
  ABR's adapt-to-consumer-pace model.

---

### \U0001f4a1 The Surprising Truth

Video streaming's biggest engineering challenge is not bandwidth
but time synchronisation for live events. Live streaming must
deliver video frames to millions of viewers within seconds of each
other (for sports, financial events, elections). The difference
between a 2-second and a 10-second delay determines whether
viewers can discuss the same event in real time on social media.
Achieving sub-5-second live streaming latency at scale requires
bypassing traditional CDN caching (which introduces delays) and
using low-latency protocols (LL-HLS, WebRTC). Most streaming
platforms quietly accept 20-30 second delays for "live" events
because true low latency at scale is significantly more expensive
- and most viewers do not notice the difference unless they are
also watching the same event on broadcast TV.

---

### \U0001f9e0 Think About This Before We Continue

**Q1.** What hurts more in your product: lower resolution or more
buffering?

*Hint:* Think about what product the user is actually consuming -
sports streaming (low latency > resolution), documentary (resolution
> latency), user-generated content (buffering tolerance varies).
Explore whether the answer changes by content type and whether the
product should offer user-configurable quality preferences.

**Q2.** How would live video design differ from on-demand video
design?

*Hint:* Think about the fundamental difference: on-demand content
has the complete file available before any viewer starts watching
(pre-encode, pre-upload to CDN), while live content has only the
last few seconds available at any moment. Explore what changes in
the encoding pipeline, CDN strategy, and error recovery when
pre-caching is impossible.

**Q3 (Scale):** A popular show launches and 2 million users start
streaming the same episode simultaneously at exactly 12:01 AM.
Your CDN has a 5-minute TTL on video segments. Design a
pre-warming strategy that ensures smooth playback at launch.

*Hint:* Think about what happens when 2 million cache misses hit
the origin simultaneously for the same segments. Explore how
pre-warming (distributing popular content to edge nodes before
launch) and staggered release (soft launch with a small cohort at
11:59 PM) prevent the thundering herd at the CDN edge.
"""

# ────────────────────────────────────────────────────────────────────
# SYD-050 - Ride-Sharing System Design
# ────────────────────────────────────────────────────────────────────
syd050 = """\
---
id: SYD-050
title: Ride-Sharing System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: \u2605\u2605\u2605
depends_on: SYD-023
used_by:
related: SYD-048, SYD-047, SYD-027
tags:
  - architecture
  - advanced
  - distributed
  - realtime
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /syd/ride-sharing-system-design/
---

# SYD-050 - Ride-Sharing System Design

\u26a1 TL;DR - Ride-sharing systems track driver locations in real
time via geospatial indexes, match riders to nearby drivers using
batch optimisation, and manage a two-sided marketplace with
dynamic pricing.

| Field           | Detail                            |
| :-------------- | :-------------------------------- |
| **Depends on:** | SYD-023 - Geo-Replication        |
| **Used by:**    | -                                 |
| **Related:**    | SYD-048, SYD-047, SYD-027        |

---

### \U0001f525 The Problem This Solves

**WORLD WITHOUT IT:**
Traditional taxi dispatch was phone-based: customers called a
central number, a dispatcher radioed the nearest driver they knew
about, and accuracy depended entirely on drivers calling in their
location. There was no real-time visibility into driver positions,
no ETA estimation, and supply-demand imbalance was invisible until
wait times exploded.

**THE BREAKING POINT:**
GPS-enabled smartphones (2007) made real-time consumer location
sharing practical. Customers now expected to see nearby drivers
on a map, get accurate ETAs, and request a ride without phone
calls. The new product demand - millions of driver location updates
per second, sub-second matching, and dynamic surge pricing - was
impossible with phone dispatch.

**THE INVENTION MOMENT:**
The core insight: treat driver location as a continuously updated
geospatial index. Index drivers by geographic cell (not by driver
ID or proximity list). Match riders to the index, not to
individual drivers. Run matching as a batch optimisation (not
greedy nearest-driver) to maximise global efficiency.

**EVOLUTION:**
Ride-sharing emerged from GPS-enabled smartphones making real-time
location sharing practical at consumer scale. Uber (2009) and
Lyft (2012) demonstrated that a marketplace matching model -
riders bidding for supply dynamically - outperformed fixed-price
taxi dispatch. The engineering challenge evolved from basic
location tracking to surge pricing algorithms, ETA prediction
with traffic, and fraud detection at marketplace scale. The
discipline absorbed techniques from computational geometry
(geospatial indexing), operations research (optimal matching
under uncertainty), and real-time systems (sub-second dispatch
latency). Modern ride-sharing platforms are simultaneously
logistics systems, financial systems, and real-time two-sided
marketplaces.

---

### \U0001f4d8 Textbook Definition

**Ride-Sharing System Design** is a system design problem
centred on ingesting and indexing continuous driver location
updates, matching riders to nearby available drivers using
optimisation algorithms, computing dynamic surge pricing from
supply-demand imbalance, and managing a two-sided marketplace
at internet scale.

---

### \u23f1\ufe0f Understand It in 30 Seconds

**One line:**
Keep driver locations fresh in a geospatial index and match
riders to drivers using batch optimisation, not greedy nearest.

**One analogy:**

> An air traffic control system: aircraft positions stream in
> continuously, the radar screen shows real-time positions, and
> controllers assign landing slots by optimising for the entire
> airspace, not just the nearest available runway.

**One insight:**
Geospatial proximity queries need geospatial data structures.
Storing latitude/longitude in a relational database and running
radius queries at scale is a bottleneck; geospatial indexes
(H3, S2, QuadTree) answer proximity in O(log n).

---

### \U0001f529 First Principles Explanation

**CORE INVARIANTS:**

1. Driver locations change continuously (every 3-5 seconds);
   any stale location is a potential mismatch.
2. Geographic proximity is the primary matching constraint -
   a driver 30 minutes away is irrelevant regardless of other
   attributes.
3. Supply-demand imbalance is local and real-time; pricing must
   reflect current conditions in a specific geographic cell.
4. Matching quality is global (optimise all active riders and
   drivers together), not local (greedily assign nearest driver
   to each rider independently).

**DERIVED DESIGN:**
Invariant 1 derives the streaming location ingest pipeline.
Invariant 2 derives geospatial indexing (not relational lat/lon).
Invariant 3 derives per-cell surge pricing computation.
Invariant 4 derives batch matching (not greedy).

**THE TRADE-OFFS:**
**Gain:** Low wait times; accurate ETAs; fair driver earnings;
dynamic supply incentivisation via surge.
**Cost:** Real-time geospatial index complexity; matching
algorithm latency budget (500ms for batch); surge pricing
user experience risk.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Location freshness; geospatial proximity queries;
supply-demand pricing; batch matching optimisation.
**Accidental:** Per-city database sharding (abstracted by
geographic cell sharding); routing graph recomputation
(use external map API); driver state machine complexity.

---

### \U0001f9ea Thought Experiment

**SETUP:** You are building a ride-sharing app. You store driver
locations in a standard relational database with latitude and
longitude columns. You run a `WHERE distance(lat, lon) < 500m`
query on every ride request.

**WHAT HAPPENS WITHOUT IT:**
With 100,000 active drivers citywide, every ride request triggers
a full table scan (no spatial index). At 1,000 concurrent ride
requests per second, the database performs 100 million distance
comparisons per second. At 10,000 requests per second (peak
surge), the database falls over. Driver matches take 10+ seconds.
Riders see "finding driver..." forever.

**WHAT HAPPENS WITH IT:**
A geospatial index (H3 hexagonal grid) divides the city into
geographic cells. A driver update writes to the cell the driver
is in. A ride request queries only the cells within 500m radius.
With average cell populations of 10-50 drivers, matching
requires comparing 50-200 drivers, not 100,000. Query time is
sub-millisecond at any scale.

**THE INSIGHT:**
Geospatial problems require geospatial data structures. The
correct abstraction is the geographic cell, not the individual
driver record.

---

### \U0001f9e0 Mental Model / Analogy

> A cellular network tower map: the city is divided into coverage
> cells. When your phone moves between cells, the network updates
> your cell assignment. When you make a call, the network routes
> it through your current cell's tower, not by scanning every
> tower in the country.

Element mapping:
- Cell tower coverage area = geospatial cell (H3 hex / S2 cell)
- Your phone = driver (continuously reporting position)
- Network routing = matching engine (queries active cell)
- Call setup = ride matching (O(drivers in cell), not all drivers)
- Coverage handoff = driver moving between geographic cells

Where this analogy breaks down: cellular handoffs are geography-
deterministic; ride matching has multiple optimisation objectives
(ETA, driver fairness, marketplace efficiency) not just geography.

---

### \U0001f4f6 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Ride-sharing apps see where all the nearby drivers are (because
drivers send their location constantly), and when you request a
ride, the app picks the most suitable driver quickly.

**Level 2 - How to use it (junior developer):**
Drivers send location updates every 4 seconds to a location
service. Store positions in Redis with geospatial commands
(`GEOADD`, `GEORADIUS`). On ride request, query nearby available
drivers, pick the closest, and send notifications to both rider
and driver.

**Level 3 - How it works (mid-level engineer):**
Location updates stream into a location ingest service that writes
to a geospatial index (Redis with H3 cell keys or a PostGIS
instance). The matching engine runs every 500ms as a batch: for
all unmatched riders, query available drivers in nearby cells,
run a linear assignment optimisation (minimising sum of ETAs),
and assign matches. Surge pricing computes per-cell supply-demand
ratio every 60 seconds and updates the multiplier in the pricing
service.

**Level 4 - Why it was designed this way (senior/staff):**
Greedy nearest-driver matching is locally optimal but globally
suboptimal: it can assign a driver 2 minutes away while a driver
4 minutes away is positioned to serve 3 future riders. Batch
matching (Hungarian algorithm or approximations) solves the global
assignment problem across all active riders and drivers in a city
in under 500ms. Uber's move from greedy to batch matching
increased driver earnings by 15% without adding new drivers.
Geographic cell sharding (rather than random database sharding)
ensures that all data for a geographic region is co-located,
making proximity queries local within a shard.

**Expert Thinking Cues:**
- "What is the staleness budget for driver location?" - 30-60
  seconds before a match is likely incorrect.
- "Why not use PostgreSQL with PostGIS?" - viable at small scale;
  at Uber scale (50K updates/sec/city), a specialised in-memory
  geospatial store is necessary.
- "How do you shard the geospatial index?" - by geographic cell
  prefix (H3 resolution level), not by driver ID.

---

### \u2699\ufe0f How It Works (Mechanism)

```
Driver update pipeline:
  Driver app (GPS) -> Location service (every 4s)
    -> Geospatial index update (H3 cell key in Redis)
    -> Driver state store (available/busy/offline)
    -> ETA service feed (for routing graph)

Ride matching pipeline (500ms batch):
  Ride requests -> Matching service
    -> Query geospatial index (nearby cells, r=2km)
    -> Filter: available drivers only
    -> Run batch assignment (linear optimisation)
    -> Assign matches, notify via push + in-app message
    -> Update driver state to 'en route'

Surge pricing pipeline (60s compute):
  Per-cell: supply_drivers / demand_riders
    -> multiplier = f(ratio, historical baseline)
    -> Write to pricing cache (Redis)
    -> Expose to rider app at request time
```

---

### \U0001f504 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
+----------+ (GPS, 4s) +----------+  write  +----------+
|  Driver  |---------->| Location |-------->|Geospatial|
|   App    |           | Ingest   |         |  Index   |
+----------+           +----------+         | (Redis)  |
                                            +----+-----+
                                                 |
+----------+ request   +----------+  query       |
|  Rider   |---------->| Matching |<-------------+
|   App    |           | Engine   |
+----------+           | (500ms   |
                        | batch)   |  <- YOU ARE HERE
                        +----+-----+  (batch optimisation)
                             |
                        assign match
                             |
                   +---------+---------+
                   |                   |
             +-----+----+        +-----+----+
             | Notify   |        | Notify   |
             | Driver   |        | Rider    |
             | (push)   |        | (push)   |
             +----------+        +----------+
```

**FAILURE PATH:**
- Location ingest overload: reduce update frequency (5s -> 10s);
  shed load for offline drivers.
- Matching engine timeout: fall back to greedy nearest-driver;
  slightly worse outcomes but instant.
- Geospatial index unavailable: read from replica; accept slight
  location staleness.

**WHAT CHANGES AT SCALE:**
- 50K location updates/sec/city: shard geospatial index by city
  and H3 cell prefix; use in-memory store.
- 10K concurrent ride requests: batch matching parallelised by
  geographic region; each batch solver handles one sub-region.
- Global deployment: per-city infrastructure; no cross-city
  geospatial queries needed.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
- Driver state transitions (available -> en_route -> in_trip ->
  available) must be atomic to prevent double-assignment.
- Matching reads and writes the same geospatial index; use
  optimistic locking or a single-writer matching service per
  region.
- Surge pricing writes every 60s; readers accept eventual
  consistency (rider sees slightly stale surge multiplier).

---

### \U0001f4bb Code Example

**BAD - Geospatial query on relational table:**

```python
# Full table scan; fails at > 10K drivers
def find_nearby_drivers(lat, lon, radius_km):
    return db.execute('''
        SELECT driver_id, lat, lon,
          6371 * acos(cos(radians(:lat))
            * cos(radians(lat))
            * cos(radians(lon) - radians(:lon))
            + sin(radians(:lat))
            * sin(radians(lat))) AS dist
        FROM drivers
        WHERE status = 'available'
        HAVING dist < :r
        ORDER BY dist
    ''', lat=lat, lon=lon, r=radius_km).all()
    # O(N) full table scan for every request
```

**GOOD - Geospatial index with H3 cells:**

```python
import h3

SEARCH_RADIUS_KM = 2.0
H3_RESOLUTION = 9  # ~0.1 km2 per hexagon

def update_driver_location(driver_id, lat, lon):
    cell = h3.geo_to_h3(lat, lon, H3_RESOLUTION)
    redis.geoadd(f"drivers:{cell}", lon, lat, driver_id)
    redis.setex(f"driver_cell:{driver_id}", 30, cell)

def find_nearby_drivers(lat, lon):
    origin_cell = h3.geo_to_h3(lat, lon, H3_RESOLUTION)
    nearby_cells = h3.k_ring(origin_cell, k=2)
    drivers = []
    for cell in nearby_cells:
        cell_drivers = redis.georadius(
            f"drivers:{cell}", lon, lat,
            SEARCH_RADIUS_KM, unit='km',
            withcoord=True
        )
        drivers.extend(cell_drivers)
    return drivers
    # O(k * drivers_per_cell) not O(all_drivers)
```

**How to test / verify correctness:**
- Unit: test that `update_driver_location` writes to the correct
  H3 cell key.
- Integration: insert 100K driver positions; verify
  `find_nearby_drivers` returns only drivers within 2km and runs
  in < 10ms.
- Load: simulate 50K location updates/sec; verify Redis write
  throughput and read latency remain within budget.

---

### \u2696\ufe0f Comparison Table

| Approach            | Use when                          | Limitation          |
| ------------------- | --------------------------------- | ------------------- |
| Redis GEORADIUS     | < 1M active drivers               | Single instance     |
| PostGIS             | Complex geo queries + persistence | Lower write rate    |
| H3 + Redis sharded  | > 1M drivers, city-scale          | Boundary complexity |
| S2 Geometry library | 3D geo (aviation, global scale)   | Higher complexity   |
| QuadTree in-memory  | Custom matching logic needed      | Memory-bound        |

---

### \u26a0\ufe0f Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Nearest driver is always the best match" | Greedy nearest-driver is locally optimal but globally suboptimal. Batch matching (considering all riders and drivers together) consistently outperforms greedy by 10-20% on average ETA. |
| "Storing lat/lon in PostgreSQL with an index is enough" | A B-tree index on lat/lon cannot efficiently answer radius queries. You need a spatial index (R-tree / GiST) or a dedicated geospatial tool. At > 10K updates/sec, relational databases require specialised extensions. |
| "Surge pricing is purely profit-driven" | Surge pricing is a two-sided marketplace signal: it incentivises more drivers to go online, increasing supply during high demand. Without surge, demand permanently exceeds supply during peaks and no drivers are incentivised to join. |
| "Driver location updates can be infrequent" | Location freshness directly determines match quality. A location 60 seconds old can place a driver 500m from their actual position. Staleness thresholds should be tuned to the mismatch cost. |

---

### \U0001f6a8 Failure Modes & Diagnosis

**Failure Mode 1: Location staleness causing mismatched ETAs**

**Symptom:** Rider's app shows driver is 2 minutes away; actual
arrival is 8 minutes. Driver location on map appears frozen.

**Root Cause:** Driver's mobile app has lost data connectivity
but has not been marked offline. The geospatial index still
shows the last known position from 90 seconds ago.

**Diagnostic:**
```bash
# Check Redis key TTL for driver location
redis-cli TTL "driver_cell:driver_123"
# < 0 = key expired (driver offline)
# > 20 = location still fresh
# Check last update timestamp from driver app logs
grep "driver_id=driver_123" /var/log/location-ingest.log \
  | tail -5
```

**Fix:**

BAD: Assume driver is online if the key exists (no TTL).
GOOD: Set 30-second TTL on every location key. If TTL expires,
driver is automatically considered unavailable. Only refresh
TTL on incoming location update.

**Prevention:** Client-side dead reckoning (extrapolate position
from last known velocity); alert on drivers with > 30s since
last location update; exclude stale-location drivers from
matching pool.

---

**Failure Mode 2: Geospatial index shard hotspot**

**Symptom:** One Redis shard is at 100% CPU during peak hours.
Location update latency spikes for one geographic area. Driver
matches in that area have 5+ second delays.

**Root Cause:** A city's downtown area (high driver density) maps
to a small number of H3 cells, all assigned to the same shard.
All updates and queries for the busiest area hit one instance.

**Diagnostic:**
```bash
# Check per-shard command rate
redis-cli -h shard-03 info stats | grep instantaneous_ops
# Compare across shards; one at 10x others = hotspot
# Identify which H3 cells are on hot shard
redis-cli -h shard-03 scan 0 match "drivers:*" count 1000
```

**Fix:**

BAD: Shard by H3 cell ID modulo N (geographic hotspots stay
on the same shard).
GOOD: Shard by consistent hash of H3 cell ID with virtual
nodes; periodically rebalance hot cells to under-loaded shards.

**Prevention:** Monitor per-shard command rate; pre-analyse
geographic density for each city and pre-balance accordingly;
use Redis Cluster with automatic slot rebalancing.

---

**Failure Mode 3: Matching engine deadlock under surge**

**Symptom:** During surge events, ride assignments stop for
60-90 seconds. Riders see "Finding your driver..." indefinitely.
Driver app shows "Waiting for requests" despite nearby riders.

**Root Cause:** The batch matching engine holds a write lock on
the driver state store for the full duration of the optimisation
solve (2-3 seconds). Location update writes block on the same
lock, causing a deadlock across services.

**Diagnostic:**
```bash
# Check matching engine lock contention
grep "lock_wait_ms" /var/log/matching-engine.log \
  | awk '{print $NF}' | sort -n | tail -20
# Values > 1000ms indicate lock contention
```

**Fix:**

BAD: Single global write lock across matching + location update.
GOOD: Separate driver state (available/busy) from location data.
Match on a snapshot of state (read at batch start). Update state
atomically via CAS (compare-and-swap) after match assignment.
Location updates never block on matching lock.

**Prevention:** Measure lock wait time in matching engine; design
matching to operate on a snapshot, not live data; use region-
partitioned matching to reduce contention scope.

---

### \U0001f517 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-023 - Geo-Replication]] - location data requires
  geographically distributed storage and indexing to serve
  drivers and riders in any region

**Builds On This (learn these next):**
- [[SYD-048 - Chat System Design]] - in-app messaging between
  driver and rider during the trip
- [[SYD-047 - Notification System Design]] - trip status and
  driver arrival push notifications
- [[SYD-027 - Capacity Planning]] - capacity planning for
  geospatial query load at peak demand events

**Alternatives / Comparisons:**
- [[SYD-048 - Chat System Design]] - contrasting real-time
  design (bidirectional messaging vs location-based matching)
- [[SYD-047 - Notification System Design]] - complementary
  notification layer for trip lifecycle events

---

### \U0001f4cc Quick Reference Card

```
+-----------------------------------------------------------+
| WHAT IT IS  | Real-time geospatial matching of riders     |
|             | to drivers in a two-sided marketplace       |
+-----------------------------------------------------------+
| PROBLEM     | Driver locations change constantly; radius  |
|             | queries on relational tables don't scale    |
+-----------------------------------------------------------+
| KEY INSIGHT | Index by geography (H3 cells), not by       |
|             | driver ID; match in batch, not greedy       |
+-----------------------------------------------------------+
| USE WHEN    | Building a location-based matching system   |
|             | with thousands of moving entities           |
+-----------------------------------------------------------+
| AVOID WHEN  | Static assets (use regular geo search);     |
|             | < 1K active drivers (relational is fine)    |
+-----------------------------------------------------------+
| TRADE-OFF   | Geospatial index complexity vs O(1)         |
|             | proximity queries at any scale              |
+-----------------------------------------------------------+
| ONE-LINER   | Stream locations into geo index; batch-     |
|             | match globally; surge-price per cell        |
+-----------------------------------------------------------+
| NEXT EXPLORE| Notification System Design (SYD-047)       |
+-----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Geospatial indexes (H3/S2/QuadTree) not relational lat/lon.
2. Batch matching (global optimisation) beats greedy nearest.
3. Surge pricing is a supply incentive signal, not just pricing.

**Interview one-liner:** "Ride-sharing systems maintain a live
geospatial index of driver locations (refreshed every 4 seconds),
run batch matching optimisation every 500ms, and compute per-cell
surge pricing from real-time supply-demand ratios."

---

### \U0001f48e Transferable Wisdom

**Reusable Engineering Principle:**
Index data by the dimension you query most. Traditional relational
databases cannot efficiently answer "find all entities within 500m"
at high update rates. Geospatial indexes answer proximity queries
in O(log n). This principle applies whenever the primary query
dimension differs from the natural identity dimension of the data.

**Where else this pattern appears:**
- **Time-series databases:** InfluxDB and TimescaleDB index data
  by time first - the primary query dimension. Non-time-indexed
  databases perform full scans for time-range queries.
- **Log search:** Elasticsearch indexes by token (the query
  dimension) not by log line number - enabling sub-second full-
  text search across billions of log entries.
- **Recommendation systems:** User-item matrices indexed by user
  ID for fast recommendation lookup - indexed by the query
  dimension (who is asking), not the item dimension (what exists).

---

### \U0001f4a1 The Surprising Truth

Uber's early matching system was trivially simple: find the
nearest available driver and assign them. As Uber scaled, they
discovered that nearest-driver matching produced globally
suboptimal outcomes - it would match a rider to a driver 2
minutes away while a driver 4 minutes away was positioned to
serve 5 future riders the system could predict. The matching
problem evolved from a greedy local optimisation to a batched
global optimisation running at 500ms intervals - assigning
multiple riders to multiple drivers simultaneously for the
globally minimum expected wait time. The upgrade from greedy to
batch optimisation increased driver earnings by 15% without
adding a single new driver to the platform. The same supply
became 15% more valuable through smarter allocation alone.

---

### \U0001f9e0 Think About This Before We Continue

**Q1.** Should dispatch optimise primarily for ETA, driver
fairness, or marketplace efficiency?

*Hint:* Think about the tension between ETA (user experience),
driver fairness (equal work distribution), and marketplace
efficiency (maximise completed trips per driver-hour). Explore
whether a single objective function can capture all three or
whether multi-objective optimisation with weights is necessary
and how product metrics determine the weights.

**Q2.** How would you reduce incorrect matches caused by stale
driver location updates?

*Hint:* Think about what stale location means for matching: if
a driver's last known location is 30 seconds old, where are they
now? Explore whether you can predict the driver's current
position from their last known velocity and heading (dead
reckoning) and what threshold of staleness makes a match
incorrect enough to warrant exclusion.

**Q3 (Scale):** During New Year's Eve, demand spikes 10x and
driver supply remains flat. Surge pricing activates. Design the
surge pricing algorithm such that it increases supply (incentivises
drivers to come online) without causing rider churn (pricing out
most users).

*Hint:* Think about surge pricing as a two-sided marketplace
signal that must simultaneously incentivise supply and rationally
ration demand. Explore whether a capped surge multiplier
(1.0-2.5x) vs uncapped surge better balances the dual objective,
and how real-time measurement of driver-online response to surge
would inform the algorithm's feedback loop.
"""

write("SYD-048 - Chat System Design.md", syd048)
write("SYD-049 - Video Streaming Design.md", syd049)
write("SYD-050 - Ride-Sharing System Design.md", syd050)
print("\nAll 3 files written.")
