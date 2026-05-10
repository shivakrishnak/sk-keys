---
id: JCC-074
title: Structured Concurrency Theory
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-044, JCC-073, JCC-062
used_on:
related: JCC-041, JCC-032, JCC-059
tags:
  - java
  - concurrency
  - advanced
  - pattern
  - deep-dive
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 74
permalink: /java-concurrency/structured-concurrency-theory/
---

# JCC-074 - STRUCTURED CONCURRENCY THEORY

⚡ **TL;DR** - Structured concurrency imposes tree-shaped lifetime
on concurrent tasks so that errors, cancellations, and results
all flow predictably through parent-child task relationships.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-044 Structured Concurrency, JCC-073 Project Loom Design Rationale, JCC-062 Thread Interruption |
| Related    | JCC-041 CopyOnWriteArrayList, JCC-032 Virtual Threads, JCC-059 CompletableFuture Composition |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`ExecutorService.submit()` creates tasks whose lifetimes are
completely unrelated to the code that submitted them. A task can
outlive its creator, silently consuming resources. If the creator
throws, spawned tasks continue running. If a spawned task fails,
the creator has no automatic notification. This creates *task
leaks* - the distributed equivalent of memory leaks.

**THE BREAKING POINT:**
A request handler spawns three async tasks: fetch user, fetch
orders, fetch inventory. The user fetch fails. The request handler
needs to cancel the other two, but the tasks are already running
in a shared `ExecutorService`. The handler has their `Future`
objects but cancellation is manual, error-prone, and often forgotten
under time pressure. Under 1,000 concurrent requests, leaked tasks
accumulate and exhaust the pool.

**THE INVENTION MOMENT:**
Martin Sustrik (ZeroMQ author) and Nathaniel J. Smith described
the "structured concurrency" concept in 2018: concurrent tasks
must follow the same nesting principle as structured code. Just as
`if/for/try` blocks must be exited before the caller moves on,
concurrent tasks spawned in a scope must complete before that scope
exits. This mirrors how `goto` was eliminated by structured
programming.

**EVOLUTION:**
- **2018:** Sustrik and Smith publish structured concurrency essays
- **Java 19-20:** `StructuredTaskScope` as Preview (JEP 428, 437)
- **Java 21:** Second preview (JEP 453)
- **Java 24+:** Moving toward finalisation
- **Kotlin:** `coroutineScope {}` implements structured concurrency
- **Swift:** `async let` and `TaskGroup` implement the same concept

---

### 📘 Textbook Definition

**Structured Concurrency** is the principle that concurrent tasks
must have a *tree-shaped lifetime structure* - child tasks cannot
outlive their parent scope. In Java, `StructuredTaskScope` enforces
this:

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User>  userTask   = scope.fork(() -> getUser(id));
    Subtask<Order> orderTask  = scope.fork(() -> getOrder(id));

    scope.join();          // wait for all forks
    scope.throwIfFailed(); // propagate first failure

    return merge(userTask.get(), orderTask.get());
}
// Scope close: ALL tasks GUARANTEED complete/cancelled
```

**Built-in policies:**
- `ShutdownOnFailure`: cancel siblings when first fails
- `ShutdownOnSuccess`: cancel siblings when first succeeds (race)

---

### ⏱️ Understand It in 30 Seconds

**One line:** Child tasks live and die within their parent's
scope - no outliving, no leaks, no silent failures.

**One analogy:**
> Structured concurrency is to concurrent tasks what lexical scoping
> is to variables. A variable declared inside a function cannot
> outlive the function. A task forked inside a scope cannot outlive
> the scope. The rule is enforced by the language/runtime, not
> discipline.

**One insight:** The analogy to structured programming (`goto`
elimination) is exact. Unstructured concurrency is `goto` for
threads - execution can jump anywhere and never return. Structured
concurrency makes task flow predictable and locally reasoned.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A `StructuredTaskScope` is a *parent scope*. All tasks forked
   within it are *child tasks*.
2. `scope.join()` blocks until ALL child tasks complete (success,
   failure, or cancellation).
3. When the scope closes (exits the `try` block), all child tasks
   are guaranteed to be done. No child outlives its scope.
4. If a child fails and the policy is `ShutdownOnFailure`, all
   siblings are interrupted immediately.
5. Errors propagate upward: the scope's parent sees the failure
   as if the scope itself failed.

**DERIVED DESIGN:**
Structured concurrency requires virtual threads - platform threads
are too heavy to create per-task. The combination of VTs (cheap
creation) + structured scopes (lifetime management) enables the
Go-style `go func() {}` pattern safely in Java.

**THE TRADE-OFFS:**

**Gain:** No task leaks; automatic cancellation propagation;
clear ownership of results; full call-stack observability; errors
never silently lost.

**Cost:** Tasks must complete before scope exits - cannot fire-and-
forget. Long-running background tasks need different patterns.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any concurrent system needs policy for: what happens
when one task fails? What if the scope is cancelled? Who owns the
result? Structured concurrency makes these policies explicit and
automatic.

**Accidental:** `StructuredTaskScope` is still a Preview API (Java
24). The API may change. Production use requires `--enable-preview`.

---

### 🧪 Thought Experiment

**SETUP:** Fetch user AND order concurrently; return both or fail
fast if either fails.

**WITHOUT structured concurrency:**
```java
ExecutorService exec = Executors.newVirtualThreadPerTaskExecutor();
Future<User>  uf = exec.submit(() -> getUser(id));
Future<Order> of = exec.submit(() -> getOrder(id));
try {
    User u = uf.get();   // blocks
    Order o = of.get();  // blocks after user done
    return merge(u, o);
} catch (ExecutionException e) {
    uf.cancel(true);     // often forgotten
    of.cancel(true);     // often forgotten
    throw new RuntimeException(e.getCause());
}
// If exception in getUser: does getOrder still run? YES - LEAK
```

**WITH structured concurrency (ShutdownOnFailure):**
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var uf = scope.fork(() -> getUser(id));
    var of = scope.fork(() -> getOrder(id));
    scope.join().throwIfFailed();
    return merge(uf.get(), of.get());
}
// If getUser fails: getOrder AUTOMATICALLY cancelled.
// No manual cancel. No leak. Guaranteed.
```

**THE INSIGHT:** With structured concurrency, the compiler (via
`try-with-resources`) enforces cancellation. Human discipline is
not required.

---

### 🧠 Mental Model / Analogy

> Think of a function call tree. When `A()` calls `B()` which
> calls `C()`, C cannot return after A. The call stack enforces
> this. Structured concurrency applies the same rule to parallel
> calls: when `scope()` forks `B()` and `C()`, neither can outlive
> scope. The scope is the call tree node; forks are the children.

**Element mapping:**
- Function call = `scope.fork(task)`
- Return from function = task completion
- Call stack frame = `StructuredTaskScope`
- Stack frame exits = scope closes (all tasks done)
- Exception propagation = `scope.throwIfFailed()`
- Unchecked exception crashing the call = `ShutdownOnFailure`

Where this analogy breaks down: sequential call trees are naturally
ordered; concurrent forks have no order, which is the whole point.
The key structural rule is lifetime, not order.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you spawn concurrent tasks inside a block of code, the block
guarantees that all tasks finish before it exits - automatically,
with no code to write.

**Level 2 - How to use it (junior developer):**
```java
// Race two services - return whichever responds first
try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
    scope.fork(() -> callServiceA());
    scope.fork(() -> callServiceB());

    scope.join();
    return scope.result(); // result of whichever succeeded first
} // other fork automatically cancelled
```

**Level 3 - How it works (mid-level engineer):**
`StructuredTaskScope` tracks all forked `Subtask` objects in an
internal list. Each fork creates a virtual thread. `join()` calls
`join()` on every child VT. When a child completes (success or
failure), the scope's policy function is called. For `ShutdownOnFailure`,
the policy calls `shutdown()` which interrupts all remaining
child virtual threads. `close()` (from `AutoCloseable`) blocks
until all children complete after shutdown.

**Level 4 - Why it was designed this way (senior/staff):**
The JEP authors consciously applied the structural rule from
Dijkstra's structured programming: control flow must be hierarchical.
The `fork/join` metaphor is intentional but distinct from
`ForkJoinPool` - it is about lifetime structure, not work-stealing.
The decision to use `try-with-resources` leverages existing Java
syntax to enforce the scope boundary without new keywords (unlike
Kotlin's `coroutineScope {}` or Swift's `async let`).

**Expert Thinking Cues:**
- `ShutdownOnFailure` is for "all must succeed" fan-out (call
  multiple services, need all results).
- `ShutdownOnSuccess` is for "first wins" hedged requests (call
  primary and backup, take whichever responds first).
- Custom policies: extend `StructuredTaskScope` and override
  `handleComplete()` to implement custom fan-out logic.
- Scopes can be nested: a child scope can fork its own sub-tasks.
  The lifetime rule applies recursively.

---

### ⚙️ How It Works (Mechanism)

**StructuredTaskScope lifecycle:**
```
new StructuredTaskScope()
  |
fork(task1): create VT, start, track in internal list
fork(task2): create VT, start, track in internal list
  |
join():
  wait for all VTs to finish
  (or wait for shutdown() to be called + all finish)
  |
[ShutdownOnFailure]: task fails -> shutdown() -> interrupt others
[ShutdownOnSuccess]: task succeeds -> shutdown() -> interrupt others
  |
throwIfFailed() / result():
  retrieve results or rethrow first failure
  |
close() (try-with-resources):
  verify all tasks done (if not, interrupt and wait)
  throw if tasks still running (programming error)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (parallel fan-out):**
```
Request handler starts         <- YOU ARE HERE
       |
  try (scope = ShutdownOnFailure)
       |
  fork: VT1 -> getUser()
  fork: VT2 -> getOrder()
  fork: VT3 -> getInventory()
       |
  scope.join() - waits for all 3
       |
  All 3 succeed:
    scope.throwIfFailed() - no-op
    merge(VT1.get(), VT2.get(), VT3.get())
       |
  return Response
```

**FAILURE PATH:**
```
VT2 -> getOrder() throws:
  scope.handleComplete(VT2) called
  ShutdownOnFailure: scope.shutdown()
  -> VT1 and VT3 interrupted
  -> VT1 and VT3: catch InterruptedException, exit
  scope.join() returns (all done)
  scope.throwIfFailed() rethrows VT2's exception
  -> request handler sees failure, no leaked tasks
```

**WHAT CHANGES AT SCALE:**
- Nested scopes: a parent scope's `join()` waits for all children,
  including entire child-scope lifecycles.
- Deadline propagation: cancel parent scope -> all child scopes
  and their tasks automatically cancelled.

---

### 💻 Code Example

**BAD - unstructured concurrent fetch (task leak risk):**
```java
// BAD: if any future fails midway, others continue running
List<Future<Data>> futures = List.of(
    exec.submit(() -> fetchA()),
    exec.submit(() -> fetchB()),
    exec.submit(() -> fetchC())
);
List<Data> results = new ArrayList<>();
for (Future<Data> f : futures) {
    results.add(f.get()); // if f[0] fails, f[1]/f[2] still run
}
```

**GOOD - structured fan-out with ShutdownOnFailure:**
```java
// GOOD: all-or-nothing semantics, zero task leaks
Response buildResponse(long id)
        throws InterruptedException, ExecutionException {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Subtask<User>      user  = scope.fork(() -> getUser(id));
        Subtask<Orders>    order = scope.fork(() -> getOrders(id));
        Subtask<Inventory> inv   = scope.fork(() -> getInventory(id));

        scope.join()           // wait for all or failure
             .throwIfFailed(); // rethrow first failure

        return Response.of(user.get(), order.get(), inv.get());
    }
    // Guaranteed: all VTs done when we exit try block
}
```

**GOOD - ShutdownOnSuccess (hedged request):**
```java
// GOOD: race two services, take whichever responds first
String fetchFast(String id) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
        scope.fork(() -> primaryService.fetch(id));
        scope.fork(() -> backupService.fetch(id));

        scope.join();
        return scope.result(); // whichever replied faster
    }
    // The slower service is automatically cancelled
}
```

**How to test:**
```java
@Test
void allTasksCompleteOrNoneLeaks() throws Exception {
    AtomicInteger running = new AtomicInteger(0);

    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        scope.fork(() -> { running.incrementAndGet();
            Thread.sleep(100); running.decrementAndGet(); return 1; });
        scope.fork(() -> { running.incrementAndGet();
            Thread.sleep(50);
            throw new RuntimeException("fail");
        });
        try {
            scope.join().throwIfFailed();
        } catch (ExecutionException ignored) {}
    }

    // After scope closes: guaranteed no running tasks
    assertThat(running.get()).isZero();
}
```

---

### ⚖️ Comparison Table

| Feature | `ExecutorService.submit()` | `CompletableFuture.allOf()` | `StructuredTaskScope` |
|---------|---------------------------|----------------------------|----------------------|
| Task lifetime guarantee | None (fire-and-forget) | Manual cancel needed | Enforced by scope |
| Auto-cancel siblings on failure | No | No | Yes (ShutdownOnFailure) |
| Error propagation | Manual (get/catch) | `exceptionally` | `throwIfFailed()` |
| API status | Stable | Stable | Preview (Java 24) |
| Virtual thread required | No | No | Yes (recommended) |
| Nesting support | No | Composable | Tree-structured |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`StructuredTaskScope` is just `CompletableFuture.allOf`" | `allOf` has no lifetime enforcement - tasks run until completion regardless of cancellation. `StructuredTaskScope` guarantees no task outlives the scope. |
| "Structured concurrency prevents all concurrency bugs" | It prevents task leaks and missing cancellations. It does NOT prevent data races in shared mutable state. |
| "`scope.join()` collects results" | `join()` only waits for all tasks to complete. Access results via `subtask.get()` after `join()`. |
| "Custom policies require extending StructuredTaskScope" | Yes, for custom fan-out logic (e.g., wait for 2-of-3). Override `handleComplete()` in a subclass. Built-in policies only cover all-or-nothing and first-wins. |
| "Structured concurrency is production-ready in Java 21" | It is Preview in Java 21 (requires `--enable-preview`). API may change. Use in production with caution until it reaches Final status. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: scope.join() never returns**

**Symptom:** Request hangs indefinitely; scope never closes.

**Root Cause:** A forked task is stuck (infinite loop, native I/O
that ignores interrupt). `ShutdownOnFailure` sent interrupt, but
task ignored it.

**Diagnostic:**
```bash
jstack <pid> | grep -A10 "StructuredTask"
# Shows VT stack traces inside the scope
```

**Fix:** Ensure all tasks respond to `InterruptedException` or
check `Thread.interrupted()`. Add `orTimeout()` wrapper:
```java
scope.fork(() -> {
    return fetchWithTimeout(id, Duration.ofSeconds(5));
});
```

---

**Failure Mode 2: subtask.get() before scope.join()**

**Symptom:** `IllegalStateException` calling `subtask.get()`.

**Root Cause:** Called `subtask.get()` while task may still be
running (before `join()`).

**Fix:** Always call `scope.join()` before any `subtask.get()`.
The API enforces this at runtime.

---

**Failure Mode 3: Leaked scope from missing try-with-resources**

**Symptom:** Thread dump shows StructuredTaskScope threads alive
long after request completion.

**Root Cause:** `new StructuredTaskScope()` created without
try-with-resources; `close()` never called.

**Fix:** Always use `try (var scope = new StructuredTaskScope...)`.
IDE should warn on unclosed `AutoCloseable`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-044 - Structured Concurrency]] - the Java API entry point
- [[JCC-073 - Project Loom Design Rationale]] - why virtual threads
  make structured concurrency practical
- [[JCC-062 - Thread Interruption and Cancellation]] - how
  cancellation propagates to child tasks

**Builds On This (learn these next):**
- Kotlin `coroutineScope {}` - production-ready equivalent
- Swift `TaskGroup` - same concept in Swift async

**Alternatives / Comparisons:**
- [[JCC-059 - CompletableFuture Composition Patterns]] - no lifetime
  guarantee but stable API
- [[JCC-063 - CompletionService]] - result collection without
  lifetime management

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Concurrent tasks with enforced     |
|              | tree-shaped lifetimes via scope    |
+--------------+------------------------------------+
| PROBLEM      | ExecutorService tasks can outlive  |
|              | their creator; leaks and lost errors|
+--------------+------------------------------------+
| KEY INSIGHT  | Concurrent tasks = structured code:|
|              | child cannot outlive parent scope  |
+--------------+------------------------------------+
| USE WHEN     | Fan-out service calls, hedged reqs,|
|              | structured error propagation       |
+--------------+------------------------------------+
| AVOID WHEN   | Long-running background tasks,     |
|              | production Java 21 (still Preview) |
+--------------+------------------------------------+
| TRADE-OFF    | Zero leaks, clear semantics /      |
|              | Preview API; all tasks must finish |
+--------------+------------------------------------+
| ONE-LINER    | try (var s = ShutdownOnFailure())  |
|              | { s.fork(a); s.fork(b); s.join(); }|
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-044 Structured Concurrency,    |
|              | Kotlin coroutineScope              |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Tasks forked in a `StructuredTaskScope` CANNOT outlive the scope
   - guaranteed by `close()` in try-with-resources.
2. `ShutdownOnFailure` = all-or-nothing. `ShutdownOnSuccess` =
   first-wins (hedged requests).
3. Call `scope.join()` then `scope.throwIfFailed()` before accessing
   any `subtask.get()`.

**Interview one-liner:** "Structured concurrency enforces that child
tasks cannot outlive their parent scope - `StructuredTaskScope`
automatically cancels siblings on failure (`ShutdownOnFailure`) or
success (`ShutdownOnSuccess`), eliminating task leaks and ensuring
errors propagate correctly."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Resource and task lifetimes
should be bounded by lexical scope, not by programmer discipline.
Any resource that can escape its creation context becomes a leak
vector. Automatic enforcement (RAII, try-with-resources, structured
concurrency) is categorically more reliable than discipline.

**Where else this pattern appears:**
- **Kotlin `coroutineScope {}`:** Enforces that all coroutines
  launched inside complete before the block returns. The canonical
  production-ready implementation of the same principle.
- **Python `asyncio.TaskGroup` (Python 3.11):** `async with
  TaskGroup() as tg:` - same lifetime semantics adopted from the
  Trio async library, directly inspired by Sustrik's essays.
- **Rust `tokio::join!` macro:** All async tasks in the join
  macro must complete before the macro returns - no task can escape.

---

### 💡 The Surprising Truth

The structured concurrency concept was not invented by the Project
Loom team. It was published in two influential 2018 blog posts:
Martin Sustrik's "Structured Concurrency" and Nathaniel J. Smith's
"Notes on Structured Concurrency, or: Go Statement Considered
Harmful." Smith's essay argued that unstructured concurrent task
creation (`go` in Go, `thread.start()` in Java) is equivalent to
the `goto` statement - it creates invisible control flow that
cannot be locally reasoned about. The Loom team read these essays
and credited them explicitly in the JEP design notes. Multiple
language ecosystems (Python asyncio, Swift, Kotlin, and now Java)
independently converged on the same solution within 5 years,
suggesting the concept fills a genuine, longstanding gap in
concurrent programming models.

---

### 🧠 Think About This Before We Continue

**Question 1 (Design Trade-off):** You need a "best-effort" fan-out:
call 5 services in parallel, collect whichever succeed within 500ms,
and discard failures. Neither `ShutdownOnFailure` nor
`ShutdownOnSuccess` fits. Design a custom `StructuredTaskScope`
policy for this pattern and describe what `handleComplete()` should
do in each task outcome case.

*Hint:* Extend `StructuredTaskScope`, override `handleComplete()`,
maintain a thread-safe list of successes, and call `shutdown()`
when either the deadline or all tasks complete. Research the JEP
453 API for the `Subtask.State` enum and how to distinguish success
from failure outcomes.

---

**Question 2 (System Interaction):** Parent scope P forks child
scope C. C forks tasks T1 and T2. T1 fails: C cancels T2, scope C
closes, exception propagates to P. P has its own sibling tasks P1
and P2. If P uses `ShutdownOnFailure`, what happens to P1 and P2
when C fails? Trace the exact interruption chain.

*Hint:* The child scope's exception propagates through `throwIfFailed()`
as an `ExecutionException` in P's `join()`. Then P's `ShutdownOnFailure`
triggers, interrupting P1 and P2. Map the exact sequence of
`handleComplete()`, `shutdown()`, and `join()` calls in breadth-
first vs depth-first order.

---

**Question 3 (Root Cause):** A team migrating from
`CompletableFuture` to `StructuredTaskScope` discovers that their
service's P99 latency *increased* by 20%. The fan-out calls 10
downstream services; structured concurrency waits for ALL to
complete. What is the root cause, and what architectural change
would preserve structured concurrency semantics while reducing P99?

*Hint:* When slowest-of-10 determines P99, adding hedged requests
(`ShutdownOnSuccess` with primary + backup per service) reduces P99
to near P50 of the underlying service. Alternatively, apply per-
task timeouts inside each fork rather than a global scope timeout.

