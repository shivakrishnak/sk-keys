---
layout: default
title: "Java Exception Hierarchy (Checked vs Unchecked)"
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /java/java-exception-hierarchy/
id: JLG-010
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Java Language, JVM
used_by: Spring Core, Testing, Java Language
related: Error Handling, Circuit Breaker, Logging
tags:
  - java
  - jvm
  - intermediate
  - foundational
---

# JLG-010 - Java Exception Hierarchy (Checked vs Unchecked)

⚡ TL;DR - Java's exception hierarchy distinguishes recoverable checked exceptions (compiler-enforced) from programming-error unchecked exceptions (optional handling).

| Attribute | Value |
|---|---|
| **Depends on** | Java Language, JVM |
| **Used by** | Spring Core, Testing, Java Language |
| **Related** | Error Handling, Circuit Breaker, Logging |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Early languages used return codes (`-1`, `null`, `errno`) to signal failure. Callers ignored them silently. A file-not-found condition was indistinguishable from a network timeout. Error-handling code was scattered, duplicated, and routinely skipped.

**THE BREAKING POINT:** When a called method can fail in multiple ways, the caller must know which failures are recoverable and which are fatal - but return codes carry no semantic type. Teams built ad-hoc conventions that broke across library boundaries.

**THE INVENTION MOMENT:** Java formalised exception handling with a typed class hierarchy rooted at `Throwable`, separating recoverable conditions (`Exception`), programming errors (`RuntimeException`), and JVM-level fatal conditions (`Error`). The compiler enforces handling of recoverable conditions at compile time via checked exceptions.

---

### 📘 Textbook Definition

**Java's exception hierarchy** is a class tree rooted at `java.lang.Throwable`, split into `Error` (unrecoverable JVM conditions), `Exception` (application-level failures), and `RuntimeException` (unchecked programming errors that are a subtype of `Exception`). Checked exceptions must be declared in the method signature via `throws` or caught in a `try-catch` block. Unchecked exceptions (`RuntimeException` and its subclasses) require no declaration; they propagate up the call stack until caught or the thread terminates.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Checked = the compiler makes you handle it; unchecked = you choose to handle it; Error = don't touch it.

> A hospital triage system: checked exceptions are conditions patients can survive with treatment (you must handle them), unchecked exceptions are self-inflicted injuries from poor decisions (bugs you shouldn't have made), and Errors are the building collapsing (nothing you can do in application code).

**One insight:** Checked exceptions are a contract: the method is telling you "this can fail in a recoverable way, and I am forcing you to decide what to do about it right now."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. All exceptions are objects - they carry a message, a cause chain, and a full stack trace
2. `Throwable` is the root; only `Throwable` subclasses can be thrown or caught
3. `Error` subclasses represent JVM/system failures - do not catch them in application code
4. Checked exceptions extend `Exception` but NOT `RuntimeException` - compiler tracks them
5. Unchecked exceptions extend `RuntimeException` - no compiler enforcement

**DERIVED DESIGN:** The compiler statically analyses every `throws` declaration and every `try-catch`. This creates a propagation-tracking mechanism at compile time for checked exceptions. Unchecked exceptions bypass this tracking, keeping code clean for programming errors that should never occur in correct code (`NullPointerException`, `ArrayIndexOutOfBoundsException`).

**THE TRADE-OFFS:**
- **Gain:** Checked exceptions make failure modes part of the API contract; clients cannot silently ignore recoverable errors
- **Cost:** Checked exceptions spread `throws` declarations through call stacks; they create friction when crossing abstraction boundaries, leading to anti-patterns like `catch (Exception e) {}`

---

### 🧪 Thought Experiment

**SETUP:** You write a method that reads a configuration file on startup.

**WHAT HAPPENS WITHOUT CHECKED EXCEPTIONS:** The method returns `null` on failure. The caller forgets to check. Three layers up, a `NullPointerException` throws with no indication that the config file was missing. The failure is silent, late, and the stack trace is misleading.

**WHAT HAPPENS WITH CHECKED EXCEPTIONS:** The method declares `throws IOException`. The compiler forces every caller to either catch the exception or propagate it with `throws IOException`. The failure is explicit, early, and the exception message names the missing file path.

**THE INSIGHT:** Checked exceptions move error-handling decisions from runtime surprises to compile-time design choices. The tension is that overzealous use pollutes APIs - the modern consensus is: use checked for recoverable I/O-style errors, unchecked for programming errors, and `RuntimeException` wrappers when crossing architecture layers.

---

### 🧠 Mental Model / Analogy

> Think of exception handling like an airline's baggage system. Checked exceptions are oversized bags - the counter agent (compiler) won't let you board without acknowledging them (catch or declare). Unchecked exceptions are prohibited items - you should have known not to pack them (bugs); security only finds them at runtime. `Error`s are the plane itself malfunctioning - no passenger procedure handles that.

- Checked exception → oversized bag: acknowledged at check-in (compile time)
- Unchecked `RuntimeException` → prohibited item: discovered at screening (runtime)
- `Error` → aircraft failure: outside passenger control; escalates to ground crew (JVM/OS)
- `finally` block → customs clearance: always happens regardless of outcome

Where this analogy breaks down: bags are resolved at a single checkpoint, but exceptions propagate up many call frames before being caught.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When something goes wrong in a Java program, the JVM throws an object describing the problem. Checked exceptions are those the compiler forces you to handle; unchecked ones you can ignore (but usually shouldn't).

**Level 2 - How to use it (junior developer):**
Wrap risky code in `try-catch`. Catch specific exceptions before general ones. Always log or rethrow; never swallow silently. Declare `throws IOException` (or other checked types) in method signatures when you can't handle the exception at that layer. Use `finally` or try-with-resources for cleanup.

**Level 3 - How it works (mid-level engineer):**
The JVM maintains an exception table per method in the bytecode. When a `throw` executes, the JVM walks the exception table for the current method looking for a matching handler type (using `instanceof` semantics). If none found, it unwinds the call stack frame by frame. Stack unwinding invokes `finally` blocks at each level. The full stack trace is captured at throw time via `fillInStackTrace()`, which is expensive - this is why re-throwing a caught exception with `new` is costlier than rethrowing the original.

**Level 4 - Why it was designed this way (senior/staff):**
James Gosling introduced checked exceptions as a forced-documentation mechanism: the method signature becomes a partial contract. The controversy is whether this achieves its goal. In practice, developers wrap checked exceptions in `RuntimeException` to escape compiler enforcement, defeating the purpose. Modern Java (post-2004) frameworks (Spring, Hibernate) largely converted checked to unchecked to reduce boilerplate. Kotlin and Scala removed checked exceptions entirely. The JVM still supports the concept - but the community consensus has shifted toward unchecked exceptions with good documentation.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│           Throwable                         │
│               │                             │
│       ┌───────┴────────┐                    │
│     Error           Exception               │
│       │                 │                   │
│  OutOfMemoryError   ┌───┴────────────────┐  │
│  StackOverflowError │                    │  │
│  AssertionError  RuntimeException  IOException│
│                      │             SQLException
│                 NullPointerException    etc. │
│                 IllegalArgumentException     │
│                 IndexOutOfBoundsException    │
│                 ClassCastException           │
└─────────────────────────────────────────────┘
```

**Exception propagation path:**
```
method3() throws
      ↑ unwind (finally runs)
method2() - no handler found
      ↑ unwind (finally runs)
method1() - catch(IOException e) → CAUGHT
```

Key JVM steps:
1. `throw e` executes → JVM searches current method's exception table
2. Match found → jump to handler; match fails → pop stack frame
3. `finally` block runs on every frame pop (matched or not)
4. Reaches thread's `run()` with no handler → `ThreadGroup.uncaughtException()`

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Client calls readConfig("app.properties")
  │         ← YOU ARE HERE (calling method)
  │
  ├─ FileInputStream("app.properties")
  │      → file found → stream opened
  │
  ├─ read bytes → parse → return Config
  │
  └─ try-with-resources closes stream
         (finally equivalent)
```

**FAILURE PATH:**
```
FileInputStream("app.properties")
  → file not found
  → throws FileNotFoundException (checked)
       ↑ propagates to readConfig()
       → wraps in ConfigException (unchecked)
            ↑ propagates to caller
            → logged + fallback to defaults
```

**WHAT CHANGES AT SCALE:**
- Exception creation is expensive (`fillInStackTrace` walks the JVM stack) - avoid throwing in hot loops
- Use `ExceptionUtils.getRootCause()` (Apache Commons) or `Throwable.getCause()` chain for wrapped exceptions
- In distributed systems, exceptions must be serialisable across the wire (REST error bodies, gRPC status codes)

---

### 💻 Code Example

**BAD - swallowed exception, wrong abstraction leak:**
```java
// BAD: swallowing exception - silent failure
public Config loadConfig(String path) {
    try {
        return parseFile(path);
    } catch (IOException e) {
        // Silent swallow - caller never knows
        return null;
    }
}

// BAD: checked exception leaking abstraction
public User findUser(int id)
        throws SQLException {  // exposes DB detail
    return db.query(id);
}
```

**GOOD - wrap, log, translate at boundaries:**
```java
// GOOD: translate at layer boundary
public Config loadConfig(String path) {
    try {
        return parseFile(path);
    } catch (FileNotFoundException e) {
        throw new ConfigNotFoundException(
            "Config not found: " + path, e);
    } catch (IOException e) {
        throw new ConfigLoadException(
            "Failed to read config: " + path, e);
    }
}

// GOOD: hide infrastructure exception from API
public User findUser(int id) {
    try {
        return db.query(id);
    } catch (SQLException e) {
        throw new DataAccessException(
            "User lookup failed for id=" + id, e);
    }
}

// GOOD: try-with-resources for cleanup
public String readFirst(String path)
        throws IOException {
    try (BufferedReader r =
            Files.newBufferedReader(
                Path.of(path))) {
        return r.readLine();
    } // auto-closes even on exception
}

// GOOD: custom exception preserving cause
public class ConfigNotFoundException
        extends RuntimeException {
    public ConfigNotFoundException(
            String msg, Throwable cause) {
        super(msg, cause);
    }
}
```

---

### ⚖️ Comparison Table

| Type | Superclass | Compiler Enforced | Must Declare | Typical Examples | Use For |
|---|---|---|---|---|---|
| Checked Exception | `Exception` | Yes | Yes (`throws`) | `IOException`, `SQLException` | Recoverable external failures |
| Unchecked Exception | `RuntimeException` | No | No | `NullPointerException`, `IllegalArgumentException` | Programming errors, violated preconditions |
| Error | `Error` | No | No | `OutOfMemoryError`, `StackOverflowError` | JVM-level fatal conditions |
| Custom Checked | `Exception` | Yes | Yes | `ConfigNotFoundException` (if checked) | Domain-specific recoverable errors |
| Custom Unchecked | `RuntimeException` | No | No | `DomainException`, `ServiceException` | Domain errors across layer boundaries |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Catching `Exception` handles everything | `Error` is not a subclass of `Exception`; `OutOfMemoryError` and `StackOverflowError` are not caught by `catch (Exception e)` |
| Unchecked exceptions don't need to be documented | They are part of the API contract and must be documented in Javadoc `@throws`; absence of enforcement doesn't mean absence of obligation |
| `finally` always runs | If `System.exit()` is called, or the JVM crashes, `finally` does NOT execute |
| Re-throwing with `throw e` loses the stack trace | `throw e` preserves the original stack trace; only `throw new SomeException()` (without cause) loses it |
| Custom exceptions should extend `Exception` by default | Modern practice prefers `RuntimeException` subclasses; checked exceptions should be reserved for genuinely recoverable, caller-actionable failures |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Silent exception swallowing**

**Symptom:** Feature silently fails; logs show nothing; users report missing data with no error. Debugging is impossible post-hoc.

**Root Cause:** `catch (Exception e) {}` or `catch (Exception e) { return null; }` - the exception is caught but discarded without logging or rethrowing.

**Diagnostic:**
```bash
# Search codebase for empty or null-returning catch blocks
grep -rn "catch.*{" src/ | grep -v "//"
# Use SonarQube rule: "Exception should not be ignored"
```

**Fix:**
```java
// BAD: silent swallow
try {
    process(data);
} catch (Exception e) { }

// GOOD: always log or rethrow
try {
    process(data);
} catch (Exception e) {
    log.error("process failed for data={}", data, e);
    throw new ProcessingException("Failed", e);
}
```

**Prevention:** Enable SonarQube or SpotBugs rule `DE_MIGHT_IGNORE`. Code review checklists must include catch-block inspection.

---

**Mode 2: Exception cause chain lost during wrapping**

**Symptom:** Production logs show `ServiceException: unknown error` with no root cause. The original `SQLException` or `IOException` is invisible, making diagnosis take hours.

**Root Cause:** The original exception is not passed as the `cause` parameter when wrapping: `throw new ServiceException("msg")` instead of `throw new ServiceException("msg", e)`.

**Diagnostic:**
```bash
# In logs, look for exceptions with no "Caused by:" line
grep -A5 "ServiceException" app.log | grep -c "Caused by"
# Zero matches = cause chain broken
```

**Fix:**
```java
// BAD: cause lost
} catch (IOException e) {
    throw new ServiceException("IO failed");
}

// GOOD: always chain the cause
} catch (IOException e) {
    throw new ServiceException(
        "IO failed reading " + path, e);
}
```

**Prevention:** Code review rule: every `throw new XxxException(msg)` in a catch block must include `, e` as the last argument.

---

**Mode 3: Catching Error causes JVM instability**

**Symptom:** Application appears to recover from `OutOfMemoryError` but then behaves erratically - corrupted state, subsequent NPEs, missing data.

**Root Cause:** `catch (Throwable t)` or `catch (Error e)` catches JVM-level errors. The JVM's heap state after `OutOfMemoryError` is undefined; objects may be partially initialised.

**Diagnostic:**
```bash
# Check GC logs and heap dumps for OOM
java -Xmx512m -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/heapdump.hprof MyApp
jmap -histo /tmp/heapdump.hprof | head -20
```

**Fix:**
```java
// BAD: catching Error
try {
    riskyOp();
} catch (Error e) {
    log.warn("recovered from error"); // DANGEROUS
}

// GOOD: let Error propagate; configure JVM restart
// In production: use process supervisors (systemd,
// Kubernetes liveness probes) to restart on OOM
```

**Prevention:** Never catch `Error` or `Throwable` in application logic. Use `-XX:+ExitOnOutOfMemoryError` to fail fast and let the orchestrator restart cleanly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Java Language - method signatures, `try-catch-finally` syntax
- JVM - stack frames, bytecode exception tables, stack unwinding

**Builds On This (learn these next):**
- Spring Core - `@ExceptionHandler`, `@ControllerAdvice`, Spring's `DataAccessException` hierarchy
- Testing - asserting thrown exceptions with JUnit 5 `assertThrows`
- Logging - structured logging of exception cause chains

**Alternatives / Comparisons:**
- Error Handling (functional) - `Optional`, `Either`, `Result` types avoid exceptions for expected failures
- Circuit Breaker - handles repeated downstream failures without exception-per-call overhead
- Logging - exception context must be captured before rethrowing or the window is lost

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════════════╗
║ WHAT IT IS   │ Typed failure signal class hierarchy║
║ PROBLEM      │ Silent failures, unhandled errors   ║
║ KEY INSIGHT  │ Checked = compiler contract;        ║
║              │ Unchecked = programmer error        ║
║ USE WHEN     │ Checked: recoverable external fail  ║
║              │ Unchecked: precondition violation   ║
║ AVOID WHEN   │ Checked across architecture layers  ║
║ TRADE-OFF    │ Safety vs boilerplate verbosity     ║
║ ONE-LINER    │ throw new XxxException(msg, cause)  ║
║ NEXT EXPLORE │ Spring @ControllerAdvice, Logging   ║
╚════════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(C - Design Trade-off)** Spring converts all `SQLException` (checked) to `DataAccessException` (unchecked) at the DAO layer. What principle drives this decision, and what are the trade-offs in terms of caller awareness, error recovery, and testability?

2. **(B - Scale)** In a microservice handling 10,000 requests per second, each `new RuntimeException()` call invokes `fillInStackTrace()`, which walks the full JVM stack. Under what conditions does exception creation become a performance bottleneck, and what mechanisms can reduce this cost without sacrificing observability?

3. **(A - System Interaction)** An exception thrown inside a `CompletableFuture` pipeline is wrapped in a `CompletionException`. When the exception crosses a REST API boundary, it becomes an HTTP 500 response. Describe the full translation chain, what information is lost at each step, and how you would preserve enough context for both client error handling and server-side diagnosis.
