---
id: CSF-041
title: Composition over Inheritance
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-015, CSF-040
used_by: DPT-001, DPT-002, DPT-009
related: CSF-016, SAP-001, DPT-004
tags: [composition, inheritance, delegation, solid, design-principles]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/csf/composition-over-inheritance/
---

⚡ TL;DR - Prefer assembling objects from collaborators
(composition) over extending parent classes (inheritance).
Composition creates loosely coupled, testable designs.
Inheritance creates fragile hierarchies. GoF Rule: "Favor
object composition over class inheritance."

| #041 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-015 (Polymorphism), CSF-040 (Interfaces vs Abstract Classes) | |
| **Used by:** | DPT-001 (Strategy Pattern), DPT-002 (Decorator), DPT-009 (Bridge) | |
| **Related:** | CSF-016 (Encapsulation), SAP-001 (SOLID), DPT-004 (Template Method) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Every new behavior is obtained by extending an existing class.
You need logging in `OrderService`? Extend `LoggingBase`.
You need caching? Extend `CachingBase`. You need metrics?
Extend `MetricsBase`. But a class can only extend ONE
other class. So you pick one, and you cannot pick the others.
Or worse, you build a tower: `MetricsBase extends CachingBase
extends LoggingBase extends Object`. Now your domain class
is buried 4 levels deep and picks up all behavior from
all ancestors whether it needs it or not.

**THE BREAKING POINT:**

The fragile base class problem: you change `LoggingBase.log()`
to flush the buffer differently. Suddenly `OrderService`
(which extends `LoggingBase`) breaks - not because you
changed `OrderService`, but because you changed its ancestor.
The class you changed is 4 levels above in the hierarchy.
Finding all the places that break requires understanding
the entire inheritance tree. Tests fail with no obvious
connection to the change you made.

**THE INVENTION MOMENT:**

The Gang of Four (Design Patterns, 1994) codified the
principle: "Favor object composition over class inheritance."
The insight: inheritance couples the subclass to the parent
class implementation. Composition couples to an interface
(the collaborator's contract), not the implementation.
Changing the collaborator's implementation does not break
the containing class if the interface is preserved.
Dependency Injection frameworks (Spring, Guice) made
composition the dominant pattern in enterprise Java by
making it trivial to inject collaborators rather than
inherit them.

---

### 📘 Textbook Definition

**Composition:** A class achieves behavior by holding
references to other objects (collaborators) and delegating
work to them. The class "has-a" collaborator rather than
"is-a" parent.

**Inheritance:** A class acquires behavior from a parent
class via the IS-A relationship. The subclass reuses
(and may override) the parent's methods and state.

**The principle:** When choosing between obtaining behavior
via inheritance (extending a class) versus composition
(holding a reference to a collaborator), prefer composition.
Use inheritance only when a genuine IS-A relationship
exists that is permanent and the Liskov Substitution
Principle holds.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of "be a Thing to do Thing's work," "have a Thing
and ask it to do the work."

**One analogy:**

> Inheritance: you are a chef, so you are also a dishwasher,
> a delivery driver, and a restaurant manager - because
> "RestaurantStaff" does all of these, and you inherited from it.
> You want to be a chef, not all of those things.
>
> Composition: you are a chef who HAS a dishwasher, HAS a
> delivery driver, HAS an assistant. You delegate the work
> to each. You do not have to be them to use their skills.

**One insight:**

Spring beans are composition in action. `OrderService` has
an `OrderRepository`, a `PaymentGateway`, a `NotificationService`.
None of these are inherited. All are injected. You can swap
`PaymentGateway` from Stripe to Braintree by changing the
injected bean - `OrderService` code does not change.
If `OrderService` extended `StripePaymentBase`, switching
payment providers would require rewriting `OrderService`.

---

### 🔩 First Principles Explanation

**WHY INHERITANCE CREATES COUPLING:**

```
┌──────────────────────────────────────────────────────┐
│ Inheritance coupling:                                │
│                                                      │
│   class OrderService extends LoggingBase {           │
│     void placeOrder(Order o) {                       │
│       log("Order: " + o.id());  // calls parent's   │
│       // ...logic...                                 │
│     }                                                │
│   }                                                  │
│                                                      │
│ What OrderService is coupled to:                     │
│   - LoggingBase's fields                             │
│   - LoggingBase's protected methods                  │
│   - LoggingBase's constructor                        │
│   - Any future changes to LoggingBase               │
│   - LoggingBase's inheritance chain above it         │
│                                                      │
│ Composition coupling:                                │
│                                                      │
│   class OrderService {                               │
│     private final Logger logger;  // interface       │
│     void placeOrder(Order o) {                       │
│       logger.info("Order: {}", o.id());              │
│     }                                                │
│   }                                                  │
│                                                      │
│ What OrderService is coupled to:                     │
│   - Logger INTERFACE (contract only, not impl)       │
└──────────────────────────────────────────────────────┘
```

**THE DELEGATION PATTERN:**

Composition with delegation forwards method calls to the
collaborator. The outer class controls what it delegates
and can add behavior around the delegation:

```
┌──────────────────────────────────────────────────────┐
│ class MetricsOrderService implements OrderService {  │
│   private final OrderService delegate; // composed   │
│   private final MetricRegistry metrics;              │
│                                                      │
│   void placeOrder(Order o) {                         │
│     long start = System.nanoTime();                  │
│     try {                                            │
│       delegate.placeOrder(o);           // delegate  │
│       metrics.counter("order.success").inc();        │
│     } catch (Exception e) {                          │
│       metrics.counter("order.failure").inc();        │
│       throw e;                                       │
│     } finally {                                      │
│       metrics.timer("order.time").update(            │
│           System.nanoTime() - start, NANOSECONDS);   │
│     }                                                │
│   }                                                  │
│ }                                                    │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE INHERITANCE EXPLOSION:**

You have `Duck`. It extends `Animal`. Now you need:
`FlightlessDuck`, `RubberDuck`, `WildDuck`, `TameDuck`.
Each needs different combinations of swim/fly/quack behavior.
With inheritance:

```
Animal
  Duck (swims)
    FlightlessDuck (swims, cannot fly)
    WildDuck (swims, flies, quacks)
      TameWildDuck (swims, flies, quacks, responds to name)
    RubberDuck (squeaks, floats in bath)
```

The hierarchy explodes. `RubberDuck` inherits `swim()` from
`Duck` even though rubber ducks do not swim. The class
is forced to override and disable inherited behavior.

With composition:

```java
class Duck {
    private final FlyBehavior flyBehavior;    // interface
    private final QuackBehavior quackBehavior; // interface
    private final SwimBehavior swimBehavior;   // interface

    Duck(FlyBehavior f, QuackBehavior q, SwimBehavior s) { ... }
}

// Create any combination:
Duck rubberDuck = new Duck(NO_FLY, SQUEAK, FLOAT_IN_BATH);
Duck wildDuck   = new Duck(FLY_WITH_WINGS, QUACK, SWIM);
```

This is the Strategy pattern - behaviors are composed,
not inherited. Any combination is possible without
creating a new class for each combination.

---

### 🎯 Mental Model / Analogy

**LEGO BRICKS:**

Composition: assemble from interchangeable bricks. A car
model uses chassis bricks, wheel bricks, window bricks.
Swap the wheels (different wheel behavior) without rebuilding
the entire car. Each brick is independent and reusable in
other models.

Inheritance: a special car brick that permanently includes
the chassis. To use different wheels, you must make a new
special car brick with different wheels built in.

**MEMORY HOOK:**

"HAS-A beats IS-A for behavior reuse.
Composition: hold a reference to the interface.
Delegation: forward the call to the collaborator.
Strategy pattern = composition in action.
Decorator pattern = composed, wraps the interface.
If you extend a class just to reuse code (not because
of IS-A), it's wrong - compose instead."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Instead of being many things to do many jobs, get helpers
who each know one job. A chef who has a dishwasher, a sous-chef,
and a delivery driver, instead of being all of them.

**Level 2 - Student:**
```java
// Composition: PaymentService HAS a gateway
class PaymentService {
    private final PaymentGateway gateway; // hold an interface
    void charge(Order o) { gateway.charge(o.total()); }
}
// vs Inheritance: PaymentService IS a StripeGateway
class PaymentService extends StripeGateway {
    void charge(Order o) { super.charge(o.total()); } // tightly coupled
}
```
Composition lets you swap the gateway. Inheritance locks you to Stripe.

**Level 3 - Professional:**
The Strategy pattern formalizes composition: a context object
holds a strategy interface. The strategy implements one behavior.
You can swap strategies at runtime. `Comparator<T>` is a strategy:
`list.sort(Comparator.comparing(User::name))` - the sort algorithm
is composed with the comparison strategy. Swapping the comparator
changes the sort key without changing the sort algorithm.

**Level 4 - Senior Engineer:**
The Decorator pattern wraps composition: a decorator implements
the same interface as its delegate and adds behavior around
the delegation. `BufferedInputStream wraps InputStream`:
`new BufferedInputStream(new FileInputStream("file.txt"))`.
The `BufferedInputStream` IS-AN `InputStream` (interface),
HAS-AN `InputStream` (the delegate). Each decorator is an
independent, composable unit of behavior. Spring AOP's
proxy-based advice IS the Decorator pattern applied at runtime.

**Level 5 - Expert:**
Mixin-like composition in Java via default interfaces vs Scala traits.
Java: `interface Auditable { default void audit() { ... } }`.
Classes implement `Auditable` and get the default behavior.
Scala traits can also have state (vals, vars) and constructors,
making them more powerful mixins. Kotlin data classes and
delegation: `class LoggingService(val service: Service) : Service by service` -
Kotlin generates all `Service` methods that forward to `service`.
This is compiler-assisted delegation (composition), eliminating
the boilerplate of manually writing `fun foo() = service.foo()`
for every method. This is the same principle as Java composition
but with language-level support.

---

### ⚙️ How It Works (Formal Basis)

**LISKOV SUBSTITUTION PRINCIPLE (LSP) AS THE INHERITANCE GUARD:**

```
┌──────────────────────────────────────────────────────┐
│ Inheritance is justified ONLY when LSP holds:        │
│                                                      │
│   If B extends A:                                    │
│   - Every place where A is used, B must work         │
│   - B must not violate A's contracts                 │
│   - B must not throw exceptions A does not throw     │
│   - B must not strengthen preconditions              │
│   - B must not weaken postconditions                 │
│                                                      │
│ VIOLATION (use composition instead):                 │
│   class Square extends Rectangle {                   │
│     @Override setWidth(int w) {                      │
│       super.setWidth(w);                             │
│       super.setHeight(w); // Square enforces equal   │
│     }                                                │
│   }                                                  │
│   // Violates: code that sets width, then height     │
│   // independently breaks for Square                 │
│   // Square IS-NOT-A Rectangle (in Liskov sense)     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Inheritance for Behavior vs Composition**

```java
// BAD: inheriting for code reuse, not IS-A
class CachingOrderRepository extends JpaOrderRepository {
    private final Cache<UUID, Order> cache;

    @Override
    public Optional<Order> findById(UUID id) {
        return cache.get(id, () -> super.findById(id)); // couples to JPA impl
    }
    // Now: changing JpaOrderRepository can break caching layer
    // Cannot cache a MongoOrderRepository without duplicating
    // the caching logic
}

// GOOD: composition with delegation
class CachingOrderRepository implements OrderRepository {
    private final OrderRepository delegate; // any OrderRepository
    private final Cache<UUID, Order> cache;

    CachingOrderRepository(OrderRepository delegate, Cache<UUID, Order> cache) {
        this.delegate = delegate;
        this.cache = cache;
    }

    @Override
    public Optional<Order> findById(UUID id) {
        // Delegate to whatever OrderRepository is composed in
        return cache.get(id, () -> delegate.findById(id));
    }
    // Works with ANY OrderRepository: JPA, Mongo, in-memory test stub
}
```

**Example 2 - Strategy Pattern (Composition in Action)**

```java
// Strategy interface
interface DiscountStrategy {
    BigDecimal apply(BigDecimal price, Customer customer);
}

// Concrete strategies
class NoDiscount implements DiscountStrategy {
    public BigDecimal apply(BigDecimal price, Customer c) {
        return price;
    }
}

class VipDiscount implements DiscountStrategy {
    public BigDecimal apply(BigDecimal price, Customer c) {
        return price.multiply(BigDecimal.valueOf(0.8)); // 20% off
    }
}

// Context composes the strategy
class PricingEngine {
    private final DiscountStrategy discount; // composed, not inherited

    PricingEngine(DiscountStrategy discount) {
        this.discount = discount;
    }

    BigDecimal price(Order order, Customer customer) {
        return order.items().stream()
            .map(item -> discount.apply(item.price(), customer))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}

// Usage: compose different behaviors at runtime
PricingEngine regular = new PricingEngine(new NoDiscount());
PricingEngine vip     = new PricingEngine(new VipDiscount());
// No subclassing PricingEngine - behavior varies by composing strategies
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Composition over Inheritance means never use inheritance" | No. Inheritance is correct when a genuine IS-A relationship exists AND LSP holds. `ArrayList extends AbstractList` (IS-A List, LSP holds). `List<String>` is not a `List<Object>` (invariance). The principle is: when in doubt, prefer composition. Use inheritance only when it is clearly the better model. |
| "Composition leads to more code (boilerplate delegation)" | Yes, in Java - but this is the cost of explicit, clear contracts. Kotlin's `by` delegation and Lombok's `@Delegate` reduce the boilerplate. Modern Java (Java 17+) with records and sealed types encourages data-centric designs where composition is more natural. The code is longer but more explicit and maintainable than a deep inheritance hierarchy. |
| "Abstract classes are for inheritance - always use them for shared behavior" | Abstract classes are correct for the template method pattern. For cross-cutting behavior (logging, caching, auditing), composition (via Spring AOP, decorators, or direct injection) is almost always better. Using abstract classes for cross-cutting concerns creates tight coupling and inheritance explosions. |
| "If two classes share 80% of the same code, they should inherit" | Code sharing is NOT a justification for inheritance. If they share code but are NOT in an IS-A relationship, extract the shared code to a collaborator (common service, utility class) and inject it. Inheritance for code reuse (without IS-A) violates the Liskov Substitution Principle and creates fragile hierarchies. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Inheritance Hierarchy Explosion**

**Symptom:** Adding a new combination of behaviors requires
creating a new class. The class hierarchy has 20 leaf classes
each handling a specific combination of 5 boolean behaviors.

**Root Cause:** Behavior is encoded in inheritance
(`ClassWithFeatureAandB extends ClassWithFeatureA`).
New combinations require new classes.

**Fix:** Identify the dimensions of variation. Extract each
dimension as a strategy interface. Compose strategies in
the context class. For N behavior dimensions with 2 options each,
composition gives 2^N combinations from N interfaces; inheritance
requires 2^N classes.

**Failure Mode 2: Fragile Base Class**

**Symptom:** You change a protected method in a base class
to fix a bug. Several subclasses break in unrelated ways
because they override the method in ways that assumed the
old behavior.

**Root Cause:** Subclasses depend on the IMPLEMENTATION
of the parent class, not just its interface contract.
`super.method()` calls establish an implicit protocol
that is not documented or enforced.

**Diagnosis:** Search for `super.` calls in subclasses.
Each is a coupling point to the parent's implementation.
If a subclass calls `super.method()` and inserts behavior
before/after, any change to `super.method()`'s behavior
could invalidate the subclass's assumptions.

**Fix:** Make the "extension points" explicit: protected
abstract template methods that subclasses must implement
(template method pattern). Document them. Or, better:
replace inheritance with composition.

---

**Security Note:**

Composition over inheritance has a security implication for
privilege escalation. A class that extends a privileged
base class inherits all its capabilities, including privileged
methods and access to protected state. If the subclass
is less carefully reviewed or is contributed by a third
party, it may use inherited privileged capabilities in
unintended ways. Composition is safer: the composing class
only has access to the PUBLIC interface of the collaborator,
not its protected internals. When designing security-sensitive
hierarchies, prefer final classes (cannot be extended) with
composition rather than open hierarchies.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - composition and inheritance are core OOP
  concepts; class and object model required
- `Polymorphism` (CSF-015) - composition relies on polymorphism
  via interfaces for the collaborator's contract
- `Interfaces vs Abstract Classes` (CSF-040) - composition
  uses interfaces as the type boundary for collaborators

**Builds On This (learn these next):**
- `Strategy Pattern` (DPT-001) - the canonical design pattern
  that formalizes composition for variable behavior
- `Decorator Pattern` (DPT-002) - composition that adds
  behavior around a delegate implementing the same interface

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ COMPOSITION  │ HAS-A collaborator (interface type)     │
│              │ Loose coupling, testable, swappable     │
├──────────────┼─────────────────────────────────────────┤
│ INHERITANCE  │ IS-A parent (implementation coupling)   │
│              │ Use only when LSP holds genuinely       │
├──────────────┼─────────────────────────────────────────┤
│ WHEN COMPOSE │ Cross-cutting behavior (log, cache)     │
│              │ Multiple behaviors that combine         │
│              │ Behavior that changes at runtime        │
│              │ Code reuse WITHOUT IS-A relationship    │
├──────────────┼─────────────────────────────────────────┤
│ WHEN INHERIT │ Genuine IS-A + LSP verified             │
│              │ Template method pattern                 │
│              │ Java standard library (AbstractList)    │
├──────────────┼─────────────────────────────────────────┤
│ RED FLAGS    │ Extending to get access to protected    │
│              │ Overriding to DISABLE inherited methods │
│              │ Hierarchy more than 2-3 levels deep     │
│              │ super. calls scattered in subclasses    │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-001 (Strategy), DPT-002 (Decorator) │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Composition couples to the INTERFACE (contract);
   inheritance couples to the IMPLEMENTATION (parent class body).
   When you compose, swapping the collaborator's implementation
   requires no change in the composing class. When you inherit,
   any change to the parent's implementation can affect every
   subclass.
2. Red flags for wrong inheritance: overriding a method to throw
   `UnsupportedOperationException` (you disabled inherited behavior -
   violation of LSP). Extending just to call `super.method()` once
   (you should compose and call the method directly). Hierarchy
   of 4+ levels (deep hierarchies are fragile and confusing).
3. The Strategy and Decorator patterns ARE composition. Any
   Spring bean injection IS composition. `@Autowired` is the Java
   syntax for "this class HAS-A collaborator." Spring enables
   the entire enterprise Java ecosystem to be built on composition,
   not inheritance.

**Interview one-liner:**
"Composition over inheritance means: when you need behavior,
hold a reference to a collaborator (interface) and delegate
to it, rather than inheriting from a class. Composition
couples to the contract; inheritance couples to the implementation.
Use inheritance only when a genuine IS-A relationship holds
and LSP is satisfied. Spring DI, the Strategy pattern, and
the Decorator pattern are all composition in practice."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Composition over inheritance is a specific instance of a
universal software principle: coupling to abstractions
(interfaces, contracts) rather than implementations (concrete
classes, specific instances). This appears everywhere:
Dependency Inversion Principle says "depend on abstractions."
Hexagonal Architecture says "application core depends on
port interfaces, not adapters." REST API clients depend
on the URL schema and JSON contract, not the server's code.
The principle transcends programming languages: in Go,
all types are effectively composed (no class inheritance;
interfaces are structural). In Rust, traits are composed
into types. In JavaScript, prototype chains are used for
inheritance but modern JS heavily uses object composition
via spread operators and mixins. Composition is the
universal mechanism; class inheritance is a specific tool
for specific problems.

**Where else this pattern appears:**

- **Spring Security's filter chain** - Spring Security is a
  composition of security filters. Each filter has one
  responsibility: authentication, authorization, CSRF,
  session management. They are composed into a chain.
  Adding a new security check means adding a new filter
  to the chain - not extending an existing class. The chain
  itself is built by Spring's auto-configuration based on
  what you configure. This is composition with open-closed
  principle: extend behavior by adding to the composition,
  not by modifying existing classes.
- **Kubernetes operator pattern** - A Kubernetes operator
  is a controller that composes: a reconciler (implements
  the reconciliation logic), a cache (watches for changes),
  a rate limiter (prevents thrashing), a leader election
  mechanism (for HA). None of these are inherited; all are
  composed in the operator framework. New operators implement
  the reconciler interface and compose the rest from the
  framework's building blocks.
- **UNIX pipes** - `cat file | grep pattern | sort | uniq | wc -l`
  is composition. Each tool does one thing (interface: stdin -> stdout).
  They compose into complex operations. No tool extends another.
  This is the original composition-over-inheritance in software design.

---

### 💡 The Surprising Truth

The Gang of Four book (Design Patterns, 1994) recommends
"Program to an interface, not an implementation" and
"Favor object composition over class inheritance" in its
very first chapter before any patterns are described.
Most developers remember the 23 patterns; few remember
that the ENTIRE pattern catalog is founded on these two
principles. Every single one of the 23 GoF patterns uses
composition and interfaces as the core mechanism.
The patterns are not clever tricks - they are worked examples
of these two principles applied to specific recurring problems.
Knowing the principles is more valuable than memorizing
the patterns: if you understand composition and programming
to interfaces, you can DERIVE the patterns rather than
memorize them.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** Review a Spring Boot service class and
   count: how many fields are injected (composition) vs
   inherited? For any inheritance relationships, check whether
   LSP holds or whether the class extends for code reuse
   (wrong). Refactor one wrong inheritance to composition.

2. **[APPLY]** Implement the Strategy pattern: a report
   generator that produces CSV, JSON, and PDF output.
   Define a `ReportFormatter` interface. Implement 3 strategies.
   Inject the strategy into the report generator. Show
   that adding a fourth format requires only a new strategy
   class, not modifying the report generator.

3. **[APPLY]** Implement the Decorator pattern: a `UserRepository`
   with caching and logging decorators. Each decorator implements
   the same `UserRepository` interface. Show that the decorators
   can be stacked in any order: `new LoggingDecorator(new CachingDecorator(jpaRepository))`.

4. **[DIAGNOSE]** Given a class with an inheritance hierarchy
   5 levels deep, with protected methods called via `super`
   at 3 levels, identify: which classes violate LSP, which
   use inheritance for code reuse only, and propose a
   refactoring plan using composition.

5. **[EVALUATE]** Evaluate the tradeoffs: a codebase uses
   abstract base classes for 10 entity processors (each
   processor has 3 abstract methods and 7 shared concrete
   methods). Estimate the cost of refactoring to composition
   vs the long-term maintenance cost of the current design.
   State the conditions under which you would keep the
   abstract class design.

---

### 🧠 Think About This Before We Continue

**Q1.** Spring AOP creates a PROXY around a bean to add
behavior (e.g., `@Transactional`). The proxy implements
the same interface as the original bean and delegates to
the original for each method call, adding behavior around
the delegation. What design pattern is this? Why does
Spring AOP fail when a method in the same class calls
another method in the same class (self-invocation)?

*Hint: Spring AOP's proxy is the DECORATOR pattern.
The proxy implements `OrderService` (interface) and delegates
to the real `OrderService` bean for each method call.
Self-invocation fails because: when `orderService.outer()`
is called from OUTSIDE the bean, the call goes through
the proxy (which applies the AOP advice). When `outer()`
internally calls `this.inner()`, it calls directly on the
real object (not through the proxy). `this` is the target
object, not the proxy. So `@Transactional` on `inner()`
is ignored for self-invocations - the proxy never intercepts.
Fix: inject the proxy into the bean itself (`@Autowired private OrderService self`) or restructure to avoid self-invocation.*

**Q2.** The `BufferedInputStream` wraps `FileInputStream` in Java:
`new BufferedInputStream(new FileInputStream("file.txt"))`.
`BufferedInputStream` IS-AN `InputStream` (inheritance for
the type contract) AND HAS-AN `InputStream` (composition for
the behavior delegation). Is this composition or inheritance?
Why does Java's IO library use this design for all its streams?

*Hint: It is BOTH - this is the Decorator pattern.
`BufferedInputStream` uses inheritance to be an `InputStream`
(so it can be used anywhere an `InputStream` is expected)
but composes/delegates to another `InputStream` for the
actual I/O. This design lets you stack decorators: `new
DataInputStream(new BufferedInputStream(new GZIPInputStream(new FileInputStream("file.gz"))))`.
Each layer adds one behavior: GZIP decompression, buffering,
typed data reading. No inheritance hierarchy explosion;
just composable layers each implementing the same `InputStream`
interface.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is 'Composition over Inheritance'? Give a real example."**

*Why they ask:* Core OOP design principle. Tests whether
the candidate thinks in terms of design, not just syntax.

*Strong answer includes:*
- Composition: the class holds a reference to a collaborator
  (interface type) and delegates work to it. HAS-A relationship.
  Coupling to the interface, not the implementation.
- Inheritance: the class acquires behavior from a parent.
  IS-A relationship. Coupling to the parent's implementation.
- Real example: Spring's `@Autowired` is composition.
  `OrderService` HAS-A `OrderRepository` - not IS-AN `OrderRepository`.
  You can swap `JpaOrderRepository` for a test stub without
  changing `OrderService`. With inheritance, swapping
  the implementation requires changing the class hierarchy.
- When to use inheritance: genuine IS-A + LSP verified.
  `ArrayList extends AbstractList` (IS-A List, works everywhere
  a List is expected). Not for code reuse.

**Q2: "What is the fragile base class problem? How does composition solve it?"**

*Why they ask:* Tests depth of understanding of inheritance risks.

*Strong answer includes:*
- Fragile base class: a parent class change breaks subclasses
  that depended on the old behavior, even without changing
  the subclasses. Caused by protected methods and `super`
  calls that establish implicit behavior contracts.
- Example: `AbstractList.removeRange(int, int)` is called
  by `clear()`. If a subclass overrides `removeRange` in
  a way that assumes `clear()` will NOT call it (because
  it was documented differently in an old version), a change
  to `AbstractList` that makes `clear()` call `removeRange`
  breaks the subclass.
- Composition fix: the class delegates to a collaborator
  via the interface. Changes to the collaborator's implementation
  do not affect the delegating class if the interface
  (contract) is preserved. There are no protected methods,
  no `super` calls, no implicit implementation contracts.

**Q3: "How does the Strategy pattern use composition? Walk me through a Spring Boot example."**

*Why they ask:* Tests practical pattern knowledge and Spring fluency.

*Strong answer includes:*
- Strategy: a context holds a strategy interface; behavior
  varies by which strategy is injected.
- Spring example:
  `interface NotificationStrategy { void send(Notification n); }`
  `@Component class EmailNotification implements NotificationStrategy { ... }`
  `@Component class SmsNotification implements NotificationStrategy { ... }`
  `class NotificationService { @Autowired NotificationStrategy strategy; ... }`
- In Spring Boot, if multiple beans implement the strategy,
  use `@Qualifier` or `@ConditionalOnProperty` to select.
  Or: inject `Map<String, NotificationStrategy> strategies`
  and select by key at runtime.
- The composing class (`NotificationService`) does not
  know or care which implementation is injected. Swapping
  SMS for email is a config change, not a code change.
