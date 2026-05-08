---
layout: default
title: "Saga Pattern (Microservices)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /microservices/saga-pattern-microservices/
id: MSV-038
category: Microservices
difficulty: ★★★
depends_on: Distributed Transaction, Event-Driven Microservices, Choreography vs Orchestration
used_by: Saga via Task Orchestration, Event Sourcing in Microservices, Temporal (Workflow Orchestration)
related: Two-Phase Commit (2PC), CQRS in Microservices, Outbox Pattern
tags:
  - microservices
  - distributed
  - pattern
  - reliability
  - deep-dive
---

# MSV-038 — Saga Pattern (Microservices)

⚡ TL;DR — The Saga pattern sequences local transactions across microservices with compensating rollback actions, replacing distributed two-phase commit with eventual consistency.

| #653            | Category: Microservices                                                                         | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Transaction, Event-Driven Microservices, Choreography vs Orchestration              |                 |
| **Used by:**    | Saga via Task Orchestration, Event Sourcing in Microservices, Temporal (Workflow Orchestration) |                 |
| **Related:**    | Two-Phase Commit (2PC), CQRS in Microservices, Outbox Pattern                                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce checkout spans three services: Orders (creates order), Inventory (reserves stock), Payments (charges card). Each service has its own database. A traditional ACID transaction cannot span three separate databases. You could use Two-Phase Commit (2PC) — but 2PC requires all services to hold database locks for the duration of the transaction, blocking concurrent operations, reducing throughput, and creating a central coordinator that becomes a single point of failure. With microservices decentralised by design, 2PC violates the autonomy principle.

**THE BREAKING POINT:**
Without a pattern, teams either use 2PC (coupling, locking, fragility) or do nothing (leaving partial states — order created, payment charged, inventory not reserved). A network failure mid-checkout leaves the customer charged but no order created. There's no recovery path.

**THE INVENTION MOMENT:**
This is exactly why the Saga pattern was created — a sequence of local transactions linked by events or commands, each with a defined compensating action, so that partial failures result in clean rollback rather than stuck partial state.

---

### 📘 Textbook Definition

A **Saga** is a distributed transaction pattern that decomposes a multi-step business operation into a sequence of local transactions, each publishing an event or sending a message to trigger the next step. If any step fails, compensating transactions are executed in reverse order to undo the completed steps. Sagas are implemented in two styles: **Choreography** (services react to events autonomously) and **Orchestration** (a central coordinator directs each step). Sagas provide eventual consistency without distributed locking.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Break a multi-service transaction into steps, with undo instructions for each step in case of failure.

**One analogy:**

> Booking a holiday involves booking flights, hotels, and car hire separately. If the car hire fails, you cancel the hotel, then cancel the flights. Each booking is a separate transaction with its own cancellation — linked in sequence. A saga is this exact process, automated.

**One insight:**
The radical shift in sagas is accepting that the system will be _temporarily inconsistent_. Between steps, the order is in a "pending" state. This is acceptable because the saga guarantees it will _eventually_ reach either fully committed or fully rolled back — no stuck half-states.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Each microservice owns its data and cannot participate in a shared database transaction.
2. A multi-step business operation can fail at any step.
3. The business must either fully complete or cleanly undo — not remain in half-done state.

**DERIVED DESIGN:**
Given these invariants: each step must be a local transaction (single database, atomic). On success, publish an event/command to trigger the next step. Each step must have a _compensating transaction_ — the business-level undo (not a database rollback). The saga must track which steps completed so it knows which compensations to execute.

**Compensation is NOT a database rollback.** If inventory was reserved and email was sent, you can't un-send the email. The compensating transaction for "reserve inventory" is "release inventory reservation." For "send confirmation email," the compensation is "send cancellation email." Compensations must be defined at design time for every step.

**Two implementation styles:**

**Choreography Saga:**

- No central coordinator.
- Each service listens to events and decides its own action.
- Steps: Order → emits `OrderCreated` → Inventory listens → reserves → emits `StockReserved` → Payment listens → charges → emits `PaymentCharged`.
- Rollback: Payment fails → emits `PaymentFailed` → Inventory listens → releases reservation → Inventory emits `StockReleased` → Order listens → marks order failed.
- Pro: loose coupling. Con: hard to track overall state; complex debugging.

**Orchestration Saga:**

- A central saga orchestrator sends commands to each service and waits for reply.
- Orchestrator tracks state machine: PENDING → ORDER_CREATED → STOCK_RESERVED → PAYMENT_CHARGED → COMPLETED.
- On failure: orchestrator sends explicit compensation commands in reverse.
- Pro: explicit state machine, easy to monitor. Con: orchestrator is a coupling point.

**THE TRADE-OFFS:**
**Gain:** Multi-service transactions without distributed locking; each service remains autonomous; works with message brokers.
**Cost:** Temporary inconsistency between steps; compensation logic complexity; saga state must be persisted; hard to implement correctly without a framework.

---

### 🧪 Thought Experiment

**SETUP:**
Checkout flow: (1) Create Order, (2) Reserve Inventory, (3) Charge Payment. Payment fails at step 3.

**WHAT HAPPENS WITHOUT SAGA:**
Step 1: order row inserted. Step 2: inventory decremented. Step 3: payment fails. No rollback mechanism. Order is "created" but unpaid. Inventory is reduced but no sale completed. Manual cleanup required. Customer confused.

**WHAT HAPPENS WITH SAGA:**
Step 3 (charge) fails → orchestrator receives `PaymentFailed` → sends compensation command to Inventory: `ReleaseReservation(orderId)` → Inventory restores stock → orchestrator sends compensation to Order: `CancelOrder(orderId)` → Order marked CANCELLED → orchestrator marks saga COMPENSATED. Customer sees "order failed" immediately. Inventory is clean. No manual intervention.

**THE INSIGHT:**
The saga's power is the _pre-planned compensation_. Because you define "how to undo step 2" at design time, failure at step 3 can execute an automatic, reliable undo without any human intervention.

---

### 🧠 Mental Model / Analogy

> A military operation has sequenced phases: air support → ground advance → supply line. The plan includes abort procedures: if ground advance fails, recall air support and withdraw to starting position. The abort plan is written before the operation begins — not improvised during failure.

- "Military operation phases" → saga steps
- "Air support → ground advance → supply" → Order → Inventory → Payment
- "Abort procedures" → compensating transactions
- "Written before the operation" → compensation defined at design time
- "Recall air support" → release inventory reservation
- "Central command" → saga orchestrator

Where this analogy breaks down: in software, "withdrawal" must be idempotent — the same compensation command may be delivered multiple times (at-least-once messaging), so releasing a reservation twice must be safe.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A saga is a multi-step process where each step knows how to undo itself if a later step fails. Like a carefully planned booking system — if anything goes wrong, everything that was booked gets automatically cancelled in the right order.

**Level 2 — How to use it (junior developer):**
Define each step as a local transaction with a service-specific database. Define the compensating transaction for each step. Use a message broker to chain steps together. Track saga state in a dedicated table. The saga completes when all steps succeed or all compensations complete.

**Level 3 — How it works (mid-level engineer):**
**Orchestration saga state machine** (recommended for complex flows):

```
INITIAL → ORDER_CREATED → INVENTORY_RESERVED
        → PAYMENT_CHARGED → COMPLETED
        ↘ PAYMENT_FAILED → INVENTORY_RELEASING
        → ORDER_CANCELLING → COMPENSATED
```

The orchestrator persists its state after each command/response pair. If the orchestrator crashes, it replays from the last persisted state. Each service operation must be idempotent — commands may be retried. The Outbox Pattern is used to ensure the command/event is atomically published with the local transaction.

**Level 4 — Why it was designed this way (senior/staff):**
The saga pattern accepts the _ACD_ part of ACID (Atomicity via compensation, Consistency via events, Durability via event log) while intentionally abandoning isolation. Between saga steps, the system violates isolation — a reader can observe the intermediate state (order created, not yet paid). This is the "lost in translation" for teams expecting ACID semantics. The design answer is _semantic locking_: mark in-progress records with status=PENDING so other operations know to wait or skip them. Temporal.io and AWS Step Functions provide saga-like orchestration with built-in state persistence and retry.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│    Orchestration Saga — Checkout Flow                   │
└─────────────────────────────────────────────────────────┘

Orchestrator                   Services
    │
    │──CreateOrder──────────►Order Service
    │◄──OrderCreated──────────│ (local tx)
    │
    │──ReserveInventory─────►Inventory Service
    │◄──StockReserved─────────│ (local tx)
    │
    │──ChargePayment────────►Payment Service
    │◄──PaymentFailed─────────│ (local tx, rollback)
    │
    │  [COMPENSATION START]
    │──ReleaseInventory─────►Inventory Service
    │◄──InventoryReleased─────│ (compensation tx)
    │
    │──CancelOrder──────────►Order Service
    │◄──OrderCancelled────────│ (compensation tx)
    │
    │  [SAGA: COMPENSATED]
```

**Choreography alternative:**

```
OrderService → emits OrderCreated
InventoryService listens → reserves → emits StockReserved
PaymentService listens → charges → emits PaymentFailed
InventoryService listens for PaymentFailed → releases
OrderService listens for StockReleased → cancels order
```

**Outbox Pattern integration:**
Each service writes to its local DB AND a local outbox table in the same transaction. A relay process reads the outbox and publishes to the message broker. This guarantees the event is published if and only if the local transaction committed.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
[User clicks checkout] → [API Gateway]
  → [Saga Orchestrator ← YOU ARE HERE]
  → [Order Service: CREATE → success]
  → [Inventory Service: RESERVE → success]
  → [Payment Service: CHARGE → success]
  → [Saga: COMPLETED]
  → [User: "Order confirmed"]
```

**FAILURE PATH:**

```
[Payment CHARGE fails]
  → [Orchestrator enters compensation]
  → [Inventory: RELEASE → success]
  → [Order: CANCEL → success]
  → [Saga: COMPENSATED]
  → [User: "Order failed - try again"]
```

**WHAT CHANGES AT SCALE:**
At 10k checkouts/sec, the orchestrator becomes a throughput bottleneck if it's a single process. Partitioning sagas by `orderId` mod N allows parallel orchestrators without coordination. At 100k/sec, saga state storage becomes hot — partition by saga ID. At 1M/sec, teams use dedicated workflow engines (Temporal, AWS Step Functions) that handle sharding, persistence, and retry internally.

---

### 💻 Code Example

**Example 1 — Orchestration saga state machine (simplified):**

```java
@Service
public class CheckoutSagaOrchestrator {

  public void startCheckout(CheckoutRequest req) {
    SagaState state = new SagaState(
      req.orderId(), SagaStatus.PENDING);
    sagaRepository.save(state);

    // Step 1: Create order
    commandBus.send(new CreateOrderCommand(req));
  }

  @EventHandler
  public void onOrderCreated(OrderCreatedEvent e) {
    SagaState state = sagaRepository.find(e.orderId());
    state.setStatus(SagaStatus.ORDER_CREATED);
    sagaRepository.save(state);
    // Step 2: Reserve inventory
    commandBus.send(new ReserveInventoryCommand(e));
  }

  @EventHandler
  public void onPaymentFailed(PaymentFailedEvent e) {
    SagaState state = sagaRepository.find(e.orderId());
    state.setStatus(SagaStatus.COMPENSATING);
    sagaRepository.save(state);
    // Compensate step 2
    commandBus.send(
      new ReleaseInventoryCommand(e.orderId()));
  }

  @EventHandler
  public void onInventoryReleased(
      InventoryReleasedEvent e) {
    // Compensate step 1
    commandBus.send(new CancelOrderCommand(e.orderId()));
  }
}
```

**Example 2 — Temporal.io orchestration saga:**

```java
@WorkflowInterface
public interface CheckoutWorkflow {
  @WorkflowMethod
  void processCheckout(CheckoutRequest req);
}

@WorkflowImpl
public class CheckoutWorkflowImpl
    implements CheckoutWorkflow {

  private final OrderActivity orders =
    Workflow.newActivityStub(OrderActivity.class,
      ActivityOptions.newBuilder()
        .setStartToCloseTimeout(Duration.ofSeconds(10))
        .build());

  @Override
  public void processCheckout(CheckoutRequest req) {
    String orderId = orders.createOrder(req);
    try {
      inventory.reserveStock(orderId, req.items());
      try {
        payment.charge(req.paymentMethod(),
                       req.amount());
      } catch (PaymentException e) {
        // Auto-compensate
        inventory.releaseStock(orderId);
        orders.cancelOrder(orderId);
        throw e;
      }
    } catch (InventoryException e) {
      orders.cancelOrder(orderId);
      throw e;
    }
  }
}
```

---

### ⚖️ Comparison Table

| Approach               | Consistency | Coupling              | Locking | Observability        | Best For                        |
| ---------------------- | ----------- | --------------------- | ------- | -------------------- | ------------------------------- |
| **Orchestration Saga** | Eventual    | Medium (orchestrator) | None    | High (state machine) | Complex multi-step flows        |
| **Choreography Saga**  | Eventual    | Low                   | None    | Low (distributed)    | Simple 2–3 step flows           |
| Two-Phase Commit (2PC) | Strong      | High                  | Heavy   | Medium               | Short, critical transactions    |
| Best-Effort (no saga)  | None        | None                  | None    | None                 | Idempotent read-only operations |

**How to choose:** Use **orchestration saga** for business flows with 3+ steps or complex compensation logic. Use **choreography** for simple event chains with clear ownership. Avoid 2PC in microservices — it violates service autonomy.

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                         |
| ----------------------------------------------------- | ------------------------------------------------------------------------------- |
| Saga provides the same consistency as ACID            | Saga provides eventual consistency — intermediate states are visible            |
| Compensating transactions are just database rollbacks | Compensations are application-level business logic, not DB-level rollbacks      |
| Choreography is always simpler than orchestration     | Choreography distributed state is harder to debug and monitor at scale          |
| Saga steps can be skipped if already compensated      | Idempotent compensation is required — same command may arrive multiple times    |
| The saga orchestrator is a single point of failure    | Orchestrator state is persisted; instances can failover without losing progress |

---

### 🚨 Failure Modes & Diagnosis

**Saga Stuck in COMPENSATING State**

**Symptom:** Orders show `status=COMPENSATING` permanently; inventory never released.

**Root Cause:** Compensation command failed and was not retried; or target service is down and message was not persisted.

**Diagnostic Command:**

```bash
# Find stuck sagas
SELECT saga_id, status, updated_at
FROM saga_states
WHERE status = 'COMPENSATING'
  AND updated_at < NOW() - INTERVAL '15 minutes'
ORDER BY updated_at;
```

**Fix:** Ensure compensation commands are published via Outbox Pattern for at-least-once delivery. Implement dead-letter queue for failed compensations.

**Prevention:** Saga compensation must be idempotent and retried with exponential backoff.

---

**Duplicate Compensation**

**Symptom:** Inventory released twice; order cancelled twice; customer receives two cancellation emails.

**Root Cause:** At-least-once message delivery triggered the compensation handler twice; handler not idempotent.

**Diagnostic Command:**

```bash
grep "ReleaseInventory" service.log | \
  awk '{print $5}' | sort | uniq -d
# Duplicates = duplicate compensation executions
```

**Fix:** All saga step handlers must be idempotent. Check if step already executed before re-executing.

**Prevention:** Use `IF NOT EXISTS` checks or saga step status tracking before executing each step.

---

**Missing Compensation for New Step**

**Symptom:** New feature added a step (loyalty points) to checkout saga; when payment fails, loyalty points are not reversed.

**Root Cause:** Compensation chain not updated when new saga step was added.

**Diagnostic Command:**

```bash
# Check loyalty points for cancelled orders
SELECT order_id, points_added FROM loyalty_ledger l
JOIN orders o ON l.order_id = o.id
WHERE o.status = 'CANCELLED'
  AND l.reversal_id IS NULL;
```

**Fix:** Add compensation step for loyalty points. Test full compensation path in integration tests.

**Prevention:** Every saga step addition requires a compensating step — enforced by code review checklist.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Distributed Transaction` — the problem sagas replace
- `Event-Driven Microservices` — event publishing mechanism used in choreography sagas
- `Choreography vs Orchestration` — the two implementation styles of saga

**Builds On This (learn these next):**

- `Outbox Pattern` — ensures saga events are reliably published
- `Event Sourcing in Microservices` — stores saga state as event log
- `Temporal (Workflow Orchestration)` — production saga framework with built-in durability

**Alternatives / Comparisons:**

- `Two-Phase Commit (2PC)` — strong consistency alternative; unsuitable for microservices at scale
- `CQRS in Microservices` — often combined with saga for read/write separation
- `Saga Pattern` (Design Patterns) — the canonical GoF-level pattern this extends

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Sequence of local transactions with       │
│              │ compensating rollback for each step       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-service transactions require ACID   │
│ SOLVES       │ without distributed locking               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Compensation is NOT a DB rollback — it is │
│              │ a business-level undo, defined in advance │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Business operation spans 2+ services with │
│              │ their own databases                       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-service operations or when strong  │
│              │ isolation is a hard requirement           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ No distributed locking vs temporary       │
│              │ inconsistency and compensation complexity │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Plan A with a pre-written Plan B for     │
│              │  every step"                              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Outbox Pattern → Temporal → Event Sourcing│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your checkout saga has 4 steps: CreateOrder, ReserveInventory, SendConfirmationEmail, ChargePayment. Payment fails at step 4. You compensate: step 3 compensation is "send cancellation email," step 2 is "release inventory," step 1 is "cancel order." The email service is down during compensation. Trace exactly: does the saga get stuck? What state is the order in? What does the customer see? How should the saga handle a failed compensation step?

**Q2.** You choose choreography over orchestration for your checkout saga to reduce coupling. Three months later, your team adds a loyalty points step between inventory reservation and payment. Describe exactly: how many services need code changes in choreography vs orchestration? How would a production incident look different in each (debugging, identifying stuck state, replaying failed saga)? What does this reveal about the long-term trade-off?
