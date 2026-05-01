---
layout: default
title: "Domain-Driven Design (DDD)"
parent: "Microservices"
nav_order: 629
permalink: /microservices/domain-driven-design/
number: "629"
category: Microservices
difficulty: ★★★
depends_on: "Monolith vs Microservices, Service Decomposition"
used_by: "Bounded Context, Aggregate, Ubiquitous Language, Anti-Corruption Layer, Event Sourcing in Microservices"
tags: #advanced, #architecture, #microservices, #pattern, #deep-dive
---

# 629 — Domain-Driven Design (DDD)

`#advanced` `#architecture` `#microservices` `#pattern` `#deep-dive`

⚡ TL;DR — **Domain-Driven Design (DDD)** is a software design approach where the model is shaped by the business domain. Its key tools are **Ubiquitous Language** (shared vocabulary), **Bounded Context** (service boundaries), and **Aggregates** (consistency boundaries within a domain). DDD is the primary intellectual foundation for microservices architecture.

| #629            | Category: Microservices                                                                                 | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Monolith vs Microservices, Service Decomposition                                                        |                 |
| **Used by:**    | Bounded Context, Aggregate, Ubiquitous Language, Anti-Corruption Layer, Event Sourcing in Microservices |                 |

---

### 📘 Textbook Definition

**Domain-Driven Design (DDD)**, introduced by Eric Evans in _Domain-Driven Design: Tackling Complexity in the Heart of Software_ (2003), is a design philosophy that centres the software model on the business domain and its rules — not the database schema, not the UI, not technical infrastructure. DDD is divided into **Strategic Design** (the high-level system structure) and **Tactical Design** (the implementation patterns within a bounded context). **Strategic DDD** concepts: Ubiquitous Language (shared business vocabulary between developers and domain experts), Bounded Context (an explicit boundary within which a specific domain model applies), Context Map (the relationships between bounded contexts), and Subdomain classification (Core, Supporting, Generic). **Tactical DDD** concepts: Entities (objects with identity), Value Objects (objects defined by their attributes), Aggregates (clusters of entities/value objects with a root entity as the consistency boundary), Domain Events (something that happened in the domain), Repositories (abstractions for retrieving aggregates), Domain Services (business logic not belonging to a single entity), and Application Services (orchestration, transactions).

---

### 🟢 Simple Definition (Easy)

DDD says: model your software to match how the business thinks and talks. Use the same words as the business uses. Group related concepts together. Define clear boundaries between different parts of the business. Let the business rules drive the code structure — not the other way around.

---

### 🔵 Simple Definition (Elaborated)

Traditional software design often starts from the database: design tables, then map them to code. DDD starts from the domain: talk to domain experts (the people who understand the business), discover their language and mental models, then build code that reflects those models directly. If the business calls something an "Order" that can be "Placed," "Confirmed," "Shipped," and "Delivered," the code should have an `Order` class with `place()`, `confirm()`, `ship()`, and `deliver()` methods — not a database table `ORDERS` with a `STATUS_CODE` column and a separate `OrderStatusUpdater` class. DDD's value is highest for complex domains where the business rules are intricate — it is overkill for simple CRUD applications.

---

### 🔩 First Principles Explanation

**DDD Building Blocks — a complete picture:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ STRATEGIC DDD                                                       │
│                                                                     │
│  Domain: the sphere of knowledge the software operates in          │
│  ├── Subdomain: a sub-area of the domain                           │
│  │     ├── Core Domain: competitive advantage, highest complexity  │
│  │     ├── Supporting Subdomain: needed, not differentiating       │
│  │     └── Generic Subdomain: commodity (Auth, Email, Billing)     │
│  │                                                                  │
│  Bounded Context: explicit boundary where a model applies          │
│  ├── Each BC has its own Ubiquitous Language                       │
│  ├── Each BC has its own domain model (same word = different thing)│
│  └── Context Map: relationships between BCs                        │
│        Partnership, Shared Kernel, Customer/Supplier,              │
│        Conformist, ACL, Open/Host Service, Published Language      │
│                                                                     │
│ TACTICAL DDD (within one Bounded Context)                          │
│                                                                     │
│  Entity: has unique identity (Order #123 persists over time)       │
│  Value Object: no identity, defined by attributes (Money $10 USD)  │
│  Aggregate: cluster of entities/VOs, one Aggregate Root            │
│  │           transactions and invariants within the root boundary  │
│  Domain Event: "OrderPlaced", "PaymentProcessed" — fact that happened│
│  Repository: interface to load/save Aggregates (not DB tables)     │
│  Domain Service: logic spanning multiple aggregates                │
│  Application Service: orchestration, transaction boundary, no DL   │
└─────────────────────────────────────────────────────────────────────┘
```

**The "same word, different context" problem — why Bounded Contexts matter:**

```
Word: "Customer"

In OrderContext:
  Customer = {orderId, shippingAddress, billingAddress, orderHistory}
  → Cares about: what did this customer buy? where to ship?

In MarketingContext:
  Customer = {emailAddress, preferences, campaignHistory, segments}
  → Cares about: what offers to send? what did they click?

In SupportContext:
  Customer = {ticketHistory, contactInfo, accountStatus, agentNotes}
  → Cares about: what issues has this customer raised?

WRONG: one shared "Customer" entity with all these fields (God Object)
  → Every context is coupled to every other context's concerns
  → OrderContext must load marketing data and support data for every order
  → Every addition to Customer affects all three contexts

RIGHT: separate Customer concept per Bounded Context
  → Customer IDs are shared (same person)
  → Models are separate (independent evolution)
  → Cross-context data exchange via Context Map integration patterns
```

**Tactical DDD — Aggregate design:**

```java
// Aggregate Root: Order — all access to order items goes through Order
// Invariant enforced: total quantity never exceeds stock limit
public class Order {  // Aggregate Root
    private OrderId id;
    private CustomerId customerId;
    private OrderStatus status;
    private List<OrderItem> items;      // entities within the aggregate
    private Money totalAmount;          // value object

    // Only the aggregate root can modify its children
    public void addItem(ProductId productId, Quantity qty, Money price) {
        if (status != OrderStatus.DRAFT) throw new InvalidOrderStateException();
        // Invariant: max 50 items per order
        if (items.size() >= 50) throw new OrderItemLimitExceededException();
        items.add(new OrderItem(productId, qty, price));
        recalculateTotalAmount();
        registerEvent(new OrderItemAddedEvent(this.id, productId, qty));
    }

    public void place() {
        if (items.isEmpty()) throw new EmptyOrderException();
        this.status = OrderStatus.PLACED;
        registerEvent(new OrderPlacedEvent(this.id, this.customerId, this.totalAmount));
    }
    // No setters on items — only business method calls
}

// Value Object: Money — no identity, defined by value
public record Money(BigDecimal amount, Currency currency) {
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) throw new CurrencyMismatchException();
        return new Money(this.amount.add(other.amount), this.currency);
    }
}

// Repository: loads/saves entire Aggregate, not individual parts
public interface OrderRepository {
    Optional<Order> findById(OrderId id);
    void save(Order order); // saves the aggregate root AND all child entities
}
// NO: OrderItemRepository — never access aggregate children directly from outside
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT DDD:

What breaks without it:

1. Software model diverges from business model — developers and business experts speak different languages, leading to mistranslation, misunderstandings, and incorrect implementations.
2. Anemic domain model: entities have only getters/setters; all business logic is in service/procedure classes — business rules are scattered and invisible.
3. No shared language means every requirements meeting requires translation — increasing bugs from misunderstanding.
4. Without Bounded Contexts, one domain concept ("Customer," "Product," "Account") grows to satisfy all contexts simultaneously — becoming a bloated, tightly-coupled God Object.

WITH DDD:
→ Code reads like the business speaks — onboarding is faster, bugs from misunderstanding are fewer.
→ Business rules are encapsulated in domain objects — a bug in pricing logic is in the `PricingPolicy` class, not hidden in a transaction script.
→ Bounded Contexts define service boundaries cleanly — the primary intellectual tool for microservices decomposition.
→ Aggregates define transactional boundaries — one `@Transactional` per aggregate root operation.

---

### 🧠 Mental Model / Analogy

> DDD is like hiring a translation expert who learns to speak fluent "business language" and builds a living dictionary of that language directly into the code. When a business rule changes — "orders over $1000 get free shipping" — the change is in `ShippingPolicy.calculateCost(order)`, not scattered across 10 service classes. The dictionary (Ubiquitous Language) is the contract: if the business says "An order is confirmed when payment is authorised," the code should have `order.confirm()` that calls `paymentService.authorise()`. No translation layer, no interpretation errors.

"Translation expert" = the DDD practitioner bridging business and technical
"Living dictionary" = Ubiquitous Language (business terms as code names)
"Business rule in one place" = tactical DDD (Aggregate with business logic methods)
"Dictionary is the contract" = if business language changes, code changes to match

---

### ⚙️ How It Works (Mechanism)

**Event Storming — discovering domain events and aggregates:**

```
Event Storming Workshop (Big Picture):
  1. Write all DOMAIN EVENTS on orange stickies:
     [OrderPlaced] [PaymentProcessed] [ItemShipped] [OrderCancelled]
     [InventoryReserved] [CustomerRegistered] [ReviewSubmitted]

  2. Identify COMMANDS (what triggers each event) on blue stickies:
     [PlaceOrder] → [OrderPlaced]
     [ProcessPayment] → [PaymentProcessed]

  3. Identify AGGREGATES (what processes the command) on yellow stickies:
     [PlaceOrder] → Order → [OrderPlaced]
     [ProcessPayment] → Payment → [PaymentProcessed]

  4. Draw BOUNDARIES around clusters of events/aggregates:
     → Order context: Order, OrderItem, OrderPlaced, OrderCancelled
     → Payment context: Payment, PaymentProcessed, PaymentFailed
     → Inventory context: Stock, InventoryReserved, InventoryReleased

  5. Identify POLICY (when event X, do command Y):
     When [PaymentProcessed] → [ReserveInventory]
     → This is the integration between Payment and Inventory contexts

  Outputs: domain model, aggregate boundaries, context map, event flow
```

---

### 🔄 How It Connects (Mini-Map)

```
Domain-Driven Design (DDD)  ◄──── (you are here)
(the design philosophy)
        │
        ├── Ubiquitous Language → shared vocabulary, code reflects business terms
        ├── Bounded Context     → service boundary definition
        ├── Aggregate           → transactional consistency boundary within a service
        ├── Anti-Corruption Layer → context map integration pattern
        ├── Domain Events       → basis for Event-Driven Microservices and Event Sourcing
        └── Service Decomposition → DDD subdomains guide microservices splitting
```

---

### 💻 Code Example

**Domain Service — business logic spanning multiple aggregates:**

```java
// Domain Service: logic that doesn't belong to a single aggregate
// "Can this customer place an order?" spans Customer and Order aggregates
@DomainService  // not a Spring @Service — a domain concept
class OrderEligibilityService {

    private final CustomerRepository customerRepo;
    private final OrderRepository orderRepo;

    public boolean isEligibleToOrder(CustomerId customerId, Money orderTotal) {
        Customer customer = customerRepo.findById(customerId)
            .orElseThrow(() -> new CustomerNotFoundException(customerId));

        // Business rule: suspended customers cannot order
        if (customer.isSuspended()) return false;

        // Business rule: customers with 3+ unpaid orders cannot place new orders
        long unpaidOrders = orderRepo.countUnpaidByCustomer(customerId);
        if (unpaidOrders >= 3) return false;

        // Business rule: new customers (< 30 days) cannot order > $5000
        if (customer.isNew() && orderTotal.isGreaterThan(Money.of(5000, USD))) return false;

        return true;
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                             | Reality                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DDD is about technical patterns (Repositories, Aggregates, Value Objects) | The tactical patterns are tools; the strategic patterns (Bounded Contexts, Ubiquitous Language, Context Maps) are the heart of DDD. Applying tactical patterns without strategic design produces over-engineered CRUD applications                            |
| DDD always produces complex code — it's overkill for simple apps          | DDD's value scales with domain complexity. For a simple invoice CRUD app, DDD is overkill. For a complex trading system or insurance platform with hundreds of business rules, DDD pays enormous dividends. Apply where the domain is complex                 |
| DDD and microservices are the same thing                                  | DDD predates microservices by a decade. DDD is a design philosophy; microservices are a deployment architecture. DDD Bounded Contexts are the primary tool for finding microservices boundaries, but DDD can be applied within a monolith just as effectively |
| Ubiquitous Language means business people write code                      | Ubiquitous Language means developers adopt the business's vocabulary and use it in code — class names, method names, package names. Business people do not write code; they verify that the code's terminology matches their mental model                     |

---

### 🔥 Pitfalls in Production

**Anemic Domain Model — the most common DDD failure**

```java
// WRONG: Anemic Domain Model (DDD anti-pattern)
// Entity has no behaviour — just data
public class Order {
    private Long id;
    private String status;
    private List<OrderItem> items;
    // getters and setters ONLY — no business logic
}

// All logic scattered in service layer
public class OrderService {
    public void placeOrder(Order order) {
        if (order.getStatus().equals("DRAFT") && !order.getItems().isEmpty()) {
            order.setStatus("PLACED"); // mutating state directly
            // validation, domain events, invariants all in service class
        }
    }
}
// Problems: - Order cannot protect its own invariants
//           - Business rules scatter across many service classes
//           - Testing requires setting up large service objects

// CORRECT: Rich Domain Model
public class Order {
    public void place() {
        // Order protects its own invariants
        if (status != OrderStatus.DRAFT) throw new InvalidOrderStateException();
        if (items.isEmpty()) throw new EmptyOrderException();
        this.status = OrderStatus.PLACED;
        registerEvent(new OrderPlacedEvent(this.id));
    }
}
```

---

### 🔗 Related Keywords

- `Bounded Context` — the strategic DDD concept that defines service boundaries
- `Aggregate` — the tactical DDD concept that defines transaction boundaries
- `Ubiquitous Language` — the shared vocabulary between developers and domain experts
- `Anti-Corruption Layer` — the context map pattern for protecting a domain from external models
- `Event Sourcing in Microservices` — an advanced tactical DDD pattern using domain events as the source of truth

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGIC    │ Ubiquitous Language, Bounded Context,     │
│ DDD          │ Context Map, Subdomain classification     │
├──────────────┼───────────────────────────────────────────┤
│ TACTICAL     │ Entity, Value Object, Aggregate,          │
│ DDD          │ Domain Event, Repository, Domain Service  │
├──────────────┼───────────────────────────────────────────┤
│ APPLY WHEN   │ Complex domain with intricate rules       │
│ SKIP WHEN    │ Simple CRUD with no business rules        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Model the code to match how the          │
│              │  business thinks and speaks."            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Eric Evans distinguishes between the Domain Layer and Application Layer in DDD's layered architecture. The Domain Layer contains Aggregates, Value Objects, Domain Events, and Domain Services — and should have NO dependency on infrastructure (no Spring annotations, no JPA annotations, no database). The Application Layer orchestrates domain objects and manages transactions. Describe the architectural tension: in practice, JPA requires annotations (`@Entity`, `@Id`, `@Column`) on domain objects — this is an infrastructure concern in the domain layer. Describe the hexagonal architecture solution (Ports and Adapters) and how it resolves this tension: what is the "Port" (interface) and what is the "Adapter" (JPA implementation)?

**Q2.** An Aggregate's consistency boundary means a transaction should not span multiple aggregate roots. Given a checkout flow that must atomically: (1) mark the Order as confirmed, (2) process payment, and (3) reserve inventory — all three are separate aggregates. Describe the two approaches to handling this: (a) Saga pattern with compensating transactions and (b) process manager / choreography. For approach (a), what are the compensating transactions for each step if step 3 fails? And what is the "eventually consistent" window during which a customer could see an inconsistent state (order confirmed but inventory not yet reserved)?
