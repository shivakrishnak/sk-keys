---
id: MSV-054
title: Outbox Pattern
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-051, MSV-048, MSV-053
used_by: MSV-051, MSV-048, MSV-053
related: MSV-051, MSV-048, MSV-053, MSV-055, MSV-046, MSV-058
tags:
  - microservices
  - pattern
  - deep-dive
  - reliability
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/microservices/outbox-pattern/
---

⚡ TL;DR - The Outbox Pattern solves the dual-write
problem: you need to write to your database AND
publish to Kafka atomically. Without Outbox: write
DB succeeds, Kafka publish fails = silent data
loss (other services never get the event). With
Outbox: write to DB AND an outbox table in the
SAME local transaction. A separate poller/relay
reads the outbox and publishes to Kafka. If publish
fails: retry from outbox. Atomicity guaranteed by
local DB transaction. Event delivery: at-least-once
(consumer must be idempotent).

| #054 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event Sourcing in Microservices, Event-Driven Microservices, Database per Service | |
| **Used by:** | Event Sourcing in Microservices, Event-Driven Microservices, Database per Service | |
| **Related:** | Event Sourcing in Microservices, Event-Driven Microservices, Database per Service, Change Data Capture, Saga Pattern, Idempotency in Microservices | |

---

### 🔥 The Problem This Solves

**THE DUAL-WRITE PROBLEM:**
Service creates an order and MUST publish an
`OrderCreated` event so downstream services process
it. Naive implementation: write to DB, then send
to Kafka. Problem: what if Kafka is down after the
DB write? Order created in DB; no event sent; other
services (notification, inventory, loyalty) never
process the order. Silent data loss. Alternatively:
send to Kafka first, then write to DB. Kafka succeeds,
then DB fails: event published, no order in DB.
Consistency violation. There is no way to make
two separate systems atomic without a distributed
transaction - and Kafka doesn't support XA.

---

### 📘 Textbook Definition

**Outbox Pattern** is a microservices messaging
pattern that guarantees at-least-once event delivery
by storing outgoing messages in a dedicated outbox
table in the service's own database (same local
transaction as the business write). A separate
Message Relay process reads from the outbox table
and publishes messages to the message broker (Kafka,
RabbitMQ). If broker is unavailable: relay retries
until successful. Once published: mark as processed
or delete from outbox. The key invariant: the business
write and the outbox write are ONE local transaction;
either both succeed or both fail. The relay
asynchronously ensures eventual delivery to the broker.
Related: Transactional Outbox (exact synonym).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Outbox Pattern: write event to local DB table
(same transaction as business write). Relay picks
up and publishes to Kafka. Atomicity via local
transaction; eventual Kafka delivery.

**One analogy:**
> You write a letter (event) and put it in the
> outbox tray on your desk (outbox table) at the
> same time you update your records (DB write).
> Both happen together: you either do both or
> neither. A mail clerk (relay) picks up letters
> from your outbox and takes them to the post office
> (Kafka). If the post office is temporarily closed:
> the clerk retries. The letter stays in your outbox
> tray until the clerk confirms it was posted.
> You never directly go to the post office (no
> direct Kafka publish from business code).

**One insight:**
The Outbox Pattern transforms a distributed atomicity
problem into a local transaction problem. Local
transactions (DB ACID) are reliable. The broker
publish moves from "part of the business transaction"
to "an eventually-reliable background task".
This shift is fundamental: you trade synchronous
Kafka delivery for guaranteed eventual delivery.
The consumer must handle at-least-once delivery
(idempotency), but the event will ALWAYS be delivered
eventually.

---

### 🔩 First Principles Explanation

**DUAL-WRITE FAILURE SCENARIOS:**

```
WITHOUT OUTBOX - RACE CONDITIONS:

Scenario 1: DB success, Kafka failure
  T=0: orderRepo.save(order) -> SUCCESS
  T=1: kafkaTemplate.send(...) -> TIMEOUT
  Result: order in DB, no event in Kafka
  Other services: never process this order
  Silent data inconsistency

Scenario 2: Kafka success, DB failure  
  T=0: kafkaTemplate.send(event) -> SUCCESS
  T=1: orderRepo.save(order) -> DB ERROR
  Result: event in Kafka, no order in DB
  Consumers: process event for non-existent order
  Cascading errors (NullPointerException, 404s)

Scenario 3: JVM crash between DB write and Kafka send
  T=0: orderRepo.save(order) -> SUCCESS
  T=1: JVM crashes (OOM, power failure)
  Result: order in DB, Kafka message never sent
  Indeterminate: may recover but may not

WITH OUTBOX PATTERN:
  T=0: BEGIN TRANSACTION
  T=1: orderRepo.save(order) -> order in orders table
  T=2: outboxRepo.save(event) -> event in outbox table
  T=3: COMMIT TRANSACTION  <- atomic; both or neither
  T=4: Relay reads outbox, sends to Kafka
  T=5: Relay marks outbox row as SENT (or deletes)
  
  Kafka failure at T=4:
    Relay retries until Kafka available
    Outbox row: remains (not deleted)
    Event: eventually delivered
  
  JVM crash between T=3 and T=5:
    On restart: relay reads unprocessed outbox rows
    Republishes events (at-least-once: may duplicate)
    Consumer: must be idempotent
```

**OUTBOX TABLE SCHEMA:**

```sql
CREATE TABLE outbox_events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  aggregate_type VARCHAR(100) NOT NULL,  -- 'Order'
  aggregate_id   VARCHAR(100) NOT NULL,  -- orderId
  event_type     VARCHAR(100) NOT NULL,  -- 'OrderCreated'
  payload        JSONB NOT NULL,         -- event data
  status         VARCHAR(20) DEFAULT 'PENDING',
                                         -- PENDING, SENT
  created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
  processed_at   TIMESTAMP,
  kafka_topic    VARCHAR(200) NOT NULL
);

CREATE INDEX idx_outbox_status
  ON outbox_events (status, created_at)
  WHERE status = 'PENDING';
-- Relay query: SELECT * FROM outbox_events
-- WHERE status='PENDING' ORDER BY created_at LIMIT 100
```

---

### 🧪 Thought Experiment

**ORDERING GUARANTEE WITH OUTBOX:**

```
CHALLENGE:
  Two concurrent orders placed at same time:
  Order A (created_at: 10:00:00.001)
  Order B (created_at: 10:00:00.002)
  
  Both insert into outbox. Relay processes:
  in what order? By created_at ascending.
  Order A published first -> correct ordering
  
  What if relay runs two concurrent threads?
  Thread 1: picks Order A (id=1)
  Thread 2: picks Order B (id=2) simultaneously
  Thread 2 finishes first (faster Kafka ack)
  Order B published before Order A
  
  If consumer cares about order (same customer,
  same partition): Order B may arrive first
  
SOLUTION:
  Relay: single-threaded (simple, no ordering issues)
  Or: relay uses SKIP LOCKED for concurrent processing
      but partitions by aggregate_id (same order's
      events processed sequentially)
  Or: rely on Kafka partition key (orderId):
      events for same orderId go to same partition
      -> ordered within one order (key insight:
      global ordering not needed; per-order ordering
      is sufficient for most use cases)
```

---

### 🧠 Mental Model / Analogy

> The Outbox Pattern is like the "save draft" feature
> in email. When you compose an email: it auto-saves
> to Drafts (outbox table) - same atomic write as
> your edits. When you click Send: the email client
> attempts to send (relay publishes to Kafka).
> If your internet is down: the draft stays in Drafts;
> the client retries on reconnect (relay retry).
> Once sent: moved to Sent folder (status=SENT or
> deleted from outbox). You cannot "lose" the email
> because it was in Drafts before you attempted
> to send. The Outbox Pattern gives the same
> guarantee to microservice events.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When saving data AND sending a notification to other
services: save both at once (same transaction).
A background process delivers the notification later.
This guarantees the notification is never lost.

**Level 2 - How to use it (junior developer):**
In your `@Transactional` service method: call
`outboxRepo.save(event)` in addition to your
business data save. Both are part of the same
transaction. Spring Boot + Debezium: CDC reads the
outbox table changes and publishes to Kafka automatically.
Or: simple polling relay (background thread every
100ms).

**Level 3 - How it works (mid-level engineer):**
Two implementation options: (1) Polling relay:
batch SELECT PENDING outbox rows, publish to Kafka,
mark SENT. Simple but may add 100ms latency
(poll interval). (2) CDC (Change Data Capture) with
Debezium: captures outbox table INSERT events
from PostgreSQL WAL (Write-Ahead Log) in real-time
(<10ms latency). More complex setup but lower
latency and no DB poll load.

**Level 4 - Why it was designed this way (senior):**
The Outbox Pattern is an application of the
"Local Transaction" principle from distributed
systems: prefer local ACID operations over distributed
transactions. XA/2PC transactions across DB + Kafka
exist but are: rare (Kafka doesn't support XA),
slow (blocking protocol), and fragile. Outbox:
no distributed transaction, uses only local DB
transactions (reliable), with asynchronous relay
(fault-tolerant). Trade-off: at-least-once delivery
(require idempotent consumers). Exactly-once: not
achievable at the application level without
distributed transaction support.

**Level 5 - Mastery (principal/distinguished):**
Outbox at scale: the outbox table becomes a hot table.
High-throughput services (10K events/sec): outbox
table receives 10K inserts/sec + 10K deletes/sec =
20K rows/sec. PostgreSQL VACUUM load: significant.
Mitigation: (1) partition outbox table by date;
(2) soft-delete + batch purge off-peak;
(3) CDC with Debezium: reads from WAL, not polling;
no SELECT load on outbox table; (4) EventStoreDB:
the event store IS the outbox (events are published
from the event store directly). Debezium + Kafka
Outbox Event Router is the production-grade pattern
for high-throughput systems.

---

### ⚙️ How It Works (Mechanism)

```java
// OPTION A: Polling Relay

// Step 1: Business service writes to DB + outbox
// (single transaction)
@Service
public class OrderService {

    @Transactional  // Both saves in ONE transaction
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.from(req));

        OrderCreatedEvent event = OrderCreatedEvent
            .from(order);

        // Write to outbox (same transaction as order)
        outboxRepo.save(OutboxEvent.builder()
            .aggregateType("Order")
            .aggregateId(order.getId().toString())
            .eventType("OrderCreated")
            .payload(objectMapper.writeValueAsString(event))
            .kafkaTopic("order-events")
            .status(OutboxStatus.PENDING)
            .build());

        return order;
        // If transaction rolls back: both order AND
        // outbox row are not saved. No orphaned event.
    }
}

// Step 2: Relay publishes outbox events to Kafka
@Component
@Slf4j
public class OutboxEventRelay {

    @Scheduled(fixedDelay = 100)  // Every 100ms
    @Transactional
    public void publishPendingEvents() {
        List<OutboxEvent> pending = outboxRepo
            .findPendingOrderByCreatedAt(100);

        for (OutboxEvent event : pending) {
            try {
                kafkaTemplate.send(
                    event.getKafkaTopic(),
                    event.getAggregateId(),  // partition key
                    event.getPayload())
                    .get(5, SECONDS);  // Wait for ack

                event.setStatus(OutboxStatus.SENT);
                event.setProcessedAt(Instant.now());
                outboxRepo.save(event);

            } catch (Exception e) {
                log.error("Failed to publish outbox event: {}",
                    event.getId(), e);
                // Don't mark as SENT: will retry next cycle
                // After N retries: mark as FAILED for DLQ
                if (event.getRetryCount() >= 10) {
                    event.setStatus(OutboxStatus.FAILED);
                    outboxRepo.save(event);
                    // Alert: manual intervention needed
                }
            }
        }
    }
}
```

```yaml
# OPTION B: CDC with Debezium (preferred for production)
# Debezium captures outbox table changes from
# PostgreSQL WAL and publishes to Kafka directly
# No polling; latency < 10ms

# Debezium connector configuration:
name: orders-outbox-connector
config:
  connector.class: io.debezium.connector.postgresql.PostgresConnector
  database.hostname: orders-db
  database.port: 5432
  database.user: debezium
  database.password: ${DEBEZIUM_PASSWORD}
  database.dbname: orders
  table.include.list: orders.outbox_events
  transforms: outbox
  transforms.outbox.type: io.debezium.transforms.outbox.EventRouter
  transforms.outbox.table.field.event.id: id
  transforms.outbox.table.field.event.key: aggregate_id
  transforms.outbox.table.field.event.payload: payload
  transforms.outbox.route.by.field: kafka_topic
  # Debezium reads PostgreSQL WAL (commit log)
  # Captures INSERT into outbox_events
  # Routes to correct Kafka topic
  # No polling; no SELECT load on DB
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
OUTBOX PATTERN FLOW (with Debezium CDC):

  order-service creates order:
  BEGIN TRANSACTION
    INSERT INTO orders (id, customer_id, ...) VALUES (...)
    INSERT INTO outbox_events (event_type='OrderCreated',
                               payload='{...}') 
  COMMIT
  
  PostgreSQL WAL records the transaction
  
  Debezium: monitors WAL continuously
    Detects: INSERT into outbox_events
    Reads: event_type, payload, kafka_topic
    Publishes: to order-events Kafka topic
    Latency: < 10ms from COMMIT to Kafka publish
  
  Consumers: notification-service, loyalty-service
    Receive: OrderCreated event
    Process: independently at own pace
  
  Failure scenarios:
    Kafka down: Debezium retries (WAL not discarded)
    order-service crash after COMMIT: Debezium
      reads WAL on recovery; publishes event
    Network partition: event buffered; delivered
      on recovery
  Guarantee: event ALWAYS delivered (at-least-once)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: dual write without Outbox**

```java
// BAD: dual write - not atomic
@Service
public class OrderService {
    @Transactional
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.from(req));
        // OUTSIDE the transaction scope!
        // If this fails: order in DB, no Kafka event
        kafkaTemplate.send("order-events",
            new OrderCreatedEvent(order));
        return order;
    }
}
// Risk: network glitch to Kafka = silent data loss
// Risk: Kafka broker restart = silent data loss
```

```java
// GOOD: Outbox Pattern - atomic write
@Service
public class OrderService {
    @Transactional  // BOTH writes in ONE transaction
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.from(req));
        // Outbox write: same transaction as business write
        outboxRepo.save(OutboxEvent.from(
            "OrderCreated", order.getId(), order));
        return order;
        // Relay/Debezium: publishes to Kafka async
        // If relay fails: retries; event not lost
        // Atomic guarantee: both saved or neither saved
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Atomicity | Latency | Complexity | Reliability |
|---|---|---|---|---|
| **Direct Kafka publish** | None (dual write) | Low | Low | Poor (data loss on failure) |
| **XA/2PC** | Yes | High | Very High | Medium (Kafka no XA) |
| **Outbox + Polling Relay** | Yes (local tx) | ~100ms | Medium | High |
| **Outbox + Debezium CDC** | Yes (local tx) | <10ms | High (infra) | Very High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Outbox Pattern guarantees exactly-once delivery | Outbox guarantees at-least-once delivery. If the relay publishes to Kafka but crashes before marking the outbox row as SENT: on restart it will publish again. Consumers receive duplicates. Consumers MUST be idempotent. Exactly-once requires Kafka Transactions API on the consumer side (consume-process-produce in one atomic Kafka transaction), which is separate from the Outbox Pattern. |
| The Outbox table should stay small | The outbox table grows without bound if: (1) Kafka is down for extended period, (2) relay stops processing, (3) FAILED events accumulate without a dead letter queue strategy. Monitor: `SELECT COUNT(*) FROM outbox_events WHERE status='PENDING' AND created_at < NOW() - INTERVAL '5 minutes'`. Alert if count grows. Implement max retry + FAILED status + DLQ + alert for manual investigation. |
| Using a transaction log tail (Debezium) is complex | For greenfield services: yes, Debezium adds infrastructure (Kafka Connect cluster, connector config, schema). But: Debezium eliminates polling overhead (no SELECT load on outbox table), provides sub-10ms latency, and is the recommended approach for high-throughput services (>1000 events/sec). The upfront complexity pays off at scale. |

---

### 🚨 Failure Modes & Diagnosis

**Silent event loss: orders created but downstream services not notified**

**Symptom:**
Customers reporting: no confirmation email after
ordering. Analytics shows orders in DB but no
corresponding events in Kafka. Started happening
3 days ago after a deployment.

**Root Cause:**
Deployment introduced a bug: the `@Transactional`
annotation was removed from the `createOrder` method
(refactoring mistake). Outbox write now happens
outside the transaction. On DB write success: outbox
write occasionally fails (connection pool exhaustion
during peak). Orders created; outbox events not
written; relay has nothing to publish.

**Diagnostic:**
```sql
-- Compare order count vs outbox event count
SELECT
  DATE_TRUNC('hour', created_at) AS hour,
  COUNT(*) AS order_count
FROM orders
GROUP BY hour
ORDER BY hour DESC;

-- Compare with outbox events
SELECT
  DATE_TRUNC('hour', created_at) AS hour,
  COUNT(*) AS event_count
FROM outbox_events
WHERE event_type = 'OrderCreated'
GROUP BY hour
ORDER BY hour DESC;

-- Divergence: orders > events = missing outbox writes
-- Starting 3 days ago: matches deployment time
```

**Fix:**
1. Restore `@Transactional` on `createOrder`.
2. For missing events: manually insert outbox rows
   for orders without corresponding events (data
   repair script).
3. Add integration test: verify outbox row is created
   for every business write. Test: call `createOrder()`,
   assert outbox table has 1 row, verify relay can
   process it.
4. Add monitoring: alert if
   `orders.count` significantly exceeds
   `outbox_events.count` (divergence detector).

---

### 🔗 Related Keywords

**Requires:**
- `Event-Driven Microservices` - Outbox ensures
  atomic write + event publish for event-driven systems
- `Event Sourcing in Microservices` - event store
  can act as the outbox (events published from store)
- `Database per Service` - Outbox relies on local
  DB transaction; requires service-owned database

**Related patterns:**
- `Change Data Capture (CDC)` - Debezium CDC is the
  preferred relay mechanism for Outbox Pattern
- `Saga Pattern` - Saga events use Outbox for reliable
  publication
- `Idempotency in Microservices` - required since
  Outbox provides at-least-once delivery

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PROBLEM      │ Dual write: DB + Kafka not atomic        │
│              │ Failure between writes = data loss       │
├──────────────┼──────────────────────────────────────────┤
│ SOLUTION     │ Write to outbox table in SAME transaction│
│              │ Relay publishes outbox events to Kafka   │
├──────────────┼──────────────────────────────────────────┤
│ GUARANTEE    │ At-least-once delivery (not exactly-once)│
│              │ Consumers MUST be idempotent             │
├──────────────┼──────────────────────────────────────────┤
│ RELAY OPTIONS│ Polling (simple) vs Debezium CDC (fast)  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Outbox solves dual write: write business data
   AND event in ONE local transaction. No distributed
   transaction needed.
2. Relay (polling or Debezium CDC) asynchronously
   publishes outbox events to Kafka. Retries on failure.
3. Guarantee: at-least-once (not exactly-once).
   Consumers must be idempotent.

**Interview one-liner:**
"Outbox Pattern solves the dual-write problem:
you cannot atomically write to a database AND publish
to Kafka. Solution: write to an outbox table in the
SAME local DB transaction as the business write.
A relay (polling or Debezium CDC) publishes outbox
events to Kafka asynchronously, retrying on failure.
Guarantee: at-least-once delivery (message relay
may duplicate on crash/restart). Consumers: must
be idempotent. Relay options: polling relay (simple,
~100ms latency) or Debezium CDC (complex, <10ms
latency from PostgreSQL WAL)."

---

### 💡 The Surprising Truth

The Outbox Pattern is often presented as a microservices
pattern, but it's actually the only correct way to
ensure event delivery in ANY system that writes to
both a database and a message broker. Even in a
monolith: if you write to a database and then publish
an event to RabbitMQ, you have the dual-write problem.
The pattern is universally applicable. Most engineers
discover it after experiencing their first incident:
customer support calls about orders with no email
confirmation; investigation reveals a Kafka publish
failed silently after a network blip. The Outbox
Pattern is the pattern you wish you'd implemented
from day one.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DUAL WRITE** Describe 3 specific failure scenarios
   that occur when writing to DB and Kafka without
   the Outbox Pattern. For each: the symptom, the
   root cause, and why it's hard to detect.
2. **IMPLEMENT** Implement the Outbox Pattern in
   Spring Boot: outbox table schema, service code
   with `@Transactional`, polling relay with retry
   logic and max retries, dead letter handling.
3. **DEBEZIUM** Explain how Debezium CDC replaces
   the polling relay. What is the PostgreSQL WAL?
   How does Debezium read it? What is the latency
   improvement?
4. **IDEMPOTENCY** An outbox relay crashes after
   publishing to Kafka but before marking the row
   as SENT. On restart: the event is published again.
   Implement an idempotent consumer using a processed
   events table that handles this duplicate.
5. **MONITORING** What metrics do you alert on for
   the Outbox Pattern? How do you detect growing
   unprocessed outbox events? What is your SLA for
   event delivery latency?

---

### 🧠 Think About This Before We Continue

**Q1.** You are using the Outbox Pattern. Your
outbox table has 50,000 PENDING events because Kafka
was down for 2 hours. Kafka is now back up. The
relay starts processing. Order of events in Kafka:
does it match the order they were created? What
if consumers have already timed out and retried
via other means (compensating actions)? How do you
handle duplicate processing for 50,000 events that
were "retried" manually?

**Q2.** Your service creates 10,000 orders/second
at peak. Each order inserts 2 rows into the outbox
table (OrderCreated + OrderAccepted events). The
outbox table receives 20,000 inserts/second and
20,000 deletes/second (40,000 writes/second to one
table). PostgreSQL performance at this rate: how
do you optimize? Consider: table partitioning, index
strategy, VACUUM configuration, and whether Debezium
CDC is better than polling at this scale.

**Q3.** You want to use the Outbox Pattern but your
service uses MongoDB (not PostgreSQL). MongoDB does
not support true ACID transactions across multiple
collections in all configurations. How do you
implement the Outbox Pattern in MongoDB? (Hint:
MongoDB 4.0+ multi-document transactions; or: use
a single document write with embedded outbox array).