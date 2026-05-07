---
layout: default
title: "Saga Pattern (DB)"
parent: "NoSQL & Distributed Databases"
nav_order: 33
permalink: /nosql/saga-pattern-db/
number: "NDB-033"
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Distributed Transactions, Two-Phase Commit (2PC), Microservices
used_by: System Design, Distributed Transactions, Event-Driven Architecture
related: Distributed Transactions, Two-Phase Commit (2PC), Outbox Pattern
tags:
  - nosql
  - saga-pattern
  - distributed-systems
  - deep-dive
---

# NDB-033 — Saga Pattern (DB)

⚡ TL;DR — The Saga pattern decomposes a distributed transaction into a sequence of local ACID transactions, each publishing an event that triggers the next; on failure, **compensating transactions** roll back already-completed steps; it provides **eventual consistency** without blocking — the key to distributed ACID-like behavior in microservices.

| #472            | Category: NoSQL & Distributed Databases                            | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Transactions, Two-Phase Commit (2PC), Microservices    |                 |
| **Used by:**    | System Design, Distributed Transactions, Event-Driven Architecture |                 |
| **Related:**    | Distributed Transactions, Two-Phase Commit (2PC), Outbox Pattern   |                 |

---

### 🔥 The Problem This Solves

**2PC IN MICROSERVICES IS IMPRACTICAL:**
Two-Phase Commit requires all services to block during Phase 1 while the coordinator waits for all votes. In a microservices architecture where each service may have different availability characteristics, a slow or unavailable service blocks the entire transaction. Additionally, 2PC requires all participants to support the XA protocol, which external APIs and many NoSQL databases don't implement.

**SAGA SOLVES LONG-RUNNING DISTRIBUTED WORKFLOWS:**
A Saga decomposes a distributed "transaction" into a sequence of local steps. Each step is a complete, committed local ACID transaction. On failure, previously committed steps are reversed by compensating transactions. No service is ever blocked waiting for a coordinator — each step proceeds independently. The Saga is eventually consistent: intermediate states are visible, but the system converges to a consistent final state.

---

### 📘 Textbook Definition

The **Saga Pattern** (Hector Garcia-Molina & Kenneth Salem, 1987) defines a long-lived transaction as a sequence of local transactions (T1, T2, ..., Tn), where each Ti is fully ACID within its own data store and publishes an event on completion. On success: T1 → T2 → ... → Tn. On failure at Ti: execute compensating transactions in reverse order: Ci-1 → Ci-2 → ... → C1. Two implementation variants: **Choreography** — each service reacts to events from the previous step and publishes events for the next; decentralized, loose coupling, harder to track overall state. **Orchestration** — a central **Saga Orchestrator** (a service or workflow engine) sends commands to each participant and handles responses; centralized, better observability, the orchestrator can become a single point of failure. Key properties of Saga: (1) **No global ACID isolation** — intermediate states are visible to concurrent transactions. (2) **Compensatable transactions** — Ti's compensation Ci must be semantically inverse (e.g., if Ti books a seat, Ci cancels the booking). (3) **Idempotent steps and compensations** — each step and compensation must be safe to execute multiple times (at-least-once Kafka delivery). (4) **Pivot transaction** — the transaction Ti after which either forward or compensating path is taken (the "point of no return").

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Saga = sequence of local transactions with a compensating transaction for each step — commit forward to succeed, run compensations in reverse to "undo."

**One analogy:**

> Booking a camping trip step-by-step: book campsite → rent car → buy gear. If the gear store is out of stock: return the car rental, cancel the campsite. Each step is independently completed (committed); failure triggers reversals (compensating transactions). Unlike 2PC (calling all vendors simultaneously and holding everyone on hold), the Saga books sequentially and reverses if needed — no one is on hold waiting.

- "Book campsite" → T1: local ACID transaction (commits)
- "Rent car" → T2: local ACID transaction (commits)
- "Buy gear — out of stock" → T3 fails → compensations triggered
- "Return car rental" → C2: compensation for T2
- "Cancel campsite" → C1: compensation for T1
- "No one on hold" → Saga is non-blocking (unlike 2PC)

**One insight:**
Compensating transactions are not a rollback — they are new forward writes that semantically reverse the effect of a completed transaction. Once T1 commits, there is no "undo" in the database sense. Ci is a new transaction: `INSERT INTO cancelled_bookings ... WHERE booking_id = T1.booking_id`. This means compensations must be designed upfront for every step, including the edge case where the compensation itself fails (compensation failures require retry + DLQ + manual intervention).

---

### 🔩 First Principles Explanation

**SAGA STATE AND STEPS:**

```
Business scenario: E-commerce order placement
Steps: Reserve Inventory → Process Payment → Confirm Order → Ship

Normal flow:
  T1: Inventory Service: reserve items (status: RESERVED)
      → publishes: "InventoryReserved" event
  T2: Payment Service: charge customer
      → publishes: "PaymentProcessed" event
  T3: Order Service: confirm order (status: CONFIRMED)
      → publishes: "OrderConfirmed" event
  T4: Shipping Service: create shipment
      → publishes: "ShipmentCreated" event

  Final state: all committed, order shipped ✓

Failure at T2 (payment fails):
  T1: COMMITTED (inventory reserved) ← must compensate
  T2: FAILED (payment charge failed) ← T3, T4 not started

  Compensations (in reverse):
  C1: Inventory Service: release reservation (status: AVAILABLE)
      → publishes: "InventoryReleased" event

Final state after compensation:
  Inventory: released (back to available)
  Payment: not charged (T2 failed before commit)
  Order: cancelled
  User sees: "Payment failed, order cancelled" ✓

Failure at T3 (order confirmation fails after payment):
  T1: COMMITTED (inventory reserved) ← must compensate
  T2: COMMITTED (payment charged) ← must compensate
  T3: FAILED ← T4 not started

  Compensations:
  C2: Payment Service: refund customer
  C1: Inventory Service: release reservation

  Final state: refunded + inventory released ✓
  Note: C2 must be robust — if refund fails, human intervention needed
```

**CHOREOGRAPHY IMPLEMENTATION:**

```java
// INVENTORY SERVICE: reacts to OrderCreated, publishes InventoryReserved/Failed
@Service
public class InventoryService {

    @KafkaListener(topics = "order.created")
    @Transactional  // local ACID transaction (inventory DB only)
    public void handleOrderCreated(OrderCreatedEvent event) {
        String sagaId = event.getSagaId();

        try {
            // T1: Reserve inventory (local ACID transaction)
            for (OrderItem item : event.getItems()) {
                Inventory inv = inventoryRepository.findByProductId(item.getProductId())
                    .orElseThrow(() -> new ProductNotFoundException(item.getProductId()));

                if (inv.getAvailable() < item.getQuantity()) {
                    throw new InsufficientInventoryException();
                }

                inv.setAvailable(inv.getAvailable() - item.getQuantity());
                inv.setReserved(inv.getReserved() + item.getQuantity());
                inventoryRepository.save(inv);
            }

            // Record saga step for idempotency + compensation
            sagaStepRepository.save(new SagaStep(sagaId, "INVENTORY_RESERVED", event.getOrderId()));

            // Publish success event → triggers Payment step
            outboxRepository.save(new OutboxEvent("inventory.reserved",
                new InventoryReservedEvent(sagaId, event.getOrderId())));

        } catch (InsufficientInventoryException e) {
            // Publish failure → triggers compensations of earlier steps
            outboxRepository.save(new OutboxEvent("inventory.reservation.failed",
                new InventoryReservationFailedEvent(sagaId, event.getOrderId(), e.getMessage())));
        }
    }

    // COMPENSATING TRANSACTION for T1
    @KafkaListener(topics = "payment.failed")
    @Transactional
    public void handlePaymentFailed(PaymentFailedEvent event) {
        // C1: Release inventory reservation (idempotent!)
        SagaStep step = sagaStepRepository
            .findBySagaIdAndStepName(event.getSagaId(), "INVENTORY_RESERVED")
            .orElse(null);

        if (step == null || step.isCompensated()) {
            return;  // Idempotency: already compensated, skip
        }

        // Reverse the reservation
        for (OrderItem item : event.getItems()) {
            Inventory inv = inventoryRepository.findByProductId(item.getProductId()).orElseThrow();
            inv.setAvailable(inv.getAvailable() + item.getQuantity());
            inv.setReserved(inv.getReserved() - item.getQuantity());
            inventoryRepository.save(inv);
        }

        step.setCompensated(true);
        sagaStepRepository.save(step);
    }
}
```

**ORCHESTRATION IMPLEMENTATION:**

```java
// SAGA ORCHESTRATOR: central coordinator, better observability
@Service
public class OrderSagaOrchestrator {

    @Transactional
    public OrderSaga startSaga(OrderRequest request) {
        OrderSaga saga = OrderSaga.builder()
            .orderId(request.getOrderId())
            .customerId(request.getCustomerId())
            .items(request.getItems())
            .status(SagaStatus.STARTED)
            .currentStep("RESERVE_INVENTORY")
            .build();
        sagaRepository.save(saga);

        // Send command to Inventory Service
        commandPublisher.send(new ReserveInventoryCommand(saga.getSagaId(), request.getItems()));
        return saga;
    }

    @KafkaListener(topics = "saga.inventory.response")
    @Transactional
    public void handleInventoryResponse(InventoryResponseEvent event) {
        OrderSaga saga = sagaRepository.findBySagaId(event.getSagaId()).orElseThrow();

        if (event.isSuccess()) {
            saga.setCurrentStep("PROCESS_PAYMENT");
            saga.setInventoryReservationId(event.getReservationId());
            sagaRepository.save(saga);
            // Proceed to next step
            commandPublisher.send(new ProcessPaymentCommand(saga.getSagaId(), saga.getCustomerId(), saga.getTotal()));
        } else {
            // Inventory failed — no prior committed steps to compensate
            saga.setStatus(SagaStatus.FAILED);
            saga.setFailureReason("Inventory unavailable: " + event.getErrorMessage());
            sagaRepository.save(saga);
            eventPublisher.publish(new OrderFailedEvent(saga.getOrderId(), saga.getFailureReason()));
        }
    }

    @KafkaListener(topics = "saga.payment.response")
    @Transactional
    public void handlePaymentResponse(PaymentResponseEvent event) {
        OrderSaga saga = sagaRepository.findBySagaId(event.getSagaId()).orElseThrow();

        if (event.isSuccess()) {
            saga.setCurrentStep("CONFIRM_ORDER");
            saga.setPaymentId(event.getPaymentId());
            sagaRepository.save(saga);
            commandPublisher.send(new ConfirmOrderCommand(saga.getSagaId(), saga.getOrderId()));
        } else {
            // Payment failed → compensate inventory
            saga.setStatus(SagaStatus.COMPENSATING);
            saga.setCurrentStep("COMPENSATE_INVENTORY");
            sagaRepository.save(saga);
            commandPublisher.send(new ReleaseInventoryCommand(saga.getSagaId(), saga.getInventoryReservationId()));
        }
    }
}
// Orchestration advantage: saga state visible in one place (sagaRepository)
// Any step can be retried: send command again to the same service
// Observability: "SELECT * FROM sagas WHERE status = 'COMPENSATING'" → failing sagas
```

**PIVOT TRANSACTION (POINT OF NO RETURN):**

```
Pivot transaction: the last step after which the saga must complete
  (no turning back; compensations would have too severe consequences)

Example: "Book flight → Book hotel → Send confirmation email"
  Pivot = "Book hotel" (T2)
  After T2: email is sent (T3) — cannot "unsend" an email
  Before pivot: can compensate (cancel flight if hotel unavailable)
  After pivot: compensations are not possible (email can't be unsent)

  Design rule: pivot transaction must be the last reversible step
  Irreversible steps (email, SMS, physical shipment) go AFTER pivot

For order processing: "Process Payment" is often the pivot:
  Before payment: all steps are reversible (inventory release = free)
  After payment: customer has been charged — compensation is a refund (complex)
  So: ensure payment is the LAST step before any irreversible action
  After payment: confirmation email, shipment creation
```

---

### 🧪 Thought Experiment

**COMPENSATION FAILURE: WHAT HAPPENS WHEN C2 FAILS?**

Saga: Reserve Inventory (T1) → Process Payment (T2) → Confirm Order (T3)

T3 fails. Compensations: C2 (refund payment) → C1 (release inventory).

C2 (refund) is called, but the payment processor's refund API is DOWN:

- The saga is stuck in "COMPENSATING" state
- Inventory is still reserved (can't release until refund is confirmed, to avoid overselling)
- Customer has been charged but order is cancelled
- No automatic recovery if C2 keeps failing

**REAL-WORLD HANDLING:**

1. Retry with exponential backoff: retry C2 for up to 1 hour with 1m, 2m, 4m... delays
2. DLQ: after max retries, publish to Dead Letter Queue
3. Alert: DLQ consumer → alert on-call team
4. Manual: support team issues manual refund via payment processor's admin interface
5. Mark saga as "FAILED_PENDING_MANUAL_RESOLUTION"

**THE LESSON:**
Saga compensations are not guaranteed to succeed. Every Saga implementation must have a DLQ + alert + human workflow for compensation failures. This is the operational cost of eventual consistency: the system converges to consistency given enough retries and human intervention, but is not atomically guaranteed like 2PC.

---

### 🧠 Mental Model / Analogy

> Saga is like building a LEGO model step-by-step: snap piece 1 → snap piece 2 → snap piece 3. If piece 3 doesn't fit: unsnap piece 2, unsnap piece 1, start over. Each snap is permanent (committed) until actively unsnapped (compensated). Compare to 2PC: hold all pieces simultaneously in mid-air before snapping any — if any piece is wrong, drop all. With Saga: pieces are snapped (committed) one at a time; wrong piece → unsnap in reverse. No mid-air suspense, but: between snapping piece 1 and confirming piece 2 fits, someone could see a half-built model (intermediate state visibility).

- "Snap piece" → local ACID transaction (T1, T2, T3)
- "Unsnap" → compensating transaction (C2, C1)
- "Mid-air before snapping any" → 2PC Phase 1 (participants prepared but not committed)
- "Half-built model visible" → intermediate state visibility (lack of isolation)
- "Start over" → compensations complete → consistent initial state restored

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Saga = a sequence of steps, each step is a complete local transaction. If any step fails, run compensating transactions in reverse to undo prior steps. Use choreography (events) or orchestration (central coordinator). Sagas are eventually consistent — no global ACID isolation.

**Level 2:** Design compensations first: before coding each step, define its compensation. Ensure all steps and compensations are idempotent (safe to repeat). Persist saga state (orchestration) to enable recovery after orchestrator crash. Define a DLQ strategy for compensation failures. Choose choreography for simple 3-5 step sagas; orchestration for complex 5+ step sagas or when observability matters.

**Level 3:** Saga isolation problem: "dirty reads" across saga steps. Other transactions can read intermediate saga states (T1 committed but T3 not yet). For inventory reservation: reserve immediately (T1 = inventory_status = RESERVED, visible to other sagas); only finalize if saga succeeds. "RESERVED" is a semantic state that prevents double-booking without needing global ACID isolation. Countermeasures for saga anomalies: Semantic lock (mark data as "RESERVED" during saga, release on complete or compensate). Commutative update (design T1..Tn so they can execute in any order — e.g., INCR/DECR are commutative, SET is not). Pessimistic view (assume some transactions will be compensated; don't expose intermediate results to end users until saga is complete).

**Level 4:** The Saga pattern is a special case of a more general idea: Compensating Transactions (Gray 1981). The insight is that long-lived transactions (spanning seconds to minutes or hours) cannot use database locks (locks held for hours are impractical). The solution: use logical "saga steps" (local ACID transactions) with business-level compensations instead of database-level rollback. The Saga pattern essentially implements the Isolation property of ACID at the business logic level rather than the database level: instead of database locks preventing concurrent access to intermediate data, the application uses semantic states (RESERVED, PENDING, CANCELLED) to communicate intent. This is more flexible and scalable but shifts complexity to the application design. The Eventuate platform (by Chris Richardson, inventor of the Saga pattern book) provides a framework for both choreography and orchestration-based sagas, demonstrating the industrial-grade complexity of production Saga implementations.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ SAGA ORCHESTRATION STATE MACHINE                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│ States: STARTED → RESERVE_INVENTORY → PROCESS_PAYMENT│
│         → CONFIRM_ORDER → COMPLETED                  │
│         → COMPENSATING → COMPENSATE_PAYMENT          │
│         → COMPENSATE_INVENTORY → FAILED              │
│                                                      │
│ [SAGA PATTERN ← YOU ARE HERE: orchestrator drives]   │
│                                                      │
│ Happy path:                                          │
│ STARTED → [cmd: ReserveInventory]                    │
│         → InventoryService: local commit             │
│         → [response: InventoryReserved]              │
│ RESERVE_INVENTORY → [cmd: ProcessPayment]            │
│         → PaymentService: local commit               │
│         → [response: PaymentProcessed]               │
│ PROCESS_PAYMENT → [cmd: ConfirmOrder]                │
│         → OrderService: local commit                 │
│         → [response: OrderConfirmed]                 │
│ CONFIRM_ORDER → COMPLETED ✓                          │
│                                                      │
│ Failure at Payment:                                  │
│ PROCESS_PAYMENT → [response: PaymentFailed]          │
│         → COMPENSATING                               │
│         → [cmd: ReleaseInventory]                    │
│         → InventoryService: compensating commit      │
│         → [response: InventoryReleased]              │
│         → FAILED ✓ (all compensations done)          │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**TRAVEL BOOKING SAGA (ORCHESTRATION):**

```
User books trip: flight + hotel + car (all or nothing)
→ TripBookingSagaOrchestrator.startSaga(tripRequest)
→ [SAGA ← YOU ARE HERE: saga persisted, step 1 started]

Step 1: commandPublisher → "BookFlight" command
→ FlightService: local ACID txn → reserve seat F23B
→ response: "FlightBooked" {confirmationCode: "AA123"}
→ Orchestrator: saga.step = "BOOK_HOTEL", save saga state

Step 2: commandPublisher → "BookHotel" command
→ HotelService: local ACID txn → reserve room 204
→ response: "HotelBooked" {confirmationCode: "HLT456"}
→ Orchestrator: saga.step = "BOOK_CAR", save saga state

Step 3: commandPublisher → "BookCar" command
→ CarService: no available cars → "CarBookingFailed"
→ Orchestrator: saga.status = COMPENSATING, save saga state

Compensations (reverse order):
→ commandPublisher → "CancelHotel" {confirmationCode: "HLT456"}
→ HotelService: cancel reservation
→ commandPublisher → "CancelFlight" {confirmationCode: "AA123"}
→ FlightService: cancel reservation

→ Saga: status = FAILED
→ User: "Sorry, no cars available. Your flight and hotel have been cancelled."
→ No charges, no locked resources ✓
```

---

### ⚖️ Comparison Table

| Aspect                 | Choreography                     | Orchestration                          |
| ---------------------- | -------------------------------- | -------------------------------------- |
| Coupling               | Loose (event-driven)             | Medium (orchestrator manages services) |
| Observability          | Hard (events spread across logs) | Easy (central saga state)              |
| Complexity             | Simple for 3-4 steps             | Better for 5+ steps                    |
| SPOF risk              | None (fully decentralized)       | Orchestrator is potential bottleneck   |
| Retry / recovery       | Complex (each service retries)   | Simple (orchestrator retries commands) |
| Debugging failed sagas | Query all event logs             | Query saga state table                 |
| Circuit breaker        | Per-service                      | Centralized in orchestrator            |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                          |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Compensating transaction = database ROLLBACK"   | Compensation is a new forward write that semantically undoes a committed transaction. Once T1 commits, it cannot be rolled back — only compensated with a new transaction                                        |
| "Saga always achieves full consistency"          | Saga achieves eventual consistency, not ACID isolation. Intermediate states are visible. Two concurrent sagas may both see AVAILABLE inventory and both proceed, causing overselling if not using semantic locks |
| "Choreography is simpler than orchestration"     | Choreography is simpler to implement initially. For complex sagas (5+ steps, retries, timeouts), orchestration is far simpler to operate, debug, and monitor                                                     |
| "Saga compensations don't need to be idempotent" | Since Kafka provides at-least-once delivery, compensations may run twice. A non-idempotent compensation (e.g., issue refund twice) can cause double payments. Always make compensations idempotent               |

---

### 🚨 Failure Modes & Diagnosis

**1. Stuck Saga (Orchestrator Crashed Mid-Compensation)**

**Symptom:** Saga is in `COMPENSATING` state for 2+ hours. No progress. Inventory is still reserved; customer has not been refunded. Orchestrator service was redeployed mid-saga.

**Root Cause:** Orchestrator persisted saga state before crashing. On restart, orchestrator didn't resume in-progress sagas.

**Fix:**

```java
// On startup: resume any sagas stuck in non-terminal state
@Component
public class SagaRecoveryTask {

    @EventListener(ApplicationReadyEvent.class)
    @Transactional
    public void resumeInProgressSagas() {
        List<OrderSaga> stuckSagas = sagaRepository
            .findByStatusIn(List.of(SagaStatus.STARTED, SagaStatus.COMPENSATING))
            .stream()
            .filter(s -> s.getUpdatedAt().isBefore(Instant.now().minus(5, MINUTES)))
            .toList();

        for (OrderSaga saga : stuckSagas) {
            log.info("Resuming stuck saga: {} at step: {}", saga.getSagaId(), saga.getCurrentStep());
            sagaOrchestrator.resume(saga);  // re-send command for current step
        }
    }
}
// Also: scheduled job (every 5 minutes) to catch sagas stuck indefinitely
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Transactions, Two-Phase Commit (2PC), Microservices
**Builds On This:** System Design, Event-Driven Architecture
**Related:** Distributed Transactions, Two-Phase Commit (2PC), Outbox Pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT        │ Sequence of local ACID txns + compensations │
│ ON SUCCESS  │ T1 → T2 → T3 → ... → Tn ✓                 │
│ ON FAILURE  │ Cn-1 → ... → C2 → C1 (reverse compensate) │
│ ISOLATION   │ NONE: intermediate states visible           │
│ COMPENSATE  │ Must be idempotent (Kafka at-least-once)   │
│ CHOREOG     │ Events, decentralized, loose coupling       │
│ ORCHESTR    │ Central state, better observability         │
│ DLQ NEEDED  │ For compensation failures                   │
│ ONE-LINER   │ "Commit forward to succeed; compensate     │
│             │  backward to recover — no blocking"         │
│ NEXT EXPLORE│ Change Data Capture → Database Proxy        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design a Saga for an insurance claim processing workflow: Submit Claim → Validate Coverage → Assess Damage (external assessor API, may take 24 hours) → Approve/Deny → Disburse Payment. Identify: (a) which implementation (choreography or orchestration) and why, (b) compensating transaction for each step, (c) what happens if the assessor's API is unavailable for 24 hours, (d) how you handle the "Deny" case (which is not a failure — it's a valid business outcome).

**Q2.** (TYPE D — Failure Scenario) An e-commerce Saga (Reserve Inventory → Process Payment → Create Shipment) is running in production. After a deploy, you notice: 5% of sagas are stuck in the "STARTED" state with no step recorded for > 1 hour. The Kafka lag metric shows the "order.created" topic consumer is lagging by 50,000 messages. The Inventory Service was deployed simultaneously with the consumer lag increase. Diagnose: what went wrong? What is the user experience? How do you resolve the backlog? How do you prevent it?
