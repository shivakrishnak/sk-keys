---
layout: default
title: "HikariCP"
parent: "Spring & Spring Boot"
nav_order: 132
permalink: /spring/hikaricp/
number: "132"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "JDBC, Connection Pooling, @Transactional, DataSource"
used_by: "@Transactional, JPA, N+1 Problem, Lazy Loading, Auto-Configuration"
tags: #java, #spring, #springboot, #database, #intermediate, #performance
---

# 132 — HikariCP

`#java` `#spring` `#springboot` `#database` `#intermediate` `#performance`

⚡ TL;DR — Spring Boot's default JDBC connection pool — maintains a pool of pre-opened database connections for reuse, eliminating the 5–200ms overhead of opening a new TCP+TLS+auth connection per query.

| #132 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JDBC, Connection Pooling, @Transactional, DataSource | |
| **Used by:** | @Transactional, JPA, N+1 Problem, Lazy Loading, Auto-Configuration | |

---

### 📘 Textbook Definition

**HikariCP** (Hikari Connection Pool) is a high-performance JDBC connection pool library that is the default `DataSource` in Spring Boot since 2.0. It maintains a pool of pre-opened `java.sql.Connection` objects to a database. When a transaction or query needs a connection, it borrows one from the pool (blocking up to `connectionTimeout` if all are in use) and returns it when the transaction commits or rolls back. HikariCP is notable for its minimal overhead, aggressive connection validation, `connectionTimeout` and `maximumPoolSize` configuration, and connection health checks via `keepAliveTime`. Spring Boot auto-configures it from `spring.datasource.hikari.*` properties.

---

### 🟢 Simple Definition (Easy)

HikariCP is a connection pool — instead of opening a new database connection every time you run a query (slow), it keeps a set of pre-opened connections ready to be reused immediately.

---

### 🔵 Simple Definition (Elaborated)

Opening a database connection involves a TCP handshake, TLS negotiation, authentication, and session setup — typically 5–200ms. Without pooling, every database operation would pay this cost. HikariCP opens a fixed number of connections at startup and keeps them alive. When your application needs a connection (for a `@Transactional` method), it borrows one from the pool in microseconds. When the transaction ends, the connection is returned — not closed — so the next request gets it instantly. Pool configuration is critical: too few connections cause queuing, too many consume DB server resources.

---

### 🔩 First Principles Explanation

**The connection cost problem:**

```
Without pooling, per-request cost:
  1. TCP 3-way handshake:        ~1-5ms
  2. TLS negotiation:            ~10-50ms
  3. DB authentication:          ~5-20ms
  4. Session/context setup:      ~1-5ms
  Total overhead per query:      ~17-80ms

At 1000 RPS, each with 1 DB query:
  1000 × 80ms = 80 seconds of DB handshake overhead/sec
  → Impossible

With HikariCP (20 pooled connections):
  Borrow from pool:              ~0.3μs
  Same 1000 RPS queued against 20 connections
  Each connection handles 50 requests/sec
  → Feasible
```

**HikariCP's pool state machine:**

```
┌─────────────────────────────────────────────────────┐
│  CONNECTION STATES                                  │
│                                                     │
│  IDLE ←──────────── connection returned             │
│    ↓                                                │
│  IN_USE ← borrowed for transaction                  │
│    ↓                                                │
│  Returned to pool after TX commit/rollback          │
│                                                     │
│  EVICTED ← keepAliveTime exceeded or validation fail│
│    ↓                                                │
│  New connection opened to replace                   │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT connection pooling:**

```
Without pooling:

  Simple DataSource (DriverManager.getConnection()):
    Every query: new TCP + TLS + auth + session
    → 50-200ms overhead per query
    → At 100 concurrent users: 100 × connection setup

  Resource exhaustion:
    Database has max_connections=200
    Without pool: 200 open at all times + setup overhead
    → DB exhausted for 201st user

  No health recovery:
    Dead connection from network fault:
    → SQLException at query time, not at borrow time
    → Request fails; no automatic reconnection
```

**WITH HikariCP:**

```
→ Borrow in microseconds — no TCP overhead
→ Connection reuse: setup paid once at startup
→ Pool size: controls max concurrent DB queries
→ connectionTimeout: fail fast if pool exhausted
→ keepAliveTime: evict stale connections proactively
→ Connection validation: evict failed connections
   and replace with fresh ones transparently
→ Pool metrics: Micrometer integration for alerting
```

---

### 🧠 Mental Model / Analogy

> HikariCP is like a **taxi dispatch service** with a fleet of pre-positioned cabs. Without pooling: every ride request summons a car from the factory (5–200ms manufacturing time). With HikariCP: a fleet of 20 cabs is always parked nearby (pool), ready to accept fares in seconds. `maximumPoolSize=20` = 20 cabs. `connectionTimeout=30000` = wait up to 30s for a free cab before giving up. `keepAliveTime` = periodically drive each idle cab around the block to keep it in working order.

"Cabs already positioned" = pre-opened pooled connections
"Accepting fare in seconds" = borrow connection in microseconds
"Fleet size" = maximumPoolSize
"Wait 30s before giving up" = connectionTimeout
"Drive idle cab around the block" = keepAliveTime validation

---

### ⚙️ How It Works (Mechanism)

**Key configuration properties:**

```yaml
spring:
  datasource:
    url: jdbc:postgresql://db:5432/app
    username: app
    password: secret
    hikari:
      # Max connections in pool (tuning critical)
      maximum-pool-size: 20
      # Min connections to maintain idly
      minimum-idle: 5
      # Time to wait for a free connection (ms)
      connection-timeout: 30000
      # Max time connection can be idle before eviction
      idle-timeout: 600000
      # Max connection lifetime (prevents stale conn)
      max-lifetime: 1800000
      # Proactive keepalive ping
      keepalive-time: 60000
      # Validation query (PostgreSQL: SELECT 1)
      connection-test-query: SELECT 1
      # Pool name for metrics labels
      pool-name: HikariPool-Primary
```

**Pool sizing formula:**

```
PostgreSQL recommendation:
  pool_size = (num_cores * 2) + num_disks

Practical formula:
  pool_size = (avg_query_time_ms / request_process_time_ms)
              × target_RPS

Example:
  avg_query: 10ms
  request_time: 100ms (10% in DB)
  target: 500 RPS
  pool_size = (10 / 100) × 500 = 50 connections
  Add 20% buffer → 60 connections

More connections ≠ better:
  DB has max_connections limit
  Too many → context-switching on DB server
  Many small pools (per microservice) > one large pool
```

**Micrometer metrics integration:**

```java
// Spring Boot auto-exposes HikariCP metrics via Actuator
// Access at: /actuator/metrics/hikaricp.connections

// key metrics:
// hikaricp.connections.active   — currently in use
// hikaricp.connections.idle     — waiting in pool
// hikaricp.connections.pending  — requests waiting for conn
// hikaricp.connections.timeout  — borrow timeout count
// hikaricp.connections.creation — time to open new conn

// Alert on:
// pending > 0 for > 30s → active connections may leak
// timeout > 0 → pool undersized or long transactions
```

---

### 🔄 How It Connects (Mini-Map)

```
@Transactional method called
        ↓
  HIKARICP (132)  ← you are here
  (borrows connection from pool)
        ↓
  Connection bound to ThreadLocal
  (TransactionSynchronizationManager)
        ↓
  @Transactional, JPA, JDBC queries
  all use this borrowed connection
        ↓
  TX commit/rollback
  → Connection RETURNED to pool (not closed)
        ↓
  Pool configuration impacts:
  N+1 Problem (130): each lazy query = borrow
  Lazy Loading (131): OSIV holds conn entire request
  REQUIRES_NEW propagation (128): borrows 2nd conn
```

---

### 💻 Code Example

**Example 1 — Connection pool exhaustion detection:**

```java
// Enable HikariCP metrics in Spring Boot Actuator
// GET /actuator/metrics/hikaricp.connections.pending

@SpringBootTest
@AutoConfigureMetrics
class ConnectionPoolTest {
  @Autowired MeterRegistry registry;

  @Test
  void poolShouldNotExhaustUnderNormalLoad() {
    // Run 100 concurrent requests
    IntStream.range(0, 100)
        .parallel()
        .forEach(i -> orderService.findByStatus("PENDING"));

    Double pending = registry
        .get("hikaricp.connections.pending")
        .gauge().value();
    assertThat(pending).isEqualTo(0.0);
    // Non-zero pending = pool too small OR connections leaked
  }
}
```

**Example 2 — Diagnosing connection leak:**

```bash
# Connection leak: connections borrowed but never returned
# Symptom: hikaricp.connections.active grows over time
# until connectionTimeout starts firing

# HikariCP has built-in leak detection:
spring:
  datasource:
    hikari:
      leak-detection-threshold: 2000  # ms
# Logs: CONNECTION LEAK DETECTION: a connection was
# not returned within 2000ms

# Common causes:
# - @Transactional missing on method that opens TX
# - Exception before return in manual connection code
# - OSIV holding connection through slow rendering
# - REQUIRES_NEW with insufficient pool size
```

**Example 3 — Multiple DataSources with separate pools:**

```java
@Configuration
public class DataSourceConfig {
  @Bean @Primary
  @ConfigurationProperties("spring.datasource.primary.hikari")
  HikariDataSource primaryDataSource() {
    return DataSourceBuilder.create()
        .type(HikariDataSource.class)
        .build();
    // Pool config from spring.datasource.primary.hikari.*
  }

  @Bean
  @ConfigurationProperties("spring.datasource.analytics.hikari")
  HikariDataSource analyticsDataSource() {
    return DataSourceBuilder.create()
        .type(HikariDataSource.class)
        .build();
    // Separate pool for heavy analytics queries
    // maximum-pool-size: 5 (analytics less critical)
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More connections always means better performance | After a threshold, more connections increase DB server context switching and actually hurt throughput. PostgreSQL recommends (cpu*2)+disks as a starting point |
| HikariCP creates connections lazily (on first use) | HikariCP pre-creates `minimumIdle` connections at startup and keeps that many warm. Connection creation happens at startup, not first use |
| connectionTimeout is the query execution timeout | connectionTimeout is the time to wait for a free connection from the POOL. Query timeout is `statement-timeout` or set via JDBC `setQueryTimeout()` |
| Pool validation query defeats the purpose of caching | Validation with `keepAliveTime` runs periodically on idle connections — it's not per-borrow by default. Per-borrow validation is configurable but rarely needed with modern DBs |

---

### 🔥 Pitfalls in Production

**1. Pool exhaustion from long @Transactional methods**

```java
// BAD: external HTTP call inside @Transactional
// Connection held during entire Stripe API call (200ms+)
@Transactional
public Receipt process(OrderRequest req) {
  Order order = orderRepo.save(Order.from(req));
  // DB connection held while waiting for Stripe!
  Receipt receipt = stripeClient.charge(req);  // 200ms
  order.setReceiptId(receipt.getId());
  return orderRepo.save(order);
}
// At 100 RPS × 200ms hold = 20 connections permanently busy
// Pool size 20 → all 20 held → 101st request waits

// GOOD: narrow @Transactional to DB-only operations
public Receipt process(OrderRequest req) {
  Long orderId = orderService.createOrder(req); // TX 1
  Receipt receipt = stripeClient.charge(req);    // no TX
  orderService.updateReceipt(orderId, receipt);  // TX 2
}
```

**2. Under-configured pool under spike traffic**

```yaml
# BAD: default pool size too small for spike load
spring.datasource.hikari.maximum-pool-size: 10
# Spike: 500 concurrent requests each needing a connection
# 490 requests waiting → connectionTimeout fires → 500 errors

# GOOD: set based on load test results + formula
spring.datasource.hikari.maximum-pool-size: 50
spring.datasource.hikari.connection-timeout: 3000

# Also: alert BEFORE exhaustion (Grafana/Prometheus)
# AlertRule: hikaricp.connections.pending > 0 for 10s
```

---

### 🔗 Related Keywords

- `DataSource` — the JDBC interface HikariCP implements as a pooling adapter
- `@Transactional` — borrows a connection from HikariCP at the start of each transaction
- `N+1 Problem` — each lazy query borrows a connection; N+1 = N pool borrows
- `Transaction Propagation REQUIRES_NEW` — opens a second connection from pool
- `Lazy Loading / OSIV` — OSIV keeps connection borrowed for full HTTP request
- `Micrometer` — HikariCP exposes `hikaricp.*` metrics for monitoring

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Pre-opened connection pool — borrow in    │
│              │ μs, return on TX end, reuse eliminates    │
│              │ TCP+auth overhead                         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (Spring Boot default). Tune pool   │
│              │ size from load test + formula             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never hold connections during external I/O│
│              │ → narrow @Transactional scope             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A fleet of pre-positioned taxis —        │
│              │  0.3μs to board vs. 80ms to manufacture." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Auto-Configuration (133) →                │
│              │ Spring Boot Actuator (134)                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** HikariCP's `maximumPoolSize` should be set to match the workload, not the database's `max_connections`. In a microservices deployment where 10 instances of the same service each configure `maximumPoolSize=20`, the total connections from this service alone is 200. Describe the total connection math across a cluster (10 services × 10 instances × pool=20 = 2,000 connections), explain why PostgreSQL's `max_connections=100 per database` default would be catastrophically too low, and describe how PgBouncer (a server-side connection pooler) changes this math.

**Q2.** HikariCP's internal implementation is famous for using a lock-free data structure (a custom `ConcurrentBag`) instead of traditional queue-based approaches. Explain the performance advantage of `ConcurrentBag` over a `LinkedBlockingQueue` approach for the borrow/return lifecycle — specifically what thread-local affinity means in this context and why it reduces CAS contention — and describe the specific failure mode under extremely high contention (thousands of threads) where even ConcurrentBag's optimistic approach degrades.

