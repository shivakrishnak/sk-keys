---
layout: default
title: "Event-Driven Microservices"
parent: "Microservices"
nav_order: 655
permalink: /microservices/event-driven-microservices/
number: "655"
category: Microservices
difficulty: ★★★
depends_on: "Synchronous vs Async Communication, Saga Pattern (Microservices)"
used_by: "Eventual Consistency (Microservices), Event Sourcing in Microservices, CQRS in Microservices"
tags: #advanced, #microservices, #distributed, #messaging, #architecture, #pattern
---

# 655 — Event-Driven Microservices

`#advanced` `#microservices` `#distributed` `#messaging` `#architecture` `#pattern`

⚡ TL;DR — **Event-Driven Microservices** architecture uses **domain events** published to a message broker (Kafka, RabbitMQ) as the primary integration mechanism between services. Services are loosely coupled: producers publish events without knowing consumers. Enables: temporal decoupling, independent scalability, and event replay. Trade-off: eventual consistency and increased operational complexity.

| #655            | Category: Microservices                                                                      | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Synchronous vs Async Communication, Saga Pattern (Microservices)                             |                 |
| **Used by:**    | Eventual Consistency (Microservices), Event Sourcing in Microservices, CQRS in Microservices |                 |

---

### 📘 Textbook Definition

**Event-Driven Microservices** is an architectural style in which microservices communicate primarily through **domain events** — facts about something that happened in the business domain (e.g., `OrderPlaced`, `PaymentProcessed`, `InventoryDepleted`). Services produce events (facts about their own state changes) and consume events from other services, without direct point-to-point dependencies. Events are published to a **message broker** or **event streaming platform** (Kafka, RabbitMQ, AWS EventBridge) which decouples producers from consumers in both time and space. Core properties: **temporal decoupling** — producer and consumer need not be running simultaneously; **spatial decoupling** — producer doesn't know the consumer's address or even existence; **loose coupling** — adding a new consumer requires no changes to the producer. Event-driven architecture can implement: simple pub/sub notifications (fans out to N subscribers), event-carried state transfer (event contains full state, consumer updates its own projection), and event sourcing (events as the system of record). Event streams can be replayed to reconstruct state or add new consumers retroactively.

---

### 🟢 Simple Definition (Easy)

Event-Driven Microservices: when something important happens (order placed, payment received), a service publishes a message describing what happened. Other services listen for these messages and react. No direct service-to-service calls — only messages through a broker. This makes services independent: they don't need to know about each other, and they can process events at their own pace.

---

### 🔵 Simple Definition (Elaborated)

When an order is placed in `OrderService`, instead of calling `InventoryService`, `PaymentService`, `NotificationService`, and `AnalyticsService` directly (4 synchronous calls = 4 potential failures), `OrderService` publishes one `OrderPlaced` event to Kafka. Each interested service subscribes and reacts: `InventoryService` reserves stock, `PaymentService` initiates charge, `NotificationService` sends email, `AnalyticsService` records the conversion. `OrderService` doesn't know about any of them — it just published the fact. Adding a new `LoyaltyService` requires zero changes to `OrderService` — it simply subscribes to the existing `order-placed-events` topic.

---

### 🔩 First Principles Explanation

**Event types — not all "events" are the same:**

```
1. DOMAIN EVENT (fact about business state change):
  Naming: past tense ("OrderPlaced", "PaymentFailed", "ProductShipped")
  Content: business data relevant to the fact
  Producer: knows what happened; doesn't know who cares
  Consumer: decides what to do with the fact
  Example:
  {
    "eventType": "OrderPlaced",
    "orderId": "ord-123",
    "customerId": "cust-456",
    "productId": "prod-789",
    "quantity": 2,
    "totalAmount": 49.99,
    "placedAt": "2024-01-15T10:30:00Z"
  }

2. COMMAND EVENT (request to do something — less pure):
  Naming: imperative ("ReserveInventory", "ProcessPayment")
  Content: parameters for the action
  Consumer: expected to perform the action
  Note: commands imply coupling (you're telling someone what to do)
  Pure event-driven purists avoid explicit commands as events
  Better: choreography uses domain events, not commands

3. EVENT-CARRIED STATE TRANSFER (full state in event):
  Event contains full current state of entity (not just delta)
  Consumer doesn't need to query producer to get current state
  Example:
  {
    "eventType": "ProductUpdated",
    "productId": "prod-789",
    "currentState": {   ← entire product state
      "name": "Widget Pro",
      "price": 49.99,
      "stock": 100,
      "category": "Electronics"
    }
  }
  Consumer: updates its local projection directly from event
  Benefit: consumer is fully autonomous (no API calls to producer)
  Cost: large events; stale local projection until next event
```

**Event schema evolution — the hard problem:**

```
PRODUCER changes the event schema:
  v1: {"orderId": "123", "amount": 49.99}
  v2: {"orderId": "123", "amount": 49.99, "currency": "USD"}  ← new field
  v3: {"orderId": "123", "totalAmount": 49.99, "currency": "USD"}  ← renamed field

CONSUMER compatibility:
  FORWARD compatible: new producer + old consumer
  v2 event with "currency" field → old consumer ignores "currency" → OK (additive)

  BACKWARD compatible: old producer + new consumer
  Old event without "currency" → new consumer handles null/default → OK

  BREAKING change: renamed field ("amount" → "totalAmount")
  Old consumer reads "amount" = null → BROKEN

STRATEGIES:
  1. Schema Registry (Confluent Schema Registry + Avro/Protobuf):
     - Producer registers schema version with registry
     - Consumer validates event against registered schema
     - Registry enforces compatibility rules (BACKWARD, FORWARD, FULL)
     - Prevents incompatible schema changes from being published

  2. Versioned topics: "order-placed-events-v1", "order-placed-events-v2"
     - Run both topics in parallel during migration
     - Old consumers: read from v1, New consumers: read from v2
     - Producer publishes to both until all consumers migrated

  3. Event envelope with version:
     {"version": "2", "eventType": "OrderPlaced", "payload": {...}}
     Consumer branches on version: v1 parser vs v2 parser

  4. Additive-only schema changes:
     Never rename or remove fields
     Only add optional fields with defaults
     → Maintains forward + backward compatibility indefinitely
```

**Consumer group patterns — who gets what:**

```
KAFKA CONSUMER GROUPS:
  Each consumer group receives a COPY of every message
  Within a group: each partition consumed by ONE consumer (horizontal scaling)

PATTERN 1: Pub/Sub (multiple groups, each gets all messages):
  Topic: "order-placed-events"
  Group "inventory-service": all 3 inventory instances consume together
  Group "payment-service": all 5 payment instances consume together
  Group "notification-service": all 2 notification instances consume together
  → Each group independently processes all events
  → Adding new service group: zero changes to producer or other consumers

PATTERN 2: Work Queue (single group, load distributed):
  Topic: "payment-processing-queue" (only PaymentService consumes)
  Group "payment-service": 5 instances
  Each partition assigned to one instance
  → 5 instances process events in parallel (horizontal scaling of processing)

PATTERN 3: Event Replay (new service onboarding):
  New "AuditService" needs ALL past order events:
  → Create new consumer group "audit-service"
  → Set auto.offset.reset=earliest
  → Kafka replays all retained events (7 days default, configurable forever)
  → AuditService processes historical events + live events
  → OrderService made zero changes to enable this
```

---

### ❓ Why Does This Exist (Why Before What)

In a synchronous microservices system with N services all calling each other, you have O(N²) potential dependencies. Adding a new consumer means updating the producer to call it. One slow consumer blocks the producer. One unavailable consumer fails the producer. Event-driven architecture reduces this to O(N) dependencies (each service only depends on the message broker) and temporal decoupling (consumers process at their own pace). The key insight: "I don't need to call you directly; I just need to tell the world that something happened."

---

### 🧠 Mental Model / Analogy

> Event-Driven Microservices is like a newspaper broadcast model. When a significant event happens (election results), a newspaper prints the story and publishes it. Millions of readers can subscribe and read at their own pace — some read immediately, some read tomorrow, some save archives for research. The newspaper doesn't know or care who is reading. Adding a new reader doesn't require the newspaper to change. If a reader is unavailable (asleep), they can catch up when they return (message retention). Compare to phone calls (synchronous): you can only call one person at a time, both must be present, and you need to know each person's number.

"Newspaper" = event producer publishing to Kafka
"Story printed" = domain event (fact about what happened)
"Readers subscribing" = consumer services subscribing to topic
"Reading tomorrow" = temporal decoupling (consumer processes when available)
"Archive for research" = Kafka event retention (replay historical events)

---

### ⚙️ How It Works (Mechanism)

**Spring Boot Kafka — producer and multiple consumers:**

```java
// EVENT DEFINITION (shared library or per-service):
record OrderPlacedEvent(
    String eventId,           // UUID for deduplication
    String orderId,
    String customerId,
    Long productId,
    int quantity,
    BigDecimal totalAmount,
    Instant placedAt
) {}

// PRODUCER (OrderService — only knows about the event, not consumers):
@Service
class OrderService {
    @Autowired KafkaTemplate<String, OrderPlacedEvent> kafkaTemplate;

    @Transactional  // with Outbox pattern: same transaction as order creation
    public Order placeOrder(CreateOrderRequest request) {
        Order order = orderRepository.save(new Order(request));

        kafkaTemplate.send("order-placed-events",
            order.getId().toString(),   // partition key: orderId
            new OrderPlacedEvent(
                UUID.randomUUID().toString(),
                order.getId().toString(),
                request.getCustomerId(),
                request.getProductId(),
                request.getQuantity(),
                order.getTotalAmount(),
                Instant.now()
            ));
        return order;
    }
}

// CONSUMER 1 (InventoryService — reacts to event, updates its own DB):
@Service
class InventoryEventConsumer {
    @KafkaListener(topics = "order-placed-events", groupId = "inventory-service")
    @Transactional
    void handleOrderPlaced(OrderPlacedEvent event) {
        inventoryService.reserve(event.productId(), event.quantity(), event.orderId());
    }
}

// CONSUMER 2 (NotificationService — also reacts, independently):
@Service
class NotificationEventConsumer {
    @KafkaListener(topics = "order-placed-events", groupId = "notification-service")
    void handleOrderPlaced(OrderPlacedEvent event) {
        emailService.sendOrderConfirmation(event.customerId(), event.orderId());
    }
}
// OrderService: zero awareness of InventoryService or NotificationService
```

---

### 🔄 How It Connects (Mini-Map)

```
Synchronous vs Async Communication
(async = event-driven path)
        │
        ▼
Event-Driven Microservices  ◄──── (you are here)
(domain events via message broker)
        │
        ├── Saga Pattern → events as the coordination mechanism for sagas
        ├── Eventual Consistency → consequence of async event processing
        ├── Event Sourcing in Microservices → events as the system of record
        └── CQRS in Microservices → events update read-side projections
```

---

### 💻 Code Example

**Event-Carried State Transfer — consumer self-sufficient projection:**

```java
// InventoryService maintains its own read-projection of product prices
// from ProductService events (no API calls needed):

@Entity
class ProductPriceProjection {
    @Id String productId;
    BigDecimal currentPrice;
    Instant lastUpdated;
}

@KafkaListener(topics = "product-updated-events", groupId = "inventory-price-projection")
@Transactional
void updatePriceProjection(ProductUpdatedEvent event) {
    // Update local projection from event-carried state:
    productPriceProjectionRepository.save(new ProductPriceProjection(
        event.getProductId(),
        event.getCurrentState().getPrice(),  // full state in event
        event.getUpdatedAt()
    ));
}

// Now InventoryService can calculate order totals without calling ProductService:
BigDecimal price = productPriceProjectionRepository
    .findById(productId)
    .map(ProjectedPriceView::getCurrentPrice)
    .orElse(null);  // if null: ProductUpdated event not yet received → fallback
```

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                                              |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Event-driven means all communication is asynchronous | Even in event-driven systems, some operations require synchronous responses (user-facing reads, real-time validation). Event-driven architecture complements synchronous calls — it doesn't replace them for all interactions                        |
| The message broker is just a pass-through            | The broker (Kafka) is a critical infrastructure component. Events are persisted in the broker for the retention period. Broker availability, partition count, replication factor, and retention configuration directly impact system behaviour       |
| Event-driven services are automatically idempotent   | Kafka delivers events at-least-once. Consumers WILL receive duplicate events. Every consumer must implement idempotency (check if event was already processed using eventId before processing)                                                       |
| Event ordering is guaranteed globally                | Kafka guarantees ordering only within a partition. Events for the same entity (e.g., same orderId) must be published to the same partition (use orderId as partition key) to guarantee ordering. Global ordering across partitions is not guaranteed |

---

### 🔥 Pitfalls in Production

**Consumer lag monitoring — unprocessed events accumulate silently**

```
SCENARIO:
  Order surge: 100,000 "OrderPlaced" events published in 10 minutes.
  NotificationService (email) can process 500 events/minute.
  Consumer lag grows: 100,000 events / 500/min = 200 minutes to catch up.
  Customers wait 3+ hours for order confirmation emails.
  No alert fires: events are queuing, NotificationService is "healthy".

DETECTION:
  Monitor consumer lag:
  kafka.consumer.lag{topic="order-placed-events", group="notification-service"} > 10000
  → Alert: "Notification consumer lag exceeds 10,000 events"

  Tools:
  - Kafka UI / Kafdrop: visual consumer lag
  - Burrow (LinkedIn): sophisticated lag monitoring with trend analysis
  - Prometheus + kafka-exporter: consumer_lag metric per group/topic/partition

RESOLUTION:
  1. Scale consumers: add more NotificationService replicas (up to partition count)
     Kafka: each partition processed by one consumer in a group
     If topic has 12 partitions → max 12 parallel consumers in same group

  2. Process-time SLA:
     Set SLA: "all order confirmation emails sent within 5 minutes"
     Alert: lag > (300 events × 5 minutes SLA = ~150 events behind)

  3. Priorities: fast-path for critical events (payments) vs batch for analytics
     Separate topics: "order-placed-critical" (fast, few partitions) vs
                      "order-placed-analytics" (high-throughput, many partitions)
```

---

### 🔗 Related Keywords

- `Synchronous vs Async Communication` — event-driven uses the async path
- `Saga Pattern (Microservices)` — uses domain events for multi-service workflow coordination
- `Eventual Consistency (Microservices)` — the data model consequence of event-driven architecture
- `Event Sourcing in Microservices` — treats events as the source of truth (not derived state)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA    │ Publish facts; consumers react            │
│ DECOUPLING   │ Temporal + spatial (no direct calls)     │
│ BROKER       │ Kafka (streaming), RabbitMQ (queue)       │
├──────────────┼───────────────────────────────────────────┤
│ BENEFITS     │ Independent scalability, replay,          │
│              │ add consumers with zero producer change   │
├──────────────┼───────────────────────────────────────────┤
│ REQUIREMENTS │ Idempotent consumers (at-least-once)     │
│              │ Schema evolution strategy (registry)      │
│              │ Consumer lag monitoring + alerting        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team migrates from synchronous REST calls to event-driven architecture. `OrderService` previously called `InventoryService` synchronously and could immediately know if an item was out of stock (400 response) before confirming the order. With events, `OrderService` publishes `OrderPlaced` and `InventoryService` asynchronously reserves stock. If the item is out of stock, `InventoryService` publishes `InventoryReservationFailed`. But the customer has already received "Order confirmed!" How do you design the UX to handle this asynchronous validation failure? What is the "optimistic order placement" pattern, and what are its business trade-offs?

**Q2.** Kafka guarantees ordering within a partition but not across partitions. Your `order-placed-events` topic has 12 partitions. A customer places Order A, then Order B in quick succession. With `orderId` as the partition key, Orders A and B hash to different partitions. `InventoryService` processes Order B first (partition 3 processed faster than partition 7). Both orders try to reserve the last item in stock. Describe the race condition: which order gets the item, and how does the losing order know to compensate? What partition key strategy ensures all orders for the same product are serialised?
