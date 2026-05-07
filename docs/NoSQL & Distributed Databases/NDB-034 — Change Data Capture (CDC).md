---
layout: default
title: "Change Data Capture (CDC)"
parent: "NoSQL & Distributed Databases"
nav_order: 34
permalink: /nosql/change-data-capture-cdc/
number: "NDB-034"
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Distributed Transactions, Saga Pattern (DB), Kafka
used_by: Polyglot Persistence, Event-Driven Architecture, System Design
related: Saga Pattern (DB), Polyglot Persistence, Outbox Pattern
tags:
  - nosql
  - cdc
  - debezium
  - event-sourcing
  - deep-dive
---

# NDB-034 — Change Data Capture (CDC)

⚡ TL;DR — CDC taps the database's internal transaction log (PostgreSQL WAL, MySQL binlog, MongoDB oplog) to capture every row-level change as a stream of events — without modifying the application — enabling real-time data pipelines to Kafka, Elasticsearch, Redis, or any downstream system with millisecond latency and zero data loss.

| #473            | Category: NoSQL & Distributed Databases                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Transactions, Saga Pattern (DB), Kafka             |                 |
| **Used by:**    | Polyglot Persistence, Event-Driven Architecture, System Design |                 |
| **Related:**    | Saga Pattern (DB), Polyglot Persistence, Outbox Pattern        |                 |

---

### 🔥 The Problem This Solves

**DUAL-WRITE IS UNRELIABLE:**
A common data pipeline pattern is "dual write": when saving an order to PostgreSQL, also write an event to Kafka or update Elasticsearch. The problem: these are two separate I/O operations. If PostgreSQL commits but the Kafka write fails (or vice versa), the systems are inconsistent. Using a distributed transaction (2PC) for database + message broker is supported by JTA but complex and imposes performance overhead.

**POLLING IS SLOW AND EXPENSIVE:**
An alternative is polling: every 5 seconds, `SELECT * FROM orders WHERE updated_at > last_poll_time`. Problems: (1) requires an `updated_at` column, often missing on legacy tables; (2) misses deletes; (3) polling interval means up to 5-second lag; (4) high read load on the database during batch polls.

**CDC SOLVES BOTH:**
CDC reads the database's existing transaction log — a durable, append-only record the database already maintains. Every committed change (INSERT, UPDATE, DELETE) is captured in the order it occurred, without modifying the application or adding columns. This achieves: exactly-once ordering (same order as the database committed), zero-missed events (including DELETEs), millisecond latency, and no extra write overhead.

---

### 📘 Textbook Definition

**Change Data Capture (CDC)** is a pattern for tracking changes to data in a database and making those changes available as a stream for downstream consumption. **Log-based CDC** reads the database's replication log: **WAL** (Write-Ahead Log) in PostgreSQL, **binlog** in MySQL/MariaDB, **oplog** in MongoDB. The CDC connector reads the log, transforms each change into a structured event (with before/after image of the row), and publishes it to a message broker (typically Kafka). **Debezium** is the dominant open-source CDC framework (Kafka Connect plugin), supporting PostgreSQL, MySQL, MongoDB, Oracle, SQL Server, and others. CDC events contain: **operation** (c=create/insert, u=update, d=delete, r=snapshot read), **before** (row state before change — null for inserts), **after** (row state after change — null for deletes), **source** metadata (database, table, WAL LSN/binlog position, commit timestamp). A **snapshot** (initial load) captures the existing table state before CDC streaming begins, ensuring the downstream system gets the full dataset, not just future changes. **Outbox Pattern** combined with CDC: application writes events to an `outbox` table (same ACID transaction as the business change), CDC captures the outbox table → Kafka, guaranteed exactly-once (no dual-write problem).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CDC reads the database's own transaction log to capture every committed change — no dual-write, no polling, just an event stream of exactly what happened and in what order.

**One analogy:**

> A bank processes thousands of transactions daily. The audit department doesn't ask tellers to photocopy every transaction slip (polling), nor does it ask tellers to file a separate report while serving customers (dual write). Instead, it reads the official ledger (transaction log) — every transaction is already recorded there in order. CDC is the audit department reading the ledger. The bank (application) has no extra work.

- "Tellers photocopying slips" → polling (`SELECT WHERE updated_at > last`)
- "Tellers filing separate report" → dual write (app writes to DB + Kafka)
- "Reading the official ledger" → log-based CDC (reads WAL/binlog)
- "Audit department" → CDC connector (Debezium)
- "Tellers have no extra work" → zero application change required

**One insight:**
CDC with the Outbox Pattern solves the dual-write problem perfectly: (1) Application writes business data + an outbox event in a single ACID transaction. (2) CDC reads the outbox table from the WAL. (3) CDC publishes the event to Kafka. Step 1 is atomic (ACID). Steps 2-3 are at-least-once (Debezium retries on failure). The application never writes to Kafka directly — Kafka only sees events that were durably committed to the database. This achieves transactional outbox (database commits ↔ Kafka events are coupled) without XA/2PC.

---

### 🔩 First Principles Explanation

**POSTGRESQL WAL AND LOGICAL REPLICATION:**

```
PostgreSQL WAL (Write-Ahead Log):
  - Every change to the database is first written to WAL before applying to data files
  - WAL purpose: crash recovery (replay WAL to recover committed transactions)
  - WAL also supports logical replication: expose changes at row level (not raw bytes)

Logical Replication Slots:
  - A replication slot tracks the WAL position of a consumer (Debezium connector)
  - PostgreSQL keeps WAL segments until ALL slots have consumed them
  - Risk: if a slot is inactive (connector down), WAL accumulates → disk full

  CREATE PUBLICATION orders_pub FOR TABLE orders;  -- expose orders table
  SELECT * FROM pg_create_logical_replication_slot('debezium_slot', 'pgoutput');
  -- Debezium creates and manages this slot automatically

Debezium change event structure:
{
  "before": null,                          // null for INSERT (no prior state)
  "after": {
    "id": 12345,
    "customer_id": 67890,
    "status": "CREATED",
    "total": 99.99
  },
  "source": {
    "db": "ecommerce",
    "table": "orders",
    "lsn": "0/16A5F60",                   // WAL position (Log Sequence Number)
    "ts_ms": 1720000000000,               // commit timestamp
    "txId": 498                           // PostgreSQL transaction ID
  },
  "op": "c",                             // c=create, u=update, d=delete, r=read(snapshot)
  "ts_ms": 1720000000010                  // event processing timestamp
}
```

**DEBEZIUM CONNECTOR CONFIGURATION:**

```json
// POST to Kafka Connect REST API: /connectors
{
  "name": "orders-postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres-host",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "debezium-password",
    "database.dbname": "ecommerce",
    "database.server.name": "ecommerce-postgres",

    // Tables to capture (whitelist)
    "table.include.list": "public.orders,public.order_items,public.outbox_events",

    // Kafka topic naming: {server.name}.{schema}.{table}
    // → ecommerce-postgres.public.orders

    // Snapshot mode: initial = snapshot then stream; never = only stream future changes
    "snapshot.mode": "initial",

    // PostgreSQL replication plugin
    "plugin.name": "pgoutput",

    // Slot name (created once; must be unique per connector)
    "slot.name": "debezium_orders_slot",

    // Publication name
    "publication.name": "debezium_publication",

    // Heartbeat interval (prevents WAL accumulation when no changes occur)
    "heartbeat.interval.ms": "5000",

    // Schema registry for Avro serialization
    "key.converter": "io.confluent.kafka.serializers.KafkaAvroSerializer",
    "value.converter": "io.confluent.kafka.serializers.KafkaAvroSerializer",
    "key.converter.schema.registry.url": "http://schema-registry:8081",
    "value.converter.schema.registry.url": "http://schema-registry:8081"
  }
}
```

**OUTBOX PATTERN + CDC (ZERO DUAL-WRITE):**

```java
@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    private UUID id;               // idempotency key for downstream consumer
    private String aggregateType;  // e.g., "Order"
    private String aggregateId;    // e.g., order ID
    private String type;           // e.g., "OrderCreated"
    private String payload;        // JSON payload
    private Instant createdAt;
}

@Service
@Transactional
public class OrderService {

    public Order placeOrder(OrderRequest request) {
        // Business write
        Order order = new Order(request.getCustomerId(), request.getItems());
        order.setStatus("CREATED");
        orderRepository.save(order);

        // Outbox event write — SAME TRANSACTION as business write
        OutboxEvent event = new OutboxEvent(
            UUID.randomUUID(),        // idempotency key
            "Order",
            order.getId().toString(),
            "OrderCreated",
            objectMapper.writeValueAsString(new OrderCreatedPayload(order))
        );
        outboxRepository.save(event);

        // SINGLE COMMIT — if this fails, NEITHER order NOR event is saved
        // If this succeeds, CDC (Debezium) will capture outbox_events row → Kafka
        // No dual-write problem: Kafka write is decoupled from this transaction
        return order;
    }
}

// Debezium captures outbox_events INSERT → publishes to Kafka
// Consumer: Kafka topic "ecommerce-postgres.public.outbox_events"
// → routes to target topic based on aggregateType field (Debezium Outbox SMT)
// → exactly-once delivery from DB perspective (idempotent Kafka key = event.id)
```

**ELASTICSEARCH SYNC WITH CDC:**

```java
// Consumer: syncs orders from Kafka CDC stream to Elasticsearch
@Component
public class OrderSearchIndexer {

    @KafkaListener(
        topics = "ecommerce-postgres.public.orders",
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void handleOrderChange(ConsumerRecord<String, OrderCdcEvent> record) {
        OrderCdcEvent event = record.value();

        switch (event.getOp()) {
            case "c", "u", "r" -> {   // create, update, snapshot-read
                OrderSearchDocument doc = toSearchDoc(event.getAfter());
                elasticsearchClient.index(idx -> idx
                    .index("orders")
                    .id(doc.getId())
                    .document(doc)
                );
            }
            case "d" -> {             // delete
                elasticsearchClient.delete(del -> del
                    .index("orders")
                    .id(event.getBefore().getId())
                );
            }
        }
    }
}
// Lag between DB commit and ES index: typically 50-200ms (Debezium + Kafka + consumer)
// On consumer crash: Kafka offset committed only after ES ack → no data loss
// On duplicate (at-least-once): ES index/delete is idempotent for same ID
```

---

### 🧪 Thought Experiment

**WHAT IF THE DEBEZIUM CONNECTOR GOES DOWN FOR 6 HOURS?**

The PostgreSQL replication slot keeps accumulating WAL segments — the WAL is NOT deleted because the slot hasn't consumed it. After 6 hours on a high-write database (1GB WAL/hour), 6GB of WAL is retained.

**RISKS:**

1. Disk full: if the PostgreSQL host's disk fills with unread WAL, PostgreSQL pauses all writes (to prevent data corruption). This is a production-stopping event.
2. On Debezium restart: it resumes from the stored WAL position — all 6 hours of changes are replayed. This is correct behavior (no data loss) but creates a Kafka backlog: all downstream consumers are 6 hours behind.

**MITIGATIONS:**

- Monitor replication slot lag: `SELECT * FROM pg_replication_slots` — alert if `confirmed_flush_lsn` is more than 1GB behind current WAL position
- Set `max_slot_wal_keep_size` (PostgreSQL 13+): if WAL exceeds this limit, the slot is invalidated (slot is deleted) — Debezium must re-snapshot. Prevents disk full at the cost of needing a re-snapshot.
- Set `heartbeat.interval.ms` in Debezium: sends periodic heartbeat writes to advance the replication slot even when no application changes occur, preventing WAL accumulation in idle periods.

---

### 🧠 Mental Model / Analogy

> CDC with Debezium is like installing a security camera in a library. The librarians (application) continue checking books in and out normally — no extra paperwork. The camera (Debezium) records every transaction in the order it happens. At any time, you can review the footage (WAL) to know exactly what was borrowed and when. The library also has a running highlight reel (Kafka) that shows only the last 7 days. If the camera is unplugged, the original footage (WAL) is still preserved — but only if the DVR (replication slot) has space.

- "Librarians doing normal work" → application writing to database (no code change)
- "Security camera" → Debezium CDC connector
- "Camera recording footage" → Debezium reading WAL
- "Highlight reel" → Kafka topics with retention period
- "Camera unplugged" → connector down
- "DVR space" → replication slot WAL retention (bounded by disk)

---

### 📶 Gradual Depth — Four Levels

**Level 1:** CDC reads the database's transaction log to capture every INSERT/UPDATE/DELETE as an event, in order, in real time. Used to sync data to Elasticsearch, invalidate caches, feed analytics pipelines, or publish domain events to Kafka — without changing application code or polling the database.

**Level 2:** Use Debezium for PostgreSQL/MySQL/MongoDB. Deploy as a Kafka Connect plugin. Set `snapshot.mode: initial` to capture existing rows before streaming. Monitor `pg_replication_slots` — alert if slot lag > threshold. Combine with Outbox Pattern: app writes outbox table + business table in one ACID transaction; Debezium captures outbox → Kafka — no dual-write. Always handle both `before` and `after` in your consumer (UPDATE needs `before` for cache invalidation, `after` for index update).

**Level 3:** Schema evolution: Debezium uses Kafka Schema Registry (Avro/Protobuf) to track schema versions. Adding a nullable column to the source table is safe (schema evolves, consumers see null for old events). Renaming columns or removing non-nullable columns breaks consumers — coordinate with consumers before schema change. Tombstone events: when Debezium captures a DELETE, it publishes: first, the delete event (`op: d`, `after: null`); then a tombstone (null value with the row key) to allow Kafka log compaction to remove the key from the compacted log. Consumers must handle null values (tombstones) without NPE. SMT (Single Message Transforms): Kafka Connect transforms applied before publishing — common use: Outbox Event Router (routes events from outbox table to per-aggregate Kafka topics), Flatten (flattens the `after` field to top-level), filter (skip CDC events for certain operations or tables).

**Level 4:** CDC is fundamentally a replication mechanism with event semantics. The WAL is the source of truth for the database's change history — CDC leverages this to decouple application writes from event publication. The key architectural insight: the WAL provides total order (every change is assigned a monotonically increasing LSN in PostgreSQL) and durability (changes in WAL are guaranteed to have been committed). By reading the WAL, CDC inherits these properties: events are published in commit order, and no committed change is ever missed. This makes CDC stronger than application-level event publishing (which can fail between commit and publish) and stronger than polling (which misses deletes and has ordering uncertainty). The Outbox Pattern leverages this: by writing events to the database, the application delegates the publication responsibility to CDC, which has stronger guarantees. The combination achieves transactional messaging without a distributed transaction: database atomicity ensures the outbox event is written if and only if the business data is written, and CDC ensures the event is published if and only if the outbox write is present in the WAL.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CDC DATA FLOW                                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 1. App writes to PostgreSQL (INSERT/UPDATE/DELETE)   │
│    → PostgreSQL writes to WAL first (durability)     │
│    → PostgreSQL applies to data files                │
│                                                      │
│ [CDC ← YOU ARE HERE: connector reads WAL]            │
│                                                      │
│ 2. Debezium connector (Kafka Connect):               │
│    → Reads WAL via logical replication slot          │
│    → Decodes WAL bytes → structured change event     │
│    → Enriches with before/after/source metadata      │
│    → Publishes to Kafka topic (one topic per table)  │
│    → Commits WAL offset to replication slot          │
│                                                      │
│ 3. Kafka consumers:                                  │
│    → Elasticsearch Indexer: index/update/delete docs │
│    → Cache Invalidator: evict stale Redis keys       │
│    → Analytics Pipeline: stream to data warehouse    │
│    → Saga Orchestrator: react to outbox events       │
│                                                      │
│ 4. On consumer failure:                              │
│    → Kafka retains events (configurable retention)   │
│    → Consumer resumes from last committed offset     │
│    → No data loss, at-least-once delivery            │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**E-COMMERCE: SEARCH INDEX SYNC WITH OUTBOX PATTERN + CDC:**

```
1. User updates product description in Admin UI
→ ProductService.updateProduct(productId, request)
→ [CDC ← YOU ARE HERE: outbox + product update in one ACID txn]

2. @Transactional:
   UPDATE products SET description = '...' WHERE id = 123
   INSERT INTO outbox_events (type='ProductUpdated', aggregate_id='123', payload={...})
   COMMIT → PostgreSQL WAL: [UPDATE products row, INSERT outbox_events row]

3. Debezium reads outbox_events INSERT from WAL
→ Outbox Event Router SMT:
   - routes to Kafka topic: "products" (based on aggregateType field)
   - key: "123" (aggregateId = consistent Kafka partition routing for same product)
   - value: ProductUpdated payload

4. Kafka consumer: ElasticsearchSyncService
→ reads "ProductUpdated" {id: 123, description: '...'}
→ es.index(index="products", id="123", doc={...})
→ commits Kafka offset

5. Next search query for product 123:
→ hits Elasticsearch → returns updated description
→ propagation latency: typically 100-500ms after DB commit ✓

If Step 4 fails (ES down):
→ consumer does not commit offset
→ Kafka retains event
→ ES recovers → consumer replays from last committed offset
→ event replayed → ES indexed
→ eventually consistent ✓ (no data loss)
```

---

### ⚖️ Comparison Table

| Aspect                  | Log-based CDC (Debezium)          | Polling (`updated_at`)         | Dual Write                    |
| ----------------------- | --------------------------------- | ------------------------------ | ----------------------------- |
| Captures DELETEs        | YES (tombstone events)            | NO                             | YES (explicit)                |
| Requires schema change  | NO                                | YES (`updated_at` column)      | NO                            |
| Application code change | NO                                | YES (polling queries)          | YES (add write to app)        |
| Consistency             | Strong (WAL order = commit order) | Eventual (up to poll interval) | Unreliable (write 2 can fail) |
| Latency                 | Milliseconds                      | Seconds (poll interval)        | Sub-millisecond (direct)      |
| Failure impact          | WAL accumulation risk             | High read load                 | Inconsistency on failure      |
| Complexity              | Medium (Kafka Connect config)     | Low                            | Low (until it fails)          |

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                       |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CDC modifies the source database"                            | Log-based CDC (Debezium) only reads the WAL via a logical replication slot. It does not write to the source database (except for the replication slot metadata and optional heartbeat writes) |
| "CDC guarantees exactly-once delivery to consumers"           | Debezium provides at-least-once delivery to Kafka. Making consumers idempotent (using the event `id` or WAL LSN as an idempotency key) achieves effective exactly-once processing             |
| "CDC can be used without Kafka"                               | Debezium is a Kafka Connect plugin and requires Kafka. For Kafka-less CDC, alternatives exist (Debezium Server with direct HTTP/Kinesis sink), but most production CDC deployments use Kafka  |
| "CDC replication slot is harmless if the connector goes down" | An inactive replication slot causes WAL accumulation. If the disk fills, PostgreSQL stops all writes. Always monitor slot lag and set `max_slot_wal_keep_size`                                |

---

### 🚨 Failure Modes & Diagnosis

**1. Replication Slot WAL Accumulation — Disk Full Risk**

**Symptom:** Debezium connector is stopped for 4+ hours. PostgreSQL disk usage is growing rapidly. No alerts were configured for replication slot lag.

**Diagnosis:**

```sql
-- Check replication slot status and lag
SELECT
    slot_name,
    plugin,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
    confirmed_flush_lsn,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag_pretty
FROM pg_replication_slots;

-- If lag_bytes is > 1GB and connector is inactive, take action:

-- Option 1: Restart connector (preferred — no data loss)
-- POST /connectors/orders-postgres-connector/restart

-- Option 2: Drop inactive slot (data loss — connector will re-snapshot)
SELECT pg_drop_replication_slot('debezium_orders_slot');
-- Then restart Debezium with snapshot.mode=initial to re-snapshot
```

**Prevention:**

```sql
-- postgresql.conf: limit WAL retained for inactive slots
max_slot_wal_keep_size = '10GB'  -- auto-invalidate slot if lag exceeds this

-- Alert: monitor replication slot lag
-- Prometheus: pg_replication_slots_pg_wal_lsn_diff gauge
-- Alert threshold: lag_bytes > 2GB → warning, > 5GB → critical
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Transactions, Saga Pattern (DB), Kafka
**Builds On This:** Polyglot Persistence, Event-Driven Architecture
**Related:** Saga Pattern (DB), Polyglot Persistence, Outbox Pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ READS       │ PostgreSQL WAL / MySQL binlog / Mongo oplog│
│ TOOL        │ Debezium (Kafka Connect plugin)            │
│ CAPTURES    │ INSERT/UPDATE/DELETE in commit order       │
│ RISK        │ Inactive slot → WAL accumulation → disk    │
│ MONITOR     │ pg_replication_slots (lag_bytes alert)     │
│ OUTBOX      │ App writes outbox+biz in 1 ACID txn; CDC → │
│             │ Kafka; solves dual-write problem            │
│ LATENCY     │ 50-200ms DB commit → Kafka → consumer      │
│ DELIVERY    │ At-least-once → make consumers idempotent  │
│ ONE-LINER   │ "Read the WAL, not the application —       │
│             │  zero code change, millisecond sync"        │
│ NEXT EXPLORE│ Database Proxy (PgBouncer) → Data Locality │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) You are designing a CDC pipeline for a healthcare application. The `patients` table in PostgreSQL contains PII (name, DOB, SSN). The CDC stream needs to feed: (a) an audit log system (needs all fields), (b) an analytics system (must NOT receive PII). Design the CDC pipeline to serve both consumers. Consider: Kafka topic structure, field masking/filtering, access control, and what happens if the masking transform has a bug.

**Q2.** (TYPE D — Failure Scenario) A Debezium connector is running in production. The engineering team applies a database migration: `ALTER TABLE orders DROP COLUMN internal_notes`. The connector was not stopped before the migration. After the migration, the Debezium connector immediately stops with: `ERROR: column "internal_notes" of relation "orders" does not exist`. Diagnosis: why did this happen? How does the Debezium Schema Registry relate to this failure? How do you recover without data loss? What is the correct procedure for future schema changes?
