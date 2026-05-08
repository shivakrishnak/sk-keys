---
layout: default
title: "SOLID Principles"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /software-architecture/solid-principles/
id: SAP-043
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming, Design Patterns, Dependency Injection
used_by: Object-oriented design, Code review, Refactoring, Architecture decisions
related: DRY, KISS, YAGNI, Law of Demeter, Clean Architecture, Dependency Injection
tags:
  - architecture
  - principles
  - oop
  - intermediate
  - design
---

# SAP-043 - SOLID Principles

⚡ TL;DR - SOLID is five object-oriented design principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) that together guide toward loosely coupled, maintainable, testable designs.

---

### 📊 Entry Metadata

| #756            | Category: Software Architecture Patterns                                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Design Patterns, Dependency Injection         |                 |
| **Used by:**    | Object-oriented design, Code review, Refactoring, Architecture decisions   |                 |
| **Related:**    | DRY, KISS, YAGNI, Law of Demeter, Clean Architecture, Dependency Injection |                 |

---

### 🔥 The Problem This Solves

**THE RIGID, FRAGILE CODEBASE:**
Code is hard to change: every change breaks something somewhere else. New features require modifying core code rather than extending it. Tests are impossible to write because classes have too many responsibilities and concrete dependencies. Adding a new payment method means editing five existing classes. This is code that violates SOLID.

**THE SOLID SOLUTION:**
Apply five principles consistently: each class has one reason to change (SRP); extend by adding new code rather than modifying old (OCP); implementations are substitutable for their abstractions (LSP); interfaces are focused, not bloated (ISP); depend on abstractions, not concretions (DIP). Applied together, these principles produce designs where changes are local, classes are testable, and the system can evolve without cascading breakage.

---

### 📘 Textbook Definition

SOLID is an acronym coined by Michael Feathers (based on principles by Robert C. Martin / "Uncle Bob") representing five principles of object-oriented class design: **S**ingle Responsibility Principle, **O**pen/Closed Principle, **L**iskov Substitution Principle, **I**nterface Segregation Principle, **D**ependency Inversion Principle. These principles are not independent rules but mutually reinforcing guidelines. Together they drive toward low coupling, high cohesion, and architecturally clean code. SOLID principles apply primarily to class-level design but scale to module and service boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Five principles that guide class design toward single-purpose, extensible, substitutable, focused, and abstraction-based code.

**One analogy:**

> SOLID is like the five building codes for a well-designed building: one use per room (SRP), add rooms without demolishing walls (OCP), rooms are interchangeable by function (LSP), doors only connect relevant rooms (ISP), rooms depend on standard utilities not specific pipes (DIP). A building that follows these codes is easier to renovate, extend, and adapt than one that doesn't.

**One insight:**
SOLID violations are symptoms of deeper design problems. Classes that are hard to test usually violate DIP. Changes that break many things usually violate OCP. Methods that only some subclasses can implement usually violate LSP. Recognizing which principle is violated points you toward the right fix.

---

### 🔩 First Principles Explanation

**THE FIVE PRINCIPLES:**

```
┌──────────────────────────────────────────────────────────┐
│                 SOLID OVERVIEW                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  S - Single Responsibility Principle (SRP)               │
│    A class should have ONE reason to change              │
│    = One responsibility, one cohesive purpose            │
│                                                          │
│  O - Open/Closed Principle (OCP)                         │
│    Open for EXTENSION, closed for MODIFICATION           │
│    = Add behavior via new code; don't edit existing code │
│                                                          │
│  L - Liskov Substitution Principle (LSP)                 │
│    Subtypes must be substitutable for their base types   │
│    = Implementations honor the full contract             │
│                                                          │
│  I - Interface Segregation Principle (ISP)               │
│    Clients should not depend on interfaces they don't use│
│    = Many small interfaces > one large interface         │
│                                                          │
│  D - Dependency Inversion Principle (DIP)                │
│    Depend on abstractions, not concretions               │
│    = High-level modules → interfaces ← low-level modules │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**RECOGNIZING VIOLATIONS:**

| Symptom                                                  | Likely SOLID violation                            |
| -------------------------------------------------------- | ------------------------------------------------- |
| Class has many unrelated public methods                  | SRP - too many responsibilities                   |
| Adding feature X requires editing class Y                | OCP - should extend, not modify                   |
| `throw new UnsupportedOperationException()` in subclass  | LSP - subtype doesn't honor base contract         |
| Implementing interface forces writing empty stub methods | ISP - interface too broad                         |
| Unit test requires real database or HTTP call            | DIP - depends on concretion, not abstraction      |
| Constructor takes `new DatabaseConnection()` directly    | DIP - creates own dependency instead of injecting |

---

### 🧠 Mental Model / Analogy

> SOLID principles applied to a Swiss Army knife vs specialized tools: The SRP says don't make a knife that's also a toothbrush and a flashlight (one tool, one job). The OCP says design the handle so new tools can be added without re-forging the handle. The LSP says any tool in the knife must fully do what a standalone tool would do. The ISP says don't require a knife user to grip the corkscrew handle just to use the blade. The DIP says the blade should fit any standard knife handle, not just one specific brand.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Five guidelines for writing classes that are easier to change, test, and extend.

**Level 2 - Per-principle examples (junior):**

**SRP**: `UserService` handles registration, profile updates, AND email sending → violates SRP. Split: `UserRegistrationService`, `UserProfileService`, `EmailNotificationService`.

**OCP**: `DiscountCalculator.calculate()` has `if (type == GOLD) ... else if (type == SILVER) ...` → violates OCP. Fix: `Discount` interface, `GoldDiscount`/`SilverDiscount` implementations, `DiscountCalculator` takes `Discount` (open for new discount types by adding class, not modifying calculator).

**LSP**: `Rectangle.setWidth(5)` guarantees `height` unchanged. `Square extends Rectangle` and overrides `setWidth(5)` to set both width and height. Code that works with `Rectangle` breaks with `Square`. Violation: `Square` is not a substitutable `Rectangle`. Fix: don't inherit; use composition or a common `Shape` interface.

**ISP**: `Worker` interface with `work()`, `eat()`, `sleep()`. `Robot implements Worker` - doesn't eat or sleep, forced to implement as empty stubs. Violation. Fix: `Workable` interface (work()), `Eatable` interface (eat()), `Sleepable` interface (sleep()).

**DIP**: `OrderService(new MySQLOrderRepository())` - hard-coded dependency on concrete class. Test requires MySQL database. Fix: `OrderService(OrderRepository repo)` where `OrderRepository` is an interface. Test injects `InMemoryOrderRepository`.

**Level 3 - SOLID at scale (mid-level):**
SOLID principles apply beyond classes. At module level: SRP → each module owns one domain; OCP → modules extend via plugins; LSP → services honor their API contracts regardless of implementation version; ISP → API clients receive only the data they need (BFF pattern); DIP → modules depend on abstractions (interfaces, events) not other modules' implementations. Architectures like Clean Architecture and Hexagonal Architecture are systematic applications of SOLID at system level.

**Level 4 - SOLID trade-offs (senior/staff):**
SOLID principles have costs. Over-application of OCP creates excessive abstraction layers; every simple change requires adding new classes. Over-application of ISP creates interface proliferation - dozens of single-method interfaces. SRP taken too far creates microservices-in-a-monolith: dozens of single-method service classes. The principles are heuristics, not laws. Apply them in response to pain: when changes are causing cascading breakage, apply OCP. When tests are hard to write, apply DIP. When a class is getting large and hard to understand, apply SRP. Don't preemptively abstract everything - let the code tell you when to refactor.

---

### ⚙️ How It Works (Mechanism)

**Dependency Inversion in depth (the most important principle):**

```
┌──────────────────────────────────────────────────────────┐
│        DEPENDENCY INVERSION - BEFORE vs AFTER            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  BEFORE (violates DIP):                                  │
│    OrderService → MySQLOrderRepository (concrete class)  │
│    High-level depends on low-level                       │
│    Cannot test OrderService without MySQL                 │
│                                                          │
│  AFTER (honors DIP):                                     │
│    OrderService → OrderRepository (interface)            │
│                        ↑                                 │
│                 MySQLOrderRepository                     │
│                 InMemoryOrderRepository (for tests)      │
│                                                          │
│    Both high-level (OrderService) and low-level          │
│    (MySQLOrderRepository) depend on the abstraction      │
│    (OrderRepository interface)                           │
│    Dependency direction inverted: plugin depends on core │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│          SOLID PRINCIPLES - MUTUAL REINFORCEMENT         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  SRP → small, focused classes                            │
│     → easier to satisfy ISP (small classes have          │
│       small interfaces)                                  │
│     → easier to satisfy OCP (small classes have          │
│       fewer reasons to change)                           │
│                                                          │
│  DIP → abstractions between modules                      │
│     → enables OCP (add new implementations without       │
│       modifying callers)                                 │
│     → enables testability (inject test doubles)          │
│                                                          │
│  LSP → reliable substitution                             │
│     → enables OCP (can substitute implementations        │
│       without modifying consuming code)                  │
│     → validates DIP (abstraction is only valuable        │
│       if implementations are interchangeable)            │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**DIP + OCP applied - payment processing:**

```java
// Abstraction (interface) - the stable contract
public interface PaymentGateway {
    PaymentResult charge(MoneyAmount amount,
                          PaymentToken token);
}

// Extension via new class (OCP): add Stripe without
// modifying OrderService
@Component
public class StripePaymentGateway
        implements PaymentGateway {
    @Override
    public PaymentResult charge(MoneyAmount amount,
                                 PaymentToken token) {
        // Stripe-specific implementation
    }
}

// High-level module depends on abstraction (DIP)
// Not on StripePaymentGateway directly
@Service
public class OrderService {
    private final PaymentGateway paymentGateway; // DIP

    @Autowired
    public OrderService(PaymentGateway gateway) {
        this.paymentGateway = gateway;
    }

    public OrderConfirmation placeOrder(Order order) {
        // OCP: works with any PaymentGateway implementation
        // no code change needed to support new gateway
        PaymentResult result = paymentGateway.charge(
            order.total(), order.paymentToken());
        ...
    }
}
```

---

### ⚖️ Comparison Table

| Principle | Guards against                      | Key benefit                     |
| --------- | ----------------------------------- | ------------------------------- |
| SRP       | Classes that do too much            | Localized change impact         |
| OCP       | Modification of tested code         | Extend by adding, not modifying |
| LSP       | Broken abstraction substitutability | Reliable polymorphism           |
| ISP       | Fat interfaces with unused methods  | Clients only see what they need |
| DIP       | Hardcoded concrete dependencies     | Testability + replaceability    |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                    |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| SRP means one method per class            | SRP means one reason to change, not one method - a class can have many methods if they all serve the same cohesive purpose |
| OCP means you never modify existing code  | OCP means you prefer extension over modification; sometimes direct modification is the right choice                        |
| LSP is just about not throwing exceptions | LSP covers the full behavioral contract: preconditions, postconditions, invariants - not just no exceptions                |
| SOLID is only for OOP                     | The principles generalize: SRP→module cohesion, OCP→plugin architecture, DIP→ports and adapters                            |

---

### 🚨 Failure Modes & Diagnosis

**Over-abstraction from premature SOLID application**

**Symptom:** Simple feature requires creating 5 new interfaces, 3 abstract classes, 2 factories, and a registry, just to add one new behavior.

**Root Cause:** SOLID applied preemptively before complexity justifies it ("speculative generality").

**Fix:** Apply SOLID reactively - in response to actual pain. When a change breaks other things → OCP. When tests require databases → DIP. When a class can't be summarized in one sentence → SRP. Don't abstract until you need to.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Object-Oriented Programming` - SOLID is specifically about OO class design

**Related:**

- `Clean Architecture` - Robert Martin's architecture applying SOLID at system level
- `DRY` - complementary principle about code duplication
- `Dependency Injection` - the implementation mechanism for DIP

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ S - SRP     │ One reason to change per class            │
├─────────────┼───────────────────────────────────────────┤
│ O - OCP     │ Extend (new code); don't modify (old code)│
├─────────────┼───────────────────────────────────────────┤
│ L - LSP     │ Subtypes fully substitutable for parents  │
├─────────────┼───────────────────────────────────────────┤
│ I - ISP     │ Small, focused interfaces; no fat APIs    │
├─────────────┼───────────────────────────────────────────┤
│ D - DIP     │ Depend on abstractions (interfaces),      │
│             │ not concretions (concrete classes)        │
└─────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a `ReportGenerator` class with methods: `generatePdfReport()`, `generateCsvReport()`, `emailReport()`, `archiveReport()`, and `logReportGeneration()`. Identify all the SOLID violations, name the principle each violates, and describe the refactored class design.

**Q2.** A `Bird` interface has methods `fly()` and `makeSound()`. A `Penguin` class implements `Bird` but its `fly()` method throws `UnsupportedOperationException`. Which SOLID principle is violated? What are two different ways to fix this design - one using interface segregation and one using a different inheritance hierarchy?
