---
layout: default
title: "Idempotent Producer"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 24
permalink: /big-data-streaming/idempotent-producer/
id: BIG-024
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Kafka, Exactly-Once Semantics
used_by: Transactional Producer, Kafka Streams, Exactly-Once Semantics
related: Transactional Producer, Exactly-Once Semantics, Apache Kafka
tags:
  - idempotent-producer
  - kafka
  - exactly-once
  - deduplication
  - deep-dive
---

# BIG-024 — Idempotent Producer

⚡ TL;DR — **Idempotent Producer** (`enable.idempotence=true`) assigns each producer a unique **PID (Producer ID)** and attaches a **monotonically increasing sequence number** to every message per partition — if the broker receives a duplicate (producer retry after network timeout), it detects the duplicate `(PID, seqNum)` and silently discards it — guaranteeing **exactly-once delivery per session per partition**; requires `acks=all`, `retries=MAX_INT`, `max.in.flight.requests ≤ 5`.

| #549            | Category: Big Data & Streaming                                | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Apache Kafka, Exactly-Once Semantics                          |                 |
| **Used by:**    | Transactional Producer, Kafka Streams, Exactly-Once Semantics |                 |
| **Related:**    | Transactional Producer, Exactly-Once Semantics, Apache Kafka  |                 |

---

### 🔥 The Problem This Solves

**PRODUCER RETRIES CREATE DUPLICATE MESSAGES:**
A Kafka producer sends a message. The broker receives it, appends to the partition log, but before it sends the ACK, a network hiccup occurs. The producer's `send()` times out. Per Kafka's retry logic, the producer retries. The broker appends the message AGAIN (it has no way to know this is a duplicate — the message looks new). Result: two copies of the same payment event. Without idempotence, "retry on failure" (at-least-once) and "no duplicates" are mutually exclusive.

---

### 📘 Textbook Definition

**Idempotent Producer** is a Kafka producer feature (enabled via `enable.idempotence=true`) that ensures each message is written to a Kafka partition at most once, eliminating duplicates from producer retries.

Mechanism:

1. **PID (Producer ID)**: assigned to each producer instance by the broker on first connection. Unique per producer session.
2. **Sequence Number**: a monotonically increasing counter maintained per `(PID, topic, partition)` triple. Starts at 0, increments by 1 per message.
3. **Broker-side deduplication**: broker stores the last N (5) sequence numbers per `(PID, partition)`. If a message arrives with a sequence number ≤ last seen: duplicate → silently discarded with ACK returned.

Limitations:

- **Session-scoped**: PID is ephemeral — if the producer restarts, it gets a new PID. Duplicates CAN occur across producer restarts (use transactions for cross-restart dedup).
- **Single partition**: dedup is per partition. Does not guarantee cross-partition atomicity (use transactions for that).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Idempotent producer = broker deduplicates producer retries using (PID, seqNum) — retry is silently ignored if the broker already has that message.

**One analogy:**

> An international wire transfer with a unique reference number (seqNum). If the transfer request is sent twice (network retry), the bank checks its log: "Transfer #abc-001 already processed." It rejects the duplicate silently and returns "success" (as if the first attempt worked). The money is transferred exactly once.

**One insight:**
Idempotent producer solves the "retry = duplicate" problem with ZERO impact on message content — you don't need to add deduplication IDs to your message payload. The mechanism is entirely at the Kafka protocol layer (PID + seqNum in the message batch header). Consumers see no difference; the extra messages are filtered by the broker before they reach consumers.

---

### 🔩 First Principles Explanation

**ENABLING IDEMPOTENT PRODUCER:**

```java
// Spring Boot Kafka producer configuration:
@Configuration
public class KafkaProducerConfig {

    @Bean
    public ProducerFactory<String, Object> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");

        // Enable idempotence:
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        // When enable.idempotence=true, Kafka AUTOMATICALLY sets:
        //   acks=all (required — otherwise broker can't sequence properly)
        //   retries=Integer.MAX_VALUE (retry forever until success or timeout)
        //   max.in.flight.requests.per.connection=5 (limited for ordering)

        // You can set these explicitly (they must match):
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);

        // Delivery timeout: total time before giving up (not per retry)
        props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000);  // 2 min

        return new DefaultKafkaProducerFactory<>(props);
    }

    @Bean
    public KafkaTemplate<String, Object> kafkaTemplate(
            ProducerFactory<String, Object> producerFactory) {
        return new KafkaTemplate<>(producerFactory);
    }
}

@Service
public class OrderEventProducer {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public CompletableFuture<SendResult<String, Object>> publishOrderCreated(Order order) {
        // With idempotence: if this call retries internally (network issue),
        // the broker deduplicates using (PID, seqNum)
        // Application code doesn't need to worry about duplicate handling
        return kafkaTemplate.send("order-events", order.getId(), order)
            .toCompletableFuture();
    }
}
```

**HOW DEDUPLICATION WORKS (INTERNALS):**

```
Producer Session 1 (PID=42):
  T=0ms: send(orders-P0, seqNum=0, value=OrderA)
  T=1ms: broker: appends OrderA at offset 8901, records last_seq[PID=42][P0]=0
  T=2ms: NETWORK TIMEOUT (ACK lost in transit)
  T=3ms: producer: NO ACK received → RETRY
  T=4ms: send(orders-P0, seqNum=0, value=OrderA)  ← same seqNum!
  T=5ms: broker: receives (PID=42, seqNum=0) → last_seq=0 → DUPLICATE → DISCARD
  T=5ms: broker: sends ACK "seqNum=0 accepted" (as if first attempt)
  T=6ms: producer: send() returns success

  Result: OrderA appears ONCE at offset 8901 in "orders" P0

  T=7ms: send(orders-P0, seqNum=1, value=OrderB)
  T=8ms: broker: last_seq=0, new seqNum=1 → VALID → appends at offset 8902
  ...

  INVALID SEQUENCE (out-of-order, indicates bug):
  If broker receives seqNum=3 but last_seq=1 (skipping 2):
  → ERROR: INVALID_RECORD
  → Producer throws OutOfOrderSequenceException

  This prevents message loss from out-of-order delivery (max.in.flight=5 allows 5
  in-flight requests, but ordering is still maintained within a sequence window)
```

**WHAT IDEMPOTENCE DOES NOT SOLVE:**

```java
// SCENARIO 1: Producer restart (new PID) — NOT deduplicated by idempotent producer

// Producer instance 1 (PID=42):
kafkaTemplate.send("orders", orderId, order);
// Network timeout — ACK not received
// Application CRASHES and RESTARTS

// Producer instance 2 (PID=43, new session):
kafkaTemplate.send("orders", orderId, order);  // retry after restart
// Broker receives (PID=43, seqNum=0) — looks completely NEW to the broker
// → Message APPENDED AGAIN (duplicate!)
// Fix: use Kafka Transactions (transactionalId survives restarts)

// SCENARIO 2: Same message sent by different producer instances
// (e.g., two pods both receive an order-placed event and try to publish)
// Each pod has a different PID → broker treats as separate messages → DUPLICATE
// Fix: idempotency at application layer (dedup by orderId before producing)
//       OR: architecture change (only ONE service instance produces per event)

// SCENARIO 3: Message published to MULTIPLE partitions (e.g., different topics)
// Idempotent producer: per (PID, partition) dedup ONLY
// No cross-partition atomicity — use transactions:
kafkaTemplate.executeInTransaction(ops -> {
    ops.send("order-events", orderId, order);
    ops.send("inventory-reservations", orderId, reservation);
    return true;
    // Atomically: both written or neither
});
```

---

### 🧪 Thought Experiment

**THE INTERACTION BETWEEN max.in.flight AND ORDERING:**

Without idempotence: if `max.in.flight=5` and a retry occurs, message M1 could arrive AFTER M2, M3, M4, M5 were already committed → M1 inserted at wrong position (ordering violation + duplicate).

With idempotence: broker uses sequence numbers to detect out-of-order arrivals. Even with `max.in.flight=5`:

- If M1 (seqNum=0) is retried after M2 (seqNum=1) is committed: broker sees M1 with seqNum=0 ≤ current last_seq=1 → duplicate → discard
- If M5 (seqNum=4) arrives before M3 (seqNum=2): broker detects gap → returns out-of-order error → producer retries in correct order

Result: idempotence + `max.in.flight=5` = both exactly-once AND ordered delivery per partition.

---

### 🧠 Mental Model / Analogy

> Idempotent producer is like a stamp counter at a notary. Every document gets a unique serial number (seqNum), stamped by this notary's seal (PID). If the same document is submitted twice with the same serial number and seal, the notary rejects the second submission: "already processed." New documents always have the next serial number. The notary keeps track of the last 5 serial numbers processed (broker's in-memory dedup window).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `enable.idempotence=true` → no duplicate messages from producer retries. Broker assigns PID per producer session; producer attaches seqNum per partition. Broker deduplicates by (PID, seqNum). Requires acks=all.

**Level 2:** Session-scoped (PID resets on restart). Per-partition (no cross-partition atomicity). Requires: acks=all, retries=MAX, max.in.flight≤5. Automatically set by enable.idempotence=true (or set explicitly). OutOfOrderSequenceException if seqNums have gaps.

**Level 3:** Broker stores last 5 seqNums per (PID, partition) in memory. If message arrives with seqNum ≤ last seen: duplicate, discarded, ACK sent. If seqNum > last+5: gap detected, INVALID_RECORD error. The 5-window matches max.in.flight=5 — all in-flight requests can be deduplicated.

**Level 4:** Idempotent producer is the foundation of Kafka's EOS (Exactly-Once Semantics). Transactions build on top: `transactionalId` (stable across restarts) + 2PC + epoch fencing. Kafka 3.0+: `enable.idempotence=true` is the DEFAULT (changed from false). For Kafka Streams `EXACTLY_ONCE_V2`: each task's producer is transactional with a stable `transactionalId` derived from `applicationId + taskId`. This ensures cross-restart deduplication at the Streams level without application code changes.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ IDEMPOTENT PRODUCER DEDUPLICATION                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Producer (PID=42, orders-P0):                       │
│   send batch: [(seqNum=5, OrderE), (seqNum=6, OrderF)]│
│         ↓                                            │
│ Broker stores: last_acked_seq[PID=42][P0] = 4       │
│   Receives seqNums 5, 6 → in sequence → APPEND      │
│   last_acked_seq → 6                                │
│ [IDEMPOTENT PRODUCER ← YOU ARE HERE: dedup by seqNum]│
│         ↓  (ACK lost in network)                    │
│ Producer retries: [(seqNum=5, OrderE), (seqNum=6, OrderF)]│
│         ↓                                            │
│ Broker: last_acked_seq=6 → seqNum 5 & 6 ≤ 6 → DUPS │
│   DISCARDS both, sends ACK "success"                │
│         ↓                                            │
│ Result: OrderE and OrderF appear ONCE each in P0    │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Order service with idempotent producer:

1. kafkaTemplate.send("orders", orderId, order) called
2. Producer internally: assign seqNum=15 to this message (batch)
3. send request: (PID=42, P3, seqNum=15, message=order)
4. Broker: last_acked_seq[PID=42][P3] = 14 → seqNum=15 = 14+1 → VALID
   Appends to P3 at offset 99501
   Updates last_acked_seq[PID=42][P3] = 15
5. ACK sent → times out (network issue)
6. Producer: no ACK → retry
7. send request: (PID=42, P3, seqNum=15, message=order) [same seqNum!]
8. Broker: last_acked_seq[PID=42][P3] = 15 → seqNum=15 ≤ 15 → DUPLICATE
   Returns ACK (without appending again)
9. Producer: send() completes successfully
10. Consumer reads offset 99501: one copy of order → processes once
```

---

### ⚖️ Comparison Table

| Config                        | Behavior                    | Duplicate Risk                        | Ordering                 |
| ----------------------------- | --------------------------- | ------------------------------------- | ------------------------ |
| acks=0 (fire-and-forget)      | Best throughput             | YES (fire-and-forget)                 | Preserved within batch   |
| acks=1, retries=0             | Fast, may lose              | NO retries                            | Preserved                |
| acks=1, retries=N             | At-least-once               | YES (retries can reorder + duplicate) | NOT guaranteed           |
| enable.idempotence=true       | Exactly-once within session | NO                                    | Guaranteed per partition |
| transactionalId + idempotence | Cross-session exactly-once  | NO                                    | Guaranteed per partition |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Idempotent producer = exactly-once end to end"     | Idempotent producer gives exactly-once within a single producer session (PID lifetime). Producer restart gets new PID → duplicate possible. Need transactions for cross-restart exactly-once                                                           |
| "enable.idempotence=true adds performance overhead" | Minimal overhead: sequence number is in the batch header (a few bytes). Dedup check is in-memory on the broker (last 5 seqNums). Throughput impact is negligible (<2%). The `acks=all` requirement has more latency impact than the idempotence itself |
| "max.in.flight=1 is needed for ordering"            | With idempotent producer: max.in.flight=5 is safe. The broker uses sequence numbers to detect and handle any out-of-order delivery. Only WITHOUT idempotence does max.in.flight=1 guarantee ordering (at the cost of throughput)                       |

---

### 🚨 Failure Modes & Diagnosis

**1. OutOfOrderSequenceException**

**Symptom:** Producer throws `OutOfOrderSequenceException`. Messages stop being sent.

**Root Cause:** Sequence number gap detected. A message was skipped (sequence number went from N to N+2). This usually indicates a bug in the producer (sending from multiple threads without synchronization, or custom producer interceptor dropping messages).

**Fix:**

```java
// WRONG: sending from multiple threads with shared producer
// Producer is NOT thread-safe for sequence numbering when multithreaded
ExecutorService pool = Executors.newFixedThreadPool(10);
for (Order order : orders) {
    pool.submit(() -> kafkaTemplate.send("orders", order));  // RACE CONDITION
}

// RIGHT: use single-threaded producer, or KafkaTemplate.send() which is thread-safe
// KafkaTemplate handles thread safety internally by batching properly
// Or: use separate producer instance per thread (each gets own PID + seqNum)
kafkaTemplate.send("orders", order.getId(), order);  // thread-safe via Spring
```

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, Exactly-Once Semantics
**Builds On This:** Transactional Producer
**Related:** Transactional Producer, Exactly-Once Semantics, Apache Kafka

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CONFIG      │ enable.idempotence=true                    │
│ PID         │ Unique producer ID per session (ephemeral) │
│ SEQNUM      │ Per (PID, partition): 0,1,2,3... per msg  │
│ DEDUP       │ Broker discards if seqNum ≤ last_acked     │
│ SCOPE       │ Per-session, per-partition only            │
│ REQUIRES    │ acks=all, retries=MAX, in.flight ≤ 5      │
│ KAFKA 3.0+  │ enable.idempotence=true IS DEFAULT         │
│ NOT COVERED │ Cross-restart dups → use transactions      │
│ NOT COVERED │ Cross-partition atomicity → use txn        │
│ ONE-LINER   │ "Sequence numbers dedup retries per       │
│             │  session; broker silently drops duplicates"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is the PID in Kafka's idempotent producer? What happens to the PID when the producer restarts? What is the sequence number and how does the broker use it to detect duplicates?

**Q2.** (TYPE B — Trace) A producer with `enable.idempotence=true` sends messages M1 (seqNum=0), M2 (seqNum=1), M3 (seqNum=2). M2's ACK is lost. What happens when the producer retries M2? What happens to M3 (already sent in flight)? Trace the exact sequence of events at the broker.
