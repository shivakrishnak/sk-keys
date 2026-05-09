---
layout: default
title: "Outbox Pattern"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /design-patterns/outbox-pattern/
id: DPT-053
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - distributed
  - deep-dive
  - microservices
  - java
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-053 - Outbox Pattern

⚡ TL;DR - The Outbox Pattern atomically saves business state and the event to publish in the same database transaction, solving the dual-write problem that causes silent message loss.

| DPT-053 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Design Patterns, CQRS Pattern, Event Sourcing Pattern, Transaction, Idempotency | |
| **Used by:** | Microservices, Distributed Systems, Event-Driven Architecture, CQRS Pattern | |
| **Related:** | CQRS Pattern, Saga Pattern, Change Data Capture, Transactional Outbox, Idempotency | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An order service creates an order in PostgreSQL and then publishes an `OrderCreated` event to Kafka. The two operations are separate: (1) database commit, (2) Kafka produce. If the Kafka broker is unavailable between step 1 and step 2, the order exists in the database but no event was published. Downstream services (inventory, email, shipping) never know the order was created. The system is silently inconsistent.

**THE BREAKING POINT:**
The two-step pattern is fundamentally broken under partial failure. You can reverse the order (publish first, then commit) but that introduces the inverse problem: the event arrives at downstream services but the order fails to commit. There is no atomic "commit to DB and publish to queue" operation across two different systems.

**THE INVENTION MOMENT:**
This is exactly why the Outbox Pattern was invented - to solve the dual-write problem by making message publishing part of the same database transaction as the state change, eliminating the gap between the two operations where failures occur.

**EVOLUTION:**
Outbox Pattern emerged from distributed systems practice as
transaction-message atomicity became a critical reliability
requirement in microservices (circa 2016-2018). Chris Richardson
documented it in "Microservices Patterns" (2018) as the canonical
solution to the dual-write problem. Spring's Modulith (2023) added
built-in `@ApplicationModuleListener` with outbox table support.
Debezium (CDC -- Change Data Capture) provides infrastructure-level
outbox support by streaming database change logs directly to Kafka,
eliminating manual outbox polling. The pattern is now considered
a prerequisite for event-driven microservices in regulated
industries.

---

### 📘 Textbook Definition

The Outbox Pattern (also called the Transactional Outbox) is a reliability pattern for event-driven architectures that solves the dual-write problem. It works by writing the intended message/event to an "outbox" table in the same database transaction as the business state change. A separate relay process then reads from the outbox and publishes the messages to the message broker. If publishing fails, the relay retries from the outbox. The outbox entry is deleted (or marked published) only after confirmed broker delivery.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Save the event you need to publish in your database alongside the data change - guaranteed never to be lost.

**One analogy:**
> Imagine you need to both file a document and mail a copy to a colleague. Normally you file first, then mail - but if you leave the office before mailing, the colleague never gets a copy. The Outbox Pattern is leaving the envelope in a dedicated "to-send" tray on your desk. A reliable mail carrier checks the tray and sends everything in it. Even if you forget, the carrier will not.

**One insight:**
The Outbox Pattern converts a distributed problem (atomic write across two systems) into a local problem (write to two tables in one transaction). Local atomicity (database ACID) is solved technology. Distributed atomicity (two-phase commit) is complex and fragile. The Outbox Pattern takes the distributed problem off the critical path.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The outbox entry and the business state change are written in a single ACID transaction - either both commit or both roll back.
2. The outbox relay only delivers a message after it is confirmed received by the broker - the outbox entry is not deleted until delivery is confirmed.
3. The relay is idempotent - if a message is delivered twice (due to relay retry after a partial failure), downstream consumers must deduplicate using the message ID.

**DERIVED DESIGN:**
The pattern exploits the fact that databases provide ACID guarantees, while cross-system writes do not. By writing both the business state and the "intent to publish" to the same database, ACID ensures the intent is preserved even if the system crashes immediately after the transaction commits. The relay decouples the persistence of the intent from its execution.

The relay can be implemented as: (1) a polling process that queries the outbox table at fixed intervals, (2) a CDC (Change Data Capture) process (like Debezium) that tails the database WAL and publishes new outbox entries without polling.

**THE TRADE-OFFS:**
**Gain:** Guaranteed event delivery without two-phase commit; resilient to broker unavailability.
**Cost:** Additional outbox table; relay process (operational complexity); at-least-once delivery (consumers must be idempotent); latency introduced by relay polling interval.

---

### 🧪 Thought Experiment

**SETUP:**
An order service must create an order in the database and publish `OrderCreated` to Kafka. Network latency to Kafka is 50ms; database commit is 5ms.

**WHAT HAPPENS without Outbox (direct publish):**
Order commits at T=0ms. Service attempts Kafka publish. At T=52ms, Kafka broker is temporarily unavailable (60ms maintenance window). Kafka publish fails. Retry logic fails too (still within window). Service returns 201 to client (order created). `OrderCreated` never reaches downstream services. Inventory not decremented. Confirmation email not sent. User has order number, no email, incorrect inventory.

**WHAT HAPPENS with Outbox:**
At T=0ms: Order row inserted AND outbox row inserted (same transaction). Transaction commits. Service returns 201. Relay process picks up outbox row at T=100ms (poll interval). Kafka broker is back. Relay publishes `OrderCreated` to Kafka. Kafka acknowledges. Relay marks outbox row as delivered (or deletes it). Downstream services process event. Zero message loss, zero two-phase commit.

**THE INSIGHT:**
The service's responsibility is to commit the transaction. The relay's responsibility is to deliver the committed intent. The separation of these concerns removes message delivery from the critical path of the user request.

---

### 🧠 Mental Model / Analogy

> Think of a postal sorting office. When you drop a letter in the post box, it goes into the collection bin. A postal worker picks up the bin periodically and delivers the letters. You do not wait at the post box until the letter is delivered. The letter is guaranteed to be delivered - the postal system's job is delivery, not yours. The Outbox Pattern is that post box: your transaction drops the letter in the box; the relay is the postal worker.

- "Post box" → the outbox table in the database
- "Letter" → the event/message to be published
- "Postal worker" → the relay process (polling or CDC)
- "Letter delivered" → event published to message broker
- "Letter confirmed delivered" → outbox entry deleted/marked
- "Duplicate delivery checked at destination" → consumer idempotency

Where this analogy breaks down: physical letters are not replayed on postal worker failure. The relay retries delivery until confirmed - this means consumers receive duplicates under certain failure conditions and must handle them.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The Outbox Pattern means writing a "reminder" to your database at the same time as your business change. A background process reads these reminders and delivers the messages. Even if the message broker goes down, the reminders are safe in the database.

**Level 2 - How to use it (junior developer):**
Create an `outbox_events` table with columns: `id`, `event_type`, `payload`, `created_at`, `published_at`. In your service: inside the same transaction that modifies business state, insert a row into `outbox_events`. Add a scheduled job (`@Scheduled` in Spring) that queries unpublished outbox rows, publishes them to Kafka/RabbitMQ, and updates `published_at`. The key: insert into outbox AND the business table in one `@Transactional` method.

**Level 3 - How it works (mid-level engineer):**
Two outbox relay implementations: (1) **Polling**: a scheduled process queries `SELECT * FROM outbox_events WHERE published_at IS NULL ORDER BY created_at LIMIT 100`. Publish each to the broker, update `published_at`. Polling has a latency proportional to the polling interval. (2) **CDC/Debezium**: Debezium tails the database WAL (Write-Ahead Log), captures each `INSERT INTO outbox_events`, and publishes directly to Kafka. Sub-second latency, no polling overhead. Each row must have a unique `id` that the broker consumer uses as an idempotency key to deduplicate retries.

**Level 4 - Why it was designed this way (senior/staff):**
The Outbox Pattern is a consequence of the Two Generals Problem: it is fundamentally impossible to guarantee exactly-once delivery across two independent systems without coordination. The pattern accepts at-least-once delivery as a constraint and shifts the correctness burden to consumer idempotency. This is the correct tradeoff: a database row that exists but was not published is always recoverable (relay retries); a message published but state not committed is harder to reverse. By making the database the source of truth for "what was published," the Outbox Pattern makes the delivery problem observable, retryable, and auditable. At scale, Debezium + Kafka is preferred over polling because it eliminates the N×polling-interval base latency and eliminates the thundering herd problem of many services polling simultaneously.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  OUTBOX PATTERN - WRITE PATH                         │
│                                                      │
│  HTTP Request → Service                              │
│                   │                                  │
│             BEGIN TRANSACTION                        │
│                   │                                  │
│    INSERT INTO orders (id, ...) VALUES (...)         │
│                   │                                  │
│    INSERT INTO outbox_events                         │
│      (id, type, payload, created_at)                 │
│      VALUES (uuid, 'OrderCreated', {...}, now())     │
│                   │                                  │
│             COMMIT TRANSACTION                       │
│                   │                                  │
│             Return 201 to client                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  OUTBOX RELAY - DELIVERY PATH (Polling version)      │
│                                                      │
│  Relay (every Nms):                                  │
│    SELECT * FROM outbox_events                       │
│      WHERE published_at IS NULL                      │
│      ORDER BY created_at LIMIT 100                   │
│         ↓                                            │
│    For each event:                                   │
│      Publish to Kafka (with event id as key)         │
│         ↓                                            │
│      UPDATE outbox_events                            │
│        SET published_at = now()                      │
│        WHERE id = event.id                           │
│         ↓                                            │
│    (If publish fails: row stays unpublished          │
│     and is retried on next poll cycle)               │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  OUTBOX RELAY - DELIVERY PATH (Debezium/CDC)         │
│                                                      │
│  Debezium tails PostgreSQL WAL                       │
│    → Captures INSERT INTO outbox_events              │
│    → Publishes to Kafka topic directly               │
│    → Sub-second latency                              │
│    → No polling overhead                             │
│    → Outbox row = Kafka message (1:1)                │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client → POST /orders
  → OrderService.createOrder()
  → BEGIN TRANSACTION
    → INSERT INTO orders
    → INSERT INTO outbox_events [← YOU ARE HERE]
  → COMMIT
  → Return 201
  → Relay picks up outbox_event (polling or CDC)
  → Relay publishes to Kafka
  → Kafka delivers to InventoryService, EmailService
  → Relay marks event delivered
```

**FAILURE PATH:**
```
SCENARIO A: Service crashes after COMMIT
  → Outbox row exists (transaction committed)
  → Relay picks it up on next poll
  → Event delivered → no message loss

SCENARIO B: Relay fails mid-delivery
  → published_at not yet set
  → Relay retries on next poll (at-least-once)
  → Consumer deduplicates by event.id
  → No lost messages, one idempotent processing

SCENARIO C: Transaction ROLLBACK
  → Order row rolled back
  → Outbox row rolled back (same transaction)
  → No orphan event published
  → Correct: no event for non-committed order
```

**WHAT CHANGES AT SCALE:**
At 1,000 writes/second, a polling relay at 100ms intervals adds up to 100ms publication latency. At 10,000 writes/second, polling creates significant database load. At 100,000 writes/second, Debezium CDC is mandatory - polling at this scale is impractical. The outbox table must be partitioned or rapidly archived to prevent unbounded growth.

---

### 💻 Code Example

**Example 1 - Service with Outbox (Spring + JPA):**

```java
@Service
@Transactional
public class OrderService {
    private final OrderRepository orders;
    private final OutboxRepository outbox;

    public UUID createOrder(CreateOrderRequest req) {
        // 1. Create business entity
        Order order = Order.from(req);
        orders.save(order);

        // 2. Create outbox entry - SAME transaction
        OutboxEvent event = new OutboxEvent(
            UUID.randomUUID(),
            "OrderCreated",
            // Serialize to JSON
            objectMapper.writeValueAsString(
                new OrderCreatedEvent(order.id(),
                    order.customerId(),
                    order.total())),
            Instant.now()
        );
        outbox.save(event);

        // Both saved or both rolled back - ACID
        return order.id();
    }
}
```

**Example 2 - Outbox relay (polling):**

```java
@Component
public class OutboxRelay {
    private final OutboxRepository outbox;
    private final KafkaTemplate<String, String> kafka;

    @Scheduled(fixedDelay = 100) // ms
    @Transactional
    public void publishPendingEvents() {
        List<OutboxEvent> pending =
            outbox.findUnpublished(Pageable.ofSize(100));

        for (OutboxEvent event : pending) {
            // Publish with event.id as Kafka key
            // (enables consumer deduplication)
            kafka.send("order-events",
                event.id().toString(),
                event.payload())
            .get(5, TimeUnit.SECONDS); // wait for ack

            // Only mark published after Kafka ack
            outbox.markPublished(event.id());
        }
    }
}
```

**Example 3 - Consumer idempotency (required by Outbox):**

```java
@KafkaListener(topics = "order-events")
public void onOrderCreated(
        ConsumerRecord<String, String> record) {
    String eventId = record.key();

    // Deduplicate: idempotency check
    if (processedEvents.contains(eventId)) {
        log.debug("Skipping duplicate event: {}", eventId);
        return;
    }

    OrderCreatedEvent event =
        objectMapper.readValue(record.value(),
            OrderCreatedEvent.class);

    inventoryService.reserve(event.items());
    processedEvents.add(eventId); // mark processed
}
```

---

### ⚖️ Comparison Table

| Approach | Message Loss Risk | Consistency | Complexity | Best For |
|---|---|---|---|---|
| Direct publish (publish then DB) | High (DB fails after publish) | Low | Low | Never for critical events |
| Direct publish (DB then publish) | High (broker fails after DB) | Low | Low | Never for critical events |
| **Outbox (polling relay)** | None | At-least-once | Medium | Most production systems |
| Outbox + CDC (Debezium) | None | At-least-once | Medium-High | High-volume systems |
| 2-Phase Commit (XA) | None | Exactly-once | Very High | Rarely - too fragile |

How to choose: use Outbox (polling) for most systems. Use Outbox + Debezium when polling latency is unacceptable or database polling overhead is too high. Never use direct publish for events that must not be lost.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Outbox pattern provides exactly-once delivery | Outbox provides at-least-once delivery. Consumers must be idempotent. Exactly-once requires Kafka transactions which have their own complexity |
| The outbox table grows indefinitely | Outbox rows should be deleted (or archived) after confirmed delivery. An unarchived outbox table grows without bound and degrades performance |
| Debezium is always better than polling | Debezium adds operational complexity (Kafka Connect, connector configuration). Polling is simpler and sufficient for < 5,000 events/second |
| Outbox pattern prevents all message loss | Outbox prevents loss between the service and the broker. It does not prevent loss between the broker and the consumer - that requires consumer commit strategies |

---

### 🚨 Failure Modes & Diagnosis

**1. Outbox Table Grows Unbounded - Database Performance Degrades**

**Symptom:** Database query times increase; `outbox_events` table reaches millions of rows; relay performance degrades as it queries a large table.

**Root Cause:** Outbox rows are not deleted or archived after delivery. Or: relay is falling behind and accumulating backlog.

**Diagnostic:**
```sql
-- Check outbox table size:
SELECT COUNT(*), 
  COUNT(*) FILTER (WHERE published_at IS NULL) as pending
FROM outbox_events;

-- Check oldest undelivered event:
SELECT MIN(created_at) FROM outbox_events
WHERE published_at IS NULL;
```

**Fix:** Add a cleanup job: `DELETE FROM outbox_events WHERE published_at < NOW() - INTERVAL '1 day'`. Add partitioning by `created_at` date for efficient cleanup.

**Prevention:** Outbox cleaner runs on a schedule. Alert if `COUNT(*) WHERE published_at IS NULL > 10,000`.

---

**2. Relay Fails to Publish - Events Accumulate**

**Symptom:** Growing backlog of unpublished outbox events; downstream services not receiving events; consumer lag at zero (no messages arriving).

**Root Cause:** Relay process crashed or Kafka broker unreachable. Events committed to database but relay not delivering.

**Diagnostic:**
```bash
# Check relay process health:
kubectl get pods -l app=outbox-relay
# Check Kafka broker connectivity from relay:
kafka-topics.sh --bootstrap-server kafka:9092 --list
# Check outbox pending count:
psql -c "SELECT COUNT(*) FROM outbox_events \
  WHERE published_at IS NULL"
```

**Fix:** Restart the relay process. Events remain in the outbox table. When relay restarts, it picks up undelivered events from oldest to newest.

**Prevention:** Monitor outbox relay as a critical service with alerts. Run two relay instances with distributed locking (Redis/DB lock) to prevent duplicate delivery while providing failover.

---

**3. Consumer Not Idempotent - Duplicate Processing**

**Symptom:** Orders processed twice; inventory decremented twice; duplicate emails sent to customers.

**Root Cause:** Relay retried an event (after partial delivery failure). Consumer processed the same event twice without deduplication.

**Diagnostic:**
```bash
# Check for duplicate events in consumer logs:
kubectl logs deployment/inventory-service \
  | grep "OrderCreated\|processing order" \
  | sort | uniq -d
# Duplicate order IDs = idempotency failure
```

**Fix:** Add idempotency key check: before processing, check if `event.id` has been processed. Use a `processed_events` table or Redis SET with event ID.

**Prevention:** Consumer idempotency is mandatory when using Outbox Pattern. Add to consumer onboarding checklist: "handle duplicate events by event ID."

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Transaction` - the Outbox Pattern relies on ACID transactions; without understanding atomic commits, the pattern's guarantee cannot be reasoned about
- `Idempotency` - the Outbox Pattern enables at-least-once delivery; consumers must be idempotent by design
- `CQRS Pattern` - Outbox is commonly used in CQRS architectures for reliable event emission from the write model

**Builds On This (learn these next):**
- `Change Data Capture (CDC)` - the Debezium-based implementation of the Outbox relay; CDC tails the database WAL to deliver outbox events without polling
- `Saga Pattern` - Sagas use Outbox for reliable step-by-step distributed workflow coordination; each saga step emits its event through the Outbox
- `Exactly-Once Semantics` - the advanced problem that Outbox's at-least-once delivery prompts engineers to explore

**Alternatives / Comparisons:**
- `Event Sourcing` - in Event Sourcing, the event log IS the state store; the Outbox Pattern is a compatibility layer for services that use separate state + event stores
- `Transactional Outbox` - a synonym for the Outbox Pattern; "Transactional" emphasises the ACID guarantee between the business write and the outbox insert

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Write event to outbox table in same DB    │
│              │ transaction - relay publishes to broker   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Dual-write problem: cannot atomically     │
│ SOLVES       │ commit to DB and publish to queue         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Database ACID solves the local problem.   │
│              │ Relay converts local to distributed.      │
│              │ Consumers must handle duplicates.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service publishes events to a broker AND  │
│              │ events must not be lost on partial failure│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Messages are best-effort (analytics,      │
│              │ metrics, non-critical logs)               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero message loss + resilience vs.        │
│              │ at-least-once delivery + relay complexity │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Writing the envelope and the letter in   │
│              │  one step - the postal worker does the    │
│              │  rest, reliably."                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CDC/Debezium → Saga Pattern →             │
│              │ Idempotency → Exactly-Once Semantics      │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When a business operation requires both a database change and
a message publication to be atomic, use the database as the
first-class message store. Write the message to the database
in the same transaction as the business change. Publish
asynchronously from the database.

**Where else this pattern appears:**
- **Write-Ahead Log (WAL) in databases:** The database first
  writes to the WAL (outbox) before modifying actual data pages.
  If the transaction rolls back, the WAL is ignored. This is
  the outbox pattern for database durability.
- **Email sending in e-commerce:** A best practice is to persist
  pending emails in the database within the order transaction,
  then send them asynchronously -- outbox prevents lost emails
  when the email service is temporarily down.
- **Audit log immutability:** Write audit log entries to the
  same transaction as the audited operation, not as a separate
  call -- the audit entry is the outbox for the audit system.

---

### 💡 The Surprising Truth

The Outbox Pattern is a rediscovery of a pattern used in
mainframe banking systems in the 1970s, called "reliable
messaging through persistent queues." Before microservices,
IBM MQ (MQSeries) implemented the same concept: messages were
persisted to stable storage before delivery, guaranteeing
at-least-once delivery even across system restarts. What is
"new" about the Outbox Pattern in microservices is the
solution to the dual-write problem using the application's own
database rather than a separate message queue -- using SQL
`COMMIT` as the atomicity boundary rather than a two-phase
commit across two separate systems.
---

### 🧠 Think About This Before We Continue

**Q1.** An order service uses the Outbox Pattern with a polling relay at 200ms intervals. A high-volume marketing event causes 10,000 orders in 5 seconds. The outbox relay processes 50 events per second normally. At peak, the outbox backlog grows to 10,000 messages, and events arrive at downstream services 200 seconds late. Design a solution that maintains the Outbox Pattern's reliability guarantee while reducing the maximum lag during burst traffic to under 10 seconds.

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A developer proposes replacing the Outbox Pattern with Kafka Transactions: "Kafka supports exactly-once semantics - we can write to Kafka transactionally and avoid the outbox table entirely." Evaluate this proposal: what does Kafka's exactly-once guarantee actually cover, what does it not cover for this scenario (order creation + event publishing), and under what conditions would Kafka Transactions be a valid replacement for the Outbox Pattern vs. when would it not?



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** An Outbox implementation uses
a polling scheduler that reads unpublished outbox records
every 100ms. Under normal load (100 events/minute) this
is fine. Under peak load (10,000 events/minute) the
scheduler falls behind, events are published with 5+ second
delay. Describe two architectural approaches to replace
polling with event-driven outbox draining, and explain
Debezium's CDC approach as a third option.

*Hint: The How It Works section shows polling as the standard
outbox drain mechanism. The event-driven alternatives are:
database trigger → message queue, and CDC log-based
streaming (Debezium reads the WAL).*
