---
id: JPH-047
title: "Connection Pooling with JPA (HikariCP)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-012, JPH-013, JPH-026, JPH-046
used_by: JPH-048, JPH-054, JPH-061
related: JPH-039, JPH-045, JPH-046, JPH-061
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/jpa-hibernate/connection-pooling-jpa/
---

⚡ **TL;DR** - HikariCP is the default Spring Boot
connection pool. It pre-creates and reuses JDBC connections.
Key settings: `maximumPoolSize` (default 10; set to
number of CPU cores x 2 for compute-heavy, or lower
for I/O-bound workloads), `connectionTimeout` (max wait
for a pool connection; default 30s; set to 5-10s in
production), `idleTimeout` (when to retire idle connections;
default 10m), `maxLifetime` (max connection lifetime;
set slightly below DB server timeout to avoid stale connections).
Pool exhaustion = `SQLTimeoutException` at scale.

| #047            | Category: JPA & Hibernate                                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | EntityManager, JPA Persistence Unit, JPA Lifecycle, @Transactional, Hibernate Statistics |                 |
| **Used by:**    | Multi-Tenancy, JPA at Scale, JPA with Multiple Databases                                 |                 |
| **Related:**    | Pessimistic Locking, Batch Processing, Hibernate Statistics, Multiple Databases          |                 |

---

### 🔥 The Problem This Solves

**WITHOUT CONNECTION POOLING:**
Every JDBC operation creates a new TCP connection to the
database. A TCP connection requires: TCP handshake
(~1-3ms), TLS handshake (~5-10ms if SSL), authentication
(~5-10ms). For a request needing 5 queries: 5 connections

- 15ms overhead = 75ms of pure connection overhead per
  request. At 1,000 req/sec: 1,000 connections/sec to
  the database - which typically has a hard limit of 100-500
  max connections.

**WITH HIKARICP:**

- Pool of 10 pre-created connections
- Request gets an existing connection from pool (< 1ms)
- Returns connection when transaction commits
- Database sees 10 persistent long-lived connections
- 1,000 req/sec all share 10 connections (connections reused)

---

### 📘 Textbook Definition

**HikariCP** (Hikari Connection Pool) is a JDBC connection
pool library, the default pool for Spring Boot. It maintains
a pool of pre-created JDBC `Connection` objects that can
be borrowed by application threads and returned after use.

**Key configuration properties:**

| Property            | Default                | Description                                                  |
| ------------------- | ---------------------- | ------------------------------------------------------------ |
| `maximumPoolSize`   | 10                     | Max connections in pool (max concurrent DB queries)          |
| `minimumIdle`       | equals maximumPoolSize | Minimum idle connections to maintain                         |
| `connectionTimeout` | 30000 ms               | Max time to wait for a connection from pool                  |
| `idleTimeout`       | 600000 ms (10min)      | Remove idle connections after this time                      |
| `maxLifetime`       | 1800000 ms (30min)     | Max age of a connection before it's retired                  |
| `keepaliveTime`     | 0 (disabled)           | Interval to send keepalive query (e.g., `SELECT 1`)          |
| `validationTimeout` | 5000 ms                | Timeout for connection validation (isValid check)            |
| `connectionInitSql` | none                   | SQL to run when connection is created (e.g., `SET timezone`) |

**How it works:**

1. At startup: create `minimumIdle` connections
2. On borrow: return an idle connection immediately (< 1ms)
3. If no idle connection and pool not full: create new connection
4. If pool full: wait up to `connectionTimeout`; throw if exceeded
5. On return: validate and return to pool (or close if maxLifetime exceeded)

---

### ⏱️ Understand It in 30 Seconds

**One line:** HikariCP keeps a pool of pre-created
database connections for reuse, eliminating connection
setup overhead on every query.

**One analogy:**

> Database connections are like rental cars at an airport.
> Without pooling: every traveler waits for a new car to
> be manufactured when they arrive (TCP connection setup).
> With pooling: a fleet of 10 cars is always ready in the
> lot (the pool). Traveler grabs a key (borrows connection),
> drives (runs queries), returns the car (connection
> returned to pool). The fleet is always ready; no wait for
> manufacturing. Pool too small: travelers wait for a car.
> Pool too large: more cars than parking spaces (DB max connections).

**One insight:** The correct pool size is NOT "as large as
possible." A pool of 100 connections with 10 CPU cores just
means 100 threads competing for the same CPU, which is slower
than 10 threads each with full CPU access. The formula:
`pool_size = (core_count * 2) + effective_spindle_count`
(HikariCP docs). For modern cloud databases: ~10-20 connections
is often optimal for a single application instance.

---

### 🔩 First Principles Explanation

**CONNECTION BORROW AND RETURN SEQUENCE:**

```
Application thread:
  em.find(Product.class, id)   <-- transaction start
    -> DataSource.getConnection()
       -> HikariCP pool check:
          idle connections available? YES: return idle
            connection
          NO, pool not full: create new JDBC connection
            (slow!)
          NO, pool full: wait up to connectionTimeout
            -> if timed out: SQLTimeoutException
    -> JDBC: SELECT FROM products WHERE id=?
    -> return ResultSet
  @Transactional method returns  <-- transaction end
    -> conn.commit()
    -> HikariCP: return connection to pool
       -> mark as idle (available for next borrow)

Note: JPA does NOT hold the JDBC connection for the full
@Transactional duration in all cases. Spring's
HibernateTransactionManager acquires the connection at
the first flush/query (lazy acquisition). The connection
is released after flush, then re-acquired for the next
flush within the same transaction.
```

**POOL EXHAUSTION:**

```
Pool max=10, all 10 connections borrowed:
  Thread 11 calls DataSource.getConnection()
  -> Pool is full
  -> Thread 11 waits (connectionTimeout=30s)
  -> After 30s: throw SQLTimeoutException
     (wrapped as CannotGetJdbcConnectionException by
       Spring)

Visible in logs:
  HikariPool-1 - Connection is not available,
  request timed out after 30000ms.

Root cause: connections held too long (long transactions,
N+1 queries accumulating connection hold time, deadlocks)
```

---

### 🧪 Thought Experiment

**OPTIMAL POOL SIZE - THE BENCHMARK PARADOX:**

```
Scenario: 100 concurrent requests, each needs 1 DB query
Database server: 8 cores

Pool size 100 (100 concurrent connections):
  100 requests: each gets a connection immediately
  But: 100 connections compete for 8 DB CPU cores
  DB switches between 100 "threads" (connections)
  Context switches + memory for 100 connections
  Throughput: X req/sec

Pool size 10 (10 concurrent connections):
  First 10 requests: get connections immediately
  Next 90 requests: queue in pool (in Java, not DB)
  DB processes 10 at a time (8 cores = optimal)
  Less context switching; better CPU utilization
  Throughput: 1.2X req/sec  (20% better than pool=100!)

This is counterintuitive but empirically observed.
HikariCP documentation: "If you have a 10 core machine,
a connection pool of 10 may be ideal for the database."
```

---

### 🧠 Mental Model / Analogy

> A JDBC connection pool is like a supermarket checkout
> with N lanes. Opening more lanes (more connections)
> does not infinitely improve throughput - if you open
> 100 lanes but only have 10 cashiers (DB cores), 90 lanes
> are waiting for the same 10 cashiers. The queue just
> moves from "waiting for a lane" (waiting for pool
> connection) to "waiting for a cashier" (DB CPU contention).
> The right number of lanes = number of cashiers (DB cores).
> `maximumPoolSize = DB_CPU_cores * 2` is the rule of thumb.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
HikariCP keeps a set of pre-made database connections
ready to use. When a query runs, it borrows one from
the pool (fast) instead of creating a new one (slow).
After the query, the connection is returned for reuse.

**Level 2 - How to configure it (junior developer):**

```properties
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.connection-timeout=5000
spring.datasource.hikari.idle-timeout=600000
spring.datasource.hikari.max-lifetime=1800000
```

**Level 3 - Key failure modes (mid-level engineer):**
Pool exhaustion: all connections borrowed; new requests
wait and timeout (HTTP 503 symptoms). Stale connections:
connection older than DB server's `wait_timeout` is
closed by DB; next use gets a broken connection. Fix:
set `maxLifetime` slightly below DB server timeout;
enable `keepaliveTime` for long-idle connections.

**Level 4 - Pool sizing (senior engineer):**
Formula: `pool_size = (core_count * 2) + effective_spindle_count`
(HikariCP official recommendation). For AWS RDS `db.t3.medium`
(2 vCPUs): pool = 2\*2 + 1 = 5 per app instance. With 10
app instances: total 50 DB connections. Check RDS
`max_connections` parameter: for db.t3.medium, ~85 max.
50 connections from 10 app instances leaves headroom for
management tools and DBA sessions.

**Level 5 - Transaction-aware connection management (staff engineer):**
Spring's `@Transactional` + HikariCP interaction: the JDBC
connection is acquired on first database operation within
the transaction (lazy acquisition), not at `@Transactional`
method entry. This means: a `@Transactional` method that
does non-DB work before its first query does NOT hold a
connection during that non-DB work. But long-running
methods with multiple DB operations hold the connection
for the entire span. Minimize connection hold time: do
all DB work upfront in a transaction, then do non-DB
work (external API calls, heavy computation) outside.

---

### ⚙️ How It Works (Mechanism)

**HIKARICP SPRING BOOT CONFIGURATION:**

```properties
# Full HikariCP configuration for production:
spring.datasource.url=jdbc:postgresql://host:5432/db
spring.datasource.username=app
spring.datasource.password=${DB_PASSWORD}
spring.datasource.driver-class-name=org.postgresql.Driver

spring.datasource.hikari.pool-name=AppPool
# Max concurrent JDBC connections:
spring.datasource.hikari.maximum-pool-size=20
# Minimum idle connections (set to maximumPoolSize
# to avoid pool resizing overhead):
spring.datasource.hikari.minimum-idle=20
# Max wait for connection from pool (ms):
spring.datasource.hikari.connection-timeout=5000
# Idle connection retirement (ms) - 10 min:
spring.datasource.hikari.idle-timeout=600000
# Max connection lifetime (ms) - 28 min (below MySQL
# default wait_timeout of 480s/8min for cloud DBs
# or 28800s for standard MySQL):
spring.datasource.hikari.max-lifetime=1680000
# Keepalive query interval (ms) - prevent firewall
# dropping idle connections after 5 min:
spring.datasource.hikari.keepalive-time=300000
# Validation query (HikariCP validates via Connection.isValid()
# by default; this overrides for DBs that need explicit ping):
# spring.datasource.hikari.connection-test-query=SELECT 1
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MONITORING POOL HEALTH:**

```java
@Component
@RequiredArgsConstructor
public class HikariPoolMonitor {

    private final DataSource dataSource;

    @Scheduled(fixedDelay = 60_000)
    public void logPoolStats() {
        if (dataSource instanceof HikariDataSource hds) {
            HikariPoolMXBean pool =
                hds.getHikariPoolMXBean();
            int total   = pool.getTotalConnections();
            int active  = pool.getActiveConnections();
            int idle    = pool.getIdleConnections();
            int waiting = pool.getThreadsAwaitingConnection();

            log.info("HikariCP: total={}, active={}, " +
                "idle={}, waiting={}",
                total, active, idle, waiting);

            if (waiting > 0) {
                log.warn("Connection pool pressure: " +
                    "{} threads waiting", waiting);
            }
            if (active == total) {
                log.warn("Pool at capacity: {}/{} active",
                    active, total);
            }
        }
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: holding DB connection during external call:**

```java
// BAD: connection held during slow HTTP call
@Transactional
public OrderConfirmation processOrder(Long orderId) {
    Order order = orderRepo.findById(orderId).orElseThrow();
    order.setStatus("PROCESSING");
    // Connection is HELD from orderRepo.findById above

    // SLOW: external payment API call (100-2000ms)
    PaymentResult result = paymentClient.charge(order);
    // Other requests wait for this connection during 2 seconds

    order.setStatus(result.isSuccess() ? "CONFIRMED" : "FAILED");
    return confirm(order);
}

// GOOD: minimize connection hold time
public OrderConfirmation processOrder(Long orderId) {
    // Step 1: Load and update status (separate transaction)
    orderService.markProcessing(orderId);

    // Step 2: External call (no transaction, no connection)
    PaymentResult result = paymentClient.charge(
        orderService.getOrderForPayment(orderId));

    // Step 3: Finalize status (separate transaction)
    return orderService.finalizeOrder(orderId, result);
    // Total connection hold: ~5ms per transaction
}
```

**Example 2 - Verifying pool configuration:**

```java
@SpringBootTest
class HikariConfigTest {
    @Autowired DataSource ds;

    @Test
    void poolConfigIsCorrect() {
        HikariDataSource hds = (HikariDataSource) ds;
        assertThat(hds.getMaximumPoolSize()).isEqualTo(20);
        assertThat(hds.getConnectionTimeout()).isEqualTo(5000);
        assertThat(hds.getMaxLifetime())
            .isLessThan(1800000); // below DB server timeout
    }
}
```

---

### ⚖️ Comparison Table

| Pool           | Default in Spring Boot | Key features                       | Best for             |
| -------------- | ---------------------- | ---------------------------------- | -------------------- |
| HikariCP       | Yes (Spring Boot 2+)   | Fast, minimal footprint, JMX       | All Spring Boot apps |
| DBCP2 (Apache) | No                     | Battle-tested, more config options | Legacy apps          |
| C3P0           | No                     | Older, complex config              | Legacy apps          |
| Tomcat JDBC    | No (was 1.x default)   | Tomcat-aware                       | Embedded Tomcat      |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                                                                                                |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Larger pool = better performance"           | Counter-intuitively, very large pools reduce throughput. Too many connections cause DB CPU context switching and memory overhead. Pool size should match DB CPU count \* 2, not the number of app threads.                                                                                             |
| "connection-timeout is the DB query timeout" | `connectionTimeout` is how long to WAIT for a connection from the POOL - not how long a query is allowed to run. Set `spring.jpa.properties.hibernate.jdbc.time_out` or `javax.persistence.query.timeout` for query timeouts.                                                                          |
| "maxLifetime being large is safe"            | If `maxLifetime` is longer than the DB server's connection idle timeout (e.g., MySQL `wait_timeout` default 8 hours), the DB server may close the connection, but HikariCP doesn't know it's dead. Next use: `SocketException: broken pipe`. Set `maxLifetime` < `wait_timeout` by at least 2 minutes. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Connection Pool Exhaustion**

**Symptom:** `Unable to acquire JDBC Connection` /
`HikariPool-1 - Connection is not available, request
timed out after 30000ms`. Users get HTTP 503.

**Root Cause:** All pool connections are borrowed and
not being returned. Common causes: (1) `@Transactional`
methods holding connections during external HTTP calls,
(2) long-running queries holding connections, (3) deadlocks
preventing transaction commit (connection never returned).

**Diagnosis:**

```java
// At runtime:
HikariPoolMXBean pool = hds.getHikariPoolMXBean();
log.info("Waiting threads: {}",
    pool.getThreadsAwaitingConnection());
log.info("Active: {}, Total: {}",
    pool.getActiveConnections(),
    pool.getTotalConnections());
// If active = total: pool fully exhausted
// If waiting > 0: active exhaustion occurring
```

**Fix:** (1) Reduce `@Transactional` scope (no external
calls inside), (2) increase `maximumPoolSize` temporarily,
(3) set shorter `connectionTimeout` to fail fast with
clear 503 instead of 30s hang.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-026 - @Transactional]] - transactions determine
  how long connections are held
- [[JPH-046 - Hibernate Statistics]] - `connectCount`
  metric shows connection acquisition frequency

**Builds On This (learn these next):**

- [[JPH-048 - Multi-Tenancy]] - multi-tenant apps often
  need multiple data sources and connection pools
- [[JPH-061 - JPA with Multiple Databases]] - routing
  DataSource uses multiple HikariCP pools

**Related:**

- [[JPH-039 - Pessimistic Locking]] - locks held in DB
  hold connections until commit; connection pool interaction
- [[JPH-045 - Batch Processing]] - batch operations hold
  connections for longer; pool sizing must account for this

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ MAX SIZE     │ hikari.maximum-pool-size (default 10)    │
│ RULE         │ core_count * 2 (not "as large as possible│
├──────────────┼──────────────────────────────────────────┤
│ CONN TIMEOUT │ hikari.connection-timeout=5000 (5 sec)   │
│              │ NOT query timeout; pool wait time        │
├──────────────┼──────────────────────────────────────────┤
│ MAX LIFETIME │ Set below DB server wait_timeout - 2 min │
│              │ Prevents stale connection errors         │
├──────────────┼──────────────────────────────────────────┤
│ EXHAUSTION   │ active == total -> pool full; threads wai│
│ FIX          │ Reduce tx scope; move external calls out │
├──────────────┼──────────────────────────────────────────┤
│ MONITOR      │ HikariPoolMXBean.getActiveConnections()  │
│              │ Spring Actuator: /actuator/metrics/      │
│              │   hikaricp.connections.active            │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "HikariCP = default Spring Boot pool;    │
│              │ size = cores*2; connection-timeout = pool│
│              │ wait, not query; maxLifetime < DB timeout│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `maximumPoolSize = cores * 2`, not "as large as possible" -
   more connections than DB can handle causes CPU contention
2. `connectionTimeout` is POOL wait time (throw if no free connection),
   not query execution timeout
3. `maxLifetime` must be set BELOW the DB server's connection
   idle timeout to prevent "broken pipe" stale connection errors

**Interview one-liner:** HikariCP is Spring Boot's default
JDBC connection pool. `maximumPoolSize` should be `db_cores * 2`
(not unlimited). `connectionTimeout` controls how long to wait
for a pool connection (not query time). `maxLifetime` must be
below the DB server's `wait_timeout` to prevent stale connections.
Pool exhaustion (all connections borrowed) causes `SQLTimeoutException`.
Root cause: long-running transactions or external API calls inside
`@Transactional` holding connections.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Resource pools
(connection pools, thread pools, object pools) are a
universal concurrency pattern. Key properties: (1) pool size
= number of resources the CONSUMER (DB, downstream service)
can handle concurrently (not caller concurrency),
(2) timeout = fail fast rather than infinite wait (prevents
cascading failures), (3) health check = validate resources
periodically (keepalive, isValid), (4) max lifetime = retire
resources to prevent staleness. These principles apply to:
HTTP client connection pools (`HttpClient.maxConnectionsPerRoute`),
thread pools (`ThreadPoolExecutor.corePoolSize`), message
consumer pools, Redis connection pools, gRPC channel pools.

**Where else this pattern appears:**

- **OkHttp ConnectionPool** - same maxIdleConnections,
  keepAliveDuration for HTTP client pooling
- **Redis Lettuce/Jedis pool** - maxTotal, maxIdle, maxWaitMillis
  = exact same parameters as HikariCP but for Redis connections
- **AWS SDK connection pool** - `ApacheHttpClient.maxConnections()`
  for S3, DynamoDB client pooling

---

### 💡 The Surprising Truth

HikariCP measures its maximum pool acquisition time in
a unique way. The `connectionTimeout` (default: 30,000ms)
is not just the wait for a connection - it includes the
time to create a NEW connection if the pool needs to grow.
Creating a connection requires the TCP + TLS + auth
handshake (10-50ms on a local network, 100-500ms across
availability zones). If your DB is across an AZ and
connection setup takes 200ms, and your pool is empty at
startup, the first 10 requests will each wait for a
new connection. If you set `minimum-idle=maximum-pool-size`
(= eager connection creation at startup), HikariCP
creates all connections when the application starts,
not when first needed. This eliminates "cold start"
latency spikes but slows down application startup.
The Spring Boot default `minimum-idle = maximum-pool-size`
already does this - all 10 connections are created at
startup. Change `minimum-idle < maximum-pool-size` only
if pool growth latency during load spikes is acceptable.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **CONFIGURE** HikariCP for a production Spring Boot
   app with appropriate `maximumPoolSize`, `connectionTimeout`,
   and `maxLifetime`
2. **EXPLAIN** why larger pool size does not always improve
   throughput (DB CPU contention)
3. **DIAGNOSE** pool exhaustion using `HikariPoolMXBean`
   metrics and identify the root cause (long transactions)
4. **SET** `maxLifetime` correctly relative to the DB
   server's `wait_timeout` to prevent stale connections
5. **MINIMIZE** connection hold time by restructuring
   `@Transactional` methods that make external calls

---

### 🎯 Interview Deep-Dive

**Q1: What is the ideal HikariCP pool size for an
application with 200 concurrent requests?**
_Why they ask:_ Tests understanding of pool sizing.
_Strong answer includes:_

- NOT 200 (not one connection per thread)
- Formula: `pool_size = db_cpu_cores * 2`
- With 8-core DB: pool = 16; 200 requests share 16 connections
- 200 requests queue in HikariCP (microsecond wait); 16 process
  at DB simultaneously; DB CPU fully utilized, no contention
- Setting pool=200: 200 DB connections compete for 8 CPU cores
  -> context switches, memory overhead, SLOWER than pool=16

**Q2: An application starts getting "Connection is not available"
errors at peak load. How do you diagnose and fix this?**
_Why they ask:_ Tests production troubleshooting.
_Strong answer includes:_

- Diagnosis: check `HikariPoolMXBean.getActiveConnections()` vs `getTotalConnections()`
  - if active = total: pool exhausted
  - check `getThreadsAwaitingConnection()` - should be 0 normally
- Common causes: (1) long `@Transactional` scope including external calls,
  (2) slow queries holding connections, (3) deadlocks preventing commit
- Short-term fix: increase `maximumPoolSize` (buy time); set shorter
  `connectionTimeout` to fail fast (503 better than 30s hang)
- Long-term fix: reduce transaction scope; move external calls outside
  `@Transactional`; optimize slow queries; fix deadlocks
