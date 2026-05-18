---
id: NET-038
title: "HTTP/2 Multiplexing"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-030
used_by: NET-039, NET-048, NET-056
related: NET-030, NET-039, NET-048
tags:
  - networking
  - http2
  - multiplexing
  - performance
  - head-of-line-blocking
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/net/http2-multiplexing/
---

**⚡ TL;DR** - HTTP/2 multiplexing sends multiple requests
and responses concurrently over a single TCP connection
using independent streams. HTTP/1.1 sends one request at
a time per connection (head-of-line blocking), requiring
6-8 parallel connections to compensate. HTTP/2 eliminates
this with streams, solves HTTP/1.1 header bloat with
HPACK compression, and enables server push. The cost: one
packet loss stalls all streams (TCP head-of-line blocking).
HTTP/3 fixes that by replacing TCP with QUIC.

| #038 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | HTTP and HTTPS Basics (NET-030) | |
| **Used by:** | HTTP/3 and QUIC Protocol, gRPC and Protocol Buffers, HTTP Connection Management | |
| **Related:** | HTTP and HTTPS Basics, HTTP/3 and QUIC Protocol, gRPC | |

---

### 🔥 The Problem HTTP/2 Solves

A modern webpage requires 80+ assets: HTML, CSS files,
JavaScript bundles, images, fonts. HTTP/1.1 processes
one request at a time per connection. Browsers work
around this with 6-8 parallel connections per domain.
But even with 8 connections, if one resource is slow,
it blocks the connection it occupies. Developers invented
hacks: domain sharding (distribute assets across
subdomains to get more connections), sprite sheets
(combine images into one), and JavaScript bundling
(combine scripts into one) - all workarounds for HTTP/1.1
head-of-line blocking. HTTP/2 makes these hacks
unnecessary.

---

### 🧠 Intuition: Streams vs Connections

```
HTTP/1.1 - One request per connection:
  Connection 1: GET /page.html  → wait → response
  Connection 2: GET /style.css  → wait → response
  Connection 3: GET /script.js  → wait → response
  ...
  (6-8 connections, sequential within each)

HTTP/2 - Multiple streams on one connection:
  Connection 1:
    Stream 1: GET /page.html   →─────→ response (chunks)
    Stream 3: GET /style.css   →──→ response (fast)
    Stream 5: GET /script.js   →────→ response
    Stream 7: GET /image.png   →──────────→ response (slow)
    (all concurrent, interleaved at frame level)
```

---

### ⚙️ HTTP/2 Core Concepts

**Frames and Streams:**

```
Connection = single TCP connection
Stream     = bidirectional channel within connection
             Each stream has a unique stream ID (odd for client)
Frame      = smallest unit of communication
             Each frame has a stream ID + type + flags + payload

Frame types:
  HEADERS      = request/response headers (HPACK compressed)
  DATA         = body content
  SETTINGS     = negotiate parameters
  WINDOW_UPDATE= flow control (per-stream and connection)
  PING         = keepalive / RTT measurement
  RST_STREAM   = cancel specific stream (no full teardown)
  PUSH_PROMISE = server announces a push
  GOAWAY       = graceful connection shutdown
```

**Multiplexed frames on one TCP connection:**

```
TCP Connection:
─────────────────────────────────────────────────────────
  [S1 HEADERS] [S3 DATA] [S5 HEADERS] [S1 DATA] [S3 DATA]
   Request 1    Resp 2    Request 3    Resp 1     Resp 2
─────────────────────────────────────────────────────────
Frames from different streams interleaved freely
```

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    C->>S: SETTINGS (initial params)
    S->>C: SETTINGS ACK
    C->>S: HEADERS stream:1 (GET /page.html)
    C->>S: HEADERS stream:3 (GET /style.css)
    C->>S: HEADERS stream:5 (GET /image.png)
    S->>C: HEADERS stream:3 (200 OK)
    S->>C: DATA stream:3 (style.css content)
    S->>C: HEADERS stream:1 (200 OK)
    S->>C: DATA stream:1 (page.html chunk 1)
    S->>C: DATA stream:1 (page.html chunk 2)
    S->>C: HEADERS stream:5 (200 OK)
    S->>C: DATA stream:5 (image chunk 1)
```

---

### ⚙️ HPACK Header Compression

**HTTP/1.1 sends full headers on every request:**

```
GET /api/data HTTP/1.1
Host: api.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Cookie: session=abc123; _ga=GA1.2.123456

→ ~600 bytes of headers per request, even for 1-byte APIs
```

**HPACK sends only the diff using indexed header table:**

```
First request: build shared table, send all headers (~600B)
Second request: reference table entries
  [index 2] ← :method GET
  [index 5] ← :path /api/data
  [index 1] ← host: api.example.com
  → 4 bytes for headers that were 600 bytes before
  → 99%+ reduction for repeated requests to same endpoint
```

---

### ⚙️ Wrong vs Right: HTTP/1.1 Hacks That Hurt HTTP/2

```
# BAD: Apply HTTP/1.1 optimization patterns to HTTP/2

# 1. Domain sharding (HURTS HTTP/2!)
# HTTP/1.1 reason: 6 connections per domain, spread across domains
# HTTP/2 effect: creates multiple TCP connections, no benefit
#                loses connection-level multiplexing gain
#                MORE overhead, not less

# 2. Over-bundling JS/CSS (reduces cache granularity)
# HTTP/1.1 reason: 1 large file = 1 request (fewer roundtrips)
# HTTP/2 effect: 50 small files = 50 parallel streams
#                each file cached independently
#                one change invalidates only that file, not bundle

# GOOD: HTTP/2 native patterns

# 1. Server push (nginx):
# location / {
#   http2_push /critical.css;
#   http2_push /app.js;
# }
# → Server pushes CSS before browser asks for it
# → Browser has CSS ready when it parses the HTML

# 2. Unbundled assets + aggressive long-term caching
#    /assets/button.v3.js  (cache forever)
#    /assets/modal.v1.js   (cache forever, only refetch on change)
```

---

### ⚙️ HTTP/2 Flow Control (Two Levels)

```
HTTP/2 has TWO independent flow control windows:
  Connection-level: total across all streams combined
  Stream-level:     per individual stream

Both use WINDOW_UPDATE frames (like TCP rwnd but at app layer)
Default initial window: 65,535 bytes (same as TCP default)

# Sender must respect: min(stream_window, connection_window)
# Receiver sends WINDOW_UPDATE to grant more quota

# Python h2 library: increase initial window
conn.update_settings({
    h2.settings.SettingCodes.INITIAL_WINDOW_SIZE:
    4 * 1024 * 1024  # 4MB per stream
})
# Also update connection-level window:
conn.increment_flow_control_window(
    increment=4 * 1024 * 1024,
    stream_id=None)  # None = connection level
```

---

### ⚙️ The TCP Head-of-Line Blocking Problem

```
HTTP/2 solves HTTP-layer HOL blocking.
TCP-layer HOL blocking remains - and is amplified.

HTTP/1.1 HOL (per connection):
  6 connections × 1 stream = 6 independently moving streams
  1 lost packet on connection 1 only stalls connection 1

HTTP/2 HOL (connection-wide):
  1 connection × 50 streams = all streams share one TCP
  1 lost packet on the TCP connection stalls ALL 50 streams

Duration of stall:
  Linux default retransmit: 200ms (first timeout)
  → All 50 streams pause for 200ms per lost packet

Frequency:
  1% packet loss, 50 streams active
  = 50 streams × 0.01 loss probability per RTT
  = 50% chance one stream is stalled each RTT
  → HTTP/2 performs WORSE than HTTP/1.1 at > 2% loss

Solution: HTTP/3 / QUIC
  QUIC has per-stream packet sequencing
  Loss in stream 7 only stalls stream 7
```

---

### ⚙️ Enabling and Verifying HTTP/2

```bash
# Check if server supports HTTP/2
curl -I --http2 https://api.example.com
# Look for: HTTP/2 200

# Verbose HTTP/2 details:
curl -v --http2 https://api.example.com 2>&1 | grep "^*"
# * Using HTTP2, server supports multiplexing
# * h2 [:method: GET]

# ALPN negotiation (TLS extension for protocol selection):
echo | openssl s_client -connect example.com:443 \
  -alpn h2 2>&1 | grep "ALPN protocol"
# ALPN protocol: h2   ← HTTP/2 negotiated

# nginx config:
# server {
#   listen 443 ssl http2;  ← "http2" keyword enables it
#   ...
# }
```

---

### 🔬 Under the Hood

```
HTTP/2 binary frame format (9-byte header):
  Bytes 0-2:  Payload Length (24-bit = max 16MB per frame)
  Byte 3:     Type (0=DATA, 1=HEADERS, 4=SETTINGS, 8=WINDOW_UPDATE)
  Byte 4:     Flags (0x1=END_STREAM, 0x4=END_HEADERS)
  Bytes 5-8:  Stream ID (31-bit, MSB=0 reserved)
  Bytes 9+:   Payload

Stream ID allocation:
  Client initiates: odd numbers (1, 3, 5, 7...)
  Server push: even numbers (2, 4, 6, 8...)
  Connection-level frames (SETTINGS, PING, GOAWAY): stream 0

HPACK dynamic table:
  Size: SETTINGS_HEADER_TABLE_SIZE (default 4096 bytes)
  Contains recent headers indexed at 62+
  Static table: 61 predefined entries (:method GET = index 2)
  Huffman coding applied to values for additional compression
```

---

### 📐 Scale Considerations

```
HTTP/1.1 (6 parallel connections, 80 assets):
  ~14 sequential rounds (80 / 6)
  At 100ms RTT: 1,400ms minimum
  Memory per connection: ~32KB buffers × 6 = 192KB

HTTP/2 (1 connection, 80 concurrent streams):
  1-2 rounds (all parallel)
  At 100ms RTT: 100-200ms for all assets
  Memory: 1 TCP connection × ~256KB buffers = 256KB
  But: server must manage 80 stream states simultaneously

gRPC at scale (1,000 concurrent RPCs):
  HTTP/2: 1 connection per server, 1,000 streams
  vs HTTP/1.1: 1,000 connections
  Memory savings: 1,000× fewer kernel TCP structures
  BUT: one TCP timeout stalls ALL 1,000 RPCs
  Production gRPC uses multiple connections as insurance
```

---

### 🧭 Decision Guide

```
Enable HTTP/2?
  YES for all public HTTPS web services (near-zero cost)
  YES for gRPC (requires HTTP/2)
  YES for internal APIs if clients support it

HTTP/2 vs HTTP/3?
  HTTP/2: mature, universally supported, use by default
  HTTP/3: better for mobile/lossy networks (Netflix, Google)
          requires QUIC (UDP-based), firewall concerns
          growing adoption (~28% of web traffic 2024)

When HTTP/2 hurts:
  High packet loss (>2%): TCP HOL blocking amplified
  Very small request volumes: overhead of HPACK table
  Behind proxies that don't support HTTP/2 end-to-end

Interview one-liner:
  "HTTP/2 multiplexes streams on one TCP connection,
  eliminating HTTP/1.1 HOL blocking. HPACK compresses
  repeated headers 99%+. Limitation: TCP-level HOL
  blocking - one lost packet stalls all streams.
  HTTP/3 fixes this with QUIC's per-stream transport."
```
---
