---
id: CSF-038
title: Interfaces vs Abstract Classes
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - pattern
status: draft
version: 2
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /csf/interfaces-vs-abstract-classes/
---

# CSF-038 - Interfaces vs Abstract Classes

⚡ TL;DR - Interfaces define a contract (what something can do); abstract classes define a partial implementation (what something partially is); choose based on whether you need behaviour inheritance.

| CSF-038         | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-003, CSF-011, CSF-013             |                 |
| **Used by:**    | CSF-039, CSF-040                      |                 |
| **Related:**    | CSF-003, CSF-013, CSF-039, CSF-046    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without interfaces, you can't program to abstractions. Every
variable must be typed to a concrete class. A `PaymentProcessor`
must be `StripeProcessor`, not "something that processes payments".
Extending behaviour requires inheritance, which creates tight
coupling and brittle hierarchies.

**THE BREAKING POINT:**
Java codebases built without interfaces are hard to test (can't
mock concrete classes easily), hard to extend (must subclass),
and hard to swap implementations. Tests require real databases
because the code says `MySQLDatabase`, not `Database`.

**THE INVENTION MOMENT:**
Simula (1967) introduced classes; Smalltalk (1972) introduced
message passing (duck typing). Java (1995) formalised the
interface as a pure contract: a type with no implementation,
only method signatures. Abstract classes occupy the middle:
a type with some implementation and some abstract method
signatures. Each serves a different design purpose.

**EVOLUTION:**
Java 8 added `default` methods to interfaces, blurring the
distinction. Kotlin and Scala allow interface methods with
implementation (`default` and `trait` bodies). Rust uses
`trait` as the sole abstraction mechanism (no inheritance).
Haskell uses type classes. The trend: interfaces with
default methods are increasingly preferred over abstract classes.

---

### 📘 Textbook Definition

An **interface** is a type that defines a contract: a set of
method signatures that implementors must provide. It specifies
_what_ a type can do, with no (or default) implementation.
An **abstract class** is a class that cannot be instantiated;
it may have abstract methods (like an interface) and concrete
methods (partial implementation). The choice: interface for
pure contracts (multiple inheritance allowed); abstract class
for shared implementation (single inheritance).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Interface = "can do" contract; abstract class = "is a" with partial implementation.

**One analogy:**

> An interface is a job description: it lists what skills are
> required. An abstract class is an apprenticeship: it provides
> some training and tools but expects you to develop the
> specialty yourself. A class implementing an interface says
> "I meet these requirements." A class extending an abstract
> class says "I was trained here and specialise in this."

**One insight:**
Prefer interfaces + composition over abstract class + inheritance.
Interfaces allow multiple contracts; composition allows mixing
behaviours. Inheritance creates a permanent, hard-to-change
bond between parent and child.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Interface = pure contract; zero or minimal implementation.
2. Abstract class = partial implementation; requires extension to be concrete.
3. A class can implement many interfaces; it can only extend one abstract class (Java).
4. Program to interfaces, not implementations (Dependency Inversion Principle).
5. Abstract classes are appropriate when subclasses genuinely _are-a_ specialisation.

**DERIVED DESIGN:**

- `interface Serializable` — marker: "this type can be serialised"
- `interface Comparable<T>` — contract: "this type can be compared"
- `abstract class HttpServlet` — template method: base provides flow, subclass provides specifics
- `abstract class AbstractList<E>` — skeletal implementation: most methods implemented, a few left abstract

**THE TRADE-OFFS:**
**Interface:** Multiple inheritance; pure contract; more flexible. Cannot hold state.
**Abstract class:** Single inheritance; can hold state; can provide substantial implementation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Different degrees of abstraction serve different design goals.
**Accidental:** Deep class hierarchies (7 levels of inheritance), abstract classes used just to share utility code.

---

### 🧪 Thought Experiment

**SETUP:**
You need to write a payment service that works with
Stripe, PayPal, and your own bank.

**WITH ABSTRACT CLASS ONLY:**

```java
abstract class PaymentProcessor {
    abstract String charge(double amount);
    // PayPal and Bank can't extend the same class!
    // What if PayPal already extends 3rd-party SDK?
}
```

**WITH INTERFACE:**

```java
interface PaymentProcessor {
    String charge(double amount);
}
class StripeProcessor implements PaymentProcessor { ... }
class PayPalProcessor implements PaymentProcessor { ... }
class BankProcessor implements PaymentProcessor { ... }
// Service depends on interface, not concrete classes
class PaymentService {
    private final PaymentProcessor processor;
    // Inject any implementation: easy testing, easy swapping
}
```

**THE INSIGHT:**
Interfaces enable _dependency inversion_: high-level code (PaymentService)
depends on an abstraction (PaymentProcessor interface), not a
concrete class. Implementations can change without touching PaymentService.

---

### 🧠 Mental Model / Analogy

> An interface is a power outlet standard: any device that
> has the right plug (implements the interface) can connect.
> An abstract class is a branded charger base: your specific
> phone charger extends it but it's tightly coupled to the brand.
> Multiple outlet standards can coexist; you can only use
> one brand's base charger.

**Element mapping:**

- Power outlet standard = interface
- Device with compatible plug = class implementing interface
- Branded charger base = abstract class
- Your phone charger = concrete subclass
- Multiple plug adapters = multiple interface implementations

Where this analogy breaks down: abstract classes can have
substantial shared logic; interfaces traditionally couldn't
(pre-Java 8 default methods).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An interface is a promise: "I can do these things." An abstract
class is a template: "I provide most of the implementation;
you complete the rest." Choose interface when you want to
specify what something _does_; choose abstract class when you
want to share _how it's done_.

**Level 2 - How to use it (junior developer):**
Default: use interface. Add abstract class only when multiple
subclasses need substantial identical implementation. Inject
dependencies as interfaces (not concrete classes) to enable
fake/mock in tests. Every concrete class that's used via
constructor injection should be behind an interface.

**Level 3 - How it works (mid-level engineer):**
JVM method dispatch for interfaces uses `invokeinterface`
bytecode; for classes, `invokevirtual`. The JIT typically
optimises both to direct calls when the call site is
monomorphic (only one implementation seen). Multiple-implementation
interface calls (polymorphic) are slower but usually negligible.
`default` methods in interfaces have been supported since Java 8
and compile to `invokevirtual` on the interface.

**Level 4 - Why it was designed this way (senior/staff):**
Rust has no classes or inheritance at all — only `trait`s (like
interfaces with default methods). All polymorphism is via traits.
This enforces composition over inheritance by language design.
Haskell's type classes are similar: a type class defines
behaviour that a type must provide. The consensus in modern
language design: interfaces/traits as the only abstraction
mechanism; inheritance is not needed.

**Expert Thinking Cues:**

- When reviewing a class hierarchy: is this `is-a` or `can-do`? Is abstract class justified?
- When seeing 5 levels of inheritance: what design pattern could flatten this?
- When a concrete class is injected directly: can it be abstracted to an interface?

---

### ⚙️ How It Works (Mechanism)

**Java interface method dispatch:**

```
PaymentProcessor p = new StripeProcessor();
p.charge(100.0);
// bytecode: invokeinterface PaymentProcessor.charge
// JVM resolves to StripeProcessor.charge at runtime
// JIT: if only StripeProcessor seen -> devirtualise to direct call
```

**Abstract class template method pattern:**

```java
abstract class DataProcessor {
    // Template method: defines algorithm skeleton
    final void process() {
        validateInput(); // from subclass
        transformData(); // from subclass
        writeOutput();   // shared implementation here
    }
    abstract void validateInput();
    abstract void transformData();
    private void writeOutput() { /* shared code */ }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
PaymentService constructed with PaymentProcessor  ← YOU ARE HERE
  -> uses interface reference (not concrete type)
runtime: PaymentProcessor is StripeProcessor
  -> invokeinterface resolves to StripeProcessor.charge
  -> JIT devirtualises after several calls (monomorphic)
test: PaymentProcessor is MockProcessor
  -> same interface; test controls behaviour
  -> PaymentService code unchanged
```

**FAILURE PATH:**

- Deep inheritance: `CustomerOrderShippingInvoiceable` extends 7 levels
- Interface explosion: 50 single-method interfaces with no coherent design
- Using abstract class for utility code: `AbstractHelper` with only static methods

---

### ⚖️ Comparison Table

| Feature                 | Interface                      | Abstract Class                          |
| ----------------------- | ------------------------------ | --------------------------------------- |
| Multiple "inheritance"  | Yes (multiple implements)      | No (single extends)                     |
| Can hold state (fields) | No (constants only)            | Yes                                     |
| Implementation          | Default methods only           | Partial or full                         |
| When to use             | Pure contract, multiple types  | Shared implementation, single hierarchy |
| In Rust/Haskell         | `trait` / type class           | Not applicable (no inheritance)         |
| Constructor             | No                             | Yes (for subclasses)                    |
| Key pattern             | Strategy, Dependency Inversion | Template Method                         |

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                 |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| "Abstract class is for shared code; interface is for polymorphism" | Both provide polymorphism; abstract class provides shared implementation                                |
| "Interfaces are slow (invokeinterface)"                            | JIT devirtualises monomorphic calls; performance difference is negligible in practice                   |
| "Java 8 default methods make abstract classes obsolete"            | Abstract classes can still hold state and constructors, which interfaces can't                          |
| "Always use abstract class if you have any shared code"            | Prefer composition + interface; only use abstract class for genuine `is-a` relationships                |
| "Marker interfaces are obsolete"                                   | Serializable, Cloneable are marker interfaces still used in JDK; annotations are the modern alternative |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Fragile Base Class Problem**
**Symptom:** Changing abstract class method breaks all subclasses unexpectedly.
**Root Cause:** Subclasses depend on base class implementation details.
**Fix:** Use interface + composition instead; or make base class methods `final`.

**Mode 2: Interface Segregation Violation**
**Symptom:** Implementing class has empty/stub implementations for methods it doesn't use.
**Root Cause:** Interface is too broad; interface segregation principle violated.
**Fix:** Split into smaller, focused interfaces (Interface Segregation Principle).

**Mode 3: Unnecessary Concrete Type Dependency**
**Symptom:** Tests require live database because code uses `MySQLUserRepository` directly.
**Root Cause:** Field typed to concrete class, not interface.
**Fix:**

```java
// BAD
private MySQLUserRepository repo; // can't mock

// GOOD
private UserRepository repo; // interface; mockable
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-003 - Object-Oriented Programming (OOP)]]
- [[CSF-011 - Encapsulation and Information Hiding]]

**Builds On This (learn these next):**

- [[CSF-039 - Generics and Parametric Polymorphism]]
- [[CSF-040 - Pattern Matching]]

**Alternatives / Comparisons:**

- Rust traits (interface without inheritance)
- Haskell type classes (constrained parametric polymorphism)
- Composition over inheritance (CSF-003)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Interface=pure contract; Abstract     │
│                 class=partial implementation          │
│ PROBLEM         Tight coupling to concrete types;      │
│ IT SOLVES       brittle inheritance hierarchies       │
│ KEY INSIGHT     Interface=can-do (multiple);           │
│                 Abstract=is-a (single)                │
│ USE WHEN        Interface: default. Abstract: genuine  │
│                 is-a with substantial shared impl     │
│ AVOID WHEN      Deep inheritance; abstract for utils  │
│ TRADE-OFF       Interface: flexible; abstract: shared  │
│                 state + impl                         │
│ ONE-LINER       Program to interfaces; extend only    │
│                 for true is-a relationships           │
│ NEXT EXPLORE    CSF-039, Rust traits, DIP             │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Interface = "can do" contract; abstract class = "is a" with shared implementation.
2. A class can implement many interfaces but only extend one abstract class — prefer interfaces.
3. Program to interfaces, not concrete classes: enables injection, testing, and swappability.

**Interview one-liner:**
"Interfaces define pure contracts (what a type can do, multiple allowed); abstract classes define partial implementations (what a type partially is, single inheritance); prefer interfaces for dependency inversion and testability."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Program to abstractions, not concretions. Every dependency on
a concrete class is a hardwired coupling. Every dependency on
an interface is a socket. Sockets can accept any compatible
plug; hardwired couplings cannot be changed without rewiring.

**Where else this pattern appears:**

- **REST API contracts** — the API spec (OpenAPI) is the interface; the implementation is the concrete class
- **Database abstraction** — JPA `EntityManager` is the interface; Hibernate is the implementation
- **Test doubles** — mock objects implement the same interface as production code

---

### 💡 The Surprising Truth

Rust, arguably the most influential systems language since C,
has no class inheritance at all. Every polymorphism in Rust is
via traits (like interfaces with default methods). Go has
no explicit interface declaration — structural typing means any
type that has the right methods _is_ the interface, without
declaring it. These two influential modern languages converged
on: no inheritance, implicit or explicit interfaces. The
decades-long industry debate about "composition vs inheritance"
was resolved by language design: new languages removed the
ambiguity by removing inheritance as an option.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Java's `Comparable<T>` interface
requires `compareTo(T other)`. If a class implements `Comparable`,
it promises a total ordering consistent with `equals`. What
happens if `compareTo` and `equals` are inconsistent
(e.g., `a.compareTo(b) == 0` but `!a.equals(b)`)?

_Hint:_ Research what `TreeSet` and `SortedMap` do when
`compareTo` and `equals` are inconsistent. What does the Javadoc
say about this contract?

**Q2 (Scale):** A large Java codebase has 800 classes that
extend `BaseEntity`. Someone needs to add a new method to
`BaseEntity`. What is the blast radius? How would an interface

- default method approach have reduced this?

_Hint:_ Consider what happens when you add a non-final method
to a base class that's overridden in 800 subclasses. Can you
add it with a default implementation? What if the method conflicts
with an existing method?

**Q3 (Design Trade-off):** Go's structural typing means any
struct that has method `Read(p []byte) (n int, err error)` implicitly
implements `io.Reader` without declaring it. Java requires
explicit `implements`. What are the advantages and disadvantages
of structural vs nominal interface implementation?

_Hint:_ Research Go's `io.Reader` and how it enables composition
across unrelated packages. Then consider the downside: how do you
know which interfaces a type implements?
