---
layout: default
title: "Concurrency vs Parallelism"
parent: "CS Fundamentals — Paradigms"
nav_order: 14
permalink: /cs-fundamentals/concurrency-vs-parallelism/
number: "0014"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Operating Systems, Synchronous vs Asynchronous
used_by: Java Concurrency, Reactive Programming, Distributed Systems
related: Threads, Event Loop, Actor Model
tags:
  - intermediate
  - concurrency
  - mental-model
  - first-principles
  - tradeoff
---

# 014 — Concurrency vs Parallelism

⚡ TL;DR — Concurrency is about _dealing with_ multiple things at once (structure); parallelism is about _doing_ multiple things at once (execution).

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #014 │ Category: CS Fundamentals — Paradigms │ Difficulty: ★★☆ │
├──────────────┼───────────────────────────────────────┼────────────────────────┤
│ Depends on: │ Operating Systems, │ │
│ │ Synchronous vs Asynchronous │ │
│ Used by: │ Java Concurrency, Reactive Programming│ │
│ │ Distributed Systems │ │
│ Related: │ Threads, Event Loop, Actor Model │ │
└─────────────────────────────────────────────────────────────────────────────────┘

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:

Imagine a web server that handles one request completely before starting the next. User A uploads a large file — takes 10 seconds. Users B, C, D, E, F are queued waiting. Users B–F each wait 10+ seconds for a simple 5ms database lookup. The server is single-threaded and sequential — maximum throughput is 1 request per 10 seconds no matter how many CPUs the machine has or how many users are waiting.

THE BREAKING POINT:

Modern computers have 8, 16, 32 cores. Most work is IO-bound (waiting for disk, network, database). A server that processes one thing at a time wastes 99% of CPU capacity waiting. The internet-scale systems we depend on — handling millions of simultaneous users — are physically impossible without structured techniques for managing many tasks at once.

THE INVENTION MOMENT:

This is exactly why the distinction between concurrency and parallelism was formalised — because they solve different problems. Concurrency addresses the _structure_ of programs that must make progress on multiple tasks. Parallelism addresses the _execution_ strategy that uses multiple processors simultaneously. Understanding the difference determines whether your performance problem is architectural (needs concurrency) or hardware utilisation (needs parallelism).

---

### 📘 Textbook Definition

**Concurrency** is a design property of a program in which multiple computations can be in progress at the same time — their execution may overlap in time, but not necessarily simultaneously. Concurrency is about the _structure_ of a program: how it is decomposed into independent tasks that can make progress without waiting for each other. **Parallelism** is a runtime property in which multiple computations execute simultaneously on different hardware units (cores, CPUs, GPUs). Parallelism is about _execution_: actually doing work at the same instant on multiple processors. A concurrent program can run on a single CPU (via interleaving); a parallel program requires multiple execution units. All parallel programs are concurrent; not all concurrent programs are parallel.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Concurrency is juggling (one person, many balls); parallelism is two people juggling simultaneously.

**One analogy:**

> A single chef preparing a complex meal is _concurrent_ — they start the roast, chop vegetables while it cooks, check the sauce, stir pasta, return to the roast. One person, many tasks in progress, interleaved. Two chefs each cooking separate dishes simultaneously is _parallel_ — two people, two dishes, truly at the same instant. The single chef's kitchen is concurrent but not parallel.

**One insight:**
You can have concurrency on a single core (tasks interleave). You can have parallelism only with multiple cores. But the far more common bottleneck is _designing for concurrency_ — because most programs are IO-bound, and making them concurrent (non-blocking, event-driven) solves the problem before parallelism ever comes into play.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Concurrency is a _design decision_ — it affects how you structure code, not what hardware you need.
2. Parallelism is a _hardware constraint_ — you can only have true parallelism if you have multiple execution units.
3. Concurrency enables parallelism — you must first design a concurrent system before a scheduler can run its parts in parallel.

DERIVED DESIGN:

On a single-core CPU, an operating system achieves concurrency by time-slicing: Thread 1 runs for 10ms, gets preempted, Thread 2 runs for 10ms, and so on. Both threads make progress (concurrency), but never simultaneously (no parallelism). The illusion of simultaneous execution is created by rapid switching.

On an 8-core CPU, eight threads can truly run simultaneously (parallelism) — but only if the program is designed for concurrency first. A single-threaded program can't use more than one core regardless of hardware.

The critical implication: designing for concurrency is a prerequisite for scaling on multi-core hardware. If your program is single-threaded, adding CPUs achieves nothing. If your program is concurrent but IO-bound, you may get performance from concurrency alone (event loop, async I/O) without needing parallelism.

THE TRADE-OFFS:

Concurrency gain: better resource utilisation, responsiveness, ability to handle many tasks with fewer resources.
Concurrency cost: coordination complexity (shared state, races, deadlocks), harder to reason about, harder to test.

Parallelism gain: throughput for CPU-bound work, reduced wall-clock time.
Parallelism cost: data dependency management, synchronisation overhead, Amdahl's Law limiting speedup.

---

### 🧪 Thought Experiment

SETUP:
A server must handle 100 simultaneous web requests. Each request takes: 1ms of CPU computation + 50ms waiting for a database query.

WHAT HAPPENS WITHOUT CONCURRENCY (sequential):
Thread 1 handles Request 1: 1ms CPU + 50ms waiting = 51ms. While waiting, the CPU is idle. Thread 1 starts Request 2 only after Request 1 completes. To handle 100 requests sequentially: 100 × 51ms = 5,100ms. The CPU is busy only 1ms out of every 51ms — 2% utilisation.

WHAT HAPPENS WITH CONCURRENCY (async I/O):
Thread 1 starts Request 1, issues the database query, and immediately starts Request 2 while waiting for the DB. The event loop manages 100 in-flight requests on a single thread, swapping in CPU work whenever a DB response arrives. 100 requests complete in approximately 51ms (not 5,100ms) — 100× improvement. CPU utilisation approaches 100% during the 1ms computation windows.

WHAT HAPPENS WITH PARALLELISM (8 cores, 8 threads):
8 threads each handle 12–13 requests, all running simultaneously. Total: ~651ms (8 × 51ms / 8 cores, but IO limits the speedup). Parallelism helps less than concurrency here because the bottleneck is IO wait, not CPU computation.

THE INSIGHT:
For IO-bound workloads (which describes most web services), concurrency alone gives 100× throughput improvement. Parallelism adds relatively little because the bottleneck is waiting for IO, not executing CPU instructions. Misdiagnosing an IO bottleneck as "needs more CPUs" when the real fix is "needs better concurrency design" is a common and expensive mistake.

---

### 🧠 Mental Model / Analogy

> **Concurrency is like a restaurant's kitchen during service.** One head chef manages multiple dishes simultaneously — pasta boiling, sauce reducing, meat resting. The chef isn't doing two things at once, but intelligently interleaving tasks so nothing burns. **Parallelism is when you hire a second chef** — now two people actually cook simultaneously, genuinely doubling throughput for CPU-bound work.

**Mapping:**

- "One chef managing multiple dishes" → concurrent single-threaded event loop
- "Multiple in-progress dishes" → multiple in-flight async tasks
- "Interleaving tasks intelligently" → event loop switching between callbacks
- "Hiring a second chef" → adding a CPU core / parallel thread
- "CPU-bound task" → a dish that requires constant attention (frying, flambéing)
- "IO-bound task" → a dish that mostly waits (simmering, baking)

**Where this analogy breaks down:** A chef can switch tasks freely; a thread requires synchronisation primitives (locks, mutexes) when accessing shared state. Two chefs working on the same dish without communication cause chaos — the analogy misses the coordination complexity that makes concurrent programming difficult.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Concurrency means a program can handle multiple tasks at the same time by switching between them — like a person who answers emails while waiting for a file to download. Parallelism means multiple processors actually work at the same instant — like two people independently solving different parts of the same problem. Concurrency is about _being organised enough_ to handle many things. Parallelism is about having _multiple workers_.

**Level 2 — How to use it (junior developer):**
In Java, `ExecutorService` and `CompletableFuture` let you design concurrent programs. For parallel CPU work, use `ForkJoinPool` or parallel streams (`list.parallelStream()`). In Node.js, everything is concurrent by design (event loop) but never parallel within a single process (JavaScript is single-threaded). In Python, `asyncio` gives concurrency; `multiprocessing` gives parallelism (threads don't help due to the GIL for CPU-bound work).

**Level 3 — How it works (mid-level engineer):**
Concurrency is implemented through interleaving mechanisms: thread scheduling (OS preempts threads every N ms), coroutines (cooperative yield points), or event loops (IO completion callbacks). Parallelism requires multiple threads/processes assigned to different CPU cores by the OS scheduler. The OS uses affinity masks and CPU run queues to distribute threads across cores. Amdahl's Law governs the maximum speedup from parallelism: if 5% of a program is inherently serial, parallelism can never yield more than 20× speedup regardless of how many cores you add.

**Level 4 — Why it was designed this way (senior/staff):**
The concurrency/parallelism distinction comes from Rob Pike's formulation: "Concurrency is about _dealing with_ lots of things at once. Parallelism is about _doing_ lots of things at once." This matters architecturally because concurrent _design_ enables parallel _execution_ — you can't run something in parallel if it was designed to run sequentially. Go's goroutines and channels, Erlang's actor model, and Java's fork-join framework all express concurrent design. The scheduler then maps concurrent tasks to available cores for parallel execution. The insight: design for concurrency first; the parallel execution is automatic if you have the cores.

---

### ⚙️ How It Works (Mechanism)

**Single-core concurrency (time-slicing):**

```
┌─────────────────────────────────────────────────────┐
│        SINGLE-CORE TIME-SLICED CONCURRENCY          │
│                                                     │
│  CPU Timeline (1 core):                             │
│                                                     │
│  [T1: 10ms]─[T2: 10ms]─[T1: 10ms]─[T3: 10ms]─...  │
│                                                     │
│  Thread 1 makes progress on Task A                  │
│  Thread 2 makes progress on Task B                  │
│  Thread 3 makes progress on Task C                  │
│                                                     │
│  All three tasks are IN PROGRESS (concurrent)       │
│  but only ONE executes at any instant (not parallel)│
└─────────────────────────────────────────────────────┘
```

**Multi-core parallelism:**

```
┌─────────────────────────────────────────────────────┐
│           MULTI-CORE TRUE PARALLELISM               │
│                                                     │
│  Core 0: [Thread 1: Task A] continuously            │
│  Core 1: [Thread 2: Task B] continuously            │
│  Core 2: [Thread 3: Task C] continuously            │
│  Core 3: [Thread 4: Task D] continuously            │
│                                                     │
│  All four tasks execute AT THE SAME INSTANT         │
│  (true parallelism — requires multiple cores)       │
└─────────────────────────────────────────────────────┘
```

**Async concurrency (event loop):**

```
┌─────────────────────────────────────────────────────┐
│         ASYNC EVENT LOOP CONCURRENCY                │
│                                                     │
│  Single thread:                                     │
│                                                     │
│  1. Receive Request A → issue DB query A            │
│  2. Receive Request B → issue DB query B            │
│  3. Receive Request C → issue DB query C            │
│     (3 requests in flight, 0 threads blocked)       │
│  4. DB query A returns → resume Request A handler   │
│  5. DB query B returns → resume Request B handler   │
│  6. DB query C returns → resume Request C handler   │
│                                                     │
│  3 concurrent requests; 1 CPU; no thread blocking   │
└─────────────────────────────────────────────────────┘
```

**Happy path:** An async web server handles 10,000 concurrent connections on 1 thread — concurrency without parallelism. A parallel data-processing job divides a 1 billion row dataset across 16 cores — parallelism for CPU-bound throughput.

**Failure mode:** A CPU-bound task running on an event loop thread blocks the entire event loop — no other requests can be processed. This is the "don't block the event loop" rule in Node.js and async Python.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
Client sends 1000 requests
      ↓
[CONCURRENCY DESIGN ← YOU ARE HERE]
  Requests placed in non-blocking queue
  Event loop / thread pool dispatches tasks
  IO tasks: async (waiting doesn't block a thread)
  CPU tasks: parallel threads (one per core)
      ↓
IO completes → callback/resume resumes task
      ↓
Response sent to client
```

FAILURE PATH:

```
CPU-bound task runs on event loop thread
      ↓
Event loop blocked for duration of CPU task
      ↓
All other requests queue up behind blocked loop
      ↓
Latency spike; timeout errors; connection backlog
      ↓
Observable: high CPU on one core, idle on others;
            request queue depth growing
```

WHAT CHANGES AT SCALE:

At 100,000 requests/second, thread-per-request models (one OS thread per request) hit OS limits (~thousands of threads max). Async event loops (Node.js, Netty, Go goroutines) scale to millions of concurrent connections on the same hardware because they don't allocate an OS thread per connection — they use lightweight coroutines or callbacks. Parallelism at this scale means routing to multiple instances (horizontal scaling), not adding threads within one instance.

---

### 💻 Code Example

**Example 1 — Sequential (no concurrency — problem pattern):**

```java
// WRONG: sequential processing wastes CPU during IO waits
public List<User> fetchAllUsers(List<Long> userIds) {
    List<User> users = new ArrayList<>();
    for (Long id : userIds) {
        // Each call blocks for ~50ms DB round-trip
        users.add(userRepository.findById(id)); // sequential
    }
    return users; // 100 IDs × 50ms = 5,000ms total
}
```

**Example 2 — Concurrent (parallel DB queries with CompletableFuture):**

```java
// RIGHT: concurrent async DB queries
public List<User> fetchAllUsers(List<Long> userIds) {
    List<CompletableFuture<User>> futures = userIds.stream()
        .map(id -> CompletableFuture.supplyAsync(
            () -> userRepository.findById(id), executor))
        .collect(Collectors.toList());

    return futures.stream()
        .map(CompletableFuture::join)
        .collect(Collectors.toList());
    // 100 IDs × 50ms / concurrency factor ≈ ~50ms total
}
```

**Example 3 — Parallel CPU work (Fork/Join):**

```java
// RIGHT: parallel computation for CPU-bound work
List<Long> numbers = LongStream.range(0, 1_000_000_000L)
    .boxed()
    .collect(Collectors.toList());

// Uses ForkJoinPool — splits work across all available cores
long sum = numbers.parallelStream()
    .mapToLong(Long::longValue)
    .sum();
// Uses all 8 cores; ~8× faster than sequential stream
```

**Example 4 — Node.js: concurrent by default:**

```javascript
// RIGHT: Node.js event loop handles IO concurrency automatically
async function fetchAllUsers(userIds) {
  // All DB queries issued concurrently
  // Event loop manages them on a single thread
  const promises = userIds.map((id) => db.findUser(id));
  return Promise.all(promises); // concurrent, not sequential
}

// WRONG: blocking the event loop (CPU-bound work inline)
app.get("/compute", (req, res) => {
  const result = heavyComputation(); // blocks event loop!
  // All other requests wait while this runs
  res.json(result);
});

// RIGHT: offload CPU work to worker threads
const { Worker } = require("worker_threads");
app.get("/compute", (req, res) => {
  const worker = new Worker("./computation.js");
  worker.on("message", (result) => res.json(result));
});
```

---

### ⚖️ Comparison Table

| Model                   | Concurrency         | Parallelism      | Best For                     | Limitation                          |
| ----------------------- | ------------------- | ---------------- | ---------------------------- | ----------------------------------- |
| **Async/Event Loop**    | Yes (single thread) | No               | IO-bound (web servers, APIs) | Blocks on CPU work                  |
| Thread Pool             | Yes                 | Yes (multi-core) | Mixed IO+CPU                 | Thread overhead, synchronisation    |
| Go Goroutines           | Yes                 | Yes (GOMAXPROCS) | IO+CPU balanced              | GC pauses under load                |
| Actor Model (Erlang)    | Yes                 | Yes              | Fault-tolerant distributed   | Message-passing overhead            |
| Parallel Streams (Java) | Limited             | Yes (ForkJoin)   | CPU-bound batch work         | Not for IO; overhead for small data |
| Python asyncio          | Yes                 | No (GIL)         | IO-bound Python services     | CPU work needs multiprocessing      |

**How to choose:** For IO-bound work (most web services), async/event-loop concurrency is sufficient — adding parallelism yields diminishing returns. For CPU-bound work (data processing, ML inference, image processing), use parallelism with thread pools or multiprocessing. For mixed workloads, thread pools or Go goroutines handle both.

---

### ⚠️ Common Misconceptions

| Misconception                     | Reality                                                                                                                                                                     |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More threads = more parallelism   | More threads than CPU cores creates context-switching overhead. Beyond `core_count` threads, you add concurrency overhead without adding parallel capacity.                 |
| Concurrency is only about threads | Async/await, coroutines, and event loops achieve concurrency without threads. Node.js handles thousands of concurrent connections on one thread.                            |
| Parallel is always faster         | For small datasets or IO-bound work, the overhead of thread coordination exceeds the benefit. A `parallelStream()` on a 10-element list is slower than a sequential stream. |
| Python threads enable parallelism | CPython's Global Interpreter Lock (GIL) prevents true parallel execution of Python bytecode in threads. `multiprocessing` module bypasses the GIL with separate processes.  |
| Concurrency means non-determinism | Concurrency introduces ordering non-determinism only when tasks share state. Immutable data or message-passing (actors) gives concurrent programs deterministic outcomes.   |

---

### 🚨 Failure Modes & Diagnosis

**Blocking the Event Loop**

Symptom:
Node.js or async Python service has excellent average latency but periodic latency spikes where all requests pause simultaneously. Spikes correlate with certain request types.

Root Cause:
A CPU-bound computation (regex on large string, JSON.parse on large payload, synchronous file I/O) runs on the event loop thread, blocking it for tens or hundreds of milliseconds. All other in-flight requests queue up behind the blocked loop.

Diagnostic Command / Tool:

```javascript
// Node.js: monitor event loop lag
const { monitorEventLoopDelay } = require("perf_hooks");
const histogram = monitorEventLoopDelay({ resolution: 10 });
histogram.enable();
setInterval(() => {
  console.log(`Event loop delay p99: ${histogram.percentile(99) / 1e6}ms`);
}, 5000);

// Also: clinic.js flame graph
// npx clinic flame -- node server.js
```

Fix:
Move CPU-bound work to worker threads (`worker_threads`), off-process via a job queue, or break large synchronous operations into chunks yielded with `setImmediate`. Replace synchronous IO (`fs.readFileSync`) with async (`fs.promises.readFile`).

Prevention:
Never perform CPU-bound work or synchronous IO in event-loop-based services. All handlers must return control quickly (< 1ms).

---

**Thread Starvation in Thread Pool**

Symptom:
Service has many threads configured but throughput plateaus. Thread pool queue depth grows. Requests time out waiting to enter the pool.

Root Cause:
Threads are blocked waiting for IO (DB, network, file). The pool is "full" of blocked threads — each holding a thread but doing no CPU work. Adding more threads just adds more blocked threads.

Diagnostic Command / Tool:

```bash
# Java: check thread states in running JVM
jstack <PID> | grep -A2 "java.lang.Thread.State"
# If most threads are WAITING or TIMED_WAITING on IO → thread starvation

# Or via JMX:
# ThreadMXBean.getThreadCount() vs
# ThreadMXBean.getDaemonThreadCount()
```

Fix:
Switch from blocking IO to async/reactive IO (Project Reactor, WebFlux, virtual threads in Java 21+). Or increase pool size to account for IO wait time: `pool_size = core_count × (1 + io_wait_time / cpu_time)` (Little's Law).

Prevention:
Design services from the ground up as async. Use reactive frameworks for IO-bound workloads. Monitor thread state distribution in production.

---

**Data Race on Shared State**

Symptom:
Intermittent, non-reproducible bugs. Values occasionally wrong. Crashes in code that "looks correct." Bugs disappear under debugger (Heisenbug).

Root Cause:
Two threads read-modify-write shared state without synchronisation. Thread 1 reads value (5), Thread 2 reads value (5), Thread 1 writes 6, Thread 2 writes 6 (instead of 7). The increment is lost.

Diagnostic Command / Tool:

```bash
# Java: ThreadSanitizer equivalent via race detection tools
# Use java.util.concurrent classes instead of raw fields

# Go: built-in race detector
go run -race main.go
# Reports: DATA RACE with goroutine + line numbers

# C/C++: ThreadSanitizer (TSan)
gcc -fsanitize=thread -g -o app app.c && ./app
```

Fix:
Use thread-safe data structures (`AtomicInteger`, `ConcurrentHashMap`), synchronisation (`synchronized`, `ReentrantLock`), or — better — eliminate shared state through message passing (channels, actor model).

Prevention:
Prefer immutable data. Use concurrent collections from the standard library. Enable race detector in CI (`go test -race`). Code review all shared mutable state access patterns.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Operating Systems` — the OS scheduler implements time-slicing concurrency; understanding process and thread models is foundational
- `Synchronous vs Asynchronous` — async I/O is the mechanism that enables concurrency on a single thread without blocking

**Builds On This (learn these next):**

- `Java Concurrency` — locks, atomic operations, executors, CompletableFuture — the toolkit for concurrent JVM programs
- `Reactive Programming` — a programming model built entirely around concurrent data streams and non-blocking composition
- `Distributed Systems` — concurrency at the inter-process and inter-machine level; introduces new failure modes (network partitions, clock skew)

**Alternatives / Comparisons:**

- `Event Loop` — the single-threaded concurrency mechanism in Node.js and async Python; achieves concurrency without threads
- `Actor Model` — Erlang/Akka's approach: isolated actors with message queues, eliminating shared state and data races
- `CSP (Communicating Sequential Processes)` — Go's concurrency model: goroutines communicating via typed channels

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Concurrency: structure to handle many     │
│              │ tasks; Parallelism: executing many tasks  │
│              │ simultaneously on multiple processors     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single-threaded programs waste CPU on     │
│ SOLVES       │ IO waits and can't use multi-core hardware│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ IO-bound: concurrency alone gives 100×    │
│              │ improvement; parallelism adds little      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Concurrency: many simultaneous IO waits   │
│              │ Parallelism: CPU-bound computation        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Parallelism for IO-bound work (overhead   │
│              │ exceeds gain); threads > cores            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Throughput and utilisation vs complexity  │
│              │ of coordination and reasoning about state │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Concurrency is about juggling.           │
│              │  Parallelism is about more jugglers."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Async/Await → Event Loop → Java Threads   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Node.js API server handles 50,000 concurrent HTTP requests on a single event loop thread. The team decides to add CPU-intensive image resizing inline. Response times spike from 10ms to 800ms across _all_ endpoints — not just image requests. Trace step-by-step exactly why all endpoints are affected, not just the image endpoints, and describe the minimum architectural change that would restore the original latency for non-image requests without losing the concurrency benefits.

**Q2.** Amdahl's Law states that if 10% of a program is serial, the maximum speedup from parallelism is 10×, regardless of how many cores you add. A real-world data pipeline runs in 100 minutes on 1 core. Adding 16 cores reduces it to 20 minutes — not the theoretical 6.25 minutes. What are at least three reasons the theoretical speedup is not achieved in practice, and how would you diagnose and address the most impactful one?
