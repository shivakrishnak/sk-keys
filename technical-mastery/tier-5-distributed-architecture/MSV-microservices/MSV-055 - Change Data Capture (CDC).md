---
id: MSV-055
title: Change Data Capture (CDC)
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-054, MSV-048
used_by: MSV-054
related: MSV-054, MSV-048, MSV-051, MSV-050, MSV-053, MSV-058
tags:
  - microservices
  - streaming
  - deep-dive
  - cdc
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/microservices/change-data-capture-cdc/
---

⚡ TL;DR - Change Data Capture (CDC) captures
database changes (INSERT, UPDATE, DELETE) in real
time by reading the database transaction log (WAL
for PostgreSQL, binlog for MySQL) rather than polling
the database. Primary tool: Debezium (open source,
Kafka Connect connector). CDC events are published
to Kafka topics. Use cases: Outbox Pattern relay,
real-time data synchronization, event-driven
replication, audit logging, cache invalidation.
Benefits: low latency (<10ms), zero application
code change for data capture, exactly captures
every change. Trade-offs: operational complexity
(Kafka Connect cluster), schema evolution requires
managed transitions.

| #055 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Outbox Pattern, Event-Driven Microservices | |
| **Used by:** | Outbox Pattern | |
| **Related:** | Outbox Pattern, Event-Driven Microservices, Event Sourcing in Microservices, CQRS in Microservices, Database per Service, Idempotency in Microservices | |

---

### 🔥 The Problem This Solves

**POLLING IS INEFFICIENT AND INCOMPLETE:**
Option 1: poll the database every N seconds for
changes (`SELECT * FROM orders WHERE updated_at
> ?`). Problems: (1) all tables need an `updated_at`
column; (2) DELETEs are invisible (row is gone);
(3) polling adds database load; (4) high latency
(N seconds between changes); (5) requires application
code changes. CDC reads the database transaction
log: captures ALL changes (INSERT, UPDATE, DELETE)
with sub-second latency, zero application code
change, minimal DB overhead.

---

### 📘 Textbook Definition

**Change Data Capture (CDC)** is a data integration
pattern that captures changes made to a database
(row-level INSERT, UPDATE, DELETE operations) by
reading the database's internal transaction log
rather than polling application tables. The transaction
log (PostgreSQL WAL = Write-Ahead Log; MySQL = binary
log) records every committed change before it is
applied to the data files. CDC tools (Debezium,
Maxwell's Daemon, AWS DMS) read this log and
convert database changes into structured events
published to a message broker (Kafka). Each change
event includes: before image (row state before
change), after image (row state after change), and
change type (INSERT/UPDATE/DELETE). These events
can be consumed by downstream systems for real-time
synchronization, event-driven workflows, and data
pipelines.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CDC reads database transaction logs to capture every
change (INSERT, UPDATE, DELETE) in real time and
publishes as events to Kafka. No polling, no code
changes.

**One analogy:**
> Imagine a bank's security camera records every
> transaction at every teller window. The camera
> records what was BEFORE (customer had $500) and
> AFTER (customer now has $300) and WHAT happened
> (withdrawal of $200). The bank doesn't need to
> ask the tellers to keep a separate log - the camera
> captures everything automatically. CDC is the
> security camera for your database. It records
> every change by watching the transaction log
> (the database's own internal record of what
> happened) rather than asking the application to
> report changes.

**One insight:**
CDC's critical advantage over application-level
eventing: CDC captures ALL changes, regardless of
how they were made. An emergency hotfix that directly
UPDATEs the database (bypassing the application):
CDC captures it. A migration script that batch-
INSERTs 1M rows: CDC captures every row. A
database-level trigger that makes changes: CDC
captures them. Application events only capture
what the application code explicitly publishes.
CDC captures the ground truth.

---

### 🔩 First Principles Explanation

**HOW POSTGRESQL WAL CDC WORKS:**

```
POSTGRESQL WRITE-AHEAD LOG (WAL):
  Before writing data to disk: PostgreSQL writes
  change to WAL (sequential log, fast I/O)
  WAL is an append-only transaction log
  Contains: every committed transaction
  Used for: crash recovery, streaming replication
  
  WAL record format:
  LSN (Log Sequence Number): position in WAL
  Transaction ID: which transaction made the change
  Table: which table was changed
  Operation: INSERT/UPDATE/DELETE
  Before image: old row values (for UPDATE/DELETE)
  After image: new row values (for INSERT/UPDATE)

DEBEZIUM CDC FLOW:
  1. Debezium registers as a PostgreSQL logical
     replication slot consumer
     (same protocol as streaming replication)
  2. PostgreSQL: streams WAL changes to Debezium
  3. Debezium: parses WAL records into change events
  4. Publishes: INSERT event to Kafka
     {before: null, after: {id:1, name:'Alice', ...}}
  5. Publishes: UPDATE event
     {before: {name:'Alice'}, after: {name:'Alice Smith'}}
  6. Publishes: DELETE event
     {before: {id:1, name:'Alice Smith'}, after: null}
  7. Debezium commits LSN: PostgreSQL knows
     WAL up to LSN can be reclaimed

KEY PROPERTY:
  Debezium reads changes AFTER they are committed
  (WAL records committed transactions)
  Change events: EXACTLY match what was committed
  No phantom reads, no uncommitted data
```

**DEBEZIUM EVENT ENVELOPE:**

```json
{
  "before": {
    "id": "order-001",
    "status": "PENDING",
    "total": 99.99
  },
  "after": {
    "id": "order-001",
    "status": "CONFIRMED",
    "total": 99.99
  },
  "source": {
    "connector": "postgresql",
    "db": "orders",
    "table": "orders",
    "lsn": 12345678,
    "ts_ms": 1704067200000
  },
  "op": "u",
  "ts_ms": 1704067200050
}
```

---

### 🧪 Thought Experiment

**CDC FOR CROSS-SERVICE SYNCHRONIZATION:**

```
SCENARIO:
  customer-service has a customers table
  order-service needs customer name for orders
  
  OPTION A: Application events
    customer-service: publishes CustomerUpdated
    when name changes via API
    Problem: direct DB updates (admin, migration)
    bypass events; order-service has stale data
  
  OPTION B: CDC
    Debezium: monitors customer-service's DB
    customers table: any change captured automatically
    Direct DB updates: captured (no bypass possible)
    Guarantee: ALL changes propagated to order-service
    Even schema changes detected (column added)
  
  USE CASE WHERE CDC IS ESSENTIAL:
    customer-service runs a data migration script:
    UPDATE customers SET name = TRIM(name)
    -- trims whitespace from all 10M customer names
    Application events: 0 events published
    (migration doesn't go through service code)
    CDC: 10M UpdatedCustomerName events published
    order-service: receives all 10M updates
    order-service customer_view: eventually updated
    Result: projection stays accurate
    Without CDC: projection permanently stale
```

---

### 🧠 Mental Model / Analogy

> CDC is like the "Track Changes" feature in a
> word processor. Every edit is recorded automatically:
> who changed what, from what to what, when. You
> don't need to ask the author to "remember to
> log their changes". The document tracks all changes
> at the infrastructure level. CDC does this for
> database tables: every INSERT, UPDATE, DELETE
> is automatically captured by the database engine
> (transaction log) and made available as a
> structured stream of events. No application code
> required. No changes missed.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
CDC watches the database and publishes a notification
to Kafka every time a row is added, changed, or
deleted. No application code needed. Every change,
captured in real time.

**Level 2 - How to use it (junior developer):**
Add a Debezium Kafka Connect connector configuration
pointing to your PostgreSQL database. Specify which
tables to watch. Debezium creates Kafka topics
automatically (one topic per table). Consume the
topics in downstream services. Debezium event:
contains before and after row values.

**Level 3 - How it works (mid-level engineer):**
PostgreSQL requires `wal_level = logical` for CDC.
Debezium uses logical replication protocol: creates
a replication slot; PostgreSQL sends WAL records
to Debezium as they are committed. Debezium: parses,
structures, and publishes. Offset tracking: Debezium
stores the LSN (WAL position) in Kafka. On restart:
resumes from last committed LSN. No events lost
between restarts.

**Level 4 - Why it matters (senior engineer):**
CDC solves the "impedance mismatch" between operational
databases and event-driven architectures. Without
CDC: developers must remember to publish events in
ALL code paths that modify data (service methods,
migration scripts, admin tools, bulk updates). Any
missed code path = silent data drift. CDC: the
database log is the single source of truth; CDC
captures everything from the log. This is the
"data as a stream" paradigm: every database table
becomes a Kafka topic; every change is an event.

**Level 5 - Mastery (principal engineer):**
CDC at scale: WAL growth and replication slot risk.
PostgreSQL: WAL is retained until the slowest
replication slot consumer acknowledges it. If Debezium
is down for hours: PostgreSQL keeps accumulating
WAL, potentially filling disk (`pg_wal` directory
grows unbounded). Production safeguard: set
`max_slot_wal_keep_size` (PostgreSQL 13+): automatically
drop the replication slot if WAL backlog exceeds
the limit. Monitor: `pg_replication_slots` -
`confirmed_flush_lsn` lag. Alert: if lag > 1GB.
Alternative: set `max_slot_wal_keep_size = 10GB`
and alert at 8GB to give time to investigate before
critical threshold.

---

### ⚙️ How It Works (Mechanism)

```yaml
# DEBEZIUM KAFKA CONNECT CONNECTOR CONFIGURATION
# Deploy in Kafka Connect cluster via REST API

POST /connectors
Content-Type: application/json

{
  "name": "orders-cdc-connector",
  "config": {
    "connector.class":
      "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "database.hostname": "orders-db.internal",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${file:/opt/secrets:db-password}",
    "database.dbname": "orders",
    "database.server.name": "orders-db",  # Kafka topic prefix
    "table.include.list": "orders.orders,orders.outbox_events",
    "plugin.name": "pgoutput",  # PostgreSQL 10+
    "publication.name": "dbz_publication",
    "slot.name": "debezium_orders_slot",
    "heartbeat.interval.ms": "1000",
    "snapshot.mode": "initial",  # Snapshot existing data
    # Transforms: for Outbox Pattern event routing
    "transforms": "outbox",
    "transforms.outbox.type":
      "io.debezium.transforms.outbox.EventRouter",
    "transforms.outbox.table.field.event.key":
      "aggregate_id",
    "transforms.outbox.route.by.field": "kafka_topic",
    "key.converter":
      "org.apache.kafka.connect.storage.StringConverter",
    "value.converter":
      "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url":
      "http://schema-registry:8081"
  }
}

# PostgreSQL setup: enable logical replication
# postgresql.conf:
# wal_level = logical
# max_replication_slots = 10
# max_wal_senders = 10

# Create replication user with correct permissions:
# CREATE USER debezium REPLICATION LOGIN PASSWORD '...';
# GRANT SELECT ON ALL TABLES IN SCHEMA orders TO debezium;
# CREATE PUBLICATION dbz_publication FOR TABLE orders.orders;
```

```java
// CONSUMER: Process CDC events from Kafka
@Component
public class OrderCdcConsumer {

    // Topic: orders-db.orders.orders (server.schema.table)
    @KafkaListener(
        topics = "orders-db.orders.orders",
        groupId = "order-analytics-cdc"
    )
    public void onOrderChange(
            @Payload OrderCdcEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key) {

        switch (event.getOp()) {
            case "c" ->  // CREATE (INSERT)
                analyticsService.recordNewOrder(
                    event.getAfter());
            case "u" ->  // UPDATE
                analyticsService.recordOrderUpdate(
                    event.getBefore(), event.getAfter());
            case "d" ->  // DELETE
                analyticsService.recordOrderDeletion(
                    event.getBefore());
            case "r" ->  // READ (snapshot)
                analyticsService.backfillOrder(
                    event.getAfter());
        }
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CDC FLOW WITH DEBEZIUM:

  order-service:
    INSERT INTO orders (status='CONFIRMED') at LSN=1234
    PostgreSQL: writes to WAL (LSN 1234)
    PostgreSQL: commits transaction
    
  Debezium:
    Reads WAL at LSN 1234
    Parses: INSERT, table=orders, after={...}
    Publishes: to orders-db.orders.orders Kafka topic
    Commits: LSN 1234 back to PostgreSQL
    Latency: < 10ms from DB commit to Kafka
  
  Consumers:
    analytics-service: receives INSERT event
      -> records new order in analytics DB
    search-service: receives INSERT event
      -> indexes order in Elasticsearch
    audit-service: receives INSERT event
      -> writes audit log entry
  
  OUTBOX PATTERN USE:
    INSERT INTO outbox_events (event_type='OrderCreated')
    Debezium: captures INSERT in outbox_events
    Routes: to order-events Kafka topic
    (based on outbox_events.kafka_topic field)
    Consumer: receives OrderCreated event
    Order of events: guaranteed (WAL sequential)
    Delivery: at-least-once (Debezium may resend
    on restart; consumers must be idempotent)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: polling vs CDC**

```java
// BAD: Polling-based change detection
// Misses: DELETEs (row gone), changes without updated_at
// Adds: DB load, latency (poll interval)
@Scheduled(fixedDelay = 5000)  // Every 5 seconds
public void pollForChanges() {
    List<Order> changed = orderRepo.findByUpdatedAtAfter(
        lastPollTime);
    // Problem 1: DELETE not captured (row is gone)
    // Problem 2: needs updated_at column in every table
    // Problem 3: 5-second latency for all changes
    // Problem 4: high DB load from constant SELECT
    changed.forEach(order ->
        analyticsService.process(order));
    lastPollTime = Instant.now();
}
```

```java
// GOOD: CDC via Debezium
// Captures: INSERT, UPDATE, DELETE
// Includes: before and after images
// Latency: < 10ms
// No application code changes needed
@KafkaListener(topics = "orders-db.orders.orders")
public void onOrderChange(OrderCdcEvent event) {
    // event.getOp(): c=insert, u=update, d=delete
    // event.getBefore(): row before change
    // event.getAfter(): row after change
    // Captures EVERYTHING including direct DB edits
    analyticsService.processCdcEvent(event);
}
// Zero polling; database-level completeness;
// <10ms latency; no updated_at column required
```

---

### ⚖️ Comparison Table

| Approach | Latency | DELETEs | App Code | DB Load | Completeness |
|---|---|---|---|---|---|
| **Polling (updated_at)** | Seconds | Missed | Required | High | Partial |
| **Database Triggers** | Low | Yes | No | High | Full |
| **Application Events** | Low | Yes | Required | Low | Partial (if missed) |
| **CDC (Debezium)** | <10ms | Yes | None | Minimal | Full |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CDC adds significant load to the database | CDC reads the WAL, which PostgreSQL already writes as part of its crash recovery mechanism. The overhead is minimal: Debezium reads sequentially from the WAL stream; no additional SELECT queries. The main overhead: CPU for logical decoding (WAL parsing). At high write throughput: measure logical replication CPU (typically 2-5% additional CPU for a busy production database). |
| CDC provides exactly-once delivery | CDC provides at-least-once delivery. If Debezium crashes between reading a change from WAL and committing the Kafka offset: on restart, it resends the change. Downstream consumers: must be idempotent. Exactly-once requires Kafka Transactions on the consumer side (read from CDC topic + write to destination in one Kafka transaction). |
| CDC replaces application events entirely | CDC and application events serve different purposes. CDC: captures ground truth from DB logs; includes before/after images; technical format (table structure). Application events: business semantics (OrderConfirmed, not "orders table updated"); published selectively; richer business context. Best practice: use CDC for Outbox Pattern relay, data sync, analytics. Use application events for business workflows between services. |

---

### 🚨 Failure Modes & Diagnosis

**PostgreSQL WAL disk full: Debezium connector down**

**Symptom:**
Debezium connector stopped. PostgreSQL disk usage:
95% and growing. `pg_wal` directory: 180GB.
All services: still writing to DB (no impact yet).
But: if disk fills 100%: PostgreSQL cannot write
WAL = PostgreSQL STOPS (cannot commit any transaction).

**Root Cause:**
Debezium was down for 6 hours (Kafka Connect
cluster restart took longer than expected). PostgreSQL:
retains WAL until the replication slot consumer
(Debezium) acknowledges. With Debezium down: no
ACK; WAL accumulates at write rate (30GB/hour).
6 hours * 30GB/hour = 180GB WAL retained.

**Diagnostic:**
```sql
-- Check replication slot lag
SELECT slot_name,
       active,
       pg_size_pretty(pg_wal_lsn_diff(
         pg_current_wal_lsn(),
         confirmed_flush_lsn)) AS lag
FROM pg_replication_slots;
-- slot_name        | active | lag
-- debezium_slot    | f      | 180 GB

-- Immediate fix: drop the slot to allow WAL reclaim
-- WARNING: events during downtime will be LOST!
SELECT pg_drop_replication_slot('debezium_slot');
-- After dropping: WAL reclaimed; disk recovers
-- Debezium restart: creates new slot; snapshot
-- from current state (events during outage: lost)
```

**Fix (long-term):**
```sql
-- PostgreSQL 13+: prevent unbounded WAL growth
-- postgresql.conf:
-- max_slot_wal_keep_size = 10GB
-- If slot lag exceeds 10GB: slot auto-dropped
-- (safer than filling disk)
```

Monitoring alert: Prometheus + `pg_replication_slots`
exporter. Alert at 5GB lag (long before 10GB limit).
Ensures Debezium is always running and healthy.

---

### 🔗 Related Keywords

**Primary use case:**
- `Outbox Pattern` - Debezium CDC is the preferred
  relay mechanism for Outbox events (WAL-based,
  low-latency, reliable)

**Enables:**
- `Event-Driven Microservices` - CDC turns database
  changes into events for downstream consumers
- `CQRS in Microservices` - CDC feeds read projections
  with real-time database changes

**Related patterns:**
- `Event Sourcing in Microservices` - event store
  changes captured via CDC for downstream projections
- `Database per Service` - CDC provides cross-service
  data propagation without shared database access

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ MECHANISM    │ Reads DB transaction log (WAL/binlog)    │
│              │ Publishes INSERT/UPDATE/DELETE to Kafka  │
├──────────────┼──────────────────────────────────────────┤
│ KEY TOOL     │ Debezium (Kafka Connect connector)       │
│              │ Postgres WAL, MySQL binlog, MongoDB oplog│
├──────────────┼──────────────────────────────────────────┤
│ RISK         │ WAL disk growth when consumer is down    │
│              │ Set max_slot_wal_keep_size in PostgreSQL │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Database log as event stream; captures  │
│              │  all changes without application code"   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. CDC reads the database transaction log (WAL),
   not the data files. Captures INSERT, UPDATE, DELETE
   in real time (<10ms). Zero application code changes.
2. Primary tool: Debezium (Kafka Connect). Publishes
   change events to Kafka with before/after images.
3. Critical risk: WAL disk growth when Debezium is
   down. Set `max_slot_wal_keep_size` in PostgreSQL.
   Monitor replication slot lag. Alert at 5GB lag.

**Interview one-liner:**
"CDC (Change Data Capture) captures database changes
(INSERT, UPDATE, DELETE) by reading the database
transaction log (PostgreSQL WAL, MySQL binlog) rather
than polling tables. Primary tool: Debezium (Kafka
Connect connector), publishes change events to Kafka
with before/after row images. Use cases: Outbox Pattern
relay (WAL-based, <10ms latency), cross-service data
sync, analytics event streams, CQRS projection updates.
Risk: WAL disk growth when Debezium is down;
mitigate with `max_slot_wal_keep_size` and lag
monitoring."

---

### 💡 The Surprising Truth

CDC is not a microservices-specific technology. It
has been used in enterprise data warehousing for
decades (Oracle GoldenGate, IBM InfoSphere CDC,
AWS DMS). What changed: open-source CDC (Debezium,
2016) made it accessible and Kafka made it scalable.
The real power of CDC in microservices: it makes
the database the event source without requiring
application code changes. Legacy systems with no
event publishing, monoliths being migrated, systems
with multiple write paths (app + migration scripts +
admin tools): CDC captures all of them. This makes
CDC the pragmatic choice for event-driven migration
of existing systems where adding event publishing
to every code path is impractical.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **SETUP** Deploy a Debezium PostgreSQL connector
   via Kafka Connect REST API. Configure: which
   tables to capture, WAL level, replication user
   permissions, publication name. Test: make a DB
   change and verify the Kafka event.
2. **EVENT FORMAT** Explain the Debezium event
   envelope: what fields are in `before`, `after`,
   `source`, `op`. What does `op: 'u'` look like
   for an UPDATE that changes one field? What does
   a DELETE event look like?
3. **WAL RISK** A Debezium connector is down for
   4 hours. Walk through: (1) what happens to WAL,
   (2) how to check current WAL lag, (3) options
   to recover without dropping the replication slot,
   (4) what `max_slot_wal_keep_size` does.
4. **OUTBOX INTEGRATION** Explain how Debezium is
   used as the relay for the Outbox Pattern. What
   is the EventRouter transform? How does it route
   outbox table changes to the correct Kafka topic?
5. **VS APPLICATION EVENTS** Given a specific scenario
   (e-commerce order service migration), decide:
   which changes should use CDC and which should
   use application events? Justify the boundary.

---

### 🧠 Think About This Before We Continue

**Q1.** You are migrating a monolith order service
to microservices. The monolith uses a PostgreSQL
database with 20 tables. You want to start event-
driving the system before the full microservices
refactor. How do you use CDC to start publishing
events from the monolith database TODAY without any
application code changes? What topics would you
create? What schema challenges do you face (DB
schema vs event schema)?

**Q2.** Your analytics team needs a real-time stream
of all database changes across 15 microservices (15
separate databases). Design the CDC infrastructure:
how many Debezium connectors, how many Kafka Connect
clusters, the Kafka topic naming convention, the
schema registry strategy, and how consumers know
which service a change came from.

**Q3.** An UPDATE CDC event arrives in your CQRS
projection consumer. The event shows `before: {status:
'PENDING'}` and `after: {status: 'CONFIRMED'}`. But
your projection already shows the order as CONFIRMED
(from a previous event that arrived out of order).
How do you handle this? Should you re-apply the
update? How do you detect and handle out-of-order
CDC events in a projection?