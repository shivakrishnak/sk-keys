---
version: 2
layout: default
title: "Fan-Out Pattern"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /big-data-streaming/fan-out-pattern/
id: BIG-027
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Apache Kafka, Consumer Group, Kafka Topic / Partition / Offset
used_by: Event-Driven Architecture, Microservices, Distributed Systems
related: Consumer Group, Point-to-Point vs Pub-Sub, Event-Driven Architecture
tags:
  - fan-out
  - pub-sub
  - consumer-groups
  - kafka
  - event-driven
---

# BIG-027 - Fan-Out Pattern

⚡ TL;DR - **Fan-Out** distributes a single event to **multiple independent consumers** - in Kafka, achieved by having **multiple consumer groups** on the same topic; each consumer group gets its own independent offset cursor and receives all messages; one `order-placed` event can simultaneously trigger inventory service, notification service, and billing service via separate consumer groups - no duplication in the source, full independence in consumption.

| #552            | Category: Big Data & Streaming                                       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, Consumer Group, Kafka Topic / Partition / Offset       |                 |
| **Used by:**    | Event-Driven Architecture, Microservices, Distributed Systems        |                 |
| **Related:**    | Consumer Group, Point-to-Point vs Pub-Sub, Event-Driven Architecture |                 |

---

### 🔥 The Problem This Solves

**BROADCASTING EVENTS TO MULTIPLE DOWNSTREAM SYSTEMS:**
An order service creates an order. It needs to notify: inventory service (reserve stock), billing service (charge customer), email service (send confirmation), analytics service (record for reporting), and fraud service (check for fraud). One approach: OrderService makes 5 HTTP calls. Problem: high coupling, synchronous blocking, partial failure (2 of 5 succeed before crash). Kafka Fan-Out: OrderService publishes one event to Kafka. Five consumer groups (one per downstream service) each independently consume all events. Publisher knows nothing about consumers - zero coupling.

---

### 📘 Textbook Definition

**Fan-Out** is a messaging pattern where a single event is delivered to multiple independent consumers or consumer groups. In Kafka:

- **Single source topic**: events are written once.
- **Multiple consumer groups**: each group has independent offset tracking in `__consumer_offsets`.
- **All groups receive all events**: each group reads from offset 0 of each partition independently.
- **Independent processing**: one consumer group's failure, lag, or error doesn't affect others.
- **No duplication in the topic**: each event is stored once in Kafka, regardless of how many consumer groups consume it.

This is the **Publish-Subscribe (Pub-Sub) model** in Kafka terminology.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Fan-out = publish one event → N consumer groups each independently receive and process it; producers don't know about consumers.

**One analogy:**

> A TV broadcast: one signal transmitted. Every TV (consumer group) in range receives the signal independently. Turning off one TV (stopping one consumer group) doesn't affect others. The broadcast tower (Kafka topic) doesn't know how many TVs are watching or what they're doing with the signal.

**One insight:**
Fan-out in Kafka is "free" - adding a new consumer group to consume an existing topic requires ZERO changes to the producer or topic. Just start a new service with a new `group.id`, and it begins consuming all historical messages from the retention window. This is one of Kafka's most powerful properties: you can add new consumers to existing event streams retroactively, without touching the producing service.

---

### 🔩 First Principles Explanation

**IMPLEMENTING FAN-OUT WITH CONSUMER GROUPS:**

```yaml
# application.yml - each service has its OWN group.id
# All services consume from the SAME topic "order-events"

# inventory-service/src/main/resources/application.yml:
spring:
  kafka:
    consumer:
      group-id: inventory-service-group
      bootstrap-servers: kafka:9092
      auto-offset-reset: earliest  # new group: start from earliest message in retention

# billing-service/application.yml:
spring:
  kafka:
    consumer:
      group-id: billing-service-group

# email-service/application.yml:
spring:
  kafka:
    consumer:
      group-id: email-service-group

# analytics-service/application.yml:
spring:
  kafka:
    consumer:
      group-id: analytics-service-group

# fraud-service/application.yml:
spring:
  kafka:
    consumer:
      group-id: fraud-service-group
```

```java
// Each service has its own listener - completely independent:
// inventory-service:
@KafkaListener(topics = "order-events", groupId = "inventory-service-group")
public void handleOrderForInventory(OrderPlacedEvent event) {
    inventoryService.reserveStock(event.getProductId(), event.getQuantity());
}

// billing-service:
@KafkaListener(topics = "order-events", groupId = "billing-service-group")
public void handleOrderForBilling(OrderPlacedEvent event) {
    billingService.chargeCustomer(event.getCustomerId(), event.getAmount());
}

// email-service:
@KafkaListener(topics = "order-events", groupId = "email-service-group")
public void handleOrderForEmail(OrderPlacedEvent event) {
    emailService.sendConfirmation(event.getCustomerEmail(), event.getOrderId());
}

// All three handle the SAME event INDEPENDENTLY:
// - If billing-service is down, inventory-service and email-service continue
// - If email-service is 1 hour behind (high lag), inventory-service is unaffected
// - Order producer knows nothing about these consumers
```

**RETROACTIVE CONSUMER - ADDING NEW SERVICE TO EXISTING STREAM:**

```java
// 6 months later: new fraud-service needs to process all historical orders

@Configuration
public class FraudServiceConfig {
    @Bean
    public ConsumerFactory<String, OrderPlacedEvent> fraudConsumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "fraud-service-group");
        // NEW GROUP: no committed offsets yet
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        // "earliest" → starts from the beginning of Kafka's retention window
        // If retention=30 days: fraud-service will process all orders from last 30 days
        // Order producer: ZERO changes required
        return new DefaultKafkaConsumerFactory<>(props);
    }
}

// fraud-service consumer:
@KafkaListener(topics = "order-events", groupId = "fraud-service-group")
public void handleOrderForFraud(OrderPlacedEvent event) {
    fraudService.analyzeOrder(event);
    // Processes all 30 days of history, then catches up to real-time
    // While catching up: other consumer groups continue unaffected
}
```

**FAN-OUT WITH TOPIC FILTERING (SELECTIVE FAN-OUT):**

```java
// Some consumers want ALL events; others want filtered subsets

// Pattern 1: Consumer-side filtering (waste: consume all, discard most)
@KafkaListener(topics = "order-events")
public void handleHighValueOrders(OrderPlacedEvent event) {
    if (event.getAmount() > 10000) {
        vipOrderService.process(event);
    }
    // Consumer receives ALL events but only processes high-value ones
    // Inefficient for very selective filters
}

// Pattern 2: Topic-based routing (upstream) - create specialized topics
// In order-service (or via ksqlDB):
// CREATE STREAM high_value_orders AS SELECT * FROM order_events WHERE amount > 10000;
// "high-value-order-events" topic - VIP consumer reads from this specialized topic

// Pattern 3: Multiple topics with producer routing
@KafkaListener(topics = {"high-value-orders", "standard-orders"})
// Consumer subscribes to multiple topics
```

**FAN-OUT vs COMPETING CONSUMERS:**

```
Fan-Out (multiple consumer GROUPS):
  Topic: [M1][M2][M3][M4][M5]
  Group A (inventory): reads M1,M2,M3,M4,M5  (own offset)
  Group B (billing):   reads M1,M2,M3,M4,M5  (own offset)
  Group C (email):     reads M1,M2,M3,M4,M5  (own offset)
  → Each message processed by EACH group = broadcast semantics

Competing Consumers (multiple consumers in ONE group):
  Topic: [M1][M2][M3][M4][M5]
  Group X, Consumer 1: reads M1,M3,M5  (partition 0,2)
  Group X, Consumer 2: reads M2,M4     (partition 1,3)
  → Each message processed by EXACTLY ONE consumer = work-queue semantics
  → Used for: parallelism, load distribution (see: Competing Consumers pattern)
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS WHEN ONE FAN-OUT CONSUMER IS SLOW?**

- inventory-service: lag = 0 (fully caught up)
- billing-service: lag = 50,000 (slow - database bottleneck)
- email-service: lag = 0 (fully caught up)

The billing-service being 50,000 messages behind has NO effect on inventory-service or email-service. Each consumer group has its own committed offset in `__consumer_offsets`. Kafka retains messages for all groups until retention expires - even groups that are behind.

However: if billing-service's lag grows beyond Kafka's retention period (e.g., 7 days), billing-service will start missing messages (oldest messages expire before billing-service reads them). Solution: alert on consumer lag AND ensure retention is longer than max acceptable service downtime.

---

### 🧠 Mental Model / Analogy

> Fan-out is like a newsletter. You write one newsletter (Kafka topic). Anyone with a subscription (consumer group) gets their own copy independently. New subscribers can request back issues (historical messages within retention). Slow readers don't block other subscribers. Unsubscribing one reader doesn't affect others. The newsletter publisher doesn't know who's reading or how they're using the content.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Fan-out = one topic, many consumer groups, each gets all messages independently. Used in event-driven microservices. Adding a new consumer group requires zero changes to producer.

**Level 2:** Each consumer group has independent offsets in `__consumer_offsets`. New group with `auto-offset-reset=earliest` gets all messages within retention window. Consumer failures in one group don't affect others. Fan-out vs competing consumers: different `group.id` = broadcast; same `group.id` = work queue.

**Level 3:** Selective fan-out: topic-based routing (create sub-topics via ksqlDB or producer-side routing), or consumer-side filtering (read all, process some). Retention tradeoff: if one fan-out consumer can be down for a week, topic retention must be > 1 week. Monitor lag for ALL consumer groups on a topic - a lagging group isn't visible to the producer.

**Level 4:** Fan-out with ordering guarantee: if downstream services must process events in order (billing before shipping), fan-out alone doesn't guarantee this - each group advances independently. Solutions: (1) orchestration service that coordinates cross-service ordering via sagas; (2) event chaining (billing publishes "payment-confirmed" event, shipping listens on that); (3) choreography-based sagas (each service advances the saga state machine independently). Fan-out is not a substitute for saga orchestration when ordering between services matters.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ KAFKA FAN-OUT WITH MULTIPLE CONSUMER GROUPS          │
├──────────────────────────────────────────────────────┤
│                                                      │
│ "order-events" Topic (3 partitions):                │
│ P0: [M1][M4][M7]...                                 │
│ P1: [M2][M5][M8]...                                 │
│ P2: [M3][M6][M9]...                                 │
│                                                      │
│ inventory-group:  P0@offset=7, P1@offset=8, P2@offset=9 (caught up)│
│ billing-group:    P0@offset=3, P1@offset=4, P2@offset=3 (50K behind)│
│ email-group:      P0@offset=7, P1@offset=8, P2@offset=9 (caught up)│
│ [FAN-OUT ← YOU ARE HERE: independent offset per group]│
│                                                      │
│ billing-group lagging:                              │
│   inventory-group and email-group: UNAFFECTED       │
│   Kafka retains messages until retention expires    │
│   (not until all groups consume - retention is time-based)│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order placed - fan-out to 4 downstream services:

T=0: order-service publishes OrderPlacedEvent {orderId: X, productId: P1, customerId: C1}
     → "order-events" P2, offset 99501 (hash(orderId) → P2)

T=1ms: inventory-service-group consumer (already caught up):
       reads offset 99501 from P2 → inventoryService.reserveStock(P1, qty=2)
       → Updates inventory DB → commits offset 99502

T=2ms: billing-service-group consumer:
       reads offset 99501 (has its own offset pointer to P2)
       → billingService.chargeCustomer(C1, $150) → DB write
       → commits offset 99502

T=3ms: email-service-group consumer:
       → emailService.sendConfirmation("customer@email.com", orderId=X)

T=5ms: fraud-service-group (new service, 3 months behind):
       reads offset 45000 from P2 (different position!)
       → Processes 3-month-old order - independent of other groups

All 4 services: processed the same event independently.
order-service: wrote the event ONCE.
order-service: knows nothing about which services consume it.
```

---

### ⚖️ Comparison Table

| Pattern             | Receivers per Message | Group Config                        | Use Case                               |
| ------------------- | --------------------- | ----------------------------------- | -------------------------------------- |
| Fan-Out (Pub-Sub)   | All subscriber groups | Multiple group.ids                  | Broadcast to multiple services         |
| Competing Consumers | Exactly one consumer  | Single group.id, multiple consumers | Parallel processing, load distribution |
| Point-to-Point      | One receiver          | Single consumer                     | Simple queue replacement               |

| Fan-Out in Kafka vs Other Systems |                                                         |
| --------------------------------- | ------------------------------------------------------- |
| RabbitMQ Fanout Exchange          | Routes to all bound queues (push model)                 |
| Kafka multiple consumer groups    | Pull model, independent offsets, retention-based replay |
| SNS → multiple SQS                | AWS-native fan-out: SNS broadcasts to N SQS queues      |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Fan-out means Kafka copies the message N times"  | Kafka stores each message ONCE. Multiple consumer groups share the same partition log, each with their own offset pointer. No data duplication                                                                                                                         |
| "Fan-out guarantees all services process in sync" | Each consumer group advances independently. No guarantee that inventory-service and billing-service process the same event at the same time                                                                                                                            |
| "Removing a consumer group is immediate"          | If consumer group stops committing offsets, Kafka's group coordinator marks it inactive after `session.timeout.ms`. The offsets remain in `__consumer_offsets` until `offsets.retention.minutes` expires (default 7 days). After that, the group's offsets are deleted |

---

### 🚨 Failure Modes & Diagnosis

**1. One Consumer Group Falling Far Behind (Retention Risk)**

**Symptom:** One fan-out consumer group (e.g., analytics-service) is days behind. Topic retention is 7 days. Risk: analytics-service will miss messages if it doesn't catch up before retention expires.

**Fix:**

1. Increase topic retention: `kafka-topics.sh --alter --topic order-events --config retention.ms=2592000000` (30 days).
2. Alert when consumer lag > 50% of retention duration.
3. Scale analytics-service consumers (up to partition count).
4. For cold replay (beyond retention): export events to S3 first, then replay from S3.

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Consumer Group
**Builds On This:** Event-Driven Architecture
**Related:** Consumer Group, Point-to-Point vs Pub-Sub, Event-Driven Architecture

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN     │ 1 topic → N consumer groups → all get it  │
│ KEY PROP    │ Different group.id = independent offsets  │
│ PRODUCER    │ Publishes ONCE; knows nothing about consumers│
│ RETROACTIVE │ New group + auto-offset-reset=earliest    │
│ ISOLATION   │ Group A lag/failure = no impact on Group B│
│ vs COMPETING│ Same group.id = work queue (divide work)  │
│ RETENTION   │ Slowest group must catch up before expire │
│ MONITOR     │ Track lag for ALL groups on a topic       │
│ STORAGE     │ Message stored ONCE (no duplication)      │
│ ONE-LINER   │ "Multiple consumer groups = each group    │
│             │  independently reads all messages; broadcast"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) How does Kafka implement the fan-out pattern? What is the role of the consumer group ID? Why can multiple consumer groups each read all messages from the same topic without interfering with each other?

**Q2.** (TYPE C - Design) An e-commerce platform has an "orders" Kafka topic. Three new services need to consume from it: analytics (can tolerate 1-day delay), fraud-detection (must be near real-time, <1s), and inventory (must be real-time). Design the fan-out architecture, topic retention settings, monitoring strategy, and failure isolation for this setup.
