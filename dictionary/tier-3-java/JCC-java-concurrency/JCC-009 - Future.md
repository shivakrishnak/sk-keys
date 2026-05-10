---
id: JCC-009
title: Future
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★☆☆
depends_on: JCC-007, JCC-008, JCC-025
used_by: JCC-010, JCC-025
related: JCC-008, JCC-010, JCC-025
tags:
  - java
  - concurrency
  - foundational
  - first-principles
  - async
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /jcc/future/
---

# JCC-009 - Future

⚡ TL;DR - `Future<V>` is a handle to an async computation: it lets you check if the result is ready, retrieve the result (blocking), or cancel the task - but it cannot chain callbacks or compose non-blocking pipelines.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | JCC-007, JCC-008, JCC-025 |     |
| **Used by:**    | JCC-010, JCC-025          |     |
| **Related:**    | JCC-008, JCC-010, JCC-025 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You submit a `Runnable` or `Callable` to a thread pool. The task runs asynchronously. But how do you know when it finishes? How do you get its result? Without `Future`, you must use shared variables, `CountDownLatch`, callbacks, or polling loops - all error-prone.

**THE BREAKING POINT:**
You submit 50 tasks to a pool. You want to process results as they complete. Without `Future`, you need a shared result list, synchronization, a mechanism to know which task produced which result, and a wait mechanism. This is 50+ lines of boilerplate to solve a fundamental problem.

**THE INVENTION MOMENT:**
`Future<V>` (Java 5) is the contract between task submitter and task executor: "I will give you a handle, and you can get the result from it when the task is done." It provides `get()` (blocking retrieval), `isDone()` (non-blocking check), `cancel()` (cooperative cancellation), and `isCancelled()`. This is the minimal async result contract.

**EVOLUTION:**
Java 5: `Future<V>` + `FutureTask<V>`. Java 8: `CompletableFuture<V>` extends `Future<V>` but adds non-blocking callbacks, chaining, and composition. Java 21: `StructuredTaskScope.Subtask<V>` is the Loom alternative that avoids `Future` entirely for structured concurrent tasks.

---

### 📘 Textbook Definition

**`java.util.concurrent.Future<V>`** is an interface representing the result of an asynchronous computation. It provides five operations: `get()` (blocks until result available), `get(timeout, unit)` (blocks with timeout), `isDone()` (non-blocking: is computation complete?), `cancel(mayInterruptIfRunning)` (attempt to cancel), `isCancelled()` (was it cancelled?). The standard implementation is `FutureTask<V>`. `Future` is an intentionally simple contract: it does not support callbacks, chaining, or non-blocking result consumption - those capabilities belong to `CompletableFuture`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`Future<V>` = a ticket for an async result - you can check if it's ready, wait for it, or cancel.

**One analogy:**

> A Future is a luggage claim ticket at an airport. You drop off your bag (submit the task), get a ticket (Future). Later, at the carousel, you either wait until your bag appears (blocking `get()`), check if it's on the belt (non-blocking `isDone()`), or tell the airline you don't want it (cancel). The ticket is not the bag - it is the handle to retrieve the bag.

**One insight:**
`Future` is intentionally limited. It only answers: "Is it done? What was the result? Can I cancel?" It cannot say: "When it's done, do this next." That composition capability belongs to `CompletableFuture`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **`Future.get()` blocks** until the computation is complete, then returns the result or throws.
2. **`cancel(true)` is cooperative** - it sets the interrupt flag on the executing thread. Whether the task actually stops depends on the task checking the interrupt flag.
3. **Once done, a `Future` is done forever** - `isDone()` remains true, `get()` returns the same value on every subsequent call.
4. **Exceptions from `call()` are wrapped in `ExecutionException`** - always unwrap with `getCause()`.
5. **`Future` has no callback mechanism** - you cannot register a listener for "when done, do X." Use `CompletableFuture` for that.

**DERIVED DESIGN:**
Given invariant 1 (blocking `get()`): if 50 threads all block on `future.get()`, those 50 threads are wasted until results are available. This is why high-throughput systems moved to `CompletableFuture` callbacks for non-blocking result handling.

Given invariant 5 (no callbacks): `Future` is fundamentally a pull model. The caller must come to the `Future` to get the result. `CompletableFuture` is a push model - it notifies registered callbacks when complete.

**THE TRADE-OFFS:**
**Gain:** Simple, predictable API. Easy to reason about. Typesafe result retrieval.
**Cost:** Blocking `get()` wastes threads. No composition or chaining. Cancellation is advisory only.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any async result needs a handle and a retrieval mechanism.
**Accidental:** Blocking retrieval, lack of composition, `ExecutionException` wrapping. `CompletableFuture` eliminates all three.

---

### 🧪 Thought Experiment

**SETUP:**
Fetch 5 external APIs in parallel. Process each result as it arrives. Total processing is complete when all 5 finish.

**WITH `Future` (blocking):**

```java
List<Future<Response>> futures = services.stream()
    .map(s -> executor.submit(() -> s.call()))
    .toList();
// Wait for each in order, not as they complete
for (Future<Response> f : futures) {
    Response r = f.get(); // blocks until THIS future is done
    process(r);           // may wait for slow ones
}
```

Problem: if service 1 takes 10s and services 2-5 take 1s each, you wait 10s before processing services 2-5, even though they finished long ago.

**WITH `CompletableFuture` (non-blocking):**

```java
services.stream()
    .map(s -> CompletableFuture
        .supplyAsync(s::call)
        .thenAccept(r -> process(r))) // fires when ready
    .toList();
```

Each result is processed immediately when its computation completes. Total wall time = longest task, not sum.

**THE INSIGHT:**
`Future` is correct but inefficient under concurrency. `CompletableFuture` is the evolution that removes the blocking bottleneck. Use `Future` when blocking is acceptable; use `CompletableFuture` for high-concurrency pipelines.

---

### 🧠 Mental Model / Analogy

> `Future` is a photograph of a moment in the future. You take the photo before the event (submit the task), and when the moment arrives (task completes), the photo develops. You can check if it's developed (`isDone()`), wait for it to develop (`get()`), or throw it away (`cancel()`). But you cannot program the photo to "automatically post to Instagram when developed" - that is `CompletableFuture` territory.

Element mapping:

- **Photo** = `Future<V>` instance
- **Camera shutter** = `executor.submit(callable)`
- **"Is it developed?"** = `future.isDone()`
- **Wait at the darkroom** = `future.get()`
- **Throw it away** = `future.cancel(true)`
- **Auto-post when developed** = `CompletableFuture.thenAccept()`

Where this analogy breaks down: a photograph can only be viewed; a `Future` can be cancelled. Cancellation is an action, not just observation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
`Future` is a receipt for work you've handed to someone else. When you need the result, you bring the receipt, and either the work is done (you get the result immediately) or you wait for it to finish.

**Level 2 - How to use it (junior developer):**

```java
Future<String> future = executor.submit(callable);
// do other work...
try {
    String result = future.get(10, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    future.cancel(true);
    // handle timeout
} catch (ExecutionException e) {
    // task threw an exception
    Throwable cause = e.getCause();
    // handle specific exception type
}
```

Always use `get(timeout, unit)` in production. Never use unbounded `get()`.

**Level 3 - How it works (mid-level engineer):**
`FutureTask<V>` is the standard `Future` implementation. Internally it uses `AbstractQueuedSynchronizer` (AQS) state transitions: `NEW → COMPLETING → NORMAL/EXCEPTIONAL/CANCELLED`. `get()` calls `AQS.acquire()` which parks the calling thread. When `run()` completes, it calls `AQS.release()`, unparking all threads blocked on `get()`. The result or exception is stored in the `outcome` field.

**Level 4 - Why it was designed this way (senior/staff):**
`Future` is intentionally minimal - it is an interface, not an implementation. This allows the JVM team to provide `FutureTask` as the standard implementation while enabling custom implementations (e.g., Guava's `ListenableFuture`, which adds callbacks without breaking the `Future` contract). `CompletableFuture` implements `Future<V>` itself, meaning all existing `Future`-aware code works with `CompletableFuture`. The minimal interface is an intentional extension point.

**Expert Thinking Cues:**

- "Is blocking on `get()` acceptable in this context? If not, use `CompletableFuture`."
- "Did I set a timeout on `get()`? Unbounded `get()` is a reliability hazard."
- "When `cancel(true)` is called, does the task actually check the interrupt flag?"

---

### ⚙️ How It Works (Mechanism)

**`FutureTask` state machine:**

```
NEW
 ├─ run() starts
 ├─ COMPLETING (transitional)
 │    ├─ success → NORMAL (result stored)
 │    └─ exception → EXCEPTIONAL (exception stored)
 └─ cancel() → CANCELLED (if not started)
              → INTERRUPTING → INTERRUPTED (if running)
```

**`get()` internals:**

```java
public V get() throws InterruptedException, ExecutionException {
    int s = state;
    if (s <= COMPLETING)
        s = awaitDone(false, 0L); // parks thread
    return report(s); // returns result or throws
}
// report():
//   NORMAL → return outcome
//   EXCEPTIONAL → throw ExecutionException(outcome)
//   CANCELLED → throw CancellationException
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Future<V> f = executor.submit(callable)
    │
    ├─ Calling thread continues (f is a handle)
    │
    └─ Pool thread executes callable.call()
            │
            ▼
       Result stored in FutureTask  ← YOU ARE HERE
            │
Calling thread: f.get()
  ├─ Task done: return V immediately
  ├─ Task running: park calling thread
  │     └─ Task completes → unpark → return V
  ├─ Task threw: throw ExecutionException
  └─ Timeout: throw TimeoutException
```

**FAILURE PATH:**
`f.get()` with no timeout → task hangs → calling thread blocked forever → thread pool thread leaked. Fix: always use `f.get(timeout, unit)` and call `f.cancel(true)` on timeout.

**WHAT CHANGES AT SCALE:**
At high concurrency, blocking `Future.get()` ties up the calling thread for the duration of the task. At 10,000 concurrent requests, this means 10,000 blocked threads. `CompletableFuture` with callbacks is the solution: no threads are blocked, results are processed by callbacks when they arrive.

---

### ⚖️ Comparison Table

| Feature               | `Future<V>`            | `CompletableFuture<V>`                   |
| --------------------- | ---------------------- | ---------------------------------------- |
| Blocking result       | `get()`                | `get()` (but also callbacks)             |
| Non-blocking callback | No                     | `thenApply()`, `thenAccept()`            |
| Chaining              | No                     | `thenCompose()`, `thenCombine()`         |
| Exception handling    | `ExecutionException`   | `exceptionally()`, `handle()`            |
| Manual completion     | No                     | `complete(v)`, `completeExceptionally()` |
| Cancellation          | `cancel(mayInterrupt)` | `cancel(mayInterrupt)`                   |
| Java version          | Java 5                 | Java 8                                   |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                             |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Calling `future.cancel()` guarantees the task stops"        | `cancel(true)` only sets the interrupt flag. The task must check `Thread.interrupted()` or call a blocking method to honor it. A CPU-bound task that never checks the interrupt flag will not stop. |
| "`future.get()` is non-blocking if the task is done"         | If `isDone()` is true, `get()` returns immediately. If `isDone()` is false, `get()` blocks. Use `isDone()` to avoid unnecessary blocking.                                                           |
| "A `Future` can be re-submitted or reset"                    | A `Future` represents a single computation. Once complete or cancelled, it cannot be rerun. Create a new `Callable` and submit it for a fresh computation.                                          |
| "`Future` and `CompletableFuture` are unrelated"             | `CompletableFuture<V>` implements both `Future<V>` and `CompletionStage<V>`. All code accepting `Future<V>` works with `CompletableFuture<V>`.                                                      |
| "Getting a `null` from `future.get()` means the task failed" | The task may have legitimately returned `null`. Check `isDone()` and catch `ExecutionException` to distinguish success-with-null from failure.                                                      |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Unbounded `future.get()` Causing Deadlock**
**Symptom:** Thread pool threads all blocked on `future.get()` waiting for subtasks to complete. No progress. JVM appears hung.
**Root Cause:** Pool thread blocks on a `Future` whose task requires another pool thread, but all pool threads are blocked.
**Diagnostic:**

```bash
jstack <pid> | grep -A 20 "pool-.*thread-"
# All threads show: at java.util.concurrent.FutureTask.get()
```

**Fix:**

```java
// BAD: pool thread blocks waiting for same pool
Future<Integer> sub = pool.submit(subTask);
return sub.get() + 1; // deadlock if pool exhausted

// GOOD: use ForkJoinPool (handles blocking internally)
// or restructure to CompletableFuture
return CompletableFuture.supplyAsync(subTask::call)
    .thenApply(r -> r + 1);
```

**Prevention:** Never block a pool thread on a `Future` from the same pool.

---

**Failure Mode 2: Timeout Not Set (Reliability)**
**Symptom:** Service hangs when a downstream dependency is slow or unresponsive.
**Root Cause:** `future.get()` called without timeout.
**Diagnostic:**

```bash
grep -rn "future\.get()" src/main/java/ | grep -v "timeout"
# Find all get() calls missing a timeout
```

**Fix:**

```java
// BAD: blocks forever on slow service
Result r = future.get();

// GOOD: timeout + cancel + fallback
try {
    Result r = future.get(3, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    future.cancel(true);
    return cachedResult();
}
```

**Prevention:** Enforce `future.get(timeout, unit)` via code review checklist or custom SonarQube rule.

---

**Failure Mode 3: ExecutionException Cause Type Loss**
**Symptom:** Specific exception types from async tasks (e.g., `DatabaseException`) are handled as generic `Exception`, losing the ability to make specific recovery decisions.
**Root Cause:** `ExecutionException.getCause()` returns `Throwable` which is cast incorrectly or not at all.
**Diagnostic:**

```bash
grep -n "ExecutionException" src/main/java/
# Look for getCause() that is not cast or type-checked
```

**Fix:**

```java
// BAD: catches ExecutionException but loses specific type
try { result = future.get(); }
catch (ExecutionException e) {
    throw new ServiceException(e); // wraps twice
}

// GOOD: unwrap and re-throw as specific type
try { result = future.get(); }
catch (ExecutionException e) {
    Throwable cause = e.getCause();
    if (cause instanceof DatabaseException dbEx) {
        throw dbEx; // propagate specific type
    }
    throw new ServiceException("Unexpected error", cause);
}
```

**Prevention:** Always inspect `getCause()` type before re-throwing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-008 - Callable]] - the task that produces the Future result
- [[JCC-025 - ExecutorService]] - the service that returns Futures from submitted tasks

**Builds On This (learn these next):**

- [[JCC-010 - CompletableFuture]] - the non-blocking, composable evolution of Future
- [[JCC-040 - Structured Concurrency]] - Java 21 alternative to Future-based task management

**Alternatives / Comparisons:**

- [[JCC-010 - CompletableFuture]] - adds callbacks, chaining, non-blocking composition
- [[JCC-040 - Structured Concurrency]] - lifetime-scoped task results without Future

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Handle to async computation result  │
│ PROBLEM       │ How to get result from async task?  │
│ KEY INSIGHT   │ Pull model: you come to get result  │
│ USE WHEN      │ Simple async task with a result     │
│ AVOID WHEN    │ Need callbacks/chaining (use CF)     │
│ TRADE-OFF     │ Simplicity vs. blocking get()        │
│ ONE-LINER     │ Future = ticket for async result     │
│ NEXT EXPLORE  │ JCC-010 CompletableFuture            │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `future.get()` blocks - always use `get(timeout, unit)` in production.
2. Exceptions are wrapped in `ExecutionException` - always call `getCause()` to unwrap.
3. `Future` has no callbacks - use `CompletableFuture` for non-blocking composition.

**Interview one-liner:**
"`Future<V>` is a handle to an asynchronous computation that allows blocking result retrieval via `get()`, cooperative cancellation, and done-checking - it is the foundation of Java async results but lacks the non-blocking composition capabilities of `CompletableFuture`."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any async operation needs two things: a way to start the operation (submit a task) and a way to retrieve the result (the handle). Separating these two concerns lets the caller decide when to retrieve the result - enabling overlap of the caller's work with the async computation. `Future` is the minimal implementation of this separation.

**Where else this pattern appears:**

- **JavaScript Promises:** A `Promise` is a `Future`. `promise.then()` is `CompletableFuture.thenApply()`. `await promise` is `future.get()`. The evolution from callbacks → Promises → async/await mirrors Java's evolution from `Runnable` → `Future` → `CompletableFuture`.
- **Python `concurrent.futures.Future`:** Identical API to Java `Future`: `result()` (blocking get), `cancel()`, `done()`. Added `add_done_callback()` for event-based completion (Java equivalent: `CompletableFuture.thenAccept()`).
- **Go channels:** `chan<- int` is conceptually a single-slot `Future`: a goroutine sends the result, the main goroutine receives it (blocking). Multiple results use buffered channels (`BlockingQueue` equivalent).

---

### 💡 The Surprising Truth

`Future.cancel(true)` does not actually cancel the computation in the way most developers expect. Setting `mayInterruptIfRunning=true` sends an interrupt to the executing thread. But a task doing pure CPU computation (sorting, encoding, cryptography) with no `sleep()`, `wait()`, or I/O calls will never observe the interrupt. `future.cancel(true)` on a CPU-bound task with no interrupt checks is effectively a no-op that merely marks the `Future` as cancelled - the task continues running until completion, using CPU resources the entire time. True cancellation requires the task to explicitly check `Thread.currentThread().isInterrupted()` in its computation loop.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** `Future.isDone()` returns `true` for both successfully completed tasks AND cancelled tasks AND tasks that threw exceptions. Why is this the correct design? What is the implication for code that checks `isDone()` before calling `get()`?
_Hint:_ Consider the state machine: NORMAL, EXCEPTIONAL, CANCELLED are all "done" states. What does the caller need to know beyond "done"?

**Q2 (B - Scale):** A service has 1,000 active `Future` objects, each representing an ongoing HTTP call. At peak, all 1,000 complete within the same 100ms window. What happens to the 1,000 threads blocked on `future.get()`? What are the OS-level implications of unblocking 1,000 threads simultaneously?
_Hint:_ Consider the OS scheduler's work to reschedule 1,000 threads and what happens to CPU cache locality.

**Q3 (C - Design Trade-off):** `CompletableFuture` extends `Future<V>`. Does this mean `CompletableFuture` is always the better choice over `Future`? What are the cases where the simpler `Future` API (as implemented by `FutureTask`) is preferable?
_Hint:_ Consider API surface area, readability, and the cost of the extra machinery in `CompletableFuture` for simple fire-and-retrieve scenarios.
