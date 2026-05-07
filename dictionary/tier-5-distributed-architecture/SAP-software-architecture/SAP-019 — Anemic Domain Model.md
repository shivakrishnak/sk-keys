---
layout: default
title: "Anemic Domain Model"
parent: "Software Architecture Patterns"
nav_order: 19
permalink: /software-architecture/anemic-domain-model/
number: "SAP-019"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Domain Model, Object-Oriented Design, Service Layer
used_by: Transaction Script, Service Layer, CRUD-based architectures
related: Domain Model, Rich Domain Model, Transaction Script, Service Layer
tags:
  - architecture
  - ddd
  - anti-pattern
  - deep-dive
  - advanced
---

# SAP-019 — Anemic Domain Model

⚡ TL;DR — An Anemic Domain Model is an anti-pattern where domain objects contain only data (getters/setters) with no business behavior — all logic is pushed into service classes, violating encapsulation and scattering business rules.

---

### 📊 Entry Metadata

| #737            | Category: Software Architecture Patterns                           | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Domain Model, Object-Oriented Design, Service Layer                |                 |
| **Used by:**    | Transaction Script, Service Layer, CRUD-based architectures        |                 |
| **Related:**    | Domain Model, Rich Domain Model, Transaction Script, Service Layer |                 |

---

### 🔥 The Problem This Solves

**THE ANTI-PATTERN CONTEXT:**
This entry describes a pattern to _avoid_. It is named and documented as a known anti-pattern by Martin Fowler. Understanding what it is and why it emerges is essential for recognizing it in code you encounter — which you will, often.

**WHY IT EMERGES:**
Developers trained in relational databases or procedural programming naturally model objects as data containers (tables in code) and write procedures that operate on them (stored procedures in Java). This looks like OO design but violates its core principle: encapsulation. The result is objects that are technically classes but philosophically structs.

**THE HIDDEN COST:**
The anemic model seems simpler and more flexible at first. Any service can access any field of any object and do anything with it. But as the system grows, the same logic appears in five different services with five slight variations, and there is no canonical place that owns the business rule. The business domain becomes invisible in the code.

---

### 📘 Textbook Definition

An Anemic Domain Model, as identified and named by Martin Fowler in his 2003 bliki post, is a domain model where the domain objects contain little or no business behavior. The domain objects are essentially data transfer objects with getters and setters, while all business logic is distributed across service classes. Fowler described it as "a fundamentally bad thing" that violates the basic principle of object-oriented design by separating data from the procedures that operate on that data, producing effectively a procedural design disguised in object-oriented clothing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Domain objects that are just data bags — all the logic is somewhere else in services.

**One analogy:**

> A bank account where the `Account` object is just a box holding a number. The rules about whether you can withdraw, how overdraft works, and what constitutes fraud all live in separate `AccountService`, `FraudService`, and `OverdraftService` classes. The account itself has no opinion about what can be done to it — any service can reach in and change any field directly.

**One insight:**
An anemic model means "the domain model exists as a concept in the team's heads but nowhere in the code." The code is organised around technical operations (save, load, validate, transform) rather than around business concepts (ship an order, cancel a subscription, approve a loan).

---

### 🔩 First Principles Explanation

**WHY IT FEELS RIGHT (INITIALLY):**

```
┌──────────────────────────────────────────────────────────┐
│              WHY ANEMIC MODEL SEEMS SENSIBLE             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Database-first thinking:                             │
│     Tables have rows and columns, not behavior.          │
│     Entity = table row in OO clothing.                   │
│                                                          │
│  2. Framework pressure:                                  │
│     JPA requires no-arg constructors + public setters.   │
│     Encourages plain bean objects.                       │
│                                                          │
│  3. "Separation of concerns" misapplied:                 │
│     "Data here, logic there" sounds clean.               │
│     But business logic IS data's concern.                │
│                                                          │
│  4. Testing confusion:                                   │
│     Services seem easier to mock and test.               │
│     (Rich domain objects are actually easier to test)    │
└──────────────────────────────────────────────────────────┘
```

**THE STRUCTURAL ANTI-PATTERN:**

```
┌──────────────────────────────────────────────────────────┐
│              ANEMIC MODEL STRUCTURE                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Order (anemic — pure data, no rules):                   │
│  + getId(): OrderId                                      │
│  + getStatus(): OrderStatus                              │
│  + setStatus(status): void  ← ANYONE can call this!     │
│  + getItems(): List<OrderItem>                           │
│  + setItems(items): void    ← DANGEROUS: bypasses rules │
│                                                          │
│  OrderService (where all the rules actually live):       │
│  + cancelOrder(order): void                              │
│  + shipOrder(order): void                                │
│  + processPayment(order): void                           │
│  + validateOrder(order): void                            │
│                                                          │
│  OrderValidationService (more rules split off):          │
│  + validate(order): void                                 │
│                                                          │
│  Problem: which service has the canonical                │
│  "can this order be cancelled?" rule?                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**TRACING A BUG:**
A reported bug: "Sometimes orders are cancelled even after they've shipped."

In an anemic model, you need to search across ALL service classes for every place that calls `order.setStatus(CANCELLED)`. You find four different places:

1. `OrderService.cancel()` — has the status check
2. `AdminService.forceCancel()` — skips the check (admin override)
3. `RefundService.processRefund()` — accidentally sets status to CANCELLED
4. `BatchCancellationJob.run()` — uses a different status check

There is no canonical rule about cancellation. You fix `RefundService` but the bug might return in a fifth place you haven't found yet.

In a rich domain model, `order.cancel()` is the only place that can change the status to CANCELLED, and it always enforces the rule. The bug has exactly one place to exist.

---

### 🧠 Mental Model / Analogy

> An anemic model is like a hospital where patients are just paper files in a folder. Doctors (services) read the files, make decisions, and write updates to the files. The files themselves don't know anything — they're just data. The problem: 50 different doctors can update the files, each with slightly different understanding of the rules. Compare to a "smart patient record" that validates all updates against clinical protocols before allowing them to be saved.

The key insight: The rules about what can be done to data should travel with the data, not be distributed across all the actors who might touch the data.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
Business objects that contain only data, with all the actual logic in separate classes. Like a document with no formatting rules — anyone can edit it any way they want.

**Level 2 — How to recognise it (junior developer):**
Signs of an anemic model: domain objects have only getters/setters; all service methods take a domain object and operate on it externally; tests test services not domain objects; you can freely call `entity.setStatus(anything)` from anywhere.

**Level 3 — Why it's harmful (mid-level):**
The anemic model breaks encapsulation — the core OO principle that objects manage their own state. This produces: scattered logic (same rule in multiple services), no canonical invariant enforcement (anyone can put the object in an invalid state), low cohesion (services have too many responsibilities), and difficult refactoring (you don't know where all the logic for an entity lives).

**Level 4 — When it's acceptable (senior/staff):**
Fowler himself notes that anemic models aren't universally wrong — they're wrong for complex domain logic. For simple CRUD applications with minimal business rules, a Transaction Script + anemic entities is simpler and faster. The key question is: does this application have significant business logic that benefits from rich modeling? If the domain is "create/read/update/delete records with a few validations," an anemic model is proportionate. If the domain is "manage complex financial instruments with sophisticated risk rules," an anemic model is technical debt from day one.

---

### ⚙️ How It Works (Mechanism)

**Recognizing anemic vs. rich code:**

```
┌──────────────────────────────────────────────────────────┐
│         ANEMIC vs RICH — SIDE BY SIDE                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ANEMIC (anti-pattern):                                  │
│  // Service checks and then calls setter                 │
│  if (order.getStatus() != SHIPPED) {                     │
│      order.setStatus(CANCELLED);                         │
│      // rule is HERE in service, not in Order            │
│  }                                                       │
│                                                          │
│  RICH (correct):                                         │
│  // Order enforces its own rule                          │
│  order.cancel();                                         │
│  // cancel() throws if status is SHIPPED                 │
│  // caller doesn't need to know the rule                 │
│                                                          │
│  TELL, DON'T ASK principle:                              │
│  Anemic model = ASK for data, then act on it             │
│  Rich model   = TELL the object to do the thing          │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**HOW ANEMIC MODELS EVOLVE OVER TIME:**

```
Year 1:  Simple app, 3 services, 5 entities
         Seems manageable. Anemic model works fine.

Year 2:  8 services, 15 entities
         Duplicate logic starts appearing.
         cancelOrder() logic in 2 places.

Year 3:  20 services, 30 entities
         cancelOrder() logic in 5 places.
         3 different versions of the rule.
         Bugs are hard to trace.

Year 4:  "Big Ball of Mud"
         No one knows all the rules for an entity.
         Refactoring is dangerous.
         Every change has unexpected side effects.
```

---

### 💻 Code Example

**Anemic Domain Model (what to avoid):**

```java
// Anemic entity — no behavior, just data
@Entity
public class BankAccount {
    @Id private UUID id;
    private BigDecimal balance;
    private AccountStatus status;
    private BigDecimal overdraftLimit;

    // Only getters and setters — anyone can do anything
    public BigDecimal getBalance() { return balance; }
    public void setBalance(BigDecimal b) { balance = b; }
    public AccountStatus getStatus() { return status; }
    public void setStatus(AccountStatus s) { status = s; }
    public BigDecimal getOverdraftLimit() {
        return overdraftLimit;
    }
}

// All logic in service — can reach into any field
@Service
public class BankAccountService {
    public void withdraw(BankAccount account,
                         BigDecimal amount) {
        // Rule duplicated here
        if (account.getStatus() == FROZEN) {
            throw new AccountFrozenException();
        }
        BigDecimal newBalance =
            account.getBalance().subtract(amount);
        // Rule duplicated here again (slightly different)
        if (newBalance.compareTo(
                account.getOverdraftLimit().negate()) < 0) {
            throw new InsufficientFundsException();
        }
        account.setBalance(newBalance); // direct setter
    }
}

// Someone else writes this later, missing the overdraft rule:
@Service
public class TellerService {
    public void processWithdrawal(BankAccount acct,
                                  BigDecimal amt) {
        if (acct.getStatus() == FROZEN) {
            throw new AccountFrozenException();
        }
        // FORGOT to check overdraft limit — bug introduced
        acct.setBalance(acct.getBalance().subtract(amt));
    }
}
```

**Refactored to Rich Domain Model:**

```java
// Rich domain object — owns its rules
public class BankAccount {
    private final UUID id;
    private Money balance;
    private AccountStatus status;
    private Money overdraftLimit;

    // No public setters — state changes only through methods
    public void withdraw(Money amount) {
        if (status == FROZEN) {
            throw new AccountFrozenException(id);
        }
        Money projected = balance.subtract(amount);
        if (projected.isLessThan(overdraftLimit.negate())) {
            throw new InsufficientFundsException(id, amount);
        }
        this.balance = projected;
    }

    public void freeze() {
        if (status == CLOSED) {
            throw new CannotFreezeClosedAccountException(id);
        }
        this.status = FROZEN;
    }
}
// Now TellerService just calls account.withdraw(amount)
// It CANNOT forget the rule — the rule is enforced by the object
```

---

### ⚖️ Comparison Table

| Approach                | Logic Location         | Encapsulation | Rule Duplication Risk | Best For                       |
| ----------------------- | ---------------------- | ------------- | --------------------- | ------------------------------ |
| **Anemic Domain Model** | Services               | None          | High                  | Simple CRUD, no business rules |
| Rich Domain Model       | Domain objects         | High          | Low                   | Complex business domains       |
| Transaction Script      | Procedure methods      | N/A           | High                  | One-off batch operations       |
| Active Record           | Object + some services | Partial       | Moderate              | Simple ORM patterns            |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Anemic model is bad, always use rich model"    | For simple CRUD, an anemic model is simpler and perfectly appropriate                                                                                  |
| "Service layer proves you have an anemic model" | Services coordinate use cases and infrastructure — they're needed even with rich domain models. The problem is services containing business invariants |
| "JPA forces anemic models"                      | JPA can work with rich domain models — use protected/package-private setters and constructor injection                                                 |
| "Anemic models are easier to test"              | Rich domain models are often easier to test — they're pure Java with no framework dependencies                                                         |

---

### 🚨 Failure Modes & Diagnosis

**Scattered Business Rules**

**Symptom:** The same business rule appears in multiple service classes with slight variations. Bugs are fixed in one place but recur because the rule exists elsewhere.

**Root Cause:** Anemic domain model — business logic lives in services, not domain objects. Multiple developers implement the same rule independently.

**Diagnostic Check:**

```bash
# Find all places that call setStatus on domain objects
# If there are more than 1-2 callers, logic is scattered
grep -rn "\.setStatus\|\.setState\|\.setAmount" \
  src/main/java/ --include="*.java" | grep -v "test"
```

**Fix:** Identify the canonical business rule, implement it as a method on the domain object, remove all external callers that replicate the logic.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Domain Model` — the rich alternative to the anemic model

**Builds On This:**

- `Rich Domain Model` — the solution that replaces the anemic model

**Alternatives:**

- `Transaction Script` — a legitimate alternative for simple domains
- `Active Record` — partial middle ground

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Domain objects with data only, no logic  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Yes — identified by Martin Fowler 2003   │
├──────────────┼───────────────────────────────────────────┤
│ ROOT CAUSE   │ Procedural thinking in OO clothing        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple CRUD, no meaningful business rules │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex domain with real business rules   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Objects that know nothing about         │
│              │  their own rules"                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team is debating whether to refactor a large existing codebase from an anemic model to a rich domain model. The codebase has 40 service classes, 20 domain entities, and 600 tests that test services. Refactoring would move logic from services into domain objects. What is the migration risk, and what strategy would you use to migrate safely without breaking the existing 600 tests?

**Q2.** A developer argues: "Our application is a form-based admin tool that does mostly CRUD — an anemic model is fine for us." Another developer argues: "Even CRUD apps get business rules added over time, so we should start with a rich model." Who is right, and what factors should guide the decision?
