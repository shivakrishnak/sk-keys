---
id: NET-042
title: "Long Polling vs WebSocket vs SSE"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-030, NET-040
used_by: NET-051, NET-056
related: NET-030, NET-040, NET-041
tags:
  - networking
  - realtime
  - long-polling
  - websocket
  - sse
  - server-sent-events
  - push
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/net/long-polling-vs-websocket-vs-sse/
---

**⚡ TL;DR** - Three mechanisms deliver real-time data to
clients. Long polling: client holds an HTTP request open
until the server has data; works everywhere, high overhead.
SSE (Server-Sent Events): server pushes events over a
persistent HTTP response; simple, one-directional, native
browser reconnect. WebSocket: full-duplex persistent
connection; lowest latency, supports bidirectional flow.
Choose by asking: does the client need to send data back?
Yes → WebSocket. No → SSE. Legacy system or CDN required
→ Long polling.

| #042 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | HTTP and HTTPS Basics (NET-030), WebSocket Protocol (NET-040) | |
| **Used by:** | N+1 Connection Problem, HTTP Connection Management | |
| **Related:** | HTTP and HTTPS Basics, WebSocket Protocol, gRPC | |

---

### 🔥 The Problem All Three Solve

HTTP is fundamentally client-initiated: the client sends
a request and gets a response. But modern applications
need server-initiated updates: a chat message arrives,
a stock price changes, a build completes. Traditional
polling sends a request every second - 59 of 60 requests
return "nothing new." These three techniques let the
server push data to the client when it's ready.

---

### ⚙️ Technique 1: Short Polling (the anti-pattern)

```python
# BAD: short polling - request every second
async function pollForUpdates():
    while True:
        response = await fetch('/api/messages/new')
        if response.messages:
            displayMessages(response.messages)
        await sleep(1000)  # wait 1 second, try again

# Problems:
# - 60 requests/minute regardless of activity
# - Each request: TCP (or TLS) overhead + HTTP headers
# - 59/60 return empty: 98% wasted
# - Latency: up to 1 second before new data shows
# - At 10K users: 10,000 req/second constant load on server
```

---

### ⚙️ Technique 2: Long Polling

```python
# How it works: client waits, server holds until data
# Server implementation:
async def long_poll_endpoint(request):
    client_id = request.args['client_id']
    last_seen = int(request.args.get('since', 0))
    timeout = 30  # hold for up to 30 seconds

    deadline = time.time() + timeout
    while time.time() < deadline:
        messages = get_messages_since(client_id, last_seen)
        if messages:
            return json_response({'messages': messages})
        await asyncio.sleep(0.1)  # check every 100ms

    # No data in 30 seconds, return empty
    return json_response({'messages': [], 'since': last_seen})

# Client implementation:
async function longPoll():
    while True:
        try:
            response = await fetch(
                '/api/messages?client_id=' + clientId +
                '&since=' + lastSeen,
                {signal: AbortSignal.timeout(35000)}  # 35s timeout
            )
            data = await response.json()
            if data.messages.length > 0:
                displayMessages(data.messages)
                lastSeen = data.messages.last().id
        catch (e):
            await sleep(1000)  # brief pause on error
        # Immediately re-request after response received
```

**Characteristics:**
```
✓ Works everywhere: CDNs cache it, proxies support it
✓ HTTP/1.1 compatible (no protocol upgrade needed)
✓ Easy to implement on any HTTP server
✗ Each response → new connection (overhead)
✗ Server holds many open connections (memory)
✗ Up to polling interval latency for new messages
✗ Not truly real-time (200ms+ latency typical)
```

---

### ⚙️ Technique 3: Server-Sent Events (SSE)

```python
# Server implementation (Python / Flask):
from flask import Response, stream_with_context
import time, json

def event_stream(channel):
    """Yield SSE events as server gets data."""
    last_event_id = 0
    while True:
        events = get_events_since(channel, last_event_id)
        for event in events:
            last_event_id = event.id
            # SSE wire format:
            yield f"id: {event.id}\n"
            yield f"event: {event.type}\n"
            yield f"data: {json.dumps(event.data)}\n"
            yield "\n"  # blank line = end of event
        # Send keep-alive comment every 15s
        yield ": keepalive\n\n"
        time.sleep(0.1)

@app.route('/events')
def sse_endpoint():
    channel = request.args.get('channel', 'default')
    return Response(
        stream_with_context(event_stream(channel)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # disable nginx buffering
        }
    )
```

```javascript
// Browser: built-in EventSource API
const source = new EventSource('/events?channel=prices');

// Reconnect is AUTOMATIC - browser handles it natively
// Sends Last-Event-ID header on reconnect
// Exponential backoff built-in (3s default, customizable)

source.addEventListener('price_update', (event) => {
    const data = JSON.parse(event.data);
    updatePrice(data.symbol, data.price);
});

source.addEventListener('error', (event) => {
    if (event.eventPhase === EventSource.CLOSED) {
        console.log('Connection closed, browser will reconnect');
    }
});

// Close when done
source.close();
```

**SSE wire format:**
```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

id: 1001\n
event: price_update\n
data: {"symbol":"AAPL","price":189.42}\n
\n
id: 1002\n
event: price_update\n
data: {"symbol":"GOOG","price":175.10}\n
\n
: keepalive\n
\n
```

**Characteristics:**
```
✓ Native browser support (EventSource API)
✓ Auto-reconnect with Last-Event-ID replay
✓ Text-based (easy to debug with curl)
✓ Works over HTTP/2 (multiple SSE streams, one connection)
✓ Firewalls don't block it (standard HTTP)
✓ CDN-compatible (for cacheable events)
✗ Server → client only (no client → server)
✗ Text only (no binary, but base64 works)
✗ IE11/EdgeHTML not supported (but Edge Chromium is fine)
```

---

### ⚙️ Technique 4: WebSocket (recap in comparison context)

```javascript
// WebSocket for bidirectional real-time
const ws = new WebSocket('wss://api.example.com/ws');

ws.onopen = () => {
    // Client CAN also send messages
    ws.send(JSON.stringify({type: 'subscribe', channel: 'prices'}));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'price_update') updatePrice(data);
};
```

**Characteristics:**
```
✓ Full-duplex: client and server both initiate
✓ Lowest latency (no HTTP overhead per message)
✓ Binary support (ArrayBuffer)
✓ Ping/pong heartbeat at protocol level
✗ Requires Upgrade handshake (stateful)
✗ Manual reconnect logic required
✗ Some enterprise proxies/firewalls block WebSocket
✗ Not cacheable by CDN
✗ Not compatible with HTTP/2 multiplexing natively
     (ws:// and wss:// are independent protocols)
```

---

### ⚙️ Decision Matrix

```
┌──────────────────────────────────────────────────────────┐
│  Real-time Mechanism Comparison                          │
├───────────────────────┬────────────┬──────────┬──────────┤
│  Factor               │ Long Poll  │  SSE     │ WebSocket│
├───────────────────────┼────────────┼──────────┼──────────┤
│  Protocol             │ HTTP/1.1   │ HTTP/1.1+│ WS/WSS   │
│  Direction            │ S→C        │ S→C      │ S↔C      │
│  Latency              │ Medium     │ Low      │ Lowest   │
│  Reconnect            │ Manual     │ Auto     │ Manual   │
│  Overhead per msg     │ High       │ Low      │ Minimal  │
│  Binary support       │ Yes (body) │ No       │ Yes      │
│  CDN compatible       │ Yes        │ Yes      │ No       │
│  Firewall friendly    │ Yes        │ Yes      │ Maybe    │
│  Browser support      │ All        │ All mod. │ All mod. │
│  HTTP/2 multiplexed   │ Yes        │ Yes      │ No       │
│  Server memory/conn   │ High       │ Medium   │ Medium   │
└───────────────────────┴────────────┴──────────┴──────────┘
```

---

### ⚙️ Wrong vs Right: SSE Behind nginx Without Buffering Disabled

```nginx
# BAD: default nginx config buffers SSE responses
# Events are batched in nginx buffer, user sees them all at once
# after nginx's buffer fills or timeout expires
server {
    location /events {
        proxy_pass http://backend;
        # Missing: proxy_buffering off!
    }
}

# GOOD: disable nginx buffering for SSE
server {
    location /events {
        proxy_pass http://backend;
        proxy_buffering off;         # critical for SSE
        proxy_cache off;             # don't cache event stream
        proxy_read_timeout 3600;     # hold open for 1 hour
        chunked_transfer_encoding on;
        # Or use X-Accel-Buffering: no response header from backend
    }
}
```

```python
# BAD: SSE response without disabling framework buffering
@app.route('/events')
def events():
    def generate():
        while True:
            yield f"data: {get_event()}\n\n"
    return Response(generate(), mimetype='text/event-stream')
# Flask's response buffering may hold chunks → bad UX

# GOOD: explicit headers to prevent all buffering layers
@app.route('/events')
def events():
    def generate():
        while True:
            yield f"data: {get_event()}\n\n"
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # tells nginx not to buffer
            'Transfer-Encoding': 'chunked',
        }
    )
```

---

### ⚙️ Production Pattern: Hybrid Approach (SSE + REST)

```python
# Most real-world systems use SSE for push, REST for actions
# This avoids WebSocket complexity while covering 90% of use cases

# Architecture:
# Client → POST /api/order      (REST, creates order)
# Server → SSE /events/orders   (streams order status updates)
# Client → GET /api/orders/123  (REST, one-time fetch)

# This is what GitHub uses for pull request live updates,
# what Linear uses for ticket updates, what Notion uses
# for collaborative editing (with OT on top).

# SSE with authentication:
@app.route('/events')
def events():
    # Auth via query param token (cookies auto-sent on EventSource)
    token = request.args.get('token') or request.cookies.get('session')
    user = verify_token(token)
    if not user:
        return Response('Unauthorized', status=401)

    def stream():
        # Subscribe to Redis Pub/Sub for this user's events
        pubsub = redis.pubsub()
        pubsub.subscribe(f"user:{user.id}:events")
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield f"data: {message['data'].decode()}\n\n"

    return Response(stream(), mimetype='text/event-stream')
```

---

### 📐 Scale Considerations

```
Server memory per persistent connection:
  Long polling: ~32KB (HTTP buffers) per open request
  SSE: ~8-16KB (streaming HTTP response) per connection
  WebSocket: ~40-80KB per connection

10,000 concurrent users (live dashboard):
  Long polling: 10K open HTTP requests × 32KB = 320MB
                + 10K × reconnect overhead every 30s
                = ~333 reconnects/second = non-trivial
  SSE: 10K connections × 16KB = 160MB (lower than WS)
  WebSocket: 10K connections × 64KB = 640MB

Horizontal scaling (all three):
  Need shared event bus: Redis Pub/Sub, Kafka, or NATS
  Each server subscribes to relevant topics
  Server publishes event → all servers → their clients
  
  Kubernetes: sticky sessions required for SSE/WS
  (connection must stay on same pod)
  K8s ingress: sessionAffinity: ClientIP or cookie-based
```

---

### 🧭 Decision Guide

```
1. Does the client need to send data to server in real-time?
   YES → WebSocket
   NO  → SSE (simpler, auto-reconnect, CDN-friendly)

2. Must it work behind enterprise firewalls?
   YES → Long polling or SSE (both plain HTTP)
   NO  → WebSocket OK

3. Do you need CDN caching for events?
   YES → Long polling (CDN can cache HTTP responses)
   NO  → Any approach

4. Are you on a legacy system with older load balancers?
   YES → Long polling (no state, works with any proxy)
   NO  → SSE or WebSocket

5. Is this a notification feed (new comments, PR status)?
   → SSE: simplest correct solution

6. Is this a chat, game, collaborative editor?
   → WebSocket: bidirectional required

Common mistakes:
  - Using WebSocket when SSE is sufficient → extra complexity
  - Using short polling when long polling would work
  - Not setting proxy_read_timeout for SSE/WebSocket
  - Forgetting reconnect logic for WebSocket
  - Forgetting Last-Event-ID handling for SSE recovery

Interview answer:
  "SSE is the simplest for pure server push (notifications,
  feeds): native browser reconnect, standard HTTP, CDN
  friendly. WebSocket is needed when the client must also
  push to the server in real-time (chat, gaming). Long
  polling is a fallback for environments that block
  WebSocket or don't support SSE."
```