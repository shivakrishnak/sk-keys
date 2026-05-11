---
layout: default
title: "Java - Java 21 and Beyond"
parent: "Java"
grand_parent: "Interview Mastery"
nav_order: 6
permalink: /interview/java/java-21-and-beyond/
topic: Java
subtopic: Java 21 and Beyond
keywords:
  - Virtual Threads
  - Scoped Values
  - Structured Concurrency
  - String Templates
difficulty_range: mixed
status: in-progress
version: 2
---

# Virtual Threads

**TL;DR** - Virtual threads are lightweight threads managed by the JVM that make blocking I/O scalable by allowing millions of threads without the memory and context-switching overhead of OS threads.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Each Java thread maps 1:1 to an OS thread. An OS thread uses 512KB-1MB of stack memory and requires an expensive kernel context switch. A server handling 10,000 concurrent connections needs 10,000 threads, consuming 5-10GB of memory just for stacks. Beyond 10K threads, the OS spends more time context-switching than doing useful work.

**THE BREAKING POINT:**
A microservice receives 50K concurrent requests during peak traffic. The thread pool has 200 threads. 49,800 requests queue, causing timeouts. Increasing the thread pool to 50K OS threads requires 25GB of RAM and makes the server unresponsive from context switching.

**THE INVENTION MOMENT:**
"This is exactly why virtual threads were created."

**EVOLUTION:**
OS threads (Java 1.0) -> thread pools and NIO for scalability (Java 1.4) -> CompletableFuture for async composition (Java 8) -> reactive frameworks (RxJava, WebFlux) -> virtual threads (Java 19 preview, Java 21 final). Virtual threads achieve the scalability of reactive without the complexity.

---

### Textbook Definition

Virtual threads (Project Loom) are lightweight threads managed by the JVM rather than the OS. They are mounted on carrier threads (a small pool of OS threads) and automatically unmount when they block on I/O, freeing the carrier for other virtual threads. This enables millions of concurrent threads with a simple blocking programming model.

---

### Understand It in 30 Seconds

**One line:**
Virtual threads let you write simple blocking code that scales to millions of concurrent tasks.

**One analogy:**

> OS threads are like hiring a full-time employee for each customer - expensive and doesn't scale. Virtual threads are like a small team of employees serving a restaurant full of customers - when one customer is waiting for food (I/O), the employee serves another table.

**One insight:**
Virtual threads don't make code faster - they make code more scalable. A single request takes the same time. But instead of blocking an expensive OS thread during I/O waits, the virtual thread unmounts and the carrier thread serves other virtual threads. You get reactive scalability with blocking-style simplicity.

---

### First Principles Explanation

**CORE INVARIANTS:**

1. Virtual threads are cheap to create (KB, not MB) and schedule (JVM, not kernel)
2. Blocking I/O operations automatically unmount the virtual thread from its carrier
3. Virtual threads should not be pooled - create a new one per task
4. `synchronized` blocks pin virtual threads to their carrier (use ReentrantLock instead)

**DERIVED DESIGN:**
The JVM's scheduler multiplexes virtual threads onto a small pool of carrier threads (default: CPU cores). When a virtual thread calls a blocking operation (`socket.read()`, `Thread.sleep()`, `Lock.lock()`), the JVM parks it and mounts another virtual thread on the same carrier.

**THE TRADE-OFFS:**
**Gain:** Millions of concurrent threads, simple blocking code, no reactive complexity
**Cost:** Cannot use `synchronized` for long-held locks (pinning), thread-locals become expensive at scale, CPU-bound work doesn't benefit

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Handling many concurrent I/O operations requires some form of multiplexing.
**Accidental:** Reactive programming's callback chains, Mono/Flux wrappers, and backpressure APIs are accidental complexity that virtual threads eliminate.

---

### Mental Model / Analogy

> Virtual threads are like green threads with a smart scheduler. Imagine a restaurant with 4 chefs (carrier threads) and 10,000 orders (virtual threads). Each chef works on an order until it needs to wait (oven timer = I/O). While waiting, the chef picks up another order. When the timer rings, any available chef continues the original order.

- "Chef" -> carrier thread (OS thread)
- "Order" -> virtual thread
- "Waiting for oven" -> blocking I/O (unmount)
- "Timer rings" -> I/O completes (remount)
- "Restaurant manager" -> JVM scheduler

Where this analogy breaks down: In a real restaurant, a chef can't pause mid-knife-cut. Virtual threads can be preempted at any blocking point.

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Virtual threads are super-lightweight threads that Java manages internally. You can create millions of them without running out of memory, making it easy to handle many tasks at once.

**Level 2 - How to use it (junior developer):**

```java
// Create a virtual thread
Thread.ofVirtual().start(() -> {
    String data = fetchFromApi(); // blocking OK
    process(data);
});

// With executor (preferred for servers)
try (var executor = Executors
        .newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> {
            // Each task gets its own virtual thread
            return httpClient.send(request);
        });
    }
} // executor.close() waits for all tasks

// Spring Boot 3.2+: just set property
// spring.threads.virtual.enabled=true
```

**Level 3 - How it works (mid-level engineer):**

Virtual threads run on a ForkJoinPool of carrier threads (default size = CPU cores). When a virtual thread encounters a blocking operation:

1. The JVM detects the blocking call
2. The virtual thread's stack (continuation) is saved to heap
3. The carrier thread is freed for other virtual threads
4. When I/O completes, the virtual thread is rescheduled on any available carrier

Key API:

- `Thread.ofVirtual()` - creates virtual thread builder
- `Thread.startVirtualThread(Runnable)` - convenience method
- `Executors.newVirtualThreadPerTaskExecutor()` - executor that creates a new virtual thread per task
- `Thread.isVirtual()` - check if current thread is virtual

**Level 4 - Mastery (senior/staff+ engineer):**

**Pinning:** `synchronized` blocks pin virtual threads to their carrier because the JVM cannot safely move a thread that holds an OS-level monitor. Use `ReentrantLock` instead:

```java
// BAD: pins virtual thread to carrier
synchronized (lock) {
    database.query(sql); // carrier blocked!
}

// GOOD: ReentrantLock doesn't pin
lock.lock();
try {
    database.query(sql); // carrier freed
} finally {
    lock.unlock();
}
```

**Thread-locals:** Each virtual thread gets its own ThreadLocal storage. With millions of virtual threads, thread-local memory adds up. Use scoped values (see below) instead.

**CPU-bound work:** Virtual threads provide no benefit for CPU-bound tasks - you still have only N CPU cores. Use parallel streams or ForkJoinPool for CPU-bound work, virtual threads for I/O-bound work.

Detect pinning with: `-Djdk.tracePinnedThreads=full`


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

```
  Virtual Thread 1    Carrier Thread A
  [running]      -->  [mounted on A]
       |
  socket.read()       [blocking I/O detected]
       |
  [unmount VT1]  -->  [A is free]
  [save stack to heap]
       |
  Virtual Thread 2    Carrier Thread A
  [waiting]      -->  [mount VT2 on A]
       |
  I/O completes for VT1
       |
  Virtual Thread 1    Carrier Thread B
  [rescheduled]  -->  [mount VT1 on B]
  [restore stack from heap]
       |
  [continue after socket.read()]
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - OS thread per connection (doesn't scale):**

```java
// 10K connections = 10K OS threads = 10GB RAM
try (var executor = Executors
        .newFixedThreadPool(10_000)) {
    for (var conn : connections) {
        executor.submit(() -> handle(conn));
    }
}
```

**GOOD - Virtual thread per connection:**

```java
// 10K connections = 10K virtual threads = ~20MB
try (var executor = Executors
        .newVirtualThreadPerTaskExecutor()) {
    for (var conn : connections) {
        executor.submit(() -> handle(conn));
    }
}
// Same blocking code, 500x less memory
```

**GOOD - Fan-out pattern:**

```java
try (var executor = Executors
        .newVirtualThreadPerTaskExecutor()) {
    List<Future<Price>> futures =
        suppliers.stream()
            .map(s -> executor.submit(
                () -> s.getPrice(product)))
            .toList();

    return futures.stream()
        .map(f -> {
            try { return f.get(2, SECONDS); }
            catch (Exception e) {
                return Price.UNAVAILABLE;
            }
        })
        .min(Comparator.naturalOrder())
        .orElseThrow();
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Virtual threads make blocking I/O scalable - create millions, use simple blocking code
2. Don't pool virtual threads - create one per task, let JVM manage carriers
3. Replace `synchronized` with `ReentrantLock` to avoid carrier pinning

**Interview one-liner:**
"Virtual threads are JVM-managed lightweight threads that unmount from carrier OS threads during blocking I/O, enabling millions of concurrent tasks with simple blocking code instead of reactive frameworks."

---

### The Surprising Truth

Virtual threads make reactive programming frameworks (WebFlux, RxJava) largely unnecessary for I/O scalability. The entire complexity of Mono/Flux chains, backpressure, and callback hell exists to avoid blocking OS threads. Virtual threads achieve the same scalability with `thread.sleep()`, `socket.read()`, and `jdbc.query()` - the blocking APIs developers already know. Spring Boot 3.2+ lets you switch to virtual threads with a single property.

---

### Interview Deep-Dive

**Q1: When should you NOT use virtual threads?**

_Why they ask:_ Tests nuanced understanding beyond the hype.

_Strong answer:_

1. **CPU-bound computation:** Virtual threads help I/O-bound work. For CPU-bound work (number crunching, image processing), you're limited by CPU cores regardless. Use parallel streams or ForkJoinPool.

2. **Tasks holding `synchronized` locks during I/O:** Pins the carrier thread, defeating the purpose. Migrate to `ReentrantLock` first.

3. **Thread-local-heavy code:** Millions of virtual threads each with heavy thread-locals = memory explosion. Migrate to scoped values.

4. **Real-time/low-latency requirements:** Virtual thread scheduling adds slight unpredictability. For sub-millisecond latency (HFT), dedicated OS threads with CPU affinity are better.

5. **Already using reactive stack productively:** If your team has mastered WebFlux/RxJava and the codebase is stable, migrating to virtual threads may not be worth the effort.

---

**Q2: How do virtual threads differ from Go's goroutines?**

_Why they ask:_ Tests cross-language understanding.

_Strong answer:_

| Aspect        | Java Virtual Threads         | Go Goroutines            |
| ------------- | ---------------------------- | ------------------------ |
| Scheduling    | Cooperative (unmount at I/O) | Cooperative + preemptive |
| Communication | Shared memory + locks        | Channels (CSP model)     |
| Stack         | Starts at ~1KB, grows        | Starts at ~2KB, grows    |
| Maturity      | Java 21 (2023)               | Go 1.0 (2012)            |
| Integration   | Drop-in for existing APIs    | Native from day one      |

Key differences:

- Go goroutines communicate via channels (message passing). Java virtual threads use shared memory with locks (traditional Java model).
- Go has preemptive scheduling at function calls. Java virtual threads unmount only at blocking points (I/O, locks, sleep).
- Java virtual threads are compatible with all existing Java APIs, libraries, and debuggers. Go goroutines were designed into the language from scratch.

Java's advantage: backward compatibility. Existing JDBC drivers, HTTP clients, and Spring applications work with virtual threads without code changes.

---

**Q3: Explain the concept of pinning and how to diagnose it.**

_Why they ask:_ Tests production-readiness knowledge.

_Strong answer:_

Pinning occurs when a virtual thread cannot unmount from its carrier:

1. **Inside `synchronized` block/method:** The JVM uses OS monitors for `synchronized`, which are tied to the OS thread. The virtual thread must stay on its carrier.

2. **Inside native method (JNI):** Native code uses the OS thread directly.

When pinned, the carrier thread is blocked - no other virtual thread can use it. If all carriers are pinned, virtual threads stall.

**Diagnosis:**

```
-Djdk.tracePinnedThreads=full
```

This JVM flag prints a stack trace whenever a virtual thread is pinned:

```
Thread[#42,VirtualThread-42] pinned:
    java.base/java.lang.VirtualThread$VThread
    Holder.park(...)
    com.app.LegacyService.process(
        LegacyService.java:47)
        <== monitors:1
```

**Fix:**

```java
// Replace synchronized with ReentrantLock
private final ReentrantLock lock =
    new ReentrantLock();

void process() {
    lock.lock();
    try {
        // I/O operations here won't pin
        database.query(sql);
    } finally {
        lock.unlock();
    }
}
```

In large codebases, use jdeprscan or custom tooling to find all `synchronized` blocks that contain I/O operations.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Virtual Threads. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Scoped Values

**TL;DR** - Scoped values are immutable, thread-bound variables that replace ThreadLocal for virtual thread workloads, with automatic cleanup and zero per-thread storage cost when not used.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
ThreadLocal works by storing a value per thread in a map attached to the thread. With OS threads (hundreds), this is fine. With virtual threads (millions), each ThreadLocal slot consumes memory per virtual thread, and forgetting to call `remove()` causes memory leaks.

**THE BREAKING POINT:**
A request-context ThreadLocal stores user identity for the duration of a request. With 1 million virtual threads, each holding a ThreadLocal reference, the application leaks gigabytes of memory because some code paths skip the `finally { context.remove(); }` cleanup.

**THE INVENTION MOMENT:**
"This is exactly why scoped values were created."

**EVOLUTION:**
ThreadLocal (Java 1.2) -> InheritableThreadLocal (for child threads) -> ScopedValue (Java 20 preview, Java 21 preview, finalizing in later releases).

---

### Textbook Definition

A `ScopedValue` is a value that is bound for a bounded period of execution (a scope). Unlike ThreadLocal, scoped values are immutable within their scope, automatically cleaned up when the scope exits, and efficiently shared with child threads in structured concurrency. They are designed for the virtual thread era.

---

### Understand It in 30 Seconds

**One line:**
Scoped values are ThreadLocal's replacement - immutable, scope-bounded, and designed for millions of virtual threads.

**One analogy:**

> ThreadLocal is like a sticky note on your desk that stays until you remember to throw it away. ScopedValue is like a message on a whiteboard in a meeting room - it exists for the duration of the meeting and is automatically erased when the meeting ends.

**One insight:**
The key difference is lifecycle management. ThreadLocal values persist until explicitly removed (memory leak risk). Scoped values are bound to a code block and automatically unbound when the block exits, even if an exception occurs.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A scoped value lets you pass data through your code without adding it to every method parameter, and it automatically cleans itself up when the operation is done.

**Level 2 - How to use it (junior developer):**

```java
private static final ScopedValue<UserContext>
    CONTEXT = ScopedValue.newInstance();

void handleRequest(Request req) {
    UserContext ctx = authenticate(req);
    ScopedValue.where(CONTEXT, ctx)
        .run(() -> {
            // CONTEXT is available here
            processRequest(req);
        });
    // CONTEXT is automatically unbound here
}

void processRequest(Request req) {
    // Access without parameter passing
    UserContext ctx = CONTEXT.get();
    authorize(ctx, req.resource());
}
```

**Level 3 - How it works (mid-level engineer):**

ScopedValue uses a scope (code block) rather than thread-lifetime binding. Key properties:

- **Immutable:** Cannot be changed within a scope (rebinding creates a new scope)
- **Bounded:** Automatically unbound when scope exits
- **Inheritable:** Structured concurrency child tasks inherit parent's scoped values
- **Efficient:** No per-thread map - uses stack-like binding/unbinding

**Level 4 - Mastery (senior/staff+ engineer):**

ScopedValue is designed to work with structured concurrency. When a parent task forks child tasks using `StructuredTaskScope`, child virtual threads automatically see the parent's scoped values without explicit passing:

```java
ScopedValue.where(CONTEXT, ctx).run(() -> {
    try (var scope =
            new StructuredTaskScope<>()) {
        scope.fork(() -> {
            // CONTEXT.get() works here
            return fetchUserProfile();
        });
        scope.fork(() -> {
            // CONTEXT.get() works here too
            return fetchUserOrders();
        });
        scope.join();
    }
});
```

This is fundamentally better than InheritableThreadLocal, which copies the value to child threads and has no automatic cleanup.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - ThreadLocal (leak-prone):**

```java
private static final ThreadLocal<User> USER =
    new ThreadLocal<>();

void handle(Request req) {
    USER.set(authenticate(req));
    try {
        process(req);
    } finally {
        USER.remove(); // forget this = leak
    }
}
```

**GOOD - ScopedValue (auto-cleanup):**

```java
private static final ScopedValue<User> USER =
    ScopedValue.newInstance();

void handle(Request req) {
    ScopedValue.where(USER, authenticate(req))
        .run(() -> process(req));
    // Automatically unbound - no leak possible
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. ScopedValue replaces ThreadLocal for virtual threads - immutable, auto-cleanup, scope-bounded
2. `ScopedValue.where(KEY, value).run(task)` binds for the task's duration
3. Child tasks in structured concurrency inherit scoped values automatically

**Interview one-liner:**
"ScopedValues are immutable, scope-bounded thread context that replaces ThreadLocal for virtual thread workloads, with automatic cleanup and zero-cost inheritance for structured concurrency child tasks."

---

### The Surprising Truth

ScopedValue is faster than ThreadLocal for reads. ThreadLocal uses a hash map per thread (`Thread.threadLocals`), requiring a hash lookup on every `get()`. ScopedValue uses a simple stack-like structure that the JIT compiler can optimize to a direct memory access in most cases.

---

### Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Scoped Values. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Structured Concurrency

**TL;DR** - Structured concurrency treats groups of related concurrent tasks as a single unit of work with unified error handling and cancellation, preventing thread leaks and orphaned tasks.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
When you fork multiple tasks with `CompletableFuture` or `ExecutorService`, each task is independent. If one fails, the others keep running. If the parent thread is cancelled, the child tasks are orphaned. Error handling requires complex `allOf`/`anyOf` composition. Resource cleanup is manual and error-prone.

**THE BREAKING POINT:**
A request handler forks three API calls. The first returns successfully, the second throws an exception, and the third runs for 30 seconds because nobody cancelled it. The response was already sent with an error, but the third task is still consuming a thread, a network connection, and server resources.

**THE INVENTION MOMENT:**
"This is exactly why structured concurrency was created."

**EVOLUTION:**
Raw threads (Java 1.0) -> ExecutorService (Java 5) -> CompletableFuture (Java 8) -> StructuredTaskScope (Java 19 preview, Java 21 preview, finalizing in later releases).

---

### Textbook Definition

Structured concurrency ensures that concurrent tasks started within a scope cannot outlive that scope. When a `StructuredTaskScope` is closed, all tasks must be complete - either finished, failed, or cancelled. This makes concurrent code as predictable as sequential code: tasks are scoped, errors propagate, and resources are cleaned up.

---

### Understand It in 30 Seconds

**One line:**
Structured concurrency makes concurrent tasks behave like structured code blocks - they start together, end together, and errors propagate naturally.

**One analogy:**

> Unstructured concurrency is like sending multiple employees on errands without a meeting point. If one gets lost, you don't know until end of day. Structured concurrency is like a field trip with a bus - everyone leaves together, returns together, and if one person needs to leave early, the whole group is accounted for.

**One insight:**
The key insight is that a group of concurrent tasks should have the same lifecycle as the code block that created them. Just as a local variable cannot outlive its method, a forked task should not outlive its scope. This eliminates an entire class of bugs: orphaned tasks, leaked threads, and unobserved exceptions.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Structured concurrency means "tasks that are started together finish together." If one task fails, the others are cancelled automatically. No tasks are left running in the background forgotten.

**Level 2 - How to use it (junior developer):**

```java
// Fan-out: call two APIs concurrently
try (var scope = new StructuredTaskScope
        .ShutdownOnFailure()) {
    Subtask<User> userTask =
        scope.fork(() -> fetchUser(id));
    Subtask<Order> orderTask =
        scope.fork(() -> fetchOrder(id));

    scope.join();          // wait for both
    scope.throwIfFailed(); // propagate errors

    // Both succeeded
    return new UserOrder(
        userTask.get(), orderTask.get());
}
// Scope closed - all tasks guaranteed complete
```

**Level 3 - How it works (mid-level engineer):**

`StructuredTaskScope` provides two built-in policies:

1. **ShutdownOnFailure:** If any task fails, cancel the remaining tasks. Use when all tasks must succeed.

2. **ShutdownOnSuccess:** When the first task succeeds, cancel the remaining tasks. Use for "fastest wins" patterns.

```java
// Fastest wins: first successful response used
try (var scope = new StructuredTaskScope
        .ShutdownOnSuccess<String>()) {
    scope.fork(() -> fetchFromCDN1(url));
    scope.fork(() -> fetchFromCDN2(url));
    scope.fork(() -> fetchFromOrigin(url));

    scope.join();
    return scope.result(); // first to succeed
}
// Slower tasks automatically cancelled
```

**Level 4 - Mastery (senior/staff+ engineer):**

Structured concurrency combined with scoped values creates a clean context-propagation model:

```java
ScopedValue.where(REQUEST_ID, reqId).run(() -> {
    try (var scope = new StructuredTaskScope
            .ShutdownOnFailure()) {
        // Child tasks inherit REQUEST_ID
        scope.fork(() -> auditLog());
        scope.fork(() -> processPayment());
        scope.join();
        scope.throwIfFailed();
    }
});
```

Custom task scopes can implement domain-specific policies:

- Retry failed tasks
- Require quorum (N of M must succeed)
- Aggregate partial results

The observability benefit is significant: thread dumps show the task hierarchy (parent-child relationship), making debugging concurrent code dramatically easier than with unstructured `CompletableFuture` chains.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Unstructured concurrency (leaked tasks):**

```java
Future<User> userFuture =
    executor.submit(() -> fetchUser(id));
Future<Order> orderFuture =
    executor.submit(() -> fetchOrder(id));

User user = userFuture.get(); // blocks
// If this throws, orderFuture keeps running!
Order order = orderFuture.get();
```

**GOOD - Structured concurrency:**

```java
try (var scope = new StructuredTaskScope
        .ShutdownOnFailure()) {
    var user = scope.fork(() -> fetchUser(id));
    var order = scope.fork(() -> fetchOrder(id));

    scope.join();
    scope.throwIfFailed();
    // If fetchUser fails, fetchOrder is cancelled
    return new Response(
        user.get(), order.get());
}
// All tasks complete before scope closes
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Tasks cannot outlive their scope - no orphaned threads
2. `ShutdownOnFailure`: all must succeed, cancel on first failure
3. `ShutdownOnSuccess`: first wins, cancel the rest

**Interview one-liner:**
"Structured concurrency scopes concurrent tasks so they cannot outlive their parent, with automatic cancellation on failure and unified error handling, eliminating orphaned tasks and leaked threads."

---

### The Surprising Truth

Structured concurrency makes thread dumps useful again. With unstructured concurrency, a thread dump shows isolated threads with no relationship to each other. With structured concurrency, thread dumps show the parent-child task hierarchy, making it immediately clear which tasks belong to which request and what the overall state is.

---

### Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Structured Concurrency. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# String Templates

**TL;DR** - String templates (preview feature) enable safe, readable string interpolation with embedded expressions, replacing error-prone string concatenation while allowing custom processors for SQL, JSON, and HTML injection prevention.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Java string composition uses concatenation (`"Hello " + name`), `String.format("Hello %s", name)`, or `MessageFormat`. All are verbose, error-prone (wrong format specifier, wrong argument order), and provide no protection against injection attacks when building SQL, HTML, or JSON.

**THE BREAKING POINT:**
Every other modern language (Kotlin, Python, JavaScript, C#, Swift) has string interpolation. Java developers write `"User " + user.getName() + " (id=" + user.getId() + ")"` while Kotlin developers write `"User ${user.name} (id=${user.id})"`. The verbosity gap is embarrassing and contributes to Java's reputation as boilerplate-heavy.

**THE INVENTION MOMENT:**
"This is exactly why string templates were created."

**EVOLUTION:**
Concatenation with `+` -> `String.format()` (Java 5) -> text blocks (Java 15) -> string templates (Java 21 preview, evolving). Note: String templates were previewed in Java 21 but were subsequently withdrawn for redesign, as the template processor API needed refinement.

---

### Textbook Definition

String templates allow embedding expressions directly in string literals using `\{expression}` syntax. Unlike simple interpolation in other languages, Java's design includes template processors - pluggable components that can validate and transform the template before producing a result, enabling injection-safe SQL, HTML, and JSON composition.

---

### Understand It in 30 Seconds

**One line:**
String templates embed expressions in strings with `\{expr}` and support custom processors for safe SQL/HTML generation.

**One analogy:**

> Simple string interpolation is like a form where you fill in the blanks with a pen - whatever you write goes in verbatim, including malicious content. Template processors are like a form that validates and sanitizes every field before accepting it.

**One insight:**
The template processor concept is what distinguishes Java's approach from every other language. `STR."Hello \{name}"` is simple interpolation. But `SQL."SELECT * FROM users WHERE name = \{name}"` could produce a `PreparedStatement` with proper parameterization - making SQL injection impossible by construction.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of joining strings with `+`, you write the string naturally with expressions inside `\{...}` placeholders.

**Level 2 - How to use it (junior developer):**

```java
// Before: concatenation
String msg = "Hello " + name + ", you have "
    + count + " items.";

// After: string template (preview)
String msg = STR."Hello \{name}, you have \{count} items.";

// Expressions allowed
String msg = STR."Total: \{price * quantity}";
String msg = STR."Status: \{user.isActive() ? "active" : "inactive"}";
```

**Level 3 - How it works (mid-level engineer):**

Templates are not just syntactic sugar for concatenation. A template literal like `STR."Hello \{name}"` is processed by the `STR` template processor. Custom processors can produce any type, not just String:

```java
// Hypothetical SQL processor
PreparedStatement stmt = SQL."""
    SELECT * FROM users
    WHERE name = \{name}
    AND age > \{minAge}
    """;
// Produces parameterized query, not string
// SQL injection impossible
```

**Level 4 - Mastery (senior/staff+ engineer):**

The template processor API separates the template (structure) from the values (data), enabling:

- **SQL processor:** Generates PreparedStatement with bind parameters
- **JSON processor:** Produces validated JSON with proper escaping
- **HTML processor:** Escapes all interpolated values to prevent XSS
- **i18n processor:** Looks up localized template and formats values

This is a fundamentally different approach from other languages where interpolation always produces a String. Java's approach enables type-safe, injection-safe template processing. However, the initial API was withdrawn from preview for redesign, so the final form may differ from Java 21's version.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Concatenation (verbose, injection-prone):**

```java
String query = "SELECT * FROM users WHERE name = '"
    + userInput + "'"; // SQL INJECTION!
String html = "<p>Hello " + userInput
    + "</p>"; // XSS!
```

**GOOD - String template with processor:**

```java
// Simple interpolation (preview)
String msg = STR."Hello \{name}!";

// Multi-line with text block
String json = STR."""
    {
      "name": "\{user.name()}",
      "email": "\{user.email()}",
      "age": \{user.age()}
    }
    """;
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. `STR."...\{expr}..."` embeds expressions in strings (preview feature)
2. Template processors enable injection-safe SQL/HTML generation
3. Feature was previewed in Java 21 but withdrawn for redesign - final API may change

**Interview one-liner:**
"String templates enable expression interpolation with pluggable processors that can produce any type, not just strings, enabling injection-safe SQL and HTML by construction rather than convention."

---

### The Surprising Truth

Java deliberately delayed string interpolation for decades while every other language added it, because the Java team wanted to solve it with template processors - not just simple string interpolation. The goal was to make SQL injection and XSS impossible by construction rather than relying on developers to remember to sanitize. This ambitious design led to the feature being previewed and then withdrawn for further refinement.

---

### Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for String Templates. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

