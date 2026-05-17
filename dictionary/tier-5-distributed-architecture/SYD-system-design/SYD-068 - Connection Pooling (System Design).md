---
id: SYD-068
title: "Connection Pooling (System Design)"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-031
used_by: ""
related: SYD-031, SYD-019, SYD-052, SYD-040
tags:
  - architecture
  - connection-pooling
  - database
  - design
  - intermediate
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 68
permalink: /syd/connection-pooling-system-design/
---

# SYD-068 - Connection Pooling (System Design)

⚡ TL;DR - A database connection is expensive: TCP
handshake, TLS handshake, authentication, session setup
- each costs ~10-100ms and significant server memory
(5-10MB per PostgreSQL connection). Connection pooling
maintains a pool of pre-established connections that
are reused across requests. Instead of creating a new
connection per request (catastrophic at scale), requests
borrow a connection from the pool, use it, and return
it. At 1,000 requests/second, pooling reduces your
database connection count from 1,000 to 20-50 while
handling the same throughput. The key design number:
PostgreSQL can handle ~100-300 connections before
performance degrades; PgBouncer pools thousands of
app connections into that range.

| #068 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Horizontal Scaling | |
| **Related:** | Horizontal Scaling, Database Replication, Distributed Cache Design, Consistent Hashing | |

---

### 🔥 The Problem This Solves

Your API server handles 500 requests/second. Each
request opens a new database connection: 500 new
connections per second. PostgreSQL supports ~200
connections before memory exhaustion (5MB × 200 = 1GB)
and context-switching overhead destroys performance.
At 500 connections: database crashes or responses
degrade to 10+ seconds. Connection pooling solution:
maintain 50 persistent connections. 500 concurrent
requests wait in the pool queue (microseconds) to
borrow one. Database sees 50 connections, not 500.

---

### 📘 Textbook Definition

**Connection pool:** A cache of database connections
maintained so that connections can be reused when
future requests for the database are required. Held
open, not created anew for each request.

**Pool size:** The number of simultaneous database
connections the pool maintains. Typically 10-50 per
application instance.

**Connection borrowing:** A request takes a connection
from the pool (if one is available), uses it, then
returns it. If no connection is available, the request
waits in a queue or throws a "pool exhausted" error.

**Pool modes:**
- **Session pooling:** Each client session holds a
  connection for its full duration. Minimal overhead.
  Best for long-lived connections.
- **Transaction pooling:** A connection is held only
  for the duration of a transaction. Returned to pool
  between transactions. Allows more clients than connections.
- **Statement pooling:** Even finer - connection returned
  after each statement. Not compatible with prepared
  statements.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Open database connections are expensive. Reuse them.
Pool = a waiting room of pre-connected, ready-to-use
database handles.

**One analogy:**
> Hotel towels vs. laundry:
>
> Without pooling: hotel washes a new towel from scratch
> every time a guest needs one. Expensive and slow.
> With pooling: hotel keeps a linen cupboard of clean
> towels (the pool). Guest checks one out, uses it,
> returns it. Next guest gets it (freshly laundered).
> Fast because towels are ready, not being washed
> each time. Pool size = number of towels. If all
> towels are checked out: next guest waits.

**One insight:**
Connection pool size is a critical tuning parameter
often configured wrong. The intuitive instinct: "more
connections = more throughput." The reality: each
PostgreSQL connection uses 5-10MB of RAM and has
a context-switching cost. After ~100-300 connections,
throughput decreases (more OS context switches, more
memory pressure than CPU can handle). The Hikari CP
maintainer's formula: `connections = ((core_count * 2) + effective_spindle_count)`.
For a 4-core DB server with SSDs: 9-10 connections
per application instance is often optimal. This is
the single most important number to get right.

---

### 🔩 First Principles Explanation

**WHY CONNECTIONS ARE EXPENSIVE:**
```
Creating a new PostgreSQL connection:
  1. TCP 3-way handshake:        ~1ms
  2. TLS handshake (if SSL):     ~5ms
  3. PostgreSQL auth handshake:  ~2ms
  4. Session initialization:     ~1ms
  Total: ~10ms per new connection

At 500 req/sec, each opening a new connection:
  Overhead: 500 × 10ms = 5 seconds of connection work.
  If DB is busy: actual connect time = 50-100ms.
  Overhead = 25 seconds per second (impossible).

Memory: PostgreSQL allocates ~5MB per connection
  (shared_buffers, work_mem per query, stack).
  200 connections: 1GB RAM just for connections.
  500 connections: 2.5GB RAM. Application queries
  get less RAM → slower. I/O context switches explode.

Connection pooling:
  10 connections open forever: 50MB RAM (always).
  500 req/sec: each borrows a connection (~1 microsecond
  to acquire from pool). No new TCP, no new auth.
  Total overhead: negligible.
```

**POOL ARCHITECTURE:**
```
Application Servers        Pool Manager          DB

[App-1: 50 threads] ─┐
[App-2: 50 threads] ─┼──→ [PgBouncer      ] ──→ [PostgreSQL]
[App-3: 50 threads] ─┘    [Pool: 50 conns ]     [200 conns MAX]

Without external pool manager (HikariCP inside app):
[App-1: pool=20]  ──────────────────────────────→ [PostgreSQL]
[App-2: pool=20]  ──────────────────────────────→ [PostgreSQL]
[App-3: pool=20]  ──────────────────────────────→ [PostgreSQL]
Total: 60 connections (20 × 3 app instances).
Scale to 20 app instances: 400 connections. DB struggles.

With PgBouncer (external connection pooler):
All app instances → PgBouncer (unlimited client connections)
PgBouncer → DB (50 actual connections, fixed).
Scale to 100 app instances: still 50 DB connections.
```

**POOL EXHAUSTION:**
```
Pool size: 20 connections.
20 concurrent long-running queries in progress.
Request #21 arrives: pool is exhausted.

Options:
  1. Wait in queue (connection timeout: 30 seconds).
     If < 30 seconds: gets connection when one returns.
     If > 30 seconds: timeout error thrown to client.
  
  2. Fail fast: pool.acquire(timeout=0) → error if empty.
     Use for health checks or low-priority requests.

Common cause: slow queries holding connections.
  SELECT * FROM orders JOIN ... (10-second query).
  20 such queries: pool exhausted. All other requests fail.
  Fix: optimize slow queries, add indexes, set query
  timeouts (statement_timeout in PostgreSQL).
  
Monitoring: pool_wait_time metric.
  Spikes = pool too small OR queries too slow.
  Pool size is rarely the fix; query optimization is.
```

---

### 🧪 Thought Experiment

**The Right Pool Size**

3-tier web application:
- 10 app servers (Spring Boot / HikariCP)
- 1 PostgreSQL primary (16-core server)
- Average query time: 5ms

What pool size per app server?

DB max capacity: 16 cores × 2 = 32 optimal connections.
DB absolute max before degradation: ~200.

Target: 32 DB connections total.
App servers: 10.
Per-app pool size: 32 / 10 = 3.2 → 4 connections.

But: requests queue inside the app anyway (thread pool).
Each app has 50 worker threads. If pool=4:
  50 workers × 5ms query = 250ms of waiting.
  Max throughput per app: 4 connections / 5ms = 800 qps.
  10 apps: 8,000 qps total throughput.

If queries get slower (100ms average):
  Max per app: 4 / 100ms = 40 qps.
  Query slowness = real bottleneck. Not pool size.

Lesson: pool size matters, but query performance
is usually the binding constraint.

---

### 🧠 Mental Model / Analogy

> Connection pooling is like a taxi fleet:
>
> Without pooling: each passenger calls for a new taxi
> to be manufactured on demand. 10-minute wait every time.
> With pooling: 20 taxis are parked and ready.
> Passenger calls: nearest taxi dispatched immediately.
> Taxi finishes trip, returns to the fleet.
> If all 20 taxis are busy: passenger waits (queue).
> Pool too small: always waiting. Pool too large:
> taxis sit idle, wasting fuel/memory.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Connecting to a database takes time and resources.
Connection pooling keeps a set of connections open
all the time. When your app needs to talk to the
database, it borrows an already-open connection,
uses it, and puts it back. Much faster than opening
a new connection for every database call.

**Level 2 - How to use it (junior developer):**
Use HikariCP in Spring Boot, SQLAlchemy's pool in
Python, or your framework's built-in connection pool.
Set `maximumPoolSize` to 10-20 as a starting point.
Set `connectionTimeout` to 30 seconds. Monitor pool
wait time: if it spikes, your queries may be slow.
Use `pool.getConnection()` or equivalent - don't
create connections manually.

**Level 3 - How it works (mid-level engineer):**
Pool maintains N open connections to the DB. On request,
blocks until a connection is available (up to
`connectionTimeout`). Connection is marked "borrowed"
while in use. On return (or transaction commit/rollback),
connection goes back to pool. Pool validates connection
health on borrow (configurable). External poolers
(PgBouncer, ProxySQL) work at the network level between
application and database - essential when multiple app
instances would otherwise exhaust DB connection limit.

**Level 4 - Why it was designed this way (senior/staff):**
The impedance mismatch: stateless HTTP request handling
(10ms-100ms requests, thousands per second) vs. stateful
database connections (expensive to create, limited count).
Connection pooling bridges this: converts a stateful
resource (connection) into a pooled, reusable one.
Transaction pooling (PgBouncer mode) takes this further:
the database connection is only held for the duration
of an active transaction, then returned. An app with
1,000 concurrent sessions but few active transactions
at any moment needs far fewer actual DB connections
than 1,000. This is how PgBouncer serves 10,000 client
connections through 50 database connections.

**Level 5 - Mastery (distinguished engineer):**
The connection pool tuning formula `(2 × cores) + disk`
from the Hikari documentation is derived from queuing
theory (specifically, the machine repairman model).
Each active query holds a DB connection. If all CPU
cores are busy processing queries simultaneously,
adding more connections creates more context-switching
overhead than query throughput gain. At Shopify, their
MySQL connection pooling was a core part of handling
Black Friday traffic: ProxySQL with aggressive connection
multiplexing, limiting each DB to a fixed connection
count regardless of upstream traffic spikes. This
decoupling of "application request count" from "database
connection count" was essential for their scaling
architecture. The key insight: optimize the invariant
(DB connections) to stay in the optimal range, and let
the variable (application requests) scale independently.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│ CONNECTION POOL LIFECYCLE                             │
│                                                        │
│ Startup: Pool creates minConnections to DB.           │
│   Validates connections are live (test query).        │
│                                                        │
│ Request arrives:                                      │
│   Pool has free connection? → borrow it (< 1ms)     │
│   Pool at max? → wait in queue (up to timeout)      │
│   Wait expires? → PoolExhaustedException            │
│                                                        │
│ During request:                                       │
│   Connection is "checked out" - exclusive to request │
│   Request runs queries using this connection         │
│                                                        │
│ Request completes:                                    │
│   Transaction committed/rolled back                  │
│   Connection returned to pool (not closed!)          │
│   Pool tests connection health (optional)            │
│   Next waiting request gets this connection          │
│                                                        │
│ PgBouncer (external pool):                           │
│   App: 1000 client connections to PgBouncer          │
│   PgBouncer: 50 real connections to PostgreSQL        │
│   Transaction mode: connection released after each   │
│   txn. 1000 app connections → 50 DB connections.    │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - HikariCP configuration (Java/Spring Boot)**
```java
// application.yml
spring:
  datasource:
    url: jdbc:postgresql://db.internal:5432/myapp
    username: myapp
    password: ${DB_PASSWORD}
    hikari:
      # Core pool settings
      maximum-pool-size: 20    # Max DB connections
      minimum-idle: 5          # Min idle connections
      idle-timeout: 600000     # Remove idle after 10 min
      
      # Timeout settings
      connection-timeout: 30000  # 30s to get from pool
      max-lifetime: 1800000    # 30 min - cycle connections
                               # (catches DB timeouts)
      
      # Health check
      connection-test-query: SELECT 1
      keepalive-time: 60000    # Ping idle connections
      
      # Critical: name the pool for monitoring
      pool-name: MyAppHikariPool
      
      # Leak detection: warn if connection held > 2s
      leak-detection-threshold: 2000

// BAD: creating connections manually - NEVER do this
@Repository
public class OrderRepository {
    public Order findById(long id) {
        // BAD: new connection per call = catastrophic at scale
        try (Connection conn = DriverManager.getConnection(
                "jdbc:postgresql://...", "user", "pass")) {
            // ... runs ~10ms just for connection setup
        }
    }
}

// GOOD: use DataSource (Hikari pool)
@Repository
public class OrderRepository {
    @Autowired
    private DataSource dataSource;  // Hikari pool
    
    public Order findById(long id) {
        // GOOD: borrows from pool (<1ms), returns on close
        try (Connection conn = dataSource.getConnection()) {
            // ... runs query on existing connection
        }
    }
}
```

**Example 2 - PgBouncer configuration**
```ini
; /etc/pgbouncer/pgbouncer.ini

[databases]
; Route myapp to PostgreSQL primary
myapp = host=primary.db.internal port=5432 dbname=myapp

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 5432

; Authentication
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

; Pool mode: transaction is best for stateless web apps
; (connection returned to pool after each transaction)
pool_mode = transaction

; Max total connections to PostgreSQL
max_client_conn = 10000   ; App connections (unlimited effectively)
default_pool_size = 50    ; Actual PostgreSQL connections

; Timeout: don't hold idle connections open
server_idle_timeout = 600
client_idle_timeout = 0

; Connection queue timeout
query_wait_timeout = 30

; Stats: expose /metrics via pgbouncer's SHOW POOLS
stats_period = 30
```

**Example 3 - Pool exhaustion detection**
```python
# Python: SQLAlchemy with pool monitoring
from sqlalchemy import create_engine, event
from sqlalchemy.pool import Pool
import logging

engine = create_engine(
    "postgresql://user:pass@db.internal/myapp",
    pool_size=20,           # Persistent connections
    max_overflow=10,        # Extra connections under load
    pool_timeout=30,        # Seconds to wait for connection
    pool_pre_ping=True,     # Validate connection before use
    pool_recycle=3600,      # Recycle connections after 1 hour
)

# Monitor pool events
@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, conn_record, conn_proxy):
    # Log pool acquisition for debugging
    logging.debug("Pool checkout: connections active")

@event.listens_for(Pool, "checkin")
def receive_checkin(dbapi_conn, conn_record):
    logging.debug("Pool checkin: connection returned")

# Expose pool stats for monitoring (Prometheus)
def get_pool_stats() -> dict:
    status = engine.pool.status()
    return {
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "checked_in": engine.pool.checkedin(),
    }

# Alert if checked_out / pool_size > 0.8
# (pool is 80% utilized - risk of exhaustion)
```

---

### ⚖️ Comparison Table

| Approach | Connections to DB | Scalability | Complexity |
|---|---|---|---|
| **No pooling** | 1 per request | Fails at ~100 RPS | Low |
| **App-level pool (Hikari)** | N per app instance | Good for 1-10 instances | Low |
| **External pooler (PgBouncer)** | Fixed regardless of app instances | Excellent; scales to 100+ app instances | Medium |
| **Database proxy (AWS RDS Proxy)** | Fixed; serverless-friendly | Excellent; auto-scales | Low (managed) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bigger pool = more throughput | Beyond the optimal point (~2× CPU cores for PostgreSQL), more connections create more context switching than throughput. PostgreSQL performance peaks at ~200 connections on typical hardware and then degrades. Adding more connections past this point slows everything down. Optimize query performance before increasing pool size. |
| Connection pooling is only for databases | Connection pools are used for any resource with expensive connection setup: Redis clients, HTTP connection pools (Apache HttpClient, OkHttp for internal APIs), gRPC channels, thread pools. Any "connect, use, disconnect" pattern benefits from pooling. |
| PgBouncer in transaction mode is always safe | Transaction mode breaks PostgreSQL features that rely on session state: SET session variables, LISTEN/NOTIFY, advisory locks, prepared statements. Applications using these features must use session mode or connection-aware coding. Spring Boot applications using advisory locks for distributed locking must not use PgBouncer transaction mode for those connections. |

---

### 🚨 Failure Modes & Diagnosis

**Connection Pool Exhaustion**

**Symptom:**
API responses: 500 errors with message:
"Unable to acquire JDBC Connection" or
"HikariPool-1 - Connection is not available,
request timed out after 30000ms."
Database CPU: low (it's not busy - it's starved).
Application thread pool: exhausted (waiting for DB connections).

**Root Cause:**
Slow queries are holding connections. N connections
are occupied by N slow queries. New requests cannot
acquire connections and timeout.

**Diagnosis:**
```sql
-- PostgreSQL: find long-running queries holding connections
SELECT pid,
       now() - pg_stat_activity.query_start AS duration,
       query,
       state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start)
      > interval '5 seconds'
ORDER BY duration DESC;

-- Kill a specific long-running query:
SELECT pg_cancel_backend(pid);  -- graceful
SELECT pg_terminate_backend(pid);  -- forceful
```

```yaml
# Hikari: expose pool metrics via Spring Boot Actuator
management:
  endpoints:
    web:
      exposure:
        include: metrics
  metrics:
    tags:
      pool: HikariPool-1
# Check: /actuator/metrics/hikaricp.connections.acquire
# Check: /actuator/metrics/hikaricp.connections.pending
# Pending > 0 for extended periods = pool exhaustion
```

**Fix:**
```sql
-- Add statement timeout to prevent runaway queries
-- (PostgreSQL: set per connection or globally)
ALTER DATABASE myapp SET statement_timeout = '10s';

-- Or per role:
ALTER ROLE myapp_user SET statement_timeout = '5s';
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Horizontal Scaling` - understanding that pooling
  is essential when scaling to multiple app instances

**Builds On This (learn these next):**
- `Database Replication (System)` - combining pooling
  with read replicas (route read pool to replicas)
- `Distributed Cache Design` - similar pattern:
  Redis client pool for Redis connections
- `Consistent Hashing` - sharded databases use pooling
  per shard with routing logic

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Pre-open N DB connections. Reuse them.   │
│             │ 1000 app requests → 50 DB connections.  │
├─────────────┼──────────────────────────────────────────  │
│ POOL SIZE   │ Start: (2 × DB_cores) + spindles.       │
│             │ Typically: 10-50 per app instance.      │
├─────────────┼──────────────────────────────────────────  │
│ EXTERNAL    │ PgBouncer/ProxySQL: many app instances  │
│             │ → fixed DB connections. Essential at scale│
├─────────────┼──────────────────────────────────────────  │
│ TXNMODE     │ PgBouncer transaction mode: conn        │
│             │ returned after each txn. More efficient.│
│             │ Breaks: SET, LISTEN, advisory locks.   │
├─────────────┼──────────────────────────────────────────  │
│ EXHAUSTION  │ Slow queries holding connections.       │
│             │ Fix: optimize queries, set query timeout│
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Reuse connections. Pool=10-50.        │
│             │  Use PgBouncer at 3+ app instances."  │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Cache Invalidation Strategies            │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Never create a new DB connection per request. Use
   a connection pool (HikariCP, SQLAlchemy, pgx).
   Pool size: start at `(2 × DB CPU cores)` for PostgreSQL.
   More is not better - connection overhead degrades
   DB performance past ~200 connections.
2. For multiple application instances, use an external
   pooler (PgBouncer for PostgreSQL, ProxySQL for MySQL).
   This keeps total DB connections fixed regardless
   of how many app instances you scale to.
3. Pool exhaustion (all connections occupied) is almost
   always caused by slow queries holding connections,
   not by a pool that's too small. Diagnose with
   `pg_stat_activity`; fix with query optimization
   and `statement_timeout`.

**Interview one-liner:**
"Connection pooling: pre-open N DB connections, reuse across requests.
Creating a new connection per request: ~10ms + memory overhead; catastrophic at
scale. Pool size: start at (2 × DB cores) - more connections past ~200 degrades
PostgreSQL. External pooler (PgBouncer transaction mode): multiplex 10,000 app
connections into 50 DB connections; connection returned after each transaction.
Pool exhaustion = slow queries holding connections. Fix: optimize queries, add
statement_timeout. Monitor: pool_pending metric in Hikari/actuator."
