---
id: MSV-048
title: Event-Driven Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-046, MSV-051
used_by: MSV-046, MSV-049
related: MSV-046, MSV-049, MSV-050, MSV-051, MSV-054, MSV-059
tags:
  - microservices
  - messaging
  - deep-dive
  - events
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /microservices/event-driven-microservices/
---

# MSV-048 - Event-Driven Microservices

⚡ TL;DR - Event-Driven Microservices communicate via
asynchronous events published to a message broker
(Kafka, RabbitMQ). The producing service emits a
domain event (OrderCreated, PaymentProcessed). Consuming
services subscribe independently - no direct coupling.
Benefits: temporal decoupling (services don't need
to be up simultaneously), scalability (consumers scale
independently), extensibility (new consumers without
changing producers). Trade-offs: eventual consistency,
complexity in debugging and ordering, need for
idempotent consumers.

| #048 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Saga Pattern, Event Sourcing in Microservices | |
| **Used by:** | Saga Pattern, Eventual Consistency in Microservices | |
| **Related:** | Saga Pattern, Eventual Consistency in Microservices, CQRS in Microservices, Event Sourcing in Microservices, Outbox Pattern, Event-Carried State Transfer | |

---

### 🔥 The Problem This Solves

**SYNCHRONOUS COUPLING:**
Order-service calls notification-service, loyalty-service,
analytics-service, and warehouse-service synchronously
on every order. If notification-service is down:
order creation fails. Order-service must wait for
all 4 services to respond sequentially (or in parallel,
but still blocked). Adding a new consumer (fraud-service)
requires modifying order-service. The order-service
becomes a hub with 5 direct dependencies.

Event-driven: order-service publishes `OrderCreated`
event to Kafka. It doesn't know or care who consumes.
Notification, loyalty, analytics, warehouse, fraud
services all subscribe independently. Order-service:
no direct dependencies on any consumer. Adding fraud-service:
no change to order-service. Notification down: order
still created; notification consumes when it recovers.

---

### 📘 Textbook Definition

**Event-Driven Microservices** is an architectural
pattern where services communicate primarily through
asynchronous events via a message broker. An event
is an immutable record of something that happened
(past tense: `OrderCreated`, not `CreateOrder`). The
producing service (publisher) emits events without
knowledge of consumers. Consuming services subscribe
to event topics independently. The message broker
(Kafka, RabbitMQ, AWS SNS/SQS) decouples producers
from consumers in time and space. Core characteristics:
temporal decoupling, location transparency, independent
scaling, eventual consistency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Event-Driven: services communicate via events on a
message bus; producer doesn't know consumers; temporal
decoupling enables independent scaling and evolution.

**One analogy:**
> A newspaper publisher (order-service) prints a
> morning edition (OrderCreated event). Subscribers
> (notification, analytics, warehouse services) receive
> the paper independently on their own schedule.
> The publisher doesn't call each subscriber. Adding
> a new subscriber (fraud-service): sign up for the
> paper; no change to the publisher. If a subscriber
> is on vacation: papers pile up; they read them all
> on return (message replay / consumer catch-up).

**One insight:**
The power of event-driven architecture is not just
decoupling - it's event history. Unlike REST calls
(ephemeral, no history), events are immutable records
persisted in Kafka. A new service can join the mesh
and replay all historical events to build its initial
state. This makes the system extensible: new business
requirements can be served by new consumers without
any producer changes.

---

### 🔩 First Principles Explanation

**EVENT TAXONOMY:**

```
DOMAIN EVENT (what happened):
  Immutable, past tense
  Contains enough data to process without callbacks
  Examples:
    OrderCreated { orderId, customerId, items, total }
    PaymentProcessed { orderId, paymentId, amount }
    InventoryReserved { orderId, productId, qty }
  
  Stored in: Kafka topic (event log)
  Consumed by: 0 or more services (fan-out)
  Retained: 7 days (Kafka default) or forever
             (event sourcing use case)

COMMAND (request to do something):
  Imperative, present/future tense
  Has one intended handler (not fan-out)
  Examples:
    ProcessPayment { orderId, amount }
    ReserveInventory { orderId, productId, qty }
  
  Used in: Saga Orchestration
  Pattern: Command-Query Responsibility Segregation

QUERY (read request):
  Not typically events; usually synchronous API calls
  Exception: CQRS with event projections
```

**EVENT-DRIVEN PATTERNS:**

```
FAN-OUT (one event, many consumers):
  OrderCreated -> [notification-service,
                  analytics-service,
                  loyalty-service,
                  warehouse-service]
  Kafka: consumer groups (each service = own group)
  Each service processes independently at own pace

CHOREOGRAPHY (event chain):
  OrderCreated -> PaymentService: processes payment
  -> PaymentProcessed -> InventoryService: reserves
  -> InventoryReserved -> ShippingService: creates
  -> ShipmentCreated -> OrderService: confirms
  Each service: listens to input events, emits output
  Saga choreography (MSV-046)

EVENT SOURCING (event as state):
  All state changes are events; DB is the event log
  Current state: replay events
  Audit trail: complete history
  Time-travel: reconstruct state at any point
  MSV-051: Event Sourcing in Microservices
```

---

### 🧪 Thought Experiment

**EVENT SCHEMA EVOLUTION:**

```
SCENARIO:
  Order-service publishes OrderCreated v1:
  { orderId, customerId, items, total }
  
  New requirement: add giftWrap flag
  Option A: Change v1 schema
    All consumers must update simultaneously
    Not backwards compatible
    Coordination across teams
    -> synchronous team coupling (defeats the purpose)
  
  Option B: Add field with default
    { orderId, customerId, items, total, giftWrap: false }
    Old consumers: ignore giftWrap (schema evolution)
    New consumers: use giftWrap
    Backwards compatible: no coordination needed
  
  Option C: Create v2 event type
    { orderId, customerId, items, total } - still published
    AND { orderId, customerId, items, total, giftWrap } - new
    Consumers can choose v1 or v2 topic
    Supports gradual migration
    
BEST PRACTICE:
  Use schema registry (Confluent Schema Registry / AWS Glue)
  Enforce schema compatibility: BACKWARD_TRANSITIVE
  Old consumers read new events (new fields optional)
  New consumers read old events (missing fields use defaults)
  Result: producers and consumers evolve independently
```

---

### 🧠 Mental Model / Analogy

> Event-Driven Microservices is like a stock market
> ticker tape. A company (producer) announces earnings
> (event: EarningsReleased). Traders (consumers) who
> subscribed to that company's ticker receive the
> announcement and act independently: buy (one trader),
> sell (another), hold (third). The company doesn't
> know how many traders subscribed or what they'll do.
> Adding a new trading algorithm: subscribe to the
> ticker; no change to the company. Historical events:
> the ticker tape archive (Kafka retention) allows
> replaying past announcements.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of services calling each other directly:
they publish events to a shared bus. Other services
listen and react. The sender doesn't know who's listening.

**Level 2 - How to use it (junior developer):**
With Spring + Kafka: `@KafkaListener(topics="orders")
public void onOrderCreated(OrderCreatedEvent event) {...}`.
Publish: `kafkaTemplate.send("orders", event)`. Serialize:
Avro or JSON with schema registry for type safety.

**Level 3 - How it works (mid-level engineer):**
Kafka topic: immutable, ordered log. Each consumer
group maintains its own offset (position in log).
Consumer group advances offset after processing. If
consumer restarts: resumes from saved offset. Multiple
consumer groups on same topic: each gets all events
(fan-out). Ordering: guaranteed within partition.
Partitioning key (orderId): all events for same order
go to same partition -> ordered per order.

**Level 4 - Why it was designed this way (senior/staff):**
Event-driven architecture solves the dependency inversion
problem: in synchronous architecture, high-level services
depend on low-level services. In event-driven:
producers depend on nothing (publish to Kafka topic).
Consumers depend on the topic (event schema), not the
producer. This is the Open/Closed Principle applied
to distributed systems: producers are "closed for
modification" when new consumers are added. The event
schema becomes the stable contract. This is why schema
registries and schema evolution compatibility rules
are critical operational decisions, not optional tooling.

**Level 5 - Mastery (distinguished engineer):**
Event-driven architecture's hidden complexity: ordering
and exactly-once semantics. Kafka guarantees ordering
within a partition. If order events for orderId=123
go to different partitions: out-of-order delivery.
Fix: partition by orderId. Exactly-once: Kafka 0.11+
supports idempotent producers and transactional APIs
(exactly-once within Kafka). But: service-to-DB writes
are not part of Kafka transaction. Use Outbox Pattern
for exactly-once service DB + Kafka write. Consumers:
always idempotent (Kafka at-least-once delivery;
duplicates possible on consumer restart).

---

### ⚙️ How It Works (Mechanism)

**KAFKA PRODUCER + CONSUMER (SPRING BOOT):**

```java
// PRODUCER: Order-service
@Service
public class OrderService {

    private final KafkaTemplate<String, OrderCreatedEvent>
        kafkaTemplate;

    @Transactional  // Local DB transaction
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.pending(req));

        // Publish event (with Outbox Pattern for reliability)
        // Here: simplified direct Kafka send
        OrderCreatedEvent event = new OrderCreatedEvent(
            order.getId(), req.getCustomerId(),
            req.getItems(), req.getTotal());

        kafkaTemplate.send("order-events",
            order.getId().toString(),  // partition key
            event);

        return order;
    }
}

// CONSUMER: Notification-service
@Component
public class OrderNotificationConsumer {

    @KafkaListener(
        topics = "order-events",
        groupId = "notification-service",  // own consumer group
        containerFactory = "kafkaListenerContainerFactory"
    )
    public void onOrderCreated(OrderCreatedEvent event,
                               Acknowledgment ack) {
        try {
            // Process idempotently
            if (notificationRepo.exists(event.getOrderId())) {
                ack.acknowledge();  // Already processed
                return;
            }
            notificationService.sendOrderConfirmation(
                event.getCustomerId(), event.getOrderId());
            notificationRepo.save(
                new ProcessedEvent(event.getOrderId()));
            ack.acknowledge();  // Commit offset
        } catch (Exception e) {
            // Don't acknowledge: message redelivered
            log.error("Failed to process order event", e);
        }
    }
}

// CONSUMER: Loyalty-service (independent, same topic)
@Component
public class LoyaltyPointsConsumer {
    @KafkaListener(
        topics = "order-events",
        groupId = "loyalty-service"  // own offset
    )
    public void onOrderCreated(OrderCreatedEvent event) {
        loyaltyService.awardPoints(
            event.getCustomerId(), event.getTotal());
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
ORDER CREATED EVENT FLOW:

  order-service publishes to: order-events (Kafka)
  Partition key: orderId
  
  Consumer groups (each independent, own offset):
  notification-service: sends confirmation email
  loyalty-service:       awards points
  analytics-service:     records revenue event
  warehouse-service:     starts pick & pack
  fraud-service:         checks order patterns
  
  Notification-service is down for 30 minutes:
    Kafka: events accumulate in topic
    notification-service offset: hasn't advanced
    When notification-service recovers:
    Consumes all 30 min of events
    Other services: unaffected (own offsets)
  
  New fraud-service deployed:
    Subscribes to order-events from offset=beginning
    Replays all historical orders
    Builds initial fraud detection state
    No change to order-service
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: chatty synchronous calls**

```java
// BAD: Order-service synchronously calls 4 services
@Service
public class OrderService {
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.from(req));
        notificationClient.sendConfirmation(order);   // fail = order fail
        loyaltyClient.awardPoints(order);             // fail = order fail
        analyticsClient.recordRevenue(order);         // fail = order fail
        warehouseClient.notifyOrder(order);           // fail = order fail
        return order;
        // 4 service dependencies; any one fails = order fails
    }
}
```

```java
// GOOD: Event-driven - publish once; consumers react
@Service
public class OrderService {
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.from(req));
        // Single publish: Kafka handles fan-out
        eventPublisher.publish(
            "order-events",
            new OrderCreatedEvent(order));
        return order;
        // No direct dependency on notification/loyalty/analytics
        // Consumers: independently subscribe
        // New consumers: no change to this code
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Synchronous (REST) | Event-Driven (Kafka) |
|---|---|---|
| **Coupling** | Tight (caller knows callee) | Loose (producer unknown consumers) |
| **Consistency** | Immediate | Eventual |
| **Failure isolation** | Caller fails if callee fails | Producer succeeds; consumer retry |
| **Scalability** | Coupled scaling | Independent scaling |
| **Observability** | Direct trace | Requires event tracing (correlation ID) |
| **New consumers** | Modify producer | Just subscribe |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Events are fire-and-forget | Events are durable in Kafka (default 7-day retention). Consumers WILL process them, even if delayed. This is reliable delivery, not fire-and-forget. Fire-and-forget uses UDP or in-memory queues that can lose messages. |
| Event-driven means no synchronous calls | Most production microservices use BOTH. Events for: notifications, analytics, fan-out to multiple services, async workflows. Synchronous REST for: read operations, immediate responses needed by client, low-volume, latency-sensitive calls. The pattern choice depends on the operation characteristics. |
| Consumer groups provide deduplication | Consumer groups provide fan-out (each group gets all events). They do NOT deduplicate. If a consumer crashes after processing but before committing offset: the event is redelivered. Consumers MUST be idempotent to handle redelivery correctly. |

---

### 🚨 Failure Modes & Diagnosis

**Consumer lag: notification service hours behind**

**Symptom:**
Customers are reporting confirmation emails arriving
3 hours after order placement. Monitoring shows:
notification-service Kafka consumer lag = 250,000
messages. notification-service is running but processing
slowly.

**Root Cause:**
Notification-service sends emails via SMTP client
with no connection pooling. Each email: new SMTP
connection (200ms). At 500 orders/minute peak:
500 * 200ms = 100 seconds per minute. Service is
processing at 0.3x the rate of production. Lag
accumulates indefinitely.

**Diagnostic:**
```bash
# Check consumer lag
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group notification-service
# GROUP     TOPIC        PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# notif-svc order-events 0          1000000         1250000         250000

# Check processing rate
# Prometheus: kafka_consumer_records_consumed_rate
# Expected: >= production rate
# Actual: 0.3x production rate

# Check notification-service logs for timing
grep 'EmailSent' notification-service.log | \
  awk '{print $1, $2}' | head -20
# See: timestamps showing 200ms+ per email
```

**Fix:**
1. Add SMTP connection pool (JavaMail session pool).
2. Parallelize: increase consumer partition count
   (more partitions = more consumer threads).
3. Batch: send bulk emails via SendGrid/SES API
   (1000 emails per API call vs 1 SMTP connection
   per email).
4. Scale: add more notification-service instances
   (each in same consumer group = distributes load).

---

### 🔗 Related Keywords

**Data patterns:**
- `Saga Pattern` - choreography-based Saga uses
  events for workflow coordination
- `Eventual Consistency in Microservices` - event-driven
  architecture produces eventual consistency
- `Event Sourcing in Microservices` - events as the
  source of truth for state
- `CQRS in Microservices` - often combined with
  event-driven for separate read/write models
- `Outbox Pattern` - ensures atomic write + event
  publish
- `Event-Carried State Transfer` - events contain
  full state data for consumer independence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE PATTERN │ Producer publishes event; consumers react │
│              │ Temporal decoupling via Kafka/broker      │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULES    │ Consumers MUST be idempotent (at-least-1x)│
│              │ Schema evolution: backward compatible     │
│              │ Partition by entity ID for ordering       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Async events via broker; producer/      │
│              │  consumer decoupled in time and space"    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Event-Driven = producer publishes immutable events
   to broker; consumers subscribe independently.
   Temporal decoupling: consumers process at own pace.
2. Consumers MUST be idempotent: Kafka delivers
   at-least-once; duplicates happen on restart.
3. Schema evolution: use schema registry with backward
   compatibility to allow producers and consumers
   to evolve independently.

**Interview one-liner:**
"Event-Driven Microservices: services communicate via
immutable domain events (OrderCreated, PaymentProcessed)
published to a message broker (Kafka). Producer is
decoupled from consumers - doesn't know who subscribes.
Benefits: temporal decoupling (consumer processes at
own pace), scalability (independent consumer scaling),
extensibility (new consumers without changing producers).
Requirements: idempotent consumers (at-least-once
delivery), schema registry for evolution, Outbox Pattern
for atomic write + event publish."

---

### 💡 The Surprising Truth

The most counterintuitive aspect of event-driven
architecture: consumers need MORE context in events
than feels "natural". The instinct is: `OrderCreated
{orderId: 123}` - let consumers look up details via
API. Problem: every consumer must call order-service
to get order details -> chatty (defeats the purpose),
ordecoupling (consumers depend on producer's API).
The correct approach: `OrderCreated {orderId, customerId,
productIds[], total, currency, shippingAddress}` -
the event carries enough data for consumers to process
without additional calls. This is the Event-Carried
State Transfer pattern (MSV-059). The event is self-
contained. The trade-off: larger event size. The
benefit: true consumer independence.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** Design the event schema for an order
   created event with enough data for all known
   consumers to process without additional API calls.
2. **KAFKA** Configure a Kafka consumer group in
   Spring Boot with manual offset commit and
   idempotency check. Handle failure (dead letter
   topic for poison messages).
3. **ORDERING** Explain why partition key choice
   matters for event ordering. Give an example where
   wrong partition key causes race conditions.
4. **SCHEMA** Set up Confluent Schema Registry.
   Register an Avro schema. Update the schema with
   a new optional field. Verify backward compatibility.
5. **LAG** Given a consumer lag of 500,000: calculate
   time to catch up given processing rate. Identify
   3 causes of consumer lag and their fixes.

---

### 🧠 Think About This Before We Continue

**Q1.** Two consumers (notification-service and
loyalty-service) subscribe to OrderCreated events.
Notification-service must send email immediately (<1s).
Loyalty-service awards points (can be delayed 1min).
Should they use the same consumer group or different
groups? How does this affect partition-level parallelism
for each service?

**Q2.** An `OrderCreated` event has been consumed
by analytics-service and recorded in its data warehouse.
24 hours later: the order is cancelled (OrderCancelled
event). How does analytics-service handle this?
Should it delete the revenue record? How do you
design for "event corrections" in an append-only
event log?

**Q3.** Your event-driven system has an `OrderCreated`
event that is consumed by 8 different services. You
need to add a required field `giftMessage` to the
event schema. Walk through the safe schema evolution
strategy that allows gradual rollout without
coordinating all 8 consumer deployments simultaneously.