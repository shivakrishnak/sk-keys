---
layout: default
title: "Future and CompletableFuture"
parent: "Java Concurrency"
nav_order: 75
permalink: /java-concurrency/future-and-completablefuture/
---
# 075 — Future & CompletableFuture

`#java` `#concurrency` `#async` `#future` `#completablefuture`

⚡ TL;DR — `Future<T>` is a promise of an async result, retrieved by blocking `.get()`; `CompletableFuture<T>` extends it with non-blocking composition pipelines (thenApply, thenCompose, allOf) and explicit completion, enabling true async programming without blocking threads.

| #075 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ExecutorService, Callable, Thread, Runnable vs Callable | |
| **Used by:** | Async APIs, Spring Async, Reactive Streams, Non-blocking IO | |

---

### 📘 Textbook Definition

**`Future<V>`** represents the result of an asynchronous computation. It provides: `get()` (blocking), `get(timeout, unit)` (bounded blocking), `isDone()`, `cancel()`, `isCancelled()`. **`CompletableFuture<T>`** (Java 8) implements both `Future<T>` and `CompletionStage<T>`, adding: non-blocking callbacks (`thenApply`, `thenAccept`, `thenRun`), composition (`thenCompose`, `thenCombine`), fan-out (`allOf`, `anyOf`), explicit completion (`complete`, `completeExceptionally`), and exception handling (`exceptionally`, `handle`). Stages run on the common `ForkJoinPool` by default, or on a provided `Executor`.

---

### 🟢 Simple Definition (Easy)

`Future` is a "ticket" for a result not yet available. You submit work, get a ticket, do other things, then hand in the ticket when you need the result — but you MUST wait at the counter. `CompletableFuture` is a smarter ticket: "When the result is ready, automatically do this next step, then that step, without anyone waiting at a counter." It chains work.

---

### 🔵 Simple Definition (Elaborated)

`Future` is limited: the only way to get the result is to call `.get()` which blocks your calling thread until the async work finishes. This means "async" code often ends up blocking. `CompletableFuture` solves this with callbacks: instead of blocking to get a value, you register what to do WHEN the value arrives — the callback runs in a thread pool automatically. You can chain many transformations, combine results from multiple async operations, and handle errors — all without blocking a single thread.

---

### 🔩 First Principles Explanation

**Future — the blocking model:**

```
Main Thread:                       Worker Thread:
  submit(task) ───────────────→   running task...
  ← Future f returned              ...computes result
  do other work...                 result ready
  f.get()  ← BLOCKS HERE ─────→  ← result returned
  continue with result
```

**CompletableFuture — the callback model:**

```
Main Thread:                       Worker Thread(s):
  submit(task)                     running task...
  .thenApply(transform)            result ready
  .thenAccept(consume)          →  transform() runs (pool thread)
  .exceptionally(handle)        →  consume() runs (pool thread)
  ← returns immediately            all done — no main thread blocked

Key insight: the pipeline is defined upfront; execution happens asynchronously
```

**CompletionStage chain:**

```
CF<A> ──thenApply(A→B)──→ CF<B> ──thenApply(B→C)──→ CF<C>
              ↑                            ↑
     runs when A ready           runs when B ready
     returns B                   returns C

Each stage produces a NEW CompletableFuture
The chain is lazy: registered, runs only when previous stage completes
```

---

### ❓ Why Does This Exist — Why Before What

```
Without CompletableFuture (just Future):
  1. Every async result requires a blocking .get() call
  2. Cannot compose: "fetch A, then use A to fetch B, then combine with C"
     without multiple blocking waits
  3. Exception handling is clunky (ExecutionException wrapper)
  4. Cannot complete a Future explicitly (mock/test difficulty)

With CompletableFuture (Java 8+):
  ✅ Chain transformations: .thenApply(), .thenCompose()
  ✅ Combine results: .thenCombine(), .allOf(), .anyOf()
  ✅ Exception recovery: .exceptionally(), .handle()
  ✅ Explicit completion: .complete(value), .completeExceptionally(ex)
  ✅ Timeout: .orTimeout(), .completeOnTimeout() (Java 9+)
  ✅ Non-blocking pipelines: no threads blocked waiting
```

---

### 🧠 Mental Model / Analogy

> `Future` is a **blocking postal service** — you order a package (submit task), get a tracking number (Future), and then MUST stand at the post office until it arrives (blocking get). `CompletableFuture` is an **Amazon delivery with notifications** — you order, leave home, and get a notification when it arrives — then your phone automatically places the next order. You're never standing at a counter; everything happens when it's ready.

---

### ⚙️ How It Works — Key Methods

```
Future<T>:
  .get()                     block forever until done
  .get(timeout, unit)        block up to timeout; throws TimeoutException
  .isDone()                  non-blocking check
  .cancel(mayInterruptIfRunning)

CompletableFuture<T>:
  Creation:
  CF.supplyAsync(Supplier<T>)         async task returning T
  CF.supplyAsync(Supplier<T>, exec)   with custom executor
  CF.runAsync(Runnable)               async task, no result
  CF.completedFuture(value)           already-completed CF (useful in tests)

  Transformation (T → U):
  .thenApply(T → U)          transform result (runs in same pool thread)
  .thenApplyAsync(T → U)     transform in new pool thread
  .thenCompose(T → CF<U>)    chain async operations (flatMap equivalent)

  Side effects:
  .thenAccept(T → void)      consume result
  .thenRun(Runnable)         run after, ignore result

  Combining:
  .thenCombine(CF<U>, (T,U)→V)     combine two CFs into one
  CF.allOf(CF...)                  complete when ALL complete
  CF.anyOf(CF...)                  complete when ANY completes

  Error handling:
  .exceptionally(Throwable → T)    recover from exception
  .handle((T, Throwable) → U)      handle both success and failure
  .whenComplete((T, Throwable) → void)  side effect on either
```

---

### 🔄 How It Connects

```
Future<T>            (Java 5) — blocking, no composition
    ↑ implemented by
CompletableFuture<T> (Java 8) — non-blocking, pipeline composition
    ↑ also implements
CompletionStage<T>   — the composition contract
    │
    ├─ ForkJoinPool.commonPool() — default async thread pool
    │
    └─ Spring @Async → returns CompletableFuture
       Reactive Streams (Project Reactor) → Mono/Flux go further (lazy, backpressure)
```

---

### 💻 Code Example

```java
// Future — blocking style
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<String> future = pool.submit(() -> fetchFromApi("https://api.example.com/user/1"));

// Do other work while task runs...
doOtherWork();

// Must block to get result:
try {
    String result = future.get(5, TimeUnit.SECONDS); // block up to 5s
    processResult(result);
} catch (TimeoutException e) {
    System.err.println("Request timed out");
    future.cancel(true);
} catch (ExecutionException e) {
    System.err.println("Task failed: " + e.getCause());
}
```

```java
// CompletableFuture — pipeline style
CompletableFuture<String> pipeline = CompletableFuture
    .supplyAsync(() -> fetchUser("alice"))      // async: fetch user
    .thenApply(user -> enrichWithProfile(user)) // transform: add profile data
    .thenApply(user -> serialize(user))         // transform: to JSON
    .exceptionally(ex -> {                      // recover from any error
        log.error("Pipeline failed", ex);
        return "{\"error\": \"" + ex.getMessage() + "\"}";
    });

// Non-blocking registration of callback:
pipeline.thenAccept(json -> sendResponse(json)); // runs when pipeline finishes
// Main thread is free immediately — no blocking!
```

```java
// Combining two independent async calls
CompletableFuture<User>   userFuture   = CompletableFuture.supplyAsync(() -> fetchUser(id));
CompletableFuture<Orders> ordersFuture = CompletableFuture.supplyAsync(() -> fetchOrders(id));

// Wait for both, combine results
CompletableFuture<Dashboard> dashboard =
    userFuture.thenCombine(ordersFuture, (user, orders) -> new Dashboard(user, orders));
// Both run in parallel! Combined when BOTH are complete
```

```java
// allOf — wait for multiple async operations
List<String> urls = List.of("url1", "url2", "url3", "url4");
List<CompletableFuture<String>> futures = urls.stream()
    .map(url -> CompletableFuture.supplyAsync(() -> fetch(url)))
    .collect(Collectors.toList());

CompletableFuture<Void> allDone = CompletableFuture.allOf(
    futures.toArray(new CompletableFuture[0])
);

// When all complete, collect all results
allDone.thenApply(v ->
    futures.stream()
           .map(CompletableFuture::join)  // join() = get() without checked exception
           .collect(Collectors.toList())
).thenAccept(results -> processAll(results));
```

```java
// Java 9+: timeout handling
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> slowOperation())
    .orTimeout(3, TimeUnit.SECONDS)           // completes exceptionally if > 3s
    .exceptionally(ex -> "default-value");    // or provide fallback on timeout

// completeOnTimeout: provide default without exception:
CompletableFuture<String> future2 = CompletableFuture
    .supplyAsync(() -> slowOperation())
    .completeOnTimeout("fallback", 3, TimeUnit.SECONDS); // complete normally with fallback
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `.thenApply()` runs in a new thread | By default runs in the completing thread (or ForkJoinPool); use `thenApplyAsync` for new thread |
| `allOf()` returns all results | `allOf()` returns `CF<Void>` — you must get each future separately |
| `join()` is safer than `get()` | `join()` wraps checked exceptions in `CompletionException`; `get()` uses `ExecutionException` |
| `.cancel()` stops the running task | `cancel()` sets the future as cancelled but doesn't interrupt the underlying thread unless you handle it |
| CompletableFuture handles backpressure | CF has no backpressure — for backpressure use Reactive Streams (Project Reactor, RxJava) |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Running blocking code in CompletableFuture on ForkJoinPool**

```java
// Bad: DB call blocks a ForkJoinPool thread — starves other tasks
CompletableFuture.supplyAsync(() -> jdbcTemplate.query(...)); // ❌
// ForkJoinPool is shared and sized to CPU count — blocking it hurts throughput

// Fix: provide a dedicated executor for blocking I/O
ExecutorService ioPool = Executors.newFixedThreadPool(20);
CompletableFuture.supplyAsync(() -> jdbcTemplate.query(...), ioPool); // ✅
```

**Pitfall 2: Not handling exceptions — silent failures**

```java
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(d -> process(d));
// If fetchData() throws → exception propagates but nobody sees it
// Future is completed exceptionally but result is never retrieved

// Fix: always add exceptionally or handle
    .exceptionally(ex -> { log.error("Failed", ex); return fallback(); })
```

**Pitfall 3: Nested CompletableFuture — CF<CF<T>>**

```java
// ❌ Returns CF<CF<String>> — nested, must .get().get()
CompletableFuture<CompletableFuture<String>> nested =
    CompletableFuture.supplyAsync(() ->
        CompletableFuture.supplyAsync(() -> "result")
    );

// ✅ Use thenCompose (flatMap) to flatten one level:
CompletableFuture<String> flat =
    CompletableFuture.supplyAsync(() -> "userId")
        .thenCompose(userId ->
            CompletableFuture.supplyAsync(() -> fetchUser(userId))
        ); // returns CF<User>, not CF<CF<User>>
```

---

### 🔗 Related Keywords

- **[ExecutorService](./074 — ExecutorService.md)** — thread pool that runs CF stages
- **[Runnable vs Callable](./067 — Runnable vs Callable.md)** — the task interfaces CF wraps
- **[Race Condition](./072 — Race Condition.md)** — CF pipelines share state across threads; immutability recommended
- **Spring @Async** — annotate methods to return `CompletableFuture<T>` automatically
- **Project Reactor (Mono/Flux)** — go further with lazy, backpressured reactive streams

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Future = blocking result handle;              │
│              │ CompletableFuture = non-blocking pipeline     │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ CF: async fan-out/fan-in, chained transforms, │
│              │ parallel service calls, timeout handling      │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't block CF on ForkJoinPool (use IO pool); │
│              │ don't use CF for complex backpressure flows   │
│              │ (use Reactor/RxJava instead)                  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Future makes you wait; CompletableFuture     │
│              │  calls you back when it's ready"              │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ thenCompose → allOf → orTimeout →            │
│              │ Spring @Async → Project Reactor → Virtual Threads│
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `CompletableFuture.allOf(f1, f2, f3)` returns `CompletableFuture<Void>`. You need all three results. Write the idiomatic pattern to collect all results after `allOf` completes without blocking?

**Q2.** `thenApply` vs `thenCompose` — what is the difference? When must you use `thenCompose`? Give an example where `thenApply` produces a `CF<CF<T>>` and how `thenCompose` solves it.

**Q3.** A `CompletableFuture` pipeline has 5 stages. Stage 3 throws an exception. What happens to stages 4 and 5? Where does the exception first appear? How does `.handle()` behave differently from `.exceptionally()` in this scenario?

