---
layout: default
title: "CyclicBarrier"
parent: "Java Concurrency"
nav_order: 358
permalink: /java-concurrency/cyclicbarrier/
number: "0358"
category: Java Concurrency
difficulty: ★★★
depends_on: CountDownLatch, Thread, ExecutorService, Semaphore (Java)
used_by: Phaser, Parallel Algorithms
related: CountDownLatch, Phaser, Semaphore (Java)
tags:
  - java
  - concurrency
  - deep-dive
  - synchronization
  - parallel
---

# 0358 — CyclicBarrier

⚡ TL;DR — CyclicBarrier makes N threads wait at a synchronisation point until all N arrive, then releases them all simultaneously and resets for reuse — unlike CountDownLatch which is single-use, CyclicBarrier is reusable across multiple phases of a parallel algorithm.

| #0358           | Category: Java Concurrency                                | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | CountDownLatch, Thread, ExecutorService, Semaphore (Java) |                 |
| **Used by:**    | Phaser, Parallel Algorithms                               |                 |
| **Related:**    | CountDownLatch, Phaser, Semaphore (Java)                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A parallel simulation runs in 4 phases. Each phase uses 8 threads computing their partition of the problem. Phase 2 can only start after ALL threads have completed Phase 1 (they share state). Without a barrier, threads that finish Phase 1 early start Phase 2 and read Phase 1 state that other threads are still writing. Race condition. Incorrect results. You add a shared counter and `wait()/notify()` logic — 40 lines of error-prone synchronisation code per phase transition.

**THE BREAKING POINT:**
The manual synchronisation pattern (counter + wait/notify) is: verbose, error-prone (missing notify, spurious wakeup handling), single-use (must recreate for each phase), and lacks the "run action on barrier" capability for post-phase cleanup.

**THE INVENTION MOMENT:**
`CyclicBarrier` was introduced in Java 5 (`java.util.concurrent`) as a reusable multi-thread rendezvous point. "Cyclic" because it automatically resets after each barrier trip, enabling it to coordinate multiple phases without recreation.

---

### 📘 Textbook Definition

**CyclicBarrier:** A synchronisation aid (`java.util.concurrent.CyclicBarrier`) that allows a fixed number of threads to wait at a common barrier point. When the last thread arrives (calls `await()`), the optional barrier action is executed by that last thread, then all waiting threads are released. The barrier is immediately reset and ready for the next cycle. Unlike `CountDownLatch`, it can be used repeatedly.

**Barrier action:** An optional `Runnable` passed to the `CyclicBarrier` constructor that is executed by the last thread to arrive at the barrier, before any thread is released. Used for per-phase aggregation or cleanup.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CyclicBarrier is a meeting point for N threads — nobody leaves until everyone arrives, and the meeting point resets automatically for the next round.

**One analogy:**

> A relay race team has 4 runners. At the end of each leg, every runner must tag the next runner simultaneously (not one at a time). The CyclicBarrier is the exchange zone where all 4 runners must gather before the next leg begins. When all 4 arrive, the coach blows the whistle (barrier action), and all 4 start the next leg simultaneously. The exchange zone is reused for every leg — that's the "cyclic" part.

**One insight:**
The critical difference from `CountDownLatch` is the reset behaviour. A `CountDownLatch(N)` is a one-way door — once opened, it stays open forever and is useless for subsequent phases. A `CyclicBarrier` is a revolving door — after each wave of N threads passes through, it resets. In multi-phase parallel algorithms (iterative solvers, parallel sorts, simulation timesteps), you need multiple barriers — either create N `CountDownLatch`es or use one `CyclicBarrier`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Exactly N threads must call `await()` before any are released.
2. The barrier action (if provided) runs exactly once per cycle, on the last-arriving thread, before any thread is released.
3. After the barrier trips, the barrier resets to count=N for the next cycle automatically.
4. If any thread is interrupted or times out at the barrier, the barrier is "broken" — all waiting threads receive `BrokenBarrierException`.

**INTERNAL MECHANISM:**

```java
// Simplified mental model of CyclicBarrier internals:
class CyclicBarrier {
    int parties;          // total threads needed
    int count;            // current waiting count
    ReentrantLock lock;
    Condition trip;       // condition to signal release
    Runnable barrierAction;

    int await() throws Exception {
        lock.lock();
        try {
            count++;
            if (count == parties) {
                // Last thread: run action, trip barrier
                if (barrierAction != null) barrierAction.run();
                trip.signalAll(); // wake all waiting threads
                count = 0;       // RESET for next cycle
                return 0;
            } else {
                // Not last: wait
                trip.await();    // releases lock, waits
                return parties - count; // arrival index
            }
        } finally {
            lock.unlock();
        }
    }
}
```

**THE TRADE-OFFS:**

**Gain:** Reusable across multiple phases. Clean API for multi-phase parallel algorithms. Built-in barrier action for per-phase aggregation. Thread-safe and well-tested.

**Cost:** Fixed party count — cannot change the number of participating threads dynamically (use `Phaser` for that). If one thread is interrupted, ALL threads at the barrier receive `BrokenBarrierException` — failure is collective. Not suitable for producer-consumer patterns (use `BlockingQueue`).

---

### 🧪 Thought Experiment

**SETUP:**
Three threads process data in three phases. Each phase depends on all threads completing the previous phase (shared mutable state between phases).

**WITHOUT CyclicBarrier:**

```
Thread 1 finishes Phase 1 immediately.
Starts Phase 2. Reads Phase 1 results.
But Thread 2 is still in Phase 1 writing those results.
→ Thread 1 reads partially-written data → wrong results.
```

**WITH CyclicBarrier (parties=3):**

```
Thread 1 finishes Phase 1 → calls barrier.await() → BLOCKED
Thread 2 finishes Phase 1 → calls barrier.await() → BLOCKED
Thread 3 finishes Phase 1 → calls barrier.await() → LAST
  → barrier action runs (e.g., validates Phase 1 results)
  → all three threads released simultaneously
Thread 1, 2, 3 start Phase 2 → read fully-written Phase 1 data
→ correct results
→ Barrier resets automatically for Phase 2→3 transition
```

**THE INSIGHT:**
CyclicBarrier converts a "happens-before" requirement between phases into a structural guarantee, without the programmer needing to reason about individual thread completion ordering.

---

### 🧠 Mental Model / Analogy

> CyclicBarrier is like a starting gate at a horse race — and the race has multiple heats. When all 8 horses are loaded into the gate (all N threads call `await()`), the gate opens simultaneously (all released). The gate resets automatically for the next heat. A one-time gate (CountDownLatch) would need to be rebuilt after each heat; the CyclicBarrier gate is reusable.

Explicit mapping:

- "horses" → worker threads
- "loading into gate" → calling `await()`
- "gate opening" → all threads released simultaneously
- "gate resets automatically" → `CyclicBarrier` resets after each cycle
- "race starter's signal" → barrier action (optional Runnable)
- "next heat" → next phase of the parallel algorithm

Where this analogy breaks down: if one horse refuses to load (thread is interrupted), the entire heat is cancelled and all other horses are returned to the stable (`BrokenBarrierException` to all waiters). This is unlike a real race where one missing horse might proceed with N-1.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CyclicBarrier is a tool that makes multiple threads wait for each other. You tell it "wait until all 5 threads have reached this point in the code." Once all 5 arrive, they all continue together. The barrier automatically resets so you can use it again for the next coordination point.

**Level 2 — How to use it (junior developer):**
Create a `CyclicBarrier(N)` shared by all N threads. Each thread calls `barrier.await()` when it finishes a phase. The last thread to call `await()` triggers the release and all threads continue. Handle `InterruptedException` and `BrokenBarrierException` — if any thread is interrupted while waiting, all threads at the barrier get `BrokenBarrierException`.

**Level 3 — How it works (mid-level engineer):**
`CyclicBarrier` uses a `ReentrantLock` + `Condition` internally. When a thread calls `await()`, it increments a counter under the lock. If the counter < parties, it calls `condition.await()` (releasing the lock). When the last thread increments count to parties, it calls `condition.signalAll()` and resets the count to 0 before releasing the lock. This reset is the "cyclic" behaviour. The barrier action (if provided) is called by the last arriving thread while still holding the lock, before signalling.

**Level 4 — Why it was designed this way (senior/staff):**
The collective failure model (BrokenBarrierException for all when one fails) is a deliberate design choice: when N threads are coordinating a multi-phase computation, a single thread failure invalidates the entire phase's result. Notifying all waiters of the failure allows the algorithm to cleanly abort rather than having N-1 threads deadlocked forever waiting for the missing thread. The alternative (letting N-1 threads proceed) would produce incorrect results because the broken thread's partition of the work is incomplete. `Phaser` was added in Java 7 to address the fixed-party-count limitation — it allows dynamic addition/removal of participating threads, at the cost of more complex usage.

---

### ⚙️ How It Works (Mechanism)

```
CyclicBarrier STATE MACHINE (parties = 3):

Initial state: waiting=0

Thread 1 → await():
  waiting=1 → BLOCKED (condition.await())

Thread 2 → await():
  waiting=2 → BLOCKED (condition.await())

Thread 3 → await():
  waiting=3 → LAST THREAD:
    1. Run barrier action (if set)
    2. condition.signalAll()
    3. Reset: waiting=0
    → Thread 3 returns index 0
  Thread 1, 2 wake up → return index > 0

Barrier is now RESET, ready for next cycle.

BROKEN BARRIER (if Thread 2 is interrupted):
  Thread 2's await() throws InterruptedException
    → barrier.breakBarrier() called internally
    → Thread 1 (waiting) receives BrokenBarrierException
    → Future await() calls receive BrokenBarrierException
    → Must call barrier.reset() to recover
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Create CyclicBarrier(N, barrierAction)
    ↓
Submit N worker tasks to ExecutorService
    ↓
Each worker: process Phase 1 partition
    ↓
[CyclicBarrier.await() ← YOU ARE HERE]
All N threads blocked until last arrives
    ↓
Last thread: runs barrierAction (e.g., merge results)
    ↓
All N threads released simultaneously
    ↓
Barrier resets (count → 0)
    ↓
Each worker: process Phase 2 partition
    ↓
[CyclicBarrier.await() ← REUSED]
Repeat until all phases complete
```

**FAILURE PATH:**
Thread k is interrupted while at barrier → `CyclicBarrier.breakBarrier()` → all waiting threads receive `BrokenBarrierException` → algorithm must handle collective failure (retry or abort).

**WHAT CHANGES AT SCALE:**
With 100+ threads at a barrier, the "thundering herd" effect on wake-up can cause contention on subsequent operations. Consider staging barriers (barrier of 10 groups of 10, then barrier of 10 group results) for very large thread counts. At extreme parallelism, `Phaser` with tiered registration is more efficient.

---

### 💻 Code Example

**Example 1 — Basic CyclicBarrier for 2-phase parallel computation:**

```java
import java.util.concurrent.*;

public class ParallelSort {
    private static final int THREADS = 4;
    private final int[][] partitions = new int[THREADS][];
    private final CyclicBarrier barrier = new CyclicBarrier(THREADS,
        // Barrier action: runs after each phase
        () -> System.out.println("Phase complete on thread: "
            + Thread.currentThread().getName()));

    public void sort(int[] data) throws Exception {
        // Partition data
        for (int i = 0; i < THREADS; i++) {
            int start = i * data.length / THREADS;
            int end = (i + 1) * data.length / THREADS;
            partitions[i] = Arrays.copyOfRange(data, start, end);
        }

        ExecutorService exec = Executors.newFixedThreadPool(THREADS);
        for (int t = 0; t < THREADS; t++) {
            final int tid = t;
            exec.submit(() -> {
                try {
                    // Phase 1: sort each partition
                    Arrays.sort(partitions[tid]);
                    barrier.await(); // wait for all partitions sorted

                    // Phase 2: merge (simplified — only one thread merges)
                    if (tid == 0) mergeAll(partitions);
                    barrier.await(); // wait for merge complete

                    // Phase 3: post-processing
                    postProcess(partitions[tid]);
                    barrier.await(); // wait for all post-processing

                } catch (InterruptedException | BrokenBarrierException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }
        exec.shutdown();
        exec.awaitTermination(1, TimeUnit.MINUTES);
    }
}
```

**Example 2 — Handling BrokenBarrierException:**

```java
CyclicBarrier barrier = new CyclicBarrier(3);

Runnable worker = () -> {
    for (int phase = 0; phase < 10; phase++) {
        try {
            doPhaseWork(phase);
            barrier.await(); // coordination point

        } catch (BrokenBarrierException e) {
            // Another thread was interrupted — barrier is broken
            // Must reset or abandon the computation
            log.error("Barrier broken in phase {}", phase);
            barrier.reset(); // reset for retry (careful — can cause
            // other threads to get another BrokenBarrierException)
            return; // or: retry logic

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return;
        }
    }
};
```

---

### ⚖️ Comparison Table

| Synchroniser      | Reusable        | Dynamic parties         | Barrier action | Use case                            |
| ----------------- | --------------- | ----------------------- | -------------- | ----------------------------------- |
| **CyclicBarrier** | Yes             | No                      | Yes            | Fixed-thread multi-phase algorithms |
| CountDownLatch    | No (single use) | No                      | No             | One-shot: wait for N events         |
| Phaser            | Yes             | Yes (arrive/deregister) | Yes            | Dynamic-thread multi-phase          |
| Semaphore         | Yes             | N/A                     | No             | Resource pool limiting              |

How to choose: use `CyclicBarrier` when you have a fixed number of threads collaborating on multiple phases. Use `CountDownLatch` for one-time synchronisation (wait for service startup). Use `Phaser` when threads may join or leave between phases.

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CyclicBarrier and CountDownLatch are interchangeable"       | CountDownLatch is single-use; CyclicBarrier resets. The semantic is also different: CDL counts down events (often different threads); CyclicBarrier counts arrivals of the same party. |
| "BrokenBarrierException only affects the interrupted thread" | All threads currently awaiting at the broken barrier receive BrokenBarrierException. It is collective.                                                                                 |
| "The barrier action runs on a random thread"                 | The barrier action always runs on the last thread to arrive. This is deterministic, but unpredictable which specific thread it is.                                                     |
| "await() returns the order threads arrived"                  | It returns the arrival index: the last to arrive returns 0; the first to arrive returns parties-1. This allows the "last thread" to be identified (return value == 0).                 |

---

### 🚨 Failure Modes & Diagnosis

**1. Deadlock — One Thread Never Calls await()**

**Symptom:** Application hangs indefinitely. Thread dump shows N-1 threads in `CyclicBarrier.await()` WAITING state. One thread is either running (infinite loop), blocked elsewhere, or already completed.

**Root Cause:** A thread in the party did not call `await()` — due to an early return, exception, or logic error. The other N-1 threads wait forever.

**Diagnostic:**

```bash
# Take thread dump to identify waiting threads
jstack <pid> | grep -A 20 "CyclicBarrier"
# Identifies threads blocked in await()
# The missing party is NOT in this list — trace its state separately
```

**Fix:** Ensure every code path in the worker (including exception handlers) either calls `await()` or calls `barrier.reset()` to break waiting threads out. Use try-finally:

```java
try {
    doWork();
} finally {
    barrier.await(); // always reach the barrier
}
```

**Prevention:** Always call `await()` in a `finally` block or ensure the exception handler calls `barrier.reset()`.

---

**2. Spurious BrokenBarrierException After Reset**

**Symptom:** After calling `barrier.reset()` following an error, some threads receive another `BrokenBarrierException`.

**Root Cause:** `reset()` breaks the barrier — any thread currently in `await()` when `reset()` is called receives `BrokenBarrierException`. If some threads were still arriving when the reset happened, they see the broken state.

**Diagnostic:**

```bash
# Add logging at barrier entry and exit:
log.debug("Thread {} entering barrier phase {}", tid, phase);
barrier.await();
log.debug("Thread {} exiting barrier phase {}", tid, phase);
# A thread that never logs "exiting" was broken
```

**Fix:** Use `reset()` only when all threads are outside the barrier (e.g., in a controlled error recovery phase). For recurring errors, consider abandoning the `CyclicBarrier` and creating a new one.

**Prevention:** Prefer clean abort (all threads exit cleanly) over reset-and-retry patterns. If retry is needed, use `Phaser` which has cleaner phase advancement with partial failures.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CountDownLatch` — the simpler, single-use predecessor; understand it first
- `Thread` — CyclicBarrier coordinates threads
- `ExecutorService` — typically used to submit the threads being coordinated

**Builds On This (learn these next):**

- `Phaser` — the flexible evolution: supports dynamic parties and tiered barriers
- `Parallel Algorithms` — multi-phase parallel algorithms that CyclicBarrier enables

**Alternatives / Comparisons:**

- `CountDownLatch` — single-use; different semantic (count events vs. collect parties)
- `Phaser` — dynamic parties; more powerful but more complex API
- `Semaphore (Java)` — controls concurrency level rather than synchronising phases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Reusable N-thread rendezvous: all wait    │
│              │ until all arrive, then all released       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-phase parallel algorithms where     │
│ SOLVES       │ phase N+1 can't start until phase N done  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Resets automatically after each trip;     │
│              │ CountDownLatch does not                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fixed set of threads, multiple phases,    │
│              │ each phase requires all-or-nothing start  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Dynamic thread count (use Phaser);        │
│              │ one-shot wait (use CountDownLatch)        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Clean phase synchronisation vs.           │
│              │ collective failure (one break = all break) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Nobody leaves until everyone arrives;    │
│              │  then the gate resets."                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Phaser → Parallel Algorithms              │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are implementing a parallel merge sort using `CyclicBarrier`. The algorithm has log(N) phases (one per merge level). In phase k, 2^(k-1) threads participate; in phase k+1, only 2^(k-2) threads participate. How does `CyclicBarrier` fail to handle this decreasing participant count? How would you redesign the synchronisation using `Phaser` to handle the variable party count across phases?

**Q2.** A distributed system coordinator uses a `CyclicBarrier` with 10 threads for hourly data aggregation. One of the 10 threads intermittently takes 5 minutes instead of the normal 30 seconds (due to a slow downstream API). The barrier holds the other 9 threads for 5 minutes, delaying every subsequent phase by 5 minutes. Design a solution that: (a) preserves correctness (Phase 2 still sees complete Phase 1 results), (b) doesn't hold all threads when one is slow, and (c) can be implemented with standard Java concurrency primitives.
