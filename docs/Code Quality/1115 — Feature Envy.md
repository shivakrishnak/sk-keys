---
layout: default
title: "Feature Envy"
parent: "Code Quality"
nav_order: 1115
permalink: /code-quality/feature-envy/
number: "1115"
category: Code Quality
difficulty: ★★★
depends_on: Code Smell, Refactoring, SOLID Principles
used_by: Technical Debt, Refactoring, Code Review
related: God Class, Long Method, Code Smell, Shotgun Surgery
tags:
  - antipattern
  - advanced
  - bestpractice
  - deep-dive
---

# 1115 — Feature Envy

⚡ TL;DR — Feature envy is a code smell where a method is more interested in the data and behaviour of another class than its own, signalling that the method is in the wrong class.

| #1115 | Category: Code Quality | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Code Smell, Refactoring, SOLID Principles | |
| **Used by:** | Technical Debt, Refactoring, Code Review | |
| **Related:** | God Class, Long Method, Code Smell, Shotgun Surgery | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `DiscountCalculator` class has this method:
```java
public double calculate(Customer customer) {
    if (customer.getAccount().getLoyaltyYears() > 5 
        && customer.getAccount().getTotalSpend() > 10000
        && customer.getProfile().getMembershipTier()
                   .equals("GOLD")) {
        return 0.20;
    }
    return 0.05;
}
```
This method knows more about `Customer`, `Account`, and `Profile` than about `DiscountCalculator` itself. It operates entirely on Customer's data. The coupling is explicit: change the Customer domain model (rename `getLoyaltyYears()`, add a level to the tier hierarchy) and this method breaks. The DiscountCalculator must change every time the Customer model changes.

**THE BREAKING POINT:**
A method that operates on another class's data is tightly coupled to that class's internals. Every internal change to the data source class potentially breaks the envious method. This coupling spreads: if 5 methods in different classes all "envy" Customer's data, a Customer refactoring requires changes in 5 different places — Shotgun Surgery.

**THE INVENTION MOMENT:**
This is exactly why **Feature Envy** was named as a code smell: to identify methods that belong in a different class — the class whose data and behaviour they're actually working with.

---

### 📘 Textbook Definition

**Feature Envy** is a code smell (from Martin Fowler's "Refactoring") describing a method that accesses the data or calls the methods of another class more than its own. The name is a metaphor: the method "envies" the features of another class, wishing it were defined there instead. Feature Envy violates the principle of **Tell, Don't Ask**: rather than asking another object for data and computing on it externally, you should tell the object to compute the result itself. The presence of Feature Envy indicates a misplaced responsibility — the method's computation belongs in the class it most accesses. The primary refactoring: **Move Method** (move the envious method to the class it envies, possibly renamed). Related smells: **Inappropriate Intimacy** (mutual feature envy between two classes — both access each other's internals), **Message Chains** (sequential feature envy: `a.getB().getC().getD()`), **Middle Man** (a class that only delegates to another — the inverse of feature envy). Detection: methods that dereference another class's fields more than 5 times, or that call another class's methods 3× more than they call their own.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A method in class A that does most of its work using class B's data — it belongs in class B.

**One analogy:**
> Feature Envy is like a bookkeeper who does the CEO's strategic planning. The bookkeeper uses the CEO's contacts, reads the CEO's market analysis, and makes strategic recommendations. But the bookkeeper belongs in the accounting department. The strategic planning work belongs with the CEO. The bookkeeper is doing the CEO's job from the wrong desk — taking their data, doing their analysis, returning the result. The CEO (the class being envied) should do their own planning.

**One insight:**
Feature Envy is a violation of encapsulation: the envious method knows what should be private about another class. When you move the method to the class it envies, that knowledge becomes internal — and the boundary between classes becomes cleaner.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A method belongs in the class whose data it primarily operates on — data and behaviour should co-locate.
2. Accessing another class's data requires knowing about that class's internal structure. This creates coupling; coupling increases change cost.
3. The "Tell, Don't Ask" principle: objects should tell each other what to do, not ask for data to make decisions externally.

**DERIVED DESIGN:**
Since behaviour should be co-located with the data it operates on (information expert principle), a method that operates on another class's data should be moved to that class. This eliminates the coupling (the method no longer needs to access internals) and places the behaviour where it can be encapsulated.

**THE TRADE-OFFS:**
Gain: Better encapsulation; reduced coupling; the class being "envied" gains meaningful behaviour (it becomes a rich domain model); lower coupling means fewer classes change when the data class changes.
Cost: Moving methods between classes requires updating all callers; may require refactoring the envied class to accommodate the new method; may reveal deeper design problems (the data class has no behaviour — Anemic Domain Model).

---

### 🧪 Thought Experiment

**SETUP:**
`PricingEngine` class:
```java
class PricingEngine {
    public BigDecimal calculateFinalPrice(Order order) {
        BigDecimal base = order.getBasePrice();
        int qty = order.getItems().size();
        String tier = order.getCustomer()
                           .getAccount()
                           .getMembershipTier();
        boolean isPremium = order.getCustomer()
                                 .isPremiumMember();
        
        // All this logic operates on Order/Customer data
        if (isPremium && "GOLD".equals(tier)) {
            return base.multiply(new BigDecimal("0.80"));
        } else if (qty > 10) {
            return base.multiply(new BigDecimal("0.90"));
        }
        return base;
    }
}
```

**PROBLEM:**
`PricingEngine.calculateFinalPrice()` knows: `Order`'s price, item count, customer membership tier, and premium status. Four pieces of data from the `Order`/`Customer` domain. If Customer adds a `PLATINUM` tier, or Order changes how `isPremiumMember()` works, `PricingEngine` must be updated even though pricing lives in a separate domain.

**REFACTORED:**
```java
// Method moved to Order (where the data lives):
class Order {
    public BigDecimal calculateFinalPrice() {
        if (customer.isGoldPremiumMember()) {
            return basePrice.multiply(new BigDecimal("0.80"));
        } else if (items.size() > 10) {
            return basePrice.multiply(new BigDecimal("0.90"));
        }
        return basePrice;
    }
}
// Customer encapsulates its own tier logic:
class Customer {
    public boolean isGoldPremiumMember() {
        return isPremiumMember() 
               && "GOLD".equals(account.getMembershipTier());
    }
}
```

**THE INSIGHT:**
After moving, `Order` changed from an anemic data container to a rich domain object. `Customer` encapsulates its own tier logic. `PricingEngine` is no longer coupled to Customer/Order internals. Adding a PLATINUM tier changes only Customer — no cascade.

---

### 🧠 Mental Model / Analogy

> Feature Envy is like a doctor making a diagnosis by calling the hospital's specialist department, asking them to read the patient records, getting the data back, then interpreting it themselves. The doctor is doing the specialist's job with the specialist's data from outside the specialist's office. In a well-designed system, you'd send the patient record to the specialist who returns the diagnosis — the knowledge stays where the expertise lives. Feature Envy means the "expertise" (the method) is in the wrong place — away from the data it needs to operate on.

- "Doctor calling specialist for raw data" → envious method calling getters on another class
- "Interpreting the specialist's data" → computing on data that doesn't belong to your class
- "Sending the patient to the specialist" → Move Method: move computation to the class that owns the data
- "Specialist returns diagnosis" → Tell, Don't Ask: let the class with the data make the decision

Where this analogy breaks down: in medicine, the doctor synthesises information from multiple specialists — this is appropriate cross-domain work. In feature envy, the computation belongs clearly in one class; cross-domain work is different from feature envy.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Feature envy happens when a method in class A works mostly with data from class B. The method should be in class B instead. Example: if you have a method in `OrderController` that calculates a discount based only on `Customer` data, that discount calculation belongs in `Customer`, not `OrderController`.

**Level 2 — How to use it (junior developer):**
Spot feature envy by looking at a method and counting: how many times does it call methods/access fields of `this` class vs. how many times does it access another class? If it accesses `customer.*` 10 times and `this.*` 0 times — it's feature envy. The fix: use IDE refactoring "Move Method" (IntelliJ: right-click method → Refactor → Move Method) to move it to the class it accesses most. After moving, the method can access `this` (the new class's own fields) directly, reducing the getter calls.

**Level 3 — How it works (mid-level engineer):**
Feature Envy is a violation of the **Information Expert** principle (from GRASP patterns): assign responsibility to the class that has the information necessary to fulfil the responsibility. When a method's information is in class B but the method lives in class A, the principle is violated. Detection heuristics: count the number of distinct other-class method calls in a method vs. own-class calls. A ratio > 2:1 (accessing external data twice as often as own data) is a strong signal. Move Method resolves feature envy by placing the method in the class it accesses most. After moving: the caller in the original class now calls a single method on the target class, rather than pulling data and computing externally. This is the "Tell, Don't Ask" pattern in action.

**Level 4 — Why it was designed this way (senior/staff):**
Feature Envy is a violation of **encapsulation** — the O(bject) in OOP. Encapsulation requires that data and the operations on that data co-locate in a class, hiding implementation details. When a method in class A accesses class B's internals (getters), class A now knows about class B's internal structure. Any change in class B's structure (renaming a getter, changing a field's type) requires changing class A. This is the definition of coupling: the cost to change B includes tracking changes required in A. Feature Envy reveals misplaced behaviour: the behaviour belongs in B because B has the data. The resulting anti-pattern it enables is the **Anemic Domain Model** (Fowler, 2003): domain objects become data containers with no behaviour (only getters/setters), while the behaviour lives in external service classes that envy the domain objects' data. This inverts object orientation: instead of objects knowing how to do things with their own data, services do things with the objects' data.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  FEATURE ENVY PATTERN                           │
├─────────────────────────────────────────────────┤
│                                                 │
│  BEFORE (Feature Envy):                         │
│  DiscountCalculator                 Customer    │
│  calcDiscount(cust) {  ──getters──→ .account   │
│    cust.getYears()                 .years       │
│    cust.getSpend() ←─────────────  .totalSpend  │
│    cust.getTier()                  .tier        │
│    if (years>5 && spend>10k && tier="GOLD")     │
│      return 0.20                                │
│    ...                                          │
│  }                                              │
│  Method is "envying" Customer's data            │
│                                                 │
│  AFTER (Feature Envy resolved):                 │
│  DiscountCalculator                 Customer    │
│  calcDiscount(cust) {  ──tell───→ .isEligible() │
│    if (cust.isLoyalGoldMember()) {              │
│      return 0.20                                │
│    }                                            │
│  }                                              │
│  Customer encapsulates its own eligibility      │
│  DiscountCalculator no longer knows internals   │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Code review: reviewer notices method accesses
  customer.getAccount().* 8 times, this.* 0 times
  → Names smell: Feature Envy
  → Suggests: move to Customer or introduce
    isEligibleForLoyaltyDiscount() on Customer
  [← YOU ARE HERE: smell named, fix proposed]
  → Developer adds isEligibleForLoyaltyDiscount() to Customer
  → Original method delegates to it
  → PR merged: coupling reduced,
    Customer behaviour enriched
```

**FAILURE PATH:**
```
Customer domain model evolves:
  getLoyaltyYears() → getLoyaltyMonths() (precision change)
  → EnvyingMethod accesses getLoyaltyYears()
  → Compilation error in DiscountCalculator.java
  → AND ReportingService.java
  → AND UserDashboardService.java
  → AND AnalyticsEngine.java
  (all 4 envied Customer's loyaltyYears data)
  → Shotgun Surgery: 4 files must change for 1 rename
```

**WHAT CHANGES AT SCALE:**
At microservices scale, feature envy becomes cross-service feature envy: Service B calls Service A's API to get data, then computes with it — rather than asking Service A to compute the result. This is the microservices equivalent: an API that returns raw data for external computation vs. provides behaviour. The second design (service provides computed results) reduces inter-service coupling.

---

### 💻 Code Example

**Example 1 — Feature Envy and Move Method:**
```java
// SMELL: BillingService envies Order's data
public class BillingService {
    public Invoice generateInvoice(Order order) {
        // All of this operates on Order data:
        String customerName = order.getCustomer()
                                    .getProfile()
                                    .getFullName();
        Address billingAddress = order.getCustomer()
                                       .getProfile()
                                       .getBillingAddress();
        List<LineItem> lines = order.getItems()
            .stream()
            .map(item -> new LineItem(
                item.getProduct().getName(),
                item.getQuantity(),
                item.getProduct().getPrice()))
            .collect(toList());
        BigDecimal total = order.getSubtotal()
            .add(order.calculateTax())
            .subtract(order.calculateDiscount());
        
        return new Invoice(customerName, billingAddress,
                           lines, total);
    }
}

// REFACTORED: Move to Order (where data lives)
public class Order {
    // Order now provides this BEHAVIOUR
    public Invoice generateInvoice() {
        return new Invoice(
            customer.getProfile().getFullName(),
            customer.getProfile().getBillingAddress(),
            buildLineItems(),
            calculateFinalTotal());
    }
    
    private List<LineItem> buildLineItems() {
        return items.stream()
            .map(item -> new LineItem(
                item.getProduct().getName(),
                item.getQuantity(),
                item.getProduct().getPrice()))
            .collect(toList());
    }
    
    private BigDecimal calculateFinalTotal() {
        return getSubtotal()
            .add(calculateTax())
            .subtract(calculateDiscount());
    }
}

// BillingService now simply:
public class BillingService {
    public Invoice generateInvoice(Order order) {
        return order.generateInvoice(); // delegates
    }
}
```

**Example 2 — Tell, Don't Ask (resolves Feature Envy):**
```java
// BAD: Ask customer for data, decide externally
if (customer.getAccount().getMembershipTier().equals("GOLD")
    && customer.getAccount().getLoyaltyYears() >= 5) {
    applyGoldDiscount(price);
}

// GOOD: Tell customer to provide the answer
if (customer.isEligibleForGoldDiscount()) {
    applyGoldDiscount(price);
}
// Customer.isEligibleForGoldDiscount() encapsulates
// the internal logic — caller doesn't know the internals
```

---

### ⚖️ Comparison Table

| Smell | Relationship | Coupling Direction | Remedy | Similar To |
|---|---|---|---|---|
| **Feature Envy** | A uses B's data excessively | A → B | Move Method to B | Law of Demeter violation |
| Inappropriate Intimacy | A and B both access each other | A ↔ B | Split or merge | Mutual Feature Envy |
| Message Chains | a.getB().getC().getD() | Chain dependency | Hide Delegate | Feature Envy chain |
| Middle Man | A just delegates to B | A → B (empty) | Remove A | Inverse of Feature Envy |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Feature Envy is always wrong | A method that operates across multiple classes equally (a cross-cutting concern) may legitimately access multiple classes. Feature Envy is specific to methods that access ONE other class more than all others. |
| Moving the method always makes the target class a God Class | If the method's computation is a natural part of the target class's domain (e.g., `Order.generateInvoice()`), it enriches the class. If the moved method is unrelated to the class's purpose, the class gains a smell (God Class). Domain alignment matters. |
| Feature Envy only appears in service classes | Feature Envy can appear anywhere: controllers accessing domain objects' internals, domain objects accessing infrastructure objects' internals. It's about method placement, not layer. |

---

### 🚨 Failure Modes & Diagnosis

**1. Anemic Domain — Feature Envy Everywhere**

**Symptom:** All business logic lives in service classes. Domain objects (User, Order, Customer) have only getters and setters. Every service envies every domain object.

**Root Cause:** Architecture decision (often in Spring applications): "domain objects are data holders; services contain business logic." This is the **Anemic Domain Model** anti-pattern.

**Diagnostic:**
```java
// Check domain class: does Order have any behaviour?
// Count methods:
//   getter/setter only: anemic = feature envy everywhere
//   rich behaviour (calculateTotal, isValid, etc.): healthy

grep -r "public.*get\|public.*set\|public.*is" \
  src/main/java/com/example/domain/ | wc -l
# vs
grep -r "public.*calculate\|public.*apply\|public.*validate" \
  src/main/java/com/example/domain/ | wc -l
# If first count >> second: anemic domain model
```

**Fix:** Gradually move behaviour into domain objects — not all at once, but as features are modified. Where a service method exclusively operates on one domain class's data, move it to that class.

**Prevention:** Architecture decision: adopt rich domain model. Service classes coordinate and orchestrate; domain classes contain domain logic.

---

**2. Move Method Creates Wrong Dependency Direction**

**Symptom:** Moving `calculateDiscount()` from `DiscountService` to `Customer` creates a dependency: `Customer` now depends on `DiscountConfig` (to read discount rates). The domain layer now depends on a configuration infrastructure concern — layer violation.

**Root Cause:** The method accesses both domain data (Customer) and infrastructure data (DiscountConfig). Moving it to Customer drags the infrastructure dependency in.

**Diagnostic:**
```java
// Before moving: count what the method accesses
// Customer data: customer.getAccount(), customer.getTier()
// Config data: discountConfig.getGoldRate()
// Mixed domain + infrastructure = can't move cleanly
```

**Fix:** Introduce **domain service**: keep `DiscountCalculator` as a domain service class (not infrastructure service), accepting domain inputs and encapsulating domain logic. OR: inject a discount policy into Customer (dependency inversion) rather than direct infrastructure access.

**Prevention:** When moving a method, check its dependencies. If the target class would gain a dependency on an infrastructure concern, introduce an abstraction (interface) instead.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Code Smell` — Feature Envy is a code smell in Fowler's taxonomy
- `Refactoring` — Move Method is the primary refactoring for Feature Envy

**Builds On This (learn these next):**
- `Shotgun Surgery` — the system-level consequence of feature envy: many methods envying data→ one data change requires many method changes
- `Divergent Change` — opposite perspective: one class changing for many reasons (often caused by receiving envious methods)

**Alternatives / Comparisons:**
- `Inappropriate Intimacy` — mutual feature envy: two classes accessing each other's data excessively
- `Message Chains` — sequential feature envy: `a.getB().getC()` accesses data through a chain of intermediate objects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Method in Class A working primarily with  │
│              │ Class B's data — it belongs in Class B   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Method coupled to another class's         │
│ SOLVES       │ internals: any field rename in B breaks A │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Data and behaviour should co-locate.      │
│              │ Tell, Don't Ask: let the object with the  │
│              │ data answer the question itself           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Method accesses another class's data >    │
│              │ 3× more than its own                      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Cross-cutting methods legitimately use    │
│              │ multiple classes equally (not envy)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Better encapsulation + Tell-Don't-Ask vs. │
│              │ enriching the target class (not anemic)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bookkeeper doing the CEO's job — using   │
│              │  the CEO's data from the wrong desk."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Shotgun Surgery → Data Clumps →           │
│              │ Divergent Change                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservices payment system has a `PaymentReportingService` that calls the `OrderService` API to retrieve order data, then calls the `CustomerService` API to retrieve customer data, then computes a financial report from both. This service "envies" both Order and Customer data across service boundaries. In a microservices context where services should be independently deployable, is this Feature Envy, or is this legitimate cross-service orchestration? How would you distinguish between the two, and what architectural alternatives exist?

**Q2.** Feature Envy and the Anemic Domain Model are related but distinct problems. A team is building a Spring Boot application. A tech lead proposes: "Domain objects should only have getters and setters. All business logic belongs in `@Service` classes." Another tech lead counters: "Business logic belongs in domain objects. Services only coordinate I/O." Both positions have real-world precedent. Design a case where the first approach leads to problems (Feature Envy everywhere) and a case where the second approach leads to problems (domain objects with infrastructure dependencies). What principle governs which logic should be in which layer?

