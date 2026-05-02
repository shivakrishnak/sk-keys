---
layout: default
title: "Future"
parent: "Java Concurrency"
nav_order: 334
permalink: /java-concurrency/future/
number: "0334"
category: Java Concurrency
difficulty: ★★☆
depends_on: Callable, Runnable, Thread (Java), ExecutorService
used_by: CompletableFuture, ExecutorService
related: CompletableFuture, Callable, ExecutorService
tags:
  - java
  - concurrency
  - async
  - intermediate
  - future
---

# 0334 — Future

⚡ TL;DR — `Future<V>` is a handle to a pending async computation — submit a task to an executor, get a `Future`, check or wait for the result later — decoupling task submission from result retrieval.

| #0334 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Callable, Runnable, Thread (Java), ExecutorService | |
| **Used by:** | CompletableFuture, ExecutorService | |
| **Related:** | CompletableFuture, Callable, ExecutorService | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
After submitting an async task, how do you get its result? With `Runnable`, you have no return path. You'd store results in shared state and use `CountDownLatch` or `Object.wait/notify` to poll for completion — custom synchronisation for every result-retrieval case. Different async APIs use different completion signals — no standard contract for "is the task done and what did it return?"

**THE BREAKING POINT:**
A service submits 10 database queries in parallel using raw `Thread` objects. The calling code uses 10 `AtomicReference<Result>` fields plus a `CountDownLatch(10)`. The result collection code is 30 lines of boilerplate. Adding exception handling doubles it. Adding timeout support doubles it again.

**THE INVENTION MOMENT:**
This is exactly why **`Future<V>`** was created — to be the standard contract for "I will give you the result eventually" — handling waiting, result retrieval, exception propagation, timeout, and cancellation in one standard interface.

---

### 📘 Textbook Definition

**`Future<V>`** is an interface in `java.util.concurrent` introduced in Java 5 representing the result of an asynchronous computation. It provides: `get()` — blocks until result is available; `get(timeout, unit)` — blocks with a time limit; `isDone()` — non-blocking check; `isCancelled()` — check if cancelled; `cancel(mayInterruptIfRunning)` — attempt cancellation. `Future` is typically obtained by submitting a `Callable<V>` to an `ExecutorService`. `FutureTask<V>` is the standard implementation — it implements both `Future<V>` and `Runnable`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`Future<V>` is a promise of a result: submit now, retrieve later when ready.

**One analogy:**
> Ordering a custom item online: you complete the order (submit task), get a tracking number (`Future`), go about your day (`other work`), then check tracking (`isDone()`) or wait at home for delivery (`get()`). The store handles production asynchronously.

**One insight:**
`Future.get()` blocks — this is both its power and its limitation. Calling it immediately after submission negates the concurrency benefit. The pattern is: submit ALL tasks first → do other work → collect results. `CompletableFuture` (Java 8) solves the blocking problem with non-blocking callbacks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A `Future` can be in three states: incomplete, completed (with value), or completed (with exception), or cancelled.
2. `get()` blocks if not yet complete and returns the value (or throws) once available.
3. Cancellation attempts to prevent the task from running; if already running, only interrupts if `mayInterruptIfRunning=true`.

**DERIVED DESIGN:**
`FutureTask<V>` is both `Runnable` and `Future<V>`. When submitted to an executor:
- Executor calls `FutureTask.run()` on a worker thread.
- `run()` calls the wrapped `Callable.call()`.
- On completion: stores result/exception, unparks waiting `get()` callers.

```
┌────────────────────────────────────────────────┐
│        Future State Machine                    │
│                                                │
│  NEW ──→ COMPLETING ──→ NORMAL (value set)    │
│       └──→ COMPLETING ──→ EXCEPTIONAL (ex set)│
│       └──→ CANCELLED                          │
│       └──→ INTERRUPTING ──→ INTERRUPTED       │
│                                                │
│  get() blocks while in NEW or COMPLETING      │
│  get() returns/throws in NORMAL/EXCEPTIONAL   │
│  get() throws CancellationException           │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Standard result retrieval interface; exception propagation; timeout; cancellation.
**Cost:** `get()` is synchronous/blocking; no chaining or composition; cannot react to completion without polling; `cancel()` doesn't guarantee task termination.

---

### 🧪 Thought Experiment

**SETUP:**
Two long-running computations needed for a report. Submit both, collect both results.

WITHOUT Future (submit-then-wait pattern error):
```java
Future<Report1> f1 = pool.submit(() -> computeReport1());
Report1 r1 = f1.get(); // BLOCKS until report1 done (5 sec)
Future<Report2> f2 = pool.submit(() -> computeReport2());
Report2 r2 = f2.get(); // BLOCKS until report2 done (5 sec)
// Total: 10 seconds — sequential!
```

WITH Future (parallel pattern):
```java
Future<Report1> f1 = pool.submit(() -> computeReport1());
Future<Report2> f2 = pool.submit(() -> computeReport2());
// Both submitted and running concurrently
Report1 r1 = f1.get(); // waits for report1
Report2 r2 = f2.get(); // report2 may already be done
// Total: max(5, 5) = 5 seconds — parallel!
```

**THE INSIGHT:**
The key to using `Future` correctly is **submitting before blocking**. Each `get()` blocks only on its specific task; parallel tasks run simultaneously. Submit all first, block for results later.

---

### 🧠 Mental Model / Analogy

> A `Future` is a claim ticket at a dry cleaner. You drop off your clothes (submit task), get a numbered ticket (`Future`). You can come back and check ("is order #42 ready?" — `isDone()`). When you show up, you either get your clothes or hear "we had a problem" (`ExecutionException`). You can also say "I changed my mind, discard it" (`cancel()`).

- "Claim ticket" → `Future<V>` reference.
- "Coming back to check" → `isDone()`.
- "Blocking at the counter" → `get()`.
- "Problem with order" → `ExecutionException(cause)`.

Where this analogy breaks down: A dry cleaner gives you your item and you keep it. `Future.get()` can be called multiple times — after the first call, the result is cached and returned immediately.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`Future` is a placeholder for a result that isn't ready yet. You get one when you submit background work, and you use it later to get the result.

**Level 2 — How to use it (junior developer):**
Submit a `Callable` to an executor, get a `Future`. Call `get()` when you need the result (it waits). Use `get(5, SECONDS)` to limit waiting. Use `isDone()` to check without blocking. Catch `ExecutionException` to get the task's thrown exception, `TimeoutException` for timeout, `InterruptedException` from the calling thread being interrupted.

**Level 3 — How it works (mid-level engineer):**
`FutureTask` uses an internal state variable (an `int`) and `Unsafe.park/unpark` for blocking `get()`. When the task completes (`run()` returns), the state transitions atomically from `NEW→COMPLETING→NORMAL` (or `EXCEPTIONAL`). All waiting `get()` callers are unparked (`LockSupport.unpark`). Result is stored as `Object outcome`.

**Level 4 — Why it was designed this way (senior/staff):**
`Future` was designed in JSR 166 (2004) as a minimal contract for async result retrieval. The blocking `get()` was a deliberate design choice for the era: hardware was transitioning to multi-core, and the primary use case was "parallelize CPU-bound work and collect results." The limitation (blocking, no callbacks) was addressed in Java 8 with `CompletableFuture`, which provides non-blocking `.thenApply()`, `.thenCompose()`, and `.handle()` — a reactive model. `Future` remains in use for `ExecutorService.submit()` compatibility.

---

### ⚙️ How It Works (Mechanism)

```java
ExecutorService pool = Executors.newFixedThreadPool(4);

// Submit callable, get Future immediately (non-blocking):
Future<String> future = pool.submit(
    () -> fetchUser(userId)  // Callable<String>
);

// Do other work here while task runs...

// Retrieve result (blocks if not done):
try {
    String user = future.get();
    System.out.println(user);
} catch (ExecutionException e) {
    log.error("Fetch failed", e.getCause());
} catch (TimeoutException e) {
    future.cancel(true);    // cancel if timeout
    log.warn("Fetch timed out for " + userId);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}

// Non-blocking check:
if (future.isDone()) {
    // Result available (or exception, or cancelled)
}
if (future.isCancelled()) {
    // Was cancelled before completion
}
```

**Parallel task submission pattern (correct):**
```java
// CORRECT: submit all, THEN collect
List<Future<Data>> futures = ids.stream()
    .map(id -> pool.submit(() -> fetch(id)))
    .collect(toList());

// All tasks running in parallel now
List<Data> results = futures.stream()
    .map(f -> {
        try { return f.get(5, SECONDS); }
        catch (Exception e) { throw new RuntimeException(e); }
    })
    .collect(toList());
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[submit(callable)] → [FutureTask created]     ← YOU ARE HERE
    → [Worker thread executes callable.call()]
    → [Result stored in FutureTask.outcome]
    → [State: NEW → COMPLETING → NORMAL]
    → [LockSupport.unpark(waiting threads)]
    → [future.get() returns stored value V]
```

**FAILURE PATH:**
```
[callable throws RuntimeException]
    → [FutureTask state: EXCEPTIONAL]
    → [Exception stored in outcome]
    → [future.get() throws ExecutionException]
    → [getCause() → original RuntimeException]
```

**WHAT CHANGES AT SCALE:**
At scale, blocking `future.get()` in a loop creates a bottleneck — results are processed sequentially. Use `CompletableFuture` for reactive, non-blocking result handling. For batch processing, `ExecutorService.invokeAll()` submits all and returns when all complete (more efficient than manual submit + get loop).

---

### 💻 Code Example

Example 1 — Parallel data fetch:
```java
List<Future<User>> futures = userIds.stream()
    .map(id -> pool.submit(() -> userRepo.findById(id)))
    .collect(toList());

// Collect with error handling:
List<User> users = new ArrayList<>();
for (Future<User> f : futures) {
    try {
        users.add(f.get(3, SECONDS));
    } catch (ExecutionException e) {
        log.error("User fetch failed", e.getCause());
    } catch (TimeoutException e) {
        f.cancel(true);
        log.warn("User fetch timed out");
    }
}
```

Example 2 — Timeout + cancellation:
```java
Future<Report> report = pool.submit(() -> generateReport());
try {
    return report.get(30, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    report.cancel(true);    // interrupt the report thread
    throw new ServiceUnavailableException("Report timeout");
}
```

---

### ⚖️ Comparison Table

| API | Blocking | Callbacks | Chain | Cancel | Best For |
|---|---|---|---|---|---|
| **Future** | Yes (get) | No | No | Yes (best-effort) | Simple async result retrieval |
| CompletableFuture | Optional | Yes (thenX) | Yes | Yes | Async pipelines, reactive chains |
| ListenableFuture (Guava) | Yes | Yes | Yes | Yes | Guava-based callbacks |

How to choose: Use `Future` for simple "submit then collect" patterns. Use `CompletableFuture` for async chains, reactive handling, or when blocking is unacceptable.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `future.get()` returns null if not ready | `get()` BLOCKS until ready — it does NOT return null. `isDone()` is the non-blocking check |
| `cancel(true)` guarantees task termination | If the task doesn't check `Thread.isInterrupted()` inside its `call()`, the interrupt signal is ignored and the task runs to completion |
| `isDone() == true` means task succeeded | `isDone()` returns true for completion (success, exception, OR cancellation). Check `isCancelled()` and `get()` to determine how it completed |
| `Future` supports result callbacks | Standard `Future` has no callback mechanism. You must poll (`isDone()`) or block (`get()`). Use `CompletableFuture` for callbacks |

---

### 🚨 Failure Modes & Diagnosis

**Blocking get() Negating Parallelism**

**Symptom:** "Parallel" code runs sequentially — total time = sum of all task times.

**Root Cause:** `submit()` followed immediately by `get()` before submitting other tasks.

**Fix:** Submit all tasks, store futures in a list, then iterate and call `get()`.

---

**Swallowed ExecutionException**

**Symptom:** Task failed silently. No exception visible to caller.

**Root Cause:** `ExecutionException` caught but cause not extracted or rethrown.

**Fix:**
```java
try { return f.get(); }
catch (ExecutionException e) {
    throw new RuntimeException(e.getCause()); // propagate cause
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Callable` — `Future` is the result handle for `Callable` tasks submitted to executors
- `ExecutorService` — the API that produces `Future` objects via `submit()`

**Builds On This (learn these next):**
- `CompletableFuture` — non-blocking, callback-based evolution of `Future` (Java 8+)

**Alternatives / Comparisons:**
- `CompletableFuture` — richer, non-blocking alternative; preferred for new code

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Handle to a pending async result:         │
│              │ submit now, retrieve later via get()      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No standard contract for "give me the     │
│ SOLVES       │ result of this async work"                │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Submit ALL tasks before calling get() on  │
│              │ ANY of them. get() blocks the caller.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple submit-and-collect async patterns  │
│              │ with ExecutorService                      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Chained async steps — use CompletableFuture│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple contract vs blocking; no callbacks │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Submit now, claim ticket, retrieve later"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CompletableFuture → ExecutorService →     │
│              │ Thread Lifecycle                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service that calls two external APIs in parallel and combines their results uses `Future<A> fa = pool.submit(callA)` and `Future<B> fb = pool.submit(callB)`, then calls `fa.get()` followed by `fb.get()`. CallA takes 3 seconds; callB takes 1 second. Trace the execution timeline and explain: why the total wait time is 3 seconds (not 4), what happens if callB completes while the caller is blocked on `fa.get()`, and why `fb.get()` returns immediately even though the caller just finished waiting for `fa`.

**Q2.** `future.cancel(true)` is documented as "best-effort" cancellation. Design a scenario where a Callable task does NOT terminate after `cancel(true)` is called, involving all three of: (1) the task ignores `InterruptedException`; (2) the task stores a reference to the `FutureTask`; (3) the code calling `future.isCancelled()` returns true. Explain why all three conditions can coexist and what the developer must do in the `call()` implementation to make cancellation reliable.

