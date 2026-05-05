---
layout: default
title: "Domain Model"
parent: "Software Architecture Patterns"
nav_order: 736
permalink: /software-architecture/domain-model/
number: "0736"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Object-Oriented Design, Ubiquitous Language, Aggregate Root, Repository Pattern
used_by: Clean Architecture, Hexagonal Architecture, CQRS Pattern, Domain Events
related: Anemic Domain Model, Rich Domain Model, Domain Events, Bounded Context
tags:
  - architecture
  - ddd
  - pattern
  - deep-dive
  - advanced
---

# 736 — Domain Model

⚡ TL;DR — A Domain Model is an object-oriented representation of the business domain that encapsulates both data AND behavior, where objects enforce business rules and speak the language of the business.

---

### 📊 Entry Metadata

| #736            | Category: Software Architecture Patterns                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Object-Oriented Design, Ubiquitous Language, Aggregate Root, Repository Pattern |                 |
| **Used by:**    | Clean Architecture, Hexagonal Architecture, CQRS Pattern, Domain Events         |                 |
| **Related:**    | Anemic Domain Model, Rich Domain Model, Domain Events, Bounded Context          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
All business logic lives in service classes. Entities are plain data holders with getters and setters. A `ProductService` has a method `applyDiscount(Product product, BigDecimal pct)`. A `InventoryService` has a method `checkStock(Product product, int qty)`. The logic for whether a product can be discounted is scattered across three services. The rules for stock reservation are duplicated in two places. Nobody knows where the authoritative rule is.

**THE BREAKING POINT:**
As the system grows, the code becomes an unmaintainable mess of procedural scripts disguised as OO. Every new business rule requires hunting through multiple service classes. Bugs appear because the same business rule exists in multiple slightly different versions.

**THE INVENTION MOMENT:**
Eric Evans's Domain-Driven Design introduced the Domain Model as a central pattern: put behavior where the data is. A `Product` object should know whether it can be discounted. An `Inventory` object should know whether it has sufficient stock. The domain model is the shared mental model of the business, expressed as code.

---

### 📘 Textbook Definition

A Domain Model, as defined by Martin Fowler in "Patterns of Enterprise Application Architecture" and elaborated by Eric Evans in "Domain-Driven Design," is an object model of the domain that incorporates both behavior and data. Domain Model objects contain the domain logic (business rules, validations, computations) directly within the model, rather than delegating that logic to separate service classes. The Domain Model uses the vocabulary of the business domain — class names, method names, and property names reflect how domain experts describe the problem.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Objects that model the business: they hold both the data AND the rules that govern that data.

**One analogy:**

> A chess piece knows the rules of its own movement. A Knight knows it moves in an L-shape — you don't need a separate `MoveValidationService` to check if a Knight's move is legal. The rule is part of what a Knight is. A Domain Model applies the same idea to business objects: an `Invoice` knows whether it can be cancelled; an `Account` knows whether it has sufficient balance for a debit.

**One insight:**
The Domain Model is not about "where to put code" — it's about making the code read like the business. When a domain expert reads `order.ship()`, they understand it immediately. When they read `orderService.updateStatusToShippedAndGenerateShipmentAndDecrementInventory(order)`, they see a technical procedure, not a business concept.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Domain objects own their invariants — they reject invalid state through constructors, setters, or operation methods, never through external validators.
2. Domain language matches business language — class names, method names, and property names are vocabulary the business experts recognise.
3. Persistence is separate — domain objects have no knowledge of how they are stored; that is the Repository's concern.

**STRUCTURAL OVERVIEW:**

```
┌──────────────────────────────────────────────────────────┐
│                   DOMAIN MODEL STRUCTURE                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Order (Aggregate Root)                          │   │
│  │  - id: OrderId                                   │   │
│  │  - customer: CustomerId                          │   │
│  │  - items: List<OrderItem>                        │   │
│  │  - status: OrderStatus                           │   │
│  │  + addItem(product, qty)  ← BEHAVIOR             │   │
│  │  + cancel()               ← BEHAVIOR + RULE      │   │
│  │  + ship()                 ← BEHAVIOR + RULE      │   │
│  │  + calculateTotal()       ← COMPUTED VALUE       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  cancel() enforces:                                      │
│    if status == SHIPPED → throw CannotCancelException    │
│    if status == DELIVERED → throw CannotCancelException  │
│  The RULE lives in the domain object, not a service     │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Business rules live in one place (the domain object). Code reads like the business. Rules are tested through the domain object, not through service interactions. Changes to business rules require changing the domain object only.
**Cost:** More complex objects than plain data classes. Requires up-front modeling effort and close collaboration with domain experts. More difficult to map directly to database tables (impedance mismatch). Requires an ORM or custom mapping layer.

---

### 🧪 Thought Experiment

**THE TEST:**
Does this code express the business concept or the technical procedure?

```java
// Procedure-oriented (no domain model):
if (order.getStatus() == OrderStatus.PENDING ||
    order.getStatus() == OrderStatus.PROCESSING) {
    order.setStatus(OrderStatus.CANCELLED);
    for (OrderItem item : order.getItems()) {
        inventory.returnStock(item.getProductId(),
                              item.getQuantity());
    }
}
```

```java
// Domain model:
order.cancel();
// cancel() internally enforces the status rule
// and raises an OrderCancelledEvent
// The caller doesn't know HOW it's done
// — only that cancellation is requested
```

**THE INSIGHT:**
The domain model version allows the `Order` to decide whether it can be cancelled. The caller trusts the object to enforce its own rules. The procedural version requires the caller (a service) to know the rules — and if the service is wrong, the domain object can be put into an invalid state.

---

### 🧠 Mental Model / Analogy

> A domain expert describing their business would say: "An Order can only be cancelled if it hasn't shipped yet." They would not say: "A service checks the status field of an Order row in the database and updates it to CANCELLED if it's not SHIPPED." The Domain Model is the first description expressed as code, not the second.

- The domain expert's language → the code's language
- The business rule → the method's guard clause
- The operation name → the method name
- The business concept → the class name

Where this breaks down: the Domain Model is only as good as the domain understanding behind it. Poor domain modeling produces complex, hard-to-use objects that are worse than simple services.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
Objects that represent business concepts and enforce the rules of the business. An Order, an Account, a Customer — these objects know their own rules and you interact with them using business language.

**Level 2 — How to use it (junior developer):**
Create classes for your key business concepts. Put business logic methods on those classes. Reject invalid states in the constructor or operation methods. Name everything using terms from the business domain. Keep persistence logic out of domain objects.

**Level 3 — How it works (mid-level):**
The Domain Model works in coordination with other DDD patterns. Aggregates define transaction boundaries. Repositories load and save aggregates. Domain Events capture what happened. Value Objects represent descriptive concepts (Money, Address, DateRange). The Domain Model is the hub — all business logic flows through it.

**Level 4 — Why it was designed this way (senior/staff):**
The Domain Model solves the fundamental tension in OO design: code that is organised for technical reasons (data here, logic there) versus code organised for domain reasons (the Order object knows everything about orders). The key insight from Evans is that software complexity is managed by the quality of the domain model — a weak model leads to a big ball of mud regardless of the architecture pattern used. The Domain Model is not a layer or a package — it's a design philosophy applied throughout the codebase. At scale, Domain Models enable multiple teams to work in separate Bounded Contexts with their own models without coupling.

---

### ⚙️ How It Works (Mechanism)

**What makes a strong Domain Model:**

```
┌──────────────────────────────────────────────────────────┐
│              DOMAIN MODEL CHARACTERISTICS                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ✅ Encapsulates invariants                              │
│     Order.cancel() throws if status is SHIPPED          │
│                                                          │
│  ✅ Uses ubiquitous language                             │
│     order.ship()  NOT  orderService.updateStatus(       │
│                            order, "SHIPPED")             │
│                                                          │
│  ✅ Raises domain events                                 │
│     order.cancel() → raises OrderCancelledEvent         │
│                                                          │
│  ✅ Returns value objects, not primitives                │
│     order.calculateTotal() → Money (not BigDecimal)     │
│                                                          │
│  ✅ Persistence ignorant                                 │
│     No @Entity annotations in domain layer (clean arch) │
│     OR minimal ORM annotations (pragmatic approach)     │
│                                                          │
│  ❌ NO ANEMIC MODEL:                                     │
│     order.setStatus("SHIPPED")  ← bypass all rules      │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│         DOMAIN MODEL IN CLEAN ARCHITECTURE              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   HTTP Request                                           │
│       ↓                                                  │
│   Controller → UseCase/Command Handler                   │
│                    ↓                                     │
│              loads Aggregate via Repository              │
│                    ↓                                     │
│              ┌─────────────────┐                        │
│              │   Domain Model  │ ← Business rules here  │
│              │  aggregate.op() │                        │
│              └─────────────────┘                        │
│                    ↓                                     │
│              saves Aggregate via Repository              │
│              publishes Domain Events                     │
│                    ↓                                     │
│   HTTP Response                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Anemic model (anti-pattern — no behavior in domain):**

```java
// BAD — pure data object, all logic in service
public class Order {
    private OrderId id;
    private OrderStatus status;
    private List<OrderItem> items;
    // Only getters and setters — no behavior
    public void setStatus(OrderStatus s) { status = s; }
}

// All logic lives in service — procedural, scattered
public class OrderService {
    public void cancel(Order order) {
        if (order.getStatus() == SHIPPED) {
            throw new IllegalStateException("Cannot cancel");
        }
        order.setStatus(CANCELLED);  // bypass invariant!
    }
    public void ship(Order order) {
        if (order.getStatus() != PROCESSING) {
            throw new IllegalStateException("Not ready");
        }
        order.setStatus(SHIPPED);
    }
}
```

**Rich Domain Model (correct):**

```java
// GOOD — behavior and rules in the domain object
public class Order {
    private final OrderId id;
    private OrderStatus status;
    private final List<OrderItem> items = new ArrayList<>();
    private final List<DomainEvent> events = new ArrayList<>();

    // Factory method — ensures valid initial state
    public static Order place(CustomerId customer,
                               List<OrderItem> items) {
        if (items.isEmpty()) {
            throw new EmptyOrderException();
        }
        Order order = new Order(OrderId.generate(),
                                 customer, items);
        order.events.add(new OrderPlacedEvent(order.id));
        return order;
    }

    // Behavior with rule enforcement
    public void cancel() {
        if (status == SHIPPED || status == DELIVERED) {
            throw new CannotCancelShippedOrderException(id);
        }
        this.status = CANCELLED;
        this.events.add(new OrderCancelledEvent(id));
    }

    public void ship() {
        if (status != PROCESSING) {
            throw new InvalidOrderStateException(
                "Cannot ship order in status: " + status);
        }
        this.status = SHIPPED;
        this.events.add(new OrderShippedEvent(id));
    }

    public Money calculateTotal() {
        return items.stream()
            .map(OrderItem::subtotal)
            .reduce(Money.ZERO, Money::add);
    }

    public List<DomainEvent> domainEvents() {
        return Collections.unmodifiableList(events);
    }
}
```

---

### ⚖️ Comparison Table

| Pattern             | Business Logic Location | Object Behavior        | Complexity | Best For                          |
| ------------------- | ----------------------- | ---------------------- | ---------- | --------------------------------- |
| **Domain Model**    | In domain objects       | Rich                   | High       | Complex business rules, DDD       |
| Anemic Domain Model | In service classes      | None (getters/setters) | Low        | Simple CRUD, scripts              |
| Transaction Script  | In procedure scripts    | N/A                    | Low        | Simple operations per transaction |
| Active Record       | In the object + DB      | Moderate               | Moderate   | Simple ORM-based CRUD             |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                               |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Domain Model means JPA Entity                  | Domain Model is a design concept; JPA Entity is a persistence annotation — they can overlap but are separate concerns |
| Domain Model is only for DDD projects          | Any complex business domain benefits from a rich model; DDD provides the vocabulary and patterns for building it      |
| Domain Model makes testing harder              | A rich domain model is actually easier to test — pure business logic with no framework dependencies                   |
| Domain Models can't be used with microservices | Each microservice has its own Domain Model scoped to its Bounded Context                                              |

---

### 🚨 Failure Modes & Diagnosis

**Anemic Domain Model Creep**

**Symptom:** Domain objects are data containers only. All business logic is in service classes. Tests test services, not domain objects. Duplicate logic appears across services.

**Root Cause:** Developers familiar with procedural or script-based approaches default to services for everything. ORM pressure encourages plain bean objects.

**Fix:** Move business logic from services into the domain objects. Start with operations that modify state — those methods should always be on the domain object.

**Prevention:** Code review rule: If a service method checks a domain object's state and then calls a setter on it, that logic belongs in the domain object.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Object-Oriented Design` — Domain Model is a rich OO design
- `Ubiquitous Language` — the vocabulary used in domain model construction

**Builds On This:**

- `Aggregate Root` — the key pattern for managing domain object consistency
- `Domain Events` — domain objects raise events when significant things happen
- `Bounded Context` — the scope within which a domain model applies

**Alternatives:**

- `Anemic Domain Model` — simpler but leads to scattered logic
- `Transaction Script` — procedural approach without an object model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Objects with both data AND business logic │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Business rules live where the data lives  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex business rules and domain logic   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD apps; no business logic       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Richer model vs more up-front design work │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Objects that know their own rules"       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `Customer` domain object has a `purchaseHistory` collection that could contain thousands of items. Loading the entire history every time a Customer object is created would be prohibitively expensive. Yet the `Customer.calculateLifetimeValue()` method needs that data. How do you balance the "domain object owns its behavior" principle with the practical need to avoid loading gigabytes of data just to call one method?

**Q2.** Two Bounded Contexts both have an `Order` concept, but they model it differently — the `Shipping` context cares about delivery addresses and tracking, while the `Billing` context cares about payments and invoices. Should there be one shared `Order` domain model, or two? What are the implications of each choice?
