---
id: CSF-040
title: Interfaces vs Abstract Classes
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-015, CSF-016
used_by: SPR-001, DPT-004
related: CSF-041, CSF-037, JLG-005
tags: [interfaces, abstract-classes, default-methods, multiple-inheritance, contract]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/csf/interfaces-vs-abstract-classes/
---

⚡ TL;DR - Interfaces define contracts (what); abstract
classes provide partial implementations (how). Java supports
one abstract class but many interfaces. Default methods
(Java 8+) blur the line. Rule: prefer interfaces for
type contracts, abstract classes for shared state/template.

| #040 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-015 (Polymorphism), CSF-016 (Encapsulation) | |
| **Used by:** | SPR-001 (Spring Beans), DPT-004 (Template Method Pattern) | |
| **Related:** | CSF-041 (Composition over Inheritance), JLG-005 (Java OOP) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Early languages with only concrete inheritance: every class
that wants to share behavior must inherit from a concrete
parent. The parent class grows: it becomes a monolith
with behavior for all subclasses. Subclasses inherit
behavior they do not need. The hierarchy becomes rigid:
you cannot extend a class that already has a parent (no
multiple inheritance in Java). A `Bird` that needs to be
both a `FlyingThing` and a `SwimmableThing` cannot inherit
from both.

**THE BREAKING POINT:**

In enterprise Java systems, a class often plays multiple
roles: a `UserService` is a `Repository`, a `Cacheable`,
an `Auditable`, a `Serializable`. With single inheritance
only, you can only inherit from one parent. The other
contracts must be satisfied by code repetition or by
putting all the behavior in one huge class.

**THE INVENTION MOMENT:**

Java's answer: separate the CONTRACT (interface) from
the IMPLEMENTATION (abstract class). An interface says
"you must be able to do X" without specifying HOW.
An abstract class says "here is HOW to do some things;
fill in the rest." Java allows multiple interface
implementation but only single class inheritance. This
design reflects the philosophy: a class can play many
ROLES (interfaces) but has only one IDENTITY (class).
Java 8 (2014) added default methods to interfaces,
allowing behavior in interfaces without breaking existing
implementations - enabling interface evolution.

---

### 📘 Textbook Definition

**Interface:** A pure contract. Specifies methods a class
must implement. Java 8+: can have `default` methods (with
implementation) and `static` methods. Java 9+: `private`
methods. No instance state (fields). No constructor.
A class can implement any number of interfaces.

**Abstract class:** A class with one or more abstract methods
(no implementation). Provides partial implementation.
Can have instance fields, constructor, concrete methods.
A class can extend only ONE abstract class.

**Key distinction:**
Interface = "IS-CAPABLE-OF" (can fly, can serialize, can cache).
Abstract class = "IS-A" with partial template (an animal that has a name and can eat, but specific animals define their sound).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Interface: the contract of what. Abstract class: the partial
implementation of how. A class can implement many interfaces
but extend only one abstract class.

**One analogy:**

> Interface = a job description. "Must be able to drive,
> must have a license." Any person who meets these requirements
> qualifies - regardless of their background.
>
> Abstract class = a partially-built house with a foundation
> and plumbing but no walls. The builder who extends it
> fills in the walls. They can only be in ONE house at a
> time (single inheritance).

**One insight:**

Spring Beans are interfaces. `ApplicationContext`, `BeanFactory`,
`Repository`, `Service` - all interfaces. Spring's core is
built on interfaces so that different implementations can
be swapped: `JdbcTemplate` uses `DataSource` (interface),
not `HikariDataSource` (concrete). You inject the interface;
the actual implementation is resolved at runtime by Spring.
This is the Interface Segregation Principle + Dependency
Inversion in action. Abstract classes are used for template
implementations: `AbstractController`, `AbstractJpaRepository`
provide shared behavior that concrete implementations extend.

---

### 🔩 First Principles Explanation

**STRUCTURAL DIFFERENCES:**

```
┌──────────────────────────────────────────────────────┐
│ INTERFACE:                                           │
│   + Multiple implementation allowed                  │
│   + Only constants (static final) as fields          │
│   + No constructor                                   │
│   + All methods implicitly public                    │
│   + default methods: provided implementation         │
│   + static methods: utility methods                  │
│   + Cannot maintain state between calls (no fields)  │
│                                                      │
│ ABSTRACT CLASS:                                      │
│   + Only one extension allowed (single inheritance)  │
│   + Instance fields with any access level            │
│   + Constructor (called by subclass via super())     │
│   + Can mix abstract and concrete methods            │
│   + Can maintain state (instance fields)             │
│   + Any access level on methods                      │
└──────────────────────────────────────────────────────┘
```

**THE DEFAULT METHOD DIAMOND PROBLEM:**

```java
interface A { default String hello() { return "A"; } }
interface B extends A { default String hello() { return "B"; } }
interface C extends A { default String hello() { return "C"; } }

class D implements B, C {
    // Compile error: ambiguous - B and C both provide hello()
    // Must override to resolve:
    @Override
    public String hello() {
        return B.super.hello(); // explicitly choose B's implementation
    }
}
```

---

### 🧪 Thought Experiment

**EVOLVING AN INTERFACE WITHOUT BREAKING CLIENTS:**

Java 7 and earlier: if you add a method to a published
interface, ALL implementing classes must implement the
new method or compilation fails. With a library used by
thousands of classes, this is a breaking change.

Java 8 solution: `default` method. `interface Collection`
adds `stream()` as a default method returning `Collection.
stream(this)`. Existing implementations automatically
get the `stream()` method - they just use the default.
If they want different behavior, they override it.

**THE LESSON:**

`default` methods solved the "interface evolution" problem:
adding behavior to an interface without forcing all
implementing classes to change. Spring's `Repository`
interfaces, Java's `List` and `Collection`, all gained new
functionality in Java 8 via default methods without breaking
existing code. The boundary between interface and abstract
class blurred: a Java 8+ interface can provide significant
behavior via default methods. The remaining distinction:
interfaces have NO instance state (no fields), abstract
classes can have state. State is the last frontier of
the interface/abstract class divide.

---

### 🎯 Mental Model / Analogy

**USB PORTS AND DEVICE BATTERIES:**

Interface: a USB standard (USB-C). Any device that implements
the standard can be charged from any compatible charger.
The standard defines the protocol (contract); it does not
care how the device stores the charge. A phone can implement
USB-C AND Bluetooth AND NFC - multiple standards at once.

Abstract class: a specific phone model's circuit board.
It provides the base hardware (battery, screen connection,
CPU) and the phone manufacturer fills in the specific
design. You can only inherit ONE board design - you cannot
combine a Pixel board with a Galaxy board.

**MEMORY HOOK:**

"Interface = contract, multiple, no state.
Abstract class = template, single, has state.
Java 8: default methods give interfaces behavior.
Rule: prefer interfaces. Use abstract class when shared
state or construction is needed. Never inherit just
for code reuse - compose instead."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
An interface is a list of things something MUST be able to do.
An abstract class is a half-finished blueprint that subclasses
complete. A class can follow many lists of rules but can only
start from one half-finished blueprint.

**Level 2 - Student:**
`interface Flyable { void fly(); }` - any class can implement
this and provide `fly()`. `abstract class Vehicle { abstract void move(); String brand; }` -
every Vehicle has a brand and can move; subclasses define HOW they move.
A `FlyingCar` can implement `Flyable` AND extend `Vehicle` - multiple
interfaces, one abstract class.

**Level 3 - Professional:**
Interface default methods enable mixin behavior:
`interface Auditable { default void audit(String action) { AuditLog.record(this, action); } }`.
Any class implementing `Auditable` gets the `audit()` method for free.
This is behavior injection without inheritance. Functional interfaces
(`@FunctionalInterface`) have exactly one abstract method - they can
be used as lambda targets. `Runnable`, `Callable`, `Comparator` are
functional interfaces.

**Level 4 - Senior Engineer:**
Interface segregation principle (ISP, SOLID): prefer many small,
specific interfaces over one large interface. A `UserRepository`
implementing one `DataRepository<T>` monster interface is bad.
Better: `UserRepository extends ReadRepository<User>, WriteRepository<User>`.
Some callers only need read; they inject `ReadRepository<User>`.
They do not see or depend on write methods. Spring Data's `CrudRepository`,
`JpaRepository` are examples: progressively larger interfaces
with increasing functionality. Callers inject the narrowest
interface they need.

**Level 5 - Expert:**
The Template Method Pattern (GoF) is implemented with abstract
classes. `AbstractList` in Java defines `add(int index, E)` as
abstract and implements `add(E)` in terms of it:
`public boolean add(E e) { add(size(), e); return true; }`.
The concrete subclass defines the one abstract method; the abstract
class provides all derived behavior. This is the Inversion of Control
at the class level: the abstract class calls the subclass's method.
The risk: fragile base class problem. If `AbstractList.add(E)`
changes its implementation, all subclasses are affected.
With interfaces + default methods, the fragile base class
problem is reduced because default methods do not share state
with implementations.

---

### ⚙️ How It Works (Formal Basis)

**METHOD RESOLUTION ORDER:**

```
┌──────────────────────────────────────────────────────┐
│ When multiple inheritance paths conflict in Java:    │
│                                                      │
│ PRIORITY (highest to lowest):                        │
│ 1. Concrete class method                             │
│ 2. More-specific interface default (inherits via     │
│    interface that extends the providing interface)   │
│ 3. Less-specific interface default                   │
│ 4. Compiler error (ambiguous - must override)        │
│                                                      │
│ Example:                                             │
│   interface A { default void foo() {...} }           │
│   interface B extends A { default void foo() {...} } │
│   class C implements A, B {}                         │
│   // C.foo() = B.foo() - B is more specific than A  │
│                                                      │
│   interface A { default void foo() {...} }           │
│   interface B { default void foo() {...} }           │
│   class C implements A, B {}                         │
│   // Compile error - must override in C              │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 System Design Implications

**DEPENDENCY INVERSION:**

Code to interfaces, not implementations. A service that
depends on `OrderRepository` (interface) can be tested
with a mock `OrderRepository`. The concrete `JpaOrderRepository`
is injected at runtime by Spring. Changing the persistence
mechanism (from JPA to Redis) requires only a new `OrderRepository`
implementation - the service is unchanged.

If the service depends on `JpaOrderRepository` (concrete),
it is coupled to JPA. A change to the repository layer
requires changing the service. Testing requires a real JPA
setup. Interfaces break this coupling.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Inheritance for Code Reuse**

```java
// BAD: using inheritance for code reuse (not IS-A)
abstract class LoggingBase {
    protected void log(String message) {
        System.out.println(message);
    }
}

class OrderService extends LoggingBase {
    // OrderService IS-NOT-A LoggingBase!
    // Using inheritance just to get log() - wrong
    void placeOrder(Order order) {
        log("Order placed: " + order.id());
    }
}

// GOOD: use composition + interface for capabilities
interface Loggable {
    default void log(String message) {
        System.out.println("[" + getClass().getSimpleName() + "] " + message);
    }
}

class OrderService implements Loggable {
    void placeOrder(Order order) {
        log("Order placed: " + order.id());  // from Loggable default
    }
}
// OR: inject a Logger (composition over mixin):
class OrderService {
    private final Logger log = LoggerFactory.getLogger(OrderService.class);
    void placeOrder(Order order) { log.info("Order placed: {}", order.id()); }
}
```

**Example 2 - Template Method Pattern with Abstract Class**

```java
// Abstract class: defines template (algorithm skeleton)
abstract class DataProcessor {
    private final DataStore store;

    DataProcessor(DataStore store) { this.store = store; } // state!

    // Template method: algorithm skeleton
    final void process(List<RawData> data) {
        List<RawData> filtered = filter(data);    // abstract
        List<Result> results = transform(filtered); // abstract
        store.save(results);                       // concrete (uses state)
        notify(results);                           // concrete
    }

    abstract List<RawData> filter(List<RawData> data);
    abstract List<Result> transform(List<RawData> data);

    private void notify(List<Result> results) {
        results.forEach(r -> log.info("Processed: {}", r));
    }
}

// Concrete subclass: fills in the abstract parts
class OrderProcessor extends DataProcessor {
    OrderProcessor(DataStore store) { super(store); }

    @Override
    List<RawData> filter(List<RawData> data) {
        return data.stream().filter(d -> d.type().equals("ORDER")).toList();
    }

    @Override
    List<Result> transform(List<RawData> data) {
        return data.stream().map(OrderProcessor::toResult).toList();
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Interface | Abstract Class |
|---|---|---|
| Multiple inheritance | Yes (implement many) | No (extend only one) |
| Instance state (fields) | No (only static final constants) | Yes (any access level) |
| Constructor | No | Yes (called via `super()`) |
| Method implementations | `default` methods only (Java 8+) | Mix of abstract and concrete |
| Access level of methods | All public (implicitly) | Any (public, protected, private) |
| IS-A vs IS-CAPABLE-OF | IS-CAPABLE-OF (roles, contracts) | IS-A (partial identity) |
| Use for | Contracts, type bounds, DI | Template method, shared state |
| Functional interface | Yes (`@FunctionalInterface`) | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Interfaces can have no implementation | Java 8+ interfaces can have `default` methods (full implementation) and `static` utility methods. Java 9+ can have `private` helper methods. Interfaces can provide significant behavior. The difference from abstract classes: they CANNOT have instance state (fields). |
| Abstract classes are obsolete since Java 8 | No. Abstract classes remain the correct choice when: (1) you need instance state (fields) shared across subclasses, (2) you need constructor initialization logic, (3) you want the template method pattern with non-public methods, (4) the subclasses have a genuine IS-A relationship, not just IS-CAPABLE-OF. |
| A class should implement as many interfaces as possible | Implementing many interfaces that the class does not genuinely represent makes the class's contract confusing. A class implementing 15 interfaces likely violates the Single Responsibility Principle. Interfaces should be narrow (Interface Segregation); classes should implement only the interfaces they genuinely fulfill. |
| `default` methods replaced the abstract class for behavior sharing | `default` methods solve the interface evolution problem (adding methods without breaking existing implementations). They are NOT a replacement for abstract class template method patterns. `default` methods cannot access instance state; abstract class concrete methods can. They serve different purposes. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Diamond Problem with Default Methods**

**Symptom:** Compilation error: "class D inherits unrelated
defaults for `foo()` from types B and C."

**Root Cause:** D implements B and C; both B and C provide
a `default foo()` with no inheritance relationship between
them. The JVM cannot choose without guidance.

**Fix:** Override `foo()` in D and explicitly choose:
```java
@Override
public String foo() {
    return B.super.foo(); // explicitly pick B's default
    // or: new combination of both
}
```

**Failure Mode 2: Extending Abstract Class Breaks Open/Closed**

**Symptom:** Changing a `protected` method in an abstract
class breaks several concrete subclasses that depended
on its previous behavior.

**Root Cause:** The abstract class (fragile base class) has
`protected` methods that subclasses call or override.
Changes to the base class propagate to all subclasses.

**Fix:** Keep abstract class `protected` methods truly
internal (do not call them from subclasses unless necessary).
Prefer composition for shared behavior that may change.
Document which methods are part of the extension contract
and which are implementation details.

---

**Security Note:**

When designing security-sensitive abstractions, prefer
interfaces over abstract classes for the TYPE BOUNDARY
that security checks go on. Reason: if a security check
is implemented in an abstract class method that subclasses
can override (or bypass by not calling `super()`), the
security guarantee is fragile. If the security check is
implemented in an interface `default` method that is final
(interfaces cannot have `final` default methods, but the
method is the default for all implementors), subclasses
do not inherit it automatically.
Better approach: security checks in FINAL methods or
via Spring AOP/method security that cannot be bypassed
by inheritance. Never rely on overridable abstract class
methods for security enforcement.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - interfaces and abstract classes are
  OOP concepts; class/object model is prerequisite
- `Polymorphism` (CSF-015) - both interfaces and abstract
  classes are mechanisms for polymorphic behavior
- `Encapsulation` (CSF-016) - interfaces control the
  visible contract; abstract classes encapsulate shared state

**Builds On This (learn these next):**
- `Composition over Inheritance` (CSF-041) - the principle
  that favors interface + composition over abstract class extension
- `Design Patterns` (DPT-004) - Template Method requires
  abstract class; Strategy and other patterns favor interfaces

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ INTERFACE    │ Contract. No state. Multiple implement. │
│              │ default methods (Java 8+): behavior     │
│              │ @FunctionalInterface: lambda target     │
├──────────────┼─────────────────────────────────────────┤
│ ABSTRACT     │ Template. Has state. Single extend.     │
│ CLASS        │ Mix abstract + concrete methods         │
│              │ Constructor for shared initialization   │
├──────────────┼─────────────────────────────────────────┤
│ RULE OF THUMB│ Interface: FIRST choice (IS-CAPABLE-OF) │
│              │ Abstract: only when state/template needed│
├──────────────┼─────────────────────────────────────────┤
│ DIAMOND FIX  │ Both provide default foo()? Must override│
│              │ Use B.super.foo() to explicitly choose  │
├──────────────┼─────────────────────────────────────────┤
│ ISP (SOLID)  │ Many small interfaces > one large one   │
│              │ Inject the narrowest interface needed   │
├──────────────┼─────────────────────────────────────────┤
│ DIP (SOLID)  │ Depend on interface, not implementation │
│              │ Spring DI: inject interface, not class  │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-041 (Composition), DPT-004 (Template)│
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Interface = contract (WHAT), no state, multiple allowed.
   Abstract class = template (PARTIAL HOW), can have state,
   only one allowed. Java 8+ default methods give interfaces
   behavior - but not state. State is the key remaining
   distinction.
2. Prefer interfaces for type contracts and dependency injection.
   `OrderService` depends on `OrderRepository` (interface),
   not `JpaOrderRepository` (class). This enables testing,
   swapping implementations, and Spring DI. Use abstract
   classes when subclasses need shared state or template
   method pattern.
3. Interface Segregation Principle: prefer narrow, focused
   interfaces over fat ones. Clients inject only the
   capabilities they need. `ReadRepository<T>` vs `WriteRepository<T>`
   instead of one `Repository<T>` with all operations.

**Interview one-liner:**
"Interfaces define contracts - what a class must do, not how.
Abstract classes provide partial implementations - what is
shared and what subclasses must complete. Java allows multiple
interface implementation but only single class inheritance.
Java 8 default methods added behavior to interfaces, but
they still cannot have instance state. Rule: prefer interfaces
for type contracts and DI; use abstract classes for template
method patterns and shared state."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The interface/abstract class distinction is a manifestation
of the Dependency Inversion Principle (DIP) and Interface
Segregation Principle (ISP) from SOLID: depend on abstractions
(interfaces), not concretions. Define the minimum interface
a client needs; do not expose the full concrete class.
This principle appears throughout system design: REST APIs
expose contracts (routes/schemas), not implementation.
gRPC defines protobuf service interfaces, not the server
implementation. Event schemas define what fields an event
contains, not how they are produced. Microservice boundaries
ARE interface definitions: the API contract is all that
is shared; the implementation is hidden. The interface/abstract
class distinction in OOP is the class-level instance of
a universal design principle.

**Where else this pattern appears:**

- **`java.util.List` vs `ArrayList`** - Java's Collections
  Framework is built on interfaces: `List`, `Map`, `Set`,
  `Queue`. The concrete implementations (`ArrayList`, `HashMap`,
  `LinkedList`) are almost never used as the declared type.
  `List<String> list = new ArrayList<>()` not `ArrayList<String>`.
  This enables switching from `ArrayList` to `LinkedList`
  by changing one constructor call. All code that uses `list`
  is unaffected.
- **Spring Boot auto-configuration** - Spring Boot uses
  interfaces to detect capabilities. `DataSource` is an
  interface. If a bean of type `DataSource` is in the context,
  Spring auto-configures JPA. It does not care if the DataSource
  is `HikariDataSource` or `SimpleDriverDataSource`. The
  interface IS the detection boundary.
- **Kubernetes Pod vs PodSpec** - Kubernetes defines resource
  interfaces (the spec) separately from the resource state
  (the actual running pod). The controller receives the
  desired spec (interface) and reconciles it with actual state.
  This IS the interface/implementation separation at the
  infrastructure level.

---

### 💡 The Surprising Truth

Java's single inheritance restriction (only one class parent)
was a deliberate choice to avoid the "deadly diamond of
death" - the C++ multiple inheritance problem where `class D
extends B, C` and both B and C inherit from A leads to two
copies of A's state in D, with ambiguous resolution.
Java's designers banned multiple class inheritance entirely.
But this created the problem: how do you give a class multiple
BEHAVIORS? The answer was interfaces. But then interfaces
could not have behavior (pre-Java 8), which created the need
for the Adapter and Strategy patterns (add behavior via
composition, not inheritance). Java 8 added default methods
to interfaces specifically to allow evolving library interfaces
without breaking existing implementations (the `stream()`
method on `Collection`). This single feature (default methods)
then enabled a partial solution to the "multiple behaviors"
problem - mixins via default methods. Java arrived at the
same destination as Scala's traits and Ruby's modules through
a 20-year journey of backward-compatible evolution, driven
by the original single-inheritance constraint.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** Given a class hierarchy in a Spring Boot
   application, identify 3 cases where the declared type
   should be an interface (not the concrete class) for
   Dependency Injection and testability. Refactor each.

2. **[APPLY]** Apply Interface Segregation Principle: take
   a `UserRepository` interface with 12 methods (CRUD +
   search + analytics) and split it into appropriate smaller
   interfaces. Show which service classes inject which
   sub-interfaces.

3. **[IMPLEMENT]** Implement a Template Method Pattern
   using an abstract class: define a 3-step process
   (validate, transform, persist) as a template in the
   abstract class, with `transform` as abstract. Create
   two concrete subclasses with different transforms.

4. **[DIAGNOSE]** Given a diamond problem compilation error
   with two interfaces both providing a `default toString()`
   equivalent method, trace the conflict, implement the
   resolution in the implementing class, and explain why
   Java requires manual resolution in this case.

5. **[DESIGN]** Design a payment processing library that
   third-party payment providers (Stripe, PayPal, Braintree)
   can implement. Define the interface contract such that:
   providers must implement only what is specific to them,
   and shared behavior (idempotency key generation, logging)
   is provided via default methods.

---

### 🧠 Think About This Before We Continue

**Q1.** Java 8+ added `default` and `static` methods to
interfaces. Java 9+ added `private` methods. At what point
does an interface become "an abstract class that allows
multiple inheritance"? What is the last capability that
abstract classes have that interfaces will NEVER have?

*Hint: The remaining capabilities that interfaces can never
have: (1) INSTANCE STATE (non-static fields). Interfaces
can have static final constants but not per-instance fields.
(2) CONSTRUCTOR logic. Interfaces have no constructors,
so you cannot enforce initialization invariants on the
object's creation through an interface.
These two are the fundamental OOP concepts that require
"identity" (a specific object instance with its own state),
which interfaces deliberately do not have.
Abstract classes represent "a thing that IS..." (identity +
partial implementation). Interfaces represent "a thing that
CAN..." (capability, no identity). This distinction is not
going away.*

**Q2.** Consider: `interface Greeter { default String greet(String name) { return "Hello, " + name; } }`.
A class `EnglishGreeter implements Greeter` does not override `greet`.
Later, the interface changes: `default String greet(String name) { return "Hi, " + name; }`.
What happens when `EnglishGreeter.greet("Alice")` is called after the
interface change? Is this a feature or a problem?

*Hint: After the interface changes, `EnglishGreeter.greet("Alice")`
returns "Hi, Alice" - the new default. This is a feature
for library evolution: the library changes the default behavior
and all non-overriding implementations automatically adopt
the new behavior. It is ALSO a problem for stability:
if `EnglishGreeter` relied on the "Hello" behavior implicitly
(tests passed against the default), those tests now fail
silently. This is the "default method trap": silently changing
behavior for all non-overriding implementations. Mitigation:
treat default method behavior as a contract, version it,
and notify implementors before changing. If a class specifically
wants "Hello" behavior, it should override and not rely
on the default.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between an interface and an
abstract class? When would you use each?"**

*Why they ask:* Classic Java OOP question. Tests design
thinking, not just syntax knowledge.

*Strong answer includes:*
- Interface: contract, no state, multiple implementation.
  USE FOR: defining types for dependency injection (service
  interfaces, repository interfaces), behavioral capabilities
  (`Comparable`, `Runnable`, `Serializable`), API contracts
  (what the library user must provide).
- Abstract class: template, has state, single inheritance.
  USE FOR: template method pattern (define algorithm skeleton,
  subclasses fill in parts), base class with constructor
  initialization (shared state setup), partial implementations
  where subclasses share significant behavior.
- Rule: prefer interfaces. Use abstract class ONLY when
  you need shared state or constructor logic.

**Q2: "What are default methods in Java interfaces?
Why were they added? What problems do they create?"**

*Why they ask:* Tests modern Java knowledge and design
trade-off understanding.

*Strong answer includes:*
- Default methods (Java 8): interface methods with a body.
  `default void foo() { ... }` - implementing classes get
  this method without overriding.
- Why added: the primary reason was `java.util.Collection`
  evolution. Java 8 added `stream()`, `forEach()`, etc. to
  `Collection`, `List`, `Iterable`. Without default methods,
  EVERY class implementing these interfaces would need to
  implement the new methods - breaking millions of lines
  of existing code. Default methods allowed adding behavior
  to interfaces without breaking existing implementations.
- Problems: (1) Diamond problem: two interfaces provide
  `default foo()` with no inheritance relationship - must
  override in implementing class. (2) Surprise behavior
  changes: a library changes a default method's implementation;
  all non-overriding implementations silently change behavior.
  (3) Interface contract bloat: default methods can make
  interfaces large and confusing - they're no longer "pure contracts."

**Q3: "Explain the Interface Segregation Principle with a Java example."**

*Why they ask:* SOLID principles are expected knowledge for senior developers.

*Strong answer includes:*
- ISP: "Clients should not be forced to depend on methods
  they do not use."
- BAD: `interface UserRepository { User findById(UUID id); void save(User u); void delete(UUID id); List<User> findAll(); Long count(); List<User> searchByName(String q); Map<String,Integer> getAgeDistribution(); }`
  A service that only reads users by ID must depend on the
  entire interface including `getAgeDistribution()`.
- GOOD: Split into focused interfaces:
  `interface UserReader { User findById(UUID id); List<User> findAll(); }`
  `interface UserWriter { void save(User u); void delete(UUID id); }`
  `interface UserAnalytics { Map<String,Integer> getAgeDistribution(); }`
  Services inject only the interface(s) they need.
  `UserProfileService` injects `UserReader`.
  `UserAdminService` injects `UserReader` and `UserWriter`.
  `UserDashboardService` injects `UserAnalytics`.
- Benefits: smaller dependency surface for each service.
  Easier to mock in tests. Clearer intent.
