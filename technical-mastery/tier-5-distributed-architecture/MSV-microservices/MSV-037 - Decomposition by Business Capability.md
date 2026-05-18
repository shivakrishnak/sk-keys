---
id: MSV-037
title: Decomposition by Business Capability
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-031, MSV-032, MSV-005
used_by: MSV-005
related: MSV-031, MSV-032, MSV-005, MSV-038, MSV-080, MSV-081
tags:
  - microservices
  - architecture
  - deep-dive
  - ddd
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/microservices/decomposition-by-business-capability/
---

⚡ TL;DR - Decomposition by Business Capability splits
a system into services based on the distinct things a
business does (its capabilities), rather than by
technical layers or data entities. A business capability
is a stable business function: Pricing, Order Management,
Inventory Control, Customer Management. Each capability
becomes a service. Stability is the key benefit: business
capabilities rarely change even as implementations do.

| #037 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain-Driven Design (DDD), Bounded Context, Service Decomposition | |
| **Used by:** | Service Decomposition | |
| **Related:** | Domain-Driven Design (DDD), Bounded Context, Service Decomposition, Decomposition by Subdomain, Conway's Law in Microservices, Team Topologies | |

---

### 🔥 The Problem This Solves

**TECHNICAL LAYER DECOMPOSITION FAILURE:**
A team decomposes by technical layer: "Data Service",
"Business Logic Service", "API Service". Result: every
feature change requires modifications to all three
services. Deploying a new feature requires coordinating
three teams. This is a distributed monolith: technically
separated but functionally coupled.

Alternative failure: decompose by data entity. "Customer
Service", "Product Service", "Order Service" - but Order
Service needs customer data for every call. Chatty
services, N+1 API calls, high coupling.

Business Capability decomposition: each service encapsulates
one complete business capability (data + logic + API).
Changing how pricing works = update Pricing Service only.
No coordination with other teams.

---

### 📘 Textbook Definition

**Decomposition by Business Capability** is a microservice
decomposition strategy where services are defined around
business capabilities - the things a business does to
create value. A business capability is: a stable,
business-meaningful function that the organisation
performs. It encapsulates the data, logic, and process
for that function. Unlike technical decomposition (by
layer) or data decomposition (by entity), business
capability decomposition creates services that are
stable, cohesive, and aligned with organisational
structure. Source: Chris Richardson's Microservices
Patterns; rooted in DDD's Bounded Context concept.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Decompose by what the business DOES, not by how the
code is technically structured.

**One analogy:**
> A department store has departments: Menswear, Electronics,
> Food, Cosmetics. Each department handles its own
> products, pricing, staff, and inventory. This is
> decomposition by business capability. A technical
> layer decomposition would be: one "Inventory Department"
> for all products, one "Pricing Department" for all
> departments. Problem: changing menswear pricing requires
> coordinating with the pricing department AND the
> menswear department. Department (capability) decomposition:
> menswear owns its own pricing. One department, one team.

**One insight:**
Business capabilities are far more stable than
technical implementations. The capability "manage orders"
has existed in retail for centuries. The IMPLEMENTATION
changes (paper ledger -> mainframe -> web app -> microservice).
Decomposing by capability creates service boundaries
that survive technical changes. Decomposing by technical
layer creates boundaries that change when technology
changes.

---

### 🔩 First Principles Explanation

**BUSINESS CAPABILITY HIERARCHY:**

```
BUSINESS CAPABILITY MAP (e-commerce example):

Level 1 (Business Areas):
  Product Management
  Customer Management
  Order Management
  Fulfillment
  Finance
  
Level 2 (Capabilities within areas):
  Product Management:
    - Catalog Management    -> catalog-service
    - Pricing Management    -> pricing-service  
    - Inventory Management  -> inventory-service
  
  Customer Management:
    - Customer Identity     -> identity-service
    - Customer Profile      -> profile-service
    - Loyalty Program       -> loyalty-service
  
  Order Management:
    - Shopping Cart         -> cart-service
    - Order Processing      -> order-service
    - Order Tracking        -> tracking-service
  
  Fulfillment:
    - Warehouse Operations  -> warehouse-service
    - Shipping              -> shipping-service
    - Returns               -> returns-service
  
  Finance:
    - Payment Processing    -> payment-service
    - Invoicing             -> invoice-service
    - Fraud Detection       -> fraud-service
                            (or use external: Kount)

EACH CAPABILITY:
  - Has clear business ownership
  - Has its own data
  - Has independent lifecycle
  - Stable: even if the tech changes, the capability exists
```

**CHARACTERISTICS OF A GOOD BUSINESS CAPABILITY:**

```
STABILITY:
  True business capabilities rarely disappear.
  "Process payment" has been a business capability
  for 200 years. The implementation changes.
  A good capability boundary survives 5+ years.

OWNERSHIP:
  One team owns one capability.
  Conway's Law: team structure = service structure.
  If two teams own the same capability: coupling.
  If one team owns two capabilities: candidate for split.

COHESION:
  Everything needed to perform the capability is
  inside the service. No "phone home" to other services
  for core operations.

INDEPENDENCE:
  Can deploy the capability independently.
  Can change the capability's implementation without
  affecting other capabilities.
```

---

### 🧪 Thought Experiment

**TECHNICAL LAYER vs BUSINESS CAPABILITY:**

```
FEATURE: "Apply loyalty discount at checkout"

TECHNICAL LAYER DECOMPOSITION:
  Required changes:
  1. API Service: add discount parameter to checkout API
  2. Business Logic Service: add discount calculation
  3. Data Service: add discount to order schema
  4. Order Service: apply discount to order total
  5. Loyalty Service: deduct loyalty points used
  
  Teams involved: 4-5 teams, 3-4 sprints, high coordination

BUSINESS CAPABILITY DECOMPOSITION:
  Required changes:
  1. Loyalty Service: add discountForOrder(orderId) method
  2. Order Service: call loyalty.discountForOrder() at
    checkout
  
  Teams involved: 2 teams, 1 sprint, minimal coordination
  Order Service: calls loyalty API, applies discount
  Loyalty Service: owns loyalty rules, discount calculation
  
  RESULT: 4x faster feature delivery, 2x fewer teams
    involved
```

---

### 🧠 Mental Model / Analogy

> Business Capability decomposition is like organising
> a toolbox by task, not by material. A "by material"
> toolbox has all metal objects together (screws, nails,
> drill bits, wrenches) and all plastic objects together.
> To fix a shelf: look in metal tools (screw), then
> plastic tools (wall anchor), then back to metal
> (drill bit). A "by task" toolbox: "hanging things"
> drawer has screws, anchors, drill bits, and a level
> all together. One drawer = one capability = everything
> needed for that task. Business Capability decomposition
> is the "by task" toolbox approach.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Decompose services based on what the business does.
Pricing team -> Pricing Service. Order management team
-> Order Service. Each service does one business thing
completely.

**Level 2 - How to use it (junior developer):**
List the distinct things your business does. Each
distinct thing (capability) becomes a candidate service.
A good test: can a business person describe what the
service does in one sentence without using technical
terms? "Pricing Service calculates product prices with
discounts and promotions." Yes. "Data Service stores
and retrieves records." No - too technical.

**Level 3 - How it works (mid-level engineer):**
Business Capability Map is the tool. Draw a hierarchy:
business areas at the top, capabilities below each.
Each Level-2 capability is a service candidate. For
each candidate: identify ownership (which team?), data
requirements (which DB tables?), and integration points
(which other services?). Use DDD Event Storming to
validate: the Bounded Contexts from Event Storming
should align with business capabilities.

**Level 4 - Why it was designed this way (senior/staff):**
Business capabilities align with Bounded Contexts (DDD)
because both represent stable boundaries of meaning.
The capability "manage orders" = the Order Bounded
Context. The ubiquitous language within the capability
is consistent. Conway's Law: the team that owns the
capability owns the code. Changes flow within one team.
This is why Spotify's engineering model (squads aligned
to capabilities) produces faster feature delivery:
the team owns the full stack for their capability.

**Level 5 - Mastery (distinguished engineer):**
Business capability vs subdomain: capabilities are
stable business functions that deliver value; subdomains
are areas of business knowledge. They usually align
but not always. A subdomain may span multiple capabilities
("customer" spans identity, profile, loyalty, support).
A capability may span multiple subdomains in edge cases.
The practical difference: capability decomposition
focuses on what the business DOES (operations); subdomain
decomposition focuses on what the business KNOWS
(knowledge areas). For microservices: capability
decomposition gives better service ownership alignment
with team structure; subdomain gives better alignment
with domain expert knowledge.

---

### ⚙️ How It Works (Mechanism)

**BUSINESS CAPABILITY MAPPING PROCESS:**

```
STEP 1: IDENTIFY BUSINESS AREAS
  Interview: C-level, VPs, department heads
  Question: "What does this business do?"
  Output: 5-8 top-level business areas

STEP 2: DECOMPOSE TO CAPABILITIES
  For each area: "What specific things do you do?"
  Pricing area: calculate list price, apply promotions,
  set geographic pricing, manage contracts
  Output: 30-60 capabilities

STEP 3: OWNERSHIP ANALYSIS
  For each capability: which team owns it?
  If multiple teams: boundary may be wrong
  If no team: capability is unmapped/risky

STEP 4: SERVICE CANDIDATES
  Each Level-2 capability = one service candidate
  Apply sizing heuristics:
  - "Two-pizza team" (5-8 engineers): right size
  - One engineer with too much context: too small
  - Multiple teams needed: too large (split)

STEP 5: VALIDATE WITH EVENT STORMING
  Domain events from Event Storming should align with
  capability boundaries. Events that cross boundaries:
  candidates for async integration (Domain Events).
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CAPABILITY MAP TO SERVICE DESIGN:**

```
Pricing Capability -> Pricing Service

Owner: Pricing team (4 engineers)
Capability description:
  "Calculate the price for a product for a customer
   in a context (cart, catalog, partner API)"

What it does:
  - List price from catalog
  - Customer-specific discount (loyalty tier)
  - Promotional discount (current campaigns)
  - Geographic pricing (currency, tax)
  - B2B contract pricing

Service responsibilities:
  POST /prices/calculate (input: productId, customerId,
                          context, qty)
  Response: { listPrice, discount, finalPrice, breakdown }

Data owned:
  Pricing rules DB (PostgreSQL)
  Promotion cache (Redis)

Integrations:
  Reads: product catalog (sync API call for base price)
  Reads: customer profile (sync API call for tier)
  Reads: active promotions (async sync from marketing)
  No writes to other services - pricing is read-heavy

Team: pricing-team (one team, full ownership)
Deploy: independent, daily deployments
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: technical vs capability decomposition**

```java
// BAD: Technical layer decomposition
// "Order Data Service" - stores/retrieves orders
// "Order Business Service" - applies business rules
// "Order API Service" - HTTP endpoints
// Every order feature change touches all three services
// Three teams must coordinate for one feature
@Service
public class OrderBusinessService {
    // Calls OrderDataService for data (coupling!)
    // Called by OrderAPIService for logic (coupling!)
    // No team owns the complete capability
}
```

```java
// GOOD: Business capability - Order Processing Service
// One service = one team = one capability
// Complete: HTTP endpoints, business logic, data access
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {
    // HTTP API: owned by order team
}

@Service
public class OrderApplicationService {
    // Business logic: owned by order team
    // Uses DDD: Order aggregate, domain events
}

@Repository
public interface OrderRepository {
    // Data access: order team owns the DB schema
    // No shared tables with other services
}

// One team: order team
// One deploy: order-service
// One codebase: order-service repo
// Feature: pricing discount -> pricing-service team
// Feature: loyalty points -> loyalty-service team
// Feature: order email notification -> notification team
// All independent!
```

---

### ⚖️ Comparison Table

| Decomposition Strategy | Stability | Team Alignment | Change Scope |
|---|---|---|---|
| **By business capability** | High (capabilities stable) | Strong (one team per capability) | One service per feature |
| **By subdomain** | High (domain knowledge stable) | Strong (domain experts guide) | One service per feature |
| **By technical layer** | Low (technology changes) | Weak (layers span features) | All layers per feature |
| **By data entity** | Medium (entities stable, but chatty) | Weak | Multiple services per feature |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Each CRUD entity is a business capability | Business capabilities are higher-level than entities. "Manage Customer" is a capability; Customer, Address, Preferences are entities within that capability. One service for the capability, not one service per entity. |
| Business capabilities never change | Business capabilities do evolve, but much more slowly than technology. A retail business's "process payment" capability is 100 years old; the implementation changed from cash registers to digital wallets. Capabilities at the right level of abstraction are stable for years. |
| Teams must perfectly match capabilities from day 1 | Start with capability mapping, then create services incrementally (Strangler Fig). Don't create all 30 services on day 1. Start with the highest-value capabilities and extract them from the monolith gradually. |

---

### 🚨 Failure Modes & Diagnosis

**Capability boundary too fine-grained: chatty services**

**Symptom:**
Checkout flow requires calling 12 services: catalog,
pricing, cart, order, payment, fraud, inventory, loyalty,
notification, tax, shipping estimate, address validation.
Latency: 2 seconds. Every service is a network hop. Any
one service failure breaks checkout.

**Root Cause:**
Capabilities were decomposed too granularly. "Tax
Calculation" is not a standalone business capability
at the Level-2 scale of most businesses - it's a function
within "Order Processing". Similarly, "Address Validation"
is a function within "Customer Management", not a separate
business capability.

**Diagnostic:**
```
Capability sizing check:
1. Team size: < 2 engineers -> too small, probably should
   be a function within a larger capability
2. Deploy frequency: same change deploys to 3 services
   together every sprint -> they should be one service
3. API call count: > 5 synchronous calls per user request
   -> capabilities likely too granular
4. Business value: can a business person articulate
   the standalone value of this capability?
   "Tax calculation" -> "it's part of order processing"
   -> should be internal to order-service
```

**Fix:**
1. Consolidate related functions into owning capability
   (Tax calculation -> Order Processing)
2. Move validation to the consuming service or to a
   shared library (address validation as library vs service)
3. Apply the CQRS pattern for read-heavy capabilities:
   materialise a checkout summary pre-computed view
   instead of 12 synchronous calls

---

### 🔗 Related Keywords

**Prerequisites:**
- `Domain-Driven Design (DDD)` - capability mapping
  is informed by DDD strategic patterns
- `Bounded Context` - business capabilities map to
  bounded contexts
- `Service Decomposition` - the general principle of
  which capability-based is a specific strategy

**Comparison:**
- `Decomposition by Subdomain` - alternative approach
  using DDD subdomains rather than business capabilities

**Organisational:**
- `Conway's Law in Microservices` - team structure
  must align with capability boundaries
- `Team Topologies` - provides organisational patterns
  for aligning teams to capabilities

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Service = one business capability        │
│              │ Capability = stable, team-owned function │
├──────────────┼──────────────────────────────────────────┤
│ VS TECHNICAL │ Bad: Data/Logic/API layer services       │
│              │ Good: Pricing/Order/Inventory services   │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Split by what the business does;        │
│              │  one team, one capability, one service"  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Decomposition by Subdomain → Conway's Law│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Decompose by what the business DOES, not by technical
   layer. Each capability = one service = one team.
2. Business capabilities are stable: "Process Payment"
   exists regardless of technology. Technical layers
   are volatile: they change with every technology shift.
3. Right-size by team: 5-8 engineers per service. If
   two teams own one service: split. If one engineer
   owns five services: consider merging some.

**Interview one-liner:**
"Decomposition by Business Capability means each microservice
corresponds to one stable business function (Pricing,
Order Management, Inventory). One team owns one capability
from API to data. Feature changes flow within one team.
Alternative - technical layer decomposition (Data/Logic/API
services) - requires all three teams to coordinate for
every feature: the distributed monolith anti-pattern."

---

### 💡 The Surprising Truth

The most revealing test of business capability decomposition
is Conway's Law retrospective: count the number of teams
required for a typical feature change. If a "single
feature" routinely requires 3+ teams to coordinate:
your service boundaries don't match your business
capabilities. The average feature should be completable
by 1-2 teams. If it's not: the boundaries are drawn
along technical, not capability, lines. The fix is not
necessarily merging services - it's re-drawing boundaries.
This is often politically difficult (existing teams own
existing services). But the coordination cost compounds:
a team spending 30% of their time in cross-team planning
for feature delivery is a 30% productivity tax that
scales with team count. Ten teams: the coordination
tax can consume more capacity than feature delivery.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **MAP** Build a business capability map for a given
   business domain: identify Level-1 areas and Level-2
   capabilities, verify each has clear ownership.
2. **DECOMPOSE** Given a monolith, identify which parts
   correspond to which capabilities; design the extraction
   order (highest value, lowest coupling first).
3. **VALIDATE** Apply the Conway's Law test: does
   your service decomposition match your team structure?
   Where it doesn't: identify the tension and its cost.
4. **SIZE** Given a proposed decomposition with 30
   micro-services, identify which should be merged
   (too fine-grained) using team size and coordination
   frequency as criteria.
5. **COMPARE** Articulate the trade-offs between
   capability-based and subdomain-based decomposition
   for a specific domain and team structure.

---

### 🧠 Think About This Before We Continue

**Q1.** A fintech startup has 10 engineers and is building
a personal finance app. They are debating whether to
create 15 microservices from day 1 (one per capability)
or start with a monolith. Apply the business capability
framework: which capabilities should be separate services
from day 1 (if any), and which should be in a monolith
initially?

**Q2.** The Pricing Capability at an e-commerce company
currently includes: catalog price management, promotional
discount calculation, B2B contract pricing, and real-time
competitor price monitoring. Four different sub-teams
work on these. Evaluate whether this is one capability
or four. Apply the business capability sizing criteria.

**Q3.** Your current "Order Service" includes: shopping
cart, checkout, order processing, order tracking, and
returns. After growth, this service is now maintained
by 12 engineers across 3 sub-teams. Apply the business
capability decomposition to propose a split. What are
the services? Who owns each? How do they integrate?