---
id: CSF-017
title: Polymorphism
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★☆☆
depends_on: CSF-003, CSF-008, CSF-009
used_by: CSF-011, CSF-019
related: CSF-003, CSF-008, CSF-011
tags:
  - foundational
  - first-principles
  - mental-model
  - design-principle
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/csf/polymorphism/
---

⚡ TL;DR - Polymorphism means one interface, many
implementations. A single piece of code can work with
any object that satisfies a contract, without knowing
the concrete type. Adding a new implementation extends
behavior without changing existing code.

| #010 | Category: CS Fundamentals - Paradigms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | OOP (CSF-003), Abstraction (CSF-008), Encapsulation (CSF-009) | |
| **Used by:** | Inheritance (CSF-011), Composition over Inheritance (CSF-019) | |
| **Related:** | OOP (CSF-003), Abstraction (CSF-008), Inheritance (CSF-011) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

You have a `PaymentProcessor` class that handles Stripe
payments. Now requirements change: support PayPal. Then
Braintree. Without polymorphism, you add a type field
and a growing chain of `if/else` or `switch` blocks:

```java
if (paymentType == "stripe") {
    stripeProcessor.charge(amount);
} else if (paymentType == "paypal") {
    paypalProcessor.pay(amount);
} else if (paymentType == "braintree") {
    braintreeProcessor.process(amount);
}
```

Every new payment provider touches this code. Every place
in the codebase that handles payments duplicates this
conditional logic. A logic error in one branch affects
correctness for all types. The code is open for bug
injection every time it is extended.

**THE BREAKING POINT:**

At three payment providers, this is manageable. At ten -
with conditional logic scattered across dozens of methods,
each with its own `switch` statement - a change to PayPal
requires auditing every conditional across the system.
Omitting a case means a silent runtime failure for one
provider. The system is fragile; extending it is high
risk.

**THE INVENTION MOMENT:**

Polymorphism solves this by replacing type-checking
conditionals with dynamic dispatch. Define one interface
(`PaymentProcessor.charge(amount)`). Each provider is
a separate class implementing the interface. Code that
processes payments holds a `PaymentProcessor` reference -
it calls `processor.charge(amount)` without knowing or
caring which provider backs it. Adding a 10th provider
adds one new class; no existing code changes.

**EVOLUTION:**

Polymorphism evolved from a pure runtime mechanism to
multiple forms: subtype polymorphism (OOP, runtime
dispatch), parametric polymorphism (generics, compile-time
type safety), and ad-hoc polymorphism (overloading).
Modern languages combine all three. Rust's trait system,
Haskell's typeclasses, and Go's interfaces are different
designs for the same underlying goal: write code once
against a contract; it works for any type satisfying
that contract.

---

### 📘 Textbook Definition

Polymorphism (Greek: "many forms") is the ability of
different types to be treated through a shared interface,
with each type providing its own specific implementation.
**Subtype polymorphism** (most common in OOP): a variable
of a base type can hold any subtype; method calls dispatch
to the concrete subtype's implementation at runtime via
dynamic dispatch (vtable lookup). **Parametric
polymorphism** (generics): code is written without
specifying concrete types; it works for any type that
satisfies constraints (type parameters). **Ad-hoc
polymorphism** (overloading): multiple methods with the
same name, differentiated by parameter types; resolved
at compile time.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Polymorphism means you can call `animal.speak()` and
get "Woof!" from a Dog or "Meow!" from a Cat - the
caller never needed to check which animal it had.

**One analogy:**

> An electrical outlet is polymorphic. The outlet's
> interface is: "provide 120V AC, accept any plug." A
> phone charger, laptop charger, or lamp plug into it.
> The outlet does not check which device you plugged
> in. The device provides its implementation of "consume
> electricity." Add a new device: the outlet is unchanged.
> The new device implements the same contract.

**One insight:**

Polymorphism is what makes the Open/Closed Principle
work: software should be open for extension (new
implementations) and closed for modification (existing
code). Without polymorphism, every extension requires
modifying existing conditional logic. With polymorphism,
extension means adding a new implementation class -
no existing code changes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **The interface is the contract** - caller code
   depends on the interface definition; it neither knows
   nor cares which concrete type satisfies the contract
   at runtime.

2. **Dispatch is dynamic** - in subtype polymorphism,
   the specific method to call is determined at runtime
   by the concrete type of the object, not at compile
   time by the declared type of the variable.

3. **Substitutability** - any subtype can be used
   wherever the interface type is expected. This is the
   Liskov Substitution Principle: if S is a subtype of
   T, code that works with T works correctly with S
   without modification.

**DERIVED DESIGN:**

At the JVM level, subtype polymorphism works via the
virtual method table (vtable). Every object has a pointer
to its class's vtable - a table of method pointers. When
you call `shape.area()` on a `Shape` reference, the JVM
reads the vtable pointer from the object, looks up the
`area()` entry in the table, and calls the function
pointer found there. If the concrete type is `Circle`,
the vtable entry points to `Circle.area()`. If `Square`,
it points to `Square.area()`. The same call site invokes
different code depending on the object's actual type.

**THE TRADE-OFFS:**

**Gain:** Adding new behavior by adding new classes,
not modifying existing logic. Code that works with the
interface works with all current and future implementations.
Testability: any implementation (including test doubles)
works wherever the interface is expected.

**Cost:** One level of indirection per virtual dispatch.
In tight, CPU-intensive loops, the vtable lookup is
measurable overhead. JIT compilers use inline caching
to optimize common dispatch paths, but the indirection
is real. Over-abstraction via polymorphism can make
code harder to understand - too many small classes with
single implementations add navigation overhead.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** When behavior genuinely varies by type
(different payment providers DO process differently),
representing that variation as separate classes with
a shared interface is essential complexity - it mirrors
reality.

**Accidental:** A class hierarchy of 12 levels for a
concept that has 2 real implementations, or creating
interfaces with one method and one implementation "for
future flexibility" - this is accidental complexity
added by over-application of polymorphism.

---

### 🧪 Thought Experiment

**SETUP:**

An audit logging system must write to stdout, a file,
or CloudWatch Logs, determined by environment.

**WITHOUT POLYMORPHISM:**

```java
public void log(String message) {
    if (env.equals("local")) {
        System.out.println(message);
    } else if (env.equals("dev")) {
        fileWriter.write(message);
    } else if (env.equals("prod")) {
        cloudwatchClient.putLog(message);
    }
}
```

Adding a new environment (staging with Datadog) touches
this method. Two occurrences in the codebase means two
places to update. Missing the second one means staging
logs silently to the wrong destination.

**WITH POLYMORPHISM:**

```java
interface Logger { void log(String message); }

class ConsoleLogger implements Logger {
    public void log(String msg) {
        System.out.println(msg);
    }
}
class FileLogger implements Logger { ... }
class CloudwatchLogger implements Logger { ... }

// Injection: one logger created at startup, used everywhere
Logger logger = loggerFactory.create(env);
logger.log(message); // no env-check in sight
```

Adding Datadog: create `DatadogLogger implements Logger`.
Inject it for staging. Zero changes to any existing code.
The staging environment gets Datadog logging with one
new class and one new factory branch.

**THE INSIGHT:**

Polymorphism moves "what type is this?" from runtime
call sites to the construction/injection point. The
type check exists once (at object creation); all call
sites are generic.

---

### 🧠 Mental Model / Analogy

> A universal remote control is polymorphic. It sends
> the "volume up" command through its interface. The TV
> (Samsung, LG, Sony) interprets and executes that
> command according to its own implementation. Adding
> a new TV brand does not change the remote control's
> "volume up" button logic. The remote is "open for
> extension" (new TV brands) and "closed for modification"
> (the button's behavior does not change).

- Remote interface → `interface`
- "Volume up" button → interface method
- Samsung TV's volume implementation → concrete class
- Adding a new TV brand → new class implementing interface
- Remote never checks TV brand → no type-checking conditionals
- OCP → open for extension (new TVs), closed for modification
  (remote button logic unchanged)

**Where this breaks down:** The remote analogy implies
a one-to-many relationship between caller and types.
In practice, polymorphism also enables many-to-many:
many callers, many types, all through one interface.
The analogy focuses on the "one interface" side but
understates the "many callers benefit" side.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Polymorphism means different things can respond to the
same instruction. "Speak!" to a Dog = "Woof!" To a Cat
= "Meow!" The instruction is the same; the response
is different based on who received it. In code, this
means you can write general instructions that work with
different specific things.

**Level 2 - How to use it (junior developer):**
Define an interface with the operations callers need.
Create multiple classes that implement the interface.
Inject the specific implementation through the constructor.
The caller holds an interface reference and calls methods
without knowing the concrete type. Use `@Override` to
mark implementations. Never check `instanceof` in
production code - that defeats polymorphism.

**Level 3 - How it works (mid-level engineer):**
At the JVM level: every object's first 8 bytes (on a
64-bit JVM) contain a class pointer (klass pointer)
to the class descriptor. The class descriptor contains
the vtable - a list of method pointers for each virtual
method. A `Shape` variable with a `Circle` object: when
you call `area()`, the JVM reads the klass pointer from
the object, loads the vtable, looks up the index for
`area()`, and jumps to that function. The index for
`area()` is determined at compile time; the function it
points to is determined at runtime by the actual type.
JIT's inline caching: if 99% of `area()` calls are on
`Circle`, the JIT generates code that checks "is this
a Circle? If yes, call Circle.area() directly; if not,
do the vtable lookup." This monomorphic inline cache
eliminates the vtable overhead for the common case.

**Level 4 - Why it was designed this way (senior/staff):**
Simula 67 introduced subtype polymorphism as a mechanism
for modeling real-world "kinds of things": a Ship and
a Truck are both Vehicles; `move()` means different
things for each. The formal basis is the Liskov
Substitution Principle (Barbara Liskov, 1987): if S is
a subtype of T, then programs using T should work with
S without needing to know S exists. This formalizes
the informal intuition that "Circle is a Shape" means
circle can be used anywhere shape is expected. The
principle drives interface design: an interface that
subtypes cannot satisfy without surprising callers is
a design flaw (fragile base class problem).

**Level 5 - Mastery (distinguished engineer):**
Polymorphism is a statement about software change.
The Open/Closed Principle says: extend by adding code,
not by modifying it. Polymorphism is the mechanism that
makes OCP achievable. At scale, a codebase where new
behavior is added by creating new classes (not modifying
old ones) has a lower bug introduction rate per extension
because new code has no footprint in existing tested code.
The staff engineer knows when not to use polymorphism:
a payment processor with two implementations (Stripe,
test double) needs an interface; a payment processor
with one implementation ever needs a class. The question
"is this likely to vary?" drives the abstraction decision.
Design patterns like Strategy, Command, and Visitor are
formalized patterns for applying polymorphism to specific
variability scenarios.

---

### ⚙️ Why It Holds True (Formal Basis)

Subtype polymorphism is formalized by the Liskov
Substitution Principle: "If S is declared to be a
subtype of T, then objects of type S should behave as
objects of type T when used in any context that expects
T." Formally: all properties of T that are provable
must also be provable for S.

Parametric polymorphism is formalized by System F (the
polymorphic lambda calculus, Girard 1972). A parametric
type `List<T>` is a function from types to types. The
universal quantifier "for all types T, List<T> is a
valid list" expresses parametric polymorphism formally.
Java generics are a restricted form of System F;
Haskell's parametric polymorphism is the full system.

---

### 🔄 System Design Implications

Polymorphism at the system level enables extensible
architectures.

**Plugin and extension points.** Frameworks define
interfaces; user code implements them. Spring's
`ApplicationListener`, Kafka's `Deserializer`, and
JUnit's `Extension` are all polymorphism: the framework
calls the interface; any implementation plugs in.

**Strategy pattern at scale.** A pricing engine that
applies discount strategies polymorphically can support
10 discount types without conditional logic. Adding a
holiday discount: one new class, registered in the
discount registry. No changes to the pricing engine.

**What changes at scale:** A monolith with 5 payment
providers and good polymorphism can scale to 50 providers
without any change to the payment processing pipeline.
The same code path handles all 50. Without polymorphism,
each new provider adds conditional branches to the
pipeline, and the pipeline becomes brittle at 50 providers.
Polymorphism's payoff scales with the number of variants.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Type-Checking Conditionals**

```java
// BAD: Type-checking conditionals.
// Each new notification type requires changing this method.
// Adding SMS notifications: find this class, add an else-if,
// test the entire block - high risk of regression.
public void sendNotification(User user, String msg,
        String type) {
    if (type.equals("email")) {
        emailSender.send(user.getEmail(), msg);
    } else if (type.equals("sms")) {
        smsSender.send(user.getPhone(), msg);
    } else if (type.equals("push")) {
        pushService.send(user.getDeviceToken(), msg);
    }
    // Adding slack? Add another else-if here.
}

// GOOD: Polymorphic dispatch.
// Adding Slack notifications: one new class, no changes
// to sendNotification or any other existing class.
interface NotificationChannel {
    void send(User user, String message);
}

class EmailChannel implements NotificationChannel {
    public void send(User user, String message) {
        emailSender.send(user.getEmail(), message);
    }
}

class SmsChannel implements NotificationChannel { ... }
class PushChannel implements NotificationChannel { ... }
// Adding Slack: class SlackChannel implements ...

public void sendNotification(User user, String msg,
        NotificationChannel channel) {
    channel.send(user, msg); // pure polymorphic dispatch
}
```

**Example 2 - Production: Strategy Pattern with Polymorphism**

```java
// Polymorphic discount strategy.
// Pricing engine calls apply(); it never knows which strategy.
public interface DiscountStrategy {
    Money apply(Money originalPrice, Order order);
}

@Component("PERCENTAGE")
public class PercentageDiscount
        implements DiscountStrategy {
    private final double pct;
    public Money apply(Money price, Order order) {
        return price.multiply(1 - pct / 100);
    }
}

@Component("LOYALTY")
public class LoyaltyDiscount implements DiscountStrategy {
    public Money apply(Money price, Order order) {
        int points = order.getCustomer().getLoyaltyPoints();
        double discount = Math.min(points * 0.001, 0.20);
        return price.multiply(1 - discount);
    }
}

// Pricing engine - knows nothing about specific discounts:
public class PricingEngine {
    private final Map<String, DiscountStrategy> strategies;

    public Money calculateFinalPrice(Order order) {
        String code = order.getDiscountCode();
        DiscountStrategy strategy = strategies.get(code);
        if (strategy == null) return order.getBasePrice();
        return strategy.apply(order.getBasePrice(), order);
    }
}
// Adding HOLIDAY discount: new class + register in Spring.
// PricingEngine: zero changes.
```

---

### ⚖️ Comparison Table

| Polymorphism Type | Mechanism | When Resolved | Example |
|---|---|---|---|
| Subtype (OOP) | vtable/interface | Runtime | `Shape s = new Circle(); s.area()` |
| Parametric (Generics) | Type parameters | Compile-time | `List<String>`, `Optional<T>` |
| Ad-hoc (Overloading) | Method signature | Compile-time | `add(int)`, `add(double)` |
| Coercion | Implicit type cast | Runtime/compile | `int + double` (int promoted) |

**How to choose:**

- **Subtype polymorphism:** behavior varies by type;
  new types will be added; Open/Closed matters. Use
  interfaces and strategy/command patterns.
- **Parametric (generics):** same algorithm works for
  many types (sort, map, filter). Use generic methods
  and classes.
- **Overloading:** same conceptual operation with
  different parameter types (format String vs int).
  Keep overloads semantically equivalent.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Polymorphism requires inheritance | Subtype polymorphism via *interface* (no inheritance, just contract) is the most useful form. Interface polymorphism is preferred over class inheritance polymorphism. |
| `instanceof` + casting is "using polymorphism" | `instanceof` checks are the OPPOSITE of polymorphism. They re-introduce the type-switching logic that polymorphism is designed to eliminate. `instanceof` is a design smell. |
| Polymorphism is always the right design | Only use polymorphism for genuine variability. A class with one implementation and no expected variants does not need an interface for polymorphism's sake. YAGNI applies. |
| Method overloading is runtime polymorphism | Overloading is resolved at compile time based on the static type of arguments - it is not dynamic dispatch. Subtype polymorphism IS runtime dispatch; overloading is NOT. |
| Polymorphism makes code slower | JIT compilers optimize monomorphic and bimorphic dispatch (one or two concrete types at a call site) very aggressively, often eliminating vtable overhead entirely via inlining. |

---

### 🚨 Failure Modes & Diagnosis

**Type-Checking Conditionals Defeating Polymorphism**

**Symptom:**
Adding a new variant (payment provider, notification
type, file format) requires changing multiple classes.
`instanceof` or `switch(type)` appears in multiple
places. A code review for "add Braintree payment"
touches 5 files, not 1.

**Root Cause:**
The design uses type-discriminating conditionals instead
of polymorphic dispatch. Each variant's handling code
is embedded in existing methods rather than being
encapsulated in its own class.

**Diagnostic Signal:**

```java
// Search for these patterns - they signal missing polymorphism:
// grep -r "instanceof.*PaymentProvider" src/
// grep -r "switch.*paymentType" src/

// Found:
if (provider instanceof StripeProvider) {
    // stripe logic
} else if (provider instanceof PaypalProvider) {
    // paypal logic
}
// This block is duplicated in 4 other methods.
```

**Fix:** Create a `PaymentProvider` interface with the
required method(s). Move each `if` branch to the
corresponding implementation class. Inject the
implementation; the caller never checks the type.

---

**Liskov Substitution Principle Violation**

**Symptom:**
A subclass overrides a method with behavior that violates
the parent's contract. Callers using the parent type
get unexpected exceptions or wrong results when a specific
subclass is provided.

**Root Cause:**
The subclass does not truly satisfy the parent's
contract (LSP violation). It "extends" the parent class
but changes semantics in ways callers cannot predict.

**Diagnostic Signal:**

```java
// Classic LSP violation: Square extends Rectangle.
// Rectangle contract: setWidth/setHeight are independent.
// Square must maintain width == height: setting width
// also changes height, violating caller expectations.
Rectangle r = new Square(); // valid polymorphism
r.setWidth(5);
r.setHeight(3);
// Caller expects area = 5 * 3 = 15.
// Square returns: area = 3 * 3 = 9. (LSP violated)
```

**Fix:** Use interfaces over inheritance when the IS-A
relationship is weak. `Square` and `Rectangle` should
both implement a `Shape` interface, not inherit from
each other - their contracts are incompatible. Favor
composition over inheritance when the subtype cannot
fully honor the parent's contract.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Object-Oriented Programming (OOP)` - polymorphism
  is one of OOP's four pillars
- `Abstraction` - the interface that makes polymorphism
  possible; the contract all implementations satisfy
- `Encapsulation` - each polymorphic implementation
  hides its own state; callers cannot distinguish
  implementations

**Builds On This (learn these next):**
- `Inheritance` - one mechanism for achieving polymorphism
  through type hierarchies; understand why composition
  is often preferred
- `Composition over Inheritance` - the design principle
  that uses polymorphism (interface-based) rather than
  inheritance-based polymorphism

**Design Patterns Using This:**
- `Strategy` - selects an algorithm (implementation)
  at runtime via polymorphic injection
- `Command` - encapsulates an action as a polymorphic
  object; command queues are type-generic
- `Visitor` - separates algorithms from the objects
  they operate on using double dispatch

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One interface, many implementations;      │
│              │ call site does not know the concrete type │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Type-checking conditionals that must be   │
│ SOLVES       │ updated every time a new variant is added │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Polymorphism makes code Open for extension │
│              │ (new classes) Closed for modification     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple types share behavior; new types  │
│              │ are likely to be added over time          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only one implementation ever; polymorphism│
│              │ for its own sake adds indirection cost    │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ `instanceof` chains and type-switch blocks│
│              │ - these are missing polymorphism markers  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Extensibility + no modification vs vtable │
│              │ indirection and navigation complexity     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Open for extension, closed for           │
│              │ modification - that's polymorphism"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LSP -> Strategy Pattern -> Visitor Pattern│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Polymorphism = one interface, many implementations,
   dispatch at runtime. The caller depends on the
   interface; the type provides the behavior.

2. `instanceof` chains are anti-polymorphism. Every
   `instanceof` check you write is a missed opportunity
   to use polymorphic dispatch. Search your codebase.

3. Polymorphism enables the Open/Closed Principle:
   new variants add new classes; existing code does
   not change; existing tests do not break.

**Interview one-liner:**
"Polymorphism means a single interface can represent
multiple concrete types, and a call through that
interface dispatches to the correct implementation at
runtime. It enables the Open/Closed Principle: you
extend behavior by adding new implementations, not by
modifying existing conditional logic."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Where behavior varies by type, represent it as types,
not as conditionals. This principle applies to every
layer: class design (strategy pattern), microservice
routing (routing rules as objects), event processing
(handler registration by event type). Anywhere you
find `if/switch/case` on a type discriminator, ask:
"Should this be polymorphism instead?"

**Where else this pattern appears:**

- **HTTP framework routing** - `GET /users` and
  `POST /users` are handled by different implementations
  registered against the same route. The framework
  dispatches polymorphically. You extend by registering
  new handlers; the framework core never changes.
- **Kafka consumer handler registration** - each message
  type maps to a handler implementation. Adding a new
  message type: add a new handler class and register
  it. No changes to the dispatch infrastructure.
- **JUnit test extensions** - `@BeforeEach`, lifecycle
  callbacks, and test runners are interfaces implemented
  by extensions. JUnit's core calls the interface methods;
  the extensions provide the behavior. JUnit is open
  for extension (new extension classes), closed for
  modification (JUnit core code).

---

### 💡 The Surprising Truth

Java's `Comparator` interface enabled an architectural
insight: you can sort ANY list by ANY criteria without
the elements knowing they will be sorted. Before
`Comparator`, objects had to implement `Comparable` -
they knew about sorting. `Comparator` is parametric and
subtype polymorphism combined: a `Comparator<User>` can
sort users by name, by age, by signup date, by last
login - the same `Collections.sort()` call handles all
of them. The list does not change; the User class does
not change; only the polymorphic `Comparator` implementation
changes. This is the power of parametric polymorphism
over ad-hoc specialization: `Comparator` was so successful
that Java 8 made it a `@FunctionalInterface` and added
lambda support specifically for it - the most commonly
passed `Comparator` is a one-liner lambda. Polymorphism
enables a design so general that it outlasts programming
paradigm shifts.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain what happens at the JVM level
   when `shape.area()` is called on a `Shape` reference
   that holds a `Circle` instance, including the role
   of the vtable and class pointer.

2. **[DEBUG]** Find all `instanceof` checks in a codebase
   that check against types in a common hierarchy and
   refactor them to polymorphic dispatch using an interface
   or abstract class.

3. **[DECIDE]** In a code review, a developer proposes
   adding a `notificationType` field to a `Notification`
   class and handling it with a switch statement. Explain
   why this is wrong and propose a polymorphic design
   that follows Open/Closed Principle.

4. **[BUILD]** Implement a `ShippingCostCalculator` with
   three strategies: standard (3% of order value),
   express (flat $15), and free over $100. Use an
   interface and three implementations. The checkout
   service should never check which strategy is active.

5. **[EXTEND]** Identify a Liskov Substitution Principle
   violation in the `Square extends Rectangle` hierarchy
   and explain why `instanceof` in the `area()` test
   that verifies LSP would be a code smell - even in
   test code.

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `List.add()` is polymorphic: calling it
on an `ArrayList`, `LinkedList`, or `CopyOnWriteArrayList`
dispatches to different implementations. But all three
share the `List` interface contract. Now consider: is
`null` a valid argument to `List.add(null)`? The
interface says yes; some implementations (`CopyOnWriteArrayList`,
certain Map-backed implementations) throw `NullPointerException`.
What does this tell you about LSP compliance in Java's
standard library, and what does it imply for how you
should design polymorphic interfaces?

*Hint: Think about what "satisfying the interface contract"
means when the interface's Javadoc says "null permitted"
but implementations refuse null. Is this an LSP violation?*

**Q2.** The Visitor pattern uses double dispatch to
achieve what looks like polymorphism on the operation
side rather than the type side. Explain the "expression
problem": why is it hard to add both new types AND new
operations to a polymorphic hierarchy simultaneously
without modifying existing code? What does the Visitor
pattern sacrifice to solve the "new operation" side?

*Hint: Adding a new type to `Shape` with standard
polymorphism (new class implements interface) is easy.
Adding a new operation (say "serialize to SVG") to all
shapes - what has to change? Now think about what
Visitor does differently.*

**Q3.** Go uses structural typing (duck typing) rather
than nominal typing for interfaces: a type satisfies
an interface if it has all the required methods, with
no `implements` declaration needed. Java requires
explicit `implements`. What are the trade-offs of each
approach for polymorphism? When does structural typing
cause problems that nominal typing prevents?

*Hint: Think about accidental interface satisfaction:
a type that happens to have `read()` and `write()` methods
might satisfy an `io.ReadWriter` interface even though
it was not designed for I/O. What breaks? When is this
actually a feature, not a bug?*

---

### 🎯 Interview Deep-Dive

**Q1: Explain the Liskov Substitution Principle with a
concrete example of a violation and why it matters for
real code correctness.**

*Why they ask:* LSP is foundational for interface design;
violations cause hard-to-debug runtime failures in code
that "looks correct." Tests depth beyond knowing the
definition.

*Strong answer includes:*
- Definition: if S extends T, code using T should work
  correctly with S without modification
- Violation example: `ReadOnlyList extends ArrayList` -
  ReadOnlyList throws `UnsupportedOperationException`
  for `add()`. Code that calls `list.add(item)` fails
  at runtime with ReadOnlyList despite the compiler
  allowing it. The T contract (add works) is violated.
- Real consequence: `Collections.unmodifiableList()`
  wraps a list and throws for mutation. Callers who
  receive `List<T>` and call `add()` get a surprise
  at runtime - a LSP violation in the standard library.
- Fix: express the contract honestly. A `ReadableList`
  interface with only read methods; `MutableList`
  extending it with mutation methods. ReadOnlyList
  satisfies `ReadableList` but not `MutableList`.

**Q2: How does polymorphism relate to testability?
Why does `new SmtpEmailService()` inside a business
class make it hard to test?**

*Why they ask:* Connects polymorphism to a practical
consequence developers care about - unit testing.

*Strong answer includes:*
- `new SmtpEmailService()` inside a class: the class
  is tightly coupled to the concrete implementation;
  tests must run a real SMTP server or fail
- With interface + injection: in tests, inject
  `InMemoryEmailService` (captures emails in a list);
  no SMTP server needed; tests run in milliseconds
- The interface is the seam (Michael Feathers' term):
  the join between the testable part (business logic)
  and the untestable part (SMTP calls)
- Polymorphism enables mock/stub injection: Spring's
  `@MockBean`, Mockito's `mock()` - these replace the
  concrete implementation with a test double at the
  polymorphic interface
- Rule: if a class is hard to test in isolation, look
  for concrete dependencies (`new`, static calls) that
  should be polymorphic interfaces

**Q3: What is the Open/Closed Principle, and how does
polymorphism implement it? Give a real system design
example.**

*Why they ask:* Tests ability to connect OOP principles
to system design, not just individual class design.

*Strong answer includes:*
- OCP: a module is open for extension (new behavior
  can be added), closed for modification (existing code
  is not changed to accommodate new behavior)
- Polymorphism implements OCP: the "open for extension"
  is "create a new class implementing the interface";
  the "closed for modification" is "all callers already
  call the interface; they don't change"
- System design example: a fraud detection system with
  rules: each rule is a class implementing
  `FraudRule.evaluate(Transaction)`. The fraud engine
  calls the interface for each rule. Adding a new rule:
  add a new class, register it. The fraud engine
  (core business logic, fully tested) is never modified.
- Scale: a fraud detection system with 100 rules
  implemented via OCP: the engine code has been
  unchanged for 3 years; rules are added weekly.
  The same system with if/else: the engine has been
  modified 100 times, accumulating technical debt and
  risk with each extension.
