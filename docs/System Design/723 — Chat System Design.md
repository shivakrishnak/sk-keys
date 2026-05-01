---
layout: default
title: "Chat System Design"
parent: "System Design"
nav_order: 723
permalink: /system-design/chat-system-design/
number: "723"
category: System Design
difficulty: ★★★
depends_on: "WebSockets, Message Queues, Caching"
used_by: "System Design Interview"
tags: #advanced, #system-design, #interview, #real-time, #websocket
---

# 723 — Chat System Design

`#advanced` `#system-design` `#interview` `#real-time` `#websocket`

⚡ TL;DR — **Chat System Design** delivers real-time messages using WebSocket persistent connections, stores messages in Cassandra (append-optimised for high write throughput), and synchronises presence and unread counts via Redis, supporting 1-1 and group chat at scale.

| #723            | Category: System Design             | Difficulty: ★★★ |
| :-------------- | :---------------------------------- | :-------------- |
| **Depends on:** | WebSockets, Message Queues, Caching |                 |
| **Used by:**    | System Design Interview             |                 |

---

### 📘 Textbook Definition

A **Chat System** provides real-time bidirectional message exchange between users, delivered with low latency (< 100ms) and high reliability (at-least-once delivery with deduplication). Key design considerations: (1) **transport layer**: WebSockets for bidirectional persistent connections (vs. long-polling for clients that don't support WebSockets); (2) **message storage**: Cassandra or HBase for time-ordered, high-write-throughput message persistence per conversation; (3) **message delivery**: online users receive messages via WebSocket push; offline users receive messages on reconnection (message sync protocol using last_received_message_id); (4) **presence**: user online/offline status tracked in Redis with heartbeat TTL; (5) **group chat**: fan-out challenges for large groups (>500 members) similar to news feed; (6) **unread counts**: counters per conversation per user in Redis. Reference systems: WhatsApp (XMPP over WebSocket), Slack (WebSocket), Facebook Messenger (MQTT/WebSocket hybrid).

---

### 🟢 Simple Definition (Easy)

Chat System: two people each have an open phone line to the server (WebSocket). Alice types → instantly sent to server → instantly pushed to Bob's phone line. If Bob is offline: message stored in database. When Bob reconnects: pulls all messages since last seen. All messages persist in a database (like conversation history). User online/offline: tracked in Redis (expires after 30 seconds without heartbeat).

---

### 🔵 Simple Definition (Elaborated)

WhatsApp at scale: 2 billion users, 100 billion messages per day. Each user's phone has a persistent WebSocket connection to a chat server. Alice sends message to Bob: client → chat server (over WebSocket) → message stored in Cassandra → if Bob is online: pushed via Bob's WebSocket connection → delivered in < 50ms. If Bob offline: message waits in DB. Bob reconnects: "give me all messages since message_id X" → receives all missed messages. Group chat of 1,000 members: one message fan-outed to 1,000 active users' WebSocket connections.

---

### 🔩 First Principles Explanation

**Chat system architecture: message flow, storage, and delivery:**

```
MESSAGE STORAGE MODEL:

  Why Cassandra (not MySQL) for chat messages?

  Chat message access pattern:
    Write: every message = 1 INSERT. Heavy write workload.
    Read: "fetch last 50 messages for conversation X" → time-range query.
    Delete: rare (individual message delete, conversation clear).
    Update: rare (edit message, add reaction).

  MySQL problem: 100B messages/day = 1M inserts/second peak.
                 Relational DB: table lock, B-tree insert overhead → bottleneck.

  Cassandra sweet spot:
    Append-optimised: LSM tree structure → writes as fast as sequential disk I/O.
    Partition by conversation_id: all messages in same chat → same Cassandra partition.
    Sort by message_id (time-ordered) within partition → efficient range reads.
    Horizontal scaling: add nodes → write capacity scales linearly.

  Message table schema (Cassandra):

  CREATE TABLE messages (
      conversation_id   UUID,           -- partition key
      message_id        TIMEUUID,       -- clustering key (time-ordered UUID)
      sender_id         BIGINT,
      content           TEXT,
      media_url         TEXT,
      message_type      TEXT,           -- TEXT, IMAGE, VIDEO, FILE
      is_deleted        BOOLEAN,
      created_at        TIMESTAMP,
      PRIMARY KEY (conversation_id, message_id)
  ) WITH CLUSTERING ORDER BY (message_id DESC)   -- newest first
    AND COMPACTION = {'class': 'TimeWindowCompactionStrategy',
                      'compaction_window_unit': 'DAYS',
                      'compaction_window_size': 7};  -- compact week-old data together

  Query: "Fetch last 50 messages for conversation X":
    SELECT * FROM messages WHERE conversation_id = X
    ORDER BY message_id DESC LIMIT 50;
    → Reads from single Cassandra partition → O(log N) → fast

  Query: "Fetch messages since message_id M" (sync on reconnect):
    SELECT * FROM messages WHERE conversation_id = X
    AND message_id > M
    ORDER BY message_id ASC;

WEBSOCKET CONNECTION MANAGEMENT:

  Problem: 500M concurrent online users × 1 WebSocket connection each.

  Each WebSocket server (chat server) handles:
    Memory per WebSocket: ~10 KB (headers, buffers, session state)
    Per server: 100,000 concurrent connections × 10 KB = 1 GB RAM
    Fleet: 500M connections / 100K per server = 5,000 chat servers

  Connection routing:
    Client connects → Load balancer → sticky routing (same session → same chat server)
    Why sticky? WebSocket = persistent connection → same client always hits same server.
    NOT round-robin (would send same client to different servers on each request).

  Chat server: in-memory map of {user_id → websocket_connection}
    Efficient: send message to online user = lookup user_id → push via WebSocket (O(1))

  Cross-server delivery (Alice on Server 1, Bob on Server 2):
    Alice → Server 1 → publishes to Redis Pub/Sub channel "user:{bob_id}"
    Server 2 → subscribes to "user:{bob_id}" → receives message → pushes to Bob's WebSocket

    Pub/Sub channel per user: each server subscribes only to channels for its connected users.

MESSAGE DELIVERY PROTOCOL:

  At-least-once delivery + client-side deduplication:

  1. Alice sends message:
     Client: POST /send or WebSocket message with client_message_id = UUID
     Server: stores in Cassandra → returns server_message_id (TIMEUUID) + server timestamp
     Client: stores mapping client_message_id → server_message_id (marks as "sent")

  2. Delivery to Bob (online):
     Server 1 → Redis Pub/Sub → Server 2 → WebSocket push to Bob
     Bob's client: receives {server_message_id, ...}
     Bob's client: sends ACK back to Server 2: "received message_id M"
     Server 2: updates delivery status in Redis: delivered:{message_id}:{bob_id} = true

  3. Delivery to Bob (offline):
     Bob reconnects → handshake: "my last_seen_message_id = M"
     Server: SELECT messages WHERE conversation_id = X AND message_id > M → send all missed
     Bob's client: receives missed messages → ACKs each

  4. Read receipts (double ticks on WhatsApp):
     Bob opens chat → "seen" event sent to server
     Server: updates read_status table → Alice's client subscribes → shows "read" indicator

PRESENCE SYSTEM:

  Online status (Redis TTL-based):

  Client: sends heartbeat to server every 5 seconds.
  Server: SET presence:{user_id} "online" EX 10  // TTL = 2× heartbeat interval

  If client disconnects (TTL expires after 10s):
    presence:{user_id} key disappears from Redis → status = "offline"

  Checking Bob's online status:
    EXISTS presence:{bob_id} → 1 = online, 0 = offline

  "Last seen" timestamp:
    On TTL expiry: Redis keyspace notification → update users.last_seen in DB
    Show: "last seen 5 minutes ago"

  Privacy: users can hide presence ("seen by nobody" mode)
    → Simply don't write to presence:{user_id} Redis key

GROUP CHAT FAN-OUT:

  Small groups (< 100 members): send to each member's WebSocket directly
    server receives group message → look up group members → push to each member's WebSocket

  Large groups (100-1,000 members):
    Store message once in messages table (no duplication).
    Fan-out: pub/sub to all online members' chat servers.
    Offline members: pull messages on reconnect from shared group message stream.

  Very large groups (>1,000 members — broadcast channels):
    Fan-out on read: don't push to offline members (too many).
    Online members: subscribed to channel via WebSocket → receive in real-time.
    Offline members: pull last N messages on reconnect (page through Cassandra).
    WhatsApp broadcast limit: 256 members (beyond that, performance degrades).
    Slack channel: fan-out on write for small channels, fan-out on read for huge ones.

UNREAD COUNT:

  Efficient unread count per conversation per user:

  Redis: HASH "unread:{user_id}" → {conversation_id: count}

  New message in conversation C: HINCRBY unread:{user_id} C 1 (for each recipient)
  User opens conversation C: HSET unread:{user_id} C 0 (reset to 0)
  Total unread: HVALS unread:{user_id} → sum all values → "23 unread messages"

  This avoids counting messages in Cassandra every time user opens app.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT dedicated chat architecture:

- HTTP polling: client requests every 1 second = 1B requests/second for 100M users → server overload
- MySQL for messages: 1M inserts/second → B-tree contention, table locks → bottleneck

WITH chat architecture:
→ WebSockets: persistent connections, server-initiated push → 1 connection per user (not 1 request/second)
→ Cassandra: LSM-tree append writes → 1M inserts/second without contention
→ Redis pub/sub: cross-server message routing without inter-server coordination

---

### 🧠 Mental Model / Analogy

> A telephone exchange with operator-assisted message routing. Each caller (user) has a dedicated line to an operator (chat server). When Alice calls the exchange and dictates a message for Bob: the operator writes it in the logbook (Cassandra), checks if Bob's line is active (Redis presence), and if so, rings Bob immediately (WebSocket push to Bob's operator → Bob's phone). If Bob's line is inactive (offline): the message waits in the logbook. When Bob reconnects ("I last received message at page 42"): operator reads all log entries after page 42 to Bob.

"Dedicated phone line to operator" = persistent WebSocket connection to chat server
"Writing in logbook" = INSERT into Cassandra messages table (durable storage)
"Operator rings Bob's line" = WebSocket push via Redis pub/sub to Bob's chat server
"Bob's line inactive" = offline user (no presence key in Redis)
"Bob asks for all entries after page 42" = message sync on reconnect (WHERE message_id > last_seen)

---

### ⚙️ How It Works (Mechanism)

**WebSocket message handler (Spring Boot):**

```java
@Component
public class ChatWebSocketHandler extends TextWebSocketHandler {

    @Autowired private MessageRepository messageRepository;  // Cassandra
    @Autowired private RedisTemplate<String, String> redis;
    @Autowired private KafkaTemplate<String, ChatMessage> kafka;

    // In-memory: userId → WebSocket session (for this server instance only)
    private final Map<Long, WebSocketSession> activeSessions = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        Long userId = getUserIdFromSession(session);
        activeSessions.put(userId, session);

        // Mark as online in Redis (TTL = 10 seconds, refreshed by heartbeats):
        redis.opsForValue().set("presence:" + userId, "online", 10, TimeUnit.SECONDS);

        // Subscribe this server to pub/sub channel for this user:
        // (handled by Redis message listener container — configured separately)
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) {
        ChatMessage msg = deserialize(message.getPayload());

        if ("HEARTBEAT".equals(msg.getType())) {
            // Refresh presence TTL:
            redis.expire("presence:" + msg.getSenderId(), 10, TimeUnit.SECONDS);
            return;
        }

        if ("MESSAGE".equals(msg.getType())) {
            // 1. Store message in Cassandra:
            UUID messageId = messageRepository.save(
                msg.getConversationId(), msg.getSenderId(),
                msg.getContent(), msg.getClientMessageId()
            );

            // 2. Acknowledge to sender (confirm stored):
            sendToUser(msg.getSenderId(), new AckMessage(msg.getClientMessageId(), messageId));

            // 3. Fan-out to recipients via Kafka (async delivery):
            for (long recipientId : msg.getRecipientIds()) {
                kafka.send("chat.messages", new ChatDeliveryMessage(
                    messageId, recipientId, msg.getConversationId(), msg.getContent()
                ));

                // Increment unread count in Redis:
                redis.opsForHash().increment("unread:" + recipientId,
                    msg.getConversationId().toString(), 1);
            }
        }
    }

    public void deliverToUser(long userId, ChatDeliveryMessage message) {
        WebSocketSession session = activeSessions.get(userId);
        if (session != null && session.isOpen()) {
            // User is on THIS server — deliver directly:
            sendToUser(userId, message);
        }
        // If not on this server: handled by Redis pub/sub routing
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        Long userId = getUserIdFromSession(session);
        activeSessions.remove(userId);
        // Presence expires naturally via Redis TTL (no explicit delete needed)
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Real-time communication requirement
        │
        ▼
Chat System Design ◄──── (you are here)
(WebSocket + Cassandra + Redis)
        │
        ├── WebSockets (persistent bidirectional transport)
        ├── Cassandra (time-ordered message storage)
        └── Redis (presence + unread counts + pub/sub routing)
```

---

### 💻 Code Example

**Message sync on reconnect (pull all missed messages):**

```python
# Client-side reconnect logic:
import websocket
import json

class ChatClient:
    def __init__(self, user_id: int, server_url: str):
        self.user_id = user_id
        self.server_url = server_url
        self.last_received_message_id = self._load_last_message_id()  # from local DB

    def on_open(self, ws):
        # On connection: request all missed messages:
        sync_request = {
            "type": "SYNC",
            "user_id": self.user_id,
            "last_message_id": self.last_received_message_id
        }
        ws.send(json.dumps(sync_request))

    def on_message(self, ws, message):
        msg = json.loads(message)

        if msg["type"] == "SYNC_RESPONSE":
            # Batch of missed messages since last_message_id:
            for missed_msg in msg["messages"]:
                self._store_locally(missed_msg)
                self._display_in_ui(missed_msg)
            self.last_received_message_id = msg["latest_message_id"]
            self._save_last_message_id(self.last_received_message_id)

        elif msg["type"] == "MESSAGE":
            # Real-time incoming message:
            self._store_locally(msg)
            self._display_in_ui(msg)
            self.last_received_message_id = msg["message_id"]
            self._save_last_message_id(self.last_received_message_id)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| WebSockets require a dedicated server — can't use stateless servers | WebSocket servers are stateful in that each connection is "pinned" to a server, but the server itself doesn't need to be stateful if connection state is stored externally. Message routing uses Redis pub/sub: message for user X → published to channel `user:X` → whichever server has X's WebSocket subscribes and delivers. Application servers can scale horizontally with shared Redis                        |
| Message ordering is guaranteed by timestamp                         | Timestamps (even millisecond precision) are not reliable for ordering in distributed systems. Clock skew between servers can cause messages to appear out of order. Use TIMEUUID (Cassandra) or monotonically increasing sequence IDs from a coordination service. TIMEUUID embeds time + UUID → sortable but unique → no timestamp collision problem                                                                |
| Group chat fan-out works like direct messages                       | Direct messages: route to 1 user. Group message: must fan-out to N users. For a group of 1,000 members: 1 message = 1,000 WebSocket pushes. If 10,000 messages/second in a large group: 10M WebSocket pushes/second. Architecture must differentiate: small groups (direct push), large groups (pub/sub channel per group), broadcast channels (pull on demand)                                                      |
| Chat messages can be stored in a relational database                | At WhatsApp scale (100B messages/day = ~1.2M inserts/second), relational DB B-tree writes create severe contention. Cassandra's LSM-tree converts random writes to sequential log appends → handles 1M inserts/second per node. The conversation_id partition key ensures all messages for a conversation are co-located (fast reads). Relational DBs are appropriate for small-scale chat (< 1,000 messages/second) |

---

### 🔥 Pitfalls in Production

**Message reordering in high-concurrency group chat:**

```
PROBLEM: Messages appear out of order for users in high-latency networks

  Group chat: Alice (US), Bob (EU), Carol (APAC)
  Messages sent at nearly the same time:

  Alice sends "Anyone ready for the call?" at T=100ms (US server clock)
  Bob sends   "Yes, joining now"           at T=99ms  (EU server clock — 1ms behind)

  Cassandra: TIMEUUID generated from server clock at INSERT time.
  Bob's message: TIMEUUID(T=99ms) — earlier clock time
  Alice's message: TIMEUUID(T=100ms) — later clock time

  Cassandra sort order: Bob's message appears BEFORE Alice's message.
  All clients see: "Yes, joining now" then "Anyone ready for the call?" — WRONG ORDER.

ROOT CAUSE: Distributed clocks are not perfectly synchronised (NTP sync: ±10ms drift).

FIX 1: MONOTONIC SERVER SEQUENCE:
  Use a centralized sequence service (or Snowflake ID) instead of pure timestamp.
  Each message gets a globally monotonic message_id.
  Ordering guaranteed by sequence, not timestamp.
  Cost: centralized service = potential bottleneck. Solution: Snowflake IDs (per-server sequence).

FIX 2: CLIENT-SIDE SEQUENCE NUMBERS:
  Each client maintains a per-conversation sequence number.
  Alice: sends message with {conversation_id, client_seq: 42}
  Bob: sends message with {conversation_id, client_seq: 38}

  Server: assigns server_seq per conversation (atomic INCR per conversation in Redis).
  Message ordering: by server_seq (not client clock or server clock).
  Client: receives messages out of order → buffer → display in server_seq order.

  This is how Slack handles message ordering.

FIX 3: LAMPORT TIMESTAMPS:
  Causal ordering for distributed systems.
  Each message carries a logical clock value.
  Server increments logical clock on each message receive.
  Client displays by logical clock order (not wall clock).
  Guarantees causal ordering: "Yes, joining now" is always after "Anyone ready?"
  if causally related (even across distributed servers).
```

---

### 🔗 Related Keywords

- `WebSockets` — transport protocol for persistent bidirectional connections (client push + server push)
- `Cassandra` — time-series optimised storage for high-write message persistence
- `Redis` — presence tracking (TTL-based), unread counts, pub/sub message routing
- `Message Queues` — Kafka for async fan-out of messages to offline-user delivery workers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ WebSocket for real-time delivery; Cassandra│
│              │ for message storage; Redis pub/sub routing│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Real-time messaging; presence; group chat; │
│              │ channel broadcast                         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Timestamp-only ordering (clock skew);     │
│              │ MySQL for 1M+ messages/second writes      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Telephone exchange: dedicated operator   │
│              │  line per caller; logbook survives        │
│              │  disconnections."                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WebSockets → Cassandra Data Model         │
│              │ → Presence System Design                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** WhatsApp supports "end-to-end encryption" (E2EE): messages are encrypted on the sender's device, and only the recipient's device can decrypt them. The server never sees plaintext. How does E2EE affect the chat system architecture described in this entry? Specifically: can the server still store messages in Cassandra? Can it still show unread counts? Can you search message content? What features become impossible or much harder to implement with E2EE, and what additional components are needed (e.g., key exchange protocol)?

**Q2.** Design the "last seen" privacy feature: User A sets privacy to "My contacts only" for last-seen timestamp. User B (not in A's contacts) should see "Last seen recently" instead of the exact timestamp. User A also wants to see last-seen for others, but if A hides their last-seen, they shouldn't be able to see others' (WhatsApp's current policy). Describe: (a) the data model for last-seen visibility settings; (b) how you enforce the mutual visibility rule efficiently; (c) how you handle the case where 2 billion users each have potentially different privacy settings for their last-seen data.
