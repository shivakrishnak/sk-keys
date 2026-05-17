---
id: MSV-005
title: Service Decomposition
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-001, MSV-002, MSV-004
used_by: MSV-031, MSV-037, MSV-038, MSV-085
related: MSV-031, MSV-032, MSV-037, MSV-038, MSV-080
tags:
  - microservices
  - architecture
  - intermediate
  - pattern
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /microservices/service-decomposition/
---

# MSV-005 - Service Decomposition

⚡ TL;DR - Service Decomposition is the process of identifying
where to cut a system into independently deployable services,
using business capabilities and domain boundaries as the
primary guide.

| #005 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Microservices Architecture, Modular Monolith | |
| **Used by:** | Domain-Driven Design, Decomposition by Business Capability, Decomposition by Subdomain, Monolith to Microservices Migration | |
| **Related:** | Domain-Driven Design, Bounded Context, Decomposition by Business Capability, Decomposition by Subdomain, Conway's Law in Microservices | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have decided to move to microservices. You open the monolith
and split by technical layer: a "database service," a "business
logic service," and a "UI service." This mirrors your technical
architecture, not your business. To add a new product feature,
you now must deploy all three services simultaneously - you have
not bought deployment independence, just added network hops
between layers.

**THE BREAKING POINT:**
Alternatively, you split too finely: every database table gets
its own service. You have 80 services for a 15-developer product.
Every feature change touches 10 services. Cross-service transactions
require distributed sagas for what was a simple database join.

**THE INVENTION MOMENT:**
This is exactly why systematic Service Decomposition exists: to
provide a principled method for drawing service boundaries at
business capability lines, so that each service can evolve,
deploy, and scale independently because it maps to something
that changes independently in the business.

**EVOLUTION:**
Early SOA decomposed by technical function (reusable services).
Domain-Driven Design (Eric Evans, 2003) provided the Bounded
Context concept as a decomposition tool. Netflix popularised
fine-grained services around 2010. Sam Newman's "Building
Microservices" (2015) synthesised decomposition strategies.
Team Topologies (Skelton/Pais, 2019) added org-structure
as a decomposition constraint.

---

### 📘 Textbook Definition

**Service Decomposition** is the architectural practice of
partitioning a system into independently deployable services
by identifying stable business capabilities, bounded contexts,
or subdomains as boundaries. A well-decomposed system has high
cohesion within services (related functionality stays together)
and loose coupling between services (minimal cross-service
data and behavioural dependencies). The decomposition strategy
determines future team autonomy, deployment frequency, and
system evolution speed.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Service Decomposition is deciding where to cut - and getting
those cuts wrong is the most expensive mistake in microservices.

**One analogy:**
> Decomposing a business into services is like deciding how
> to organise a newspaper. You could split by process (writing,
> editing, printing each as a department) or by content area
> (Sports, Politics, Business each as an independent section).
> Process-based splits create bottlenecks when every story
> needs all departments. Content-based splits let each section
> operate independently because Sports does not need to wait
> for Politics.

**One insight:**
The right decomposition criterion is: what changes together
should live together. Business capabilities change together
because the business owns them. Technical layers (DB, API,
UI) span many capabilities and must change in sync - making
them wrong cut points.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A service boundary must be stable. If the boundary requires
   frequent renegotiation (schema sharing, joint deploys),
   it is wrong.
2. Each service must be independently releasable. A change to
   service A must not require a change to service B to deploy.
3. Services should correspond to a team ownership unit. If no
   team owns the service end-to-end, it will decay.

**DECOMPOSITION STRATEGIES:**

```
Strategy 1: By Business Capability
─────────────────────────────────
Business Capability = what the business does
Example (e-commerce):
  ┌──────────────┬──────────────┬──────────────┐
  │  Customer    │  Order       │  Catalog     │
  │  Management  │  Management  │  Management  │
  └──────────────┴──────────────┴──────────────┘
Stable? YES - capabilities change slowly
Team alignment? Natural - "Order team"

Strategy 2: By DDD Subdomain
────────────────────────────
Core Domain: unique competitive advantage → most services
Supporting Domain: needed but not differentiating → fewer
Generic Domain: commodity → buy/use off-the-shelf

Strategy 3: By Change Frequency (WRONG baseline)
────────────────────────────────────────────────
Do NOT split by "this module changes a lot" -
you end up with arbitrary cuts that don't reflect ownership
```

**THE TRADE-OFFS:**
**Gain:** Right decomposition = teams move independently,
services evolve separately, scaling is targeted.
**Cost:** Wrong decomposition = chatty services, distributed
transactions for simple operations, teams blocked on each other.
The wrong decomposition is WORSE than a monolith.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Every system has some coupling that crosses
service boundaries - you cannot eliminate it, only minimise it.
**Accidental:** Over-decomposition (nano-services) creates
artificial boundaries that generate more cross-service coupling
than necessary. Right-sizing services reduces accidental
complexity.

---

### 🧪 Thought Experiment

**SETUP:**
You are decomposing an online retail platform with these
operations: browse products, add to cart, checkout, pay,
ship, return, review product. You can split by technical
layer (DB/Logic/UI), by functional area (Catalog/Order/Payment),
or by user journey phase (Discovery/Purchase/Fulfillment).

**WHAT HAPPENS WITH WRONG DECOMPOSITION (by layer):**
- "DB service" owns all writes
- Every feature touches all three layers
- Adding a product attribute requires: Schema Service update,
  Logic Service update, UI Service update - three deploys

**WHAT HAPPENS WITH RIGHT DECOMPOSITION (by capability):**
- Catalog Service: browse, search, product detail
- Cart Service: add to cart, remove, update quantities
- Order Service: checkout, order history
- Payment Service: charge, refund
- Fulfillment Service: ship, track, return
- Review Service: submit and display reviews

Each change maps to one service. Adding a product attribute
means only Catalog Service changes and deploys.

**THE INSIGHT:**
The right decomposition cuts along the natural seams of the
business - where the organisation already thinks in separate
domains. If your business has a "Catalog team" and an "Order
team," your service boundaries should match. Conway's Law is
not a warning, it is guidance.

---

### 🧠 Mental Model / Analogy

> Service decomposition is like designing rooms in a house.
> You could have one giant open space (monolith) or many
> tiny rooms (nano-services). The right design has rooms
> sized for their purpose: one kitchen, one bathroom,
> bedrooms by occupant. The rule is: things that need
> privacy or different use patterns get their own room.
> A bathroom and a kitchen share nothing and have
> different visitors - separate rooms. A master bedroom
> and its ensuite bathroom are closely coupled and share
> occupants - together.

- "Room" - service
- "Privacy / different visitors" - different teams or users
- "Close coupling" - things that change together
- "Shared occupants" - shared data or operations

Where this analogy breaks down: rooms have obvious physical
boundaries. Service boundaries require explicit design -
the coupling in software is invisible until you draw it.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Service Decomposition is deciding which parts of your
application should be their own independent service. It is
the most important decision in microservices because the
wrong cut makes everything harder, not easier.

**Level 2 - How to use it (junior developer):**
When joining a decomposition exercise, ask: "What do our
teams already own?" Map existing team ownership to service
candidates. A team that already owns "Orders end-to-end"
suggests an Order Service. This is the first signal. Then
ask: "What changes together?" If catalog and pricing always
change in the same sprint, they might belong together.

**Level 3 - How it works (mid-level engineer):**
The DDD approach: identify Bounded Contexts (a linguistic
boundary where a term like "Product" means the same thing
to the same team). Each Bounded Context becomes a service
candidate. Then classify by subdomain type: Core (build),
Supporting (build or buy), Generic (buy/off-the-shelf).
Allocate more services to the Core domain where you
differentiate.

**Level 4 - Why it was designed this way (senior/staff):**
The stability rule is the key insight: service boundaries
that are stable over time are correct; those that require
constant renegotiation are wrong. Technical boundaries
(by layer) are almost always wrong because they span
all business capabilities. Business capability boundaries
are almost always right because the business defines them.
The DDD Bounded Context adds precision: each context has
its own ubiquitous language, which means terms do not bleed
across boundaries unexpectedly.

**Level 5 - Mastery (distinguished engineer):**
Staff engineers apply the "team cognitive load" test to
every proposed boundary. A service boundary is correct
when the team that owns it can understand the full system
behaviour of that service in their heads - its API, its
failure modes, its data model, its dependencies. If owning
a service requires knowing too much about another team's
service, the boundary is wrong. Team Topologies (Skelton/
Pais) formalises this: stream-aligned teams own end-to-end
capabilities; platform teams own shared infrastructure.
The service architecture mirrors this topology.

---

### ⚙️ How It Works (Mechanism)

**DECOMPOSITION PROCESS:**

```
Step 1: Identify Business Capabilities
───────────────────────────────────────
Workshop: "What does this business DO?"
Not "How is it built?" but "What value does it provide?"

E-commerce capabilities:
  - Customer Identity Management
  - Product Catalog Management
  - Pricing and Promotions
  - Order Management
  - Payment Processing
  - Inventory Management
  - Fulfillment and Shipping
  - Customer Support
  - Reviews and Recommendations

Step 2: Map to Teams
────────────────────
Which team already owns or should own each capability?
A capability without a clear team owner = a service risk.

Step 3: Identify Data Ownership
────────────────────────────────
Which database entities belong to which capability?
Entities that must be split across multiple capabilities
indicate a boundary problem.

Step 4: Identify Coupling
──────────────────────────
Draw arrows: which capability reads data from which?
High in-degree = shared kernel or boundary problem.
Circular dependencies = wrong boundary.

Step 5: Validate with Change Frequency
────────────────────────────────────────
Review last 3 months of features. Which capabilities
changed together? If A and B always change together,
they might be one service, not two.
```

**DECOMPOSITION ANTI-PATTERNS:**

```
Anti-Pattern 1: Decomposition by layer
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  DB Svc  │  │Logic Svc │  │  UI Svc  │
  └──────────┘  └──────────┘  └──────────┘
  Every feature touches all 3. WRONG.

Anti-Pattern 2: Nano-services (too fine)
  ┌────────┐ ┌─────────┐ ┌──────────┐
  │Get User│ │Save User│ │Delete Usr│
  └────────┘ └─────────┘ └──────────┘
  Trivial operations are separate services. WRONG.

Anti-Pattern 3: Chatty boundaries
  OrderService → calls UserService 5 times per request
  → calls InventoryService 3 times per request
  → calls PricingService 2 times per request
  Indicates the Order boundary is too narrow. WRONG.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**WELL-DECOMPOSED SYSTEM INTERACTION:**

```
User: "Place an order"
  │
  ▼
API Gateway → routes to Order Service
  │
  ▼
Order Service  ← YOU ARE HERE (owns order lifecycle)
  │ calls Payment Service once (charge)
  │ publishes OrderPlaced event
  │ owns its own DB (orders table)
  ▼
Payment Service (owns payment lifecycle)
  │ charges card
  │ publishes PaymentConfirmed event
  ▼
Fulfillment Service (consumes OrderPlaced)
  │ creates shipment
  │ owns its own DB (shipments table)
  ▼
Notification Service (consumes PaymentConfirmed)
  │ sends confirmation email
```

Each service owns its step. No service needs to know the
internals of another.

**FAILURE PATH:**
```
Payment Service returns error
  → Order Service compensates (cancel order creation)
  → Returns error to user
  Fulfillment Service never receives OrderPlaced event
  (event not published because payment failed)
  No orphaned shipments
```

**WHAT CHANGES AT SCALE:**
At 10x load, Order Service scales independently of Fulfillment.
If Fulfillment is the bottleneck (shipping partner is slow),
only Fulfillment scales up. At 100x, event-driven communication
becomes critical - synchronous calls to all downstream services
would create a latency multiplication cascade.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: decomposition by layer**

```java
// BAD: three services, one per technical layer
// Feature "get order with user name" requires all 3 services:

// DB Service
@RestController
public class DatabaseController {
    @GetMapping("/query")  // Generic DB query endpoint!
    public Object query(@RequestBody String sql) { ... }
}

// Logic Service
@RestController
public class LogicController {
    @GetMapping("/order/{id}")
    public OrderWithUser getOrder(@PathVariable Long id) {
        // Calls DB Service twice (order + user)
        Order order = dbService.query("SELECT * FROM orders ...");
        User user = dbService.query("SELECT * FROM users ...");
        return merge(order, user);
    }
}
// Every change needs both services. Shared DB = monolith.
```

```java
// GOOD: decomposition by business capability

// Order Service - owns orders domain end-to-end
@RestController
public class OrderController {
    @GetMapping("/orders/{id}")
    public OrderResponse getOrder(@PathVariable Long id) {
        Order order = orderRepo.findById(id); // owns DB
        // Gets user name via User Service public API
        UserDTO user = userClient.getUser(order.getUserId());
        return OrderResponse.from(order, user.getName());
    }
}
// Order Service owns: order entity, order repository,
// order business logic, order API
// It calls User Service for user-related data only
```

**Example 2 - Identifying boundaries using event storming**

```
Event Storming notation (on a whiteboard or Miro board):

DOMAIN EVENTS (orange sticky notes):
  OrderPlaced | PaymentReceived | ItemShipped |
  ItemReturned | ReviewSubmitted

COMMANDS (blue sticky notes):
  PlaceOrder → OrderPlaced
  ProcessPayment → PaymentReceived
  ShipItem → ItemShipped

AGGREGATES (yellow sticky notes):
  Order aggregate: {PlaceOrder, CancelOrder} → OrderPlaced
  Payment aggregate: {ProcessPayment} → PaymentReceived
  Shipment aggregate: {ShipItem, TrackItem} → ItemShipped

Aggregates = Service candidates!
```

**How to test / verify correctness:**
After decomposition, apply the "independent deployment test":
can you deploy Service A (with a backwards-compatible change)
without deploying Service B? If not, the boundary is wrong.
Also apply the "own your data test": does Service A ever
read Service B's database tables directly? If yes, the
boundary is wrong.

---

### ⚖️ Comparison Table

| Strategy | Stability | Team Alignment | Risk | Best For |
|---|---|---|---|---|
| **By Business Capability** | High | Natural | Low | Most systems |
| By DDD Subdomain | High | Natural | Medium | Complex domains |
| By Resource/Entity | Medium | Technical | High | Simple CRUD |
| By Technical Layer | Low | Technical | Very High | Never recommended |
| By Change Frequency | Low | None | High | Poor heuristic alone |

**How to choose:** Start with Business Capability decomposition
for its team alignment and stability. Apply DDD Bounded Context
analysis to clarify boundaries where capabilities overlap
or share data. Avoid technical layer decomposition entirely.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Smaller services are always better | Services should be sized to match a team's cognitive load. "Microservices" means small responsibility, not small code size. |
| You can get decomposition right the first time | Service boundaries evolve as the domain is better understood. Plan for service merges as well as splits. |
| Two-pizza team rule means each service = one team | One team can own multiple services. The rule is cognitive load per team, not ratio of teams to services. |
| Decomposition is a one-time architectural decision | It is ongoing. Correct decomposition changes as the business changes and as domain understanding deepens. |

---

### 🚨 Failure Modes & Diagnosis

**Chatty services - too-fine decomposition**

**Symptom:**
A single user action (e.g., view order detail) triggers 8-12
HTTP calls across 6 different services. P99 latency is 2 seconds
despite each service responding in 50ms.

**Root Cause:**
Service boundaries were drawn too finely. Operations that
logically belong together (order + items + shipping address)
were split into separate services, requiring an API
composition layer for every read.

**Diagnostic Command:**
```bash
# Count unique service calls in a distributed trace
curl -s "http://jaeger:16686/api/traces/$TRACE_ID" \
  | jq '[.data[0].spans[].operationName] | unique | length'

# Count: if > 5 unique services for a single user operation,
# investigate decomposition
```

**Fix:**
Consider merging Order, OrderItems, and ShippingAddress into
one Order Service (high cohesion, same bounded context).
Alternatively, introduce an API Composition service or
GraphQL layer that batches the reads.

**Prevention:**
At design time, trace the full request flow for the top 3
most common user operations. If any operation requires >3
sequential service calls, reconsider the boundaries.

---

**Circular service dependencies**

**Symptom:**
Order Service calls Payment Service. Payment Service calls
Order Service to update payment status. Deploying either
requires deploying both. Team A is blocked on Team B.

**Root Cause:**
The boundary was drawn incorrectly. Payment status update
logically belongs to the entity that owns the order lifecycle.

**Diagnostic Command:**
```bash
# Map call graph (extract from distributed trace data)
curl -s "http://jaeger:16686/api/services" \
  | jq '.data[]'

# Visualise dependencies
# In Grafana service map or Kiali (for Istio)
```

**Fix:**
Break the circular dependency by event-driven communication:
Payment Service publishes `PaymentCompleted` event. Order
Service subscribes and updates its own status. Neither
service calls the other directly.

**Prevention:**
Draw the service dependency graph before implementation.
Any cycle in the graph = wrong boundary. Resolve before
coding begins.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Monolith vs Microservices` - why decomposition is needed
- `Microservices Architecture` - the constraints that
  well-decomposed services must satisfy

**Builds On This (learn these next):**
- `Domain-Driven Design (DDD)` - the theory behind capability
  and subdomain decomposition
- `Bounded Context` - the DDD boundary concept that maps
  to service boundaries
- `Decomposition by Business Capability` - detailed pattern
- `Decomposition by Subdomain` - DDD-based variant

**Alternatives / Comparisons:**
- `Modular Monolith` - applies the same decomposition logic
  without the network boundary; lower operational cost
- `Conway's Law` - org structure as a decomposition guide

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Finding where to cut a system into         │
│              │ independently deployable services          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Wrong cuts = chatty services, distributed  │
│ SOLVES       │ transactions, teams blocked on each other  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cut at business capability boundaries -    │
│              │ NOT at technical layer boundaries          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing a new microservices system OR    │
│              │ extracting services from a monolith        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Domain not yet understood - premature      │
│              │ decomposition creates wrong boundaries     │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Nano-services per DB table; layer services │
│              │ (DB/Logic/UI); circular dependencies       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Team autonomy + independent deploys vs     │
│              │ cross-service latency + coordination cost  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wrong service boundaries are worse than   │
│              │  no decomposition at all"                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Domain-Driven Design → Bounded Context     │
│              │ → Decomposition by Business Capability     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Cut at business capability boundaries - what the business
   does, not how it is technically structured.
2. A well-cut service supports independent deployment. A
   poorly-cut service creates deployment dependencies that
   are worse than a monolith.
3. Circular service dependencies always indicate a wrong
   boundary - resolve with event-driven communication or
   by merging the services.

**Interview one-liner:**
"Service Decomposition means finding where to cut the system
along business capability or DDD bounded context lines. Wrong
cuts - by technical layer or too-fine granularity - create
chatty services and distributed transactions for operations
that were simple DB joins. The test is: can each service
deploy independently without triggering cascading changes?"

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
High cohesion within boundaries and low coupling between
them is the universal architecture principle. It applies at
every scale: functions within a class, classes within a
module, modules within a service, services within a system.
Correct decomposition at any level means: things that change
together live together; things that change independently are
separate.

**Where else this pattern appears:**
- Database normalization - decompose data by functional
  dependency to avoid update anomalies
- Team structure - org design follows the same boundary
  principles (Conway's Law runs in both directions)
- API design - endpoints are decomposed by resource
  (noun) not by operation (verb), mirroring business objects

**Industry applications:**
- Healthcare systems - patient, appointment, billing, and
  prescriptions are natural capability boundaries; they
  change independently and are owned by different departments
- Banking platforms - accounts, payments, lending, and
  fraud are different domains with different change rates,
  compliance requirements, and team structures

---

### 💡 The Surprising Truth

Amazon's service decomposition was not driven by a
technology strategy - it was forced by a business problem.
The Amazon retail site originally had services organised
around customer-facing pages (home page service, product
detail service, checkout service). When the company launched
AWS and third-party seller APIs, they discovered that their
page-oriented services could not be reused independently.
The pivot to capability-based decomposition (inventory,
pricing, orders) was driven by the need to expose individual
capabilities as APIs to external partners - not by a desire
to scale engineering teams.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Given a ride-sharing domain, identify 5-7
   business capabilities and justify each boundary with
   "this changes independently because..."
2. **DEBUG** Given a microservices architecture with 3-second
   P99 latency for a simple read operation, use distributed
   tracing to identify which service calls are chained
   sequentially and which boundary decisions caused them.
3. **DECIDE** Two services call each other in a circular
   dependency. Propose a decomposition change (merge, split,
   or event-driven) with trade-off analysis for each option.
4. **BUILD** Run an Event Storming session for an e-commerce
   checkout flow. Identify the domain events, commands, and
   aggregates, then derive 3-4 service candidates with their
   data ownership.
5. **EXTEND** Apply capability-based decomposition to
   a data platform (ingestion, processing, storage, serving,
   monitoring). Identify which capabilities are core (build)
   vs generic (buy), and where the most likely incorrect
   boundary would be drawn.

---

### 🧠 Think About This Before We Continue

**Q1.** A large insurance company has a Claims service that
needs data from Policy, Customer, and Payment services to
process a claim. This requires 4 synchronous service calls
in sequence. A staff engineer says "the boundary is wrong"
and a junior engineer says "this is just microservices
overhead." Who is right, and what specific evidence from
the call pattern would confirm the answer?
*Hint: Distinguish between essential cross-service reads
(data genuinely owned elsewhere) and artificial boundaries
(data that should be in the same service).*

**Q2.** Two teams propose splitting the Payments capability
into micro-services: PaymentMethodService, ChargeService,
RefundService, and PaymentHistoryService. Each team member
owns one service. Evaluate this decomposition. What is the
key question to ask about each proposed boundary?
*Hint: Apply the "change together, live together" and
"team cognitive load" tests.*

**Q3.** You are given a 5-year-old monolith with 500k lines
of Java. You have 3 weeks to recommend a decomposition plan.
Describe your discovery process (what you look at, in what
order) and how you would identify the first service to extract
with the lowest risk.
*Hint: Look for natural seams: modules that already have
few imports from other modules are already semi-isolated.*

---

### 🎯 Interview Deep-Dive

**Q1: "How do you decide where to draw service boundaries?
Walk me through your process."**

*Why they ask:* The most common and most revealing
microservices architecture question.

*Strong answer includes:*
- Start with business capabilities (what the business does)
- Map teams: who currently owns which capability?
- Apply DDD: identify bounded contexts and their language
- Validate with change frequency: do these change together?
- Test: can each service deploy independently after the cut?

**Q2: "What is a chatty service relationship and how do
you fix it?"**

*Why they ask:* Tests practical experience with decomposition
failure modes.

*Strong answer includes:*
- Definition: Service A makes 5+ calls to Service B per
  request, indicating B's data is too granular or belongs
  in A's bounded context
- Fix options: merge services if they share a bounded context;
  introduce a read model (CQRS) that pre-aggregates B's data;
  use async event-driven updates to maintain a local copy in A
- Tradeoff: merging reduces network overhead but increases
  service size; local copy introduces eventual consistency

**Q3: "Your team has a User service with 50 different
endpoints covering authentication, profile management,
preferences, and notifications. A colleague says to
split this into 4 services. How do you evaluate this?"**

*Why they ask:* Tests right-sizing judgment vs reflexive
decomposition.

*Strong answer includes:*
- Auth: likely separate (different security requirements,
  different scaling - every request hits auth)
- Profile management + preferences: likely together (same
  bounded context, change together, same team)
- Notifications: separate if different team or different
  scaling (async, high volume)
- Test: do these 4 things have different change frequencies?
  Different team owners? Different scaling profiles?
  If all no → keep together or modular monolith approach