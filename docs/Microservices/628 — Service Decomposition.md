---
layout: default
title: "Service Decomposition"
parent: "Microservices"
nav_order: 628
permalink: /microservices/service-decomposition/
number: "628"
category: Microservices
difficulty: ★★☆
depends_on: "Monolith vs Microservices, Domain-Driven Design (DDD), Bounded Context"
used_by: "Strangler Fig Pattern, Modular Monolith, Database per Service"
tags: #intermediate, #architecture, #microservices, #pattern
---

# 628 — Service Decomposition

`#intermediate` `#architecture` `#microservices` `#pattern`

⚡ TL;DR — **Service decomposition** is the process of deciding how to split a system into microservices. The two primary strategies are **decompose by business capability** (what the system does) and **decompose by subdomain** (DDD Bounded Context). Wrong decomposition creates "distributed monoliths."

| #628            | Category: Microservices                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Monolith vs Microservices, Domain-Driven Design (DDD), Bounded Context |                 |
| **Used by:**    | Strangler Fig Pattern, Modular Monolith, Database per Service          |                 |

---

### 📘 Textbook Definition

**Service Decomposition** is the architectural activity of identifying and defining the boundaries of microservices in a system. The two primary decomposition patterns are: **Decompose by Business Capability** — a business capability is something the business does to generate value (e.g., "manage orders," "process payments," "manage customers") — each capability maps to one microservice that owns all data and logic for that capability. **Decompose by Subdomain** (DDD) — identify subdomains in the domain model: Core Domains (competitive advantage, highest investment), Supporting Subdomains (needed but not differentiating), and Generic Subdomains (commodity, buy not build). Each subdomain maps to one or more Bounded Contexts, each implemented as a microservice. Bad decomposition patterns include: decomposing by verb/use-case (leads to many fine-grained services), decomposing by noun/resource (leads to shared data problems), and decomposing by technical layer (leads to the distributed monolith anti-pattern).

---

### 🟢 Simple Definition (Easy)

Service decomposition answers: "how do we split our application into services?" The answer is to cut along natural business boundaries — each service should own a complete business capability with its own data. Cut too fine and you get chatty services; cut too coarse and you get a monolith.

---

### 🔵 Simple Definition (Elaborated)

The key insight is: a service boundary is correct when changes within that boundary do NOT require changing other services. If adding a new order type requires modifying both `OrderService` and `ProductService`, the boundary is wrong. Good decomposition is guided by what naturally changes together (cohesion) and what naturally changes independently (coupling). DDD's Bounded Context is the most rigorous tool for finding these boundaries: each context has its own language, its own model, and its own lifecycle. The practical approach is to map the business capabilities (what does the business do?), draw context maps (how do these capabilities relate?), then draw service boundaries around natural contexts.

---

### 🔩 First Principles Explanation

**Decomposition by Business Capability:**

```
E-COMMERCE BUSINESS CAPABILITIES → SERVICES:
  ┌────────────────────────────────────────────────────────────┐
  │ Business Capability    │ Service           │ Owns           │
  ├────────────────────────┼───────────────────┼────────────────┤
  │ Manage product catalog │ ProductService    │ products DB    │
  │ Manage customer accts  │ CustomerService   │ customers DB   │
  │ Accept orders          │ OrderService      │ orders DB      │
  │ Process payments       │ PaymentService    │ payments DB    │
  │ Manage inventory       │ InventoryService  │ inventory DB   │
  │ Ship products          │ ShippingService   │ shipments DB   │
  │ Send notifications     │ NotificationService│ notifications  │
  └────────────────────────┴───────────────────┴────────────────┘
  Each service = one team, one codebase, one database, one deployment

WRONG DECOMPOSITION (by technical layer):
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │ UIService   │  │ BusinessSvc │  │ DataService  │
  │ (frontend)  │→ │ (logic)     │→ │ (DB access) │
  └─────────────┘  └─────────────┘  └─────────────┘
  → All three change together for every feature
  → Cannot deploy one layer without the others
  → Distributed monolith by design
```

**Decomposition by DDD Subdomain:**

```
DOMAIN: E-Commerce
  ┌─────────────────────────────────────────────────────────────┐
  │ CORE DOMAIN (competitive advantage — invest most)          │
  │   Order Management: complex pricing, promotions, rules     │
  │   → Build in-house, DDD aggregate design, high investment  │
  │                                                            │
  │ SUPPORTING SUBDOMAIN (needed but not differentiating)      │
  │   Inventory Management, Shipping Calculation              │
  │   → Simpler design, can use CRUD with basic domain model  │
  │                                                            │
  │ GENERIC SUBDOMAIN (commodity — buy or use open source)     │
  │   Authentication, Notifications, Payment Processing        │
  │   → Use Auth0, SendGrid, Stripe — don't build from scratch │
  └─────────────────────────────────────────────────────────────┘

Context Map relationships:
  OrderContext ──Conformist──► ProductContext
                               (Order follows Product's model)
  OrderContext ──ACL──► ExternalPaymentContext
                        (Anti-Corruption Layer wraps Stripe API)
  OrderContext ──Partnership──► InventoryContext
                                (Both contexts evolve together)
```

**The decomposition heuristics:**

```
SINGLE RESPONSIBILITY: each service should have exactly ONE reason to change
  ✓ PaymentService changes when payment processing rules change
  ✗ OrderService changes when payment rules, product catalog, AND customer data change
    → OrderService is doing too much

LOOSE COUPLING: a service change should NOT require other services to change
  ✓ Adding a new payment method: only PaymentService changes
  ✗ Adding a new payment method: OrderService, CustomerService also need changes
    → Boundary is wrong: payment logic leaked into other services

HIGH COHESION: all code within a service should relate to the same business concept
  ✓ OrderService: create, cancel, track, modify orders (all "order" domain)
  ✗ OrderService: create orders AND manage product inventory AND send emails
    → Too many unrelated responsibilities

THE TWO-PIZZA RULE (Amazon): a team should be fed by two pizzas (5-8 people)
  → Service should map to a team
  → Too many services per team = operational overhead without autonomy benefit
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT deliberate decomposition:

What breaks without it:

1. Services are split arbitrarily (by developer preference, by file size, by "that seemed right") — no relation to business change patterns.
2. Every feature requires changes to multiple services — deployment coordination overhead.
3. Services share data directly — preventing independent evolution.
4. "Death by a thousand services" — too fine-grained, everything is chatty and fragile.

WITH deliberate decomposition:
→ Services aligned to business capabilities mean one feature change = one service change.
→ Team autonomy: each team owns their service's domain completely.
→ Independent deployability: each service deploys without coordinating with others.
→ When requirements change, only the affected service's team needs to act.

---

### 🧠 Mental Model / Analogy

> Service decomposition is like city planning. Bad city planning cuts blocks arbitrarily — roads go everywhere, buildings are mixed randomly, everything is congested. Good city planning creates zones: residential, commercial, industrial — each with its own character, infrastructure, and rules. You do not build a school inside a factory. Similarly, bad service decomposition cuts along technical layers or arbitrary sizes; good decomposition cuts along natural business domains. Changes within a domain stay within that "zone" without requiring cross-zone construction work.

"City planning zones" = service boundaries (one per bounded context)
"Roads between zones" = inter-service APIs (stable, well-defined)
"Building a school inside a factory" = putting payment logic inside OrderService
"Changes within a domain stay local" = low coupling (correct boundary)
"Cross-zone construction" = cross-service coordination when a single feature changes multiple services

---

### ⚙️ How It Works (Mechanism)

**Testing boundary correctness — the "change test":**

```
BOUNDARY TEST: For each upcoming feature/change, answer:
  "Which services need to be modified?"

GOOD boundary:
  Feature: "Add Apple Pay as a payment method"
  Changes needed: ONLY PaymentService → ✓ boundary correct

BAD boundary:
  Feature: "Add Apple Pay as a payment method"
  Changes: PaymentService ✓, OrderService (payment type field) ✗,
           CustomerService (saved payment methods) ✗
  → Payment logic is scattered across services → boundary is wrong
  → Fix: move payment method management into PaymentService

CONTEXT MAP SMELL DETECTOR:
  If service A calls service B for EVERY operation A performs:
  → A and B are probably one service split incorrectly
  If service A knows about B's internal data model directly:
  → Missing Anti-Corruption Layer or wrong boundary
```

---

### 🔄 How It Connects (Mini-Map)

```
Monolith vs Microservices
        │
        ▼
Service Decomposition  ◄──── (you are here)
(how to split the system into services)
        │
        ├── Domain-Driven Design (DDD) → subdomains guide boundaries
        ├── Bounded Context → each context = one service (usually)
        ├── Anti-Corruption Layer → isolates context boundaries from external models
        ├── Strangler Fig Pattern → incrementally extracts one service at a time
        └── Database per Service → follows naturally from correct decomposition
```

---

### 💻 Code Example

**Context Map as code — Anti-Corruption Layer wrapping an external service:**

```java
// ExternalShippingService uses its own model (not our domain model)
// Anti-Corruption Layer translates between contexts:
@Service
class ShippingContextAdapter {  // ACL implementation

    @Autowired FedExApiClient fedExClient; // external API

    // Translates from our domain model to FedEx's model
    public ShipmentConfirmation shipOrder(Order order) {
        // Our model: Order with Address
        // FedEx model: CreateShipmentRequest with Shipper/Recipient
        CreateShipmentRequest fedExRequest = CreateShipmentRequest.builder()
            .shipper(new FedExShipper(warehouseAddress))
            .recipient(new FedExRecipient(
                order.getShippingAddress().getFullName(),
                order.getShippingAddress().toFedExAddress()))
            .packageWeight(order.getTotalWeight())
            .serviceType(FedExServiceType.GROUND)
            .build();

        FedExShipmentResponse response = fedExClient.createShipment(fedExRequest);

        // Translate FedEx response back to our domain model
        return new ShipmentConfirmation(
            response.getTrackingNumber(),
            response.getEstimatedDeliveryDate(),
            response.getLabelUrl()
        );
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Each microservice should be small (a few hundred lines)   | Service size is irrelevant. The correct measure is business cohesion. A service that owns all order-related logic might be thousands of lines — that is correct. A tiny service that must be deployed with three others for every feature is incorrectly decomposed regardless of size |
| One service per table (resource decomposition) is correct | Decomposing by data resource (one service per database table) leads to anemic services with no business logic — all logic is in orchestrators that call multiple resource services. This is the "Transaction Script" anti-pattern distributed                                          |
| Decomposition is a one-time design activity               | Decomposition is iterative. Initial boundaries will be wrong. As the team learns the domain, boundaries are adjusted. The "evolutionary architecture" approach accepts that service boundaries will be refactored as understanding grows                                               |
| More services = better microservices architecture         | Service count should match team count and change-frequency. Amazon has hundreds of services because it has hundreds of teams. A 5-person team running 50 microservices has operational overhead without autonomy benefit                                                               |

---

### 🔥 Pitfalls in Production

**The "god service" — decomposition too coarse**

```
SYMPTOM: One service handles 70% of all requests
  OrderService:
    - create/modify/cancel orders
    - manage product catalog
    - send email notifications
    - track inventory
    - process refunds
    - manage customer loyalty points

CONSEQUENCE:
  - One team bottleneck: all product, inventory, and notification changes
    require coordination with the OrderService team
  - Cannot scale inventory checks independently from order creation
  - Any change to notifications requires re-testing the full order flow
  - Service becomes the new monolith

FIX: Apply single responsibility — extract clear capabilities:
  OrderService → only orders state machine
  NotificationService → all customer communications
  InventoryService → stock levels and reservations
  LoyaltyService → points, rewards, redemption
```

---

### 🔗 Related Keywords

- `Domain-Driven Design (DDD)` — the methodology that provides the theoretical foundation for service decomposition
- `Bounded Context` — the DDD concept that directly maps to service boundaries
- `Strangler Fig Pattern` — the technique for incrementally performing service decomposition on an existing monolith
- `Anti-Corruption Layer` — protects a service's domain model from external service models
- `Database per Service` — the data isolation pattern that follows from correct service decomposition

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGY 1   │ By Business Capability                    │
│              │ (what the business does to generate value) │
├──────────────┼───────────────────────────────────────────┤
│ STRATEGY 2   │ By DDD Subdomain                          │
│              │ Core / Supporting / Generic               │
├──────────────┼───────────────────────────────────────────┤
│ SMELL        │ Feature change touches N services         │
│              │ → boundary is in the wrong place          │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ By layer (UI/Logic/Data) → distrib mono   │
│              │ By table → anemic, no domain logic        │
│              │ Too fine-grained → chatty, fragile        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The "single responsibility" principle applied to services says a service should have one reason to change. But in practice, "one business capability" can mean different things to different organisations. Describe how team topology influences the decomposition: given a 3-team organisation (team A owns orders and payments, team B owns products and inventory, team C owns customers and notifications), what service boundaries would naturally emerge aligned to Conway's Law? Now describe what happens if team A is split into two teams (orders team and payments team) — do the service boundaries need to change, and what migration work is required?

**Q2.** "Decompose by subdomain" classifies subdomains as Core, Supporting, or Generic. The classification affects investment level and build-vs-buy decisions. Walk through the e-commerce example: payment processing starts as a Generic Subdomain (use Stripe). The business decides to build a custom payment orchestration layer to support 15+ payment providers globally and negotiate better rates — the payment domain is now a Core Domain. Describe the architectural consequences: does the service boundary change, does the model complexity change, and what does an Anti-Corruption Layer look like when wrapping multiple payment provider APIs behind a single internal payment domain model?
