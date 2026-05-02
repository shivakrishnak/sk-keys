---
layout: default
title: "Shared Kernel"
parent: "Software Architecture Patterns"
nav_order: 757
permalink: /software-architecture/shared-kernel/
number: "757"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Bounded Context, Context Map, Domain-Driven Design"
used_by: "DDD strategy, Multi-team projects, Shared domain libraries"
tags: #advanced, #architecture, #ddd, #strategy, #integration
---

# 757 — Shared Kernel

`#advanced` `#architecture` `#ddd` `#strategy` `#integration`

⚡ TL;DR — **Shared Kernel** is a DDD Context Map relationship where two bounded contexts explicitly share a small, jointly owned subset of the domain model — both teams must agree to any change, making it a coordination commitment, not an accident.

| #757            | Category: Software Architecture Patterns                   | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Context Map, Domain-Driven Design         |                 |
| **Used by:**    | DDD strategy, Multi-team projects, Shared domain libraries |                 |

---

### 📘 Textbook Definition

**Shared Kernel** (Eric Evans, "Domain-Driven Design," 2003): a Context Map pattern in which two bounded contexts designate a subset of the domain model that both use and both own jointly. The shared portion is explicitly bounded, explicitly agreed upon, and explicitly maintained together. Neither team can change the shared kernel unilaterally. The shared kernel typically includes: value objects shared across contexts (`Money`, `CustomerId`, `ProductId`), core domain events consumed by both, and fundamental business rules that are truly universal. Shared Kernel is a deliberate trade-off: it reduces duplication at the cost of coordination overhead and reduced team autonomy. Evans warns against expanding it too broadly — "shared kernel has a gravitational pull" that can collapse into a distributed monolith if undisciplined.

---

### 🟢 Simple Definition (Easy)

Two countries sharing a river. The river belongs to both — neither can dam or pollute it unilaterally. There is a joint committee for river decisions. Both countries benefit from the shared resource. But any change to the river requires both to agree. The river is small, defined, and explicitly managed. The rest of each country's territory: fully independent.

---

### 🔵 Simple Definition (Elaborated)

Order context and Billing context both use `Money` (amount + currency), `CustomerId`, and the `OrderPlacedEvent`. These are in the Shared Kernel: a separate library both teams depend on. The Order team cannot change `Money.add()` behavior without Billing team's agreement — because Billing's calculations depend on it. The Shared Kernel library has its own test suite, owned jointly. Everything OUTSIDE the kernel: each team's independent domain. Order has `CartItem`, `ShippingAddress` — Billing doesn't know these. Billing has `Invoice`, `TaxRule` — Order doesn't know these. The kernel is the intersection: small, explicitly bounded.

---

### 🔩 First Principles Explanation

**When to use Shared Kernel and when to avoid it:**

```
THE SHARED KERNEL CHOICE:

  Problem: Two bounded contexts need the same concept.

  Option 1: DUPLICATE
    Each context defines its own version.

    Order:   record OrderMoney(BigDecimal amount, String currency) {}
    Billing: record BillingMoney(BigDecimal amount, Currency currency) {}

    Result: inevitable divergence. Billing adds rounding logic. Order doesn't.
    Now they're different. Integration: conversion/mapping between the two.
    Sometimes this is fine (Separate Ways pattern — duplication is intentional).

  Option 2: SHARED KERNEL
    Extract to shared library, jointly owned.

    // shared-kernel library (separate artifact):
    public record Money(BigDecimal amount, Currency currency) {
        public Money add(Money other) { ... }
        public Money multiply(BigDecimal factor) { ... }
    }

    // Both Order and Billing depend on shared-kernel:
    // Order uses Money for order totals.
    // Billing uses Money for invoice amounts.
    // Same class, same semantics, same rounding rules.

    Result: guaranteed consistency. Cost: coordination for every change.

  Option 3: UPSTREAM OWNS IT (Customer/Supplier)
    One team owns the concept; the other consumes it.

    Billing team owns Money (they are the financial experts).
    Order team uses Billing's Money definition as a downstream consumer.

    This is C/S, not Shared Kernel. Better when one team is clearly the expert.

WHAT BELONGS IN SHARED KERNEL:

  GOOD candidates (truly universal, stable, changes rarely):
    - Value objects: Money, PhoneNumber, EmailAddress, PostalAddress
    - Entity identifiers: CustomerId, OrderId, ProductId
    - Core domain events consumed by multiple contexts: OrderPlacedEvent
    - Business invariants truly universal: "Money must have non-null currency"

  BAD candidates (should NOT be in shared kernel):
    - Business logic specific to one context (OrderDiscountCalculator)
    - Infrastructure (database access, HTTP clients)
    - Anything that changes frequently (violation triggers constant joint coordination)
    - Large aggregates (Order, Customer, Invoice)

  RULE: Shared Kernel = things both teams USE, not things one team OWNS.

SHARED KERNEL IN PRACTICE:

  Version management:
    Shared kernel = separate Maven artifact (jar), npm package, or NuGet.

    // Maven:
    <dependency>
        <groupId>com.company</groupId>
        <artifactId>shared-kernel</artifactId>
        <version>2.1.0</version>
    </dependency>

    Both Order and Billing depend on shared-kernel version.
    Upgrade: both teams test → both teams agree → release new shared-kernel version.

  Test ownership:
    shared-kernel has its own test suite.
    Both teams contribute tests.
    No team's CI pipeline should pass if shared-kernel tests fail.

  Governance:
    Joint review for any change to shared-kernel.
    No unilateral modifications.

SHARED KERNEL vs. COMMON/GENERIC SUBDOMAIN:

  Common/Generic subdomain: reusable, non-specific domain logic.
    Example: generic email service, generic audit log.
    Anyone can use it. Owned by a single team. Others are customers (C/S).

  Shared Kernel: DOMAIN-SPECIFIC concepts shared between specific bounded contexts.
    Example: Money shared between Order and Billing.
    JOINTLY owned by BOTH teams. Changes require coordination.

ANTI-PATTERN — ACCIDENTAL SHARED KERNEL:

  Many teams accidentally share too much:
    - A "core" package with hundreds of classes used by everything
    - A "common" module that grew to contain domain logic
    - A shared database schema (schema IS a de facto shared kernel)

  These are accidental shared kernels without the governance.
  Result: any change breaks something. Everyone scared to change core.
  Fix: either (a) explicitly govern it as Shared Kernel, or (b) split it —
  determine which context should own each concept.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Shared Kernel governance:

- Both contexts have `Money` defined differently — conversion bugs at every integration point
- "Core" module grows uncontrolled — everyone depends on it, nobody owns it, nobody can change it safely

WITH Shared Kernel:
→ Shared concepts explicitly bounded and jointly governed — consistent semantics everywhere they're used
→ Coordination commitment is visible: team knows changing `Money` requires joint decision

---

### 🧠 Mental Model / Analogy

> Two research labs sharing a particle accelerator. The accelerator is expensive and both labs benefit from it. Neither lab can modify it unilaterally — both must agree on any change to the accelerator's configuration (it affects both experiments). The rest of each lab: fully independent research, no coordination needed. The accelerator is small, defined, and explicitly shared. Keeping the shared resource small is key: if everything became shared accelerator equipment, neither lab could work independently.

"Particle accelerator" = shared kernel (small, expensive to duplicate, explicitly shared)
"Both labs must agree on changes" = joint ownership and coordination requirement
"Rest of each lab: independent" = each bounded context's own model, not shared
"Keep shared resource small" = don't let shared kernel grow beyond what's truly universal

---

### ⚙️ How It Works (Mechanism)

```
SHARED KERNEL STRUCTURE:

  shared-kernel/ (separate artifact, separate repository or module)
    ├── src/main/java/com/company/kernel/
    │   ├── Money.java              // jointly owned value object
    │   ├── CustomerId.java         // jointly owned identifier
    │   ├── ProductId.java
    │   └── events/
    │       └── OrderPlacedEvent.java  // event consumed by both contexts
    └── src/test/java/com/company/kernel/
        └── MoneyTest.java          // owned by both teams

  order-service/ depends on → shared-kernel:2.1.0
  billing-service/ depends on → shared-kernel:2.1.0

  CHANGE PROCESS:
    1. Team A needs to change Money.add() rounding behavior.
    2. Opens PR on shared-kernel repository.
    3. BOTH teams review and approve.
    4. shared-kernel:2.2.0 released.
    5. Both services update dependency.
    6. Both services' CI runs with new version.
    7. Both services deploy (coordinated release).
```

---

### 🔄 How It Connects (Mini-Map)

```
Multiple bounded contexts needing the same domain concept
        │
        ▼ (explicit joint ownership of shared subset)
Shared Kernel ◄──── (you are here)
(small, explicitly bounded, jointly owned domain model fragment)
        │
        ├── Context Map: Shared Kernel is one of the 7 Context Map relationship patterns
        ├── Bounded Context: Shared Kernel lives at the intersection of two bounded contexts
        ├── Anti-Corruption Layer: alternative to Shared Kernel (translate instead of share)
        └── Value Objects: typical Shared Kernel content (Money, Ids, shared events)
```

---

### 💻 Code Example

```java
// SHARED KERNEL (separate artifact: shared-kernel.jar):

// Money — jointly owned by Order and Billing teams:
public record Money(BigDecimal amount, Currency currency) {
    public Money {
        Objects.requireNonNull(amount, "amount required");
        Objects.requireNonNull(currency, "currency required");
        if (amount.compareTo(BigDecimal.ZERO) < 0)
            throw new IllegalArgumentException("Money cannot be negative");
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency))
            throw new CurrencyMismatchException(this.currency, other.currency);
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public static Money of(BigDecimal amount, Currency currency) {
        return new Money(amount, currency);
    }
}

// OrderPlacedEvent — consumed by both Order and Billing:
public record OrderPlacedEvent(
    OrderId orderId,
    CustomerId customerId,
    Money total,
    Instant occurredAt
) implements DomainEvent {}

// ────────────────────────────────────────────────────────────────────

// ORDER CONTEXT (uses shared kernel):
class OrderService {
    void placeOrder(Cart cart) {
        Money total = cart.calculateTotal(); // Uses shared-kernel Money
        Order order = Order.place(cart.customerId(), cart.items(), total);
        orderRepo.save(order);
        // Publishes shared-kernel event:
        eventBus.publish(new OrderPlacedEvent(order.id(), order.customerId(), total, Instant.now()));
    }
}

// BILLING CONTEXT (uses same shared kernel — Money/OrderPlacedEvent are the SAME classes):
class InvoiceService {
    @EventHandler
    void on(OrderPlacedEvent event) {
        // Uses same Money class — no conversion needed:
        Invoice invoice = Invoice.create(event.customerId(), event.total(), event.orderId());
        invoiceRepo.save(invoice);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shared Kernel is the same as a "common library"              | A common utility library (logging helpers, HTTP clients, serialization utils) is infrastructure — not domain model. Shared Kernel is a domain-level concept: specific business objects (Money, CustomerId) jointly owned by teams with domain responsibility. The critical difference: domain change governance. Common utility library: owned by platform team, no joint governance. Shared Kernel: owned jointly by domain teams |
| Shared Kernel reduces team autonomy, so it should be avoided | Shared Kernel is a deliberate trade-off. When the cost of duplication (maintaining two diverging Money implementations) exceeds the cost of coordination (joint review for changes), Shared Kernel wins. Evans's warning is about SCOPE: keep it small. A small, stable Shared Kernel (Money, identifiers) with low change frequency has minimal coordination overhead and high value                                              |
| Shared Kernel means shared database                          | A shared database is an ACCIDENTAL Shared Kernel — the worst kind, because: (1) it's not explicitly scoped, (2) the entire schema is implicitly shared, (3) there's no governance process. True Shared Kernel is deliberately small, explicitly defined, and governed. Shared databases should be refactored away; Shared Kernels are a legitimate pattern                                                                         |

---

### 🔥 Pitfalls in Production

**Shared kernel scope creep — growing into a distributed monolith:**

```java
// STARTS WELL: small shared kernel
shared-kernel v1.0:
    Money.java
    CustomerId.java
    OrderPlacedEvent.java

// 1 YEAR LATER: "just add this one thing..."
shared-kernel v4.7 (scope creep):
    Money.java
    CustomerId.java, OrderId.java, InvoiceId.java, ShipmentId.java, ...
    OrderPlacedEvent.java, OrderCancelledEvent.java, InvoiceCreatedEvent.java, ...
    DiscountPolicy.java  // ← ORDER-specific logic added here "for reuse"
    TaxCalculator.java   // ← BILLING-specific logic added here "for sharing"
    CustomerService.java // ← should be in Customer context, not kernel!
    AddressValidator.java
    ... (80+ classes)

// Result: every bounded context depends on the bloated shared kernel.
// Change anything in shared kernel: all 6 services must be tested and redeployed.
// This IS a distributed monolith via shared library coupling.

// FIX: governance discipline — reject any PR to shared kernel that adds:
// - Business logic specific to one context
// - Service classes (only value objects and events)
// - Anything that changes more than once per quarter
// Regularly audit: "does this class TRULY need to be shared?"
```

---

### 🔗 Related Keywords

- `Bounded Context` — Shared Kernel sits at the explicit intersection of two bounded contexts
- `Context Map` — Shared Kernel is one of the 7 Context Map relationship patterns
- `Anti-Corruption Layer` — alternative: instead of sharing the model, translate it at the boundary
- `Value Objects` — typical content of Shared Kernel (Money, Ids, enums, shared events)
- `Customer/Supplier` — alternative: one team owns it, the other is a downstream consumer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Small, explicitly bounded domain model   │
│              │ jointly owned by two teams. Neither can  │
│              │ change it without the other's agreement. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Two contexts truly share domain concepts  │
│              │ (Money, Ids); duplication cost > joint   │
│              │ coordination cost; concepts rarely change │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Concepts change frequently (coordination  │
│              │ overhead dominates); one team clearly     │
│              │ owns it (use C/S instead); scope tends   │
│              │ to grow (strict governance needed)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two labs sharing one particle accelerator│
│              │  — neither can reconfigure it alone, but │
│              │  both benefit from one shared resource."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Context Map → Anti-Corruption Layer →     │
│              │ Bounded Context → Customer/Supplier       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce platform has an Order context and a Promotions context. Both need to evaluate "is this customer eligible for the premium discount?" — the same business rule. Option A: Shared Kernel with a `DiscountEligibilityPolicy` class owned jointly. Option B: Duplicate the rule in both contexts (Separate Ways). Option C: Promotions context owns it (C/S — Order is downstream). Evaluate each option using the criteria: stability of the rule, who is the domain expert, change frequency, and coordination cost.

**Q2.** When does a Shared Kernel become a liability? Specifically: the shared kernel library has `Money` (stable, rarely changes) and `OrderStatus` (changes frequently — new statuses added every quarter as the business evolves). How do you handle the `OrderStatus` case? Should it stay in the shared kernel, be extracted to its own versioned schema (like Avro schema registry), or should each context define its own view of order status and translate at the boundary?
