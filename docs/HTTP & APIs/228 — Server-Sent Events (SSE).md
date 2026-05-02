---
layout: default
title: "Server-Sent Events (SSE)"
parent: "HTTP & APIs"
nav_order: 228
permalink: /http-apis/server-sent-events/
number: "0228"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, HTTP/2, Event Streaming
used_by: Real-time Notifications, Live Feeds, LLM Streaming Responses
related: WebSocket, Long Polling, gRPC Streaming
tags:
  - api
  - sse
  - realtime
  - server-push
  - intermediate
---

# 228 — Server-Sent Events (SSE)

⚡ TL;DR — Server-Sent Events (SSE) is a simple HTTP-based server-push mechanism where the server streams a sequence of text events over a single persistent HTTP connection; the browser auto-reconnects on disconnect, making it ideal for one-way real-time feeds like notifications, live scores, and LLM token streaming.

| #228 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, HTTP/2, Event Streaming | |
| **Used by:** | Real-time Notifications, Live Feeds, LLM Streaming Responses | |
| **Related:** | WebSocket, Long Polling, gRPC Streaming | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A dashboard shows live server metrics: CPU, memory, network I/O, updated every second.
With polling: 1,000 dashboard users × 1 req/s = 1,000 HTTP requests per second,
each carrying ~500 bytes of headers, most returning the same data.
With WebSocket: overkill — the dashboard never needs to send anything back to the
server. The complexity of WebSocket (handshake, frame protocol, masking, reconnect
logic) is unwarranted for pure server-to-client event streams.

**THE BREAKING POINT:**
Modern LLM chat interfaces (ChatGPT, Claude) stream AI-generated tokens to the browser
as they're produced. The server generates tokens one at a time and needs to push each
token instantly to the user without waiting for the entire response. HTTP/REST would
require either one giant response (wait until done) or polling (slow, wasteful).
WebSocket works but is heavier than needed for this one-directional use case.

**THE INVENTION MOMENT:**
SSE (standardized in HTML5 and W3C EventSource API) provides exactly what's needed:
a simple text-based streaming protocol where the server writes `data: ...\n\n` lines
over a persistent HTTP response, and the browser displays them in real-time with
built-in auto-reconnect. No JavaScript WebSocket complexity. No frame protocol to
implement. Works over plain HTTP/1.1 or HTTP/2 with content-type `text/event-stream`.

---

### 📘 Textbook Definition

**Server-Sent Events (SSE)** is a W3C standard (via HTML Living Standard) and
server-push mechanism where a server sends a sequence of events to a client over
a single long-lived HTTP connection with `Content-Type: text/event-stream`. Events
are formatted as UTF-8 text with optional fields: `id:`, `event:`, `data:`, `retry:`,
followed by a blank line as the event separator. The browser's `EventSource` API
handles the HTTP connection, event parsing, automatic reconnection (using `Last-Event-ID`
header to resume from the last received event), and dispatches events to JavaScript
handlers. SSE is unidirectional (server→client only) and text-only by design.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SSE is the simplest way to push real-time updates from server to browser — just write text lines to an open HTTP response, browser reads them as they arrive.

**One analogy:**

> SSE is like a live news ticker scrolling at the bottom of a TV broadcast.
> The TV station (server) keeps scrolling new headlines (events) over the same
> broadcast connection. You (browser) are always receiving — you don't send anything
> back. If the channel goes fuzzy (connection drops), your TV auto-tunes back in
> (auto-reconnect) and the broadcaster resumes from where you left off (Last-Event-ID).

**One insight:**
SSE is the "right tool" for a specific use case: reliable, low-complexity server-to-client
event streams over HTTP. It's _not_ a fallback for WebSocket — it's genuinely better
than WebSocket for one-directional, text-based event streams because:
(1) works over HTTP/2 (multiple streams on one connection), (2) auto-reconnects natively,
(3) no client-side WebSocket state machine, (4) proxies handle it like regular HTTP.

---

### 🔩 First Principles Explanation

**SSE WIRE FORMAT:**

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

id: 1
event: priceUpdate
data: {"symbol": "AAPL", "price": 175.23}

id: 2
data: simple text message

id: 3
event: alert
data: line 1 of
data: multiline message

retry: 5000

```

**FORMAT RULES:**

```
data:  — payload (required for content)
event: — event type (default "message" if omitted)
id:    — event ID for reconnect resume (Last-Event-ID header)
retry: — client reconnect delay in ms
\n\n   — blank line = event separator (sends the event)
:      — comment (line starting with colon, ignored by client)
```

**AUTO-RECONNECT FLOW:**

```
Client opens EventSource("https://api.example.com/events")
     ↓ receives events ↓
Server goes down / connection drops
     ↓ EventSource auto-reconnects (default 3000ms) ↓
Client sends: GET /events
              Last-Event-ID: 12 (last received event ID)
Server resumes from event ID 13 onward
```

**HTTP/2 ADVANTAGE:**
With HTTP/1.1: max 6 SSE connections per browser per host (6-connection limit).
With HTTP/2: one TCP connection, unlimited multiplexed streams — 100 concurrent
SSE subscriptions use one TCP connection.

**THE TRADE-OFFS:**

- Gain: built-in auto-reconnect with resume → zero client reconnect code needed.
- Cost: text-only (UTF-8) — binary data must be Base64 encoded (25% overhead).
- Gain: standard HTTP — works through proxies, CDNs, load balancers naturally.
- Cost: unidirectional — client can't send data over the SSE connection; use separate HTTP calls.
- Gain: simpler than WebSocket — no frame protocol, no masking, no state machine.
- Cost: HTTP/1.1 browser connection limit (6/host) — mitigated by HTTP/2.

---

### 🧪 Thought Experiment

**SETUP:**
An LLM chat interface streams 500-token completions. Each token arrives ~20ms apart.
The UI should display tokens as they're generated, not wait for the full response.

**WITHOUT SSE (single JSON response):**
User sends question → waits 10 seconds → entire response arrives → displays.
UX: 10-second blank wait. Conversion rate: poor.

**WITH SSE:**
User sends question → first token appears in ~200ms → user sees the response
being "typed" token by token → UX feels responsive even before completion.

**IMPLEMENTATION:**

```
Server response:
Content-Type: text/event-stream

data: {"token": "The", "done": false}

data: {"token": " answer", "done": false}

data: {"token": " is", "done": false}

data: {"token": " 42", "done": false}

data: {"token": "", "done": true}

```

**THE INSIGHT:**
SSE's streaming model maps naturally to generative AI token-by-token output.
OpenAI's API, Anthropic's Claude API, and most LLM APIs use SSE for this exact
reason. The protocol is so simple that the `data:` prefix is the only convention —
everything else is JSON inside the data.

---

### 🧠 Mental Model / Analogy

> Think of SSE as a subscription to a live newsfeed (like Twitter's streaming API
> before it was removed). You open one long-lived HTTP connection. Events flow
> to you as a text stream, line by line. Unlike WebSocket (a two-way radio channel),
> SSE is like a radio station — you receive broadcasts, you don't transmit.
> If the station goes off the air (server down), your radio automatically tries
> to re-tune to the same frequency (auto-reconnect). Your radio also notes the
> last broadcast ID so you can ask for a replay from that point (Last-Event-ID).

- "Tuning to a station" → `new EventSource(url)`
- "Listening to broadcast" → `source.onmessage` handler
- "Different show types" → `event:` types + `source.addEventListener('priceUpdate', ...)`
- "Retrying dead station" → auto-reconnect with configurable `retry:` interval
- "Picking up where you left off" → `Last-Event-ID` header on reconnect

**Where this analogy breaks down:** A real radio broadcasts to everyone indiscriminately.
SSE is a dedicated line per client — each client gets their own HTTP connection.
Sending the same event to 10,000 clients means 10,000 HTTP write operations
(though HTTP/2 multiplexing reduces TCP connections).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
SSE lets a webpage receive continuous updates from a server without ever refreshing
the page. The server keeps the response "streaming" and adds new event lines whenever
something happens. The browser displays them automatically. Chat notifications,
live scores, AI responses being typed — all use this pattern.

**Level 2 — How to use it (junior developer):**
Browser: `const source = new EventSource('/events');`
`source.onmessage = e => console.log(e.data);`
`source.addEventListener('priceUpdate', e => handlePrice(e.data));`
Server-side Spring (Spring MVC): return `SseEmitter` from controller.
`SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);`
`emitter.send(SseEmitter.event().data("hello").id("1").name("greeting"));`
`emitter.complete();`
WebFlux: return `Flux<ServerSentEvent<String>>` — Spring streams it automatically.

**Level 3 — How it works (mid-level engineer):**
When the browser creates an `EventSource`, it opens a GET request with
`Accept: text/event-stream`. The server must return `Content-Type: text/event-stream`
and keep the response body open (never send final `\r\n\r\n` that would close HTTP/1).
Each event is written as text lines followed by `\n\n`. The browser's SSE parser
accumulates field lines until the blank line, then dispatches the event. For Spring MVC
(blocking): `SseEmitter` holds a response writer open on a thread; use async servlets
to avoid blocking the thread pool. For Spring WebFlux (reactive): `Flux<ServerSentEvent>`
streams through Reactor without holding a thread between events. At scale with
multiple server instances: SSE connections are stateful (tied to a specific server
instance) — events published on server A don't reach clients on server B. Fix:
use Redis Pub/Sub to broadcast events to all server instances.

**Level 4 — Why it was designed this way (senior/staff):**
SSE's text-only, unidirectional, line-based design was intentional simplicity.
The EventSource API was designed to be accessible to any web developer without
understanding TCP framing, masking, or binary protocols. The decision to use plain
HTTP (not a new protocol) makes SSE work through every HTTP infrastructure — CDNs,
load balancers, and proxies treat it as a long-running HTTP response. HTTP/2
multiplexing fixed SSE's biggest practical limitation (the 6-connection browser limit)
without changing SSE itself. The resurgence of SSE in the LLM era (ChatGPT, Claude,
Gemini all use SSE for streaming completions) demonstrates that simple protocols
age well. SSE's auto-reconnect with `Last-Event-ID` was ahead of its time —
most WebSocket implementations still have to implement this manually. The limitation
of text-only is rarely an issue: JSON over text-format events covers 95% of
real-time web use cases.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────────┐
│              SSE STREAM FLOW                                 │
├──────────────────────────────────────────────────────────────┤
│  Client: GET /events                                         │
│          Accept: text/event-stream                          │
│          Last-Event-ID: 5  (on reconnect)                   │
│                          ↓                                   │
│  Server: HTTP/1.1 200 OK                                    │
│          Content-Type: text/event-stream                    │
│          Cache-Control: no-cache                            │
│          [response body stays OPEN]                         │
│                          ↓                                   │
│  Server writes event:                                       │
│  id: 6\n                                                    │
│  event: priceUpdate\n                                       │
│  data: {"price": 175.00}\n                                  │
│  \n         ← blank line SENDS the event                    │
│                          ↓ client EventSource decodes       │
│  source.addEventListener("priceUpdate", handler) fires      │
│  handler receives: {data: '{"price": 175.00}', lastEventId: '6'}
│                          ↓                                   │
│  Connection drops → EventSource waits retry ms → reconnects │
│  Sends Last-Event-ID: 6 → server resumes from event 7       │
└──────────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
User loads dashboard page
EventSource("/api/metrics") opens
   ↓
Server: SseEmitter / Flux<SSE> subscription starts
   ↓
Background job publishes metrics every second
   ↓
Server writes: data: {cpu:45, mem:60}\n\n to each connected emitter
   ↓
Browser EventSource fires onmessage callback
   ↓
UI updates CPU/memory gauges in real-time
   ↓
Server restart: connection drops → EventSource reconnects in 3s
   ↓
Server sends missed events using Last-Event-ID (if buffered)
```

---

### 💻 Code Example

```java
// Spring Boot MVC — SseEmitter approach
@RestController
public class MetricsStreamController {

    @Autowired private MetricsService metricsService;

    // Store emitters for broadcasting
    private final List<SseEmitter> emitters =
        Collections.synchronizedList(new ArrayList<>());

    @GetMapping(path = "/api/metrics/stream",
                produces = "text/event-stream")
    public SseEmitter streamMetrics() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);

        emitters.add(emitter);
        emitter.onCompletion(() -> emitters.remove(emitter));
        emitter.onTimeout(() -> emitters.remove(emitter));
        emitter.onError(e -> emitters.remove(emitter));

        return emitter;
    }

    // Called by background scheduler
    @Scheduled(fixedRate = 1000)
    public void broadcastMetrics() {
        Metrics metrics = metricsService.getCurrent();
        List<SseEmitter> dead = new ArrayList<>();

        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event()
                    .id(String.valueOf(System.currentTimeMillis()))
                    .name("metrics")
                    .data(metrics)
                    .reconnectTime(3000));
            } catch (IOException e) {
                dead.add(emitter);
            }
        }
        emitters.removeAll(dead);
    }
}
```

```java
// Spring WebFlux — reactive streaming (preferred for high concurrency)
@RestController
public class ReactiveSseController {

    @Autowired private MetricsEventPublisher publisher;

    @GetMapping(path = "/api/metrics/stream",
                produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<Metrics>> streamMetrics(
            @RequestHeader(value = "Last-Event-ID",
                           required = false) String lastEventId) {

        return publisher.getMetricsFlux()
            .map(metrics -> ServerSentEvent.<Metrics>builder()
                .id(String.valueOf(metrics.getTimestamp()))
                .event("metrics")
                .data(metrics)
                .retry(Duration.ofSeconds(3))
                .build())
            .doOnSubscribe(s -> log.info("SSE stream started, lastEventId={}",
                lastEventId));
    }
}
```

```javascript
// Browser JavaScript EventSource client
const source = new EventSource("/api/metrics/stream");

// Handle default "message" event type
source.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboard(data);
};

// Handle custom event type
source.addEventListener("metrics", (event) => {
  const metrics = JSON.parse(event.data);
  updateCpuGauge(metrics.cpu);
  updateMemGauge(metrics.memory);
});

source.onerror = (error) => {
  console.error("SSE error:", error);
  // EventSource auto-reconnects — no manual retry needed
};

// Manual close when navigating away:
window.addEventListener("beforeunload", () => source.close());
```

---

### ⚖️ Comparison Table

| Feature                  | SSE                | WebSocket                | Long Polling                |
| ------------------------ | ------------------ | ------------------------ | --------------------------- |
| **Direction**            | Server → Client    | Bidirectional            | Server → Client (simulated) |
| **Protocol**             | Plain HTTP         | HTTP upgrade → WS        | Plain HTTP                  |
| **Auto-reconnect**       | ✓ Built-in         | ✗ Manual                 | Manual (per request)        |
| **Resume on reconnect**  | ✓ Last-Event-ID    | ✗ Manual                 | ✗ Manual                    |
| **Proxy/firewall**       | Works naturally    | Sometimes blocked        | Works naturally             |
| **HTTP/2**               | ✓ Multiple streams | Separate spec (RFC 8441) | N/A                         |
| **Data format**          | Text only          | Text or Binary           | Any                         |
| **LLM token streaming**  | ★ Perfect fit      | Overkill                 | Not suitable                |
| **Chat (bidirectional)** | ✗ Can't send       | ★ Perfect fit            | Usable (with effort)        |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                 |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| SSE is deprecated or inferior to WebSocket   | SSE is actively used (LLM APIs, notifications); it's better than WebSocket for unidirectional use cases                                 |
| SSE requires WebSocket as fallback           | SSE works in all modern browsers; long polling is only needed for IE < 10 (legacy)                                                      |
| SSE is limited to 6 connections per host     | HTTP/1.1 limit applies; with HTTP/2, the limit is effectively gone — single TCP connection for many SSE streams                         |
| SSE can send binary data                     | SSE is text-only; binary must be Base64-encoded or use WebSocket instead                                                                |
| Auto-reconnect means messages are never lost | Auto-reconnect resumes from `Last-Event-ID` only if the server implements event buffering; if not, events during disconnection are lost |

---

### 🚨 Failure Modes & Diagnosis

**SSE Broken by Buffering Proxy**

Symptom:
SSE works in direct browser tests but not through corporate proxy or nginx.
Events arrive in batches (buffered) rather than individually, or don't arrive
until connection closes.

Root Cause:
HTTP proxy is buffering the response body, waiting until the connection closes
before forwarding. SSE requires events to be flushed immediately.

Diagnostic Command / Tool:

```bash
# Test SSE directly vs through proxy:
curl -N -H "Accept: text/event-stream" http://api.example.com/events
# -N: disabled output buffering, shows events as they arrive

# nginx config fix:
# proxy_buffering off;
# proxy_cache off;
# X-Accel-Buffering: no;  # or set header from app
```

Fix (server-side):
Add response header `X-Accel-Buffering: no` to disable nginx buffering.
Add `Cache-Control: no-cache` to prevent any caching layer from buffering.

Prevention:
Test SSE through your actual production proxy/CDN stack before launch.
Never strip `X-Accel-Buffering: no` headers in proxy configuration.

---

**SseEmitter Memory Leak (Spring MVC)**

Symptom:
Memory grows steadily with each new SSE subscriber. After running for hours,
OutOfMemoryError occurs with thousands of `SseEmitter` objects in heap.

Root Cause:
`SseEmitter` objects added to the emitters list but never removed when the
client disconnects. `onCompletion`, `onTimeout`, and `onError` handlers were
not registered, so disconnected emitters stay in the list forever.

Fix:
Always register all three handlers:

```java
emitter.onCompletion(() -> emitters.remove(emitter));
emitter.onTimeout(() -> emitters.remove(emitter));
emitter.onError(e -> emitters.remove(emitter));
```

Set reasonable timeout: `new SseEmitter(60_000L)` (60 seconds).

Prevention:
Use Spring WebFlux (`Flux<ServerSentEvent>`) for better backpressure handling.
Monitor emitter list size as a metric.

---

### 🔗 Related Keywords

- `WebSocket` — full-duplex alternative for bidirectional real-time communication
- `Long Polling` — older fallback technique before SSE was universal
- `HTTP/2` — SSE over HTTP/2 enables unlimited concurrent streams per connection
- `Reactive Programming` — Spring WebFlux `Flux<ServerSentEvent>` is the reactive SSE model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Server-push via open HTTP response with  │
│              │ text/event-stream content type           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Polling is wasteful; WebSocket is heavy  │
│ SOLVES       │ for server-to-client-only streams        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Auto-reconnect + Last-Event-ID resume    │
│              │ built-in — zero client reconnect code   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Notifications, feeds, LLM token stream,  │
│              │ live dashboards — one-way server push    │
├──────────────┼───────────────────────────────────────────┤
│ WATCH OUT    │ Text-only; nginx/proxy buffering breaks  │
│              │ it; SseEmitter leaks if not cleaned up   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HTTP streaming with auto-reconnect"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ WebSocket → Long Polling → HTTP/2        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're building an LLM streaming interface. The model generates tokens at variable speed — sometimes fast (simple completions), sometimes slow (complex reasoning). Design the complete SSE implementation that handles: token-by-token streaming, graceful completion signaling, error propagation mid-stream, user-initiated cancellation (stop generating), and reconnect resume (user's connection drops mid-response). What happens to the LLM inference if the user cancels?

**Q2.** 10,000 users are subscribed to a real-time inventory tracking system via SSE. An inventory update affects 3,000 of the 10,000 items tracked. A batch of 500 item updates arrives simultaneously. Compare two delivery strategies: (a) emit all 500 events immediately, (b) batch-group per user and emit once. Profile CPU, memory, and network impact for each at scale.
