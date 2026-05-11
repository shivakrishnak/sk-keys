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
version: 3
---

**Keywords covered in this file:**

- [Virtual Threads](#virtual-threads)
- [Scoped Values](#scoped-values)
- [Structured Concurrency](#structured-concurrency)
- [String Templates](#string-templates)

# Virtual Threads

**TL;DR** - Virtual threads are lightweight threads managed by the JVM that make blocking I/O scalable by allowing millions of threads without the memory and context-switching overhead of OS threads.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Each Java thread maps 1:1 to an OS thread. An OS thread uses 512KB-1MB of stack memory and requires an expensive kernel context switch. A server handling 10,000 concurrent connections needs 10,000 threads, consuming 5-10GB of memory just for stacks. Beyond 10K threads, the OS spends more time context-switching than doing useful work.

**THE BREAKING POINT:**
A microservice receives 50K concurrent requests during peak traffic. The thread pool has 200 threads. 49,800 requests queue, causing timeouts. Increasing the thread pool to 50K OS threads requires 25GB of RAM and makes the server unresponsive from context switching.

**THE INVENTION MOMENT:**
"This is exactly why virtual threads were created."

**EVOLUTION:**
OS threads (Java 1.0) -> thread pools and NIO for scalability (Java 1.4) -> CompletableFuture for async composition (Java 8) -> reactive frameworks (RxJava, WebFlux) -> virtual threads (Java 19 preview, Java 21 final). Virtual threads achieve the scalability of reactive without the complexity.
---

### 📘 Textbook Definition

Virtual threads (Project Loom) are lightweight threads managed by the JVM rather than the OS. They are mounted on carrier threads (a small pool of OS threads) and automatically unmount when they block on I/O, freeing the carrier for other virtual threads. This enables millions of concurrent threads with a simple blocking programming model.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
Virtual threads let you write simple blocking code that scales to millions of concurrent tasks.

**One analogy:**

> OS threads are like hiring a full-time employee for each customer - expensive and doesn't scale. Virtual threads are like a small team of employees serving a restaurant full of customers - when one customer is waiting for food (I/O), the employee serves another table.

**One insight:**
Virtual threads don't make code faster - they make code more scalable. A single request takes the same time. But instead of blocking an expensive OS thread during I/O waits, the virtual thread unmounts and the carrier thread serves other virtual threads. You get reactive scalability with blocking-style simplicity.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> Virtual threads are like green threads with a smart scheduler. Imagine a restaurant with 4 chefs (carrier threads) and 10,000 orders (virtual threads). Each chef works on an order until it needs to wait (oven timer = I/O). While waiting, the chef picks up another order. When the timer rings, any available chef continues the original order.

- "Chef" -> carrier thread (OS thread)
- "Order" -> virtual thread
- "Waiting for oven" -> blocking I/O (unmount)
- "Timer rings" -> I/O completes (remount)
- "Restaurant manager" -> JVM scheduler

Where this analogy breaks down: In a real restaurant, a chef can't pause mid-knife-cut. Virtual threads can be preempted at any blocking point.
---

### 📶 Gradual Depth - Five Levels

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
Virtual threads are the JVM's implementation of the universal lightweight concurrency primitive that exists in every modern runtime: Go goroutines, Kotlin coroutines, Erlang processes, Rust tokio tasks. The cross-domain insight: all of these solve the same problem - OS threads are too expensive (1MB stack, kernel scheduling overhead) to model one-thread-per-request at scale. Virtual threads solve this by decoupling the Java thread (the programming model) from the OS thread (the execution resource). A virtual thread is mounted on a carrier (platform) thread only while it has CPU work; during blocking IO, it unmounts, freeing the carrier for other virtual threads. At extreme scale (millions of concurrent connections), virtual threads eliminate the need for reactive programming (Project Reactor, RxJava) for IO-bound workloads while keeping the simple thread-per-request model. If redesigning today, virtual threads would be the ONLY thread type, and platform threads would be an implementation detail never exposed to developers.

**Expert thinking cues:**
- "Is this IO-bound or CPU-bound?" - virtual threads help IO-bound; CPU-bound needs platform threads
- "Are we pinning?" - synchronized blocks and native calls pin virtual threads to carriers
- "Is thread-per-request viable now?" - with virtual threads, yes - even at millions of requests
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

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** Lightweight threads managed by the JVM (not OS), enabling millions of concurrent threads for IO-bound workloads (JDK 21)
**PROBLEM IT SOLVES:** OS thread limits (~10K) force complex async/reactive code for high-concurrency IO workloads
**KEY INSIGHT:** Virtual threads decouple the Java thread (programming model) from the OS thread (execution resource)
**USE WHEN:** IO-bound workloads (HTTP servers, DB queries, microservice calls) needing high concurrency with simple code
**AVOID WHEN:** CPU-bound computation (use platform thread pools), or when using synchronized blocks extensively (pinning)
**ANTI-PATTERN:** Pooling virtual threads - they are cheap to create and should be one-per-task, never pooled
**TRADE-OFF:** Simplicity (thread-per-request) vs control (reactive gives more backpressure control)
**ONE-LINER:** "Virtual threads make thread-per-request viable at million-connection scale with blocking code"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Virtual threads make blocking I/O scalable - create millions, use simple blocking code
2. Don't pool virtual threads - create one per task, let JVM manage carriers
3. Replace `synchronized` with `ReentrantLock` to avoid carrier pinning

**Interview one-liner:**
"Virtual threads are JVM-managed lightweight threads that unmount from carrier OS threads during blocking I/O, enabling millions of concurrent tasks with simple blocking code instead of reactive frameworks."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Virtual threads make reactive programming frameworks (WebFlux, RxJava) largely unnecessary for I/O scalability. The entire complexity of Mono/Flux chains, backpressure, and callback hell exists to avoid blocking OS threads. Virtual threads achieve the same scalability with `thread.sleep()`, `socket.read()`, and `jdbc.query()` - the blocking APIs developers already know. Spring Boot 3.2+ lets you switch to virtual threads with a single property.
---

### ⚖️ Comparison Table

| Aspect | Virtual Threads | Platform Threads | Reactive (Reactor) |
|--------|----------------|-----------------|-------------------|
| Stack size | ~1KB (grows) | ~1MB fixed | N/A (callback) |
| Max count | Millions | ~10K | N/A (event loop) |
| Blocking IO | Unmounts carrier | Blocks OS thread | Non-blocking |
| Code style | Imperative/blocking | Imperative/blocking | Reactive/functional |
| Debugging | Standard stack traces | Standard stack traces | Complex (async) |
| Best for | IO-bound, high concurrency | CPU-bound | IO-bound, backpressure |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Virtual threads are faster than platform threads | Virtual threads are not faster per-task. They are more scalable - you can have millions of them. A single virtual thread runs at the same speed as a platform thread. |
| 2 | Virtual threads replace reactive programming entirely | For IO-bound workloads, yes. But reactive frameworks still provide backpressure, which virtual threads don't. CPU-bound work still needs bounded thread pools. |
| 3 | Virtual threads should be pooled | Never pool virtual threads. They are cheap to create (~1KB) and meant to be one-per-task. Pooling adds complexity without benefit. |
| 4 | synchronized works fine with virtual threads | synchronized blocks PIN virtual threads to carrier threads, blocking the carrier. Replace synchronized with ReentrantLock to allow unmounting during contention. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Thread pinning due to synchronized blocks**
**Symptom:** Virtual thread pool carriers are all blocked. Throughput drops to number of carrier threads. Thread dump shows virtual threads stuck in synchronized.
**Root Cause:** `synchronized` blocks pin virtual threads to carrier (platform) threads. The carrier cannot be reused until the synchronized block exits, even during IO waits inside it.
**Diagnostic:**

```
# JDK 21+: detect pinning with JFR events
# -Djdk.tracePinnedThreads=short (or =full)
# Look for jdk.VirtualThreadPinned events in JFR
jcmd <pid> JFR.start name=pin duration=60s
```

**Fix:**
```java
// BAD: synchronized pins virtual thread
synchronized (lock) {
    var result = httpClient.send(req, handler);
    // Carrier is pinned during entire HTTP call
}

// GOOD: use ReentrantLock instead
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    var result = httpClient.send(req, handler);
    // Virtual thread can unmount during IO
} finally {
    lock.unlock();
}
```
**Prevention:** Replace all `synchronized` with `ReentrantLock` in code that runs on virtual threads. Use `-Djdk.tracePinnedThreads=short` to detect pinning.

**Failure Mode 2: Memory exhaustion from millions of virtual threads**
**Symptom:** OutOfMemoryError. Each virtual thread holds request state, accumulated objects fill heap.
**Root Cause:** Creating millions of virtual threads, each holding significant state (large request bodies, database result sets). Virtual threads are cheap but their stack/state is not free.
**Diagnostic:**

```
# Count active virtual threads
jcmd <pid> Thread.dump_to_file -format=json threads.json
# Check heap usage per thread
jmap -histo:live <pid> | head -20
```

**Fix:**
```java
// BAD: unlimited virtual threads with large state
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    for (var req : millionsOfRequests) {
        exec.submit(() -> processLargePayload(req));
    }
}

// GOOD: use semaphore to bound concurrency
Semaphore permits = new Semaphore(10_000);
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    for (var req : millionsOfRequests) {
        permits.acquire();
        exec.submit(() -> {
            try { processLargePayload(req); }
            finally { permits.release(); }
        });
    }
}
```
**Prevention:** Bound concurrency with Semaphore when memory per task is significant. Monitor heap usage. Virtual threads are cheap but not free.

**Failure Mode 3: ThreadLocal memory leaks at scale**
**Symptom:** Heap grows linearly with virtual thread count. GC can't reclaim ThreadLocal-attached objects.
**Root Cause:** Each virtual thread gets its own ThreadLocal copies. With millions of virtual threads, ThreadLocal storage becomes a significant memory consumer.
**Diagnostic:**

```
# Heap dump analysis
jmap -dump:live,format=b,file=heap.hprof <pid>
# In Eclipse MAT: find ThreadLocal instances
# Look for ThreadLocal$ThreadLocalMap entries
```

**Fix:**
```java
// BAD: ThreadLocal with virtual threads
private static final ThreadLocal<ExpensiveObj> cache =
    ThreadLocal.withInitial(ExpensiveObj::new);
// Millions of virtual threads = millions of objects

// GOOD: use ScopedValue or shared cache
private static final ScopedValue<RequestCtx> CTX =
    ScopedValue.newInstance();
ScopedValue.where(CTX, new RequestCtx(userId))
    .run(() -> handleRequest());
```
**Prevention:** Replace ThreadLocal with ScopedValue for virtual threads. Audit all ThreadLocal usage before migrating to virtual threads.
---

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Java threading and concurrency - Thread, Runnable, ExecutorService, thread pools
- Blocking IO vs non-blocking IO - understanding why blocking wastes OS threads

**Builds on this (learn these next):**

- Structured Concurrency - managing virtual thread lifetimes with StructuredTaskScope
- Scoped Values - replacing ThreadLocal for virtual thread-safe context propagation

**Alternatives / Comparisons:**

- Project Reactor / RxJava - reactive streams for IO-bound work with backpressure (more complex)
- Kotlin Coroutines - similar lightweight concurrency with suspend functions (Kotlin-specific)


---

---

# Scoped Values

**TL;DR** - Scoped values are immutable, thread-bound variables that replace ThreadLocal for virtual thread workloads, with automatic cleanup and zero per-thread storage cost when not used.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
ThreadLocal works by storing a value per thread in a map attached to the thread. With OS threads (hundreds), this is fine. With virtual threads (millions), each ThreadLocal slot consumes memory per virtual thread, and forgetting to call `remove()` causes memory leaks.

**THE BREAKING POINT:**
A request-context ThreadLocal stores user identity for the duration of a request. With 1 million virtual threads, each holding a ThreadLocal reference, the application leaks gigabytes of memory because some code paths skip the `finally { context.remove(); }` cleanup.

**THE INVENTION MOMENT:**
"This is exactly why scoped values were created."

**EVOLUTION:**
ThreadLocal (Java 1.2) -> InheritableThreadLocal (for child threads) -> ScopedValue (Java 20 preview, Java 21 preview, finalizing in later releases).
---

### 📘 Textbook Definition

A `ScopedValue` is a value that is bound for a bounded period of execution (a scope). Unlike ThreadLocal, scoped values are immutable within their scope, automatically cleaned up when the scope exits, and efficiently shared with child threads in structured concurrency. They are designed for the virtual thread era.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
Scoped values are ThreadLocal's replacement - immutable, scope-bounded, and designed for millions of virtual threads.

**One analogy:**

> ThreadLocal is like a sticky note on your desk that stays until you remember to throw it away. ScopedValue is like a message on a whiteboard in a meeting room - it exists for the duration of the meeting and is automatically erased when the meeting ends.

**One insight:**
The key difference is lifecycle management. ThreadLocal values persist until explicitly removed (memory leak risk). Scoped values are bound to a code block and automatically unbound when the block exits, even if an exception occurs.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

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
Scoped values are the successor to ThreadLocal that solves its fundamental design flaws: unbounded lifetime, memory leaks, and incompatibility with virtual threads. The same scoped-context pattern appears in Go's `context.Context`, Rust's task-local storage, and React's Context API. The cross-domain insight: when you need to pass contextual data (user identity, correlation ID, transaction context) through a deep call stack without parameter threading, you need a scope-bound, immutable, inheritable container. ThreadLocal's mutability and unbounded lifetime make it a memory leak factory in virtual thread scenarios (millions of threads = millions of ThreadLocal copies). Scoped values fix this by being immutable, bound to a structured scope (runs only within a `where().run()` block), and automatically cleaned up when the scope exits. If redesigning today, scoped values would be the only mechanism for thread-contextual data, and ThreadLocal would not exist.

**Expert thinking cues:**
- "Is this data per-request or per-thread?" - scoped values model per-scope, which aligns with per-request
- "Is this mutable?" - if yes, scoped values won't work; rethink the design
- "How many threads will exist?" - if millions (virtual threads), ThreadLocal is a memory bomb
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** Immutable, scope-bound context values that replace ThreadLocal for passing data through call stacks (JDK 21 preview)
**PROBLEM IT SOLVES:** ThreadLocal memory leaks and unbounded lifetime in virtual thread scenarios with millions of threads
**KEY INSIGHT:** Scoped values are immutable, bound to a structured scope, and automatically cleaned up - unlike ThreadLocal
**USE WHEN:** Passing request context (user ID, correlation ID, transaction) through deep call stacks without parameters
**AVOID WHEN:** Mutable per-thread state is needed (scoped values are immutable), or on JDK versions before 21
**ANTI-PATTERN:** Using ThreadLocal with virtual threads - millions of threads create millions of ThreadLocal copies
**TRADE-OFF:** Immutability constraint vs memory safety and predictable lifecycle
**ONE-LINER:** "Scoped values are ThreadLocal done right: immutable, scoped, and safe for virtual threads"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. ScopedValue replaces ThreadLocal for virtual threads - immutable, auto-cleanup, scope-bounded
2. `ScopedValue.where(KEY, value).run(task)` binds for the task's duration
3. Child tasks in structured concurrency inherit scoped values automatically

**Interview one-liner:**
"ScopedValues are immutable, scope-bounded thread context that replaces ThreadLocal for virtual thread workloads, with automatic cleanup and zero-cost inheritance for structured concurrency child tasks."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

ScopedValue is faster than ThreadLocal for reads. ThreadLocal uses a hash map per thread (`Thread.threadLocals`), requiring a hash lookup on every `get()`. ScopedValue uses a simple stack-like structure that the JIT compiler can optimize to a direct memory access in most cases.
---

### ⚖️ Comparison Table

| Aspect | ScopedValue | ThreadLocal | Parameter passing |
|--------|------------|-------------|------------------|
| Mutability | Immutable | Mutable | Immutable (by convention) |
| Lifetime | Scope-bound | Unbounded | Call stack |
| Cleanup | Automatic | Manual (remove()) | Automatic |
| Inheritance | StructuredTaskScope | InheritableThreadLocal | Explicit |
| Virtual thread safe | Yes | No (memory leak) | Yes |
| Performance | Optimized | Hash lookup | Zero overhead |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Scoped values are just immutable ThreadLocals | Scoped values have fundamentally different semantics: scope-bound lifetime (auto-cleanup), no set() method, and optimized for virtual threads. They're a new abstraction, not a ThreadLocal variant. |
| 2 | Scoped values can replace all ThreadLocal uses | Scoped values are immutable within a scope. If you need mutable per-thread state (counters, buffers), ThreadLocal is still necessary. |
| 3 | Scoped values are only for virtual threads | Scoped values work with both platform and virtual threads. They are beneficial for any code that needs scoped context, regardless of thread type. |
| 4 | Scoped values have high overhead | Scoped values are optimized by the JVM to be faster than ThreadLocal for read-heavy patterns. The immutability enables caching optimizations. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Accessing scoped value outside its scope**
**Symptom:** `NoSuchElementException` when calling `scopedValue.get()` outside a `where().run()` block.
**Root Cause:** Scoped values are only bound within their scope. Accessing them from a thread or code path not within the `where().run()` scope throws an exception.
**Diagnostic:**

```
# Look for ScopedValue.get() calls
grep -rn "\.get()" src/ | grep -i scoped
# Ensure every get() is within a where().run() scope
```

**Fix:**
```java
// BAD: accessing outside scope
static final ScopedValue<String> USER =
    ScopedValue.newInstance();
void process() {
    String u = USER.get(); // NoSuchElementException!
}

// GOOD: always access within scope
ScopedValue.where(USER, "alice").run(() -> {
    process(); // USER.get() works here
});
// Or check: if (USER.isBound()) { USER.get(); }
```
**Prevention:** Always check `isBound()` before `get()` in code that might run outside a scope. Design APIs to require scoped context.

**Failure Mode 2: Trying to mutate a scoped value**
**Symptom:** Compilation error or design confusion when trying to change a scoped value within its scope.
**Root Cause:** Scoped values are immutable within a scope. There is no `set()` method. To change the value, you must create a new nested scope.
**Diagnostic:**

```
# Look for attempts to reassign scoped values
grep -rn "ScopedValue" src/ | grep "set\|assign\|="
```

**Fix:**
```java
// BAD: trying to mutate scoped value
static final ScopedValue<String> ROLE =
    ScopedValue.newInstance();
ScopedValue.where(ROLE, "user").run(() -> {
    // ROLE.set("admin"); // No set() method!
    
    // GOOD: create a nested scope
    ScopedValue.where(ROLE, "admin").run(() -> {
        // ROLE.get() returns "admin" here
    });
    // ROLE.get() returns "user" here
});
```
**Prevention:** Design for immutability. If value needs to change, use nested scopes. If mutable state is required, scoped values are not the right tool.

**Failure Mode 3: ScopedValue not inherited by child threads**
**Symptom:** Child threads spawned with `Thread.start()` cannot access parent's scoped values. `NoSuchElementException` in child.
**Root Cause:** Scoped values are only inherited through `StructuredTaskScope`. Raw `Thread.start()` creates unstructured threads that don't inherit scoped values.
**Diagnostic:**

```
# Find thread creation inside scoped value scopes
grep -rn "Thread(" src/ | grep -v "test"
# These won't inherit scoped values
```

**Fix:**
```java
// BAD: raw thread doesn't inherit scoped values
ScopedValue.where(USER, "alice").run(() -> {
    new Thread(() -> {
        USER.get(); // NoSuchElementException!
    }).start();
});

// GOOD: use StructuredTaskScope for inheritance
ScopedValue.where(USER, "alice").run(() -> {
    try (var scope = new StructuredTaskScope<>()) {
        scope.fork(() -> {
            USER.get(); // Works! Inherited via scope
            return null;
        });
        scope.join();
    }
});
```
**Prevention:** Always use StructuredTaskScope to spawn child tasks when scoped values need to be inherited. Never use raw Thread creation.
---

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- ThreadLocal - understanding per-thread storage, its API, and its memory leak problems
- Virtual Threads - why ThreadLocal is problematic at million-thread scale

**Builds on this (learn these next):**

- Structured Concurrency - scoped values inherit through StructuredTaskScope, not raw threads
- Context propagation - how scoped values replace MDC, SecurityContext in frameworks

**Alternatives / Comparisons:**

- ThreadLocal - mutable, unbounded lifetime, works everywhere but leaks with virtual threads
- Parameter passing - explicit, refactor-friendly, but verbose in deep call stacks


---

---

# Structured Concurrency

**TL;DR** - Structured concurrency treats groups of related concurrent tasks as a single unit of work with unified error handling and cancellation, preventing thread leaks and orphaned tasks.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
When you fork multiple tasks with `CompletableFuture` or `ExecutorService`, each task is independent. If one fails, the others keep running. If the parent thread is cancelled, the child tasks are orphaned. Error handling requires complex `allOf`/`anyOf` composition. Resource cleanup is manual and error-prone.

**THE BREAKING POINT:**
A request handler forks three API calls. The first returns successfully, the second throws an exception, and the third runs for 30 seconds because nobody cancelled it. The response was already sent with an error, but the third task is still consuming a thread, a network connection, and server resources.

**THE INVENTION MOMENT:**
"This is exactly why structured concurrency was created."

**EVOLUTION:**
Raw threads (Java 1.0) -> ExecutorService (Java 5) -> CompletableFuture (Java 8) -> StructuredTaskScope (Java 19 preview, Java 21 preview, finalizing in later releases).
---

### 📘 Textbook Definition

Structured concurrency ensures that concurrent tasks started within a scope cannot outlive that scope. When a `StructuredTaskScope` is closed, all tasks must be complete - either finished, failed, or cancelled. This makes concurrent code as predictable as sequential code: tasks are scoped, errors propagate, and resources are cleaned up.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
Structured concurrency makes concurrent tasks behave like structured code blocks - they start together, end together, and errors propagate naturally.

**One analogy:**

> Unstructured concurrency is like sending multiple employees on errands without a meeting point. If one gets lost, you don't know until end of day. Structured concurrency is like a field trip with a bus - everyone leaves together, returns together, and if one person needs to leave early, the whole group is accounted for.

**One insight:**
The key insight is that a group of concurrent tasks should have the same lifecycle as the code block that created them. Just as a local variable cannot outlive its method, a forked task should not outlive its scope. This eliminates an entire class of bugs: orphaned tasks, leaked threads, and unobserved exceptions.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

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
Structured concurrency applies the structured programming principle (every block has one entry, one exit) to concurrent tasks. Just as structured programming replaced goto with blocks, structured concurrency replaces fire-and-forget threads with scoped task groups. This same pattern appears in Kotlin's coroutineScope, Swift's TaskGroup, Python's trio nurseries, and Go's errgroup. The cross-domain insight: unstructured concurrency (raw thread creation) is the concurrent equivalent of goto - it creates invisible control flow paths that leak resources, orphan tasks, and make error handling impossible. Structured concurrency guarantees: if a scope exits, all child tasks have completed (or been cancelled). This makes concurrent code as predictable as sequential code. At extreme scale, structured concurrency composes with virtual threads and scoped values to form a complete concurrency model: lightweight threads (virtual), scoped context (scoped values), and lifetime management (structured concurrency). If redesigning today, `Thread.start()` would not exist - only structured task submission.

**Expert thinking cues:**
- "What happens to child tasks when the parent fails?" - structured concurrency guarantees cancellation
- "Can tasks outlive their scope?" - structured = no, unstructured = yes (and that's the bug)
- "How do I compose concurrent operations?" - StructuredTaskScope is the composition primitive
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** API for managing concurrent subtasks as a unit with guaranteed lifetime and cancellation semantics (JDK 21 preview)
**PROBLEM IT SOLVES:** Fire-and-forget threads leak resources, orphan tasks, and make error handling in concurrent code impossible
**KEY INSIGHT:** If a scope exits, ALL child tasks have completed or been cancelled - concurrent code becomes as predictable as sequential
**USE WHEN:** Fan-out/fan-in patterns, parallel API calls, any concurrent work that should have a bounded lifetime
**AVOID WHEN:** Truly independent background tasks that should outlive the request, or fire-and-forget scenarios
**ANTI-PATTERN:** Using raw Thread.start() or ExecutorService.submit() without lifetime management - tasks can leak
**TRADE-OFF:** Strict lifetime control vs flexibility of unstructured fire-and-forget concurrency
**ONE-LINER:** "Structured concurrency is to threads what structured programming was to goto"
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Tasks cannot outlive their scope - no orphaned threads
2. `ShutdownOnFailure`: all must succeed, cancel on first failure
3. `ShutdownOnSuccess`: first wins, cancel the rest

**Interview one-liner:**
"Structured concurrency scopes concurrent tasks so they cannot outlive their parent, with automatic cancellation on failure and unified error handling, eliminating orphaned tasks and leaked threads."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Structured concurrency makes thread dumps useful again. With unstructured concurrency, a thread dump shows isolated threads with no relationship to each other. With structured concurrency, thread dumps show the parent-child task hierarchy, making it immediately clear which tasks belong to which request and what the overall state is.
---

### ⚖️ Comparison Table

| Aspect | StructuredTaskScope | ExecutorService | CompletableFuture |
|--------|-------------------|----------------|------------------|
| Lifetime | Scope-bound | Unbounded | Unbounded |
| Cancellation | Automatic on failure | Manual | Manual |
| Error handling | ShutdownOnFailure | try-catch per task | exceptionally() |
| Task leaks | Impossible | Common | Common |
| Debugging | Clear parent-child | Disconnected | Disconnected |
| Virtual thread aware | Yes | Partially | No |
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Structured concurrency is just a try-with-resources for threads | It's deeper: structured concurrency guarantees that ALL subtasks complete before the scope exits, propagates cancellation to children, and creates a parent-child relationship visible in debugging. |
| 2 | Structured concurrency prevents all task leaks | Within a StructuredTaskScope, yes. But code can still create unstructured threads outside the scope. Discipline is needed to use structured concurrency consistently. |
| 3 | Structured concurrency is only for fan-out patterns | It applies to any concurrent work with bounded lifetime: parallel API calls, concurrent validation, map-reduce, timeout handling, and competitive execution (first-to-complete). |
| 4 | You need structured concurrency for simple parallelism | For embarrassingly parallel, independent tasks with no error correlation, a simple parallel stream or ExecutorService may be simpler. Structured concurrency shines when tasks are related. |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Forgetting to call join() before processing results**
**Symptom:** `IllegalStateException` when calling `subtask.get()` or scope methods before `join()` completes.
**Root Cause:** StructuredTaskScope requires `join()` to be called before accessing results. This ensures all subtasks have completed.
**Diagnostic:**

```
# Look for result access before join()
grep -rn "subtask.get\|scope.result" src/
# Ensure join() is called before any result access
```

**Fix:**
```java
// BAD: accessing result before join
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var task = scope.fork(() -> fetchData());
    String data = task.get(); // IllegalStateException!
    scope.join();
}

// GOOD: join first, then access results
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var task = scope.fork(() -> fetchData());
    scope.join();
    scope.throwIfFailed();
    String data = task.get(); // Safe after join
}
```
**Prevention:** Always follow the pattern: fork -> join -> throwIfFailed -> get results. Never access subtask results before join.

**Failure Mode 2: Task leak when not using try-with-resources**
**Symptom:** Subtasks continue running after the logical scope has ended. Resource leaks, orphaned operations.
**Root Cause:** StructuredTaskScope implements AutoCloseable. Without try-with-resources, close() is not called, and subtasks may not be cancelled on scope exit.
**Diagnostic:**

```
# Find scope creation without try-with-resources
grep -rn "StructuredTaskScope" src/ | grep -v "try"
# These are potential task leak sites
```

**Fix:**
```java
// BAD: manual scope management, easy to leak
var scope = new StructuredTaskScope.ShutdownOnFailure();
scope.fork(() -> riskyOperation());
// If exception thrown here, scope never closed!
scope.join();
scope.close();

// GOOD: try-with-resources guarantees cleanup
try (var scope = new StructuredTaskScope
        .ShutdownOnFailure()) {
    scope.fork(() -> riskyOperation());
    scope.join();
    scope.throwIfFailed();
} // Automatically cancels and closes
```
**Prevention:** ALWAYS use try-with-resources with StructuredTaskScope. Never manually manage scope lifecycle.

**Failure Mode 3: Using ShutdownOnSuccess when all results are needed**
**Symptom:** Some subtasks are cancelled before completing. Missing results from cancelled tasks.
**Root Cause:** `ShutdownOnSuccess` cancels remaining subtasks when the FIRST one succeeds. If you need ALL results, this policy is wrong.
**Diagnostic:**

```
grep -rn "ShutdownOnSuccess" src/
# Verify that only one result is actually needed
# If all results needed, use ShutdownOnFailure
```

**Fix:**
```java
// BAD: ShutdownOnSuccess when all needed
try (var scope = new StructuredTaskScope
        .ShutdownOnSuccess<String>()) {
    var t1 = scope.fork(() -> fetchFromDB());
    var t2 = scope.fork(() -> fetchFromAPI());
    scope.join();
    // t2 might be cancelled if t1 finished first!
}

// GOOD: ShutdownOnFailure to wait for ALL
try (var scope = new StructuredTaskScope
        .ShutdownOnFailure()) {
    var t1 = scope.fork(() -> fetchFromDB());
    var t2 = scope.fork(() -> fetchFromAPI());
    scope.join();
    scope.throwIfFailed();
    combine(t1.get(), t2.get()); // Both available
}
```
**Prevention:** Use `ShutdownOnFailure` when you need ALL results. Use `ShutdownOnSuccess` only for competitive execution (first-to-complete wins).
---

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- Virtual Threads - the lightweight thread primitive that structured concurrency manages
- CompletableFuture / ExecutorService - the unstructured concurrency APIs that this replaces

**Builds on this (learn these next):**

- Scoped Values - context propagation through structured task scopes
- Error handling in concurrent systems - how structured concurrency simplifies error aggregation

**Alternatives / Comparisons:**

- ExecutorService + Future - unstructured, more flexible but prone to task leaks
- CompletableFuture chains - functional composition but complex error handling and debugging


---

---

# String Templates

**TL;DR** - String templates (preview feature) enable safe, readable string interpolation with embedded expressions, replacing error-prone string concatenation while allowing custom processors for SQL, JSON, and HTML injection prevention.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Java string composition uses concatenation (`"Hello " + name`), `String.format("Hello %s", name)`, or `MessageFormat`. All are verbose, error-prone (wrong format specifier, wrong argument order), and provide no protection against injection attacks when building SQL, HTML, or JSON.

**THE BREAKING POINT:**
Every other modern language (Kotlin, Python, JavaScript, C#, Swift) has string interpolation. Java developers write `"User " + user.getName() + " (id=" + user.getId() + ")"` while Kotlin developers write `"User ${user.name} (id=${user.id})"`. The verbosity gap is embarrassing and contributes to Java's reputation as boilerplate-heavy.

**THE INVENTION MOMENT:**
"This is exactly why string templates were created."

**EVOLUTION:**
Concatenation with `+` -> `String.format()` (Java 5) -> text blocks (Java 15) -> string templates (Java 21 preview, evolving). Note: String templates were previewed in Java 21 but were subsequently withdrawn for redesign, as the template processor API needed refinement.
---

### 📘 Textbook Definition

String templates allow embedding expressions directly in string literals using `\{expression}` syntax. Unlike simple interpolation in other languages, Java's design includes template processors - pluggable components that can validate and transform the template before producing a result, enabling injection-safe SQL, HTML, and JSON composition.
---

### ⏱️ Understand It in 30 Seconds

**One line:**
String templates embed expressions in strings with `\{expr}` and support custom processors for safe SQL/HTML generation.

**One analogy:**

> Simple string interpolation is like a form where you fill in the blanks with a pen - whatever you write goes in verbatim, including malicious content. Template processors are like a form that validates and sanitizes every field before accepting it.

**One insight:**
The template processor concept is what distinguishes Java's approach from every other language. `STR."Hello \{name}"` is simple interpolation. But `SQL."SELECT * FROM users WHERE name = \{name}"` could produce a `PreparedStatement` with proper parameterization - making SQL injection impossible by construction.
---

### 🔩 First Principles Explanation

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

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

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

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

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

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. `STR."...\{expr}..."` embeds expressions in strings (preview feature)
2. Template processors enable injection-safe SQL/HTML generation
3. Feature was previewed in Java 21 but withdrawn for redesign - final API may change

**Interview one-liner:**
"String templates enable expression interpolation with pluggable processors that can produce any type, not just strings, enabling injection-safe SQL and HTML by construction rather than convention."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Java deliberately delayed string interpolation for decades while every other language added it, because the Java team wanted to solve it with template processors - not just simple string interpolation. The goal was to make SQL injection and XSS impossible by construction rather than relying on developers to remember to sanitize. This ambitious design led to the feature being previewed and then withdrawn for further refinement.
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for String Templates. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

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

### 🎯 Interview Deep-Dive

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

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]
