---
id: DPT-015
title: Decorator
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-012
used_by: DPT-018, DPT-041
related: DPT-012, DPT-018, DPT-016, DPT-041
tags:
  - pattern
  - structural
  - intermediate
  - java
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/design-patterns/decorator/
---

⚡ TL;DR - Decorator dynamically adds behavior to an object
by wrapping it in another object that implements the same
interface - enabling "add behavior without subclassing"
and composable behavior stacking at runtime.

| #15 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-012 | |
| **Used by:** | DPT-018, DPT-041 | |
| **Related:** | DPT-012, DPT-018, DPT-016, DPT-041 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `TextStream` class reads plain text. New requirements:
compressed reading, encrypted reading, buffered reading,
logging, and combinations thereof. Using inheritance:
`BufferedTextStream`, `EncryptedTextStream`,
`CompressedTextStream`, `BufferedEncryptedTextStream`,
`LoggingBufferedTextStream`,
`LoggingBufferedEncryptedCompressedTextStream` - the class
count explodes with each added behavior and combination.

**THE BREAKING POINT:**
With 4 optional behaviors (buffering, encryption, compression,
logging), inheritance produces 2^4 = 16 subclasses to cover
all combinations. Adding a 5th behavior doubles the count
again. Changing one behavior (upgrade the encryption
algorithm) requires modifying multiple subclasses.

**THE INVENTION MOMENT:**
Decorator: instead of subclassing, wrap the component in
another object that implements the SAME interface. The
wrapper adds behavior before/after delegating to the
wrapped object. Wrappers can be STACKED: buffered(encrypted
(compressed(stream))). Each decorator is independent;
combinations are achieved by composition, not inheritance.

**EVOLUTION:**
Decorator is central to Java I/O: `FileInputStream` is wrapped
in `BufferedInputStream`, which is wrapped in `GZIPInputStream`,
which is wrapped in `DataInputStream`. Each layer adds
behavior. This is the definitive Java Decorator application.
In modern Spring applications, AOP (Aspect-Oriented
Programming) achieves the same goal (adding behavior to
beans without modifying them) via generated proxies - a
dynamic Decorator.

---

### 📘 Textbook Definition

The **Decorator** pattern is a Structural design pattern
that attaches additional responsibilities to an object
dynamically. Decorators provide a flexible alternative to
subclassing for extending functionality. A Decorator
implements the same interface as the component it wraps
and maintains a reference to a Component object. Each
method in the Decorator delegates to the wrapped component
and adds behavior before, after, or around the delegation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Decorator wraps an object in another object with the same
interface, adding behavior without changing the original.

**One analogy:**
> A basic coffee (Component). Add milk → MilkDecorator
> wraps the coffee. Add syrup → SyrupDecorator wraps the
> milk-coffee. Each wrapper adds its cost to the total
> price. The order can be changed; any combination works.
> The base coffee is unchanged.

**One insight:**
Decorator is the "open/closed principle in action": the
base component is closed for modification; decorators
extend it without touching it. Behavior is composed,
not inherited. You can add, remove, and reorder behaviors
at runtime.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Decorator implements the SAME interface as the component
   it wraps - this is what makes the wrapping invisible
   to callers.
2. Decorator delegates to the wrapped component for all
   base behavior - it does not re-implement it.
3. Decorators are composable: any Decorator can wrap any
   other Component (including other Decorators).

**DERIVED DESIGN:**
Four participants:
- **Component**: the interface defining operations
- **ConcreteComponent**: the base implementation; the
  "unwrapped" object
- **Decorator** (abstract, optional): implements Component;
  holds a Component reference; base Decorator class
- **ConcreteDecorator**: specific Decorator that adds
  one behavior

**BEFORE/AFTER/AROUND:**
Each Decorator method can:
- Execute code BEFORE delegating: logging entry, metrics start
- Execute code AFTER delegating: logging exit, metrics end
- REPLACE the delegation: caching (skip call if cached)
- WRAP with exception handling: retry, fallback

**TRADE-OFFS:**

**Gain:** Single Responsibility: each Decorator adds exactly
one concern. OCP: add behaviors without modifying the
component. Composable: behaviors combined at runtime.

**Cost:** Debugging decorator chains is harder (many
layers in stack traces). Object identity is broken: a
Decorator is not the same object as what it wraps (equality
and instanceof checks may surprise). Order matters:
`compress(encrypt(data))` vs `encrypt(compress(data))`
have different results.

---

### 🧪 Thought Experiment

**SETUP:**
A payment service has `processPayment(Payment p)`. New
requirements: rate limiting (reject if too many requests),
logging (log all payment attempts), retry on failure, and
metrics recording. These must be independently combinable.

**WITHOUT DECORATOR:**
Four separate concerns in one `PaymentService.processPayment()`:
rate limiting code, logging code, retry logic, metrics code,
PLUS the actual payment logic. The method grows to 100 lines.
Testing the payment logic requires setting up rate limiter,
logger, metrics, AND retry logic.

**WITH DECORATOR:**
```
RateLimitedPaymentService(
  LoggingPaymentService(
    RetryingPaymentService(
      MetricsPaymentService(
        ActualPaymentService()))))
```
Each concern is in its own class (20-30 lines). The actual
payment service is tested alone. Behaviors are added or
removed by changing the wrapping order. The rate limiting
logic is reusable for any service.

**THE INSIGHT:**
Decorator decomposes cross-cutting concerns (logging, rate
limiting, retry, metrics) from business logic (actual
payment processing) at the object level, not the AOP level.

---

### 🧠 Mental Model / Analogy

> Decorator is like GIFT WRAPPING. A book (Component) is
> wrapped in tissue paper (Decorator 1) which is wrapped in
> a box (Decorator 2) which is wrapped in ribbon (Decorator 3).
> Every layer IS the gift - it is a "gift" that wraps a
> "gift." Unwrapping reveals the book inside. The book
> was never changed; each layer adds presentation.

- "Book" = ConcreteComponent
- "Tissue paper, box, ribbon" = ConcreteDecorators
- "Gift interface" = Component (what you can DO with it)
- "Unwrapping" = calling the delegate

**Where this analogy breaks down:**
Gift wrapping is sequential and only adds presentation.
Decorators can add functional behavior, can change the
ORDER of operations, and can conditionally skip the
delegation (caching: don't wrap the gift if you can
serve a cached copy). The analogy captures the structure
but not the behavioral flexibility.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Decorator adds new behavior to an existing object by
wrapping it. The wrapper looks exactly like the original
(same interface), so callers cannot tell they are talking
to a wrapper. You can stack multiple wrappers to add
multiple behaviors.

**Level 2 - How to use it (junior developer):**
Create a class that implements the same interface as the
target. Accept the target object in the constructor.
Delegate all method calls to the target. Add your extra
behavior before, after, or around the delegation.
Stack decorators by wrapping the result in another decorator.

**Level 3 - How it works (mid-level engineer):**
Java I/O is the canonical example: `new BufferedReader(new
FileReader("file.txt"))`. BufferedReader IS a Reader (same
interface). It wraps a FileReader (ConcreteComponent).
When `read()` is called on BufferedReader, it maintains
an internal buffer, reading ahead from the underlying
FileReader. When the buffer is empty, it calls
`wrapped.read()`. Buffering is added without modifying
FileReader.

**Level 4 - Why it was designed this way (senior/staff):**
Decorator addresses the fundamental tension between the
Single Responsibility Principle (each class does one thing)
and the Open/Closed Principle (don't modify existing code).
Adding a cross-cutting concern (logging, retry, metrics)
to a class violates SRP. Subclassing to add the concern
violates OCP eventually (class explosion). Decorator
satisfies both: each decorator is one responsibility;
the component is never modified. Spring AOP is Decorator
implemented via dynamic proxies - the framework generates
the wrapper class at runtime from annotations.

**Level 5 - Mastery (distinguished engineer):**
Decorator and AOP are structurally equivalent but differ
in how the wrapping is registered. Decorator: explicit
composition in code (`new Logging(new Retry(service))`).
AOP: declarative wrapping via annotations (`@Logged`,
`@Retryable`) with framework-generated proxies. Decorator
is easier to debug and trace (explicit in code). AOP
is less verbose for many call sites. Expert engineers
choose Decorator when the wrapping is domain-meaningful
(the logging IS part of the service contract) and AOP
when the concern is truly cross-cutting infrastructure
that all services share identically.

---

### ⚙️ How It Works (Mechanism)

```
Decorator Chain
┌────────────────────────────────────────────────────────┐
│  Client calls outermost.read()                         │
│                                                        │
│  LoggingDecorator          ← outer (adds logging)      │
│   ↓ log "before read"                                  │
│   → delegates to wrapped                               │
│                                                        │
│    BufferingDecorator      ← middle (adds buffer)      │
│     ↓ check buffer                                     │
│     → if empty, delegates to wrapped                   │
│                                                        │
│      FileInputStream       ← innermost (actual I/O)    │
│       ↓ reads bytes from disk                          │
│       ← returns bytes                                  │
│      BufferingDecorator fills buffer, returns bytes    │
│    LoggingDecorator logs result, returns bytes         │
│  Client receives bytes                                 │
│                                                        │
│  All objects implement InputStream (same interface)    │
│  Client sees only InputStream - knows nothing of chain │
└────────────────────────────────────────────────────────┘
```

**Chain construction:**
```
InputStream raw    = new FileInputStream("data.bin");
InputStream buffed = new BufferedInputStream(raw);  //
  wrap 1
InputStream zipped = new GZIPInputStream(buffed);   //
  wrap 2
// Now: reading from zipped decompresses bytes and buffers
  I/O
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client calls component.operation()
  → OuterDecorator.operation():
      pre-behavior (log, check rate limit, start timer)
      delegate: wrapped.operation()
      → InnerDecorator.operation():
          pre-behavior
          delegate: concreteComponent.operation()
          post-behavior
      ← result from inner
      post-behavior (log result, stop timer, emit metric)
  ← result from outer
Client receives result; never knew of any decorator
```

**FAILURE PATH:**
```
ConcreteComponent.operation() throws RuntimeException
  → InnerDecorator: exception propagates unless caught
  → OuterDecorator (Retry): catches, retries N times
  → After N retries: rethrows original exception
  → Client receives exception
Stack trace shows all decorator layers (debugging
  challenge)
```

**WHAT CHANGES AT SCALE:**
At high request rates, each decorator layer adds method
call overhead (JVM dispatch). With JIT compilation, the
overhead per layer is <10ns and effectively zero for
throughput. The real scale concern is stateful decorators:
a `RateLimitingDecorator` needs a shared counter across
threads; the counter management is the concurrency concern.

---

### 💻 Code Example

**Example 1 - Without Decorator (mixed concerns):**

```java
// BAD: payment logic mixed with logging, retry, metrics
class PaymentService {
    private final Logger log = LoggerFactory.getLogger(...);
    private final MeterRegistry metrics;

    void process(Payment p) {
        log.info("Processing payment {}", p.id()); // logging
        Timer.Sample sample = Timer.start(metrics); // metrics
        int attempts = 0;
        while (attempts < 3) { // retry logic
            try {
                actuallyProcess(p); // the real logic
                sample.stop(metrics.timer("payment.time"));
                log.info("Payment {} done", p.id());
                return;
            } catch (TransientException e) {
                attempts++;
                if (attempts == 3) throw e;
            }
        }
    }
}
// Testing actuallyProcess in isolation: impossible without
// setting up all surrounding infrastructure
```

**Example 2 - Decorator solution:**

```java
// GOOD: each concern in its own Decorator

// Component interface
interface PaymentProcessor {
    void process(Payment p);
}

// ConcreteComponent: only payment logic
class CorePaymentProcessor implements PaymentProcessor {
    public void process(Payment p) {
        // Only payment processing logic here
        gateway.charge(p.amount(), p.cardToken());
    }
}

// Abstract Decorator base (optional but reduces boilerplate)
abstract class PaymentDecorator implements PaymentProcessor {
    protected final PaymentProcessor wrapped;
    PaymentDecorator(PaymentProcessor wrapped) {
        this.wrapped = wrapped;
    }
}

// ConcreteDecorator 1: adds logging
class LoggingPaymentProcessor extends PaymentDecorator {
    LoggingPaymentProcessor(PaymentProcessor wrapped) {
        super(wrapped);
    }
    public void process(Payment p) {
        log.info("Processing {}", p.id());
        wrapped.process(p);          // delegate
        log.info("Processed {}", p.id());
    }
}

// ConcreteDecorator 2: adds retry
class RetryingPaymentProcessor extends PaymentDecorator {
    private final int maxAttempts;
    RetryingPaymentProcessor(PaymentProcessor w, int max) {
        super(w);
        this.maxAttempts = max;
    }
    public void process(Payment p) {
        for (int i = 1; i <= maxAttempts; i++) {
            try {
                wrapped.process(p); // delegate
                return;
            } catch (TransientException e) {
                if (i == maxAttempts) throw e;
                // else retry
            }
        }
    }
}

// Composition: stack decorators
PaymentProcessor core  = new CorePaymentProcessor(gateway);
PaymentProcessor retry = new RetryingPaymentProcessor(core, 3);
PaymentProcessor full  = new LoggingPaymentProcessor(retry);
// Usage: full.process(payment) → log → retry → core
// Testing core: inject CorePaymentProcessor directly (no noise)
```

**Example 3 - Java I/O as canonical Decorator:**

```java
// RECOGNITION: Java I/O IS the Decorator pattern
// Component interface: InputStream
// ConcreteComponent: FileInputStream (raw bytes from file)
// Decorators: BufferedInputStream, GZIPInputStream, etc.

InputStream in = new GZIPInputStream(          // decompress
                   new BufferedInputStream(    // buffer
                     new FileInputStream(      // read file
                       "data.csv.gz")));

// Reading from 'in': decompresses GZip blocks,
//   reads through buffer, reads from file as needed
// Each class in chain: InputStream -> InputStream (same iface)
// Order matters: GZip wraps Buffered wraps File
// Change order: BufferedInputStream(new GZIPInputStream(...))
//   is also valid - buffer AFTER decompression
int b = in.read(); // single interface; whole chain engaged
```

**How to test/verify correctness:**
Test ConcreteComponent in isolation (zero decorator
dependencies). Test each ConcreteDecorator with a mock
wrapped component: verify it calls the mock, verify it
executes its added behavior. Test the composed chain
end-to-end with integration tests.

---

### ⚖️ Comparison Table

| Approach        | Add behavior | Same interface | Runtime compose | Test in isolation |
| --------------- | ------------ | -------------- | --------------- | ----------------- |
| **Decorator**   | Yes          | Yes            | Yes             | Yes               |
| Inheritance     | Yes          | Yes            | No (compile)    | No (coupled)      |
| AOP (Spring)    | Yes          | Yes (proxy)    | Via annotations | Yes (no proxy)    |
| Static utility  | Sort of      | No             | No              | Yes               |

**How to choose:**
- Adding behavior composably at runtime? Decorator
- Same behavior across all instances of a type (library
  framework level)? AOP
- Only one combination ever needed? Inheritance is simpler
- Decorators vs AOP: Decorators are explicit (visible in
  code); AOP is implicit (added via annotations, invisible
  at call sites). Use Decorators when the wrapping is
  meaningful to domain logic; AOP for pure infrastructure

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Decorator changes the interface | Decorator does NOT change the interface - it implements the SAME interface. If the interface changes: Adapter, not Decorator |
| Decorator and Proxy are the same | Decorator adds behavior; Proxy controls access or adds lifecycle management (lazy loading, remote invocation). Both wrap and implement the same interface - the PURPOSE differs |
| Decorator order does not matter | Order is critical for many decorators: logging before caching logs misses; caching before retry caches errors |
| The base Decorator class is required | The abstract base Decorator class is optional (Bloch recommends it for boilerplate reduction but it is not required) |
| AOP replaces Decorator | AOP is Decorator with framework-generated wrappers; they solve the same problem with different trade-offs (explicit vs declarative) |

---

### 🚨 Failure Modes & Diagnosis

**Decorator Breaking Object Identity**

**Symptom:**
A service stores a reference to a `PaymentProcessor`
and later checks `processor instanceof CorePaymentProcessor`
to determine if direct charging is supported. After adding
a Logging decorator, the check always returns false, even
though the core processor is inside the chain. Null
pointer exceptions occur where the code expected a specific
processor type.

**Root Cause:**
Decorators wrap objects - `instanceof` checks on a decorator
return the decorator's type, not the wrapped component's
type. Object identity is broken by design.

**Diagnostic Signal:**
`instanceof` checks on a Component type in code that USES
a decorated component indicate a design issue.

**Fix:**
Remove `instanceof` checks from client code. If specific
behavior needs to be queryable, add a method to the
Component interface: `boolean supportsDirectCharge()`.
Implement it in the concrete component as `return true`;
implement it in Decorators that preserve the contract as
`return wrapped.supportsDirectCharge()`.

**Prevention:**
Never check `instanceof` on decorated objects in client
code. Design the Component interface to expose all
capabilities clients need to query. Decorators pass
through capability queries by default.

---

**Decorator Chain State Inconsistency**

**Symptom:**
A `LoggingDecorator` wraps a `RetryingDecorator`. Logs
show "Processing payment X" once (log before first attempt),
but the actual payment is processed 3 times (RetryingDecorator
retries twice). The logs show one "Processing" but three
charges. Customers are billed three times.

**Root Cause:**
The RetryingDecorator retries the wrapped.process() call,
but the LoggingDecorator is OUTSIDE the retry loop - it
only logs the outer call, not each retry.

**Diagnostic Signal:**
When a decorator's behavior depends on the number of actual
calls to the inner component, and a retry decorator is
in the chain, the outer decorator's count may not match
the inner call count.

**Fix:**
Rearrange the decorator chain: wrap the RetryingDecorator
OUTSIDE the LoggingDecorator so logging happens once per
final attempt:
```java
// Before (wrong for logging):
new LoggingDecorator(new RetryingDecorator(core));
// After (logs each attempt):
new RetryingDecorator(new LoggingDecorator(core));
// Or: each decorator is clear about its scope
```

**Prevention:**
Document the intended order of decorator stacking.
Use a builder to assemble the chain in the correct order
rather than ad-hoc composition at call sites.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Adapter` - related wrapping pattern; understanding
  Adapter's "different interface" helps clarify Decorator's
  "same interface" characteristic

**Builds On This (learn these next):**
- `Decorator vs Proxy vs Adapter` - deep structural pattern
  comparison; resolves the most common pattern confusion
- `Proxy` - same wrapping mechanism; Proxy is for access
  control, Decorator for behavior addition

**Alternatives / Comparisons:**
- `Proxy` - same structure (wraps, same interface), different
  purpose (control access, not add behavior)
- `Chain of Responsibility` - also chains handlers; CoR is
  for REQUEST ROUTING (each handler decides to handle or pass);
  Decorator for BEHAVIOR STACKING (all handlers always execute)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Wrapper adding behavior to an object     │
│              │ via same-interface composition           │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Decorator IS-A Component AND HAS-A       │
│              │ Component (self-referential, composable) │
├──────────────┼──────────────────────────────────────────┤
│ VS ADAPTER   │ Adapter: changes the interface           │
│              │ Decorator: same interface, adds behavior │
├──────────────┼──────────────────────────────────────────┤
│ VS PROXY     │ Proxy: controls access (same interface)  │
│              │ Decorator: adds behavior (same interface)│
├──────────────┼──────────────────────────────────────────┤
│ ORDER MATTERS│ compress(encrypt(data)) ≠               │
│              │ encrypt(compress(data))                  │
├──────────────┼──────────────────────────────────────────┤
│ REAL EXAMPLE │ java.io: BufferedInputStream(            │
│              │  GZIPInputStream(FileInputStream()))     │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ instanceof checks on decorated objects   │
│              │ return decorator type, not wrapped type  │
├──────────────┼──────────────────────────────────────────┤
│ MODERN EQUIV │ Spring AOP = generated Decorator proxies │
│              │ via @Transactional, @Cacheable, etc.     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Facade → Proxy → Chain of Responsibility │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Decorator = same interface, wraps, adds behavior.
   Adapter = different interface. Proxy = same interface,
   controls access. The same wrapping mechanism; different
   purposes.
2. Java I/O IS Decorator: `new BufferedInputStream(new
   GZIPInputStream(new FileInputStream(...)))` is the
   canonical example - memorize this structure
3. Order of decorator stacking matters: it affects both
   correctness (encrypt-then-compress vs compress-then-encrypt)
   and behavior (log inside or outside retry loop)

**Interview one-liner:**
"Decorator adds behavior to an object by wrapping it in
another object with the same interface, enabling composable
behavior without subclassing. Java I/O is the canonical
example: BufferedInputStream wraps GZIPInputStream wraps
FileInputStream - each adds one behavior to the InputStream
interface. Spring's @Transactional generates a Decorator
proxy dynamically."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate WHAT a class does (its core responsibility) from
HOW it is enhanced (logging, caching, retrying, rate
limiting). Decorators make each enhancement a standalone,
reusable class that works with any component implementing
the interface.

**Where else this pattern appears:**
- **Java I/O** - the canonical implementation: every
  `InputStream` and `OutputStream` subclass that wraps
  another is a Decorator: `BufferedInputStream`,
  `DataInputStream`, `GZIPInputStream`,
  `CipherInputStream`, `CheckedInputStream`
- **Spring AOP** - `@Transactional`, `@Cacheable`,
  `@Async`, `@Retryable` are all Decorator proxies
  generated by Spring at startup via CGLIB or JDK proxy
- **Resilience4j** - `Decorators.ofSupplier(service)
  .withRetry(retry).withCircuitBreaker(cb).decorate()` is
  explicit Decorator composition for fault-tolerance

**Industry applications:**
- **HTTP client interceptors** - OkHttp `Interceptor`,
  Apache HttpClient `HttpRequestInterceptor` - each is
  a Decorator around the HTTP call chain
- **Authentication middleware** - each security concern
  (JWT validation, RBAC check, rate limiting) is a
  Decorator around the handler function in Servlet-based
  and functional frameworks

---

### 💡 The Surprising Truth

Java's `Collections.synchronizedList(list)` IS a Decorator.
It wraps a `List` in another object that implements `List`
(same interface), adding `synchronized` blocks around
every method call. The wrapped list is unchanged - the
Decorator adds thread-safety to any List implementation
without requiring the underlying list to be thread-aware.
`Collections.unmodifiableList()`, `Collections.checkedList()`,
and `Collections.emptyList()` are all Decorators in the
Java standard library, applied to the most common
collection interfaces. Java's Collections class is a
Decorator factory - yet most developers call it "a utility
class" rather than recognizing that every `synchronized*`
and `unmodifiable*` method is producing a Decorator.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [DISTINGUISH] State in one sentence each the difference
   between Decorator, Proxy, and Adapter - all three use
   the same wrapping structure but serve different purposes
2. [BUILD] Implement a Decorator chain from memory for
   Java I/O: FileInputStream → BufferedInputStream →
   GZIPInputStream → DataInputStream; draw the wrapping
   structure and describe what each layer adds
3. [ORDER] Explain why `logging(retry(service))` vs
   `retry(logging(service))` produces different behavior
   for a retried operation - which is correct for
   "log every attempt" vs "log only the final outcome"
4. [DIAGNOSE] Given a decorator chain where `instanceof`
   checks fail unexpectedly, identify the root cause and
   implement the fix using interface methods instead
5. [COMPARE] Explain when you would choose explicit
   Decorator composition vs Spring AOP for adding logging
   to a service - state the deciding criterion

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `@Transactional` generates a Decorator
proxy around a service bean. When `serviceA.method1()`
calls `serviceA.method2()` (both `@Transactional`), does
the second transaction decorator intercept the call to
`method2()`? Why or why not? What is the name for this
problem?

*Hint: No. The proxy is around the bean from the outside.
When code INSIDE the bean calls another method on the same
bean, it calls `this.method2()` - which bypasses the proxy.
This is the "self-invocation proxy trap." The decorator
is not invoked for internal calls. Solution: inject the
proxy reference (AopContext.currentProxy()) or restructure
to call through a separate bean.*

**Q2.** Resilience4j's Decorator API:
`Decorators.ofSupplier(service::call).withRetry(retry)
.withCircuitBreaker(cb).withBulkhead(bh).decorate()`
stacks three decorators. What is the execution order?
Which decorator is outermost? If the circuit breaker is
OPEN, does the retry decorator still execute?

*Hint: The LAST decorator added becomes the outermost.
Execution: Bulkhead checks concurrency → CircuitBreaker
checks open/closed → Retry wraps the actual call.
If CircuitBreaker is open: it throws CallNotPermittedException
BEFORE reaching the Retry decorator. The Retry (innermost)
never sees the call. This matters for metric counting:
circuit-breaker-open calls are counted by the CB, not by
Retry.*

**Q3.** Design a "debuggable decorator chain" for a payment
service. The chain is `logging(rateLimit(retry(core)))`.
When a failure occurs, you need to know: how many times
retry attempted, what the rate limiter's current count was,
and what the core processor's error was. How do you expose
this diagnostic information without breaking the Decorator
pattern (without making client code aware of decorator
internals)?

*Hint: Add a DiagnosticContext (ThreadLocal or MDC) that each
decorator writes to. LoggingDecorator reads DiagnosticContext
on exit and logs all accumulated context. Each decorator
writes: `DiagnosticContext.put("retryCount", n)` or
`DiagnosticContext.put("rateLimitCount", m)`. The logging
decorator aggregates and outputs the full context in one
structured log entry. Client code only knows the outer
interface; diagnostics flow through the shared context.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between Decorator and Proxy?
They seem to have identical structure.**

*Why they ask:* Most common Decorator confusion in interviews;
tests whether the candidate knows purpose vs structure.

*Strong answer includes:*
- Structure: IDENTICAL - both wrap an object, both implement
  the same interface, both delegate to the wrapped object
- PURPOSE differs:
  - Decorator: ADD BEHAVIOR - logging, buffering, retry,
    metrics; the wrapped object is used normally, behaviors
    are stacked
  - Proxy: CONTROL ACCESS - lazy initialization (virtual
    proxy), remote invocation (remote proxy), access control
    (protection proxy), caching (caching proxy)
- Practical distinction: Decorator changes WHAT the method
  DOES (adds behavior); Proxy may change WHETHER the method
  executes at all (protection proxy can reject calls)

**Q2: Explain Java's I/O class hierarchy as an example
of the Decorator pattern.**

*Why they ask:* This is the canonical Java Decorator example;
tests real-world pattern recognition.

*Strong answer includes:*
- Component interface: `java.io.InputStream`
- ConcreteComponent: `FileInputStream` (reads raw bytes
  from a file; no decoration)
- Decorators: `FilterInputStream` (the abstract Decorator
  base), `BufferedInputStream` (adds buffering),
  `GZIPInputStream` (adds decompression),
  `DataInputStream` (adds primitive type reading)
- Construction: `new DataInputStream(new GZIPInputStream(
  new BufferedInputStream(new FileInputStream("f.gz"))))`
- Every class in the chain IS-A InputStream; reading from
  DataInputStream reads → decompresses → buffers → file I/O

**Q3: How does Spring's @Transactional implement the
Decorator pattern? What generates the wrapper class?**

*Why they ask:* Tests understanding of Spring internals
and connection between pattern and framework.

*Strong answer includes:*
- Spring detects `@Transactional` beans during context
  creation and generates a proxy (wrapper) class
- Two proxy mechanisms: JDK dynamic proxy (if the bean
  implements an interface) or CGLIB subclass proxy (if
  the bean is a concrete class)
- The generated proxy IS-A Component (same interface or
  subclass), wraps the real bean, implements Decorator
  pattern: before the method call - begin transaction;
  after method call - commit; on RuntimeException - rollback
- The real bean has no transaction code; the Decorator
  proxy handles the lifecycle
- Self-invocation problem: internal method calls bypass
  the proxy because `this.method()` calls the real bean,
  not the proxy wrapper

