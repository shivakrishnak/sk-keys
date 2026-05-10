---
version: 2
layout: default
title: "Outbox Pattern"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /messaging-streaming/outbox-pattern/
id: MSG-025
category: Messaging & Event Streaming
difficulty: ★★★
depends_on: Exactly-Once Semantics, Transactional Producer, Message Broker vs Event Bus
used_by: Reliable Event Publishing, Transactional Outbox, Event-Driven Architecture
related: Transactional Outbox, Dead Letter Queue, Event-Driven Architecture
tags:
  - outbox-pattern
  - dual-write
  - at-least-once
  - event-publishing
  - transactional-integrity
---

# MSG-025 - Outbox Pattern

⚡ TL;DR - **Outbox Pattern** solves the **dual-write problem**: writing to a DB and publishing to Kafka in a single request are NOT atomic (one can succeed, the other can fail → inconsistency); solution: write to both the **business table and an outbox table** in the **SAME DB transaction** → a separate **relay process** polls the outbox table and publishes to Kafka → **at-least-once guarantee**; requires **idempotent consumers** downstream (relay may republish on retry).

| #567            | Category: Big Data & Streaming                                              | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Exactly-Once Semantics, Transactional Producer, Message Broker vs Event Bus |                 |
| **Used by:**    | Reliable Event Publishing, Transactional Outbox, Event-Driven Architecture  |                 |
| **Related:**    | Transactional Outbox, Dead Letter Queue, Event-Driven Architecture          |                 |

---

### 🔥 The Problem This Solves

**THE DUAL-WRITE PROBLEM:**

```java
// BROKEN: two separate writes, no atomicity
@Transactional
public Order placeOrder(CreateOrderRequest request) {
    Order order = orderRepository.save(new Order(request));  // DB write: success
    kafkaTemplate.send("orders", order.getId(), new OrderEvent(order));  // Kafka: FAILS?

    // Scenario A: Kafka broker down
    //   DB: order saved ✓
    //   Kafka: message not published ✗
    //   Result: order in DB, no downstream notification → inconsistency

    // Scenario B: service crashes after DB commit, before Kafka publish
    //   DB: order saved ✓
    //   Kafka: message never sent ✗
    //   Result: same inconsistency

    // Scenario C: Kafka publish succeeds, DB rollback
    //   DB: order not saved ✗
    //   Kafka: ghost event published ✓
    //   Result: ghost events trigger downstream actions for non-existent orders

    return order;
}
// @Transactional wraps only the DB transaction - Kafka send is outside it
// Two-phase commit (XA transactions) could solve this but is slow and complex
// The Outbox Pattern is the standard solution
```

---

### 📘 Textbook Definition

**The Outbox Pattern** is a reliability pattern for event publishing in microservices that ensures atomic consistency between database writes and message broker publishing.

**How it works:**

1. **Write phase**: In a single DB transaction, write to the business table AND an `outbox_events` table.
2. **Relay phase**: A separate process polls the outbox table and publishes events to the broker.
3. **Cleanup phase**: After successful broker publish, mark outbox entry as `PUBLISHED` (or delete it).

**Properties:**

- **At-least-once delivery**: relay may retry on failure → possible duplicates → consumers must be idempotent.
- **No dual-write problem**: both writes are in the same DB transaction → atomically consistent.
- **Eventual consistency**: events published asynchronously (milliseconds to seconds delay) - not synchronous.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Outbox = write to DB + outbox table in ONE transaction; relay picks up outbox → publishes to Kafka; at-least-once (replay on retry); consumers must be idempotent.

**One analogy:**

> You need to send a letter AND file paperwork. The letter takes time to arrive. The outbox pattern: write the letter AND put a note in your outbox ledger simultaneously (atomic). A secretary (relay) periodically checks your outbox ledger → picks up the letter → mails it → marks it as sent. Even if the secretary is delayed: the note is there, the letter will be sent eventually. The filing and the letter are always consistent.

**One insight:**
The Outbox Pattern is the correct solution for the vast majority of "DB + Kafka must be consistent" use cases. It's simple (one extra table + one polling process), reliable (database-guaranteed), and doesn't require XA transactions or two-phase commit (which have catastrophic failure modes). The tradeoff: small latency (relay polling interval) and at-least-once (not exactly-once). For most business logic, idempotent consumers + at-least-once is acceptable and easier to reason about than exactly-once.

---

### 🔩 First Principles Explanation

**OUTBOX TABLE SCHEMA:**

```sql
CREATE TABLE outbox_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic       VARCHAR(255) NOT NULL,          -- Kafka topic to publish to
    message_key VARCHAR(255),                   -- Kafka partition key
    payload     JSONB NOT NULL,                 -- event payload
    headers     JSONB,                          -- optional Kafka headers
    status      VARCHAR(20) NOT NULL DEFAULT 'PENDING',  -- PENDING / PUBLISHED / FAILED
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at TIMESTAMP,                     -- set when published
    retry_count INT NOT NULL DEFAULT 0,

    INDEX idx_outbox_status_created (status, created_at)  -- relay query index
);
```

**OUTBOX WRITE (SAME TRANSACTION):**

```java
// Spring Boot implementation

@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    @GeneratedValue
    private UUID id;

    private String topic;
    private String messageKey;

    @Column(columnDefinition = "jsonb")
    private String payload;

    @Enumerated(EnumType.STRING)
    private OutboxStatus status = OutboxStatus.PENDING;

    private LocalDateTime createdAt = LocalDateTime.now();
    private LocalDateTime publishedAt;
    private int retryCount = 0;
}

@Repository
public interface OutboxEventRepository extends JpaRepository<OutboxEvent, UUID> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    List<OutboxEvent> findTop100ByStatusOrderByCreatedAtAsc(OutboxStatus status);
    // SELECT ... WHERE status='PENDING' ORDER BY created_at LIMIT 100 FOR UPDATE
    // FOR UPDATE: prevents multiple relay instances from picking up same events
}

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
        Order order = orderRepository.save(new Order(request));

        // Write 2: outbox entry (SAME transaction)
        OutboxEvent outboxEvent = new OutboxEvent();
        outboxEvent.setTopic("order-events");
        outboxEvent.setMessageKey(order.getId().toString());
        outboxEvent.setPayload(objectMapper.writeValueAsString(new OrderCreatedEvent(order)));
        outboxRepository.save(outboxEvent);

        // SINGLE @Transactional: BOTH writes commit together OR both rollback
        // If DB crashes: both rolled back → no inconsistency
        // Kafka not involved in this transaction (no dual-write problem)

        return order;
    }
}
```

**OUTBOX RELAY (POLLING):**

```java
@Component
public class OutboxRelay {

    @Autowired
    private OutboxEventRepository outboxRepository;

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    @Scheduled(fixedDelay = 500)  // poll every 500ms
    @Transactional
    public void relay() {
        // Fetch and lock pending events (pessimistic lock prevents concurrent relay instances):
        List<OutboxEvent> pendingEvents =
            outboxRepository.findTop100ByStatusOrderByCreatedAtAsc(OutboxStatus.PENDING);

        if (pendingEvents.isEmpty()) return;

        for (OutboxEvent event : pendingEvents) {
            try {
                // Publish to Kafka (synchronous send with acks=all):
                CompletableFuture<SendResult<String, String>> future = kafkaTemplate.send(
                    event.getTopic(),
                    event.getMessageKey(),
                    event.getPayload()
                );
                future.get(5, TimeUnit.SECONDS);  // wait for broker ack

                // Mark as published:
                event.setStatus(OutboxStatus.PUBLISHED);
                event.setPublishedAt(LocalDateTime.now());

            } catch (Exception e) {
                log.error("Failed to publish outbox event {}: {}", event.getId(), e.getMessage());
                event.setRetryCount(event.getRetryCount() + 1);

                if (event.getRetryCount() >= 5) {
                    event.setStatus(OutboxStatus.FAILED);
                    // Alert: manual intervention needed
                    alertService.sendAlert("Outbox event stuck: " + event.getId());
                }
            }
        }
        // Transaction commits: all status updates saved
    }
}

// CLEANUP: remove old PUBLISHED events (optional, keeps table lean)
@Scheduled(cron = "0 0 2 * * *")  // 2 AM daily
@Transactional
public void cleanup() {
    outboxRepository.deleteByStatusAndPublishedAtBefore(
        OutboxStatus.PUBLISHED,
        LocalDateTime.now().minusDays(7)
    );
}
```

**HANDLING RELAY IN PRODUCTION:**

```java
// Multi-instance relay: prevent duplicate publishing
// Problem: 3 relay instances all poll simultaneously → all pick same event → publish 3x

// SOLUTION 1: Pessimistic locking (shown above)
//   SELECT FOR UPDATE: only one instance acquires lock → others wait or skip
//   Good for: low relay instance count, simple setup

// SOLUTION 2: Kafka Streams processing guarantee (Transactional Outbox with Debezium)
//   See next entry (#568 - Transactional Outbox)
//   Better for: high volume, low latency, multiple relay instances

// SOLUTION 3: Optimistic lock with status check
//   Update: SET status='PROCESSING', locked_by=instanceId WHERE status='PENDING'
//   Only relay with matching locked_by processes and publishes

// MULTI-INSTANCE EXAMPLE (optimistic):
@Transactional
public void relay() {
    String instanceId = UUID.randomUUID().toString();

    // Claim batch (atomic update, no SELECT FOR UPDATE):
    int claimed = outboxRepository.claimBatch(instanceId, 100);
    if (claimed == 0) return;

    List<OutboxEvent> myEvents = outboxRepository.findByLockedBy(instanceId);
    // Process only events claimed by this instance
    // ...
}
```

---

### 🧪 Thought Experiment

**WHAT IF THE RELAY IS DOWN FOR 1 HOUR?**

Service is running, orders are being placed. All orders write to DB + outbox table. Relay is down (deployment). After 1 hour: relay recovers → reads all PENDING events in order → publishes all of them to Kafka → marks each as PUBLISHED. Downstream services receive all events (1 hour delayed but complete). No events lost, no inconsistency.

Compare to direct Kafka publish without outbox: 1 hour of Kafka broker downtime = 1 hour of orders without Kafka publishing = inconsistency. Some orders in DB with no events → downstream services never notified → manual reconciliation required.

The outbox decouples the publishing latency from the transactional integrity.

---

### 🧠 Mental Model / Analogy

> The outbox is like saving a letter draft before sending. You write the letter AND save the draft to "Outbox" folder (same action, atomic). An automated process (relay) periodically sends drafts. If the email server is down: draft stays in Outbox. When server recovers: draft gets sent. Database = letter filing. Outbox table = Outbox folder. Kafka = email server. Relay = email send daemon.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Outbox = write DB + outbox table in same TX → relay → Kafka → mark published. Solves dual-write. At-least-once (relay retries). Consumers must be idempotent.

**Level 2:** Outbox table: id, topic, key, payload, status, created_at. Relay: polls pending → publishes → marks published. Use `SELECT FOR UPDATE` to prevent multi-instance duplicates. Polling interval: 100ms–1s tradeoff between latency and DB load.

**Level 3:** Production concerns: (1) Outbox table grows: need cleanup (delete PUBLISHED after N days). (2) FAILED events: alert ops team (Kafka unreachable, serialization error). (3) Relay performance: process in batches (100 events/poll) not one-by-one. (4) Ordering: publish in `created_at` order to preserve event sequence. (5) Transaction isolation: relay `SELECT FOR UPDATE` within a transaction ensures atomicity of claim + status update.

**Level 4:** CDC-based relay (Transactional Outbox with Debezium): instead of polling, Debezium reads the DB transaction log (WAL/binlog) → captures INSERT to outbox_events → publishes to Kafka. Advantages: sub-millisecond latency (no polling interval), zero additional DB load (reads from replication slot), no FOR UPDATE lock contention. This is #568 - Transactional Outbox. The polling relay vs CDC relay tradeoff: polling is simpler (no Debezium infra), CDC is faster and more scalable.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ OUTBOX PATTERN FLOW                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│ OrderService.placeOrder():                          │
│   BEGIN TRANSACTION                                 │
│     INSERT INTO orders (id, ...) VALUES (...)       │
│     INSERT INTO outbox_events (topic, key, payload) │
│   COMMIT TRANSACTION  ← atomic: both or neither    │
│                                                      │
│ OutboxRelay @Scheduled(500ms):                      │
│   SELECT * FROM outbox_events                       │
│     WHERE status='PENDING' FOR UPDATE               │
│   → Publish to Kafka (wait for ack)                │
│   → UPDATE outbox_events SET status='PUBLISHED'    │
│   → COMMIT                                         │
│                                                      │
│ Consumer (OrderNotificationService):               │
│   @KafkaListener → receives event                  │
│   Check: already processed? (idempotency check)    │
│   If no: process, mark as processed                │
│                                                      │
│ Failure scenarios:                                  │
│   DB down: both writes fail, no partial state      │
│   Kafka down: outbox stays PENDING, relay retries  │
│   Relay crash: restarts, picks up PENDING events   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Full order lifecycle with Outbox Pattern:

09:00:01 - POST /orders → OrderService.placeOrder()
  TRANSACTION:
    INSERT orders (id='123', status='PLACED', amount=50.00) ✓
    INSERT outbox_events (topic='order-events', key='123',
                          payload='{"orderId":"123","amount":50}',
                          status='PENDING') ✓
  COMMIT ✓

09:00:01.200 - OutboxRelay polls (every 500ms):
  SELECT * FROM outbox_events WHERE status='PENDING' LIMIT 100 FOR UPDATE
  Finds: event id='abc', topic='order-events', key='123'
  kafkaTemplate.send('order-events', '123', '{...}')
  Kafka ACK received ✓
  UPDATE outbox_events SET status='PUBLISHED' WHERE id='abc'
  COMMIT ✓

09:00:01.250 - NotificationService @KafkaListener:
  Receives: OrderCreatedEvent {orderId: '123', amount: 50}
  Check: processedEvents.contains('123')? NO
  emailService.sendConfirmation('user@example.com')
  processedEvents.save('123')

Total latency: ~250ms (DB commit + poll + Kafka + consumer)
No data loss, no ghost events, no dual-write inconsistency

Crash scenario:
  Service crashes at 09:00:01.100 (after DB commit, relay not yet run)
  Service restarts
  OutboxRelay: finds PENDING event from before crash
  Publishes event → NotificationService processes (idempotency: already processed? NO)
  Event processed correctly despite crash
```

---

### ⚖️ Comparison Table

| Approach       | Dual Write       | Outbox (Polling)   | Outbox (CDC)             | XA Transactions |
| -------------- | ---------------- | ------------------ | ------------------------ | --------------- |
| Atomicity      | NO (can diverge) | YES (DB TX)        | YES (DB TX)              | YES             |
| Complexity     | Low              | Medium             | High (Debezium)          | High            |
| Latency        | Synchronous      | 100ms-1s           | Milliseconds             | Synchronous     |
| Exactly-once   | NO               | NO (at-least-once) | NO (at-least-once)       | YES             |
| Infrastructure | None             | Polling scheduler  | Debezium + Kafka Connect | XA coordinator  |
| DB performance | No overhead      | Polling overhead   | WAL read overhead        | Heavyweight     |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                                                                     |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Outbox Pattern gives exactly-once delivery"         | Outbox gives AT-LEAST-ONCE. The relay can publish and then crash before marking as PUBLISHED → publishes again on restart → duplicate. Consumers must be idempotent. Exactly-once requires Kafka transactions AND idempotent consumers (Transactional Outbox with Debezium) |
| "I can use @Transactional to wrap both DB and Kafka" | `@Transactional` only wraps the DB transaction. Kafka send is outside the DB transaction. The outbox table is the correct way to make both operations consistent                                                                                                            |
| "The Outbox Pattern adds too much latency"           | Polling relay adds 100-500ms latency (half the polling interval on average). For most business use cases (order notifications, emails, analytics) this is acceptable. For sub-10ms event publishing, use Debezium CDC (Transactional Outbox, #568)                          |

---

### 🚨 Failure Modes & Diagnosis

**1. Growing PENDING Backlog - Relay Stuck**

**Symptom:** `outbox_events` table has thousands of PENDING rows, increasing. Downstream services not receiving events.

**Root Cause:** Relay is down, or Kafka is unreachable.

**Diagnosis:**

```sql
-- Check PENDING backlog:
SELECT status, COUNT(*), MIN(created_at), MAX(created_at)
FROM outbox_events
GROUP BY status;
-- PENDING: 50000 rows from 2 hours ago → relay stuck

-- Check relay logs:
-- "Failed to publish: Connection to Kafka refused" → Kafka down
-- "Application is not running" → relay not deployed

-- Check retry_count to find stuck events:
SELECT id, topic, retry_count, created_at
FROM outbox_events
WHERE status IN ('PENDING', 'FAILED')
ORDER BY created_at
LIMIT 10;
```

**Fix:**

1. Fix Kafka connectivity → relay auto-recovers and processes backlog.
2. If relay process crashed → restart it → auto-processes PENDING.
3. If relay is running but Kafka unreachable > 1 hour: events with retry_count=5 → FAILED. Manual intervention: change FAILED back to PENDING → relay reprocesses.

---

### 🔗 Related Keywords

**Prerequisites:** Exactly-Once Semantics, Transactional Producer
**Builds On This:** Transactional Outbox (CDC-based)
**Related:** Transactional Outbox, Dead Letter Queue, Event-Driven Architecture

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PROBLEM     │ Dual-write: DB ✓ + Kafka ✗ = inconsistency│
│ SOLUTION    │ DB + outbox table in ONE transaction       │
│ RELAY       │ Polls outbox → publishes → marks done     │
│ GUARANTEE   │ At-least-once (relay may retry)           │
│ IDEMPOTENCY │ Consumer must deduplicate                 │
│ SCHEMA      │ id, topic, key, payload, status, created  │
│ LOCKING     │ SELECT FOR UPDATE (multi-relay instances) │
│ LATENCY     │ 100ms-1s (polling interval)               │
│ CLEANUP     │ Delete PUBLISHED events periodically      │
│ NEXT LEVEL  │ CDC (Debezium) → sub-ms latency (#568)   │
│ ONE-LINER   │ "Write outbox in same DB TX; relay        │
│             │  publishes to Kafka; at-least-once"      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the dual-write problem? How does the Outbox Pattern solve it? What consistency guarantee does it provide (exactly-once or at-least-once) and what does that require from consumers?

**Q2.** (TYPE C - Design) An order service writes orders to PostgreSQL and must publish `OrderCreatedEvent` to Kafka reliably. The service can crash at any point. Design the Outbox Pattern implementation: the outbox table schema, how the order service writes to it, how the relay process works, and how you handle failures (relay crash, Kafka downtime). What happens if the relay runs multiple instances simultaneously?
