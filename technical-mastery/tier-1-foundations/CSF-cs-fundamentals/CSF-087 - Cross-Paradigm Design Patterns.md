---
id: CSF-087
title: Cross-Paradigm Design Patterns
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-086, CSF-001, CSF-002
used_by:
related: CSF-086, CSF-001, CSF-002, CSF-084, CSF-088
tags: [design-patterns, gof-patterns, functional-patterns, cross-paradigm, oop-patterns]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 87
permalink: /technical-mastery/csf/cross-paradigm-design-patterns/
---

⚡ TL;DR - Cross-paradigm design patterns: understanding that the 23 GoF (Gang of Four)
patterns solve PROBLEMS, not implement OOP. Each pattern has a functional equivalent that
solves the SAME problem with fewer lines. Strategy pattern -> first-class function (pass the
function, not an interface). Command pattern -> lambda/closure. Observer -> Reactive streams.
Template Method -> higher-order function. Iterator -> Stream/Sequence. The key insight: knowing
the PROBLEM each pattern solves (not just the OOP implementation) enables cross-paradigm
translation and choosing the simplest implementation.

| #087 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-086 (Paradigm-Agnostic Thinking), CSF-001 (OOP), CSF-002 (FP) | |
| **Used by:** | (code review, refactoring, architecture, technical interviews) | |
| **Related:** | CSF-086 (Paradigm-Agnostic), CSF-001 (OOP), CSF-002 (FP), CSF-084 (Migration), CSF-088 (Trade-off Framing) | |

---

### 🔥 The Problem This Solves

**THE "PATTERN DOGMATIST" FAILURE:**

Engineer reviews a PR. The PR contains:
```java
interface SortStrategy { void sort(List<Integer> list); }
class QuickSortStrategy implements SortStrategy { ... }
class MergeSortStrategy implements SortStrategy { ... }
class SortingService {
    private final SortStrategy strategy;
    SortingService(SortStrategy s) { this.strategy = s; }
    void execute(List<Integer> list) { strategy.sort(list); }
}
```

Four classes/interfaces for `list.sort(comparator)`.

The engineer says: "Great use of the Strategy pattern!" The PR is approved.
The ACTUAL cost: 4 types instead of 1 function call. Future engineers must understand
and maintain a class hierarchy for a problem solved by a lambda.

**THE PATTERN WITHOUT THE PROBLEM:**

GoF Design Patterns (1994, Gamma/Helm/Johnson/Vlissides): documented solutions to recurring
DESIGN PROBLEMS. The book was written in the context of C++ and Smalltalk (1994). At that time:
languages DID NOT have first-class functions, lambdas, or higher-order functions built in.
The patterns: provided WORKAROUNDS for language limitations. In a language without first-class
functions: the Strategy pattern IS the correct solution for "parameterizing behavior."

In 2024, with Java 8+ lambdas, Kotlin, Scala, Swift, Python, and JavaScript:
most behavioral patterns have functional equivalents that are SIMPLER.

The **cross-paradigm awareness** principle: know WHICH PROBLEM each pattern solves.
Then: choose the simplest implementation (OOP pattern, FP equivalent, or hybrid).

---

### 📘 Textbook Definition

**Design Patterns (GoF):** Twenty-three recurring solutions to common object-oriented design
problems, documented by Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides in "Design
Patterns: Elements of Reusable Object-Oriented Software" (1994). Organized into: Creational
(object creation), Structural (object composition), Behavioral (object interaction and
responsibility).

**Functional Patterns:** Recurring solutions to common functional programming design problems.
Examples: Maybe/Option (null-safe computation), Either (two-path computation), Reader monad
(dependency injection via function composition), Free monad (pure description of effects).
These are NOT in the GoF book (written before FP was mainstream in industry).

**Cross-Paradigm Pattern Translation:** The mapping from an OOP design pattern to its functional
equivalent. Not all OOP patterns have functional equivalents (structural patterns like Decorator
are useful in both OOP and FP contexts). Behavioral patterns: most have functional equivalents.
Creational patterns: partially have functional equivalents (factory function).

**First-Class Function:** A function that can be stored in a variable, passed as an argument,
and returned from another function - just like any other value. Languages with first-class
functions: Java (lambda/Function<T,R>), Kotlin (function types), Scala, JavaScript, Python,
Go, Rust, Swift, C# (delegates/Func<T,R>). Languages WITHOUT first-class functions: early
Java (pre-8), C (function pointers via #include, not truly first-class), older languages.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GoF patterns solve problems. Problems exist in any paradigm. FP often solves the same
problem with less ceremony. Strategy pattern = "parameterize behavior" = pass a function.
Know the problem; choose the simplest solution.

**One analogy:**

> The GoF patterns: recipes for cooking without a blender (1994).
> "To puree: mash by hand with a fork and sieve" (Strategy pattern: create a Masher class).
> "To mix: fold repeatedly with a spatula" (Command pattern: create a FoldCommand).
> In 1994: there was no blender (no first-class functions in Java).
>
> In 2024: most kitchens have a blender (Java 8+, Kotlin, Python, JavaScript).
> The PROBLEM (puree, mix, blend) is the same.
> The SOLUTION is simpler: use the blender.
> "list.stream().map(fn).collect()" = blender for data transformation.
>
> The chef who still uses a fork when a blender is available: loyal to the tool, not the result.
> The chef who uses the blender when it fits, and the spatula when it fits:
> paradigm-agnostic.

**One insight:**

Peter Norvig (Director of Research, Google) studied all 23 GoF patterns and found that
17 of them are "invisible" or "simpler" in languages with first-class functions (Lisp, then
Python, then all modern languages). His conclusion: patterns are evidence of MISSING LANGUAGE
FEATURES. Once the language adds the feature (first-class functions), the pattern becomes
unnecessary.

Example: Strategy pattern in 2024 Java:
```java
// GoF Strategy pattern (Java pre-8): needed because no first-class functions
interface Sorter { void sort(List<Integer> list); }
class QuickSorter implements Sorter { void sort(List<Integer> l) { /* quicksort */ } }

// Java 8+: first-class functions make Strategy pattern unnecessary (for simple cases)
Comparator<Integer> naturalOrder = Integer::compareTo;
list.sort(naturalOrder); // The strategy IS the function. No interface. No class.
```

The pattern still exists in education and code reviews because:
(1) the GoF book is still the primary reference for "design patterns",
(2) many Java engineers learned patterns before Java 8 and still default to them,
(3) for COMPLEX strategies (with multiple methods, configuration, dependencies),
the OOP Strategy pattern IS still appropriate.

---

### 🔩 First Principles Explanation

**THE PROBLEM-PATTERN-FP TRANSLATION TABLE:**

```
┌──────────────────────────────────────────────────────┐
│ BEHAVIORAL PATTERNS: OOP vs FP                       │
│                                                      │
│ STRATEGY:                                           │
│   PROBLEM: "Parameterize an algorithm/behavior"     │
│   OOP: Strategy interface + concrete implementations│
│   FP: Pass a function (lambda / Comparator / BiFunction)│
│   FP WHEN: strategy is one method, no configuration │
│   OOP WHEN: strategy is complex, multiple methods   │
│                                                      │
│ COMMAND:                                            │
│   PROBLEM: "Encapsulate an action for deferred      │
│     execution, undo, or queuing"                    │
│   OOP: Command interface with execute() + receiver  │
│   FP: Runnable / Supplier / Consumer + closure      │
│   FP WHEN: single action, state captured by closure │
│   OOP WHEN: complex commands with undo + redo       │
│                                                      │
│ OBSERVER:                                           │
│   PROBLEM: "Notify dependent objects on state change│
│     without tight coupling"                         │
│   OOP: Observer interface + Subject/EventSource     │
│   FP: Reactive Streams (Rx, Reactor, Kotlin Flow)  │
│   FP WHEN: async event streams with backpressure    │
│   OOP WHEN: simple synchronous listener list       │
│                                                      │
│ TEMPLATE METHOD:                                    │
│   PROBLEM: "Define algorithm skeleton; let subclass │
│     fill in specific steps"                         │
│   OOP: Abstract class with hooks                    │
│   FP: Higher-order function (pass the "hook" fn)   │
│   FP WHEN: the "hook" is one function              │
│   OOP WHEN: multiple hooks with shared state       │
│                                                      │
│ ITERATOR:                                           │
│   PROBLEM: "Traverse a collection without exposing  │
│     its internal representation"                    │
│   OOP: Iterator interface with hasNext()/next()    │
│   FP: Stream / Sequence / Iterable.forEach         │
│   FP WHEN: collection traversal with transformations│
│   OOP WHEN: stateful iteration requiring manual ctrl│
│                                                      │
│ CHAIN OF RESPONSIBILITY:                            │
│   PROBLEM: "Pass request through a chain of handlers│
│     until one handles it"                           │
│   OOP: Handler abstract class with next handler ref │
│   FP: Compose predicates/functions: list of handlers│
│     processed via stream.filter().findFirst()      │
│   FP WHEN: handlers are pure functions/predicates  │
│   OOP WHEN: handlers have complex state/dependencies│
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE SAME PROBLEM: DECORATOR PATTERN**

```java
// PROBLEM: "Add behavior to an object without modifying its class"
// (e.g., add logging, caching, validation to a service)

// OOP: Decorator pattern (always appropriate for wrapping behavior)
interface OrderService { Order findById(OrderId id); }
class OrderServiceImpl implements OrderService { ... }

class CachingOrderService implements OrderService {
    private final OrderService delegate;
    private final Cache<OrderId, Order> cache;
    CachingOrderService(OrderService d, Cache<OrderId, Order> c) {
        this.delegate = d; this.cache = c;
    }
    @Override
    public Order findById(OrderId id) {
        return cache.computeIfAbsent(id, delegate::findById);
    }
}

class LoggingOrderService implements OrderService {
    private final OrderService delegate;
    LoggingOrderService(OrderService d) { this.delegate = d; }
    @Override
    public Order findById(OrderId id) {
        log.info("Finding order {}", id);
        Order result = delegate.findById(id);
        log.info("Found order {}: {}", id, result.getStatus());
        return result;
    }
}

// Usage: compose decorators
OrderService service = new LoggingOrderService(
    new CachingOrderService(
        new OrderServiceImpl(repository), cache));

// FP approach: Function composition (for simple cases)
Function<OrderId, Order> findById = repository::findById;

// Compose: logging + caching decorators as function transformations
Function<OrderId, Order> withLogging = id -> {
    log.info("Finding order {}", id);
    Order result = findById.apply(id);
    log.info("Found: {}", result.getStatus());
    return result;
};
Function<OrderId, Order> withCache = id ->
    cache.computeIfAbsent(id, findById::apply);

// VERDICT: For simple single-method decoration: FP function composition cleaner.
// For multi-method interfaces with stateful decorators: OOP Decorator more readable.
// Decorator: rare case where OOP and FP are both common. Context determines choice.
```

---

### 🎯 Mental Model / Analogy

**PATTERN TRANSLATION VISUAL**

```
┌──────────────────────────────────────────────────────┐
│ CROSS-PARADIGM PATTERN TRANSLATIONS:                 │
│                                                      │
│ OOP STRATEGY:     FP EQUIVALENT:                    │
│ ─────────────     ──────────────                    │
│ interface         Function<Order, BigDecimal>        │
│ SortStrategy      = order -> order.total() * 0.15   │
│   .sort(list)     sort.apply(list) // simpler        │
│                                                      │
│ OOP COMMAND:      FP EQUIVALENT:                    │
│ ─────────────     ──────────────                    │
│ interface         Runnable = () -> queue.add(order)  │
│ Command           scheduler.schedule(command)        │
│   .execute()      command.run() // simpler           │
│                                                      │
│ OOP TEMPLATE:     FP EQUIVALENT:                    │
│ ─────────────     ──────────────                    │
│ abstract class    process(validate, transform, save) │
│   processOrder()  where validate/transform/save are  │
│   validateHook()  passed as Function parameters.    │
│   saveHook()      // template = HOF call             │
│                                                      │
│ OOP OBSERVER:     FP EQUIVALENT:                    │
│ ─────────────     ──────────────                    │
│ EventSource       Flux<Event>.subscribe(handler)     │
│   .subscribe()    // reactive stream handles         │
│   .notify()       backpressure, error, completion   │
│                   automatically                     │
│                                                      │
│ BOTH PARADIGMS:   (Structural patterns often better │
│ ─────────────     as OOP)                           │
│ Decorator: both OOP (multi-method) or FP (single fn)│
│ Proxy: usually OOP (interface implementation)       │
│ Facade: either (depends on complexity)             │
└──────────────────────────────────────────────────────┘
```

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
A design pattern is a named solution to a common problem. Like a recipe named "chocolate cake"
- it tells you the STEPS to make something. But if you have a cake machine (a better tool):
you can make the same cake more easily. OOP design patterns are recipes for making code when
the programming language didn't have special tools. Modern programming languages have better
tools (lambdas, streams). Same cake, fewer steps, same result.

**Level 2 - Student:**
Strategy pattern: OOP vs FP
```java
// OOP: Strategy pattern for sorting (Java pre-8)
interface SortStrategy {
    int[] sort(int[] arr);
}
class BubbleSortStrategy implements SortStrategy {
    @Override public int[] sort(int[] arr) {
        /* bubble sort implementation */ return arr;
    }
}
class QuickSortStrategy implements SortStrategy {
    @Override public int[] sort(int[] arr) {
        /* quicksort implementation */ return arr;
    }
}
SortStrategy strategy = ascending ? new QuickSortStrategy() : new BubbleSortStrategy();
int[] sorted = strategy.sort(arr);

// FP: first-class function (Java 8+)
// The "strategy" IS the function. No interface. No class.
IntUnaryOperator[] sorters = {arr2 -> quickSort(arr2), arr2 -> bubbleSort(arr2)};
IntUnaryOperator sorter = ascending ? sorters[0] : sorters[1];
int[] sorted = sorter.applyAsInt(arr);
// Even simpler for List:
Comparator<Integer> naturalOrder = Comparator.naturalOrder();
Comparator<Integer> reverseOrder = Comparator.reverseOrder();
list.sort(ascending ? naturalOrder : reverseOrder);
// Comparator IS the Strategy: a function passed to sort().
// The "Strategy pattern" here is invisible because List.sort() accepts it directly.
```

**Level 3 - Professional:**
Observer vs Reactive Streams:
```java
// OOP: Observer pattern (Java pre-8 EventListener style)
interface OrderEventListener {
    void onOrderCreated(Order order);
    void onOrderShipped(Order order);
    void onOrderCancelled(Order order);
}
class EmailNotificationListener implements OrderEventListener {
    @Override public void onOrderCreated(Order o) { sendEmail(o.getCustomer(), "Created"); }
    @Override public void onOrderShipped(Order o) { sendEmail(o.getCustomer(), "Shipped"); }
    @Override public void onOrderCancelled(Order o) { sendEmail(o.getCustomer(), "Cancelled");}
}
class OrderService {
    private final List<OrderEventListener> listeners = new ArrayList<>();
    void addListener(OrderEventListener l) { listeners.add(l); }
    void createOrder(OrderRequest req) {
        Order order = buildOrder(req);
        save(order);
        listeners.forEach(l -> l.onOrderCreated(order)); // notify all
    }
}
// Problem: synchronous. If listener throws: blocks order creation.
// Problem: no backpressure (listener overwhelmed by events: no mechanism to slow down).

// FP/Reactive: Spring Application Events (sync) or Reactor (async with backpressure)
// Using Reactor for async event stream:
class OrderService {
    private final Sinks.Many<OrderEvent> eventSink =
        Sinks.many().multicast().onBackpressureBuffer();

    Flux<OrderEvent> orderEvents() { return eventSink.asFlux(); }

    void createOrder(OrderRequest req) {
        Order order = buildOrder(req);
        save(order);
        eventSink.tryEmitNext(new OrderCreatedEvent(order)); // async, non-blocking
    }
}

// Subscriber: non-blocking, backpressure-aware
orderService.orderEvents()
    .filter(event -> event instanceof OrderCreatedEvent)
    .map(event -> ((OrderCreatedEvent) event).getOrder())
    .flatMap(order -> sendEmailAsync(order.getCustomer(), "Created")) // async email
    .subscribe(); // non-blocking

// FP ADVANTAGE: backpressure built-in. Async by default. Error handling: onErrorResume().
// OOP ADVANTAGE: simpler for synchronous listener scenarios where backpressure not needed.
```

**Level 4 - Senior Engineer:**
Factory Method vs factory function vs DI:
```java
// OOP: Factory Method (GoF Creational)
// PROBLEM: "Defer object creation to subclasses"
abstract class MessageSenderFactory {
    abstract MessageSender createSender(); // factory method
    void sendMessage(String message) {
        MessageSender sender = createSender(); // deferred to subclass
        sender.send(message);
    }
}
class EmailSenderFactory extends MessageSenderFactory {
    @Override MessageSender createSender() { return new EmailSender(smtpConfig); }
}
class SmsSenderFactory extends MessageSenderFactory {
    @Override MessageSender createSender() { return new SmsSender(twilioConfig); }
}
// Usage: EmailSenderFactory.sendMessage("Hello")

// FP: factory function (simpler when creation logic is simple)
Supplier<MessageSender> emailSenderFactory = () -> new EmailSender(smtpConfig);
Supplier<MessageSender> smsSenderFactory = () -> new SmsSender(twilioConfig);

void sendMessage(String msg, Supplier<MessageSender> factory) {
    factory.get().send(msg);
}
// Usage: sendMessage("Hello", emailSenderFactory)
// No abstract class. No subclass hierarchy. Just a Supplier<T>.

// BEST PRACTICE (2024): Dependency Injection frameworks
// Factory Method: largely replaced by DI (Spring, Guice, CDI)
// DI: the "factory" is the DI container. @Bean creates the instance.
// No Factory class, no factory method, no abstract class needed.
@Configuration
class MessagingConfig {
    @Bean
    @ConditionalOnProperty(name = "sender.type", havingValue = "email")
    MessageSender emailSender(SmtpConfig config) { return new EmailSender(config); }
    @Bean
    @ConditionalOnProperty(name = "sender.type", havingValue = "sms")
    MessageSender smsSender(TwilioConfig config) { return new SmsSender(config); }
}
// @Autowired MessageSender sender -> DI injects the correct implementation.
// DI: replaced most Factory patterns in Spring applications.
// The PROBLEM (deferred/conditional creation) is the same.
// The SOLUTION: simpler with modern DI frameworks.
```

**Level 5 - Expert:**
Monad as a cross-paradigm pattern:
```java
// Expert: the Monad - an FP "pattern" that is emerging in OOP languages
// (Optional, CompletableFuture, Stream are all Monads in Java, even if unnamed)

// A Monad is a DESIGN PATTERN for CHAINING COMPUTATIONS in a context:
// 1. "Wrap" a value in a context: Optional.of(value)
// 2. "Transform" the value in the context: .map(fn)  [same context out]
// 3. "Chain" to another context-producing computation: .flatMap(fn) [flatten]

// Optional as Maybe monad (null-safe computation):
Optional<String> email = userRepository.findById("user-123")
    .map(User::getProfile)          // map: User -> Profile (or empty if absent)
    .map(Profile::getEmail)         // map: Profile -> String
    .filter(e -> e.contains("@")); // filter: keeps value or empties

// CompletableFuture as Promise monad (async computation):
CompletableFuture<Order> order = userRepository.findByIdAsync("user-123")
    .thenApply(User::getPrimaryAddress)       // map: async step
    .thenCompose(addr -> orderRepo.findLatestAsync(addr)); // flatMap: async chain

// Stream as List monad (collection computation):
List<String> activeEmails = users.stream()
    .filter(User::isActive)     // filter in context
    .map(User::getEmail)        // map in context
    .collect(Collectors.toList()); // exit context

// THE PATTERN: all three (Optional, CompletableFuture, Stream) are monads.
// The Java language: did not name them as such. But the API (map, flatMap): is the monad API.
// Recognizing this: the engineer sees that Optional<User>.flatMap(u -> Optional.ofNullable(u.getProfile()))
// is the same STRUCTURAL pattern as CompletableFuture.thenCompose() and Stream.flatMap().
// All three: "flatten a nested context into a single-level context."
// Same problem: different types. Same solution: flatMap. Cross-paradigm pattern recognition.

// GoF equivalent: Decorator pattern (wrapping a value in a context and adding behavior)
// But Decorator in OOP: structural. Monad in FP: behavioral (chain computation).
// Same "wrapping" concept: different abstraction level.
```

---

### ⚙️ How It Works

**THE PATTERN SELECTION DECISION:**

```
┌──────────────────────────────────────────────────────┐
│ WHEN TO USE OOP PATTERN vs FP EQUIVALENT:            │
│                                                      │
│ USE OOP PATTERN when:                               │
│   - The "strategy/handler" has MULTIPLE METHODS.    │
│     (A Comparator is one method: FP wins.)          │
│     (A "Sorter" with sort(), compare(), validate(): │
│     multiple methods -> OOP interface wins.)        │
│   - The pattern implementation has INTERNAL STATE   │
│     that requires encapsulation.                    │
│     (A cached strategy with its own cache field:    │
│     OOP class is cleaner.)                          │
│   - The pattern participates in a HIERARCHY where   │
│     polymorphism is the design driver.              │
│     (Abstract base class with shared behavior:      │
│     OOP inheritance is appropriate.)               │
│   - The TEAM is more familiar with OOP patterns     │
│     and the FP equivalent offers no clarity benefit.│
│                                                      │
│ USE FP EQUIVALENT when:                             │
│   - The strategy is ONE function (one method).      │
│     Replace interface + class with a lambda.        │
│   - The command has no undo requirement.            │
│     Replace Command class with Runnable/Supplier.  │
│   - The template method has ONE variable step.      │
│     Replace abstract class with HOF parameter.     │
│   - The observer needs backpressure/async behavior. │
│     Replace Observer with Reactive Stream (Reactor).│
│   - The factory creates objects with NO dependencies│
│     or SIMPLE dependencies.                         │
│     Replace Factory with DI + factory function.    │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Template Method Pattern**

```java
// BAD: OOP Template Method for a single-step algorithm
// Abstract class overhead for a pattern that can be one function parameter.
abstract class DataProcessor {
    // Template method: defines the algorithm skeleton
    final void process(List<String> data) {
        List<String> validated = validate(data);     // step 1
        List<String> transformed = transform(validated); // step 2 (variable)
        save(transformed);                           // step 3
    }
    List<String> validate(List<String> data) { /* default validation */ return data; }
    abstract List<String> transform(List<String> data); // THE ONLY VARIABLE STEP
    void save(List<String> data) { /* save to DB */ }
}

class UpperCaseProcessor extends DataProcessor {
    @Override List<String> transform(List<String> d) {
        return d.stream().map(String::toUpperCase).collect(Collectors.toList());
    }
}
class TrimProcessor extends DataProcessor {
    @Override List<String> transform(List<String> d) {
        return d.stream().map(String::trim).collect(Collectors.toList());
    }
}
// One abstract class + 2 concrete classes for one variable step.

// GOOD: Higher-order function replaces Template Method when one step is variable.
class DataProcessor {
    void process(
            List<String> data,
            UnaryOperator<List<String>> transform) { // parameter = the "hook"
        List<String> validated = validate(data);
        List<String> transformed = transform.apply(validated); // call the hook
        save(transformed);
    }
    private List<String> validate(List<String> d) { return d; }
    private void save(List<String> d) { /* save */ }
}

// Usage: pass the transform as a lambda. No subclass needed.
DataProcessor processor = new DataProcessor();
processor.process(data, d -> d.stream().map(String::toUpperCase).collect(...)); // uppercase
processor.process(data, d -> d.stream().map(String::trim).collect(...));        // trim
processor.process(data, UnaryOperator.identity()); // no-op transform: also easy
// When to keep Template Method: when there are MULTIPLE variable steps, or when
// subclasses share complex state that makes inheritance natural.
```

**Example 2 - Production: Chain of Responsibility as Function Composition**

```java
// PROBLEM: HTTP request handling chain (validation -> authentication -> authorization -> handler)
// Classic Chain of Responsibility (OOP):
abstract class RequestHandler {
    private RequestHandler next;
    void setNext(RequestHandler n) { this.next = n; }
    abstract boolean handle(HttpRequest req);
    boolean passToNext(HttpRequest req) { return next != null && next.handle(req); }
}
class AuthenticationHandler extends RequestHandler {
    @Override boolean handle(HttpRequest req) {
        if (!authenticate(req)) return false; // short-circuit
        return passToNext(req);
    }
}
// 3+ classes for a chain of predicates.

// FP: Composed predicates + Optional short-circuit
// Each handler: Predicate<HttpRequest> (true = pass, false = reject)
Predicate<HttpRequest> authCheck = req -> authenticate(req.getAuthHeader());
Predicate<HttpRequest> authzCheck = req -> authorize(req.getPath(), req.getUserRole());
Predicate<HttpRequest> rateLimitCheck = req -> !rateLimiter.isThrottled(req.getClientId());

// Compose: all must pass. Short-circuit on first failure.
Predicate<HttpRequest> pipeline = authCheck
    .and(authzCheck)        // Predicate.and() = short-circuit &&
    .and(rateLimitCheck);

// Usage:
if (pipeline.test(request)) {
    handler.handle(request);
} else {
    response.sendError(403, "Forbidden");
}
// 0 abstract classes. 3 lambdas. Same chain behavior with short-circuit.
// WHEN to use OOP Chain of Responsibility:
// When handlers have complex state, multiple methods, or async behavior.
// For pure predicate chains: function composition is cleaner.
```

---

### ⚖️ Comparison Table

| OOP Pattern | Problem It Solves | FP Equivalent | When OOP is Better |
|---|---|---|---|
| Strategy | Parameterize behavior | First-class function (lambda) | Strategy has multiple methods or complex state |
| Command | Encapsulate action for deferred execution | Runnable / Supplier / closure | Complex undo/redo with command history |
| Observer | Notify dependents on state change | Reactive Stream (Flux, Flow) | Simple synchronous listeners (EventListener) |
| Template Method | Algorithm skeleton with variable steps | Higher-order function (pass hook as param) | Multiple variable steps with shared state |
| Iterator | Traverse collection without exposing internals | Stream / Iterable.forEach | Stateful iteration needing manual control |
| Chain of Responsibility | Pass request through handler chain | Predicate.and() / function composition | Async handlers, complex state per handler |
| Factory Method | Defer creation to subclasses | Supplier<T> / factory function / DI | Multiple factory methods with shared logic |
| Decorator | Add behavior without subclassing | Function composition (wrap the function) | Multi-method interface decoration |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "FP equivalents always replace OOP patterns" | FP equivalents are SIMPLER for patterns that solve "parameterize a single behavior." But OOP patterns remain appropriate when: the pattern implementation is complex (multiple methods, stateful, dependencies), when the design requires runtime polymorphism across multiple implementations (Strategy with 10+ complex strategies: OOP interface is better than 10 lambdas), or when the team is more familiar with OOP patterns and the clarity benefit of FP equivalents is marginal. Peter Norvig's finding: 17 of 23 GoF patterns are simpler in functional languages. That means 6 patterns: still benefit from OOP implementation even in functional languages. Judgment required for each case. |
| "Design patterns are OOP-specific" | The 23 GoF patterns are documented in an OOP context. But "design pattern" means "a recurring solution to a recurring problem." FP has its own set of patterns: Functor (mappable container), Monad (chainable computation in a context), Applicative (parallel application of functions to values), Lens (composable getter/setter for nested data), Railway-Oriented Programming (two-path error handling). These are not in the GoF book but are widely used in Haskell, Scala, and increasingly in Kotlin, TypeScript (fp-ts), and Rust. A complete understanding of design patterns requires both GoF (OOP) and functional patterns. |
| "Knowing 23 patterns makes you a good designer" | Knowing the 23 patterns by name and structure is table stakes. What makes a good designer: knowing WHICH PROBLEM each pattern solves, recognizing when the problem recurs in a new codebase, choosing the SIMPLEST implementation (OOP pattern, FP equivalent, or a combination), and knowing when to NOT apply a pattern (when the problem is simple enough that no pattern is needed). Over-use of patterns: a common failure mode for engineers who have just learned them ("AbstractFactory for everything"). The pattern is a MEANS to solving a design problem. The design problem: is the goal. Patterns that exist in the code without a clear problem they are solving: are design smell, not design quality. |
| "Reactive streams (Rx) replaced the Observer pattern" | Reactive streams (RxJava, Reactor, Kotlin Flow, RxJS) are more POWERFUL than the classical Observer pattern: they add backpressure (consumer can slow down producer), operators (map, filter, flatMap applied to event streams), composition (combine multiple streams), and async error handling. But this power comes with complexity. For simple synchronous listener patterns (button click listener in Swing, Spring ApplicationEvent listener): the classical Observer (EventListener, @EventListener) is simpler and more readable. Reactive streams: appropriate when async, backpressure, or stream composition is needed. Classical Observer: appropriate for simple synchronous notification. The move is not "Rx replaced Observer everywhere" - it is "Rx extends Observer for async streaming contexts." |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Pattern Explosion (Over-Engineering via Patterns)**

**Symptom:** A simple service has 15+ classes for 3 operations. Every operation has an interface,
an implementation, a factory, and a strategy. Adding a new field requires touching 8 files.
Code review: "follows all design patterns." In practice: impossible to understand or change.

**Diagnosis:**
```java
// SMELL DETECTOR: count the ratio of interfaces/abstractions to implementations
// If ratio > 2:1 (more interfaces than implementations): likely over-engineered.
// "For every class that does something: there are 2 that describe what it could do."

// QUESTION: "Who are the multiple implementations of this interface?"
interface OrderValidator { boolean validate(Order o); }
// Answer: there is ONE implementation: OrderValidatorImpl.
// ONE implementation -> the interface adds NO value. Remove it.
// (Exception: Spring @Autowired where the interface enables mocking in tests:
// this is valid use of interface even with one implementation.)

// QUESTION: "Can this class be replaced with a lambda?"
class IsActiveUserPredicate implements Predicate<User> {
    @Override public boolean test(User u) { return u.isActive(); }
}
// ONE method. NO state. -> Replace with: Predicate<User> isActive = User::isActive;
// The class IS the lambda. Remove it.

// QUESTION: "Is this pattern solving a real problem or adding ceremony?"
class OrderBuilderFactory {
    OrderBuilder createBuilder() { return new OrderBuilder(); }
}
// OrderBuilder has no dependencies. createBuilder() is: return new OrderBuilder().
// Replace: just use `new OrderBuilder()` directly. Factory adds no value here.
```

---

**Security Note:**

Cross-paradigm patterns have security implications in how they handle sensitive data:

1. **Command pattern with sensitive state in closure:**
   ```java
   // RISK: Lambda (Command FP equivalent) captures sensitive state in closure
   String password = getPasswordFromUser(); // sensitive
   Runnable loginCommand = () -> authService.login(username, password);
   // password is now captured in the lambda's closure.
   // If the lambda is: stored in a queue, serialized, or passed to another thread:
   // the password may be accessible in memory longer than intended.
   // FIX: use char[] for passwords (clearable after use).
   // FIX: limit lambda lifetime. Do not store security-sensitive lambdas long-term.
   // FIX: use Spring Security's authentication infrastructure (clears credentials after auth).
   ```

2. **Observer pattern: event data validation:**
   ```java
   // OOP Observer: if event data is not validated before dispatching:
   eventSource.notifyObservers(untrustedData); // passing untrusted data to all observers
   // FP Reactive: same risk. Unvalidated events flowing through stream: each operator
   // receives untrusted data.
   // FIX: validate and sanitize event data BEFORE publishing to the event stream.
   orderEventSink.tryEmitNext(validate(event)); // validate before emitting
   ```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Paradigm-Agnostic Thinking` (CSF-086) - the foundation for cross-paradigm pattern recognition
- `Object-Oriented Programming` (CSF-001) - OOP patterns context
- `Functional Programming` (CSF-002) - FP equivalents context

**Builds On This (learn these next):**
- `Trade-off Framing` (CSF-088) - applying trade-off thinking to pattern selection
- `First-Principles Language Selection` (CSF-089) - first-principles approach

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ STRATEGY  │ Parameterize behavior.                     │
│           │ FP: lambda/Function. OOP: interface+class │
├───────────┼─────────────────────────────────────────┤
│ COMMAND   │ Encapsulate deferred action.              │
│           │ FP: Runnable/closure. OOP: Command class │
├───────────┼─────────────────────────────────────────┤
│ OBSERVER  │ Notify dependents.                        │
│           │ FP: Rx/Reactor. OOP: EventListener list  │
├───────────┼─────────────────────────────────────────┤
│ TEMPLATE  │ Algorithm skeleton, variable steps.      │
│           │ FP: HOF param. OOP: abstract class+hooks │
├───────────┼─────────────────────────────────────────┤
│ ITERATOR  │ Traverse without exposing internals.     │
│           │ FP: Stream. OOP: Iterator interface      │
├───────────┼─────────────────────────────────────────┤
│ USE OOP   │ Multiple methods in pattern.             │
│ PATTERN   │ Complex state. Runtime polymorphism.     │
├───────────┼─────────────────────────────────────────┤
│ USE FP    │ One method. Simple/no state.             │
│ EQUIV     │ Backpressure needed (Observer -> Rx).    │
└───────────┴─────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. GoF patterns solve PROBLEMS, not implement OOP. Every pattern has a "problem statement." The
   Strategy pattern problem: "parameterize an algorithm/behavior." In 1994 (no lambdas): the
   solution was an interface + class. In 2024 (first-class functions): the solution is a lambda
   for simple cases, still an interface for complex cases. Know the PROBLEM; choose the simplest
   solution.
2. The FP vs OOP pattern decision rule: single-method, no state -> FP lambda. Multiple methods or
   complex state -> OOP pattern. Backpressure/async needed for Observer -> Reactive streams. DI
   container available -> Factory Method largely unnecessary. For the 6-10 patterns that STILL
   benefit from OOP even in modern languages: Decorator (multi-method), Visitor (double dispatch),
   Composite (tree structure), Proxy (multi-method interface).
3. Monad recognition: `Optional`, `CompletableFuture`, and `Stream` are all monads in Java (they
   all support `map` and `flatMap` with the same structural behavior). Recognizing this: the same
   `flatMap` pattern that flattens `Optional<Optional<T>>` to `Optional<T>` also flattens
   `Stream<Stream<T>>` to `Stream<T>` and `CompletableFuture<CompletableFuture<T>>` to
   `CompletableFuture<T>`. One pattern: three types. This is cross-paradigm pattern recognition
   at the most fundamental level.

**Interview one-liner:**
"Cross-paradigm patterns: GoF patterns solve recurring PROBLEMS. In 1994 (no first-class functions), Strategy = interface + class. In 2024 (Java 8+ lambdas), Strategy = lambda when one method, OOP interface when multiple methods or complex state. Key translations: Strategy -> lambda, Command -> Runnable/closure, Observer -> Reactive streams (with backpressure), Template Method -> higher-order function. Monads (Optional, CompletableFuture, Stream): share flatMap structure - cross-paradigm recognition enables reusing the same chaining mental model across all three."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
RECOGNIZE THE PROBLEM, NOT JUST THE SOLUTION.

This principle extends beyond patterns to all of engineering:
- Protocol design: "What PROBLEM is TCP's three-way handshake solving? (Establish reliable
  connection state on both sides before data transfer.)" -> "Could a two-way handshake solve it?
  (No: the client never confirms it received the server's SYN-ACK.)" -> "What other protocols
  solve the same problem differently? (QUIC: connection establishment in 0-RTT, different solution
  to the same connection reliability problem.)"
- Database: "What PROBLEM is a database index solving? (Avoid full table scan: O(n) -> O(log n)
  for lookups.)" -> "What other data structures solve the same problem? (Hash index: O(1) for
  exact match but no range queries. B-tree: O(log n) for both exact and range.)"
- System design: "What PROBLEM is a message queue solving? (Decouple producer from consumer:
  producer does not wait for consumer to process.)" -> "What else solves the same problem?
  (Batch processing, synchronous buffering, circuit breaker for rate limiting.)"

The engineer who understands PROBLEMS: can recognize when a new solution applies to an old
problem, and when an old solution is overkill for a simpler problem. The engineer who only
knows SOLUTIONS: pattern-matches on symptoms and applies a hammer to every nail.

---

### 💡 The Surprising Truth

The most important pattern in the GoF book is one that was considered trivial and obvious
when the book was published: the **Null Object** pattern. A Null Object: an implementation
of an interface that does nothing (or returns sensible defaults) instead of returning `null`.
This pattern - if applied universally in the Java ecosystem in 1996 instead of returning
`null` from methods - would have prevented the majority of Java NullPointerExceptions in
the history of the JVM. Tony Hoare (who invented null references in ALGOL in 1965) called it
his "billion-dollar mistake" in 2009, estimating the total cost of null-related bugs across
all software systems. The GoF book documented the Null Object pattern as a solution in 1994.
Java did not adopt it (Optional<T> did not arrive until Java 8 in 2014 - 20 years later).
The lesson: understanding patterns is not sufficient. The patterns must be embedded in the
language or framework so that engineers reach for them by DEFAULT, not as a special design
decision. Java Optional<T> (2014) and Kotlin's null safety (2016): finally gave mainstream
languages the "Null Object by default" behavior that the GoF book described as a design
pattern in 1994.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[TRANSLATION]** For each of these five GoF patterns: State, Visitor, Command, Strategy, Template
   Method - identify the problem it solves and its FP equivalent (if one exists). For each: when
   would you choose the OOP pattern over the FP equivalent?

2. **[SIMPLIFICATION]** Given a Java service with a `SortingStrategyFactory` that creates
   `BubbleSortingStrategy` or `QuickSortingStrategy` based on a configuration flag: refactor it
   to use `Comparator<T>` or `Function<List<T>, List<T>>` without any Factory or Strategy classes.

3. **[MONAD RECOGNITION]** Explain why `Optional`, `CompletableFuture`, and `Stream` are all monads.
   Demonstrate the structural equivalence of `Optional.flatMap`, `CompletableFuture.thenCompose`,
   and `Stream.flatMap` with a concrete example.

4. **[REACTIVE OBSERVER]** Convert a classical Java `EventListener` / `Observable` / `Observer`
   implementation to a Reactor `Flux` / `Sink` implementation. Show how backpressure is handled
   in the Reactor version that was not available in the classical Observer.

5. **[OVER-ENGINEERING DETECTION]** Given a codebase with `AbstractOrderProcessorFactory`,
   `OrderProcessorStrategy`, `OrderProcessorCommand`, and `OrderProcessorTemplate` for a service
   that does one thing: write a code review comment explaining which patterns are over-engineering,
   why, and what the simpler implementation would be.

---

### 🧠 Think About This Before We Continue

**Q1.** The Visitor pattern is often described as "double dispatch" - calling a method based on
the type of TWO objects (the visitor and the visited). Why is Visitor one of the GoF patterns
that does NOT have a simple FP equivalent in Java? What FP feature would replace it?

*Hint: VISITOR PATTERN - WHY NO SIMPLE FP EQUIVALENT IN JAVA (YET):

VISITOR SOLVES: "Add new operations to a class hierarchy without modifying the classes."
Example: a Document hierarchy (Paragraph, Table, Image). 
Operations: renderToHTML, renderToPDF, extractText.
Without Visitor: each new operation requires modifying every class (Open/Closed violation).
With Visitor: each operation is a Visitor class. The hierarchy accepts the visitor.
The hierarchy never changes when new operations are added.

WHY NO SIMPLE FP EQUIVALENT IN JAVA:
Visitor uses DOUBLE DISPATCH: when visitor.visit(element) is called:
  1. Dynamic dispatch on the VISITOR type (which operation to perform)
  2. The element calls visitor.visit(this): dynamic dispatch on the ELEMENT type
     to select the specific visitParagraph(), visitTable(), or visitImage() method.
Two levels of polymorphism: visitor type + element type.

In FP: this is PATTERN MATCHING. Match on the type of the value.
```
// Haskell / Scala:
def render(element: DocumentElement, format: RenderFormat): String = (element, format) match {
  case (Paragraph(text), HTML) => s"<p>$text</p>"
  case (Paragraph(text), PDF)  => renderParagraphToPdf(text)
  case (Table(rows), HTML)     => renderTableToHtml(rows)
  // Compiler: enforces exhaustive handling of all (element, format) pairs.
}
// This is Visitor WITHOUT the boilerplate. Pattern matching on BOTH dimensions.

// Java 21+ (limited pattern matching):
String render(DocumentElement element, RenderFormat format) {
    return switch (element) {           // dispatch on element type
        case Paragraph p -> switch (format) {  // dispatch on format type
            case HTML -> "<p>" + p.text() + "</p>";
            case PDF  -> renderToPdf(p.text());
        };
        case Table t -> switch (format) {
            case HTML -> renderTableToHtml(t.rows());
            case PDF  -> renderTableToPdf(t.rows());
        };
    };
}
// Java 21: pattern matching in switch (preview/standard in 21).
// Exhaustiveness: checked by compiler if element is sealed.
// This IS the FP equivalent of Visitor. But Java 21 is NEW.
// Java 8-20: no clean way to do this without Visitor pattern.

WHEN VISITOR IS STILL NEEDED (Java):
  - When the class hierarchy is NOT sealed (cannot enumerate all subtypes).
  - When the Visitor must maintain state across multiple visit() calls.
  - When compatibility with Java < 21 is required.

WITH JAVA 21+ sealed classes + pattern matching:
  Visitor pattern: largely replaceable with switch expression + sealed hierarchy.
  The compiler enforces exhaustive handling (like the GoF Visitor's compile-time completeness guarantee).

CONCLUSION: Visitor has no simple FP equivalent in Java 8-20.
In Java 21+ with sealed classes: pattern matching replaces it cleanly.
Haskell/Scala: had the FP equivalent for 30+ years (algebraic data types + pattern matching).
Java: catching up with Java 17 sealed classes + Java 21 pattern matching in switch.*

---

### 🎯 Interview Deep-Dive

**Q1: "How does the Strategy design pattern relate to functional programming?"**

*Why they ask:* Tests understanding of both OOP patterns and FP. Expected for senior Java engineers.

*Strong answer includes:*
- Strategy problem: "parameterize behavior." OOP solution: interface + concrete implementations.
- FP solution: first-class function (lambda, Comparator, Function<T,R>). The function IS the strategy.
- Java 8+ example: `list.sort(Comparator)` - Comparator is the Strategy as a function. No interface needed if Strategy is one method.
- When to keep OOP Strategy: strategy has multiple methods (sort + validate + serialize), complex internal state (dependencies, configuration), 10+ implementations where class hierarchy is clearer than 10 lambdas.
- Connection to Peter Norvig's finding: 17 of 23 GoF patterns are simpler in functional languages. Strategy is the canonical example.

**Q2: "What is a monad and do you use them in Java?"**

*Why they ask:* Tests FP depth. Expected for Scala/Kotlin/functional-oriented roles.

*Strong answer includes:*
- Monad: a design pattern for chaining computations in a context. Three operations: wrap (put value in context), map (transform value in context), flatMap (chain to context-producing computation, flattens nested context).
- Java examples: Optional (map/flatMap for null-safe computation), CompletableFuture (thenApply/thenCompose for async chaining), Stream (map/flatMap for collection processing).
- Structural equivalence: `Optional.flatMap`, `CompletableFuture.thenCompose`, `Stream.flatMap` are all the same monad operation on different types.
- Don't need to call it "monad" in production code. The concept: "chaining computations where each step can produce a new context-wrapped value."
