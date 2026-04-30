---
layout: default
title: "Thread"
parent: "Java Concurrency"
nav_order: 331
permalink: /java-concurrency/thread/
---
# 331 — Thread

`#java` `#concurrency` `#threading` `#jvm`

⚡ TL;DR — A Thread is an independent path of execution within a JVM process; each thread has its own stack, program counter, and native thread mapping, sharing the heap with all other threads in the process.

| #331 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | JVM, Stack Memory, Heap Memory, OS Scheduling | |
| **Used by:** | Concurrency, ExecutorService, Thread Lifecycle, Runnable | |

---

### 📘 Textbook Definition

A **Thread** in Java is an instance of `java.lang.Thread` that maps to a native OS thread. Each thread has its own **program counter**, **JVM stack** (holding stack frames for method calls), and **local variables**. All threads in a JVM process share the **heap** (objects), **Metaspace** (class metadata), and **code cache**. A thread begins executing when `start()` is called and terminates when its `run()` method returns or throws an uncaught exception.

---

### 🟢 Simple Definition (Easy)

A thread is an independent task running inside your program. Your Java program normally runs on one thread (main). You can create more threads to do work in parallel — each thread runs its own sequence of instructions while sharing access to the same objects in memory.

---

### 🔵 Simple Definition (Elaborated)

Every Java application starts with at least one thread: the `main` thread. When you create a `Thread` and call `start()`, the JVM asks the OS to create a native thread — a separate execution unit with its own call stack. All threads share the heap (so they can exchange data via shared objects), but each thread's stack is private (local variables are never visible to other threads). This sharing gives threads their power — and concurrency bugs their danger.

---

### 🔩 First Principles Explanation

**Why threads exist:**

```
Single-threaded program:
   Task A runs → completes → Task B runs → completes → Task C runs

Problem 1: Blocking I/O
   Task A waits for disk read (10ms)
   CPU sits idle the entire time
   Tasks B and C can't run

Problem 2: Multi-core CPUs
   Modern CPUs have 8, 16, 32 cores
   Single-threaded program uses exactly 1 core
   15+ cores idle — wasted hardware

Solution: Multiple threads
   Thread 1: Task A  → blocks on I/O → CPU free
   Thread 2: Task B  → runs during A's I/O wait
   Thread 3: Task C  → runs on another core simultaneously
```

**What each thread owns:**

```
JVM Process memory:
┌────────────────────────────────────────────────────┐
│  HEAP (shared by ALL threads)                      │
│   Objects, arrays — any thread can read/write      │
├────────────────────────────────────────────────────┤
│  METASPACE (shared)   CODE CACHE (shared)          │
├────────────────────────────────────────────────────┤
│  Thread 1              Thread 2              ...   │
│  ┌───────────┐         ┌───────────┐               │
│  │ Stack     │         │ Stack     │               │
│  │  Frame 3  │         │  Frame 2  │               │
│  │  Frame 2  │         │  Frame 1  │               │
│  │  Frame 1  │         └───────────┘               │
│  └───────────┘                                     │
│  PC register           PC register                 │
└────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist — Why Before What

```
Without threads (single-threaded server):
  Request 1 arrives → processing (100ms) → done
  Request 2 waits 100ms before processing starts
  Request 3 waits 200ms ...
  → 10 requests/second max regardless of CPU capacity

With threads (thread-per-request model):
  Request 1 → Thread 1 starts
  Request 2 → Thread 2 starts simultaneously
  Request 3 → Thread 3 starts simultaneously
  → All processed in parallel (up to CPU/thread limit)
  → Throughput scales with cores

Modern: Virtual Threads (Java 21)
  Platform thread = 1 OS thread (expensive, ~1MB stack)
  Virtual thread = lightweight, millions possible
  → Thread-per-request without overhead
```

---

### 🧠 Mental Model / Analogy

> A JVM process is a **kitchen**. The heap is the **shared counter and fridge** — everyone can grab ingredients. Each thread is a **chef** with their own **cutting board** (stack) and recipe card (program counter). Multiple chefs work simultaneously on different dishes, but they all share the same fridge — so they must coordinate (synchronization) when reaching for the same ingredient.

---

### ⚙️ How It Works

```
Creating a thread:
1. new Thread(runnable)  — wraps a Runnable in a Thread
2. thread.start()        — calls native OS: "create a thread"
3. OS creates native thread, JVM allocates stack
4. Thread begins executing Runnable.run() on new stack
5. run() returns → thread terminates → stack freed

Key methods:
  thread.start()         → starts new thread (don't call run() directly)
  thread.join()          → calling thread waits for this thread to finish
  thread.interrupt()     → sets interrupt flag (cooperative stop signal)
  Thread.sleep(ms)       → pauses current thread (releases CPU, not locks)
  Thread.currentThread() → returns reference to current thread
  thread.setDaemon(true) → JVM exits when only daemon threads remain
```

---

### 🔄 How It Connects

```
Thread
  │
  ├─ Stack Memory     → each thread has private stack
  ├─ Heap Memory      → shared across threads (source of race conditions)
  ├─ Thread Lifecycle → NEW → RUNNABLE → BLOCKED/WAITING → TERMINATED
  ├─ Runnable/Callable → the task the thread executes
  ├─ ExecutorService  → manages pool of threads (don't create threads manually)
  ├─ synchronized     → prevents two threads from running a block simultaneously
  ├─ volatile         → ensures heap writes are visible across threads
  └─ Virtual Threads  → Java 21 lightweight threads (millions possible)
```

---

### 💻 Code Example

```java
// Creating threads — three ways

// 1. Extend Thread (not recommended — ties task to threading mechanism)
class MyThread extends Thread {
    @Override public void run() {
        System.out.println("Running in: " + Thread.currentThread().getName());
    }
}
new MyThread().start();

// 2. Runnable lambda (preferred for simple cases)
Thread t = new Thread(() -> {
    System.out.println("Running in: " + Thread.currentThread().getName());
});
t.start();

// 3. ExecutorService (preferred for production)
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(() -> System.out.println("Thread pool task"));
pool.shutdown();
```

```java
// Thread.join() — wait for completion
Thread worker = new Thread(() -> {
    try { Thread.sleep(2000); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    System.out.println("Worker done");
});
worker.start();
worker.join(); // main thread blocks here until worker finishes
System.out.println("Both done");
```

```java
// Daemon threads — background tasks that don't prevent JVM shutdown
Thread monitor = new Thread(() -> {
    while (true) {
        System.out.println("Heartbeat...");
        try { Thread.sleep(1000); } catch (InterruptedException e) { break; }
    }
});
monitor.setDaemon(true); // JVM won't wait for this thread to finish
monitor.start();
// setDaemon MUST be called before start()
```

```java
// Cooperative interruption
Thread worker = new Thread(() -> {
    while (!Thread.currentThread().isInterrupted()) {
        // do work...
    }
    System.out.println("Interrupted — exiting cleanly");
});
worker.start();
Thread.sleep(100);
worker.interrupt(); // sets interrupt flag — worker will see it and exit
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Calling `run()` starts a new thread | `run()` executes on the CURRENT thread; only `start()` creates a new one |
| More threads = faster program | Too many threads → context switching overhead → slower; use thread pools |
| `Thread.stop()` safely stops a thread | Deprecated — can leave objects in inconsistent state; use interruption |
| Threads have separate heaps | All threads share ONE heap; separate stacks only |
| `Thread.sleep()` releases locks | sleep() does NOT release locks — use `wait()` to release a monitor |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Calling `run()` instead of `start()`**

```java
// Bug: runs on current thread — no concurrency at all
thread.run();   // ❌ — executes run() here, synchronously

// Fix:
thread.start(); // ✅ — creates new thread, runs concurrently
```

**Pitfall 2: Creating threads without bounds (unbounded thread creation)**

```java
// Bad: one thread per request — will explode with load
for (Request req : requests) {
    new Thread(() -> process(req)).start(); // ❌ 10,000 requests = 10,000 threads
}

// Fix: use bounded thread pool
ExecutorService pool = Executors.newFixedThreadPool(100);
for (Request req : requests) {
    pool.submit(() -> process(req)); // ✅ max 100 threads, rest queued
}
```

**Pitfall 3: Ignoring InterruptedException**

```java
// Bad: swallowing interrupt — thread can never be stopped
try { Thread.sleep(1000); } catch (InterruptedException e) { } // ❌

// Fix: restore interrupt flag
try { Thread.sleep(1000); }
catch (InterruptedException e) { Thread.currentThread().interrupt(); } // ✅
```

---

### 🔗 Related Keywords

- **[Thread Lifecycle](./068 — Thread Lifecycle.md)** — all states a thread passes through
- **[Runnable vs Callable](./067 — Runnable vs Callable.md)** — how to define the task for a thread
- **[ExecutorService](./074 — ExecutorService.md)** — managed thread pool (preferred over raw threads)
- **[synchronized](./069 — synchronized.md)** — prevents concurrent access to shared state
- **[volatile](./070 — volatile.md)** — visibility of writes across threads
- **Stack Memory** — each thread has its own stack

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Independent execution path with own stack;    │
│              │ shares heap with all threads in the process   │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Parallel work: I/O, CPU tasks, background     │
│              │ jobs — always via ExecutorService, not raw    │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Direct raw Thread creation in production;     │
│              │ use ExecutorService or virtual threads (21+)  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "A thread is a chef in a shared kitchen —     │
│              │  own cutting board, shared fridge,            │
│              │  must coordinate when grabbing the same food" │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Runnable/Callable → Thread Lifecycle →        │
│              │ ExecutorService → synchronized → volatile     │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The JVM stack is private per thread, but the heap is shared. What does this mean for `static` fields? What about local variables declared inside a method? Can a local variable ever be visible to another thread?

**Q2.** You have 4 CPU cores and create 4 threads. Later you increase to 8 threads. Will performance improve, stay the same, or get worse? What factors determine the answer?

**Q3.** What is the difference between a user thread and a daemon thread? When does the JVM actually exit?

