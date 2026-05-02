---
layout: default
title: "Carrier Thread"
parent: "Java Concurrency"
nav_order: 354
permalink: /java-concurrency/carrier-thread/
number: "354"
category: Java Concurrency
difficulty: ★★★
depends_on: Virtual Threads (Project Loom), Thread (Java), Continuation, ExecutorService
used_by: Structured Concurrency, Continuation
tags:
  - java
  - concurrency
  - advanced
  - deep-dive
---

# 354 — Carrier Thread

`#java` `#concurrency` `#advanced` `#deep-dive`

⚡ TL;DR — A platform (OS) thread in Project Loom that runs virtual threads on its stack, temporarily "mounting" a virtual thread to execute it until it blocks.

| #354 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Virtual Threads (Project Loom), Thread (Java), Continuation, ExecutorService | |
| **Used by:** | Structured Concurrency, Continuation | |

---

### 📘 Textbook Definition

A **Carrier Thread** is a platform (OS-backed) thread in the Java Virtual Threads (Project Loom) model that executes virtual threads on behalf of the JVM scheduler. The JVM maintains a pool of carrier threads (typically sized to the number of CPU cores). A virtual thread is *mounted* onto a carrier thread when it has work to do; when the virtual thread performs a blocking operation (I/O, `sleep`, `park`), it is *unmounted* — its continuation (stack state) is saved to the heap and the carrier thread becomes available to run another virtual thread. Carrier threads are transparent to application code; they are managed exclusively by the JVM.

### 🟢 Simple Definition (Easy)

A carrier thread is a real OS thread that "borrows out" to virtual threads one at a time, running each until it needs to wait, then quickly switching to another.

### 🔵 Simple Definition (Elaborated)

Before Project Loom, each Java thread was backed by exactly one OS thread — 1:1 mapping. Creating millions of threads was impossible because OS threads are heavy (1 MB stack, OS scheduler entry). Project Loom introduced virtual threads: lightweight, JVM-managed threads mapped M:N onto a small pool of OS threads. The OS threads in this pool are called carrier threads. A virtual thread runs on a carrier thread until it blocks; the JVM then "unmounts" the virtual thread (saves its stack state) and "mounts" another ready virtual thread onto the same carrier thread. The carrier thread never waits idle — it keeps running work.

### 🔩 First Principles Explanation

**The M:N threading problem:**
- OS threads: ~1 MB stack, ~10μs context switch, limited to ~10,000–100,000 per machine.
- Goal: support 1,000,000 concurrent virtual threads on a machine.
- Solution: a small fixed pool of OS threads (carriers), with the JVM scheduler multiplexing millions of virtual threads onto them.

**Carrier thread pool:** By default, Project Loom creates a `ForkJoinPool`-based carrier pool sized to `Runtime.getRuntime().availableProcessors()`. This is intentional: if you have 8 CPUs, you have 8 carrier threads — all potentially running code simultaneously. More carriers doesn't help because CPU is the bottleneck for compute.

**Mount / Unmount cycle:**
```
VirtualThread.start()
       ↓
JVM Scheduler: pick available carrier thread
       ↓
Mount: copy virtual thread's continuation onto carrier's stack
       ↓
Virtual thread executes (carrier is "busy with" it)
       ↓
Virtual thread calls blocking op (e.g., Socket.read())
       ↓
JVM intercepts: Unmount virtual thread
  - Continuation (stack snapshot) saved to heap
  - Carrier thread freed
       ↓
Carrier runs another virtual thread
       ↓
When I/O completes: VT re-marked as RUNNABLE
       ↓
Next available carrier: re-mount VT → resumes from continuation
```

**Pinning — when carrier threads get stuck:**

A virtual thread can be "pinned" to its carrier thread — unable to unmount — in two cases:
1. Executing a `synchronized` block or method (legacy monitors hold thread identity).
2. Calling native code (JNI) that performs blocking operations.

When pinned, the JVM may create an extra carrier thread (compensating thread) to avoid deadlock, but this can saturate the carrier pool under heavy pinning.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Carrier Threads (legacy 1:1 model):

- Each concurrent I/O operation requires one OS thread.
- 10,000 concurrent HTTP connections = 10,000 OS threads = ~10 GB stack space.
- Thread pool sizing becomes a scalability bottleneck.

What breaks without it:
1. Blocking I/O workloads (HTTP servers, databases) can't scale beyond available OS thread count.
2. Reactive/async code required to avoid blocking — dramatically increases code complexity.

WITH Carrier Threads + Virtual Threads:
→ 1,000,000 concurrent virtual threads on 8 carrier threads — I/O-bound threads don't consume OS resources while waiting.
→ Blocking code style restored — simple, readable, no callback hell.
→ Platform threads (carriers) stay CPU-busy continualy; no idle time waiting for I/O.

### 🧠 Mental Model / Analogy

> Carrier threads are like taxi drivers. A city has only 8 taxis (carrier threads) but thousands of passengers (virtual threads). Each passenger gets in, rides to their destination (executes), exits when they need to wait somewhere (blocks on I/O). The taxi immediately picks up the next passenger rather than idling at the curb. When the first passenger's wait is done (I/O completes), they hail the next available taxi. The 8 taxis keep running 24/7, serving thousands of passengers efficiently — without ever sitting idle waiting for one person.

"Taxis" = carrier threads, "passengers" = virtual threads, "riding" = executing, "waiting at a destination" = blocked on I/O, "hailing next taxi" = re-mounting onto available carrier.

The key: the taxis (OS threads) are always doing work. Passengers (virtual threads) wait on benches (heap), not in taxis.

### ⚙️ How It Works (Mechanism)

**Carrier thread pool internals:**
```java
// Carrier pool = ForkJoinPool with FIFO mode
// Created internally by JVM; not directly accessible

// Check active carrier threads in JFR / JVM diagnostic:
jcmd <pid> Thread.print | grep "CarrierThread"
// Or in JFR: monitor VirtualThreadPinned events
```

**Detecting pinned virtual threads:**

```bash
# Enable JFR monitoring for pinning events
java -Djdk.tracePinnedThreads=full \
     -jar myapp.jar
# Prints stack trace whenever a virtual thread is pinned

# Alternatively via JFR:
jcmd <pid> JFR.start settings=default
# Then inspect: jdk.VirtualThreadPinned events
```

**Virtual thread state transitions:**
```
NEW → STARTED
           ↓ mounted on carrier
RUNNING (executing on carrier thread)
           ↓ blocking op
PARKING / BLOCKED
  (continuation saved to heap;
   carrier thread freed)
           ↓ I/O complete / unparked
RUNNABLE
           ↓ carrier available
RUNNING again on same or different carrier
           ↓ task complete
TERMINATED
```

### 🔄 How It Connects (Mini-Map)

```
OS Thread (platform thread)
         ↓ is a
Carrier Thread ← you are here
         ↓ executes
Virtual Threads (millions possible)
         ↓ saved as
Continuation (stack snapshot on heap)
         ↓ managed by
JVM Scheduler (ForkJoinPool-based)
```

### 💻 Code Example

Example 1 — Virtual threads using carrier threads (transparent):

```java
// Java 21: create 100,000 virtual threads on ~8 carrier threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> {
            // This blocks (HTTP call or sleep)
            // JVM unmounts from carrier during block
            Thread.sleep(Duration.ofMillis(100));
            return "done";
        });
    }
} // awaits all completions

// Only 8 carrier OS threads; 100,000 virtual threads
// Peak memory: ~100,000 small continuations on heap
// vs. 100,000 OS threads = ~100 GB stack!
```

Example 2 — Detecting pinning (synchronized blocks):

```java
// BAD: synchronized block pins virtual thread to carrier
public class PinningExample {
    private final Object lock = new Object();

    public void pinnedMethod() {
        synchronized (lock) {
            // Virtual thread PINNED here if it blocks!
            socket.read(); // blocks but can't unmount
        }
    }
}

// GOOD: Use ReentrantLock — virtual thread can unmount
private final ReentrantLock lock = new ReentrantLock();

public void unpinnedMethod() throws InterruptedException {
    lock.lock();
    try {
        socket.read(); // virtual thread unmounts during read
    } finally {
        lock.unlock();
    }
}
```

Example 3 — Monitoring carrier threads:

```java
// Count active carrier threads
ThreadMXBean tmx =
    ManagementFactory.getThreadMXBean();
long[] ids = tmx.getAllThreadIds();
long carriers = java.util.Arrays.stream(ids)
    .mapToObj(id -> tmx.getThreadInfo(id))
    .filter(info -> info != null &&
        info.getThreadName().contains("ForkJoinPool"))
    .count();
System.out.println("Approx carrier threads: " + carriers);
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Carrier threads = virtual threads | Carrier threads are platform (OS) threads; virtual threads are JVM-scheduled lightweight threads that run ON carrier threads. |
| More carrier threads means better virtual thread performance | Carrier pool size defaults to CPU count; increasing it beyond that doesn't help for I/O-bound workloads and hurts for CPU-bound ones. |
| Virtual threads are faster than platform threads for CPU work | Virtual threads have the same CPU execution overhead as platform threads; their benefit is only for I/O-blocking workloads. |
| Pinning is always a critical problem | Brief pinning (nanoseconds) is harmless; sustained pinning (milliseconds) blocks a carrier and reduces throughput. Monitor and fix hot paths. |
| Setting the carrier pool size is how you tune virtual thread performance | For I/O-bound: heap size (many continuations), not carrier count. For CPU-bound: virtual threads provide no benefit — use platform threads. |

### 🔥 Pitfalls in Production

**1. Pinning via synchronized in Library Code**

```java
// Many Java libraries use synchronized internally
// e.g., older JDBC drivers, some SSL implementations

// Detect: run with JVM flag
System.setProperty("jdk.tracePinnedThreads", "full");
// or: -Djdk.tracePinnedThreads=full

// Fix: Use virtual-thread-friendly alternatives
// JDBC: use connection pools that support virtual threads
// (HikariCP 5.1+, JDBC connection pool that uses semaphore, not synchronized)
```

**2. Saturating Carrier Pool with CPU-Bound Virtual Threads**

```java
// BAD: CPU-intensive work in virtual threads blocks carriers
for (int i = 0; i < 1000; i++) {
    Thread.ofVirtual().start(() -> {
        computeHeavyMath(); // never blocks → stays mounted
        // All ~8 carrier threads pinned by heavy compute
        // Other virtual threads starved
    });
}

// GOOD: Platform threads for CPU-bound work
ExecutorService cpuPool =
    Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors());
cpuPool.submit(this::computeHeavyMath);
```

**3. Misusing ThreadLocal with Virtual Threads (Carrier Identity Issue)**

```java
// BAD: ThreadLocal holds carrier identity, not virtual thread
// ThreadLocal values shared if multiple VTs run on same carrier
// Use ScopedValue (Java 21) for per-virtual-thread context

// GOOD: Java 21 ScopedValue for virtual thread-local data
ScopedValue<String> REQUEST_ID = ScopedValue.newInstance();
ScopedValue.where(REQUEST_ID, "req-123")
    .run(() -> {
        // REQUEST_ID.get() = "req-123" here, not leaked
        processRequest();
    });
```

### 🔗 Related Keywords

- `Virtual Threads (Project Loom)` — the lightweight threads that run on carrier threads.
- `Continuation` — the heap-stored stack snapshot unmounted from a carrier thread.
- `Structured Concurrency` — uses virtual threads and carrier pool for scoped task execution.
- `Thread (Java)` — platform threads that serve as carrier threads.
- `ForkJoinPool` — the default carrier thread pool implementation.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ OS thread that mounts/unmounts virtual    │
│              │ threads; always running — never waiting.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Understanding virtual thread performance; │
│              │ diagnosing pinning; carrier pool sizing.  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't size carrier pool > CPU count for   │
│              │ I/O workloads — it won't help.            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Carrier thread: the taxi that never      │
│              │ parks while a passenger is waiting."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Continuation → Structured Concurrency     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A virtual-thread-based HTTP server handles 500,000 concurrent requests. Each request reads from a database using a JDBC driver that uses `synchronized` internally, causing pinning. With 8 carrier threads and an average DB query time of 50ms, calculate the maximum request throughput the server can achieve due to carrier thread exhaustion, and explain what code change would lift this ceiling.

**Q2.** The JVM creates extra "compensating" carrier threads when all current carriers are pinned, to prevent deadlock. Why is this only a partial solution rather than a complete fix for the pinning problem, and under what production scenario does compensating thread creation make a system's behaviour worse rather than better?

