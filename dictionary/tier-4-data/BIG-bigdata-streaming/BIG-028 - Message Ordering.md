---
layout: default
title: "Message Ordering"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 28
permalink: /big-data-streaming/message-ordering/
id: BIG-028
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Kafka, Kafka Topic / Partition / Offset, Consumer Group
used_by: Event-Driven Architecture, Financial Systems, State Machines
related: Kafka Topic / Partition / Offset, Consumer Group, Idempotent Producer
tags:
  - message-ordering
  - kafka
  - partition-key
  - ordering-guarantees
  - deep-dive
---

# BIG-028 - Message Ordering

⚡ TL;DR - Kafka guarantees **ordering WITHIN a partition** - all messages with the same **partition key** (e.g., `orderId` or `userId`) go to the same partition and are consumed in order; **global ordering** (across all partitions) requires a single-partition topic (sacrifices parallelism); ordering across partitions is NOT guaranteed; producer-side deordering can occur with retries unless `enable.idempotence=true`; the core design question: "what is the ordering unit?" → choose partition key accordingly.

| #553            | Category: Big Data & Streaming                                        | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, Kafka Topic / Partition / Offset, Consumer Group        |                 |
| **Used by:**    | Event-Driven Architecture, Financial Systems, State Machines          |                 |
| **Related:**    | Kafka Topic / Partition / Offset, Consumer Group, Idempotent Producer |                 |

---

### 🔥 The Problem This Solves

**OUT-OF-ORDER EVENTS CORRUPT STATE MACHINES:**
An order management system receives events: `ORDER_PLACED → PAYMENT_CONFIRMED → ORDER_SHIPPED → ORDER_DELIVERED`. If `ORDER_SHIPPED` arrives before `PAYMENT_CONFIRMED`, the state machine tries to mark an order as shipped before payment is confirmed - invalid state. Without ordering guarantees, distributed systems that react to event sequences are unreliable. Kafka's partition-based ordering ensures all events for a specific order are processed in the exact sequence they were produced.

---

### 📘 Textbook Definition

**Message Ordering** in Kafka:

1. **Per-partition ordering**: all messages written to the same partition are delivered to consumers in the exact order they were written (total order within a partition). Guaranteed by append-only log semantics.

2. **Partition key determines placement**: `hash(key) % numPartitions = partitionIndex`. Same key → always same partition → ordered per key.

3. **No cross-partition ordering**: messages on different partitions are consumed in an arbitrary order relative to each other. Consumer reads from all assigned partitions, delivering messages in a round-robin or arbitrary interleaving.

4. **Global ordering**: achievable only with 1 partition per topic. Total ordering, no parallelism.

5. **Idempotent producer**: required to maintain ordering under retries with `max.in.flight > 1`. Without idempotence: retried batches can land out of order.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Kafka orders messages within a partition - same partition key = same partition = ordered processing per entity; different keys = different partitions = unordered relative to each other.

**One analogy:**

> Multiple bank tellers (partitions). All transactions for Account 42 always go to Teller 3 (partition key = accountId). Teller 3 processes Account 42's transactions in the exact order received - no race conditions for that account. Account 99 goes to Teller 7 - independent. No guarantee that Teller 3 and Teller 7 process their last transactions in any synchronized order.

**One insight:**
The partition key is an **ordering unit selector**. The question is not "do I need ordering?" (you usually do for stateful entities) but "what is my ordering unit?" For financial systems: `accountId` (order per account). For chat: `conversationId`. For user activity: `userId`. For global order: null key (forces single partition) or custom partitioner. If you send messages with null key, Kafka uses round-robin → messages for the same entity go to different partitions → NO ordering guarantee.

---

### 🔩 First Principles Explanation

**PARTITION KEY AND ORDERING:**

```java
@Service
public class OrderEventProducer {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    // CORRECT: use orderId as partition key → all order-X events go to same partition
    public void publishOrderEvent(String orderId, OrderEvent event) {
        kafkaTemplate.send(
            new ProducerRecord<>(
                "order-events",   // topic
                orderId,          // KEY = partition key → hash(orderId) % numPartitions
                event             // value
            )
        );
        // All events for orderId="order-123" → same partition → delivered in order:
        // ORDER_PLACED → PAYMENT_CONFIRMED → ORDER_SHIPPED → ORDER_DELIVERED ✓
    }

    // WRONG: null key → round-robin partitioning → different partitions
    public void publishOrderEventWrong(OrderEvent event) {
        kafkaTemplate.send("order-events", event);  // no key!
        // ORDER_PLACED → P0, PAYMENT_CONFIRMED → P1, ORDER_SHIPPED → P2
        // Consumer sees them in arbitrary order → state machine corrupted ✗
    }

    // WRONG: random key → no consistent ordering
    public void publishOrderEventRandomWrong(OrderEvent event) {
        kafkaTemplate.send("order-events",
            UUID.randomUUID().toString(), event);  // random key each time!
        // Different UUIDs → different partitions each time → NO ordering ✗
    }
}

// Consumer side: messages for same orderId arrive in order
@KafkaListener(topics = "order-events")
public void handleOrderEvent(OrderEvent event,
                              @Header(KafkaHeaders.RECEIVED_PARTITION) int partition) {
    // All events with same orderId are handled by the same consumer instance
    // (because same partition → assigned to one consumer in the group)
    // → ORDER_PLACED → PAYMENT_CONFIRMED → SHIPPED → DELIVERED → in order ✓
    orderStateMachine.transition(event.getOrderId(), event.getType());
}
```

**ORDERING UNDER RETRIES - IDEMPOTENT PRODUCER REQUIREMENT:**

```java
// Without idempotent producer + max.in.flight > 1: ORDERING VIOLATION
// Scenario:
// Batch 1: [M1, M2] sent to partition P0
// Network: batch 1 lost, producer retries
// Meanwhile: Batch 2: [M3, M4] sent (already in flight)
// Broker: receives M3, M4 first (offset 0, 1)
//         receives retry of M1, M2 (offset 2, 3)
// Consumer: sees M3, M4, M1, M2 - OUT OF ORDER

// FIX: enable idempotence
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
// → max.in.flight limited to 5, sequence numbers added
// → Broker: M1(seqNum=0), M2(seqNum=1) → on retry: deduped or reordered correctly
// → M3(seqNum=2), M4(seqNum=3) → broker detects gap if seqNums arrive wrong order
//    → returns error → producer retries in correct order

// For strict ordering with single in-flight (maximum ordering, minimum throughput):
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 1);
// → Guarantees ordering even without idempotence (serial sends, no overlapping batches)
// → Throughput: ~50% less than max.in.flight=5 with idempotence
```

**PARTITION COUNT AND ORDERING:**

```
// SCENARIO: global ordering required (e.g., audit log where ALL events must be ordered)

// Option 1: Single partition topic
// Creates: audit-log (1 partition)
// kafka-topics.sh --create --topic audit-log --partitions 1 --replication-factor 3
//
// Ordering: GUARANTEED (total order)
// Parallelism: NONE (only 1 consumer can read; max 1 partition = max 1 active consumer)
// Throughput: limited to 1 partition's capacity (~100MB/s with replication)
// Use when: audit logs, global ID sequences, single-entity state machines

// Option 2: Multi-partition + partition key (PER-ENTITY ordering)
// Creates: order-events (12 partitions)
// Orders for orderId=X: always P3 (hash("X") % 12 = 3)
// Ordering: guaranteed per orderId
// Parallelism: up to 12 consumers in parallel
// Use when: per-entity ordering (per account, per order, per user)

// Option 3: Explicit partition routing (override hash)
public void sendToExplicitPartition(String orderId, OrderEvent event, int partition) {
    kafkaTemplate.send(
        new ProducerRecord<>("order-events", partition, orderId, event)
    );
    // Bypass hash partitioner → direct partition assignment
    // Use for: custom load distribution, co-partitioning requirements
}

// CUSTOM PARTITIONER: special-case routing
public class VipFirstPartitioner implements Partitioner {
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                         Object value, byte[] valueBytes, Cluster cluster) {
        if (value instanceof OrderEvent && ((OrderEvent)value).isVip()) {
            return 0;  // VIP orders always go to partition 0
        }
        // Else: hash-based routing (standard behavior)
        return Utils.toPositive(Utils.murmur2(keyBytes)) %
               cluster.availablePartitionsForTopic(topic).size();
    }
}
```

**CROSS-PARTITION ORDERING (THE HARD CASE):**

```
Problem: You need ORDER_PLACED and USER_PROFILE_UPDATED for the same user
         to be processed in the correct relative order.

ORDER_PLACED uses key=orderId → partition based on orderId → P3
USER_PROFILE_UPDATED uses key=userId → partition based on userId → P1

Consumer reads from P3 and P1 interleaved → no guaranteed ordering between them

Solutions:
1. USE SAME KEY: both events keyed by userId → same partition → ordered
   ORDER_PLACED with key=userId → P1 (same as user profile updates)
   Tradeoff: all user's orders in same partition → can't parallelize per-user

2. CO-PARTITIONING: ensure both topics have same number of partitions
   AND same partitioning function for the common key (userId)
   Kafka Streams join: KStream[orderId→userId keyed] join KTable[userId keyed]
   Only works if streams are co-partitioned (Kafka Streams enforces this)

3. APPLICATION-LEVEL SEQUENCING: consumer reads both streams, buffers,
   applies sequence numbers to order globally (complex, stateful)

4. ACCEPT EVENTUAL CONSISTENCY: process events with handler that checks
   "if USER_PROFILE_UPDATED arrives before ORDER_PLACED, store profile and
   apply when ORDER_PLACED arrives" (saga-style buffering)
```

---

### 🧪 Thought Experiment

**PARTITION REBALANCING AND ORDERING:**

Consumer group rebalances: Consumer A was handling P3, gets reassigned to Consumer B. Messages in-flight from Consumer A's last poll: Consumer A already received M100-M110 from P3 and started processing M100. After rebalance, Consumer B starts from the last COMMITTED offset (say, M95 - A only committed up to M95).

Result: M95-M110 are re-processed by Consumer B (at-least-once). This means:

1. If Consumer A partially processed M96-M99 and had side effects → duplicate side effects.
2. Ordering within the re-processed range (M95-M110) is maintained (same partition, same offsets).
3. Global ordering during rebalance: briefly disrupted while ownership transitions.

Solution: idempotent consumer (dedup by event ID) + at-least-once with exactly-once semantics (EOS) at the pipeline level.

---

### 🧠 Mental Model / Analogy

> Kafka partitions are like numbered conveyor belts in a factory. Items (messages) are routed to specific belts based on their label (partition key). Belt #3 always carries "red items" (orderId=X). Items on Belt #3 are always in the order they were placed - item 1 exits before item 2 before item 3. Items on Belt #5 (a different order) are independent. You can't say "item on Belt #3 is BEFORE item on Belt #5" - they run independently. But within each belt: perfect order.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Kafka guarantees order within a partition. Same partition key = same partition = ordered delivery. Different keys → different partitions → unordered relative to each other. Use orderId, userId, or accountId as partition key for per-entity ordering.

**Level 2:** Null key = round-robin = no ordering. `enable.idempotence=true` + `max.in.flight=5` maintains ordering under retries. Single partition = global ordering but no parallelism. Custom partitioner for special routing.

**Level 3:** Consumer rebalancing causes at-least-once re-delivery at partition boundaries. Co-partitioning requirement for Kafka Streams joins: same number of partitions + same partitioning function per key. Adding partitions after topic creation: changes `hash(key) % N` → same key goes to different partition → ordering breaks for existing consumers until they re-consume → not recommended for ordered topics.

**Level 4:** Causal ordering (Lamport timestamps or vector clocks) is NOT provided by Kafka. Kafka provides per-partition physical ordering (append order). If producer A's message causally depends on producer B's message (B happens before A, in different partitions), the consumer has no way to know this from Kafka alone. Solution: embed causal timestamps in message headers, or use a serialization service (Zookeeper/etcd-based sequence number), or model all causally related messages in the same partition. For distributed systems requiring causal consistency: explore event sourcing frameworks (Axon, EventStore) that build on Kafka but add causal ordering metadata.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PARTITION KEY → ORDERING GUARANTEE                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Producer sends order events for Order-X:            │
│   key="order-X" → hash("order-X") % 6 = 3 → P3    │
│                                                      │
│ P3 append-only log (immutable, ordered):            │
│   [offset 0: ORDER_PLACED for Order-X]             │
│   [offset 1: ORDER_PLACED for Order-Y]  ← different key, same partition by hash│
│   [offset 2: PAYMENT_CONFIRMED for Order-X]        │
│   [offset 3: ORDER_SHIPPED for Order-X]            │
│   [offset 4: ORDER_DELIVERED for Order-X]          │
│ [ORDERING ← YOU ARE HERE: within-partition guarantee]│
│                                                      │
│ Consumer processes P3 sequentially:                 │
│   → Order-X: PLACED → ... wait for offset 2 ... → CONFIRMED → SHIPPED → DELIVERED│
│   Order-X state: correct sequence, no skipped steps│
│                                                      │
│ Different partition P5 (Order-Z):                  │
│   Consumer processes P5 independently              │
│   No guaranteed ordering between P3 events and P5 events│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order lifecycle with correct partition-based ordering:

Order-123 life cycle:
T=0: OrderService publishes ORDER_PLACED{orderId:123, amount:$150}
     key="123" → hash % 8 = 4 → Partition 4, offset 5500

T=5s: PaymentService publishes PAYMENT_CONFIRMED{orderId:123}
      key="123" → hash % 8 = 4 → Partition 4, offset 5510
      (5500 < 5510: ORDER_PLACED comes before PAYMENT_CONFIRMED in P4)

T=15s: ShippingService publishes ORDER_SHIPPED{orderId:123}
       key="123" → Partition 4, offset 5523

T=25s: DeliveryService publishes ORDER_DELIVERED{orderId:123}
       key="123" → Partition 4, offset 5541

Consumer (order-fulfillment-group), assigned to P4:
Reads: offset 5500 → ORDER_PLACED → stateMachine.transition(123, PLACED) ✓
Reads: offset 5510 → PAYMENT_CONFIRMED → stateMachine.transition(123, CONFIRMED) ✓
Reads: offset 5523 → ORDER_SHIPPED → stateMachine.transition(123, SHIPPED) ✓
Reads: offset 5541 → ORDER_DELIVERED → stateMachine.transition(123, DELIVERED) ✓
State: Order-123 correctly reaches DELIVERED state with no invalid transitions
```

---

### ⚖️ Comparison Table

| Ordering Scope       | Configuration                  | Parallelism       | Use Case                        |
| -------------------- | ------------------------------ | ----------------- | ------------------------------- |
| Per entity (per key) | `key = entityId`, N partitions | Up to N consumers | Orders, accounts, users         |
| Global (total order) | 1 partition, any key           | 1 consumer max    | Audit log, global sequence      |
| No ordering          | Null key (round-robin)         | Up to N consumers | High-throughput, order-agnostic |

| Risk                                  | Cause                                   | Fix                                    |
| ------------------------------------- | --------------------------------------- | -------------------------------------- |
| Ordering violation on retry           | `max.in.flight > 1` without idempotence | `enable.idempotence=true`              |
| Ordering violation on key change      | Different keys for same entity          | Consistent partition key strategy      |
| Ordering disruption after repartition | Added partitions to existing topic      | Don't add partitions to ordered topics |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Kafka guarantees ordering for all messages"          | Only within a partition. Cross-partition ordering is not guaranteed and cannot be relied upon                                                          |
| "Multiple consumers in a group don't affect ordering" | Each consumer handles specific partitions. Within each consumer's partitions: perfect order. Across consumers: no cross-partition ordering             |
| "acks=all guarantees ordering"                        | `acks=all` ensures durability (ISR replication). Ordering is determined by partition key selection and idempotence for retries - not by `acks` setting |

---

### 🚨 Failure Modes & Diagnosis

**1. State Machine Corruption - Events Arriving Out of Order**

**Symptom:** `InvalidStateTransitionException`. Orders appearing SHIPPED before PAYMENT_CONFIRMED.

**Root Cause:** Events for the same order ID sent with different/null keys, routing to different partitions. Check:

```bash
# Show partition for recent messages:
kafka-console-consumer --topic order-events --max-messages 100 --property print.key=true \
  --property print.partition=true --from-beginning | grep "order-123"
# Should show: Partition: 4 for all order-123 messages
# If partition varies: key strategy is inconsistent
```

**Fix:** Enforce consistent partition key:

```java
// Add a validation to ProducerFactory or custom partitioner to assert key is set:
public void publishOrderEvent(OrderEvent event) {
    Objects.requireNonNull(event.getOrderId(), "Order event must have orderId as key");
    kafkaTemplate.send("order-events", event.getOrderId(), event);
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Kafka Topic / Partition / Offset
**Builds On This:** Event-Driven Architecture, State Machines
**Related:** Kafka Topic / Partition / Offset, Consumer Group, Idempotent Producer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ GUARANTEE   │ Ordered WITHIN partition; not across       │
│ PARTITION   │ hash(key) % numPartitions = destination    │
│ NULL KEY    │ Round-robin → NO ordering guaranteed       │
│ IDEMPOTENCE │ enable.idempotence=true to preserve order  │
│             │ under retries with max.in.flight ≤ 5       │
│ GLOBAL ORD  │ 1 partition → total order, no parallelism  │
│ KEY CHOICE  │ entityId (orderId, userId, accountId)      │
│ REPARTITION │ AVOID adding partitions to ordered topics  │
│ COPART.     │ Kafka Streams joins need co-partitioned    │
│ ONE-LINER   │ "Same key = same partition = in order;    │
│             │  different keys = independent ordering"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Why does Kafka only guarantee ordering within a partition and not globally? What determines which partition a message goes to? How does `enable.idempotence=true` affect ordering guarantees?

**Q2.** (TYPE C - Design) A banking system publishes events for account transactions: DEPOSIT, WITHDRAWAL, TRANSFER_OUT, TRANSFER_IN. Multiple accounts, multiple currencies, millions of events per day. Design the Kafka partition strategy to ensure: each account's transactions are processed in order, maximum parallelism, and cross-account transfer ordering is handled correctly.
