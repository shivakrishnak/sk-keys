---
layout: default
title: "Structured Concurrency"
parent: "Java Concurrency"
nav_order: 365
permalink: /java-concurrency/structured-concurrency/
number: "365"
category: Java Concurrency
difficulty: ★★★
depends_on: Virtual Threads, ExecutorService, Thread, Future
used_by: Parallel Service Calls, Fan-out/Fan-in, Error Propagation
tags: #java, #java21, #concurrency, #structured-concurrency, #loom
---

# 365 — Structured Concurrency (Java 21)

`#java` `#java21` `#concurrency` `#structured-concurrency` `#loom`

⚡ TL;DR — Structured Concurrency (Java 21 preview) ensures that child threads spawned within a task don't outlive their parent scope — a `StructuredTaskScope` auto-cancels siblings on first failure or success, preventing thread leaks and simplifying error handling.

| #365 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Virtual Threads, ExecutorService, Thread, Future | |
| **Used by:** | Parallel Service Calls, Fan-out/Fan-in, Error Propagation | |

---

### 📘 Textbook Definition

**Structured Concurrency** (Java 21 preview, `java.util.concurrent.StructuredTaskScope`) treats a group of concurrent tasks as a single unit of work with a defined lifetime. A `StructuredTaskScope` is opened with `try-with-resources`; tasks are forked inside it; the scope's `join()` waits for all tasks; subtasks cannot outlive the scope. Built-in policies: `ShutdownOnFailure` (cancels remaining tasks when any fails; throws if any failed) and `ShutdownOnSuccess` (returns first success; cancels others). The API is designed specifically for virtual threads.

---

### 🟢 Simple Definition (Easy)

Problem: you fan-out 3 parallel API calls. If one fails, the other two keep running (wasted work). If the main thread exits, leaked threads may still be running. Structured Concurrency fixes both: open a scope, fork the tasks, join. If any fails — all cancelled. Scope closes — all guaranteed done. No leaks.

---

### 🔵 Simple Definition (Elaborated)

Unstructured concurrency (ExecutorService): you submit tasks and get Futures. The tasks live independently — you must manually cancel them if things go wrong. Missing a cancellation leaks threads and resources. Structured Concurrency enforces a **containment rule**: subtasks must complete before the parent scope exits. This mirrors structured programming (a function's control flow must complete before returning) applied to concurrency. Error handling becomes natural: exceptions from subtasks are collected and rethrown at join().

---

### 🔩 First Principles Explanation

```
Problem with unstructured concurrency:
  Future<User>   userFuture   = pool.submit(() -> fetchUser(id));
  Future<Orders> ordersFuture = pool.submit(() -> fetchOrders(id));
  
  User user = userFuture.get();   // blocks
  // If fetchUser throws, fetchOrders keeps running — resource waste
  // Thread leak: pool thread not returned until fetchOrders also finishes
  // Manual cleanup: must catch + cancel in finally → error-prone

Structured Concurrency:
  try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User>   user   = scope.fork(() -> fetchUser(id));
    Subtask<Orders> orders = scope.fork(() -> fetchOrders(id));
    
    scope.join();           // wait for all
    scope.throwIfFailed();  // throw if any failed
    
    return merge(user.get(), orders.get());
  } // scope closes: all subtasks must be complete
  
  If fetchUser() throws:
    → ShutdownOnFailure cancels fetchOrders immediately
    → scope.throwIfFailed() rethrows the exception
    → No resource leak; no running orphan threads
```

**Structured vs Unstructured:**

```
Unstructured:            Structured:
Tasks can outlive scope  Tasks contained within scope
Manual cancellation      Auto-cancellation on policy trigger
Thread leaks possible    Impossible (scope enforces lifetime)
Error handling complex   join() + throwIfFailed() — simple
```

---

### 🧠 Mental Model / Analogy

> Structured Concurrency is like a **team project with a strict deadline**. A manager (scope) assigns subtasks to team members (virtual threads). The project is only "done" when ALL members finish OR the project is cancelled (first failure). The team can't leave the office until the project concludes — no one sneaks out early, no orphaned "still working" threads. The manager (scope.join()) waits and collects all outcomes.

---

### ⚙️ How It Works

```
StructuredTaskScope (try-with-resources):
  Constructor options:
    new ShutdownOnFailure()   → cancel all on first failure; throwIfFailed() at join
    new ShutdownOnSuccess<T>()→ cancel all on first success; result() returns winner

  fork(Callable<T>) → Subtask<T>  // schedule task as virtual thread
  join()                          // wait for all (or until shutdown policy triggers)
  throwIfFailed()                 // (ShutdownOnFailure only) throws if any task failed
  result()                        // (ShutdownOnSuccess only) returns first successful result
  close()                         // called automatically via try-with-resources

  Subtask<T> state:
    UNAVAILABLE → running/not started
    SUCCESS     → task.get() returns result
    FAILED      → task.exception() returns exception
```

---

### 🔄 How It Connects

```
Structured Concurrency
  │
  ├─ Designed for  → Virtual Threads (pairs naturally)
  ├─ Replaces     → manual Future.cancel() + try/finally in fan-out
  ├─ Lifetime     → subtasks cannot outlive enclosing scope
  ├─ ShutdownOnFailure → fail-fast: cancel all when one fails
  ├─ ShutdownOnSuccess → first-wins: cancel all when one succeeds (hedged requests)
  └─ companion    → ScopedValue (typed, scoped ThreadLocal for structured tasks)
```

---

### 💻 Code Example

```java
// ShutdownOnFailure: all succeed or fail together
Response fetchFullResponse(String userId) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Subtask<User>    user    = scope.fork(() -> userService.fetch(userId));
        Subtask<Profile> profile = scope.fork(() -> profileService.fetch(userId));
        Subtask<Orders>  orders  = scope.fork(() -> orderService.fetch(userId));

        scope.join()          // blocks until all done or one fails
             .throwIfFailed(); // throws ExecutionException if any failed

        // All three succeeded — use results
        return new Response(user.get(), profile.get(), orders.get());
    }
    // Scope closed: all virtual threads guaranteed complete
}
```

```java
// ShutdownOnSuccess: hedged requests — return whichever server responds first
String fetchFromFastestSource(String key) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
        scope.fork(() -> primaryServer.get(key));
        scope.fork(() -> replicaServer.get(key));
        scope.fork(() -> cacheServer.get(key));

        scope.join(); // waits until FIRST success (cancels remaining)
        return scope.result(); // returns the winning result
    }
    // First response wins; other two virtual threads cancelled
}
```

```java
// Timed join — auto-cancel if all tasks don't finish in time
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<Data> data = scope.fork(() -> fetchSlowData());

    scope.joinUntil(Instant.now().plusSeconds(5)); // cancel after 5s
    scope.throwIfFailed(e -> new TimeoutException("Service too slow"));

    return data.get();
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Structured Concurrency replaces CompletableFuture | Complementary: SC for lifetime management; CF for complex async pipelines |
| Subtasks run on a shared thread pool | Each `fork()` creates a new virtual thread — not pooled |
| Tasks can be forked outside the scope | `fork()` must be called within the scope's try-with-resources block |
| `scope.join()` throws exceptions directly | `join()` doesn't throw; call `throwIfFailed()` separately to surface exceptions |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Forgetting throwIfFailed after join**

```java
// ❌ Missing throwIfFailed — exceptions silently swallowed
scope.join();
return new Response(user.get(), orders.get()); // user.get() may throw if task failed!

// ✅ Always call throwIfFailed for ShutdownOnFailure
scope.join().throwIfFailed();
return new Response(user.get(), orders.get());
```

**Pitfall 2: Forking outside scope (IllegalStateException)**

```java
var scope = new StructuredTaskScope.ShutdownOnFailure();
scope.fork(() -> doWork()); // ❌ Must be inside try-with-resources
scope.join();

// ✅ Always use try-with-resources
try (var scope2 = new StructuredTaskScope.ShutdownOnFailure()) {
    scope2.fork(() -> doWork());
    scope2.join().throwIfFailed();
}
```

---

### 🔗 Related Keywords

- **[Virtual Threads](./085 — Virtual Threads.md)** — structured concurrency designed for VTs
- **[Future & CompletableFuture](./075 — Future and CompletableFuture.md)** — alternative for async composition
- **[Thread Interruption](./090 — Thread Interruption.md)** — scope cancellation uses interruption
- **[CountDownLatch](./078 — CountDownLatch.md)** — manual fan-in; SC replaces this for many cases
- **ScopedValue** — structured ThreadLocal for passing context into forked tasks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Subtasks can't outlive the scope; auto-cancel │
│              │ on failure/success; eliminates thread leaks   │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Fan-out parallel calls (user+orders+profile); │
│              │ hedged requests (fastest wins); fail-fast     │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Complex async pipelines (use CompletableFuture│
│              │ for thenApply/thenCompose chains)             │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Subtasks live and die with the scope —       │
│              │  no thread outlives its parent task"          │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ScopedValue → Virtual Threads →               │
│              │ CompletableFuture → Project Loom              │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `ShutdownOnSuccess` cancels remaining tasks when the first succeeds. What happens if ALL tasks fail — what does `scope.result()` return, and how do you handle all-failed scenarios?

**Q2.** Structured Concurrency uses virtual threads for each `fork()`. Why does this make the per-fork cost negligible compared to creating a platform thread per subtask?

**Q3.** Compare `StructuredTaskScope.ShutdownOnFailure` + `scope.join().throwIfFailed()` with `CompletableFuture.allOf(f1, f2, f3)`. What does Structured Concurrency provide that `allOf` does not, specifically around thread lifetime management?

