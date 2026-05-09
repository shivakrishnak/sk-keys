---
layout: default
title: "Decorator"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /design-patterns/decorator/
id: DPT-015
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
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-015 - Decorator

⚡ TL;DR - Decorator adds behaviour to an object at runtime without changing its class by wrapping it in objects that implement the same interface.

| DPT-015 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Composition over Inheritance, Interface, Polymorphism, Object-Oriented Programming (OOP) | |
| **Used by:** | Java I/O Streams, Web Middleware, Logging Wrappers, HTTP Request Pipelines | |
| **Related:** | Proxy, Adapter, Composite, Bridge, Chain of Responsibility | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An `InputStream` needs to support: buffering (for performance), gzip decompression (for compressed data), and encryption (for secure data). Using inheritance: `BufferedInputStream`, `GzipInputStream`, `EncryptedInputStream`, `BufferedGzipInputStream`, `BufferedEncryptedInputStream`, `GzipEncryptedInputStream`, `BufferedGzipEncryptedInputStream` - 7 classes for 3 features in 3 combinations. With 4 features: 15 classes. With N features: 2^N - 1 classes. Every combination requires a new subclass with copy-pasted logic.

**THE BREAKING POINT:**
A user wants to read a gzip-compressed, encrypted, buffered network stream. To add this combination: write exactly the same N-way inheritance it already uses or create yet another subclass. The class hierarchy is a combinatorial explosion of every possible feature combination - each combination a separate class that must be tested, maintained, and updated when any feature changes.

**THE INVENTION MOMENT:**
This is exactly why the Decorator pattern was created. Java's I/O library uses it correctly: each feature is a separate decorator class. To read a gzip-compressed, encrypted, buffered stream: `new BufferedInputStream(new GzipInputStream(new EncryptedInputStream(socket.getInputStream())))`. Three independent decorators, composed dynamically. Adding a fourth feature: add one class. Zero subclass explosion.

**EVOLUTION:**
Decorator was the standard solution for cross-cutting concerns
in pre-AOP Java. Spring AOP and AspectJ (early 2000s) largely
replaced manual decorator chains for logging, security, and
transaction management by weaving these concerns at the
bytecode level. Decorator survived and thrived in I/O streams
(Java's `InputStream`/`OutputStream` hierarchy uses it
pervasively) and in functional composition (`Function.andThen()`,
`Stream.filter(...).map(...)`). Modern annotations + AOP cover
most cross-cutting use cases, while Decorator remains the
primary pattern for streaming I/O and functional pipelines.

---

### 📘 Textbook Definition

The **Decorator** pattern is a structural design pattern that attaches additional responsibilities to an object dynamically. A Decorator class implements the same interface as the decorated object, holds a reference to the component (the object being decorated), and calls the component's methods - adding behaviour before or after each call. Multiple decorators can be layered, each wrapping the previous, forming a chain that composes behaviour. The pattern is an alternative to subclassing for extending functionality.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Wrap an object with another object of the same interface to silently add behaviour.

**One analogy:**
> Wrapping a gift. The gift is the core object. Wrapping paper adds visual decoration. A bow adds an extra flourish. A gift bag wraps the whole thing. Each layer adds something to the presentation - none changes what's inside - and the recipient sees only the outermost layer.

**One insight:**
The secret of Decorator is that both the wrapper and the wrapped object implement the same interface. This means ANY number of wrappers can be stacked, and the caller never knows. The caller calls `read()` on what appears to be a simple InputStream - in reality, the call passes through three decorator layers before reaching the actual data source.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The same interface must be accessible before and after decoration - clients must not need to change how they use the object.
2. Feature combinations cannot all be foreseen - the set of possible combinations is open.
3. Features must be independent - applying encryption should not require knowing about buffering.

**DERIVED DESIGN:**
Given invariant 1: the Decorator must implement the same interface as the Component. Given invariant 2: each feature is a separate Decorator class, not a separate subclass per combination. Given invariant 3: each Decorator's logic is independent - it calls `component.method()` and adds its concern before or after.

The pattern structure is:
```
abstract class Decorator implements Component {
    protected final Component wrapped;
    Decorator(Component c) { wrapped = c; }
    void operation() { wrapped.operation(); }  // default delegate
}
```
Concrete decorators override `operation()` to add their behaviour. The delegation chain (`wrapped.operation()` call) ensures the entire chain executes.

**THE TRADE-OFFS:**
**Gain:** Feature combinations at runtime - any order, any subset; each feature class is independently testable; no class explosion; Open/Closed Principle: add features without modifying existing classes.
**Cost:** Many small wrapper objects accumulate - debugging requires understanding the entire chain; object identity is lost (wrapped ≠ decorator in `==`); order of decorators matters for correctness (encrypting before compressing vs after produces different results); constructing a deeply nested chain is verbose and error-prone without a builder API.

---

### 🧪 Thought Experiment

**SETUP:**
A simple `TextWriter` writes plain text to a file. Requirements emerge over time: (1) write to a log file simultaneously, (2) encrypt sensitive fields, (3) compress output. Using inheritance would be 7 classes. Using Decorator:

**WHAT HAPPENS WITHOUT DECORATOR (inheritance):**
```
TextWriter → LoggingTextWriter
          → EncryptingTextWriter
          → CompressingTextWriter
          → LoggingEncryptingTextWriter
          → LoggingCompressingTextWriter
          → EncryptingCompressingTextWriter
          → LoggingEncryptingCompressingTextWriter
```
A bug in logging requires fixing `LoggingTextWriter`, `LoggingEncryptingTextWriter`, `LoggingCompressingTextWriter`, and `LoggingEncryptingCompressingTextWriter` - four classes for one fix.

**WHAT HAPPENS WITH DECORATOR:**
```
TextWriter writer = new LoggingDecorator(
    new CompressingDecorator(
        new EncryptingDecorator(
            new BasicTextWriter(file))));
```
Bug in logging: fix `LoggingDecorator` only. New requirement (add timestamping): add `TimestampDecorator` class, zero changes to existing classes.

**THE INSIGHT:**
Each decorator owns exactly one concern. A bug in one concern has exactly one fix location. A new concern has exactly one addition. The chain does NOT require changing any existing class.

---

### 🧠 Mental Model / Analogy

> Decorator is like a stack of transparent filters on a camera lens. The base lens captures the image (Component). A UV filter (Decorator 1) reduces haze. A polariser (Decorator 2) reduces glare. A neutral density filter (Decorator 3) allows longer exposure. Each filter is independent. Stacking them in any order works (though order affects the result). Removing one requires no changes to others. The photographer uses the lens stack without knowing exactly which filters are on it.

- "Base camera lens" → Component (basic implementation)
- "Each filter" → Decorator class
- "Stacking filters" → wrapping one decorator inside another
- "Photographer using the stacked lens" → client using Component interface
- "Order of filters matters" → decorator order affects behaviour
- "Adding a fourth filter" → adding one Decorator class, no other changes

Where this analogy breaks down: camera filters only affect the output (light). Decorators can affect both input parameters (modification before delegating) and output values (modification after delegating receives the wrapped result).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Decorator is gift-wrapping for objects. The original object is unchanged. Each wrapper adds a layer of new behaviour. The final user sees all the layers as if it were one object. Unwrap one layer and the behaviour below is still there - all independent.

**Level 2 - How to use it (junior developer):**
Create a `Component` interface. Implement a `BaseComponent`. Create a `Decorator` abstract class that implements `Component` and holds a `Component` reference. Concrete decorators extend `Decorator` and override methods: call `super.method()` (which calls `wrapped.method()`) and add their behaviour. Stack decorators at construction. In Spring applications, AOP proxies are runtime Decorators applied via `@Around` advice without manual wrapping.

**Level 3 - How it works (mid-level engineer):**
The chain execution order: calling `topDecorator.operation()` → `topDecorator` runs pre-behaviour → calls `middleDecorator.operation()` → `middleDecorator` runs pre-behaviour → calls `baseComponent.operation()` → returns value → `middleDecorator` runs post-behaviour → returns → `topDecorator` runs post-behaviour → caller receives result. This is an onion-peel execution model - each decorator wraps the next, innermost runs last. This is identical to HTTP middleware chains in Node.js/Express and Servlet Filters in Java EE. The decorator chain is essentially a manually-constructed call stack.

**Level 4 - Why it was designed this way (senior/staff):**
Decorator is the OOP equivalent of function composition: `f(g(h(x)))`. In functional programming, this is first-class; in OOP, Decorator achieves the same composition. The critical constraint is that each decorator must implement the same interface as the component - this is what enables transparent substitution. In Java I/O, `InputStream`/`OutputStream` is the interface; `FileInputStream`, `SocketInputStream` are base implementations; `BufferedInputStream`, `DataInputStream`, `GZIPInputStream` are decorators. The design is so fundamental that it was chosen as the core abstraction for Java I/O in 1996, and it scales from single-threaded to multi-threaded use with appropriate synchronisation decorators (`SynchronizedOutputStream`). In modern frameworks, Decorator manifests as: Spring AOP `@Around`, Spring Security filter chains, Servlet filters, Express middleware, and `java.util.Collections.synchronizedList()` - all wrappers adding behaviour to existing interfaces without modification.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────┐
│  DECORATOR CHAIN - CALL FLOW                  │
│                                               │
│  Client                                       │
│     │ read()                                  │
│     ▼                                         │
│  BufferedInputStream  ← Decorator 3           │
│     │ checks buffer first                     │
│     │ if empty: read() below                  │
│     ▼                                         │
│  GZIPInputStream  ← Decorator 2               │
│     │ bytes from below                        │
│     │ decompress block                        │
│     ▼                                         │
│  EncryptedInputStream  ← Decorator 1          │
│     │ bytes from below                        │
│     │ decrypt block                           │
│     ▼                                         │
│  FileInputStream  ← Base Component            │
│     │ raw bytes from disk                     │
│                                               │
│  Return path (bottom to top):                 │
│   raw bytes → decrypted → decompressed →      │
│   buffered → returned to client               │
└───────────────────────────────────────────────┘
```

**Execution order is LIFO for output:**
```
client.read():
  BufferedInputStream.read():
    (no buffered data)
    GZIPInputStream.read():
      EncryptedInputStream.read():
        FileInputStream.read():
          → raw encrypted+compressed bytes
        ← decrypt
      ← decompress
    ← buffer
  ← return plain bytes
← client receives plain bytes
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Application Layer
  → Calls textService.write("Hello")
  → Reaches LoggingDecorator.write("Hello")
                              ← YOU ARE HERE
  → Logs: "Writing: Hello"
  → Calls wrapped.write("Hello")
  → Reaches EncryptingDecorator.write("Hello")
  → Encrypts: "X4kP..." 
  → Calls wrapped.write("X4kP...")
  → Reaches BaseTextWriter.write("X4kP...")
  → Writes to file
  → Returns to EncryptingDecorator (post-actions: none)
  → Returns to LoggingDecorator
  → Logs: "Write complete"
  → Returns to Application
```

**FAILURE PATH:**
```
EncryptingDecorator throws EncryptionException
  → propagates up through LoggingDecorator
  → LoggingDecorator catches, logs the error, re-throws
  → Application sees EncryptionException with audit log
  → Correct: each decorator handles/propagates as designed
```

**WHAT CHANGES AT SCALE:**
At high throughput (100,000 writes/second), each decorator adds a method call overhead (~5 ns) and potential object allocation. With 5 decorators, ~25 ns overhead per operation. For CPU-intensive operations this is negligible; for microsecond-latency systems, directly implementing the combined behaviour may be preferred. Object creation in the chain creates GC pressure - decorator instances should be long-lived (one chain per service) rather than recreated per request.

---

### 💻 Code Example

**Example 1 - BAD: Subclassing for feature combinations:**
```java
// BAD: 7 classes for 3 features in all combinations
class BufferedEncryptedCompressedWriter
    extends BufferedEncryptedWriter {
    // Duplicate compress logic + all parent constructors
    // Bug in buffering requires fixing 4 classes
}
```

**Example 2 - GOOD: Decorator pattern:**
```java
// Component interface
public interface TextWriter {
    void write(String text);
    void flush();
    void close();
}

// Base component: plain file writing
public class FileTextWriter implements TextWriter {
    private final Writer writer;

    public FileTextWriter(Path path) throws IOException {
        this.writer = Files.newBufferedWriter(path);
    }

    @Override public void write(String text) {
        try { writer.write(text); }
        catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
    @Override public void flush() {
        try { writer.flush(); }
        catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
    @Override public void close() {
        try { writer.close(); }
        catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}

// Abstract decorator base - delegates by default
public abstract class TextWriterDecorator
        implements TextWriter {
    protected final TextWriter wrapped;

    protected TextWriterDecorator(TextWriter wrapped) {
        this.wrapped = wrapped;
    }

    @Override public void write(String text) {
        wrapped.write(text);        // default delegation
    }
    @Override public void flush()  { wrapped.flush(); }
    @Override public void close()  { wrapped.close(); }
}

// Concrete decorator 1: add logging
public class LoggingTextWriter extends TextWriterDecorator {
    private final Logger log = LoggerFactory.getLogger(
        LoggingTextWriter.class);

    public LoggingTextWriter(TextWriter wrapped) {
        super(wrapped);
    }

    @Override
    public void write(String text) {
        log.debug("Writing {} chars", text.length());
        wrapped.write(text);         // always delegate
        log.debug("Write complete");
    }
}

// Concrete decorator 2: add upper-case transformation
public class UpperCaseTextWriter extends TextWriterDecorator {
    public UpperCaseTextWriter(TextWriter wrapped) {
        super(wrapped);
    }

    @Override
    public void write(String text) {
        wrapped.write(text.toUpperCase()); // transform, then delegate
    }
}

// Concrete decorator 3: add character counting
public class CountingTextWriter extends TextWriterDecorator {
    private int totalCharsWritten = 0;

    public CountingTextWriter(TextWriter wrapped) {
        super(wrapped);
    }

    @Override
    public void write(String text) {
        totalCharsWritten += text.length();
        wrapped.write(text);
    }

    public int getTotalCharsWritten() {
        return totalCharsWritten;
    }
}

// Usage: compose any combination at runtime
CountingTextWriter counter = new CountingTextWriter(
    new LoggingTextWriter(
        new UpperCaseTextWriter(
            new FileTextWriter(Paths.get("output.txt"))
        )
    )
);
counter.write("hello world");
System.out.println(counter.getTotalCharsWritten()); // 11
// File contains: "HELLO WORLD", with logging of the write
```

**Example 3 - Java I/O (real-world Decorator in JDK):**
```java
// Decorator chain for reading compressed encrypted data:
try (InputStream in =
        new BufferedInputStream(        // Decorator 3
            new GZIPInputStream(        // Decorator 2
                new CipherInputStream(  // Decorator 1
                    new FileInputStream("data.enc.gz"),
                    cipher)))) {        // Base Component

    byte[] buffer = new byte[8192];
    int bytesRead;
    while ((bytesRead = in.read(buffer)) != -1) {
        process(buffer, bytesRead);
    }
}
// Java I/O has been using Decorator since 1.0 (1996)
```

**Example 4 - Spring AOP as runtime Decorator:**
```java
// Spring @Around is a Decorator applied via proxy
@Aspect
@Component
public class LoggingAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object logAround(ProceedingJoinPoint jp)
            throws Throwable {
        log.info("Before: {}", jp.getSignature());
        Object result = jp.proceed(); // calls wrapped method
        log.info("After: {}", jp.getSignature());
        return result;
    }
}
// Spring generates a Decorator proxy at runtime
// Service interface contract unchanged for callers
```

---

### ⚖️ Comparison Table

| Pattern | Same Interface? | Adds Behaviour? | Structure | Best For |
|---|---|---|---|---|
| **Decorator** | Yes (wraps same) | Yes | Chain | Adding features without subclassing |
| Proxy | Yes (wraps same) | No (controls access) | Single wrap | Caching, security, lazy loading |
| Adapter | No (translates) | No | Single wrap | Incompatible interface integration |
| Composite | Yes (tree) | No (aggregates) | Tree | Part-whole hierarchies |
| Chain of Responsibility | Yes | Optional | Chain | Conditional handler chain |

How to choose: use Decorator to add behaviour transparently. Use Proxy to control access to an object. Use Adapter to translate interfaces. If behaviour is conditional (some handlers may not process a request), use Chain of Responsibility instead.

---

### 🔁 Flow / Lifecycle

```
DECORATOR CHAIN CONSTRUCTION
────────────────────────────────────────
1. Create base component:
   base = new FileTextWriter(path)

2. Wrap with first decorator:
   enc = new EncryptingDecorator(base)

3. Wrap with second decorator:
   log = new LoggingDecorator(enc)

4. Client receives reference to outermost:
   TextWriter writer = log;

METHOD CALL FLOW (write("data"))
────────────────────────────────────────
→ LoggingDecorator.write("data")
    pre-action: log
    → EncryptingDecorator.write("data")
        pre-action: encrypt → "Xk4p"
        → FileTextWriter.write("Xk4p")
            write to disk
        ← return
        post-action: (none)
    ← return
    post-action: log "complete"
← return to caller

CHAIN DISMANTLING
────────────────────────────────────────
close() propagates through chain:
LoggingDecorator.close()
  → EncryptingDecorator.close()
      → FileTextWriter.close()  ← flushes+closes file
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Decorator and Proxy are the same pattern | Decorator adds behaviour. Proxy controls access (caching, authentication, lazy loading) without changing behaviour. Both wrap same-interface objects - the intent differs |
| Decorator changes the object being decorated | Decorator adds behaviour in the wrapping layer. The decorated object is unchanged and can be used directly without decorators if needed |
| Decorator order never matters | Order matters significantly. Encrypt-then-compress ≠ compress-then-encrypt. Log-then-transform ≠ transform-then-log. Always document intended decorator order |
| Only one decorator can be applied at a time | Any number of decorators can be stacked. Java's `BufferedInputStream(GZIPInputStream(CipherInputStream(FileInputStream)))` shows four levels |
| Decorator requires modifying the base component class | The base component only needs to implement the Component interface. Decorators add behaviour purely through composition |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing Delegation - Decorator Swallows the Call**

**Symptom:** Adding a decorator causes the underlying operation to stop executing. No errors - the operation silently does nothing.

**Root Cause:** The decorator overrides a method but never calls `wrapped.operation()`. The chain is broken.

**Diagnostic:**
```java
// Add instrumentation to base component:
@Override public void write(String text) {
    log.trace("FileTextWriter.write called: {}", text);
    // ... write to file
}
// If log never appears after adding decorator:
// decorator isn't delegating
grep -n "wrapped\." LoggingTextWriter.java
# If method not found in the grep results: delegation missing
```

**Fix:**
Every overridden method in a Decorator must call `wrapped.method(...)`. Use the abstract base decorator class pattern to enforce default delegation.

**Prevention:** Code review rule: every overridden method in a Decorator must include a `wrapped.*` call (or explicitly document why it is intentionally suppressed).

---

**2. Exception Handling Breaks Chain - Wrapper Catches Without Re-throwing**

**Symptom:** An error occurs in the base component, but the decorator swallows it. The caller receives a successful response while the underlying write failed silently.

**Root Cause:** A decorator's try-catch catches an exception and only logs it, not re-throwing. Callers never know the operation failed.

**Diagnostic:**
```bash
# Search for catch blocks without re-throw in decorators:
grep -A 5 "catch" src/LoggingTextWriter.java
# Look for catches that log but don't re-throw
```

**Fix:**
```java
// BAD: silently swallows exception
try {
    wrapped.write(text);
} catch (Exception e) {
    log.error("Write failed", e); // swallowed!
}

// GOOD: log AND re-throw
try {
    wrapped.write(text);
} catch (Exception e) {
    log.error("Write failed", e);
    throw e;  // always propagate
}
```

**Prevention:** Decorators should not swallow exceptions unless explicitly designed as error-handling decorators with documented fallback behaviour.

---

**3. Decorator Applied in Wrong Order**

**Symptom:** Data is corrupted. Reading encrypted+compressed data fails with decompression errors.

**Root Cause:** Decrypt decorator wraps compress decorator, but data was written by encrypting the compressed bytes. Reading requires: decrypt first, then decompress - but the chain is constructed backwards.

**Diagnostic:**
```java
// Log each layer's input/output to verify data at each step:
@Override public byte[] read() {
    byte[] data = wrapped.read();
    log.debug("{}: received {} bytes, hex: {}",
        getClass().getSimpleName(), data.length,
        Hex.encode(data));
    byte[] result = processData(data);
    log.debug("{}: producing {} bytes, hex: {}",
        getClass().getSimpleName(), result.length,
        Hex.encode(result));
    return result;
}
```

**Fix:**
Document the correct construction order. Verify by comparing input and output data checksums at each decorator layer.

**Prevention:** Write an integration test that constructs the chain, writes a known payload, reads it back, and verifies exact round-trip equality. This test will fail immediately if the order is wrong.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Composition over Inheritance` - Decorator is the canonical application of composition over inheritance for extending behaviour; understanding WHY inheritance fails here drives correct design
- `Interface` - Decorator relies on the wrapped object and wrapper sharing an interface for transparent substitution
- `Polymorphism` - method dispatch through the interface allows the caller to be unaware of the decorator chain

**Builds On This (learn these next):**
- `Chain of Responsibility` - a sibling pattern where each handler in a chain decides whether to handle a request; similar chain structure to Decorator but for conditional handling
- `Proxy` - the structural cousin; shares the same-interface wrapping technique but for access control rather than behaviour addition
- `Aspect-Oriented Programming (AOP)` - Spring AOP and AspectJ generate Decorator proxies automatically; understanding manual Decorator makes AOP comprehensible

**Alternatives / Comparisons:**
- `Inheritance` - the pre-Decorator approach to extending behaviour; leads to combinatorial explosion with multiple orthogonal features
- `Proxy` - wraps same interface; controls access rather than adding behaviour; the distinction is intent and what is added
- `Bridge` - separates abstraction from implementation into two hierarchies; Decorator extends one hierarchy at runtime

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Wrapper that implements same interface,   │
│              │ adds behaviour, delegates to wrapped obj  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Subclassing for feature combinations      │
│ SOLVES       │ causes exponential class explosion        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Stacking decorators = function composition│
│              │ in OOP form - order matters               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple independent features need to be  │
│              │ combined in any subset/order at runtime   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Features are not independent (require     │
│              │ each other); or exactly one combination   │
│              │ is ever needed (just subclass)            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Runtime flexibility + zero class          │
│              │ explosion vs complex chain debugging      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wrap the object, same interface,         │
│              │  new behaviour without changing class."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Proxy → Chain of Responsibility →         │
│              │ Aspect-Oriented Programming               │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Add behaviour to objects dynamically by wrapping them in
decorator objects that delegate to the wrapped object and
add their layer of logic before or after the delegation.
Compose complex behaviour from simple interchangeable layers.

**Where else this pattern appears:**
- **HTTP middleware stacks (Express.js, ASP.NET Core):** Each
  middleware "wraps" the request/response pipeline -- logging
  middleware decorates the next handler, and authentication
  middleware decorates that, etc.
- **Java I/O streams:** `new BufferedReader(new InputStreamReader(
  new FileInputStream("file.txt")))` -- classic three-layer
  Decorator: buffering decorates encoding which decorates bytes.
- **React Higher-Order Components (HOC):** A HOC wraps a
  component and adds props or behaviour -- e.g.,
  `withAuth(MyComponent)` decorates MyComponent with auth logic.

---

### 💡 The Surprising Truth

Java's I/O stream API -- `InputStream`, `OutputStream`,
`Reader`, `Writer` -- is the most-used Decorator implementation
in all of Java, used by virtually every Java program that
reads or writes data. Yet surveys of Java developers show
that fewer than 30% recognize it as a Decorator pattern.
The GoF specifically cited Java's I/O streams as their primary
motivating example for Decorator in "Design Patterns" (1994),
making Java streams the pattern's canonical illustration
before Java was even widely adopted.
---

### 🧠 Think About This Before We Continue

**Q1.** Java's `java.util.Collections.synchronizedList(list)` is a Decorator that wraps any `List` to make it thread-safe. But the Javadoc says: "It is imperative that the user manually synchronize on the returned list when traversing it via Iterator." This means the synchronisation decorator is incomplete - iterators bypass it. Trace the exact mechanism by which an iterator on `synchronizedList` is NOT thread-safe despite the wrapper, and describe what the Decorator pattern would need to change to make iterators thread-safe.

*Hint: Look at the First Principles section for the core invariants, and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A team uses Decorators to implement HTTP request middleware: `AuthDecorator` → `RateLimitDecorator` → `LoggingDecorator` → `BaseHttpClient`. A new requirement: "if rate limiting blocks the request, the auth token should NOT be consumed." This means the `AuthDecorator` needs to know whether `RateLimitDecorator` blocked the request BEFORE the auth token is recorded as used. Describe whether this can be solved within the Decorator pattern, and if not, what design pattern better handles this conditional, cross-concern coordination.



*Hint: The Comparison Table and the Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A `PriceCalculator` decorator chain
is: `TaxDecorator(DiscountDecorator(ShippingDecorator(base)))`.
A customer reports the wrong final price. Describe a systematic
debugging strategy for identifying which decorator in the chain
is producing the wrong calculation, without modifying any
decorator's production code.

*Hint: The Failure Modes section shows the debugging challenge
of deep decorator chains. Think about how the decorator's
transparent interface design -- the very feature that makes
it powerful -- is also what makes debugging hard.*
