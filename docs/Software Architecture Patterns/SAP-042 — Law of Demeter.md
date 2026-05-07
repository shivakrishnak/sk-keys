---
layout: default
title: "Law of Demeter"
parent: "Software Architecture Patterns"
nav_order: 42
permalink: /software-architecture/law-of-demeter/
number: "SAP-042"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming, Coupling, Encapsulation
used_by: OO design, API design, Code review, Refactoring
related: Tell Don't Ask, Encapsulation, Coupling, SOLID Principles
tags:
  - architecture
  - principles
  - oop
  - intermediate
  - coupling
---

# SAP-042 — Law of Demeter

⚡ TL;DR — The Law of Demeter states that a method should only call methods on its direct collaborators — not on objects obtained from those collaborators — preventing deep chains that expose and couple to internal object structures.

---

### 📊 Entry Metadata

| #760            | Category: Software Architecture Patterns                  | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Coupling, Encapsulation      |                 |
| **Used by:**    | OO design, API design, Code review, Refactoring           |                 |
| **Related:**    | Tell Don't Ask, Encapsulation, Coupling, SOLID Principles |                 |

---

### 🔥 The Problem This Solves

**THE TRAIN WRECK PROBLEM:**

```java
double discount =
    order.getCustomer()
         .getLoyaltyAccount()
         .getTier()
         .getDiscountRate();
```

This chain of calls traverses three objects deep into the object graph. `OrderService` now knows that `Order` has a `Customer`, `Customer` has a `LoyaltyAccount`, `LoyaltyAccount` has a `Tier`, and `Tier` has a `getDiscountRate()`. Changing any of these internal structures (renaming `LoyaltyAccount` to `RewardsMembership`, changing `Tier` to return a discount as a `BigDecimal` instead of `double`) breaks this code. The `OrderService` is coupled to the internals of `Customer`, `LoyaltyAccount`, and `Tier` — objects it should know nothing about.

**THE LAW OF DEMETER SOLUTION:**

```java
double discount = order.getDiscountRate();
```

`Order` computes the discount from its collaborators internally. `OrderService` asks `Order` for what it needs — not for the object that has the thing it needs, or the object that has the object that has the thing.

---

### 📘 Textbook Definition

The Law of Demeter (LoD), also known as the Principle of Least Knowledge, was formulated at Northeastern University in 1987 (Lieberherr and Holland) during the "Demeter project." The formal definition: a method M of object O may only call methods on: 1) O itself (self/this), 2) M's parameters, 3) objects created within M, 4) O's direct instance variables (fields), 5) global/static variables. In other words: only talk to your immediate friends; don't talk to strangers. The "train wreck" pattern (`a.getB().getC().doD()`) violates LoD because `a` is reaching through `b` to talk to `c`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Only call methods on objects you directly hold — don't reach through objects to call methods on their internals.

**One analogy:**

> If you want to ask a colleague to send an email on your behalf, you ask your colleague directly: "Please send this email." You don't reach into your colleague's desk drawer, take their phone, find the email app, and compose the message yourself. You talk to your direct collaborator (colleague), not their collaborator (phone). The colleague decides how to send the email.

**One insight:**
LoD violations create structural coupling: you can't change the internals of `Customer` without potentially breaking code in `OrderService`, `ReportService`, `NotificationService`, and any other class that traverses through `Customer`. LoD violations spread structural knowledge of object internals across the codebase.

---

### 🔩 First Principles Explanation

**THE DEMETER RULE — ALLOWED AND FORBIDDEN:**

```
┌──────────────────────────────────────────────────────────┐
│     LAW OF DEMETER — ALLOWED METHOD CALL TARGETS         │
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

Rename `LoyaltyAccount` to `RewardsMembership`: Update `Customer` (which holds the account), and any class directly using `LoyaltyAccount`. No changes to `OrderService`, `ReportService`, or `NotificationService` — they never knew `LoyaltyAccount` existed.

---

### 🧠 Mental Model / Analogy

> The Law of Demeter is like a company's org chart. You should communicate with your immediate team and direct managers/reports — not jump levels to talk directly to your manager's manager's manager, or to a subordinate of a subordinate. Going through channels ensures each layer manages its own concerns. Direct cross-level communication bypasses encapsulation (each level's internal organization) and creates structural dependencies on the org's internal structure.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
Only call methods on objects you directly have. Don't chain calls: `a.getB().getC().doD()`. Instead ask `a` to do whatever `getB().getC().doD()` was supposed to accomplish.

**Level 2 — How to apply it (junior):**
When you find yourself writing `a.getB().getC()`, stop. Ask: "Who should be responsible for this?" The object that knows about `C` (i.e., `B` in this case) should provide a method that does what you need. Add `doD()` to `B` (or a method on `A` that delegates to `B`). The chain becomes `a.doD()`. Test: can you describe what a method does without knowing the types of intermediate objects? If not, you're likely violating LoD.

**Level 3 — LoD and Tell Don't Ask (mid-level):**
Law of Demeter and Tell Don't Ask (TDA) are related. TDA says: tell objects to do things, don't ask for their data to do it yourself. LoD says: don't navigate through objects to get to the data. Both principles point in the same direction: move behavior to where the data is. `order.getCustomer().getLoyaltyAccount().getPoints()` violates both LoD (navigation chain) and TDA (asking for data to use externally). Fix: `order.applyLoyaltyDiscount(cart)` — tell Order to apply the discount, not ask it for the data needed to compute the discount. The discount computation moves into `Order`/`Customer`/`LoyaltyAccount` where the data lives.

**Level 4 — Structural vs data coupling (senior/staff):**
LoD applies primarily to behavioral/structural navigation. It doesn't mean you can never return data from a method call. Returning value objects (not object graphs) is fine. The distinction: `customer.getAddress()` returning an `Address` value object is fine — you use the `Address` to render it, not to further navigate its graph. `customer.getAddress().getCity().getCountry().getCurrencyCode()` is a violation — you're navigating through `Address`'s structure. The practical rule: if you're calling a method just to get an object to call another method on, that's likely LoD. If you're calling a method to get a value you'll use directly, that's probably fine. Fluent builders (`Person.builder().name("Alice").age(30).build()`) are a deliberate exception to LoD — they're a designed API pattern where chaining is the interface.

---

### ⚙️ How It Works (Mechanism)

**Refactoring to comply:**

```
┌──────────────────────────────────────────────────────────┐
│      LAW OF DEMETER — REFACTORING STEPS                  │
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
│          Order — it IS the order; it has the customer    │
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

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│     LAW OF DEMETER — BEFORE AND AFTER                    │
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

### ⚖️ Comparison Table

| Pattern            | Problem                                         | Solution direction                                       |
| ------------------ | ----------------------------------------------- | -------------------------------------------------------- |
| **Law of Demeter** | Navigation chains expose internal structure     | Add delegating methods; ask objects, not their internals |
| Tell Don't Ask     | Asking for data to do work the object should do | Move logic to where the data is                          |
| Encapsulation      | Internal state exposed via getters              | Hide state; expose behavior                              |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| LoD means no method chaining         | Fluent builder APIs chain by design and are acceptable; LoD targets navigation through an object graph, not designed fluent interfaces |
| LoD means lots of delegating methods | It does add delegation methods, but these are in the right class — the class that owns the relevant data                               |
| LoD only applies to navigation       | LoD also applies to not reaching into collections returned by methods and calling methods on the collection's elements                 |
| LoD reduces functionality            | LoD only changes WHERE the logic is written, not what it does; same behavior, better encapsulation                                     |

---

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

### 🔗 Related Keywords

**Prerequisites:**

- `Encapsulation` — LoD is a way to enforce encapsulation through call discipline
- `Coupling` — LoD violations create hidden structural coupling

**Related:**

- `Tell Don't Ask` — complementary principle: tell objects what to do, don't ask for data
- `Connascence` — formal framework for analyzing coupling including LoD-type violations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Only call methods on direct collaborators│
│              │ Not on objects navigated through getters │
├──────────────┼───────────────────────────────────────────┤
│ VIOLATION    │ a.getB().getC().doD() — train wreck      │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Add a.doD() that delegates internally    │
├──────────────┼───────────────────────────────────────────┤
│ COST OF VIOL.│ Structural coupling; fragile refactoring │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ask your colleague, not your colleague's │
│              │  phone — talk to friends, not strangers"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're reviewing a PR with this code: `report.getAuthor().getTeam().getManager().getEmail()`. Explain why this violates the Law of Demeter and write the refactored version. Where do you add delegation methods, and in which direction does the responsibility flow?

**Q2.** The Law of Demeter says don't call methods on returned objects. But consider this code: `orderItems.stream().filter(i -> i.isExpired()).collect(toList())`. Here `orderItems` is a field, `.stream()` returns a `Stream`, `.filter()` returns another `Stream`, `.collect()` returns a `List`. Is this a LoD violation? What is the practical rule that distinguishes acceptable fluent APIs from harmful navigation chains?
