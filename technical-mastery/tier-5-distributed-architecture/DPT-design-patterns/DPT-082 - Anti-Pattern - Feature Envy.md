---
id: DPT-082
title: "Anti-Pattern: Feature Envy"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-074, DPT-081
used_by: []
related: DPT-074, DPT-081, DPT-083, DPT-063
tags:
  - anti-pattern
  - code-smell
  - intermediate
  - cohesion
  - refactoring
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 82
permalink: /technical-mastery/design-patterns/feature-envy/
---

⚡ TL;DR - Feature Envy is a code smell where a method
is more interested in the data of another class than
its own. A method that accesses many fields and methods
of another class should usually be moved to that class.
The method "envies" the other class's data.

| #82 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-074, DPT-081 | |
| **Used by:** | N/A | |
| **Related:** | DPT-074, DPT-081, DPT-083, DPT-063 | |

---

### 🔥 The Problem This Solves

**THE METHOD IN THE WRONG CLASS:**
An `OrderService` has a method `calculateOrderTotal(Order order)`:
```java
class OrderService {
    double calculateOrderTotal(Order order) {
        double subtotal = 0;
        for (OrderItem item : order.getItems()) {
            subtotal += item.getQuantity() * item.getUnitPrice();
        }
        double discount = 0;
        if (order.getCustomer().isLoyaltyMember()) {
            discount = subtotal * order.getCustomer()
                .getLoyaltyDiscount();
        }
        double tax = subtotal * order.getTaxRegion()
            .getTaxRate();
        return subtotal - discount + tax;
    }
}
```
This method accesses: `order.getItems()`, `item.getQuantity()`,
`item.getUnitPrice()`, `order.getCustomer()`,
`customer.isLoyaltyMember()`, `customer.getLoyaltyDiscount()`,
`order.getTaxRegion()`, `taxRegion.getTaxRate()`.

It touches 3 different classes' internals extensively.
But it lives in `OrderService`.

**THE CONSEQUENCE:**
The logic that knows most about `Order`, `OrderItem`,
`Customer`, and `TaxRegion` is not IN those classes.
When these classes change their internal structure:
`OrderService` must also change. The knowledge is
in the wrong place.

---

### 📘 Textbook Definition

**Feature Envy** (Martin Fowler, "Refactoring", 1999)
is a code smell:

> "A method that seems more interested in a class other
> than the one it actually is in. The most common focus
> of the envy is the data. Time and time again the method
> in question is accessing other object's fields."

**The key insight:**
A method that extensively uses another class's data
is a signal that the method BELONGS in that other class,
not in its current location.

**Why it matters:**
Encapsulation principle: data and the behavior that
operates on that data should be together. Feature Envy
is the violation of this principle - behavior and its
data are in different classes.

**Fowler's exception:**
"There are several elegant patterns that deliberately
violate [Feature Envy]. Strategy, Visitor, and
Self-Delegation use this technique. Those doing this
are deliberately putting the behavior somewhere that
is outside the main class, and they use delegation
deliberately. As a result, there isn't a problem."
Patterns that intentionally separate data from behavior
for extensibility are not Feature Envy violations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A method that uses another class's data more than its
own class's data belongs in that other class.

**One analogy:**
> An office assistant who constantly walks to the
> finance department to access their data and systems
> to perform calculations.
>
> They are "envying" the finance department's data.
> The work they do is financial work that belongs in
> the finance department.
>
> Solution: move the assistant to the finance department.
> The work happens where the data is.
>
> Feature Envy: the method is the assistant; the other
> class is the finance department. The fix: move the
> method closer to the data it actually uses.

---

### 🔩 First Principles Explanation

**ENCAPSULATION AND LOCALITY OF REFERENCE:**
Good OO design: behavior is co-located with the data
it operates on. An `Order` class should contain methods
that operate on order data. A method that operates
heavily on `Order` data but lives elsewhere violates
this locality principle.

**WHY FEATURE ENVY EMERGES:**
1. **Service class syndrome**: developers put all business
   logic in `*Service` classes (`OrderService`, `CustomerService`),
   treating domain classes as anemic data holders (see
   Anemic Domain Model). The service methods are Feature
   Envy because the logic belongs in the domain class.
2. **Fear of fat models**: reluctance to put logic in model
   classes (especially in MVC patterns where models
   are kept thin). Logic migrates to controllers/services.
3. **Incremental growth**: a small method in a service
   grows over time as requirements grow, accumulating
   more and more knowledge about another class.

**THE ANEMIC DOMAIN MODEL CONNECTION:**
Feature Envy is the CODE SMELL that manifests when
the Anemic Domain Model (anti-pattern) is applied:
domain objects have no behavior (just getters/setters),
and all behavior is in service classes that operate
on the domain objects. The service methods are, by
definition, Feature Envy violations.

---

### 🧪 Thought Experiment

**WHERE DOES ORDER TOTAL BELONG?**

Ask: "What object knows most about how an order total
is computed?"
- `OrderService`? It knows ABOUT orders but is not AN order.
- `Order`? It contains items, customer, tax region.
  All the data needed for total calculation is in Order.

Answer: `order.calculateTotal()` is the right home.
The method belongs in the class that OWNS the data.

Now: when `Order` changes (new discount field added),
the change is in one class. When `calculateTotal()`
logic changes, it is in the class that owns the data.

**BEFORE vs AFTER:**
```
BEFORE:
  OrderService.calculateTotal(Order) - accesses Order,
    Items, Customer, TaxRegion

AFTER:
  Order.calculateTotal() - accesses this.items,
    this.customer, this.taxRegion
  All data is in scope. No excessive reaching into other
    classes.
```

---

### 🧠 Mental Model / Analogy

> Feature Envy = "Long-Distance Relationship" code.
>
> A method in Class A is in a constant long-distance
> relationship with Class B's data. Every time A's method
> runs: it calls B repeatedly, crosses the conceptual
> boundary over and over.
>
> The fix: the method moves "closer" to B.
> It becomes a resident of B (or at least a neighbor).
>
> Good code has "locality of reference": behavior lives
> next to the data it operates on. Feature Envy breaks
> this locality. The fix restores it.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Detecting Feature Envy:**
Count the classes a method references. If a method:
- Calls methods on another object 3+ times
- Accesses fields from another object more than its own
- Uses more data from parameter objects than from `this`

...it is a candidate for Feature Envy.

**Level 2 - Refactoring choices:**
- **Move Method**: move the envious method to the class
  it is envying. Often the simplest fix.
- **Extract Method + Move**: if only PART of a method envies
  another class, extract that part first, then move.
- **Split between classes**: if a method envies 2 classes
  (A and B), split: half to A, half to B.

**Level 3 - Intentional Feature Envy (Patterns):**
Fowler's exception: Strategy and Visitor patterns
deliberately put behavior outside the class it operates on.
This is architecturally intentional (for OCP extensibility)
not accidental Feature Envy.
Recognizing the difference: accidental Feature Envy
has no design reason; the method is simply in the wrong
class. Intentional Feature Envy (Strategy, Visitor)
has a structural reason (extensibility without modification).

---

### ⚙️ How It Works (Mechanism)

```
Feature Envy Detection
┌─────────────────────────────────────────────────────────┐
│ Method: OrderService.calculateTotal(Order order)        │
│                                                         │
│ Object references count:                               │
│   this (OrderService) references: 0                    │
│   order references: 4 (getItems, getCustomer,          │
│                        getTaxRegion, ...)              │
│   customer references: 2 (isLoyaltyMember,            │
│                           getLoyaltyDiscount)          │
│   item references: 2 (getQuantity, getUnitPrice)       │
│   taxRegion references: 1 (getTaxRate)                 │
│                                                         │
│ VERDICT: This method uses Order's world more than      │
│          its own. STRONG Feature Envy signal.           │
│                                                         │
│ FIX: Move to Order.calculateTotal()                    │
│   order references: now this.items (own data)          │
│   No excessive external reaching.                      │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Feature Envy and refactoring:**

```java
// BAD: OrderService envies Order's data.

class OrderService {
    // This method accesses Order's fields more than OrderService's.
    double calculateShippingCost(Order order) {
        double weight = 0;
        for (OrderItem item : order.getItems()) {
            weight += item.getProduct().getWeight()
                * item.getQuantity();
        }
        Address dest = order.getDeliveryAddress();
        String zone = dest.getCountry().equals("US")
            ? "domestic"
            : "international";

        if (zone.equals("domestic")) {
            return weight * 0.50; // $0.50 per unit weight domestic
        } else {
            return weight * 2.00; // $2.00 per unit weight intl
        }
    }
    // This method:
    // - uses order.getItems() (Order data)
    // - uses item.getProduct().getWeight() (Item/Product data)
    // - uses order.getDeliveryAddress() (Order data)
    // - uses dest.getCountry() (Address data)
    // It BARELY uses OrderService's own state.
    // It HEAVILY accesses Order and its components.
}
```

```java
// GOOD: Shipping cost calculation moved to Order.

class Order {
    private final List<OrderItem> items;
    private final Address deliveryAddress;

    // Behavior co-located with the data it uses.
    double calculateShippingCost() {
        double weight = items.stream()
            .mapToDouble(i -> i.getProduct().getWeight()
                * i.getQuantity())
            .sum();

        boolean isDomestic =
            deliveryAddress.getCountry().equals("US");
        return isDomestic ? weight * 0.50 : weight * 2.00;
    }
}

class OrderService {
    // Now OrderService delegates to Order.
    // OrderService is no longer envying Order.
    double getShippingCost(Order order) {
        return order.calculateShippingCost(); // one line
    }
    // Or simply: callers call order.calculateShippingCost() directly.
}
```

**Example 2 - Recognizing intentional Feature Envy (Strategy):**

```java
// NOT Feature Envy: Strategy Pattern is intentional.
// The strategy is DESIGNED to be outside the class
// for OCP extensibility.

interface ShippingStrategy {
    // Strategy methods access Order data by design.
    // This is intentional separation for OCP.
    double calculate(Order order);
}

class DomesticShippingStrategy implements ShippingStrategy {
    public double calculate(Order order) {
        // Accesses Order data. But this is the STRATEGY PATTERN
        // - deliberate, for extensibility. Not accidental envy.
        return order.getTotalWeight() * 0.50;
    }
}

// The DIFFERENCE from accidental Feature Envy:
// DomesticShippingStrategy is designed to be separate from Order
// so that new shipping strategies can be added without modifying
// Order.
// Accidental Feature Envy: same code but in OrderService with no
// extensibility purpose - just "I put it here because it was
// convenient."
```

---

### ⚖️ Deciding Where Logic Belongs

| Question | Answer |
|---|---|
| Which class owns most of the data this method uses? | Move the method there |
| Does the method use data from 2 classes equally? | Split: extract into two methods, move each to its class |
| Is this a Strategy/Visitor/Command (intentional separation)? | Not Feature Envy. Leave it |
| Is this service layer logic that orchestrates multiple domain objects? | May be appropriate in a service (not all service methods are Feature Envy) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All logic in service classes is Feature Envy | Service classes legitimately orchestrate workflows involving multiple domain objects. Orchestration logic does not belong in any single domain class. Feature Envy is when a method operates primarily on ONE other class's data |
| Moving logic to domain classes always fixes Feature Envy | Sometimes the data access pattern is inherently cross-class (e.g., a report that aggregates data from many entities). These are better in a dedicated query/report class, not in any single entity |
| Feature Envy and Data Class are opposite problems | They are related but different. Data Class (anemic domain model) is a class with no behavior. Feature Envy is a method that belongs in a different class. A Data Class causes Feature Envy (logic about that class lives elsewhere) |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Method uses another class's data more   │
│              │ than its own. Belongs in that class.    │
├──────────────┼──────────────────────────────────────────┤
│ DETECTION    │ Count class references. Method that     │
│              │ calls another class 3+ times = suspect. │
├──────────────┼──────────────────────────────────────────┤
│ ROOT CAUSE   │ Anemic domain model. Logic in service;  │
│              │ data in model. Behavior/data separated. │
├──────────────┼──────────────────────────────────────────┤
│ FIX          │ Move Method to the class being "envied."│
│              │ Co-locate behavior with data.           │
├──────────────┼──────────────────────────────────────────┤
│ EXCEPTION    │ Strategy, Visitor, Command: intentional │
│              │ separation. Not Feature Envy.           │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-083: Circular Dependencies          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Feature Envy = method in the wrong class. The method
   extensively accesses another class's data. Signal:
   the method calls another object's methods 3+ times
   while barely using `this`. Fix: Move Method.
2. Root cause: Anemic Domain Model. When domain objects
   are pure data holders (no behavior), all behavior
   goes to service classes that must reach into the data
   objects extensively. The service methods are Feature Envy.
3. Exception: Strategy, Visitor, Command patterns are
   INTENTIONAL separation of behavior from data for
   extensibility. These are not Feature Envy. The distinction:
   intentional (architectural reason) vs accidental
   (just put it there without design intent).

