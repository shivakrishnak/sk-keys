---
layout: default
title: "Outbox Pattern"
parent: "Design Patterns"
nav_order: 807
permalink: /design-patterns/outbox-pattern/
number: "807"
category: Design Patterns
difficulty: ★★★
depends_on: "Event-Driven Pattern, Distributed Systems, Database Fundamentals, ACID"
used_by: "Microservices, event sourcing, saga orchestration, reliable messaging"
tags: #advanced, #design-patterns, #distributed-systems, #messaging, #reliability, #microservices
---

# 807 — Outbox Pattern

`#advanced` `#design-patterns` `#distributed-systems` `#messaging` `#reliability` `#microservices`

⚡ TL;DR — **Outbox Pattern** solves the dual-write problem in distributed systems: atomically write to the database AND guarantee message delivery by storing the event in an outbox table within the same database transaction, then publishing asynchronously.

| #807 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event-Driven Pattern, Distributed Systems, Database Fundamentals, ACID | |
| **Used by:** | Microservices, event sourcing, saga orchestration, reliable messaging | |

---

### 📘 Textbook Definition

**Outbox Pattern** (also: Transactional Outbox Pattern; popularized by Chris Richardson, "Microservices Patterns", 2018): a microservices messaging pattern that guarantees at-least-once delivery of domain events without requiring distributed transactions (2PC). The pattern works by persisting domain events to an "outbox" table in the same database transaction as the domain state change, then having a separate message relay component read from the outbox and publish to a message broker. If the broker is unavailable, events remain in the outbox until they can be delivered. If the relay fails mid-publish, it republishes from the outbox on restart (idempotent consumers required). Ensures: events are published if and only if the DB transaction commits.

---

### 🟢 Simple Definition (Easy)

Problem: you update an order in the DB and publish an event to Kafka. The DB update succeeds. Kafka publish fails. Order is updated but nobody is notified. Or: the DB update fails after the Kafka publish. Event is published for a change that didn't actually happen. Outbox Pattern: save the event to a special table in the SAME transaction as the order update. A background job reads the event from that table and publishes it to Kafka. If the transaction fails: no event. If Kafka is down: the event waits in the table until Kafka recovers.

---

### 🔵 Simple Definition (Elaborated)

An e-commerce order service creates an order and must publish `OrderCreated` event to Kafka for downstream services (inventory, notification, analytics). Naive approach: `orderRepo.save(order)` then `kafkaTemplate.send("order-created", event)`. Problem: the two operations are not atomic — any failure between them leaves the system in an inconsistent state. Outbox Pattern: within one DB transaction, save the order AND insert an `OutboxEvent` record. A polling relay (or CDC tool like Debezium) reads uncommitted outbox records and publishes to Kafka, then marks as published. Atomicity at the DB level guarantees consistency.

---

### 🔩 First Principles Explanation

**The dual-write problem and the Outbox Pattern solution in depth:**

```
THE DUAL-WRITE PROBLEM:

  Service must do TWO things:
  1. Update DB state (order created)
  2. Publish event to message broker (OrderCreated)
  
  These two operations are in different systems → not atomic.
  
  FAILURE SCENARIOS:
  
  Scenario A: DB succeeds, Kafka fails
  → Order persisted. OrderCreated never published.
  → Inventory never decremented. Notification never sent.
  → State: order exists, downstream knows nothing.
  
  Scenario B: Kafka succeeds, DB fails (rollback)
  → OrderCreated published to Kafka.
  → Order does NOT exist in DB (transaction rolled back).
  → Downstream processes a phantom order.
  → State: event published for non-existent order.
  
  Both scenarios: data inconsistency.
  
OUTBOX PATTERN SOLUTION:

  Core insight: use the DB itself as the message staging area.
  The DB is ACID: use a local transaction to guarantee both writes atomically.
  
  Step 1: Create outbox table (same database as domain data):
  
  CREATE TABLE outbox_events (
      id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      aggregate_type VARCHAR(255) NOT NULL,    -- "Order", "Customer"
      aggregate_id   VARCHAR(255) NOT NULL,    -- order ID
      event_type     VARCHAR(255) NOT NULL,    -- "OrderCreated", "OrderCancelled"
      payload        JSONB NOT NULL,           -- serialized event data
      created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
      published_at   TIMESTAMPTZ,             -- NULL = not yet published
      sequence_no    BIGSERIAL                -- ordering within aggregate
  );
  
  Step 2: Domain service — one transaction, two writes:
  
  @Service
  @Transactional                               // one local transaction
  class OrderService {
      void createOrder(CreateOrderCommand cmd) {
          // Write 1: domain state
          Order order = new Order(cmd);
          orderRepository.save(order);
          
          // Write 2: outbox event (same transaction)
          OutboxEvent event = OutboxEvent.of(
              "Order",
              order.getId().toString(),
              "OrderCreated",
              objectMapper.writeValueAsString(new OrderCreatedEvent(order))
          );
          outboxRepository.save(event);
          
          // Either BOTH persist (transaction commits) or NEITHER (rollback).
          // No partial state possible.
      }
  }
  
  Step 3: Message Relay — reads outbox and publishes:
  
  OPTION A: Polling Relay (simpler, higher latency, more DB load):
  @Scheduled(fixedDelay = 1000)
  void relay() {
      List<OutboxEvent> unpublished = outboxRepo.findByPublishedAtIsNullOrderBySequenceNo();
      for (OutboxEvent event : unpublished) {
          kafkaTemplate.send(topicFor(event.getEventType()), event.getPayload()).get();
          event.markPublished();
          outboxRepo.save(event);
      }
  }
  
  OPTION B: Change Data Capture (CDC) with Debezium (lower latency, no polling):
  // Debezium reads PostgreSQL WAL (Write-Ahead Log) in real-time.
  // Detects INSERT on outbox_events table → publishes to Kafka automatically.
  // No polling. No additional DB load. Sub-second latency.
  // Configuration: Debezium Kafka Connect connector on the outbox table.
  
  Step 4: Consumer must be IDEMPOTENT (at-least-once delivery):
  // Relay may publish the same event twice (on failure/restart).
  // Consumers must handle duplicate events:
  
  @KafkaListener(topics = "order-created")
  void handleOrderCreated(OrderCreatedEvent event) {
      // Idempotent check: has this event been processed?
      if (processedEventRepository.existsById(event.getEventId())) {
          return;    // already processed — skip (idempotent)
      }
      
      // Process the event:
      inventoryService.reserve(event.getItems());
      
      // Mark as processed (in same transaction as inventory update):
      processedEventRepository.save(new ProcessedEvent(event.getEventId()));
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Outbox Pattern:
- Dual writes: DB and broker can diverge on any failure → inconsistent distributed state
- Either lost events or phantom events — both cause downstream failures

WITH Outbox Pattern:
→ Event delivery atomically linked to DB transaction. No lost events. No phantom events. Broker downtime: events queue in outbox until broker recovers. System is eventually consistent but always recoverable.

---

### 🧠 Mental Model / Analogy

> Sending a certified letter through a postal service: you drop the letter in the post office outbox (same trip as writing the letter). The letter sits there until the postal service picks it up and delivers it. If the postal service is temporarily closed: letter waits in the outbox. If your house burns down before you drop the letter: no letter exists. The letter is only in the outbox after you physically deposit it — and the post office guarantees delivery once it's deposited.

"Writing the letter and depositing it in the outbox in one trip" = DB transaction writes domain state AND outbox event atomically
"Letter waits in outbox until postal service picks it up" = event waits in outbox table until relay publishes it to Kafka
"If postal service closed: letter waits" = if Kafka down: event persists in outbox until Kafka recovers
"If house burns before depositing: no letter" = if DB transaction rolls back: no event in outbox
"Postal service guarantees delivery once deposited" = relay guarantees at-least-once delivery of outbox events

---

### ⚙️ How It Works (Mechanism)

```
OUTBOX PATTERN ARCHITECTURE:

  ┌─────────────────────────────────────────────────┐
  │  Order Service                                  │
  │                                                 │
  │  @Transactional                                 │
  │  createOrder() {                                │
  │    orderRepo.save(order)     ──────┐            │
  │    outboxRepo.save(event)    ──────┤            │
  │  }                                │            │
  └───────────────────────────────────┼────────────┘
                                      │ ONE TRANSACTION
                                      ▼
  ┌─────────────────────────────────────────────────┐
  │  PostgreSQL                                     │
  │  ┌──────────────┐  ┌────────────────────────┐  │
  │  │ orders table │  │ outbox_events table     │  │
  │  │              │  │  id, event_type,        │  │
  │  │ id, status,  │  │  payload, published_at  │  │
  │  │ customer_id  │  │  (NULL = pending)       │  │
  │  └──────────────┘  └───────────┬────────────┘  │
  └──────────────────────────────────┼──────────────┘
                                      │
                   ┌──────────────────┴────────────────┐
                   │                                   │
           OPTION A:                           OPTION B:
           Polling Relay                       CDC (Debezium)
           @Scheduled                          Reads PostgreSQL WAL
           findByPublishedAtIsNull()           Detects INSERT on outbox_events
                   │                                   │
                   └──────────────────┬────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────┐
  │  Apache Kafka                                   │
  │  Topic: order-created                           │
  │  Topic: order-cancelled                         │
  └─────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
Dual-write problem (DB + Broker not atomic) → Outbox Pattern solves with local transaction
        │
        ▼
Outbox Pattern ◄──── (you are here)
(atomic write to DB + outbox; relay publishes at-least-once; consumer must be idempotent)
        │
        ├── Transactional Outbox: more specific variant (see 816)
        ├── Saga Pattern: Outbox is used within saga steps for reliable event publishing
        ├── Event-Driven Pattern: Outbox enables reliable event-driven architecture
        └── Idempotent Consumer: required pairing — at-least-once delivery needs idempotent consumers
```

---

### 💻 Code Example

```java
// Spring Boot Outbox Pattern implementation:

// Outbox entity:
@Entity
@Table(name = "outbox_events")
@Getter @NoArgsConstructor
public class OutboxEvent {
    @Id @GeneratedValue
    private UUID id;
    
    @Column(nullable = false)
    private String aggregateType;
    
    @Column(nullable = false)
    private String aggregateId;
    
    @Column(nullable = false)
    private String eventType;
    
    @Column(columnDefinition = "jsonb", nullable = false)
    private String payload;
    
    @Column(nullable = false)
    private Instant createdAt = Instant.now();
    
    private Instant publishedAt;   // null = not yet published
    
    public static OutboxEvent of(String aggregateType, String aggregateId,
                                  String eventType, String payload) {
        OutboxEvent e = new OutboxEvent();
        e.aggregateType = aggregateType;
        e.aggregateId = aggregateId;
        e.eventType = eventType;
        e.payload = payload;
        return e;
    }
    
    public void markPublished() { this.publishedAt = Instant.now(); }
}

// Service — atomic order + outbox write:
@Service @RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepo;
    private final OutboxEventRepository outboxRepo;
    private final ObjectMapper mapper;
    
    @Transactional
    public Order createOrder(CreateOrderCommand cmd) {
        Order order = new Order(cmd.getCustomerId(), cmd.getItems(), cmd.getTotal());
        orderRepo.save(order);
        
        // Publish to outbox — same transaction as order creation:
        String payload = mapper.writeValueAsString(
            new OrderCreatedEvent(order.getId(), order.getCustomerId(), order.getTotal()));
        outboxRepo.save(OutboxEvent.of("Order", order.getId().toString(),
                                        "OrderCreated", payload));
        
        return order;   // transaction commits: BOTH order AND outbox row persisted
    }
}

// Message relay (polling approach):
@Component @RequiredArgsConstructor
@Slf4j
public class OutboxMessageRelay {
    private final OutboxEventRepository outboxRepo;
    private final KafkaTemplate<String, String> kafka;
    
    @Scheduled(fixedDelay = 500)   // poll every 500ms
    @Transactional
    public void relay() {
        outboxRepo.findTop100ByPublishedAtIsNullOrderByCreatedAtAsc()
            .forEach(this::publish);
    }
    
    private void publish(OutboxEvent event) {
        try {
            String topic = event.getEventType().toLowerCase().replace(".", "-");
            kafka.send(topic, event.getAggregateId(), event.getPayload()).get();
            event.markPublished();
            outboxRepo.save(event);
        } catch (Exception e) {
            log.error("Failed to publish outbox event {}: {}", event.getId(), e.getMessage());
            // Leave publishedAt null → will retry on next poll
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The Outbox Pattern guarantees exactly-once delivery | The Outbox Pattern guarantees at-least-once delivery. If the relay publishes the event and then crashes before marking it as published, the event will be re-published on restart. Consumers must be idempotent to handle duplicates. Exactly-once delivery in distributed systems requires additional mechanisms (e.g., Kafka transactions + idempotent producers + transactional consumers). |
| CDC (Debezium) is always better than polling relay | Both have tradeoffs. Polling relay: simpler, no additional infrastructure, higher latency (depends on polling interval), more DB load. CDC (Debezium + Kafka Connect): lower latency (WAL-based), less DB load, but requires additional infrastructure (Kafka Connect cluster), more operational complexity. For teams starting out: polling relay is simpler. At scale: CDC is preferable. |
| The Outbox Pattern requires a separate microservice | The relay can be an `@Scheduled` component in the same service. Many implementations run the relay as a background thread in the producing service. A dedicated relay service (separate deployment) is only needed when the relay itself needs to scale independently or when multiple services share a relay infrastructure. |

---

### 🔥 Pitfalls in Production

**Outbox table growing unbounded due to missing cleanup:**

```java
// ANTI-PATTERN — outbox table with no cleanup:
// After 6 months of production:
// SELECT COUNT(*) FROM outbox_events WHERE published_at IS NOT NULL;
// → 50,000,000 rows
// Query for unpublished: full table scan → 30 seconds
// @Scheduled relay: timing out
// DB disk: 80% full
//
// FIX 1: Partition the table by published_at (PostgreSQL partitioning)
// FIX 2: Add cleanup job:

@Scheduled(cron = "0 0 2 * * *")   // 2am daily
@Transactional
public void cleanupPublishedEvents() {
    int deleted = outboxRepo.deleteByPublishedAtBeforeAndPublishedAtIsNotNull(
        Instant.now().minus(7, ChronoUnit.DAYS)
    );
    log.info("Cleaned up {} published outbox events older than 7 days", deleted);
}

// FIX 3: Index on published_at to speed up relay query:
// CREATE INDEX CONCURRENTLY idx_outbox_unpublished
//     ON outbox_events (created_at) WHERE published_at IS NULL;
// Partial index: only on unpublished rows → small, fast.

// MONITORING: alert if unpublished outbox events count > threshold
// SELECT COUNT(*) FROM outbox_events WHERE published_at IS NULL AND created_at < NOW() - INTERVAL '5 minutes';
// > 100: relay may be stuck. Page on-call.
```

---

### 🔗 Related Keywords

- `Event-Driven Pattern` — Outbox Pattern enables reliable event-driven architecture
- `Saga Pattern` — Outbox used within saga steps for reliable compensation event publishing
- `Transactional Outbox` — the formal name (816), a specific refinement of this pattern
- `Idempotent Consumer` — required pairing: at-least-once delivery requires idempotent consumers
- `Change Data Capture (CDC)` — Debezium-based alternative to polling for outbox event relay

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Atomic write: domain state + outbox event │
│              │ in ONE DB transaction. Relay publishes   │
│              │ asynchronously. No dual-write problem.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Microservice must update DB AND publish  │
│              │ event reliably; broker may be unavailable;│
│              │ eventual consistency is acceptable        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Same-process, in-memory communication;   │
│              │ synchronous response needed from consumer;│
│              │ exactly-once required (use Kafka txns)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Drop the letter in the post office      │
│              │  outbox. It waits until the postal       │
│              │  service picks it up — guaranteed."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Transactional Outbox → Saga → CDC →      │
│              │ Idempotent Consumer → Event-Driven Pattern│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Outbox Pattern guarantees at-least-once delivery. Many distributed system guarantees (Kafka, SQS) also provide at-least-once delivery. The design implication: every consumer of events must be idempotent — processing the same event twice must produce the same result as processing it once. How do you design an idempotent Kafka consumer in Spring Boot? Describe at minimum: (a) the deduplication check, (b) where the "processed" record is stored, (c) how the idempotency check and the actual processing are made atomic.

**Q2.** Debezium reads the database's Write-Ahead Log (WAL) to detect changes — including inserts to the outbox table. This is called Change Data Capture (CDC). In PostgreSQL, the WAL records every committed transaction. Debezium's Kafka Connect connector tails the WAL and publishes changes. But WAL retention has a limit: if Debezium falls behind (broker down, connector lag), the WAL segment may be recycled before Debezium reads it — losing events. How does Debezium handle WAL retention, and what configuration prevents event loss if the connector has extended downtime?
