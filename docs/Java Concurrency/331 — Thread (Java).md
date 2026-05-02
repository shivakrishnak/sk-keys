---
layout: default
title: "Thread (Java)"
parent: "Java Concurrency"
nav_order: 331
permalink: /java-concurrency/thread/
number: "0331"
category: Java Concurrency
difficulty: ★☆☆
depends_on: JVM, Operating Systems, Heap Memory, Stack Memory
used_by: Runnable, Callable, Thread Lifecycle, synchronized
related: Runnable, Callable, Virtual Threads (Java 21)
tags:
  - java
  - concurrency
  - thread
  - foundational
  - jvm
---

# 0331 — Thread (Java)

⚡ TL;DR — A Java `Thread` is a lightweight unit of execution that runs concurrently with other threads, sharing the JVM heap but owning its own stack — enabling parallel work but requiring synchronisation to safely share mutable data.

| #0331 | Category: Java Concurrency | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Operating Systems, Heap Memory, Stack Memory | |
| **Used by:** | Runnable, Callable, Thread Lifecycle, synchronized | |
| **Related:** | Runnable, Callable, Virtual Threads (Java 21) | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Without threads, a Java program runs as a single execution flow — one statement, then the next, then the next. An HTTP server handling a request must finish responding before accepting the next request. A long database query blocks the entire application. Waiting for I/O freezes the user interface. A CPU with 8 cores sits idle at 12.5% utilisation because only one core ever runs application code.

THE BREAKING POINT:
An e-commerce site processes checkout: validate cart, charge card, send receipt, update inventory, notify warehouse. Sequentially: 3 seconds total. Only 200 concurrent checkouts possible. Peak load: 2,000/second. The site crashes every Black Friday.

THE INVENTION MOMENT:
This is exactly why **Threads** were created — to run multiple independent execution paths concurrently, using multiple CPU cores, and overlapping I/O wait time with computation — turning a sequential bottleneck into a parallel pipeline.

### 📘 Textbook Definition

A **Thread** in Java is a sequential flow of control within a process, represented by the `java.lang.Thread` class. Every Java program has at least one thread (the main thread). Threads share the JVM's heap memory (objects, static variables) — enabling communication — but each thread has its own program counter, stack, and local variables. The JVM maps Java threads to OS threads (platform threads, pre-Java 21). The OS scheduler multiplexes threads across CPU cores. Java 21 introduced virtual threads (`Thread.ofVirtual()`) as lightweight user-space threads for high-throughput I/O concurrency.

### ⏱️ Understand It in 30 Seconds

**One line:**
A thread is the JVM's way to run two things at the same time in the same program.

**One analogy:**
> A restaurant kitchen has one pass-through window (the CPU core) but many cooks preparing dishes simultaneously. Each cook is a thread — they work independently on their dish, share the kitchen equipment (heap memory), but own their cutting board and personal space (stack). The kitchen manager (OS scheduler) decides which cook steps up to the window at any moment.

**One insight:**
Threads share heap memory — and that's both their power and their danger. Two threads can communicate through a shared object (power), but can also corrupt each other's data without synchronisation (danger). Every shared mutable object in a multi-threaded program is a potential source of race conditions.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Each thread has its own stack — method call frames, local primitives, and references are thread-private.
2. All threads share the JVM heap — objects, static fields, and instance fields are shared unless explicitly isolated.
3. Platform threads are 1:1 with OS threads — each Java thread is an OS thread with ~1MB of stack overhead.

DERIVED DESIGN:
Given invariant 1 + 2: a `String s = "hello"` in a method is stack-allocated (the reference) — each thread's `s` is independent. But `sharedList.add("hello")` modifies an object on the heap — both threads see the modification. This is why thread-safety requires synchronisation for heap-shared state.

Given invariant 3: creating 10,000 platform threads = 10GB of stack allocation and massive OS context-switching overhead. This motivated virtual threads (Java 21): user-space threads that don't map 1:1 to OS threads, enabling millions of concurrent threads with far less overhead.

```
┌────────────────────────────────────────────────┐
│       Thread Memory Layout                     │
│                                                │
│  JVM Process                                   │
│  ┌──────────────────────────────────────────┐ │
│  │ HEAP (shared by all threads)             │ │
│  │  Object instances, static variables      │ │
│  └──────────────────────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐            │
│  │ Thread 1    │  │ Thread 2    │            │
│  │ Stack:      │  │ Stack:      │            │
│  │  main()     │  │  httpHandler│            │
│  │  doWork()   │  │  parseReq() │            │
│  │ PC register │  │ PC register │            │
│  └─────────────┘  └─────────────┘            │
└────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Concurrency and parallelism; overlapping I/O with computation; multi-core utilisation.
Cost: Complexity — shared state requires synchronisation; race conditions, deadlocks, and livelocks are hard bugs; 1MB+ stack per thread limits scalability; context switching overhead.

### 🧪 Thought Experiment

SETUP:
A web server needs to handle multiple requests simultaneously.

WITHOUT THREADS (single-threaded):
1. Request A arrives. Server processes it: reads DB (100ms), computes response (10ms), writes DB (50ms) = 160ms.
2. Request B arrives during step 1. It waits.
3. At t=160ms, Request B starts. Wait time for B = 160ms.
4. Maximum throughput: 1/160ms = 6.25 requests/second.

WITH THREADS (multi-threaded):
1. Request A arrives. New thread created. It starts DB read (100ms wait).
2. Request B arrives at t=1ms. New thread created. It starts DB read independently.
3. Both threads wait for DB concurrently. Both responses sent ~160ms after each arrived.
4. Maximum throughput limited by DB/CPU, not by waiting for A to finish before B starts.

THE INSIGHT:
Threads allow I/O wait time (where the CPU is idle) to be overlapped with work from other threads. The server isn't working harder — it's filling idle time with other requests' work. This is threads' primary win for I/O-bound workloads.

### 🧠 Mental Model / Analogy

> Think of a Java program as a factory with multiple assembly lines (threads) sharing a common warehouse (heap). Each assembly line has its own workers and their own task list (stack). Workers from different lines can grab materials from the warehouse at the same time — but if two workers grab the last bolt simultaneously and both try to use it, chaos ensues (race condition). A sign-out system (synchronized) prevents this: only one worker checks out the bolt at a time.

"Assembly line" → thread.
"Warehouse" → heap.
"Worker's task list" → thread stack.
"Two grabbing same bolt" → race condition on shared heap object.
"Sign-out system" → synchronization primitives.

Where this analogy breaks down: Real assembly lines are physically separate; Java threads share the SAME heapspace — they're less "separate assembly lines" and more "overlapping work zones in the same space."

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When a program needs to do two things at the same time — like downloading a file while responding to user clicks — it uses threads. Each thread is a separate execution path running concurrently, sharing the program's data.

**Level 2 — How to use it (junior developer):**
Create a thread by extending `Thread` (rarely used) or implementing `Runnable` (preferred) and passing to `Thread`. Call `.start()` — NOT `.run()`. `.start()` creates the new native thread; `.run()` just executes the method in the current thread. Use `Executors.newFixedThreadPool(n)` for managed thread pools rather than raw thread creation in production.

**Level 3 — How it works (mid-level engineer):**
`Thread.start()` calls the JVM's native `JavaThread::start()`. The JVM creates an OS thread via `pthread_create` (Linux) or `CreateThread` (Windows). The OS thread runs the JVM's `thread_main` function, which calls back into Java's `Thread.run()`. The JVM thread is registered in the `JavaThreadList`. All threads share the JVM's safepoint coordination: during GC, threads must reach a safepoint before GC can proceed — this is why STW pauses exist.

**Level 4 — Why it was designed this way (senior/staff):**
Java's 1:1 thread model (one Java thread = one OS thread) was the original design choice in Java 1.0 (1995). It leverages OS scheduling but limits scalability to OS-level thread limits (~10K-100K threads per JVM). Java green threads (early 1990s) were M:N (many Java threads to fewer OS threads) but were abandoned because they couldn't use multiple CPU cores effectively. Java 21's virtual threads revisit M:N threading: many virtual threads multiplexed over a small pool of OS carrier threads, enabling high concurrency without OS thread limits. The historical evolution was forced by changing hardware: in 1995, multi-core was exotic; by 2021, 64-core servers are common and thread limits matter enormously.

### ⚙️ How It Works (Mechanism)

**Creating and starting threads:**
```java
// Option 1: extending Thread (not recommended — limits OOP)
class WorkerThread extends Thread {
    @Override
    public void run() {
        System.out.println("Running in: " + getName());
    }
}
new WorkerThread().start();

// Option 2: Runnable (preferred)
Thread t = new Thread(() -> {
    System.out.println("Running in: " + Thread.currentThread().getName());
});
t.start();

// Option 3: Thread.ofPlatform() / Thread.ofVirtual() (Java 21+)
Thread vt = Thread.ofVirtual().start(() -> {
    System.out.println("Virtual thread");
});
```

**Thread lifecycle states:**
```
NEW        → .start() called  → RUNNABLE
RUNNABLE   → scheduled out   → BLOCKED/WAITING/TIMED_WAITING
BLOCKED    → lock acquired   → RUNNABLE
WAITING    → notified        → RUNNABLE
TIMED_WAIT → timeout/notify  → RUNNABLE
RUNNABLE   → run() returns   → TERMINATED
```

**Key thread methods:**
```java
Thread t = new Thread(myTask);
t.setName("worker-1");        // name for debugging
t.setDaemon(true);            // dies when main thread exits
t.setPriority(Thread.MAX_PRIORITY); // hint to OS scheduler
t.start();                    // create OS thread, begin execution

t.join();                     // wait for t to complete
t.join(5000);                 // wait max 5 seconds
t.interrupt();                // set interrupt flag
Thread.sleep(100);            // current thread pauses 100ms
Thread.currentThread();       // get current thread reference
Thread.currentThread().isInterrupted(); // check flag
```

**Thread info for diagnostics:**
```bash
# Thread dump (identify deadlocks, blocked threads):
jstack <pid> | head -100

# JFR profiling:
jcmd <pid> JFR.start duration=30s filename=threads.jfr
jfr print --events jdk.JavaThreadStart threads.jfr
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Application: new Thread(task).start()]
    → [JVM: new JavaThread object created]  ← YOU ARE HERE
    → [OS: pthread_create / CreateThread]
    → [OS schedules thread on CPU core]
    → [Thread.run() executes task]
    → [run() returns → thread transitions TERMINATED]
    → [JVM: JavaThread removed from thread list]
    → [OS thread resources released]
```

FAILURE PATH:
```
[Thread.run() throws uncaught exception]
    → [UncaughtExceptionHandler.uncaughtException() called]
    → [If none set: exception logged to stderr]
    → [Thread terminates abnormally]
    → [Other threads: unaffected (continue running)]
    → [Fix: set UncaughtExceptionHandler on ThreadPool]
```

WHAT CHANGES AT SCALE:
At scale, raw `new Thread()` is never used in production — thread pools (`ExecutorService`) are used to manage thread lifecycle, cap concurrency, and reuse threads. At 10K+ concurrent I/O operations, virtual threads (Java 21) replace platform threads: no stack allocation per blocking operation, no OS thread limits. For CPU-bound parallelism, `ForkJoinPool` (used by parallel streams) dynamically adjusts worker count to match available cores.

### 💻 Code Example

Example 1 — Basic thread creation:
```java
// BAD: new Thread() for production work
for (int i = 0; i < 100; i++) {
    new Thread(() -> processRequest()).start();
    // Creates 100 OS threads — overhead, no control
}

// GOOD: thread pool
ExecutorService pool = Executors.newFixedThreadPool(10);
for (int i = 0; i < 100; i++) {
    pool.submit(() -> processRequest());
}
pool.shutdown();
```

Example 2 — Thread identification and naming:
```java
ExecutorService pool = Executors.newFixedThreadPool(
    4,
    r -> { // custom ThreadFactory for naming
        Thread t = new Thread(r);
        t.setName("order-worker-" + threadCount.getAndIncrement());
        t.setDaemon(false); // don't let these die with main
        return t;
    }
);
```

Example 3 — Join (wait for completion):
```java
Thread dataLoader = new Thread(() -> loadProducts());
Thread configLoader = new Thread(() -> loadConfig());

dataLoader.start();
configLoader.start();

// Wait for both to finish before serving requests:
dataLoader.join();
configLoader.join();
System.out.println("Ready to serve");
```

Example 4 — Interrupt handling:
```java
Thread worker = new Thread(() -> {
    while (!Thread.currentThread().isInterrupted()) {
        try {
            processNextItem();
            Thread.sleep(100); // may throw InterruptedException
        } catch (InterruptedException e) {
            // Restore interrupt flag (sleep clears it)
            Thread.currentThread().interrupt();
            break; // exit loop on interrupt
        }
    }
    System.out.println("Worker shutting down cleanly");
});
worker.start();

// Later: graceful shutdown
worker.interrupt();
worker.join(5000); // wait 5 sec for clean shutdown
```

### ⚖️ Comparison Table

| Thread Type | Overhead | Max Count | I/O Blocking | Best For |
|---|---|---|---|---|
| **Platform thread (Java 8+)** | ~1MB stack | ~10K/JVM | Blocks OS thread | CPU-bound work |
| Virtual thread (Java 21+) | ~few KB | Millions | Unmounts carrier | I/O-intensive workloads |
| Thread pool (Executors) | Pool size fixed | Config | Blocks pool thread | General server work |
| ForkJoinPool | Dynamic | Core count | Work-stealing | Parallel compute |

How to choose: Use virtual threads (`Executors.newVirtualThreadPerTaskExecutor()`) for I/O-bound work in Java 21+. Use `ForkJoinPool` / parallel streams for CPU-bound compute. Use fixed thread pools for work requiring bounded concurrency. Never create unbounded raw `Thread` objects in production.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `thread.run()` starts a new thread | `run()` executes the Runnable in the CURRENT thread — no new thread is created. Only `.start()` creates a new OS thread. This is one of the most common threading bugs |
| Daemon threads are lower-priority | Daemon threads are not lower priority (that's `Thread.setPriority()`). Daemon threads are "background" threads that the JVM shuts down when only daemon threads remain — even if they're still running |
| Thread.sleep() releases locks | `Thread.sleep()` does NOT release synchronized locks. The thread pauses but holds any locks it acquired. `Object.wait()` DOES release the lock during the wait |
| More threads = more speed | For CPU-bound work, threads > CPU cores = slower (context switch overhead). For I/O-bound work, many threads help. For memory-bound work, threads compete for cache bandwidth and may degrade. Profile first |
| Thread.stop() is safe for termination | `Thread.stop()` is deprecated and unsafe — it releases all locks the thread holds, potentially leaving shared state in an inconsistent mid-update state. Use interruption + cooperative shutdown |

### 🚨 Failure Modes & Diagnosis

**Race Condition (Unsynchronized Shared State)**

Symptom: Intermittent wrong results, counters off, list corruptions. Bug is non-deterministic — appears under load, disappears in tests.

Root Cause: Two threads read-modify-write the same heap object without synchronization.

Diagnostic:
```bash
# Thread sanitizer equivalent for Java:
# Run with -XX:+PrintSafepointStatistics or thread dump:
jstack <pid> | grep RUNNABLE -A5

# Helgrind (Valgrind) equivalent: use Java Memory Model tools
# ThreadSanitizer-like: jconsole or async-profiler for contention
```

Fix:
```java
// BAD: unsynchronized counter
int count = 0;
// Two threads: both read 5, both write 6 → lost increment
void increment() { count++; } // NOT atomic!

// GOOD: atomic operation
AtomicInteger count = new AtomicInteger(0);
void increment() { count.incrementAndGet(); }
```

Prevention: Any shared mutable field accessed from multiple threads needs synchronization (`synchronized`, `volatile`, `AtomicX`, or `java.util.concurrent` classes).

---

**Thread Leak (Unbounded Thread Creation)**

Symptom: JVM memory grows. Thread dump shows thousands of threads. Eventually: `OutOfMemoryError: unable to create new native thread`.

Root Cause: Threads created faster than they complete. Often: `new Thread().start()` inside a request handler.

Diagnostic:
```bash
# Count threads:
jstack <pid> | grep "^\"" | wc -l
# If > 200 and growing: thread leak

# Or: jcmd <pid> VM.info | grep "Threads"
```

Fix:
```java
// BAD: one thread per request
@GetMapping("/process")
void handleRequest() {
    new Thread(() -> asyncWork()).start(); // LEAK
}

// GOOD: bounded thread pool
@Autowired ExecutorService pool;
@GetMapping("/process")
void handleRequest() {
    pool.submit(() -> asyncWork()); // bounded
}
```

Prevention: Never create threads directly in request handlers. Use thread pools from startup. Set `maximumPoolSize` to cap thread creation.

---

**Thread.run() instead of Thread.start()**

Symptom: "Concurrent" code runs sequentially — main thread blocks until "thread" completes.

Root Cause: `thread.run()` called instead of `thread.start()`.

Diagnostic:
```bash
# Thread dump during execution shows only main thread running
jstack <pid> | grep "RUNNABLE"
# If only one thread RUNNABLE despite "multi-threaded" code:
# check for .run() vs .start()
```

Fix:
```java
// BAD: runs in current thread
Thread t = new Thread(() -> longTask());
t.run();   // Executes synchronously — blocks!

// GOOD: creates new OS thread
Thread t = new Thread(() -> longTask());
t.start(); // Starts concurrently
```

Prevention: Code review checklist: all `new Thread(...)` uses should call `.start()`. Static analysis tools (SpotBugs, Checkstyle) flag `.run()` on Thread objects.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — threads are JVM execution units; understanding the JVM's memory model is foundational for threading
- `Heap Memory` — threads share the heap; heap memory is the primary source of thread safety issues
- `Stack Memory` — each thread has its own stack; stack isolation is what allows thread-private local variables

**Builds On This (learn these next):**
- `Runnable` — the task interface passed to threads; the immediate next concept
- `Callable` — like Runnable but can return a value and throw checked exceptions
- `synchronized` — the fundamental mechanism for thread-safe access to shared heap state

**Alternatives / Comparisons:**
- `Virtual Threads (Java 21)` — lightweight user-space threads for I/O-concurrency without OS thread limits
- `Callable` — the return-value analog of the `Runnable` passed to threads

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ JVM execution unit with private stack,    │
│              │ sharing heap with all other threads       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Sequential programs can't use multiple    │
│ SOLVES       │ CPU cores or overlap I/O wait time        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Threads share the heap — this enables     │
│              │ communication but requires synchronization│
│              │ for all shared mutable state              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Concurrent work needed: parallel compute, │
│              │ I/O overlap, background tasks             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Raw new Thread() in production — use      │
│              │ ExecutorService or virtual threads        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Concurrency and multi-core use vs race    │
│              │ conditions, deadlocks, and complexity     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two workers sharing a warehouse —        │
│              │  fast together, chaotic without rules"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Runnable → Callable → synchronized →      │
│              │ ExecutorService                           │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** A web application creates one `Thread` per incoming HTTP request. Under normal load (100 req/sec), the server runs fine with ~100 active threads. During a traffic spike (5,000 req/sec), the server crashes with `OutOfMemoryError: unable to create new native thread`. Trace exactly what happens as thread count grows from 100 to failure: what memory is consumed per thread, at what count the OS limit is hit (assuming a typical Linux default), why GC cannot help even with available heap, and what the minimum change is to prevent the crash while maintaining throughput.

**Q2.** Java's Thread.sleep(100) guarantees the thread sleeps AT LEAST 100ms, not exactly 100ms. In a real-time trading system where a thread must fire an order at a precise timestamp (within ±1ms), explain why Thread.sleep() is fundamentally unsuitable for precision timing regardless of OS scheduler configuration, what Java mechanism (if any) provides sub-millisecond timing guarantees, and how high-frequency trading systems actually achieve microsecond-precision timing without using Thread.sleep().

