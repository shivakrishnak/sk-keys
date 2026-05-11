---
layout: default
title: "Java Concurrency - Thread Basics"
parent: "Java Concurrency"
grand_parent: "Interview Mastery"
nav_order: 1
permalink: /interview/java-concurrency/thread-basics/
topic: Java Concurrency
subtopic: Thread Basics
keywords:
  - Thread and Runnable
  - Callable and Future
  - Executor Framework
  - ThreadPoolExecutor
  - ForkJoinPool
  - CompletableFuture
difficulty_range: mixed
status: complete
version: 1
---

# Thread and Runnable

**TL;DR** - Thread is the unit of execution in Java; Runnable is the task abstraction that separates "what to do" from "how to execute it," enabling the Executor framework and modern concurrency patterns.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Without threads, a program can only do one thing at a time. A web server handles one request at a time - all other clients wait. A GUI freezes during file download. A database query blocks all other operations.

**THE BREAKING POINT:**
A single-threaded web server can handle 1 request/second when each request takes 1 second. With 1000 concurrent users, the queue grows unboundedly. Response times exceed minutes.

**THE INVENTION MOMENT:**
"This is exactly why threads were created."

**EVOLUTION:**
Single-threaded programs -> Thread subclassing (Java 1.0) -> Runnable interface (separating task from thread) -> Executor framework (Java 5) -> Virtual threads (Java 21).

---

### Textbook Definition

A `Thread` is a lightweight process managed by the JVM, sharing heap memory with other threads but having its own stack. `Runnable` is a functional interface representing a task that can be executed by a thread. The separation of task (Runnable) from executor (Thread) is the foundation of Java's concurrency model.

---

### Understand It in 30 Seconds

**One line:**
Thread = the worker, Runnable = the job description. Separate them for flexible scheduling.

**One analogy:**

> Threads are employees. Runnable is a work order. You don't hire a new employee for every task - you give work orders to an existing team (thread pool).

**One insight:**
Never extend Thread to define work. Implement Runnable (or Callable) instead. Subclassing Thread conflates the worker with the work, making it impossible to submit the same task to different executors. This is the single most important beginner lesson in Java concurrency.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Each thread has its own stack (local variables are thread-safe by default)
2. All threads share the heap (objects require synchronization)
3. Thread scheduling is non-deterministic (never assume execution order)
4. Thread creation is expensive (1MB stack, OS kernel call)

**THE TRADE-OFFS:**
**Gain:** Concurrent execution, responsive applications, hardware utilization
**Cost:** Complexity (race conditions, deadlocks, visibility issues), resource overhead

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A thread lets your program do multiple things simultaneously - like a chef who can watch the oven while chopping vegetables.

**Level 2 - How to use it (junior developer):**

```java
// BAD: Extending Thread (don't do this)
class MyThread extends Thread {
    public void run() { /* work */ }
}
new MyThread().start();

// GOOD: Implement Runnable
Runnable task = () -> {
    System.out.println(
        Thread.currentThread().getName());
};
Thread t = new Thread(task, "worker-1");
t.start();
t.join(); // wait for completion
```

**Level 3 - How it works (mid-level engineer):**

Thread states: NEW -> RUNNABLE -> (BLOCKED | WAITING | TIMED_WAITING) -> TERMINATED

```
Thread.start() -> schedules with OS
  |
  v
run() executes on new OS thread
  |                     |
  v                     v
RUNNABLE             BLOCKED (waiting for lock)
  |                     |
  v                     v
TERMINATED           WAITING (wait/join/park)
```

Key methods:

- `start()` - begins execution (calls `run()` on new thread)
- `join()` - caller blocks until thread terminates
- `interrupt()` - sets interrupt flag, wakes from sleep/wait
- `Thread.sleep(ms)` - pauses current thread

**Level 4 - Mastery (senior/staff+ engineer):**

Direct Thread creation is a code smell in modern Java. Every `new Thread()` should be replaced with executor submission:

1. Thread pools bound concurrency, preventing resource exhaustion
2. Virtual threads (Java 21) eliminate the need for manual thread management entirely
3. Thread-per-task is only acceptable with virtual threads

The only legitimate uses of raw Thread in modern Java:

- Daemon threads for JVM-level services
- JVM shutdown hooks
- Framework/library implementation internals

---

### Code Example

**BAD - Thread per request (doesn't scale):**

```java
// Creates unbounded threads - crashes under load
ServerSocket server = new ServerSocket(8080);
while (true) {
    Socket client = server.accept();
    new Thread(() -> handle(client)).start();
    // 10K connections = 10K threads = OOM
}
```

**GOOD - Submit to executor:**

```java
ExecutorService pool = Executors
    .newFixedThreadPool(200);
ServerSocket server = new ServerSocket(8080);
while (true) {
    Socket client = server.accept();
    pool.submit(() -> handle(client));
    // Bounded at 200 threads, excess queued
}
```

---

### Quick Recall

**If you remember only 3 things:**

1. Implement Runnable (or Callable), never extend Thread
2. Thread creation is expensive - use executors/pools
3. Threads share heap, have private stacks - shared state needs synchronization

**Interview one-liner:**
"Thread is the execution unit, Runnable is the task abstraction. Separate them, submit tasks to executors, and in Java 21+ prefer virtual threads for I/O-bound work."

---

### The Surprising Truth

`Thread.start()` and `Thread.run()` are completely different. Calling `run()` directly executes the code on the current thread - no new thread is created. This is a common bug that compiles and runs without error but provides no concurrency. `start()` is what actually schedules execution on a new OS thread.

---

### Interview Deep-Dive

**Q1: What is the difference between extending Thread and implementing Runnable?**

_Why they ask:_ Tests understanding of OOP design and separation of concerns.

_Strong answer:_

Extending Thread conflates the task with the execution mechanism:

- You can't extend another class (Java is single-inheritance)
- You can't submit the task to different executors
- You can't reuse the same task in multiple threads
- You can't control the lifecycle separately

Implementing Runnable separates the task from execution:

- The task is just data (what to do)
- Any executor can run it (thread pool, virtual thread, ForkJoinPool)
- Same Runnable can be submitted multiple times
- Testable: just call `run()` directly in unit tests

Rule: Always implement Runnable or Callable. The only reason Thread is a class and not final is historical - pre-Java 5 there was no Executor framework.

---

**Q2: How do you properly stop a thread in Java?**

_Why they ask:_ Tests knowledge of thread interruption protocol.

_Strong answer:_

`Thread.stop()` is deprecated (can leave objects in inconsistent state). The correct approach is cooperative interruption:

```java
class Worker implements Runnable {
    public void run() {
        while (!Thread.currentThread()
                .isInterrupted()) {
            try {
                doWork();
                Thread.sleep(100);
            } catch (InterruptedException e) {
                // Restore interrupt flag
                Thread.currentThread().interrupt();
                break; // exit gracefully
            }
        }
        cleanup();
    }
}

// To stop:
workerThread.interrupt();
```

Key rules:

1. Check `isInterrupted()` in loops
2. Catch `InterruptedException` and restore the flag or exit
3. Never swallow `InterruptedException` silently
4. Blocking methods (sleep, wait, join, I/O) respond to interruption

---

**Q3: Explain thread states and transitions.**

_Why they ask:_ Tests understanding of thread lifecycle.

_Strong answer:_

| State         | Meaning                  | Transition from         |
| ------------- | ------------------------ | ----------------------- |
| NEW           | Created, not started     | Constructor             |
| RUNNABLE      | Running or ready to run  | start()                 |
| BLOCKED       | Waiting for monitor lock | Entering synchronized   |
| WAITING       | Waiting indefinitely     | wait(), join(), park()  |
| TIMED_WAITING | Waiting with timeout     | sleep(ms), wait(ms)     |
| TERMINATED    | Finished execution       | run() returned or threw |

Key transitions:

- `new Thread()` -> NEW
- `thread.start()` -> RUNNABLE
- Entering `synchronized` when lock is held -> BLOCKED
- `object.wait()` -> WAITING
- `Thread.sleep(1000)` -> TIMED_WAITING
- `run()` completes -> TERMINATED

A thread can go WAITING -> BLOCKED (notified but must still acquire the monitor before proceeding).

---

**Q4: What happens if an exception is thrown in a thread?**

_Why they ask:_ Tests understanding of error handling in concurrent code.

_Strong answer:_

If an uncaught exception escapes `run()`:

1. The thread terminates
2. The exception is passed to the thread's `UncaughtExceptionHandler`
3. If no handler is set, it prints to stderr and the thread dies silently
4. Other threads are NOT affected

```java
Thread t = new Thread(() -> {
    throw new RuntimeException("crash");
});
t.setUncaughtExceptionHandler((thread, ex) -> {
    log.error("Thread {} died: {}",
        thread.getName(), ex.getMessage());
    alertOps(ex);
});
t.start();
```

With ExecutorService, exceptions are captured in the Future:

```java
Future<?> f = executor.submit(() -> {
    throw new RuntimeException("crash");
});
try {
    f.get(); // throws ExecutionException
} catch (ExecutionException e) {
    Throwable cause = e.getCause();
}
```

---

**Q5: Why is `Thread.sleep(0)` sometimes used? What does it do?**

_Why they ask:_ Tests nuanced scheduler understanding.

_Strong answer:_

`Thread.sleep(0)` yields the current thread's time slice to the scheduler without actually sleeping. It acts as a scheduling hint: "I'm willing to give up my CPU time if other threads are waiting."

Uses:

1. Cooperative scheduling in CPU-bound loops
2. Giving other same-priority threads a chance to run
3. Triggering thread state transition

However, `Thread.yield()` is the proper API for this purpose. In practice, neither is reliable for correctness - they're hints. For real coordination, use `CountDownLatch`, `Semaphore`, or `CompletableFuture`.

---

---

# Callable and Future

**TL;DR** - Callable is like Runnable but can return a result and throw checked exceptions; Future is the handle to retrieve that result, enabling asynchronous computation with eventual result retrieval.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Runnable's `void run()` can't return values or throw checked exceptions. To get a result from another thread, you need shared mutable state (race conditions) and manual signaling (wait/notify). Error propagation requires custom mechanisms.

**THE BREAKING POINT:**
A service needs to call 5 external APIs concurrently and combine results. With Runnable, you need 5 shared variables, 5 exception holders, a CountDownLatch, and careful synchronization.

**THE INVENTION MOMENT:**
"This is exactly why Callable and Future were created."

**EVOLUTION:**
Runnable + shared state (Java 1.0) -> Callable + Future (Java 5) -> CompletableFuture (Java 8) -> Structured Concurrency (Java 21).

---

### Textbook Definition

`Callable<V>` is a functional interface with a single method `V call() throws Exception` - it produces a result and can throw checked exceptions. `Future<V>` represents the result of an asynchronous computation, providing methods to check completion, wait for the result, and cancel the task.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Callable is a task that produces an answer. Future is the receipt you get when submitting the task - you can check on it later or wait for the answer.

**Level 2 - How to use it (junior developer):**

```java
ExecutorService executor = Executors
    .newFixedThreadPool(4);

Future<String> future = executor.submit(() -> {
    Thread.sleep(1000);
    return "result";
});

// Do other work while task runs...
doOtherWork();

// Get result (blocks if not ready)
String result = future.get(5, TimeUnit.SECONDS);
```

**Level 3 - How it works (mid-level engineer):**

Future API:

- `get()` - blocks until result available
- `get(timeout, unit)` - blocks with timeout
- `isDone()` - true if completed (any way)
- `cancel(mayInterrupt)` - attempts cancellation
- `isCancelled()` - true if cancelled

```java
List<Future<Price>> futures = suppliers
    .stream()
    .map(s -> executor.submit(
        () -> s.getPrice(product)))
    .toList();

List<Price> prices = new ArrayList<>();
for (Future<Price> f : futures) {
    try {
        prices.add(f.get(2, SECONDS));
    } catch (TimeoutException e) {
        f.cancel(true);
    } catch (ExecutionException e) {
        log.warn("Supplier failed",
            e.getCause());
    }
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

Limitations of Future that led to CompletableFuture:

1. `get()` blocks - can't compose futures without blocking threads
2. No callback mechanism
3. No way to combine multiple futures
4. Exception handling is cumbersome

```java
// Future's blocking problem:
Future<A> fa = executor.submit(fetchA);
A a = fa.get(); // BLOCKS a thread!
Future<B> fb = executor.submit(
    () -> processA(a));
B b = fb.get(); // BLOCKS again!

// CompletableFuture solves this:
CompletableFuture.supplyAsync(this::fetchA)
    .thenApply(this::processA)
    .thenAccept(this::save);
```

---

### Code Example

**BAD - Blocking main thread waiting for results:**

```java
Future<User> userF = exec.submit(
    () -> getUser(id));
User user = userF.get(); // blocks here!
Future<Orders> ordersF = exec.submit(
    () -> getOrders(user)); // sequential!
```

**GOOD - True parallel execution:**

```java
Future<User> userF = exec.submit(
    () -> getUser(id));
Future<List<Order>> ordersF = exec.submit(
    () -> getOrders(id));
// Both run in parallel
User user = userF.get();
List<Order> orders = ordersF.get();
return new UserProfile(user, orders);
```

---

### Quick Recall

**If you remember only 3 things:**

1. Callable returns a value and throws exceptions; Runnable does neither
2. Future.get() blocks - submit all tasks first, then collect results
3. For composition/chaining, use CompletableFuture instead of raw Future

**Interview one-liner:**
"Callable adds return values and checked exceptions to Runnable, Future provides the async result handle, but for composition and non-blocking chains use CompletableFuture."

---

### Interview Deep-Dive

**Q1: What happens when you call Future.get() and the task threw an exception?**

_Why they ask:_ Tests error handling knowledge.

_Strong answer:_

`Future.get()` wraps any exception from the Callable in an `ExecutionException`. The original exception is available via `getCause()`:

```java
Future<String> f = exec.submit(() -> {
    throw new IOException("network error");
});

try {
    f.get();
} catch (ExecutionException e) {
    Throwable cause = e.getCause();
    // cause is IOException("network error")
    if (cause instanceof IOException io) {
        handleNetworkError(io);
    }
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
} catch (CancellationException e) {
    // Task was cancelled
}
```

Three possible exceptions from `get()`:

1. `ExecutionException` - task threw an exception
2. `InterruptedException` - waiting thread was interrupted
3. `CancellationException` - task was cancelled

---

**Q2: How does Future.cancel() work? Can you truly cancel a running task?**

_Why they ask:_ Tests understanding of cooperative cancellation.

_Strong answer:_

`cancel(boolean mayInterruptIfRunning)`:

- If task hasn't started: removed from queue, returns true
- If task is running and `mayInterruptIfRunning=true`: sends interrupt, returns true
- If task is running and `mayInterruptIfRunning=false`: returns false
- If task is already complete: returns false

The interrupt only works if the task checks `isInterrupted()` or is in a blocking call. A CPU-bound loop that ignores interruption cannot be cancelled.

```java
Future<?> f = exec.submit(() -> {
    while (!Thread.currentThread()
            .isInterrupted()) {
        computeChunk();
    }
});
f.cancel(true); // sends interrupt
```

After cancellation, `f.get()` throws `CancellationException` and `f.isCancelled()` returns true.

---

**Q3: When would you use invokeAll vs invokeAny?**

_Why they ask:_ Tests knowledge of bulk task submission.

_Strong answer:_

`invokeAll(tasks)`:

- Submits all tasks, blocks until ALL complete
- Returns List<Future> in same order as input
- Every future is guaranteed done (success or failure)
- Use case: Fan-out to N services, need all results

```java
List<Future<Price>> results = exec.invokeAll(
    suppliers.stream()
        .map(s -> (Callable<Price>)
            () -> s.getPrice(item))
        .toList(),
    5, SECONDS); // timeout for all
```

`invokeAny(tasks)`:

- Submits all tasks, returns FIRST successful result
- Cancels remaining tasks after first success
- Throws ExecutionException if ALL fail
- Use case: Redundant calls, fastest response wins

```java
String result = exec.invokeAny(List.of(
    () -> primaryService.call(),
    () -> backupService.call(),
    () -> fallbackService.call()));
// Returns whichever completes first
```

---

---

# Executor Framework

**TL;DR** - The Executor framework decouples task submission from task execution, providing thread pool management, task queuing, lifecycle control, and rejection policies through a unified API.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Creating threads manually for each task wastes resources, provides no bound on concurrency, gives no mechanism for graceful shutdown, and requires custom queuing logic for every application.

**THE BREAKING POINT:**
A service creates a new thread per incoming request. Under load spike (10K requests/second), the JVM attempts to create 10K OS threads, consuming 10GB of stack memory. The system OOMs and all requests fail.

**THE INVENTION MOMENT:**
"This is exactly why the Executor framework was created."

---

### Textbook Definition

The Executor framework (java.util.concurrent) separates task submission from execution policy. It provides: `Executor` (basic task submission), `ExecutorService` (lifecycle management + Future support), and `ScheduledExecutorService` (delayed/periodic execution). Factory methods in `Executors` create common configurations.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of creating threads yourself, you submit tasks to a managed pool of workers that handles scheduling, queuing, and cleanup for you.

**Level 2 - How to use it (junior developer):**

```java
ExecutorService pool = Executors
    .newFixedThreadPool(
        Runtime.getRuntime()
            .availableProcessors());

pool.submit(() -> processOrder(order));
Future<Report> f = pool.submit(
    () -> generateReport(data));

// Graceful shutdown
pool.shutdown();
pool.awaitTermination(30, SECONDS);
```

**Level 3 - How it works (mid-level engineer):**

Common pool configurations:

| Factory                             | Pool Size | Queue            | Use Case        |
| ----------------------------------- | --------- | ---------------- | --------------- |
| `newFixedThreadPool(n)`             | n fixed   | Unbounded        | General purpose |
| `newCachedThreadPool()`             | 0 to MAX  | SynchronousQueue | Short-lived     |
| `newSingleThreadExecutor()`         | 1         | Unbounded        | Sequential      |
| `newScheduledThreadPool(n)`         | n core    | DelayedWorkQueue | Periodic        |
| `newVirtualThreadPerTaskExecutor()` | Unbounded | None             | I/O (Java 21)   |

Shutdown protocol:

```java
pool.shutdown();
if (!pool.awaitTermination(30, SECONDS)) {
    pool.shutdownNow();
    pool.awaitTermination(5, SECONDS);
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Never use `newCachedThreadPool()` in production** - it can create unlimited threads under load. And `newFixedThreadPool()` has an unbounded queue that can cause OOM.

The production-grade approach: construct `ThreadPoolExecutor` directly:

```java
ThreadPoolExecutor pool =
    new ThreadPoolExecutor(
        10,              // corePoolSize
        50,              // maxPoolSize
        60, SECONDS,     // keepAlive
        new ArrayBlockingQueue<>(1000),
        new CustomThreadFactory("api-"),
        new CallerRunsPolicy());
```

This gives: bounded threads (50 max), bounded queue (1000), and a rejection policy (caller runs the task, providing backpressure).

---

### Code Example

**BAD - Unbounded cached thread pool:**

```java
ExecutorService pool = Executors
    .newCachedThreadPool();
for (Request r : requests) {
    pool.submit(() -> handle(r));
    // 100K requests = 100K threads = OOM
}
```

**GOOD - Bounded pool with rejection:**

```java
ExecutorService pool = new ThreadPoolExecutor(
    10, 50, 60, SECONDS,
    new ArrayBlockingQueue<>(1000),
    new ThreadPoolExecutor.CallerRunsPolicy());

for (Request r : requests) {
    pool.submit(() -> handle(r));
    // Max 50 threads + 1000 queued
    // Excess: caller thread handles it
}
```

---

### Quick Recall

**If you remember only 3 things:**

1. Never create raw threads in production - use ExecutorService
2. `newCachedThreadPool()` and unbounded queues can cause OOM under load
3. Use `ThreadPoolExecutor` directly with bounded queue and rejection policy

**Interview one-liner:**
"The Executor framework separates task submission from execution, providing bounded thread pools, work queues, lifecycle management, and rejection policies that prevent resource exhaustion under load."

---

### Interview Deep-Dive

**Q1: What are the four rejection policies and when would you use each?**

_Why they ask:_ Tests understanding of backpressure mechanisms.

_Strong answer:_

When both the thread pool and queue are full:

| Policy                  | Behavior                          | Use Case        |
| ----------------------- | --------------------------------- | --------------- |
| `AbortPolicy` (default) | Throws RejectedExecutionException | Fail fast       |
| `CallerRunsPolicy`      | Caller thread runs the task       | Backpressure    |
| `DiscardPolicy`         | Silently drops the task           | Fire-and-forget |
| `DiscardOldestPolicy`   | Drops oldest, retries             | Real-time       |

`CallerRunsPolicy` is often best: it slows down the submitter naturally (they can't submit more while executing), preventing overflow without losing tasks.

---

**Q2: How do you properly size a thread pool?**

_Why they ask:_ Tests performance engineering knowledge.

_Strong answer:_

**CPU-bound tasks:** `threads = number of CPU cores`

- More threads than cores causes context switching overhead

**I/O-bound tasks:** `threads = cores * (1 + wait_time / compute_time)`

- 90ms network + 10ms CPU on 8 cores = 8 \* 10 = 80 threads

**Mixed workloads:** Separate pools for CPU and I/O work

```java
int cpuPool = Runtime.getRuntime()
    .availableProcessors();
int ioPool = cpuPool * 10;

// Java 21: virtual threads for I/O
var ioExec = Executors
    .newVirtualThreadPerTaskExecutor();
```

In practice: start with cores\*2, measure under production load, monitor queue depth and task latency.

---

**Q3: Explain the shutdown sequence.**

_Why they ask:_ Tests lifecycle management understanding.

_Strong answer:_

```java
// Phase 1: Stop accepting new tasks
pool.shutdown();
// Queued tasks still run. Running continues.

// Phase 2: Wait for completion
boolean done = pool.awaitTermination(
    30, SECONDS);

// Phase 3: Force stop if needed
if (!done) {
    List<Runnable> queued =
        pool.shutdownNow();
    // Returns un-started tasks
    // Sends interrupt to running tasks
    pool.awaitTermination(5, SECONDS);
}
```

`shutdownNow()` returns un-started tasks and interrupts running ones. But interruption is cooperative - tasks must handle it.

For Spring apps: register in `@PreDestroy` or shutdown hook for graceful drain.

---

---

# ThreadPoolExecutor

**TL;DR** - ThreadPoolExecutor is the configurable engine behind all standard thread pools, with 7 parameters controlling core/max threads, queue type, keep-alive, thread factory, and rejection policy.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
`Executors.newFixedThreadPool()` uses unbounded queues (can OOM). `newCachedThreadPool()` creates unbounded threads (can OOM). Neither provides the precise control needed for production workloads.

**THE INVENTION MOMENT:**
"This is exactly why ThreadPoolExecutor was created with 7 tunable parameters."

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
ThreadPoolExecutor is the engine that powers all Java thread pools. You configure exactly how many workers, how long the queue, and what happens when overloaded.

**Level 2 - How to use it (junior developer):**

```java
ThreadPoolExecutor pool =
    new ThreadPoolExecutor(
        4,                         // core
        8,                         // max
        60, TimeUnit.SECONDS,      // keepAlive
        new ArrayBlockingQueue<>(100));

pool.submit(() -> processRequest(req));
```

**Level 3 - How it works (mid-level engineer):**

The 7-parameter constructor:

```java
ThreadPoolExecutor(
    int corePoolSize,     // always kept alive
    int maximumPoolSize,  // max under pressure
    long keepAliveTime,   // idle timeout for
    TimeUnit unit,        //   excess threads
    BlockingQueue<Runnable> workQueue,
    ThreadFactory threadFactory,
    RejectedExecutionHandler handler)
```

**Task submission flow:**

```
submit(task)
     |
     v
core threads < corePoolSize?
  YES -> create new core thread
  NO  -> queue full?
           NO  -> add to queue
           YES -> threads < maxPoolSize?
                    YES -> create new thread
                    NO  -> rejection policy
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Critical insight:** Tasks go to the queue BEFORE creating threads beyond core. With unbounded queue, max pool size is never reached:

```java
// TRAP: maxPoolSize is useless here!
new ThreadPoolExecutor(
    10, 100, 60, SECONDS,
    new LinkedBlockingQueue<>()); // unbounded!
// Queue never fills -> max(100) never used
// You effectively have a 10-thread pool
```

**Production configuration:**

```java
new ThreadPoolExecutor(
    10, 100, 60, SECONDS,
    new ArrayBlockingQueue<>(500), // bounded!
    new ThreadPoolExecutor.CallerRunsPolicy());
// Queue fills -> threads grow to 100
// Both full -> caller runs (backpressure)
```

Monitor with JMX:

- `pool.getActiveCount()` - running threads
- `pool.getQueue().size()` - queued tasks
- `pool.getCompletedTaskCount()` - total done
- `pool.getLargestPoolSize()` - peak threads

---

### Code Example

**Production-ready pool configuration:**

```java
@Bean
public ExecutorService orderProcessingPool() {
    ThreadPoolExecutor pool =
        new ThreadPoolExecutor(
            10,    // core threads
            50,    // max threads
            60, SECONDS,
            new ArrayBlockingQueue<>(2000),
            new ThreadFactoryBuilder()
                .setNameFormat("order-%d")
                .setDaemon(false)
                .build(),
            new CallerRunsPolicy());

    pool.prestartAllCoreThreads();
    return pool;
}
```

---

### Quick Recall

**If you remember only 3 things:**

1. Tasks go to queue before creating beyond-core threads - use bounded queue
2. 7 parameters: core, max, keepAlive, unit, queue, factory, handler
3. `CallerRunsPolicy` provides natural backpressure

**Interview one-liner:**
"ThreadPoolExecutor's 7 parameters give fine-grained control over concurrency bounds, with the critical insight that bounded queues are required for the max pool size to ever be reached."

---

### Interview Deep-Dive

**Q1: Draw the task flow through ThreadPoolExecutor.**

_Why they ask:_ Tests complete understanding of the execution model.

_Strong answer:_

```
Task arrives
  |
  v
Active threads < corePoolSize?
  |YES              |NO
  v                 v
Create thread    Queue has space?
Execute task       |YES       |NO
                   v           v
               Enqueue      Threads < max?
               task           |YES      |NO
                              v          v
                         Create new   Reject!
                         thread       (policy)
```

Key insight: Queue is checked BEFORE creating threads beyond core. This is counterintuitive.

- `SynchronousQueue` -> threads scale to max immediately
- `LinkedBlockingQueue` (unbounded) -> max never reached
- `ArrayBlockingQueue(N)` (bounded) -> max reached when queue fills

---

**Q2: How would you monitor a ThreadPoolExecutor in production?**

_Why they ask:_ Tests operational maturity.

_Strong answer:_

Expose metrics via Micrometer/Prometheus:

```java
Gauge.builder("pool.active",
    pool, ThreadPoolExecutor::getActiveCount)
    .register(registry);
Gauge.builder("pool.queue.size",
    pool, p -> p.getQueue().size())
    .register(registry);
Counter rejectedCounter = Counter.builder(
    "pool.rejected").register(registry);
```

Alert thresholds:

- `queue.size > 80% capacity` -> approaching saturation
- `active == max` for > 5 min -> pool exhaustion
- `rejected > 0` -> requests being dropped
- `completedTasks` rate dropping -> tasks slowing

Override `beforeExecute/afterExecute` to track task duration distribution.

---

**Q3: What happens with `allowCoreThreadTimeOut(true)`?**

_Why they ask:_ Tests nuanced understanding of pool lifecycle.

_Strong answer:_

By default, core threads live forever even when idle. Setting `allowCoreThreadTimeOut(true)` allows core threads to be terminated after `keepAliveTime` of inactivity.

Use case: Bursty workloads where you want the pool to scale to zero between bursts (e.g., batch processing that runs every hour).

```java
ThreadPoolExecutor pool =
    new ThreadPoolExecutor(
        10, 50, 30, SECONDS,
        new ArrayBlockingQueue<>(100));
pool.allowCoreThreadTimeOut(true);
// After 30s of no tasks, even core threads
// are terminated. Pool can shrink to 0.
```

Without this, 10 core threads remain alive permanently, consuming 10MB of stack memory even when the pool is completely idle.

---

---

# ForkJoinPool

**TL;DR** - ForkJoinPool is a work-stealing thread pool optimized for recursive divide-and-conquer tasks, powering parallel streams and CompletableFuture's async operations.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Divide-and-conquer algorithms create many subtasks of varying duration. A fixed thread pool wastes threads waiting for slow subtasks while fast ones complete. Load imbalance reduces parallelism.

**THE INVENTION MOMENT:**
"This is exactly why work-stealing was created."

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
ForkJoinPool is a special thread pool where idle threads "steal" work from busy threads' queues, keeping all CPUs utilized even when tasks are uneven.

**Level 2 - How to use it (junior developer):**

```java
ForkJoinPool common = ForkJoinPool.commonPool();

// Used implicitly by parallel streams
list.parallelStream()
    .filter(x -> x > 0)
    .mapToInt(Integer::intValue)
    .sum();

// Custom pool for isolation
ForkJoinPool custom = new ForkJoinPool(8);
custom.submit(() ->
    list.parallelStream()
        .forEach(this::process))
    .get();
```

**Level 3 - How it works (mid-level engineer):**

Work-stealing algorithm:

1. Each thread has a double-ended queue (deque)
2. When a thread forks subtasks, they go into its own deque
3. The thread takes work from the bottom (LIFO)
4. Idle threads steal from the top of others' deques (FIFO)

```
Thread A deque:    Thread B deque:
[task4] bottom     [task7] bottom
[task3]            (empty - steals from A)
[task2]                |
[task1] top    <-------+ steals task1
```

LIFO for own work = cache-friendly (hot)
FIFO for stealing = large tasks (bigger chunks)

**Level 4 - Mastery (senior/staff+ engineer):**

**The common pool trap:**
`ForkJoinPool.commonPool()` is shared by parallel streams, CompletableFuture, and any code without a specified pool. If one parallel stream has a slow I/O task, it blocks a common pool thread, reducing parallelism for ALL operations JVM-wide.

```java
// DANGER: I/O in parallel stream
list.parallelStream()
    .map(id -> httpClient.get(id)) // blocks!
    .toList();
// Starves other parallel operations

// FIX: Dedicated pool for I/O
ForkJoinPool ioPool = new ForkJoinPool(50);
List<Response> results = ioPool.submit(() ->
    list.parallelStream()
        .map(id -> httpClient.get(id))
        .toList()
).get();
```

Or better: use virtual threads for I/O, ForkJoinPool for CPU-only.

---

### Quick Recall

**If you remember only 3 things:**

1. Work-stealing: idle threads steal from busy threads' queues
2. `commonPool()` is shared - never block it with I/O
3. ForkJoinPool for CPU-bound work; virtual threads for I/O

**Interview one-liner:**
"ForkJoinPool uses work-stealing to keep all threads busy during recursive divide-and-conquer, but its shared common pool must never be blocked by I/O operations."

---

### The Surprising Truth

When you call `join()` on a `ForkJoinTask`, the joining thread doesn't just sit idle waiting. It actually steals and executes other tasks from the pool while waiting for its subtask to complete. This "helping" behavior is why ForkJoinPool can use the same number of threads as CPU cores without deadlocking on recursive task dependencies.

---

### Interview Deep-Dive

**Q1: Why shouldn't you do I/O in a parallel stream?**

_Why they ask:_ Tests understanding of common pool sharing.

_Strong answer:_

Parallel streams use `ForkJoinPool.commonPool()` which has only `availableProcessors() - 1` threads. If tasks block on I/O:

- 8-core machine = 7 common pool threads
- 7 I/O tasks blocking = all threads blocked
- Every other parallel stream, CompletableFuture.supplyAsync(), etc. starves

Solution: Dedicated ForkJoinPool, virtual threads, or CompletableFuture with custom executor.

---

**Q2: How does fork/join differ from submit on a regular executor?**

_Why they ask:_ Tests understanding of recursive parallelism.

_Strong answer:_

`fork()` pushes a subtask onto the current thread's work queue (no thread creation, no global queue). `join()` either retrieves the result or helps compute it (the joining thread steals and executes).

```java
class SumTask extends RecursiveTask<Long> {
    protected Long compute() {
        if (array.length <= THRESHOLD)
            return sequentialSum();
        int mid = array.length / 2;
        SumTask left = new SumTask(
            array, 0, mid);
        SumTask right = new SumTask(
            array, mid, array.length);
        left.fork();  // push to local deque
        Long r = right.compute(); // this thread
        Long l = left.join();     // get or help
        return l + r;
    }
}
```

Key differences from `submit()`:

- `fork()` is local (deque), not global (shared queue)
- `join()` can execute the task itself (work-stealing)
- Far less overhead for recursive decomposition

---

**Q3: How do you size a ForkJoinPool?**

_Why they ask:_ Tests understanding of parallelism tuning.

_Strong answer:_

Default `commonPool()` size: `Runtime.getRuntime().availableProcessors() - 1`

For CPU-bound recursive work: use default (matches cores).

For mixed workloads:

```java
// Set parallelism higher for I/O-bound work
ForkJoinPool pool = new ForkJoinPool(
    50,  // parallelism (active threads)
    ForkJoinPool.defaultForkJoinWorkerThreadFactory,
    null,  // exception handler
    true); // asyncMode for event-style tasks
```

`asyncMode=true` changes deque processing from LIFO to FIFO - better for non-recursive event processing tasks (each task triggers at most one other task rather than recursively splitting).

System property to configure common pool:
`-Djava.util.concurrent.ForkJoinPool.common.parallelism=16`

---

**Q4: What is the ManagedBlocker pattern?**

_Why they ask:_ Tests advanced ForkJoinPool knowledge.

_Strong answer:_

`ManagedBlocker` lets ForkJoinPool compensate for blocked threads. When a task must block (e.g., waiting for I/O), the pool creates a temporary extra thread to maintain parallelism:

```java
ForkJoinPool.managedBlock(
    new ForkJoinPool.ManagedBlocker() {
        public boolean block() {
            result = blockingCall();
            return true; // done
        }
        public boolean isReleasable() {
            return result != null;
        }
    });
// Pool may spawn extra thread to compensate
```

This prevents the pool from stalling when tasks unexpectedly block. It's how the pool maintains throughput despite blocking operations. Used internally by `Phaser` and `CompletableFuture`.

---

---

# CompletableFuture

**TL;DR** - CompletableFuture enables non-blocking asynchronous programming with composable pipelines, combining multiple async operations without callback hell or blocking threads.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
`Future.get()` blocks the calling thread. To compose async operations (A then B then C), you need to block between each step, wasting threads. Combining results from multiple futures requires complex coordination.

**THE BREAKING POINT:**
A service calls 3 APIs sequentially (800ms each) because Future composition requires blocking. Total: 2.4 seconds. Parallel execution would take 800ms, but coordinating Futures without blocking requires 50 lines of callback spaghetti.

**THE INVENTION MOMENT:**
"This is exactly why CompletableFuture was created."

---

### Textbook Definition

`CompletableFuture<T>` is a Future that can be explicitly completed, combined with other futures, and chained with non-blocking transformations. It provides 50+ methods for composing async operations including `thenApply`, `thenCompose`, `thenCombine`, `allOf`, `anyOf`, and exception handling.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
CompletableFuture lets you say "when A finishes, do B, then C" without waiting at each step. Like setting up dominoes.

**Level 2 - How to use it (junior developer):**

```java
CompletableFuture
    .supplyAsync(() -> fetchUser(id))
    .thenApply(user -> enrichProfile(user))
    .thenAccept(profile -> cache.put(
        id, profile));

// Combine two independent results
var userCF = supplyAsync(() -> getUser(id));
var ordersCF = supplyAsync(
    () -> getOrders(id));

var profileCF = userCF.thenCombine(ordersCF,
    (user, orders) ->
        new UserProfile(user, orders));
```

**Level 3 - How it works (mid-level engineer):**

**Method naming conventions:**

| Suffix   | Meaning                   |
| -------- | ------------------------- |
| `Async`  | Runs on different thread  |
| (none)   | Runs on completing thread |
| `Both`   | Combines two futures      |
| `Either` | First to complete wins    |

**Core operations:**

```java
// Transform: T -> U (map)
cf.thenApply(t -> transform(t))

// Chain async: T -> CF<U> (flatMap)
cf.thenCompose(t -> asyncLookup(t))

// Combine two: (T, U) -> V
cf1.thenCombine(cf2, (t, u) -> merge(t, u))

// Wait for all
CompletableFuture.allOf(cf1, cf2, cf3)
    .thenRun(() -> allDone());

// First to complete
CompletableFuture.anyOf(cf1, cf2, cf3)
    .thenAccept(first -> use(first));
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Error handling patterns:**

```java
CompletableFuture.supplyAsync(() -> riskyCall())
    .thenApply(this::process)
    .exceptionally(ex -> {
        log.error("Failed", ex);
        return fallbackValue;
    });

// handle() for both paths
cf.handle((result, ex) -> {
    if (ex != null) return defaultValue;
    return transform(result);
});

// Timeout (Java 9+)
cf.orTimeout(5, SECONDS)
  .exceptionally(ex -> handleTimeout());

// Fallback on timeout
cf.completeOnTimeout(defaultValue, 5, SECONDS);
```

**Executor control:**

```java
// Default: ForkJoinPool.commonPool()
supplyAsync(() -> task());

// Custom executor (production must-do for I/O)
supplyAsync(() -> task(), ioExecutor);
```

---

### Code Example

**BAD - Sequential blocking:**

```java
Future<User> uf = exec.submit(
    () -> getUser(id));
User user = uf.get(); // blocks!
Future<List<Order>> of = exec.submit(
    () -> getOrders(user.id()));
List<Order> orders = of.get(); // blocks!
// Total: sum of all latencies
```

**GOOD - Parallel with CompletableFuture:**

```java
var userCF = supplyAsync(
    () -> getUser(id), ioPool);
var ordersCF = supplyAsync(
    () -> getOrders(id), ioPool);
var recsCF = supplyAsync(
    () -> getRecs(id), ioPool);

return userCF.thenCombine(ordersCF,
    (user, orders) ->
        new Partial(user, orders))
    .thenCombine(recsCF,
        (partial, recs) ->
            new FullProfile(
                partial.user(),
                partial.orders(),
                recs))
    .orTimeout(3, SECONDS)
    .join();
// Total: max of all latencies (parallel)
```

---

### Quick Recall

**If you remember only 3 things:**

1. `thenApply` = map, `thenCompose` = flatMap (chain async)
2. Always specify a custom executor for I/O operations
3. `allOf` for fan-out, `anyOf` for race, `orTimeout` for deadline

**Interview one-liner:**
"CompletableFuture enables non-blocking async composition with thenApply/thenCompose for chaining, thenCombine/allOf for fan-out, and exceptionally/handle for error recovery, all without blocking threads."

---

### The Surprising Truth

`CompletableFuture.supplyAsync(() -> task())` without an executor runs on `ForkJoinPool.commonPool()`. Since this pool has only CPU-core threads, a single slow I/O operation in any chain can starve ALL other async operations in the entire JVM - including parallel streams. Always pass a dedicated executor for I/O work.

---

### Interview Deep-Dive

**Q1: What is the difference between thenApply and thenCompose?**

_Why they ask:_ Tests understanding of monadic composition.

_Strong answer:_

`thenApply` is `map`: transforms the result synchronously.

```java
// T -> U, result is CF<U>
CF<String> name = userCF.thenApply(
    user -> user.getName());
```

`thenCompose` is `flatMap`: chains another async operation.

```java
// T -> CF<U>, result is CF<U> (not CF<CF<U>>)
CF<Profile> profile = userCF.thenCompose(
    user -> asyncFetchProfile(user.id()));
```

Using `thenApply` with an async function gives nested `CF<CF<U>>`. `thenCompose` flattens it.

Identical to `map` vs `flatMap` in Stream, Optional, and Mono.

---

**Q2: How do you handle errors in a CompletableFuture chain?**

_Why they ask:_ Tests production error handling.

_Strong answer:_

Three approaches:

```java
// 1. exceptionally: recover with default
cf.thenApply(this::process)
  .exceptionally(ex -> {
      log.warn("Fallback", ex);
      return defaultValue;
  });

// 2. handle: branch on success/failure
cf.handle((result, ex) -> {
    if (ex != null) return fallback;
    return transform(result);
});

// 3. whenComplete: observe only
cf.whenComplete((result, ex) -> {
    if (ex != null) log.error("Failed", ex);
});
// Original result passes through
```

Exceptions propagate downstream. All `thenApply` calls skip until `exceptionally` or `handle` catches.

---

**Q3: Design a pattern for parallel service calls with timeout and partial results.**

_Why they ask:_ Tests real-world async architecture.

_Strong answer:_

```java
public UserDashboard getDashboard(String id) {
    var userCF = supplyAsync(
        () -> userService.get(id), ioPool)
        .orTimeout(2, SECONDS)
        .exceptionally(ex -> User.ANONYMOUS);

    var ordersCF = supplyAsync(
        () -> orderService.list(id), ioPool)
        .orTimeout(2, SECONDS)
        .exceptionally(ex -> List.of());

    var recsCF = supplyAsync(
        () -> recService.get(id), ioPool)
        .orTimeout(2, SECONDS)
        .exceptionally(ex -> Recs.EMPTY);

    return userCF.thenCombine(ordersCF,
            (u, o) -> new Partial(u, o))
        .thenCombine(recsCF,
            (p, r) -> new UserDashboard(
                p.user(), p.orders(), r))
        .join();
}
```

Pattern:

1. Each call has individual timeout + fallback
2. Graceful degradation with partial results
3. Custom ioPool prevents common pool starvation
4. Single blocking point at the end
5. Total latency = max(individual), not sum

---

**Q4: What is the difference between `join()` and `get()` on CompletableFuture?**

_Why they ask:_ Tests API knowledge and exception handling.

_Strong answer:_

Both block until completion. Differences:

| Method   | Checked Exception           | Wrapping            |
| -------- | --------------------------- | ------------------- |
| `get()`  | Throws InterruptedException | ExecutionException  |
| `join()` | No checked exceptions       | CompletionException |

`join()` is preferred in lambda contexts because you don't need try-catch:

```java
// get() requires try-catch (annoying in lambda)
stream.map(cf -> {
    try { return cf.get(); }
    catch (Exception e) { throw new RE(e); }
});

// join() is clean in lambdas
stream.map(CompletableFuture::join);
```

Use `get(timeout, unit)` when you need a timeout at the blocking point. Use `join()` everywhere else.

---

**Q5: When should you use CompletableFuture vs virtual threads (Java 21)?**

_Why they ask:_ Tests modern Java knowledge.

_Strong answer:_

**CompletableFuture:** Best for complex async pipelines where you need to compose, combine, race, or handle errors in a declarative chain. The pipeline structure itself is the value.

**Virtual threads:** Best for straightforward sequential I/O code that just needs to not block platform threads. Write synchronous-looking code and let the runtime handle it.

```java
// CF: Complex composition needed
supplyAsync(() -> getUser(id))
    .thenCompose(u -> getOrders(u.id()))
    .thenCombine(getRecs(id),
        (orders, recs) -> merge(orders, recs))
    .orTimeout(3, SECONDS);

// Virtual threads: Simple sequential I/O
try (var scope = new StructuredTaskScope
        .ShutdownOnFailure()) {
    var user = scope.fork(() -> getUser(id));
    var orders = scope.fork(
        () -> getOrders(id));
    scope.join().throwIfFailed();
    return new Profile(
        user.get(), orders.get());
}
```

Rule: If you're just doing parallel I/O calls and collecting results, virtual threads + structured concurrency is simpler. If you need timeout per call, fallback values, pipeline composition, or fan-out/fan-in patterns, CompletableFuture is more expressive.
