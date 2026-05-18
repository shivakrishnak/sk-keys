---
id: DPT-053
title: Outbox Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-052
used_by: DPT-064, DPT-065
related: DPT-052, DPT-054, DPT-084, DPT-085
tags:
  - pattern
  - distributed-systems
  - advanced
  - message-reliability
  - transactional-outbox
  - event-driven
  - exactly-once
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/design-patterns/outbox-pattern/
---

⚡ TL;DR - The Outbox Pattern guarantees at-least-once
message delivery in distributed systems by writing events
to a transactional "outbox" table in the SAME database
transaction as the business state change, then having
a separate process reliably publish those events to
a message broker.

| #53 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-052 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-052, DPT-054, DPT-084, DPT-085 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT OUTBOX:**
```java
@Transactional
public void placeOrder(OrderRequest req) {
    Order order = new Order(req);
    orderRepository.save(order);           // DB write: success
    kafkaTemplate.send("orders", event);   // Kafka publish: ??
}
```

**THREE FAILURE SCENARIOS:**
1. DB saves successfully. Kafka publish throws exception.
   Transaction rolls back. Order is gone. Event was never
   published (but Kafka might have received it before
   the exception). → Lost order, possible duplicate event.

2. DB saves. Kafka receives the message. Application crashes
   before the transaction commits. DB rolls back.
   Kafka cannot roll back. Event is published for an order
   that does not exist. → Ghost event, downstream confusion.

3. Network timeout sending to Kafka. Did Kafka receive it?
   Unknown. Developer adds retry: possible duplicate
   events. → Duplicate processing, double charges, etc.

**The ROOT PROBLEM:**
Database transactions and Kafka publishes are in DIFFERENT
transactional domains. There is no distributed transaction
that makes them atomic. This is the "dual write" problem:
writing to two systems atomically is impossible without
a distributed commit protocol (expensive, brittle).

**THE SOLUTION:**
Write the event to the SAME database as the business
data (same transaction, always atomic). A separate relay
process reads committed events from the database and
publishes to Kafka. The relay is the only component
that talks to Kafka; it has clear retry and deduplication
semantics.

---

### 📘 Textbook Definition

The **Outbox Pattern** (also called Transactional Outbox)
solves the dual-write problem in event-driven architectures.
Instead of publishing directly to a message broker during
a transaction, the service writes the event to an `outbox`
table in the SAME database transaction as the business
change. A separate "relay" component (Change Data Capture
or polling relay) reads from the `outbox` table and
publishes events to the broker, with idempotency guarantees.

**Guarantees:**
- If the business transaction commits, the outbox record exists.
- If the business transaction rolls back, the outbox record
  does not exist.
- The relay publishes all committed outbox records at least once.
- Consumers handle deduplication (idempotency).

**Result:** At-least-once delivery with exactly-once
business logic (idempotent consumers make this effectively
exactly-once end-to-end).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Outbox Pattern: write event + business state in one
transaction, publish separately - never lose an event,
never publish for a rolled-back transaction.

**One analogy:**
> The "outbox" on a physical desk: important letters
> to send. You write a letter (business change) and
> put it in the outbox (same action, same moment, atomic).
> A mail carrier (relay) takes all letters from the
> outbox and delivers them to the post office (Kafka).
> The letter is definitely in the outbox (or was never
> written, if the writing was interrupted). The mail
> carrier reliably delivers everything in the outbox.
> Result: every written letter is eventually delivered;
> no letter is delivered for something that was never
> written.

**One insight:**
The Outbox Pattern trades the dual-write problem for
a single-write problem (database transaction) + an
async relay. The relay is a simple, stateless component
with clear semantics: read from outbox, publish to broker,
mark as published. This is tractable. The dual-write
(DB + Kafka atomically) is not tractable without distributed
transactions.

---

### 🔩 First Principles Explanation

**THE DUAL WRITE PROBLEM:**
Two systems. One operation. Must keep them consistent.
Without a distributed transaction protocol (two-phase
commit): impossible to guarantee atomicity.

**THE OUTBOX INSIGHT:**
Convert the dual write (DB + broker) into a single write
(DB only) + an async relay. The database is the source
of truth. The broker receives events eventually from
the relay.

**RELAY MECHANICS:**
Two approaches:
1. **Polling relay:** A scheduled process queries `SELECT *
   FROM outbox WHERE published = false ORDER BY created_at`
   every N seconds. Publishes each record to Kafka. Marks
   as published. Simple but adds polling overhead.
2. **CDC (Change Data Capture):** Debezium reads the
   PostgreSQL WAL (Write-Ahead Log) and publishes every
   INSERT to the `outbox` table directly to Kafka. No
   polling. Low latency (seconds). No additional DB load.
   Complex to set up.

**AT-LEAST-ONCE DELIVERY:**
If the relay publishes an event and then crashes before
marking it as published, the event will be re-published
on restart. Consumers may receive duplicates. They must
be idempotent: processing the same event twice has the
same effect as processing it once.

---

### 🧪 Thought Experiment

**WHAT HAPPENS WHEN:**

**Scenario A: DB transaction commits, relay crashes before Kafka publish:**
On relay restart: outbox record still exists (not marked
published). Relay publishes it. Consumer processes it.
Result: correct delivery. Event is published once.

**Scenario B: Relay publishes to Kafka, crashes before marking as published:**
On relay restart: outbox record still not marked published.
Relay publishes AGAIN. Consumer receives duplicate.
Consumer must be idempotent: process the duplicate
without double-effect. Result: at-least-once delivery.
Idempotent consumer: effectively-once business outcome.

**Scenario C: DB transaction rolls back:**
Outbox record never written. Relay never sees this event.
Kafka never receives this event. Result: no ghost events.
Correct: if the order didn't save, no "order placed" event.

---

### 🧠 Mental Model / Analogy

> Outbox Pattern solves a bank transfer problem:
> "Debit account A AND notify account B in one atomic step."
> Without outbox: sometimes the debit happens, sometimes
> the notification; rarely both reliably.
> With outbox: Debit A and write "notify B" to the outbox
> in ONE transaction. A messenger (relay) reads the
> outbox and sends the notification. If the messenger
> fails, they try again (at-least-once). If the bank
> branch receives the message twice, it checks "was this
> already processed?" (idempotency check) and ignores
> the duplicate.
>
> Two-phase problems require two-phase solutions.
> Outbox makes "write data + notify" into one-phase write
> + one-phase relay.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Outbox Pattern: when you save data AND need to publish
an event, write both to the database together (same
transaction). A background process reads the pending
events and publishes them to Kafka. Never lose an event.
Never publish a ghost event for a rolled-back write.

**Level 2 - How to implement it:**
Add an `outbox` table: `(id, aggregate_type, aggregate_id,
event_type, payload, published, created_at)`. In the
same `@Transactional` method that saves business data:
also `INSERT INTO outbox (...)`. A scheduled relay
(or Debezium CDC) reads unpublished outbox records,
publishes to Kafka, marks as published.

**Level 3 - CDC vs polling relay:**
Polling: simple, adds DB read load every N seconds.
CDC (Debezium + Kafka Connect): reads PostgreSQL WAL,
zero polling overhead, sub-second latency, but requires
Kafka Connect cluster and Debezium configuration.
For low-throughput systems: polling. For high-throughput:
CDC.

**Level 4 - Idempotency design:**
Every consumer of outbox-published events MUST be idempotent.
An event ID (UUID) should be the idempotency key.
Consumer: before processing, check if `event_id` is
in `processed_events` table. If yes: skip. If no:
process and insert into `processed_events`. Use a unique
constraint to prevent race conditions on the insert.

**Level 5 - Outbox at scale:**
At high throughput (10,000+ events/sec): the outbox table
becomes a hot-spot. Optimizations:
- Partition outbox by aggregate type (separate tables
  per event type reduce contention).
- Use PostgreSQL UNLOGGED tables for the outbox (faster
  writes, acceptable loss on crash since WAL captures changes).
- Archival: regularly move published outbox records to
  a cold storage table or delete them. The outbox table
  should never have unbounded growth.
- Debezium CDC: avoids polling but requires WAL replication
  slot maintenance (monitor slot lag; lagging slots block
  WAL cleanup and can fill disk).

---

### ⚙️ How It Works (Mechanism)

```
Outbox Pattern Flow

WRITE TRANSACTION (atomic):
┌─────────────────────────────────────────────────────────┐
│ BEGIN TRANSACTION                                       │
│   INSERT INTO orders (...) VALUES (...)      ─── write  │
│   INSERT INTO outbox (aggregate_id, event_type,         │
│     payload, published=false)                ─── outbox │
│ COMMIT                                                  │
│                                                         │
│ Either BOTH inserted or NEITHER (atomicity)             │
└─────────────────────────────────────────────────────────┘
                         │
RELAY (async, separate process):
┌─────────────────────────────────────────────────────────┐
│ SELECT * FROM outbox WHERE published = false            │
│   ORDER BY created_at LIMIT 100                         │
│                                                         │
│ FOR EACH record:                                        │
│   kafkaTemplate.send(record.eventType, record.payload)  │
│   UPDATE outbox SET published=true WHERE id=record.id   │
│                                                         │
│ If crash after publish, before UPDATE:                  │
│   → Re-reads on restart → republishes (at-least-once)  │
└─────────────────────────────────────────────────────────┘
                         │
CONSUMER (idempotent):
┌─────────────────────────────────────────────────────────┐
│ Receive event                                           │
│   IF event_id IN processed_events: SKIP                 │
│   ELSE: process + INSERT INTO processed_events          │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - The dual write problem (dangerous pattern):**

```java
// BAD: Publishing directly from @Transactional - dual write
@Transactional
public void placeOrder(OrderRequest req) {
    Order order = orderRepository.save(new Order(req));
    // PROBLEM: this publish is NOT in the DB transaction
    // If it fails: order saved but event lost
    // If app crashes between save() and send(): ghost state
    kafkaTemplate.send("order-placed", new OrderPlacedEvent(order));
}
```

**Example 2 - Outbox Pattern implementation:**

```java
// GOOD: Transactional Outbox - event written to DB atomically

// Outbox entity:
@Entity @Table(name = "outbox")
class OutboxRecord {
    @Id String id;
    String aggregateType;   // "Order"
    String aggregateId;     // order UUID
    String eventType;       // "OrderPlaced"
    String payload;         // JSON
    boolean published;      // default false
    LocalDateTime createdAt;
}

// Service: write order + outbox in ONE transaction
@Service class OrderCommandService {
    @Autowired OrderRepository orderRepo;
    @Autowired OutboxRepository outboxRepo;
    @Autowired ObjectMapper objectMapper;

    @Transactional
    public String placeOrder(OrderRequest req) throws Exception {
        Order order = orderRepo.save(new Order(req));

        // Write event to outbox IN THE SAME TRANSACTION
        OutboxRecord outbox = new OutboxRecord();
        outbox.setId(UUID.randomUUID().toString());
        outbox.setAggregateType("Order");
        outbox.setAggregateId(order.getId());
        outbox.setEventType("OrderPlaced");
        outbox.setPayload(objectMapper.writeValueAsString(
            new OrderPlacedEvent(order)));
        outbox.setPublished(false);
        outboxRepo.save(outbox);

        return order.getId();
        // COMMIT: both Order AND OutboxRecord saved atomically
        // If commit fails: neither saved (no ghost events)
        // If commit succeeds: event guaranteed to be published
    }
}

// Relay: polling publisher
@Component class OutboxRelay {
    @Autowired OutboxRepository outboxRepo;
    @Autowired KafkaTemplate<String, String> kafkaTemplate;

    @Scheduled(fixedDelay = 1000)  // every 1 second
    @Transactional
    public void publishPendingEvents() {
        List<OutboxRecord> pending =
            outboxRepo.findByPublishedFalseOrderByCreatedAt(
                PageRequest.of(0, 100));

        for (OutboxRecord record : pending) {
            kafkaTemplate.send(record.getEventType(),
                record.getPayload())
                .get(5, SECONDS);  // wait for broker ack
            record.setPublished(true);
            outboxRepo.save(record);
        }
    }
}
```

**Example 3 - Idempotent consumer:**

```java
// Consumer: must handle duplicate events
@KafkaListener(topics = "OrderPlaced")
@Transactional
public void onOrderPlaced(String payload,
    @Header(KafkaHeaders.RECORD_METADATA) RecordMetadata meta)
    throws Exception {

    OrderPlacedEvent event = objectMapper.readValue(
        payload, OrderPlacedEvent.class);

    // IDEMPOTENCY CHECK: skip if already processed
    if (processedEventRepo.existsById(event.getEventId())) {
        log.debug("Duplicate event {}, skipping", event.getEventId());
        return;
    }

    // PROCESS (business logic):
    inventoryService.reduceStock(event.getItems());

    // MARK AS PROCESSED (within same transaction):
    processedEventRepo.save(new ProcessedEvent(event.getEventId()));
    // If crash here: transaction rolls back.
    // On re-consume: inventory NOT reduced (rollback),
    // event not marked as processed.
    // Next attempt: processes correctly.
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Outbox Pattern achieves exactly-once delivery | Outbox achieves at-least-once delivery. Exactly-once requires idempotent consumers in addition. Together: effectively-once business outcome |
| Outbox requires Debezium / CDC | Polling relay is a valid simpler alternative. CDC (Debezium) is more efficient at scale but adds operational complexity. Start with polling; migrate to CDC when throughput warrants it |
| Inbox and Outbox are the same | They address opposite sides. Outbox: producer reliably publishes. Inbox (DPT-084): consumer reliably processes without losing messages between receipt and processing |
| Using Kafka transactions solves the dual write problem | Kafka transactions provide atomic multi-partition writes within Kafka. They do NOT provide atomicity across Kafka + PostgreSQL. The database transaction and Kafka transaction are still in separate systems |

---

### 🚨 Failure Modes & Diagnosis

**Relay Not Processing / Outbox Table Grows Unbounded**

**Symptom:**
Downstream consumers are not receiving events. The `outbox`
table has millions of `published=false` records.

**Root Cause:**
The relay stopped publishing (crash, Kafka unavailability,
exception in processing one record).

**Diagnosis:**
```sql
-- Check oldest unpublished record
SELECT MIN(created_at), COUNT(*)
FROM outbox WHERE published = false;
-- If oldest is hours ago: relay is stuck

-- Check relay log
-- "Failed to publish event" → Kafka connectivity issue
-- "Exception processing record X" → one bad record blocks the queue
```

**Fix:**
For relay stuck on a bad record: add dead-letter handling
in the relay (skip/DLQ record after N retries).
For Kafka unavailability: relay will backlog until
connectivity restored. The outbox is the buffer.
Set an alert on `outbox` size > threshold.

---

### 🔗 Related Keywords

**Prerequisite:**
- `CQRS Pattern` - DPT-052: Outbox is how the write side
  reliably publishes events to update the read model

**Builds on this:**
- `Inbox Pattern` - DPT-084: consumer-side reliability
- `Idempotency Pattern` - DPT-085: consumers handling
  at-least-once delivery

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Write event to DB in same transaction   │
│              │ as business change; relay publishes async│
├──────────────┼──────────────────────────────────────────┤
│ GUARANTEES   │ At-least-once delivery                  │
│              │ No ghost events (rolled-back transactions│
│              │ No lost events (committed transactions)  │
├──────────────┼──────────────────────────────────────────┤
│ RELAY OPTIONS│ Polling (simple) vs CDC/Debezium (fast) │
├──────────────┼──────────────────────────────────────────┤
│ REQUIRES     │ Idempotent consumers (duplicate handling)│
├──────────────┼──────────────────────────────────────────┤
│ SCALE ALERT  │ Monitor outbox table size + relay lag   │
│              │ WAL slot lag for CDC deployments        │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-054: Saga Pattern                   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Dual write problem: DB + Kafka cannot be atomic without
   distributed transactions. Outbox: write event to DB
   (same transaction as business state). Relay publishes
   from DB to Kafka. Atomic where it matters (DB).
2. Outbox = at-least-once (relay may republish on crash).
   Consumers must be idempotent to make it effectively-once.
3. Relay options: polling (simple, latency ~1s, DB load)
   vs CDC/Debezium (complex, sub-second, no polling load).
   Monitor outbox table size; unbounded growth = relay stuck.

