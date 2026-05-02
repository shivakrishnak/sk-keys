---
layout: default
title: "Event-Driven Pattern"
parent: "Design Patterns"
nav_order: 818
permalink: /design-patterns/event-driven-pattern/
number: "818"
category: Design Patterns
difficulty: ★★★
depends_on: "CQRS Pattern, Saga Pattern, Outbox Pattern, Apache Kafka"
used_by: "Microservices, asynchronous communication, real-time systems, domain decoupling"
tags: #advanced, #design-patterns, #architecture, #microservices, #events, #kafka, #async
---

# 818 — Event-Driven Pattern

`#advanced` `#design-patterns` `#architecture` `#microservices` `#events` `#kafka` `#async`

⚡ TL;DR — **Event-Driven Pattern** enables asynchronous, decoupled service communication by publishing events (facts about what happened) to a broker; consumers react independently without the publisher knowing who — or how many — are listening.

| #818            | Category: Design Patterns                                                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | CQRS Pattern, Saga Pattern, Outbox Pattern, Apache Kafka                        |                 |
| **Used by:**    | Microservices, asynchronous communication, real-time systems, domain decoupling |                 |

---

### 📘 Textbook Definition

**Event-Driven Architecture (EDA)** / **Event-Driven Pattern**: an architectural and design pattern in which components communicate by producing, routing, and consuming events. An event represents a significant state change or occurrence in the system (fact: something happened — immutable, past tense). Publishers emit events without knowledge of consumers. Consumers react to events independently and asynchronously. Key broker: Apache Kafka (durable, ordered, partitioned log). Alternatives: RabbitMQ (message-oriented), AWS EventBridge (cloud-native). Key differentiator from message-driven: events are facts (what happened); messages are commands/requests (do this). CloudEvents (CNCF standard): portable event envelope schema across clouds and brokers.

---

### 🟢 Simple Definition (Easy)

Order Service: "An order was placed" (event published to Kafka). Inventory Service: "I'll reserve the items." Notification Service: "I'll send the confirmation email." Analytics Service: "I'll record this for reporting." Order Service doesn't know any of these consumers exist. New consumer (e.g., Fraud Service) added: subscribes to the same event — no change to Order Service. Completely decoupled. Order Service just says "this happened" and moves on.

---

### 🔵 Simple Definition (Elaborated)

Synchronous API call: Order Service calls Inventory Service's REST endpoint directly. Coupling: Order Service must know Inventory Service's URL, must wait for its response, fails if Inventory is down. Event-driven: Order Service publishes `OrderPlaced` event to Kafka topic. Inventory Service subscribes to that topic and processes whenever it's ready. If Inventory is down: Kafka retains the event; Inventory processes when it recovers. Order Service: no coupling to Inventory's availability, no knowledge of Inventory's URL. Add a new consumer: subscribe to the topic — zero changes to any existing service.

---

### 🔩 First Principles Explanation

**Event schema, Spring Boot Kafka integration, and CloudEvents:**

```
KAFKA FUNDAMENTALS (brief):

  Topic: named, ordered, durable log (e.g., "order-events")
  Partition: topic split into N partitions; messages within a partition ordered
  Key: determines partition (same key → same partition → ordered for that key)
  Consumer Group: group of consumers sharing a topic's partitions
  Offset: position of each consumer in each partition
  Retention: Kafka retains events for configured duration (default 7 days) regardless of consumption

  Kafka vs. RabbitMQ:
  Kafka: durable log, multiple independent consumer groups, replay from offset, high throughput
  RabbitMQ: message queue, message deleted after acknowledgement, one consumer per message (by default)

  EVENT SCHEMA — CLOUDEVENTS STANDARD:

  {
    "specversion": "1.0",
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "source": "//order-service/orders",
    "type": "com.example.orders.v1.OrderPlaced",
    "datacontenttype": "application/json",
    "time": "2024-01-15T14:30:00Z",
    "data": {
      "orderId": "order-123",
      "customerId": "cust-456",
      "total": 99.99,
      "items": [...]
    }
  }

  CloudEvents: CNCF standard envelope. Benefits: portable across brokers (Kafka, EventBridge,
  Pub/Sub), tooling support (Knative Eventing), event versioning via type field.

SPRING BOOT KAFKA PRODUCER:

  // Producer:
  @Service @RequiredArgsConstructor
  public class OrderEventPublisher {
      private final KafkaTemplate<String, OrderPlacedEvent> kafkaTemplate;

      public void publishOrderPlaced(Order order) {
          OrderPlacedEvent event = new OrderPlacedEvent(
              order.getId(), order.getCustomerId(),
              order.getItems(), order.getTotal());

          // Key = orderId: ensures all events for same order go to same partition (ordering)
          kafkaTemplate.send("order-events", order.getId().toString(), event);
      }
  }

SPRING BOOT KAFKA CONSUMER:

  @Service
  @KafkaListener(topics = "order-events", groupId = "inventory-service")
  public class InventoryEventConsumer {

      @KafkaHandler
      public void on(OrderPlacedEvent event) {
          // Reserve inventory for this order:
          inventoryService.reserve(event.getOrderId(), event.getItems());
      }
  }

  // Multiple independent consumer groups:
  // Inventory Service: groupId = "inventory-service"  → processes its own offset
  // Notification Service: groupId = "notification-service" → processes its own offset
  // Analytics Service: groupId = "analytics-service"   → processes its own offset
  // Each group gets ALL events — complete fan-out (broadcast) at no extra cost.

KAFKA CONFIGURATION (application.yml):

  spring:
    kafka:
      bootstrap-servers: kafka:9092
      producer:
        key-serializer: org.apache.kafka.common.serialization.StringSerializer
        value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
        acks: all        # wait for leader + all ISR replicas to ack → durability
        retries: 3
        properties:
          enable.idempotence: true    # Exactly-once producer semantics (no duplicates on retry)
      consumer:
        key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
        value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
        auto-offset-reset: earliest  # On new group: start from beginning of topic
        enable-auto-commit: false    # Manual ack: commit offset only after successful processing
        properties:
          spring.json.trusted.packages: "com.example.events"

DEAD LETTER TOPIC (DLT):

  // Configure DLT for failed message handling:
  @Bean
  public DefaultErrorHandler errorHandler(KafkaTemplate<?, ?> template) {
      DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(template,
          (r, e) -> new TopicPartition(r.topic() + ".DLT", r.partition()));

      // Retry 3 times with exponential backoff; then send to DLT:
      FixedBackOff backOff = new FixedBackOff(1000L, 3);  // 1s interval, 3 attempts
      return new DefaultErrorHandler(recoverer, backOff);
  }
  // Message in DLT: manual investigation and replay required.
  // Alert: if DLT topic has messages → processing failures needing investigation.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Event-Driven:

- Synchronous coupling: services must be available simultaneously; failures cascade; tight temporal coupling
- New consumer requires changing the publisher (adding a new REST call)
- Multiple consumers: N synchronous calls from publisher → response time grows with N consumers

WITH Event-Driven:
→ Publisher decoupled from consumers: publishes once, N consumers process independently. New consumer: subscribe to topic, zero changes to publisher. Temporal decoupling: consumer processes when ready. Kafka retains events for replay and new consumer bootstrapping.

---

### 🧠 Mental Model / Analogy

> A newspaper publishing daily editions. The newspaper: prints one edition (the event). Subscribers: each subscriber reads their own copy on their own schedule. The newspaper doesn't know how many subscribers exist, doesn't wait for them to finish reading, doesn't know how each subscriber uses the news. Add a new subscriber: sign up — no change to the newspaper. If a subscriber is on vacation: they catch up on missed editions when they return (Kafka offset replay). Each subscriber group is independent.

"Newspaper printing one edition" = event published to Kafka topic (published once)
"Each subscriber reads their own copy" = each consumer group processes its own offset
"Newspaper doesn't know how many subscribers" = publisher decoupled from consumers
"Doesn't wait for them to finish reading" = asynchronous, temporal decoupling
"Add a new subscriber: sign up" = new consumer group — zero publisher changes
"Catch up on missed editions" = Kafka offset replay (consumer reconnects, replays from offset)
"Each subscriber group is independent" = each consumer group: independent throughput, offset, scaling

---

### ⚙️ How It Works (Mechanism)

```
EVENT-DRIVEN COMMUNICATION FLOW:

  Order Service:                         Kafka:           Consumers:
  ─────────────                          ──────────────── ──────────
  createOrder() completes ──────────►  topic: order-events
  (via Outbox Pattern)                   partition 0:    ──►  Inventory Service (offset 0)
                                         [OrderPlaced]   ──►  Notification Service (offset 0)
                                         [OrderPlaced]   ──►  Analytics Service (offset 0)
                                         partition 1:         (each independent consumer group)
                                         [OrderPlaced]

  Key point: Order Service never calls Inventory, Notification, or Analytics directly.
  All three receive OrderPlaced event and process independently.

  ORDERING GUARANTEE:
  - Within a partition: events are strictly ordered (by offset).
  - orderId as key → same orderId always in same partition → all events for one order ordered.
  - Across partitions: no ordering guarantee.
  - Implication: don't expect OrderPlaced to be processed before OrderShipped
    across different consumer threads — only within one consumer's partition assignment.

EVENT SCHEMA EVOLUTION:

  Challenge: producer adds new field → consumer compiled against old schema → breaks.

  Solution 1: Backward-compatible schema changes only:
  - Adding optional fields: safe (old consumer ignores unknown fields with JsonDeserializer)
  - Removing required fields: breaking change — coordinate version upgrade

  Solution 2: Schema Registry (Confluent Schema Registry or Apicurio):
  - Avro/Protobuf schemas registered with versioned IDs
  - Producer validates against registered schema before publishing
  - Consumer fetches schema by ID from registry at deserialize time
  - Schema compatibility modes: BACKWARD, FORWARD, FULL

  Solution 3: CloudEvents type field versioning:
  type: "com.example.orders.v1.OrderPlaced"  →  type: "com.example.orders.v2.OrderPlaced"
  Consumers: handle both v1 and v2 during migration window.
```

---

### 🔄 How It Connects (Mini-Map)

```
Services need asynchronous, decoupled communication
        │
        ▼
Event-Driven Pattern ◄──── (you are here)
(events = facts; publisher unaware of consumers; Kafka broker; eventual consistency)
        │
        ├── Outbox Pattern: required for atomic DB write + event publish at producer side
        ├── CQRS Pattern: command side events drive read model projections (event-driven projection)
        ├── Saga Pattern: Choreography sagas are fully event-driven (services react to events)
        └── Idempotent Consumer: consumers must handle duplicate event delivery (at-least-once)
```

---

### 💻 Code Example

(See First Principles — complete Spring Boot Kafka producer/consumer example with configuration, DLT, and CloudEvents schema.)

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Event-driven and message-driven are the same                | Events: facts — something happened (past tense, immutable, publisher doesn't care what consumers do). Messages: commands or requests — do this (publisher typically expects a specific action or response). Event-driven: decoupled, broadcast semantics. Message-driven: often point-to-point or work queue. Kafka: event log. RabbitMQ: message queue. Both can implement both patterns, but their defaults and strengths differ.                        |
| Kafka guarantees exactly-once delivery                      | Kafka's default: at-least-once delivery. Producer with `enable.idempotence=true` + transactional producer: exactly-once at the producer → broker level. Consumer: at-least-once (can receive duplicate messages if consumer crashes after processing but before committing offset). True end-to-end exactly-once: requires idempotent consumers (or transactional consume-process-produce with Kafka Streams). Design consumers to be idempotent.          |
| Event-driven architecture reduces overall system complexity | Event-driven reduces coupling and synchronous dependency complexity. It introduces different complexity: distributed tracing (events lack the request trace of synchronous calls), debugging (hard to trace a request flow across async event handlers), eventual consistency management, event schema evolution, DLT monitoring, consumer lag monitoring. "Simpler in some ways, more complex in others" — EDA trades one kind of complexity for another. |

---

### 🔥 Pitfalls in Production

**Consumer lag: unchecked lag causes event processing hours behind:**

```java
// ANTI-PATTERN — slow consumer processing, no lag alerting:

@KafkaListener(topics = "order-events", groupId = "analytics-service")
public void on(OrderPlacedEvent event) {
    // SLOW: calls external ML service for fraud scoring — 500ms per event:
    fraudScore = externalMLService.score(event);  // 500ms × 10,000 events/day = 83 minutes lag
    analyticsRepo.save(new AnalyticsRecord(event, fraudScore));
}
// Result: analytics service falls 83 minutes behind during peak hours.
// User experience: analytics dashboard shows data from 1+ hours ago.
// Incident: DLT fills up because external ML service goes down → consumer crashes → retries.

// FIX 1 — Increase partition count + consumer instances:
// Kafka topic: 6 partitions → run 6 consumer instances (one partition each)
// Throughput: 6× parallel processing without changing consumer code.

// FIX 2 — Async/batch the slow external call:
@KafkaListener(topics = "order-events", groupId = "analytics-service")
public void on(List<OrderPlacedEvent> events) {   // Batch consumer
    // Batch ML scoring: 100 events in one API call instead of 100 separate calls:
    List<FraudScore> scores = externalMLService.scoreBatch(events);   // 200ms for 100 events
    // 200ms / 100 = 2ms per event (250× faster)
    analyticsRepo.saveAll(zip(events, scores));
}

// FIX 3 — Monitor consumer lag (Prometheus + kafka_consumer_lag_seconds metric):
// Alert: if consumer group "analytics-service" lag > 10,000 messages → PagerDuty.
// Grafana dashboard: consumer group offset vs. topic end offset per partition.
// Action: scale consumer instances, optimize processing, or add partitions.
```

---

### 🔗 Related Keywords

- `Apache Kafka` — primary event broker for event-driven microservices
- `Outbox Pattern` — atomic event publish: required at every event-producing service
- `CQRS Pattern` — read model projections are driven by events (event-driven projection updates)
- `Saga Pattern` — Choreography sagas: services react to domain events (fully event-driven)
- `CloudEvents` — CNCF standard for portable event schema across brokers and clouds

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Publish events (facts). Consumers react  │
│              │ independently. Publisher decoupled from  │
│              │ all consumers. Kafka as durable log.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Async service communication; multiple    │
│              │ consumers of same event; temporal        │
│              │ decoupling; Choreography saga steps      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Immediate, consistent response required; │
│              │ simple request-response; small system    │
│              │ with 2-3 services (REST sufficient)      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Newspaper: print once, N subscribers    │
│              │  read independently on their schedule.  │
│              │  Publisher never calls readers directly."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Kafka → Outbox Pattern → CQRS →          │
│              │ Saga → CloudEvents → Schema Registry     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kafka's ordering guarantee is within a partition (same key → same partition → ordered). But a consumer group with N consumer instances: each instance is assigned a subset of partitions. Processing for a single orderId is ordered (same partition), but processing across different orderIds may be concurrent. If OrderPlaced (orderId=123) is in partition 0 and OrderCancelled (orderId=123) is also in partition 0 — but a consumer processes partition 0 events sequentially — are you guaranteed OrderPlaced is processed before OrderCancelled? What happens if the consumer crashes mid-partition and restarts from an earlier offset?

**Q2.** Kafka Schema Registry (Confluent or Apicurio) with Avro or Protobuf schemas: producers register schemas, consumers look up schemas by ID embedded in messages. Compare this approach to JSON with no schema registry: what are the tradeoffs in terms of schema enforcement, backward/forward compatibility guarantees, consumer resilience to producer schema changes, and operational overhead? When would you choose JSON without a registry (simpler, lower overhead) vs. Avro with Schema Registry (stronger compatibility guarantees)?
