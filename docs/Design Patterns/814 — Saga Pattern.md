---
layout: default
title: "Saga Pattern"
parent: "Design Patterns"
nav_order: 814
permalink: /design-patterns/saga-pattern/
number: "0814"
category: Design Patterns
difficulty: ★★★
depends_on: Design Patterns, Distributed Transactions, Outbox Pattern, CQRS Pattern, Event-Driven Architecture
used_by: Microservices, Distributed Systems, Order Processing, Long-Running Processes
related: Outbox Pattern, CQRS Pattern, Circuit Breaker Pattern, Two-Phase Commit, Choreography vs Orchestration
tags:
  - pattern
  - distributed
  - deep-dive
  - microservices
  - architecture
---

# 814 — Saga Pattern

⚡ TL;DR — The Saga Pattern manages distributed transactions across microservices by breaking them into a sequence of local transactions with compensating actions to undo completed steps if any step fails.

| #814 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Design Patterns, Distributed Transactions, Outbox Pattern, CQRS Pattern, Event-Driven Architecture | |
| **Used by:** | Microservices, Distributed Systems, Order Processing, Long-Running Processes | |
| **Related:** | Outbox Pattern, CQRS Pattern, Circuit Breaker Pattern, Two-Phase Commit, Choreography vs Orchestration | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce order placement spans 4 services: Payment, Inventory, Shipping, and Notification. Using a 2-Phase Commit (2PC) to guarantee atomicity across all 4 requires a distributed coordinator that locks resources in all 4 services while waiting for every participant to vote. If Shipping is slow, all resources stay locked. If the coordinator fails mid-commit, all services are blocked indefinitely. At 10,000 orders/second, the locking overhead makes 2PC impractical — it produces the very bottleneck it was designed to prevent.

**THE BREAKING POINT:**
2PC does not scale in microservices. Services are owned by different teams, deployed independently, and may be temporarily unavailable. A distributed lock spanning independently-deployed services is a single point of failure that contradicts the entire point of microservices.

**THE INVENTION MOMENT:**
This is exactly why the Saga Pattern was developed — to achieve eventual consistency across distributed services without distributed locks, by chaining local transactions and providing compensating transactions that undo already-completed steps when a downstream step fails.

---

### 📘 Textbook Definition

A Saga is a sequence of local transactions where each transaction updates a single service and publishes a message or event to trigger the next transaction in the sequence. If a step fails, the saga executes compensating transactions for all previously completed steps (in reverse order) to undo their effects and restore the system to a consistent state. Sagas achieve eventual consistency (not strong consistency) and release resources after each local transaction rather than holding locks across the entire workflow.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Break a distributed transaction into steps; if any step fails, undo the completed ones in reverse order.

**One analogy:**
> Booking a business trip: you book flight → hotel → rental car, each independently. If the rental car is unavailable, you cancel the hotel and then the flight — reversing the completed steps. No one locks all three systems while you check availability. Each booking is independent. Cancellation is the compensating action. The saga is the complete workflow: forward steps + compensating steps.

**One insight:**
A Saga does not prevent failure — it manages it. The key design decision is: what is the compensating action for each completed step? Designing compensating actions is harder than designing forward actions. A Saga without well-defined compensating actions is not a Saga — it is just optimistic execution.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each step in a Saga is a local transaction — it commits independently and releases locks immediately after its step succeeds.
2. Compensating transactions undo the effect of completed steps — they are logically inverse but not literally reversals (a payment compensation is a refund, not an undo).
3. A Saga achieves eventual consistency — between steps, the system is in a temporarily inconsistent state (known as a "pivotal transaction" or "saga intermediate state").

**DERIVED DESIGN:**
The invariants explain why Sagas are semantically different from 2PC: 2PC provides atomicity across all steps (all or nothing, simultaneously). A Saga provides eventual consistency (all succeed forward, or all completed steps are compensated). Between the first forward step and the last (or first failing step), the system is in a partial state — some services have committed, others have not.

Two implementation styles:
- **Choreography**: each service listens for events and decides its next action, emitting its own events. No central coordinator.
- **Orchestration**: a saga orchestrator sends commands to each service and receives their responses, deciding what to execute next.

**THE TRADE-OFFS:**
**Gain:** Scalability (lock released after each step), resilience (partial failures managed), decentralisation.
**Cost:** Complex error handling (compensating transactions); eventual consistency (temporary partial states); testing difficulty (all failure combinations must be tested).

---

### 🧪 Thought Experiment

**SETUP:**
Order placement saga: steps are (1) Reserve payment, (2) Reserve inventory, (3) Create shipping label, (4) Confirm order. Each step is in a separate service.

**WHAT HAPPENS without Saga (2PC):**
All 4 services are locked simultaneously. Coordinator sends PREPARE to all. Step 3 (Shipping) times out — shipping service is slow. All resources locked for 30 seconds. Payment service transaction times out. All steps ROLLBACK. User must retry. At 10,000 orders/second, shipping slowness propagates as a bottleneck to payment and inventory. One slow service degrades the entire system.

**WHAT HAPPENS with Saga:**
Step 1: Payment service reserves $49.99 (committed). Step 2: Inventory service reserves item (committed). Step 3: Shipping service times out. Saga detects failure. Compensating step: Inventory service releases reservation. Compensating step: Payment service reverses the reserve (or voids the hold). Order fails cleanly — user notified. No lock held outside each service's local transaction.

**THE INSIGHT:**
A Saga externalises the coordination of a distributed workflow. The complexity of error handling is concentrated in the saga definition (including compensating actions) rather than distributed lock management. This is fundamentally more scalable.

---

### 🧠 Mental Model / Analogy

> Think of a distributed orchestra (orchestration-style Saga). The conductor (Saga orchestrator) directs each musician: "Now strings — now brass — now percussion." If the brass section fails, the conductor stops the piece and tells the previous sections to return to the beginning (compensate). The conductor knows the full score and manages execution. No musician locks the others — they play when told and stop when told.

- "Conductor" → Saga orchestrator
- "Musician" → individual microservice
- "Playing a section" → executing a local transaction
- "Returning to the beginning" → compensating transaction
- "Full score" → the saga definition (sequence of forward + compensating steps)

Where this analogy breaks down: an orchestra is synchronous — the conductor sees immediate outcomes. A Saga orchestrator is asynchronous — it sends commands and waits for responses, sometimes with timeout and retry.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Saga is a way to coordinate a multi-step business process across different services without freezing all of them at once. Each step happens independently. If a step fails, earlier steps are undone. It works like booking a trip — you can book and cancel each part independently.

**Level 2 — How to use it (junior developer):**
Implement a Saga by defining: (1) the ordered list of forward steps and (2) the compensating step for each forward step. Start with choreography (event-driven): each service publishes an event when its step completes; downstream services listen for events and execute the next step. For a payment saga: `PaymentReserved` event triggers inventory reservation; `InventoryReserved` triggers shipping; `ShippingFailed` triggers inventory release, which triggers payment release.

**Level 3 — How it works (mid-level engineer):**
Choreography vs. Orchestration trade-offs: Choreography is decentralised (each service knows its next action) — good for simpler workflows, harder to visualise the full saga path. Orchestration is centralised (a dedicated orchestrator process holds the saga state) — easier to visualise, debug, and add cross-cutting concerns (timeouts, retry policies). Frameworks: Axon Framework (Java), Conductor (Netflix), Temporal, or Spring State Machine. Each saga instance must be tracked: saga state (which step completed, which are compensating) must be persisted — if the orchestrator crashes, it must be able to resume.

**Level 4 — Why it was designed this way (senior/staff):**
The Saga Pattern acknowledges that distributed systems cannot achieve ACID atomicity across service boundaries without coordination protocols (2PC) that are impractical at scale. Instead, Sagas embrace the BASE (Basically Available, Soft-state, Eventually consistent) model. The design implication: every forward transaction in a Saga must have a semantically meaningful compensating transaction. Not all operations are compensatable ("I sent the package" cannot be literally reversed — the compensating action is "send a return label"). These are "pivotal transactions" — after which compensation becomes external (customer service, manual process). Identifying pivotal transactions in a business workflow is the most important design decision in a Saga. Operations after the pivotal transaction must either be retried until success or accepted as terminal.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  SAGA CHOREOGRAPHY (Event-Driven)                    │
│                                                      │
│  Order Service: creates order                        │
│    → emits OrderCreated                              │
│         ↓                                            │
│  Payment Service: reserves payment                   │
│    → emits PaymentReserved                           │
│         ↓                                            │
│  Inventory Service: reserves stock                   │
│    → emits InventoryReserved                         │
│         ↓                                            │
│  Shipping Service: creates label                     │
│    → emits ShippingLabelCreated                      │
│         ↓                                            │
│  Order Service: confirms order                       │
│                                                      │
│  FAILURE PATH (ShippingFailed):                      │
│  Shipping Service: fails                             │
│    → emits ShippingFailed                            │
│         ↓                                            │
│  Inventory Service: sees ShippingFailed              │
│    → executes compensate: releases stock             │
│    → emits InventoryReleased                         │
│         ↓                                            │
│  Payment Service: sees InventoryReleased             │
│    → executes compensate: voids payment hold         │
│    → emits PaymentVoided                             │
│         ↓                                            │
│  Order Service: sees PaymentVoided                   │
│    → marks order FAILED                              │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  SAGA ORCHESTRATION                                  │
│                                                      │
│  Saga Orchestrator                                   │
│    → Command: ReservePayment → PaymentService        │
│    ← Event: PaymentReserved                          │
│    → Command: ReserveInventory → InventoryService    │
│    ← Event: InventoryReserved                        │
│    → Command: CreateShipping → ShippingService       │
│    ← Event: ShippingFailed                           │
│    [FAILURE]                                         │
│    → Command: ReleaseInventory → InventoryService    │
│    → Command: VoidPayment → PaymentService           │
│    → Update saga state: FAILED                       │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
POST /orders → OrderSaga starts [← YOU ARE HERE]
  → Step 1: PaymentService.reserve() → success
  → Step 2: InventoryService.reserve() → success
  → Step 3: ShippingService.createLabel() → success
  → Step 4: OrderService.confirm() → success
  → Saga complete: order fulfilled
```

**FAILURE + COMPENSATION PATH:**
```
Step 3: ShippingService.createLabel() → FAIL
  → Saga enters compensation:
    Compensate Step 2: InventoryService.release()
    Compensate Step 1: PaymentService.void()
  → Order marked FAILED
  → User notified: "Order could not be fulfilled"
```

**WHAT CHANGES AT SCALE:**
At 1,000 sagas/second, a single orchestrator may become a bottleneck. At 10,000 sagas/second, the orchestrator must be stateless with saga state in a database, horizontally scalable. At 100,000 sagas/second, Kafka-based choreography is typically preferred: no single orchestrator, saga state derived from the event log.

---

### 💻 Code Example

**Example 1 — Orchestration saga (Spring):**

```java
// Saga Orchestrator — holds saga state
@Service
public class OrderSagaOrchestrator {
    private final SagaStateRepository sagaRepo;
    private final PaymentService payment;
    private final InventoryService inventory;
    private final ShippingService shipping;

    public void startSaga(UUID orderId, Order order) {
        SagaState state = new SagaState(orderId, STARTED);
        sagaRepo.save(state);
        executeStep1(orderId, order);
    }

    private void executeStep1(UUID orderId, Order order) {
        try {
            payment.reserve(order.total(),
                order.paymentMethod());
            sagaRepo.updateStep(orderId,
                PAYMENT_RESERVED);
            executeStep2(orderId, order);
        } catch (PaymentException e) {
            sagaRepo.updateStep(orderId, FAILED);
            // No compensation needed: step 1 failed
        }
    }

    private void executeStep2(UUID orderId, Order order) {
        try {
            inventory.reserve(order.items());
            sagaRepo.updateStep(orderId,
                INVENTORY_RESERVED);
            executeStep3(orderId, order);
        } catch (InventoryException e) {
            compensateStep1(orderId, order);
            sagaRepo.updateStep(orderId, FAILED);
        }
    }

    // ... step 3, compensations follow the same pattern
}
```

**Example 2 — Compensating transactions:**

```java
// Each compensation is semantically inverse, not literal
@Service
public class PaymentCompensation {
    private final PaymentGateway gateway;
    private final OutboxRepository outbox;

    @Transactional
    public void voidPaymentHold(UUID orderId) {
        // Idempotent: void is safe to retry
        PaymentHold hold = gateway.findHold(orderId);
        if (hold.isActive()) {
            gateway.voidHold(hold.id());
        }
        // Emit event via Outbox for reliability
        outbox.save(new OutboxEvent(
            UUID.randomUUID(), "PaymentVoided",
            orderId.toString(), Instant.now()));
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Scalability | Consistency | Complexity | Best For |
|---|---|---|---|---|
| **Saga (Choreography)** | Very high | Eventual | Medium | Simple, event-driven flows |
| **Saga (Orchestration)** | High | Eventual | Medium-High | Complex flows with visibility needs |
| 2-Phase Commit | Low | Strong | High | Small, co-located services |
| Long-Running Transaction | Very low | Strong | Low | Monoliths with ACID DB |

How to choose: Use Saga as the default for cross-service distributed workflows. Choose Choreography for simpler flows. Choose Orchestration when you need centralized visibility, complex retry policies, or cross-cutting concerns. Only use 2PC if strong consistency is a true business requirement and scale is low.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Sagas provide ACID transactions | Sagas provide eventual consistency. Between steps, the system is in a partial state — this is acceptable but must be handled in the business logic |
| Compensation means rollback | Compensation is a forward action that semantically undoes a previous step — not a database rollback. A payment compensation is a refund, which is a new transaction |
| Choreography is always better (no single point of failure) | Choreography makes it harder to track saga progress and debug failures. Orchestration is often operationally preferable despite having a coordinator |
| Every step can be compensated | Some steps cannot be semantically compensated (email sent, package shipped). These are pivotal transactions — design the saga to confirm they succeed before any non-compensatable action |

---

### 🚨 Failure Modes & Diagnosis

**1. Saga Stuck in Compensating State**

**Symptom:** Order is in `COMPENSATING` state for hours. Inventory released but payment void is failing repeatedly.

**Root Cause:** Payment service is unavailable. Compensation is retrying but not succeeding. Saga cannot complete compensation.

**Diagnostic:**
```bash
# Check saga state in database:
psql -c "SELECT id, state, step, updated_at
  FROM saga_state
  WHERE state = 'COMPENSATING'
  AND updated_at < NOW() - INTERVAL '30 minutes'"

# Check payment service health:
curl -s http://payment-service/actuator/health
```

**Fix:** Compensating transactions must be retried with exponential backoff indefinitely — compensation must eventually succeed or be escalated to a human process. Alert when any saga is stuck in COMPENSATING > 5 minutes.

**Prevention:** Design compensating transactions with Circuit Breaker. If compensation fails after N retries, park the saga in a `DEAD_LETTER` state and alert for manual intervention.

---

**2. Saga Coordination Message Lost**

**Symptom:** Saga advances forward to step 2, then freezes — step 3 never executed despite step 2 succeeding.

**Root Cause:** Event or command message from step 2 to step 3 was lost (broker unavailability, consumer restart).

**Diagnostic:**
```bash
# Check if the saga coordination event was published:
kafka-console-consumer.sh \
  --topic inventory-events \
  --from-beginning \
  | grep "InventoryReserved" | grep $ORDER_ID

# If missing: event was not published (missing Outbox)
```

**Fix:** All saga step completion events must use the Outbox Pattern to guarantee delivery.

**Prevention:** All saga coordination events must go through the Outbox Pattern. No direct Kafka publish from saga steps.

---

**3. Idempotency Failure — Step Executed Twice**

**Symptom:** Payment charged twice for one order; inventory decremented twice.

**Root Cause:** Saga step re-executed due to message redelivery after consumer restart. Step was not idempotent.

**Diagnostic:**
```bash
# Check for duplicate saga step execution:
psql -c "SELECT order_id, step, COUNT(*)
  FROM saga_execution_log
  GROUP BY order_id, step
  HAVING COUNT(*) > 1
  ORDER BY COUNT(*) DESC"
```

**Fix:** Each saga step must be idempotent by checking if the step was already executed for this saga instance ID before executing the local transaction.

**Prevention:** All saga step handlers must log their execution with `(saga_id, step_name)` as a unique key. Re-execution of a recorded step must be a no-op.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Distributed Transactions` — the problem Sagas solve; understanding 2PC and its limitations motivates the Saga approach
- `Outbox Pattern` — the reliable event publishing mechanism that Sagas depend on for coordination; saga steps must use the Outbox to prevent coordination message loss
- `Idempotency` — mandatory for Saga consumers; at-least-once delivery of saga coordination messages requires every step handler to be idempotent

**Builds On This (learn these next):**
- `Choreography vs. Orchestration` — the two Saga implementation styles; understanding their trade-offs is the primary design decision
- `Circuit Breaker Pattern` — compensation steps must include circuit breakers to prevent cascading retries when a service is unavailable
- `Temporal (workflow engine)` — a production-grade Saga orchestration engine that handles state persistence, retry, and timeout automatically

**Alternatives / Comparisons:**
- `Two-Phase Commit (2PC)` — the alternative for strong consistency; impractical at microservice scale but correct for co-located, low-volume workflows
- `Process Manager` — a related pattern (similar to orchestration saga) that coordinates long-running processes with explicit state machines

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Sequence of local transactions with       │
│              │ compensating actions for failure rollback │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Distributed transactions across services  │
│ SOLVES       │ without distributed locks (2PC)           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Sagas don't prevent failure — they manage │
│              │ it. Every forward step needs a            │
│              │ compensating step designed upfront.       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-step cross-service workflows that   │
│              │ must be consistent but can tolerate       │
│              │ eventual consistency                      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Strong (immediate) consistency across     │
│              │ all steps is a hard business requirement  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Scalability + no distributed locks vs.    │
│              │ eventual consistency + compensation       │
│              │ complexity                                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A saga is a chain of local transactions  │
│              │  with a cancellation plan built in."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Outbox Pattern → Temporal →               │
│              │ Circuit Breaker → Event Sourcing          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce order saga has 5 steps: reserve payment, reserve inventory, assign warehouser, create shipping label, and send confirmation email. Steps 1-4 have compensating actions. The email (step 5) cannot be compensated — once sent, it cannot be unsent. A saga designer calls step 5 a "pivotal transaction." Design the saga so that if any step before step 5 fails, compensation works correctly, and identify exactly what happens if step 5 itself fails after steps 1-4 have completed.

**Q2.** A team is choosing between Choreography and Orchestration for a 7-step order fulfillment saga. The CTO says "Choreography is better — no single point of failure." The Tech Lead says "Orchestration is better — centralized visibility and debugging." Describe the three most important operational factors (not theoretical ones) that would make you choose one over the other in a production system at 5,000 sagas/day, and explain why each factor tips the balance.

