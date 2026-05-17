---
id: MSV-031
title: Domain-Driven Design (DDD)
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-005, MSV-002, MSV-080
used_by: MSV-032, MSV-033, MSV-034, MSV-035, MSV-037, MSV-038
related: MSV-032, MSV-033, MSV-034, MSV-035, MSV-037, MSV-038, MSV-005, MSV-080
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
nav_order: 31
permalink: /microservices/domain-driven-design-ddd/
---

# MSV-031 - Domain-Driven Design (DDD)

⚡ TL;DR - Domain-Driven Design is a software design
approach that centers the architecture on the business
domain model, placing business language and rules at
the core of the design. In microservices: DDD provides
the vocabulary and tools to identify service boundaries
(Bounded Contexts), define what belongs inside a service
(Aggregates), and how services communicate (Domain Events,
Context Mapping). DDD is the most rigorous basis for
microservice decomposition.

| #031 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Decomposition, Microservices Architecture, Conway's Law in Microservices | |
| **Used by:** | Bounded Context, Aggregate, Ubiquitous Language, Anti-Corruption Layer, Decomposition by Business Capability, Decomposition by Subdomain | |
| **Related:** | Bounded Context, Aggregate, Ubiquitous Language, Anti-Corruption Layer, Decomposition by Business Capability, Decomposition by Subdomain, Service Decomposition, Conway's Law in Microservices | |

---

### 🔥 The Problem This Solves

**THE DATA MODEL ANTI-PATTERN:**
A team builds an e-commerce system. Database designer
creates a single `Customer` table with all customer
attributes (shipping address, payment method, loyalty
points, support tickets, preferences). Multiple services
share this table. The Shipping Service, Payment Service,
Marketing Service, and Support Service all read/write
the `Customer` table. Over time: every service is
coupled to every other service via this shared schema.
Changing the Customer table requires coordinating all
teams. This is the "distributed monolith" - microservices
that are actually more tightly coupled than a monolith.

**THE DDD SOLUTION:**
DDD recognises that "Customer" means different things
in different contexts. For Shipping: Customer = delivery
address + contact info. For Payment: Customer = billing
info + payment methods. For Marketing: Customer = segment
+ preferences. For Support: Customer = case history.
DDD names these different contexts (Bounded Contexts)
and makes them explicit. Each context owns its own data
model. No shared tables. Services communicate via
Domain Events, not shared databases.

---

### 📘 Textbook Definition

**Domain-Driven Design (DDD)** is an approach to software
development that focuses the design on the core domain
and domain logic, bases complex designs on a model of
the domain, and initiates a creative collaboration
between technical and domain experts to iteratively
refine the model. DDD provides two levels of tools:
**Strategic DDD** (for large-scale architecture): Bounded
Context, Context Map, Ubiquitous Language, and subdomains.
**Tactical DDD** (for within-service design): Entity,
Value Object, Aggregate, Domain Event, Repository,
Domain Service. In microservices: Strategic DDD provides
the service decomposition framework; Tactical DDD guides
the internal design of each service.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DDD says: model your software around how the business
works and thinks, using the same language the business
uses, and keep different parts of the business separate.

**One analogy:**
> A hospital has different departments: Emergency,
> Radiology, Cardiology, Billing. Each uses "patient"
differently. Emergency: patient = vital signs + triage.
> Billing: patient = insurance info + procedure codes.
> Radiology: patient = scan history + order. They don't
> share one single "master patient record" because each
> department's needs are different. DDD in software:
> each department's model is a Bounded Context. The
> hospital system = a collection of contexts, each
> with its own "patient" concept.

**One insight:**
DDD is not about database design or code patterns. It's
about language. When the business says "Order" and the
code says "Transaction" and the database says "SalesRecord" -
you have no common language. When bugs occur, the team
spends 30% of the time just translating between terms.
DDD's first discipline (Ubiquitous Language) eliminates
this translation: one term, used consistently by business,
developers, and code.

---

### 🔩 First Principles Explanation

**DDD BUILDING BLOCKS:**

```
STRATEGIC DDD (between services - architecture level):
───────────────────────────────────────

BOUNDED CONTEXT:
  A boundary within which a domain model is defined
  and applicable. The same term can mean different
  things in different contexts.
  Microservices mapping: 1 Bounded Context = 1 service
  (or a small cluster of closely related services).

UBIQUITOUS LANGUAGE:
  A shared language between domain experts and developers,
  used consistently in code, documents, and conversations.
  "Order" in the code matches "Order" in the business.

SUBDOMAIN:
  Core domain: the competitive advantage; invest heavily.
  Supporting domain: needed but not differentiating.
  Generic domain: commodity (use off-the-shelf).
  
  Example (e-commerce):
  Core: recommendation engine, pricing intelligence
  Supporting: order management, inventory
  Generic: payments (use Stripe), email (use SendGrid)

CONTEXT MAP:
  Diagram showing relationships between Bounded Contexts.
  Patterns: Customer-Supplier, Conformist, Anticorruption
  Layer, Shared Kernel, Partnership, Open Host Service.

TACTICAL DDD (within a service - code level):
───────────────────────────────────────

ENTITY:
  Object with identity that persists over time.
  Example: Order (OrderId=1001; order can change state
  but it's still the same order)

VALUE OBJECT:
  Object defined by its attributes, no identity.
  Example: Money(100, USD); Address("123 Main St", "NYC").
  Immutable; two Money(100, USD) are identical.

AGGREGATE:
  Cluster of entities + value objects with one root.
  All access through the root; consistency boundary.
  Example: Order (root) + OrderItems + ShippingAddress.
  Cannot update OrderItem directly - must go through Order.

DOMAIN EVENT:
  Something that happened in the domain; past tense.
  Example: OrderPlaced, PaymentProcessed, ItemShipped.
  Cross-context communication; triggers reactions.

REPOSITORY:
  Abstraction for aggregate persistence.
  OrderRepository.findById() / save(order).
  Hides database details from domain logic.

DOMAIN SERVICE:
  Business logic that doesn't belong to any entity.
  Example: PricingService.calculateDiscount(order, customer).
  Not an application service (no HTTP); pure domain.
```

---

### 🧪 Thought Experiment

**SHARED CUSTOMER MODEL ANTI-PATTERN vs DDD:**

```
ANTI-PATTERN (Shared Database):
  One Customer model, shared across all services:
  class Customer {
    id, name, email,            // identity
    shippingAddress,            // shipping
    billingAddress, creditCard, // payment
    loyaltyPoints, segment,     // marketing
    supportCases                // support
  }
  
  Problem: Every service coupled to every field.
  Shipping team wants to rename shippingAddress:
  -> Must coordinate with Payment, Marketing, Support.
  -> This is tight coupling disguised as microservices.

DDD APPROACH (Bounded Contexts):
  Shipping Context: 
    DeliveryCustomer { id, shippingAddress, contact }
  
  Payment Context:
    PaymentCustomer { id, billingAddress, paymentMethod }
  
  Marketing Context:
    MarketingProfile { customerId, segment, preferences }
  
  Support Context:
    SupportAccount { customerId, caseHistory }
  
  Result: Each context owns its data model.
  Shipping team changes DeliveryCustomer freely.
  No coupling between contexts.
  Cross-context: events (CustomerAddressUpdated)
  sync derived data between contexts.
```

---

### 🧠 Mental Model / Analogy

> DDD is like city planning. A city is divided into
> zones (residential, commercial, industrial) - Bounded
> Contexts. Within each zone, different rules apply
> (zoning laws = business rules). A "building" means
> different things in residential vs industrial zones.
> The city plan (Context Map) shows how zones relate.
> You don't design a "universal building type" that
> serves residential, commercial, and industrial needs;
> each zone has its own building types. DDD applies
> the same principle to software: each business context
> has its own models, its own rules, its own language.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
DDD says: design software using the same words and
structure that the business uses. If the business calls
it "Order", the code calls it "Order". Split the software
into sections that match how the business is organised
(shipping, billing, support) and keep them separate.

**Level 2 - How to use it (junior developer):**
In a Spring Boot project: (1) Identify the Bounded Context
(e.g., Order Management). (2) Create a package per
aggregate root. (3) Use Entities (have ID) vs Value
Objects (no ID, immutable). (4) Use the domain language
in class names. (5) Use a Repository interface for
persistence. (6) Raise Domain Events on state changes.

**Level 3 - How it works (mid-level engineer):**
Aggregate design rules: (1) reference other aggregates
by ID only, not by object reference. (2) Transactions
should not span aggregates. (3) Keep aggregates small.
Example: Order aggregate owns its OrderItems.
Customer is a separate aggregate - reference only by
customerId. If you need customer data in an order query:
it's a query (read model) concern, not a write model
concern. CQRS (Command Query Responsibility Segregation)
is the complement to DDD for read-heavy operations.

**Level 4 - Why it was designed this way (senior/staff):**
DDD's strategic patterns map directly to microservice
decomposition heuristics. Subdomain analysis: identify
core, supporting, and generic subdomains. Each subdomain
becomes a service (or small cluster). Core subdomain:
built in-house (competitive advantage). Generic: use
off-the-shelf (payments via Stripe, email via SendGrid).
Context Map: Customer-Supplier relationship between
contexts drives API design. Conformist: downstream team
adapts to upstream model. Anti-Corruption Layer: wrapper
that translates an external model to your domain model
(prevents "alien concepts" polluting your domain).

**Level 5 - Mastery (distinguished engineer):**
Event Storming (Alberto Brandolini) is the DDD discovery
technique: workshop where domain experts and developers
jointly model the domain using sticky notes.
Order: Domain Events (orange) -> Commands (blue) ->
Policies (purple) -> Aggregates (yellow). The output:
a context map, aggregate boundaries, domain events.
This is how well-designed microservice architectures
are born: the Event Storming output directly maps to
microservice boundaries and Kafka topic structures.
Without Event Storming (or equivalent), microservice
boundaries are guesses; with it, they reflect the
actual business process.

---

### ⚙️ How It Works (Mechanism)

**TACTICAL DDD IN SPRING BOOT:**

```java
// VALUE OBJECT: immutable, defined by attributes
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException(
                "Amount cannot be negative");
        }
        this.amount = amount;
        this.currency = currency;
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException(
                "Cannot add different currencies");
        }
        return new Money(this.amount.add(other.amount),
            this.currency);
    }
    // equals() and hashCode() based on amount + currency
}

// ENTITY: has identity (orderId)
@Entity
public class Order {
    @Id
    private OrderId orderId;
    private CustomerId customerId;  // ID reference, not object
    @OneToMany(cascade = CascadeType.ALL)
    private List<OrderItem> items = new ArrayList<>();
    private OrderStatus status;

    // Domain method with business rule
    public void addItem(ProductId productId,
            int qty, Money unitPrice) {
        if (this.status != OrderStatus.DRAFT) {
            throw new DomainException(
                "Can only add items to DRAFT orders");
        }
        this.items.add(new OrderItem(productId, qty, unitPrice));
        // Register domain event (Spring Data event)
        registerEvent(new ItemAddedToOrderEvent(
            this.orderId, productId, qty));
    }

    public void submit() {
        if (this.items.isEmpty()) {
            throw new DomainException("Order has no items");
        }
        this.status = OrderStatus.SUBMITTED;
        registerEvent(new OrderSubmittedEvent(this.orderId,
            this.customerId, this.total()));
    }
}

// REPOSITORY: abstraction over persistence
public interface OrderRepository {
    Order findById(OrderId id);
    void save(Order order);
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**EVENT STORMING -> MICROSERVICES MAPPING:**

```
Event Storming Output:

  [OrderPlaced] -> <ProcessPayment command>
              -> <Payment Service>
  
  [PaymentProcessed] -> <ReserveInventory command>
                    -> <Inventory Service>
  
  [InventoryReserved] -> <ShipOrder command>
                     -> <Shipping Service>

Bounded Context Identification:
  Order Context: Order, OrderItem, OrderStatus
  Payment Context: Payment, PaymentMethod, PaymentStatus  
  Inventory Context: Product, StockLevel, Reservation
  Shipping Context: Shipment, DeliveryAddress, Carrier

Microservices Mapping:
  Order Context -> order-service
  Payment Context -> payment-service
  Inventory Context -> inventory-service
  Shipping Context -> shipping-service

Context Map:
  order-service: Customer-Supplier with payment-service
    (order-service is customer; payment-service is supplier)
  payment-service: Open Host Service (well-defined API)
  shipping-service: Conformist to carrier APIs
    (or Anti-Corruption Layer if carrier API is poor)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: anemic domain model**

```java
// BAD: Anemic domain model - no business logic in entities
@Entity
public class Order {
    private Long id;
    private String status;    // just data
    private List<OrderItem> items;  // just data
    // getters/setters only - no behavior
}

@Service
public class OrderService {
    // ALL business logic scattered in service layer
    public void submitOrder(Long orderId) {
        Order order = orderRepo.findById(orderId);
        if (order.getItems().isEmpty())
            throw new RuntimeException("No items");
        // Business rules duplicated across services
        order.setStatus("SUBMITTED");  // no domain enforcement
    }
}
// Problem: business rules spread across service layer
// Problem: Order can be in any state without enforcement
// Problem: no domain language in code
```

```java
// GOOD: Rich domain model - behavior in entities
@Entity
public class Order {  // ENTITY with behavior
    private OrderId id;
    private OrderStatus status = OrderStatus.DRAFT;
    private List<OrderItem> items = new ArrayList<>();

    // Business method with embedded rule
    public void submit() {
        if (this.status != OrderStatus.DRAFT)
            throw new InvalidStateException(
                "Order " + id + " is not in DRAFT state");
        if (this.items.isEmpty())
            throw new InvalidStateException(
                "Cannot submit empty order");
        this.status = OrderStatus.SUBMITTED;
        // Raise domain event - other contexts react
        registerEvent(new OrderSubmittedEvent(this.id));
    }
    // Business rules enforced at the domain level
    // Ubiquitous Language: submit(), not setStatus()
}
```

---

### ⚖️ Comparison Table

| Concept | Strategic DDD | Tactical DDD |
|---|---|---|
| **Level** | Architecture (between services) | Code (within service) |
| **Key concepts** | Bounded Context, Ubiquitous Language, Context Map | Entity, Value Object, Aggregate, Domain Event |
| **Microservices use** | Service boundary identification | Internal service design |
| **Benefit** | Prevents shared-data coupling | Encapsulates business rules |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 1 microservice = 1 DDD entity | 1 microservice should correspond to 1 Bounded Context. A Bounded Context contains multiple entities, aggregates, and value objects. Mapping one entity to one service creates chatty, tightly coupled services. |
| DDD is too complex for small teams | Strategic DDD (just identify bounded contexts and use ubiquitous language) can be applied without any tactical DDD patterns. The benefit is immediate even with minimal investment. Tactical DDD (aggregates, domain events) is applied incrementally in the core domain. |
| Anemic domain model is fine if you have services | Anemic domain model + service layer = business rules scattered across services, duplicated, and inconsistently enforced. Rich domain model = business rules in one place (the aggregate), consistently enforced, testable without infrastructure. |

---

### 🚨 Failure Modes & Diagnosis

**Distributed monolith: microservices tightly coupled via shared database**

**Symptom:**
15 microservices but deployments still require coordinating
8 teams. A database schema change affects 6 services.
"Independent deployment" is a fiction - everything
deployable in order. New features require PR reviews
across 5 repositories.

**Root Cause:**
Services decomposed by technical layer (data service,
business service, API service) not by domain. Multiple
services share the same database tables. No Bounded
Contexts: every service has a direct foreign key
dependency on the "shared customer table".

**Diagnostic:**
```
Context map anti-pattern indicators:
1. Multiple services own the same database
2. Services communicate via shared database reads
3. "Entity ID" is shared across all services
4. A data change in one service requires schema changes
   propagated to multiple other services
5. Teams cannot deploy their service without coordinating
   with other teams

Refactoring path:
1. Identify true Bounded Contexts (Event Storming)
2. Give each context its own database
3. Replace shared-table reads with:
   a. API calls for synchronous data access
   b. Event-based sync for eventual consistency
4. Apply Anti-Corruption Layer at context boundaries
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Decomposition` - DDD provides the rigorous
  framework for doing service decomposition correctly
- `Microservices Architecture` - DDD answers "how do
  you find the right service boundaries?"
- `Conway's Law in Microservices` - team structure
  should align with bounded contexts

**Builds On This:**
- `Bounded Context` - the primary DDD concept for
  service boundary definition
- `Aggregate` - the DDD concept for consistency boundary
  within a service
- `Ubiquitous Language` - the shared vocabulary aspect
- `Anti-Corruption Layer` - protects domain model from
  external models
- `Decomposition by Business Capability` - DDD-informed
  decomposition approach
- `Decomposition by Subdomain` - maps DDD subdomains
  to microservices

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGIC    │ Bounded Context: service boundary        │
│ DDD          │ Ubiquitous Language: shared vocabulary   │
│              │ Context Map: between-service relations  │
├──────────────┼───────────────────────────────────────────┤
│ TACTICAL     │ Entity: has ID; Value Object: no ID     │
│ DDD          │ Aggregate: consistency boundary          │
│              │ Domain Event: cross-context communication│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Model software on business domains;     │
│              │  contexts = service boundaries"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Context → Aggregate → Ubiquitous │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Strategic DDD: Bounded Contexts = service boundaries.
   Each context owns its own data model. No shared tables.
2. Ubiquitous Language: use the business vocabulary in
   code. "Order.submit()" not "OrderService.setStatus(SUBMITTED)".
3. Tactical DDD: Aggregate = consistency boundary.
   Never update an aggregate across two services in one
   transaction; use Domain Events instead.

**Interview one-liner:**
"DDD provides Strategic and Tactical patterns for microservices.
Strategically: Bounded Context defines service boundaries
(each context owns its data, uses its own model). Ubiquitous
Language = code uses business terms. Tactically: Aggregate
is the consistency boundary (all changes go through the
aggregate root). Domain Events cross context boundaries
(OrderPlaced triggers PaymentService to process payment).
The Event Storming workshop is the practical technique
for discovering bounded contexts."

---

### 💡 The Surprising Truth

The most common DDD mistake is applying Tactical DDD
(Aggregates, Value Objects, Domain Events) without first
doing Strategic DDD (Bounded Contexts). Teams spend
months building beautifully crafted Aggregates... inside
a Bounded Context that's too large. When the context is
too large (contains multiple business capabilities), you
have a "big service" with the same coupling problems as
a monolith. Strategic DDD is the 20% that gives 80%
of the benefit. Start there: identify contexts, establish
ubiquitous language, draw the context map. Tactical DDD
patterns can be adopted incrementally. The service
boundary decision is permanent (or very expensive to
change); the internal code patterns are not.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **FACILITATE** Run a simplified Event Storming session
   for a new feature: identify domain events, commands,
   aggregates, and bounded contexts.
2. **MAP** Given a business description of an e-commerce
   system, identify the bounded contexts, draw a context
   map showing relationships (Customer-Supplier, ACL),
   and map to microservices.
3. **CODE** Implement a rich domain model with an Aggregate
   root, Value Objects, and Domain Events using Spring
   Data's `@DomainEvents` or explicit event publishing.
4. **DIAGNOSE** Given a "distributed monolith" with shared
   databases across services, identify the missing bounded
   context separation and design the migration path.
5. **EXPLAIN** Articulate the difference between an
   anemic domain model and a rich domain model, and
   describe the concrete benefits of the rich model in
   terms of maintainability and testability.

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing a new e-commerce platform.
"Customer" is used by: the checkout flow (shipping
address, payment method), the loyalty program (points,
tier), the customer support team (case history, agents),
and the analytics team (behaviour, segments). How do
you apply DDD to model Customer? How many Bounded
Contexts does this suggest? What is the Ubiquitous
Language for Customer in each context?

**Q2.** Your team has an Order Aggregate with 20 fields
and 15 methods. Changes to the Order aggregate are
becoming a bottleneck: every feature touches it, testing
is slow, and it's hard to understand. How does DDD
guidance on aggregate design (keep aggregates small)
apply here? What is the decomposition strategy?

**Q3.** Design the Domain Events for an e-commerce
checkout flow. For each event: name (past tense),
what triggered it, what data it carries, which Bounded
Contexts subscribe to it, and what they do when they
receive it. Verify that no synchronous cross-aggregate
transactions are needed.