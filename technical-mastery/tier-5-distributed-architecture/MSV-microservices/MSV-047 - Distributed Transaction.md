---
id: MSV-047
title: Distributed Transaction
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-046, MSV-056
used_by: MSV-046
related: MSV-046, MSV-056, MSV-049, MSV-057, MSV-058
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
nav_order: 47
permalink: /technical-mastery/microservices/distributed-transaction/
---

⚡ TL;DR - A Distributed Transaction spans multiple
databases or services that must be updated atomically.
In microservices, each service owns its own database,
making traditional distributed transactions (2PC)
problematic: blocking, not supported by many datastores
(Kafka, MongoDB, DynamoDB), and creates tight coupling.
The recommended alternative: Saga Pattern (eventual
consistency) for most use cases. True distributed
transactions are avoided in microservices; instead,
business operations are designed to tolerate eventual
consistency, or Saga coordinates compensating transactions.

| #047 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Saga Pattern, Two-Phase Commit | |
| **Used by:** | Saga Pattern | |
| **Related:** | Saga Pattern, Two-Phase Commit, Eventual Consistency in Microservices, Compensating Transaction, Idempotency in Microservices | |

---

### 🔥 The Problem This Solves

In a monolith: `@Transactional` - one database, one
transaction, ACID guarantee. In microservices: order-service
has its own DB; payment-service has its own DB. A
single business operation (place order + charge payment)
spans two databases. How do you ensure both succeed
or both fail? This is the distributed transaction
problem. No single `@Transactional` annotation spans
multiple databases.

---

### 📘 Textbook Definition

**Distributed Transaction** is a transaction that spans
multiple resource managers (databases, message queues,
externalservices). For all participants to commit or
roll back atomically, a coordination protocol is needed.
Classical approach: Two-Phase Commit (2PC) protocol
with a transaction coordinator. Problems in microservices:
(1) Many modern datastores don't support 2PC (Kafka,
Mongo, DynamoDB, Redis). (2) Blocking: coordinator
locks all participants during prepare phase. (3) Coupling:
all services must join the same distributed transaction
manager. Alternatives for microservices: Saga Pattern
(eventual consistency), Outbox Pattern (local atomic
write + event), or accepting temporary inconsistency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed transaction = atomic update across multiple
databases. In microservices: avoided using Saga (eventual
consistency) because 2PC is impractical.

**One analogy:**
> Two-Phase Commit is like two people agreeing to
> swap items. Phase 1 (Prepare): both say "I'm ready
to give up my item" (but don't yet). Phase 2 (Commit):
both simultaneously make the swap. If either person
can't show up for phase 2: the swap is cancelled
(rollback). The coordinator facilitates. Problem: both
persons are "locked" (holding items) until the
coordinator gives the go-ahead. If coordinator crashes:
both are blocked indefinitely.

**One insight:**
The reason distributed transactions are avoided in
microservices is not that they're impossible - it's
that they violate service autonomy. A distributed
transaction requires all participants to be available
and reachable simultaneously. In a microservices
architecture designed for independent deployment and
failure isolation: this violates the core principle.
Saga trades ACID for eventual consistency and maintains
service autonomy.

---

### 🔩 First Principles Explanation

**TWO-PHASE COMMIT (2PC) DEEP DIVE:**

```
ACTORS:
  Transaction Coordinator (TC): the driver
  Participants: all services/DBs in the transaction

PHASE 1 - PREPARE:
  TC -> each Participant: "prepare to commit"
  Participant: write to undo log, acquire locks,
               respond READY or ABORT
  ALL participants READY: -> Phase 2
  ANY participant ABORT: -> Phase 2 (ROLLBACK)

PHASE 2 - COMMIT or ROLLBACK:
  If all READY: TC -> each Participant: "commit"
  If any ABORT: TC -> each Participant: "rollback"
  Participants: complete the action

PROBLEM 1 - COORDINATOR FAILURE:
  Phase 1 complete: all participants sent READY
  TC crashes before sending commit
  Participants: waiting indefinitely (locks held!)
  Resolution: requires TC recovery, timeout mechanism
  OR: new coordinator queries participant logs
  
PROBLEM 2 - PARTICIPANT FAILURE (during phase 2):
  TC sent commit; Participant A committed
  Participant B crashes before commit
  On recovery: B checks its log, finds prepared state
  Queries TC for decision; commits if TC says commit
  This works if TC is durable (logged its decision)

PROBLEM 3 - NETWORK PARTITION:
  Coordinator <-> Participant: network fails after PREPARE
  Participant: holds locks, can't get commit decision
  Locks block other transactions indefinitely
```

**WHY MICROSERVICES AVOID 2PC:**

```
1. DATASTORE INCOMPATIBILITY:
   Kafka does not support 2PC
   DynamoDB does not support 2PC
   Redis (without transactions) does not support 2PC
   Most NoSQL stores: no XA protocol support

2. COUPLING:
   All services must use the same transaction manager
   (Atomikos, Narayana for JTA)
   Microservices: different tech stacks, different DBs
   One transaction manager managing all: tight coupling

3. AVAILABILITY vs CONSISTENCY:
   CAP theorem: during network partition, 2PC prefers
   consistency (blocks rather than proceeding)
   Microservices: prefer availability (eventual
     consistency)

4. PERFORMANCE:
   2PC adds coordinator round trip to every transaction
   At 1000 TPS: coordinator is a bottleneck
   At 10,000 TPS: 2PC coordinator is unscalable
```

---

### 🧪 Thought Experiment

**WHEN DISTRIBUTED TRANSACTION IS ACTUALLY NEEDED:**

```
SCENARIO: Banking transfer (strict ACID required)
  Debit account A by $100
  Credit account B by $100
  Both must be atomic: no partial state (money lost)

  OPTION A: Both accounts in same DB
    @Transactional: atomic. Done.
    But: separate microservices with separate DBs...

  OPTION B: Saga (eventual consistency)
    Step 1: Debit A
    Step 2: Credit B
    If step 2 fails: compensate (credit A back)
    Risk: brief window where A is debited but B not
    credited. For banking: this is acceptable if
    compensated correctly and idempotently.
    Most banking: ACTUALLY uses eventual consistency
    with careful reconciliation.

  OPTION C: 2PC between account-service DBs
    Requires: both DBs support XA
    Both on same network at all times
    Coordinator never fails
    Result: ACID, but blocking, fragile
    Decision: for internal bank DBs with strict
    requirements and homogeneous stack: valid.
    For microservices with heterogeneous stack: use Saga.
```

---

### 🧠 Mental Model / Analogy

> Distributed Transaction (2PC) is like a marriage
> ceremony requiring BOTH parties to say "I do"
> simultaneously (the coordinator is the officiant).
> If either person has cold feet (ABORT): the ceremony
> doesn't happen. If the officiant has a heart attack
> after both said "I do" but before declaring them
> married: both people are "locked" in a limbo state
> (holding hands, can't commit or abort). Saga is like
> a series of signed contracts: first one signs,
> then the other. If the second refuses: first tears
> up their contract (compensation). No "limbo state";
> each step is a committed local action.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Distributed transaction: update multiple databases
from different services at once. Hard in microservices
because each service has its own database and they
don't share a transaction system.

**Level 2 - How to use it (junior developer):**
In microservices: avoid distributed transactions.
Use Saga Pattern instead. If you MUST have a distributed
transaction (same tech stack, same DB type, XA support):
use JTA with Atomikos/Narayana in Spring Boot. But
first ask: can I redesign the business operation to
use eventual consistency?

**Level 3 - How it works (mid-level engineer):**
2PC with JTA: `@Transactional(transactionManager="jtaTransactionManager")`.
JTA coordinator manages the prepare/commit phases
across XA-compliant resources. Problem: Kafka is not
XA. If your Saga needs to write to DB AND publish
to Kafka atomically: use Outbox Pattern (write to
outbox table in same DB transaction; relay publishes
to Kafka separately).

**Level 4 - Why it was designed this way (senior/staff):**
The key insight: strict consistency and availability
are in tension (CAP theorem). Banking traditionally
preferred consistency (strong ACID, 2PC). Internet-scale
systems (Amazon, Netflix) discovered that availability
better serves user experience. Amazon's Dynamo paper
(2007) formalized eventual consistency for distributed
systems. Microservices inherit this philosophy: design
business operations to tolerate temporary inconsistency,
with reconciliation to resolve conflicts.

**Level 5 - Mastery (distinguished engineer):**
Modern distributed databases (Google Spanner,
CockroachDB) provide globally-distributed ACID
transactions using different mechanisms: TrueTime
(Spanner) - use GPS/atomic clocks for timestamp
ordering, making global consistency possible without
2PC's blocking. CockroachDB: MVCC + consensus-based
commit. These are NOT 2PC; they achieve consistency
differently. For truly global consistency requirements:
Spanner or CockroachDB within a single service (one
DB, multiple regions) is preferred over 2PC across
services.

---

### ⚙️ How It Works (Mechanism)

**OUTBOX PATTERN: ATOMIC LOCAL TX + EVENT:**

```java
// Atomic: DB write + outbox event in one local transaction
@Service
@Transactional
public class OrderService {

    public Order createOrder(OrderRequest req) {
        // Write order to orders table
        Order order = orderRepo.save(new Order(req));

        // Write event to outbox table (SAME transaction)
        // If transaction commits: both saved atomically
        // If transaction fails: neither saved
        outboxRepo.save(new OutboxEvent(
            "OrderCreated",
            order.getId(),
            objectMapper.writeValueAsString(
                new OrderCreatedEvent(order))
        ));

        return order;
        // Outbox relay: separate process reads outbox
        // and publishes to Kafka
    }
}

// OutboxRelay: CDC (Debezium) or polling relay
// Reads outbox table; publishes to Kafka
// Marks events as published
// At-least-once delivery; consumers must be idempotent
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
MICROSERVICES APPROACH: No 2PC

ORDER CREATION (eventual consistency):
  1. order-service: local TX - create order + outbox event
     Outbox: {OrderCreated, orderId=123, payload=...}
  
  2. Debezium CDC: reads outbox table change
     Publishes OrderCreated to Kafka topic
  
  3. payment-service: consumes OrderCreated
     Local TX: create payment record (PENDING)
               + outbox {PaymentCreated, sagaId=xxx}
  
  4. Continue until all services have processed
  
CONSISTENCY WINDOW:
  T=0: Order created (status=PENDING)
  T=50ms: Payment processing
  T=100ms: Inventory reserved
  T=200ms: Order status=CONFIRMED
  
  During T=0 to T=200ms: partial state is visible
  Design: order status = PENDING until saga completes
  Users: see PENDING order (not CONFIRMED until done)
  This is eventual consistency with explicit status.
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: 2PC attempt**

```java
// BAD: Attempting 2PC across microservice DBs
// This is what 2PC in microservices looks like:
@Transactional(transactionManager = "jtaTransactionManager")
public void placeOrder(OrderRequest req) {
    // Two DBs: order-service DB and payment-service DB
    // Both enrolled in JTA transaction
    // Problems: tight coupling, Kafka excluded,
    // blocking, not supported by cloud-managed DBs
    orderRepository.save(order);
    paymentRepository.save(payment); // Different DB!
    // If payment DB times out: order DB locks held
}
```

```java
// GOOD: Eventual consistency with Outbox + Saga
@Transactional  // Local transaction only
public Order createOrder(OrderRequest req) {
    // Single DB: order-service DB
    Order order = orderRepository.save(
        Order.pending(req));

    // Outbox: same local transaction = atomic
    outboxRepository.save(
        OutboxEvent.orderCreated(order.getId(), req));

    // Return PENDING order to client
    // Payment will happen asynchronously via Saga
    // Order status updated to CONFIRMED when Saga completes
    return order;  // status=PENDING
}
// Outcome: no distributed lock, no 2PC
// Eventual consistency: order confirmed in ~200ms
// Failure: Saga compensates automatically
```

---

### ⚖️ Comparison Table

| Approach | Consistency | Availability | Datastore Support | Complexity |
|---|---|---|---|---|
| **2PC** | Strong ACID | Low (blocking) | XA datastores only | High infra |
| **Saga** | Eventual | High | Any datastore | Medium code |
| **Outbox + Saga** | Eventual + reliable delivery | High | Any datastore | Medium code |
| **Single DB** | Strong ACID | High | One DB per service | Low |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 2PC is always wrong in microservices | 2PC is impractical for most microservice scenarios (polyglot stores, availability requirements). For a small number of same-technology, same-infrastructure services with strict consistency requirements: 2PC via JTA is a valid engineering trade-off. Know the trade-offs; don't dogmatically reject it. |
| Eventual consistency means data is wrong temporarily | Eventual consistency means data is eventually CORRECT after a short window. It's not "sometimes wrong" - it's "right after a brief delay". Design for this: don't read-your-own-write immediately after a write; use order status PENDING until confirmed; show "processing" indicators to users. |
| Saga and distributed transaction are the same | No. A distributed transaction (2PC) guarantees atomic commit across all participants. A Saga executes local transactions sequentially; partial states exist; compensation handles failure. Saga achieves eventual consistency. 2PC achieves strong consistency. Very different consistency models. |

---

### 🚨 Failure Modes & Diagnosis

**JTA 2PC coordinator failure: blocked transactions**

**Symptom:**
All database connections are "waiting for lock". The
JTA transaction coordinator (Atomikos) was restarted.
Transactions from before the restart are blocking:
they are in PREPARED state (phase 1 complete, waiting
for phase 2 commit decision). The coordinator doesn't
know it already sent COMMIT to Participant A. On
recovery: it queries participants for in-doubt
transactions. But if the coordinator log was lost:
transactions are permanently blocked.

**Root Cause:**
Atomikos transaction log stored in memory (not durable)
or on ephemeral pod storage. On coordinator restart:
log is empty; in-doubt transactions are not recovered.

**Diagnostic:**
```bash
# Check for in-doubt transactions (PostgreSQL)
SELECT * FROM pg_prepared_xacts;
# Shows prepared transactions waiting for commit/rollback

# Atomikos log location
ls /var/lib/atomikos/
# Should have .log files for recovery
# If empty: coordinator log was lost

# Manually commit or rollback in-doubt transactions
-- PostgreSQL: commit the prepared transaction
COMMIT PREPARED 'your-prepared-xid';
-- or rollback
ROLLBACK PREPARED 'your-prepared-xid';
```

**Fix:**
1. Use durable coordinator log (persistent volume,
   not ephemeral pod storage).
2. Better: migrate from 2PC to Saga + Outbox.
   Avoid JTA coordinator entirely.
3. Monitoring: alert on `pg_prepared_xacts` count > 0
   for more than 30 seconds.

---

### 🔗 Related Keywords

**Solutions to the distributed transaction problem:**
- `Saga Pattern` - the recommended microservices
  approach; eventual consistency via local transactions
- `Two-Phase Commit` - the classical distributed
  transaction protocol (avoid in microservices)

**Related patterns:**
- `Eventual Consistency in Microservices` - the
  consistency model that replaces 2PC
- `Compensating Transaction` - the mechanism for
  rollback in Saga
- `Idempotency in Microservices` - required for Saga
  step retry safety

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PROBLEM      │ Atomic update across multiple DBs/service│
│ 2PC          │ Classic solution; blocking; avoid in MSV │
│ SAGA         │ Recommended; eventual consistency        │
│ OUTBOX       │ Atomic local TX + event publish          │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "2PC is avoided; use Saga for distributed│
│              │  transactions across microservices"      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Distributed transaction in microservices: avoid 2PC
   because it's blocking, not supported by most
   datastores (Kafka, DynamoDB), and violates service
   autonomy.
2. Recommended alternative: Saga Pattern (eventual
   consistency) + Outbox Pattern (atomic local write
   + event).
3. When consistency is non-negotiable: consider a
   single service with one database or use Google
   Spanner/CockroachDB for distributed ACID within
   the same service.

**Interview one-liner:**
"Distributed transactions across microservices should
avoid 2PC: blocking, most datastores (Kafka, DynamoDB)
don't support XA, and it couples all participants to
one transaction manager. Alternative: Saga Pattern for
eventual consistency with compensating transactions,
and Outbox Pattern for atomic DB write + event publish
within one local transaction. 2PC is acceptable for
small, same-tech-stack, strict-consistency scenarios
but is the exception, not the rule, in microservices."

---

### 💡 The Surprising Truth

The most surprising fact about distributed transactions:
Strict ACID consistency is not actually required for
most business operations that seem to require it.
Example: "Charge customer and create order must be
atomic." Reality: e-commerce giants (Amazon, Shopify)
use eventual consistency for orders. The order is
created in PENDING state. Payment is processed
asynchronously. If payment fails: order is cancelled
(compensating transaction). Customers see: "Order
received, payment processing." The strict ACID
requirement was an engineering assumption, not a
business requirement. Questioning the requirement
before engineering the solution often reveals that
eventual consistency with good UX is acceptable.
This redesign eliminates the distributed transaction
problem entirely.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** The two phases of 2PC, what happens
   when the coordinator fails between phases, and
   why this creates blocking.
2. **IDENTIFY** Given a microservices design with
   a proposed distributed transaction: identify the
   datastores involved, determine if 2PC is feasible,
   and propose an eventual consistency alternative.
3. **OUTBOX** Design the Outbox Pattern for a service
   that needs to write to DB and publish to Kafka
   atomically. Explain what guarantees it provides.
4. **SPANNER** Explain how Google Spanner achieves
   global ACID without 2PC. Why doesn't it suffer
   the same blocking problem?
5. **TRADE-OFF** For a specific business scenario
   (banking transfer), evaluate: when is eventual
   consistency acceptable? When is strict ACID
   required? Who makes this decision (engineering
   or business)?

---

### 🧠 Think About This Before We Continue

**Q1.** A fintech company needs to transfer money
between two accounts. Both accounts are in the same
database (PostgreSQL). They are proposing to use
2PC with JTA because they're splitting into microservices.
Is 2PC necessary here? What would you recommend?

**Q2.** Your Saga has 4 steps: create order, charge
payment, reserve inventory, create shipment. The
Outbox Pattern is used for steps 1, 2, and 3. Step
4 (create shipment) calls a third-party logistics
API (no Outbox possible). The logistics API call
succeeds but the network times out on the response.
The Saga doesn't know if shipment was created. How
do you handle this ambiguity? What pattern applies?

**Q3.** Your service is running on Kubernetes with
epochemeral storage. You chose Atomikos JTA for distributed
transactions. After a pod restart due to OOM kill:
you find 15 in-doubt transactions blocking your database.
How did this happen? What is the permanent fix?
How do you resolve the current blocked transactions?