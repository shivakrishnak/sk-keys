---
id: NET-047
title: "Connection Pooling"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-020, NET-035
used_by: NET-051, NET-056
related: NET-020, NET-035, NET-051
tags:
  - networking
  - connection-pooling
  - database
  - performance
  - HikariCP
  - pgbouncer
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/net/connection-pooling/
---

**⚡ TL;DR** - Connection pooling reuses existing TCP
connections instead of creating a new one per request.
Without a pool, a 1ms database query spends 3-5ms on
TCP + TLS + DB auth handshakes. With a pool, the handshake
cost is paid once and amortized over thousands of queries.
The two critical parameters: `maximumPoolSize` (don't set
too high - databases crash) and `connectionTimeout` (fail
fast rather than queue indefinitely). PostgreSQL's default
max connections is 100 - a common production crisis point.

| #047 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
|:---|:---|:---|
| **Depends on:** | TCP (NET-020), TCP Connection Lifecycle (NET-035) | |
| **Used by:** | N+1 Connection Problem, HTTP Connection Management | |
| **Related:** | TCP (NET-020), TCP Connection Lifecycle, N+1 Connection Problem | |

---

### 🔥 The Problem Without a Pool

A Spring Boot app makes 1,000 requests/second to
PostgreSQL. Without pooling:
- Each request: new TCP connection (1 RTT) + auth (1-2 RTTs)
- 3 RTTs × 1ms = 3ms handshake overhead per query
- At 1,000 RPS: 1,000 new TCP connections/second
- PostgreSQL forks a process per connection
- At 1,000 concurrent: PostgreSQL runs 1,000 processes = OOM
- PostgreSQL defaults: `max_connections = 100` → error 53300

With HikariCP pool of 10 connections:
- Pool maintains 10 persistent connections
- Queries borrow a connection, execute, return it
- 1,000 RPS served by 10 connections rotating
- Handshake cost: ~0 (connection already warm)
- PostgreSQL sees only 10 connections: stable

---

### 🧠 Intuition: Borrowing vs Creating

```
Without pool:              With pool:
request → open TCP         request → borrow from pool
       → auth              execute query
       → query             return to pool
       → close TCP         
         (3-5ms overhead)  (< 0.1ms overhead)

Pool = pre-warmed connections waiting to be used
Request = borrow for duration of work, return immediately
Pool manager = monitors health, replaces dead connections
```

---

### ⚙️ HikariCP: The Gold Standard for Java

```java
// HikariCP configuration (used by Spring Boot default)
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://db.host:5432/mydb");
config.setUsername("app_user");
config.setPassword("secret");

// CRITICAL SETTINGS:
config.setMaximumPoolSize(10);
// How many connections to keep open.
// Rule of thumb: num_cores × 2 for DB-heavy apps
// Diminishing returns: bigger is NOT better (contention)
// Benchmark: start at 10, adjust based on metrics

config.setMinimumIdle(5);
// Keep at least 5 connections warm even when idle
// Avoids latency spike on traffic increase

config.setConnectionTimeout(30000);
// Throw exception after 30s waiting for available connection
// Better than waiting forever (masks outage)

config.setIdleTimeout(600000);
// Remove idle connection after 10 minutes
// Prevents "connection gone stale" errors after long idle

config.setMaxLifetime(1800000);
// Replace every connection after 30 minutes regardless
// Prevents: database restarts, firewall idle timeouts
// Avoids: connection being silently dropped by router/firewall

config.setKeepaliveTime(60000);
// Send keepalive query every 60s to prevent firewall cutoff

config.setConnectionTestQuery("SELECT 1");
// Test connection before handing to app (optional with JDBC4)

HikariDataSource dataSource = new HikariDataSource(config);
```

---

### ⚙️ PostgreSQL Connection Limits: The Silent Killer

```
PostgreSQL process model:
  Each connection = 1 OS process (not thread!)
  Each process: ~5-10MB memory baseline
  max_connections = 100 (default):
    100 connections × 10MB = 1GB just for connection overhead
    Plus actual query memory per connection
    
  Error when exceeded:
    FATAL: sorry, too many clients already
    PSQLException: FATAL: remaining connection slots
    are reserved for non-replication superuser connections

Common antipattern:
  10 microservices × 10 replicas × 10 connections each
  = 1,000 connections → crashes PostgreSQL!

Solution: PgBouncer (connection pooler for PostgreSQL)
  All app instances → PgBouncer → (few connections) → PostgreSQL
  PgBouncer maintains pool of 20 connections to Postgres
  Multiplexes 1,000 app-side connections across 20 server-side

PgBouncer pool modes:
  session:    app gets a real connection for the session duration
  transaction: connection returned to pool after each transaction
              (preferred: reduces Postgres connections by 10-50x)
  statement:  connection returned after each statement
              (incompatible with transactions - use carefully)
```

---

### ⚙️ HTTP Connection Pooling (Keep-Alive)

```python
# BAD: new HTTP connection per request
import urllib.request

def fetch(url):
    # Opens TCP, sends request, reads response, CLOSES TCP
    with urllib.request.urlopen(url) as response:
        return response.read()
# Every call: TCP connect (1 RTT) + HTTP GET + TCP close

# GOOD: persistent connections with session
import requests

# Session reuses TCP connection across requests
session = requests.Session()
# Internally uses urllib3 with connection pool

# Configure pool:
from requests.adapters import HTTPAdapter

adapter = HTTPAdapter(
    pool_connections=10,    # number of distinct hosts
    pool_maxsize=100,       # connections per host
    max_retries=3,
    pool_block=False,       # raise error if pool full (vs wait)
)
session.mount('https://', adapter)

# All requests reuse connections within the pool
for i in range(1000):
    response = session.get('https://api.example.com/data')
    process(response.json())
# Connection established once, reused 1000 times
```

---

### ⚙️ Wrong vs Right: Pool Size Too Large

```java
// BAD: large pool "more connections = faster"
config.setMaximumPoolSize(200);
// 10 app instances × 200 connections = 2,000 PostgreSQL connections
// PostgreSQL crashes: max_connections = 100 exceeded
// Even if Postgres allows it:
//   2,000 concurrent queries create lock contention
//   Context switching between 200 threads per app instance
//   Throughput DECREASES at this level

// BAD: pool size zero or one (no reuse)
config.setMaximumPoolSize(1);
// Requests serialize: if one request takes 100ms,
// all others wait in queue
// At 100 RPS: average wait = 50ms (queuing theory)

// GOOD: right-size the pool
// Database throughput is limited by:
//   1. Number of CPU cores on DB server (parallelism)
//   2. I/O bandwidth (disk reads for uncached data)
//   3. Lock contention (serialized writes)
// Pool size should match DB's ability to make progress
//
// HikariCP's recommendation:
//   pool_size = (cores * 2) + effective_spindle_count
//   For SSD, no spindles: pool_size = (cores * 2) + 1
//   8-core DB server: 8*2+1 = 17 connections optimal
//   But: this is per application instance!
//   If 10 instances all use 17 → 170 total DB connections
//   Plan for total across ALL app instances

config.setMaximumPoolSize(10);  // per instance, with 5 instances total = 50 DB conns
```

---

### ⚙️ Pool Monitoring and Diagnosis

```bash
# HikariCP metrics (exposed via Micrometer/JMX):
hikaricp.connections.active     # currently in use
hikaricp.connections.idle       # waiting in pool
hikaricp.connections.pending    # requests waiting for a conn
hikaricp.connections.timeout    # failed to get connection
hikaricp.connections.acquire    # histogram of wait time

# Warning signs:
#  pending > 0 consistently   → pool too small
#  timeout > 0                → pool too small or DB too slow
#  active == maximumPoolSize  → pool saturated

# Query current pool state (HikariCP via JMX):
# MBean: com.zaxxer.hikari:type=Pool (pool-name)
# Attribute: ActiveConnections, IdleConnections, TotalConnections

# PostgreSQL: see all connections
SELECT client_addr, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE datname = 'mydb'
ORDER BY state, client_addr;

# Count per state:
SELECT state, count(*)
FROM pg_stat_activity
WHERE datname = 'mydb'
GROUP BY state;
# idle = connection in pool, waiting
# active = currently executing
# idle in transaction = transaction open but not executing (BUG!)
```

---

### ⚙️ Failure Example: "Idle in Transaction" Pool Exhaustion

**Symptoms:** Application hangs during peak load. Pool
metrics show `pending > 0`. All connections in pool show
`idle in transaction` in pg_stat_activity.

**Root cause:**

```java
// BAD: forgetting to commit or rollback a transaction
try {
    conn = pool.getConnection();
    conn.setAutoCommit(false);
    conn.execute("UPDATE accounts SET balance = ... WHERE id = 1");
    // Exception thrown here, or code returns without commit/rollback
    return result;  // <-- connection never committed or rolled back!
} catch (Exception e) {
    log(e);
    // forgot: conn.rollback()
}
// conn.close() called by try-with-resources... but:
// PostgreSQL sees "idle in transaction" until connection drops
// Connection is returned to pool with open transaction
// Next query from pool gets wrong transaction context!

// GOOD: always commit or rollback in finally
Connection conn = pool.getConnection();
try {
    conn.setAutoCommit(false);
    executeWork(conn);
    conn.commit();    // always commit
} catch (Exception e) {
    conn.rollback();  // always rollback on error
    throw e;
} finally {
    conn.close();     // return to pool
}
// Or: use Spring @Transactional - it handles commit/rollback
```

---

### 📐 Scale Considerations

```
10 RPS, 10ms average query time:
  10 × 0.01s = 0.1 connections needed (theory)
  Pool of 5 = massive overhead
  → Start with 2-5 connections

1,000 RPS, 10ms average query time:
  1,000 × 0.01s = 10 connections needed (theory)
  Add headroom for spikes: 15-20 connections
  → Pool of 10-20 per instance

10,000 RPS, 10ms average query time:
  10,000 × 0.01s = 100 connections (theory)
  With 10 instances: 10 connections per instance
  Postgres total: 100 connections → within default limit
  → Add PgBouncer when approaching max_connections

Mixed workloads (OLTP + analytics):
  Long-running analytics queries hold connections
  OLTP queries can't get connections → timeouts
  Solution: separate connection pools or separate Postgres instances
  → Analytics: read replica with its own pool
  → OLTP: primary with tight pool timeout (fail fast)
```

---

### 🧭 Decision Guide

```
Do I need a connection pool?
  YES for: any database, any HTTP API calling backend services,
           any service you call more than once per second

No pool needed:
  One-shot scripts, batch jobs that run once, Lambda/Serverless
  (FaaS functions share pools via RDS Proxy, not per-instance)

How large should my pool be?
  1. Start with 10 (safe default)
  2. Monitor hikaricp.connections.pending under load
  3. If pending > 0 under normal load: increase by 5
  4. If DB CPU spikes with larger pool: you hit DB limit
  5. Rule: DB throughput = (connections × query_rate)
           More connections past DB capacity = worse, not better

PgBouncer vs HikariCP - when to use both?
  HikariCP: app-side pool (reduces connection setup overhead)
  PgBouncer: server-side pool (reduces total Postgres connections)
  With 100 microservice replicas × 10 conns each = 1,000 Postgres conns
  PgBouncer in transaction mode: limits Postgres to 50 conns
  Both together: app pool + PgBouncer = best of both

Interview one-liner:
  "Connection pooling reuses TCP connections instead of
  creating one per request. Without it, a 1ms query pays
  3-5ms handshake overhead. Pool of 10 handles hundreds
  of RPS. Key parameters: maximumPoolSize (too high crashes
  the DB), connectionTimeout (fail fast vs queue forever),
  maxLifetime (replace stale connections before firewall kills them)."
```