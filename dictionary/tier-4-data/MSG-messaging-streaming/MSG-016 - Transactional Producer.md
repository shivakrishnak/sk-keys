---
version: 2
layout: default
title: "Transactional Producer"
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /messaging-streaming/transactional-producer/
id: MSG-016
category: Messaging & Event Streaming
difficulty: ★★★
depends_on: Idempotent Producer, Exactly-Once Semantics, Apache Kafka
used_by: Kafka Streams, Event-Driven Architecture, Exactly-Once Semantics
related: Idempotent Producer, Exactly-Once Semantics, Consumer Group
tags:
  - transactional-producer
  - kafka-transactions
  - exactly-once
  - 2pc
  - deep-dive
---

# MSG-016 - Transactional Producer

⚡ TL;DR - **Transactional Producer** extends idempotent producer with a **stable `transactionalId`** (survives restarts) and a **2PC protocol** via a **Transaction Coordinator** - `beginTransaction()` → `send()` to multiple partitions → `commitTransaction()` makes all messages atomically visible to `read_committed` consumers; **epoch fencing** (TC bumps epoch on restart) kills zombie producers from prior sessions; provides **cross-partition, cross-session exactly-once** semantics at ~30-50% throughput cost.

| #550            | Category: Big Data & Streaming                                   | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Idempotent Producer, Exactly-Once Semantics, Apache Kafka        |                 |
| **Used by:**    | Kafka Streams, Event-Driven Architecture, Exactly-Once Semantics |                 |
| **Related:**    | Idempotent Producer, Exactly-Once Semantics, Consumer Group      |                 |

---

### 🔥 The Problem This Solves

**IDEMPOTENT PRODUCER HAS TWO GAPS:**

1. **Producer restart**: PID is ephemeral → restart gets new PID → retried messages after restart are NOT deduplicated → DUPLICATES.
2. **Multi-partition atomicity**: sending to two partitions (say, "order-events" and "inventory-reservations") can partially succeed - first partition written, then crash - leaving inconsistent state.

Transactional producer solves BOTH: a stable `transactionalId` (human-assigned string) persists across restarts and is used to maintain sequence numbers across sessions. The 2PC commit protocol ensures all-or-nothing across partitions.

---

### 📘 Textbook Definition

**Transactional Producer** is a Kafka producer that participates in Kafka's transaction protocol, providing:

1. **Cross-session idempotence**: `transactionalId` is a stable, user-assigned string (e.g., `"payment-service-1"`). On restart, the same `transactionalId` is used → Transaction Coordinator (TC) associates the new PID with the same `transactionalId` → sequence numbers are fenced against old PIDs.
2. **Multi-partition atomicity**: all messages in a transaction are committed atomically - consumers with `isolation.level=read_committed` see them all or none.
3. **Zombie fencing via epoch**: each time a producer (re)initializes with a `transactionalId`, the TC increments an epoch. Any old producer instance attempting to write with a stale epoch gets a `ProducerFencedException`.

Key methods:

- `initTransactions()`: called once on startup. Registers with TC, bumps epoch if recovering.
- `beginTransaction()`: starts a new transaction (in memory only).
- `send()`: writes messages - visible to `read_committed` consumers only AFTER `commitTransaction()`.
- `commitTransaction()`: 2PC commit. TC makes all messages in this transaction visible.
- `abortTransaction()`: 2PC abort. All messages in this transaction are permanently invisible.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Transactional producer = idempotent producer + stable transactionalId (survives restarts) + 2PC coordinator (atomic multi-partition commit) + epoch fencing (kills zombie producers).

**One analogy:**

> A restaurant's POS system processes orders: debit card + kitchen ticket are two systems. Idempotent = no duplicate charges (sequence numbers). Transactional = both the charge AND the kitchen ticket are issued atomically - kitchen never gets a ticket without a charge, and a charge always produces a kitchen ticket. If the system crashes mid-way: on restart (same `transactionalId` = same restaurant), the TC says "was the last transaction committed? No → abort it → start fresh."

**One insight:**
The most common production use case for transactional producers is Kafka Streams. When Kafka Streams uses `EXACTLY_ONCE_V2`, each task (input partition) has its own transactional producer with a stable `transactionalId` = `${applicationId}-${taskId}`. This means: reading an input offset + writing output + committing the input offset happen in one atomic transaction. If the application restarts, the TC recognizes the `transactionalId` and fences any zombie. You don't write this code - Kafka Streams does. Understanding transactions is how you understand what Kafka Streams EOS actually does.

---

### 🔩 First Principles Explanation

**TRANSACTIONAL PRODUCER CONFIGURATION:**

```java
@Configuration
public class KafkaTransactionalConfig {

    @Bean
    public ProducerFactory<String, Object> transactionalProducerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");

        // Transactional ID: MUST be stable across restarts, UNIQUE per producer instance
        // Pattern for multi-instance apps: use instance ID or pod name
        String instanceId = System.getenv().getOrDefault("POD_NAME", "payment-service-0");
        props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "payment-txn-" + instanceId);
        // payment-txn-payment-service-0, payment-txn-payment-service-1, etc.

        // Idempotence is IMPLICITLY enabled by transactionalId
        // acks, retries, max.in.flight also auto-configured

        // Transaction timeout (broker-side): abort if not committed in time
        props.put(ProducerConfig.TRANSACTION_TIMEOUT_CONFIG, 30000);  // 30s

        DefaultKafkaProducerFactory<String, Object> factory =
            new DefaultKafkaProducerFactory<>(props);
        // NOTE: Do NOT set transactionIdPrefix if you set transactionalId directly
        // (Spring's transactionIdPrefix appends a suffix - use one or the other)
        return factory;
    }

    @Bean
    public KafkaTransactionManager<String, Object> kafkaTransactionManager(
            ProducerFactory<String, Object> pf) {
        return new KafkaTransactionManager<>(pf);
    }
}
```

**USING TRANSACTIONS - LOW-LEVEL API:**

```java
@Service
public class OrderTransactionService {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    // LOW-LEVEL: manual transaction control
    public void processOrderManually(Order order) {
        Producer<String, Object> producer = kafkaTemplate.getProducerFactory()
            .createTransactionalProducer();

        producer.initTransactions();  // called ONCE per producer instance lifecycle

        try {
            producer.beginTransaction();

            // Write to multiple topics atomically:
            ProducerRecord<String, Object> orderRecord =
                new ProducerRecord<>("order-events", order.getId(), order);
            ProducerRecord<String, Object> inventoryRecord =
                new ProducerRecord<>("inventory-reservations",
                    order.getProductId(), new Reservation(order));
            ProducerRecord<String, Object> auditRecord =
                new ProducerRecord<>("audit-log", order.getId(),
                    new AuditEntry("order_created", order));

            producer.send(orderRecord);
            producer.send(inventoryRecord);
            producer.send(auditRecord);

            producer.commitTransaction();
            // At this point: all 3 records visible to read_committed consumers

        } catch (ProducerFencedException e) {
            // CRITICAL: zombie fencing - another instance has taken over this transactionalId
            // Do NOT call abortTransaction() - it won't work
            // Close this producer and do NOT retry - the new instance will handle it
            producer.close();
            throw new RuntimeException("Producer fenced - another instance is active", e);

        } catch (KafkaException e) {
            producer.abortTransaction();
            // All 3 records permanently invisible - no partial state
            throw e;
        }
    }

    // SPRING INTEGRATION: @Transactional with KafkaTransactionManager
    @Transactional("kafkaTransactionManager")
    public void processOrderWithSpring(Order order) {
        // Spring manages beginTransaction/commitTransaction/abortTransaction
        kafkaTemplate.send("order-events", order.getId(), order);
        kafkaTemplate.send("inventory-reservations", order.getProductId(),
            new Reservation(order));
        // If exception thrown here → Spring calls abortTransaction()
        // On success → Spring calls commitTransaction()
    }

    // COMBINING KAFKA + DB TRANSACTION (chained transactions):
    @Transactional  // DB transaction (JPA/Spring)
    public void processOrderWithDbAndKafka(Order order) {
        // 1. Save to DB:
        orderRepository.save(order);

        // 2. Publish Kafka event (using executeInTransaction):
        kafkaTemplate.executeInTransaction(ops -> {
            ops.send("order-events", order.getId(), order);
            return true;
        });
        // NOTE: Kafka transaction and DB transaction are SEPARATE transactions
        // If DB commit succeeds but Kafka commit fails (or vice versa):
        //   → Use Outbox Pattern for true atomicity across DB + Kafka
        // This pattern (save to DB + publish to Kafka) is at-least-once at best
    }
}
```

**TRANSACTION COORDINATOR (TC) INTERNALS:**

```
Transaction Coordinator (TC):
  - A Kafka broker partition leader of "__transaction_state" internal topic
  - Each transactionalId hashes to one TC partition → consistent assignment
  - TC stores transaction state in "__transaction_state"

2PC Protocol for commitTransaction():

Phase 1 - PREPARE:
  Producer → TC: "commit transaction TxnId=X, involved partitions: [orders-P1, inventory-P2, audit-P0]"
  TC: writes {TxnId=X, status=PREPARE_COMMIT, partitions=[orders-P1, inventory-P2, audit-P0]}
        to __transaction_state (durably)
  TC → Producer: "prepared, proceed"

Phase 2 - COMMIT:
  TC → Broker(orders-P1): write commit marker for TxnId=X
  TC → Broker(inventory-P2): write commit marker for TxnId=X
  TC → Broker(audit-P0): write commit marker for TxnId=X
  (These are special control records - not consumer-visible data)
  All markers written → TC writes {TxnId=X, status=COMPLETE_COMMIT}

  Consumer (read_committed isolation):
  Reads records from each partition
  Encounters uncommitted records → HOLDS (reads up to High Watermark - uncommitted msgs)
  Sees commit markers → all messages in transaction NOW VISIBLE

  Crash Recovery:
  If broker restarts after PREPARE_COMMIT but before writing commit markers:
  TC: reads __transaction_state → sees PREPARE_COMMIT → sends commit markers again
  (TC acts as coordinator to complete the commit - 2PC guarantees completion)

EPOCH FENCING:
  transactionalId="payment-service-0" → epoch=3
  Producer instance A (epoch=3) is writing
  Instance A crashes
  Instance B starts with transactionalId="payment-service-0"
  TC: increments epoch to 4, provides PID+epoch=4 to Instance B
  Instance A recovers from crash and tries to write:
  Broker sees epoch=3 → current epoch=4 → STALE → ProducerFencedException
  Instance A is a "zombie" - killed before it can write stale data
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS IF YOU REUSE transactionalId ACROSS INSTANCES?**

Suppose you deploy two pods with `transactionalId="payment-service"` (same string). Pod 1 is writing. Pod 2 starts and calls `initTransactions()` with the same `transactionalId`. The TC bumps the epoch. Pod 1 is now fenced - its next `send()` throws `ProducerFencedException`.

This is intentional! Two pods should never share a `transactionalId`. But if your deployment has N pods and they all read from the same environment variable that returns the same string - you'll fence each other on every restart. The `transactionalId` MUST be unique per producer instance (use pod name or replica index).

---

### 🧠 Mental Model / Analogy

> The Transaction Coordinator is like a wedding registrar. The bride (Producer) registers under a transactionalId ("Smith-Johnson-Wedding"). She fills out the registry (beginTransaction + send messages). The registrar (TC) records everything she's registered. When she says "commit" (commitTransaction), the registrar stamps it official - everyone can now see the registry. If the bride shows up again (restart), she proves her identity via transactionalId, and the registrar gives her a new epoch (new ID card) - invalidating any old imposters (zombie producers with stale epoch).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Transactional producer = stable transactionalId + 2PC commit. All messages in a transaction are visible atomically to `read_committed` consumers. Commit or abort. Used by Kafka Streams EOS.

**Level 2:** `initTransactions()` once on startup. `beginTransaction()` → `send()` to N partitions → `commitTransaction()` or `abortTransaction()`. Transaction Coordinator manages 2PC. `read_committed` isolation needed on consumer side.

**Level 3:** 2PC: PREPARE_COMMIT written to `__transaction_state` (durable) → commit markers written to all involved partitions → COMPLETE_COMMIT. On crash after PREPARE: TC completes the commit on recovery (2PC guarantee). Epoch: incremented on each `initTransactions()` call with same `transactionalId`. Stale epoch → `ProducerFencedException` (zombie fencing).

**Level 4:** `transactionalId` must be unique per producer instance (not per service). Pattern: `{serviceName}-{instanceId}`. KEDA or manual pod scaling: each new pod gets its own transactionalId → no fencing. Kafka Streams uses `${applicationId}-${taskId}` → tasks are deterministic (same task always on same partition → same transactionalId → stable across restarts). Transaction log (`__transaction_state`) is a compacted topic - TC state persists across TC restarts. Performance: each transaction requires 2 round trips to TC (prepare + complete) → target 10-100 messages per transaction for good throughput.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ TRANSACTIONAL PRODUCER COMMIT FLOW                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Producer (transactionalId="pay-svc-0", epoch=5):    │
│   beginTransaction()                                 │
│   send(orders-P1, OrderA) → in-flight, uncommitted  │
│   send(inventory-P2, ResA) → in-flight, uncommitted │
│   commitTransaction()                                │
│         ↓                                            │
│ [TC ← YOU ARE HERE: 2PC coordinator]                │
│   Write PREPARE_COMMIT to __transaction_state        │
│         ↓                                            │
│   Write commit markers to orders-P1 + inventory-P2  │
│         ↓                                            │
│   Write COMPLETE_COMMIT to __transaction_state       │
│         ↓                                            │
│ Consumer (read_committed):                          │
│   Reads orders-P1: OrderA + commit marker → VISIBLE │
│   Reads inventory-P2: ResA + commit marker → VISIBLE│
│   OrderA and ResA appear atomically                 │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Payment service restart scenario (epoch fencing):

T=0: PaymentService Pod-0 starts
     initTransactions(transactionalId="pay-svc-0") → epoch=5, PID=200

T=10: Pod-0 is mid-transaction: sent to orders-P1, NOT yet committed
T=11: Pod-0 crashes (network partition - not dead, just partitioned)

T=12: Kubernetes starts Pod-1 (new instance, same transactionalId="pay-svc-0")
      initTransactions() → TC: bumps epoch to 6, PID=201
      TC: detects open transaction from epoch=5 → writes ABORT marker
      (old transaction from Pod-0 is aborted - messages invisible)

T=13: Pod-1 begins new transaction with epoch=6
      beginTransaction()
      send(orders-P1, OrderA)  ← epoch=6 in message headers
      send(inventory-P2, ResA) ← epoch=6
      commitTransaction() → 2PC → COMPLETE_COMMIT

T=14: Pod-0 recovers from network partition, tries to send:
      send(orders-P1, OrderA) with epoch=5
      Broker: current epoch=6 → received epoch=5 → STALE → ProducerFencedException
      Pod-0: catches ProducerFencedException → closes producer
      → Pod-0 is zombie-killed

Result: OrderA processed exactly once (by Pod-1's epoch=6 transaction)
```

---

### ⚖️ Comparison Table

| Feature         | Idempotent Producer                  | Transactional Producer                   |
| --------------- | ------------------------------------ | ---------------------------------------- |
| Session scope   | Per session (PID resets on restart)  | Cross-session (transactionalId persists) |
| Partition scope | Per partition                        | Multi-partition atomic                   |
| Zombie fencing  | No (new PID on restart, no fencing)  | Yes (epoch fencing via TC)               |
| Configuration   | enable.idempotence=true              | transactionalId="..."                    |
| Consumer config | Any                                  | isolation.level=read_committed           |
| Overhead        | Minimal                              | ~30-50% throughput reduction             |
| Use case        | Single partition, single session EOS | Multi-partition, Kafka Streams EOS       |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Transactions make Kafka like a relational database"        | Kafka transactions are append-only and Kafka-scoped. No rollback of existing data, no foreign keys, no isolation levels beyond read_committed. It's atomic append across partitions, not ACID in the RDBMS sense                                                                |
| "I need transactions for all Kafka-to-DB writes"            | Kafka transactions only ensure atomic writes across Kafka partitions. Kafka→DB atomicity requires the Outbox Pattern (write to DB + outbox table in one DB transaction; relay publishes from outbox to Kafka). Kafka transactions + DB writes are separate 2PCs and can diverge |
| "transactionalId can be the same for all service instances" | Must be unique per producer instance. Sharing a transactionalId between two running instances causes mutual fencing (each restart fences the other). Use pod name, replica index, or UUID per instance                                                                          |

---

### 🚨 Failure Modes & Diagnosis

**1. ProducerFencedException - Transaction Hijacked**

**Symptom:** Producer throws `ProducerFencedException`. Application stops writing to Kafka.

**Root Cause:** Another producer instance initialized with the same `transactionalId`, bumping the epoch. Old instance is now fenced. Common causes: (1) transactionalId not unique per pod (configuration bug), (2) Kubernetes rolling deploy where old pod overlaps with new pod (both use same transactionalId), (3) consumer group rebalance causes Kafka Streams to reassign tasks → each task's producer reinitializes.

**Fix:**

```java
// WRONG: shared transactionalId
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "payment-service");
// Two pods → mutual fencing

// RIGHT: unique per instance
String podName = System.getenv("HOSTNAME");  // Kubernetes sets this = pod name
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "payment-service-" + podName);

// Handle ProducerFencedException in code:
try {
    producer.commitTransaction();
} catch (ProducerFencedException e) {
    // Do NOT abort - this producer is no longer valid
    // Do NOT retry - a new instance has taken over
    producer.close(Duration.ZERO);  // close immediately without timeout
    // Application should re-initialize with a new producer
    // or let Kubernetes restart the pod
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Idempotent Producer, Exactly-Once Semantics, Apache Kafka
**Builds On This:** Kafka Streams EOS
**Related:** Idempotent Producer, Exactly-Once Semantics, Consumer Group

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ transactionalId  │ Stable string, unique per instance   │
│ initTransactions │ Called ONCE on startup; bumps epoch  │
│ beginTransaction │ Starts tx (in memory)                │
│ commitTransaction│ 2PC: PREPARE → markers → COMPLETE    │
│ abortTransaction │ All msgs in tx permanently invisible │
│ EPOCH FENCING    │ Old epoch rejected → zombie killed   │
│ TC               │ Transaction Coordinator manages 2PC  │
│ CONSUMER         │ isolation.level=read_committed       │
│ COST             │ ~30-50% throughput vs non-txn        │
│ FENCED EXCEPTION │ ProducerFencedException → close, die │
│ ONE-LINER        │ "Stable ID + epoch fencing + 2PC =  │
│                  │  atomic multi-partition exactly-once" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) What is epoch fencing in Kafka transactions? Why is it important? What happens when two producers share the same transactionalId?

**Q2.** (TYPE C - Design) A microservice needs to: (1) write an order to PostgreSQL, (2) publish an "order-placed" event to Kafka topic A, (3) publish an "inventory-decrement" command to Kafka topic B. All three must succeed or none. Can Kafka transactions solve this? If not, what pattern would you use?
