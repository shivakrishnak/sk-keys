---
layout: default
title: "Consumer Group"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /big-data-streaming/consumer-group/
id: BIG-017
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Kafka Topic / Partition / Offset, Apache Kafka
used_by: Distributed Event Consumers, Microservices, Stream Processing
related: Kafka Topic / Partition / Offset, Consumer Lag, ISR
tags:
  - kafka-consumer-group
  - partition-assignment
  - consumer-rebalance
  - parallel-consumption
  - deep-dive
---

# BIG-017 - Consumer Group

⚡ TL;DR - A Kafka **consumer group** is a set of consumers that **share the work** of consuming a topic - each partition is assigned to exactly **one consumer** in the group (no duplicate processing), enabling horizontal scalability; when a consumer joins/leaves, a **rebalance** reassigns partitions; different groups read the same topic **independently** (each has its own offset tracking), enabling multiple services to consume the same events.

| #542            | Category: Big Data & Streaming                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Kafka Topic / Partition / Offset, Apache Kafka                |                 |
| **Used by:**    | Distributed Event Consumers, Microservices, Stream Processing |                 |
| **Related:**    | Kafka Topic / Partition / Offset, Consumer Lag, ISR           |                 |

---

### 🔥 The Problem This Solves

**PARALLELIZING EVENT CONSUMPTION WITHOUT DUPLICATES:**
A single consumer reading 10 partitions × 100K events/second = 1M events/second - too much for one JVM. Ten consumers in a group: each reads 1 partition = 100K events/second per consumer. But if 2 consumers read the same partition: the same order event processed twice (duplicate inventory deduction). Consumer groups solve this: each partition is assigned to exactly ONE consumer in the group - no duplicates, maximum parallelism.

---

### 📘 Textbook Definition

**Consumer Group**: a logical grouping of Kafka consumers identified by a `group.id`. The Kafka cluster assigns partitions to consumers in the group such that each partition is consumed by exactly one consumer. All consumers in a group collectively consume all partitions of the subscribed topics.

**Partition Assignment**: Kafka's `GroupCoordinator` (a broker) manages partition assignments using a partition assignor strategy:

- `RangeAssignor` (default): assigns partitions contiguously per consumer.
- `RoundRobinAssignor`: distributes partitions evenly across consumers.
- `StickyAssignor`: minimizes partition movement during rebalances.
- `CooperativeStickyAssignor`: cooperative rebalance - consumers keep their partitions during rebalance and only release those that need to move (no full stop-the-world rebalance).

**Group Coordinator**: one broker per consumer group acts as the coordinator. Tracks consumer membership (heartbeats), assigns partitions, stores committed offsets in `__consumer_offsets` topic.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Consumer group = N consumers splitting a topic's partitions evenly (each partition → exactly 1 consumer), each group reads independently with its own offsets - parallelism without duplication.

**One analogy:**

> A consumer group is a team of checkout operators in a supermarket (consumer group). The store has 6 checkout lanes (partitions). 6 operators each take 1 lane. If an operator calls in sick (consumer crashes): their lane is reassigned to another operator (rebalance). A different store team (another consumer group) can simultaneously process the same customers (different group = independent offset) - loyalty card rewards team reads the same queue as cashiers, independently.

**One insight:**
**Multiple consumer groups = fan-out pattern.** One topic can be subscribed to by 10 consumer groups, each representing a different service. The "orders" topic published once is simultaneously processed by: inventory-service, notification-service, analytics-service, fraud-detection-service - each at its own pace, each committed offset completely independent. This is fundamentally different from a traditional message queue where one consumer deletes the message - Kafka's log retention enables this fan-out by design.

---

### 🔩 First Principles Explanation

**PARTITION ASSIGNMENT RULES:**

```
Topic "orders" - 4 partitions (P0, P1, P2, P3)
Consumer group "inventory-service"

Scenario 1: 1 consumer (C1)
  C1: P0, P1, P2, P3  (all partitions - max load on one consumer)

Scenario 2: 2 consumers (C1, C2) - ideal parallelism for 2
  C1: P0, P1  (2 partitions each)
  C2: P2, P3

Scenario 3: 4 consumers (C1, C2, C3, C4) - optimal parallelism
  C1: P0   C2: P1   C3: P2   C4: P3  (1 partition each)

Scenario 4: 5 consumers (C1, C2, C3, C4, C5) - over-provisioned
  C1: P0   C2: P1   C3: P2   C4: P3   C5: IDLE
  → C5 receives no partitions (partitions < consumers)
  → Common pattern: provision 1 extra consumer for fast failover

Rebalance on consumer crash (C2 fails):
  C1: P0, P1   C3: P2   C4: P3   (P1 moved from C2 to C1)
```

**STOP-THE-WORLD vs COOPERATIVE REBALANCE:**

```
Eager (Stop-The-World) Rebalance (RangeAssignor, RoundRobinAssignor):
  1. All consumers: REVOKE ALL partitions (stop processing everything)
  2. All consumers: re-join the group (send JoinGroup request)
  3. Group Coordinator: compute new assignment for all consumers
  4. All consumers: RECEIVE new assignment
  5. All consumers: resume consuming from new partitions

  Problem: ALL consumers stop for 2-10 seconds during rebalance
  Cause: any consumer joining or leaving (scale out/in, crash, rolling deploy)

Cooperative (Incremental) Rebalance (CooperativeStickyAssignor):
  1. Group Coordinator: compute new assignment
  2. Only consumers with CHANGED partitions:
     a. Revoke only the partitions that need to move
     b. Other consumers CONTINUE processing their existing partitions
  3. Revoked partitions: reassigned to target consumers
  4. Only affected consumers briefly pause; others never stop

  Enable:
  partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor

  Spring Boot:
  spring.kafka.consumer.properties.partition.assignment.strategy=
    org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

**CONSUMER GROUP MANAGEMENT:**

```bash
# List all consumer groups:
kafka-consumer-groups.sh --bootstrap-server kafka:9092 --list

# Describe a consumer group (see partition assignment and lag):
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group inventory-service
# Output:
# GROUP            TOPIC   PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# inventory-service orders  0          15200           15237           37
# inventory-service orders  1          8895            8901            6
# inventory-service orders  2          22100           22100           0

# Reset offsets (replay from beginning):
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group inventory-service \
  --topic orders \
  --reset-offsets --to-earliest \
  --execute
# CAUTION: consumer must be stopped before resetting offsets

# Reset to specific timestamp (replay from 1 hour ago):
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group inventory-service \
  --topic orders \
  --reset-offsets \
  --to-datetime "2024-01-15T10:00:00.000" \
  --execute
```

**SPRING BOOT - CONSUMER CONCURRENCY:**

```java
@Component
public class OrderConsumer {

    // concurrency = 3: 3 consumer threads, each assigned to 1 partition (max)
    // Topic must have at least 3 partitions for full parallelism
    @KafkaListener(
        topics = "orders",
        groupId = "inventory-service",
        concurrency = "3"
    )
    public void consume(
            ConsumerRecord<String, OrderEvent> record,
            Acknowledgment ack) {

        log.info("Processing partition={} offset={}",
                 record.partition(), record.offset());

        try {
            inventoryService.processOrder(record.value());
            ack.acknowledge();  // commit offset after success
        } catch (RetryableException e) {
            // Don't ack → retry on next poll
            throw e;
        } catch (NonRetryableException e) {
            // Don't retry → send to DLQ
            deadLetterPublisher.publish(record.value());
            ack.acknowledge();  // ack to avoid endless retry loop
        }
    }
}

// Configuration for consumer group:
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory =
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(consumerFactory());
    factory.getContainerProperties().setAckMode(AckMode.MANUAL_IMMEDIATE);

    // Cooperative rebalance (Kafka 2.4+):
    factory.getContainerProperties().setConsumerRebalanceListener(
        new ConsumerAwareRebalanceListener() {
            @Override
            public void onPartitionsRevokedBeforeCommit(
                    Consumer<?, ?> consumer, Collection<TopicPartition> partitions) {
                log.info("Partitions revoked: {}", partitions);
            }
            @Override
            public void onPartitionsAssigned(
                    Consumer<?, ?> consumer, Collection<TopicPartition> partitions) {
                log.info("Partitions assigned: {}", partitions);
            }
        }
    );
    return factory;
}
```

---

### 🧪 Thought Experiment

**REBALANCE STORM DURING ROLLING DEPLOYMENT:**

Scenario: 10-instance service, 10-partition topic, each instance is one consumer (1:1 ratio). Rolling deploy replaces one instance at a time.

Step 1: Instance 1 stops → rebalance (9 consumers, 10 partitions): 9 consumers get 1 partition, 1 gets 2. Processing resumes.

Step 2 (30s later): Instance 2 stops → another rebalance.

...8 more rebalances for a 10-instance rolling deploy. Each rebalance: 2-10 second consumer pause. Total consumer downtime: 10 × 5s = 50 seconds during a rolling deploy.

**Solutions:**

1. `CooperativeStickyAssignor`: incremental rebalance, no stop-the-world.
2. Static membership: assign fixed `group.instance.id` per consumer. When consumer leaves/rejoins within `session.timeout.ms` (45s): Kafka waits before rebalancing (recognizes it as a known member returning). Rolling deploy with `group.instance.id` + `session.timeout.ms=60s`: Kafka waits 60s before declaring a member dead - rolling deploy takes <60s → no rebalance.

---

### 🧠 Mental Model / Analogy

> A consumer group is like a relay race team. There are 4 relay legs (partitions). 4 runners (consumers) each run exactly one leg. If a runner sprains their ankle (crashes): the remaining 3 runners redistribute - 1 runner takes 2 legs. Adding a 5th runner: someone rests (idle). All 4 runners must start from where the previous runner left off (offset - exact handoff position). A second relay team (different consumer group) runs the same course completely independently - they don't know about the first team's position.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Consumer group = N consumers, each assigned to different partitions. No two consumers in a group read the same partition → no duplicates. Rebalance: triggered by consumer join/leave. Multiple groups = independent parallel consumers of same topic.

**Level 2:** Partition count limits parallelism: max consumers = partition count. Adding consumers beyond partition count = idle consumers. Cooperative rebalance (`CooperativeStickyAssignor`): minimizes disruption. `kafka-consumer-groups.sh --describe`: shows per-partition lag for a group.

**Level 3:** Group coordinator: one broker per group. `session.timeout.ms`: if no heartbeat in this window → member considered dead → rebalance. `max.poll.interval.ms`: max time between polls; if exceeded → consumer excluded from group (intended for processing that takes a long time). `heartbeat.interval.ms`: frequency of heartbeat sends (should be 1/3 of `session.timeout.ms`).

**Level 4:** Static membership (`group.instance.id`): assigns a stable identity to a consumer instance. Kafka doesn't trigger a rebalance for a known instance until `session.timeout.ms` expires. During rolling deploys: if deploy < `session.timeout.ms`, no rebalance occurs. The partition assignment "remembers" each consumer's ID and waits for it to return instead of immediately redistributing its partitions. This eliminates rebalance storms during planned maintenance and deployments.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CONSUMER GROUP "inventory-service"                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Topic "orders" (4 partitions, replicated):          │
│ P0[Broker1]  P1[Broker2]  P2[Broker3]  P3[Broker1] │
│      ↑             ↑             ↑           ↑      │
│   Consumer1    Consumer2    Consumer3   Consumer4    │
│   (instance1)  (instance2)  (instance3) (instance4) │
│                                                      │
│ [CONSUMER GROUP ← YOU ARE HERE: 1:1 partition assign]│
│                                                      │
│ Each consumer commits to __consumer_offsets:         │
│   inventory-service P0 offset=15237                 │
│   inventory-service P1 offset=8901                  │
│   inventory-service P2 offset=22100                 │
│   inventory-service P3 offset=9802                  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Multiple consumer groups reading "orders" topic independently:

Producer → Kafka "orders" topic (P0, P1, P2)

Consumer Group "inventory-service" (3 consumers, 3 partitions):
  C1→P0: processes inventory reservation → commits P0 offset
  C2→P1: processes inventory reservation → commits P1 offset
  C3→P2: processes inventory reservation → commits P2 offset

Consumer Group "notification-service" (2 consumers, 2 threads each):
  C1→P0,P1: sends order confirmation emails → commits its own P0, P1 offsets
  C2→P2: sends emails → commits P2 offset
  ← reads SAME events as inventory-service (independent offsets)

Consumer Group "analytics-pipeline" (Spark Structured Streaming):
  Reads all 3 partitions, updates real-time dashboard
  ← SAME events, independent consumer group offset

Rebalance scenario (C1 of inventory-service crashes):
  1. Group Coordinator detects: C1 heartbeat missed for session.timeout.ms (30s)
  2. Triggers rebalance: C2 and C3 revoke their partitions (eager)
  3. New assignment: C2→P0,P1, C3→P2
  4. Resume: C2 reads from last committed C1 offset for P0 (at-least-once)
  ← notification-service and analytics are UNAFFECTED by this rebalance
```

---

### ⚖️ Comparison Table

| Aspect               | Kafka Consumer Group            | RabbitMQ Competing Consumers | Database Polling          |
| -------------------- | ------------------------------- | ---------------------------- | ------------------------- |
| Duplicate prevention | Per partition → 1 consumer      | Broker ACK-based             | Application-level locking |
| Replay               | Yes (offset seek)               | No (delete on ACK)           | No                        |
| Fan-out              | Multiple groups (independent)   | Exchange + multiple queues   | N polling services        |
| Parallelism          | = partition count               | Unlimited consumers          | Unlimited threads         |
| Rebalance            | Automatic (triggered by change) | N/A (stateless)              | N/A                       |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                        |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Adding more consumers always increases throughput" | Adding consumers beyond the partition count has no effect - idle consumers receive no partitions. To increase parallelism: increase partition count first, then add consumers                  |
| "Consumer group rebalance is transparent"           | Eager rebalance causes ALL consumers in the group to pause (2-10 seconds). This can cause processing latency spikes and offset commit gaps. Use `CooperativeStickyAssignor` to minimize impact |
| "Each consumer in a group processes all events"     | The OPPOSITE is true. Each partition is assigned to exactly ONE consumer. To ensure all consumers receive all events: use SEPARATE consumer groups (one per service), not one shared group     |

---

### 🚨 Failure Modes & Diagnosis

**1. Consumer Excluded From Group Due to Processing Timeout**

**Symptom:** Logs show `ConsumerCoordinator - Member ... sending LeaveGroup request to coordinator` repeatedly. Constant rebalances. One consumer repeatedly joins and leaves.

**Root Cause:** `max.poll.interval.ms` (default 5 minutes) exceeded. Consumer takes > 5 minutes to process a batch of records between `poll()` calls. Kafka interprets this as a dead consumer and removes it from the group → rebalance. Other consumers pick up its partitions → rebalance again when it tries to rejoin.

**Fix options:**

1. Reduce `max.poll.records` (process fewer records per poll cycle): `spring.kafka.consumer.max-poll-records=50`
2. Increase `max.poll.interval.ms` to match your processing time: `max.poll.interval.ms=600000` (10 minutes)
3. Offload slow processing to async: poll → publish to internal queue → worker thread → `ack.acknowledge()` asynchronously

---

### 🔗 Related Keywords

**Prerequisites:** Kafka Topic / Partition / Offset, Apache Kafka
**Builds On This:** Consumer Lag, ISR, Kafka Streams
**Related:** Kafka Topic / Partition / Offset, Consumer Lag, ISR

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ASSIGNMENT  │ Each partition → exactly 1 consumer        │
│ MAX PARALLEL│ = partition count (idle beyond that)       │
│ FAN-OUT     │ Multiple groups = independent parallel      │
│ REBALANCE   │ Triggered by join/leave; pause all (eager) │
│ COOPERATIVE │ CooperativeStickyAssignor → no full stop   │
│ STATIC MEM  │ group.instance.id → no rebalance on redep │
│ DIAGNOSE    │ kafka-consumer-groups.sh --describe LAG    │
│ TIMEOUT     │ max.poll.interval.ms → processing budget   │
│ SESSION     │ session.timeout.ms → heartbeat window      │
│ ONE-LINER   │ "N consumers split N partitions; each part │
│             │  to exactly 1 consumer; groups independent"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What triggers a Kafka consumer group rebalance? What is the difference between eager and cooperative rebalancing? What is static group membership and when should you use it?

**Q2.** (TYPE C - Production) A 10-instance microservice consumes a 10-partition Kafka topic. During a rolling deployment (one instance replaced every 2 minutes), you observe 10 rebalances with ~5-second processing gaps each. How do you eliminate or minimize these rebalances?
