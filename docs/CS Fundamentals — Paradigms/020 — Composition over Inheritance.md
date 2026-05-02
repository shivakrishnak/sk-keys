---
layout: default
title: "Composition over Inheritance"
parent: "CS Fundamentals — Paradigms"
nav_order: 20
permalink: /cs-fundamentals/composition-over-inheritance/
number: "0020"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Inheritance, Encapsulation, Polymorphism
used_by: Design Patterns, SOLID Principles, Software Architecture Patterns
related: Inheritance, Strategy Pattern, Dependency Injection
tags:
  - intermediate
  - mental-model
  - first-principles
  - pattern
  - tradeoff
  - bestpractice
---

# 020 — Composition over Inheritance

⚡ TL;DR — Compose objects from smaller, focused behaviours rather than building deep inheritance hierarchies — it produces more flexible, maintainable code.

| #020 | Category: CS Fundamentals — Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Inheritance, Encapsulation, Polymorphism | |
| **Used by:** | Design Patterns, SOLID Principles, Software Architecture Patterns | |
| **Related:** | Inheritance, Strategy Pattern, Dependency Injection | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

You model a video game with inheritance. `Character` is the base. `FlyingCharacter extends Character`. `SwimmingCharacter extends Character`. Now you need a character that can both fly and swim. Java doesn't allow `extends FlyingCharacter, SwimmingCharacter`. You create `FlyingSwimmingCharacter extends FlyingCharacter` and copy-paste the swimming logic. Later: `FlyingShootingCharacter`, `SwimmingShootingCharacter`, `FlyingSwimmingShootingCharacter`. The explosion of subclasses is called the "combinatorial explosion" problem.

**THE BREAKING POINT:**

With n independent behaviours, inheritance requires 2^n subclasses to cover all combinations. Four behaviours (fly, swim, shoot, stealth) = 16 subclasses. Each new ability doubles the hierarchy. The hierarchy becomes unmanageable at 3–4 orthogonal dimensions. You can't give a character new abilities at runtime — inheritance is static.

**THE INVENTION MOMENT:**

This is exactly why "composition over inheritance" was formalised as a principle in _Design Patterns_ (Gang of Four, 1994) — to replace behaviour stacking via class hierarchy with behaviour assembly via object combination. Instead of `extends FlyingSwimmingCharacter`, the character _has_ a `MovementStrategy` and an `AttackStrategy` — components that can be mixed, matched, and swapped at runtime without touching the character's class.

---

### 📘 Textbook Definition

**Composition over inheritance** is a design principle stating that objects should achieve polymorphic behaviour and code reuse by _containing_ instances of other classes that implement the desired behaviour (composition) rather than by _inheriting_ from classes that provide that behaviour (inheritance). A "has-a" relationship (the object holds a component) is preferred over an "is-a" relationship (the object is a subtype) whenever the goal is behaviour reuse rather than type substitutability. Composition creates loose coupling (the component can be replaced at runtime), while inheritance creates tight coupling (the relationship is fixed at compile time).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Build objects by combining small, focused pieces rather than stacking on a deep family tree.

**One analogy:**

> Building with LEGO bricks (composition) vs carving from stone (inheritance). With LEGO, you assemble complex structures from small, reusable pieces — add or remove bricks freely. With stone carving, you start from a block and chip away — hard to add, hard to change, shapes are set in stone.

**One insight:**
Inheritance is a compile-time contract: you can't change what a `FlyingCharacter` is at runtime. Composition is a runtime configuration: you can give any character a `FlyingAbility` object at any time. This flexibility is the core reason composition wins for behaviour reuse — inheritance wins only for stable type hierarchies.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Inheritance is a static, compile-time relationship — you cannot change what a class extends at runtime.
2. Composition is a dynamic, runtime relationship — you can swap components via assignment or dependency injection.
3. An object needs to _be a type_ (use inheritance) but it can _have behaviours_ from many sources (use composition).

**DERIVED DESIGN:**

With inheritance: behaviour comes from the class hierarchy — fixed at compile time. To change behaviour, you need a different subclass.

With composition: behaviour comes from composed objects — changeable at runtime. To change behaviour, swap the component.

```
INHERITANCE MODEL:
  Character → FlyingCharacter → FlyingShootingCharacter
  (static, 2^n explosion, runtime flexibility = zero)

COMPOSITION MODEL:
  Character has:
    movementStrategy: MovementStrategy (Flying, Swimming, Walking)
    attackStrategy: AttackStrategy (Shooting, Melee, Magic)

  At runtime: character.setMovement(new FlyingMovement())
              character.setAttack(new ShootingAttack())
  Combinations: n × m instead of 2^(n+m)
```

**THE TRADE-OFFS:**

Composition gain: runtime flexibility, no combinatorial explosion, loose coupling, easy testing (mock components), no fragile base class.
Composition cost: more boilerplate (delegation — must forward calls to components), sometimes less readable ("what strategy does this object have?"), requires designing component interfaces upfront.

Inheritance gain: simpler syntax, automatic method availability, clear type hierarchy, less boilerplate.
Inheritance cost: rigid, static, fragile, prevents multiple behaviour combinations.

---

### 🧪 Thought Experiment

**SETUP:**
Build a notification system. Currently: `EmailNotifier`. Requirements change: SMS support. Then Slack. Then batching (send all notifications at end of day, not immediately). Then retries (retry failed sends 3 times).

**WHAT HAPPENS WITH INHERITANCE:**

```
EmailNotifier
BatchingEmailNotifier extends EmailNotifier  (add batching)
RetryingEmailNotifier extends EmailNotifier  (add retry)
BatchingRetryingEmailNotifier extends ??? (need both!)
SmsNotifier extends ??? (no shared logic with Email)
BatchingSmsNotifier extends SmsNotifier
RetryingSmsNotifier extends SmsNotifier
BatchingRetryingSmsNotifier extends SmsNotifier
SlackNotifier + 3 more = 12 classes total for 4 features
```

Every new feature doubles the hierarchy. Every new channel adds 4 more classes.

**WHAT HAPPENS WITH COMPOSITION:**

```
Notifier (interface): send(message)

EmailNotifier implements Notifier
SmsNotifier implements Notifier
SlackNotifier implements Notifier

BatchingNotifier implements Notifier {
    BatchingNotifier(Notifier delegate) {...}
    // wraps any notifier, adds batching
}

RetryingNotifier implements Notifier {
    RetryingNotifier(Notifier delegate, int maxRetries) {...}
    // wraps any notifier, adds retry
}

// Combine features freely at runtime:
Notifier n = new RetryingNotifier(
    new BatchingNotifier(
        new EmailNotifier()), 3);
// Email + batching + retry — 3 classes, not 12
// Add Slack + batching + retry: 0 new classes, just compose differently
```

**THE INSIGHT:**
Composition scales as `n + m` (behaviours + channels); inheritance scales as `2^(n+m)`. For 5 channels and 5 cross-cutting behaviours, composition requires 10 classes; inheritance requires 32. Composition wins overwhelmingly at scale.

---

### 🧠 Mental Model / Analogy

> Composition is like a **smartphone app ecosystem**. The phone (base object) has a camera, GPS, microphone — each a separate hardware component. Apps compose these components: the mapping app uses GPS + display; the camera app uses camera + display + GPS; the call app uses microphone + speaker. Each capability is a separate module, composable in any combination. No app "inherits" from another to get GPS — it just accesses the GPS component.

**Mapping:**

- "Phone" → the base object
- "GPS chip, camera, microphone" → composed behaviour components
- "Mapping app" → object that composes GPS + display behaviour
- "Each app uses only the components it needs" → Interface Segregation Principle
- "Swap GPS chip for better model" → replace component implementation at runtime
- "No app inherits from another" → no inheritance for behaviour reuse

**Where this analogy breaks down:** Smartphone apps interact with hardware via OS APIs — there's an abstraction layer. In code, composition can mean direct object references without this layer, making the coupling slightly more direct than a hardware abstraction.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of building a class by saying "this class IS a type of that class" (inheritance), composition says "this class HAS one of these components." A car doesn't inherit from "engine" — it HAS an engine. Swapping the engine is possible; inheriting from a different engine class is not. Composition is about assembling from pieces.

**Level 2 — How to use it (junior developer):**
Define behaviour as an interface. Create classes that implement the interface. Instead of subclassing, hold a reference to the interface in your main class. Delegate the behaviour to that reference. In the constructor or via dependency injection, provide which implementation to use. The result: the main class can be combined with any implementation of the interface without the class changing.

**Level 3 — How it works (mid-level engineer):**
The Decorator pattern and Strategy pattern are the canonical implementations of composition over inheritance. Decorator wraps an object and adds behaviour before/after delegation. Strategy injects the varying algorithm. Both patterns eliminate class hierarchy explosion by moving the variable part (behaviour) into a composed object. The GoF Decorator pattern is exactly `RetryingNotifier(BatchingNotifier(EmailNotifier))` — each layer adds a concern, delegates the core operation.

**Level 4 — Why it was designed this way (senior/staff):**
The GoF explicitly stated "favor object composition over class inheritance" in 1994, after observing that inheritance hierarchies in large codebases became unmaintainable. The Open/Closed Principle (Bertrand Meyer, 1988) is enabled by composition: you extend behaviour by adding new component classes without modifying existing ones. Modern dependency injection frameworks (Spring, Guice) are entirely built around composition — services are assembled from components at startup, not inherited. Kotlin's `by` delegation keyword and Go's embedding make composition syntactically as convenient as inheritance, removing the boilerplate excuse for preferring inheritance.

---

### ⚙️ How It Works (Mechanism)

**Decorator pattern (composition chain):**

```
┌─────────────────────────────────────────────────────┐
│       DECORATOR COMPOSITION CHAIN                   │
│                                                     │
│  Client calls: notifier.send("alert!")              │
│                                                     │
│  RetryingNotifier.send("alert!")                    │
│    └── try up to 3 times                            │
│    └── delegate.send("alert!")                      │
│          ↓                                          │
│        BatchingNotifier.send("alert!")              │
│          └── buffer until batch threshold           │
│          └── delegate.send(batchedMessages)         │
│                ↓                                    │
│              EmailNotifier.send(batchedMessages)    │
│                └── actual SMTP call                 │
│                                                     │
│  Each layer adds one concern; delegates the rest    │
│  All implement Notifier — composable transparently  │
└─────────────────────────────────────────────────────┘
```

**Composition vs inheritance object layout:**

```
INHERITANCE:
  FlyingSwimmingCharacter object:
  [vtable ptr → FSCharacter vtable]
  [Character fields][Flying fields][Swimming fields]
  All behaviour baked into the single class hierarchy

COMPOSITION:
  Character object:
  [vtable ptr → Character vtable]
  [base fields]
  [movementRef → FlyingMovement object]
  [attackRef → ShootingAttack object]

  character.movementRef = new SwimmingMovement();
  // Behaviour changed at runtime — no subclass needed
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
New requirement: add retry behaviour to all notifiers
      ↓
[COMPOSITION OVER INHERITANCE ← YOU ARE HERE]
  Create: RetryingNotifier implements Notifier {
      RetryingNotifier(Notifier delegate, int retries)
  }
      ↓
In DI configuration:
  @Bean Notifier emailNotifier() {
    return new RetryingNotifier(new EmailNotifier(), 3);
  }
      ↓
Zero changes to EmailNotifier, SmsNotifier, SlackNotifier
Zero changes to callers — all see Notifier interface
New behaviour: one new class
```

**FAILURE PATH:**

```
Composition chain too deep → hard to trace execution
  RetryingNotifier → LoggingNotifier → BatchingNotifier
  → ThrottlingNotifier → EmailNotifier
  Stack trace: 5 layers deep for every send call
  Debugging: which layer failed?

Observable: misleading stack traces; unclear failure
            attribution across layers
Fix: limit decorator depth; add clear logging at each layer
     with component identification
```

**WHAT CHANGES AT SCALE:**

At scale (50+ services), composition over inheritance at the architecture level means microservices — each service is a focused component with a clear interface. Cross-cutting concerns (auth, logging, retry, circuit breaking) are added as middleware/decorators, not inherited. This is composition at the deployment topology level: the same principle that prevents class hierarchy explosion prevents service hierarchy explosion.

---

### 💻 Code Example

**Example 1 — Wrong: inheritance for behaviour reuse (anti-pattern):**

```java
// BAD: using inheritance to add logging to UserService
public class LoggingUserService extends UserService {
    @Override
    public User findById(Long id) {
        log.info("Finding user {}", id);
        User result = super.findById(id);  // fragile: depends on parent
        log.info("Found user: {}", result);
        return result;
    }
    // Problem: tightly coupled to UserService
    // Can't add logging to OrderService without another subclass
}
```

**Example 2 — Right: composition for cross-cutting behaviour:**

```java
// GOOD: logging via composition (Decorator pattern)
public interface UserRepository {
    User findById(Long id);
    void save(User user);
}

// Core implementation
public class JpaUserRepository implements UserRepository {
    @Override
    public User findById(Long id) { /* JPA query */ return null; }
    @Override
    public void save(User user) { /* JPA persist */ }
}

// Logging decorator — composes around any UserRepository
public class LoggingUserRepository implements UserRepository {
    private final UserRepository delegate;
    private final Logger log = LoggerFactory.getLogger(getClass());

    public LoggingUserRepository(UserRepository delegate) {
        this.delegate = delegate;  // composed, not inherited
    }

    @Override
    public User findById(Long id) {
        log.info("findById: id={}", id);
        User result = delegate.findById(id);  // delegate
        log.info("findById result: {}", result);
        return result;
    }

    @Override
    public void save(User user) {
        log.info("save: user={}", user.getId());
        delegate.save(user);
    }
}

// Compose at configuration time:
UserRepository repo = new LoggingUserRepository(
    new JpaUserRepository(entityManager)
);
// Same pattern works for ANY repository — zero subclasses per repo type
```

**Example 3 — Strategy pattern: replacing inheritance for algorithm variation:**

```java
// Without composition: one subclass per sort algorithm
// BubbleSortList, MergeSortList, QuickSortList — all extend List

// With composition: inject the algorithm
public interface SortStrategy<T> {
    List<T> sort(List<T> items, Comparator<T> comparator);
}

public class BubbleSortStrategy<T> implements SortStrategy<T> {
    @Override
    public List<T> sort(List<T> items, Comparator<T> cmp) {
        // bubble sort implementation
        return items;
    }
}

public class SortedList<T> {
    private final SortStrategy<T> strategy;  // composed behaviour

    public SortedList(SortStrategy<T> strategy) {
        this.strategy = strategy;
    }

    public List<T> sort(List<T> items, Comparator<T> cmp) {
        return strategy.sort(items, cmp);  // delegate
    }

    // Swap algorithm at runtime:
    public SortedList<T> withStrategy(SortStrategy<T> newStrategy) {
        return new SortedList<>(newStrategy);
    }
}

// Usage:
SortedList<User> sorter = new SortedList<>(new MergeSortStrategy<>());
List<User> sorted = sorter.sort(users, Comparator.by(User::getName));
// Switch to quicksort: new SortedList<>(new QuickSortStrategy<>())
```

**Example 4 — Kotlin `by` delegation (syntax sugar for composition):**

```kotlin
// Kotlin makes composition as concise as inheritance
interface Printer { fun print(doc: String) }
interface Scanner { fun scan(): String }

class LaserPrinter : Printer {
    override fun print(doc: String) { println("Laser: $doc") }
}

class FlatbedScanner : Scanner {
    override fun scan(): String = "scanned document"
}

// Compose without inheritance — 'by' delegates automatically
class AllInOneMachine(
    private val printer: Printer,
    private val scanner: Scanner
) : Printer by printer, Scanner by scanner
// AllInOneMachine gets both capabilities via delegation, not inheritance
// Zero boilerplate forwarding methods
```

---

### ⚖️ Comparison Table

| Approach              | Coupling | Runtime Flexibility    | Code Volume                     | When to Use                                |
| --------------------- | -------- | ---------------------- | ------------------------------- | ------------------------------------------ |
| **Composition**       | Low      | High — swap at runtime | More (delegation boilerplate)   | Behaviour reuse, cross-cutting concerns    |
| Inheritance           | High     | None                   | Less (inherited automatically)  | "is-a" type hierarchy                      |
| Mixin/Trait           | Medium   | Limited                | Medium                          | Language-specific multiple inheritance     |
| Delegation (explicit) | Low      | High                   | High (must forward all methods) | When no interface exists                   |
| Template Method       | Medium   | None                   | Low                             | Algorithm with fixed steps, variable parts |

**How to choose:** Default to composition. Use inheritance only when (a) the relationship is unambiguously "is-a," (b) the subclass honours the full parent contract (LSP), and (c) the hierarchy will be shallow and stable. For behaviour reuse, cross-cutting concerns, or any case where you'd want runtime flexibility, use composition.

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                                    |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Composition always means more code                 | Kotlin's `by` delegation, Java 16 records, and modern DI frameworks reduce composition boilerplate dramatically. The code volume gap has largely closed.                                                                   |
| Composition and inheritance are mutually exclusive | You can (and should) use interfaces for type contracts (inheritance-like) while using composition for behaviour. The two are complementary — the principle says don't use inheritance _for behaviour reuse_.               |
| Composition makes code harder to read              | Flat composition with clear component names is easier to read than deep inheritance. `new RetryingNotifier(new EmailNotifier(), 3)` is self-documenting.                                                                   |
| The principle means never use inheritance          | Inheritance is the right tool when there is a genuine, stable "is-a" relationship. `ArrayList extends AbstractList` is legitimate inheritance. The principle warns against using inheritance as a shortcut for code reuse. |
| Composition can't implement OOP polymorphism       | Composition via interfaces gives you full polymorphism. `List<Notifier>` works with `EmailNotifier`, `SmsNotifier`, and any future notifier regardless of their class hierarchy.                                           |

---

### 🚨 Failure Modes & Diagnosis

**Combinatorial Class Explosion from Inheritance**

**Symptom:**
Codebase has many classes with names like `LoggingRetryingEmailNotifier`, `LoggingBatchingEmailNotifier`, `RetryingSmsNotifier` — systematically combining features across types. Every new feature multiplies the class count.

**Root Cause:**
Inheritance was used for behaviour reuse. Each cross-cutting concern (logging, retry, batching) creates a parallel subclass hierarchy for every base type.

**Diagnostic Command / Tool:**

```bash
# Count classes with multiple feature words in their names:
find src -name "*.java" | xargs grep -l "class.*Logging.*Retry\|class.*Retry.*Email\|class.*Batching.*Sms"
# More than 3 hits: combinatorial explosion in progress

# Better: count class files per package vs exported interfaces
find src/notifications -name "*.java" | wc -l
# If much larger than the number of notifier types + concerns: explosion
```

**Fix:**
Refactor using Decorator pattern. Create one class per concern (LoggingDecorator, RetryDecorator). Compose them at configuration time.

**Prevention:**
When adding a new cross-cutting concern: ask "does this need to be added to N other classes?" If yes, it's a candidate for a decorator/composition approach.

---

**Deep Hierarchy Behaviour Tracing**

**Symptom:**
Debugger shows 8-level call stack when a simple method is called. Behaviour changes happen at multiple levels in the hierarchy. Bug is traced to an ancestor class 5 levels up.

**Root Cause:**
Deep inheritance hierarchy (5+ levels). Method behaviour is assembled across multiple overrides in multiple classes. No single place to see the full behaviour.

**Diagnostic Command / Tool:**

```bash
# Visualise the class hierarchy depth:
# Java: use javap or IDE class hierarchy view
javap -verbose FullClassName | grep "Superclass"
# Also: IDE → Show Type Hierarchy for any class

# In code review: count the 'extends' chain
grep -rn "extends" src/ --include="*.java" | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -10
```

**Fix:**
Flatten the hierarchy by extracting shared behaviour into composed objects. Replace abstract methods with strategy injection. Aim for maximum 2 levels of inheritance depth for domain classes.

**Prevention:**
Code review standard: no class hierarchy deeper than 2 levels (class → abstract base → concrete) without explicit justification. Prefer flat hierarchies.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Inheritance` — you must understand what inheritance is and why it fails before understanding why composition is preferred
- `Polymorphism` — composition achieves the same polymorphism as inheritance, but through interfaces rather than class hierarchy
- `Encapsulation` — composition naturally encapsulates each behaviour component — understanding encapsulation clarifies why this matters

**Builds On This (learn these next):**

- `Design Patterns` — Strategy, Decorator, and Composite patterns are composition in action — systematic solutions to common hierarchy problems
- `SOLID Principles` — Open/Closed Principle is enabled by composition; Dependency Inversion Principle requires it
- `Dependency Injection` — the runtime mechanism for assembling composed objects — DI makes composition practical at application scale

**Alternatives / Comparisons:**

- `Inheritance` — the alternative this principle argues against for behaviour reuse; valid for "is-a" type relationships
- `Strategy Pattern` — the specific pattern that replaces inheritance for algorithm variation — inject the strategy object
- `Decorator Pattern` — the specific pattern for additive behaviour — wrap objects to add cross-cutting concerns
- `Mixins / Traits` — language features that provide behaviour composition without full class inheritance (Scala traits, Kotlin extension functions, Ruby modules)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Assemble behaviour from small, composed   │
│              │ components rather than inheriting it      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Inheritance causes 2^n class explosion    │
│ SOLVES       │ for n orthogonal behaviours               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Inheritance is static (compile-time);     │
│              │ composition is dynamic (runtime swappable)│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Code reuse across multiple types;         │
│              │ cross-cutting concerns; runtime variation │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ True "is-a" relationship: use             │
│              │ inheritance for type hierarchy            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Runtime flexibility and loose coupling vs │
│              │ delegation boilerplate                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "LEGO, not stone carving. Assemble;       │
│              │  don't carve away from a monolith."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strategy Pattern → Decorator → DI         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot's `RestTemplate` and `WebClient` both support interceptors and filters that can be added as composition layers (authentication headers, retry logic, logging, timeout enforcement). These interceptors are exactly Decorators in the composition sense. When you add 5 interceptors to a `WebClient`, they form a chain where each calls the next. If interceptor 3 needs to know that interceptor 1 has already run (e.g., needs to read a header interceptor 1 set), how does this requirement break the clean composition model — and what pattern or design mechanism addresses it without coupling the interceptors to each other?

**Q2.** Go uses embedding for composition: `type LoggingDB struct { *sql.DB; logger *log.Logger }`. This automatically promotes all `*sql.DB` methods onto `LoggingDB` — you can call `logDB.QueryContext()` without forwarding it. But if `*sql.DB` adds a new method in a library update, `LoggingDB` automatically inherits it — without any chance to intercept or log it. This is the same fragile base class problem that OOP inheritance has. What does this reveal about the fundamental difference between "embedding" (auto-promotion) and "true composition" (explicit delegation), and under what conditions is each appropriate?
