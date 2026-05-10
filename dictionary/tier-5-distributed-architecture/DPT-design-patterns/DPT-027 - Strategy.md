---
layout: default
title: "Strategy"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /design-patterns/strategy/
id: DPT-027
category: Design Patterns
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
status: complete
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-027 - Strategy

⚡ TL;DR - Strategy defines a family of algorithms, encapsulates each one, and makes them interchangeable so behaviour can vary independently from the clients that use it.

| DPT-027 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Composition over Inheritance, Polymorphism | |
| **Used by:** | Sorting Algorithms, Payment Processing, Compression, Routing Logic | |
| **Related:** | State, Template Method, Command, Decorator, Policy Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce platform supports payment by credit card, PayPal, and bank transfer. The `CheckoutService.processPayment()` method contains a large `if/else` chain: `if (method == CREDIT_CARD) { ... } else if (method == PAYPAL) { ... } else if (method == BANK) { ... }`. Adding Apple Pay requires modifying `CheckoutService` - core checkout logic changes every time a payment partner is added or removed. Integration tests for credit card break when PayPal code is modified.

**THE BREAKING POINT:**
Every new payment provider touches production code. A bug in the new PayPal integration could crash credit card processing. The checkout service becomes a 500-line class tightly coupled to every payment provider's SDK. Testing requires mocking providers that are irrelevant to the test scenario. The Open/Closed Principle is violated at every new feature.

**THE INVENTION MOMENT:**
This is exactly why the Strategy pattern was created. Each payment algorithm is encapsulated behind a `PaymentStrategy` interface. `CheckoutService` holds a `PaymentStrategy` and calls `strategy.process(amount)`. Adding Apple Pay = adding a new class. Zero changes to checkout.

**EVOLUTION:**
Strategy was a cornerstone pattern for algorithm substitution
in pre-lambda Java. The explicit Strategy interface + multiple
ConcreteStrategy classes became boilerplate-heavy. Java 8
(2014) transformed Strategy: a `Comparator` lambda replaces
a `ComparatorStrategy` class; a sorting algorithm is passed
as a `Function`. Template Method's static structure gave
way to Strategy's dynamic composition. Modern Java uses
`java.util.function` interfaces (Predicate, Function,
Consumer) as single-method Strategy contracts. Spring's
`ResourceLoader`, `TransactionManager`, and `CacheManager`
are injectable Strategy interfaces used throughout the framework.

---

### 📘 Textbook Definition

The **Strategy** pattern is a behavioural design pattern that defines a family of algorithms, encapsulates each one in a separate class behind a common interface, and makes them interchangeable at runtime. The **Context** holds a reference to a `Strategy` interface and delegates the algorithm execution to it. The Context and Strategy interact through the interface - Concrete Strategies are interchangeable from the Context's perspective.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Swap the algorithm inside an object without changing the object itself.

**One analogy:**
> A GPS navigation app (Context) can route you via fastest route, shortest route, or avoid-tolls route. Each routing algorithm (Strategy) is swappable. The map display, turn-by-turn voice, and ETA calculation are identical regardless of strategy. You pick the strategy at start; the app uses it without needing to know which one you chose.

**One insight:**
Strategy's core value is that the CHOICE of algorithm and the USE of algorithm are separated. The context doesn't choose - a caller does. The context just executes whatever it was given. This inversion of control is what makes behaviour injectable and testable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Multiple algorithms solve the same problem differently; the client should not be coupled to any specific one.
2. The algorithm must be substitutable without modifying the context.
3. The context must not know which specific algorithm it is using.

**DERIVED DESIGN:**
Given invariant 1+3: define a `Strategy` interface with an `execute()` method (or whatever the algorithm signature is). All concrete algorithms implement this interface. The Context depends only on `Strategy`, never on `CreditCardStrategy` or `PayPalStrategy`.

Given invariant 2: the Context accepts a `Strategy` via constructor or setter. The algorithm can be injected at construction time (immutable strategy) or changed at runtime (mutable strategy).

The pattern is essentially "composition over inheritance." Without Strategy, you'd have subclasses: `CheckoutServiceWithCreditCard`, `CheckoutServiceWithPayPal`. Strategy gives you the same flexibility via composition - swap the algorithm object without creating a new Context subclass.

**THE TRADE-OFFS:**
**Gain:** Algorithms interchangeable without modifying context; each strategy independently testable; new strategies added without modifying existing code; strategies injectable (great for testing).
**Cost:** More classes (one per strategy); clients must know about all available strategies to select one; if strategies are few and rarely change, a simple if/else may be cleaner.

---

### 🧪 Thought Experiment

**SETUP:**
A `DataExporter` needs to export records as CSV, JSON, or Excel. Each format has a different serialisation algorithm.

**WHAT HAPPENS WITHOUT STRATEGY:**
`DataExporter.export(format)` has `if (format==CSV) { ... csv logic ... } else if (format==JSON) { ... json logic ... }`. Adding XML requires modifying `DataExporter`. The JSON exporter and the CSV exporter share a class - a bug in JSON can prevent CSV exports from compiling.

**WHAT HAPPENS WITH STRATEGY:**
`DataExporter` holds a `ExportStrategy strategy`. Three classes exist: `CsvExportStrategy`, `JsonExportStrategy`, `ExcelExportStrategy` - each implementing `ExportStrategy`. `DataExporter.export()` calls `strategy.serialize(data)`. Adding XML = one new class. DataExporter never changes.

**THE INSIGHT:**
Strategy separates "what we're exporting" (context's responsibility) from "how we serialize" (strategy's responsibility). The variant part of the algorithm is isolated from the invariant part.

---

### 🧠 Mental Model / Analogy

> Strategy is like interchangeable blades on a kitchen knife handle. The handle (Context) stays the same - your grip, your motion, your skill. The blade (Strategy) determines what you can cut: bread knife for bread, paring knife for fruit, carving knife for meat. You swap the blade; the handle never changes.

- "Knife handle" → Context
- "Blade" → Strategy (interface)
- "Specific blade type" → Concrete Strategy (BreadKnifStrategy, etc.)
- "Swapping the blade" → `context.setStrategy(new BreadKnifeStrategy())`
- "Cutting motion" → `context.execute()` → delegates to `strategy.cut()`

Where this analogy breaks down: in cooking, blades must be physically compatible with the handle. In code, the Strategy interface provides this compatibility guarantee at compile time - any class implementing the interface is guaranteed to fit the context.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Strategy is a pattern where you plug different "algorithms" into an object from outside, like a USB device. The object works the same way regardless of which algorithm you plug in.

**Level 2 - How to use it (junior developer):**
Create a `Strategy` interface with the method signature of the varying behaviour. Create one concrete class per algorithm, each implementing the interface. The `Context` class has a `Strategy` field, set via constructor or setter. In `Context.doWork()`, call `strategy.execute()`. In Java, simple strategies can be passed as lambdas since Java 8: `context.setStrategy(data -> data.sort(...))`.

**Level 3 - How it works (mid-level engineer):**
Strategies are stateless by preference - they take input and return output without mutating internal fields. This makes them thread-safe singletons: one `CsvExportStrategy` instance can serve thousands of simultaneous exports. If a strategy is stateful (e.g., maintains a cursor through a multi-page export), it must be scoped per-request. Spring's `@Bean` with `scope = "prototype"` or `ThreadLocal` handles this. In Spring, strategies are naturally injected as beans: `@Autowired private List<PaymentStrategy> strategies` gives you all registered strategy beans for registry-based selection.

**Level 4 - Why it was designed this way (senior/staff):**
Strategy is the GoF formalisation of the function-as-first-class-citizen concept that functional programming languages had from the start. In Java 8+, a `@FunctionalInterface` IS a strategy: `Comparator`, `Predicate`, `Function` are all single-method interfaces - the compiler enforces the contract, and lambdas provide implementation without ceremony. The pre-Java-8 GoF Strategy pattern required full class declarations; lambdas made it fluent. The pattern remains explicitly useful when strategies have multiple methods or carry configuration state. The "Policy" naming in some frameworks (`SecurityPolicy`, `RetryPolicy`) is almost always Strategy under a domain name.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────┐
│  STRATEGY PATTERN - MECHANISM                 │
│                                               │
│  Client                                       │
│    ↓ chooses strategy                         │
│    ↓ injects into context                     │
│                                               │
│  Context                                      │
│  ┌────────────────────────────────────┐       │
│  │ strategy: Strategy (interface)     │       │
│  │                                    │       │
│  │ execute():                         │       │
│  │   return strategy.run(data)        │       │
│  └────────────────────────────────────┘       │
│           │ delegates                         │
│    ┌──────┼──────────────┐                    │
│    ↓      ↓              ↓                    │
│  CsvStrat JsonStrat  ExcelStrat               │
│  run(d)   run(d)     run(d)                   │
│  = csv    = json     = xlsx                   │
└───────────────────────────────────────────────┘
```

**Selection and injection steps:**
1. Client determines which algorithm is needed (based on user choice, config, or runtime condition)
2. Client instantiates (or retrieves from registry) a concrete strategy
3. Client injects strategy into context: `new Context(strategy)` or `context.setStrategy(strategy)`
4. Client calls `context.execute(input)`
5. Context delegates: `strategy.run(input)`
6. Concrete strategy executes its algorithm, returns result
7. Context returns result to client

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
HTTP POST /export?format=csv
  → ExportController.export(format)
  → strategyRegistry.get(format)
            ← YOU ARE HERE (Strategy selected)
  → new DataExporter(csvStrategy)
  → exporter.exportAll(records)
  → csvStrategy.serialize(records)
  → returns CSV bytes
  → HTTP 200 with CSV content
```

**FAILURE PATH:**
```
format = "xml" - no strategy registered
  → strategyRegistry.get("xml") returns null
  → NullPointerException or
  → IllegalArgumentException("Unknown format: xml")
Fix: registry.get() throws or returns Optional;
     caller handles gracefully
```

**WHAT CHANGES AT SCALE:**
With 10,000 concurrent exports, stateless strategy singletons scale perfectly - one `JsonStrategy` instance serves all threads simultaneously. Stateful strategies (maintaining per-export cursor state) must be prototype-scoped. At very high throughput, strategy selection overhead (registry lookup, null check) is negligible compared to the I/O of the export itself.

---

### 💻 Code Example

**Example 1 - Payment strategy:**
```java
// Strategy interface
public interface PaymentStrategy {
    void pay(BigDecimal amount, String orderId);
}

// Concrete strategies
public class CreditCardStrategy implements PaymentStrategy {
    private final String cardToken;

    public CreditCardStrategy(String cardToken) {
        this.cardToken = cardToken;
    }

    @Override
    public void pay(BigDecimal amount, String orderId) {
        // charge via Stripe API using cardToken
        stripeClient.charge(cardToken, amount, orderId);
    }
}

public class PayPalStrategy implements PaymentStrategy {
    private final String paypalEmail;

    @Override
    public void pay(BigDecimal amount, String orderId) {
        paypalClient.transfer(paypalEmail, amount, orderId);
    }
}

// Context
public class CheckoutService {
    private final PaymentStrategy paymentStrategy;

    public CheckoutService(PaymentStrategy strategy) {
        this.paymentStrategy = strategy;
    }

    public void checkout(Cart cart) {
        BigDecimal total = cart.calculateTotal();
        String orderId = orderRepo.create(cart);
        paymentStrategy.pay(total, orderId);
        // No if/else - strategy handles the rest
    }
}

// Usage
CheckoutService service =
    new CheckoutService(new CreditCardStrategy(token));
service.checkout(cart);

// Swap with PayPal - zero changes to CheckoutService
CheckoutService ppService =
    new CheckoutService(new PayPalStrategy(email));
```

**Example 2 - Lambda strategy (Java 8+):**
```java
// Functional interface (single-method)
@FunctionalInterface
public interface SortStrategy<T> {
    List<T> sort(List<T> items);
}

public class DataProcessor<T> {
    private SortStrategy<T> sortStrategy;

    public void setSortStrategy(SortStrategy<T> s) {
        this.sortStrategy = s;
    }

    public List<T> process(List<T> data) {
        return sortStrategy.sort(data);
    }
}

// Client injects lambdas as strategies
DataProcessor<Integer> proc = new DataProcessor<>();

proc.setSortStrategy(items ->
    items.stream().sorted().collect(toList())); // ascending

proc.setSortStrategy(items ->
    items.stream()
         .sorted(Comparator.reverseOrder())
         .collect(toList())); // descending
```

**Example 3 - Registry-based strategy selection:**
```java
// Strategy registry: maps keys to strategy beans
@Configuration
public class ExportConfig {
    @Bean
    public Map<String, ExportStrategy> strategies(
        CsvExportStrategy csv,
        JsonExportStrategy json,
        ExcelExportStrategy excel) {

        return Map.of("csv", csv, "json", json, "xlsx", excel);
    }
}

@Service
public class ExportService {
    private final Map<String, ExportStrategy> registry;

    public ExportService(Map<String, ExportStrategy> registry) {
        this.registry = registry;
    }

    public byte[] export(String format, List<Record> data) {
        ExportStrategy strategy = Optional
            .ofNullable(registry.get(format))
            .orElseThrow(() ->
                new UnsupportedFormatException(format));
        return strategy.serialize(data);
    }
}
```

---

### ⚖️ Comparison Table

| Pattern | When Algorithm Changes | Who Selects | Self-Transitions | Best For |
|---|---|---|---|---|
| **Strategy** | At creation or explicitly | Caller/client | No | Interchangeable algorithms |
| State | Automatically on event | State itself | Yes | Lifecycle state machines |
| Template Method | Never (skeleton fixed) | N/A (inheritance) | No | Algorithm with fixed steps |
| Command | On command execution | Invoker | No | Undo/redo, queuing operations |

How to choose: use Strategy when the CALLER controls which algorithm runs and it may change per request. Use State when the OBJECT automatically picks its behaviour based on its current state.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strategy and State are the same pattern | State transitions itself; Strategy is selected by the client. State owns the switching logic; Strategy has no switching logic - the client does |
| Strategy always requires a separate class per algorithm | Java lambdas and method references ARE strategies for single-method interfaces; no class required |
| Strategy should replace all if/else chains | Only chains where alternatives are cleanly interchangeable algorithms justify Strategy; simple flag checks do not |
| The context must not be aware of which strategy is active | The context can LOG which strategy is active or choose between strategies via a registry - it just should not contain the algorithm logic itself |
| Strategies must be stateless | Strategies CAN be stateful; this just means they cannot be singletons. Stateless strategies are preferred for thread safety |

---

### 🚨 Failure Modes & Diagnosis

**1. Null Strategy - NullPointerException on Execute**

**Symptom:** `NullPointerException` at `context.execute()`. Occurs when strategy was never set or when strategy registry lookup returned null.

**Root Cause:** `strategy` field was never injected, or registry didn't contain the requested key.

**Diagnostic:**
```bash
# Spring: check bean wiring
./gradlew test --tests "*ContextTest*"
# In application logs:
grep "No qualifying bean of type.*Strategy" app.log
```

**Fix:**
```java
// BAD: no null guard
public class Context {
    private Strategy strategy; // may be null!
    public void execute() { strategy.run(); } // NPE

// GOOD: guard in constructor + Optional in registry
public class Context {
    private final Strategy strategy;

    public Context(Strategy strategy) {
        this.strategy = Objects.requireNonNull(
            strategy, "Strategy must not be null");
    }
}
```

**Prevention:** Use constructor injection with `Objects.requireNonNull`. For registry-based selection, use `Optional.ofNullable(...).orElseThrow()`.

---

**2. Strategies Not Thread-Safe When Stateful**

**Symptom:** Race condition in exports: one user's data appears in another user's export. Unpredictable output under concurrent load.

**Root Cause:** A stateful strategy (e.g., `ExcelExportStrategy` holds a `Workbook` instance) is registered as a Spring singleton and shared between multiple requests.

**Diagnostic:**
```bash
# Check Spring bean scope
grep -r "@Scope" src/ --include="*.java"
# Stateful strategy beans with no @Scope = singleton = shared
```

**Fix:**
```java
// BAD: stateful singleton strategy
@Component // singleton by default!
public class ExcelExportStrategy implements ExportStrategy {
    private Workbook workbook; // per-export state: WRONG

// GOOD: prototype scope for stateful strategies
@Component
@Scope("prototype")
public class ExcelExportStrategy implements ExportStrategy {
    private Workbook workbook; // new instance per request
```

**Prevention:** Stateless strategies → singleton. Stateful strategies → prototype scope or created per-request in a factory.

---

**3. Strategy Registry Missing New Variant**

**Symptom:** Adding a new export format (XML) results in `UnsupportedFormatException` even though `XmlExportStrategy` was implemented. The new strategy is simply not registered.

**Root Cause:** The registry (Map) in config or factory was not updated with the new strategy bean.

**Diagnostic:**
```bash
# Log all registered strategies at startup:
registry.keySet().forEach(k ->
    log.info("Registered strategy: {}", k));
# If "xml" not in list: not registered
```

**Fix:**
```java
// Use Spring auto-discovery instead of manual map:
// All beans implementing ExportStrategy are auto-injected
@Autowired
private List<ExportStrategy> strategies;

// Build registry from a discriminator method:
public ExportService(List<ExportStrategy> strategies) {
    this.registry = strategies.stream()
        .collect(toMap(
            ExportStrategy::supportedFormat,
            Function.identity()));
}
```

**Prevention:** Use Spring's `@Autowired List<Interface>` to auto-discover all strategy beans; registry is built automatically when new strategies are added to the Spring context.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Interface` - the Strategy interface is the contract; all concrete strategies must implement it for interchangeability
- `Composition over Inheritance` - Strategy is the canonical example of this principle in action; algorithms composed in, not inherited
- `Polymorphism` - `context.strategy.execute()` dispatches polymorphically to the correct concrete strategy

**Builds On This (learn these next):**
- `Template Method` - closely related; Template Method uses inheritance to vary algorithm steps; Strategy uses composition to vary the whole algorithm
- `Dependency Injection Pattern` - Strategy injection is a primary use case of DI; strategies are injected as beans in Spring
- `Policy Pattern` - the domain-specific application of Strategy in frameworks (RetryPolicy, SecurityPolicy, CacheEvictionPolicy)

**Alternatives / Comparisons:**
- `State` - changes behaviour automatically as state transitions occur; Strategy changes only when caller sets a new strategy
- `Decorator` - adds behaviour to an existing algorithm; Strategy replaces the algorithm entirely
- `Command` - encapsulates an action for queuing or undo; Strategy encapsulates an algorithm for immediate execution

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Plug-in interchangeable algorithms via    │
│              │ a common interface                        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multiple algorithm variants hardcoded in  │
│ SOLVES       │ context via if/else; change requires edit │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The CALLER selects the algorithm; the     │
│              │ context just executes - no conditionals   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple interchangeable algorithms for   │
│              │ the same task; algorithm varies by config │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only one algorithm ever; simple conditio- │
│              │ nal is clearer and easier to read         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Open/Closed compliance vs extra classes   │
│              │ and explicit strategy selection logic     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tell me HOW to do it - I'll do the       │
│              │  rest the same way regardless."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Template Method → State →                 │
│              │ Dependency Injection Pattern              │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate the algorithm (the how) from the context that uses
it (the what). Express the algorithm as a first-class value
that can be substituted at runtime. The context becomes
algorithm-agnostic.

**Where else this pattern appears:**
- **Sorting algorithms:** `List.sort(comparator)` accepts any
  `Comparator` -- `naturalOrder()`, `reverseOrder()`, or a
  custom multi-key comparator. The list's sort mechanism is
  the context; the comparator is the strategy.
- **Payment processing:** A `PaymentService` accepts a
  `PaymentStrategy` -- `StripeStrategy`, `PayPalStrategy`,
  `CryptoStrategy`. The processing workflow is fixed; the
  payment mechanism is substitutable.
- **Compression utilities (zip, gzip, brotli):** I/O stream
  compressors accept a `Codec` strategy -- the stream wrapper
  is fixed; the compression algorithm is substituted per format.

---

### 💡 The Surprising Truth

Java 8 lambdas made Strategy so lightweight that many developers
stopped recognising it as a pattern. `list.sort((a, b) ->
a.age - b.age)` is a Strategy pattern -- the lambda is a
`Comparator` (concrete strategy), passed to `sort()` (the
context). The pattern did not disappear with lambdas; it became
invisible because Java's functional interface mechanism
eliminates the need for an explicit strategy class. The lesson:
patterns manifest differently in different language generations.
In Java 14+, `switch` expressions with sealed interfaces can
replace Strategy entirely for finite algorithm sets -- the
pattern evolves as the language evolves.
---

### 🧠 Think About This Before We Continue

**Q1.** A `PricingEngine` uses a `DiscountStrategy` to calculate order discounts. In production, 10 different strategies exist: seasonal, loyalty, bulk, employee, etc. Each order type requires a different combination of strategies (e.g., loyalty + bulk together). A single `DiscountStrategy` interface assumption breaks - you need to apply multiple strategies and combine results. Describe two design approaches that extend the Strategy pattern to support composable multi-strategy execution, and identify the trade-offs of each.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A `SortStrategy` is injected into a `DataGrid` component that displays thousands of rows. The strategy is currently selected at page-load time from user preferences. The PM now wants to make sorting strategy switchable in real-time as the user interacts. Trace the exact design change needed, describe the thread-safety risks when switching strategies on a live grid that is simultaneously being rendered, and prescribe the fix.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A `ReportGenerator` uses Strategy
to select between PDF, Excel, and HTML output formats. A new
requirement: "generate all three formats simultaneously."
Modify the design to support multi-strategy execution, then
evaluate whether the result is still Strategy or has evolved
into Composite, Observer, or a different pattern.

*Hint: The First Principles CORE INVARIANTS say one strategy
is selected at a time. When multiple strategies execute
simultaneously, the context has changed -- map this to the
Composite pattern (DPT-014) or a collection-based dispatcher.*
