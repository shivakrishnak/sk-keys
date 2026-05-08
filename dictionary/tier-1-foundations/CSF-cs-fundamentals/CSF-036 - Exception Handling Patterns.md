---
id: CSF-036
title: Exception Handling Patterns
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - pattern
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /csf/exception-handling-patterns/
---

# CSF-036 - Exception Handling Patterns

⚡ TL;DR - Exception handling patterns define how, where, and at what level to catch, wrap, log, and rethrow exceptions to maintain clean error flow without losing context.

| CSF-036         | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-022, CSF-020, CSF-021             |                 |
| **Used by:**    | CSF-053, CSF-057                      |                 |
| **Related:**    | CSF-022, CSF-035, CSF-049, CSF-053    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without patterns for exception handling, code devolves into
two failure modes: catch-and-swallow (silent failures), or
propagating raw exceptions across layers (exposing internals,
losing context, making stack traces useless).

**THE BREAKING POINT:**
A service catches `Exception` at the top level and logs "an error
occurred" with no stack trace. Or: a `java.sql.SQLException` leaks
out of the repository layer into the REST controller. The first
makes bugs invisible; the second violates layered architecture.

**THE INVENTION MOMENT:**
Enterprise Java patterns formalised exception handling conventions:
translate at layer boundaries, log once, rethrow semantically
rich exceptions. Functional languages formalised it differently:
`Result<T, E>` types that carry success or failure as a value,
eliminating the need for try/catch entirely.

**EVOLUTION:**
Modern patterns: checked exceptions deprecated in favour of
unchecked + Result types; error boundaries in React; global
exception handlers in Spring (`@ControllerAdvice`); resilience
patterns (circuit breakers, retry with backoff) as exception
handling at the system level.

---

### 📘 Textbook Definition

Exception handling patterns are design conventions that determine:
(1) where exceptions are caught; (2) when to rethrow vs handle;
(3) how to translate exceptions at layer boundaries; (4) how
to preserve context when wrapping; and (5) how to ensure
exceptions are logged exactly once. The core principle:
catch exceptions at the level where you can _do something useful
with them_; everywhere else, let them propagate.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Catch exceptions where you can handle them; translate at layer boundaries; log once; never swallow.

**One analogy:**

> Exception handling is like incident escalation in an organisation.
> A junior employee handles what they can; escalates what they can't.
> Each escalation adds context ("here's what I tried"). The top-level
> manager sees a complete picture. Swallowing an exception is like
> never reporting the incident — the problem festers silently.

**One insight:**
The most common exception bug is catching an exception at the
wrong level: too early (before you can meaningfully handle it)
or too late (after the context is gone). The rule: catch where
you can _act on it_.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Catch exceptions only where you can _do something useful_ with them.
2. Translate exceptions at layer boundaries (SQLException → RepositoryException).
3. Log once, at the top — not at every rethrow point.
4. Never silently swallow exceptions (empty catch block).
5. When wrapping, always preserve the original exception as `cause`.

**DERIVED DESIGN:**

- **Let it propagate**: infrastructure code throws; business code catches and handles
- **Translate at boundary**: `catch(SQLExc e) { throw new DataException("...", e); }`
- **Catch and recover**: retry, fallback, circuit break
- **Catch and log**: top-level handler only; then rethrow or return error response
- **Fail fast**: validate preconditions early; throw immediately on invalid state

**THE TRADE-OFFS:**
**Gain:** Clean separation of error paths. Layer abstraction preserved.
Debugging enabled (cause chain preserved).
**Cost:** Requires discipline to apply consistently. Can produce
verbose code without good language support.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Errors happen at different layers and require different handling.
**Accidental:** Duplicate logging, lost cause chains, overly broad catch blocks,
exceptions as flow control.

---

### 🧪 Thought Experiment

**SETUP:**
A REST controller calls a service which calls a repository.
The database throws `PSQLException: connection timeout`.

**WRONG HANDLING (3 anti-patterns):**

```java
// Anti-pattern 1: Swallow
catch (Exception e) { } // silent failure

// Anti-pattern 2: Rethrow raw across layers
// PSQLException leaks into REST layer -- exposes DB details

// Anti-pattern 3: Log at every layer
catch (Exception e) {
    log.error("error", e); // logged here
    throw e; // logged again higher up -- duplicate stack traces
}
```

**CORRECT PATTERN:**

```java
// Repository layer: translate
catch (PSQLException e) {
    throw new DatabaseException("User lookup failed", e); // wrapped, cause preserved
}
// Service layer: let it propagate (can't handle DB issues here)
// Controller layer: catch and respond
catch (DatabaseException e) {
    log.error("Database error processing user request", e); // log ONCE
    return ResponseEntity.status(503).body("Service unavailable");
}
```

**THE INSIGHT:**
Translation preserves layer abstraction. Log once preserves
readability. Cause chain preserves debuggability. All three
rules serve different goals.

---

### 🧠 Mental Model / Analogy

> Exception handling is like sorting mail at each level of
> a large organisation. Mail room handles delivery issues.
> Departmental secretary handles misdirected mail. Executive
> assistant handles anything requiring a response. CEO only
> sees things that genuinely require CEO-level decision.
> Each level translates (rewraps) the issue into their domain
> vocabulary. Nothing gets shredded without acknowledgement.

**Element mapping:**

- Mail = exception
- Handling at your level = catch and resolve
- Escalating with context = `throw new HigherLevelException("context", original)`
- Shredding mail = empty catch block (swallowing)
- CEO alert = top-level exception handler (log + return 500)

Where this analogy breaks down: mail escalation is sequential;
exception propagation unwinds the call stack.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When something goes wrong, you need a plan: fix it here, pass
it up, or tell the user. Exception patterns are the plan.

**Level 2 - How to use it (junior developer):**
Never use empty catch blocks. Always log the full stack trace
(use `log.error("msg", e)` not `log.error(e.getMessage())`)
. Wrap exceptions from lower layers with context. Catch
specific exception types, not `Exception` broadly.

**Level 3 - How it works (mid-level engineer):**
Spring's `@ControllerAdvice` + `@ExceptionHandler` provides a
centralised exception handling strategy for REST controllers.
It catches exceptions from any controller, translates them to
appropriate HTTP responses, and logs them — a clean implementation
of the "catch at the right level" principle.

**Level 4 - Why it was designed this way (senior/staff):**
Rust's `?` operator is the compile-time equivalent of "let it
propagate": it returns `Err(e)` from the current function if
a Result is `Err`. Combined with `map_err` for translation, it
implements the exact same pattern (translate at boundaries,
propagate to a handler) with zero runtime overhead and compile-time
verification that all failure paths are handled.

**Expert Thinking Cues:**

- When reviewing catch blocks: can we actually recover here, or should we rethrow?
- When a method has 5 different catch blocks: is there a common abstraction?
- When seeing duplicate log entries: is the same exception logged multiple times?

---

### ⚙️ How It Works (Mechanism)

**Exception propagation:**

```
repository.find()  -- throws PSQLException
  |-> caught, translated to DatabaseException
  |-> re-thrown
service.getUser()  -- DatabaseException propagates uncaught
controller.handle() -- catches DatabaseException
  |-> logs once (with full cause chain)
  |-> returns HTTP 503
```

**Cause chain preservation:**

```java
// Always include original as cause (second argument)
new DataAccessException("User lookup failed", originalSQLException);
// Result: stack trace shows both new exception AND original cause
// Printed as: DataAccessException: User lookup failed
//   Caused by: PSQLException: connection timeout
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
DB throws PSQLException             ← YOU ARE HERE
  |
Repository catches PSQLException:
  throws new DatabaseException(msg, cause)
  |
Service: DatabaseException propagates (no catch)
  |
Controller catches DatabaseException:
  log.error("...", e) -- logged ONCE with full cause chain
  return 503 response
```

**FAILURE PATH:**

- Empty catch: bug disappears silently
- Raw exception leaks: DB schema details in 500 response
- Log at every level: same stack trace 3 times in logs
- Exception without cause: debugger can't trace origin

---

### ⚖️ Comparison Table

| Pattern               | When to Use                                   | Risk If Overused                        |
| --------------------- | --------------------------------------------- | --------------------------------------- |
| Let it propagate      | Infrastructure errors the caller can't handle | Incorrect abstraction level for handler |
| Translate at boundary | Any layer crossing                            | Verbosity; over-abstracted errors       |
| Catch and recover     | Retry-able, fallback-able errors              | Infinite retry loops                    |
| Catch and log at top  | Final handler (controller/main)               | Duplicate logs if also caught lower     |
| Fail fast             | Programmer errors / violated preconditions    | Too aggressive for expected conditions  |
| Circuit breaker       | Cascading failure prevention                  | False positives, circuit stays open     |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                           |
| ----------------------------------------- | --------------------------------------------------------------------------------- |
| "Log at every catch block"                | Log once at the top; multiple logs mean duplicate stack traces                    |
| "Catching Exception broadly is defensive" | It hides errors; catch specific types you can handle                              |
| "Checked exceptions ensure reliability"   | They led to empty catch blocks; unchecked + Result types are the modern consensus |
| "`e.getMessage()` is sufficient logging"  | Always log the full exception with `log.error("msg", e)` to get the stack trace   |
| "Exceptions are for error handling only"  | Exceptions also carry context for debugging; preserve the cause chain always      |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Exception Swallowing**
**Symptom:** Request returns 200 but operation didn't complete; no error in logs.
**Diagnostic:**

```bash
grep -rn 'catch.*{\s*}' src/
grep -rn 'catch.*e.*}' src/ # single-line empty catches
```

**Fix:** At minimum, log and rethrow; ideally handle or propagate.

**Mode 2: Cause Chain Lost**
**Symptom:** Log shows `DataAccessException` but no SQL error; debugging is impossible.
**Root Cause:** `throw new DataAccessException(msg)` — missing `cause` argument.
**Fix:**

```java
// BAD
throw new DataAccessException(e.getMessage()); // cause lost!

// GOOD
throw new DataAccessException("User lookup failed", e); // cause preserved
```

**Mode 3: Duplicate Log Entries**
**Symptom:** Same stack trace appears 3 times in logs; 3 different log levels.
**Root Cause:** Each layer logs before rethrowing.
**Fix:** Log only at the final handler. Intermediate layers rethrow without logging.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-022 - Error vs Exception]]
- [[CSF-020 - Control Flow (if, loops, switch)]]

**Builds On This (learn these next):**

- [[CSF-053 - Concurrency Anti-Patterns (Shared State)]]
- [[CSF-057 - Memory Safety Vulnerabilities in Language Design]]

**Alternatives / Comparisons:**

- Result types (CSF-022/Rust) — error as a value vs exception
- Circuit breaker pattern — system-level exception handling

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Patterns for where/how to catch,      │
│                 translate, log, and rethrow           │
│ PROBLEM         Swallowed exceptions / leaked          │
│ IT SOLVES       internals / duplicate logs            │
│ KEY INSIGHT     Catch where you can ACT; translate at  │
│                 boundaries; log ONCE; preserve cause  │
│ USE WHEN        Every application layer                │
│ AVOID WHEN      Using exceptions for flow control      │
│ TRADE-OFF       Verbosity vs debuggability             │
│ ONE-LINER       Catch where you can act; translate at  │
│                 boundaries; log once at the top       │
│ NEXT EXPLORE    CSF-022, Spring @ControllerAdvice      │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Catch at the level where you can do something useful; everywhere else, let it propagate.
2. Translate exceptions at layer boundaries; preserve the original as `cause`.
3. Log once at the top; never log at every rethrow point.

**Interview one-liner:**
"Exception handling patterns define where to catch (where you can act), how to translate (at layer boundaries with cause preserved), and where to log (once, at the top-level handler)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Handle errors at the level of abstraction that understands them.
A database driver knows what a connection timeout is; a REST
controller knows what a 503 means; but neither understands
the other's vocabulary. Translation at boundaries is the
engineering discipline that keeps those vocabularies separate.

**Where else this pattern appears:**

- **Kubernetes health probes** — liveness (unrecoverable; restart) vs readiness (temporary; stop traffic)
- **HTTP status codes** — 4xx (client error; don't retry) vs 5xx (server error; retry-able)
- **Domain-Driven Design** — anti-corruption layers translate between bounded context vocabularies

---

### 💡 The Surprising Truth

A 2016 study of 5 distributed systems (Cassandra, HBase, HDFS,
MapReduce, Redis) found that 92% of catastrophic failures were
caused by _incorrect error handling_ — specifically, empty catch
blocks, over-broad catches, or treating all errors as equivalent.
Only 8% were caused by unpredictable hardware failures. The most
common production outages are not caused by unknown bugs; they
are caused by developers catching errors they shouldn't catch,
or not catching errors they should.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A Spring Boot service uses
`@ControllerAdvice` to catch all exceptions. One day, an
exception that _should_ be caught by a specific handler
is caught by the generic `Exception` handler instead,
returning 500 to the client. How do you debug the handler
orderin Spring?

_Hint:_ Research `@ExceptionHandler` handler resolution order
in Spring and how `@Order` or exception hierarchy affects which
handler is selected.

**Q2 (Scale):** In a system handling 10,000 requests/second,
each request throws an exception on average once per 100 requests.
That's 100 exceptions/second, each creating a stack trace
(typically 50+ frames). What is the performance impact, and
what options exist to reduce it?

_Hint:_ Research the cost of `Throwable.fillInStackTrace()` in
Java and when it makes sense to override it. Look at how some
frameworks use pre-allocated exceptions.

**Q3 (Design Trade-off):** Go doesn't have exceptions — all
errors are return values: `func findUser() (User, error)`. Every
caller must check the error return. How does this compare to
Java's propagation model for a large codebase? What does
Go code look like at scale with this pattern?

_Hint:_ Research the "if err != nil" idiom in Go and how
proposals for error handling improvements (try, generics-based
approaches) have been received by the Go community.
