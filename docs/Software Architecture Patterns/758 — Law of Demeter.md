---
layout: default
title: "Law of Demeter"
parent: "Software Architecture Patterns"
nav_order: 758
permalink: /software-architecture/law-of-demeter/
number: "758"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "Cohesion and Coupling, SOLID Principles, Object-Oriented Programming"
used_by: "OOP design, Code review, Refactoring, Clean code"
tags: #intermediate, #architecture, #oop, #coupling, #clean-code
---

# 758 — Law of Demeter

`#intermediate` `#architecture` `#oop` `#coupling` `#clean-code`

⚡ TL;DR — The **Law of Demeter (LoD)** — "Don't talk to strangers" — states that an object should only call methods on itself, its fields, its parameters, and objects it creates — never on objects returned from method calls — preventing deep navigation chains that create tight coupling to internal structure.

| #758 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Cohesion and Coupling, SOLID Principles, Object-Oriented Programming | |
| **Used by:** | OOP design, Code review, Refactoring, Clean code | |

---

### 📘 Textbook Definition

**Law of Demeter** (Ian Holland, Northeastern University, 1987 — discovered during the "Demeter Project"): a design guideline for object-oriented software that states a method `M` of an object `O` should only invoke methods of: (1) `O` itself; (2) objects passed as parameters to `M`; (3) any objects created/instantiated within `M`; (4) direct component objects of `O` (fields). Informally: "only talk to your immediate friends." Violation: traversing a chain of method calls to reach a deeply nested object (`a.getB().getC().doSomething()`). This couples the caller to the internal structure of `a` AND `b`. If `B` ever stops containing `C`, the caller breaks. LoD is a specific form of the low-coupling principle: it limits coupling to STRUCTURAL knowledge of intermediate objects.

---

### 🟢 Simple Definition (Easy)

Ordering at a restaurant. You tell the waiter: "I'd like the salmon." The waiter coordinates with the kitchen, the chef, the supplier. You don't walk into the kitchen, find the chef, tell the chef to open the fridge, take out the salmon, and cook it. You talk to your immediate contact (the waiter). The internal structure of the restaurant (chef → fridge → salmon) is not your concern — and it can change without affecting your order.

---

### 🔵 Simple Definition (Elaborated)

`customer.getAddress().getCity().getPostalCode()` — this is a LoD violation. The caller knows: `Customer` has an `Address`; `Address` has a `City`; `City` has a `PostalCode`. If the customer's address model changes (Address is refactored to store city differently), the caller breaks. LoD fix: `customer.getPostalCode()` — Customer now encapsulates the navigation. Callers only know that Customer has a postal code. They don't know (or care) where Customer stores it internally.

---

### 🔩 First Principles Explanation

**LoD as a coupling discipline:**

```
THE PROBLEM LoD SOLVES:

  Each dot in a.getB().getC().doX() is a coupling point:
  
    a.getB()         — caller knows "a" contains something of type B
    .getC()          — caller knows B contains something of type C
    .doX()           — caller knows C has a method doX()
    
  THREE structural dependencies, not one.
  
  If B stops containing C (internal refactor): three callers break.
  If C moves its method: three callers break.
  If a decides to store B differently: three callers break.
  
  FORMAL LoD RULES:

    Method M in class C may call methods on:
    1. C itself (this.method())
    2. Objects passed to M as parameters (param.method())
    3. Objects created inside M (new Thing().method())
    4. Direct fields of C (this.field.method())
    5. [Some versions include]: returned objects from direct fields ONLY
    
    NOT ALLOWED:
    • Methods on objects RETURNED by any of the above (the "chain" problem):
      this.field.getSomething().doWork()  ← LoD violation
      
IDENTIFYING VIOLATIONS — "one dot" heuristic:

  EACH chained call BEYOND the first is a potential LoD violation.
  
  this.order.getCustomer().getAddress().getCity()
       ─────  ────────────  ──────────  ─────────
       field  returns Cust  returns Addr returns City
  
  Violations: .getAddress() (navigating into Customer's internals),
              .getCity() (navigating into Address's internals)
              
FIXING LoD VIOLATIONS:

  Strategy 1: DELEGATION — let the intermediate object navigate itself.
  
    BEFORE:
    String city = order.getCustomer().getAddress().getCity();
    
    AFTER:
    String city = order.getCustomerCity();  // Order delegates to Customer.getCity()
    
    class Order {
        String getCustomerCity() {
            return customer.getCity(); // Customer delegates to Address.getCity()
        }
    }
    class Customer {
        String getCity() {
            return address.getCity(); // Address has the data
        }
    }
    
    Now: each class navigates only its own immediate components.
    
  Strategy 2: TELL DON'T ASK — instead of getting data to compute elsewhere, tell the object to compute itself.
  
    BEFORE (ask + chain):
    double discount = customer.getAccount().getLoyaltyTier().getDiscountRate() * order.getTotal();
    
    AFTER (tell):
    double discount = customer.calculateDiscount(order.getTotal());
    // Customer asks its own Account, which asks its own LoyaltyTier.
    // Caller knows none of this internal structure.
    
  Strategy 3: INTRODUCE QUERY METHOD — when you need data from deep inside:
  
    BEFORE:
    boolean isPremium = user.getProfile().getMembership().getTier().equals(Tier.PREMIUM);
    
    AFTER:
    boolean isPremium = user.isPremiumMember();
    // Single, semantic query method. Internal structure irrelevant to caller.

LoD WITH BUILDERS AND FLUENT APIS:

  IMPORTANT EXCEPTION: Fluent builder APIs are NOT LoD violations.
  
  order.withCustomer(c).withItems(items).withShipping(addr).build()
  
  Each .with() returns the SAME builder object. No structural traversal.
  The builder is explicitly designed for chaining.
  
  Similarly, stream/reactive operations:
  list.stream().filter(x -> x.isActive()).map(x -> x.name()).toList()
  These operate on a single pipeline — stream → stream → stream → list.
  Not traversing foreign internal structure.
  
LoD IN MICROSERVICES:

  LoD applies to service calls too.
  
  VIOLATION: OrderService.getOrder(id).getCustomer().getAddress().getCity()
  (synchronous chain of service calls: Order → Customer → Address → Geo)
  
  If any intermediate service changes its response shape: cascade failure.
  
  FIX: OrderService returns a pre-composed DTO with all needed data,
       OR: query the necessary services independently and compose in the caller.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Law of Demeter:
- `a.getB().getC().doX()` — caller coupled to internal structure of 3 classes
- Refactoring `B`'s internals breaks all callers that navigated through it

WITH LoD:
→ Callers know only their immediate collaborators
→ Refactor internal structure: callers unaffected (they never saw the internals)

---

### 🧠 Mental Model / Analogy

> You want your neighbor's dog to fetch a ball. LoD: you ask your neighbor. Your neighbor tells their dog. The dog fetches. You don't need to know the neighbor has a dog, the dog responds to "fetch", or which yard the ball is in. Anti-LoD: you walk to your neighbor's house → open their door → find the dog → give the "fetch" command → walk to the yard → throw the ball. You now know: neighbor's house layout, they have a dog, dog understands "fetch", yard location. If neighbor gets a cat instead: you're lost.

"Asking your neighbor" = calling a method on your immediate collaborator
"Neighbor tells their dog" = delegation — intermediate object navigates its own internals
"You don't need to know they have a dog" = caller isolated from internal structure
"Walk through house → find dog → yard" = `a.getNeighbor().getDog().getFetch().getBall()`

---

### ⚙️ How It Works (Mechanism)

```
LOD COMPLIANCE CHECKLIST:

  For each method call in code:
  
  1. Am I calling a method on `this`? ✓ OK
  2. Am I calling a method on a parameter passed to this method? ✓ OK
  3. Am I calling a method on an object I created in this method? ✓ OK
  4. Am I calling a method on a direct field of this class? ✓ OK
  5. Am I calling a method on the RETURN VALUE of any of the above? ✗ VIOLATION
  
  Fix: introduce a delegation method on the intermediate object.
```

---

### 🔄 How It Connects (Mini-Map)

```
Coupling between objects (structural dependencies)
        │
        ▼ (limit coupling to immediate collaborators)
Law of Demeter ◄──── (you are here)
("Don't talk to strangers" — only immediate friends)
        │
        ├── Cohesion and Coupling: LoD is a specific coupling discipline (structural coupling)
        ├── Tell Don't Ask: closely related — tell objects to do work vs. extracting data
        ├── Command-Query Separation: related principle about method responsibilities
        └── Encapsulation (OOP): LoD enforces encapsulation by preventing external navigation
```

---

### 💻 Code Example

```java
// LAW OF DEMETER VIOLATION:
class OrderPricingService {
    double calculateShipping(Order order) {
        // Violates LoD — navigates 3 levels of internal structure:
        String countryCode = order.getCustomer()    // field of Order
                                  .getAddress()      // field of Customer (stranger!)
                                  .getCountry()      // field of Address (double stranger!)
                                  .getIso2Code();    // method on Country (triple!)
        
        return shippingRateTable.getRate(countryCode);
    }
}
// OrderPricingService is coupled to: Customer, Address, Country, iso2Code field.
// Rename Address.getCountry() → getDeliveryCountry(): THIS class breaks.

// ────────────────────────────────────────────────────────────────────

// LAW OF DEMETER COMPLIANT — delegation chain:
class OrderPricingService {
    double calculateShipping(Order order) {
        // Ask Order for what we need — single collaborator, single call:
        String countryCode = order.getCustomerCountryCode();
        return shippingRateTable.getRate(countryCode);
    }
}

class Order {
    // Order delegates to Customer:
    String getCustomerCountryCode() {
        return customer.getCountryCode();
    }
}

class Customer {
    // Customer delegates to Address:
    String getCountryCode() {
        return address.getCountryIso2();
    }
}

class Address {
    String getCountryIso2() { return country.getIso2Code(); }
}

// Now: internal structure refactors are contained.
// Address stores country as String instead of Country object?
// Only Address.getCountryIso2() changes. OrderPricingService: zero changes.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LoD means "one dot per line" | LoD is about structural traversal, not syntactic dots. `list.stream().filter().map().collect()` has 4 dots but no LoD violation — each operator transforms the same stream pipeline. `order.getCustomer().getAddress()` has 2 dots but IS a violation — traversing into foreign internal structure. Count structural traversals, not dots |
| LoD always improves design — always apply it | LoD can lead to "shotgun surgery" if over-applied: you add a delegation method to every intermediate class, bloating each class with pass-through methods. Use judgment: apply LoD when structural coupling is genuinely harmful. For simple data transfer objects (DTOs) in the outer layers of the application, dot-chaining may be acceptable |
| LoD is the same as Tell Don't Ask | Related but distinct. LoD: don't chain method calls through strangers (structural coupling concern). Tell Don't Ask: don't extract data from an object to make decisions externally; instead, tell the object to make the decision itself (behavior responsibility concern). A method can violate TDA without violating LoD (calling one method on a direct field, extracting data, computing externally) |

---

### 🔥 Pitfalls in Production

**Violation in service orchestration creating cascade coupling:**

```java
// ANTI-PATTERN: LoD violation across service calls:
class OrderFulfillmentService {
    void fulfill(OrderId orderId) {
        // Traverses three service calls to get warehouse address:
        Order order = orderService.getOrder(orderId);
        Warehouse warehouse = inventoryService
            .getWarehouse(order.getWarehouseId())    // call 1
            .getPreferredPicker()                    // returns Picker?
            .getAssignedWarehouse();                 // Another service call buried!
            
        // Problem: if InventoryService restructures Warehouse model:
        // OrderFulfillmentService breaks.
    }
}

// FIX: Fetch independently or let InventoryService return what you need:
class OrderFulfillmentService {
    void fulfill(OrderId orderId) {
        Order order = orderService.getOrder(orderId);
        // Ask InventoryService directly for the warehouse address — single call:
        WarehouseAddress warehouseAddr = inventoryService.getPickingAddress(order.getWarehouseId());
        shippingService.schedule(order, warehouseAddr);
    }
}
// InventoryService internally figures out Warehouse → Picker → Address.
// Callers see only getPickingAddress(). Internal reorganization: invisible.
```

---

### 🔗 Related Keywords

- `Cohesion and Coupling` — LoD is a specific coupling discipline (limits structural coupling)
- `Tell Don't Ask` — closely related: tell objects to compute vs. extracting their data
- `Encapsulation` — LoD enforces encapsulation: external code can't navigate internal structure
- `Command-Query Separation` — related principle separating state-changing from state-reading methods
- `Refactoring` — "Replace Method Chain" is a specific refactoring that fixes LoD violations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Only talk to your immediate friends.      │
│              │ Don't navigate through an object's        │
│              │ internals to reach a distant object.      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any time you write a.getB().getC().doX()  │
│              │ — stop and ask: should I add a delegate  │
│              │ method to A?                              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Fluent builder chains (same object);      │
│              │ stream pipelines; DTOs in outer layers    │
│              │ where structural access is intentional   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tell the waiter your order — don't walk  │
│              │  into the kitchen and tell the chef which │
│              │  shelf the salmon is on."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tell Don't Ask → Encapsulation →          │
│              │ Command-Query Separation → Refactoring    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `order.getCustomer().getAddress().getCity()` violates LoD. You add delegation methods: `Order.getCustomerCity()` → `Customer.getCity()` → `Address.getCity()`. This creates "pass-through" methods in Order and Customer that simply delegate without adding behavior. Some argue these delegation methods clutter the classes and are just as bad as the original chain. How do you evaluate this trade-off? When is the delegation method genuinely better, and when might the original chain be acceptable?

**Q2.** In a microservices architecture, Service A calls Service B to get an Order, then calls Service C with Order's customerId to get customer details. Is this a LoD violation? At what point does the Law of Demeter apply to service-to-service communication, and how is it different from applying it within a single service's classes? What pattern (API Gateway, BFF, data aggregation) addresses structural coupling in service-level interactions?
