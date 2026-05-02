---
layout: default
title: "Executor"
parent: "Java Concurrency"
nav_order: 349
permalink: /java-concurrency/executor/
number: "0349"
category: Java Concurrency
difficulty: ★★☆
depends_on: Runnable, Thread (Java), Callable
used_by: ExecutorService, ThreadPoolExecutor, ForkJoinPool
related: ExecutorService, Runnable, ThreadPoolExecutor
tags:
  - java
  - concurrency
  - executor
  - intermediate
  - thread-pool
---

# 0349 — Executor

⚡ TL;DR — `Executor` is a one-method interface (`execute(Runnable)`) that decouples task submission from task execution — enabling tasks to run in thread pools, on the calling thread, or any other strategy without changing the task code.

| #0349 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Runnable, Thread (Java), Callable | |
| **Used by:** | ExecutorService, ThreadPoolExecutor, ForkJoinPool | |
| **Related:** | ExecutorService, Runnable, ThreadPoolExecutor | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Code that submits work to threads is coupled to the threading mechanism. `new Thread(task).start()` creates a new OS thread for every task — not reusable, no limits, no lifecycle management. Swapping from "new thread per task" to "thread pool" requires rewriting every submission site.

THE INVENTION MOMENT:
**`Executor`** separates "what to run" (`Runnable`) from "how to run it" — enabling the threading strategy to change without modifying task code.

### 📘 Textbook Definition

**`Executor`** is a functional interface in `java.util.concurrent` with one method: `void execute(Runnable command)`. It is the base interface for all executor-style task submission in Java. Implementations include: `ThreadPoolExecutor`, `ForkJoinPool`, inline/direct executor (`r -> r.run()`), and scheduled executors. `ExecutorService` extends `Executor` with lifecycle management (`shutdown`, `awaitTermination`) and `Callable`/`Future` support (`submit`).

### ⏱️ Understand It in 30 Seconds

**One line:**
`Executor` = a single method that says "please run this task" — without specifying how.

**One analogy:**
> A task inbox: you put a task in the inbox (Executor.execute()), and the system handles running it — whether that means assigning it to an intern immediately, adding it to a queue for later, or running it yourself. The task doesn't know who processes it.

**One insight:**
The `Executor` interface enables strategy pattern for execution. `execute(task)` always means "run this task" — whether synchronously, in a pool, delayed, or distributed. Changing the `Executor` implementation changes the execution strategy without touching task code.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. `execute(Runnable)` submits a task — it does not specify when or where it runs.
2. `Executor` makes no guarantees about execution order, timing, or thread.
3. Execution may be asynchronous (thread pool) or synchronous (direct executor).

DERIVED DESIGN:
```java
// Direct executor: runs in calling thread
Executor direct = Runnable::run;

// Thread-per-task: creates new thread each time
Executor newThreadEach = r -> new Thread(r).start();

// Thread pool: reuses threads (production standard)
Executor pool = Executors.newFixedThreadPool(10);

// All accept Runnable with identical syntax:
direct.execute(() -> doWork());
newThreadEach.execute(() -> doWork());
pool.execute(() -> doWork());
```

THE TRADE-OFFS:
Gain: Decouples task from execution; enables strategy pattern; the interface is minimal.
Cost: `execute(Runnable)` only — no result retrieval, no lifecycle. For richer functionality, use `ExecutorService`.

### 🧪 Thought Experiment

SETUP:
Toggle execution strategy for tests vs. production.

```java
// Production: thread pool
Executor pool = Executors.newFixedThreadPool(4);
service.processOrders(orders, pool);

// Test: synchronous execution
Executor sync = Runnable::run; // direct executor
service.processOrders(orders, sync); // runs in test thread
// No threads created in tests — deterministic, fast

void processOrders(List<Order> orders, Executor exec) {
    orders.forEach(o -> exec.execute(() -> process(o)));
    // Works with ANY Executor implementation
}
```

THE INSIGHT:
Injecting `Executor` as a dependency enables test-friendly synchronous execution alongside production thread pool execution — the code never changes, only the injected strategy.

### 🧠 Mental Model / Analogy

> `Executor` is like a "done for you" button with no specification of who does it. Your task is the button's label. The implementation decides whether a robot, intern, or you yourself does the job.

### 📶 Gradual Depth — Four Levels

**Level 1:** `Executor` is "give me work to do" — a single-method interface for submitting tasks.

**Level 2:** Use `Executors.newFixedThreadPool(n)` which implements a richer `ExecutorService`. Use bare `Executor` when no return value or lifecycle management is needed.

**Level 3:** `Executor` is the base abstraction. `ExecutorService` extends it with `submit()`, `shutdown()`, and `invokeAll()`. `AbstractExecutorService` provides default implementations. `ThreadPoolExecutor` is the canonical implementation.

**Level 4:** The `Executor` interface enables inversion of control for concurrent execution — a cornerstone of testable, configurable concurrent systems. Dependency injection of `Executor` (or `ExecutorService`) rather than using static `Executors.newX()` methods is a critical production practice.

### ⚙️ How It Works (Mechanism)

```java
// Executor examples:
// 1. Fixed thread pool (production standard)
Executor executor = Executors.newFixedThreadPool(Runtime
    .getRuntime().availableProcessors());

// 2. Direct/synchronous (testing)
Executor synchronous = command -> command.run();

// 3. Custom executor
Executor loggedExecutor = command -> {
    log.info("Executing: {}", command);
    command.run();
    log.info("Completed");
};

// Usage (identical regardless of implementation):
executor.execute(() -> processRequest(request));
```

**When to use `Executor` vs `ExecutorService`:**
```java
// Use Executor when:
// - Only need fire-and-forget (no results, no shutdown)
// - Maximum flexibility in tests

// Use ExecutorService when:
// - Need Future/Callable (results)
// - Need shutdown() for graceful termination
// - Need submitAll/invokeAny patterns
```

### 🔄 The Complete Picture — End-to-End Flow

```
[Service: executor.execute(() -> processOrder(id))]
    → [Executor impl: routes to thread pool task queue] ← YOU ARE HERE
    → [Pool thread picks up task]
    → [Runnable.run() executes: processOrder(id)]
    → [Thread returns to pool]
```

### 💻 Code Example

```java
// Injecting Executor for testability:
class OrderProcessor {
    private final Executor executor;

    OrderProcessor(Executor executor) {
        this.executor = executor;
    }

    void processAll(List<Order> orders) {
        orders.forEach(o ->
            executor.execute(() -> process(o))
        );
    }
}

// Production:
new OrderProcessor(Executors.newFixedThreadPool(4));

// Test:
new OrderProcessor(Runnable::run); // synchronous
```

### ⚖️ Comparison Table

| Interface | Submit Style | Returns Future | Lifecycle | Best For |
|---|---|---|---|---|
| **Executor** | execute(Runnable) | No | No | Minimal abstraction |
| ExecutorService | submit(Callable) | Yes | Yes | Production use |
| ScheduledExecutorService | schedule(Runnable/Callable) | Yes | Yes | Delayed/periodic tasks |

How to choose: Use `ExecutorService` in production (richer API). Use `Executor` for dependency injection of execution strategy (includes synchronous implementations for testing).

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `Executor.execute()` guarantees async execution | An `Executor` can run tasks synchronously (`command -> command.run()`). Async execution is implementation-dependent |
| `Executor` and `Thread` are interchangeable | `Thread` IS the execution unit. `Executor` is the submission abstraction. Thread pools reuse threads across many Executor.execute() calls |

### 🚨 Failure Modes & Diagnosis

**Task rejection in bounded executor:**
Symptom: `RejectedExecutionException` on `execute()`.

Fix: Configure `RejectedExecutionHandler` or use unbounded queue (with caution for memory).

### 🔗 Related Keywords

**Prerequisites:** `Runnable`, `Thread (Java)` 
**Builds on:** `ExecutorService`, `ThreadPoolExecutor`
**Alternatives:** `ExecutorService` (richer), direct `new Thread(r).start()` (simpler but unmanaged)

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single-method interface: execute(Runnable)│
│              │ — decouples task from execution mechanism │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Enables strategy pattern for execution;   │
│              │ synchronous impl for tests, pool for prod │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Here's work to do — you decide how"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ExecutorService → ThreadPoolExecutor      │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** A developer uses a direct `Executor` (`command -> command.run()`) in a Spring `@Async` bean. The `@Async` annotation is supposed to run methods asynchronously, but the direct executor runs them synchronously in the calling thread. Explain why this defeats the purpose of `@Async`, what the `.execute()` contract actually guarantees vs. what developers assume, and how Spring's `@Async` could detect and warn about the direct executor configuration.

