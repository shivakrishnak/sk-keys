---
id: SAP-047
layout: default
title: "Law of Demeter"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /software-architecture/law-of-demeter/
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-043, SAP-051
used_by: 
related: SAP-043, SAP-048, SAP-051
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
---

# SAP-047 - Law of Demeter

⚡ TL;DR - The Law of Demeter states that a method should only call methods on its direct collaborators - not on objects obtained from those collaborators - preventing deep chains that expose and couple to internal object structures.

---
id: SAP-047

### 🔥 The Problem This Solves

**THE TRAIN WRECK PROBLEM:**

```java
double discount =
    order.getCustomer()
         .getLoyaltyAccount()
         .getTier()
         .getDiscountRate();
```

This chain of calls traverses three objects deep into the object graph. `OrderService` now knows that `Order` has a `Customer`, `Customer` has a `LoyaltyAccount`, `LoyaltyAccount` has a `Tier`, and `Tier` has a `getDiscountRate()`. Changing any of these internal structures (renaming `LoyaltyAccount` to `RewardsMembership`, changing `Tier` to return a discount as a `BigDecimal` instead of `double`) breaks this code. The `OrderService` is coupled to the internals of `Customer`, `LoyaltyAccount`, and `Tier` - objects it should know nothing about.

**THE LAW OF DEMETER SOLUTION:**

```java
double discount = order.getDiscountRate();
```

`Order` computes the discount from its collaborators internally. `OrderService` asks `Order` for what it needs - not for the object that has the thing it needs, or the object that has the object that has the thing.

**EVOLUTION:** The Law of Demeter was formalized in 1987 at Northeastern University during the Demeter research project (Lieberherr and Holland). The formal definition was straightforward; widespread adoption was slow because OO languages (Java, C++) made method chaining syntactically convenient and visually appealing. Martin Fowler's refactoring catalog (1999) named the anti-pattern "Message Chains" and the corresponding smell "Middle Man," giving practitioners concrete vocabulary for LoD violations. The rise of fluent APIs (Java Streams 2014, Kotlin builders, Jest test chains) created a generation-long debate about what constitutes a LoD violation versus an intentional DSL - resolved by the distinction between object navigation (bad) and pipeline operations on the same object type (acceptable)., also known as the Principle of Least Knowledge, was formulated at Northeastern University in 1987 (Lieberherr and Holland) during the "Demeter project." The formal definition: a method M of object O may only call methods on: 1) O itself (self/this), 2) M's parameters, 3) objects created within M, 4) O's direct instance variables (fields), 5) global/static variables. In other words: only talk to your immediate friends; don't talk to strangers. The "train wreck" pattern (`a.getB().getC().doD()`) violates LoD because `a` is reaching through `b` to talk to `c`.

---
id: SAP-047

### ⏱️ Understand It in 30 Seconds

**One line:**
Only call methods on objects you directly hold - don't reach through objects to call methods on their internals.

**One analogy:**

> If you want to ask a colleague to send an email on your behalf, you ask your colleague directly: "Please send this email." You don't reach into your colleague's desk drawer, take their phone, find the email app, and compose the message yourself. You talk to your direct collaborator (colleague), not their collaborator (phone). The colleague decides how to send the email.

**One insight:**
LoD violations create structural coupling: you can't change the internals of `Customer` without potentially breaking code in `OrderService`, `ReportService`, `NotificationService`, and any other class that traverses through `Customer`. LoD violations spread structural knowledge of object internals across the codebase.

---
id: SAP-047

### 🔩 First Principles Explanation

**THE DEMETER RULE - ALLOWED AND FORBIDDEN:**

```
┌──────────────────────────────────────────────────────────┐
│     LAW OF DEMETER - ALLOWED METHOD CALL TARGETS         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  In method doSomething(ParamType p) of ClassA:           │
│                                                          │
│  ✅ ALLOWED:                                             │
│    this.method()            (self)                       │
│    p.method()               (parameter)                  │
│    localVar.method()        (locally created object)     │
│    this.field.method()      (direct field/component)     │
│    StaticClass.method()     (static)                     │
│                                                          │
│  ❌ FORBIDDEN (LoD violation):                           │
│    this.getB().method()     (stranger via getter)        │
│    p.getX().method()        (stranger via parameter)     │
│    a.b.c.method()           (chained navigation)         │
│                                                          │
│  KEY: You can only call methods on objects you HOLD      │
│  Not on objects obtained by calling other methods        │
└──────────────────────────────────────────────────────────┘
```

**WHY TRAIN WRECKS ARE HARMFUL:**

```
┌──────────────────────────────────────────────────────────┐
│        TRAIN WRECK COUPLING ANALYSIS                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  order.getCustomer().getLoyaltyAccount().getTier()       │
│        .getDiscountRate()                                │
│                                                          │
│  OrderService must KNOW:                                 │
│    1. Order has a getCustomer() method                   │
│    2. Customer has a getLoyaltyAccount() method          │
│    3. LoyaltyAccount has a getTier() method              │
│    4. Tier has a getDiscountRate() method                │
│    5. That the return type of getDiscountRate() is double│
│                                                          │
│  OrderService is coupled to FOUR class internals         │
│  Change any of these: OrderService breaks                │
│                                                          │
│  LoD-compliant: order.getDiscountRate()                  │
│  OrderService coupled to ONE class internal              │
│  Order handles the internal navigation                   │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-047

### 🧪 Thought Experiment

**STRUCTURAL CHANGE IMPACT:**
Before LoD:

- OrderService: `order.getCustomer().getLoyaltyAccount().getTier().getDiscountRate()`
- ReportService: `customer.getLoyaltyAccount().getTier().getDiscountName()`
- NotificationService: `order.getCustomer().getLoyaltyAccount().getPoints()`

Now: rename `LoyaltyAccount` to `RewardsMembership`. Search: 47 call sites reference `getLoyaltyAccount()`. All must be updated. Fragile refactoring.

After LoD:

- OrderService: `order.getDiscountRate()`
- ReportService: `customer.getTierName()`
- NotificationService: `order.getCustomerRewardPoints()`

Rename `LoyaltyAccount` to `RewardsMembership`: Update `Customer` (which holds the account), and any class directly using `LoyaltyAccount`. No changes to `OrderService`, `ReportService`, or `NotificationService` - they never knew `LoyaltyAccount` existed.

---
id: SAP-047

### 🧠 Mental Model / Analogy

> The Law of Demeter is like a company's org chart. You should communicate with your immediate team and direct managers/reports - not jump levels to talk directly to your manager's manager's manager, or to a subordinate of a subordinate. Going through channels ensures each layer manages its own concerns. Direct cross-level communication bypasses encapsulation (each level's internal organization) and creates structural dependencies on the org's internal structure.

---
id: SAP-047

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Only call methods on objects you directly have. Don't chain calls: `a.getB().getC().doD()`. Instead ask `a` to do whatever `getB().getC().doD()` was supposed to accomplish.

**Level 2 - How to apply it (junior):**
When you find yourself writing `a.getB().getC()`, stop. Ask: "Who should be responsible for this?" The object that knows about `C` (i.e., `B` in this case) should provide a method that does what you need. Add `doD()` to `B` (or a method on `A` that delegates to `B`). The chain becomes `a.doD()`. Test: can you describe what a method does without knowing the types of intermediate objects? If not, you're likely violating LoD.

**Level 3 - LoD and Tell Don't Ask (mid-level):**
Law of Demeter and Tell Don't Ask (TDA) are related. TDA says: tell objects to do things, don't ask for their data to do it yourself. LoD says: don't navigate through objects to get to the data. Both principles point in the same direction: move behavior to where the data is. `order.getCustomer().getLoyaltyAccount().getPoints()` violates both LoD (navigation chain) and TDA (asking for data to use externally). Fix: `order.applyLoyaltyDiscount(cart)` - tell Order to apply the discount, not ask it for the data needed to compute the discount. The discount computation moves into `Order`/`Customer`/`LoyaltyAccount` where the data lives.

**Level 4 - Structural vs data coupling (senior/staff):**
LoD applies primarily to behavioral/structural navigation. It doesn't mean you can never return data from a method call. Returning value objects (not object graphs) is fine. The distinction: `customer.getAddress()` returning an `Address` value object is fine - you use the `Address` to render it, not to further navigate its graph. `customer.getAddress().getCity().getCountry().getCurrencyCode()` is a violation - you're navigating through `Address`'s structure. The practical rule: if you're calling a method just to get an object to call another method on, that's likely LoD. If you're calling a method to get a value you'll use directly, that's probably fine. Fluent builders (`Person.builder().name("Alice").age(30).build()`) are a deliberate exception to LoD - they're a designed API pattern where chaining is the interface.

---
id: SAP-047

### ⚙️ How It Works (Mechanism)

**Refactoring to comply:**

```
┌──────────────────────────────────────────────────────────┐
│      LAW OF DEMETER - REFACTORING STEPS                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  IDENTIFY: order.getCustomer()                           │
│                 .getLoyaltyAccount()                     │
│                 .getTier()                               │
│                 .getDiscountRate()                       │
│                                                          │
│  STEP 1: What am I trying to do?                         │
│          Get the discount rate for this order            │
│                                                          │
│  STEP 2: Which object should know this?                  │
│          Order - it IS the order; it has the customer    │
│                                                          │
│  STEP 3: Add delegating method to Order:                 │
│          public double getDiscountRate() {               │
│            return customer.getLoyaltyAccount()           │
│                           .getTier()                     │
│                           .getDiscountRate();            │
│          }                                               │
│                                                          │
│  STEP 4: Can Customer simplify further?                  │
│          customer.getDiscountRate()                      │
│          → which delegates to loyalty account            │
│                                                          │
│  RESULT: Each object manages its own navigation          │
│  External callers: order.getDiscountRate()               │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-047

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│     LAW OF DEMETER - BEFORE AND AFTER                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  BEFORE (violation):                                     │
│                                                          │
│  OrderService knows: Order, Customer, LoyaltyAccount,    │
│  Tier (4 classes, 4 coupling dependencies)               │
│                                                          │
│  ┌──────────────┐   get   ┌──────────┐                  │
│  │ OrderService │ ──────▶ │ Customer │                   │
│  │              │ ──────▶ │LoyaltyAcc│                   │
│  │              │ ──────▶ │ Tier     │                   │
│  └──────────────┘         └──────────┘                  │
│                                                          │
│  AFTER (compliant):                                      │
│                                                          │
│  OrderService knows: Order (1 class, 1 coupling dep)     │
│                                                          │
│  ┌──────────────┐         ┌──────────┐                  │
│  │ OrderService │ ──────▶ │  Order   │ (manages rest)   │
│  └──────────────┘         └──────────┘                  │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-047

### 💻 Code Example

```java
// VIOLATION: OrderService reaches into Customer structure
public class OrderService {
    public BigDecimal calculateDiscountedTotal(Order order) {
        // Knows about Customer, LoyaltyAccount, Tier
        // all internal to each other
        double discountRate = order.getCustomer()
            .getLoyaltyAccount()
            .getTier()
            .getDiscountRate();

        return order.getTotal()
            .multiply(BigDecimal.ONE
                .subtract(BigDecimal.valueOf(discountRate)));
    }
}

// ─────────────────────────────────────────────────────────

// COMPLIANT: Add discountedTotal() to Order
public class Order {
    private final Customer customer;
    private final MoneyAmount total;

    // Order delegates to Customer, which delegates to tier
    // OrderService doesn't know how this is computed
    public MoneyAmount discountedTotal() {
        double rate = customer.getDiscountRate();
        return total.multiply(1.0 - rate);
    }
}

public class Customer {
    private final LoyaltyAccount loyaltyAccount;

    // Customer exposes what callers need
    // Callers don't know LoyaltyAccount exists
    public double getDiscountRate() {
        return loyaltyAccount.getCurrentDiscountRate();
    }
}

// OrderService: one direct collaborator, Order
public class OrderService {
    public MoneyAmount calculateDiscountedTotal(Order order) {
        return order.discountedTotal(); // clean, simple
    }
}
```

---
id: SAP-047

### ⚖️ Comparison Table

| Pattern            | Problem                                         | Solution direction                                       |
| ------------------ | ----------------------------------------------- | -------------------------------------------------------- |
| **Law of Demeter** | Navigation chains expose internal structure     | Add delegating methods; ask objects, not their internals |
| Tell Don't Ask     | Asking for data to do work the object should do | Move logic to where the data is                          |
| Encapsulation      | Internal state exposed via getters              | Hide state; expose behavior                              |

---
id: SAP-047

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| LoD means no method chaining         | Fluent builder APIs chain by design and are acceptable; LoD targets navigation through an object graph, not designed fluent interfaces |
| LoD means lots of delegating methods | It does add delegation methods, but these are in the right class - the class that owns the relevant data                               |
| LoD only applies to navigation       | LoD also applies to not reaching into collections returned by methods and calling methods on the collection's elements                 |
| LoD reduces functionality            | LoD only changes WHERE the logic is written, not what it does; same behavior, better encapsulation                                     |

---
id: SAP-047

### 🚨 Failure Modes & Diagnosis

**Deep navigation coupling breaks on refactoring**

**Symptom:** Renaming an internal field or class triggers cascade of failures in many unrelated classes.

**Root Cause:** LoD violations causing widespread structural coupling.

**Diagnosis:**

```bash
# Find potential train wrecks in Java code
grep -rn "\\.get[A-Z][a-zA-Z]*()\\.get[A-Z]" src/
# Multi-dot chains: a.getX().getY().getZ()
# Each match is a potential LoD violation
```

---
id: SAP-047

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** A unit of code should only communicate with its immediate collaborators, not navigate through them to reach distant objects. Every additional hop in a call chain is another coupling to an internal structure that can change.

**Where else this pattern appears:**

- **Organizational hierarchy:** In a well-run organization, a VP doesn't direct individual engineers (skipping managers). Communication follows the hierarchy. Bypassing hierarchy is "going around" the proper collaborator - the equivalent of a LoD violation.
- **Medical referrals:** A GP refers you to a specialist; you don't call the specialist's subspecialty clinic directly. Each layer of the medical system knows its immediate collaborators (GP knows specialists; specialists know subspecialists). No one reaches through the organizational structure.
- **REST API design:** A well-designed REST API exposes resources at the right level of abstraction. You call `/orders/{id}` to get order details including customer name - you don't call `/orders/{id}` then `/customers/{customerId}` then `/loyalty/{loyaltyId}`. The API encapsulates the navigation; you ask for the output, not the path.

---
id: SAP-047

### 💡 The Surprising Truth

The Law of Demeter is one of the most frequently cited and most frequently misunderstood design principles. The common misconception: "only one dot" - that `object.method()` is fine but `object.getA().method()` always violates LoD. This is wrong. The correct principle is about STRUCTURAL coupling, not syntactic chaining. `list.stream().filter(x -> x > 0).toList()` chains multiple method calls but does NOT violate LoD because each call returns the same conceptual type (a stream/collection) - you're not navigating to a different object's INTERNAL state. The LoD violation is navigating through an object to reach the PRIVATE STRUCTURE of a different object. The practical test: does changing the internal structure of any intermediate object break this call?

---
id: SAP-047

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-043 - SOLID Principles (specifically SRP and ISP: LoD violations often indicate that the object being navigated through is not presenting the right interface to its callers)
- SAP-051 - Coupling (LoD is a rule for controlling structural coupling; understanding coupling types helps classify which LoD violations are most harmful)

**Builds On This (learn these next):**

- SAP-048 - Tell Don't Ask (the behavioral companion to LoD: LoD says don't navigate to distant objects; TDA says tell the immediate object to perform the behavior, don't ask it for state and decide externally)
- SAP-043 - SOLID Principles (ISP: LoD violations often expose ISP violations; the intermediate object that exposes navigation chains may need a more focused interface)

**Alternatives / Comparisons:**

- SAP-051 - Coupling (LoD violations create Connascence of Position and structural coupling; understanding coupling types provides the theoretical foundation for why LoD matters)
- SAP-052 - Connascence (precise framework for describing exactly WHAT type of coupling a LoD violation creates)

---
id: SAP-047

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Only call methods on direct collaborators│
│              │ Not on objects navigated through getters │
├──────────────┼───────────────────────────────────────────┤
│ VIOLATION    │ a.getB().getC().doD() - train wreck      │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Add a.doD() that delegates internally    │
├──────────────┼───────────────────────────────────────────┤
│ COST OF VIOL.│ Structural coupling; fragile refactoring │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ask your colleague, not your colleague's │
│              │  phone - talk to friends, not strangers"  │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-047

### 🧠 Think About This Before We Continue

**Q1.** You're reviewing a PR with this code: `report.getAuthor().getTeam().getManager().getEmail()`. Explain why this violates the Law of Demeter and write the refactored version. Where do you add delegation methods, and in which direction does the responsibility flow?

*Hint:* Research "Tell Don't Ask" and specifically the delegation chain pattern: `Report` adds `getAuthorManagerEmail()` which internally calls `author.getManagerEmail()`, and `Author` adds `getManagerEmail()` which calls `team.getManagerEmail()`, and `Team` adds `getManagerEmail()` which returns `manager.getEmail()`. The responsibility flows inward - each class delegates to its direct collaborators. The key question: does `Report` need to know that authors are organized into teams with managers? If not, `Report.getAuthorManagerEmail()` hides all of that.

**Q2.** The Law of Demeter says don't call methods on returned objects. But consider this code: `orderItems.stream().filter(i -> i.isExpired()).collect(toList())`. Here `orderItems` is a field, `.stream()` returns a `Stream`, `.filter()` returns another `Stream`, `.collect()` returns a `List`. Is this a LoD violation? What is the practical rule that distinguishes acceptable fluent APIs from harmful navigation chains?

*Hint:* Research the "one dot" rule misconception and the correct LoD formulation. Java Streams do NOT violate LoD because: (1) Stream operations are applied to the same logical thing (a sequence of items); (2) `Stream` is a public abstraction with no internal structure exposed; (3) changing how `orderItems` is stored internally doesn't break the stream chain. LoD is violated when you navigate to the PRIVATE INTERNAL STRUCTURE of an object (`.getAuthor().team.managers` where `team` and `managers` are internal to `Author`). Test: "If I refactor the internal structure of any object in this chain, does this code break?"

**Q3.** A developer argues: "Adding delegation methods (LoD-compliant forwarding methods) causes code bloat. My `Report` class now has 12 delegation methods that just forward calls to `Author`, `Team`, and `Manager`. This is worse than the original chained calls." How do you respond, and what design smell does this argument reveal about the `Report` class?

*Hint:* Research the "Message Chain" refactoring and the associated smell: when a class needs 12 delegation methods to satisfy LoD, it may be doing too much. Fowler's advice: consider whether `Report` actually NEEDS all 12 behaviors, or whether some callers should work with `Author` directly instead of through `Report`. LoD violations often reveal a missing direct relationship - if callers frequently navigate `report.getAuthor().something()`, perhaps those callers should depend on `Author` directly, not `Report`. The delegation method smell is a symptom of incorrect dependency relationships, not a problem with LoD.
