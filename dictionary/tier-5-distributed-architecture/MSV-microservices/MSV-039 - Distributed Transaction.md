---
layout: default
title: "Distributed Transaction"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /microservices/distributed-transaction/
id: MSV-039
category: Microservices
difficulty: ★★★
depends_on: Database Fundamentals, Two-Phase Commit (2PC), CAP Theorem
used_by: Saga Pattern (Microservices), CQRS in Microservices, Outbox Pattern
related: Two-Phase Commit (2PC), Saga Pattern (Microservices), Eventual Consistency (Microservices)
tags:
  - microservices
  - distributed
  - database
  - reliability
  - deep-dive
status: complete
version: 1
---

# MSV-039 - Distributed Transaction

⚡ TL;DR - A distributed transaction atomically spans multiple databases or services, but the fundamental tension with microservices autonomy makes true atomicity impractical at scale.

| #654            | Category: Microservices                                                                    | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Database Fundamentals, Two-Phase Commit (2PC), CAP Theorem                                 |                 |
| **Used by:**    | Saga Pattern (Microservices), CQRS in Microservices, Outbox Pattern                        |                 |
| **Related:**    | Two-Phase Commit (2PC), Saga Pattern (Microservices), Eventual Consistency (Microservices) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a monolith, you call `BEGIN TRANSACTION`, update three tables, and `COMMIT`. Either all three updates stick or none do. When you split that monolith into microservices, each service owns its own database. Suddenly, updating three services requires three separate database operations with no coordination. If service B's update succeeds and service C's fails, you have inconsistent data with no automatic rollback.

**THE BREAKING POINT:**
Business operations frequently span entities owned by different services. Moving money between accounts, fulfilling an order, processing a subscription cancellation - each involves writes to multiple independent datastores. Without coordination, partial failure leaves the system in an impossible state: money debited but not credited, inventory reduced but no order created.

**THE INVENTION MOMENT:**
This is exactly why distributed transactions were explored - to provide the same "all-or-nothing" guarantee across service boundaries that ACID transactions provide within a single database.


**EVOLUTION:**
Two-Phase Commit (2PC) was proposed by Jim Gray in 1978 as the solution for atomicity across multiple nodes. XA transactions (X/Open DTP, 1991) standardised 2PC for distributed databases. The Paxos consensus algorithm (Leslie Lamport, 1989) provided a foundation for agreement without a single coordinator. In microservices, teams discovered that 2PC's requirements (all participants locked during commit, coordinator as single point of failure) were incompatible with service independence requirements. Saga became the preferred alternative. The discipline evolved from 'use 2PC for cross-service consistency' to 'design for eventual consistency with explicit compensation.'
---

### 📘 Textbook Definition

A **distributed transaction** is a transaction that spans multiple independent data stores or services, requiring all participating resources to either commit or rollback together. The classical implementation uses Two-Phase Commit (2PC), where a coordinator manages a prepare/commit protocol across all participants. In modern microservices, true distributed transactions are largely replaced by saga patterns (with compensating transactions) or the Outbox Pattern, because 2PC conflicts with service autonomy, introduces distributed locking, and creates availability bottlenecks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Make writes to multiple separate databases succeed or fail together - but this is fundamentally hard in distributed systems.

**One analogy:**

> Paying a restaurant bill split across three credit cards: you need all three charges to go through, or none. If one card declines after the others succeed, you need to reverse the successful charges. Distributed transactions automate this reversal - but require all banks to "hold" the money while the decision is made.

**One insight:**
The uncomfortable truth: true ACID distributed transactions require all participants to hold locks until the coordinator decides. This means a single slow service can block all others. For this reason, the industry has largely moved from distributed transactions to saga patterns that accept temporary inconsistency in exchange for availability.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. ACID atomicity requires all changes commit together or not at all.
2. Network partitions can separate the coordinator from participants at any moment.
3. Locks held across a network cannot be held indefinitely - the holder may crash.

**DERIVED DESIGN:**
**Two-Phase Commit (2PC) - the classical approach:**

Phase 1 (Prepare): Coordinator asks each participant "can you commit?" Each participant acquires locks and writes to a local write-ahead log. Responds YES or NO.

Phase 2 (Commit/Rollback): If all YES → coordinator sends COMMIT; all release locks. If any NO → coordinator sends ROLLBACK; all undo.

**The fundamental problem:** Between Phase 1 and Phase 2, if the coordinator crashes, participants are in "uncertain" state - they have locks held and don't know whether to commit or rollback. They must block, waiting for coordinator recovery. This is called the _blocking problem_ of 2PC.

**Three-Phase Commit (3PC)** adds a "pre-commit" phase to reduce blocking but still cannot handle network partitions (FLP Impossibility Theorem: no distributed consensus algorithm can be both safe and live under asynchronous message passing with failures).

**The microservices answer:**
Accept eventual consistency. Use sagas for long-lived transactions. Use Outbox Pattern for reliable event publishing. Design business processes to tolerate temporary inconsistency with semantic locking (status=PENDING).

**THE TRADE-OFFS:**
**Gain (2PC):** True atomicity across services; no intermediate visible states.
**Cost (2PC):** Distributed locking; coordinator SPOF; blocking on crash; throughput limited by slowest participant; couples all participants to coordinator protocol.
**Gain (Saga/Eventual):** High availability; no cross-service locking; each service independent.
**Cost (Saga/Eventual):** Temporary inconsistency; compensation complexity; visible intermediate states require application-level handling.

---

### 🧪 Thought Experiment

**SETUP:**
Transfer $100 from Account A (Bank Service) to Account B (Bank Service). They're in the same service but imagine they could be separate.

**WHAT HAPPENS WITHOUT COORDINATION:**
Debit A: success. Credit B: database crash. A is debited, B is not credited. $100 vanishes. No recovery mechanism. Manual fix required.

**WHAT HAPPENS WITH 2PC:**
Coordinator asks both: "ready to debit A and credit B?" Both lock rows and log to WAL. Both say YES. Coordinator sends COMMIT. Both commit atomically. If B crashes after prepare but before commit, B's WAL has the intent - it commits on recovery.

**WHAT HAPPENS WITH SAGA:**
Debit A: local transaction. Emit `AccountDebited` event. Credit B service listens: credit B, emit `AccountCredited`. If credit fails, compensating transaction: re-credit A. Temporary state: A debited but B not yet credited (detectable by status=PENDING on the transfer).

**THE INSIGHT:**
2PC is correct but brittle. Saga is eventually correct and robust. The choice is a business decision: can you tolerate the 50ms–500ms window where $100 is "in flight" but not yet received? For most business operations, yes. For financial settlement, you need explicit accounting for in-flight state.

---

### 🧠 Mental Model / Analogy

> A conductor leads an orchestra to perform a piece simultaneously. The conductor holds their baton raised (prepare phase) - all musicians have their instruments ready, waiting. When the baton drops (commit), all play together. If the conductor faints (coordinator crash) while the baton is raised, all musicians are frozen - instruments up, waiting, unable to proceed or stand down.

- "Conductor" → transaction coordinator
- "Baton raised" → prepare phase; participants hold locks
- "Baton drops" → commit signal
- "Conductor faints" → coordinator crash
- "Musicians frozen" → participants blocked in uncertain state
- "Orchestra manager takes over" → coordinator recovery from WAL

Where this analogy breaks down: real orchestras can make independent decisions - distributed participants cannot without risking inconsistency, which is the exact reason 2PC forces them to wait.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A distributed transaction is an attempt to make writes to multiple separate systems succeed or fail as one unit - like making sure two bank transfers happen together, not one without the other.

**Level 2 - How to use it (junior developer):**
In practice, avoid distributed transactions in microservices. Use saga pattern instead. If you must use them (legacy system integration), use XA transactions with a JTA transaction manager (Atomikos, Narayana). Configure each data source as an XA resource and wrap operations in `@Transactional`.

**Level 3 - How it works (mid-level engineer):**
XA protocol: Java's standard for 2PC. The `XADataSource` interface exposes `start()`, `end()`, `prepare()`, `commit()`, `rollback()`. A JTA transaction manager coordinates across multiple XA datasources. Each datasource writes a prepare record to its WAL before returning YES to the coordinator. The WAL ensures the participant can commit on recovery even if it crashed before the coordinator's commit signal arrived.

**Level 4 - Why it was designed this way (senior/staff):**
2PC was designed for tightly-coupled, co-located systems of the 1980s-90s (relational databases in the same datacenter). The assumption: lock holding times are milliseconds, coordinator crashes are rare. In microservices across clouds, these assumptions break: locks may be held for seconds (GC pauses), coordinators can be partitioned, and services are independently deployed. The CAP theorem makes strong consistency across partitioned services impossible. The industry's answer: embrace BASE (Basically Available, Soft-state, Eventual consistency) and design business logic to tolerate transient inconsistency.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│    Two-Phase Commit Protocol                            │
└─────────────────────────────────────────────────────────┘

Coordinator         Service A           Service B
    │                   │                   │
    │──PREPARE──────────►│                   │
    │──PREPARE───────────────────────────────►│
    │                   │ Locks rows         │ Locks rows
    │                   │ Writes WAL         │ Writes WAL
    │◄──YES─────────────│                   │
    │◄──YES──────────────────────────────────│
    │                   │                   │
    │──COMMIT───────────►│                   │
    │──COMMIT────────────────────────────────►│
    │                   │ Commits            │ Commits
    │                   │ Releases locks     │ Releases locks
    │◄──ACK─────────────│                   │
    │◄──ACK──────────────────────────────────│
    │
    │ [TRANSACTION COMPLETE]

FAILURE CASE - Coordinator crash after PREPARE:
    Participants: LOCKED, WAL written, UNCERTAIN
    Cannot commit or rollback without coordinator
    Participants BLOCK until coordinator recovers
```

**XA transaction in Java (Atomikos):**

```java
@Configuration
public class XAConfig {
  @Bean
  public JtaTransactionManager transactionManager() {
    UserTransactionManager utm =
      new UserTransactionManager();
    return new JtaTransactionManager(utm, utm);
  }
  // Both datasources registered as XA resources
}

@Transactional  // JTA-managed - spans both DBs
public void transfer(String from, String to,
                     BigDecimal amount) {
  accountRepository.debit(from, amount);  // DB1
  ledgerRepository.credit(to, amount);    // DB2
  // XA commit coordinates both atomically
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Business Operation spans Services A+B]
  → [Coordinator begins 2PC ← YOU ARE HERE]
  → [PREPARE: A locks, B locks]
  → [Both YES]
  → [COMMIT: A commits, B commits]
  → [Transaction complete]
```

**FAILURE PATH:**

```
[B returns NO during PREPARE]
  → [Coordinator sends ROLLBACK to A and B]
  → [A undoes prepare, B undoes prepare]
  → [Transaction aborted cleanly]

[Coordinator crashes after PREPARE]
  → [A and B BLOCKED - uncertain state]
  → [Must wait for coordinator recovery]
  → [Recovery: read coordinator WAL, send COMMIT/ROLLBACK]
```

**WHAT CHANGES AT SCALE:**
At 1k TPS, 2PC adds ~5–10ms latency (2 network round trips). At 10k TPS, coordinator becomes throughput bottleneck. At 100k TPS, distributed locking across services makes 2PC impractical - saga or event sourcing is the only viable approach. At global scale, 2PC across regions (100ms+ round trips × 2 phases) adds 200ms+ to every transaction, making it commercially unusable for user-facing operations.

---

### 💻 Code Example

**Example 1 - Why 2PC breaks in microservices:**

```java
// Service A database
@Repository OrderRepository orderRepo; // DB: orders-db

// Service B database - SEPARATE DATABASE SERVER
@Repository InventoryRepository inventoryRepo; // DB: inventory-db

// PROBLEM: @Transactional wraps ONE datasource only
@Transactional  // Only covers orderRepo's datasource!
public void createOrderAndReserveInventory(Order order) {
  orderRepo.save(order);           // commits to orders-db
  inventoryRepo.reserve(order);    // separate tx on inventory-db
  // If inventory fails here: order saved, inventory NOT reserved
  // @Transactional rollback only rolls back orders-db
}
```

**Example 2 - Saga replaces distributed transaction:**

```java
// No cross-service transaction - sequential local transactions
@Service
public class CheckoutService {
  public void checkout(Order order) {
    // Local transaction to orders-db only
    String orderId = orderService.createOrder(order);

    // Message triggers inventory service's OWN local tx
    eventBus.publish(new OrderCreatedEvent(orderId, order));

    // If inventory fails, compensation event rolls back order
  }
}
```

**Example 3 - XA transaction (when unavoidable, e.g., legacy):**

```java
// Both datasources must be XA-capable
@Bean
public XADataSource ordersXADataSource() {
  PGXADataSource ds = new PGXADataSource();
  ds.setUrl("jdbc:postgresql://orders-db/orders");
  return ds;
}

@Bean
public XADataSource inventoryXADataSource() {
  PGXADataSource ds = new PGXADataSource();
  ds.setUrl("jdbc:postgresql://inv-db/inventory");
  return ds;
}

@Transactional(transactionManager = "jtaTxManager")
public void atomicOperation() {
  ordersRepo.save(order);      // XA resource 1
  inventoryRepo.reserve(item); // XA resource 2
  // JTA coordinator runs 2PC across both
}
```

---

### ⚖️ Comparison Table

| Approach                      | Consistency   | Availability   | Latency              | Best For                                |
| ----------------------------- | ------------- | -------------- | -------------------- | --------------------------------------- |
| **2PC / XA**                  | Strong (ACID) | Low (blocking) | High (2 round trips) | Co-located services, short transactions |
| Saga (Orchestration)          | Eventual      | High           | Medium               | Complex multi-step flows                |
| Saga (Choreography)           | Eventual      | High           | Medium               | Simple event chains                     |
| Outbox + Events               | Eventual      | High           | Low                  | Reliable event publishing               |
| Best-effort (no coordination) | None          | Highest        | Lowest               | Idempotent reads                        |

**How to choose:** Prefer saga over 2PC for microservices. Use 2PC only within a single service that happens to write to two tightly-coupled, co-located databases (unusual).

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Microservices can easily use 2PC like monoliths did  | 2PC across service-owned databases violates autonomy and creates SPOF                                  |
| Saga is "almost as good" as distributed transactions | Saga is intentionally weaker - it accepts temporary inconsistency                                      |
| XA transactions are production-safe in microservices | XA across services creates distributed locks; one slow service blocks all others                       |
| The coordinator can always recover gracefully        | Coordinator crash during prepare puts participants in uncertain, blocking state                        |
| Eventual consistency means data loss                 | Eventual consistency means temporary inconsistency, not data loss - saga guarantees all-or-compensated |

---

### 🚨 Failure Modes & Diagnosis

**Heuristic Transaction Completion (XA Hazard)**

**Symptom:** After coordinator outage, one participant committed and another rolled back. Data is permanently inconsistent.

**Root Cause:** XA participant's administrator used "heuristic rollback" to unblock the system while coordinator was still recovering. Both sides diverged.

**Diagnostic Command:**

```bash
# Check for XA transactions in PREPARED state
# (PostgreSQL)
SELECT * FROM pg_prepared_xacts;
# Any entries older than a few seconds = problem
```

**Fix:** Never use heuristic completion without understanding the cross-service state. Coordinate recovery from WAL.

**Prevention:** Monitor `pg_prepared_xacts` - alert on any entry older than 30 seconds.

---

**Coordinator as Single Point of Failure**

**Symptom:** All transactions fail when coordinator service restarts or is slow.

**Root Cause:** 2PC coordinator is a centralised service with no HA setup.

**Diagnostic Command:**

```bash
# Check coordinator availability
curl -s http://transaction-coordinator/health
# Check for pending prepared transactions
SELECT count(*) FROM pg_prepared_xacts;
```

**Fix:** Run coordinator in HA mode with leader election (Raft-based). Or migrate to saga pattern.

**Prevention:** Design without single transaction coordinators - prefer saga or event-driven patterns.

---

**Lock Contention Under 2PC**

**Symptom:** Transaction latency spikes to 5–30 seconds; timeouts cascade; database shows high lock wait time.

**Root Cause:** 2PC prepare phase holds database locks for duration of coordinator round trip. Slow services cascade into lock buildup.

**Diagnostic Command:**

```bash
# PostgreSQL lock waits
SELECT pid, wait_event, query, query_start
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
ORDER BY query_start;
```

**Fix:** Add timeouts to 2PC prepare; reduce prepare-to-commit window; migrate to saga.

**Prevention:** Benchmark 2PC lock duration under realistic failure scenarios before production deployment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Database Fundamentals` - ACID properties and local transaction semantics
- `Two-Phase Commit (2PC)` - the classical distributed transaction protocol
- `CAP Theorem` - explains why strong consistency across partitioned services is impossible

**Builds On This (learn these next):**

- `Saga Pattern (Microservices)` - the practical replacement for distributed transactions
- `Outbox Pattern` - ensures reliable event publishing without distributed transactions
- `CQRS in Microservices` - separates command handling, reducing the need for multi-service writes

**Alternatives / Comparisons:**

- `Saga Pattern (Microservices)` - event-driven alternative with compensation
- `Eventual Consistency (Microservices)` - the consistency model sagas provide
- `Idempotency (Distributed)` - enables safe retry that substitutes for strong atomicity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Atomic operation spanning multiple        │
│              │ independent databases or services         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Business operations cross service         │
│ SOLVES       │ boundaries but need all-or-nothing        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ True distributed transactions require     │
│              │ distributed locking - incompatible with   │
│              │ microservice autonomy at scale            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Co-located, tightly-coupled legacy        │
│              │ systems where 2PC is the only option      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Modern microservices - use saga instead   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Strong atomicity vs availability,         │
│              │ throughput, and service autonomy          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Perfect consistency that breaks          │
│              │  everything else"                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Two-Phase Commit → Saga Pattern →         │
│              │ Outbox Pattern                            │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Distributed consistency and high availability are in direct tension. 2PC requires all participants to be available and responsive for the full duration of the transaction - a 100ms transaction has a 100ms window where all participants must be locked and available. Every distributed transaction is a bet that availability will hold for its duration. When that bet fails, the transaction blocks until the coordinator recovers.

**Where else this pattern appears:**
- **Consensus protocols:** Raft and Paxos solve distributed agreement using quorum-based consensus rather than all-or-nothing 2PC commit - achieving consistency without a single coordinator blocking on all participants.
- **Synchronous database replication:** All replicas must acknowledge before commit - strong consistency at the cost of availability if any replica is slow or unreachable.
- **Git push:** Local commit (local consistency) then push to remote (remote consistency eventually) - eventual consistency applied to distributed version control.

---

### 💡 The Surprising Truth

The most dangerous property of 2PC is the blocking period when the coordinator crashes after receiving all YES votes but before sending COMMIT. All participants are in 'prepared' state: resources locked, cannot proceed or abort unilaterally. If the coordinator's transaction log is unavailable, participants remain blocked until the coordinator recovers - which can take minutes to hours in a real production failure. Teams using 2PC in microservices often discover this blocking behavior for the first time during their first coordinator-host failure in production.
---

### 🧠 Think About This Before We Continue

**Q1.** You have a 2PC transaction coordinating two services. The coordinator sends PREPARE to both, both return YES, then the coordinator crashes before sending COMMIT. Service A is locked in "uncertain" state. Service B is also uncertain. A new coordinator starts from WAL and sees the transaction was in the prepare phase with all-YES. What must it do, and why? Now consider: the coordinator's WAL was on the same host that crashed and the WAL is corrupt. What happens? Is this recoverable?

*Hint:* Think about what 'prepared' state means: both participants have locked resources and are waiting for a decision. The new coordinator reads the WAL, sees all-YES was received, and by protocol must send COMMIT (aborting would violate the atomicity guarantee since both participants agreed). It sends COMMIT and both proceed normally. Now consider corrupt WAL: no coordinator has the transaction state. Both participants are stuck indefinitely - this is the 'blocking problem' of 2PC and requires DBA manual intervention to resolve.

**Q2.** Your team is migrating from a monolith with `@Transactional` spanning three tables to three microservices. The tech lead says "just use XA with a JTA transaction manager - it's the same thing." You argue for a saga. Write the exact argument: what specific scenario makes XA fail that saga handles correctly? What does the saga cost that XA would give you for free?

*Hint:* Think about what XA fails at in microservices: XA holds locks on all participants from PREPARE to COMMIT. If any participant restarts during this window, XA enters a blocking state. With saga: each step completes and releases locks immediately; compensation handles failures. The saga's cost vs XA: saga cannot provide true atomicity (intermediate state is visible during execution); XA provides apparent atomicity (no intermediate state visible externally) at the cost of availability during the transaction window.

**Q3 (Design Trade-off):** A financial system requires that account debit and account credit be atomic - either both happen or neither. The two accounts live in different microservices. Design the strongest possible consistency guarantee without using 2PC, and specify what consistency level this achieves.

*Hint:* Think about what 'strongest without 2PC' means: the Outbox pattern (debit + debit-event in one local transaction; event consumer applies credit idempotently) provides eventual consistency with at-least-once delivery and no data loss. The window of inconsistency is bounded to the event processing latency (typically milliseconds to seconds). Explore whether the business requirement actually needs true atomicity or whether a bounded-eventual model (both operations complete within N seconds or the transaction is flagged for manual review) satisfies the regulatory requirement.
