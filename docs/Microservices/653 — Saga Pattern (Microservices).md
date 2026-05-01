---
layout: default
title: "Saga Pattern (Microservices)"
parent: "Microservices"
nav_order: 653
permalink: /microservices/saga-pattern-microservices/
number: "653"
category: Microservices
difficulty: ★★★
depends_on: "Synchronous vs Async Communication, Eventual Consistency (Microservices), Event-Driven Microservices"
used_by: "Distributed Transaction, CQRS in Microservices"
tags: #advanced, #microservices, #distributed, #messaging, #pattern, #reliability
---

# 653 — Saga Pattern (Microservices)

`#advanced` `#microservices` `#distributed` `#messaging` `#pattern` `#reliability`

⚡ TL;DR — The **Saga Pattern** manages **distributed transactions across multiple microservices** without a two-phase commit. A saga is a sequence of local transactions, each publishing an event or message. If any step fails, **compensating transactions** roll back previously completed steps. Two styles: **Choreography** (event-driven) and **Orchestration** (central coordinator).

| #653            | Category: Microservices                                                                              | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Synchronous vs Async Communication, Eventual Consistency (Microservices), Event-Driven Microservices |                 |
| **Used by:**    | Distributed Transaction, CQRS in Microservices                                                       |                 |

---

### 📘 Textbook Definition

The **Saga Pattern** is a design pattern for managing data consistency across multiple microservices without using distributed ACID transactions. A saga decomposes a business transaction (e.g., place order) into a sequence of local transactions, each executed within a single service's local database. After each step succeeds, the service publishes a domain event or sends a message to trigger the next step. If a step fails, the saga executes **compensating transactions** — the inverse operations for each previously completed step — to restore the system to a consistent state. Two implementation variants: **Choreography-based Saga** — services react to domain events published by other services; no central coordinator; event-driven; decoupled but harder to trace end-to-end flow. **Orchestration-based Saga** — a central orchestrator (Saga Orchestrator Service or Temporal workflow) sends commands to each participant and handles failures/compensations; easier to reason about, easier to monitor, but creates a central dependency. Sagas achieve eventual consistency (not ACID consistency) — there is a period during saga execution where the system is in a partially committed state.

---

### 🟢 Simple Definition (Easy)

A Saga is a way to complete a multi-step business operation across multiple services when you can't use a single database transaction. Each service does its part (local transaction), then signals the next service. If something fails mid-way, each service undoes its part (compensating transaction). Example: order placement requires inventory reservation, payment charge, and shipment creation — three different services, three local transactions, one coordinated saga.

---

### 🔵 Simple Definition (Elaborated)

Placing an order involves 3 services: reserve inventory in `InventoryService`, charge payment in `PaymentService`, create shipment in `ShippingService`. These are 3 separate databases — you can't do them in one ACID transaction. Using a Saga: Step 1: reserve inventory (InventoryService commits to its DB). Step 2: charge payment (PaymentService commits to its DB). Step 3: create shipment (ShippingService commits to its DB). If Step 2 fails (payment declined): run compensating transactions → cancel shipment (not yet created) → release inventory reservation. Each step either completes normally or is undone. Final state is always consistent — either all 3 steps complete, or all are undone.

---

### 🔩 First Principles Explanation

**Why ACID distributed transactions don't work in microservices:**

```
MONOLITH (one database):
  BEGIN TRANSACTION
    UPDATE inventory SET reserved = reserved + 1 WHERE product_id = 123
    INSERT INTO payments VALUES (...)
    INSERT INTO shipments VALUES (...)
  COMMIT  ← all or nothing, ACID guaranteed

MICROSERVICES (three databases):
  InventoryService.db  → PostgreSQL (different server)
  PaymentService.db    → MySQL (different server)
  ShippingService.db   → MongoDB (different technology)

  2-Phase Commit (2PC) attempt:
    Phase 1 (Prepare): all three DBs lock resources, prepare to commit
    Phase 2 (Commit): coordinator sends commit to all
    PROBLEMS:
      - Locks held across all services during coordinator decision
      - If coordinator crashes between prepare and commit → stuck indefinitely
      - Tightly couples all services to coordinator availability
      - Violates microservices independence principle
      - Not supported by most NoSQL databases
      → Industry consensus: 2PC not viable for microservices at scale
```

**Choreography-based Saga:**

```
FLOW:
  No central coordinator. Services react to domain events.

  OrderService:
    1. Creates order (PENDING), persists to DB
    2. Publishes: "OrderCreated" event (Kafka)

  InventoryService:
    Consumes "OrderCreated"
    3. Reserves inventory (local DB), publishes "InventoryReserved"
    or: inventory insufficient → publishes "InventoryReservationFailed"

  PaymentService:
    Consumes "InventoryReserved"
    4. Charges payment (local DB), publishes "PaymentProcessed"
    or: payment declined → publishes "PaymentFailed"

  ShippingService:
    Consumes "PaymentProcessed"
    5. Creates shipment (local DB), publishes "ShipmentCreated"

  OrderService:
    Consumes "ShipmentCreated"
    6. Updates order to COMPLETED

FAILURE PATH (PaymentFailed):
  PaymentService publishes: "PaymentFailed"
  InventoryService consumes "PaymentFailed":
    → Runs compensating transaction: release inventory reservation
    → Publishes "InventoryReleasedDueToPaymentFailure"
  OrderService consumes:
    → Updates order to CANCELLED

PROS: Decoupled. No single point of failure. Services independent.
CONS: Hard to track end-to-end flow. Difficult to debug. "Where is my order?"
      requires correlating events across multiple service logs.
```

**Orchestration-based Saga:**

```
FLOW:
  Central OrderSagaOrchestrator sends commands to each service.

  OrderSagaOrchestrator (state machine in code or Temporal workflow):

  State: STARTED
    → Send command to InventoryService: "ReserveInventory"

  State: INVENTORY_RESERVED
    → Send command to PaymentService: "ChargePayment"

  State: PAYMENT_PROCESSED
    → Send command to ShippingService: "CreateShipment"

  State: COMPLETED (success)

  FAILURE HANDLING:
  State: PAYMENT_FAILED
    → Send compensation command to InventoryService: "ReleaseReservation"

  State: SHIPMENT_FAILED
    → Send compensation command to PaymentService: "RefundPayment"
    → Send compensation command to InventoryService: "ReleaseReservation"

  State: COMPENSATED (all rolled back)

PROS: Easy to visualise. Clear ownership. Easier debugging (central state).
      Temporal/Conductor provide workflow dashboards.
CONS: Orchestrator is a new service to maintain.
      Risk of "god service" if business logic leaks into orchestrator.
      Orchestrator becomes a single point of failure (mitigated by HA).
```

**Compensating transactions — what makes a good compensation:**

```
REQUIREMENT: compensation must be semantically correct, not just reversed.

  EXAMPLE: PaymentService.chargePayment(amount=100)
  SIMPLE REVERSAL (wrong): delete the payment record
  CORRECT COMPENSATION: add a refund transaction (PaymentService.refundPayment(amount=100))
  WHY: payment may have been partially processed (notification sent to bank).
       Deleting the DB record doesn't cancel the bank transaction.
       A refund creates an audit trail: charge happened, then refund.

  IDEMPOTENCY OF COMPENSATIONS:
  The saga may retry compensation if it doesn't receive acknowledgement.
  Compensation must be idempotent:
    refund(orderId=123, amount=100) called twice:
    → First call: creates refund record, marks order as refunded
    → Second call: finds existing refund for orderId=123 → returns success without duplicate refund
  Idempotency key: orderId or compensationTransactionId
```

---

### ❓ Why Does This Exist (Why Before What)

Before microservices, multi-step business operations were atomic ACID transactions. After decomposing into services with independent databases, ACID transactions are impossible without 2PC — which is impractical at scale. The Saga pattern is the standard solution to achieve data consistency across service boundaries without distributed locking.

---

### 🧠 Mental Model / Analogy

> A Saga is like a bank wire transfer involving multiple correspondent banks. Bank A (sends) → Bank B (intermediate) → Bank C (receives). Each bank processes its leg independently. If the final transfer to Bank C fails: Bank C notifies Bank B to reverse its leg, Bank B notifies Bank A to reverse the debit. Each bank applies its own reversal. The overall transfer either completes fully or is completely undone through sequential compensations — even though no bank has a lock on the others' accounts simultaneously.

"Wire transfer leg" = local transaction in one microservice
"Correspondent bank" = microservice with its own database
"Reversal notice" = compensating transaction command/event
"Transfer fully reversed" = saga compensated to consistent initial state

---

### ⚙️ How It Works (Mechanism)

**Spring + Axon Framework — choreography saga:**

```java
// Axon Framework: event-sourced saga orchestration/choreography:
@Saga
class OrderSaga {

    @Autowired transient CommandGateway commandGateway;

    @StartSaga
    @SagaEventHandler(associationProperty = "orderId")
    void handle(OrderCreatedEvent event) {
        commandGateway.send(new ReserveInventoryCommand(
            event.getOrderId(), event.getProductId(), event.getQuantity()
        ));
    }

    @SagaEventHandler(associationProperty = "orderId")
    void handle(InventoryReservedEvent event) {
        commandGateway.send(new ChargePaymentCommand(
            event.getOrderId(), event.getCustomerId(), event.getAmount()
        ));
    }

    @SagaEventHandler(associationProperty = "orderId")
    void handle(PaymentFailedEvent event) {
        // Compensation: release inventory
        commandGateway.send(new ReleaseInventoryCommand(
            event.getOrderId(), event.getProductId()
        ));
    }

    @EndSaga
    @SagaEventHandler(associationProperty = "orderId")
    void handle(ShipmentCreatedEvent event) {
        commandGateway.send(new CompleteOrderCommand(event.getOrderId()));
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Distributed Transaction
(multi-service business operation needing consistency)
        │
        ▼
Saga Pattern (Microservices)  ◄──── (you are here)
        │
        ├── Choreography → services react to domain events (decoupled)
        ├── Orchestration → central coordinator sends commands
        ├── Eventual Consistency → saga is eventually consistent, not ACID
        └── Event Sourcing in Microservices → events drive saga state transitions
```

---

### 💻 Code Example

**Temporal workflow (orchestration saga):**

```java
// Temporal: Orchestration saga as a durable workflow:
@WorkflowInterface
interface OrderFulfillmentWorkflow {
    @WorkflowMethod
    OrderResult fulfillOrder(OrderRequest request);
}

public class OrderFulfillmentWorkflowImpl implements OrderFulfillmentWorkflow {

    private final InventoryActivities inventory = Workflow.newActivityStub(InventoryActivities.class,
        ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(10)).build());
    private final PaymentActivities payment = Workflow.newActivityStub(PaymentActivities.class,
        ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(10)).build());
    private final ShippingActivities shipping = Workflow.newActivityStub(ShippingActivities.class,
        ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(10)).build());

    @Override
    public OrderResult fulfillOrder(OrderRequest request) {
        try {
            inventory.reserveInventory(request.getProductId(), request.getQuantity());
            try {
                payment.chargePayment(request.getCustomerId(), request.getAmount());
                try {
                    shipping.createShipment(request.getOrderId(), request.getAddress());
                    return OrderResult.success(request.getOrderId());
                } catch (ShippingException e) {
                    payment.refundPayment(request.getCustomerId(), request.getAmount());  // compensation
                    inventory.releaseInventory(request.getProductId(), request.getQuantity());  // compensation
                    return OrderResult.failed("Shipping failed: " + e.getMessage());
                }
            } catch (PaymentException e) {
                inventory.releaseInventory(request.getProductId(), request.getQuantity());  // compensation
                return OrderResult.failed("Payment declined: " + e.getMessage());
            }
        } catch (InventoryException e) {
            return OrderResult.failed("Out of stock");
        }
    }
}
// Temporal handles: retries, timeouts, crash recovery, workflow visibility dashboard
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sagas are ACID transactions across services                  | Sagas are NOT ACID. During execution, the system is in an intermediate state (partially committed). Other concurrent transactions may see this intermediate state (no isolation). Sagas achieve BASE (Basically Available, Soft state, Eventually consistent) |
| Choreography is always preferred because it's more decoupled | Choreography is hard to reason about at scale. For complex business workflows with many steps and compensation paths, orchestration (Temporal, Axon Saga) provides clearer visibility and easier failure diagnosis                                            |
| Compensating transactions are just rollbacks                 | Compensating transactions are semantic reversals, not database rollbacks. A payment compensation is a refund (adds a new transaction), not a delete. The original transaction stays in the audit log                                                          |

---

### 🔥 Pitfalls in Production

**Lost events — saga stuck in intermediate state**

```
SCENARIO:
  OrderSaga: inventory reserved, payment charged, shipping command sent.
  ShippingService crashes before processing the command.
  Command lost (in-memory queue, not persisted).
  Payment charged but no shipment created.
  Order stuck in "PAYMENT_PROCESSED" state indefinitely.

PREVENTION STACK:
  1. Use durable message queues (Kafka/RabbitMQ with persistence)
     → Command message persisted even if ShippingService is down
     → ShippingService consumes when it restarts

  2. Use Outbox Pattern for event publishing
     → Event published within same DB transaction as local step
     → Even if producer crashes after DB commit, event will be published on restart

  3. Use saga timeout:
     If saga not completed within 24 hours → trigger compensation automatically
     Temporal: Workflow.newTimer(Duration.ofHours(24))
     → After 24h: cancel order, refund payment, release inventory

  4. Saga dashboard (Temporal Web UI, Axon Server):
     → Monitor stuck workflows
     → Alert: saga older than 1 hour that hasn't completed
```

---

### 🔗 Related Keywords

- `Distributed Transaction` — the problem Saga solves
- `Eventual Consistency (Microservices)` — the consistency model sagas achieve
- `Event Sourcing in Microservices` — events as the mechanism for saga state transitions
- `Outbox Pattern` — ensures reliable event publishing within a saga step

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SOLVES       │ Multi-service transactions without 2PC    │
│ CONSISTENCY  │ Eventual (BASE), not ACID                 │
├──────────────┼───────────────────────────────────────────┤
│ CHOREOGRAPHY │ Services react to events (decoupled)      │
│              │ Pros: no SPOF. Cons: hard to trace        │
├──────────────┼───────────────────────────────────────────┤
│ ORCHESTRATION│ Central coordinator sends commands        │
│              │ Pros: clear flow. Cons: new service       │
├──────────────┼───────────────────────────────────────────┤
│ COMPENSATION │ Semantic undo (refund ≠ delete)           │
│ TOOLS        │ Axon Framework, Temporal, Conductor       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A saga for order placement has 4 steps: reserve inventory → charge payment → create shipment → notify customer. Each step can fail. Draw the complete state machine including all compensating paths: if shipment creation fails, what compensations must run? If payment fails, what compensations must run? If inventory reservation fails, are there compensations needed? In a choreography-based saga, which service is responsible for triggering each compensation?

**Q2.** The "Lost Update" problem in sagas: two concurrent sagas for the same product can both read available inventory (stock=1) and both proceed to reserve it (both see stock > 0). After both reserve, stock = -1 (oversold). Describe three strategies to prevent this: (a) optimistic locking with version numbers in the inventory service; (b) reservation as a separate entity (reserve-then-confirm pattern); (c) using a message queue with single-partition ordering to serialise inventory operations. What are the trade-offs of each approach for high-throughput flash sales?
