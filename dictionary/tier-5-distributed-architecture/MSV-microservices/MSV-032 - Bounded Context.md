---
id: MSV-032
title: Bounded Context
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-031, MSV-005, MSV-034
used_by: MSV-035, MSV-037, MSV-038, MSV-053
related: MSV-031, MSV-033, MSV-034, MSV-035, MSV-037, MSV-038, MSV-053, MSV-005
tags:
  - microservices
  - architecture
  - deep-dive
  - ddd
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /microservices/bounded-context/
---

# MSV-032 - Bounded Context

⚡ TL;DR - Bounded Context is a DDD (Domain-Driven Design)
strategic pattern that defines a clear boundary within
which a domain model is valid and consistent. Within
the boundary: terms have specific meanings, models are
cohesive, and a single team owns the design. In microservices:
each Bounded Context typically corresponds to one service
(or a small cluster). The boundary prevents "model
pollution": the same term (Customer, Order, Product)
means different things in different contexts.

| #032 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain-Driven Design (DDD), Service Decomposition, Ubiquitous Language | |
| **Used by:** | Anti-Corruption Layer, Decomposition by Business Capability, Decomposition by Subdomain, Database per Service | |
| **Related:** | Domain-Driven Design (DDD), Aggregate, Ubiquitous Language, Anti-Corruption Layer, Decomposition by Business Capability, Decomposition by Subdomain, Database per Service, Service Decomposition | |

---

### 🔥 The Problem This Solves

**THE "UNIVERSAL MODEL" TRAP:**
A senior architect says: "We need ONE canonical Customer
model used everywhere." The canonical model has 85 fields.
Every team must include ALL 85 fields in their Customer
data, even if they only care about 3. Adding a new field
requires a DB migration affecting 15 services. The
"User" concept means different things to different teams:
Sales says User = "lead"; Marketing says User = "subscriber";
Engineering says User = "account". One model satisfies
none of them fully.

The universal model breaks down because: (1) the domain
is too large and diverse for one coherent model, (2)
different contexts have genuinely different invariants
and rules, (3) forced model unification creates coupling
without cohesion. Bounded Contexts say: stop trying to
force one model. Let each context have its own.

---

### 📘 Textbook Definition

**Bounded Context** is a central pattern in Domain-Driven
Design that defines a boundary around a domain model.
Within the boundary: a Ubiquitous Language is used
consistently, terms have specific meanings, and the model
is internally consistent. Across boundaries: the same
term may exist with different meanings. The boundary is
enforced by: team ownership (one team per context),
technical enforcement (separate codebase, database, API),
and integration via explicit contracts (APIs, events).
In microservices: 1 Bounded Context = 1 service (preferred)
or 1 Bounded Context = small cluster of related services.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bounded Context = a bubble where one model of reality
is valid; outside the bubble, the same words mean
different things.

**One analogy:**
> The word "bank" has different meanings in different
> contexts: financial institution, river bank, memory
> bank. In each context, "bank" is clear and unambiguous.
> No one needs a universal definition of "bank" that
> covers all meanings. Bounded Context applies this
> principle: within the "Finance" context, Customer =
> account holder with credit score. Within the "Support"
> context, Customer = person with support cases. Both
> are valid, separate, and unambiguous within their
> respective context.

**One insight:**
The Bounded Context is both a model boundary and a team
boundary. Conway's Law: the system's architecture mirrors
the communication structure of the team. A Bounded Context
is owned by one team, one codebase, one database. When
you draw a Bounded Context map, you're also drawing the
team map. Service boundary = team boundary = model boundary.

---

### 🔩 First Principles Explanation

**CONTEXT MAP PATTERNS (how Bounded Contexts relate):**

```
PATTERN 1 - CUSTOMER-SUPPLIER:
  Upstream (supplier): defines the model
  Downstream (customer): consumes the model
  
  Payment Service (supplier) defines PaymentResult
  Order Service (customer) consumes PaymentResult
  
  Relationship: Order Service adapts to Payment Service's
  model OR uses an Anti-Corruption Layer to translate

PATTERN 2 - SHARED KERNEL:
  Two contexts share a small, agreed-upon model subset
  Both teams own the shared part
  Changes require consensus from both teams
  Use sparingly: creates coupling
  
  Example: shared "Money" value object (amount, currency)
  used by both Payment and Order contexts

PATTERN 3 - CONFORMIST:
  Downstream team simply adopts the upstream model
  No translation layer
  Used when: upstream model is acceptable as-is
  Risk: downstream polluted by upstream design decisions

PATTERN 4 - ANTI-CORRUPTION LAYER (ACL):
  Downstream creates a translation layer
  Upstream model does not leak into downstream
  Used when: upstream model is poor or external
  
  Example: translating a legacy ERP system's concept
  of "item" into your domain's concept of "product"

PATTERN 5 - OPEN HOST SERVICE:
  Upstream publishes a well-defined protocol (API)
  Multiple downstreams consume via this protocol
  Examples: REST API with OpenAPI spec, Kafka topics
  with Avro schemas

PATTERN 6 - PUBLISHED LANGUAGE:
  A well-documented shared language between contexts
  Often combined with Open Host Service
  Examples: JSON-LD, industry standard event schemas
  FHIR for healthcare, FIX protocol for finance
```

**FINDING BOUNDED CONTEXTS:**

```
SIGNALS THAT A BOUNDARY EXISTS:
1. Terminology shift: "Customer" in billing = account holder;
   "Customer" in CRM = sales lead
   Different words for same thing? Same word for
   different things? Context boundary is here.

2. Ownership change: "Sales team owns customer data;
   engineering team owns product data"
   Organisational boundary = context boundary

3. Lifecycle divergence: Order lifecycle (draft -> submitted
   -> processing -> shipped -> delivered) is independent
   of Payment lifecycle (pending -> processing -> completed)
   Different lifecycles -> different aggregates
   potentially in different contexts

4. Change frequency difference: Product catalog changes
   rarely (days); shopping cart changes every second.
   Different change rates suggest different contexts.

COMMON BOUNDED CONTEXTS IN E-COMMERCE:
  Catalog: products, categories, descriptions, pricing
  Cart: sessions, items, totals, promotions
  Order: placed orders, order lifecycle, fulfillment
  Payment: payment methods, transactions, refunds
  Inventory: stock levels, warehouses, reservations
  Shipping: carriers, shipments, tracking
  Customer: identity, preferences, history
  Notification: emails, SMS, push (pure supporting)
```

---

### 🧪 Thought Experiment

**"PRODUCT" IN THREE CONTEXTS:**

```
CATALOG CONTEXT:
  Product = {id, name, description, images,
             categories, attributes, specs}
  Invariants: must have name, at least one image
  Owner: Catalog team
  DB: Product catalog database (rich content)

INVENTORY CONTEXT:
  Product = {sku, stockLevel, warehouseLocations,
             reorderPoint, supplier}
  Invariants: stockLevel >= 0
  Owner: Warehouse team
  DB: Inventory database (operational)

ORDER CONTEXT:
  OrderItem = {productId, productName [snapshot],
               quantity, unitPrice [snapshot]}
  NOT a Product object - it's a snapshot at order time
  Invariants: price and name frozen at order placement
  Owner: Order team
  DB: Orders database (transactional)

CONCLUSION:
  Three contexts, three different models for "product".
  Order context doesn't store the full catalog data.
  It snapshots what it needs at order time.
  Catalog changes don't break existing orders.
  This is proper bounded context separation.
```

---

### 🧠 Mental Model / Analogy

> A Bounded Context is like a country. Within the country:
> laws apply, language is spoken, currency is used.
> Crossing the border: laws change, language may change,
> currency changes. Traveling between countries: you use
> a passport (API) and possibly a translator (ACL). No
> one expects French law to apply in Germany. No one
> expects the French definition of "ordinance" to mean
> the same as the German "Verordnung". Each country's
> legal model is coherent internally. Inter-country
> interaction uses formal treaties (contracts/APIs).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A Bounded Context is a section of the system where
everyone agrees on what the words mean. In the "Shipping"
section, Customer means the delivery recipient. In
"Billing", Customer means the account holder. Each
section has its own rules and its own data.

**Level 2 - How to use it (junior developer):**
In code: separate packages or modules per context.
Each context has its own entity classes with only the
fields that context needs. Communication between contexts:
via REST API calls or Kafka events, not by sharing the
same Java class or database table.

**Level 3 - How it works (mid-level engineer):**
In a Java codebase: each Bounded Context is a separate
Maven module (or Gradle subproject). The module defines
its own domain classes. To receive data from another
context: define a dedicated translation class (mapper)
or Anti-Corruption Layer. The test: can you deploy
the module independently without touching other modules?
If yes: proper context separation. If no: contexts
are coupled.

**Level 4 - Why it was designed this way (senior/staff):**
Bounded Contexts solve the fundamental challenge of
large-team software development: Conway's Law. The
architecture will reflect the communication structure
of the team. If 5 teams all share one domain model:
five teams are in constant coordination. If each team
owns one bounded context: they are independent. The
bounded context is the technical enablement of team
autonomomy. Without it, microservices is an illusion.

**Level 5 - Mastery (distinguished engineer):**
Bounded Context sizing is the hardest design decision.
Too large: context contains multiple business capabilities,
still coupled. Too small: services are chatty, a single
business operation requires synchronous calls across
5 services. The "right" size: a context that maps to
one autonomous business capability, owned by one team,
deployable independently. Rules of thumb: can a 5-person
team fully own and understand the context? Can a business
operation complete within the context without requiring
synchronous calls to other contexts? If yes to both:
probably the right size.

---

### ⚙️ How It Works (Mechanism)

**INTER-CONTEXT COMMUNICATION PATTERNS:**

```java
// ORDER CONTEXT: receives data from CATALOG context
// Uses a snapshot (not a reference) - context isolation

@Entity
public class OrderItem {
    private UUID productId;        // ID reference only
    private String productName;    // snapshot at order time
    private BigDecimal unitPrice;  // snapshot at order time
    // NOT a reference to the Catalog's Product entity
    // Catalog can change product name/price freely;
    // existing orders are unaffected
}

// ANTI-CORRUPTION LAYER: translate shipping carrier
// model into our domain model
public class ShippingCarrierACL {

    private final UPSClient upsClient;  // external model

    // Translate UPS's "tracking_id" to our ShipmentId
    // Translate UPS's "delivery_status" to our ShipmentStatus
    public Shipment getShipmentStatus(ShipmentId shipmentId) {
        // UPS model: {tracking_id, current_status_code,
        //             location_code, eta_timestamp}
        UPSTrackingResponse upsResponse =
            upsClient.track(shipmentId.getValue());

        // Translate to our domain model
        return Shipment.builder()
            .id(shipmentId)
            .status(translateStatus(upsResponse.getStatusCode()))
            .location(upsResponse.getLocationCode())
            .estimatedDelivery(
                Instant.ofEpochSecond(upsResponse.getEta()))
            .build();
        // UPS model never leaks into our shipping domain
    }

    private ShipmentStatus translateStatus(
            String upsStatusCode) {
        return switch (upsStatusCode) {
            case "X" -> ShipmentStatus.IN_TRANSIT;
            case "D" -> ShipmentStatus.DELIVERED;
            case "P" -> ShipmentStatus.PICKUP;
            default -> ShipmentStatus.UNKNOWN;
        };
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CONTEXT MAP EVOLUTION:**

```
PHASE 1: Identify Bounded Contexts
  Event Storming output: 6 contexts identified
  Context Map: draw relationships
  
    Catalog --[OHS]--> Order
    Order --[C-S]--> Payment (Order is customer)
    Order --[C-S]--> Inventory (Order is customer)
    Order --[OHS]--> Shipping
    Shipping --[ACL]--> Carrier (external)
    Identity --[OHS]--> all contexts (authentication)

PHASE 2: Technical Boundaries
  Each context gets:
  - Its own codebase (Git repo or module)
  - Its own database (schema or server)
  - Its own API contract (OpenAPI spec)
  - Its own team ownership

PHASE 3: Integration
  Synchronous: REST API calls for real-time data
  Asynchronous: Kafka events for state synchronisation
  
  Example: OrderPlaced event (from Order context)
    -> Payment context: create PaymentRequest
    -> Inventory context: reserve stock
    -> Notification context: send confirmation email
  
  Order context does not know about Payment, Inventory,
  Notification internals. It publishes the event.
  Others subscribe. Loose coupling.
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: shared model vs bounded contexts**

```java
// BAD: Shared Customer entity across all services
// All services import this from a shared library
public class Customer {
    // Identity context fields
    private Long id;
    private String username;
    private String passwordHash;  // security context!
    // CRM context fields
    private String salesStage;
    private String assignedRep;
    // Shipping context fields
    private Address defaultShippingAddress;
    // Billing context fields
    private String billingAddress;
    private String creditCardToken;
    // Support context fields
    private List<SupportCase> openCases;
    // 85 fields total
    // EVERY service coupled to ALL fields
    // Adding a field requires 10 teams to coordinate
}
```

```java
// GOOD: Each context defines its own Customer view

// In shipping-service:
public class DeliveryCustomer {
    private CustomerId customerId;  // reference to identity
    private String displayName;     // copied from identity
    private Address shippingAddress;
    private String contactPhone;
    // Only fields needed for shipping decisions
    // Shipping team owns this model completely
}

// In billing-service:
public class BillingAccount {
    private CustomerId customerId;
    private String billingName;
    private Address billingAddress;
    private String paymentMethodToken;  // PCI scope
    // Only fields needed for billing
    // Billing team owns this model completely
}

// In support-service:
public class SupportAccount {
    private CustomerId customerId;
    private String displayName;
    private List<SupportTicketId> openTickets;
    // Only what support team needs
}
// Each context is independently deployable
// Changes to BillingAccount don't affect Shipping team
```

---

### ⚖️ Comparison Table

| Context Map Pattern | Coupling | When to Use |
|---|---|---|
| **Shared Kernel** | High | Small shared value objects (Money), agreed by both teams |
| **Customer-Supplier** | Medium | Clear upstream-downstream with planned releases |
| **Conformist** | Medium-High | Upstream model is acceptable; no translation needed |
| **Anti-Corruption Layer** | Low | Upstream model is poor or external; protect your domain |
| **Open Host Service** | Low | One provider, many consumers; well-defined API |
| **Published Language** | Low | Industry standard schemas; maximum interoperability |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 1 microservice = 1 Bounded Context always | Usually yes, but a Bounded Context can span multiple closely related microservices (e.g., "Order" context might include order-service and order-query-service for CQRS). A microservice should NOT span multiple Bounded Contexts. |
| Bounded Contexts must have completely separate databases | In practice, different schemas in the same database server is a valid starting point. The key is: each context owns its schema exclusively. No other context reads or writes it directly. Full database server separation is the target, not a day-1 requirement. |
| Finding the right Bounded Context is a one-time decision | Bounded Context boundaries evolve as understanding of the domain deepens. Starting with fewer, larger contexts and splitting them as needed is a valid strategy. The cost of wrong boundaries: high coupling (merge contexts) or chatty services (merge or redesign). |

---

### 🚨 Failure Modes & Diagnosis

**Context boundary too large: "God service" problem**

**Symptom:**
Order Service has grown to 50,000 lines of code, 45 tables,
and 8 engineers. Every new feature touches Order Service.
All other services coordinate through Order Service.
The team calls it the "Order Monolith".

**Root Cause:**
The Order Bounded Context was defined too broadly:
it captured order placement, inventory reservation,
payment processing, shipping label generation, and
customer notification. These are 5 separate bounded
contexts (or at minimum, 5 aggregates that warrant
separate services).

**Diagnostic:**
```
Strategic DDD indicators for a context needing split:
1. More than one "core domain" within the context
   (e.g., Order Management AND Payment Processing)
2. Team size > 8 ("two-pizza team" rule)
3. Multiple teams editing the same codebase
4. Frequently changing subsystems coupled to stable ones
5. Different deployment frequencies within the context
   (payment processing needs daily deploy;
    order history can deploy monthly)

Refactoring approach:
1. Event Storming to identify natural sub-boundaries
2. Identify the Aggregate roots that could be independent
3. Extract new Bounded Context: start with new service
   getting events from old service (Strangler Fig)
4. Gradually migrate responsibility to new service
5. Old service becomes thin orchestrator, then retires
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Domain-Driven Design (DDD)` - Bounded Context is
  the primary Strategic DDD pattern
- `Service Decomposition` - Bounded Context is the DDD
  answer to the decomposition question
- `Ubiquitous Language` - the language that makes the
  boundary concrete

**Builds On This:**
- `Anti-Corruption Layer` - protection at context boundaries
- `Decomposition by Business Capability` - business
  capabilities map to bounded contexts
- `Decomposition by Subdomain` - subdomains provide
  another lens for finding contexts
- `Database per Service` - technical enforcement of
  bounded context data isolation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Boundary where a model is valid;         │
│              │ 1 context = 1 service (usually)          │
├──────────────┼───────────────────────────────────────────┤
│ SIGNALS      │ Same word, different meanings?          │
│              │ Different teams, different change rates? │
├──────────────┼───────────────────────────────────────────┤
│ INTEGRATION  │ APIs (sync) + Domain Events (async)      │
│              │ ACL for external/poor upstream models    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Clear boundary = each term has one      │
│              │  meaning; each context owns its data"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Aggregate → Anti-Corruption Layer        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Bounded Context = boundary where a domain model is
   valid; one team owns it, one codebase, one database.
2. Same word different meaning = context boundary.
   "Customer" in shipping ≠ "Customer" in billing.
3. Contexts integrate via APIs (sync) or Domain Events
   (async). Never via shared database tables.

**Interview one-liner:**
"Bounded Context is a DDD strategic pattern that defines
a boundary around a domain model. Within the boundary:
one team owns the model, one codebase, one database,
consistent ubiquitous language. Across boundaries: terms
may mean different things. In microservices: 1 Bounded
Context typically maps to 1 service. Contexts are
integrated via REST APIs or Kafka events, never via shared
databases. The Context Map documents the relationships
between contexts (Customer-Supplier, ACL, Conformist)."

---

### 💡 The Surprising Truth

The hardest part of Bounded Contexts is NOT technical
- it's organisational. A Bounded Context requires that
one team OWNS it fully: they make design decisions,
they set the API contract, they do not need approval
from other teams for internal changes. In many organisations,
the "ownership" is unclear, the "shared library" is
maintained by a committee, and the "common model" is
politically protected by whoever first created it.
Bounded Contexts are as much an organisational design
pattern as a technical one. Before trying to implement
Bounded Contexts technically: address the organisational
question of ownership. Who owns this context? Can they
make unilateral decisions about its internal model?
If the answer is "no, we need sign-off from 3 other
teams": the Bounded Context doesn't actually exist yet.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** Given a business domain description,
   identify the Bounded Contexts by finding terminology
   shifts, ownership changes, and lifecycle divergences.
2. **MAP** Draw a Context Map for a 5-service system,
   labelling each relationship with the appropriate
   Context Map pattern (ACL, Customer-Supplier, etc.).
3. **ENFORCE** Given a codebase where two contexts share
   a model, refactor to give each context its own model
   class with an explicit translation between them.
4. **DESIGN** Design the integration between two Bounded
   Contexts: choose between synchronous API call and
   asynchronous Domain Event, justify the choice.
5. **GOVERN** Define the ownership model for a Bounded
   Context: who can change the API? How are changes
   communicated? What is the contract management process?

---

### 🧠 Think About This Before We Continue

**Q1.** Your team is building a healthcare platform.
"Patient" is used in: Clinical (diagnosis, treatments,
medical history), Administrative (insurance, billing,
appointments), and Analytics (anonymised aggregate stats).
What are the Bounded Contexts? What does "Patient" mean
in each? How do the contexts integrate? Identify the
security implications of sharing patient data across
contexts.

**Q2.** You have two services that need to stay in sync:
order-service creates orders and inventory-service
reserves stock. Currently they share a database table.
Design the migration to proper Bounded Context isolation:
separate databases, event-based synchronisation. What
are the consistency trade-offs? How do you handle the
case where inventory reservation fails after order is
created?

**Q3.** The Bounded Context for "Pricing" has grown
to include: price catalogue management, promotional
discount rules, real-time competitor pricing, and
per-customer pricing. Is this one Bounded Context or
multiple? Apply the DDD signals (team ownership, change
frequency, terminology) to justify your answer.