---
layout: default
title: "Virtual Threads (Project Loom)"
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 28
permalink: /java-concurrency/virtual-threads/
id: JCC-028
category: Java Concurrency
difficulty: ★★★
depends_on: Thread (Java), ForkJoinPool, ThreadLocal, ExecutorService
used_by: Carrier Thread, Continuation, Structured Concurrency
related: Thread (Java), Carrier Thread, Continuation
tags:
  - java
  - concurrency
  - virtual-threads
  - deep-dive
  - java21
---

# JCC-028 — Virtual Threads (Project Loom)

⚡ TL;DR — Virtual threads are lightweight JVM-managed threads that unmount from their OS carrier thread during blocking I/O — enabling millions of concurrent threads with near-zero per-thread overhead, eliminating the scalability limit of 1:1 platform threads.

| #0353 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), ForkJoinPool, ThreadLocal, ExecutorService | |
| **Used by:** | Carrier Thread, Continuation, Structured Concurrency | |
| **Related:** | Thread (Java), Carrier Thread, Continuation | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Platform threads (1:1 with OS threads) cost ~1MB of stack. A server handling 10,000 concurrent HTTP requests that each make a blocking database call needs 10,000 platform threads = 10GB of stack memory. Context switches between thousands of OS threads add OS scheduler overhead. Thread pool sizes become critical tuning parameters — too small: requests queue; too large: memory and context-switch overhead.

**THE BREAKING POINT:**
Java reactive frameworks (Spring WebFlux, Vert.x) exist BECAUSE of platform thread limitations. Reactive code avoids blocking with callbacks and `CompletableFuture` chains — but at the cost of drastically reduced code readability. The entire "reactive paradigm" in Java is a workaround for "we can't have 100,000 threads."

**THE INVENTION MOMENT:**
**Virtual threads** (Project Loom, Java 21 GA) solve this at the JVM level — making each blocking I/O call efficiently unmount the thread from the OS, with no programmer effort. Blocking code remains readable and correct; scalability matches reactive without the complexity.

---

### 📘 Textbook Definition

**Virtual threads** are JVM-managed lightweight threads introduced in Java 21 (JEP 444). They are mapped M:N to platform (OS) threads: many virtual threads share a small pool of platform "carrier" threads managed by `ForkJoinPool`. When a virtual thread blocks (on I/O, `sleep()`, `LockSupport.park()`), it is **unmounted** from the carrier thread — the carrier is freed immediately to run another virtual thread. When the blocking operation completes, the virtual thread is **mounted** onto an available carrier to continue. Created via `Thread.ofVirtual().start(task)` or `Executors.newVirtualThreadPerTaskExecutor()`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Virtual threads park on I/O without consuming an OS thread — you get blocking code readability with reactive-style scalability.

**One analogy:**
> A hotel with 4 concierges (carrier threads) and 10,000 guests (virtual threads). When a guest is "on hold with the airline" (blocking I/O), the concierge sets them aside (unmounts) and serves another guest. When the airline replies (I/O complete), the concierge takes the guest back (mounts). 4 concierges handle 10,000 simultaneous requests because they never truly wait.

**One insight:**
Virtual threads do NOT improve CPU-bound code — only I/O-bound blocking code benefits. If the task is doing heavy computation (no I/O waits), adding more virtual threads doesn't help (still limited by CPU cores). The win is: I/O-waiting code occupying near-zero resources instead of blocking a platform thread.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. One virtual thread runs on exactly one carrier at any moment; one carrier runs one virtual thread at a time.
2. Blocking operations in JDK code (`SocketInputStream.read()`, `Thread.sleep()`, `Object.wait()`) are instrumented to unmount the virtual thread rather than blocking the carrier.
3. Virtual threads cannot be "pinned" to a carrier permanently — EXCEPT when inside `synchronized` blocks or calling native methods (`native` methods pin until return).

**DERIVED DESIGN:**
```
Virtual Thread ↔ Carrier Thread (ForkJoinPool worker):

  VT = "Hello"   mounted on    CT = FJWorker-1
  [VT calls Socket.read()]
  [Socket.read() → JDK schedules async I/O]
  [VT UNMOUNTED from CT]  ← CT is now FREE
  [CT = FJWorker-1 picks up VT = "World"]
  [... async I/O completes ...]
  [VT = "Hello" scheduled on next free carrier]
  [VT = "Hello" MOUNTED on CT = FJWorker-2]
  [Socket.read() returns data to VT = "Hello"]
```

**Pinning (carrier blocking)**:
```java
// BAD: synchronized pins virtual thread to carrier
synchronized (sharedLock) {
    socket.read(); // blocks carrier while in synchronized!
}
// FIX: use ReentrantLock instead of synchronized
lock.lock();
try { socket.read(); } // virtual thread can unmount
finally { lock.unlock(); }
```

**THE TRADE-OFFS:**
**Gain:** Millions of concurrent threads at low cost; no reactive framework needed for scalability; existing blocking code runs efficiently; structured concurrency enabled.
**Cost:** Pinning in `synchronized` blocks cancels benefit; CPU-bound code gains nothing; `ThreadLocal` semantics change (performance — each VT can have its own TL copy, increasing memory for millions of VTs); debugging is more complex.

---

### 🧪 Thought Experiment

**SETUP:**
10,000 concurrent HTTP requests, each calling a database (10ms latency).

WITH PLATFORM THREADS (10 pool size):
```
10 threads → max 10 DB calls in parallel → 1000 batches × 10ms = 10s total
Queue depth: 9,990 tasks waiting
Throughput: 10 req/10ms = 1,000 req/sec
```

WITH VIRTUAL THREADS:
```
10,000 virtual threads launched simultaneously
All issue DB calls → all unmounted during DB wait (10ms)
Only ~10 carrier threads actually used during wait
After 10ms: all 10,000 VTs mount and process results
Throughput: 10,000 req/10ms = 1,000,000 req/sec theoretical
```

**THE INSIGHT:**
The database connection pool is now the bottleneck, not the thread count. Virtual threads expose the actual system constraints (DB pool size, network bandwidth) rather than creating artificial thread-count constraints.

---

### 🧠 Mental Model / Analogy

> Virtual threads are like browser tabs in a computer. Each tab is a "virtual process" (virtual thread) — you can have 100 tabs open. Most are idle (waiting for page load = waiting for I/O). The actual CPU work (renderer = carrier thread) jumps between tabs — rendering a page here, processing JS there. Tabs waiting for network data don't use the CPU.

- "Browser tabs" → virtual threads.
- "CPU renderer" → carrier threads (4-8, based on CPU count).
- "Tab waiting for page load" → virtual thread unmounted during I/O.
- "Renderer switches to another tab" → carrier mounts a different virtual thread.

Where this analogy breaks down: Browser tabs are isolated (no shared memory). Virtual threads share heap — all the concurrent access rules still apply. Virtual threads are NOT a concurrency correctness tool — only a scalability tool.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Virtual threads let you write blocking code that scales like non-blocking code — the JVM handles the "don't actually block" part.

**Level 2:** Use `Executors.newVirtualThreadPerTaskExecutor()` for I/O-heavy work. Or `Thread.ofVirtual().start(task)`. Use `ReentrantLock` instead of `synchronized` blocks that contain I/O (avoids pinning). Don't pool virtual threads — create one per task (they're cheap).

**Level 3:** Virtual threads are implemented via **continuations** (`java.lang.Continuation` - JVM internal). A continuation captures the entire call stack of a virtual thread. On unmount, the continuation (stack snapshot + local variables) is stored on the heap. On remount, the continuation is restored onto a carrier's stack. The carrier pool is `ForkJoinPool` (default parallelism = CPU cores).

**Level 4:** Virtual threads make the thread-per-request model scale again — the original Java servlet model before reactive frameworks. Spring Boot 3.2+ supports virtual threads via `spring.threads.virtual.enabled=true`. Structured Concurrency (JEP 428/453) builds on virtual threads: `StructuredTaskScope` ensures all virtual threads in a scope complete (or fail) before the scope exits — eliminating the leak-on-exception problem of `ExecutorService` pools.

---

### ⚙️ How It Works (Mechanism)

**Creating virtual threads:**
```java
// Option 1: Thread factory
Thread vt = Thread.ofVirtual()
    .name("order-processor-", 0) // named
    .start(() -> processOrder(orderId));

// Option 2: Executor (best for server workloads)
try (ExecutorService executor =
        Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<Response>> futures = requests.stream()
        .map(req -> executor.submit(() -> handle(req)))
        .toList();
    // All run as virtual threads
} // close() = await all completion

// Option 3: Thread builder (unstarted)
Thread.Builder builder = Thread.ofVirtual().name("vt");
Thread t1 = builder.start(() -> task1());
Thread t2 = builder.start(() -> task2());
```

**Spring Boot integration:**
```yaml
# application.properties (Spring Boot 3.2+):
spring.threads.virtual.enabled=true
# Switches Tomcat thread pool to virtual threads
# All @RestController handlers run on virtual threads
```

**Detecting pinning (JVM flag):**
```bash
# Log when virtual thread is pinned:
java -Djdk.tracePinnedThreads=full MyApp
# Output example:
# Thread[#35,ForkJoinPool-1-worker-1,5,CarrierThreads]
#   ...
#   com.example.Service.process(Service.java:42)
#   <== pinned (synchronized block with I/O)
```

**Avoid pinning with ReentrantLock:**
```java
// PINNING: synchronized with I/O inside
synchronized (lock) {
    response = httpClient.send(request); // pins carrier!
}

// NO PINNING: ReentrantLock unmounts correctly
lock.lock();
try {
    response = httpClient.send(request); // unmounts carrier
} finally {
    lock.unlock();
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
[Virtual thread VT1: httpClient.send(request)]
    → [JDK: async socket registered with NIO selector]  ← YOU ARE HERE
    → [VT1 continuation saved to heap]
    → [VT1 UNMOUNTED from FJWorker-1]
    → [FJWorker-1: free → mounts VT2]
    → [... NIO selector: response received ...]
    → [JDK: VT1 scheduled on ForkJoinPool]
    → [FJWorker-2: MOUNTS VT1]
    → [VT1: continuation restored, httpClient.send() returns]
    → [VT1 continues processing response]
```

PINNING PATH:
```
[VT1 enters synchronized(sharedLock) {socket.read()}]
    → [JVM: VT1 is inside synchronized monitor]
    → [VT1 CANNOT unmount: socket.read() blocks FJWorker-1]
    → [FJWorker-1 is PINNED for entire duration]
    → [All other VTs that need FJWorker-1: must wait]
    → [Diagnose: -Djdk.tracePinnedThreads=full]
    → [Fix: replace synchronized with ReentrantLock]
```

**WHAT CHANGES AT SCALE:**
At scale, the connection pool (database, HTTP client) becomes the bottleneck instead of thread count. Size connection pools large enough for the concurrency level. JVM metric: `jdk.VirtualThreadPinned` JFR event — monitor pinning frequency to identify `synchronized` block performance issues.

---

### 💻 Code Example

Example 1 — Before/after with virtual threads (Spring Boot):
```java
// BEFORE (Spring MVC, platform threads, bounded pool):
@RestController
class OrderController {
    @GetMapping("/order/{id}")
    OrderResponse get(@PathVariable Long id) {
        // Blocks Tomcat platform thread during load
        return orderService.fetchOrder(id); // DB call
    }
}
// @100 RPS × 50ms latency: needs 5+ platform threads
// @10,000 RPS × 50ms: needs 500 platform threads = 500MB stack

// AFTER (virtual threads, spring.threads.virtual.enabled=true):
@RestController
class OrderController {
    @GetMapping("/order/{id}")
    OrderResponse get(@PathVariable Long id) {
        // This Tomcat handler thread IS a virtual thread
        return orderService.fetchOrder(id); // DB call unmounts VT!
    }
}
// @10,000 RPS × 50ms: 500 VTs active, only 8 carrier threads used
// Memory: ~500 KB for 500 active VTs (vs 500MB for platform threads)
```

Example 2 — Concurrent fanout (replacing CompletableFuture chains):
```java
// BEFORE: CompletableFuture for parallel calls
CompletableFuture<User>  userFuture  =
    CompletableFuture.supplyAsync(() -> userService.get(id));
CompletableFuture<Order> orderFuture =
    CompletableFuture.supplyAsync(() -> orderService.get(id));
UserDashboard dashboard = userFuture
    .thenCombine(orderFuture, UserDashboard::new)
    .join();

// AFTER: virtual threads (readable blocking code)
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User>  user  = scope.fork(() -> userService.get(id));
    Subtask<Order> order = scope.fork(() -> orderService.get(id));
    scope.join().throwIfFailed();
    return new UserDashboard(user.get(), order.get());
}
// Both calls run concurrently on virtual threads
// StructuredTaskScope ensures cleanup if either fails
```

---

### ⚖️ Comparison Table

| Thread Type | Memory/Thread | Max Threads | Blocking I/O | Best For |
|---|---|---|---|---|
| Platform thread | ~1MB stack | ~10K/JVM | Blocks OS thread | CPU-bound; low concurrency |
| **Virtual thread** | ~few KB | Millions | Unmounts carrier | I/O-bound; high concurrency |
| Pool thread (reactive) | ~1MB | Bounded pool | Must be non-blocking | Reactive programming |

How to choose: Virtual threads for I/O-heavy workloads (HTTP servers, DB-calling services). Platform threads for CPU-bound computation. Virtual threads with `StructuredTaskScope` to replace `CompletableFuture` chains for concurrent fanout.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Virtual threads make code faster in general | Virtual threads specifically help I/O-BOUND blocking code scale. CPU-bound code gains nothing — still limited by CPU cores |
| You should pool virtual threads (like platform threads) | No — virtual threads are cheap to create. Pooling them wastes the simplicity. Use one virtual thread per task |
| Virtual threads are thread-safe | Virtual threads have the same concurrency semantics as platform threads — shared state still requires synchronization |
| Virtual threads replace reactive frameworks entirely | For simple blocking code, yes. For advanced reactive patterns (backpressure, streaming), reactive frameworks (Reactor, RxJava) still have advantages |
| synchronized blocks are forbidden in virtual threads | synchronized is legal but causes **pinning** (carrier blocked). Use `ReentrantLock` for I/O inside critical sections. Pinning is a perf issue, not a correctness issue |

---

### 🚨 Failure Modes & Diagnosis

**Virtual Thread Pinning**

**Symptom:** High carrier thread utilisation despite low VT count; throughput doesn't improve.

**Diagnostic:**
```bash
# Enable pinning trace:
java -Djdk.tracePinnedThreads=full MyApp 2>&1 | grep "pinned"

# JFR event:
jcmd <pid> JFR.start duration=30s filename=vt.jfr
jfr print --events jdk.VirtualThreadPinned vt.jfr
```

**Fix:** Replace `synchronized` blocks containing I/O with `ReentrantLock`.

---

**Memory Growth from ThreadLocal in Millions of VTs**

**Symptom:** Heap grows linearly with concurrent virtual thread count.

**Root Cause:** `ThreadLocal` creates per-thread copies — millions of VTs = millions of TL copies.

**Fix:** Use `ScopedValues` (Java 21) for immutable context. Avoid large `ThreadLocal` values in VT-heavy code.

---

**Connection Pool Exhaustion**

**Symptom:** Virtual threads scale fine but DB/HTTP performance degrades.

**Root Cause:** 10,000 VTs all trying to use a 10-connection pool — 9,990 VTs block on connection acquisition.

**Fix:** Size connection pool for expected concurrency: `spring.datasource.hikari.maximum-pool-size=100` (or appropriate for workload).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Thread (Java)` — virtual threads are a type of thread; platform thread understanding is prerequisite
- `ForkJoinPool` — virtual thread carrier pool; understanding FJP explains how VT scheduling works
- `ThreadLocal` — VT changes ThreadLocal performance characteristics; understanding TL scope

**Builds On This (learn these next):**
- `Carrier Thread` — the platform thread a virtual thread mounts on; directly paired with VT
- `Continuation` — the internal mechanism that enables VT unmount/remount
- `Structured Concurrency` — the concurrent pattern that virtual threads enable cleanly

**Alternatives / Comparisons:**
- `Carrier Thread` — the execution vehicle; directly paired with VT
- `Thread (Java)` — platform thread; the predecessor VT is designed to replace for I/O workloads

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Lightweight JVM threads that unmount from │
│              │ OS thread during blocking I/O             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Platform threads: 1MB each, ~10K max;     │
│ SOLVES       │ forces reactive code for scalability      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ONLY helps I/O-bound code. CPU-bound code │
│              │ gains nothing. synchronized blocks PINS   │
│              │ carrier — use ReentrantLock for I/O       │
│              │ in critical sections                      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ HTTP servers, DB-calling services,        │
│              │ any high-concurrency I/O workload         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ CPU-bound computation; code with          │
│              │ unavoidable synchronized+IO (pinning)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ I/O scalability vs pinning risk;          │
│              │ simplicity vs ThreadLocal overhead        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Blocking code that scales — JVM parks    │
│              │  it without blocking the OS thread"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Carrier Thread → Continuation →           │
│              │ Structured Concurrency                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service running 1,000,000 concurrent virtual threads calls `ThreadLocal.get()` on a ThreadLocal that stores a 10KB `HashMap`. Calculate: (a) the approximate total heap used when all 1M VTs have initialised this ThreadLocal, (b) how this compares to the same workload using `ScopedValues` (which is immutable and shared), (c) why `ThreadLocal.remove()` is even more critical for VT workloads than platform thread pools, and (d) what JVM monitoring data would reveal this pattern.

**Q2.** Java's virtual thread specification says that `synchronized` causes "pinning" where the carrier thread is blocked during I/O inside the synchronized block. Explain the technical reason why the JVM cannot simply unmount a virtual thread that is inside a synchronized block — specifically, what invariant of the JVM's monitor (intrinsic lock) implementation prevents the VT from moving to a different carrier thread mid-synchronized-block, and whether Project Loom has a timeline or design plan to eventually fix this limitation (describe the challenge in terms of monitor ownership tracking).

