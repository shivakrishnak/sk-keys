---
id: DPT-054
title: Saga Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-053
used_by: DPT-064, DPT-065
related: DPT-052, DPT-053, DPT-060, DPT-085
tags:
  - pattern
  - distributed-systems
  - advanced
  - distributed-transactions
  - event-driven
  - compensation
  - choreography
  - orchestration
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/design-patterns/saga-pattern/
---

⚡ TL;DR - The Saga Pattern manages long-running distributed
transactions across multiple microservices by breaking
the transaction into a sequence of local transactions,
each with a compensating transaction that undoes its
effect if a later step fails.

| #54 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-053 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-052, DPT-053, DPT-060, DPT-085 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT SAGA:**
Placing an order in a microservices architecture requires:
1. Reserve inventory (Inventory Service)
2. Charge customer (Payment Service)
3. Create shipment (Shipping Service)

In a monolith: one `@Transactional` method, all three
steps atomic. Either all succeed or all roll back.

In microservices: three services, three databases.
No distributed transaction (two-phase commit: too slow,
too brittle). Without Saga:
- Step 1 succeeds: inventory reserved.
- Step 2 succeeds: customer charged.
- Step 3 fails: shipment cannot be created.
- Result: inventory reserved, customer charged, no shipment.
- Customer is billed for an order that will never arrive.

**THE PROBLEM:**
Distributed systems cannot use ACID transactions across
service boundaries. Yet many business operations require
multiple services to either ALL succeed or ALL fail.

**THE INVENTION MOMENT:**
Accept that distributed atomicity is not achievable.
Instead: design each step to be reversible. If step N
fails, execute compensating transactions for steps N-1,
N-2, ... 1 in reverse order to undo their effects.

---

### 📘 Textbook Definition

The **Saga Pattern** is a design pattern for managing
distributed transactions in microservices architectures.
A Saga is a sequence of local transactions:
1. Each step executes a local transaction on one service.
2. Each step publishes an event or message upon completion.
3. Each step has a **compensating transaction** that
   reverses its effect.
4. If any step fails, the saga executes compensating
   transactions for all previously completed steps in
   reverse order.

**Two coordination styles:**
- **Choreography**: services react to events. No central
  coordinator. Each service listens for events and
  decides what to do.
- **Orchestration**: a central saga orchestrator sends
  commands to services and tracks progress.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Saga = distributed transaction = sequence of local transactions
with compensating transactions for rollback.

**One analogy:**
> Booking a trip: flight, hotel, car rental (3 services).
> Choreography: Book flight → "flight booked" event →
> Book hotel → "hotel booked" event → Book car.
> If car fails: "car failed" event → cancel hotel →
> cancel flight. Each service knows how to undo its action.
>
> Orchestration: a travel agent (orchestrator) calls
> each service in sequence: "book flight," "book hotel,"
> "book car." If car fails, the agent calls "cancel hotel"
> then "cancel flight." The agent has the full view.

---

### 🔩 First Principles Explanation

**WHY DISTRIBUTED TRANSACTIONS FAIL:**
Two-phase commit (2PC) provides distributed atomicity
but requires all services to be available during the
commit phase. One service is slow or down: all others
block. This is incompatible with microservices resilience
requirements.

**THE SAGA SOLUTION:**
- Accept eventual consistency across service boundaries.
- Each service maintains its own consistency locally.
- Cross-service consistency is achieved through compensating
  transactions (semantic rollback).

**COMPENSATING TRANSACTIONS:**
A compensating transaction reverses the business effect
of a step. Not always a database rollback:
- "Reserve inventory" → compensating: "release reservation"
- "Charge customer" → compensating: "issue refund"
- "Create shipment" → compensating: "cancel shipment"

Some operations are not reversible (sending an email).
For these, "compensating" means sending a correction
(a cancellation email). Saga requires all steps to have
defined semantics for failure.

**CHOREOGRAPHY vs ORCHESTRATION:**

**Choreography pros:**
- Loose coupling: services don't know about each other
- No single point of failure
- Easy to add new services to the saga

**Choreography cons:**
- Hard to trace: no central view of saga state
- Cyclic dependencies can emerge
- Adding a new step: change multiple services

**Orchestration pros:**
- Central visibility: orchestrator tracks full saga state
- Easier to change flow: only orchestrator changes
- Clearer failure handling

**Orchestration cons:**
- Orchestrator is a new service to build and maintain
- Orchestrator can become a bottleneck or single point of failure
- Tighter coupling to the orchestrator

---

### 🧪 Thought Experiment

**ORDER PLACEMENT SAGA (Orchestration):**

Happy path:
1. Orchestrator → `ReserveInventory` → Inventory Service
   → `InventoryReserved` ✓
2. Orchestrator → `ChargePayment` → Payment Service
   → `PaymentCharged` ✓
3. Orchestrator → `CreateShipment` → Shipping Service
   → `ShipmentCreated` ✓
4. Saga complete. Order confirmed.

Failure path (shipment fails):
1. `ReserveInventory` ✓
2. `ChargePayment` ✓
3. `CreateShipment` FAILS → shipping service returns error
4. Orchestrator executes compensating transactions:
   - `RefundPayment` → Payment Service ✓
   - `ReleaseInventoryReservation` → Inventory Service ✓
5. Saga failed with clean compensation.

**WHAT IF A COMPENSATING TRANSACTION FAILS?**
This is the hardest case. If `RefundPayment` fails: retry
with exponential backoff. After N retries: put the saga
in a "stuck" state and alert operations. A human reviews
and manually issues the refund. Saga Pattern does not
eliminate the need for human intervention in extreme
failure cases; it minimizes them.

---

### 🧠 Mental Model / Analogy

> Saga Pattern is the "undo history" model.
> A word processor maintains an undo history.
> Every action is recorded. Ctrl+Z executes the most
> recent action's undo. Multiple Ctrl+Z: multiple undos
> in reverse order.
>
> Saga maintains the execution history of distributed
> steps. If step N fails, it executes undo (compensating
> transaction) for step N-1, then N-2, then ... 1.
> Each step's "undo" must be defined by the service
> that owns that step. The orchestrator (or choreography)
> manages the sequence; each service manages its own undo.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Saga Pattern replaces a distributed transaction with
a sequence of local transactions, where each step can
be undone if a later step fails. Instead of atomic
all-or-nothing: try-and-compensate.

**Level 2 - The two styles:**
Choreography: services talk to each other via events.
Simple to start but hard to trace. Orchestration:
a coordinator sends commands and handles the sequence.
More visible, more centralized.

**Level 3 - Designing compensating transactions:**
Every step must have a defined compensating transaction.
Design compensating transactions when designing the step.
"What must be undone if this step succeeded but a later
step failed?" Not all operations have clean compensations
(email already sent); accept this as a saga limitation
and design for "best effort" compensation.

**Level 4 - Idempotency and at-least-once:**
Saga commands are usually published via the Outbox Pattern
(DPT-053). Services receive commands at-least-once.
All saga steps must be idempotent: receiving the same
command twice produces the same result as receiving
it once. Use command IDs as idempotency keys.

**Level 5 - Saga state machine:**
A saga is a distributed state machine. The orchestrator's
state machine defines: valid transitions, compensation
paths, and terminal states (succeeded, compensated,
stuck). Implement using a workflow engine (Temporal,
Camunda, AWS Step Functions) for complex sagas with
many steps, retries, and timeouts. For simple sagas:
a custom state table in the database is sufficient.

---

### ⚙️ How It Works (Mechanism)

```
Order Placement Saga (Orchestration Style)

STATE MACHINE:
┌─────────────────────────────────────────────────────────┐
│ PENDING → INVENTORY_RESERVED → PAYMENT_CHARGED          │
│        → SHIPMENT_CREATED → COMPLETED                   │
│                                                         │
│ On SHIPMENT_FAILED:                                     │
│ SHIPMENT_CREATED → PAYMENT_REFUNDED                     │
│               → INVENTORY_RELEASED → COMPENSATED        │
│                                                         │
│ On PAYMENT_FAILED:                                      │
│ PAYMENT_CHARGED → INVENTORY_RELEASED → COMPENSATED      │
└─────────────────────────────────────────────────────────┘

ORCHESTRATOR FLOW:
┌─────────────────────────────────────────────────────────┐
│ 1. Receive PlaceOrderRequest                            │
│ 2. Create Saga record (state=PENDING)                   │
│ 3. Send ReserveInventoryCommand → Inventory Service     │
│ 4. Receive InventoryReservedEvent                       │
│    → Update saga state=INVENTORY_RESERVED               │
│ 5. Send ChargePaymentCommand → Payment Service          │
│ 6. Receive PaymentChargedEvent                          │
│    → Update saga state=PAYMENT_CHARGED                  │
│ 7. Send CreateShipmentCommand → Shipping Service        │
│ 8a. Receive ShipmentCreatedEvent → state=COMPLETED ✓   │
│ 8b. Receive ShipmentFailedEvent → start compensation    │
│     → Send RefundPaymentCommand                         │
│     → Send ReleaseInventoryCommand                      │
│     → state=COMPENSATED                                 │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Choreography saga:**

```java
// CHOREOGRAPHY: services react to events

// OrderService publishes event after order creation:
@Transactional
public Order placeOrder(OrderRequest req) {
    Order order = orderRepo.save(new Order(req));
    // Outbox Pattern: event written to DB in same TX
    outboxRepo.save(new OutboxRecord(
        "OrderCreated", toJson(new OrderCreatedEvent(order))));
    return order;
}

// InventoryService reacts to OrderCreated:
@KafkaListener(topics = "OrderCreated")
@Transactional
public void onOrderCreated(OrderCreatedEvent event) {
    boolean reserved = inventory.reserve(event.getItems());
    if (reserved) {
        // Trigger next step
        outboxRepo.save(new OutboxRecord(
            "InventoryReserved", toJson(
                new InventoryReservedEvent(event.getOrderId()))));
    } else {
        // Trigger compensation
        outboxRepo.save(new OutboxRecord(
            "InventoryReservationFailed", toJson(
                new InventoryReservationFailedEvent(
                    event.getOrderId()))));
    }
}

// PaymentService reacts to InventoryReserved:
@KafkaListener(topics = "InventoryReserved")
public void onInventoryReserved(InventoryReservedEvent event) {
    // Charge payment...
}

// OrderService reacts to InventoryReservationFailed (compensation):
@KafkaListener(topics = "InventoryReservationFailed")
@Transactional
public void onInventoryFailed(InventoryReservationFailedEvent e) {
    Order order = orderRepo.findById(e.getOrderId()).orElseThrow();
    order.fail("Inventory unavailable");
    orderRepo.save(order);
}
```

**Example 2 - Orchestration saga state tracking:**

```java
// ORCHESTRATION: central saga coordinator

@Entity @Table(name = "order_sagas")
class OrderSaga {
    @Id String orderId;
    @Enumerated(EnumType.STRING)
    SagaState state;  // PENDING, INVENTORY_RESERVED, ...
    LocalDateTime startedAt;
    LocalDateTime updatedAt;
}

@Service class OrderSagaOrchestrator {
    @Autowired OrderSagaRepository sagaRepo;
    @Autowired OutboxRepository outboxRepo;

    @Transactional
    public void startSaga(String orderId) {
        OrderSaga saga = new OrderSaga(orderId, PENDING);
        sagaRepo.save(saga);
        // Send first command via Outbox
        outboxRepo.save(new OutboxRecord(
            "ReserveInventory",
            toJson(new ReserveInventoryCommand(orderId))));
    }

    @Transactional
    @EventListener
    public void onInventoryReserved(InventoryReservedEvent e) {
        OrderSaga saga =
            sagaRepo.findById(e.getOrderId()).orElseThrow();
        saga.setState(INVENTORY_RESERVED);
        sagaRepo.save(saga);
        // Send next command
        outboxRepo.save(new OutboxRecord(
            "ChargePayment",
            toJson(new ChargePaymentCommand(e.getOrderId()))));
    }

    @Transactional
    @EventListener
    public void onShipmentFailed(ShipmentFailedEvent e) {
        OrderSaga saga =
            sagaRepo.findById(e.getOrderId()).orElseThrow();
        saga.setState(COMPENSATING);
        sagaRepo.save(saga);
        // Start compensation
        outboxRepo.save(new OutboxRecord(
            "RefundPayment",
            toJson(new RefundPaymentCommand(e.getOrderId()))));
    }
}
```

---

### ⚖️ Choreography vs Orchestration

| Aspect | Choreography | Orchestration |
|---|---|---|
| Coupling | Loose (events) | Tighter (to orchestrator) |
| Visibility | Hard to trace | Central view |
| Failure handling | Distributed | Centralized |
| Adding new step | Change multiple services | Change orchestrator only |
| State tracking | No single state store | Saga state in orchestrator |
| Complexity | Low initially, grows fast | Higher initial, scales better |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Saga provides the same guarantees as ACID | Saga provides eventual consistency, not isolation. A partially-executed saga is visible to other sagas. This can cause anomalies (e.g., another saga sees the inventory reserved before compensation completes). Design for this |
| Compensating transactions are always "undo" | Some effects cannot be truly undone (email sent, message published). Compensation for these is semantic: sending a "cancellation" email. Design compensation early |
| Orchestration is always better than choreography | Each has trade-offs. Choreography works well for simple 2-3 step sagas. Orchestration is better for complex flows with many steps and complex failure paths |
| Using a saga means you don't need transactions | Local transactions within each service are still critical. The saga coordinates across service boundaries; each step must be locally ACID |

---

### 🚨 Failure Modes & Diagnosis

**Stuck Saga (Compensation Loop)**

**Symptom:**
A saga has been in `COMPENSATING` state for hours.
Alerts fire on the saga timeout.

**Root Cause:**
A compensating transaction is failing and being retried
indefinitely. Common cause: the Payment Service's refund
endpoint is down.

**Diagnosis:**
```sql
-- Find stuck sagas
SELECT order_id, state, updated_at
FROM order_sagas
WHERE state = 'COMPENSATING'
  AND updated_at < NOW() - INTERVAL '1 hour';
```
Check outbox for unprocessed compensation commands.
Check Payment Service health.

**Fix:**
Set a max retry count for compensation commands. After
exhausting retries: move saga to `STUCK` state, alert
operations. Manual intervention required. This is the
expected behavior for unrecoverable failures.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Distributed transaction = sequence of    │
│              │ local transactions + compensating txns   │
├──────────────┼──────────────────────────────────────────┤
│ CHOREOGRAPHY │ Services react to events, no coordinator │
│              │ Loose coupling, hard to trace            │
├──────────────┼──────────────────────────────────────────┤
│ ORCHESTRATION│ Central coordinator sends commands       │
│              │ Full visibility, easier to change        │
├──────────────┼──────────────────────────────────────────┤
│ KEY DESIGN   │ Every step needs a compensating txn      │
│              │ Define compensation BEFORE building step │
├──────────────┼──────────────────────────────────────────┤
│ REQUIRES     │ Idempotent steps + Outbox Pattern for    │
│              │ reliable event publishing                │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-055: Strangler Fig Pattern           │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Saga = distributed transaction without 2PC. Sequence of
   local transactions. If any step fails, run compensating
   transactions for all previous steps in reverse order.
2. Two styles: Choreography (services react to events,
   decoupled but hard to trace) vs Orchestration (central
   coordinator, visible state, easier to change the flow).
3. Every step MUST have a defined compensating transaction.
   Design it at the same time as the forward step. "What
   do I do if this succeeded but a later step failed?"

