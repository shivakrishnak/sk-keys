---
layout: default
title: "Long Polling"
parent: "HTTP & APIs"
nav_order: 229
permalink: /http-apis/long-polling/
number: "0229"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, REST, HTTP Timeout
used_by: Legacy Real-time Systems, Chat Applications, Push Notifications
related: WebSocket, Server-Sent Events, Short Polling
tags:
  - api
  - realtime
  - polling
  - push
  - intermediate
---

# 229 — Long Polling

⚡ TL;DR — Long polling simulates server push by having the client send an HTTP request that the server holds open until an event occurs or a timeout is reached; when the server responds, the client immediately sends another request — creating a near-real-time push effect using standard HTTP.

| #229 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, REST, HTTP Timeout | |
| **Used by:** | Legacy Real-time Systems, Chat Applications, Push Notifications | |
| **Related:** | WebSocket, Server-Sent Events, Short Polling | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You want to push a notification to a user the moment it occurs. But HTTP is
request/response — the server can't send data unless the client asked for it first.
Short polling (asking every 2 seconds) wastes bandwidth and server connections.
WebSocket and SSE exist, but older browser environments don't support them, and
some corporate firewalls block WebSocket upgrades. You need real-time-ish behavior
with plain old HTTP.

**THE INVENTION MOMENT:**
Long polling was a widely used technique in the pre-WebSocket era (2000–2013).
The insight: instead of making a request, getting an immediate empty response,
and waiting 2 seconds to try again — make a request and have the server hold it
open until there's actual data. The server waits (up to a timeout) before
responding. The moment data is available, it responds. The client immediately
fires another request. Result: near-real-time delivery with standard HTTP,
no new protocol needed. Gmail, Facebook Chat, and early Comet apps all used this.

---

### 📘 Textbook Definition

**Long Polling** is a technique where a client makes an HTTP request to a server;
if no data is immediately available, the server holds the connection open until
data becomes available or a timeout is reached, then responds. The client
immediately re-requests upon receiving a response. This cycle enables the client
to receive push-like notifications using standard HTTP — no persistent connection
or special protocol required beyond a timeout management strategy. Compared to
short polling (immediate responses whether data exists or not), long polling
dramatically reduces the number of empty-response round trips while maintaining
compatibility with all HTTP infrastructure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Long polling tricks HTTP into push: client asks "any messages?", server waits silently until there ARE messages (or timeout), then responds — client immediately asks again.

**One analogy:**

> Short polling is ordering food at a busy restaurant by asking the waiter
> "is my order ready?" every 30 seconds. Long polling is the waiter saying:
> "instead of you asking me every 30 seconds, just wait here — I'll bring your
> food the moment it's ready." Less interruptions, faster delivery, same kitchen.

**One insight:**
Long polling's key insight is that "holding a request open" is actually cheaper
than "repeatedly sending requests." A held request uses one persistent TCP connection
and one server-side async handle. Repeated polling uses one TCP connection too,
but also HTTP overhead (headers, connection setup sometimes) per cycle. Long polling
wins on latency (event delivered immediately vs up to polling-interval delay) and
on "useful request ratio" (most responses have data vs most responses are empty).

---

### 🔩 First Principles Explanation

**SHORT POLLING vs LONG POLLING:**

```
SHORT POLLING (interval: 2s):
  t=0:  Client → GET /messages?since=0 → Server: [] (empty, 200ms RTT)
  t=2:  Client → GET /messages?since=0 → Server: [] (empty)
  t=4:  Client → GET /messages?since=0 → Server: [] (empty)
  t=5.1: Server has a message available
  t=6:  Client → GET /messages?since=0 → Server: [{message}] ← 0.9s LATE!
  Total: 4 round trips, 3 useless, up to 2s latency

LONG POLLING (timeout: 30s):
  t=0:  Client → GET /messages?since=0&timeout=30
        Server: HOLDS open (checking for messages)
  t=5.1: Message arrives at server
        Server → [{message}] (immediate response — 0ms latency!)
  t=5.2: Client immediately → GET /messages?since=5.1&timeout=30
        Server: HOLDS open again
  Total: 1 useful round trip, ~0ms latency
```

**SERVER-SIDE IMPLEMENTATION APPROACHES:**

```
APPROACH 1 — Thread-per-connection (simple, bad at scale):
  Block the thread waiting for events (using synchronized wait/notify)
  Problem: 10,000 clients = 10,000 threads blocked → thread starvation

APPROACH 2 — Async servlet (Java EE approach):
  Register an AsyncContext; release the servlet thread
  When event occurs: get AsyncContext, write response, complete()
  Scales to 10,000 clients with a small thread pool

APPROACH 3 — Reactive (Spring WebFlux):
  Return Mono<ResponseEntity> that completes when event arrives
  No thread held; Reactor manages the async wait
```

**THE TRADE-OFFS:**

- Gain: real-time-ish behavior using standard HTTP — works everywhere.
- Cost: server must hold async handles per connected client; more complex than REST.
- Gain: works through HTTP proxies and old firewalls that block WebSocket.
- Cost: each "cycle" still has HTTP header overhead (~500 bytes) vs WebSocket (~2 bytes).
- Gain: simple client implementation: just a loop with an HTTP request inside.
- Cost: at 10,000 clients, 10,000 hanging requests put pressure on server's async handles.

---

### 🧪 Thought Experiment

**SETUP:**
A notification service sends ~5 notifications per user per hour.
100,000 active users. Short polling interval: 10 seconds.

**SHORT POLLING:**

```
Requests/second = 100,000 / 10 = 10,000 req/s
Empty responses: (3600 - 5) / 3600 ≈ 99.9% empty
Useful requests: ~500 total/minute = ~8/second
Wasted requests: ~9,992/second
Server load: 10,000 req/s regardless of notification rate
```

**LONG POLLING (30-second timeout):**

```
Max open connections: 100,000 (one per user)
"Wasted" request cycles: only when timeout fires with no data
  = 100,000 clients × (3600/30) cycles/hour × empty rate
  ≈ 100,000 × 120 × 99.9% ≈ ~12,000 empty cycles/hour ≈ ~3.3 empty cycles/s
Useful responses: 500 total notifications/minute ≈ 8/second
Server load: ~11 HTTP completions/second (vs 10,000/second for polling)
```

**THE INSIGHT:**
Long polling reduces server HTTP processing load by ~99% vs short polling
for this low-notification pattern. The cost: 100,000 persistent async handles.
At high notification rates (10/second per user), long polling loses its efficiency
advantage over SSE or WebSocket.

---

### 🧠 Mental Model / Analogy

> Long polling is like a held-order model at a phone operator.
> Customer (client) calls and says "do you have any messages for me?"
> Operator (server) says "let me check... still looking... still looking...
> oh — yes! Here's your message." Customer hangs up, immediately calls back.
> Compare to a customer calling every 10 seconds and hanging up if there's nothing.
> Long polling: one call that eventually delivers. Short polling: many calls, mostly wasted.

**Where this breaks down:** If 10,000 customers call simultaneously and no messages
arrive, the operator holds 10,000 simultaneous calls open for up to 30 seconds.
That's a lot of concurrent connections to manage — long polling trades polling
overhead for connection management complexity.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of repeatedly asking "is there a message?" every few seconds, long polling
asks once and the server holds the line open, saying "I'll tell you the moment
something arrives." When something arrives, you get it immediately. Then you ask again.

**Level 2 — How to use it (junior developer):**
Client: send HTTP GET request with a long timeout (30+ seconds). In the response:
if data is present, process it and immediately request again. If timeout (204 or empty),
immediately request again. Server: don't respond until data is available or timeout.
Use an event/notification system — when data arrives, release all waiting clients.
Spring: use `DeferredResult<ResponseEntity<T>>` — return it immediately, complete it
when data arrives.

**Level 3 — How it works (mid-level engineer):**
Server-side: on receiving the long-poll request, check for pending events. If found,
respond immediately. If not, register a callback: `DeferredResult<>` timeout + result.
When an event arrives (from another thread, message queue, etc.), complete the
DeferredResult with the result. If the timeout fires with no event, return empty
(204 or empty array) — client will re-request. The critical detail: client must
track what events it has seen (using a cursor, timestamp, or event ID) and pass
it in each request. Server returns only events AFTER that cursor. Without this,
the client could receive duplicate events or miss events published during the
instant the connection is re-established.

**Level 4 — Why it was designed this way (senior/staff):**
Long polling emerged before server-sent events (SSE) were standardized and before
WebSocket was universally supported (WebSocket RFC is 2011). It was the pragmatic
adaptation of HTTP request/response to push semantics without requiring any new
infrastructure. The "Comet" pattern (umbrella term for long polling and related
techniques) was widely used 2006–2013. Long polling's legacy is visible: MQTT brokers,
Firebase's early HTTPS transport, and SockJS (WebSocket fallback library) all
implemented long polling as a compatibility fallback. Today, long polling should not
be chosen for new systems — SSE or WebSocket are better. Long polling remains in
mission-critical legacy systems where HTTP compatibility constraints prevent upgrading
and in environments where corporate proxies block WebSocket and SSE connections.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────────┐
│              LONG POLLING CYCLE                              │
├──────────────────────────────────────────────────────────────┤
│  Client:  GET /notifications?since=1000&timeout=30          │
│           (last event ID = 1000, wait up to 30 seconds)     │
│                          ↓                                   │
│  Server:  Check for events > 1000. None found.             │
│           Register DeferredResult, timeout=30s              │
│           Release request-handling thread                    │
│                          ↓                                   │
│  [15 seconds pass, no events]                               │
│                          ↓                                   │
│  Event arrives: eventId=1001, userId=42                     │
│  Server: find DeferredResult for userId 42                  │
│           setResult([{id:1001, message:"Hello"}])           │
│           DeferredResult completes → response sent          │
│                          ↓                                   │
│  Client: receives: [{id:1001, ...}]                         │
│          immediately sends: GET /notifications?since=1001   │
│          (next cycle, using new since=1001 cursor)          │
└──────────────────────────────────────────────────────────────┘

TIMEOUT PATH:
  Server: DeferredResult times out after 30s, no events
  Server: setResult([]) (empty response or 204)
  Client: receives empty → immediately re-requests with same cursor
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
User navigates to app → JS starts long poll loop:

function longPoll(cursor) {
    fetch(`/api/events?since=${cursor}&timeout=30000`)
        .then(resp => resp.json())
        .then(events => {
            events.forEach(e => { processEvent(e); cursor = e.id; });
            longPoll(cursor); // immediately re-request
        })
        .catch(err => {
            // Network error: retry with backoff
            setTimeout(() => longPoll(cursor), 1000);
        });
}
longPoll(lastKnownEventId);
```

Server-side: DeferredResult per user, completed when event or timeout.
At scale: event notification via Redis Pub/Sub or application event bus.

````

---

### 💻 Code Example

```java
// Spring MVC — DeferredResult-based long polling
@RestController
public class NotificationController {

    // Map of userId → pending DeferredResult (long poll handle)
    private final ConcurrentHashMap<String, DeferredResult<List<Notification>>>
        pendingPolls = new ConcurrentHashMap<>();

    @GetMapping("/api/notifications")
    public DeferredResult<List<Notification>> poll(
            @RequestParam String userId,
            @RequestParam long since,
            @RequestParam(defaultValue = "30000") long timeout) {

        // Create deferred result with timeout
        DeferredResult<List<Notification>> result =
            new DeferredResult<>(timeout, Collections.emptyList());

        // Check for existing events immediately
        List<Notification> existing = notificationService.getSince(userId, since);
        if (!existing.isEmpty()) {
            result.setResult(existing);
            return result;
        }

        // No events yet — register for future delivery
        pendingPolls.put(userId, result);
        result.onCompletion(() -> pendingPolls.remove(userId));
        result.onTimeout(() -> pendingPolls.remove(userId));
        return result;
    }

    // Called when a new notification is available
    public void notifyUser(String userId, Notification notification) {
        DeferredResult<List<Notification>> pending = pendingPolls.get(userId);
        if (pending != null && !pending.isSetOrExpired()) {
            pending.setResult(List.of(notification));
        } else {
            // No pending poll — store for next poll request
            notificationService.store(userId, notification);
        }
    }
}
````

```javascript
// Client JavaScript — long poll loop
class LongPollClient {
  constructor(userId) {
    this.userId = userId;
    this.cursor = 0;
    this.running = false;
  }

  start() {
    this.running = true;
    this.poll();
  }

  stop() {
    this.running = false;
  }

  async poll() {
    if (!this.running) return;

    try {
      const url =
        `/api/notifications?userId=${this.userId}` +
        `&since=${this.cursor}&timeout=30000`;

      const response = await fetch(url, { signal: AbortSignal.timeout(35000) });
      const notifications = await response.json();

      if (notifications.length > 0) {
        notifications.forEach((n) => {
          this.onNotification(n);
          this.cursor = Math.max(this.cursor, n.id);
        });
      }

      // Immediately poll again (no delay on successful response)
      this.poll();
    } catch (error) {
      if (this.running) {
        // Retry with exponential backoff on error
        setTimeout(() => this.poll(), Math.min(30000, (this.retryDelay *= 2)));
      }
    }
  }

  onNotification(notification) {
    /* override in subclass */
  }
}
```

---

### ⚖️ Comparison Table

| Technique         | Latency        | Server Load     | Complexity | Browser Support | Use Today |
| ----------------- | -------------- | --------------- | ---------- | --------------- | --------- |
| **Short Polling** | Up to interval | High (wasteful) | Low        | Universal       | Rarely    |
| **Long Polling**  | ~0ms           | Medium          | Medium     | Universal       | Legacy    |
| **SSE**           | ~0ms           | Low             | Low        | All modern      | ✓         |
| **WebSocket**     | ~0ms           | Low-medium      | Medium     | All modern      | ✓         |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                   |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Long polling and short polling are the same      | Short polling returns immediately whether data exists or not; long polling holds the connection until data or timeout                                     |
| Long polling holds a thread per client           | Modern implementations use async servlets (DeferredResult, AsyncContext) that don't block threads; one thread pool serves thousands                       |
| Long polling is always replaced by WebSocket now | Legacy enterprise and corporate proxy environments still use long polling where WebSocket is blocked                                                      |
| Long polling is free of message loss risk        | The gap between receiving a response and sending the next request has a window where events can be missed; must use cursor/since parameter to handle this |

---

### 🚨 Failure Modes & Diagnosis

**Message Loss in the Re-connection Window**

Symptom:
Occasional notifications are missed. No error in logs. Reproducible under load.

Root Cause:
Event arrives at server during the brief window between a long-poll response
being sent and the client's next poll request arriving. Without a cursor,
the new poll misses this event.

Diagnostic Command / Tool:

```
# Trace event lifecycle:
GET /api/events?since=100  → returns [{id:101, ...}]
Event 102 fires AT SERVER while client processes 101 response
Client sends: GET /api/events?since=101 → event 102 is in "pending"? Or missed?

# Fix: server must buffer events for a window (1–5 minutes)
# and return all events since the cursor on each poll
```

Fix:
Buffer events server-side. On each poll, return ALL events since the `cursor`.
Client always advances cursor to the latest received event ID.

Prevention:
Test with a producer that fires events at high frequency during the re-connection
window. Assert no events are missed over 1000 cycles.

---

### 🔗 Related Keywords

- `WebSocket` — the modern replacement for long polling for bidirectional real-time
- `Server-Sent Events (SSE)` — the modern replacement for long polling for server→client push
- `Short Polling` — simpler but less efficient predecessor to long polling
- `DeferredResult` — Spring's mechanism for non-blocking long poll server implementation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ HTTP held open until data or timeout:    │
│              │ simulates push with plain HTTP            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Real-time push needed where WebSocket/SSE │
│ SOLVES       │ blocked; old browser/proxy compatibility  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Holding request open + immediate re-      │
│              │ request on response = near-zero latency   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Legacy integration; proxy blocks WS/SSE;  │
│              │ fallback mode only                        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Building new systems — use SSE or WS      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wait for data before responding"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SSE → WebSocket → DeferredResult          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A mobile app backend supports 500,000 concurrent long polls (users waiting for push notifications). The average hold duration is 28 seconds before either a notification fires or the 30-second timeout. Design the server infrastructure (threading model, connection management, event delivery pipeline, and database impact) that handles this load with < 2GB RAM per process and < 5% CPU idle overhead.
