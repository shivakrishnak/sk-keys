---
layout: default
title: "WebSocket"
parent: "HTTP & APIs"
nav_order: 227
permalink: /http-apis/websocket/
number: "0227"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, TCP, HTTP Upgrade Mechanism
used_by: Real-time Apps, gRPC Streaming, GraphQL Subscriptions
related: Server-Sent Events, Long Polling, gRPC Streaming
tags:
  - api
  - websocket
  - realtime
  - bidirectional
  - intermediate
---

# 227 — WebSocket

⚡ TL;DR — WebSocket is a full-duplex, persistent communication channel between a client and server over a single TCP connection, established via an HTTP upgrade handshake — enabling real-time bidirectional data exchange without the overhead of repeated HTTP requests.

┌──────────────────────────────────────────────────────────────────────────┐
│ #227 │ Category: HTTP & APIs │ Difficulty: ★★☆ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ HTTP, TCP, HTTP Upgrade Mechanism │ │
│ Used by: │ Real-time Apps, gRPC Streaming, │ │
│ │ GraphQL Subscriptions │ │
│ Related: │ Server-Sent Events, Long Polling, │ │
│ │ gRPC Streaming │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A chat application using REST: the client polls `GET /messages?since=lastTime` every
2 seconds. At 10,000 users sending 5 messages each: 10,000 HTTP requests every 2
seconds just for polling, most returning empty responses. Each request carries full
HTTP headers (~500 bytes). Messages have up to 2-second delivery latency. The server
holds 10,000 half-open connections just waiting for the next poll cycle.

**THE BREAKING POINT:**
A stock trading platform needs sub-100ms price updates. A multiplayer game needs
game-state updates 60 times per second per client. An online collaborative editor
needs keystrokes delivered in real-time to all participants. None of these are possible
with polling without either drowning the server or having unacceptably high latency.

**THE INVENTION MOMENT:**
WebSocket (RFC 6455, 2011) solves this by converting an HTTP connection into a
persistent bidirectional channel. After a one-time HTTP upgrade handshake, the
connection stays open. Either side can send a message any time, with just 2–14
bytes of framing overhead (vs ~500 bytes HTTP headers per request). A chat message
is delivered the millisecond it's sent, with minimal overhead.

---

### 📘 Textbook Definition

**WebSocket** is a full-duplex communication protocol over a single persistent TCP
connection, standardized in RFC 6455 (2011) and supported by all modern browsers
via the `WebSocket` API. Established by an HTTP upgrade handshake (client sends
`Upgrade: websocket` header; server confirms with `101 Switching Protocols`), after
which the connection switches from HTTP framing to WebSocket framing. WebSocket
frames carry a payload (text or binary), an opcode (Text=1, Binary=2, Ping=9, Pong=10,
Close=8), a masking bit (all client→server frames are masked), and a payload length.
Either party can initiate a message independently. Neither party has to "wait for a turn."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
WebSocket upgrades an HTTP connection into a permanent two-way communication channel — like a phone call that stays open instead of sending individual text messages.

**One analogy:**

> HTTP is like sending letters: you write one (request), mail it, wait for a reply letter
> (response), then write again. WebSocket is like a phone call: you dial once (handshake),
> and then you both can speak and listen simultaneously for as long as you want, with
> no "please wait for my full reply" protocol. The connection is open; speaking is instant.

**One insight:**
WebSocket's magic is not protocol complexity — the handshake is a single HTTP exchange.
The power is in staying connected. Instead of paying 500 bytes of HTTP header overhead
per message, WebSocket pays that overhead once at handshake time. Every subsequent
message adds only 2–14 bytes of framing. A 50-byte chat message costs 50+2 bytes
(WebSocket) vs 50+500 bytes (HTTP). At 1,000 messages/second, that's 500KB/s vs
550KB/s — trivial. At 1,000,000 messages/second: 50MB/s vs 550MB/s — significant.

---

### 🔩 First Principles Explanation

**WEBSOCKET HANDSHAKE:**

```
Client request:
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

Server response:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After `101 Switching Protocols`, the TCP connection is now a WebSocket channel.
HTTP is no longer spoken on this connection.

**FRAME FORMAT:**

```
Byte 0: [FIN|RSV1|RSV2|RSV3|Opcode(4bits)]
Byte 1: [MASK|Payload length(7bits)]
Bytes 2-N: Extended payload length (if needed)
Bytes N-M: Masking key (4 bytes, client→server only)
Bytes M-end: Payload data
```

**OPCODES:**

```
0x1 = Text frame
0x2 = Binary frame
0x8 = Close frame (graceful close)
0x9 = Ping (keepalive probe)
0xA = Pong (keepalive response)
```

**MASKING (security):**
Client→server frames are always masked with a 4-byte random key to prevent
cache poisoning attacks on intermediaries (proxies that might cache WebSocket
frames as if they were HTTP responses). Server→client frames are NOT masked.

**THE TRADE-OFFS:**

- Gain: full-duplex, persistent → zero per-message HTTP overhead.
- Cost: stateful connections → horizontal scaling requires sticky sessions or shared state.
- Gain: sub-millisecond delivery latency for push messages.
- Cost: no built-in message format, authentication, or reconnection — all must be implemented in application code.
- Gain: binary or text frames — works for any data type.
- Cost: not cacheable; no automatic retries; connection drops silently if not monitored with pings.

---

### 🧪 Thought Experiment

**SETUP:**
A live auction platform in the final 10 seconds of bidding. 5,000 users are all
watching the same item. Each increment updates the displayed price. Average: 3 bids
per second in the final 10 seconds = 30 price changes broadcast to 5,000 users.

**HTTP POLLING (2-second interval):**

```
Polling: 5,000 users × 0.5 req/s = 2,500 req/s
Useful responses: ~30 price changes / 10 seconds = 3/s
Useful ratio: 3/2500 = 0.1% useful
Plus: up to 2-second latency per update (a bid could expire before users see it)
```

**WEBSOCKET:**

```
Connections: 5,000 open WebSocket connections
Event push: server broadcasts each bid to all 5,000 connections
Messages/second: 3 events × 5,000 subscribers = 15,000 pushes/s
Latency: ~5ms (network round trip)
Server memory: ~5,000 connection objects × ~50KB = ~250MB
```

**THE INSIGHT:**
WebSocket's persistent connections have a fixed memory cost but dramatically
lower computational cost for real-time events. The cost model inverts: polling
is cheap per-connection but expensive per-event; WebSocket is expensive per-connection
but cheap per-event. For high-frequency, multi-subscriber events, WebSocket wins.
For infrequent or one-off notifications: polling or SSE may be sufficient.

---

### 🧠 Mental Model / Analogy

> HTTP is a vending machine: insert a request (coin), get a response (item), machine
> goes back to waiting. Each exchange is independent. WebSocket is a telephone line
> connected to your home: once installed, both parties can communicate instantly any
> time, in either direction, until someone hangs up. The phone company doesn't charge
> you per word — just for the line being open.

- "Calling a number" → HTTP upgrade handshake
- "Line connected" → WebSocket connection established
- "Both speaking/listening" → full-duplex frames in both directions
- "Hanging up" → Close frame (opcode 0x8)
- "Busy signal" → server refusing the upgrade (HTTP 400/500)
- "Static on the line" → network interruption requiring reconnect

**Where this analogy breaks down:** Phone calls have natural silence detection.
WebSocket connections silently die if one side drops without sending a Close frame
(e.g., server restart, network interruption). Applications must implement Ping/Pong
to detect dead connections — WebSocket doesn't do this automatically.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
WebSocket lets a web page stay in a permanent two-way conversation with a server.
Instead of constantly asking "any new messages?" and getting "not yet" 99% of the time,
WebSocket keeps a line open so the server can instantly send new information as soon
as it's available. Chat applications, live sports scores, and real-time stock prices
all use WebSocket.

**Level 2 — How to use it (junior developer):**
Browser JavaScript: `const ws = new WebSocket("wss://api.example.com/chat");`
Listen for events: `ws.onopen`, `ws.onmessage`, `ws.onerror`, `ws.onclose`.
Send: `ws.send("Hello server")`. Server-side Spring Boot: extend
`TextWebSocketHandler`, override `handleTextMessage()`, `afterConnectionEstablished()`.
Register in `WebSocketConfigurer`. Use `SockJS` + `STOMP` for richer features
(reconnect, message routing) and older browser support.

**Level 3 — How it works (mid-level engineer):**
After the `101 Switching Protocols` response, the HTTP parser on both sides is replaced
by the WebSocket framing parser. Messages are sent as one or more frames (large
messages can be fragmented). The server receives frames, buffers fragmented messages,
and delivers complete messages to application handlers. Session management is
per-connection application responsibility — the server must maintain a map of
`sessionId → WebSocketSession` to send targeted messages. Broadcast to N clients
requires iterating the session map and calling `session.sendMessage()` N times.
This is where SockJS/STOMP add value: a message broker (RabbitMQ, STOMP broker)
handles routing and broadcast, decoupling session management from business logic.
At scale with multiple server instances: publish events to a shared broker; each
instance delivers to its locally connected clients.

**Level 4 — Why it was designed this way (senior/staff):**
The HTTP upgrade handshake was a pragmatic choice to make WebSocket firewall-friendly.
Traditional HTTP ports (80, 443) are open in most corporate firewalls; a new TCP
port for real-time communication would be blocked. By starting as an HTTP request
and upgrading, WebSocket works through existing firewall rules. The `Sec-WebSocket-Key`
/ `Sec-WebSocket-Accept` challenge-response prevents web pages from hijacking HTTP
connections belonging to other applications (security guard against cross-origin
cache poisoning). The masking requirement for client→server frames was added when
it was discovered that non-masked frames could be exploited through misconfigured
HTTP proxies that cached WebSocket frames as HTTP responses. This masking has
non-trivial CPU cost at very high message rates — a recognized spec criticism.
HTTP/2's server push feature was initially seen as a WebSocket competitor, but
server push was removed from HTTP/2 by major browsers in 2022 (too complex, rarely
used) — reinforcing WebSocket's position as the standard for bidirectional real-time
communication.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────────┐
│              WEBSOCKET CONNECTION LIFECYCLE                  │
├──────────────────────────────────────────────────────────────┤
│  1. HANDSHAKE:                                               │
│  Client → HTTP GET + Upgrade headers                        │
│  Server → 101 Switching Protocols                           │
│  TCP connection remains open; HTTP parsing ends             │
│                                                              │
│  2. DATA EXCHANGE:                                           │
│  Client → [FIN=1][opcode=0x1][MASK=1][len=5][key][payload] │
│              "Hello"  (masked, text frame)                  │
│  Server → [FIN=1][opcode=0x1][MASK=0][len=5][payload]      │
│              "World"  (unmasked, text frame)                │
│                                                              │
│  3. KEEPALIVE:                                              │
│  Server → [FIN=1][opcode=0x9][] (Ping)                     │
│  Client → [FIN=1][opcode=0xA][] (Pong) — must respond      │
│  No Pong within timeout → server closes connection          │
│                                                              │
│  4. CLOSE:                                                  │
│  Either side → [FIN=1][opcode=0x8][status code + reason]   │
│  Other side echoes Close frame                              │
│  TCP connection closed (FIN/ACK)                            │
└──────────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Client opens: ws://api.example.com/chat  (or wss:// for TLS)
     ↓ HTTP Upgrade handshake ↓
WebSocket connection established
     ↓
Client sends: ws.send(JSON.stringify({type:"join", channel:"general"}))
     ↓ Frame arrives at server ↓
Server handler: onmessage() → parse JSON → route to channel
Server broadcasts: session.sendMessage(new TextMessage(eventJson))
     ↓ to ALL sessions in "general" channel ↓
Client receives: ws.onmessage → display message
     ↓
Client closes tab: TCP FIN → server onclose() → remove from channel map
```

---

### 💻 Code Example

```java
// Spring Boot WebSocket server
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Autowired private ChatWebSocketHandler chatHandler;

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(chatHandler, "/ws/chat")
                .setAllowedOrigins("https://app.example.com")
                .withSockJS(); // fallback for environments that block WebSocket
    }
}

@Component
public class ChatWebSocketHandler extends TextWebSocketHandler {

    // Thread-safe map of active connections per channel
    private final ConcurrentHashMap<String, Set<WebSocketSession>> channels =
        new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        String channel = getChannelFromHandshake(session);
        channels.computeIfAbsent(channel, k -> ConcurrentHashMap.newKeySet())
                .add(session);
        log.info("Connection {} joined channel {}", session.getId(), channel);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session,
                                     TextMessage message) throws Exception {
        ChatMessage msg = parseMessage(message.getPayload());
        broadcastToChannel(msg.getChannel(), message.getPayload(), session);
    }

    private void broadcastToChannel(String channel, String payload,
                                    WebSocketSession sender) {
        Set<WebSocketSession> sessions = channels.getOrDefault(channel, Set.of());
        for (WebSocketSession target : sessions) {
            if (target.isOpen() && !target.getId().equals(sender.getId())) {
                try {
                    target.sendMessage(new TextMessage(payload));
                } catch (IOException e) {
                    log.warn("Failed to send to session {}", target.getId(), e);
                }
            }
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session,
                                      CloseStatus status) {
        channels.values().forEach(s -> s.remove(session));
        log.info("Connection {} closed: {}", session.getId(), status);
    }
}
```

```javascript
// Browser JavaScript WebSocket client
const ws = new WebSocket("wss://api.example.com/ws/chat?channel=general");

ws.onopen = () => {
  console.log("Connected");
  ws.send(JSON.stringify({ type: "join", user: "Alice" }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  displayMessage(msg);
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = (event) => {
  console.log("Disconnected, code:", event.code);
  // Reconnect with exponential backoff:
  setTimeout(() => reconnect(), Math.min(30000, backoffMs));
};

// Send a message:
ws.send(
  JSON.stringify({ type: "message", text: "Hello!", channel: "general" }),
);
```

---

### ⚖️ Comparison Table

| Feature                  | WebSocket           | SSE                  | Long Polling         | gRPC Bidirectional         |
| ------------------------ | ------------------- | -------------------- | -------------------- | -------------------------- |
| **Direction**            | Full duplex         | Server→Client only   | Simulated push       | Full duplex                |
| **Protocol**             | WS (TCP)            | HTTP/1.1, HTTP/2     | HTTP                 | HTTP/2                     |
| **Browser support**      | Universal           | Universal            | Universal            | gRPC-Web proxy needed      |
| **Auto-reconnect**       | No (manual)         | Yes (built-in)       | Per-request          | No (manual)                |
| **Message typing**       | Text or Binary      | Text only            | Text/JSON            | Typed (Protobuf)           |
| **Overhead per message** | ~2–14 bytes         | HTTP headers         | Full HTTP            | ~5 bytes (gRPC frame)      |
| **Best for**             | Chat, games, collab | Notifications, feeds | Simple push (legacy) | Internal service streaming |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                      |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| WebSocket works through all proxies                 | Corporate HTTP proxies often break WebSocket; use `wss://` (TLS) which is harder for proxies to intercept; or test behind your load balancer |
| WebSocket connections auto-reconnect                | WebSocket has NO built-in reconnection; the application must implement retry logic (most libraries like SockJS provide this)                 |
| WebSocket replaces REST for all communication       | REST is still better for standard CRUD; WebSocket is for sustained real-time bidirectional communication                                     |
| Dead WebSocket connections are detected immediately | Without Ping/Pong heartbeats, a silent TCP reset may not be detected for minutes; always implement heartbeat keepalives                      |
| WebSocket and HTTP/2 are incompatible               | HTTP/2 supports WebSocket (RFC 8441 "Bootstrapping WebSockets with HTTP/2") but browser support varies                                       |

---

### 🚨 Failure Modes & Diagnosis

**Silent Dead Connection — Messages Sent to Lost Clients**

Symptom:
Server logs show messages sent but clients don't receive them. Session count
grows indefinitely but active users stay flat. Memory slowly grows.

Root Cause:
Connections drop due to network interruptions without proper TCP FIN/RST.
Server still has `WebSocketSession` objects marked as open, but sending fails
silently or with delayed IOException.

Diagnostic Command / Tool:

```java
// Add ping-based heartbeat to detect dead connections:
@Scheduled(fixedDelay = 30000) // every 30 seconds
public void pingAll() {
    for (Map.Entry<String, Set<WebSocketSession>> entry : channels.entrySet()) {
        entry.getValue().removeIf(session -> {
            if (!session.isOpen()) return true;
            try {
                session.sendMessage(new PingMessage());
                return false;
            } catch (IOException e) {
                log.warn("Dead session detected: {}", session.getId());
                return true; // remove from set
            }
        });
    }
}
```

Fix:
Implement Ping/Pong heartbeats. Remove sessions that don't respond to pings
within a timeout. Use `session.isOpen()` before sending.

Prevention:
Set `SO_KEEPALIVE` on server TCP sockets. Add application-level heartbeat
with 30-second interval and 90-second timeout. Monitor session count vs
active user count — divergence indicates session leaks.

---

### 🔗 Related Keywords

- `HTTP` — WebSocket starts with an HTTP upgrade handshake
- `Server-Sent Events (SSE)` — simpler, unidirectional alternative for server-push
- `Long Polling` — older fallback technique for server-push before WebSocket
- `gRPC Streaming` — WebSocket alternative for typed, binary internal service streaming
- `GraphQL Subscriptions` — built on WebSocket for real-time GraphQL events

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Full-duplex TCP channel via HTTP upgrade: │
│              │ both sides send/receive any time          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ HTTP polling is wasteful; no way to push  │
│ SOLVES       │ server → client without client asking     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ One-time handshake → persistent low-      │
│              │ overhead bidirectional channel            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Chat, gaming, live dashboards, collab     │
│              │ editing — bidirectional real-time needed  │
├──────────────┼───────────────────────────────────────────┤
│ WATCH OUT    │ No auto-reconnect; no auto dead detection │
│              │ → implement Ping/Pong heartbeats          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HTTP upgrade → phone call"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SSE → Long Polling → gRPC Streaming      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A multiplayer game server handles 50,000 concurrent WebSocket connections, each receiving 60 game-state updates per second. The server has 16 CPU cores. Profile the bottlenecks in: (a) iterating all sessions for broadcast, (b) JSON serialization per frame, (c) TCP write calls. How would you redesign the broadcast model to achieve 3 million messages/second on this hardware?

**Q2.** Enterprise firewalls intermittently break WebSocket connections by injecting HTTP responses mid-stream. You need WebSocket functionality but can't control the network. Design a transparent fallback strategy that: detects when WebSocket is blocked, falls back to long polling automatically, maintains the same application API for both transport modes.
