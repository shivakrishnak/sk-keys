---
version: 2
layout: default
title: "Event-Driven Architecture"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /messaging-streaming/event-driven-architecture/
id: MSG-028
category: Messaging & Event Streaming
difficulty: ★★★
depends_on: Message Broker vs Event Bus, Outbox Pattern, Apache Kafka
used_by: Microservices, Loose Coupling, Event Sourcing
related: Outbox Pattern, Event Sourcing, CQRS
tags:
  - event-driven-architecture
  - eda
  - choreography
  - orchestration
  - loose-coupling
---

# MSG-042 - Event-Driven Architecture

⚡ TL;DR - **Event-Driven Architecture (EDA)**: services communicate via **events** (immutable facts: "OrderPlaced", "PaymentCharged") through a broker (Kafka/RabbitMQ); producers fire events without knowing who consumes them; consumers react independently; **loose coupling** + **temporal decoupling** (consumer can be offline); **choreography** (services react to events independently, no coordinator) vs **orchestration** (saga coordinator tells each service what to do); challenges: eventual consistency, complex debugging, schema evolution.

| #569            | Category: Big Data & Streaming                            | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Message Broker vs Event Bus, Outbox Pattern, Apache Kafka |                 |
| **Used by:**    | Microservices, Loose Coupling, Event Sourcing             |                 |
| **Related:**    | Outbox Pattern, Event Sourcing, CQRS                      |                 |

---

### 🔥 The Problem This Solves

**TIGHT COUPLING IN SYNCHRONOUS MICROSERVICES:**
Order service places an order and synchronously calls: InventoryService.reserveItems() → PaymentService.charge() → NotificationService.sendEmail(). Problems: (1) If PaymentService is down: order fails. (2) Order service knows about 3 downstream services → high coupling. (3) Adding a new AnalyticsService requires changing OrderService code. EDA solution: OrderService publishes `OrderPlacedEvent`. InventoryService, PaymentService, NotificationService, AnalyticsService all react independently. OrderService knows only about the Kafka topic, not the consumers. Adding a new consumer = zero changes to OrderService.

---

### 📘 Textbook Definition

**Event-Driven Architecture (EDA)** is a software design paradigm where services communicate by publishing and subscribing to **events** - immutable records of things that happened in the past.

**Core concepts:**

- **Event**: an immutable record of a fact that occurred. Named in past tense: `OrderPlaced`, `PaymentCharged`, `UserRegistered`. Contains: event type, timestamp, aggregate ID, relevant payload.
- **Event Producer** (Publisher): emits events when something happens in its domain. Does not know who consumes the events (decoupled).
- **Event Consumer** (Subscriber): reacts to events it's interested in. Independent of the producer.
- **Event Broker**: infrastructure that routes events from producers to consumers (Kafka, RabbitMQ, AWS SNS/SQS).

**Two coordination patterns:**

- **Choreography**: no central coordinator. Each service listens for events and reacts independently. Implicit flow: OrderPlaced → InventoryService (reserves) → InventoryReserved → PaymentService (charges) → PaymentCharged → NotificationService (sends email).
- **Orchestration**: central saga orchestrator tells each service what to do via commands and listens for replies. Explicit flow: Orchestrator → Reserve(Inventory) → InventoryReserved → Charge(Payment) → PaymentCharged → SendEmail(Notification).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
EDA = services talk via events (past-tense facts), not synchronous calls; loose coupling; choreography (reactive, implicit flow) vs orchestration (coordinator, explicit flow); eventual consistency.

**One analogy:**

> EDA = a newsroom. A reporter (producer) publishes a story (event). Any editor, analyst, printer, or social media manager (consumers) who's interested picks it up and acts. The reporter doesn't call each one - they just publish. Late-arriving staff: they still read the story when they come in (temporal decoupling).
> Orchestration = a director who calls each person: "Print this story now. Wait. Now send the tweet. Wait. Now update the website."

**One insight:**
EDA is powerful for loose coupling but makes the overall flow hard to trace. In synchronous: you follow one call stack. In EDA: a single business transaction triggers a cascade of events across 5 services, each with their own failures, retries, and timings. This is why observability (distributed tracing with correlation IDs, Kafka consumer lag monitoring) is critical in EDA systems.

---

### 🔩 First Principles Explanation

**EVENTS AS FIRST-CLASS CITIZENS:**

```java
// Events: immutable, past-tense, domain-meaningful
// NOT: "ProcessOrder" (command - imperative, present-tense)
// YES: "OrderPlaced" (event - declarative, past-tense)

// Event design:
@Immutable
public record OrderPlacedEvent(
    String eventId,           // unique event ID (for idempotency)
    String eventType,         // "OrderPlaced"
    Instant eventTimestamp,   // when the event occurred
    String orderId,           // aggregate ID
    String userId,
    BigDecimal amount,
    List<OrderItem> items,
    String correlationId      // ties together a business transaction across services
) {}

// Correlation ID: critical for tracing
// Same correlationId threads through:
//   OrderPlacedEvent → InventoryReservedEvent → PaymentChargedEvent → EmailSentEvent
// In distributed tracing: correlationId = traceId (Zipkin, Jaeger)
```

**CHOREOGRAPHY (DECENTRALIZED, REACTIVE):**

```java
// CHOREOGRAPHY: each service listens and reacts independently
// No central coordinator; flow emerges from event chains

// InventoryService: listens for OrderPlaced → reacts
@Service
public class InventoryEventHandler {

    @KafkaListener(topics = "order-events", groupId = "inventory-service")
    @Transactional
    public void handleOrderPlaced(ConsumerRecord<String, OrderPlacedEvent> record) {
        OrderPlacedEvent event = record.value();

        try {
            inventoryService.reserveItems(event.items(), event.orderId());

            // Publish next event in the chain:
            eventPublisher.publish("inventory-events",
                new InventoryReservedEvent(event.orderId(), event.correlationId()));

        } catch (InsufficientStockException e) {
            // Compensation: publish failure event
            eventPublisher.publish("inventory-events",
                new InventoryReservationFailedEvent(event.orderId(), "INSUFFICIENT_STOCK",
                    event.correlationId()));
        }
    }
}

// PaymentService: listens for InventoryReserved → charges payment
@Service
public class PaymentEventHandler {

    @KafkaListener(topics = "inventory-events", groupId = "payment-service")
    @Transactional
    public void handleInventoryReserved(ConsumerRecord<String, InventoryReservedEvent> record) {
        InventoryReservedEvent event = record.value();

        try {
            paymentService.charge(event.orderId(), event.amount());
            eventPublisher.publish("payment-events",
                new PaymentChargedEvent(event.orderId(), event.correlationId()));
        } catch (PaymentFailedException e) {
            // Compensation: tell inventory to release the reservation
            eventPublisher.publish("payment-events",
                new PaymentFailedEvent(event.orderId(), "PAYMENT_DECLINED",
                    event.correlationId()));
        }
    }
}

// InventoryService: also listens for PaymentFailed → release reservation
@Service
public class InventoryCompensationHandler {

    @KafkaListener(topics = "payment-events", groupId = "inventory-compensation")
    public void handlePaymentFailed(ConsumerRecord<String, PaymentFailedEvent> record) {
        PaymentFailedEvent event = record.value();
        inventoryService.releaseReservation(event.orderId());  // compensating transaction
    }
}

// CHOREOGRAPHY PROBLEM: the flow is hard to see
// To understand "what happens when order is placed" you must read all event handlers
// across ALL services - no single place shows the full saga
```

**ORCHESTRATION (CENTRALIZED, EXPLICIT):**

```java
// ORCHESTRATION: central saga orchestrator controls the flow
// Clear: the entire saga logic is in one place

@Service
public class OrderSagaOrchestrator {

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    // Entry point: triggered by OrderPlaced event
    @KafkaListener(topics = "order-events", groupId = "saga-orchestrator")
    public void startOrderSaga(OrderPlacedEvent event) {
        // Step 1: command InventoryService to reserve
        kafkaTemplate.send("inventory-commands",
            new ReserveInventoryCommand(event.orderId(), event.items(), event.correlationId()));
    }

    // Step 2: inventory reserved → command PaymentService to charge
    @KafkaListener(topics = "inventory-replies", groupId = "saga-orchestrator")
    public void handleInventoryReply(Object reply) {
        if (reply instanceof InventoryReservedReply r) {
            kafkaTemplate.send("payment-commands",
                new ChargePaymentCommand(r.orderId(), r.amount(), r.correlationId()));
        } else if (reply instanceof InventoryFailedReply r) {
            // Abort saga: notify order service
            kafkaTemplate.send("order-commands",
                new FailOrderCommand(r.orderId(), "INVENTORY_FAILED"));
        }
    }

    // Step 3: payment charged → command NotificationService to send email
    @KafkaListener(topics = "payment-replies", groupId = "saga-orchestrator")
    public void handlePaymentReply(Object reply) {
        if (reply instanceof PaymentChargedReply r) {
            kafkaTemplate.send("notification-commands",
                new SendEmailCommand(r.orderId(), r.correlationId()));
            // Mark saga complete
        } else if (reply instanceof PaymentFailedReply r) {
            // Compensate: tell inventory to release
            kafkaTemplate.send("inventory-commands",
                new ReleaseInventoryCommand(r.orderId()));
            // Abort saga
        }
    }

    // ORCHESTRATION ADVANTAGES:
    // 1. Saga logic in ONE place (easy to reason about, debug)
    // 2. Easy to add new steps (change orchestrator only)
    // 3. Clear compensating transaction flow
    // ORCHESTRATION DISADVANTAGES:
    // 1. Orchestrator knows all downstream services → coupling at orchestrator level
    // 2. Single point of failure (orchestrator must be highly available)
    // 3. Each step adds network roundtrips
}
```

**WHEN TO CHOOSE EACH:**

```
CHOREOGRAPHY:
  ✓ Few services (2-3 steps)
  ✓ Simple, linear flows
  ✓ High autonomy: each service owns its own reaction
  ✓ No complex compensating transactions
  ✗ Hard to debug when flow spans 5+ services
  ✗ Circular dependencies possible (Service A listens to B, B listens to A)

  Example: UserRegistered → (async) send welcome email, create default settings
    Simple, no compensation needed, 2 services

ORCHESTRATION:
  ✓ Complex multi-step sagas with compensations (place order, reserve, charge, ship)
  ✓ Business process visibility needed (where is this order in the flow?)
  ✓ Error paths must be explicit and reliable
  ✗ Orchestrator becomes coupled to all participants

  Example: Order fulfillment saga (5+ services, multiple failure paths)
    Complex, needs explicit compensation, benefit from centralized visibility

HYBRID: choreography for simple notifications, orchestration for critical sagas
```

---

### 🧪 Thought Experiment

**SCHEMA EVOLUTION PROBLEM IN EDA:**

OrderService publishes `OrderPlacedEvent` with fields: `orderId`, `userId`, `amount`. 3 months later: need to add `couponCode` field. 4 consumer services have been running for 3 months.

- **Forward compatibility** (old consumer, new event): old InventoryService doesn't know about `couponCode` → must silently ignore it (safe).
- **Backward compatibility** (new consumer, old event): new AnalyticsService needs `couponCode` → must handle missing field (treat as null or "NO_COUPON").

Solution: use **Schema Registry** (Confluent Schema Registry with Avro). Enforce backward/forward compatibility at schema registration time. Any schema change that breaks compatibility → rejected before deployment. This is why schema evolution is one of the hardest operational problems in EDA.

---

### 🧠 Mental Model / Analogy

> EDA = supply chain: factory (producer) makes goods → places on truck (event broker) → retail stores (consumers) pick up independently. Factory doesn't call each store. New store opens: starts receiving trucks without factory knowing. Choreography = stores figure out what to do with goods themselves. Orchestration = distribution center (coordinator) tells each store what to stock.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Events = past-tense immutable facts. Producers publish, consumers react. Loose coupling: producer doesn't know consumers. Temporal decoupling: consumer can be offline. Choreography vs orchestration.

**Level 2:** Choreography: each service publishes + subscribes independently; flow is distributed across services. Orchestration: saga orchestrator sends commands, receives replies; flow is centralized. Both need compensating transactions for rollback. Correlation ID traces business transactions across services.

**Level 3:** Event schema design: backward/forward compatibility (Avro Schema Registry). Event versioning: V1 event still must be processable by V1 consumers after V2 schema deployed. Consumer idempotency. Event ordering: per-partition in Kafka (aggregate events → same partition key = aggregate ID → ordered per aggregate). Event replay: Kafka's retention enables new consumers to bootstrap from history.

**Level 4:** Event sourcing (full EDA): store events as the system of record, not state. Current state = replay of all events. Projection = read model derived from events. CQRS (Command Query Responsibility Segregation): write side = commands + events; read side = projections. Complex but enables: full audit trail, temporal queries ("what was the order state at 14:03?"), easy undo/replay. EDA without event sourcing: events for service communication only, state stored in traditional DB. Event sourcing = state stored AS events (different concept, often confused).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ EVENT-DRIVEN ARCHITECTURE: CHOREOGRAPHY              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ [OrderService] ── publishes ──> "order-events"      │
│                                      │               │
│             ┌────────────────────────┤               │
│             ↓                        ↓               │
│ [InventoryService]         [NotificationService]    │
│  listens "order-events"    listens "order-events"   │
│  reserves items             sends confirmation       │
│  publishes "inv-reserved"                           │
│             ↓                                       │
│ [PaymentService]                                    │
│  listens "inv-reserved"                             │
│  charges payment                                    │
│  publishes "payment-charged"                        │
│                                                      │
│ Flow: emergent from event chains                    │
│ No coordinator: each service knows its own role     │
│                                                      │
│ PROBLEM: where is the saga flow?                    │
│ ANSWER: distributed across ALL service event handlers│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order Placed - Full EDA Choreography Flow:

09:00:00 OrderService: publishes OrderPlacedEvent {orderId:'123', amount:50}
         Kafka: "order-events" partition 3 (key = orderId % partitions)

09:00:00.010 InventoryService: @KafkaListener
  reserves items for order '123'
  publishes InventoryReservedEvent to "inventory-events"

09:00:00.020 PaymentService: @KafkaListener (inventory-events)
  charges $50 for order '123'
  publishes PaymentChargedEvent to "payment-events"

09:00:00.030 NotificationService: @KafkaListener (payment-events)
  sends confirmation email to user

09:00:00.010 (parallel) AnalyticsService: @KafkaListener (order-events)
  updates revenue dashboard (independent of fulfillment flow)

Total: ~40ms from order placement to email dispatch
All services: independent, can fail/restart independently
Ordering: all events for orderId '123' on same Kafka partition → ordered per order

Failure scenario:
09:00:00.020 PaymentService: PaymentDeclinedException
  publishes PaymentFailedEvent to "payment-events"
09:00:00.025 InventoryService: @KafkaListener (payment-events)
  compensation: releases inventory reservation for order '123'
09:00:00.027 OrderService: @KafkaListener (payment-events)
  updates order status to 'PAYMENT_FAILED'

Correlation: all events carry correlationId='txn-abc-123'
Distributed trace: Jaeger/Zipkin shows full saga timeline by correlationId
```

---

### ⚖️ Comparison Table

| Dimension        | EDA (Events)                                | Synchronous REST                    |
| ---------------- | ------------------------------------------- | ----------------------------------- |
| Coupling         | Loose (producer unaware of consumers)       | Tight (caller knows callee API)     |
| Availability     | High (temporal decoupling)                  | Dependent (all services must be up) |
| Latency          | Eventual (async)                            | Low (synchronous)                   |
| Debugging        | Complex (distributed flow)                  | Simple (one call stack)             |
| Scalability      | High (independent scaling)                  | Limited by synchronous chain        |
| Data consistency | Eventual consistency                        | Strong consistency possible         |
| Schema evolution | Complex (Schema Registry)                   | Simple (contract testing)           |
| Best for         | Loose coupling, high scale, async workflows | Simple CRUD, strong consistency     |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                                                           |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "EDA is always better than REST for microservices" | EDA has higher complexity (observability, schema evolution, eventual consistency). Simple CRUD or query services are better with REST. Use EDA for: high-decoupling needs, async workflows, fan-out to many services. Mix both in the same system |
| "Choreography is simpler than orchestration"       | Choreography is simpler per-service but harder to reason about as a SYSTEM. When the business process spans 5 services with complex error paths: orchestration gives you a single place to see and debug the entire flow                          |
| "Events are the same as messages"                  | Events = facts that happened (past tense, immutable, broadcast). Messages = instructions to do something (command, point-to-point, consumed once). EDA uses events; task queues use messages. Both use the same broker infrastructure             |

---

### 🚨 Failure Modes & Diagnosis

**1. Saga Left in Partial State (Missing Compensating Transaction)**

**Symptom:** Order stuck in "PAYMENT_PENDING" state. Inventory reserved but no payment attempted. No error in logs.

**Root Cause:** PaymentService was down when InventoryReservedEvent was published. Consumer group lag grew during downtime. PaymentService recovered → processed events → sent to DLQ (transient error).

**Diagnosis:**

```bash
# Check consumer lag for payment-service group:
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group payment-service
# Columns: TOPIC, PARTITION, CURRENT-OFFSET, LOG-END-OFFSET, LAG, CONSUMER-ID

# Check DLT for failed events:
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic inventory-events-dlt --from-beginning
# If events here: permanent failure in PaymentService

# Check order state in DB:
SELECT order_id, status, created_at FROM orders
WHERE status = 'PAYMENT_PENDING' AND created_at < NOW() - INTERVAL '5 minutes';
```

**Fix:**

1. Fix root cause (PaymentService bug in DLT handler).
2. Replay DLT events (fix-and-replay pattern: fix bug → consume from DLT).
3. Add saga timeout: orders stuck in PAYMENT_PENDING for > 10 minutes → auto-compensate.

---

### 🔗 Related Keywords

**Prerequisites:** Message Broker vs Event Bus, Outbox Pattern
**Builds On This:** Event Sourcing, CQRS, Saga Pattern
**Related:** Outbox Pattern, Event Sourcing, CQRS

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ EVENTS      │ Immutable past-tense facts (OrderPlaced)  │
│ PRODUCER    │ Publishes events, unaware of consumers    │
│ CONSUMER    │ Reacts to events, independent             │
│ CHOREOGRAPHY│ Each service reacts independently         │
│ ORCHESTRATION│ Central coordinator controls flow        │
│ LOOSE CPLG  │ Producer doesn't know consumers           │
│ TEMPORAL    │ Consumer can be offline (broker buffers)  │
│ CORRELATION │ ID ties events across services (tracing)  │
│ CHALLENGES  │ Eventual consistency, debugging, schema   │
│ SCHEMA REG  │ Avro + Confluent Schema Registry for compat│
│ ONE-LINER   │ "Events = facts; producer fires-forget;  │
│             │  consumers react; choreography vs orch"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is Event-Driven Architecture? What is the difference between choreography and orchestration in EDA? Give one advantage and one disadvantage of each approach.

**Q2.** (TYPE C - Design) An e-commerce platform needs to implement order fulfillment: (1) Reserve inventory, (2) Charge payment, (3) Schedule shipment, (4) Send notification. Either step can fail and previous steps must be compensated. Design this as an EDA system. Should you use choreography or orchestration? Draw the event/command flow including failure paths.
