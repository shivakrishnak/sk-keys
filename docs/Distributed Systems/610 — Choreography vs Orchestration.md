---
layout: default
title: "Choreography vs Orchestration"
parent: "Distributed Systems"
nav_order: 610
permalink: /distributed-systems/choreography-vs-orchestration/
number: "610"
category: Distributed Systems
difficulty: ★★★
depends_on: "Saga Pattern, Event-Driven Architecture"
used_by: "Microservices, Kafka, Temporal, AWS Step Functions, Axon Framework"
tags: #advanced, #distributed, #microservices, #coordination, #event-driven
---

# 610 — Choreography vs Orchestration

`#advanced` `#distributed` `#microservices` `#coordination` `#event-driven`

⚡ TL;DR — **Choreography** lets services react to events independently (decoupled, hard to trace); **Orchestration** uses a central conductor sending commands (easy to trace, explicit workflow) — choose based on complexity and observability requirements.

| #610 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Saga Pattern, Event-Driven Architecture | |
| **Used by:** | Microservices, Kafka, Temporal, AWS Step Functions, Axon Framework | |

---

### 📘 Textbook Definition

**Choreography** is a decentralized coordination approach where each service publishes domain events and subscribes to events from other services, reacting independently — no central coordinator. Services know WHAT events happened; they decide HOW to react. Analogy: jazz band improvisation — each musician listens and responds. **Orchestration** is a centralized coordination approach where a saga orchestrator sends explicit commands to services and receives result events; services are "workers" that execute specific commands. Analogy: symphony orchestra conductor — musicians follow explicit instructions. **Trade-offs**: Choreography — lower coupling, resilient (no SPOF), but: emergent complexity (workflow logic scattered), hard to trace/debug, testing requires full event simulation. Orchestration — explicit workflow (single view of business process), easy to debug/monitor, but: orchestrator as potential SPOF (needs HA), orchestrator knows all services (coupling through orchestrator). In practice: choreography for simple (1-3 step) flows with stable contracts; orchestration for complex (4+ step), conditional, retry-heavy workflows. Hybrid: top-level orchestration + internal service-level choreography.

---

### 🟢 Simple Definition (Easy)

Choreography: a flash mob dance. Each dancer knows the routine and watches others — no director. When dancer A does move 1: dancer B knows to do move 2. Decentralized. Hard to know if everyone is in sync. Orchestration: directed movie scene. Director calls "Action!" Actor A does their line. Director: "Cut! Now Actor B." Central control. Easy to see what's happening. Hard if the director goes missing. Choose: flash mob for simple, stable dances; director for complex, multi-actor scenes.

---

### 🔵 Simple Definition (Elaborated)

When to pick which: Choreography — good for 2-3 service flows that are unlikely to change. "Order created → ship it" (2 services, simple). Bad for: 10-service order processing with conditional paths. Orchestration — good for complex multi-step workflows with explicit error handling and retry. "Order → inventory → payment → fraud check → fulfillment → notify" (6 steps, conditional on fraud result). The operational advantage of orchestration: look at ONE place (orchestrator dashboard) to see where an order is stuck. With choreography: trace events across 6 services' logs to find where things went wrong.

---

### 🔩 First Principles Explanation

**Choreography and orchestration mechanics, trade-offs, and hybrid approaches:**

```
CHOREOGRAPHY: DECENTRALIZED EVENT REACTION

  Event bus (Kafka): topics per domain event.
  
  Service A (Order): publishes OrderPlaced.
  Service B (Inventory): subscribes to OrderPlaced. Reacts: reserves. Publishes InventoryReserved.
  Service C (Payment): subscribes to InventoryReserved. Reacts: charges. Publishes PaymentCharged.
  Service D (Fulfillment): subscribes to PaymentCharged. Reacts: ships. Publishes OrderShipped.
  
  FLOW VISUALIZATION:
    OrderPlaced ──► InventoryService → InventoryReserved ──► PaymentService → PaymentCharged ──► FulfillmentService
    
  Each service: knows only about the events it cares about.
  OrderService: doesn't know InventoryService exists (never directly calls it).
  
  FAILURE HANDLING (choreography):
    PaymentService: publishes PaymentFailed.
    InventoryService: subscribes to PaymentFailed → releases reservation → publishes InventoryReleased.
    OrderService: subscribes to InventoryReleased → cancels order.
    
    EVENT SUBSCRIPTION MAP grows complex:
    InventoryService: subscribes to: OrderPlaced, PaymentFailed, FulfillmentFailed.
    OrderService: subscribes to: InventoryReservationFailed, PaymentFailed, ShipmentFailed, OrderShipped.
    
    With 5 services and multiple failure modes: subscription map = complex web.
    Each service: needs to know about events from ALL other services (despite "loose coupling").
    
  CHOREOGRAPHY ANTI-PATTERN: "Spaghetti Events"
    At scale (10+ services, 30+ event types):
    Service A: subscribes to 8 event types from 5 services.
    Service B: subscribes to 10 event types from 6 services.
    Adding new step: which services need new event subscriptions?
    Where is the business logic for "Order Processing"? Scattered across 10 services.
    Answer: "grep the codebases."
    
  TESTING CHOREOGRAPHY:
    To test "order processing end-to-end":
    Must publish OrderPlaced event → verify all downstream services react correctly.
    Requires: full event infrastructure (Kafka), all services running.
    Integration test: high infrastructure overhead.
    Unit test: mock event publishing. Miss integration bugs.

ORCHESTRATION: CENTRALIZED COMMAND-AND-CONTROL

  Saga Orchestrator: tracks overall saga state. Sends commands. Receives events.
  
  Orchestrator workflow for "Place Order":
    1. Send Command: CreateOrder to OrderService. 
       Wait: OrderCreated event.
    2. Send Command: ReserveInventory to InventoryService.
       Wait: InventoryReserved or InventoryFailed.
    3a. If InventoryFailed: Send Command: CancelOrder to OrderService. → COMPENSATED.
    3b. If InventoryReserved: Send Command: ChargePayment to PaymentService.
       Wait: PaymentCharged or PaymentFailed.
    4a. If PaymentFailed: Send Command: ReleaseInventory. Send Command: CancelOrder. → COMPENSATED.
    4b. If PaymentCharged: Send Command: ScheduleFulfillment to FulfillmentService.
       Wait: FulfillmentScheduled or FulfillmentFailed.
    5a. If FulfillmentFailed: → Compensation chain.
    5b. If FulfillmentScheduled: → Order complete.
    
  SERVICES: each service only responds to commands addressed to it.
    OrderService: listens for CreateOrder, CancelOrder commands.
    Does NOT know about InventoryService or PaymentService.
    
  OBSERVABILITY:
    Orchestrator state table:
    | SagaID | Step       | Status   | StartedAt           | CompletedAt         |
    |--------|------------|----------|---------------------|---------------------|
    | abc-1  | Payment    | Running  | 2024-01-15 10:00:05 | -                   |
    | abc-2  | Inventory  | Failed   | 2024-01-15 10:00:01 | 2024-01-15 10:00:03 |
    | abc-3  | Fulfilled  | Complete | 2024-01-15 09:59:55 | 2024-01-15 10:00:10 |
    
    Customer support: "Where is order abc-1?" → "In payment processing, started 10:00:05."
    
  ORCHESTRATOR FAILURE:
    Orchestrator is a stateful service. Needs HA.
    Solution: run orchestrator as 3-replica deployment.
    Saga state persisted in DB. On crash: any replica can resume.
    Temporal: durable execution engine specifically designed for orchestrator HA.
    
  TESTING ORCHESTRATION:
    Unit test orchestrator: mock service responses. Test workflow logic without real services.
    Integration test: test each service individually (send command, verify event).
    No need to run all services simultaneously for unit tests.

COMPARISON TABLE:

  Aspect             | Choreography                    | Orchestration
  ───────────────────┼─────────────────────────────────┼────────────────────────────────
  Workflow visibility| Scattered across services        | Centralized in orchestrator
  Service coupling   | Services coupled to event schema | Services decoupled from each other
  Single point of failure | None (all services equal) | Orchestrator (must be HA)
  Complexity ceiling | Good for < 3 steps               | Good for any complexity
  Error handling     | Each service adds error logic    | Centralized in orchestrator
  Testing            | Full integration needed          | Unit testable per layer
  Debugging          | Trace across all services' logs  | Single orchestrator log/state
  Adding new step    | All services potentially updated | Change only orchestrator
  Operations at scale| Spaghetti events at 10+ services | Orchestrator bottleneck at very high scale
  Best for           | Simple, stable, asynchronous flows| Complex, conditional, auditable flows
  
HYBRID APPROACH (most production systems):

  Top-level business processes: orchestrated (order processing, user onboarding).
  Internal service reactions: choreographed (inventory service reacts to its own events internally).
  
  Example:
    Order saga: ORCHESTRATED (orchestrator sends commands to Inventory, Payment, Fulfillment).
    Internal to InventoryService: microevents choreographed within the service
      (inventory reserved → trigger warehouse allocation → trigger supplier notification).
    From the orchestrator's perspective: InventoryService is a black box.
    Internally: InventoryService uses its own event bus for internal coordination.
    
  This isolates complexity: top-level flow is observable and explicit.
  Internal service complexity: each team owns their internal coordination style.

AWS STEP FUNCTIONS (MANAGED ORCHESTRATION):

  State machine as a managed service:
    {
      "Comment": "Order Processing Saga",
      "StartAt": "ReserveInventory",
      "States": {
        "ReserveInventory": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:us-east-1:...:inventory-reserve",
          "Catch": [{"ErrorEquals": ["InsufficientInventory"], "Next": "CancelOrder"}],
          "Next": "ChargePayment"
        },
        "ChargePayment": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:us-east-1:...:payment-charge",
          "Catch": [{"ErrorEquals": ["PaymentFailed"], "Next": "ReleaseInventory"}],
          "Next": "ScheduleFulfillment"
        },
        "ScheduleFulfillment": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:us-east-1:...:fulfillment-schedule",
          "End": true
        },
        "ReleaseInventory": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:us-east-1:...:inventory-release",
          "Next": "CancelOrder"
        },
        "CancelOrder": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:us-east-1:...:order-cancel",
          "End": true
        }
      }
    }
    
  Managed HA, automatic retry, visual workflow debugger.
  Execution history: every state transition logged. Debuggable.
  Cost: per state transition. At very high volume: can be expensive.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT explicit coordination style:
- Ad-hoc service-to-service calls: tight coupling, hard to change
- No clear ownership of business process flow: logic scattered
- Both styles are valid — choosing correctly matters for maintainability

WITH choreography:
→ Services truly decoupled: change Inventory service without touching Payment service
→ Resilient: no orchestrator SPOF

WITH orchestration:
→ Observable: one place to see the state of any running business process
→ Maintainable: complex flows with conditions and compensations in one place

---

### 🧠 Mental Model / Analogy

> Choreography = dominos falling. You tip the first; each domino reacts to the previous one falling, no one is in charge. Easy to set up simple chains; hard to debug which domino stopped mid-chain without watching every single one. Orchestration = factory assembly line with a supervisor. Supervisor: "Worker A: do step 1." Worker A reports back. Supervisor: "Worker B: do step 2." One supervisor knows exactly where the product is in the assembly process.

"Dominos reacting to each other" = services reacting to domain events in choreography
"Supervisor directing workers explicitly" = orchestrator sending commands in orchestration
"Watching every domino" = distributed tracing needed to debug choreography

---

### ⚙️ How It Works (Mechanism)

```
CHOREOGRAPHY (Kafka):
  Each service: has its own consumer group for relevant event topics.
  Event published → all consumers in subscribed groups receive it.
  Each service: processes event, publishes new event (or not).
  No central coordinator tracking state.

ORCHESTRATION (Temporal/Step Functions):
  Orchestrator: persists saga state (current step, results so far).
  Sends command → waits for response event (async message pattern).
  On response: advance saga state machine → send next command.
  Saga state durable: crash → resume from last persisted state.
```

---

### 🔄 How It Connects (Mini-Map)

```
Saga Pattern (sequence of steps requiring coordination)
        │
        ▼
Choreography vs Orchestration ◄──── (you are here)
(two ways to coordinate saga steps: event-driven vs command-driven)
        │
        ├── Outbox Pattern: enables reliable event publishing for choreography
        ├── Temporal: production-grade orchestration engine
        └── Event-Driven Architecture: broader context for choreography
```

---

### 💻 Code Example

**Orchestration with Temporal workflow:**

```java
// Temporal Orchestration Workflow:
@WorkflowInterface
public interface OrderSagaWorkflow {
    @WorkflowMethod
    OrderResult processOrder(OrderRequest request);
}

@WorkflowImpl
public class OrderSagaWorkflowImpl implements OrderSagaWorkflow {
    
    // Activity stubs: represent external service calls.
    // Each call: auto-retry with configurable policy. Durable.
    private final InventoryActivities inventory = Workflow.newActivityStub(
        InventoryActivities.class,
        ActivityOptions.newBuilder()
            .setStartToCloseTimeout(Duration.ofSeconds(30))
            .setRetryOptions(RetryOptions.newBuilder()
                .setMaximumAttempts(3)
                .setInitialInterval(Duration.ofSeconds(1))
                .build())
            .build());
    
    private final PaymentActivities payment = Workflow.newActivityStub(
        PaymentActivities.class,
        ActivityOptions.newBuilder()
            .setStartToCloseTimeout(Duration.ofSeconds(60))
            .build());
    
    @Override
    public OrderResult processOrder(OrderRequest request) {
        String orderId = request.getOrderId();
        
        // T1: Reserve inventory (auto-retry on transient failure)
        InventoryResult invResult = inventory.reserve(orderId, request.getItems());
        if (!invResult.isSuccess()) {
            return OrderResult.failed("Inventory: " + invResult.getMessage());
        }
        
        // T2: Charge payment
        PaymentResult payResult;
        try {
            payResult = payment.charge(orderId, request.getPaymentToken(), request.getAmount());
        } catch (ActivityFailure e) {
            // Payment failed: compensate T1
            inventory.release(orderId);  // C1: release reservation
            return OrderResult.failed("Payment failed");
        }
        
        // T3: Schedule fulfillment (non-compensatable if this fails — email customer to retry)
        fulfillment.schedule(orderId, request.getShippingAddress());
        
        return OrderResult.success(payResult.getTransactionId());
        
        // KEY: if Temporal worker crashes at ANY point:
        // On restart: workflow REPLAYS from beginning (Temporal's event sourcing).
        // Activities already completed: NOT re-executed (idempotent by design).
        // Workflow: continues from last successful step.
        // No manual recovery code needed.
    }
}

// Starting a saga:
WorkflowClient client = WorkflowClient.newInstance(WorkflowServiceStubs.newLocalServiceStubs());
OrderSagaWorkflow workflow = client.newWorkflowStub(
    OrderSagaWorkflow.class,
    WorkflowOptions.newBuilder()
        .setWorkflowId("order-" + orderId)  // Idempotency: same orderId → same workflow ID
        .setTaskQueue("order-processing")
        .setWorkflowExecutionTimeout(Duration.ofMinutes(30))
        .build());

// Async: returns immediately, saga runs in background.
WorkflowClient.start(workflow::processOrder, orderRequest);

// Or synchronous: wait for result.
OrderResult result = workflow.processOrder(orderRequest);
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Choreography has no coupling — services are completely independent | Choreography replaces service coupling with EVENT SCHEMA coupling. Service A publishes "OrderCreated" event with specific fields. Service B depends on that schema. Change the event schema: all subscribers break. In orchestration: schema coupling is contained to orchestrator ↔ individual service. Choreography spreads schema coupling N×M (N publishers × M subscribers) |
| Orchestration means a single monolithic orchestrator for all workflows | Each business process should have its own orchestrator (or workflow type). Order processing orchestrator is separate from user onboarding orchestrator. Multiple orchestrator instances run in parallel (horizontally scaled). Temporal: workflows are isolated execution contexts — millions can run concurrently |
| Choreography always scales better than orchestration | Choreography can create fan-out event storms at scale: one event → 15 services each doing work → each publishing events → more work. Without careful event design: cascading event amplification. Orchestration: controlled flow, explicit sequencing. Temporal handles millions of concurrent workflows. The orchestrator overhead is minimal compared to the actual service work |
| You must choose one or the other for your entire system | Hybrid is the most practical approach. Orchestration for: top-level business process sagas (order, payment, fulfillment). Choreography for: internal service reactions (inventory-reserved → warehouse-allocation, internal to the service). Simple triggers (user-created → send-welcome-email, two services, one direction). No single answer: choose per use case complexity |

---

### 🔥 Pitfalls in Production

**Choreography event loop — services responding to their own events:**

```
SCENARIO: Order processing via choreography.
  
  OrderService: publishes OrderUpdated when order changes.
  InventoryService: subscribes to OrderUpdated (for inventory sync).
  InventoryService: after updating, publishes InventoryUpdated.
  OrderService: subscribes to InventoryUpdated (to update order status).
  OrderService: updates order → publishes OrderUpdated.
  
  INFINITE LOOP:
    OrderUpdated → InventoryUpdated → OrderUpdated → InventoryUpdated → ...
    
  Symptoms: Kafka consumer lag: infinity. CPU: 100%. No business progress.
  
BAD: Circular event subscriptions:
  // OrderService subscribes to InventoryUpdated → updates order → publishes OrderUpdated.
  // InventoryService subscribes to OrderUpdated → updates inventory → publishes InventoryUpdated.
  // LOOP.
  
FIX 1: Directed event DAG (no cycles):
  Events must form a Directed Acyclic Graph.
  OrderService: ONLY publishes OrderPlaced, OrderCancelled (not OrderUpdated).
  InventoryService: ONLY subscribes to OrderPlaced, OrderCancelled.
  InventoryService: publishes InventoryReserved, InventoryReleased.
  OrderService: does NOT subscribe to InventoryReserved (that's PaymentService's trigger).
  No cycle.
  
FIX 2: Event versioning / idempotency flag:
  Add "source" and "eventId" to every event.
  Consumer: track processed eventIds. If same eventId already processed → skip.
  Prevents re-processing of reflected events.
  
FIX 3: Switch to orchestration for complex flows:
  If you find yourself managing many event subscriptions and cycles:
  → signal that orchestration would be simpler.
  → Refactor to orchestrated saga.

PRODUCTION GOTCHA: Event schema version mismatch during deployment:
  OldOrderService: publishes OrderCreated with field "items" as List<String>.
  NewInventoryService: expects "items" as List<Item> (objects, not strings).
  Deployment: inventory deployed before order service updated.
  
  OrderCreated event arrives: InventoryService: deserialization failure. Consumer dies.
  Dead letter queue fills. Orders stuck.
  
  FIX: schema compatibility (Avro with Schema Registry, or JSON with backward-compatible changes).
  Add fields: don't remove or change existing fields.
  Deploy consumers before producers (backward compatibility).
  Or: orchestration where schema mismatch is contained to orchestrator ↔ one service pair.
```

---

### 🔗 Related Keywords

- `Saga Pattern` — the distributed transaction pattern that both choreography and orchestration implement
- `Outbox Pattern` — reliable event publishing enabling choreography sagas
- `Event-Driven Architecture` — broader context where choreography operates
- `Temporal` — production-grade orchestration engine for complex saga workflows

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Choreography: services react to events   │
│              │ (decoupled, hard to trace). Orchestration│
│              │ : conductor sends commands (explicit,    │
│              │ observable, single coordinator).         │
├──────────────┼───────────────────────────────────────────┤
│ USE CHOREOGRAPHY  │ Simple 2-3 step flows; stable event │
│              │ contracts; teams want autonomy           │
├──────────────┼───────────────────────────────────────────┤
│ USE ORCHESTRATION │ Complex 4+ step conditional flows;  │
│              │ customer-facing workflows needing status;│
│              │ operational visibility critical          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Flash mob vs. directed film: simple     │
│              │  dance vs. complex scenes need a director│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Saga Pattern → Outbox Pattern → Temporal │
│              │ → AWS Step Functions → Event Sourcing    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You inherit a choreography-based order system with 8 services and 25 event types. Customer support reports: "Order ABC-123 is stuck — customer paid but hasn't received shipping confirmation." How do you diagnose this? What tools/queries do you use? How long would it take compared to an orchestration-based system where you could query the orchestrator's state table for order ABC-123? What changes would you make to improve observability without switching to orchestration?

**Q2.** A Temporal workflow (orchestration) for order processing has this challenge: Step 3 (payment) calls an external payment provider (Stripe). Stripe has a 99.9% SLA (8.7 hours downtime/year). If Stripe is down: should the workflow wait (for hours?), retry indefinitely, fail fast, or use a fallback payment provider? Design the retry/fallback strategy within the Temporal workflow. How does Temporal's "workflow execution timeout" interact with this design?
