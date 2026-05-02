---
layout: default
title: "Keep-Alive / Connection Pooling"
parent: "HTTP & APIs"
nav_order: 212
permalink: /http-apis/keep-alive-connection-pooling/
number: "0212"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP/1.1, TCP, Sockets, HTTP Headers
used_by: HTTP/2, API Performance, Database Connection Pools, HTTP Client Libraries
related: TCP, HTTP/2, Connection Management, HikariCP, Thread Pools
tags:
  - http
  - networking
  - performance
  - tcp
  - intermediate
---

# 212 — Keep-Alive / Connection Pooling

⚡ TL;DR — Keep-Alive reuses a single TCP connection for multiple HTTP requests instead of reconnecting for every one, cutting connection setup latency from the critical path; connection pooling manages a set of pre-established connections shared across concurrent request threads.

| #212            | Category: HTTP & APIs                                                     | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | HTTP/1.1, TCP, Sockets, HTTP Headers                                      |                 |
| **Used by:**    | HTTP/2, API Performance, Database Connection Pools, HTTP Client Libraries |                 |
| **Related:**    | TCP, HTTP/2, Connection Management, HikariCP, Thread Pools                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every HTTP request requires a TCP connection. Every TCP connection requires a
3-way handshake (SYN → SYN-ACK → ACK) costing at least one round-trip time (RTT).
For HTTPS, add another 1–2 RTTs for TLS negotiation. With HTTP/1.0's default
"close the connection after every response," a service making 10 API calls to the
same upstream must pay 10 × (TCP handshake + TLS handshake) overhead — potentially
500ms of pure setup latency before any response data arrives, for requests that
might take 5ms of actual server processing time.

**THE BREAKING POINT:**
A service at 1,000 req/s accepting short-lived API calls to a backend would spend
95% of its time establishing connections rather than doing work. OS socket file
descriptors would be exhausted by connections stuck in TIME_WAIT. The server
would see a flood of SYN packets rather than productive traffic.

**THE INVENTION MOMENT:**
This is exactly why HTTP keep-alive and connection pooling were introduced. HTTP/1.1
made persistent connections the default. Connection pooling took this further:
pre-establishing connections and reusing them across multiple concurrent threads.

---

### 📘 Textbook Definition

**HTTP Keep-Alive** (persistent connections) is an HTTP/1.1 feature that maintains
a TCP connection open after a request-response cycle, allowing subsequent requests
to reuse the same connection without re-establishing the TCP (and TLS) handshake.
The `Connection: keep-alive` header (redundant in HTTP/1.1 where it is the default)
and `Connection: close` (opt-out) control this behaviour. **Connection pooling**
extends keep-alive to concurrent multi-threaded scenarios: a pool of pre-established,
idle TCP connections is shared across threads, with a connection acquired before a
request and returned immediately after. The pool manages limits (max total, max per
host), idle timeouts (evicting connections the server may have closed), and
validation (probing connections for liveness before use).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Keep-Alive reuses the same TCP "highway" for many requests instead of tearing
it down and rebuilding it for every trip.

**One analogy:**

> Without keep-alive: every time you need to make a phone call, you pick up the
> phone, dial the number, wait for it to ring, say hello, talk, then hang up and
> dial again for the very next sentence. With keep-alive: you dial once, say
> everything you need to say in multiple exchanges, and only hang up when the
> full conversation is done. Connection pooling is having a bank of phones,
> all pre-dialled and ready — any employee can pick one up instantly.

**One insight:**
The latency saving of keep-alive is not proportional to request frequency — it
is absolute. Whether you make 1 request or 100 requests, you pay the TCP+TLS
setup cost once. For short, fast API calls (< 5ms server processing), the
setup cost can dominate total latency. Connection pooling converts this fixed
cost from per-request to per-application.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A TCP connection is a bidirectional byte stream with session state maintained
   at both endpoints. Setting it up is expensive (RTT); tearing it down is cheap.
2. HTTP is request-response: requests and responses are perfectly serialised on a
   single connection in HTTP/1.1. Concurrent requests need concurrent connections.
3. Connection re-establishment is always the highest cost in low-payload, high-
   frequency API patterns.

**DERIVED DESIGN:**

**Keep-Alive (single connection reuse):**

```
┌──────────────────────────────────────────────────┐
│ Without Keep-Alive (HTTP/1.0 default):           │
│                                                  │
│ SYN→SYN-ACK→ACK  → Req1 → Resp1 → FIN/ACK       │
│ SYN→SYN-ACK→ACK  → Req2 → Resp2 → FIN/ACK       │
│ SYN→SYN-ACK→ACK  → Req3 → Resp3 → FIN/ACK       │
│ 3 full TCP setups for 3 requests                 │
│                                                  │
│ With Keep-Alive (HTTP/1.1 default):              │
│                                                  │
│ SYN→SYN-ACK→ACK  → Req1 → Resp1                 │
│                  → Req2 → Resp2                  │
│                  → Req3 → Resp3 → FIN/ACK        │
│ 1 TCP setup for 3 requests                       │
└──────────────────────────────────────────────────┘
```

**Connection Pool (concurrent access):**

```
┌──────────────────────────────────────────────────┐
│         Connection Pool Structure                │
├──────────────────────────────────────────────────┤
│ Pool to: api.example.com:443                     │
│                                                  │
│  Connections:                                    │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ Conn 1 │ │ Conn 2 │ │ Conn 3 │ │ Conn 4 │   │
│  │ IDLE   │ │ IN USE │ │ IN USE │ │ IDLE   │   │
│  └────────┘ └────────┘ └────────┘ └────────┘   │
│                                                  │
│  Thread A acquires Conn 1:  instant (no setup)  │
│  Thread B acquires Conn 4:  instant             │
│  Thread C: pool full? wait or fail              │
└──────────────────────────────────────────────────┘
```

**Idle Timeout Problem:**
Servers close idle connections after a timeout (Nginx default: 75s, AWS ALB: 60s).
If a pool holds a connection idle for longer, the next request on that connection
hits a half-open socket: the client writes to it, the server has closed it, the
client receives `Connection reset by peer`. The pool must:

1. Set its idle-eviction timeout below the server's keepalive timeout
2. Validate connections before use (TCP write probe or cheap HEAD request)

**THE TRADE-OFFS:**

- Gain: eliminates TCP/TLS setup latency from the hot path; reduces OS, CDN, and
  server socket state
- Cost: idle connections consume memory and server-side socket descriptors; an
  underused pool with 50 idle connections still occupies 50 kernel TCP sockets

---

### 🧪 Thought Experiment

**SETUP:**
A microservice makes 100 calls/second to a downstream HTTPS API. Each call takes
5ms of server processing time. TCP+TLS setup = 30ms (3 RTTs on a 10ms RTT link).

**WITHOUT CONNECTION POOLING:**

- Each request: 30ms setup + 5ms processing = 35ms per request
- 100 req/s × 35ms = 3,500ms worth of active ops per second
- Actual server processing time: 100 × 5ms = 500ms
- Connection setup overhead: 3,000ms = 857% overhead
- At 200 req/s the system would need 200 simultaneous TCP setups → port exhaustion

**WITH CONNECTION POOL (max 10 connections):**

- On startup: 10 connections established (10 × 30ms — one-time cost)
- Each request: 0ms setup + 5ms processing = 5ms per request
- 100 req/s × 5ms = 500ms worth of active ops per second
- 10 connections × 100ms average response = 1,000ms of concurrent pipeline
- Bottleneck: can serve 200 req/s with 10 connections (10 × 100ms pipelining)
- Connection setup overhead: ~0%

**THE INSIGHT:**
Connection pooling converts a per-request TCP setup cost (O(N) where N = request
count) into a one-time startup cost (O(P) where P = pool size). For high-frequency
APIs, this single change can reduce p50 latency by 30-100ms and eliminate port
exhaustion issues.

---

### 🧠 Mental Model / Analogy

> A connection pool is like a fleet of taxis parked at an airport. Without the
> pool, each passenger (request) books an Uber, waits for the driver to navigate
> from home, pick them up, and drive to the destination. With the pool, 10 taxis
> are already waiting, engines running. A passenger walks out and immediately gets
> in — no wait. The pool manager ensures there are always enough taxis and replaces
> any cab whose engine has gone cold while waiting.

**Mapping:**

- "airport" → your application
- "destination" → downstream API server
- "taxi" → TCP connection (with TLS already established)
- "booking the Uber, waiting for driver" → TCP + TLS handshake
- "pool manager" → connection pool implementation (OkHttp, Apache HC)
- "cold engine" → idle timeout (server closed the connection)
- "enough taxis" → max pool size configuration

**Where this analogy breaks down:**
Unlike taxis, HTTP connections in a pool are strictly single-threaded (one
request per connection in HTTP/1.1). If all 10 "taxis" are occupied with long
rides, the 11th passenger must wait — leading to connection pool exhaustion.
HTTP/2 solves this by multiplexing streams on one connection.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Making a phone call takes setup time — dialling, ringing, connecting. Keep-alive
means you stay on the line between conversations instead of hanging up and
calling back each time. Connection pooling means you have a switchboard with
many pre-connected lines, ready for whoever needs one.

**Level 2 — How to use it (junior developer):**
Most HTTP client libraries handle keep-alive and pooling automatically:
OkHttp, Apache HttpClient, and Java 11 HttpClient all use connection pools by
default. The mistakes to avoid: creating a new client instance per request
(defeats pooling entirely), not closing response bodies (leaks connections),
and not configuring pool size to match load patterns. Never use `HttpURLConnection`
directly in production without wrapping it in a proper pool.

**Level 3 — How it works (mid-level engineer):**
Connection pools track connections in three states: idle (available for reuse),
active (in-use by a thread), and connecting (TCP handshake in progress). Pool
configuration critical parameters: `maxTotal` (absolute connection limit),
`maxPerRoute` (per-host limit — prevents one slow host from exhausting the pool),
`idleTimeout` (how long idle connections are kept before eviction — must be less
than server's keepalive timeout), `connectionTimeout` (max wait to establish
a new TCP connection), and `socketTimeout` (max wait for data from server).
`validateAfterInactivity` triggers a lightweight probe (typically a TCP write
with a small ping) to verify connections haven't gone stale before use.

**Level 4 — Why it was designed this way (senior/staff):**
The `maxPerRoute` limit was a deliberate design to prevent one misbehaving
upstream from consuming all connections in a shared pool — a form of bulkhead
isolation. The fundamental tension is between having enough idle connections
to absorb bursts (requiring more memory/server descriptors) vs minimising waste
for steady-state load. Modern HTTP/2 dissolved much of this tension: with
multiplexing, one connection can carry hundreds of parallel requests, and a pool
of 1–2 HTTP/2 connections can outperform a pool of 20 HTTP/1.1 connections.
The residual need for HTTP/1.1 pools comes from legacy systems, backend
databases (which don't speak HTTP), and scenarios where HTTP/2 is unavailable.

---

### ⚙️ How It Works (Mechanism)

**Keep-Alive Headers (HTTP/1.1):**

```
# Request (keep-alive is implicit in HTTP/1.1):
GET /api/data HTTP/1.1
Host: api.example.com
Connection: keep-alive

# Response:
HTTP/1.1 200 OK
Connection: keep-alive
Keep-Alive: timeout=60, max=100
Content-Length: 47
```

`timeout`: idle seconds before server closes. `max`: max requests on this connection.

**Connection Pool Lifecycle State Machine:**

```
┌──────────────────────────────────────────────────┐
│     Connection Pool State Machine                │
├──────────────────────────────────────────────────┤
│                                                  │
│ NEW CONNECTION:                                  │
│   [created] → TCP connect → TLS handshake        │
│          → [IDLE in pool]                        │
│                                                  │
│ REQUEST ARRIVES:                                 │
│   [IDLE] → acquired by thread → [ACTIVE]        │
│   [ACTIVE] → request sent → response read       │
│          → [IDLE in pool] (if keep-alive)        │
│          → [CLOSED] (if Connection: close)      │
│                                                  │
│ IDLE TIMEOUT EXPIRES:                            │
│   [IDLE] → evicted → TCP socket closed          │
│                                                  │
│ SERVER CLOSES CONNECTION:                        │
│   [IDLE] → next use: ECONNRESET                 │
│          → pool removes, opens new connection   │
└──────────────────────────────────────────────────┘
```

**Pool Exhaustion:**
When all connections are ACTIVE: new request waits up to `connectionRequestTimeout`.
If timeout elapses: `ConnectionPoolTimeoutException` thrown. This is the most
common connection pool failure in high-load systems.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
┌──────────────────────────────────────────────────┐
│     Request Through a Connection Pool            │
├──────────────────────────────────────────────────┤
│ Incoming request to your service                 │
│         ↓                                        │
│ Business logic: need to call downstream API      │
│         ↓                                        │
│ [KEEP-ALIVE / POOL ← YOU ARE HERE]               │
│ Pool: acquire idle connection for api.example.com│
│   → IDLE connection found → no TCP setup needed  │
│         ↓                                        │
│ Write HTTP request to socket                     │
│         ↓                                        │
│ Downstream API processes, writes response        │
│         ↓                                        │
│ Read response, parse body                        │
│         ↓                                        │
│ Return connection to pool (state: IDLE)          │
│         ↓                                        │
│ Thread continues, response returned to caller    │
└──────────────────────────────────────────────────┘
```

**FAILURE PATH:**
All pool connections ACTIVE + new request arrives → waits for `connectionRequestTimeout`
→ timeout fires → `ConnectionPoolTimeoutException` → request fails with 503.

**WHAT CHANGES AT SCALE:**
At 10,000 req/s, connection pool sizing becomes critical. Too few connections:
queue depth grows, p99 latency spikes from wait time. Too many: server-side
descriptor exhaustion and memory pressure. The correct size is empirically:
`pool size = (max_concurrent_requests × avg_response_time_seconds)`. For a
service with 1,000 concurrent threads each taking 50ms: pool needs 50 connections.

---

### 💻 Code Example

**Example 1 — OkHttp connection pool configuration:**

```java
// BAD: New client per request — defeats pooling entirely
public String callApi(String url) throws IOException {
    OkHttpClient client = new OkHttpClient(); // NEW per request!
    Request req = new Request.Builder().url(url).build();
    try (Response resp = client.newCall(req).execute()) {
        return resp.body().string();
    }
}

// GOOD: Single shared client with configured pool
@Bean
public OkHttpClient okHttpClient() {
    return new OkHttpClient.Builder()
        .connectionPool(new ConnectionPool(
            50,           // max idle connections
            30,           // keep-alive duration
            TimeUnit.SECONDS  // must be < server's idle timeout (60s)
        ))
        .connectTimeout(Duration.ofSeconds(3))
        .readTimeout(Duration.ofSeconds(10))
        .build();
}
```

**Example 2 — Apache HttpClient pool:**

```java
PoolingHttpClientConnectionManager cm =
    new PoolingHttpClientConnectionManager();
cm.setMaxTotal(100);          // total connections across all hosts
cm.setDefaultMaxPerRoute(20); // per-host limit (bulkhead!)
cm.setValidateAfterInactivity(5_000); // validate after 5s idle

CloseableHttpClient client = HttpClients.custom()
    .setConnectionManager(cm)
    .setKeepAliveStrategy((response, ctx) ->
        60_000) // keep-alive 60s (< Nginx's 75s default)
    .build();
```

**Example 3 — Spring Boot: configure WebClient connection pool:**

```java
@Bean
public WebClient webClient() {
    HttpClient httpClient = HttpClient.create()
        .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 3000)
        .responseTimeout(Duration.ofSeconds(10))
        .doOnConnected(conn -> conn
            .addHandlerLast(new ReadTimeoutHandler(10))
            .addHandlerLast(new WriteTimeoutHandler(10)));

    // Reactor Netty uses connection pool internally by default
    // Configure pool:
    ConnectionProvider provider = ConnectionProvider.builder("custom")
        .maxConnections(50)
        .maxIdleTime(Duration.ofSeconds(25)) // < server timeout
        .build();

    return WebClient.builder()
        .clientConnector(new ReactorClientHttpConnector(
            HttpClient.create(provider)))
        .build();
}
```

---

### ⚖️ Comparison Table

| Strategy                   | Connections  | Thread Safety    | Overhead          | Best For                |
| -------------------------- | ------------ | ---------------- | ----------------- | ----------------------- |
| New connection per request | N (one each) | No               | Maximum           | Testing only            |
| **Keep-Alive (no pool)**   | 1 per thread | Yes (per-thread) | Low (1 handshake) | Single-threaded clients |
| **Connection Pool**        | Configurable | Yes              | Minimal           | Multi-threaded servers  |
| HTTP/2 multiplexing        | 1–2 total    | Yes              | Near zero         | Modern APIs, gRPC       |

**How to choose:** Use connection pooling for any multi-threaded HTTP client.
Set `maxPerRoute` to prevent one slow upstream from exhausting the entire pool.
For HTTP/2-capable upstreams, a smaller pool (5–10 connections) with multiplexing
handles more load than a bigger HTTP/1.1 pool.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                    |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| More pool connections = better performance       | Diminishing returns above queue depth saturation. Too many idle connections waste server descriptors and JVM memory                        |
| Keep-alive prevents all connection setup latency | Keep-alive eliminates latency for reused connections. The first connection to each host still pays full handshake cost                     |
| Connection pools are only for databases          | HTTP client connection pools are equally important. Creating new OkHttp clients per request is a very common production performance bug    |
| maxTotal and maxPerRoute are the same setting    | maxTotal is the absolute pool cap; maxPerRoute is per-upstream-host. A route-level limit prevents one slow host from monopolising the pool |
| HTTPS connections can't be reused                | HTTPS connections benefit even more from reuse because TLS handshake (~100ms) adds to TCP handshake (~30ms), increasing total setup cost   |

---

### 🚨 Failure Modes & Diagnosis

**Connection Pool Exhaustion (Latency Spike)**

Symptom: p99 latency suddenly 10× higher than p50; logs show
`ConnectionPoolTimeoutException` or `Unable to acquire connection`; thread dumps
show many threads waiting on `leaseConnection()`.

Root Cause: All pool connections in use; slow downstream creating long hold times;
pool sized too small for peak concurrency.

Diagnostic Command / Tool:

```bash
# Check OkHttp pool stats (expose via Micrometer):
curl http://localhost:8080/actuator/metrics/http.client.requests \
  | jq '.measurements'

# Thread dump to find blocked threads:
jcmd <pid> Thread.print | grep -A5 "ConnectionPool"

# Real-time pool state (Apache HttpClient):
cm.getTotalStats().toString()
# Output: [leased: 20; pending: 5; available: 0; max: 20]
# "pending: 5" = 5 threads waiting for a connection
```

Fix: Increase `maxTotal`/`maxPerRoute`. Add circuit breaker around slow downstream.
Enable connection timeout to fail fast instead of blocking indefinitely.

Prevention: Size pool based on Little's Law: `L = λ × W` (connections needed =
request rate × average time holding a connection). Monitor pool utilisation as
a first-class metric.

---

**Stale Connection — EOF / Connection Reset**

Symptom: Sporadic `java.net.SocketException: Connection reset` or
`java.io.EOFException in HttpClient`; failures are rare but unpredictable;
restart clears the problem temporarily.

Root Cause: Server-side idle timeout (e.g., AWS ALB 60s) closed the connection
while it was idle in the client's pool. Next request attempts to write to the
closed socket, receives TCP RST, and fails.

Diagnostic Command / Tool:

```bash
# Check server-side keepalive timeout:
# For Nginx:
grep keepalive_timeout /etc/nginx/nginx.conf
# For AWS ALB: check "Idle timeout" in Target Group settings

# Observe connection state changes:
watch -n 1 "ss -n state time-wait | wc -l"
```

Fix:

```java
// Set pool idle timeout BELOW server's keepalive timeout:
.maxIdleTime(Duration.ofSeconds(45))  // server = 60s, ours = 45s
// Plus enable stale connection validation:
.evictInBackground(Duration.ofSeconds(10))
```

Prevention: Always configure client pool idle timeout as `(server_keepalive - 10s)`.
Never use the default, which may exceed server timeouts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `TCP` — keep-alive reuses TCP connections; understanding TCP's 3-way handshake
  cost and TIME_WAIT state is essential to understanding why keep-alive matters
- `HTTP/1.1` — keep-alive is an HTTP/1.1 default behaviour defined in the spec;
  HTTP/1.0 required explicit opt-in

**Builds On This (learn these next):**

- `HTTP/2` — HTTP/2 takes connection reuse to its logical extreme: one connection
  serves all concurrent requests via multiplexed streams, making large per-host
  connection pools unnecessary
- `HikariCP` — the same connection pool pattern applied to database connections;
  identical trade-offs and configuration principles

**Alternatives / Comparisons:**

- `HTTP/2 Multiplexing` — eliminates the need for large HTTP connection pools;
  one multiplexed connection replaces the role of 10–50 HTTP/1.1 pool connections

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ TCP connection reuse across HTTP requests │
│              │ + pool of pre-established connections     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ TCP+TLS handshake (30–100ms) on every    │
│ SOLVES       │ request dominates latency for fast APIs  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Connection setup is a fixed cost paid    │
│              │ once per pool slot, not per request      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any HTTP client making > 1 request/sec   │
│              │ to the same host                         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never create new HTTP client per request │
│              │ in production code                       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Eliminates per-request setup cost vs     │
│              │ idle connections wasting server fd quota │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pre-dial the phone; don't hang up       │
│              │  between sentences."                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HTTP/2 → TCP → HikariCP → Thread Pools  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Java microservice uses OkHttp with a connection pool of 20 connections
to call a downstream service. The downstream service is behind an AWS ALB with
a 60-second idle connection timeout. The microservice handles 50 req/s with an
average response time of 100ms, but at night drops to 0.1 req/s for 6 hours.
Describe in detail what happens to the pool's connections during the night-time
idle period, what error the first morning request experiences, how OkHttp handles
it transparently, and what configuration change would prevent any visible error.

**Q2.** A service's HTTP connection pool is sized at 20 connections. Under load
testing, you discover that p99 latency is 800ms even though the downstream API
p50 is 20ms. Using Little's Law (`L = λ × W`), calculate whether the pool is
undersized — and explain why pool exhaustion causes latency to spike
disproportionately rather than linearly.
