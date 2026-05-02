---
layout: default
title: "Object-Oriented Programming (OOP)"
parent: "CS Fundamentals — Paradigms"
nav_order: 3
permalink: /cs-fundamentals/object-oriented-programming/
number: "0003"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Imperative Programming, Functions, Variables
used_by: Design Patterns, Spring Core, Java Language
related: Functional Programming, Procedural Programming, Composition over Inheritance
tags:
  - foundational
  - pattern
  - mental-model
  - java
  - architecture
---

# 003 — Object-Oriented Programming (OOP)

⚡ TL;DR — OOP organises code into objects that combine state and behaviour, modelling real-world entities so software mirrors the problem domain.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #0003 │ Category: CS Fundamentals — Paradigms │ Difficulty: ★☆☆ │
├──────────────┼───────────────────────────────────────┼─────────────────────────┤
│ Depends on: │ Imperative Programming, Functions, │ │
│ │ Variables │ │
│ Used by: │ Design Patterns, Spring Core, │ │
│ │ Java Language │ │
│ Related: │ Functional Programming, Procedural, │ │
│ │ Composition over Inheritance │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
In the era of procedural code, a banking application would have
global arrays for account balances, transaction histories, and
customer names — all linked by numeric indices. A `transfer()`
function would reach into all three arrays simultaneously. As the
system grew, any function could modify any global data. Adding a
savings account type meant hunting through every function that
touched account data and adding special-case conditionals.

THE BREAKING POINT:
At 100,000 lines of procedural code, the coupling between data
structures and the functions that manipulated them became
unmanageable. Changing the representation of an account balance
required updating dozens of functions. There was no systematic
way to model "an account does these things" as a single unit.

THE INVENTION MOMENT:
This is exactly why Object-Oriented Programming was created. By
bundling data (fields) and the operations on that data (methods)
into an object, OOP enforced a contract: only an `Account` object
knows how to modify an account balance. The rest of the system
calls `account.deposit(100)` without knowing the internals.

### 📘 Textbook Definition

Object-Oriented Programming is a paradigm that organises software
around objects — entities that encapsulate state (fields/attributes)
and behaviour (methods). OOP is characterised by four pillars:
Encapsulation (hiding internal state), Abstraction (exposing only
relevant interfaces), Inheritance (deriving specialised types from
general ones), and Polymorphism (different objects responding to
the same interface differently). Objects communicate by sending
messages — calling each other's methods.

### ⏱️ Understand It in 30 Seconds

**One line:**
Bundle data and the functions that operate on it into a single unit called an object.

**One analogy:**

> A car is an object: it has state (fuel level, current speed) and
> behaviour (accelerate, brake, steer). You don't need to know
> whether the engine is fuel injection or carburetted — you just
> call `car.accelerate()`. The implementation is hidden inside
> the object.

**One insight:**
OOP's power isn't classes or inheritance — it's the principle that
data and the code that mutates it should live together. When you
change a data structure, you only change one class. The rest of
the system is insulated from that change through the interface.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. An object is the indivisible unit of state + behaviour.
   You cannot separate an object's data from the methods
   that operate on it.
2. Objects communicate via messages (method calls) —
   no external code directly accesses another object's state
   (in a strictly OO model).
3. Identity: an object has an identity distinct from its
   value — two Account objects with the same balance are
   still two different accounts.

DERIVED DESIGN:
Given invariant 1, a class is the natural blueprint: it defines
the fields (state template) and methods (behaviour template) that
all objects of that type share. Given invariant 2, fields should
be private by default, with public methods as the interface.
Given invariant 3, objects use references, not value copies.

This forces the following design:

```
Class (blueprint) → instantiate → Object (instance)
Object.method() sends message → executes on object's state
```

THE TRADE-OFFS:
Gain: Natural modelling of real-world entities; change isolation
(modify internals without breaking callers); reuse via
inheritance and polymorphism.
Cost: Can lead to deep inheritance hierarchies that are brittle;
mutable shared objects cause concurrency bugs; not all
problems map naturally to "things with behaviour."

### 🧪 Thought Experiment

SETUP:
A system needs to process payments. There are three types: credit
card, bank transfer, PayPal. Each has different validation and
processing logic.

WHAT HAPPENS WITHOUT OOP (procedural):

```
processPayment(type, amount, details) {
    if (type == "credit") { validateCreditCard(details); ... }
    else if (type == "bank") { validateBankTransfer(details); ... }
    else if (type == "paypal") { validatePayPal(details); ... }
}
```

Adding a 4th payment type means modifying `processPayment`.
Every switch statement in the codebase grows. Tests break.

WHAT HAPPENS WITH OOP:

```
interface Payment { validate(); process(); }
class CreditCard implements Payment { ... }
class BankTransfer implements Payment { ... }
class PayPal implements Payment { ... }

// Caller is unchanged when new types are added:
payment.validate();
payment.process();
```

Adding a new payment type creates a new class. Existing code is
untouched. This is the Open/Closed Principle in practice.

THE INSIGHT:
Polymorphism means "add new types without changing existing code."
OOP's biggest design win is enabling extension without modification.

### 🧠 Mental Model / Analogy

> Objects are like departments in a company. The Payroll department
> has its own data (employee salaries) and its own operations
> (process payroll, add employee). The Marketing department doesn't
> reach into Payroll's spreadsheets — it sends a request: "process
> payroll for employee 42." Payroll handles it internally.

"Department" → class / object
"Department's private files" → private fields
"Sending a request to another department" → calling a method
"The request interface" → the public API / method signature
"Department structure" → class definition

Where this analogy breaks down: unlike real departments, objects
can be cloned instantly, and object identity (reference vs. value)
has no real-world equivalent.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
OOP is a way of organising code that groups related data and
actions together. A `Dog` object knows its own name and can
`bark()`. You don't need to know how barking works internally —
you just call `myDog.bark()`.

**Level 2 — How to use it (junior developer):**
Create classes with private fields and public methods. Use
constructors to initialise objects. Extend base classes to
reuse code. Implement interfaces to define contracts that multiple
classes can fulfil. Be cautious with inheritance depth — prefer
composition (has-a) over deep inheritance chains (is-a).

**Level 3 — How it works (mid-level engineer):**
At the JVM level, an object is a heap-allocated block containing
the fields and a pointer to the class's method table (vtable).
When you call `animal.speak()`, the JVM looks up the method in
the vtable at runtime — this is dynamic dispatch. The vtable
pointer determines which concrete implementation runs, enabling
polymorphism. Every object also has a header containing GC
metadata and the lock word for `synchronized`.

**Level 4 — Why it was designed this way (senior/staff):**
Smalltalk (1972) formalised OOP as message-passing between
autonomous objects — Alan Kay's vision was closer to independent
actors than Java's class hierarchy. Java's design prioritised
static typing and performance, which is why method calls are
vtable lookups rather than dynamic message sends. The "four pillars"
framing (APIE) is a pedagogical simplification — production OOP
design centres on SOLID principles, not pillars. The ongoing
debate between OOP and FP (functional programming) is really a
debate about mutable state: OOP manages it with encapsulation;
FP eliminates it with immutability.

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│          OOP OBJECT MEMORY LAYOUT (JVM)          │
├──────────────────────────────────────────────────┤
│ Object Header (16 bytes)                         │
│   Mark Word: GC info, hashCode, lock state       │
│   Class Pointer: → Method Table (vtable)         │
├──────────────────────────────────────────────────┤
│ Instance Fields (per class in hierarchy)         │
│   field1: int (4 bytes)                          │
│   field2: reference (8 bytes on 64-bit JVM)      │
│   ...                                            │
└──────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────┐
│           METHOD TABLE (vtable)                  │
├──────────────────────────────────────────────────┤
│ speak()    → Dog.speak() implementation          │
│ eat()      → Animal.eat() (inherited)            │
│ toString() → Dog.toString() (overridden)         │
└──────────────────────────────────────────────────┘
```

**Object creation:** `new Dog("Rex")` allocates space on the heap,
initialises the header, sets the vtable pointer to Dog's method
table, then calls the constructor to set fields.

**Method dispatch:** `animal.speak()` looks up `speak` in the
vtable at runtime. If `animal` actually holds a `Dog`, it calls
`Dog.speak()`. If it holds a `Cat`, it calls `Cat.speak()`. This
runtime lookup is polymorphism via dynamic dispatch.

**Inheritance:** A subclass's vtable is a copy of the superclass
vtable with overridden entries replaced. Inherited methods point
to the same implementation as the parent; overridden ones point
to the new implementation.

**Happy path:** Objects are properly initialised, methods are
called through well-defined interfaces, and changes to internals
don't propagate through the system.

**Failure path:** Mutable shared objects accessed from multiple
threads without synchronisation cause race conditions. Deep
inheritance with method overriding causes surprising dispatch
to the wrong method (fragile base class problem).

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[Client Code: payment.process(100)]
  → [JVM: load reference from variable]
  → [JVM: fetch vtable pointer from object header]
  → [JVM: look up process() in vtable]
  → [Dynamic dispatch ← YOU ARE HERE]
  → [Execute CreditCard.process() or BankTransfer.process()]
  → [Return result to caller]
```

FAILURE PATH:
[NullPointerException: payment is null]
→ [JVM throws NPE] → [Stack unwind]
→ [Observable: NullPointerException in logs]

WHAT CHANGES AT SCALE:
At 10x load, mutable objects shared between threads require
synchronisation — every `synchronized` method becomes a
contention bottleneck. At 100x, immutable value objects (a
functional style applied within OOP) dramatically reduce locking
overhead. At 1000x distributed scale, objects can no longer
span process boundaries — you need serialisation and distributed
proxies, which break the "send a message" mental model.

### 💻 Code Example

**Example 1 — Encapsulation (Java):**

```java
// BAD: Public fields — anyone can break invariants
public class BankAccount {
    public double balance;  // caller sets balance = -1000
}

// GOOD: Private state, controlled mutations
public class BankAccount {
    private double balance;  // only this class modifies it

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException(
            "Amount must be positive"
        );
        this.balance += amount;
    }

    public double getBalance() {
        return balance;  // read-only access
    }
}
```

**Example 2 — Polymorphism (Java):**

```java
// Define the contract
interface Shape {
    double area();
}

class Circle implements Shape {
    private final double radius;
    Circle(double r) { this.radius = r; }
    public double area() { return Math.PI * radius * radius; }
}

class Rectangle implements Shape {
    private final double w, h;
    Rectangle(double w, double h) { this.w = w; this.h = h; }
    public double area() { return w * h; }
}

// Caller is oblivious to concrete type — polymorphism
double totalArea(List<Shape> shapes) {
    return shapes.stream()
        .mapToDouble(Shape::area)
        .sum();
}
```

**Example 3 — Composition over Inheritance:**

```java
// BAD: Deep inheritance for code reuse
class Vehicle { void start() {...} }
class Car extends Vehicle { void honk() {...} }
class ElectricCar extends Car { void charge() {...} }
// Adding a new dimension breaks the hierarchy

// GOOD: Compose behaviours
class Car {
    private final Engine engine;  // has-a, not is-a
    private final Horn horn;

    Car(Engine e, Horn h) { this.engine = e; this.horn = h; }
    void start() { engine.start(); }
    void honk()  { horn.sound(); }
}
```

### ⚖️ Comparison Table

| Paradigm      | State Model            | Code Reuse               | Concurrency Safety     | Best For                        |
| ------------- | ---------------------- | ------------------------ | ---------------------- | ------------------------------- |
| **OOP**       | Mutable (encapsulated) | Inheritance + interfaces | Medium (needs sync)    | Domain modelling, large systems |
| Functional    | Immutable              | Higher-order functions   | High (no shared state) | Data transforms, concurrency    |
| Procedural    | Mutable (global/local) | Functions                | Low                    | Scripts, small programs         |
| Data-oriented | Value types            | Composition              | High                   | Performance-critical, games     |

How to choose: Use OOP when modelling entities with complex
lifecycles and many operations. Use functional when data
transformations dominate and concurrency correctness is critical.

### 🔁 Flow / Lifecycle

```
┌──────────────────────────────────────────────────┐
│           OBJECT LIFECYCLE                       │
├──────────────────────────────────────────────────┤
│  [Class loaded] → JVM loads bytecode             │
│       ↓                                          │
│  [new ClassName()] → heap allocation             │
│       ↓                                          │
│  [Constructor runs] → fields initialised         │
│       ↓                                          │
│  [Object in use] → methods called                │
│       ↓                                          │
│  [No more references] → GC eligible              │
│       ↓                                          │
│  [finalise() if defined] → resource cleanup      │
│       ↓                                          │
│  [GC collects] → memory reclaimed                │
└──────────────────────────────────────────────────┘
```

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                               |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| OOP means using classes              | OOP means encapsulating state with behaviour — classes are one implementation mechanism                               |
| Inheritance is the core of OOP       | Polymorphism and encapsulation are more important; deep inheritance hierarchies are widely considered an anti-pattern |
| OOP is always better than procedural | For simple scripts and data pipelines, procedural code is cleaner; OOP's benefit shows at scale                       |
| private means completely hidden      | In Java/Python, reflection can bypass private access — "private" is a design contract, not a security guarantee       |

### 🚨 Failure Modes & Diagnosis

**1. Mutable Shared Object (Thread Safety Bug)**

Symptom:
Counter increments are lost under concurrent load; values are
inconsistent across requests.

Root Cause:
Two threads read the same field simultaneously, both see value 5,
both write 6, net result is +1 instead of +2.

Diagnostic:

```bash
# Java: detect with ThreadSanitizer or helgrind
java -ea MyApp 2>&1 | grep "race condition"

# JVM thread dump to see blocked threads
jstack <pid> | grep -A 5 "BLOCKED"
```

Fix:

```java
// BAD: unsynchronised
class Counter { private int count; void inc() { count++; } }

// GOOD: thread-safe atomic
class Counter {
    private final AtomicInteger count = new AtomicInteger();
    void inc() { count.incrementAndGet(); }
}
```

Prevention: Make objects immutable wherever possible; use
`AtomicInteger`, `ConcurrentHashMap` for shared mutable state.

**2. Fragile Base Class**

Symptom:
Changing a method in a parent class breaks subclass behaviour
in unexpected ways; tests for subclasses fail after a "safe"
parent change.

Root Cause:
Subclass overrides a method and calls `super()`, relying on the
parent's internal sequence. Parent changes the sequence.

Diagnostic:

```bash
# Review all subclasses of the changed parent
grep -r "extends ParentClass" src/
# Check each for super() calls
grep -r "super\." src/
```

Fix:

```java
// BAD: subclass depends on super's internal order
class Sub extends Base {
    @Override void doWork() {
        super.doWork(); // breaks if super changes
        extraStep();
    }
}

// GOOD: prefer composition
class Better {
    private final Base base;
    void doWork() {
        base.doWork();
        extraStep();
    }
}
```

Prevention: Follow the Liskov Substitution Principle; prefer
composition over inheritance for code reuse.

**3. Anemic Domain Model**

Symptom:
Classes contain only getters/setters; all business logic lives
in "service" classes that manipulate data objects. OOP provides
no value over procedural code.

Root Cause:
Developers treat domain objects as data containers rather than
putting domain logic inside them.

Diagnostic:

```bash
# Count methods vs fields in model classes
# If a class has 10 fields but only getters/setters,
# it's anemic
grep -c "get\|set" src/model/Order.java
grep -c "void\|return" src/service/OrderService.java
```

Fix:

```java
// BAD: anemic Order — logic lives in OrderService
class Order { private double total; /* only getters/setters */ }
class OrderService {
    void applyDiscount(Order o) { o.setTotal(o.getTotal()*0.9); }
}

// GOOD: rich domain object — logic lives inside Order
class Order {
    private double total;
    void applyDiscount(double rate) {
        if (rate < 0 || rate > 1) throw new IllegalArgumentException();
        this.total *= (1 - rate);
    }
}
```

Prevention: Ask "should this logic belong to the object?" before
placing business rules in service classes.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Imperative Programming` — OOP methods are blocks of imperative code
- `Functions` — methods are specialised functions bound to objects
- `Variables` — fields are named, typed, object-scoped variables

**Builds On This (learn these next):**

- `Inheritance` — the mechanism for deriving specialised types
- `Polymorphism` — different objects responding to the same interface
- `Design Patterns` — proven OOP solutions to recurring problems

**Alternatives / Comparisons:**

- `Functional Programming` — treats code as mathematical functions; minimises mutable state
- `Procedural Programming` — functions and global state without the object abstraction
- `Composition over Inheritance` — the modern OOP best practice that replaces deep hierarchies

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ Bundling data + behaviour into objects │
│ │ that model real-world entities │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ Global mutable data with no ownership; │
│ SOLVES │ uncontrolled access to shared state │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ Polymorphism = add new types without │
│ │ changing existing code (Open/Closed) │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ Modelling entities with complex state and │
│ │ many operations across a large codebase │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ Data transformation pipelines; concurrent │
│ │ code where immutability is safer │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ Encapsulation + extensibility vs. mutable │
│ │ state complexity at concurrent scale │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "A car: you call accelerate() — you don't │
│ │ need to know what's inside the engine." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Encapsulation → Polymorphism → SOLID │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Two threads call `bankAccount.deposit(100)` simultaneously.
The balance starts at £500. Trace step-by-step at the JVM bytecode
level (`getfield`, `iadd`, `putfield`) what happens — and explain
precisely why encapsulation in Java does NOT protect against this
race condition.

**Q2.** You're designing a system where `ElectricCar` needs to
reuse code from both `Car` and `ElectricVehicle`. Java doesn't
support multiple inheritance of classes. Design the cleanest
possible solution using only OOP constructs, then explain what
this limitation reveals about a fundamental tension in the
OOP model.
