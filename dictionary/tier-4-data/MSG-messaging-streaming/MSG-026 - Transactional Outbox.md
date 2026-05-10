---
version: 2
layout: default
title: "Transactional Outbox"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: 26
permalink: /messaging-streaming/transactional-outbox/
id: MSG-026
category: Messaging & Event Streaming
difficulty: ★★★
depends_on: Outbox Pattern, Change Data Capture (CDC), Apache Kafka
used_by: Low-Latency Event Publishing, CDC-Based Outbox, Reliable Streaming
related: Outbox Pattern, Change Data Capture (CDC), Debezium
tags:
  - transactional-outbox
  - debezium
  - cdc
  - wal
  - kafka-connect
---

# MSG-026 - Transactional Outbox

⚡ TL;DR - **Transactional Outbox** = Outbox Pattern + **CDC (Change Data Capture)** via **Debezium** - instead of polling the outbox table, Debezium reads the **database transaction log** (PostgreSQL WAL, MySQL binlog) → captures INSERT to `outbox_events` → publishes to Kafka; advantages: **sub-millisecond latency** (no polling), **lower DB load** (reads from replication slot, not tables), **no locking** (no `SELECT FOR UPDATE`); Debezium **Outbox Router SMT** (Single Message Transform) routes events to correct Kafka topics automatically.

| #568            | Category: Big Data & Streaming                                     | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Outbox Pattern, Change Data Capture (CDC), Apache Kafka            |                 |
| **Used by:**    | Low-Latency Event Publishing, CDC-Based Outbox, Reliable Streaming |                 |
| **Related:**    | Outbox Pattern, Change Data Capture (CDC), Debezium                |                 |

---

### 🔥 The Problem This Solves

**POLLING RELAY LIMITATIONS:**
The Outbox Pattern with a polling relay has two problems: (1) **Latency**: average latency = polling interval ÷ 2 (500ms polling → ~250ms average latency). Not acceptable for near-real-time event processing. (2) **DB load**: every 500ms, a `SELECT ... FOR UPDATE` query hits the database. Under high volume: thousands of polls per minute, plus row-level locks that block concurrent writes. The Transactional Outbox solves both by replacing the polling relay with Debezium CDC: reads database transaction logs directly (zero polling overhead), captures changes at commit time (sub-millisecond latency), and requires no application-side polling process.

---

### 📘 Textbook Definition

**Transactional Outbox** is the Outbox Pattern implemented with CDC (Change Data Capture) instead of polling.

**How it works:**

1. **Write phase** (same as Outbox): write to business table + `outbox_events` table in one DB transaction.
2. **Capture phase (Debezium)**: Debezium connector reads the DB transaction log (PostgreSQL WAL, MySQL binlog). When a row is inserted into `outbox_events`, Debezium captures the change event.
3. **Publish phase**: Debezium Outbox Router SMT reads the event's `topic`, `key`, and `payload` fields → publishes to the correct Kafka topic (not the generic `outbox_events` Kafka topic).
4. **No status updates**: unlike polling relay, there's no `status='PUBLISHED'` update. Debezium uses the WAL offset as its position (committed = published). Idempotent producers + Debezium offset tracking ensure no duplicate publishes.

**Key component: Outbox Router SMT (Single Message Transform)**:

- Transforms Debezium's raw change event (which targets `server.schema.outbox_events` Kafka topic) into targeted events on the correct topic per outbox row's `topic` field.
- Eliminates the need to read from a generic outbox Kafka topic.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Transactional Outbox = Outbox Pattern + Debezium CDC; instead of polling, Debezium reads DB logs → publishes to Kafka sub-millisecond; Outbox Router SMT routes to correct topics.

**One analogy:**

> Polling relay = a secretary who checks the "Outbox" tray every 30 seconds. Slow, wastes trips.
> Debezium CDC = a sensor on the Outbox tray that triggers instantly when a letter is placed. Zero delay, no wasted trips.
> Both deliver the letter - CDC is just faster and more efficient.

**One insight:**
Debezium is an enterprise-grade CDC platform (originally Red Hat, Apache-licensed). It's used at Netflix, Airbnb, LinkedIn for CDC pipelines. For Transactional Outbox specifically, Debezium's Outbox Router SMT is purpose-built for this pattern - it transforms the generic `{op: c, before: null, after: {id, topic, key, payload}}` CDC event into `{topic: <from outbox row's topic field>, key: <key>, value: <payload>}`. This is exactly the message that downstream consumers should see, without exposing the outbox table internals.

---

### 🔩 First Principles Explanation

**DEBEZIUM CONNECTOR CONFIGURATION:**

```json
// Kafka Connect: deploy Debezium PostgreSQL connector
// POST to Kafka Connect REST API:
// curl -X POST http://kafka-connect:8083/connectors -H "Content-Type: application/json" -d @connector.json

{
  "name": "order-service-outbox-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${file:/opt/kafka/external.properties:db.password}",
    "database.dbname": "orderdb",
    "database.server.name": "order-db", // Kafka topic prefix
    "plugin.name": "pgoutput", // PostgreSQL logical replication plugin
    "publication.name": "debezium_publication", // PostgreSQL publication (created below)
    "slot.name": "order_service_slot", // replication slot name (unique)

    // Only capture changes to outbox_events table:
    "table.include.list": "public.outbox_events",

    // Outbox Router SMT: routes to correct Kafka topics
    "transforms": "outbox",
    "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
    "transforms.outbox.table.field.event.id": "id",
    "transforms.outbox.table.field.event.key": "message_key",
    "transforms.outbox.table.field.event.payload": "payload",
    "transforms.outbox.table.field.event.type": "event_type",
    "transforms.outbox.route.by.field": "topic",
    "transforms.outbox.route.topic.replacement": "${routedByValue}",
    // ^ Routes to the topic value from the 'topic' column in outbox_events

    // Tombstone deletion: delete outbox rows after publishing (optional)
    "transforms.outbox.table.expand.json.payload": "true",

    // Schema registry (if using Avro):
    // "key.converter": "io.confluent.kafka.serializers.KafkaAvroSerializer",
    // "value.converter": "io.confluent.kafka.serializers.KafkaAvroSerializer",

    // Kafka producer settings (acks=all for durability):
    "producer.override.acks": "all",
    "producer.override.enable.idempotence": "true"
  }
}
```

**POSTGRESQL SETUP (LOGICAL REPLICATION):**

```sql
-- Enable logical replication in postgresql.conf:
-- wal_level = logical
-- max_replication_slots = 10
-- max_wal_senders = 10

-- Create replication user:
CREATE USER debezium WITH REPLICATION LOGIN PASSWORD 'secure_password';
GRANT SELECT ON TABLE outbox_events TO debezium;
-- For logical replication, also need:
GRANT USAGE ON SCHEMA public TO debezium;

-- Create publication (what Debezium will replicate):
CREATE PUBLICATION debezium_publication FOR TABLE outbox_events;
-- Debezium will now receive change events for all INSERTs/UPDATEs/DELETEs on outbox_events

-- Replication slot (created automatically by Debezium, or manually):
-- SELECT pg_create_logical_replication_slot('order_service_slot', 'pgoutput');
```

**SPRING BOOT: WRITE TO OUTBOX (SAME AS POLLING OUTBOX, NO CHANGE):**

```java
// The application code is IDENTICAL to polling Outbox Pattern
// The change is in the relay (Debezium CDC vs polling scheduler)

@Service
@Transactional
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private OutboxEventRepository outboxRepository;

    @Autowired
    private ObjectMapper objectMapper;

    public Order placeOrder(CreateOrderRequest request) throws JsonProcessingException {
        // Write 1: business entity
        Order order = new Order(request);
        orderRepository.save(order);

        // Write 2: outbox event (SAME transaction)
        OutboxEvent event = OutboxEvent.builder()
            .topic("order-events")          // Debezium routes to "order-events" Kafka topic
            .messageKey(order.getId().toString())
            .eventType("OrderCreated")      // for filtering/routing
            .payload(objectMapper.writeValueAsString(new OrderCreatedEvent(order)))
            .build();
        outboxRepository.save(event);

        // Both committed atomically
        // Debezium reads WAL → captures outbox INSERT → publishes to "order-events" topic
        // Latency from DB commit to Kafka publish: ~1-10ms (WAL capture latency)

        return order;
    }
}
```

**OUTBOX TABLE (EXTENDED FOR DEBEZIUM OUTBOX ROUTER SMT):**

```sql
CREATE TABLE outbox_events (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id VARCHAR(255) NOT NULL,    -- e.g., orderId (for key)
    aggregate_type VARCHAR(100) NOT NULL,  -- e.g., "Order" (for routing context)
    event_type   VARCHAR(100) NOT NULL,    -- e.g., "OrderCreated"
    topic        VARCHAR(255) NOT NULL,    -- Kafka topic to route to
    message_key  VARCHAR(255),             -- Kafka message key
    payload      JSONB NOT NULL,           -- event payload
    created_at   TIMESTAMP NOT NULL DEFAULT NOW()

    -- NO status column (Debezium tracks offset in replication slot)
    -- NO retry_count (Debezium handles retries via offset replay)
    -- OPTIONAL: add tombstone deletion via Debezium after-publish hook
);

-- Note: no status column needed!
-- Debezium uses WAL offset as "what's been published" cursor
-- If Debezium crashes: restart → re-reads from last committed WAL offset → re-publishes
-- Kafka idempotent producer (enable.idempotence=true): deduplicates re-published events
```

**DEBEZIUM EVENT TRANSFORMATION (OUTBOX ROUTER SMT):**

```
WITHOUT Outbox Router SMT:
  Debezium publishes to: "order-db.public.outbox_events" (topic per table)
  Event format: {
    "before": null,
    "after": {"id":"abc", "topic":"order-events", "message_key":"123", "payload":"{...}"},
    "op": "c"  // c=create (INSERT)
  }
  Consumer: must parse the nested "after" → extract payload → find correct topic
  → messy, couples consumers to outbox schema

WITH Outbox Router SMT ("transforms.outbox.route.by.field": "topic"):
  Debezium publishes to: "order-events" (the value of the "topic" column)
  Event format: the VALUE of the "payload" column directly
  Key: the value of "message_key" column
  Consumer: receives clean OrderCreatedEvent directly
  → transparent to consumer (they don't know about outbox table)

Example:
  INSERT INTO outbox_events (topic='order-events', message_key='123', payload='{"orderId":"123",...}')

  Debezium WAL capture → SMT → publish to Kafka topic "order-events":
    Key: "123"
    Value: {"orderId":"123", "amount":50, "userId":"u456"}

  NotificationService @KafkaListener(topics="order-events"):
    receives: {"orderId":"123", "amount":50, "userId":"u456"}
    // No knowledge of outbox table
```

---

### 🧪 Thought Experiment

**REPLICATION SLOT BACKPRESSURE:**

Debezium creates a PostgreSQL replication slot. The replication slot RETAINS WAL segments until Debezium consumes them. If Debezium is down for 24 hours: PostgreSQL WAL accumulates 24 hours of changes. PostgreSQL disk: fills up with WAL segments. PostgreSQL crash: disk full = DB crash.

**Critical production requirement**: Monitor replication slot lag and Debezium health. Set `max_slot_wal_keep_size` (PostgreSQL 13+) to limit WAL accumulation. Alert if Debezium is down for > 1 hour (before WAL fills disk). This is the #1 operational risk of CDC with PostgreSQL.

---

### 🧠 Mental Model / Analogy

> PostgreSQL WAL = a security camera recording every change (never stops, perfectly accurate). Debezium = a security guard watching the live feed and writing down what happened. Polling relay = guard who checks the filing cabinet every 30 seconds. CDC = guard with live access to the camera feed (real-time, no delay).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Transactional Outbox = Outbox + Debezium CDC. App writes to outbox table. Debezium reads DB log → publishes to Kafka. Outbox Router SMT routes to correct topics. Sub-millisecond latency. No polling.

**Level 2:** PostgreSQL: WAL (Write-Ahead Log) + logical replication + publication + replication slot. Debezium reads from replication slot. SMT transforms raw change events into routed, clean Kafka messages. No `status` column needed - offset tracks what's published.

**Level 3:** Replication slot risks: Debezium down → WAL accumulates → disk full → DB crash. Mitigation: monitor `pg_replication_slots` lag (`SELECT slot_name, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag FROM pg_replication_slots`). Alert threshold: > 5GB WAL lag. `max_slot_wal_keep_size = 10GB` (PostgreSQL 13+) limits WAL retention (but Debezium may miss events if exceeded).

**Level 4:** Debezium in Kafka Connect cluster: Debezium connector = Kafka Connect connector plugin. Kafka Connect provides: distributed execution, fault tolerance, offset storage (in Kafka's `connect-offsets` topic). Connector config stored in `connect-configs` topic. Connector status in `connect-status` topic. For zero-downtime upgrades: pause connector → upgrade → resume (offsets preserved). Exactly-once with Debezium: Debezium + Kafka transactions + idempotent producers = end-to-end exactly-once from DB to downstream consumer. Complex but achievable.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ TRANSACTIONAL OUTBOX WITH DEBEZIUM                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ OrderService:                                       │
│   @Transactional:                                   │
│     INSERT orders (id='123', ...)                   │
│     INSERT outbox_events (topic='order-events',     │
│                           key='123', payload={...}) │
│   COMMIT → WAL record written                       │
│                                                      │
│ PostgreSQL WAL: [... INSERT outbox_events row ...]  │
│                                                      │
│ Debezium (reads WAL via replication slot):          │
│   Captures: INSERT to outbox_events                 │
│   Row: {topic:'order-events', key:'123', payload:...}│
│                                                      │
│ Outbox Router SMT:                                  │
│   Routes to Kafka topic: "order-events"             │
│   Message key: "123"                                │
│   Message value: {orderId:'123', amount:50, ...}    │
│                                                      │
│ NotificationService @KafkaListener:                 │
│   Receives: OrderCreatedEvent {orderId:'123', ...}  │
│                                                      │
│ Latency: DB commit → Kafka publish: ~1-10ms         │
│ (vs polling relay: ~250ms)                          │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Transactional Outbox in production (3-service e-commerce):

Infrastructure:
  PostgreSQL (order DB) + replication slot "order_slot"
  Debezium PostgreSQL connector (Kafka Connect cluster)
  Kafka (3-broker cluster)
  NotificationService, InventoryService (consumers)

Flow:
  1. POST /orders → OrderService.placeOrder()
  2. DB transaction: INSERT orders + INSERT outbox_events [same TX]
  3. PostgreSQL WAL: captures both INSERTs atomically

  4. Debezium: reads WAL via "order_slot"
     Finds: INSERT to outbox_events → captures change event

  5. Outbox Router SMT:
     Reads "topic" column = "order-events"
     Reads "message_key" = orderId
     Reads "payload" = OrderCreatedEvent JSON
     → Publishes to Kafka "order-events" topic, key=orderId

  6. NotificationService (groupId=notifications):
     @KafkaListener → receives OrderCreatedEvent
     Idempotency check (processedMessages table, key=orderId)
     sendEmail() → ACK

  7. InventoryService (groupId=inventory):
     @KafkaListener → receives same OrderCreatedEvent
     decreaseStock(event.items) → ACK

Failure and recovery:
  Case: Debezium crashes after step 4 but before step 5
  Recovery: Debezium restarts → reads from last WAL offset in connect-offsets topic
  Re-captures and re-publishes → idempotent Kafka producer deduplicates
  Consumers: already-processed events skipped (idempotency check)

  Case: Kafka down during step 5
  Debezium: buffered in connect worker memory (or task retried)
  PostgreSQL WAL: retained in replication slot
  Debezium retries until Kafka available → publishes when Kafka recovers
  Latency impact: +Kafka downtime duration; no data loss
```

---

### ⚖️ Comparison Table

| Dimension          | Outbox (Polling)                    | Outbox (CDC/Debezium)                     |
| ------------------ | ----------------------------------- | ----------------------------------------- |
| Latency            | 100ms-1s (polling interval)         | 1-10ms (WAL capture)                      |
| DB load            | Polling queries + row locks         | Replication slot (WAL read)               |
| Status tracking    | `status` column (PENDING/PUBLISHED) | Debezium WAL offset                       |
| Infrastructure     | Scheduler in app                    | Debezium + Kafka Connect                  |
| Complexity         | Low                                 | High (Debezium config, replication slots) |
| Operational risk   | Low                                 | Replication slot lag (WAL disk fill)      |
| Duplicate handling | Retry with idempotency              | Idempotent producer + consumer            |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                         |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Debezium provides exactly-once"                               | Debezium provides at-least-once (WAL re-read on restart → possible re-publish). Kafka idempotent producer deduplicates within a session. For end-to-end exactly-once: need Kafka transactions + idempotent consumers            |
| "The status column in outbox_events is required with Debezium" | NO - Debezium tracks position via WAL offset in connect-offsets Kafka topic. No status column needed. In fact, STATUS updates would create ADDITIONAL WAL events (UPDATEs) that Debezium would also capture (unnecessary noise) |
| "Transactional Outbox is the same as just the Outbox Pattern"  | Transactional Outbox specifically refers to the CDC (Debezium) variant. The polling variant is usually just called "Outbox Pattern." Both solve dual-write, but CDC provides lower latency and less polling overhead            |

---

### 🚨 Failure Modes & Diagnosis

**1. PostgreSQL Disk Full - Replication Slot Lag**

**Symptom:** PostgreSQL WAL directory fills up disk. DB crashes with "no space left on device". Debezium was down for several hours.

**Root Cause:** Replication slot retains WAL until Debezium consumes it. Debezium downtime = WAL accumulation.

**Diagnosis:**

```sql
-- Check replication slot lag:
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag_size,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
FROM pg_replication_slots;
-- If lag_bytes > 5GB → alert!
-- If Debezium is inactive (active=false) → CRITICAL: WAL accumulating

-- Emergency: if Debezium cannot recover quickly and WAL fills disk:
-- DROP replication slot (will lose Debezium position → possible duplicate events):
SELECT pg_drop_replication_slot('order_service_slot');
-- After: Debezium restarts from "earliest" or configured snapshot mode
-- Downstream: consumers see duplicate events → idempotency handles them
```

**Prevention:**

```sql
-- PostgreSQL 13+: limit WAL size for slot
ALTER SYSTEM SET max_slot_wal_keep_size = '10GB';
SELECT pg_reload_conf();

-- Alert if slot lag > 1GB:
-- Prometheus query: pg_replication_slots_wal_status_size > 1073741824
```

---

### 🔗 Related Keywords

**Prerequisites:** Outbox Pattern, Change Data Capture (CDC)
**Builds On This:** Low-Latency Event Pipelines
**Related:** Outbox Pattern, Change Data Capture (CDC), Debezium

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ vs POLLING  │ CDC: sub-ms; no polling; no status col    │
│ DEBEZIUM    │ Reads PostgreSQL WAL via replication slot │
│ SMT         │ Routes to correct Kafka topic (not generic)│
│ NO STATUS   │ Debezium tracks via WAL offset            │
│ IDEMPOTENT  │ Still needed (WAL re-read on restart)     │
│ PG SETUP    │ wal_level=logical + publication + slot    │
│ WAL RISK    │ Slot fills disk if Debezium down          │
│ MONITOR     │ pg_replication_slots lag + disk space     │
│ LATENCY     │ 1-10ms (vs 100ms-1s polling)             │
│ COMPLEXITY  │ Higher than polling (Debezium infra)      │
│ ONE-LINER   │ "Outbox + Debezium CDC: WAL capture →    │
│             │  Kafka publish in sub-ms; no polling"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the difference between the Outbox Pattern (polling relay) and the Transactional Outbox (CDC with Debezium)? What are the advantages of CDC? What is the most critical operational risk of Debezium's replication slot?

**Q2.** (TYPE C - System Design) A high-throughput order service processes 50,000 orders/minute. They currently use a polling Outbox relay (500ms interval) but the 250ms average latency is too slow for near-real-time inventory updates. Design the Transactional Outbox with Debezium: PostgreSQL configuration, Debezium connector settings, Outbox Router SMT configuration, and how you would monitor for the replication slot WAL disk fill risk.
