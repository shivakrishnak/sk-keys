---
id: API-036
title: "HTTP/2 Multiplexing and Server Push"
category: "HTTP & APIs"
tier: tier-2-networking-security
folder: API-http-apis
difficulty: ★★★
depends_on: API-001, API-003
used_by: API-053, API-065
related: API-053, API-031, API-065
tags:
  - http2
  - multiplexing
  - server-push
  - hpack
  - performance
status: complete
version: 4
layout: default
parent: "HTTP & APIs"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/api/http-2-multiplexing-and-server-push/
---

⚡ TL;DR - HTTP/2 solves HTTP/1.1's head-of-line
blocking and connection overhead by multiplexing
multiple concurrent request-response streams over a
single TCP connection; HPACK header compression reduces
repeated header bytes (cookies, auth headers) by up
to 90%; Server Push allows servers to proactively send
resources the client will need before the client asks;
HTTP/2 is binary (not text), requires TLS in practice,
and is transparent to application code - the performance
benefits are protocol-level, not requiring API changes.

---

| #036 | Category: HTTP & APIs | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1 Fundamentals, HTTP Response Headers | |
| **Used by:** | HTTP/3 and QUIC, HTTP Keep-Alive and Connection Reuse | |
| **Related:** | HTTP/3 and QUIC, HTTP Compression, HTTP Keep-Alive | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
HTTP/1.1 has two critical performance limitations:

(1) **Head-of-line blocking:** One TCP connection
handles one request at a time. Sending a large response
(image, JS bundle) blocks all other requests on that
connection until it completes. The browser opens 6
parallel TCP connections per domain as a workaround.

(2) **Header redundancy:** Every HTTP/1.1 request sends
the full headers: `User-Agent`, `Accept`, `Accept-Language`,
`Cookie` (potentially thousands of bytes), `Authorization`
- all repeated verbatim on every request. A 2 KB cookie
sent on 100 requests = 200 KB of pure overhead.

**THE BREAKING POINT:**
Google's SPDY protocol (2009) demonstrated that
multiplexing multiple HTTP requests over one TCP
connection reduced page load times by 55%. The browser's
hack of 6 parallel connections was a workaround for
HTTP/1.1's single-request limitation. With proper
multiplexing, 1 connection is faster than 6.

**THE INVENTION MOMENT:**
HTTP/2 (RFC 7540, 2015), standardized from SPDY, introduced:
binary framing (not text), stream multiplexing (many
requests per connection), HPACK header compression,
and server push. All visible to application code as
standard HTTP.

---

### 📘 Textbook Definition

HTTP/2 (RFC 7540) is the second major version of HTTP,
introducing: **Binary framing:** all HTTP/2 messages
are encoded as binary frames (not text), enabling
efficient parsing and multiplexing. **Stream
multiplexing:** a single TCP connection carries multiple
concurrent request-response exchanges (streams), each
with a numeric ID. Streams are independent; a slow
stream does not block others. **HPACK header compression
(RFC 7541):** headers are encoded using a static table
(common header name-value pairs), a dynamic table
(recently used headers), and Huffman encoding; repeated
headers (Authorization, Cookie, User-Agent) are compressed
to 1-2 bytes per request. **Server Push:** the server
can send resources (CSS, JS) before the client requests
them, using `PUSH_PROMISE` frames. **Flow control:**
per-stream and per-connection backpressure using WINDOW_UPDATE
frames. **TLS:** required in practice (browsers only
support HTTP/2 over TLS, h2; plaintext h2c theoretically
exists but no browser implements it).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HTTP/2 is like upgrading from a single-lane road to
a multi-lane highway: many cars (requests) travel
simultaneously on the same road (TCP connection), with
a carpool express lane (server push).

**One analogy:**
> HTTP/1.1 is ordering at a restaurant with one waiter
> who goes to the kitchen after each order and waits
> for the food before taking the next order. If a slow
> dish (large image) is in the kitchen, all other
> customers wait. HTTP/2 is a kitchen order ticket system:
> all orders go in simultaneously, kitchen works on all
> of them in parallel, items arrive as ready.

**One insight:**
HTTP/2 is transparent to application code. You do not
change your API routes, controllers, or HTTP client
code. The protocol upgrade happens at the TLS/transport
layer. A server that supports HTTP/2 automatically
negotiates it via ALPN (Application-Layer Protocol
Negotiation) during TLS handshake. Your FastAPI/Express
app works unchanged over HTTP/2.

---

### 🔩 First Principles Explanation

**HTTP/1.1 vs HTTP/2 CONNECTION MODEL:**
```
HTTP/1.1 (6 connections per domain):
Client                         Server
  |--TCP1: GET /style.css ----->|
  |  [waiting for response]     |
  |--TCP2: GET /app.js -------->|
  |  [waiting for response]     |
  |--TCP3: GET /image.jpg ----->|
  |  [waiting for response]     |
  [3 more connections]
  ← 6 TCP handshakes × 3-way each = 18 RTTs of overhead

HTTP/2 (1 connection, multiple streams):
Client                         Server
  |--TCP1: Stream 1: /style.css>|
  |--TCP1: Stream 3: /app.js -->|
  |--TCP1: Stream 5: /image.jpg>|
  |<-TCP1: Stream 3 response --|
  |<-TCP1: Stream 1 response --|
  |<-TCP1: Stream 5 response --|
  ← 1 TCP handshake = 1-2 RTTs total
  ← Responses arrive out of order (no blocking)
```

**HPACK HEADER COMPRESSION:**
```
HTTP/1.1 Request #1 (full headers, ~1200 bytes):
:method: GET
:path: /api/users
:authority: api.example.com
:scheme: https
user-agent: Mozilla/5.0 (...)
accept: application/json
accept-encoding: gzip, deflate, br
accept-language: en-US,en;q=0.9
cookie: session=abc123; preferences=dark-mode
authorization: Bearer eyJhbGciOiJSUzI1NiJ9...

HTTP/2 Request #2 (HPACK compressed, ~20 bytes):
:path: /api/orders  ← indexed reference to other fields
                    ← Authorization: compressed to 1 byte
                    ← Cookie: compressed to 2 bytes
                    ← All others: indexed from prior request
```

**HTTP/2 STREAM MULTIPLEXING:**
```
Connection: single TCP connection
Streams: each request/response pair is a stream
Stream IDs: client-initiated streams are odd (1,3,5,...)
            server push streams are even (2,4,6,...)
Frame types:
  HEADERS: request/response header block
  DATA: request/response body
  PUSH_PROMISE: server announces a push
  SETTINGS: connection configuration
  WINDOW_UPDATE: flow control
  PING: keepalive
  RST_STREAM: abort a stream
  GOAWAY: graceful connection shutdown
```

---

### 🧪 Thought Experiment

**SCENARIO: Web page with 20 API calls on load**

**HTTP/1.1 with 6 connections:**
- 20 requests dispatched; 6 run in parallel (browser limit)
- Each batch of 6 requests: TCP connection + TLS + request
- Batches: 4 batches × ~50ms per batch = ~200ms overhead
- Plus actual response times
- Total connection overhead: 4 × 3-way TCP + 4 × TLS
  = ~8 round trips just for connections

**HTTP/2 with 1 connection:**
- 1 TCP connection + 1 TLS handshake upfront: ~50ms
- 20 requests sent simultaneously over streams 1,3,5,...
- Responses arrive as ready (no head-of-line blocking)
- Connection overhead: 1 TCP + 1 TLS = ~2 round trips
- Savings: ~6 round trips = ~150ms on 25ms RTT connection

**For API-heavy SPAs, HTTP/2 reduces initial load overhead
by 50-70% on high-latency connections.**

---

### 🧠 Mental Model / Analogy

> HPACK header compression is like a shared codebook.
> The first time you say "Authorization: Bearer
> eyJhbGciOiJSUzI1NiJ9..." (a long token), both sides
> record "header entry #62 = this whole thing." On
> subsequent requests, instead of sending the full token,
> you just say "#62" (1-2 bytes). The server looks up
> #62 in the shared table and knows the full header.
> Both static (predefined common headers) and dynamic
> (recently sent headers) tables are maintained.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
HTTP/2 makes web requests faster. The main trick:
instead of using 6 separate connections to load a web
page's resources in parallel, it uses 1 connection
that carries all requests at once. Less connection
overhead = faster page loads.

**Level 2 - How to use it (junior developer):**
Enable HTTP/2 in your web server (Nginx: `listen 443
ssl http2;`). HTTP/2 requires TLS. Application code
is unchanged - the protocol negotiation is transparent.
Your FastAPI, Express, or Spring Boot app works the
same way.

**Level 3 - How it works (mid-level engineer):**
HTTP/2 negotiation: client sends TLS ClientHello with
ALPN extension (`h2` for HTTP/2, `http/1.1` as fallback).
Server selects `h2` if supported. All subsequent
communication is HTTP/2 binary frames. Each request-
response pair is a stream with an ID. HPACK compresses
headers against a dynamic table shared for the connection
lifetime. Server Push: server sends `PUSH_PROMISE` frame
before sending the pushed resource; client can reject
with `RST_STREAM` if it already has the resource cached.

**Level 4 - Why it was designed this way (senior/staff):**
HTTP/2's binary framing (vs HTTP/1.1 text) was chosen
for efficiency: text parsing requires scanning for
delimiters (`\r\n`); binary frames have explicit length
fields (O(1) parsing). The binary format also enables
multiplexing: streams are interleaved at the frame
level (each frame has a stream ID), which text encoding
cannot express. HPACK's dynamic table is connection-
scoped (not shared across connections), which enables
stateful compression without TLS key extraction attacks
(like CRIME on HTTP/1.1's DEFLATE compression).

**Level 5 - Mastery (distinguished engineer):**
HTTP/2 eliminates HTTP/1.1 head-of-line blocking at
the HTTP layer but HTTP/2 still has TCP-level head-of-
line blocking: a lost TCP packet stalls ALL streams
until retransmission. On high-loss networks (mobile),
HTTP/2 can actually perform worse than HTTP/1.1 with
6 connections (because the 6 connections are independent
TCP streams - a loss on one does not block others).
This motivated HTTP/3 (QUIC): QUIC uses UDP with its
own reliable delivery per stream, eliminating TCP-level
HOL blocking. HTTP/2 is optimal for low-loss wired
connections; HTTP/3 wins on mobile and high-latency
networks. Server Push was deprecated in Chrome in 2022
(added complexity, rarely beneficial; ESI and preload
hints are better alternatives).

---

### ⚙️ How It Works (Mechanism)

**Nginx HTTP/2 configuration:**

```nginx
server {
    listen 443 ssl http2;  # Enable HTTP/2
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/api.crt;
    ssl_certificate_key /etc/ssl/private/api.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    # HPACK benefits from persistent connections
    keepalive_timeout 65;

    # HTTP/2 push (deprecated but shown for reference)
    # location = /index.html {
    #     http2_push /style.css;
    #     http2_push /app.js;
    # }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;  # proxy to backend via HTTP/1.1
        # (HTTP/2 to Nginx; Nginx proxies as HTTP/1.1 to app)
    }
}
```

```mermaid
sequenceDiagram
    participant C as Client
    participant N as Nginx (HTTP/2)
    participant B as Backend (HTTP/1.1)
    C->>N: TLS ClientHello (ALPN: h2)
    N-->>C: TLS ServerHello (ALPN: h2)
    Note over C,N: HTTP/2 negotiated
    C->>N: Stream 1: GET /api/users
    C->>N: Stream 3: GET /api/orders
    C->>N: Stream 5: GET /api/products
    N->>B: HTTP/1.1 GET /api/users
    N->>B: HTTP/1.1 GET /api/orders
    N->>B: HTTP/1.1 GET /api/products
    B-->>N: Response: users
    B-->>N: Response: orders
    B-->>N: Response: products
    N-->>C: Stream 3: orders response
    N-->>C: Stream 1: users response
    N-->>C: Stream 5: products response
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Verifying HTTP/2 in production:**

```bash
# Check if server supports HTTP/2
curl -vso /dev/null --http2 https://api.example.com/health
# Look for: "Using HTTP2, server supports HTTP2"

# Check ALPN negotiation
openssl s_client -connect api.example.com:443 \
  -alpn h2 2>&1 | grep ALPN
# Should show: ALPN protocol: h2

# Compare HTTP/1.1 vs HTTP/2 performance
time curl --http1.1 https://api.example.com/data
time curl --http2  https://api.example.com/data
# HTTP/2 should be faster for repeated requests
# (connection reuse + header compression)
```

---

### 💻 Code Example

**Example 1 - BAD: HTTP/2 anti-patterns**

```python
# BAD: Opening new connection per request (defeats HTTP/2)
import httpx

def fetch_all_data_bad():
    results = []
    for url in urls:
        # New client per request = new TCP/TLS = no HTTP/2 benefit
        with httpx.Client() as client:
            results.append(client.get(url))
    return results

# GOOD: Reuse client (HTTP/2 multiplexes over one connection)
def fetch_all_data_good():
    with httpx.Client(http2=True) as client:
        # All requests use the same HTTP/2 connection
        # Sent concurrently via stream multiplexing
        import asyncio
        return asyncio.gather(*[
            client.get(url) for url in urls
        ])
```

---

**Example 2 - HTTP/2 gRPC benefit**

```
gRPC uses HTTP/2 natively:
- Each RPC call is an HTTP/2 stream
- Bidirectional streaming: both client and server can
  send messages at any time on the same stream
- Multiplexing: 100 concurrent RPC calls over 1 TCP
  connection (vs 100 separate connections in HTTP/1.1)
- HPACK compresses gRPC metadata headers across calls
- Result: gRPC achieves higher throughput than REST/HTTP
  in part due to HTTP/2 efficiency
```

---

### ⚖️ Comparison Table

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|:---|:---|:---|:---|
| Encoding | Text | Binary frames | Binary (QUIC) |
| Connections | 6 per domain (browser) | 1 per server | 1 per server |
| Multiplexing | No (pipelining, broken) | Yes (streams) | Yes (QUIC streams) |
| Header compression | None | HPACK | QPACK |
| HOL blocking | HTTP + TCP level | TCP level only | None (QUIC) |
| Server Push | No | Yes (deprecated) | Yes |
| TLS | Optional | Required (browsers) | Always (QUIC) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| HTTP/2 requires code changes | Zero application code changes. HTTP/2 is negotiated at the TLS layer (ALPN). Your HTTP handlers work unchanged. Only server configuration changes (Nginx `listen ... http2;`). |
| HTTP/2 Server Push is widely beneficial | Server Push was deprecated by Chrome in 2022 because it frequently pushed resources already in the browser cache, wasting bandwidth. HTTP preload hints (`<link rel="preload">`) and Early Hints (103 status code) are better alternatives. |
| HTTP/2 eliminates all latency | HTTP/2 eliminates HTTP-layer HOL blocking. TCP-level HOL blocking remains: a lost TCP packet stalls all streams. On high-loss networks, HTTP/3 (QUIC over UDP) is needed. |
| 1 HTTP/2 connection is always better than multiple | For microservices, a single HTTP/2 connection from API gateway to backend may become a bottleneck at very high throughput (single TCP stream). Use connection pooling with multiple HTTP/2 connections for high-throughput microservice communication. |

---

### 🚨 Failure Modes & Diagnosis

**HTTP/2 not active despite server configuration**

**Symptom:** Client requests show HTTP/1.1 instead of HTTP/2 in DevTools. `curl --http2` shows "Using HTTP1.1."

**Root Cause:** Browser and HTTP clients only support HTTP/2 over TLS. If TLS is not configured, or ALPN is not set correctly, the server falls back to HTTP/1.1.

**Diagnostic:**
```bash
# Check TLS and ALPN
openssl s_client -connect api.example.com:443 \
  -alpn h2 2>&1 | grep -E "ALPN|Protocol"
# Expected: ALPN protocol: h2
# If shows: http/1.1 → server not offering h2 in ALPN

# Check Nginx config
nginx -T | grep "listen.*http2"
# Should show: listen 443 ssl http2;
```

**Fix:** Ensure `http2` keyword is in Nginx `listen` directive. Nginx 1.25.1+ uses `http2 on;` directive instead. Verify TLS certificates are valid (ALPN extension requires valid TLS).

---

**HTTP/2 RST_STREAM floods (rapid reset attack)**

**Symptom:** Server CPU spikes. Nginx error log shows
many `RST_STREAM` frames. Server performance degrades.

**Root Cause:** HTTP/2 Rapid Reset Attack (CVE-2023-44487).
Attacker opens many streams and immediately resets them,
generating server-side work without completing requests.

**Fix:** Update Nginx/HAProxy/Apache to patched version.
Configure `http2_max_concurrent_streams` limit (Nginx
default: 128). Rate-limit new connections per IP.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HTTP/1.1 Fundamentals` - baseline protocol HTTP/2 improves
- `HTTP Response Headers` - headers being compressed

**Builds On This (learn these next):**
- `HTTP/3 and QUIC for APIs` - eliminating TCP-level HOL blocking
- `HTTP Keep-Alive and Connection Reuse` - connection persistence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ HTTP upgrade: binary framing, stream      │
│              │ multiplexing, HPACK header compression,   │
│              │ server push over single TLS connection    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ HTTP/1.1 head-of-line blocking; header    │
│ SOLVES       │ redundancy (repeated cookies/auth per req)│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Zero app code changes; TLS config only;   │
│              │ HTTP/2 still has TCP HOL blocking         │
├──────────────┼───────────────────────────────────────────┤
│ GAINS        │ 50-70% fewer connections; HPACK: 80-90%   │
│              │ header compression; simultaneous streams  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ New connection per request (defeats reuse);│
│              │ HTTP/2 Server Push (deprecated, use hints)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "1 TCP connection, N concurrent streams;  │
│              │ HPACK compresses repeated headers to 0."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HTTP/3 and QUIC → gRPC (uses HTTP/2)      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. HTTP/2 multiplexes many requests over one TCP
   connection, eliminating HTTP/1.1 head-of-line
   blocking. Zero application code changes required.
2. HPACK compresses repeated headers (Cookie, Authorization)
   to 1-2 bytes per request after the first. Significant
   bandwidth savings for auth-heavy API requests.
3. HTTP/2 still has TCP-level HOL blocking. HTTP/3
   (QUIC) solves this. On high-loss mobile networks,
   HTTP/3 is needed for maximum performance.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Protocol improvements are transparent to applications."
HTTP/2 is the canonical example: application code sees
HTTP methods and headers; the binary framing and
multiplexing are invisible. This pattern appears in:
TLS (application sees a socket; encryption is transport-
layer); gzip compression (application sends bytes;
compression is middleware); TCP itself (application
sees a byte stream; reliability and ordering are
transport-layer). Good protocol design creates layers
with clean separation. Application developers benefit
from protocol improvements without rewriting their code.

**Where else this pattern applies:**
- gRPC uses HTTP/2 natively: gRPC streams are HTTP/2
  streams; gRPC gets HTTP/2 performance benefits
  automatically
- QUIC: used by HTTP/3, QUIC protocol handles reliability
  per-stream (not per-connection like TCP)

---

### 💡 The Surprising Truth

HTTP/2 was designed with Server Push as a key feature,
allowing servers to proactively push CSS and JavaScript
before the browser requests them. Google promoted Server
Push heavily as a performance feature. In 2022, Google
Chrome deprecated HTTP/2 Server Push and removed support.
The reason: browsers frequently already had the pushed
resources cached. Server Push had no way to know what
the client had cached (that information is private),
so it re-sent resources clients already had, wasting
bandwidth. The alternative - HTTP `<link rel="preload">`
hints and Early Hints (103 status code) - achieves the
same goal with browser cache awareness. This is a rare
case of a major protocol feature being removed after
deployment.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** HTTP/2 stream multiplexing: how multiple
   requests share one TCP connection and why it is
   faster than 6 separate HTTP/1.1 connections.
2. **CONFIGURE** HTTP/2 in Nginx and verify it is active
   using `curl --http2` and DevTools.
3. **DESCRIBE** HPACK header compression: static table,
   dynamic table, and why it is connection-scoped.
4. **COMPARE** HTTP/2 vs HTTP/3: which HOL blocking
   problem remains in HTTP/2 and how HTTP/3 solves it.
5. **EXPLAIN** Why HTTP/2 Server Push was deprecated and
   what the recommended alternative is.

---

### 🎯 Interview Deep-Dive

**Q1: What is head-of-line blocking in HTTP/1.1 and
how does HTTP/2 solve it?**

*Why they ask:* Tests protocol depth and performance
understanding.

*Strong answer includes:*
- HTTP/1.1 head-of-line blocking: one request per TCP
  connection at a time. A slow response (large image,
  slow endpoint) blocks all subsequent requests on
  that connection.
- Browser workaround: 6 parallel TCP connections per
  domain. But each connection has TCP + TLS handshake
  overhead.
- HTTP/2 solution: stream multiplexing. One TCP connection
  carries many independent request-response streams
  simultaneously. A slow stream does not block others.
- Remaining HOL blocking: TCP-level. A lost TCP packet
  stalls ALL streams until retransmission. HTTP/3 (QUIC)
  solves this.

**Q2: What is HPACK and why is it important for API
performance?**

*Why they ask:* Tests HTTP/2 depth.

*Strong answer includes:*
- HPACK: HTTP/2 header compression. Two tables: static
  (61 common header name-value pairs predefined) and
  dynamic (recently sent headers for this connection).
  Huffman encoding for literal strings.
- Importance: HTTP/1.1 repeats full headers on every
  request. Authorization (JWT: 200-400 bytes), Cookie
  (session + preferences: 500-2000 bytes), User-Agent
  (~100 bytes) - sent verbatim on EVERY request.
- With HPACK: after the first request, Authorization
  is added to the dynamic table. Subsequent requests
  reference it as a 1-2 byte index. 2000 bytes → 2 bytes.
- Impact: 80-90% header size reduction for auth-heavy
  API traffic. Significant bandwidth and latency savings.

**Q3: Does migrating to HTTP/2 require changing your
API code?**

*Why they ask:* Tests practical deployment knowledge.

*Strong answer includes:*
- No application code changes required. HTTP/2 is
  negotiated at the TLS layer via ALPN. The server
  sends `ALPN: h2` in the TLS handshake; client and
  server speak HTTP/2 from that point.
- Required: (1) TLS enabled (required for browser HTTP/2);
  (2) Server configured for HTTP/2 (Nginx `http2` in
  listen directive; Apache `Protocols h2 http/1.1`).
- Client (httpx, fetch, curl): automatically uses
  HTTP/2 if available. Explicit for testing: `curl
  --http2 https://api.example.com`.
- Exception: HTTP/2 between services in a cluster
  (microservices) may require explicit configuration
  in service mesh (Istio, Linkerd). But HTTP/2 from
  browser to API gateway is transparent.
