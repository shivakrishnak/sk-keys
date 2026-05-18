---
id: DPT-027
title: Strategy
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-026
used_by: DPT-039, DPT-064, DPT-073
related: DPT-026, DPT-028, DPT-019, DPT-039
tags:
  - pattern
  - behavioral
  - intermediate
  - algorithm
  - dependency-injection
  - solid
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/design-patterns/strategy/
---

⚡ TL;DR - Strategy defines a family of algorithms,
encapsulates each one, and makes them interchangeable -
separating the algorithm's behavior from the context
that uses it, enabling runtime algorithm selection.

| #27 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-026 | |
| **Used by:** | DPT-039, DPT-064, DPT-073 | |
| **Related:** | DPT-026, DPT-028, DPT-019, DPT-039 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A payment service supports: credit card, PayPal, and
bank transfer. The payment method is chosen at runtime:

```java
void processPayment(String method, Payment p) {
    if ("CARD".equals(method)) {
        // 30 lines of card processing
    } else if ("PAYPAL".equals(method)) {
        // 25 lines of PayPal processing
    } else if ("BANK".equals(method)) {
        // 35 lines of bank transfer processing
    }
}
```

**THE BREAKING POINT:**
Adding Stripe: modify `processPayment()` (90 lines, high
risk). Every payment method change touches this method.
Testing one method requires stubbing the others.
The method grows indefinitely with new payment methods.

**THE INVENTION MOMENT:**
Strategy: extract each payment algorithm into its own class:
`CardPaymentStrategy`, `PayPalStrategy`, `BankTransferStrategy`.
`PaymentService` holds a `PaymentStrategy` reference and
calls `strategy.process(payment)`. The caller injects the
correct strategy. Adding Stripe: one new class.
Zero changes to `PaymentService`.

**EVOLUTION:**
Java's `Comparator<T>` is Strategy: different sort
orderings are different strategies passed to `Collections.sort`.
Spring's `ResourceLoader`, `CacheManager`, `TransactionManager`,
`PasswordEncoder` are all Strategy interfaces. Dependency
Injection frameworks ARE built on Strategy: injected
beans are interchangeable strategies for the injection
point. Every Spring `@Service` that can have multiple
implementations used via its interface is Strategy in action.

---

### 📘 Textbook Definition

The **Strategy** pattern is a Behavioral design pattern
that defines a family of algorithms, encapsulates each
one in a class, and makes them interchangeable. Strategy
lets the algorithm vary independently from clients that
use it. The Context class delegates execution to a
Strategy object; the client selects which Strategy to
inject. The Context calls the Strategy interface; it does
not know the concrete Strategy implementation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Strategy replaces "if A then algorithm1, else if B then
algorithm2" with "inject the right algorithm as an object."

**One analogy:**
> Google Maps (Context) with three transport strategies:
> DRIVE, WALK, BIKE. Each strategy knows the optimal
> route calculation for its mode. Google Maps calls
> `selectedStrategy.buildRoute(origin, destination)`.
> Switching from driving to biking: inject BikeStrategy.
> Google Maps code is unchanged; only the strategy changes.

**One insight:**
Strategy is the most fundamental application of the
Open/Closed Principle: the context is CLOSED for modification
when adding algorithms; the family of strategies is OPEN
for extension by adding new strategy classes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The Context holds a reference to a Strategy interface;
   it never references concrete strategy classes directly.
2. The Strategy is interchangeable at runtime (injected
   by the client or factory).
3. The Strategy interface defines the WHAT (what operation
   to perform); concrete strategies define the HOW.

**DERIVED DESIGN:**
Two key participants:
- **Strategy interface**: defines the algorithm's signature
  (`execute(context, params): result`).
- **ConcreteStrategy**: implements one algorithm.
- **Context**: holds a `Strategy` reference; calls
  `strategy.execute(...)`.

**INJECTION MODES:**
- **Constructor injection**: strategy is set at creation,
  immutable (recommended for most cases).
- **Setter injection**: strategy can be changed at runtime.
- **Method parameter**: strategy passed on each call
  (`sort(list, comparatorStrategy)`) - most flexible.

**TRADE-OFFS:**

**Gain:** Open/Closed Principle. Algorithms testable in
isolation. Client chooses algorithm without knowing its
implementation. Eliminates conditional branching.

**Cost:** Client must know all available strategies to
choose the right one (or a factory chooses). Slight
overhead from interface dispatch (minor, usually irrelevant).
Over-engineering risk: if only one algorithm exists and
a second is not anticipated, Strategy adds unnecessary
abstraction.

---

### 🧪 Thought Experiment

**SETUP:**
A text compressor with three algorithms: ZIP, GZIP,
BROTLI. The compressor must be configurable per-file
type (images prefer BROTLI, logs prefer GZIP, archives
prefer ZIP).

**WITHOUT STRATEGY:**
`Compressor.compress(data, algorithm)` has three branches.
Adding LZ4 requires modifying `Compressor`.

**WITH STRATEGY:**
```java
interface CompressionStrategy { byte[] compress(byte[] data); }
class ZipStrategy implements CompressionStrategy { ... }
class GzipStrategy implements CompressionStrategy { ... }
class BrotliStrategy implements CompressionStrategy { ... }

class Compressor {
    private CompressionStrategy strategy;
    Compressor(CompressionStrategy s) { this.strategy = s; }
    byte[] compress(byte[] data) {
        return strategy.compress(data); // one line
    }
}
// Compressor never changes when adding LZ4. Zero modification.
```

---

### 🧠 Mental Model / Analogy

> Strategy is a POWER TOOL with interchangeable heads.
> The drill body (Context) is the same. The bits (Strategies)
> are: flat-head, Phillips, hex, Torx. Same trigger, same
> handle. Swap the bit for the job. You would not buy a
> separate drill for each screw type.

- "Drill body" = Context
- "Bit" = ConcreteStrategy
- "Swapping bits" = changing strategy at runtime
- "Knowing which bit to use" = client or factory decides

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Strategy means "one main object, many interchangeable
ways to do the work." The main object (context) does not
care HOW the work is done - it asks a strategy object
to do it. You can swap the strategy without changing
the context.

**Level 2 - How to use it (junior developer):**
Create an interface for the varying algorithm. Create one
class per algorithm. The context holds a reference to
the interface (not the concrete class). The client or
factory injects the right concrete class. The context
calls the interface method.

**Level 3 - How it works (mid-level engineer):**
`java.util.Comparator<T>` is the most-used Strategy in
Java. `Collections.sort(list, comparator)` - the comparator
IS the strategy for "how to compare two elements." The
sort algorithm (merge sort in Java) calls
`comparator.compare(a, b)` without knowing the concrete
comparator. `Comparator.naturalOrder()`, `reversed()`,
`thenComparing()` are different strategies. Java 8 lambdas:
`list.sort((a, b) -> a.name().compareTo(b.name()))` -
the lambda IS a `Comparator` strategy.

**Level 4 - Why it was designed this way (senior/staff):**
Strategy is how frameworks achieve extensibility without
modification. Spring's `PasswordEncoder` interface
(BCryptPasswordEncoder, Argon2PasswordEncoder, etc.) is
Strategy: the `UserDetailsService` calls `passwordEncoder
.encode(rawPassword)` without knowing the algorithm.
Swapping from BCrypt to Argon2: inject a different
strategy. The authentication code does not change.
Security algorithms can evolve independently of the
authentication framework. This is also why Dependency
Injection IS essentially Strategy: every injected bean
at an interface injection point is a pluggable strategy.

**Level 5 - Mastery (distinguished engineer):**
Strategy is the structural implementation of the Dependency
Inversion Principle: "high-level modules should not depend
on low-level modules; both should depend on abstractions."
The Context (high-level) depends on the Strategy interface
(abstraction). ConcreteStrategies (low-level implementations)
implement the abstraction. The DI container injects the
appropriate ConcreteStrategy at runtime. When Strategy
is applied at the architectural level (e.g., pluggable
databases, storage backends, messaging systems), it becomes
the "Ports and Adapters" (Hexagonal Architecture) pattern:
the Port IS the Strategy interface; the Adapter IS the
ConcreteStrategy; the Domain (Context) depends only on
the Port.

---

### ⚙️ How It Works (Mechanism)

```
Strategy Pattern for Payment
┌─────────────────────────────────────────────────────────┐
│ <<interface>> PaymentStrategy                           │
│   + processPayment(Payment p): PaymentResult            │
│                                                         │
│ CardPaymentStrategy implements PaymentStrategy          │
│   + processPayment(p): charge card via Stripe API       │
│                                                         │
│ PayPalStrategy implements PaymentStrategy               │
│   + processPayment(p): redirect to PayPal, poll result  │
│                                                         │
│ BankTransferStrategy implements PaymentStrategy         │
│   + processPayment(p): initiate ACH/SWIFT transfer      │
│                                                         │
│ PaymentService (Context)                                │
│ - strategy: PaymentStrategy  ← injected, not hard-coded │
│ + PaymentService(PaymentStrategy s): this.strategy = s  │
│ + checkout(Payment p): PaymentResult                    │
│     return strategy.processPayment(p)  ← delegates      │
│                                                         │
│ PaymentService never references CardPaymentStrategy etc.│
│ Knows only PaymentStrategy interface                    │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
User selects "Pay with PayPal"

Factory/DI:
  strategy = new PayPalStrategy(paypalApiKey)
  paymentService = new PaymentService(strategy)

paymentService.checkout(payment):
  → strategy.processPayment(payment)
  → PayPalStrategy: redirects to PayPal OAuth
  → PayPal confirms payment
  → PayPalStrategy returns PaymentResult.SUCCESS

Adding Stripe:
  class StripePaymentStrategy implements PaymentStrategy {
    ... }
  strategy = new StripePaymentStrategy(stripeApiKey)
  // PaymentService code: UNCHANGED
```

---

### 💻 Code Example

**Example 1 - Without Strategy (if/else proliferation):**

```java
// BAD: algorithm selection via if/else - grows forever
class RouteCalculator {
    Route buildRoute(Location from, Location to, String mode) {
        if ("DRIVE".equals(mode)) {
            // road network graph traversal, traffic weights
            // 40 lines...
        } else if ("WALK".equals(mode)) {
            // pedestrian paths, walking speed
            // 30 lines...
        } else if ("BIKE".equals(mode)) {
            // bike lanes, elevation, cycling speed
            // 35 lines...
        }
        // Adding TRANSIT: modify this method (risky)
        throw new IllegalArgumentException("Unknown: " + mode);
    }
}
```

**Example 2 - Strategy pattern:**

```java
// GOOD: each algorithm is its own class

interface RouteStrategy {
    Route buildRoute(Location from, Location to);
}

class DrivingStrategy implements RouteStrategy {
    @Override
    public Route buildRoute(Location from, Location to) {
        // road network graph, traffic weights
        return roadGraphAlgo.find(from, to, trafficData);
    }
}

class WalkingStrategy implements RouteStrategy {
    @Override
    public Route buildRoute(Location from, Location to) {
        // pedestrian paths
        return pedestrianGraph.find(from, to);
    }
}

class CyclingStrategy implements RouteStrategy {
    @Override
    public Route buildRoute(Location from, Location to) {
        // bike lanes, elevation-aware
        return bikeGraph.find(from, to, elevationData);
    }
}

// Context: knows only the Strategy interface
class Navigator {
    private RouteStrategy strategy;

    Navigator(RouteStrategy strategy) {
        this.strategy = strategy;
    }

    // Strategy can be changed at runtime
    void setStrategy(RouteStrategy strategy) {
        this.strategy = strategy;
    }

    Route navigate(Location from, Location to) {
        return strategy.buildRoute(from, to); // delegate
    }
}

// Client: selects the strategy
Navigator nav = new Navigator(new DrivingStrategy());
Route route = nav.navigate(home, office);

// Switch to walking
nav.setStrategy(new WalkingStrategy());
route = nav.navigate(home, park);
// Navigator code: UNCHANGED

// Adding TransitStrategy:
class TransitStrategy implements RouteStrategy { ... }
nav.setStrategy(new TransitStrategy());
// Navigator: UNCHANGED
```

**Example 3 - Java's Comparator as Strategy:**

```java
// RECOGNITION: Comparator IS Strategy

List<Employee> employees = getEmployees();

// Different strategies for different sort requirements
employees.sort(Comparator.comparing(Employee::getName));
// by name
employees.sort(Comparator.comparing(Employee::getSalary));
// by salary
employees.sort(
    Comparator.comparing(Employee::getDepartment)
        .thenComparing(Employee::getName));  // composed

// Lambda as anonymous strategy:
employees.sort((a, b) -> a.getHireDate().compareTo(b.getHireDate()));

// Collections.sort takes the strategy as parameter
// It knows nothing about the comparison logic
// Each Comparator is a ConcreteStrategy
```

**Example 4 - Spring PasswordEncoder (Strategy in framework):**

```java
// Spring Security uses Strategy for password encoding

// Strategy interface:
// PasswordEncoder { String encode(CharSequence raw); boolean
// matches(); }

// ConcreteStrategies:
@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);   // BCrypt strategy
    // or: return new Argon2PasswordEncoder(); // Argon2 strategy
    // or: return new SCryptPasswordEncoder(); // SCrypt strategy
}

// Context (AuthenticationService): knows only the interface
@Service
class AuthService {
    @Autowired
    private PasswordEncoder encoder; // injected strategy

    boolean authenticate(String raw, String hashed) {
        return encoder.matches(raw, hashed); // strategy call
    }
    // Swapping BCrypt to Argon2: change the @Bean.
    // AuthService code: UNCHANGED.
}
```

**How to test/verify correctness:**
Test each strategy class independently: given input, verify
output is correct for that strategy. Test the Context
separately: verify it correctly delegates to the strategy
(mock the strategy, verify the mock was called with the
right arguments).

---

### ⚖️ Comparison Table

| Pattern | # algorithms | Selected by | Changes at runtime | Intent |
|---|---|---|---|---|
| **Strategy** | Many | Client/DI | Yes | Algorithm family |
| State | Many | State itself | Yes (transitions) | Lifecycle phases |
| Template Method | One skeleton, many hooks | Subclass (fixed) | No | Algorithm skeleton |
| Command | One per command | Client | N/A | Request as object |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strategy requires runtime switching | Strategy enables runtime switching but does NOT require it. If the strategy is set at construction time and never changed, it is still the Strategy pattern - the value is in the decoupling and extensibility, not necessarily runtime switching |
| Strategy is only useful with 3+ algorithms | Strategy is valuable even for ONE algorithm if you anticipate a second or if testability via mocking the strategy is needed. But for truly fixed behavior with no anticipated variation: Strategy adds unnecessary indirection |
| Dependency Injection is not Strategy | DI frameworks use Strategy as their fundamental abstraction: injected dependencies are strategies; injection point types are strategy interfaces. Every Spring `@Autowired` field that accepts multiple possible implementations IS a Strategy injection point |
| Lambda = Strategy is oversimplification | Lambdas CAN implement single-method Strategy interfaces. `(a, b) -> a.compareTo(b)` IS a `Comparator` (Strategy) implementation. Functional interfaces in Java 8+ are specifically designed to enable this: any functional interface is a potential Strategy |

---

### 🚨 Failure Modes & Diagnosis

**Null Strategy Causes NullPointerException**

**Symptom:**
`NullPointerException` at `strategy.processPayment(payment)`.
The Context was created without a strategy being set.

**Root Cause:**
Strategy field is null because it was not set (optional
setter injection, no required guard; or factory returned
null for an unsupported type).

**Fix:**
Use constructor injection + `Objects.requireNonNull()`:
```java
class PaymentService {
    private final PaymentStrategy strategy;

    PaymentService(PaymentStrategy strategy) {
        this.strategy = Objects.requireNonNull(strategy,
            "PaymentStrategy must not be null");
    }
}
// NullPointerException at construction time, not at use
// Much easier to debug
```

**Prevention:**
Prefer constructor injection over setter injection for
required strategies. Use default strategy pattern when
a no-op default is appropriate:
```java
private PaymentStrategy strategy = DEFAULT_STRATEGY;
```

---

**Strategy Leaks Context State**

**Symptom:**
A caching strategy in a web request keeps serving stale
data because a previous request's strategy instance
was cached (wrong scope).

**Root Cause:**
Strategy instances that are stateful (contain per-request
state) were incorrectly shared across requests (e.g.,
stored in a Spring singleton bean's field).

**Fix:**
Stateless strategies: use singletons (created once, shared).
Stateful strategies: create a new instance per scope
(per-request, per-transaction) or use prototype scope
in Spring.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `State` - DPT-026; the structural twin of Strategy;
  understanding State's lifecycle focus clarifies
  Strategy's algorithm-selection focus

**Builds On This (learn these next):**
- `Dependency Injection Pattern` - DPT-039; DI IS the
  Strategy pattern at the framework level
- `Template Method` - DPT-028; Template Method is an
  alternative to Strategy using inheritance vs composition

**Alternatives / Comparisons:**
- `State` - lifecycle transitions; Strategy selects algorithms
- `Template Method` - inheritance-based variation; Strategy
  is composition-based

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Family of interchangeable algorithms;    │
│              │ Context delegates to injected Strategy   │
├──────────────┼──────────────────────────────────────────┤
│ JAVA EXAMPLE │ Comparator<T> (sort strategy),           │
│              │ PasswordEncoder, ResourceLoader          │
├──────────────┼──────────────────────────────────────────┤
│ KEY BENEFIT  │ Open/Closed: add algorithms without      │
│              │ modifying Context (new class, not change)│
├──────────────┼──────────────────────────────────────────┤
│ DI LINK      │ Every Spring @Service at an interface    │
│              │ injection point IS a Strategy            │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Null strategy → NPE at use;              │
│              │ use constructor injection + null check   │
├──────────────┼──────────────────────────────────────────┤
│ VS STATE     │ Strategy: client selects algorithm;      │
│              │ State: object transitions its own state  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Template Method → Visitor → Null Object  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `Comparator<T>` is the canonical Java Strategy: different
   comparators are different strategies passed to sort;
   the sort algorithm delegates comparison without knowing
   the concrete comparator
2. Strategy is how Spring achieves extensibility: every
   interface (`PasswordEncoder`, `TransactionManager`,
   `ResourceLoader`) with multiple implementations is a
   Strategy family - inject a different implementation
   to change behavior
3. Strategy and State: same structure, opposite direction.
   Strategy: "client selects" (passive context, active client).
   State: "object self-transitions" (active context,
   passive client).

**Interview one-liner:**
"Strategy encapsulates interchangeable algorithms, letting
the context delegate behavior to an injected strategy
object without knowing its implementation. Java's Comparator
is the canonical example. Spring's PasswordEncoder, TransactionManager,
and ResourceLoader are Strategy interfaces in the framework.
Every Spring @Service at an interface injection point IS
a Strategy - Dependency Injection IS the Strategy pattern."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When the WHAT is fixed but the HOW varies: use Strategy.
"Sort a list" (what) - the comparison logic (how) varies.
"Process a payment" (what) - the payment method (how)
varies. Extract the "how" to a Strategy interface;
inject the right Strategy for the current context.

**Where else this pattern appears:**
- **Java Streams** - `filter(Predicate)`, `map(Function)`,
  `sorted(Comparator)` - each takes a Strategy for that
  pipeline stage. The stream pipeline IS a Strategy chain.
- **Spring Security** - `AuthenticationProvider` is Strategy:
  many providers (JWT, OAuth, LDAP, in-memory); the
  `ProviderManager` iterates them until one authenticates.
- **Hibernate dialect** - `Database Dialect` (H2Dialect,
  MySQL8Dialect, PostgreSQLDialect) is Strategy: Hibernate
  generates different SQL dialects; the ORM context
  (Session) delegates to the injected dialect.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Why `Collections.sort(list, comparator)` is
   Strategy pattern - name the Context, Strategy interface,
   and ConcreteStrategy in this call
2. [IMPLEMENT] Refactor a payment processor with 3 if/else
   payment methods into the Strategy pattern - verify
   the processor has zero knowledge of concrete strategy
   classes after refactoring
3. [CONNECT] Explain why Spring DI is "Strategy pattern
   at the framework level" - use a Spring service with
   a PasswordEncoder dependency as the example
4. [DISTINGUISH] Describe the same scenario using State
   pattern vs Strategy pattern - explain when each would
   be the better choice

---

### 🎯 Interview Deep-Dive

**Q1: How would you refactor a payment service with a
growing if/else chain to use the Strategy pattern?**

*Why they ask:* Classic Strategy application question -
tests ability to identify the pattern and apply it.

*Strong answer includes:*
- Identify the varying behavior: payment processing algorithm
- Create `PaymentStrategy` interface with `process(Payment)` method
- Extract each if/else branch to its own implementing class
- Context (`PaymentService`) holds `PaymentStrategy` injected
  via constructor
- Client or factory selects the correct strategy and injects it
- Result: adding new payment method = new class, zero
  changes to `PaymentService` (OCP satisfied)

**Q2: What is the difference between Strategy and Template
Method patterns?**

*Why they ask:* Tests the composition vs inheritance
distinction for behavioral variation.

*Strong answer includes:*
- Strategy: COMPOSITION - behavior variation via injected
  object; different strategies are different classes;
  Context-Strategy relationship at runtime
- Template Method: INHERITANCE - behavior variation via
  subclass override; the skeleton algorithm is in the
  base class; varying steps are abstract methods
- Strategy: more flexible (strategies can be swapped at
  runtime; multiple strategies composable); more classes
- Template Method: simpler (fewer classes; variation
  through override); behavior fixed at compile time via
  class selection; cannot swap at runtime
- Modern Java preference: Strategy + lambdas (less class
  proliferation); Template Method less common in modern code

