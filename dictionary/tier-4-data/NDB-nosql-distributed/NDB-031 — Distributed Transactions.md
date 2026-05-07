---
layout: default
title: "Distributed Transactions"
parent: "NoSQL & Distributed Databases"
nav_order: 31
permalink: /nosql/distributed-transactions/
number: "NDB-031"
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: ACID, CAP Theorem (DB), Database Sharding
used_by: Two-Phase Commit (2PC), Saga Pattern (DB), System Design
related: Two-Phase Commit (2PC), Saga Pattern (DB), ACID
tags:
  - nosql
  - distributed-transactions
  - acid
  - deep-dive
---

# NDB-031 — Distributed Transactions

⚡ TL;DR — A distributed transaction coordinates atomic ACID operations across multiple independent databases or services; the main approaches are **Two-Phase Commit (2PC)** (strongly consistent but blocking) and the **Saga Pattern** (eventually consistent but non-blocking); choosing between them is a choice of consistency guarantee vs. failure resilience.

| #470            | Category: NoSQL & Distributed Databases                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | ACID, CAP Theorem (DB), Database Sharding                |                 |
| **Used by:**    | Two-Phase Commit (2PC), Saga Pattern (DB), System Design |                 |
| **Related:**    | Two-Phase Commit (2PC), Saga Pattern (DB), ACID          |                 |

---

### 🔥 The Problem This Solves

**MULTI-SERVICE ATOMIC OPERATIONS:**
Modern applications spread operations across multiple databases and services: deduct from Account A (PostgreSQL), credit to Account B (another PostgreSQL, different bank), update ledger (DynamoDB), send notification (email service). In a single database with one ACID transaction, this would be trivially atomic. Across independent systems: if step 3 fails after steps 1 and 2 succeed, you have deducted money from A and credited B, but the ledger is incomplete. The application has inconsistent state with no automatic rollback mechanism.

**DISTRIBUTED TRANSACTIONS:**
The solution space: 2PC (coordinate via a transaction manager that drives a two-phase protocol) or Saga (sequence of local transactions + compensating transactions for rollback). Neither is free: 2PC adds network round trips and is blocking (participants hold locks). Saga provides eventual consistency but requires designing compensating transactions for every step. Understanding when to use each is a core distributed systems design skill.

---

### 📘 Textbook Definition

A **distributed transaction** is a transaction that spans multiple independent data stores or services, ensuring that all operations either commit together (atomicity) or all roll back. **XA Transactions**: the industry standard protocol (X/Open DTP standard, implemented by most relational databases). A **Transaction Manager (TM)** coordinates multiple **Resource Managers (RMs)** via the **Two-Phase Commit (2PC)** protocol. **Phase 1 (Prepare)**: TM asks all RMs to prepare (lock resources, write to redo log, respond YES/NO). **Phase 2 (Commit/Abort)**: if all YES → TM sends COMMIT to all RMs; if any NO → TM sends ROLLBACK to all. **Problems with 2PC**: blocking (if TM crashes between phases, RMs wait indefinitely), lock contention (RMs hold locks during both phases), coordinator single point of failure. **Saga Pattern**: alternative for microservices — a sequence of local ACID transactions, where each step publishes an event (choreography) or is orchestrated by a coordinator. Failure triggers compensating transactions (compensations are application-defined, inverse operations). Sagas provide **eventual consistency** (not ACID atomicity) but are non-blocking and fault-tolerant.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed transactions coordinate "commit or all rollback" across multiple independent databases — either by lock-based consensus (2PC, strongly consistent) or by compensating transactions (Saga, eventually consistent).

**One analogy:**

> Planning a multi-city surprise party. 2PC: call all venues simultaneously, ask "are you available?" — all say yes → book all; any says no → cancel all; if your phone dies after half say yes (coordinator crash), venues are stuck on hold. Saga: book venue 1 → book venue 2 → book venue 3; if venue 3 is unavailable, call venues 1 and 2 to cancel (compensating transactions); no one is stuck waiting.

- "All venues say yes → book all" → 2PC Phase 1 (prepare) + Phase 2 (commit)
- "Phone dies mid-booking" → TM crash (2PC blocking problem)
- "Venues stuck on hold" → participants locked waiting for TM decision
- "Book sequentially, cancel if needed" → Saga pattern (local transactions + compensations)
- "No one stuck waiting" → Saga is non-blocking

**One insight:**
2PC guarantees ACID-level atomicity but introduces a blocking window (the window between Phase 1 responses and Phase 2 decision). During this window, any participant crash → other participants are blocked (hold locks) until recovery. This is the **blocking problem** of 2PC, and it's the primary reason microservice architectures prefer Saga patterns instead. Saga sacrifices atomic isolation (intermediate states are visible) for non-blocking, fault-tolerant operation.

---

### 🔩 First Principles Explanation

**2PC PROTOCOL — STEP BY STEP:**

```
Scenario: transfer $100 from Account A (Bank1 DB) to Account B (Bank2 DB)
Participants: TM (Transaction Manager), RM_A (Bank1 DB), RM_B (Bank2 DB)

[PHASE 1: PREPARE]
TM → RM_A: "PREPARE transaction T1: deduct $100 from Account A"
  RM_A: validates (balance >= 100), writes prepare record to redo log
  RM_A: acquires EXCLUSIVE LOCK on Account A row
  RM_A → TM: "YES (prepared)" or "NO (insufficient funds)"

TM → RM_B: "PREPARE transaction T1: credit $100 to Account B"
  RM_B: validates (account exists), writes prepare record to redo log
  RM_B: acquires EXCLUSIVE LOCK on Account B row
  RM_B → TM: "YES (prepared)"

[TM DECISION POINT]
All YES → proceed to Phase 2 COMMIT
Any NO → proceed to Phase 2 ABORT
TM writes commit decision to durable log (before sending to RMs)

[PHASE 2: COMMIT]
TM → RM_A: "COMMIT T1"
  RM_A: applies deduction, releases lock, writes commit record
TM → RM_B: "COMMIT T1"
  RM_B: applies credit, releases lock, writes commit record

Transaction complete. Both Account A (deducted) and Account B (credited) ✓

[THE BLOCKING PROBLEM]
What if TM crashes after Phase 1 but before Phase 2?
  RM_A: prepared, holding lock on Account A — cannot proceed or rollback
  RM_B: prepared, holding lock on Account B — cannot proceed or rollback
  Duration: until TM recovers (minutes, hours, or indefinitely)
  Impact: Account A and Account B are LOCKED, inaccessible
  Other transactions trying to read/write Account A: blocked

3PC (Three-Phase Commit) attempts to solve this:
  Adds a "pre-commit" phase to allow non-blocking recovery
  But: introduces more complexity, longer round trips
  Rarely used in practice (2PC + recovery tools is more common)
```

**XA TRANSACTIONS IN JAVA (SPRING + JTA):**

```java
// XA transactions: Java Transaction API (JTA)
// Transaction Manager: Atomikos, Bitronix, or Java EE container
// Resource Managers: DataSource implementing XADataSource

@Configuration
public class XADataSourceConfig {
    @Bean
    @Primary
    public DataSource primaryXaDataSource() {
        PGXADataSource xaDataSource = new PGXADataSource();
        xaDataSource.setUrl("jdbc:postgresql://bank1-db/accounts");
        // ...
        AtomikosDataSourceBean atomikos = new AtomikosDataSourceBean();
        atomikos.setXaDataSource(xaDataSource);
        atomikos.setUniqueResourceName("bank1-db");
        return atomikos;
    }

    @Bean
    public DataSource secondaryXaDataSource() {
        PGXADataSource xaDataSource = new PGXADataSource();
        xaDataSource.setUrl("jdbc:postgresql://bank2-db/accounts");
        AtomikosDataSourceBean atomikos = new AtomikosDataSourceBean();
        atomikos.setXaDataSource(xaDataSource);
        atomikos.setUniqueResourceName("bank2-db");
        return atomikos;
    }
}

@Service
public class TransferService {
    @Autowired private AccountRepository bank1Accounts;
    @Autowired private AccountRepository bank2Accounts;

    @Transactional  // JTA transaction — spans both DataSources
    public void transfer(String fromId, String toId, BigDecimal amount) {
        Account from = bank1Accounts.findById(fromId).orElseThrow();
        Account to = bank2Accounts.findById(toId).orElseThrow();

        if (from.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException();
        }

        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));

        bank1Accounts.save(from);  // writes to Bank1 DB
        bank2Accounts.save(to);    // writes to Bank2 DB
        // @Transactional: JTA TM coordinates XA 2PC across both databases
        // Either both commit or both rollback
    }
}
```

**SAGA PATTERN (CHOREOGRAPHY):**

```java
// Saga via choreography (event-driven, no central coordinator)
// Step 1: Order Service creates order
@Service
public class OrderService {
    @Transactional  // local ACID transaction
    public Order createOrder(OrderRequest request) {
        Order order = new Order(request);
        order.setStatus(OrderStatus.PENDING_PAYMENT);
        orderRepository.save(order);

        // Outbox event → Kafka (same local transaction)
        outboxRepository.save(new OutboxEvent("OrderCreated", order));
        return order;
    }

    // COMPENSATING TRANSACTION for this step:
    @Transactional
    public void cancelOrder(String orderId, String reason) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.setStatus(OrderStatus.CANCELLED);
        order.setCancellationReason(reason);
        orderRepository.save(order);
        outboxRepository.save(new OutboxEvent("OrderCancelled", order));
    }
}

// Step 2: Payment Service (Kafka consumer for "OrderCreated")
@KafkaListener(topics = "order.created")
public void processPayment(OrderCreatedEvent event) {
    try {
        paymentService.chargeCustomer(event.getCustomerId(), event.getTotal());
        // Publish: "PaymentSucceeded" → triggers inventory step
    } catch (PaymentFailedException e) {
        // Publish: "PaymentFailed" → triggers Order cancellation (compensation)
        eventPublisher.publish(new PaymentFailedEvent(event.getOrderId(), e.getMessage()));
    }
}

// Compensation: Order Service listens for "PaymentFailed"
@KafkaListener(topics = "payment.failed")
public void handlePaymentFailed(PaymentFailedEvent event) {
    orderService.cancelOrder(event.getOrderId(), "Payment failed: " + event.getReason());
}
// Result: OrderCreated → PaymentFailed → OrderCancelled
// Each step: local ACID transaction
// Total: eventually consistent saga (not ACID across services)
// No blocking: each step proceeds asynchronously
```

**SAGA PATTERN (ORCHESTRATION):**

```java
// Saga via orchestration (central saga orchestrator drives the steps)
// Better for: complex workflows, easier to visualize and debug

@Component
public class CreateOrderSagaOrchestrator {

    @Transactional
    public void startSaga(OrderRequest request) {
        SagaState saga = new SagaState("CreateOrder", request);
        sagaRepository.save(saga);

        // Step 1: Reserve inventory
        inventoryService.reserveItems(request.getItems())
            .onSuccess(event -> handleInventoryReserved(saga.getId(), event))
            .onFailure(event -> handleInventoryFailed(saga.getId(), event));
    }

    public void handleInventoryReserved(String sagaId, InventoryReservedEvent event) {
        SagaState saga = sagaRepository.findById(sagaId).orElseThrow();
        saga.setStep("INVENTORY_RESERVED");
        sagaRepository.save(saga);

        // Step 2: Process payment
        paymentService.processPayment(saga.getCustomerId(), saga.getTotal())
            .onSuccess(e -> handlePaymentSuccess(sagaId, e))
            .onFailure(e -> compensateInventory(sagaId, e)); // compensation!
    }

    public void compensateInventory(String sagaId, PaymentFailedEvent e) {
        SagaState saga = sagaRepository.findById(sagaId).orElseThrow();
        saga.setStep("COMPENSATING");
        sagaRepository.save(saga);

        // Compensating transaction: release the reserved inventory
        inventoryService.releaseReservation(saga.getItems());
        orderService.cancelOrder(saga.getOrderId(), "Payment failed");
    }
}
// Orchestration: easier to track saga state, handle retries, visualize flow
// Choreography: lower coupling, harder to track overall saga state
```

---

### 🧪 Thought Experiment

**THE HOTEL + FLIGHT + CAR BOOKING PROBLEM**

Book a vacation: hotel (DB1), flight (DB2), car rental (DB3). All or nothing.

**2PC APPROACH:**
TM asks all 3: "PREPARE booking?"

- Hotel: "YES, room 204 reserved" (lock held)
- Flight: "YES, seat 17B reserved" (lock held)
- Car: "YES, Toyota Camry reserved" (lock held)
- TM: all YES → send COMMIT

Problem: TM server is in a cloud region that goes down between PREPARE and COMMIT.

- Hotel, Flight, Car: all holding locks, waiting for TM decision
- Duration: until TM recovers. Could be 30 minutes.
- Other users can't book room 204, seat 17B, or that Camry
- Recovery: TM restarts, reads log, sends COMMIT → all complete

For a consumer booking site: 30-minute lock on a hotel room and flight seat is unacceptable.

**SAGA APPROACH:**
Step 1: Book hotel → SUCCESS. "HotelBooked" event published.
Step 2: Book flight → SUCCESS. "FlightBooked" event published.
Step 3: Book car → FAILURE (no cars available). "CarBookingFailed" event published.
Compensations triggered:

- "FlightCancelled" compensation: cancel flight booking in DB2
- "HotelCancelled" compensation: cancel hotel booking in DB1
  No locks held: hotel room and flight seat are immediately available to other users after cancellation.

Downside: During step 3 failure and compensation, another user could read "Alice's trip" as partially booked (hotel + flight, but no car). This is "intermediate state visibility" — Saga lacks full ACID isolation.

For this use case: Saga is clearly better. The compensation design is the application's responsibility (cancel hotel, cancel flight if car unavailable).

---

### 🧠 Mental Model / Analogy

> 2PC is like a bank transfer that requires all ATMs in both banks to simultaneously confirm availability before proceeding. Everyone is on hold, keys locked in the safe, until the central coordinator gives the green light. If the coordinator's phone dies, everyone waits. Saga is like buying things with cash: buy the concert ticket (local transaction), buy the parking pass (local transaction), try to buy the merchandise — sold out — refund the parking pass, cancel the concert ticket (compensating transactions). Each purchase is independent; nobody waits for a central coordinator.

- "Central coordinator gives green light" → 2PC Transaction Manager Phase 2 decision
- "Everyone on hold, keys locked" → 2PC participants holding locks during Phase 1
- "Coordinator's phone dies" → TM crash (blocking problem)
- "Buy with cash, independent purchases" → Saga (local transactions)
- "Refund and cancel" → Saga compensating transactions
- "Nobody waits" → Saga is non-blocking

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Distributed transactions ensure that operations across multiple databases either all commit or all rollback. 2PC uses a coordinator to achieve this atomically but is vulnerable to coordinator crashes (blocking). Saga breaks the operation into steps with compensations — no blocking, but intermediate states are visible to other transactions.

**Level 2:** Use 2PC (XA): same organization controls all databases, strong ACID required, short transactions (< 1s), acceptable coordinator risk (with recovery strategy). Use Saga: microservices architecture, different teams/services, long-running transactions, high availability required. Design compensations first: each Saga step must have a reversible compensation before implementation. Use idempotency keys to prevent duplicate compensations.

**Level 3:** Saga failure modes: (a) Lost compensation: compensation event published but consumer is down → DLQ → manual intervention. (b) Non-idempotent compensation: compensation runs twice (Kafka at-least-once) → double-refund. Fix: idempotency keys + CHECK before applying compensation. (c) Partial completion: saga orchestrator crashes mid-saga → use persistent saga state (orchestrator saves step completion to DB); on recovery, resume from last completed step. Choreography vs. Orchestration: Choreography (events, no central coordinator): lower coupling, harder to track overall state. Orchestration (saga coordinator service): easier to monitor, debug, retry failed steps, but introduces a central coordinator (SPF risk). Event Sourcing + Saga: natural fit — events are the source of truth; saga state is derived from events.

**Level 4:** The distributed transactions problem reflects a fundamental impossibility result: FLP Impossibility (Fischer, Lynch, Paterson, 1985) proves that in an asynchronous distributed system, no consensus protocol can guarantee termination in the presence of a single crashed process. 2PC does not guarantee termination (it can block indefinitely on coordinator crash). 3PC improves this but adds complexity. Practical solutions: (a) 2PC with automated TM recovery (Atomikos, Java EE TM): TM logs decisions durably before Phase 2; on crash + recovery, completes Phase 2 — not blocking in practice, but requires recovery time. (b) Saga + compensations: avoids the blocking entirely by design. The microservices movement has largely adopted Saga as the preferred pattern because it aligns with service autonomy (each service owns its data and compensations), while 2PC is appropriate only in monolithic or tightly-coupled database architectures. The interesting frontier: Google Spanner and CockroachDB implement distributed transactions via Percolator/2PC variants at the storage layer — transparent to the application, with the TM replicated via Raft for non-blocking recovery.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ 2PC vs SAGA: FAILURE COMPARISON                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 2PC: Normal case                                     │
│  TM → RM_A: PREPARE → YES                           │
│  TM → RM_B: PREPARE → YES                           │
│  TM → RM_A: COMMIT                                  │
│  TM → RM_B: COMMIT ✓                                │
│                                                      │
│ [DIST TRANSACTIONS ← YOU ARE HERE: 2PC Phase 2]      │
│                                                      │
│ 2PC: TM crash after Phase 1                          │
│  TM → RM_A: PREPARE → YES (RM_A locked)             │
│  TM → RM_B: PREPARE → YES (RM_B locked)             │
│  TM: CRASH ← locks held; RM_A, RM_B blocked         │
│  Recovery: TM restarts → reads log → sends COMMIT   │
│  Blocking duration: TM recovery time                 │
│                                                      │
│ SAGA: Step 2 fails                                   │
│  Step 1: local COMMIT ✓ (RM_A updated)               │
│  Step 2: local COMMIT fails ← compensation triggered │
│  Compensation for Step 1: RM_A compensating write   │
│  No locks held: other transactions proceed normally  │
│  Intermediate state: RM_A was updated, then reverted │
│  Other transactions could have seen RM_A intermediate│
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**E-COMMERCE ORDER (SAGA CHOREOGRAPHY):**

```
User clicks "Place Order"
→ Order Service: creates PENDING order + outbox event (local ACID txn)
→ [DISTRIBUTED TRANSACTIONS ← YOU ARE HERE: Saga begins]
→ Kafka: "OrderCreated"

→ Inventory Service (Kafka consumer):
   Reserve items (local ACID txn)
   If success → Kafka: "InventoryReserved"
   If failure → Kafka: "InventoryReservationFailed"

→ Payment Service (consumer of "InventoryReserved"):
   Charge customer (local ACID txn)
   If success → Kafka: "PaymentSucceeded"
   If failure → Kafka: "PaymentFailed"

→ On "PaymentFailed":
   Inventory Service compensates: release reservation
   Order Service compensates: cancel order
   User sees: "Order could not be processed" (compensation complete)

→ On "PaymentSucceeded":
   Order Service: update status to CONFIRMED
   Email Service: send confirmation
   Fulfillment Service: begin picking

EVENTUAL CONSISTENCY:
  Between "OrderCreated" and "InventoryReserved": order is "PENDING"
  Other users COULD see pending order in admin dashboard (intermediate state)
  Within 2-3 seconds: order reaches terminal state (CONFIRMED or CANCELLED)
```

---

### ⚖️ Comparison Table

| Aspect           | 2PC (XA)                         | Saga (Choreography)                        | Saga (Orchestration)          |
| ---------------- | -------------------------------- | ------------------------------------------ | ----------------------------- |
| Consistency      | ACID atomicity                   | Eventual consistency                       | Eventual consistency          |
| Blocking         | Yes (TM crash = blocked)         | No                                         | No                            |
| Isolation        | Full isolation (locks held)      | No isolation (intermediate states visible) | No isolation                  |
| Failure recovery | TM recovery (automatic)          | DLQ + compensations                        | Saga state + compensations    |
| Coupling         | Tight (TM coordinates all)       | Loose (event-driven)                       | Medium (orchestrator)         |
| Observability    | Difficult (TM is black box)      | Hard (events spread across services)       | Easy (central state)          |
| Use when         | Single-org, ACID-critical, short | Microservices, long-running, HA            | Complex saga, need visibility |

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                                                                                                                               |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Saga is a replacement for ACID transactions"                           | Saga provides eventual consistency, not ACID. Intermediate states are visible; there's no isolation guarantee. For operations that require strict ACID (e.g., financial transfers within one database), use a local ACID transaction — no saga needed |
| "2PC always blocks indefinitely on crash"                               | With durable TM log (Atomikos, Java EE TM): on crash+recovery, the TM reads its log and completes Phase 2. Blocking is bounded by TM recovery time, not indefinite — but recovery time can be significant                                             |
| "Choreography is always better than Orchestration for sagas"            | Choreography has lower coupling but harder observability. For complex multi-step sagas (5+ steps), orchestration is usually operationally superior: you can see the saga's state, retry failed steps, and monitor completion                          |
| "Distributed transactions are only needed for multi-database scenarios" | Distributed transactions are also needed when: multiple microservices must update data atomically, even if they each use the same database type; a service must update a database and publish an event atomically                                     |

---

### 🚨 Failure Modes & Diagnosis

**1. Saga Compensation Failure (Non-Idempotent Compensation)**

**Symptom:** Customer receives two refunds. System logs show: "RefundProcessed" for the same order twice. Customer support reports customers occasionally receive extra money.

**Root Cause:** Kafka consumer processed the `PaymentFailed` event twice (at-least-once delivery). The compensation (refund) was not idempotent — it ran twice without checking if the refund was already issued.

**Fix:**

```java
@KafkaListener(topics = "payment.failed")
@Transactional
public void handlePaymentFailed(PaymentFailedEvent event) {
    // Idempotency check: was compensation already applied?
    if (sagaCompensationRepository.existsByOrderIdAndType(
            event.getOrderId(), "REFUND_ISSUED")) {
        log.info("Compensation already applied for order {}", event.getOrderId());
        return;  // skip: already done
    }

    // Apply compensation
    paymentService.issueRefund(event.getOrderId(), event.getAmount());

    // Record that compensation was applied
    sagaCompensationRepository.save(new SagaCompensation(
        event.getOrderId(), "REFUND_ISSUED", Instant.now()
    ));
}
```

---

### 🔗 Related Keywords

**Prerequisites:** ACID, CAP Theorem (DB), Database Sharding
**Builds On This:** Two-Phase Commit (2PC), Saga Pattern (DB)
**Related:** Two-Phase Commit (2PC), Saga Pattern (DB), ACID

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 2PC         │ ACID atomic; blocking; TM crash = locked   │
│ SAGA        │ Eventual consistent; non-blocking;         │
│             │ compensating txns for rollback             │
│ USE 2PC     │ Same-org DBs, short txns, ACID required    │
│ USE SAGA    │ Microservices, long-running, HA required   │
│ CHOREOG     │ Event-driven, loose coupling               │
│ ORCHESTR    │ Central coordinator, better observability  │
│ CRITICAL    │ Compensations must be idempotent           │
│ ONE-LINER   │ "2PC = all-or-nothing by lock consensus;   │
│             │  Saga = all-or-rollback via compensations" │
│ NEXT EXPLORE│ Two-Phase Commit (2PC) → Saga Pattern (DB) │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design the distributed transaction strategy for a travel booking platform: users book a hotel + flight + car simultaneously. Requirements: all must be booked or none (consistency); the booking platform doesn't control hotel/flight/car databases directly (external APIs); each booking request should complete in < 5 seconds. Choose between 2PC and Saga, design the failure handling, and specify what the user sees if the car booking fails after hotel and flight are confirmed.

**Q2.** (TYPE D — Failure Scenario) An e-commerce saga is: Reserve Inventory → Process Payment → Update Order Status. The "Process Payment" step crashes 30% of the time due to a flaky payment gateway. The Inventory Reservation compensation (release inventory) is not idempotent. After 1 week of production, the inventory database shows: 5% of reserved items are never released (ghost reservations), and 2% of items were released twice (negative inventory). Diagnose both bugs and provide fixes.
