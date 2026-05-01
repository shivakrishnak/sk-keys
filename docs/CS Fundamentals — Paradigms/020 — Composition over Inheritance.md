---
layout: default
title: "Composition over Inheritance"
parent: "CS Fundamentals — Paradigms"
nav_order: 20
permalink: /cs-fundamentals/composition-over-inheritance/
number: "20"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Inheritance, Encapsulation, Polymorphism, Object-Oriented Programming (OOP)
used_by: Design Patterns, Dependency Injection, Functional Programming
tags: #intermediate, #architecture, #pattern, #deep-dive
---

# 20 — Composition over Inheritance

`#intermediate` `#architecture` `#pattern` `#deep-dive`

⚡ TL;DR — Build complex behaviour by combining small, focused objects (has-a) rather than inheriting from a class hierarchy (is-a), favouring flexibility over code reuse via extension.

| #20             | Category: CS Fundamentals — Paradigms                                       | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Inheritance, Encapsulation, Polymorphism, Object-Oriented Programming (OOP) |                 |
| **Used by:**    | Design Patterns, Dependency Injection, Functional Programming               |                 |

---

### 📘 Textbook Definition

**Composition over Inheritance** is a design principle, articulated in the _Gang of Four_ book, stating that classes should achieve polymorphic behaviour and code reuse by composing objects (holding references to collaborators) rather than by extending a class hierarchy. Composition establishes a _has-a_ relationship and delegates behaviour to composed parts; inheritance establishes an _is-a_ relationship and inherits behaviour from a parent. Composition is preferred because it is more flexible (collaborators can be changed at runtime), avoids the fragile base class problem, does not expose internal parent state, and supports single-responsibility more naturally.

---

### 🟢 Simple Definition (Easy)

Instead of saying "a Car _is_ a Vehicle _is_ a Machine", say "a Car _has_ an engine, _has_ a transmission, _has_ wheels." Build it from parts rather than extending a chain.

---

### 🔵 Simple Definition (Elaborated)

Inheritance feels natural: a `Duck` extends `Animal`, reusing `name`, `age`, and `breathe()`. But when your hierarchy needs a flying duck, a rubber duck, and a wooden decoy duck, inheritance produces tangled trees of overrides and abstract methods. Composition solves this by letting objects hold references to helper objects that implement specific capabilities: a `Duck` has a `FlyBehaviour` (which might be `CanFly`, `CannotFly`, or `FliesWithRocket`). You change the duck's flying behaviour at runtime by swapping the `FlyBehaviour` object — something inheritance cannot do. This is the core of the _Strategy Pattern_, the _Decorator Pattern_, and Spring's entire component model.

---

### 🔩 First Principles Explanation

**The problem: inheritance hierarchies break when requirements change.**

Classic animal hierarchy:

```
Animal
├── FlyingAnimal
│   ├── Duck
│   └── Parrot
└── SwimmingAnimal
    ├── Duck    ← PROBLEM: Duck should be in BOTH subtrees
    └── Fish
```

A duck both flies and swims. Java's single inheritance cannot place `Duck` under two parents. The solution is either:

1. Duplicate code, or
2. Create a `FlyingSwimmingAnimal` class — what if we add running?

The hierarchy explodes with every new capability combination.

**The composition solution — behaviours as objects:**

```java
// Capabilities as interfaces
interface FlyBehaviour  { void fly(); }
interface SwimBehaviour { void swim(); }

// Implementations
class CanFly   implements FlyBehaviour  { public void fly()  { /* flap wings */ } }
class CanSwim  implements SwimBehaviour { public void swim() { /* paddle */ } }
class CannotFly implements FlyBehaviour { public void fly()  { /* do nothing */ } }

// Duck COMPOSES its behaviours — does not extend them
class Duck {
    private FlyBehaviour  flyBehaviour;  // has-a
    private SwimBehaviour swimBehaviour; // has-a

    Duck(FlyBehaviour f, SwimBehaviour s) {
        this.flyBehaviour  = f;
        this.swimBehaviour = s;
    }

    void fly()  { flyBehaviour.fly(); }   // delegate
    void swim() { swimBehaviour.swim(); } // delegate

    // RUNTIME CHANGE: swap behaviour without changing Duck class
    void setFlyBehaviour(FlyBehaviour f) { this.flyBehaviour = f; }
}

// Create variations without touching the hierarchy
Duck mallard     = new Duck(new CanFly(),    new CanSwim());
Duck rubberDucky = new Duck(new CannotFly(), new CanSwim());
```

New capability? Add an implementation class. No class hierarchy change required.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Composition (inheritance-only):

```java
// Attempting to model permissions via inheritance
class User { }
class AdminUser extends User { void deleteAll() {} }
class PremiumUser extends User { void export() {} }
// What about an AdminPremiumUser?
class AdminPremiumUser extends ??? {} // Java: no multiple class inheritance
// Forced to pick one, or create an explosion of combination subclasses
```

What breaks without it:

1. Java's single inheritance makes multi-capability combinations impossible without duplication.
2. Parent class changes (Fragile Base Class Problem) cascade to all children.
3. Subclasses expose all parent methods — even ones that make no sense for them.
4. You cannot change behaviour at runtime — inheritance is fixed at compile time.
5. Unit testing requires testing the whole inheritance chain, not just the unit.

WITH Composition:
→ Mix any combination of behaviours via constructor injection.
→ Behaviour changes at runtime — inject a different implementation.
→ Parent changes do not affect composed classes — they are independent.
→ Each behaviour class is independently testable.
→ Follows Single Responsibility — each class does one focused thing.

---

### 🧠 Mental Model / Analogy

> Think of building a character in a video game RPG. In a system based on inheritance, you would extend `Character` → `Warrior` → `HeavyWarrior` — but what if you want a warrior who can also cast spells, or a mage who can also pick locks? The class tree explodes. In a composition-based system, your character _has_ a weapon skill, _has_ a magic ability, _has_ a thieving skill. You equip and unequip capabilities at runtime. New abilities are new objects you attach — not new branches in a class tree.

"Character's equipped weapon skill" = composed behaviour object
"Changing equipped weapon" = swapping a composed collaborator at runtime
"Class tree for every combination" = inheritance explosion anti-pattern
"New ability as a new item" = new implementation of an interface

---

### ⚙️ How It Works (Mechanism)

**The core pattern — delegation:**

```
┌───────────────────────────────────────────────────────┐
│         Composition via Delegation                    │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │  Duck                                        │    │
│  │    - flyBehaviour:  FlyBehaviour  ──────────►│    │
│  │    - swimBehaviour: SwimBehaviour ──────────►│    │
│  │                                              │    │
│  │  fly()  → flyBehaviour.fly()                 │    │
│  │  swim() → swimBehaviour.swim()               │    │
│  └──────────────────────────────────────────────┘    │
│                                                       │
│   Duck DELEGATES to composed objects.                 │
│   Behaviour controlled by the injected impl.          │
└───────────────────────────────────────────────────────┘
```

**Strategy Pattern = Composition over Inheritance codified:**

```java
// Strategy: encapsulate interchangeable algorithms as objects
interface SortStrategy {
    <T extends Comparable<T>> void sort(List<T> list);
}

class QuickSort  implements SortStrategy { ... }
class MergeSort  implements SortStrategy { ... }
class BubbleSort implements SortStrategy { /* for small lists */ }

class DataSorter {
    private SortStrategy strategy; // composed

    DataSorter(SortStrategy strategy) { this.strategy = strategy; }

    // Swap algorithm at runtime
    void setStrategy(SortStrategy s) { this.strategy = s; }

    <T extends Comparable<T>> void sort(List<T> list) {
        strategy.sort(list); // delegate
    }
}
```

**Decorator Pattern = Composition for layered wrapping:**

```java
interface Logger { void log(String msg); }

class ConsoleLogger implements Logger {
    public void log(String msg) { System.out.println(msg); }
}

class TimestampLogger implements Logger {
    private final Logger delegate; // composed
    TimestampLogger(Logger delegate) { this.delegate = delegate; }

    public void log(String msg) {
        delegate.log(Instant.now() + " " + msg); // wrap and delegate
    }
}

// Chain decorators at runtime
Logger logger = new TimestampLogger(new ConsoleLogger());
logger.log("Order placed"); // → "2026-05-01T10:00:00Z Order placed"
```

---

### 🔄 How It Connects (Mini-Map)

```
Inheritance (is-a)
        │  ← limitations →
        ▼
Composition over Inheritance  ◄──── (you are here)
        │
        ├─────────────────────────────────────────────┐
        ▼                                             ▼
Strategy Pattern                           Decorator Pattern
(swap algorithms via composition)         (layer behaviour via composition)
        │                                             │
        ▼                                             ▼
Dependency Injection                      Functional Programming
(compose via injected collaborators)      (compose via function combination)
```

---

### 💻 Code Example

**Example 1 — Replacing an inheritance hierarchy with composition:**

```java
// INHERITANCE version — hierarchy explosion
class Report { String render() { return ""; } }
class HtmlReport  extends Report { ... }
class CsvReport   extends Report { ... }
class EncryptedHtmlReport extends HtmlReport { ... } // explosion
class CompressedCsvReport extends CsvReport  { ... } // explosion

// COMPOSITION version — combine independently
interface Formatter  { String format(ReportData data); }
interface Encryptor  { String encrypt(String content); }
interface Compressor { byte[] compress(String content); }

class ReportGenerator {
    private final Formatter formatter;
    private final Encryptor encryptor;   // optional
    private final Compressor compressor; // optional

    // Any combination works via constructor injection
    ReportGenerator(Formatter f, Encryptor e, Compressor c) {
        this.formatter  = f;
        this.encryptor  = e;
        this.compressor = c;
    }
}
// New format? New Formatter. No hierarchy changes.
```

**Example 2 — Spring's component model (composition everywhere):**

```java
// Spring injects composed collaborators — no inheritance needed
@Service
public class OrderService {
    private final OrderRepository  repository; // has-a
    private final PaymentGateway   payment;    // has-a
    private final NotificationPort notifier;   // has-a

    // Spring injects implementations at startup
    OrderService(OrderRepository r, PaymentGateway p,
                 NotificationPort n) {
        this.repository = r;
        this.payment    = p;
        this.notifier   = n;
    }

    public void placeOrder(Order order) {
        repository.save(order);
        payment.charge(order);
        notifier.notify(order);
    }
}
// Swap any collaborator for testing or feature-flag rollout
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                               |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Composition over inheritance means never use inheritance | Inheritance is correct for genuine is-a relationships with stable hierarchies (e.g., Exception hierarchies, JPA entities). The principle targets misuse of inheritance for code reuse |
| Composition always requires more classes                 | Composition adds behaviour classes, but eliminates combinatorial subclass explosion; the net class count is often lower for complex feature sets                                      |
| Interfaces are the same as composition                   | Interfaces define the contract; composition is the _use_ of that contract by holding a reference to an object implementing it                                                         |
| Composition cannot achieve polymorphism                  | Polymorphism via composition is achieved through interface references — `FlyBehaviour flyBehaviour` is polymorphic regardless of whether `CanFly` or `CannotFly` is assigned          |

---

### 🔥 Pitfalls in Production

**Over-engineering with composition when inheritance is simpler**

```java
// BAD: composition for a trivially stable hierarchy
interface LogLevel  { String levelName(); }
class InfoLevel     implements LogLevel { ... }
class DebugLevel    implements LogLevel { ... }
// ... just to avoid extending a 2-level enum-like hierarchy

// GOOD: use a sealed class or enum for stable, closed sets
enum LogLevel { INFO, DEBUG, WARN, ERROR }
// Composition is not always better — evaluate the actual stability
```

---

**Composed collaborators not replaced in tests — hidden coupling**

```java
// BAD: default collaborator is a real HTTP client
class PricingService {
    private final ExchangeRateClient client =
        new HttpExchangeRateClient(); // fixed — cannot be replaced in tests

    double convert(double amount, String currency) {
        return amount * client.getRate(currency); // calls real HTTP in tests!
    }
}

// GOOD: inject the collaborator — testable and swappable
class PricingService {
    private final ExchangeRateClient client; // injected

    PricingService(ExchangeRateClient client) { this.client = client; }
    // Tests inject FakeExchangeRateClient — no HTTP needed
}
```

---

### 🔗 Related Keywords

- `Inheritance` — the principle composition is preferred over for reuse without a genuine is-a relationship
- `Strategy Pattern` — the canonical design pattern implementing composition over inheritance
- `Decorator Pattern` — layered behaviour wrapping via composition
- `Dependency Injection` — the mechanism that delivers composed collaborators to their consumers
- `Polymorphism` — composition achieves polymorphism via interfaces, not class hierarchy
- `Single Responsibility Principle` — composition naturally leads to classes with one focused role
- `Functional Programming` — FP takes this further: functions are composed, never extended

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Hold references to collaborators (has-a)  │
│              │ rather than extending parent classes      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Capabilities combine in multiple ways;    │
│              │ behaviour needs to change at runtime;     │
│              │ inheritance hierarchy is unstable         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Genuine is-a relationship with a stable,  │
│              │ shallow hierarchy (2–3 levels)            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Inherit what you ARE; compose what you   │
│              │ DO — and most things you DO can change."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → Decorator Pattern →    │
│              │ Dependency Injection → SOLID Principles   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `ApplicationContext` wire up beans via composition: a `UserService` has a `UserRepository`, a `PasswordEncoder`, and an `EventPublisher` — all injected. At runtime, each of these can be a different implementation. Contrast this with a hypothetical design where `UserService` extends `BaseUserService` which extends `AbstractService`. Identify three concrete production scenarios where the composition model makes a critical operational task (feature flag, blue-green deploy, A/B test) straightforward, and explain why the inheritance model makes the same task difficult or impossible.

**Q2.** The Gang of Four _Decorator Pattern_ and the _Inheritance_ pattern both add behaviour to an existing type. A `TimestampLogger` wrapping a `FileLogger` wrapping a `ConsoleLogger` chains three loggers via composition. Describe the precise order of execution when `logger.log("event")` is called on the outermost decorator, and explain what would happen to this execution order if `TimestampLogger` instead extended `FileLogger` — covering both the method resolution mechanism and the implications for adding a fourth logging layer.
