---
version: 2
layout: default
title: "Point-to-Point vs Pub-Sub"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/messaging-streaming/point-to-point-vs-pub-sub/
id: MSG-036
category: Messaging & Event Streaming
difficulty: ★★☆
depends_on: Message Broker vs Event Bus, RabbitMQ, Apache Kafka
used_by: Messaging Architecture, Microservices, Event-Driven Systems
related: Competing Consumers, Fan-Out Pattern, RabbitMQ
tags:
  - point-to-point
  - pub-sub
  - queue
  - topic
  - messaging-patterns
---

⚡ TL;DR - **Point-to-Point (Queue)**: message sent to ONE receiver only - competing consumers share the queue, each message consumed exactly once - ideal for task distribution (work queues); **Publish-Subscribe (Topic)**: message broadcast to ALL subscribers - each subscriber gets its own copy - ideal for event broadcasting (fan-out); tools: RabbitMQ queues = P2P; RabbitMQ fanout exchange = Pub-Sub; Kafka topic with ONE consumer group = P2P; Kafka topic with MULTIPLE consumer groups = Pub-Sub.

| #565            | Category: Big Data & Streaming                              | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Message Broker vs Event Bus, RabbitMQ, Apache Kafka         |                 |
| **Used by:**    | Messaging Architecture, Microservices, Event-Driven Systems |                 |
| **Related:**    | Competing Consumers, Fan-Out Pattern, RabbitMQ              |                 |

---

### 🔥 The Problem This Solves

**WHICH CONSUMERS GET WHICH MESSAGES?**
An e-commerce platform places an order. Three things must happen: (1) deduct inventory, (2) charge payment, (3) send confirmation email. If all three share one queue (P2P): the first consumer to pick up the message handles it - only ONE of the three services gets the order. That's wrong. Each service needs its own copy (Pub-Sub). Conversely, if five instances of the inventory service all subscribe to a Pub-Sub topic, all five get the same message and all five try to deduct the same inventory. That's also wrong. For load balancing the inventory service: P2P (each message to ONE instance). Understanding P2P vs Pub-Sub is fundamental to getting messaging semantics right.

---

### 📘 Textbook Definition

**Point-to-Point (Queue Model)**:

- Producer sends message to a **queue**.
- **Exactly one consumer** receives each message.
- Multiple consumers on the same queue = **competing consumers** (load balancing, NOT broadcast).
- Message removed from queue after consumption.
- Use for: **task distribution** - one of N workers picks up the task.

**Publish-Subscribe (Topic/Fan-Out Model)**:

- Publisher sends message to a **topic** (or exchange).
- **All subscribers** receive a copy of the message.
- Each subscriber gets its own independent copy.
- Producer doesn't know how many subscribers exist (decoupled).
- Use for: **event broadcasting** - all interested parties notified.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
P2P queue = ONE consumer gets each message (load balancing); Pub-Sub topic = ALL subscribers get a copy (broadcasting); same queue+group.id = P2P; different group.ids = Pub-Sub.

**One analogy:**

> **P2P (Queue)**: A shared task list at work. One of your 5 team members picks up each task. No two people work on the same task simultaneously.
> **Pub-Sub (Topic)**: Company-wide email. Everyone gets a copy. 50 employees, 50 copies. Each reads independently.

**One insight:**
In Kafka, P2P and Pub-Sub are not separate mechanisms - they're the same topic with different consumer group configurations. Same group ID = competing consumers = P2P. Different group IDs = fan-out = Pub-Sub. This is Kafka's elegance: one system handles both patterns with no reconfiguration of the topic itself.

---

### 🔩 First Principles Explanation

**P2P WITH RABBITMQ (QUEUE):**

```java
// RabbitMQ: classic work queue (P2P)
// 3 order processor instances share ONE queue → competing consumers

// Configuration:
@Bean
public Queue orderQueue() {
    return QueueBuilder.durable("orders.processing").build();
}
// No exchange binding needed: publish directly to queue (default
// exchange)

// Producer: send to queue directly
@Service
public class OrderProducer {
    @Autowired
    private RabbitTemplate rabbitTemplate;

    public void queueOrder(Order order) {
        rabbitTemplate.convertAndSend("orders.processing", order);
        // Default exchange routes by queue name (direct exchange
        // behavior)
    }
}

// 3 consumer instances (all bound to same queue):
@Service
public class OrderProcessor {

    @RabbitListener(queues = "orders.processing", concurrency = "3")
    // concurrency=3: 3 concurrent consumer threads on THIS instance
    // Combined with 2 instances deployed: 6 total competing consumers
    public void processOrder(Order order) {
        orderService.process(order);
        // Each order processed by exactly ONE consumer
    }
}
// Result: 100 orders → distributed across all consumers → each order
// processed ONCE
```

**PUB-SUB WITH RABBITMQ (FANOUT EXCHANGE):**

```java
// RabbitMQ: fanout exchange = pub-sub
// ONE message → emailQueue + smsQueue + analyticsQueue

@Bean
public FanoutExchange orderEventsExchange() {
    return new FanoutExchange("order.events.fanout");
}

@Bean
public Queue emailNotificationQueue() {
    return QueueBuilder.durable("order.email.notifications").build();
}

@Bean
public Queue smsNotificationQueue() {
    return QueueBuilder.durable("order.sms.notifications").build();
}

@Bean
public Queue analyticsQueue() {
    return QueueBuilder.durable("order.analytics").build();
}

// Each service binds its own queue to the fanout exchange:
@Bean
public Binding emailBinding() {
    return BindingBuilder.bind(emailNotificationQueue())
        .to(orderEventsExchange());
}

@Bean
public Binding smsBinding() {
    return BindingBuilder.bind(smsNotificationQueue())
        .to(orderEventsExchange());
}

@Bean
public Binding analyticsBinding() {
    return BindingBuilder.bind(analyticsQueue())
        .to(orderEventsExchange());
}

// Producer: publish to fanout exchange
@Service
public class OrderEventPublisher {
    public void publishOrderPlaced(Order order) {
        rabbitTemplate.convertAndSend("order.events.fanout", "",
            order);
        // Fanout: message copied to ALL 3 queues
        // EmailService: reads from emailNotificationQueue → sends
        // email
        // SMSService: reads from smsNotificationQueue → sends SMS
        // AnalyticsService: reads from analyticsQueue → updates
        // dashboard
    }
}
```

**P2P AND PUB-SUB WITH KAFKA (SAME TOPIC, DIFFERENT GROUPS):**

```java
// Kafka: ONE topic, different behavior depending on consumer group

// SAME GROUP = P2P (work queue / load balancing):
@KafkaListener(topics = "order-events", groupId = "order-processor")
// Group "order-processor": 5 instances → each partition assigned to
// ONE instance
// Order processor 1: handles partitions 0, 1
// Order processor 2: handles partitions 2, 3
// → Each order processed ONCE

// DIFFERENT GROUPS = PUB-SUB (fan-out / broadcast):
// OrderProcessorService:
@KafkaListener(topics = "order-events", groupId = "order-processor")
public void processOrder(
    OrderEvent event) { /* handles fulfillment */ }

// EmailNotificationService (different service/JVM):
@KafkaListener(topics = "order-events",
    groupId = "email-notification")
public void sendEmail(
    OrderEvent event) { /* sends confirmation email */ }

// InventoryService (different service/JVM):
@KafkaListener(topics = "order-events", groupId = "inventory-service")
public void updateInventory(
    OrderEvent event) { /* decreases stock */ }

// AnalyticsService (different service/JVM):
@KafkaListener(topics = "order-events", groupId = "analytics")
public void trackOrder(OrderEvent event) { /* updates dashboard */ }

// Result: ONE order event → 4 independent groups → each group
// processes it independently
// Each group has its own __consumer_offsets entry
// New service (AnalyticsV2) with new groupId = "analytics-v2":
// → Can subscribe and read from BEGINNING
// (auto.offset.reset=earliest)
//   → Zero producer changes: Kafka retains all historical messages
```

**CHOOSING BETWEEN PATTERNS:**

```
DECISION TREE:

Q: Do you need every subscriber to receive every message?
   YES → PUB-SUB
   NO → P2P

Q: Do you need to distribute a task among workers for
  parallel processing?
   YES → P2P (competing consumers)
   NO → consider Pub-Sub

Q: Do multiple independent services need to react to the
  same event?
   YES → PUB-SUB
   NO → P2P to one specific service

Q: Kafka: how many consumer groups are subscribed to this
  topic?
   ONE group → P2P (work queue)
   MULTIPLE groups → Pub-Sub (fan-out to each group)

COMMON PATTERNS:

Order processing (load balancing): P2P
  Order placed → 1 of 5 order processors handles it (P2P)

Order notification (broadcast): Pub-Sub
  Order placed → email service + inventory service +
    analytics (all 3)

Mixed:
  Order placed → topic (Pub-Sub)
  → email-service group: 3 email workers (P2P within the
    group)
  → inventory-service group: 5 inventory workers (P2P
    within the group)
  → analytics group: 1 analytics worker

  = Fan-out at the group level (Pub-Sub between groups)
  + Work queue at the consumer level (P2P within each
    group)
```

---

### 🧪 Thought Experiment

**THE REPROCESSING ADVANTAGE OF KAFKA PUB-SUB:**

In RabbitMQ fanout: messages consumed and deleted. A new analytics service needs historical order data → cannot get it (already deleted). Must ask the order service for a bulk export (expensive, coupling).

In Kafka: messages retained for 7 days (or more). New analytics service with `groupId="analytics-v2"` subscribes with `auto.offset.reset=earliest` → replays all historical messages → bootstraps its state from history. Producer unchanged. This is the key advantage of Kafka's log-based model over RabbitMQ's fanout exchange.

---

### 🧠 Mental Model / Analogy

> **P2P Queue** = Shared to-do list. Each task can only be checked off by ONE person. 5 team members, 100 tasks → efficient parallel work.
> **Pub-Sub Topic** = Newsletter subscription. Everyone on the list gets every issue. 5 subscribers, 100 issues → each gets 100 copies.
> **Kafka consumer groups** = Multiple mailing lists that all receive the same newsletter, but members of each list share the reading (P2P within, Pub-Sub across lists).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** P2P = one consumer gets each message (queue, work distribution). Pub-Sub = all subscribers get each message (topic, broadcasting). Kafka: same groupId = P2P; different groupId = Pub-Sub.

**Level 2:** RabbitMQ P2P: direct queue. RabbitMQ Pub-Sub: fanout exchange + one queue per subscriber. Kafka: topic + consumer groups. In Kafka, P2P and Pub-Sub are the SAME topic - group configuration drives behavior. Kafka advantage: replay (new subscriber can read history).

**Level 3:** Competing consumers (P2P at scale): more consumers → more parallel processing → higher throughput. Kafka: limited by partition count (max consumers in a group = partition count). RabbitMQ: no partition limit - add consumers freely. For massive P2P parallelism: RabbitMQ or Kafka with many partitions.

**Level 4:** Hybrid patterns: topic + multiple consumer groups (Kafka fan-out) where each group uses multiple consumers (P2P within group). This is the standard production Kafka pattern: one topic, N services each with their own group, each service runs M instances (competing consumers within group). AWS SNS + SQS: SNS (Pub-Sub: fan-out to multiple SQS queues) + SQS (P2P: each SQS queue distributes to workers). Replicates Kafka's fan-out + competing consumers on AWS managed services.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ P2P vs PUB-SUB COMPARISON                            │
├──────────────────────────────────────────────────────┤
│                                                      │
│ P2P (Work Queue):                                   │
│   Producer → Queue → Consumer1 (gets msg1)          │
│                     → Consumer2 (gets msg2)         │
│                     → Consumer3 (gets msg3)         │
│   Each message: ONE consumer                        │
│   Purpose: parallel task processing                 │
│                                                      │
│ PUB-SUB (Topic/Fan-Out):                            │
│   Publisher → Topic → Consumer1 (gets copy of msg)  │
│                      → Consumer2 (gets copy of msg) │
│                      → Consumer3 (gets copy of msg) │
│   Each message: ALL consumers get a copy            │
│   Purpose: broadcasting events                      │
│                                                      │
│ KAFKA (unified):                                    │
│   Topic → Group A (3 consumers, P2P within group)  │
│         → Group B (5 consumers, P2P within group)  │
│         → Group C (1 consumer)                     │
│   Groups: Pub-Sub (each gets own copy)             │
│   Within group: P2P (competing consumers)          │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Event: Order Placed ($200 purchase)

1. OrderService publishes to Kafka topic "order-events":
   {orderId: "123", userId: "u456", amount: 200, items:
     [...]}

2. THREE consumer groups subscribed:

   Group "fulfillment" (5 instances of FulfillmentService):
     Kafka assigns partitions to 5 instances
     Instance 2 gets order-123 → picks items, creates
       shipment
     (P2P: one instance handles each order)

   Group "notification" (3 instances of
     NotificationService):
     Instance 1 gets order-123 → sends email + SMS to u456
     (P2P: one instance handles each notification)

   Group "analytics" (1 instance of AnalyticsService):
     Receives order-123 → updates revenue dashboard
     (P2P: one instance, effectively fan-out from
       fulfillment/notification)

3. Result:
   Each order: fulfilled by ONE FulfillmentService instance
   Each order: notified by ONE NotificationService instance
   Each order: tracked by analytics

4. New service added: FraudDetectionService,
  groupId="fraud-detection"
   Subscribes to "order-events", auto.offset.reset=latest
   Gets all FUTURE orders → no changes to producer or
     other consumers
   Zero coordination needed: Kafka's consumer group
     isolation
```

---

### ⚖️ Comparison Table

| Dimension               | Point-to-Point (Queue)             | Publish-Subscribe (Topic)               |
| ----------------------- | ---------------------------------- | --------------------------------------- |
| Message delivery        | ONE consumer receives              | ALL subscribers receive                 |
| Purpose                 | Task distribution / load balancing | Event broadcasting                      |
| Kafka implementation    | One consumer group                 | Multiple consumer groups                |
| RabbitMQ implementation | Direct queue                       | Fanout exchange + queues per subscriber |
| Scale-out               | Add consumers (share load)         | Add consumer groups (fan-out)           |
| Ordering                | Per-queue (with single consumer)   | Per-partition per group                 |
| Replay (Kafka)          | Yes (by group offset)              | Yes (each group independently)          |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                            |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Kafka is always Pub-Sub"                                   | Kafka is BOTH, depending on consumer group configuration. One consumer group = P2P (work queue). Multiple consumer groups = Pub-Sub (fan-out). Kafka is a log that multiple groups can read independently          |
| "In P2P, messages are always sent to ONE consumer instance" | P2P guarantees each message is consumed by ONE consumer in a group - but within a single consumer, messages may be batched. Each message is consumed by exactly one consumer at a time (with proper ack semantics) |
| "RabbitMQ only supports P2P"                                | RabbitMQ supports both: direct queues = P2P; fanout exchange = Pub-Sub. RabbitMQ's exchange model makes routing between the patterns flexible                                                                      |

---

### 🚨 Failure Modes & Diagnosis

**1. All 5 Consumer Instances Receive the Same Message (P2P Broken)**

**Symptom:** 5 inventory service instances all deduct stock for the same order → stock goes negative.

**Root Cause (RabbitMQ):** 5 instances subscribed to a **fanout exchange** (Pub-Sub) instead of a direct queue (P2P). Each instance has its own queue binding → all 5 receive each message.

**Root Cause (Kafka):** 5 instances using DIFFERENT `groupId` values instead of the same `groupId`. Each group gets an independent copy.

**Fix:**

```java
// KAFKA FIX: ensure all instances of the same service use THE SAME
// groupId
@KafkaListener(topics = "order-events", groupId = "inventory-service")
// All 5 instances: groupId = "inventory-service"
// Kafka: partitions distributed among the 5 instances → each message
// to one

// RABBITMQ FIX: use a direct queue, not fanout exchange
// All 5 instances: bind to the SAME queue
@RabbitListener(queues = "inventory.orders")
// All 5 instances: subscribe to the same queue → competing consumers
// → P2P
```

---

### 🔗 Related Keywords

**Prerequisites:** Message Broker vs Event Bus

**Builds On This:** Competing Consumers, Fan-Out Pattern

**Related:** Competing Consumers, Fan-Out Pattern, RabbitMQ

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ P2P         │ ONE consumer gets each message            │
│ PUB-SUB     │ ALL subscribers get each message          │
│ KAFKA P2P   │ Same groupId (competing consumers)        │
│ KAFKA PUBSUB│ Multiple groupIds (fan-out between groups)│
│ RABBIT P2P  │ Direct queue with multiple consumers      │
│ RABBIT PUBSUB│ Fanout exchange + queue per subscriber   │
│ P2P USE     │ Task queues, work distribution            │
│ PUBSUB USE  │ Event notification, broadcasting          │
│ REPLAY      │ Kafka: new group reads history; RMQ: NO  │
│ MIXED       │ Groups (pub-sub) + consumers in group (P2P│
│ ONE-LINER   │ "P2P: one picks it up; pub-sub: all get  │
│             │  a copy; Kafka: same group = P2P"        │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the difference between point-to-point and publish-subscribe messaging? For each, give a real-world use case and describe how you would implement it with Kafka or RabbitMQ.

**Q2.** (TYPE C - Design) An order management platform has these requirements: (1) Each order must be processed by exactly ONE fulfillment worker (5 fulfillment workers available). (2) Each order must also trigger email notification, inventory update, and analytics tracking - all independently. Design the Kafka topic and consumer group structure to support all requirements simultaneously.
