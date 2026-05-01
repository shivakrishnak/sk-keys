---
layout: default
title: "Strategy Pattern"
parent: "Design Patterns"
nav_order: 785
permalink: /design-patterns/strategy-pattern/
number: "785"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Dependency Injection, Open-Closed Principle"
used_by: "Sorting, payment processing, validation, compression, routing"
tags: #intermediate, #design-patterns, #behavioral, #oop, #solid, #extensibility
---

# 785 — Strategy Pattern

`#intermediate` `#design-patterns` `#behavioral` `#oop` `#solid` `#extensibility`

⚡ TL;DR — **Strategy** defines a family of algorithms, encapsulates each one, and makes them interchangeable — enabling the algorithm to vary independently from clients that use it, and eliminating conditionals that select behavior at runtime.

| #785 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Dependency Injection, Open-Closed Principle | |
| **Used by:** | Sorting, payment processing, validation, compression, routing | |

---

### 📘 Textbook Definition

**Strategy** (GoF, 1994): a behavioral design pattern that defines a family of algorithms, encapsulates each one, and makes them interchangeable. Strategy lets the algorithm vary independently from clients that use it. Components: **Strategy interface** — declares the operation(s) all algorithms implement; **Concrete strategies** — each implements one algorithm variant; **Context** — holds a reference to a strategy and calls it. GoF intent: "Define a family of algorithms, encapsulate each one, and make them interchangeable." Java: `java.util.Comparator<T>` is the canonical Strategy pattern — different comparators = different comparison strategies, injected into `List.sort()`, `TreeMap`, `PriorityQueue`. Also: `java.util.Formatter`, `javax.servlet.http.HttpServlet` (`service()` selects strategy based on HTTP method).

---

### 🟢 Simple Definition (Easy)

Navigation app. Multiple route-finding strategies: `DrivingStrategy`, `WalkingStrategy`, `CyclingStrategy`, `PublicTransitStrategy`. All implement the same interface: `calculateRoute(from, to)`. The navigation app just calls `currentStrategy.calculateRoute(source, destination)`. Switching from driving to walking: swap the strategy object. The app itself doesn't change. New strategy (ScooterStrategy): implement the interface and inject it. Zero changes to the navigation app.

---

### 🔵 Simple Definition (Elaborated)

Payment processing: `checkout.pay(amount)`. Without Strategy: `if (method == CREDIT_CARD) { ... } else if (method == PAYPAL) { ... } else if (method == CRYPTO) { ... }`. With Strategy: each payment method is a `PaymentStrategy`. `checkout.setPaymentStrategy(new CreditCardStrategy(card))`. `checkout.pay(amount)` → calls `strategy.pay(amount)`. New payment method: create new class implementing `PaymentStrategy` — zero changes to `Checkout`. Java's `Comparator<T>` is Strategy: `list.sort(Comparator.comparing(Person::getAge))` — the `Comparator` is the strategy; `sort()` is the context.

---

### 🔩 First Principles Explanation

**How Strategy decouples algorithm selection from algorithm execution:**

```
WITHOUT STRATEGY — CONDITIONAL LOGIC IN CONTEXT:

  class Sorter {
      void sort(List<Integer> data, String algorithm) {
          if (algorithm.equals("bubble")) {
              // bubble sort code...
          } else if (algorithm.equals("quick")) {
              // quick sort code...
          } else if (algorithm.equals("merge")) {
              // merge sort code...
          }
          // Adding new algorithm: MODIFY this method.
          // Testing individual algorithms: can't test in isolation without calling Sorter.
          // Algorithm code mixed with selection logic.
      }
  }
  
WITH STRATEGY PATTERN:

  // STRATEGY INTERFACE:
  @FunctionalInterface
  interface SortStrategy {
      void sort(List<Integer> data);
  }
  
  // CONCRETE STRATEGIES — each algorithm fully encapsulated:
  class BubbleSort implements SortStrategy {
      @Override
      public void sort(List<Integer> data) {
          // bubble sort algorithm — isolated, independently testable
          for (int i = 0; i < data.size() - 1; i++) {
              for (int j = 0; j < data.size() - i - 1; j++) {
                  if (data.get(j) > data.get(j + 1)) {
                      Collections.swap(data, j, j + 1);
                  }
              }
          }
      }
  }
  
  class QuickSort implements SortStrategy {
      @Override
      public void sort(List<Integer> data) { /* quick sort */ }
  }
  
  class TimSort implements SortStrategy {
      @Override
      public void sort(List<Integer> data) { /* tim sort */ }
  }
  
  // CONTEXT:
  class Sorter {
      private SortStrategy strategy;
      
      Sorter(SortStrategy strategy) {
          this.strategy = strategy;    // inject strategy
      }
      
      void setStrategy(SortStrategy strategy) {
          this.strategy = strategy;   // swap at runtime
      }
      
      void sort(List<Integer> data) {
          strategy.sort(data);         // delegate — no algorithm knowledge here
      }
  }
  
  // Client selects strategy:
  Sorter sorter = new Sorter(new QuickSort());
  sorter.sort(data);
  
  sorter.setStrategy(new TimSort());  // switch algorithm at runtime
  sorter.sort(bigData);
  
  // Lambda strategy (Java 8+, @FunctionalInterface):
  sorter.setStrategy(data -> Collections.sort(data));  // strategy as lambda
  
JAVA CANONICAL: java.util.Comparator<T>

  // Comparator<T> IS the Strategy interface.
  // Different comparators = different strategies for comparison.
  // Context = sort(), TreeMap, PriorityQueue.
  
  List<Person> people = ...;
  
  // Strategy 1: sort by age (ascending):
  people.sort(Comparator.comparing(Person::getAge));
  
  // Strategy 2: sort by last name then first name:
  people.sort(Comparator.comparing(Person::getLastName)
                        .thenComparing(Person::getFirstName));
  
  // Strategy 3: custom sort — descending age, nulls last:
  people.sort(Comparator.comparing(Person::getAge, Comparator.reverseOrder())
                        .thenComparing(Comparator.nullsLast(
                            Comparator.comparing(Person::getEmail))));
  
  // TreeMap with custom ordering strategy:
  new TreeMap<>(Comparator.comparing(String::length)
                          .thenComparing(Comparator.naturalOrder()));
  
  // PriorityQueue with custom priority strategy:
  PriorityQueue<Task> taskQueue = new PriorityQueue<>(
      Comparator.comparing(Task::getPriority).reversed()
  );
  
PAYMENT STRATEGY WITH SPRING:

  // Strategy interface:
  interface PaymentStrategy {
      PaymentResult pay(BigDecimal amount, PaymentDetails details);
      boolean supports(PaymentMethod method);
  }
  
  // Concrete strategies:
  @Component
  class CreditCardStrategy implements PaymentStrategy {
      public PaymentResult pay(BigDecimal amount, PaymentDetails details) { ... }
      public boolean supports(PaymentMethod method) { return method == CREDIT_CARD; }
  }
  
  @Component
  class PayPalStrategy implements PaymentStrategy {
      public PaymentResult pay(BigDecimal amount, PaymentDetails details) { ... }
      public boolean supports(PaymentMethod method) { return method == PAYPAL; }
  }
  
  // Context (Strategy Selector + Executor):
  @Service
  class PaymentService {
      private final List<PaymentStrategy> strategies;
      
      @Autowired
      PaymentService(List<PaymentStrategy> strategies) {
          this.strategies = strategies;   // Spring injects ALL PaymentStrategy beans
      }
      
      public PaymentResult processPayment(Order order) {
          PaymentStrategy strategy = strategies.stream()
              .filter(s -> s.supports(order.getPaymentMethod()))
              .findFirst()
              .orElseThrow(() -> new UnsupportedPaymentException(order.getPaymentMethod()));
          
          return strategy.pay(order.getTotal(), order.getPaymentDetails());
          // New payment method: add new @Component implementing PaymentStrategy.
          // PaymentService: zero changes (OCP).
      }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Strategy:
- Algorithm selection mixed with algorithm execution — `if/else` chains in context
- Adding new algorithm: modify context (OCP violation)

WITH Strategy:
→ Context only delegates: `strategy.execute()`. Adding new algorithm: add new class. Context and other strategies: zero changes.
→ Algorithms independently testable: test `QuickSort` directly without going through `Sorter`.

---

### 🧠 Mental Model / Analogy

> A game character with interchangeable weapons. Character is the context. Each weapon is a strategy: `SwordStrategy.attack()` = melee slash; `BowStrategy.attack()` = ranged arrow; `SpellStrategy.attack()` = magic blast. Character calls `currentWeapon.attack(target)`. Switching weapon = switching strategy. Character doesn't need to know the physics of each weapon — just calls `attack()`. New weapon (Grenade): implement the interface, hand to the character.

"Character" = Context (holds reference to current strategy)
"Each weapon" = concrete Strategy class
"character.attack()" = context delegates to strategy.attack()
"Switching weapon" = setStrategy() — replacing the strategy at runtime
"Character doesn't know how weapons work" = decoupling; context ignorant of algorithm details

---

### ⚙️ How It Works (Mechanism)

```
STRATEGY FLOW:

  1. Define Strategy interface (or @FunctionalInterface for lambdas)
  2. Implement each concrete algorithm as a Strategy class
  3. Context holds strategy field; delegates operations to it
  4. Client injects strategy (constructor, setter, or method arg)
  5. Swap strategy at runtime for different behavior

  Pattern variants:
  - Constructor injection: strategy fixed at creation
  - Setter injection: strategy swappable at runtime
  - Method argument: strategy passed per-call (most flexible)
```

---

### 🔄 How It Connects (Mini-Map)

```
Interchangeable algorithms injected from outside; context unaware of implementation
        │
        ▼
Strategy Pattern ◄──── (you are here)
(Strategy interface; context delegates; client selects algorithm)
        │
        ├── State: similar structure but State transitions internally; Strategy injected externally
        ├── Template Method: fixed algorithm skeleton with overridable steps (vs Strategy: entire algorithm swapped)
        ├── Command: encapsulates request; Strategy encapsulates algorithm
        └── Dependency Injection: DI framework selects/injects strategy bean at runtime
```

---

### 💻 Code Example

```java
// Compression strategy — interchangeable algorithms:
@FunctionalInterface
interface CompressionStrategy {
    byte[] compress(byte[] data);
}

// Concrete strategies:
class GzipCompression implements CompressionStrategy {
    @Override
    public byte[] compress(byte[] data) {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
             GZIPOutputStream gzip = new GZIPOutputStream(bos)) {
            gzip.write(data);
            gzip.finish();
            return bos.toByteArray();
        } catch (IOException e) { throw new CompressException(e); }
    }
}

class LZ4Compression implements CompressionStrategy {
    @Override
    public byte[] compress(byte[] data) { return LZ4Factory.fastestInstance().fastCompressor().compress(data); }
}

// No-op strategy for tests or environments where compression is not needed:
class NoCompression implements CompressionStrategy {
    @Override
    public byte[] compress(byte[] data) { return data; }
}

// Context:
class FileStorage {
    private CompressionStrategy compression;
    
    FileStorage(CompressionStrategy compression) {
        this.compression = compression;
    }
    
    void setCompression(CompressionStrategy c) { this.compression = c; }
    
    void store(String filename, byte[] data) {
        byte[] compressed = compression.compress(data);
        storageDriver.write(filename, compressed);
    }
}

// Lambda strategy (inline, no class needed):
FileStorage storage = new FileStorage(data -> Snappy.compress(data));

// Switch strategy at runtime:
storage.setCompression(new GzipCompression());
storage.store("large.bin", largeData);

storage.setCompression(new NoCompression());  // switch for small files
storage.store("config.json", smallData);
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strategy and State are the same pattern | Structurally similar (both delegate to interface). Behavioral difference: Strategy algorithm is selected by the client/externally; context doesn't change it during execution. State: the state transitions happen internally; state objects or context transitions between states. Strategy = what HOW to do something. State = WHAT behavior the object exhibits now. |
| Strategy requires a class per algorithm | Java 8+ functional interfaces make Strategy expressible as a lambda. `SortStrategy sortByAge = list -> list.sort(Comparator.comparing(Person::getAge));` is a valid strategy. Only create a full class when the algorithm has constructor parameters, internal state, or complex behavior. `Comparator.comparing()` chains are typical lambda strategies. |
| Strategy over-engineers simple cases | True for trivial single-use cases. But as soon as you find yourself writing `if (type == X) doX() else if (type == Y) doY()` for algorithm selection, Strategy is the right tool. Especially when new algorithm variants are anticipated, or when algorithms need to be independently testable. |

---

### 🔥 Pitfalls in Production

**Strategy instances maintaining mutable state — not thread-safe:**

```java
// ANTI-PATTERN: stateful strategy — shared across threads breaks:
class StatisticsStrategy implements AnalysisStrategy {
    private List<Double> results = new ArrayList<>();  // ← mutable instance state!
    
    @Override
    public double analyze(List<Double> data) {
        results.addAll(data);       // accumulates across calls
        return results.stream().mapToDouble(Double::doubleValue).average().orElse(0);
    }
}

// If this strategy is a Spring @Bean (singleton), it's shared across all requests:
@Bean
AnalysisStrategy statisticsStrategy() { return new StatisticsStrategy(); }
// Thread A and Thread B both call analyze() → race condition on results list.

// FIX 1: Make strategy stateless — compute from input only:
class StatisticsStrategy implements AnalysisStrategy {
    @Override
    public double analyze(List<Double> data) {
        return data.stream().mapToDouble(Double::doubleValue).average().orElse(0);
        // No instance state. Thread-safe.
    }
}

// FIX 2: If state is needed, make strategy request-scoped or instantiate per-call:
@Bean
@Scope("prototype")  // new instance per injection
AnalysisStrategy statisticsStrategy() { return new StatisticsStrategy(); }

// RULE: Strategy implementations should be stateless.
// If algorithm needs state, pass state via method parameters or create new instance per use.
```

---

### 🔗 Related Keywords

- `State Pattern` — similar structure but strategies transition internally; State describes current mode
- `Template Method Pattern` — fixes algorithm skeleton, overrides steps (vs Strategy: swaps entire algorithm)
- `Command Pattern` — encapsulates a request; Strategy encapsulates an algorithm
- `Dependency Injection` — DI framework injects the right strategy bean based on configuration
- `java.util.Comparator` — canonical Strategy in Java standard library

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Define algorithm family behind interface. │
│              │ Client selects and injects strategy.      │
│              │ Context delegates — doesn't know which.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple algorithm variants; need to swap │
│              │ algorithms at runtime; eliminate if/else  │
│              │ on algorithm type; OCP compliance needed  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only 1-2 algorithms unlikely to change;  │
│              │ algorithm differences are trivial;        │
│              │ overhead of interface outweighs benefit   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Swappable weapons: character just calls │
│              │  attack() — sword, bow, spell all work;   │
│              │  swap weapon without changing character." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ State Pattern → Template Method Pattern → │
│              │ Command Pattern → java.util.Comparator    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `java.util.Comparator<T>` is arguably the most widely used Strategy pattern in the Java ecosystem. It's also a `@FunctionalInterface`, making every lambda that compares two objects a strategy. Java 8 added `Comparator.comparing()`, `thenComparing()`, `reversed()`, `nullsFirst()`, `nullsLast()` — all returning new `Comparator` instances via composition. This is Strategy + Decorator (composing strategies). How do `Comparator.comparing(keyExtractor).thenComparing(secondKeyExtractor)` work internally? What design pattern does the `thenComparing()` chain represent?

**Q2.** Spring's `List<PaymentStrategy>` injection (injecting all beans implementing a given interface) is a powerful Spring idiom that enables open-closed extension: add new `@Component PaymentStrategy` implementations without modifying `PaymentService`. But this introduces an implicit dependency: the `PaymentService` assumes exactly one strategy will match for any given payment method. If two strategies both return `supports(CREDIT_CARD) == true`, behavior depends on bean ordering. How would you design `PaymentService` to handle this ambiguity safely? Consider: using `@Primary`, `@Order`, or changing `findFirst()` to explicit priority ordering.
