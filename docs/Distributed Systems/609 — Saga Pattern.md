---
layout: default
title: "Saga Pattern"
parent: "Distributed Systems"
nav_order: 609
permalink: /distributed-systems/saga-pattern/
number: "609"
category: Distributed Systems
difficulty: ★★★
depends_on: "Idempotency (Distributed), Two-Phase Commit"
used_by: "Microservices, Axon Framework, Temporal, AWS Step Functions"
tags: #advanced, #distributed, #transactions, #microservices, #eventual-consistency
---

# 609 — Saga Pattern

`#advanced` `#distributed` `#transactions` `#microservices` `#eventual-consistency`

⚡ TL;DR — **Saga Pattern** manages long-running distributed transactions as a sequence of local transactions, each publishing events to trigger the next step — and each with a **compensating transaction** to undo its work if a later step fails, achieving eventual consistency without distributed locks.

| #609 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Idempotency (Distributed), Two-Phase Commit | |
| **Used by:** | Microservices, Axon Framework, Temporal, AWS Step Functions | |

---

### 📘 Textbook Definition

**Saga Pattern** (Hector Garcia-Molina & Kenneth Salem, 1987; popularized in microservices by Chris Richardson) is a pattern for managing distributed transactions across multiple services. A Saga is a sequence of local transactions: T1 → T2 → T3 → ... → Tn. Each Ti is a local ACID transaction within a single service. On step failure at Ti: compensating transactions (C(i-1) → C(i-2) → ... → C1) are executed in reverse order to undo previously committed work. Two coordination styles: (1) **Choreography** — each service publishes domain events; downstream services react. No central coordinator. Decoupled but hard to track overall state. (2) **Orchestration** — a central saga orchestrator (saga manager) sends commands to each service; services return events. Explicit workflow. Easier to monitor and debug. **Trade-offs vs. 2PC**: Sagas avoid distributed locks and two-phase commit. Benefit: higher availability (no blocked resources). Cost: no ACID isolation across services — intermediate states are visible (T1 committed, T2 pending = partial state visible to concurrent readers). Requires explicit compensation logic for each step. Compensating transactions must be idempotent. Used by: e-commerce order processing (reserve inventory → charge payment → schedule fulfillment), travel booking (book flight → book hotel → rent car).

---

### 🟢 Simple Definition (Easy)

Saga: instead of one big atomic transaction across 3 services (which needs distributed locks), you do 3 smaller transactions, one at a time. If step 3 fails: you run "undo step 2" and "undo step 1." Like booking a vacation: book flight (step 1), book hotel (step 2), rent car (step 3). Car unavailable: cancel hotel, cancel flight (compensations). Each cancellation is a separate local operation on each service. No global lock holding all three services hostage simultaneously.

---

### 🔵 Simple Definition (Elaborated)

Saga vs 2PC: 2PC creates a distributed transaction that locks resources across all 3 services simultaneously. High availability cost: if the coordinator crashes, everything is frozen. Saga: no locks. Each step commits independently. If a later step fails: run compensating transactions (cancel/undo). Availability benefit: only the failing service is impacted during compensation. Weakness: during the saga execution, other requests can see partially committed state (flight booked, hotel not yet confirmed). This is "eventual consistency" — the saga will eventually reach a consistent state (fully committed or fully compensated), but intermediate states are visible.

---

### 🔩 First Principles Explanation

**Saga state machine, choreography vs orchestration, and compensation design:**

```
SAGA EXECUTION MODEL:

  Business operation: "Place Order"
  Steps:
    T1: Order Service — create order (status=PENDING).
    T2: Inventory Service — reserve items.
    T3: Payment Service — charge customer.
    T4: Fulfillment Service — schedule shipment.
    
  Compensating transactions (rollback path):
    C1: Order Service — cancel order (status=CANCELLED).
    C2: Inventory Service — release reservation.
    C3: Payment Service — refund payment.
    C4: Fulfillment Service — cancel shipment.
    
  SUCCESS PATH:
    T1 → T2 → T3 → T4. Order complete. Status: FULFILLED.
    
  FAILURE at T3 (payment fails):
    T1 ✓ (committed: order created)
    T2 ✓ (committed: inventory reserved)
    T3 ✗ (payment failed: card declined)
    
    Compensation:
    C2: Inventory — release reservation. (T2 compensation)
    C1: Order — cancel order. (T1 compensation)
    
    T4: never executed (saga stopped at T3 failure).
    C3, C4: not needed (T3, T4 never committed).
    
  FAILURE at T4 (fulfillment service down):
    T1 ✓ T2 ✓ T3 ✓ (payment charged!)
    T4 ✗ (fulfillment service unavailable)
    
    Compensation:
    C3: Payment — refund customer. (CRITICAL: must not fail!)
    C2: Inventory — release reservation.
    C1: Order — cancel order.
    
  COMPENSATION REQUIREMENTS:
    1. Idempotent: compensating transaction may be retried.
    2. Eventually complete: must succeed eventually (cannot fail permanently).
    3. Semantically correct: undoes BUSINESS EFFECT, not necessarily DB state.
       Example: cannot DELETE a payment record after charging (audit trail needed).
       Instead: INSERT refund_transaction. Payment history preserved.

CHOREOGRAPHY-BASED SAGA:

  No central coordinator. Each service: listens for domain events, publishes domain events.
  
  Flow:
    1. OrderService: creates order. Publishes: OrderCreated event.
    2. InventoryService: receives OrderCreated. Reserves items. 
       Publishes: InventoryReserved (success) or InventoryReservationFailed (failure).
    3. PaymentService: receives InventoryReserved. Charges payment.
       Publishes: PaymentCharged or PaymentFailed.
    4. FulfillmentService: receives PaymentCharged. Schedules shipment.
       Publishes: ShipmentScheduled or FulfillmentFailed.
       
  COMPENSATION FLOW (payment failed):
    PaymentService publishes: PaymentFailed.
    InventoryService: receives PaymentFailed → releases reservation → publishes: InventoryReleased.
    OrderService: receives InventoryReleased → cancels order → publishes: OrderCancelled.
    
  PROS:
    Decoupled: services don't know about each other (only about events).
    No single point of failure (no coordinator).
    Simple for short sagas (2-3 steps).
    
  CONS:
    Hard to understand overall flow (logic distributed across services).
    Difficult to track saga progress (which step is the order at?).
    Cyclic dependencies: InventoryService must know about OrderCancelled, PaymentFailed, etc.
    Hard to implement complex business logic (conditional branches, retries).
    Testing: must simulate entire event chain.

ORCHESTRATION-BASED SAGA:

  Central saga orchestrator sends commands; services respond with events.
  
  Orchestrator state machine:
    State: PENDING → INVENTORY_RESERVED → PAYMENT_CHARGED → FULFILLED
    Compensating state: COMPENSATING → INVENTORY_RELEASED → CANCELLED
    
  Flow:
    1. Orchestrator: sends CreateOrder command to OrderService.
       OrderService: responds: OrderCreated.
    2. Orchestrator: sends ReserveInventory command to InventoryService.
       InventoryService: responds: InventoryReserved or InventoryFailed.
    3. Orchestrator: sends ChargePayment command to PaymentService.
       PaymentService: responds: PaymentCharged or PaymentFailed.
    4. Orchestrator: sends ScheduleFulfillment command to FulfillmentService.
       FulfillmentService: responds: FulfillmentScheduled or FulfillmentFailed.
       
  COMPENSATION FLOW (payment failed):
    Orchestrator: receives PaymentFailed.
    Orchestrator: sends ReleaseInventory command to InventoryService.
    InventoryService: responds: InventoryReleased.
    Orchestrator: sends CancelOrder command to OrderService.
    OrderService: responds: OrderCancelled.
    Orchestrator: marks saga as COMPENSATED.
    
  PROS:
    Centralized saga logic: easy to understand, debug, and monitor.
    Complex logic: easy to add conditions, parallel steps, retries.
    Observable: orchestrator tracks exact state of saga.
    Services simpler: just respond to commands (don't need to know about other services).
    
  CONS:
    Orchestrator is a central component (potential bottleneck, needs to be HA).
    More coupling: orchestrator knows about all services.
    
  IMPLEMENTATION: Temporal, Axon Framework, AWS Step Functions, Apache Camel.

SAGA ISOLATION PROBLEM (THE COUNTERMEASURES):

  2PC has ACID isolation: T2 can't see T1's uncommitted data.
  Saga has NO isolation: T1 commits, T2 commits. Between T1 and T2:
    Concurrent request R reads order (T1 committed) → sees "PENDING" status.
    R tries to act on partial state. Data integrity risk.
    
  COUNTERMEASURES:
  
  1. SEMANTIC LOCK (pessimistic):
     T1: sets flag "processing=true" on the record.
     Concurrent requests: "if processing=true, reject or queue."
     T2: updates. Clears "processing=false".
     Drawback: similar to locks. Adds latency.
     
  2. COMMUTATIVE UPDATES:
     Design operations to be order-independent.
     Instead of "set inventory=50": use "decrement inventory by 1."
     Multiple concurrent sagas: decrement independently. No interference.
     Compensation: increment by 1 (undo).
     
  3. PESSIMISTIC VIEW (read after write):
     Read operations: query only fully-committed data.
     Example: only show orders with status=FULFILLED or CANCELLED (not PENDING).
     Users don't see partial state. But: orders in PENDING state invisible during saga.
     
  4. REREAD VALUE:
     Before compensation: re-read current value to check if already compensated.
     Prevent double-compensation.
     
  5. VERSION FILE (audit log of changes):
     Record all updates as append-only events (event sourcing).
     Compensation: add a "compensating event."
     No actual deletion/update of records.
     Full audit trail maintained.

SAGA IDEMPOTENCY (CRITICAL):

  Saga step failures cause retries. Each step MUST be idempotent.
  
  Order of failure:
    Orchestrator: sends ReserveInventory. Network drops. No response.
    Orchestrator: timeout → retries: sends ReserveInventory again.
    InventoryService: must detect duplicate (idempotency key = sagaId + stepId).
    InventoryService: checks "have I already reserved for saga abc-123, step 2?"
    If yes: return cached result. Don't double-reserve.
    
  COMPENSATION IDEMPOTENCY:
    Compensation retry: "release inventory" sent twice.
    InventoryService: "already released (inventory not negative)." 
    Idempotent: second release is a no-op.

TEMPORAL WORKFLOW (ORCHESTRATION SAGA):

  Temporal: durable execution engine for saga orchestration.
  
  Key property: workflow code is "durable" — if server crashes mid-workflow,
  workflow replays from last checkpoint (event sourced execution log).
  No saga state lost on crash. Automatic resumption.
  
  @WorkflowImpl
  public class OrderSagaWorkflow implements OrderSaga {
      
      private final InventoryActivities inventory = Workflow.newActivityStub(
          InventoryActivities.class,
          ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(30)).build());
          
      private final PaymentActivities payment = Workflow.newActivityStub(
          PaymentActivities.class, 
          ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(30)).build());
  
      @Override
      public OrderResult processOrder(OrderRequest request) {
          // T1: Reserve inventory (auto-retry on failure by Temporal)
          try {
              inventory.reserve(request.getOrderId(), request.getItems());
          } catch (ActivityFailure e) {
              // T1 failed (no compensation needed — T1 is first step)
              return OrderResult.failed("Inventory unavailable");
          }
          
          // T2: Charge payment
          try {
              payment.charge(request.getOrderId(), request.getPaymentDetails());
          } catch (ActivityFailure e) {
              // T2 failed: compensate T1
              inventory.release(request.getOrderId()); // Compensation C1
              return OrderResult.failed("Payment failed");
          }
          
          // Success: T3 (fulfillment)
          fulfillment.schedule(request.getOrderId());
          return OrderResult.success();
          
          // If this workflow crashes and restarts: Temporal replays from checkpoint.
          // Already-executed activities: not re-executed (idempotent by Temporal design).
          // Workflow picks up where it left off.
      }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT saga (only 2PC for distributed transactions):
- All services locked simultaneously during transaction → high latency, low throughput
- Coordinator failure → all resources frozen until recovery
- Scale limitation: 2PC doesn't scale to microservices (each needs to be a 2PC participant)

WITH saga:
→ No distributed locks: each service commits independently → high availability
→ Scale: works across any number of services without 2PC overhead
→ Failure isolation: only failing step blocked; others proceed (vs. all blocked in 2PC)

---

### 🧠 Mental Model / Analogy

> Trip booking: book flight, book hotel, rent car — three separate reservations at three separate companies. Car unavailable: cancel hotel, cancel flight — three separate cancellation calls. No "mega lock" holding all three travel companies' systems frozen while you decide. Each transaction completes independently. Compensation = cancellation with explicit reversal. The state during booking (flight booked, hotel not yet confirmed) is "partially done" — you might get an email saying "flight confirmed" before the hotel replies.

"Three separate travel companies" = three independent microservices with local databases
"Cancellation call" = compensating transaction per service
"Email saying flight confirmed before hotel replies" = intermediate saga state visible externally

---

### ⚙️ How It Works (Mechanism)

```
OUTBOX + SAGA (reliable event publishing):

  To avoid: T1 commits DB + sends event, then crashes before event is sent.
  Solution: Outbox pattern.
  
  T1: 
    BEGIN DB TRANSACTION:
      UPDATE orders SET status='pending' WHERE id=...
      INSERT INTO outbox (event_type, payload) VALUES ('OrderCreated', ...)
    COMMIT.
    
  Outbox relay (separate process):
    Polls outbox table.
    Publishes events to Kafka/RabbitMQ.
    Marks published (DELETE or status='published').
    
  Guarantee: event published exactly-once (at-least-once + consumer idempotency).
```

---

### 🔄 How It Connects (Mini-Map)

```
Two-Phase Commit (alternative: distributed atomic commit with locks)
        │
        ▼ (sagas replace 2PC for microservices)
Saga Pattern ◄──── (you are here)
(sequence of local transactions + compensations = distributed eventual consistency)
        │
        ├── Choreography vs Orchestration: the two coordination approaches
        ├── Outbox Pattern: reliable event publishing for choreography sagas
        └── Idempotency: each saga step must be safe to retry
```

---

### 💻 Code Example

**Choreography saga with Kafka (Spring Boot):**

```java
// Order Service: publishes OrderCreated event.
@Service
public class OrderService {
    
    @Transactional  // Local DB transaction + outbox (atomically)
    public Order placeOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.create(req)); // status=PENDING
        eventPublisher.publish(new OrderCreated(order.getId(), req.getItems(), req.getPayment()));
        return order;
    }
    
    @KafkaListener(topics = "inventory-events")
    public void onInventoryEvent(InventoryEvent event) {
        if (event instanceof InventoryReserved) {
            // Inventory reserved: no action needed (PaymentService reacts next)
        } else if (event instanceof InventoryReservationFailed) {
            // Inventory failed: cancel order (saga complete with failure).
            orderRepo.updateStatus(event.getOrderId(), OrderStatus.CANCELLED);
        }
    }
    
    @KafkaListener(topics = "payment-events")
    public void onPaymentEvent(PaymentEvent event) {
        if (event instanceof PaymentFailed) {
            orderRepo.updateStatus(event.getOrderId(), OrderStatus.CANCELLED);
        }
    }
}

// Inventory Service: reacts to OrderCreated, publishes result.
@Service
public class InventoryService {
    
    @KafkaListener(topics = "order-events")
    @Transactional
    public void onOrderCreated(OrderCreated event) {
        // Idempotency: check if already processed this sagaId.
        if (processedEvents.contains(event.getOrderId())) return;
        
        try {
            reserve(event.getOrderId(), event.getItems());
            eventPublisher.publish(new InventoryReserved(event.getOrderId()));
        } catch (InsufficientInventoryException e) {
            eventPublisher.publish(new InventoryReservationFailed(event.getOrderId(), e.getMessage()));
        }
        processedEvents.add(event.getOrderId()); // Mark as processed (idempotency).
    }
    
    @KafkaListener(topics = "payment-events")  // Compensation trigger.
    @Transactional
    public void onPaymentFailed(PaymentFailed event) {
        release(event.getOrderId()); // C2: release reservation.
        eventPublisher.publish(new InventoryReleased(event.getOrderId()));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Sagas provide ACID transactions across services | Sagas provide ACD but NOT Isolation. T1 commits, T2 pending: concurrent requests can read T1's committed state. This is "eventual consistency" — the saga will converge to a consistent state, but during execution: intermediate states are visible. This is fundamentally different from 2PC where no intermediate state is visible (isolation guaranteed) |
| Compensation is equivalent to rollback | Compensation is a semantic undo, not a database rollback. Rollback: DB state reverts as if the transaction never happened. Compensation: a NEW transaction that reverses the business effect. Example: cannot "rollback" a sent email (side effect already occurred). Compensation: send a follow-up email "please disregard previous email." Compensation preserves audit history; rollback erases it |
| Choreography is always better than orchestration (less coupling) | Choreography reduces service-to-service coupling but increases event-schema coupling and operational complexity. Debugging a failed saga in choreography: requires tracing events across all services. Adding a new step to a choreography saga: requires changing multiple services. Orchestration: change only the orchestrator. For complex sagas (> 3 steps, conditional logic, retry strategies): orchestration is significantly easier to maintain |
| Sagas can handle any distributed transaction use case | Sagas are best for long-running business transactions where eventual consistency is acceptable. They are NOT suitable for: short, tight financial transactions requiring strict isolation (use 2PC or database-level transactions); transactions requiring read-your-writes consistency in real-time (saga's eventual consistency means writes may not be immediately visible); very high-frequency operations where compensation overhead is unacceptable |

---

### 🔥 Pitfalls in Production

**Lost compensation event — saga stuck in partially compensated state:**

```
SCENARIO: Order saga. T3 (payment charged). T4 (fulfillment) fails.
  Orchestrator: sends C3 (refund) command to PaymentService.
  PaymentService: processes refund. Returns RefundComplete.
  Network: drops response. Orchestrator: never receives RefundComplete.
  
  What happens:
    Orchestrator: retry timeout → sends C3 again ("refund for order X").
    PaymentService: must be idempotent (second refund = no-op, return cached RefundComplete).
    
  IF PaymentService is NOT idempotent:
    Second C3: issues SECOND REFUND. Customer: refunded twice. Company: loses money.
    
BAD: Compensation not idempotent:
  @PostMapping("/refund/{orderId}")
  public void refund(@PathVariable String orderId) {
      Payment p = paymentRepo.findByOrderId(orderId);
      stripeRefundService.refund(p.getStripeChargeId()); // WRONG: no idempotency check!
      p.setStatus(PaymentStatus.REFUNDED);
      paymentRepo.save(p);
  }
  // If called twice: two Stripe refund API calls → two refunds.

FIX: Idempotent compensation with saga+step as idempotency key:
  @PostMapping("/refund/{orderId}")
  public void refund(@PathVariable String orderId) {
      Payment p = paymentRepo.findByOrderId(orderId);
      
      // Idempotency check: already refunded?
      if (p.getStatus() == PaymentStatus.REFUNDED) {
          log.info("Refund for order {} already processed. Returning.", orderId);
          return; // Idempotent: no-op on duplicate.
      }
      
      // Atomic: refund + mark status (prevents race condition on concurrent retries).
      try {
          String refundId = stripeRefundService.refund(
              p.getStripeChargeId(),
              "idempotency_key=" + orderId + "-refund"  // Stripe idempotency key too!
          );
          p.setStatus(PaymentStatus.REFUNDED);
          p.setRefundId(refundId);
          paymentRepo.save(p);
      } catch (StripeException e) {
          throw new CompensationFailedException("Refund failed for order " + orderId, e);
          // Saga orchestrator: will retry. Idempotency key prevents double refund.
      }
  }
  
SAGA STUCK: orchestrator crashes mid-saga — recovery needed:
  Saga state persisted in DB (orchestrator must persist state after each step).
  On restart: orchestrator resumes from persisted state.
  Temporal: automatically recovers (durable execution).
  Custom orchestrators: must implement saga state persistence + recovery logic.
```

---

### 🔗 Related Keywords

- `Choreography vs Orchestration` — the two coordination styles for saga execution
- `Outbox Pattern` — reliable event publishing that enables choreography sagas
- `Idempotency` — each saga step and compensation must be safely retryable
- `Two-Phase Commit` — what sagas replace for distributed transactions in microservices

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ N local transactions + N compensations.  │
│              │ Failure at step i: reverse steps i-1...1.│
│              │ No distributed locks. Eventual consistency│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-service business transactions where │
│              │ eventual consistency is acceptable;      │
│              │ replacing 2PC in microservices           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ ACID isolation required (financial txns  │
│              │ needing strict read isolation); operations│
│              │ that can't be compensated (sent emails,  │
│              │ irrevocable external side effects)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Book trip in 3 steps; failure = call    │
│              │  each company to cancel. No mega-lock."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Choreography vs Orchestration → Outbox  │
│              │ Pattern → Idempotency → Temporal         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Saga has 5 steps: T1 (Order), T2 (Inventory), T3 (Payment), T4 (Loyalty Points), T5 (Fulfillment). T5 fails. The compensation C4 (reverse loyalty points) fails permanently (loyalty service is down for 3 hours). The orchestrator retries C4 for 3 hours. Meanwhile: the customer has already been charged (T3). What do you do? What is the "saga failure escalation" strategy when compensations themselves fail? How does this compare to 2PC's handling of the same scenario?

**Q2.** Choreography sagas use domain events to trigger each step. If the event bus (Kafka) goes down between T2 (InventoryReserved) and T3 (PaymentService waiting for InventoryReserved): what happens? How long is the saga paused? What is the maximum time to complete the saga if Kafka is unavailable for 1 hour? How do you implement "saga timeout" — detecting that a saga has been stuck in an intermediate state too long and triggering compensation automatically?
