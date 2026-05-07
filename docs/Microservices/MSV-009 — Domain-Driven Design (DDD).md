---
layout: default
title: "Domain-Driven Design (DDD)"
parent: "Microservices"
nav_order: 9
permalink: /microservices/domain-driven-design/
number: "MSV-009"
category: Microservices
difficulty: ★★★
depends_on: Service Decomposition, Object-Oriented Programming, Software Architecture Patterns
used_by: Bounded Context, Aggregate, Ubiquitous Language, Anti-Corruption Layer
related: Event Sourcing, CQRS, Bounded Context
tags:
  - microservices
  - architecture
  - pattern
  - deep-dive
  - distributed
---

# MSV-009 — Domain-Driven Design (DDD)

⚡ TL;DR — DDD is an approach to software design that models complex business domains directly in code, using a shared language between developers and domain experts to build software that reflects the actual business.

| #629 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Decomposition, Object-Oriented Programming, Software Architecture Patterns | |
| **Used by:** | Bounded Context, Aggregate, Ubiquitous Language, Anti-Corruption Layer | |
| **Related:** | Event Sourcing, CQRS, Bounded Context | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A large insurance company has a software system built by developers who never spoke properly with the business experts. The developers called a concept a "Policy"; the underwriters call the same thing a "Cover." The claims team calls a "Policy" something entirely different — the settlement document. The codebase has a 500-line `Policy` class that tries to be all things. When the claims team asks for "the policy to be transferred," the development team builds the wrong thing because they modelled the word without understanding the context.

**THE BREAKING POINT:**
Business logic is scattered across the codebase in random utility classes. The database schema looks nothing like the business domain. Developers spend 60% of their time translating between business language and code language. Adding a simple feature takes weeks because no one fully understands what the code represents.

**THE INVENTION MOMENT:**
This is exactly why Eric Evans created Domain-Driven Design — to make the software model a first-class representation of the actual business domain, with a shared, unambiguous language that eliminates translation overhead.

---

### 📘 Textbook Definition

**Domain-Driven Design (DDD)** is a software development approach introduced by Eric Evans in his 2003 book of the same name. It centres on three pillars: (1) a **Ubiquitous Language** — a shared vocabulary rigorously used by both domain experts and developers; (2) **strategic design** — decomposing the domain into Bounded Contexts that isolate different subdomains; and (3) **tactical design** — modelling domain concepts using building blocks (Entities, Value Objects, Aggregates, Domain Events, Repositories, Services, Factories). DDD is most valuable for complex domains with rich business logic.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DDD means making your code speak the same language as your business — not translating between the two.

**One analogy:**
> Imagine architects designing a hospital wing by interviewing surgeons, nurses, and administrators — and then drawing blueprints using the exact same terms the staff uses (not engineering jargon). The floor plan becomes immediately readable to the medical team who will work there. DDD applied to software produces code that a knowledgeable business person can read and recognise.

**One insight:**
The most dangerous translation layer in software is the gap between what the business means and what the code represents. DDD collapses that gap by making the domain model the *language* of the codebase.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Complex business domains contain multiple sub-languages — the same word means different things in different contexts. Models must be context-specific.
2. Business rules are the intellectual core of a software system. Everything else is plumbing.
3. Code that accurately reflects the domain is easier to change when the domain changes.

**DERIVED DESIGN:**
Given Invariant 1, no single unified model of the entire business can be correct — it would have to resolve all ambiguities by degrading precision. DDD's answer is Bounded Contexts: each context has its own model and its own ubiquitous language, valid within that context only.

Given Invariant 2, domain logic belongs in domain objects, not in service classes or database queries. An `Order` entity should enforce its own invariants (e.g., "a confirmed order cannot have a quantity of zero"), not delegate them to an `OrderValidator` utility class.

**DDD BUILD-ING BLOCKS:**

| Building Block | Purpose | Example |
|---|---|---|
| Entity | Has identity, mutable state | `Order` with `orderId` |
| Value Object | No identity, immutable, describes attribute | `Money(100, USD)` |
| Aggregate | Cluster of entities/VOs with single root | `Order` + `OrderLines` |
| Domain Event | Something that happened in the domain | `OrderPlaced`, `PaymentFailed` |
| Repository | Persistence abstraction for aggregates | `OrderRepository` |
| Domain Service | Stateless operation spanning multiple objects | `PricingService` |
| Factory | Creates complex objects/aggregates | `OrderFactory` |

**THE TRADE-OFFS:**
**Gain:** Code that accurately models business intent, easier to maintain as business rules evolve, natural microservices boundaries via Bounded Contexts.
**Cost:** Steep learning curve, high upfront design investment, overkill for simple CRUD applications.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce company has "Product" in two teams' vocabularies. The Catalog team's "Product" has SKU, description, images, and categories. The Inventory team's "Product" has stock levels, warehouse locations, and reorder thresholds.

**WHAT HAPPENS WITHOUT DDD:**
One shared `Product` class is created with 40 fields, satisfying neither team perfectly. Catalog changes break inventory logic. A "product" database table has nullable columns that only make sense in one context. Searches for `product.stockLevel` appear in Catalog controllers (wrong model used in wrong context).

**WHAT HAPPENS WITH DDD:**
Two separate bounded contexts are defined:
- **Catalog Context** has `CatalogProduct` (SKU, description, images)
- **Inventory Context** has `InventoryItem` (SKU, quantity, warehouse)

Each has its own `ProductId` (or they share just the SKU as a correlation ID). Each team uses their model freely without worrying about the other. When the Inventory team adds a "hazardous materials" flag, it does not pollute the Catalog model.

**THE INSIGHT:**
A single unified model of a complex domain is almost always the wrong model for everyone. Explicit context boundaries with explicit translations between them are cleaner than a bloated universal model.

---

### 🧠 Mental Model / Analogy

> DDD is like a hospital with specialist departments. The word "patient" in Cardiology means one thing (a person's cardiac history). In Billing, "patient" means another thing (a billing account number and insurance details). The hospital doesn't create one mega-Patient record — it has a Cardiology record, a Billing record, and they share only a Patient ID to correlate. Each department has its own precise language.

- "Hospital department" → Bounded Context
- "Department's definition of 'patient'" → context-specific domain model
- "Shared Patient ID" → shared identifier or Context Map
- "Doctor's precise medical language" → Ubiquitous Language within the department

Where this analogy breaks down: unlike hospital departments that coordinate through paperwork, DDD contexts coordinate through domain events or explicit Anti-Corruption Layers — the integration is explicit and code-enforced.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
DDD is a way of writing software where the code uses the same words and concepts that the business uses — so developers and business experts can understand each other directly without a translator in the middle.

**Level 2 — How to use it (junior developer):**
Identify the business language for your feature. Use those exact terms as class names and method names. Keep business rules inside domain objects (not service layers). Use Value Objects for concepts that are defined by their value (e.g., Money, Address). Use Entities for things identified by an ID.

**Level 3 — How it works (mid-level engineer):**
Strategic DDD: map the domain using Event Storming workshops. Identify where the same word means different things — those are context boundaries. Define a Context Map showing how bounded contexts relate (Conformist, Customer-Supplier, Anti-Corruption Layer, Open Host Service). Tactical DDD: implement each context using Aggregates as the core consistency boundary. An Aggregate Root controls all mutations to the aggregate. External code only holds references to Aggregate Roots, never to internal entities directly.

**Level 4 — Why it was designed this way (senior/staff):**
Evans designed DDD after observing that most software failures are knowledge problems, not technical problems. The key insight from the book: "The heart of software is its ability to solve domain-related problems for its users." The technical patterns (Aggregate, Repository) exist to enforce invariants and manage complexity — but the *strategic* patterns (Bounded Context, Ubiquitous Language) are the most undervalued and most impactful. Without strategic DDD, tactical DDD is just OOP with new names. The Aggregate pattern exists because transactions should not span multiple aggregates — keeping aggregates small (ideally 1–3 entities) prevents lock contention and enables eventual consistency.

---

### ⚙️ How It Works (Mechanism)

**Strategic Design — Finding Bounded Contexts:**

```
┌─────────────────────────────────────────────┐
│     DDD Strategic Design Process            │
├─────────────────────────────────────────────┤
│ 1. Event Storming workshop                  │
│    — domain experts + devs at a whiteboard  │
│    — orange: Domain Event (past tense)      │
│    — purple: Command (intent)               │
│    — yellow: Actor (who)                    │
│    — blue: Policy (if X then Y)             │
├─────────────────────────────────────────────┤
│ 2. Identify linguistic boundaries           │
│    — where does the same word mean          │
│      different things?                      │
│    — those are Bounded Context borders      │
├─────────────────────────────────────────────┤
│ 3. Draw Context Map                         │
│    — how do contexts integrate?             │
│    — Upstream/Downstream relationships      │
│    — Integration patterns: ACL, OHS, CF     │
└─────────────────────────────────────────────┘
```

**Tactical Design — Aggregate Pattern:**

```java
// Aggregate Root: Order controls all modifications
public class Order {  // Aggregate Root
    private final OrderId id;
    private OrderStatus status;
    private final List<OrderLine> lines; // internal entity
    private Money total;

    // All mutations via methods — enforces invariants
    public void addLine(ProductId productId, int qty, Money price) {
        if (status != OrderStatus.DRAFT) {
            throw new OrderException("Cannot add to confirmed order");
        }
        lines.add(new OrderLine(productId, qty, price));
        recalculateTotal();
    }

    public void confirm() {
        if (lines.isEmpty()) {
            throw new OrderException("Cannot confirm empty order");
        }
        this.status = OrderStatus.CONFIRMED;
        // Publish domain event
        registerEvent(new OrderConfirmedEvent(this.id, this.total));
    }
    // External code never manipulates OrderLine directly
}
```

**Repository pattern (persistence abstraction):**

```java
// Repository: hides persistence from the domain model
public interface OrderRepository {
    Order findById(OrderId id);
    void save(Order order);
}

// Implementation can be JPA, JDBC, or in-memory for tests
@Repository
public class JpaOrderRepository implements OrderRepository {
    private final OrderJpaRepository jpaRepo;

    public Order findById(OrderId id) {
        return jpaRepo.findById(id.value())
            .map(OrderMapper::toDomain)
            .orElseThrow(() -> new OrderNotFoundException(id));
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
HTTP Request → Application Service (orchestrates) → Load Aggregate via Repository ← YOU ARE HERE → Invoke domain method (business rule enforced) → Aggregate emits Domain Event → Repository saves Aggregate → Event published to message bus → Other Bounded Contexts react

**FAILURE PATH:**
Aggregate invariant violated (e.g., adding line to confirmed order) → Domain Exception thrown → Application Service rolls back transaction → Error response returned → No event published → Domain stays consistent

**WHAT CHANGES AT SCALE:**
At high write volume, large aggregates (many entities per aggregate root) become contention hotspots — a single `Order` being modified by concurrent updates holds DB row locks. DDD's prescription is to keep aggregates small, use eventual consistency between aggregates, and use Domain Events to coordinate cross-aggregate workflows. At 1000x scale, the Value Object immutability pattern enables aggressive caching since Value Objects never change.

---

### 💻 Code Example

**Example 1 — BAD: Anemic domain model (domain logic leaked to service):**

```java
// BAD: Order is just a data bag — no behaviour
public class Order {
    public Long id;
    public String status;
    public List<OrderLine> lines;
    public BigDecimal total;
    // No methods — pure data
}

// BAD: All logic in service — violates DDD
@Service
public class OrderService {
    // Business rule "only draft orders can be added to"
    // is scattered across multiple services
    public void addLine(Long orderId, OrderLine line) {
        Order o = repo.findById(orderId);
        if (!"DRAFT".equals(o.status)) { // rule in wrong place
            throw new RuntimeException("Not draft");
        }
        o.lines.add(line); // direct field access
        o.total = recalculate(o.lines);
        repo.save(o);
    }
}
```

**Example 2 — GOOD: Rich domain model (rules inside aggregate):**

```java
// GOOD: business rules live inside the Aggregate
public class Order {
    private final OrderId id;
    private OrderStatus status = OrderStatus.DRAFT;
    private final List<OrderLine> lines = new ArrayList<>();

    public void addLine(ProductId product, Quantity qty, Money price) {
        // Invariant enforced here — not in service layer
        if (!status.isDraft()) {
            throw new OrderException(
                "Can only add lines to draft orders"
            );
        }
        lines.add(new OrderLine(product, qty, price));
    }

    public Money getTotal() {
        return lines.stream()
            .map(OrderLine::lineTotal)
            .reduce(Money.ZERO, Money::add);
    }
}
```

**Example 3 — Value Object (immutable, equality by value):**

```java
// Value Object: no ID, immutable, equality by attributes
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Negative money");
        }
        this.amount = amount;
        this.currency = currency;
    }

    public Money add(Money other) {
        if (!currency.equals(other.currency)) {
            throw new CurrencyMismatch();
        }
        return new Money(amount.add(other.amount), currency);
    }

    @Override
    public boolean equals(Object o) { /* compare by value */ }
}
```

**Example 4 — Domain Event for cross-context communication:**

```java
// Domain Event: immutable record of something that happened
public record OrderPlacedEvent(
    OrderId orderId,
    CustomerId customerId,
    Money total,
    Instant occurredAt
) implements DomainEvent {}

// Consumer in Notifications Bounded Context
@EventHandler
public class SendOrderConfirmationHandler {
    public void handle(OrderPlacedEvent event) {
        emailService.sendConfirmation(
            event.customerId(), event.orderId()
        );
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Complexity | Domain Fidelity | Team Scalability | Best For |
|---|---|---|---|---|
| **DDD (Strategic + Tactical)** | High | Very High | High | Complex domains, many teams |
| DDD (Tactical Only) | Medium | High | Medium | Clear domain, small team |
| Transaction Script | Low | Low | Low | Simple CRUD, small domain |
| Active Record | Low-Medium | Medium | Medium | Moderate complexity, rapid dev |
| CQRS + Event Sourcing | Very High | Highest | High | Audit-heavy, complex write/read needs |

How to choose: apply full DDD when business logic is genuinely complex, the domain has multiple subdomains with distinct languages, and teams need explicit boundaries. Do not apply DDD to CRUD-heavy applications — the investment exceeds the return.

---

### 🔁 Flow / Lifecycle

```
┌────────────────────────────────────────────────┐
│    Command Handling in a DDD Application       │
├────────────────────────────────────────────────┤
│ 1. HTTP Request → Command DTO created          │
│ 2. Application Service receives command        │
│ 3. Load Aggregate from Repository              │
│ 4. Call domain method on Aggregate Root        │
│    — invariants checked                        │
│    — state mutated                             │
│    — domain events registered                  │
│ 5. Repository saves Aggregate                  │
│ 6. Domain events published                     │
│ 7. HTTP Response returned                      │
│                                                │
│ On Error at step 4:                            │
│ — Domain Exception raised                      │
│ — No save, no event                            │
│ — 400/422 returned                             │
└────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DDD means using Aggregates, Entities, and Value Objects | That is tactical DDD. Strategic DDD (Bounded Contexts, Ubiquitous Language, Context Maps) is more important and frequently skipped |
| DDD is suitable for all applications | DDD is overkill for simple CRUD apps; its value scales with domain complexity — apply it where business logic is genuinely rich |
| One Bounded Context = One Microservice | Often true but not required. A context could span multiple services, or one service could host multiple contexts temporarily |
| Aggregates should be large to capture all related data | Aggregates should be as small as possible — only entities that must change together in a single transaction |
| DDD is about patterns and code structure | DDD is primarily about knowledge crunching with domain experts — the patterns are just implementation tools for capturing that knowledge |
| A Repository is just a DAO | A Repository is part of the domain model and returns fully-loaded domain objects (not DTOs or ORM entities). A DAO is an infrastructure concern |

---

### 🚨 Failure Modes & Diagnosis

**1. Anemic Domain Model**

**Symptom:** Domain classes are pure data holders (getters/setters only). All business logic is in `*Service` classes that are 1000+ lines long and reference each other circularly.

**Root Cause:** Developers used to transaction-script (scripted logic in service layers) failed to move business rules into domain objects. The classes look like they follow DDD naming but are shells.

**Diagnostic:**
```bash
# Check average method count per domain class
find src/main -name "*.java" | xargs grep -l "class.*Entity\|class.*Aggregate" | \
  xargs grep -c "public void\|public.*get\|public.*set" | \
  awk -F: '{if ($2 < 3) print $1 " may be anemic"}'
```

**Fix:**
```java
// BAD: rule in service
if (order.getStatus().equals("CANCELLED")) {
    throw new IllegalStateException();
}
order.setStatus("CONFIRMED");

// GOOD: rule in aggregate
order.confirm(); // Order.confirm() checks its own invariants
```

**Prevention:** Do not create setters on domain aggregates — expose only intent-revealing methods that enforce invariants.

**2. Bounded Context Bleed**

**Symptom:** The `Order` entity in the Orders context has a `customerEmailAddress` field just to send notifications — data that belongs to the Customers context.

**Root Cause:** Developers reached across bounded context boundaries to avoid an API call, bringing in concepts that belong to another context.

**Diagnostic:**
```bash
# Find cross-context field references
grep -rn "Customer\." src/orders/ --include="*.java" | \
  grep -v "CustomerId"  # CustomerId is shared key; other fields are violations
```

**Fix:** Remove the cross-context field. Add a Domain Event (`OrderPlaced`) with only the Order's own data. Let the Notifications context subscribe and look up customer contact details from its own context.

**Prevention:** Strictly define what data each bounded context owns; use shared identifiers (Customer ID) rather than shared entities.

**3. Large Aggregates Causing Lock Contention**

**Symptom:** High `update` latency on Orders during peak; database deadlocks visible in slow query logs.

**Root Cause:** The `Order` aggregate includes `Product` inventory data, `Customer` preferences, and `Discount` rules — locking all this data for every order update.

**Diagnostic:**
```bash
# PostgreSQL: find long-running locks
SELECT pid, query, wait_event_type, wait_event
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
  AND state = 'active';
```

**Fix:** Split the oversized aggregate. `Order` should contain only items directly owned by the order. Reference `Product` by ID only (not embed its entity). Use Domain Events for cross-aggregate coordination.

**Prevention:** Keep aggregates to 3–5 entities maximum; never embed entities from another aggregate (use IDs only).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Decomposition` — DDD's bounded contexts are the most rigorous framework for service decomposition decisions
- `Object-Oriented Programming` — tactical DDD building blocks are OOP concepts applied with explicit domain intent
- `Software Architecture Patterns` — DDD adds domain-layer structure to standard architecture layers

**Builds On This (learn these next):**
- `Bounded Context` — the key strategic DDD concept that defines context isolation and maps to service boundaries
- `Aggregate` — the tactical DDD pattern that manages consistency boundaries within a bounded context
- `Event Sourcing in Microservices` — naturally complements DDD by storing domain events as the source of truth

**Alternatives / Comparisons:**
- `Transaction Script` — simpler alternative for CRUD-heavy domains with little business logic
- `CQRS in Microservices` — a complementary pattern often applied with DDD to separate read and write models

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A design approach where code models the   │
│              │ business domain using shared language and  │
│              │ explicit context boundaries               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Code that doesn't reflect the business    │
│ SOLVES       │ becomes unmaintainable as the domain grows│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Strategic DDD (Bounded Contexts) matters  │
│              │ more than tactical DDD (Aggregates).      │
│              │ Most teams skip the important part        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Domain is complex with rich business logic │
│              │ and multiple subdomains with distinct      │
│              │ vocabularies                              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ CRUD app, simple domain, small team with  │
│              │ no domain experts to collaborate with     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ High domain fidelity vs steep learning    │
│              │ curve and upfront design cost             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Make the code speak the language of      │
│              │  the business — not the other way round." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Context → Aggregate →             │
│              │ Ubiquitous Language                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are designing a healthcare platform with three teams: Clinical (manages patient care plans), Billing (manages insurance claims), and Scheduling (manages appointments). The word "patient" appears in all three teams' code and means something slightly different in each. Design the Bounded Context strategy: what fields does each context's "patient" model contain, how do they share identity, and what happens when a patient's demographic data changes — who is the source of truth and how do the other contexts learn about the change?

**Q2.** A DDD practitioner insists that Aggregates should never span more than one database transaction and all cross-aggregate coordination should use eventual consistency via Domain Events. A senior developer pushes back: "Eventual consistency means we might charge a customer for an order we then can't fulfil." Trace the exact sequence of events in both the consistent and eventual-consistent models for this scenario, and identify the precise conditions under which eventual consistency is safe and when it is not.

