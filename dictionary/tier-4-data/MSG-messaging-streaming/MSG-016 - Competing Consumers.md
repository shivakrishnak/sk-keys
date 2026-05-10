---
version: 2
layout: default
title: "Competing Consumers"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /messaging-streaming/competing-consumers/
id: MSG-023
category: Messaging & Event Streaming
difficulty: ★★☆
depends_on: Point-to-Point vs Pub-Sub, Consumer Group, Message Ordering
used_by: Task Parallelism, Load Balancing, Work Queue Scaling
related: Point-to-Point vs Pub-Sub, Fan-Out Pattern, Consumer Group
tags:
  - competing-consumers
  - work-queue
  - load-balancing
  - consumer-group
  - parallelism
---

# MSG-037 - Competing Consumers

⚡ TL;DR - **Competing Consumers** pattern: multiple consumer instances on the **same queue or consumer group** - each message processed by **exactly one consumer** - enables horizontal scale-out (add consumers → more throughput); Kafka: max parallelism = partition count (consumer instances > partitions = idle instances); RabbitMQ: unlimited competing consumers (no partition limit); requires **idempotent consumers** (message may be redelivered on consumer crash before ack); **fair dispatch** (prefetch=1 in RabbitMQ; Kafka: partition count = parallelism ceiling).

| #566            | Category: Big Data & Streaming                              | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Point-to-Point vs Pub-Sub, Consumer Group, Message Ordering |                 |
| **Used by:**    | Task Parallelism, Load Balancing, Work Queue Scaling        |                 |
| **Related:**    | Point-to-Point vs Pub-Sub, Fan-Out Pattern, Consumer Group  |                 |

---

### 🔥 The Problem This Solves

**ONE CONSUMER IS A BOTTLENECK:**
An order processing service receives 10,000 orders/minute. One consumer can process 1,000 orders/minute. Queue grows unboundedly. Solution: run 10 consumer instances - each picks up different orders from the queue. 10× throughput. No ordering conflicts: each order processed by exactly one consumer. This is the Competing Consumers pattern: horizontal scale-out for message processing without coordination overhead.

---

### 📘 Textbook Definition

**Competing Consumers** is a messaging pattern where multiple consumer instances subscribe to the **same queue or consumer group** to process messages in parallel. Each message is consumed by exactly one consumer (P2P semantics at the consumer level).

**Key Properties:**

- **Load balancing**: the broker distributes messages among available consumers.
- **Scale-out**: add consumers → reduce consumer lag → higher throughput.
- **Fault tolerance**: if one consumer crashes, its unacknowledged messages are redelivered to another consumer (with manual ack).
- **Idempotency**: required if messages can be redelivered after consumer crash (at-least-once delivery).
- **Parallelism ceiling (Kafka)**: cannot exceed partition count. Consumer instances > partitions → extra consumers idle.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Competing consumers = N instances share ONE queue/group → each message processed by exactly ONE consumer; scale: add instances; Kafka limit = partition count; requires idempotency.

**One analogy:**

> A fast-food restaurant (Kafka topic = order queue). 5 cashiers (competing consumers) all look at the SAME customer queue. Customer (message) goes to the first available cashier. No two cashiers serve the same customer. More customers than cashiers → queue grows. Hire more cashiers (add consumers) → queue shrinks.

**One insight:**
In Kafka, the partition count is the hard ceiling for parallelism in a consumer group. Planning for future scale-out: create topics with MORE partitions than currently needed (partitions can be added later, but changing the partition count is operationally disruptive for keyed topics - key routing changes). Common starting point: 12 partitions (divisible by 1, 2, 3, 4, 6, 12 - flexible consumer counts). RabbitMQ has no such limit: add consumers freely.

---

### 🔩 First Principles Explanation

**COMPETING CONSUMERS WITH KAFKA:**

```java
// Kafka: competing consumers = multiple instances of same consumer group

// application.yml:
spring:
  kafka:
    consumer:
      group-id: order-processor     # ALL instances use this SAME group-id
      auto-offset-reset: latest
      max-poll-records: 50          # max records per poll (controls throughput)

@Service
public class OrderConsumer {

    @KafkaListener(
        topics = "order-events",
        groupId = "order-processor",    // same group-id = competing consumers
        concurrency = "3"               // 3 threads per instance
    )
    public void processOrder(ConsumerRecord<String, OrderEvent> record) {
        log.info("Processing order {} on partition {} thread {}",
            record.key(), record.partition(), Thread.currentThread().getName());
        orderService.process(record.value());
    }
}

// Deployment scenario:
// Topic: "order-events" with 12 partitions
// Instance 1 (concurrency=3): threads handle partitions 0,1,2 / 3,4,5 / 6,7,8
// Instance 2 (concurrency=3): threads handle partitions 9,10,11 (remaining)
//
// Wait: 3 threads on instance 1 × 4 partitions each? No:
// 3 threads × 2 instances = 6 consumers total, 12 partitions → 2 partitions per consumer
//
// Parallelism: min(total consumer threads, partition count)
// = min(3×2, 12) = min(6, 12) = 6 parallel consumers → 6 partitions processed simultaneously

// Scale up (add instance 3):
// 3 threads × 3 instances = 9 consumers → 9 partitions active simultaneously
// 3 partitions become idle after redistribution (triggers rebalance)

// MAX PARALLELISM: 12 instances × 1 thread = 12 consumers = 12 partitions
// BEYOND MAX: 13th instance → idle (0 partitions assigned) → wasteful
```

**COMPETING CONSUMERS WITH RABBITMQ:**

```java
// RabbitMQ: no partition limit - add consumers freely
// All instances listen to same queue = competing consumers

@Service
public class OrderConsumer {

    // concurrency: 3 threads per instance (3 competing consumers per instance)
    @RabbitListener(queues = "orders.processing", concurrency = "3-10")
    // "3-10": min 3, max 10 threads dynamically based on queue depth
    public void processOrder(Order order, Channel channel,
                              @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag)
            throws IOException {
        try {
            orderService.process(order);
            channel.basicAck(deliveryTag, false);
        } catch (Exception e) {
            channel.basicNack(deliveryTag, false, false);  // DLQ
        }
    }
}

// Deploy 5 instances × 3 threads = 15 competing consumers
// Queue depth: 1000 orders
// Each consumer: picks up one order, processes, acks, picks up next
// Throughput: 15 orders in parallel

// FAIR DISPATCH with prefetchCount=1:
// Consumer is only given 1 unacknowledged message at a time
// Slow consumer: doesn't get more work while still processing
// Fast consumer: gets more work faster
// Without prefetch (default unlimited): broker sends all messages to first consumer
// that connects → unfair → slow consumer gets overwhelmed

@Bean
public SimpleRabbitListenerContainerFactory rabbitListenerContainerFactory(
        ConnectionFactory factory) {
    SimpleRabbitListenerContainerFactory containerFactory =
        new SimpleRabbitListenerContainerFactory();
    containerFactory.setConnectionFactory(factory);
    containerFactory.setPrefetchCount(1);  // strict fair dispatch
    // tradeoff: prefetch=1 → lower throughput (wait for each ack before next)
    // prefetch=10 → better throughput, less perfect fairness
    containerFactory.setAcknowledgeMode(AcknowledgeMode.MANUAL);
    return containerFactory;
}
```

**IDEMPOTENCY REQUIREMENT:**

```java
// Consumer crashes after processing but BEFORE ack
// Broker: no ack received → redelivers message to another consumer
// Same message processed TWICE = double-charge, double-ship, double-inventory-deduct

// SOLUTION: idempotent consumer
@Service
public class IdempotentOrderConsumer {

    @Autowired
    private ProcessedMessageRepository processedRepo;

    @KafkaListener(topics = "order-events", groupId = "order-processor")
    @Transactional
    public void processOrder(ConsumerRecord<String, OrderEvent> record) {
        String messageId = record.key();  // or deduplicated messageId in payload

        // Check if already processed:
        if (processedRepo.existsByMessageId(messageId)) {
            log.info("Skipping duplicate message: {}", messageId);
            return;  // idempotent: skip duplicates
        }

        // Process (in same transaction):
        orderService.fulfillOrder(record.value());

        // Record as processed:
        processedRepo.save(new ProcessedMessage(messageId, Instant.now()));

        // Transaction: both DB writes atomic
        // If crash between process() and save(): replays → processedRepo.exists() = false → reprocesses
        // If crash after save() commits: redelivered → processedRepo.exists() = true → skip
        // At-least-once (broker) + idempotent consumer = effectively exactly-once
    }
}

// Alternative idempotency: database UNIQUE constraint
// orders table: UNIQUE(order_id)
// Process: INSERT INTO orders (id, ...) VALUES (orderId, ...)
// On duplicate: throws DataIntegrityViolationException
//   → catch it → log "duplicate" → skip processing
// Simpler: no processedRepo table needed
@Transactional
public void processOrder(OrderEvent event) {
    try {
        Order order = new Order(event.getOrderId(), ...);
        orderRepository.save(order);  // UNIQUE(order_id) constraint
        // if duplicate → throws ConstraintViolationException
        paymentService.charge(order);
    } catch (DataIntegrityViolationException e) {
        log.info("Duplicate order {}, skipping", event.getOrderId());
        // Don't rethrow: idempotent skip
    }
}
```

**PARTITION PLANNING FOR KAFKA:**

```
Planning competing consumers capacity:

Current load: 100 orders/min, 1 consumer handles 50/min → 2 consumers needed
Future load (6 months): 600 orders/min → 12 consumers needed

Partition count strategy:
  DON'T create 2 partitions (max concurrency = 2 = future bottleneck)
  CREATE 12 partitions now (can run 2 today, scale to 12 later)

  Rebalance: adding consumers within capacity = automatic rebalance (fast)
  Adding partitions: partition reassignment needed (operationally complex for keyed topics)

Why divisible numbers matter:
  12 partitions: can distribute to 1, 2, 3, 4, 6, or 12 consumers evenly
  13 partitions: works for 1 or 13, awkward for 2 (6+7), 3 (4+4+5)

  Choose partition count = expected MAX parallel consumers
  (or a round multiple like 12, 24, 48)
```

---

### 🧪 Thought Experiment

**CONSUMER REBALANCE COST:**

10 consumers in a Kafka consumer group processing 100 partitions (10 partitions each). One consumer crashes. Rebalance triggered: 9 remaining consumers must be assigned the 10 orphaned partitions. During rebalance: ALL 9 consumers stop processing (stop-the-world rebalance by default in older Kafka). In Kafka 2.4+: cooperative rebalance - only the affected partitions are reassigned; others continue processing. Key config: `partition.assignment.strategy=CooperativeStickyAssignor` (Kafka 2.4+) to minimize rebalance downtime. Important for large consumer groups (10+ consumers) with frequent restarts.

---

### 🧠 Mental Model / Analogy

> **Competing Consumers** = a checkout at a grocery store. Multiple cashiers (consumers), one shared queue of customers (messages). Each customer (message) handled by exactly one cashier. Long queue? Open more checkout lanes (add consumers). Kahier on break (consumer crashes)? Customers requeue (messages redelivered).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Multiple consumers on same queue/group → each message processed once. Add consumers → more throughput. Kafka: ceiling = partition count. RabbitMQ: no ceiling. Needs idempotency.

**Level 2:** Kafka: `groupId` determines competing consumer set. Parallelism = min(consumers, partitions). Don't deploy more consumers than partitions. Plan partition count for future scale (12 is good default). RabbitMQ: prefetch=1 for fairness, prefetch=10 for throughput. Manual ack required for reliability.

**Level 3:** Rebalance (Kafka): triggered by consumer join/leave. Old: stop-the-world (all pause). New: `CooperativeStickyAssignor` (partial reassignment, minimal downtime). Session timeout tuning: `heartbeat.interval.ms` (3s default) vs `session.timeout.ms` (45s default). Slow processing → `max.poll.interval.ms` exceeded → consumer kicked out of group → rebalance → redelivery. Fix: `max.poll.records=1` if processing is slow.

**Level 4:** Consumer group protocol (JoinGroup, SyncGroup): when a consumer joins, it sends JoinGroup to group coordinator (a Kafka broker). Coordinator waits for all to join (joinTimeout) then elects a group leader (first to join). Leader computes partition assignment → sends to coordinator via SyncGroup → coordinator distributes back to all members. For large groups (100+ consumers): this coordination has overhead. Kafka KIP-848 (consumer group rebalance redesign): incremental cooperative protocol to avoid full rebalance even at join/leave time. Critical for serverless/autoscaling workloads where consumers join/leave frequently.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ COMPETING CONSUMERS: KAFKA                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Topic: "order-events" (12 partitions)               │
│                                                      │
│ Consumer Group "order-processor" (4 instances):     │
│   Instance 1: handles partitions 0, 1, 2            │
│   Instance 2: handles partitions 3, 4, 5            │
│   Instance 3: handles partitions 6, 7, 8            │
│   Instance 4: handles partitions 9, 10, 11          │
│   → 4 parallel consumers, each processing 3 partitions│
│                                                      │
│ Instance 3 crashes:                                 │
│   Rebalance: partitions 6,7,8 reassigned to 1,2,4  │
│   Instance 1: now handles 0,1,2,6                   │
│   Instance 2: handles 3,4,5,7                       │
│   Instance 4: handles 8,9,10,11                     │
│   No data loss: messages from partitions 6-8        │
│   re-read from last committed offset                │
│                                                      │
│ Scale up (add Instance 5,6):                        │
│   Rebalance: 12 partitions / 6 consumers = 2 each  │
│   Throughput: 3× original (6 vs 2 initial consumers)│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order processing at peak load (Black Friday):

Normal (2 consumer instances, 4 partitions):
  Consumer 1: partitions 0,1 → processes 500 orders/min
  Consumer 2: partitions 2,3 → processes 500 orders/min
  Total: 1,000 orders/min
  Lag: 0

Peak (orders spike to 5,000/min):
  Lag: grows 4,000/min
  Alert: consumer lag > 10,000 messages

Auto-scale (KEDA: Kafka-based HPA):
  Detects lag → scales consumer deployment from 2 → 4 instances
  Each instance: concurrency=1 → 4 competing consumers
  Rebalance: 4 partitions / 4 consumers = 1 partition each
  BUT: only 4 partitions → 4 is the max! 5th instance would be idle.

Throughput with 4 consumers: 2,000 orders/min (constrained by partitions)
Lag: still growing at 3,000/min

Lesson: topic had only 4 partitions - insufficient for Black Friday
Fix: recreate topic with 20 partitions before next sale → 20 max consumers
     KEDA can scale up to 20 instances → fully drain the lag
```

---

### ⚖️ Comparison Table

| Dimension          | Kafka Competing Consumers     | RabbitMQ Competing Consumers                   |
| ------------------ | ----------------------------- | ---------------------------------------------- |
| Parallelism limit  | Partition count               | Unlimited (no limit)                           |
| Scale up           | Add instances (rebalance)     | Add instances (immediate)                      |
| Message ordering   | Per-partition only            | Per-queue (single thread) or none (concurrent) |
| Idempotency needed | Yes (redelivery on crash)     | Yes (nack + requeue)                           |
| Fair dispatch      | Partition assignment (sticky) | Prefetch count (prefetch=1)                    |
| Replay             | Yes (offset replay)           | No (consumed = deleted)                        |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                           |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "More consumers always means more throughput" | In Kafka: capped at partition count. Adding consumers beyond partition count = idle consumers. Zero throughput increase. The bottleneck shifts to partition count, not consumer count                                             |
| "Competing consumers guarantee ordering"      | Only within a Kafka partition (single consumer). No global ordering across partitions. RabbitMQ with multiple consumers: no ordering guarantee (round-robin dispatch)                                                             |
| "Competing consumers don't need idempotency"  | At-least-once delivery: if consumer crashes after processing but before ack, the message is redelivered to another consumer. Without idempotency: double-processing. Always implement idempotent consumers for critical workflows |

---

### 🚨 Failure Modes & Diagnosis

**1. max.poll.interval.ms Exceeded - Consumer Kicked Out**

**Symptom:** Consumer log: `org.apache.kafka.clients.consumer.CommitFailedException: Offset commit cannot be completed...` Frequent rebalances. Messages processed multiple times.

**Root Cause:** Processing one batch of messages takes longer than `max.poll.interval.ms` (default: 5 minutes). Kafka broker assumes consumer is dead → removes from group → triggers rebalance → messages redelivered.

**Fix:**

```java
// Option 1: Reduce records per poll → faster processing per poll cycle
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 10);  // process only 10 at a time

// Option 2: Increase max.poll.interval.ms for genuinely slow processing
props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 600_000);  // 10 minutes

// Option 3: Process asynchronously + manual commit
@KafkaListener(topics = "order-events", containerFactory = "manualAckFactory")
public void processOrder(ConsumerRecord<String, OrderEvent> record, Acknowledgment ack) {
    // Async: submit to thread pool, ack when done
    executor.submit(() -> {
        orderService.process(record.value());
        ack.acknowledge();  // commit offset after processing
    });
    // Return immediately → poll() called again → heartbeat maintained
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Point-to-Point vs Pub-Sub, Consumer Group
**Builds On This:** Load Balancing, Autoscaling with KEDA
**Related:** Point-to-Point vs Pub-Sub, Fan-Out Pattern, Consumer Group

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION  │ Multiple consumers, same queue/group      │
│ EACH MSG    │ Processed by exactly ONE consumer         │
│ KAFKA LIMIT │ Max consumers = partition count           │
│ RABBITMQ    │ No limit (add consumers freely)           │
│ IDEMPOTENCY │ Required (redelivery on crash)            │
│ PREFETCH=1  │ Fair dispatch (RabbitMQ)                  │
│ PARTITION # │ Plan ahead: create more than current need │
│ REBALANCE   │ CooperativeStickyAssignor for minimal stop│
│ POLL ISSUE  │ max.poll.interval.ms > processing time   │
│ SCALE       │ Add consumers up to partition count       │
│ ONE-LINER   │ "Multiple workers, one queue: each       │
│             │  message to ONE worker; Kafka capped at  │
│             │  partition count; needs idempotency"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the Competing Consumers pattern? How does it differ between Kafka and RabbitMQ? What is the parallelism ceiling in Kafka and why does it exist?

**Q2.** (TYPE B - Bug Hunt) A Kafka consumer group with 8 instances processes an "order-events" topic with 4 partitions. Throughput is not improving despite having 8 instances. What is the root cause? What should you do to achieve 8× parallelism?
