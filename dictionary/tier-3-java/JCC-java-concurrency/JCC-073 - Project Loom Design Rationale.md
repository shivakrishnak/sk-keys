---
id: JCC-073
title: Project Loom Design Rationale
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-032, JCC-033, JCC-034
used_by:
related: JCC-044, JCC-066, JCC-062
tags:
  - java
  - concurrency
  - jvm
  - advanced
  - deep-dive
status: complete
version: 1
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 73
permalink: /java-concurrency/project-loom-design-rationale/
---

# JCC-073 - PROJECT LOOM DESIGN RATIONALE

⚡ **TL;DR** - Project Loom adds virtual threads to Java so that
blocking-style code scales like async code - without callbacks,
reactive frameworks, or developer complexity.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-032 Virtual Threads (Project Loom), JCC-033 Carrier Thread, JCC-034 Continuation |
| Used by    | (design rationale - foundational understanding)    |
| Related    | JCC-044 Structured Concurrency, JCC-066 Thread Pinning, JCC-062 Thread Interruption |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Java's thread-per-request model works at moderate scale (hundreds
of concurrent requests) but fails at the thousands-to-millions
scale required by modern cloud services. Each platform thread
consumes ~1MB of memory and requires an OS context switch on every
blocking I/O call. With 10,000 concurrent requests, 10GB of stack
space is consumed before a line of business logic runs.

**THE BREAKING POINT:**
To scale beyond ~10,000 concurrent requests without virtual threads,
Java developers must adopt reactive programming: `CompletableFuture`
chains, Project Reactor `Mono/Flux`, or RxJava. These frameworks
deliver the I/O scalability of async I/O but at enormous cognitive
cost: callback hell, non-linear code execution, split stack traces,
and complex error handling. Senior engineers spend months debugging
reactive pipelines that would be trivial in sequential code.

**THE INVENTION MOMENT:**
Ron Pressler and Alan Bateman (Oracle) led Project Loom from 2017.
The core insight (from concurrent research going back to Green
Threads and Erlang): use *continuations* to suspend and resume
Java threads in userspace without OS involvement. The operating
system never sees 10,000 threads - it sees only the small carrier
pool. The JVM manages the rest.

**EVOLUTION:**
- **2017:** Project Loom started (JEP 353, 354, 425...)
- **Java 19-20:** Virtual threads as Preview
- **Java 21 LTS:** Virtual threads GA (JEP 444)
- **Java 21:** Structured Concurrency preview (JEP 453)
- **Java 24+:** JEP 491 - synchronized without pinning (planned)

---

### 📘 Textbook Definition

**Project Loom** is the OpenJDK project that delivered virtual
threads (JEP 444, Java 21) and structured concurrency (JEP 453).

**Design goals:**
1. Enable thread-per-request at scale (millions of threads)
2. Keep sequential, blocking-style code as the programming model
3. Minimal change to existing Java APIs
4. Backward compatibility with existing `java.lang.Thread` code

**Key components:**
- **Virtual threads:** JVM-managed threads that unmount from carrier
  threads during blocking I/O
- **Continuations:** Resumable computation units (stackful continuations)
- **Structured Concurrency:** Task-tree lifecycle management
- **Scoped Values:** Thread-local replacement for virtual threads

---

### ⏱️ Understand It in 30 Seconds

**One line:** Virtual threads let you write blocking code that scales
like non-blocking code - no callbacks, no reactive frameworks, no
fundamental change to how you think about concurrency.

**One analogy:**
> Before Loom: a restaurant with only 100 waiters. If 1,000
> customers arrive, 900 wait outside (thread starvation).
> After Loom: 1,000 "ghost waiters" - each handles one customer.
> When a ghost waiter must go to the kitchen (I/O block), it
> becomes invisible, freeing a real waiter (carrier thread) for
> another ghost. The kitchen never sees 1,000 waiters at once.

**One insight:** Virtual threads do not make I/O faster. They
remove the *one-thread-per-request* throughput ceiling by making
blocked threads free.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A virtual thread is a Java object (a `Thread` subclass) with
   a heap-allocated stack (continuation). It is NOT an OS thread.
2. A virtual thread mounts onto a carrier thread to execute, and
   unmounts when it would block.
3. The JVM scheduler (a `ForkJoinPool`) schedules virtual threads
   onto carrier threads.
4. JVM-level blocking operations (`LockSupport.park`, `socket.read`,
   `sleep`) unmount the virtual thread; the carrier is immediately
   available for another virtual thread.
5. `synchronized` and native methods PIN the virtual thread to its
   carrier (see JCC-066 Thread Pinning).

**DERIVED DESIGN:**
Virtual threads reuse the existing `java.lang.Thread` API completely.
`Thread.start()`, `Thread.join()`, `Thread.sleep()`, `ExecutorService`,
and all blocking APIs work unchanged. The only new API is the factory:
`Thread.ofVirtual().start(runnable)`.

**THE TRADE-OFFS:**

**Gain:** Thread-per-request model scales to millions; no reactive
complexity; existing blocking code works unchanged; full stack
traces; familiar sequential reasoning.

**Cost:** Pinning from `synchronized`; not faster than async for
CPU-bound work; thread-locals have higher memory cost at VT scale;
debugging tools needed updates for VT support.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Multiplexing millions of concurrent tasks onto a
small OS thread pool requires yield/resume (continuation) semantics.
This is irreducible.

**Accidental:** The pinning limitation from `synchronized` is an
accidental implementation constraint, being addressed by JEP 491.

---

### 🧪 Thought Experiment

**SETUP:** 10,000 concurrent HTTP requests, each making one
database query (5ms each). Server has 8 cores.

**WITH platform threads (Tomcat default: ~200 thread pool):**
```
Max concurrent: 200 requests
Remaining 9,800: queue, increasing latency
Active threads: 200 (each blocked 5ms on DB)
Throughput: 200 / 0.005s = 40,000 req/s (theoretical)
Reality: context switch overhead reduces to ~20,000 req/s
```

**WITH virtual threads (thread-per-request):**
```
10,000 virtual threads created (one per request)
Each blocks on DB query:
  -> virtual thread unmounts from carrier
  -> carrier takes next runnable VT
8 carriers serve all 10,000 VTs during their active (non-blocked) time
DB query time: 5ms, but carrier is FREE during those 5ms
Throughput: 10,000 concurrent / 0.005s = 2,000,000 req/s potential
DB connection pool is now the bottleneck, not thread count
```

**THE INSIGHT:** Virtual threads shift the bottleneck from
"thread count" to "actual resource limits" (DB connections, CPU).
The programming model stays identical.

---

### 🧠 Mental Model / Analogy

> Virtual threads are like coroutines: lightweight cooperative
> tasks that yield control to others when waiting, but look
> exactly like regular OS threads from the programmer's perspective.
> The JVM (not the OS) decides when to yield and when to resume -
> completely transparent to application code.

**Element mapping:**
- Coroutine = virtual thread
- Cooperative yield = unmount during blocking call
- Scheduler = ForkJoinPool managing carrier threads
- OS threads = carrier threads (8 of them, for 8 cores)
- Coroutine stack = heap-allocated continuation
- Coroutine resume = virtual thread mounting on available carrier

Where this analogy breaks down: Go goroutines are always
"virtual" (the Go runtime manages all scheduling). Java has both
platform threads (OS-managed) and virtual threads (JVM-managed) -
you choose per use case.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Virtual threads make Java able to handle millions of simultaneous
operations without needing millions of actual OS threads - each
operation "borrows" a real thread only when actively computing,
releasing it when waiting.

**Level 2 - How to use it (junior developer):**
```java
// Create virtual thread - single task
Thread vt = Thread.ofVirtual()
    .name("my-vt")
    .start(() -> handleRequest(request));

// Virtual thread executor (thread-per-task)
try (ExecutorService exec =
        Executors.newVirtualThreadPerTaskExecutor()) {
    for (Request req : requests) {
        exec.submit(() -> handleRequest(req));
    }
} // auto-shutdown, waits for all tasks
```

**Level 3 - How it works (mid-level engineer):**
Each virtual thread has a heap-allocated `Continuation` object
storing its Java stack frames. When the VT blocks (calls `park()`,
`sleep()`, any blocking I/O), the JVM serialises the continuation
to the heap and parks without blocking the carrier. When the unpark
signal arrives (I/O complete, timeout expired), the VT is submitted
to the ForkJoinPool. A carrier thread picks it up, deserialises
the continuation (mounts), and execution resumes from exactly where
it left off.

**Level 4 - Why it was designed this way (senior/staff):**
The key design decision: make virtual threads look exactly like
platform threads to application code. Alternative: coroutines /
`async/await` (C#, Python, Kotlin coroutines). The Loom team
rejected this because `async/await` creates the "function colouring"
problem - every function in a call chain must be marked `async`,
making it impossible to compose async and sync code freely. Java's
approach (virtual threads as transparent threads) avoids this. The
cost: continuation implementation complexity inside the JVM vs
surface-level language change.

**Expert Thinking Cues:**
- `Executors.newVirtualThreadPerTaskExecutor()` is the recommended
  replacement for `newCachedThreadPool()` for I/O-bound workloads.
- Virtual threads are NOT faster for CPU-bound work. CPU-bound tasks
  should use platform thread pools sized to core count.
- Thread-local variables work but cost more memory at VT scale.
  Prefer `ScopedValue` (Java 21 preview) for VT-friendly context.
- Spring Boot 3.2+ configures virtual threads automatically via
  `spring.threads.virtual.enabled=true`.

---

### ⚙️ How It Works (Mechanism)

**Virtual thread state machine:**
```
NEW -(start())-> RUNNABLE
  |
  |--(needs carrier)-> MOUNTED (executing on carrier)
  |
  |--(blocks: park/IO)-> UNMOUNTED (continuation on heap)
  |                      carrier freed for another VT
  |
  |--(unpark signal)-> RUNNABLE (submitted to scheduler)
  |
  |--(run() returns)-> TERMINATED
```

**Stack frame serialization (simplified):**
```
VT executing:
  UserController.handleRequest()   <- top of stack
    UserService.getUser()
      UserRepository.findById()    <- about to call JDBC read()
        ... BLOCKING CALL ...

VT blocks: JVM captures stack frames:
  [frame: findById, args, locals]
  [frame: getUser, args, locals]
  [frame: handleRequest, args, locals]
  -> stored in Continuation heap object

Carrier thread: free to execute another VT
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
HTTP request arrives -> VT created    <- YOU ARE HERE
       |
  VT mounts on carrier C1
       |
  UserService.getUser() runs
       |
  JDBC query: socket.read() -> VT unmounts
  Carrier C1 immediately mounts next VT
       |
  DB response arrives
       |
  VT resubmitted to scheduler
       |
  Carrier C2 (may be different) mounts VT
       |
  Result returned, response sent
  VT terminates
```

**FAILURE PATH - carrier exhaustion from pinning:**
```
VT enters synchronized block
  -> VT PINNED to carrier (cannot unmount)
  -> carrier occupied during entire JDBC call (5ms)
  -> 8 carriers, all pinned = only 8 concurrent requests
  -> same as platform thread limitation
```

**WHAT CHANGES AT SCALE:**
- At 100k concurrent requests, JVM creates 100k `Thread` + `Continuation`
  objects (~2-4KB each = ~200-400MB). Heap must accommodate.
- GC pressure from frequent VT lifecycle. Z GC or G1 recommended.

---

### 💻 Code Example

**BAD - reactive complexity for I/O scale (before Loom):**
```java
// BAD: Reactive code to handle concurrent I/O
// Complex, non-linear, hard to debug
public Mono<Response> getUser(long id) {
    return userRepository.findById(id)   // returns Mono
        .flatMap(user ->
            orderRepository.findByUser(user.id())
                .collectList()
                .map(orders ->
                    new Response(user, orders)))
        .onErrorResume(e ->
            Mono.just(Response.fallback()));
}
```

**GOOD - blocking style with virtual threads (same scalability):**
```java
// GOOD: Sequential, readable, same I/O scalability as reactive
public Response getUser(long id) {       // regular blocking method
    try {
        User user = userRepository.findById(id);   // blocks VT
        List<Order> orders =
            orderRepository.findByUser(user.id()); // blocks VT
        return new Response(user, orders);
    } catch (Exception e) {
        return Response.fallback();
    }
}

// Spring Boot 3.2+: enable globally
// spring.threads.virtual.enabled=true
```

**GOOD - explicit virtual thread executor:**
```java
// For non-Spring code: replace fixed thread pool
// BEFORE:
ExecutorService exec = Executors.newFixedThreadPool(200);

// AFTER:
ExecutorService exec =
    Executors.newVirtualThreadPerTaskExecutor();

// Submit tasks identically - no other code changes
List<Future<Result>> futures = tasks.stream()
    .map(task -> exec.submit(() -> process(task)))
    .toList();
```

**How to verify:**
```java
@Test
void virtualThreadsHandleHighConcurrency() throws Exception {
    int taskCount = 10_000;
    CountDownLatch latch = new CountDownLatch(taskCount);

    try (ExecutorService exec =
            Executors.newVirtualThreadPerTaskExecutor()) {
        for (int i = 0; i < taskCount; i++) {
            exec.submit(() -> {
                Thread.sleep(10); // simulate I/O
                latch.countDown();
            });
        }
        assertThat(latch.await(5, TimeUnit.SECONDS))
            .as("All %d tasks should complete in 5s", taskCount)
            .isTrue();
    }
    // 10,000 tasks * 10ms I/O = 100s on 1 platform thread
    // = 1.25s on 8 virtual thread carriers
}
```

---

### ⚖️ Comparison Table

| Approach | Scale | Code Style | Debugging | Adoption |
|---------|-------|-----------|-----------|---------|
| Platform threads | ~1,000 | Simple blocking | Easy | Universal |
| Virtual threads (Loom) | ~1,000,000 | Simple blocking | Good (JDK 21+) | Growing |
| CompletableFuture | ~100,000 | Functional chains | Medium | Widespread |
| Project Reactor (Flux) | ~1,000,000 | Reactive chain | Hard | Spring WebFlux |
| Kotlin coroutines | ~1,000,000 | suspend functions | Good | Kotlin codebases |
| Go goroutines | ~1,000,000 | Simple blocking | Good | Go codebases |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Virtual threads make I/O faster" | Virtual threads do not reduce I/O latency. They allow MORE requests to be in-flight simultaneously without blocking carrier threads. Throughput improves, latency per request does not. |
| "Virtual threads replace async/reactive everywhere" | For CPU-bound work, platform threads are correct. For streaming, backpressure, or reactive pipelines, Reactor/RxJava still have advantages. Loom targets I/O-bound thread-per-request workloads. |
| "All synchronized code auto-migrates to virtual threads" | `synchronized` blocks cause pinning. Libraries must replace `synchronized` with `ReentrantLock` in blocking paths. Until JEP 491 lands, pinning is a real migration concern. |
| "Virtual threads are free to create - create millions" | Virtual threads have ~1-4KB overhead each (continuation). Creating 10 million VTs uses 10-40GB of heap. Match creation rate to actual concurrency needs. |
| "Thread.start() creates a virtual thread in Java 21+" | `Thread.start()` still creates a platform thread. Use `Thread.ofVirtual().start()` or `Executors.newVirtualThreadPerTaskExecutor()`. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: No throughput improvement after virtual thread migration**

**Symptom:** Throughput identical before/after enabling virtual threads.

**Root Cause:** Library code uses `synchronized` in blocking paths,
causing pinning. See JCC-066.

**Diagnostic:**
```bash
java -Djdk.tracePinnedThreads=full -jar app.jar
# Outputs stack trace of pinned VTs during blocking ops
```

**Fix:** Upgrade JDBC/ORM drivers. Enable JEP 491 when released.
Replace framework `synchronized` with `ReentrantLock` in hot paths.

---

**Failure Mode 2: OutOfMemoryError at high concurrency**

**Symptom:** OOM at 100k concurrent requests despite virtual threads.

**Root Cause:** Each VT has continuation stack (~2-4KB). 100k VTs =
200-400MB minimum. Application heap insufficient.

**Fix:**
```bash
# Increase heap:
java -Xmx4g -jar app.jar
# Or: limit concurrent virtual threads with a semaphore:
Semaphore limit = new Semaphore(50_000);
exec.submit(() -> {
    limit.acquire();
    try { handleRequest(); }
    finally { limit.release(); }
});
```

---

**Failure Mode 3: ThreadLocal memory bloat at VT scale**

**Symptom:** Heap grows linearly with active virtual thread count
due to `ThreadLocal` values.

**Root Cause:** `ThreadLocal<HeavyObject>` creates one `HeavyObject`
per virtual thread. At 50k VTs = 50k heavy objects.

**Fix:** Replace `ThreadLocal` with `ScopedValue` (Java 21 preview)
which is a read-only, scope-bound value with zero per-VT overhead
once the scope exits.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-032 - Virtual Threads (Project Loom)]] - the feature itself
- [[JCC-033 - Carrier Thread]] - the OS thread VTs mount on
- [[JCC-034 - Continuation]] - the mechanism enabling unmounting

**Builds On This (learn these next):**
- [[JCC-044 - Structured Concurrency]] - task-tree lifecycle for VTs
- [[JCC-066 - Thread Pinning (Virtual Threads Problem)]] - the main
  migration concern

**Alternatives / Comparisons:**
- [[JCC-059 - CompletableFuture Composition Patterns]] - non-blocking
  alternative without virtual threads
- Kotlin coroutines - language-level virtual thread equivalent

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | JVM-managed threads that unmount   |
|              | during I/O, scaling to millions    |
+--------------+------------------------------------+
| PROBLEM      | Platform threads: 1MB each, OS     |
|              | limit; reactive: developer burden  |
+--------------+------------------------------------+
| KEY INSIGHT  | Blocking code CAN scale like async |
|              | if blocked threads cost nothing    |
+--------------+------------------------------------+
| USE WHEN     | I/O-bound, thread-per-request,     |
|              | migrating from fixed thread pools  |
+--------------+------------------------------------+
| AVOID WHEN   | CPU-bound (use platform pool),     |
|              | streaming/backpressure (use Reactor)|
+--------------+------------------------------------+
| TRADE-OFF    | Simple code, huge scale / pinning  |
|              | from synchronized; heap overhead   |
+--------------+------------------------------------+
| ONE-LINER    | Executors                          |
|              |   .newVirtualThreadPerTaskExecutor()|
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-044 Structured Concurrency,    |
|              | JCC-066 Thread Pinning             |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Virtual threads make blocking code scalable by unmounting from
   carriers during I/O - no callbacks, no reactive framework needed.
2. `synchronized` causes pinning - replace with `ReentrantLock` in
   blocking paths for full virtual thread benefit.
3. Virtual threads are for I/O-bound work; CPU-bound work still
   needs fixed-size platform thread pools.

**Interview one-liner:** "Project Loom's virtual threads (Java 21)
solve the thread-per-request scalability ceiling: each VT unmounts
from its carrier during blocking I/O, freeing the carrier for
other VTs, enabling millions of concurrent requests with blocking-
style code and no reactive complexity."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The right abstraction removes
accidental complexity without hiding essential complexity. Virtual
threads hide OS thread management (accidental) while keeping
sequential execution semantics (essential) - the programmer still
reasons about one task at a time.

**Where else this pattern appears:**
- **Erlang/Elixir processes:** Erlang's BEAM VM runs millions of
  lightweight processes that block freely on message receive. The
  scheduler multiplexes them onto OS threads. This is project Loom's
  exact architecture - Java learned from 30 years of Erlang.
- **Go goroutines:** Same concept - goroutines are JVM-managed
  (Go runtime-managed) lightweight threads. `go func()` is
  `Thread.ofVirtual().start(func)` in Java 21.
- **Nginx worker model:** Nginx uses async I/O with a small worker
  pool. Project Loom achieves the same throughput model while
  allowing blocking-style request handler code instead of Nginx's
  async callback C code.

---

### 💡 The Surprising Truth

Project Loom was nearly abandoned in 2019 when the team discovered
that implementing continuations in the JVM required changing the
interpreter, JIT compiler, garbage collector, and debugger
simultaneously - all of which had assumed for 25 years that a Java
stack was bound to an OS thread. The stackful continuation required
the JVM to treat stacks as heap objects while maintaining all
existing guarantees about garbage collection, debugging, and
profiling. The engineering effort was so complex that it took 7
years from project start to Java 21 GA. Ron Pressler later noted
that implementing virtual threads correctly required understanding
and modifying more JVM internals than any other OpenJDK feature in
the JDK's history.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** A Spring Boot service switches
to virtual threads for all request handling. It uses HikariCP with
`maximumPoolSize=10`. Under 10,000 concurrent virtual thread requests
each requiring a DB query, what is the actual concurrency limit and
why? How would increasing `maximumPoolSize` to 1,000 affect both
throughput and database health?

*Hint:* The bottleneck shifts from thread count to connection pool
size. Virtual threads wait for a connection from the pool (blocking
on semaphore). Investigate what happens to DB when 1,000 connections
are held open simultaneously.

---

**Question 2 (Design Trade-off):** Spring WebFlux uses Project
Reactor (non-blocking) while Spring MVC uses platform/virtual
threads (blocking). After Java 21, when should you choose WebFlux
over Spring MVC + virtual threads? Name three scenarios where
WebFlux still wins.

*Hint:* Research backpressure (VTs don't support it), streaming
responses over HTTP/2 server-sent events, and reactive data sources
(R2DBC, reactive MongoDB) where the non-blocking pipeline is end-
to-end vs breaking it at the VT boundary.

---

**Question 3 (Root Cause):** A Java 21 service creates 100,000
virtual threads, each running for 200ms (mixed I/O and CPU). After
10 minutes, the JVM throws `OutOfMemoryError: GC overhead limit
exceeded`. Thread count is holding steady. What is causing the GC
pressure, and what would you change in the VT lifecycle design?

*Hint:* Each VT's continuation stack is a heap object. GC must
handle live VT stacks as roots. Under sustained VT load with
short-lived objects on VT stacks, GC frequency and pressure scale
with active VT count. Investigate G1 vs ZGC for VT-heavy workloads
and the effect of `Xss` stack size on VT continuation footprint.

