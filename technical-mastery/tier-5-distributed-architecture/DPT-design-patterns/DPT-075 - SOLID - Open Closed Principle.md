---
id: DPT-075
title: "SOLID: Open/Closed Principle"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-074
used_by: []
related: DPT-074, DPT-076, DPT-077, DPT-078, DPT-027
tags:
  - concept
  - solid
  - intermediate
  - open-closed
  - extensibility
  - software-design
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 75
permalink: /technical-mastery/design-patterns/ocp/
---

⚡ TL;DR - Software entities should be open for extension
but closed for modification: add new behavior by adding
new code (new implementations, new classes), not by
modifying existing, tested code.

| #75 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-074 | |
| **Used by:** | N/A | |
| **Related:** | DPT-074, DPT-076, DPT-077, DPT-078, DPT-027 | |

---

### 🔥 The Problem This Solves

**THE MODIFICATION CASCADE:**
Every time a new payment type is added to an e-commerce
system, the `PaymentProcessor` class is modified:
```
if (type == CREDIT_CARD) { ... }
else if (type == PAYPAL) { ... }
else if (type == CRYPTO) { ... }  // just added
```
Modifying tested, deployed, production code to add a
new payment type risks breaking the existing logic.
A bug in the new CRYPTO case could affect the CREDIT_CARD
case if the code paths share logic. Regression testing
is required for the entire payment processing flow.

**THE COST:**
Each new payment type requires: modifying existing code,
regression testing all existing types, risk of production
regression from the modification.

**THE OPEN/CLOSED SOLUTION:**
Add new behavior by adding NEW code (a new implementation
of the payment interface), never by modifying the existing
payment processor. The processor is "closed" to modification;
the type system is "open" to extension.

---

### 📘 Textbook Definition

The **Open/Closed Principle (OCP)** is the second SOLID
principle (Bertrand Meyer, 1988; popularized by Robert
C. Martin):

> "Software entities (classes, modules, functions, etc.)
> should be open for extension but closed for modification."

**Open for extension**: new behavior can be added.
**Closed for modification**: existing, working code is
not changed to add the new behavior.

**How OCP is achieved:**
- Through **abstraction** (interfaces, abstract classes):
  the abstraction is stable (closed); implementations
  extend the behavior.
- Through **composition** over inheritance: new behavior
  is composed (plugged in), not modified into.
- Through **Strategy Pattern** (DPT-027): the algorithm
  is extensible (new strategies can be added) without
  modifying the context.
- Through **data-driven extension**: configuration-driven
  behavior that adds cases without code changes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Add new behavior by adding new code, not by modifying
existing code. Abstractions are stable (closed); implementations
extend them (open).

**One analogy:**
> A power strip. "Closed for modification" - you don't
> rewire the power strip to add a new device.
> "Open for extension" - you plug a new device into the
> available socket. The power strip's design doesn't change.
> The available sockets are the "extension points."
>
> OCP design: identify where variation will occur (extension
> points, like sockets). Design them as abstractions.
> New behavior: implement the abstraction (plug in).
> Existing behavior: unchanged.

---

### 🔩 First Principles Explanation

**WHY "OPEN" AND "CLOSED" SEEMS PARADOXICAL:**
"Open" and "closed" at the same time sounds contradictory.
The resolution: they refer to different aspects:
- OPEN for EXTENSION (the behavior can be extended = new implementations)
- CLOSED for MODIFICATION (the implementation is not changed = stable code)

The key is ABSTRACTION: the abstraction (interface) is
the stable part (closed). Implementations of the abstraction
are the extensible part (open).

**THE EXTENSION POINT CONCEPT:**
OCP requires identifying, in advance, WHERE variation
is likely to occur in the design. These are "extension
points" - designed as abstractions that can be implemented
by new code.

Example extension points in payment processing:
- The payment type (credit card vs PayPal vs crypto)
- The tax calculation strategy (by region, by product type)
- The discount rule (loyalty, seasonal, coupon)

Each extension point becomes an interface. New variations
are new implementations.

**OCP AND THE STRATEGY PATTERN:**
Strategy Pattern (DPT-027) IS the implementation of OCP
for behavioral variation. The `Context` is closed to
modification; new strategies extend the behavior.
Similarly: Template Method (DPT-028) implements OCP
via inheritance (the template method is fixed; subclasses
extend the abstract steps).

---

### 🧪 Thought Experiment

**ADDING A NEW DISCOUNT TYPE:**

**WITHOUT OCP:**
```java
double applyDiscount(Order order, String discountType) {
    if (discountType.equals("LOYALTY")) { ... }
    else if (discountType.equals("SEASONAL")) { ... }
    else if (discountType.equals("COUPON")) { ... }
    // Adding FLASH_SALE: modify this method. Risk: regression.
}
```

**WITH OCP (Strategy Pattern for discounts):**
```java
interface DiscountStrategy {
    double apply(Order order);
}
class LoyaltyDiscount implements DiscountStrategy { ... }
class SeasonalDiscount implements DiscountStrategy { ... }
class CouponDiscount implements DiscountStrategy { ... }
// Adding FLASH_SALE: NEW class FlashSaleDiscount implements
// DiscountStrategy {}
// applyDiscount() method: UNCHANGED.
```

Adding FLASH_SALE: one new file. Zero modifications to
existing code. Zero regression risk to existing logic.
The existing discounts are unaffected (different classes).

---

### 🧠 Mental Model / Analogy

> OCP = the "plugin architecture" model.
> A text editor with a plugin system.
> "Closed for modification": you cannot edit the editor's
> source code (it is a compiled binary).
> "Open for extension": you can add plugins (syntax
> highlighting, autocomplete, file comparison).
>
> Plugins implement a stable plugin API (the abstraction).
> New plugins extend the editor's behavior without
> modifying the editor's source.
>
> Well-designed class systems work the same way. The
> stable core (closed) defines abstractions. New behavior
> (open) implements those abstractions as plugins.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Identifying OCP violation:**
Any `if/else` or `switch` that grows every time a new
variant is added is a potential OCP violation. Each
new case is a modification to tested code. The test:
"Can I add a new variant without modifying any existing code?"
If NO: OCP violation.

**Level 2 - Designing extension points:**
Extension points require upfront identification. The
discipline: when writing code, identify which behaviors
will vary. Extract those behaviors as interfaces/abstractions.
New behaviors will implement the interface.
Risk: identifying too many extension points leads to
over-engineering (DPT-072). Identify extension points
where variation is KNOWN, not speculative.

**Level 3 - OCP at architectural level:**
At the architecture level, OCP means: new business
requirements should be implemented by adding new services/
modules/functions, not by modifying existing ones.
A plugin system at the infrastructure level (like OSGi,
Eclipse's extension point system, or Apache's HttpModule)
implements OCP for entire modules. The Strangler Fig
Pattern (DPT-055) implements OCP at the migration level:
new behavior is added alongside old behavior without
modifying the old system.

---

### ⚙️ How It Works (Mechanism)

```
OCP Structure: Abstraction + Extension
┌─────────────────────────────────────────────────────────┐
│ CLOSED PART (stable - do not modify):                   │
│   PaymentProcessor → uses → PaymentStrategy (interface) │
│                                                         │
│ OPEN PART (extensible - add new code here):            │
│   CreditCardStrategy implements PaymentStrategy        │
│   PayPalStrategy implements PaymentStrategy            │
│   CryptoStrategy implements PaymentStrategy  ← NEW     │
│                                                         │
│ Adding CryptoStrategy:                                  │
│   + 1 new file (CryptoStrategy.java)                   │
│   0 changes to PaymentProcessor.java                   │
│   0 changes to CreditCardStrategy.java                 │
│   0 changes to PayPalStrategy.java                     │
│   0 regression risk for existing payment methods       │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - OCP violation and fix:**

```java
// BAD: Modifying existing code to add new behavior.
// Every new tax region: modify this method.

class TaxCalculator {
    double calculate(Order order, String region) {
        if (region.equals("US")) {
            return order.getTotal() * 0.08;
        } else if (region.equals("UK")) {
            return order.getTotal() * 0.20;
        } else if (region.equals("EU")) {  // just added
            return order.getTotal() * 0.21;
        }
        // Adding CANADA: modify this method. Risk regression.
        return 0;
    }
}
```

```java
// GOOD: Extension point (interface) + implementations.
// Adding new region: add new class, no modification.

interface TaxStrategy {
    double calculate(Order order);
}

class UsTaxStrategy implements TaxStrategy {
    public double calculate(Order order) {
        return order.getTotal() * 0.08;
    }
}
class UkTaxStrategy implements TaxStrategy {
    public double calculate(Order order) {
        return order.getTotal() * 0.20;
    }
}
// Adding Canada: NEW class, no modification to existing:
class CanadaTaxStrategy implements TaxStrategy {
    public double calculate(Order order) {
        return order.getTotal() * 0.15;
    }
}

class TaxCalculator {   // CLOSED: never modified again
    public double calculate(Order order, TaxStrategy strategy) {
        return strategy.calculate(order); // delegates
    }
}
```

---

### ⚖️ OCP vs YAGNI

| Concern | OCP | YAGNI |
|---|---|---|
| When to add extension point | When variation is KNOWN | Only when 2nd variant EXISTS |
| Risk of early abstraction | Over-engineering (unused interface) | Simple direct code until needed |
| Synthesis | OCP applies to KNOWN extension points; YAGNI prevents premature extension points |

The synthesis: do not add extension points speculatively
(YAGNI). When the second variant arrives: refactor to
extract the OCP abstraction (now it's justified by
known variation). From then on: the abstraction is closed;
all new variants are additions.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| OCP means never modifying existing code | OCP means new BEHAVIOR should not require modifying existing code. Bug fixes, refactoring, and performance improvements are modifications to existing code and do not violate OCP |
| OCP and YAGNI are contradictory | They are complementary. YAGNI: don't create extension points speculatively. OCP: once a 2nd variant exists, extract the abstraction so the 3rd (and beyond) can be added without modification. YAGNI first; OCP after the pattern is established |
| OCP requires inheritance | OCP can be achieved via interfaces + composition (Strategy Pattern - composition), or via inheritance (Template Method). Modern Java prefers composition over inheritance for OCP |
| A switch statement always violates OCP | A switch statement that changes when new variants are added violates OCP. A switch statement over a FIXED set of variants that will never change does not violate OCP. The question: "will this switch grow?" |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Open for extension (new code adds new   │
│              │ behavior); closed for modification      │
│              │ (existing code unchanged for new behavior│
├──────────────┼──────────────────────────────────────────┤
│ MECHANISM    │ Abstractions (interfaces) as extension   │
│              │ points. New behavior = new implementation│
├──────────────┼──────────────────────────────────────────┤
│ VIOLATION    │ Adding a new case requires modifying an │
│              │ existing if/else or switch              │
├──────────────┼──────────────────────────────────────────┤
│ PATTERNS     │ Strategy (behavioral OCP), Template     │
│              │ Method (structural OCP), Decorator      │
│              │ (behavioral extension without modificatio│
├──────────────┼──────────────────────────────────────────┤
│ YAGNI SYNC   │ Add extension points when 2nd variant   │
│              │ EXISTS, not speculatively               │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-076: SOLID - LSP                    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. OCP = new behavior via new code, not by modifying existing
   code. Extension points (interfaces) are the mechanism.
   New variants implement the interface. The interface
   and its callers are never modified.
2. OCP violation signal: every new variant requires
   modifying an existing `if/else` or `switch`. This
   is the "growing conditional" smell.
3. YAGNI and OCP work together: YAGNI says don't add
   extension points speculatively. OCP says once the
   second variant appears, extract the abstraction.
   The second variant justifies the OCP abstraction;
   YAGNI prevents doing it for the first variant.

