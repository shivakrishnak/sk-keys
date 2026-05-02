---
layout: default
title: "Fiber / Coroutine"
parent: "Operating Systems"
nav_order: 93
permalink: /operating-systems/fiber-coroutine/
number: "0093"
category: Operating Systems
difficulty: ★★☆
depends_on: Thread, Stack, Cooperative Scheduling
used_by: Async I/O, Node.js Event Loop, Virtual Thread, Kotlin Coroutines
related: Thread, Async I/O, Virtual Thread, Green Thread
tags:
  - os
  - concurrency
  - internals
  - intermediate
---

# 093 — Fiber / Coroutine

⚡ TL;DR — A fiber or coroutine is a user-space cooperative concurrency unit that suspends and resumes at explicit yield points without involving the OS scheduler.

| #093 | Category: Operating Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, Stack, Cooperative Scheduling | |
| **Used by:** | Async I/O, Node.js Event Loop, Virtual Thread, Kotlin Coroutines | |
| **Related:** | Thread, Async I/O, Virtual Thread, Green Thread | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Modern services handle thousands of simultaneous IO-bound operations —
HTTP requests waiting on database responses, network reads pending
remote data. With OS threads, each waiting operation ties up a thread:
8 MB stack + OS scheduling overhead. A server with 10,000 concurrent
connections needs 10,000 OS threads → 80 GB of stack space, and the OS
scheduler grinding through 10,000 context switches per second.

The alternative — callback-based async code — solves the memory problem
but destroys readability. Code that logically reads top-to-bottom
becomes a nest of callbacks, error handlers, and continuation-passing
closures. Reasoning about control flow becomes impossible.

**THE BREAKING POINT:**
Neither "one thread per task" nor "callback hell" scales: the first
exhausts OS resources, the second makes code unmaintainable.

**THE INVENTION MOMENT:**
This is exactly why **Fiber / Coroutine** was created — a lightweight
user-space execution unit that looks like synchronous code but can
suspend without blocking an OS thread, making sequential-looking code
that scales to millions of concurrent tasks.

---

### 📘 Textbook Definition

A **fiber** (also called a coroutine, green thread, or cooperative thread)
is a user-space execution unit with its own stack and program counter,
managed entirely by the runtime or application rather than the OS kernel.
Unlike OS threads, fibers yield control explicitly at defined suspension
points (typically IO waits), transferring execution to another fiber
without an OS syscall or kernel context switch. The scheduler is
implemented in user space and maps many fibers onto one or more OS threads.
Key property: fibers are cooperative (yield at explicit points), not
preemptive (interrupted by timer interrupt).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A fiber is a function that can pause itself mid-execution and resume later.

**One analogy:**

> Imagine you're reading multiple books simultaneously. You read a chapter
> of Book A, put a bookmark in (suspend), pick up Book B, read a chapter,
> bookmark it, return to Book A at exactly where you left off. You are one
> person (one OS thread), but you're making progress on many books
> concurrently. The bookmarks are the saved stack state.

**One insight:**
The key insight is that most of what threads spend time doing is
_waiting_ — for disk, network, or locks. A fiber only needs an OS thread
while it's actively computing; it releases the thread during waits, letting
another fiber run. This is why fibers can number in the millions where
threads cap at thousands.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Explicit yield points**: a fiber only suspends at places the code
   explicitly marks (await, yield, suspend) — never preempted by a timer.
2. **Cheap stack**: a fiber stack starts tiny (~2 KB) and grows on demand,
   unlike OS thread stacks (typically 1–8 MB fixed).
3. **User-space scheduling**: switching between fibers is a function call
   in the runtime, not a syscall — ~10 ns vs ~1 µs for OS context switch.

**DERIVED DESIGN:**
Given that fibers cooperate voluntarily, the runtime scheduler is simple:
maintain a queue of runnable fibers; when one yields, pop the next and
resume it by restoring its saved stack pointer and registers. The OS sees
one thread doing work; inside, hundreds of fibers take turns.

**THE TRADE-OFFS:**
**Gain:** millions of concurrent tasks on a handful of OS threads; sequential
readable code; near-zero context switch cost.
**Cost:** CPU-bound fibers that never yield will starve all others on that
OS thread (cooperative = one bad actor can block all); debugging
stack traces cross yield points and are harder to read; shared state
is still unsafe if multiple OS threads run the fiber scheduler.

---

### 🧪 Thought Experiment

**SETUP:**
A service handles 1,000 concurrent database queries. Each query takes
50 ms total: 1 ms CPU + 49 ms waiting for DB response.

**WHAT HAPPENS WITHOUT FIBER (OS threads):**
1,000 threads created. 1,000 × 1 MB stacks = 1 GB memory. OS scheduler
manages 1,000 threads. During the 49 ms wait, each thread blocks on
a socket read — the OS parks it but still owns the stack. With 4 CPU
cores, at most 4 threads run simultaneously; the other 996 sleep in the
kernel. Creating and context-switching 1,000 threads costs ~10 ms/second
of overhead.

**WHAT HAPPENS WITH FIBER:**
1,000 fibers created on 4 OS threads (one per core). Fiber 1 starts
query, hits await socket.read(), suspends (saves 2 KB stack). Fiber 2
starts immediately. While the DB responds (49 ms), the 4 OS threads
cycle through all 1,000 fibers at the 1 ms CPU portions. When Fiber 1's
response arrives, it's re-queued and resumes in microseconds.
Memory: 1,000 × 2 KB = 2 MB. Context switch: ~10 ns each.

**THE INSIGHT:**
IO-bound concurrency is 98% waiting. Fibers eliminate the cost of waiting
by making the wait invisible to the OS thread.

---

### 🧠 Mental Model / Analogy

> A fiber is like a generator function that can pause at `yield` and
> resume later. The runtime is the function caller deciding which
> generator to advance next.

**Analogy mapping:**

- "Generator function" → fiber / coroutine body
- "yield keyword" → suspension point (await / suspend)
- "Saved generator state" → fiber's saved stack frame
- "Caller deciding next generator" → fiber scheduler (event loop)
- "Multiple generators in flight" → thousands of concurrent fibers

Where this analogy breaks down: generators typically produce values to
a consumer; fibers model arbitrary suspended computation including IO
waits, locks, and timers — broader than value generation.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A fiber is like a thread but much cheaper. You can have millions of them.
They take turns running on a small number of real CPU threads, pausing
whenever they need to wait for something.

**Level 2 — How to use it (junior developer):**
In Kotlin: `launch { val result = suspendingDbQuery() }` creates a
coroutine. In JavaScript: `async function` with `await`. In Java 21:
`Thread.ofVirtual().start(runnable)`. The `await`/`suspend` keywords are
yield points — the runtime knows it can run other coroutines here.

**Level 3 — How it works (mid-level engineer):**
The Kotlin coroutine compiler transforms `suspend` functions into state
machines. At each `suspend` point, the current continuation (remaining
code + locals) is captured as an object on the heap. When resumed, the
state machine jumps to the correct state. The JVM carries only one active
stack frame — the heap-stored continuation holds the rest. Java 21 virtual
threads instead keep the full stack as heap segments, enabling unmodified
blocking code to become non-blocking.

**Level 4 — Why it was designed this way (senior/staff):**
The choice between "CPS transform" (Kotlin/JavaScript) and "stack copying"
(Go goroutines, Java virtual threads) reflects a fundamental tradeoff.
CPS transform is zero-overhead at the JVM level (no stack copy on suspend)
but requires all code in the call chain to be `suspend`-aware — the
"function colour" problem. Stack copying (Go) allows any code to block
freely but must copy the stack on each suspend. Java Virtual Threads chose
a middle path: OS blocking syscalls are intercepted by the JVM and converted
to virtual thread yields, requiring no source-code changes.

---

### ⚙️ How It Works (Mechanism)

**Fiber scheduler loop (simplified):**

```
┌──────────────────────────────────────────────────┐
│              FIBER SCHEDULER (user space)        │
├──────────────────────────────────────────────────┤
│  runQueue = [Fiber1, Fiber2, Fiber3, ...]        │
│  waitQueue = {Fiber4 → socket_fd, ...}           │
│                                                  │
│  LOOP:                                           │
│    fiber = runQueue.pop()                        │
│    resume(fiber)         ← restore SP + regs     │
│    fiber runs until yield/await                  │
│    save(fiber)           ← capture SP + regs     │
│    if fiber waiting on IO:                       │
│      move to waitQueue                           │
│    else: push back to runQueue                   │
│    poll(IO events) → wake waiting fibers         │
└──────────────────────────────────────────────────┘
```

**Kotlin coroutine state machine (compiled output concept):**

```kotlin
// Source:
suspend fun fetchUser(id: Int): User {
    val data = db.query(id)   // suspension point
    return User(data)
}

// Compiler generates a state machine equivalent to:
fun fetchUser(id: Int, cont: Continuation): Any {
    return when (cont.state) {
        0 -> {
            cont.state = 1
            val result = db.query(id, cont)  // may suspend
            if (result == SUSPENDED) return SUSPENDED
            User(result as Data)
        }
        1 -> {
            User(cont.result as Data)
        }
    }
}
```

**Context switch cost comparison:**

```
┌─────────────────────────────────────────────────┐
│  OS Thread Context Switch:  ~1,000–10,000 ns    │
│  • Syscall entry (mode switch)                  │
│  • Save/restore 16+ registers                   │
│  • TLB flush (if process switch)                │
│  • Scheduler O(log n) queue                     │
├─────────────────────────────────────────────────┤
│  Fiber Context Switch:      ~10–100 ns          │
│  • Save ~6 registers (callee-saved)             │
│  • Update stack pointer                         │
│  • Jump to saved instruction pointer            │
│  • No syscall, no TLB flush                     │
└─────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
HTTP request arrives
  → Event loop / fiber scheduler receives event
  → Creates new fiber for request handling
  → [FIBER RUNNING ← YOU ARE HERE]
  → Fiber calls await db.query()
  → Fiber suspends → scheduler runs next fiber
  → DB response arrives (IO event)
  → Fiber rescheduled → resumes after await
  → Fiber returns HTTP response
  → Fiber completes → scheduler reclaims stack
```

**FAILURE PATH:**

```
Fiber throws uncaught exception
  → Runtime catches at fiber boundary
  → Exception stored in coroutine Job object
  → Parent coroutine / structured scope notified
  → Other fibers in scope may be cancelled
  → Error propagated to caller via await/join
```

**WHAT CHANGES AT SCALE:**
At 1,000,000 concurrent fibers, scheduler queue management and memory
for saved stacks becomes the bottleneck. Go's goroutine scheduler uses
work-stealing across OS threads to balance load. Java Virtual Thread
continuation heap segments fragment GC. At this scale, the scheduler
design (work-stealing vs. single-queue) dominates throughput.

---

### 💻 Code Example

Example 1 — Kotlin coroutines: sequential-looking async code:

```kotlin
// BAD: callback-based (hard to follow)
fun getUserAndOrders(userId: Int) {
    db.getUser(userId) { user ->
        db.getOrders(userId) { orders ->
            notifyUI(user, orders) // deeply nested
        }
    }
}

// GOOD: coroutines — sequential and readable
suspend fun getUserAndOrders(userId: Int) {
    val user = db.getUser(userId)    // suspends here
    val orders = db.getOrders(userId) // suspends here
    notifyUI(user, orders)
}
```

Example 2 — Parallel coroutines with structured concurrency:

```kotlin
import kotlinx.coroutines.*

suspend fun fetchAll(userId: Int) = coroutineScope {
    // Both run concurrently; both must complete
    val user = async { db.getUser(userId) }
    val prefs = async { db.getPrefs(userId) }
    combineResults(user.await(), prefs.await())
}
// If either throws, the other is cancelled automatically
```

Example 3 — Java 21 Virtual Threads (unmodified blocking code):

```java
// GOOD: virtual threads make blocking code scale
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> {
            // This BLOCKS — but on a virtual thread,
            // the carrier OS thread is released during block
            String result = jdbcTemplate.queryForObject(
                "SELECT ...", String.class);
            process(result);
        });
    }
}
// 100,000 concurrent DB calls on ~50 OS threads
```

---

### ⚖️ Comparison Table

| Model          | OS Visible | Preemptive | Stack Size | Max Count | Best For         |
| -------------- | ---------- | ---------- | ---------- | --------- | ---------------- |
| OS Thread      | Yes        | Yes        | 1–8 MB     | ~10K      | CPU-bound work   |
| **Fiber**      | No         | No (coop.) | ~2 KB      | Millions  | IO-bound async   |
| Virtual Thread | No         | Yes (JVM)  | ~1 KB      | Millions  | Blocking IO code |
| Go Goroutine   | No         | Yes (Go)   | ~2 KB      | Millions  | General async    |

How to choose: use fibers/coroutines for IO-bound workloads with many
concurrent tasks; use OS threads for CPU-bound parallel computation that
needs true simultaneous execution on multiple cores.

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                     |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| "Fibers are faster than threads for CPU work"       | Fibers win only on IO-bound work; for CPU-bound parallelism, OS threads on multiple cores beat fibers on one OS thread                      |
| "async/await makes code truly concurrent"           | `await` suspends the current coroutine but only enables concurrency if the underlying scheduler runs other coroutines                       |
| "Fibers eliminate race conditions"                  | If multiple OS threads run the fiber scheduler, fibers on different OS threads can race on shared state                                     |
| "Virtual threads replace all use of thread pools"   | Thread pools are still useful for CPU-bound tasks; virtual threads shine for IO-bound blocking code                                         |
| "A coroutine is just syntactic sugar for callbacks" | The compiler transforms to state machines, but the semantics include structured concurrency, cancellation, and scope — far beyond callbacks |

---

### 🚨 Failure Modes & Diagnosis

**1. Blocking a Fiber on CPU-bound work**

**Symptom:**
All requests on one OS thread stall while one request processes a
large computation. Latency spikes to hundreds of milliseconds. Other
fibers on the same OS thread cannot run.

**Root Cause:**
A fiber runs a CPU-intensive loop (e.g., image processing, crypto)
without yielding. Since fibers are cooperative, no other fiber can run
on that OS thread until the computation completes.

**Diagnostic:**

```bash
# Kotlin: coroutine debugger shows blocked coroutines
# Enable: -ea -Dkotlinx.coroutines.debug
# Java VT: check carrier thread pinning
jcmd <pid> Thread.dump_to_file -format=json /tmp/threads.json
grep -c "PINNED" /tmp/threads.json
```

**Fix:** dispatch CPU-bound work to a dedicated thread pool dispatcher:

```kotlin
// BAD: blocking the coroutine dispatcher
withContext(Dispatchers.Default) { heavyCpuComputation() }

// Actually GOOD for CPU work — Default uses thread pool
// BAD is when you forget to switch dispatchers:
// suspend fun handler() { heavyCpuComputation() } // blocks IO dispatcher
```

**Prevention:** use `Dispatchers.Default` (thread pool) for CPU work,
`Dispatchers.IO` (blocking-aware pool) for legacy blocking IO.

**2. Structured Concurrency Violation / Leaked Coroutine**

**Symptom:**
Long-running coroutines accumulate. Memory grows. Application never
fully shuts down — some background tasks keep running.

**Root Cause:**
Coroutines launched with `GlobalScope.launch` or bare `async` outside
a structured scope have no parent to cancel them on shutdown.

**Diagnostic:**

```bash
# Kotlin: coroutine debug dump
Thread.getAllStackTraces().keys.forEach { t ->
    println(t.name + " " + t.state)
}
# Count active coroutines via DebugProbes
DebugProbes.dumpCoroutines()
```

**Fix:** always use structured scopes:

```kotlin
// BAD: GlobalScope is a fire-and-forget leak
GlobalScope.launch { longRunningTask() }

// GOOD: scope tied to lifecycle
lifecycleScope.launch { longRunningTask() }
// or in a service:
coroutineScope { launch { longRunningTask() } }
```

**Prevention:** ban `GlobalScope` in code reviews; use structured
concurrency scopes tied to the owning component's lifecycle.

**3. Carrier Thread Pinning (Java Virtual Threads)**

**Symptom:**
Virtual thread throughput does not improve over platform threads.
`jdk.tracePinnedThreads` shows frequent pinning events.

**Root Cause:**
Virtual threads cannot unmount from their carrier OS thread when
blocked inside a `synchronized` block or native method. The carrier
thread is pinned — it cannot run other virtual threads.

**Diagnostic:**

```bash
# JVM flag to log pinning events
java -Djdk.tracePinnedThreads=full -jar app.jar
# Or JFR event: jdk.VirtualThreadPinned
```

**Fix:** replace `synchronized` with `ReentrantLock` in hot paths:

```java
// BAD: pins carrier thread when blocking
synchronized (lock) {
    result = blockingIO(); // carrier pinned here
}

// GOOD: virtual-thread-friendly
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    result = blockingIO(); // virtual thread can unmount
} finally { lock.unlock(); }
```

**Prevention:** audit `synchronized` usage in IO-heavy paths before
migrating to virtual threads.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Thread` — fibers are the evolution of threads; understand threads first
- `Cooperative Scheduling` — fibers rely on cooperative yield points
- `Stack` — fiber stacks are the core differentiator from threads

**Builds On This (learn these next):**

- `Async I/O` — fibers are typically paired with non-blocking IO
- `Virtual Thread` — Java 21's implementation of fibers in the JVM
- `Node.js Event Loop` — Node uses a single fiber-like event loop

**Alternatives / Comparisons:**

- `Thread` — OS-managed, preemptive; better for CPU-bound parallelism
- `Async/Await` — JavaScript/Python pattern built on top of coroutine semantics

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ User-space cooperative execution unit │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ OS threads too heavy for millions of │
│ SOLVES │ concurrent IO-bound tasks │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ Most concurrency is waiting — fibers │
│ │ make waiting free for the OS thread │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ Thousands+ concurrent IO-bound tasks │
│ │ (DB queries, HTTP calls, file reads) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ CPU-intensive parallel computation — │
│ │ OS threads on separate cores win │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ Massive concurrency vs CPU parallelism │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "Read a thousand books with one bookmark │
│ │ per book — and one pair of eyes" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Async I/O → Virtual Thread → Event Loop │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kotlin coroutines and JavaScript's async/await both use compiler
CPS transformation and cooperative scheduling. Yet Kotlin coroutines can
run on multiple OS threads simultaneously (via Dispatchers.Default) while
JavaScript is fundamentally single-threaded. What precise guarantee does
single-threaded JavaScript provide that Kotlin cannot, and what class of
bugs disappear in JavaScript that you must still handle in Kotlin
coroutines?

**Q2.** Go's goroutines can be preempted at any safe point since Go 1.14,
not just at yield points. This makes Go goroutines behave more like OS
threads (preemptive) than classic coroutines (cooperative). What problem
did this preemptive model solve that the earlier cooperative model could
not, and what is the cost introduced by enabling preemption at safe points
in terms of runtime complexity and code generation?
