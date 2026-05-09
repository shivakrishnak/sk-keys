---
version: 1
layout: default
title: "HikariCP"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /spring/hikaricp/
id: SPR-048
category: Spring Core
difficulty: ★★☆
depends_on: JDBC, Connection Pooling, Database Fundamentals, Spring Boot
used_by: Spring Data JPA, Auto-Configuration, Transaction Management
related: DBCP2, c3p0, PgBouncer
tags:
  - spring
  - java
  - database
  - performance
  - intermediate
---

# SPR-048 - HikariCP

⚡ TL;DR - HikariCP is Spring Boot's default JDBC connection pool: it pre-creates database connections, reuses them across requests, and is fast enough that its own overhead is rarely measurable.

| #400            | Category: Spring Core                                        | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | JDBC, Connection Pooling, Database Fundamentals, Spring Boot |                 |
| **Used by:**    | Spring Data JPA, Auto-Configuration, Transaction Management  |                 |
| **Related:**    | DBCP2, c3p0, PgBouncer                                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Spring app receives 500 concurrent HTTP requests, each needing a database query. Without a connection pool, each request calls `DriverManager.getConnection()` - which opens a TCP connection to the database, performs TCP handshake, TLS negotiation, database authentication, and session setup. This takes 50–200ms per connection. 500 requests × 150ms = your database is flooded with authentication requests and your app latency spikes to hundreds of milliseconds per query, even for trivial lookups.

**THE BREAKING POINT:**
Database connections are expensive OS resources. PostgreSQL limits connections via `max_connections` (default 100). Each connection holds memory on the DB server (~5–10MB). Opening and closing connections on every request is not only slow - it can exhaust the database's connection limit, causing subsequent requests to fail with "too many connections."

**THE INVENTION MOMENT:**
"This is exactly why connection pooling was created."

---

### 📘 Textbook Definition

**HikariCP** (Hikari Connection Pool) is a high-performance JDBC connection pool library that pre-creates a configurable number of database connections, holds them open in a pool, and lends them to application threads on demand. When a thread needs a connection it borrows one from the pool (or waits if all are in use); when done, it returns the connection to the pool for reuse rather than closing it. HikariCP has been the default Spring Boot data source since Spring Boot 2.0, replacing Tomcat JDBC Pool. It is distinguished by its minimal footprint, lock-free internal design, and fast acquisition path.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HikariCP keeps N database connections warm and lends them out, so your code never pays the cost of opening a new connection.

**One analogy:**

> A rental car company that pre-purchases 20 cars. When a customer arrives, they get a car immediately - no manufacturing delay. When they return it, the car goes back to the fleet. Without a fleet, every customer would wait while a new car is built from scratch.

**One insight:**
HikariCP's value is not just speed - it's bounded resource usage. By capping the pool size, it ensures your app can never accidentally overwhelm the database with more connections than it can handle.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Creating a database connection is expensive (50–200ms, OS resources, DB memory). Connection pools amortize this cost across many requests.
2. The pool maintains a minimum number of idle connections always ready for immediate use.
3. The pool caps the maximum connections to prevent overwhelming the database.

**DERIVED DESIGN:**
HikariCP's internals are deliberately minimal. It uses a single `ConcurrentBag<PoolEntry>` structure - a custom lock-free collection optimized for the specific pattern of "borrow one, return one." When a thread requests a connection, `ConcurrentBag` checks thread-local storage first (the last-returned connection is likely the same thread's again), avoiding CAS operations entirely in the hot path.

Connection validity is maintained via `keepaliveTime` (periodic background pings) and `maxLifetime` (forced rotation of connections to prevent stale TCP state). When a connection is borrowed, HikariCP wraps it in a `ProxyConnection` that intercepts `close()` to return the connection to the pool instead of physically closing it.

**THE TRADE-OFFS:**
**Gain:** Near-zero connection acquisition overhead; bounded database resource usage; automatic stale connection detection and eviction.
**Cost:** Fixed memory overhead of maintaining N idle connections; pool size tuning requires understanding your DB's `max_connections` and your application's concurrency; misconfigured pool sizes can cause connection starvation (too small) or DB overload (too large).

---

### 🧪 Thought Experiment

**SETUP:**
A Spring Boot service handles 200 concurrent requests per second, each needing 10ms of database work. The database allows max 100 connections.

**WITHOUT HIKARICP (open connection per request):**
200 requests × 150ms connection overhead = 30,000ms of connection-opening time per second. Plus, all 200 connections go to the DB - exceeding max_connections=100. 100 requests fail immediately with "connection refused." Service is 50% unreliable.

**WITH HIKARICP (pool-size=20):**
20 connections pre-opened. Each request borrows a connection in ~0.05ms, runs 10ms of DB work, returns it. At 200 req/s with 10ms DB work, you need at most 200 × 0.01 = 2 concurrent connections. Pool-size=20 is more than enough. Zero connection-refused errors. P99 latency is 10ms + application overhead, not 10ms + 150ms connection overhead.

**THE INSIGHT:**
Little's Law: at steady state, the number of concurrent DB connections needed ≈ (requests/second) × (seconds per DB operation). A service doing 1,000 req/s with 5ms DB operations needs only ~5 concurrent connections. Most apps are massively over-sized if using per-request connections.

---

### 🧠 Mental Model / Analogy

> Think of HikariCP as a valet parking lot with a fixed number of cars. The pool has 10 cars (connections). When a customer (thread) arrives, the valet hands over a car key immediately (borrow connection). The customer drives the car (uses connection for queries), then returns it to the lot (return connection). The car doesn't disappear - it waits for the next customer.

- "Valet parking lot with N cars" → the connection pool with pool-size=N
- "Customer borrows a car key" → `dataSource.getConnection()`
- "Car is driven" → SQL queries executed on the connection
- "Car returned to lot" → `connection.close()` which triggers pool return
- "Too many customers, all cars taken" → `connectionTimeout` wait → SQLException if timeout exceeded

Where this analogy breaks down: unlike cars, database connections can silently go stale if the DB server closes the TCP connection from its side - HikariCP detects this and replaces the stale connection transparently.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
HikariCP keeps a small collection of database connections open and ready. Each request borrows one connection, uses it, and puts it back. This is much faster than creating a new connection for every request.

**Level 2 - How to use it (junior developer):**
HikariCP is included automatically with `spring-boot-starter-data-jpa` or `spring-boot-starter-jdbc`. Configure it in `application.properties` with `spring.datasource.*` properties. The most important settings are `maximum-pool-size` (default 10), `minimum-idle`, and `connection-timeout`. You never interact with HikariCP directly in application code - Spring's `DataSource` abstraction handles it transparently.

**Level 3 - How it works (mid-level engineer):**
HikariCP's `HikariDataSource` wraps a `HikariPool` which maintains a `ConcurrentBag<PoolEntry>`. Each `PoolEntry` wraps a real `java.sql.Connection`. When `getConnection()` is called, `ConcurrentBag.borrow()` first checks thread-local state (the thread's previously returned connections), then the shared idle list, then waits (using `SynchronousQueue`) if no connections are available. The returned connection is a `HikariProxyConnection` that intercepts `close()` to return the `PoolEntry` to the bag rather than closing the physical connection. Background threads handle keepalive pings and maxLifetime rotation.

**Level 4 - Why it was designed this way (senior/staff):**
Bret Wooldridge designed HikariCP with the explicit goal of making connection acquisition unmeasurably fast. The key design insights: thread-local caching of recently returned connections exploits temporal locality (the same thread likely needs a connection again soon); using `ConcurrentBag` instead of a standard `BlockingQueue` avoids lock contention; avoiding bytecode instrumentation or reflection at acquisition time keeps the hot path minimal. These choices make HikariCP acquisition overhead typically under 1 microsecond in the uncontended case - compared to 50–200ms for a fresh connection. The Spring team chose HikariCP as the default in Boot 2.0 after benchmarks showed it outperforming Tomcat JDBC Pool and DBCP2 by 5–20x in contended scenarios.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ HIKARICP POOL INTERNALS                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Application Thread                                     │
│    │ dataSource.getConnection()                         │
│    ↓                                                    │
│  HikariPool.getConnection(timeout)                      │
│    │                                                    │
│    ├─1. Check thread-local bag (O(1), no contention)   │
│    │    → hit: return ProxyConnection immediately       │
│    │                                                    │
│    ├─2. Check shared idle connections                   │
│    │    → hit: return ProxyConnection (~1µs)            │
│    │                                                    │
│    ├─3. Wait on SynchronousQueue for return             │
│    │    → timeout → throw SQLTransientException        │
│    │                                                    │
│    └─4. Maybe create new connection if below maxPool    │
│                                                         │
│  ProxyConnection wraps real Connection                  │
│    close() → returns PoolEntry to ConcurrentBag        │
│                                                         │
│  Background Threads:                                    │
│    housekeeper: evict maxLifetime connections           │
│    keepalive: ping idle connections to keep them alive  │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Essential Spring Boot configuration:**

```properties
# application.properties - HikariCP key settings

# Pool size: how many connections to maintain
# Formula: Npools = Ncores * 2 + spindle_count (for spinning disk)
# For SSD/cloud DB: start with 10, tune from metrics
spring.datasource.hikari.maximum-pool-size=10

# Minimum idle connections to maintain (default = maximum-pool-size)
spring.datasource.hikari.minimum-idle=5

# Max time to wait for a connection (default 30s)
# Set lower in high-traffic apps to fail fast
spring.datasource.hikari.connection-timeout=3000

# Max time a connection can be idle before eviction (default 10m)
spring.datasource.hikari.idle-timeout=600000

# Max lifetime of any connection (default 30m)
# Must be shorter than DB's wait_timeout / TCP timeout
spring.datasource.hikari.max-lifetime=1800000

# Name shown in JMX/metrics for this pool
spring.datasource.hikari.pool-name=OrderServicePool

# Connection keepalive interval (default 0 = disabled)
# Set shorter than DB idle timeout to prevent stale connections
spring.datasource.hikari.keepalive-time=60000
```

**Example 2 - Programmatic configuration (if needed):**

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://db:5432/orders");
        config.setUsername("app_user");
        config.setPassword(resolvePassword());
        config.setMaximumPoolSize(10);
        config.setConnectionTimeout(3_000);
        config.setMaxLifetime(1_800_000);
        config.setPoolName("OrderServicePool");

        // Validation query (Hikari default: SELECT 1 for PG)
        config.setConnectionTestQuery("SELECT 1");

        // Add pool metrics to Micrometer (Spring Boot Actuator)
        config.setMetricRegistry(
            /* inject Micrometer MeterRegistry */ null);

        return new HikariDataSource(config);
    }
}
```

**Example 3 - Monitoring pool exhaustion:**

```java
// Check pool stats at runtime via JMX or Actuator
// With spring-boot-actuator, metrics are auto-exposed:

// Pool size metrics (Micrometer/Prometheus):
// hikaricp.connections.active{pool="OrderServicePool"}
// hikaricp.connections.idle{pool="OrderServicePool"}
// hikaricp.connections.pending{pool="OrderServicePool"}
// hikaricp.connections.acquire (acquisition time histogram)

// Detect pool exhaustion in logs:
// HikariPool-1 - Connection is not available,
//   request timed out after 3000ms

// SQL to check active connections on PostgreSQL:
// SELECT count(*) FROM pg_stat_activity
//   WHERE datname = 'orders';
```

---

### ⚖️ Comparison Table

| Pool         | Acquisition Speed  | Default in Spring Boot | Notable Feature                |
| ------------ | ------------------ | ---------------------- | ------------------------------ |
| **HikariCP** | ~1µs (uncontended) | ✅ Since Boot 2.0      | Lock-free ConcurrentBag        |
| Tomcat JDBC  | ~50µs              | Boot 1.x               | Mature, many config options    |
| DBCP2        | ~100µs             | Apache Commons         | Simple, well-understood        |
| c3p0         | Slower             | No                     | Verbose config, older codebase |
| PgBouncer    | N/A (proxy)        | No (external)          | Connection pooling outside JVM |

How to choose: Use HikariCP (the default) for virtually all Spring Boot applications. Use PgBouncer as an additional layer for PostgreSQL at very high scale (thousands of application connections needing to multiplex into a smaller DB connection count).

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                      |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Bigger pool = better performance                                        | Pool size beyond ~20-30 causes lock contention on the DB side; Postgres documentation recommends keeping connections as few as necessary     |
| You can safely open connections manually alongside the pool             | Direct `DriverManager.getConnection()` bypasses the pool entirely - always use `dataSource.getConnection()`                                  |
| Pool exhaustion means the DB is slow                                    | It usually means pool-size is too small for your concurrency level, OR a code path is holding connections too long (transactions not closed) |
| `connection.close()` in application code closes the physical connection | HikariCP intercepts `close()` and returns the connection to the pool - the physical connection stays open                                    |
| `minimum-idle` should always equal `maximum-pool-size`                  | In environments with variable load (serverless, infrequent use), minimum-idle < maximum-pool-size saves DB resources during quiet periods    |

---

### 🚨 Failure Modes & Diagnosis

**1. Pool Exhaustion - All Connections In Use**

**Symptom:** Application hangs; threads accumulate; eventually `SQLTransientConnectionException: Connection is not available, request timed out after 3000ms`.

**Root Cause:** Pool is sized too small for concurrent load, OR transactions are not being closed (connections leaked).

**Diagnostic:**

```bash
# Check pool metrics via Actuator
curl http://localhost:8080/actuator/metrics/\
  hikaricp.connections.pending

# Check for unreturned connections
curl http://localhost:8080/actuator/metrics/\
  hikaricp.connections.active

# Enable leak detection threshold
# application.properties:
spring.datasource.hikari.leak-detection-threshold=5000
# Logs stack trace of any connection held > 5s
```

**Fix:**

```java
// BAD: connection not closed on exception path
Connection conn = dataSource.getConnection();
Statement stmt = conn.createStatement();
stmt.execute("UPDATE orders SET status='processed'");
// Exception here → conn never returned to pool → leak

// GOOD: use try-with-resources
try (Connection conn = dataSource.getConnection();
     Statement stmt = conn.createStatement()) {
    stmt.execute("UPDATE orders SET status='processed'");
} // conn.close() called automatically → returned to pool
```

**Prevention:** Always use Spring's `JdbcTemplate` or `@Transactional` - they manage connection lifecycle automatically. Enable `leak-detection-threshold` in all environments.

---

**2. Stale Connections After DB Restart**

**Symptom:** After database server restart or network interruption, application throws `Communications link failure` or `Connection reset`; resolves after some minutes.

**Root Cause:** HikariCP pool still holds references to TCP connections that are now dead (the DB server reset them). The pool doesn't know the connections are stale until it tries to use them.

**Diagnostic:**

```bash
# Look for connection reset errors in logs
grep "Communications link failure\|Connection reset" app.log

# Check HikariCP eviction in logs (DEBUG level)
# "Connection ... has been evicted (reset)"
```

**Fix:**

```properties
# Set max-lifetime below DB's wait_timeout (MySQL)
# or tcp_keepalives_idle (PostgreSQL)
spring.datasource.hikari.max-lifetime=600000   # 10 min
spring.datasource.hikari.keepalive-time=60000  # 1 min pings

# Enable test-on-borrow (slightly slower but catches stales)
spring.datasource.hikari.connection-test-query=SELECT 1
```

**Prevention:** Configure `keepalive-time` (background pings to keep TCP alive) and `max-lifetime` (force recycle connections before they go stale) to shorter intervals than the database's idle timeout.

---

**3. Pool Size Causing DB Connection Limit Exhaustion**

**Symptom:** Database logs show `too many connections`; new client connections fail; multiple application pods each trying to hold their full pool.

**Root Cause:** 10 pods × pool-size=20 = 200 connections. PostgreSQL's `max_connections` is 100. All pods compete for limited DB connections.

**Diagnostic:**

```sql
-- Check active connections on PostgreSQL
SELECT count(*), application_name
FROM pg_stat_activity
GROUP BY application_name
ORDER BY count DESC;
```

**Fix:**

```properties
# Reduce pool size for horizontally-scaled deployments
# Total connections = pods × pool-size < max_connections
# 10 pods, max_connections=100 → pool-size=8 per pod
spring.datasource.hikari.maximum-pool-size=8

# Or add PgBouncer as an external connection pooler
# to multiplex many app connections into fewer DB connections
```

**Prevention:** Calculate maximum total connections as a function of pod count and pool size before deploying at scale. Consider an external pooler (PgBouncer) for PostgreSQL at high connection volume.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JDBC` - HikariCP is a JDBC connection pool; understand the `Connection`/`Statement`/`ResultSet` lifecycle first
- `Connection Pooling` - the general concept that HikariCP implements
- `Database Fundamentals` - understanding DB connection limits and transaction overhead contextualizes pool sizing

**Builds On This (learn these next):**

- `Spring Data JPA` - uses HikariCP under the hood; understanding the pool helps diagnose JPA performance issues
- `Transaction Management (@Transactional)` - Spring transactions borrow a HikariCP connection for the transaction duration
- `Observability & SRE` - HikariCP metrics (active/idle/pending connections) are critical production signals

**Alternatives / Comparisons:**

- `DBCP2` - older Apache Commons pool; simpler but slower; used when HikariCP is unavailable
- `PgBouncer` - external server-side pool for PostgreSQL; multiplexes JVM connections; useful at massive scale
- `Tomcat JDBC Pool` - Spring Boot 1.x default; still functional but HikariCP is preferred

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Spring Boot's default JDBC connection     │
│              │ pool - pre-creates and reuses DB conns    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Creating a DB connection per request is   │
│ SOLVES       │ 50–200ms and exhausts DB limits           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ acquisition overhead < 1µs vs 150ms cold  │
│              │ open; pool bounds DB connection count     │
├──────────────┼───────────────────────────────────────────┤
│ KEY SETTINGS │ maximum-pool-size=10, connection-timeout  │
│              │ =3000, max-lifetime=1800000               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ Pool size × pods > DB max_connections     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Memory for idle connections vs. speed     │
│              │ and bounded resource usage                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "It's a rental fleet - borrow a DB        │
│              │  connection, use it, return it"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring Data JPA → @Transactional →        │
│              │ Observability metrics                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE B - Scale) Your Spring Boot service runs with 20 pods, each with HikariCP `maximum-pool-size=10`. Your PostgreSQL instance has `max_connections=150`. You want to scale to 30 pods during a peak event. What happens when pod 21 starts? How do you safely increase pod count without hitting the DB connection ceiling? What is the minimum configuration change that makes this safe?

**Q2.** (TYPE D - Debugging) A production alert fires: `hikaricp.connections.pending > 0` is non-zero for more than 60 seconds. The pool size is 10, but the service is receiving only 5 requests per second, each querying for less than 1ms. What three distinct root causes could explain this pool starvation scenario, and what diagnostic step would distinguish between them?
