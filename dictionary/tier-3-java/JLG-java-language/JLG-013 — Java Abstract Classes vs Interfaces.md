---
layout: default
title: "Java Abstract Classes vs Interfaces"
parent: "Java & JVM Internals"
nav_order: 13
permalink: /java/java-abstract-classes-vs-interfaces/
id: JLG-013
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Java Language, Inheritance, Polymorphism
used_by: Design Patterns, Spring Core, Java Language
related: Composition over Inheritance, SOLID Principles, Strategy Pattern
tags:
  - java
  - jvm
  - intermediate
  - pattern
---

# JLG-013 — Java Abstract Classes vs Interfaces

⚡ TL;DR — Abstract classes provide shared implementation and state via single inheritance; interfaces define behaviour contracts supporting multiple type inheritance.

| Attribute | Value |
|---|---|
| **Depends on** | Java Language, Inheritance, Polymorphism |
| **Used by** | Design Patterns, Spring Core, Java Language |
| **Related** | Composition over Inheritance, SOLID Principles, Strategy Pattern |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Without abstraction mechanisms, code duplication proliferates — every class reimplements the same base behaviour. Without interfaces, you cannot write methods that accept any object satisfying a contract regardless of its class hierarchy. Without abstract classes, partial implementations must be copied across unrelated concrete classes.

**THE BREAKING POINT:** A banking system has `SavingsAccount` and `CheckingAccount`. Both share 80% of the same transaction logic but differ in interest calculation. Without a shared abstraction, any bug fix must be applied twice. Worse, a `PaymentProcessor` that should work with any account type has no type to program against.

**THE INVENTION MOMENT:** Java provided two complementary mechanisms: abstract classes for "is-a" relationships with shared implementation, and interfaces for "can-do" contracts that any class can satisfy. Java 8 added default methods to interfaces, blurring the boundary — but the fundamental design intent remains distinct.

---

### 📘 Textbook Definition

An **abstract class** in Java is a class declared with the `abstract` keyword that may contain a mix of abstract methods (no body) and concrete methods (with body), as well as instance fields and constructors. It cannot be instantiated directly. It enforces single-class inheritance via `extends`.

An **interface** in Java is a reference type that defines a pure contract: abstract methods that implementing classes must provide, plus (since Java 8) `default` methods with implementations and `static` methods. Since Java 9, interfaces can have `private` methods. A class implements an interface with `implements` and may implement multiple interfaces simultaneously.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Abstract class = partial blueprint (share state + behaviour); Interface = pure contract (declare capability, not implementation).

> An abstract class is the building code for a residential neighbourhood — all houses must have a roof and a door (enforced shared structure), but each house can vary its interior. An interface is a trade certification — any entity (person, company, robot) that passes the electrical inspection can be called a certified electrician, regardless of what else they are.

**One insight:** Prefer interfaces when defining capabilities that cut across type hierarchies. Use abstract classes when you have shared state or a common partial implementation that subclasses genuinely need to inherit.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Abstract class — single inheritance only (`extends`); can have fields, constructors, and fully implemented methods
2. Interface — multiple implementation (`implements`); prior to Java 8 had no implementation; from Java 8 allows `default` and `static` methods
3. A class can extend ONE abstract class but implement MANY interfaces
4. Interfaces define type — `instanceof` checks pass for any implementing class
5. `abstract` methods in either construct have no body; subclass/implementor must provide one

**DERIVED DESIGN:** The distinction maps to two different OO relationships: abstract class → IS-A (a `CheckingAccount` IS-A `BankAccount`); interface → CAN-DO (a `CheckingAccount` CAN-DO `Transferable`, `Auditable`). Java's single-inheritance constraint for classes prevents the Diamond Problem while interfaces with default methods have a defined resolution rule (class > interface; more-specific interface > less-specific).

**THE TRADE-OFFS:**
- **Gain (abstract):** Shared state, template method pattern, encapsulated default behaviour, constructors
- **Cost (abstract):** Burns the single inheritance slot; tight coupling between superclass and subclasses
- **Gain (interface):** Multiple types, loose coupling, mockable in tests, retroactively addable
- **Cost (interface):** No shared state; `default` methods can create diamond ambiguity; cannot have constructors

---

### 🧪 Thought Experiment

**SETUP:** Design a notification system with `EmailNotifier`, `SmsNotifier`, and `PushNotifier`.

**WHAT HAPPENS WITH ONLY ABSTRACT CLASS:** You create `AbstractNotifier` with shared logging and retry logic. But `SmsNotifier` must extend `AbstractNotifier` — it can no longer extend your existing `ThirdPartyIntegration` base class. You've used up the single inheritance slot. Adding `Auditable` behaviour requires duplicating code across all three notifiers.

**WHAT HAPPENS WITH INTERFACE + ABSTRACT CLASS:** Define `Notifier` interface for the contract. Create `AbstractNotifier` abstract class that implements `Notifier` and provides shared retry logic. Each concrete class extends `AbstractNotifier` and also implements additional interfaces (`Auditable`, `Retryable`) freely. The `NotificationService` depends only on `Notifier` — decoupled from all implementations.

**THE INSIGHT:** Use the interface to define the contract, the abstract class to provide the shared implementation, and let concrete classes inherit from the abstract class. This is the Template Method pattern and matches how Java's own `AbstractList`, `AbstractMap`, and `AbstractSet` are designed.

---

### 🧠 Mental Model / Analogy

> Think of an abstract class as a partially-built house template provided to a contractor: it has foundations and load-bearing walls already in place (concrete methods), but the contractor must complete the rooms (abstract methods). The contractor can only build one house from this template at a time (single inheritance). An interface is a building permit specification: any structure — house, warehouse, office building — must meet these standards (fire exits, electrical rating), but the structure is built entirely independently.

- Abstract class → partially-built template: shared foundation, one-time use
- Interface → permit specification: any structure can comply, many permits at once
- `default` methods → prefabricated modules: snap-in fittings that any building may optionally override

Where this analogy breaks down: in Java, a class implementing an interface that has a `default` method gets a working implementation for free — unlike a permit, which only sets requirements without providing materials.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An abstract class is a half-finished class that other classes complete. An interface is a list of methods that a class promises to provide. Use abstract classes to share code; use interfaces to share contracts.

**Level 2 — How to use it (junior developer):**
Declare `abstract class Animal { abstract String sound(); String breathe() { return "oxygen"; } }`. Subclasses extend it and must implement `sound()`. Declare `interface Flyable { void fly(); }`. Any class — `Bird`, `Airplane`, `Superhero` — implements it regardless of their class hierarchy. Prefer `interface` as the default; use `abstract class` only when you have common fields or a shared partial implementation.

**Level 3 — How it works (mid-level engineer):**
The JVM represents abstract classes and interfaces differently in bytecode. An abstract class compiles to a normal `.class` file with `ACC_ABSTRACT` set in the access flags. Interface methods are `ACC_INTERFACE | ACC_ABSTRACT`. When the JVM resolves a virtual method call (`invokevirtual` for classes, `invokeinterface` for interfaces), `invokeinterface` was historically slower because the JVM couldn't assume a fixed vtable slot. Modern JVMs (HotSpot) optimise both via inline caches, erasing most of the difference. Java 8 `default` methods are resolved by a specific order: class method > most-specific interface > compile error on unresolvable diamond.

**Level 4 — Why it was designed this way (senior/staff):**
Java's single-inheritance-of-implementation constraint was a deliberate response to C++'s diamond inheritance problem. The interface-only multiple inheritance avoids the ambiguity of two parent classes both providing a field with the same name. Java 8's `default` methods were added primarily to evolve the Collections API (`Collection.stream()`, `Iterable.forEach()`) without breaking every existing implementation. This was a pragmatic compromise; Scala `trait`s and Kotlin interfaces took a more powerful approach. The canonical Java design pattern (Interface → Abstract → Concrete) mirrors how the JDK itself is structured: `List` → `AbstractList` → `ArrayList`.

---

### ⚙️ How It Works (Mechanism)

**Type hierarchy and dispatch:**
```
┌────────────────────────────────────────────────┐
│  interface Notifier                            │
│      void send(Message m);                     │
│      default void retry(Message m) { ... }     │
│             ↑                                  │
│  abstract class AbstractNotifier              │
│      implements Notifier                       │
│      private final Logger log;  ← has state   │
│      void logSend(Message m) { ... } ← shared │
│      abstract String format(Message m); ← tmpl│
│             ↑              ↑                   │
│  EmailNotifier         SmsNotifier             │
│  implements Auditable  implements Auditable    │
└────────────────────────────────────────────────┘
```

**Diamond default method resolution (Java 8+):**
```
interface A { default void hello() { "A" } }
interface B extends A { default void hello() { "B" }}
class C implements A, B → uses B.hello() (more specific)
class D implements A, B, overrides hello() → D wins
class E implements A, B (no override, equal specificity)
  → compiler error: must override hello() explicitly
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Template Method via abstract class):**
```
Client calls notifier.send(msg)
       ← YOU ARE HERE
  │
  ├─ AbstractNotifier.send(msg) [concrete]
  │      ├─ log.info("Sending...")
  │      ├─ String formatted = format(msg)
  │      │       ↑ ABSTRACT — dispatched to subclass
  │      │       └─ EmailNotifier.format(msg)
  │      └─ dispatch(formatted)
  │
  └─ Result returned to client
```

**FAILURE PATH:**
- Forgot to implement abstract method → compile error (correct behaviour)
- Diamond default method ambiguity → compile error, must explicitly override
- Abstract class constructor throws → subclass constructor fails silently mid-chain

**WHAT CHANGES AT SCALE:**
- Spring proxies work on interfaces by default (JDK dynamic proxy); abstract class requires CGLIB byte-buddy proxy
- Interfaces are easier to mock (`Mockito.mock(Notifier.class)`) without `CGLIB`
- Abstract classes with protected fields create tight coupling — subclasses break when superclass refactors

---

### 💻 Code Example

**BAD — abstract class used where interface is correct; tight coupling:**
```java
// BAD: using abstract class for a cross-cutting
// capability → burns single-inheritance slot
abstract class Auditable {
    abstract void logAction(String action);
}

// EmailNotifier can't now extend anything else
class EmailNotifier extends Auditable {
    void logAction(String a) { System.out.println(a);}
}
```

**GOOD — interface for contract, abstract class for template:**
```java
// GOOD: interface defines the contract
public interface Notifier {
    void send(Message message);

    default boolean isEnabled() { return true; }
}

// GOOD: abstract class provides shared implementation
public abstract class AbstractNotifier
        implements Notifier {

    private final NotifierConfig config;

    protected AbstractNotifier(NotifierConfig cfg) {
        this.config = Objects.requireNonNull(cfg);
    }

    // Template method: subclass provides step
    protected abstract String format(Message msg);

    @Override
    public void send(Message message) {
        if (!isEnabled()) return;
        String formatted = format(message); // hook
        doSend(config.getEndpoint(), formatted);
    }

    private void doSend(String endpoint, String msg) {
        // shared dispatch logic
    }
}

// GOOD: concrete class is lean
public class EmailNotifier extends AbstractNotifier
        implements Auditable {

    public EmailNotifier(NotifierConfig cfg) {
        super(cfg);
    }

    @Override
    protected String format(Message msg) {
        return "<html>" + msg.body() + "</html>";
    }

    @Override
    public void audit(String action) { /* impl */ }
}

// GOOD: client depends only on interface
public class AlertService {
    private final Notifier notifier; // not concrete!

    public AlertService(Notifier notifier) {
        this.notifier = notifier;
    }
}
```

---

### ⚖️ Comparison Table

| Feature | Abstract Class | Interface (Java 8+) |
|---|---|---|
| Instance fields | Yes | No (only `static final` constants) |
| Constructors | Yes | No |
| Concrete methods | Yes | `default` only |
| Multiple inheritance | No (single `extends`) | Yes (multiple `implements`) |
| State sharing | Yes | No |
| Access modifiers on methods | Any | `public` or `private` (Java 9+) |
| Can be instantiated | No | No |
| Can extend/implement | Extends one class; implements interfaces | Extends multiple interfaces |
| Use for | Shared implementation + state | Type contract, multiple type |
| Mock in tests | Harder (CGLIB required) | Easy (JDK proxy) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Interfaces can have no implementation | Since Java 8, interfaces can have `default` methods with full implementations; since Java 9, also `private` helper methods |
| Abstract classes are always better for code reuse | Abstract classes couple subclasses to a superclass; composition via interfaces often produces more maintainable code |
| `default` methods make interfaces equivalent to abstract classes | Interfaces still cannot have instance fields, constructors, or `protected` methods — these remain exclusive to abstract classes |
| You should always prefer interfaces over abstract classes | When there is genuinely shared state or a partial implementation that all subclasses need, abstract class is the right tool |
| Implementing an interface is slower than extending a class | `invokeinterface` was historically slower; modern JVM inline caches make the difference negligible in practice |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Fragile base class problem**

**Symptom:** A change to the abstract class (adding a method, changing a field) silently breaks one or more subclasses — they call `super.method()` and receive unexpected behaviour.

**Root Cause:** Subclasses depend on the superclass's internal implementation. The superclass method that the subclass overrides calls other methods on `this`, which are themselves overridden — unexpected polymorphic dispatch within the superclass.

**Diagnostic:**
```bash
# Identify all subclasses of the abstract class
grep -rn "extends AbstractNotifier" src/
# Review each override for super() calls and
# assumptions about superclass call order
```

**Fix:**
```java
// BAD: send() calls format() which is overridden
// AbstractNotifier.send() expects format() to be
// safe to call before config is validated —
// subclass breaks this assumption

// GOOD: document method contracts with @implSpec
/**
 * @implSpec Implementations must not call
 * any other instance methods on 'this'.
 */
protected abstract String format(Message msg);
```

**Prevention:** Follow Bloch's advice: "Design and document for inheritance, or prohibit it." Use `final` on concrete methods in abstract classes that subclasses must not override.

---

**Mode 2: Diamond default method compile error**

**Symptom:** `error: class X inherits unrelated defaults for method() from types A and B`

**Root Cause:** Two interfaces both declare a `default` method with the same signature. The implementing class did not override to resolve the ambiguity.

**Diagnostic:**
```bash
javac -verbose MyClass.java 2>&1 | grep "inherits"
# Compiler message identifies the conflicting interfaces
```

**Fix:**
```java
// BAD: compile error — unresolved diamond
interface A { default void hello() { System.out.println("A"); } }
interface B { default void hello() { System.out.println("B"); } }
class C implements A, B { } // ERROR

// GOOD: explicit override resolves ambiguity
class C implements A, B {
    @Override
    public void hello() {
        A.super.hello(); // explicitly delegate to A
    }
}
```

**Prevention:** When introducing a `default` method to a widely-implemented interface, search the codebase for naming conflicts before releasing.

---

**Mode 3: Spring proxy failure on abstract class dependency**

**Symptom:** `@Transactional` or `@Cacheable` annotation on a method in an abstract class has no effect — the behaviour is not applied.

**Root Cause:** Spring's default proxy mechanism (JDK dynamic proxy) only works on interfaces. When a bean's type is an abstract class and the client holds a reference to the concrete subclass type, CGLIB subclass proxy is needed — but may not be enabled.

**Diagnostic:**
```bash
# Check proxy type in Spring context
grep -rn "proxyTargetClass\|@EnableAspectJAutoProxy" src/
# Or at runtime:
System.out.println(bean.getClass().getName());
# If it contains "CGLIB" or "EnhancerBy" → CGLIB active
```

**Fix:**
```java
// BAD: client depends on concrete type, no interface
@Service
class ReportService extends AbstractService { ... }

@Autowired
ReportService svc; // Spring can't proxy interface

// GOOD: program to interface → JDK proxy works
@Service
class ReportService extends AbstractService
        implements ReportPort { ... }

@Autowired
ReportPort svc; // JDK dynamic proxy applied cleanly
```

**Prevention:** Always inject Spring beans by interface type. Enable `@EnableAspectJAutoProxy(proxyTargetClass=true)` when CGLIB proxying of class types is genuinely required.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Java Language — class declarations, `extends`, `implements`, polymorphism
- Inheritance — IS-A relationship, method overriding, virtual dispatch
- Polymorphism — runtime dispatch, subtype substitution

**Builds On This (learn these next):**
- Design Patterns — Template Method (abstract class), Strategy (interface), Decorator (interface + composition)
- Spring Core — how Spring proxies interface vs class beans; `@Component` hierarchy
- SOLID Principles — Interface Segregation Principle, Liskov Substitution, Dependency Inversion

**Alternatives / Comparisons:**
- Composition over Inheritance — favour delegating to a collaborator over extending an abstract class
- Strategy Pattern — replaces inheritance-based variation with interface-based delegation
- Kotlin sealed classes / `open` — Kotlin's explicit opt-in model for class hierarchy design

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════════════╗
║ WHAT IT IS   │ Two Java abstraction mechanisms     ║
║ PROBLEM      │ Code duplication vs type coupling   ║
║ KEY INSIGHT  │ Interface = contract; Abstract =    ║
║              │ shared implementation + state       ║
║ USE WHEN     │ Abstract: shared state + template   ║
║              │ Interface: multiple type contracts  ║
║ AVOID WHEN   │ Abstract: no shared state needed    ║
║ TRADE-OFF    │ Code reuse vs coupling flexibility  ║
║ ONE-LINER    │ implements Interface,               ║
║              │ extends AbstractBase               ║
║ NEXT EXPLORE │ Template Method, Composition,       ║
║              │ SOLID Principles                   ║
╚════════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(C — Design Trade-off)** Java 8 added `default` methods to interfaces specifically to evolve the `Collection` API without breaking existing implementations. What were the alternatives (versioned interfaces, separate utility classes, extension methods), and what long-term design costs did the `default` method approach introduce?

2. **(F — Comparison)** Kotlin's `interface` supports `abstract` properties and default implementations much like Java 8+, but Kotlin also has `open class` and `sealed class`. Under what circumstances would you choose a Kotlin `sealed class` hierarchy over a Java-style `abstract class` hierarchy, and what does this reveal about the underlying design intent?

3. **(A — System Interaction)** Spring's `@Transactional` works by creating a proxy around your bean. If your `@Service` extends an `AbstractService` that itself has `@Transactional` methods, and your concrete service overrides those methods without re-annotating, describe what happens to transaction propagation and why the proxy type (JDK vs CGLIB) matters in this scenario.
