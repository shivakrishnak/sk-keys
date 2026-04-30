---
layout: default
title: "Runnable vs Callable"
parent: "Java Concurrency"
nav_order: 67
permalink: /java-concurrency/runnable-vs-callable/
---
# 067 — Runnable vs Callable

`#java` `#concurrency` `#threading` `#functional`

⚡ TL;DR — Runnable defines a task with no return value and no checked exception; Callable<T> defines a task that returns a result and can throw a checked exception — use Runnable for fire-and-forget, Callable when you need the result.

| #067 | Category: Java Concurrency | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Thread, Generics, Checked Exceptions | |
| **Used by:** | ExecutorService, Thread, Future, CompletableFuture | |

---

### 📘 Textbook Definition

**`Runnable`** is a functional interface (`void run()`) representing a task with no return value and no declared checked exception. **`Callable<V>`** is a functional interface (`V call() throws Exception`) representing a task that produces a result of type `V` and may throw a checked exception. Both can be submitted to an `ExecutorService`; Callable submissions return a `Future<V>` to retrieve the result.

---

### 🟢 Simple Definition (Easy)

- `Runnable`: "Go do this thing. I don't need a result back, and errors are your problem."
- `Callable<T>`: "Go do this thing. Come back with a result. If something goes wrong, tell me about it."

---

### 🔵 Simple Definition (Elaborated)

Both interfaces define tasks to run on a thread. `Runnable` is the original (since Java 1.0) — simple, no return, no checked exception. `Callable<T>` was added in Java 5 with the concurrency package — it enables tasks that produce a result (`T`) and can propagate checked exceptions back to the caller through the `Future<T>` that wraps the result. In practice: if you use `ExecutorService.submit(callable)`, you get a `Future<T>` you can call `.get()` on to retrieve the result or catch any exception the task threw.

---

### 🔩 First Principles Explanation

**Interface signatures:**

```
@FunctionalInterface
public interface Runnable {
    void run();  // no return, no checked exception
}

@FunctionalInterface
public interface Callable<V> {
    V call() throws Exception;  // returns V, declares checked Exception
}
```

**The gap Callable fills:**

```
Task type             Runnable            Callable<T>
─────────────────────────────────────────────────────
Return value?         No (void)           Yes (T)
Checked exception?    No                  Yes (throws Exception)
Used with Thread?     Yes                 No (Thread only takes Runnable)
Used with pool?       Yes (execute/submit) Yes (submit only)
Returns Future?       Future<?> (no value) Future<T> (has value)
```

**Why two interfaces instead of one:**

```
Runnable is from Java 1.0 — predates generics (Java 5)
Callable added in Java 5 to:
  1. Enable tasks that produce typed results
  2. Enable checked exception propagation
  3. Enable use with Future<T>

Changing Runnable would break backward compatibility
→ Callable was added as a companion, not a replacement
```

---

### ❓ Why Does This Exist — Why Before What

```
Without Callable:
  Runnable cannot return a value
  → Must use shared mutable state to pass results back
  → Thread-safety problems, extra synchronization required

  public class ResultHolder { volatile String result; } // messy!
  Runnable r = () -> holder.result = computeResult();   // race-prone

  Also: Runnable cannot throw checked exceptions
  → Must catch and wrap, often silently swallowing errors

With Callable<T>:
  pool.submit(callable) → returns Future<T>
  Future<T> future = pool.submit(() -> fetch("url"));
  String result = future.get(); // blocks until done, propagates exception
  → Clean separation: task produces value, caller retrieves it
```

---

### 🧠 Mental Model / Analogy

> `Runnable` is a **task note** left on someone's desk: "Do this. I don't need a reply." `Callable` is an **order ticket**: "Do this and bring me the result (and tell me if there's a problem)." Both are tasks — but only the order ticket comes back with something in hand.

---

### ⚙️ How It Works

```
Runnable path:
  new Thread(runnable).start()          → void, no result
  pool.execute(runnable)                → void, no result
  pool.submit(runnable)                 → Future<?> (value = null)

Callable path:
  Future<T> f = pool.submit(callable)   → Future<T>
  T result = f.get()                    → blocks, returns T or throws
  T result = f.get(1, TimeUnit.SECONDS) → blocks up to 1s, throws TimeoutException

Exception propagation:
  Callable throws Exception inside call()
  → wrapped in ExecutionException
  → f.get() throws ExecutionException
  → getCause() returns original exception
```

---

### 🔄 How It Connects

```
Task definition
  ├─ Runnable → Thread / pool.execute / pool.submit
  │                             └─ Future<?> (no meaningful value)
  │
  └─ Callable<T> → pool.submit → Future<T>
                                     ├─ .get()          blocking result
                                     ├─ .get(timeout)   bounded wait
                                     ├─ .isDone()       non-blocking check
                                     └─ .cancel()       cancel if not started
```

---

### 💻 Code Example

```java
// Runnable — fire and forget
ExecutorService pool = Executors.newFixedThreadPool(4);

Runnable logTask = () -> System.out.println("Logging from thread: "
    + Thread.currentThread().getName());

pool.execute(logTask);       // no return value
pool.submit(logTask);        // Future<?>, but value is null — rarely useful
```

```java
// Callable<T> — task with a result
ExecutorService pool = Executors.newFixedThreadPool(4);

Callable<Integer> computeTask = () -> {
    Thread.sleep(200); // simulate work
    return 42;
};

Future<Integer> future = pool.submit(computeTask);

// Do other work while task runs...
System.out.println("Submitted, working on something else...");

// Block and retrieve result
Integer result = future.get(); // blocks until done
System.out.println("Result: " + result); // 42
```

```java
// Callable with checked exception propagation
Callable<String> fetchTask = () -> {
    // throws IOException — allowed in Callable, NOT in Runnable
    return Files.readString(Path.of("/tmp/data.txt"));
};

Future<String> future = pool.submit(fetchTask);
try {
    String content = future.get();
} catch (ExecutionException e) {
    Throwable cause = e.getCause(); // the original IOException
    System.err.println("Task failed: " + cause.getMessage());
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

```java
// Converting Runnable to Callable (when you need both to go in a list)
List<Callable<Void>> tasks = List.of(
    Executors.callable(runnable1, null),   // wraps Runnable as Callable<Void>
    Executors.callable(runnable2, null)
);
List<Future<Void>> futures = pool.invokeAll(tasks);
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| You can pass Callable to `new Thread()` | Thread only accepts Runnable; Callable requires ExecutorService |
| `pool.submit(runnable)` returns null | Returns `Future<?>` — but `.get()` returns null (no value from Runnable) |
| Checked exceptions in Runnable lambdas are fine | Runnable.run() has no `throws` clause — checked exceptions must be caught inside |
| Callable is always better than Runnable | Runnable is simpler and perfectly fine when you don't need a result |
| `Callable` and `Supplier<T>` are the same | Supplier doesn't declare `throws Exception` — can't be used where checked exceptions are thrown |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Catching exceptions silently in Runnable**

```java
// Bad: exception silently swallowed — task "succeeds" from pool's perspective
Runnable r = () -> {
    try {
        riskyOperation();
    } catch (Exception e) {
        // nothing — exception disappears!
    }
};
pool.execute(r); // pool thinks task completed normally

// Fix: use Callable + Future.get() for proper error handling
Future<?> f = pool.submit(() -> riskyOperation()); // exception preserved
f.get(); // throws ExecutionException wrapping the original exception
```

**Pitfall 2: Forgetting `future.get()` — exceptions never observed**

```java
// Bad: task throws exception, future.get() never called → silent failure
Future<String> f = pool.submit(() -> { throw new RuntimeException("fail"); });
// exception sits in Future forever, never seen

// Fix: always retrieve the Future result or at least check for errors
try {
    f.get();
} catch (ExecutionException e) {
    log.error("Task failed", e.getCause());
}
```

---

### 🔗 Related Keywords

- **[Thread](./066 — Thread.md)** — Runnable is the native task for Thread
- **[ExecutorService](./074 — ExecutorService.md)** — executes both Runnable and Callable
- **[Future & CompletableFuture](./075 — Future and CompletableFuture.md)** — holds Callable results
- **Checked Exceptions** — only Callable can declare them in its contract
- **Functional Interfaces** — both Runnable and Callable are `@FunctionalInterface`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Runnable = fire-and-forget task;              │
│              │ Callable<T> = task with result + exception    │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Runnable: side effects only (logging, writes) │
│              │ Callable: need result or must handle errors   │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use Runnable when you need the result   │
│              │ — use Callable + Future.get() instead         │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Runnable doesn't talk back;                  │
│              │  Callable returns a result and can complain"  │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ExecutorService → Future → CompletableFuture  │
│              │ → Thread Lifecycle                            │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `Supplier<T>` in java.util.function also has a method `T get()` with no checked exceptions. How is it different from `Callable<T>`? In which contexts would you use one versus the other?

**Q2.** When you submit a `Runnable` to an ExecutorService, you get back a `Future<?>`. When would calling `.get()` on this Future be useful, even though it always returns null?

**Q3.** If a `Callable` throws a `RuntimeException` (not a checked exception), how does that propagate through `Future.get()`? Is it wrapped in `ExecutionException`?

