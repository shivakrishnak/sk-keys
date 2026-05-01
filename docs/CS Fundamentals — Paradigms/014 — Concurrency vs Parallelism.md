---
layout: default
title: "Concurrency vs Parallelism"
parent: "CS Fundamentals — Paradigms"
nav_order: 14
permalink: /cs-fundamentals/concurrency-vs-parallelism/
number: "14"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Synchronous vs Asynchronous, Operating Systems, Processes and Threads
used_by: Java Concurrency, Event-Driven Programming, Reactive Programming
tags: #concurrency, #intermediate, #performance, #architecture
---

# 14 — Concurrency vs Parallelism

`#concurrency` `#intermediate` `#performance` `#architecture`

⚡ TL;DR — Concurrency is about _dealing with_ multiple things at once (structure); parallelism is about _doing_ multiple things at once (execution).

| #14             | Category: CS Fundamentals — Paradigms                                 | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Synchronous vs Asynchronous, Operating Systems, Processes and Threads |                 |
| **Used by:**    | Java Concurrency, Event-Driven Programming, Reactive Programming      |                 |

---

### 📘 Textbook Definition

**Concurrency** is a property of a system's _design_: structuring a program so that multiple logical tasks can be in-progress simultaneously, making progress by interleaving their execution on one or more processors. **Parallelism** is a property of _execution_: two or more computations physically occurring at the same instant on separate hardware resources (CPU cores, machines). Concurrency enables parallelism but does not require it — a single-core CPU can run a concurrent program by time-slicing without true simultaneous execution. Rob Pike's formulation: _concurrency is about dealing with lots of things at once; parallelism is about doing lots of things at once._

---

### 🟢 Simple Definition (Easy)

Concurrency is juggling — one person, multiple balls in the air, but only ever holding one at a time. Parallelism is a team — multiple people each holding a ball simultaneously.

---

### 🔵 Simple Definition (Elaborated)

A concurrent program is _designed_ so that multiple tasks can overlap — one task pauses while another runs. On a single CPU core, this is achieved via time-slicing: the OS switches between tasks so rapidly that they appear simultaneous. Parallelism goes further: multiple tasks execute at the _exact same physical instant_ on multiple CPU cores or machines. You can have concurrency without parallelism (single-core time-slicing) and you cannot meaningfully have parallelism without some form of concurrent design to express which tasks run in parallel. The confusion arises because modern CPUs have many cores — programs that use concurrency are _eligible_ for parallel execution but must be explicitly structured for it.

---

### 🔩 First Principles Explanation

**The problem: a single CPU instruction stream cannot fully utilise modern hardware or serve multiple users simultaneously.**

A sequential program does one thing at a time:

```
Task A: ████████████████████████████████
Task B:                                 ████████████████████
Time:   ───────────────────────────────────────────────────►
```

If Task A waits for a database response (1ms), the CPU sits idle rather than processing Task B.

**The constraint:** hardware provides multiple cores, but software must be structured to use them.

**Concurrency — structural decomposition:**

```
Single Core — Concurrent but NOT parallel:
Task A: ████░░████░░████░░████
Task B: ░░░░████░░████░░████
Time:   ──────────────────────►
```

The CPU switches between tasks (context switch). Both tasks _progress_ — neither fully blocks. This is what Node.js, goroutines, and async/await deliver on a single core.

**Parallelism — simultaneous physical execution:**

```
Multi-Core — Concurrent AND parallel:
Core 1: Task A: ████████████████████████
Core 2: Task B: ████████████████████████
Time:           ────────────────────────►
```

Both tasks run at the same physical instant. This is what Java's `ForkJoinPool`, Go's multi-core goroutine scheduler, and SIMD achieve.

**The key insight:** concurrency is a _design_ property you control. Parallelism is an _execution_ property determined by the runtime and hardware. You must design concurrently to benefit from parallelism.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT concurrency (purely sequential server):

```java
// One request served at a time — next waits behind current
while (true) {
    Request req = server.accept();    // blocks until request
    Response res = process(req);      // blocks for full processing
    server.send(res);                 // blocks until sent
}
// User 2 waits for User 1 to fully complete — unusable at scale
```

What breaks without it:

1. A single slow request (database timeout, large file) blocks all other users.
2. CPU sits idle during I/O waits — wasted hardware capacity.
3. Throughput is bounded by the slowest single operation, not hardware capability.
4. Multi-core CPUs deliver zero benefit to a single-threaded program.

WITH concurrency:
→ Multiple requests handled simultaneously — slow requests do not block fast ones.
→ I/O wait time is used to process other tasks.
→ Multi-core hardware is utilised — throughput scales with cores.

WITHOUT the distinction (confusing concurrency with parallelism):
→ Engineers add threads expecting a speedup, but CPU-bound tasks serialise on a lock.
→ Engineers avoid threads entirely thinking "parallel is hard", missing free I/O concurrency.

---

### 🧠 Mental Model / Analogy

> A chef in a kitchen illustrates both concepts. **Concurrency**: the chef starts boiling water, then chops vegetables while waiting, then stirs the pot, then plates — one person, multiple tasks interleaved. **Parallelism**: two chefs work simultaneously — one boils, one chops at the same instant. A restaurant with one kitchen (single-core CPU) can be highly concurrent (the chef never idles) but not parallel. A restaurant with multiple kitchens (multi-core CPU) achieves both.

"Chef's cooking tasks interleaved" = concurrent execution (single core)
"Two chefs working simultaneously" = parallel execution (multi-core)
"Kitchen" = CPU core
"Tasks on the chef's board" = threads / goroutines / coroutines

The chef's skill is concurrency design: never idling, always making progress. Having more chefs is parallelism.

---

### ⚙️ How It Works (Mechanism)

**OS-level concurrency — time-slicing:**

```
┌──────────────────────────────────────────────────────┐
│            CPU Time-Slicing (1 Core)                 │
│                                                      │
│  Thread A: run──►IO wait──────────►run──►IO wait──   │
│  Thread B: ──────────►run──►run────────────►run────  │
│                                                      │
│  CPU executes only ONE thread at a time              │
│  OS scheduler switches every ~10ms (quantum)         │
│  Appears simultaneous to users                       │
└──────────────────────────────────────────────────────┘
```

**Multi-core parallelism:**

```
┌──────────────────────────────────────────────────────┐
│       Multi-Core Execution (4 Cores)                 │
│                                                      │
│  Core 0: Thread A ████████████████████████           │
│  Core 1: Thread B ████████████████████████           │
│  Core 2: Thread C ████████████████████████           │
│  Core 3: Thread D ████████████████████████           │
│                                                      │
│  All four threads execute simultaneously             │
└──────────────────────────────────────────────────────┘
```

**Concurrency models in practice:**

| Model         | Mechanism                | Example                          | Parallel?                       |
| ------------- | ------------------------ | -------------------------------- | ------------------------------- |
| OS Threads    | OS context switching     | Java `Thread`, `ExecutorService` | Yes (multi-core)                |
| Green Threads | Userspace scheduler      | Go goroutines, Kotlin coroutines | Yes (scheduled onto OS threads) |
| Event Loop    | Single-thread, async I/O | Node.js, Vert.x                  | No (single thread)              |
| Actor Model   | Message-passing          | Akka, Erlang                     | Yes (actors on thread pool)     |

---

### 🔄 How It Connects (Mini-Map)

```
Synchronous vs Asynchronous
        │
        ▼
Concurrency vs Parallelism  ◄──── (you are here)
        │
        ├─────────────────────────────────────────┐
        ▼                                         ▼
Java Concurrency                        Event-Driven Programming
(threads, locks, ForkJoinPool)         (single-thread concurrency)
        │                                         │
        ▼                                         ▼
  Parallelism (multi-core)               Reactive Programming
  (parallel streams, parallel GC)       (async stream processing)
```

---

### 💻 Code Example

**Example 1 — Concurrency via threads (eligible for parallelism):**

```java
// Two tasks run concurrently — JVM schedules onto available cores
ExecutorService pool = Executors.newFixedThreadPool(4);

Future<String> userFuture  = pool.submit(() -> fetchUser(userId));
Future<String> orderFuture = pool.submit(() -> fetchOrders(userId));

// Both fetches in-progress simultaneously (parallel on multi-core)
String user   = userFuture.get();   // wait for result
String orders = orderFuture.get();
```

**Example 2 — Concurrency without parallelism (Node.js event loop):**

```javascript
// Single-threaded but concurrent via async I/O
async function handleRequest(req, res) {
  // Both DB calls started concurrently (interleaved, not parallel)
  const [user, orders] = await Promise.all([
    db.findUser(req.userId), // non-blocking I/O
    db.findOrders(req.userId), // non-blocking I/O
  ]);
  res.json({ user, orders });
}
// One JS thread, two DB calls in flight simultaneously
```

**Example 3 — True parallelism with Java parallel streams:**

```java
// BAD: sequential — processes elements one at a time
long count = largeList.stream()
    .filter(this::isValid)
    .count();

// GOOD: parallel — splits work across ForkJoinPool threads
long count = largeList.parallelStream()
    .filter(this::isValid)  // each core processes a partition
    .count();
// Correct only if isValid() is stateless and thread-safe
```

**Example 4 — Amdahl's Law: parallelism has a ceiling:**

```
If 20% of a program is sequential and 80% is parallelisable:
  1 core:   1.0× speedup
  2 cores:  1.67× speedup (not 2×)
  4 cores:  2.5×  speedup (not 4×)
  ∞ cores:  5×    speedup (theoretical maximum, not ∞)

The sequential 20% is the ceiling — parallelism cannot help it.
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                             |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| More threads always means faster execution          | On a single core, more threads means more context-switch overhead; for CPU-bound work, thread count should match core count                         |
| Concurrent programs are parallel                    | A concurrent program on a single-core CPU interleaves execution — no two instructions run simultaneously                                            |
| Parallelism solves all performance problems         | Amdahl's Law: the sequential portion of a program caps the maximum parallel speedup; I/O-bound code benefits from concurrency more than parallelism |
| Node.js cannot handle concurrent requests           | Node.js handles thousands of concurrent I/O-bound requests via its event loop — it just does not execute JavaScript in parallel                     |
| Synchronisation (locks) solves concurrency problems | Locks prevent parallelism by serialising access — overusing locks eliminates the performance benefit of concurrency                                 |

---

### 🔥 Pitfalls in Production

**CPU-bound work on the Node.js event loop**

```javascript
// BAD: CPU-intensive work blocks the event loop
app.get("/analyse", (req, res) => {
  const result = heavyAnalysis(req.body); // blocks all other requests
  res.json(result);
});

// GOOD: offload to a worker thread
const { Worker } = require("worker_threads");
app.get("/analyse", (req, res) => {
  const worker = new Worker("./analysis-worker.js", { workerData: req.body });
  worker.on("message", (result) => res.json(result));
});
```

---

**Thread pool exhaustion causing deadlocks**

```java
// BAD: task submits sub-tasks to same pool — deadlock risk
ExecutorService pool = Executors.newFixedThreadPool(4);

pool.submit(() -> {
    // This task consumes 1 of 4 threads
    Future<String> sub = pool.submit(() -> fetchData()); // needs a thread
    return sub.get(); // blocks waiting for a thread that may never come
    // All 4 threads blocked waiting for sub-tasks → deadlock
});

// GOOD: use ForkJoinPool with work-stealing, or separate pools
ForkJoinPool forkJoin = ForkJoinPool.commonPool();
```

---

**Race condition from unprotected shared mutable state**

```java
// BAD: shared counter mutated by multiple threads
int counter = 0;

Runnable increment = () -> {
    for (int i = 0; i < 10_000; i++) counter++; // not atomic!
};
// Run 4 threads: expected 40,000 — actual: unpredictable (<40,000)

// GOOD: use atomic or synchronised access
AtomicInteger counter = new AtomicInteger(0);
Runnable increment = () -> {
    for (int i = 0; i < 10_000; i++) counter.incrementAndGet();
};
```

---

### 🔗 Related Keywords

- `Synchronous vs Asynchronous` — async programming enables concurrency by freeing threads during waits
- `Event-Driven Programming` — achieves concurrency on a single thread via non-blocking I/O
- `Reactive Programming` — composable concurrency over streams of events
- `Java Concurrency` — the Java API for threads, locks, atomics, and concurrent collections
- `Memory Barrier` — CPU-level mechanism ensuring thread-visible memory ordering in concurrent programs
- `Happens-Before` — the JMM rule defining when memory writes in one thread are visible to another
- `Amdahl's Law` — the mathematical limit on parallel speedup imposed by the sequential fraction
- `Actor Model` — a concurrency model (Akka, Erlang) where actors communicate via messages, avoiding shared state

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Concurrency = structure (tasks interleave)│
│              │ Parallelism = execution (tasks simultaneous│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Concurrency: I/O-bound work, server apps  │
│              │ Parallelism: CPU-bound bulk processing    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Parallelism for I/O-bound: adds overhead  │
│              │ Concurrency with unprotected shared state │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Concurrency is about structure; you can  │
│              │ have it on one core. Parallelism requires │
│              │ extra hardware — and a concurrent design."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Java Concurrency → Happens-Before →       │
│              │ Memory Barrier → Actor Model → Amdahl's   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Java service uses a `ThreadPoolExecutor` with 200 threads to handle HTTP requests, each of which makes a blocking JDBC database call taking 50ms. The service handles 4,000 requests per second. Calculate whether 200 threads is sufficient using Little's Law (L = λW), and explain what happens to latency and memory when the pool is exhausted — then describe the architectural change that would reduce the required thread count by 10× without reducing throughput.

**Q2.** Go's goroutines are described as "concurrent but optionally parallel." The Go runtime multiplexes M goroutines onto N OS threads (M:N scheduling). When a goroutine blocks on a syscall (e.g., file I/O), the runtime creates a new OS thread to prevent the block from stalling other goroutines. Describe two conditions under which a Go program with 10,000 goroutines could still exhaust OS threads, and how `GOMAXPROCS` interacts with both concurrency and parallelism in this model.
