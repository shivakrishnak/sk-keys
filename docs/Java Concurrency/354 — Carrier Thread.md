---
layout: default
title: "Carrier Thread"
parent: "Java Concurrency"
nav_order: 354
permalink: /java-concurrency/carrier-thread/
number: "0354"
category: Java Concurrency
difficulty: ★★★
depends_on: Virtual Threads (Project Loom), ForkJoinPool, Thread (Java)
used_by: Continuation, Structured Concurrency
related: Virtual Threads (Project Loom), Continuation, ForkJoinPool
tags:
  - java
  - concurrency
  - virtual-threads
  - deep-dive
  - java21
---

# 0354 — Carrier Thread

⚡ TL;DR — A carrier thread is a platform OS thread in `ForkJoinPool` on which a virtual thread is **mounted** to execute — when the virtual thread blocks on I/O, it **unmounts** and the carrier is freed to run another virtual thread, enabling high concurrency from a small carrier pool.

| #0354 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Virtual Threads (Project Loom), ForkJoinPool, Thread (Java) | |
| **Used by:** | Continuation, Structured Concurrency | |
| **Related:** | Virtual Threads (Project Loom), Continuation, ForkJoinPool | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Without understanding carrier threads, developers cannot diagnose why virtual thread performance degrades when `synchronized` blocks contain I/O (carrier pinning), why the `-Djdk.tracePinnedThreads` flag matters, or how to tune the carrier pool size. Carrier threads are the execution resource that virtual threads share — understanding the mount/unmount lifecycle is key to virtual thread performance.

---

### 📘 Textbook Definition

A **carrier thread** is a platform thread (OS thread) from `ForkJoinPool` that executes virtual thread code. Virtual threads are **mounted** onto a carrier when they have work to do, and **unmounted** when they block on I/O or `LockSupport.park()`. One carrier can serve many virtual threads sequentially — mounting the next one immediately after the current one unmounts. Carrier threads are managed by `VirtualThread.ForkJoinPool` (default parallelism = `Runtime.availableProcessors()`). Virtual threads cannot choose their carrier; the ForkJoinPool scheduler assigns one.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A carrier thread is the actual OS thread that a virtual thread uses when running — shared among many virtual threads, freed during I/O waits.

**One analogy:**
> Carrier threads are shared bicycles. Virtual threads are commuters. When a commuter (VT) reaches their destination (I/O: waiting for server response), they park the bike (unmount carrier). Another commuter immediately takes that bike. When the first commuter's server responds, they grab any available bike (mount on available carrier).

**One insight:**
The number of carrier threads = number of simultaneously executing virtual threads. For CPU-bound work, more carriers = more CPU used. For I/O-bound work, a few carriers serve thousands of VTs — carriers are only used when VTs actually execute, not when they wait.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. One virtual thread runs on exactly one carrier at any moment.
2. One carrier runs exactly one virtual thread at a time.
3. A virtual thread is **pinned** to its carrier when inside `synchronized` blocks or calling native code — the carrier cannot be freed until the pin is released.

**Mount/unmount lifecycle:**
```
Carrier FJWorker-1:
T=0ms: mounting VT "order-1", running processOrder()
T=5ms: VT "order-1" calls Socket.read() → unmount
         [Socket.read() scheduled as async NIO]
T=5ms: mounting VT "order-2", running processOrder()
T=8ms: NIO: VT "order-1" data received → schedule remount
T=10ms: VT "order-2" calls Socket.read() → unmount
          mounting VT "order-1" → continues after Socket.read()
...
```

**Pinning scenario:**
```java
// Carrier PINNED during I/O in synchronized:
synchronized (sharedLock) {         // pin begins
    data = socket.read();            // carrier blocked — cannot release
    process(data);
}                                   // pin ends
// Carrier cannot serve other VTs during this time
// FIX: use ReentrantLock — VT can unmount inside lock
```

THE TRADE-OFFS:
Carrier threads provide efficient I/O multiplexing at the cost of **pinning** risk — any `synchronized` block or native call that contains I/O blocks the carrier fully.

---

### 🧪 Thought Experiment

SETUP:
8 carrier threads, 1,000 virtual threads, each making a 100ms network call.

WITHOUT PINNING:
- At t=0ms: 8 VTs mounted, 992 waiting to be scheduled
- At t=1ms: all 8 VTs issue network calls → unmount
- Immediately: 8 more VTs mounted — no idle carriers
- At t=100ms: first 8 complete, get remounted for results
- Total: all 1,000 requests complete ≈ 100ms + scheduling overhead
- 8 carriers served 1,000 VTs in ~100ms (theoretical throughput: 10,000/sec)

WITH PINNING (synchronized + I/O):
- At t=0ms: 8 VTs mounted, enter synchronized blocks
- All 8 carriers PINNED for 100ms (one I/O wait each)
- 992 VTs cannot start — no free carriers
- Total: 1,000/8 = 125 rounds × 100ms = 12.5 seconds
- Pinning converts virtual thread parallelism back to platform thread limits!

THE INSIGHT:
Pinning is the primary performance risk with virtual threads. Even one pinned carrier per request can eliminate virtual thread benefits.

---

### 🧠 Mental Model / Analogy

> Carriers are like hospital operating rooms. Virtual threads are surgeries. When a surgery needs to pause (anesthesia setting = I/O wait), the surgeon (carrier) can go use another operating room for a ready surgery. But if the pause happens in a locked-down procedure (synchronized block), the surgeon must stay in that OR the whole time — blocking other surgeries.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A carrier is the actual thread that does the work for a virtual thread when it's running. When the VT waits for I/O, the carrier goes to help someone else.

**Level 2:** Default carriers = CPU cores. Tune with `-Djava.util.concurrent.ForkJoinPool.common.parallelism=N`. Detect pinning with `-Djdk.tracePinnedThreads=full`. Replace `synchronized` containing I/O with `ReentrantLock`. Monitor `jdk.VirtualThreadPinned` JFR events.

**Level 3:** Carrier threads are workers in `VirtualThread.ForkJoinPool` — a dedicated `ForkJoinPool` separate from `ForkJoinPool.commonPool()`. Virtual thread continuations are submitted to this pool on mount. On unmount, the continuation is saved to heap; the FJPool worker (carrier) becomes available for the next submitted continuation.

**Level 4:** In Java 23+, Loom developers work on removing synchronized pinning via "Structured Pinning" solutions. The challenge: JVM's monitor ownership is stored in the object header and identified by the carrier thread — moving the VT to another carrier mid-synchronized would require re-associating the monitor with the new carrier, changing monitor semantics. This is a deep JVM engineering problem without a simple solution.

---

### ⚙️ How It Works (Mechanism)

**Checking carrier assignment:**
```java
// No public API to get the carrier thread from a VT
// But can be seen in thread dumps:
// "ForkJoinPool-1-worker-3" — this is the carrier name
// when a virtual thread is mounted on it

// Carrier pool size:
System.out.println(
    "Carrier count: " +
    ForkJoinPool.commonPool().getParallelism()
);
// Note: VirtualThread pool is distinct from commonPool
// VT pool parallelism = Runtime.availableProcessors()
```

**Monitoring with JFR:**
```bash
jcmd <pid> JFR.start duration=30s filename=carriers.jfr
jfr print --events jdk.VirtualThreadPinned,\
    jdk.VirtualThreadStart,jdk.VirtualThreadEnd \
    carriers.jfr | head -50
```

**Tuning carriers:**
```bash
# Increase carriers for I/O-heavy + some pinning:
java -Djdk.virtualThreadScheduler.parallelism=32 \
     -Djdk.virtualThreadScheduler.maxPoolSize=256 \
     MyApp
# Note: increasing carriers for pinning is a workaround
# The correct fix is to eliminate synchronized+IO pinning
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
[VT "order-1" ready to run]
    → [FJPool: schedule VT on available carrier]     ← YOU ARE HERE
    → [Carrier FJWorker-3 MOUNTS VT "order-1"]
    → [VT: runs userCode() until socket.read()]
    → [socket.read(): registers async I/O]
    → [VT "order-1" UNMOUNTED from FJWorker-3]
    → [FJWorker-3 freed: picks up VT "order-2"]
    → [NIO: socket data arrives for "order-1"]
    → [VT "order-1" added to FJPool work queue]
    → [FJWorker-3 (when free) MOUNTS VT "order-1" again]
    → [socket.read() returns — VT continues]
```

---

### 💻 Code Example

```java
// Check if running on a virtual thread:
Thread current = Thread.currentThread();
if (current.isVirtual()) {
    // This is a virtual thread
    // The carrier is a ForkJoinPool worker
    System.out.println("Virtual: " + current);
} else {
    System.out.println("Platform: " + current);
}

// Avoid pinning — safe pattern for VTs with synchronized:
private final ReentrantLock lock = new ReentrantLock();

void safeBlockingMethod() {
    lock.lock(); // VT can unmount while waiting for lock
    try {
        ioOperation(); // VT can unmount during I/O
    } finally {
        lock.unlock();
    }
}
```

---

### ⚖️ Comparison Table

| Concept | Resource | Count | Blocking I/O Behaviour |
|---|---|---|---|
| Virtual thread | Heap continuation | Millions | Unmounts carrier |
| **Carrier thread** | OS thread (~1MB) | CPU count | Platform thread when VT is mounted |
| Platform thread | OS thread | Thousands | Fully blocks OS thread |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More carrier threads = more virtual thread concurrency | Carriers are only used DURING execution. Adding more carriers helps only if VTs are CPU-bound (pinned or computing). For I/O, adding carriers has diminishing returns |
| Virtual threads have their own stack | Virtual threads have their own call stack stored as a heap continuation (linked `StackChunk` objects), NOT a dedicated OS stack. The carrier's stack is used during mount |
| One carrier per virtual thread | One carrier per MOUNTED virtual thread at any instant. Carriers are time-shared across many VTs sequentially |

---

### 🚨 Failure Modes & Diagnosis

**Carrier pinning (all carriers saturated):**
```bash
# Check for carrier starvation:
jstack <pid> | grep "ForkJoinPool.*VirtualThread" -A5
# All carriers BLOCKED = VTs pinned somewhere

# Enable pinning trace:
java -Djdk.tracePinnedThreads=full MyApp
```

---

### 🔗 Related Keywords

**Prerequisites:** `Virtual Threads (Project Loom)`, `ForkJoinPool`, `Thread (Java)`
**Builds on:** `Continuation` (the mechanism enabling unmount)
**Related:** `Virtual Threads (Project Loom)`, `Structured Concurrency`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Platform OS thread that virtual threads   │
│              │ mount on to execute                       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ synchronized + I/O = PINNING = carrier    │
│              │ blocked. Replace with ReentrantLock.      │
│              │ Default count = CPU cores.                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The actual OS thread a VT borrows        │
│              │  while running"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Continuation → Structured Concurrency     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Describe the exact JVM internal data flow when a virtual thread running on `ForkJoinPool-VirtualThread-worker-3` calls `LockSupport.park()` (not I/O, just a plain park): what happens to the VT's call stack, what data structure stores it, which carrier is freed and when, and what mechanism eventually causes the VT to be remounted when `LockSupport.unpark(vt)` is called from a different thread.

