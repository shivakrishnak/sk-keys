---
layout: default
title: "Choreography vs Orchestration"
parent: "Distributed Systems"
nav_order: 610
permalink: /distributed-systems/choreography-vs-orchestration/
number: "0610"
category: Distributed Systems
difficulty: ★★★
depends_on: Saga Pattern, Event-Driven Architecture, Message Broker, Microservices
used_by: Saga Pattern, Order Processing, Distributed Workflows, BPMN
related: Saga Pattern, Event Sourcing, Outbox Pattern, Service Mesh, CQRS
tags:
  - distributed
  - microservices
  - coordination
  - pattern
  - deep-dive
---

# 610 — Choreography vs Orchestration

⚡ TL;DR — Choreography: services react to events autonomously with no central coordinator (participants are peers); Orchestration: a central workflow engine directs each participant what to do and when (one coordinator, many participants) — two fundamentally different coordination models for multi-service workflows.

| #610            | Category: Distributed Systems                                          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Saga Pattern, Event-Driven Architecture, Message Broker, Microservices |                 |
| **Used by:**    | Saga Pattern, Order Processing, Distributed Workflows, BPMN            |                 |
| **Related:**    | Saga Pattern, Event Sourcing, Outbox Pattern, Service Mesh, CQRS       |                 |

---

### 🔥 The Problem This Solves

**THE COORDINATION PROBLEM:**
"Place an order" involves Inventory, Payment, Shipping, and Notification services. How do these services know when to take action? Who decides the order of operations? Who handles failures? Two fundamentally different answers exist, with different trade-offs for coupling, observability, and complexity.

**WORLD WITHOUT EXPLICIT CHOICE:**
Teams instinctively build choreography (services react to events because it's "event-driven") without realizing they've created a distributed monolith where the workflow logic is invisible — scattered across dozens of event handlers. Or they build orchestration with a heavyweight BPM engine that becomes a bottleneck, requiring modifications for every business process change. Choosing between them intentionally — understanding the trade-offs — is what architects do.

---

### 📘 Textbook Definition

**Choreography**: each service's behavior is defined by the events it subscribes to and the events it publishes. No service orchestrates others — each acts autonomously on received events. The workflow "emerges" from the interaction of independent reactive services. Analogy: a jazz ensemble improvising — each musician reacts to others.

**Orchestration**: a central orchestrator service explicitly calls other services in a defined sequence, handles the control flow, manages state, and coordinates error handling/compensation. Other services are "participants" — they do what the orchestrator tells them. Analogy: a conductor directing an orchestra — every musician follows the conductor's cues.

**Hybrid**: many real-world systems use both — orchestration within a bounded context (service cluster), choreography between bounded contexts (domain boundaries).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Choreography = each service knows its own role and reacts to events; Orchestration = one brain tells all services what to do next.

**One analogy:**

> Choreography is a self-organizing flash mob — each dancer follows their own cue from the music. No one is directing individuals. Orchestration is a ballet performance — the director has a script, calls each dancer's entrance, and runs the show. Both produce coordinated movement; one is emergent, one is directed.

**One insight:**
In choreography, the workflow logic is **distributed** and **implicit** — it lives in every service's event handler, nowhere centrally visible. In orchestration, the workflow is **centralized** and **explicit** — one place to read the entire workflow. This is the core observability trade-off: choreography is harder to debug when things go wrong; orchestration makes the "happy path" explicit but the orchestrator becomes a single point of coupling.

---

### 🔩 First Principles Explanation

**CHOREOGRAPHY (ORDER SAGA via EVENTS):**

```
Events published/consumed:

OrderService:
  PUBLISHES: OrderCreated {orderId, items, amount, userId}
  CONSUMES: ItemsReleased (on failure) → cancels order

InventoryService:
  CONSUMES: OrderCreated → reserves items
  PUBLISHES: ItemsReserved {orderId} OR InventoryInsufficient {orderId}
  CONSUMES: PaymentFailed → releases items, publishes ItemsReleased

PaymentService:
  CONSUMES: ItemsReserved → charges customer
  PUBLISHES: PaymentSucceeded {orderId, chargeId} OR PaymentFailed {orderId}
  CONSUMES: ShipmentFailed → refunds, publishes PaymentRefunded

ShippingService:
  CONSUMES: PaymentSucceeded → creates shipment
  PUBLISHES: ShipmentCreated {orderId, trackingNo} OR ShipmentFailed {orderId}

NotificationService:
  CONSUMES: ShipmentCreated → sends confirmation email

No service knows the full workflow. The workflow emerges from event chains.
```

**ORCHESTRATION (ORDER SAGA via ORCHESTRATOR):**

```java
// All workflow logic in ONE place:
@Service
public class OrderOrchestrator {

    public void processOrder(Order order) {
        try {
            // Explicit, readable workflow:
            inventoryService.reserve(order.getItems());     // Step 1
            paymentService.charge(order.getAmount());        // Step 2
            shippingService.createShipment(order);           // Step 3
            notificationService.sendConfirmation(order);     // Step 4

        } catch (PaymentException e) {
            // Compensation: explicit, visible, in one place:
            inventoryService.release(order.getItems());
            order.cancel();
        } catch (ShipmentException e) {
            paymentService.refund(order.getChargeId());
            inventoryService.release(order.getItems());
            order.cancel();
        }
    }
}
```

**COMPARING THE SAME WORKFLOW:**

```
CHOREOGRAPHY:
  Visibility:      Distributed across 5 services
  Change process:  Modify event handlers in each affected service
  Debug Path:      Trace event chain across Kafka/RabbitMQ topics
  Coupling:        Services coupled through shared event schemas

ORCHESTRATION:
  Visibility:      All in OrderOrchestrator (single class/workflow)
  Change process:  Modify OrderOrchestrator only
  Debug Path:      Read orchestrator logs sequentially
  Coupling:        Services coupled to the orchestrator (it calls them)
```

**SERVICE MESH SIDE NOTE:**

```
Service mesh (Istio/Linkerd) handles infrastructure-level concerns:
  - Load balancing, service discovery, mutual TLS
  - Not about business workflow coordination

Choreography/Orchestration is about BUSINESS WORKFLOW coordination.
These operate at different layers: don't confuse them.
```

---

### 🧪 Thought Experiment

**THE WORKFLOW VISIBILITY TEST:**

A new engineer joins. Task: "Find where the logic is that sends a confirmation email after an order is placed."

**Choreography system:**

1. Search codebase for "OrderCreated" event consumers.
2. Find: InventoryService subscribes. Look at it — not the email.
3. Find InventoryService publishes "ItemsReserved".
4. Search for "ItemsReserved" consumers.
5. Find: PaymentService subscribes. Look at it — not the email.
6. … (continue 3 more steps)
7. Finally find: NotificationService subscribes to ShipmentCreated and sends email.

The engineer traced through 5 services and 4 event topics to understand one workflow.

**Orchestration system:**

1. Find OrderOrchestrator class.
2. Read the 20-line `processOrder` method.
3. See `notificationService.sendConfirmation(order)` on line 18.

Done. The entire workflow is readable in one class.

**Lesson:** Choreography's distributed logic becomes a maintenance burden. Orchestration's central logic is easier to understand but harder to modify independently (the orchestrator must be changed for every workflow alteration, potentially coupling teams).

---

### 🧠 Mental Model / Analogy

> Choreography is like a relay race train: each runner passes the baton to the next runner who is already waiting at the right position. Each runner knows their leg of the race, their handoff point, and who takes the baton next. But if you want to add a new leg to the race, or change the order, you need to tell multiple runners.

> Orchestration is like a race director with a megaphone: "Runner 1, go! Runner 2, your turn! Runner 3, wait — Runner 2 tripped, hold! Runner 2, try again!" The director sees everything and controls everything. If they drop the megaphone (crash), the race stops.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Choreography = each service reacts to events independently. Orchestration = one service directs all others. Choose based on workflow complexity and team ownership.

**Level 2:** Choreography: event-driven, loose coupling, implicit workflow, harder to debug. Orchestration: explicit workflow, easier debug, tight coupling to orchestrator. Hybrid: orchestration within bounded contexts, choreography between them.

**Level 3:** Choreography problems at scale: "event spaghetti" — circular event subscriptions, event loops, no clear entry point. Solution: design event diagrams explicitly before implementing, enforce no-cycle topologies. Orchestration problems: the orchestrator becomes a "god object" knowing all service internals; teams must coordinate changes through the orchestrator owner. Solution: orchestration per saga (not global orchestrator for all workflows).

**Level 4:** Temporal.io provides a middle-ground: workflow-as-code (looks like orchestration) but the orchestrator is stateless and distributed (runs on a worker fleet) — it's not a SPoF. The workflow definition is code; Temporal's server handles persistence, retries, and scheduling. For complex enterprise workflows with human approval steps: BPMN (Business Process Model and Notation) tools (Camunda, Activiti) provide visual orchestration with operator dashboards. The "right" choice in practice: start with orchestration (simpler, explicit), evolve to choreography only where independent team scalability requires it.

---

### ⚙️ How It Works (Mechanism)

**Choreography with Apache Kafka:**

```java
// InventoryService subscribes to OrderCreated:
@KafkaListener(topics = "order-created", groupId = "inventory-service")
public void onOrderCreated(OrderCreated event) {
    try {
        inventoryRepository.reserve(event.getOrderId(), event.getItems());
        kafkaTemplate.send("items-reserved", new ItemsReserved(event.getOrderId()));
    } catch (InsufficientInventoryException e) {
        kafkaTemplate.send("inventory-insufficient",
            new InventoryInsufficient(event.getOrderId()));
    }
}

// PaymentService subscribes to ItemsReserved:
@KafkaListener(topics = "items-reserved", groupId = "payment-service")
public void onItemsReserved(ItemsReserved event) {
    // charge ... then publish PaymentSucceeded/PaymentFailed
}
```

---

### ⚖️ Comparison Table

| Dimension            | Choreography                           | Orchestration                             |
| -------------------- | -------------------------------------- | ----------------------------------------- |
| Workflow visibility  | Implicit (distributed)                 | Explicit (central)                        |
| Coupling             | Services ↔ Event schema                | Services → Orchestrator                   |
| Team independence    | High (each service is autonomous)      | Low (changes require orchestrator update) |
| Debugging            | Hard (trace events across systems)     | Easy (read orchestrator logs)             |
| Failure handling     | Distributed (each service compensates) | Centralized (orchestrator compensates)    |
| Best for             | Simple, well-defined, stable flows     | Complex business rules, human-in-loop     |
| Scales independently | Yes                                    | Orchestrator can become bottleneck        |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                                 |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Event-driven = choreography            | Event-driven is a mechanism; you can orchestrate using events (orchestrator sends events as commands to participants)                                                   |
| Orchestration = synchronous HTTP calls | Orchestration can use async messaging; the synchronous/async dimension is orthogonal to orchestration/choreography                                                      |
| Choreography scales better             | Both can scale. Choreography scales teams better (decoupled services); orchestration can scale instances but the orchestrator itself is a bottleneck if not distributed |

---

### 🚨 Failure Modes & Diagnosis

**Choreography Event Loop (Circular Dependency)**

**Symptom:** Service A publishes EventX → Service B consumes EventX, publishes EventY
→ Service A consumes EventY, publishes EventX again → infinite event loop. Message
broker queue depth grows unboundedly. Service restarts due to memory exhaustion.

Cause: Circular event subscription introduced during a feature addition. No global
event flow diagram showing the full event topology.

**Fix:** (1) Maintain an event topology diagram — reviewed for cycles before any new
subscription is added. (2) Add correlation ID propagation: if the same correlation ID
appears in the same service twice without completion, route to dead letter queue.
(3) Add saga orchestration for complex workflows to eliminate possibility of circular
event chains.

---

### 🔗 Related Keywords

- `Saga Pattern` — uses either choreography or orchestration as its coordination model
- `Event Sourcing` — provides the event log that choreography relies on
- `Outbox Pattern` — ensures reliable event publishing in choreography
- `Service Mesh` — handles infrastructure concerns (not business workflow coordination)
- `CQRS` — often combined with choreography for read model projection

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  CHOREOGRAPHY: reactive, decentralized, event-driven     │
│  → Services are autonomous peers; workflow is emergent   │
│  → Risk: event spaghetti, hard to debug                  │
│                                                          │
│  ORCHESTRATION: directive, centralized, workflow-as-code │
│  → One brain; clear flow; easier to debug                │
│  → Risk: orchestrator as bottleneck / god object         │
│                                                          │
│  HYBRID: orchestrate within domain, choreograph between  │
│  Temporal.io: best of both (distributed orchestrator)    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 5-step order workflow is implemented with choreography. Six months later, the business adds a new "fraud check" step between payment and shipping. List all the services that must be modified in: (a) the choreography implementation, (b) an orchestration implementation. Which requires more coordination across teams? Which is more risky to release?

**Q2.** You're advising a startup on how to implement a multi-step user onboarding workflow: verify email → create account → send welcome email → schedule 30-day check-in → enroll in AB test cohort. Two engineers disagree: one wants choreography (events), one wants orchestration (Temporal). What factors would you evaluate to make this decision? What is your recommendation and why?
