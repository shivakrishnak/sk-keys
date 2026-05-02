---
layout: default
title: "Outbox Pattern"
parent: "Distributed Systems"
nav_order: 617
permalink: /distributed-systems/outbox-pattern/
number: "0617"
category: Distributed Systems
difficulty: ★★★
depends_on: Event Sourcing, CQRS, Idempotency (Distributed), Database Fundamentals
used_by: Saga Pattern, CQRS Projections, Microservices, Transactional Messaging
related: Event Sourcing, Saga Pattern, CQRS, Idempotency (Distributed), Change Data Capture
tags:
  - distributed
  - data-integrity
  - pattern
  - messaging
  - deep-dive
---

# 617 — Outbox Pattern

⚡ TL;DR — The Outbox Pattern solves the dual-write problem: instead of writing to a database AND publishing to a message broker in two separate operations (both can fail independently), you write to BOTH in one database transaction — a business record + an outbox record — and a separate relay process publishes from the outbox to the broker, guaranteeing atomicity.

| #617            | Category: Distributed Systems                                                      | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Event Sourcing, CQRS, Idempotency (Distributed), Database Fundamentals             |                 |
| **Used by:**    | Saga Pattern, CQRS Projections, Microservices, Transactional Messaging             |                 |
| **Related:**    | Event Sourcing, Saga Pattern, CQRS, Idempotency (Distributed), Change Data Capture |                 |

---

### 🔥 The Problem This Solves

**THE DUAL-WRITE PROBLEM:**
Order service creates an order in PostgreSQL AND publishes `OrderCreated` to Kafka. Two separate writes. Two ways this can fail:

```
Scenario A: DB write succeeds, Kafka publish fails.
  Order is in DB. Event never published. Inventory service never reserves items.
  Order stuck: visible to customer, but never processed downstream.

Scenario B: DB write fails, Kafka publish succeeds (briefly connected before crash).
  Event published. Inventory reserves items. Payment charged.
  But there's no order in the DB. Inventory reserved for a ghost order. Customer charged for nothing.
```

Neither is acceptable. The dual-write problem has no solution without the Outbox Pattern (or 2PC, which doesn't work across DB + Kafka).

---

### 📘 Textbook Definition

The **Outbox Pattern** addresses the dual-write problem — the impossibility of atomically writing to a database and publishing a message to an external broker in one operation. **Mechanism:** (1) In the same database transaction as the business write, insert the to-be-published message into an `outbox` table in the same database. (2) A separate **relay process** (outbox relay/publisher) reads from the outbox table and publishes to the message broker. (3) On successful publish, the outbox record is marked as published or deleted. **Guarantees:** the database transaction ensures atomicity of the business write + outbox write. The relay provides at-least-once delivery (network failure between publish and mark-as-published causes re-delivery). Consumers must be **idempotent** (handle duplicates). **Implementation options:** polling relay (query outbox table every N seconds), CDC (Change Data Capture — stream DB WAL changes to broker using Debezium). CDC is preferred for lower latency and less polling load.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Don't publish to a message broker directly — write to an outbox table in the same DB transaction, then let a relay process publish from there.

**One analogy:**

> Outbox Pattern is like an email system with a Drafts folder. Instead of "send email while also saving to Sent" (dual write — one can fail), you first save to Drafts (outbox table) in one step, then a background process sends from Drafts and moves to Sent (marks as published). If the send fails, it retries from Drafts. If the background process crashes after send but before moving to Sent, it resends from Drafts (at-least-once delivery) — the recipient handles duplicates.

**One insight:**
The key insight is that the outbox table is in the SAME database as the business data. This makes the write atomic — EITHER both the business record AND the outbox entry are committed, OR neither is (if the transaction fails). The semantically hard part (atomicity of business + message) is guaranteed by the database's existing transactional guarantee. The relay — which reads from outbox and publishes to broker — only needs to be eventually reliable (at-least-once retry), not transactional.

---

### 🔩 First Principles Explanation

**OUTBOX TABLE STRUCTURE:**

```sql
CREATE TABLE outbox_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type  VARCHAR(255) NOT NULL,   -- "Order", "Payment"
    aggregate_id    VARCHAR(255) NOT NULL,   -- ID of the aggregate
    event_type      VARCHAR(255) NOT NULL,   -- "OrderPlaced", "PaymentCharged"
    payload         JSONB NOT NULL,          -- event data
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at    TIMESTAMP,               -- NULL = not yet published
    retry_count     INT NOT NULL DEFAULT 0
);

-- Business transaction: both writes or neither:
BEGIN;
  INSERT INTO orders (id, customer_id, status, total)
  VALUES ('order-123', 'cust-456', 'PLACED', 150.00);

  INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload)
  VALUES ('Order', 'order-123', 'OrderPlaced',
          '{"orderId":"order-123","customerId":"cust-456","total":150.00}');
COMMIT;
-- If any part fails: ROLLBACK — no order, no outbox entry. Consistent.
```

**POLLING RELAY:**

```java
@Scheduled(fixedDelay = 100) // Poll every 100ms
@Transactional
public void publishPendingEvents() {
    List<OutboxEvent> pending = outboxRepo.findPendingEvents(
        PageRequest.of(0, 50)  // Process up to 50 at a time
    );

    for (OutboxEvent event : pending) {
        try {
            // Publish to Kafka:
            kafkaTemplate.send(event.getEventType(),
                event.getAggregateId(),
                event.getPayload());

            // Mark as published (idempotent — if this step fails, re-published next cycle):
            event.setPublishedAt(Instant.now());
            outboxRepo.save(event);

        } catch (Exception e) {
            event.setRetryCount(event.getRetryCount() + 1);
            outboxRepo.save(event);
            log.error("Failed to publish outbox event {}", event.getId(), e);
        }
    }
}
```

**CDC (CHANGE DATA CAPTURE) WITH DEBEZIUM:**

```
Debezium captures PostgreSQL WAL (Write-Ahead Log) changes in real-time.
No polling. Event fires within milliseconds of commit.

Architecture:
  1. PostgreSQL WAL: every INSERT/UPDATE/DELETE logged here (standard Postgres feature).
  2. Debezium connector: reads WAL, translates to Kafka messages.
     Monitors: public.outbox_events table.
  3. Kafka: receives CDC events for each outbox_events INSERT.
  4. Consumer: reads from Kafka topic, processes OrderPlaced etc.

  Debezium config (Kafka Connect):
  {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "table.include.list": "public.outbox_events",
    "transforms": "outbox",
    "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter"
  }

Advantages over polling:
  - Latency: <1ms vs. polling interval (100ms-1s)
  - No polling overhead on DB
  - Exactly-once semantics possible (if consumer uses Kafka offset + idempotency key)
```

**AT-LEAST-ONCE + IDEMPOTENCY:**

```
Outbox relay crash scenario:
  1. Relay publishes event to Kafka. (SUCCESS at broker)
  2. Relay crashes BEFORE marking outbox_events.published_at.
  3. Relay restarts. Re-reads unpublished outbox entry.
  4. Re-publishes to Kafka. Consumer receives DUPLICATE event.

Consumer must handle duplicates:
  // Idempotent consumer — uses Kafka offset as idempotency key:
  @KafkaListener(topics = "order-events")
  @Transactional
  public void consume(ConsumerRecord<String, OrderPlacedEvent> record) {
    String kafkaOffset = record.partition() + "-" + record.offset();

    // Check if already processed:
    if (processedOffsetRepo.exists(kafkaOffset)) {
        return; // Already processed — skip duplicate
    }

    // Process event:
    inventoryService.reserveItems(record.value());

    // Mark as processed (in same transaction as business state change):
    processedOffsetRepo.save(new ProcessedOffset(kafkaOffset));
  }
```

---

### 🧪 Thought Experiment

**WHAT IF THE OUTBOX TABLE GROWS INDEFINITELY?**

If the relay crashes and is not repaired, the outbox table accumulates unprocessed events. 100 events/second × 24 hours = 8,640,000 rows. PostgreSQL query performance degrades. Application DB is now a message queue (bad).

**Prevention:**

1. Monitor: alert if `unpublished outbox events count > 1000 for > 60 seconds`.
2. Relay SLA: relay is a critical infrastructure component; treat relay failure as P1 (same as application failure).
3. Archival: once published, delete outbox entries (or move to a cold archive table). Don't keep published events in the hot outbox table.
4. Outbox table index: `(published_at IS NULL, created_at)` — fast scan for unpublished events.

---

### 🧠 Mental Model / Analogy

> Outbox Pattern is like hand-delivering an envelope to a post office. You write the letter and seal the envelope (business write). You put it in your outbox tray (outbox table). A mail carrier (relay process) picks up from the outbox and hands it to the post office (message broker). The letter exists in the tray - you know it will be sent. If the mail carrier drops it on the way, they pick it up and re-deliver (at-least-once). The recipient's mailbox accepts duplicate deliveries and ignores duplicates with the same tracking number (idempotent consumer).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Write to DB + outbox in one transaction. A relay process publishes from outbox to broker. No more dual-write problem.

**Level 2:** Polling relay (simple but adds latency) vs. CDC with Debezium (fast, WAL-based). At-least-once delivery: relay may re-publish after crash. Consumers must be idempotent. Outbox table maintenance: archive/delete published rows.

**Level 3:** Transactional outbox in Axon/Spring frameworks (built-in). Debezium Outbox router: transforms with CDC transformation to route events to correct Kafka topics by `aggregate_type`. Partitioning: use `aggregate_id` as Kafka partition key to ensure ordering of events per aggregate. Dead letter queue (DLQ): failed publish after N retries → DLQ for manual inspection.

**Level 4:** The outbox pattern is the foundation of the "transactional messaging" guarantee necessary for microservice saga patterns. Without it, saga compensation may run for a transaction that never officially completed. With it, every forward step and every compensation is guaranteed-published or never-published. Event sourcing + outbox: the event store append (to domain events table) doubles as the outbox — domain events ARE the outbox entries. Debezium reads the events table and publishes to Kafka. Zero code for the relay. The domain event table serves double duty as persistence AND outbox. This is the cleanest implementation of event-sourced CQRS with guaranteed event publishing.

---

### ⚙️ How It Works (Mechanism)

**Spring Boot + Debezium Outbox:**

```java
@Service
@Transactional
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private OutboxRepository outboxRepository;

    public String placeOrder(PlaceOrderRequest request) {
        // Step 1: Business write
        Order order = new Order(request.getCustomerId(), request.getItems());
        order = orderRepository.save(order);

        // Step 2: Outbox write (SAME transaction)
        OrderPlacedEvent event = new OrderPlacedEvent(
            order.getId(), order.getCustomerId(), order.getTotal()
        );
        outboxRepository.save(new OutboxEntry(
            "Order",
            order.getId(),
            "OrderPlaced",
            objectMapper.writeValueAsString(event)  // serialized payload
        ));

        // Both saved or both rolled back — atomically.
        return order.getId();

        // Debezium picks up the outbox INSERT via WAL and publishes to Kafka.
        // No explicit relay code needed.
    }
}
```

---

### ⚖️ Comparison Table

| Approach                | Atomicity     | Latency          | Complexity           | Duplicates                 |
| ----------------------- | ------------- | ---------------- | -------------------- | -------------------------- |
| Dual write (no pattern) | None          | Low              | Low                  | Possible + inconsistencies |
| Outbox + polling        | Guaranteed    | polling interval | Medium               | Yes (at-least-once)        |
| Outbox + CDC (Debezium) | Guaranteed    | ~1ms             | High (Kafka Connect) | Yes (at-least-once)        |
| Two-Phase Commit        | Guaranteed    | High             | Very High            | No (exactly-once)          |
| Saga with compensation  | Semantic only | Medium           | High                 | No (business-level)        |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                    |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Outbox pattern gives exactly-once delivery          | It gives at-least-once. For exactly-once semantics: consumers must use idempotency keys or Kafka transactional producers (Kafka exactly-once adds complexity)                              |
| CDC (Debezium) eliminates the relay entirely        | CDC is the relay — it reads the WAL and writes to Kafka. It still needs to be deployed, managed, and monitored                                                                             |
| Publishing from outbox is as fast as direct publish | Outbox adds latency: polling relay (up to interval delay) or CDC relay (WAL capture latency ~1ms). For real-time systems, CDC is preferred; polling is fine for non-latency-critical flows |

---

### 🚨 Failure Modes & Diagnosis

**Relay Down — Outbox Table Overflowing**

**Symptom:** Downstream services stop receiving events. Order placed but inventory not
reserved, payment not processed. Outbox table growing at 1000 rows/minute.
Customer-visible impact: orders stuck in PENDING state.

Cause: Debezium connector crashed and was not paged. Outbox table now has 2 million
unprocessed rows.

**Fix:** (1) Restart Debezium connector. It resumes from last committed WAL position.
(2) If WAL position was lost: replay from earliest unpublished outbox row.
(3) Consumers are idempotent — duplicate events processed correctly.
(4) Prevention: alert on `outbox_events count(published_at IS NULL) > 500`.
Alert on Kafka Connect connector status via JMX/REST API.
Post-incident: add liveness check for relay as part of readiness probe.

---

### 🔗 Related Keywords

- `Event Sourcing` — domain events table serves as the outbox
- `Saga Pattern` — outbox guarantees reliable saga step event publishing
- `CQRS` — outbox ensures read model projectors receive all events without gaps
- `Idempotency (Distributed)` — required for consumers processing at-least-once delivered events
- `Change Data Capture` — Debezium uses CDC to implement the outbox relay from WAL

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  OUTBOX: solve dual-write (DB write + broker publish)    │
│  Write: business record + outbox entry in ONE tx        │
│  Relay: separate process reads outbox → publishes        │
│  Polling relay: simple, adds latency (100ms-1s)          │
│  CDC relay: Debezium reads WAL → ~1ms latency            │
│  Delivery: at-least-once → consumers must be idempotent  │
│  Monitor: alert if unpublished count grows unbounded     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An order service uses outbox pattern with polling relay (interval=500ms). The business requirement says "inventory must be reserved within 2 seconds of order placement." Calculate the worst-case end-to-end latency from order INSERT to inventory update, accounting for: outbox polling interval, Kafka producer batch delay (100ms), consumer poll interval (100ms), and inventory service processing time (50ms). Does the system meet the 2-second SLA? What change would you make if it doesn't?

**Q2.** During a high-throughput sale event, 10,000 orders are placed per second. The polling relay processes 50 outbox entries per poll cycle at 100ms intervals. How many outbox entries accumulate per second (backlog growth rate)? After 60 seconds of this load, what is the backlog size? How would you scale the relay to handle this load? What is the risk of running multiple relay instances simultaneously?
