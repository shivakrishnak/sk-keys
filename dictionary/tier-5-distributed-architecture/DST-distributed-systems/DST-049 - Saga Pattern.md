---
id: DST-049
title: "Saga Pattern"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-045, DST-050
related: DST-035, DST-033, DST-045, DST-056, DST-055
tags:
  - distributed
  - pattern
  - architecture
  - deep-dive
  - advanced
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /distributed-systems/saga-pattern/
---

# DST-049 - Saga Pattern

⚡ TL;DR - A saga is a sequence of local transactions across microservices where each step publishes an event (or sends a command) to trigger the next, and each step has a corresponding compensating transaction to undo it if a later step fails — replacing distributed 2PC with eventual consistency.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-045, DST-050                            |     |
| **Related:**    | DST-035, DST-033, DST-045, DST-056, DST-055 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user places an order in an e-commerce system built with microservices: Order Service → Payment Service → Inventory Service → Shipping Service. Each service has its own database. The operation must be atomic: either ALL succeed or ALL are rolled back. The obvious solution: 2-Phase Commit (DST-035). But 2PC requires a distributed coordinator that holds locks across all 4 services until all confirm. In a microservices architecture: this creates tight coupling, synchronous blocking, and availability problems (if ANY service is unavailable: the coordinator blocks, all resources are locked).

**THE BREAKING POINT:**
Two-Phase Commit (2PC) was designed for databases within the same organization, connected by a reliable network, with coordinated schemas. Microservices violate all three assumptions: different teams, unreliable network between services, independently deployed. 2PC in microservices leads to: distributed deadlocks (services holding locks while waiting for a coordinator that's down), availability collapse (all services blocked when coordinator fails), and tight coupling (services can't be deployed independently when bound by a coordinator). 2PC scales to ~5 participants; order workflows regularly involve 10+ services.

**THE INVENTION MOMENT:**
Hector Garcia-Molina and Kenneth Salem published "Sagas" in 1987 in the context of long-lived database transactions (LLTs). An LLT holds locks for seconds or minutes — too long for OLTP performance. Their insight: break an LLT into a sequence of short transactions (T1, T2, …, Tn), each completing atomically. If Tk fails: run compensating transactions C(k-1), C(k-2), …, C1 to undo the work done so far. Total atomicity is replaced by eventual consistency + compensation. Microservices architects adopted this pattern for distributed transactions in 2015-2018 as the limitations of 2PC in distributed systems became apparent.

**EVOLUTION:**
1987: Garcia-Molina & Salem — Sagas for LLTs in RDBMS. 2015: Sam Newman's _Building Microservices_ — sagas for cross-service transactions. 2016: Chris Richardson — Saga pattern classification (choreography vs orchestration). 2018: Richardson's _Microservices Patterns_ — comprehensive Saga treatment with outbox pattern integration. 2019+: Axon Framework, Temporal, AWS Step Functions — saga orchestration engines. 2022: Temporal — workflow-as-code with automatic compensation.

---

### 📘 Textbook Definition

**Saga** is a pattern for managing data consistency across microservices in distributed systems without using distributed transactions (2PC). A saga is a sequence of local transactions (T1, T2, …, Tn). Each Ti is ACID within its service's database. Ti completes by publishing an event or sending a command to trigger Ti+1. If Ti fails: a sequence of compensating transactions (C(i-1), C(i-2), …, C1) is executed to semantically undo the completed steps. **Compensating transactions** are NOT rollbacks — they are NEW forward transactions that undo the EFFECT of the original transaction. `OrderCreated` cannot be rolled back; `OrderCancelled` is the compensation. **Two saga styles:** (1) **Choreography:** each service listens for events and decides its own next action. Decentralized coordination. (2) **Orchestration:** a central saga orchestrator sends commands to services and receives responses, controlling the flow. Both achieve the same consistency guarantee — eventual consistency with compensation.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Replace one distributed transaction with a sequence of local transactions, each undoable by a compensation step if anything fails downstream.

> A saga is like a relay race with an undo button. Each runner (service) runs their leg (local transaction) and passes the baton (event). If a runner drops the baton (transaction fails): all previous runners must run BACKWARDS to their starting positions (compensation transactions). The race is "consistent" even if it didn't complete: either everyone finished forward, or everyone returned to the start.

**One insight:** A saga does NOT guarantee atomicity — it guarantees eventual consistency. Between the time T2 completes and C1 runs compensation, the system is in a "partially completed" state. This is a fundamental difference from 2PC: sagas trade ACID atomicity for availability and decoupling.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Each Ti is a local ACID transaction.** No distributed coordination within a single step. The unit of atomicity is the local transaction, not the whole saga.
2. **Each Ti has a compensating transaction Ci.** Ci is a semantically meaningful undo. It cannot be a database rollback (Ti is already committed). Ci must be a NEW transaction: `CreateOrder` → compensating = `CancelOrder`.
3. **Compensating transactions must be idempotent (DST-045).** Compensation may be triggered multiple times (message retry). `CancelOrder(orderId)` called twice must produce the same result as calling once.
4. **Sagas have no global locks.** Resources are locked only for the duration of each local transaction (milliseconds). No cross-service locking. This means: another saga or query may read partially-completed saga data. Sagas provide ACD (no Isolation) not ACID.

**DERIVED DESIGN:**

```
Saga steps:
  T1: CreateOrder (Order Service)     → C1: CancelOrder
  T2: ReserveInventory (Inventory)    → C2: ReleaseInventory
  T3: AuthorizePayment (Payment)      → C3: RefundPayment
  T4: ApproveOrder (Order Service)    → (no compensation needed)
  T5: ShipOrder (Shipping)            → (terminal step)

Failure at T3 (payment declined):
  Run C2: ReleaseInventory
  Run C1: CancelOrder
  Saga terminates in compensated state
```

**THE TRADE-OFFS:**
**Gain:** No distributed locking. Each service independently available. Services can fail and recover without blocking others. Scalable to N services.
**Cost:** No isolation — dirty reads possible (another transaction sees T1's result before the saga completes or compensates). Compensation logic complexity. Eventual consistency (not immediate). Compensating transactions that are hard or impossible to write (external side effects: emails sent, physical goods shipped).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Designing compensating transactions for irreversible real-world actions is inherently complex. "Payment authorized" cannot be truly undone if the user's bank already settled the transaction — you issue a refund (semantically undo, not technically undo). This complexity is irreducible — it's the price of not having 2PC.
**Accidental:** Choreography vs orchestration (DST-050), saga state persistence mechanism (Axon, Temporal, custom), event sourcing (DST-056) vs CRUD for saga state.

---

### 🧪 Thought Experiment

**SETUP:** Order saga: T1 (CreateOrder) → T2 (ReserveInventory) → T3 (AuthorizePayment) → T4 (ShipOrder). Payment service fails at T3 (card declined).

**WITH 2PC:**

- Coordinator holds locks on ALL four services during the entire transaction.
- T1, T2, T3 run in one phase. T3 fails.
- Coordinator sends ABORT to all participants.
- T1 and T2 rolled back (database rollback — transaction never committed).
- Strong atomicity: either all succeed or none.
- But: if Payment Service is down for 1 hour → all locks held for 1 hour → Order Service and Inventory Service completely blocked for 1 hour.

**WITH SAGA:**

- T1: CreateOrder (commits immediately). Order is now in "PENDING" state.
- T2: ReserveInventory (commits). Inventory shows item as "reserved."
- T3: AuthorizePayment (fails — card declined). Payment NOT committed.
- Run C2: ReleaseInventory (NEW transaction — releases reservation).
- Run C1: CancelOrder (NEW transaction — order moved to "CANCELLED").
- If Payment Service is down: saga pauses at T3. T1 and T2 remain committed. Retry T3 when Payment Service recovers. Or: C2, C1 run after timeout. No locks held on other services during the wait.

**THE INSIGHT:** Between T2 committed and C2 running: there is a window where inventory shows "reserved" for an order that will be cancelled. This is the lack of isolation. A query reading inventory during this window sees incorrect state. Saga trades this isolation window for the ability to continue operating when any single service is unavailable.

---

### 🧠 Mental Model / Analogy

> A saga is like booking a multi-leg trip: flight + hotel + rental car. You book each separately (T1, T2, T3). If the rental car is unavailable (T3 fails): you cancel the hotel (C2) and cancel the flight (C1). Each cancellation is a NEW booking action — you call the hotel to cancel (you can't press "un-click" on a past booking). The travel agency doesn't hold the flights and hotel suspended while you confirm the rental car — they're already booked (committed). You just undo them with cancellation (compensation) if needed.

**Mapping:**

- **Booking a flight** → T1 (CreateOrder)
- **Booking a hotel** → T2 (ReserveInventory)
- **Rental car booking fails** → T3 failure
- **Cancelling hotel** → C2 (ReleaseInventory compensation)
- **Cancelling flight** → C1 (CancelOrder compensation)
- **No "un-click"** → no database rollback — compensations are forward transactions

Where this analogy breaks down: cancellation fees (the compensation is more costly than the original). In software: compensations may have side effects (refund notifications, inventory system updates, customer emails). The compensation may not perfectly restore the original state — some saga steps have inherent side effects that cannot be fully compensated.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A saga is a business transaction that spans multiple databases. Instead of locking everything and hoping it all works (2PC), each step completes and saves its work. If a later step fails: each earlier step is "undone" with a new undo action. Like booking a trip piece by piece — if something doesn't work, you cancel what you already booked, one piece at a time.

**Level 2 - How to use it (junior developer):**
Design saga steps: list all the services involved in the business transaction. For each step: write the forward transaction AND the compensating transaction. Name them clearly: `CreateOrder` / `CancelOrder`, `ReserveItem` / `ReleaseItem`. Use a message broker (Kafka, RabbitMQ) to sequence steps: each service publishes an event on success, another service listens. Use a saga orchestrator (Axon, Temporal, Spring State Machine) to track which step failed and which compensations to run.

**Level 3 - How it works (mid-level engineer):**
Saga state must be persisted durably. When T2 completes: the saga state (`SAGA_ID=123, STEP=2, STATUS=SUCCESS`) must be written to a store (DB or event log). If the saga orchestrator crashes: on restart, it reads the saga state and resumes from where it left off. Without durable saga state: crash between steps = saga stuck (neither completed nor compensated). Outbox pattern (DST-033) is critical: T1's local transaction must atomically write the order record AND the saga event to the same database (outbox table). A transactional outbox relay publishes the event to the message broker. Without outbox: T1 commits, event publish fails → T2 never triggers → saga stuck.

**Level 4 - Why it was designed this way (senior/staff):**
Garcia-Molina's original 1987 paper defined two properties of sagas: SEC (Saga Execution Complete) — either all Ti complete successfully, or all Ci for completed Ti have run. This is "eventual atomicity" — not ACID atomicity. The key insight of the modern microservices saga: each service is its own consistency boundary. The inter-service consistency is achieved through compensations, not locks. This matches the CAP theorem (DST-027) — choosing availability over consistency at the distributed level, while maintaining consistency within each service's local transaction. The saga pattern is thus a direct application of CAP: accept eventual consistency across services, maintain ACID within each service.

**Expert Thinking Cues:**

- "Compensation T3 needs to refund a payment, but the bank is slow and the refund takes 3 business days" → This is an irreversible side effect. The compensation is "issue refund request" — not "undo payment." The saga is complete when the refund is ISSUED (not settled). The customer receives their money after 3 days. This is correct saga behavior: sagas guarantee business-level consistency (refund issued), not technical-level atomicity (money immediately returned).
- "Two saga instances conflict: they both reserve the last item in inventory" → Saga lacks isolation. Both T2s may succeed for the last item. When T4 (shipping) runs: only one item exists → one saga fails. Compensation runs. Solution: use optimistic locking in the inventory service (`version` field) — the second concurrent reservation fails at the database level. Sagas rely on application-level conflict detection, not database-level isolation.
- "How do I handle a failed compensation?" → This is the "saga stuck" case — both the forward transaction and the compensating transaction are failing. Solution: (1) Retry compensation with backoff (most failures are transient). (2) Alert: human intervention required. (3) Store "saga stuck" state for manual resolution. Never silently ignore a failed compensation — the data is now inconsistent and requires human resolution.

---

### ⚙️ How It Works (Mechanism)

**Orchestration-based saga state machine:**

```
                  [Saga Orchestrator]
                         │
                   [STARTED]
                         │
          ─────────────────────────
          │                       │
    T1 success               T1 failure
    [ORDER_CREATED]          [SAGA_FAILED]
          │
    T2 success / T2 failure
    [INV_RESERVED] / [COMPENSATING]
                                │
                            C1: CancelOrder
                            [SAGA_COMPENSATED]
          │
    T3 success / T3 failure
    [PAYMENT_AUTHORIZED] / [COMPENSATING]
                                │
                            C2: ReleaseInventory
                            C1: CancelOrder
                            [SAGA_COMPENSATED]
          │
    T4 success
    [ORDER_SHIPPED]
    [SAGA_COMPLETED]
```

**Outbox pattern integration (mandatory for reliability):**

```
T1 executes:
  BEGIN TRANSACTION
    INSERT INTO orders VALUES (...)   -- local state
    INSERT INTO outbox VALUES (       -- saga event
      'OrderCreated', orderId, ...)
  COMMIT

Outbox relay (async):
  SELECT * FROM outbox WHERE published=false
  Publish 'OrderCreated' to Kafka
  UPDATE outbox SET published=true
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ORDER SAGA (ORCHESTRATION STYLE):**

```
Client  Orchestrator  OrderSvc  InventorySvc  PaymentSvc
  │         │             │          │            │
  │─place──▶│             │          │            │
  │         │─CreateOrder▶│          │            │
  │         │◀─Created────│          │            │
  │         │─ReserveInv─────────────▶           │
  │         │◀─Reserved────────────────           │
  │         │─AuthPayment────────────────────────▶│
  │         │             │          │            │ ← YOU ARE HERE
  │         │◀─Declined───────────────────────────│ (card declined)
  │         │─ReleaseInv─────────────▶ (C2)      │
  │         │◀─Released────────────────           │
  │         │─CancelOrder▶│ (C1)     │            │
  │         │◀─Cancelled──│          │            │
  │◀─failed─│ (order failed: no payment)
```

**WHAT CHANGES AT SCALE:**
At scale: many sagas run concurrently. Each saga is independent (different order IDs). The saga orchestrator must handle concurrent sagas: saga state is partitioned by saga ID. Kafka partitioned by order ID: events for the same saga go to the same partition, preserving ordering within a saga while allowing parallelism across sagas.

---

### 💻 Code Example

**BAD - Distributed transaction attempt with synchronous chaining:**

```java
// BAD: synchronous chain with no compensation
// If payment fails: inventory already reserved (data inconsistent)
public void placeOrder(Order order) {
    orderService.create(order);        // commits immediately
    inventoryService.reserve(order);   // commits immediately
    try {
        paymentService.charge(order);  // fails?
    } catch (PaymentFailedException e) {
        // No compensation: inventory stays reserved!
        throw new OrderFailedException(e);
    }
}
```

**GOOD - Orchestration saga with compensation:**

```java
// GOOD: Saga orchestrator with defined compensation steps
@SagaOrchestrator
public class OrderSaga {
    private String sagaId;
    private String orderId;

    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void handle(PlaceOrderCommand cmd) {
        this.sagaId = cmd.getSagaId();
        this.orderId = cmd.getOrderId();
        // Step 1: create order (local transaction)
        commandGateway.send(new CreateOrderCommand(orderId));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(OrderCreatedEvent evt) {
        // Step 2: reserve inventory
        commandGateway.send(
            new ReserveInventoryCommand(orderId,
                evt.getItems()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryReservedEvent evt) {
        // Step 3: authorize payment
        commandGateway.send(
            new AuthorizePaymentCommand(orderId,
                evt.getAmount()));
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(PaymentDeclinedEvent evt) {
        // Failure: compensate in reverse order
        commandGateway.send(
            new ReleaseInventoryCommand(orderId)); // C2
    }

    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryReleasedEvent evt) {
        commandGateway.send(
            new CancelOrderCommand(orderId));      // C1
    }

    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(OrderCancelledEvent evt) {
        // Compensation complete: saga ends
        log.info("Saga {} compensated for order {}",
            sagaId, orderId);
    }
}

// Compensation must be idempotent:
@CommandHandler
public void handle(ReleaseInventoryCommand cmd) {
    Inventory inv = inventoryRepo.findById(cmd.getOrderId());
    if (inv.getStatus() != RELEASED) { // idempotent check
        inv.release();
        inventoryRepo.save(inv);
        eventBus.publish(new InventoryReleasedEvent(
            cmd.getOrderId()));
    }
}
```

---

### ⚖️ Comparison Table

|                  | Two-Phase Commit (2PC) | Saga (Choreography)         | Saga (Orchestration)       |
| :--------------- | :--------------------- | :-------------------------- | :------------------------- |
| Coordination     | Central coordinator    | Decentralized (events)      | Central orchestrator       |
| Atomicity        | ACID (full atomicity)  | ACD (eventual consistency)  | ACD (eventual consistency) |
| Isolation        | Full (locks held)      | None (dirty reads possible) | None                       |
| Coupling         | Tight (coordinator)    | Loose (events)              | Medium (orchestrator)      |
| Failure recovery | Coordinator handles    | Each service handles        | Orchestrator handles       |
| Scalability      | Low (locking)          | High                        | High                       |
| Debugging        | Difficult              | Very difficult              | Easier (central state)     |

---

### 🔁 Flow / Lifecycle

**Saga state lifecycle:**

```
STARTED
  → T1 running → T1_DONE
  → T2 running → T2_DONE
  → ...
  → COMPLETED (all steps succeeded)

  OR (failure at step Tk):
  → Tk_FAILED
  → COMPENSATING (running C(k-1)...C1)
  → COMPENSATED (all compensations complete)

  OR (compensation failure):
  → COMPENSATION_FAILED (human intervention required)
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| :----------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Saga provides the same consistency as 2PC"            | Saga provides eventual consistency, NOT ACID atomicity. A saga has no global isolation — between T2 committing and the saga completing/compensating, other transactions can read partially-completed saga state. This "dirty read" window is a fundamental property of sagas. If your use case requires full isolation: 2PC or a different architecture is needed.                                                                                                                              |
| "Compensation = rollback"                              | Compensation is a FORWARD transaction that semantically undoes a previous transaction. It is NOT a database rollback. T1 (`CreateOrder`) is already committed to the database — it cannot be rolled back. C1 (`CancelOrder`) is a new transaction that changes the order status to CANCELLED. The database still has the original row, now with CANCELLED status. Audit logs show both the creation AND the cancellation.                                                                       |
| "If a compensation fails, just retry and it will work" | A compensation that fails consistently (not a transient error) indicates a business-level problem: the state that compensation was trying to fix may have changed further (a shipping label was already printed, a physical good already dispatched). Repeated compensation failure requires human intervention, not just technical retry. Alert and escalate immediately.                                                                                                                      |
| "Choreography sagas are simpler than orchestration"    | Choreography (events-only, no central orchestrator) appears simpler initially — no orchestrator to build. But saga state is implicit in the event sequence, making it very hard to answer "what state is this saga in right now?" Debugging a stuck choreography saga requires reconstructing state from a sequence of events across multiple services. Orchestration sagas have explicit, queryable state in the orchestrator. At scale: orchestration is almost always operationally simpler. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Lost Saga Event — Saga Stuck in Intermediate State**

**Symptom:** Orders are "stuck" in PENDING status indefinitely. Investigation: `CreateOrder` and `ReserveInventory` completed. `AuthorizePayment` event was published to Kafka, but the payment service never processed it. Kafka topic retention period expired (7 days). Event lost. Saga waiting for payment response that will never come.
**Root Cause:** No outbox pattern. Event was published directly to Kafka outside the database transaction. Payment service was down when event published → Kafka received event → retention expired → event gone. No idempotent re-publish mechanism.
**Diagnostic:**

```bash
# Find stuck sagas:
SELECT saga_id, current_step, last_updated
FROM sagas
WHERE status = 'IN_PROGRESS'
  AND last_updated < NOW() - INTERVAL '1 hour'
ORDER BY last_updated;
# Sagas in-progress > 1h: stuck (timeout exceeded)

# Check Kafka consumer lag for saga events:
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe --group saga-consumer
# High lag: consumer not processing events
# Offset = latest: event may have been consumed but not acked
```

**Fix:**
BAD: Publish event directly to Kafka after DB commit (separate operations, can fail independently).
GOOD: Use outbox pattern: write event to outbox table in the SAME transaction as the business operation. Outbox relay publishes idempotently. Set saga timeout: if no progress for X minutes → trigger compensation.
**Prevention:** Every saga step must use outbox pattern. Saga orchestrator must have a timeout/watchdog: stuck sagas detected after N minutes → compensation triggered automatically.

**Failure Mode 2: Compensation Fails — Data Permanently Inconsistent**

**Symptom:** Order saga: T1 (CreateOrder) and T2 (ReserveInventory) succeeded. T3 (AuthorizePayment) failed. C2 (ReleaseInventory) triggered but failed — Inventory Service is down for maintenance. Saga stuck: order is CANCELLED (C1 ran), but inventory still shows the item as RESERVED. Inventory inconsistent with no automatic recovery.
**Root Cause:** Compensation failure is not handled — no retry, no alert, no human escalation path. The saga is in COMPENSATION_FAILED state with no recovery strategy.
**Diagnostic:**

```bash
# Find sagas with failed compensations:
SELECT saga_id, failed_step, compensation_attempts
FROM sagas
WHERE status = 'COMPENSATION_FAILED'
ORDER BY created_at DESC;
# These require manual investigation

# Check inventory for stuck reservations:
SELECT order_id, item_id, reserved_at, status
FROM inventory_reservations
WHERE status = 'RESERVED'
  AND order_id IN (
    SELECT saga_id FROM sagas
    WHERE status = 'COMPENSATION_FAILED'
  );
# Reserved items for cancelled orders: inconsistency found
```

**Fix:**
BAD: Compensation failure → log and ignore.
GOOD: (1) Retry compensation with exponential backoff (max 10 retries). (2) If retries exhausted: move saga to COMPENSATION_FAILED, alert on-call. (3) Provide admin tool for manual compensation replay. (4) Design compensations to be IDEMPOTENT so they can be replayed safely.
**Prevention:** Test compensation failure scenarios in staging. Implement saga watchdog: any saga in COMPENSATING state for > 30 minutes → alert. Provide runbook for manual compensation.

**Failure Mode 3: Security - Saga Without Idempotency Key — Duplicate Charges**

**Symptom:** Payment service processes a charge for order 123. Response sent to saga orchestrator. Network drops. Orchestrator retries T3 (AuthorizePayment) with the same orderId. Payment service sees orderId=123, no idempotency check, processes charge again. Customer charged twice.
**Root Cause:** Payment service T3 is not idempotent. Saga orchestrator retries on timeout (correct behavior) but payment service processes the retry as a new charge. Saga assumes retryable operations are idempotent — they must be.
**Diagnostic:**

```bash
# Find duplicate charges for same order:
SELECT order_id, amount, authorized_at, charge_id
FROM payment_authorizations
WHERE order_id IN (
  SELECT order_id FROM payment_authorizations
  GROUP BY order_id HAVING COUNT(*) > 1
);
# Duplicate rows = double charge

# Check if payment service uses idempotency keys:
grep -r "idempotencyKey\|X-Idempotency-Key\|idempotent" \
  payment-service/src/ | grep -v test
# If not present: no idempotency → duplicate charge risk
```

**Fix:**
BAD: Saga T3 sends `{orderId: 123, amount: 100}`. Payment service charges on every call with same orderId.
GOOD: Saga T3 sends `{orderId: 123, amount: 100, idempotencyKey: "saga-123-step-3"}`. Payment service checks idempotency key first (DST-045). Duplicate request → return stored result (no second charge).
**Prevention:** Every saga step that has an external side effect (payment, email, SMS, shipping label) MUST be idempotent. Rule: saga step = local transaction that is idempotent. No exceptions for money movement, external API calls, or physical world operations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-045 - Idempotency (compensating transactions must be idempotent; saga steps must be idempotent for safe retry)
- DST-050 - Choreography vs Orchestration (saga is implemented with either choreography or orchestration — understand both before choosing)

**Builds On This (learn these next):**

- DST-033 - Outbox Pattern (reliable event publication for saga steps — required for production sagas)
- DST-056 - Event Sourcing (saga state stored as event sequence; natural pairing with sagas)

**Alternatives / Comparisons:**

- DST-035 - Two-Phase Commit (alternative for distributed transactions — strong consistency vs saga's eventual consistency)
- DST-055 - CQRS (often combined with saga for eventual consistency in read models)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Sequence of local transactions |
|                  | with compensating transactions |
|                  | for failure recovery           |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Distributed transactions across|
|                  | microservices without 2PC      |
|                  | (no distributed locking)       |
+------------------+--------------------------------+
| KEY INSIGHT      | Trade ACID atomicity for       |
|                  | ACD (eventual consistency)     |
|                  | + compensation on failure      |
+------------------+--------------------------------+
| USE WHEN         | Multi-service business         |
|                  | transactions; microservices;   |
|                  | long-running workflows         |
+------------------+--------------------------------+
| AVOID WHEN       | Need full ACID isolation;      |
|                  | compensations are impossible   |
|                  | (physical goods dispatched)    |
+------------------+--------------------------------+
| TRADE-OFF        | Availability + decoupling      |
|                  | vs isolation + complexity      |
+------------------+--------------------------------+
| ONE-LINER        | Local transactions + reverse   |
|                  | compensation = distributed     |
|                  | "eventual atomicity"           |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-033 Outbox Pattern,        |
|                  | DST-056 Event Sourcing,        |
|                  | DST-050 Choreography vs Orch   |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Compensation is NOT rollback — it is a NEW forward transaction that semantically undoes a previous committed transaction. `CancelOrder` is not a database rollback of `CreateOrder` — it's a new transaction that changes the order status to CANCELLED. Both transactions exist in the audit log.
2. Every saga step must be idempotent (DST-045). The saga orchestrator will retry failed or timed-out steps. If a step charges a payment: charging twice because of a retry is a bug, not expected behavior. Use idempotency keys for all external side effects.
3. Use the outbox pattern (DST-033) for publishing saga events. Direct Kafka publish after DB commit has a failure window: DB commits, publish fails, saga never advances. Outbox atomically stores events in the same DB transaction, then reliably publishes them.

**Interview one-liner:**
"A saga replaces distributed 2PC with a sequence of local ACID transactions, each with a compensating transaction for rollback. If step N fails: run compensations for steps N-1 through 1 in reverse order. Two implementations: choreography (services react to events, decentralized) and orchestration (central orchestrator commands services). Key trade-off: no global isolation — between steps, partially-completed saga state is visible to other transactions. Critical invariant: every saga step must be idempotent (safe to retry) and every compensation must be idempotent (safe to replay). Production requirement: outbox pattern for reliable event publication."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Long operations that span multiple systems must be designed as reversible sequences, not atomic blocks. The illusion of atomicity breaks at distribution boundaries. The principle: for any multi-step operation, define the compensation (undo) at design time — before implementing the forward operation. If the compensation is impossible (physical goods shipped, email sent, money transferred externally): acknowledge this upfront and design mitigation (grace period, manual override, "best effort" compensation notice). This principle appears in undo/redo in text editors, compensating entries in accounting, and transaction reversal in banking — wherever a committed operation must be "semantically undone" without violating the integrity of the record.

**Where else this pattern appears:**

- **Double-entry bookkeeping:** Every financial transaction is recorded as two entries: debit and credit. A compensation (reversal) is a new pair of entries — not an erasure of the original. The original transaction is immutable. This is exactly the saga pattern applied to accounting: forward transactions commit permanently, compensations are NEW transactions that offset the original. The ledger shows both the original debit and the compensating credit — full audit trail.
- **CQRS + Saga for order processing:** In CQRS (DST-055): commands (CreateOrder, ReserveInventory) are handled by saga steps. Events (OrderCreated, InventoryReserved) update read models asynchronously. The saga coordinates the command side while CQRS handles the read side. This pairing — saga for write-side consistency, CQRS for read-side eventual consistency — is a common pattern in DDD-based microservices (Axon Framework uses exactly this).
- **Kubernetes operator reconciliation as a saga:** A Kubernetes operator that provisions a multi-component system (database + app + ingress) implements a saga: each provisioning step is a local operation. If any step fails: the operator runs cleanup steps (delete created resources). The reconciliation loop is the compensation mechanism: repeatedly runs until the desired state is achieved or compensation completes. Kubernetes controllers are the infrastructure-layer equivalent of saga orchestrators.

---

### 💡 The Surprising Truth

The saga pattern was invented in 1987 — not for microservices, but for the opposite problem: LONG-RUNNING TRANSACTIONS within a single relational database. Garcia-Molina's paper addressed the case where a single SQL transaction might hold locks for minutes or hours (batch processing, complex calculations), blocking all other database operations. Their solution — break the long transaction into smaller committed sub-transactions with compensating transactions — was entirely within a single database. Microservices architects 30 years later realized the same principle applied across service boundaries: if a "transaction" spans multiple services (each with its own database), use the same sequence-of-local-transactions + compensation approach. The surprising truth: the saga pattern's origin had nothing to do with distributed systems. It was a solution to database locking in a single machine — and it turned out to be exactly the right model for distributed systems too.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** An order saga runs T1 (CreateOrder) → T2 (ReserveInventory) → T3 (AuthorizePayment). T3 fails. C2 (ReleaseInventory) is triggered. During C2 execution: the Inventory Service crashes and restarts. C2 never completes. The saga orchestrator retries C2 after restart. But: inventory service lost its in-memory state (it was not using the outbox pattern for compensation events). What state is the system in, and what is required for C2 to be safely retried?
_Hint:_ State: T2 is committed (inventory reserved). T3 failed (no payment). C2 was partially executed (compensation incomplete due to crash). On retry: C2 runs again on the same orderId. If C2 (`ReleaseInventory`) is idempotent: calling it again returns success (inventory was already released in the partial execution, or releases it on retry). If C2 is NOT idempotent: could release inventory that was already released (double-release: inventory count goes negative or wrong). Required for safe retry: C2 must be idempotent. Implementation: `UPDATE inventory SET status='AVAILABLE' WHERE order_id=? AND status='RESERVED'`. This is naturally idempotent — repeated calls only change status from RESERVED to AVAILABLE once. If status is already AVAILABLE: no change, no error.

**Q2 (B - Scale):** An e-commerce platform runs 10,000 order sagas per minute. Each saga has 5 steps. The saga orchestrator stores saga state in a single PostgreSQL database. What are the scalability challenges of this design, and how would you architect the saga state store for 10,000 sagas/minute?
_Hint:_ Problems at 10,000 sagas/minute: (1) 10,000 sagas × 5 steps = 50,000 state updates/minute = ~833 writes/second to the saga state table. At 5ms per write: 4.2s of serial write time. This is fine for a single writer, but with concurrent sagas: row-level locking contention on the saga state table. (2) Long-running sagas (minutes to hours) fill the saga state table. Need TTL/archival strategy. (3) Orchestrator becomes a hot spot: all 10,000 concurrent sagas route through it. Solutions: (1) Partition saga state by saga ID (sharding). (2) Use event sourcing (DST-056) for saga state — append-only event log (better write throughput). (3) Use dedicated saga infrastructure (Temporal, Axon) that handles partitioning internally. (4) Separate hot saga state (in-progress) from cold state (completed) — hot state in Redis, cold state in DB.

**Q3 (D - Root Cause):** A team migrated from 2PC to sagas for their order processing system. Post-migration: customer service receives increased reports of "ghost orders" — orders that appear in the customer's order history as PENDING but are never fulfilled and never cancelled. They persist for days. What is the likely cause, and how do you diagnose it?
_Hint:_ "Ghost orders" = saga stuck in PENDING (T1 complete, saga never advanced to T2, T3, or compensation). Likely causes: (1) Saga event for step 2 (ReserveInventory) was lost or never published. T1 committed, event published to Kafka, Kafka consumer for Inventory Service was down → event consumed but not processed → consumer offset committed → event gone. Saga waits for InventoryReservedEvent that will never come. Fix: saga watchdog — detect sagas in_progress for > 10 minutes, trigger compensation. (2) Outbox relay is not running. Events are in the outbox table but never published to Kafka. Saga waits for step 2 that was never triggered. Fix: monitor outbox table for unpublished events > 1 minute. (3) Inventory Service is consuming events but crashing before publishing InventoryReservedEvent. Fix: Inventory Service must use outbox pattern for its own events too — not just the first service in the chain. Diagnostic: query `SELECT * FROM sagas WHERE status='IN_PROGRESS' AND updated_at < NOW() - INTERVAL '10 minutes'`. These are your ghost orders.
