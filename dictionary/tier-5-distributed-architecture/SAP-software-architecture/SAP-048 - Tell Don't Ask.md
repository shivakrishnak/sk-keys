---
id: SAP-048
layout: default
title: "Tell Don't Ask"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /software-architecture/tell-dont-ask/
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-043, SAP-047
used_by: 
related: SAP-047, SAP-049
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
---

# SAP-048 - Tell Don't Ask

⚡ TL;DR - Tell Don't Ask (TDA) states that you should tell objects what to do rather than asking for their state and making decisions externally - behavior should be in the class that owns the data, not scattered in callers.

---
id: SAP-048

### 🔥 The Problem This Solves

**THE OUTSIDE-DECISION PROBLEM:**

```java
// Anemic pattern: ask, then decide externally
if (order.getStatus() == OrderStatus.PENDING &&
    order.getPaymentStatus() == PaymentStatus.CONFIRMED) {
    order.setStatus(OrderStatus.PROCESSING);
    order.setProcessedAt(Instant.now());
    inventory.reserve(order.getItems());
}
```

The logic for "when an order can move to PROCESSING" lives in the caller (`OrderService`), not in `Order`. Every service that needs to make this decision duplicates or re-implements this logic. The `Order` class is just a data bag - an Anemic Domain Model. When the business rule changes (e.g., also require address verification), every caller must be updated.

**THE TELL DON'T ASK SOLUTION:**

```java
// Tell the order to process itself
order.startProcessing(inventory);
```

`Order.startProcessing()` encapsulates the rule: check status, check payment, update status, set timestamp, trigger inventory reservation. Callers tell `Order` what to do. `Order` knows whether it can do it and how.

**EVOLUTION:** Tell Don't Ask was articulated by Andy Hunt and Dave Thomas (The Pragmatic Programmers) in their influential "Pragmatic Programmer" book (1999) and later refined in their columns and essays. The principle gained renewed importance in the 2000s with the formalization of the Anemic Domain Model anti-pattern by Martin Fowler (2003), which named the exact failure mode TDA prevents. Domain-Driven Design (Evans, 2003) built on TDA as a core principle of rich domain models. The pattern experienced a backlash with the rise of functional programming (2010s), where immutable data structures and pure functions deliberately separate data from behavior - TDA applies specifically to object-oriented designs where encapsulation is the primary tool for managing complexity. (The Pragmatic Programmers), stated as: "Tell objects what you want them to do; don't ask them questions about their state, make a decision, and then tell them what to do." The principle is the behavioral complement to encapsulation: encapsulation says hide data, TDA says hide decisions. Data and the logic that operates on that data belong together in the same class. If you find yourself asking an object for data, making a decision based on that data, and then acting on the object, the decision should be inside the object.

---
id: SAP-048

### ⏱️ Understand It in 30 Seconds

**One line:**
Move the "if/then" decision inside the object that owns the data - callers say what should happen, not how to check if it should.

**One analogy:**

> You don't ask your car "are your wheels turning and is the engine running?" and then press the accelerator. You press the accelerator and the car decides how to respond (engine power, gear, fuel injection). The car encapsulates the "how" of going faster. You just tell it what you want: go faster. The car, not you, makes the implementation decisions.

**One insight:**
Anemic Domain Models are a systemic violation of Tell Don't Ask. When a class has only getters/setters and all business logic is in service classes that manipulate the data objects, every piece of business logic is "asking" for state and deciding externally. Moving business logic into the domain model (Rich Domain Model) is the systematic application of TDA.

---
id: SAP-048

### 🔩 First Principles Explanation

**ASK vs TELL PATTERNS:**

```
┌──────────────────────────────────────────────────────────┐
│           ASK PATTERN (TDA VIOLATION)                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. ASK about state: order.getStatus()                   │
│  2. DECIDE externally: if (status == PENDING && ...)     │
│  3. TELL what to set: order.setStatus(PROCESSING)        │
│                                                          │
│  Problems:                                               │
│  - Decision logic in caller, not in Order                │
│  - Multiple callers may duplicate/contradict the logic   │
│  - Order's internal consistency is caller's responsibility│
│  - Refactoring Order's internals breaks callers          │
│                                                          │
│         ─────────────────────────────                    │
│                                                          │
│           TELL PATTERN (TDA COMPLIANT)                   │
│                                                          │
│  1. TELL the object: order.startProcessing(inventory)    │
│                                                          │
│  Order internally:                                       │
│  - Checks its own preconditions                          │
│  - Makes the decision                                    │
│  - Updates its own state                                 │
│  - Coordinates with collaborators                        │
│                                                          │
│  Caller is decoupled from Order's internal logic         │
└──────────────────────────────────────────────────────────┘
```

**TELL DON'T ASK APPLIED TO STATE MACHINES:**

```
┌──────────────────────────────────────────────────────────┐
│     ORDER STATE MACHINE - ASK vs TELL                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ASK (violation): External state machine logic           │
│                                                          │
│  if (order.getStatus() == DRAFT) {                       │
│    if (order.getItems().isEmpty()) {                     │
│      throw new InvalidOrderException();                  │
│    }                                                     │
│    order.setStatus(SUBMITTED);                           │
│    order.setSubmittedAt(Instant.now());                  │
│  }                                                       │
│  // In OrderService                                      │
│                                                          │
│  TELL (compliant): State machine inside Order            │
│                                                          │
│  order.submit(); // Order handles the state transition   │
│  // Order internally: check items, check status,         │
│  // set SUBMITTED, set submittedAt, publish event        │
│  // Order owns its state machine                         │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-048

### 🧪 Thought Experiment

**RICH DOMAIN MODEL = TELL DON'T ASK:**

The difference between Anemic and Rich Domain Models is fundamentally about TDA.

| Anemic Model (ASK)                             | Rich Model (TELL)                                   |
| ---------------------------------------------- | --------------------------------------------------- |
| `order.getStatus()` then `if (...)` in service | `order.submit()` - order decides validity           |
| `account.getBalance()` then check in service   | `account.withdraw(amount)` - account enforces rules |
| `user.getRole()` then check in controller      | `user.canAccessResource(resource)` - user decides   |

The Rich Model **tells** objects to do things. The Anemic Model **asks** for data and does things to objects. TDA is the reason to prefer Rich Domain Models.

---
id: SAP-048

### 🧠 Mental Model / Analogy

> Tell Don't Ask is like a good manager versus a micromanager. A micromanager asks the employee "what's your current task status?" then "what are the next three steps?" then "do step one." A good manager tells the employee: "Complete the user login feature by Friday." The employee knows their own state (current task, dependencies, blockers) and manages their own work. The manager gets results without needing to know all the implementation details.

---
id: SAP-048

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Instead of getting data from an object and making decisions yourself, tell the object what you want accomplished and let it decide how.

**Level 2 - How to apply it (junior):**
Spot TDA violations: whenever you write `object.getSomething()` and use the result in an `if/else` that then calls `object.setSomethingElse()`, the if/else likely belongs inside the object. Refactoring: move the conditional and the resulting action into a new method on the object. The method name should describe the intent: `order.submit()`, `account.withdraw(amount)`, `user.grantAccess(resource)`. The object verifies preconditions internally, performs the action, and throws an exception (or returns an error result) if the action isn't valid.

**Level 3 - TDA with return values (mid-level):**
TDA creates a design tension with functional-style code that chains transformations. Returning values is fine - asking for a value to pass to another method is fine. The violation is: asking for a value, making a decision, and then telling the object to change state based on your decision. `order.getTotal()` to display in a UI is fine. `order.getStatus()` to decide whether to call `order.setStatus(NEXT_STATE)` is a TDA violation - the state transition belongs in Order. The functional/immutable style avoids TDA violations differently: instead of `order.setStatus()`, return a new order: `order.submit()` returns a new `Order` with `SUBMITTED` status.

**Level 4 - TDA in domain-driven design (senior/staff):**
TDA is the behavioral specification of Domain-Driven Design's Rich Domain Model. In DDD: Aggregate Roots (like `Order`) are responsible for their own invariants. The rule "an Order can only be submitted if it has at least one item and payment is confirmed" is an invariant of `Order`. `Order.submit()` enforces this invariant by checking preconditions internally and throwing a domain exception if violated. External code (application services) TELLS aggregates to perform commands; it doesn't ask for internal state to decide whether a command is valid. This keeps business rules in the domain model, not scattered in application services. When rules change, one change - in the aggregate - is sufficient.

---
id: SAP-048

### ⚙️ How It Works (Mechanism)

**Preconditions in Tell Don't Ask:**

```
┌──────────────────────────────────────────────────────────┐
│      TELL DON'T ASK - PRECONDITION HANDLING              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  When caller TELLS object to do something, the object:   │
│                                                          │
│  1. Checks its own preconditions                         │
│     (is this action valid in the current state?)         │
│                                                          │
│  2a. If valid: perform the action; update state          │
│                                                          │
│  2b. If invalid: throw domain exception                  │
│      (describing what's wrong, not how to fix it)        │
│                                                          │
│  Caller handles success or catches domain exception       │
│  Caller does NOT pre-check validity - that's the         │
│  object's job                                            │
│                                                          │
│  Exception: UX validation (check before trying)          │
│  Use a separate canDo() query: order.canSubmit()         │
│  But the definitive check still happens in submit()      │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-048

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│      TELL DON'T ASK - COMPLETE EXAMPLE                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Application Service (tells):                            │
│    order.submit(paymentGateway, inventoryService);       │
│                                                          │
│  Order.submit() (handles internally):                    │
│    - Guard: this.status == DRAFT? else throw             │
│    - Guard: this.items.notEmpty()? else throw            │
│    - Charge payment: paymentGateway.charge(this.total)   │
│    - Reserve stock: inventoryService.reserve(this.items) │
│    - Update state: this.status = SUBMITTED               │
│    - Record: this.submittedAt = Instant.now()            │
│    - Publish: this.events.add(new OrderSubmitted(this))  │
│                                                          │
│  All business rules in ONE place: Order.submit()         │
│  App service knows NOTHING about how submission works    │
│  Change submission rules → change Order.submit() only    │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-048

### 💻 Code Example

```java
// ASK violation - submission logic in application service
@Service
public class OrderApplicationService {
    public void submitOrder(OrderId orderId) {
        Order order = orderRepo.findById(orderId);

        // Asking and deciding externally (TDA violation)
        if (order.getStatus() != OrderStatus.DRAFT) {
            throw new IllegalStateException(
                "Cannot submit non-draft order");
        }
        if (order.getItems().isEmpty()) {
            throw new IllegalStateException(
                "Cannot submit empty order");
        }
        if (!order.getPaymentMethod().isValid()) {
            throw new IllegalStateException(
                "Invalid payment method");
        }
        order.setStatus(OrderStatus.SUBMITTED);
        order.setSubmittedAt(Instant.now());
        orderRepo.save(order);
    }
}

// ─────────────────────────────────────────────────────────

// TELL DON'T ASK - logic inside Order aggregate
public class Order {
    // private fields - callers cannot inspect internals
    private OrderStatus status;
    private List<OrderItem> items;
    private PaymentMethod paymentMethod;
    private Instant submittedAt;

    // TELL: caller says "submit", Order handles HOW
    public void submit() {
        // Object checks its own preconditions
        if (status != OrderStatus.DRAFT) {
            throw new OrderAlreadySubmittedException(id);
        }
        if (items.isEmpty()) {
            throw new EmptyOrderException(id);
        }
        if (!paymentMethod.isValid()) {
            throw new InvalidPaymentMethodException(id);
        }

        // Object manages its own state transition
        this.status = OrderStatus.SUBMITTED;
        this.submittedAt = Instant.now();
        // Publish domain event (TDA: aggregate tells)
        registerEvent(new OrderSubmitted(this.id));
    }
}

// Application service: thin - just TELLS the aggregate
@Service
public class OrderApplicationService {
    public void submitOrder(OrderId orderId) {
        Order order = orderRepo.findById(orderId);
        order.submit(); // One line - tells, doesn't ask
        orderRepo.save(order);
    }
}
```

---
id: SAP-048

### ⚖️ Comparison Table

| Pattern                | Decision location | State change owner | Best for                               |
| ---------------------- | ----------------- | ------------------ | -------------------------------------- |
| **Tell Don't Ask**     | Inside the object | The object itself  | Rich domain models, stateful entities  |
| Ask pattern            | In the caller     | The caller         | Simple DTOs, query-only objects        |
| Functional (immutable) | In the caller     | Returns new value  | Functional code, value transformations |

---
id: SAP-048

### ⚠️ Common Misconceptions

| Misconception                       | Reality                                                                                                                                              |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| TDA means never use getters         | TDA means don't use getters for decision-making about the object's own state; query getters (for display, reporting) are fine                        |
| TDA only applies to OOP             | TDA is an OOP principle; functional programming achieves the same goal differently (pass behavior, not state)                                        |
| TDA conflicts with CQRS queries     | CQRS query handlers read state - that's fine. TDA applies to command handling where you modify state                                                 |
| TDA means objects can't collaborate | Objects can call methods on other objects (their direct collaborators); they just shouldn't expose their internal state for external decision-making |

---
id: SAP-048

### 🚨 Failure Modes & Diagnosis

**Anemic model with procedural service layer**

**Symptom:** Domain objects have only getters, setters, and no business logic. All business logic is in `*Service` classes that manipulate domain objects.

**Root Cause:** Systematic TDA violation - the service layer asks all objects for their state, makes all decisions, and calls setters.

**Fix:** Gradually move business logic from services into domain objects. Start with the most self-contained rules (order state machine, account balance checks). Introduce domain methods (`order.submit()`, `account.withdraw()`) and have services call them instead of managing state directly. This is the "Rich Domain Model" refactoring.

---
id: SAP-048

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The class that owns the data should own the decisions about that data. External decision-making on another class's data is the root cause of both duplicated logic and fragile coupling to internal state.

**Where else this pattern appears:**

- **Medical diagnosis:** A doctor (the object) decides on treatment based on their own assessment of your condition (their data). You don't tell the doctor "your diagnosis showed X and Y, therefore apply treatment Z" - you tell the doctor "I have these symptoms" and the doctor decides. TDA at the human expert level.
- **ATM machines:** You tell the ATM "withdraw £200"; the ATM decides whether to allow it based on its own balance information, daily limit rules, and PIN verification. You don't ask the ATM for your balance, check it against your daily limit yourself, and tell it to dispense - the ATM encapsulates that decision.
- **Smart home automation:** You tell the thermostat "I want 22°C"; the thermostat manages heating and cooling decisions. You don't ask for current temperature, calculate when to turn on heating, and send a command. The thermostat owns its data and behavior.

---
id: SAP-048

### 💡 The Surprising Truth

Tell Don't Ask and functional programming's separation of data and behavior are fundamentally at odds - and both are correct in their respective contexts. TDA says: put behavior in the class that owns the data (OOP enriched domain model). Functional programming says: keep data structures pure and separate from the functions that operate on them (data + pure functions). The resolution: TDA applies in OOP domain models where object identity, lifecycle, and consistency invariants matter (your bank account MUST enforce its own balance rules). FP separation applies in data transformation pipelines where the same data needs to be processed by many different functions without coupling them to each other. Choosing between OOP TDA and FP data separation is one of the most important architectural decisions in system design.

---
id: SAP-048

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-043 - SOLID Principles (SRP: TDA violations scatter related logic across callers; SRP says cohesive logic belongs in one class; TDA is the behavioral application of SRP)
- SAP-047 - Law of Demeter (LoD and TDA address the same problem from different angles: LoD says don't navigate to distant objects; TDA says don't ask for state and decide externally; applying both together eliminates most structural coupling)

**Builds On This (learn these next):**

- SAP-049 - Command-Query Separation (CQS complements TDA: commands tell objects to do things and return nothing; queries ask objects about their state; TDA says commands are always preferable to ask-and-then-command sequences)

**Alternatives / Comparisons:**

- Anemic Domain Model (the anti-pattern TDA prevents: data classes with no behavior, all logic in services; appropriate for functional/CQRS architectures, wrong for OOP rich domain models)
- Rich Domain Model (the result of consistently applying TDA; all domain logic in the domain objects; the object-oriented answer to the anemic domain model)

---
id: SAP-048

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Tell objects what to do, don't ask for   │
│              │ their state to decide yourself           │
├──────────────┼───────────────────────────────────────────┤
│ VIOLATION    │ getX() → if (...) → setY() in caller    │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Move if/then into the object as a method │
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFIT  │ Business rules in ONE place:             │
│              │ the class that owns the relevant data    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Good manager: tells you to complete     │
│              │  the feature. Micromanager: asks about   │
│              │  every step."                             │
└──────────────────────────────────────────────────────────┘
```

---
id: SAP-048

### 🧠 Think About This Before We Continue

**Q1.** You have a `BankAccount` class with `getBalance()` and `setBalance()`. A `TransferService` does: `if (from.getBalance() >= amount) { from.setBalance(from.getBalance() - amount); to.setBalance(to.getBalance() + amount); }`. Rewrite this to follow Tell Don't Ask. What method(s) do you add to `BankAccount`, what do they do internally, and what does `TransferService.transfer()` look like after the refactoring?

*Hint:* Research the Tell Don't Ask refactoring: `BankAccount.debit(amount)` throws `InsufficientFundsException` if balance < amount, otherwise decrements; `BankAccount.credit(amount)` increments. `TransferService.transfer()` calls `from.debit(amount)` then `to.credit(amount)`. The business rule "balance must be sufficient" moves into `BankAccount` where the data lives. Key insight: `setBalance()` disappears entirely - no external caller should ever set a balance directly; only domain operations (`debit`, `credit`, `refund`) mutate balance.

**Q2.** Tell Don't Ask says put decisions in the object. But you're building a UI form that needs to show/hide a "Submit Order" button based on whether the order can be submitted. If the decision is inside `order.submit()`, how do you let the UI know whether submission is currently possible - without duplicating the business rule logic?

*Hint:* Research two patterns: (1) `order.canSubmit(): boolean` - a Query that exposes the submittability condition without mutating state; the UI calls `canSubmit()` to set button state. This is CQS-compliant (read-only) and TDA-compliant (the rule lives in Order). (2) Domain events: the Order publishes an `OrderSubmittabilityChanged` event when its state changes; the UI subscribes and updates the button. Pattern 1 is simpler for most cases; Pattern 2 is better for reactive UIs with complex state machines.

**Q3.** A team applies Tell Don't Ask strictly and moves all business logic into domain objects. After 6 months, the `Order` class has 45 methods, 18 fields, and 700 lines of code. Unit testing it requires setting up 8 collaborators. Has TDA been applied correctly? What is the alternative design when a domain object grows to this complexity?

*Hint:* Research the distinction between "rich domain model" and "god object" - when an object accumulates ALL behavior related to its concept, it violates SRP (multiple reasons to change). The fix: decompose the `Order` object using Domain-Driven Design's aggregate pattern. `Order` (aggregate root) delegates to `OrderItems` (value object), `PaymentInformation` (entity), `ShippingDetails` (value object). Each sub-component has its own TDA-compliant methods. The `Order` root coordinates but doesn't contain all logic itself. Research how the DDD aggregate pattern imposes natural size limits on domain objects.
