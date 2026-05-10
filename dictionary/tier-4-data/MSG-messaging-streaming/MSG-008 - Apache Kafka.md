---
version: 2
layout: default
title: "Apache Kafka"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /messaging-streaming/apache-kafka/
id: MSG-031
category: Messaging & Event Streaming
difficulty: ★★☆
depends_on: Distributed Computing, Messaging Systems
used_by: Kafka Topic / Partition / Offset, Consumer Group, ISR, Structured Streaming, Flink
related: Kafka Topic / Partition / Offset, Consumer Group, Distributed Systems
tags:
  - apache-kafka
  - event-streaming
  - message-broker
  - distributed-log
  - deep-dive
---

# MSG-010 - Apache Kafka

⚡ TL;DR - Apache Kafka is a **distributed event streaming platform** - a persistent, ordered, replicated **commit log** that producers write events to and consumers read from; originally built at LinkedIn for high-throughput activity feeds (millions of messages/second), it became the backbone of event-driven architectures: stream processing (with Kafka Streams/Flink/Spark), event sourcing, CDC, and microservice decoupling via topics and partitions.

| #540            | Category: Big Data & Streaming                                                     | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Computing, Messaging Systems                                           |                 |
| **Used by:**    | Kafka Topic / Partition / Offset, Consumer Group, ISR, Structured Streaming, Flink |                 |
| **Related:**    | Kafka Topic / Partition / Offset, Consumer Group, Distributed Systems              |                 |

---

### 🔥 The Problem This Solves

**DECOUPLING PRODUCERS FROM CONSUMERS AT SCALE:**
Before Kafka, microservices called each other directly (point-to-point HTTP) or through traditional message queues (RabbitMQ). Problems: (1) consumer outage blocks producers; (2) 10 consumers of the same event = 10 separate API calls; (3) events not persisted = replay impossible; (4) throughput bottleneck - traditional queues top out at ~100K messages/second. Kafka: producers write to a log, consumers read at their own pace, events retained for days/weeks (replayable), throughput scales to millions of messages/second by adding partitions.

---

### 📘 Textbook Definition

**Apache Kafka** is a distributed, partitioned, replicated **commit log service** with:

- **Topic**: a logical category of events (e.g., "orders", "payments", "user-clicks"). Divided into partitions.
- **Partition**: an ordered, immutable sequence of records (events). Each record has an offset (monotonically increasing integer). Partitions are distributed across brokers.
- **Producer**: writes events to a topic. Chooses which partition via partition key (hash) or round-robin.
- **Consumer**: reads events from partitions by tracking its current offset. Pulls data (not pushed).
- **Consumer Group**: N consumers sharing the work of a topic. Each partition assigned to exactly one consumer in the group - enables parallel consumption.
- **Broker**: a Kafka server node. Each broker stores some partitions.
- **ZooKeeper (legacy) / KRaft (Kafka 3.x+)**: cluster metadata storage and leader election.
- **Replication**: each partition has one leader (handles reads/writes) and N-1 followers (replicate from leader). ISR (In-Sync Replicas): followers that are fully caught up.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Kafka = distributed append-only log - producers append events, consumers read at their own pace by tracking offsets, events persisted for replay, millions of events/second by adding partitions.

**One analogy:**

> Kafka is a newspaper printing press and archive. Publishers (producers) print editions (events) to specific sections (topics/partitions). The newspaper archive stores all editions for 7 days (retention). Subscribers (consumers) read editions at their own pace - some read today's paper, some are catching up on last week's. Multiple readers (consumer group) can split up reading different sections (partitions). If you miss an edition: go back to the archive and re-read from where you left off (offset replay).

**One insight:**
The key Kafka insight: **the log is the source of truth**. Traditional message queues delete messages after consumption. Kafka keeps messages for a configurable retention period. This enables: (1) **replay** - re-run a consumer group from offset 0 if you need to reprocess historical data; (2) **multiple independent consumers** - each consumer group reads independently at its own pace; (3) **time-travel debugging** - replay events that caused a bug to debug the processing logic. The log-as-source-of-truth enables event sourcing architectures at scale.

---

### 🔩 First Principles Explanation

**KAFKA CORE CONCEPTS:**

```
TOPIC: "orders"
  Partition 0: [offset 0: order_1] [offset 1: order_2] [offset 2: order_5] ...
  Partition 1: [offset 0: order_3] [offset 1: order_6] [offset 2: order_8] ...
  Partition 2: [offset 0: order_4] [offset 1: order_7] [offset 2: order_9] ...

  - Partitions = parallelism unit (more partitions → more consumers)
  - Events in a partition are ORDERED (offset 0 → 1 → 2 → ...)
  - Events ACROSS partitions are NOT globally ordered (interleaved)
  - Each partition stored as sequential log files on broker disk

PRODUCER writes "order_10" with key="user_42":
  Partition = hash("user_42") % 3 = partition 1
  Event appended to Partition 1 at next offset

  Key → same partition: all orders for user_42 always go to same partition
  → ensures ordering of events per user
  No key → round-robin across partitions (maximize throughput)

CONSUMER GROUP "inventory-service":
  Consumer A → reads Partition 0
  Consumer B → reads Partition 1
  Consumer C → reads Partition 2

  Each consumer reads independently, commits its own offsets
  Adding a 4th consumer: one consumer will be idle (3 partitions, 4 consumers)

  If Consumer B crashes: Partition 1 reassigned to Consumer A or C (rebalance)
```

**SPRING BOOT KAFKA INTEGRATION:**

```java
// Producer:
@Service
public class OrderProducer {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public void publishOrder(Order order) {
        OrderEvent event = OrderEvent.from(order);

        // Key = order.getUserId() → same user's orders → same partition → ordered
        kafkaTemplate.send("orders", order.getUserId().toString(), event)
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Failed to publish order {}: {}", order.getId(), ex.getMessage());
                } else {
                    log.debug("Order {} published to partition {} offset {}",
                        order.getId(),
                        result.getRecordMetadata().partition(),
                        result.getRecordMetadata().offset());
                }
            });
    }
}

// Consumer:
@Component
public class OrderConsumer {

    @KafkaListener(
        topics = "orders",
        groupId = "inventory-service",
        concurrency = "3"  // 3 consumer threads = consume 3 partitions in parallel
    )
    public void consumeOrder(
            @Payload OrderEvent event,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset) {

        log.info("Received order {} from partition {} offset {}",
                 event.getOrderId(), partition, offset);

        // Process the order:
        inventoryService.reserveItems(event);
        // If processing fails → throw exception → consumer retries
        // If processing succeeds → offset auto-committed (or manually commit)
    }

    // Dead letter queue handler:
    @KafkaListener(topics = "orders.DLT", groupId = "orders-dlt-handler")
    public void handleDeadLetter(OrderEvent event) {
        alertService.notifyDeadLetter(event);
    }
}
```

**APPLICATION PROPERTIES:**

```yaml
# application.yml - Spring Boot Kafka configuration
spring:
  kafka:
    bootstrap-servers: kafka-broker1:9092,kafka-broker2:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: io.confluent.kafka.serializers.KafkaAvroSerializer
      acks: all # wait for all ISR replicas to confirm
      retries: 3 # retry on transient failures
      properties:
        enable.idempotence: true # idempotent producer (no duplicates on retry)
        max.in.flight.requests.per.connection: 5 # 5 unconfirmed requests (idempotent)
    consumer:
      group-id: inventory-service
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: io.confluent.kafka.serializers.KafkaAvroDeserializer
      auto-offset-reset: earliest # start from beginning if no committed offset
      enable-auto-commit: false # manual commit for at-least-once processing
      max-poll-records: 500 # max records per poll (batch size)
    listener:
      ack-mode: MANUAL_IMMEDIATE # commit offset manually after processing
```

**PRODUCER ACKS AND DURABILITY:**

```
acks=0: Producer doesn't wait for any acknowledgment
  → Fastest, but data loss possible (broker crash before writing)
  → Use only for metrics/logging where loss is acceptable

acks=1: Producer waits for leader to write to its local log
  → If leader crashes BEFORE replicating to followers → data loss
  → Still possible data loss, but much less likely

acks=all (acks=-1): Producer waits for ALL ISR replicas to confirm
  → No data loss as long as at least one ISR replica is available
  → Slowest (waits for all ISR) but strongest durability guarantee
  → Required for financial/critical data

min.insync.replicas=2:
  Combined with acks=all: require at least 2 ISR replicas to confirm
  If only 1 replica available (ISR shrinks): writes fail (rather than risk data loss)
  Typical production: replication.factor=3, min.insync.replicas=2
  → Can lose 1 broker and still accept writes
  → If 2 brokers are down: writes fail (safety) → "no silent data loss"
```

---

### 🧪 Thought Experiment

**ORDERING GUARANTEE - A COMMON TRAP:**

"We need guaranteed ordering of all payment events."

Naive: create a topic with 1 partition → global ordering maintained. Problem: 1 partition = 1 consumer = no parallelism. At 100K events/second this single consumer becomes the bottleneck.

Better: partition by `payment_id`. All events for the same payment (INITIATED, AUTHORIZED, COMPLETED) are ordered within one partition. No global ordering needed - only per-payment ordering matters.

Even better for user-scoped ordering: partition by `user_id`. All events for user 42 are in order across all payments. Consumer for partition X sees all events for its users in order.

Key insight: **identify the ordering scope** (per-payment? per-user? global?), then partition by that scope's key. You rarely need global ordering - and when you think you do, it usually means you need per-entity ordering.

---

### 🧠 Mental Model / Analogy

> Kafka is like a conveyor belt factory system. The conveyor belt (partition) runs in one direction, never backward. Workers (producers) place items on the belt. A numbered sticker (offset) is placed on each item as it arrives. Inspectors (consumers) walk alongside the belt and examine items from their current position. Multiple inspection teams (consumer groups) each have their own inspector at different positions on different belts. The belt runs continuously - items aren't removed when inspected (retention). If an inspector needs to re-examine items: they walk back to the sticker number they need (seek to offset).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Kafka = distributed message log. Producers write events to topics. Consumers read events at their own pace by tracking offsets. Events persist for days/weeks (replayable). Scales to millions of events/second by adding partitions.

**Level 2:** Partition key determines which partition an event goes to - same key → same partition → ordered within that key. Consumer group: each partition assigned to one consumer (parallelism). `acks=all` + `min.insync.replicas=2` = no data loss. Retention period = how long events are kept (default 7 days).

**Level 3:** Idempotent producer: `enable.idempotence=true` - each message assigned sequence number, broker deduplicates retries. ISR (In-Sync Replicas): replicas within `replica.lag.time.max.ms` (10s) of leader. Leader election: ZooKeeper/KRaft detects leader failure → elects new leader from ISR. Consumer offset commit: `enable.auto.commit=false` + manual commit after processing = at-least-once; Kafka transactions = exactly-once.

**Level 4:** Kafka's performance comes from: (1) **sequential disk writes** (append-only log → disk sequential I/O is as fast as RAM random access); (2) **zero-copy transfer** (`sendfile()` syscall: kernel reads from disk, copies directly to network socket without copying to userspace - eliminates 2 of 4 data copies); (3) **batch compression**: produces send batches of messages, compressed together (snappy/lz4/zstd - 5-10× compression on structured data). Combined: Kafka achieves 200-600MB/s throughput per broker on standard hardware.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ KAFKA CLUSTER                                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [Producer] → hash(key) → Partition Leader           │
│                                │                    │
│  Broker 1: [P0-leader] [P1-follower] [P2-follower]  │
│  Broker 2: [P0-follower] [P1-leader] [P2-follower]  │
│  Broker 3: [P0-follower] [P1-follower] [P2-leader]  │
│                                │                    │
│  [KAFKA ← YOU ARE HERE: replicated commit log]       │
│                                │                    │
│  Consumer Group A: C1←P0, C2←P1, C3←P2             │
│  Consumer Group B: C4←P0,P2, C5←P1 (2 consumers)   │
│                                                      │
│  ZooKeeper/KRaft: cluster metadata + leader election │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
E-commerce order event flow:

1. Order Service (Producer) → "order-placed" event to Kafka topic "orders"
   Key: order.getUserId() → Partition 1 (consistent for this user)
   acks=all → Broker 2 (P1 leader) writes + replicates to Broker 1, Broker 3

2. Kafka cluster: event stored at Partition 1, Offset 15,237
   Replicated to ISR replicas on Broker 1 and Broker 3

3. Consumer Group "inventory-service":
   Consumer thread 2 (reads Partition 1) polls: gets event at offset 15,237
   Processes: reserve items in inventory DB
   Manual commit: "inventory-service consumed P1 offset 15,237"

4. Consumer Group "notification-service":
   Consumer thread 2 reads SAME event from Partition 1 (independent offset)
   Sends email notification
   Commits its own offset

5. Consumer Group "analytics-pipeline":
   Spark Structured Streaming reads the event (also independent)
   Updates real-time dashboard

6. Event retained for 7 days (retention.ms=604800000)
   Can replay from offset 0 if notification-service needs to reprocess
```

---

### ⚖️ Comparison Table

| Feature    | Apache Kafka                 | RabbitMQ                 | AWS SQS                |
| ---------- | ---------------------------- | ------------------------ | ---------------------- |
| Model      | Pull (consumer polls)        | Push (broker pushes)     | Pull                   |
| Ordering   | Per-partition ordering       | FIFO queues              | Optional FIFO          |
| Retention  | Configurable (days/weeks)    | Delete on consume        | 4 days (standard)      |
| Replay     | Yes (offset seek)            | No (deleted on ACK)      | No                     |
| Throughput | Millions/sec per broker      | ~100K/sec                | Very high (managed)    |
| State      | Stateless broker             | Stateful (message state) | Stateless              |
| Best for   | Event streaming, log, replay | Task queues, routing     | AWS-native task queues |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                                                                                                        |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Kafka is a message queue"                    | Kafka is a distributed log/event stream. Unlike queues (delete on consume), Kafka retains events. Multiple consumer groups can each read all events independently. Design for replay, not consumption-and-delete                                                                                               |
| "More partitions always = better performance" | Partitions have overhead: each partition = one file handle on the broker, memory for tracking, one ISR state machine. Too many partitions → high leader election time (ZooKeeper bottleneck), high controller load. Recommended: start with 3-12 partitions per topic, scale up based on measured consumer lag |
| "Kafka guarantees message ordering"           | Kafka guarantees ordering WITHIN a partition. Messages across partitions are not globally ordered. Design your partition key to ensure events that need ordering (per-user, per-order) land in the same partition                                                                                              |

---

### 🚨 Failure Modes & Diagnosis

**1. Consumer Lag Growing - Processing Slower Than Production**

**Symptom:** `kafka-consumer-groups.sh --describe` shows LAG column growing continuously. Alerts fire: "Consumer group payment-service lag > 100,000 messages."

**Root Cause:** Consumer processing rate < Kafka production rate. Could be slow DB write, slow external API call, or insufficient consumer parallelism.

**Diagnosis:**

1. Check consumer processing time: Spring Boot actuator metrics `kafka.consumer.fetch-rate`, `spring.kafka.listener.invocation.duration`
2. Check producer rate vs consumer rate
3. If single slow operation in consumer: add timeout, async processing

**Fix:**

- Increase consumer parallelism: `@KafkaListener(concurrency = "6")` (= 6 threads) up to partition count
- Add more consumer instances (scale horizontally)
- Fix slow processing: identify the bottleneck (DB write, API call) and optimize

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Computing, Messaging Systems
**Builds On This:** Kafka Topic / Partition / Offset, Consumer Group, ISR, Kafka Streams
**Related:** Kafka Topic / Partition / Offset, Consumer Group, Distributed Systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOPIC       │ Named event category → split into partitions│
│ PARTITION   │ Ordered, immutable log segment (on disk)   │
│ OFFSET      │ Event position within partition             │
│ PARTITION KEY│ hash(key) % N → same key → same partition │
│ CONSUMER GRP│ Each partition → 1 consumer (parallelism)  │
│ RETENTION   │ Events kept 7 days (default) for replay    │
│ acks=all    │ + min.insync.replicas=2 → no data loss     │
│ vs RABBITMQ │ Kafka: log+replay; RabbitMQ: queues        │
│ THROUGHPUT  │ Millions/sec: sequential I/O + zero-copy   │
│ ONE-LINER   │ "Distributed append-only log; producers   │
│             │  write, consumers read at own pace"        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the relationship between Kafka partitions and consumer groups? If you have a topic with 3 partitions and add a 4th consumer to a consumer group, what happens? How does adding partitions affect scaling?

**Q2.** (TYPE C - Design) You need to implement event-driven order processing: Order Service → Kafka → [Inventory Service, Notification Service, Analytics]. Each downstream service has different throughput and SLA requirements. Design the Kafka topic structure, partition strategy, consumer group setup, and retention policy.
