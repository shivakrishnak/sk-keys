---
layout: default
title: "Scoped Values"
parent: "Java Concurrency"
nav_order: 366
permalink: /java-concurrency/scoped-values/
number: "0366"
category: Java Concurrency
difficulty: ★★★
depends_on: ThreadLocal, Virtual Threads, Structured Concurrency
used_by: Request Context, Security Context, Trace Propagation, Configuration
related: ThreadLocal, Structured Concurrency, Virtual Threads, MDC (Logging)
tags:
  - concurrency
  - java
  - scoped-values
  - context
  - loom
  - advanced
---

# 366 — Scoped Values

⚡ TL;DR — Scoped Values provide immutable, inheritable per-thread context that is automatically propagated to child tasks in Structured Concurrency and automatically removed when the scope exits — replacing `ThreadLocal` for modern concurrent Java.

| #0366           | Category: Java Concurrency                                          | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | ThreadLocal, Virtual Threads, Structured Concurrency                |                 |
| **Used by:**    | Request Context, Security Context, Trace Propagation, Configuration |                 |
| **Related:**    | ThreadLocal, Structured Concurrency, Virtual Threads, MDC (Logging) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A web request arrives. You store the authenticated `User` in a `ThreadLocal<User>`. The user context needs to be available deep in the call stack — in a DAO, a service, a utility — without passing it through every method signature. This works for synchronous, single-thread-per-request servers. Problems: (1) With virtual threads or `CompletableFuture`, child tasks run on different threads and don't inherit the `ThreadLocal`. (2) `ThreadLocal` values leak if not explicitly removed — causing stale context across pooled thread reuse. (3) Mutable `ThreadLocal` values can be accidentally modified deep in the call stack, corrupting context invisibly.

**THE BREAKING POINT:**
As Java moves to virtual threads and Structured Concurrency with millions of concurrent tasks, `ThreadLocal`'s thread-per-value semantics break down: virtual threads are too numerous to maintain per-thread storage efficiently. And `ThreadLocal`'s mutability makes it a source of subtle context corruption bugs.

**THE INVENTION MOMENT:**
Scoped Values (JEP 446, Java 21 preview; stable Java 25+) introduce a new model: immutable values bound to a specific execution scope. The value is visible to any code running within the scope (including child tasks in Structured Concurrency), and automatically unbound when the scope exits. No cleanup needed. No mutation possible. Propagation to child tasks is automatic and correct.

---

### 📘 Textbook Definition

A **Scoped Value** (`java.lang.ScopedValue`) is an immutable, inheritable per-scope variable introduced in Java 21. Unlike `ThreadLocal`, it is: (1) **immutable within a scope** — no `set()` method; (2) **automatically bounded** — value is only visible within the `ScopedValue.where(sv, value).run(() -> ...)` block; (3) **automatically propagated** to tasks forked within a `StructuredTaskScope`; (4) **efficient with virtual threads** — stored in the task frame, not in thread-local storage. Nested scopes can shadow outer values: inner `where()` bindings override outer ones for the duration of the inner block. `ScopedValue.get()` retrieves the current bound value; throws `NoSuchElementException` if unbound.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Scoped Values are immutable context variables that are visible anywhere within a defined execution scope and automatically cleaned up when the scope exits.

**One analogy:**

> Scoped Values are like a backstage badge at a concert. When you enter the backstage area (scope), you're issued a badge (value binding). Everyone in the backstage that evening — crew, artists, guests (child tasks) — can see and verify your badge. When the concert ends (scope exits), all badges are automatically collected. Nobody can modify a badge while they hold it. It only exists during the event.

**One insight:**
The immutability constraint is not a limitation — it's the design. Immutable context is safe to share with all child tasks without defensive copying. Mutable `ThreadLocal` requires careful reasoning about which thread modified it; immutable `ScopedValue` requires no such reasoning.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `ScopedValue<T>` is a static final handle — it names the variable without holding a value.
2. `ScopedValue.where(sv, value)` creates a binding; `.run(...)` executes the body with that binding.
3. Within the body: `sv.get()` returns `value`.
4. On body exit: binding removed automatically.
5. Child tasks forked in `StructuredTaskScope` inherit all current ScopedValue bindings.
6. No `set()` method — values are immutable per scope.

**DERIVED DESIGN:**

```java
// Declaration (static, like a handle):
public static final ScopedValue<User> CURRENT_USER =
    ScopedValue.newInstance();

// Binding (in request handler):
ScopedValue.where(CURRENT_USER, user).run(() -> {
    orderService.process(orderId); // can call sv.get() here
    // Child tasks in StructuredTaskScope inherit this binding
});
// After run(): CURRENT_USER.isBound() == false

// Retrieval (anywhere in the scope):
User user = CURRENT_USER.get();   // never null if bound
User user = CURRENT_USER.orElse(User.GUEST); // safe default

// Nested scope (shadow outer value):
ScopedValue.where(CURRENT_USER, adminUser).run(() -> {
    // This nested scope overrides outer binding
    // CURRENT_USER.get() == adminUser here
});
// Outer scope restored after nested run() exits
```

```
PROPAGATION TO CHILD TASKS:
┌─────────────────────────────────────────────────────────┐
│  ScopedValue.where(USER, alice).run(() -> {             │
│    try (var scope =                                     │
│         new StructuredTaskScope.ShutdownOnFailure()) {  │
│      scope.fork(() -> {                                 │
│        USER.get() == alice ← inherited automatically    │
│      });                                                │
│      scope.fork(() -> {                                 │
│        USER.get() == alice ← same binding, read-only   │
│      });                                                │
│      scope.join().throwIfFailed();                      │
│    }                                                    │
│  });                                                    │
└─────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

- **Gain:** No cleanup bugs; immutable = thread-safe; efficient with virtual threads; propagates automatically to child tasks.
- **Cost:** No mutation (by design — but you might genuinely need mutable context); preview API (Java 21-24); can't be used as drop-in `ThreadLocal` replacement if mutation is required.

---

### 🧪 Thought Experiment

**SETUP:**
A request handler uses `MDC.put("traceId", id)` (Logback/MDC uses `ThreadLocal`). The handler fans out to 10 parallel DB queries via Structured Concurrency. You need the traceId in all 10 DB queries' log lines.

**WITHOUT Scoped Values (ThreadLocal + virtual threads):**
`MDC.put("traceId", id)` sets the ThreadLocal for the request thread. When `scope.fork()` creates child virtual threads, they don't automatically inherit the parent's MDC (it's a ThreadLocal — each thread has its own). The DB query logs have no traceId. You must manually copy MDC into each child thread's context — boilerplate, and easy to forget.

**WITH Scoped Values:**

```java
static final ScopedValue<String> TRACE_ID = ScopedValue.newInstance();

ScopedValue.where(TRACE_ID, traceId).run(() -> {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        for (String query : queries) {
            scope.fork(() -> {
                log.info("traceId={}", TRACE_ID.get()); // inherited!
                return db.execute(query);
            });
        }
        scope.join().throwIfFailed();
    }
});
```

All 10 forks automatically inherit `TRACE_ID`. No manual propagation. No cleanup needed.

**THE INSIGHT:**
Scoped Values and Structured Concurrency are designed together: SC defines the task lifetime, Scoped Values automatically propagate context through that lifetime. They are complementary, not competing.

---

### 🧠 Mental Model / Analogy

> Scoped Values are like a sealed envelope passed to every participant in a meeting. At the meeting's start (scope entry), everyone receives the same sealed envelope (binding). They can open and read it (get()) but not modify its contents. When the meeting ends (scope exit), all envelopes are automatically collected. Sub-meetings (nested scopes) can issue a different sealed envelope that overrides the outer one for that sub-meeting only. Nobody forgets to return their envelope — it's automatic.

- "Sealed envelope" → immutable ScopedValue binding
- "Opening and reading" → `sv.get()`
- "Cannot modify contents" → no `set()` method
- "Meeting ends: envelope collected" → automatic unbinding on scope exit
- "Sub-meeting with different envelope" → nested `ScopedValue.where(sv, newVal).run()`

Where this analogy breaks down: unlike real envelopes, Scoped Values are not copied to each thread — they're stored in a single location and accessed via a lookup chain, which is why they're more efficient than ThreadLocal for virtual threads.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Scoped Values let you share read-only information — like a logged-in user or a trace ID — with all code running within a specific block, including parallel tasks. The information is automatically removed when the block ends. No cleanup code needed.

**Level 2 — How to use it (junior developer):**
Declare: `public static final ScopedValue<User> USER = ScopedValue.newInstance()`. Bind: `ScopedValue.where(USER, user).run(() -> { doWork(); })`. Read anywhere in `doWork()`: `USER.get()`. Never call `set()` — it doesn't exist. If you need a different value in a nested call, use a nested `ScopedValue.where(USER, differentUser).run(...)` — it automatically restores the outer value on exit.

**Level 3 — How it works (mid-level engineer):**
Internally, bindings are stored in a stack-like snapshot of the scope's carrier thread, or in the virtual thread's frame. `ScopedValue.get()` walks the bindings chain from the innermost (most nested `where()`) outward. Binding snapshots are inherited by child tasks in `StructuredTaskScope.fork()` by copying the current binding snapshot to the new task's execution context. Unlike `ThreadLocal` (which stores per-thread mutable slots), ScopedValue bindings are immutable once created and are referenced via an efficient inheritance chain — O(depth) lookup where depth is the nesting level of `where()` calls.

**Level 4 — Why it was designed this way (senior/staff):**
`ThreadLocal` has O(1) access but requires per-thread storage slots — problematic at millions of virtual threads. ScopedValue trades O(depth) access for storage that scales with scope nesting, not thread count. The immutability invariant solves a class of bugs unique to `ThreadLocal`: accidental mutation by deep callee code corrupts context for the caller. The JEP explicitly notes that `ThreadLocal` cannot be safely retrofitted with these semantics — a new API was required. The propagation to forked tasks was designed specifically to integrate with `StructuredTaskScope`, completing the Loom concurrency model: Virtual Threads for scalability, Structured Concurrency for task lifetime, Scoped Values for context propagation.

---

### ⚙️ How It Works (Mechanism)

```
SCOPED VALUE BINDING CHAIN:
Thread execution frame:
┌──────────────────────────────────────────────────────────┐
│ Scope Level 3: USER=charlie, LOCALE=FR                   │
├──────────────────────────────────────────────────────────┤
│ Scope Level 2: USER=bob                                  │
├──────────────────────────────────────────────────────────┤
│ Scope Level 1: USER=alice, TRACE_ID=abc123               │
└──────────────────────────────────────────────────────────┘

USER.get() at Level 3: walks chain → finds charlie (level 3)
USER.get() at Level 2: walks chain → finds bob (level 2)
TRACE_ID.get() at Level 3: walks chain → finds abc123 (level 1)
LOCALE.get() at Level 1: walks chain → not found → NoSuchElementException

CHILD TASK INHERITS SNAPSHOT OF BINDINGS AT FORK TIME:
ScopedValue.where(USER, alice).run(() -> {
    // Binding snapshot: {USER=alice}
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        scope.fork(() -> {
            // Fork inherits snapshot: {USER=alice}
            USER.get() == alice ✓
            // Can nest: ScopedValue.where(USER, bob).run(...)
            // → creates local override without affecting parent
        });
        scope.join();
    }
});
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (request handling with trace propagation):
HTTP request arrives → traceId extracted from header
→ ScopedValue.where(TRACE_ID, traceId).run(() → {
    [Scoped Value binding in effect ← YOU ARE HERE]
→ Handler fans out to parallel DB calls via StructuredTaskScope
→ Each fork inherits TRACE_ID binding automatically
→ All DB query logs include traceId
→ run() exits → binding automatically removed
→ Thread returned to pool with NO residual context

FAILURE PATH:
ThreadLocal MDC not inherited by virtual thread forks
→ Child tasks log without traceId
→ Log correlation impossible
→ Observable: missing traceId fields in child task logs
→ Fix: replace ThreadLocal MDC with ScopedValue or
       use a logging framework that supports ScopedValue propagation

WHAT CHANGES AT SCALE:
With millions of virtual threads, ThreadLocal storage must
be maintained per thread (O(threads) memory). ScopedValue
bindings are stored in the execution frame (scope depth O(depth)),
scaling independently of thread count — critical for
1,000,000+ virtual thread workloads.
```

---

### 💻 Code Example

```java
// Example 1 — Security context propagation
// Declaration (static final handle — never holds a value)
public static final ScopedValue<SecurityContext> SEC_CTX =
    ScopedValue.newInstance();

// In authentication filter:
ScopedValue.where(SEC_CTX, buildContext(request)).run(() ->
    handler.handle(request, response)
);

// Deep in call stack — no parameter passing needed:
SecurityContext ctx = SEC_CTX.get(); // automatically available
boolean canWrite = ctx.hasPermission(WRITE);

// Example 2 — Multiple bindings in one call
ScopedValue
    .where(TRACE_ID, "req-123")
    .where(TENANT_ID, "acme")
    .run(() -> {
        processRequest(); // both values available here
    });

// Example 3 — Nested scope shadows outer value
ScopedValue.where(USER, regularUser).run(() -> {
    // USER.get() == regularUser
    doUserWork();

    // Temporarily elevate to admin for one operation:
    ScopedValue.where(USER, adminUser).run(() -> {
        // USER.get() == adminUser (shadow)
        performAdminOp();
    });
    // Back to regularUser automatically
    // USER.get() == regularUser again
});

// Example 4 — WRONG: ThreadLocal doesn't propagate to fork
// BAD
ThreadLocal<String> TL = new ThreadLocal<>();
TL.set("request-123");
executor.submit(() -> {
    TL.get() // null — different thread!
});

// GOOD: ScopedValue propagates automatically
ScopedValue<String> SV = ScopedValue.newInstance();
ScopedValue.where(SV, "request-123").run(() -> {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        scope.fork(() -> SV.get()); // "request-123" inherited!
        scope.join().throwIfFailed();
    }
});
```

---

### ⚖️ Comparison Table

| Feature                 | ThreadLocal              | ScopedValue               | MDC (Logback) |
| ----------------------- | ------------------------ | ------------------------- | ------------- |
| Mutability              | Mutable                  | Immutable                 | Mutable       |
| Cleanup required        | Yes (remove())           | No (automatic)            | Yes (clear()) |
| Child task propagation  | No (new thread)          | Yes (forked tasks)        | No            |
| Virtual thread friendly | Poor (memory)            | Yes                       | Poor          |
| Nested override         | No                       | Yes (shadow)              | Yes           |
| Best for                | Mutable per-thread state | Immutable request context | Log metadata  |

**How to choose:** Prefer `ScopedValue` for any new Java 21+ code using Virtual Threads or Structured Concurrency. Keep `ThreadLocal` only where mutation of the context is genuinely required (rare). For logging, check if your framework supports ScopedValue natively or create a bridge.

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ScopedValue is just a renamed ThreadLocal             | ThreadLocal is mutable and per-thread; ScopedValue is immutable and per-scope. The semantics are fundamentally different — ScopedValue was a new API, not a rename        |
| ScopedValue.get() works anywhere in the JVM           | ScopedValue.get() throws NoSuchElementException if called outside a binding scope. Always check isBound() or use orElse() for safe access                                 |
| All threads created in a scope inherit ScopedValue    | Only tasks forked via StructuredTaskScope.fork() automatically inherit bindings. Threads created manually (new Thread()) do NOT inherit unless explicitly propagated      |
| Nested ScopedValue.where() modifies the outer binding | Nesting creates a shadow binding visible only within the inner run(). The outer binding is fully restored when the inner run() exits. The outer binding is never modified |

---

### 🚨 Failure Modes & Diagnosis

**Missing Context in Child Tasks (ThreadLocal used with Virtual Threads)**

**Symptom:** Log lines in parallel tasks lack traceId/userId; NPE when calling `sv.get()` in forked tasks.

**Root Cause:** Using `ThreadLocal` for context; child virtual threads don't inherit parent's ThreadLocal values.

**Diagnostic Command:**

```java
// Instrument to detect missing context:
if (!TRACE_ID.isBound()) {
    log.warn("TRACE_ID not bound — context propagation missing");
    // Capture thread dump to trace call site:
    Arrays.stream(Thread.currentThread().getStackTrace())
          .forEach(e -> log.debug(" at {}", e));
}
```

**Fix:** Migrate from `ThreadLocal` to `ScopedValue` for request context. Use `ScopedValue.where(...).run(...)` at the request boundary.

**Prevention:** Establish architectural rule: no `ThreadLocal` for request-scoped context in new code using Virtual Threads.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ThreadLocal` — the mechanism ScopedValue replaces; understand its limitations first
- `Virtual Threads` — the concurrency model that motivated ScopedValue's creation
- `Structured Concurrency` — the scoping model that ScopedValue propagates through

**Builds On This (learn these next):**

- `Project Loom` — the overall JDK project delivering Virtual Threads + SC + ScopedValues together
- `MDC (Mapped Diagnostic Context)` — logging framework's context propagation; integrate with ScopedValue

**Alternatives / Comparisons:**

- `ThreadLocal` — mutable, requires cleanup, doesn't propagate to child threads; use for genuinely mutable per-thread state
- `Baggage (OpenTelemetry)` — distributed tracing context propagation across service boundaries

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Immutable, inheritable per-scope          │
│              │ context variable bound to execution scope │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ ThreadLocal doesn't propagate to child    │
│ SOLVES       │ tasks; mutable context causes bugs        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Immutability makes context propagation    │
│              │ to child tasks trivially safe             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Request context, trace IDs, security      │
│              │ context with Virtual Threads / SC         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Mutable per-thread state genuinely needed │
│              │ (ThreadLocal); Java < 21                  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Clean propagation + immutability vs no    │
│              │ ability to mutate context mid-scope       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A sealed envelope passed to every task   │
│              │  — readable by all, modifiable by none"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ThreadLocal → Structured Concurrency →    │
│              │ Virtual Threads                           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** ScopedValue uses an inheritance chain (not per-thread slots) for storage. Each `ScopedValue.where(...).run(...)` level adds one entry to the chain. Retrieval is O(depth) where depth is nesting level. If a deep application framework nests 20 layers of middleware wrappers, each adding ScopedValue bindings, what is the performance implication of 20-level chain lookups at 1,000,000 requests/second — and what design decision could reduce lookup to O(1) at the cost of binding flexibility?

**Q2.** ScopedValue forbids mutation within a scope, but a common pattern is "accumulating context" — e.g., adding items to a request-scoped list as the call stack deepens. Describe two idiomatic ways to achieve mutable-accumulation semantics within the constraints of ScopedValue (hint: consider what type you bind — an immutable value or a mutable container), and explain which approach is safer in a concurrent context with parallel forked tasks.
