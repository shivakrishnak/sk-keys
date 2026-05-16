---
id: SYD-031
title: "Connection Pooling (System Design)"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-005, SYD-008
used_by:
related: SYD-030
tags:
  - database
  - performance
  - intermediate
  - architecture
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /system-design/connection-pooling-system-design/
---

# SYD-031 - Connection Pooling (System Design)

⚡ TL;DR - Connection pooling reuses expensive database
connections so each request borrows one from a pool
instead of paying TCP+auth overhead on every query.

| #031            | Category: System Design             | Difficulty: ★★☆ |
| :-------------- | :---------------------------------- | :-------------- |
| **Depends on:** | What is Scalability, DB Replication |                 |
| **Used by:**    | -                                   |                 |
| **Related:**    | CDN Architecture Pattern            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every HTTP request that needs a database connection
opens a new TCP connection, performs a TLS handshake,
authenticates, and creates a server-side session -
all before executing a single SQL query. This setup
costs 20-50ms. At 1,000 requests per second, you
create and destroy 1,000 database connections per
second. PostgreSQL's connection limit is typically
100-300. At 100 concurrent requests, you are at the
limit. New requests fail with "too many connections."
The database spends 40% of its CPU managing
connection lifecycle rather than executing queries.

**THE BREAKING POINT:**
The database process model matters: PostgreSQL forks
a new OS process per connection. Each process
consumes 5-10MB of memory. 300 connections = 1.5-3GB
of RAM used just for connection overhead, before a
single byte of data is processed. MySQL uses threads
but the principle holds. Every un-pooled architecture
hits this wall.

**THE INVENTION MOMENT:**
"This is exactly why connection pooling was created"

- establish a fixed number of long-lived connections
  once and let multiple application requests reuse them.

**EVOLUTION:**
Application-level pools appeared with early JDBC
(Java, late 1990s). `c3p0` and then `HikariCP`
became the dominant Java pool implementations.
External poolers (PgBouncer for PostgreSQL, ProxySQL
for MySQL) emerged to decouple pooling from the
application tier. Serverless architectures (Lambda,
Cloud Run) reignited interest in external poolers
because function instances create fresh connections
on cold start.

---

### 📘 Textbook Definition

**Connection pooling** is a technique where a set of
pre-established database connections is maintained
(the pool) so application requests can borrow a
connection, use it, and return it to the pool, rather
than opening and closing a new connection per request.
The pool manages lifecycle (creation, validation,
eviction), concurrency (wait queues when all
connections are in use), and health (removing broken
connections). It trades connection resource overhead
for the constraint of a fixed pool size.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Connection pooling is like a hotel key card system:
you check out a key, use your room, and return the
key - the room is not demolished and rebuilt each time.

**One analogy:**

> A taxi company maintains a fleet of 20 cars on
> standby. When a customer calls, they get a car
> from the fleet. When done, the car returns to
> the fleet. The company does not manufacture a
> new car for every customer and scrap it after.
> The pool is the fleet. The connection is the car.

**One insight:**
Connection pools do not just reduce connection
setup cost - they protect the database from
connection storms. A pool with a maximum of 20
connections means no matter how many requests
arrive, the database never sees more than 20
concurrent connections. The pool is a throttle,
not just an optimization.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Database connection creation is expensive (TCP +
   auth = 20-50ms per connection).
2. Databases have a finite connection limit.
3. Most requests use a connection for only a few
   milliseconds.

**DERIVED DESIGN:**
Given that connections are expensive to create but
cheap to hold idle, and given that requests need
connections briefly, a pool of pre-created
connections that are borrowed and returned is the
optimal design. The pool must handle:

- **Borrowing:** thread-safe, with a configurable
  wait timeout
- **Validation:** check the connection is alive
  before lending
- **Eviction:** remove connections idle too long
  or after max lifetime

**Pool size formula (empirical baseline):**
`pool_size ≈ (core_count * 2) + effective_spindle_count`

For a 4-core server with SSD: `4 * 2 + 1 = 9`.
The DBAs at HikariCP documented this empirically.
More connections means more context switching
overhead, not more throughput.

**THE TRADE-OFFS:**
**Gain:** Near-zero connection setup cost per request.
Bounded database connections regardless of app tier
scale.

**Cost:** Fixed pool means requests may queue when
all connections are in use. Pool sizing is a
configuration knob that requires tuning. Overly small
pool causes request latency; overly large pool
causes database overload.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Managing concurrency and lifecycle
of shared resources is inherently complex.

**Accidental:** Every connection pool library has
different configuration parameters with confusing
defaults (idle timeout, max lifetime, validation
query). This is tooling complexity, not fundamental.

---

### 🧪 Thought Experiment

**SETUP:**
A web app has 50 concurrent HTTP requests. Each
request runs 3 database queries. Each query takes
5ms. Total DB time per request: 15ms. Connection
setup time: 30ms.

**WHAT HAPPENS WITHOUT CONNECTION POOL:**
Each request opens a new connection (30ms) + runs
queries (15ms) + closes connection = 45ms database
time. 50 concurrent requests open 50 connections.
At 1,000 RPS sustained, 1,000 connections/second
open and close. PostgreSQL buckles at 300 active
connections. Connection refused errors flood logs.

**WHAT HAPPENS WITH CONNECTION POOL (size=20):**
20 connections are established once at startup.
Each request borrows a connection (~0.1ms), runs
queries (15ms), returns connection. Total: 15.1ms
per request. Peak concurrency: 20 connections,
no matter how many HTTP requests arrive. 30 extra
concurrent requests queue for ~15ms until a
connection frees. The database sees ≤20 connections
at all times.

**THE INSIGHT:**
The pool converts O(requests) connections into
O(pool_size) connections. The database sees a
constant load regardless of traffic spikes.

---

### 🧠 Mental Model / Analogy

> Imagine a library with 10 reference books, each
> allowed to leave the library for 30 minutes. 200
> students want to read them simultaneously. Without
> a checkout system, students queue. The library
> never has 200 book requests outstanding - just
> 10 books in circulation. The checkout desk is the
> pool manager. The books are the connections.

Mapping:

- "Library books" → database connections
- "Checkout desk" → pool manager
- "Student" → application thread / request
- "30-minute limit" → connection max lifetime
- "Queue" → pool wait queue when all connections
  are in use

**Where this analogy breaks down:** Books do not
"wear out" from use. Database connections can become
stale (TCP half-open, server-side timeout, idle
eviction). The pool must validate connections before
lending them, which books do not require.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Connection pooling keeps a set of database connections
open and ready. Each request borrows one, uses it,
and gives it back. Avoids the cost of opening and
closing connections constantly.

**Level 2 - How to use it (junior developer):**
Use a pool library like HikariCP (Java), `psycopg2`
connection pool (Python), or `pg` Pool (Node.js).
Set `maximumPoolSize` to 10-20 as a starting point.
Configure `connectionTimeout` (how long to wait for
a connection from pool) and `idleTimeout` (when to
close unused connections).

**Level 3 - How it works (mid-level engineer):**
The pool maintains an available queue and a
borrowed queue. When borrowing: check available
queue, validate the connection (optional ping),
move to borrowed. When returning: run a reset
(ROLLBACK any uncommitted transaction), move back
to available. If pool is empty and max size reached,
the borrowing thread blocks until `connectionTimeout`
expires or a connection frees.

**Level 4 - Why it was designed this way (senior/staff):**
Pool size is counter-intuitively small for optimal
performance. More connections mean more parallelism,
right? No - the database processes queries on CPU
cores. With 8 cores and 200 connections, only 8
can run simultaneously; the other 192 context-switch
overhead wastes CPU. HikariCP's benchmark showed
pool_size = (cores \* 2) + 1 outperforms larger pools
in throughput. This is why the default HikariCP
`maximumPoolSize` is 10, not 100.

**Level 5 - Mastery (distinguished engineer):**
External poolers (PgBouncer) operate at a different
level than application pools. PgBouncer sits between
the application and PostgreSQL, multiplexing
thousands of "virtual" connections (from hundreds
of application instances) onto tens of real server
connections. In transaction pooling mode, it reuses
server connections across transactions from different
clients. This is essential in serverless environments
where Lambda functions create fresh application pools
on each cold start, potentially exhausting PostgreSQL's
connection limit. The architecture is: Lambda →
PgBouncer (10 real PG connections) → PostgreSQL.
Understanding when to use application-level vs.
external pooling is a staff-level architectural
decision.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│       CONNECTION POOL LIFECYCLE         │
│                                         │
│  App Thread 1: borrow ─────────────┐   │
│  App Thread 2: borrow ─────────────┤   │
│  App Thread 3: waiting (pool full)  │   │
│                                     │   │
│  Pool [conn1 IN-USE][conn2 IN-USE]  │   │
│       [conn3 IDLE  ][conn4 IDLE  ]  │   │
│                                     │   │
│  Thread 1: return conn1 ◀───────────┘   │
│  Pool [conn1 AVAIL ][conn2 IN-USE]      │
│  Thread 3: borrows conn1 ───────────┐   │
│                                         │
│  Validation: SELECT 1 (configurable)    │
│  Eviction: idle > maxIdleTime → close   │
└─────────────────────────────────────────┘
```

**Step 1 - Initialization:**
At application startup, the pool creates `minimumIdle`
connections to the database. Each connection executes
a TCP handshake, TLS (if configured), and auth.

**Step 2 - Borrow:**
Request arrives. Pool checks `availableQueue`. If
empty and `currentSize < maximumPoolSize`, a new
connection is created. If `currentSize == max`,
the request blocks until `connectionTimeout`.

**Step 3 - Use:**
The borrowed connection is used exclusively by the
requesting thread. No other thread touches it.

**Step 4 - Return:**
Thread calls `close()` on the connection object.
The pool intercepts this (proxying the real
connection), rolls back any open transactions,
and returns the connection to `availableQueue`.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
HTTP Request
  → App Server (Thread)
  → Pool.borrow()
      ← YOU ARE HERE (pool layer)
  → SQL query (5ms)
  → Pool.return()
  → HTTP Response
```

**FAILURE PATH:**

```
All 20 pool connections in use
  → New request blocks (waits up to 30s)
  → If timeout: SQLException "Connection
    pool timeout"
  → HTTP 503 to user
  → Alert: "pool exhausted" fires
  → Fix: increase pool size OR diagnose
    slow queries holding connections
```

**WHAT CHANGES AT SCALE:**
At 10x request rate, if queries are fast enough,
the pool handles it without resizing (connections
are returned and reused quickly). At 100x, slow
queries cause pool exhaustion - the fix is query
optimization, not a bigger pool. At 1000x (serverless
with thousands of function instances), external
pooler (PgBouncer) is required.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Connection management**

```java
// BAD - creates new connection per request
// Exhausts database connections under load
public List<User> getUsers() {
    // New connection every call - 30ms overhead
    Connection conn = DriverManager.getConnection(
        DB_URL, USER, PASS
    );
    try {
        PreparedStatement ps = conn.prepareStatement(
            "SELECT * FROM users"
        );
        // execute, map results...
    } finally {
        conn.close(); // expensive: TCP teardown
    }
}
```

```java
// GOOD - HikariCP connection pool
// Connection borrowed in ~0.1ms, returned after
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource hikariDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(DB_URL);
        config.setUsername(USER);
        config.setPassword(PASS);
        // Key tuning parameters:
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(5);
        // Max time to wait for a connection
        config.setConnectionTimeout(30_000);
        // Remove idle connections after 10 min
        config.setIdleTimeout(600_000);
        // Recycle connection after 30 min
        config.setMaxLifetime(1_800_000);
        return new HikariDataSource(config);
    }
}

// Usage: pool.getConnection() under the hood
@Autowired DataSource dataSource;

public List<User> getUsers() {
    try (Connection conn = dataSource.getConnection();
         PreparedStatement ps = conn.prepareStatement(
             "SELECT * FROM users"
         )) {
        // connection returned to pool on try-close
    }
}
```

**Example 2 - PgBouncer config for serverless**

```ini
# /etc/pgbouncer/pgbouncer.ini
# Pools 1000 app connections onto 20 real PG connections

[pgbouncer]
# transaction mode: connection freed after each txn
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
# How long client waits for pool connection
query_wait_timeout = 30
# Idle server connections removed after 60s
server_idle_timeout = 60

[databases]
# Virtual DB -> real DB mapping
mydb = host=postgres port=5432 dbname=mydb

[users]
# Per-user pool size overrides
app_user = pool_size=20
```

**Example 3 - Monitoring pool health**

```java
// HikariCP exposes JMX metrics
// Connect via jconsole or expose via Actuator:

management:
  endpoints:
    web:
      exposure:
        include: health,metrics
  metrics:
    export:
      prometheus:
        enabled: true

# Prometheus metrics exposed:
# hikaricp_connections_active   (in-use)
# hikaricp_connections_idle     (available)
# hikaricp_connections_pending  (waiting)
# hikaricp_connections_timeout_total (exhaustion count)

# Alert when pending > 0 for > 30 seconds
```

---

### ⚖️ Comparison Table

| Approach                          | Setup Cost      | Connections to DB | Best For                       |
| --------------------------------- | --------------- | ----------------- | ------------------------------ |
| **No Pool (raw connections)**     | Per-request     | O(RPS)            | Dev/test only                  |
| Application Pool (HikariCP)       | Startup only    | O(pool_size)      | Single-app deployments         |
| External Pooler (PgBouncer)       | Always-on proxy | O(pool_size)      | Serverless, many app instances |
| Serverless DB (Aurora Serverless) | Managed         | Built-in          | Pure serverless, variable load |

**How to choose:** HikariCP for Spring Boot monoliths
or fixed-fleet services. PgBouncer when deploying
100+ application instances (containerized, serverless)
that would each create their own pool. Aurora
Serverless v2 for fully managed serverless databases.

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                            |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bigger pool = better performance              | Optimal pool size is small (cores\*2+1). Larger pools cause DB CPU context-switching overhead and degrade throughput.                              |
| Connection pooling is only for databases      | Connection pooling applies to any expensive connection: HTTP keep-alive pools, SMTP connection pools, gRPC channel pools.                          |
| Returning a connection closes it              | In a pool, `conn.close()` returns the connection to the pool, not to the OS. The TCP connection stays open.                                        |
| Pool exhaustion means the pool is too small   | Pool exhaustion often means queries are too slow, not that the pool is undersized. Profile queries before increasing pool size.                    |
| External pooler (PgBouncer) replaces app pool | They serve different purposes. In serverless, PgBouncer handles connection multiplexing; the app may still benefit from a small per-instance pool. |

---

### 🚨 Failure Modes & Diagnosis

**Pool Exhaustion Under High Latency**

**Symptom:**
Requests queue. Latency spikes. Errors: "Connection
pool timeout after 30000ms." Pool metrics show
`hikaricp_connections_pending > 0` for extended time.

**Root Cause:**
A slow query (or a missing index) holds a connection
for 5s instead of 5ms. At 20 pool size, 20 slow
queries = all connections occupied. Requests queue
until timeout.

**Diagnostic Command / Tool:**

```sql
-- PostgreSQL: find long-running queries
SELECT pid, now() - query_start AS duration,
       query, state
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start < now() - interval '5 seconds'
ORDER BY duration DESC;
```

**Fix:**
Fix the slow query (add index, optimize joins).
Do NOT simply increase pool size - you are moving
the bottleneck to the database level.

**Prevention:**
Set `statement_timeout` = 5000ms in PostgreSQL to
kill runaway queries automatically. Alert on
`hikaricp_connections_pending > 0`.

---

**Connection Leak**

**Symptom:**
Pool steadily depletes. Active connections grow.
Idle connections go to zero. Eventually pool
exhaustion. Application restart temporarily fixes.

**Root Cause:**
A code path borrows a connection but never returns
it (exception before `close()`, connection not
in a try-with-resources block).

**Diagnostic Command / Tool:**

```java
// HikariCP: enable leak detection
config.setLeakDetectionThreshold(2000);
// Logs stack trace of any connection held > 2s
// Output: "Connection leak detected"
// + stack trace of borrowing code path
```

**Fix:**
Always use try-with-resources for connections:
`try (Connection conn = pool.getConnection()) {...}`

**Prevention:**
Enable `leakDetectionThreshold` in development.
Code review: ensure all getConnection() calls
are in try-with-resources blocks.

---

**Stale Connection (Half-Open TCP)**

**Symptom:**
Periodic "broken pipe" or "connection reset by peer"
errors on first query after a period of inactivity
(typically overnight). First request fails, retry
succeeds.

**Root Cause:**
The database server's TCP keepalive timeout
(typically 8 hours) closed idle connections, but
the pool still considers them valid.

**Diagnostic Command / Tool:**

```bash
# Check active TCP connections from pool to DB
ss -tnp | grep ':5432'
# If count stays high after long idle: stale
```

**Fix:**
Set `idleTimeout` < database TCP timeout.
Set `maxLifetime` < database connection timeout.
Configure `connectionTestQuery = "SELECT 1"`
(less efficient) or rely on JDBC4 `isValid()`.

**Prevention:**
Set `maxLifetime` = 30 minutes (well under most
database server timeouts of 8 hours).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What is Scalability` - connection pooling is the
  prerequisite for horizontally scaling services that
  share a database
- `Database Replication` - pools work in conjunction
  with replicas; separate pools for primary and
  replica connections

**Builds On This (learn these next):**

- `PgBouncer` - the reference external pooler for
  PostgreSQL; essential for serverless architectures
- `ProxySQL` - the reference external pooler for
  MySQL; adds query routing and read-write splitting

**Alternatives / Comparisons:**

- `Serverless Databases (Aurora Serverless)` -
  managed connection pooling built into the
  database tier; removes pool management from apps

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Reusable pre-established DB connections   │
│              │ borrowed per request and returned to pool │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Per-request connection creation costs     │
│ SOLVES       │ 20-50ms and exhausts DB connection limits │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The pool is a throttle, not just a cache; │
│              │ it bounds max concurrent DB connections   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always. No production app should open     │
│              │ raw DB connections per request.           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never avoid - but tune pool size to be    │
│              │ small (not large) for best performance    │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Increasing pool size to fix slow query    │
│              │ pool exhaustion (masks the real problem)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Near-zero connection overhead vs fixed    │
│              │ ceiling on concurrency (queue on exhaustion)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reuse connections like hotel room keys   │
│              │  - check out, use, return."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ PgBouncer → ProxySQL → Serverless DB      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Optimal pool size is small: `(CPU cores * 2) + 1`.
   Bigger pools hurt, not help.
2. Pool exhaustion usually means slow queries, not a
   small pool. Profile before resizing.
3. Always use try-with-resources for connections to
   prevent leaks.

**Interview one-liner:**
"Connection pooling maintains a fixed set of long-lived
database connections that requests borrow and return,
eliminating the 20-50ms TCP+auth overhead per request.
The pool is also a backpressure mechanism - it caps
the maximum concurrent database connections regardless
of application concurrency, protecting the database
from connection storms."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Pre-allocate and reuse expensive resources." This
applies to any resource with high creation cost but
low reuse cost: thread pools (ExecutorService),
HTTP keep-alive connections, gRPC channel pools,
SSL session resumption. The pattern is universal:
pay the creation cost once, amortize across many
uses.

**Where else this pattern appears:**

- Thread pools (ExecutorService) - reuse threads
  instead of creating OS threads per task
- HTTP connection pooling - keep-alive headers
  reuse TCP connections for multiple HTTP requests
- Object pools (game engines) - reuse enemy
  objects instead of allocating/GC-ing per spawn

**Industry applications:**

- High-frequency trading - microsecond-latency
  requirements make per-request DB connections
  impossible; fixed pools with connection warming
- Serverless platforms (AWS Lambda) - PgBouncer
  is mandatory architecture when Lambda invocations
  number in the thousands

---

### 💡 The Surprising Truth

Increasing pool size beyond the optimal value
actually degrades database throughput, not improves
it. The 2013 HikariCP benchmarks showed that at
pool_size = 256 on an 8-core database server,
throughput was lower than at pool_size = 9. The
reason: the database kernel spends more time on
context switching between 256 competing threads
than actually executing queries. More connections
means more concurrency, which means more contention,
which means more CPU wasted on coordination.
The sweet spot is counter-intuitively tiny.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. [EXPLAIN] Explain the connection pool as a
   throttle on database concurrency - not just
   a speed optimization - using the hotel key analogy.
2. [DEBUG] Given `hikaricp_connections_pending > 0`
   alerts, identify slow queries as the likely root
   cause and write the SQL to diagnose them.
3. [DECIDE] Given a system with 500 Lambda function
   instances each needing database access, decide
   between application pool (HikariCP) and external
   pool (PgBouncer) with justification.
4. [BUILD] Configure HikariCP with correct
   `maximumPoolSize`, `idleTimeout`, `maxLifetime`,
   and `leakDetectionThreshold` for a Spring Boot app.
5. [EXTEND] Design a connection pooling strategy
   for a multi-tenant SaaS with 1,000 tenants each
   on separate schemas, without using 1,000 pools.

---

### 🧠 Think About This Before We Continue

**Q1.** Your application has a HikariCP pool of size 20. Under normal load it works fine. During a batch
job at midnight, all 20 connections are held for 60
seconds each by slow analytical queries. What happens
to real-time user requests, and what are two ways
to fix this without killing the batch job?
_Hint: Think about query timeout settings and using
a separate connection pool for analytical workloads._

**Q2.** You deploy 200 Lambda function instances
each with a HikariCP pool of minimum 2, maximum 10.
What is the maximum number of connections your
PostgreSQL server might see, and why is this a
problem even if each Lambda instance thinks its
pool is small?
_Hint: Multiply across instances and consider
PostgreSQL's max_connections default._

**Q3.** [HANDS-ON] Instrument a Spring Boot
application with HikariCP and Prometheus to expose
pool metrics. Simulate pool exhaustion by writing
a test that holds all connections for 5 seconds.
What metrics spike, what is the shape of the
latency histogram during exhaustion, and how do
the metrics return to normal when the test finishes?
_Hint: Use `hikaricp_connections_pending` and
`hikaricp_connection_acquired_nanos` metrics._

---

### 🎯 Interview Deep-Dive

**Q1: What happens when all connections in a
connection pool are in use and a new request arrives?**
_Why they ask:_ Tests understanding of pool
mechanics under load.
_Strong answer includes:_

- The requesting thread blocks (waits) until
  `connectionTimeout` expires or a connection frees.
- If timeout expires: throws `SQLException` with
  "Connection is not available, request timed out."
- Application should translate this to HTTP 503.
- Root fix: faster queries or larger pool (carefully).

**Q2: A developer is getting intermittent "broken
pipe" errors on the first database query each
morning. What is the likely cause and fix?**
_Why they ask:_ Tests production debugging experience
with stale connections.
_Strong answer includes:_

- Stale connections: DB server's TCP keepalive
  closed idle connections overnight. Pool holds
  references to dead sockets.
- Fix: set `maxLifetime` < DB server connection
  timeout (typically 8 hours). Use `keepaliveTime`
  to ping idle connections.
- Configure `connectionTestQuery` as a fallback.

**Q3: Your microservice has 50 instances, each with
a connection pool of size 10. Is this fine?**
_Why they ask:_ Tests awareness of fleet-level
connection math.
_Strong answer includes:_

- 50 instances x 10 = 500 connections to the DB.
- PostgreSQL default max_connections = 100.
  This would fail immediately.
- Fix 1: use PgBouncer in transaction mode to
  multiplex 500 app "connections" onto 20 real ones.
- Fix 2: reduce per-instance pool size to 2 and
  ensure DB has 50 \* 2 + overhead = 120+ max_connections.
- Always calculate fleet-level DB connection budget
  before deploying microservices.
