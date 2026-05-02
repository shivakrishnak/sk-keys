---
layout: default
title: "Saga Pattern"
parent: "Distributed Systems"
nav_order: 609
permalink: /distributed-systems/saga-pattern/
number: "0609"
category: Distributed Systems
difficulty: ★★★
depends_on: Two-Phase Commit, Idempotency (Distributed), Choreography vs Orchestration, Event Sourcing
used_by: Microservices, Distributed Transactions, Order Processing, Choreography vs Orchestration
related: Two-Phase Commit, Outbox Pattern, Idempotency (Distributed), Event Sourcing, CQRS
tags:
  - distributed
  - transactions
  - microservices
  - pattern
  - deep-dive
---

# 609 — Saga Pattern

⚡ TL;DR — A saga replaces a distributed ACID transaction with a sequence of local transactions, each publishing an event or message; if any step fails, compensating transactions (roll-back actions) are executed in reverse order to undo completed steps — maintaining consistency without distributed locking.

| #609            | Category: Distributed Systems                                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Two-Phase Commit, Idempotency (Distributed), Choreography vs Orchestration, Event Sourcing |                 |
| **Used by:**    | Microservices, Distributed Transactions, Order Processing, Choreography vs Orchestration   |                 |
| **Related:**    | Two-Phase Commit, Outbox Pattern, Idempotency (Distributed), Event Sourcing, CQRS          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
"Place an order" requires: (1) reserve inventory, (2) charge customer, (3) create shipment, (4) send confirmation email — across 4 separate microservices with 4 separate databases. ACID transaction (2PC) would hold locks in all 4 DBs simultaneously, violating microservice isolation, hurting availability, and not working cross-technology (MySQL + Cassandra + Stripe API can't participate in the same 2PC). Without saga: no way to ensure all 4 steps either ALL complete or ALL roll back.

**THE BREAKING POINT:**
Two-Phase Commit (2PC) requires a coordinator that can synchronously lock all participating resources. In microservices: this creates tight coupling between services, reduces availability (any participant's unavailability blocks the commit), and doesn't work with third-party APIs (you can't 2PC with Stripe).

**THE INVENTION MOMENT:**
Hector Garcia-Molina and Kenneth Salem's 1987 paper "Sagas" proposed breaking long-running transactions into a sequence of shorter local transactions. If any step fails: run compensating transactions to semantically undo the completed steps. No distributed locks. Each service owns its own transaction.

---

### 📘 Textbook Definition

A **saga** is a sequence of local transactions `[T₁, T₂, ..., Tₙ]` where each Tᵢ updates a single service/database and publishes an event or message that triggers the next step. If Tᵢ fails or is cancelled, compensating transactions `[C_(i-1), C_(i-2), ..., C₁]` run in reverse order to semantically undo the effect of completed steps. **Key properties:**

- **ACD but not I**: Sagas provide Atomicity (all steps complete or all compensate), Consistency (business rules maintained throughout), Durability (completed steps are durable). They sacrifice **Isolation**: intermediate states are visible to other transactions.
- **Compensating transactions**: must semantically reverse the original operation. Some compensations are imperfect (e.g., "cancellation fee charged" is not a perfect reversal of "order placed").
- **Idempotency required**: each step and compensation must be idempotent — saga orchestrators may re-execute steps after crashes.
- **Two coordination strategies**: Choreography (event-driven, distributed) and Orchestration (centralized saga orchestrator).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A saga breaks a distributed transaction into steps; each step commits locally; if anything fails later, "undo" steps run in reverse to restore consistency.

**One analogy:**

> A saga is like booking a vacation package step-by-step: first book flights, then hotel, then rental car. If the rental car is unavailable (step 3 fails), you cancel the hotel (undo step 2) and cancel the flights (undo step 1). You don't hold a "lock" on flights and hotel while checking rental car availability — you commit each booking and cancel if subsequent steps fail. The cancellation fees are the "imperfect compensation" of real sagas.

**One insight:**
Sagas are semantically consistent but NOT isolated. Between T₂ committing and C₂ running (during a failure scenario), other transactions might read the intermediate state (inventory reserved but order ultimately cancelled). This is called a **dirty read at the saga level** and must be handled by designing compensating transactions that account for the possibility that state was observed and acted upon between steps.

---

### 🔩 First Principles Explanation

**SAGA SEQUENCE (ORDER PROCESSING):**

```
Step 1: T₁ — OrderService: CREATE order (status=PENDING)
Step 2: T₂ — InventoryService: RESERVE items (items marked reserved)
Step 3: T₃ — PaymentService: CHARGE customer (charge $150)
Step 4: T₄ — ShippingService: CREATE shipment (tracking number generated)
Step 5: T₅ — NotificationService: SEND confirmation email

If Step 3 (payment) fails:
  C₂ — InventoryService: RELEASE reservation (items unmarked reserved)
  C₁ — OrderService: CANCEL order (status=CANCELLED)

If Step 4 (shipping) fails:
  C₃ — PaymentService: REFUND customer ($150 refunded)
  C₂ — InventoryService: RELEASE reservation
  C₁ — OrderService: CANCEL order

Compensation does NOT undo T₃'s effects in the DB — it creates a new
row/event that semantically reverses the business effect:
  PaymentService: INSERT INTO charges (type=REFUND, amount=150, ref=original_charge_id)
  Not: DELETE FROM charges WHERE id = ... (that would destroy audit history)
```

**CHOREOGRAPHY SAGA (EVENT-DRIVEN):**

```
OrderService creates order → publishes OrderCreated event
↓
InventoryService consumes OrderCreated → reserves items → publishes ItemsReserved
↓
PaymentService consumes ItemsReserved → charges customer → publishes PaymentCharged
↓
ShippingService consumes PaymentCharged → creates shipment → publishes ShipmentCreated
↓
NotificationService consumes ShipmentCreated → sends email → saga complete

IF PaymentService fails:
PaymentService publishes PaymentFailed event
↓
InventoryService consumes PaymentFailed → releases reservation → publishes ItemsReleased
↓
OrderService consumes ItemsReleased → cancels order → saga complete (failed path)

No central coordinator. Each service knows its own step and its compensation.
```

**ORCHESTRATION SAGA (CENTRALIZED COORDINATOR):**

```java
@Service
public class OrderSagaOrchestrator {

    public void executeOrderSaga(OrderRequest req) {
        SagaState state = new SagaState(req.getOrderId());

        try {
            // Step 1:
            orderClient.createOrder(req.getOrderId(), req); // T₁
            state.markStep("order_created");

            // Step 2:
            inventoryClient.reserve(req.getOrderId(), req.getItems()); // T₂
            state.markStep("inventory_reserved");

            // Step 3:
            paymentClient.charge(req.getOrderId(), req.getAmount()); // T₃
            state.markStep("payment_charged");

            // Step 4:
            String trackingNo = shippingClient.createShipment(req.getOrderId()); // T₄
            state.markStep("shipment_created", trackingNo);

            // All steps complete: saga succeeds

        } catch (PaymentException e) {
            // Compensate completed steps in reverse:
            compensate(state);
        }
    }

    private void compensate(SagaState state) {
        if (state.hasStep("inventory_reserved")) {
            inventoryClient.release(state.getOrderId()); // C₂
        }
        if (state.hasStep("order_created")) {
            orderClient.cancel(state.getOrderId()); // C₁
        }
    }
}
```

**SAGA CRASH RECOVERY (ORCHESTRATOR):**

```
Orchestrator crashes AFTER T₂ (inventory reserved) but BEFORE T₃ (payment).
On restart: orchestrator reads SagaState from persistent store.
  state = {"order_id": "123", "steps": ["order_created", "inventory_reserved"]}

Because orchestrator crashed mid-saga (incomplete saga with no terminal state):
  Option A: Resume forward (retry from T₃ with idempotency key for T₂).
  Option B: Compensate backward (run C₂, C₁) and mark saga as FAILED.

Typical policy: retry forward N times; if all retries fail: compensate.
All T operations and all C operations must be IDEMPOTENT (re-runnable on restart).
```

---

### 🧪 Thought Experiment

**THE LOST UPDATE ANOMALY IN SAGAS:**

Saga 1: Reserve items → Charge → Ship (for customer Alice, 5 units).
Saga 2: Reserve items → Charge → Ship (for customer Bob, 3 units).

Timeline (parallel execution):
T=0: Saga1 T₂ — reserves 5 units (inventory: 8 → 3 remaining).
T=1: Saga2 T₂ — reserves 3 units (inventory: 3 → 0 remaining).
T=2: Saga1 T₃ — payment FAILS. C₂ runs: releases 5 units (inventory: 0 → 5).
T=3: Saga2 T₃ — payment succeeds. T₄ runs. Shipment sent (3 units).
T=4: Saga1's C₂ released 5 units back — but at T=3, Bob's shipment already consumed 3. Final: inventory = 5 - 3 = 2 units. Correct.

But what if Saga2's T₃ ran at T=1.5, AFTER Saga1's T₂ but BEFORE Saga1's C₂?
Saga2's T₃ charged Bob. Shipment created. Meanwhile, Saga1 cancels.
No problem: Saga1's cancellation returns 5 units to inventory after Saga2 already consumed 3. Final state is consistent.

**The dangerous scenario**: if your inventory reservation is "soft" (advisory, not database-enforced), and the inventory service doesn't enforce atomicity via DB constraints, concurrent sagas can both believe they reserved items when there aren't enough. This is the "phantom reservation" problem. Solution: inventory reservation must use an atomic DB operation (UPDATE inventory SET reserved = reserved + 5 WHERE available >= 5).

---

### 🧠 Mental Model / Analogy

> Saga is like a relay race with a "undo" anchor leg. If any runner drops the baton, instead of calling the race off and starting from scratch, you run the relay backwards (compensations) — each runner returns to their starting position. The race is "cancelled" only once everyone is back at the start. The key: each compensation must reliably bring each runner back to start, even if other things happened between the forward run and the backward compensation.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Saga = sequence of steps. If any step fails, run undo steps in reverse. No distributed locks. Each service commits locally.

**Level 2:** Choreography (events drive flow, decentralized) vs. Orchestration (central coordinator drives flow). Compensating transactions must be idempotent. Saga provides ACD but not Isolation — intermediate states are visible.

**Level 3:** Saga state machine: RUNNING, COMPLETED, COMPENSATING, FAILED. Orchestrator must persist saga state to survive crashes (in Temporal, Axon, or custom saga table). The Outbox Pattern solves the dual-write problem: write saga event to DB in same transaction as business state change, then publish from outbox to message broker.

**Level 4:** Countermeasures for saga isolation violations: (1) Semantic lock: mark a record as "saga in progress" (e.g., `order.status=PENDING`) so other sagas treat it as locked; (2) Commutative updates: ensure operations and compensations are commutative so order of concurrent sagas doesn't matter; (3) Re-read: before compensation, re-read current state and only compensate if still in expected state. Saga frameworks: Temporal.io (workflow-as-code, handles saga persistence, retries, compensations automatically), Axon Framework (Java, event sourcing + CQRS + saga), AWS Step Functions (managed orchestration, supports saga with error handling).

---

### ⚙️ How It Works (Mechanism)

**Temporal Saga (Go):**

```go
func OrderSagaWorkflow(ctx workflow.Context, order Order) error {
    // Each activity runs as a durable step; Temporal handles retry + persistence.

    defer func() {
        if r := recover(); r != nil {
            // Compensation runs in defer if workflow PANICS:
            workflow.ExecuteActivity(ctx, CancelOrderActivity, order.ID).Get(ctx, nil)
        }
    }()

    // Forward transactions:
    err := workflow.ExecuteActivity(ctx, CreateOrderActivity, order).Get(ctx, nil)
    if err != nil { return compensate(ctx, order, err) }

    err = workflow.ExecuteActivity(ctx, ReserveInventoryActivity, order).Get(ctx, nil)
    if err != nil { return compensate(ctx, order, err) }

    err = workflow.ExecuteActivity(ctx, ChargePaymentActivity, order).Get(ctx, nil)
    if err != nil { return compensate(ctx, order, err) }

    return nil  // Success
}

func compensate(ctx workflow.Context, order Order, originalErr error) error {
    // Run compensations in reverse:
    workflow.ExecuteActivity(ctx, ReleaseInventoryActivity, order.ID).Get(ctx, nil)
    workflow.ExecuteActivity(ctx, CancelOrderActivity, order.ID).Get(ctx, nil)
    return originalErr
}
```

---

### ⚖️ Comparison Table

| Property         | 2PC                                         | Saga                                      |
| ---------------- | ------------------------------------------- | ----------------------------------------- |
| Atomicity        | Yes (all-or-nothing)                        | Semantic (compensations may be imperfect) |
| Isolation        | Yes (locks across participants)             | No (intermediate states visible)          |
| Cross-technology | No (requires XA support)                    | Yes (any tech that can publish events)    |
| Availability     | Low (coordinator + all participants needed) | High (steps independent)                  |
| Compensations    | Automatic rollback                          | Manual compensating transactions          |
| Latency          | High (multiple round trips + locks)         | Lower (async between steps)               |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                                              |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Saga rollback is the same as DB rollback  | DB rollback reverts to pre-transaction state. Saga compensation creates a new offsetting operation. Side effects (emails sent, charges made) between steps may be visible and partially irreversible |
| Saga guarantees full isolation            | Sagas explicitly do NOT guarantee isolation. Other transactions may read intermediate states. Plan for this with semantic locks or countermeasures                                                   |
| Choreography is better than orchestration | Choreography scales better; Orchestration is easier to understand and debug. Choose based on team size and complexity of the saga, not dogma                                                         |

---

### 🚨 Failure Modes & Diagnosis

**Compensating Transaction Failure (Compensation Saga Stuck)**

Symptom: Order stuck in `COMPENSATING` state. Logs show compensation C₂ (inventory
release) has been retried 20 times and failing with "item not found" — inventory service
was since redeployed and item IDs changed.

Cause: Compensation is not idempotent, and the target state has changed since the
original reservation (inventory service schema migration).

Fix: (1) Compensations must never throw on "already compensated" — treat it as success.
(2) Compensations should work with the ID captured at compensation time (stored in saga
state), not inferred from current system state. (3) For permanently failed compensations:
saga moves to `STUCK` state, triggers human-review queue (payment team reviews manually).
(4) Build a "saga admin UI" to view stuck sagas and approve/reject manual compensations.

---

### 🔗 Related Keywords

- `Two-Phase Commit` — the alternative to saga; provides isolation but requires distributed lock
- `Choreography vs Orchestration` — the two coordination strategies for sagas
- `Outbox Pattern` — solves dual-write problem when publishing saga events
- `Idempotency (Distributed)` — required for every saga step and compensation
- `Event Sourcing` — often used with sagas for complete audit trail of state transitions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  SAGA: sequence of local txns + compensations            │
│  Forward path: T₁ → T₂ → ... → Tₙ                       │
│  Compensation path: Cₙ₋₁ → ... → C₂ → C₁ (on failure)  │
│  ACD but NOT Isolated: intermediate state visible        │
│  Choreography: event-driven, decentralized               │
│  Orchestration: central coordinator                      │
│  Every step must be idempotent (crash recovery)          │
│  Frameworks: Temporal, Axon, AWS Step Functions          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A hotel booking saga: T₁=reserve room, T₂=charge credit card, T₃=send confirmation. The saga succeeds through T₃. 10 minutes later, the hotel's system reports the room was double-booked (it was reserved by another saga that ran concurrently). The saga is "complete" but the business invariant (unique room reservation) is violated. What saga countermeasure would prevent this? How does it interact with the fact that sagas don't provide isolation?

**Q2.** Compare the saga approach to the 2PC approach for a "transfer funds between two bank accounts" use case. Account A and Account B are in different bank systems (Bank X and Bank Y). (a) Why is 2PC impractical here? (b) Design a saga for this transfer. (c) What happens if the debit from Account A succeeds but the credit to Account B fails 3 times? (d) What is the user-visible state during the compensation phase?
