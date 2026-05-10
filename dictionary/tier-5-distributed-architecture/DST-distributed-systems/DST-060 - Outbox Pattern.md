---
id: DST-066
title: "Outbox Pattern"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-062, DST-061, DST-029
related: DST-062, DST-056, DST-061
tags:
  - distributed
  - architecture
  - pattern
  - deep-dive
  - advanced
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 60
permalink: /distributed-systems/outbox-pattern/
---

# DST-063 - Outbox Pattern

⚡ TL;DR - The Outbox Pattern solves the dual-write problem by writing both the business state change and the outgoing event/message to the same database in one transaction, then reliably delivering the event to the message broker via a separate process — guaranteeing at-least-once delivery without distributed transactions.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-062, DST-061, DST-029 |     |
| **Related:**    | DST-062, DST-056, DST-061 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Service A processes a payment command: (1) UPDATE database: set order.status = PAID. (2) Publish "OrderPaid" event to Kafka. These are two separate systems. What happens if step (1) succeeds and step (2) fails (Kafka is down, network timeout, service crashes between steps 1 and 2)? The database says the order is PAID. Kafka never received the event. The downstream services (fulfillment, notification, accounting) never know the order was paid. The system is permanently inconsistent — the order will never be fulfilled, the customer never notified, but they were charged.

**THE BREAKING POINT:**
The dual-write problem: updating two independent systems atomically requires a distributed transaction (2PC). But distributed transactions sacrifice availability (both systems must be up and participating) and performance (blocking coordination protocol). Most modern systems avoid 2PC. But without atomicity: either the database update succeeds without the event being published (data consistency without event propagation), or the event is published without the database update succeeding (events for non-existent state changes). Both are bugs.

**THE INVENTION MOMENT:**
The Outbox Pattern (named in the context of microservices around 2015-2017) applies the same principle as email outboxes: before you send an email, you save it to your "Outbox" folder (within the same mail client transaction). A background process then sends emails from the Outbox. If the mail client crashes: the email is still in the Outbox and will be sent on restart. The key insight: use the same transactional boundary as the business operation to record the intent to publish, then deliver reliably out-of-band.

**EVOLUTION:**
2000s: Enterprise messaging patterns (Hohpe & Woolf) — reliable messaging patterns. 2015+: Microservices popularize the dual-write problem. 2017: "Outbox Pattern" named explicitly in microservices context. 2018: Debezium (Red Hat) — CDC-based outbox relay becomes mainstream. 2020+: Debezium Outbox Event Router — official CDC outbox implementation. 2022+: Polling publisher as alternative to CDC for simpler infrastructure. Today: Outbox Pattern + CDC (Change Data Capture) via Debezium is the standard approach for reliable event publishing in microservices.

---

### 📘 Textbook Definition

The **Outbox Pattern** (also: Transactional Outbox) is a microservices messaging pattern that ensures reliable event publication by: (1) Within the same database transaction as the business operation: writing the business state change AND writing the outgoing event to an `outbox` table. (2) A separate relay process (polling publisher or CDC-based) reads new rows from the `outbox` table and publishes them to the message broker (Kafka, RabbitMQ). (3) On successful broker acknowledgment: marks the outbox row as published (or deletes it). **Guarantees:** At-least-once delivery (the relay retries until the broker acknowledges). Exactly-once delivery requires idempotent consumers (DST-029). **Relay implementations:** (a) Polling publisher: periodically queries `outbox` for unpublished events. Simple but adds latency. (b) CDC (Change Data Capture): streams database transaction log (Postgres WAL, MySQL binlog) — Debezium captures outbox table inserts in near-real-time. Lower latency, no polling overhead.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Write the event to your own database first (same transaction as your business update), then deliver it reliably to the broker separately.

> The Outbox Pattern is like a mail room in a building. When a department (service) needs to send a letter (event), they don't mail it directly — they deliver it to the building's mail room (outbox table) as part of their normal workflow (same transaction). The mail room (relay process) is responsible for sending letters to the post office (Kafka). If the mail room clerk is sick for a day: letters pile up but aren't lost. When the clerk returns: all letters are sent. The department's workflow never fails because of post office issues.

**One insight:** The outbox table is a "buffer" inside your own system's trust boundary. Writing to your own database is a LOCAL operation (part of your transaction). Publishing to Kafka is a REMOTE operation (outside your transaction). By making the remote operation asynchronous (relay sends it later), you eliminate the dependency on the remote system's availability from your critical transaction path.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Business state change and outbox entry are atomically written.** `BEGIN TRANSACTION; UPDATE orders SET status='PAID'; INSERT INTO outbox (payload, topic, status) VALUES (..., 'PENDING'); COMMIT;`. If the transaction commits: both the state change and the outbox entry exist. If it rolls back: neither exists. No dual-write inconsistency possible within the same database.
2. **Relay provides at-least-once delivery.** The relay reads `outbox` rows with `status='PENDING'` and publishes to Kafka. If Kafka ACK is received: mark row as `DONE` (or delete). If Kafka is down: row remains `PENDING`, relay retries. If the relay crashes AFTER Kafka ACK but BEFORE marking DONE: the row is retried → duplicate message published to Kafka. This is at-least-once. Consumers must be idempotent (DST-029).
3. **Ordering within an aggregate is preserved.** Events for the same order must be published in the order they were written. Outbox table: `sequenceNumber` per aggregate. Relay publishes events ordered by `sequenceNumber`. Kafka partition key = aggregateId → events for the same aggregate go to the same partition in order.
4. **Relay is idempotent.** Relay may process the same outbox row multiple times (crash-recovery). Must not publish duplicate events from the same row (use unique messageId per outbox row; Kafka idempotent producer deduplicates by messageId within a session).

**DERIVED DESIGN:**

```
Service transaction:
  BEGIN TX
    UPDATE orders SET status='PAID' WHERE id=123
    INSERT INTO outbox (
      aggregateId='123', aggregateType='Order',
      eventType='OrderPaid', payload={...},
      status='PENDING', sequenceNo=5
    )
  COMMIT TX

Relay (CDC-based, Debezium):
  reads Postgres WAL → detects INSERT on outbox
  publishes to Kafka topic 'order-events'
    key=aggregateId, value=payload
  → Kafka ACK
  UPDATE outbox SET status='DONE' WHERE id=row.id
```

**THE TRADE-OFFS:**
**Gain:** Reliable event publishing without distributed transactions. No dependency on message broker availability in the critical transaction path. At-least-once delivery guaranteed.
**Cost:** Additional `outbox` table per service. Relay process to deploy and maintain (CDC adds complexity). At-least-once → idempotent consumers required. Slightly increased write latency (outbox insert in transaction). CDC requires database WAL access (not always available in managed DBaaS).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** At-least-once vs exactly-once is an irreducible trade-off. Exactly-once delivery across a distributed boundary requires either 2PC (available) or idempotent consumers (at-least-once + dedup). There is no way to eliminate this complexity.
**Accidental:** Debezium configuration complexity. Outbox table schema decisions. Kafka producer idempotency configuration. These are implementation details.

---

### 🧪 Thought Experiment

**SETUP:** Payment service processes 1,000 payments/minute. For each payment: update DB + publish Kafka event. Kafka has 0.1% unavailability (5.26 hours/year). Without Outbox Pattern: how many payments are processed but events lost?

**WITHOUT OUTBOX PATTERN (dual-write):**

```
For each payment:
  UPDATE orders SET paid=true;  [DB TX]
  publish to Kafka;             [if Kafka is down → LOST]
```

- 1,000 payments/min × 0.1% Kafka unavailability = 1 payment/min lost during downtime.
- 5.26 hours of downtime/year × 60 min/hr = 315 minutes × 1 lost event/min = 315 lost payment events/year.
- 315 payments processed but never fulfilled. 315 angry customers.

**WITH OUTBOX PATTERN:**

```
For each payment:
  BEGIN TX
    UPDATE orders SET paid=true;
    INSERT INTO outbox (payload, status='PENDING');
  COMMIT
  [Relay sends to Kafka — if Kafka is down,
   relay retries until Kafka comes back]
```

- Kafka unavailability: relay retries. When Kafka comes back: all pending outbox rows are published.
- 0 lost payment events.
- Slightly delayed delivery during Kafka outage — but no data loss.

**THE INSIGHT:** The Outbox Pattern converts Kafka availability into a latency concern (events may be delayed during Kafka downtime) rather than a data loss concern (events permanently lost). The trade-off: delayed delivery is acceptable; silent data loss is not.

---

### 🧠 Mental Model / Analogy

> The Outbox Pattern is like a store's accounting system. When a sale is made (business state change): the cashier records it in the sales ledger AND places a copy in the "Accounts Receivable" outbox tray — both in one step (before closing the register drawer). At end of day: the accounting clerk picks up all items from the outbox tray and sends invoices (publishes events). If the clerk is sick: items pile up in the tray (relay backlog). When the clerk returns: all invoices are sent — no sales are lost. The sales ledger (database) and the outbox tray (outbox table) are updated together (same transaction) — atomically.

**Mapping:**

- **Sales ledger** → business database (orders table)
- **Outbox tray** → outbox table
- **Recording sale + placing copy in tray** → atomic transaction (business update + outbox insert)
- **Accounting clerk sending invoices** → relay process (Debezium CDC or polling publisher)
- **Post office (external)** → Kafka (message broker)
- **Invoice copy in tray** → outbox row with `status='PENDING'`

Where this analogy breaks down: the mail clerk sends each invoice once (exactly-once). The relay process provides at-least-once delivery — if the clerk posts an invoice but forgets to remove it from the tray: it would be sent twice. Downstream services (invoice recipients) must handle duplicate invoices gracefully (idempotent processing).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you need to update your database AND send a message at the same time, one of them might fail. The Outbox Pattern says: write a "to-do note" to send the message in your own database (at the same time as your database update — as one operation). A background helper reads your to-do notes and sends the messages. If the message service is down: notes pile up, no messages are lost. When it comes back: all messages are sent.

**Level 2 - How to use it (junior developer):**
Spring Boot + Postgres + Debezium:

```java
@Transactional
public void processPayment(PaymentRequest req) {
    // Step 1: business update
    Order order = orderRepo.findById(req.orderId());
    order.markPaid(req.amount());
    orderRepo.save(order);

    // Step 2: write to outbox (SAME TRANSACTION)
    OutboxEvent event = OutboxEvent.builder()
        .aggregateId(order.getId())
        .aggregateType("Order")
        .eventType("OrderPaid")
        .payload(objectMapper.writeValueAsString(
            new OrderPaidEvent(order)))
        .status("PENDING")
        .build();
    outboxRepo.save(event);
    // Both saved atomically — if payment fails, outbox row
    // is also rolled back. No inconsistency.
}
// Debezium reads WAL, detects outbox INSERT, publishes to Kafka
```

**Level 3 - How it works (mid-level engineer):**
**CDC-based relay (Debezium):** Debezium connects to Postgres as a replication slot consumer. It reads the Write-Ahead Log (WAL) — a record of every committed database change. When Debezium sees a new row INSERT in the `outbox` table: it reads the `topic`, `key`, and `payload` columns and publishes to the corresponding Kafka topic. The Debezium "Outbox Event Router" is a Kafka Connect SMT (Single Message Transform) that knows the outbox table schema and routes events to the correct topic based on `aggregateType`/`eventType` columns. **Polling-based relay:** simpler but less efficient. A scheduled job: `SELECT * FROM outbox WHERE status='PENDING' ORDER BY createdAt LIMIT 100`. Publishes each to Kafka. On ACK: `UPDATE outbox SET status='DONE'`. Polling adds latency (up to polling interval). Retries on partial failures. For lower volume or simpler infrastructure: polling is sufficient.

**Level 4 - Why it was designed this way (senior/staff):**
The Outbox Pattern's architecture is a direct consequence of the CAP theorem and the distributed systems impossibility result: you cannot atomically update two independent systems (database + Kafka) without coordination. 2PC provides coordination but sacrifices availability (both systems must be up and participating). The Outbox Pattern eliminates the need for coordination by reducing the problem to a single-system operation: the database transaction is the only critical-path operation. Kafka publishing is deferred to a background process that can retry indefinitely. This is a classic systems design move: convert a synchronous dependency (Kafka must be up for the business operation to complete) into an asynchronous dependency (Kafka can be down; retry when available). The pattern works because the database is already in the service's trust boundary — writing to it is a local, reliable operation. The message broker is an external dependency — publishing to it is an unreliable remote operation. By making the remote operation asynchronous, you decouple the business operation's reliability from the broker's availability.

**Expert Thinking Cues:**

- "Outbox relay is falling behind — growing backlog in outbox table" → Relay throughput too low. Check: Debezium lag (`kafka-consumer-groups.sh` for Debezium connector consumer group). Kafka producer throughput limit. Database: `SELECT COUNT(*) FROM outbox WHERE status='PENDING'` — is it growing? Fix: scale Debezium connectors, optimize Kafka producer batch settings, or shard the outbox table by aggregateId.
- "Events published to Kafka out of order for the same aggregate" → Polling relay with concurrent threads: thread 1 publishes event 5, thread 2 publishes event 6, but thread 2 completes first → event 6 arrives before event 5 in Kafka. Fix: single-threaded relay per aggregate (partition by aggregateId), or use Kafka's idempotent producer + transactional producer to enforce ordering. CDC-based (Debezium) preserves WAL ordering — naturally ordered per aggregate.
- "Database table running out of space — outbox table growing" → Relay is failing silently. Check relay logs. `status='PENDING'` rows accumulating: relay not processing them. Fix the relay. Long-term: add `createdAt < now() - interval '24 hours'` alert for stale outbox rows. Implement outbox table cleanup job for `status='DONE'` rows older than 30 days.

---

### ⚙️ How It Works (Mechanism)

**Transaction atomicity:**

```
Service DB Transaction:
  BEGIN
    UPDATE orders SET status='PAID' WHERE id=123
    INSERT INTO outbox_events (
      id=uuid, aggregateId='123',
      aggregateType='Order', eventType='OrderPaid',
      payload='{"orderId":"123","amount":150}',
      topic='order-events', status='PENDING',
      createdAt=now()
    )
  COMMIT
  [Both rows written or neither — atomically]
```

**CDC relay flow (Debezium):**

```
Postgres WAL    Debezium    Kafka
    │              │          │
    │─new INSERT───▶           │
    │  outbox row   │          │
    │               │─publish──▶
    │               │  topic=order-events
    │               │  key=aggregateId
    │               │  value=payload
    │               │◀─ACK─────│
    │               │ mark DONE or continue
    │               │ (WAL offset committed)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PAYMENT PROCESSED → EVENT PUBLISHED:**

```
Client  API  PaymentSvc  DB       Outbox   Debezium   Kafka
  │      │       │        │         │          │         │
  │─pay──▶       │        │         │          │         │
  │       │─cmd──▶        │         │          │         │
  │       │       │BEGIN TX│         │          │         │
  │       │       │─UPDATE─▶│         │         │         │
  │       │       │─INSERT──────────▶│          │         │
  │       │       │COMMIT   │         │          │         │
  │◀─200──│       │         │         │          │         │
  │                         │[WAL]────────────────▶        │
  │                         │         │          │─publish──▶
  │                         │    ← YOU ARE HERE  │         │
  │                         │         │          │◀─ACK────│
  │                         │         │[mark DONE]│         │
```

**WHAT CHANGES AT SCALE:**
At high write volume: the outbox table becomes a hot table (many concurrent inserts). Partition the outbox table by `aggregateType` or `createdAt` range. Debezium connector can have multiple tasks (parallelism). At very high scale: one Debezium connector per service → multiple connectors on a shared Kafka Connect cluster. Monitor: Debezium lag, outbox table row count by status.

---

### 💻 Code Example

**BAD - Dual-write without Outbox Pattern:**

```java
// BAD: dual-write — two independent systems
// One can succeed while the other fails
// No guaranteed consistency

@Transactional
public void processPayment(String orderId, BigDecimal amount) {
    // Step 1: update DB (succeeds)
    orderRepo.updateStatus(orderId, "PAID");
    // Step 2: publish event (might fail)
    // If Kafka is down here:
    // - DB is updated (order is PAID)
    // - Kafka event is LOST
    // - Fulfillment never triggered
    // - Customer paid but order not fulfilled
    kafkaTemplate.send("order-events",
        new OrderPaidEvent(orderId, amount));
}
```

**GOOD - Outbox Pattern: atomic write + reliable relay:**

```java
// GOOD: Outbox Pattern — single DB transaction,
// reliable async delivery

// Schema (single migration):
// CREATE TABLE outbox_events (
//   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//   aggregate_id VARCHAR(255) NOT NULL,
//   aggregate_type VARCHAR(255) NOT NULL,
//   event_type VARCHAR(255) NOT NULL,
//   payload JSONB NOT NULL,
//   status VARCHAR(20) DEFAULT 'PENDING',
//   created_at TIMESTAMPTZ DEFAULT now()
// );

@Transactional // SINGLE TRANSACTION — both writes are atomic
public void processPayment(String orderId,
    BigDecimal amount) {
    // Business state update
    Order order = orderRepo.findById(orderId)
        .orElseThrow();
    order.markPaid(amount);
    orderRepo.save(order);

    // Outbox entry — in SAME transaction
    OutboxEvent outboxEvent = OutboxEvent.builder()
        .aggregateId(orderId)
        .aggregateType("Order")
        .eventType("OrderPaid")
        .payload(buildPayload(order, amount))
        .build();
    outboxRepo.save(outboxEvent);
    // Atomically committed — Kafka is NOT involved here
    // Debezium relay will publish asynchronously
}

// Debezium Kafka Connect configuration:
// {
//   "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
//   "table.include.list": "public.outbox_events",
//   "transforms": "outbox",
//   "transforms.outbox.type":
//     "io.debezium.transforms.outbox.EventRouter",
//   "transforms.outbox.route.by.field": "aggregate_type",
//   "transforms.outbox.table.field.event.key": "aggregate_id"
// }
```

---

### ⚖️ Comparison Table

|                    | Outbox + CDC             | Outbox + Polling          | Direct dual-write            |
| :----------------- | :----------------------- | :------------------------ | :--------------------------- |
| Delivery guarantee | At-least-once            | At-least-once             | Best-effort (data loss risk) |
| Latency            | Near-real-time (~ms)     | Polling interval (s)      | Lowest (synchronous)         |
| Infrastructure     | Debezium + Kafka Connect | Scheduled job             | None extra                   |
| Complexity         | High (CDC setup)         | Low                       | None                         |
| Broker dependency  | None in critical path    | None in critical path     | Yes (broker must be up)      |
| Ordering           | WAL order preserved      | Depends on implementation | Not guaranteed               |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| :-------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Outbox Pattern provides exactly-once delivery"     | Outbox Pattern provides AT-LEAST-ONCE delivery. If the relay publishes to Kafka and then crashes before marking the outbox row as `DONE`: on restart, it will re-read the same row and publish again → duplicate message. Consumers must be idempotent (DST-029). If you need exactly-once: use Kafka's transactional producer + consumer, coordinated with the database transaction — but this is significantly more complex.                                                                               |
| "CDC is required for the Outbox Pattern"            | CDC (Debezium) is the preferred relay implementation for low-latency and high-volume scenarios, but is NOT required. A polling publisher (scheduled job queries outbox table, publishes, marks done) works fine for lower volumes and simpler infrastructure. CDC adds: near-real-time relay (WAL-based, no polling delay), lower database load (no repeated SELECT queries), and WAL-based ordering guarantees. Polling is sufficient for services with moderate event rates and is much simpler to deploy. |
| "The outbox table is permanent — never delete rows" | Outbox rows with `status='DONE'` can and should be deleted (or archived) after a retention period. Retaining all outbox rows indefinitely grows the table unboundedly. Implement a cleanup job: delete `DONE` rows older than 30 days (or your audit retention requirement). If CDC is used: Debezium tracks its WAL offset — not the outbox table rows. Deleting `DONE` rows does not affect CDC delivery.                                                                                                  |
| "Outbox Pattern is only for events to Kafka"        | The relay can deliver to any messaging system: RabbitMQ, SQS/SNS (AWS), Azure Service Bus, HTTP webhooks, email. The pattern is broker-agnostic. The relay reads the outbox table and delivers to whatever target the `topic` or `destination` column specifies. Some implementations use a single outbox table for multiple destinations, with the `eventType` or `destination` column routing to different brokers.                                                                                        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Relay Silently Fails — Outbox Grows Indefinitely**

**Symptom:** Operations team receives alert: outbox table has 500,000 `PENDING` rows and growing. Services downstream have not received new events for 2 hours. Projection read models are stale. Saga orchestrations are stuck.
**Root Cause:** Debezium connector failed (lost replication slot, Kafka Connect worker crash, misconfigured SMT). The connector is not processing the outbox table. No alert was configured for connector failure or outbox lag.
**Diagnostic:**

```bash
# Check Debezium connector status:
curl http://kafka-connect:8083/connectors/outbox-connector/status
# Look for: "connector.state": "FAILED" or task state FAILED
# Error message: replication slot not found, connection refused, etc.

# Check outbox table pending count:
psql -c "SELECT COUNT(*), MAX(created_at) FROM outbox_events
         WHERE status='PENDING';"
# If count growing and max(created_at) is old: relay stuck

# Check Debezium lag (WAL offset behind):
psql -c "SELECT slot_name, pg_wal_lsn_diff(
           pg_current_wal_lsn(), restart_lsn) AS lag_bytes
         FROM pg_replication_slots
         WHERE slot_name = 'debezium_outbox';"
# Large lag_bytes: Debezium hasn't consumed WAL recently
```

**Fix:** Restart Debezium connector: `PUT /connectors/outbox-connector/restart`. If replication slot was dropped: recreate the slot and reset Debezium offset to process new events (events already PENDING must be handled by a polling fallback). Add circuit breaker: if outbox pending count > 10,000 → alert immediately.
**Prevention:** Monitor Kafka Connect connector health with Prometheus. Alert on: connector `FAILED` state, outbox `PENDING` count > 1,000, replication slot lag > 1GB. Implement a polling publisher as a fallback for when CDC fails.

**Failure Mode 2: At-Least-Once Duplicates Cause Double Processing**

**Symptom:** Order fulfillment service processes `OrderPaid` events. Some orders are shipped twice. Investigation: `outbox_events` table shows events with `status='PENDING'` that were already published (relay crashed after Kafka ACK, before marking `DONE`). On relay restart: the same events re-published → fulfillment receives duplicates → ships twice.
**Root Cause:** At-least-once delivery is working as designed. Relay crashed in the window between Kafka ACK and outbox row status update. Fulfillment service is NOT idempotent — it processes each `OrderPaid` event without checking if the order was already fulfilled.
**Diagnostic:**

```bash
# Check for duplicate events in Kafka:
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic order-events --from-beginning | \
  jq '.aggregateId' | sort | uniq -d
# Duplicate aggregateIds: confirmed duplicates in topic

# Check fulfillment service for idempotency:
grep -r "orderId\|deduplication\|idempotent" \
  fulfillment-service/src/
# If not present: missing idempotency
```

**Fix:** Fulfillment service must be idempotent: before processing `OrderPaid`, check if the order is already in `FULFILLED` status. `INSERT INTO fulfillments (orderId, ...) ON CONFLICT (orderId) DO NOTHING` — idempotent insert. Or: check `fulfilled_orders` table before processing. Kafka: use consumer group offset management — if `OrderPaid` event has been processed (offset committed), it won't be redelivered by the same consumer group (but won't protect against relay-level duplicates in the topic itself).
**Prevention:** Design ALL event consumers to be idempotent. Treat "at-least-once delivery" as the baseline — never assume exactly-once. Include a unique `eventId` (UUID) in every outbox event. Consumers track `processed_event_ids` — skip events already processed.

**Failure Mode 3: Security - Outbox Payload Contains Sensitive Data**

**Symptom:** Security audit of the outbox table: `OrderPaid` events contain full credit card number, CVV, and billing address in the JSON payload. The outbox table is accessible to DBA team, monitoring tools, and Debezium. Kafka topics accessible to multiple consumer services — all can read payment card data. PCI-DSS compliance violation.
**Root Cause:** Service stored the full payment request payload in the outbox event, including sensitive fields. Outbox table and Kafka have broad access — developers and tools can read these fields.
**Diagnostic:**

```bash
# Check outbox payload for sensitive data:
psql -c "SELECT payload FROM outbox_events
         WHERE event_type='OrderPaid' LIMIT 1;" | \
  python3 -c "import sys,json; d=json.load(sys.stdin);
  print([k for k in d if k in
    ['cardNumber','cvv','ssn','password']])"
# If non-empty: sensitive fields in payload

# Check Kafka topic for PCI data:
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic order-events --from-beginning --max-messages 1 | \
  jq 'keys'
# Identify sensitive keys in event payload
```

**Fix:** Sanitize outbox payloads before writing: include only non-sensitive fields needed for downstream processing. `OrderPaid` event: `{orderId, amount, currency, customerId}` — NOT card numbers. Use tokenization: store Stripe payment method ID (token) — not raw card data. Never include raw PCI/PII data in events.
**Prevention:** Event schema review: classify every field in every event type. Events containing PCI/PII data must be reviewed by security. Apply field-level encryption for sensitive fields that must appear in events (decrypt only in authorized consumers). Restrict Kafka topic ACLs: `order-events` readable only by fulfillment-service and accounting-service (not all services).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-062 - Event Sourcing (Outbox Pattern solves reliable publishing from Event Sourcing stores)
- DST-061 - CQRS (Outbox enables reliable event delivery for CQRS projections)
- DST-029 - Idempotency (at-least-once delivery requires idempotent consumers)

**Builds On This (learn these next):**

- DST-056 - Saga Pattern (Sagas use reliable event publishing — Outbox Pattern enables this)
- DST-062 - Event Sourcing (ES + Outbox = reliable event sourcing pipeline)

**Alternatives / Comparisons:**

- DST-061 - CQRS (CQRS projections need reliable event delivery — Outbox Pattern is the solution)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Write outbox entry + business  |
|                  | update in one DB transaction;  |
|                  | relay delivers to Kafka async  |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Dual-write: DB update succeeds |
|                  | but Kafka publish fails = data |
|                  | loss / inconsistency           |
+------------------+--------------------------------+
| KEY INSIGHT      | DB transaction is local (safe);|
|                  | Kafka is remote (unreliable);  |
|                  | make remote delivery async     |
+------------------+--------------------------------+
| USE WHEN         | Service must update DB AND     |
|                  | publish event; broker may be   |
|                  | unavailable; no 2PC available  |
+------------------+--------------------------------+
| AVOID WHEN       | Exactly-once is required (need |
|                  | Kafka transactions + idempotent|
|                  | consumers); simple 2-service   |
|                  | systems where polling suffices |
+------------------+--------------------------------+
| TRADE-OFF        | Reliable delivery vs added     |
|                  | outbox table + relay infra +   |
|                  | at-least-once complexity       |
+------------------+--------------------------------+
| ONE-LINER        | Atomic DB write + relay to     |
|                  | Kafka = no event data loss     |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-062 Event Sourcing;        |
|                  | Debezium docs                  |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. The Outbox Pattern's invariant: business state change + outbox entry are written in ONE database transaction. Atomicity eliminates the dual-write race condition. The database transaction is the only critical-path operation — Kafka publishing is deferred and retried asynchronously.
2. At-least-once delivery is the guarantee — not exactly-once. Relay failures cause duplicate messages. ALL event consumers must be idempotent. Include a unique `eventId` in every outbox event. Consumers track processed event IDs and skip duplicates.
3. Monitor outbox table pending count and relay health. If the relay fails silently: PENDING rows accumulate, read models grow stale, sagas get stuck. Alert on pending count > 1,000 or max(created_at) > 5 minutes old. Have a polling fallback for CDC relay failures.

**Interview one-liner:**
"The Outbox Pattern solves the dual-write problem: within the same database transaction as the business operation, insert an outbox row alongside the state change. A relay process (Debezium CDC or polling publisher) reads outbox rows and publishes to Kafka asynchronously. If Kafka is down: rows remain PENDING, relay retries. Guarantee: at-least-once delivery — relay crash after Kafka ACK but before marking DONE causes duplicate messages. Consumers must be idempotent. The pattern's key insight: writing to your own database (within the transaction boundary) is reliable; writing to Kafka (external) is not — make the external write asynchronous and retryable."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Convert external (unreliable) dependencies in critical paths to asynchronous (retryable) operations by buffering intent locally. The principle: when a critical operation requires coordination with an unreliable external system, record the intent locally (in your trust boundary) and deliver externally in a background process that can retry indefinitely. This eliminates availability coupling — your critical operation succeeds regardless of the external system's state. The pattern appears wherever reliable delivery across system boundaries is required: email sending (save to outbox, deliver by mail daemon), payment initiation (record in ledger, submit to payment network asynchronously), async HTTP webhooks (record event + URL in DB, deliver by webhook worker), and SMS notifications (record in notification queue, deliver by SMS gateway worker).

**Where else this pattern appears:**

- **Email client (Outbox folder):** The original metaphor. When you click "Send" in an email client with poor connectivity: the email goes to the Outbox folder (written locally). The email client's background sync process delivers it when connectivity is restored. If the connection drops mid-send: the email stays in Outbox and is retried. You never lose an email you clicked "Send" on because sending is decoupled from the local write. The Outbox Pattern in microservices is structurally identical: "click Send" = database transaction + outbox insert; "background sync" = relay process publishing to Kafka.
- **SAGA orchestration with durable state:** A Saga orchestrator (DST-056) must send commands to multiple services reliably. If a command to Service B is lost: the Saga is stuck. The orchestrator uses the Outbox Pattern: each command to a remote service is written to the outbox table within the saga state transaction. The relay delivers the command. If delivery fails: the saga state is preserved (outbox row is PENDING), relay retries, saga eventually progresses. The Outbox Pattern is the foundation of reliable saga orchestration.
- **Mobile app offline sync:** A mobile app records user actions locally (SQLite, local database) when offline. On network restoration: a sync process delivers the local records to the server. If the server is unavailable: records remain in local storage, retried periodically. This is the Outbox Pattern at the mobile edge: local storage = outbox table; sync process = relay; server API = Kafka. The pattern is universal: record locally first, deliver remotely asynchronously.

---

### 💡 The Surprising Truth

The Outbox Pattern solves a problem that most distributed systems introductions don't acknowledge: the implicit assumption that "publish an event" is a reliable operation. Developers write `kafkaTemplate.send("topic", event)` and assume the event is delivered. But: Kafka publish can fail due to network issues, broker unavailability, producer buffer overflow, or serialization errors. At 0.1% failure rate: 1 in 1,000 events is silently lost. The surprising truth: **most microservices in production are losing events silently** — they have dual-write code with no Outbox Pattern, Kafka failures are swallowed (producer.send is fire-and-forget in many implementations), and event loss is invisible (no monitoring of event pipeline completeness). The Outbox Pattern is the correct default for any system where event loss has business consequences (payment events, fulfillment events, audit events). Yet most teams discover they need it only after a production incident where events were silently lost, causing business data inconsistency that took days to diagnose and reconcile. The correct decision is to implement the Outbox Pattern from day one on any event-driven critical path — before the inevitable failure that makes its absence visible.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** Service A uses the Outbox Pattern. Debezium reads the WAL and publishes events to Kafka. Service B consumes from Kafka and updates its read model. Service A's database has a Postgres replication slot used by Debezium. The DBA team drops the replication slot (routine cleanup of unused slots). What happens? What is the impact on the system? How do you recover?
_Hint:_ When Debezium's replication slot is dropped: Debezium loses its WAL position. Postgres no longer retains WAL segments that Debezium hasn't consumed (the replication slot is what tells Postgres "don't discard this WAL yet"). On restart: Debezium cannot resume from its last WAL position — the WAL segments are gone. Debezium must start from the "current" WAL position → all events written between the last consumed WAL position and now are NEVER replayed. Those outbox rows remain `PENDING` forever — or they have not been inserted yet. Impact: all events between last Debezium consumption and slot deletion are lost (never published to Kafka). Downstream services have a gap. Recovery: (1) Identify the time gap (when was the slot last consumed? when was it dropped?). (2) Query the outbox table for `PENDING` rows created during that window. (3) Use a polling publisher to process those `PENDING` rows manually — publish to Kafka, mark DONE. (4) Recreate the Debezium replication slot from current WAL position. Lesson: never drop Debezium replication slots. Monitor slot health. Alert if slot WAL lag grows (slot retained WAL but Debezium not consuming → unbounded WAL growth). Add IAM/ACL restrictions: only Debezium service account can access the replication slot.

**Q2 (D - Root Cause):** The outbox relay is functioning correctly (Debezium running, Kafka receiving events, relay marking rows DONE). But consumer service B's read model is missing some events. Investigation: some `DONE` rows in the outbox table have no corresponding Kafka message in the topic. What are the possible explanations?
_Hint:_ Possible root causes: (1) **Kafka topic retention deleted old events.** If the Kafka topic has `retention.ms=86400000` (1 day), events published more than 1 day ago are deleted. Service B's consumer started reading from the beginning after a reset → topic retention deleted old messages → events appear missing. Fix: increase retention or replay from the outbox table for the gap period. (2) **Debezium marked the outbox row as DONE but Kafka publish failed silently.** This should not happen with proper Debezium configuration (Debezium commits WAL offset AFTER Kafka ACK). But: if Kafka transactional producer is misconfigured, a Kafka error can be swallowed. Check Debezium logs for WARN/ERROR during publish. (3) **Consumer skipped events due to deserialization error.** Consumer received the event but threw a deserialization exception → went to the DLQ → not reflected in the read model. Check DLQ topic for messages. (4) **Kafka topic partition key caused event ordering issue.** Events for the same aggregate published to different partitions (hash collision, key routing change) → consumer reads them out of order → later events processed before earlier ones → earlier event's state update is overwritten. Check: are partition keys consistent (always `aggregateId`)? Investigate by checking Kafka message partition for affected aggregateIds.

**Q3 (C - Design Trade-off):** A team is deciding between: (A) Outbox Pattern + Debezium CDC, (B) Outbox Pattern + polling publisher, and (C) direct dual-write (update DB then publish to Kafka) for their order event publishing. The system: 500 orders/minute, Kafka 99.9% available (8.7 hours downtime/year), team has 2 engineers. Which approach do you recommend and why? What happens to the rejected approaches at 10× scale?
_Hint:_ At 500 orders/minute (8.3 orders/second): (A) Debezium CDC: near-zero latency, no polling overhead, WAL ordering guaranteed. Complexity: Debezium setup, Kafka Connect cluster, WAL management, replication slot monitoring. Maintenance cost for 2 engineers: HIGH (Debezium is complex, requires ongoing monitoring). (B) Polling publisher: polling every 1 second with batch=100 gives 1-second max delay, sufficient for 8.3 orders/second. Simplicity: scheduled job, simple SELECT/UPDATE. Reliability: at-least-once (same as CDC). Suitable for 2-engineer team. (C) Direct dual-write: at 99.9% Kafka availability → 8.7 hours downtime/year × (500/60) orders/min = 4,350 orders potentially lost/year during Kafka downtime. Unacceptable if each lost order = business data loss. **Recommendation: (B) polling publisher** for this scale and team size. Simple, reliable, maintainable by 2 engineers. 1-second delay: acceptable for order events. At 10× scale (5,000 orders/minute = 83 orders/second): (A) Debezium becomes appropriate — polling at 83 orders/second with 100-row batches means polling every 1.2 seconds with full batches, adding database load. CDC is more efficient (WAL-based, no polling SELECT). (C) direct dual-write: at 10× scale, Kafka downtime impact increases 10×: 43,500 lost orders/year. Even more unacceptable. Scale changes the cost/benefit of CDC vs polling — higher volume justifies CDC complexity.

