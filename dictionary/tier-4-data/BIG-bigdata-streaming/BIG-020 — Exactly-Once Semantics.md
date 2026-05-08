---
layout: default
title: "Exactly-Once Semantics"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /big-data-streaming/exactly-once-semantics/
id: BIG-020
category: Big Data & Streaming
difficulty: ★★★
depends_on: Apache Kafka, ISR (In-Sync Replicas), Idempotent Producer
used_by: Kafka Transactions, Kafka Streams, Structured Streaming
related: Idempotent Producer, Transactional Producer, Kafka Streams
tags:
  - exactly-once
  - kafka-transactions
  - idempotent
  - eos
  - deep-dive
---

# BIG-020 — Exactly-Once Semantics

⚡ TL;DR — **Exactly-Once Semantics (EOS)** guarantees that every message is **processed and produced exactly once** — no duplicates from retries, no data loss from failures; Kafka achieves this via **idempotent producer** (sequence numbers deduplicate retries), **transactions** (atomic multi-partition writes with 2PC coordinator), and **read-process-write atomicity** (Kafka Streams reads offset + writes output in one atomic transaction); end-to-end EOS requires all three components working together.

| #545            | Category: Big Data & Streaming                             | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Apache Kafka, ISR (In-Sync Replicas), Idempotent Producer  |                 |
| **Used by:**    | Kafka Transactions, Kafka Streams, Structured Streaming    |                 |
| **Related:**    | Idempotent Producer, Transactional Producer, Kafka Streams |                 |

---

### 🔥 The Problem This Solves

**NETWORK FAILURES CAUSE DUPLICATE OR LOST MESSAGES:**
A producer writes a payment event, the broker receives it, the broker crashes before sending an ACK. Producer's write() times out. Producer retries. Broker restarts, processes the retry — the original write is ALSO recovered from its write-ahead log. Result: payment processed twice. Traditional solutions: at-most-once (don't retry → risk loss) or at-least-once (retry → risk duplicates). Exactly-once eliminates both: broker deduplicates the retry using sequence numbers, and transactions ensure the consume→produce pipeline is atomic.

---

### 📘 Textbook Definition

**Exactly-Once Semantics (EOS)** means: each message is processed exactly once, regardless of failures and retries.

Three levels of exactly-once in Kafka:

1. **Idempotent Producer** (single-partition, single-session): each producer assigned a unique `producerId (PID)`. Each message sent with a `sequenceNumber` (0, 1, 2...). Broker tracks `(PID, sequenceNumber)` → deduplicates exact retries. Doesn't survive producer restart.

2. **Kafka Transactions** (multi-partition atomicity): a producer assigned a `transactionalId` (survives restarts). All messages in a transaction are committed atomically — either all visible or none. Consumer configured with `isolation.level=read_committed` sees only committed messages.

3. **Kafka Streams EOS**: reads input offset + writes output message + commits input offset in a single atomic transaction. Ensures: no message is processed twice, no output is produced without the input offset being committed.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
EOS = idempotent producer (deduplicates retries by sequence number) + transactions (atomic multi-partition writes) + offset-output atomicity (Kafka Streams reads and writes atomically).

**One analogy:**

> A bank's wire transfer system:
>
> - **At-most-once**: transfer once, don't retry. If it fails: no debit, no credit — money lost in the ether.
> - **At-least-once**: retry until success. If network fails between bank's "transfer done" and your confirmation: retry = double transfer.
> - **Exactly-once**: each transfer has a unique `transferId`. If you try twice with same `transferId`: second attempt is a no-op (idempotent). The debit and credit are one atomic transaction: either both happen or neither.

**One insight:**
EOS in Kafka is often misunderstood as "the broker guarantees no duplicates." In reality, **EOS requires all three layers**: (1) idempotent producer (eliminates duplicate writes), (2) consumer `isolation.level=read_committed` (eliminates reading uncommitted/aborted messages), (3) atomic output-and-offset commit (ensures processing isn't redone after failure). Missing any layer breaks EOS. The most common mistake: enabling producer idempotence but not using transactions for the full read-process-write cycle.

---

### 🔩 First Principles Explanation

**LAYER 1 — IDEMPOTENT PRODUCER:**

```java
// Idempotent producer: enable.idempotence=true
// Each producer gets a PID (Producer ID) from the broker on startup
// Each message gets a SequenceNumber per partition (0, 1, 2, 3...)

// producer.properties:
enable.idempotence=true
acks=all                                       // required for idempotence
retries=2147483647                             // retry indefinitely
max.in.flight.requests.per.connection=5        // up to 5 unacked requests

// How deduplication works:
// T=0: Producer sends (PID=42, P0, seqNum=100, data=M)
// T=1: Broker receives M, appends to P0, records (PID=42, seqNum=100)
// T=2: Network timeout → Producer doesn't get ACK
// T=3: Producer RETRIES (PID=42, P0, seqNum=100, data=M)  ← same seqNum
// T=4: Broker receives retry: (PID=42, seqNum=100) already seen → DISCARD duplicate
//      Sends ACK (like it worked the first time)
// Result: M appears exactly ONCE in P0

// LIMITATION: PID is ephemeral (assigned per producer session)
// If producer restarts: gets new PID → new sequence numbers → can't dedup across restarts
// Solution for cross-restart idempotence: TRANSACTIONS (see below)
```

**LAYER 2 — KAFKA TRANSACTIONS:**

```java
// Transactional producer: transactional.id="payment-service-1"
// transactionalId is stable across restarts → enables cross-session dedup

@Configuration
public class KafkaTransactionalProducerConfig {

    @Bean
    public ProducerFactory<String, Object> transactionalProducerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "payment-service-1");
        // IMPORTANT: each producer instance must have UNIQUE transactionalId
        // For N instances: payment-service-0, payment-service-1, ... payment-service-N-1
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        DefaultKafkaProducerFactory<String, Object> factory =
            new DefaultKafkaProducerFactory<>(props);
        factory.setTransactionIdPrefix("payment-txn-");  // Spring adds suffix per instance
        return factory;
    }
}

@Service
public class PaymentService {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Transactional  // Spring manages Kafka transaction via KafkaTransactionManager
    public void processPayment(Payment payment) {
        // All of these are in ONE atomic Kafka transaction:
        kafkaTemplate.send("payment-events", payment.getId(), payment);
        kafkaTemplate.send("account-debits", payment.getUserId(), new DebitEvent(payment));
        kafkaTemplate.send("notifications", payment.getUserId(), new PaymentNotification(payment));
        // Either ALL three are written, or NONE (transaction aborted on exception)
    }
}
```

**KAFKA TRANSACTION PROTOCOL (2PC):**

```
Transaction lifecycle:
  1. initTransactions(): producer registers with Transaction Coordinator (TC)
     TC assigns: epoch to transactionalId (fencing old zombie instances)

  2. beginTransaction(): mark start of transaction in memory

  3. send() × N: write messages to multiple partitions
     TC: records all partitions involved in this transaction
     Messages written to broker logs but INVISIBLE to read_committed consumers

  4. commitTransaction():
     a. TC writes "PREPARE_COMMIT" to transaction log (durable)
     b. TC writes commit markers to all involved partitions
     c. TC writes "COMPLETE_COMMIT" to transaction log
     d. All messages in transaction now VISIBLE to read_committed consumers

  abortTransaction():
     a. TC writes "PREPARE_ABORT"
     b. TC writes abort markers to all partitions
     c. Messages permanently invisible

Consumer with isolation.level=read_committed:
  - Only reads messages UP TO the last committed transaction marker
  - Messages from in-progress or aborted transactions: SKIPPED
  - Acts as if uncommitted/aborted messages never existed

Consumer with isolation.level=read_uncommitted (default):
  - Reads ALL messages (including in-progress transactions)
  - May see "dirty reads" from aborted transactions
```

**KAFKA STREAMS — FULL EOS READ-PROCESS-WRITE:**

```java
// Kafka Streams EOS: read input + write output + commit input offset ATOMICALLY

Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-processor");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");

// EOS v1 (Kafka 0.11+): EXACTLY_ONCE
// EOS v2 (Kafka 2.5+): EXACTLY_ONCE_V2 (better performance, fewer coordinators)
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);

// With EOS enabled:
// - Each task gets a unique transactional.id
// - Input offsets and output messages committed in one atomic transaction
// - If crash after processing but before commit: transaction aborted
//   → On recovery: re-reads same input messages (input offset not committed)
//   → Re-processes → commits output + offset atomically
//   → Consumer of output sees each message exactly once

StreamsBuilder builder = new StreamsBuilder();
KStream<String, Order> orders = builder.stream("orders");
KStream<String, Invoice> invoices = orders
    .filter((key, order) -> order.getAmount() > 0)
    .mapValues(order -> Invoice.from(order));
invoices.to("invoices");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

**PERFORMANCE COST OF EOS:**

```
acks=all (required for EOS):
  → Wait for all ISR replicas (2-3ms extra latency vs acks=1)
  → Required for durability

enable.idempotence=true:
  → Sequence number tracking per partition (minimal overhead)
  → max.in.flight.requests limited to 5

Transactions:
  → beginTransaction(), commitTransaction() round trips to TC (~2ms each)
  → Commit requires write to transaction log (durable, N broker writes)
  → EOS throughput: ~50-70% of non-transactional throughput

BENCHMARK (approximate, varies by hardware):
  Without EOS (acks=1): ~1M messages/sec
  With idempotent producer only: ~700K messages/sec
  With full transactions (EOS): ~300-500K messages/sec

  For most business workloads: EOS cost is acceptable
  For pure throughput (logging, metrics): use acks=0 or acks=1
```

---

### 🧪 Thought Experiment

**EXACTLY-ONCE IS NOT ENOUGH WITHOUT AN IDEMPOTENT CONSUMER:**

Kafka EOS guarantees that each message is in the output Kafka topic exactly once. But if the consumer of that output topic does a non-idempotent operation (e.g., `INSERT INTO orders VALUES (...)` without a unique constraint), a consumer restart and replay will insert duplicates in the database.

**The full picture:**

- Kafka → Kafka: EOS achievable with transactions
- Kafka → Database: need **idempotent sink** (upsert with unique key, `INSERT ... ON CONFLICT DO NOTHING`)
- Kafka → External API: need **idempotency key** in the API call

EOS is about the Kafka layer. The system-wide exactly-once guarantee requires idempotency at every layer the message passes through.

---

### 🧠 Mental Model / Analogy

> EOS is like a notarized contract signing:
>
> - **Idempotent producer**: the notary checks "was this document already signed?" using a serial number — no double-stamping the same document.
> - **Transaction**: all signatories (multiple Kafka partitions) must sign in one session — either all sign or none sign. No partial execution.
> - **Kafka Streams atomicity**: the notary confirms both "the client gave me the document" (input offset committed) and "I stamped it" (output written) in the same official record — a crash between the two is undone and the process repeats.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** EOS = no duplicates + no loss. Kafka achieves via: (1) idempotent producer (sequence numbers dedup retries), (2) transactions (atomic multi-partition writes), (3) Kafka Streams atomic read+write. Costs: ~30-50% throughput reduction. Essential for financial/critical pipelines.

**Level 2:** Idempotent producer: `enable.idempotence=true`, broker deduplicates by (PID, seqNum). Transactions: `transactionalId` survives restarts; 2PC protocol; consumer needs `isolation.level=read_committed`. Kafka Streams EOS: `EXACTLY_ONCE_V2` — input offset + output atomic.

**Level 3:** Transaction coordinator (TC): one broker partition in `__transaction_state` topic manages each `transactionalId`. Epoch: on restart with same `transactionalId`, TC bumps epoch — old zombie producer with stale epoch is rejected ("fencing"). `EXACTLY_ONCE_V2` vs V1: V2 uses per-input-partition transactions (not per-task), reducing coordinator load and improving throughput.

**Level 4:** EOS is a guarantee about the Kafka log only. End-to-end system exactly-once (Kafka → external DB → external API) requires: (1) idempotent writes to external DB (upsert/ON CONFLICT), (2) idempotency keys for external APIs, (3) outbox pattern + CDC to bridge Kafka transactions with DB transactions. True end-to-end EOS across heterogeneous systems is extremely complex — most production systems accept at-least-once with idempotent consumers (semantic deduplication at the application layer) as a pragmatic compromise.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ KAFKA EXACTLY-ONCE: READ → PROCESS → WRITE           │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Input topic "orders" (source)                       │
│       ↓ read with read_committed isolation           │
│ [Kafka Streams Task]                                 │
│   beginTransaction()                                 │
│   process(order)                                     │
│   send(invoice) → output topic "invoices"           │
│   commitOffsets(input: orders-P0-offset=100)        │
│   commitTransaction() → ATOMIC (both or neither)    │
│ [EOS ← YOU ARE HERE: atomic read+write]              │
│       ↓                                              │
│ Output topic "invoices" (only committed messages)   │
│                                                      │
│ Crash after send() but before commit:               │
│   TC: aborts transaction → invoice NOT visible      │
│   Input offset NOT committed → re-read order 100   │
│   Re-process → new transaction → commit → visible  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Payment processing with Kafka EOS:

1. Producer: beginTransaction()
2. Producer: send("payment-events", paymentId, paymentEvent) — invisible to consumers
3. Producer: send("account-debits", userId, debitEvent) — invisible
4. Producer: commitTransaction()
   → TC: writes PREPARE_COMMIT
   → TC: writes commit markers to payment-events + account-debits
   → Both messages NOW VISIBLE to read_committed consumers

Consumer "ledger-service" (isolation.level=read_committed):
5. Reads payment event → processes → updates ledger
6. Reads debit event → processes → updates ledger
   Both guaranteed to appear atomically — no partial state

Failure scenario:
   Producer crashes after step 3, before step 4:
   TC: detects no commitTransaction → writes ABORT marker
   Both messages permanently invisible
   Producer restarts with same transactionalId:
   TC: issues new epoch → old zombie producer fenced
   Producer: re-processes and re-sends → new transaction → commit
   Result: one payment-event + one debit-event (exactly once)
```

---

### ⚖️ Comparison Table

| Semantic      | Behavior                         | Use Case                                        |
| ------------- | -------------------------------- | ----------------------------------------------- |
| At-most-once  | May lose messages (no retry)     | Metrics, logs (loss acceptable)                 |
| At-least-once | May duplicate (retry on failure) | Most business events (with idempotent consumer) |
| Exactly-once  | No loss, no duplicates           | Financial transactions, billing, inventory      |

| EOS Layer           | Mechanism                        | Scope                            |
| ------------------- | -------------------------------- | -------------------------------- |
| Idempotent producer | (PID, seqNum) deduplication      | Single partition, single session |
| Transactions        | 2PC with Transaction Coordinator | Multi-partition, cross-session   |
| Kafka Streams EOS   | Atomic read+write transaction    | Full pipeline                    |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "enable.idempotence=true = exactly-once"    | Idempotent producer eliminates duplicates from retries on a SINGLE partition within ONE session. It doesn't handle: producer restart (new PID), multi-partition atomicity, or consumer-side processing |
| "EOS means zero duplicates in the database" | Kafka EOS is about the Kafka log. If your consumer does non-idempotent DB writes, you can still get duplicates. EOS in Kafka + idempotent consumer = system-wide exactly-once                          |
| "EOS is always worth the cost"              | For logging, metrics, click tracking: at-least-once with idempotent consumers is usually sufficient and 2-3× faster. Use full EOS only when the cost of duplicates exceeds the throughput cost         |

---

### 🚨 Failure Modes & Diagnosis

**1. Transaction Timeout — Long Transactions Aborted**

**Symptom:** Producers failing with `ProducerFencedException` or `TimeoutException`. Transactions are being aborted.

**Root Cause:** Transaction took longer than `transaction.timeout.ms` (default 60s). TC aborts long-running transactions. Common cause: slow processing within a transaction, or waiting for a slow external call inside `beginTransaction()...commitTransaction()`.

**Fix:** Keep transactions short (milliseconds, not seconds). Move slow operations outside the transaction. Increase `transaction.timeout.ms` if unavoidable (max 900000ms = 15 min):

```java
props.put(ProducerConfig.TRANSACTION_TIMEOUT_CONFIG, 30000);  // 30s
// Or as broker config: transaction.max.timeout.ms=900000
```

---

### 🔗 Related Keywords

**Prerequisites:** Apache Kafka, ISR (In-Sync Replicas)
**Builds On This:** Idempotent Producer, Transactional Producer, Kafka Streams
**Related:** Idempotent Producer, Transactional Producer, Kafka Streams

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ IDEMPOTENT  │ enable.idempotence=true → (PID,seqNum) dedup│
│ TRANSACTION │ transactionalId → atomic multi-part write  │
│ ISOLATION   │ read_committed → no dirty reads            │
│ STREAMS EOS │ EXACTLY_ONCE_V2 → atomic read+write       │
│ 2PC COORD   │ Transaction Coordinator manages 2PC        │
│ FENCING     │ Epoch increments on restart → no zombie    │
│ COST        │ ~30-50% throughput reduction               │
│ DB EOS      │ Needs idempotent sink (upsert/ON CONFLICT) │
│ USE WHEN    │ Financial, billing, inventory — no dups OK │
│ ONE-LINER   │ "Sequence numbers dedup retries; 2PC txn  │
│             │  atomicity; Streams atomic read+write"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain the three layers of Kafka's exactly-once semantics. What is the role of the Transaction Coordinator? What is "epoch fencing" and why is it important?

**Q2.** (TYPE C — Design) A payment service reads from Kafka, updates a PostgreSQL database, and produces a confirmation to another Kafka topic. Design an exactly-once pipeline. What guarantees does Kafka provide and what must your application code provide?
