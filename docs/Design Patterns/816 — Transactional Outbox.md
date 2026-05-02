---
layout: default
title: "Transactional Outbox"
parent: "Design Patterns"
nav_order: 816
permalink: /design-patterns/transactional-outbox/
number: "816"
category: Design Patterns
difficulty: ★★★
depends_on: "Outbox Pattern, Saga Pattern, Event-Driven Pattern, Change Data Capture"
used_by: "Microservices, saga orchestration, reliable event publishing, CDC pipelines"
tags: #advanced, #design-patterns, #distributed-systems, #messaging, #cdc, #microservices
---

# 816 — Transactional Outbox

`#advanced` `#design-patterns` `#distributed-systems` `#messaging` `#cdc` `#microservices`

⚡ TL;DR — **Transactional Outbox** is a specific Outbox Pattern implementation that uses CDC (Change Data Capture) — via Debezium reading the database WAL — to publish outbox events to a message broker with sub-second latency and zero polling overhead.

| #816            | Category: Design Patterns                                                   | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Outbox Pattern, Saga Pattern, Event-Driven Pattern, Change Data Capture     |                 |
| **Used by:**    | Microservices, saga orchestration, reliable event publishing, CDC pipelines |                 |

---

### 📘 Textbook Definition

**Transactional Outbox** (formalized by Chris Richardson in "Microservices Patterns", 2018): a refinement of the Outbox Pattern that specifically combines the Outbox with Change Data Capture (CDC) as the relay mechanism. Rather than a polling relay (which introduces latency and DB load), CDC tools (primarily Debezium) tail the database's Write-Ahead Log (WAL) and detect outbox table inserts in near-real-time, forwarding them to a message broker. Key properties: atomicity (outbox write in same DB transaction as domain write), at-least-once delivery, sub-second latency (WAL-based, not polling), zero DB polling overhead, CDC infrastructure must be sized and monitored as a production component.

---

### 🟢 Simple Definition (Easy)

Outbox Pattern (807) + CDC relay instead of polling. The difference: polling checks the outbox table every 500ms-1s (adds latency, costs DB queries). CDC reads the PostgreSQL Write-Ahead Log (a real-time stream of all committed changes) — detects the outbox insert within milliseconds and publishes to Kafka. Same atomicity guarantee, same at-least-once delivery — but faster and less DB load.

---

### 🔵 Simple Definition (Elaborated)

Polling relay: "Are there unpublished events? Check. No. Check. No. Check. Yes! Publish. Mark published." Overhead: N queries per second against the outbox table, even when there are no events. CDC relay: Debezium tails the PostgreSQL WAL (the database's own append-only change log). When the outbox INSERT commits, Debezium sees it within milliseconds and publishes to Kafka. Zero polling. Latency: ~50-100ms vs. 500ms-1s for polling. At 10K events/second: CDC is dramatically more efficient.

---

### 🔩 First Principles Explanation

**Debezium + PostgreSQL WAL Transactional Outbox setup:**

```
POSTGRESQL WAL-BASED CDC:

  PostgreSQL Write-Ahead Log (WAL):
  - All committed transactions written to WAL (redo log)
  - WAL = sequential, durable, ordered log of all DB changes
  - Replication slots: external consumers can read the WAL

  Debezium:
  - Runs as a Kafka Connect connector
  - Connects to PostgreSQL via logical replication slot
  - Reads WAL → converts to Kafka messages per table row change
  - Supports: INSERT, UPDATE, DELETE events per table

  For Outbox: only outbox_events INSERTs matter (ignore UPDATE/DELETE).

DEBEZIUM OUTBOX EVENT ROUTER (Kafka Connect SMT):

  Debezium ships an "Outbox Event Router" Single Message Transform (SMT).
  Purpose: transform a raw outbox_events INSERT → properly formatted event message.

  Without SMT: Kafka message topic = "mydb.public.outbox_events" (all events in one topic)
  With SMT:
  - Route to topic based on: aggregateType (e.g., "Order" → "order")
  - Use aggregateId as Kafka message key (enables ordering per aggregate)
  - Use payload field as message value
  - Filters out the outbox table envelope (no OutboxEvent metadata in the event)

  Kafka Connect connector config (debezium-postgres-outbox.json):
  {
    "name": "order-service-outbox",
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium_user",
    "database.password": "secret",
    "database.dbname": "orderdb",
    "database.server.name": "orderdb",
    "table.include.list": "public.outbox_events",     // Only outbox table
    "plugin.name": "pgoutput",
    "publication.name": "outbox_pub",
    "slot.name": "outbox_slot",
    "transforms": "outbox",
    "transforms.outbox.type":
      "io.debezium.transforms.outbox.EventRouter",
    "transforms.outbox.table.field.event.id": "id",
    "transforms.outbox.table.field.event.key": "aggregate_id",
    "transforms.outbox.table.field.event.type": "event_type",
    "transforms.outbox.table.field.event.payload": "payload",
    "transforms.outbox.route.by.field": "aggregate_type",
    "transforms.outbox.route.topic.replacement": "${routedByValue}"
  }

  Result: INSERT to outbox_events with aggregate_type="Order" →
          Kafka message on topic "Order" with key=aggregate_id, value=payload

POSTGRESQL SETUP FOR DEBEZIUM:

  -- Enable logical replication (postgres.conf or RDS parameter):
  wal_level = logical

  -- Create publication for outbox table only:
  CREATE PUBLICATION outbox_pub FOR TABLE outbox_events;

  -- Create replication user with replication privilege:
  CREATE USER debezium_user WITH REPLICATION LOGIN PASSWORD 'secret';
  GRANT SELECT ON outbox_events TO debezium_user;

  -- Replication slot (created automatically by Debezium on first start):
  -- SELECT * FROM pg_replication_slots;

WAL RETENTION RISK:

  Replication slot: PostgreSQL retains WAL segments until the slot consumer reads them.
  If Debezium goes down for extended period: WAL retention grows unbounded → disk full.

  MITIGATION:
  -- Set maximum replication slot WAL size (PostgreSQL 13+):
  max_slot_wal_keep_size = '1GB'   -- if exceeded: slot is invalidated

  Monitor: SELECT slot_name, pg_size_pretty(pg_wal_lsn_diff(
               pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag
           FROM pg_replication_slots;
  Alert: if lag > 500MB.

  If slot invalidated: Debezium must re-snapshot from scratch.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT CDC Relay (polling relay):

- DB queries every N milliseconds even with no new events (wasted load)
- Polling interval adds latency (500ms-1s vs. <100ms for CDC)
- At high volume: polling relay becomes a bottleneck

WITH Transactional Outbox (CDC relay):
→ Sub-second event propagation. Zero polling overhead. WAL-based: exactly tracks DB commits. Scales to high event volume without proportional DB load increase.

---

### 🧠 Mental Model / Analogy

> A newspaper reporter checking their mailbox every hour for story tips (polling relay). vs. A journalist who has a direct wire to the newsroom — every tip is transmitted the moment it's written (CDC relay). The mailbox check: guaranteed to find the tip eventually (at most 1 hour late), but wastes 23 trips per day when the box is empty. The direct wire: tip arrives within seconds, no empty trips. Transactional Outbox with Debezium = direct wire from database to Kafka, reading the database's own WAL as the wire.

"Checking mailbox every hour" = polling relay (`@Scheduled` every 500ms)
"Empty mailbox trips" = polling overhead when no events pending
"At most 1-hour delay" = 500ms-1s polling latency
"Direct wire from newsroom" = Debezium reading PostgreSQL WAL
"Tip arrives within seconds" = WAL-based CDC detects insert < 100ms
"No empty trips" = CDC reacts to actual WAL events — no polling

---

### ⚙️ How It Works (Mechanism)

```
TRANSACTIONAL OUTBOX + DEBEZIUM ARCHITECTURE:

  ┌──────────────────────────────────────────────┐
  │  Order Service                               │
  │  @Transactional createOrder() {             │
  │    orderRepo.save(order)  ───┐              │
  │    outboxRepo.save(event) ───┤ ONE TX       │
  │  }                           │              │
  └──────────────────────────────┼──────────────┘
                                 │
  ┌──────────────────────────────▼──────────────┐
  │  PostgreSQL                                 │
  │  ┌─────────────┐  ┌──────────────────────┐ │
  │  │ orders      │  │ outbox_events        │ │
  │  │ (committed) │  │ (committed INSERT)   │ │
  │  └─────────────┘  └──────────┬───────────┘ │
  │                               │             │
  │  WAL: ... INSERT outbox_events ← committed  │
  └───────────────────────────────┼─────────────┘
                                  │ Debezium reads WAL
                                  │ (logical replication slot)
  ┌───────────────────────────────▼─────────────┐
  │  Debezium Kafka Connect Connector           │
  │  - Reads WAL commit                         │
  │  - Outbox Event Router SMT:                 │
  │    aggregate_type="Order" →                 │
  │    topic="Order", key=aggregateId           │
  └───────────────────────────────┬─────────────┘
                                  │
  ┌───────────────────────────────▼─────────────┐
  │  Apache Kafka                               │
  │  Topic: Order (key=orderId)                 │
  │  Event: OrderCreated payload                │
  └─────────────────────────────────────────────┘
  Latency: DB commit → Kafka: ~50-100ms
```

---

### 🔄 How It Connects (Mini-Map)

```
Outbox Pattern + CDC relay = Transactional Outbox
        │
        ▼
Transactional Outbox ◄──── (you are here)
(Debezium reads WAL; sub-second latency; no polling; at-least-once delivery)
        │
        ├── Outbox Pattern (807): parent pattern — Transactional Outbox is the CDC-relay variant
        ├── Saga Pattern: Transactional Outbox used at each saga step for reliable event publishing
        ├── CQRS Pattern: Transactional Outbox feeds the read-model update pipeline
        └── Change Data Capture: Debezium is the CDC tool enabling Transactional Outbox
```

---

### 💻 Code Example

```java
// Application code: identical to Outbox Pattern (807)
// The difference is in the relay infrastructure (Debezium, not polling)

@Service @RequiredArgsConstructor @Transactional
public class OrderService {
    private final OrderRepository orderRepo;
    private final OutboxEventRepository outboxRepo;

    public Order createOrder(CreateOrderCommand cmd) {
        Order order = new Order(cmd.getCustomerId(), cmd.getItems(), cmd.getTotal());
        orderRepo.save(order);

        // Outbox write — same transaction:
        // Debezium will detect this INSERT via WAL and publish to Kafka "Order" topic
        outboxRepo.save(OutboxEvent.of(
            "Order",                // aggregate_type → Kafka topic name
            order.getId().toString(), // aggregate_id → Kafka message key
            "OrderCreated",          // event_type → included in Kafka message header
            serialize(new OrderCreatedEvent(order))  // payload → Kafka message value
        ));

        return order;
    }
}

// No polling relay needed — Debezium handles publication.
// No published_at column needed in outbox_events — Debezium reads and publishes.
// Outbox table is append-only from application perspective.
// Cleanup: Debezium published_at tracking is external (Kafka consumer offset).

// MONITORING (Kafka Connect REST API):
// GET /connectors/order-service-outbox/status
// → { "connector": {"state": "RUNNING"}, "tasks": [{"state": "RUNNING"}] }

// Alert if connector not RUNNING:
// Implication: outbox events accumulating, not being published to Kafka.
// Check: SELECT COUNT(*), MAX(created_at) FROM outbox_events;
// Growing count + old max created_at: Debezium lag / failure.
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Transactional Outbox and Outbox Pattern are different patterns | They are the same pattern — the distinction is the relay mechanism. "Outbox Pattern" typically refers to the overall pattern (atomic write to outbox + asynchronous relay). "Transactional Outbox" often specifically refers to the CDC-based relay variant. Some sources use them interchangeably; others reserve "Transactional Outbox" for the Debezium-based CDC variant. The core mechanism (atomic local transaction) is identical. |
| Debezium guarantees exactly-once delivery                      | Debezium provides at-least-once delivery. If Debezium publishes an event to Kafka and then fails before committing its consumer offset, it will re-read and re-publish the event on restart. Combine with Kafka idempotent producers and transactional consumers for stronger guarantees. Downstream consumers must be idempotent.                                                                                                        |
| Debezium is simple to operate at scale                         | Debezium running on Kafka Connect is production-grade but operationally complex: replication slot monitoring, WAL retention management, Kafka Connect cluster sizing, connector failure handling, schema evolution in the outbox payload, Debezium version upgrades. Teams new to CDC should assess this operational complexity before adopting vs. the simpler polling relay.                                                            |

---

### 🔥 Pitfalls in Production

**Replication slot lag causing PostgreSQL disk exhaustion:**

```sql
-- ANTI-PATTERN: Debezium connector down for 6 hours, no monitoring:

-- WAL retention: PostgreSQL holds ALL WAL since Debezium's last read position
-- 6 hours × 500MB WAL/hour = 3GB WAL retained
-- PostgreSQL disk: 10GB total → 70% full → DB performance degradation
-- PostgreSQL disk full → DB crash → complete service outage

-- MONITORING (add to Prometheus/Grafana):
-- pg_replication_slot_files: Prometheus postgres_exporter metric
-- Alert: if pg_replication_slot_files{slot_name="outbox_slot"} > 500 (500 WAL files)

-- SAFEGUARD: max_slot_wal_keep_size (PostgreSQL 13+):
ALTER SYSTEM SET max_slot_wal_keep_size = '2GB';
SELECT pg_reload_conf();
-- If slot lag exceeds 2GB: slot invalidated.
-- Implication: Debezium must re-snapshot. All pending outbox events in those WAL files
-- were already committed to the outbox table → Debezium reads from last checkpoint.
-- Some events may be re-published (at-least-once) — idempotent consumers handle this.

-- MONITORING query (add to health check):
SELECT
    slot_name,
    pg_size_pretty(
        pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)
    ) AS replication_lag,
    active
FROM pg_replication_slots
WHERE slot_name = 'outbox_slot';

-- Alert threshold: replication_lag > '1GB' → PagerDuty alert.
-- Runbook: (1) Check Debezium connector status; (2) Restart if failed;
--           (3) If disk > 80%: temporarily drop + recreate slot after Debezium recovers.
```

---

### 🔗 Related Keywords

- `Outbox Pattern` — parent pattern: Transactional Outbox is the CDC-relay variant
- `Change Data Capture (CDC)` — Debezium: the CDC tool tailing the PostgreSQL WAL
- `Saga Pattern` — Transactional Outbox used at each saga step for reliable command/event publishing
- `CQRS Pattern` — CDC feeds read model updates; Transactional Outbox feeds event streams
- `Kafka Connect` — the infrastructure running Debezium connectors

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Outbox Pattern + Debezium CDC relay.     │
│              │ Reads PostgreSQL WAL in real-time.       │
│              │ Sub-second latency. No polling overhead. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High-volume event publishing (>100 evt/s);│
│              │ low-latency event propagation required;  │
│              │ polling relay too slow or too costly     │
├──────────────┼───────────────────────────────────────────┤
│ MONITOR      │ Replication slot WAL lag;                │
│              │ Kafka Connect connector status;          │
│              │ PostgreSQL disk usage near replication   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Direct wire vs. mailbox: Debezium reads │
│              │  the WAL in real-time; no empty polling │
│              │  trips to the database."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Debezium → Kafka Connect → CDC →         │
│              │ Outbox Pattern → CQRS → Saga              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Debezium supports multiple databases: PostgreSQL, MySQL, MongoDB, SQL Server, Oracle. Each uses a different replication mechanism: PostgreSQL uses logical replication (WAL); MySQL uses the binary log (binlog); MongoDB uses the oplog (capped collection). For PostgreSQL, the publication/subscription model (`wal_level=logical`, `CREATE PUBLICATION`) requires specific DB configuration. What operational prerequisites must be in place on PostgreSQL for Debezium to work, and what are the implications of enabling logical replication on a high-write-throughput production PostgreSQL instance (WAL volume, replication latency, disk pressure)?

**Q2.** The Outbox Event Router SMT (Single Message Transform) in Debezium routes outbox events to different Kafka topics based on the `aggregate_type` field. But Kafka topic ordering guarantees are per-partition: messages with the same key go to the same partition. The aggregate_id is used as the Kafka message key, ensuring all events for the same aggregate (e.g., all events for order-123) are ordered within a partition. But what happens to ordering if the same aggregate has events published by two different microservices (e.g., OrderService publishes OrderCreated, PaymentService publishes PaymentCompleted — both with key=orderId but to different topics)? How do you design event ordering guarantees across topics in an event-driven system?
