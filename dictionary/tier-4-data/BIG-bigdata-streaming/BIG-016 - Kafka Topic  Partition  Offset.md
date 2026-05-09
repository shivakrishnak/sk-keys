---
version: 1
layout: default
title: "Kafka Topic  Partition  Offset"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /big-data-streaming/kafka-topic-partition-offset/
id: BIG-016
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Apache Kafka
used_by: Consumer Group, ISR, Kafka Streams, Producers, Consumers
related: Apache Kafka, Consumer Group, ISR
tags:
  - kafka-topic
  - kafka-partition
  - kafka-offset
  - event-ordering
  - deep-dive
---

# BIG-016 - Kafka Topic  Partition  Offset

⚡ TL;DR - A Kafka **topic** is a logical event category (like a table); a **partition** is a physical ordered, append-only log segment within a topic (enables parallelism - N partitions = N parallel consumers); an **offset** is the monotonically increasing integer position of a record within a partition - consumers track their position by committing the last-processed offset, enabling replay and exactly-once/at-least-once guarantees.

| #541            | Category: Big Data & Streaming                           | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka                                             |                 |
| **Used by:**    | Consumer Group, ISR, Kafka Streams, Producers, Consumers |                 |
| **Related:**    | Apache Kafka, Consumer Group, ISR                        |                 |

---

### 🔥 The Problem This Solves

**SCALABLE, REPLAYABLE, ORDERED EVENT DELIVERY:**
A single ordered log can't scale - one writer/reader is a bottleneck. Multiple unordered logs lose the ordering guarantee. Kafka's partitioned design solves both: partition by a meaningful key (e.g., `user_id`) → all events for the same user are in the same partition → ordered for that user → N partitions = N parallel consumers. Offsets make the position explicit - consumers can replay, skip ahead, or commit progress independently.

---

### 📘 Textbook Definition

**Topic**: a named, durable category for a stream of events. A topic has N partitions, a replication factor, and a retention policy (time-based or size-based). Created with `kafka-topics.sh --create` or auto-created if `auto.create.topics.enable=true`.

**Partition**: an ordered, immutable sequence of records stored as a commit log on a broker's disk. Partitions are the unit of parallelism in Kafka - more partitions → more consumers → higher throughput. Each partition has exactly one leader broker (handles reads/writes) and `replication.factor - 1` follower replicas.

**Offset**: a non-negative, monotonically increasing integer unique within a partition. The first record = offset 0. Records are never deleted or modified (only expired by retention). Consumers commit their offset to track progress. A consumer that crashes and restarts reads from its last committed offset (at-least-once by default).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Topic = named event category; Partition = ordered log segment (parallelism unit); Offset = record position - consumer commits offset to track progress and enable replay/recovery.

**One analogy:**

> A multi-lane highway. The highway (topic) carries traffic (events). Each lane (partition) flows independently in one direction - you can't go backward. Mile markers (offsets) label every position. Each car (consumer) tracks "I'm at mile 15,237." If a driver gets lost: go back to mile 15,237 and continue (offset replay). Multiple drivers in different lanes process in parallel (consumer group). Partitioning by route: all cars going to "NYC" stay in Lane 1 (partition key), ensuring NYC-bound cars maintain their relative order.

**One insight:**
**Partition key is the most critical design decision in a Kafka topic.** The wrong key causes: (1) **ordering violations** - events that must be ordered end up in different partitions; (2) **hot partitions** - one partition gets 80% of all traffic (e.g., key = "order-status" with values "PENDING"×90%, "COMPLETED"×5%, "CANCELLED"×5%); (3) **sticky partition anomaly** - round-robin without a key distributes events, but batching causes recent events to all go to one partition. Always ask: "Which events must be ordered relative to each other?" - those events must share a partition key.

---

### 🔩 First Principles Explanation

**PARTITION INTERNALS - SEGMENT FILES:**

```
/kafka-data/topics/orders-0/   (Partition 0 of topic "orders")
  00000000000000000000.log    (segment: offsets 0 - 999999)
  00000000000000000000.index  (offset → byte position index)
  00000000000000000000.timeindex (timestamp → offset index)
  00000000000001000000.log    (segment: offsets 1000000 - 1999999)
  00000000000001000000.index
  ...
  00000000000014000000.log    (active segment: current writes go here)

Segment file:
  Each record: [timestamp(8B)][offset(8B)][key_size(4B)][key][value_size(4B)][value][headers]
  Records appended sequentially (append-only, no random writes)

  → Sequential disk writes: 500MB/s on standard HDD, 3GB/s on SSD
  → Much faster than random writes (B-tree indexes in traditional DBs)

Retention:
  log.retention.hours=168 (7 days default)
  log.retention.bytes=-1 (unlimited by size, default)
  log.segment.bytes=1073741824 (1GB per segment file)

  Old segments deleted when: oldest segment age > retention.hours
  OR total partition size > retention.bytes (whichever triggers first)

  Cleanup policy:
  cleanup.policy=delete (default): delete old segments
  cleanup.policy=compact (log compaction): keep only latest value per key
```

**OFFSET MANAGEMENT:**

```java
// CONSUMER OFFSET TRACKING:

// Option 1: Enable auto-commit (at-most-once risk)
// auto-commits current offset every auto.commit.interval.ms (default 5s)
// Problem: if processing fails after auto-commit → message lost
consumer.subscribe(Collections.singletonList("orders"));
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        processRecord(record.value());  // if this fails AFTER auto-commit → message lost
    }
    // auto-commit happens in the background at commit interval
}

// Option 2: Manual commit (at-least-once)
// Commit AFTER successful processing → if processing fails: re-process from last commit
consumer.subscribe(Collections.singletonList("orders"));
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        processRecord(record.value());
    }
    consumer.commitSync();  // commit AFTER all records in batch processed
    // If processRecord fails: batch replayed (at-least-once)
    // If commitSync fails: batch replayed (at-least-once)
}

// Option 3: Manual per-record commit (highest control)
for (ConsumerRecord<String, String> record : records) {
    processRecord(record.value());
    // Commit specific offset (offset+1 = next offset to read):
    TopicPartition partition = new TopicPartition(record.topic(), record.partition());
    OffsetAndMetadata offsetAndMeta = new OffsetAndMetadata(record.offset() + 1);
    consumer.commitSync(Collections.singletonMap(partition, offsetAndMeta));
}

// SPRING BOOT with manual commit:
@KafkaListener(topics = "orders", groupId = "inventory-service")
public void consume(
        ConsumerRecord<String, String> record,
        Acknowledgment ack) {  // inject Acknowledgment for manual commit
    try {
        processOrder(record.value());
        ack.acknowledge();  // commit offset AFTER successful processing
    } catch (Exception e) {
        // Don't ack → record will be replayed on next poll
        log.error("Processing failed for offset {}", record.offset(), e);
    }
}
```

**PARTITION KEY DESIGN - BEST PRACTICES:**

```
GOOD partition keys (high cardinality, even distribution, ordering-meaningful):
  - user_id: all events per user ordered, millions of users → even distribution
  - order_id: all events per order ordered, millions of orders → even distribution
  - device_id: IoT sensor events ordered per device

BAD partition keys (low cardinality → hot partitions):
  - event_type: "ORDER_PLACED" 90%, "CANCELLED" 5%, "REFUNDED" 5%
    → Partition for "ORDER_PLACED" handles 90% of all traffic = hot partition
  - day_of_week: Mon-Sun → only 7 distinct values, uneven traffic
  - status: "ACTIVE"×99%, "INACTIVE"×1% → extreme skew

HOT PARTITION DIAGNOSIS:
  kafka-consumer-groups.sh --describe --group inventory-service
  → Shows per-partition LAG:
    PARTITION 0: LAG=0      (healthy)
    PARTITION 1: LAG=500000 (HOT - growing lag)
    PARTITION 2: LAG=0      (healthy)

  Fix: change partition key to higher-cardinality field
  Or: salt the hot key - append random(0-9) to the key
    (user_123 → user_123_3, user_123_7, ...)
    → distributes across 10 partitions, loses strict ordering
    → use when ordering is less important than throughput
```

**SEEKING AND REPLAYING OFFSETS:**

```java
// Replay: re-read from beginning (e.g., reprocess historical events):
consumer.subscribe(Collections.singletonList("orders"));
consumer.poll(Duration.ofMillis(0));  // trigger partition assignment
consumer.seekToBeginning(consumer.assignment());  // seek all partitions to offset 0

// Seek to specific offset (e.g., replay from 1 hour ago):
long oneHourAgo = System.currentTimeMillis() - 3600_000;
Map<TopicPartition, Long> timestampsToSearch = new HashMap<>();
for (TopicPartition tp : consumer.assignment()) {
    timestampsToSearch.put(tp, oneHourAgo);
}
Map<TopicPartition, OffsetAndTimestamp> offsets = consumer.offsetsForTimes(timestampsToSearch);
for (Map.Entry<TopicPartition, OffsetAndTimestamp> entry : offsets.entrySet()) {
    if (entry.getValue() != null) {
        consumer.seek(entry.getKey(), entry.getValue().offset());
    }
}
// Now consumer will re-read all events from 1 hour ago

// Seek to end (skip all existing events, start from new events only):
consumer.seekToEnd(consumer.assignment());
```

---

### 🧪 Thought Experiment

**HOW MANY PARTITIONS SHOULD YOU CREATE?**

Rule: number of partitions = max number of consumers you'll ever want in a consumer group.

If you have 3 consumers today and might scale to 10: create 10 partitions. You can't reduce partitions without recreating the topic. Adding partitions: possible, but can disrupt ordering (same key might route to different partition after partition count changes).

Other considerations:

- Each partition = one thread/file handle on broker = overhead
- Each partition's ISR state tracked by controller = controller overhead
- Kafka recommendation: fewer, larger partitions (100-200 per broker max for older Kafka; KRaft handles thousands better)
- For high-throughput (100K+ events/sec per topic): 30-100 partitions
- For low-throughput (1K events/sec): 3-6 partitions

---

### 🧠 Mental Model / Analogy

> Partitions are like checkout lanes in a supermarket. The store (topic) has N lanes. Each lane has its own queue (partition = ordered). A number dispenser assigns customers to lanes based on their cart type (partition key: express lane for < 10 items). Each cashier (consumer) handles one lane exclusively. Adding cashiers (consumers) up to the number of lanes helps; beyond that, cashiers sit idle. Changing lanes mid-queue (seeking to a different offset) is allowed - the cashier can pick up from any point. The receipt tape (offset) records every transaction permanently for 7 days.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Topic = named log. Partition = ordered segment (parallelism). Offset = record position (consumer tracks progress). More partitions = more consumers = more throughput. Same key → same partition → ordered for that key.

**Level 2:** Partition key selection: high cardinality (many distinct values), even distribution, matches ordering requirements. Hot partition: one partition gets all traffic → one consumer overwhelmed → growing lag. Manual offset commit: commit after processing (at-least-once), not before. Replay: seek to offset 0 or use `offsetsForTimes()` to find an offset by timestamp.

**Level 3:** Segment files on disk: rolling 1GB files, append-only. Index files for O(log N) offset lookup. Retention: delete old segments or compact (keep latest value per key). Log compaction: useful for change log / state topics - compacted log is always readable but only retains the latest value per key. Consumer offset storage: `__consumer_offsets` internal Kafka topic (not ZooKeeper since Kafka 0.9).

**Level 4:** Partition reassignment: when brokers are added/removed, partitions can be reassigned to rebalance storage/load (`kafka-reassign-partitions.sh`). Leader election: if leader broker fails, controller promotes one of the ISR replicas to leader. `unclean.leader.election.enable=false`: prevents non-ISR replica from becoming leader (could have stale data) - may cause temporary unavailability but prevents data loss. `unclean.leader.election.enable=true`: promotes any replica even if behind (availability over consistency). Preferred leader: the first replica in the ISR list is the "preferred leader" - `kafka-leader-election.sh` can trigger preferred leader election to rebalance load after a failure and recovery.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ TOPIC "orders" - 3 PARTITIONS × REPLICATION FACTOR 3│
├──────────────────────────────────────────────────────┤
│                                                      │
│ P0 leader(Broker1): [0][1][2][3]...[15237]←new      │
│ P0 follower(Broker2): [0][1][2][3]...[15237] (ISR)  │
│ P0 follower(Broker3): [0][1][2][3]...[15230] (ISR)  │
│                                                      │
│ P1 leader(Broker2): [0][1][2]...[8900]←new          │
│ P1 follower(Broker1): [0][1][2]...[8900] (ISR)      │
│ P1 follower(Broker3): [0][1][2]...[8898] (ISR)      │
│                                                      │
│ P2 leader(Broker3): [0][1][2]...[22100]←new         │
│ P2 follower(Broker1): [0][1][2]...[22100] (ISR)     │
│ P2 follower(Broker2): [0][1][2]...[22095] (ISR)     │
│                                                      │
│ Consumer group "inventory-service":                  │
│   Consumer1 → P0 (last committed: 15100)            │
│   Consumer2 → P1 (last committed: 8800)             │
│   Consumer3 → P2 (last committed: 22000)            │
│ [TOPIC/PARTITION/OFFSET ← YOU ARE HERE]              │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Producer sends order event with key="user_42":

1. hash("user_42") % 3 = 1 → Partition 1
2. Producer → Broker2 (P1 leader): write event at Offset 8901
3. Broker2: appends to P1 log, replicates to Broker1 and Broker3 (ISR)
4. Broker1 + Broker3 replicate → ACK back to Broker2
5. Broker2 → Producer: ACK (acks=all satisfied)
6. Event committed at P1, Offset 8901

Consumer "inventory-service", Consumer2 reads P1:
7. poll(): fetches P1 offsets 8801-8901 (100 events, max.poll.records)
8. processOrder(event at offset 8901)
9. commitSync(): records "inventory-service P1 offset=8902" in __consumer_offsets

Consumer crashes:
10. Restart: reads last committed offset 8802 (not 8902 - if crash before commit)
    → replays 8802-8901 (at-least-once: same orders processed again)
    → idempotency key in order processing handles duplicates
```

---

### ⚖️ Comparison Table

| Feature       | Kafka Partition      | Database Shard  | Message Queue           |
| ------------- | -------------------- | --------------- | ----------------------- |
| Ordering      | Within partition     | None guaranteed | FIFO queue only         |
| Replay        | Yes (offset seek)    | No              | No (deleted on consume) |
| Parallelism   | 1 consumer/partition | N readers       | N parallel consumers    |
| State         | Stateless log        | Stateful data   | Stateless queue         |
| Max consumers | = partition count    | Unlimited reads | Unlimited               |

---

### ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                                                                                                                                                                                                       |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Kafka guarantees global ordering" | Kafka guarantees ordering WITHIN a partition only. For global ordering: use 1 partition (sacrifices parallelism). Design partition keys to scope ordering to what matters                                                                                     |
| "You can always add partitions"    | You can add partitions to a topic. But existing events already in the old partitions don't move. New events with previously-consistent keys may now route to different partitions - breaking per-key ordering for events that span the partition count change |
| "Offset commit = message deletion" | Committing an offset doesn't delete the message. It records the consumer's progress. The message remains in the partition until the retention period expires. Other consumer groups can re-read the same message                                              |

---

### 🚨 Failure Modes & Diagnosis

**1. Out-of-Order Events Reaching Consumer**

**Symptom:** Business logic fails because an "ORDER_COMPLETED" event arrives at the consumer before "ORDER_PLACED" for the same order.

**Root Cause:** Multiple producers writing to different partitions for the same order ID, OR the partition key isn't the order ID (round-robin) so ORDER_PLACED and ORDER_COMPLETED land in different partitions.

**Diagnosis:** Inspect producer code - is `order_id` used as the partition key? Log the partition and offset of each event on consume.

**Fix:** Ensure all events for the same entity (order, user) use the same partition key. If using multiple producer topics: ensure all topics use the same key for the same entity. If you need cross-partition ordering: use a single-partition topic (sacrifices parallelism) or implement ordering in the consumer (collect all events for an entity, wait for completeness, then process in order).

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka
**Builds On This:** Consumer Group, ISR, Kafka Streams
**Related:** Apache Kafka, Consumer Group, ISR

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOPIC       │ Named event category, N partitions         │
│ PARTITION   │ Ordered append-only log (segment files)    │
│ OFFSET      │ Record position within partition           │
│ PARTITION KEY│ hash(key) % N → same key → same partition │
│ ORDERING    │ Within partition only (NOT global)         │
│ REPLAY      │ Seek to offset 0 or by timestamp           │
│ HOT PART    │ Low-cardinality key → uneven distribution  │
│ COMMIT      │ offset+1 = next to read; after processing  │
│ PARTITIONS  │ = max consumer group parallelism           │
│ ONE-LINER   │ "Topic=category; Partition=ordered log;   │
│             │  Offset=position; same key→same partition" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain how Kafka partition key selection affects both event ordering and throughput. What makes a "good" partition key? Give an example of a bad partition key and how to fix it.

**Q2.** (TYPE C - Troubleshooting) Your e-commerce system publishes "cart-events" to a Kafka topic with 10 partitions. The partition key is `event_type` (ADD_ITEM, REMOVE_ITEM, CHECKOUT). Consumer lag is growing on the CHECKOUT partition. Diagnose and fix.
