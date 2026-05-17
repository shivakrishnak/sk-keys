---
id: MSV-046
title: Saga Pattern
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-047, MSV-048, MSV-057
used_by: MSV-047, MSV-057
related: MSV-047, MSV-048, MSV-049, MSV-050, MSV-051, MSV-054, MSV-057, MSV-058
tags:
  - microservices
  - distributed
  - deep-dive
  - transactions
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /microservices/saga-pattern/
---

# MSV-046 - Saga Pattern

⚡ TL;DR - Saga Pattern manages distributed transactions
across multiple microservices without a distributed
lock (2PC). A Saga is a sequence of local transactions.
Each step executes a local transaction and publishes
an event. If a step fails: compensating transactions
roll back previous steps. Two implementations:
(1) Choreography - each service listens to events
and reacts. No central coordinator. (2) Orchestration
- a Saga Orchestrator drives the workflow, calling
each service in sequence and handling failures. Provides
eventual consistency, not ACID consistency.

| #046 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Distributed Transaction, Event-Driven Microservices, Compensating Transaction | |
| **Used by:** | Distributed Transaction, Compensating Transaction | |
| **Related:** | Distributed Transaction, Event-Driven Microservices, Eventual Consistency in Microservices, CQRS in Microservices, Event Sourcing in Microservices, Outbox Pattern, Idempotency in Microservices, Compensating Transaction | |

---

### 🔥 The Problem This Solves

**DISTRIBUTED TRANSACTION ACROSS SERVICES:**

```
PROBLEM: Place an order (e-commerce)
  Requires atomic update across 4 services:
  1. Order-service: create order (PENDING)
  2. Payment-service: charge customer
  3. Inventory-service: reserve product stock
  4. Shipping-service: create shipment
  
  REQUIREMENT: All or nothing.
  If payment succeeds but inventory is out of stock:
  -> Charge customer for unavailable item = wrong
  If inventory reserved but payment fails:
  -> Reserve stock for unpaid order = wrong

2PC (Two-Phase Commit) solution:
  Coordinator locks all 4 services (prepare phase)
  Then commits all (commit phase)
  Problems: distributed lock, not supported by
  most microservice data stores (Kafka, NoSQL),
  blocks if any participant is unavailable

SAGA solution:
  Execute steps sequentially, locally
  Each step: local transaction + event
  Failure: execute compensating transactions in reverse
  No distributed lock; eventual consistency
```

---

### 📘 Textbook Definition

**Saga Pattern** is a design pattern for managing
distributed transactions across multiple microservices.
A Saga is a sequence of local transactions. Each local
transaction updates the service's own database and
publishes a message or event that triggers the next
transaction in the sequence. If a transaction fails,
the Saga executes compensating transactions to undo
changes made by preceding transactions. Two implementation
strategies: (1) Choreography-based: services communicate
via events, no central coordinator. (2) Orchestration-based:
a Saga Orchestrator service drives the workflow. Provides
eventual consistency rather than ACID transactions.
Originated in database literature (Garcia-Molina and
Salem, 1987); popularized by Chris Richardson's
Microservices Patterns.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Saga = sequence of local transactions with compensation
on failure. Distributed transaction without distributed
lock.

**One analogy:**
> Booking a flight + hotel + car rental for a trip.
Travel agency method: book flight (local). If OK:
book hotel. If OK: book car. If car is unavailable:
cancel hotel (compensating transaction). Cancel flight
(compensating transaction). Each step is local; failure
triggers cancellations in reverse. No one "locks" all
three providers simultaneously - that would be 2PC.
The travel agency (orchestrator) drives the workflow
and handles the compensations.

**One insight:**
The hardest part of Sagas is not the happy path - it's
the compensation logic. Each forward action needs a
compensating action: `createOrder` -> `cancelOrder`;
`chargePayment` -> `refundPayment`; `reserveInventory`
-> `releaseInventory`. And compensations can fail too
(can you always refund? What if payment provider is
down during refund?). This is why Saga implementations
need persistent Saga state and idempotent operations.

---

### 🔩 First Principles Explanation

**CHOREOGRAPHY-BASED SAGA:**

```
EVENT FLOW (Order Saga - choreography):

  Order-service                 Payment-service
  Inventory-service             Shipping-service
  \-> Each service listens to topic; reacts to events

HAPPY PATH:
  1. Order-service: create order -> publish OrderCreated
  2. Payment-service: hears OrderCreated
               -> charge payment
               -> publish PaymentProcessed
  3. Inventory-service: hears PaymentProcessed
                -> reserve stock
                -> publish InventoryReserved
  4. Shipping-service: hears InventoryReserved
                -> create shipment
                -> publish ShipmentCreated
  5. Order-service: hears ShipmentCreated
                -> set order CONFIRMED

FAILURE: Inventory out of stock
  1-2: Same as above (OrderCreated, PaymentProcessed)
  3. Inventory-service: out of stock
     -> publish InventoryReservationFailed
  4. Payment-service: hears InventoryReservationFailed
     -> refund payment
     -> publish PaymentRefunded
  5. Order-service: hears PaymentRefunded
     -> cancel order, notify customer

PROS: Simple, decoupled, no central coordinator
CONS: Hard to trace end-to-end; circular dependencies
     risk; no central place to see Saga state
```

**ORCHESTRATION-BASED SAGA:**

```
ORCHESTRATOR DRIVES THE WORKFLOW:

  Saga Orchestrator (Order Saga Service)
    |-- Step 1: call Payment-service.charge()
    |   Success: -> Step 2
    |   Failure: -> abort (no compensation needed yet)
    |
    |-- Step 2: call Inventory-service.reserve()
    |   Success: -> Step 3
    |   Failure: -> compensate Step 1: refund payment
    |
    |-- Step 3: call Shipping-service.create()
    |   Success: -> complete
    |   Failure: -> compensate Step 2: release inventory
    |           -> compensate Step 1: refund payment

SAGA STATE (persisted):
  {
    sagaId: "saga-123",
    orderId: "order-456",
    state: "INVENTORY_RESERVED",
    compensations: [
      {step: "PAYMENT", action: "refund",
       reference: "payment-789"}
    ]
  }

PROS: Clear workflow; easy to monitor and debug;
      handles complex failure scenarios centrally
CONS: Orchestrator is a dependency for all steps;
      more code to write and maintain
```

---

### 🧪 Thought Experiment

**WHAT IF COMPENSATION FAILS?**

```
SCENARIO:
  Step 1: charge payment -> SUCCESS ($99.99)
  Step 2: reserve inventory -> FAILED (out of stock)
  Compensation: refund payment -> FAILED (Stripe API down)
  
  Now: customer was charged but no order exists
       Refund is pending but failed
       System is in an inconsistent state

SOLUTION:
  1. Idempotent compensation: each compensation has
     an idempotency key. Retry until it succeeds.
     Store compensation state persistently.
  2. Dead letter queue: if compensation fails after
     N retries -> publish to DLQ -> manual intervention
  3. Saga state machine: track compensation status.
     COMPENSATING state: compensation in progress.
     COMPENSATED state: completed.
     COMPENSATION_FAILED: manual intervention required.
  4. Alerting: COMPENSATION_FAILED triggers PagerDuty.
     Finance team: manually issue refund.

KEY INSIGHT:
  Compensations must eventually succeed.
  Use: exponential backoff retries, idempotency keys,
  circuit breakers for compensation calls, DLQ for
  manual intervention, monitoring for COMPENSATION_FAILED.
```

---

### 🧠 Mental Model / Analogy

> Saga is like a contractor managing a home renovation.
> Each subcontractor (electrician, plumber, painter)
> does their part independently (local transactions).
> If the plumber finds a broken pipe that stops the
> project: the contractor tells the electrician to
> undo their completed work (compensation). The
> contractor (orchestrator) tracks the project state
> and coordinates compensations. The contractors
> (services) don't know about each other - they just
> receive instructions. The state machine (project
> plan) is the Saga. Choreography = the contractors
> communicate directly via walkie-talkie (events);
> no contractor takes the orchestrator role.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Saga handles multi-step processes across services:
do step 1, then step 2, then step 3. If step 2 fails:
undo step 1. Each step is its own transaction. No
"all or nothing" lock across all services.

**Level 2 - How to use it (junior developer):**
For an order flow: create a Saga class with steps
(payment, inventory, shipping). Each step calls a
service and defines a compensation. Use Axon Framework
or Eventuate Tram in Spring Boot. The framework handles
Saga state persistence and step orchestration.

**Level 3 - How it works (mid-level engineer):**
Saga Orchestrator: implemented as a state machine.
Each state = completed step. Transitions trigger
next step calls. Failure transitions trigger compensation.
Saga state persisted (DB) after each step. On restart
(crash recovery): load Saga state, resume from last
state. Idempotency: each service operation needs an
idempotency key (sagaId + stepId) to safely retry.

**Level 4 - Why it was designed this way (senior/staff):**
Choreography vs Orchestration trade-off: Choreography
follows event-driven architecture principles: services
are truly decoupled; they react to domain events.
But: debugging a failed Saga requires tracing events
across 5 services. Orchestration: one place to see
Saga state and what happened. But: orchestrator is
coupled to all participants. For complex business
workflows (10+ steps): orchestration is preferred
because observability and error handling are centralized.
For simple workflows (2-3 steps): choreography may
suffice.

**Level 5 - Mastery (distinguished engineer):**
Saga vs 2PC at scale: 2PC with a coordinator that
locks 4 databases creates a latency multiplier (each
step waits for coordinator ack) and a single point
of failure. At 1000 Sagas/second: 2PC coordinator
becomes a bottleneck. Saga: each step executes locally
(fast); orchestrator is stateless per request (can
scale horizontally). The Outbox Pattern is critical
for Saga reliability: after a local transaction, the
event/command must be published atomically with the
DB write. Without Outbox: the DB update succeeds but
the event publish fails -> Saga stuck. Outbox solves
this: write event to Outbox table in same local
transaction; separate relay publishes to Kafka.

---

### ⚙️ How It Works (Mechanism)

**ORCHESTRATED SAGA (Spring + Axon Framework):**

```java
@Saga
public class OrderSaga {

    @Autowired
    private transient CommandGateway commandGateway;

    // Start Saga when order is created
    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(OrderCreatedEvent event) {
        // Step 1: initiate payment
        commandGateway.send(
            new ProcessPaymentCommand(
                event.getOrderId(),
                event.getCustomerId(),
                event.getAmount()
            )
        );
    }

    // Step 2: payment succeeded -> reserve inventory
    @SagaEventHandler(associationProperty = "orderId")
    public void on(PaymentProcessedEvent event) {
        commandGateway.send(
            new ReserveInventoryCommand(
                event.getOrderId(),
                event.getProductId(),
                event.getQuantity()
            )
        );
    }

    // Compensation: payment failed -> cancel order
    @SagaEventHandler(associationProperty = "orderId")
    public void on(PaymentFailedEvent event) {
        commandGateway.send(
            new CancelOrderCommand(
                event.getOrderId(),
                "Payment failed: " + event.getReason()
            )
        );
        SagaLifecycle.end();
    }

    // Compensation: inventory failed -> refund payment
    @SagaEventHandler(associationProperty = "orderId")
    public void on(InventoryReservationFailedEvent event) {
        commandGateway.send(
            new RefundPaymentCommand(
                event.getOrderId(),
                event.getPaymentId()
            )
        );
        // After refund: cancel order
    }

    // Complete: all steps done
    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    public void on(ShipmentCreatedEvent event) {
        commandGateway.send(
            new ConfirmOrderCommand(event.getOrderId())
        );
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
ORDER SAGA - FULL FLOW:

HAPPY PATH:
  OrderCreated -> ProcessPayment
  -> PaymentProcessed -> ReserveInventory
  -> InventoryReserved -> CreateShipment
  -> ShipmentCreated -> ConfirmOrder
  -> OrderConfirmed (Saga ends)

FAILURE AT INVENTORY:
  OrderCreated -> ProcessPayment
  -> PaymentProcessed -> ReserveInventory
  -> InventoryReservationFailed
  -> COMPENSATION: RefundPayment
  -> PaymentRefunded -> CancelOrder
  -> OrderCancelled (Saga ends)

SAGA STATE (persisted in DB):
  saga_id, order_id, current_step, status,
  compensation_data (payment_id for refund reference)
  
ON SERVICE RESTART:
  Load pending Sagas from DB
  Resume from current_step
  Operations are idempotent (same sagaId+step = same result)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: no compensation logic**

```java
// BAD: Sequential calls without compensation
// If any step fails: partial state, no cleanup
public void placeOrder(OrderRequest req) {
    paymentService.charge(req.getCustomerId(), req.getAmount());
    // payment succeeded
    try {
        inventoryService.reserve(req.getProductId(), req.getQty());
        // inventory check fails
    } catch (OutOfStockException e) {
        // Payment was charged but order can't be fulfilled
        // No refund triggered. Customer charged for nothing.
        throw new OrderException("Out of stock");
    }
}
```

```java
// GOOD: Saga with compensating transactions
@Service
public class OrderSagaService {

    public void placeOrder(OrderRequest req) {
        String sagaId = UUID.randomUUID().toString();
        SagaState saga = sagaRepo.save(
            new SagaState(sagaId, req.getOrderId(),
                SagaStep.PAYMENT_PENDING));

        try {
            // Step 1: charge
            PaymentId paymentId = paymentService.charge(
                sagaId,  // idempotency key
                req.getCustomerId(), req.getAmount());
            saga.setPaymentId(paymentId);
            saga.setStep(SagaStep.INVENTORY_PENDING);
            sagaRepo.save(saga);

            // Step 2: reserve
            inventoryService.reserve(
                sagaId, req.getProductId(), req.getQty());
            saga.setStep(SagaStep.COMPLETED);
            sagaRepo.save(saga);

        } catch (OutOfStockException e) {
            // Compensate Step 1: refund
            paymentService.refund(
                sagaId, saga.getPaymentId());
            saga.setStep(SagaStep.COMPENSATED);
            sagaRepo.save(saga);
            throw new OrderException("Out of stock; refunded");
        }
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Consistency | Complexity | Failure Handling | Scalability |
|---|---|---|---|---|
| **2PC (Two-Phase Commit)** | Strong ACID | Low code, high infra | Coordinator failure = blocked | Poor (lock bottleneck) |
| **Saga Orchestration** | Eventual | Medium | Centralized compensation | High |
| **Saga Choreography** | Eventual | Low-Medium | Distributed, event-driven | High |
| **No distributed tx** | None (data inconsistency) | Low | None | High (but wrong) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Saga provides atomicity like ACID | Saga provides eventual consistency, not atomicity. During a Saga execution, partial states are visible. Step 1 committed and visible; Step 2 not yet. This is unavoidable. Design for it: use a PENDING state in the final record until the Saga completes. Users should not see PENDING orders as confirmed. |
| Compensating transaction = rollback | Database rollback is instantaneous and undoes the change. Compensating transaction is a new forward transaction that reverses the business effect. A payment refund is NOT a rollback - it's a new payment going back. It can fail. It is visible. It takes time. It needs to be modeled explicitly in the business process. |
| Choreography is simpler than orchestration | Choreography is simpler in happy-path code. But compensations in choreography require each service to react to failure events from OTHER services - creating hidden coupling via event topic contracts. In orchestration: compensation logic is in one place. At 5+ steps: orchestration compensation logic is substantially easier to understand and debug. |

---

### 🚨 Failure Modes & Diagnosis

**Saga stuck in COMPENSATING state**

**Symptom:**
Monitoring shows 47 Sagas in `COMPENSATING` state
for 6 hours. These are orders where inventory was
unavailable. The refund compensation step is failing.
Customers have been charged but no refund issued.
Manual intervention required.

**Root Cause:**
Stripe API rate limit hit during peak compensation.
All refund calls getting `429 Too Many Requests`.
Compensation retry is not implemented with backoff.
All retries hit the rate limit simultaneously (retry
storm).

**Diagnostic:**
```bash
# Find stuck Sagas
SELECT saga_id, order_id, step, created_at,
       compensation_attempts
FROM saga_state
WHERE status = 'COMPENSATING'
  AND created_at < NOW() - INTERVAL '1 HOUR'
ORDER BY created_at;

# Check compensation failure logs
grep 'compensation.*failed\|refund.*429' \
  /var/log/order-service/*.log | tail -50

# Check Stripe API rate limit headers
# Stripe returns: X-RateLimit-Remaining: 0
```

**Fix:**
1. Immediate: manually trigger refund for stuck Sagas
   (compensate via admin API).
2. Short-term: add exponential backoff + jitter to
   compensation retry. Stop the retry storm.
3. Long-term: implement proper compensation retry
   with circuit breaker. Alert when compensation
   fails > N times: trigger PagerDuty.
4. Add dead letter queue for permanently failed
   compensations: finance team dashboard for manual
   refund issuance.

---

### 🔗 Related Keywords

**Core Saga concepts:**
- `Distributed Transaction` - the problem Saga solves
- `Compensating Transaction` - the mechanism for
  Saga rollback
- `Idempotency in Microservices` - required for Saga
  step retry safety

**Data patterns used with Saga:**
- `Outbox Pattern` - ensures local transaction and
  event publication are atomic (critical for Sagas)
- `Event-Driven Microservices` - choreography Saga
  runs on event-driven architecture
- `Event Sourcing in Microservices` - Sagas integrate
  naturally with event sourcing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CHOREOGRAPHY │ Services react to events; decoupled      │
│ ORCHESTRATION│ Central coordinator drives steps         │
├──────────────┼───────────────────────────────────────────┤
│ KEY NEED     │ Compensating transactions per step       │
│              │ Idempotency keys for all operations      │
│              │ Persistent Saga state                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Distributed transaction via sequential  │
│              │  local steps + compensating rollback"    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Saga = sequence of local transactions + compensating
   transactions for rollback. Provides eventual
   consistency, not ACID.
2. Two styles: Choreography (event-driven, decoupled,
   harder to trace) and Orchestration (central
   coordinator, easier to debug, more coupled).
3. Compensation must be idempotent and retryable.
   Store compensation data (paymentId, reference) in
   Saga state for retry.

**Interview one-liner:**
"Saga Pattern handles distributed transactions across
microservices without 2PC. A sequence of local transactions:
each step updates its own DB and publishes an event/command.
Failure triggers compensating transactions in reverse.
Two styles: Choreography (event-driven, decoupled) and
Orchestration (central Saga coordinator, easier debugging).
Evental consistency, not ACID. Required: idempotent
operations, persistent Saga state, Outbox Pattern for
atomic event publication."

---

### 💡 The Surprising Truth

The most common Saga implementation mistake: not
persisting Saga state before publishing commands.
Wrong order: (1) publish command to payment service,
(2) save Saga state to DB. If the service crashes
between steps 1 and 2: the payment command was sent
but the Saga state doesn't reflect it. On restart:
the Saga re-executes from the previous state and sends
the payment command again. Double charge. The correct
order: (1) save Saga state WITH idempotency key,
(2) publish command. With Outbox Pattern: write
(Saga state update + outbox event) in ONE local
transaction. This guarantees exactly-once semantics:
if the transaction commits, the event will eventually
be published. If the transaction fails: neither
happens. The Outbox relay handles publishing independently.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** Design an Order Saga (5 steps) with
   choreography: list all events, all compensation
   events, all services involved. Draw the event
   flow for happy path and 2 failure scenarios.
2. **ORCHESTRATION** Implement a 3-step Saga orchestrator
   in Spring Boot: state persistence, step execution,
   compensation on failure, idempotency keys.
3. **COMPARE** Explain when to use choreography vs
   orchestration: give 3 criteria that favor each.
4. **COMPENSATION** Design the compensation strategy
   for a payment that cannot be refunded immediately
   (payment provider API down). What states are needed?
5. **OUTBOX** Explain why Outbox Pattern is necessary
   for Saga reliability. Draw the failure scenario
   without Outbox. Show how Outbox prevents it.

---

### 🧠 Think About This Before We Continue

**Q1.** A hotel booking Saga has 3 steps: reserve hotel,
charge card, issue confirmation. Step 3 (issue
confirmation - sends email) fails due to email service
outage. Should the Saga compensate (cancel reservation
and refund)? Or mark the Saga as "confirmation pending"
and retry step 3? What factors determine the right
choice?

**Q2.** You are implementing a choreography-based Saga
for order placement. The Saga has 5 services and
something has gone wrong: customer was charged but
order shows CANCELLED. Describe how you would debug
this using only event logs and Saga state records.
What information would you look for in each service's
logs?

**Q3.** Two Sagas are running concurrently: both want
to reserve the last unit of Product X. Saga 1 reserves
at T=0. Saga 2 reserves at T=0.5s. Both succeed
because the inventory check was not atomic. Now
both customers received confirmation for an item with
quantity 1. How do you handle this? What consistency
model does Saga provide, and what compensating action
is needed?