---
id: NET-040
title: "WebSocket Protocol"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-030
used_by: NET-041, NET-048
related: NET-030, NET-038, NET-041
tags:
  - networking
  - websocket
  - realtime
  - bidirectional
  - http-upgrade
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/net/websocket-protocol/
---

**⚡ TL;DR** - WebSocket is a persistent, full-duplex
communication channel over a single TCP connection. It
starts as an HTTP request (the Upgrade handshake), then
promotes the connection to a binary protocol where either
side can send messages at any time with 2-byte overhead.
Use it for real-time features: live dashboards, chat,
collaborative editing, trading feeds, game state. The
common mistake: using WebSocket for request-response APIs
that don't need real-time push.

| #040 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | HTTP and HTTPS Basics (NET-030) | |
| **Used by:** | Long Polling, WebSocket, and SSE, gRPC and Protocol Buffers | |
| **Related:** | HTTP and HTTPS Basics, HTTP/2 Multiplexing, Long Polling / WebSocket / SSE | |

---

### 🔥 The Problem WebSocket Solves

A stock trading dashboard needs live price updates. With
HTTP polling, the client requests `/prices` every second:
60 requests/minute, each with HTTP headers (~800 bytes),
each requiring a TCP round-trip to check if data changed.
If nothing changed: 60 wasted round-trips per minute per
user. At 10,000 users: 600,000 wasted requests/minute.
With WebSocket, one connection per user, server pushes
only when prices change. A price update is sent in one
frame with 2-6 bytes of framing overhead.

---

### 🧠 Intuition: HTTP Upgrade to Full Duplex

```
HTTP: request → response (half-duplex, client-initiated)
WebSocket: persistent pipe, either side sends any time (full-duplex)

Lifecycle:
  1. HTTP request with Upgrade header (TCP port 80 or 443)
  2. Server responds 101 Switching Protocols
  3. Connection "upgraded": no more HTTP on this socket
  4. WebSocket frames flow in both directions
  5. Either side sends Close frame → connection ends
```

---

### ⚙️ The WebSocket Handshake

```
Client sends HTTP request:
  GET /ws/prices HTTP/1.1
  Host: api.example.com
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
  Sec-WebSocket-Version: 13

Server responds:
  HTTP/1.1 101 Switching Protocols
  Upgrade: websocket
  Connection: Upgrade
  Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=

The Accept header = base64(SHA-1(key + magic_guid))
This is not real authentication - it just proves the
server understood the WebSocket upgrade request.

After the 101: no more HTTP. Binary WebSocket frames only.
```

---

### ⚙️ WebSocket Frame Format

```
WebSocket frame (minimum 2 bytes header):

Byte 0: FIN(1) RSV(3) Opcode(4)
         │         │        └─ 0x0=continuation, 0x1=text,
         │         │           0x2=binary, 0x8=close,
         │         │           0x9=ping, 0xA=pong
         │         └─ Reserved (must be 0 unless extension)
         └─ 1=final fragment of message
         
Byte 1: MASK(1) Payload-Length(7)
         │              └─ 0-125 = actual length
         │                 126 = extended 2-byte length
         │                 127 = extended 8-byte length
         └─ 1=client→server (always masked), 0=server→client

Client→server: always masked (4-byte random key XOR'd with payload)
  Masking prevents malicious scripts from exploiting
  transparent HTTP proxies that cache data
  
Server→client: NOT masked

Total overhead:
  Small message (< 126 bytes): 2-6 bytes
  Large message (> 64KB): 10-14 bytes
  vs HTTP/1.1: 600-1200 bytes headers per request
```

---

### ⚙️ Server-Side WebSocket Implementation

```python
# Python WebSocket server with websockets library
import asyncio
import websockets
import json

CONNECTED_CLIENTS = set()

async def price_feed(websocket, path):
    CONNECTED_CLIENTS.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        # Keep connection alive, handle client messages
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "subscribe":
                symbol = data["symbol"]
                # Register for price updates for this symbol
                await subscribe_to_symbol(websocket, symbol)
    except websockets.exceptions.ConnectionClosedOK:
        pass  # clean close
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection error: {e}")
    finally:
        CONNECTED_CLIENTS.discard(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

async def broadcast_price_update(symbol, price):
    """Push price update to all subscribers."""
    message = json.dumps({
        "type": "price_update",
        "symbol": symbol,
        "price": price
    })
    # Send to all connected clients
    if CONNECTED_CLIENTS:
        await asyncio.gather(
            *[ws.send(message) for ws in CONNECTED_CLIENTS],
            return_exceptions=True  # don't fail on closed conn
        )

async def main():
    # 'ping_interval=30' sends WebSocket pings every 30s
    # to detect dead connections before TCP keepalive kicks in
    async with websockets.serve(
        price_feed,
        "0.0.0.0",
        8765,
        ping_interval=30,  # send PING frame every 30s
        ping_timeout=10,   # close if PONG not received in 10s
    ):
        await asyncio.Future()  # run forever
```

---

### ⚙️ Client-Side WebSocket (Browser)

```javascript
// Browser WebSocket API
const ws = new WebSocket('wss://api.example.com/ws/prices');

// Connection opened
ws.onopen = (event) => {
    console.log('Connected');
    // Subscribe to AAPL prices
    ws.send(JSON.stringify({
        type: 'subscribe',
        symbol: 'AAPL'
    }));
};

// Message received
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'price_update') {
        updatePriceDisplay(data.symbol, data.price);
    }
};

// Connection closed
ws.onclose = (event) => {
    console.log(`Closed: code=${event.code} reason=${event.reason}`);
    // Reconnect with exponential backoff:
    setTimeout(connect, 1000 * Math.min(30, 2 ** reconnectAttempt));
    reconnectAttempt++;
};

// Error
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Close gracefully (sends Close frame)
ws.close(1000, 'User navigated away');
```

---

### ⚙️ Wrong vs Right: The Missing Reconnect Logic

```javascript
// BAD: no reconnect logic
const ws = new WebSocket('wss://api.example.com/ws');
ws.onmessage = (e) => updateUI(e.data);
// Server restarts → connection drops → UI shows stale data forever
// User must refresh page to restore updates

// GOOD: exponential backoff reconnect
class ReliableWebSocket {
    constructor(url) {
        this.url = url;
        this.reconnectDelay = 1000;
        this.maxDelay = 30000;
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('Connected');
            this.reconnectDelay = 1000; // reset on success
            this.resubscribe(); // re-send subscriptions
        };

        this.ws.onmessage = (e) => this.handleMessage(e.data);

        this.ws.onclose = (e) => {
            if (e.code !== 1000) { // 1000 = normal close
                console.log(`Reconnecting in ${this.reconnectDelay}ms`);
                setTimeout(() => this.connect(), this.reconnectDelay);
                this.reconnectDelay = Math.min(
                    this.maxDelay,
                    this.reconnectDelay * 2
                );
            }
        };
    }
}
```

---

### ⚙️ WebSocket vs Server-Sent Events (SSE) vs Polling

```
┌──────────────────────────────────────────────────────────┐
│  Mechanism       │ Direction  │ Protocol │ Use When       │
├──────────────────┼────────────┼──────────┼────────────────┤
│ Short polling    │ C → S      │ HTTP/1.1 │ Never          │
│ Long polling     │ C → S hold │ HTTP/1.1 │ Legacy, simple │
│ SSE              │ S → C only │ HTTP/1.1 │ Server push,   │
│                  │            │          │ no client send │
│ WebSocket        │ Full-duplex│ WS/WSS   │ Real-time chat,│
│                  │            │          │ gaming, trading│
│ WebSocket/HTTP2  │ Full-duplex│ HTTP/2   │ Same, better   │
│                  │            │          │ multiplexing   │
└──────────────────┴────────────┴──────────┴────────────────┘

SSE advantages over WebSocket:
  - Native browser reconnect (EventSource API)
  - Works over standard HTTP/2 (no protocol switch)
  - Simple server: just write "data: ...\n\n" to response
  - No custom ping/pong (HTTP keepalive handles it)
  - Firewalls don't block it (it's HTTP)

WebSocket advantages over SSE:
  - Full duplex: client can also push to server
  - Lower latency for bidirectional traffic
  - Binary data support without base64 encoding
  - Native WebSocket framing (no HTTP overhead)
```

---

### ⚙️ Production Concerns: Connection Management

```python
# Problem: WebSocket connections never close by themselves
# A dead client (network drop, process kill) looks connected
# until the OS detects the dead TCP connection (hours!)

# Solution: application-level ping/pong + timeout

# Server-side: send PING frames, close on no PONG
async with websockets.serve(
    handler,
    host="0.0.0.0",
    port=8765,
    ping_interval=20,   # PING every 20 seconds
    ping_timeout=20,    # close if PONG not received in 20s
    close_timeout=10,   # grace period for Close frame
):
    ...

# Load balancer consideration:
# AWS ALB default idle timeout: 60 seconds
# WebSocket connections are idle between messages
# → ALB kills idle WebSocket connection after 60s!
# Fix: increase idle timeout or send pings every 55s
# AWS CLI:
# aws elbv2 modify-load-balancer-attributes \
#   --attributes Key=idle_timeout.timeout_seconds,Value=3600

# nginx proxy for WebSocket:
# location /ws/ {
#     proxy_pass http://backend;
#     proxy_http_version 1.1;
#     proxy_set_header Upgrade $http_upgrade;
#     proxy_set_header Connection "Upgrade";
#     proxy_read_timeout 3600;  ← must be > ping interval!
# }
```

---

### ⚙️ Failure Example: WebSocket Behind a Proxy That Strips Upgrade Headers

**Symptoms:** WebSocket connection fails with 200 OK or
400 Bad Request. `ws.onerror` fires immediately after
connection attempt.

**Root cause:**

```bash
# Diagnose: capture the handshake
curl -v -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     https://api.example.com/ws

# If response is 200 OK (not 101):
# → Proxy intercepted the request and returned HTTP response
# → Proxy doesn't support WebSocket passthrough

# If response is 400:
# → Proxy stripped the Upgrade header before forwarding
# → Server got request without Upgrade → rejected

# Fix: configure proxy to pass WebSocket headers
# nginx:
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection $connection_upgrade;
# map $http_upgrade $connection_upgrade {
#   default upgrade;
#   ''      close;
# }

# AWS ALB: supports WebSocket natively (no config needed)
# HAProxy: "option http-server-close" breaks WebSocket
#          Use "option http-tunnel" for WebSocket backends
```

---

### 📐 Scale Considerations

```
WebSocket connection cost per server:
  Memory: ~40-80 KB per connection (OS socket + buffers)
  File descriptor: 1 per connection (system limit applies)
  CPU: negligible when idle

10,000 concurrent WebSocket connections:
  Memory: 10K × 64KB = ~640MB (manageable)
  File descriptors: 10,000 (Linux default limit: 65,536)
  Check/increase: ulimit -n 100000

Horizontal scaling challenge:
  Connection 1 on server-A, Connection 2 on server-B
  Message for all users must reach both servers
  Solution: Pub/Sub layer (Redis Pub/Sub, Kafka)
    Server-A publishes to Redis channel "prices:AAPL"
    Server-B subscribes and forwards to its connections

  Architecture:
    Client1 →[WS]→ Server-A →[subscribe]→ Redis ←[subscribe]← Server-B ←[WS]← Client2
    When price changes: Redis pub → both servers → both clients

1M concurrent connections:
  1M × 64KB = 64GB memory
  Requires multiple servers with Redis/Kafka fan-out
  Netflix, Slack, Discord operate at this scale
```

---

### 🧭 Decision Guide

```
Should I use WebSocket?
  YES if:
  - Server needs to PUSH updates to client unpredictably
  - Client also sends data back (chat, gaming, collaborative)
  - Low latency is critical (financial trading, real-time gaming)
  - High update frequency (> 1 update/second per client)

  NO if:
  - Server never pushes (just request-response) → HTTP is fine
  - Server pushes, client never sends → SSE is simpler
  - Update frequency is low (< 1/minute) → long polling is fine
  - Enterprise environment with strict firewall → SSE safer

WebSocket Close Codes (to know):
  1000 = Normal closure
  1001 = Going away (page navigated away or server shutdown)
  1002 = Protocol error
  1003 = Unsupported data
  1006 = Abnormal closure (no Close frame, TCP reset)
  1011 = Server internal error
  1012 = Service restart (client should reconnect)
  1013 = Try again later (overloaded, back off)

Interview one-liner:
  "WebSocket starts as HTTP GET with Upgrade header.
  Server responds 101. The TCP connection becomes a
  persistent full-duplex channel. Frames have 2-6 byte
  overhead vs 600+ bytes for HTTP requests. Use for
  real-time push: chat, trading, gaming, live dashboards.
  Critical: implement reconnect with backoff and
  application-layer pings to detect dead connections."
```