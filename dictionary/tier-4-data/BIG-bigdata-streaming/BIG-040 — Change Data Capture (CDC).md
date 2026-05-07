---
layout: default
title: "Change Data Capture (CDC)"
parent: "Big Data & Streaming"
nav_order: 40
permalink: /big-data-streaming/change-data-capture/
number: "BIG-040"
category: Big Data & Streaming
difficulty: ★★★
depends_on: Transactional Outbox, Apache Kafka, Event-Driven Architecture
used_by: Data Replication, Cache Invalidation, Search Index Sync, Transactional Outbox
related: Transactional Outbox, Apache Kafka, Event-Driven Architecture
tags:
  - cdc
  - debezium
  - change-data-capture
  - wal
  - data-replication
---

# BIG-040 — Change Data Capture (CDC)

⚡ TL;DR — **Change Data Capture (CDC)** captures row-level database changes (INSERT/UPDATE/DELETE) in real-time as events and streams them to downstream systems; **Debezium** is the standard open-source CDC platform — connectors for PostgreSQL (WAL), MySQL (binlog), MongoDB (oplog), Oracle; change events include **before/after state** + **operation type** (c/u/d); use cases: cache invalidation, search index sync, Transactional Outbox, data warehouse replication, cross-service data sync; **vs polling**: CDC is row-level, sub-millisecond, low DB overhead.

| #570            | Category: Big Data & Streaming                                                | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Transactional Outbox, Apache Kafka, Event-Driven Architecture                 |                 |
| **Used by:**    | Data Replication, Cache Invalidation, Search Index Sync, Transactional Outbox |                 |
| **Related:**    | Transactional Outbox, Apache Kafka, Event-Driven Architecture                 |                 |

---

### 🔥 The Problem This Solves

**KEEPING MULTIPLE DATA STORES IN SYNC:**
A user updates their profile in PostgreSQL. That change must be reflected in:

1. Redis cache (invalidate cached user record)
2. Elasticsearch (update user search index)
3. Analytics data warehouse (update user dimension)
4. Notification service (trigger "profile updated" notification)

**WITHOUT CDC (Polling approach):**
Each system polls every 30 seconds → 30-second staleness. Or: application code calls each system in sequence → coupling, partial failures. Or: DB trigger → stored procedure → HTTP call → complex, brittle.

**WITH CDC:**
Debezium reads PostgreSQL WAL → captures `UPDATE users` → publishes `UserUpdatedEvent` to Kafka. All 4 systems consume from Kafka independently → zero coupling, sub-millisecond latency, no polling overhead.

---

### 📘 Textbook Definition

**Change Data Capture (CDC)** is a pattern that identifies and captures changes (INSERT, UPDATE, DELETE) made to a database and delivers those changes, in near-real-time, to downstream systems.

**How CDC works (at the DB level):**

- **PostgreSQL**: Logical Replication + WAL (Write-Ahead Log). Debezium uses `pgoutput` plugin to read WAL. Requires `wal_level = logical`.
- **MySQL**: Binary Log (binlog). Debezium reads binlog events. Requires `binlog_format = ROW`.
- **MongoDB**: Oplog (operation log). Debezium reads change events from the replica set oplog.
- **Oracle**: LogMiner. Debezium reads Oracle redo log via LogMiner.

**Debezium event envelope:**

```json
{
  "before": { "id": 1, "name": "Alice", "email": "old@example.com" },
  "after": { "id": 1, "name": "Alice", "email": "new@example.com" },
  "source": { "db": "userdb", "table": "users", "ts_ms": 1705000000000 },
  "op": "u", // c=create (INSERT), u=update (UPDATE), d=delete (DELETE), r=read (snapshot)
  "ts_ms": 1705000000100
}
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CDC = database changes (INSERT/UPDATE/DELETE) → captured from transaction logs → streamed to Kafka → consumed by downstream systems; Debezium = industry-standard CDC tool; before/after state in every event.

**One analogy:**

> CDC is like a bank's audit log. Every transaction (deposit/withdrawal) is recorded in the bank's ledger (WAL/binlog). An auditor (Debezium) reads the ledger continuously and broadcasts each change to anyone who needs to know: the fraud department, the reporting team, the customer's app. No need to poll the account — changes flow automatically.

**One insight:**
CDC reads from the database's transaction log, not from tables. This means: (1) **Zero polling overhead**: no SELECT queries on the application tables. (2) **All changes captured**: every committed transaction, including those from scripts, other services, or bulk imports. (3) **Before/after state**: know WHAT changed AND what the previous value was (perfect for cache invalidation — you know which key to evict). (4) **Ordering guaranteed**: WAL/binlog is ordered per primary key within a table.

---

### 🔩 First Principles Explanation

**DEBEZIUM POSTGRESQL CONNECTOR SETUP:**

```json
// Kafka Connect: deploy Debezium PostgreSQL connector
// POST http://kafka-connect:8083/connectors

{
  "name": "postgres-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1", // CDC: always 1 task (WAL is sequential)

    // Database connection:
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium", // dedicated low-privilege user
    "database.password": "${file:/opt/kafka/secrets.properties:pg.password}",
    "database.dbname": "appdb",

    // Debezium server identity (Kafka topic prefix):
    "database.server.name": "appdb",
    // Topics: appdb.public.users, appdb.public.orders, etc.

    // Replication:
    "plugin.name": "pgoutput",
    "publication.name": "debezium_pub",
    "slot.name": "debezium_slot",

    // Which tables to capture (include = capture only these):
    "table.include.list": "public.users,public.orders,public.products",

    // Initial snapshot (when connector first starts):
    "snapshot.mode": "initial",
    // "initial": snapshot ALL existing data first, then stream changes
    // "never": skip snapshot, only stream changes from NOW
    // "initial_only": snapshot only, no streaming (one-time data load)
    // "always": re-snapshot every connector restart (expensive!)

    // Topic routing (one topic per table):
    // Default: {server}.{schema}.{table} = "appdb.public.users"

    // Event timestamp precision:
    "time.precision.mode": "connect",

    // Tombstone deletion events for compaction:
    "tombstones.on.delete": "true"
  }
}
```

**POSTGRESQL SETUP:**

```sql
-- postgresql.conf (requires restart):
wal_level = logical
max_replication_slots = 10   -- max simultaneous CDC connectors
max_wal_senders = 10

-- Create dedicated Debezium user (principle of least privilege):
CREATE USER debezium WITH REPLICATION LOGIN PASSWORD 'secure_password';

-- Grant access to captured tables:
GRANT SELECT ON TABLE users, orders, products TO debezium;
GRANT USAGE ON SCHEMA public TO debezium;

-- Create publication (declares which tables Debezium will replicate):
CREATE PUBLICATION debezium_pub FOR TABLE users, orders, products;
-- OR capture ALL tables:
-- CREATE PUBLICATION debezium_pub FOR ALL TABLES;

-- Replication slot (Debezium creates this automatically, or manually):
-- SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput');
```

**CONSUMING CDC EVENTS (SPRING BOOT):**

```java
// CDC event consumer: cache invalidation on user update
@Service
public class UserCdcConsumer {

    @Autowired
    private RedisTemplate<String, User> redisTemplate;

    @Autowired
    private ElasticsearchOperations elasticsearchOps;

    // Debezium publishes to: "appdb.public.users" (server.schema.table)
    @KafkaListener(topics = "appdb.public.users", groupId = "cache-invalidation")
    public void handleUserChange(ConsumerRecord<String, String> record) throws JsonProcessingException {

        // Parse Debezium envelope:
        DebeziumEnvelope<User> envelope = objectMapper.readValue(
            record.value(), new TypeReference<DebeziumEnvelope<User>>() {}
        );

        String userId = String.valueOf(envelope.getPayload().getAfter().getId());
        // (Or use record.key() — Debezium sets key = primary key of changed row)

        switch (envelope.getPayload().getOp()) {
            case "c" -> {  // CREATE (INSERT)
                redisTemplate.opsForValue().set("user:" + userId, envelope.getPayload().getAfter(),
                    Duration.ofHours(1));
                // Elasticsearch index:
                elasticsearchOps.save(envelope.getPayload().getAfter());
            }
            case "u" -> {  // UPDATE
                // Invalidate cache (or update):
                redisTemplate.delete("user:" + userId);
                // Full update in Elasticsearch:
                elasticsearchOps.save(envelope.getPayload().getAfter());
            }
            case "d" -> {  // DELETE
                redisTemplate.delete("user:" + userId);
                elasticsearchOps.delete(userId, User.class);
            }
            case "r" -> {  // READ (snapshot event, initial load)
                // Populate cache from snapshot:
                redisTemplate.opsForValue().set("user:" + userId, envelope.getPayload().getAfter(),
                    Duration.ofHours(1));
            }
        }
    }
}

// Debezium envelope model:
@Data
public class DebeziumEnvelope<T> {
    private Payload<T> payload;

    @Data
    public static class Payload<T> {
        private T before;    // state before change (null for INSERT)
        private T after;     // state after change (null for DELETE)
        private String op;   // c, u, d, r
        private Source source;

        @Data
        public static class Source {
            private String db;
            private String table;
            @JsonProperty("ts_ms")
            private long timestampMs;
        }
    }
}
```

**MYSQL CONNECTOR (binlog):**

```json
{
  "name": "mysql-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "${file:/opt/secrets.properties:mysql.password}",
    "database.server.id": "184054", // UNIQUE server ID (must not conflict with MySQL replicas)
    "database.server.name": "mysqldb",

    // MySQL binlog setup:
    // my.cnf: [mysqld] log-bin = mysql-bin; binlog_format = ROW; binlog_row_image = FULL

    "table.include.list": "ecommerce.orders,ecommerce.users",
    "snapshot.mode": "initial",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes.mysqldb"
    // ^ MySQL connector stores schema history (DDL changes) in this Kafka topic
    // Required because MySQL binlog references schema by column positions (not names)
  }
}
```

**CDC USE CASES:**

```
1. CACHE INVALIDATION (most common):
   DB write → CDC → cache eviction/update
   Before CDC: polling (stale cache) or application-level invalidation (complex coupling)
   With CDC: automatic, sub-ms, decoupled

2. SEARCH INDEX SYNC:
   DB write → CDC → Elasticsearch update
   Alternative: dual writes from application (brittle, partial failures)
   With CDC: reliable, all changes captured (including bulk DB migrations)

3. DATA WAREHOUSE REPLICATION:
   OLTP DB → CDC → Kafka → Flink/Spark job → DWH
   Traditional ETL: nightly batch (stale by up to 24h)
   With CDC: near-real-time OLTP-to-DWH sync (streaming ETL)

4. TRANSACTIONAL OUTBOX (#568):
   Application writes outbox_events table → Debezium CDC → Kafka
   (covered in detail in entry #568)

5. CROSS-SERVICE DATA SYNC:
   Service A owns users table → CDC → Service B gets user change events
   Without CDC: Service A must call Service B API (tight coupling)
   With CDC: Service B subscribes to user-change events (loose coupling)

6. AUDIT LOGGING:
   All DB changes captured with before/after state
   Compliance: who changed what, when, from what to what
   Without CDC: application-level audit logging (can be bypassed by direct SQL)
   With CDC: captures ALL changes regardless of source (app, scripts, DBA)
```

---

### 🧪 Thought Experiment

**CDC vs APPLICATION-LEVEL EVENT PUBLISHING:**

A developer considers publishing domain events from the application layer instead of using CDC. They write `userService.update(user)` + `kafkaTemplate.send("user-events", new UserUpdatedEvent(user))`.

But then: a DBA runs a bulk migration: `UPDATE users SET tier='GOLD' WHERE total_orders > 100`. This updates 50,000 rows directly in SQL. Application code never runs → no Kafka events → 50,000 users' caches stay stale → Elasticsearch is out of sync.

CDC captures the bulk migration automatically (it reads the WAL, which records all 50,000 UPDATE statements). Application events don't capture changes made outside the application. CDC is the only reliable way to capture ALL database changes.

---

### 🧠 Mental Model / Analogy

> CDC is like a bank statement feed. Instead of checking your balance periodically (polling), your bank sends you a notification for EVERY transaction (CDC). You see each deposit and withdrawal as it happens (sub-millisecond). The notification includes what changed: previous balance (before state) and new balance (after state). Any transaction, no matter how it was made (mobile app, ATM, wire transfer, bank adjustment), shows up in the feed.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** CDC = capture DB changes in real-time. Debezium reads WAL/binlog. Events: before/after + op (c/u/d). Use cases: cache invalidation, Elasticsearch sync, Transactional Outbox. vs polling: real-time, lower overhead.

**Level 2:** PostgreSQL: wal_level=logical + publication + replication slot. MySQL: binlog_format=ROW + server.id. Debezium connector config: server.name (topic prefix), table.include.list, snapshot.mode. Event envelope: before, after, op, source. Kafka topic per table: `{server}.{schema}.{table}`.

**Level 3:** Snapshot modes: `initial` (full table scan first then stream), `never` (stream only from now), `initial_only` (one-time load). Schema changes (DDL): Debezium handles most but `DROP COLUMN` can break things. MySQL stores schema history in Kafka topic (required for binlog column mapping). PostgreSQL handles DDL via WAL more gracefully. Debezium SMTs (Single Message Transforms): Outbox Router, Filtering (exclude rows), Value-to-Key SMT (customize Kafka key).

**Level 4:** Exactly-once CDC delivery: combine Debezium (at-least-once) + Kafka idempotent producer + Kafka transactions → exactly-once from DB to Kafka. Debezium Server: standalone Debezium without Kafka Connect (publishes directly to Kinesis, Pub/Sub, Redis Streams, HTTP sink). For low-latency use cases where full Kafka Connect infrastructure is too heavy. Debezium UI: management dashboard for connector lifecycle (available in Debezium 1.5+). For PostgreSQL: `pg_replication_slot_advance()` can manually advance a slot (use with caution — skips events). Production CDC: ensure pgoutput publication includes `REPLICA IDENTITY FULL` for UPDATE events to include the `before` state (default: before = null for UPDATEs).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ DEBEZIUM CDC ARCHITECTURE                            │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Application:                                        │
│   UPDATE users SET email='new@example.com'          │
│   WHERE id=1                                        │
│         ↓ write                                     │
│ PostgreSQL WAL:                                     │
│   [LSN 0/1234ABCD]: UPDATE users id=1               │
│     before: {email:'old@example.com'}               │
│     after: {email:'new@example.com'}                │
│         ↓ Debezium reads via replication slot       │
│ Debezium Connector:                                 │
│   Captures change event                             │
│   Publishes to: "appdb.public.users" Kafka topic   │
│         ↓                                           │
│ ┌────────────┬────────────┬──────────────────┐      │
│ │Redis Cache │Elasticsearch│Analytics DWH     │      │
│ │invalidate  │update index │stream ETL        │      │
│ │user:1      │doc id=1     │UPDATE dim_users  │      │
│ └────────────┴────────────┴──────────────────┘      │
│   All 3 consumers: independent, parallel            │
│   No application coupling, no polling               │
│                                                      │
│ REPLICA IDENTITY FULL on users table:               │
│   Ensures "before" state is populated for UPDATEs  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
User profile update → CDC → 3 systems in sync:

09:00:00.000 - API: PUT /users/1 {"email":"new@example.com"}
09:00:00.010 - UserService: UPDATE users SET email='new@...' WHERE id=1
09:00:00.011 - PostgreSQL: WAL record written (commit)

09:00:00.015 - Debezium: reads WAL → captures UPDATE on users.id=1
  Event: {before: {email:'old@...'}, after: {email:'new@...'}, op:'u', id:1}
  Publishes to Kafka "appdb.public.users", key="1"

09:00:00.020 - CacheInvalidationConsumer (groupId=cache-inv):
  Key = "1" → redisTemplate.delete("user:1")
  Next API call for user:1 → cache miss → DB fetch → re-populate

09:00:00.022 - ElasticsearchSyncConsumer (groupId=es-sync):
  PUT /users/_doc/1 {"email":"new@example.com", ...}
  Elasticsearch: search results now reflect new email

09:00:00.025 - DataWarehouseConsumer (groupId=dwh):
  Flink job: UPDATE dim_users SET email='new@...' WHERE user_id=1
  Analytics: user dimension table updated

Total end-to-end: ~25ms from API call to all 3 systems consistent

Bulk update scenario:
  DBA runs: UPDATE users SET tier='PREMIUM' WHERE orders_count > 50
  → 10,000 rows updated in one SQL statement
  → 10,000 CDC events published to Kafka
  → Cache, Elasticsearch, DWH all updated for all 10,000 users
  → Zero application code changes needed (CDC captures ALL SQL)
```

---

### ⚖️ Comparison Table

| Approach             | CDC (Debezium)           | Polling                     | Dual Write (App)        |
| -------------------- | ------------------------ | --------------------------- | ----------------------- |
| Latency              | Sub-millisecond          | Polling interval (30s-5min) | Synchronous             |
| DB overhead          | WAL read only            | SELECT queries              | None (app-level)        |
| All changes captured | YES (SQL, migrations)    | Only since last poll        | Only app changes        |
| Before/after state   | YES                      | Usually only after          | Usually only after      |
| Infrastructure       | Debezium + Kafka Connect | Scheduler in app            | None                    |
| Failure handling     | At-least-once (offset)   | Application retry           | Complex (partial fails) |
| Schema changes       | Handled by Debezium      | N/A                         | App-level               |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "CDC requires changes to application code"          | CDC reads from the DB transaction log, completely independent of application code. Zero application changes needed. This is its major advantage — it captures ALL changes including manual SQL, migrations, and bulk operations                                    |
| "CDC is the same as polling"                        | Fundamentally different: polling reads tables (overhead), CDC reads logs (minimal overhead). Polling has configurable latency; CDC is sub-millisecond. Polling doesn't capture before-state; CDC does                                                              |
| "Debezium handles all schema changes automatically" | Most schema changes (add column, modify type) are handled. But some changes break Debezium (drop column that Debezium is capturing, rename table without connector config update). CDC requires coordination between DB schema changes and connector configuration |

---

### 🚨 Failure Modes & Diagnosis

**1. UPDATE Events Have Null Before State**

**Symptom:** Cache invalidation fails — the `before` value is null for all UPDATE events. Redis key eviction doesn't work because you don't know what the previous email was.

**Root Cause:** PostgreSQL table's `REPLICA IDENTITY` is not set to `FULL`. Default (`DEFAULT`): only include primary key in `before` for UPDATEs. For cache invalidation (where you need the old value to know which cache key to evict), `FULL` is required.

**Fix:**

```sql
-- Set REPLICA IDENTITY FULL for tables where you need before-state in UPDATEs:
ALTER TABLE users REPLICA IDENTITY FULL;
ALTER TABLE orders REPLICA IDENTITY FULL;

-- Verify:
SELECT relname, relreplident FROM pg_class WHERE relname IN ('users', 'orders');
-- relreplident = 'f' → FULL; 'd' → DEFAULT (primary key only)

-- CAUTION: REPLICA IDENTITY FULL increases WAL size significantly
-- (WAL must store all column values for each UPDATE, not just changed + PK)
-- For very wide tables or high-update-rate tables: consider USING INDEX instead
-- USING INDEX: include specific indexed columns in before-state
ALTER TABLE users REPLICA IDENTITY USING INDEX users_email_idx;
```

---

### 🔗 Related Keywords

**Prerequisites:** Transactional Outbox, Apache Kafka
**Builds On This:** Data Replication Pipelines, Streaming ETL
**Related:** Transactional Outbox, Apache Kafka, Event-Driven Architecture

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION  │ Capture DB changes as real-time events    │
│ DEBEZIUM    │ Open-source CDC; PG/MySQL/MongoDB/Oracle  │
│ PG SOURCE   │ WAL + logical replication + slot          │
│ MYSQL SRC   │ Binlog (ROW format)                       │
│ ENVELOPE    │ before, after, op (c/u/d/r), source      │
│ TOPIC       │ {server}.{schema}.{table}                │
│ SNAPSHOT    │ initial = full load + stream changes      │
│ USE CASES   │ Cache invalidation, ES sync, DWH, Outbox │
│ vs POLLING  │ Sub-ms latency, WAL read, before+after   │
│ REPLICA ID  │ FULL needed for before-state in UPDATEs  │
│ WAL RISK    │ Slot fills disk if Debezium is down       │
│ ONE-LINER   │ "DB changes → WAL → Debezium → Kafka →  │
│             │  consumers; all changes, all sources"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is Change Data Capture? How does Debezium implement CDC for PostgreSQL? What information is included in a Debezium event envelope and what does each field mean?

**Q2.** (TYPE C — System Design) A financial services platform needs to: (1) Keep a Redis cache of user balances in sync with PostgreSQL in near real-time, (2) Update an Elasticsearch search index when account records change, (3) Audit ALL changes to accounts (including direct DB scripts, not just application changes). Design a CDC solution using Debezium. Address: PostgreSQL setup, connector configuration, consumer implementation for each use case, and what happens to `before` state for UPDATE events.
