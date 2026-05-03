---
layout: default
title: "Network Latency Optimization"
parent: "Networking"
nav_order: 190
permalink: /networking/network-latency-optimization/
number: "0190"
category: Networking
difficulty: ★★★
depends_on: TCP, HTTP & APIs, DNS, CDN, TLS/SSL, Bandwidth vs Throughput
used_by: System Design, Platform & Modern SWE, Observability & SRE, Cloud — AWS
related: CDN, DNS, TCP, QUIC, TLS/SSL, HTTP & APIs, Bandwidth vs Throughput
tags:
  - networking
  - latency
  - performance
  - optimization
  - ttfb
  - tcp
  - http2
---

# 190 — Network Latency Optimization

⚡ TL;DR — Latency optimisation is systematic: (1) move content closer to users (CDN, edge compute); (2) reduce connection setup cost (persistent HTTP/keep-alive, HTTP/2, QUIC, 0-RTT); (3) optimise TLS handshake (TLS 1.3, session resumption, OCSP stapling); (4) reduce payload size (compression, binary protocols); (5) tune OS/TCP (BBR, tcp_nodelay, buffer sizes). Understanding TTFB (Time to First Byte) and breaking it into components is the key diagnostic tool.

---

### 🔥 The Problem This Solves

A website takes 3 seconds to load for users in Tokyo despite being "fast" for users in New York. A microservice p99 latency is 500ms despite p50 being 10ms. An API gateway adds 200ms to every request. These are symptoms of latency problems that require systematic diagnosis and multi-layer fixes — not just "add more servers."

---

### 📘 Textbook Definition

**Network latency optimization** is the practice of reducing end-to-end response time by identifying and eliminating latency sources at each layer of the network stack: physical distance (propagation), connection establishment (TCP handshake, TLS handshake), protocol overhead (HTTP/1.1 head-of-line blocking), payload size (uncompressed responses), and OS/kernel settings (socket buffers, congestion control).

**TTFB (Time to First Byte):** The time from the client initiating a request to receiving the first byte of the response. TTFB = DNS resolution + TCP handshake + TLS handshake + server processing + first byte. A high TTFB is a clear indicator of network or server-side latency issues.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Latency optimisation: get the server closer (CDN), reduce handshake costs (HTTP/2, TLS 1.3, 0-RTT), compress payloads, and tune TCP settings — each layer multiplicatively improves performance.

**One analogy:**
> Optimising network latency is like optimising a bank visit. CDN = open a branch near you (reduce travel). Persistent connections = have a dedicated teller (no queue each time). TLS session resumption = the teller remembers you (skip ID check). HTTP/2 multiplexing = process multiple requests simultaneously at the counter. Compression = submit a form instead of explaining everything verbally.

---

### 🔩 First Principles Explanation

**LATENCY ANATOMY — TTFB BREAKDOWN:**
```
User types URL → browser shows page:

DNS resolution:          20-100ms (cached: 0ms; recursive: 20-100ms)
TCP handshake:           1 × RTT (SYN → SYN-ACK → ACK)
TLS 1.2 handshake:      2 × RTT (2 round trips for full handshake)
TLS 1.3 handshake:      1 × RTT (0-RTT on resumption: 0 RTT)
HTTP request:            1 × RTT (GET → response)
Server processing:       varies (10ms - 1s)

Total (TLS 1.2, no cache, 100ms RTT):
  DNS: 50ms + TCP: 100ms + TLS: 200ms + HTTP: 100ms + server: 50ms
  = 500ms TTFB

With CDN (10ms RTT to edge, TLS 1.3):
  DNS: 5ms + TCP: 10ms + TLS: 10ms + HTTP: 10ms + server: 50ms
  = 85ms TTFB (6× improvement)

HTTP/2 on same CDN (connection reused):
  No DNS, no TCP, no TLS (connection exists)
  HTTP: 10ms + server: 50ms = 60ms TTFB
```

**OPTIMISATION TECHNIQUES:**

*1. CDN / Edge Proximity:*
```
Without CDN (London server, Sydney user, 300ms RTT):
  All DNS + TCP + TLS at 300ms RTT → 1200ms+ overhead

With CDN (Sydney PoP, 5ms RTT to edge):
  DNS + TCP + TLS at 5ms RTT → 20ms overhead
  CDN → origin: 300ms RTT (but only for cache miss)
  Cache HIT: 5ms RTT total
```

*2. Connection Reuse (HTTP Keep-Alive / HTTP/2):*
```
HTTP/1.0: new TCP connection per request
  3-way handshake + TLS (1-2 RTT) for EVERY request
  10 resources = 10 × (1 RTT TCP + 1.5 RTT TLS) = 25 RTTs

HTTP/1.1 Keep-Alive: reuse TCP connection
  First request: 2.5 RTT (TCP + TLS + HTTP)
  Subsequent: 1 RTT each
  10 resources = 2.5 + 9 = 11.5 RTTs (2× improvement)

HTTP/2: multiplexed streams on single connection
  10 resources in parallel over 1 connection
  Total: 2.5 RTT (TCP + TLS + all resources in parallel)
  10× improvement in connection overhead
```

*3. TLS Optimisation:*
```
TLS 1.2: 2-RTT handshake (expensive)
TLS 1.3: 1-RTT handshake (50% faster)
TLS 1.3 0-RTT: 0-RTT on session resumption
  (data sent with first message, no handshake round trip)
  Trade-off: replay attacks possible; use only for idempotent requests

Session tickets / OCSP stapling:
  Session ticket: skip certificate re-validation on reconnect
  OCSP stapling: server includes cert revocation status in handshake
    (client doesn't need separate OCSP lookup = -1 RTT)
```

*4. Protocol Optimisation:*
```
HTTP/1.1 Head-of-Line Blocking:
  Request 1 (large): must complete before Request 2 starts
  
HTTP/2 Multiplexing:
  All requests in parallel streams on one connection
  Request 1 and 2 both in-flight simultaneously
  Stream priority: critical CSS/JS first, images later
  Server push: server sends CSS before client asks for it
  
HTTP/3 / QUIC:
  UDP-based: eliminates TCP head-of-line blocking
  (TCP: one lost packet blocks all streams;
   QUIC: one lost QUIC packet only blocks its stream)
  0-RTT on reconnect (built-in to QUIC)
  Connection migration: maintains connection across IP changes (mobile)
```

*5. Payload Reduction:*
```
Gzip/Brotli compression:
  Typical HTML: 100 KB → 20 KB (80% reduction)
  JS bundle: 500 KB → 150 KB
  Savings: 350 KB × 1 Mbps / 8 = 2.8 seconds less transfer time
  Brotli: ~20% better than gzip for text; similar CPU cost

Content optimisation:
  Critical CSS inline (eliminates render-blocking request)
  Lazy loading images (defer non-visible images)
  Resource hints: <link rel="preconnect"> (DNS + TCP + TLS ahead of use)
  DNS prefetch: <link rel="dns-prefetch"> (DNS only)
```

*6. TCP/OS Tuning:*
```bash
# Enable TCP BBR (better throughput, lower latency)
sysctl -w net.ipv4.tcp_congestion_control=bbr

# Disable Nagle's algorithm for interactive protocols (SSH, gaming)
# Nagle: batches small packets → adds up to 40ms latency
sysctl -w net.ipv4.tcp_nodelay=1
# (per-socket: socket.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1))

# Reduce TIME_WAIT duration (frees ports faster)
sysctl -w net.ipv4.tcp_fin_timeout=30

# Tune socket buffers for high-BDP paths
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"

# Enable TCP Fast Open (skip one RTT for repeat connections)
sysctl -w net.ipv4.tcp_fastopen=3
```

---

### 🧪 Thought Experiment

**WATERFALL ANALYSIS:**
A web page has 20 resources. Without optimisation: serial loading with 100ms RTT. Each resource = 1 RTT = 100ms. Total: 2,000ms just in network time.

With HTTP/2 + CDN:
- All 20 resources in parallel: 1 × 100ms base RTT = 100ms (+ server processing)
- CDN: RTT = 10ms → 10ms for all 20 resources in parallel
- Total: ~60ms (10ms network + 50ms server processing)

Result: 2000ms → 60ms from these two changes alone (33× improvement).

---

### 🧠 Mental Model / Analogy

> Network latency optimisation is like optimising a restaurant order:
> 1. Open a local branch (CDN) — no cross-city travel
> 2. Pre-order online (TLS 0-RTT) — order taken before you arrive
> 3. Order everything at once (HTTP/2 multiplexing) — not item by item
> 4. Compress the menu (smaller payloads) — only the dishes you want
> 5. Keep your usual table (connection reuse) — no wait for a table

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Get servers closer to users (CDN). Reuse connections (HTTP/2). Compress data (gzip). These three changes cover 80% of network latency wins.

**Level 2:** Use Chrome DevTools → Network tab. Sort by TTFB. Identify: long DNS resolution (use DNS prefetch), long TLS (upgrade to TLS 1.3, session resumption), many serial requests (HTTP/2), large responses (compress). Use `curl -w` to measure TTFB from different locations.

**Level 3:** Connection-level tuning: HTTP/2 prioritisation (critical path resources get high priority streams), server push (push CSS with HTML response), preload (`<link rel="preload">`). TCP_NODELAY for APIs (disable Nagle). QUIC/HTTP/3 for mobile users (handles packet loss better, connection migration). Service mesh: reduce per-hop TLS overhead with mTLS session reuse.

**Level 4:** Tail latency reduction: at p99, latency spikes are often caused by OS scheduling jitter, GC pauses, connection pool exhaustion, or cold TCP connections. Mitigation: connection pool pre-warming (establish connections before traffic, not on first request), hedged requests (send same request to two backends, take first response, cancel second), circuit breakers (fail fast instead of waiting for timeout). The key insight: median latency and tail latency have different root causes — median is network-bound; p99 is often application or scheduling-bound.

---

### ⚙️ How It Works (Mechanism)

```bash
# Measure TTFB breakdown with curl
curl -w "\n\
DNS:        %{time_namelookup}s\n\
TCP:        %{time_connect}s\n\
TLS:        %{time_appconnect}s\n\
TTFB:       %{time_starttransfer}s\n\
Total:      %{time_total}s\n\
Size:       %{size_download} bytes\n" \
  -o /dev/null -s https://example.com

# Check TLS version and cipher
openssl s_client -connect example.com:443 2>/dev/null | \
  grep -E "Protocol|Cipher"

# Test HTTP/2 support
curl -I --http2 https://example.com | grep -i "HTTP/"
# HTTP/2 200 ← server supports HTTP/2

# Check compression
curl -H "Accept-Encoding: gzip, br" -I https://example.com | \
  grep -i "content-encoding"
# content-encoding: br ← Brotli compression

# Measure from multiple locations (use online tools or VPN)
# WebPageTest: https://www.webpagetest.org
# GTmetrix: https://gtmetrix.com

# DNS prefetch resolve time
time dig example.com @8.8.8.8
# vs cached:
time dig example.com @8.8.8.8  # second call (cached in resolver)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Optimised Request Flow (CDN + HTTP/2 + TLS 1.3):

t=0ms:   Browser cache miss, needs index.html
t=0ms:   DNS lookup (cached from previous: 0ms)
t=5ms:   TCP connect to CDN edge (5ms RTT)
t=10ms:  TLS 1.3 handshake complete (1 RTT = 5ms)
         (TLS 1.3 0-RTT on reconnect: would be 5ms total)
t=15ms:  HTTP/2 GET /index.html (multiplexed)
         Browser also sends: GET /style.css, GET /app.js
         All 3 in parallel on same connection
t=25ms:  All 3 responses received (cache HIT at CDN)
t=25ms:  Browser starts parsing, finds 10 more resources
t=25ms:  GET all 10 in parallel (HTTP/2 streams)
t=35ms:  All resources received
t=45ms:  Page rendered (10ms JS execution)

Total: 45ms (vs 2000ms+ with HTTP/1.1, no CDN, TLS 1.2)
```

---

### 💻 Code Example

```python
import urllib.request
import time
import gzip
import json
from typing import Optional

def benchmark_endpoint(url: str, n: int = 10) -> dict:
    """Benchmark TTFB and download time for an endpoint."""
    latencies = []
    
    for _ in range(n):
        req = urllib.request.Request(url)
        req.add_header("Accept-Encoding", "gzip, br")
        
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=10) as resp:
            ttfb = time.perf_counter() - start
            body = resp.read()  # download full response
        total = time.perf_counter() - start
        
        latencies.append({
            "ttfb_ms": ttfb * 1000,
            "total_ms": total * 1000,
            "size_bytes": len(body),
            "encoding": resp.headers.get("Content-Encoding", "none"),
            "http_version": resp.headers.get("Via", ""),
        })
        time.sleep(0.1)
    
    ttfbs = [l["ttfb_ms"] for l in latencies]
    return {
        "url": url,
        "samples": n,
        "ttfb_p50_ms": sorted(ttfbs)[n // 2],
        "ttfb_p99_ms": sorted(ttfbs)[int(n * 0.99)],
        "ttfb_avg_ms": sum(ttfbs) / len(ttfbs),
        "encoding": latencies[0]["encoding"],
    }

# Compare endpoints
endpoints = [
    "https://example.com/api/data",
    "https://cdn.example.com/api/data",
]
for url in endpoints:
    result = benchmark_endpoint(url, n=20)
    print(f"{url}")
    print(f"  TTFB: p50={result['ttfb_p50_ms']:.1f}ms "
          f"p99={result['ttfb_p99_ms']:.1f}ms "
          f"encoding={result['encoding']}")
```

---

### ⚖️ Comparison Table

| Technique | Latency Reduction | Complexity | When to Apply |
|---|---|---|---|
| CDN | 50-90% for static | Low | Always for static assets |
| HTTP/2 | 50-80% for many resources | Low | Always (server config) |
| TLS 1.3 | 1 RTT saved | Low | Always (upgrade config) |
| QUIC/HTTP/3 | Lossy/mobile paths | Medium | Mobile-heavy traffic |
| Brotli compression | 15-30% size reduction | Low | Always for text content |
| TCP BBR | 10-30% throughput | Low | Always (Linux sysctl) |
| 0-RTT | 1 RTT saved on reconnect | Medium | High-return-user traffic |
| Edge compute | Eliminates origin RTT | High | Complex dynamic logic |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More bandwidth solves latency | Bandwidth and latency are orthogonal. A 10 Gbps link still has 100ms RTT to a distant server. Latency requires physical proximity or fewer round trips |
| TLS adds significant overhead | TLS 1.3 adds ~1 RTT (first connection) or 0 RTT (session resume). CPU overhead is <5% on modern hardware. The handshake RTT is often larger than the crypto overhead |
| HTTP/2 is always faster than HTTP/1.1 | HTTP/2 improves multi-resource page loads. For single-resource APIs, HTTP/1.1 with keep-alive may perform comparably. HTTP/2's benefit is parallelism, not reduced per-request overhead |

---

### 🚨 Failure Modes & Diagnosis

**High TTFB Despite CDN — Origin Not Cached**

```bash
# Check CDN cache status
curl -I https://cdn.example.com/api/data | grep -i "cf-cache\|x-cache\|age"
# CF-Cache-Status: MISS → CDN fetching from origin every time
# Age: 0 → not cached

# Root cause: API response has Cache-Control: no-store or no-cache
curl -I https://cdn.example.com/api/data | grep -i cache-control
# Cache-Control: no-store  ← CDN can't cache this

# Fix options:
# 1. Add s-maxage for CDN caching: Cache-Control: s-maxage=60, max-age=0
# 2. If truly dynamic: move to edge compute (Cloudflare Workers)
#    to process closer to user without full origin round-trip
# 3. Add CDN Shield/Origin Shield to reduce origin fetches

# Also check: DNS TTL for CDN
dig cdn.example.com | grep -i ttl
# Low TTL (< 300s) → more DNS lookups → more latency for new users
# Fix: increase DNS TTL to 300-3600s
```

---

### 🔗 Related Keywords

**Prerequisites:** `TCP`, `HTTP & APIs`, `DNS`, `CDN`, `TLS/SSL`

**Related:** `QUIC`, `CDN`, `Bandwidth vs Throughput`, `Packet Loss, Latency & Jitter`, `DNS Resolution Flow`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TTFB         │ DNS + TCP + TLS + server → measure first  │
│              │ curl -w time_starttransfer to diagnose     │
├──────────────┼───────────────────────────────────────────┤
│ TOP WINS     │ 1. CDN (proximity); 2. HTTP/2 (parallel)  │
│              │ 3. TLS 1.3 (1-RTT); 4. Compression        │
├──────────────┼───────────────────────────────────────────┤
│ TCP TUNING   │ BBR, tcp_nodelay, buffer ≥ BDP, TCP FO    │
├──────────────┼───────────────────────────────────────────┤
│ TAIL LATENCY │ Connection pool warmup, hedged requests,   │
│              │ circuit breakers for p99 improvement       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fewer round trips, closer servers,        │
│              │ smaller payloads — in that priority order" │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A global fintech platform serves users in 50 countries. They observe: p50 API latency = 20ms, p99 = 800ms. Propose a systematic latency reduction programme: (a) diagnose the 800ms p99 (is it network? GC pause? connection pool exhaustion? slow database queries?), (b) explain how distributed tracing (Jaeger, Zipkin) with trace context propagation identifies which hop contributes the most to tail latency, (c) design a CDN strategy for dynamic API responses (API Gateway at edge with Cloudflare Workers / Lambda@Edge, cache personalised responses with Vary headers), (d) propose the connection pool sizing formula for a service making 1,000 req/s with 50ms average backend latency (Little's Law: N = λ × L → 1000 × 0.05 = 50 connections needed), and (e) explain hedged requests as a technique for tail latency reduction (send to two backends after p95 latency threshold, use first response — reduces p99 at cost of ~5% extra backend load).
