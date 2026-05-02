---
layout: default
title: "Callable"
parent: "Java Concurrency"
nav_order: 333
permalink: /java-concurrency/callable/
number: "333"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread (Java), Runnable, ExecutorService
used_by: Future, CompletableFuture, ExecutorService, ThreadPoolExecutor
tags:
  - java
  - concurrency
  - intermediate
---

# 333 — Callable

`#java` `#concurrency` `#intermediate`

⚡ TL;DR — A functional interface like Runnable but able to return a result and throw checked exceptions, used with ExecutorService to get Future results.

| #333 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), Runnable, ExecutorService | |
| **Used by:** | Future, CompletableFuture, ExecutorService, ThreadPoolExecutor | |

---

### 📘 Textbook Definition

`java.util.concurrent.Callable<V>` is a functional interface introduced in Java 5 representing a task that returns a result of type `V` and may throw a checked exception. Unlike `Runnable`, which has a `void run()` method, `Callable` declares `V call() throws Exception`. It is the standard mechanism for submitting value-returning tasks to an `ExecutorService`, which wraps the result in a `Future<V>` for asynchronous retrieval.

### 🟢 Simple Definition (Easy)

Callable is like Runnable — a task you want to run in another thread — but it can hand back an answer and report errors properly.

### 🔵 Simple Definition (Elaborated)

Before `Callable`, the only way to run code in a thread was `Runnable`, which returned nothing and couldn't throw checked exceptions. This forced workarounds: storing results in shared variables (thread-unsafe) or catching and swallowing checked exceptions. `Callable` solves both problems: its `call()` method has a return type and is declared to throw `Exception`. Submitting a `Callable` to an `ExecutorService` returns a `Future` that blocks until the result is available and re-throws any exception thrown by `call()` wrapped in an `ExecutionException`.

### 🔩 First Principles Explanation

**Problem with Runnable:**
```java
// Runnable: no return, checked exceptions must be caught
Runnable r = () -> {
    try {
        String result = fetchFromDB(); // throws IOException
        // Where does result go?? Can't return it!
    } catch (IOException e) {
        // Force to swallow or use a shared variable — messy
    }
};
```

**Solution — Callable:**
```java
Callable<String> c = () -> fetchFromDB(); // throws IOException naturally
// Submit to executor, get a Future
Future<String> future = executor.submit(c);
String result = future.get(); // retrieves result or re-throws exception
```

**The Callable interface definition:**

```java
@FunctionalInterface
public interface Callable<V> {
    V call() throws Exception;
}
```

**How ExecutorService wraps it:** When you call `executor.submit(callable)`, the executor creates a `FutureTask<V>` wrapping the callable. The `FutureTask` runs the callable's `call()` method in a thread pool thread, stores the result (or exception), and makes it available via `Future.get()`. The exception is wrapped in `ExecutionException` so the calling thread can handle it.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Callable:

- Value-returning async tasks required awkward shared state (AtomicReference or concurrent collections).
- Checked exceptions inside `Runnable` had to be caught and wrapped or silently swallowed.
- No standardised way to observe whether an async task succeeded or failed.

What breaks without it:
1. Error handling for async tasks is ad-hoc and error-prone.
2. Retrieving results from threads requires manual synchronisation.

WITH Callable:
→ Result and exception both travel cleanly through the Future API.
→ Exception from async code re-thrown in the calling thread at `future.get()`.
→ Composable with `ExecutorService.invokeAll()` for batch parallel tasks.

### 🧠 Mental Model / Analogy

> Runnable is like giving someone a task with "go do it, I don't need to hear back." Callable is like giving someone a task and getting a claim ticket in return. Later you can cash the ticket to get the result — and if they ran into a problem, the cashier tells you exactly what went wrong when you present the ticket.

"Claim ticket" = `Future<V>`, "cashing" = `future.get()`, "ran into a problem" = exception wrapped in `ExecutionException`.

The key upgrade over Runnable: you get confirmation of success or specific failure, not just silent completion.

### ⚙️ How It Works (Mechanism)

```
executor.submit(callable)
           ↓
Creates FutureTask<V> wrapping callable
           ↓
FutureTask submitted to thread pool queue
           ↓
Worker thread calls futureTask.run()
  → internally calls callable.call()
  → stores result V or caught exception
           ↓
Future<V> returned to caller immediately
           ↓
Caller calls future.get()
  → if done: returns result V
  → if exception: throws ExecutionException(cause)
  → if not done yet: blocks until complete
```

### 🔄 How It Connects (Mini-Map)

```
Runnable (no return, no checked exception)
           ↓ upgrade
Callable<V> ← you are here
           ↓ submitted to
ExecutorService.submit(callable)
           ↓ returns
Future<V>
           ↓ evolved to
CompletableFuture<V> (non-blocking composition)
```

### 💻 Code Example

Example 1 — Basic Callable with ExecutorService:

```java
ExecutorService executor =
    Executors.newFixedThreadPool(4);

Callable<Integer> sumTask = () -> {
    int sum = 0;
    for (int i = 1; i <= 1_000_000; i++) sum += i;
    return sum; // returns result to Future
};

Future<Integer> future = executor.submit(sumTask);

// Continue doing other work...

try {
    Integer result = future.get(); // blocks until done
    System.out.println("Sum: " + result);
} catch (ExecutionException e) {
    // exception from call() is wrapped here
    System.err.println("Task failed: " + e.getCause());
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}

executor.shutdown();
```

Example 2 — invokeAll for parallel tasks:

```java
List<Callable<String>> tasks = List.of(
    () -> fetchUserFromDB(1),
    () -> fetchUserFromDB(2),
    () -> fetchUserFromDB(3)
);

// All 3 run in parallel; invokeAll blocks until ALL complete
List<Future<String>> futures =
    executor.invokeAll(tasks);

for (Future<String> f : futures) {
    System.out.println(f.get()); // results in submission order
}
```

Example 3 — Callable vs Runnable exception handling comparison:

```java
// BAD: Runnable — must swallow checked exceptions
Runnable r = () -> {
    try {
        riskyMethod(); // checked IOException
    } catch (IOException e) {
        // forced catch — messy, easy to miss
        log.error("error", e);
    }
};

// GOOD: Callable — exception propagates naturally
Callable<Void> c = () -> {
    riskyMethod(); // IOException propagates to Future
    return null;
};
Future<Void> f = executor.submit(c);
try {
    f.get();
} catch (ExecutionException e) {
    if (e.getCause() instanceof IOException io) {
        // handle specifically
    }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Callable runs in the current thread when submitted | Callable runs in a thread pool worker thread; submit() returns immediately with a Future. |
| Exceptions from Callable are lost | They are stored in the FutureTask and re-thrown as ExecutionException when future.get() is called. |
| Callable<Void> is redundant — just use Runnable | Callable<Void> allows throwing checked exceptions, which Runnable doesn't. For throws-checked + no-return tasks, Callable<Void> returning null is the idiom. |
| invokeAll() returns futures only after all tasks complete | invokeAll() blocks until ALL submitted callables complete (or the timeout expires), then returns a list of done futures. |
| future.get() with no timeout is always safe | future.get() blocks indefinitely if the task never completes; always use future.get(timeout, unit) in production code. |

### 🔥 Pitfalls in Production

**1. Blocking All Threads with future.get() Without Timeout**

```java
// BAD: Infinite block if remote call in Callable hangs
Future<String> f = executor.submit(() -> httpClient.get(url));
String result = f.get(); // hangs forever if server unreachable

// GOOD: Always bound the wait
try {
    String result = f.get(5, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    f.cancel(true); // interrupt the task
    throw new ServiceUnavailableException();
}
```

**2. Swallowing ExecutionException and Losing Root Cause**

```java
// BAD: Root cause hidden
try {
    future.get();
} catch (ExecutionException e) {
    log.error("task failed"); // loses e.getCause()!
}

// GOOD: Always unwrap and handle the cause
catch (ExecutionException e) {
    Throwable cause = e.getCause();
    if (cause instanceof IOException io) { /* handle */ }
    else throw new RuntimeException("Unexpected", cause);
}
```

**3. Not Shutting Down ExecutorService**

```java
// BAD: Thread pool threads are non-daemon by default
// → JVM won't exit even after main() returns
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(task);
// main exits but JVM stays alive!

// GOOD: Always shut down
pool.shutdown();
pool.awaitTermination(30, TimeUnit.SECONDS);
```

### 🔗 Related Keywords

- `Runnable` — the simpler sibling: no return value, no checked exceptions.
- `Future` — the handle returned by ExecutorService.submit(Callable) for result retrieval.
- `CompletableFuture` — the modern evolution supporting non-blocking chaining.
- `ExecutorService` — the thread pool that accepts and executes Callables.
- `FutureTask` — the concrete wrapper the JVM creates around a Callable submission.
- `Thread (Java)` — lower-level alternative; Callable avoids manual thread management.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Like Runnable but returns V and throws    │
│              │ checked exceptions; used with Executor.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Async task that returns a value or may    │
│              │ throw a checked exception.                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Fire-and-forget tasks with no result →    │
│              │ use Runnable; non-blocking chains → use   │
│              │ CompletableFuture.                        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Callable is Runnable with a receipt."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Future → CompletableFuture → ForkJoinPool │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 100 Callable tasks submitted to a fixed thread pool of 10 threads. Each task makes an HTTP call that takes an average of 200ms but can occasionally take 10 seconds. You call `invokeAll()` with no timeout. Under what conditions can this lead to resource exhaustion, and how would you redesign the submission pattern to be safe?

**Q2.** `ExecutorService.invokeAny()` takes a list of Callables and returns the result of the first one to complete successfully. If 5 of the 10 submitted tasks throw exceptions and the remaining 5 succeed, what exactly happens to the exceptions from the failing tasks — are they silently discarded, logged, or surfaced somewhere — and what design implication does this have for error observability in parallel fan-out operations?

