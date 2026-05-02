---
layout: default
title: "CompletableFuture"
parent: "Java Concurrency"
nav_order: 335
permalink: /java-concurrency/completable-future/
number: "0335"
category: Java Concurrency
difficulty: ★★★
depends_on: Future, Callable, Functional Interfaces, Lambda Expressions
used_by: Spring WebFlux, Reactive Programming, HTTP APIs
related: Future, Reactive Programming, ExecutorService
tags:
  - java
  - concurrency
  - async
  - deep-dive
  - java8
---

# 0335 — CompletableFuture

⚡ TL;DR — `CompletableFuture<T>` is a non-blocking async pipeline: chain transformations with `thenApply`, combine results with `thenCombine`, handle errors with `exceptionally` — all without blocking threads to wait for results.

| #0335 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Future, Callable, Functional Interfaces, Lambda Expressions | |
| **Used by:** | Spring WebFlux, Reactive Programming, HTTP APIs | |
| **Related:** | Future, Reactive Programming, ExecutorService | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`Future.get()` blocks the calling thread. To chain async operations (fetch service A, then use result to call service B, then combine with service C result), blocking `Future.get()` occupies real threads doing nothing but waiting:
```java
Future<A> fa = pool.submit(() -> callA());
A a = fa.get();             // Thread 1: blocked waiting
Future<B> fb = pool.submit(() -> callB(a));
B b = fb.get();             // Thread 1: blocked again
```
Two blocking waits = two threads occupied doing nothing. In a web server with 1,000 concurrent request pipelines, 2,000 threads are blocked waiting for I/O. The thread pool is exhausted.

**THE BREAKING POINT:**
A microservice gateway chains 5 downstream calls per request (auth, catalog, pricing, inventory, recommendations). With blocking `Future.get()`, each request occupies a thread for the entire 200ms chain. At 5,000 concurrent requests: 5,000 blocked threads. The JVM runs out of memory or degrades badly.

**THE INVENTION MOMENT:**
This is exactly why **`CompletableFuture`** was created — to chain async operations as callbacks without blocking any thread to wait, composing async pipelines that use threads only during actual computation, not during waiting.

---

### 📘 Textbook Definition

**`CompletableFuture<T>`** is a `Future<T>` implementation introduced in Java 8 that can be explicitly completed (by calling `complete(value)` or `completeExceptionally(ex)`) and supports non-blocking callback chaining. Key methods: `thenApply(fn)` — transform result; `thenCompose(fn)` — flat-map to another `CompletableFuture`; `thenCombine(other, fn)` — combine two independents; `thenAccept(consumer)` — consume result; `exceptionally(fn)` — handle exception; `handle(fn)` — handle both result and exception; `allOf(futures...)` — complete when all complete; `anyOf(futures...)` — complete when any completes. Static factory: `supplyAsync(supplier, executor)`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`CompletableFuture` lets you describe an async pipeline — "when A finishes, do B, then C" — without any thread blocking to wait.

**One analogy:**
> A smart coffee machine: start the beans grinding (`supplyAsync`). When done, the grinder automatically starts the espresso (`thenApply`). When the espresso is ready, the machine automatically steams milk (`thenCompose`). If anything fails, it beeps for help (`exceptionally`). You walk away and come back to a finished drink — no waiting at each step.

**One insight:**
`CompletableFuture` enables "callback-driven" async: instead of blocking a thread to wait for A before starting B, you register "when A completes, start B." The thread is released immediately and only re-engaged when B needs to execute. This is the foundation of non-blocking I/O for Java web servers.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A `CompletableFuture` can be completed by any thread at any time, not just the executor that created it.
2. Callback registration (`.thenApply`, `.thenCompose`) returns a NEW `CompletableFuture` representing the chained result.
3. If the future is already complete when a callback is registered, the callback executes immediately (synchronously or in the notifying thread).

**DERIVED DESIGN:**
Given invariant 2, chaining creates an immutable DAG of `CompletableFuture` nodes. The terminal node fires when all upstream nodes complete. Intermediate nodes fire in whatever thread completes the upstream.

```
┌────────────────────────────────────────────────┐
│   CompletableFuture Pipeline                   │
│                                                │
│  supplyAsync(A)                                │
│      ↓ thenApply(B)   ← executes in pool      │
│      ↓ thenCompose(C) ← returns new CF        │
│      ↓ thenCombine(D) ← waits for D too       │
│      ↓ exceptionally  ← any failure handled   │
│      ↓ thenAccept     ← final consumer        │
│                                                │
│  No thread blocked at any stage —             │
│  each stage fires when upstream completes      │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Non-blocking; composable pipelines; error handling at any point; combines multiple async operations; integrates with reactive frameworks.
**Cost:** Complex debugging (no linear stack trace); exception semantics require care (unhandled exceptions silently swallowed); thread pool for callbacks matters (avoid using network thread pool for CPU callbacks); hard to cancel mid-chain.

---

### 🧪 Thought Experiment

**SETUP:**
A user profile endpoint: fetch user, fetch preferences, combine into ProfileResponse.

WITH BlockING Future:
```java
User user = pool.submit(() -> fetchUser(id)).get(); // blocks T1
Prefs prefs = pool.submit(()->fetchPrefs(id)).get();// blocks T1 again
return new ProfileResponse(user, prefs);
// Total time: userFetch + prefsFetch (sequential)
// Thread T1 spent entire time doing 0 computation
```

WITH CompletableFuture (parallel, non-blocking):
```java
CompletableFuture<User> userCF =
    CompletableFuture.supplyAsync(() -> fetchUser(id), pool);
CompletableFuture<Prefs> prefsCF =
    CompletableFuture.supplyAsync(() -> fetchPrefs(id), pool);
return userCF.thenCombine(prefsCF, ProfileResponse::new)
             .get(); // one final block, or .join()
// Total time: max(userFetch, prefsFetch) — parallel!
// T1 submits and registers callback — doesn't block during fetch
```

**THE INSIGHT:**
`thenCombine` runs when BOTH are complete — the callback is registered, not blocked. Thread T1 is freed immediately after `supplyAsync`. The combines fires in whatever thread finishes last. Total time = max(userFetch, prefsFetch), not sum.

---

### 🧠 Mental Model / Analogy

> `CompletableFuture` is a promise chain. You set up a chain of "promises": "promise to fetch user, then when done, promise to transform, then when done, promise to send response." You hand off the chain setup and walk away. The chain self-executes — each link fires when the previous one completes, driven by events, not blocked threads.

- "Promise to do X after Y" → `.thenApply()`, `.thenCompose()`.
- "Promise to handle both value and error" → `.handle()`.
- "Collect the chain's final result" → `.get()` or `.join()`.

Where this analogy breaks down: Promise chains in JavaScript execute in the event loop (single-threaded). Java `CompletableFuture` chains execute in thread pools — multiple threads can process different stages simultaneously, with ordering governed by the data dependency graph.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`CompletableFuture` lets you write "do A, then with A's result do B, then with B's result do C" without your main code waiting during each step. The steps happen automatically when each finishes.

**Level 2 — How to use it (junior developer):**
`CompletableFuture.supplyAsync(() -> value, executor)` starts async computation. `.thenApply(Function)` transforms the result. `.thenAccept(Consumer)` consumes it. `.exceptionally(Function)` handles exceptions. `.join()` blocks to get the final result (like `get()` but throws unchecked `CompletionException`). Use `thenCompose` when your transformation returns another `CompletableFuture` (to avoid nesting).

**Level 3 — How it works (mid-level engineer):**
Internally, `CompletableFuture` stores a linked list of `Completion` objects (callbacks). On completion, it iterates the list and fires each callback. The callback is submitted to the thread pool (`thenApplyAsync`) or runs in the completing thread (`thenApply` without "Async"). `allOf(cfs...)` creates an internal aggregator that completes when all inputs complete using a count-down mechanism. Error propagation: if any stage throws, subsequent `thenX` stages are skipped; `exceptionally` fires IF there's an exception, `handle` fires always.

**Level 4 — Why it was designed this way (senior/staff):**
`CompletableFuture` was designed as a bridge between Java's thread-based model and reactive programming. The design explicitly supports both "synchronous" callbacks (in the completing thread — fast but couples caller and I/O threads) and "async" callbacks (in a pool — decoupled but requires executor choice). The lack of backpressure distinguishes `CompletableFuture` from reactive streams (Project Reactor, RxJava): `CompletableFuture` is for single values (request-response); reactive streams are for sequences under load. In practice, Spring WebFlux wraps `CompletableFuture` patterns into `Mono<T>` for backpressure-aware reactive HTTP handling.

---

### ⚙️ How It Works (Mechanism)

**Basic pipeline:**
```java
ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();

CompletableFuture<String> pipeline =
    CompletableFuture
        .supplyAsync(() -> fetchOrder(orderId), pool)     // step 1
        .thenApply(order -> enrich(order))                 // step 2
        .thenApply(enriched -> serialize(enriched))        // step 3
        .exceptionally(ex -> {
            log.error("Pipeline failed", ex);
            return "{}"; // fallback
        });

String result = pipeline.join(); // block for final result
```

**Combining independent Futures:**
```java
CompletableFuture<User>  userCF  =
    CompletableFuture.supplyAsync(() -> getUser(id), pool);
CompletableFuture<Order> orderCF =
    CompletableFuture.supplyAsync(() -> getOrder(id), pool);

// Combine when both complete:
String response = userCF
    .thenCombine(orderCF, (user, order) ->
        buildResponse(user, order))
    .join();
```

**Wait for all:**
```java
List<CompletableFuture<Void>> sends = emails.stream()
    .map(email -> CompletableFuture.runAsync(
        () -> sendEmail(email), pool
    ))
    .collect(toList());

CompletableFuture.allOf(sends.toArray(new CompletableFuture[0]))
    .join(); // waits for all sends to complete
```

**Error handling at each stage:**
```java
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(data -> process(data))       // skipped if fetchData failed
    .exceptionally(ex -> defaultData())    // handles failure, returns default
    .thenApply(d -> serialize(d))           // runs with real or default data
    .handle((result, ex) -> {              // always runs; both available
        if (ex != null) return "error";
        return result;
    });
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[supplyAsync(() -> fetchUser(id), pool)]  ← YOU ARE HERE
    → [Pool thread T1: fetchUser() runs]
    → [T1 completes: result stored, callbacks fired]
    → [thenApply callback: T1 or new thread transform(user)]
    → [thenCombine: waits for both futures, fires when ready]
    → [pipeline completes → .join() returns]
```

**FAILURE PATH:**
```
[fetchUser() throws RuntimeException]
    → [CF marked exceptional]
    → [thenApply callbacks SKIPPED]
    → [exceptionally(ex -> ...) fires]
    → [Returns fallback value]
    → [downstream stages continue with fallback]
```

**WHAT CHANGES AT SCALE:**
At high scale, the choice of executor for async callbacks is critical. Using `ForkJoinPool.commonPool()` (the default for `thenApplyAsync` with no executor) for I/O callbacks starves CPU tasks. Use a dedicated executor for I/O-bound callback chains. Virtual threads (Java 21) simplify this: `Executors.newVirtualThreadPerTaskExecutor()` scales to millions of concurrent I/O operations without thread starvation.

---

### 💻 Code Example

Example 1 — HTTP request pipeline:
```java
CompletableFuture<ApiResponse> apiPipeline(String userId) {
    return CompletableFuture
        .supplyAsync(() -> authService.validateUser(userId), ioPool)
        .thenCompose(user ->
            CompletableFuture.supplyAsync(
                () -> dataService.fetch(user.getId()), ioPool
            )
        )
        .thenApply(data -> ApiResponse.of(data))
        .exceptionally(ex -> ApiResponse.error(ex.getMessage()));
}
// No thread blocked during HTTP calls
```

Example 2 — Timeout handling:
```java
CompletableFuture<Report> reportFuture =
    CompletableFuture.supplyAsync(() -> generateReport(), pool);

// Java 9+: orTimeout replaces manual cancel
Report report = reportFuture
    .orTimeout(10, TimeUnit.SECONDS)  // fails with TimeoutException
    .exceptionally(ex -> Report.fallback())
    .join();
```

Example 3 — anyOf for first-wins:
```java
// Race multiple caches, use first to respond:
CompletableFuture<String> local  =
    CompletableFuture.supplyAsync(() -> localCache.get(key));
CompletableFuture<String> remote =
    CompletableFuture.supplyAsync(() -> remoteCache.get(key));

String value = (String) CompletableFuture
    .anyOf(local, remote)
    .join(); // first to complete wins
```

---

### ⚖️ Comparison Table

| API | Non-blocking | Chain | Error Handling | Best For |
|---|---|---|---|---|
| `Future.get()` | No (blocks) | Manual | ExecutionException | Simple request-response |
| **CompletableFuture** | Yes | Fluent API | exceptionally/handle | Chained async operations |
| Project Reactor Mono | Yes | Backpressure | onError | Reactive streams with load control |
| RxJava Observable | Yes | Rich operators | onError | Event sequences/streams |

How to choose: Use `CompletableFuture` for async pipelines involving single results. Use `Mono/Flux` (Reactor) for reactive HTTP endpoints with backpressure. Use `Future` only for simple blocking result retrieval.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CompletableFuture exceptions are automatically logged | Unhandled exceptions in `thenApply` or `supplyAsync` are silently swallowed unless `.exceptionally()` or `.handle()` are added AND the final `CompletableFuture` is observed |
| `thenApply` always runs in a different thread | `thenApply` (without "Async") runs in the completing thread or the calling thread if already complete. For thread pool control, use `thenApplyAsync(fn, executor)` |
| `CompletableFuture.allOf()` returns results | `allOf()` returns `CompletableFuture<Void>` — you must retrieve individual results from each input future after `allOf().join()` |
| `join()` is safer than `get()` | Both block. `join()` throws `CompletionException` (unchecked); `get()` throws `ExecutionException` (checked). `join()` is more convenient; `get()` forces explicit exception handling |
| CompletableFuture supports backpressure | No — `CompletableFuture` is for single values, not streams. For backpressure over sequences, use Reactor `Flux` or reactive streams |

---

### 🚨 Failure Modes & Diagnosis

**Silent Exception Swallowing**

**Symptom:** Pipeline appears to run but produces no output. No exception logged.

**Root Cause:** `CompletableFuture` without exception handling; exception in a stage swallows silently.

**Fix:**
```java
// Always add exception handler or observe the future:
CompletableFuture.supplyAsync(() -> riskyOp(), pool)
    .thenApply(this::transform)
    .exceptionally(ex -> {
        log.error("Pipeline failed", ex);
        return null;
    })
    .thenAccept(result -> {
        if (result != null) handle(result);
    });
```

**Prevention:** Every `CompletableFuture` chain must have at least one `exceptionally` or `handle` to prevent silent failure.

---

**Thread Pool Starvation from Sync Callbacks**

**Symptom:** I/O thread pool fully occupied with computation tasks; application latency spikes.

**Root Cause:** CPU-bound callbacks registered with `thenApply` (not `thenApplyAsync`) run in the I/O thread that completed the upstream future.

**Fix:**
```java
// BAD: CPU compute runs in I/O thread
CompletableFuture.supplyAsync(() -> fetchFromDB(), ioPool)
    .thenApply(data -> heavyCPUTransform(data)); // runs in ioPool!

// GOOD: separate pools for I/O and CPU
CompletableFuture.supplyAsync(() -> fetchFromDB(), ioPool)
    .thenApplyAsync(data -> heavyCPUTransform(data), cpuPool);
```

**Prevention:** Use `thenXxxAsync(fn, executor)` for callbacks that should not run in the upstream's thread.

---

**allOf Not Propagating Individual Errors**

**Symptom:** `allOf().join()` completes but individual futures have exceptions. Results treated as null.

**Root Cause:** `allOf()` completes normally even if individual futures failed. Each future must be checked separately.

**Fix:**
```java
CompletableFuture<Void> all = CompletableFuture.allOf(f1, f2, f3);
all.join();
// Check each individually:
List.of(f1, f2, f3).forEach(f -> {
    if (f.isCompletedExceptionally()) {
        f.exceptionally(ex -> { log.error("Failed", ex); return null; })
         .join();
    }
});
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Future` — `CompletableFuture` extends `Future`; understanding `Future`'s blocking model explains why `CompletableFuture` exists
- `Callable` — `supplyAsync` accepts `Supplier<T>` which plays the same role as `Callable<T>`
- `Functional Interfaces` — all `CompletableFuture` callbacks are functional interfaces (`Function`, `Consumer`, `BiFunction`)

**Builds On This (learn these next):**
- `Reactive Programming` — `CompletableFuture` is the single-value async model; reactive streams extend it to sequences with backpressure
- `Spring WebFlux` — uses `Mono<T>` (Project Reactor) built on similar principles to `CompletableFuture`

**Alternatives / Comparisons:**
- `Future` — simpler, blocking alternative; use when chaining is not needed
- `Reactive Programming (Mono/Flux)` — for sequences and backpressure; the multi-value generalisation of `CompletableFuture`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Non-blocking async pipeline: chain        │
│              │ transformations without blocking threads  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Future.get() blocks threads; chaining     │
│ SOLVES       │ async operations requires manual blocking │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ thenApply runs in completing thread;      │
│              │ thenApplyAsync runs in specified pool.    │
│              │ Exceptions silently swallowed without     │
│              │ exceptionally/handle                      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Chained async computations, parallel      │
│              │ service calls, non-blocking HTTP handlers │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Streams of data (use Reactor Flux);       │
│              │ when backpressure is needed               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Non-blocking scalability vs complex debug;│
│              │ callbacks vs linear code readability      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Define the pipeline now, run it later,   │
│              │  no thread blocked while waiting"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread Lifecycle → synchronized →         │
│              │ Reactive Programming (Reactor)            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service uses a `CompletableFuture` chain: `supplyAsync(A, ioPool).thenApply(B).thenApplyAsync(C, cpuPool).thenApply(D)`. A peak load, the I/O pool has 20 threads, the CPU pool has 8 threads. Trace: in which thread does each step (A, B, C, D) execute? What happens when step A completes but the CPU pool is fully occupied when `thenApplyAsync(C)` fires? What is the queue depth for the CPU pool under sustained load, and what change prevents CPU pool queue from growing unboundedly?

**Q2.** `CompletableFuture` has no native backpressure mechanism. A service uses `CompletableFuture.supplyAsync()` to handle incoming events — 100,000 events/second arrive, each `supplyAsync` submitting to a bounded executor of 100 threads. The executor's queue depth grows without bound. Explain exactly when the queue starts growing (what conditions trigger it), why the JVM eventually runs out of heap (describe the memory growth path precisely), and compare THREE different approaches to add backpressure — one using `CompletableFuture` with a `RejectedExecutionHandler`, one using Project Reactor, and one using a `BlockingQueue` — assessing the trade-offs for each.

