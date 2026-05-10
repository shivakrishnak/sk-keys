---
id: SAP-007
title: SOLID Principles
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★☆
depends_on: SAP-012, SAP-048
used_by: SAP-035, SAP-036, SAP-045, SAP-046
related: SAP-035, SAP-036, SAP-045, SAP-046
tags:
  - architecture
  - principles
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /software-architecture/solid-principles/
  - design
---

# SAP-044 - SOLID Principles

⚡ TL;DR - SOLID is five object-oriented design principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) that together guide toward loosely coupled, maintainable, testable designs.

| Field          | Value                              |
| -------------- | ---------------------------------- |
| **Depends on** | SAP-012, SAP-048                   |
| **Used by**    | SAP-035, SAP-036, SAP-045, SAP-046 |
| **Related**    | SAP-035, SAP-036, SAP-045, SAP-046 |

---

### 🔥 The Problem This Solves

**THE RIGID, FRAGILE CODEBASE:**
Code is hard to change: every change breaks something somewhere else. New features require modifying core code rather than extending it. Tests are impossible to write because classes have too many responsibilities and concrete dependencies. Adding a new payment method means editing five existing classes. This is code that violates SOLID.

**THE SOLID SOLUTION:**
Apply five principles consistently: each class has one reason to change (SRP); extend by adding new code rather than modifying old (OCP); implementations are substitutable for their abstractions (LSP); interfaces are focused, not bloated (ISP); depend on abstractions, not concretions (DIP). Applied together, these principles produce designs where changes are local, classes are testable, and the system can evolve without cascading breakage.

**EVOLUTION:**
Robert C. Martin published the individual principles between 1994 and 2002 in various software engineering publications. Michael Feathers coined the SOLID acronym in 2004, giving the principles a memorable collective name. Martin's "Clean Code" (2008) brought SOLID to mainstream developers, and "Clean Architecture" (2017) elevated them to architectural principles. SOLID was formulated specifically for object-oriented design; the principles require adaptation for functional programming (where immutability replaces SRP/OCP in many cases) and for microservices (where SRP applies at service granularity). The SOLID principles remain the dominant design vocabulary for OOP code reviews and architecture discussions worldwide.

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

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Design software so that changes are local. A requirement change should require modifying exactly one unit of code (one class, one module, one service). When a single requirement change ripples through five files, the design is wrong.

**Where else this pattern appears:**

- **Electronics circuit design:** A well-designed circuit board separates concerns into components (capacitors, resistors, ICs) connected by a standard interface (electrical signals). Replacing one component doesn't require redesigning the board - this is OCP at the hardware level.
- **Restaurant kitchen stations:** A kitchen is organized by stations (grill, sauté, pastry), each with single responsibility. The grill cook doesn't know how to plate desserts. New menu items can be added to a single station without reorganizing the kitchen - SRP and OCP applied to kitchen design.
- **Legal code structure:** Laws are organized so that a change to tax law doesn't require changes to criminal law. Each legal domain has its own codification (SRP). New legal frameworks extend existing law without modifying it (OCP at societal scale).

---

### 💡 The Surprising Truth

SOLID principles were formulated for object-oriented class design but are often misapplied as absolute rules rather than design guidelines. The most commonly over-applied principle is SRP: developers create classes with only one method, producing hundreds of tiny classes that are impossible to understand in context. Robert Martin himself clarified that SRP means "one reason to change" - not "one method" or "one responsibility." A `Customer` class with 10 methods related to customer behavior has ONE reason to change (when customer business rules change). The correct application of SRP is about identifying cohesive groups of behaviors, not minimizing class size.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-012 - Cohesion (SRP is the object-level application of cohesion; understanding cohesion provides the conceptual foundation for SRP)
- SAP-048 - Coupling (DIP and ISP both reduce coupling; understanding coupling explains why these principles matter)

**Builds On This (learn these next):**

- SAP-035 - DRY (complementary principle about code duplication; DRY and SOLID often reinforce each other)
- SAP-036 - KISS (counterbalancing principle; SOLID without KISS leads to over-engineered abstractions)
- SAP-045 - YAGNI (another counterbalancing principle; DIP requires abstractions, YAGNI warns against premature abstraction)
- SAP-046 - Law of Demeter (closely related to ISP; LoD enforces low coupling at the method call level)

**Alternatives / Comparisons:**

- SAP-035 - DRY (complementary, not alternative; DRY governs code duplication, SOLID governs class design)
- Functional programming principles (immutability, pure functions, function composition) - alternative design principles for non-OOP code; SOLID doesn't translate directly to FP

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

_Hint:_ Research SRP violation: `ReportGenerator` has multiple reasons to change (report format changes, email provider changes, archive location changes, logging format changes). ISP violation: any caller that only needs `generatePdfReport()` must still depend on the interface that includes email and archiving. DIP violation: if the class directly instantiates concrete email and PDF libraries. Refactored: `PdfReportGenerator`, `CsvReportGenerator` (format); `EmailSender` (notification); `ReportArchiver` (storage); `ReportAuditLogger` (logging); an `ApplicationService` orchestrates them.

**Q2.** A `Bird` interface has methods `fly()` and `makeSound()`. A `Penguin` class implements `Bird` but its `fly()` method throws `UnsupportedOperationException`. Which SOLID principle is violated? What are two different ways to fix this design - one using interface segregation and one using a different inheritance hierarchy?

_Hint:_ Research LSP violation (Liskov Substitution Principle): code that uses `Bird bird = new Penguin()` and calls `bird.fly()` will throw an exception - the substitution breaks the caller's assumptions. ISP fix: split `Bird` into `FlyingBird` (with `fly()`) and `Bird` (with `makeSound()` only); `Penguin` implements `Bird` only. Inheritance hierarchy fix: `Animal` base with `makeSound()`; `FlyingAnimal extends Animal` adds `fly()`; `Penguin extends Animal` without `fly()`; `Eagle extends FlyingAnimal`.

**Q3.** A senior developer argues: "SOLID makes our codebase more complex. We have 47 interfaces for 47 classes - every interface has exactly one implementation. The indirection makes the code harder to read and debug. SOLID is causing more harm than good here." How do you evaluate this critique, and what counter-argument or agreement would you give?

_Hint:_ Research Robert Martin's response to this criticism - specifically the distinction between "incidental abstractions" (interfaces created just to follow SOLID rules) and "meaningful abstractions" (interfaces that represent conceptual boundaries or variation points). An interface with only one implementation that never changes is an incidental abstraction - it adds indirection without value. A `PaymentGateway` interface with one implementation TODAY but planned multiple implementations is a meaningful abstraction. The test: "If I remove this interface and use the concrete class directly, what would become harder?" If the answer is "nothing," the interface is not justified.
