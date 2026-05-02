---
layout: default
title: "Future"
parent: "Java Concurrency"
nav_order: 334
permalink: /java-concurrency/future/
number: "334"
category: Java Concurrency
difficulty: ★★☆
depends_on: Callable, ExecutorService, Thread (Java)
used_by: CompletableFuture, ForkJoinPool
tags:
  - java
  - concurrency
  - intermediate
---

# 334 — Future

`#java` `#concurrency` `#intermediate`

⚡ TL;DR — A handle to the result of an asynchronous computation — you can check if it's done, cancel it, or block to retrieve the result when needed.

| #334 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Callable, ExecutorService, Thread (Java) | |
| **Used by:** | CompletableFuture, ForkJoinPool | |

---

### 📘 Textbook Definition

`java.util.concurrent.Future<V>` is an interface representing the result of an asynchronous computation. It provides methods to check completion (`isDone()`), cancel execution (`cancel()`), and retrieve the result (`get()` — blocking until available, or with a timeout). `Future` is returned by `ExecutorService.submit(Callable<V>)` and `ExecutorService.submit(Runnable, V)`. A `Future` can be in one of three states: pending (not yet complete), completed normally (result available), or completed exceptionally (exception stored). Its principal limitation is that `get()` is a blocking call — it cannot register a callback to run when the result becomes available.

### 🟢 Simple Definition (Easy)

A Future is a placeholder for a result you haven't got yet — like a coffee shop number: the barista is making your coffee and you can check back later or wait at the counter.

### 🔵 Simple Definition (Elaborated)

When you submit a Callable to a thread pool, the pool starts working on it immediately and returns a Future to you right away. The Future doesn't have the result yet — it's a promise of a result. You can continue doing other things, and when you eventually need the result, you call `future.get()`. If the computation is done, you get the result immediately. If not, you block until it finishes. You can also set a timeout so you don't wait forever, or cancel the task if you need to. The main drawback: there's no way to say "call me when it's done" — for that, you need CompletableFuture.

### 🔩 First Principles Explanation

**The problem before Future:** Spawning a thread gave you no handle back. To know when the thread finished or get its result, you needed manual synchronisation — shared variables with volatile/locks, CountDownLatch etc. This was error-prone boilerplate.

**What Future gives you:**
1. A typed handle back from `executor.submit()`.
2. Non-blocking submission — thread pool starts work; caller continues.
3. Retrieval on demand — `get()` when you actually need the result.
4. Cancellation — `cancel(true)` to interrupt an in-progress task.
5. Status polling — `isDone()` for non-blocking check.

**FutureTask — the implementation:** The concrete class returned by most executors is `FutureTask<V>`, which implements both `Future<V>` and `Runnable`. The worker thread runs `FutureTask.run()`, which calls the wrapped `Callable.call()` internally, then stores the result in a `volatile` field. `get()` reads that field, blocking via `LockSupport.park()` if not yet set.

**The state machine:**
```
NEW → COMPLETING → NORMAL     (result set)
              → EXCEPTIONAL  (exception set)
NEW → CANCELLED
NEW → INTERRUPTING → INTERRUPTED
```

**Key limitation:** `Future` is purely pull-based. The caller decides when to retrieve the result by calling `get()`. There's no "push" — no way to say "when you're done, do this." This limitation motivated `CompletableFuture` (Java 8), which adds callback registration and chaining.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Future:

- Thread results required shared `volatile` fields or `CountDownLatch` for coordination.
- Error handling across threads required custom exception-passing mechanisms.
- No standardised cancellation API.

What breaks without it:
1. Concurrent task results coupled to shared mutable state → race conditions.
2. No clean way to propagate exceptions from worker threads to calling threads.

WITH Future:
→ Task result and exception both encapsulated in one typed object.
→ Cancellation standardised via `cancel(mayInterruptIfRunning)`.
→ Timeout support via `get(timeout, unit)`.

### 🧠 Mental Model / Analogy

> A Future is like a coat check receipt at a restaurant. You hand in your coat (submit your task), get a receipt (Future), enjoy dinner (do other work), then present the receipt when leaving to get your result (call get()). If the restaurant loses your coat (exception occurred), they tell you when you present the ticket. If you decide to leave early, you can ask them to discard the coat without returning it (cancel()).

"Coat check receipt" = Future, "enjoying dinner" = doing concurrent work, "presenting the receipt" = calling get(), "restaurant loses coat" = ExecutionException.

The limitation: you must go back to the coat check yourself — the restaurant can't bring your coat to the table mid-dinner (no callback mechanism).

### ⚙️ How It Works (Mechanism)

**Future Method Reference:**

```
isDone()         → boolean; non-blocking check
isCancelled()    → boolean; was cancel() called?
cancel(boolean)  → attempts cancellation:
                   true  = interrupt thread if running
                   false = only prevent if not started
get()            → blocks indefinitely until done
get(long, TimeUnit) → blocks at most timeout duration
                      throws TimeoutException if exceeded
```

**Internal state transitions (FutureTask):**
```
submit(callable) → state = NEW
                        ↓ worker starts
call() running   → state = NEW (still running)
                        ↓
call() returns   → state = COMPLETING
                        ↓ result stored
result available → state = NORMAL
                   → get() returns value

call() throws    → state = COMPLETING
                        ↓ exception stored
exception stored → state = EXCEPTIONAL
                   → get() throws ExecutionException

cancel() called  → state = CANCELLED (if not started)
                   → state = INTERRUPTING→INTERRUPTED (if running + mayInterrupt)
```

### 🔄 How It Connects (Mini-Map)

```
Callable / Runnable
        ↓ submitted to
ExecutorService.submit()
        ↓ returns
   Future<V> ← you are here
        ↓
future.get() (blocking pull)
        ↓ evolved to
CompletableFuture<V>
(non-blocking callbacks, chaining, composition)
```

### 💻 Code Example

Example 1 — Basic Future usage with timeout:

```java
ExecutorService pool = Executors.newCachedThreadPool();

Future<String> future = pool.submit(() -> {
    Thread.sleep(1000);     // simulate work
    return "Hello from async task";
});

// Do other work here...

try {
    // Block at most 2 seconds for result
    String result = future.get(2, TimeUnit.SECONDS);
    System.out.println(result);
} catch (TimeoutException e) {
    future.cancel(true);    // interrupt the task
    System.err.println("Task timed out, cancelled");
} catch (ExecutionException e) {
    // Re-throw cause for specific handling
    throw new RuntimeException(e.getCause());
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}

pool.shutdown();
```

Example 2 — Checking multiple futures without blocking:

```java
List<Future<Integer>> futures = new ArrayList<>();
for (int i = 0; i < 10; i++) {
    int taskId = i;
    futures.add(pool.submit(() -> compute(taskId)));
}

// Poll until all done (non-blocking check)
while (!futures.stream().allMatch(Future::isDone)) {
    Thread.sleep(50); // check every 50ms
}

// Collect results
for (Future<Integer> f : futures) {
    if (!f.isCancelled()) {
        System.out.println(f.get()); // won't block; all done
    }
}
```

Example 3 — Why CompletableFuture is preferred for callbacks:

```java
// BAD: Polling Future in a loop wastes CPU
while (!future.isDone()) {
    Thread.sleep(10); // busy-waiting
}
String result = future.get();

// GOOD: Use CompletableFuture for reactive callback
CompletableFuture<String> cf =
    CompletableFuture.supplyAsync(() -> "result", pool);
cf.thenAccept(result -> System.out.println("Got: " + result));
// No blocking, no polling — callback fires when done
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Future.get() is non-blocking | get() blocks the calling thread until the result is available or the task fails; always use get(timeout, unit) in production. |
| cancel(true) guarantees the task stops immediately | cancel(true) sends an interrupt signal; the task must check Thread.isInterrupted() or use interruptible blocking operations to actually stop. |
| isCancelled() and cancel() are the same state concept | isCancelled() returns true only if cancel() was called successfully before the task completed normally. A task that finished normally never returns isCancelled()=true. |
| Future can be re-submitted after cancellation | Once cancelled, a FutureTask cannot be restarted — create a new Callable submission instead. |
| Exceptions from Callable are lost if get() is not called | If get() is never called, the exception is stored internally in FutureTask but never surfaced — it silently disappears. |

### 🔥 Pitfalls in Production

**1. Unbounded get() Causing Thread Starvation**

```java
// BAD: Blocking a thread pool thread on another future
ExecutorService pool = Executors.newFixedThreadPool(4);

// Task A blocks on Task B's future:
pool.submit(() -> {
    Future<String> b = pool.submit(() -> "result");
    return b.get(); // DEADLOCK if pool is full!
    // Task A occupies a thread waiting for Task B
    // If all 4 threads are doing this → no thread available for B
});

// GOOD: Use CompletableFuture with async composition,
// or use a separate executor for dependent tasks
```

**2. Not Handling Exceptions from Future.get()**

```java
// BAD: Exception from async task silently lost
Future<String> f = executor.submit(() -> {
    throw new RuntimeException("database error");
});
f.get(); // throws ExecutionException but not caught!

// GOOD: Always catch ExecutionException
try {
    f.get();
} catch (ExecutionException e) {
    log.error("Task failed", e.getCause()); // unwrap cause
}
```

**3. Memory Leak — Holding References to Completed Futures**

```java
// BAD: Storing all futures in a list indefinitely
List<Future<?>> allFutures = new ArrayList<>();
while (running) {
    allFutures.add(pool.submit(task)); // grows unbounded!
}

// GOOD: Remove completed futures from tracking structures
allFutures.removeIf(Future::isDone);
```

### 🔗 Related Keywords

- `Callable` — the task that produces the value a Future wraps.
- `CompletableFuture` — the modern, callback-capable successor to Future.
- `ExecutorService` — the thread pool that creates and manages Futures.
- `FutureTask` — the concrete implementation of Future used internally.
- `Thread (Java)` — bare threads lack Future's result/exception encapsulation.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Handle to async computation: check, wait, │
│              │ cancel, or retrieve result on demand.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Submitting Callable tasks with result     │
│              │ retrieval needed later; cancellable tasks.│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need callbacks / chaining → use           │
│              │ CompletableFuture instead.                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Future: the claim ticket for async work; │
│              │ CompletableFuture: the concierge."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CompletableFuture → ForkJoinPool          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service submits 50 Callable tasks to a thread pool of 10 threads, collecting all 50 Futures into a list. After submitting, it iterates the list calling `future.get()` in order (0 to 49). Task 0 is a slow 30-second database query; tasks 1–49 each take 100ms. How long does the service wait before it has all results, and why is this a poor traversal strategy? What alternative approach reduces total waiting time?

**Q2.** `cancel(true)` sends an interrupt to the executing thread. A task is running `Thread.sleep(60000)` (a 60-second sleep). After `cancel(true)`, how quickly does the task actually stop, what exception does it receive to the thread, and what happens to the Future's state after the task receives the interrupt? Now contrast with a task that's running a tight CPU loop with no interruptible calls — does cancel(true) stop it?

