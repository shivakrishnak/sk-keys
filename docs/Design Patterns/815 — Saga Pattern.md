---
layout: default
title: "Saga Pattern"
parent: "Design Patterns"
nav_order: 815
permalink: /design-patterns/saga-pattern/
number: "815"
category: Design Patterns
difficulty: ★★★
depends_on: "Microservices, Outbox Pattern, Event-Driven Pattern, Distributed Systems"
used_by: "Distributed transactions, microservices orchestration, long-running business processes"
tags: #advanced, #design-patterns, #distributed-systems, #microservices, #transactions, #saga
---

# 815 — Saga Pattern

`#advanced` `#design-patterns` `#distributed-systems` `#microservices` `#transactions` `#saga`

⚡ TL;DR — **Saga Pattern** manages distributed transactions across multiple microservices by breaking them into a sequence of local transactions, each publishing events or commands — with compensating transactions to undo completed steps if any step fails.

| #815            | Category: Design Patterns                                                              | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Microservices, Outbox Pattern, Event-Driven Pattern, Distributed Systems               |                 |
| **Used by:**    | Distributed transactions, microservices orchestration, long-running business processes |                 |

---

### 📘 Textbook Definition

**Saga Pattern** (Hector Garcia-Molina and Kenneth Salem, "Sagas", ACM SIGMOD 1987; applied to microservices by Chris Richardson, "Microservices Patterns", 2018): a way to manage data consistency across microservices in the absence of distributed ACID transactions. A saga is a sequence of local transactions, where each transaction updates data within a single service and publishes an event or command to trigger the next step. If a step fails, compensating transactions are executed in reverse order to undo the effects of the preceding steps. Two implementation styles: Choreography (services react to events — no central coordinator) and Orchestration (a Saga Orchestrator sends commands to services and tracks state). Sagas provide Eventual Consistency rather than strong (ACID) consistency.

---

### 🟢 Simple Definition (Easy)

An order involves: Order Service (create order), Inventory Service (reserve items), Payment Service (charge card), Shipping Service (schedule delivery). All four must succeed or the whole thing must be undone. In a single database: a transaction covers all four. In microservices: no shared transaction. Saga: each service does its local transaction and publishes an event. If Payment fails: publish "payment failed" event → Inventory releases reservation → Order cancels. Each service has a "compensating action" that undoes its step if something later fails.

---

### 🔵 Simple Definition (Elaborated)

A hotel booking platform: book flight (Airline Service), hotel (Hotel Service), and rental car (Car Service) — all-or-nothing. If any one of them fails, the others must be undone. Two-Phase Commit (2PC) across three external APIs: impossible. Saga: Flight booked → Hotel booked → Car booked → SUCCESS. If Car fails: Send "cancel car booking" (no-op, wasn't booked), send "cancel hotel booking" (compensating transaction), send "cancel flight" (compensating transaction). Each step has a compensating action. No distributed transaction needed.

---

### 🔩 First Principles Explanation

**Choreography vs. Orchestration saga styles with production implementation:**

```
SAGA STYLES:

  1. CHOREOGRAPHY (event-driven, decentralized):

  Services react to events from other services.
  No central coordinator.

  Order Saga (Choreography):

  OrderService: ORDER_CREATED event ──────────────────────────┐
                                                              ▼
  InventoryService: listens to ORDER_CREATED                  │
                    reserves stock                            │
                    publishes STOCK_RESERVED                  │
                    or STOCK_UNAVAILABLE ───────────────────► │
                                                              ▼
  PaymentService: listens to STOCK_RESERVED                   │
                  charges payment                             │
                  publishes PAYMENT_COMPLETED                 │
                  or PAYMENT_FAILED ──────────────────────► ──┤
                                                              ▼
  ShippingService: listens to PAYMENT_COMPLETED               │
                   schedules shipment                         │
                   publishes ORDER_SHIPPED                    │

  FAILURE — PAYMENT_FAILED:
  InventoryService: listens to PAYMENT_FAILED
                    releases stock reservation (compensation)
                    publishes STOCK_RELEASED
  OrderService: listens to STOCK_RELEASED
                marks order as FAILED (compensation)

  PROS: decentralized, simple, no single point of failure
  CONS: hard to see the big picture, difficult to implement complex flows,
        cyclic dependencies possible, hard to debug/monitor

  2. ORCHESTRATION (centralized coordinator):

  Saga Orchestrator manages the flow: sends commands, receives replies.

  OrderOrchestrator → RESERVE_STOCK command → InventoryService
  OrderOrchestrator ← STOCK_RESERVED reply  ← InventoryService

  OrderOrchestrator → CHARGE_PAYMENT command → PaymentService
  OrderOrchestrator ← PAYMENT_FAILED reply   ← PaymentService

  OrderOrchestrator → RELEASE_STOCK command → InventoryService (compensation)
  OrderOrchestrator → CANCEL_ORDER command  → OrderService (compensation)

  PROS: clear business flow in one place (orchestrator), easy to monitor,
        easy to add steps, clear compensation sequence
  CONS: orchestrator = additional component to build and maintain,
        single point of failure (mitigated by persistent orchestrator state)

  RECOMMENDATION: Use Orchestration for complex sagas (>3 steps).
                  Use Choreography for simple, 2-3 step flows.

SAGA IMPLEMENTATION WITH AXON FRAMEWORK (Spring Boot):

  // Orchestration saga with Axon:

  @Saga
  @ProcessingGroup("order-saga")
  public class OrderSaga {

      @Autowired @Transient
      private CommandGateway commandGateway;

      private String orderId;
      private String customerId;

      @StartSaga
      @SagaEventHandler(associationProperty = "orderId")
      public void on(OrderCreatedEvent event) {
          this.orderId = event.getOrderId();
          this.customerId = event.getCustomerId();

          // Step 1: Reserve inventory
          commandGateway.send(new ReserveStockCommand(
              event.getOrderId(), event.getProductId(), event.getQuantity()));
      }

      @SagaEventHandler(associationProperty = "orderId")
      public void on(StockReservedEvent event) {
          // Step 2: Charge payment
          commandGateway.send(new ChargePaymentCommand(
              event.getOrderId(), customerId, event.getAmount()));
      }

      @SagaEventHandler(associationProperty = "orderId")
      public void on(PaymentChargedEvent event) {
          // Step 3: Schedule shipping
          commandGateway.send(new ScheduleShipmentCommand(event.getOrderId()));
      }

      @SagaEventHandler(associationProperty = "orderId")
      public void on(ShipmentScheduledEvent event) {
          // All steps successful — saga complete
          commandGateway.send(new ConfirmOrderCommand(event.getOrderId()));
          SagaLifecycle.end();   // Saga is complete — remove from tracking
      }

      // COMPENSATION: payment failed
      @SagaEventHandler(associationProperty = "orderId")
      public void on(PaymentFailedEvent event) {
          // Compensate: release the stock that was reserved
          commandGateway.send(new ReleaseStockCommand(event.getOrderId()));
      }

      @SagaEventHandler(associationProperty = "orderId")
      public void on(StockReleasedEvent event) {
          // Compensate: cancel the order
          commandGateway.send(new CancelOrderCommand(orderId, "Payment failed"));
          SagaLifecycle.end();   // Saga complete (with failure)
      }

      // COMPENSATION: stock unavailable
      @SagaEventHandler(associationProperty = "orderId")
      public void on(StockUnavailableEvent event) {
          // No stock compensation needed (nothing reserved)
          commandGateway.send(new CancelOrderCommand(orderId, "Out of stock"));
          SagaLifecycle.end();
      }
  }

SAGA + OUTBOX PATTERN:

  Each saga step must publish its event/command atomically with its DB write.
  Use Outbox Pattern at each step:

  @Transactional
  void handleReserveStockCommand(ReserveStockCommand cmd) {
      // Local transaction:
      stockRepository.reserve(cmd.getProductId(), cmd.getQuantity());

      // Outbox: publish either STOCK_RESERVED or STOCK_UNAVAILABLE atomically:
      outboxRepository.save(OutboxEvent.of(
          "Inventory", cmd.getOrderId(), "StockReserved", ...));
  }
  // Atomic: either both persist (transaction commits) or neither (rollback).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Saga:

- Distributed transactions (2PC) require all services to be available simultaneously; lock resources; scale poorly; couple services tightly
- Result: inconsistent data across services when any step fails

WITH Saga:
→ Each service handles its own local transaction. Compensating transactions restore consistency on failure. Services loosely coupled via events/commands. Eventual consistency maintained without distributed locks.

---

### 🧠 Mental Model / Analogy

> Planning a multi-leg international trip: book flight, hotel, and rental car. Each booking: a separate transaction with a separate vendor. No vendor can see the other's booking. If the car rental falls through at the last moment: cancel the hotel (compensation), cancel the flight (compensation). Each vendor has a cancellation policy (compensating transaction). The travel agent (orchestrator) coordinates the sequence and handles failures. No three-way "atomic" booking exists — but compensation makes the outcome consistent.

"Each booking with a separate vendor" = local transaction in each microservice
"No vendor can see the other's booking" = no shared distributed transaction
"Car rental falls through" = saga step fails (PAYMENT_FAILED, STOCK_UNAVAILABLE)
"Cancel hotel, cancel flight" = compensating transactions executed in reverse
"Each vendor has a cancellation policy" = each service implements a compensating command
"Travel agent coordinates" = Saga Orchestrator manages the flow and failure handling

---

### ⚙️ How It Works (Mechanism)

```
SAGA STATE MACHINE:

  OrderSaga states:
  PENDING → STOCK_RESERVED → PAYMENT_PROCESSING → PAYMENT_CHARGED → SHIPPING_SCHEDULED → COMPLETE
                                                         │
                                                    PAYMENT_FAILED
                                                         │
                                                    STOCK_RELEASING → ORDER_CANCELLED (FAILED)

  Each state transition:
  - Triggered by event received
  - Results in command sent or compensation triggered
  - Saga state persisted (Axon: EventStore; others: saga state table)

IDEMPOTENCY REQUIREMENT:

  Saga steps must be idempotent: if the orchestrator resends a command (network failure),
  the service must handle the duplicate without double-processing.

  Pattern: check if command already processed:
  if (stockReservations.existsByOrderId(cmd.getOrderId())) {
      // Already processed — publish reply event again (idempotent)
      eventPublisher.publish(new StockReservedEvent(cmd.getOrderId()));
      return;
  }
  // First time: process normally
```

---

### 🔄 How It Connects (Mini-Map)

```
Distributed multi-service business process needs consistency without 2PC
        │
        ▼
Saga Pattern ◄──── (you are here)
(sequence of local transactions; compensating transactions on failure; eventual consistency)
        │
        ├── Outbox Pattern: required for reliable event/command publishing at each saga step
        ├── Event-Driven Pattern: Choreography sagas are fully event-driven
        ├── CQRS Pattern: sagas often combined with CQRS for command/query separation
        └── Idempotent Consumer: saga steps must be idempotent (resent commands)
```

---

### 💻 Code Example

```java
// Simple Choreography Saga with Spring Boot + Kafka:

// Step 1: Order Service creates order and publishes event via Outbox:
@Service @RequiredArgsConstructor @Transactional
public class OrderService {
    public Order createOrder(CreateOrderCommand cmd) {
        Order order = orderRepo.save(new Order(cmd.getCustomerId(), cmd.getItems()));

        // Outbox: event will be published to Kafka by relay:
        outboxRepo.save(OutboxEvent.of("Order", order.getId().toString(),
            "OrderCreated", serialize(new OrderCreatedEvent(order))));

        return order;
    }
}

// Step 2: Inventory Service listens and reserves stock:
@Service @KafkaListener(topics = "order-created") @Transactional
public class InventoryService {
    public void on(OrderCreatedEvent event) {
        if (stockRepo.reserve(event.getProductId(), event.getQuantity())) {
            outboxRepo.save(OutboxEvent.of("Inventory", event.getOrderId(),
                "StockReserved", serialize(new StockReservedEvent(event.getOrderId(), ...))));
        } else {
            outboxRepo.save(OutboxEvent.of("Inventory", event.getOrderId(),
                "StockUnavailable", serialize(new StockUnavailableEvent(event.getOrderId()))));
        }
    }
}

// Compensation in Inventory Service:
@KafkaListener(topics = "payment-failed") @Transactional
public void onPaymentFailed(PaymentFailedEvent event) {
    stockRepo.release(event.getOrderId());   // compensating transaction
    outboxRepo.save(OutboxEvent.of("Inventory", event.getOrderId(),
        "StockReleased", serialize(new StockReleasedEvent(event.getOrderId()))));
}

// Compensation in Order Service:
@KafkaListener(topics = "stock-released") @Transactional
public void onStockReleased(StockReleasedEvent event) {
    orderRepo.findByOrderId(event.getOrderId())
        .ifPresent(order -> {
            order.cancel("Payment failed");
            orderRepo.save(order);
        });
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Saga is just a distributed transaction            | Saga does NOT provide ACID isolation. Between saga steps, the intermediate state is visible to other operations (e.g., stock is "reserved" while payment is processing). This is Eventual Consistency, not strong consistency. If strong ACID isolation across services is required, saga is not sufficient — you need a different architecture or accept the coupling of shared-database transactions.                                                   |
| Compensating transactions fully undo the original | Compensating transactions achieve semantic cancellation, not perfect undo. If a payment was charged and then the downstream step failed: the compensation sends a refund (not a database rollback). The refund is a new transaction, not an undo. "Compensation" in Saga means: reaching a consistent end state, not necessarily the original pre-saga state. The user may see: charged → refunded (two transactions visible), not a single clean cancel. |
| Choreography is always simpler than Orchestration | For 2-3 simple steps: Choreography is simpler (no orchestrator component needed). For complex flows (>5 steps, conditional branches, parallel steps, timeout handling): Choreography produces a complex, hard-to-understand web of event handlers. Orchestration provides a clear, readable flow in one component. The "simpler" label reverses at scale. Choose based on saga complexity, not dogma.                                                     |

---

### 🔥 Pitfalls in Production

**Saga without compensating transactions leaving system in inconsistent state:**

```java
// ANTI-PATTERN — saga step fails, no compensation:

// Scenario: Order Saga, step 3 (shipping) fails:
// Step 1: Order created ✓
// Step 2: Stock reserved ✓
// Step 3: Payment charged ✓
// Step 4: Shipping scheduled ✗ (Shipping service returns 500)

// WITHOUT compensation:
// System state:
// - Order: PAYMENT_CHARGED (but not COMPLETE)
// - Stock: RESERVED (never released or fulfilled)
// - Payment: CHARGED (customer was billed)
// - Shipping: NOT scheduled
// Customer: paid, no delivery scheduled, order stuck in PAYMENT_CHARGED state forever.

// FIX — compensation chain for shipping failure:
@SagaEventHandler(associationProperty = "orderId")
public void on(ShipmentFailedEvent event) {
    // 1. Refund payment (compensation for step 3)
    commandGateway.send(new RefundPaymentCommand(event.getOrderId(), event.getAmount()));
}

@SagaEventHandler(associationProperty = "orderId")
public void on(PaymentRefundedEvent event) {
    // 2. Release stock (compensation for step 2)
    commandGateway.send(new ReleaseStockCommand(event.getOrderId()));
}

@SagaEventHandler(associationProperty = "orderId")
public void on(StockReleasedEvent event) {
    // 3. Cancel order (compensation for step 1)
    commandGateway.send(new CancelOrderCommand(orderId, "Shipping failed"));
    SagaLifecycle.end();
}
// Result: customer refunded, stock released, order cancelled.
// Consistent end state even after step 4 failure.
// EVERY saga step needs a corresponding compensation command designed upfront.
```

---

### 🔗 Related Keywords

- `Outbox Pattern` — required at each saga step for reliable event/command publishing
- `Event-Driven Pattern` — Choreography-style sagas are entirely event-driven
- `CQRS Pattern` — often combined with Sagas: commands modify state; events represent what happened
- `Idempotent Consumer` — saga steps must be idempotent (resent commands from orchestrator)
- `Distributed Systems` — Saga solves the distributed consistency problem without 2PC

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Multi-service business process: sequence  │
│              │ of local transactions. Compensating txns │
│              │ undo completed steps on failure.         │
├──────────────┼───────────────────────────────────────────┤
│ STYLES       │ Choreography: event-driven, decentralized│
│              │ Orchestration: coordinator-managed flow  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-service transaction; no 2PC;       │
│              │ eventual consistency acceptable;         │
│              │ long-running business process            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Travel agent: flight, hotel, car booked │
│              │  separately. Car fails: cancel hotel,   │
│              │  cancel flight. Each has a cancel policy."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Outbox Pattern → CQRS → Event Sourcing → │
│              │ Axon Framework → Choreography vs. Orch.  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Saga Pattern achieves eventual consistency but not isolation (the "I" in ACID). Between saga steps, intermediate states are visible to concurrent operations. This creates anomalies: a "lost update" if two concurrent sagas both check stock simultaneously (neither sees the other's reservation until their step completes), or a "dirty read" if a user queries order status while the saga is mid-flight. These are known as "Saga anomalies." What specific patterns (e.g., semantic locks, countermeasures, pivot transactions) does Chris Richardson recommend to handle Saga isolation anomalies in production microservices?

**Q2.** Axon Framework's Saga implementation persists saga state in an event store (Event Sourcing + CQRS model) — each state transition is recorded as an event. This means saga state is durable: if the orchestrator service crashes mid-saga, on restart it replays events to reconstruct the current saga state and continues from where it left off. Compare this approach to a saga state machine persisted in a relational database (status column in a table). What are the tradeoffs in terms of durability, auditability, replay capability, and operational complexity?
