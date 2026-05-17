---
id: SYD-048
title: Chat System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-036, SYD-008
used_by: ""
related: SYD-036, SYD-008, SYD-037, SYD-047
tags:
  - architecture
  - websocket
  - realtime
  - messaging
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /syd/chat-system-design/
---

# SYD-048 - Chat System Design

⚡ TL;DR - A chat system delivers messages between
users in real-time with persistence. Core architecture:
WebSocket connections for real-time delivery (long-lived
TCP connection, bidirectional, low overhead vs HTTP polling).
Messages stored in a chat-optimized database (Cassandra
with row key = {sender_id + receiver_id + timestamp} or
{channel_id + timestamp}). Online/offline presence tracked
in Redis. Key challenges: message ordering guarantees,
exactly-once delivery, offline message delivery when the
recipient reconnects, and scaling WebSocket servers
horizontally while routing messages to the correct server.

| #048 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Push vs Pull Architecture, Caching | |
| **Related:** | Push vs Pull, Caching, Polling vs Webhooks, Notification System Design | |

---

### 🔥 The Problem This Solves

WhatsApp serves 100B+ messages per day to 2B users.
The fundamental challenge: when User A sends a message
to User B, the message must:
1. Reach User B's device in < 100ms if they are online
2. Be stored persistently and delivered when B comes online
3. Be ordered correctly (message 3 must not arrive before message 2)
4. Be acknowledged (A must know B received it)
5. Support group chats (1 sender → N receivers)

---

### 📘 Textbook Definition

**Chat system:** A real-time messaging platform that
enables bidirectional message exchange between users
(1:1) or groups of users. Messages are persisted,
delivered in order, and acknowledged. The system
maintains presence awareness (online/offline/typing).

**WebSocket:** A protocol (RFC 6455) that establishes
a persistent, full-duplex TCP connection between client
and server. Unlike HTTP (request → response), WebSocket
allows the server to push data to the client at any
time without polling. Standard for real-time chat,
gaming, and live data feeds.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
User sends message → WebSocket server receives → stores
message → routes to recipient's WebSocket server →
delivers to recipient's open connection.

**One analogy:**
> Think of chat servers as telephone switchboard operators:
>
> Each user is connected to one operator (WebSocket server).
> When you say something to the operator (send message),
> the operator writes it down (stores in DB), then connects
> to the other person's operator (routes via message broker),
> who relays it to the recipient (delivers via WebSocket).
>
> If the recipient is not connected, the message is left
> in their inbox (offline message store) for when they
> reconnect.

**One insight:**
The critical insight is that WebSocket servers are
stateful - each server knows which users are connected
to it. When User A sends a message to User B, you must
route the message to the specific WebSocket server
that holds User B's connection. This routing problem
is solved with a presence service (Redis) that maps
user_id → server_id.

---

### 🔩 First Principles Explanation

**WEBSOCKET vs POLLING:**
```
HTTP Short Polling:
  Client: GET /new-messages every 5 seconds
  Server: return new messages (or empty)
  
  Latency: up to 5 seconds (polling interval)
  Load: N users × (1 req / 5 sec) = 20% of 1M users
    = 40K req/sec just for polling (mostly empty)
  Efficient: No (most responses are empty)

HTTP Long Polling:
  Client: GET /new-messages (server holds request open)
  Server: hold connection until message arrives, then respond
  Client: immediately opens new long-poll connection
  
  Latency: ~50-200ms (HTTP overhead)
  Connections: N concurrent open HTTP connections
  Problems: HTTP headers on every message, half-duplex

WebSocket:
  Client: upgrades HTTP connection to WebSocket
  Server: holds connection open indefinitely
  Bidirectional: server can push anytime; client can send anytime
  
  Latency: < 50ms (persistent connection, minimal framing overhead)
  Overhead: 2-14 bytes per frame vs 500+ bytes for HTTP
  Connections: N persistent TCP connections (server must
    handle N connections in memory)
```

**MESSAGE ROUTING:**
```
Challenge: 10 WebSocket servers, 1M users. User A
(on server-3) sends message to User B. User B could
be on any of the 10 servers.

Solution: Presence store (Redis)
  On connect: SET user:{user_id}:server = "ws-server-3" EX 300
  On disconnect: DEL user:{user_id}:server
  On heartbeat: EXPIRE user:{user_id}:server 300 (refreshed)

On message from A to B:
  1. WebSocket server-3 receives message from A
  2. Save to message DB (persistent)
  3. Lookup: GET user:{user_id_B}:server → "ws-server-7"
  4. Publish message to Redis Pub/Sub channel "ws-server-7"
  5. ws-server-7 subscribes to its own channel;
     receives message and pushes to User B's connection
  6. If user_id_B:server = null: User B is offline
     → store in offline message queue (Kafka/Redis)
     → on reconnect: flush offline messages to User B
```

**MESSAGE STORAGE (CASSANDRA PATTERN):**
```
Table: messages
  partition key: (sender_id, receiver_id) [for 1:1]
    OR (channel_id) [for group]
  clustering key: message_id DESC (newest first)
  columns: content, sent_at, status

Why Cassandra?
  - Write-heavy: every message is one write
  - Read pattern: "latest 50 messages for conversation X"
    = scan by partition key, limit by clustering key
  - No complex joins needed
  - Horizontal scale: partition by conversation_id
  - Fast writes: LSM-tree structure

Message ID: Snowflake (timestamp-based)
  - Sortable by time (enables clustering key sort)
  - Globally unique
  - No coordination needed

Retention:
  Cassandra TTL per row: e.g., 90 days
  Older messages: archived to S3 / data warehouse
```

---

### 🧪 Thought Experiment

**SIZING: Design chat at WhatsApp scale**

Users: 2B registered, 500M daily active (DAU)
Messages/day: 100B = 1.16M messages/second
Avg message size: 100 bytes text + metadata = 300 bytes
Total storage/day: 100B × 300 bytes = 30TB/day
Storage/year: ~10PB (with replication factor 3: 30PB)

Peak load: 10x = 11.6M messages/second

**WebSocket server capacity:**
1 server: 100K concurrent connections (with tuning:
  ulimit, epoll, non-blocking I/O, 16-32 GB RAM).
500M DAU (but online simultaneously: 20% = 100M).
100M connections / 100K per server = 1,000 WS servers.

**Message writes:**
Cassandra handles 1M+ writes/second on a moderate cluster.
For 11.6M writes/sec (peak): ~50-100 Cassandra nodes.

**Presence store:**
100M online users in Redis: 100M keys × ~50 bytes = 5GB.
Trivial for Redis. Multi-node cluster for redundancy.

---

### 🧠 Mental Model / Analogy

> Imagine the post office became instant:
>
> WebSocket connection = a permanent open phone line
>   between you and your nearest post office.
>
> Sending a message = speaking into the phone.
>   The operator (server) writes it down instantly.
>
> Message routing = the operator calls the recipient's
>   post office (their WebSocket server via Redis pub/sub).
>
> Offline delivery = if the recipient's phone is off,
>   the message sits in their mailbox. When they turn
>   on their phone (reconnect), all waiting messages
>   are read to them at once.
>
> The DB = the permanent record of all messages ever
>   written, regardless of delivery status.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A chat system lets two or more people send messages
to each other instantly. Messages appear in real-time
on both screens (like talking on the phone, but written).
If someone is offline, they see the messages when they
log back in.

**Level 2 - How to use it (junior developer):**
WebSocket server: accept connections, receive messages,
save to database, route to recipient. Use a key-value
store (Redis) to track which server each user is connected
to. Store messages in a database with timestamp ordering.
Push unread messages to users when they reconnect.

**Level 3 - How it works (mid-level engineer):**
WebSocket servers are stateful (hold user connections).
Route messages via Redis Pub/Sub: lookup recipient's
server, publish to that server's channel. Message storage:
Cassandra with partition key = conversation_id and
clustering key = message_id (Snowflake, timestamp-based).
Offline messages: queued in Kafka or Redis list per user,
flushed on reconnect. Delivery receipts: 3-state model
(sent, delivered, read).

**Level 4 - Why it was designed this way (senior/staff):**
Cassandra for messages: write-heavy workload (every message
is a write), simple read pattern (latest N by conversation),
linear horizontal scale. WebSocket over HTTP polling: orders
of magnitude lower overhead per message, true bidirectional
push. Redis for presence: sub-millisecond lookup, automatic
TTL expiry (presence info expires if heartbeat stops - handles
abrupt disconnections). Redis Pub/Sub for cross-server routing:
each server subscribes to exactly one channel (its own server
ID), guaranteeing that messages are routed only to the server
holding the recipient's connection.

**Level 5 - Mastery (distinguished engineer):**
At WhatsApp scale, the end-to-end encryption requirement adds
a fundamental constraint: the server never sees plaintext.
Messages encrypted on the sender device, decrypted on the
recipient device. This means the server cannot read or index
message content. Metadata (sender, recipient, timestamp) is
unencrypted. Key distribution (Signal Protocol) is a separate
subsystem. For group chats at scale: sender encryption with
N keys (one per group member) vs sender key (one key per
group, shared) - the trade-off between forward secrecy and
fan-out efficiency. At the operational level: message ordering
in group chats is a distributed systems problem (no global
clock). Logical clocks (Lamport timestamps or vector clocks)
maintain causal ordering. Total ordering requires consensus
(Paxos/Raft) - too slow for chat latency. Most systems use
causal ordering (weaker guarantee, but fast enough).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CHAT MESSAGE DELIVERY                               │
│                                                      │
│  User A (on ws-server-1) sends message to User B   │
│                                                      │
│  1. ws-server-1 receives message via WebSocket      │
│  2. Generate Snowflake message_id                   │
│  3. WRITE to Cassandra (async, returns quickly)     │
│  4. Lookup Redis: user:B:server → "ws-server-3"    │
│  5. PUBLISH to Redis Pub/Sub: channel="ws-server-3" │
│  6. ws-server-3 receives from its subscription      │
│  7. Find User B's WebSocket connection              │
│  8. Send message frame to User B                   │
│  9. User B sends ACK frame back                    │
│  10. ws-server-3 publishes ACK to ws-server-1 via  │
│      Redis Pub/Sub                                 │
│  11. ws-server-1 sends "delivered" receipt to A    │
│                                                      │
│  If User B offline (step 4: key not found):        │
│  4b. Store in offline_queue:{user_B_id} (Redis list)│
│  On User B reconnect:                              │
│      LRANGE offline_queue:{B} → flush all messages │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - WebSocket chat server with routing**
```python
import asyncio
import json
import redis.asyncio as aioredis
import websockets
from collections import defaultdict

# Connection registry: {user_id: websocket}
# In-memory per server instance
connected_users = {}

r = aioredis.Redis()
SERVER_ID = "ws-server-1"

async def register_user(user_id: int, websocket):
    """Register user connection, set presence."""
    connected_users[user_id] = websocket
    # Set presence with 5-min TTL (refreshed by heartbeat)
    await r.setex(f"user:{user_id}:server",
                  300, SERVER_ID)
    # Flush offline messages
    await flush_offline_messages(user_id, websocket)

async def flush_offline_messages(user_id: int,
                                   websocket):
    """Deliver queued offline messages on reconnect."""
    queue_key = f"offline:{user_id}"
    messages = await r.lrange(queue_key, 0, -1)
    if messages:
        await r.delete(queue_key)
        for msg_bytes in messages:
            await websocket.send(msg_bytes)

async def route_message(sender_id: int, recipient_id: int,
                          content: str, message_id: str):
    """Route message to recipient's WebSocket server."""
    # Save to Cassandra (async)
    await save_message_to_db(
        sender_id, recipient_id, message_id, content)

    # Find recipient's server
    server = await r.get(f"user:{recipient_id}:server")

    if server and server.decode() == SERVER_ID:
        # Recipient is on THIS server
        ws = connected_users.get(recipient_id)
        if ws:
            await ws.send(json.dumps({
                "type": "message",
                "message_id": message_id,
                "sender_id": sender_id,
                "content": content,
            }))
            return

    if server:
        # Recipient is on another server: pub/sub routing
        channel = server.decode()
        await r.publish(channel, json.dumps({
            "type": "deliver",
            "recipient_id": recipient_id,
            "sender_id": sender_id,
            "message_id": message_id,
            "content": content,
        }))
    else:
        # Recipient offline: store in offline queue
        await r.rpush(
            f"offline:{recipient_id}",
            json.dumps({
                "type": "message",
                "message_id": message_id,
                "sender_id": sender_id,
                "content": content,
            })
        )

async def subscribe_to_routing():
    """Subscribe to this server's routing channel."""
    async with r.pubsub() as pubsub:
        await pubsub.subscribe(SERVER_ID)
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                if data["type"] == "deliver":
                    recipient_id = data["recipient_id"]
                    ws = connected_users.get(recipient_id)
                    if ws:
                        await ws.send(json.dumps(data))
```

**Example 2 - Polling anti-pattern (BAD)**
```python
# BAD: HTTP polling - high latency, high server load
@app.get("/messages/new")
async def poll_messages(user_id: int,
                         last_message_id: str):
    # Client polls every 3 seconds
    # Even when no new messages
    # At 1M users: 333K requests/sec of mostly empty responses
    messages = db.query(
        "SELECT * FROM messages WHERE recipient_id = %s "
        "AND id > %s LIMIT 50",
        user_id, last_message_id
    )
    return messages
    # Latency: up to 3 seconds before user sees new message
    # Load: massive (mostly wasted empty responses)

# GOOD: WebSocket - server pushes on new message
# Zero polling overhead; sub-50ms delivery latency
```

---

### ⚖️ Comparison Table

| Approach | Latency | Server Load | Bidirectional | Complexity |
|---|---|---|---|---|
| **Short Polling** | 1-5 sec | High (empty responses) | No | Simple |
| **Long Polling** | 50-200ms | Medium | No | Medium |
| **WebSocket** | < 50ms | Low per connection | Yes | High |
| **SSE (Server-Sent Events)** | < 100ms | Low per connection | No (server-to-client only) | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| WebSocket servers can be scaled stateless like HTTP servers | WebSocket servers are stateful - each holds open TCP connections. You cannot put a round-robin load balancer in front and restart servers freely. Users must reconnect when their WebSocket server restarts. Use sticky sessions (route by user_id hash) or handle reconnection gracefully (client reconnects within 1-2 seconds). |
| Cassandra guarantees message ordering within a conversation | Cassandra's clustering key provides ordering within a partition (conversation). But concurrent inserts with the same timestamp can cause ordering issues. Use Snowflake IDs as clustering keys (monotonically increasing) to guarantee ordering. Never use wall-clock timestamps as the sole ordering key. |
| Real-time chat requires strong consistency | Chat systems use eventual consistency. A message sent by User A may be acknowledged before it appears in User B's history. Strong consistency (across all replicas before acknowledging) adds too much latency for real-time chat. The trade-off: occasional brief inconsistency (B sees message 2 before message 1 for milliseconds) is acceptable for chat UX. |

---

### 🚨 Failure Modes & Diagnosis

**Message Duplication on Network Reconnect**

**Symptom:**
When a user reconnects after a brief network drop,
messages sent just before the disconnect appear twice
in the chat history - once in the chat window and
again after re-delivery.

**Root Cause:**
User A sent a message. Server received it and stored
it in Cassandra. But the ACK to User A was lost during
the network drop. User A's client retries (correct
behavior: at-least-once send). Server receives the
message again, stores a second copy.

**Fix - Client-side idempotency key:**
```python
# Client: send with idempotency key
import uuid

def send_message(content: str, recipient_id: int):
    message_id = str(uuid.uuid4())  # Client-generated
    payload = {
        "message_id": message_id,  # Idempotency key
        "recipient_id": recipient_id,
        "content": content,
    }
    # Store locally before sending (for retry)
    local_pending[message_id] = payload
    websocket.send(json.dumps(payload))

# Server: deduplicate by message_id
async def on_receive_message(data: dict):
    message_id = data["message_id"]
    # Check if already processed
    dedup_key = f"msg:processed:{message_id}"
    already_processed = not await r.set(
        dedup_key, "1", nx=True, ex=86400)  # 24h
    if already_processed:
        # Already stored: just send ACK (don't re-store)
        await send_ack(message_id)
        return
    
    # New message: store and route
    await save_message_to_db(data)
    await route_message(data)
    await send_ack(message_id)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Push vs Pull Architecture` - WebSocket is a push
  model; polling is a pull model
- `Caching` - Redis for presence tracking and offline
  message queuing

**Builds On This (learn these next):**
- `Polling vs Webhooks` - contrast with push model
- `Notification System Design` - offline message
  delivery via push notifications

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CONNECTION  │ WebSocket: persistent, bidirectional TCP  │
│             │ Stateful server: holds user connections   │
├─────────────┼──────────────────────────────────────────  │
│ ROUTING     │ Redis: user:{id}:server → server_id      │
│             │ Redis Pub/Sub for cross-server delivery   │
├─────────────┼──────────────────────────────────────────  │
│ STORAGE     │ Cassandra: partition=(conv_id),          │
│             │ cluster=message_id (Snowflake, sorted)   │
├─────────────┼──────────────────────────────────────────  │
│ OFFLINE     │ Redis list offline:{user_id}. Flush on   │
│             │ reconnect. Expire after 7 days.          │
├─────────────┼──────────────────────────────────────────  │
│ DELIVERY    │ Client ACK → "delivered". User opens     │
│             │ chat → "read". 3-state: sent/delivered/read│
├─────────────┼──────────────────────────────────────────  │
│ DUPLICATION │ Client-generated message_id + Redis NX   │
│             │ dedup on server (idempotent insert)      │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "WebSocket + Redis routing + Cassandra  │
│             │  storage + offline queue = chat"        │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Video Streaming Design → Ride-Sharing    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. WebSocket (not HTTP polling) for real-time chat.
   Servers are stateful: each holds user connections.
   Route cross-server messages via Redis Pub/Sub
   (lookup user's server → publish to that server's channel).
2. Cassandra for message storage: partition by conversation_id,
   cluster by Snowflake message_id (monotonically increasing
   for deterministic ordering). Write-heavy workload; Cassandra
   excels here.
3. Client-generated message_id as idempotency key. Server
   uses Redis SET NX to deduplicate retries. Without this,
   network drops cause message duplication (client retries
   on ACK timeout, server stores twice).

**Interview one-liner:**
"Chat system: WebSocket connections (not polling) for real-time, sub-50ms
delivery. WebSocket servers are stateful - track user:server mapping in
Redis (TTL refreshed by heartbeat). Cross-server routing via Redis Pub/Sub:
look up recipient's server, publish to that channel, subscriber delivers.
Offline users: store messages in Redis list, flush on reconnect. Storage:
Cassandra with partition key=conversation_id, clustering key=Snowflake
message_id (time-sorted, unique). Duplication prevention: client-generated
message_id + Redis SET NX on server to reject retransmissions."
