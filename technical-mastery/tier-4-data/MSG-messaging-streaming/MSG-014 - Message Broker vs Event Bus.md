---
version: 2
layout: default
title: "Message Broker vs Event Bus"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/messaging-streaming/message-broker-vs-event-bus/
id: MSG-021
category: Messaging & Event Streaming
difficulty: ★★☆
depends_on: Point-to-Point vs Pub-Sub, RabbitMQ, Apache Kafka
used_by: Microservices Communication, Event-Driven Architecture
related: RabbitMQ, Apache Kafka, Event-Driven Architecture
tags:
  - message-broker
  - event-bus
  - pub-sub
  - spring-events
  - messaging-patterns
---

⚡ TL;DR - **Message Broker**: external, durable store-and-forward system (Kafka, RabbitMQ) - messages survive service restarts, cross-process, replay possible; **Event Bus**: in-process pub-sub (Spring's `ApplicationEventPublisher`, Guava EventBus) - no durable storage, fire-and-forget, synchronous by default, messages lost if no listener is active at publish time; use **Broker** for: inter-service communication, durability, decoupling across processes; use **Event Bus** for: within a single service (e.g., domain events triggering other components in the same JVM).

| #564            | Category: Big Data & Streaming                         | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Point-to-Point vs Pub-Sub, RabbitMQ, Apache Kafka      |                 |
| **Used by:**    | Microservices Communication, Event-Driven Architecture |                 |
| **Related:**    | RabbitMQ, Apache Kafka, Event-Driven Architecture      |                 |

---

### 🔥 The Problem This Solves

**NOT ALL EVENT PATTERNS NEED KAFKA:**
A developer adds a Kafka producer and consumer within the same Spring Boot service to decouple an `OrderService` from an `EmailService` in the same JVM. This is massive over-engineering: Kafka adds network calls, serialization, a broker cluster, consumer group management - all for events that could be handled in-memory with a simple Spring event. Conversely, using Spring's `ApplicationEventPublisher` for cross-service communication is wrong: if the email service is down when the event is published, the event is silently lost. Right tool: **Event Bus** = within process; **Message Broker** = across process boundaries.

---

### 📘 Textbook Definition

**Message Broker**:

- An external infrastructure component that receives messages from producers and routes them to consumers.
- **Persistent**: messages stored durably (disk) until consumed (or TTL expires).
- **Cross-process**: producers and consumers can be in different services, machines, or languages.
- **Asynchronous**: producer sends and returns immediately; consumer processes independently.
- **Replay**: consumers can re-read past messages (Kafka offset replay; RabbitMQ: no).
- Examples: Apache Kafka, RabbitMQ, Apache Pulsar, AWS SQS/SNS, Azure Service Bus, ActiveMQ.

**Event Bus**:

- An in-process pub-sub mechanism within a single application or JVM.
- **Non-durable**: events exist only in memory. No storage. Service restart = all pending events lost.
- **In-process**: producers and consumers share the same JVM/process.
- **Synchronous or async**: Spring events: synchronous by default (`@EventListener` runs in publisher's thread); async with `@Async`.
- **Fire-and-forget**: if no listener registered at publish time → event is silently dropped.
- Examples: Spring `ApplicationEventPublisher`, Guava EventBus, Java Observer pattern, CDI events.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Broker = external + durable + cross-process (Kafka/RabbitMQ); Event Bus = in-process + non-durable (Spring events, Guava).

**One analogy:**

> **Message Broker** = postal service. Letters (messages) stored in sorting centers (broker). Even if recipient isn't home (consumer is down), the letter is held safely. Delivered when recipient is available.
> **Event Bus** = loudspeaker announcement. Only heard by people in the building RIGHT NOW. If you left the building, you miss it. No recording.

**One insight:**
Spring's `ApplicationEventPublisher` is perfectly appropriate for intra-service decoupling (e.g., after saving an order to DB, publish `OrderCreatedEvent` → audit logger + inventory updater both listen within the same service). But the moment you need cross-service communication or durability, use a broker. The pattern that bridges both: **Transactional Outbox** (save event to DB table + publish to broker atomically → use broker for cross-service delivery).

---

### 🔩 First Principles Explanation

**SPRING EVENT BUS (IN-PROCESS):**

```java
// ===== SPRING APPLICATION EVENTS =====
// In-process: producer and consumer in the SAME Spring
// ApplicationContext
// (Same JVM, same service)

// 1. Define the event:
public class OrderCreatedEvent extends ApplicationEvent {
    private final Order order;

    public OrderCreatedEvent(Object source, Order order) {
        super(source);  // source = the publishing component
        this.order = order;
    }

    public Order getOrder() { return order; }
}

// Simpler: POJO event (Spring 4.2+):
public record OrderCreatedEvent(Order order) {}
// no ApplicationEvent needed

// 2. Publisher: inject ApplicationEventPublisher
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    @Transactional
    public Order createOrder(CreateOrderRequest request) {
        Order order = new Order(request);
        orderRepository.save(order);

        // Publish event WITHIN the same transaction (default:
        // synchronous)
        eventPublisher.publishEvent(new OrderCreatedEvent(order));
        // Listeners run SYNCHRONOUSLY in the same thread (default)
        // If a listener throws → this @Transactional rolls back (both
        // are same tx)

        return order;
    }
}

// 3. Listener: @EventListener
@Component
public class OrderAuditListener {

    @EventListener
    public void onOrderCreated(OrderCreatedEvent event) {
        // Runs in the SAME thread as the publisher (synchronous)
        // SAME transaction if publisher has @Transactional
        auditService.log("ORDER_CREATED", event.order().getId());
    }
}

@Component
public class InventoryUpdateListener {

    @Async  // runs in a separate thread (async event listener)
    @EventListener
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    // AFTER_COMMIT: only fire this event listener AFTER the
    // transaction commits
    // Prevents: listener running → order saved → transaction rolls
    // back → listener already ran
    public void onOrderCreated(OrderCreatedEvent event) {
        // Different thread (async) → different transaction
        inventoryService.decreaseStock(event.order());
    }
}

// CRITICAL: @TransactionalEventListener(phase = AFTER_COMMIT)
// When to use:
//   - Listener does external calls (send HTTP, Kafka message)
//   - Must only run if the triggering DB transaction COMMITTED
// - Without AFTER_COMMIT: listener runs even if transaction rolls
// back
//     → external calls made for a rolled-back order (bug!)
//
// Without @Transactional: default @EventListener (runs at publish
// time, in-transaction)
// With @Transactional: use AFTER_COMMIT for side effects outside the
// transaction
```

**BROKER USAGE (CROSS-SERVICE):**

```java
// ===== MESSAGE BROKER (KAFKA) =====
// Cross-service: producer in OrderService, consumer in
// NotificationService (different JVM)

@Service
public class OrderService {

    @Autowired
    private KafkaTemplate<String, OrderCreatedEvent> kafkaTemplate;

    @Transactional
    public Order createOrder(CreateOrderRequest request) {
        Order order = orderRepository.save(new Order(request));

        // Publish to Kafka: cross-process, durable
        kafkaTemplate.send("order-events", order.getId(),
            new OrderCreatedEvent(order));
        // Consumer (NotificationService): different JVM, can be
        // offline
        // Message persisted in Kafka: safe even if
        // NotificationService restarts

        return order;
    }
}

// IN NotificationService (separate microservice):
@Component
public class OrderNotificationConsumer {

    @KafkaListener(topics = "order-events",
        groupId = "notification-service")
    public void onOrderCreated(OrderCreatedEvent event) {
        // Runs in NotificationService's JVM
        // Can lag behind - Kafka retains messages
        emailService.sendOrderConfirmation(event.getOrder());
    }
}
```

**COMPARISON: WHEN TO USE EACH:**

```
USE SPRING EVENT BUS when:
  ✓ Components are in the SAME service (same JVM, same
    Spring context)
  ✓ No durability needed (if service restarts, state comes
    from DB)
  ✓ Simple decoupling: OrderService shouldn't directly
    call AuditService
  ✓ Transaction coordination:
    @TransactionalEventListener(AFTER_COMMIT)
  ✓ Zero infrastructure: no broker cluster to run

  Examples:
  - Order saved → audit log + inventory (same service)
  - User registered → send welcome email (same service,
    async @EventListener)
  - Cache invalidation triggered by DB write (same service)

USE MESSAGE BROKER when:
  ✓ Cross-service communication (OrderService →
    NotificationService)
  ✓ Consumer may be temporarily unavailable (need
    durability)
  ✓ Replay required: new service needs past events
  ✓ High volume: Kafka handles millions/sec
  ✓ Multiple independent consumer teams (fan-out to N
    services)

  Examples:
  - Order placed → notify: email service + SMS service +
    analytics service
  - Payment captured → update: inventory service +
    fulfillment service
  - User action → event stream for ML pipeline
```

**GUAVA EVENT BUS (IN-PROCESS, NON-SPRING):**

```java
// Non-Spring applications: Guava EventBus
// Also in-process, fire-and-forget, no durability
EventBus eventBus = new EventBus("order-events");
// AsyncEventBus: runs handlers in a thread pool
// EventBus: synchronous (same thread)

// Register subscriber:
eventBus.register(new Object() {
    @Subscribe
    public void handleOrderCreated(OrderCreatedEvent event) {
        System.out.println("Order created: " + event.order().getId());
    }
});

// Publish:
eventBus.post(new OrderCreatedEvent(order));
// Handler runs immediately, synchronously

// LIMITATION vs Spring:
// No @Transactional integration
// No AFTER_COMMIT semantics
// Use Spring ApplicationEventPublisher in Spring apps (more features)
```

---

### 🧪 Thought Experiment

**THE SILENT LOSS PROBLEM:**

Using Spring events for cross-service: `emailService` is a separate microservice. Developer publishes `OrderCreatedEvent` via `ApplicationEventPublisher`. But `emailService` has no `@EventListener` in the same JVM - it's a separate process. Result: event silently dropped. No error. No indication. User never gets confirmation email.

With Kafka: publish `OrderCreatedEvent` to `order-events` topic. EmailService consumer is down (deployment). Message waits in Kafka. EmailService restarts → reads from last committed offset → processes the missed event. User gets email (slightly delayed, but no loss).

Silent loss is the most dangerous failure mode of event buses used for cross-process communication.

---

### 🧠 Mental Model / Analogy

> Event Bus = **intercom** (in a building). Press button → anyone in the building hears it RIGHT NOW. Nobody home → nobody hears it. No recording.
> Message Broker = **email** (external service). Send email → email server stores it. Recipient reads it when they check their inbox, even days later.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Broker = external + durable (Kafka/RabbitMQ). Event Bus = in-process + volatile (Spring events). Cross-service → broker. Same service → event bus. Broker survives restarts; event bus doesn't.

**Level 2:** Spring events: `ApplicationEventPublisher.publishEvent()`. `@EventListener` (sync). `@Async @EventListener` (async). `@TransactionalEventListener(AFTER_COMMIT)` (only after TX commits). Key pattern: AFTER_COMMIT for side effects (email, HTTP calls) to avoid running them on rollback.

**Level 3:** Spring's `@TransactionalEventListener` integrates with Spring's transaction synchronization. Under the hood: registers a `TransactionSynchronization.afterCommit()` callback. If no active transaction: falls back to BEFORE_COMMIT or not-executed depending on `fallbackExecution` flag. For async listeners (`@Async`): new transaction is NOT started automatically (each async method is independent). Use `@Transactional` on the async listener if it needs its own DB transaction.

**Level 4:** The Outbox Pattern bridges both: use `@EventListener` (or `@TransactionalEventListener`) within the service to capture events and write them to an outbox DB table (in the same transaction). A separate relay process reads the outbox and publishes to Kafka. This gives you: in-process event bus semantics (no broker dependency in the service) + broker durability (events safely persisted to broker after commit). Best of both worlds for transactional event publishing.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ EVENT BUS vs BROKER COMPARISON                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│ EVENT BUS (Spring ApplicationEventPublisher):       │
│   OrderService.createOrder()                        │
│       → publishEvent(OrderCreatedEvent)             │
│       → AuditListener.onOrderCreated() [same thread]│
│       → InventoryListener.onOrderCreated() [same]  │
│   All in ONE JVM, ONE process, ONE Spring context  │
│   Zero network calls, zero infrastructure          │
│                                                      │
│ MESSAGE BROKER (Kafka):                             │
│   OrderService (JVM 1): send("order-events", event)│
│       → Kafka broker (external, durable)           │
│   NotificationService (JVM 2):                     │
│       → poll("order-events") → processEvent()      │
│   Different processes, network between them        │
│   Kafka retains message → consumer can be offline  │
│                                                      │
│ [DECIDE ← YOU ARE HERE: same JVM? → bus; cross-JVM? → br│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order service: hybrid (event bus + broker)

1. Request: POST /orders → OrderService.createOrder()
2. @Transactional: save Order to DB
3. Within same TX: publishEvent(OrderCreatedEvent)

4a. @EventListener (synchronous, same TX):
    AuditService.logEvent() → saves audit record to DB
    (same transaction: either both commit or both rollback)

4b. @TransactionalEventListener(AFTER_COMMIT):
    [deferred until TX commits]
    After commit fires:
    KafkaTemplate.send("order-events", event)
    → EmailService (separate JVM) receives via Kafka →
      sends email
    → InventoryService receives via Kafka → decreases stock
    → AnalyticsService receives via Kafka → updates
      dashboard

Result:
  - In-process audit: simple, transactionally safe, no
    infrastructure
  - Cross-service notification/inventory: durable,
    resilient, scalable
  - @TransactionalEventListener: ensures Kafka publish
    only after DB commit
    (prevents: Kafka event published, DB rollback → ghost
      events)
```

---

### ⚖️ Comparison Table

| Dimension               | Message Broker (Kafka/RabbitMQ)          | Event Bus (Spring Events)            |
| ----------------------- | ---------------------------------------- | ------------------------------------ |
| Scope                   | Cross-process (cross-service)            | In-process (same JVM)                |
| Durability              | Yes (disk, configurable retention)       | No (in-memory, lost on restart)      |
| Infrastructure          | External broker cluster required         | Built into Spring (no infra)         |
| Latency                 | Network (ms)                             | In-process (μs)                      |
| Reliability             | High (at-least-once / exactly-once)      | Low (fire-and-forget)                |
| Replay                  | Yes (Kafka offset replay)                | No                                   |
| Transaction integration | Limited (Outbox Pattern)                 | Native (@TransactionalEventListener) |
| Scaling                 | Independent services scale independently | All in same process                  |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Event bus and message broker are the same thing"            | Fundamentally different: scope, durability, infrastructure requirements. Event bus = in-process, volatile. Broker = cross-process, durable. Using the wrong one → silent data loss or over-engineering        |
| "Spring @EventListener is reliable enough for cross-service" | Spring events exist only in the JVM. If the service restarts between event publication and processing, the event is gone. For cross-service: always use a broker                                              |
| "@Async @EventListener handles failures gracefully"          | @Async runs in a thread pool. If the thread throws an exception, it's swallowed by default (unless `AsyncUncaughtExceptionHandler` is configured). This can silently lose events even within the same service |

---

### 🚨 Failure Modes & Diagnosis

**1. @EventListener Runs on Transaction Rollback**

**Symptom:** Email sent for order that was rolled back (DB error after event published). User gets "order confirmed" email for an order that doesn't exist.

**Root Cause:** Using `@EventListener` (not `@TransactionalEventListener`) for side effects.

**Fix:**

```java
// WRONG: @EventListener runs during transaction (before
// commit/rollback)
@EventListener
public void onOrderCreated(OrderCreatedEvent event) {
    emailService.sendConfirmation(event.order());
    // runs even if TX rolls back!
}

// RIGHT: @TransactionalEventListener runs only after commit
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onOrderCreated(OrderCreatedEvent event) {
    emailService.sendConfirmation(event.order());
    // only if DB write succeeded
}

// If no active transaction (e.g., called from non-@Transactional
// context):
@TransactionalEventListener(
    phase = TransactionPhase.AFTER_COMMIT,
    fallbackExecution = true  // run even without transaction
)
```

---

### 🔗 Related Keywords

**Prerequisites:** Point-to-Point vs Pub-Sub

**Builds On This:** Outbox Pattern, Transactional Outbox

**Related:** RabbitMQ, Apache Kafka, Event-Driven Architecture

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ BROKER      │ External, durable, cross-process          │
│ EVENT BUS   │ In-process, non-durable, same JVM         │
│ USE BROKER  │ Cross-service, durability needed          │
│ USE BUS     │ Within-service component decoupling       │
│ @EventListener│ Sync, same thread, in-transaction       │
│ @Async      │ Separate thread, swallows exceptions      │
│ AFTER_COMMIT│ Only fires after TX success (KEY pattern) │
│ GUAVA BUS   │ Non-Spring in-process pub-sub             │
│ SILENT LOSS │ Event bus for cross-service = lost events │
│ ONE-LINER   │ "Broker = postal service (durable);      │
│             │  Event Bus = intercom (in-process only)" │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the difference between a message broker and an event bus? Give one example of each and explain when you would choose each. What is the key risk of using an event bus for cross-service communication?

**Q2.** (TYPE B - Bug Hunt) A Spring Boot service uses `@EventListener` to send confirmation emails when orders are created. The email service calls `emailService.send()` which is an external HTTP call. During load testing, you notice emails being sent for orders that were subsequently rolled back due to database constraint violations. What is the root cause and how do you fix it?
