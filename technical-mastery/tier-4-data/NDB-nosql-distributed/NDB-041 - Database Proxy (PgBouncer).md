---
version: 2
layout: default
title: "Database Proxy (PgBouncer)"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/nosql/database-proxy-pgbouncer/
id: NDB-042
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Database Fundamentals, Connection Pool, PostgreSQL
used_by: System Design, Cloud - AWS, Microservices
related: Connection Pool, PostgreSQL, Caching
tags:
  - nosql
  - pgbouncer
  - connection-pooling
  - database-proxy
  - deep-dive
---

⚡ TL;DR - A database proxy sits between application servers and the database, multiplexing thousands of application connections into a small pool of actual database connections; **PgBouncer** (PostgreSQL) is the standard lightweight connection pooler - it solves the "too many connections" problem that kills PostgreSQL under microservice-scale load.

| #474            | Category: NoSQL & Distributed Databases            | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Database Fundamentals, Connection Pool, PostgreSQL |                 |
| **Used by:**    | System Design, Cloud - AWS, Microservices          |                 |
| **Related:**    | Connection Pool, PostgreSQL, Caching               |                 |

---

### 🔥 The Problem This Solves

**POSTGRESQL'S PROCESS-PER-CONNECTION MODEL:**
PostgreSQL creates a new backend process for every connection. Each process consumes ~5-10MB of RAM. A typical production PostgreSQL instance supports a `max_connections` of 200-500 before RAM exhaustion or context-switch overhead degrades performance. At microservice scale: 10 services × 20 instances × 10 connections per instance = 2,000 connections requested. Without a proxy, PostgreSQL crashes or rejects connections.

**APPLICATION-LEVEL POOLS ARE INSUFFICIENT:**
HikariCP (Java) or similar per-service connection pools create pools local to each service instance. With 20 instances of a service, 20 separate pools each hold 10 connections = 200 connections for one service. 10 services = 2,000+ connections, overwhelming PostgreSQL. Application pools don't know about each other - they can't share a global connection limit.

**PGBOUNCER SOLVES THIS WITH MULTIPLEXING:**
PgBouncer sits in front of PostgreSQL and maintains a small pool of real database connections (e.g., 50 server connections). Thousands of client connections connect to PgBouncer. PgBouncer assigns a server connection to a client only when the client executes a query - and returns it immediately after (in transaction pool mode). 2,000 application threads → 50 PostgreSQL connections, with sub-millisecond multiplexing latency.

---

### 📘 Textbook Definition

A **Database Proxy** is a middleware layer between database clients (applications) and the database server. It provides: **connection pooling** (multiplex many client connections to few server connections), **query routing** (read replicas vs. primary), **authentication** (centralize credentials), **load balancing**, and **observability** (query metrics). **PgBouncer** is a lightweight, single-process C program (< 2MB RAM) acting as a PostgreSQL protocol-compatible proxy. It implements three **pool modes**: **Session Pool** - a server connection is assigned to a client for the duration of the client's session (TCP connection lifetime); simplest, but doesn't reduce server connections much. **Transaction Pool** - a server connection is assigned for the duration of a single transaction; returned to pool on commit/rollback; most efficient for typical OLTP workloads; **most commonly used mode**. **Statement Pool** - a server connection is assigned for a single SQL statement; most aggressive pooling but incompatible with multi-statement transactions. **RDS Proxy** (AWS) is Amazon's managed equivalent for RDS/Aurora, providing the same connection multiplexing with native IAM authentication and automatic failover on Multi-AZ events. **ProxySQL** is the equivalent for MySQL/MariaDB.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
PgBouncer is a lightweight proxy that sits in front of PostgreSQL - thousands of app connections talk to PgBouncer, which uses only tens of real database connections, multiplexing via transaction-level assignment.

**One analogy:**

> A hotel has 500 guests but only 30 room service staff. Without a dispatcher (PgBouncer), each guest would need their own dedicated staff member (1:1 connection = 500 staff). With a dispatcher: guests call the front desk, a free staff member is dispatched for their request, then becomes available for the next guest. 30 staff serve 500 guests efficiently. The guests don't know the difference - they just call the front desk.

- "500 guests" → thousands of application connections (HikariCP)
- "30 staff" → max server connections to PostgreSQL (pool_size)
- "Front desk dispatcher" → PgBouncer
- "Staff member dispatched per request" → transaction pool mode (assign on BEGIN, return on COMMIT)
- "Guests don't know the difference" → PgBouncer is PostgreSQL-protocol-compatible - apps need no code changes

**One insight:**
Transaction pool mode has a critical limitation: **prepared statements are not compatible** with it. A prepared statement (`PREPARE stmt AS SELECT ...`) is tied to a specific server connection. In transaction pool mode, each transaction may run on a different server connection - the prepared statement from a previous connection doesn't exist on the new one. This is why ORMs like Hibernate with `prepareStatements=true` or JDBC drivers with `prepareThreshold > 0` can break silently with PgBouncer transaction mode. The fix: use `prepareThreshold=0` in the JDBC connection string, or use PgBouncer statement-level protocol (which disables server-side prepared statements).

---

### 🔩 First Principles Explanation

**PGBOUNCER POOL MODES COMPARED:**

```
SESSION POOL MODE:
  Client connects → assigned 1 dedicated server connection
  Client disconnects → server connection returned to pool

  Client: connects at 9am, sends 5 queries over 8 hours,
    disconnects at 5pm
  Server connection: occupied from 9am to 5pm (8 hours
    idle between queries)

  max_client_conn = 1000, pool_size = 100
  → 100 clients get connections; 900 wait
  Session mode is only useful when clients disconnect
    frequently

TRANSACTION POOL MODE (default recommendation):
  Client connects → no server connection yet
  Client sends BEGIN → PgBouncer assigns a free server
    connection
  Client sends COMMIT → server connection returned to pool
    immediately

  Client: connects, sends 100 transactions over 8 hours
    (each < 100ms)
  Server connection: occupied ~100ms per transaction, idle
    rest of the time

  max_client_conn = 10000, pool_size = 50
  → 10,000 clients can connect; 50 server connections
    serve all of them
  (at any instant, only 50 transactions run concurrently
    on PostgreSQL)

STATEMENT POOL MODE:
  Client connects → no server connection
  Client sends any SQL statement → assigned server
    connection → returned after statement

  Cannot be used with: multi-statement transactions, any
    stateful operations
  Rarely used in production (too restrictive)

POOL SIZING RULE OF THUMB:
  pool_size ≈ (number of PostgreSQL cores) × 2 to 4
  For 8-core PostgreSQL: pool_size = 16 to 32
  Adjust based on: query duration, read vs. write ratio,
    query mix

  max_client_conn = 10x to 100x pool_size
  With pool_size = 50: max_client_conn = 500 to 5000
```

**PGBOUNCER CONFIGURATION:**

```ini
; /etc/pgbouncer/pgbouncer.ini

[databases]
; Database alias → actual PostgreSQL connection string
ecommerce = host=postgres-primary port=5432 dbname=ecommerce
ecommerce_read = host=postgres-replica port=5432 dbname=ecommerce

[pgbouncer]
; Listen address (applications connect here)
listen_addr = 0.0.0.0
listen_port = 5432

; Pool mode (most common: transaction)
pool_mode = transaction

; Server connections to PostgreSQL (the real connection limit)
max_client_conn = 10000   ; max application connections to PgBouncer
default_pool_size = 50    ; max server connections to PostgreSQL per database/user pair
max_db_connections = 100  ; absolute cap per database across all users

; Connection lifetime management
server_idle_timeout =
    600   ; close idle server connections after 10 minutes
client_idle_timeout =
    0     ; don't close idle client connections (0 = disabled)
server_lifetime =
    3600      ; recycle server connections every 1 hour (
        prevents stale)

; Prepared statement handling (IMPORTANT for transaction mode)
; server_reset_query =
    DISCARD ALL  ; default: reset connection state between clients
; For prepared statements: use JDBC prepareThreshold=0 or set:
; ignore_startup_parameters =
    extra_float_digits  ; some JDBC drivers send this

; Auth
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Logging
log_connections = 0   ; 0 in production (high volume, verbose)
log_disconnections = 0
log_pooler_errors = 1
stats_period = 60     ; emit stats to logs every 60s

; Admin interface
admin_users = pgbouncer_admin
stats_users = pgbouncer_monitor
```

**PREPARED STATEMENT INCOMPATIBILITY FIX:**

```java
// PROBLEM: Hibernate/JDBC with server-side prepared statements +
// PgBouncer transaction mode
// PostgreSQL server-side prepared statement is bound to a specific
// backend process
// PgBouncer transaction mode can route each transaction to a
// different backend
// → prepared statement from previous transaction doesn't exist on new
// backend
// → ERROR: prepared statement "S_1" does not exist

// SOLUTION 1: Disable server-side prepared statements in JDBC
spring:
  datasource:
    url: jdbc:postgresql://pgbouncer:5432/ecommerce?prepareThreshold=0
    # prepareThreshold=0 → JDBC never creates server-side prepared
    # statements
    # All queries use extended query protocol (parse/bind/execute each
    # time)
    # Performance impact: minimal for OLTP (server-side prep benefit
    # is small)

// SOLUTION 2: Use PgBouncer session mode (sacrifices connection
// multiplexing)
// pool_mode = session  → stateful, prepared statements work, but no
// multiplexing

// SOLUTION 3: Use pgBouncer's statement-level protocol
// Only viable for simple, stateless queries; not for Hibernate/JPA

// VERIFY: after configuring prepareThreshold=0, test with:
// pgbench -c 100 -j 4 -t 1000 -h pgbouncer-host -U appuser ecommerce
// Monitor: SHOW POOLS; in pgbouncer admin interface
```

**PGBOUNCER VS RDS PROXY:**

```
Feature               | PgBouncer              | RDS Proxy
----------------------|------------------------|-----------
Deployment            | Self-managed (EC2/K8s) | Fully
  managed (AWS service)
Protocol support      | PostgreSQL only         |
  PostgreSQL + MySQL/MariaDB
Pool modes            | Session/Txn/Statement   |
  Transaction mode only
IAM auth              | Manual config           | Native
  IAM integration
Failover handling     | Manual (set new primary)|
  Automatic (Multi-AZ failover)
Connection overhead   | ~1ms                    | ~2-3ms
  (managed layer overhead)
Cost                  | Free (OSS)              |
  $0.015/hr per vCPU (RDS instance)
Horizontal scaling    | Manual (multiple proxies)|
  AWS-managed scaling
Monitoring            | SHOW POOLS; SHOW STATS; |
  CloudWatch metrics

When to use PgBouncer:
- Self-managed PostgreSQL (on-prem, EC2)
- Need session or statement pool mode
- Cost-sensitive deployments

When to use RDS Proxy:
- RDS/Aurora PostgreSQL
- Need IAM authentication (serverless Lambda → RDS)
- Need automatic failover handling
- Lambda functions (Lambda scales rapidly → many
  short-lived connections)
```

**MONITORING PGBOUNCER:**

```sql
-- Connect to PgBouncer admin interface:
-- psql -U pgbouncer_admin -h pgbouncer-host -p 5432 pgbouncer

-- Pool stats: most important view
SHOW POOLS;
-- Output columns:
--   database: database alias
--   user: connecting user
--   cl_active: clients currently active (in a transaction)
--   cl_waiting: clients waiting for a server connection (
    queue depth!)
--   sv_active: server connections in use
--   sv_idle: server connections idle in pool
--   sv_used: server connections that were recently used
--   maxwait: longest a client has been waiting (seconds)
--   pool_mode: session|transaction|statement

-- ALERT: cl_waiting > 0 for sustained period → pool is too small
-- ALERT: maxwait > 1 second → clients backing up → add pool_size or PostgreSQL capacity

-- Global stats
SHOW STATS;
-- total_requests, total_received, total_sent, avg_query_time

-- Server connections
SHOW SERVERS;
-- Shows each actual connection to PostgreSQL: state, age, last use

-- Client connections
SHOW CLIENTS;
-- Shows each client connection to PgBouncer: state, wait time
```

---

### 🧪 Thought Experiment

**LAMBDA + RDS WITHOUT A PROXY:**

An AWS Lambda function handles HTTP requests. Lambda scales from 0 to 1,000 concurrent instances in seconds. Each Lambda instance uses HikariCP with min-pool-size=2. On a traffic spike: 1,000 instances × 2 connections = 2,000 connections to RDS PostgreSQL. PostgreSQL's `max_connections = 500`. Result: `FATAL: remaining connection slots are reserved for non-replication superuser connections`. The Lambda function fails for 500+ concurrent users.

**WITH RDS PROXY:**
1,000 Lambda instances connect to RDS Proxy. RDS Proxy maintains a fixed pool of 50 server connections to PostgreSQL. 1,000 client connections → 50 server connections. Lambda scales to 10,000 instances → still 50 server connections. PostgreSQL `max_connections = 100` (well within limits). Latency added: ~2ms. Connection establishment from Lambda to RDS Proxy: <5ms (persistent connection reuse across Lambda warm invocations). The proxy completely decouples Lambda's elastic connection count from PostgreSQL's fixed limit.

---

### 🧠 Mental Model / Analogy

> PgBouncer is like a parking valet service for a restaurant with 5 parking spaces. 100 diners arrive. Without valet, the first 5 get spaces, the rest circle the block (connection refused or wait). With valet: all 100 diners hand their keys to the valet (connect to PgBouncer). The valet parks only the cars that are actively dining - uses all 5 spaces efficiently. When a diner finishes (COMMIT), the valet retrieves their car (returns server connection to pool). 5 spaces → 100 diners served. Constraint: the valet can't start your car with a "personalized setting" it doesn't have (prepared statement on a different server connection).

- "5 parking spaces" → pool_size (server connections to PostgreSQL)
- "100 diners" → max_client_conn (application connections to PgBouncer)
- "Valet service" → PgBouncer connection pooler
- "Diner finishes" → COMMIT (transaction pool: server connection returned)
- "Personalized setting not available" → prepared statement incompatibility in transaction mode

---

### 📶 Gradual Depth - Four Levels

**Level 1:** PgBouncer sits between your app and PostgreSQL. Apps connect to PgBouncer (5432). PgBouncer maintains a small pool of real PostgreSQL connections. Each app transaction gets a server connection from the pool; after COMMIT, the connection returns. 1,000 app connections → 50 PostgreSQL connections. This prevents PostgreSQL from being overwhelmed.

**Level 2:** Use transaction pool mode for OLTP. Set `pool_size` to 2-4× PostgreSQL CPU cores. Set `max_client_conn` 10-100× `pool_size`. Disable server-side prepared statements in JDBC (`prepareThreshold=0`) when using transaction mode. Monitor `SHOW POOLS` - alert when `cl_waiting > 0` sustained or `maxwait > 1s`. On AWS, prefer RDS Proxy for Lambda-to-RDS connections (automatic failover, IAM auth). Deploy PgBouncer on the same host or in the same Kubernetes cluster as the application to minimize roundtrip latency.

**Level 3:** PgBouncer connection lifecycle: (1) Client connects → PgBouncer accepts TCP, parses startup message. (2) PgBouncer checks auth (`userlist.txt` or passthrough to PostgreSQL). (3) Client in `cl_login` state → transitions to `cl_active` or `cl_waiting`. (4) On BEGIN/first query: PgBouncer assigns an idle server connection (`sv_idle` → `sv_active`). (5) On COMMIT/ROLLBACK: PgBouncer sends `server_reset_query` (DISCARD ALL by default) to clear server state, then returns connection to `sv_idle`. `DISCARD ALL` resets: temporary tables, prepared statements, session-level settings, advisory locks. For performance: replace `server_reset_query = DISCARD ALL` with `server_reset_query = RESET ALL; SET SESSION AUTHORIZATION DEFAULT` to avoid dropping temp tables that aren't used.

**Level 4:** PgBouncer operates at the PostgreSQL wire protocol level - it speaks the PostgreSQL frontend/backend protocol. This makes it completely transparent to applications (no driver change needed) and independent of specific PostgreSQL versions. The performance impact of PgBouncer is minimal: the proxy adds ~0.5-1ms per connection assignment (memory copy of the connection context). The real performance gain comes from reduced PostgreSQL process spawning: connecting to PostgreSQL without PgBouncer involves forking a new backend process (~50ms overhead for the fork). PgBouncer amortizes this cost across many client connections using the pre-forked server pool. For very short queries (<5ms), the connection overhead without PgBouncer can dominate. With PgBouncer, connection overhead drops to ~1ms (pool assignment), making high-frequency microservice calls practical. The tradeoff: PgBouncer is a single point of failure - deploy multiple PgBouncer instances (with HAProxy or Route 53 in front), or use RDS Proxy's managed HA.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PGBOUNCER TRANSACTION POOL MODE                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Application layer:                                   │
│   App1 (HikariCP pool: 10 conns) ──┐                │
│   App2 (HikariCP pool: 10 conns) ──┤→ PgBouncer     │
│   App3 (HikariCP pool: 10 conns) ──┘  max_client=10K│
│   ... (100 service instances × 10 conns = 1000)      │
│                                                      │
│ PgBouncer layer:                                     │
│   [client connections: 1000]                         │
│   ↓ transaction pool assignment ↓                    │
│   [server connections: pool_size=50]                 │
│                                                      │
│ [PROXY ← YOU ARE HERE: txn pool assign]              │
│                                                      │
│ PostgreSQL layer:                                    │
│   max_connections = 100 (50 PgBouncer + 10 admin +  │
│   5 replication + 35 reserved)                       │
│   Each process: ~7MB RAM                             │
│   50 connections: 50 × 7MB = 350MB RAM for conns    │
│   Without PgBouncer: 1000 × 7MB = 7GB → OOM         │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SPRING BOOT MICROSERVICE → PGBOUNCER → POSTGRESQL:**

```
1. Service starts: HikariCP initializes
   → connects to PgBouncer:5432 (NOT directly to
     PostgreSQL)
   → HikariCP pool: min=5, max=20 per service instance
   → PgBouncer: 50 service instances × 20 = 1000 client
     connections accepted

2. HTTP request arrives: POST /api/orders
   → OrderService.placeOrder(@Transactional)
   → [PROXY ← YOU ARE HERE: HikariCP acquires conn from
     local pool]
   → HikariCP gets connection (connects to PgBouncer if
     not already connected)
   → JDBC sends BEGIN → PgBouncer assigns server
     connection (sv_idle → sv_active)

3. Inside transaction:
   → INSERT INTO orders ... (via PgBouncer → PostgreSQL)
   → INSERT INTO order_items ... (same server connection
     within same transaction)
   → COMMIT → PostgreSQL commits
   → PgBouncer: sends RESET (server_reset_query) to server
     connection
   → Server connection returned to pool (sv_active →
     sv_idle)
   → HikariCP: connection returned to local pool

4. Transaction duration: 15ms total
   Server connection occupied: 15ms (not 8 hours like
     session mode)

5. At peak: 1000 app threads all execute transactions
  simultaneously
   PgBouncer: 1000 clients waiting → 50 server connections
     serving
   At 15ms per transaction: each server connection handles
     1000/50 × 15ms = 300ms queue
   maxwait visible in SHOW POOLS
   → If maxwait > 1s: increase pool_size or scale
     PostgreSQL
```

---

### ⚖️ Comparison Table

| Aspect               | Session Mode                       | Transaction Mode                         | Statement Mode            |
| -------------------- | ---------------------------------- | ---------------------------------------- | ------------------------- |
| Server conn held for | Duration of client session         | Duration of one transaction              | Duration of one statement |
| Connection reduction | Minimal                            | High (10-100×)                           | Maximum                   |
| Prepared statements  | Supported                          | NOT supported (JDBC: prepareThreshold=0) | NOT supported             |
| Session variables    | Supported (`SET session`)          | NOT supported (reset between txns)       | NOT supported             |
| Advisory locks       | Supported                          | NOT supported (reset on return)          | NOT supported             |
| Best for             | Long-lived sessions, session state | OLTP microservices (most common)         | Simple read-only queries  |

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "PgBouncer increases the number of PostgreSQL connections allowed" | PgBouncer reduces the number of connections PostgreSQL receives, not increases. PostgreSQL `max_connections` is still the hard limit - PgBouncer stays well below it                                                   |
| "Transaction mode works with all PostgreSQL features"              | Transaction mode does NOT support: server-side prepared statements, session-level settings (`SET search_path`), advisory locks, temporary tables (reset between transactions). Use session mode if these are required  |
| "PgBouncer adds significant latency"                               | PgBouncer adds ~0.5-1ms per query (pool assignment overhead). For queries >5ms, this is negligible. The latency benefit from avoiding PostgreSQL process spawn (50ms without pooling) far outweighs the proxy overhead |
| "HikariCP makes PgBouncer unnecessary"                             | HikariCP pools connections per service instance but doesn't reduce total connections to PostgreSQL across many instances. PgBouncer provides a global pool, fundamentally different from per-instance pools            |

---

### 🚨 Failure Modes & Diagnosis

**1. Connection Queue Buildup (maxwait > 1s)**

**Symptom:** Application latency spikes. HTTP 500 errors: `HikariPool-1 - Connection is not available, request timed out after 30000ms`. PgBouncer `SHOW POOLS` shows `cl_waiting = 500, maxwait = 5`.

**Root Cause:** Transaction pool is exhausted: all `pool_size = 50` server connections are active (slow queries or long-running transactions holding connections). Incoming client requests queue in PgBouncer (cl_waiting).

**Diagnosis:**

```sql
-- PgBouncer admin
SHOW POOLS;
-- cl_waiting: clients in queue waiting for a server connection
-- maxwait: how long the longest-waiting client has been waiting
-- sv_active: server connections currently in a transaction

-- PostgreSQL: find long-running transactions
SELECT pid, now() - xact_start AS duration, query, state
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY duration DESC
LIMIT 20;

-- Find blocking queries
SELECT * FROM pg_blocking_pids(pid) WHERE pg_blocking_pids(
    pid) != '{}';
```

**Fix:**

```sql
-- Short term: kill long-running transactions
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - xact_start > interval '60 seconds';

-- Long term: increase pool_size (
    if PostgreSQL can handle more connections)
-- OR: add statement_timeout/idle_in_transaction_session_timeout to PostgreSQL
-- postgresql.conf:
-- idle_in_transaction_session_timeout =
    30000  (30s: auto-kill idle-in-txn)
-- statement_timeout =
    60000                    (60s: auto-kill slow queries)
```

---

### 🔗 Related Keywords

**Prerequisites:** Database Fundamentals, Connection Pool, PostgreSQL

**Builds On This:** System Design, Cloud - AWS

**Related:** Connection Pool, PostgreSQL, Caching

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT        │ Connection pooler: many clients → few conn│
│ MODES       │ Session | Transaction (most common) | Stmt│
│ POOL SIZE   │ 2-4× PostgreSQL CPU cores (start here)    │
│ PREP STMTS  │ Broken in txn mode → use prepareThreshold=│
│ MONITOR     │ SHOW POOLS: cl_waiting > 0 → alert        │
│ AWS ALT     │ RDS Proxy (managed, IAM auth, auto-failove│
│ USE FOR     │ Lambda→RDS, 50+ microservice instances    │
│ AVOID       │ Session mode features: temp tables, SET va│
│ ONE-LINER   │ "Thousands of app connections → tens of DB│
│             │  connections via transaction-level mux"   │
│ NEXT EXPLORE│ Data Locality → Caching                   │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) A Spring Boot application uses Hibernate with second-level cache (Ehcache). The team decides to add PgBouncer in transaction pool mode between the app and PostgreSQL. After deploying, they see intermittent `ERROR: prepared statement "HibernateStatementXxx" does not exist`. Walk through: (a) why this happens, (b) exactly what configuration change fixes it, (c) what performance impact the fix has, (d) what alternative Hibernate configuration avoids this issue entirely.

**Q2.** (TYPE E - Optimization) A high-traffic API receives 10,000 requests/second. Each request reads data from PostgreSQL with a single SELECT query (no transactions, no writes). Currently: 200 app instances × 10 HikariCP connections = 2,000 connections to PostgreSQL, near max_connections limit. PgBouncer is deployed with pool_size=100. After deployment, p99 latency improves from 200ms to 45ms. Explain: (a) why latency improved, (b) why the improvement is so significant (not just 1ms proxy overhead), (c) what the optimal pool_size formula is for a read-only workload, (d) what monitoring you add to validate the pool is correctly sized.
