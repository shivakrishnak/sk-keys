---
layout: default
title: "Keep-Alive / Connection Pooling"
parent: "HTTP & APIs"
nav_order: 212
permalink: /http-apis/keep-alive-connection-pooling/
number: "212"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP/1.1, TCP, HTTP Headers
used_by: HTTP/2, REST, API Gateway, gRPC
tags:
  - networking
  - protocol
  - http
  - performance
  - intermediate
---

# 212 — Keep-Alive / Connection Pooling

`#networking` `#protocol` `#http` `#performance` `#intermediate`

⚡ TL;DR — Reusing TCP connections across multiple HTTP requests (keep-alive) and managing a pool of pre-established connections (connection pooling) to eliminate per-request TCP/TLS handshake overhead.

| #212 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1, TCP, HTTP Headers | |
| **Used by:** | HTTP/2, REST, API Gateway, gRPC | |

---

### 📘 Textbook Definition

**HTTP Keep-Alive** (persistent connection) is a mechanism enabling multiple HTTP request-response pairs to be transmitted over a single TCP connection rather than closing and reopening the connection for each exchange. Controlled by the `Connection: keep-alive` header (default in HTTP/1.1) and `Keep-Alive: timeout=5, max=100` directives specifying idle timeout and maximum requests per connection. **Connection Pooling** extends this by maintaining a pre-warmed pool of established TCP (and optionally TLS) connections, allowing concurrent requests to immediately acquire connections without waiting for handshake latency. Connection pooling is implemented by HTTP client libraries (OkHttp, Apache HttpClient, Java 11 HttpClient), JDBC drivers, and application servers.

### 🟢 Simple Definition (Easy)

Keep-alive reuses an existing connection for multiple requests. Connection pooling maintains a ready collection of these connections so you never wait to establish one.

### 🔵 Simple Definition (Elaborated)

Opening a TCP connection takes at least one round-trip (100ms on a cross-continental link). Adding TLS adds 1–2 more round-trips. If every HTTP request requires a brand-new connection, 10 requests per user action = 10 × 300ms = 3 seconds of pure connection overhead. Keep-alive solves this by keeping the connection open after a response — the next request reuses the same TCP socket. Connection pooling takes it further: maintains 10–50 idle connections to common hosts ready to go, so a request can be sent with zero setup latency. This is why Java's HikariCP (for databases) and OkHttp (for HTTP) are so much faster than naive connection creation.

### 🔩 First Principles Explanation

**TCP connection cost:**

```
TCP handshake:     1 RTT = ~100ms (typical cross-DC)
TLS 1.2 handshake: 2 RTT = ~200ms
TLS 1.3 handshake: 1 RTT = ~100ms
Total new HTTPS connection: 200-300ms before first byte

With Keep-Alive (reuse): 0ms connection cost
With Connection Pool (idle conn): 0ms connection cost
```

**Keep-Alive mechanism:**

```
HTTP/1.1:  Connection: keep-alive (default)
           Keep-Alive: timeout=30, max=1000
           → server keeps connection open for 30s idle
           → server accepts up to 1000 requests per connection

HTTP/1.0:  Connection: keep-alive (opt-in; not default)
HTTP/2:    Always persistent; replaced by stream multiplexing
```

**Connection pool dynamics:**

```
Pool: [conn1:idle] [conn2:active] [conn3:active] [conn4:idle] ...

Request arrives:
→ Acquire idle conn1 from pool
→ Send request
→ Receive response
→ Return conn1 to pool as idle

All connections busy:
→ Wait in queue (bounded wait)
→ If pool exhausted + max connections reached: reject or wait
```

**Pool configuration parameters:**

```
maxConnections (maxPoolSize):  total connections (default: 5–20)
maxIdleConnections:            idle connections retained
keepAliveTimeout:              how long idle connections survive
connectionTimeout:             max wait to acquire from pool
readTimeout:                   max wait for server response
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT Keep-Alive / Connection Pooling:

- Every HTTP request requires a new TCP handshake (100ms) + TLS (200ms).
- For an API service making 10 downstream calls per request: 10 × 300ms = 3s overhead.
- Database connections take 5–10ms each; creating per-query = massive overhead.
- Under high concurrency, rapid TCP connection creation exhausts ephemeral ports and file descriptors.

What breaks without it:
1. API gateway latency dominated by connection setup, not actual processing time.
2. Database exhaustion: 10,000 req/s × 5ms per connection = 50 connection-seconds overhead.

WITH Keep-Alive / Connection Pooling:
→ Downstream API calls: 0ms connection overhead after first request.
→ Database pool (HikariCP): 20 connections serving thousands of concurrent queries.
→ OS file descriptor usage bounded by pool size, not request rate.

### 🧠 Mental Model / Analogy

> Without keep-alive: Every time you need a taxi (TCP connection), you open the Uber app, request a new taxi, wait for it to arrive (TCP+TLS handshake), get in, travel, and dismiss the taxi at the destination. Next trip: order new taxi.

> With connection pooling: A company pre-books 20 taxis waiting outside the office (connection pool). When you need a trip, you walk out and take the idle taxi immediately (acquire from pool). After the trip, the taxi returns to wait outside (return to pool). 20 taxis serve hundreds of employees without waiting.

"Taxi" = TCP connection, "waiting outside" = idle pool connection, "open the app / wait" = TCP+TLS handshake, "dismiss taxi" = connection close.

### ⚙️ How It Works (Mechanism)

**Connection pool state machine:**

```
Pool starts: N connections established (or lazy on first use)

Request:
  → borrow idle connection → send → receive → return to pool
                                                    ↓
                               validation check (test query / ping)
                               if failed → discard → create new
```

**Idle connection eviction:**

```
Keep-Alive timeout from server: keepAliveTimeout=30s
Pool idle connection timeout:   idleTimeout=600s (HikariCP)
Connection max lifetime:        maxLifetime=1800s (HikariCP)

Connections evicted:
- When idle for > idleTimeout
- When alive for > maxLifetime (prevents MySQL wait_timeout issues)
- When health check fails
```

**Key pool libraries:**

| Use Case | Library | Default Pool Size |
|---|---|---|
| JDBC (databases) | HikariCP | 10 |
| HTTP client | OkHttp connection pool | 5 |
| HTTP client | Apache HttpClient | 20 |
| HTTP client | Java 11 HttpClient | System-defined |
| Redis | Lettuce (reactor pool) | 8 |

### 🔄 How It Connects (Mini-Map)

```
TCP/TLS connection (expensive to create)
           ↓ reuse via
Keep-Alive ← you are here
           ↓ managed by
Connection Pool
  (pre-warmed, bounded, health-checked)
           ↓ used in
OkHttp | HikariCP | Apache HttpClient
           ↓ superseded by
HTTP/2 (multiplexing: many requests, one connection)
```

### 💻 Code Example

Example 1 — HikariCP database connection pool:

```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://db:5432/mydb");
config.setUsername("user");
config.setPassword("pass");
config.setMaximumPoolSize(20);          // max connections
config.setMinimumIdle(5);              // idle connections kept
config.setConnectionTimeout(3000);     // ms to wait for connection
config.setIdleTimeout(600000);         // 10 min idle eviction
config.setMaxLifetime(1800000);        // 30 min connection lifetime
config.setKeepaliveTime(30000);        // send keepalive every 30s
config.setConnectionTestQuery(
    "SELECT 1");                        // health check query

HikariDataSource dataSource = new HikariDataSource(config);
// Use: dataSource.getConnection() → borrowed from pool
```

Example 2 — OkHttp connection pooling:

```java
// Create OkHttpClient with connection pool (shared singleton)
OkHttpClient client = new OkHttpClient.Builder()
    .connectionPool(new ConnectionPool(
        10,             // max idle connections
        5, TimeUnit.MINUTES)) // keep idle for 5 minutes
    .connectTimeout(3, TimeUnit.SECONDS)
    .readTimeout(10, TimeUnit.SECONDS)
    .build();

// BAD: Creating new client per request
// OkHttpClient badClient = new OkHttpClient(); // new pool each time!

// GOOD: Singleton client reused across all requests
// Both GET and POST requests share the same connection pool
Request request = new Request.Builder()
    .url("https://api.example.com/users")
    .build();

try (Response response = client.newCall(request).execute()) {
    System.out.println(response.body().string());
}
```

Example 3 — Diagnosing connection pool exhaustion:

```bash
# HikariCP pool metrics via Spring Boot Actuator
curl http://localhost:8080/actuator/metrics/hikaricp.connections
# {..,"value":20.0} = total pool size

curl http://localhost:8080/actuator/metrics/hikaricp.connections.pending
# {..,"value":15.0} = 15 requests waiting for a connection!
# → pool too small; increase maximumPoolSize

# Check pool config:
curl http://localhost:8080/actuator/metrics/hikaricp.connections.max
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bigger connection pool always means better performance | Connection pools should be sized to actual thread parallelism and database limits. Over-provisioning wastes database connection resources and can cause the database to become the bottleneck. |
| HTTP/2 eliminates the need for connection pooling | HTTP/2 multiplexes streams on ONE connection; for high-concurrency scenarios, multiple HTTP/2 connections in a pool are still beneficial. |
| Keep-Alive prevents connection leaks | Keep-Alive has a timeout; connections that idle past it are closed by the server. Your pool must handle server-side disconnects gracefully (validate connections before use). |
| Connection pool size = max concurrent requests | Pool size limits concurrent database/HTTP connections, not total request throughput. With async/virtual threads, 20 pool connections can serve thousands of concurrent requests. |
| Setting maxConnections=1000 improves throughput | Database servers have limits (PostgreSQL default: 100). Set pool size from the actual worker threads and DB server limits, not from app concurrency. |

### 🔥 Pitfalls in Production

**1. Connection Leak — Not Returning Connections to Pool**

```java
// BAD: Connection not returned if exception thrown
Connection conn = pool.getConnection();
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT ...");
rs.next(); // throws exception → conn never returned!
// Pool starves: "Connection is not available, timeout!"

// GOOD: Always close in finally or try-with-resources
try (Connection conn = dataSource.getConnection();
     PreparedStatement stmt = conn.prepareStatement("...")) {
    // ...
} // auto-closes: conn returned to pool
```

**2. Pool Too Small for Thread Count**

```bash
# Typical mistake: 10 connections for 200-thread web server
# During peak: 200 threads all block on getConnection()
# → connection timeout exceptions → cascading failures

# Rule of thumb (HikariCP formula):
# connections = (core_count * 2) + effective_spindle_count
# For 8 CPU cores, SSD: connections = 8 * 2 + 0 = 16-20

# But also: don't exceed database's max_connections setting
# Check: SHOW max_connections; (PostgreSQL) → default 100
```

**3. Stale Connections After Network Outage**

```java
// BAD: Pool holds connections from before network outage
// After network recovers: stale connections in pool → failure

// GOOD: Configure connection validation
config.setConnectionTestQuery("SELECT 1"); // test before borrow
// or use HikariCP's built-in keepalive:
config.setKeepaliveTime(30000); // ping idle connections
// or validate on borrow by checking if conn is still valid:
config.setValidationTimeout(5000);
```

### 🔗 Related Keywords

- `HTTP/1.1` — introduced keep-alive as default connection behaviour.
- `HTTP/2` — replaces keep-alive with stream multiplexing on a single connection.
- `TCP` — the transport layer connections that keep-alive and pooling reuse.
- `HikariCP` — the standard database connection pool for Java/Spring applications.
- `gRPC` — the RPC framework that inherently uses HTTP/2's persistent multiplexed connection.
- `API Gateway` — often manages connection pools to upstream services.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Reuse and pre-warm TCP connections to     │
│              │ eliminate 200-300ms handshake per request.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — for any service making repeated  │
│              │ HTTP or database connections.             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Pool size > database max_connections;     │
│              │ don't share pools across process forks.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Connection pooling: keep the taxi running│
│              │ outside so your passengers never wait."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HTTP/2 → REST → API Gateway → HikariCP    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application uses a HikariCP pool with `maximumPoolSize=20` and handles HTTP requests on a thread pool of 200 threads. During load testing, P99 latency spikes to 3 seconds while connection timeout exceptions appear in logs. Without changing the pool size, describe two architectural changes at the application layer that would allow the 200 threads to share 20 database connections without exhaustion — and explain why one of those approaches works with virtual threads but may not work with platform threads.

**Q2.** A microservice creates a new `OkHttpClient` instance inside a request handler for every outgoing HTTP call to a downstream service. Describe the exact chain of resource allocations that occurs per request, calculate the approximate overhead for 1,000 requests per second making one downstream call each, and explain why this anti-pattern can eventually cause `too many open files` OS errors even if each individual request completes successfully.

