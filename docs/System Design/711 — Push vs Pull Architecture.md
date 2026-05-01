---
layout: default
title: "Push vs Pull Architecture"
parent: "System Design"
nav_order: 711
permalink: /system-design/push-vs-pull/
number: "711"
category: System Design
difficulty: ★★★
depends_on: "Fan-Out on Write vs Read, Polling vs Webhooks"
used_by: "News Feed Design, Notification System Design, Polling vs Webhooks"
tags: #advanced, #architecture, #distributed, #messaging, #performance
---

# 711 — Push vs Pull Architecture

`#advanced` `#architecture` `#distributed` `#messaging` `#performance`

⚡ TL;DR — **Push** sends data to consumers as soon as it's available (server-initiated); **Pull** waits for consumers to request data when they're ready (client-initiated) — each suits different latency, coupling, and load distribution requirements.

| #711 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Fan-Out on Write vs Read, Polling vs Webhooks | |
| **Used by:** | News Feed Design, Notification System Design, Polling vs Webhooks | |

---

### 📘 Textbook Definition

**Push Architecture** (server-initiated delivery): the server detects a state change and proactively sends data to registered clients without the client having to request it. Mechanisms: WebSockets, Server-Sent Events (SSE), webhooks, push notifications (FCM/APNs), message brokers with consumer subscriptions (Kafka consumer groups, RabbitMQ consumers). Push is optimal for real-time, low-latency delivery where client availability is reliable. **Pull Architecture** (client-initiated retrieval): clients periodically request data from the server at their own pace. Mechanisms: HTTP polling (GET /events?since=timestamp), long polling, message queue consumer poll loops (SQS, Kafka consumer.poll()). Pull is optimal when consumers process at their own rate, when consumer availability is unreliable, or when processing time is variable and backpressure is needed. In practice, modern systems often layer both: event-driven push notification (e.g., "new data available") that triggers a subsequent pull to fetch the actual data.

---

### 🟢 Simple Definition (Easy)

Push: the server calls you. Pull: you call the server. Push: a news alert notification appears on your phone the moment breaking news happens — server pushed it. Pull: you open the news app and refresh — you pulled the latest news. Push is faster and more immediate; Pull is simpler and more controllable.

---

### 🔵 Simple Definition (Elaborated)

GitHub webhooks: when you push code, GitHub (server) calls your CI server's URL (push notification → trigger build). Your CI doesn't need to poll GitHub every minute asking "any new commits?" — GitHub tells it instantly. Alternative: CI polls GitHub API every 60 seconds (pull). Push: 0-latency between commit and build trigger; Pull: up to 60-second lag. But Pull is simpler (no public URL needed for CI, no webhook configuration). CI/CD systems typically offer both: webhooks (push) for speed, polling (pull) for simplicity and reliability.

---

### 🔩 First Principles Explanation

**Push vs Pull in different system layers:**

```
LAYER 1: CLIENT-SERVER COMMUNICATION

  PUSH (WebSocket):
    Client → Server: "Connect" (WebSocket handshake)
    Server → Client: data pushed as it arrives
    
    Pros: Zero-latency delivery. No repeated HTTP requests. Stateful connection.
    Cons: Server must maintain connection state per client (memory: ~50KB/connection).
          100K connected clients → 5 GB RAM just for connections.
          If client disconnects: must reconnect + handle missed messages.
    Use: chat applications, live trading dashboards, collaborative editing (Google Docs).
  
  PUSH (Server-Sent Events / SSE):
    Simpler unidirectional version of WebSocket.
    Client → Server: GET /events (one HTTP request, connection stays open)
    Server → Client: events pushed as text/event-stream
    
    Pros: Simpler than WebSocket. HTTP/1.1 compatible. Automatic reconnect built-in.
    Cons: One-directional (server → client only). HTTP/1.1 limit: 6 concurrent SSE per domain.
    Use: live feeds (Twitter streaming, sports scores, live dashboards).
  
  PULL (HTTP Polling):
    Client → Server: GET /events?since={last_id} (repeated at interval)
    Server → Client: events since last_id (or empty if none)
    
    Pros: Simple. Works over standard HTTP. No persistent connection.
    Cons: Latency = polling interval (30-second poll → up to 30s lag).
          Wasted requests when no new data.
          N clients polling = N × polling_frequency requests/sec (load).
    Use: dashboards that update every 30 seconds, simple notifications.
    
  PULL (Long Polling):
    Client → Server: GET /events?since={last_id}
    Server: holds the request open if no new events (up to 30s).
    Server: responds immediately when new event arrives OR timeout.
    Client: immediately re-issues request after response.
    
    Pros: Near-real-time with lower load than short-interval polling.
    Cons: Still has reconnect overhead. Server: many open connections.
    Use: Baseline for chat (Slack, Discord pre-WebSocket). Legacy AJAX push.

LAYER 2: DATA PIPELINE (KAFKA EXAMPLE)

  KAFKA: PULL-BASED (consumers pull from brokers)
  
    Consumer.poll(100ms): consumer asks broker "any new messages?"
    Broker: returns messages if available, waits if empty.
    
    WHY PULL (not push) for Kafka:
    1. BACKPRESSURE: consumer controls its own consumption rate.
       If consumer is slow: it simply polls less frequently → no message loss.
       Push model: broker pushes at producer rate → overwhelms slow consumers.
    2. VARIABLE PROCESSING: consumer may take 1ms or 10 seconds per message.
       Push: broker must know consumer capacity → complex rate management.
       Pull: consumer decides when it's ready → inherently backpressure-safe.
    3. CONSUMER INDEPENDENCE: 10 consumer groups pulling independently.
       Each at their own rate. No coordination between consumers needed.
       
    KAFKA PULL PATTERN:
    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, String> record : records) {
            processRecord(record);  // takes variable time
        }
        consumer.commitSync();  // commit only after processing
    }
    
    BENEFIT: If processRecord() takes 5 seconds, no messages lost.
             Consumer simply processes at its own rate.
             Broker holds messages until consumer commits.

  RABBITMQ / ACTIVEMQ: PUSH-BASED
  
    Broker pushes messages to consumers via AMQP protocol.
    Consumer: acknowledges each message.
    prefetch_count: limits how many messages broker pushes before waiting for ACK.
    
    prefetch_count=1: one message at a time pushed. Fair round-robin. Slow.
    prefetch_count=10: 10 messages buffered per consumer. Better throughput.
    
    Risk without prefetch: broker pushes 1,000 messages to one fast consumer
    while other consumers are idle → uneven distribution.

LAYER 3: MOBILE PUSH NOTIFICATIONS

  PUSH (APNs/FCM):
    Server → APNs/FCM gateway → Device (push)
    Latency: 1-5 seconds
    Pros: Works when app is not running (OS-level delivery)
    Cons: Requires device token management. Message size limits (4KB FCM).
    Use: "You received a message", "Your order shipped"
    
  PULL (App polling in background):
    App: background fetch every 15-30 minutes.
    Pros: No external service dependency. Always consistent.
    Cons: Battery drain. 15-minute minimum interval (iOS Background App Refresh).
          App must be installed and have permission.
    Use: Email, content sync (not real-time notifications)

HYBRID PATTERN ("kick" + fetch):

  Problem: Push sends large payload → bandwidth waste (many clients, large data).
  Problem: Push sends stale data → client fetched different version than push contained.
  
  Solution: PUSH NOTIFICATION + PULL FETCH ("nudge + fetch")
  
  1. Server detects change: new comment on user's post.
  2. Server sends LIGHTWEIGHT push: {"type": "new_comment", "post_id": 123}
     (no actual data — just a notification that something changed)
  3. Client receives push → immediately pulls: GET /posts/123/comments?since=last
  4. Client gets fresh data directly from source
  
  Benefits:
  - Push payload tiny (no data staleness risk)
  - Pull gets current state (race conditions with push payload eliminated)
  - Works with push rate limiting (multiple events → one notification → one fetch)
  
  Used by: Google Drive sync, Slack, iMessage, GitHub notifications.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT push/pull distinction:
- Chat app built with polling: 1M users × poll every second = 1M HTTP req/sec for mostly empty responses
- Kafka with push model: slow consumers overwhelmed → consumer crashes → message loss

WITH correct push/pull selection:
→ Chat: WebSocket push — 1M persistent connections, near-zero overhead for idle users
→ Kafka: pull — slow consumers process at their own rate, no message loss
→ Mobile notifications: push via APNs/FCM — works even when app is closed

---

### 🧠 Mental Model / Analogy

> Push: a taxi dispatch system — HQ (server) calls available drivers (clients) when a ride appears. Drivers don't constantly call HQ asking "any rides?" — HQ pushes the ride to them instantly. vs. Pull: a job board — job seekers (clients) check the job board periodically ("any new jobs?"). The board doesn't call every job seeker when a new listing appears — seekers pull at their own pace.

"Taxi dispatch calling drivers" = push (server initiates, low latency)
"Each driver available and reachable" = push works when clients are always connected
"Job board: seekers check it themselves" = pull (client initiates at own pace)
"Job seeker can check daily or hourly" = pull rate is client-controlled
"Taxi HQ doesn't know if driver is available" = push can fail if client is offline

---

### ⚙️ How It Works (Mechanism)

**WebSocket push vs SSE vs polling comparison:**

```java
// 1. WebSocket Push (Spring Boot):
@ServerEndpoint("/ws/notifications")
public class NotificationWebSocket {
    
    private static Set<Session> sessions = ConcurrentHashMap.newKeySet();
    
    @OnOpen
    public void onOpen(Session session) {
        sessions.add(session);
    }
    
    @OnClose
    public void onClose(Session session) {
        sessions.remove(session);
    }
    
    // Push to all connected clients:
    public static void pushToAll(String message) {
        sessions.forEach(session -> {
            try {
                session.getBasicRemote().sendText(message);
            } catch (IOException e) {
                sessions.remove(session);
            }
        });
    }
}

// 2. SSE (Server-Sent Events) — simpler unidirectional push:
@GetMapping(value = "/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter streamEvents(@RequestParam Long userId) {
    SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
    
    // Register emitter for this user:
    emitterService.register(userId, emitter);
    
    // Send event to user when triggered:
    // emitter.send(SseEmitter.event().data("{\"type\":\"notification\"}"));
    
    return emitter;
}

// 3. Long Polling (fallback for clients behind restrictive firewalls):
@GetMapping("/poll/notifications")
public DeferredResult<List<Notification>> pollNotifications(
        @RequestParam Long since, 
        @RequestParam Long userId) {
    
    DeferredResult<List<Notification>> result = new DeferredResult<>(30_000L);  // 30s timeout
    
    List<Notification> pending = notificationService.getSince(userId, since);
    if (!pending.isEmpty()) {
        result.setResult(pending);  // Immediate response if data available
    } else {
        // Suspend request until new notification arrives or timeout:
        notificationService.registerWaiter(userId, result);
    }
    
    return result;
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Event occurs (new message, new post, etc.)
        │
        ▼
Push vs Pull Architecture ◄──── (you are here)
        │
        ├── PUSH → WebSocket, SSE, Webhook, APNs/FCM
        ├── PULL → Polling, Long Polling, Kafka Consumer Poll
        └── HYBRID → Push notification + Pull fetch ("nudge + fetch")
                │
                ▼
        News Feed Design, Notification System Design
```

---

### 💻 Code Example

**Hybrid push + pull (webhook notification → client pull fetch):**

```python
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- SERVER SIDE: push lightweight notification ---
def notify_user_of_new_message(user_webhook_url: str, conversation_id: str):
    """Push lightweight event to client webhook — no message content."""
    payload = {
        "event": "new_message",
        "conversation_id": conversation_id,  # client will fetch the actual message
        "timestamp": time.time()
    }
    try:
        requests.post(user_webhook_url, json=payload, timeout=5)
    except requests.Timeout:
        # Webhook delivery failed — queue for retry
        retry_queue.enqueue(user_webhook_url, payload)

# --- CLIENT SIDE: receive push, then pull actual data ---
@app.route("/webhook/receive", methods=["POST"])
def receive_webhook():
    event = request.json
    if event["event"] == "new_message":
        conversation_id = event["conversation_id"]
        
        # Pull actual message content (fresh from source):
        messages = requests.get(
            f"https://api.example.com/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"since": get_last_seen_id(conversation_id)}
        ).json()
        
        display_new_messages(messages)
    
    return jsonify({"status": "ok"})
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Push is always faster than pull | Push is lower latency for delivering the notification, but the actual data is often fetched via pull after the push notification. The hybrid "nudge + fetch" pattern means total latency = push notification latency + subsequent pull latency. For large data payloads, push can actually be slower (push must deliver full payload; nudge + pull can use cached/compressed delivery) |
| WebSocket is the only way to push to clients | WebSocket is one option. SSE (Server-Sent Events) is simpler for unidirectional push. Long polling works without WebSocket. Push notifications (APNs/FCM) work even when the app is closed. HTTP/2 server push can pre-emptively send resources. The choice depends on: bidirectional need, offline delivery, browser/platform support |
| Kafka is a push-based system | Kafka consumers actively poll the broker — it is pull-based. This is fundamental to Kafka's design: it enables backpressure (consumers control their rate), replayability (consumers can re-read old messages), and consumer independence. Many people confuse Kafka with push-based systems because producers push messages to the broker, but the broker-to-consumer direction is always pull |
| Pull requires polling (constant requests) | Long polling is a pull mechanism that avoids constant requests: the client sends one request, the server holds it until data is available (or timeout), then the client re-requests. This provides near-real-time pull with much lower load than short-interval polling |

---

### 🔥 Pitfalls in Production

**Push-based system overwhelms consumers with no backpressure:**

```
PROBLEM: RabbitMQ push overwhelms slow consumer

  Config: RabbitMQ consumer, prefetch_count = unlimited (default in some clients)
  Producer: 10,000 messages/second
  Consumer: processes 100 messages/second (complex business logic)
  
  Day 1:
    Queue: 10,000 msg/sec in, 100 msg/sec out → +9,900 msg/sec backlog
    After 24 hours: 9,900 × 86,400 = 855M messages queued.
    RabbitMQ: runs out of memory → crashes.
    
  Day 2:
    Recovery: restart RabbitMQ.
    BUT: 855M message backlog → consumer takes 855M / 100 = 99 days to catch up.
    
  ROOT CAUSE: No backpressure. Producer faster than consumer. Push model without flow control.
  
FIX 1: prefetch_count = 1 (one message at a time)

  Consumer: processes one message, sends ACK, receives next.
  RabbitMQ: never pushes more than 1 message per consumer.
  Risk: low throughput (serial processing).
  
FIX 2: prefetch_count = 10 (bounded prefetch)

  Consumer: has at most 10 unacked messages in flight.
  Better throughput than prefetch=1; still bounded memory.
  
FIX 3: Switch to PULL model (SQS or Kafka)

  SQS consumer.receive(maxMessages=10): 
    Receives 10 messages, processes, sends deletes, receives next 10.
    Natural backpressure: consumer only gets what it asks for.
    Queue backlog grows if consumer is slow — no consumer OOM.
    
  LESSON: In distributed systems, backpressure is critical.
          Pull models provide implicit backpressure.
          Push models require explicit flow control (prefetch, rate limiting).
```

---

### 🔗 Related Keywords

- `Fan-Out on Write vs Read` — fan-out on write = push model; fan-out on read = pull model
- `Polling vs Webhooks` — polling = pull; webhooks = push (in HTTP API context)
- `Notification System Design` — push notifications to mobile/web clients
- `News Feed Design` — push model pre-computes feed; pull model computes at read time

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Push: server sends proactively (low lat); │
│              │ Pull: client requests at own pace         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Push: real-time, connected clients (chat);│
│              │ Pull: variable processing, backpressure   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Push without flow control (overwhelms);   │
│              │ Pull at short intervals (wasteful polling) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Taxi dispatch (push) vs job board (pull) │
│              │  — choose who initiates the interaction." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Polling vs Webhooks → WebSocket           │
│              │ → Notification System Design              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're building a collaborative document editor (like Google Docs). Multiple users edit the same document simultaneously. Should you use push (WebSocket) or pull (polling) to synchronise edits between users? What specific problems arise if you use polling at 500ms intervals with 10 simultaneous editors? What problems arise with WebSocket push if the server has 100,000 simultaneously active documents each with an average of 3 editors?

**Q2.** A third-party payment processor sends events to your system when payments are completed (e.g., Stripe webhooks). Your event handler processes payment events and updates orders in your database. Describe: (a) the full flow of a webhook push delivery with retry logic; (b) what happens if your webhook endpoint is down for 30 minutes — how many webhook retries does Stripe make and what is the risk? (c) design a "catch-up" pull mechanism that reconciles any missed webhook events, including exactly when to run it and what API to call.
