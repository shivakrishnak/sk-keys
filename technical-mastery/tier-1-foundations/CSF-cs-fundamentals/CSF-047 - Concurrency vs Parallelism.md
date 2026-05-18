---
id: CSF-047
title: Concurrency vs Parallelism
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-026
used_by: JCC-001, CSF-048, CSF-031
related: CSF-048, JCC-001, OSY-014
tags: [concurrency, parallelism, threads, virtual-threads, async]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/csf/concurrency-vs-parallelism/
---

⚡ TL;DR - Concurrency: multiple tasks in progress (may
not run simultaneously). Parallelism: multiple tasks
running simultaneously on multiple cores. Rob Pike:
"Concurrency is about dealing with many things; parallelism
is about doing many things." Concurrency is a design;
parallelism is execution.

| #047 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-026 (Imperative Programming) | |
| **Used by:** | JCC-001 (Java Concurrency), CSF-048 (Concurrency Anti-Patterns), CSF-031 (Event-Driven) | |
| **Related:** | CSF-048 (Concurrency Anti-Patterns), OSY-014 (Thread Scheduling) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A single-threaded web server processes one request at a time.
Request A arrives, takes 200ms to process (50ms CPU, 150ms
waiting for database). While waiting for the database,
the server is idle. Request B arrives during that 150ms
wait. It queues. Request B waits 200ms (A's processing)
+ its own processing time. With 100 simultaneous users,
the 100th user waits 100 * 200ms = 20 seconds. Completely
unacceptable.

**THE BREAKING POINT:**

Modern applications are I/O-bound: 80-90% of a request's
time is spent waiting for external systems (databases,
APIs, caches). A purely sequential design wastes the CPU
during every I/O wait. Thousands of simultaneous users
cannot be served by a sequential server. The only solutions:
more processes (expensive, high memory), or concurrency
within a single process.

**THE INVENTION MOMENT:**

Threads (the unit of concurrency in most systems) were
introduced to allow multiple tasks to be "in flight" simultaneously
within a single process, sharing memory. The OS scheduler
interleaves threads on one or more CPUs. Even on a single CPU,
concurrency enables progress: while Thread A waits for
I/O, the CPU switches to Thread B. On multi-core CPUs,
threads ALSO run in parallel (simultaneously on different cores).
The distinction between "concurrent" (multiple in progress)
and "parallel" (multiple at the same instant) becomes
critical when reasoning about correctness and performance.

---

### 📘 Textbook Definition

**Concurrency:** A property of a program or system where
multiple tasks (threads, processes, coroutines) are in progress
at the same time (their lifecycles overlap), though they
may not execute simultaneously. On a single-core CPU,
concurrency is achieved by time-slicing (interleaving).

**Parallelism:** A property of execution where multiple
computations literally run at the same physical instant,
on multiple CPU cores or machines. Parallelism is a SUBSET
of concurrency: parallel execution is concurrent, but
concurrent execution is not necessarily parallel.

**Rob Pike's distinction (Go co-creator):**
"Concurrency is about DEALING WITH many things at once.
Parallelism is about DOING many things at once."
Concurrency is a software design concern (structure);
parallelism is a hardware execution concern (resource).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Concurrency = multiple tasks in progress (structure).
Parallelism = multiple tasks executing simultaneously (execution).
A concurrent program on one CPU is NOT parallel. A single task
on 4 cores is NOT concurrent.

**One analogy:**

> Concurrency: one barista making 3 coffees. They start
> espresso #1, while it pulls they froth milk for #2, while
> steaming they grind beans for #3. Three coffees "in progress"
> simultaneously, but only one action at a time (one pair of hands).
>
> Parallelism: three baristas, each making one coffee
> simultaneously. Three coffees actually progressing at the
> same physical instant.
>
> One barista can be concurrent but not parallel.
> Three baristas ARE parallel (and also concurrent, because
> they can interleave their subtasks).

**One insight:**

Java's `parallelStream()` is parallelism: it uses the
ForkJoinPool to split the work across all available CPU cores
and process sub-tasks simultaneously. A Spring Boot server
handling 200 concurrent requests is concurrency: 200 threads
are in progress, but a 4-core CPU can only run 4 simultaneously
(the OS interleaves the 200 threads across 4 cores).
Using `parallelStream()` inside a request handler adds
parallelism (inner CPU parallelism) within the concurrency
(outer thread concurrency). Confusing the two leads to:
using `parallelStream()` for I/O-bound tasks (wrong: wastes
threads), or using a single thread for CPU-bound tasks
(wrong: leaves cores idle).

---

### 🔩 First Principles Explanation

**SINGLE-CORE vs MULTI-CORE:**

```
┌──────────────────────────────────────────────────────┐
│ SINGLE CORE - CONCURRENT (time-sliced):              │
│                                                      │
│ CPU: [A][A][B][A][B][B][A][C][B][C]...              │
│      Thread A, B, C interleaved by scheduler         │
│      At any instant: only one thread runs            │
│      But all three are "in progress"                 │
│                                                      │
│ MULTI-CORE - PARALLEL (and concurrent):              │
│                                                      │
│ Core 1: [A][A][A][A][A][A]...                       │
│ Core 2: [B][B][B][B][B][B]...                       │
│ Core 3: [C][C][C][C][C][C]...                       │
│         At every instant: 3 threads run simultaneously│
└──────────────────────────────────────────────────────┘
```

**WHEN TO USE EACH:**

```
┌──────────────────────────────────────────────────────┐
│ I/O-BOUND tasks (DB, network, file I/O):             │
│   Most time spent WAITING, not using CPU             │
│   Solution: CONCURRENCY (more threads than cores)    │
│   More threads = more tasks can wait simultaneously  │
│   Example: Tomcat 200 threads for 200 concurrent req │
│   Java 21 Virtual Threads: millions of concurrent    │
│   tasks (each blocked waiting) without high memory   │
│                                                      │
│ CPU-BOUND tasks (computation, encoding, ML):         │
│   Most time spent COMPUTING, not waiting             │
│   Solution: PARALLELISM (one thread per core)        │
│   More cores = more work per second                  │
│   Example: Java ForkJoinPool, parallelStream()       │
│   Adding threads beyond core count: context switching│
│   overhead; no benefit, often worse                  │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE PARALLELISM OVERHEAD TRAP:**

A developer optimizes an HTTP request handler that calls
a single database query (200ms I/O, 5ms CPU for processing
the result). They "optimize" by splitting the processing
into 4 parallel tasks using `parallelStream()`:

Before: 1 thread, 205ms total.
After: 4 threads (ForkJoinPool), 5ms / 4 cores ≈ 1.25ms CPU.
Expected total: 200ms I/O + 1.25ms = 201.25ms.
Actual total: 215ms.

Overhead: ForkJoinPool task splitting + thread synchronization
+ result merging = ~14ms overhead for 3.75ms of savings.

**THE LESSON:**

Parallelism overhead (thread creation, task splitting, synchronization,
result merging) is fixed cost. For small or I/O-heavy tasks,
the overhead exceeds the benefit. Parallelism pays off when:
(1) the parallel portion is CPU-bound AND large enough that
the parallel speedup exceeds the overhead, and (2) there
are free CPU cores available. Amdahl's Law quantifies this:
if 5% of a task is I/O and 95% is CPU, parallelizing the CPU
part across 4 cores gives speedup of 1 / (0.05 + 0.95/4) ≈ 3.27x,
not 4x. The sequential I/O portion limits the speedup.

---

### 🎯 Mental Model / Analogy

**RESTAURANT KITCHEN:**

Concurrency: one chef manages 5 dishes "in progress" simultaneously -
sauce reducing, pasta boiling, meat resting. One chef (one CPU),
many tasks in progress. At any moment, only one task is being
actively worked. But all are progressing.

Parallelism: 5 chefs, each working on one dish simultaneously.
True simultaneous progress across all dishes.

A restaurant with many concurrent orders but one chef is NOT
doing parallel cooking. A restaurant with 5 chefs is doing
both concurrent AND parallel cooking (each chef may also have
multiple dishes in progress).

**MEMORY HOOK:**

"Concurrency = overlapping lifetimes (design).
Parallelism = same instant (execution).
Concurrent + single-core = time-sliced.
Concurrent + multi-core = potentially parallel.
I/O-bound: concurrency (threads blocked waiting).
CPU-bound: parallelism (more cores = more work).
Virtual threads (Java 21): millions concurrent for I/O.
ForkJoinPool: parallel CPU computation."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Concurrency: juggling - 3 balls in the air but only one in
your hands at a time. Parallelism: 3 people each juggling
their own ball at the same time.

**Level 2 - Student:**
`new Thread(() -> task.run()).start()` = concurrency (thread
is in progress). If 4 threads run on 4 cores at the same instant = parallel.
`IntStream.range(0, 1000).parallel().forEach(i -> process(i))` =
parallelism (ForkJoinPool splits 1000 tasks across all cores).

**Level 3 - Professional:**
Spring Boot's Tomcat thread pool (default 200 threads):
concurrent web server. 200 threads can be "in progress"
handling requests. On 4 cores: only 4 threads running at
any instant; 196 are waiting (for I/O, for CPU time).
Adding more threads beyond CPU count helps for I/O-bound
requests (more waiting threads = more concurrent I/O).
Does NOT help for CPU-bound requests (more threads = more
context switching, worse performance).

**Level 4 - Senior Engineer:**
Java 21 Virtual Threads (Project Loom): lightweight threads
that the JVM schedules on a small thread pool (carrier threads,
one per CPU core). Virtual threads park (unblock from carrier)
when blocking on I/O. The carrier thread switches to another
virtual thread. Millions of virtual threads can be "in progress"
concurrently. Cost per virtual thread: ~few KB (vs ~1MB per
platform thread). This decouples the "number of concurrent
tasks" from "number of OS threads." Concurrency scales to
the number of tasks; parallelism is bounded by CPU cores.

**Level 5 - Expert:**
Amdahl's Law: `Speedup = 1 / (S + P/N)` where S = serial
fraction, P = parallel fraction, N = number of cores.
If S = 0.05 (5% serial), P = 0.95, N = 100 cores:
Speedup = 1 / (0.05 + 0.95/100) ≈ 16.8x, not 100x.
The serial fraction is the bottleneck. Gustafson's Law
counters: for larger problems, the parallel portion grows
while serial remains fixed - so parallelism gives better
returns on larger problem sizes (high-performance computing).

---

### ⚙️ How It Works (Formal Basis)

**JAVA THREADING AND VIRTUAL THREADS:**

```
┌──────────────────────────────────────────────────────┐
│ Platform Thread (Java < 21):                         │
│   1:1 with OS thread (~1MB stack)                    │
│   Blocking I/O: OS thread blocked                    │
│   10,000 concurrent requests = 10,000 OS threads     │
│   Memory: 10GB for stacks alone                      │
│                                                      │
│ Virtual Thread (Java 21+):                           │
│   Many:1 mapping to carrier threads (OS threads)     │
│   Blocking I/O: virtual thread parks, carrier frees  │
│   Carrier picks up another virtual thread            │
│   10,000 concurrent requests = few KB each = ~100MB  │
│                                                      │
│ Scheduler:                                           │
│   OS scheduler: preemptive (switches threads based   │
│   on time quanta or priority)                        │
│   Virtual thread scheduler: cooperative (parks on I/O│
│   or explicit park), built on ForkJoinPool           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: parallelStream on I/O-bound Work**

```java
// BAD: parallelStream for I/O-bound operations
List<Order> orders = orderIds.stream()
    .parallel()
    .map(id -> orderRepo.findById(id)) // I/O: each blocks a thread
    .toList();
// ForkJoinPool threads blocked on I/O = other CPU tasks starved
// ForkJoinPool is a SHARED pool; blocking it affects all parallel ops

// GOOD option 1: Virtual threads for concurrent I/O (Java 21)
List<Order> orders;
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    var futures = orderIds.stream()
        .map(id -> executor.submit(() -> orderRepo.findById(id)))
        .toList();
    orders = futures.stream().map(f -> {
        try { return f.get(); }
        catch (Exception e) { throw new RuntimeException(e); }
    }).toList();
}
// Virtual threads: each I/O operation parks (frees carrier thread)
// No carrier thread starvation; scales to millions of concurrent ops

// GOOD option 2: CompletableFuture with dedicated I/O pool
ExecutorService ioPool = Executors.newFixedThreadPool(50);
List<CompletableFuture<Order>> futures = orderIds.stream()
    .map(id -> CompletableFuture.supplyAsync(
        () -> orderRepo.findById(id), ioPool))
    .toList();
List<Order> orders = futures.stream().map(CompletableFuture::join).toList();
ioPool.shutdown();
```

**Example 2 - Correct Use of parallelStream: CPU-Bound Work**

```java
// GOOD: parallelStream for CPU-intensive, I/O-free computation
List<Report> reports = rawData.stream()
    .parallel()  // split across all available cores
    .map(data -> {
        // Pure CPU computation: no I/O, no blocking
        return computeComplexReport(data); // CPU-heavy: encryption, ML, aggregation
    })
    .toList();
// Benefits: available CPU cores used in parallel
// Works because: compute is CPU-bound; no blocking; ForkJoinPool free

// When NOT to use parallelStream:
// - Ordered operations (forEachOrdered is still sequential)
// - Small datasets (overhead > benefit)
// - I/O operations (blocks ForkJoinPool threads)
// - Operations with shared mutable state (race conditions)
```

---

### ⚖️ Comparison Table

| Aspect | Concurrency | Parallelism |
|---|---|---|
| Core question | How to manage multiple tasks in progress? | How to use multiple cores for one problem? |
| CPU requirement | Can be single-core | Requires multiple cores |
| Java mechanism | Threads, virtual threads, async | ForkJoinPool, parallelStream, RecursiveTask |
| Goal | Throughput (more requests) | Speed (faster processing) |
| I/O-bound? | Yes - primary use case | No - wasted waiting on single I/O |
| CPU-bound? | Less effective (one at a time) | Yes - primary use case |
| Java 21 | Virtual threads (millions) | unchanged (ForkJoinPool) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More threads always means faster" | For I/O-bound work: adding threads up to the point of concurrent I/O saturation helps. Adding beyond that: more context switching, more memory, no benefit. For CPU-bound: adding threads beyond the number of CPU cores is harmful (context switch overhead). The optimal thread count depends on the task type and hardware. |
| "`parallelStream()` is always faster than sequential" | `parallelStream()` has overhead: task splitting, ForkJoinPool submission, result merging. For small datasets or I/O-bound operations, this overhead exceeds the benefit. Rule: `parallelStream()` is appropriate for CPU-bound, stateless operations on large datasets. For I/O: use async/reactive. For small datasets: stay sequential. |
| "Virtual threads replace parallelism" | Virtual threads solve CONCURRENCY at scale (millions of I/O-waiting tasks without OS thread overhead). They do NOT speed up CPU-bound computation. For a task that is 100% CPU computation, a virtual thread runs on one carrier thread (one CPU core). You need actual parallel decomposition (ForkJoinPool, parallelStream) to use multiple cores for CPU-bound work. |
| "Concurrency always introduces race conditions" | Race conditions occur when concurrent tasks share MUTABLE state and at least one is writing. Concurrent tasks with no shared mutable state (share-nothing or share-immutable) have no race conditions. Functional programming, immutable data, message passing, and actor models are concurrency designs that avoid race conditions structurally. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Thread Starvation (ForkJoinPool Blocking)**

**Symptom:** System-wide slowdown when certain operations
are triggered. `parallelStream()` operations become slow.
Async operations queue up without executing.

**Root Cause:** Blocking I/O inside `parallelStream()` or
`CompletableFuture.runAsync()` blocks ForkJoinPool threads.
The shared common ForkJoinPool has `Runtime.getRuntime().availableProcessors()`
threads. If all are blocked on I/O, CPU-bound parallel tasks
queue. Even OTHER `parallelStream()` calls in the application
slow down (shared pool).

**Diagnosis:**
```bash
# Thread dump to see ForkJoinPool thread states
jcmd <pid> Thread.print | grep -A 5 "ForkJoinPool"
# If all ForkJoinPool threads show "WAITING" or "TIMED_WAITING"
# with I/O stack frames -> thread starvation confirmed
```

**Fix:** Use a dedicated thread pool for I/O-bound async work.
Never block ForkJoinPool threads. Use virtual threads (Java 21)
for I/O-bound concurrent work.

---

**Security Note:**

Concurrency bugs (race conditions, time-of-check/time-of-use)
are security vulnerabilities. Classic example: authentication
check followed by privileged operation:
```java
if (user.isAuthorized("ADMIN")) {
    // Time gap here
    adminOperation(); // is user still authorized?
}
```
In a concurrent system, the user's authorization may be
revoked between the check and the operation (TOCTOU race).
The fix: make the check and the operation atomic (hold
a lock, or use a single transactional operation). Similarly,
race conditions in financial transaction processing (multiple
concurrent requests to withdraw from the same account)
can cause funds to be withdrawn beyond the balance.
Concurrency correctness is a security property for any
system handling authentication, authorization, or financial
operations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - threads operate on shared object state;
  object model required
- `Imperative Programming` (CSF-026) - threads are the imperative
  model for concurrency

**Builds On This (learn these next):**
- `Java Concurrency` (JCC-001) - Java-specific thread,
  synchronized, Lock, concurrent collections API
- `Concurrency Anti-Patterns` (CSF-048) - race conditions,
  deadlocks, and shared state bugs

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ CONCURRENCY  │ Multiple tasks in progress              │
│              │ May be time-sliced on one core          │
│              │ For I/O-bound: more threads = more wait │
├──────────────┼─────────────────────────────────────────┤
│ PARALLELISM  │ Multiple tasks at same instant          │
│              │ Requires multiple CPU cores             │
│              │ For CPU-bound: more cores = more speed  │
├──────────────┼─────────────────────────────────────────┤
│ I/O-BOUND    │ Use concurrency: threads, virtual threads│
│              │ Java 21: newVirtualThreadPerTaskExecutor │
├──────────────┼─────────────────────────────────────────┤
│ CPU-BOUND    │ Use parallelism: ForkJoinPool           │
│              │ stream().parallel() for large datasets  │
├──────────────┼─────────────────────────────────────────┤
│ VIRTUAL THR  │ Java 21. Millions concurrent. Few KB.   │
│              │ Parks on blocking I/O (carrier freed)   │
│              │ Does NOT add parallelism to CPU work    │
├──────────────┼─────────────────────────────────────────┤
│ AMDAHL LAW   │ Speedup limited by serial fraction      │
│              │ 5% serial = max ~20x from any N cores   │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ JCC-001 (Java Concurrency), CSF-048     │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Concurrency is DESIGN (multiple tasks in progress, possibly
   interleaved). Parallelism is EXECUTION (multiple tasks at
   the same physical instant on multiple cores). A concurrent
   single-core program is NOT parallel. Correct the common
   interview claim: "I made my code concurrent/parallel"
   without understanding which.
2. Match the model to the task: I/O-bound (waiting for DB/network/disk)
   benefits from concurrency (more threads waiting = more
   parallel I/O). CPU-bound (pure computation) benefits from
   parallelism (more cores = more compute per second). Using
   `parallelStream()` on I/O-bound work starves the ForkJoinPool.
   Using a single thread for CPU-bound work leaves cores idle.
3. Java 21 virtual threads enable millions of concurrent
   I/O-bound tasks without OS thread overhead. Each virtual
   thread parks (releases its carrier thread) when blocking.
   This scales concurrency far beyond the 200-thread Tomcat
   default while using less memory. Virtual threads do NOT
   add parallelism - they add CONCURRENCY for I/O-bound workloads.

**Interview one-liner:**
"Concurrency is multiple tasks in progress at overlapping times
(design); parallelism is multiple tasks executing simultaneously
on multiple cores (execution). I/O-bound workloads benefit
from concurrency (more threads = more waiting tasks = more
throughput). CPU-bound workloads benefit from parallelism
(more cores = more computation). Java 21 virtual threads scale
I/O-bound concurrency to millions; ForkJoinPool/parallelStream
handle CPU parallelism."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The concurrency/parallelism distinction is an instance of
the "design vs execution" principle: what the software IS
STRUCTURED to do (concurrent: multiple tasks in progress)
vs what the hardware DOES (parallel: multiple tasks at once).
This separation appears everywhere: a microservice DESIGN
can handle 1,000 concurrent requests, but the hardware
can only execute as many in parallel as there are cores.
A Kafka consumer design is concurrent (multiple consumers
in a group), but only as many partitions as there are
consumer instances execute in parallel. A database transaction
design is concurrent (many transactions in progress), but
the database executes as many as its lock contention allows
in parallel. In every case: design for concurrency, size
hardware for the required parallelism.

**Where else this pattern appears:**

- **Go goroutines and the Go scheduler** - Go's goroutines
  are like Java's virtual threads: lightweight concurrent tasks
  (few KB each). The Go scheduler multiplexes goroutines
  onto OS threads (GOMAXPROCS, default = number of CPU cores).
  `go myFunc()` is concurrency: the goroutine is in progress
  concurrently. If GOMAXPROCS=4, up to 4 goroutines run in
  parallel. Go's CSP (Communicating Sequential Processes) model
  emphasizes: share data by communicating (channels), not
  communicate by sharing data. This is the anti-race-condition design.
- **Node.js event loop** - Node.js is single-threaded with
  an event loop: one OS thread, many tasks "in progress."
  This is concurrency without OS-level parallelism. I/O operations
  are handed to the OS (async I/O); when they complete, the
  callback is queued to the event loop. CPU-bound tasks block
  the event loop (prevent other tasks from progressing) -
  a fundamental limitation. Worker threads (Node 12+) add
  parallelism for CPU-bound work. The design: single-thread
  concurrency for I/O; multi-thread parallelism for CPU.
- **Kubernetes pod scaling** - Horizontal Pod Autoscaler
  adds pod instances (parallelism at the service level):
  more pods = more requests processed simultaneously.
  Within each pod, the application handles concurrent requests
  via its own threading model. HPA is parallelism at the
  deployment level; the thread pool inside each pod is
  concurrency at the process level. Scaling for concurrency
  vs parallelism at the infra level.

---

### 💡 The Surprising Truth

The Go programming language was designed to make concurrency
easy - channels and goroutines are first-class features.
Go's creator, Rob Pike, gave a famous talk ("Concurrency
is not Parallelism", 2012) specifically to correct the
widespread conflation of the two terms. The talk's key
demo: a text "gopher" digests books by separating:
fetching books (I/O), analyzing pages (CPU), archiving results (I/O).
Each stage is a separate goroutine. The stages run concurrently.
On a multi-core machine, they run in parallel. But the
CONCURRENT DESIGN works correctly even on a single core -
because concurrency is about structure, not execution.
The talk is famous for the quote "Concurrency is about
DEALING WITH many things at once. Parallelism is about
DOING many things at once" - Rob Pike, 2012. This distinction
has been clarified in CS textbooks but not consistently
in industry. The interview question "what's the difference
between concurrency and parallelism?" still catches many
experienced developers who have spent years writing concurrent
code without clarifying the terms.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** Review a Spring Boot service that uses
   `parallelStream()` to call external REST APIs in parallel.
   Explain why this is incorrect. Refactor to use virtual
   threads (Java 21) or `CompletableFuture` with a dedicated
   I/O thread pool.

2. **[EXPLAIN]** Given a 4-core machine, a 10-thread Tomcat
   thread pool, and 100 simultaneous HTTP requests each
   waiting 200ms for a database: how many requests are
   CONCURRENT? How many are PARALLEL? What is the effective
   throughput (requests/second)?

3. **[APPLY]** Use `Executors.newVirtualThreadPerTaskExecutor()`
   to make 1,000 parallel HTTP calls to an external service
   and collect results. Explain why virtual threads are
   appropriate here vs `parallelStream()`.

4. **[CALCULATE]** A program has a serial section (setup,
   final aggregation) that takes 10ms and a parallel section
   (processing) that takes 90ms on 1 core. Apply Amdahl's
   Law to compute the speedup with 8 cores. What is the
   theoretical maximum speedup with infinite cores?

5. **[DESIGN]** Design the threading model for an image
   processing pipeline: (1) download images from S3 (I/O-bound),
   (2) resize each image (CPU-bound), (3) upload to CDN (I/O-bound).
   Specify: which executor for each stage, why, and how
   to compose the stages.

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot application migrates from Tomcat
(platform threads) to using virtual threads via
`spring.threads.virtual.enabled=true` (Spring Boot 3.2+).
Before migration: 200 platform threads, each ~1MB stack = ~200MB.
After migration: potentially thousands of virtual threads.
Does this reduce or increase memory usage? Does it add parallelism?

*Hint: Virtual thread memory usage: each virtual thread uses
a few KB for its stack (vs ~1MB for platform threads). If
10,000 requests arrive concurrently, 10,000 virtual threads
are created. Memory: 10,000 * ~10KB = ~100MB vs 10,000 * 1MB
= 10GB for platform threads. Virtual threads REDUCE memory
dramatically for high concurrency. Does it add parallelism?
NO. Virtual threads still run on carrier threads (one per
CPU core). On 4 cores, up to 4 virtual threads execute
simultaneously. The rest are parked (waiting for I/O).
Virtual threads add CONCURRENCY (more tasks in progress)
not PARALLELISM (more tasks at once).*

**Q2.** Amdahl's Law states that serial sections limit
speedup from parallelism. In practice, what are some
sources of "serial sections" in a web application that
make it impossible to achieve linear speedup from adding
more CPUs or threads?

*Hint: Hidden serial sections:
(1) Lock contention: any code protected by a synchronized
lock or database row lock runs one thread at a time.
All other threads wait. This is a serial section even
if the lock is held briefly.
(2) Connection pool: if all threads need database connections
and the pool size is less than the number of threads,
threads queue for connections (serial wait).
(3) Single-partition Kafka topic: only one consumer can
process one partition at a time. If all messages go to
one partition, parallel consumers make no difference.
(4) Global sequence generator: if every request increments
a global counter (for order IDs), that increment is a
serial operation. 1,000 TPS = 1,000 serialized counter increments.
(5) Single database writer: if all concurrent requests
write to the same database table and the database serializes
writes, the write throughput is bounded by the database,
not the application thread count.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between concurrency and parallelism?
Give a Java example of each."**

*Why they ask:* Classic CS fundamentals question. Frequently
asked and frequently confused.

*Strong answer includes:*
- Concurrency: multiple tasks in progress, possibly interleaved.
  Java example: Spring Boot's Tomcat thread pool.
  200 threads can be "in progress" handling requests.
  On 4 cores, only 4 run at any instant (others wait for
  I/O or CPU time). The system is concurrent but not fully parallel.
- Parallelism: multiple tasks at same physical instant.
  Java example: `list.parallelStream().map(this::compute).toList()`.
  ForkJoinPool splits the list across all CPU cores.
  4 cores: 4 tasks process simultaneously.
- Key insight: use concurrency for I/O-bound (more threads
  = more waiting); use parallelism for CPU-bound (more cores
  = more computing).

**Q2: "When should you NOT use `parallelStream()`?"**

*Why they ask:* Tests knowledge of when parallelism hurts.
Common mistake in Java applications.

*Strong answer includes:*
- I/O-bound operations: `parallelStream()` maps tasks to
  ForkJoinPool threads. If tasks block on I/O, ForkJoinPool
  threads are stuck waiting. The shared common pool has
  `availableProcessors()` threads. If all block, parallel
  operations in other parts of the application slow down.
  Use virtual threads or CompletableFuture with a dedicated
  I/O pool instead.
- Small datasets: parallelism overhead (task splitting,
  thread synchronization, result merging) exceeds benefit
  for small N. Rule of thumb: parallel benefit for N > ~10,000
  with non-trivial computation. Profile, don't guess.
- Operations with shared mutable state: race conditions.
  Use `Collectors.toConcurrentMap()` or reduce without side effects.
- Ordered operations where order matters: `forEachOrdered`
  is still sequential; `findFirst()` is complex on parallel streams.

**Q3: "What are Java 21 virtual threads and how do they change
the concurrency model?"**

*Why they ask:* Tests modern Java knowledge. Virtual threads
are the biggest change to Java concurrency in a decade.

*Strong answer includes:*
- Virtual threads: lightweight threads managed by the JVM
  (not 1:1 with OS threads). Carried by a small pool of
  platform threads (carrier threads, one per CPU core).
- Key behavior: when a virtual thread blocks on I/O
  (`Thread.sleep`, JDBC, HTTP), the virtual thread PARKS -
  the carrier thread is released and picks up another
  virtual thread. No OS thread is blocked.
- Scale: millions of virtual threads vs ~1,000 platform threads
  (memory and OS limits). Stack: ~few KB vs ~1MB per thread.
- Usage: `Executors.newVirtualThreadPerTaskExecutor()`,
  or Spring Boot 3.2+ `spring.threads.virtual.enabled=true`.
- What they DO NOT change: parallelism. CPU-bound tasks still
  need ForkJoinPool. Synchronized blocks on platform
  thread monitors may still cause "pinning" (virtual thread
  cannot park while holding a native monitor on some JVM versions).
  Test with `-Djdk.tracePinnedThreads=full` to find pinning.
