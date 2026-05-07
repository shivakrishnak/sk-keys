---
layout: default
title: "Service Decomposition"
parent: "Microservices"
nav_order: 8
permalink: /microservices/service-decomposition/
number: "MSV-008"
category: Microservices
difficulty: ★★☆
depends_on: Monolith vs Microservices, Domain-Driven Design, Bounded Context
used_by: API Gateway, Service Discovery, Service Mesh
related: Modular Monolith, Strangler Fig Pattern, Database per Service
tags:
  - microservices
  - architecture
  - pattern
  - intermediate
  - distributed
---

# MSV-008 — Service Decomposition

⚡ TL;DR — Service decomposition is the practice of deciding how to split a large system into independently deployable services by applying proven decomposition strategies around business capabilities and domains.

| #628 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Domain-Driven Design, Bounded Context | |
| **Used by:** | API Gateway, Service Discovery, Service Mesh | |
| **Related:** | Modular Monolith, Strangler Fig Pattern, Database per Service | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team decided to "go microservices." They split their e-commerce app into services by technical layers: a "frontend service," a "business logic service," and a "database service." Now every feature requires simultaneous changes to all three services. Deployments are coordinated disasters. The "business logic service" has ballooned to 200,000 lines. They have all the pain of microservices and none of the benefits.

**THE BREAKING POINT:**
Services are split along the wrong lines. Instead of reducing coupling, the split amplified it. Technical layering as a decomposition strategy guarantees a distributed monolith — all the network overhead with none of the autonomy.

**THE INVENTION MOMENT:**
This is exactly why Service Decomposition strategies were codified — to give teams principled, repeatable methods for finding service boundaries that minimise coupling, maximise cohesion, and mirror organisational structure.

---

### 📘 Textbook Definition

**Service Decomposition** is the process of partitioning a software system into discrete, bounded services using structured strategies. The two primary strategies are decomposition by **business capability** (what the business does) and decomposition by **subdomain** (using Domain-Driven Design to find bounded contexts). A well-decomposed service is loosely coupled to other services, highly cohesive internally, and independently deployable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Deciding where to draw the dividing lines between services so each team can work and deploy without waiting for others.

**One analogy:**
> Imagine a hospital reorganising its departments. Splitting by floor (technical layer) means every patient visit requires all floors to coordinate. Splitting by specialty (cardiology, neurology, orthopaedics) means each team owns the complete care path for their patient type and rarely needs to involve others for routine work.

**One insight:**
The right decomposition dramatically reduces inter-team coordination. If every feature requires two teams to change code and coordinate deployments, the service boundary is wrong — regardless of how clean the code looks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A service is independently deployable only if it can change without requiring simultaneous changes to other services.
2. Loose coupling means a service knows as little as possible about other services' internals.
3. High cohesion means everything within a service is strongly related to a single business purpose.

**DERIVED DESIGN:**
The invariants point to splitting by *business capability* — a stable unit of what the business does — rather than by technical function. Business capabilities change less often than technical implementations.

The four main decomposition strategies:

**Strategy 1 — By Business Capability:**
Identify what the business does: Catalog Management, Order Processing, Payment, Notifications, Customer Management. Each becomes a service. Capabilities are stable because business goals rarely pivot; internal implementations can change freely.

**Strategy 2 — By DDD Subdomain:**
Identify core, supporting, and generic subdomains. Extract core subdomains (competitive differentiators) into their own services first. Use supporting subdomains together if coupling is low.

**Strategy 3 — By Team Structure (Conway's Law):**
Service boundaries should mirror team boundaries. If two teams own the same service, ownership is unclear and deployments require coordination. One team → one or few services.

**Strategy 4 — By Deployment/Scaling Need:**
Services used by high-traffic paths or needing different scaling characteristics (e.g., image processing, recommendation engine) become their own services even if business-capability-wise they could be bundled.

**THE TRADE-OFFS:**
**Gain:** Team autonomy, independent deployability, fault isolation, targeted scaling.
**Cost:** Network calls between services, distributed transactions, eventual consistency requirements, more services to operate.

---

### 🧪 Thought Experiment

**SETUP:**
You have a retail app. You must decide: split into (A) UI / BL / DB services, or (B) Catalog / Orders / Payments / Notifications services.

**WHAT HAPPENS WITH OPTION A (Technical Layer Split):**
A developer adds a "discount" field to orders. They change the DB service schema, the BL service DTO, and the UI layer. Three PRs. Three deployments. Three teams must coordinate. The "BL service" contains logic for catalog, orders, payments, AND notifications, so any change risks all four features.

**WHAT HAPPENS WITH OPTION B (Business Capability Split):**
A developer adds a "discount" field to orders. They change only the Orders service — its schema, its logic, and its API response. One PR. One deployment. One team. The Payments and Catalog services are untouched.

**THE INSIGHT:**
Splitting by technical layer guarantees coupling. Splitting by business capability enables independence. The right split means most features touch exactly one service.

---

### 🧠 Mental Model / Analogy

> Think of a city council splitting departments: Option A is splitting by building floor (planning + environment + roads all on floor 1; finance + HR on floor 2). Option B is splitting by service type (Planning Department, Roads Department, Finance Department). Every planning decision under Option A requires all floors to coordinate. Under Option B, planning runs independently.

- "Splitting by floor" → splitting by technical layer (UI / BL / DB)
- "Splitting by department type" → splitting by business capability
- "Requiring all floors for one decision" → tight coupling across layered services
- "Planning runs independently" → one service owns the complete capability end-to-end

Where this analogy breaks down: some services genuinely need to share functions (like HR is shared across all departments) — this is handled by "supporting" or "generic" subdomains in DDD, not by merging all departments.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Service decomposition is the art of deciding how to slice your app into separate pieces so that each team can work on their piece without bumping into others.

**Level 2 — How to use it (junior developer):**
Start by listing the main things your business does (capabilities). Name each one as a noun: Catalog, Orders, Payments, Notifications, Users. Each becomes a candidate service. Check: can I change this without changing others? If yes, the boundary is right. If no, the capability is too split or too merged.

**Level 3 — How it works (mid-level engineer):**
Use event storming workshops to identify domain events and who emits them. Events naturally cluster around bounded contexts. Each context is a service candidate. Apply Robert C. Martin's Common Closure Principle: things that change together, deploy together — so they belong in one service. Things that change for different reasons, at different times, or by different teams — they belong in different services.

**Level 4 — Why it was designed this way (senior/staff):**
The theoretical foundations are Conway's Law (organisation structure → system structure), the Common Closure/Common Reuse Principles from SOLID, and DDD bounded contexts. In practice, Sam Newman's "Build Microservices" identifies the danger of splitting too fine too early: the 2-pizza team rule suggests a team can own a few services but not 50 micro-functions. The trend toward "macro-services" (coarser splits than Amazon's extreme microservices) reflects the real operational cost of each service boundary.

---

### ⚙️ How It Works (Mechanism)

**Decomposition by Business Capability — Step by Step:**

```
┌────────────────────────────────────────────────┐
│      Service Decomposition Process             │
├────────────────────────────────────────────────┤
│ 1. Event Storming session                      │
│    — map domain events on a timeline           │
│    — who produces each event?                  │
├────────────────────────────────────────────────┤
│ 2. Identify Bounded Contexts                   │
│    — group events by who owns them             │
│    — each cluster = candidate service          │
├────────────────────────────────────────────────┤
│ 3. Validate with "change test"                 │
│    — adding feature X, how many services      │
│      need to change? (goal: 1)                 │
├────────────────────────────────────────────────┤
│ 4. Validate with "team alignment test"         │
│    — does one team own this entire service?    │
├────────────────────────────────────────────────┤
│ 5. Define service API contracts                │
│    — OpenAPI spec for synchronous calls        │
│    — AsyncAPI spec for events                  │
├────────────────────────────────────────────────┤
│ 6. Extract, starting with lowest-coupling      │
│    service (Strangler Fig)                     │
└────────────────────────────────────────────────┘
```

**Bad vs Good decomposition — e-commerce example:**

```
BAD DECOMPOSITION (technical layers):
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  UI Service  │→ │  BL Service  │→ │  DB Service  │
│  (React SSR) │  │ (ALL logic)  │  │  (ALL data)  │
└──────────────┘  └──────────────┘  └──────────────┘
Every feature touches all 3 services.

GOOD DECOMPOSITION (business capabilities):
┌──────────────┐  ┌──────────────┐
│   Catalog    │  │   Orders     │
│   Service    │  │   Service    │
└──────────────┘  └──────────────┘
┌──────────────┐  ┌──────────────┐
│  Payments    │  │Notifications │
│   Service    │  │   Service    │
└──────────────┘  └──────────────┘
Most features touch exactly 1 service.
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
Business Analysis → Event Storming → Bounded Context Identification ← YOU ARE HERE → Service API Contract Definition → Team Assignment → Implementation → Deployment

**FAILURE PATH:**
Wrong decomposition identified (coupled services) → Every new feature requires multi-service coordinated deployments → Teams slow down → Re-decomposition required → Data migration needed (most painful step) → Months of refactoring

**WHAT CHANGES AT SCALE:**
At 100+ services, the decomposition granularity matters enormously for operational overhead. Each service boundary creates: a network hop, a deployment pipeline, an alerting rule set, a log stream, and ownership documentation. Too-fine decomposition (nano-services) creates hundreds of services for logic that could share a process, multiplying ops cost. The trend at massive scale (Netflix, Amazon) is to find the right grain — typically aligned with team size and bounded by 1–3 services per engineer.

---

### 💻 Code Example

**Example 1 — Validating decomposition with a simple "change test" checklist:**

```yaml
# Decomposition validation matrix:
# For each planned feature, list services that must change.
# Goal: most features touch only 1 service.

feature: "Add discount code to checkout"
services_changed:
  - orders-service    # owns checkout flow — expected
  # Good: only 1 service changed

feature: "Add loyalty points on purchase"
services_changed:
  - orders-service    # places order
  - loyalty-service   # tracks points
  - notifications-service  # sends email
  # Acceptable: 3 services but through events, not sync calls
```

**Example 2 — Service contract definition (OpenAPI for Orders service):**

```yaml
# orders-service/openapi.yaml
openapi: "3.0.0"
info:
  title: Orders Service
  version: "1.0.0"
paths:
  /orders:
    post:
      summary: Place a new order
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PlaceOrderRequest'
      responses:
        '201':
          description: Order created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
# Each service owns and publishes its own OpenAPI spec
```

**Example 3 — Event-based communication to decouple services:**

```java
// Orders service publishes an event — does NOT call
// notifications or loyalty services directly
@Service
public class OrderService {
    private final ApplicationEventPublisher eventBus;

    public Order placeOrder(PlaceOrderRequest request) {
        Order order = orderRepository.save(new Order(request));
        // Publish event — let subscribers react independently
        eventBus.publishEvent(
            new OrderPlacedEvent(order.getId(), order.getTotal())
        );
        return order;
    }
}

// Notifications service subscribes — fully independent
@EventListener
public void onOrderPlaced(OrderPlacedEvent event) {
    emailService.sendConfirmation(event.getOrderId());
}
```

---

### ⚖️ Comparison Table

| Strategy | Coupling | Team Alignment | Difficulty | Best For |
|---|---|---|---|---|
| **By Business Capability** | Low | High | Medium | Most teams — stable, business-aligned |
| By DDD Subdomain | Low | High | High | Large, complex domains |
| By Technical Layer | High | Poor | Low | Avoid — creates distributed monolith |
| By Team/Conway's Law | Medium | Highest | Low | Org-first decomposition |
| By Scaling Requirement | Low | Medium | Low | Hot paths with 10x scale difference |

How to choose: start with business capability decomposition for its simplicity; refine with DDD subdomain analysis when domain complexity warrants the investment.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Technical layer splits (frontend/backend/DB) are a valid decomposition | This creates a distributed monolith — every feature touches all layers simultaneously |
| More services = better decomposition | More services = more operational overhead; the goal is fewer, rightly-sized services |
| Decomposition decisions are made once and are permanent | As the domain evolves and teams reorganise, service boundaries should be revisited — merging services is also valid |
| Every microservice should be tiny (nano-service) | Nano-services (100 lines each) create network overhead and deployment burden that exceeds their benefit |
| You must complete full decomposition before going live | Use the Strangler Fig pattern — extract one service at a time while the monolith continues to run |

---

### 🚨 Failure Modes & Diagnosis

**1. Distributed Monolith from Bad Decomposition**

**Symptom:** Every release requires coordinating deployments across 4+ services simultaneously; build board shows services all in "yellow" together.

**Root Cause:** Services are split along technical layers, not business capabilities — they are coupled at the data or interface level.

**Diagnostic:**
```bash
# Count how many services must be deployed together per release
git log --oneline --all --since="3 months ago" | \
  grep -E "deploy|release" | wc -l
# High number with multiple services in same commit = problem
# Or check deployment pipeline: are services always deployed in lock-step?
```

**Fix:** Re-decompose by business capability. Identify the domain events, find who owns them, redraw boundaries. Accept this is a multi-month refactoring investment.

**Prevention:** Validate decomposition with the "change test" before implementing — count services impacted per feature before writing a line of code.

**2. Service Too Fine-Grained (Nano-Service)**

**Symptom:** A single user request produces 50+ spans in distributed tracing. P99 latency is 2 seconds despite each service responding in milliseconds.

**Root Cause:** Services are split at function level rather than capability level — every small operation is its own network hop.

**Diagnostic:**
```bash
# Check span count for a typical request in Jaeger
curl "http://jaeger:16686/api/traces?service=api-gateway&limit=1" \
  | jq '[.data[0].spans[].operationName] | length'
# > 20 spans for a single request = too fine-grained
```

**Fix:** Merge related nano-services into a single coarser-grained service that handles the full business capability. Favour in-process function calls over network calls.

**Prevention:** Apply the "two-pizza team" heuristic — if one person owns a service with 50 lines of code, it is too small.

**3. Missing API Contract Before Implementation**

**Symptom:** Two teams both implement their services and discover incompatible APIs three weeks before launch, with no time to renegotiate.

**Root Cause:** No API-first design process; each team designed their service independently without agreeing on inter-service contracts.

**Diagnostic:**
```bash
# Validate that published and consumed OpenAPI specs match
npx @stoplight/spectral-cli lint orders-service/openapi.yaml
# Run consumer-driven contract tests
./mvnw verify -pl contract-tests
```

**Fix:** Adopt API-first development: publish the OpenAPI spec before implementation, have consuming services write consumer-driven contract tests, run Pact tests in CI before any deployment.

**Prevention:** Make contract-first design a team process: no service is implemented before its API spec is reviewed and agreed by all consumers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Monolith vs Microservices` — establishes why decomposition is needed and the trade-offs involved
- `Domain-Driven Design` — the primary theoretical framework for finding correct service boundaries
- `Bounded Context` — the DDD concept that directly maps to service boundaries

**Builds On This (learn these next):**
- `Strangler Fig Pattern` — the recommended approach for extracting services one at a time from an existing monolith
- `Database per Service` — the data isolation pattern that accompanies correct service decomposition
- `Consumer-Driven Contract Testing` — validates that service APIs remain compatible as they evolve

**Alternatives / Comparisons:**
- `Modular Monolith` — applies the same decomposition principles without the microservices operational overhead
- `Aggregate` — the DDD unit that often maps 1:1 to a service boundary

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The process of finding correct service    │
│              │ boundaries using principled strategies    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Wrong splits create distributed monoliths │
│ SOLVES       │ — more pain than a monolith               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Split by business capability, not         │
│              │ technical layer — features should touch   │
│              │ exactly one service                       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Extracting services from a monolith or    │
│              │ designing a greenfield microservices arch │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Domain is poorly understood — premature   │
│              │ decomposition is harder to fix than a     │
│              │ monolith                                  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Team autonomy vs operational complexity   │
│              │ per service boundary                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Split by what the business does,         │
│              │  not by how the code is layered."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain-Driven Design → Bounded Context →  │
│              │ Strangler Fig Pattern                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are decomposing a banking app. One team argues that "Account Management" and "Transaction Processing" should be separate services because different teams work on them. Another argues they should be the same service because every transaction touches an account. Describe the exact data access patterns that would determine which decomposition is correct, and what the cost of getting it wrong would be.

**Q2.** Your decomposition is complete and services are running in production. Six months later, business priorities shift and two previously separate domains merge into one product area. The two corresponding services now change together 90% of the time. At what point is the operational cost of merging two microservices back into one worth paying, and how would you execute that merge without downtime?

