---
id: SYD-062
title: Saga Pattern
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-057, SYD-060
used_by: ""
related: SYD-057, SYD-060, SYD-058, SYD-033
tags:
  - architecture
  - saga
  - distributed-transactions
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 62
permalink: /syd/saga-pattern/
---

# SYD-062 - Saga Pattern

⚡ TL;DR - The Saga pattern manages distributed transactions
across multiple microservices without a two-phase commit
(2PC). A saga is a sequence of local transactions, each
publishing an event or message that triggers the next step.
If any step fails, the saga executes compensating transactions
to undo the completed steps. Two implementations:
Choreography (services react to events, no central
coordinator) and Orchestration (a central saga orchestrator
sends commands and tracks state). Key trade-off: eventual
consistency instead of ACID across services.

| #062 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event-Driven Architecture, Circuit Breaker | |
| **Related:** | Event-Driven Architecture, Circuit Breaker, CQRS, Database Internals | |

---

### 🔥 The Problem This Solves

An e-commerce order spans 4 services: Order, Inventory,
Payment, Shipping. To place an order:
1. Create order record (Order service)
2. Reserve inventory (Inventory service)
3. Process payment (Payment service)
4. Create shipment (Shipping service)

If Payment fails after Inventory was reserved:
- Inventory is reserved for an order that will never ship
- This is an inconsistent state across services

Traditional solution (2PC - two-phase commit): all 4
services participate in a distributed transaction. But:
2PC requires a transaction coordinator, locks resources
across services during the transaction (blocking), and
is a single point of failure. Microservices cannot use
2PC across independent databases.

Saga solution: each step is a local transaction; if any
step fails, compensating transactions undo prior steps.

---

### 📘 Textbook Definition

**Saga:** A pattern for managing data consistency across
microservices in distributed transaction scenarios.
A saga is a sequence of local transactions. Each local
transaction updates a single service's data and either
triggers the next step (via event or command) or triggers
a compensating transaction if the step fails.

**Compensating transaction:** An action that reverses
the effect of a previously completed step. Not literally
an undo (which would require database rollback across
services); instead, a business-level reversal (e.g.,
release reserved inventory, refund payment).

**Choreography saga:** No central coordinator. Each
service listens for events and reacts. Decentralized.
Harder to visualize the overall flow.

**Orchestration saga:** A central orchestrator (saga
manager) explicitly sends commands to each service and
tracks the saga state. Easier to visualize and debug,
but the orchestrator is a central bottleneck.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sequence of local transactions + compensating transactions
on failure. No distributed lock. Eventually consistent.

**One analogy:**
> Booking a multi-leg international trip:
> Step 1: Book flight A (confirmed).
> Step 2: Book connecting flight B (confirmed).
> Step 3: Book hotel (FAILS - unavailable).
>
> Compensating transactions:
> Cancel hotel booking attempt.
> Cancel flight B.
> Cancel flight A.
>
> Each booking was a real, committed transaction.
> The "rollback" is a new set of real cancellations.
> No single lock held all bookings at once.
> Eventually consistent: there may be a moment where
> flight A is booked but hotel is not.

**One insight:**
Sagas trade ACID consistency for availability and
scalability. The system will eventually reach a consistent
state (either all steps succeed, or all are compensated),
but during execution there are intermediate inconsistent
states. Design your system to handle these gracefully
(e.g., a user cannot pay for an order that has no
inventory reserved).

---

### 🔩 First Principles Explanation

**CHOREOGRAPHY SAGA:**
```
No central coordinator. Services react to events.

Happy path (order placement):
  1. Order Service: creates order (PENDING)
     publishes: OrderCreated
  
  2. Inventory Service: receives OrderCreated
     reserves inventory
     publishes: InventoryReserved (success)
     or: InventoryReservationFailed (failure)
  
  3. Payment Service: receives InventoryReserved
     charges card
     publishes: PaymentProcessed (success)
     or: PaymentFailed (failure)
  
  4. Shipping Service: receives PaymentProcessed
     creates shipment
     publishes: ShipmentCreated

Failure compensation:
  3. PaymentFailed is published.
  
  Inventory Service: receives PaymentFailed
    releases inventory (compensating transaction)
  
  Order Service: receives PaymentFailed
    updates order status: CANCELLED

Pro: no central coordinator; very scalable.
Con: hard to trace the overall flow; hard to add new steps;
  each service must know which events to compensate on.
```

**ORCHESTRATION SAGA:**
```
Central OrderSagaOrchestrator manages the flow.

Happy path:
  1. Client calls: OrderSagaOrchestrator.startOrderSaga()
  
  2. Orchestrator: send ReserveInventory command to Inventory
     wait for InventoryReserved / InventoryFailed
  
  3. If InventoryReserved:
     send ProcessPayment command to Payment
     wait for PaymentProcessed / PaymentFailed
  
  4. If PaymentProcessed:
     send CreateShipment command to Shipping
     wait for ShipmentCreated
  
  5. If ShipmentCreated:
     update order: CONFIRMED
     return success

Failure compensation:
  4. PaymentFailed received.
  
  Orchestrator: 
    send ReleaseInventory command (compensate step 2)
    wait for InventoryReleased
    update order: CANCELLED
    return failure

Pro: the entire flow is in one place (orchestrator).
     Easy to visualize and debug.
     Easy to add new steps.
Con: orchestrator is a central bottleneck and SPF.
     Requires persistent state for the orchestrator.
```

**COMPENSATING TRANSACTIONS:**
```
Compensating transactions must be:
  1. Idempotent: safe to run multiple times.
     ReleaseInventory for order 123 can run twice
     without double-releasing.
     
  2. Non-reversible: some actions cannot be compensated.
     An email was sent: cannot unsend. Design around this:
     send email AFTER the saga completes (last step).
  
  3. Retryable: compensations may fail. Retry with
     exponential backoff until all compensations complete.
     
Critical: saga completion must be guaranteed.
  Either ALL forward steps complete, or ALL compensations run.
  Use persistent saga state: track which steps are done.
  On failure/restart: resume from last known state.
```

---

### 🧪 Thought Experiment

**SAGA STATE PERSISTENCE**

Saga orchestrator crashes mid-way through an order saga.
Order is in state: inventory reserved, payment not yet
charged. On restart: the orchestrator must know:
- Which saga was in progress?
- Which step completed?
- Which step to retry or compensate?

Without persistent saga state: orphaned reserved
inventory (never released). Permanently inconsistent.

With persistent saga state (database per orchestrator):
```
saga_state table:
saga_id | step | status | created_at | updated_at
xyz123  |  2   | DONE   | ...        | ...
xyz123  |  3   | PENDING| ...        | ...

On crash and restart:
  Load all PENDING sagas.
  Resume from last committed step.
  Retry step 3 (ProcessPayment).
```

This is why orchestration sagas are often easier to
implement correctly: the state machine is centralized
and explicitly persisted. Choreography sagas distribute
state across services, making recovery harder to reason
about.

---

### 🧠 Mental Model / Analogy

> A saga is like a contractor hiring subcontractors
> for a home renovation:
>
> Step 1: Electrician rewires the kitchen. Done.
> Step 2: Plumber reroutes pipes. Done.
> Step 3: Cabinet installer tries to install.
>         PROBLEM: wrong measurements.
>
> Compensation (cannot simply undo physical work):
>   Cabinet installer cancels order (compensating tx).
>   Plumber patches back (compensating tx).
>   Electrician reverses wiring (compensating tx).
>
> Each step was a real, completed action.
> "Rollback" is a new set of real compensating actions.
> No single contractor held a lock on the whole house.
>
> Choreography: subcontractors coordinate by calling each
> other (event-based).
> Orchestration: the contractor (saga manager) calls each
> subcontractor in sequence and tracks progress.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A saga is a way to handle multi-step business processes
(like placing an order) across multiple services. If any
step fails, it automatically undoes the previous steps
using "compensating actions" (like releasing reserved
inventory or refunding a payment).

**Level 2 - How to use it (junior developer):**
Choreography: each service publishes events when it
succeeds or fails; other services react. Orchestration:
a central saga orchestrator sends commands and tracks
state. Both use compensating transactions on failure.

**Level 3 - How it works (mid-level engineer):**
Saga state persisted in a database. Each step: execute,
record step as complete, publish event/command for next
step. On failure: execute compensating transactions for
all completed steps (in reverse order). Compensations
must be idempotent. Use event-driven delivery (Kafka)
for saga steps to ensure at-least-once delivery.

**Level 4 - Why it was designed this way (senior/staff):**
Sagas exist because 2PC cannot span independent databases
in microservices (requires synchronized XA transactions,
locking resources, tight coupling, single transaction
coordinator). Sagas replace ACID with BASE: eventually
consistent outcomes. The trade-off is explicit intermediate
states. The system designer must answer: "What happens
if the user sees a partially-completed state?" Often
the answer is: show "order processing" (pending state)
until the saga completes. Orchestration vs. choreography
is a real trade-off: choreography is more scalable and
decoupled; orchestration is easier to implement correctly
with compensations. Most teams start with orchestration.

**Level 5 - Mastery (distinguished engineer):**
Amazon (Vogels, 2007) describes the Order Saga as the
canonical example of distributed transaction management
without 2PC. The key insight: for business workflows,
eventual consistency is acceptable because business
operations are naturally temporal (an order "processing"
is a valid business state, not a failure). The challenge
is correctness: ensuring compensations always run
completely. Tools like AWS Step Functions, Temporal.io,
and Axon Framework provide durable saga orchestration:
the orchestrator state is persisted automatically, and
the system automatically retries failed steps and
compensations. For high-volume payment systems (Stripe,
Klarna): sagas underpin every payment flow, with idempotency
keys preventing double-charging on compensation retries.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ ORCHESTRATION SAGA: ORDER PLACEMENT                 │
│                                                      │
│ Client → POST /orders → Saga Orchestrator           │
│                                                      │
│ Step 1: Orchestrator → ReserveInventory → Inventory │
│         Inventory: reserve, return InventoryReserved│
│                                                      │
│ Step 2: Orchestrator → ProcessPayment → Payment     │
│         Payment: charge card                        │
│         FAILURE: card declined                      │
│         Returns: PaymentFailed                      │
│                                                      │
│ Compensation (executed in reverse):                 │
│ Step 1 comp: Orchestrator → ReleaseInventory       │
│              → Inventory: release                   │
│              → InventoryReleased                    │
│                                                      │
│ Orchestrator: update order status → CANCELLED      │
│ Client: receives 402 Payment Required              │
│                                                      │
│ Saga state table:                                   │
│  saga_id | step | status | compensation_status      │
│  xyz123  |  1   | DONE   | COMPENSATED             │
│  xyz123  |  2   | FAILED | N/A                     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Orchestration saga (Python)**
```python
from enum import Enum
from dataclasses import dataclass

class SagaStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"

@dataclass
class SagaState:
    saga_id: str
    order_id: str
    status: SagaStatus
    completed_steps: list  # ["INVENTORY", "PAYMENT"]

class OrderSagaOrchestrator:
    def __init__(self, saga_repo, inventory, payment,
                  shipping, event_bus):
        self.saga_repo = saga_repo
        self.inventory = inventory
        self.payment = payment
        self.shipping = shipping
        self.event_bus = event_bus

    def start(self, order_id: str, items: list,
               payment_method: str) -> str:
        import uuid
        saga_id = str(uuid.uuid4())
        state = SagaState(
            saga_id=saga_id,
            order_id=order_id,
            status=SagaStatus.PENDING,
            completed_steps=[]
        )
        self.saga_repo.save(state)

        try:
            # Step 1: Reserve inventory
            self.inventory.reserve(order_id, items)
            state.completed_steps.append("INVENTORY")
            self.saga_repo.save(state)

            # Step 2: Process payment
            charge_id = self.payment.charge(
                order_id, payment_method)
            state.completed_steps.append("PAYMENT")
            self.saga_repo.save(state)

            # Step 3: Create shipment
            self.shipping.create(order_id)
            state.completed_steps.append("SHIPPING")

            state.status = SagaStatus.COMPLETED
            self.saga_repo.save(state)
            self.event_bus.publish(
                "OrderConfirmed", {"order_id": order_id})
            return saga_id

        except Exception as e:
            self._compensate(state)
            raise

    def _compensate(self, state: SagaState):
        """Execute compensating transactions in reverse."""
        state.status = SagaStatus.COMPENSATING
        self.saga_repo.save(state)

        # Compensate in reverse order
        if "SHIPPING" in state.completed_steps:
            try:
                self.shipping.cancel(state.order_id)
            except Exception:
                pass  # Log and retry async

        if "PAYMENT" in state.completed_steps:
            try:
                self.payment.refund(state.order_id)
            except Exception:
                pass  # Log and retry async

        if "INVENTORY" in state.completed_steps:
            try:
                self.inventory.release(state.order_id)
            except Exception:
                pass  # Log and retry async

        state.status = SagaStatus.COMPENSATED
        self.saga_repo.save(state)
        self.event_bus.publish(
            "OrderCancelled", {"order_id": state.order_id})
```

**Example 2 - Distributed transaction without saga (BAD)**
```python
# BAD: 2PC across services - not possible in microservices
# with independent databases. This is pseudo-code showing
# why it does not work.

def place_order_2pc_bad(order):
    # Phase 1: Prepare all services
    # This requires all services to be available simultaneously
    # and hold locks while waiting for coordinator
    inventory_ok = inventory_service.prepare(order)
    payment_ok = payment_service.prepare(order)
    shipping_ok = shipping_service.prepare(order)

    # Phase 2: Commit or rollback
    # If coordinator crashes here: services are STUCK
    # with locks held indefinitely
    if inventory_ok and payment_ok and shipping_ok:
        inventory_service.commit()
        payment_service.commit()  # If crashes here?
        shipping_service.commit() # stuck lock forever
    else:
        inventory_service.rollback()
        payment_service.rollback()
        shipping_service.rollback()

# GOOD: Saga orchestrator with compensating transactions.
# No locks held across services.
# Eventual consistency: acceptable for business workflows.
```

---

### ⚖️ Comparison Table

| Aspect | Choreography | Orchestration |
|---|---|---|
| **Coordinator** | None (events drive flow) | Central saga orchestrator |
| **State** | Distributed across services | Centralized in orchestrator |
| **Coupling** | Loose (event-based) | Tighter (knows all services) |
| **Debugging** | Hard (trace events across services) | Easy (orchestrator has full state) |
| **Adding steps** | All services must be updated | Update orchestrator only |
| **Failure recovery** | Complex (distributed state) | Easier (centralized state) |
| **Best for** | Simple, stable flows | Complex, evolving workflows |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Compensating transactions are the same as rollbacks | Database rollbacks undo uncommitted changes. Compensating transactions execute new business operations that reverse the effects of committed actions. You cannot "un-send" an email; you can only send a "sorry, order cancelled" follow-up. Design your saga steps to defer side effects (notifications, external API calls) to the final step, after all compensatable steps succeed. |
| Sagas guarantee atomicity (all or nothing) | Sagas guarantee eventual consistency, not atomicity. During execution, intermediate states exist (inventory reserved but payment not yet processed). Design your UI and business logic to handle these intermediate states gracefully (show "order processing," not "order confirmed" until the saga completes). |
| Choreography is simpler than orchestration | Choreography appears simpler initially (no orchestrator to build). But as the number of services and failure scenarios grows, the implicit flow spread across many services becomes very hard to reason about, debug, and change. Orchestration has more upfront cost but better long-term maintainability. Most production systems use orchestration for complex sagas. |

---

### 🚨 Failure Modes & Diagnosis

**Stuck Saga - Compensations That Never Complete**

**Symptom:**
Orders are stuck in COMPENSATING status indefinitely.
Inventory shows items as reserved with no order.
Customers see "order processing" forever. Support tickets.

**Root Cause:**
A compensating transaction (e.g., ReleaseInventory) failed
and was not retried. No retry mechanism on compensation
failures. Saga stuck in COMPENSATING state permanently.

**Fix - Guaranteed retry of compensations:**
```python
class RetryingOrchestrator(OrderSagaOrchestrator):
    MAX_RETRIES = 10
    RETRY_DELAY = [1, 2, 4, 8, 16, 32, 60, 60, 60, 60]

    def _compensate_with_retry(
            self, compensation_fn, step_name: str,
            order_id: str):
        """Retry compensation with exponential backoff."""
        for attempt in range(self.MAX_RETRIES):
            try:
                compensation_fn(order_id)
                return  # Success
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY[attempt]
                    # In production: use a job queue
                    # (Celery, Temporal) for async retry
                    print(f"Compensation {step_name} "
                          f"failed (attempt {attempt+1}),"
                          f" retry in {delay}s: {e}")
                    import time
                    time.sleep(delay)
                else:
                    # All retries exhausted
                    # Alert on-call. Manual intervention needed.
                    alert_oncall(
                        f"CRITICAL: Compensation {step_name} "
                        f"failed after {self.MAX_RETRIES} "
                        f"retries for order {order_id}"
                    )
                    raise

# Better: use Temporal.io or AWS Step Functions
# which provide durable retry built-in
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Event-Driven Architecture` - choreography sagas
  use EDA as the communication mechanism between
  saga steps
- `Circuit Breaker (System)` - wrap each saga step
  call with a circuit breaker to handle downstream
  service failures gracefully

**Builds On This (learn these next):**
- `CQRS` - saga orchestrators often combine with CQRS:
  commands trigger saga steps; events update read models
- `Database Internals` - understanding ACID transactions
  illuminates why sagas are needed (no ACID across
  services with independent databases)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Sequence of local txns + compensations.   │
│             │ No 2PC. Eventually consistent.            │
├─────────────┼──────────────────────────────────────────  │
│ CHOREOGRAPHY│ No coordinator. Events drive flow.        │
│             │ Loose coupling. Hard to debug.            │
├─────────────┼──────────────────────────────────────────  │
│ ORCHESTRATION│ Central saga manager. Explicit commands. │
│              │ Easy to debug. Orchestrator = bottleneck.│
├─────────────┼──────────────────────────────────────────  │
│ COMPENSATION│ New business action (not DB rollback).    │
│             │ Must be idempotent + retryable.           │
├─────────────┼──────────────────────────────────────────  │
│ SAGA STATE  │ Persist completed steps.                  │
│             │ Resume on crash. Retry/compensate.        │
├─────────────┼──────────────────────────────────────────  │
│ FAILURE     │ Stuck saga: retry compensations.         │
│             │ Use job queue (Temporal, Step Functions). │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Local txns + compensating txns.         │
│             │  No 2PC. Eventual consistency."         │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ What is Scalability (Conceptual)          │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Sagas replace distributed 2PC with a sequence of local
   transactions and compensating transactions. No cross-service
   lock is held. The system is eventually consistent:
   intermediate inconsistent states exist during execution.
2. Choreography (no coordinator, event-driven) vs.
   Orchestration (central coordinator, command-driven).
   Orchestration is easier to implement correctly for
   complex flows; use it as the default.
3. Compensating transactions must be idempotent and must
   always complete (with retries). A saga that gets stuck
   in COMPENSATING state is a permanent inconsistency.
   Use a durable job queue (Temporal.io, AWS Step Functions)
   to guarantee retry until completion.

**Interview one-liner:**
"Saga pattern: distributed transaction without 2PC. Sequence of local transactions;
each step publishes event/command for next step. On failure: compensating
transactions (new business actions, not DB rollback) in reverse order.
Choreography: services react to events (no coordinator, loose coupling, harder to
debug). Orchestration: central saga orchestrator sends commands and tracks state
(easier to debug, orchestrator = bottleneck). Compensations must be idempotent
and retryable. Persist saga state: on crash, resume from last known step. Use
Temporal.io or AWS Step Functions for production sagas."
