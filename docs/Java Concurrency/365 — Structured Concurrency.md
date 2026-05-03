---
layout: default
title: "Structured Concurrency"
parent: "Java Concurrency"
nav_order: 365
permalink: /java-concurrency/structured-concurrency/
number: "0365"
category: Java Concurrency
difficulty: ★★★
depends_on: Virtual Threads, ExecutorService, Thread, CompletableFuture
used_by: Parallel Task Execution, Scoped Task Lifetimes, Error Propagation
related: Virtual Threads, Scoped Values, CompletableFuture, ExecutorService, Project Loom
tags:
  - concurrency
  - structured-concurrency
  - java
  - loom
  - advanced
  - error-handling
---

# 365 — Structured Concurrency

⚡ TL;DR — Structured Concurrency treats a group of concurrent tasks as a single unit of work: the unit succeeds when all tasks succeed, and fails atomically with cleanup when any task fails — eliminating the thread-leak and error-swallowing problems of unstructured async code.

| #0365           | Category: Java Concurrency                                                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Virtual Threads, ExecutorService, Thread, CompletableFuture                      |                 |
| **Used by:**    | Parallel Task Execution, Scoped Task Lifetimes, Error Propagation                |                 |
| **Related:**    | Virtual Threads, Scoped Values, CompletableFuture, ExecutorService, Project Loom |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You call `executor.submit(taskA)` and `executor.submit(taskB)` in parallel. Task A fails with an exception. What happens? The exception is swallowed in the `Future` returned by submit — unless you explicitly call `future.get()` and handle it. Task B continues running even though the overall operation has already failed. You're responsible for: (1) cancelling task B manually, (2) capturing and re-throwing task A's exception, (3) ensuring no thread leaks when either task fails or is interrupted. Every developer writes this cleanup code differently, resulting in resource leaks and silent exception losses.

**THE BREAKING POINT:**
Traditional concurrent code violates the principle of structured programming: a function should exit at a single point, with all side effects (threads, resources) cleaned up. `ExecutorService` lets you start threads that outlive the scope they were started in. Errors in child threads don't automatically propagate to the parent. This makes multi-threaded code a minefield of subtle bugs that only manifest under specific failure conditions.

**THE INVENTION MOMENT:**
Structured Concurrency (JEP 453, introduced as a preview in Java 21) borrows from structured programming: just as a `try` block guarantees code after it runs after the block exits, `StructuredTaskScope` guarantees all subtasks are either completed or cancelled before the scope exits. The parent thread always outlives its children. Errors propagate automatically. No task can leak.

---

### 📘 Textbook Definition

**Structured Concurrency** (Java 21, preview; stable Java 25+) is a programming model where a `StructuredTaskScope` defines the lifetime of a set of concurrent tasks. All tasks forked within the scope complete (either succeed or fail) before the scope closes. Built-in policies: `ShutdownOnFailure` — cancels all tasks if any fails; `ShutdownOnSuccess` — cancels all tasks as soon as any succeeds (for parallel search/race patterns). The scope is `AutoCloseable`: `scope.join()` waits for all tasks; `scope.close()` cancels and cleans up. Task results are retrieved via `Subtask<T>` handles. If the current thread is interrupted, all subtasks are cancelled. The lifecycle constraint — parent outlives children — enables stack-like reasoning about concurrent code.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Structured Concurrency makes parallel tasks behave like a single compound operation: either everything succeeds together or everything fails together, with no leaks.

**One analogy:**

> Structured Concurrency is like a flight crew pre-departure checklist. The captain (parent thread) can't push back from the gate until ALL crew members (subtasks) have checked in. If any crew member reports a problem (subtask fails), all crew members stop their current tasks (cancel), the captain hears about it immediately, and the gate remains until everyone is accounted for. Nobody walks off and gets lost in the airport (thread leak).

**One insight:**
Structured Concurrency's key promise is not performance — it's **observability**. Thread dumps show parent-child task relationships, just like call stacks. Monitoring tools can reason about task trees rather than disconnected thread pools. Error propagation is automatic. This transforms concurrent code from "a bag of threads" into "a call tree with lifetimes."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Tasks forked within a scope cannot outlive the scope.
2. `scope.join()` waits for all tasks to complete or for the scope's shutdown policy to trigger.
3. On scope exit: all incomplete subtasks are cancelled; all thrown exceptions are collected.
4. Exceptions thrown in subtasks propagate to the parent via `throwIfFailed()` (for `ShutdownOnFailure`).
5. Interrupting the scope's thread cancels all subtasks.

**DERIVED DESIGN:**

```java
// PATTERN 1: ShutdownOnFailure (all-or-nothing)
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<String> user  = scope.fork(() -> fetchUser(id));
    Subtask<Order> order  = scope.fork(() -> fetchOrder(id));
    scope.join()           // wait: all complete or any fails
         .throwIfFailed(); // propagate first exception

    // Reaching here: BOTH tasks succeeded
    return new Response(user.get(), order.get());
} // scope.close(): cancels any outstanding tasks, releases

// PATTERN 2: ShutdownOnSuccess (first-to-win race)
try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
    scope.fork(() -> fetchFromPrimaryDB(key));
    scope.fork(() -> fetchFromReplicaDB(key));
    scope.join();
    return scope.result(); // first non-null winner
}
```

```
LIFETIME GUARANTEE:
┌──────────────────────────────────────────────────────────┐
│  Parent Thread                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │ try (StructuredTaskScope scope) {                │   │
│  │   fork(taskA) ─────────────────────────────► [A]│   │
│  │   fork(taskB) ─────────────────────────────► [B]│   │
│  │   scope.join()  // waits                        │   │
│  │   // A and B MUST complete before here          │   │
│  │ } // close: cancels outstanding tasks           │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
Invariant: scope.close() called AFTER all forked tasks finish
```

**THE TRADE-OFFS:**

- **Gain:** No thread leaks; automatic error propagation; observability (thread dumps show task trees); clean cancellation semantics.
- **Cost:** Preview API (still evolving in Java 21-24); doesn't cover all async patterns; can't express inter-task communication easily; requires Java 21+ with `--enable-preview`.

---

### 🧪 Thought Experiment

**SETUP:**
A microservice endpoint needs: (A) fetch user profile (100ms), (B) fetch recent orders (150ms). Currently done sequentially: 250ms total. You parallelize them.

**WITHOUT Structured Concurrency:**

```java
Future<User> userFuture = executor.submit(() -> fetchUser(id));
Future<List<Order>> orderFuture = executor.submit(() -> fetchOrders(id));
User user = userFuture.get();       // blocks 100ms
List<Order> orders = orderFuture.get(); // returns immediately (already done)
```

If `fetchUser` throws: `ExecutionException` wraps it. `fetchOrders` is still running in the thread pool. You must manually cancel it. If you forget, threads accumulate over time → thread pool exhaustion.

**WITH Structured Concurrency:**

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var user   = scope.fork(() -> fetchUser(id));
    var orders = scope.fork(() -> fetchOrders(id));
    scope.join().throwIfFailed();
    return new Profile(user.get(), orders.get());
}
```

If `fetchUser` throws: `ShutdownOnFailure` cancels `fetchOrders` automatically. `throwIfFailed()` re-throws the original exception. Zero manual cancellation code. Zero thread leaks.

**THE INSIGHT:**
Structured Concurrency is not just convenience — it encodes the invariant "this function's concurrent tasks live and die with this function's execution" directly into the API. The invariant is impossible to violate accidentally.

---

### 🧠 Mental Model / Analogy

> Structured Concurrency is like a project manager who kicks off parallel sub-teams and cannot hand in the project until all teams have delivered or all are stood down. If sub-team A delivers disaster news, the PM immediately tells all other sub-teams to stop, collects the bad news, and reports it upward. No sub-team goes rogue after the project is cancelled. No sub-team's work is lost silently.

- "Project manager" → parent thread
- "Sub-teams" → forked subtasks in the scope
- "Project delivery deadline" → `scope.join()`
- "Disaster news" → subtask exception
- "Stand down all teams" → `ShutdownOnFailure` cancellation
- "Report upward" → `throwIfFailed()` re-propagation

Where this analogy breaks down: unlike real project managers, StructuredTaskScope's scope is strictly bounded by the `try-with-resources` block — tasks can't outlive the block, whereas real sub-teams could outlive their manager's authority.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Structured Concurrency lets you run tasks in parallel and guarantees they all finish before your function returns. If any task fails, the others are cancelled automatically and the error is reported to you. No forgotten threads, no swallowed exceptions.

**Level 2 — How to use it (junior developer):**
Use `StructuredTaskScope.ShutdownOnFailure` for "all must succeed" patterns. Use `StructuredTaskScope.ShutdownOnSuccess` for "first to win" patterns. Always in `try-with-resources` so `close()` is called. Use `scope.fork(callable)` to start tasks and `scope.join()` to wait. Call `throwIfFailed()` after join to propagate exceptions. Retrieve results via `subtask.get()` only after join (throws `IllegalStateException` if called before join completes).

**Level 3 — How it works (mid-level engineer):**
`StructuredTaskScope` creates a `ForkJoinPool`-backed pool (or uses a provided thread factory). `fork()` submits the callable and returns a `Subtask<T>` handle tracking the task's state (UNAVAILABLE, SUCCESS, FAILED). `join()` blocks until the policy's shutdown condition is met (all done, or first failure/success). On `close()`: for any still-running tasks, their threads are interrupted. The scope establishes a parent-child thread relationship tracked in a `LinkedHashSet` of subtasks. This parent-child relationship is what makes thread dumps show task trees — each forked thread knows its scope owner.

**Level 4 — Why it was designed this way (senior/staff):**
The design explicitly avoids `CompletableFuture`'s continuation-chaining model (`thenApply`, `exceptionally`) because continuations break the lexical relationship between task creation and task completion — the completion callback might run on an arbitrary thread at an arbitrary time. StructuredTaskScope keeps all task lifecycle management on the forking thread, which is always in scope. This restores the "call tree" shape of single-threaded code in a concurrent setting. The JEP notes that the design was influenced by Python's `asyncio.TaskGroup` and Kotlin's coroutine `coroutineScope`, both of which enforce the same parent-outlives-children invariant. The choice to use `try-with-resources` rather than callbacks is deliberate: it keeps the concurrent code looking like sequential code structurally.

---

### ⚙️ How It Works (Mechanism)

```java
// Full example: parallel service calls with error handling
// Requires: Java 21+ with --enable-preview

import java.util.concurrent.StructuredTaskScope;

record UserProfile(User user, List<Order> orders,
                   Optional<Coupon> coupon) {}

UserProfile buildProfile(String userId)
        throws InterruptedException, ExecutionException {

    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        // All three calls run in parallel (virtual threads)
        Subtask<User>          user   =
            scope.fork(() -> userService.findById(userId));
        Subtask<List<Order>>   orders =
            scope.fork(() -> orderService.findByUser(userId));
        Subtask<Optional<Coupon>> coupon =
            scope.fork(() -> couponService.findActive(userId));

        scope.join()           // wait for all or any failure
             .throwIfFailed(); // re-throw first exception

        // All three succeeded — results are safe to get
        return new UserProfile(user.get(), orders.get(), coupon.get());

        // On scope close (try exit):
        // - If we got here: all tasks done
        // - If exception thrown: outstanding tasks are cancelled
    }
}

// Example: ShutdownOnSuccess (racing two mirrors)
String fetchWithFallback(String key)
        throws ExecutionException, InterruptedException {

    try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
        scope.fork(() -> primaryCache.get(key));   // try cache
        scope.fork(() -> secondaryCache.get(key)); // try replica
        scope.fork(() -> database.get(key));       // try DB
        scope.join();
        return scope.result(); // first non-null responder wins
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (ShutdownOnFailure):
Parent thread enters StructuredTaskScope
→ fork(taskA), fork(taskB), fork(taskC)
→ scope.join() blocks parent
→ [StructuredTaskScope ← YOU ARE HERE]
→ taskA finishes (success)
→ taskB finishes (success)
→ taskC finishes (success)
→ join() returns → throwIfFailed() (no-op) → results collected
→ scope.close() (all tasks done, nothing to cancel)
→ Parent continues

FAILURE PATH:
→ taskA finishes (success)
→ taskB throws IOException
→ ShutdownOnFailure: cancels taskC (interrupt)
→ join() returns → throwIfFailed() throws ExecutionException
→ Parent propagates exception
→ scope.close(): confirms all tasks cancelled/completed
→ No thread leaks

WHAT CHANGES AT SCALE:
Structured Concurrency pairs naturally with Virtual Threads
(Project Loom): each forked task gets a lightweight virtual
thread. You can fork 100,000 tasks per request without
exhausting OS threads. At scale, the parent-outlives-children
guarantee prevents thundering-herd thread leaks when requests
spike and tasks pile up.
```

---

### 💻 Code Example

```java
// Example 1: WRONG (unstructured — task leaks on failure)
// BAD
CompletableFuture<User> cf1 = CompletableFuture
    .supplyAsync(() -> fetchUser(id));
CompletableFuture<Order> cf2 = CompletableFuture
    .supplyAsync(() -> fetchOrder(id));
// If cf1 fails: cf2 keeps running — LEAK!
User u = cf1.join(); // exception propagation is manual
Order o = cf2.join();

// Example 1: GOOD (structured — no leaks)
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var u = scope.fork(() -> fetchUser(id));
    var o = scope.fork(() -> fetchOrder(id));
    scope.join().throwIfFailed();
    return process(u.get(), o.get());
}

// Example 2: Custom shutdown policy
// Shutdown when all tasks complete (like join-all)
try (var scope = new StructuredTaskScope<String>()) {
    var results = List.of(
        scope.fork(() -> "taskA"),
        scope.fork(() -> "taskB")
    );
    scope.join(); // wait for all (no early shutdown)
    results.forEach(t ->
        System.out.println(t.state() + ": " + t.get()));
}
```

---

### ⚖️ Comparison Table

| Approach                | Task Lifetime | Error Propagation   | Thread Leaks | Best For                  |
| ----------------------- | ------------- | ------------------- | ------------ | ------------------------- |
| ExecutorService         | Unbounded     | Manual (Future.get) | Possible     | Long-running work pools   |
| CompletableFuture       | Unbounded     | Chained callbacks   | Possible     | Async pipelines           |
| **StructuredTaskScope** | Scope-bounded | Automatic           | Impossible   | Scoped parallel subtasks  |
| ParallelStream          | Scope-bounded | Automatic           | Impossible   | Data-parallel collections |

**How to choose:** Use `StructuredTaskScope` (Java 21+ preview) for any method that fans out to parallel calls and must aggregate results. Use `CompletableFuture` for event-driven async pipelines where the caller doesn't wait. Use `ExecutorService` for long-lived background task pools.

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                              |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Structured Concurrency replaces all ExecutorService use      | It targets scoped fan-out patterns, not long-lived background pools. Scheduled jobs and persistent worker pools still use ExecutorService                                                            |
| ShutdownOnSuccess returns the FASTEST result                 | ShutdownOnSuccess returns the FIRST result that completes without error. If the fastest task throws an exception, it waits for another successful task. It's "first success", not "first completion" |
| scope.join() blocks the OS thread                            | With Virtual Threads (Loom), `scope.join()` parks the virtual thread without blocking the carrier OS thread. Other virtual threads can run on the same OS thread while parent is parked              |
| Structured Concurrency is available in Java 21 without flags | In Java 21, it requires `--enable-preview`. It becomes stable in later Java versions                                                                                                                 |

---

### 🚨 Failure Modes & Diagnosis

**Task Leaks with CompletableFuture (Pre-SC)**

**Symptom:** Thread pool threads accumulate over time; memory grows; task completion after timeout continues in background.

**Root Cause:** `executor.submit(task)` started; request cancelled or timed out; task continues running because no automatic cancellation exists.

**Diagnostic Command:**

```bash
# Check active threads in ForkJoinPool or custom pool:
jstack <pid> | grep -c "java.util.concurrent"

# Or with JFR, check live virtual threads:
jcmd <pid> Thread.dump_to_file -format=json threads.json
```

**Fix:** Migrate to `StructuredTaskScope`. For Java < 21: use explicit `Future.cancel(true)` in `finally` blocks.

**Prevention:** Audit all `executor.submit()` calls for cancellation paths. Prefer StructuredTaskScope for scoped parallel work.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Threads` — StructuredTaskScope works best with virtual threads (Project Loom)
- `ExecutorService` — the unstructured alternative SC replaces for scoped work
- `CompletableFuture` — the callback-based alternative with weaker lifetime guarantees

**Builds On This (learn these next):**

- `Scoped Values` — thread-local-like values that propagate cleanly through StructuredTaskScope forks
- `Project Loom` — the overall framework providing Virtual Threads + Structured Concurrency

**Alternatives / Comparisons:**

- `CompletableFuture` — more flexible but no lifetime guarantee; use for async pipelines
- `Kotlin coroutineScope` — equivalent concept in Kotlin with structured coroutine lifetimes
- `Python asyncio.TaskGroup` — equivalent concept in Python async

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Scope that bounds lifetime of forked      │
│              │ concurrent tasks to the enclosing block   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Thread leaks and silent exception loss    │
│ SOLVES       │ in unstructured parallel code             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Parent always outlives children — no task │
│              │ can escape the scope that created it      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Method fans out to parallel subtasks and  │
│              │ aggregates results (Java 21+)             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long-lived background pools; Java < 21;   │
│              │ complex async pipelines (use CF)          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lifetime safety vs flexibility; preview   │
│              │ API still evolving in Java 21-24          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tasks are born and die with the          │
│              │  function that created them — always"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Scoped Values → Virtual Threads →         │
│              │ Project Loom                              │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Structured Concurrency guarantees that forked tasks cannot outlive the scope that created them. But `StructuredTaskScope.fork()` submits tasks to a thread pool — and thread pools are external to the scope. Explain exactly how the JDK enforces the lifetime guarantee: what happens at the JVM level when `scope.close()` is called with running tasks, and why is thread interruption (rather than thread termination) used as the cancellation mechanism?

**Q2.** `ShutdownOnSuccess` cancels all remaining tasks when the first task succeeds. If you use `ShutdownOnSuccess` to race three cache lookups (primary, secondary, DB) and the primary cache always responds in 1ms while DB takes 500ms, what is the exact overhead cost of the racing approach vs. sequential fallback? And under what cache-miss rate does racing become MORE expensive than sequential, accounting for the cost of starting and immediately cancelling virtual threads?
