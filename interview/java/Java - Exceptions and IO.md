---
layout: default
title: "Java - Exceptions and IO"
parent: "Java"
grand_parent: "Interview Mastery"
nav_order: 3
permalink: /interview/java/exceptions-and-io/
topic: Java
subtopic: Exceptions and IO
keywords:
  - Exception Hierarchy
  - Checked vs Unchecked Exceptions
  - Try-with-Resources
  - IO Streams
  - NIO and NIO.2
difficulty_range: mixed
status: complete
version: 1
---

# Exception Hierarchy

**TL;DR** - Java's exception hierarchy splits into checked (compiler-enforced) and unchecked (runtime) exceptions rooted at Throwable, and knowing which to throw and catch prevents both swallowed errors and cluttered APIs.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Without a structured exception hierarchy, error handling is ad-hoc. Some methods return -1 for errors, others return null, others set a global error flag. Callers forget to check return values, errors propagate silently, and the program crashes hours later with no trace of what originally went wrong.

**THE BREAKING POINT:**
A payment system returns 0 for "no balance" and 0 for "account not found." The calling code treats both as zero balance, processes the payment against a non-existent account, and creates an orphan transaction that takes weeks to reconcile.

**THE INVENTION MOMENT:**
"This is exactly why Exception Hierarchy was created."

**EVOLUTION:**
C used error codes and `errno`. C++ introduced exceptions but without a forced hierarchy. Java (1.0) created a mandatory hierarchy rooted at `Throwable` with the checked/unchecked distinction, forcing compile-time awareness of recoverable errors. Kotlin, Scala, and modern Java frameworks have since moved away from checked exceptions, favoring unchecked exceptions with sealed hierarchies.

---

### Textbook Definition

Java's exception hierarchy is a class tree rooted at `Throwable`. `Error` (subclass of Throwable) represents unrecoverable JVM-level failures (e.g., `OutOfMemoryError`). `Exception` (subclass of Throwable) represents recoverable conditions. `RuntimeException` (subclass of Exception) and its subclasses are unchecked - not enforced by the compiler. All other Exception subclasses are checked - the compiler requires they be caught or declared in the method signature.

---

### Understand It in 30 Seconds

**One line:**
Java forces you to handle predictable failures at compile time and lets runtime bugs crash fast.

**One analogy:**

> Think of a hospital triage system. Checked exceptions are scheduled appointments - the system knows they're coming and has a plan. Unchecked exceptions are emergencies - they shouldn't happen in normal operation, but when they do, you escalate immediately.

**One insight:**
The checked/unchecked split answers one question: "Can the caller reasonably recover from this?" If yes (file not found, network timeout), make it checked - force the caller to have a plan. If no (null pointer, array out of bounds), make it unchecked - it's a bug, not a condition.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Every exception is a `Throwable` - the JVM only throws Throwable instances
2. `Error` = JVM is broken (don't catch), `Exception` = application-level (handle it)
3. Checked exceptions are enforced at compile time - catch or declare
4. Unchecked exceptions (RuntimeException) are programmer errors - fix the code, don't catch

**DERIVED DESIGN:**
The compiler enforcement of checked exceptions creates a contract: the method signature tells callers exactly what can go wrong. This is a form of documentation that the compiler verifies.

**THE TRADE-OFFS:**
**Gain:** Compile-time error awareness, forced handling of recoverable conditions
**Cost:** Verbose code (try-catch blocks), API pollution (throws clauses leak implementation details)

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Distinguishing "expected failures" from "bugs" is inherently necessary in any robust system.
**Accidental:** Java's checked exception mechanism forces handling at every call site, even when the only reasonable action is to propagate. This leads to anti-patterns like swallowing exceptions.

---

### Mental Model / Analogy

> Think of a building's safety system. Fire alarms (checked exceptions) are planned for - every floor has an evacuation route (catch block). Structural collapse (Error) means the building is done - no recovery plan, just evacuate. Someone tripping on their shoelaces (RuntimeException) is their own fault - fix the shoes, don't redesign the building.

- "Fire alarm" -> checked exception (IOException, SQLException)
- "Evacuation route" -> catch block with recovery logic
- "Structural collapse" -> Error (OutOfMemoryError, StackOverflowError)
- "Tripping on shoelaces" -> RuntimeException (NullPointerException)

Where this analogy breaks down: In real buildings, you can't prevent structural collapse at compile time.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When something goes wrong in a Java program, it throws an exception. Exceptions come in types organized in a family tree. Some types the compiler forces you to handle; others it doesn't. This hierarchy keeps programs from silently failing.

**Level 2 - How to use it (junior developer):**
Catch specific exceptions, never catch `Exception` or `Throwable` broadly. Always catch the most specific type first (subclass before superclass). For custom exceptions, extend `RuntimeException` for bugs or `Exception` for recoverable conditions. Always include a meaningful message and cause chain.

**Level 3 - How it works (mid-level engineer):**
Exception creation captures the call stack via `fillInStackTrace()`, which is the most expensive part (walks the entire thread stack). `throw` unwinds the stack searching for a matching `catch` block. Each stack frame is checked against the exception type hierarchy. If no catch is found, the thread's `UncaughtExceptionHandler` is invoked. `finally` blocks execute during stack unwinding regardless of exception type.

**Level 4 - Mastery (senior/staff+ engineer):**
Stack trace creation is the hidden performance cost. In hot paths, pre-allocating exception instances or overriding `fillInStackTrace()` to return `this` (skipping stack capture) can improve throughput dramatically. Libraries like Netty do this for flow control exceptions. The checked exception debate is largely settled in practice: modern Java APIs (Stream, CompletableFuture) avoid checked exceptions because they don't compose with lambdas. In architectures with global error handlers (Spring `@ControllerAdvice`), checked exceptions add ceremony without value - everything propagates to the handler anyway.

---

### How It Works

```
Exception Hierarchy:

  Throwable
  +-- Error (DON'T CATCH)
  |   +-- OutOfMemoryError
  |   +-- StackOverflowError
  |   +-- VirtualMachineError
  |
  +-- Exception
      +-- IOException        [CHECKED]
      |   +-- FileNotFoundException
      +-- SQLException       [CHECKED]
      +-- InterruptedException [CHECKED]
      |
      +-- RuntimeException   [UNCHECKED]
          +-- NullPointerException
          +-- IllegalArgumentException
          +-- IndexOutOfBoundsException
          +-- ClassCastException
          +-- UnsupportedOperationException
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
method() throws IOException
  -> risky operation fails
  -> new IOException("msg")
  -> fillInStackTrace()  <- expensive
  -> stack unwinding begins
  -> matching catch block found <- YOU ARE HERE
  -> recovery logic executes
  -> finally blocks run
  -> normal execution resumes
```

**FAILURE PATH:**

```
Exception thrown, no matching catch
  -> unwinds entire stack
  -> Thread.UncaughtExceptionHandler invoked
  -> Thread terminates
  -> If main thread: JVM exits
```

**WHAT CHANGES AT SCALE:**
In high-throughput systems (100K+ requests/sec), exception-driven flow control becomes a performance problem. Each exception captures a full stack trace - at 50+ frames deep in a Spring/microservice stack, this takes microseconds. At scale, use error codes or `Optional` for expected failures and reserve exceptions for truly exceptional conditions.

---

### Code Example

**Example 1 - Exception handling anti-patterns**

```java
// BAD: swallowing exceptions
try {
    processPayment(order);
} catch (Exception e) {
    // silently swallowed - order lost!
}

// BAD: catching too broadly
try {
    processPayment(order);
} catch (Exception e) {
    log.error("Failed", e);
    // catches NPE too - hides bugs
}

// GOOD: specific catch with recovery
try {
    processPayment(order);
} catch (PaymentDeclinedException e) {
    notifyCustomer(e.getReason());
    order.markDeclined();
} catch (PaymentGatewayException e) {
    log.warn("Gateway down, retrying", e);
    retryQueue.add(order);
}
```

**Example 2 - Custom exception hierarchy**

```java
// Base exception for the domain
public class OrderException
        extends RuntimeException {
    private final String orderId;

    public OrderException(String orderId,
            String message, Throwable cause) {
        super(message, cause);
        this.orderId = orderId;
    }

    public String getOrderId() {
        return orderId;
    }
}

// Specific subclass
public class InsufficientStockException
        extends OrderException {
    private final int requested, available;

    public InsufficientStockException(
            String orderId,
            int requested, int available) {
        super(orderId, String.format(
            "Requested %d but only %d available",
            requested, available), null);
        this.requested = requested;
        this.available = available;
    }
}
```

**How to test / verify correctness:**
Use `assertThrows()` in JUnit to verify the correct exception type is thrown, check the message and cause chain, and ensure no exceptions are silently swallowed by checking log output.

---

### Quick Recall

**If you remember only 3 things:**

1. Checked = compiler forces handling (recoverable conditions). Unchecked = bugs (fix the code)
2. Never catch `Exception` or `Throwable` broadly - catch the most specific type
3. Exception creation is expensive (stack trace capture) - don't use exceptions for flow control

**Interview one-liner:**
"Java's exception hierarchy splits at RuntimeException: checked exceptions force compile-time awareness of recoverable failures like I/O errors, while unchecked exceptions represent programming bugs that should be fixed, not caught. I design custom hierarchies as unchecked with domain context."

---

### The Surprising Truth

Creating an exception is 50-100x more expensive than a normal object because `fillInStackTrace()` must walk the entire thread call stack and create StackTraceElement objects for each frame. In a deep Spring Boot stack (60+ frames), this takes 5-10 microseconds per exception. Libraries like Netty override `fillInStackTrace()` to skip this for flow-control exceptions like `ChannelClosedException`, improving throughput by up to 30% in connection-heavy workloads.

---

### Interview Deep-Dive

**Q1: What's the difference between checked and unchecked exceptions? When would you use each?**

_Why they ask:_ Foundational understanding every Java developer must have.

**Answer:**
**Checked exceptions** (subclass of `Exception` but not `RuntimeException`) are enforced at compile time. The compiler requires callers to either catch them or declare them with `throws`. Examples: `IOException`, `SQLException`, `InterruptedException`.

**Unchecked exceptions** (subclass of `RuntimeException`) are not enforced at compile time. They represent programming errors that should be fixed in code, not caught. Examples: `NullPointerException`, `IllegalArgumentException`, `ArrayIndexOutOfBoundsException`.

**Decision framework:**

- Use checked when: the caller **can and should** recover (retry on network failure, prompt for different file, use fallback)
- Use unchecked when: it's a bug in the calling code (null argument, invalid state, violated precondition)
- In modern practice: most teams use unchecked for everything and handle cross-cutting concerns with a global error handler (Spring `@ControllerAdvice`, global exception filter)

The shift toward unchecked is driven by lambdas and streams, which don't support checked exceptions:

```java
// This won't compile with checked exception:
list.stream()
    .map(this::parseFile) // throws IOException
    .toList();
```

Key insight: checked exceptions were a noble experiment in compiler-enforced error handling. In practice, they cause more harm (swallowed exceptions, throws clause pollution) than good in large codebases.

---

**Q2: You're seeing `StackOverflowError` in production. How do you diagnose and fix it?**

_Why they ask:_ Tests ability to handle Error-level exceptions.

**Answer:**
`StackOverflowError` means the thread stack (default 512KB-1MB) is exhausted, usually from unbounded recursion.

**Diagnosis:**

1. **Read the stack trace:** Look for repeating frame patterns:

   ```
   at com.app.TreeWalker.visit(TreeWalker.java:42)
   at com.app.TreeWalker.visit(TreeWalker.java:42)
   at com.app.TreeWalker.visit(TreeWalker.java:42)
   ... 1024 more
   ```

   The repeating frames show the recursive method.

2. **Check the data:** What input causes deep recursion? A tree with 10K depth? A circular reference?

3. **Common causes:**
   - Recursive algorithm on deep data (tree traversal, graph walk)
   - Circular object references (`a.parent = b; b.parent = a;`)
   - Missing base case in recursion
   - toString()/hashCode() calling itself through circular refs

**Fixes:**

- Convert recursion to iteration with an explicit stack:

  ```java
  // BAD: recursive
  void visit(Node n) {
      process(n);
      for (Node c : n.children) visit(c);
  }

  // GOOD: iterative
  void visit(Node root) {
      Deque<Node> stack = new ArrayDeque<>();
      stack.push(root);
      while (!stack.isEmpty()) {
          Node n = stack.pop();
          process(n);
          for (Node c : n.children)
              stack.push(c);
      }
  }
  ```

- Increase stack size: `-Xss2m` (temporary fix)
- Add depth limit with cycle detection for graph traversal

Key insight: `StackOverflowError` is an `Error`, not an `Exception`. You generally shouldn't catch it, but in some frameworks (like recursive parsers) catching it at a top-level boundary with a graceful error response is acceptable.

---

**Q3: Explain the exception chaining mechanism and why it matters.**

_Why they ask:_ Tests understanding of production debugging support.

**Answer:**
Exception chaining preserves the original cause through layers of abstraction:

```java
try {
    jdbc.execute(sql);
} catch (SQLException e) {
    // Wrap low-level exception in domain exception
    throw new DataAccessException(
        "Failed to save order " + orderId, e);
    // The original SQLException is the "cause"
}
```

Without chaining, the `DataAccessException` would only say "failed to save order" - useless for debugging. With chaining, the full stack trace shows both the domain context AND the root cause:

```
com.app.DataAccessException: Failed to save order 123
  at OrderRepo.save(OrderRepo.java:42)
  ...
Caused by: java.sql.SQLException: Unique constraint
  violated on column EMAIL
  at oracle.jdbc.driver...(...)
  ...
```

**Rules:**

1. Always pass the original exception as the `cause` parameter
2. Never discard the cause: `throw new MyException(msg)` without cause = lost debugging info
3. Use `getCause()` or `initCause()` to access the chain
4. Log the full chain: `log.error("Failed", e)` - the `e` is crucial

Key insight: in microservice architectures, exception chains often cross service boundaries. Serialize the root cause message (not the full stack) into error responses so upstream services can log the original failure context.

---

**Q4: What's the performance impact of exceptions and how do you mitigate it in hot paths?**

_Why they ask:_ Tests production performance awareness.

**Answer:**
Exception cost breakdown:

1. **Creation:** `new Exception()` calls `fillInStackTrace()` which walks the thread stack. In a typical Spring Boot app with 60+ frames, this takes 5-10 microseconds.
2. **Throwing:** Stack unwinding checks each frame for matching catch blocks. Cost proportional to stack depth between throw and catch.
3. **Catching:** Minimal cost - just a branch.

**Mitigation strategies:**

1. **Don't use exceptions for flow control:**

   ```java
   // BAD: exception as control flow
   try {
       return Integer.parseInt(input);
   } catch (NumberFormatException e) {
       return defaultValue;
   }

   // GOOD: check first
   if (isNumeric(input)) {
       return Integer.parseInt(input);
   }
   return defaultValue;
   ```

2. **Pre-allocate exceptions for known cases:**

   ```java
   private static final MyException INSTANCE =
       new MyException("expected condition");

   // Override to skip stack trace
   @Override
   public Throwable fillInStackTrace() {
       return this;
   }
   ```

3. **Use Optional or Result types for expected failures:**
   ```java
   Optional<User> findUser(String email);
   // Instead of: User findUser(String email)
   //   throws UserNotFoundException;
   ```

At 100K+ requests/sec, exception-heavy code paths show up clearly in CPU profiles. A single unnecessary exception per request at 100K RPS = 100K stack trace captures per second.

---

**Q5: How does multi-catch work and what are its limitations?**

_Why they ask:_ Tests awareness of modern exception handling syntax.

**Answer:**
Multi-catch (Java 7) lets you catch multiple unrelated exception types in one block:

```java
try {
    processFile(path);
} catch (FileNotFoundException
       | PermissionDeniedException e) {
    log.warn("File access failed: {}", e.getMessage());
    return fallback();
}
```

**Rules and limitations:**

1. Exception types must be unrelated (not in the same inheritance chain). This won't compile:

   ```java
   // COMPILE ERROR: IOException is parent of
   // FileNotFoundException
   catch (IOException | FileNotFoundException e)
   ```

2. The variable `e` is effectively final - you can't reassign it:

   ```java
   catch (IOException | SQLException e) {
       e = new RuntimeException(); // ERROR
   }
   ```

3. The inferred type is the nearest common superclass. If catching `IOException | SQLException`, the type of `e` is `Exception` - but you can only call methods common to both types.

4. Rethrow is special - the compiler tracks which types can actually be thrown:
   ```java
   catch (IOException | SQLException e) {
       throw e; // compiler knows: throws IOException,
                // SQLException (not Exception)
   }
   ```

Multi-catch reduces code duplication when the handling logic is identical for different exception types.

---

---

# Checked vs Unchecked Exceptions

**TL;DR** - Checked exceptions force compile-time handling for recoverable failures while unchecked exceptions represent programming bugs, and choosing wrong clutters APIs or hides errors.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Without the distinction, every exception is the same. Callers can't tell whether a failure is something they should handle (network timeout) or something that indicates a bug (null pointer). APIs don't communicate what can go wrong, so callers either over-catch everything or under-catch and crash.

**THE BREAKING POINT:**
A team catches `Exception` everywhere because they can't distinguish recoverable from non-recoverable. When a `NullPointerException` is caught and logged instead of crashing, a data corruption bug runs for weeks before anyone notices.

**THE INVENTION MOMENT:**
"This is exactly why the Checked vs Unchecked distinction was created."

**EVOLUTION:**
Java was the first mainstream language to enforce checked exceptions at compile time (1995). C# deliberately omitted them after observing Java's pain points. Kotlin treats all exceptions as unchecked. Modern Java practice has shifted toward unchecked exceptions with global handlers, using checked exceptions only at system boundaries (I/O, network, database).

---

### Textbook Definition

Checked exceptions are subclasses of `Exception` (but not `RuntimeException`) that the Java compiler enforces handling for - callers must either catch them or declare them in their `throws` clause. Unchecked exceptions are subclasses of `RuntimeException` that the compiler does not enforce. The distinction encodes the designer's intent: checked = "this can reasonably fail and the caller should have a plan," unchecked = "this is a programming error."

---

### Understand It in 30 Seconds

**One line:**
Checked means "expect this to fail," unchecked means "you have a bug."

**One analogy:**

> Checked exceptions are like a mandatory safety briefing before a flight - the airline forces you to know where the exits are, even if you'll probably never need them. Unchecked exceptions are like running into a wall - it's your fault for not looking where you were going.

**One insight:**
The real question when designing an exception is: "Can the immediate caller do something useful about this?" If yes (retry, use fallback, prompt user), checked is appropriate. If the only option is to crash and log, unchecked is better - forcing empty catch blocks helps nobody.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Checked exceptions appear in method signatures - they're part of the API contract
2. Unchecked exceptions can be thrown from anywhere without declaration
3. The compiler prevents compiling code that ignores checked exceptions
4. Both checked and unchecked propagate identically at runtime

**DERIVED DESIGN:**
By making anticipated failures part of the method signature, the compiler forces every caller to make a conscious decision about error handling. The cost: verbose APIs and exception wrapping.

**THE TRADE-OFFS:**
**Gain:** Compile-time safety for recoverable failures, self-documenting APIs
**Cost:** Throws clause pollution, exception swallowing, incompatibility with lambdas/streams

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Some errors are genuinely recoverable and callers need to know about them.
**Accidental:** Java's implementation forces handling at every call layer, even when the only option is to propagate.

---

### Mental Model / Analogy

> Checked exceptions are like a contract clause saying "weather may delay delivery." You must acknowledge it and have a plan (accept delay, cancel order, use backup supplier). Unchecked exceptions are like the delivery truck catching fire - nobody planned for it because it shouldn't happen.

- "Contract clause" -> `throws` declaration
- "Acknowledge and plan" -> catch block with recovery
- "Truck fire" -> RuntimeException (bug)
- "Accept delay" -> retry logic
- "Cancel order" -> graceful degradation

Where this analogy breaks down: In software, unchecked exceptions happen far more frequently than truck fires.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java has two kinds of errors. Some (checked) the compiler forces you to handle - like mandatory insurance. Others (unchecked) are your own fault - like tripping over your own feet.

**Level 2 - How to use it (junior developer):**
When calling a method that throws checked exceptions, either catch them or add `throws` to your method. For custom exceptions: extend `RuntimeException` for precondition violations, extend `Exception` for recoverable external failures. Never catch `RuntimeException` broadly.

**Level 3 - How it works (mid-level engineer):**
The compiler checks every method call against the target's `throws` clause. If a checked exception isn't handled, compilation fails. At runtime, there's zero difference - both types propagate via the same stack unwinding mechanism. The `throws` clause is purely a compile-time contract.

**Level 4 - Mastery (senior/staff+ engineer):**
The checked exception experiment has produced clear patterns of misuse: swallowed exceptions (`catch (Exception e) {}`), throws clause pollution where `throws IOException` propagates through 10 layers, and exception wrapping hell. Modern best practice: use checked exceptions only at system boundaries (I/O layer, external integrations) and convert to unchecked at the boundary. Domain exceptions should be unchecked with rich context. Spring's entire data access layer follows this pattern - `SQLException` (checked) becomes `DataAccessException` (unchecked).

---

### How It Works

```
Compile-time enforcement:

  void readFile() throws IOException {
      //                    ^^^^^^^^
      // Compiler: "callers MUST handle this"
  }

  void caller() {
      readFile();
      // COMPILE ERROR: unreported IOException
  }

  void callerFixed() throws IOException {
      readFile(); // propagate
  }

  void callerFixed2() {
      try {
          readFile();
      } catch (IOException e) {
          handleError(e); // handle
      }
  }

  // Unchecked: no compile-time enforcement
  void validate(String s) {
      if (s == null)
          throw new IllegalArgumentException();
      // No throws clause needed
  }
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Library method: throws IOException
  -> Your method: catch or declare
     <- YOU ARE HERE (design decision)
  -> catch: recover locally
  -> declare: push decision to caller
  -> eventually: someone handles it
```

**FAILURE PATH:**

```
Checked exception swallowed:
  catch (IOException e) { /* empty */ }
  -> data silently lost
  -> symptoms appear hours/days later
  -> root cause untraceable
```

**WHAT CHANGES AT SCALE:**
In large codebases, checked exceptions create coupling: changing a low-level implementation detail (switching from file I/O to network I/O) changes the throws clause, which ripples through every caller. This is why frameworks like Spring wrap checked exceptions in unchecked ones at the boundary layer.

---

### Code Example

**Example 1 - The boundary pattern**

```java
// BAD: leaking checked exception through layers
public interface UserRepository {
    User findById(long id) throws SQLException;
    //                        ^^^^^^^^^^^^^^
    // Every caller must handle SQL details!
}

// GOOD: convert at boundary
public interface UserRepository {
    User findById(long id); // clean API
}

public class JdbcUserRepository
        implements UserRepository {
    public User findById(long id) {
        try {
            return jdbc.queryForObject(sql, id);
        } catch (SQLException e) {
            throw new DataAccessException(
                "User lookup failed: " + id, e);
            // Unchecked - callers don't need SQL
        }
    }
}
```

**Example 2 - Checked exceptions and lambdas**

```java
// BAD: checked exception breaks lambda
List<String> urls = List.of("http://a.com",
                            "http://b.com");
// Won't compile: map doesn't allow checked
urls.stream()
    .map(url -> new URL(url).openStream())
    .toList();

// GOOD: wrap in unchecked
urls.stream()
    .map(url -> {
        try {
            return new URL(url).openStream();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    })
    .toList();
```

**How to test / verify correctness:**
Test that checked exceptions are properly wrapped at boundaries (not swallowed), that unchecked exceptions contain the original cause chain, and that the appropriate exception type is thrown for each failure scenario.

---

### Quick Recall

**If you remember only 3 things:**

1. Checked = recoverable (I/O, network, parsing). Unchecked = bugs (null, invalid args, bad state)
2. Convert checked to unchecked at boundaries - don't let SQL/IO details leak through your API
3. Checked exceptions don't work with lambdas/streams - another reason to use unchecked in modern Java

**Interview one-liner:**
"I treat checked exceptions as boundary-layer contracts for external I/O failures and convert them to rich unchecked domain exceptions at the adapter boundary. This keeps domain APIs clean and compatible with streams and lambdas."

---

### The Surprising Truth

Java's checked exception mechanism was so controversial that the architects of C# (including Anders Hejlsberg, who also designed Turbo Pascal and Delphi) specifically studied Java's experience and decided to omit checked exceptions from C#. Their conclusion: checked exceptions work well for small programs but create significant maintenance burden in large systems because throws clauses become part of the public API contract, making internal implementation changes a breaking change.

---

### Interview Deep-Dive

**Q1: Your team is debating whether a new custom exception should be checked or unchecked. What's your decision framework?**

_Why they ask:_ Tests design thinking about exception strategy.

**Answer:**
I use three criteria:

1. **Can the immediate caller recover?**
   - Yes: checked (retry, fallback, prompt)
   - No: unchecked (log and propagate)

2. **Is it caused by the caller's mistake?**
   - Yes (null arg, invalid state): unchecked (`IllegalArgumentException`)
   - No (external failure): potentially checked

3. **Where in the architecture does it occur?**
   - System boundary (I/O, network, DB): checked may be appropriate
   - Business logic: unchecked (domain exceptions)
   - Framework/library: unchecked (don't burden consumers)

In practice, I default to unchecked for most custom exceptions and only use checked exceptions at the outermost integration layer (where a developer integrating an SDK genuinely needs to handle the failure). Modern Java codebases trend heavily toward unchecked.

```java
// Domain exception - always unchecked
public class InsufficientFundsException
        extends RuntimeException {
    // Rich context, not compiler burden
}

// SDK exception - checked is defensible
public class PaymentGatewayException
        extends Exception {
    // External system, caller MUST have a plan
}
```

---

**Q2: How does Spring convert checked exceptions to unchecked? Why?**

_Why they ask:_ Tests framework knowledge and pattern understanding.

**Answer:**
Spring wraps all data access checked exceptions (`SQLException`, `HibernateException`) into its unchecked `DataAccessException` hierarchy:

```
DataAccessException (RuntimeException)
+-- DuplicateKeyException
+-- DataIntegrityViolationException
+-- CannotAcquireLockException
+-- DeadlockLoserDataAccessException
```

The mechanism is `SQLExceptionTranslator`: it maps vendor-specific SQL error codes to Spring exception types. For example, Oracle error `ORA-00001` (unique constraint) maps to `DuplicateKeyException`.

**Why Spring does this:**

1. **Decoupling:** Service layer doesn't need to know whether data access uses JDBC, Hibernate, or MongoDB - all throw the same `DataAccessException` subclasses
2. **Lambda compatibility:** Service methods can use streams without try-catch pollution
3. **Practical reality:** Most `SQLException` instances can't be recovered at the service layer - they should propagate to a global handler

This pattern is reusable: at any system boundary (REST client, message queue, file system), wrap implementation-specific checked exceptions into your domain's unchecked hierarchy.

---

**Q3: What happens when a checked exception is thrown from a method that doesn't declare it?**

_Why they ask:_ Tests deep language knowledge.

**Answer:**
Normally, the compiler prevents this. But there are ways to circumvent the check:

1. **Reflection:** `Method.invoke()` wraps all exceptions in `InvocationTargetException` (unchecked)

2. **Unsafe/bytecode manipulation:** `sun.misc.Unsafe.throwException()` or bytecode libraries can throw checked exceptions without declaration

3. **Generics type erasure trick (sneaky throw):**

   ```java
   @SuppressWarnings("unchecked")
   static <T extends Throwable> void sneakyThrow(
           Throwable t) throws T {
       throw (T) t; // unchecked cast
   }

   // Usage: throws IOException without declaring it
   sneakyThrow(new IOException("surprise"));
   ```

   This works because generics are erased at runtime. The JVM doesn't enforce checked exceptions - only `javac` does.

4. **Lombok's `@SneakyThrows`:** Uses this exact trick to let you throw checked exceptions from methods that don't declare them.

Key insight: checked exception enforcement is purely a compiler feature. The JVM has no concept of checked vs unchecked - at the bytecode level, any `Throwable` can be thrown from any method.

---

**Q4: How would you design an exception handling strategy for a microservices application?**

_Why they ask:_ Tests architecture-level thinking.

**Answer:**
Layered strategy with clean boundaries:

1. **Domain layer:** Unchecked domain exceptions with business context:

   ```java
   throw new OrderNotFoundException(orderId);
   throw new InsufficientInventoryException(
       sku, requested, available);
   ```

2. **Infrastructure layer:** Convert external exceptions at the boundary:

   ```java
   catch (SQLException e) {
       throw new DataAccessException(
           "Order save failed", e);
   }
   ```

3. **API layer:** Global exception handler maps to HTTP responses:

   ```java
   @ControllerAdvice
   class GlobalHandler {
       @ExceptionHandler(OrderNotFoundException.class)
       ResponseEntity<?> handle(
               OrderNotFoundException e) {
           return ResponseEntity.status(404)
               .body(new ErrorResponse(
                   "ORDER_NOT_FOUND",
                   e.getMessage()));
       }

       @ExceptionHandler(DataAccessException.class)
       ResponseEntity<?> handle(
               DataAccessException e) {
           log.error("Data access failure", e);
           return ResponseEntity.status(503)
               .body(new ErrorResponse(
                   "SERVICE_UNAVAILABLE",
                   "Please retry"));
       }
   }
   ```

4. **Cross-service:** Include correlation IDs in error responses for tracing. Never expose internal exceptions to external callers - map to error codes.

5. **Monitoring:** Alert on exception rates per type. Sudden spikes in `DataAccessException` = database issue. Spike in `OrderNotFoundException` = possible data inconsistency or bad client.

---

**Q5: A developer on your team catches Exception everywhere "just to be safe." How do you coach them?**

_Why they ask:_ Tests mentoring and code quality judgment.

**Answer:**
I'd explain the three dangers of broad catch:

1. **Hides bugs:** Catching `Exception` catches `NullPointerException`, `ClassCastException`, and every RuntimeException. These are bugs that should crash fast, not be logged and forgotten.

2. **Prevents recovery:** Different exceptions need different handling. A `TimeoutException` should trigger retry. A `ValidationException` should return 400. Catching `Exception` treats them all the same.

3. **Makes debugging harder:** When the system misbehaves weeks later, you can't trace the original exception because it was caught, logged among thousands of other warnings, and execution continued in a corrupted state.

**The coaching approach:**

- Show a real example where a caught NPE caused data corruption
- Teach the rule: catch the most specific type you can recover from
- Introduce the pattern: let unchecked exceptions propagate to a global handler
- If they truly need a catch-all (top-level loop), use:
  ```java
  catch (Exception e) {
      log.error("Unexpected error processing "
          + item, e);
      metrics.increment("unexpected.errors");
      // Don't swallow - re-throw or fail the item
      throw e;
  }
  ```

Key insight: the instinct to "catch everything" comes from fear of crashes. The fix is confidence in the global error handler - once it exists, developers relax about uncaught exceptions.

---

---

# Try-with-Resources

**TL;DR** - Try-with-resources guarantees that AutoCloseable resources are closed even when exceptions occur, eliminating the most common source of resource leaks in Java.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Closing resources in `finally` blocks requires nested try-catch inside finally, null checks, and careful ordering. A database connection opened before a statement must be closed after the statement, but if closing the statement throws, the connection leaks. Real production code had 15+ lines of boilerplate for two resources.

**THE BREAKING POINT:**
A connection pool exhausts because developers occasionally forget `finally` blocks or misorder close calls. Under load, the application stops serving requests. The fix requires auditing hundreds of files for resource leak patterns.

**THE INVENTION MOMENT:**
"This is exactly why Try-with-Resources was created."

**EVOLUTION:**
Pre-Java 7: manual `finally` blocks. Java 7 introduced try-with-resources and the `AutoCloseable` interface. Java 9 enhanced it to allow effectively-final variables declared outside the try block. The pattern has become the standard for all resource management in modern Java.

---

### Textbook Definition

Try-with-resources (Java 7+) is a statement that declares one or more resources in the try header. Resources must implement `AutoCloseable`. The compiler generates code to call `close()` on each resource in reverse declaration order when the try block exits, whether normally or via exception. If both the try body and `close()` throw, the body's exception is primary and the close exception is added as a suppressed exception.

---

### Understand It in 30 Seconds

**One line:**
Declare resources in the try header and Java guarantees they're closed no matter what.

**One analogy:**

> Think of a hotel checkout system. When you check in (try header), the hotel guarantees it will process your checkout (close) whether you leave normally or are carried out on a stretcher (exception). Multiple rooms are checked out in reverse order.

**One insight:**
The real insight is suppressed exceptions. Before Java 7, if `close()` threw, it masked the original exception from the try body - you'd debug the wrong problem. Try-with-resources preserves both: the body exception is primary, the close exception is suppressed and accessible via `getSuppressed()`.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Resources declared in try header are always closed (guaranteed by compiler)
2. Close order is reverse of declaration order
3. If both try body and close throw, body's exception wins (close exception is suppressed)
4. Resources must implement `AutoCloseable`

**DERIVED DESIGN:**
The compiler generates a finally block with null checks and suppressed exception handling. This is 15+ lines of boilerplate that every developer would have to write correctly - automating it eliminates an entire class of bugs.

**THE TRADE-OFFS:**
**Gain:** Guaranteed resource cleanup, correct exception handling, dramatically less boilerplate
**Cost:** Resources must implement AutoCloseable, slight learning curve for suppressed exceptions

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Resources must be released regardless of success or failure - this is inherent.
**Accidental:** Pre-Java 7, the accidental complexity was enormous - 15 lines of boilerplate per resource.

---

### Mental Model / Analogy

> Think of a self-closing door. You walk through (try body), and whether you walk out normally or run out in a panic (exception), the door closes itself behind you. If you're carrying boxes through multiple doors, they all close in reverse order.

- "Self-closing door" -> AutoCloseable resource in try header
- "Walk through" -> execute try body
- "Door closes itself" -> `close()` called automatically
- "Multiple doors" -> multiple resources, closed in reverse
- "Door jams while you're falling" -> suppressed exception

Where this analogy breaks down: Doors don't suppress their own errors when you're already having an emergency.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A special try statement where you declare resources (files, connections, etc.) that Java automatically closes when you're done, even if something goes wrong.

**Level 2 - How to use it (junior developer):**
Put resource declarations in the try parentheses. They're automatically closed when the block exits. Multiple resources are separated by semicolons. Always use this instead of manual finally blocks. Works with `Connection`, `InputStream`, `BufferedReader`, and any `AutoCloseable`.

**Level 3 - How it works (mid-level engineer):**
The compiler desugars try-with-resources into a try-finally with null checks and suppressed exception handling. Each resource's `close()` is called in reverse declaration order. If the try body throws ExA and close() throws ExB, ExA is the thrown exception and ExB is added via `ExA.addSuppressed(ExB)`. Access suppressed exceptions via `ex.getSuppressed()`.

**Level 4 - Mastery (senior/staff+ engineer):**
Java 9 allows effectively-final variables in try-with-resources: `try (conn)` instead of redeclaring. Custom `AutoCloseable` implementations should be idempotent - `close()` should be safe to call multiple times. In resource hierarchies (BufferedReader wrapping FileReader), closing the outer resource closes the inner one - don't close both explicitly or you risk double-close issues. For pooled resources (connection pools), `close()` returns to pool rather than destroying - this is why `DataSource.getConnection()` works with try-with-resources even though you're not destroying the connection.

---

### How It Works

```
What you write:
  try (InputStream in = new FileInputStream(f);
       BufferedReader br = new BufferedReader(
           new InputStreamReader(in))) {
      return br.readLine();
  }

What the compiler generates (simplified):
  InputStream in = new FileInputStream(f);
  Throwable primary = null;
  try {
      BufferedReader br = new BufferedReader(
          new InputStreamReader(in));
      try {
          return br.readLine();
      } catch (Throwable t) {
          primary = t;
          throw t;
      } finally {
          if (primary != null) {
              try { br.close(); }
              catch (Throwable t) {
                  primary.addSuppressed(t);
              }
          } else {
              br.close();
          }
      }
  } finally {
      // same pattern for 'in'
  }
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
try (resource1; resource2)  <- declare
  -> execute body           <- YOU ARE HERE
  -> close resource2 (reverse order)
  -> close resource1
  -> return result
```

**FAILURE PATH:**

```
try body throws ExA
  -> close resource2 throws ExB
  -> ExA.addSuppressed(ExB)
  -> close resource1 (still executes)
  -> ExA is thrown (with ExB suppressed)
```

**WHAT CHANGES AT SCALE:**
In high-throughput systems, resource leaks are the #1 cause of gradual degradation. Try-with-resources eliminates this class entirely. At scale, the pattern extends to custom AutoCloseable wrappers for connection pools, thread pools, and distributed locks.

---

### Code Example

**Example 1 - Manual vs automatic**

```java
// BAD: manual finally (error-prone)
Connection conn = null;
PreparedStatement stmt = null;
try {
    conn = dataSource.getConnection();
    stmt = conn.prepareStatement(sql);
    stmt.executeUpdate();
} finally {
    if (stmt != null) {
        try { stmt.close(); }
        catch (SQLException e) { /* swallowed! */ }
    }
    if (conn != null) {
        try { conn.close(); }
        catch (SQLException e) { /* swallowed! */ }
    }
}

// GOOD: try-with-resources
try (Connection conn = dataSource.getConnection();
     PreparedStatement stmt =
         conn.prepareStatement(sql)) {
    stmt.executeUpdate();
}
// Both closed automatically, exceptions preserved
```

**Example 2 - Custom AutoCloseable**

```java
public class DistributedLock
        implements AutoCloseable {
    private final String lockKey;
    private final RedisClient redis;

    public DistributedLock(RedisClient redis,
            String key, Duration ttl) {
        this.redis = redis;
        this.lockKey = key;
        redis.set(key, "locked", ttl);
    }

    @Override
    public void close() {
        redis.del(lockKey);
    }
}

// Usage: lock auto-released on exit
try (var lock = new DistributedLock(
        redis, "order:" + id, Duration.ofSeconds(30))) {
    processOrder(id);
}
// Lock released even if processOrder throws
```

**How to test / verify correctness:**
Create a mock `AutoCloseable` that records `close()` calls. Verify it's called even when exceptions occur. Check `getSuppressed()` when both body and close throw.

---

### Quick Recall

**If you remember only 3 things:**

1. Resources in try header are always closed in reverse order - guaranteed by the compiler
2. Body exception wins over close exception - close exception becomes suppressed
3. Use this for ALL resources (connections, streams, locks) - never manual finally

**Interview one-liner:**
"Try-with-resources guarantees AutoCloseable resources are closed in reverse declaration order, even when exceptions occur. If both the try body and close() throw, the body exception is primary and the close exception is added as suppressed."

---

### The Surprising Truth

Before Java 7, the official Sun/Oracle examples for JDBC code had resource leak bugs. The correct manual pattern requires nested try-finally blocks with null checks and exception handling - roughly 20 lines of boilerplate per pair of resources. Studies of open-source Java projects found that over 60% of resource management code had potential leaks. Try-with-resources didn't just reduce boilerplate - it eliminated an entire category of production defects.

---

### Interview Deep-Dive

**Q1: What are suppressed exceptions and how do you access them?**

_Why they ask:_ Tests understanding beyond basic usage.

**Answer:**
Suppressed exceptions handle the case where both the try body AND `close()` throw. Without suppression, one exception would mask the other - you'd lose critical debugging information.

```java
try (var res = new MyResource()) {
    throw new RuntimeException("body error");
} // close() throws IOException

// Result: RuntimeException is thrown
// IOException is suppressed

catch (RuntimeException e) {
    System.out.println(e.getMessage());
    // "body error"

    Throwable[] suppressed = e.getSuppressed();
    // suppressed[0] = IOException from close()
}
```

The body exception takes priority because it's typically the root cause. The close exception is a secondary effect.

In production logging:

```java
catch (Exception e) {
    log.error("Primary failure", e);
    for (Throwable s : e.getSuppressed()) {
        log.warn("Suppressed during cleanup", s);
    }
}
```

Key insight: before Java 7, if both `readFile()` and `close()` threw, the close exception would replace the read exception in a finally block - you'd spend hours debugging a "stream closed" error when the real problem was a corrupted file.

---

**Q2: Can you use try-with-resources with a resource declared outside the try block?**

_Why they ask:_ Tests Java 9 enhancement knowledge.

**Answer:**
Yes, Java 9 added support for effectively-final variables:

```java
// Java 7-8: must declare in try header
Connection conn = dataSource.getConnection();
try (Connection c = conn) { // redeclare
    c.prepareStatement(sql);
}

// Java 9+: use effectively-final variable directly
Connection conn = dataSource.getConnection();
try (conn) { // same variable
    conn.prepareStatement(sql);
}
```

The variable must be effectively final - you can't reassign it between declaration and the try block:

```java
Connection conn = dataSource.getConnection();
conn = anotherDataSource.getConnection(); // reassign
try (conn) { } // COMPILE ERROR: not effectively final
```

This is particularly useful when:

- Resource is created by a factory method that returns a specific type
- Resource needs configuration between creation and use
- Resource is passed as a parameter

---

**Q3: What happens if close() is called multiple times on a resource?**

_Why they ask:_ Tests understanding of the idempotent close contract.

**Answer:**
The `AutoCloseable` javadoc states that `close()` should be idempotent - calling it multiple times should have no additional effect. However, this is not enforced - implementations may throw on double-close.

**Implementations that handle double-close:**

- `BufferedReader.close()`: sets a flag, subsequent calls are no-ops
- JDBC `Connection.close()` from a pool: returns to pool first time, no-op after
- `InputStream.close()`: generally safe

**Implementations that may throw:**

- Some third-party resources that don't follow the contract
- Resources wrapping native handles (file descriptors)

This matters with resource hierarchies:

```java
// DANGER: closing both inner and outer
try (FileReader fr = new FileReader(path);
     BufferedReader br = new BufferedReader(fr)) {
    // br.close() will close fr internally
    // then try-with-resources closes fr again
}
// fr.close() called twice!
// Usually safe (FileReader handles it)
// but not guaranteed for all implementations
```

Best practice: only close the outermost wrapper:

```java
try (BufferedReader br = new BufferedReader(
         new FileReader(path))) {
    // br.close() handles FileReader.close()
}
```

---

**Q4: How does try-with-resources interact with connection pools?**

_Why they ask:_ Tests production knowledge.

**Answer:**
Connection pools (HikariCP, C3P0) return proxy Connection objects from `getConnection()`. The proxy's `close()` method returns the connection to the pool instead of destroying it:

```java
// This does NOT destroy the connection
try (Connection conn =
         dataSource.getConnection()) {
    // conn is a pool proxy
    PreparedStatement stmt =
        conn.prepareStatement(sql);
    stmt.executeUpdate();
}
// conn.close() returns to pool, not destroyed
```

This is why try-with-resources works perfectly with pools - `close()` is repurposed to mean "I'm done with this resource."

The pool typically:

1. Marks the connection as available
2. Resets connection state (auto-commit, isolation level)
3. Validates the connection (optional ping)
4. If unhealthy, destroys and creates a new one

Gotcha: if you forget try-with-resources, the connection is never returned to the pool. Under load, all connections are checked out and new requests block. HikariCP's `leakDetectionThreshold` setting logs a warning with the stack trace of where the connection was checked out - essential for finding leaks.

---

**Q5: Write a custom AutoCloseable that manages a temporary directory and cleans it up automatically.**

_Why they ask:_ Tests ability to apply the pattern creatively.

**Answer:**

```java
public class TempDirectory
        implements AutoCloseable {
    private final Path dir;

    public TempDirectory(String prefix)
            throws IOException {
        this.dir = Files.createTempDirectory(prefix);
    }

    public Path getPath() { return dir; }

    public Path createFile(String name)
            throws IOException {
        return Files.createFile(dir.resolve(name));
    }

    @Override
    public void close() throws IOException {
        // Walk in reverse depth order to delete
        // files before directories
        try (var walk = Files.walk(dir)) {
            walk.sorted(Comparator.reverseOrder())
                .forEach(path -> {
                    try {
                        Files.deleteIfExists(path);
                    } catch (IOException e) {
                        // Log but don't fail
                        // cleanup is best-effort
                    }
                });
        }
    }
}

// Usage
try (var tmp = new TempDirectory("build")) {
    Path config = tmp.createFile("config.xml");
    Files.writeString(config, xmlContent);
    runBuild(tmp.getPath());
}
// Directory and all contents cleaned up
```

Key design decisions:

- `close()` deletes in reverse depth order (files before directories)
- Individual file delete failures are logged but don't prevent cleaning other files
- `Files.walk()` is itself AutoCloseable - nested try-with-resources

---

---

# IO Streams

**TL;DR** - Java's IO stream model uses decorator-chained byte streams (InputStream/OutputStream) and character streams (Reader/Writer), and understanding the decorator pattern prevents the most common IO performance mistake: unbuffered reading.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Without a unified IO abstraction, reading from a file uses one API, reading from a network socket uses another, and reading from memory uses a third. Your code is tightly coupled to the data source. Switching from file to network requires rewriting all IO logic.

**THE BREAKING POINT:**
A data pipeline hardcodes `FileInputStream` throughout. When the team needs to read from S3 instead, they must modify every file-reading class. Testing requires creating actual files on disk because there's no way to inject a mock data source.

**THE INVENTION MOMENT:**
"This is exactly why IO Streams were created."

**EVOLUTION:**
Java 1.0 introduced `InputStream`/`OutputStream` (bytes) and `Reader`/`Writer` (characters). Java 1.1 added `BufferedReader`/`BufferedWriter`. Java 4 introduced NIO with channels and buffers for non-blocking I/O. Java 7 added NIO.2 with `Files` utility class and `Path`. Java 8+ added `Files.lines()` returning a Stream for lazy file processing.

---

### Textbook Definition

Java IO streams are sequential, ordered sequences of data elements. Byte streams (`InputStream`/`OutputStream`) handle raw bytes. Character streams (`Reader`/`Writer`) handle Unicode characters with encoding conversion. Both families use the Decorator pattern: concrete streams wrap other streams to add behavior (buffering, compression, encryption) without modifying the underlying source. This composition model provides a uniform API across diverse data sources.

---

### Understand It in 30 Seconds

**One line:**
Streams are pipes that move data byte-by-byte or char-by-char from a source to a destination.

**One analogy:**

> Think of a water pipe system. The source (faucet) connects through pipes that can add features: a filter pipe (InputStreamReader for encoding), a tank pipe (BufferedInputStream for batching), a pressure gauge pipe (CountingInputStream for metrics). You stack pipes however you need.

**One insight:**
The #1 performance mistake in Java IO is forgetting to buffer. `FileInputStream.read()` makes one OS system call per byte. Wrapping in `BufferedInputStream` batches reads into 8KB chunks, easily giving 100x throughput improvement.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Streams are sequential - you read/write in order, no random access (use `RandomAccessFile` for that)
2. Byte streams handle raw bytes; character streams handle encoded text
3. Decorators compose: `new BufferedReader(new InputStreamReader(new FileInputStream(f), "UTF-8"))`
4. Streams must be closed to release OS resources

**DERIVED DESIGN:**
The Decorator pattern allows combining behaviors. Need buffered, compressed, encrypted file reading? Chain the decorators. Each decorator has the same interface as the base stream.

**THE TRADE-OFFS:**
**Gain:** Source-agnostic code, composable behaviors, uniform API
**Cost:** Verbose constructor chains, sequential-only access, blocking by default

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Data comes from diverse sources - abstraction is necessary.
**Accidental:** The byte-stream/character-stream split and manual decorator chaining is verbose. NIO.2's `Files.readString()` and `Files.lines()` reduce this significantly.

---

### Mental Model / Analogy

> Think of an assembly line in a factory. Raw materials (bytes) enter one end and pass through stations (decorators). Each station adds something: one converts materials to products (InputStreamReader), another batches items for efficiency (BufferedReader), another counts items (monitoring). The factory owner doesn't care where raw materials come from - file, network, or another factory.

- "Raw materials" -> bytes from InputStream
- "Station converting to products" -> InputStreamReader (bytes to chars)
- "Batching station" -> BufferedReader (read-ahead buffer)
- "Factory owner" -> your code, source-agnostic

Where this analogy breaks down: Assembly lines process items in parallel; Java IO streams are strictly sequential.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java IO streams are pipes that move data from one place to another. Byte streams handle raw data. Character streams handle text. You can chain multiple streams together to add features like buffering or encoding.

**Level 2 - How to use it (junior developer):**
For reading text files, use `Files.readString(path)` (small files) or `Files.lines(path)` (large files, lazy). For writing, use `Files.writeString(path, content)`. Always use try-with-resources. Always specify charset explicitly: `StandardCharsets.UTF_8`. For custom IO, chain: `new BufferedReader(new InputStreamReader(stream, UTF_8))`.

**Level 3 - How it works (mid-level engineer):**
`InputStream.read()` is a native method that makes a system call. Without buffering, each `read()` crosses the user-kernel boundary. `BufferedInputStream` allocates an 8192-byte internal array, fills it with one system call, and serves subsequent reads from memory. `InputStreamReader` uses a `StreamDecoder` that converts bytes to chars using the specified `Charset`. The `Charset` maintains state for multi-byte encodings (UTF-8 can be 1-4 bytes per character).

**Level 4 - Mastery (senior/staff+ engineer):**
The classic IO model is blocking and thread-per-connection. For high-connection-count servers (10K+ connections), NIO with `Selector` multiplexes many connections on few threads. However, for most file IO and moderate-connection-count applications, blocking IO with virtual threads (Java 21+) is simpler and performs comparably. `Files.lines()` returns a lazy Stream that reads on demand - process a 100GB file with constant memory. `MappedByteBuffer` via `FileChannel.map()` memory-maps files for random access at near-memory speed.

---

### How It Works

```
Decorator chain for reading a UTF-8 text file:

  FileInputStream
    reads raw bytes from OS file descriptor
         |
  BufferedInputStream
    batches reads into 8KB chunks
         |
  InputStreamReader (UTF-8)
    converts byte sequences to chars
         |
  BufferedReader
    adds readLine() and char buffering
         |
  Your code: br.readLine()

  Modern equivalent:
  Files.newBufferedReader(path, UTF_8)
  // Creates the entire chain in one call
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Files.lines(path)
  -> FileChannel opens file descriptor
  -> BufferedReader created <- YOU ARE HERE
  -> readLine() reads from buffer
  -> buffer empty? -> OS read() fills 8KB
  -> stream.forEach(this::process)
  -> close() releases file descriptor
```

**FAILURE PATH:**

```
Stream not closed (no try-with-resources)
  -> file descriptor leaked
  -> OS limit reached (ulimit)
  -> "Too many open files" IOException
  -> New connections/files fail
```

**WHAT CHANGES AT SCALE:**
For files > 1GB, `Files.readAllBytes()` causes OutOfMemoryError - use streaming (`Files.lines()` or buffered reading). For 10K+ concurrent connections, blocking IO exhausts thread pools - use NIO or virtual threads. For random access to large files, `MappedByteBuffer` avoids read/write system calls entirely.

---

### Code Example

**Example 1 - Buffering matters**

```java
// BAD: unbuffered - 1 system call per byte
try (InputStream in =
         new FileInputStream("data.bin")) {
    int b;
    while ((b = in.read()) != -1) {
        process(b); // ~1M syscalls for 1MB file
    }
}

// GOOD: buffered - 1 syscall per 8KB
try (InputStream in = new BufferedInputStream(
         new FileInputStream("data.bin"))) {
    int b;
    while ((b = in.read()) != -1) {
        process(b); // ~125 syscalls for 1MB file
    }
}

// BEST: modern API
try (var lines = Files.lines(Path.of("data.txt"),
         StandardCharsets.UTF_8)) {
    lines.filter(l -> !l.isBlank())
         .map(String::trim)
         .forEach(this::process);
}
```

**Example 2 - Writing with proper encoding**

```java
// BAD: platform-dependent encoding
try (FileWriter fw = new FileWriter("out.txt")) {
    fw.write("Hello");
    // Uses system default encoding!
}

// GOOD: explicit UTF-8
try (BufferedWriter bw = Files.newBufferedWriter(
         Path.of("out.txt"),
         StandardCharsets.UTF_8)) {
    bw.write("Hello");
}
```

**How to test / verify correctness:**
Use `ByteArrayInputStream`/`ByteArrayOutputStream` for unit tests - no real files needed. Verify encoding by reading back with explicit charset and comparing. Test resource cleanup with `AutoCloseable` mocks.

---

### Quick Recall

**If you remember only 3 things:**

1. Always buffer IO - unbuffered `FileInputStream.read()` makes a system call per byte (100x slower)
2. Always specify charset explicitly - `StandardCharsets.UTF_8` prevents platform-dependent encoding bugs
3. Always use try-with-resources - leaked file descriptors cause "Too many open files" under load

**Interview one-liner:**
"Java IO uses the Decorator pattern: byte streams handle raw data, character streams handle encoded text, and decorators like BufferedReader compose for buffered, encoded reading. The key performance rule is always buffer - the difference between buffered and unbuffered file reading is 100x."

---

### The Surprising Truth

`FileWriter` and `FileReader` use the platform's default encoding, which varies by OS and locale. A file written with `FileWriter` on a Windows machine (Windows-1252) becomes garbled when read on a Linux server (UTF-8). This is why `FileWriter` and `FileReader` are effectively deprecated in practice - always use `Files.newBufferedWriter(path, StandardCharsets.UTF_8)` or `OutputStreamWriter` with an explicit charset.

---

### Interview Deep-Dive

**Q1: What is the difference between byte streams and character streams? When do you use each?**

_Why they ask:_ Tests fundamental IO understanding.

**Answer:**
**Byte streams** (`InputStream`/`OutputStream`) handle raw binary data. Each `read()` returns one byte (0-255). Use for: binary files (images, PDFs), network protocols, serialized objects, any non-text data.

**Character streams** (`Reader`/`Writer`) handle text with charset encoding. Each `read()` returns one char (Unicode). Use for: text files, config files, CSV, JSON, log files.

The bridge between them is `InputStreamReader` and `OutputStreamWriter`, which wrap a byte stream and apply a charset decoder/encoder.

Critical rule: never use byte streams to read text (you'll get encoding bugs) and never use character streams for binary data (you'll get corruption).

```java
// Binary data: byte streams
try (InputStream in =
         new FileInputStream("image.png")) {
    byte[] data = in.readAllBytes();
}

// Text data: character streams (modern API)
String text = Files.readString(
    Path.of("config.json"), UTF_8);
```

---

**Q2: A team reports their file processing is extremely slow. The file is 500MB. What do you investigate?**

_Why they ask:_ Tests performance diagnosis ability.

**Answer:**
Common causes for slow file IO, in order of likelihood:

1. **Unbuffered reading:** Check if they're using raw `FileInputStream` without `BufferedInputStream`. Fix: wrap in buffer or use `Files.newBufferedReader()`.

2. **Reading entire file into memory:** `Files.readAllBytes()` on 500MB allocates a 500MB byte array. Fix: use streaming (`Files.lines()` or buffered line-by-line reading).

3. **Wrong encoding handling:** `InputStreamReader` with a complex charset (UTF-16) decodes every byte pair. Usually not a bottleneck but can add 10-20% overhead.

4. **Sync IO from many threads:** Multiple threads reading the same file or different files on the same disk. SSDs handle this well; HDDs serialize randomly.

5. **Processing bottleneck masquerading as IO:** The actual `read()` is fast but `process(line)` does heavy computation or database calls.

Diagnosis:

```bash
# Check if process is IO-bound or CPU-bound
iostat -x 1
# High %util + low CPU = IO bound
# Low %util + high CPU = processing bound

# Java-specific: async-profiler with IO events
./profiler.sh -e wall -d 30 -f out.html <pid>
```

Quick benchmark for 500MB file:

- Unbuffered `read()`: ~60 seconds
- Buffered 8KB: ~0.5 seconds
- `Files.readAllBytes()`: ~0.3 seconds (but 500MB heap)
- Memory-mapped: ~0.2 seconds

---

**Q3: Explain the Decorator pattern as applied in Java IO. Why was it designed this way?**

_Why they ask:_ Tests design pattern understanding through a real example.

**Answer:**
The Decorator pattern in Java IO allows adding behavior to streams by wrapping them:

```java
// Base: raw file bytes
InputStream raw = new FileInputStream("f");

// Add buffering (8KB read-ahead)
InputStream buf = new BufferedInputStream(raw);

// Add decompression
InputStream gz = new GZIPInputStream(buf);

// Add object deserialization
ObjectInputStream obj = new ObjectInputStream(gz);
```

Each decorator:

1. Implements the same interface as the wrapped stream
2. Delegates most methods to the wrapped stream
3. Adds specific behavior (buffering, decompression, etc.)
4. Can be combined in any order

**Why not inheritance?**
If buffering were a subclass of FileInputStream, you'd need: `BufferedFileInputStream`, `BufferedSocketInputStream`, `BufferedByteArrayInputStream` - one for every source. With 4 sources and 4 behaviors, inheritance requires 16 classes. Decoration requires 8 (4 sources + 4 decorators).

**The trade-off:** Flexibility at the cost of verbose constructor chains. Modern APIs like `Files.newBufferedReader()` hide the chaining behind convenience methods.

---

**Q4: What's the difference between `Files.readAllBytes()`, `Files.lines()`, and `Files.newBufferedReader()`?**

_Why they ask:_ Tests practical API knowledge for different scenarios.

**Answer:**

| Method                | Memory      | Use case               | Returns          |
| --------------------- | ----------- | ---------------------- | ---------------- |
| `readAllBytes()`      | Entire file | Small files (<50MB)    | `byte[]`         |
| `readString()`        | Entire file | Small text files       | `String`         |
| `lines()`             | One line    | Large files, streaming | `Stream<String>` |
| `newBufferedReader()` | Buffer only | Custom parsing         | `BufferedReader` |

```java
// Small file: simple, entire content in memory
String json = Files.readString(
    Path.of("config.json"), UTF_8);

// Large file: lazy streaming, constant memory
try (Stream<String> lines =
         Files.lines(Path.of("access.log"))) {
    long errors = lines
        .filter(l -> l.contains("ERROR"))
        .count();
}

// Custom parsing: full control
try (BufferedReader br =
         Files.newBufferedReader(path, UTF_8)) {
    String line;
    while ((line = br.readLine()) != null) {
        if (line.startsWith("#")) continue;
        processCSVLine(line);
    }
}
```

Critical gotcha: `Files.lines()` returns a Stream that MUST be closed (it holds a file handle). Always use try-with-resources. This is different from `List.stream()` which doesn't need closing.

---

**Q5: How would you read a 10GB log file and find the top 10 most frequent IP addresses with constant memory?**

_Why they ask:_ Tests streaming IO with algorithm design.

**Answer:**
Use `Files.lines()` for lazy streaming with a frequency map:

```java
Map<String, Long> topIPs;
try (Stream<String> lines =
         Files.lines(Path.of("access.log"))) {
    topIPs = lines
        .map(line -> line.split(" ")[0]) // IP
        .collect(Collectors.groupingBy(
            Function.identity(),
            Collectors.counting()));
}

List<Map.Entry<String, Long>> top10 = topIPs
    .entrySet().stream()
    .sorted(Map.Entry.<String, Long>
        comparingByValue().reversed())
    .limit(10)
    .toList();
```

Memory analysis: only one line is in memory at a time from the file. The frequency map holds at most one entry per unique IP. For 10GB of web logs, unique IPs are typically < 1M, so the map uses ~50MB.

For truly massive cardinality (billions of unique IPs), use a streaming approximation algorithm like Count-Min Sketch or HyperLogLog, trading exact counts for bounded memory.

---

---

# NIO and NIO.2

**TL;DR** - NIO provides non-blocking I/O with channels and buffers for high-connection servers, while NIO.2 adds the modern `Path`/`Files` API that replaces `java.io.File` for all file operations.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Classic `java.io` is blocking: one thread per connection. A chat server with 10,000 users needs 10,000 threads. Each thread uses 512KB-1MB of stack space. At 10K threads, you've consumed 5-10GB just for stacks, plus context-switching overhead brings the CPU to its knees.

**THE BREAKING POINT:**
An IoT platform receives telemetry from 100K devices. Each device maintains a persistent connection. With blocking IO, the platform needs 100K threads. The server runs out of memory at 30K threads and falls over.

**THE INVENTION MOMENT:**
"This is exactly why NIO was created."

**EVOLUTION:**
Java 1.4 introduced NIO (channels, buffers, selectors) for non-blocking IO. Java 7 added NIO.2 (java.nio.file) with `Path`, `Files`, `FileSystem`, `WatchService`, and asynchronous file channels. Java 21 introduced virtual threads, which make blocking IO scale like NIO but with simpler code - potentially reducing NIO's primary use case.

---

### Textbook Definition

NIO (New I/O, `java.nio`) provides channel-based, buffer-oriented I/O with optional non-blocking mode and selector-based multiplexing. Channels represent connections to I/O devices; buffers are fixed-size containers for data. `Selector` monitors multiple channels for readiness, enabling one thread to manage thousands of connections. NIO.2 (`java.nio.file`, Java 7) adds the `Path` interface replacing `File`, the `Files` utility class with 50+ static methods, and the `FileSystem` abstraction for virtual file systems.

---

### Understand It in 30 Seconds

**One line:**
NIO handles thousands of connections on few threads; NIO.2 is the modern file API.

**One analogy:**

> Classic IO is like a restaurant with one waiter per table - 100 tables need 100 waiters. NIO is like a single efficient waiter who checks all tables for who needs attention (Selector) and serves only those who are ready - one waiter handles 100 tables.

**One insight:**
NIO and NIO.2 solve different problems. NIO's non-blocking channels and selectors solve the C10K problem (10K+ concurrent connections). NIO.2's `Path`/`Files` API solves the terrible `java.io.File` API (no exceptions on failure, platform-dependent behavior, no symbolic link support). You typically use NIO.2 daily and NIO rarely (frameworks like Netty wrap it).

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Channels are bidirectional (unlike streams which are unidirectional)
2. Buffers have position, limit, and capacity - explicit state management
3. Selectors multiplex: one thread monitors many channels for readiness
4. `Path` is the replacement for `File` - immutable, filesystem-aware, symbolic-link-aware

**DERIVED DESIGN:**
By separating "is data available?" (Selector) from "read the data" (Channel + Buffer), NIO avoids blocking threads on idle connections. Only ready channels consume CPU time.

**THE TRADE-OFFS:**
**Gain:** Scalable to 100K+ connections, efficient memory use, modern file API
**Cost:** Complex buffer management (flip/clear/compact), callback-style programming, harder to debug

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Non-blocking IO inherently requires readiness checking and event-driven programming.
**Accidental:** Buffer's flip()/clear()/compact() API is notoriously confusing and error-prone.

---

### Mental Model / Analogy

> Classic IO: a phone operator manually connecting each call (one thread per connection). NIO: a switchboard that lights up when any line has activity, and the operator handles only active lines.

- "Phone line" -> Channel
- "Switchboard light" -> Selector key readiness
- "Operator" -> single thread
- "Call buffer" -> ByteBuffer
- "Multiple lit lines" -> multiple ready channels

Where this analogy breaks down: Modern phone switchboards are automated, while NIO still requires manual buffer management.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
NIO lets a server handle many connections without needing one thread per connection. NIO.2 is Java's modern way to work with files and directories - much better than the old `File` class.

**Level 2 - How to use it (junior developer):**
For file operations, use `Path` and `Files` exclusively - never `java.io.File`. `Files.readString()`, `Files.lines()`, `Files.copy()`, `Files.walk()` cover 90% of file needs. For network programming, use a framework (Netty, Spring WebFlux) that wraps NIO - don't write raw NIO code.

**Level 3 - How it works (mid-level engineer):**
NIO `Selector` uses OS-level epoll (Linux) or kqueue (macOS) to efficiently monitor file descriptors. When `selector.select()` returns, it provides a set of `SelectionKey`s indicating which channels are ready for read, write, accept, or connect. `ByteBuffer` manages an internal array with position/limit/capacity cursors: `put()` advances position, `flip()` sets limit=position and position=0 for reading, `clear()` resets for new writing. `MappedByteBuffer` maps files into virtual memory for zero-copy access.

**Level 4 - Mastery (senior/staff+ engineer):**
NIO's event-driven model underpins all high-performance Java servers: Netty, Tomcat NIO connector, Vert.x, gRPC. The Reactor pattern wraps Selector with a thread pool: one selector thread accepts connections, worker threads handle ready channels. With Java 21 virtual threads, the NIO complexity becomes optional for most workloads - `Thread.ofVirtual()` with blocking IO achieves similar scalability with simpler code. However, NIO still wins for true zero-copy scenarios (`FileChannel.transferTo()`) and memory-mapped I/O. `WatchService` provides filesystem event monitoring but has platform-specific reliability issues - on macOS it falls back to polling.

---

### How It Works

```
NIO Selector model:

  Selector
    +-- Channel A (READABLE)    --> read
    +-- Channel B (idle)        --> skip
    +-- Channel C (WRITABLE)    --> write
    +-- Channel D (ACCEPTABLE)  --> accept
    +-- Channel E (idle)        --> skip

  One thread loop:
  while (true) {
      selector.select(); // blocks until ready
      for (key : selector.selectedKeys()) {
          if (key.isAcceptable()) accept();
          if (key.isReadable())   read();
          if (key.isWritable())   write();
      }
  }
  // 1 thread handles 1000s of connections
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
ServerSocketChannel.open()
  -> bind to port
  -> register with Selector (OP_ACCEPT)
  -> selector.select()  <- YOU ARE HERE
  -> client connects -> OP_ACCEPT fires
  -> accept() -> register client (OP_READ)
  -> client sends data -> OP_READ fires
  -> read into ByteBuffer -> process
  -> register OP_WRITE -> write response
```

**FAILURE PATH:**

```
Buffer not flipped before reading
  -> position at end, limit at capacity
  -> read returns 0 bytes
  -> silent data loss / empty responses
  -> hours of debugging buffer state
```

**WHAT CHANGES AT SCALE:**
At 100K connections, a single Selector thread becomes a bottleneck. Netty uses multiple Selectors across an `EventLoopGroup` (typically one per CPU core). Each Selector handles a subset of connections. At 1M+ connections, OS-level tuning is needed: increase `ulimit -n`, tune `net.core.somaxconn`, enable `SO_REUSEPORT`.

---

### Code Example

**Example 1 - NIO.2 file operations (use this daily)**

```java
// BAD: old File API
File f = new File("/data/config.txt");
if (f.exists()) { // doesn't throw on error!
    // might fail silently
}

// GOOD: NIO.2 Path/Files API
Path p = Path.of("/data/config.txt");
if (Files.exists(p)) {
    String content = Files.readString(p, UTF_8);
}

// File operations with proper error handling
Files.copy(source, target,
    StandardCopyOption.REPLACE_EXISTING);
Files.move(old, newPath,
    StandardCopyOption.ATOMIC_MOVE);
Files.createDirectories(
    Path.of("/data/logs/2024"));

// Walk directory tree
try (Stream<Path> walk = Files.walk(root)) {
    List<Path> javaFiles = walk
        .filter(p -> p.toString().endsWith(".java"))
        .toList();
}
```

**Example 2 - ByteBuffer basics**

```java
// Allocate buffer
ByteBuffer buf = ByteBuffer.allocate(1024);
// position=0, limit=1024, capacity=1024

// Write data into buffer
buf.put("Hello".getBytes(UTF_8));
// position=5, limit=1024

// CRITICAL: flip before reading!
buf.flip();
// position=0, limit=5

// Read data from buffer
byte[] data = new byte[buf.remaining()];
buf.get(data);
// position=5, limit=5

// Reset for reuse
buf.clear();
// position=0, limit=1024
```

**How to test / verify correctness:**
Test NIO.2 operations with `jimfs` (in-memory filesystem). Test buffer operations by verifying position/limit after each operation. Test Selector-based code with `SocketChannel.open()` in test connecting to a local server.

---

### Quick Recall

**If you remember only 3 things:**

1. Use `Path`/`Files` for all file operations - never `java.io.File` (NIO.2 is the modern API)
2. NIO Selector lets one thread handle thousands of connections - but use Netty instead of raw NIO
3. ByteBuffer: always `flip()` before reading - the #1 NIO bug is forgetting this

**Interview one-liner:**
"NIO provides non-blocking I/O with Selectors that multiplex thousands of connections on few threads - this powers Netty and Tomcat's NIO connector. NIO.2's Path/Files API replaced the broken java.io.File with proper exception handling and modern filesystem operations."

---

### The Surprising Truth

Java 21's virtual threads may make NIO's non-blocking model unnecessary for most applications. With virtual threads, you write simple blocking IO code (`socket.read()`) and the JVM automatically parks the virtual thread and reuses the carrier thread - achieving NIO-like scalability with blocking-style simplicity. Internally, virtual threads use NIO under the hood. The framework does the complex event-driven programming so you don't have to.

---

### Interview Deep-Dive

**Q1: What is the difference between NIO and NIO.2?**

_Why they ask:_ Tests whether you know these are different things.

**Answer:**
They solve completely different problems:

**NIO (Java 1.4, `java.nio`):**

- Channels and Buffers for I/O
- Selector for non-blocking network I/O
- Solves: high-concurrency server problem (C10K)
- Key classes: `SocketChannel`, `Selector`, `ByteBuffer`

**NIO.2 (Java 7, `java.nio.file`):**

- Modern file system API
- Replaces `java.io.File`
- Solves: broken File API (no error handling, no symlinks, platform issues)
- Key classes: `Path`, `Files`, `FileSystem`, `WatchService`

In daily development, you use NIO.2 constantly (`Files.readString()`, `Path.of()`) but rarely touch raw NIO (Netty wraps it). Think of NIO.2 as "the thing you should use for files" and NIO as "the thing Netty uses for networking."

---

**Q2: Explain ByteBuffer's position, limit, and capacity. What does flip() do and why is it critical?**

_Why they ask:_ Tests understanding of the most error-prone NIO concept.

**Answer:**
ByteBuffer has three state variables:

- **capacity:** Total buffer size (fixed at allocation)
- **position:** Index of next read/write location
- **limit:** First index that should NOT be read/written

Invariant: `0 <= position <= limit <= capacity`

**Common operations:**

```
allocate(10):  pos=0  lim=10  cap=10
               [_, _, _, _, _, _, _, _, _, _]
                ^                             ^
               pos                           lim/cap

put("Hello"):  pos=5  lim=10  cap=10
               [H, e, l, l, o, _, _, _, _, _]
                               ^              ^
                              pos            lim

flip():        pos=0  lim=5   cap=10
               [H, e, l, l, o, _, _, _, _, _]
                ^              ^
               pos            lim
               "Ready to READ 5 bytes"

get(5 bytes):  pos=5  lim=5   cap=10
               [H, e, l, l, o, _, _, _, _, _]
                               ^
                            pos=lim

clear():       pos=0  lim=10  cap=10
               "Ready to WRITE again"
```

**Why flip() is critical:** Without flip(), position stays at 5 (after writing) and limit stays at 10. A read would start at position 5 and read garbage data from positions 5-9 instead of the "Hello" at positions 0-4.

Mnemonic: **write-flip-read-clear**: Write data, flip to prepare for reading, read data, clear to prepare for writing.

---

**Q3: How does Selector-based multiplexing work? What OS mechanism does it use?**

_Why they ask:_ Tests systems-level understanding.

**Answer:**
`Selector.select()` delegates to the OS kernel's I/O multiplexing mechanism:

| OS      | Mechanism | Characteristics                         |
| ------- | --------- | --------------------------------------- |
| Linux   | epoll     | O(1) per ready event, edge-triggered    |
| macOS   | kqueue    | O(1) per ready event, edge-triggered    |
| Windows | IOCP      | Completion-based (async), not readiness |

**How epoll works (Linux):**

1. Application registers file descriptors with epoll via `epoll_ctl()`
2. Application calls `epoll_wait()` - blocks until any FD is ready
3. Kernel returns only the ready FDs (O(number_ready), not O(total_FDs))
4. Application processes ready FDs and loops

Java's `Selector.select()` maps to `epoll_wait()`. Each `SelectionKey` represents a registered channel+interest-ops pair. When `select()` returns, `selectedKeys()` gives only channels with pending events.

```java
// Java Selector -> OS epoll mapping
Selector sel = Selector.open();
// -> epoll_create()

channel.register(sel, OP_READ);
// -> epoll_ctl(EPOLL_CTL_ADD, fd, EPOLLIN)

sel.select();
// -> epoll_wait() - blocks
// returns when any registered fd is ready
```

Key insight: older `select()` and `poll()` system calls are O(n) where n is total FDs. `epoll` is O(k) where k is ready FDs. This is why NIO scales to 100K+ connections.

---

**Q4: When would you use memory-mapped files (MappedByteBuffer)?**

_Why they ask:_ Tests knowledge of advanced IO optimization.

**Answer:**
Memory-mapped files map a file directly into the process's virtual address space. Reads and writes become memory accesses - no `read()`/`write()` system calls.

```java
try (FileChannel fc = FileChannel.open(
         path, READ, WRITE)) {
    MappedByteBuffer mmap = fc.map(
        FileChannel.MapMode.READ_WRITE,
        0, fc.size());

    // Read: direct memory access (no syscall)
    byte b = mmap.get(1000);

    // Write: direct memory access
    mmap.put(1000, (byte) 42);
    // OS flushes to disk asynchronously
}
```

**Use when:**

1. **Random access to large files:** Database storage engines, search indexes
2. **Shared memory between processes:** Multiple JVMs reading the same mapped file
3. **High-performance read-heavy workloads:** The OS page cache handles caching automatically

**Avoid when:**

1. **Sequential reading:** `BufferedInputStream` is simpler and nearly as fast
2. **Files larger than available virtual address space:** 32-bit JVMs limited to ~2GB mappings
3. **Frequent writes with durability needs:** `mmap.force()` for fsync is expensive

**Real-world users:** Lucene (search indexes), RocksDB, Kafka (log segments), Chronicle Queue.

Key insight: memory-mapped I/O doesn't actually load the file into memory. It creates a virtual memory mapping. The OS loads pages on demand (page faults) and can evict them under memory pressure. You can "map" a 100GB file on a machine with 8GB RAM - the OS manages which pages are resident.

---

**Q5: With Java 21 virtual threads, is NIO still necessary?**

_Why they ask:_ Tests awareness of modern Java evolution.

**Answer:**
For most applications, virtual threads make NIO's non-blocking model unnecessary. Here's the comparison:

**NIO approach (pre-Java 21):**

```java
// Complex, callback-driven
Selector sel = Selector.open();
channel.register(sel, OP_READ);
while (true) {
    sel.select();
    for (SelectionKey key : sel.selectedKeys()) {
        if (key.isReadable()) handleRead(key);
    }
}
```

**Virtual threads approach (Java 21+):**

```java
// Simple, blocking code that scales
try (var server = ServerSocket(8080)) {
    while (true) {
        Socket client = server.accept();
        Thread.ofVirtual().start(() -> {
            handle(client); // blocking IO is fine!
        });
    }
}
```

Virtual threads park on blocking IO calls and release the carrier thread - achieving NIO-like scalability with blocking-style simplicity.

**Where NIO still wins:**

1. **Zero-copy:** `FileChannel.transferTo()` sends file data to a socket without copying through user space
2. **Memory-mapped files:** Direct file-to-memory mapping has no virtual thread equivalent
3. **Existing frameworks:** Netty, gRPC, and async frameworks are built on NIO and won't rewrite
4. **Ultra-low latency:** NIO with busy-polling avoids the virtual thread scheduling overhead

For new projects: start with virtual threads + blocking IO. Only drop to NIO if profiling shows it's needed.
