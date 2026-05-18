---
id: DST-043
title: Saga Pattern
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-018, DST-033
used_by: DST-044, DST-045
related: DST-014, DST-018, DST-028, DST-033, DST-044, DST-045
tags:
  - distributed
  - transactions
  - saga
  - microservices
  - choreography
  - orchestration
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/distributed-systems/saga-pattern/
---

⚡ TL;DR - A Saga is a sequence of local transactions
where each step publishes an event or message to
trigger the next step, and each step has a
compensating transaction that undoes its effect if
a later step fails; it replaces distributed ACID
transactions (2PC) with eventual consistency and
explicit failure handling, accepting that the system
may be temporarily inconsistent during execution.

---

### 📋 Entry Metadata

| #043 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, Idempotency, Two-Phase Commit | |
| **Used by:** | CQRS, Event Sourcing | |
| **Related:** | Consistency, Idempotency, Eventual Consistency, 2PC, CQRS, Event Sourcing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce order service uses three microservices:
Order (Postgres), Inventory (MySQL), Payment (Stripe).
Placing an order requires atomically: creating the
order, reserving inventory, and charging the customer.
Using 2PC: the distributed coordinator must communicate
with Postgres, MySQL, and Stripe simultaneously and
hold locks across all three while getting votes.
Stripe does not support XA transactions. Even if
it did, holding locks across three external systems
during a network round-trip (payment processing can
take 2-5 seconds) is impractical. 2PC is not viable
across service boundaries.

**THE INSIGHT:**
Instead of one atomic transaction, execute a sequence
of local transactions, each within one service. If
a step fails, undo previous steps with compensating
transactions. Temporary inconsistency (order created,
inventory not yet reserved) is acceptable if the
system guarantees it will eventually reach a consistent
terminal state (either fully done or fully undone).

---

### 📘 Textbook Definition

A **Saga** is a pattern for managing distributed
transactions across multiple microservices, where a
long-running business process is broken into a sequence
of smaller, locally atomic steps. Each step has a
corresponding **compensating transaction** that
reverses its effects if a later step fails.

**Two coordination styles:**

| Style | Mechanism | Coupling |
|---|---|---|
| **Choreography** | Each service publishes events; other services react | Loose |
| **Orchestration** | A central saga orchestrator sends commands to services | Centralized |

**Key properties:**
- Each local transaction completes and commits atomically
- No global locks or 2PC
- Failure recovery via compensating transactions (not rollback)
- Eventual consistency: intermediate states are visible

---

### ⏱️ Understand It in 30 Seconds

```
HAPPY PATH (order placement):
  1. Order Service: Create Order (status=PENDING)
  2. Inventory Service: Reserve Items
  3. Payment Service: Charge Customer
  4. Order Service: Update Order (status=CONFIRMED)

FAILURE at step 3 (payment fails):
  Compensating transactions run in reverse:
  3'. [skip - payment not charged]
  2'. Inventory Service: Release Reserved Items
  1'. Order Service: Update Order (status=FAILED)

NOTE: During steps 1-2, the order is PENDING and
items are RESERVED. Other requests might see this
intermediate state. This is acceptable in Saga.
In 2PC, intermediate states are invisible (hidden
behind locks). Saga trades isolation for scalability.
```

---

### 🔩 First Principles Explanation

**CHOREOGRAPHY-BASED SAGA:**

```
Services communicate via events/messages.
No central coordinator.

Order Service                 Inventory Service
    |                               |
    |-- OrderCreated event -------->|
    |                         [reserve items]
    |<-- InventoryReserved ---------|
    |                               |
    |--- (forward to Payment) ----->|
    |                         Payment Service
    |<-- PaymentCharged ------------|
    |                               |
    [update order = CONFIRMED]

FAILURE HANDLING:
  Payment Service: payment declined
    → publish PaymentFailed event
  Inventory Service: listens to PaymentFailed
    → release reservation
    → publish InventoryReleased event
  Order Service: listens to InventoryReleased
    → mark order as FAILED
```

**ORCHESTRATION-BASED SAGA:**

```
A dedicated Saga Orchestrator issues commands
and receives events.

Saga Orchestrator
    |
    |-- Command: CreateOrder -------> Order Service
    |<-- Event: OrderCreated -------- Order Service
    |
    |-- Command: ReserveInventory --> Inventory Service
    |<-- Event: InventoryReserved --- Inventory Service
    |
    |-- Command: ChargePayment -----> Payment Service
    |<-- Event: PaymentFailed ------- Payment Service
    |
    |-- Command: ReleaseInventory --> Inventory Service
    |<-- Event: InventoryReleased --- Inventory Service
    |
    |-- Command: FailOrder ---------> Order Service
    |<-- Event: OrderFailed --------- Order Service
    [Saga complete (failed path)]
```

**COMPENSATING TRANSACTION DESIGN:**

Not all compensating transactions are simple undos.
Some operations cannot be undone cleanly after they
have had external effects. Categories:

```
RETRYABLE: Can be retried until success
  Example: sending a confirmation email (idempotent)
  Compensation: not needed (always succeeds eventually)

REVERSIBLE: Can be undone cleanly
  Example: reserving inventory (no external effect yet)
  Compensation: release reservation

PIVOTAL: The point of no return
  Example: charging a credit card
  Cannot be undone - instead: issue a refund
  Compensation: create a refund transaction

PIVOT POINT:
  All steps before: reversible
  All steps after: retryable (must succeed)
  Pivot step: transaction of no return
```

**IDEMPOTENCY REQUIREMENT:**

Because Saga steps may be retried (message redelivery,
network failures), every step must be idempotent.
Use unique transaction IDs to detect and discard
duplicates:

```sql
INSERT INTO inventory_reservations
  (order_id, item_id, quantity)
VALUES
  (:order_id, :item_id, :quantity)
ON CONFLICT (order_id, item_id) DO NOTHING;
-- Idempotent: duplicate OrderId+ItemId is ignored
```

---

### 🧠 Mental Model / Analogy

> A Saga is like booking a trip where you reserve
> flights, hotel, and rental car separately (three
> local transactions). If your rental car booking
> fails, you cancel the hotel, then cancel the flights
> (compensating transactions in reverse order). Unlike
> a "package deal" (2PC - all or nothing atomically),
> you might briefly hold a flight and hotel without
> a rental car. Other systems might see you have a
> flight reserved. This is acceptable because you
> have a clear plan to undo everything if needed.
> The trip either fully completes or fully unwinds.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Instead of one big transaction across multiple services
(impossible across network boundaries), use a chain
of smaller transactions. If one fails, undo the
previous ones with compensating actions. The system
is temporarily inconsistent during the chain but
eventually reaches a consistent final state.

**Level 2 - Choreography vs Orchestration:**
Choreography: services communicate via events; no
central brain; simpler but hard to understand the
overall flow. Orchestration: a saga orchestrator
sends commands and tracks state; clearer flow but
single point of failure. Use choreography for simple
sagas (<3 steps); orchestration for complex ones.

**Level 3 - Compensation is not rollback:**
Database rollback undoes effects atomically - nothing
is ever visible. Saga compensation runs AFTER the
step has committed - effects ARE visible during
execution. A compensation must create a new transaction
that counteracts the original. "Release inventory
reservation" is not a rollback; it is a new operation.
Design compensations as explicit business operations.

**Level 4 - The semantic lock anti-pattern:**
When Order is created with status=PENDING, it is
visible to other parts of the system. Another request
might try to operate on this pending order. This is
called a "semantic lock." Best practice: use a
PENDING/PROCESSING status on sagas in progress.
Prevent external operations on resources in this
state until the saga completes or fails.

**Level 5 - Distributed Saga and the ACD properties:**
Saga provides ACD but NOT isolation (the "I" in ACID):
- **Atomicity:** Either all steps complete or all
  compensations run (eventual atomicity)
- **Consistency:** Business invariants hold at the
  end, but not necessarily during execution
- **Durability:** Each local transaction is durable
- **No Isolation:** Intermediate states are visible

If other transactions can observe intermediate Saga
state, you may have dirty reads. Mitigations: semantic
locks (pending status), countermeasures (track and
react to anomalies), and careful saga ordering
(put most likely failure steps first).

---

### 💻 Code Example

**Orchestration Saga: Wrong vs Right**

```python
# BAD: Saga without idempotency or compensation

class OrderService:
    def place_order(self, order_data: dict) -> str:
        order_id = db.insert_order(order_data)

        # BUG 1: No idempotency - duplicate messages
        #         create duplicate orders
        inventory.reserve(order_id, order_data["items"])

        # BUG 2: No compensation if payment fails -
        #         inventory left reserved permanently
        payment.charge(
            order_id,
            order_data["user_id"],
            order_data["amount"]
        )

        return order_id
```

```python
# GOOD: Orchestration saga with compensation and idempotency

import enum
from dataclasses import dataclass

class SagaStatus(enum.Enum):
    PENDING = "PENDING"
    INVENTORY_RESERVED = "INVENTORY_RESERVED"
    PAYMENT_CHARGED = "PAYMENT_CHARGED"
    COMPLETED = "COMPLETED"
    COMPENSATING = "COMPENSATING"
    FAILED = "FAILED"

@dataclass
class OrderSaga:
    saga_id: str
    order_data: dict
    status: SagaStatus = SagaStatus.PENDING

class OrderSagaOrchestrator:

    def execute(self, saga: OrderSaga) -> bool:
        try:
            # Step 1: Create order (idempotent)
            order_id = self._create_order(saga)
            saga.status = SagaStatus.PENDING

            # Step 2: Reserve inventory (idempotent)
            reserved = self._reserve_inventory(
                saga.saga_id,
                order_id,
                saga.order_data["items"]
            )
            if not reserved:
                self._compensate_order(order_id)
                saga.status = SagaStatus.FAILED
                return False
            saga.status = SagaStatus.INVENTORY_RESERVED

            # Step 3: Charge payment (pivot point - no undo)
            charged = self._charge_payment(
                saga.saga_id,
                order_id,
                saga.order_data["amount"]
            )
            if not charged:
                # Compensate in reverse order
                self._release_inventory(
                    saga.saga_id,
                    order_id
                )
                self._compensate_order(order_id)
                saga.status = SagaStatus.FAILED
                return False
            saga.status = SagaStatus.PAYMENT_CHARGED

            # Step 4: Confirm order (retryable - must succeed)
            self._confirm_order(order_id)
            saga.status = SagaStatus.COMPLETED
            return True

        except Exception:
            saga.status = SagaStatus.COMPENSATING
            self._run_compensations(saga)
            saga.status = SagaStatus.FAILED
            return False

    def _reserve_inventory(
        self,
        saga_id: str,
        order_id: str,
        items: list
    ) -> bool:
        """Idempotent: uses saga_id as idempotency key."""
        return inventory_service.reserve(
            idempotency_key=f"saga:{saga_id}:reserve",
            order_id=order_id,
            items=items
        )

    def _release_inventory(
        self,
        saga_id: str,
        order_id: str
    ) -> None:
        """Compensation for _reserve_inventory."""
        inventory_service.release(
            idempotency_key=f"saga:{saga_id}:release",
            order_id=order_id
        )
```

---

### ⚖️ Comparison Table

| Property | Saga | 2PC (Two-Phase Commit) |
|---|---|---|
| **Cross-service** | Yes - local transactions per service | Requires XA support in every participant |
| **Locks held** | None across steps | Held for entire transaction duration |
| **Failure model** | Compensating transactions | Blocking if coordinator crashes |
| **Isolation** | None (intermediate states visible) | Full (uncommitted changes hidden) |
| **Latency** | Each step: local commit latency | Full round-trip with coordinator lock |
| **Best for** | Long-running business processes | Short RDBMS transactions |

| Style | Coupling | Visibility | Complexity |
|---|---|---|---|
| Choreography | Loose | Hard to trace | Low initial |
| Orchestration | Central | Easy to trace | Higher initial, lower operational |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Saga provides ACID transactions across services" | Saga provides ACD (Atomicity, Consistency, Durability) but NOT Isolation. Intermediate states are visible to other requests. Design for this explicitly. |
| "Choreography is always simpler" | Choreography is simpler to build but harder to reason about and debug. In production, understanding "why did this order get stuck?" requires tracing events across multiple services' logs. Orchestration centralizes this visibility. |
| "The compensating transaction can always undo the original" | Some operations cannot be undone - only counteracted. Charging a credit card cannot be rolled back; a refund is a new financial transaction. Design compensations as forward-moving operations, not true rollbacks. |
| "Sagas eliminate the need for idempotency" | Sagas increase the need for idempotency. Message redelivery and saga recovery can cause the same step to execute multiple times. Every step must be idempotent. |

---

### 🚨 Failure Modes & Diagnosis

**Stuck Saga (Compensation Never Completed)**

**Symptom:** Orders are stuck in COMPENSATING status.
Inventory shows reservations that should have been
released. Customer was not charged but inventory
is still reserved.

**Root Cause:** Inventory service was down when the
compensation command was sent. The release message
was lost or not retried. No dead-letter queue or
retry mechanism on the compensating transaction.

**Diagnosis:**
```sql
-- Find sagas stuck in compensating state:
SELECT saga_id, status, created_at, last_updated_at
FROM order_sagas
WHERE status IN ('COMPENSATING', 'PENDING')
  AND last_updated_at < NOW() - INTERVAL '10 minutes'
ORDER BY created_at;

-- Find orphaned inventory reservations:
SELECT r.order_id, r.saga_id, r.reserved_at
FROM inventory_reservations r
LEFT JOIN order_sagas s ON r.saga_id = s.saga_id
WHERE s.status IN ('FAILED', 'COMPENSATING', NULL)
  AND r.released_at IS NULL
  AND r.reserved_at < NOW() - INTERVAL '1 hour';
```

**Fix:**
1. Implement compensating transactions with retry
   (publish to durable message queue with retry).
2. Add a saga recovery job: periodically find sagas
   in non-terminal states older than threshold and
   re-trigger compensations.
3. Use an outbox pattern for compensation messages
   (write compensation intent to DB before executing,
   deliver from DB if message delivery fails).

---

### 🔗 Related Keywords

**Prerequisites:** `Consistency` (DST-014),
`Idempotency` (DST-018),
`Two-Phase Commit` (DST-033)

**Builds On This:** `CQRS` (DST-044),
`Event Sourcing` (DST-045)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT       │ Chain of local transactions + compensations│
│ WHY        │ Replace 2PC across service boundaries      │
│ TRADE-OFF  │ No isolation; intermediate states visible  │
├────────────┼────────────────────────────────────────────┤
│ STYLES     │ Choreography: events (loose coupling)      │
│            │ Orchestration: commands (centralized)      │
├────────────┼────────────────────────────────────────────┤
│ PIVOT POINT│ Step before which: reversible              │
│            │ Step at/after which: retryable only        │
│ COMPENSATE │ Not rollback - a new forward transaction   │
├────────────┼────────────────────────────────────────────┤
│ REQUIRE    │ Idempotency on every step (retries happen) │
│            │ Semantic lock while saga is in-progress   │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Saga = sequence of commits + plan to undo │
│            │  if anything goes wrong."                 │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The Saga pattern makes explicit a trade-off that was
previously hidden in system design: distributed
atomicity at the cost of distributed complexity. When
you write a single-service function that wraps multiple
operations in `BEGIN ... COMMIT`, the database handles
failures silently. When you cross service boundaries,
there is no `BEGIN` for the whole operation. Saga forces
you to design the failure path explicitly: what is the
compensating action for every step? This is not a
limitation - it is a clarification. Many systems have
bugs precisely because the failure path was never
designed. The Saga pattern's discipline of "define
compensation before implementation" is valuable even
when the underlying system could have used 2PC.

---

### 💡 The Surprising Truth

The Saga pattern was first described by Hector
Garcia-Molina and Kenneth Salem in 1987 in a paper
called "Sagas" - 30 years before microservices made
it popular. Their original context was long-running
database transactions (think: a multi-day hospital
admission record that spans many database updates).
The problem they solved was that a 3-day transaction
holding database locks for the entire duration was
impractical. Their solution: break it into steps with
compensations. The pattern was rediscovered by the
microservices community because it solves the same
problem at the network boundary. The insight hasn't
changed in 35 years: if you can't hold a lock for
the entire duration, you need a way to undo partial
work when things go wrong.

---

### ✅ Mastery Checklist

1. [DESIGN] For a hotel booking saga (reserve room,
   reserve flight, charge card), identify the pivot
   point and write the compensating transaction for
   each step that comes before it.
2. [CHOOSE] A 3-step saga: payment service is external
   (Stripe), inventory is internal, order is internal.
   Choose choreography or orchestration and justify.
3. [IMPLEMENT] Add idempotency to a saga step that
   reserves inventory. Handle the case where the
   reserve message is delivered twice.
4. [DEBUG] Orders are stuck in COMPENSATING for hours.
   Write the SQL query to find them and describe
   the recovery job to re-trigger compensations.
5. [COMPARE] List three concrete situations where 2PC
   is still the right choice over Saga.
