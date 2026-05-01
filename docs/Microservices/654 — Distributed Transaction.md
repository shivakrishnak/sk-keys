---
layout: default
title: "Distributed Transaction"
parent: "Microservices"
nav_order: 654
permalink: /microservices/distributed-transaction/
number: "654"
category: Microservices
difficulty: ★★★
depends_on: "Saga Pattern (Microservices), Eventual Consistency (Microservices)"
used_by: "Saga Pattern (Microservices), CQRS in Microservices, Event Sourcing in Microservices"
tags: #advanced, #microservices, #distributed, #database, #pattern
---

# 654 — Distributed Transaction

`#advanced` `#microservices` `#distributed` `#database` `#pattern`

⚡ TL;DR — A **Distributed Transaction** coordinates a single atomic operation across multiple databases or services. True ACID distributed transactions require **Two-Phase Commit (2PC)** — which has serious availability and performance problems in microservices. The practical alternative is the **Saga Pattern** (eventual consistency through compensating transactions).

| #654            | Category: Microservices                                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Saga Pattern (Microservices), Eventual Consistency (Microservices)                   |                 |
| **Used by:**    | Saga Pattern (Microservices), CQRS in Microservices, Event Sourcing in Microservices |                 |

---

### 📘 Textbook Definition

A **Distributed Transaction** is a database transaction that spans multiple independent data stores (databases, services, resource managers) and must satisfy ACID (Atomicity, Consistency, Isolation, Durability) properties across all of them. The standard protocol for distributed transactions is **Two-Phase Commit (2PC)**: in Phase 1 (Prepare/Voting), the transaction coordinator asks all participants to prepare their local transaction and vote yes/no; in Phase 2 (Commit/Abort), if all vote yes, the coordinator sends commit; if any vote no, the coordinator sends abort to all participants. 2PC is implemented by transaction managers (XA standard: X/Open XA) and is supported by JDBC drivers, JMS brokers, and application servers (JBoss, WebLogic). In microservices, 2PC is generally avoided because: it requires synchronous coordination across all services; it holds locks across all databases during coordination; it has availability problems (coordinator crash leaves participants locked); and most cloud services and NoSQL databases don't support XA. The recommended alternative is the Saga Pattern using compensating transactions.

---

### 🟢 Simple Definition (Easy)

A distributed transaction is "one transaction that spans two or more databases." If you update both `OrderService.db` and `PaymentService.db`, and both updates must either succeed or both fail — that's a distributed transaction. The challenge: you can't do a normal SQL COMMIT that covers both databases simultaneously. Traditional solution: Two-Phase Commit (complex, fragile). Microservices solution: Saga (eventual consistency through compensating transactions).

---

### 🔵 Simple Definition (Elaborated)

Debiting $100 from a bank account (`FinanceService.db`) and adding a payment record (`PaymentService.db`) must both happen atomically — no half-done state. Two-Phase Commit: a transaction coordinator tells both databases to prepare (hold locks), then commits both. But what if the coordinator crashes after `FinanceService` commits but before `PaymentService` commits? $100 debited, no payment record created — money lost. This is the "in-doubt transaction" problem of 2PC. In microservices, instead use a Saga: debit account, publish "AccountDebited" event, PaymentService records payment on consuming the event. If payment fails: publish compensating "RefundToAccount" event. Eventually consistent — not atomically consistent.

---

### 🔩 First Principles Explanation

**Two-Phase Commit — protocol and failure modes:**

```
2PC PROTOCOL:

  Coordinator (Transaction Manager)
    │
    ├── Participant 1: OrderService.db (PostgreSQL)
    ├── Participant 2: PaymentService.db (MySQL)
    └── Participant 3: InventoryService.db (PostgreSQL)

PHASE 1 (PREPARE):
  Coordinator → "Prepare, transaction T1"
  Each participant:
    - Executes all SQL statements for T1 locally
    - Writes PREPARED record to local WAL (write-ahead log)
    - Acquires all necessary locks
    - Responds YES (ready to commit) or NO (abort)

PHASE 2A (COMMIT) — if all YES:
  Coordinator → "Commit T1"
  Each participant:
    - Writes COMMITTED record to WAL
    - Releases locks
    - Responds ACK

PHASE 2B (ROLLBACK) — if any NO:
  Coordinator → "Abort T1" to all participants
  Each participant: rollback local changes, release locks

FAILURE MODES:
  1. Coordinator crashes BEFORE Phase 2:
     Participants are in PREPARED state (holding locks).
     Cannot commit, cannot abort (don't know coordinator's decision).
     Locks held indefinitely → BLOCKED state.
     Recovery: new coordinator reads WAL → if all YES → commit; else abort.
     Window of blocked locks: until coordinator recovers.

  2. Participant crashes during Phase 1:
     Coordinator receives timeout → sends ABORT to all.
     Safe: no participant committed.

  3. Network partition DURING Phase 2:
     Coordinator commits participant A.
     Network drops → participant B and C never receive COMMIT.
     B and C stay in PREPARED state (holding locks) until network recovers.
     → Inconsistent state during partition window.

  KEY PROBLEM: 2PC is a BLOCKING protocol.
  During any coordinator failure: participants hold locks, system blocked.
  This is unacceptable for microservices with many distributed components.
```

**Why 2PC fails in microservices specifically:**

```
MICROSERVICES ENVIRONMENT:
  Services deploy independently (multiple per day)
  Services crash independently (pods restart, Kubernetes evictions)
  Services use different databases (Postgres, MongoDB, Cassandra, DynamoDB)
  Services may be in different cloud providers

2PC REQUIREMENTS:
  1. All databases must support XA protocol
     DynamoDB: NO XA support
     MongoDB: limited XA (4.0+, single replica set)
     Cassandra: NO XA support
     → Can't use 2PC if ANY service uses a non-XA database

  2. Transaction coordinator must be highly available
     Coordinator failure = all participants blocked
     HA coordinator: complex to implement, maintain

  3. All participants must be reachable during prepare + commit
     Kubernetes: pods restart frequently
     During pod restart: XA participant unreachable → all others blocked

  4. Performance:
     2PC requires 2 round trips + locks across all participants
     For a 4-service transaction: 8 network round trips minimum
     At p99 latency of 50ms per hop: 400ms minimum coordination overhead
     NOT acceptable for high-throughput operations

CONCLUSION: 2PC is viable for small, stable, same-infrastructure monolithic systems.
            For microservices: use Saga + compensating transactions instead.
```

**XA transactions in Java (for context — not recommended for microservices):**

```java
// Java XA (javax.transaction.UserTransaction):
// Used in traditional Java EE application servers, NOT in microservices:

@Transactional  // Spring @Transactional with JTA transaction manager
public void processOrder(Order order) {
    // With JTA (Java Transaction API) + XA datasources:
    // Both DB operations are part of same distributed XA transaction
    orderRepository.save(order);             // XA resource 1: OrderDB
    paymentRepository.createPayment(order);  // XA resource 2: PaymentDB

    // If either throws an exception: both are rolled back (2PC automatically)
    // Coordinator: Bitronix, Atomikos, or JBoss TM
}

// WHY NOT IN MICROSERVICES:
// orderRepository calls OrderService's DB directly (same JVM) — OK for monolith
// paymentRepository would need to call PaymentService via HTTP — NOT a DB resource
// You cannot include HTTP calls in an XA transaction
// → XA/2PC only works when services share the same JVM or direct DB access
```

---

### ❓ Why Does This Exist (Why Before What)

Business operations often span multiple resources. A bank transfer must debit one account AND credit another atomically. In a monolith with one database, this is trivial. As systems grow, databases are separated, services split out, and cloud databases with no XA support are adopted. Distributed transactions solve the fundamental question: "how do we ensure all or nothing across multiple independent resources?" The answer varies by context: 2PC for traditional systems, Saga for microservices.

---

### 🧠 Mental Model / Analogy

> A 2PC distributed transaction is like a choir performing in perfect synchrony. The conductor (coordinator) raises the baton (Phase 1: prepare) — every singer takes a breath and signals ready. The conductor drops the baton (Phase 2: commit) — every singer starts simultaneously. If the conductor collapses between raising and dropping the baton: every singer freezes mid-breath, waiting for a signal that may never come. The performance is blocked indefinitely. A Saga is like the same choir where each section starts when the previous section finishes a phrase — no conductor needed, each section listens for the previous section's cue. If the tenors fail their phrase, the basses (who haven't started yet) stay quiet, and the sopranos (who already sang) repeat their phrase to undo it.

---

### ⚙️ How It Works (Mechanism)

**Alternatives to 2PC in microservices:**

```
OPTION 1: Saga Pattern (most common)
  → See Saga Pattern entry #653
  → Eventual consistency through compensating transactions
  → Choreography or Orchestration style

OPTION 2: Outbox Pattern
  → Write event to outbox table in same DB transaction as business data
  → Outbox publisher sends event to message broker asynchronously
  → Ensures at-least-once event delivery without distributed transaction

OPTION 3: Change Data Capture (CDC)
  → Debezium monitors PostgreSQL WAL for INSERT/UPDATE/DELETE
  → Automatically publishes changed records as events to Kafka
  → No outbox table needed; uses DB's native change stream

OPTION 4: Try-Confirm-Cancel (TCC)
  → Service exposes: tryReserve (tentative), confirm (commit), cancel (rollback)
  → Coordinator calls tryReserve on all services
  → If all succeed: call confirm on all
  → If any fail: call cancel on all that succeeded
  → Application-level 2PC with semantic operations
  → Better availability than XA 2PC but still requires coordinator
  → Used in: Seata (Apache), ByteTCC
```

---

### 🔄 How It Connects (Mini-Map)

```
ACID transactions (single DB — trivial)
        │
        ▼
Distributed Transaction  ◄──── (you are here)
(multi-DB atomicity problem)
        │
        ├── Two-Phase Commit (2PC/XA) → traditional solution, impractical for microservices
        └── Saga Pattern → microservices solution (eventual consistency)
            ├── Eventual Consistency → accepted trade-off
            └── Event Sourcing → events as the mechanism
```

---

### 💻 Code Example

**Outbox Pattern — reliable event publication without 2PC:**

```java
// Instead of distributed transaction or Kafka transaction:
// Write to outbox table in same ACID transaction as business data

@Transactional
public Order placeOrder(CreateOrderRequest request) {
    // STEP 1: Create order in OrderDB (local ACID transaction):
    Order order = orderRepository.save(new Order(
        request.getProductId(), request.getCustomerId(), OrderStatus.PENDING
    ));

    // STEP 2: Write event to OUTBOX in SAME transaction (atomic!):
    outboxRepository.save(new OutboxEvent(
        UUID.randomUUID().toString(),    // event ID (idempotency key for consumer)
        "order-placed-events",           // target Kafka topic
        order.getId().toString(),        // partition key
        serialize(new OrderPlacedEvent(order)),  // event payload
        OutboxStatus.PENDING
    ));

    return order;
    // If commit succeeds: both order + outbox event persisted atomically
    // If commit fails: neither persisted → no event published → consistent
}

// Separate publisher reads outbox (no distributed transaction needed):
@Scheduled(fixedDelay = 1_000)
@Transactional
void publishOutboxEvents() {
    outboxRepository.findByStatus(OutboxStatus.PENDING).forEach(event -> {
        kafkaTemplate.send(event.getTopic(), event.getKey(), event.getPayload())
            .addCallback(
                result -> outboxRepository.markPublished(event),
                failure -> log.error("Failed to publish outbox event {}", event.getId())
            );
    });
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                  |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Two-Phase Commit guarantees perfect atomicity             | 2PC guarantees atomicity only when the transaction manager and all participants recover correctly. During network partitions or coordinator crashes, 2PC can leave participants in in-doubt state for extended periods                                                   |
| Sagas are inferior to 2PC because they lack ACID          | Sagas deliberately trade isolation (I in ACID) for availability and decoupling. For most business operations, eventual consistency is acceptable. For strict financial operations requiring isolation, design the saga carefully with idempotency and optimistic locking |
| You can use JTA/@Transactional to span microservice calls | JTA/XA coordinates resources within the same JVM (datasources, JMS queues registered with the transaction manager). You cannot include remote HTTP service calls in an XA transaction — they are not XA resources                                                        |

---

### 🔥 Pitfalls in Production

**In-doubt XA transactions blocking production database**

```
SCENARIO (in a legacy system still using 2PC):
  JBoss transaction coordinator crashes during Phase 2.
  PostgreSQL has 3 prepared transactions (in PREPARED state).
  pg_prepared_xacts shows 3 rows, each holding locks on critical tables.
  Application cannot INSERT/UPDATE on these tables.
  Production is DOWN.

DIAGNOSIS:
  SELECT * FROM pg_prepared_xacts;
  -- xact_start: 2024-01-15 03:45:00 (2 hours ago!)
  -- gid: 'java:jboss:1234' (XA global transaction ID)

RESOLUTION (emergency):
  ROLLBACK PREPARED 'java:jboss:1234';  -- manually abort the prepared transaction
  -- WARNING: This may cause inconsistency if other participants committed!
  -- Must check transaction manager logs to determine commit/abort decision

PREVENTION:
  In microservices: don't use 2PC/XA
  Use Saga + Outbox Pattern instead
  If legacy XA is unavoidable:
    - Monitor pg_prepared_xacts for stale prepared transactions
    - Set lock timeout on prepared transactions
    - Ensure HA transaction coordinator (Atomikos, Bitronix cluster)
```

---

### 🔗 Related Keywords

- `Saga Pattern (Microservices)` — the practical alternative to distributed ACID transactions
- `Eventual Consistency (Microservices)` — the consistency model after abandoning 2PC
- `Event Sourcing in Microservices` — provides durable event log for saga coordination
- `CQRS in Microservices` — often paired with sagas for separate read/write models

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 2PC PHASES   │ Prepare (lock + vote) → Commit/Abort      │
│ 2PC PROBLEM  │ Blocking protocol. Coordinator SPOF.      │
│              │ Most NoSQL doesn't support XA             │
├──────────────┼───────────────────────────────────────────┤
│ IN MICROSVCS │ DON'T use 2PC. Use Saga instead.          │
├──────────────┼───────────────────────────────────────────┤
│ ALTERNATIVES │ Saga + Compensating Transactions          │
│              │ Outbox Pattern (reliable event publishing) │
│              │ CDC (Change Data Capture via Debezium)     │
│              │ TCC (Try-Confirm-Cancel — app-level 2PC)   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The XA protocol's "in-doubt transaction" window is a real production risk in 2PC systems. Describe the exact database state during an in-doubt transaction: which tables/rows are locked, what happens to concurrent reads and writes that touch the same rows, and how long can an in-doubt transaction persist. For a high-traffic e-commerce database, quantify the impact: if a popular product table row is locked by an in-doubt transaction for 60 seconds, how many checkout operations are blocked?

**Q2.** The Try-Confirm-Cancel (TCC) pattern is described as "application-level 2PC." Design the TCC operations for an order placement transaction across `InventoryService` and `PaymentService`: (a) what does `InventoryService.tryReserveInventory()` do — does it actually decrement stock or create a tentative reservation? (b) What does `InventoryService.cancelReservation()` do? (c) What is the timeout for the "try" phase, and what happens to a try reservation that never receives a confirm or cancel? Compare TCC reliability vs Saga reliability in terms of failure recovery.
