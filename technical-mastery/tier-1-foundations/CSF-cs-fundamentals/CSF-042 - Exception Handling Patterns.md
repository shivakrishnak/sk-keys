---
id: CSF-042
title: Exception Handling Patterns
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-024, CSF-043
used_by: SPR-015, JPH-018
related: CSF-038, CSF-043, DST-022
tags: [exceptions, checked-exceptions, error-handling, result-type, exception-patterns]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/csf/exception-handling-patterns/
---

⚡ TL;DR - Exceptions signal failures that callers must handle.
Checked exceptions force handling at compile time; unchecked
don't. Patterns: checked for recoverable (caller can react),
unchecked for programming errors, Result/Either for
functional-style explicit error paths.

| #042 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-024 (Functional Programming), CSF-043 (Null Safety) | |
| **Used by:** | SPR-015 (Spring Exception Handling), JPH-018 (JPA Exceptions) | |
| **Related:** | CSF-038 (Algebraic Data Types), DST-022 (Resilience Patterns) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Early languages (C) use return codes to signal errors.
`read()` returns -1 on error; 0 on EOF; positive on bytes read.
The caller MUST check the return value to detect errors.
But nothing FORCES the caller to check. Unchecked return
codes are the most common source of bugs in C programs:
`int fd = open("file"); // fd could be -1; nobody checked`.
The error propagates silently until it manifests as
corruption or a crash far from where the error originated.

**THE BREAKING POINT:**

Two problems: (1) error codes are invisible - a method
returns `null` or `-1` to signal error, but the type
system does not distinguish this from a valid return value;
(2) error propagation requires every caller in the call
stack to explicitly check and propagate errors, creating
layers of `if (error != null) return error;` boilerplate
that obscures the happy path.

**THE INVENTION MOMENT:**

CLU (1975) introduced exceptions: a separate channel for
error signaling that INTERRUPTS normal flow and FORCES
handling at some level (or terminates the program). Java
extended this with CHECKED exceptions (compiler-enforced
handling): if a method declares `throws IOException`, every
caller MUST either catch the exception or declare that it
also throws it. This brought error handling into the type
system. The trade-off: checked exceptions force handling
but add verbosity; unchecked exceptions are silent but
require discipline. Modern systems also use Result/Either
types (functional) that make error paths explicit in the
return type without the exception control flow overhead.

---

### 📘 Textbook Definition

**Exception:** An object that signals an unexpected condition
has occurred. When thrown, the normal execution stack is
unwound until a matching `catch` block is found or the
thread terminates.

**Checked exception (`extends Exception`):** Compiler requires
every caller to handle or declare (`throws`). Signals
recoverable conditions where the caller is expected to
react (file not found, network timeout).

**Unchecked exception (`extends RuntimeException`):** No
compiler enforcement. Signals programming errors or
unrecoverable conditions (null pointer, array index out
of bounds, illegal argument).

**Error (`extends Error`):** JVM-level problems (OutOfMemoryError,
StackOverflowError). Should never be caught in application code.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Exceptions are a separate error channel that interrupt normal
flow. Checked = "you MUST handle this"; unchecked = "this
should not happen."

**One analogy:**

> Normal code: happy path, like driving on a clear road.
> Exception: an emergency exit ramp that diverts traffic off
> the main road. Checked exception: the road has mandatory
> exit signs that every driver must acknowledge. Unchecked:
> the emergency exit exists but drivers are expected to stay
> on the road (programming errors mean the driver made a mistake).

**One insight:**

Spring's `@ExceptionHandler` and `@ControllerAdvice` are
the production answer to the question "where should
exceptions be handled?" In a layered Spring application,
service methods throw domain exceptions (e.g., `OrderNotFoundException`);
the Spring MVC layer catches them via `@ControllerAdvice`
and maps them to HTTP responses (404, 400, etc.). The
service layer does NOT know about HTTP; the web layer
does NOT know about domain logic. Exceptions are the
cross-layer error signaling mechanism; `@ControllerAdvice`
is the "catch all" at the boundary.

---

### 🔩 First Principles Explanation

**JAVA EXCEPTION HIERARCHY:**

```
┌──────────────────────────────────────────────────────┐
│ Throwable                                            │
│   Error (JVM-level; never catch)                     │
│     OutOfMemoryError                                 │
│     StackOverflowError                               │
│   Exception (application-level)                      │
│     IOException (CHECKED - declare or catch)         │
│       FileNotFoundException                          │
│     SQLException (CHECKED)                           │
│     RuntimeException (UNCHECKED - no declaration)    │
│       NullPointerException                           │
│       IllegalArgumentException                       │
│       IllegalStateException                          │
│       IndexOutOfBoundsException                      │
└──────────────────────────────────────────────────────┘
```

**EXCEPTION HANDLING PATTERNS:**

```
┌──────────────────────────────────────────────────────┐
│ 1. CATCH AND RECOVER                                 │
│    try { save(entity); }                             │
│    catch (DuplicateKeyException e) {                 │
│        // recoverable: try upsert instead            │
│        update(entity);                               │
│    }                                                 │
│                                                      │
│ 2. CATCH AND RETHROW (translate)                     │
│    try { db.save(entity); }                          │
│    catch (SQLException e) {                          │
│        // wrap infrastructure exception in domain   │
│        throw new OrderPersistenceException(          │
│            "Failed to save order", e);               │
│    }                                                 │
│                                                      │
│ 3. CATCH AND LOG (only at boundary)                  │
│    try { process(event); }                           │
│    catch (Exception e) {                             │
│        log.error("Event processing failed: {}", e);  │
│    }                                                 │
│                                                      │
│ 4. LET IT PROPAGATE (no catch at all)                │
│    void saveOrder(Order o) throws OrderException {   │
│        orderRepo.save(o); // throws -> propagates    │
│    }  // caller handles                              │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**CHECKED vs UNCHECKED: THE JAVA DEBATE:**

`java.io.IOException` is checked. Every time you read a file,
you must handle or declare `IOException`. In a 5-layer call
stack (Controller -> Service -> Repository -> FileManager -> IO),
EVERY layer must either catch or re-declare `throws IOException`.
This creates:
- 5 try-catch or throws declarations for one IO operation
- Callers know the INTERNAL implementation detail (it uses IO)
- The abstraction leaks: `UserService.findUser()` declaring
  `throws IOException` reveals it uses file IO internally

The Spring/modern Java answer: wrap checked exceptions in
unchecked at the boundary. Spring's `JdbcTemplate` wraps
`SQLException` (checked) in `DataAccessException` (unchecked).
Callers are freed from mandatory handling. The principle:
checked exceptions should be used only when the caller
is ACTUALLY EXPECTED TO RECOVER. For most infrastructure
errors (IO, DB failures), recovery is not possible at the
service layer - the error should propagate to the application
boundary (HTTP 500) without every layer explicitly re-declaring it.

---

### 🎯 Mental Model / Analogy

**TWO POSTAL SERVICES:**

Checked exception: certified mail. You MUST sign for it.
The carrier does not leave until you acknowledge receipt.
You CANNOT ignore it.

Unchecked exception: a live grenade that appears if your
code has a bug. It explodes (crashes the thread) if not
caught. No one forces you to have a plan; you are expected
to write code without bugs (not throw unchecked exceptions
under normal conditions).

**MEMORY HOOK:**

"Checked = recoverable, force handling.
Unchecked = programmer error or unrecoverable.
Never catch Exception blindly - catch the specific type.
Never swallow exceptions silently (empty catch block).
Translate infrastructure exceptions to domain exceptions.
Handle at the BOUNDARY; propagate through the middle."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
An exception is a surprise that stops normal code. If you
tell your program to open a file that does not exist, the
file-not-found exception is the program saying "I cannot
do this - what should I do?" The program then follows special
instructions for handling surprises.

**Level 2 - Student:**
```java
try {
    String content = Files.readString(Path.of("data.txt"));
    process(content);
} catch (IOException e) {         // handle file errors
    log.error("File read failed", e);
    throw new DataProcessingException("Cannot process data", e);
} finally {
    cleanup(); // always runs, even on exception
}
```
`try` = attempt. `catch` = handle specific error type. `finally` = always run.

**Level 3 - Professional:**
Translate exceptions at architectural boundaries. Repository
catches `SQLException`, wraps in `DataAccessException` (domain).
Service catches `DataAccessException`, may wrap in `OrderServiceException`.
Controller catches domain exceptions, maps to HTTP status codes via
`@ControllerAdvice`. Each layer speaks its own exception language.
Infrastructure exceptions never leak to the API response.

**Level 4 - Senior Engineer:**
Result types (functional approach):
```java
sealed interface Result<T> permits Result.Ok, Result.Err {}
record Ok<T>(T value) implements Result<T> {}
record Err<T>(String message, Exception cause) implements Result<T> {}

Result<Order> findOrder(UUID id) {
    return orderRepo.findById(id)
        .map(Result::Ok)
        .<Result<Order>>map(ok -> ok)
        .orElse(new Err<>("Order not found: " + id, null));
}
// Caller: switch on Result type (pattern matching)
switch (findOrder(id)) {
    case Ok<Order> ok -> processOrder(ok.value());
    case Err<Order> err -> log.warn(err.message());
}
```
Result types make error paths explicit in the return type.
No exceptions, no hidden control flow.

**Level 5 - Expert:**
Exception handling performance: in Java, exception creation
includes capturing the stack trace (relatively expensive).
For high-throughput paths where exceptions are EXPECTED
(e.g., a parser that frequently encounters invalid tokens),
options: (1) pre-create and re-throw a static exception
(loses stack trace but avoids allocation), (2) use error
codes or Result types for expected failures, (3) override
`fillInStackTrace()` to return `this` (skip stack capture).
For UNEXPECTED exceptions, the performance cost of creation
is acceptable - exceptions should not be on the hot path.

---

### ⚙️ How It Works (Formal Basis)

**EXCEPTION PROPAGATION:**

```
┌──────────────────────────────────────────────────────┐
│ Call stack:                                          │
│   main() -> loadConfig() -> parseFile() -> readLine()│
│                                                      │
│ readLine() throws IOException:                       │
│   Stack unwinds: readLine frame exits (no catch)     │
│   parseFile frame: no catch for IOException -> exits │
│   loadConfig frame: has catch (IOException e) -> runs│
│                                                      │
│ Unwinding is non-local: skips all frames between     │
│ throw and the matching catch. finally blocks run      │
│ during unwinding. Resources in try-with-resources    │
│ are closed automatically during unwinding.           │
│                                                      │
│ try-with-resources (Java 7+):                        │
│   try (Connection conn = ds.getConnection()) {       │
│       // conn is AutoCloseable                       │
│   }  // conn.close() called automatically            │
│   // Even if exception thrown, close is guaranteed   │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Exception Handling Anti-Patterns**

```java
// BAD #1: swallowing exception (silent failure)
try {
    processOrder(order);
} catch (Exception e) {
    // nothing - bug disappears silently
}

// BAD #2: catching Exception (too broad)
try {
    processOrder(order);
} catch (Exception e) {  // catches NPE, OOM, everything!
    log.error("Error", e); // and continues - dangerous
}

// BAD #3: losing the cause (missing getCause chain)
try {
    db.save(entity);
} catch (SQLException e) {
    throw new ServiceException("DB error"); // original e LOST
}

// GOOD: catch specific, translate with cause, handle at boundary
try {
    db.save(entity);
} catch (DuplicateKeyException e) {
    // Recoverable: specific exception type
    throw new EntityAlreadyExistsException(entity.id(), e); // cause preserved
} catch (DataAccessException e) {
    // Unrecoverable at this level: propagate with context
    throw new OrderPersistenceException(
        "Failed to persist order " + entity.id(), e); // cause preserved
}
```

**Example 2 - Production: Spring @ControllerAdvice Pattern**

```java
// Domain exceptions (unchecked)
class OrderNotFoundException extends RuntimeException {
    private final UUID orderId;
    OrderNotFoundException(UUID id) {
        super("Order not found: " + id);
        this.orderId = id;
    }
    UUID orderId() { return orderId; }
}

// Centralized exception-to-HTTP mapping
@ControllerAdvice
class GlobalExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    ResponseEntity<ErrorResponse> handleOrderNotFound(
            OrderNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(
                "ORDER_NOT_FOUND",
                ex.getMessage(),
                ex.orderId().toString()
            ));
    }

    @ExceptionHandler(ValidationException.class)
    ResponseEntity<ErrorResponse> handleValidation(
            ValidationException ex) {
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("VALIDATION_ERROR", ex.getMessage(), null));
    }

    @ExceptionHandler(Exception.class) // catch-all (last resort)
    ResponseEntity<ErrorResponse> handleUnexpected(Exception ex) {
        log.error("Unexpected error", ex); // log with full stack
        return ResponseEntity.internalServerError()
            .body(new ErrorResponse("INTERNAL_ERROR",
                "An unexpected error occurred", null));
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Language | Type Safety | Performance | Best For |
|---|---|---|---|---|
| Checked exceptions | Java | Compiler-enforced | Normal | Recoverable errors (IO, network) |
| Unchecked exceptions | Java, Kotlin | Runtime only | Normal | Programming errors, unrecoverable |
| Result/Either type | Kotlin, Scala, Java (manual) | Compiler-enforced | No stack trace | Expected failures (parsing, validation) |
| Error codes | C, Go | None (must check) | Fast | Systems programming |
| Optional | Java, Kotlin | Compiler-enforced | Fast | Missing values (not errors) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Checked exceptions are better because they force handling" | Checked exceptions force syntactic handling but not semantic handling. An empty catch block "handles" a checked exception without actually doing anything. Many APIs (Spring, Hibernate) wrap checked exceptions in unchecked precisely because forcing every layer to declare `throws X` leaks implementation details and creates verbosity without real safety. |
| "Catch (Exception e) is fine because I log it" | Catching `Exception` catches `RuntimeException` including `NullPointerException`, `IllegalStateException` - bugs that should crash-and-fix, not log-and-continue. Catching `NullPointerException` and logging it hides a bug. Catch the MOST SPECIFIC type you can handle. Use a catch-all `Exception` handler ONLY at the outermost boundary (HTTP layer, message consumer), where logging and error response are the only options. |
| "Exceptions are expensive - avoid them" | Exception creation (including stack trace capture) has cost, but exceptions are for EXCEPTIONAL conditions. If exceptions appear frequently in profiling, the design is wrong (exceptions used for flow control, which is an anti-pattern). For truly exceptional errors, the cost is acceptable. Never sacrifice error handling clarity for premature optimization. |
| "`finally` always runs, even with `return` in try" | `finally` runs even when `return` is in the `try` block. But `finally` does NOT run if the JVM is killed (`System.exit()`), the thread is force-killed, or hardware failure. For resource cleanup, `try-with-resources` is preferred over `finally`. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Exception Swallowing in Async Code**

**Symptom:** Async tasks (thread pool, `CompletableFuture`,
`@Async`) silently fail. Operations seem to complete but
produce no result. No error in logs.

**Root Cause:** Uncaught exceptions in async tasks are
swallowed by the executor. `ExecutorService.submit()` returns
a `Future`. If you never call `future.get()`, any exception
inside the task is silently lost. Spring `@Async` methods
that return `void` have the same problem.

**Diagnosis:**
```java
// Configure Spring @Async exception handler
@Bean
AsyncUncaughtExceptionHandler asyncExceptionHandler() {
    return (ex, method, params) ->
        log.error("Async error in {}: {}", method.getName(), ex.getMessage(), ex);
}
```
**Fix:** Return `CompletableFuture<T>` from `@Async` methods
so callers can chain `exceptionally()`. Or configure
`AsyncUncaughtExceptionHandler`. Always log exceptions
in task executor rejection handlers.

**Failure Mode 2: Exception Translation Missing Cause Chain**

**Symptom:** Exception in logs shows a service-level exception
with a generic message but no root cause. Cannot trace
back to the original SQL error, network error, or IO error.

**Root Cause:** Exception wrapping without passing the cause:
`throw new ServiceException("Failed")` - no `cause` parameter.
The original exception (with the real error detail and stack)
is lost.

**Fix:** ALWAYS pass the cause when wrapping:
`throw new ServiceException("Failed to process order " + id, originalException)`.
In logging: `log.error("Failed", e)` not `log.error("Failed: " + e.getMessage())`.
The second form loses the stack trace; the first form logs both
message and stack.

---

**Security Note:**

Exception messages are a security risk when they leak
implementation details to API responses. A `try { ... }
catch (SQLException e) { return Response.serverError().entity(e.getMessage()).build(); }`
exposes the SQL query structure, table names, column names
to the API consumer - information useful for SQL injection
attacks. Rule: NEVER return raw exception messages to API
responses. Map exceptions to safe, generic error responses
at the API boundary. Log the full exception internally
but expose only a code (e.g., `"ORDER_NOT_FOUND"`) and
user-safe message externally. Stack traces in HTTP responses
are a OWASP Top 10 finding (A05:2021 Security Misconfiguration).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - exceptions are objects in an inheritance
  hierarchy; class hierarchy and polymorphism required
- `Functional Programming` (CSF-024) - Result/Either types
  are functional error handling patterns

**Builds On This (learn these next):**
- `Null Safety` (CSF-043) - `Optional` and null handling
  is the adjacent error-avoidance concern
- `Spring Exception Handling` (SPR-015) - production Spring
  patterns for `@ControllerAdvice` and exception mapping

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ CHECKED      │ extends Exception (not Runtime)         │
│              │ Compiler forces handle or declare       │
│              │ Use: recoverable (IO, network)          │
├──────────────┼─────────────────────────────────────────┤
│ UNCHECKED    │ extends RuntimeException                │
│              │ No compiler enforcement                 │
│              │ Use: programming errors, unrecoverable  │
├──────────────┼─────────────────────────────────────────┤
│ TRANSLATE    │ catch SQLException -> throw DomainEx    │
│              │ ALWAYS pass cause: new Ex("msg", e)     │
├──────────────┼─────────────────────────────────────────┤
│ HANDLE AT    │ Exception handler at API/consumer       │
│              │ boundary - not in every layer           │
├──────────────┼─────────────────────────────────────────┤
│ NEVER DO     │ Empty catch block (swallows silently)   │
│              │ catch(Exception e) in business logic    │
│              │ throw new Ex("msg") without cause       │
│              │ Exception message in API response       │
├──────────────┼─────────────────────────────────────────┤
│ TRY-WITH-RES │ try(Resource r = ...) { } // auto-close │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-043 (Null Safety), SPR-015 (Spring) │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Checked exceptions = force handling, use for conditions
   the caller can ACTUALLY RECOVER FROM (file not found -
   create the file; network timeout - retry). Unchecked =
   programmer errors (NPE, IAE) or unrecoverable failures.
   Modern frameworks wrap infrastructure checked exceptions
   in unchecked to prevent leaking implementation details.
2. Always preserve the cause chain: `throw new DomainException("msg", originalException)`.
   Never `throw new DomainException("msg")` without the
   cause - you lose the root cause and stack trace. Log
   with `log.error("Failed", e)` not `log.error("Failed: " + e.getMessage())`.
3. Handle at the boundary, not in every layer. Spring's
   `@ControllerAdvice` and `@ExceptionHandler` map domain
   exceptions to HTTP responses at the web layer. Service
   and repository layers throw; the boundary catches and translates.
   Never expose internal exception messages in API responses.

**Interview one-liner:**
"Checked exceptions force compile-time handling for recoverable
conditions; unchecked signal programming errors or unrecoverable
failures. Pattern: service layers throw domain-specific
unchecked exceptions; `@ControllerAdvice` maps them to HTTP
status codes at the boundary. Always wrap with cause chain;
never swallow silently; never expose internal exception
details in API responses."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Exception handling reflects the "separation of concerns"
principle applied to error paths. The code that detects
a failure (low-level: IO, SQL) should not decide how to
respond to it (business level: retry, fallback, reject).
Exceptions allow these concerns to be separated across
layers. This same principle drives: circuit breakers
(Resilience4j) separate failure detection from response policy;
Kafka consumer error handling separates detection (deserialization
failure) from policy (dead-letter queue, retry, skip);
HTTP 4xx/5xx separates error detection (server) from handling
(client retry logic). Error propagation and error handling
are two distinct responsibilities that belong at different
architectural layers.

**Where else this pattern appears:**

- **gRPC status codes** - gRPC has a standardized set of
  status codes (OK, CANCELLED, INVALID_ARGUMENT, NOT_FOUND,
  ALREADY_EXISTS, PERMISSION_DENIED, INTERNAL) analogous
  to checked exceptions but for RPC. Every gRPC call returns
  a `Status`. The client must handle non-OK statuses.
  This is the "checked exception" model for distributed systems.
- **Go's multiple return values** - Go uses `(value, error)`
  returns as its error handling mechanism: `f, err := os.Open("file")`.
  The caller MUST check `err != nil` before using `f`.
  This is the "error code" model with explicit multiplicity.
  No exceptions, no control flow changes. Compared to Java:
  more explicit, less syntactically overhead for propagation,
  but requires discipline to not ignore the error return.
- **Rust's `Result<T, E>` type** - Rust has no exceptions.
  All fallible operations return `Result<T, E>`. The `?`
  operator propagates errors: `let f = File::open("file")?;`
  automatically returns the error if `open` fails.
  `match result { Ok(v) => use(v), Err(e) => handle(e) }`.
  This is the functional Result pattern at the language level.
  Java 21+ sealed interfaces + pattern matching can approximate
  this (`Result<T>` as sealed record union).

---

### 💡 The Surprising Truth

Java's checked exceptions were conceived as a revolutionary
safety feature: the compiler would guarantee that all
exceptional conditions are handled, eliminating the silent
error-propagation bugs of C. By 2010, they were widely
considered a failed experiment. Why? Because the Java
ecosystem proved that most exceptions are NOT recoverable
at the call site. `IOException`, `SQLException`, `ClassNotFoundException` -
callers almost always either propagate them or wrap them.
The `throws` declarations became noise. The most successful
Java frameworks (Spring, Hibernate, JPA) all wrap checked
exceptions in unchecked (Spring's `DataAccessException`,
Hibernate's `HibernateException`). Kotlin removed checked
exceptions entirely. Scala never had them. Java's own
`CompletableFuture` API works entirely with unchecked
exceptions. The original vision - compiler-enforced exception
handling - produced more boilerplate than safety.
The lesson: safety enforced by the compiler must match
what developers actually do in practice, or it will be
worked around. Checked exceptions are the most prominent
case of a well-intentioned Java feature that the ecosystem
rejected over 30 years.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[DESIGN]** Design exception hierarchy for an e-commerce
   service: base `EcommerceException`, subclasses for
   `OrderNotFoundException`, `PaymentDeclinedException`,
   `InventoryException`. Decide which are checked vs unchecked
   and justify each decision.

2. **[IMPLEMENT]** Implement a Spring `@ControllerAdvice` that
   handles `OrderNotFoundException` (404), `ValidationException`
   (400), `PaymentDeclinedException` (402), and a catch-all
   (500). Each response must include an error code, user-safe
   message, and correlation ID (from MDC). No internal
   exception details in the response body.

3. **[DIAGNOSE]** Given a Spring Boot application where
   `@Async` methods occasionally fail silently (no error
   in logs, no result produced), diagnose the root cause
   and implement the fix using `AsyncUncaughtExceptionHandler`.

4. **[REFACTOR]** Take a 20-line service method with
   multiple `try-catch` blocks, empty catches, and one
   missing cause chain. Refactor to correct patterns:
   specific types, cause preservation, translation to
   domain exceptions.

5. **[DESIGN]** Design a Result type for a Java service
   that validates user registration input. Use sealed
   interfaces and records. Show how the caller uses
   pattern matching to handle `Ok` and `Err` cases.

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `try-with-resources` ensures that the resource's
`close()` method is called even if an exception occurs.
If BOTH the try block throws an exception AND the `close()`
method throws an exception, what happens? Which exception
is visible to the caller?

*Hint: The exception from the try block is the PRIMARY
exception - it is what the caller receives. The exception
from `close()` is a SUPPRESSED exception: it is attached
to the primary exception via `addSuppressed()` and can
be retrieved via `getSuppressed()`. This is an important
behavior: if `close()` threw the exception and suppressed
the try-block exception, the original failure context
would be lost. Java's design preserves the try-block
exception as the primary and attaches the close-exception
as secondary. In logging: always log the full exception
with `.getSuppressed()` to see both errors.*

**Q2.** In a Spring Boot application, a `@Service` method
is annotated with `@Transactional`. It calls a repository
which throws a `RuntimeException`. Spring's transaction
management catches the exception, rolls back the transaction,
and re-throws it. But the developer wraps the repository
call in `try { ... } catch (Exception e) { log.error("...", e); }`
and DOES NOT re-throw. What happens to the transaction?

*Hint: The transaction is NOT rolled back. Spring's transaction
management works by intercepting exceptions as they propagate
through the proxy. If the exception is caught and not
re-thrown, Spring's proxy never sees the exception. Spring
cannot distinguish "the method completed normally" from
"the method caught and swallowed an exception." Result:
the transaction COMMITS even though the operation failed.
This is one of the most common Spring @Transactional bugs.
Fix: either re-throw (or throw a different exception),
or call `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()`
to manually mark the transaction for rollback.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between checked and unchecked
exceptions in Java? When would you use each?"**

*Why they ask:* Core Java knowledge. Tests whether the candidate
understands the design rationale, not just the syntax.

*Strong answer includes:*
- Checked: extends `Exception` (not `RuntimeException`).
  Compiler requires the caller to handle or declare.
  Intended for recoverable conditions where the caller
  is expected to react. Example: `IOException` - the caller
  may retry with a different file or show a user-facing error.
- Unchecked: extends `RuntimeException`. No compiler enforcement.
  For programming errors (NPE, IAE) or unrecoverable conditions.
  Callers are not expected to recover programmatically.
- Modern practice: most enterprise Java uses unchecked.
  Frameworks wrap checked exceptions in unchecked (Spring's
  `DataAccessException`). Kotlin and Scala have no checked exceptions.
  Rule: use checked only when the caller can MEANINGFULLY recover.

**Q2: "What is the anti-pattern of swallowing exceptions?
How do you handle exceptions in async/reactive code?"**

*Why they ask:* Common production bug source. Tests real-world experience.

*Strong answer includes:*
- Swallowing: `catch (Exception e) { }` or `catch (Exception e) { log.info("Failed") }`.
  The exception is gone; the operation silently failed.
  System may appear to work but produce wrong results.
- Async/reactive:
  - `CompletableFuture`: exceptions propagate only when
    `.get()` or `.join()` is called. Add `.exceptionally(e -> fallback)`
    to handle in the chain.
  - Spring `@Async` with `void` return: exceptions are
    silently swallowed unless `AsyncUncaughtExceptionHandler`
    is configured.
  - Reactor: subscribe without `onError` handler -> exception
    silently lost. Always provide `onError` or use `doOnError`.

**Q3: "How do you design exception handling across the layers
of a Spring Boot application?"**

*Why they ask:* Architecture question. Tests understanding
of separation of concerns in error handling.

*Strong answer includes:*
- Repository layer: catches infrastructure exceptions
  (DataAccessException), wraps in domain exceptions if needed.
  Or lets Spring's DataAccessException propagate.
- Service layer: throws domain exceptions (`OrderNotFoundException`,
  `PaymentDeclinedException`). Does NOT know about HTTP.
  Does NOT catch to silently continue.
- Controller/`@ControllerAdvice`: catches domain exceptions,
  maps to HTTP status codes and error response bodies.
  Only layer that knows about HTTP.
- Key rules: (1) always preserve cause chain in wrapping,
  (2) never expose internal exception details in API responses,
  (3) log at the boundary with full stack trace,
  (4) use a global catch-all for unexpected exceptions (HTTP 500).
