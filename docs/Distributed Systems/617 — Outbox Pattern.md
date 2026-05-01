---
layout: default
title: "Outbox Pattern"
parent: "Distributed Systems"
nav_order: 617
permalink: /distributed-systems/outbox-pattern/
number: "617"
category: Distributed Systems
difficulty: ★★★
depends_on: "Event-Driven Architecture, Idempotency (Distributed)"
used_by: "Debezium, Spring Modulith, Kafka, Transactional Outbox"
tags: #advanced, #distributed, #reliability, #messaging, #transactions
---

# 617 — Outbox Pattern

`#advanced` `#distributed` `#reliability` `#messaging` `#transactions`

⚡ TL;DR — The **Outbox Pattern** solves the dual-write problem: instead of writing to the DB and publishing an event atomically (impossible across two systems), write both to the **same DB transaction** — the event row in an outbox table — then a relay process publishes it to the message broker asynchronously.

| #617            | Category: Distributed Systems                          | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Event-Driven Architecture, Idempotency (Distributed)   |                 |
| **Used by:**    | Debezium, Spring Modulith, Kafka, Transactional Outbox |                 |

---

### 📘 Textbook Definition

**Outbox Pattern** (Transactional Outbox Pattern) is a reliability pattern that guarantees at-least-once delivery of domain events to a message broker. The dual-write problem: a service that writes to the DB AND publishes to Kafka — if the DB commits but the Kafka publish fails (or vice versa), the systems become inconsistent. The Outbox Pattern: write DB state change AND the outgoing event to the SAME local database transaction (atomically). A separate relay process (outbox relay/CDC) polls or subscribes to the outbox table and publishes events to the message broker. On failure: the relay retries. Events delivered at-least-once (consumers must be idempotent). Implementations: (1) **Polling relay** — polls outbox table periodically. Simple but adds DB load and latency. (2) **CDC (Change Data Capture) relay** — Debezium reads the database transaction log (WAL for PostgreSQL, binlog for MySQL), captures outbox table changes, publishes to Kafka. Near real-time, low DB overhead.

---

### 🟢 Simple Definition (Easy)

Email outbox: you write an email and click Send. It goes to your Outbox folder first (saved locally). The email client then sends it to the mail server. If your internet drops: the email stays in Outbox and sends later. You never lose a drafted email. Same idea: your service writes the event to an "outbox" table (same DB transaction as your business data). A relay process sends it to Kafka. If Kafka is down: event stays in outbox until Kafka recovers. Event never lost.

---

### 🔵 Simple Definition (Elaborated)

The problem without outbox: OrderService saves the order to PostgreSQL AND publishes OrderCreated to Kafka. Between the two writes: the service crashes. PostgreSQL: order saved. Kafka: no event. Result: InventoryService never reserves items. Order stuck. Customer complains. With outbox: single DB transaction: save order + insert outbox row. If crash happens before outbox row published: relay retries. If crash happens after: idempotent consumers ignore the duplicate. The only failure mode: DB commit fails (then nothing happened — consistent).

---

### 🔩 First Principles Explanation

**Dual-write problem, outbox table, polling relay, CDC with Debezium:**

```
DUAL-WRITE PROBLEM (why outbox is needed):

  WITHOUT OUTBOX:

    BEGIN TRANSACTION:
      INSERT INTO orders (id, status, ...) VALUES ('abc-123', 'PLACED', ...);
    COMMIT; -- DB write succeeds.

    // === CRASH ZONE: service crashes here ===

    kafkaTemplate.send("order-events", new OrderCreated("abc-123")); // NEVER EXECUTED.

  Result: Order exists in DB. No Kafka event. Downstream services: never notified.
  Inconsistency: permanent (unless manual fix).

  REVERSE FAILURE:
    kafkaTemplate.send("order-events", new OrderCreated("abc-123")); // Succeeds.
    // Kafka broker confirms.

    BEGIN TRANSACTION:
      INSERT INTO orders (...) VALUES (...);
    // === DB failure (connection reset) ===
    ROLLBACK; // Order not saved.

  Result: Kafka event published. DB: no order. Downstream: processes event for non-existent order.

  ROOT CAUSE: Two systems (PostgreSQL, Kafka) = two separate transaction coordinators.
  No atomic commit across both without distributed transactions (2PC — too expensive).

OUTBOX PATTERN SOLUTION:

  Outbox table in SAME database as business data:

    CREATE TABLE outbox (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        event_type VARCHAR NOT NULL,          -- e.g., 'OrderPlaced'
        aggregate_id VARCHAR NOT NULL,        -- e.g., 'abc-123'
        aggregate_type VARCHAR NOT NULL,      -- e.g., 'Order'
        payload JSONB NOT NULL,               -- event data
        created_at TIMESTAMPTZ DEFAULT NOW(),
        published BOOLEAN DEFAULT FALSE,      -- polling relay: mark when published
        published_at TIMESTAMPTZ             -- for cleanup/debugging
    );

  WRITE FLOW (single DB transaction):
    BEGIN TRANSACTION:
      INSERT INTO orders (id, status, ...) VALUES ('abc-123', 'PLACED', ...);
      INSERT INTO outbox (event_type, aggregate_id, payload)
        VALUES ('OrderPlaced', 'abc-123', '{"userId": "u-456", "total": 75.00}');
    COMMIT;

  GUARANTEE:
    Case A: COMMIT succeeds → both order row AND outbox row exist → relay publishes event.
    Case B: COMMIT fails → neither row exists → no event → no inconsistency.
    Case C: Relay crashes after DB commit but before publishing → relay retries on restart.
      (outbox row still unpublished: published=FALSE → relay retries).

  RESULT: At-least-once delivery guarantee.
  Consumers: MUST be idempotent (relay may publish same event twice on retry).

POLLING RELAY:

  Separate process (thread, scheduled job, or microservice):

    @Scheduled(fixedDelay = 100) // Poll every 100ms
    @Transactional
    public void pollAndPublish() {
        List<OutboxEvent> unpublished = outboxRepo.findByPublishedFalseOrderByCreatedAtAsc();

        for (OutboxEvent event : unpublished) {
            try {
                kafkaTemplate.send(
                    topicFor(event.getEventType()),
                    event.getAggregateId(), // Partition key for ordering.
                    event.getPayload()
                ).get(); // Wait for Kafka acknowledgement.

                event.setPublished(true);
                event.setPublishedAt(Instant.now());
                outboxRepo.save(event);
            } catch (Exception e) {
                log.error("Failed to publish outbox event {}", event.getId(), e);
                // Don't mark as published. Will retry on next poll.
            }
        }
    }

    // Cleanup: delete published events older than 7 days.
    @Scheduled(cron = "0 0 * * * *") // Hourly
    public void cleanupOldPublishedEvents() {
        outboxRepo.deleteByPublishedTrueAndPublishedAtBefore(
            Instant.now().minus(7, ChronoUnit.DAYS));
    }

  DRAWBACKS OF POLLING:
    Latency: up to poll interval (100ms-1s).
    DB load: constant polling query even when no events.
    Thundering herd: many events → many rows → slow query.

  OPTIMIZATION: Use SELECT FOR UPDATE SKIP LOCKED for concurrent relay instances:
    @Query("SELECT o FROM OutboxEvent o WHERE o.published = FALSE ORDER BY o.createdAt FOR UPDATE SKIP LOCKED")
    List<OutboxEvent> findUnpublishedForUpdate();
    // Multiple relay instances: each locks different rows. No duplicate publishing.

CDC RELAY WITH DEBEZIUM (production-grade):

  Debezium: Change Data Capture tool. Reads database transaction log.
  PostgreSQL: WAL (Write-Ahead Log). MySQL: binlog.

  Debezium reads: every row INSERT in outbox table → publishes to Kafka.
  No polling. Near-real-time (WAL-based, sub-100ms lag).
  No additional DB load (reads WAL, not rows).

  DEBEZIUM CONFIGURATION (PostgreSQL outbox):
    {
      "name": "outbox-connector",
      "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": "postgres",
        "database.dbname": "orders",
        "table.include.list": "public.outbox",
        "transforms": "outbox",
        "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
        "transforms.outbox.table.field.event.id": "id",
        "transforms.outbox.table.field.event.key": "aggregate_id",
        "transforms.outbox.table.field.event.type": "event_type",
        "transforms.outbox.table.field.event.payload": "payload",
        "transforms.outbox.route.by.field": "aggregate_type"
        // Routes to topic: "Order", "Payment", etc. based on aggregate_type.
      }
    }

  DEBEZIUM FLOW:
    1. DB transaction commits: outbox row inserted.
    2. PostgreSQL WAL: logs the INSERT.
    3. Debezium connector: reads WAL change → transforms to Kafka message.
    4. Publishes to Kafka topic (e.g., "Order" topic, key=aggregate_id).
    5. No DB polling. Pure WAL streaming.

  ADVANTAGE: Outbox events published even if relay was down.
  Debezium resumes from WAL position (stored in Kafka offsets).
  No events missed during downtime (unlike polling relay which might miss events if DB cleaned up).

ORDERING GUARANTEE:

  Events for the same aggregate MUST be ordered.
  Example: OrderPlaced → OrderShipped (must be consumed in this order).

  Kafka: ordered within a partition. Key → partition (consistent hashing).
  Outbox relay: publish with key = aggregate_id.
  OrderService: all events for "Order-abc-123" → same partition.
  Consumer: processes events in order within partition.

  CROSS-AGGREGATE ORDERING: not guaranteed (different aggregates → different partitions).
  Design: events that must be ordered should come from the same aggregate.

SPRING MODULITH OUTBOX:

  Spring Modulith: provides built-in outbox implementation.

  @ApplicationModuleListener
  public class OrderEventHandler {
      // Spring Modulith: stores this event in outbox automatically.
      // Published to ApplicationEventPublisher → stored in DB → relayed to broker.
  }

  // In service:
  @Transactional
  public Order createOrder(OrderRequest req) {
      Order order = orderRepo.save(Order.create(req));
      // ApplicationEventPublisher: Spring Modulith intercepts and stores in outbox.
      eventPublisher.publishEvent(new OrderCreatedEvent(order.getId()));
      return order;
  }
  // Developer: no manual outbox table management. Spring Modulith handles it.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT outbox pattern:

- Dual-write: DB commit succeeds, Kafka publish fails → silent inconsistency
- No retry on message publish failure (message lost)
- System discovers inconsistency only when downstream service reports missing order

WITH outbox pattern:
→ Atomic: DB state change + event publishing in same local transaction
→ At-least-once guaranteed: relay retries until broker acknowledges
→ Audit: outbox table shows all events ever published

---

### 🧠 Mental Model / Analogy

> Email drafts with send retry: you write the email → it goes to Drafts (outbox table, same local save). Background process: sends it to the mail server (relay publishes to Kafka). If mail server is unreachable: retry every 30 seconds. Email stays in Drafts until confirmed sent. You can't "unsave" the draft without also cancelling the send. The draft and the send are coupled — either both happen or neither.

"Email draft" = outbox table row (in same DB transaction as business data)
"Background send process" = relay (polling or Debezium)
"Mail server" = Kafka broker
"Retry until confirmed sent" = relay retries until Kafka acknowledges

---

### ⚙️ How It Works (Mechanism)

```
TRANSACTION BOUNDARY:

  ┌─────────────────────────────────────┐
  │ DB TRANSACTION (atomic)             │
  │  INSERT INTO orders (...)          │
  │  INSERT INTO outbox (event_type,..) │
  └─────────────────────────────────────┘
           │
           ▼ (outside transaction)
  Relay reads outbox → publishes to Kafka → marks as published
```

---

### 🔄 How It Connects (Mini-Map)

```
Dual-Write Problem (inconsistency between DB and message broker)
        │
        ▼ (outbox pattern solves this)
Outbox Pattern ◄──── (you are here)
(atomic: DB write + outbox row; relay publishes asynchronously)
        │
        ├── CDC (Change Data Capture): Debezium reads WAL for outbox relay
        ├── Idempotency: consumers must be idempotent (at-least-once delivery)
        └── Saga Pattern: choreography sagas use outbox for reliable event publishing
```

---

### 💻 Code Example

```java
// Spring Boot outbox with Debezium CDC:

// 1. Domain service — writes order + outbox in single transaction:
@Service
@Transactional
public class OrderService {

    public Order placeOrder(PlaceOrderRequest request) {
        // Business write.
        Order order = orderRepository.save(Order.from(request));

        // Outbox write — same transaction.
        outboxRepository.save(OutboxEvent.builder()
            .id(UUID.randomUUID())
            .eventType("OrderPlaced")
            .aggregateType("Order")
            .aggregateId(order.getId())
            .payload(objectMapper.writeValueAsString(new OrderPlacedEvent(
                order.getId(), request.getUserId(), order.getTotal())))
            .build());

        return order; // Transaction commits: both rows written atomically.
    }
}

// 2. Outbox entity:
@Entity
@Table(name = "outbox")
public class OutboxEvent {
    @Id UUID id;
    String eventType;
    String aggregateType;
    String aggregateId;
    @Column(columnDefinition = "jsonb") String payload;
    Instant createdAt = Instant.now();
    // No 'published' column needed when using Debezium (delete row after CDC reads it).
}

// 3. Kafka consumer — idempotent processing:
@KafkaListener(topics = "Order")
public void consume(ConsumerRecord<String, String> record) {
    String eventId = record.headers().lastHeader("id").toString(); // Debezium sets event ID.

    // Idempotency check: already processed?
    if (processedEventRepository.existsById(eventId)) {
        log.debug("Skipping duplicate event: {}", eventId);
        return;
    }

    inventoryService.reserve(parseOrderPlaced(record.value()));
    processedEventRepository.save(new ProcessedEvent(eventId, Instant.now()));
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Outbox pattern guarantees exactly-once delivery    | Outbox guarantees AT-LEAST-ONCE delivery. The relay may publish an event multiple times (on retry after relay crash, after Kafka broker failure/retry). Consumers MUST be idempotent. Exactly-once delivery requires Kafka's transactional producer + idempotent consumer together — significantly higher complexity                                                                      |
| The outbox table must be cleaned up manually       | Cleanup is important but can be automated. Polling relay: mark published=true, scheduled job deletes published events older than retention period (e.g., 7 days). Debezium: after CDC reads the row, you can DELETE the row (Debezium captures INSERT, not the subsequent DELETE). Spring Modulith: handles cleanup automatically. Infinite outbox growth: will slow down polling queries |
| CDC (Debezium) is always better than polling relay | Debezium: lower latency, lower DB load, no polling overhead. But: operational complexity (Kafka Connect cluster, Debezium connector management, WAL slot management). Polling relay: simple (one scheduled job), no extra infrastructure. For low-event-volume services: polling relay is perfectly adequate. Debezium: justified at high event volume or strict low-latency requirements |

---

### 🔥 Pitfalls in Production

**Outbox table grows unboundedly — slowing the relay query:**

```
SCENARIO: New service deployed. Outbox table cleaned up manually.
  After 6 months: outbox table = 50 million published rows (cleanup job accidentally disabled).
  Polling relay query: "SELECT * FROM outbox WHERE published=FALSE ORDER BY created_at"
  Even with index: query scans 50M rows. Relay latency: 10+ seconds.
  Event processing: effectively stopped.

BAD: No cleanup scheduled:
  @Scheduled(fixedDelay = 100)
  public void pollAndPublish() {
      // Publishes events but NEVER deletes them.
      // outbox grows forever.
  }

FIX 1: Scheduled cleanup job:
  @Scheduled(cron = "0 */1 * * * *") // Every minute
  @Transactional
  public void cleanupPublishedOutboxEvents() {
      int deleted = outboxRepo.deleteByPublishedTrueAndCreatedAtBefore(
          Instant.now().minus(Duration.ofHours(24)));
      if (deleted > 0) {
          log.info("Cleaned up {} published outbox events", deleted);
      }
  }

FIX 2: Index on (published, created_at) — partial index for unpublished:
  CREATE INDEX CONCURRENTLY idx_outbox_unpublished
    ON outbox (created_at) WHERE published = FALSE;
  -- Query only scans unpublished rows (not 50M total).

FIX 3: Separate outbox table per aggregate type:
  outbox_orders, outbox_payments, outbox_inventory
  Smaller per-table row count. Cleanup per table. Queries faster.

FIX 4: Debezium — no cleanup needed at application level:
  Debezium reads WAL: publish row → immediately DELETE the row.
  Outbox table stays near-empty (only uncommitted or just-committed events).
  No growth, no cleanup concern.
```

---

### 🔗 Related Keywords

- `Saga Pattern` — sagas use outbox for reliable event publishing in choreography-based coordination
- `Idempotency` — outbox delivers at-least-once; consumers must be idempotent
- `CDC (Change Data Capture)` — Debezium uses WAL to implement the outbox relay
- `Event-Driven Architecture` — outbox is the reliability layer for event publishing
- `Dual-Write Problem` — the specific problem that outbox pattern solves

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Write DB + outbox row in ONE transaction.│
│              │ Relay publishes outbox row to broker.    │
│              │ At-least-once guaranteed. No dual-write. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service writes to DB AND publishes to    │
│              │ message broker; reliability required;    │
│              │ dual-write inconsistency unacceptable    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Service only publishes events (no DB     │
│              │ write); message loss is acceptable;      │
│              │ using Kafka transactions directly        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Email Drafts + retry: write first,     │
│              │  send when possible, never lose it."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CDC → Debezium → Idempotency →           │
│              │ Saga Pattern → Spring Modulith            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You use Debezium CDC to implement the outbox relay. Your PostgreSQL server is at 95% disk capacity. The DBA warns: "WAL segments are accumulating because Debezium's replication slot is lagging." What is happening? Why does a lagging Debezium connector cause WAL accumulation? What are the risks if this continues? How do you fix it?

**Q2.** The outbox relay publishes an event to Kafka successfully, then crashes before marking the outbox row as `published=true`. On restart: the relay republishes the same event. The downstream consumer (InventoryService) receives the event twice and reserves inventory twice. Design the complete idempotency mechanism in InventoryService to handle this scenario without double-reserving inventory.
