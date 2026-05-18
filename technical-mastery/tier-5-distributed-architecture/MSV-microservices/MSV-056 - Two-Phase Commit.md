---
id: MSV-056
title: Two-Phase Commit
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-047, MSV-046
used_by: MSV-047, MSV-046
related: MSV-047, MSV-046, MSV-057, MSV-049, MSV-054, MSV-058
tags:
  - microservices
  - distributed
  - deep-dive
  - transactions
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/microservices/two-phase-commit/
---

⚡ TL;DR - Two-Phase Commit (2PC) is a distributed
consensus protocol that ensures atomicity across
multiple resource managers (databases, message
brokers). Phase 1 (Prepare): coordinator asks all
participants "can you commit?" All must reply YES.
Phase 2 (Commit): coordinator sends COMMIT; all
participants commit. If any participant replies NO
in Phase 1: coordinator sends ROLLBACK to all.
Problem: blocking protocol - if coordinator fails
after Phase 1, participants are blocked (in-doubt
transaction). For microservices: Kafka doesn't
support XA; 2PC across services is impractical.
Alternative: Saga Pattern.

| #056 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Distributed Transaction, Saga Pattern | |
| **Used by:** | Distributed Transaction, Saga Pattern | |
| **Related:** | Distributed Transaction, Saga Pattern, Compensating Transaction, Eventual Consistency in Microservices, Outbox Pattern, Idempotency in Microservices | |

---

### 🔥 The Problem This Solves

In a distributed system: you need to write to two
databases atomically. Either both succeed or both
fail. Without coordination: DB1 write succeeds,
DB2 write fails = inconsistent state. 2PC solves
this by coordinating a two-step atomic commit
across multiple resource managers. Used in: JTA
(Java Transaction API), XA transactions, some
distributed databases. In microservices: rarely
used directly (Kafka does not support XA); Saga
Pattern is preferred.

---

### 📘 Textbook Definition

**Two-Phase Commit (2PC)** is a distributed atomic
commit protocol that coordinates multiple processes
(participants) to agree on committing or aborting
a distributed transaction. Two phases: (1) Prepare
phase - coordinator sends PREPARE to all participants;
each participant writes the transaction to its
durable log and replies PREPARED (YES) or NO.
(2) Commit phase - if all replied YES: coordinator
writes COMMIT to its log, sends COMMIT to all;
if any replied NO: coordinator writes ABORT, sends
ROLLBACK to all. Participants commit/rollback and
release locks. Guarantees: atomicity (all or nothing)
and durability (committed data survives crashes).
Does NOT guarantee availability during coordinator
failure: participants in PREPARED state must wait
(blocking protocol).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
2PC: coordinator asks all participants "ready to
commit?" If all yes: commit all. If any no: rollback
all. Atomic but blocking on coordinator failure.

**One analogy:**
> A wedding ceremony. The officiant (coordinator)
asks each party: "Do you take this person as your
spouse?" (Prepare phase). Each must answer YES.
If both say YES: officiant declares "You are
married!" (Commit phase). If either says NO:
the ceremony is called off (Rollback). The ceremony
cannot complete until BOTH parties respond.
Problem: if the officiant collapses after both
said YES but before announcing it: both parties
are in limbo - married? Not married? They must
wait for a replacement officiant to check the
log and resume (in-doubt transaction resolution).

**One insight:**
2PC is blocking: if the coordinator crashes after
Phase 1 PREPARE (all participants ready) but before
Phase 2 COMMIT: all participants are locked (holding
locks, resource reserved) until the coordinator
recoveries. In practice: coordinator recovery takes
seconds to minutes. During this time: all participants
cannot service other requests on the locked resources.
This is why 2PC is impractical at scale and why
microservices use Saga (non-blocking, eventual) instead.

---

### 🔩 First Principles Explanation

**2PC PROTOCOL STATES:**

```
NORMAL EXECUTION:

  Coordinator                Participant A    Participant B
  ----------                 -------------    -------------
  BEGIN TRANSACTION
  PREPARE          --------> store in log     store in log
                   --------> lock resources   lock
                     resources
                   <-------- PREPARED         PREPARED
  All PREPARED:
  Write COMMIT               
  to coord log
  COMMIT           --------> commit           commit
                   --------> release locks    release locks
                   <-------- ACK              ACK
  DONE

FAILURE SCENARIO 1: Participant fails before PREPARE
  Coordinator: receives NO response
  Action: send ROLLBACK to all
  Result: clean rollback; no in-doubt state

FAILURE SCENARIO 2: Coordinator fails after all PREPARED
  Participants A and B: in PREPARED state
  - Locks held, cannot rollback, cannot commit
  - Must wait for coordinator recovery
  Recovery:
    Coordinator restarts, reads log
    Log shows: sent PREPARE to A, B; received PREPARED
    Coordinator was about to COMMIT
    Action: sends COMMIT to A and B
  In-doubt window: coordinator restart time (seconds)
```

**WHY 2PC FAILS IN MICROSERVICES:**

```
REQUIREMENTS FOR 2PC:
  1. All participants must support XA protocol
  2. Coordinator must be able to reach all participants
  3. Resource managers: must support two-phase locking
  
MICROSERVICES REALITY:
  Kafka: does NOT support XA transactions
  REST APIs: no XA protocol
  Different databases: XA support varies
  Cross-internet: network unreliable, high latency
  Participants may have different ownership teams
  
RESULT:
  2PC in microservices: impractical for most cases
  Exception: within a single service's own resources
  (e.g., two databases in same data center with XA)
  Across service boundaries: use Saga Pattern instead
```

---

### 🧪 Thought Experiment

**2PC VS SAGA COMPARISON:**

```
SCENARIO: Place order (debit account + reserve inventory)

2PC APPROACH:
  Coordinator: begin XA transaction TXN-001
  Phase 1:
    payment-db: PREPARE (lock $99.99 in account)
    inventory-db: PREPARE (lock 1 unit of SKU-123)
  Phase 2:
    Both PREPARED:
    payment-db: COMMIT (debit account)
    inventory-db: COMMIT (decrease inventory)
  Result: atomic, immediate consistency
  Problem: what if payment-db and inventory-db
           are in different services/different orgs?
           Kafka is between them? -> 2PC fails

SAGA APPROACH:
  OrderCreated event published
  payment-service: processes PaymentRequest
    -> publishes PaymentProcessed
  inventory-service: processes InventoryReserve
    -> publishes InventoryReserved
  order-service: confirms order
  Failure: payment fails
    -> order-service compensates:
       InventoryReleased compensation event
       OrderCancelled
  Result: eventually consistent (not immediate)
          non-blocking (no locks across services)
          works with Kafka, REST, any transport
```

---

### 🧠 Mental Model / Analogy

> 2PC is like a synchronized diving competition.
> The head judge (coordinator) asks each judge:
> "Are you ready to score?" (Prepare). All judges
> must respond YES. The head judge then says
> "Score now!" (Commit), and all judges simultaneously
> raise their scorecards. If the head judge falls
> ill between asking and saying "score now":
> all judges are frozen, hand raised, waiting.
> Nobody can move until the head judge recovers.
> This blocking behavior is the fundamental
> limitation of 2PC.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
2PC: a way for multiple databases to either all
save data at the same time, or all cancel. Like
asking multiple people to press a button at exactly
the same time - works well, but if the coordinator
gets stuck, everyone waits.

**Level 2 - How it applies (junior developer):**
JTA with Spring: `@Transactional` on methods that
use multiple DataSources configured with XADataSource.
Atomikos or Bitronix as JTA transaction manager.
Both databases: commit or rollback together. Works
for: multiple databases within same service's data
center. Does NOT work across services or with Kafka.

**Level 3 - How it works (mid-level engineer):**
XA protocol: each resource manager (database)
exposes `XAResource` interface with `prepare()`,
`commit()`, `rollback()`. Transaction Manager calls
prepare on all XAResources; if all return XA_OK:
calls commit on all. Databases use write-ahead
logging to ensure durability during prepare phase.
In-doubt transactions: coordinator's log is the
ordinal log for recovery.

**Level 4 - Why it's avoided (senior engineer):**
2PC is a CP protocol (CAP theorem): prefers
Consistency over Availability. During network
partition: participants in PREPARED state cannot
proceed (waiting for coordinator = unavailable).
For high-availability distributed systems: AP
(available, eventually consistent) is preferred.
Saga + Outbox Pattern: achieves AP with eventual
consistency. 2PC: use only for tightly coupled,
low-latency resource managers in same availability
zone where network partition probability is very low.

**Level 5 - Mastery (principal engineer):**
Presumptuous Abort (2PC optimization): coordinator
presumes ABORT until explicitly logging COMMIT
intent. If crash recovery finds no log: abort.
Reduces recovery time. 3PC (Three-Phase Commit):
adds a pre-commit phase to reduce in-doubt window;
never widely adopted (more complex, slower, still
blocks on network partition). Paxos/Raft (distributed
consensus): fundamentally different - leader election
vs coordinator lock; tolerates failures without
blocking; used in distributed databases (CockroachDB,
TiDB). Modern choice: distributed databases with
Raft internally + Saga between services.

---

### ⚙️ How It Works (Mechanism)

```java
// 2PC WITH JTA IN SPRING (within a single service)
// Works when both DBs are in same data center
// Requires XA-capable JDBC drivers

@Configuration
public class XaTransactionConfig {

    @Bean
    @Primary
    public XADataSource ordersXaDataSource() {
        PGXADataSource ds = new PGXADataSource();
        ds.setServerName("orders-db");
        ds.setDatabaseName("orders");
        return ds;
    }

    @Bean
    public XADataSource inventoryXaDataSource() {
        PGXADataSource ds = new PGXADataSource();
        ds.setServerName("inventory-db");
        ds.setDatabaseName("inventory");
        return ds;
    }

    @Bean
    public JtaTransactionManager transactionManager() {
        // Atomikos: coordinates XA transactions
        return new JtaTransactionManager();
    }
}

@Service
public class OrderPlacementService {

    @Transactional  // JTA: coordinates both DBs
    public void placeOrder(Order order) {
        // Both writes in same XA transaction
        orderRepo.save(order);           // orders-db
        inventoryRepo.reserve(           // inventory-db
            order.getProductId(), 1);
        // If either fails: both roll back (XA guarantee)
        // Transaction Manager: Phase 1 PREPARE both,
        //   Phase 2 COMMIT both (or ROLLBACK both)
    }
}
// LIMITATION: Kafka cannot participate in XA
// Cannot atomically write to DB + publish to Kafka
// For that: use Outbox Pattern
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
2PC FLOW:

T=0: Coordinator begins distributed transaction

T=1: Phase 1 - PREPARE
     Coordinator -> orders-db: PREPARE TXN-001
     Coordinator -> inventory-db: PREPARE TXN-001
     
     orders-db: writes pending changes to WAL
                acquires row locks
                responds PREPARED
                
     inventory-db: writes pending changes to WAL
                   acquires row locks
                   responds PREPARED

T=2: Both PREPARED
     Coordinator: writes COMMIT TXN-001 to own log
     
T=3: Phase 2 - COMMIT
     Coordinator -> orders-db: COMMIT TXN-001
     Coordinator -> inventory-db: COMMIT TXN-001
     
     Both: commit changes, release locks
     
T=4: DONE - atomically committed

FAILURE AT T=2 (between log write and COMMIT send):
     Coordinator: crashes
     Both DBs: in PREPARED state, locks held
     Recovery: coordinator restarts
               reads log: COMMIT TXN-001 logged
               resends COMMIT to both DBs
               COMMITTED successfully
               In-doubt window: coordinator restart time
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: why 2PC fails with Kafka**

```java
// BAD: trying to use @Transactional for DB + Kafka
// Kafka does not support XA; not truly atomic
@Transactional  // JTA - but Kafka NOT in XA group!
public void createOrder(Order order) {
    orderRepo.save(order);   // In XA transaction
    kafkaTemplate.send(      // NOT in XA transaction!
        "orders", new OrderCreatedEvent(order));
    // If DB rolls back: Kafka message already sent
    // Cannot rollback Kafka publish in XA transaction
    // False sense of atomicity
}
```

```java
// GOOD: Outbox Pattern for DB + Kafka atomicity
@Transactional  // JTA or local - both in SAME tx
public void createOrder(Order order) {
    orderRepo.save(order);     // Business data
    outboxRepo.save(           // Outbox (same DB)
        OutboxEvent.from(order));
    // Relay (Debezium/polling) publishes outbox
    // to Kafka asynchronously with retry
    // Atomicity: local DB transaction
    // Kafka delivery: eventually guaranteed via relay
}
```

---

### ⚖️ Comparison Table

| Aspect | 2PC | Saga Pattern |
|---|---|---|
| **Consistency** | Immediate (all or nothing) | Eventual |
| **Blocking** | Yes (on coordinator failure) | No |
| **Kafka support** | No (XA not supported) | Yes (events) |
| **Cross-service** | Impractical | Designed for it |
| **Failure handling** | Automatic rollback | Compensating transactions |
| **Performance** | Low (locks held during prepare) | High (no cross-service locks) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 2PC guarantees no data loss | 2PC guarantees atomicity (all or nothing) but the coordinator's log IS the single point of durability. If the coordinator's log is corrupted or lost: in-doubt transactions cannot be resolved. Coordinator must use durable, replicated storage for its log. |
| Saga is always better than 2PC | For resources that support XA within a single availability zone (two databases in the same service, both XA-capable, low latency): 2PC may be simpler than Saga. Saga has its own complexity: compensating transactions, idempotency requirements, partial failure visibility. Match the tool to the context. |
| @Transactional in Spring includes Kafka | Spring's `@Transactional` with a standard `DataSource` only spans the JDBC connection. Kafka sends are NOT part of the database transaction. Adding JTA does not change this: Kafka's `KafkaTemplate` does not register as an XA resource. The only correct approach for atomic DB + Kafka: Outbox Pattern. |

---

### 🚨 Failure Modes & Diagnosis

**In-doubt transactions blocking for 5 minutes**

**Symptom:**
Aftter a JTA transaction coordinator crash: some
database connections are hung. Transactions neither
commit nor rollback. After 5 minutes: connection
pool exhausted; application serving 503s.

**Root Cause:**
Coordinator crashed after writing COMMIT to its log
but before all participants acknowledged. Participants:
in PREPARED state. After coordinator restart: recovery
process must send COMMIT to pending participants.
If recovery takes 5 minutes (startup time, log scan):
participants hold locks for 5 minutes.

**Diagnostic:**
```sql
-- Check PostgreSQL in-doubt XA transactions
SELECT gid, prepared, owner, database
FROM pg_prepared_xacts;
-- gid: global transaction ID
-- prepared: when the PREPARE was received
-- If here > 30 seconds: coordinator likely down

-- Manual rollback if coordinator cannot recover:
ROLLBACK PREPARED 'TXN-001';
-- Only do this if coordinator confirms ABORT
-- Never manually commit/rollback without coordinator
```

**Prevention:**
Use managed JTA providers (Bitronix, Atomikos) with
configured transaction timeout (e.g., 30 seconds).
Automatic rollback if coordinator doesn't complete
Phase 2 within timeout. For microservices: prefer
Saga Pattern; avoid 2PC across services entirely.

---

### 🔗 Related Keywords

**The problem 2PC solves:**
- `Distributed Transaction` - 2PC is the classic
  mechanism for distributed ACID transactions

**The alternative:**
- `Saga Pattern` - event-driven alternative to 2PC;
  eventual consistency instead of immediate
- `Compensating Transaction` - the undo mechanism
  that Saga uses instead of 2PC rollback

**Related reliability patterns:**
- `Outbox Pattern` - solves DB + Kafka atomicity
  without 2PC
- `Idempotency in Microservices` - required since
  Saga delivers at-least-once

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PROTOCOL     │ Phase 1: PREPARE (all must say YES)      │
│              │ Phase 2: COMMIT (or ROLLBACK if any NO)  │
├──────────────┼──────────────────────────────────────────┤
│ WEAKNESS     │ Blocking: coordinator crash = participant│
│              │ locked until recovery. Low availability. │
├──────────────┼──────────────────────────────────────────┤
│ MS REPLACE   │ Saga Pattern (eventual, non-blocking)    │
│              │ Outbox Pattern for DB+Kafka atomicity    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Prepare-all then Commit-all; blocking;  │
│              │  Kafka can't XA; use Saga instead"       │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. 2PC = two phases: PREPARE (all agree), COMMIT
   (all execute). Atomic across multiple resources.
2. Blocking weakness: if coordinator fails after
   PREPARE: all participants locked until recovery.
3. In microservices: 2PC impractical (Kafka no XA;
   cross-service locks unacceptable). Use Saga Pattern.

**Interview one-liner:**
"Two-Phase Commit: distributed atomic commit protocol.
Phase 1 (Prepare): coordinator asks all participants
to vote YES/NO. Phase 2 (Commit/Rollback): if all
voted YES, commit all; otherwise rollback all. Guarantees
atomicity across multiple databases. Weakness: blocking
protocol - if coordinator fails between phases,
participants hold locks indefinitely. In microservices:
Kafka doesn't support XA; cross-service 2PC creates
availability problems. Alternative: Saga Pattern
(eventual consistency, non-blocking) + Outbox
Pattern for atomic DB + Kafka write."

---

### 💡 The Surprising Truth

2PC's critical problem is rarely the prepare or
commit phases - it's the coordinator's log. The
coordinator must write its decision (COMMIT or ABORT)
to durable storage BEFORE sending Phase 2 messages.
This log is the single source of truth for in-doubt
transaction recovery. If the coordinator uses a
non-durable log (in-memory, NFS without fsync):
corruption or loss of the log = permanent in-doubt
transactions that can never be resolved automatically.
The participants are stuck FOREVER. Real production
incidents with "stuck transactions that require
DBA manual intervention" are almost always caused
by coordinator log corruption or loss. The humble
log file is the most critical component in 2PC.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **PROTOCOL** Walk through the 2PC protocol for
   a 3-participant transaction. Show: the sequence
   of messages, lock acquisition, log writes. What
   happens if participant 2 of 3 fails to respond
   to PREPARE?
2. **FAILURE** Coordinator crashes between writing
   COMMIT to its log and sending COMMIT to participants.
   What state are participants in? What does recovery
   look like? How long do participants wait?
3. **MICROSERVICES** A team proposes using JTA 2PC
   across order-service and inventory-service (both
   PostgreSQL XA). Counter the proposal: list 3
   specific reasons 2PC is inappropriate across
   services and propose the correct alternative.
4. **KAFKA** Explain why `@Transactional` does not
   make Kafka publishes part of the 2PC transaction.
   What would need to be true for Kafka to participate
   in XA? (It does not support this today.)
5. **JTA** Configure Spring Boot with Atomikos JTA
   for two XADataSources. When is this valid? Give
   a specific architectural context where 2PC with
   JTA is appropriate.

---

### 🧠 Think About This Before We Continue

**Q1.** Your company uses Oracle RAC with XA for
a critical financial system. You are migrating to
microservices. The financial team insists on ACID
atomicity across payment-service and account-service
(both PostgreSQL). Design the migration strategy:
when can you keep 2PC, when do you need Saga, and
how do you handle the transition period?

**Q2.** Distributed databases (CockroachDB, Google
Spanner) provide distributed ACID transactions without
exposing the 2PC protocol to the application. How
do they achieve this? What consistency model do
they use internally? Are they suitable for
microservices cross-service transactions?

**Q3.** A colleague says: "We can solve the 2PC
blocker problem by using 3PC (Three-Phase Commit)
which adds a pre-commit phase." Research 3PC.
Does it truly eliminate blocking? What new problems
does it introduce? Is 3PC used in production systems?